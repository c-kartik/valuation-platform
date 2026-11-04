"""Independent Apple review: raw retained source bytes, arithmetic, runtime parity.

Does not import producer scripts. Writes only this independent-review folder.
"""
import argparse
import base64
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
BASE=HERE.parent
X='http://www.xbrl.org/2003/instance'
CACHE={}
POINTS=set()

def load(path):return json.loads(path.read_text())
def value(x):return F(x['amount_usd'] if isinstance(x,dict) and 'amount_usd' in x else x)
def source(receipt):
    reference=receipt['source_reference']
    if reference not in CACHE:
        file,fragment=reference.split('#')
        obj=load(ROOT/file)
        for key in fragment.strip('/').split('/'):
            obj=obj[int(key)] if isinstance(obj,list) else obj[key]
        body=gzip.decompress(base64.b64decode(obj['response_body_gzip_base64']))
        assert hashlib.sha256(body).hexdigest()==receipt['sha256']==obj['sha256']
        assert len(body)==receipt['byte_length']==obj['byte_length']
        assert obj['source_url']==receipt['url']
        tree=ET.fromstring(body)
        CACHE[reference]=(body,tree,{e.get('id'):e for e in tree.iter() if e.get('id')})
    return CACHE[reference]

def primary_number(node):
    text=''.join(node.itertext()).strip().replace(',','').replace('\u00a0','').replace('$','')
    if text in ('—','–','-'):number=F()
    else:number=F(text)
    number*=F(10)**int(node.get('scale','0'))
    return -number if node.get('sign')=='-' else number

def verify_point(point):
    receipts=point['sources']
    p=next(x for x in receipts if x['url'].endswith('.htm'))
    i=next(x for x in receipts if x['url'].endswith('.xml'))
    _,pt,pids=source(p);_,it,iids=source(i)
    occurrences=point.get('occurrences') or [{'context_id':point['instance_context_id'],'xml_id':point['primary_locator'].split('#',1)[1]}]
    for occurrence in occurrences:
        context=occurrence['context_id'];xml_id=occurrence['xml_id']
        key=(p['url'],point['namespace'],point['concept'],context,xml_id,point['value'])
        if key in POINTS:continue
        primary=pids[xml_id]
        assert primary.get('contextRef')==context
        assert primary.get('name').split(':')[-1]==point['concept']
        assert primary_number(primary)==F(point['value']),(key,primary_number(primary))
        facts=[n for n in it.iter('{'+point['namespace']+'}'+point['concept']) if n.get('contextRef')==context]
        assert facts and all(F(''.join(n.itertext()))==F(point['value']) for n in facts)
        for fact,ids in [(primary,pids),*((f,iids) for f in facts)]:
            unit=ids[fact.get('unitRef')]
            measure=unit.find('{'+X+'}measure').text.split(':')[-1]
            assert measure==point['unit'],(key,measure,point['unit'])
        pc=pids[context];ic=iids[context]
        def period(c):
            p=c.find('{'+X+'}period')
            return {n.tag.split('}')[-1]:n.text for n in p}
        assert period(pc)==period(ic)
        expected_end=point.get('as_of') or point.get('target_annual_end')
        if isinstance(point.get('scope'),dict):expected_end=point['scope']['end']
        if expected_end:assert expected_end in period(ic).values(),(key,expected_end,period(ic))
        assert pc.find('.//{'+X+'}identifier').text.lstrip('0')=='320193'
        assert ic.find('.//{'+X+'}identifier').text.lstrip('0')=='320193'
        POINTS.add(key)

def walk(node):
    if isinstance(node,dict):
        if isinstance(node.get('sources'),list) and 'concept' in node and 'namespace' in node and 'value' in node:
            verify_point(node)
        for child in node.values():walk(child)
    elif isinstance(node,list):
        for child in node:walk(child)

