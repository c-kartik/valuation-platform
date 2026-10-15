"""Fixed eighteen statement bindings; authoritative index joins, no filename guesses."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import statement_delivery as s
from acquire_selected_filing_identities import RecordingClient, body_of

OUTPUT='docs/evidence/preparation-statement-binding-repair.json'
BASELINE='60837808489c5a4bfe2526c489e6decb76572d11'


def documents(body,cik,accession):
    return s.index_documents(body,cik,accession)


def targets():
    ledger=json.loads(subprocess.check_output(['git','show',BASELINE+':docs/reported-population-delivery-ledger.json'],cwd=s.ROOT))
    out=[dict(ticker=r['ticker'],identity={k:v for k,v in r['identity']['fields'].items()})
         for r in ledger['rows'] if r['reconciliation']['status']=='NOT_ASSESSED']
    for r in out:
        for k in ('annual_start','annual_end'):r['identity'][k]=r['identity'][k]['date']
    if len(out)!=18 or {t:sum(r['ticker']==t for r in out) for t in ('CAT','MCD','PM','IBM')}!={'CAT':5,'MCD':5,'PM':3,'IBM':5}:raise ValueError('Fixed eighteen scope differs')
    return out


def acquire(path):
    selected=targets();catalog,_=s.records();client=RecordingClient(os.environ.get('SEC_USER_AGENT','').strip())
    if not os.environ.get('SEC_USER_AGENT','').strip():raise ValueError('CONFIG_VARIABLE_EMPTY; no requests')
    payload=json.loads(path.read_text()) if path.exists() else dict(version='statement-binding-repair-v1',baseline=BASELINE,targets=selected,rows=[],artifacts=[],attempts=[],request_count=0)
    if payload['targets']!=selected:raise ValueError('Fixed scope changed')
    def get(url):
        local=[r for r in catalog if r['url']==url]
        if len({r['sha256'] for r in local})>1:raise ValueError('Conflicting retained response bodies')
        if local:return local[0]['body'],dict(path=local[0]['path'],locator=local[0]['locator'],sha256=local[0]['sha256'],url=url,reused=True)
        existing=[a for a in payload['artifacts'] if a['source_url']==url]
        if existing:return body_of(existing[0]),dict(path=OUTPUT,locator='/artifacts/'+str(payload['artifacts'].index(existing[0])),sha256=existing[0]['sha256'],url=url,reused=False)
        attempted={a['source_url'] for a in payload['attempts']}
        if url in attempted:raise ValueError('Prior bounded request unsuccessful; no repeat')
        try:raw=client.get_bytes(url)
        finally:
            for a in client.receipts:a.update(retrieval_mode='authorized_eighteen_selected_statement_binding_repair',refresh_history='New actual receipt; prior evidence retained, not recovered original metadata.')
            payload['artifacts']+=client.receipts;payload['attempts']+=client.attempts
            client.receipts=[];client.attempts=[];payload['request_count']=len(payload['attempts'])
            path.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n')
        return raw,dict(path=OUTPUT,locator='/artifacts/'+str(len(payload['artifacts'])-1),sha256=hashlib.sha256(raw).hexdigest(),url=url,reused=False)
    for target in selected:
        previous=next((r for r in payload['rows'] if r['identity']==target['identity']),None)
        if previous is not None and previous['status']=='DOCUMENT_BOUND':continue
        row=dict(target,status='UNRESOLVED');p=target['identity'];base='https://www.sec.gov/Archives/edgar/data/'+str(p['cik'])+'/'+p['accession'].replace('-','')+'/'
        try:
            index,ref=get(base+p['accession']+'-index.html');docs=documents(index,p['cik'],p['accession'])
            primary=[r for r in docs if r['type']=='10-K' and r['url'].endswith(('.htm','.html'))]
            if len(primary)!=1:raise ValueError('Unique authoritative 10-K index document unavailable')
            raw,primary_ref=get(primary[0]['url']);s.verify_primary(dict(body=raw,url=primary[0]['url']),p)
            row.update(index=ref,primary=primary_ref,document=primary_ref,document_type='10-K')
            if target['ticker']=='IBM':
                text=raw.decode()
                # Exact exhibit type plus explicit incorporation; not a plausible report name.
                import re
                if not re.search(r'annual report.{0,250}incorporat|incorporat.{0,250}annual report',re.sub('<[^>]+>',' ',text),re.I|re.S):raise ValueError('Annual report incorporation reference unavailable')
                reports=[r for r in docs if r['type'] in ('EX-13','EX-13.1')]
                if len(reports)!=1:raise ValueError('Unique incorporated annual report index document unavailable')
                report,report_ref=get(reports[0]['url'])
                row.update(document=report_ref,document_type=reports[0]['type'],incorporation='Selected primary explicitly incorporates annual report; authoritative index EX-13 document',report_description=reports[0]['description'])
            row['status']='DOCUMENT_BOUND'
        except Exception as exc:row['reason']=str(exc) if isinstance(exc,ValueError) else type(exc).__name__
        if previous is not None:
            row['prior_binding_attempt']=previous
            payload['rows'][payload['rows'].index(previous)]=row
        else:payload['rows'].append(row)
        path.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n')
    return payload


def verify(payload):
    if payload['baseline']!=BASELINE or payload['targets']!=targets():raise ValueError('Exact fixed acquisition scope differs')
    if len(payload['rows'])!=18 or payload['request_count']!=len(payload['attempts']):raise ValueError('Target/request accounting differs')
    if [(r['ticker'],r['identity']) for r in payload['rows']]!=[(r['ticker'],r['identity']) for r in payload['targets']]:raise ValueError('Exact target row identities differ')
    if len({a['source_url'] for a in payload['attempts']})!=len(payload['attempts']):raise ValueError('Repeated bounded request')
    allowed=set()
    for row in payload['rows']:
        p=row['identity'];base='https://www.sec.gov/Archives/edgar/data/'+str(p['cik'])+'/'+p['accession'].replace('-','')+'/'
        allowed.add(base+p['accession']+'-index.html')
        if row['status']=='DOCUMENT_BOUND':allowed.update(row[k]['url'] for k in ('primary','document'))
    for a in payload['artifacts']:
        body_of(a)
        if a['source_url'] not in allowed:raise ValueError('Out-of-scope response')
        attempts=[x for x in payload['attempts'] if x['source_url']==a['source_url']]
        if len(attempts)!=1 or attempts[0]['request_started_at_utc']!=a['request_started_at_utc'] or attempts[0]['http_status']!=a['http_status']:raise ValueError('Actual receipt/attempt binding differs')
    scope,catalog,_=s.scope();bound=s.repaired_records(scope,catalog)
    for row in payload['rows']:
        if row['status']=='DOCUMENT_BOUND':
            r=bound.get(row['identity']['accession'])
            if r is None or (r['url'],r['sha256'])!=(row['document']['url'],row['document']['sha256']):raise ValueError('Repaired statement replay differs')
    return dict(targets=18,requests=payload['request_count'],bound=sum(r['status']=='DOCUMENT_BOUND' for r in payload['rows']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--checkpoint',type=Path,required=True);args=parser.parse_args()
    if args.checkpoint.resolve().is_relative_to(s.ROOT):raise ValueError('External acquisition checkpoint required')
    p=acquire(args.checkpoint)
    print(json.dumps(dict(targets=len(p['targets']),requests=p['request_count'],bound=sum(r['status']=='DOCUMENT_BOUND' for r in p['rows']),unresolved=[dict(ticker=r['ticker'],accession=r['identity']['accession'],reason=r.get('reason')) for r in p['rows'] if r['status']!='DOCUMENT_BOUND']),sort_keys=True))
