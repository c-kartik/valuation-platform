"""Retained reconciliation observations, never a working-capital aggregate.

Explicit standard-element meanings, not a name-pattern financial resolver.
Pilot interpretations/outputs stay in their original reviewed mapping.
"""
from dataclasses import dataclass, replace, asdict
import json
import re
from types import MappingProxyType
from . import historical_inputs as h, retained_components as r
from . import retained_cfo_preparation as cfo, retained_income_preparation as missing


@dataclass(frozen=True)
class Rule:
    concept: str
    sign: int
    population: str
    definition: str
    possible_children: tuple[str, ...] = ()


# These are individual taxonomy semantics. The asset increase/decrease elements
# report account movement (minus for cash), liability elements plus for cash.
# No inference from arbitrary IncreaseDecrease spelling is used for selection.
RULES = (
    Rule('IncreaseDecreaseInAccountsReceivable', -1, 'receivables', 'Increase/decrease in accounts receivable.'),
    Rule('IncreaseDecreaseInOtherReceivables', -1, 'other_receivables', 'Increase/decrease in other receivables.'),
    Rule('IncreaseDecreaseInReceivables', -1, 'combined_receivables', 'Increase/decrease in receivables.', ('IncreaseDecreaseInAccountsReceivable', 'IncreaseDecreaseInOtherReceivables')),
    Rule('IncreaseDecreaseInAccountsAndOtherReceivables', -1, 'combined_receivables', 'Increase/decrease in accounts and other receivables.', ('IncreaseDecreaseInAccountsReceivable', 'IncreaseDecreaseInOtherReceivables')),
    Rule('IncreaseDecreaseInInventories', -1, 'inventories', 'Increase/decrease in inventories.'),
    Rule('IncreaseDecreaseInPrepaidExpense', -1, 'prepaid', 'Increase/decrease in prepaid expense.'),
    Rule('IncreaseDecreaseInPrepaidDeferredExpenseAndOtherAssets', -1, 'combined_prepaid_deferred_other_assets', 'Increase/decrease in prepaid/deferred expense and other assets.', ('IncreaseDecreaseInPrepaidExpense', 'IncreaseDecreaseInOtherCurrentAssets', 'IncreaseDecreaseInOtherNoncurrentAssets')),
    Rule('IncreaseDecreaseInOtherCurrentAssets', -1, 'other_current_assets', 'Increase/decrease in other current assets.'),
    Rule('IncreaseDecreaseInOtherNoncurrentAssets', -1, 'other_noncurrent_assets', 'Increase/decrease in other noncurrent assets.'),
    Rule('IncreaseDecreaseInOtherOperatingAssets', -1, 'other_operating_assets_current_noncurrent_unspecified', 'Increase/decrease in other operating assets.'),
    Rule('IncreaseDecreaseInAccountsPayable', 1, 'payables', 'Increase/decrease in accounts payable.'),
    Rule('IncreaseDecreaseInAccountsPayableTrade', 1, 'trade_payables', 'Increase/decrease in trade accounts payable.'),
    Rule('IncreaseDecreaseInAccruedLiabilities', 1, 'accrued_liabilities', 'Increase/decrease in accrued liabilities.', ('IncreaseDecreaseInAccruedIncomeTaxesPayable',)),
    Rule('IncreaseDecreaseInAccountsPayableAndAccruedLiabilities', 1, 'combined_payables_accruals', 'Increase/decrease in accounts payable and accrued liabilities.', ('IncreaseDecreaseInAccountsPayable', 'IncreaseDecreaseInAccruedLiabilities')),
    Rule('IncreaseDecreaseInAccruedLiabilitiesAndOtherOperatingLiabilities', 1, 'combined_accruals_other_liabilities', 'Increase/decrease in accrued and other operating liabilities.', ('IncreaseDecreaseInAccruedLiabilities', 'IncreaseDecreaseInOtherOperatingLiabilities')),
    Rule('IncreaseDecreaseInOtherOperatingLiabilities', 1, 'other_operating_liabilities_current_noncurrent_unspecified', 'Increase/decrease in other operating liabilities.'),
    Rule('IncreaseDecreaseInOtherCurrentLiabilities', 1, 'other_current_liabilities', 'Increase/decrease in other current liabilities.'),
    Rule('IncreaseDecreaseInOtherNoncurrentLiabilities', 1, 'other_noncurrent_liabilities', 'Increase/decrease in other noncurrent liabilities.'),
    Rule('IncreaseDecreaseInAccruedIncomeTaxesPayable', 1, 'income_tax_liabilities', 'Increase/decrease in accrued income taxes payable.'),
    Rule('IncreaseDecreaseInIncomeTaxes', 1, 'income_taxes_mixed', 'Reported income-tax reconciliation movement; reviewed Alphabet mapping uses cash contribution plus.'),
    Rule('IncreaseDecreaseInContractWithCustomerLiability', 1, 'contract_liabilities', 'Increase/decrease in contract-with-customer liabilities.'),
    Rule('IncreaseDecreaseInDeferredRevenue', 1, 'deferred_revenue', 'Increase/decrease in deferred revenue.'),
    Rule('IncreaseDecreaseInOperatingCapital', -1, 'reported_operating_capital_total', 'Increase/decrease in operating capital; an account-movement total, not a complete requested perimeter.', tuple()),
)
RULE_BY_CONCEPT = MappingProxyType({v.concept: v for v in RULES})
LIMITATIONS = (
    'Reported reconciliation rows are not book delta NWC, additional CFO or an approved operating investment aggregate.',
    'Coverage/non-overlap is unproved; no aggregation, absent component zero or completeness certification.',
    'Consolidated versus continuing scope and acquisition/disposal/FX/reclassification exclusions require statement-specific evidence; not inferred from nondimensionality.',
    'Tax/noncurrent/combined populations stay separate; issuer extensions and unreviewed net movements have no sign/scope approval.',
)


