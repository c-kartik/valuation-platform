"""Reproduce Meta's approved analyst source projection; never mutate source facts.

Run with PYTHONPATH=src .venv/bin/python scripts/build_meta_analyst_policy.py
[--check]. The replay verifies original primary/instance facts and five complete
financing statements before projecting the versioned analyst assumptions.
"""
import argparse
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path

from calculate_historical_fcff_from_filings import RetainedFiling
from resolve_meta_alphabet_cashflows import build_company

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/company-resolutions/META/analyst-ready-2026-11-04'
FILES = {
    'historical': 'docs/company-resolutions/META/results.json',
    'adopted': 'docs/company-resolutions/META/adopted-history.json',
    'shares': 'docs/company-resolutions/implementation-2026-11-03/share-bridge/source-schedules.json',
    'basis': 'docs/company-resolutions/implementation-2026-11-03/basis-bridge/schedules.json',
    'package': 'docs/company-data-preparation/meta-analyst-input-package.json',
    'preload': 'data/preload/meta-v1/policy.json',
    'observations': 'data/preload/meta-v1/observations.json',
    'source_manifest': 'data/preload/meta-v1/sources/manifest.json',
    'source_map': 'docs/company-resolutions/META/source-map.json',
    'decisions': 'docs/company-resolutions/META/decisions.json',
}


