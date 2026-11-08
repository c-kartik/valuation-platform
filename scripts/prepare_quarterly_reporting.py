"""Refresh/reproduce isolated reporting assets using existing SEC transport/parser.

Run from the repository root with PYTHONPATH=src. No existing DCF files written.
"""
import argparse, gzip, hashlib, json, os
from datetime import date, datetime, timezone
from pathlib import Path
from valuation_platform.sec.client import SECClient
from valuation_platform.sec.company_facts import fetch_company_facts
from valuation_platform.sec.tickers import SECCompanyIdentity
from valuation_platform.reporting.quarterly import prepare_quarters

ROOT = Path(__file__).resolve().parents[1]
PILOTS = {'GOOGL': (1652044, 'Alphabet Inc.'), 'AAPL': (320193, 'Apple Inc.'), 'META': (1326801, 'Meta Platforms, Inc.')}

class SnapshotClient:
    def __init__(self, path, refresh, user_agent):
        self.path, self.refresh = path, refresh
        self.client = SECClient(user_agent, timeout=40) if refresh else None
    def get_json(self, url):
        if self.refresh:
            payload = self.client.get_json(url)
            raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_bytes(gzip.compress(raw, mtime=0))
        return json.loads(gzip.decompress(self.path.read_bytes()))

def build(ticker, as_of, refresh=False, user_agent='offline reproduction', output=None):
    cik, name = PILOTS[ticker]
    identity = SECCompanyIdentity(ticker, cik, f'{cik:010d}', name,
        'https://www.sec.gov/files/company_tickers.json', datetime.now(timezone.utc))
    path = ROOT/'data/quarterly-reporting/sources'/f'{ticker}.json.gz'
    facts = fetch_company_facts(SnapshotClient(path, refresh, user_agent), identity)
    package = prepare_quarters(facts, as_of)
    package['source_snapshot_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    destination = output or ROOT/'frontend/public/research-data'/f'{ticker}.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(package, sort_keys=True, indent=2)+'\n'
    destination.write_text(content)
    return package

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ticker', choices=list(PILOTS), required=True)
    parser.add_argument('--as-of', type=date.fromisoformat, required=True)
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    agent = os.environ.get('SEC_USER_AGENT', '')
    if args.refresh and not agent.strip():
        parser.error('Set SEC_USER_AGENT to an identifying contact for SEC access')
    result = build(args.ticker, args.as_of, args.refresh, agent)
    print(json.dumps({'ticker': args.ticker, 'quarters': len(result['rows']),
                      'annual_tie_outs': len(result['validation']['annual_tie_outs']),
                      'latest': result['rows'][-1]['end'], 'excluded': result['validation']['excluded_periods']}))
