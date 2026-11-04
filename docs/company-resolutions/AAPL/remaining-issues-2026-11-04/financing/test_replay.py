import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('apple_financing_stage', Path(__file__).with_name('replay.py'))
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
from resolve_apple_cashflows import classified_cash


class FinancingReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = replay.build()

    def test_source_bound_exact_results(self):
        expected = ['105618000000', '111320000000', '89683000000', '102809000000', '90284000000']
        self.assertEqual([p['identified_funding_fcfe']['amount_usd'] for p in self.data['periods']], expected)
        self.assertEqual(self.data['validation']['primary_instance_source_pairs'], 5)
        self.assertEqual(self.data['validation']['exact_full_fcfe_newly_cleared'], 0)

    def test_unknowns_never_zero_or_verified(self):
        for p in self.data['periods']:
            self.assertIsNone(p['full_fcfe_usd'])
            self.assertIsNone(p['actual_finance_lease_principal_usd'])
            self.assertIsNone(p['unknown_other_debt_component_usd'])
            self.assertFalse(p['classification_assumes_other_zero'])
            self.assertFalse(p['lease_principal_subtracted_again'])

    def test_duplicate_and_missing_rows_fail_closed(self):
        rows = self.data['periods'][0]['source_rows']
        with self.assertRaises(ValueError):
            classified_cash(rows + [rows[0]])
        with self.assertRaises(ValueError):
            classified_cash(rows[1:])

    def test_request_not_sent_and_reclassification_exact(self):
        self.assertFalse(self.data['issuer_request_sent'])
        self.assertEqual(self.data['fy2021_presentation_bridge']['difference_usd'], '0')
        self.assertEqual(self.data['fy2021_presentation_bridge']['fcfe_change_usd'], '0')


if __name__ == '__main__':
    unittest.main()