def build():
    data = {k: json.loads((ROOT / f).read_text()) for k, f in FILES.items()}
    replay = build_company('META')
    if replay != data['historical']:
        raise ValueError('Meta source-bound financing/history replay differs')
    # Rebind every selected share-bridge point to retained original filing bytes.
    spec = importlib.util.spec_from_file_location(
        'meta_share_source_replay', ROOT / 'docs/company-resolutions/implementation-2026-11-03/share-bridge/build.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    share = next(c for c in data['shares']['companies'] if c['ticker'] == 'META')
    filings = [RetainedFiling(ROOT, r, {}) for r in data['package']['periods']]
    points = module.verified_points(filings[-1], '2025-12-31')
    if points != share['source_points']:
        raise ValueError('Meta current balance/share source observations differ')

    def selected(concept, member=None):
        matches = [p for p in points if p['concept'] == concept
                   and p['scope']['end'] == '2025-12-31'
                   and (not p['scope']['dimensions'] if member is None else
                        any(d['member'].endswith('#' + member) for d in p['scope']['dimensions']))]
        if not matches or len({p['value'] for p in matches}) != 1:
            raise ValueError('Missing or competing Meta selection: ' + concept)
        return matches[0]

    facts = {key: selected(concept, member) for key, concept, member in (
        ('cash', 'CashAndCashEquivalentsAtCarryingValue', None),
        ('marketable_securities', 'MarketableSecuritiesCurrent', None),
        ('term_debt_carrying', 'LongTermDebtNoncurrent', None),
        ('term_debt_face', 'DebtInstrumentCarryingAmount', None),
        ('term_debt_fair_value', 'LongTermDebtFairValue', 'SeniorNotesMember'),
        ('finance_lease', 'FinanceLeaseLiability', None),
        ('finance_lease_current', 'FinanceLeaseLiabilityCurrent', None),
        ('finance_lease_noncurrent', 'FinanceLeaseLiabilityNoncurrent', None),
        ('dated_common_shares', 'CommonStockSharesOutstanding', 'CommonStockMember'),
        ('class_a_shares', 'CommonStockSharesOutstanding', 'CommonClassAMember'),
        ('class_b_shares', 'CommonStockSharesOutstanding', 'CommonClassBMember'),
        ('unvested_rsus', 'ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber', 'RestrictedStockUnitsRSUMember'),
        ('unrecognized_award_cost', 'EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized', None),
        ('restricted_cash_current', 'RestrictedCashAndCashEquivalentsAtCarryingValue', None),
        ('restricted_cash_noncurrent', 'RestrictedCashAndCashEquivalentsNoncurrent', None),
        ('nonmarketable_equity', 'NonmarketableEquitySecuritiesCarryingValue', None),
        ('equity_method_investments', 'EquityMethodInvestments', None),
        ('legal_accrual', 'LegalRelatedAccruedLiabilitiesCurrent', None),
        ('unrecognized_tax_benefits', 'UnrecognizedTaxBenefits', None),
    )}
    amount = lambda key: Decimal(facts[key]['value'])
    assert amount('finance_lease') == amount('finance_lease_current') + amount('finance_lease_noncurrent')
    assert amount('dated_common_shares') == amount('class_a_shares') + amount('class_b_shares')
    anchor = {
        'gross_cash_usd': str(amount('cash') + amount('marketable_securities')),
        'financing_debt_carrying_usd': str(amount('term_debt_carrying') + amount('finance_lease')),
        'financing_debt_fair_proxy_usd': str(amount('term_debt_fair_value') + amount('finance_lease')),
        'dated_common_shares': str(amount('dated_common_shares')),
        'unvested_rsus': str(amount('unvested_rsus')),
        'nonoperating_investments_carrying_usd': str(amount('nonmarketable_equity')),
    }
    history = []
    for p, adopted, filing in zip(data['historical']['periods'], data['adopted']['periods'], filings, strict=True):
        assert p['identity'] == adopted['identity'] == filing.source_identity
        identity = p['identity']
        cfo = filing.extract('NetCashProvidedByUsedInOperatingActivities', identity)
        sbc = filing.extract('ShareBasedCompensation', identity)
        cash_ppe = filing.extract('PaymentsToAcquirePropertyPlantAndEquipment', identity)
        assert cfo['value'] == p['inputs']['cfo']
        assert cash_ppe['value'] == adopted['original_cash_ppe_usd']
        assert Decimal(cash_ppe['value']) - Decimal(adopted['identified_receipts_usd']) == Decimal(p['inputs']['cash_ppe'])
        basis = next(r for r in data['basis']['periods'] if r['ticker'] == 'META' and r['identity'] == identity)
        assert sbc['value'] == basis['reported_sbc_addback']['amount_usd']
        assert p['fcff']['amount_usd'] == adopted['fcff_usd']
        assert len(p['financing']['unallocated_other_usd']) == 1
        history.append({
            'fiscal_year': p['fiscal_year'], 'identity': identity,
            'cfo_usd': cfo['value'], 'cash_ppe_usd': p['inputs']['cash_ppe'],
            'identified_net_borrowing_usd': p['financing']['net_borrowing']['amount_usd'],
            'other_financing_usd': p['financing']['unallocated_other_usd'][0],
            'sbc_usd': sbc['value'], 'fcff_usd': p['fcff']['amount_usd'],
            'source_urls': sorted({s['url'] for s in filing.references}),
            'cfo_source': cfo, 'sbc_source': sbc, 'gross_cash_ppe_source': cash_ppe,
            'identified_ppe_receipts_usd': adopted['identified_receipts_usd'],
            'identified_ppe_receipt_sources': p['investment_receipt_sources'],
            'financing_sources': p['financing']['source_rows'],
            'historical_source_reference': FILES['historical'] + '#/periods/' + str(len(history)),
            'fcff_methodology': p['fcff'],
        })
    config = data['preload']['configuration']
    macro = {o['key']: o for o in data['observations'] if o['key'] in ('treasury_10y', 'implied_erp')}
    macro_sources = [s for s in data['source_manifest']['sources'] if s['id'] in {o['source'] for o in macro.values()}]
    for source in macro_sources:
        body = ROOT / 'data/preload/meta-v1/sources' / source['file']
        if hashlib.sha256(body.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('Meta discount-source body digest differs')
    rf = Decimal(macro['treasury_10y']['value']); erp = Decimal(macro['implied_erp']['value'])
    ke = rf + Decimal(config['beta']) * erp; kd = rf + Decimal(config['credit_spread'])
    wacc = ke * Decimal(config['equity_weight']) + kd * (1 - Decimal(config['debt_tax_shield'])) * Decimal(config['debt_weight'])
    rights = ('The holders of our Class A and Class B common stock (together, "common stock") '
              'have identical liquidation and dividend rights but different voting rights.')
    if rights not in filings[-1].text:
        raise ValueError('Meta equal cash-flow rights sentence missing from retained source')
    note5 = ('Non-marketable equity investments under measurement alternative 20,076 6,018 '
             'Non-marketable equity investments under equity method 7,448 52 '
             'Total carrying value of non-marketable equity investments $ 27,524 $ 6,070')
    unconsolidated = ('We do not have the power to direct the activities that most significantly impact '
                      "the Venture's economic performance. Therefore, we are not the primary beneficiary "
                      'and do not consolidate the variable interest entity (VIE).')
    guarantee = 'As of December 31, 2025, RVG payments are not probable and therefore, no liability has been recorded.'
    if any(s not in filings[-1].text for s in (note5, unconsolidated, guarantee)):
        raise ValueError('Meta nonmarketable investment scope/guarantee source changed')
    assert amount('nonmarketable_equity') == Decimal('20076000000') + amount('equity_method_investments')
    return {
        'schema_version': 'company-analyst-policy-v1', 'version': 'meta-analyst-2026-11-04-v1',
        'ticker': 'META', 'name': 'Meta Platforms', 'cik': 1326801, 'anchor_date': '2025-12-31',
        'approval': 'User: complete the five outputs for both Meta and Alphabet to the approved Apple analyst-readiness level, with reasonable disclosed assumptions.',
        'anchor_support': anchor,
        'defaults': {'operating_cash_reserve_ratio': '0.02', 'cost_of_equity': str(ke),
                     'pre_tax_cost_of_debt': str(kd), 'rsu_vesting_fraction': '1',
                     'additional_claims_usd': '0', 'historical_other_financing_fraction': '0',
                     'nci_claim_usd': '0', 'historical_minority_cash_share': '0',
                     'additional_assets_usd': str(amount('nonmarketable_equity'))},
        'financed_fraction_cash_ppe': config['new_financed_fraction_cash_ppe'],
        'discount_basis': {'risk_free': str(rf), 'beta': config['beta'], 'equity_risk_premium': str(erp),
                           'target_equity_weight': config['equity_weight'], 'target_debt_weight': config['debt_weight'],
                           'debt_tax_shield': config['debt_tax_shield'], 'saved_base_wacc': str(wacc),
                           'macro_observations': macro,
                           'macro_sources': macro_sources,
                           'classification': 'DATED_MACRO_OBSERVATIONS_AND_CONFIGURED_ANALYST_ASSUMPTIONS'},
        'class_treatment': {'classification': 'ANALYST_ASSUMPTION_SUPPORTED_BY_REPORTED_RIGHTS',
                            'treatment': 'Equal per-share economic claim across A/B; no control premium or voting-equivalence claim.',
                            'reported_excerpt': rights, 'text_offset': filings[-1].text.index(rights),
                            'sources': filings[-1].references},
        'nci_valuation': {'classification': 'ANALYST_ASSUMPTION_NOT_REPORTED_ZERO',
                          'amount_usd': '0', 'treatment': 'No separate unmodeled minority-interest claim in this analytical perimeter; alternative claims use the editable additional-claims adjustment.'},
        'nonoperating_investments': {
            'classification': 'ANALYST_CARRYING_VALUE_PROXY_NOT_REPORTED_FAIR_VALUE',
            'amount_usd': str(amount('nonmarketable_equity')),
            'equity_method_component_usd': str(amount('equity_method_investments')),
            'measurement_alternative_component_usd': '20076000000',
            'treatment': 'Add the 27.524bn total once outside the consolidated EBIT forecast. Equity-method 7.448bn is INCLUDED, not additive; no 34.972bn subtotal. Carrying value is a proxy subject to editable zero/half-value stress, restrictions, liquidity and investee risk.',
            'reported_excerpts': [{'text': s, 'text_offset': filings[-1].text.index(s), 'sources': filings[-1].references}
                                  for s in (note5, unconsolidated, guarantee)],
            'venture_risk': '20% Louisiana venture includes future funding, leases and contingent RVGs; 45.95bn maximum exposure includes the 1.83bn equity investment and is not a current expected-loss liability. Future operating leases belong in future margins once; the analyst baseline assumes no incremental unmodeled guarantee loss. Additional-claims sensitivity exposes alternative expected incremental loss.'},
        'facts': facts, 'historical': history,
        'qualification_policy': {
            'other_financing': 'Exclude unknown residual by disclosed analyst assumption; allocation stress is not a bound on unidentified offsetting gross flows.',
            'historical_fcff': 'Preserve adopted CFO plus expensed-interest allocation less net identified cash PP&E. Capitalized interest is not added again without an investment/tax bridge.',
            'historical_tax': 'Retain reported historical provision and CFO, including FY2025 discrete tax effects. Do not add back the accounting charge to CFO; recurring forecast tax is separate.',
            'investment': 'Net separately identified PP&E receipts once. Historical cash PP&E differs from forecast cash plus financed additions; no automatic history-to-forecast FCFF CAGR.',
            'cash': 'Gross named unrestricted cash/marketable securities less 2% of anchor revenue as analyst operating-reserve proxy; restricted cash excluded. Additional assets use total nonmarketable investments 27.524bn carrying proxy, including equity-method 7.448bn once; no extra 7.448bn addition.',
            'debt': 'Notes disclosed fair value plus finance-lease carrying value as proxy in FCFF bridge. FCFE interest uses carrying debt plus finance leases; debt is not subtracted again after FCFE discounting.',
            'awards': 'Anchor common shares plus assumed vesting fraction of unvested RSUs. Full vesting is a conservative dilution proxy, not a current fair-value award calculation; no grant-date value or unrecognized cost deduction. Future SBC remains expensed and potential service-overlap bias is disclosed.',
            'other_claims': 'Zero additional separate claim is an analyst baseline, not verified absence. Legal/tax accruals remain in modeled operating flows without a second automatic deduction; users can impose incremental unmodeled claims.',
        },
        'source_documents': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES.values()},
        'methodology_sources': [
            'https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation',
            'https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-a',
            'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/mgtoption.htm',
            'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/noncashwc.htm',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + '\n'
    if args.check:
        if (DEST / 'policy.json').read_text() != text:
            raise ValueError('Meta analyst policy source replay differs')
    else:
        DEST.mkdir(parents=True, exist_ok=True); (DEST / 'policy.json').write_text(text)
    print('PASS: Meta analyst source projection and policy reproduce.')
