"""Read-only public catalog projection, with original resources kept private."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from valuation_platform.api.app import create_app
from valuation_platform.api.bundle import build_bundle, remove_bundle
from valuation_platform.api.catalog import CATALOG_MAX_BYTES, build_catalog
from valuation_platform.valuation import case_inputs as c

ROOT = Path(__file__).resolve().parents[2]


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.bundle = Path(cls.temp.name) / 'private'
        build_bundle(ROOT, cls.bundle)

    @classmethod
    def tearDownClass(cls):
        remove_bundle(cls.bundle)
        cls.temp.cleanup()

    def test_identity_templates_precision_and_narrow_projection(self):
        with patch.object(c, 'run_case', side_effect=AssertionError('calculation')):
            with TestClient(create_app(self.bundle)) as client:
                with patch('valuation_platform.api.app.build_catalog', side_effect=AssertionError('per-request rebuild')):
                    response = client.get('/api/v1/catalog')
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(client.get('/api/v1/catalog').content, response.content)
                self.assertEqual(response.headers['cache-control'], 'no-store')
                self.assertLess(len(response.content), CATALOG_MAX_BYTES)
                d = response.json()
                self.assertEqual(d['schema_version'], 'local-ev-catalog-v1')
                self.assertEqual([e['company'] for e in d['entries']], ['META', 'GOOGL', 'AAPL'])
                for entry in d['entries']:
                    kind = entry['kind']
                    original = json.loads((ROOT / f'examples/valuation/{kind}-unset.json').read_text())
                    self.assertEqual(entry['template'], original)
                    self.assertEqual(entry['identity'], original['anchor'])
                    self.assertEqual(entry['precision'], '-6')
                    self.assertEqual(entry['unit'], 'USD')
                    self.assertTrue(all(url.startswith('https://www.sec.gov/Archives/') for url in entry['source_links']))
                    values = [y[k] for y in original['forecast_years'] for k in c.ANNUAL_RATES]
                    values += [original['wacc'], original['terminal_growth'], *original['terminal'].values()]
                    self.assertEqual(values, [None] * 37)
                    self.assertIsNone(original['analyst']['author'])
                self.assertEqual(d['synthetic_demo'], json.loads((ROOT/'examples/valuation/synthetic-base.json').read_text()))
                for private in ('source_details_json', 'approval_details_json', 'runtime-manifest', '/Users/', 'review_revision', 'source_revision', 'current_history', 'sha256'):
                    self.assertNotIn(private, response.text)
                self.assertNotIn('access-control-allow-origin', response.headers)
                self.assertEqual(client.get('/api/v1/catalog?path=AGENTS.md').status_code, 422)
                self.assertEqual(client.get('/api/v1/catalog/meta-fy2025').status_code, 404)
                self.assertEqual(client.get('/examples/valuation/meta-fy2025-unset.json').status_code, 404)

    def test_catalog_budget_is_enforced_before_response(self):
        with patch('valuation_platform.api.catalog.CATALOG_MAX_BYTES', 256):
            with self.assertRaises(ValueError):
                build_catalog(self.bundle)


if __name__ == '__main__':
    unittest.main()
