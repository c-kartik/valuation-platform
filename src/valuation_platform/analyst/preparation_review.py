"""Analyst-facing preparation views; no extraction, decisions or financial totals."""
from __future__ import annotations

from collections import defaultdict
import json

from . import prepared_assembly as a, analyst_overrides as o, historical_inputs as h

SCHEMA = 'preparation-field-review-v1'
REPORT = 'docs/preparation-workflow-summary.json'


def _periods(prepared, view):
    if view not in ('full', 'latest'): raise h.InputError('Explicit full/latest view required')
    annuals = prepared.bundle.annuals
    return annuals if view == 'full' else annuals[-1:]


def _counts(items, observations, history):
    all_items = (*items, *observations)
    return dict(primary_items=len(items),informational_fields=len(observations),
        nested_actionable_causes=sum(c['actionable'] for item in all_items for c in item['causes']),
        nested_informational_causes=sum(not c['actionable'] for item in all_items for c in item['causes']),
        original_diagnostics=sum(len(item['diagnostics']) for item in all_items),
        invalid_evidence_diagnostics=sum('INVALID_EVIDENCE' in c['codes'] for item in all_items for c in item['diagnostics']),
        history_exceptions=len(history))


def primary_queue(prepared, view='full', priority=a.PRIORITY):
    """One actionable annual/field primary; cause memberships are not issue counts.

    Informational-only fields and history exceptions remain separately reachable.
    All original cards remain verbatim, deduplicated only by exact card identity.
    """
    if set(priority) != set(h.Field) or any(type(v) is not int or v < 1 for v in priority.values()):
        raise h.InputError('Explicit positive field-priority profile required')
    annuals = {v.period.accession:v for v in prepared.bundle.annuals}
    bindings = {(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)}
    populations = defaultdict(list); history = []
    for group in o.grouped_queue(prepared):
        if group['accession'] is None: history.append(group); continue
        populations[(group['accession'],group['field'])].append(group)
    items = []; observations = []
    for (accession,field), groups in populations.items():
        annual = annuals[accession]; cards = {}; causes = []
        for group in groups:
            for card in group['details']:
                old = cards.setdefault(card['target_id'],card)
                if old != card: raise h.InputError('Differing duplicate diagnostic identity')
            causes.append({**{k:v for k,v in group.items() if k != 'details'},
                'diagnostic_ids':[c['target_id'] for c in group['details']]})
        components = []
        for value in annual.inputs:
            if value.field.value != field: continue
            binding = bindings[(accession,value.input_id)]
            target_id = a.target(value.period,field,{'channel':binding['channel'],'input_id':value.input_id})
            components.append(dict(target_id=target_id,binding=binding,input=a.click(value),
                scope_status=value.scope_status.value,coverage_keys=list(value.coverage_keys),
                diagnostic_ids=[target_id] if target_id in cards else []))
        item = dict(target_id=a.target(annual.period,field,{'kind':'field'}),
            ticker=prepared.ticker,aliases=list(prepared.aliases),period=h._encode(annual.period),
            accession=accession,annual_end=str(annual.period.annual_end),field=field,
            priority=priority[h.Field(field)],actionable=any(g['actionable'] for g in groups),
            field_target_unambiguous=len(components)==1,
            override_constraints='Existing exact identity/unit/scope/evidence validation remains mandatory; no permission or completeness inferred.',
            component_targets=components,causes=sorted(causes,key=lambda c:(c['cause'],not c['actionable'])),
            diagnostics=[cards[k] for k in sorted(cards)],
            action='REVIEW_ONLY_NO_AUTOMATIC_ACCEPTANCE_OR_COMPLETENESS')
        (items if item['actionable'] else observations).append(item)
    ordering = lambda v:(v['priority'],-int(v['annual_end'].replace('-','')),v['field'],v['target_id'])
    items.sort(key=ordering); observations.sort(key=ordering)
    chosen = {v.period.accession for v in _periods(prepared,view)}
    selected = [v for v in items if v['accession'] in chosen]
    selected_info = [v for v in observations if v['accession'] in chosen]
    omitted = [v for v in items if v['accession'] not in chosen]
    omitted_info = [v for v in observations if v['accession'] not in chosen]
    return dict(schema=SCHEMA,ticker=prepared.ticker,aliases=list(prepared.aliases),view=view,
        selected_periods=len(chosen),full_history_periods=len(annuals),primary_items=selected,
        informational_fields=selected_info,history_exceptions=history,
        counts=_counts(selected,selected_info,history),full_history_counts=_counts(items,observations,history),
        outside_view_counts=_counts(omitted,omitted_info,[]),
        financial_sufficiency='NOT_ASSESSED')


def inspection_payload(prepared, view='full', store=None):
    """Separate original/effective displays; applied patches do not clear source issues."""
    overlay = None if store is None else o.overlay(prepared,store)
    patches = {} if overlay is None else {
        (v.period.accession,v.alternatives[0].input_id):v for v in overlay.values}
    bindings = {(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)}
    annuals = []
    for annual in _periods(prepared,view):
        values = []
        for source in annual.inputs:
            patch = patches.get((annual.period.accession,source.input_id))
            invalid_ratio=overlay is not None and annual.period.accession+'#'+source.input_id in overlay.dependent_review
            effective=a.click(source if patch is None else patch)
            if invalid_ratio:
                effective={**effective,'value':None,'null_reason':'Original reported ETR is inconsistent with an overridden operand; no adjusted ratio calculated.',
                    'origin':'unavailable','quality':'limited','formula':None,
                    'requirements':effective['requirements']+['Dependent reported ETR is invalidated; adjusted ratio requires a separate derivation contract.'],
                    'flags':effective['flags']+['dependent_etr_invalidated']}
            values.append(dict(input_id=source.input_id,field=source.field.value,
                target_id=a.target(source.period,source.field.value,{
                    'channel':bindings[(annual.period.accession,source.input_id)]['channel'],'input_id':source.input_id}),
                binding=bindings[(annual.period.accession,source.input_id)],
                original=a.click(source),effective=effective,
                effective_basis='DEPENDENT_ETR_INVALIDATED' if invalid_ratio else 'SOURCE_UNCHANGED' if patch is None else 'SEPARATE_ANALYST_OVERLAY',
                scope_status=source.scope_status.value,coverage_keys=list(source.coverage_keys)))
        annuals.append(dict(bundle_id=annual.bundle_id,period=h._encode(annual.period),
            inputs=values,limitations=list(annual.limitations)))
    return dict(schema=SCHEMA,ticker=prepared.ticker,aliases=list(prepared.aliases),view=view,
        bundle=dict(history_id=prepared.bundle.history_id,annuals=annuals,
            history_exceptions=list(prepared.bundle.history_exceptions)),
        quality_full_history=a.quality(prepared),queue=primary_queue(prepared,view),
        overlay=None if overlay is None else json.loads(o.serialize_overlay(overlay)),
        financial_sufficiency='NOT_ASSESSED')


def summary(histories):
    per = {name:{view:primary_queue(p,view)['counts'] for view in ('full','latest')}
           for name,p in sorted(histories.items())}
    keys = next(iter(per.values()))['full'].keys()
    return dict(schema=SCHEMA,issuers=len(per),selected_periods=sum(len(p.bundle.annuals) for p in histories.values()),
        per_issuer=per,totals={view:{key:sum(p[view][key] for p in per.values()) for key in keys}
                             for view in ('full','latest')})
