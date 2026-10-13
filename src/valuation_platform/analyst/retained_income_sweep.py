"""Offline universe sweep. Inspection is not financial acceptance or sufficiency."""
from collections import Counter
import base64
import gzip
import hashlib
import json
from . import historical_inputs as h, retained_income_batch as batch
from . import nvda_income_inputs as shared, retained_income_preparation as income
from . import pilot_historical_inputs as pilot

CLASSIFICATIONS='docs/universe/phase-1h5-issuer-validation.json'
CATALOG='docs/retained-income-sweep-sources.json'
LIMITATIONS=batch.LIMITATIONS


def sources():
    config=json.loads((shared.ROOT/CATALOG).read_text())
    refs=[]
    for path,digest in config.items():
        doc=shared.pinned(path,digest)
        artifacts=doc if isinstance(doc,list) else doc.get('artifacts',[])
        for i,a in enumerate(artifacts):
            if a.get('source_url','').endswith('_htm.xml'):
                refs.append((path,i,a))
    return config,refs


def expected_reference(row,refs):
    try:return batch.instance_reference(row)
    except h.InputError:
        # No filename inferred. A retained exact-directory instance may provide
        # the binding, but competing representations require explicit review.
        directory='/'+str(row['identity']['cik'])+'/'+row['identity']['accession'].replace('-','')+'/'
        matches={(a['source_url'],a['sha256']) for _,_,a in refs if directory in a['source_url']}
        if len(matches)>1:raise h.InputError('Competing retained instance identities')
        if matches:
            url,digest=next(iter(matches));return dict(url=url,sha256=digest)
        return dict(url=None,sha256=None,artifact_type='selected filing XBRL instance; filename not retained')


def inspect_row(row,refs,config):
    expected=expected_reference(row,refs)
    matches=[ref for ref in refs if ref[2]['source_url']==expected['url']]
    if len(matches)>1:
        raise h.InputError('Multiple retained source bindings; explicit review required, no precedence')
    source=None;artifacts=[]
    if matches:
        path,i,a=matches[0]
        if a.get('response_body_gzip_base64'):
            encoded=a['response_body_gzip_base64']
            if isinstance(encoded,list):encoded=''.join(encoded)
            body=gzip.decompress(base64.b64decode(encoded,validate=True))
            if (a.get('representation')!='sec_response_body_bytes' or a.get('digest_type')!='sha256_sec_response_body_bytes'
                    or hashlib.sha256(body).hexdigest()!=a['sha256'] or len(body)!=a['byte_length']):
                raise h.InputError('Retained original-body representation/digest/length mismatch')
        source=dict(path=path,locator='/artifacts/'+str(i),repository_sha256=config[path],
                    original_metadata={k:v for k,v in a.items() if 'base64' not in k})
        artifacts=[dict(a,accession=row['identity']['accession'])]
    if expected['url'] is None:
        reason='No retained exact instance filename/body reference; inspection cannot establish fact provenance.'
        return None,None,None,[dict(field=f.value,status='UNAVAILABLE',outcome='MISSING_RETAINED_BODY',
            candidates=[],selected=None,unresolved_requirements=[reason]) for f in income.POLICIES]
    else:
        proxy=dict(row,candidates=[dict(artifacts=[expected])])
        evidence,results,_=shared.inspect_period(proxy,artifacts,LIMITATIONS)
    fields=[]
    for field,result in results.items():
        slot=batch.slot(field,result,evidence)
        if slot['status']=='POPULATED':outcome='POPULATED'
        elif result and result.competing_values:outcome='CONFLICTING_VALUES'
        elif not matches:outcome='MISSING_RETAINED_BODY'
        elif not artifacts[0].get('response_body_gzip_base64'):outcome='MISSING_RETAINED_BODY'
        elif not evidence.receipts:outcome='MISSING_RECEIPT'
        elif result is None:outcome='INSUFFICIENT_SCOPE'
        elif not result.candidates:outcome='NO_ELIGIBLE_DIRECT_CONCEPT'
        else:outcome='INSUFFICIENT_SCOPE'
        fields.append(dict(slot,outcome=outcome))
    return evidence,results,source,fields


