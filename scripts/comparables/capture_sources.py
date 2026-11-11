"""Capture new official SEC snapshots into a NEW directory; never replace a freeze.

SEC_USER_AGENT must identify a contact. Use --output for a later snapshot and
review it before replacing the accepted preparation snapshot. No DCF files used.
"""
import argparse
import gzip
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from valuation_platform.sec.client import SECClient
from prepare import BASE, ISSUERS, ROOT, write

def capture(output):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Choose an empty snapshot directory; retained evidence cannot be overwritten')
    output.mkdir(parents=True, exist_ok=True)
    client = SECClient(os.environ['SEC_USER_AGENT'], timeout=60)
    sources = []
    for ticker, cik in ISSUERS.items():
        for kind, url in [('companyfacts', f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010}.json'),
                          ('submissions', f'https://data.sec.gov/submissions/CIK{cik:010}.json')]:
            raw = client.get_bytes(url)
            json.loads(raw)
            path = output / f'{ticker}-{kind}.json.gz'
            path.write_bytes(gzip.compress(raw, mtime=0))
            sources.append({'ticker': ticker, 'kind': kind, 'url': url,
                            'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            time.sleep(.25)
    write(output / 'manifest.json', {'retrieved_at': datetime.now(timezone.utc).isoformat(), 'sources': sources})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=BASE / 'sources')
    args = parser.parse_args()
    if not os.environ.get('SEC_USER_AGENT'):
        parser.error('Set SEC_USER_AGENT to an identifying contact')
    capture(args.output.resolve())
