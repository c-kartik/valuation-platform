"""Bounded bridge-claim and DEI share observations; no equity calculation."""
from collections import Counter
from dataclasses import dataclass,fields,replace,asdict
import json
from . import historical_inputs as h,retained_components as r,retained_bridge_components as bridge
from . import retained_cfo_preparation as cfo,retained_income_preparation as missing

SCHEMA='retained-claims-shares-inspection-v1'
LEDGER='docs/retained-claims-shares-ledger.json'
FIELDS=(h.Field.OTHER_BRIDGE,h.Field.SHARES)
LIMITS=('Component/class observations are not complete issuer claims, assets or shares; absence is not zero.',
        'No netting, valuation adjustment, class sum/equivalence or dilution estimate.',
        'Accounting bases, dates, dimensions and possible investment overlap require review.',
        'No new financial approval; original pilots, fields, policies and frozen outputs remain unchanged.')
# Closed elements, not a pension/deferred-tax/claim name search. Broader totals
# are separate support populations, not substitutes for net pension or NOL DTA.
RULES=(
 bridge.Rule(FIELDS[0],'PreferredStockValue','preferred_carrying','Preferred-stock carrying caption; redemption/liquidation/fair value not inferred.','preferred'),
 bridge.Rule(FIELDS[0],'PreferredStockRedemptionValue','preferred_redemption','Preferred redemption value, not carrying or fair value.','preferred_redemption',('preferred',)),
 bridge.Rule(FIELDS[0],'PreferredStockLiquidationPreferenceValue','preferred_liquidation','Preferred liquidation preference, not carrying value.','preferred_liquidation',('preferred',)),
 bridge.Rule(FIELDS[0],'RedeemableNoncontrollingInterestEquityCarryingAmount','redeemable_nci_carrying','Redeemable NCI carrying amount; not equity NCI equivalence.','redeemable_nci',('nci',)),
 bridge.Rule(FIELDS[0],'MinorityInterest','noncontrolling_equity','Noncontrolling equity interest caption; not a market-value claim.','nci',('redeemable_nci',)),
 bridge.Rule(FIELDS[0],'NoncontrollingInterestInConsolidatedEntity','noncontrolling_equity_other_caption','Noncontrolling interest in consolidated entities; possible overlap with minority-interest caption.','nci_other',('nci','redeemable_nci')),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanFundedStatusOfPlan','pension_net_funded_status','Reported net funded status; preserve raw sign, not an independently constructed net liability.','pension_net',('pension_assets','pension_obligation','pension_recognized_asset','pension_recognized_liability')),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanAssetsForPlanBenefits','pension_plan_assets','Gross pension-plan asset population, not an issuer cash asset.','pension_assets',('pension_net',)),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent','pension_noncurrent_plan_asset','Noncurrent pension asset population, not cash or a net-liability deduction.','pension_noncurrent_asset',('pension_assets','pension_recognized_asset')),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanFairValueOfPlanAssets','pension_plan_assets_fair_value','Reported fair value of pension-plan assets, not carrying cash or net funded status.','pension_assets_fair',('pension_assets','pension_net','pension_assets_fair_gross')),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanFairValueOfPlanAssetsGross','pension_gross_plan_assets_fair_value','Gross fair value of pension-plan assets; relationship to other asset captions requires review.','pension_assets_fair_gross',('pension_assets_fair','pension_assets','pension_net')),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanBenefitObligation','pension_benefit_obligation','Gross benefit obligation; not a net funded-status claim.','pension_obligation',('pension_net',)),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanProjectedBenefitObligation','pension_projected_obligation','Projected benefit obligation, separate from other obligation bases.','pension_pbo',('pension_obligation','pension_net')),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanAccumulatedBenefitObligation','pension_accumulated_obligation','Accumulated benefit obligation, not projected obligation equivalence.','pension_abo',('pension_pbo','pension_obligation')),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanAmountsRecognizedInBalanceSheetAsset','pension_recognized_asset','Recognized pension asset caption; gross/net/plan coverage requires review.','pension_recognized_asset',('pension_net',)),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanAmountsRecognizedInBalanceSheetLiability','pension_recognized_liability','Recognized pension liability caption; no netting against pension assets.','pension_recognized_liability',('pension_net',)),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanAmountsRecognizedInBalanceSheetLiabilityCurrent','pension_current_liability','Current recognized pension liability.','pension_current',('pension_recognized_liability',)),
 bridge.Rule(FIELDS[0],'DefinedBenefitPlanAmountsRecognizedInBalanceSheetLiabilityNoncurrent','pension_noncurrent_liability','Noncurrent recognized pension liability.','pension_noncurrent',('pension_recognized_liability',)),
 bridge.Rule(FIELDS[0],'EquityMethodInvestments','equity_method_carrying','Equity-method investment carrying population, not fair value; already inspected in cash/investment family.','equity_method',('cash_investment_components:equity_method','long_term_investments')),
 bridge.Rule(FIELDS[0],'LongTermInvestments','long_term_investment_mixed','Mixed long-term investments, not a new independent asset.','long_term_investments',('cash_investment_components:long_term_investments','equity_method','other_long_term')),
 bridge.Rule(FIELDS[0],'OtherLongTermInvestments','other_long_term_investment','Other long-term investments; composition unreviewed.','other_long_term',('cash_investment_components:other_long_term','long_term_investments')),
 bridge.Rule(FIELDS[0],'EquityMethodInvestmentsSummarizedFinancialInformationFairValue','equity_method_fair_value_support','Fair value support for equity-method investments, not carrying amount or an additional asset.','equity_method_fair',('equity_method',)),
 bridge.Rule(FIELDS[0],'DeferredTaxAssetsOperatingLossCarryforwards','nol_deferred_tax_asset','Reported operating-loss-carryforward DTA; gross/net, jurisdiction and usability require review.','nol_dta',('dta_total','carryforward_dta')),
 bridge.Rule(FIELDS[0],'DeferredTaxAssetsTaxDeferredExpenseCompensationAndBenefitsShareBasedCompensationCost','sbc_dta_not_nol','SBC-related DTA, not an operating-loss-carryforward asset.','sbc_dta',('dta_total',)),
 bridge.Rule(FIELDS[0],'DeferredTaxAssetsTaxCarryforwards','carryforward_dta_broader','Broader tax-carryforward DTA, not pure NOL or cash tax saving.','carryforward_dta',('nol_dta','dta_total')),
 bridge.Rule(FIELDS[0],'DeferredTaxAssetsGross','gross_deferred_tax_assets','Gross DTA total, not NOL-only or realizable/net value.','dta_total',('nol_dta','carryforward_dta','sbc_dta')),
 bridge.Rule(FIELDS[0],'DeferredTaxAssetsNet','net_deferred_tax_assets','Net DTA caption; allowances/netting/coverage must be reviewed.','dta_net',('dta_total','nol_dta')),
 bridge.Rule(FIELDS[0],'DeferredIncomeTaxAssetsNet','net_deferred_income_tax_assets','Net deferred-income-tax assets, not pure NOL or independent asset relative to other DTA captions.','income_dta_net',('dta_net','dta_total','nol_dta')),
 bridge.Rule(FIELDS[0],'DeferredIncomeTaxAssetsLiabilitiesNet','net_deferred_tax_asset_liability','Combined deferred-tax asset/liability net caption; no automatic sign/netting treatment.','dt_net',('dta_net','income_dta_net')),
 bridge.Rule(FIELDS[0],'DeferredTaxAssetsValuationAllowance','dta_valuation_allowance','Deferred-tax valuation allowance, not a second asset or a calculated NOL deduction.','dta_allowance',('dta_total','dta_net','nol_dta')),
)
SHARE_CONCEPT='EntityCommonStockSharesOutstanding'
WEIGHTED=('WeightedAverageNumberOfSharesOutstandingBasic','WeightedAverageNumberOfDilutedSharesOutstanding','WeightedAverageNumberOfSharesOutstandingBasicAndDiluted')


