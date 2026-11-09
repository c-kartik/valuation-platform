"""Full-window reporting audit against raw retained filing XBRL.

Independent XML inspection does not call either reporting preparation consumer.
Reads published packages; writes only an audit receipt and missing audit evidence.
Original Python/DCF pipelines and accepted reporting amounts are never rewritten.
"""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

from valuation_platform.sec.submissions import fetch_submissions, fetch_submission_history
from valuation_platform.sec.tickers import SECCompanyIdentity
from valuation_platform.sec.filing_xbrl import discover_extracted_xbrl

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mix_sources', ROOT/'scripts/prepare_revenue_mix.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
NS = {'x':'http://www.xbrl.org/2003/instance', 'd':'http://xbrl.org/2006/xbrldi'}
METRICS = ('revenue','operating_income','net_income','cfo','cash_capex','sbc')

class AuditError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise AuditError(message)

def expanded(value, namespaces):
    if ':' not in value:
        return '{'+namespaces.get('', '')+'}'+value
    prefix,local=value.split(':',1)
    return '{'+namespaces[prefix]+'}'+local

def raw_instance(data):
    """Independently read XML QNames, contexts, units and integer USD values."""
    require(b'<!DOCTYPE' not in data.upper() and b'<!ENTITY' not in data.upper(), 'Unsafe XML')
    namespaces={prefix:uri for _,(prefix,uri) in ET.iterparse(io.BytesIO(data),events=['start-ns'])}
    root=ET.fromstring(data)
    contexts={}
    for c in root.findall('x:context',NS):
        dimensions=[]
        for member in c.findall('.//d:explicitMember',NS):
            dimensions.append((expanded(member.attrib['dimension'],namespaces),expanded(member.text,namespaces)))
        contexts[c.attrib['id']]={'start':c.findtext('x:period/x:startDate',namespaces=NS),
            'end':c.findtext('x:period/x:endDate',namespaces=NS),
            'entity':c.findtext('x:entity/x:identifier',namespaces=NS),
            'typed':len(c.findall('.//d:typedMember',NS)), 'dimensions':tuple(sorted(dimensions))}
    units={u.attrib['id']:u for u in root.findall('x:unit',NS)}
    facts=[]
    for f in root:
        if 'contextRef' not in f.attrib or f.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}nil') in ('true','1'):
            continue
        u=units.get(f.attrib.get('unitRef'))
        if u is None or len(u)!=1 or u[0].tag!='{'+NS['x']+'}measure':
            continue
        if expanded(u[0].text,namespaces)!='{http://www.xbrl.org/2003/iso4217}USD':
            continue
        try:value=Decimal(f.text)
        except Exception:continue
        facts.append({'tag':f.tag,'context_id':f.attrib['contextRef'],'context':contexts[f.attrib['contextRef']],
                      'value':value,'decimals':f.attrib.get('decimals')})
    return facts

def check_fact(facts, operand, cik, namespace=None, dimensions=()):
    concept=operand['concept'].split(':')[-1]
    matching=[f for f in facts if f['tag'].split('}')[-1]==concept
        and (f['tag']=='{'+namespace+'}'+concept if namespace else f['tag'].startswith('{http://fasb.org/us-gaap/'))
        and f['context']['start']==operand['start'] and f['context']['end']==operand['end']
        and f['context']['dimensions']==tuple(sorted(dimensions)) and not f['context']['typed']
        and int(f['context']['entity'])==cik]
    require(bool(matching),f'Missing raw filing fact: {operand}')
    require({f['value'] for f in matching}=={Decimal(operand['value'])},f'Raw filing value contradiction: {operand}')
    require(all(f['value'].is_finite() and f['value']==f['value'].to_integral_value() for f in matching),'Noninteger USD')
    return {'accession':operand['accession'],'concept':operand['concept'],'start':operand['start'],'end':operand['end'],
            'value':operand['value'],'context_ids':sorted({f['context_id'] for f in matching}),
            'decimals':sorted({str(f['decimals']) for f in matching}),'dimensions':list(dimensions)}

