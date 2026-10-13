"""Fixed retained NVDA five-period application, not an approval registry."""
import base64
from dataclasses import replace
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
from . import historical_inputs as h, retained_components as r, retained_income_preparation as income
from .cash_flow_inputs import _receipt

ROOT=Path(__file__).resolve().parents[3]
MANIFEST='docs/phase1-selected-filing-identity-manifest.json'
MANIFEST_SHA256='bed57b00ed024de7e631a4cbe5f9c6ea638e5d6fef2b56264a8ac908115e7ba0'
BODIES='docs/evidence/nvda-capex-response-bodies.json'
BODIES_SHA256='64ea48f91b7f4b5f545e638422f58d53c15e07a456ecb71b69b506beee08c591'
LIMITATIONS=('Only approved direct Revenue/EBIT observations inspected; twelve other contract families unassessed.',
    'Consolidated income statement R3.htm and original primary 10-K are not retained in this evidence set; no independent face-statement re-review.',
    'Evidence includes explicitly refreshed bodies from prior research; old unverifiable fingerprints are not recovered original receipts.',
    'No complete financial-input sufficiency, organic/perimeter comparability, timing or valuation-consumption approval.')


def pinned(path,digest):
    body=(ROOT/path).read_bytes()
    if hashlib.sha256(body).hexdigest()!=digest:raise h.InputError('Retained manifest changed: '+path)
    return json.loads(body)


def selections():
    rows=[(i,row) for i,row in enumerate(pinned(MANIFEST,MANIFEST_SHA256)['rows']) if row['ticker']=='NVDA']
    if len(rows)!=5 or any(row['cik']!=1045810 or row['status']!='VERIFIED_RETAINED_IDENTITY' for _,row in rows):
        raise h.InputError('Exactly five frozen verified NVDA selections required')
    return rows


def period(identity):
    return h.Period(identity['cik'],identity['accession'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']),identity['form'])


def inspect_period(row, artifacts):
    p=period(row['identity']);expected=row['candidates'][0]['artifacts'][0]
    refs=[a for a in artifacts if a['source_url']==expected['url']]
    receipts=();issues=[];metadata=None
    if len(refs)>1:raise h.InputError('Conflicting retained instance references')
    if refs:
        a=refs[0];metadata={k:v for k,v in a.items() if k!='response_body_gzip_base64'}
        if a['sha256']!=expected['sha256'] or a['accession']!=p.accession:raise h.InputError('Selected instance identity/fingerprint differs')
        if not a.get('retrieved_at_utc') or a.get('http_status')!=200 or not a.get('retrieval_mode'):
            issues.append('Retained original body receipt incomplete: timestamp/status/retrieval mode not established.')
        elif not a.get('response_body_gzip_base64'):
            issues.append('Retained instance body unavailable; metadata is not fact provenance.')
        else:
            if a.get('storage_encoding')!='gzip_base64':raise h.InputError('Retained encoding differs')
            receipts=(_receipt(a,gzip.decompress(base64.b64decode(a['response_body_gzip_base64'],validate=True))),)
    else:issues.append('Selected retained instance artifact unavailable.')
    evidence=r.prepare(p,receipts,(r.ArtifactBinding(expected['url'],expected['sha256'],'instance'),))
    if issues:evidence=replace(evidence,unresolved_requirements=evidence.unresolved_requirements+tuple(issues))
    results={f:income.inspect(evidence,f,LIMITATIONS) for f in income.POLICIES}
    return evidence,results,metadata


def build():
    artifacts=pinned(BODIES,BODIES_SHA256)['artifacts'];rows=[];annuals=[]
    for index,row in selections():
        evidence,results,metadata=inspect_period(row,artifacts)
        annuals.append(income.annual(evidence,results,LIMITATIONS));slots=[]
        for field,result in results.items():
            selected,reason=income.choose(result,field)
            slots.append(dict(field=field.value,status='POPULATED_REPORTED_DIRECT' if selected is not None else 'UNRESOLVED',
                selected=selected,selection_rationale=reason,unit='USD',scale=1,sign=1,
                role='reported_revenue' if field is h.Field.REVENUE else 'reported_operating_income',
                candidates=[] if result is None else [dict(namespace=c.namespace,concept=c.concept,value_usd=str(c.value),precision=c.precision,
                    occurrences=[o.__dict__ | dict(start=str(o.start),end=str(o.end),dimensions=list(o.dimensions)) for o in c.occurrences],
                    evidence_references=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                        locator=s.locator,representation=s.receipt.artifact.representation,digest_type=s.receipt.artifact.digest_type) for s in c.evidence_references]) for c in result.candidates],
                unresolved_requirements=list(evidence.unresolved_requirements+LIMITATIONS if result is None else result.unresolved_requirements)))
        rows.append(dict(identity=row['identity'],identity_reference=MANIFEST+'#/rows/'+str(index),source_reference=BODIES,
            retained_instance=metadata,fields=slots,other_field_families='UNASSESSED_UNAVAILABLE_NOT_SEARCHED'))
    history=h.HistoryBundle('retained-direct-income:NVDA',1,1045810,tuple(annuals),())
    ledger=dict(schema='retained-direct-income-candidate-ledger-v1',issuer='NVDA',selected_period_count=5,field_period_count=10,
        identity_manifest_sha256=MANIFEST_SHA256,retained_bodies_sha256=BODIES_SHA256,limitations=list(LIMITATIONS),rows=rows)
    return ledger,history


def load_history():return build()[1]
