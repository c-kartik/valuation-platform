"""Financial/provenance controls for the Meta M1–M3 decision workpaper."""
import gzip,hashlib,json,unittest
from fractions import Fraction
from pathlib import Path
R=Path(__file__).resolve().parent
ROOT=R.parents[3]
def read(name):return json.loads((R/name).read_text())
class MetaReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=read('review-results.json');cls.points=read('numeric-source-points.json');cls.sources=read('all-primary-source-manifest.json')['sources'];cls.old=json.loads((R.parent/'results.json').read_text())
 def test_exact_source_bodies(self):
  method=read('method-source.json');self.assertEqual(hashlib.sha256((R/method['file']).read_bytes()).hexdigest(),method['sha256'])
  self.assertEqual(len(self.sources),21)
  for s in self.sources:
   b=(ROOT/s['path']).read_bytes()
   if s.get('encoding')=='gzip' or s.get('storage_encoding')=='gzip':b=gzip.decompress(b)
   self.assertEqual(hashlib.sha256(b).hexdigest(),s['sha256'])
 def test_full_quarter_population(self):
  self.assertEqual(len(self.r['quarterly_financing']),15)
  self.assertEqual({x['date'] for x in self.r['quarterly_financing']},{f'{y}-{m}' for y in range(2021,2026) for m in ('03-31','06-30','09-30')})
 def test_annual_cash_flow_identity_and_unknowns(self):
  self.assertEqual([p['fiscal_year'] for p in self.r['periods']],list(range(2021,2026)))
  for p,old in zip(self.r['periods'],self.old['periods']):
   i={k:Fraction(v) for k,v in old['inputs'].items()};fcff=i['cfo']-Fraction(old['net_cash_investment']['amount_usd'])+i['interest_expense']*(1-i['tax_provision']/i['pretax_income'])
   fcfe=i['cfo']-Fraction(old['net_cash_investment']['amount_usd'])+Fraction(old['financing']['net_borrowing']['amount_usd'])
   f=p['historical_fcff_exact_fraction_usd'];self.assertEqual(Fraction(int(f['numerator']),int(f['denominator'])),fcff)
   self.assertEqual(Fraction(p['provisional_fcfe_usd']),fcfe)
   self.assertEqual(p['financing_statement_tie_difference_usd'],'0')
   self.assertIsNone(p['parent_common_fcfe_usd'])
   self.assertNotEqual(Fraction(p['unresolved_other_financing_usd']),0)
 def test_quarterly_cash_pool_reclassifications(self):
  c=self.r['comparative_presentations'];self.assertEqual(len(c),3)
  for row,expected in zip(c,[4000000,-105000000,-351000000]):
   self.assertEqual(Fraction(row['old_other_usd'])+Fraction(row['old_overdraft_usd']),expected)
   self.assertEqual(Fraction(row['later_other_usd']),expected)
   self.assertIsNone(row['annual_debt_change_justified_usd'])
 def test_interest_capitalization_not_cash_substitute(self):
  self.assertEqual([p['interest_capitalized_incurred']['amount_usd'] if p['interest_capitalized_incurred'] else None for p in self.r['periods']],[None,None,'283000000','384000000','535000000'])
  for p in self.r['periods']:
   self.assertIsNone(p['cash_interest_capitalized_usd']);self.assertIsNone(p['broader_unlevered_fcff_usd']);self.assertEqual(p['historical_change_usd'],'0')
 def test_cash_interest_population_is_not_all_interest(self):
  for p,expected in zip(self.r['periods'],[15000000,16000000,20000000,23000000,31000000]):self.assertEqual(Fraction(p['finance_lease_interest_cash_separately_reported']['amount_usd']),expected)
  self.assertEqual(Fraction(self.r['periods'][0]['cash_interest_excluding_capitalized']['amount_usd']),0)
  self.assertEqual(Fraction(self.r['periods'][1]['cash_interest_excluding_capitalized']['amount_usd']),0)
  self.assertIsNone(self.r['periods'][0]['cash_interest_capitalized_usd'])
 def test_tax_current_deferred_separate_from_cash(self):
  for p,old in zip(self.r['periods'],self.old['periods']):
   self.assertEqual(Fraction(p['current_tax_expense_note']['amount_usd'])+Fraction(p['deferred_tax_expense_note']['amount_usd']),Fraction(old['inputs']['tax_provision']))
  p=self.r['periods'][-1];self.assertEqual(Fraction(p['cash_tax']['amount_usd']),7578000000)
  self.assertNotEqual(Fraction(p['cash_tax']['amount_usd']),Fraction(p['current_tax_expense_note']['amount_usd']))
 def test_tax_event_and_partial_reversal(self):
  t=self.r['tax_review'];self.assertEqual(Fraction(t['obbba_charge']['amount_usd']),15930000000);self.assertEqual(Fraction(t['noncash_valuation_allowance_charge']['amount_usd']),14030000000)
  self.assertEqual(Fraction(t['other_obbba_charge_derived_usd']),1900000000)
  f=t['2025_etr_excluding_only_non_cash_va']['fraction'];self.assertEqual(Fraction(int(f['numerator']),int(f['denominator'])),Fraction(11444,85932))
  f=t['2026_ytd_etr_before_named_discrete_benefit_context_not_operating_tax']['fraction'];self.assertEqual(Fraction(int(f['numerator']),int(f['denominator'])),Fraction(9058,53509))
 def test_forward_policy_reaffirmed_not_filing_fact(self):
  t=self.r['tax_review']['selected_forward_policy'];self.assertEqual(t['operating_tax_annual'],{str(y):v for y,v in zip(range(2026,2031),['0.16','0.17','0.18','0.19','0.20'])});self.assertEqual(t['terminal_tax'],'0.20');self.assertFalse(t['numeric_preload_change']);self.assertEqual(t['historical_cfo_change_usd'],'0');self.assertEqual(t['ev_change_from_this_policy_review_usd'],'0')
 def test_open_parent_status(self):
  self.assertEqual(self.r['parent_status'],'OPEN');self.assertFalse(self.r['historical_values_changed']);self.assertEqual(len(self.r['open_issues']),2)
if __name__=='__main__':unittest.main(verbosity=2)
