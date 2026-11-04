import copy
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path
import unittest
from valuation_platform.preload.generate import generate
from valuation_platform.preload.profile import digest
from valuation_platform.review.discount_inputs import discount_inputs
ROOT=Path(__file__).resolve().parents[2]

class SavedDiscountTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.profiles={t:generate(ROOT,ticker=t) for t in ('AAPL','META','GOOGL')}
 def test_independent_capm_wacc_and_retained_sources(self):
  for t,p in self.profiles.items():
   before=copy.deepcopy(p);d=discount_inputs(p,t);o=d['operands'];v={k:F(s) for k,s in o.items()}
   ke=v['risk_free']+v['beta']*v['erp'];w=ke*v['equity_weight']+(v['risk_free']+v['spread'])*(1-v['tax_shield'])*v['debt_weight']
   self.assertEqual(F(d['cost_of_equity']),ke);self.assertEqual(F(d['base_wacc']),w)
   self.assertEqual(F(d['cost_of_equity_percent']),100*ke)
   self.assertFalse(d['automatic_adoption']);self.assertFalse(d['scenario_wacc_offset_applied_to_cost_of_equity'])
   self.assertEqual({s['id'] for s in d['sources']},{a['source'] for a in d['observed_macro_inputs']})
   self.assertEqual({a['end'] for a in d['observed_macro_inputs']},{'2026-10-28','2026-10-01'})
   self.assertEqual(p,before)
 def test_context_isolation(self):
  p=self.profiles['AAPL'];ref=discount_inputs(p,'AAPL')
  with localcontext() as c:c.prec=6;self.assertEqual(discount_inputs(p,'AAPL'),ref)
 def test_stale_or_missing_never_supplies_cost_equity(self):
  for status in ('STALE','MISSING_EVIDENCE','INCOMPATIBLE_DEFINITION'):
   p=copy.deepcopy(self.profiles['AAPL']);f=p['economic']['fields']['wacc'];f['status']=status
   if status!='STALE':
    f['value']=None;p['economic']['scenarios']['Base']['wacc']=None
   p['economic_hash']=digest(p['economic']);d=discount_inputs(p,'AAPL');self.assertEqual(d['status'],'UNAVAILABLE');self.assertIsNone(d['cost_of_equity']);self.assertIsNone(d['cost_of_equity_percent'])
 def test_inconsistent_operands_source_or_hash_rejected(self):
  for change in ('profile_hash','beta','macro_source','macro_amount','wacc','rule'):
   p=copy.deepcopy(self.profiles['AAPL']);e=p['economic'];f=e['fields']['wacc']
   if change=='beta':f['operands']['beta']='1.2'
   if change=='macro_source':next(o for o in e['observations'] if o['key']=='treasury_10y')['source_sha256']='0'*64
   if change=='macro_amount':next(o for o in e['observations'] if o['key']=='treasury_10y')['value']='0.03'
   if change=='wacc':f['value']='0.2';e['scenarios']['Base']['wacc']='0.2'
   if change=='rule':f['rule']='unreviewed-rule'
   if change!='profile_hash':p['economic_hash']=digest(e)
   else:p['economic_hash']='0'*64
   with self.subTest(change=change),self.assertRaises(ValueError):discount_inputs(p,'AAPL')
 def test_cross_issuer_rejected(self):
  with self.assertRaises(ValueError):discount_inputs(self.profiles['META'],'AAPL')
if __name__=='__main__':unittest.main()
