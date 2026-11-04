import copy
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('apple_da_replay', HERE / 'replay.py')
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)


class DaPopulationReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = work.build()

    def test_fy2024_same_context_and_original_comparative_equality(self):
        point = self.data['later_comparative_points'][0]
        self.assertEqual(point['target_identity']['annual_start'], '2023-10-01')
        self.assertEqual(point['target_identity']['annual_end'], '2024-09-28')
        for fact in point['points'].values():
            self.assertEqual(fact['source_identity']['accession'], '0000320193-26-000026')
            self.assertEqual(fact['target_identity']['annual_end'], '2024-09-28')
            self.assertEqual(fact['evidence_depth'], 'exact_primary_inline_and_instance_verified')
        self.assertEqual(point['points']['combined_da']['value'], '11445000000')
        self.assertEqual(self.data['validation']['original_and_later_da_compares_equal'], 2)

    def test_rounding_cannot_explain_2024_but_can_2025(self):
        rows = {r['fiscal_year']: r for r in self.data['later_comparative_points']}
        rounding = rows[2024]['rounding']
        self.assertEqual(rounding['nominal_difference_usd'], '355000000')
        self.assertEqual(rounding['difference_lower_usd'], '254500000')
        self.assertEqual(rounding['difference_upper_usd'], '455500000')
        self.assertFalse(rounding['rounding_can_explain_difference'])
        self.assertTrue(rows[2025]['rounding']['rounding_can_explain_difference'])
        self.assertEqual(rows[2026]['comparison_role'], 'later-year population diagnostic only; not added to scope')

    def test_no_unsourced_or_unmatched_extra_addback(self):
        self.assertEqual(work.guarded_addback('11445000000', '0'), 11445000000)
        for source_ok, investment_ok in [(False, False), (True, False), (False, True)]:
            with self.assertRaises(ValueError):
                work.guarded_addback('11445000000', '355000000', source_ok, investment_ok)
        self.assertTrue(all(p['additional_da_plug_usd'] == '0' for p in self.data['annual_adopted_inputs']))
        self.assertFalse(self.data['diagnostic_only']['adopted'])
        self.assertEqual(self.data['diagnostic_only']['increment_applied_to_runtime_usd'], '0')

    def test_source_tamper_fails_closed(self):
        import json
        path = work.ROOT / 'docs/company-resolutions/AAPL/implementation-2026-11-03/new-source-row.json'
        row = json.loads(path.read_text())
        row['sources'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            work.RetainedFiling(work.ROOT, row, {})

    def test_policy_closed_is_not_exact_reconciliation_closed(self):
        self.assertEqual(self.data['policy_treatment_status'], 'IMPLEMENTED_RETAIN_REPORTED_COMBINED_DA')
        self.assertEqual(self.data['exact_expense_population_reconciliation_status'], 'UNRESOLVED_NO_SOURCE_BOUND_BRIDGE')
        self.assertEqual(self.data['company_status'], 'OPEN')
        self.assertEqual([p['fiscal_year'] for p in self.data['annual_adopted_inputs']], list(range(2021, 2026)))


if __name__ == '__main__':
    unittest.main()
