"""Offline evidence checks. A PASS is not FCFF/FCFE financial clearance."""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    receipts = json.loads((HERE / 'retrieval-manifest.json').read_text())
    assert len({r['url'] for r in receipts}) == len(receipts)
    for r in receipts:
        body = gzip.decompress((HERE / r['body']).read_bytes())
        assert len(body) == r['bytes']
        assert hashlib.sha256(body).hexdigest() == r['sha256']
        assert r['status'] == 200
    correspondence = json.loads((HERE / 'correspondence-screen.json').read_text())
    assert len(correspondence) == 22
    assert sum(x['ticker'] == 'AAPL' for x in correspondence) == 6
    assert sum(x['ticker'] == 'META' for x in correspondence) == 16
    assert sum(x['pages'] is not None for x in correspondence) == 10
    screens = json.loads((HERE / 'later-and-quarterly-screen.json').read_text())
    assert len(screens) == 25
    for r in correspondence + screens:
        text = (HERE / r['text_file']).read_bytes()
        assert hashlib.sha256(text).hexdigest() == r['text_sha256']
    apple = [r for r in screens if 'Apple FY2021-25' in r['role']]
    assert len(apple) == 15
    missing_years = ['20231230', '20240330', '20240629', '20241228', '20250329', '20250628']
    gap_quarters = [r for r in apple if any(date in r['url'] for date in missing_years)]
    assert len(gap_quarters) == 6
    assert all(not any(r['exact_inline_tag_presence'].values()) for r in gap_quarters)
    assert all(r['exact_inline_tag_presence']['us-gaap:InterestExpense'] > 0
               for r in apple if r not in gap_quarters)
    # Immutable current adopted historical data must not be changed by research.
    baseline = ROOT / 'docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json'
    baseline_hash = hashlib.sha256(baseline.read_bytes()).hexdigest()
    assert baseline_hash == '9b2a9d775745e9d4bd08efe60d49619c24f632b16a28fce5fcba014fe1f55d86'
    result = dict(status='PASS_SOURCE_PACKET_CHECKS_ONLY', successful_retained_sources=len(receipts),
                  correspondence_documents=22, pdf_correspondence_documents=10,
                  apple_target_quarterlies=15, later_quarterlies=9, proxy_documents=1,
                  baseline_unchanged_sha256=baseline_hash, new_verified_cashflow_cells=0,
                  financial_clearance='OPEN', new_method_adopted=False,
                  limitation='Text/tag screening and targeted note review do not prove universal disclosure absence or zero amounts.')
    (HERE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
