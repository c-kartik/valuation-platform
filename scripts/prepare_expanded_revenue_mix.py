"""Offline FY2021-Q1 extension. Original revenue/quarterly/DCF files stay intact."""
import copy
import gzip
import hashlib
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from valuation_platform.sec.client import SECClient
from valuation_platform.reporting.revenue_mix import prepare_mix
from valuation_platform.sec.filing_xbrl import fetch_filing_xbrl
from valuation_platform.sec.submissions import fetch_submissions, fetch_submission_history
from valuation_platform.sec.tickers import SECCompanyIdentity
from prepare_revenue_mix import IDS
ROOT = Path(__file__).resolve().parents[1]
class Retained:
    def __init__(self,ticker):
        self.ticker=ticker
        self.sources={}
    def get_bytes(self,url):
        name=hashlib.sha256(url.encode()).hexdigest()+'.gz'
        for folder in ['data/revenue-mix-expanded/sources','data/revenue-mix/sources','data/quarterly-reporting/filing-evidence','data/cash-allocation/sources']:
            path=ROOT/folder/self.ticker/name
            if path.exists():
                raw=gzip.decompress(path.read_bytes())
                self.sources[url]={'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
                return raw
        if '--refresh' in sys.argv:
            raw=SECClient(os.environ['SEC_USER_AGENT'],timeout=45).get_bytes(url)
            path=ROOT/'data/revenue-mix-expanded/sources'/self.ticker/name
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(raw,mtime=0))
            self.sources[url]={'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
            return raw
        raise ValueError('Missing retained evidence: '+url)
    def get_json(self,url):return json.loads(self.get_bytes(url))
def build(ticker):
    original=json.loads((ROOT/f'frontend/public/revenue-mix/{ticker}.json').read_text())
    history=json.loads((ROOT/f'frontend/public/cash-bridge/{ticker}.json').read_text())
    report=copy.deepcopy(history)
    company=SECCompanyIdentity(ticker,IDS[ticker],f'{IDS[ticker]:010d}',ticker,'SEC',datetime.now(timezone.utc))
    client=Retained(ticker)
    submissions=fetch_submissions(client,company)
    filings={f.accession_number:f for f in submissions.filings}
    earliest=min(date.fromisoformat(o['filed']) for r in report['rows'] for o in r['evidence']['revenue']['operands'])
    for h in submissions.history_files:
        if h.filing_to>=earliest:filings.update({f.accession_number:f for f in fetch_submission_history(client,h)})
    if ticker=='META':
        # Family of Apps / Reality Labs began in Q4 2021. Earlier 2021 quarters
        # use explicitly dated 2022 comparative segment disclosures, not invented splits.
        for row in report['rows']:
            if row['fiscal_year']==2021 and row['quarter']<4:
                for o in row['evidence']['revenue']['operands']:
                    comparable=next(q for q in history['rows'] if q['fiscal_year']==2022 and q['quarter']==int(o['end'][5:7])//3)
                    source=comparable['evidence']['revenue']['operands'][0]
                    o.update({k:source[k] for k in ['accession','filed','source_url']})
    accessions={o['accession'] for r in report['rows'] for o in r['evidence']['revenue']['operands']}
    if ticker=='META':accessions.add('0001326801-22-000108')
    instances={acc:fetch_filing_xbrl(client,company,filings[acc]) for acc in sorted(accessions)}
    package=prepare_mix(report,instances)
    assert package['rows'][-20:]==original['rows'], 'Original revenue observations changed'
    if ticker=='META':
        package['basis']+=' FY2021 Q1–Q3 use 2022 comparative FoA/RL disclosures; consolidated amounts match the original accepted quarters exactly.'
        package['notes'].append('FY2021 Q1–Q3: FoA/RL reporting was introduced in Q4 2021. These earlier quarters use comparative three/six/nine-month 2021 segment disclosures in the corresponding 2022 filings. Subtraction follows those comparative YTD operands; original consolidated quarterly revenue is unchanged. This is a disclosed recast presentation, not an as-known historical series.')
        for row in package['rows']:
            if row['fiscal_year']==2021 and row['quarter']<4:
                for evidence in row['evidence'].values():evidence['method']+=' · 2022 comparative segment disclosure'
    # Independent raw XML checks for every newly exposed consolidated metric
    # and each revenue component/parent-detail operand.
    from audit_reporting import raw_instance, check_fact, METRICS
    raw_cache={}
    def raw_source(accession):
        if accession not in instances:
            instances[accession]=fetch_filing_xbrl(client,company,filings[accession])
        instance=instances[accession]
        if accession not in raw_cache:raw_cache[accession]=raw_instance(client.get_bytes(instance.source_url))
        return raw_cache[accession]
    metric_checks=[];mix_checks=[]
    for row in history['rows'][:-20]:
        for metric in METRICS:
            for operand in row['evidence'][metric]['operands']:
                metric_checks.append(check_fact(raw_source(operand['accession']),operand,IDS[ticker]))
    for row in package['rows'][:-20]:
        for evidence in row['evidence'].values():
            for operand in evidence['operands']:
                dims=[('{'+d['axis_namespace']+'}'+d['axis'],'{'+d['member_namespace']+'}'+d['member']) for d in operand['dimensions']]
                mix_checks.append(check_fact(raw_source(operand['accession']),operand,IDS[ticker],operand['namespace'],dims))
    receipt={'ticker':ticker,'status':'MATCH','scope':'Newly exposed FY2021 quarters; independent retained XML metric and dimensional fact checks',
        'quarters':[r['id'] for r in history['rows'][:-20]],'metric_fact_checks':metric_checks,'revenue_fact_checks':mix_checks,
        'annual_category_checks':package['validation']['annual_category_checks']}
    receipt_path=ROOT/f'data/revenue-mix-expanded/{ticker}-audit.json';receipt_path.parent.mkdir(parents=True,exist_ok=True)
    receipt_path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    manifest={'ticker':ticker,'as_of':history['as_of'],'sources':client.sources}
    manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    dest=ROOT/f'data/revenue-mix-expanded/{ticker}-sources.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(manifest_bytes)
    package['source_manifest_sha256']=hashlib.sha256(manifest_bytes).hexdigest()
    out=ROOT/f'frontend/public/revenue-mix-expanded/{ticker}.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(package,sort_keys=True,indent=2)+'\n')
    print(ticker,len(package['rows']),'quarters; exact component/detail/annual reconciliations; original 20 rows unchanged')
    return package
if __name__=='__main__':
    for ticker in IDS:build(ticker)
