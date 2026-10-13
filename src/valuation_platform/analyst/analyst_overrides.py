"""Local, revision-bound Phase 1 decisions; never mutate facts or calculate totals."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal
import fcntl
import json
import os
from pathlib import Path
import re
import tempfile

from valuation_platform.analyst import historical_inputs as h
from valuation_platform.analyst import prepared_assembly as a

SCHEMA = 'analyst-override-audit-v1'
OVERLAY_SCHEMA = 'analyst-input-overlay-v1'
KINDS = frozenset({'CLASSIFICATION_CORRECTION', 'NUMERICAL_ASSUMPTION'})
REVIEW_ACTIONS = {
    'CONFLICT': 'Inspect competing populations; explicit revision-bound decision only, not precedence.',
    'INVALID_EVIDENCE': 'Repair the exact evidence binding; an override does not verify invalid evidence.',
    'MISSING_REQUIRED_VALUE': 'Review exact missing input; acknowledgment cannot supply or clear it.',
    'UNRESOLVED_REQUIREMENTS': 'Disposition each retained requirement; a supplied number alone cannot clear it.',
    'PARTIAL_OR_UNREVIEWED_SCOPE': 'Review stated population and completeness; no partial-to-total promotion.',
    'OVERLAP_WARNING': 'Inspect parent/child or reused sources; retain separately, do not sum.',
    'HISTORY_EXCEPTION': 'Preserve short/empty history; no fabricated periods.',
}


def _json(text):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out: raise h.InputError('Duplicate JSON key')
            out[key] = value
        return out
    try: return json.loads(text, object_pairs_hook=pairs)
    except (ValueError, TypeError) as exc: raise h.InputError('Malformed decision JSON') from exc


def relevant(content):
    """Keep financial/evidence content, not refreshed transport time or global seals."""
    if isinstance(content, dict):
        return {k: relevant(v) for k, v in content.items() if k not in
                {'retrieved_at_utc', 'http_status', 'retrieval_mode', 'ledger_sha256'}}
    if isinstance(content, (list, tuple)): return [relevant(v) for v in content]
    return content


@dataclass(frozen=True)
class Target:
    target_id: str
    source: h.InputValue
    revision: str
    review_json: str = '[]'

    def __post_init__(self):
        h._text(self.target_id)
        if type(self.source) is not h.InputValue or not re.fullmatch('[0-9a-f]{64}',self.revision):
            raise h.InputError('Exact immutable source and SHA-256 revision required')
        if type(_json(self.review_json)) is not list:
            raise h.InputError('Retained source/review payload list required')


def targets(prepared):
    """Only registered source populations; ambiguous family IDs cannot supply totals."""
    bindings = {(b['accession'], b['input_id']): b for b in _json(prepared.bindings_json)}
    cards = a.review_queue(prepared)
    out = {}
    for annual in prepared.bundle.annuals:
        for field in h.Field:
            values = [v for v in annual.inputs if v.field is field]
            field_id = a.target(annual.period, field.value, {'kind': 'field'})
            context = dict(period=h._encode(annual.period), field=field.value,
                populations=[dict(input=a.click(v), scope_status=v.scope_status.value,
                                  coverage_keys=list(v.coverage_keys), binding=bindings[(v.period.accession,v.input_id)])
                             for v in values],
                diagnostics=[c for c in cards if c.get('field_target_id') == field_id])
            revision = a.digest(relevant(context))
            for value in values:
                binding = bindings[(value.period.accession, value.input_id)]
                target_id = a.target(value.period, field.value,
                    {'channel': binding['channel'], 'input_id': value.input_id})
                review = a.canonical([c for c in cards if c['target_id'] == target_id or
                    (c.get('field_target_id') == field_id and 'INVALID_EVIDENCE' in c['codes'])])
                out[target_id] = Target(target_id, value, revision, review)
            if len(values) == 1:
                out[field_id] = Target(field_id, values[0], revision, review)
    return out


def _validate_payload(target, payload):
    if type(payload) is not dict or set(payload) != {'value','unit','sign','precision','scope','scope_status','kind'}:
        raise h.InputError('Closed explicit value/unit/sign/precision/scope/kind required')
    try: value = Decimal(payload['value'])
    except Exception as exc: raise h.InputError('Finite decimal string required') from exc
    source = target.source
    if type(payload['value']) is not str or not value.is_finite():
        raise h.InputError('Finite decimal string required')
    if payload['unit'] != source.unit or type(payload['sign']) is not int or payload['sign'] != source.sign:
        raise h.InputError('Exact unit and existing cash/representation sign required')
    for name in ('scope', 'precision'): h._text(payload[name])
    if payload['scope_status'] != source.scope_status.value or payload['scope'] != source.scope:
        raise h.InputError('Scope changes require a separate treatment milestone')
    if payload['kind'] not in KINDS: raise h.InputError('Explicit numerical-assumption or correction classification required')
    if source.field is h.Field.CAPEX and value > 0:
        raise h.InputError('Prepared cash Capex must remain a negative outflow')
    if source.field is h.Field.SHARES and (source.as_of is None or not source.sources):
        raise h.InputError('Shares need an existing evidenced observation date/class population')
    if any('INVALID_EVIDENCE' in f for f in source.flags):
        raise h.InputError('Invalid evidence cannot be repaired by an override')
    return value


def _snapshot(source, review_json):
    return dict(input=a.click(source),period=h._encode(source.period),
                scope_status=source.scope_status.value,coverage_keys=list(source.coverage_keys),
                review_payloads=_json(review_json))


class AuditStore:
    """Exclusive immutable event files + atomic head; lock serializes local writers.

    Integrity checks detect changed/missing/reordered events against the head.
    This is not an adversarial signing service or a financial approval authority.
    """
    def __init__(self, directory):
        self.directory = Path(directory)

    def read(self):
        if not self.directory.exists(): return ()
        paths = sorted(self.directory.glob('event-*.json'))
        head = self.directory / 'HEAD.json'
        if not head.exists():
            if paths: raise h.InputError('Unanchored audit events')
            return ()
        anchor = _json(head.read_text())
        if set(anchor) != {'count','sha256'} or type(anchor['count']) is not int or anchor['count'] != len(paths):
            raise h.InputError('Missing audit event or invalid head')
        events = []; previous = '0' * 64
        for number, path in enumerate(paths, 1):
            event = _json(path.read_text())
            if set(event) != {'schema','sequence','previous','action','target_id','revision','reference','payload','manual','source_snapshot','sha256'}:
                raise h.InputError('Malformed closed audit event')
            unsigned = {k:v for k,v in event.items() if k != 'sha256'}
            if (path.name != f'event-{number:08d}.json' or event['sequence'] != number or
                    event['previous'] != previous or event['schema'] != SCHEMA or a.digest(unsigned) != event['sha256']):
                raise h.InputError('Changed or reordered audit history')
            if event['action'] not in {'PROPOSE','ACCEPT','REVALIDATE','REVOKE','ACKNOWLEDGE'}:
                raise h.InputError('Unknown audit action')
            h.ManualIdentity(**event['manual'])
            h._text(event['target_id'])
            if not re.fullmatch('[0-9a-f]{64}',event['revision']):
                raise h.InputError('Exact content revision required')
            snapshot = event['source_snapshot']
            if type(snapshot) is not dict or set(snapshot) != {'input','period','scope_status','coverage_keys','review_payloads'}:
                raise h.InputError('Exact displaced source snapshot required')
            if event['action'] in {'ACCEPT','REVALIDATE','REVOKE'}:
                ref = next((e for e in events if e['sha256'] == event['reference']), None)
                if ref is None or ref['action'] != 'PROPOSE' or ref['target_id'] != event['target_id'] or event['payload'] != ref['payload']:
                    raise h.InputError('Decision must reference its exact proposal')
                if event['action'] == 'ACCEPT' and ref['revision'] != event['revision']:
                    raise h.InputError('Stale acceptance requires revalidation')
            elif event['reference'] is not None: raise h.InputError('Unexpected audit reference')
            if event['action'] == 'ACKNOWLEDGE' and event['payload'] is not None:
                raise h.InputError('Acknowledgment cannot supply a value')
            if event['action'] != 'ACKNOWLEDGE' and (type(event['payload']) is not dict or
                    set(event['payload']) != {'value','unit','sign','precision','scope','scope_status','kind'}):
                raise h.InputError('Malformed decision value payload')
            previous = event['sha256']; events.append(event)
        if anchor['sha256'] != previous: raise h.InputError('Audit head mismatch')
        return tuple(events)

    def record(self, action, target, *, author, rationale, payload=None, reference=None):
        """Explicit caller decision; runtime supplies the actual UTC event time."""
        if type(target) is not Target: raise h.InputError('Exact current source target required')
        if action not in {'PROPOSE','ACCEPT','REVALIDATE','REVOKE','ACKNOWLEDGE'}:
            raise h.InputError('Unknown action')
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / '.writer.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            events = self.read()
            if action in {'ACCEPT','REVALIDATE','REVOKE'}:
                proposal = next((e for e in events if e['sha256'] == reference and e['action'] == 'PROPOSE'), None)
                if proposal is None or proposal['target_id'] != target.target_id:
                    raise h.InputError('Exact proposal reference required')
                payload = proposal['payload']
                if action == 'ACCEPT' and proposal['revision'] != target.revision:
                    raise h.InputError('Stale proposal requires explicit revalidation')
            elif reference is not None: raise h.InputError('Unexpected reference')
            if action == 'ACKNOWLEDGE':
                if payload is not None: raise h.InputError('Acknowledgment supplies no number')
            else: _validate_payload(target, payload)
            manual = h.ManualIdentity(author, datetime.now(timezone.utc).isoformat(), rationale)
            event = dict(schema=SCHEMA, sequence=len(events)+1,
                previous=events[-1]['sha256'] if events else '0'*64, action=action,
                target_id=target.target_id, revision=target.revision, reference=reference,
                payload=payload, manual=dict(author=manual.author,timestamp_utc=manual.timestamp_utc,rationale=manual.rationale))
            event['source_snapshot'] = _snapshot(target.source,target.review_json)
            event['sha256'] = a.digest(event)
            path = self.directory / f"event-{event['sequence']:08d}.json"
            with path.open('x') as output:
                output.write(a.canonical(event)); output.flush(); os.fsync(output.fileno())
            fd, temporary = tempfile.mkstemp(dir=self.directory, prefix='.head-')
            try:
                with os.fdopen(fd, 'w') as output:
                    output.write(a.canonical(dict(count=len(events)+1,sha256=event['sha256'])))
                    output.flush(); os.fsync(output.fileno())
                os.replace(temporary, self.directory/'HEAD.json')
            finally:
                if os.path.exists(temporary): os.unlink(temporary)
            return event


@dataclass(frozen=True)
class Overlay:
    """Accepted patches remain separate; no rewritten history or readiness claim."""
    values: tuple[h.InputValue, ...]
    applied: tuple[str, ...]
    stale: tuple[str, ...]
    acknowledgments: tuple[str, ...]
    dependent_review: tuple[str, ...]
    audit_json: str

    def __post_init__(self):
        h._typed(self.values,h.InputValue)
        for refs in (self.applied,self.stale,self.acknowledgments,self.dependent_review):h._strings(refs)
        if (len(self.values) != len(self.applied) or any(v.origin is not h.Origin.OVERRIDE for v in self.values)
                or set(self.applied) & set(self.stale) or type(_json(self.audit_json)) is not list):
            raise h.InputError('Separate typed analyst patches and disjoint audit states required')


def overlay(prepared, store):
    catalog = targets(prepared); events = store.read(); decisions = {}; acknowledgments = []
    for event in events:
        if event['action'] == 'ACKNOWLEDGE': acknowledgments.append(event['sha256'])
        if event['action'] in {'ACCEPT','REVALIDATE','REVOKE'}: decisions[event['target_id']] = event
    values = []; applied = []; stale = []; dependencies = []
    seen = set()
    for target_id, event in sorted(decisions.items()):
        if event['action'] == 'REVOKE': continue
        target = catalog.get(target_id)
        if (target is None or target.revision != event['revision'] or
                relevant(event['source_snapshot']) != relevant(_snapshot(target.source,target.review_json))):
            stale.append(event['sha256']); continue
        source = target.source; key = (source.period.accession, source.input_id)
        if key in seen: raise h.InputError('Competing field/component overrides for same population')
        seen.add(key)
        value = _validate_payload(target, event['payload'])
        patch = replace(source, input_id='analyst:'+event['sha256'], value=value,
            origin=h.Origin.OVERRIDE, quality=h.Quality.LIMITED, review=h.Review.ACCEPTED,
            scale=1, precision=event['payload']['precision'], sources=(), formula=None,
            alternatives=(source,), manual=h.ManualIdentity(**event['manual']), null_reason=None,
            selection_rationale=event['manual']['rationale'],
            flags=tuple(dict.fromkeys((*source.flags,'separate_analyst_overlay',event['payload']['kind']))))
        # Completeness, limitations and original unresolved requirements are intentionally unchanged.
        values.append(patch); applied.append(event['sha256'])
        dependencies.extend(v.input_id for annual in prepared.bundle.annuals for v in annual.inputs
                            if v.formula and source.input_id in v.formula.operands)
    return Overlay(tuple(values), tuple(applied), tuple(stale), tuple(acknowledgments),
                   tuple(sorted(set(dependencies))), a.canonical(events))


def serialize_overlay(value):
    if type(value) is not Overlay: raise h.InputError('Typed isolated overlay required')
    return a.canonical(dict(schema=OVERLAY_SCHEMA,values=[h._encode(v) for v in value.values],
        applied=list(value.applied),stale=list(value.stale),acknowledgments=list(value.acknowledgments),
        dependent_review=list(value.dependent_review),audit=_json(value.audit_json)))


def deserialize_overlay(text, prepared, store):
    expected = overlay(prepared, store)
    # Rebuild from the current anchored audit and source revision, not trust serialized approvals.
    if _json(text) != _json(serialize_overlay(expected)):
        raise h.InputError('Overlay differs from exact audit/source revision')
    return expected


def grouped_queue(prepared):
    """One group per annual field/actionable cause; original cards remain expandable."""
    groups = {}
    for card in a.review_queue(prepared):
        for cause in card['codes']:
            observation = card['payload'].get('binding', {}).get('category') in {
                'support_observation','component_observation','derivation_operand'}
            informational = cause == 'HISTORY_EXCEPTION' or (cause == 'PARTIAL_OR_UNREVIEWED_SCOPE'
                and observation and card['payload'].get('input', {}).get('value') is not None
                and 'CONFLICT' not in card['codes'])
            key = (card['ticker'], card['accession'], card['field'], cause, not informational)
            group = groups.setdefault(key, dict(group_id='group:'+a.digest(key),
                ticker=card['ticker'],aliases=card['aliases'],accession=card['accession'],
                annual_end=card['annual_end'],field=card['field'],cause=cause,
                field_target_id=card.get('field_target_id'),next_action=REVIEW_ACTIONS[cause],
                priority=card['priority'],actionable=not informational,
                action='REVIEW_ONLY_NO_AUTOMATIC_ACCEPTANCE',details=[]))
            group['details'].append(card)
    return tuple(sorted(groups.values(),key=lambda g:(g['priority'],g['ticker'],g['accession'] or '',g['field'],g['cause'])))


def queue_summary(prepared):
    groups = grouped_queue(prepared)
    return dict(diagnostics=len(a.review_queue(prepared)),groups=len(groups),
        actionable=sum(g['actionable'] for g in groups),informational=sum(not g['actionable'] for g in groups),
        causes=dict(Counter(g['cause'] for g in groups)))
