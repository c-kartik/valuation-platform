"""Replay approved Apple historical tax policy and first-forecast basis bridge.
Read-only against runtime, source packages and policies; writes only this workpaper.
"""
import argparse
from copy import copy
from datetime import date, timedelta
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'src')]
from calculate_historical_fcff_from_filings import RetainedFiling
from reconcile_historical_fcff_adjustments import exact
from valuation_platform.review.apple_operating_history import calculate, working_capital
from valuation_platform.review.operating_fcff import amount, serialized
from valuation_platform.preload.generate import generate, engine_request
from valuation_platform.valuation.case_inputs import read_case, run_case

INPUTS = [
    'docs/company-resolutions/AAPL/remaining-issues-2026-11-04/approval.json',
    'docs/company-data-preparation/aapl-analyst-input-package.json',
    'docs/company-resolutions/AAPL/implementation-2026-11-03/evidence-ledger.json',
    'docs/company-resolutions/AAPL/operating-fcff-2026-11-04/adopted-history.json',
    'docs/company-resolutions/AAPL/operating-fcff-2026-11-04/source-ledger.json',
    'data/preload/aapl-v1/policy.json',
]
TAX_CONCEPTS = {
    'provision': 'IncomeTaxExpenseBenefit',
    'pretax_income': 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
    'cash_taxes_paid': 'IncomeTaxesPaidNet',
    'current_federal': 'CurrentFederalTaxExpenseBenefit',
    'current_state': 'CurrentStateAndLocalTaxExpenseBenefit',
    'current_foreign': 'CurrentForeignTaxExpenseBenefit',
    'deferred_federal': 'DeferredFederalIncomeTaxExpenseBenefit',
    'deferred_state': 'DeferredStateAndLocalIncomeTaxExpenseBenefit',
    'deferred_foreign': 'DeferredForeignIncomeTaxExpenseBenefit',
}


def money(value):
    return serialized(value)['amount_usd']


def diagnostic_tax_exclusion(inputs, opening_tax, closing_tax):
    """Diagnostic only: unavailable opening/closing tax must never become zero."""
    if opening_tax is None or closing_tax is None:
        return None
    return amount(calculate(inputs)['amount_usd']) - amount(closing_tax) + amount(opening_tax)


def reconcile_bridge(historical, forecast):
    """Signed operand differences; engine serialization residue is not a cash plug."""
    signs = {'ebit': 1, 'tax': -1, 'd_and_a': 1, 'investment': -1,
             'working_capital_cash_requirement': -1}
    components = {key: signs[key] * (amount(forecast[key]) - historical[key])
                  for key in signs}
    hist_fcff = sum(signs[key] * historical[key] for key in signs)
    target = amount(forecast['fcff'])
    residue = target - hist_fcff - sum(components.values())
    if abs(residue) > Fraction('1e-30'):
        raise ValueError('First-forecast bridge exceeds engine precision envelope')
    return {'historical_fcff_usd': money(hist_fcff),
            'forecast_fcff_usd': money(target),
            'signed_components_usd': {key: money(value) for key, value in components.items()},
            'sum_signed_components_usd': money(sum(components.values())),
            'fcff_change_usd': money(target - hist_fcff),
            'serialization_residual_usd': money(residue),
            'serialization_residual_is_cash_adjustment': False,
            'identity_pass': True}


