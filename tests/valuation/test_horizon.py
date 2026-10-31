"""Ten-year arithmetic against independent rational expectations; no company forecasts."""
from decimal import Decimal as D
from fractions import Fraction as F
import json
import unittest
from tests.valuation.test_terminal_methods import method_document, execute, ROOT
from valuation_platform.valuation import case_inputs as c, scenario_inputs as scenarios, sensitivity_inputs as sensitivity
from valuation_platform.api.budget import read_http_case
from valuation_platform.review.comparison import run_review


def ten_year_document(exit=False, equity=False):
    doc=method_document(exit=exit,equity=equity,investor=True)
    doc.update(schema_version='investor-case-v4',forecast_horizon=10)
    doc['conventions']['discounting']='fiscal-end-terminal-ev-ebit-v2' if exit else 'fiscal-end-annual-gordon-v1'
    for i in range(6,11):
        doc['forecast_years'].append(dict(doc['forecast_years'][-1],period_index=i,fiscal_year_label=f'FY{2025+i}'))
    return doc


class TenYearHorizonTests(unittest.TestCase):
    def test_gordon_exact_ten_cashflows_and_year_eleven_terminal(self):
        b=execute(ten_year_document())['stage_b']
        self.assertEqual(len(b['years']),10)
        self.assertEqual(b['terminal']['period_index'],11)
        self.assertEqual(b['timing']['annual_discount_exponents'],list(range(1,11)))
        self.assertEqual(b['timing']['terminal_value_discount_exponent'],10)
        explicit=sum(F(100)*F(11,10)**i*F(8,100)/F(5,4)**i for i in range(1,11))
        # Fixture terminal: .30 × (1 − .20) + .04 − .09 − .01 = .18.
        tv=F(100)*F(11,10)**10*F(105,100)*F(18,100)/F(20,100)
        for key,value in [('pv_explicit_fcff',explicit),('terminal_value',tv),('pv_terminal_value',tv/F(5,4)**10),('enterprise_value',explicit+tv/F(5,4)**10)]:
            self.assertEqual(F(D(b[key])),value)
        five=execute(method_document(exit=False,investor=True))['stage_b']
        self.assertEqual(b['stage_a']['years'][:5],five['stage_a']['years'])
        self.assertEqual(b['years'][:5],five['years'])

    def test_exit_uses_year_ten_ebit_and_tenth_discount_factor(self):
        b=execute(ten_year_document(exit=True))['stage_b']
        self.assertEqual(b['terminal_basis']['period_index'],10)
        self.assertIn('final_year_ebit',b['terminal_basis']);self.assertNotIn('year_five_ebit',b['terminal_basis'])
        tv=F(100)*F(11,10)**10*F(1,5)*15
        self.assertEqual(F(D(b['terminal_value'])),tv)
        self.assertEqual(F(D(b['pv_terminal_value'])),tv/F(5,4)**10)
        self.assertIn('implied_final_year_ev_ebit',execute(ten_year_document())['terminal_comparison'])

    def test_missing_extra_year_inputs_and_malformed_horizons_are_rejected(self):
        for change in ('missing','duplicate','legacy','flag','unknown'):
            doc=ten_year_document()
            if change=='missing':doc['forecast_years'][9]['revenue_growth']=None
            if change=='duplicate':doc['forecast_years'][9]['period_index']=9
            if change=='legacy':doc['schema_version']='investor-case-v3';doc.pop('forecast_horizon')
            if change=='flag':doc['forecast_horizon']=True
            if change=='unknown':doc['forecast_horizon']=7
            with self.subTest(change=change),self.assertRaises(c.CaseInputError):c.read_case(json.dumps(doc))

    def test_http_budget_intake_and_equity_handoff(self):
        doc=ten_year_document(equity=True)
        case=read_http_case(json.dumps(doc).encode())
        result=c.run_case(case,ROOT)
        self.assertEqual(len(result['stage_b']['years']),10)
        self.assertEqual(result['stage_c']['stage_b']['enterprise_value'],result['stage_b']['enterprise_value'])

    def test_scenarios_require_same_horizon_and_calculate_all_ten_years(self):
        doc=dict(schema_version='investor-scenario-set-v3',scenario_set_name='Synthetic ten years',scenarios=[dict(label=label,analytical_date='2025-12-31',information_cutoff=None,case=ten_year_document()) for label in ('Bear','Base','Bull')])
        result=scenarios.run_scenario_set(scenarios.read_scenario_set(json.dumps(doc)),ROOT)
        self.assertTrue(all(len(x['result']['stage_b']['years'])==10 for x in result['scenarios']))
        doc['scenarios'][0]['case']=method_document(exit=False,investor=True)
        with self.assertRaisesRegex(c.CaseInputError,'period identities'):scenarios.read_scenario_set(json.dumps(doc))

    def test_sensitivity_reuses_ten_year_source_for_both_methods(self):
        for exit in (False,True):
            case=ten_year_document(exit=exit)
            doc=dict(schema_version='investor-sensitivity-request-v3' if exit else 'investor-sensitivity-request-v2',sensitivity_name='Synthetic ten years',source=dict(kind='single_case',case=case,analytical_date='2025-12-31',information_cutoff=None),wacc_values=['0.25'])
            doc['exit_ev_ebit_multiple_values' if exit else 'terminal_growth_values']=['15'] if exit else ['0.05']
            result=sensitivity.run_sensitivity(sensitivity.read_sensitivity(json.dumps(doc)),ROOT)
            self.assertEqual(result['cells'][0][0]['metrics']['enterprise_value'],result['reference_result']['stage_b']['enterprise_value'])
            self.assertEqual(len(result['reference_result']['stage_b']['years']),10)
            if exit:self.assertIn('final_year_ebit',result['cells'][0][0]['metrics'])

    def test_review_retains_ten_year_output_and_blocks_five_year_reverse_certificate(self):
        r=run_review(c.read_case(json.dumps(ten_year_document())),ROOT)
        self.assertEqual(len(r['result']['stage_b']['years']),10)
        self.assertEqual(D(r['review']['forecast_cagr']),D('.1'))
        self.assertTrue(any('UNSUPPORTED_REVERSE_HORIZON' in x for x in r['review']['reasons']))
        self.assertIsNone(r['review']['market_implied_growth'])
