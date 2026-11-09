"""Retain filing-level segment facts and prepare an isolated revenue-mix package.

Offline by default; --refresh permits missing evidence retrieval via existing SEC
transport/discovery. Never changes the quarterly or DCF input datasets.
"""
import argparse
import gzip
import hashlib
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

from valuation_platform.sec.client import SECClient
from valuation_platform.sec.filing_xbrl import fetch_filing_xbrl
from valuation_platform.sec.submissions import fetch_submissions, fetch_submission_history
from valuation_platform.sec.tickers import SECCompanyIdentity

ROOT = Path(__file__).resolve().parents[1]
IDS = {'GOOGL': 1652044, 'AAPL': 320193, 'META': 1326801}

class EvidenceClient:
    def __init__(self, ticker, refresh):
        self.directory = ROOT / 'data/revenue-mix/sources' / ticker
        self.fallback = ROOT / 'data/quarterly-reporting/filing-evidence' / ticker
        self.directory.mkdir(parents=True, exist_ok=True)
        self.refresh = refresh
        self.client = SECClient(os.environ.get('SEC_USER_AGENT', 'offline reproduction'), timeout=45)
        self.sources = {}

    def get_bytes(self, url):
        name = hashlib.sha256(url.encode()).hexdigest() + '.gz'
        path = self.directory / name
        if not path.exists() and (self.fallback / name).exists():
            path.write_bytes((self.fallback / name).read_bytes())
        if not path.exists():
            if not self.refresh:
                raise ValueError('Missing retained source: ' + url)
            path.write_bytes(gzip.compress(self.client.get_bytes(url), mtime=0))
        data = gzip.decompress(path.read_bytes())
        self.sources[url] = {'file': name, 'sha256': hashlib.sha256(data).hexdigest()}
        return data

    def get_json(self, url):
        return json.loads(self.get_bytes(url))


def collect(ticker, refresh=False, verbose=True):
    report = json.loads((ROOT / f'frontend/public/research-data/{ticker}.json').read_text())
    cik = IDS[ticker]
    company = SECCompanyIdentity(ticker, cik, f'{cik:010d}', ticker, 'SEC', datetime.now(timezone.utc))
    client = EvidenceClient(ticker, refresh)
    submissions = fetch_submissions(client, company)
    filings = {f.accession_number: f for f in submissions.filings}
    earliest = min(date.fromisoformat(o['filed']) for r in report['rows'] for o in r['evidence']['revenue']['operands'])
    for history in submissions.history_files:
        if history.filing_to >= earliest:
            filings.update({f.accession_number: f for f in fetch_submission_history(client, history)})
    operands = [o for r in report['rows'] for o in r['evidence']['revenue']['operands']]
    accessions = sorted({o['accession'] for o in operands})
    instances = {}
    for accession in accessions:
        if accession not in filings:
            raise ValueError('Filing absent from submissions: ' + accession)
        instances[accession] = fetch_filing_xbrl(client, company, filings[accession])
        if verbose:
            print(f'{ticker} retained {accession}', flush=True)
    manifest = {'ticker': ticker, 'as_of': report['as_of'], 'sources': client.sources}
    return report, instances, manifest


def build(ticker, refresh=False, fetch_only=False):
    from valuation_platform.reporting.revenue_mix import prepare_mix
    report, instances, manifest = collect(ticker, refresh)
    (ROOT / f'data/revenue-mix/{ticker}-sources.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    if fetch_only:
        return
    package = prepare_mix(report, instances)
    package['source_manifest_sha256'] = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    path = ROOT / f'frontend/public/revenue-mix/{ticker}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(package, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'ticker': ticker, 'quarters': len(package['rows']), 'total_checks': package['validation']['quarter_total_checks']}))
    return package

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ticker', choices=IDS, required=True)
    p.add_argument('--refresh', action='store_true')
    p.add_argument('--fetch-only', action='store_true')
    args = p.parse_args()
    if args.refresh and not os.environ.get('SEC_USER_AGENT'):
        p.error('Set SEC_USER_AGENT to an identifying contact')
    build(args.ticker, args.refresh, args.fetch_only)
