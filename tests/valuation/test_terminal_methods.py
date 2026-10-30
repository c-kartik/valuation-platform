"""Synthetic method arithmetic, strict intake and legacy byte compatibility."""
from copy import deepcopy
from dataclasses import replace
from decimal import Context, Decimal as D, Inexact, Rounded, ROUND_DOWN, localcontext
from fractions import Fraction as F
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from tests.valuation.test_case_inputs import ROOT, EXAMPLES, document, cli
from valuation_platform.valuation import case_inputs as c, sensitivity_inputs as s, scenario_inputs as scenarios
from valuation_platform.valuation.bridge import bridge_to_per_share, BridgeValidationError
from valuation_platform.valuation.forecast import forecast_five_years
from valuation_platform.valuation.terminal_methods import value_terminal, implied_multiple
from valuation_platform.valuation.reverse_inputs import read_reverse


def method_document(exit=True, equity=False, investor=False):
    doc=json.loads((EXAMPLES/('synthetic-equity.json' if equity else 'synthetic-base.json')).read_text())
    gordon=dict(method='perpetual_growth', terminal_growth=doc.pop('terminal_growth'), terminal=doc.pop('terminal'))
    multiple=dict(method='exit_multiple', exit_ev_ebit_multiple='15')
    doc.update(schema_version='analyst-case-v3', calculation_scope='EQUITY_PER_SHARE' if equity else 'ENTERPRISE_VALUE',
        terminal_valuation=multiple if exit else gordon, comparison_terminal_valuation=gordon if exit else multiple)
    doc['conventions']['discounting']='fiscal-end-year-five-ev-ebit-v1' if exit else 'fiscal-end-annual-gordon-v1'
    if investor:
        doc.pop('analyst');doc.pop('scope');doc['schema_version']='investor-case-v3'
        doc['preparation']={'provenance':'ANONYMOUS_INVESTOR','timestamp_utc':'2000-01-01T00:00:00Z','notes':'Synthetic method test only'}
    return doc


def execute(doc):return c.run_case(c.read_case(json.dumps(doc)),ROOT)


def grid_document(equity=False):
    return dict(schema_version='investor-sensitivity-request-v3', sensitivity_name='Synthetic WACC × multiple',
        source=dict(kind='single_case',case=method_document(equity=equity,investor=True),analytical_date='2025-12-31',information_cutoff=None),
        wacc_values=['0.10','0.25'],exit_ev_ebit_multiple_values=['10','15','20'])


