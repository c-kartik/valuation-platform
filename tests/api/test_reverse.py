"""Reverse HTTP integration; synthetic economics, retained revenue, no actual forecasts."""
from copy import deepcopy
from decimal import Decimal as D
import concurrent.futures
from fractions import Fraction as F
import json
import multiprocessing
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.budget import ServerPolicy
from valuation_platform.valuation import case_inputs as c, reverse_inputs as r
from tests.api.test_cases import BundleFixture, blocking_worker
from tests.api.test_sensitivity import document as grid
from tests.valuation.test_reverse import document as legacy, zero_case
ROOT=Path(__file__).resolve().parents[2]


def document(equity=False,kind=None,growth='0.073456789123'):
    case=grid(equity,kind)['source']['case']
    changed=deepcopy(case)
    for y in changed['forecast_years']:y['revenue_growth']=growth
    forward=c.run_case(c.read_case(json.dumps(changed)),ROOT)
    return {'schema_version':r.INVESTOR_SCHEMA,'reverse_dcf_name':'Synthetic conditional growth test','source':{'kind':'single_case','case':case,'analytical_date':case['anchor']['annual_end'],'information_cutoff':'2026-02-05'},'target':{'metric':'VALUE_PER_SHARE' if equity else 'ENTERPRISE_VALUE','amount':forward['stage_c']['value_per_share'] if equity else forward['stage_b']['enterprise_value'],'unit':'USD/share' if equity else 'USD','date':case['anchor']['annual_end']},'growth_bounds':{'lower':'0','upper':'0.2'}}


def independent(test,case,forward):
    """Exact rational arithmetic, separately structured; fixed precision tolerance only at comparison."""
    b=forward['stage_b'];revenue=F(b['stage_a']['anchor']['revenue']);pv=F(0);w=F(case['wacc']);g=F(case['terminal_growth']);count=0
    def equal(actual,expected):
        nonlocal count
        test.assertLessEqual(abs(F(actual)-expected),F('1e-30')+abs(expected)*F('1e-46'));count+=1
    for i,(y,actual,discounted) in enumerate(zip(case['forecast_years'],b['stage_a']['years'],b['years']),1):
        revenue*=1+F(y['revenue_growth']);ebit=revenue*F(y['operating_margin']);tax=max(ebit,F(0))*F(y['forecast_tax_rate']);da=revenue*F(y['d_and_a_percent_revenue']);investment=revenue*F(y['capex_percent_revenue']);wc=revenue*F(y['change_in_operating_nwc_percent_revenue']);fcff=ebit-tax+da-investment-wc;factor=1/(1+w)**i
        for key,value in dict(revenue=revenue,ebit=ebit,tax=tax,nopat=ebit-tax,d_and_a=da,investment=investment,working_capital_cash_requirement=wc,fcff=fcff).items():equal(actual[key],value)
        equal(discounted['discount_factor'],factor);equal(discounted['pv_fcff'],fcff*factor);pv+=fcff*factor
    t=case['terminal'];tr=revenue*(1+g);ebit=tr*F(t['operating_margin']);fcff=ebit-max(ebit,F(0))*F(t['operating_tax_rate'])+tr*(F(t['d_and_a_percent_revenue'])-F(t['investment_percent_revenue'])-F(t['working_capital_cash_requirement_percent_revenue']));tv=fcff/(w-g);tpv=tv/(1+w)**5;ev=pv+tpv
    for actual,expected in [(b['terminal']['fcff'],fcff),(b['terminal_value'],tv),(b['pv_explicit_fcff'],pv),(b['pv_terminal_value'],tpv),(b['enterprise_value'],ev)]:equal(actual,expected)
    if 'stage_c' in forward:
        bridge=case['bridge'];net=sum((F(x['amount'])*(1 if x['role']=='ELIGIBLE_ASSET' else -1) for x in bridge['components']),F(0));shares=F(bridge['shares']['shares']);equal(forward['stage_c']['equity_value'],ev+net);equal(forward['stage_c']['value_per_share'],(ev+net)/shares)
    return count


