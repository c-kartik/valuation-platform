"""Fixed 119-accession pass; resumable generated checkpoint, no automatic retries."""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from acquire_selected_filing_identities import RecordingClient,body_of
from acquire_retained_income_instances import verify_instance
from valuation_platform.sec.filing_xbrl import _parse_directory_names, _validate_basename

BASELINE='5d4f3808584a2712a054978420ca80bcbdb19c3f'
LEDGER='docs/retained-income-sweep-ledger.json'
MANIFEST='docs/phase1-selected-filing-identity-manifest.json'
OUTPUT='docs/evidence/income-sweep-backlog-acquisition.json'


def pinned(path):return subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT)


def scope():
    ledger=json.loads(pinned(LEDGER));manifest=json.loads(pinned(MANIFEST));targets=ledger['acquisition_backlog']
    if len(targets)!=119 or Counter(r['reasons'][0] for r in targets)!=dict(MISSING_RETAINED_BODY=96,MISSING_RECEIPT=23):
        raise ValueError('Fixed 96-body/23-receipt scope differs')
    if len({(r['identity']['cik'],r['identity']['accession']) for r in targets})!=119:raise ValueError('Duplicate target')
    for t in targets:
        matches=[r for r in manifest['rows'] if r['ticker']==t['issuer'] and r['identity']==t['identity']]
        if len(matches)!=1 or matches[0]['status']!='VERIFIED_RETAINED_IDENTITY':raise ValueError('Exact frozen identity differs')
        if t['issuer'] in ('META','COST','GE'):raise ValueError('Excluded acquisition target')
    return targets


def directory(t):
    i=t['identity'];return 'https://www.sec.gov/Archives/edgar/data/'+str(i['cik'])+'/'+i['accession'].replace('-','')


def instance_url(t,index_body):
    names=[_validate_basename(n,'instance') for n in _parse_directory_names(json.loads(index_body)) if n.endswith('_htm.xml')]
    if len(names)!=1:raise ValueError('Directory does not identify exactly one extracted instance; no plausible selection')
    return directory(t)+'/'+names[0]


def prior(t):
    ledger=json.loads(pinned(LEDGER));r=next(r for r in ledger['rows'] if r['identity']==t['identity'])
    source=r.get('retained_source');result=dict(required_artifact=t['required_artifact'],retained_source=source,
        original_metadata_status='Preserved; refresh is not recovered original metadata.')
    body=None
    if source:
        doc=json.loads(pinned(source['path']));a=doc['artifacts'][int(source['locator'].split('/')[-1])]
        encoded=a.get('response_body_gzip_base64')
        if encoded:
            if isinstance(encoded,list):encoded=''.join(encoded)
            body=gzip.decompress(base64.b64decode(encoded,validate=True))
            if hashlib.sha256(body).hexdigest()!=a['sha256']:raise ValueError('Prior body fingerprint differs')
    return result,body


def verification(t,receipt):
    url=receipt['source_url']
    if not url.startswith(directory(t)+'/') or not url.endswith('_htm.xml'):raise ValueError('Out-of-target instance')
    if t['required_artifact']['url'] and url!=t['required_artifact']['url']:raise ValueError('Exact selected URL differs')
    v=verify_instance(dict(identity=t['identity'],expected_instance=dict(url=url)),receipt)
    history,old=prior(t);new=body_of(receipt)
    comparison=('IDENTICAL_ORIGINAL_BYTES' if old==new else 'DIFFERENT_ORIGINAL_BYTES') if old is not None else 'PRIOR_BODY_UNAVAILABLE'
    return dict(identity_verification=v,prior_history=history,byte_comparison=comparison,
        prior_fingerprint_comparison=('SAME_DIGEST' if t['required_artifact']['sha256']==receipt['sha256'] else 'DIFFERENT_DIGEST')
            if t['required_artifact']['sha256'] else 'PRIOR_FINGERPRINT_UNAVAILABLE')