class TerminalMethodTests(unittest.TestCase):
    def test_independent_rational_exit_and_identical_annual_components(self):
        old=execute(document())['stage_b'];new=execute(method_document())['stage_b']
        self.assertEqual(new['stage_a']['years'],old['stage_a']['years']);self.assertEqual(new['years'],old['years'])
        self.assertEqual(new['pv_explicit_fcff'],old['pv_explicit_fcff'])
        revenue=F(100)*F(11,10)**5;ebit=revenue/F(5);tv=ebit*15;pv=tv/F(5,4)**5
        explicit=sum(F(100)*F(11,10)**i*F(8,100)/F(5,4)**i for i in range(1,6))
        for key,exact in [('terminal_value',tv),('pv_terminal_value',pv),('pv_explicit_fcff',explicit),('enterprise_value',pv+explicit)]:
            self.assertEqual(F(D(new[key])),exact)
        self.assertNotIn('terminal',new);self.assertNotIn('terminal_assumptions',new)
        self.assertNotIn('terminal_growth',new['stage_a']['assumptions'])
        self.assertEqual(new['terminal_basis']['period_index'],5)
        self.assertEqual(new['timing']['terminal_value_discount_exponent'],5)

    def test_comparison_selected_independent_of_missing_or_invalid_other(self):
        for exit in (False,True):
            for other in (None,{'method':'perpetual_growth','terminal_growth':None,'terminal':{k:None for k in c.TERMINAL_RATES}} if exit else {'method':'exit_multiple','exit_ev_ebit_multiple':'-1'}):
                doc=method_document(exit);doc['comparison_terminal_valuation']=other
                r=execute(doc);selected=doc['terminal_valuation']['method'];comp=r['terminal_comparison']
                self.assertEqual(comp['results'][selected]['status'],'CURRENT');self.assertEqual(len(comp['results']),2)
                self.assertEqual(comp['results']['perpetual_growth' if exit else 'exit_multiple']['status'],'AWAITING_INPUTS')
                self.assertIsNone(comp['ev_difference_exit_minus_perpetual'])
        zero_ebit=method_document(False)
        zero_ebit['forecast_years'][4]['operating_margin']='0'
        self.assertIsNone(execute(zero_ebit)['terminal_comparison']['implied_year_five_ev_ebit']['value'])
        comp=execute(method_document())['terminal_comparison']
        self.assertEqual(D(comp['implied_year_five_ev_ebit']['value']),D('4.725'))
        with localcontext(Context(prec=50)):
            self.assertEqual(D(comp['ev_difference_exit_minus_perpetual']),D('186.0259692544')-D('77.577060352'))

    def test_strict_multiple_and_no_unused_gordon_operands(self):
        for raw in (None,0,15,True,'0','-1','NaN','Infinity','15×','15%','1e99999999999999999999'):
            doc=method_document();doc['terminal_valuation']['exit_ev_ebit_multiple']=raw
            with self.subTest(raw=raw),self.assertRaises(c.CaseInputError):c.read_case(json.dumps(doc))
        for raw in ('0','-0.2',None):
            doc=method_document();doc['forecast_years'][4]['operating_margin']=raw
            with self.assertRaisesRegex(c.CaseInputError,'forecast_years\\[4\\].operating_margin'):c.read_case(json.dumps(doc))
        doc=method_document();doc['terminal_growth']='0.03'
        with self.assertRaisesRegex(c.CaseInputError,'unknown field'):c.read_case(json.dumps(doc))
        text=json.dumps(method_document()).replace('"exit_ev_ebit_multiple": "15"','"exit_ev_ebit_multiple": "15", "exit_ev_ebit_multiple": "20"')
        with self.assertRaisesRegex(c.CaseInputError,'Duplicate JSON key'):c.read_case(text)
        doc=method_document();doc['comparison_terminal_valuation']['unknown']='x'
        with self.assertRaisesRegex(c.CaseInputError,'unknown fields'):c.read_case(json.dumps(doc))
        doc=method_document();doc['comparison_terminal_valuation']=None;doc['wacc']='0.01'
        self.assertGreater(D(execute(doc)['stage_b']['enterprise_value']),0) # No g<WACC against unused growth.

    def test_negative_zero_and_over_one_contributions(self):
        # At no growth, w=.25, EBIT=20, terminal multiple 15 => PV terminal 98.304.
        # Sum five factors = 2.68928; select FCFF so explicit PV cancels exactly.
        for fcff in (D('-40'),D('-36.553191489361702127659574468085106382978723404255'),D('-10')):
            doc=method_document();doc['comparison_terminal_valuation']=None
            for y in doc['forecast_years']:
                y.update(revenue_growth='0',operating_margin='0.2',forecast_tax_rate='0',d_and_a_percent_revenue='0',change_in_operating_nwc_percent_revenue='0')
                with localcontext(Context(prec=50)):y['capex_percent_revenue']=str((D(20)-fcff)/100)
            b=execute(doc)['stage_b'];self.assertTrue(all(D(y['fcff'])<0 for y in b['stage_a']['years']))
            if fcff==D('-40'):self.assertLess(D(b['enterprise_value']),0)
            if fcff==D('-10'):self.assertGreater(D(b['pv_terminal_value'])/D(b['enterprise_value']),1)
        # Exact zero fixture uses WACC=1, equal annual FCFF -10, EBIT=20, multiple15.5.
        doc=method_document();doc['wacc']='1';doc['comparison_terminal_valuation']=None;doc['terminal_valuation']['exit_ev_ebit_multiple']='15.5'
        for y in doc['forecast_years']:y.update(revenue_growth='0',operating_margin='0.2',forecast_tax_rate='0',d_and_a_percent_revenue='0',capex_percent_revenue='0.3',change_in_operating_nwc_percent_revenue='0')
        r=execute(doc);self.assertEqual(D(r['stage_b']['enterprise_value']),0)
        self.assertIn('undefined (EV is zero)',cli.render_summary(r));self.assertIsNone(s._metrics(r)['terminal_contribution'])

    def test_implied_unavailable_and_exit_handoff_tampering(self):
        from valuation_platform.valuation.discounting import discount_to_enterprise_value
        from tests.valuation.test_discounting import stage_a,terminal_assumptions
        from tests.valuation.test_bridge import inputs
        a=stage_a();negative=replace(terminal_assumptions(),operating_margin=D('-1'))
        self.assertIsNone(implied_multiple(discount_to_enterprise_value(a,negative))['value'])
        exit_case=c.read_case(json.dumps(method_document(equity=True)));run=c._prepare_case_runner(exit_case,ROOT)
        result=run(exit_case);self.assertEqual(D(result['stage_c']['value_per_share']),(D(result['stage_b']['enterprise_value'])-11)/4)
        # Reconstruct from publicly constructible models and reject modified convention/totals/order.
        anchor=stage_a().anchor
        a=forecast_five_years(anchor,exit_case.assumptions)
        b=value_terminal(a,exit_case.terminal)
        for bad in (replace(b,enterprise_value=b.enterprise_value+1),replace(b,convention_version='gordon'),replace(b,years=b.years[::-1])):
            with self.assertRaises(BridgeValidationError):bridge_to_per_share(bad,exit_case.bridge)

    def test_isolated_context_and_no_input_mutation(self):
        doc=method_document();before=deepcopy(doc);expected=execute(doc)
        with localcontext() as context:
            context.prec=3;context.rounding=ROUND_DOWN;context.traps[Inexact]=True;context.traps[Rounded]=True;context.clear_flags()
            self.assertEqual(execute(doc),expected);self.assertFalse(any(context.flags.values()))
        self.assertEqual(doc,before)

    def test_exit_grid_matches_independent_single_cases_and_rationals(self):
        for equity in (False,True):
            doc=grid_document(equity);before=deepcopy(doc);result=s.run_sensitivity(s.read_sensitivity(json.dumps(doc)),ROOT)
            self.assertNotIn('terminal_growth_values',result)
            for i,w in enumerate(doc['wacc_values']):
                for j,m in enumerate(doc['exit_ev_ebit_multiple_values']):
                    cell=result['cells'][i][j];single=deepcopy(doc['source']['case']);single['wacc']=w;single['terminal_valuation']['exit_ev_ebit_multiple']=m
                    self.assertEqual(cell['metrics']['enterprise_value'],execute(single)['stage_b']['enterprise_value'])
                    exact=sum(F(100)*F(11,10)**n*F(8,100)/(1+F(w))**n for n in range(1,6))+F(100)*F(11,10)**5*F(1,5)*F(m)/(1+F(w))**5
                    with localcontext(Context(prec=50)):
                        self.assertLess(abs(D(cell['metrics']['enterprise_value'])-D(exact.numerator)/D(exact.denominator)),D('1e-46'))
                    self.assertNotIn('terminal_fcff',cell['metrics'])
            self.assertEqual(doc,before)
        for values in (['0'],['-1'],['15']*12,['20','15'],['NaN']):
            doc=grid_document();doc['exit_ev_ebit_multiple_values']=values
            with self.assertRaises(s.SensitivityInputError):s.read_sensitivity(json.dumps(doc))

    def test_scenarios_same_method_multiple_only_changes_value(self):
        doc=dict(schema_version='investor-scenario-set-v3',scenario_set_name='Synthetic method set',scenarios=[dict(label=l,analytical_date='2025-12-31',information_cutoff=None,case=method_document(investor=True)) for l in scenarios.LABELS])
        for i,e in enumerate(doc['scenarios']):e['case']['terminal_valuation']['exit_ev_ebit_multiple']=str(10+5*i)
        r=scenarios.run_scenario_set(scenarios.read_scenario_set(json.dumps(doc)),ROOT)
        self.assertEqual(len({x['result']['stage_b']['enterprise_value'] for x in r['scenarios']}),3)
        self.assertEqual(r['scenarios'][0]['result']['stage_b']['stage_a']['years'],r['scenarios'][2]['result']['stage_b']['stage_a']['years'])
        doc['scenarios'][0]['case']=method_document(exit=False,investor=True)
        with self.assertRaisesRegex(scenarios.ScenarioInputError,'conventions'):scenarios.read_scenario_set(json.dumps(doc))

    def test_reverse_explicitly_rejects_exit_before_calculation(self):
        from tests.valuation.test_reverse import document as reverse_document
        doc=reverse_document();doc['source']=dict(kind='single_case',case=method_document(),analytical_date='2025-12-31',information_cutoff='2026-01-29')
        with self.assertRaisesRegex(c.CaseInputError,'UNSUPPORTED_TERMINAL_METHOD'):read_reverse(json.dumps(doc))

    def test_validation_only_and_cli_output_protection(self):
        from contextlib import redirect_stdout,redirect_stderr
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'input.json';path.write_text(json.dumps(method_document()));before=path.read_bytes()
            with patch('valuation_platform.valuation.case_inputs.run_case',side_effect=AssertionError('must not calculate')),redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main([str(path)]),0)
            output=Path(directory)/'result.json'
            with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(path),'--run','--output',str(output)]),0)
            self.assertEqual(json.loads(output.read_text()),execute(method_document()))
            with redirect_stderr(io.StringIO()):self.assertEqual(cli.main([str(path),'--run','--output',str(output)]),2)
            self.assertEqual(before,path.read_bytes());self.assertIn('Year-five EV/EBIT',cli.render_summary(execute(method_document())))

    def test_legacy_outputs_against_isolated_starting_checkout(self):
        # Run the original engine, not the original CLI importing our current engine.
        raw=subprocess.check_output(['git','archive','021796d','src','scripts/run_analyst_case.py','examples/valuation'],cwd=ROOT)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with tarfile.open(fileobj=io.BytesIO(raw)) as archive:archive.extractall(root,filter='data')
            for name in ('synthetic-base.json','synthetic-equity.json'):
                before=subprocess.check_output([sys.executable,str(root/'scripts/run_analyst_case.py'),str(root/'examples/valuation'/name),'--run'],cwd=root)
                after=subprocess.check_output([sys.executable,str(ROOT/'scripts/run_analyst_case.py'),str(EXAMPLES/name),'--run'],cwd=ROOT)
                self.assertEqual(before,after)
