"""Opt-in assembly and read-only review; no new field resolver or acceptance."""
from collections import Counter,defaultdict
from dataclasses import dataclass,fields,replace
from hashlib import sha256
from types import MappingProxyType
import json,csv
from decimal import Decimal
from . import historical_inputs as h,refreshed_capex as parent,retained_d_and_a as da
from . import retained_bridge_components as bridge,retained_claims_shares as claims
from . import retained_cfo_preparation as cfo

ROOT=parent.capex.shared.ROOT
SCHEMA='assembled-historical-input-review-v1'
REPORT='docs/prepared-assembly-summary.json'
LEDGERS=('docs/repaired-income-ledger.json','docs/approved-income-integration-bindings.json',
    'docs/retained-cfo-ledger.json','docs/retained-working-capital-ledger.json','docs/retained-tax-sbc-ledger.json',
    'docs/refreshed-capex-ledger.json',da.LEDGER,bridge.LEDGER,claims.LEDGER)
PRIMARY=frozenset((h.Field.REVENUE,h.Field.EBIT,h.Field.DA,h.Field.CAPEX,h.Field.CFO))
# Configured review order, not confidence or materiality scores. No acceptance
# threshold is implied by position. Overrides of this ordering must be explicit.
ORDER=(h.Field.REVENUE,h.Field.EBIT,h.Field.CFO,h.Field.CAPEX,h.Field.DA,h.Field.CF_WORKING_CAPITAL,
       h.Field.DEFERRED_TAX,h.Field.SBC,h.Field.TAX,h.Field.CFO_RESIDUAL,h.Field.CASH_INVESTMENTS,
       h.Field.DEBT_LEASES,h.Field.OTHER_BRIDGE,h.Field.SHARES)
PRIORITY=MappingProxyType({f:i+1 for i,f in enumerate(ORDER)})
LIMITS=('Assembly does not resolve required values, conflicts or scope, or authorize financial consumption.',
        'Support, operands and partial populations are not totals or additional economic charges.',
        'No residual, aggregation, analyst assumption, acceptance, sufficiency or valuation calculation.',
        'Original parents/pilots and frozen financial outputs remain separate and unchanged.')


def canonical(v):return parent.canonical(v)
def digest(v):return sha256(canonical(v).encode()).hexdigest()
def unwrap(v):return v.bundle if type(v) is parent.RefreshedHistory else v
def aliases_for(cik):
    with (ROOT/'docs/universe/sp500-top-50-2026-10-02.csv').open() as source:
        return tuple(sorted({v['project_ticker'] for v in csv.DictReader(source) if int(v['sec_cik'])==cik}))


def seals():return tuple((path,sha256((ROOT/path).read_bytes()).hexdigest()) for path in LEDGERS)


def diagnostics(original):
    """Retain existing errors/status/overlap locations, not new fact extraction."""
    accessions={a.period.accession for a in unwrap(original).annuals};out=[]
    for path in LEDGERS:
        doc=json.loads((ROOT/path).read_text())
        for i,row in enumerate(doc.get('rows',[])):
            acc=row.get('identity',{}).get('accession')
            if acc not in accessions:continue
            errors={}
            for f,v in row.get('fields',{}).items() if type(row.get('fields')) is dict else ():
                if v.get('errors'):errors[f]=v['errors']
            if row.get('evidence_errors'):errors[h.Field.DA.value]=row['evidence_errors']
            if row.get('errors') and path=='docs/retained-working-capital-ledger.json':
                errors[h.Field.CF_WORKING_CAPITAL.value]=row['errors']
            out.append(dict(accession=acc,ledger=path,locator='/rows/'+str(i),
                errors=errors,record_status=row.get('status'),
                field_statuses={f:v.get('status') for f,v in row.get('fields',{}).items()} if type(row.get('fields')) is dict else {},
                overlap_metadata=[dict(concept=v.get('concept'),possible_children=v.get('possible_children',[]))
                    for v in row.get('observations',[]) if v.get('possible_children')]))
    return canonical(out)


