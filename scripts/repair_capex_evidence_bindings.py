"""Fixed 85 artifact pass: local search first, at most one request per missing URL."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from valuation_platform.analyst import capex_evidence_repair as repair
from acquire_selected_filing_identities import RecordingClient


def acquire(checkpoint):
    targets=repair.scope();local=repair.local_search(targets)
    agent=os.environ.get('SEC_USER_AGENT','').strip()
    if not agent:raise ValueError('Configuration variable empty; no requests')
    client=RecordingClient(agent);rows=[]
    payload=dict(version='fixed-capex-binding-repair-v1',baseline_revision=repair.BASELINE,
        baseline_ledger_sha256=hashlib.sha256(repair.pinned(repair.LEDGER)).hexdigest(),targets=targets,local_search=local,
        request_count=0,attempts=client.attempts,artifacts=client.receipts,rows=rows,
        limits='Serial at most two starts/second; one attempt per missing URL; zero automatic retries; independent targets continue.')
    for t in targets:
        row=dict(target=t,status='REQUEST_FAILED',reason=None)
        if t['source_url'] in local['matches']:row.update(status='REUSED_LOCAL',reason='Existing original body and registered digest verified.')
        else:
            try:
                client.get_bytes(t['source_url'])
                a=client.receipts[-1];row.update(status='VERIFIED_REFRESH' if a['sha256']==t['sha256'] else 'BYTE_MISMATCH',
                    reason='Registered original bytes verified with new receipt.' if a['sha256']==t['sha256'] else 'New bytes differ; registry unchanged, no automatic refresh approval.')
            except Exception as exc:row['reason']=type(exc).__name__+' for exact target; no automatic retry.'
            for a in client.receipts:
                if a['source_url']==t['source_url']:
                    a.update(retrieval_mode='new_authorized_fixed_capex_binding_repair',accession=t['identity']['accession'],
                        prior_expected_sha256=t['sha256'],refresh_history='New receipt, not recovered original metadata; immutable prior fingerprint retained.')
        rows.append(row);payload['request_count']=len(client.attempts)
        payload['attempts']=[{k:v for k,v in a.items() if k!='reason'} for a in client.attempts]
        # Generated checkpoint outside repository, preserving every attempted response.
        checkpoint.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    return payload


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--acquire',action='store_true');p.add_argument('--checkpoint',type=Path);args=p.parse_args()
    if args.acquire:
        if args.checkpoint is None or args.checkpoint.resolve().is_relative_to(ROOT):raise ValueError('External checkpoint required')
        if args.checkpoint.exists():raise ValueError('Existing checkpoint not overwritten/retried')
        x=acquire(args.checkpoint)
        print(json.dumps(dict(requests=x['request_count'],reused=len(x['local_search']['matches']),
            verified=sum(r['status']=='VERIFIED_REFRESH' for r in x['rows']),mismatched=sum(r['status']=='BYTE_MISMATCH' for r in x['rows']),
            failed=sum(r['status']=='REQUEST_FAILED' for r in x['rows'])),sort_keys=True))
    else:
        x=json.loads((ROOT/repair.OUTPUT).read_text());print(json.dumps(dict(verified=len(repair.verify(x)),requests=x['request_count']),sort_keys=True))
