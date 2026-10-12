"""Retained four-pilot liability observations, not a debt resolver or aggregate.

The mapping evidence is not an issuer approval registry. Exact reviewed location
dimensions may identify a component; all other dimension populations stay outside
that component. Original parsers, receipts and historical input models are reused.
"""

from dataclasses import dataclass, replace
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

from . import historical_inputs as h
from .cash_flow_inputs import _instance
from .pilot_cash_investments import _Tags
from ..sec import filing_xbrl as x
from ..normalization.balance_sheet import CURRENT_PORTION_OF_LONG_TERM_DEBT_POLICY, LONG_TERM_DEBT_NONCURRENT_POLICY

EVIDENCE_PATH = Path(__file__).resolve().parents[3] / 'docs/pilot-debt-lease-evidence.json'
EVIDENCE_SHA256 = 'aac330aeccc9c132fcaa3e30054edacb25419cb2a12f2647567111d062945aec'


def dimensions(context):
    return tuple(f'{{{d.dimension.namespace}}}{d.dimension.local_name}=' +
        (f'{{{d.explicit_member.namespace}}}{d.explicit_member.local_name}' if d.explicit_member else d.typed_member_xml)
        for d in context.dimensions)


@dataclass(frozen=True)
class Candidate:
    value: Decimal
    precision: str
    occurrences: tuple[dict, ...]


@dataclass(frozen=True)
class Component:
    spec: dict
    candidates: tuple[Candidate, ...]
    selected: int | None
    reason: str | None


def review_for(source):
    body = EVIDENCE_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != EVIDENCE_SHA256:
        raise h.InputError('Reviewed debt/lease mapping evidence bytes changed')
    review = next((r for r in json.loads(body)['periods'] if r['bundle_id'] == source.bundle_id), None)
    if review is None:
        raise h.InputError('Only the four mapped source periods')
    return review


def inspect(source, review=None):
    review = review_for(source) if review is None else review
    period = source.period
    if review['bundle_id'] != source.bundle_id or review['period'] != dict(cik=period.cik,
            accession=period.accession, annual_start=str(period.annual_start), annual_end=str(period.annual_end), form=period.form):
        raise h.InputError('Exact source/annual identity required')
    instance = next(r for r in source.artifacts if r.artifact.url.endswith('_htm.xml'))
    primary = next(r for r in source.artifacts if r.artifact.url.endswith('.htm'))
    if (review['digest_type'] != 'sha256_sec_response_body_bytes' or any(
            review[k + '_sha256'] != r.artifact.sha256 or review[k + '_url'] != r.artifact.url
            for k, r in (('instance', instance), ('primary', primary)))):
        raise h.InputError('Exact original-body receipt binding required')
    root, _, _, ns = _instance(source.artifacts, period)
    contexts = {c.context_id: c for c in x._parse_contexts(root, ns)}
    units = {u.unit_id: u for u in x._parse_units(root, ns)}
    facts = x._parse_facts(root, contexts, units, period.accession, instance.artifact.url)
    ordinals = [i for i, e in enumerate(root) if e.get('contextRef') is not None]
    tags = _Tags(); tags.feed(primary.artifact.body.decode('utf-8'))
    text = ' '.join(' '.join(tags.parts).split())
    if any(note['text'] not in text for note in review['scope_notes']):
        raise h.InputError('Reviewed debt/lease note scope evidence missing')
    results = []
    for spec in review['components']:
        if spec['namespace'] != ns.get(spec['taxonomy']):
            raise h.InputError('Exact concept namespace required')
        policy = {'current_debt': CURRENT_PORTION_OF_LONG_TERM_DEBT_POLICY,
                  'noncurrent_debt': LONG_TERM_DEBT_NONCURRENT_POLICY}.get(spec['component_id'])
        if policy and not any(c.concept.taxonomy == spec['taxonomy'] and c.concept.name == spec['concept'] for c in policy.candidates):
            raise h.InputError('Existing direct current/noncurrent debt semantics required')
        groups = {}
        for fact, ordinal in zip(facts, ordinals):
            if (fact.namespace, fact.concept) != (spec['namespace'], spec['concept']): continue
            context = contexts[fact.context_id]
            if (context.entity_identifier_scheme != 'http://www.sec.gov/CIK' or int(context.entity_identifier) != period.cik
                    or context.start is not None or context.end != period.annual_end
                    or dimensions(context) != tuple(spec['dimensions'])): continue
            if (fact.is_nil or fact.numeric_value is None or fact.unit is None or fact.unit.denominator_measures
                    or fact.unit.numerator_measures != (x.FilingXBRLQName('http://www.xbrl.org/2003/iso4217', 'USD'),)
                    or not re.fullmatch(r'INF|-?\d+', fact.decimals or '')):
                raise h.InputError('Eligible component requires non-nil exact USD numeric/precision evidence')
            occurrence = dict(namespace=fact.namespace, concept=fact.concept, context_id=fact.context_id,
                entity_cik=period.cik, start=None, end=str(fact.end), unit_id=fact.unit_ref,
                raw_value=fact.raw_value, decimals=fact.decimals, ordinal=ordinal,
                normalized_unit='USD', dimensions=list(dimensions(context)), nil=False)
            groups.setdefault((fact.numeric_value, fact.decimals), []).append(occurrence)
        candidates = tuple(Candidate(v, precision, tuple(items)) for (v, precision), items in groups.items())
        matched = True
        for statement in spec['statements']:
            actual = tags.tags.get(statement['id'])
            if actual is None or any(actual[0].get(k) != v for k, v in statement['attributes'].items()) or actual[1].strip() != statement['displayed_value']:
                raise h.InputError('Reviewed inline representation changed')
            attrs, raw = actual
            value = Decimal(raw.strip().replace(',', '') + 'e' + attrs['scale'])
            if attrs.get('sign') == '-': value = value.copy_negate()
            matched &= any(c.value == value and any(o['context_id'] == attrs['contextref'] and
                o['unit_id'] == attrs['unitref'] and o['decimals'] == attrs['decimals'] for o in c.occurrences) for c in candidates)
        reason = ('No eligible exact year-end component bound in retained evidence; absence is not zero.' if not candidates
            else 'Differing eligible component values remain conflicting; no precedence or rounding adjustment.' if len({c.value for c in candidates}) != 1
            else 'No independently matching retained statement/note representation.' if not matched or not spec['statements'] else None)
        results.append(Component(spec, candidates, 0 if reason is None else None, reason))
    return review, tuple(results)


