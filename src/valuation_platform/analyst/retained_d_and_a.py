"""Retained D&A overlays; existing financial policies only, never a new sum."""
from collections import Counter
from dataclasses import dataclass,fields,replace
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
import json
from . import historical_inputs as h, retained_components as inspect
from . import retained_capex as capex, refreshed_capex as parent
from . import retained_cfo_preparation as cfo, retained_income_preparation as missing
from ..normalization.concepts import D_AND_A_POLICY,FinancialMetric
from ..normalization.historical import _resolve_metric
from ..normalization.derived import applicable_derivation_policy,ANNUAL_DERIVATION_POLICIES,derive_annual_metric
from ..normalization.models import NormalizedHistoricalValue,DerivedHistoricalValue,AmbiguousHistoricalMetric,EvidenceSourceKind,FactEvidence
from ..normalization import d_and_a_scope as curated
from ..normalization.output import _serialize_policy,_policy_reference
from ..sec.company_facts import SECFactObservation
from ..sec.fact_selection import FilingFactObservations,SelectedFactObservation,ObservationRelationship
from ..sec.submissions import SECFiling
from ..sec.tickers import SECCompanyIdentity
from ..sec.filing_xbrl import parse_filing_xbrl_instance
from ..sec.annual_period import resolve_annual_period,ResolvedAnnualPeriod

SCHEMA='retained-d-and-a-preparation-v1'
LEDGER='docs/retained-d-and-a-ledger.json'
PROOF='retained_d_and_a_policy:'
DIRECT=D_AND_A_POLICY.candidates[0].name
LIMITS=('Approved historical policy replay is not expense-timing or integrated FCFF compatibility certification.',
        'CFO add-backs, note expenses and required D&A are distinct roles, never additional economic charges.',
        'Components and mixed impairment/accretion/lease populations do not establish completeness; no unapproved sum or absent-amortization zero.',
        'No new financial policy, adjustment, evidence refresh or valuation use.')
# Bounded exact concepts; extension names are observations, never approvals.
SUPPORT={
    DIRECT:'approved_direct_concept_observation_placement_not_reverified',
    'DepreciationAndAmortization':'combined_d_and_a_support_unapproved_except_exact_curated_entry',
    'Depreciation':'depreciation_component_expense_support',
    'AmortizationOfIntangibleAssets':'finite_lived_amortization_component_expense_support',
    'DepreciationAmortizationAndAccretionNet':'mixed_d_and_a_accretion_support',
    'DepreciationAmortizationAndImpairment':'mixed_d_and_a_impairment_support',
    'DepreciationDepletionAndAmortizationIncludingImpairments':'mixed_d_and_a_impairment_support',
    'DepreciationAmortizationAndOther':'mixed_cfo_d_and_a_other_support',
    'DepreciationAmortizationAndOtherNonCashItems':'mixed_cfo_d_and_a_other_support',
    'FinanceLeaseRightOfUseAssetAmortization':'finance_lease_amortization_separate_support',
    'FinanceLeaseDepreciationAmortizationAndInterestExpense':'mixed_finance_lease_amortization_interest_support',
    'OperatingLeaseRightOfUseAssetAmortizationExpense':'operating_lease_amortization_separate_support',
    'OperatingLeaseRightofUseAssetAmortization':'operating_lease_amortization_separate_support',
    'AdjustmentForAmortization':'amortization_adjustment_scope_unapproved',
    'AmortizationOfDeferredCharges':'deferred_cost_amortization_scope_unapproved',
    'AmortizationOfFinancingCosts':'financing_cost_amortization_not_operating_d_and_a',
    'AmortizationOfFinancingCostsAndDiscounts':'financing_cost_discount_amortization_not_operating_d_and_a',
    'AmortizationOfDebtDiscountPremium':'debt_discount_amortization_not_operating_d_and_a',
    'CapitalizedContractCostAmortization':'contract_cost_amortization_scope_unapproved',
    'AmortizationOfAcquisitionRelatedIntangibles':'acquired_intangible_amortization_component_support',
    'DepreciationAndAmortizationOfNonAcquiredIntangibles':'restricted_nonacquired_d_and_a_support',
    'OtherDepreciationAndAmortization':'other_d_and_a_scope_unapproved',
}


