"""Additive, offline bridge history for the shared cash-analysis period control.

Uses the existing SEC snapshots and quarterly preparation policy unchanged.
Never overwrites the original research or DCF packages.
"""
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from prepare_quarterly_reporting import PILOTS, SnapshotClient
from valuation_platform.sec.company_facts import fetch_company_facts
from valuation_platform.sec.tickers import SECCompanyIdentity
from valuation_platform.reporting.quarterly import prepare_quarters

ROOT = Path(__file__).resolve().parents[1]
for ticker, (cik, name) in PILOTS.items():
    old_bytes = (ROOT / f'frontend/public/research-data/{ticker}.json').read_bytes()
    old = json.loads(old_bytes)
    cash = json.loads((ROOT / f'frontend/public/cash-allocation/{ticker}.json').read_bytes())
    snapshot = ROOT / f'data/quarterly-reporting/sources/{ticker}.json.gz'
    identity = SECCompanyIdentity(ticker, cik, f'{cik:010d}', name,
        'https://www.sec.gov/files/company_tickers.json', datetime.now(timezone.utc))
    facts = fetch_company_facts(SnapshotClient(snapshot, False, 'offline reproduction'), identity)
    report = prepare_quarters(facts, date.fromisoformat(old['as_of']), count=len(cash['quarterly']))
    assert report['rows'][-20:] == old['rows'], 'Existing reported observations changed'
    for row, allocation in zip(report['rows'], cash['quarterly'], strict=True):
        assert (row['id'], row['start'], row['end']) == (allocation['id'], allocation['start'], allocation['end'])
        assert row['values']['cfo'] == allocation['values']['cfo']
        assert row['values']['cash_capex'] == -allocation['values']['ppe']
    report['source_snapshot_sha256'] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    report['history_snapshot_sha256'] = hashlib.sha256(old_bytes).hexdigest()
    output = ROOT / f'frontend/public/cash-bridge/{ticker}.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print(ticker, len(report['rows']), 'quarters; original observations and allocation dates/CFO/capex match')