def inspect(evidence):
    """One explicit selector per population; conflicts are within, not across rows."""
    ns = evidence.namespaces.get('us-gaap', '')
    observations = []; ledger = []; errors = []
    if not ns.startswith('http://fasb.org/us-gaap/'):
        return (), [], ['Exact standard US-GAAP namespace unavailable.']
    for rule in RULES:
        spec = r.SelectionSpec(rule.concept, (r.Selector(ns, rule.concept, ()),), 'annual', 'USD',
            'reported_reconciliation_movement', rule.definition, LIMITATIONS)
        try:
            result = r.inspect(evidence, spec)
        except h.InputError as exc:
            reason = rule.concept + ': ' + str(exc)
            errors.append(reason)
            observations.append(replace(missing.unavailable(evidence.period, h.Field.CF_WORKING_CAPITAL,
                reason, h.Review.REVIEWED), input_id='retained-cf-movement:invalid:' + rule.concept))
            continue
        if not result.candidates: continue
        conflict = bool(result.competing_values)
        candidates = tuple(h.InputValue('retained-cf-movement:' + rule.concept + ':root-' + str(c.occurrences[0].ordinal),
            h.Field.CF_WORKING_CAPITAL, evidence.period, None, c.value * rule.sign, 'USD', 1, rule.sign,
            c.precision, 'reported_operating_capital_total' if rule.population=='reported_operating_capital_total' else 'reported_cash_flow_movement',
            h.Origin.REPORTED, h.Quality.LIMITED, rule.population + '; ' + rule.definition,
            h.Scope.MIXED, h.Completeness.PARTIAL, h.Review.REVIEWED, c.evidence_references,
            None, None, (), 'Explicit taxonomy account-movement sign only; statement scope not independently re-reviewed.',
            ('no_aggregation', 'not_book_delta_nwc', 'not_additional_cfo', 'statement_scope_unverified',
             'acquisition_exclusion_not_established', 'rule_version:1'), LIMITATIONS, None, (rule.population,))
            for c in result.candidates)
        if conflict:
            value = missing.unavailable(evidence.period, h.Field.CF_WORKING_CAPITAL,
                'Unequal eligible values for ' + rule.concept + '; no precedence selection.', h.Review.REVIEWED)
            observations.append(replace(value, input_id='retained-cf-movement:conflict:' + rule.concept,
                alternatives=candidates, quality=h.Quality.CONFLICTING))
        else:
            observations.append(replace(candidates[0], alternatives=candidates[1:]))
        ledger.append(dict(concept=rule.concept, population=rule.population, definition=rule.definition,
            sign=rule.sign, status='CONFLICTING' if conflict else 'OBSERVED',
            possible_children=([v.concept for v in RULES if v is not rule] if rule.population=='reported_operating_capital_total'
                else list(rule.possible_children)), overlap='POTENTIAL_NOT_INDEPENDENTLY_PROVED',
            candidates=[dict(raw_value=str(c.value), cash_contribution=str(c.value * rule.sign), precision=c.precision,
                occurrences=[dict(ordinal=o.ordinal, context_id=o.context_id, unit_id=o.unit_id,
                    raw_value=o.raw_value, precision=o.decimals) for o in c.occurrences],
                source=dict(url=evidence.instance.artifact.url, sha256=evidence.instance.artifact.sha256,
                    representation=evidence.instance.artifact.representation, digest_type=evidence.instance.artifact.digest_type,
                    retrieved_at_utc=evidence.instance.retrieved_at_utc, http_status=evidence.instance.http_status,
                    namespace=c.namespace, accession=evidence.period.accession, start=str(evidence.period.annual_start),
                    end=str(evidence.period.annual_end), unit='USD', dimensions=[])) for c in result.candidates]))
    return tuple(observations), ledger, errors