def combine(original,ds,bs,cs):
    """Copy exact existing InputValues; only container identities are new."""
    history=unwrap(original);mapping=[];annuals=[]
    for a,d,b,c in zip(history.annuals,ds,bs,cs):
        if not a.period==d.period==b.period==c.period:raise h.InputError('Exact period-aligned overlays required')
        selected={};bindings={}
        operands={o for v in a.inputs if v.formula for o in v.formula.operands}
        def add(v,category,channel):
            if v.input_id in selected:
                if selected[v.input_id]!=v:raise h.InputError('Conflicting duplicate input identity')
                return
            selected[v.input_id]=v;bindings[v.input_id]=dict(accession=a.period.accession,input_id=v.input_id,
                field=v.field.value,category=category,channel=channel)
        for v in a.inputs:
            if v.field in (h.Field.DA,h.Field.CASH_INVESTMENTS,h.Field.DEBT_LEASES,h.Field.OTHER_BRIDGE,h.Field.SHARES):
                if v.value is not None:add(v,'support_observation','original_parent')
                elif v.review is not h.Review.UNREVIEWED and v.field is not h.Field.DA:
                    add(v,'unresolved_requirement','original_parent')
                continue  # Old placeholders remain in attached original parent.
            category=('unresolved_requirement' if v.value is None else 'derivation_operand' if v.input_id in operands else
                'support_observation' if any(f.startswith('support_only') for f in v.flags) or v.field not in PRIMARY else 'prepared_value')
            add(v,category,'original_parent')
        add(d.required_value,'prepared_value' if d.required_value.value is not None else 'unresolved_requirement','d_and_a')
        for v in d.support_only:add(v,'support_observation','d_and_a')
        for v in d.operands:add(v,'derivation_operand','d_and_a')
        for channel,values in (('instant_components',(*b.cash_investments,*b.debt_leases)),('claims_shares',(*c.other_bridge,*c.shares))):
            for v in values:add(v,'component_observation' if v.value is not None else 'unresolved_requirement',channel)
        vv=tuple(sorted(selected.values(),key=lambda v:(list(h.Field).index(v.field),v.input_id)))
        annuals.append(h.AnnualBundle('assembled-inputs:'+a.period.accession,1,a.period,vv,
            tuple(dict.fromkeys((*a.limitations,*LIMITS)))))
        mapping.extend(bindings[v.input_id] for v in vv)
    if not len(history.annuals)==len(ds)==len(bs)==len(cs):raise h.InputError('Every selected annual requires all overlays')
    return h.HistoryBundle('assembled-inputs:'+str(history.cik),1,history.cik,tuple(annuals),history.history_exceptions),canonical(mapping)


@dataclass(frozen=True)
class PreparedHistory:
    ticker:str
    aliases:tuple[str,...]
    original:h.HistoryBundle|parent.RefreshedHistory
    d_and_a:tuple[da.AnnualDAndA,...]
    instant:tuple[bridge.AnnualComponents,...]
    claims_shares:tuple[claims.AnnualClaimsShares,...]
    bundle:h.HistoryBundle
    bindings_json:str
    diagnostics_json:str
    ledger_seals:tuple[tuple[str,str],...]

    def __post_init__(self):
        h._text(self.ticker);h._strings(self.aliases)
        if self.ticker not in self.aliases or self.aliases!=aliases_for(unwrap(self.original).cik) or self.ledger_seals!=seals():raise h.InputError('Exact ticker/retained ledger revision required')
        if type(self.original) not in (h.HistoryBundle,parent.RefreshedHistory):raise h.InputError('Original typed parent required')
        for vv,cls in ((self.d_and_a,da.AnnualDAndA),(self.instant,bridge.AnnualComponents),(self.claims_shares,claims.AnnualClaimsShares)):
            h._typed(vv,cls)
        expected,mapping=combine(self.original,self.d_and_a,self.instant,self.claims_shares)
        if (self.bundle,self.bindings_json)!=(expected,mapping):raise h.InputError('Assembled values/bindings differ from original materialized inputs')
        if self.diagnostics_json!=diagnostics(self.original):raise h.InputError('Invalid evidence/diagnostic ledger binding differs')


