"""Target-specific peer mappings, fiscal periods and preserved source contracts."""
import importlib
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/comparables'))
exports=importlib.import_module('export_targets')

class TargetExportsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={ticker:exports.build(ticker) for ticker in ['AAPL','META']}

    def test_target_specific_peers_not_a_copied_alphabet_basket(self):
        apple,meta=self.packages['AAPL'],self.packages['META']
        self.assertEqual(apple['peer_order'],['AAPL','DELL','HPQ','MSFT','GOOGL','AMZN','NFLX'])
        self.assertEqual(meta['peer_order'],['META','GOOGL','SNAP','PINS','RDDT','TTD','AMZN'])
        self.assertEqual(apple['peers']['AAPL']['role'],'Target company')
        self.assertEqual(meta['peers']['META']['role'],'Target company')

    def test_hardware_dates_are_not_calendar_aligned_or_fabricated(self):
        g=self.packages['AAPL']['growth']
        self.assertEqual(g['AAPL_mac']['current_end'],'2026-09-26')
        self.assertEqual(g['DELL_client_solutions']['current_end'],'2026-07-31')
        self.assertEqual(g['DELL_client_solutions']['prior_end'],'2025-08-01')
        self.assertEqual(g['HPQ_personal_systems']['current_end'],'2026-07-31')
        self.assertEqual(self.packages['AAPL']['peers']['DELL']['ttm_end'],'2026-07-31')

    def test_apple_uses_shared_revenue_package_and_reconciles(self):
        package=self.packages['AAPL'];mix=json.loads((exports.ROOT/'frontend/public/revenue-mix-expanded/AAPL.json').read_text())
        row=mix['rows'][-1]
        for key,value in row['values'].items():self.assertEqual(package['growth']['AAPL_'+key]['current'],value)
        self.assertEqual(sum(package['growth']['AAPL_'+k]['current'] for k in row['values']),row['total'])
        self.assertIn('derivation',package['growth']['AAPL_mac']['basis'])
        self.assertIsNone(package['presentation']['groups'][0]['cards'][0]['income'])

    def test_direct_comparative_growth_uses_same_filing_and_exact_arithmetic(self):
        for d in self.packages.values():
            for key,g in d['growth'].items():
                with self.subTest(target=d['target'],key=key):
                    self.assertAlmostEqual(g['growth'],g['current']/g['prior']-1)
                    if key.startswith('AAPL_') or key=='GOOGL_advertising':continue
                    self.assertEqual(len({o['source_url'] for o in g['operands']}),1)

    def test_negative_snap_earnings_and_reality_labs_losses_are_preserved(self):
        d=self.packages['META']
        self.assertLess(d['peers']['SNAP']['ttm']['ebit'],0)
        rows=d['presentation']['business_tables'][0]['rows']
        self.assertLess(rows[1][2],0)
        self.assertEqual(rows[0][1]+rows[1][1],rows[2][1])
        self.assertEqual(rows[0][2]+rows[1][2],rows[2][2])

    def test_netflix_proxy_has_its_disclosed_company_profit_not_missing(self):
        card=self.packages['AAPL']['presentation']['groups'][1]['cards'][-1]
        self.assertIn('proxy',card['scope'])
        self.assertGreater(card['income'],0)

    def test_public_packages_reproduce_without_prices_or_private_paths(self):
        for ticker,d in self.packages.items():
            with self.subTest(ticker=ticker):
                path=exports.ROOT/f'frontend/public/features/trading-comparables/{ticker}.json'
                self.assertEqual(json.loads(path.read_text()),d)
                self.assertTrue(all(v is None for v in d['market'].values()))
                self.assertNotIn('/Users/',json.dumps(d))

if __name__=='__main__':unittest.main()
