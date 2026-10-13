"""One fixed retained-only batch; shared inspection/packaging, no issuer policies."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from . import historical_inputs as h, retained_income_preparation as income
from . import nvda_income_inputs as shared

ISSUERS=('AMZN','AVGO','CSCO','KO','HD','NFLX','PLTR','AMAT')
SOURCES={
    'docs/evidence/hd-capex-response-bodies.json':'06e9158e4b8001345eb18da7e787da56739bd0a59f0f512470c1260e9b6bd96f',
    'docs/evidence/selected-filing-identity-acquisition.json':'d1501453dac98f540064d1f689c4c37186f8e8a8b1d525e3344faeb5bbef49e7',
    'tests/fixtures/capex_amzn_response_bodies.json':'7cd3c480d9afb1fca1f858d40a40389d7e7dab921518b191a9fb8c4f29db1650'}
LIMITATIONS=('Only approved direct Revenue/EBIT candidates inspected; twelve other contract families unassessed, not searched.',
    'No independent consolidated face-statement or primary-filing re-review; original instance evidence only where retained and receipted.',
    'Absent retained evidence is not proof of unavailable financial disclosure; extracts/fingerprints cannot replace original bodies/receipts.',
    'No organic/perimeter comparability, complete financial-input sufficiency, timing or valuation approval.')


def selections():
    manifest=shared.pinned(shared.MANIFEST,shared.MANIFEST_SHA256)
    return [(i,row) for name in ISSUERS for i,row in enumerate(manifest['rows']) if row['ticker']==name]


def catalog():
    refs=[]
    for path,digest in SOURCES.items():
        doc=shared.pinned(path,digest);rows=doc if isinstance(doc,list) else doc['artifacts']
        for i,a in enumerate(rows):
            refs.append((path,i,a))
    return refs


def instance_reference(row):
    refs=[a for c in row['candidates'] for a in c['artifacts'] if str(a.get('url',a.get('source_url',''))).endswith('_htm.xml')]
    identities={(a.get('url',a.get('source_url')),a['sha256']) for a in refs}
    if len(identities)!=1:raise h.InputError('Frozen selection has missing/conflicting exact instance references')
    url,digest=next(iter(identities));return dict(url=url,sha256=digest)


def inspect_row(row,refs):
    expected=instance_reference(row)
    matches=[(path,i,a) for path,i,a in refs if a.get('source_url')==expected['url']]
    if len(matches)>1:raise h.InputError('Conflicting source catalog bindings; no silent precedence')
    bound=[];source=None
    if matches:
        path,index,a=matches[0]
        source=dict(path=path,locator='/artifacts/'+str(index),repository_sha256=SOURCES[path],
            original_metadata={k:v for k,v in a.items() if 'base64' not in k},
            accession_binding='Exact frozen identity and selected-accession artifact URL, not invented retrieval metadata')
        # Acquisition receipts lack a redundant accession field; exact URL/identity
        # binds it explicitly. All actual retrieval/representation fields stay intact.
        bound=[dict(a,accession=row['identity']['accession'])]
    proxy=dict(row,candidates=[dict(artifacts=[expected])])
    evidence,results,metadata=shared.inspect_period(proxy,bound,LIMITATIONS)
    return evidence,results,source


def slot(field,result,evidence):
    selected,reason=income.choose(result,field)
    status='POPULATED' if selected is not None else 'CONFLICTING' if result and result.competing_values else 'UNAVAILABLE'
    return dict(field=field.value,status=status,origin='reported' if selected is not None else 'unavailable',selected=selected,
        selection_rationale=reason,unit='USD',scale=1,sign=1,scope='approved_direct_annual_only',completeness='partial' if selected is not None else 'unknown',
        candidates=[] if result is None else [dict(namespace=c.namespace,concept=c.concept,value_usd=str(c.value),precision=c.precision,
            occurrences=[o.__dict__ | dict(start=str(o.start),end=str(o.end),dimensions=list(o.dimensions)) for o in c.occurrences],
            source_references=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                representation=s.receipt.artifact.representation,digest_type=s.receipt.artifact.digest_type,locator=s.locator) for s in c.evidence_references]) for c in result.candidates],
        unresolved_requirements=list(evidence.unresolved_requirements+LIMITATIONS if result is None else result.unresolved_requirements))


def build():
    refs=catalog();selected=selections();rows=[];annuals={name:[] for name in ISSUERS};summary={}
    for index,row in selected:
        evidence,results,source=inspect_row(row,refs)
        annuals[row['ticker']].append(income.annual(evidence,results,LIMITATIONS))
        rows.append(dict(issuer=row['ticker'],identity=row['identity'],identity_reference=shared.MANIFEST+'#/rows/'+str(index),
            expected_instance=instance_reference(row),retained_source=source,
            fields=[slot(f,result,evidence) for f,result in results.items()],other_families='UNASSESSED_UNAVAILABLE_NOT_SEARCHED'))
    histories={}
    for name in ISSUERS:
        aa=tuple(sorted(annuals[name],key=lambda a:a.period.annual_end))
        if not aa:raise h.InputError('No frozen issuer identity; do not invent history')
        histories[name]=h.HistoryBundle('retained-direct-income:'+name,1,aa[0].period.cik,aa,
            () if len(aa)==5 else ('Only '+str(len(aa))+' frozen selections exist; absent target years are not fabricated.',))
        counts=Counter(f['status'] for row in rows if row['issuer']==name for f in row['fields'])
        summary[name]=dict(selected_periods=len(aa),slots=2*len(aa),populated=counts['POPULATED'],conflicting=counts['CONFLICTING'],unavailable=counts['UNAVAILABLE'])
    ledger=dict(schema='retained-income-batch-ledger-v1',scope=list(ISSUERS),identity_manifest_sha256=shared.MANIFEST_SHA256,
        retained_source_manifest_sha256=SOURCES,limitations=list(LIMITATIONS),selected_periods=len(rows),field_period_slots=2*len(rows),summary=summary,rows=rows)
    return ledger,histories