def audit(ticker, refresh=False):
    report=json.loads((ROOT/f'frontend/public/research-data/{ticker}.json').read_text())
    mix=json.loads((ROOT/f'frontend/public/revenue-mix/{ticker}.json').read_text())
    cik=module.IDS[ticker]
    company=SECCompanyIdentity(ticker,cik,f'{cik:010d}',ticker,'SEC',datetime.now(timezone.utc))
    client=module.EvidenceClient(ticker,refresh)
    # New audit evidence is isolated; retained revenue-mix sources are read-only fallback.
    client.fallback=ROOT/f'data/revenue-mix/sources/{ticker}'
    client.directory=ROOT/f'data/reporting-audit/sources/{ticker}'
    client.directory.mkdir(parents=True,exist_ok=True)
    submission=fetch_submissions(client,company)
    filings={f.accession_number:f for f in submission.filings}
    annuals=report['validation']['annual_tie_outs']
    operands=[o for r in report['rows'] for e in r['evidence'].values() for o in e['operands']]+[a['annual'] for a in annuals]
    earliest=min(date.fromisoformat(o['filed']) for o in operands)
    for history in submission.history_files:
        if history.filing_to>=earliest:
            filings.update({f.accession_number:f for f in fetch_submission_history(client,history)})
    instances={};links={};checks=[]
    def source(accession):
        if accession not in instances:
            require(accession in filings,'Missing submission accession '+accession)
            filing=filings[accession]
            require(str(filing.filing_date)<=report['as_of'],'Filing after cutoff')
            artifact=discover_extracted_xbrl(client,company,filing)
            data=client.get_bytes(artifact.source_url)
            instances[accession]=raw_instance(data);links[accession]=artifact.source_url
        return instances[accession]
    distinct={}
    for operand in operands:
        key=(operand['accession'],operand['concept'],operand['start'],operand['end'])
        if key in distinct:
            require(distinct[key]==operand['value'],'Conflicting published operands')
            continue
        require(str(filings[operand['accession']].filing_date)==operand['filed'],'Filed date mismatch')
        checks.append(check_fact(source(operand['accession']),operand,cik))
        distinct[key]=operand['value']
    derivations=[]
    for i,row in enumerate(report['rows']):
        if i:require(date.fromisoformat(report['rows'][i-1]['end'])+timedelta(days=1)==date.fromisoformat(row['start']),'Quarter gap')
        require(70<=(date.fromisoformat(row['end'])-date.fromisoformat(row['start'])).days+1<=110,'Invalid quarter duration')
        for metric in METRICS:
            e=row['evidence'][metric];ops=e['operands']
            require(len(ops)==(1 if row['quarter']==1 else 2),'Wrong derivation arity')
            require(ops[0]['end']==row['end'],'Quarter operand end mismatch')
            if len(ops)==2:
                require(ops[0]['start']==ops[1]['start'],'YTD starts differ')
                require(date.fromisoformat(ops[1]['end'])+timedelta(days=1)==date.fromisoformat(row['start']),'Wrong YTD subtraction boundary')
            else:require(ops[0]['start']==row['start'],'Q1 start mismatch')
            amount=ops[0]['value']-(ops[1]['value'] if len(ops)==2 else 0)
            require(amount==row['values'][metric],'Derived amount mismatch')
        v=row['values']
        require(v['fcf']==v['cfo']-v['cash_capex'],'FCF mismatch')
        require(v['other_operating']==v['cfo']-v['net_income']-v['sbc'],'Other bridge mismatch')
        for metric,numerator in [('operating_margin','operating_income'),('fcf_margin','fcf')]:
            expected=v[numerator]/v['revenue'] if v['revenue'] else None
            require(v[metric]==expected,'Margin mismatch')
        derivations.append({'quarter':row['id'],'six_reported_metrics':'MATCH','FCF':'MATCH','other_bridge':'MATCH','margins':'MATCH'})
    mix_checks=[];seen=set()
    require(len(mix['rows'])==len(report['rows'])==20,'Wrong window')
    for row,h in zip(mix['rows'],report['rows']):
        require(all(row[k]==h[k] for k in ('id','start','end','fiscal_year','quarter')),'Mix calendar mismatch')
        require(row['total']==h['values']['revenue'],'Mix total mismatch')
        require(sum(row['values'][s['id']] for s in mix['series'])==row['total'],'Top-level mix mismatch')
        if mix['detail']['series']:
            require(sum(row['values'][s['id']] for s in mix['detail']['series'])==row['values'][mix['detail']['parent']],'Mix detail mismatch')
        for key,e in row['evidence'].items():
            ops=e['operands']
            require(ops[0]['value']-(ops[1]['value'] if len(ops)==2 else 0)==row['values'][key],'Mix derivation mismatch')
            for o in ops:
                dims=[('{'+d['axis_namespace']+'}'+d['axis'],'{'+d['member_namespace']+'}'+d['member']) for d in o['dimensions']]
                identity=(o['accession'],o['concept'],o['start'],o['end'],tuple(sorted(dims)))
                if identity in seen:continue
                match=check_fact(source(o['accession']),o,cik,o['namespace'],dims)
                require(o['source_url']==links[o['accession']],'Wrong mix source URL')
                require(set(o['context_ids'])<=set(match['context_ids']),'Wrong context IDs')
                mix_checks.append(match);seen.add(identity)
    standalone_checks=[]
    for c in report['validation']['discrete_quarter_checks']:
        row=next(r for r in report['rows'] if r['id']==c['quarter_id'])
        require(c['derived']==row['values'][c['metric']],'Stale standalone comparison')
        o=c['reported']
        check_fact(source(o['accession']),o,cik)
        require(c['derived']-o['value']==c['difference'],'Wrong standalone difference')
        standalone_checks.append({'quarter':row['id'],'metric':c['metric'],'difference':c['difference']})
    mix_standalone_checks=[]
    for c in mix['validation']['direct_quarter_checks']:
        row=next(r for r in mix['rows'] if r['id']==c['quarter'])
        o=dict(row['evidence'][c['series']]['operands'][0],start=row['start'],value=c['reported'])
        dims=[('{'+d['axis_namespace']+'}'+d['axis'],'{'+d['member_namespace']+'}'+d['member']) for d in o['dimensions']]
        check_fact(source(o['accession']),o,cik,o['namespace'],dims)
        require(c['derived']==row['values'][c['series']] and c['derived']-c['reported']==c['difference'],'Wrong mix standalone comparison')
        mix_standalone_checks.append(c)
    for a in annuals:
        require(a['sum_quarters']==a['annual']['value'],'Consolidated annual mismatch')
    for a in mix['validation']['annual_category_checks']:
        require(a['sum_quarters']==a['reported_annual'],'Mix annual mismatch')
    sources={'ticker':ticker,'files':client.sources}
    out=ROOT/'data/reporting-audit';out.mkdir(exist_ok=True)
    (out/f'{ticker}-sources.json').write_text(json.dumps(sources,indent=2,sort_keys=True)+'\n')
    receipt={'schema':'full-reporting-audit/v1','ticker':ticker,'as_of':report['as_of'],'status':'MATCH',
        'scope':'All 20 displayed quarters, all six underlying metrics, all preparation annual totals and all revenue-mix source operands. Independent direct XML selection, not only package arithmetic.',
        'filings':len(instances),'consolidated_fact_checks':len(checks),'revenue_mix_fact_checks':len(mix_checks),
        'quarter_checks':derivations,'consolidated_facts':checks,'revenue_mix_facts':mix_checks,
        'standalone_consolidated_checks':len(standalone_checks),'standalone_mix_checks':len(mix_standalone_checks),
        'annual_metric_tieouts':len(annuals),'annual_mix_tieouts':len(mix['validation']['annual_category_checks']),
        'consolidated_standalone_differences':[c for c in report['validation']['discrete_quarter_checks'] if c['difference']],
        'mix_standalone_differences':[c for c in mix['validation']['direct_quarter_checks'] if c['difference']],
        'package_sha256':{name:hashlib.sha256((ROOT/f'frontend/public/{name}/{ticker}.json').read_bytes()).hexdigest() for name in ('research-data','revenue-mix')},
        'limitations':['Exact match to retained SEC filing XBRL is not a line-by-line PDF/HTML audit or a latest-restated series.','Other is a derived aggregate, not an independently disclosed working-capital line.','Meta2021 segment comparative exception and standalone/YTD presentation differences remain explicit.']}
    (out/f'{ticker}-audit.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:receipt[k] for k in ('ticker','status','filings','consolidated_fact_checks','revenue_mix_fact_checks')}),flush=True)
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ticker',choices=module.IDS,required=True);parser.add_argument('--refresh',action='store_true');args=parser.parse_args();audit(args.ticker,args.refresh)
