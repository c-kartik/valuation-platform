"""Fixed exact-primary acquisition for the selected preparation cohort; no crawl."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import statement_delivery as s
from acquire_selected_filing_identities import RecordingClient, body_of


def acquire(checkpoint):
    rows,_,errors=s.scope()
    targets=[r for r in rows if r['status']=='MISSING_PRIMARY']
    scope_hash=hashlib.sha256(s.canonical(targets).encode()).hexdigest()
    agent=os.environ.get('SEC_USER_AGENT','').strip()
    if not agent:raise ValueError('CONFIG_VARIABLE_EMPTY; no requests')
    if checkpoint.exists():
        payload=json.loads(checkpoint.read_text())
        if payload['targets']!=targets or payload['scope_sha256']!=scope_hash:raise ValueError('Exact committed identity/metadata scope changed')
    else:
        payload=dict(version='selected-preparation-primary-acquisition-v1',targets=targets,
            scope_sha256=scope_hash,rows=[],artifacts=[],attempts=[],request_count=0,
            retained_errors=errors,unresolved_metadata=[r for r in rows if r['status']=='METADATA_UNRESOLVED'],
            boundary='Only exact selected primary URLs; two starts/second, one attempt per target, no automatic retries. New receipts are not recovered original metadata.')
    client=RecordingClient(agent)
    for target in targets[len(payload['rows']):]:
        outcome=dict(ticker=target['ticker'],identity=target['identity'],url=target['url'],status='REQUEST_FAILED')
        try:
            raw=client.get_bytes(target['url'])
            outcome['status']='BODY_RETAINED_BINDING_UNVERIFIED'
            receipt=client.receipts[-1]
            record=dict(url=target['url'],body=raw)
            s.verify_primary(record,target['identity'])
            outcome['status']='PRIMARY_IDENTITY_VERIFIED'
        except Exception as exc:
            outcome['reason']=type(exc).__name__+': '+str(exc) if isinstance(exc,(ValueError,s.h.InputError)) else type(exc).__name__
        for receipt in client.receipts:
            receipt.update(accession=target['identity']['accession'] if receipt['source_url']==target['url'] else receipt.get('accession'),
                retrieval_mode='new_authorized_selected_primary_preparation_acquisition',
                refresh_history='New actual receipt; original bodies/fingerprints and metadata gaps preserved in their original collections.')
        payload['rows'].append(outcome)
        payload['artifacts']+=client.receipts;payload['attempts']+=client.attempts
        client.receipts=[];client.attempts=[]
        payload['request_count']=len(payload['attempts'])
        checkpoint.write_text(json.dumps(payload,sort_keys=True,indent=2)+'\n')
    return payload


def verify(payload):
    if len(payload['rows'])!=len(payload['targets']) or len({r['url'] for r in payload['targets']})!=len(payload['targets']):raise ValueError('Exact finite scope differs')
    if hashlib.sha256(s.canonical(payload['targets']).encode()).hexdigest()!=payload['scope_sha256']:raise ValueError('Target identity hash differs')
    if payload['request_count']!=len(payload['attempts']):raise ValueError('Request count differs')
    revalidated={r['url']:r for r in payload.get('retained_revalidation',[])}
    if len(revalidated)!=len(payload.get('retained_revalidation',[])):raise ValueError('Duplicate offline revalidation')
    accepted=0
    for target,row in zip(payload['targets'],payload['rows']):
        if (row['url'],row['identity'])!=(target['url'],target['identity']):raise ValueError('Source/target binding differs')
        artifacts=[r for r in payload['artifacts'] if r['source_url']==target['url']]
        if len(artifacts)>1:raise ValueError('Duplicate target request')
        review=revalidated.get(target['url'])
        if row['status']=='PRIMARY_IDENTITY_VERIFIED' or review is not None:
            if len(artifacts)!=1:raise ValueError('Receipt absent')
            raw=body_of(artifacts[0]);s.verify_primary(dict(body=raw),row['identity'])
            artifact=artifacts[0]
            if (artifact['representation'],artifact['digest_type'],artifact['http_status'])!=('sec_response_body_bytes','sha256_sec_response_body_bytes',200):raise ValueError('Original receipt representation/status differs')
            if review is not None and (review['identity'],review['sha256'],review['status'])!=(target['identity'],artifact['sha256'],'PRIMARY_IDENTITY_VERIFIED'):raise ValueError('Offline review identity/body differs')
            accepted+=1
    return dict(targets=len(payload['targets']),requests=payload['request_count'],
        verified=accepted,failed=len(payload['targets'])-accepted,
        initially_verified=sum(r['status']=='PRIMARY_IDENTITY_VERIFIED' for r in payload['rows']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--checkpoint',type=Path);parser.add_argument('--verify',type=Path);args=parser.parse_args()
    if args.verify:print(json.dumps(verify(json.loads(args.verify.read_text())),sort_keys=True))
    else:
        if args.checkpoint is None or args.checkpoint.resolve().is_relative_to(s.ROOT):raise ValueError('External checkpoint required')
        result=acquire(args.checkpoint);print(json.dumps(verify(result),sort_keys=True))
