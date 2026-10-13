"""Reusable reported CFO subtotal inspection. No reconciliation or adjustments."""
from collections import Counter
from dataclasses import replace
import hashlib
import json
from . import historical_inputs as h, retained_components as inspection
from . import repaired_income_preparation as income, retained_income_preparation as missing
from . import retained_income_batch as batch, nvda_income_inputs as nvda
from . import pilot_historical_inputs as pilot

CONCEPT='NetCashProvidedByUsedInOperatingActivities'
SCOPES={CONCEPT:('reported_consolidated_cfo_subtotal',h.Scope.CONSOLIDATED_REPORTED),
    CONCEPT+'ContinuingOperations':('reported_continuing_operations_cfo_subtotal',h.Scope.RESTRICTED),
    CONCEPT+'DiscontinuedOperations':('reported_discontinued_operations_cfo_subtotal',h.Scope.RESTRICTED)}
LIMITATIONS=('Reported CFO is not FCFF, organic/unlevered cash flow or reconstructed book delta NWC.',
    'Subtotal extraction does not validate CFO reconciliation, acquisition/FX effects, tax/interest/lease scope or future consumer sufficiency.',
    'Scope alternatives are distinct populations, not additive or substitutable; no absent component is zero.',
    'Exact approved standard root concept/entity/annual context establishes reported subtotal scope; independent face-placement re-review not performed.')


def receipt_of(annual):
    receipts={}
    def visit(v):
        for s in v.sources:
            if s.receipt.artifact.url.endswith('_htm.xml'):
                key=(s.receipt.artifact.url,s.receipt.artifact.sha256)
                if key in receipts and receipts[key]!=s.receipt:raise h.InputError('Conflicting actual receipt metadata')
                receipts[key]=s.receipt
        for a in v.alternatives:visit(a)
    for v in annual.inputs:visit(v)
    if len(receipts)!=1:raise h.InputError('One exact retained instance/receipt required; no synthesized binding')
    return next(iter(receipts.values()))


def prepare(annual):
    receipt=receipt_of(annual)
    return inspection.prepare(annual.period,(receipt,),
        (inspection.ArtifactBinding(receipt.artifact.url,receipt.artifact.sha256,'instance'),))


def inspect(evidence):
    ns=evidence.namespaces.get('us-gaap')
    if ns is None or not ns.startswith('http://fasb.org/us-gaap/'):
        return None,'Approved standard US-GAAP CFO namespace unavailable.'
    specification=inspection.SelectionSpec(h.Field.CFO.value,tuple(inspection.Selector(ns,c,()) for c in SCOPES),
        'annual','USD','reported_cfo_scope_candidate','Exact standard root total versus distinct continuing/discontinued scope; no aggregation.',LIMITATIONS)
    try:return inspection.inspect(evidence,specification),None
    except h.InputError as exc:return None,'Eligible CFO evidence has invalid unit/nil/numeric/precision or structural binding: '+str(exc)


def observations(evidence,result):
    if result is None:return ()
    values=[]
    for c in result.candidates:
        role,scope=SCOPES[c.concept]
        values.append(h.InputValue(f'retained-cfo:{c.concept}:root-{c.occurrences[0].ordinal}',h.Field.CFO,evidence.period,None,
            c.value,'USD',1,1,c.precision,role,h.Origin.REPORTED,h.Quality.LIMITED,role,
            scope,h.Completeness.PARTIAL,h.Review.REVIEWED,c.evidence_references,None,None,(),
            'Exact reported observation; root total alone may populate CFO. Scope alternatives are never summed or substituted.',
            ('reported_subtotal_only','not_fcff_or_organic','not_book_delta_nwc','cfo_reconciliation_not_validated',
             'independent_face_placement_not_reviewed')+(() if c.concept==CONCEPT else ('non_substitutable_scope_alternative',)),
            LIMITATIONS,None,(role,)))
    return tuple(values)


