"""Fixed 13-entry acquisition; offline replay default, original-body stdout log.

No filing selection, submissions fetch, notes, retry loop or broad discovery.
Source the external SEC configuration in the retrieval shell before --acquire.
"""
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
from dataclasses import replace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from acquire_selected_filing_identities import RecordingClient,body_of
from valuation_platform.analyst import historical_inputs as h,retained_components as r
from valuation_platform.analyst.nvda_income_inputs import period
from valuation_platform.analyst.cash_flow_inputs import _receipt

BASELINE='3bf319eda79b9c5e3e855f134ebb82d496cb004a'
BASELINE_LEDGER='docs/retained-income-batch-ledger.json'
MANIFEST='docs/phase1-selected-filing-identity-manifest.json'
OUTPUT='docs/evidence/retained-income-instance-acquisition.json'


def pinned(path):return subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT)


def scope():
    ledger=json.loads(pinned(BASELINE_LEDGER));manifest=json.loads(pinned(MANIFEST))
    rows=[row for row in ledger['rows'] if any(s['status']=='UNAVAILABLE' for s in row['fields'])]
    if len(rows)!=13 or Counter(row['issuer'] for row in rows)!=dict(AMZN=5,AVGO=5,AMAT=3):raise ValueError('Fixed missing-instance scope differs')
    for row in rows:
        if row['retained_source'] is not None or not all(s['status']=='UNAVAILABLE' and not s['candidates'] and
                any('Missing retained instance body' in x for x in s['unresolved_requirements']) for s in row['fields']):
            raise ValueError('Unavailable cause differs from retained-instance absence')
        matches=[m for m in manifest['rows'] if m['ticker']==row['issuer'] and m['identity']==row['identity']]
        if len(matches)!=1 or matches[0]['status']!='VERIFIED_RETAINED_IDENTITY':raise ValueError('Frozen identity mismatch')
    return rows


def verify_instance(target,receipt):
    body=body_of(receipt);p=period(target['identity'])
    if receipt['source_url']!=target['expected_instance']['url']:raise ValueError('Exact instance URL differs')
    artifact=_receipt(dict(receipt,accession=p.accession),body)
    evidence=r.prepare(p,(artifact,),(r.ArtifactBinding(receipt['source_url'],receipt['sha256'],'instance'),))
    # Reuse established annual DEI/entity/form replay, without reselecting filings.
    # AVGO's existing reviewed annual-context identity uses the same exact rules.
    return dict(identity=target['identity'],instance_sha256=artifact.artifact.sha256,
        fact_count=len(evidence.facts),annual_dei=[dict(namespace=f.namespace,concept=f.concept,context_id=f.context_id,
        raw_value=f.raw_value) for f,_ in evidence.facts if f.namespace.startswith('http://xbrl.sec.gov/dei/') and
        f.concept in ('DocumentType','DocumentFiscalPeriodFocus','DocumentPeriodEndDate','DocumentFiscalYearFocus') and
        f.start==p.annual_start and f.end==p.annual_end and not f.dimensions])


