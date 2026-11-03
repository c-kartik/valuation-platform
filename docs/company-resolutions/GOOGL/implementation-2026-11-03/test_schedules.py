import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('googl_resolution_schedules',Path(__file__).with_name('build_schedules.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class AlphabetScheduleChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.data=module.build();cls.rows=cls.data['periods']
    def test_exact_consolidated_fcfe(self):
        self.assertEqual([r['consolidated_fcfe_before_nci_allocation']['amount_usd'] for r in self.rows],['65776000000','58814000000','68735000000','73652000000','105403000000'])
    def test_missing_owner_cash_never_becomes_zero(self):
        for r in self.rows:
            self.assertIsNone(r['parent_common_fcfe']['amount_usd']);self.assertIsNone(r['ownership_schedule']['nci_cash_allocation_usd'])
            self.assertFalse(r['consolidated_fcfe_before_nci_allocation']['publishable_as_parent_common'])
    def test_book_nci_never_substituted_for_fair_value(self):
        for r in self.rows:
            self.assertGreater(int(r['ownership_schedule']['book_nci_usd_rounded']),0)
            self.assertIsNone(r['ownership_schedule']['nci_fair_value_usd']);self.assertFalse(r['ownership_schedule']['book_nci_used_as_fair_value'])
    def test_rnci_contained_not_added(self):
        for r in self.rows:self.assertLess(int(r['ownership_schedule']['book_rnci_usd_rounded_included_in_nci']),int(r['ownership_schedule']['book_nci_usd_rounded']))
    def test_prepaid_cash_not_non_cash_assets(self):
        r=self.rows[-1]['lease_schedule']
        self.assertEqual(r['financing_cash']['amount_usd'],'1988000000');self.assertEqual(r['noncash_assets_obtained']['amount_usd'],'1606000000')
        self.assertEqual(r['prepayments']['amount_usd_rounded'],'1100000000');self.assertIsNone(r['commenced_lease_principal_usd'])
    def test_no_second_lease_deduction_or_noncash_capex(self):
        for r in self.rows:
            self.assertEqual(r['lease_schedule']['additional_cash_deduction_usd'],'0');self.assertEqual(r['lease_schedule']['noncash_assets_added_to_cash_capex_usd'],'0')
    def test_absent_2021_separate_lease_cash_not_zero(self):
        self.assertIsNone(self.rows[0]['lease_schedule']['financing_cash']);self.assertIsNone(self.rows[0]['lease_schedule']['noncash_assets_obtained'])
    def test_no_false_closure_or_numeric_change(self):
        self.assertEqual(self.data['company_status'],'OPEN');self.assertEqual(set(self.data['open_roadblocks']),{'G1','G2','G3'})
        self.assertTrue(all(r['numerical_change_from_prior_consolidated_result_usd']=='0' for r in self.rows))

if __name__=='__main__':unittest.main()