def source_payload(s):
    a=s.receipt.artifact
    return dict(source_id=s.source_id,accession=s.period.accession,url=a.url,body_reference=a.sha256,
        digest_type=a.digest_type,representation=a.representation,retrieved_at_utc=s.receipt.retrieved_at_utc,
        http_status=s.receipt.http_status,locator=s.locator,namespace=s.namespace,concept=s.concept,
        context_id=s.context_id,ordinal=s.occurrence_ordinal,dimensions=list(s.dimensions),unit=s.unit,
        raw_value=s.raw_value,precision=s.decimals,start=None if s.start is None else str(s.start),end=str(s.end))


def validate_parent(original):
    """Check existing ledger values and original occurrences, not new selection."""
    income={r['identity']['accession']:r for r in json.loads((ROOT/LEDGERS[0]).read_text())['rows']}
    cash={r['identity']['accession']:r for r in json.loads((ROOT/'docs/retained-cfo-ledger.json').read_text())['rows']}
    capex={r['identity']['accession']:r for r in json.loads((ROOT/parent.LEDGER).read_text())['rows']}
    for a in unwrap(original).annuals:
        e=cfo.prepare(a);facts={i:f for f,i in e.facts}
        operands={o for v in a.inputs if v.formula for o in v.formula.operands}
        roots={v.field:v for v in a.inputs if v.field in PRIMARY and v.input_id not in operands and not any(f.startswith('support_only') for f in v.flags)}
        for f in (h.Field.REVENUE,h.Field.EBIT):
            slot=next(v for v in income[a.period.accession]['fields'] if v['field']==f.value)
            expected=(slot['value_usd'] if 'value_usd' in slot else
                slot['candidates'][slot['selected']]['value_usd'] if slot.get('selected') is not None else None)
            actual=roots[f].value
            if actual!=(None if expected is None else Decimal(expected)):raise h.InputError('Original income differs from committed ledger')
            if roots[f].formula and roots[f].formula.expression!=slot['formula']['expression']:raise h.InputError('Existing registered equation differs')
        for f,records in ((h.Field.CFO,cash),(h.Field.CAPEX,capex)):
            expected=records[a.period.accession]['value_usd']
            if roots[f].value!=(None if expected is None else Decimal(expected)):raise h.InputError('Original cash-flow input differs from ledger')
        def check(v):
            for s in v.sources:
                if s.occurrence_ordinal is None:continue  # Original note provenance remains attached.
                fact=facts.get(s.occurrence_ordinal)
                if (s.receipt.artifact.sha256!=e.instance.artifact.sha256 or fact is None or fact.is_nil or
                    (fact.namespace,fact.concept,fact.context_id,fact.start,fact.end,fact.decimals)!=
                    (s.namespace,s.concept,s.context_id,s.start,s.end,s.decimals) or fact.numeric_value!=Decimal(s.raw_value)):
                    raise h.InputError('Original input source differs from retained occurrence')
            for alt in v.alternatives:check(alt)
        for v in a.inputs:check(v)


def click(v):
    return dict(input_id=v.input_id,value=None if v.value is None else str(v.value),origin=v.origin.value,role=v.role,
        unit=v.unit,scale=v.scale,sign=v.sign,precision=v.precision,as_of=None if v.as_of is None else str(v.as_of),
        quality=v.quality.value,completeness=v.completeness.value,review=v.review.value,scope=v.scope,
        null_reason=v.null_reason,requirements=list(v.unresolved_requirements),flags=list(v.flags),
        formula=None if v.formula is None else h._encode(v.formula),sources=[source_payload(s) for s in v.sources],
        alternatives=[click(a) for a in v.alternatives])


def target(period,field,population):
    return 'review:'+str(period.cik)+':'+period.accession+':'+field+':'+digest(population)[:24]


def for_ticker(histories,ticker):
    matches=[v for v in histories.values() if ticker in v.aliases]
    if len(matches)!=1:raise h.InputError('One non-specialized issuer history required for ticker')
    return matches[0]  # Security alias lookup is not a share-class mapping.