def select(e,concept):
    ns=e.namespaces.get('us-gaap','')
    if not ns.startswith('http://fasb.org/us-gaap/'):raise h.InputError('Approved standard D&A namespace unavailable')
    return inspect.inspect(e,inspect.SelectionSpec('d-and-a:'+concept,(inspect.Selector(ns,concept,()),),
        'annual','USD','d_and_a_exact_policy_candidate','Existing policy approval required; no component completeness inferred.',LIMITS))


def bucket(e,results):
    p=e.period;filing=SimpleNamespace(accession_number=p.accession,form=p.form,report_date=p.annual_end)
    projected=[]
    for concept,result in results:
        for value in dict.fromkeys(c.value for c in result.candidates):
            if value!=value.to_integral_value():raise h.InputError('Legacy numeric selector cannot retain exact fractional USD without float conversion')
            obs=SECFactObservation('USD',int(value),p.annual_start,p.annual_end,p.accession,None,None,p.form,None,None)
            projected.append(SelectedFactObservation('us-gaap',concept,obs,ObservationRelationship.CURRENT))
    return FilingFactObservations(filing,tuple(projected))


def compact(c,e):
    p=e.period
    return FactEvidence(EvidenceSourceKind.FILING_XBRL,e.instance.artifact.url,'us-gaap',c.concept,c.value,
        'USD',p.annual_start,p.annual_end,p.accession,p.form,None,None,None,None)


def observations(e):
    values=[];diagnostics=[]
    groups={}
    for f,i in e.facts:
        if f.concept not in SUPPORT:continue
        c=e.contexts[f.context_id]
        if c.end!=e.period.annual_end:continue
        ds=inspect.dimensions(c)
        diagnostics.append(dict(namespace=f.namespace,concept=f.concept,ordinal=i,context_id=f.context_id,
            start=None if c.start is None else str(c.start),end=str(c.end),dimensions=list(ds),
            unit_id=f.unit_ref,raw_value=f.raw_value,precision=f.decimals,nil=f.is_nil,
            role=SUPPORT[f.concept],source_url=f.source_url,source_sha256=e.instance.artifact.sha256,
            eligibility='ANNUAL_SUPPORT_ONLY' if c.start==e.period.annual_start else 'NONANNUAL_OR_BALANCE_DIAGNOSTIC_ONLY'))
        if c.start==e.period.annual_start:groups.setdefault((f.namespace,f.concept,ds),None)
    errors=[]
    for ns,concept,ds in groups:
        role=SUPPORT[concept]+('_issuer_extension_unapproved' if not ns.startswith('http://fasb.org/us-gaap/') else '')
        try:
            result=inspect.inspect(e,inspect.SelectionSpec('d-and-a-support:'+concept,(inspect.Selector(ns,concept,ds),),
                'annual','USD',role,'Reported population only; statement placement and completeness not inferred.',LIMITS))
            for c in result.candidates:
                values.append(h.InputValue('retained-da:observation:'+concept+':'+str(c.occurrences[0].ordinal),h.Field.DA,e.period,None,
                    c.value,'USD',1,1,c.precision,role,h.Origin.REPORTED,h.Quality.LIMITED,role,h.Scope.RESTRICTED,
                    h.Completeness.PARTIAL,h.Review.REVIEWED,c.evidence_references,None,None,(),
                    'Exact raw support population, not an additional required D&A or authorized component sum.',
                    ('support_only','no_sum','placement_not_independently_reverified')+(('dimensioned_support',) if ds else ()),LIMITS,None,(concept,)))
        except h.InputError as exc:errors.append(concept+': '+str(exc))
    return tuple(values),diagnostics,errors


