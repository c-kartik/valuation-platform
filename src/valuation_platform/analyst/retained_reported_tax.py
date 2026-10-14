"""Separate reported tax context replay, not cash tax or an operating-tax rate.

The USD-only historical InputValue contract is deliberately unchanged. ETR is a
separate pure-unit policy result, with both monetary operands attached, rather
than a falsely USD-labelled input or a new generic formula engine.
"""
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal
import json
from . import historical_inputs as h, retained_components as r
from . import retained_d_and_a as da, retained_cfo_preparation as cfo
from . import retained_income_preparation as missing
from . import approved_income_integration as metadata
from ..normalization.concepts import INCOME_TAX_EXPENSE_POLICY, PRETAX_INCOME_POLICY
from ..normalization.historical import _resolve_metric
from ..normalization.derived import derive_reported_effective_tax_rate
from ..normalization import pretax_scope as curated
from ..normalization.models import NormalizedHistoricalValue, DerivedHistoricalValue, AmbiguousHistoricalMetric
from ..normalization.output import _serialize_policy, _policy_reference
from ..sec.submissions import SECFiling
from ..sec.tickers import SECCompanyIdentity
from ..sec.filing_xbrl import parse_filing_xbrl_instance
from ..sec.annual_period import resolve_annual_period, ResolvedAnnualPeriod

SCHEMA='retained-reported-tax-context-v1'
LEDGER='docs/retained-reported-tax-context-ledger.json'
LIMITS=('Reported provision, pretax income and accounting ETR are not cash taxes, deferred-tax reconciliation, operating tax or a future rate.',
        'Existing exact policies only; no clamp, loss monetization, scope fallback or consumer readiness approval.',
        'Fact/policy replay does not independently re-review every statement or certify integrated financial sufficiency.')


def inspect(e, concept):
    ns=e.namespaces.get('us-gaap','')
    if not ns.startswith('http://fasb.org/us-gaap/'): raise h.InputError('Standard tax namespace unavailable')
    return r.inspect(e,r.SelectionSpec('tax:'+concept,(r.Selector(ns,concept,()),),'annual','USD',
        'reported_tax_policy_operand','Exact continuing-operations policy population; not operating-tax allocation.',LIMITS))


def filing_metadata(e):
    """Only existing reviewed metadata; never manufacture a filed date."""
    p=e.period
    found=[m['filing'] for m in metadata.bindings(True)['filings'] if m['filing']['accession_number']==p.accession]
    if found:
        m=found[0]
        if m['form']!=p.form or m['report_date']!=str(p.annual_end):raise h.InputError('Tax filing metadata mismatch')
        return SECFiling(p.accession,p.form,date.fromisoformat(m['filing_date']),p.annual_end,m['primary_document']), 'existing_submission_bound_income_metadata'
    # Original exact-accession Capex registrations retain reviewed filing metadata.
    from ..normalization.capex_scope import CAPEX_SCOPE_V2_POLICY
    found=[x for x in CAPEX_SCOPE_V2_POLICY.entries if
        (x.company_cik,x.accession_number,x.annual_start,x.annual_end)==(p.cik,p.accession,p.annual_start,p.annual_end)]
    if found:
        x=found[0]
        return SECFiling(x.accession_number,x.form,x.filed,x.report_date,x.primary_document), 'unchanged_exact_capex_registration_filing_metadata'
    return None,None