def review_queue(prepared,priority=PRIORITY):
    if set(priority)!=set(h.Field) or any(type(v) is not int or v<1 for v in priority.values()):raise h.InputError('Explicit positive field-importance order required')
    bb={(v['accession'],v['input_id']):v for v in json.loads(prepared.bindings_json)};queue=[]
    diagnostics_by=defaultdict(list)
    for d in json.loads(prepared.diagnostics_json):diagnostics_by[d['accession']].append(d)
    for annual in prepared.bundle.annuals:
        p=annual.period;known=defaultdict(list)
        for v in annual.inputs:
            for s in v.sources:known[(s.receipt.artifact.sha256,s.occurrence_ordinal,s.context_id,s.namespace,s.concept)].append(v.input_id)
        def item(field,pop,reason,codes,payload):
            queue.append(dict(target_id=target(p,field.value,pop),ticker=prepared.ticker,aliases=list(prepared.aliases),
                accession=p.accession,annual_end=str(p.annual_end),field=field.value,priority=priority[field],
                codes=sorted(set(codes)),reasons=list(dict.fromkeys(reason)),payload=payload,
                action='REVIEW_ONLY_NO_ACCEPTANCE_OR_BLOCKER_REMOVAL'))
        for v in annual.inputs:
            binding=bb[(p.accession,v.input_id)];codes=[];reasons=[]
            if v.value is None:codes.append('MISSING_REQUIRED_VALUE');reasons.append(v.null_reason)
            if v.quality is h.Quality.CONFLICTING:codes.append('CONFLICT');reasons.append('Competing candidates remain unselected.')
            if v.completeness is not h.Completeness.COMPLETE or v.scope_status in (h.Scope.UNKNOWN,h.Scope.RESTRICTED,h.Scope.MIXED):
                codes.append('PARTIAL_OR_UNREVIEWED_SCOPE');reasons.append(v.scope)
            overlap=[f for f in v.flags if 'overlap' in f and not f.endswith(':')]
            shared=sorted({other for s in v.sources for other in known[(s.receipt.artifact.sha256,s.occurrence_ordinal,s.context_id,s.namespace,s.concept)] if other!=v.input_id})
            if overlap or shared:codes.append('OVERLAP_WARNING');reasons.append('Known same-source reuse or possible parent/component overlap; not independent amounts.')
            if v.unresolved_requirements:codes.append('UNRESOLVED_REQUIREMENTS');reasons.extend(v.unresolved_requirements)
            if codes:item(v.field,dict(channel=binding['channel'],input_id=v.input_id),reasons,codes,
                dict(binding=binding,input=click(v),shared_source_inputs=shared,overlap_flags=overlap))
            if codes and any(f.startswith(parent.MARKER) for f in v.flags):
                audit=next(a for a in prepared.original.refresh_audits if a.input_id==v.input_id)
                queue[-1]['payload']['refresh_provenance']=dict(refresh_id=audit.refresh_id,version=audit.refresh_version,
                    policy_id=audit.financial_policy_id,policy_version=audit.financial_policy_version,
                    original_entry_sha256=audit.original_entry_sha256,original_byte_equivalence=audit.original_byte_equivalence,
                    acceptance_basis=audit.acceptance_basis,review_path=audit.review_path,review_sha256=audit.review_sha256,
                    artifacts=[dict(historical_sha256=a.historical_sha256,historical_digest_type=a.historical_digest_type,
                        original_status=a.historical_status,refreshed=dict(url=a.refreshed_receipt.artifact.url,
                            body_reference=a.refreshed_receipt.artifact.sha256,digest_type=a.refreshed_receipt.artifact.digest_type,
                            representation=a.refreshed_receipt.artifact.representation,retrieved_at_utc=a.refreshed_receipt.retrieved_at_utc,
                            http_status=a.refreshed_receipt.http_status,retrieval_mode=a.refreshed_receipt.retrieval_mode,
                            receipt_path=a.receipt_path,receipt_locator=a.receipt_locator),supports=list(a.supported_requirements)) for a in audit.artifacts])
        for d in diagnostics_by[p.accession]:
            for f,errors in d['errors'].items():
                item(h.Field(f),dict(ledger=d['ledger'],locator=d['locator'],field=f),errors,['INVALID_EVIDENCE'],
                    dict(ledger=d['ledger'],locator=d['locator'],ledger_sha256=dict(prepared.ledger_seals)[d['ledger']],
                         errors=errors,accepted_value=False))
            if d['overlap_metadata']:
                item(h.Field.CF_WORKING_CAPITAL,dict(ledger=d['ledger'],locator=d['locator'],kind='movement_overlap'),
                    ['Retained movement parents/children may overlap; no total is calculated.'],['OVERLAP_WARNING'],d)
    for i,reason in enumerate(prepared.bundle.history_exceptions):
        queue.append(dict(target_id='review:'+str(prepared.bundle.cik)+':history:'+str(i),ticker=prepared.ticker,
            aliases=list(prepared.aliases),accession=None,annual_end=None,field='history',priority=0,
            codes=['HISTORY_EXCEPTION'],reasons=[reason],payload=dict(selected_periods=len(prepared.bundle.annuals)),
            action='REVIEW_ONLY_NO_ACCEPTANCE_OR_BLOCKER_REMOVAL'))
    for q in queue:
        if q['accession'] is not None:
            p=next(a.period for a in prepared.bundle.annuals if a.period.accession==q['accession'])
            q['field_target_id']=target(p,q['field'],dict(kind='field'))
    return sorted(queue,key=lambda q:(q['priority'], -(int(q['annual_end'].replace('-','')) if q['annual_end'] else 0),q['field'],q['target_id']))