def select(evidence,result,error=None):
    values=observations(evidence,result)
    roots=[] if result is None else [i for i,c in enumerate(result.candidates) if c.concept==CONCEPT]
    distinct=set() if result is None else {result.candidates[i].value for i in roots}
    if error:status='UNAVAILABLE';reason=error
    elif any(s.startswith('Missing retained') for s in evidence.unresolved_requirements):status='UNAVAILABLE';reason='Required original body/receipt missing.'
    elif len(distinct)>1:status='CONFLICTING';reason='Unequal eligible consolidated CFO totals; occurrence order cannot choose a value.'
    elif not roots:status='UNAVAILABLE';reason='No exact annual nondimensional consolidated CFO root; continuing/discontinued or comparative/component observations cannot substitute.'
    else:
        index=roots[0]
        return replace(values[index],alternatives=tuple(v for i,v in enumerate(values) if i!=index)),'POPULATED',index
    v=missing.unavailable(evidence.period,h.Field.CFO,reason,h.Review.REVIEWED)
    return replace(v,alternatives=values,quality=h.Quality.CONFLICTING if status=='CONFLICTING' else h.Quality.LIMITED,
                   unresolved_requirements=v.unresolved_requirements+evidence.unresolved_requirements+LIMITATIONS),status,None


def fact_ledger(evidence):
    """Retain scope/comparative/dimension populations without monetary sums."""
    rows=[];p=evidence.period
    for f,i in evidence.facts:
        if f.concept not in SCOPES or not f.namespace.startswith('http://fasb.org/us-gaap/'):continue
        c=evidence.contexts[f.context_id];dims=inspection.dimensions(c)
        exclusion=('DIMENSIONED_COMPONENT' if dims else 'OTHER_PERIOD_COMPARATIVE_OR_NONANNUAL' if (c.start,c.end)!=(p.annual_start,p.annual_end)
            else 'ENTITY_MISMATCH' if int(c.entity_identifier)!=p.cik or c.entity_identifier_scheme!='http://www.sec.gov/CIK' else 'EXACT_ANNUAL_SCOPE_CANDIDATE')
        rows.append(dict(ordinal=i,namespace=f.namespace,concept=f.concept,context_id=f.context_id,entity=c.entity_identifier,
            start=None if c.start is None else str(c.start),end=str(c.end),dimensions=list(dims),unit_id=f.unit_ref,
            unit=None if f.unit is None else dict(numerator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.numerator_measures],
                denominator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.denominator_measures]),
            raw_value=f.raw_value,numeric_value=None if f.numeric_value is None else str(f.numeric_value),precision=f.decimals,nil=f.is_nil,
            disposition=exclusion,source_url=f.source_url,instance_sha256=evidence.instance.artifact.sha256))
    return rows