def artifact_store():
    # Documented retained collections already have representation/hash validation.
    # No use of LLY Capex refresh authorization to approve Visa D&A reports.
    return capex.artifacts()


def resolve(e,store):
    direct=select(e,DIRECT)
    result=_resolve_metric(bucket(e,[(DIRECT,direct)]),D_AND_A_POLICY,e.instance.artifact.url,None)
    if isinstance(result,NormalizedHistoricalValue):
        refs=tuple(compact(c,e) for c in direct.candidates)
        result=replace(result,chosen_source=refs[0],confirming_sources=refs[1:])
    proof=dict(policy_id='D_AND_A_POLICY',version=None,version_status='existing_unversioned_direct_policy',
        concept=DIRECT,resolver='normalization.historical._resolve_metric',
        numeric_projection='Exact integer signatures only; no Company Facts receipt or evidence emitted.',
        source_kind='filing_xbrl',timing_readiness='NOT_ASSESSED')
    operands=();gaps=[];inspection_result=direct
    entry=next((x for x in curated.D_AND_A_SCOPE_EQUIVALENCE_POLICY.entries if
        (x.company_cik,x.accession_number,x.annual_start,x.annual_end)==(e.period.cik,e.period.accession,e.period.annual_start,e.period.annual_end)),None)
    if isinstance(result,AmbiguousHistoricalMetric):return result,inspection_result,proof,operands,gaps
    if entry:
        gaps=[dict(url=u,sha256=d,representation='sec_response_body_bytes',digest_type='sha256_sec_response_body_bytes',
            reason='Exact registered original D&A artifact not retained; no automatic refresh.',
            alternatives=[ref for (url,digest),(raw,ref) in store.items() if url==u and digest!=d])
            for u,d in entry.artifact_digests if (u,d) not in store and (u,d)!=(e.instance.artifact.url,e.instance.artifact.sha256)]
        if e.instance.artifact.sha256!=entry.instance_digest:
            gaps.append(dict(url=entry.instance_url,sha256=entry.instance_digest,reason='Retained instance differs from registered original D&A body.'))
        proof.update(registered_policy_id=curated.D_AND_A_SCOPE_POLICY_ID,registered_version='1')
        if not gaps:
            filing=SECFiling(entry.accession_number,entry.form,entry.filed,entry.report_date,entry.primary_document)
            stamp=datetime.fromisoformat(e.instance.retrieved_at_utc)
            company=SECCompanyIdentity('RETAINED',e.period.cik,f'{e.period.cik:010d}','Exact retained issuer',e.instance.artifact.url,stamp)
            x=parse_filing_xbrl_instance(e.instance.artifact.body,company=company,filing=filing,source_url=entry.instance_url,retrieved_at=stamp)
            period=resolve_annual_period(x)
            if not isinstance(period,ResolvedAnnualPeriod) or (period.start,period.end)!=(e.period.annual_start,e.period.annual_end):raise h.InputError('D&A annual identity mismatch')
            bodies={u:e.instance.artifact.body if u==entry.instance_url else store[u,d][0] for u,d in entry.artifact_digests}
            attested=curated.verify_d_and_a_artifacts(entry,bodies,x)
            result=curated.apply_curated_d_and_a_scope_policy(FilingFactObservations(filing,()),result,e.period.cik,period,x,attested)
            if isinstance(result,NormalizedHistoricalValue) and result.policy_provenance:
                curated.validate_d_and_a_scope_provenance(result.policy_provenance)
                proof=dict(_serialize_policy(_policy_reference(result.policy_provenance,filing)),artifact_bindings=[
                    store[u,d][1] if u!=entry.instance_url else dict(url=u,sha256=d,source='unchanged_verified_instance_receipt') for u,d in entry.artifact_digests])
                inspection_result=select(e,entry.concept)
    derivation=applicable_derivation_policy(FinancialMetric.D_AND_A,e.period.cik,ANNUAL_DERIVATION_POLICIES)
    from ..normalization.models import MissingHistoricalMetric
    if isinstance(result,MissingHistoricalMetric) and derivation is not None:
        inspected=[(c.name,select(e,c.name)) for c in derivation.operands]
        result=derive_annual_metric(bucket(e,inspected),derivation,e.instance.artifact.url)
        proof=dict(policy_id=derivation.policy_id,version='1',version_basis='Existing policy ID ends in _v1',operation='ADD',
            operands=[c.name for c in derivation.operands],applicable_ciks=sorted(derivation.applicable_ciks),
            resolver='normalization.derived.derive_annual_metric',source_kind='filing_xbrl',timing_readiness='NOT_ASSESSED',
            numeric_projection='Exact signatures into unchanged arithmetic resolver; source evidence rebound to actual filing facts.')
        if isinstance(result,DerivedHistoricalValue):
            chosen=[]
            for name,found in inspected:
                c=found.candidates[0]
                chosen.append(h.InputValue('retained-da:operand:'+name,h.Field.DA,e.period,None,c.value,'USD',1,1,c.precision,
                    'existing_msft_policy_operand_not_generic_sum',h.Origin.REPORTED,h.Quality.SUPPORTED,name,h.Scope.RESTRICTED,
                    h.Completeness.PARTIAL,h.Review.REVIEWED,c.evidence_references,None,None,
                    tuple(h.InputValue('retained-da:operand-alternative:'+name+':'+str(v.occurrences[0].ordinal),h.Field.DA,e.period,None,v.value,
                        'USD',1,1,v.precision,'support_only_operand_representation',h.Origin.REPORTED,h.Quality.LIMITED,name,h.Scope.RESTRICTED,
                        h.Completeness.PARTIAL,h.Review.REVIEWED,v.evidence_references,None,None,(),'Equivalent original representation retained.',
                        ('support_only',),LIMITS,None,(name,)) for v in found.candidates[1:]),
                    'Only the existing Microsoft derivation policy authorizes this operand.',('not_generic_component_approval',),LIMITS,None,(name,)))
            operands=tuple(chosen)
            result=replace(result,operands=tuple(compact(found.candidates[0],e) for _,found in inspected))
    return result,inspection_result,proof,operands,gaps


