"""Offline, source-pinned reconciliation of the four November 4 workstreams.

Produces review workpapers, never replaces historical facts or valuation inputs.
Run stages in order. Exact fractions avoid dollar-rounding reconciliation plugs.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from valuation_platform.review.operating_fcff import serialized

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/company-resolutions/execution-2026-11-04'


def load(path):
    return json.loads((ROOT / path).read_text())


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def verify_pins():
    baseline = load(OUT.relative_to(ROOT) / 'baseline.json')
    for path, pin in baseline['source_pins'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != pin:
            raise ValueError('Reviewed input changed: ' + path)
    return baseline


def record(stage, output, outcome):
    path = OUT / 'run-log.json'
    rows = json.loads(path.read_text()) if path.exists() else []
    # Replays do not fabricate new implementation events.
    if not any(r['stage'] == stage for r in rows):
        if [r['stage'] for r in rows] != list(range(1, stage)):
            raise ValueError('Workstreams must execute in order')
        rows.append({'stage': stage, 'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
                     'output': output, 'outcome': outcome, 'parent_financial_status': 'OPEN'})
        save('run-log.json', rows)


def apple_operating():
    verify_pins()
    old = load('docs/company-resolutions/AAPL/results.json')
    ledger = load('docs/company-resolutions/AAPL/implementation-2026-11-03/evidence-ledger.json')
    periods = []
    for p, e in zip(old['periods'], ledger['periods'], strict=True):
        c = p['operating_fcff_candidate']
        inputs = {k: F(v['value']) for k, v in c['inputs'].items()}
        terms = e['operating_bridge']['statement_terms']
        value = lambda t: F(t['cash_contribution_usd'])
        one = lambda concept: next(value(t) for t in terms if t['source']['concept'] == concept)
        ni = one('NetIncomeLoss'); da = one('DepreciationDepletionAndAmortization')
        sbc = one('ShareBasedCompensation')
        ebit, pretax, provision, capex, cfo = (inputs[k] for k in
            ('ebit', 'pretax_income', 'tax_provision', 'cash_ppe', 'cfo_control'))
        cash_tax = F(e['tax_review']['cash_paid']['value'])
        assert p['fiscal_year'] == e['fiscal_year']
        assert sum(map(value, terms), F()) == cfo and ni == pretax - provision
        tax_rate = provision / pretax
        nopat = ebit * (1 - tax_rate)
        nonop_after_allocated_tax = (pretax - ebit) * (1 - tax_rate)
        trade = sum((value(t) for t in terms if t['role'] == 'named_trade_movement'), F())
        mixed = sum((value(t) for t in terms if t['role'] == 'mixed_asset_liability_movement'), F())
        # Explicit population: all source reconciliation rows other than NI,
        # D&A, SBC and named trade rows. Do not classify its remainder as WC.
        aggregate_terms = [t for t in terms if t['role'] not in
            ('net_income_control', 'reported_da_or_combined_impairment', 'named_trade_movement')
            and t['source']['concept'] != 'ShareBasedCompensation']
        aggregate = sum(map(value, aggregate_terms), F())
        tax_conversion = provision - cash_tax
        unclassified_after_tax_conversion = aggregate - tax_conversion
        broad_test = nopat + da + trade + mixed - capex
        timing_diagnostic = nopat + da + trade + unclassified_after_tax_conversion - capex
        assert abs(broad_test - F(c['operating_method_test']['result']['amount_usd'])) < F(1, 10**30)
        assert timing_diagnostic + sbc + nonop_after_allocated_tax + tax_conversion == cfo - capex
        periods.append({'fiscal_year': p['fiscal_year'], 'identity': e['identity'],
            'source_urls': e['source_urls'],
            'filing_operands_usd': {**{k: str(v) for k, v in inputs.items()},
                'net_income': str(ni), 'cash_tax_paid_net': str(cash_tax),
                'cash_statement_da': str(da), 'sbc': str(sbc)},
            'nopat_reported_etr_convention': serialized(nopat),
            'trade_cash_contribution': serialized(trade), 'mixed_cash_contribution': serialized(mixed),
            'aggregate_unclassified_population': [{'concept': t['source']['concept'],
                'contribution_usd': t['cash_contribution_usd'],
                'source_pointer': 'docs/company-resolutions/AAPL/implementation-2026-11-03/evidence-ledger.json#/periods/' + str(len(periods)) +
                    '/operating_bridge/statement_terms/' + str(terms.index(t))} for t in aggregate_terms],
            'aggregate_before_tax_conversion': serialized(aggregate),
            'provision_minus_cash_tax': serialized(tax_conversion),
            'aggregate_after_tax_conversion_UNCLASSIFIED': serialized(unclassified_after_tax_conversion),
            'broad_statement_movement_diagnostic_NOT_FCFF': serialized(broad_test),
            'tax_timing_diagnostic_NOT_FCFF': serialized(timing_diagnostic),
            'net_nonoperating_after_allocated_tax': serialized(nonop_after_allocated_tax),
            'reported_cfo_less_cash_ppe': serialized(cfo - capex),
            'bridge_difference_usd': '0', 'balancing_plug_used': False,
            'verified_operating_fcff_usd': None, 'eligible_for_forecast_calibration': False,
            'remaining_issues': ['A4', 'A5', 'A6'],
            'da_comparative_check': e['new_comparative_support']['note_sum_minus_cash_statement_da']
                if e['new_comparative_support'] else None})
    result = {'schema_version': 'apple-operating-reconciliation-v1', 'ticker': 'AAPL',
        'periods': periods, 'arithmetic_verdict': 'PASS_FIVE_EXACT_RECONCILIATIONS',
        'financial_verdict': 'NOT_CLEARED_AS_OPERATING_FCFF', 'numerical_adoption': False,
        'interpretation': 'Provision minus cash taxes is an observable consolidated conversion. '
            'Removing it from the entire aggregate is an algebraic decomposition, not proof '
            'of which mixed caption contains tax or that the remaining amount is operating WC. '
            'D&A and cash PP&E keep their reported populations. No alternative is spliced into history.',
        'bridge_formula': 'cash FCF = tax-timing diagnostic + SBC + net nonoperating after allocated tax + provision minus cash taxes'}
    save('step-1-apple-operating.json', result)
    record(1, 'step-1-apple-operating.json', 'Five exact numeric bridges; no certified replacement or new historical value')
    return result


def financing_review():
    verify_pins()
    if not (OUT / 'step-1-apple-operating.json').exists():
        raise ValueError('First reconcile Apple operating inputs')
    projection = load('docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json')
    companies = {}
    for ticker in ('AAPL', 'META'):
        original = load('docs/company-resolutions/' + ticker + '/results.json')
        periods = []
        for p, live in zip(original['periods'], projection['companies'][ticker]['periods'], strict=True):
            rows = p['financing_source_rows'] if ticker == 'AAPL' else p['financing']['source_rows']
            total = [r for r in rows if r['classification'] == 'FINANCING_TOTAL']
            components = [r for r in rows if r['classification'] != 'FINANCING_TOTAL']
            unknown = [r for r in rows if r['classification'] == 'OTHER_FINANCING_EXCLUDED']
            assert len(total) == len(unknown) == 1
            assert sum((F(r['signed_cash_usd']) for r in components), F()) == F(total[0]['signed_cash_usd'])
            net = sum((F(r['signed_cash_usd']) for r in components if r['included_in_net_borrowing']), F())
            assert net == F(live['identified_net_borrowing_usd'])
            assert F(live['reported_cash_fcf_usd']) + net == F(live['fcfe']['amount_usd'])
            periods.append({'fiscal_year': p['fiscal_year'], 'identity': p['identity'],
                'source_urls': live['fcfe']['source_urls'],
                'cash_fcf_usd': live['reported_cash_fcf_usd'],
                'identified_net_borrowing_usd': str(net),
                'provisional_fcfe_usd': live['fcfe']['amount_usd'],
                'other_financing_net_usd': unknown[0]['signed_cash_usd'],
                'debt_content_of_other_usd': None, 'other_net_is_uncertainty_bound': False,
                'complete_fcfe_usd': None, 'source_row_sum_difference_usd': '0',
                'unknown_assumed_zero': False,
                'identified_debt_rows': [{'caption': r['caption'], 'signed_cash_usd': r['signed_cash_usd'],
                    'concept': r['concept'], 'context_id': r['context_id']} for r in components if r['included_in_net_borrowing']],
                'principal_containment': 'NOT_ESTABLISHED' if ticker == 'AAPL' else 'IDENTIFIED_FINANCE_LEASE_PRINCIPAL_DEDUCTED_ONCE',
                'remaining_blockers': ['A2', 'A3'] if ticker == 'AAPL' else ['M1']})
        questions = ([
            'Provide annual USGAAP gross expensed interest for FY2024 and FY2025, or a public reconciliation to those exact amounts.',
            'For each FY2021–25, split Other financing into actual debt proceeds, debt/finance-lease principal, equity, derivatives and other cash. Identify the filing caption and any netting.',
            'Identify actual annual finance-lease principal and whether it is contained in term-debt repayments, Other financing, or another caption. Reconcile any additions, interest, FX and modifications separately from cash.',
            'Explain which amortization/expense populations are inside cash-statement D&A versus the later depreciation/intangible notes; identify tax and noncurrent cash components within mixed operating movements.'
        ] if ticker == 'AAPL' else [
            'For each FY2021–25, split Other financing into actual debt/overdraft/cash-pool cash, equity and other components, including the cash-pool termination in FY2022.',
            'Reconcile FY2025 Other financing +2.220B into its full annual cash components; the Q4 net increment alone does not classify debt.',
            'Identify actual paid capitalized interest and cash PP&E containment for FY2024/25, separately from incurred capitalization and interest paid net of capitalized amounts.'
        ])
        companies[ticker] = {'periods': periods, 'arithmetic': 'PASS_FIVE_STATEMENT_AND_FCFE_SUMS',
            'financial_status': 'PROVISIONAL_FINANCING_SCOPE_UNRESOLVED',
            'clarification_request': {'status': 'DRAFT_NOT_SENT', 'requested_years': list(range(2021, 2026)),
                'public_or_disclosable_information_only': True, 'questions': questions,
                'requested_response_columns': ['fiscal_year', 'transaction_component', 'cash_amount_usd',
                    'cash_statement_caption', 'gross_or_net', 'included_in_existing_debt_parent', 'public_source_url']}}
    result = {'schema_version': 'pilot-financing-review-v1', 'companies': companies,
        'company_reviews': 'OPEN', 'outgoing_messages_sent': 0, 'new_verified_fcfe_cells': 0,
        'interpretation': 'The full financing statements tie, but a net Other row can conceal offsetting debt and non-debt flows. '
            'Its magnitude is not a bound on the omitted borrowing component. No default-zero or materiality waiver is applied.'}
    save('step-2-financing.json', result)
    record(2, 'step-2-financing.json', 'Ten provisional calculations reconciled; precise issuer requests prepared, not sent')
    return result


def alphabet_ownership():
    verify_pins()
    if not (OUT / 'step-2-financing.json').exists():
        raise ValueError('First finish the financing reconciliation')
    path = 'docs/company-resolutions/GOOGL/implementation-2026-11-03/schedules.json'
    schedule = load(path)
    original = load('docs/company-resolutions/GOOGL/results.json')
    projection = load('docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json')['companies']['GOOGL']
    periods = []
    for p, s, live in zip(original['periods'], schedule['periods'], projection['periods'], strict=True):
        assert p['fiscal_year'] == s['fiscal_year'] == live['fiscal_year']
        cfo = F(live['reported_cash_fcf_usd'])
        net = F(p['financing']['net_borrowing']['amount_usd'])
        assert cfo + net == F(live['fcfe']['amount_usd'])
        own = s['ownership_schedule']; lease = s['lease_schedule']
        assert own['nci_fair_value_usd'] is None and own['nci_cash_allocation_usd'] is None
        assert own['book_nci_used_as_fair_value'] is False
        assert lease['financing_cash_contained_in_debt_repayments'] is True
        assert F(lease['additional_cash_deduction_usd']) == 0
        periods.append({'fiscal_year': p['fiscal_year'], 'annual_end': live['annual_end'],
            'source_urls': live['fcfe']['source_urls'],
            'consolidated_fcfe_usd': live['fcfe']['amount_usd'],
            'available_under_declared_consolidated_convention': True,
            'parent_common_fcfe_usd': None, 'exact_parent_cash_attribution_available': False,
            'outside_equity_cash_NOT_DEBT_usd': own['outside_capital_cash_usd'],
            'book_nci_context_only_usd': own['book_nci_usd_rounded'],
            'redeemable_nci_ALREADY_INCLUDED_usd': own['book_rnci_usd_rounded_included_in_nci'],
            'nci_fair_value_usd': None,
            'parent_value_bridge': {'valuation_date': live['annual_end'],
                'consolidated_value_usd': None, 'eligible_nonoperating_assets_usd': None,
                'financing_claims_usd': None, 'nci_fair_value_usd': None,
                'other_claims_usd': None, 'parent_common_value_usd': None,
                'status': 'NOT_POPULATED_NO_VALUE_INFERRED',
                'scope_rule': 'FCFF route deducts matching debt/claims. FCFE route does not deduct debt already captured in financing. '
                    'Add only eligible assets whose returns are excluded from cash flows; deduct outside interests only once.'},
            'lease_cash_counted_once': True, 'economic_investment_timing_bridge_open': True,
            'numerical_change_usd': '0'})
    result = {'schema_version': 'alphabet-ownership-separation-v1', 'ticker': 'GOOGL',
        'input_schedule': path, 'input_sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
        'periods': periods, 'new_parent_common_amounts': 0,
        'consolidated_history_available': 5, 'parent_status': 'OPEN',
        'treatment': 'Display consolidated cash history with ownership label while separately requiring a dated NCI/claims bridge for parent value. '
            'A value bridge does not manufacture annual parent cash attribution. No 2026 round is backdated; no book NCI is treated as fair value.'}
    save('step-3-alphabet-ownership.json', result)
    record(3, 'step-3-alphabet-ownership.json', 'Five consolidated FCFE observations kept available; parent cash/value remain separately gated')
    return result


def platform_separation():
    verify_pins()
    if not (OUT / 'step-3-alphabet-ownership.json').exists():
        raise ValueError('First finish the ownership reconciliation')
    from valuation_platform.review.pilot_cashflows import read_cashflows, RESOURCE
    old = load(RESOURCE)
    companies = {t: read_cashflows(ROOT, t) for t in ('AAPL', 'META', 'GOOGL')}
    for t, current in companies.items():
        assert {k: v for k, v in current.items() if k != 'readiness'} == old['companies'][t]
    counts = {k: sum(c['readiness']['counts'][k] for c in companies.values())
              for k in companies['AAPL']['readiness']['counts']}
    assert counts == {'available_stated_convention': 18, 'provisional_financing': 10,
                     'missing_required_input': 2, 'parent_common_fcfe_available': 0}
    strict_failed_cells = sum(p['fcff']['amount_usd'] is None for c in companies.values() for p in c['periods'])
    strict_failed_cells += sum(p['fcfe']['parent_common_amount_usd'] is None for c in companies.values() for p in c['periods'])
    assert strict_failed_cells == 17
    result = {'schema_version': 'cashflow-platform-separation-v1',
        'counts': counts, 'prior_strict_parent_common_failed_cells': strict_failed_cells,
        'prior_projection_sha256': hashlib.sha256((ROOT / RESOURCE).read_bytes()).hexdigest(),
        'new_measurements': 0, 'changed_amounts': 0,
        'manual_forecast_disabled_by_historical_gaps': False,
        'company_financial_reviews': 'OPEN',
        'companies': {t: c['readiness'] for t, c in companies.items()},
        'validation_scope': 'Additive runtime contract; full source, API, frontend and independent checks logged separately.'}
    save('step-4-platform-separation.json', result)
    record(4, 'step-4-platform-separation.json', 'Runtime/UI readiness separated; old 17 strict failures preserved, no financial amount changed')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=int, choices=(1, 2, 3, 4), required=True)
    args = parser.parse_args()
    if args.stage == 1:
        apple_operating()
        print('Step 1: five exact Apple reconciliations; verified operating FCFF remains unavailable.')
    elif args.stage == 2:
        financing_review()
        print('Step 2: ten financing/FCFE reconciliations; clarification drafts prepared, none sent.')
    elif args.stage == 3:
        alphabet_ownership()
        print('Step 3: five consolidated Alphabet amounts reconciled; parent attribution and value remain null.')
    else:
        platform_separation()
        print('Step 4: 18 available, 10 provisional, 2 missing; old strict gate still has 17 failures.')