def replay(e):
    inspected=[(p.candidates[0].name,inspect(e,p.candidates[0].name)) for p in (INCOME_TAX_EXPENSE_POLICY,PRETAX_INCOME_POLICY)]
    bucket=da.bucket(e,inspected)
    tax=_resolve_metric(bucket,INCOME_TAX_EXPENSE_POLICY,e.instance.artifact.url,None)
    pretax=_resolve_metric(bucket,PRETAX_INCOME_POLICY,e.instance.artifact.url,None)
    proof=dict(direct_policies=[p.metric.value for p in (INCOME_TAX_EXPENSE_POLICY,PRETAX_INCOME_POLICY)],
        direct_version='existing_unversioned_policy',numeric_projection='Exact integer semantic signatures; real filing occurrences retained, no Company Facts provenance invented.')
    entry=next((x for x in curated.PRETAX_SCOPE_EQUIVALENCE_POLICY.entries if
        (x.company_cik,x.accession_number,x.annual_start,x.annual_end)==(e.period.cik,e.period.accession,e.period.annual_start,e.period.annual_end)),None)
    gaps=[]
    if entry:
        proof['registered_pretax_entry']=dict(policy_id=curated.PRETAX_SCOPE_POLICY_ID,
            version=curated.PRETAX_SCOPE_POLICY_VERSION,cik=entry.company_cik,accession=entry.accession_number,
            annual_start=str(entry.annual_start),annual_end=str(entry.annual_end),concept=entry.concept,
            expected_value_usd=str(entry.expected_value),scope=entry.economic_scope.value,
            reviewed_evidence=[dict(evidence_id=v.evidence_id,source_url=v.source_url,filing_location=v.filing_location,
                research_artifact=v.research_artifact,reviewed_on=str(v.reviewed_on),review_status=v.review_status,
                rationale=v.rationale,content_digest=v.content_digest) for v in entry.reviewed_evidence])
        candidate=inspect(e,entry.concept); inspected.append((entry.concept,candidate))
        filing,basis=filing_metadata(e)
        if filing is None:
            gaps.append('Registered Pretax entry cannot replay: exact retained filing date/primary-document metadata binding unavailable; no metadata invented.')
        else:
            stamp=datetime.fromisoformat(e.instance.retrieved_at_utc)
            company=SECCompanyIdentity('RETAINED',e.period.cik,f'{e.period.cik:010d}','Retained registrant',e.instance.artifact.url,stamp)
            x=parse_filing_xbrl_instance(e.instance.artifact.body,company=company,filing=filing,source_url=e.instance.artifact.url,retrieved_at=stamp)
            annual=resolve_annual_period(x)
            if not isinstance(annual,ResolvedAnnualPeriod) or (annual.start,annual.end)!=(e.period.annual_start,e.period.annual_end):raise h.InputError('Tax annual DEI mismatch')
            for review in entry.reviewed_evidence:
                if review.review_status!='approved' or not (metadata.shared.ROOT/review.research_artifact).is_file():raise h.InputError('Original Pretax review reference unavailable')
                expected=f'/{filing.accession_number.replace("-","")}/{filing.primary_document}'
                if not review.source_url.endswith(expected):raise h.InputError('Original Pretax primary identity mismatch')
            pretax=curated.apply_curated_pretax_scope_policy(da.bucket(e,inspected),pretax,e.period.cik,e.instance.artifact.url,annual,x)
            proof['curated_metadata_basis']=basis
            if isinstance(pretax,NormalizedHistoricalValue) and pretax.policy_provenance:
                proof['curated_pretax']=_serialize_policy(_policy_reference(pretax.policy_provenance,filing))
    # Rebind compact legacy operands to actual retained XBRL sources; every
    # confirming occurrence remains in the InputValues below.
    rebound=[]
    for result in (tax,pretax):
        if isinstance(result,NormalizedHistoricalValue):
            matching=[c for name,found in inspected for c in found.candidates if c.concept==result.chosen_source.concept and c.value==Decimal(str(result.value))]
            refs=tuple(da.compact(c,e) for c in matching)
            if not refs:raise h.InputError('Resolved tax operand lacks retained candidate')
            result=replace(result,chosen_source=refs[0],confirming_sources=refs[1:])
        rebound.append(result)
    etr=derive_reported_effective_tax_rate(e.period.accession,e.period.annual_end,tuple(rebound))
    return tuple(rebound),etr,inspected,proof,gaps


