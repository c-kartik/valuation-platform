"""Acquire only ten committed independent-validation primary document targets."""
import argparse
import json
import os
from pathlib import Path
import sys
import subprocess
import base64
import gzip
import hashlib
import re
from datetime import datetime

def verify(payload):
    targets=scope()
    if payload['targets']!=targets or payload['request_count']!=10:raise ValueError('Exact acquisition scope/count differs')
    verified=[]
    for t in targets:
        records=[a for a in payload['artifacts'] if a['source_url']==t['source_url']]
        if len(records)!=1:raise ValueError('Exact target receipt unavailable/conflicting')
        a=records[0]
        if (a['accession'],a['representation'],a['digest_type'],a['http_status'])!=(t['accession'],'sec_response_body_bytes','sha256_sec_response_body_bytes',200):
            raise ValueError('Artifact receipt identity/representation/status differs')
        stamp=datetime.fromisoformat(a['retrieved_at_utc'])
        if stamp.utcoffset().total_seconds()!=0:raise ValueError('UTC receipt required')
        body=gzip.decompress(base64.b64decode(a['response_body_gzip_base64'],validate=True))
        if hashlib.sha256(body).hexdigest()!=a['sha256'] or len(body)!=a['byte_length']:raise ValueError('Body digest/length differs')
        text=body.decode()
        def dei(concept):
            match=re.search(r'<ix:nonNumeric[^>]*name="dei:'+concept+r'"[^>]*>(.*?)</ix:nonNumeric>',text,re.S|re.I)
            if not match:raise ValueError('Exact primary DEI missing')
            return match,re.sub('<[^>]+>','',match.group(1)).strip()
        if int(dei('EntityCentralIndexKey')[1])!=t['cik'] or dei('DocumentType')[1]!='10-K':raise ValueError('Primary CIK/form differs')
        end=dei('DocumentPeriodEndDate')[0]
        context=re.search(r'contextRef="([^"]+)"',end.group(),re.I).group(1)
        c=re.search(r'<xbrli:context[^>]*id="'+re.escape(context)+r'".*?</xbrli:context>',text,re.S|re.I)
        if not c:raise ValueError('Primary annual DEI context missing')
        start=re.search(r'<xbrli:startDate>([^<]+)',c.group());finish=re.search(r'<xbrli:endDate>([^<]+)',c.group())
        if not start or not finish or (start.group(1),finish.group(1))!=(t['annual_start'],t['annual_end']):raise ValueError('Primary DEI annual dates differ')
        verified.append(dict(ticker=t['ticker'],accession=t['accession'],sha256=a['sha256'],
            primary_dei_context=context,annual_start=start.group(1),annual_end=finish.group(1),
            depth='Primary DEI CIK/form/annual context; fact semantics/statement scope independently reviewed separately.'))
    return verified
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from acquire_selected_filing_identities import RecordingClient
from valuation_platform.analyst import preparation_validation as v

BASELINE='c96fadacaee4e01c35d3e1c3334933565eca20da'
OUTPUT='docs/evidence/independent-validation-document-acquisition.json'

def scope():
    backlog=json.loads(subprocess.check_output(['git','show',BASELINE+':docs/preparation-independent-results.json'],cwd=ROOT))['artifact_backlog']
    # Only the committed ten primary targets, never discovered report URLs.
    targets=[dict(ticker=x['ticker'],accession=x['accession'],annual_start=x['annual_start'],
        annual_end=x['annual_end'],source_url=x['required_artifact_url'],references=x['primary_metadata_references']) for x in backlog]
    identities={r['identity']['accession']:r['identity'] for r in json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())['rows']}
    refs=v.primary_references()
    if len(targets)!=10 or len({t['source_url'] for t in targets})!=10:raise ValueError('Fixed ten-target scope differs')
    for t in targets:
        p=identities[t['accession']]
        names={r['filename'] for r in refs[t['accession']]}
        if len(names)!=1:raise ValueError('Primary identity not unique')
        expected='https://www.sec.gov/Archives/edgar/data/'+str(p['cik'])+'/'+p['accession'].replace('-','')+'/'+next(iter(names))
        if (t['source_url'],t['annual_start'],t['annual_end'])!=(expected,p['annual_start'],p['annual_end']):raise ValueError('Exact primary/annual binding differs')
        t['cik']=p['cik'];t['form']=p['form']
    return targets

def acquire(checkpoint):
    targets=scope();agent=os.environ.get('SEC_USER_AGENT','').strip()
    if not agent:raise ValueError('Nonempty external SEC configuration required; no requests')
    client=RecordingClient(agent);rows=[]
    payload=dict(version='independent-primary-acquisition-v1',baseline_revision=BASELINE,targets=targets,
        request_count=0,attempts=[],artifacts=[],rows=rows,
        limits='Only exact ten URLs; serial two starts/second maximum; one attempt each, no retry; preserve prior evidence.')
    for t in targets:
        row=dict(target=t,status='REQUEST_FAILED')
        try:
            body=client.get_bytes(t['source_url'])
            if b'<html' not in body.lower():raise ValueError('Non-HTML response')
            row['status']='BODY_RETAINED_PENDING_INDEPENDENT_REVIEW'
        except Exception as exc:row['reason']=type(exc).__name__+'; exact target not retried.'
        for artifact in client.receipts:
            if artifact['source_url']==t['source_url']:
                artifact.update(accession=t['accession'],retrieval_mode='new_authorized_independent_primary_acquisition',
                    refresh_history='New actual receipt, not recovered original metadata; no previous artifact overwritten.')
        rows.append(row);payload.update(request_count=len(client.attempts),
            attempts=[{k:v for k,v in x.items() if k!='reason'} for x in client.attempts],artifacts=client.receipts)
        checkpoint.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n')
    return payload

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True);args=p.parse_args()
    if args.checkpoint.exists() or args.checkpoint.resolve().is_relative_to(ROOT):raise ValueError('New external checkpoint required')
    result=acquire(args.checkpoint)
    print(json.dumps(dict(requests=result['request_count'],retained=len(result['artifacts']),
        failures=sum(r['status']=='REQUEST_FAILED' for r in result['rows']))))
