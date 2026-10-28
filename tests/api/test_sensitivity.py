"""Bounded sensitivity HTTP acceptance; synthetic economics on retained anchors."""
from copy import deepcopy
from decimal import Decimal as D
import concurrent.futures
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
from valuation_platform.valuation import case_inputs as c, sensitivity_inputs as s
from tests.api.test_cases import BundleFixture, payload, blocking_worker, broken_worker
ROOT=Path(__file__).resolve().parents[2]


def document(equity=False,kind=None,maximum=False):
    case=payload(equity,kind);case.pop('analyst');case.pop('scope')
    case.update(schema_version='investor-case-v2' if equity else 'investor-case-v1',preparation={'provenance':'ANONYMOUS_INVESTOR','timestamp_utc':'2026-10-28T12:00:00Z','notes':'Software test only, not company forecasts.'})
    return {'schema_version':s.INVESTOR_SCHEMA,'sensitivity_name':'Synthetic grid acceptance','source':{'kind':'single_case','case':case,'analytical_date':case['anchor']['annual_end'],'information_cutoff':'2026-02-05'},'wacc_values':[f'0.{i:02d}' for i in range(20,31)] if maximum else ['0.02','0.25','0.30'],'terminal_growth_values':[f'0.{i:03d}' for i in range(40,51)] if maximum else ['0.02','0.05']}