def null(p,field,reason,identity='requirement',as_of=None):
    v=missing.unavailable(p,field,reason,h.Review.UNREVIEWED)
    return replace(v,input_id='claims-shares:'+field.value+':'+identity,
        as_of=(p.annual_end if field is FIELDS[0] else as_of),unresolved_requirements=v.unresolved_requirements+LIMITS)


def population(e,spec,field,pop,overlap):
    result=r.inspect_instant(e,spec)
    vv=tuple(h.InputValue('claims-shares:'+field.value+':'+str(c.occurrences[0].ordinal),field,e.period,spec.as_of,
        c.value,spec.unit,1,1,c.precision,spec.role,h.Origin.REPORTED,h.Quality.LIMITED,spec.scope,
        h.Scope.RESTRICTED,h.Completeness.PARTIAL,h.Review.UNREVIEWED,c.evidence_references,None,None,(),
        'Exact observed population/date only; not issuer total, economic equivalence or complete scope.',
        ('inspection_only','no_aggregation_or_valuation_authorization','possible_overlap:'+','.join(overlap)),
        LIMITS,None,(pop,)) for c in result.candidates)
    row=dict(role=spec.role,scope=spec.scope,concept=spec.selectors[0].concept,namespace=spec.selectors[0].namespace,
        as_of=str(spec.as_of),dimensions=list(spec.selectors[0].dimensions),population=pop,possible_overlap=list(overlap),
        status='CONFLICTING' if result.competing_values else 'OBSERVED',
        candidates=[dict(value=str(c.value),unit=spec.unit,scale=1,sign=1,precision=c.precision,
            occurrences=[dict(ordinal=o.ordinal,context_id=o.context_id,unit_id=o.unit_id,raw_value=o.raw_value,
                precision=o.decimals,as_of=str(o.end),dimensions=list(o.dimensions)) for o in c.occurrences]) for c in result.candidates])
    if not vv:return None,row
    if result.competing_values:
        return replace(null(e.period,field,'Competing unequal values for '+spec.field_id+'; no precedence or rounding tolerance.',
            spec.field_id,spec.as_of),quality=h.Quality.CONFLICTING,alternatives=vv,role=spec.role),row
    return replace(vv[0],alternatives=vv[1:]),row


