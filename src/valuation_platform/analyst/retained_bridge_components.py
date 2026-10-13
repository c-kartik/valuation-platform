"""Retained year-end component inspection; no aggregates or scope acceptance.

Separate overlays leave reviewed pilot and prior preparation payloads untouched.
Element definitions describe candidates, not issuer-specific note interpretations.
"""
from collections import Counter
from dataclasses import dataclass, fields, replace, asdict
import json
from . import historical_inputs as h, retained_components as r
from . import retained_cfo_preparation as cfo, retained_income_preparation as missing
from . import refreshed_capex as parent

SCHEMA = 'retained-bridge-component-inspection-v1'
LEDGER = 'docs/retained-bridge-component-ledger.json'
FIELDS = (h.Field.CASH_INVESTMENTS, h.Field.DEBT_LEASES)
LIMITS = (
    'Exact fact binding and taxonomy population inspection, not independently reviewed issuer financial scope.',
    'Partial/unknown family coverage; absent components are not zero and no aggregate is authorized.',
    'Parent/child and alternative accounting populations may overlap; relationships require issuer review.',
    'Liabilities, principal, fair value and undiscounted schedules are distinct; lease cash payments remain separate.',
    'No unrestricted/excess cash, net debt, debt convention, economic treatment or valuation authorization.',
)


@dataclass(frozen=True)
class Rule:
    field: h.Field
    concept: str
    role: str
    definition: str
    population: str
    overlap: tuple[str, ...] = ()


