"""Fixed four-issuer metadata/seed repair; offline replay is default."""
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from acquire_selected_filing_identities import RecordingClient,ReplayClient,body_of,cutoff,annual_identity
from valuation_platform.sec.submissions import fetch_submissions,fetch_submission_history
from valuation_platform.sec.filing_selection import select_filings
from valuation_platform.sec.filing_xbrl import fetch_filing_xbrl,_primary_document_stem
from valuation_platform.sec.tickers import SECCompanyIdentity

BASELINE='eb99ab310fe6d3860d4cd3036e8a922189350d38'
OUTPUT='docs/evidence/income-binding-repair.json'


def pinned(path):return subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT)


def scope():
    ledger=json.loads(pinned('docs/approved-income-integration-ledger.json'))
    groups={n:[] for n in ('JNJ','KLAC','META','COST')}
    for r in ledger['rows']:
        if r['issuer'] in groups:
            groups[r['issuer']].append(dict(issuer=r['issuer'],identity=r['identity']))
    if any(len(g)!=5 for g in groups.values()):raise ValueError('Exactly four five-period frozen groups required')
    if sum(r['identity']['accession'] is not None for n in ('META','COST') for r in groups[n])!=9:raise ValueError('Nine seed candidates plus one unknown required')
    manifest=json.loads(pinned('docs/phase1-selected-filing-identity-manifest.json'))
    for n in ('JNJ','KLAC'):
        for r in groups[n]:
            if len([m for m in manifest['rows'] if m['identity']==r['identity'] and m['ticker']==n])!=1:raise ValueError('Approved target identity differs')
    return groups


def company(name,cik):return SECCompanyIdentity(name,cik,f'{cik:010d}',name,'Frozen issuer/CIK mapping',cutoff())


def selected_metadata(client,name,targets):
    c=company(name,targets[0]['identity']['cik']);sub=fetch_submissions(client,c)
    raw=client.get_json(sub.source_url) if isinstance(client,ReplayClient) else json.loads(body_of(client.receipts[-1]))
    if int(raw['cik'])!=c.cik:raise ValueError('Submissions entity differs')
    filings=[f for f in sub.filings if f.filing_date<=cutoff().date()]
    selected=select_filings(filings)
    for history in sub.history_files:
        if selected.has_complete_annual_history:break
        # Existing bounded history loader: only listed supplemental submissions,
        # stop once the unchanged five-annual selector is satisfied.
        filings.extend(f for f in fetch_submission_history(client,history) if f.filing_date<=cutoff().date())
        selected=select_filings(filings)
    return c,{str(f.report_date):f for f in selected.annual}


def filing_dict(f):return dict(accession_number=f.accession_number,form=f.form,filing_date=str(f.filing_date),report_date=str(f.report_date),primary_document=f.primary_document)


def target_binding(target,f):
    i=target['identity']
    if f.form!='10-K' or str(f.report_date)!=i['annual_end'] or (i['accession'] and f.accession_number!=i['accession']):raise ValueError('Frozen exact candidate differs from selected official record')


def acquire():
    groups=scope();agent=os.environ.get('SEC_USER_AGENT','').strip()
    if not agent:raise ValueError('Nonempty exported SEC_USER_AGENT required; no requests')
    client=RecordingClient(agent);rows=[];selection=[]
    for name,targets in groups.items():
        try:
            c,by_end=selected_metadata(client,name,targets)
            selection.append(dict(issuer=name,selected_ends=list(by_end),frozen_ends=[r['identity']['annual_end'] for r in targets],
                complete_frozen_history_match=list(by_end)==[r['identity']['annual_end'] for r in targets]))
        except Exception as exc:
            rows.extend(dict(issuer=name,target=r['identity'],status='UNRESOLVED',reason=type(exc).__name__+' during fixed submissions replay',filing=None,identity=None) for r in targets);continue
        for t in targets:
            row=dict(issuer=name,target=t['identity'],status='UNRESOLVED',reason=None,filing=None,identity=None)
            try:
                f=by_end.get(t['identity']['annual_end'])
                if f is None:raise ValueError('Frozen annual end absent from unchanged cutoff selection')
                target_binding(t,f);row['filing']=filing_dict(f)
                if name in ('META','COST'):
                    x=fetch_filing_xbrl(client,c,f);identity,dei=annual_identity(x,t['identity']['annual_end'])
                    if t['identity']['accession'] and identity!=t['identity']:raise ValueError('Seed annual DEI differs from documented candidate')
                    row.update(identity=identity,annual_evidence=dei,instance_url=x.source_url)
                else:
                    # Existing verified body is reused; only metadata is acquired.
                    row['identity']=t['identity']
                row['status']='VERIFIED';row['reason']='Exact current official record selected under frozen cutoff; no historical receipt recovery.'
            except Exception as exc:
                row['reason']=type(exc).__name__+' in exact target selection/annual verification; no retry or plausible accession.'
            rows.append(row)
    for a in client.receipts:
        a['retrieval_mode']='new_authorized_fixed_income_binding_repair'
        a['refresh_history']='New receipt; original metadata gaps and prior candidates preserved.'
        encoded=a['response_body_gzip_base64'];a['response_body_gzip_base64']=[encoded[i:i+1024] for i in range(0,len(encoded),1024)]
    return dict(version='fixed-income-binding-repair-v1',baseline_revision=BASELINE,
        baseline_ledger_sha256=hashlib.sha256(pinned('docs/approved-income-integration-ledger.json')).hexdigest(),
        frozen_cutoff=cutoff().isoformat(),scope_count=20,request_count=len(client.attempts),
        rate_limit='Serial at most two starts/second; no automatic retries; independent targets continue.',
        attempts=[{k:v for k,v in a.items() if k!='reason'} for a in client.attempts],artifacts=client.receipts,rows=rows,selection=selection)


