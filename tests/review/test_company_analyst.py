"""Issuer source preservation, independent valuation identities and assumption controls."""
import copy
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import unittest

from valuation_platform.preload.generate import generate, engine_request
from valuation_platform.review.company_analyst import READY, SPECS, analyst_profile, read_company_analyst, read_policy, run_company_analyst
from valuation_platform.review.pilot_cashflows import read_cashflows
from valuation_platform.valuation.case_inputs import CaseInputError, read_case, run_case
from valuation_platform.review.apple_analyst import run_apple_analyst
from valuation_platform.valuation.fcfe import financing_bridge
from tests.review.test_apple_analyst import document as apple_document

ROOT=Path(__file__).resolve().parents[2]


def document(ticker='META',label='Base',horizon=5,profile=None):
    p=profile or generate(ROOT,ticker=ticker,generated_at='2026-11-04T00:00:00+00:00')
    base=engine_request(p,label)
    if horizon==10:
        base.update(schema_version='analyst-case-v4',forecast_horizon=10)
        for i in range(6,11):base['forecast_years'].append(dict(base['forecast_years'][-1],period_index=i,fiscal_year_label=f'FY{2025+i}'))
    return dict(schema_version='company-analyst-request-v1',ticker=ticker,base_case=base,assumptions=analyst_profile(ROOT,ticker)['defaults'])


class CompanyAnalystTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles={t:generate(ROOT,ticker=t,generated_at='2026-11-04T00:00:00+00:00') for t in SPECS}
        cls.documents={t:document(t,profile=cls.profiles[t]) for t in SPECS}
        cls.results={t:run_company_analyst(d,ROOT) for t,d in cls.documents.items()}

    def test_five_histories_preserve_cfo_capex_financing_and_original_unknowns(self):
        for t,r in self.results.items():
            old=read_cashflows(ROOT,t)['periods']
            for new,legacy in zip(r['historical'],old,strict=True):
                self.assertEqual(D(new['fcff_usd']),D(legacy['fcff']['amount_usd']))
                self.assertEqual(D(new['consolidated_fcfe_usd']),D(legacy['fcfe']['amount_usd']))
                self.assertFalse(new['exact_parent_cash_verified'])
                self.assertIsNone(legacy['fcfe']['parent_common_amount_usd'])
                self.assertEqual(D(new['economic_fcfe_usd']),D(new['fcfe_usd'])-D(new['sbc_usd']))
            self.assertEqual(len(r['historical']),5)
            self.assertEqual([g['status'] for g in r['readiness']],[READY]*5)
            self.assertFalse(r['exact_full_historical_fcfe_claim'])
            self.assertFalse(r['automatic_history_calibration'])
        self.assertTrue(all(p['scope']=='UNALLOCATED_CONSOLIDATED_PROXY' for p in self.results['GOOGL']['historical']))

    def test_source_bound_bridge_operands_and_investment_containment(self):
        expected={'META':('81592000000','58404000000','27524000000','2645552000','0'),
                  'GOOGL':('126843000000','48100000000','68687000000','12370000000','3400000000')}
        for t,values in expected.items():
            b=self.results[t]['bridge']
            for key,value in zip(('gross_cash_usd','debt_claims_usd','additional_assets_usd','valuation_shares','nci_claim_usd'),values):
                self.assertEqual(D(b[key]),D(value))
            # Meta 7.448B equity-method holdings are inside its 27.524B total.
            self.assertNotEqual(D(b['additional_assets_usd']),D('34972000000'))
            self.assertFalse(b['debt_subtracted_after_fcfe_discounting'])
            self.assertEqual(b['operating_lease_debt_deduction_usd'],'0')
            self.assertEqual(b['separate_existing_rsu_claim_deduction_usd'],'0')

    def test_independent_discounting_financing_and_both_per_share_identities(self):
        for t,r in self.results.items():
            doc=self.documents[t];a=doc['assumptions'];ke=F(a['cost_of_equity']);kd=F(a['pre_tax_cost_of_debt'])
            support=read_policy(ROOT,t)['anchor_support'];debt=F(support['financing_debt_carrying_usd']);pv=F(0)
            for i,(y,raw) in enumerate(zip(r['fcfe']['years'],doc['base_case']['forecast_years'],strict=True),1):
                self.assertEqual(F(y['closing_debt_usd']),debt)
                self.assertEqual(F(y['net_borrowing_usd']),0)
                self.assertEqual(F(y['interest_expense_usd']),debt*kd)
                tax=F(raw['forecast_tax_rate']);expected=F(y['fcff_usd'])-debt*kd*(1-tax)
                self.assertLess(abs(F(y['fcfe_usd'])-expected),F('1e-25'))
                pv+=F(y['fcfe_usd'])/(1+ke)**i
            g=F(doc['base_case']['terminal_valuation']['terminal_growth'])
            self.assertLess(abs(F(r['fcfe']['terminal']['net_borrowing_usd'])-debt*g),F('1e-25'))
            pv+=F(r['fcfe']['terminal']['fcfe_usd'])/(ke-g)/(1+ke)**len(r['fcfe']['years'])
            self.assertLess(abs(pv-F(r['fcfe']['operating_equity_value_usd'])),F('1e-25'))
            b=r['bridge'];assets=F(b['eligible_cash_usd'])+F(b['additional_assets_usd']);claims=F(b['additional_claims_usd'])+F(b['nci_claim_usd'])
            ff=F(r['fcff']['enterprise_value_usd'])+assets-F(b['debt_claims_usd'])-claims
            fe=F(r['fcfe']['operating_equity_value_usd'])+assets-claims
            self.assertLess(abs(F(r['fcff']['value_per_share_usd'])-ff/F(b['valuation_shares'])),F('1e-35'))
            self.assertLess(abs(F(r['fcfe']['value_per_share_usd'])-fe/F(b['valuation_shares'])),F('1e-35'))

    def test_twelve_scenario_horizon_combinations_and_decimal_isolation(self):
        for t,p in self.profiles.items():
            for label in ('Bear','Base','Bull'):
                for horizon in (5,10):
                    d=document(t,label,horizon,p);r=run_company_analyst(d,ROOT)
                    self.assertEqual(len(r['fcfe']['years']),horizon)
                    self.assertEqual(r['fcff']['enterprise_value_usd'],run_case(read_case(json.dumps(d['base_case'])),ROOT)['stage_b']['enterprise_value'])
                    self.assertTrue(all(D(r[k]['value_per_share_usd'])>0 for k in ('fcff','fcfe')))
            with localcontext() as ctx:
                ctx.prec=6
                self.assertEqual(run_company_analyst(self.documents[t],ROOT),self.results[t])

    def test_minority_cash_attribution_and_valuation_claim_are_separate(self):
        original=self.results['GOOGL'];d=copy.deepcopy(self.documents['GOOGL'])
        d['assumptions']['historical_minority_cash_share']='0.05';changed=run_company_analyst(d,ROOT)
        self.assertEqual(original['fcfe'],changed['fcfe']);self.assertEqual(original['fcff'],changed['fcff'])
        for p in changed['historical']:
            self.assertEqual(D(p['fcfe_usd']),D(p['consolidated_fcfe_usd'])*D('.95'))
        d=copy.deepcopy(self.documents['GOOGL']);shares=D(original['bridge']['valuation_shares'])
        d['assumptions']['nci_claim_usd']=str(D(d['assumptions']['nci_claim_usd'])+shares)
        changed=run_company_analyst(d,ROOT)
        for method in ('fcff','fcfe'):
            self.assertLess(abs(D(original[method]['value_per_share_usd'])-D(changed[method]['value_per_share_usd'])-1),D('1e-24'))
        self.assertEqual(original['historical'],changed['historical'])

    def test_private_asset_and_other_financing_assumptions_change_only_intended_scope(self):
        for t in SPECS:
            d=copy.deepcopy(self.documents[t]);old=self.results[t]
            d['assumptions']['additional_assets_usd']='0';r=run_company_analyst(d,ROOT)
            with localcontext() as ctx:
                ctx.prec=50;expected=D(old['bridge']['additional_assets_usd'])/D(old['bridge']['valuation_shares'])
                for method in ('fcff','fcfe'):self.assertLess(abs(D(old[method]['value_per_share_usd'])-D(r[method]['value_per_share_usd'])-expected),D('1e-35'))
            self.assertEqual(old['historical'],r['historical'])
        d=copy.deepcopy(self.documents['META']);d['assumptions']['historical_other_financing_fraction']='1'
        r=run_company_analyst(d,ROOT)
        for old,new in zip(self.results['META']['historical'],r['historical'],strict=True):
            self.assertEqual(D(new['fcfe_usd'])-D(old['fcfe_usd']),D(old['other_financing_usd']))
        self.assertEqual(r['fcfe'],self.results['META']['fcfe'])

    def test_invalid_issuer_identity_ownership_and_missing_inputs_are_rejected(self):
        for change in (lambda d:d.update(ticker='AAPL'),lambda d:d['assumptions'].pop('additional_assets_usd'),
                       lambda d:d['assumptions'].update(cost_of_equity='0.01'),lambda d:d['assumptions'].update(nci_claim_usd='1'),
                       lambda d:d['assumptions'].update(historical_minority_cash_share='0.1'),lambda d:d['assumptions'].update(additional_assets_usd='NaN')):
            d=copy.deepcopy(self.documents['META']);change(d)
            with self.assertRaises(CaseInputError):read_company_analyst(json.dumps(d))
        d=copy.deepcopy(self.documents['META']);d['assumptions']['operating_cash_reserve_ratio']='1'
        with self.assertRaises(CaseInputError):run_company_analyst(d,ROOT)

    def test_apple_existing_accepted_values_and_other_source_records_do_not_change(self):
        r=run_apple_analyst(apple_document(),ROOT)
        self.assertEqual(D(r['fcff']['value_per_share_usd']).quantize(D('.01')),D('175.46'))
        self.assertEqual(D(r['fcfe']['value_per_share_usd']).quantize(D('.01')),D('161.00'))

    def test_ten_year_rounding_is_visible_and_real_cash_component_errors_still_fail(self):
        r=run_company_analyst(document('GOOGL','Bear',10,self.profiles['GOOGL']),ROOT)
        rounded=[y for y in [*r['fcfe']['years'],r['fcfe']['terminal']] if 'income_bridge_rounding_difference_usd' in y]
        self.assertTrue(rounded)
        for y in rounded:
            difference=abs(D(y['income_bridge_rounding_difference_usd']))
            self.assertLess(difference,D('1e-30'))
            self.assertLessEqual(difference,D(y['income_bridge_rounding_envelope_usd']))
            self.assertFalse(y['rounding_difference_is_cash_adjustment'])
        op=dict(ebit='100',d_and_a='5',investment='10',working_capital_cash_requirement='2',fcff='68.01')
        funding=dict(interest_expense_usd='1',cash_debt_issued_usd='0',new_finance_asset_funding_usd='0',principal_repaid_usd='0')
        with self.assertRaisesRegex(CaseInputError,'operating FCFF'):
            financing_bridge(op,D('.25'),funding,D('10'))


if __name__=='__main__':unittest.main()