@dataclass(frozen=True)
class AnnualDAndA:
    period: h.Period
    required_value: h.InputValue
    support_only: tuple[h.InputValue,...]
    operands: tuple[h.InputValue,...]
    receipt: h.Receipt | None
    policy_json: str
    diagnostics_json: str

    def __post_init__(self):
        if type(self.period) is not h.Period or (self.receipt is not None and
                (type(self.receipt) is not h.Receipt or self.receipt.artifact.accession!=self.period.accession)):
            raise h.InputError('Exact annual D&A overlay and retained instance receipt required')
        if self.receipt is None and (self.required_value.value is not None or self.support_only or self.operands):
            raise h.InputError('Missing D&A body cannot support a value or observations')
        h._typed(self.support_only,h.InputValue);h._typed(self.operands,h.InputValue)
        for v in (self.required_value,*self.support_only,*self.operands):
            if type(v) is not h.InputValue or v.field is not h.Field.DA or v.period!=self.period:raise h.InputError('D&A field/period mismatch')
        if any('support_only' not in v.flags for v in self.support_only):raise h.InputError('Observations cannot silently become required D&A')
        json.loads(self.policy_json);json.loads(self.diagnostics_json)


def package(e,store):
    if e.instance is None:
        value=missing.unavailable(e.period,h.Field.DA,'Missing exact retained instance/receipt; no value inferred.',h.Review.REVIEWED)
        return AnnualDAndA(e.period,value,(),(),None,'{}','[]'),dict(status='EVIDENCE_GAP',value_usd=None,policy={},
            support_observations=0,support_available=False,support_complete=False,approved_entry_evidence_gaps=[],
            evidence_errors=['Missing exact retained instance/receipt.'],diagnostics=[])
    support,diagnostics,errors=observations(e);operands=();gaps=[];proof={};status='UNAPPROVED_SCOPE_COMPLETENESS'
    try:
        resolved,selected,proof,operands,gaps=resolve(e,store)
        if isinstance(resolved,NormalizedHistoricalValue):
            candidates=tuple(h.InputValue('retained-da:candidate:'+c.concept+':'+str(c.occurrences[0].ordinal),h.Field.DA,e.period,None,c.value,
                'USD',1,1,c.precision,'support_only_policy_candidate',h.Origin.REPORTED,h.Quality.LIMITED,c.concept,h.Scope.RESTRICTED,
                h.Completeness.PARTIAL,h.Review.REVIEWED,c.evidence_references,None,None,(),'Original eligible representation retained.',
                ('support_only',),LIMITS,None,(c.concept,)) for c in selected.candidates)
            chosen=next(v for v in candidates if v.value==Decimal(str(resolved.value)))
            status='CURATED' if resolved.policy_provenance else 'DIRECT'
            value=replace(chosen,input_id='retained-da:required:'+e.period.accession,role='approved_historical_policy_d_and_a',
                quality=h.Quality.SUPPORTED,alternatives=tuple(v for v in candidates if v is not chosen),
                scope='Existing approved D&A policy; consumer timing/scope remains unassessed.',
                flags=(PROOF+parent.canonical(proof),'not_additional_cfo_addback'),
                selection_rationale='Unchanged approved resolver replay with actual retained filing evidence.')
        elif isinstance(resolved,DerivedHistoricalValue):
            status='DERIVED_APPROVED'
            formula=h.Formula(resolved.policy_id,1,h.FormulaKind.COMPONENT_TOTAL,'Depreciation + AmortizationOfIntangibleAssets',
                tuple(v.input_id for v in operands),False,True,True,tuple(s.source_id for v in operands for s in v.sources))
            value=h.InputValue('retained-da:required:'+e.period.accession,h.Field.DA,e.period,None,Decimal(str(resolved.value)),
                'USD',1,1,'derived_from_original_operand_precision','existing_approved_msft_d_and_a_derivation',h.Origin.DERIVED,
                h.Quality.SUPPORTED,'Existing MSFT two-operand policy only; no new sum or timing certification.',h.Scope.RESTRICTED,
                h.Completeness.PARTIAL,h.Review.REVIEWED,tuple(s for v in operands for s in v.sources),None,formula,(),
                'Unchanged approved MSFT arithmetic resolver; original operands and their precision retained.',
                (PROOF+parent.canonical(proof),'not_additional_cfo_addback'),LIMITS,None,('existing_msft_d_and_a',))
        else:
            status='CONFLICTING' if isinstance(resolved,AmbiguousHistoricalMetric) else 'EVIDENCE_GAP' if gaps else 'UNAPPROVED_SCOPE_COMPLETENESS'
            value=missing.unavailable(e.period,h.Field.DA,'No approved D&A replay: '+status+'; absence of amortization is not zero.',h.Review.REVIEWED)
            if status=='CONFLICTING':value=replace(value,quality=h.Quality.CONFLICTING)
    except (ValueError,KeyError) as exc:
        status='EVIDENCE_GAP';value=missing.unavailable(e.period,h.Field.DA,'D&A source/policy replay failed: '+str(exc),h.Review.REVIEWED)
        errors.append(str(exc))
    overlay=AnnualDAndA(e.period,value,support,operands,e.instance,parent.canonical(proof),parent.canonical(diagnostics))
    return overlay,dict(status=status,value_usd=None if value.value is None else str(value.value),policy=proof,
        support_observations=len(support),support_available=bool(support),support_complete=False,
        approved_entry_evidence_gaps=gaps,evidence_errors=errors,diagnostics=diagnostics)