def inspect(e,field):
    if field not in FIELDS:raise h.InputError('Explicit other-bridge or shares field required')
    ns=e.namespaces.get('us-gaap' if field is FIELDS[0] else 'dei','')
    expected='http://fasb.org/us-gaap/' if field is FIELDS[0] else 'http://xbrl.sec.gov/dei/'
    values=[];rows=[];errors=[];diagnostics=[];groups={}
    rules={v.concept:v for v in RULES}
    names=set(rules) if field is FIELDS[0] else {SHARE_CONCEPT,*WEIGHTED}
    for f,i in e.facts:
        if f.concept not in names:continue
        c=e.contexts[f.context_id];ds=r.dimensions(c)
        reason=('WEIGHTED_AVERAGE_NOT_POINT_IN_TIME' if f.concept in WEIGHTED else
            'UNSUPPORTED_NAMESPACE' if f.namespace!=ns or not ns.startswith(expected) else
            'DURATION_NOT_INSTANT' if c.start is not None else
            'NOT_FISCAL_YEAR_END' if field is FIELDS[0] and c.end!=e.period.annual_end else
            'ENTITY_MISMATCH' if c.entity_identifier_scheme!='http://www.sec.gov/CIK' or int(c.entity_identifier)!=e.period.cik else
            'EXACT_POPULATION_CANDIDATE')
        diagnostics.append(dict(ordinal=i,concept=f.concept,namespace=f.namespace,context_id=c.context_id,
            start=None if c.start is None else str(c.start),end=str(c.end),dimensions=list(ds),entity=c.entity_identifier,
            raw_value=f.raw_value,precision=f.decimals,unit_id=f.unit_ref,nil=f.is_nil,disposition=reason,
            numeric_value=None if f.numeric_value is None else str(f.numeric_value),
            unit=None if f.unit is None else dict(numerator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.numerator_measures],
                denominator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.denominator_measures])))
        if reason=='EXACT_POPULATION_CANDIDATE':groups.setdefault((f.concept,c.end,tuple(sorted(ds))),None)
    for concept,date,ds in groups:
        rule=rules.get(concept);pop=rule.population if rule else 'common_shares_class_unreviewed'
        role=rule.role if rule else 'reported_point_in_time_common_shares'
        scope=(rule.definition if rule else 'Actual DEI observation date/class; not weighted-average shares or certified issuer total.')
        if ds:scope+=' Exact dimensioned population only; no consolidated/class-equivalence approval.'
        spec=r.InstantObservationSpec(field.value+':'+concept+':'+str(date)+':'+str(ds),(r.Selector(ns,concept,ds),),
            date,'USD' if rule else 'shares',role,scope,LIMITS)
        try: value,row=population(e,spec,field,pop,rule.overlap if rule else ())
        except h.InputError as exc:errors.append(spec.field_id+': '+str(exc));continue
        if value is not None:values.append(value);rows.append(row)
    observed=bool(values);conflict=any(v.quality is h.Quality.CONFLICTING for v in values)
    unsupported=any(v['disposition']=='UNSUPPORTED_NAMESPACE' for v in diagnostics)
    status=('EVIDENCE_GAP' if e.instance is None or e.unresolved_requirements or errors else
        'CONFLICTING' if conflict else 'OBSERVATIONS' if observed else 'UNSUPPORTED_SCOPE' if unsupported else 'NO_ELIGIBLE_OBSERVATIONS')
    requirement=null(e.period,field,'Complete non-overlapping bridge perimeter is unestablished.' if field is FIELDS[0] else
        'Issuer share-total/class completeness and intended consumption date are unapproved; no date selection or class sum.')
    return (requirement,*values),dict(status=status,has_observations=observed,has_conflicts=conflict,unsupported_candidates=unsupported,
        observations=rows,diagnostics=diagnostics,errors=list(errors)+list(e.unresolved_requirements),coverage='PARTIAL_UNKNOWN',
        unresolved_requirements=list(LIMITS),unobserved_concepts=sorted(names-{v['concept'] for v in rows}))