def build():
    source = {path: json.loads((ROOT / path).read_text()) for path in INPUTS}
    hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in INPUTS}
    approval = source[INPUTS[0]]
    assert any('all-year tax-inclusive' in text for text in approval['approved_treatments'])
    assert approval['parent_company_status'] == 'OPEN'
    originals = source[INPUTS[1]]['aapl_history_review']['periods']
    prior = source[INPUTS[2]]['periods']
    adopted = source[INPUTS[3]]['periods']
    ledger = source[INPUTS[4]]['periods']
    tax_by_date = {}
    for p in ledger:
        fact = p['separately_disclosed_current_tax_diagnostic']
        if fact is not None:
            source_row = next(row for row in originals if row['identity'] == fact['source_identity'])
            tax_filing = RetainedFiling(ROOT, source_row, {})
            view = copy(tax_filing); view.facts = {}
            view.fact('tax', fact['concept'], 'Exact dated current-tax balance', namespace=fact['namespace'], instant=True, as_of=p['identity']['annual_end'])
            assert view.facts['tax']['value'] == fact['value']
            assert view.facts['tax']['as_of'] == p['identity']['annual_end']
        tax_by_date[p['identity']['annual_end']] = fact
    first_start = originals[0]['identity']['annual_start']
    tax_by_date[str(date.fromisoformat(first_start) - timedelta(days=1))] = None
    output, final_filing = [], None
    for row, previous, active, old_ledger in zip(originals, prior, adopted, ledger, strict=True):
        identity = row['identity']; year = int(identity['annual_end'][:4])
        assert year == previous['fiscal_year'] == active['fiscal_year'] == old_ledger['fiscal_year']
        filing = RetainedFiling(ROOT, row, {})
        facts = {key: exact(filing, identity, concept) for key, concept in TAX_CONCEPTS.items()}
        reviewed = previous['tax_review']
        assert amount(facts['cash_taxes_paid']['value']) == amount(reviewed['cash_paid']['value'])
        assert amount(facts['provision']['value']) == amount(active['inputs']['tax_provision'])
        assert amount(facts['pretax_income']['value']) == amount(active['inputs']['pretax_income'])
        for key in ('current', 'deferred'):
            bound = [facts[f'{key}_{jurisdiction}'] for jurisdiction in ('federal', 'state', 'foreign')]
            assert [p['value'] for p in bound] == [p['value'] for p in reviewed[f'{key}_components']]
        current = sum(amount(facts[f'current_{j}']['value']) for j in ('federal', 'state', 'foreign'))
        deferred = sum(amount(facts[f'deferred_{j}']['value']) for j in ('federal', 'state', 'foreign'))
        assert current + deferred == amount(facts['provision']['value'])
        state = reviewed['state_aid_item']
        if state is not None:
            state_bound = exact(filing, identity, state['concept'], namespace=state['namespace'])
            assert state_bound['value'] == state['value']
        else:
            state_bound = None
        end = identity['annual_end']; opening = str(date.fromisoformat(identity['annual_start']) - timedelta(days=1))
        opening_fact = tax_by_date.get(opening); closing_fact = tax_by_date[end]
        opening_tax = None if opening_fact is None else opening_fact['value']
        closing_tax = None if closing_fact is None else closing_fact['value']
        change_tax = None if opening_tax is None or closing_tax is None else amount(closing_tax) - amount(opening_tax)
        assert amount(active['inputs']['opening_nwc']) == working_capital(active['opening_balances'])
        assert amount(active['inputs']['closing_nwc']) == working_capital(active['closing_balances'])
        assert calculate(active['inputs']) == active['fcff']
        output.append({'fiscal_year': year, 'identity': identity, 'tax_facts': facts,
            'current_provision_usd': money(current), 'deferred_provision_usd': money(deferred),
            'provision_component_difference_usd': '0',
            'state_aid_accounting_reconciliation_item': state_bound,
            'reported_effective_rate': serialized(amount(facts['provision']['value']) / amount(facts['pretax_income']['value'])),
            'operating_cash_tax_allocation_usd': None,
            'cash_taxes_restatement_usd': '0', 'additional_cash_tax_fcff_adjustment_usd': '0',
            'nwc': {'opening_date': opening, 'closing_date': end,
                'opening_current_tax_fact': opening_fact, 'closing_current_tax_fact': closing_fact,
                'current_tax_balance_change_usd': None if change_tax is None else money(change_tax),
                'tax_inclusive_fcff_effect_vs_tax_excluded_usd': None if change_tax is None else money(change_tax),
                'tax_excluded_fcff_diagnostic_usd': None if change_tax is None else money(diagnostic_tax_exclusion(active['inputs'], opening_tax, closing_tax)),
                'diagnostic_adopted': False, 'unknown_tax_means_zero': False},
            'adopted_fcff_usd': active['fcff']['amount_usd'],
            'historical_runtime_change_usd': '0'})
        final_filing = filing
    text = ' '.join(' '.join(ET.fromstring(final_filing.primary.artifact.body).itertext()).split())
    excerpts = []
    for label, marker, length in [
        ('state_aid_charge_and_escrow', 'As a result, during the fourth quarter of 2024 the Company recorded a one-time income tax charge', 430),
        ('restricted_cash', 'As of September 28, 2024, cash and cash equivalents included', 300),
        ('restricted_current_securities', 'As of September 28, 2024, current marketable securities included', 300),
    ]:
        assert text.count(marker) == 1
        start = text.index(marker)
        excerpts.append({'label': label, 'source_url': final_filing.primary.artifact.url,
            'source_sha256': final_filing.primary.artifact.sha256,
            'locator': 'Unique normalized-text marker: ' + marker, 'text': text[start:start + length]})
    profile = generate(ROOT, ticker='AAPL', generated_at='2026-11-04T00:00:00+00:00')
    cfg = profile['economic']['configuration']
    assert (cfg['tax_start'], cfg['tax_endpoint'], cfg['terminal_tax'], cfg['incremental_wc']) == ('0.18', '0.20', '0.20', '0.05')
    hist = adopted[-1]; inp = {key: amount(value) for key, value in hist['inputs'].items()}
    hist_components = {'ebit': inp['ebit'], 'tax': inp['ebit'] * inp['tax_provision'] / inp['pretax_income'],
        'd_and_a': inp['da'], 'investment': inp['cash_ppe'],
        'working_capital_cash_requirement': inp['closing_nwc'] - inp['opening_nwc']}
    bridges = []
    for scenario in ('Base', 'Bear', 'Bull'):
        request = engine_request(profile, scenario, 'perpetual_growth')
        response = run_case(read_case(json.dumps(request)), ROOT)
        annual_tax = [p['forecast_tax_rate'] for p in request['forecast_years']]
        assert annual_tax == ['0.18', '0.185', '0.19', '0.195', '0.20']
        assert request['terminal_valuation']['terminal']['operating_tax_rate'] == '0.20'
        first = response['stage_b']['stage_a']['years'][0]
        actual_wc = amount(first['working_capital_cash_requirement'])
        revenue_increase = amount(first['revenue']) - amount(response['stage_b']['stage_a']['anchor']['revenue'])
        assert abs(actual_wc - amount(request['forecast_years'][0]['change_in_operating_nwc_percent_revenue']) * amount(first['revenue'])) < Fraction('1e-30')
        if scenario == 'Base':
            assert abs(actual_wc - amount(cfg['incremental_wc']) * revenue_increase) < Fraction('1e-30')
        bridges.append({'scenario': scenario, 'historical_start': hist['identity']['annual_start'],
            'historical_end': hist['identity']['annual_end'], 'first_forecast_label': first['fiscal_year_label'],
            'anchor_identity': request['anchor'], 'first_forecast_components': first,
            'annual_forecast_tax_rates': annual_tax, 'terminal_tax_rate': '0.20',
            'forecast_working_capital_driver': ('Base ratio derived from5% incremental sales' if scenario == 'Base' else 'Existing scenario policy inherits Base WC/revenue ratio; not a separately recomputed5% of scenario incremental sales'),
            'first_year_implied_incremental_sales_coefficient': serialized(actual_wc / revenue_increase),
            'forecast_request_sha256': hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest(),
            'enterprise_value_usd': response['stage_b']['enterprise_value'],
            'algebraic_component_bridge': reconcile_bridge(hist_components, first)})
    assert hashes == {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in INPUTS}
    return {'schema_version': 'apple-approved-tax-nwc-basis-bridge-v1', 'date': '2026-11-04',
        'company_status': 'OPEN', 'tax_policy_treatment_status': 'IMPLEMENTED_USER_APPROVED_CONVENTION',
        'approval_reference': INPUTS[0], 'source_replay_status': 'PASS',
        'source_input_sha256': hashes, 'historical_periods': output, 'source_excerpts': excerpts,
        'historical_policy': 'Uniform tax-inclusive noncash/non-debt current-balance NWC; current leases excluded; mixed Other retained by aggregate convention.',
        'exact_operating_cash_tax_status': 'UNRESOLVED_NOT_INFERRED',
        'historical_runtime_changed': False, 'forward_policy_changed': False,
        'forward_policy': {'configuration': cfg, 'economic_hash': profile['economic_hash'],
            'tax_policy_is_analyst_assumption': True, 'automatic_history_calibration': False},
        'forecast_bridges': bridges, 'cross_basis_cagr_enabled': False,
        'limitations': [
            'Component bridge is an exact algebraic comparison within engine serialization precision, not a source-supported economic attribution of the forecast change.',
            'FY2025 actual reporting population and FY2026 model assumptions differ in date, business size, tax policy, D&A/investment population and working-capital definition.',
            'Current tax balances include State Aid and other tax effects; do not assign the entire balance movement to State Aid.',
            'Provision, current/deferred accounting expense, cash taxes and payable/escrow movements are different populations. No exact operating cash-tax allocation is disclosed or invented.',
            'Tax-inclusive NWC and provision-based EBIT allocation is a standardized approved convention, not proof of exact unlevered cash FCFF.',
            'Forecast18% to20%, terminal20% and Base5% incremental-sales cash coefficient remain analyst assumptions, not sustainable rates reported in filings. Bear/Bull retain the generated Base WC/revenue ratios; their implied incremental-sales coefficients differ. No policy change is silently introduced.',
            'Retained later-filed July2026 information supports estimates; the2025-09-27 analytical origin is not a current-date fair value or contemporaneous backtest.',
        ]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    result = build(); rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.check:
        if (HERE / 'results.json').read_text() != rendered:
            raise ValueError('Tax workpaper replay differs')
    else:
        (HERE / 'results.json').write_text(rendered)
    print('PASS: five tax schedules and three first-forecast bridges; no runtime or policy changes.')
