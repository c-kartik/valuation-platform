import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.bundle import build_bundle, remove_bundle
from valuation_platform.review.pilot_cashflows import read_cashflows, RESOURCE
from tests.valuation.test_fcfe import document
ROOT=Path(__file__).resolve().parents[2]

class CashFlowApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.bundle=Path(cls.temp.name)/'private';build_bundle(ROOT,cls.bundle)
    @classmethod
    def tearDownClass(cls):remove_bundle(cls.bundle);cls.temp.cleanup()

    def test_all_thirty_records_reach_runtime_without_clearing_gaps(self):
        with TestClient(create_app(self.bundle)) as client:
            missing=[]
            for ticker in ('AAPL','META','GOOGL'):
                r=client.get('/api/v1/cashflows/'+ticker);self.assertEqual(r.status_code,200);d=r.json()
                self.assertEqual(d,read_cashflows(ROOT,ticker));self.assertFalse(d['review_passed']);self.assertEqual(d['status'],'OPEN')
                self.assertEqual([p['fiscal_year'] for p in d['periods']],list(range(2021,2026)))
                for p in d['periods']:
                    if p['fcff']['amount_usd'] is None:missing.append((ticker,p['fiscal_year']))
                    self.assertIsNotNone(p['fcfe']['amount_usd']);self.assertFalse(p['fcfe']['cleared']);self.assertIsNone(p['fcfe']['parent_common_amount_usd'])
            self.assertEqual(missing,[])
            a=client.get('/api/v1/cashflows/AAPL').json()
            self.assertEqual([p['legacy_cfo_fcff']['amount_usd'] is None for p in a['periods']],[False,False,False,True,True])
            self.assertEqual(client.get('/api/v1/cashflows/MSFT').status_code,404)
            self.assertEqual(client.get('/api/v1/cashflows/AAPL?year=2025').status_code,422)
            self.assertEqual(client.get('/api/v1/cashflows/aapl').status_code,200)

    def test_actual_fcfe_worker_and_failure_diagnostics(self):
        with TestClient(create_app(self.bundle)) as client:
            d=document();v=client.post('/api/v1/fcfe/validate',json=d);self.assertEqual(v.status_code,200);self.assertFalse(v.json()['calculation_performed'])
            r=client.post('/api/v1/fcfe/run',json=d);self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(r.json()['equity_value_usd'],'80.000000000000000000000000000000000000000000000000')
            self.assertFalse(r.json()['debt_subtracted_after_fcfe_discounting'])
            d['terminal_financing']['cash_debt_issued_usd']='1'
            fail=client.post('/api/v1/fcfe/run',json=d);self.assertEqual(fail.status_code,422,fail.text)
            self.assertIn('terminal_financing',fail.text);self.assertNotIn('/Users',fail.text)
            del d['financing_years'][0]['interest_expense_usd']
            self.assertEqual(client.post('/api/v1/fcfe/validate',json=d).status_code,422)

    def test_reader_rejects_ownership_and_clearance_tampering(self):
        original=json.loads((ROOT/RESOURCE).read_text())
        for field,value in [('parent_common_amount_usd','1'),('cleared',True),('status','VERIFIED')]:
            d=copy.deepcopy(original);d['companies']['AAPL']['periods'][0]['fcfe'][field]=value
            with patch.object(Path,'read_text',return_value=json.dumps(d)):
                with self.assertRaises(ValueError):read_cashflows(ROOT,'AAPL')

if __name__=='__main__':unittest.main()