def build():
    previous,histories=parent.build();store=artifact_store();rows=[];overlays={}
    for name,wrapped in histories.items():
        history=wrapped.bundle if type(wrapped) is parent.RefreshedHistory else wrapped;aa=[]
        for annual in history.annuals:
            overlay,row=package(cfo.prepare(annual),store);aa.append(overlay)
            rows.append(dict(row,issuer=name,identity=dict(cik=annual.period.cik,accession=annual.period.accession,
                form=annual.period.form,annual_start=str(annual.period.annual_start),annual_end=str(annual.period.annual_end)),
                pilot_original_unmodified=name in ('MSFT','AAPL','GOOGL')))
        overlays[name]=tuple(aa)
    blockers={}
    for row in rows:
        for gap in row['approved_entry_evidence_gaps']:
            key=(gap['url'],gap['sha256']);blockers.setdefault(key,dict(gap,affected=[]))['affected'].append(row['identity'])
    ledger=dict(schema=SCHEMA,selected_periods=len(rows),issuer_count=len(histories),outcomes=dict(Counter(r['status'] for r in rows)),
        support_periods=sum(r['support_available'] for r in rows),support_observations=sum(r['support_observations'] for r in rows),
        summary={name:dict(periods=len(v),outcomes=dict(Counter(r['status'] for r in rows if r['issuer']==name)),
            support_periods=sum(r['support_available'] for r in rows if r['issuer']==name)) for name,v in overlays.items()},
        evidence_backlog=list(blockers.values()),history_exceptions=previous['history_exceptions'],rows=rows,limitations=list(LIMITS),
        delivery='Separate annual D&A overlays; no original pilot or parent-history input replaced.')
    return ledger,histories,overlays