def run(bundle=None,api=None):
    stages={s:load(BASE/s/'results.json') for s in ('financing','da','tax','equity')}
    for stage in stages.values():walk(stage)
    record=load(BASE/'platform-resolution.json')
    for s in stages:
        assert record['stage_workpaper_sha256'][s]==hashlib.sha256((BASE/s/'results.json').read_bytes()).hexdigest()
    assert record['company_status']=='OPEN' and record['company_complete'] is False
    assert all(v is False for v in record['readiness'].values())
    financing=[]
    for p in stages['financing']['periods']:
        rows=p['source_rows'];total=next(r for r in rows if r['classification']=='FINANCING_TOTAL')
        detail=[r for r in rows if r['classification']!='FINANCING_TOTAL']
        assert sum(F(r['signed_cash_usd']) for r in detail)==F(total['signed_cash_usd'])
        funding=sum(F(r['signed_cash_usd']) for r in detail if r['included_in_net_borrowing'])
        assert funding==value(p['identified_net_borrowing'])
        cfo=F(p['reported_operating_cash_flow']['value']);ppe=F(p['reported_cash_ppe']['value'])
        assert cfo-ppe+funding==value(p['identified_funding_fcfe'])
        assert p['full_fcfe_usd'] is None and p['actual_finance_lease_principal_usd'] is None
        assert p['finance_lease_principal_containing_caption'] is None
        financing.append({'year':p['fiscal_year'],'fcfe_usd':str(cfo-ppe+funding),'exact_fcfe':False})
    assert stages['financing']['issuer_request_sent'] is False
    da=stages['da']
    for p in da['annual_adopted_inputs']:
        assert F(p['additional_da_plug_usd'])==0
        assert F(p['adopted_da_usd'])==F(p['reported_combined_da']['value'])
    for p in da['later_comparative_points']:
        points=p['points'];delta=F(points['ppe_depreciation']['value'])+F(points['intangible_amortization']['value'])-F(points['combined_da']['value'])
        radius=sum(F(10)**(-int(z['precision']))/2 for z in points.values())
        assert delta==F(p['rounding']['nominal_difference_usd'])
        assert p['rounding']['rounding_can_explain_difference']==(delta-radius<=0<=delta+radius)
        if p['fiscal_year']==2024:assert delta==355000000 and delta-radius>0
    tax=stages['tax']
    for p in tax['historical_periods']:
        f=p['tax_facts'];current=sum(F(f['current_'+j]['value']) for j in ('federal','state','foreign'))
        deferred=sum(F(f['deferred_'+j]['value']) for j in ('federal','state','foreign'))
        assert current+deferred==F(f['provision']['value'])
        assert p['operating_cash_tax_allocation_usd'] is None
        assert F(p['additional_cash_tax_fcff_adjustment_usd'])==0
        nwc=p['nwc'];a=nwc['opening_current_tax_fact'];b=nwc['closing_current_tax_fact']
        if a is None or b is None:assert nwc['tax_excluded_fcff_diagnostic_usd'] is None
        else:
            change=F(b['value'])-F(a['value'])
            assert change==F(nwc['current_tax_balance_change_usd'])
            assert abs(F(p['adopted_fcff_usd'])-change-F(nwc['tax_excluded_fcff_diagnostic_usd']))<F('1e-35')
    for bridge in tax['forecast_bridges']:
        b=bridge['algebraic_component_bridge']
        assert abs(sum(F(v) for v in b['signed_components_usd'].values())-F(b['fcff_change_usd']))<F('1e-30')
        assert bridge['annual_forecast_tax_rates']==['0.18','0.185','0.19','0.195','0.20']
        assert bridge['terminal_tax_rate']=='0.20'
    prior_parity=load(ROOT/'docs/company-resolutions/implementation-2026-11-03/basis-bridge/valuation-parity.json')
    apple_prior=next(c for c in prior_parity['companies'] if c['policy_path']=='data/preload/aapl-v1/policy.json')
    assert hashlib.sha256((ROOT/apple_prior['policy_path']).read_bytes()).hexdigest()==apple_prior['current_policy_sha256']
    for bridge,old in zip(tax['forecast_bridges'],apple_prior['scenarios'],strict=True):
        assert bridge['enterprise_value_usd']==old['after_enterprise_value_usd']
    equity=stages['equity'];s=equity['sources'];a=equity['anchor_support']
    assert sum(F(x['value']) for x in s['cash'].values())==F(a['cash_and_securities_usd'])==132420000000
    assert sum(F(x['value']) for x in s['debt'].values())==F(a['named_debt_carrying_usd'])==98657000000
    assert sum(F(x['value']) for x in s['finance_leases'].values())==F(a['finance_lease_liability_usd'])==1230000000
    assert F(s['dated_common_shares']['value'])==F(a['dated_common_shares'])==14773260000
    assert F(s['term_debt_fair_value']['value'])==F(a['term_debt_fair_value_usd'])==80400000000
    assert all(v is None for v in equity['unresolved_operands'].values())
    assert equity['no_missing_claims_assumed_zero'] and equity['no_automatic_rsu_addition']
    # Independent fresh interpreter loads only the sealed allowlist, not this repo.
    runtime=None
    if bundle:
        code="from pathlib import Path;import json;from valuation_platform.review.pilot_cashflows import read_cashflows;print(json.dumps(read_cashflows(Path("+repr(str(bundle))+"),'AAPL')))"
        import os
        env={**os.environ,'PYTHONPATH':str(bundle/'src')}
        proc=subprocess.run([sys.executable,'-c',code],cwd='/tmp',env=env,capture_output=True,text=True,check=True)
        runtime=json.loads(proc.stdout)
    if api:
        req=urllib.request.Request(api+'/api/v1/cashflows/AAPL',headers={'Origin':'http://127.0.0.1:5193'})
        served=json.load(urllib.request.urlopen(req))
        if runtime is not None:assert served==runtime
        runtime=served
    if runtime is not None:
        assert runtime['current_resolution']==record
        old=load(ROOT/'docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json')['companies']['AAPL']
        adopted=load(ROOT/'docs/company-resolutions/AAPL/operating-fcff-2026-11-04/adopted-history.json')['periods']
        for p,q,r in zip(runtime['periods'],old['periods'],adopted,strict=True):
            assert p['fcfe']==q['fcfe']
            assert p['legacy_cfo_fcff']==q['fcff']
            assert p['fcff']['amount_usd']==r['fcff']['amount_usd']
        assert runtime['status']=='OPEN' and runtime['review_passed'] is False
    result={'date':'2026-11-04','audit_verdict':'READY_WITH_CAVEATS_FOR_SOURCE_REVIEW; NOT_READY_FOR_COMPLETE_APPLE_FCFE_OR_PER_SHARE_CERTIFICATION',
        'independent_primary_instance_fact_bindings':len(POINTS),'unique_hashed_source_bodies':len(CACHE),
        'financing_statements_reconciled':5,'provisional_fcfe_reproduced':financing,'annual_tax_component_schedules_reconciled':5,
        'forecast_component_bridges_recomputed':3,'new_financial_values_adopted':0,
        'three_existing_apple_scenario_enterprise_values_unchanged':True,
        'fresh_sealed_runtime_checked':bool(bundle),'live_api_checked':bool(api),
        'company_complete':False,'unresolved_evidence':['Other financing and actual finance-lease principal/containment','FY2024 D&A exact expense reconciliation','Cash eligibility, complete claims, non-overlapping existing awards','Economic history-to-forecast alignment and explicit forward FCFE financing'],
        'scope_limitation':'Verifies retained-source bindings and implementation controls. No issuer response obtained, no exact cash-tax inference, no PM valuation/price recommendation, and no whole-company clearance.'}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path);p.add_argument('--api');a=p.parse_args();run(a.bundle,a.api)