def build():
    income_ledger,histories=income.build();annuals={}
    for history in (*histories.values(),*batch.build()[1].values(),nvda.load_history()):
        for a in history.annuals:
            key=(a.period.cik,a.period.accession)
            if key in annuals:raise h.InputError('Duplicate exact annual packaging')
            annuals[key]=a
    pilots={}
    for name in ('MSFT','AAPL','GOOGL'):
        for a in pilot.load_history(name).annuals:
            key=(a.period.cik,a.period.accession);pilots[key]=a;annuals[key]=a
    if len(annuals)!=income_ledger['selected_periods']:raise h.InputError('Exact retained annual accounting differs')
    rows=[];out={};backlog={}
    for row in income_ledger['rows']:
        identity=row['identity'];key=(identity['cik'],identity['accession']);annual=annuals[key]
        if key in pilots:
            value=next(v for v in annual.inputs if v.field is h.Field.CFO)
            status='POPULATED' if value.value is not None else 'UNAVAILABLE';selected=None;facts=[]
            source='UNCHANGED_PREVIOUSLY_REVIEWED_PILOT';evidence=None
        else:
            source='RETAINED_EXACT_INSTANCE_SUBTOTAL_ONLY'
            try:
                evidence=prepare(annual);result,error=inspect(evidence);value,status,selected=select(evidence,result,error)
                facts=fact_ledger(evidence)
            except (ValueError,KeyError) as exc:
                evidence=None;facts=[];status='UNAVAILABLE';selected=None
                reason='Retained CFO identity/body/receipt/structure unavailable: '+type(exc).__name__+': '+str(exc)
                value=missing.unavailable(annual.period,h.Field.CFO,reason,h.Review.UNREVIEWED)
                backlog[key]=dict(identity=identity,requirement=reason,required_artifact='Exact selected instance/verified receipt; no acquisition in this pass.')
            annual=replace(annual,inputs=tuple(value if v.field is h.Field.CFO else v for v in annual.inputs))
        out.setdefault(row['issuer'],[]).append(annual)
        candidates=(value,*value.alternatives) if value.value is not None else value.alternatives
        rows.append(dict(issuer=row['issuer'],identity=identity,status=status,origin=value.origin.value,
            value_usd=None if value.value is None else str(value.value),unit=value.unit,scale=value.scale,sign=value.sign,precision=value.precision,
            role=value.role,scope=value.scope,completeness=value.completeness.value,evidence_depth=source,selected_candidate=selected,
            null_reason=value.null_reason,unresolved_requirements=list(value.unresolved_requirements),
            candidates=[dict(input_id=v.input_id,value_usd=str(v.value),role=v.role,scope=v.scope,precision=v.precision,flags=list(v.flags),
                sources=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                    digest_type=s.receipt.artifact.digest_type,representation=s.receipt.artifact.representation,
                    retrieved_at_utc=s.receipt.retrieved_at_utc,http_status=s.receipt.http_status,retrieval_mode=s.receipt.retrieval_mode,
                    ordinal=s.occurrence_ordinal,context_id=s.context_id,namespace=s.namespace,concept=s.concept,raw_value=s.raw_value,precision=s.decimals,
                    start=None if s.start is None else str(s.start),end=str(s.end)) for s in v.sources]) for v in candidates],facts=facts,
            income_fields=row['fields']))
    validation=json.loads((nvda.ROOT/sweep_classification()).read_text());summary={};packages={}
    for issuer in validation['rows']:
        if issuer['classification']=='SPECIALIZED_METHODOLOGY_REQUIRED':continue
        name=issuer['execution_ticker'];aa=tuple(sorted(out.get(name,[]),key=lambda a:a.period.annual_end))
        packages[name]=h.HistoryBundle('retained-reported-cfo:'+name,1,issuer['cik'],aa,
            () if len(aa)==5 else ('Frozen selected history has '+str(len(aa))+' periods; no missing target period fabricated.',))
        summary[name]=dict(periods=len(aa),outcomes=dict(Counter(r['status'] for r in rows if r['issuer']==name)))
    ledger=dict(schema='retained-reported-cfo-v1',selected_periods=len(rows),issuer_count=len(summary),summary=summary,
        outcomes=dict(Counter(r['status'] for r in rows)),limitations=list(LIMITATIONS),history_exceptions=income_ledger['history_exceptions'],
        income_outcomes=income_ledger['outcomes'],unresolved_income_reviews=[dict(issuer=r['issuer'],identity=r['identity'],fields=[f for f in r['fields'] if f['outcome'] in ('CONFLICTING_VALUES','NO_ELIGIBLE_DIRECT_CONCEPT')],
            disposition='UNRESOLVED_REVIEW_REQUIREMENT_NOT_ABANDONED_OR_ACCEPTED') for r in income_ledger['rows'] if any(f['outcome'] in ('CONFLICTING_VALUES','NO_ELIGIBLE_DIRECT_CONCEPT') for f in r['fields'])],
        artifact_exceptions=list(backlog.values()),rows=rows)
    return ledger,packages


def sweep_classification():return 'docs/universe/phase-1h5-issuer-validation.json'


def validate_history(payload):
    """Replay new CFO values/scope/nulls after unchanged structural deserialization."""
    history=h.deserialize(payload)
    pilots={}
    for name in ('MSFT','AAPL','GOOGL'):
        for a in pilot.load_history(name).annuals:pilots[(a.period.cik,a.period.accession)]=a
    for annual in history.annuals:
        key=(annual.period.cik,annual.period.accession)
        actual=next(v for v in annual.inputs if v.field is h.Field.CFO)
        if key in pilots:
            if actual!=next(v for v in pilots[key].inputs if v.field is h.Field.CFO):raise h.InputError('Reviewed pilot CFO changed')
            continue
        evidence=prepare(annual);result,error=inspect(evidence);expected,_,_=select(evidence,result,error)
        if actual!=expected:raise h.InputError('Serialized CFO value/scope/precision/provenance differs from actual retained facts')
    return history