def verify(payload):
    targets=scope()
    if payload['baseline_revision']!=BASELINE or payload['baseline_ledger_sha256']!=hashlib.sha256(pinned(LEDGER)).hexdigest():raise ValueError('Baseline changed')
    if payload['identity_manifest_sha256']!=hashlib.sha256(pinned(MANIFEST)).hexdigest():raise ValueError('Manifest changed')
    if payload['scope_count']!=119 or payload['request_count']!=len(payload['attempts']):raise ValueError('Count mismatch')
    if len(payload['rows'])>119:raise ValueError('Out-of-scope rows')
    if len(payload['artifacts'])!=len([a for a in payload['attempts'] if a['http_status'] is not None]):raise ValueError('Missing response body')
    allowed={directory(t):t for t in targets[:len(payload['rows'])]}
    for attempt in payload['attempts']:
        base,name=attempt['source_url'].rsplit('/',1)
        if base not in allowed or (name!='index.json' and not name.endswith('_htm.xml')):raise ValueError('Out-of-scope request')
    for a in payload['artifacts']:
        if a['source_url'].rsplit('/',1)[0] not in allowed:raise ValueError('Out-of-scope response')
        attempts=[x for x in payload['attempts'] if x['source_url']==a['source_url'] and x['request_started_at_utc']==a['request_started_at_utc']]
        if len(attempts)!=1 or attempts[0]['http_status']!=a['http_status']:raise ValueError('Receipt/request mismatch')
        # Error responses are retained too, but are never accepted evidence.
        encoded=a['response_body_gzip_base64'];encoded=''.join(encoded) if isinstance(encoded,list) else encoded
        body=gzip.decompress(base64.b64decode(encoded,validate=True))
        if hashlib.sha256(body).hexdigest()!=a['sha256'] or len(body)!=a['byte_length']:raise ValueError('Response digest mismatch')
        if a['representation']!='sec_response_body_bytes' or a['digest_type']!='sha256_sec_response_body_bytes':raise ValueError('Wrong digest representation')
    for t,row in zip(targets,payload['rows']):
        if row['identity']!=t['identity'] or row['issuer']!=t['issuer']:raise ValueError('Target order differs')
        if row['status']!='VERIFIED':
            if not row['reason']:raise ValueError('Failure reason missing')
            continue
        matches=[a for a in payload['artifacts'] if a['source_url']==row['instance_url'] and a['http_status']==200]
        if len(matches)!=1 or verification(t,matches[0])!=row['verification']:raise ValueError('Offline identity/evidence differs')
        if t['required_artifact']['url'] is None:
            ix=[a for a in payload['artifacts'] if a['source_url']==directory(t)+'/index.json' and a['http_status']==200]
            if len(ix)!=1 or instance_url(t,body_of(ix[0]))!=row['instance_url']:raise ValueError('Directory binding differs')
    return dict(requests=payload['request_count'],verified=sum(r['status']=='VERIFIED' for r in payload['rows']),
        failed=sum(r['status']!='VERIFIED' for r in payload['rows']),unattempted=119-len(payload['rows']))


def acquire(checkpoint):
    targets=scope()
    agent=os.environ.get('SEC_USER_AGENT','').strip()
    if not agent:raise ValueError('Nonempty exported SEC_USER_AGENT required before requests')
    if checkpoint.exists():
        payload=json.loads(checkpoint.read_text());verify(payload)
    else:
        payload=dict(version='fixed-119-income-sweep-acquisition-v1',baseline_revision=BASELINE,
            baseline_ledger_sha256=hashlib.sha256(pinned(LEDGER)).hexdigest(),
            identity_manifest_sha256=hashlib.sha256(pinned(MANIFEST)).hexdigest(),scope_count=119,
            request_count=0,rate_limit='Serial at most two starts/second; zero automatic retries; completed failures not reattempted.',
            attempts=[],artifacts=[],rows=[])
    client=RecordingClient(agent)
    for t in targets[len(payload['rows']):]:
        row=dict(issuer=t['issuer'],identity=t['identity'],status='UNRESOLVED',instance_url=None,reason=None,verification=None)
        try:
            url=t['required_artifact']['url']
            if url is None:
                client.get_bytes(directory(t)+'/index.json')
                url=instance_url(t,body_of(client.receipts[-1]))
            row['instance_url']=url;client.get_bytes(url)
            receipt=client.receipts[-1];receipt['accession']=t['identity']['accession']
            receipt['retrieval_mode']='new_authorized_fixed_119_income_sweep_refresh'
            receipt['refresh_history']='Explicit new receipt; prior artifact/metadata gap preserved, not recovered.'
            row['verification']=verification(t,receipt);row['status']='VERIFIED'
        except Exception as exc:
            row['reason']=type(exc).__name__+' in exact-target acquisition/identity verification; no automatic retry.'
        payload['rows'].append(row)
        payload['attempts'].extend({k:v for k,v in a.items() if k!='reason'} for a in client.attempts)
        for a in client.receipts:
            encoded=a['response_body_gzip_base64'];a['response_body_gzip_base64']=[encoded[i:i+1024] for i in range(0,len(encoded),1024)]
            payload['artifacts'].append(a)
        client.attempts.clear();client.receipts.clear();payload['request_count']=len(payload['attempts'])
        # Generated resumable receipt log, outside the repository; no source edit.
        tmp=checkpoint.with_suffix('.tmp');tmp.write_text(json.dumps(payload,indent=2));tmp.replace(checkpoint)
        if len(payload['rows'])%10==0:print('Completed targets:',len(payload['rows']),flush=True)
    print(json.dumps(verify(payload)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--acquire',action='store_true');p.add_argument('--checkpoint',type=Path,default=Path('/tmp/income-sweep-119-checkpoint.json'));args=p.parse_args()
    if args.acquire:acquire(args.checkpoint)
    else:print(json.dumps(verify(json.loads((ROOT/OUTPUT).read_text()))))
