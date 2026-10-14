"""Exact negative preparation dispositions, never financial approvals/fallbacks."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
from . import historical_inputs as h

ROOT=Path(__file__).resolve().parents[3]
RECORD='docs/d-and-a-independent-scope-dispositions.json'
RECORD_SHA256='163210d61119ed1b0d43ce93d39234892030a22c41e18bf3a24afb0f7f88575a'

def entries():
    raw=(ROOT/RECORD).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RECORD_SHA256:raise h.InputError('Changed version-1 negative scope review')
    doc=json.loads(raw)
    if doc['version']!=1:raise h.InputError('Unsupported negative scope review version')
    return doc['entries']

def disposition(period,concept,value):
    found=[r for r in entries() if r['accession']==period.accession]
    if not found:return None
    if len(found)!=1:raise h.InputError('Conflicting negative scope records')
    r=found[0]
    if (r['cik'],r['annual_start'],r['annual_end'],r['concept'],r['value_usd'])!=(period.cik,str(period.annual_start),str(period.annual_end),concept,str(value)):
        raise h.InputError('Negative scope review identity/value mismatch; required input blocked')
    doc=json.loads((ROOT/r['path']).read_text());items=doc if isinstance(doc,list) else doc['artifacts']
    item=items[r['artifact_index']]
    if (item['source_url'],item['sha256'],item['representation'],item['digest_type'])!=(r['url'],r['sha256'],'sec_response_body_bytes','sha256_sec_response_body_bytes'):
        raise h.InputError('Negative scope statement artifact binding differs')
    encoded=item.get('response_body_gzip_base64') or item.get('body_gzip_base64')
    body=gzip.decompress(base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded,validate=True))
    if hashlib.sha256(body).hexdigest()!=r['sha256']:raise h.InputError('Tampered negative scope statement')
    from .cash_interest_annotations import _text
    text=_text(body)
    if not all(p in text for p in r['required_text']):raise h.InputError('Negative scope reviewed passage differs')
    return r
