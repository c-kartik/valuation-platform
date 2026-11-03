"""Financial/provenance controls for the partial SBC basis bridge."""
import base64,gzip,hashlib,json,subprocess,unittest
from fractions import Fraction
from pathlib import Path
R=Path(__file__).resolve().parent;ROOT=R.parents[3]
def j(p):return json.loads(p.read_text())
def f(x):
 p=x['exact_fraction_usd'];return Fraction(int(p['numerator']),int(p['denominator']))
class BasisBridge(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s=j(R/'schedules.json');cls.rows=cls.s['periods']
 def test_complete_scope(self):
  self.assertEqual(len(self.rows),15)
  self.assertEqual({(p['ticker'],p['fiscal_year']) for p in self.rows},{(t,y) for t in ['AAPL','META','GOOGL'] for y in range(2021,2026)})
 def test_exact_once_only_sbc_reversal(self):
  for p in self.rows:
   self.assertEqual(f(p['sbc_addback_reversal']),-f(p['reported_sbc_addback']))
   self.assertEqual(f(p['cfo_after_reversing_reported_sbc_addback']),f(p['reported_cfo'])-f(p['reported_sbc_addback']))
   self.assertEqual(p['tax_adjustment_applied_usd'],'0');self.assertEqual(p['additional_sbc_or_dilution_charge_applied_usd'],'0')
 def test_cash_statement_source_populations(self):
  for p in self.rows:
   for key,concept in [('reported_cfo_source','NetCashProvidedByUsedInOperatingActivities'),('reported_sbc_addback_source','ShareBasedCompensation')]:
    point=p[key];cell=point['statement_cell'];self.assertEqual(point['concept'],concept);self.assertEqual(point['target_annual_start'],p['identity']['annual_start']);self.assertEqual(point['target_annual_end'],p['identity']['annual_end']);self.assertEqual(cell['primary_attributes']['name'].split(':')[-1],concept)
    self.assertIn(cell['context_id'],{o['context_id'] for o in point['occurrences']});self.assertTrue(cell['primary_xml_id']);self.assertTrue(cell['caption'])
 def test_all_original_source_bodies(self):
  cache={};seen=set()
  for ref in self.s['source_manifest']:
   path,pointer=ref['source_reference'].split('#')
   if path not in cache:cache[path]=j(ROOT/path)
   entry=cache[path]['artifacts'][int(pointer.split('/')[-1])];encoded=entry['response_body_gzip_base64'];encoded=''.join(encoded) if isinstance(encoded,list) else encoded
   body=gzip.decompress(base64.b64decode(encoded));self.assertEqual(hashlib.sha256(body).hexdigest(),ref['sha256']);self.assertEqual(len(body),ref['byte_length']);seen.add((ref['url'],ref['sha256']))
  self.assertEqual(len(seen),30)
 def test_alphabet_expense_difference_is_not_a_plug(self):
  p=next(p for p in self.rows if p['ticker']=='GOOGL' and p['fiscal_year']==2025)
  self.assertEqual(f(p['reported_sbc_addback']),24953000000);self.assertEqual(Fraction(p['reported_total_sbc_expense_source']['value']),27100000000)
  self.assertEqual(f(p['reported_expense_minus_addback_arithmetic_comparison_usd']),2147000000)
  self.assertTrue(p['expense_comparison_is_not_a_new_adjustment']);self.assertEqual(f(p['sbc_addback_reversal']),-24953000000)
 def test_no_false_alignment_or_historical_replacement(self):
  self.assertFalse(self.s['historical_values_modified']);self.assertFalse(self.s['forecasts_modified']);self.assertEqual(self.s['parent_status'],'OPEN')
  for p in self.rows:
   self.assertFalse(p['reported_historical_values_replaced']);self.assertEqual(p['historical_change_usd'],'0')
   for key in ('valuation_aligned_cfo_usd','valuation_aligned_fcff_usd','valuation_aligned_fcfe_usd'):self.assertIsNone(p[key])
   self.assertTrue(p['remaining_gaps']);self.assertTrue(p['basis_guardrails']['no_cagr_join_to_forecast']);self.assertTrue(p['basis_guardrails']['not_actual_cash_paid'])
 def test_reviewed_tax_policy_numerical_parity(self):
  self.assertEqual(len(self.s['tax_policy_comparison']),2)
  for p in self.s['tax_policy_comparison']:
   self.assertEqual(p['configuration_before'],p['configuration_after']);self.assertEqual(p['annual_tax_before'],p['annual_tax_after']);self.assertEqual(p['terminal_tax_before'],p['terminal_tax_after']);self.assertFalse(p['numeric_inputs_changed']);self.assertFalse(p['source_fact']);self.assertEqual(p['annual_parameter_differences'],['0']*5)
   self.assertEqual(hashlib.sha256((ROOT/p['current_policy_path']).read_bytes()).hexdigest(),p['current_policy_sha256'])
 def test_deterministic_replay(self):
  before=(R/'schedules.json').read_bytes();subprocess.run([str(ROOT/'.venv/bin/python'),str(R/'build_basis_bridge.py')],check=True,capture_output=True);self.assertEqual(before,(R/'schedules.json').read_bytes())
if __name__=='__main__':unittest.main(verbosity=2)
