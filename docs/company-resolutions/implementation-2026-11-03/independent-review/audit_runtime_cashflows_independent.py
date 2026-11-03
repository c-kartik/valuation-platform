"""Exercise a running API; reconcile its published records to independent sources."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

OUT = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equal(actual, expected):
    if expected is None:
        assert actual is None
    else:
        assert actual is not None
        assert abs(Fraction(actual) - Fraction(expected)) < Fraction(1, 10 ** 30)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--health-api')
    args = parser.parse_args()
    independent = json.loads((OUT / 'source-audit.json').read_text())
    base = args.api.rstrip('/')
    bundle = args.bundle.resolve()
    resource = 'docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json'
    config = json.loads((bundle / 'src/valuation_platform/api/bundle-files.json').read_text())
    source_config = json.loads((ROOT / 'src/valuation_platform/api/bundle-files.json').read_text())
    assert config == source_config
    assert digest(bundle / resource) == digest(ROOT / resource) == config['resources'][resource]
    # Independently verify every allowlisted code/resource byte, not only API totals.
    hashes = {}
    for path in config['python_files']:
        assert digest(bundle / path) == digest(ROOT / path), path
        hashes[path] = digest(bundle / path)
    for path, expected in config['resources'].items():
        assert digest(bundle / path) == expected, path
        hashes[path] = expected

    def fetch(path):
        with urlopen(base + path, timeout=15) as response:
            assert response.status == 200
            return json.loads(response.read())

    with urlopen((args.health_api or base).rstrip('/') + '/health', timeout=15) as response:
        assert json.loads(response.read()) == {'status': 'ready'}
    checks = []
    for ticker in ('AAPL', 'META', 'GOOGL'):
        company = fetch(f'/api/v1/cashflows/{ticker}')
        assert company['ticker'] == ticker and company['status'] == 'OPEN'
        assert company['review_passed'] is False
        assert company['roadblock_register'] == 'docs/company-resolutions/OPEN-ROADBLOCKS.md'
        assert company['unresolved_scope_items'] == {
            'AAPL': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'S1', 'S2', 'S3', 'S4'],
            'META': ['M1', 'M2', 'S1', 'S2', 'S3', 'S4'],
            'GOOGL': ['G1', 'G2', 'G3', 'S1', 'S2', 'S3', 'S4'],
        }[ticker]
        assert [p['fiscal_year'] for p in company['periods']] == list(range(2021, 2026))
        for period in company['periods']:
            year = period['fiscal_year']
            ff = next(c for c in independent['cells'] if c['ticker'] == ticker and c['fiscal_year'] == year and c['metric'] == 'FCFF')
            fe = next(c for c in independent['cells'] if c['ticker'] == ticker and c['fiscal_year'] == year and c['metric'] == 'FCFE')
            equal(period['fcff']['amount_usd'], ff['independently_recomputed_usd'])
            equal(period['fcfe']['amount_usd'], fe['independently_recomputed_partial_or_consolidated_usd'])
            assert period['fcff']['scope'] == 'CONSOLIDATED'
            assert period['fcff']['valuation_basis_aligned'] is False
            assert period['fcff']['cleared'] == (ff['independently_recomputed_usd'] is not None)
            assert period['fcfe']['parent_common_amount_usd'] is None
            assert period['fcfe']['cleared'] is False
            assert period['fcfe']['status'] == fe['published_status']
            assert period['fcfe']['scope'] == ('CONSOLIDATED_BEFORE_NCI_ATTRIBUTION' if ticker == 'GOOGL' else 'IDENTIFIED_FINANCING_ONLY')
            for metric in ('fcff', 'fcfe'):
                assert period[metric]['source_urls'] and period[metric]['basis']
                assert all(s.startswith('https://www.sec.gov/Archives/edgar/data/') for s in period[metric]['source_urls'])
            checks.append(dict(ticker=ticker, fiscal_year=year, api_publication_verdict='PASS',
                               requested_financial_coverage_verdict='FAIL' if ff['hard_blockers'] or fe['hard_blockers'] else 'PASS',
                               record=period))
        (OUT / f'runtime-{ticker}.json').write_text(json.dumps(company, indent=2) + '\n')
    result = dict(api=base, bundle=str(bundle), integration_verdict='PASS', frontend_verdict='PENDING',
                  requested_full_financial_coverage_verdict='FAIL', checked_metric_cells=30,
                  checked_bundle_hashes=hashes, periods=checks)
    (OUT / 'runtime-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: 30 API metric publications/source ties and pinned bundle bytes. FAIL: requested full financial coverage. Frontend pending.')


if __name__ == '__main__':
    main()
