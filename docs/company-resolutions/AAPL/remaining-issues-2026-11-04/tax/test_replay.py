"""Financial invariants for the approved Apple tax/NWC workpaper."""
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('apple_tax_workpaper', HERE / 'replay.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class TaxWorkpaperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = module.build()

    def test_source_bound_workpaper_replays_without_mutation(self):
        self.assertEqual(self.result, json.loads((HERE / 'results.json').read_text()))
        self.assertFalse(self.result['historical_runtime_changed'])
        self.assertFalse(self.result['forward_policy_changed'])
        self.assertEqual(self.result['tax_policy_treatment_status'], 'IMPLEMENTED_USER_APPROVED_CONVENTION')
        self.assertEqual(self.result['company_status'], 'OPEN')

    def test_accounting_provision_and_cash_taxes_stay_distinct(self):
        for p in self.result['historical_periods']:
            f = p['tax_facts']
            self.assertEqual(Fraction(p['current_provision_usd']) + Fraction(p['deferred_provision_usd']), Fraction(f['provision']['value']))
            self.assertIsNone(p['operating_cash_tax_allocation_usd'])
            self.assertEqual(p['additional_cash_tax_fcff_adjustment_usd'], '0')
            self.assertEqual(p['cash_taxes_restatement_usd'], '0')
            for point in f.values():
                self.assertEqual(point['target_identity']['annual_end'], p['identity']['annual_end'])
                self.assertTrue(point['sources'])

    def test_unknown_tax_never_becomes_zero_and_diagnostic_not_adopted(self):
        p = self.result['historical_periods']
        self.assertIsNone(p[0]['nwc']['opening_current_tax_fact'])
        self.assertIsNone(p[0]['nwc']['closing_current_tax_fact'])
        self.assertIsNone(p[1]['nwc']['tax_excluded_fcff_diagnostic_usd'])
        self.assertEqual(p[3]['nwc']['current_tax_balance_change_usd'], '17782000000')
        self.assertEqual(p[4]['nwc']['current_tax_balance_change_usd'], '-13585000000')
        self.assertTrue(all(not row['nwc']['diagnostic_adopted'] for row in p))
        self.assertIsNone(module.diagnostic_tax_exclusion({}, None, '123'))

    def test_all_scenario_bridges_and_preserved_policy(self):
        for b in self.result['forecast_bridges']:
            self.assertEqual(b['annual_forecast_tax_rates'], ['0.18', '0.185', '0.19', '0.195', '0.20'])
            self.assertEqual(b['terminal_tax_rate'], '0.20')
            self.assertEqual(b['anchor_identity']['annual_end'], '2025-09-27')
            bridge = b['algebraic_component_bridge']
            self.assertLess(abs(Fraction(bridge['serialization_residual_usd'])), Fraction('1e-30'))
            self.assertFalse(bridge['serialization_residual_is_cash_adjustment'])
        self.assertFalse(self.result['cross_basis_cagr_enabled'])
        self.assertFalse(self.result['forward_policy']['automatic_history_calibration'])
        self.assertEqual(self.result['forecast_bridges'][0]['first_year_implied_incremental_sales_coefficient']['amount_usd'], '0.05')
        self.assertNotEqual(self.result['forecast_bridges'][1]['first_year_implied_incremental_sales_coefficient']['amount_usd'], '0.05')

    def test_bridge_rejects_a_cash_plug(self):
        historical = {'ebit': Fraction(100), 'tax': Fraction(20), 'd_and_a': Fraction(10), 'investment': Fraction(15), 'working_capital_cash_requirement': Fraction(5)}
        forecast = {key: str(value) for key, value in historical.items()}; forecast['fcff'] = '71'
        with self.assertRaises(ValueError):
            module.reconcile_bridge(historical, forecast)


if __name__ == '__main__':
    unittest.main()