def mapping_entry(source, inspection=None):
    review, components = inspect(source) if inspection is None else inspection
    return dict(status='mapped', origin='reported', quality='limited', review='reviewed', scope='mixed',
        completeness='partial', aggregation='none', null_reason=None,
        unresolved_requirements=[u['component_id'] + ': ' + u['reason'] for u in review['unknowns']],
        bindings=[dict(input_id=c.spec['component_id'], origin='reported', role=c.spec['role'],
            population=c.spec['component_id'], unit='USD', scale=1, sign=1,
            precision=c.candidates[c.selected].precision if c.selected is not None else 'unknown',
            retained_debt=dict(evidence_sha256=EVIDENCE_SHA256, spec=c.spec, selected=c.selected, null_reason=c.reason,
                candidates=[dict(value_usd=str(a.value), occurrences=list(a.occurrences)) for a in c.candidates])) for c in components])


def values(row, source, entry):
    review, components = inspect(source)
    if entry != mapping_entry(source, (review, components)):
        raise h.InputError('Exact debt/lease component mapping required')
    instance = next(r for r in source.artifacts if r.artifact.url.endswith('_htm.xml'))
    primary = next(r for r in source.artifacts if r.artifact.url.endswith('.htm'))
    result = []
    for c in components:
        spec = c.spec; observations = []
        locator = dict(evidence_path='docs/pilot-debt-lease-evidence.json', evidence_sha256=EVIDENCE_SHA256,
            reviewed_period=review['period'], component=spec, scope_notes=review['scope_notes'], mapping_sha256=row.get('mapping_sha256'))
        for a in c.candidates:
            refs = tuple(h.SourceReference(f"{source.bundle_id}:{spec['component_id']}:ordinal-{o['ordinal']}", source.period,
                instance, json.dumps(dict(locator=locator, unit_id=o['unit_id'], nil=False), sort_keys=True), o['namespace'], o['concept'],
                o['context_id'], o['ordinal'], None, source.period.annual_end, 'USD', o['raw_value'], o['decimals'], tuple(o['dimensions'])) for o in a.occurrences)
            refs += (h.SourceReference(f"{source.bundle_id}:{spec['component_id']}:primary:{a.occurrences[0]['ordinal']}", source.period,
                primary, json.dumps(locator, sort_keys=True), '', '', '', None, None, source.period.annual_end, 'USD', str(a.value), a.precision, ()),)
            observations.append(h.InputValue(f"debt_lease:{spec['component_id']}:ordinal-{a.occurrences[0]['ordinal']}", h.Field.DEBT_LEASES,
                source.period, source.period.annual_end, a.value, 'USD', 1, 1, a.precision, spec['role'], h.Origin.REPORTED,
                h.Quality.LIMITED, spec['scope'], h.Scope.MIXED, h.Completeness.PARTIAL, h.Review.REVIEWED, refs, None, None, (),
                'Retained reported component only; taxonomy names do not establish principal/carrying/lease equivalence.',
                ('mapping_status:mapped', 'no_aggregation_or_valuation_authorization', 'separate_from_lease_cash_payments',
                 'possible_overlap:' + ','.join(spec['overlap_with'])), tuple(entry['unresolved_requirements']), None, (spec['component_id'],)))
        if c.selected is not None:
            result.append(replace(observations[c.selected], alternatives=tuple(v for i,v in enumerate(observations) if i != c.selected)))
        else:
            result.append(_null(source, spec['component_id'], c.reason, tuple(observations),
                h.Quality.CONFLICTING if len({a.value for a in c.candidates}) > 1 else h.Quality.LIMITED))
    result.extend(_null(source, u['component_id'], u['reason']) for u in review['unknowns'])
    return tuple(result)


def _null(source, identity, reason, alternatives=(), quality=h.Quality.UNASSESSED):
    return h.InputValue(f'debt_lease:{identity}:unresolved', h.Field.DEBT_LEASES, source.period, source.period.annual_end,
        None, 'USD', 1, 1, 'unknown', 'unavailable_debt_lease_requirement', h.Origin.UNAVAILABLE, quality, reason,
        h.Scope.UNKNOWN, h.Completeness.UNKNOWN, h.Review.REVIEWED, (), None, None, alternatives,
        'No inferred zero or approved debt total.', ('required_value_unresolved', 'no_aggregation_or_valuation_authorization'), (reason,), reason, ())
