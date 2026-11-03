"""Controlled independent financing / discount-rate / tax perimeter checks."""
import copy
from decimal import Decimal as D, localcontext
import json
from pathlib import Path
import unittest

from valuation_platform.valuation.fcfe import FIELDS, financing_bridge, read_fcfe, run_fcfe, equity_cost, weighted_cost
from valuation_platform.valuation.case_inputs import CaseInputError, read_case, run_case
ROOT = Path(__file__).resolve().parents[2]

def funding(interest='0',issue='0',assets='0',repayment='0'):
    return dict(zip(FIELDS,(interest,issue,assets,repayment)))

def document(growth='0',debt='0'):
    base=json.loads((ROOT/'examples/valuation/synthetic-base.json').read_text())
    for y in base['forecast_years']:y['revenue_growth']=format(D(growth),'f')
    base['wacc']='0.10';base['terminal_growth']=format(D(growth),'f')
    base['terminal']=dict(operating_margin='0.20',operating_tax_rate='0.25',d_and_a_percent_revenue='0.05',investment_percent_revenue='0.10',working_capital_cash_requirement_percent_revenue='0.02')
    return dict(schema_version='fcfe-forecast-request-v1',base_case=base,scope='DECLARED_PARENT_COMMON',cost_of_equity='.10',opening_debt_usd=debt,
        financing_years=[dict(period_index=i,**funding()) for i in range(1,6)],terminal_growth=growth,terminal_financing=funding())

class FcfeTests(unittest.TestCase):
    def test_ten_year_fcfe_and_declared_ownership_scope(self):
        from tests.valuation.test_horizon import ten_year_document
        d=document();d['base_case']=ten_year_document()
        d['financing_years']=[dict(period_index=i,**funding()) for i in range(1,11)]
        d['cost_of_equity']=d['base_case']['wacc']
        d['terminal_growth']=d['base_case']['terminal_valuation']['terminal_growth']
        result=run_fcfe(d,ROOT)
        reference=run_case(read_case(json.dumps(d['base_case'])),ROOT)
        self.assertEqual(len(result['years']),10)
        self.assertEqual(result['equity_value_usd'],reference['stage_b']['enterprise_value'])
        self.assertEqual(result['scope'],'DECLARED_PARENT_COMMON')
        self.assertEqual(result['semantic_input_review'],'USER_ASSUMPTIONS_NOT_INDEPENDENTLY_CERTIFIED')

    def test_all_equity_matches_fcff_and_no_second_debt_subtraction(self):
        d=document('.02');v=run_fcfe(d,ROOT);f=run_case(read_case(json.dumps(d['base_case'])),ROOT)
        self.assertEqual(v['equity_value_usd'],f['stage_b']['enterprise_value'])
        self.assertFalse(v['debt_subtracted_after_fcfe_discounting']);self.assertIsNone(v['value_per_share'])

    def test_consistent_leverage_and_positive_debt_growth_match_fcff(self):
        # Independent growing perpetuity: FCFF1=8*1.02; FCFE1=8.16-.75+.4=7.81.
        # E0=7.81/(.10-.02)=97.625; D0=20. Cost debt .05; debt grows2%.
        with localcontext() as ctx:
            ctx.prec=50
            g=D('.02');debt=D(20);d=document(str(g),str(debt));equity=D('97.625')
            wacc=weighted_cost('.10','.05','.25',str(equity),str(debt));d['base_case']['wacc']=str(wacc)
            for y in d['financing_years']:
                y.update(funding(str(debt*D('.05')),str(debt*g)));debt*=1+g
            d['terminal_financing']=funding(str(debt*D('.05')),str(debt*g))
            e=run_fcfe(d,ROOT);f=run_case(read_case(json.dumps(d['base_case'])),ROOT)
            self.assertLess(abs(D(e['equity_value_usd'])-equity),D('1e-40'))
            self.assertLess(abs(D(f['stage_b']['enterprise_value'])-D(20)-equity),D('1e-40'))

    def test_loss_tax_shield_is_capped_and_finance_assets_count_once(self):
        op=dict(ebit='1',d_and_a='2',investment='5',working_capital_cash_requirement='1',fcff='-3.25')
        r=financing_bridge(op,D('.25'),funding('2','0','3','1'),D('10'))
        self.assertEqual(D(r['interest_tax_shield_usd']),D('.25'))
        self.assertEqual(D(r['fcfe_usd']),D('-3'))
        self.assertEqual(D(r['closing_debt_usd']),D(12))
        op.update(ebit='-1',fcff='-5')
        self.assertEqual(D(financing_bridge(op,D('.25'),funding('2'),D(10))['interest_tax_shield_usd']),0)
        with self.assertRaises(CaseInputError):financing_bridge(op,D('.25'),funding('2','0','6'),D(10))
        with self.assertRaises(CaseInputError):financing_bridge(op,D('.25'),funding('0','0','0','11'),D(10))

    def test_context_isolation_and_explicit_terminal_constraints(self):
        d=document();ref=run_fcfe(d,ROOT)
        with localcontext() as ctx:
            ctx.prec=6
            self.assertEqual(run_fcfe(d,ROOT),ref)
        d['terminal_financing']=funding('0','1')
        with self.assertRaises(CaseInputError):run_fcfe(d,ROOT)
        d=document();d['base_case']['terminal']['operating_margin']='0.01'
        with self.assertRaises(CaseInputError):run_fcfe(d,ROOT)

    def test_strict_inputs_require_complete_explicit_financing(self):
        for mutation in [lambda d:d['financing_years'].pop(),lambda d:d['financing_years'][0].update(principal_repaid_usd=None),lambda d:d.update(cost_of_equity='NaN'),lambda d:d.update(terminal_growth='.10'),lambda d:d.update(scope='PARENT_PROVEN'),lambda d:d['terminal_financing'].update(extra='0')]:
            d=document();mutation(d)
            with self.assertRaises(CaseInputError):read_fcfe(json.dumps(d))
        d=document();d['base_case']['bridge']={}
        with self.assertRaises(CaseInputError):read_fcfe(json.dumps(d))
        self.assertEqual(equity_cost('.04','1.2','.05'),D('.10'))
        self.assertEqual(weighted_cost('.10','.05','.25','80','20'),D('.0875'))

if __name__=='__main__':unittest.main()
