import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).with_name('replay.py');spec=importlib.util.spec_from_file_location('apple_equity_stage',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class EquitySourceReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=m.build()
 def test_matching_anchor_population_and_issued_control(self):
  d=self.d;self.assertEqual(d['anchor_support']['dated_common_shares'],'14773260000');self.assertEqual(d['sources']['dated_common_shares']['value'],d['sources']['common_shares_issued_control']['value']);self.assertFalse(d['adopted_population_choices']['weighted_average_eps_shares_used'])
 def test_nonoverlapping_parent_sums_and_market_debt_alternative(self):
  a=self.d['anchor_support'];self.assertEqual(a['cash_and_securities_usd'],'132420000000');self.assertEqual(a['named_debt_carrying_usd'],'98657000000');self.assertEqual(a['finance_lease_liability_usd'],'1230000000');self.assertEqual(a['term_debt_fair_value_usd'],'80400000000');self.assertFalse(self.d['debt_comparison']['alternative_values_added_together'])
 def test_missing_claims_and_awards_are_not_zero_or_price(self):
  self.assertTrue(all(v is None for v in self.d['unresolved_operands'].values()));self.assertIsNone(self.d['anchor_support']['fair_value_per_share_usd']);self.assertTrue(self.d['no_automatic_rsu_addition'])
 def test_wrong_date_and_eps_concept_cannot_supply_denominator(self):
  p=dict(self.d['sources']['dated_common_shares']);p['scope']=dict(p['scope'],end='2025-10-17')
  with self.assertRaises(ValueError):m.one([p],'CommonStockSharesOutstanding',unit='shares')
  p['scope']['end']='2025-09-27';p['concept']='WeightedAverageNumberOfDilutedSharesOutstanding'
  with self.assertRaises(ValueError):m.one([p],'CommonStockSharesOutstanding',unit='shares')
if __name__=='__main__':unittest.main()