# Closed standard element mapping. No substrings, issuer extensions, financial
# equivalence or automatic adoption of the four reviewed note interpretations.
RULES = (
    Rule(h.Field.CASH_INVESTMENTS, 'CashAndCashEquivalentsAtCarryingValue', 'cash_equivalents_carrying', 'Cash and cash equivalents carrying caption; unrestricted/excess status unestablished.', 'cash'),
    Rule(h.Field.CASH_INVESTMENTS, 'Cash', 'cash_only', 'Cash-only caption, not a cash-equivalents total.', 'cash_only', ('cash',)),
    Rule(h.Field.CASH_INVESTMENTS, 'ShortTermInvestments', 'current_investments_scope_unreviewed', 'Current investments; marketability and instrument composition need issuer evidence.', 'current_investments'),
    Rule(h.Field.CASH_INVESTMENTS, 'MarketableSecuritiesCurrent', 'current_marketable_securities', 'Current marketable securities; restrictions and cash-equivalent inclusion unestablished.', 'current_marketable', ('current_investments', 'cash')),
    Rule(h.Field.CASH_INVESTMENTS, 'MarketableSecuritiesNoncurrent', 'noncurrent_marketable_securities', 'Noncurrent marketable securities; lock-ups and restrictions need issuer evidence.', 'noncurrent_marketable', ('long_term_investments',)),
    Rule(h.Field.CASH_INVESTMENTS, 'LongTermInvestments', 'long_term_investments_mixed', 'Long-term investment caption, not assumed marketable-only or liquid.', 'long_term_investments', ('noncurrent_marketable', 'equity_method', 'strategic_equity')),
    Rule(h.Field.CASH_INVESTMENTS, 'OtherLongTermInvestments', 'other_long_term_investments', 'Other long-term investments, composition unreviewed.', 'other_long_term', ('long_term_investments', 'strategic_equity', 'equity_method')),
    Rule(h.Field.CASH_INVESTMENTS, 'CashCashEquivalentsAndShortTermInvestments', 'cash_current_investment_parent', 'Combined cash/equivalents and short-term investment parent, not an additional asset.', 'cash_current_parent', ('cash', 'current_investments', 'current_marketable')),
    Rule(h.Field.CASH_INVESTMENTS, 'CashCashEquivalentsAndMarketableSecurities', 'cash_marketable_parent', 'Combined cash and marketable securities parent; current/noncurrent perimeter needs review.', 'cash_marketable_parent', ('cash', 'current_marketable', 'noncurrent_marketable', 'cash_current_parent')),
    Rule(h.Field.CASH_INVESTMENTS, 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 'cash_restricted_parent', 'Combined cash/equivalents and restricted cash; not standalone restricted cash.', 'cash_restricted_parent', ('cash', 'restricted_cash')),
    Rule(h.Field.CASH_INVESTMENTS, 'RestrictedCashAndCashEquivalentsCurrent', 'restricted_cash_current', 'Current restricted cash/equivalents, not unrestricted liquidity.', 'restricted_cash', ('cash_restricted_parent',)),
    Rule(h.Field.CASH_INVESTMENTS, 'RestrictedCashAndCashEquivalentsNoncurrent', 'restricted_cash_noncurrent', 'Noncurrent restricted cash/equivalents.', 'restricted_cash_noncurrent', ('cash_restricted_parent',)),
    Rule(h.Field.CASH_INVESTMENTS, 'RestrictedCashAndCashEquivalents', 'restricted_cash_parent', 'Restricted cash/equivalents total; current/noncurrent inclusion needs review.', 'restricted_cash_parent', ('restricted_cash', 'restricted_cash_noncurrent', 'cash_restricted_parent')),
    Rule(h.Field.CASH_INVESTMENTS, 'EquityMethodInvestments', 'equity_method_investments', 'Equity-method carrying investments, not marketable securities or cash.', 'equity_method', ('long_term_investments', 'other_long_term')),
    Rule(h.Field.CASH_INVESTMENTS, 'EquitySecuritiesWithoutReadilyDeterminableFairValueAmount', 'measurement_alternative_equity', 'Nonmarketable equity measurement-alternative carrying population, not cash.', 'strategic_equity', ('long_term_investments', 'other_long_term')),
    Rule(h.Field.CASH_INVESTMENTS, 'EquitySecuritiesFvNi', 'fair_value_equity_investments', 'Equity securities measured at fair value through earnings; instrument/current/restriction scope unreviewed.', 'fair_value_equity', ('current_investments', 'long_term_investments')),
    Rule(h.Field.CASH_INVESTMENTS, 'AvailableForSaleSecuritiesDebtSecurities', 'available_for_sale_debt', 'Available-for-sale debt securities; maturity/current allocation and cash inclusion unreviewed.', 'afs_debt', ('current_investments', 'long_term_investments', 'cash')),
    Rule(h.Field.CASH_INVESTMENTS, 'HeldToMaturitySecurities', 'held_to_maturity_investments', 'Held-to-maturity investments; not automatically marketable or cash-equivalent.', 'htm', ('current_investments', 'long_term_investments')),
    Rule(h.Field.DEBT_LEASES, 'CommercialPaper', 'commercial_paper_borrowing', 'Commercial-paper borrowing balance, not investment holdings.', 'commercial_paper', ('short_term_borrowing', 'current_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'ShortTermBorrowings', 'short_term_borrowing', 'Short-term borrowing caption; commercial-paper/current debt inclusion needs review.', 'short_term_borrowing', ('commercial_paper', 'current_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'ShortTermBorrowingsCurrent', 'current_short_term_borrowing', 'Current short-term borrowing caption; commercial-paper inclusion needs review.', 'current_short_term_borrowing', ('short_term_borrowing', 'commercial_paper', 'current_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'ShortTermDebtCurrent', 'current_short_term_debt', 'Current short-term debt caption, not current portion of long-term debt equivalence.', 'short_term_debt', ('short_term_borrowing', 'commercial_paper', 'current_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebtCurrent', 'current_long_term_debt', 'Current portion of long-term debt; principal/carrying basis needs note review.', 'current_long_term_debt', ('current_debt_parent', 'long_term_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebtNoncurrent', 'noncurrent_long_term_debt', 'Noncurrent long-term debt; principal/carrying basis needs note review.', 'noncurrent_long_term_debt', ('long_term_debt_parent',)),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebt', 'long_term_debt_parent_basis_unreviewed', 'Long-term debt parent; do not infer carrying versus face principal from tag alone.', 'long_term_debt_parent', ('current_long_term_debt', 'noncurrent_long_term_debt', 'instrument_carrying')),
    Rule(h.Field.DEBT_LEASES, 'DebtCurrent', 'current_debt_parent', 'Current debt parent; short-term/current long-term composition needs review.', 'current_debt_parent', ('short_term_borrowing', 'commercial_paper', 'current_long_term_debt')),
    Rule(h.Field.DEBT_LEASES, 'DebtAndCapitalLeaseObligations', 'debt_legacy_lease_parent', 'Combined debt and legacy capital-lease obligations, not debt-only or finance-lease equivalence.', 'debt_lease_parent', ('long_term_debt_parent', 'finance_lease_parent', 'current_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebtAndCapitalLeaseObligations', 'long_term_debt_legacy_lease_parent', 'Long-term debt/legacy capital-lease combined caption; actual inclusion unreviewed.', 'long_term_debt_lease_parent', ('long_term_debt_parent', 'finance_lease_parent')),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebtAndCapitalLeaseObligationsCurrent', 'current_debt_legacy_lease_parent', 'Current long-term debt and capital-lease caption.', 'current_debt_lease_parent', ('current_long_term_debt', 'finance_lease_current')),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebtAndCapitalLeaseObligationsNoncurrent', 'noncurrent_debt_legacy_lease_parent', 'Noncurrent long-term debt and capital-lease caption.', 'noncurrent_debt_lease_parent', ('noncurrent_long_term_debt', 'finance_lease_noncurrent')),
    Rule(h.Field.DEBT_LEASES, 'DebtInstrumentCarryingAmount', 'instrument_carrying_candidate', 'Instrument carrying-amount element; issuer note may use another presentation basis, requiring review.', 'instrument_carrying', ('long_term_debt_parent', 'current_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'DebtInstrumentFaceAmount', 'instrument_face_principal', 'Instrument face principal, not carrying amount or fair value.', 'instrument_face', ('long_term_debt_parent', 'instrument_carrying')),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebtFairValue', 'debt_fair_value', 'Debt fair value, not carrying amount or additional debt.', 'debt_fair_value', ('long_term_debt_parent', 'instrument_carrying', 'instrument_face')),
    Rule(h.Field.DEBT_LEASES, 'LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths', 'next_year_principal_schedule', 'Contractual next-year principal maturity schedule, not current carrying debt or past cash paid.', 'principal_schedule', ('current_long_term_debt', 'long_term_debt_parent')),
    Rule(h.Field.DEBT_LEASES, 'OperatingLeaseLiability', 'discounted_operating_lease_parent', 'Recognized discounted operating-lease liability, not cash payments or ROU asset.', 'operating_lease_parent', ('operating_lease_current', 'operating_lease_noncurrent')),
    Rule(h.Field.DEBT_LEASES, 'OperatingLeaseLiabilityCurrent', 'discounted_operating_lease_current', 'Current recognized operating-lease liability.', 'operating_lease_current', ('operating_lease_parent',)),
    Rule(h.Field.DEBT_LEASES, 'OperatingLeaseLiabilityNoncurrent', 'discounted_operating_lease_noncurrent', 'Noncurrent recognized operating-lease liability.', 'operating_lease_noncurrent', ('operating_lease_parent',)),
    Rule(h.Field.DEBT_LEASES, 'FinanceLeaseLiability', 'discounted_finance_lease_parent', 'Recognized discounted finance-lease liability, not principal payments or ROU asset.', 'finance_lease_parent', ('finance_lease_current', 'finance_lease_noncurrent', 'debt_lease_parent')),
    Rule(h.Field.DEBT_LEASES, 'FinanceLeaseLiabilityCurrent', 'discounted_finance_lease_current', 'Current recognized finance-lease liability.', 'finance_lease_current', ('finance_lease_parent', 'current_debt_lease_parent')),
    Rule(h.Field.DEBT_LEASES, 'FinanceLeaseLiabilityNoncurrent', 'discounted_finance_lease_noncurrent', 'Noncurrent recognized finance-lease liability.', 'finance_lease_noncurrent', ('finance_lease_parent', 'noncurrent_debt_lease_parent')),
    Rule(h.Field.DEBT_LEASES, 'LesseeOperatingLeaseLiabilityPaymentsDue', 'undiscounted_operating_lease_schedule', 'Future undiscounted operating-lease payments, not discounted liability or historical service cash.', 'operating_lease_schedule', ('operating_lease_parent',)),
    Rule(h.Field.DEBT_LEASES, 'FinanceLeaseLiabilityPaymentsDue', 'undiscounted_finance_lease_schedule', 'Future undiscounted finance-lease payments, not liability or historical principal cash.', 'finance_lease_schedule', ('finance_lease_parent',)),
)
EXCLUDED = {
    'OperatingLeasePayments': 'LEASE_CASH_PAYMENT_NOT_LIABILITY',
    'FinanceLeaseInterestPaymentOnLiability': 'LEASE_CASH_INTEREST_NOT_LIABILITY',
    'FinanceLeasePrincipalPayments': 'LEASE_CASH_PRINCIPAL_NOT_LIABILITY',
    'OperatingLeaseRightOfUseAsset': 'LEASE_ASSET_NOT_DEBT',
    'FinanceLeaseRightOfUseAsset': 'LEASE_ASSET_NOT_DEBT',
    'PaymentsToAcquireInvestments': 'CASH_PURCHASE_FLOW_NOT_INVESTMENT_BALANCE',
    'ProceedsFromIssuanceOfLongTermDebt': 'BORROWING_FLOW_NOT_DEBT_BALANCE',
    'RepaymentsOfLongTermDebt': 'PRINCIPAL_CASH_FLOW_NOT_DEBT_BALANCE',
}
# Known pilot combined extension caption: retain diagnostics, not a selector or
# universal lease-parent interpretation. Other extensions remain in original bodies.
DIAGNOSTIC_ONLY = {'OperatingandFinanceLeaseLiability': 'UNREVIEWED_COMBINED_LEASE_CAPTION'}


def inspect(evidence, field):
    if field not in FIELDS: raise h.InputError('Explicit bridge component family required')
    ns = evidence.namespaces.get('us-gaap', '')
    values = []; rows = []; errors = []
    if not ns.startswith('http://fasb.org/us-gaap/'):
        return (), [], ('Verified standard taxonomy namespace unavailable.',)
    for rule in (v for v in RULES if v.field is field):
        spec = r.SelectionSpec('bridge:'+rule.concept, (r.Selector(ns, rule.concept, ()),),
            'instant', 'USD', rule.role, rule.definition, LIMITS)
        try: result = r.inspect(evidence, spec)
        except h.InputError as exc:
            errors.append(rule.concept+': '+str(exc)); continue
        if not result.candidates: continue
        candidates = tuple(h.InputValue('bridge:'+rule.concept+':'+str(c.occurrences[0].ordinal), field,
            evidence.period, evidence.period.annual_end, c.value, 'USD', 1, 1, c.precision, rule.role,
            h.Origin.REPORTED, h.Quality.LIMITED, rule.definition, h.Scope.RESTRICTED,
            h.Completeness.PARTIAL, h.Review.UNREVIEWED, c.evidence_references, None, None, (),
            'Verified exact instant observation only; element population is not independently reviewed issuer scope.',
            ('rule_version:1', 'no_aggregation_or_valuation_authorization', 'separate_from_lease_cash_payments',
             'possible_overlap:'+','.join(rule.overlap)), LIMITS, None, (rule.population,)) for c in result.candidates)
        if result.competing_values:
            gap = null(evidence.period, field, 'Unequal eligible values for '+rule.concept+'; no silent selection.')
            values.append(replace(gap, input_id='bridge:conflict:'+rule.concept, role=rule.role,
                quality=h.Quality.CONFLICTING, alternatives=candidates))
        else: values.append(replace(candidates[0], alternatives=candidates[1:]))
        rows.append(dict(concept=rule.concept, role=rule.role, definition=rule.definition,
            population=rule.population, possible_overlap=list(rule.overlap), status='CONFLICTING' if result.competing_values else 'OBSERVED',
            candidates=[dict(value_usd=str(c.value), namespace=c.namespace, precision=c.precision, scale=1, sign=1,
                occurrences=[dict(ordinal=o.ordinal, context_id=o.context_id, unit_id=o.unit_id,
                    raw_value=o.raw_value, precision=o.decimals, start=None, end=str(o.end), dimensions=list(o.dimensions))
                    for o in c.occurrences]) for c in result.candidates]))
    return tuple(values), rows, tuple(errors)


def null(period, field, reason):
    value = missing.unavailable(period, field, reason, h.Review.UNREVIEWED)
    return replace(value, input_id='bridge:requirement:'+field.value, as_of=period.annual_end,
        unresolved_requirements=value.unresolved_requirements+LIMITS)


def package(evidence, field):
    values, rows, errors = inspect(evidence, field)
    conflict = any(v.quality is h.Quality.CONFLICTING for v in values)
    observed = any(v.value is not None or v.alternatives for v in values)
    status = ('EVIDENCE_GAP' if evidence.instance is None or evidence.unresolved_requirements or errors else
              'CONFLICTING' if conflict else 'OBSERVATIONS' if observed else 'NO_ELIGIBLE_OBSERVATIONS')
    # An explicit family requirement always remains, even with many observations.
    requirement = null(evidence.period, field, 'Complete non-overlapping '+field.value+' perimeter is not established; components only.')
    return (requirement, *values), dict(status=status, has_eligible_observations=observed,
        has_conflicts=conflict, has_evidence_gap=status=='EVIDENCE_GAP', coverage='PARTIAL_UNKNOWN',
        observations=rows, errors=list(errors)+list(evidence.unresolved_requirements),
        unobserved_concepts=[v.concept for v in RULES if v.field is field and not any(v.concept==row['concept'] for row in rows)],
        unresolved_requirements=list(LIMITS))


def diagnostics(evidence):
    names={v.concept for v in RULES}|set(EXCLUDED)|set(DIAGNOSTIC_ONLY); rows=[]; p=evidence.period
    for f, ordinal in evidence.facts:
        if f.concept not in names: continue
        c=evidence.contexts[f.context_id]
        if c.end != p.annual_end: continue
        ds=r.dimensions(c)
        disposition=('UNSUPPORTED_EXTENSION' if f.namespace!=evidence.namespaces.get('us-gaap') else
            EXCLUDED[f.concept] if f.concept in EXCLUDED else
            DIAGNOSTIC_ONLY[f.concept] if f.concept in DIAGNOSTIC_ONLY else
            'DURATION_NOT_YEAR_END_BALANCE' if c.start is not None else
            'DIMENSIONED_SCOPE_REQUIRES_REVIEW' if ds else
            'ENTITY_MISMATCH' if c.entity_identifier_scheme!='http://www.sec.gov/CIK' or int(c.entity_identifier)!=p.cik else
            'STANDARD_NON_DIMENSIONAL_INSTANT_CANDIDATE')
        rows.append(dict(concept=f.concept, namespace=f.namespace, ordinal=ordinal, context_id=c.context_id,
            start=None if c.start is None else str(c.start), end=str(c.end), dimensions=list(ds),
            entity=c.entity_identifier, unit_id=f.unit_ref, raw_value=f.raw_value,
            precision=f.decimals, nil=f.is_nil, disposition=disposition,
            numeric_value=None if f.numeric_value is None else str(f.numeric_value),scale=1,sign=1,
            source_url=f.source_url,instance_sha256=evidence.instance.artifact.sha256,
            unit=None if f.unit is None else dict(numerator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.numerator_measures],
                denominator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.denominator_measures])))
    return rows


@dataclass(frozen=True)
class AnnualComponents:
    period: h.Period
    cash_investments: tuple[h.InputValue, ...]
    debt_leases: tuple[h.InputValue, ...]
    receipt: h.Receipt | None

    def __post_init__(self):
        if type(self.period) is not h.Period: raise h.InputError('Exact period required')
        for field, values in zip(FIELDS, (self.cash_investments, self.debt_leases)):
            h._typed(values,h.InputValue)
            if not values or len({v.input_id for v in values})!=len(values): raise h.InputError('Unique component observations and explicit requirement required')
            if any(v.field is not field or v.period!=self.period or v.as_of!=self.period.annual_end for v in values):
                raise h.InputError('Exact component field and annual-end binding required')
            if any(v.formula or v.completeness is h.Completeness.COMPLETE for v in values): raise h.InputError('No aggregates or completeness approval')
        if self.receipt is None and any(v.value is not None or v.alternatives for v in (*self.cash_investments,*self.debt_leases)):
            raise h.InputError('Absent receipt cannot support components')


def overlay(evidence):
    cash,cr=package(evidence,FIELDS[0]); debt,dr=package(evidence,FIELDS[1])
    return AnnualComponents(evidence.period,cash,debt,evidence.instance), {FIELDS[0].value:cr,FIELDS[1].value:dr}


def build():
    previous,histories=parent.build(); rows=[]; overlays={}
    for name,wrapped in histories.items():
        history=wrapped.bundle if type(wrapped) is parent.RefreshedHistory else wrapped
        entries=[]
        for annual in history.annuals:
            try: evidence=cfo.prepare(annual)
            except (ValueError, KeyError) as exc:
                evidence=r.Evidence(annual.period,(),None,{}, {},(),
                    ('Retained instance/receipt/identity structure unavailable: '+type(exc).__name__+': '+str(exc),))
            result, families=overlay(evidence); entries.append(result)
            receipt=evidence.instance
            rows.append(dict(issuer=name,identity=dict(cik=annual.period.cik,accession=annual.period.accession,
                form=annual.period.form,annual_start=str(annual.period.annual_start),annual_end=str(annual.period.annual_end)),
                fields=families,diagnostics=diagnostics(evidence),receipt=None if receipt is None else dict(
                    url=receipt.artifact.url,sha256=receipt.artifact.sha256,digest_type=receipt.artifact.digest_type,
                    representation=receipt.artifact.representation,retrieved_at_utc=receipt.retrieved_at_utc,
                    http_status=receipt.http_status,retrieval_mode=receipt.retrieval_mode)))
        overlays[name]=tuple(entries)
    def summary(selected):
        return {f.value:dict(outcomes=dict(Counter(v['fields'][f.value]['status'] for v in selected)),
            periods_with_observations=sum(v['fields'][f.value]['has_eligible_observations'] for v in selected),
            conflicting_periods=sum(v['fields'][f.value]['has_conflicts'] for v in selected),
            component_populations=sum(len(v['fields'][f.value]['observations']) for v in selected)) for f in FIELDS}
    backlog=[dict(issuer=row['issuer'],identity=row['identity'],field=f.value,requirements=row['fields'][f.value]['errors'])
        for row in rows for f in FIELDS if row['fields'][f.value]['has_evidence_gap']]
    ledger=dict(schema=SCHEMA,rule_version=1,rules=[dict(asdict(v),field=v.field.value,overlap=list(v.overlap)) for v in RULES],
        selected_periods=len(rows),issuer_count=len(histories),summary=summary(rows),
        issuers={name:dict(periods=len(entries),families=summary([v for v in rows if v['issuer']==name])) for name,entries in overlays.items()},
        evidence_backlog=backlog,history_exceptions=previous['history_exceptions'],limitations=list(LIMITS),rows=rows,
        delivery='Separate instant-component overlays; all original parent/pilot inputs remain unchanged.')
    return ledger,histories,overlays


def validate_overlay(value):
    if type(value) is not AnnualComponents: raise h.InputError('Typed instant-component overlay required')
    value.__post_init__()
    if value.receipt is None: return value
    evidence=r.prepare(value.period,(value.receipt,),
        (r.ArtifactBinding(value.receipt.artifact.url,value.receipt.artifact.sha256,'instance'),))
    expected,_=overlay(evidence)
    if value!=expected: raise h.InputError('Component values/roles/precision/provenance differ from retained replay')
    return value


def serialize(value):
    validate_overlay(value); bodies={}
    entry={f.name:parent._encode(getattr(value,f.name),bodies) for f in fields(value)}
    return parent.canonical(dict(schema=SCHEMA,entry=entry,original_bodies=bodies))


def deserialize(payload):
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result: raise h.InputError('Duplicate serialized key')
            result[k]=v
        return result
    try:
        doc=json.loads(payload,object_pairs_hook=unique)
        if set(doc)!={'schema','entry','original_bodies'} or doc['schema']!=SCHEMA: raise h.InputError('Exact component envelope required')
        if set(doc['entry'])!={f.name for f in fields(AnnualComponents)}: raise h.InputError('Closed component fields required')
        bodies={}; used=set()
        for digest,encoded in doc['original_bodies'].items():
            raw=h._decode(encoded)
            if type(raw) is not bytes or parent.review.sha(raw)!=digest: raise h.InputError('Tampered original body')
            bodies[digest]=raw
        result=AnnualComponents(**{k:parent._decode(v,bodies,used) for k,v in doc['entry'].items()})
        if used!=set(bodies): raise h.InputError('Unused serialized body')
        return validate_overlay(result)
    except (ValueError,KeyError,TypeError) as exc: raise h.InputError('Invalid component payload') from exc