def acquire():
    targets=scope();agent=os.environ.get('SEC_USER_AGENT','').strip()
    if not agent:raise ValueError('SEC_USER_AGENT unavailable; no requests permitted')
    client=RecordingClient(agent);rows=[];stopped=False
    for target in targets:
        row=dict(issuer=target['issuer'],identity=target['identity'],expected_instance=target['expected_instance'],
            status='UNRESOLVED',reason=None,verification=None)
        if stopped:row['reason']='Not requested after bounded acquisition failure.';rows.append(row);continue
        try:
            client.get_bytes(target['expected_instance']['url'])
            receipt=client.receipts[-1]
            receipt['retrieval_mode']='new_authorized_fixed_13_income_instance_acquisition'
            receipt['accession']=target['identity']['accession']
            receipt['prior_fingerprint']=target['expected_instance']['sha256']
            receipt['prior_fingerprint_status']='Historical claimed fingerprint; original body/receipt unavailable in baseline.'
            receipt['prior_comparison']='SAME_DIGEST' if receipt['sha256']==receipt['prior_fingerprint'] else 'DIFFERENT_DIGEST_NO_BYTE_EQUALITY_CLAIM'
            receipt['refresh_history']='New acquisition receipt, not recovered original metadata; prior inventory/ledger preserved.'
            row['verification']=verify_instance(target,receipt);row['status']='VERIFIED'
        except Exception as exc:
            row['reason']=type(exc).__name__+' during exact-instance acquisition/verification; fixed pass stopped.';stopped=True
        rows.append(row)
    return dict(version='fixed-13-income-instance-acquisition-v1',baseline_revision=BASELINE,
        baseline_ledger_sha256=hashlib.sha256(pinned(BASELINE_LEDGER)).hexdigest(),
        identity_manifest_sha256=hashlib.sha256(pinned(MANIFEST)).hexdigest(),scope_count=13,
        request_count=len(client.attempts),rate_limit='Serial at most two starts per second; zero automatic retries.',
        attempts=[{k:v for k,v in a.items() if k!='reason'} for a in client.attempts],artifacts=client.receipts,rows=rows)


def verify(payload):
    targets=scope()
    if payload['baseline_revision']!=BASELINE or payload['baseline_ledger_sha256']!=hashlib.sha256(pinned(BASELINE_LEDGER)).hexdigest():raise ValueError('Baseline differs')
    if payload['identity_manifest_sha256']!=hashlib.sha256(pinned(MANIFEST)).hexdigest():raise ValueError('Identity manifest differs')
    if payload['scope_count']!=13 or len(payload['rows'])!=13 or payload['request_count']!=len(payload['attempts']):raise ValueError('Scope/request count differs')
    if len({a['source_url'] for a in payload['artifacts']})!=len(payload['artifacts']) or len(payload['artifacts'])!=len([x for x in payload['attempts'] if x['http_status'] is not None]):raise ValueError('Artifact/response count differs')
    if [row['identity'] for row in payload['rows']]!=[t['identity'] for t in targets]:raise ValueError('Exact target order/identities differ')
    if any(a['source_url'] not in {t['expected_instance']['url'] for t in targets} for a in payload['attempts']):raise ValueError('Out-of-scope request')
    for target,row in zip(targets,payload['rows']):
        if row['issuer']!=target['issuer'] or row['expected_instance']!=target['expected_instance']:raise ValueError('Target label/reference differs')
        if row['status']!='VERIFIED':continue
        matches=[a for a in payload['artifacts'] if a['source_url']==target['expected_instance']['url']]
        if len(matches)!=1 or verify_instance(target,matches[0])!=row['verification']:raise ValueError('Offline identity/body verification differs')
        if matches[0]['prior_fingerprint']!=target['expected_instance']['sha256'] or 'unavailable' not in matches[0]['prior_fingerprint_status']:raise ValueError('Prior evidence history differs')
        attempts=[a for a in payload['attempts'] if a['source_url']==matches[0]['source_url']]
        if len(attempts)!=1 or attempts[0]['http_status']!=200 or attempts[0]['request_started_at_utc']!=matches[0]['request_started_at_utc']:raise ValueError('Receipt/request binding differs')
    return dict(requests=payload['request_count'],verified=sum(row['status']=='VERIFIED' for row in payload['rows']),
        unresolved=sum(row['status']!='VERIFIED' for row in payload['rows']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');args=parser.parse_args()
    if args.acquire:
        payload=acquire()
        # Storage chunks only; digests always identify original decoded response bytes.
        for a in payload['artifacts']:
            encoded=a['response_body_gzip_base64'];a['response_body_gzip_base64']=[encoded[i:i+1024] for i in range(0,len(encoded),1024)]
        print(json.dumps(payload,indent=2))
    else:print(json.dumps(verify(json.loads((ROOT/OUTPUT).read_text())),sort_keys=True))
