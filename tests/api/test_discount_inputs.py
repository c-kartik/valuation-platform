import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from valuation_platform.api.app import create_app
from valuation_platform.api.bundle import build_bundle,remove_bundle
from valuation_platform.preload.generate import generate
from valuation_platform.review.discount_inputs import discount_inputs
ROOT=Path(__file__).resolve().parents[2]
class DiscountApiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.bundle=Path(cls.tmp.name)/'bundle';build_bundle(ROOT,cls.bundle)
 @classmethod
 def tearDownClass(cls):remove_bundle(cls.bundle);cls.tmp.cleanup()
 def test_all_saved_rates_sources_and_inputs_unchanged_no_calculation(self):
  with patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('No valuation on a read')):
   with TestClient(create_app(self.bundle)) as client:
    for t in ('AAPL','META','GOOGL'):
     r=client.get('/api/v1/discount-inputs/'+t);self.assertEqual(r.status_code,200,r.text)
     p=generate(ROOT,ticker=t);self.assertEqual(r.json(),discount_inputs(p,t));self.assertEqual(r.headers['cache-control'],'no-store')
     self.assertEqual(client.get('/api/v1/preloads/'+t.lower()).json()['economic'],p['economic'])
     history=client.get('/api/v1/cashflows/'+t).json();self.assertFalse(history['review_passed']);self.assertTrue(all(x['fcfe']['parent_common_amount_usd'] is None for x in history['periods']))
    self.assertEqual(client.get('/api/v1/discount-inputs/GOOG').status_code,404)
    self.assertEqual(client.get('/api/v1/discount-inputs/MSFT').status_code,404)
    self.assertEqual(client.get('/api/v1/discount-inputs/AAPL?date=2026-11-04').status_code,422)
if __name__=='__main__':unittest.main()