def quality(prepared):
    bb={(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)};summary={}
    for f in h.Field:
        vv=[(a,v,bb[(a.period.accession,v.input_id)]) for a in prepared.bundle.annuals for v in a.inputs if v.field is f]
        summary[f.value]=dict(selected_periods=len(prepared.bundle.annuals),
            periods_with_values=len({a.period.accession for a,v,b in vv if v.value is not None}),
            policy_prepared_value_periods=len({a.period.accession for a,v,b in vv if v.value is not None and b['category']=='prepared_value'}),
            periods_with_conflicts=len({a.period.accession for a,v,b in vv if v.quality is h.Quality.CONFLICTING}),
            unresolved_periods=len({a.period.accession for a,v,b in vv if v.value is None or v.unresolved_requirements or v.completeness is not h.Completeness.COMPLETE}),
            valued_inputs=sum(v.value is not None for a,v,b in vv),support_observations=sum(v.value is not None and b['category'] in ('support_observation','component_observation') for a,v,b in vv),
            derivation_operands=sum(b['category']=='derivation_operand' for a,v,b in vv),unresolved_entries=sum(v.value is None for a,v,b in vv),
            origins=dict(Counter(v.origin.value for a,v,b in vv)),completeness=dict(Counter(v.completeness.value for a,v,b in vv)))
    return dict(fields=summary,history_exceptions=list(prepared.bundle.history_exceptions),financial_sufficiency='NOT_ASSESSED')


