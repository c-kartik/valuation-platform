"""Offline fresh source binding for Apple financing, without clearing unknowns."""
import argparse
import csv
from fractions import Fraction
import hashlib
from io import StringIO
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'src')]
from calculate_historical_fcff_from_filings import RetainedFiling
from resolve_apple_cashflows import full_financing, presentation_bridge
from valuation_platform.review.operating_fcff import amount, serialized


def build():
    source_map = json.loads((ROOT / 'docs/company-resolutions/AAPL/source-map.json').read_text())
    prior = json.loads((ROOT / 'docs/company-resolutions/AAPL/results.json').read_text())
    package = json.loads((ROOT / 'docs/company-data-preparation/aapl-analyst-input-package.json').read_text())
    rows = package['aapl_history_review']['periods']
    manifests, filings, periods, receipt_hashes = {}, {}, [], {}
    for source, mapping, old in zip(rows, source_map['periods'], prior['periods'], strict=True):
        identity = source['identity']
        assert identity == mapping['identity'] == old['identity']
        year = int(identity['annual_end'][:4])
        filing = RetainedFiling(ROOT, source, manifests)
        filings[year] = filing
        bound, classified = full_financing(filing, identity, mapping['financing_rows'])
        points = {}
        for key in ('cfo_control', 'cash_ppe'):
            previous = old['operating_fcff_candidate']['inputs'][key]
            point = filing.extract(previous['concept'], identity, previous['namespace'])
            assert amount(point['value']) == amount(previous['value'])
            points[key] = point
        cash_fcf = amount(points['cfo_control']['value']) - amount(points['cash_ppe']['value'])
        funding = amount(classified['net_borrowing']['amount_usd'])
        provisional = cash_fcf + funding
        assert provisional == amount(old['fcfe']['amount_usd'])
        for point in [*points.values(), *(r['source'] for r in bound)]:
            for receipt in point['sources']:
                receipt_hashes[receipt['url']] = {k: receipt[k] for k in ('sha256', 'byte_length', 'source_reference')}
        periods.append({
            'fiscal_year': year, 'identity': identity,
            'source_rows': bound, 'classification': classified,
            'reported_operating_cash_flow': points['cfo_control'],
            'reported_cash_ppe': points['cash_ppe'],
            'reported_cash_fcf': serialized(cash_fcf),
            'identified_net_borrowing': serialized(funding),
            'identified_funding_fcfe': serialized(provisional),
            'full_fcfe_usd': None,
            'status': 'PROVISIONAL_FINANCING_SCOPE_UNRESOLVED',
            'exact_current_fix_possible': False,
            'unknown_other_debt_component_usd': None,
            'actual_finance_lease_principal_usd': None,
            'finance_lease_principal_containing_caption': None,
            'financing_statement_difference_usd': '0',
            'old_to_new_fcfe_change_usd': '0',
            'classification_assumes_other_zero': False,
            'lease_principal_subtracted_again': False,
        })
    assert [p['fiscal_year'] for p in periods] == list(range(2021, 2026))
    return {
        'schema_version': 'apple-remaining-financing-replay-v1',
        'date': '2026-11-04', 'ticker': 'AAPL', 'company_status': 'OPEN',
        'stage_status': 'SOURCE_REPLAY_PASS_DISCLOSURE_DEPENDENCY_OPEN',
        'method': 'reported CFO - reported cash PP&E + separately identified net term-debt and commercial-paper cash',
        'unit': 'USD', 'source_receipts': receipt_hashes, 'periods': periods,
        'fy2021_presentation_bridge': presentation_bridge(filings, source_map),
        'validation': {'annual_financing_statements_reconciled': 5,
                       'primary_instance_source_pairs': len(receipt_hashes) // 2,
                       'reported_cfo_and_cash_ppe_rebound': 10,
                       'provisional_fcfe_reproduced': 5,
                       'exact_full_fcfe_newly_cleared': 0,
                       'runtime_values_changed': 0},
        'closure_conditions': [
            'Identify any debt funding, debt repayment and financing-fee components inside Other; provide a gross component reconciliation to each signed disclosed net amount.',
            'Obtain actual consolidated USGAAP finance-lease principal cash paid for each year and identify its containing cash-statement caption, including whether amounts overlap already identified debt cash.',
            'Alternatively obtain a complete sourced finance-lease liability roll-forward with additions, interest, principal, modifications, terminations, FX and other noncash changes distinguished; stock reclassification is not repayment.',
            'Recompute net borrowing once per cash transaction, reconcile the complete statement, then independently review historical FCFE and update the adopted pipeline only after the evidence passes.',
        ],
        'prohibited_shortcuts': ['Assign all Other to debt', 'Assume Other contains no debt',
            'Infer principal from closing minus opening liability alone',
            'Treat future maturities or noncash ROU additions as historical cash principal',
            'Treat a small net Other outflow as a bound on unknown offsetting gross components',
            'Copy subsidiary IFRS lease cash into Apple Inc consolidated USGAAP FCFE'],
        'issuer_request_sent': False,
    }


def csv_text(data):
    out = StringIO(newline='')
    fields = ['fiscal_year', 'caption', 'signed_cash_usd', 'classification', 'included_in_net_borrowing',
              'table', 'row', 'column', 'context_id', 'primary_xml_id', 'primary_source_url', 'primary_sha256']
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for period in data['periods']:
        for row in period['source_rows']:
            receipt = next(s for s in row['source']['sources'] if s['url'].endswith('.htm'))
            writer.writerow({**{k: row[k] for k in fields if k in row},
                'fiscal_year': period['fiscal_year'], 'primary_source_url': receipt['url'],
                'primary_sha256': receipt['sha256']})
    return out.getvalue()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    data = build()
    outputs = {'results.json': json.dumps(data, indent=2, sort_keys=True) + '\n',
               'financing-classifications.csv': csv_text(data)}
    for name, content in outputs.items():
        path = HERE / name
        if args.write:
            path.write_text(content)
        elif path.read_text() != content:
            raise SystemExit(f'Replay differs: {path}')
    print(json.dumps(data['validation'], sort_keys=True))