class ReverseApiTests(BundleFixture,unittest.TestCase):
    def test_validation_is_calculation_free_and_both_scopes_match_cli_all_anchors(self):
        checks=0;measurements=[]
        with TestClient(create_app(self.bundle)) as client,tempfile.TemporaryDirectory() as folder:
            for kind in c.ANCHORS:
                for equity in (False,True):
                    d=document(equity,kind);before=deepcopy(d)
                    with patch.object(c,'run_case',side_effect=AssertionError('forward')),patch.object(r,'_certificate',side_effect=AssertionError('certificate')),patch.object(r,'run_reverse',side_effect=AssertionError('solve')),patch.object(c,'load_revenue_anchor',side_effect=AssertionError('history')),patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('spawn')):
                        out=client.post('/api/v1/reverse/validate',json=d);self.assertEqual(out.status_code,200,out.text);self.assertFalse(out.json()['calculation_performed'])
                    started=time.monotonic();out=client.post('/api/v1/reverse/run',json=d);elapsed=time.monotonic()-started;self.assertEqual(out.status_code,200,out.text[:300]);v=out.json();self.assertEqual(v['status'],'SUCCESS');sol=v['solution'];self.assertLessEqual(abs(D(sol['constant_annual_growth'])-D('0.073456789123')),D('1e-12'))
                    p=Path(folder)/'reverse.json';p.write_text(json.dumps(d));cmd=[sys.executable,str(ROOT/'scripts/run_analyst_reverse_dcf.py'),str(p),'--run'];self.assertEqual(json.loads(subprocess.check_output(cmd)),v);self.assertIn('Anonymous investor',subprocess.check_output(cmd+['--format','summary'],text=True));fresh=c.run_case(c.read_case(json.dumps(sol['forward_result']['submitted_inputs'])),ROOT);self.assertEqual(fresh,sol['forward_result']);checks+=independent(self,fresh['submitted_inputs'],fresh);self.assertEqual(d,before)
                    measurements.append(dict(anchor=kind,equity=equity,seconds=round(elapsed,3),response_bytes=len(out.content),evaluations=v['evaluations']))
        print('\nREVERSE_MEASUREMENTS '+json.dumps(measurements)+' INDEPENDENT_COMPARISONS '+str(checks),flush=True)

    def test_statuses_endpoint_inconclusive_flat_and_legacy_compatibility(self):
        with TestClient(create_app(self.bundle)) as client:
            d=document(growth='0');out=client.post('/api/v1/reverse/run',json=d);self.assertEqual(out.json()['status'],'SUCCESS');self.assertTrue(out.json()['solution']['exact_endpoint'])
            d=document();d['target']['amount']='-100000';out=client.post('/api/v1/reverse/run',json=d);self.assertEqual(out.json()['status'],'UNREACHABLE_TARGET');self.assertIsNone(out.json()['solution'])
            d=legacy();zero_case(d);out=client.post('/api/v1/reverse/run',json=d);self.assertEqual(out.json()['status'],'FLAT_RESPONSE');self.assertIsNone(out.json()['solution']);self.assertEqual(out.json()['schema_version'],r.RESULT_SCHEMA)
            case=d['source']['case'];case['forecast_years'][0]['d_and_a_percent_revenue']='1.25';case['forecast_years'][1]['capex_percent_revenue']='0.625';d['growth_bounds']={'lower':'0','upper':'1'};out=client.post('/api/v1/reverse/run',json=d);self.assertEqual(out.json()['status'],'UNIQUENESS_NOT_CERTIFIED');self.assertIsNone(out.json()['solution'])

    def test_bad_intake_stops_before_worker_and_retains_existing_budgets(self):
        with TestClient(create_app(self.bundle)) as client,patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('spawn')):
            for change,field in [(lambda d:d['growth_bounds'].update(lower='0.3'),'growth_bounds'),(lambda d:d['growth_bounds'].update(upper='1e101'),'numeric'),(lambda d:d['target'].update(date='2026-01-01'),'target.date'),(lambda d:d['target'].update(unit='USD/share'),'target.unit'),(lambda d:d['target'].update(metric='VALUE_PER_SHARE',unit='USD/share'),'equity/share'),(lambda d:d['source']['case']['bridge'].update(unresolved_requirements=['pending']),'unresolved_requirements')]:
                d=document(field=='unresolved_requirements');change(d)
                for route in ('validate','run'):
                    out=client.post('/api/v1/reverse/'+route,json=d);self.assertEqual(out.status_code,422,out.text);self.assertIn(field,out.text)
            self.assertEqual(client.post('/api/v1/reverse/run?iterations=999',json=document()).status_code,422)
            self.assertEqual(client.post('/api/v1/reverse/run',json=document(),headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)
            self.assertEqual(client.post('/api/v1/reverse/run',content=b'x'*(256*1024+1),headers={'Content-Type':'application/json'}).status_code,413)

    def test_demanding_rational_work_extreme_permitted_inputs_and_fixed_iteration_ceiling(self):
        samples=[]
        with TestClient(create_app(self.bundle)) as client:
            for kind in c.ANCHORS:
                d=document(True,kind);d['growth_bounds']={'lower':'-1','upper':'1e100'};d['target']['amount']='1e100';case=d['source']['case'];case['wacc']='0.2500000000000000000000000000000000000000000000000000000000000001';case['terminal_growth']='0.25'
                started=time.monotonic();out=client.post('/api/v1/reverse/run',json=d);elapsed=time.monotonic()-started;self.assertEqual(out.status_code,200,out.text[:300]);self.assertIsNone(out.json()['solution']);self.assertIn(out.json()['status'],('ITERATION_LIMIT','UNIQUENESS_NOT_CERTIFIED','NUMERICAL_VERIFICATION_FAILED'));self.assertLessEqual(out.json()['iterations'],128);self.assertLess(elapsed,35);self.assertLess(len(out.content),2*1024*1024);samples.append(dict(anchor=kind,seconds=round(elapsed,3),response_bytes=len(out.content),status=out.json()['status']))
        print('\nDEMANDING_REVERSE_MEASUREMENTS '+json.dumps(samples),flush=True)

    def test_shared_gate_timeout_cleanup_and_response_budget(self):
        ctx=multiprocessing.get_context('spawn');started,release=ctx.Event(),ctx.Event()
        with TestClient(create_app(self.bundle,policy=ServerPolicy(deadline_seconds=1),worker_target=blocking_worker,worker_args=(started,release))) as client:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pending=pool.submit(client.post,'/api/v1/reverse/run',json=document());self.assertTrue(started.wait(5))
                for action in ('cases','scenarios','sensitivity','reverse'):self.assertEqual(client.post('/api/v1/'+action+'/run',json={}).status_code,503)
                self.assertEqual(client.post('/api/v1/reverse/validate',json=document()).status_code,200);self.assertEqual(pending.result().status_code,504)
            self.assertIsNone(client.app.state.calculator.job)
            from valuation_platform.api.worker import calculate
            client.app.state.calculator.target=calculate;client.app.state.calculator.target_args=();self.assertEqual(client.post('/api/v1/reverse/run',json=document(growth='0.1')).status_code,200)
        with TestClient(create_app(self.bundle,policy=ServerPolicy(max_response_bytes=8192))) as client:
            self.assertEqual(client.post('/api/v1/reverse/run',json=document()).status_code,422);self.assertIsNone(client.app.state.calculator.job)