def _pilot_fields(annual):
    fields=[]
    for v in annual.inputs:
        if v.field not in income.POLICIES:continue
        fields.append(dict(field=v.field.value,outcome='POPULATED' if v.value is not None else 'INSUFFICIENT_SCOPE',
            status='POPULATED' if v.value is not None else 'UNAVAILABLE',value_usd=str(v.value) if v.value is not None else None,
            unit=v.unit,scale=v.scale,sign=v.sign,precision=v.precision,
            origin=v.origin.value,role=v.role,scope=v.scope,completeness=v.completeness.value,
            alternatives=[dict(value_usd=str(a.value),role=a.role,precision=a.precision,
                sources=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                    locator=s.locator,context_id=s.context_id,occurrence_ordinal=s.occurrence_ordinal,
                    namespace=s.namespace,concept=s.concept,raw_value=s.raw_value) for s in a.sources]) for a in v.alternatives],
            sources=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                          locator=s.locator,context_id=s.context_id,occurrence_ordinal=s.occurrence_ordinal,
                          namespace=s.namespace,concept=s.concept,raw_value=s.raw_value) for s in v.sources],
            unresolved_requirements=list(v.unresolved_requirements)))
    return fields


def build():
    validation=json.loads((shared.ROOT/CLASSIFICATIONS).read_text())
    manifest=shared.pinned(shared.MANIFEST,shared.MANIFEST_SHA256)
    scope=[r for r in validation['rows'] if r['classification']!='SPECIALIZED_METHODOLOGY_REQUIRED']
    excluded=[r['execution_ticker'] for r in validation['rows'] if r['classification']=='SPECIALIZED_METHODOLOGY_REQUIRED']
    allowed={r['execution_ticker']:r for r in scope}
    config,refs=sources();existing={}
    for path in ('docs/retained-income-batch-ledger.json','docs/nvda-retained-income-ledger.json'):
        doc=json.loads((shared.ROOT/path).read_text())
        for i,r in enumerate(doc['rows']):
            existing[(r['identity']['cik'],r['identity']['accession'])]=(r,path+'#/rows/'+str(i))
    pilot_annuals={}
    for name in ('MSFT','AAPL','GOOGL'):
        for a in pilot.load_history(name).annuals:
            pilot_annuals[(a.period.cik,a.period.accession)]=a
    rows=[];annuals={};backlog=[]
    for i,r in enumerate(manifest['rows']):
        name=r['ticker']
        if name not in allowed:raise h.InputError('Manifest scope differs from frozen classification')
        key=(r['cik'],r['identity']['accession']);base=dict(issuer=name,identity=r['identity'],
            identity_reference=shared.MANIFEST+'#/rows/'+str(i),other_families='UNASSESSED_BY_SWEEP',
            financial_sufficiency='NOT_ASSESSED')
        if key in pilot_annuals:
            a=pilot_annuals[key]
            base.update(reused=True,package_reference='existing pilot adapter; unchanged',fields=_pilot_fields(a))
        elif key in existing:
            old,ref=existing[key]
            fields=[dict(f,outcome='POPULATED' if f['selected'] is not None else 'INSUFFICIENT_SCOPE') for f in old['fields']]
            base.update(reused=True,package_reference=ref,fields=fields)
        else:
            evidence,results,source,fields=inspect_row(r,refs,config)
            base.update(reused=False,expected_instance=expected_reference(r,refs),retained_source=source,fields=fields)
            if evidence is None:
                p=shared.period(r['identity'])
                aa=h.AnnualBundle('retained-direct-income:'+str(p.cik)+':'+p.accession,1,p,
                    tuple(income.unavailable(p,f,'No retained instance reference/body for direct income.' if f in income.POLICIES
                        else 'Outside Revenue/EBIT sweep; unassessed, not searched.',h.Review.UNREVIEWED) for f in h.Field),LIMITATIONS)
            else:aa=income.annual(evidence,results,LIMITATIONS)
            annuals.setdefault(name,[]).append(aa)
            gaps=[f for f in fields if f['outcome'] in ('MISSING_RETAINED_BODY','MISSING_RECEIPT')]
            if gaps:
                backlog.append(dict(issuer=name,identity=r['identity'],required_artifact=expected_reference(r,refs),
                    fields=[f['field'] for f in gaps],reasons=sorted({f['outcome'] for f in gaps}),
                    action='Separate authorization required for exact-instance acquisition or receipt repair; no requests in this sweep.'))
        # Preserve the implemented derived policy reference, never populate direct EBIT from it.
        if allowed[name]['measure_resolution_counts'].get('operating_income:derived',0):
            base['existing_derived_ebit_reference']=dict(policy_id='operating_income_component_derivation',version='1',
                evidence='docs/operating-income-derivation-design.md',integration='not integrated; direct inspection only')
        rows.append(base)
    # Supported issuers are outside the forty-issuer manifest. Counts-only corpus
    # supplies selected ends, not accessions/annual starts; do not fabricate them.
    for name,r in allowed.items():
        if any(row['issuer']==name for row in rows):continue
        for end in r['selected_annual_end_dates']:
            rows.append(dict(issuer=name,identity=dict(cik=r['cik'],accession=None,form=None,annual_start=None,annual_end=end),
                identity_reference=CLASSIFICATIONS+'#/rows/'+str(validation['rows'].index(r)),reused=False,
                fields=[dict(field=f.value,outcome='INSUFFICIENT_IDENTITY_BINDING',status='UNAVAILABLE',
                    unresolved_requirements=['Counts-only selected end is not exact filing/annual-start identity; no value inferred.']) for f in income.POLICIES],
                other_families='UNASSESSED_BY_SWEEP',financial_sufficiency='NOT_ASSESSED'))
    keys=[(r['identity']['cik'],r['identity']['annual_end']) for r in rows]
    if len(keys)!=len(set(keys)):raise h.InputError('Duplicate selected-period accounting')
    summary={}
    for name,r in allowed.items():
        rr=[x for x in rows if x['issuer']==name]
        if len(rr)!=r['history_period_count']:raise h.InputError('Selected history count mismatch')
        summary[name]=dict(periods=len(rr),slots=2*len(rr),outcomes=dict(sorted(Counter(f['outcome'] for x in rr for f in x['fields']).items())))
    histories={name:h.HistoryBundle('retained-income-sweep:'+name,1,aa[0].period.cik,
        tuple(sorted(aa,key=lambda a:a.period.annual_end)),('This package contains only newly inspected selections, not a complete issuer history.',))
        for name,aa in annuals.items()}
    ledger=dict(schema='retained-income-sweep-v1',classification_source=CLASSIFICATIONS,
        classification_sha256=hashlib.sha256((shared.ROOT/CLASSIFICATIONS).read_bytes()).hexdigest(),
        identity_manifest_sha256=shared.MANIFEST_SHA256,source_sha256=config,excluded_specialized=excluded,
        limitations=list(LIMITATIONS),issuer_count=len(scope),selected_periods=len(rows),slots=2*len(rows),
        summary=summary,outcomes=dict(sorted(Counter(f['outcome'] for row in rows for f in row['fields']).items())),
        history_exceptions=manifest['history_exceptions'],rows=rows,
        acquisition_backlog=backlog,
        identity_backlog=[dict(issuer=r['issuer'],identity=r['identity'],
            reason='Selected end only; exact filing identity unavailable in inspected retained records.')
            for r in rows if any(f['outcome']=='INSUFFICIENT_IDENTITY_BINDING' for f in r['fields'])])
    return ledger,histories
