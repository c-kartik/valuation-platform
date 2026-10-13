"""Additive official binding repair. Existing direct/derivation semantics only."""
from collections import Counter
from dataclasses import replace
import base64
import gzip
import hashlib
import json
from . import approved_income_integration as approved, historical_inputs as h
from . import retained_income_sweep as sweep, retained_income_batch as batch
from . import retained_income_preparation as income, nvda_income_inputs as shared
from ..normalization.models import DerivedHistoricalValue

RECEIPTS='docs/evidence/income-binding-repair.json'
CONFIG='docs/income-binding-repair-config.json'


def load():
    config=json.loads((shared.ROOT/CONFIG).read_text())
    return shared.pinned(RECEIPTS,config['receipt_sha256'])


def metadata_binding(accession):
    """Exact official array locator and actual typed receipt metadata, no guesses."""
    payload=load();row=next(r for r in payload['rows'] if r['status']=='VERIFIED' and r['filing']['accession_number']==accession)
    matches=[]
    for a in payload['artifacts']:
        if not a['source_url'].startswith('https://data.sec.gov/submissions/'):continue
        encoded=a['response_body_gzip_base64'];encoded=''.join(encoded) if isinstance(encoded,list) else encoded
        body=gzip.decompress(base64.b64decode(encoded,validate=True))
        if hashlib.sha256(body).hexdigest()!=a['sha256']:raise h.InputError('Official metadata body digest differs')
        doc=json.loads(body);prefix='/filings/recent' if 'filings' in doc else '/'
        records=doc['filings']['recent'] if 'filings' in doc else doc
        for index,value in enumerate(records.get('accessionNumber',[])):
            if value!=accession:continue
            observed=dict(accession_number=value,form=records['form'][index],filing_date=records['filingDate'][index],
                report_date=records['reportDate'][index],primary_document=records['primaryDocument'][index])
            if observed!=row['filing']:raise h.InputError('Official submission array differs from approved filing metadata')
            matches.append(dict(receipt={k:v for k,v in a.items() if 'base64' not in k},array_prefix=prefix,array_index=index))
    if len(matches)!=1:raise h.InputError('Exactly one official metadata source locator required')
    return dict(identity=row['identity'],filing=row['filing'],frozen_cutoff=payload['frozen_cutoff'],
        source=matches[0],repair_document=RECEIPTS,repair_document_sha256=json.loads((shared.ROOT/CONFIG).read_text())['receipt_sha256'])


