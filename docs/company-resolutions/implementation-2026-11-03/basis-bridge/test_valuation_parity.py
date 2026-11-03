"""Controls on the separately executed committed/current policy EV comparison."""
import hashlib,json,unittest
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
from pathlib import Path
R=Path(__file__).resolve().parent
class ValuationParity(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=json.loads((R/'valuation-parity.json').read_text())
 def test_executed_scope(self):
  self.assertEqual(self.r['scenario_pairs'],6);self.assertEqual(self.r['independent_engine_executions'],12)
  self.assertEqual({c['ticker'] for c in self.r['companies']},{'AAPL','META'})
  for c in self.r['companies']:self.assertEqual({s['scenario'] for s in c['scenarios']},{'Base','Bear','Bull'})
 def test_all_requests_and_results_identical(self):
  for c in self.r['companies']:
   self.assertEqual(c['baseline_policy_sha256'],c['current_policy_sha256']);self.assertEqual(c['before_economic_hash'],c['after_economic_hash'])
   for s in c['scenarios']:
    self.assertEqual(s['before_request'],s['after_request']);self.assertEqual(s['before_result'],s['after_result']);self.assertEqual(Decimal(s['enterprise_value_difference_usd']),0);self.assertEqual(Decimal(s['before_enterprise_value_usd']),Decimal(s['after_enterprise_value_usd']))
 def test_independent_ev_subtotal_identities(self):
  with localcontext() as c:
   c.prec=50;c.rounding=ROUND_HALF_EVEN
   for company in self.r['companies']:
    for s in company['scenarios']:
     for key in ('before_result','after_result'):
      b=s[key]['stage_b'];explicit=sum((Decimal(y['pv_fcff']) for y in b['years']),Decimal(0))
      self.assertEqual(explicit,Decimal(b['pv_explicit_fcff']));self.assertEqual(Decimal(b['enterprise_value']),Decimal(b['pv_explicit_fcff'])+Decimal(b['pv_terminal_value']))
 def test_reviewed_tax_paths_and_scope_limit(self):
  expected={'AAPL':['0.18','0.185','0.19','0.195','0.20'],'META':['0.16','0.17','0.18','0.19','0.20']}
  for c in self.r['companies']:
   for s in c['scenarios']:
    self.assertEqual([Decimal(x) for x in s['annual_tax_before']],[Decimal(x) for x in expected[c['ticker']]])
    self.assertEqual(s['annual_tax_before'],s['annual_tax_after']);self.assertEqual(Decimal(s['terminal_tax_before']),Decimal('.20'));self.assertEqual(s['method'],'FCFF_PERPETUAL_GROWTH_WACC')
  self.assertFalse(self.r['accepted_inputs_or_runtime_modified']);self.assertTrue(any('S2' in s and 'OPEN' in s for s in self.r['limitations']))
if __name__=='__main__':unittest.main(verbosity=2)
