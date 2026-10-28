"""Bounded scenario HTTP adapter; synthetic assumptions and retained anchors only."""
from copy import deepcopy
import json
import multiprocessing
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.budget import ServerPolicy, read_http_scenarios
from valuation_platform.valuation import case_inputs as c, scenario_inputs as s
from tests.api.test_cases import BundleFixture, payload, blocking_worker, broken_worker


def document(equity=False, kind=None):
    case=payload(equity,kind);case.pop('analyst');case.pop('scope')
    case.update(schema_version='investor-case-v2' if equity else 'investor-case-v1',
                preparation={'provenance':'ANONYMOUS_INVESTOR','timestamp_utc':'2026-10-28T12:00:00Z','notes':None})
    return {'schema_version':s.INVESTOR_SCHEMA,'scenario_set_name':'Synthetic software comparison',
            'scenarios':[{'label':label,'analytical_date':case['anchor']['annual_end'],
                          'information_cutoff':'2026-02-05','case':deepcopy(case)} for label in s.LABELS]}


class ScenarioApiTests(BundleFixture,unittest.TestCase):
    def test_validation_no_calculation_or_anchor_access_and_anonymous_trace(self):
        with TestClient(create_app(self.bundle)) as client:
            with patch.object(c,'run_case',side_effect=AssertionError('calculate')),patch.object(c,'load_revenue_anchor',side_effect=AssertionError('history')),patch.object(s,'run_scenario_set',side_effect=AssertionError('scenario calculation')):
                for equity in (False,True):
                    out=client.post('/api/v1/scenarios/validate',json=document(equity))
                    self.assertEqual(out.status_code,200,out.text);self.assertFalse(out.json()['calculation_performed'])
            for equity in (False,True):
                d=document(equity);before=deepcopy(d);out=client.post('/api/v1/scenarios/run',json=d)
                self.assertEqual(out.status_code,200,out.text);result=out.json()
                self.assertEqual(result,s.run_scenario_set(s.read_scenario_set(json.dumps(d)),Path(__file__).resolve().parents[2]))
                self.assertEqual(result['schema_version'],s.INVESTOR_RESULT_SCHEMA);self.assertEqual(d,before)
                self.assertEqual(result['scenarios'][0]['result']['stage_b'],result['scenarios'][2]['result']['stage_b'])
                self.assertNotIn('analyst',result['submitted_inputs']['scenarios'][0]['case'])

    def test_comparability_missing_cases_scope_and_strict_numeric_limits(self):
        edits=[(lambda d:d['scenarios'].pop(),'scenarios'),
               (lambda d:d['scenarios'][1].update(information_cutoff=None),'information_cutoff'),
               (lambda d:d['scenarios'][1]['case']['forecast_years'][0].update(forecast_tax_rate='1.5'),'forecast_tax_rate'),
               (lambda d:d['scenarios'][1]['case'].update(wacc='1e101'),'numeric'),
               (lambda d:d['scenarios'][1]['case']['bridge']['shares'].update(shares='21'),'bridge'),
               (lambda d:d['scenarios'][1]['case']['bridge'].update(unresolved_requirements=['Missing claim']),'unresolved_requirements'),
               (lambda d:d['scenarios'][1]['case']['anchor'].update(cik=1),'anchor'),
               (lambda d:d.update(output='/tmp/no'),'unknown field')]
        with TestClient(create_app(self.bundle)) as client:
            with patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('spawn before validation')):
                for edit,field in edits:
                    d=document(True);edit(d)
                    for route in ('validate','run'):
                        out=client.post('/api/v1/scenarios/'+route,json=d);self.assertEqual(out.status_code,422,out.text);self.assertIn(field,out.text)
                text=json.dumps(document()).replace('"wacc": "0.25"','"wacc":"0.25","wacc":"0.3"',1)
                self.assertEqual(client.post('/api/v1/scenarios/run',content=text,headers={'Content-Type':'application/json'}).status_code,422)
                self.assertEqual(client.post('/api/v1/scenarios/run?deadline=100',json=document()).status_code,422)
                self.assertEqual(client.post('/api/v1/scenarios/run',content=b'x'*(256*1024+1),headers={'Content-Type':'application/json'}).status_code,413)
                self.assertEqual(client.post('/api/v1/scenarios/run',json=document(),headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)

    def test_legacy_scenario_contract_cli_summary_and_individual_compatibility(self):
        import subprocess,sys
        root=Path(__file__).resolve().parents[2]
        with TestClient(create_app(self.bundle)) as client,tempfile.TemporaryDirectory() as folder:
            for kind in c.ANCHORS:
                d=document(kind=kind);d['scenarios'][0]['case']['forecast_years'][0]['operating_margin']='-0.10'
                out=client.post('/api/v1/scenarios/run',json=d);self.assertEqual(out.status_code,200,out.text)
                p=Path(folder)/'case.json';p.write_text(json.dumps(d));command=[sys.executable,str(root/'scripts/run_analyst_scenarios.py'),str(p),'--run']
                self.assertEqual(json.loads(subprocess.check_output(command)),out.json())
                self.assertIn('Anonymous investor',subprocess.check_output(command+['--format','summary'],text=True))
                for entry in out.json()['scenarios']:
                    single=client.post('/api/v1/cases/run',json=entry['result']['submitted_inputs']);self.assertEqual(single.json(),entry['result'])
            old=json.loads((root/'examples/valuation/synthetic-scenarios-ev.json').read_text())
            result=client.post('/api/v1/scenarios/run',json=old);self.assertEqual(result.status_code,200,result.text);self.assertEqual(result.json()['schema_version'],s.RESULT_SCHEMA)

    def test_worker_failure_timeout_result_budget_and_shared_gate_recover(self):
        ctx=multiprocessing.get_context('spawn');started,release=ctx.Event(),ctx.Event()
        with TestClient(create_app(self.bundle,policy=ServerPolicy(deadline_seconds=1),worker_target=blocking_worker,worker_args=(started,release))) as client:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pending=pool.submit(client.post,'/api/v1/scenarios/run',json=document());self.assertTrue(started.wait(5))
                self.assertEqual(client.post('/api/v1/cases/run',json=payload()).status_code,503)
                self.assertEqual(client.post('/api/v1/scenarios/run',json=document()).status_code,503)
                self.assertEqual(client.post('/api/v1/scenarios/validate',json=document()).status_code,200)
                self.assertEqual(pending.result().status_code,504)
            self.assertIsNone(client.app.state.calculator.job)
            from valuation_platform.api.worker import calculate
            client.app.state.calculator.target=calculate;client.app.state.calculator.target_args=()
            self.assertEqual(client.post('/api/v1/scenarios/run',json=document()).status_code,200)
        with TestClient(create_app(self.bundle,worker_target=broken_worker)) as client:
            out=client.post('/api/v1/scenarios/run',json=document());self.assertEqual(out.status_code,500);self.assertNotIn('Traceback',out.text);self.assertIsNone(client.app.state.calculator.job)
        with TestClient(create_app(self.bundle,policy=ServerPolicy(max_response_bytes=8192))) as client:
            out=client.post('/api/v1/scenarios/run',json=document());self.assertEqual(out.status_code,422);self.assertEqual(out.json()['error']['code'],'response_budget');self.assertIsNone(client.app.state.calculator.job)