def unsupported(evidence):
    """Name-pattern discovery ONLY: not eligibility, role, sign or a financial claim.

    This retains unreviewed change-tag diagnostics (including non-WC concepts).
    It deliberately cannot produce InputValues or approve extensions.
    """
    rows = []
    for f, ordinal in evidence.facts:
        if not f.concept.lower().startswith('increasedecrease'): continue
        context = evidence.contexts[f.context_id]
        if (context.start, context.end) != (evidence.period.annual_start, evidence.period.annual_end): continue
        standard = f.namespace == evidence.namespaces.get('us-gaap')
        ds = r.dimensions(context)
        valid=(not f.is_nil and f.numeric_value is not None and f.unit is not None
            and not f.unit.denominator_measures and len(f.unit.numerator_measures)==1
            and f.unit.numerator_measures[0].namespace=='http://www.xbrl.org/2003/iso4217'
            and f.unit.numerator_measures[0].local_name=='USD' and re.fullmatch(r'INF|-?\d+',f.decimals or ''))
        if standard and f.concept in RULE_BY_CONCEPT and not ds and valid: continue
        rows.append(dict(namespace=f.namespace, concept=f.concept, ordinal=ordinal, context_id=f.context_id,
            raw_value=f.raw_value, precision=f.decimals, unit_id=f.unit_ref, nil=f.is_nil, dimensions=list(ds),
            start=str(context.start), end=str(context.end), entity=context.entity_identifier,
            numeric_value=None if f.numeric_value is None else str(f.numeric_value),
            unit=None if f.unit is None else dict(numerator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.numerator_measures],
                denominator=[dict(namespace=q.namespace,name=q.local_name) for q in f.unit.denominator_measures]),
            normalized_sign=None, role=None, disposition='DIMENSIONED_NOT_SELECTED' if ds else
                'UNSUPPORTED_EXTENSION' if not standard else 'INVALID_MAPPED_EVIDENCE' if f.concept in RULE_BY_CONCEPT else 'UNREVIEWED_ROLE_OR_SIGN',
            source_url=f.source_url, sha256=evidence.instance.artifact.sha256))
    return rows