def verify(payload):
    groups=scope()
    if payload['baseline_revision']!=BASELINE or payload['frozen_cutoff']!=cutoff().isoformat() or payload['baseline_ledger_sha256']!=hashlib.sha256(pinned('docs/approved-income-integration-ledger.json')).hexdigest():raise ValueError('Frozen baseline/cutoff differs')
    if payload['scope_count']!=20 or len(payload['rows'])!=20 or payload['request_count']!=len(payload['attempts']):raise ValueError('Fixed scope/count differs')
    if len(payload['artifacts'])!=len([a for a in payload['attempts'] if a['http_status'] is not None]):raise ValueError('Response accounting differs')
    # Successful replay validates bytes/representation/time for accepted evidence;
    # failed responses remain receipts but are not promoted into identity proof.
    client=ReplayClient([a for a in payload['artifacts'] if a['http_status']==200])
    for a in payload['artifacts']:
        matches=[x for x in payload['attempts'] if x['source_url']==a['source_url'] and x['request_started_at_utc']==a['request_started_at_utc']]
        if len(matches)!=1 or matches[0]['http_status']!=a['http_status']:raise ValueError('Receipt/request metadata differs')
    allowed=set();offset=0;selection=[]
    for name,targets in groups.items():
        rr=payload['rows'][offset:offset+5];offset+=5
        if [r['target'] for r in rr]!=[t['identity'] for t in targets] or any(r['issuer']!=name for r in rr):raise ValueError('Exact target order differs')
        allowed.add(f"https://data.sec.gov/submissions/CIK{targets[0]['identity']['cik']:010d}.json")
        submissions_url=f"https://data.sec.gov/submissions/CIK{targets[0]['identity']['cik']:010d}.json"
        if submissions_url not in client.bodies:
            if any(r['status']=='VERIFIED' for r in rr):raise ValueError('Verified group lacks official submissions')
            continue
        c,by_end=selected_metadata(client,name,targets)
        selection.append(dict(issuer=name,selected_ends=list(by_end),frozen_ends=[r['identity']['annual_end'] for r in targets],
            complete_frozen_history_match=list(by_end)==[r['identity']['annual_end'] for r in targets]))
        for t,row in zip(targets,rr):
            candidate=by_end.get(t['identity']['annual_end'])
            if candidate is not None and name in ('META','COST'):
                directory=f"https://www.sec.gov/Archives/edgar/data/{c.cik}/{candidate.accession_number.replace('-','')}"
                allowed.update((directory+'/index.json',directory+'/'+_primary_document_stem(candidate.primary_document)+'_htm.xml'))
            if row['status']!='VERIFIED':
                if not row['reason']:raise ValueError('Unresolved reason missing')
                continue
            f=by_end[t['identity']['annual_end']];target_binding(t,f)
            if row['filing']!=filing_dict(f):raise ValueError('Official filing metadata binding differs')
            if name in ('META','COST'):
                directory=f"https://www.sec.gov/Archives/edgar/data/{c.cik}/{f.accession_number.replace('-','')}"
                allowed.update((directory+'/index.json',row['instance_url']))
                x=fetch_filing_xbrl(client,c,f);identity,dei=annual_identity(x,t['identity']['annual_end'])
                if identity!=row['identity'] or dei!=row['annual_evidence'] or x.source_url!=row['instance_url']:raise ValueError('Annual/instance replay differs')
            elif row['identity']!=t['identity']:raise ValueError('Approved metadata identity differs')
    # Supplemental metadata requests are limited to names listed by the four
    # successful official submissions responses and used by the existing loader.
    for a in payload['artifacts']:
        if a['source_url'].startswith('https://data.sec.gov/submissions/') and a['source_url'] in client.bodies:
            try:d=json.loads(body_of(a))
            except ValueError:continue
            if isinstance(d.get('filings'),dict):
                for f in d['filings'].get('files',[]):allowed.add('https://data.sec.gov/submissions/'+f['name'])
    if any(a['source_url'] not in allowed for a in payload['attempts']):raise ValueError('Out-of-scope request')
    if selection!=payload['selection']:raise ValueError('Frozen selection summary differs from actual replay')
    return dict(requests=payload['request_count'],verified=sum(r['status']=='VERIFIED' for r in payload['rows']),
        unresolved=sum(r['status']!='VERIFIED' for r in payload['rows']),statuses=dict(Counter(r['status'] for r in payload['rows'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    if args.acquire:print(json.dumps(acquire(),indent=2))
    else:print(json.dumps(verify(json.loads((ROOT/OUTPUT).read_text()))))
