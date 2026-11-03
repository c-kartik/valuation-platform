"""Generate/check the current five-year, two-metric platform projection.

Reads the immutable reviewed company ledgers; their source replays remain
separate controls. Provisional values are visible with their actual scope.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from valuation_platform.review.resolved_history import adopted_window
from valuation_platform.review.pilot_cashflows import RESOURCE

KINDS = {'AAPL': 'aapl-fy2025', 'META': 'meta-fy2025', 'GOOGL': 'googl-fy2025'}


def generate(root=ROOT):
    inputs = {}; companies = {}
    for ticker, kind in KINDS.items():
        path = f'docs/company-resolutions/{ticker}/results.json'
        raw = (root / path).read_bytes(); inputs[path] = hashlib.sha256(raw).hexdigest()
        ledger = json.loads(raw); periods = []
        for original, historical in zip(ledger['periods'], adopted_window(root, kind), strict=True):
            identity = original['identity']; revenue = historical['revenue']
            if identity['annual_end'] != revenue['period_end'] or identity['accession'] != revenue['accession']:
                raise ValueError('Resolution and adopted period disagree')
            fcfe = original['fcfe']; funding = original['financing']['net_borrowing']['amount_usd']
            if ticker == 'AAPL':
                cash_fcf = original['reported_cash_fcf']['amount_usd']
                sources = historical['fcff_calculation']['sources']
                unresolved = ['A2', 'A3']
            else:
                cash_fcf = str(Fraction(original['inputs']['cfo']) - Fraction(original['net_cash_investment']['amount_usd']))
                sources = original['source_urls']; unresolved = ['M1'] if ticker == 'META' else ['G1', 'G2']
            if Fraction(cash_fcf) + Fraction(funding) != Fraction(fcfe['amount_usd']):
                raise ValueError('Cash generation plus funding does not reproduce FCFE')
            provisional = fcfe['status'] == 'PROVISIONAL_FINANCING_SCOPE_UNRESOLVED'
            year = original['fiscal_year']
            periods.append({
                'fiscal_year': year, 'annual_start': identity['annual_start'], 'annual_end': identity['annual_end'],
                'accession': identity['accession'], 'revenue_usd': revenue['amount'],
                'reported_cash_fcf_usd': cash_fcf, 'identified_net_borrowing_usd': funding,
                'fcff': {'amount_usd': historical['fcff'], 'basis': historical['fcff_basis'],
                    'status': 'AVAILABLE_UNDER_REPORTED_CASH_CONVENTION' if historical['fcff'] is not None else 'UNAVAILABLE_MISSING_INTEREST',
                    'scope': 'CONSOLIDATED', 'cleared': historical['fcff'] is not None,
                    'source_urls': sources, 'operands': historical['fcff_calculation']['inputs'],
                    'open_items': ['A1'] if historical['fcff'] is None else [],
                    'valuation_basis_aligned': False},
                'fcfe': {'amount_usd': fcfe['amount_usd'], 'basis': 'REPORTED_CFO_CASH_PPE_IDENTIFIED_NET_BORROWING',
                    'status': fcfe['status'],
                    'scope': 'IDENTIFIED_FINANCING_ONLY' if provisional else 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION',
                    'cleared': False, 'parent_common_amount_usd': None,
                    'parent_common_status': 'UNAVAILABLE_FINANCING_SCOPE' if provisional else 'UNAVAILABLE_ATTRIBUTION_NOT_DISCLOSED',
                    'source_urls': sources, 'open_items': unresolved,
                    'formula': 'reported CFO - cash PP&E net of identified receipts + identified net borrowing'},
            })
        companies[ticker] = {'schema_version': 'pilot-company-cashflows-v1', 'ticker': ticker,
            'status': 'OPEN', 'review_passed': False, 'periods': periods,
            'roadblock_register': 'docs/company-resolutions/OPEN-ROADBLOCKS.md',
            'unresolved_scope_items': {'AAPL':['A1','A2','A3','A4','A5','A6','A7','S1','S2','S3','S4'],
                'META':['M1','M2','S1','S2','S3','S4'], 'GOOGL':['G1','G2','G3','S1','S2','S3','S4']}[ticker],
            'notice': 'Historical cash measures are derived from rounded filing inputs. Provisional FCFE excludes unclassified funding and is not cleared parent-common cash. Consolidated FCFE is before minority-interest attribution. Missing is not zero. Historical CFO and EBIT-forecast bases differ; no cross-basis FCFF CAGR.',
            'decision_record': f'docs/company-resolutions/{ticker}/README.md',
            'resolution_sha256': inputs[path]}
    return {'schema_version': 'pilot-cashflow-projection-v1', 'approval_date': '2026-11-03',
        'inputs_sha256': inputs, 'companies': companies}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--write', action='store_true'); args = parser.parse_args()
    expected = json.dumps(generate(), sort_keys=True, indent=2) + '\n'; path = ROOT / RESOURCE
    if args.write: path.write_text(expected)
    elif not path.exists() or path.read_text() != expected: raise SystemExit('Pilot platform projection differs from reviewed ledger replay')
    print('Pilot projection: 15 periods / 30 metric records; open statuses preserved')


if __name__ == '__main__': main()
