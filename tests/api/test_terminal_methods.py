"""Bounded HTTP/CLI agreement for explicit terminal methods; synthetic inputs only."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.api.test_cases import BundleFixture, ROOT
from tests.valuation.test_terminal_methods import method_document, grid_document, execute
from valuation_platform.api.app import create_app
from valuation_platform.review.comparison import run_review


class TerminalApiTests(BundleFixture,unittest.TestCase):
    def test_both_methods_both_scopes_exact_cli_api_and_review_comparison(self):
        with TestClient(create_app(self.bundle)) as client,tempfile.TemporaryDirectory() as directory:
            for exit in (False,True):
                for equity in (False,True):
                    doc=method_document(exit,equity,True);before=deepcopy(doc)
                    valid=client.post('/api/v1/cases/validate',json=doc)
                    self.assertEqual(valid.status_code,200,valid.text);self.assertFalse(valid.json()['calculation_performed'])
                    response=client.post('/api/v1/cases/run',json=doc)
                    self.assertEqual(response.status_code,200,response.text)
                    self.assertEqual(response.json(),execute(doc))
                    source=Path(directory)/'case.json';source.write_text(json.dumps(doc))
                    output=subprocess.check_output([sys.executable,str(ROOT/'scripts/run_analyst_case.py'),str(source),'--run'],cwd=ROOT)
                    self.assertEqual(json.loads(output),response.json());self.assertEqual(before,doc)
                    review=client.post('/api/v1/review/run',json=doc)
                    self.assertEqual(review.status_code,200,review.text)
                    self.assertEqual(review.json()['result'],response.json())
                    if exit:self.assertTrue(any('UNSUPPORTED_TERMINAL_METHOD' in s for s in review.json()['review']['reasons']))

    def test_validation_has_no_execution_and_useful_errors(self):
        with TestClient(create_app(self.bundle)) as client,patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('no calculation')):
            for value in (None,'0','-1','15%'):
                doc=method_document();doc['terminal_valuation']['exit_ev_ebit_multiple']=value
                response=client.post('/api/v1/cases/validate',json=doc)
                self.assertEqual(response.status_code,422,response.text)
                self.assertIn('exit_ev_ebit_multiple',response.text)
            self.assertEqual(client.post('/api/v1/cases/validate',json=method_document()).status_code,200)

    def test_exit_grid_and_scenarios_through_bounded_worker(self):
        from valuation_platform.valuation.sensitivity_inputs import read_sensitivity,run_sensitivity
        from valuation_platform.valuation.scenario_inputs import LABELS,read_scenario_set,run_scenario_set
        with TestClient(create_app(self.bundle)) as client:
            doc=grid_document(True)
            r=client.post('/api/v1/sensitivity/run',json=doc);self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(r.json(),run_sensitivity(read_sensitivity(json.dumps(doc)),ROOT))
            scenarios=dict(schema_version='investor-scenario-set-v3',scenario_set_name='Synthetic',scenarios=[dict(label=l,analytical_date='2025-12-31',information_cutoff=None,case=method_document(investor=True)) for l in LABELS])
            r=client.post('/api/v1/scenarios/run',json=scenarios);self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(r.json(),run_scenario_set(read_scenario_set(json.dumps(scenarios)),ROOT))

    def test_maximum_exit_grid_within_unchanged_budget_and_reverse_rejection(self):
        from decimal import Decimal as D
        from tests.valuation.test_reverse import document as reverse_document
        with TestClient(create_app(self.bundle)) as client:
            doc=grid_document(True)
            doc['wacc_values']=[str(D(i)/100) for i in range(1,12)]
            doc['exit_ev_ebit_multiple_values']=[str(i) for i in range(10,21)]
            response=client.post('/api/v1/sensitivity/run',json=doc)
            self.assertEqual(response.status_code,200,response.text)
            result=response.json();self.assertEqual(len(result['cells']),11);self.assertTrue(all(len(row)==11 for row in result['cells']))
            self.assertTrue(all(cell['status']=='VALID' for row in result['cells'] for cell in row))
            self.assertLess(len(response.content),2*1024*1024)
            reverse=reverse_document();reverse['source']=dict(kind='single_case',case=method_document(),analytical_date='2025-12-31',information_cutoff='2026-01-29')
            response=client.post('/api/v1/reverse/validate',json=reverse)
            self.assertEqual(response.status_code,422);self.assertIn('UNSUPPORTED_TERMINAL_METHOD',response.text)
