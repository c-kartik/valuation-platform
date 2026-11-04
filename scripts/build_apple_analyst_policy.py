"""Reproduce the Apple analyst source projection without modifying retained facts."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/company-resolutions/AAPL/analyst-ready-2026-11-04'
FILES = {
    'financing': 'docs/company-resolutions/AAPL/remaining-issues-2026-11-04/financing/results.json',
    'equity': 'docs/company-resolutions/AAPL/remaining-issues-2026-11-04/equity/results.json',
    'operating': 'docs/company-resolutions/AAPL/operating-fcff-2026-11-04/adopted-history.json',
    'ledger': 'docs/company-resolutions/AAPL/implementation-2026-11-03/evidence-ledger.json',
    'preload': 'data/preload/aapl-v1/policy.json',
    'observations': 'data/preload/aapl-v1/observations.json',
    'source_manifest': 'data/preload/aapl-v1/sources/manifest.json',
}


def build():
    data = {k: json.loads((ROOT / f).read_text()) for k, f in FILES.items()}
    equity = data['equity']['sources']
    config = data['preload']['configuration']
    macro = {o['key']: o for o in data['observations'] if o['key'] in ('treasury_10y', 'implied_erp')}
    rf = Decimal(macro['treasury_10y']['value']); erp = Decimal(macro['implied_erp']['value'])
    ke = rf + Decimal(config['beta']) * erp
    kd = rf + Decimal(config['credit_spread'])
    wacc = ke * Decimal(config['equity_weight']) + kd * (1-Decimal(config['debt_tax_shield'])) * Decimal(config['debt_weight'])
    facts = {}
    for group in ('cash', 'debt', 'finance_leases'):
        facts.update(equity[group])
    for name in ('term_debt_fair_value', 'dated_common_shares', 'unvested_rsus'):
        facts[name] = equity[name]
    # Each projection retains its exact source location, period, unit and receipt.
    history = []
    for funding, operating, ledger in zip(data['financing']['periods'], data['operating']['periods'], data['ledger']['periods'], strict=True):
        assert funding['fiscal_year'] == operating['fiscal_year'] == ledger['fiscal_year']
        sbc = ledger['operating_bridge']['sbc_remains_expensed']
        history.append({
            'fiscal_year': funding['fiscal_year'], 'identity': funding['identity'],
            'cfo_usd': funding['reported_operating_cash_flow']['value'],
            'cash_ppe_usd': funding['reported_cash_ppe']['value'],
            'identified_net_borrowing_usd': funding['identified_net_borrowing']['amount_usd'],
            'other_financing_usd': funding['classification']['unknown_components'][0]['amount_usd'],
            'sbc_usd': sbc['cash_contribution_usd'],
            'fcff_usd': operating['fcff']['amount_usd'],
            'source_urls': operating['source_urls'],
            'cfo_source': funding['reported_operating_cash_flow'],
            'cash_ppe_source': funding['reported_cash_ppe'],
            'sbc_source': sbc['source'],
            'financing_source_reference': FILES['financing'] + '#/periods/' + str(len(history)),
        })
    return {
        'schema_version': 'apple-analyst-policy-v1', 'version': 'aapl-analyst-2026-11-04-v1',
        'ticker': 'AAPL', 'cik': 320193, 'anchor_date': '2025-09-27',
        'approval': 'User: work on Apple to make all five outputs analyst ready, following approval of reasonable disclosed analyst assumptions.',
        'defaults': {'operating_cash_reserve_ratio': '0.02', 'cost_of_equity': str(ke),
                     'pre_tax_cost_of_debt': str(kd), 'rsu_vesting_fraction': '1',
                     'additional_claims_usd': '0', 'historical_other_financing_fraction': '0'},
        'discount_basis': {'risk_free': str(rf), 'beta': config['beta'], 'equity_risk_premium': str(erp),
                           'target_equity_weight': config['equity_weight'], 'target_debt_weight': config['debt_weight'],
                           'debt_tax_shield': config['debt_tax_shield'], 'saved_base_wacc': str(wacc),
                           'macro_observations': macro,
                           'macro_sources': [s for s in data['source_manifest']['sources'] if s['id'] in {o['source'] for o in macro.values()}],
                           'classification': 'DATED_MACRO_OBSERVATIONS_AND_CONFIGURED_ANALYST_ASSUMPTIONS'},
        'facts': facts, 'historical': history,
        'source_documents': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES.values()},
        'methodology_sources': [
            'https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation',
            'https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-a',
            'https://pages.stern.nyu.edu/~adamodar/pdfiles/eqnotes/valopt.pdf',
            'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/noncashwc.htm',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    text = json.dumps(build(), indent=2, sort_keys=True) + '\n'
    if args.check:
        if (DEST / 'policy.json').read_text() != text: raise ValueError('Apple analyst policy source replay differs')
    else:
        DEST.mkdir(parents=True, exist_ok=True); (DEST / 'policy.json').write_text(text)
    print('PASS: Apple analyst source projection and policy reproduce.')
