"""Retain a bounded public-source research packet; never change financial values."""
from pathlib import Path
import datetime as dt
import gzip
import hashlib
import json
import os
import time

import requests

HERE = Path(__file__).resolve().parent
SESSION = requests.Session()
SESSION.headers['User-Agent'] = os.environ['SEC_USER_AGENT']
MANIFEST = HERE / 'retrieval-manifest.json'
receipts = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []


def fetch(url, name, role):
    previous = next((x for x in receipts if x['url'] == url and x['status'] == 200), None)
    if previous:
        return gzip.decompress((HERE / previous['body']).read_bytes())
    response = SESSION.get(url, timeout=35)
    body = response.content
    target = 'sources/' + name + '.gz'
    (HERE / 'sources').mkdir(exist_ok=True)
    (HERE / target).write_bytes(gzip.compress(body, mtime=0))
    receipts.append(dict(url=url, final_url=response.url, role=role,
                         retrieved_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                         status=response.status_code, bytes=len(body),
                         sha256=hashlib.sha256(body).hexdigest(), body=target))
    MANIFEST.write_text(json.dumps(receipts, indent=2) + '\n')
    time.sleep(.3)
    return body if response.status_code == 200 else None


def rows(data):
    return [dict(zip(data, values)) for values in zip(*data.values())]


def main():
    inventory = []
    for ticker, cik in [('AAPL', 320193), ('META', 1326801), ('GOOGL', 1652044)]:
        raw = fetch(f'https://data.sec.gov/submissions/CIK{cik:010d}.json',
                    ticker + '-submissions', 'SEC filing inventory; locate correspondence')
        if not raw:
            continue
        filing_index = json.loads(raw)['filings']
        filings = rows(filing_index['recent'])
        for archive in filing_index.get('files', []):
            if archive['filingTo'] >= '2021-01-01' and archive['filingFrom'] <= '2026-11-04':
                body = fetch('https://data.sec.gov/submissions/' + archive['name'],
                             ticker + '-' + archive['name'], 'SEC older filing inventory')
                if body:
                    filings.extend(rows(json.loads(body)))
        selected = [r for r in filings if r['form'] in ('CORRESP', 'UPLOAD')
                    and '2021-01-01' <= r['filingDate'] <= '2026-11-04']
        for r in selected:
            accession = r['accessionNumber'].replace('-', '')
            url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{r["primaryDocument"]}'
            fetch(url, ticker + '-' + r['accessionNumber'], 'Public SEC staff/issuer correspondence')
            inventory.append(dict(ticker=ticker, form=r['form'], date=r['filingDate'], url=url))
        for r in filings:
            target_apple = (ticker == 'AAPL' and r['form'] == '10-Q'
                            and '2021-01-01' <= r['filingDate'] <= '2025-10-30')
            later_quarterly = (r['form'] == '10-Q'
                               and '2026-01-01' <= r['filingDate'] <= '2026-11-04')
            if target_apple or later_quarterly:
                url = (f'https://www.sec.gov/Archives/edgar/data/{cik}/'
                       f'{r["accessionNumber"].replace("-", "")}/{r["primaryDocument"]}')
                role = ('Apple FY2021-25 quarterly notes and MD&A; interest/financing/lease research'
                        if target_apple else 'Later 2026 quarterly notes and MD&A; comparative evidence only for FY2021-25 gaps')
                fetch(url, ticker + '-' + r['primaryDocument'], role)
    fetch('https://www.sec.gov/Archives/edgar/data/1652044/000130817926000342/goog-20260424.htm',
          'GOOGL-2026-proxy', 'Related-party Waymo financing and subsidiary ownership; no assumed cap table')
    (HERE / 'correspondence-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print(json.dumps(dict(correspondence_documents=len(inventory),
                         successful_sources=sum(x['status'] == 200 for x in receipts))))


if __name__ == '__main__':
    main()
