import importlib
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/comparables'))
exporter = importlib.import_module('export_browser')

class BrowserExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = exporter.build()

    def test_growth_is_same_filing_same_quarter(self):
        for key, value in self.package['growth'].items():
            with self.subTest(key=key):
                self.assertAlmostEqual(value['growth'], value['current']/value['prior']-1)
                if key == 'GOOGL_advertising': continue
                self.assertEqual([o['start'] for o in value['operands']], ['2025-07-01','2026-07-01'])
                self.assertEqual(len({o['source_url'] for o in value['operands']}),1)

    def test_google_ads_aggregates_revenue_not_growth_rates(self):
        parts = [self.package['growth']['GOOGL_'+k] for k in ['search','youtube_ads','network']]
        total = self.package['growth']['GOOGL_advertising']
        self.assertEqual(total['current'],sum(v['current'] for v in parts))
        self.assertEqual(total['prior'],sum(v['prior'] for v in parts))

    def test_public_projection_has_no_private_paths_or_market_defaults(self):
        text=json.dumps(self.package)
        self.assertNotIn('/Users/',text)
        self.assertTrue(all(v is None for v in self.package['market'].values()))
        self.assertEqual(len(self.package['peers']),7)
        self.assertEqual(self.package['validation']['business_reconciliations'],32)

    def test_current_public_snapshot_reproduces(self):
        path=exporter.ROOT/'frontend/public/features/trading-comparables/GOOGL.json'
        self.assertEqual(json.loads(path.read_text()), self.package)

if __name__ == '__main__':
    unittest.main()