def serialize(overlay):
    if type(overlay) is not AnnualDAndA:raise h.InputError('D&A annual overlay required')
    validate_overlay(overlay)
    bodies={};entry={f.name:parent._encode(getattr(overlay,f.name),bodies) for f in fields(overlay)}
    return parent.canonical(dict(schema=SCHEMA,entry=entry,original_bodies=bodies))


def deserialize(payload):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise h.InputError('Duplicate D&A serialized key')
            d[k]=v
        return d
    try:
        doc=json.loads(payload,object_pairs_hook=unique)
        if type(doc) is not dict or set(doc)!={'schema','entry','original_bodies'} or doc['schema']!=SCHEMA:
            raise h.InputError('Exact D&A overlay schema required')
        if set(doc['entry'])!={f.name for f in fields(AnnualDAndA)}:raise h.InputError('Closed D&A fields required')
        bodies={};used=set()
        for digest,encoded in doc['original_bodies'].items():
            raw=h._decode(encoded)
            if type(raw) is not bytes or parent.review.sha(raw)!=digest:raise h.InputError('Changed D&A body transport')
            bodies[digest]=raw
        result=AnnualDAndA(**{k:parent._decode(v,bodies,used) for k,v in doc['entry'].items()})
        if used!=set(bodies):raise h.InputError('Unused D&A body transport')
        if result.receipt is None:
            if result.required_value.value is not None:raise h.InputError('Missing-source D&A cannot resolve')
            return result
        return validate_overlay(result)
    except (ValueError,KeyError,TypeError) as exc:raise h.InputError('Invalid D&A preparation payload') from exc


def validate_overlay(result):
    if type(result) is not AnnualDAndA:raise h.InputError('Typed D&A overlay required')
    if result.receipt is None:
        if result.required_value.value is not None or result.support_only or result.operands:
            raise h.InputError('Missing-source D&A cannot resolve')
        return result
    evidence=inspect.prepare(result.period,(result.receipt,),
        (inspect.ArtifactBinding(result.receipt.artifact.url,result.receipt.artifact.sha256,'instance'),))
    expected,_=package(evidence,artifact_store())
    if result!=expected:raise h.InputError('D&A policy/source/value differs from independent replay')
    return result