@dataclass(frozen=True)
class AnnualClaimsShares:
    period:h.Period
    other_bridge:tuple[h.InputValue,...]
    shares:tuple[h.InputValue,...]
    receipt:h.Receipt|None

    def __post_init__(self):
        if type(self.period) is not h.Period:raise h.InputError('Exact selected annual required')
        for field,values in zip(FIELDS,(self.other_bridge,self.shares)):
            h._typed(values,h.InputValue)
            if not values or len({v.input_id for v in values})!=len(values):raise h.InputError('Unique observations and explicit requirement required')
            if any(v.field is not field or v.period!=self.period or v.formula or v.completeness is h.Completeness.COMPLETE for v in values):
                raise h.InputError('Separate partial observations only')
        if self.receipt is None and any(v.value is not None or v.sources or v.alternatives for v in (*self.other_bridge,*self.shares)):
            raise h.InputError('Missing evidence cannot support observations')


def overlay(e):
    a,aa=inspect(e,FIELDS[0]);s,ss=inspect(e,FIELDS[1])
    return AnnualClaimsShares(e.period,a,s,e.instance),{FIELDS[0].value:aa,FIELDS[1].value:ss}


def build():
    prior,histories,previous=bridge.build();rows=[];out={}
    for name,annuals in previous.items():
        out[name]=[]
        for a in annuals:
            e=r.prepare(a.period,() if a.receipt is None else (a.receipt,),
                (r.ArtifactBinding(a.receipt.artifact.url,a.receipt.artifact.sha256,'instance'),)) if a.receipt else r.Evidence(a.period,(),None,{}, {},(),('Missing retained instance receipt.',))
            value,entry=overlay(e);out[name].append(value)
            rows.append(dict(issuer=name,identity=dict(cik=a.period.cik,accession=a.period.accession,form=a.period.form,
                annual_start=str(a.period.annual_start),annual_end=str(a.period.annual_end)),fields=entry,
                receipt=next(v['receipt'] for v in prior['rows'] if v['identity']['accession']==a.period.accession)))
        out[name]=tuple(out[name])
    def summary(aa):
        return {f.value:dict(outcomes=dict(Counter(v['fields'][f.value]['status'] for v in aa)),
            periods_with_observations=sum(v['fields'][f.value]['has_observations'] for v in aa),
            conflicting_periods=sum(v['fields'][f.value]['has_conflicts'] for v in aa),
            populations=sum(len(v['fields'][f.value]['observations']) for v in aa)) for f in FIELDS}
    shares=[v['fields'][FIELDS[1].value] for v in rows]
    ledger=dict(schema=SCHEMA,rule_version=1,rules=[dict(asdict(v),field=v.field.value,overlap=list(v.overlap)) for v in RULES],
        selected_periods=len(rows),issuer_count=len(out),summary=summary(rows),
        issuers={name:dict(periods=len(aa),families=summary([v for v in rows if v['issuer']==name])) for name,aa in out.items()},
        share_limits=dict(multiple_dates_periods=sum(len({o['as_of'] for o in v['observations']})>1 for v in shares),
            dimensioned_periods=sum(any(o['dimensions'] for o in v['observations']) for v in shares),
            non_year_end_periods=sum(any(o['as_of']!=row['identity']['annual_end'] for o in row['fields'][FIELDS[1].value]['observations']) for row in rows)),
        history_exceptions=prior['history_exceptions'],rows=rows,limitations=list(LIMITS),
        delivery='Separate other-claim/share overlays; no prior annual input replaced.')
    return ledger,histories,out,prior