def build():
    baseline, histories = cfo.build(); rows = []; packages = {}; summaries = {}
    for name, history in histories.items():
        annuals = []
        for annual in history.annuals:
            evidence = cfo.prepare(annual)
            observations, facts, errors = inspect(evidence)
            diagnostics = unsupported(evidence)
            original = tuple(v for v in annual.inputs if v.field is h.Field.CF_WORKING_CAPITAL)
            pilot = any(v.value is not None for v in original)
            if not pilot:
                values = observations or (missing.unavailable(annual.period, h.Field.CF_WORKING_CAPITAL,
                    'No eligible observation in bounded retained taxonomy mapping; not absence of disclosure or zero.', h.Review.REVIEWED),)
                # Even populated rows do not discharge the complete-family requirement.
                gap = missing.unavailable(annual.period, h.Field.CF_WORKING_CAPITAL,
                    'Complete movement perimeter, overlap and statement/acquisition scope remain unestablished.', h.Review.REVIEWED)
                annual = replace(annual, inputs=tuple(v for v in annual.inputs if v.field is not h.Field.CF_WORKING_CAPITAL)
                    + values + ((replace(gap,input_id='retained-cf-movement:coverage-unknown'),) if observations else ()))
            annuals.append(annual)
            rows.append(dict(issuer=name, identity=dict(cik=annual.period.cik, accession=annual.period.accession,
                form=annual.period.form, annual_start=str(annual.period.annual_start), annual_end=str(annual.period.annual_end)),
                instance_receipt=dict(url=evidence.instance.artifact.url, sha256=evidence.instance.artifact.sha256,
                    digest_type=evidence.instance.artifact.digest_type, representation=evidence.instance.artifact.representation,
                    retrieved_at_utc=evidence.instance.retrieved_at_utc,http_status=evidence.instance.http_status,
                    retrieval_mode=evidence.instance.retrieval_mode),
                has_observations=bool(facts), has_populated_rows=any(v.value is not None for v in observations),
                has_reported_total=any(v.value is not None and v.role=='reported_operating_capital_total' for v in observations),
                coverage='PARTIAL_UNKNOWN', original_pilot_preserved=pilot, row_count=len(facts),
                not_observed_concepts=[v.concept for v in RULES if not any(f['concept']==v.concept for f in facts)],
                statement_scope='ORIGINAL_REVIEWED_MAPPING_ONLY' if pilot else 'CONTINUING_VERSUS_CONSOLIDATED_NOT_INDEPENDENTLY_ESTABLISHED',
                acquisition_exclusions='See unchanged original pilot sources/locations; not generalized.' if pilot else 'NOT_ESTABLISHED',
                conflicting_rows=sum(f['status']=='CONFLICTING' for f in facts), observations=facts,
                unsupported_candidates=diagnostics, errors=errors, unresolved_requirements=list(LIMITATIONS)))
        packages[name]=replace(history, history_id='retained-cf-movements:'+name, annuals=tuple(annuals))
        rr=[v for v in rows if v['issuer']==name]
        summaries[name]=dict(periods=len(rr), periods_with_observations=sum(v['has_observations'] for v in rr),
            periods_with_reported_totals=sum(v['has_reported_total'] for v in rr), row_count=sum(v['row_count'] for v in rr),
            conflicting_rows=sum(v['conflicting_rows'] for v in rr))
    ledger=dict(schema='retained-cf-movement-inspection-v1', rule_version=1,
        rules=[dict(asdict(v),possible_children=list(v.possible_children)) for v in RULES],
        selected_periods=len(rows), issuer_count=len(packages), summary=summaries,
        period_outcomes=dict(with_observations=sum(v['has_observations'] for v in rows),
            reported_totals=sum(v['has_reported_total'] for v in rows), partial_unknown=len(rows),
            no_eligible_observations=sum(not v['has_observations'] for v in rows),
            with_conflicting_rows=sum(v['conflicting_rows']>0 for v in rows), with_invalid_evidence=sum(bool(v['errors']) for v in rows)),
        row_counts=dict(observed=sum(sum(f['status']=='OBSERVED' for f in v['observations']) for v in rows),
            conflicting=sum(v['conflicting_rows'] for v in rows), unsupported_diagnostics=sum(len(v['unsupported_candidates']) for v in rows)),
        history_exceptions=baseline['history_exceptions'], income_outcomes=baseline['income_outcomes'],
        cfo_outcomes=baseline['outcomes'], limitations=list(LIMITATIONS), rows=rows)
    return ledger, packages


def validate_history(payload):
    """Independent occurrence/sign replay, not merely structural round-trip."""
    history=h.deserialize(payload)
    from . import pilot_historical_inputs as p
    pilots={a.period:a for name in ('MSFT','AAPL','GOOGL') for a in p.load_history(name).annuals}
    for annual in history.annuals:
        actual=tuple(v for v in annual.inputs if v.field is h.Field.CF_WORKING_CAPITAL)
        if annual.period in pilots:
            if actual!=tuple(v for v in pilots[annual.period].inputs if v.field is h.Field.CF_WORKING_CAPITAL):
                raise h.InputError('Original pilot movement changed')
        else:
            expected=inspect(cfo.prepare(annual))[0]
            if tuple(v for v in actual if v.input_id.startswith('retained-cf-movement:') and v.input_id!='retained-cf-movement:coverage-unknown')!=expected:
                raise h.InputError('Retained movement/sign/occurrence differs')
    return history
