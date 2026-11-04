"""Actual isolated HTTP worker and sealed-source integration for Apple."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.bundle import build_bundle, remove_bundle
from valuation_platform.review.apple_analyst import run_apple_analyst
from tests.review.test_apple_analyst import document

ROOT = Path(__file__).resolve().parents[2]


class AppleAnalystApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.bundle = Path(cls.temp.name) / 'private'; build_bundle(ROOT, cls.bundle)
        cls.doc = document()

    @classmethod
    def tearDownClass(cls):
        remove_bundle(cls.bundle); cls.temp.cleanup()

    def test_sealed_worker_publishes_all_five_current_outputs(self):
        with TestClient(create_app(self.bundle)) as client:
            result = client.post('/api/v1/apple/analyst/run', json=self.doc)
            self.assertEqual(result.status_code, 200, result.text)
            self.assertEqual(result.json(), run_apple_analyst(self.doc, ROOT))
            self.assertEqual(len(result.json()['historical']), 5)
            self.assertEqual(len(result.json()['readiness']), 5)
            self.assertEqual(result.headers.get('cache-control'), 'no-store')
            for method in ('fcff', 'fcfe'):
                self.assertIsNotNone(result.json()[method]['value_per_share_usd'])

    def test_recalculation_follows_input_changes_and_ten_year_horizon(self):
        with TestClient(create_app(self.bundle)) as client:
            old = client.post('/api/v1/apple/analyst/run', json=self.doc).json()
            changed = copy.deepcopy(self.doc); changed['assumptions']['additional_claims_usd'] = '10000000000'
            new = client.post('/api/v1/apple/analyst/run', json=changed)
            self.assertEqual(new.status_code, 200, new.text)
            self.assertNotEqual(old['fcff']['value_per_share_usd'], new.json()['fcff']['value_per_share_usd'])
            ten = client.post('/api/v1/apple/analyst/run', json=document(horizon=10))
            self.assertEqual(ten.status_code, 200, ten.text)
            self.assertEqual(len(ten.json()['fcfe']['years']), 10)

    def test_invalid_inputs_rejected_without_paths_or_number_invention(self):
        with TestClient(create_app(self.bundle)) as client:
            for key, value in [('rsu_vesting_fraction', '2'), ('cost_of_equity', '0.01'), ('operating_cash_reserve_ratio', '1')]:
                doc = copy.deepcopy(self.doc); doc['assumptions'][key] = value
                response = client.post('/api/v1/apple/analyst/run', json=doc)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertNotIn('/Users', response.text)
            self.assertEqual(client.post('/api/v1/apple/analyst/run?company=META', json=self.doc).status_code, 422)
            nonapple = copy.deepcopy(self.doc); nonapple['base_case']['anchor']['kind'] = 'meta-fy2025'
            self.assertEqual(client.post('/api/v1/apple/analyst/run', json=nonapple).status_code, 422)

    def test_original_issuer_evidence_records_and_other_companies_are_unchanged(self):
        with TestClient(create_app(self.bundle)) as client:
            before = {t: client.get('/api/v1/cashflows/' + t).json() for t in ('AAPL', 'META', 'GOOGL')}
            self.assertEqual(client.post('/api/v1/apple/analyst/run', json=self.doc).status_code, 200)
            after = {t: client.get('/api/v1/cashflows/' + t).json() for t in before}
            self.assertEqual(before, after)
            self.assertFalse(after['AAPL']['review_passed'])
            self.assertIsNone(after['AAPL']['periods'][0]['fcfe']['parent_common_amount_usd'])


if __name__ == '__main__': unittest.main()