def value(e,result,inspected,role,proof):
    candidates=[]
    for name,found in inspected:
        for c in found.candidates:
            candidates.append(h.InputValue('reported-tax:'+role+':'+name+':'+str(c.occurrences[0].ordinal),h.Field.TAX,e.period,None,
                c.value,'USD',1,1,c.precision,role,h.Origin.REPORTED,h.Quality.LIMITED,role,h.Scope.RESTRICTED,
                h.Completeness.PARTIAL,h.Review.REVIEWED,c.evidence_references,None,None,(),
                'Existing policy scope only; no tax allocation or assumption.',('separate_reported_tax_context',),LIMITS,None,(role,)))
    if isinstance(result,NormalizedHistoricalValue):
        matches=[c for c in candidates if c.sources[0].concept==result.chosen_source.concept and c.value==Decimal(str(result.value))]
        selected=matches[0]
        return replace(selected,input_id='reported-tax:required:'+role,quality=h.Quality.SUPPORTED,
            alternatives=tuple(c for c in candidates if c is not selected),flags=selected.flags+('existing_policy_proof:'+da.parent.canonical(proof),))
    reason=result.reason.value
    v=missing.unavailable(e.period,h.Field.TAX,role+': '+reason,h.Review.REVIEWED)
    return replace(v,input_id='reported-tax:required:'+role,role=role,alternatives=tuple(candidates),
        quality=h.Quality.CONFLICTING if isinstance(result,AmbiguousHistoricalMetric) else h.Quality.LIMITED,
        unresolved_requirements=v.unresolved_requirements+LIMITS)


@dataclass(frozen=True)
class AnnualTaxContext:
    period: h.Period
    provision: h.InputValue
    pretax: h.InputValue
    receipt: h.Receipt
    etr_json: str
    proof_json: str

    def __post_init__(self):
        if type(self.period) is not h.Period or type(self.receipt) is not h.Receipt:
            raise h.InputError('Exact annual tax period/receipt required')
        if self.receipt.artifact.accession!=self.period.accession:raise h.InputError('Tax receipt accession mismatch')
        for v in (self.provision,self.pretax):
            if type(v) is not h.InputValue or v.field is not h.Field.TAX or v.period!=self.period or v.unit!='USD':
                raise h.InputError('Exact monetary tax operand binding required')
            if any(s.receipt!=self.receipt for s in v.sources):raise h.InputError('Tax source receipt differs')
        ratio=json.loads(self.etr_json);json.loads(self.proof_json)
        if (ratio.get('policy_id')!='annual_reported_effective_tax_rate_v1' or ratio.get('version')!='1'
                or ratio.get('unit')!='pure' or ratio.get('operation')!='DIVIDE'
                or ratio.get('operand_ids')!=[self.provision.input_id,self.pretax.input_id]):
            raise h.InputError('Existing ETR policy and exact operand identities required')
        if ratio.get('value') is not None and (ratio.get('origin')!='derived' or not Decimal(ratio['value']).is_finite()):
            raise h.InputError('Finite policy-derived ETR required')


def package(e):
    if e.instance is None or e.unresolved_requirements:raise h.InputError('Verified complete retained instance binding required')
    results,etr,inspected,proof,gaps=replay(e)
    provision=value(e,results[0],inspected[:1],'reported_income_tax_expense_benefit',proof)
    pretax=value(e,results[1],inspected[1:],'reported_continuing_pretax_income',proof)
    if gaps and pretax.value is None:
        pretax=replace(pretax,null_reason=pretax.null_reason+'; '+'; '.join(gaps),
            unresolved_requirements=pretax.unresolved_requirements+tuple(gaps))
    ratio=dict(policy_id='annual_reported_effective_tax_rate_v1',version='1',operation='DIVIDE',unit='pure',
        value=None,origin='unavailable',reason=None,diagnostics=[],operand_ids=[provision.input_id,pretax.input_id],
        operand_precision=[provision.precision,pretax.precision],precision='Decimal division, 34 significant digits; underlying reported precision unchanged',
        limitations=list(LIMITS),curated_operand_provenance=proof.get('curated_pretax'))
    if isinstance(etr,DerivedHistoricalValue):ratio.update(value=str(etr.value),origin='derived',diagnostics=[d.value for d in etr.diagnostics])
    else:ratio['reason']=etr.reason.value
    result=AnnualTaxContext(e.period,provision,pretax,e.instance,da.parent.canonical(ratio),da.parent.canonical(dict(proof,evidence_gaps=gaps)))
    def payload(v):
        return dict(input_id=v.input_id,value=None if v.value is None else str(v.value),role=v.role,origin=v.origin.value,
            unit=v.unit,scale=v.scale,sign=v.sign,precision=v.precision,scope=v.scope,completeness=v.completeness.value,
            sources=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                digest_type=s.receipt.artifact.digest_type,representation=s.receipt.artifact.representation,
                retrieved_at_utc=s.receipt.retrieved_at_utc,http_status=s.receipt.http_status,
                namespace=s.namespace,concept=s.concept,context_id=s.context_id,ordinal=s.occurrence_ordinal,
                locator=s.locator,unit=s.unit,raw_value=s.raw_value,precision=s.decimals,dimensions=list(s.dimensions),
                start=str(s.start),end=str(s.end)) for s in v.sources],alternatives=[payload(a) for a in v.alternatives])
    row=dict(identity=dict(cik=e.period.cik,accession=e.period.accession,form=e.period.form,annual_start=str(e.period.annual_start),annual_end=str(e.period.annual_end)),
        fields={role:dict(status='POPULATED' if v.value is not None else 'CONFLICTING' if v.quality is h.Quality.CONFLICTING else 'UNAVAILABLE',
            value=None if v.value is None else str(v.value),precision=v.precision,source_count=len(v.sources),
            alternatives=len(v.alternatives),reason=v.null_reason,observation=payload(v)) for role,v in [('provision',provision),('pretax',pretax)]},
        etr=ratio,proof=json.loads(result.proof_json))
    return result,row