def build():
    ledger,histories=approved.build();payload=load();config,refs=sweep.sources()
    manifest=shared.pinned(shared.MANIFEST,shared.MANIFEST_SHA256)
    seed_annuals={};failures=[]
    for index,repair in enumerate(payload['rows']):
        target=repair['target']
        row=next(r for r in ledger['rows'] if r['issuer']==repair['issuer'] and r['identity']['annual_end']==target['annual_end'])
        if repair['status']!='VERIFIED':
            failures.append(dict(issuer=repair['issuer'],target=target,reason=repair['reason']));continue
        if repair['issuer'] in ('JNJ','KLAC'):
            if next(f for f in row['fields'] if f['field']=='ebit')['outcome']!='NO_ELIGIBLE_DIRECT_CONCEPT':
                raise h.InputError('Metadata repair cannot override populated or conflicting EBIT')
            selection=next(s for s in manifest['rows'] if s['identity']==repair['identity'])
            evidence,_,_,_=sweep.inspect_row(selection,refs,config)
            result=approved.execute(evidence,repair['filing'],include_repairs=True)
            if not isinstance(result,DerivedHistoricalValue):
                failures.append(dict(issuer=repair['issuer'],target=target,reason='Unchanged approved resolver did not resolve: '+type(result).__name__));continue
            history=histories[repair['issuer']];annual=next(a for a in history.annuals if a.period==evidence.period)
            packaged,proof=approved.package(annual,evidence,result,metadata_binding=metadata_binding(annual.period.accession))
            histories[repair['issuer']]=replace(history,annuals=tuple(packaged if a.period==annual.period else a for a in history.annuals))
            root=next(v for v in packaged.inputs if v.formula)
            row['fields']=[dict(field='ebit',outcome='DERIVED',status='POPULATED_DERIVED',origin='derived',value_usd=str(result.value),
                unit='USD',scale=1,sign=1,precision=root.precision,provenance=proof,
                formula=dict(expression=root.formula.expression,kind='signed_registered_component_total'),
                source_references=[dict(source_id=s.source_id,url=s.receipt.artifact.url,sha256=s.receipt.artifact.sha256,
                    ordinal=s.occurrence_ordinal,context_id=s.context_id,raw_value=s.raw_value,precision=s.decimals) for s in root.sources])
                if f['field']=='ebit' else f for f in row['fields']]
            row['derivation_integration']=dict(status='VERIFIED_DERIVED',metadata_reference=RECEIPTS+'#/rows/'+str(index)+'/filing')
        else:
            if any(f['outcome'] in ('POPULATED','DERIVED','CONFLICTING_VALUES') for f in row['fields']):
                raise h.InputError('Seed repair cannot override populated or conflicting inputs')
            artifacts=[a for a in payload['artifacts'] if a['source_url']==repair['instance_url']]
            if len(artifacts)!=1:raise h.InputError('Unique verified seed instance required')
            original=artifacts[0];a=dict(original,accession=repair['identity']['accession'])
            expected=dict(url=a['source_url'],sha256=a['sha256'])
            selection=dict(identity=repair['identity'],candidates=[dict(artifacts=[expected])])
            evidence,results,_=shared.inspect_period(selection,[a],batch.LIMITATIONS)
            annual=income.annual(evidence,results,batch.LIMITATIONS)
            binding_flag=approved.METADATA_FLAG+json.dumps(metadata_binding(evidence.period.accession),sort_keys=True,separators=(',',':'))
            annual=replace(annual,inputs=tuple(replace(v,flags=v.flags+(binding_flag,)) if v.field in income.POLICIES else v for v in annual.inputs))
            seed_annuals.setdefault(repair['issuer'],[]).append(annual)
            fields=[]
            for field,result in results.items():
                slot=batch.slot(field,result,evidence)
                outcome='POPULATED' if slot['selected'] is not None else 'CONFLICTING_VALUES' if result and result.competing_values else 'NO_ELIGIBLE_DIRECT_CONCEPT'
                fields.append(dict(slot,outcome=outcome))
            row['prior_seed_identity']=row['identity'];row['prior_identity_reference']=row['identity_reference']
            row.update(identity=repair['identity'],identity_reference=RECEIPTS+'#/rows/'+str(index),
                identity_depth='VERIFIED_OFFICIAL_CUTOFF_SELECTION_AND_ANNUAL_DEI',fields=fields,expected_instance=expected,
                retained_source=dict(path=RECEIPTS,locator='/artifacts/'+str(payload['artifacts'].index(original)),
                    metadata_reference='/rows/'+str(index)+'/filing',original_metadata={k:v for k,v in original.items() if 'base64' not in k}))
    for name,annuals in seed_annuals.items():
        histories[name]=h.HistoryBundle('repaired-retained-direct-income:'+name,1,annuals[0].period.cik,
            tuple(sorted(annuals,key=lambda a:a.period.annual_end)),() if len(annuals)==5 else ('Only independently verified seed periods packaged; unresolved frozen slots not fabricated.',))
    ledger['schema']='repaired-income-preparation-v1'
    ledger['outcomes']=dict(sorted(Counter(f['outcome'] for r in ledger['rows'] for f in r['fields']).items()))
    for name,s in ledger['summary'].items():
        s['outcomes']=dict(sorted(Counter(f['outcome'] for r in ledger['rows'] if r['issuer']==name for f in r['fields']).items()))
    ledger['binding_repair_receipt_sha256']=json.loads((shared.ROOT/CONFIG).read_text())['receipt_sha256']
    ledger['binding_repair_exceptions']=failures
    ledger['derivation_metadata_exceptions']=[r for r in ledger['derivation_metadata_exceptions'] if not any(p['status']=='VERIFIED' and p['identity']==r['identity'] for p in payload['rows'])]
    ledger['identity_backlog']=[r for r in ledger['identity_backlog'] if not any(p['status']=='VERIFIED' and p['issuer']==r['issuer'] and p['identity']['annual_end']==r['identity']['annual_end'] for p in payload['rows'])]
    ledger['seed_identity_exceptions']=[r for r in ledger['rows'] if r['issuer'] in ('META','COST') and any(f['outcome']!='POPULATED' for f in r['fields'])]
    return ledger,histories