class SensitivityApiTests(BundleFixture,unittest.TestCase):
    def test_validation_never_calculates_or_loads_history_and_run_matches_cli(self):
        with TestClient(create_app(self.bundle)) as client,tempfile.TemporaryDirectory() as folder:
            for equity in (False,True):
                d=document(equity);before=deepcopy(d)
                with patch.object(c,'run_case',side_effect=AssertionError('calculate')),patch.object(c,'load_revenue_anchor',side_effect=AssertionError('load')),patch.object(s,'run_sensitivity',side_effect=AssertionError('grid')),patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('spawn')):
                    out=client.post('/api/v1/sensitivity/validate',json=d);self.assertEqual(out.status_code,200,out.text);self.assertFalse(out.json()['calculation_performed'])
                out=client.post('/api/v1/sensitivity/run',json=d);self.assertEqual(out.status_code,200,out.text);self.assertEqual(out.json(),s.run_sensitivity(s.read_sensitivity(json.dumps(d)),ROOT));self.assertEqual(d,before)
                p=Path(folder)/'grid.json';p.write_text(json.dumps(d));cmd=[sys.executable,str(ROOT/'scripts/run_analyst_sensitivity.py'),str(p),'--run'];self.assertEqual(json.loads(subprocess.check_output(cmd)),out.json());self.assertIn('Anonymous investor',subprocess.check_output(cmd+['--format','summary'],text=True))
                self.assertEqual(out.headers['cache-control'],'no-store');self.assertNotIn('access-control-allow-origin',out.headers)
            legacy=json.loads((ROOT/'examples/valuation/synthetic-sensitivity-ev.json').read_text());out=client.post('/api/v1/sensitivity/run',json=legacy);self.assertEqual(out.status_code,200,out.text);self.assertEqual(out.json()['schema_version'],s.RESULT_SCHEMA)

    def test_all_retained_grids_cli_selected_cells_and_independent_arithmetic(self):
        from tests.api.test_reverse import independent
        comparisons=0;cells=0
        with TestClient(create_app(self.bundle)) as client,tempfile.TemporaryDirectory() as folder:
            for kind,equity in [(k,False) for k in c.ANCHORS]+[('meta-fy2025',True)]:
                d=document(equity,kind);d.update(wacc_values=['0.20','0.25','0.30'],terminal_growth_values=['0.02','0.05'])
                response=client.post('/api/v1/sensitivity/run',json=d);self.assertEqual(response.status_code,200,response.text);out=response.json()
                p=Path(folder)/'grid.json';p.write_text(json.dumps(d));self.assertEqual(json.loads(subprocess.check_output([sys.executable,str(ROOT/'scripts/run_analyst_sensitivity.py'),str(p),'--run'])),out)
                for cell in (out['cells'][0][0],out['cells'][-1][-1]):
                    case=deepcopy(out['selected_case']);case.update(wacc=cell['wacc'],terminal_growth=cell['terminal_growth']);p.write_text(json.dumps(case));forward=json.loads(subprocess.check_output([sys.executable,str(ROOT/'scripts/run_analyst_case.py'),str(p),'--run']));b=forward['stage_b']
                    for key in ('enterprise_value','pv_explicit_fcff','pv_terminal_value','terminal_value'):self.assertEqual(b[key],cell['metrics'][key])
                    self.assertEqual(b['terminal']['fcff'],cell['metrics']['terminal_fcff'])
                    if equity:
                        for key in ('equity_value','value_per_share'):self.assertEqual(forward['stage_c'][key],cell['metrics'][key])
                    comparisons+=independent(self,case,forward);cells+=1
        print('\nGRID_CLI_COMPARISONS 4 INDIVIDUAL_CELLS '+str(cells)+' INDEPENDENT_COMPARISONS '+str(comparisons),flush=True)

    def test_maximum_supported_dimensions_within_unchanged_http_bounds(self):
        measurements=[]
        with TestClient(create_app(self.bundle)) as client:
            for kind,equity in [(k,False) for k in c.ANCHORS]+[('aapl-fy2025',True)]:
                started=time.monotonic();out=client.post('/api/v1/sensitivity/run',json=document(equity,kind,True));elapsed=time.monotonic()-started
                self.assertEqual(out.status_code,200,out.text[:200]);self.assertEqual(len(out.json()['cells']),11);self.assertEqual(len(out.json()['cells'][0]),11);self.assertLess(len(out.content),2*1024*1024);self.assertLess(elapsed,35)
                measurements.append({'anchor':kind,'equity':equity,'seconds':round(elapsed,3),'response_bytes':len(out.content)})
        print('\nMAX_GRID_MEASUREMENTS '+json.dumps(measurements),flush=True)

    def test_invalid_pairs_all_invalid_grid_and_resource_rejection_before_spawn(self):
        with TestClient(create_app(self.bundle)) as client:
            mixed=client.post('/api/v1/sensitivity/run',json=document());self.assertEqual(mixed.status_code,200,mixed.text);cell=mixed.json()['cells'][0][0];self.assertEqual(cell['status'],'INVALID');self.assertTrue(all(v is None for v in cell['metrics'].values()));self.assertIsNone(cell['changes'])
            edits=[(lambda d:d.update(wacc_values=['0.01']),'all cells invalid'),(lambda d:d.update(wacc_values=['0.01']*12),'1 to 11'),(lambda d:d.update(wacc_values=['1e101']),'numeric'),(lambda d:d['source'].update(information_cutoff=None),'information_cutoff'),(lambda d:d['source']['case']['anchor'].update(cik=1),'anchor'),(lambda d:d['source']['case']['bridge'].update(unresolved_requirements=['unresolved']),'unresolved_requirements')]
            with patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('spawn')):
                for edit,field in edits:
                    d=document(True);edit(d)
                    for route in ('validate','run'):
                        out=client.post('/api/v1/sensitivity/'+route,json=d);self.assertEqual(out.status_code,422,out.text);self.assertIn(field,out.text)
                raw=json.dumps(document()).replace('"wacc_values":','"wacc_values":[],"wacc_values":',1);self.assertEqual(client.post('/api/v1/sensitivity/run',content=raw,headers={'Content-Type':'application/json'}).status_code,422)
                self.assertEqual(client.post('/api/v1/sensitivity/run?deadline=100',json=document()).status_code,422)
                self.assertEqual(client.post('/api/v1/sensitivity/run',content=b'x'*(256*1024+1),headers={'Content-Type':'application/json'}).status_code,413)
                self.assertEqual(client.post('/api/v1/sensitivity/run',json=document(),headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)

    def test_signed_and_zero_metrics_preserve_undefined_ratios(self):
        with TestClient(create_app(self.bundle)) as client:
            for margin in ('0','-0.10'):
                d=document();case=d['source']['case'];case['terminal'].update(operating_margin=margin,d_and_a_percent_revenue='0',investment_percent_revenue='0',working_capital_cash_requirement_percent_revenue='0')
                for y in case['forecast_years']:y.update(operating_margin=margin,d_and_a_percent_revenue='0',capex_percent_revenue='0',change_in_operating_nwc_percent_revenue='0')
                out=client.post('/api/v1/sensitivity/run',json=d);self.assertEqual(out.status_code,200,out.text)
                for row in out.json()['cells']:
                    for cell in row:
                        if cell['status']=='VALID':
                            if margin=='0':self.assertEqual(D(cell['metrics']['enterprise_value']),0);self.assertIsNone(cell['metrics']['terminal_contribution'])
                            else:self.assertLess(D(cell['metrics']['enterprise_value']),0)

    def test_worker_timeout_failure_budget_and_cross_action_gate_recovery(self):
        ctx=multiprocessing.get_context('spawn');started,release=ctx.Event(),ctx.Event()
        with TestClient(create_app(self.bundle,policy=ServerPolicy(deadline_seconds=1),worker_target=blocking_worker,worker_args=(started,release))) as client:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pending=pool.submit(client.post,'/api/v1/sensitivity/run',json=document());self.assertTrue(started.wait(5))
                for path in ('cases','scenarios','sensitivity'):self.assertEqual(client.post('/api/v1/'+path+'/run',json={}).status_code,503)
                self.assertEqual(client.post('/api/v1/sensitivity/validate',json=document()).status_code,200);self.assertEqual(pending.result().status_code,504)
            self.assertIsNone(client.app.state.calculator.job)
            from valuation_platform.api.worker import calculate
            client.app.state.calculator.target=calculate;client.app.state.calculator.target_args=();self.assertEqual(client.post('/api/v1/sensitivity/run',json=document()).status_code,200)
        for options,status in [({'worker_target':broken_worker},500),({'policy':ServerPolicy(max_response_bytes=8192)},422)]:
            with TestClient(create_app(self.bundle,**options)) as client:
                out=client.post('/api/v1/sensitivity/run',json=document());self.assertEqual(out.status_code,status,out.text);self.assertIsNone(client.app.state.calculator.job);self.assertNotIn('Traceback',out.text)