def build():
    old,parents,claim_overlays,prior=claims.build();store=da.artifact_store();out={}
    with (ROOT/'docs/universe/sp500-top-50-2026-10-02.csv').open() as source:
        security=list(csv.DictReader(source))
    for ticker,original in parents.items():
        ds=[];bs=[];cs=claim_overlays[ticker]
        for a in unwrap(original).annuals:
            e=cfo.prepare(a);d,_=da.package(e,store);b,_=bridge.overlay(e);ds.append(d);bs.append(b)
        bundle,bindings=combine(original,tuple(ds),tuple(bs),cs)
        aliases=tuple(sorted({v['project_ticker'] for v in security if int(v['sec_cik'])==bundle.cik}))
        out[ticker]=PreparedHistory(ticker,aliases,original,tuple(ds),tuple(bs),cs,bundle,bindings,diagnostics(original),seals())
    per={name:dict(quality=quality(v),review_count=len(review_queue(v)),review_codes=dict(Counter(code for q in review_queue(v) for code in q['codes']))) for name,v in out.items()}
    aggregate={f.value:{key:sum(per[n]['quality']['fields'][f.value][key] for n in out)
        for key in ('selected_periods','periods_with_values','policy_prepared_value_periods','periods_with_conflicts','unresolved_periods','valued_inputs','support_observations','derivation_operands','unresolved_entries')} for f in h.Field}
    report=dict(schema=SCHEMA,issuer_count=len(out),selected_periods=sum(len(v.bundle.annuals) for v in out.values()),
        field_slots=sum(len(v.bundle.annuals)*len(h.Field) for v in out.values()),history_target_deficits=len(old['history_exceptions']),
        history_exception_issuers=[n for n,v in out.items() if v.bundle.history_exceptions],priority_profile={f.value:v for f,v in PRIORITY.items()},
        field_coverage=aggregate,review_count=sum(v['review_count'] for v in per.values()),
        review_codes=dict(sum((Counter(v['review_codes']) for v in per.values()),Counter())),issuers=per,
        source_ledgers=dict(seals()),financial_sufficiency='NOT_ASSESSED',limitations=list(LIMITS))
    return report,out


def serialize(value):
    if type(value) is not PreparedHistory:raise h.InputError('Typed prepared history required')
    value.__post_init__();bodies={}
    def overlay(v):return dict(fields={f.name:parent._encode(getattr(v,f.name),bodies) for f in fields(v)})
    entry=dict(ticker=value.ticker,aliases=list(value.aliases),original=parent._encode(value.original,bodies),
        d_and_a=[overlay(v) for v in value.d_and_a],instant=[overlay(v) for v in value.instant],claims_shares=[overlay(v) for v in value.claims_shares],
        bundle=parent._encode(value.bundle,bodies),bindings_json=value.bindings_json,diagnostics_json=value.diagnostics_json,
        ledger_seals=[list(s) for s in value.ledger_seals])
    return canonical(dict(schema=SCHEMA,entry=entry,original_bodies=bodies))


def deserialize(payload):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise h.InputError('Duplicate assembly key')
            d[k]=v
        return d
    try:
        doc=json.loads(payload,object_pairs_hook=unique)
        if set(doc)!={'schema','entry','original_bodies'} or doc['schema']!=SCHEMA:raise h.InputError('Closed assembly envelope required')
        e=doc['entry']
        if set(e)!={f.name for f in fields(PreparedHistory)}:raise h.InputError('Closed prepared history fields required')
        bodies={};used=set()
        for key,v in doc['original_bodies'].items():
            raw=h._decode(v)
            if type(raw) is not bytes or sha256(raw).hexdigest()!=key:raise h.InputError('Changed original body')
            bodies[key]=raw
        def overlays(entries,cls):
            result=[]
            for v in entries:
                if set(v)!={'fields'} or set(v['fields'])!={f.name for f in fields(cls)}:raise h.InputError('Closed overlay fields required')
                result.append(cls(**{k:parent._decode(val,bodies,used) for k,val in v['fields'].items()}))
            return tuple(result)
        value=PreparedHistory(e['ticker'],tuple(e['aliases']),parent._decode(e['original'],bodies,used),
            overlays(e['d_and_a'],da.AnnualDAndA),overlays(e['instant'],bridge.AnnualComponents),overlays(e['claims_shares'],claims.AnnualClaimsShares),
            parent._decode(e['bundle'],bodies,used),e['bindings_json'],e['diagnostics_json'],tuple(tuple(s) for s in e['ledger_seals']))
        if used!=set(bodies):raise h.InputError('Unused body references')
        for v in value.d_and_a:da.validate_overlay(v)
        for v in value.instant:bridge.validate_overlay(v)
        for v in value.claims_shares:claims.validate_overlay(v)
        validate_parent(value.original)
        return value
    except (ValueError,KeyError,TypeError) as exc:raise h.InputError('Invalid assembled preparation payload') from exc