def validate(v):
    if type(v) is not AnnualTaxContext:raise h.InputError('Typed reported-tax overlay required')
    e=r.prepare(v.period,(v.receipt,),(r.ArtifactBinding(v.receipt.artifact.url,v.receipt.artifact.sha256,'instance'),))
    if v!=package(e)[0]:raise h.InputError('Tax context differs from exact policy/evidence replay')
    return v


def serialize(v):
    validate(v);bodies={}
    from dataclasses import fields
    return da.parent.canonical(dict(schema=SCHEMA,entry={f.name:da.parent._encode(getattr(v,f.name),bodies) for f in fields(v)},original_bodies=bodies))


def deserialize(payload):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise h.InputError('Duplicate tax key')
            d[k]=v
        return d
    doc=json.loads(payload,object_pairs_hook=unique)
    from dataclasses import fields
    if set(doc)!= {'schema','entry','original_bodies'} or doc['schema']!=SCHEMA or set(doc['entry'])!={f.name for f in fields(AnnualTaxContext)}:raise h.InputError('Closed tax envelope required')
    bodies={k:h._decode(v) for k,v in doc['original_bodies'].items()};used=set()
    if any(type(v) is not bytes or da.parent.review.sha(v)!=k for k,v in bodies.items()):raise h.InputError('Tampered tax body')
    result=AnnualTaxContext(**{k:da.parent._decode(v,bodies,used) for k,v in doc['entry'].items()})
    if used!=set(bodies):raise h.InputError('Unused tax bodies')
    return validate(result)


def build(histories):
    rows=[];overlays={}
    for ticker,history in histories.items():
        annuals=history.bundle.annuals if hasattr(history,'bundle') else history.annuals
        overlays[ticker]=[]
        for a in annuals:
            result,row=package(cfo.prepare(a));row['issuer']=ticker;rows.append(row);overlays[ticker].append(result)
        overlays[ticker]=tuple(overlays[ticker])
    summary={key:dict(Counter(row['fields'][key]['status'] for row in rows)) for key in ('provision','pretax')}
    summary['etr']=dict(Counter('POPULATED' if row['etr']['value'] is not None else 'CONFLICTING' if row['etr']['reason']=='incompatible_derivation_operands' else 'UNAVAILABLE' for row in rows))
    if len(rows)!=199 or len({r['identity']['accession'] for r in rows})!=199 or len(overlays)!=42:raise h.InputError('Exact 199-period/42-issuer tax accounting required')
    return dict(schema=SCHEMA,selected_periods=199,issuers=42,summary=summary,rows=rows,limitations=list(LIMITS),
        delivery='Separate pure-unit ETR overlay; unchanged USD-only InputValue, pilots and frozen schemas. No complete tax-consumer contract.'),overlays