def validate_overlay(v):
    v.__post_init__()
    if v.receipt is None:return v
    e=r.prepare(v.period,(v.receipt,),(r.ArtifactBinding(v.receipt.artifact.url,v.receipt.artifact.sha256,'instance'),))
    if v!=overlay(e)[0]:raise h.InputError('Claim/share source/date/class/precision differs from replay')
    return v


def serialize(v):
    if type(v) is not AnnualClaimsShares:raise h.InputError('Typed claim/share overlay required')
    validate_overlay(v);bodies={}
    return bridge.parent.canonical(dict(schema=SCHEMA,entry={f.name:bridge.parent._encode(getattr(v,f.name),bodies) for f in fields(v)},original_bodies=bodies))


def deserialize(payload):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise h.InputError('Duplicate serialized key')
            d[k]=v
        return d
    try:
        doc=json.loads(payload,object_pairs_hook=unique)
        if set(doc)!={'schema','entry','original_bodies'} or doc['schema']!=SCHEMA or set(doc['entry'])!={f.name for f in fields(AnnualClaimsShares)}:
            raise h.InputError('Closed claim/share envelope required')
        bodies={};used=set()
        for digest,encoded in doc['original_bodies'].items():
            raw=h._decode(encoded)
            if type(raw) is not bytes or bridge.parent.review.sha(raw)!=digest:raise h.InputError('Tampered source body')
            bodies[digest]=raw
        result=AnnualClaimsShares(**{k:bridge.parent._decode(v,bodies,used) for k,v in doc['entry'].items()})
        if used!=set(bodies):raise h.InputError('Unused serialized source body')
        return validate_overlay(result)
    except (ValueError,KeyError,TypeError) as exc:raise h.InputError('Invalid claim/share serialization') from exc
