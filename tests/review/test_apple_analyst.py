"""Independent arithmetic and economic-perimeter checks for the analyst consumer."""
import copy
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import unittest

from valuation_platform.preload.generate import generate, engine_request
from valuation_platform.review.apple_analyst import DEFAULTS, READY, RESOURCE, read_apple_analyst, read_policy, run_apple_analyst
from valuation_platform.review.pilot_cashflows import read_cashflows
from valuation_platform.valuation.case_inputs import CaseInputError, read_case, run_case

ROOT = Path(__file__).resolve().parents[2]


def document(profile=None, label='Base', horizon=5):
    p = profile or generate(ROOT, ticker='AAPL', generated_at='2026-11-04T00:00:00+00:00')
    base = engine_request(p, label)
    if horizon == 10:
        base.update(schema_version='analyst-case-v4', forecast_horizon=10)
        for i in range(6, 11):
            base['forecast_years'].append(dict(base['forecast_years'][-1], period_index=i, fiscal_year_label=f'FY{2025+i}'))
    return {'schema_version': 'apple-analyst-request-v1', 'base_case': base, 'assumptions': dict(DEFAULTS)}


class AppleAnalystTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = generate(ROOT, ticker='AAPL', generated_at='2026-11-04T00:00:00+00:00')
        cls.doc = document(cls.profile)
        cls.result = run_apple_analyst(cls.doc, ROOT)

    def test_five_histories_reproduce_without_changing_legacy_or_unknowns(self):
        r = self.result
        expected = ['105618000000', '111320000000', '89683000000', '102809000000', '90284000000']
        self.assertEqual([p['fcfe_usd'] for p in r['historical']], expected)
        legacy = read_cashflows(ROOT, 'AAPL')
        for new, old in zip(r['historical'], legacy['periods'], strict=True):
            self.assertEqual(new['fcff_usd'], old['fcff']['amount_usd'])
            self.assertEqual(new['fcfe_usd'], old['fcfe']['amount_usd'])
            self.assertFalse(old['fcfe']['cleared'])
            self.assertFalse(new['exact_full_fcfe_verified'])
            self.assertEqual(D(new['economic_fcfe_usd']), D(new['fcfe_usd']) - D(new['sbc_usd']))
        self.assertFalse(r['exact_full_historical_fcfe_claim'])
        self.assertFalse(r['automatic_history_calibration'])
        self.assertEqual([p['status'] for p in r['readiness']], [READY] * 5)

    def test_equity_bridge_matches_independent_fractions_and_no_duplicate_claims(self):
        r = self.result; b = r['bridge']
        cash = F(35934+18763+77723) * 10**6
        reserve = F(416161) * 10**6 * F(2, 100)
        debt = F(80400+7979+1230) * 10**6
        shares = F(14773260000+151574000)
        fcff = F(r['fcff']['enterprise_value_usd']) + cash - reserve - debt
        fcfe = F(r['fcfe']['operating_equity_value_usd']) + cash - reserve
        for key, expected in [('gross_cash_usd', cash), ('operating_reserve_usd', reserve), ('eligible_cash_usd', cash-reserve), ('debt_claims_usd', debt), ('valuation_shares', shares)]:
            self.assertEqual(F(b[key]), expected)
        self.assertLess(abs(F(r['fcff']['value_per_share_usd']) - fcff/shares), F('1e-40'))
        self.assertLess(abs(F(r['fcfe']['value_per_share_usd']) - fcfe/shares), F('1e-40'))
        self.assertFalse(r['fcfe']['debt_subtracted_after_fcfe_discounting'])
        self.assertEqual(b['operating_lease_debt_deduction_usd'], '0')
        self.assertEqual(b['separate_existing_rsu_claim_deduction_usd'], '0')

    def test_fcfe_roll_forward_interest_tax_shield_and_present_value(self):
        r = self.result; ke = F(DEFAULTS['cost_of_equity']); kd = F(DEFAULTS['pre_tax_cost_of_debt'])
        debt = F(99887)*10**6; total = F(0)
        for i, (y, a) in enumerate(zip(r['fcfe']['years'], self.doc['base_case']['forecast_years'], strict=True), 1):
            self.assertEqual(F(y['opening_debt_usd']), debt)
            self.assertEqual(F(y['closing_debt_usd']), debt)
            self.assertEqual(F(y['net_borrowing_usd']), 0)
            self.assertEqual(F(y['interest_expense_usd']), debt*kd)
            expected = F(y['fcff_usd']) - debt*kd*(1-F(a['forecast_tax_rate']))
            self.assertLess(abs(F(y['fcfe_usd'])-expected), F('1e-30'))
            total += F(y['fcfe_usd'])/(1+ke)**i
        g = F(self.doc['base_case']['terminal_valuation']['terminal_growth'])
        self.assertEqual(F(r['fcfe']['terminal']['net_borrowing_usd']), debt*g)
        total += F(r['fcfe']['terminal']['fcfe_usd'])/(ke-g)/(1+ke)**len(r['fcfe']['years'])
        self.assertLess(abs(total-F(r['fcfe']['operating_equity_value_usd'])), F('1e-30'))

    def test_changes_recalculate_both_values_with_exact_one_dollar_per_share_effect(self):
        changed = copy.deepcopy(self.doc)
        changed['assumptions']['additional_claims_usd'] = self.result['bridge']['valuation_shares']
        r = run_apple_analyst(changed, ROOT)
        for method in ('fcff', 'fcfe'):
            self.assertLess(abs(D(self.result[method]['value_per_share_usd']) - D(r[method]['value_per_share_usd']) - 1), D('1e-24'))
        changed = copy.deepcopy(self.doc); changed['assumptions']['historical_other_financing_fraction'] = '1'
        other = run_apple_analyst(changed, ROOT)
        for old, new in zip(self.result['historical'], other['historical'], strict=True):
            self.assertEqual(D(new['fcfe_usd'])-D(old['fcfe_usd']), D(old['other_financing_usd']))
        self.assertEqual(other['fcff'], self.result['fcff'])
        self.assertEqual(other['fcfe'], self.result['fcfe'])

    def test_all_scenarios_five_and_ten_years_and_ambient_decimal_isolation(self):
        for label in ('Bear', 'Base', 'Bull'):
            for horizon in (5, 10):
                doc = document(self.profile, label, horizon)
                r = run_apple_analyst(doc, ROOT)
                self.assertEqual(len(r['fcfe']['years']), horizon)
                self.assertEqual(len(r['readiness']), 5)
                self.assertEqual(r['fcff']['enterprise_value_usd'], run_case(read_case(json.dumps(doc['base_case'])), ROOT)['stage_b']['enterprise_value'])
        with localcontext() as ctx:
            ctx.prec = 6
            self.assertEqual(run_apple_analyst(self.doc, ROOT), self.result)

    def test_validation_rejects_unjustified_and_incompatible_requests(self):
        mutations = [
            lambda d: d['base_case']['anchor'].update(kind='meta-fy2025'),
            lambda d: d['assumptions'].update(additional_claims_usd='-1'),
            lambda d: d['assumptions'].update(cost_of_equity='0.025'),
            lambda d: d['assumptions'].update(rsu_vesting_fraction='1.01'),
            lambda d: d['assumptions'].update(cost_of_equity='NaN'),
            lambda d: d['assumptions'].update(extra='0'),
        ]
        for mutation in mutations:
            doc = copy.deepcopy(self.doc); mutation(doc)
            with self.assertRaises(CaseInputError): read_apple_analyst(json.dumps(doc))
        doc = copy.deepcopy(self.doc); doc['assumptions']['operating_cash_reserve_ratio'] = '1'
        with self.assertRaises(CaseInputError): run_apple_analyst(doc, ROOT)

    def test_source_pin_and_history_are_not_status_overrides(self):
        policy = read_policy(ROOT)
        self.assertEqual(policy['defaults'], DEFAULTS)
        self.assertEqual(policy['facts']['dated_common_shares']['scope']['end'], '2025-09-27')
        self.assertTrue(all(p['exact_full_fcfe_verified'] is False for p in self.result['historical']))
        self.assertTrue(all(s['classification']=='ILLUSTRATIVE_ANALYST_SENSITIVITY_NOT_A_BOUND' for s in self.result['sensitivities']))


if __name__ == '__main__': unittest.main()
