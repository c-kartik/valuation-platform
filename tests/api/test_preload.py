"""Calculation-free pinned profile transport and actual engine/CLI equivalence."""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.api.test_cases import BundleFixture,ROOT
from valuation_platform.api.app import create_app
from valuation_platform.preload.generate import generate,engine_request
from valuation_platform.preload.profile import validate_profile

class PreloadApiTests(BundleFixture,unittest.TestCase):
 def test_profile_read_is_bounded_calculation_free_and_no_arbitrary_resource_route(self):
  with patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('no calculation')),TestClient(create_app(self.bundle)) as client:
   r=client.get('/api/v1/preloads/googl');self.assertEqual(r.status_code,200,r.text);self.assertLess(len(r.content),192*1024)
   p=validate_profile(r.json());self.assertEqual(p['economic_hash'],generate(ROOT)['economic_hash'])
   self.assertEqual(client.get('/api/v1/preloads/googl').content,r.content)
   self.assertEqual(client.get('/api/v1/preloads/msft').status_code,404)
   self.assertEqual(client.get('/api/v1/preloads/googl?path=AGENTS.md').status_code,422)
   self.assertEqual(r.headers['cache-control'],'no-store')
 def test_each_registered_profile_matches_its_own_catalog_anchor_and_has_no_calculation(self):
  with patch('valuation_platform.api.process.Calculator.run',side_effect=AssertionError('no calculation')),TestClient(create_app(self.bundle)) as client:
   catalog=client.get('/api/v1/catalog').json()
   for entry in catalog['entries']:
    response=client.get(entry['preload_route']);self.assertEqual(response.status_code,200)
    self.assertLess(len(response.content),192*1024)
    p=validate_profile(response.json());self.assertEqual(p['economic']['anchor'],entry['identity'])
    self.assertEqual(p['economic']['anchor_revenue'],entry['revenue'])
    self.assertEqual(p['economic']['issuer']['ticker'],entry['company'])
    self.assertEqual(p['economic_hash'],generate(ROOT,ticker=entry['company'])['economic_hash'])
    self.assertEqual(client.get(entry['preload_route']).content,response.content)
   for route in ('/api/v1/preloads/msft','/api/v1/preloads/../../AGENTS.md'):
    self.assertEqual(client.get(route).status_code,404)
 def test_generated_base_bear_bull_complete_api_cli_json_agreement(self):
  with TestClient(create_app(self.bundle)) as client,tempfile.TemporaryDirectory() as directory:
   for ticker in ('GOOGL','META','AAPL'):
    profile=generate(ROOT,ticker=ticker)
    for label in ('Base','Bear','Bull'):
     doc=engine_request(profile,label);source=Path(directory)/'case.json';source.write_text(json.dumps(doc))
     valid=client.post('/api/v1/cases/validate',json=doc);self.assertEqual(valid.status_code,200,valid.text);self.assertFalse(valid.json()['calculation_performed'])
     r=client.post('/api/v1/cases/run',json=doc);self.assertEqual(r.status_code,200,r.text)
     cli=subprocess.check_output([sys.executable,str(ROOT/'scripts/run_analyst_case.py'),str(source),'--run'],cwd=ROOT)
     self.assertEqual(json.loads(cli),r.json())
