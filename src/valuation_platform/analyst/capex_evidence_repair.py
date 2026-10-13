"""Fixed original-byte binding repair; never a new Capex approval."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from . import historical_inputs as h, retained_capex as capex, nvda_income_inputs as shared

BASELINE='231dfa15d2844b36a8e5b087baa2655de30ca0d3'
LEDGER='docs/retained-capex-ledger.json'
OUTPUT='docs/evidence/capex-binding-repair.json'


def pinned(path):return subprocess.check_output(['git','show',BASELINE+':'+path],cwd=shared.ROOT)


def scope():
    ledger=json.loads(pinned(LEDGER));targets=[];entries=[]
    for row in ledger['rows']:
        if not row['approved_entry_evidence_gaps']:continue
        matches=[(p,e) for p in capex.curated.CAPEX_SCOPE_POLICY_CATALOG.policies for e in p.entries
            if (e.company_cik,e.accession_number,str(e.annual_start),str(e.annual_end))==
                (row['identity']['cik'],row['identity']['accession'],row['identity']['annual_start'],row['identity']['annual_end'])]
        if len(matches)!=1:raise h.InputError('Exact approved entry mismatch')
        policy,entry=matches[0];entries.append(row['identity'])
        for gap in row['approved_entry_evidence_gaps']:
            if (gap['url'],gap['sha256']) not in entry.artifact_digests:raise h.InputError('Requirement not registered')
            targets.append(dict(issuer=row['issuer'],identity=row['identity'],policy_version=policy.version,
                source_url=gap['url'],sha256=gap['sha256'],representation='sec_response_body_bytes',
                digest_type='sha256_sec_response_body_bytes',prior_requirement=gap))
    if len(entries)!=15 or len(targets)!=85 or len({t['source_url'] for t in targets})!=85:
        raise h.InputError('Fixed 15-entry / 85-artifact scope mismatch')
    return targets


def body(record):
    if record.get('representation')!='sec_response_body_bytes' or record.get('digest_type')!='sha256_sec_response_body_bytes':
        raise h.InputError('Unsupported original-byte representation')
    encoded=record.get('response_body_gzip_base64') or record.get('body_gzip_base64')
    if encoded:
        if isinstance(encoded,list):encoded=''.join(encoded)
        raw=gzip.decompress(base64.b64decode(encoded,validate=True))
    elif record.get('response_body_base64'):raw=base64.b64decode(record['response_body_base64'],validate=True)
    elif record.get('body_base64'):raw=base64.b64decode(record['body_base64'],validate=True)
    else:raise h.InputError('Original body unavailable')
    if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise h.InputError('Retained declared body digest differs')
    if record.get('byte_length') is not None and len(raw)!=record['byte_length']:raise h.InputError('Retained length differs')
    return raw


def local_search(targets):
    """Bounded committed JSON + explicitly referenced retained-file paths only."""
    wanted={t['source_url']:t for t in targets};matches={};issues=[];checked_paths=set()
    files=subprocess.check_output(['git','ls-files','*.json'],cwd=shared.ROOT,text=True).splitlines()
    def visit(node,path,pointer,parent=None):
        if isinstance(node,dict):
            url=node.get('source_url') or node.get('url')
            if url in wanted:
                t=wanted[url];digest=node.get('sha256') or node.get('response_digest')
                representation=node.get('representation');kind=node.get('digest_type')
                if representation=='sec_response_body_bytes' and kind=='sha256_sec_response_body_bytes':
                    raw=None;origin=None
                    try:
                        raw=body(node);origin=dict(path=path,locator=pointer)
                    except h.InputError:
                        for key in ('retained_path','retained_path_at_review','original_retained_path','retained_cache_path'):
                            ref=node.get(key)
                            if not ref:continue
                            checked_paths.add(ref);p=Path(ref)
                            if p.is_file():
                                candidate=p.read_bytes()
                                if hashlib.sha256(candidate).hexdigest()==digest:
                                    raw=candidate;origin=dict(path=path,locator=pointer,retained_file=ref);break
                    if raw is not None and hashlib.sha256(raw).hexdigest()==t['sha256']:
                        receipt_parent=parent if isinstance(parent,dict) and parent.get('artifact') is node else {}
                        meta={k:node.get(k,receipt_parent.get(k)) for k in ('retrieved_at_utc','http_status','retrieval_mode')}
                        matches.setdefault(url,dict(source_url=url,sha256=t['sha256'],representation=representation,digest_type=kind,
                            byte_length=len(raw),storage_encoding='gzip_base64',response_body_gzip_base64=base64.b64encode(gzip.compress(raw,mtime=0)).decode(),
                            **meta,local_source=dict(origin,document_sha256=hashlib.sha256((shared.ROOT/path).read_bytes()).hexdigest()),
                            evidence_history='Verified retained original body reused; unavailable original retrieval metadata remains unknown.'))
                    elif digest==t['sha256']:
                        issues.append(dict(source_url=url,path=path,locator=pointer,reason='Declared matching raw fingerprint but original body/path unavailable.'))
            for key,value in node.items():visit(value,path,pointer+'/'+key,node)
        elif isinstance(node,list):
            for i,value in enumerate(node):visit(value,path,pointer+'/'+str(i),parent)
    for path in files:visit(json.loads((shared.ROOT/path).read_bytes()),path,'')
    return dict(matches=matches,issues=issues,searched_json_files=len(files),explicit_retained_paths_checked=sorted(checked_paths))


def verify(payload):
    targets=scope()
    if payload.get('version')!='fixed-capex-binding-repair-v1':raise h.InputError('Unsupported repair version')
    if payload['baseline_revision']!=BASELINE or payload['baseline_ledger_sha256']!=hashlib.sha256(pinned(LEDGER)).hexdigest():raise h.InputError('Baseline binding changed')
    if payload['targets']!=targets or len(payload['rows'])!=85:raise h.InputError('Fixed scope/rows differ')
    attempts=payload['attempts'];artifacts=payload['artifacts']
    if payload['request_count']!=len(attempts) or len({a['source_url'] for a in attempts})!=len(attempts):raise h.InputError('Request count/duplicate attempt differs')
    if any(a['source_url'] not in {t['source_url'] for t in targets} for a in attempts):raise h.InputError('Out of scope request')
    if len(artifacts)!=sum(a['http_status'] is not None for a in attempts):raise h.InputError('Response/attempt counts differ')
    for a in artifacts:
        raw=body(a)
        aa=[v for v in attempts if v['source_url']==a['source_url'] and v['request_started_at_utc']==a['request_started_at_utc']]
        if len(aa)!=1 or aa[0]['http_status']!=a['http_status']:raise h.InputError('Actual request/receipt binding differs')
        target=next(t for t in targets if t['source_url']==a['source_url'])
        if a['prior_expected_sha256']!=target['sha256'] or a['accession']!=target['identity']['accession']:
            raise h.InputError('Prior fingerprint/accession history differs')
        from datetime import datetime, timezone
        if datetime.fromisoformat(a['retrieved_at_utc']).utcoffset()!=timezone.utc.utcoffset(None):raise h.InputError('Actual UTC metadata required')
        if a['refresh_history']!='New receipt, not recovered original metadata; immutable prior fingerprint retained.':raise h.InputError('Refresh history lost')
    accepted={}
    for t,row in zip(targets,payload['rows']):
        if row['target']!=t:raise h.InputError('Target order/entry differs')
        if row['status']=='REUSED_LOCAL':
            a=payload['local_search']['matches'][t['source_url']];raw=body(a)
            ref=a['local_source'];p=shared.ROOT/ref['path']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=ref['document_sha256']:raise h.InputError('Local source document changed')
            original=json.loads(p.read_bytes());parent=None
            for key in ref['locator'].strip('/').split('/'):
                if not key:continue
                parent=original;original=original[int(key)] if isinstance(original,list) else original[key]
            receipt_parent=parent if isinstance(parent,dict) and parent.get('artifact') is original else {}
            for key in ('retrieved_at_utc','http_status','retrieval_mode'):
                if a.get(key)!=original.get(key,receipt_parent.get(key)):raise h.InputError('Local metadata does not bind source record')
            if not ref.get('retained_file') and body(original)!=raw:raise h.InputError('Local body does not bind source record')
            if ref.get('retained_file') and Path(ref['retained_file']).read_bytes()!=raw:raise h.InputError('Retained file bytes changed')
        else:
            aa=[a for a in artifacts if a['source_url']==t['source_url']]
            if row['status']=='REQUEST_FAILED':
                if not row['reason']:raise h.InputError('Explicit failure required')
                if any(a['http_status']==200 for a in aa):raise h.InputError('Successful response cannot be hidden as failed')
                continue
            if len(aa)!=1:raise h.InputError('One actual refreshed artifact required')
            a=aa[0];raw=body(a)
            expected='VERIFIED_REFRESH' if a['http_status']==200 and a['sha256']==t['sha256'] else 'BYTE_MISMATCH' if a['http_status']==200 else 'REQUEST_FAILED'
            if row['status']!=expected:raise h.InputError('Receipt cannot satisfy registered bytes/status')
        if row['status'] in ('REUSED_LOCAL','VERIFIED_REFRESH'):
            if hashlib.sha256(raw).hexdigest()!=t['sha256']:raise h.InputError('Immutable required hash mismatch')
            accepted[t['source_url'],t['sha256']]=(raw,dict(source_url=t['source_url'],sha256=t['sha256'],
                representation=t['representation'],digest_type=t['digest_type'],retrieved_at_utc=a.get('retrieved_at_utc'),
                http_status=a.get('http_status'),evidence_history=a['evidence_history'] if row['status']=='REUSED_LOCAL' else a['refresh_history'],
                path=OUTPUT,locator='/local_search/matches/'+t['source_url'] if row['status']=='REUSED_LOCAL' else '/artifacts/'+str(artifacts.index(a)),
                document_sha256=hashlib.sha256((shared.ROOT/OUTPUT).read_bytes()).hexdigest() if (shared.ROOT/OUTPUT).exists() else None))
    return accepted


def build():
    """Add verified bodies to the old store; replay only the fixed 15 entries."""
    from collections import Counter
    from dataclasses import replace
    from . import retained_cfo_preparation as cfo
    payload=json.loads((shared.ROOT/OUTPUT).read_text());accepted=verify(payload)
    old,histories=capex.build();ledger=json.loads(json.dumps(old));store=capex.artifacts()
    for key,value in accepted.items():store.setdefault(key,value)
    target_keys={(t['identity']['cik'],t['identity']['accession']) for t in scope()}
    for row in ledger['rows']:
        identity=row['identity'];key=(identity['cik'],identity['accession'])
        if key not in target_keys:continue
        history=histories[row['issuer']];annual=next(a for a in history.annuals if (a.period.cik,a.period.accession)==key)
        value,replay=capex.package(cfo.prepare(annual),store)
        annual=replace(annual,inputs=tuple(value if v.field is h.Field.CAPEX else v for v in annual.inputs))
        histories[row['issuer']]=replace(history,annuals=tuple(annual if a.period==annual.period else a for a in history.annuals))
        row.update(replay)
        row['binding_repair']=dict(source=OUTPUT,status_counts=dict(Counter(r['status'] for r in payload['rows'] if r['target']['identity']==identity)),
            limitations='Only matching registered raw bodies accepted; mismatches do not authorize hash/scope changes.')
    ledger.update(schema='repaired-retained-capex-v1',outcomes=dict(Counter(r['status'] for r in ledger['rows'])),
        curated_versions=dict(Counter(r['policy'].get('version') for r in ledger['rows'] if r['status']=='CURATED')),
        summary={n:dict(periods=len(hist.annuals),outcomes=dict(Counter(r['status'] for r in ledger['rows'] if r['issuer']==n))) for n,hist in histories.items()},
        binding_repair=dict(verified_requirements=len(accepted),requests=payload['request_count'],
            outcome_counts=dict(Counter(r['status'] for r in payload['rows'])),baseline_ledger_sha256=payload['baseline_ledger_sha256']))
    return ledger,histories


def validate_history(serialized):
    from . import retained_cfo_preparation as cfo
    from . import pilot_historical_inputs as pilot
    history=h.deserialize(serialized);accepted=verify(json.loads((shared.ROOT/OUTPUT).read_text()));store=capex.artifacts()
    for key,value in accepted.items():store.setdefault(key,value)
    pilots={a.period:a for n in ('MSFT','AAPL','GOOGL') for a in pilot.load_history(n).annuals}
    for annual in history.annuals:
        actual=next(v for v in annual.inputs if v.field is h.Field.CAPEX)
        expected=(next(v for v in pilots[annual.period].inputs if v.field is h.Field.CAPEX) if annual.period in pilots else capex.package(cfo.prepare(annual),store)[0])
        if actual!=expected:raise h.InputError('Repaired policy/source/value serialization differs from independent replay')
    return history
