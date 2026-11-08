"""Independently tie selected reporting operands to filing-level extracted XBRL.

Reuses the existing SEC submissions, discovery and structural XBRL parsers.
Retains source responses for offline repetition. No valuation artifacts touched.
"""
import argparse, gzip, hashlib, json, os
from datetime import date, datetime, timezone
from pathlib import Path
from valuation_platform.sec.client import SECClient
from valuation_platform.sec.company_facts import fetch_company_facts
from valuation_platform.sec.submissions import fetch_submissions
from valuation_platform.sec.filing_xbrl import fetch_filing_xbrl
from valuation_platform.sec.tickers import SECCompanyIdentity
ROOT=Path(__file__).resolve().parents[1]
IDS={'GOOGL':1652044,'AAPL':320193,'META':1326801}
class EvidenceClient:
    def __init__(self,directory,refresh):
        self.directory=directory;directory.mkdir(parents=True,exist_ok=True)
        self.client=SECClient(os.environ.get('SEC_USER_AGENT','offline evidence'),timeout=40)
        self.refresh=refresh
    def get_bytes(self,url):
        path=self.directory/(hashlib.sha256(url.encode()).hexdigest()+'.gz')
        if not path.exists():
            if not self.refresh:raise ValueError('Missing retained filing source: '+url)
            path.write_bytes(gzip.compress(self.client.get_bytes(url),mtime=0))
        return gzip.decompress(path.read_bytes())
    def get_json(self,url): return json.loads(self.get_bytes(url))
def validate(ticker,refresh=False):
    package=json.loads((ROOT/f'frontend/public/research-data/{ticker}.json').read_text())
    cik=IDS[ticker]
    identity=SECCompanyIdentity(ticker,cik,f'{cik:010d}',ticker,'SEC',datetime.now(timezone.utc))
    client=EvidenceClient(ROOT/f'data/quarterly-reporting/filing-evidence/{ticker}',refresh)
    filings=fetch_submissions(client,identity).filings
    # Validate all operands for the latest quarter, plus the latest annual totals.
    operands=[o for e in package['rows'][-1]['evidence'].values() for o in e['operands']]
    latest_fy=max(t['fiscal_year'] for t in package['validation']['annual_tie_outs'])
    operands += [t['annual'] for t in package['validation']['annual_tie_outs'] if t['fiscal_year']==latest_fy]
    evidence=[];instances={}
    for o in operands:
        accession=o['accession']
        if accession not in instances:
            filing=next(f for f in filings if f.accession_number==accession)
            instances[accession]=fetch_filing_xbrl(client,identity,filing)
        instance=instances[accession]
        matches=[f for f in instance.facts if not f.dimensions and not f.is_nil
            and f.concept==o['concept'].split(':')[1] and f.start==date.fromisoformat(o['start'])
            and f.end==date.fromisoformat(o['end']) and f.numeric_value is not None
            and f.unit and not f.unit.is_divided
            and len(f.unit.numerator_measures)==1 and f.unit.numerator_measures[0].local_name=='USD']
        values={f.numeric_value for f in matches}
        if values!={o['value']}:raise ValueError(f'{ticker}: filing contradiction {o}, values {values}')
        evidence.append({'concept':o['concept'],'start':o['start'],'end':o['end'],
            'value':o['value'],'accession':accession,'source_url':instance.source_url,
            'contexts':[f.context_id for f in matches],'status':'MATCH'})
    receipt={'ticker':ticker,'as_of':package['as_of'],'source_snapshot_sha256':package['source_snapshot_sha256'],
        'filings':len(instances),'checks':len(evidence),'evidence':evidence,
        'scope':'Latest quarter and its YTD operands plus latest annual totals; not independent re-extraction of every displayed quarter.'}
    (ROOT/f'data/quarterly-reporting/{ticker}-filing-validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'ticker':ticker,'checks':len(evidence),'filings':len(instances),'status':'MATCH'}))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ticker',choices=IDS,required=True);p.add_argument('--refresh',action='store_true');a=p.parse_args();validate(a.ticker,a.refresh)
