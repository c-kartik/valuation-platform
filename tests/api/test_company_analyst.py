"""Metadata and live isolated execution for two named analyst consumers."""
import copy
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.bundle import build_bundle, remove_bundle
from valuation_platform.review.company_analyst import analyst_profile, run_company_analyst
from tests.review.test_company_analyst import document
from tests.review.test_apple_analyst import document as apple_document

ROOT=Path(__file__).resolve().parents[2]


class CompanyAnalystApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.bundle=Path(cls.temp.name)/'private';build_bundle(ROOT,cls.bundle)
        cls.documents={t:document(t) for t in ('META','GOOGL')}

    @classmethod
    def tearDownClass(cls):remove_bundle(cls.bundle);cls.temp.cleanup()

    def test_metadata_is_pinned_issuer_specific_and_does_not_execute_valuation(self):
        with TestClient(create_app(self.bundle)) as c:
            for t in self.documents:
                response=c.get('/api/v1/analyst/'+t)
                self.assertEqual(response.status_code,200,response.text)
                self.assertEqual(response.json(),analyst_profile(ROOT,t))
                self.assertEqual(response.headers['cache-control'],'no-store')
            self.assertEqual(c.get('/api/v1/analyst/MSFT').status_code,404)
            self.assertEqual(c.get('/api/v1/analyst/META?default=1').status_code,422)

    def test_both_sealed_workers_return_five_outputs_and_match_direct_execution(self):
        with TestClient(create_app(self.bundle)) as c:
            for t,d in self.documents.items():
                response=c.post('/api/v1/analyst/run',json=d)
                self.assertEqual(response.status_code,200,response.text)
                self.assertEqual(response.json(),run_company_analyst(d,ROOT))
                self.assertEqual(len(response.json()['readiness']),5)
                self.assertEqual(len(response.json()['historical']),5)
                self.assertFalse(response.json()['fcfe']['debt_subtracted_after_fcfe_discounting'])
                self.assertLess(len(response.content),192*1024)

    def test_editable_claims_and_ten_year_requests_reach_current_consumer(self):
        with TestClient(create_app(self.bundle)) as c:
            for t,d in self.documents.items():
                old=c.post('/api/v1/analyst/run',json=d).json()
                updated=copy.deepcopy(d);updated['assumptions']['additional_claims_usd']='10000000000'
                new=c.post('/api/v1/analyst/run',json=updated)
                self.assertEqual(new.status_code,200,new.text)
                self.assertNotEqual(old['fcff']['value_per_share_usd'],new.json()['fcff']['value_per_share_usd'])
                ten=c.post('/api/v1/analyst/run',json=document(t,horizon=10))
                self.assertEqual(ten.status_code,200,ten.text)
                self.assertEqual(len(ten.json()['fcfe']['years']),10)

    def test_mismatched_sources_ownership_and_failed_calculations_do_not_leak_paths(self):
        with TestClient(create_app(self.bundle)) as c:
            for mutate in (lambda d:d.update(ticker='GOOGL'),lambda d:d['assumptions'].update(nci_claim_usd='1'),
                           lambda d:d['assumptions'].update(cost_of_equity='NaN'),lambda d:d['assumptions'].update(operating_cash_reserve_ratio='1')):
                d=copy.deepcopy(self.documents['META']);mutate(d);response=c.post('/api/v1/analyst/run',json=d)
                self.assertEqual(response.status_code,422,response.text)
                self.assertNotIn('/Users',response.text)
            self.assertEqual(c.post('/api/v1/analyst/run?issuer=META',json=self.documents['META']).status_code,422)

    def test_apple_and_original_three_issuer_evidence_records_are_preserved(self):
        with TestClient(create_app(self.bundle)) as c:
            old={t:c.get('/api/v1/cashflows/'+t).json() for t in ('META','GOOGL','AAPL')}
            apple=c.post('/api/v1/apple/analyst/run',json=apple_document()).json()
            for d in self.documents.values():self.assertEqual(c.post('/api/v1/analyst/run',json=d).status_code,200)
            self.assertEqual(old,{t:c.get('/api/v1/cashflows/'+t).json() for t in old})
            self.assertEqual(apple,c.post('/api/v1/apple/analyst/run',json=apple_document()).json())


if __name__=='__main__':unittest.main()
