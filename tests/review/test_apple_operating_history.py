from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from valuation_platform.review import apple_operating_history as apple
from valuation_platform.review.pilot_cashflows import read_cashflows, RESOURCE as OLD
from valuation_platform.api.catalog import build_catalog

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import build_apple_operating_history as builder


class AppleOperatingTests(unittest.TestCase):
    def test_source_replay_and_all_five_api_chart_values_agree(self):
        rebuilt=builder.build()
        self.assertEqual(rebuilt['adopted-history.json'],apple.read_overlay(ROOT))
        self.assertEqual(rebuilt['source-ledger.json'],json.loads((ROOT/builder.OUT/'source-ledger.json').read_text()))
        expected=['93.41','108.44','99.84','115.68','95.12']
        current=read_cashflows(ROOT,'AAPL');overlay=apple.read_overlay(ROOT)
        catalog=json.loads(build_catalog(ROOT));entry=next(e for e in catalog['entries'] if e['company']=='AAPL')
        for i,(p,h,want) in enumerate(zip(current['periods'],entry['historical_window'],expected,strict=True)):
            self.assertEqual(p['fcff']['amount_usd'],h['fcff'])
            self.assertEqual(overlay['periods'][i]['fcff']['display_billions'],want)
            self.assertEqual(p['fcff']['basis'],apple.BASIS)
            self.assertIsNone(p['fcfe']['parent_common_amount_usd'])
            self.assertFalse(p['fcff']['exact_unlevered_cash_flow_claim'])
        self.assertEqual(current['readiness']['counts']['missing_required_input'],0)
        self.assertIn('current tax accruals',entry['historical_fcff_policy']['notice'])

    def test_no_interest_input_no_debt_double_count_and_missing_not_zero(self):
        p=apple.read_overlay(ROOT)['periods'][-1]
        self.assertNotIn('interest_expense',p['inputs'])
        v=p['inputs'];self.assertEqual(apple.calculate(v),p['fcff'])
        missing=dict(v);missing.pop('da')
        with self.assertRaises(ValueError):apple.calculate(missing)
        missing=dict(v,da=None)
        with self.assertRaises(ValueError):apple.calculate(missing)
        self.assertEqual(p['inputs']['closing_nwc'],'-49925000000')
        self.assertEqual(p['inputs']['opening_nwc'],'-66065000000')

    def test_current_tax_changes_not_silently_removed_or_double_counted(self):
        overlay=apple.read_overlay(ROOT)
        self.assertEqual([str(F(p['inputs']['closing_nwc'])-F(p['inputs']['opening_nwc'])) for p in overlay['periods']],
                         ['1250000000','-7965000000','-1807000000','-20150000000','16140000000'])
        ledger=json.loads((ROOT/builder.OUT/'source-ledger.json').read_text())
        self.assertIsNone(ledger['periods'][0]['separately_disclosed_current_tax_diagnostic'])
        self.assertFalse(ledger['periods'][0]['tax_diagnostic_missing_means_zero'])

    def test_legacy_series_and_other_issuers_unchanged(self):
        original=json.loads((ROOT/OLD).read_text())
        for ticker in ('AAPL','META','GOOGL'):
            current=read_cashflows(ROOT,ticker)
            for p,old in zip(current['periods'],original['companies'][ticker]['periods'],strict=True):
                self.assertEqual(p['fcfe'],old['fcfe'])
                self.assertEqual(p['legacy_cfo_fcff'] if ticker=='AAPL' else p['fcff'],old['fcff'])
        self.assertEqual([p['legacy_cfo_fcff']['amount_usd'] is None for p in read_cashflows(ROOT,'AAPL')['periods']], [False,False,False,True,True])

    def test_pin_and_recomputed_arithmetic_fail_closed(self):
        original=(ROOT/apple.RESOURCE).read_bytes()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/apple.RESOURCE;p.parent.mkdir(parents=True);p.write_bytes(original+b' ')
            with self.assertRaisesRegex(ValueError,'adopted pin'):apple.read_overlay(root)
            data=json.loads(original);data['periods'][4]['fcff']['amount_usd']='1'
            body=json.dumps(data).encode();p.write_bytes(body)
            with patch.object(apple,'PIN',hashlib.sha256(body).hexdigest()):
                with self.assertRaisesRegex(ValueError,'does not reproduce'):apple.read_overlay(root)


if __name__=='__main__':unittest.main()
