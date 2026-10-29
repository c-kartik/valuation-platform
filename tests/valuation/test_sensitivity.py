"""Synthetic sensitivity arithmetic, boundary, CLI and retained-anchor integration."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from decimal import Context, Decimal as D, Inexact, ROUND_DOWN, Rounded, localcontext
from fractions import Fraction as F
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

from valuation_platform.valuation import case_inputs as c, sensitivity_inputs as s
from tests.valuation.test_case_inputs import ROOT, EXAMPLES
from tests.valuation.test_scenarios import document as scenario_document

SCRIPT = ROOT / 'scripts/run_analyst_sensitivity.py'
spec = importlib.util.spec_from_file_location('sensitivity_cli', SCRIPT)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def document(equity=False, scenario=None):
    doc = json.loads((EXAMPLES / ('synthetic-sensitivity-equity.json' if equity else 'synthetic-sensitivity-ev.json')).read_text())
    if scenario is not None:
        doc['source'] = dict(kind='scenario_set', scenario_label=scenario, scenario_set=scenario_document(equity))
    return doc


def parse(doc):
    return s.read_sensitivity(json.dumps(doc))


def execute(doc=None):
    return s.run_sensitivity(parse(document() if doc is None else doc), ROOT)


class SensitivityTests(unittest.TestCase):
    def assert_close(self, actual, exact):
        with localcontext(Context(prec=70)):
            expected = D(exact.numerator) / D(exact.denominator)
            self.assertLess(abs(D(actual) - expected), D('1e-40'))

    def test_every_valid_cell_and_reference_equal_independent_single_submissions(self):
        for equity in (False, True):
            doc = document(equity); before = deepcopy(doc); result = execute(doc)
            selected = doc['source']['case']
            reference = c.run_case(c.read_case(json.dumps(selected)), ROOT)
            self.assertEqual(result['reference_result'], reference)
            self.assertEqual(result['submitted_inputs'], doc)
            self.assertEqual(result['selected_case'], selected)
            for row in result['cells']:
                for cell in row:
                    if cell['status'] == 'INVALID':
                        self.assertTrue(all(value is None for value in cell['metrics'].values()))
                        self.assertIsNone(cell['changes']);continue
                    submission = deepcopy(selected)
                    submission.update(wacc=cell['wacc'], terminal_growth=cell['terminal_growth'])
                    independent = c.run_case(c.read_case(json.dumps(submission)), ROOT)
                    for key in ('enterprise_value','pv_explicit_fcff','pv_terminal_value'):
                        self.assertEqual(cell['metrics'][key], independent['stage_b'][key])
                    self.assertEqual(independent['stage_b']['stage_a']['years'], reference['stage_b']['stage_a']['years'])
                    self.assertEqual(independent['stage_b']['stage_a']['anchor'], reference['stage_b']['stage_a']['anchor'])
                    fixed = deepcopy(independent['submitted_inputs']);fixed.update(wacc=selected['wacc'],terminal_growth=selected['terminal_growth'])
                    self.assertEqual(fixed,selected)
                    if equity:
                        for key in ('equity_value','value_per_share'):
                            self.assertEqual(cell['metrics'][key], independent['stage_c'][key])
                        self.assertEqual(independent['stage_c']['inputs'],reference['stage_c']['inputs'])
            self.assertEqual(result['cells'][1][1]['metrics'],result['reference_metrics'])
            self.assertTrue(all(D(x['absolute']) == 0 for x in result['cells'][1][1]['changes'].values()))
            self.assertEqual(doc,before)

    def test_independent_rational_arithmetic_and_growth_changes_terminal_numerator(self):
        result=execute(document(True))
        for row in result['cells']:
            for cell in row:
                if cell['status']!='VALID':continue
                w,g=F(cell['wacc']),F(cell['terminal_growth'])
                revenues=[F(100)*F(11,10)**i for i in range(1,6)]
                pv=sum(r*F(8,100)/(1+w)**i for i,r in enumerate(revenues,1))
                terminal_r=revenues[-1]*(1+g);terminal_f=terminal_r*F(18,100)
                tv=terminal_f/(w-g);pvt=tv/(1+w)**5;ev=pv+pvt
                for key,exact in dict(enterprise_value=ev,pv_explicit_fcff=pv,pv_terminal_value=pvt,
                                      terminal_revenue=terminal_r,terminal_fcff=terminal_f,terminal_value=tv,
                                      equity_value=ev-11,value_per_share=(ev-11)/4,terminal_contribution=pvt/ev).items():
                    self.assert_close(cell['metrics'][key],exact)
                reference_ev=F('77.577060352')
                for key,current,ref in (('enterprise_value',ev,reference_ev),
                                        ('equity_value',ev-11,reference_ev-11),
                                        ('value_per_share',(ev-11)/4,(reference_ev-11)/4)):
                    self.assert_close(cell['changes'][key]['absolute'],current-ref)
                    self.assert_close(cell['changes'][key]['fractional_change'],(current-ref)/ref)
        self.assertNotEqual(result['cells'][2][0]['metrics']['terminal_fcff'],result['cells'][2][1]['metrics']['terminal_fcff'])
        # The reference need not be on either axis.
        doc=document();doc.update(wacc_values=['0.20'],terminal_growth_values=['0.02'])
        out=execute(doc);self.assertEqual(out['reference_result'],execute()['reference_result'])
        self.assertNotEqual(out['cells'][0][0]['metrics'],out['reference_metrics'])

    def test_explicit_scenario_selection_validates_entire_source_and_isolates_selection(self):
        for label in ('Bear','Base','Bull'):
            doc=document(True,label);result=execute(doc)
            entry=next(x for x in doc['source']['scenario_set']['scenarios'] if x['label']==label)
            self.assertEqual(result['reference_result'],c.run_case(c.read_case(json.dumps(entry['case'])),ROOT))
            self.assertEqual(result['selection']['scenario_label'],label)
            self.assertEqual(result['selection']['information_cutoff'],entry['information_cutoff'])
        doc=document(scenario='Bear');doc['source'].pop('scenario_label')
        with self.assertRaisesRegex(s.SensitivityInputError,'source.scenario_label'):parse(doc)
        doc=document(scenario='Bear');doc['source']['scenario_set']['scenarios'][2]['case']['wacc']=None
        with patch.object(s,'_prepare_case_runner') as engine,self.assertRaisesRegex(s.SensitivityInputError,r'scenario_set.scenarios\[2\].case.wacc'):parse(doc)
        engine.assert_not_called()
        doc=document(scenario='Bear');before=execute(doc)
        doc['source']['scenario_set']['scenarios'][1]['case']['operating_margin']='0.9'
        with self.assertRaisesRegex(s.SensitivityInputError,'unknown field'):parse(doc)
        doc=document(scenario='Bear');doc['source']['scenario_set']['scenarios'][1]['case']['forecast_years'][0]['operating_margin']='0.9'
        after=execute(doc);self.assertEqual(before['reference_result'],after['reference_result']);self.assertEqual(before['cells'],after['cells'])

    def test_domains_mixed_invalid_and_all_invalid_fail_before_calculation_or_output(self):
        doc=document();result=execute(doc)
        self.assertEqual([[x['status'] for x in row] for row in result['cells']],
                         [['VALID','INVALID','INVALID'],['VALID','VALID','INVALID'],['VALID','VALID','VALID']])
        doc.update(wacc_values=['0.01','0.02'],terminal_growth_values=['0.02','0.03'])
        with patch.object(s,'_prepare_case_runner') as engine,self.assertRaisesRegex(s.SensitivityInputError,'all cells invalid'):parse(doc)
        engine.assert_not_called()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.json';path.write_text(json.dumps(doc));out=Path(tmp)/'out.json'
            with redirect_stderr(io.StringIO()):self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),2)
            self.assertFalse(out.exists())
        doc=document();doc['terminal_growth_values']=['-0.5','0'];self.assertEqual(execute(doc)['cells'][0][0]['status'],'VALID')

    def test_axis_rejection_paths_duplicates_order_types_and_size(self):
        for key in ('wacc_values','terminal_growth_values'):
            for bad in ([],['0.1']*12,['0.1','0.10'],['0.2','0.1'],[0.1],[1],[True],[None],['NaN'],['Infinity'],['1e999999999999999999999'],['9%'],['.09'],{},None):
                doc=document();doc[key]=bad
                with self.subTest(key=key,bad=bad),patch.object(s,'_prepare_case_runner') as engine,self.assertRaisesRegex(s.SensitivityInputError,'sensitivity.'+key):parse(doc)
                engine.assert_not_called()
        for key,bad in (('wacc_values',['0']),('wacc_values',['-0.1']),('terminal_growth_values',['-1'])):
            doc=document();doc[key]=bad
            with self.assertRaisesRegex(s.SensitivityInputError,key):parse(doc)
        doc=document();doc['wacc_values']=[str(D(i)/100) for i in range(1,12)];doc['terminal_growth_values']=['-0.5']
        self.assertEqual(len(parse(doc).wacc_values),11)

    def test_strict_structure_nested_types_dates_duplicate_keys_and_unknowns(self):
        edits=[(lambda d:d.update(extra=True),'sensitivity.extra'),
               (lambda d:d.update(schema_version='bad'),'schema_version'),
               (lambda d:d.update(sensitivity_name=' '),'sensitivity_name'),
               (lambda d:d['source'].update(kind='file'),'source.kind'),
               (lambda d:d['source'].update(case_file='x'),'source.case_file'),
               (lambda d:d['source'].update(analytical_date='2025-12-30'),'analytical_date'),
               (lambda d:d['source'].update(information_cutoff='2025-01-01'),'information_cutoff'),
               (lambda d:d['source'].update(information_cutoff=None),'information_cutoff'),
               (lambda d:d['source']['case']['forecast_years'][1].update(forecast_tax_rate=None),r'source.case.forecast_years\[1\].forecast_tax_rate')]
        for edit,message in edits:
            doc=document();edit(doc)
            with self.subTest(message=message),self.assertRaisesRegex(s.SensitivityInputError,message):parse(doc)
        for raw in ('null','[]','{','{}'):
            with self.assertRaises(s.SensitivityInputError):s.read_sensitivity(raw)
        raw=json.dumps(document())
        for changed,path in ((raw.replace('"wacc_values": ["0.04"','"wacc_values": [NaN',1),r'wacc_values\[0\]'),
                             (raw.replace('"wacc_values":','"wacc_values": [], "wacc_values":',1),'wacc_values'),
                             (raw.replace('"wacc": "0.25"','"wacc": "0.25", "wacc": "0.3"',1),'source.case.wacc')):
            with self.assertRaisesRegex(s.SensitivityInputError,path):s.read_sensitivity(changed)

    def test_zero_negative_reference_and_equity_signed_changes_no_clamping(self):
        doc=document(True)
        for y in doc['source']['case']['forecast_years']:
            for key in c.ANNUAL_RATES:y[key]='0'
        for key in c.TERMINAL_RATES:doc['source']['case']['terminal'][key]='0'
        zero=execute(doc)
        self.assertEqual(D(zero['reference_metrics']['enterprise_value']),0)
        for row in zero['cells']:
            for cell in row:
                if cell['status']=='VALID':
                    self.assertIsNone(cell['metrics']['terminal_contribution'])
                    self.assertIsNone(cell['changes']['enterprise_value']['fractional_change'])
                    self.assertIn('reference is zero',cell['changes']['enterprise_value']['note'])
        for component in doc['source']['case']['bridge']['components']:component['amount']='0'
        zero=execute(doc)
        self.assertIsNone(zero['cells'][2][0]['changes']['equity_value']['fractional_change'])
        self.assertIsNone(zero['cells'][2][0]['changes']['value_per_share']['fractional_change'])
        doc=document(True)
        for y in doc['source']['case']['forecast_years']:y['operating_margin']='-0.1'
        doc['source']['case']['terminal']['operating_margin']='-0.1'
        negative=execute(doc)
        self.assertLess(D(negative['reference_metrics']['enterprise_value']),0)
        self.assertLess(D(negative['reference_metrics']['equity_value']),0)
        cell=negative['cells'][2][0]
        with localcontext(Context(prec=50)):
            for key in ('enterprise_value','equity_value','value_per_share'):
                self.assertEqual(D(cell['changes'][key]['fractional_change']),D(cell['changes'][key]['absolute'])/D(negative['reference_metrics'][key]))
        doc=document()
        for y in doc['source']['case']['forecast_years']:y['operating_margin']='0'
        over=execute(doc)
        self.assertGreater(D(over['reference_metrics']['terminal_contribution']),1)
        doc=document();doc['source']['case']['terminal']['operating_margin']='0.02'
        signed=execute(doc)
        self.assertLess(D(signed['cells'][2][0]['metrics']['terminal_contribution']),0)

    def test_immutable_models_context_and_serialization(self):
        raw=json.dumps(document(True));request=s.read_sensitivity(raw);result=s.run_sensitivity(request,ROOT);before=deepcopy(result)
        with self.assertRaises(FrozenInstanceError):request.sensitivity_name='changed'
        with patch.object(s,'_prepare_case_runner') as engine,self.assertRaises(s.SensitivityInputError):s.run_sensitivity(replace(request,wacc_values=(D('.9'),)),ROOT)
        engine.assert_not_called()
        with localcontext() as ctx:
            ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;ctx.clear_flags();ctx.flags[Rounded]=True;snapshot=ctx.copy()
            self.assertEqual(s.read_sensitivity(raw),request)
            invalid=document();invalid['wacc_values']=['1e999999999999999999999']
            with self.assertRaises(s.SensitivityInputError):parse(invalid)
            again=s.run_sensitivity(request,ROOT)
            self.assertEqual(again,result);self.assertEqual(s.serialize_sensitivity(again),s.serialize_sensitivity(result))
            cli.render_summary(result)
            self.assertEqual((ctx.prec,ctx.rounding,ctx.flags,ctx.traps),(snapshot.prec,snapshot.rounding,snapshot.flags,snapshot.traps))
        self.assertEqual(result,before);self.assertEqual(request.submitted_json,raw)

    def test_summary_units_axes_invalid_legend_limits_and_rounding(self):
        result=execute(document(True));report=cli.render_summary(result)
        for text in ('Company: Synthetic fixture','USD millions','USD/share','25.00%','5.00%',
                     'WACC rows / g columns','INVALID*','terminal growth >= WACC','16.64426509',
                     '0.00007758','fiscal end using later-filed information','2026-01-31','not probability analysis',
                     result['selected_case']['analyst']['rationale']):self.assertIn(text,report)
        self.assertNotIn('value/share matrix',cli.render_summary(execute()))
        result['cells'][2][0]['metrics']['value_per_share']='-1.123456785'
        self.assertIn('-1.12345678',cli.render_summary(result))
        self.assertEqual(result['cells'][2][0]['metrics']['value_per_share'],'-1.123456785')
        doc=document(scenario='Bull');self.assertIn('Scenario: Bull',cli.render_summary(execute(doc)))

    def test_validation_only_no_calculation_history_or_result_writes(self):
        with patch.object(s,'_prepare_case_runner') as run,patch.object(c,'load_revenue_anchor') as loader, \
             patch.object(c,'forecast_five_years') as a,patch.object(c,'discount_to_enterprise_value') as b, \
             patch.object(c,'bridge_to_per_share') as bridge,patch.object(Path,'write_text',side_effect=AssertionError('no writes')):
            parse(document(scenario='Base'))
            with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(EXAMPLES/'synthetic-sensitivity-equity.json')]),0)
            for mock in (run,loader,a,b,bridge):mock.assert_not_called()

    def test_cli_json_summary_new_file_only_and_failure_atomicity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'request.json';path.write_text(json.dumps(document()));before=path.read_bytes()
            command=[sys.executable,str(SCRIPT),str(path)]
            default=subprocess.run(command,capture_output=True,text=True,cwd=tmp)
            self.assertEqual(default.returncode,0,default.stderr);self.assertEqual(list(Path(tmp).iterdir()),[path])
            run=subprocess.run(command+['--run'],capture_output=True,text=True,cwd=tmp)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(run.stdout,s.serialize_sensitivity(execute()))
            for fmt in ('json','summary'):
                out=Path(tmp)/('out.'+fmt)
                with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(path),'--run','--format',fmt,'--output',str(out)]),0)
                content=out.read_bytes()
                with patch.object(cli,'run_sensitivity') as engine,redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),2);engine.assert_not_called()
                self.assertEqual(out.read_bytes(),content)
            for out in (path,ROOT/'docs/forbidden-sensitivity.json'):
                with patch.object(cli,'run_sensitivity') as engine,redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),2);engine.assert_not_called()
            with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):cli.main([str(path),'--output',str(Path(tmp)/'no')])
            out=Path(tmp)/'failed.json'
            reference=c.run_case(parse(document()).case,ROOT)
            with patch.object(s,'_prepare_case_runner',return_value=Mock(side_effect=[reference,ValueError('stale anchor')])),redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),2)
            self.assertFalse(out.exists());self.assertEqual(path.read_bytes(),before)

    def test_temporary_three_company_both_scopes_scenario_selection_and_protection(self):
        packages=[ROOT/value['package'] for value in c.ANCHORS.values()]
        hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in packages}
        with tempfile.TemporaryDirectory() as tmp,patch.object(socket,'socket',side_effect=AssertionError('network forbidden')):
            for kind,revenue in (('meta-fy2025','200966000000'),('googl-fy2025','402836000000'),('aapl-fy2025','416161000000')):
                for equity in (False,True):
                    doc=document(equity,'Bull' if equity else None)
                    identity=c.ANCHORS[kind]['identity']
                    entries=doc['source']['scenario_set']['scenarios'] if equity else [doc['source']]
                    for entry in entries:
                        entry.update(analytical_date=identity['annual_end'],information_cutoff='2026-02-05')
                        case=entry['case'];case.update(anchor=dict(kind=kind,**identity),input_basis='MANUAL_INPUT',case_name='SYNTHETIC sensitivity integration on '+kind)
                        case['analyst']['rationale']='SYNTHETIC forward inputs and bridge only; actual retained revenue, not an analyst valuation.'
                        case['conventions']['forecast']='manual-fcff-v1'
                        if equity:
                            bridge=case['bridge'];bridge.update(input_basis='MANUAL_INPUT',convention_version='manual-equity-bridge-v1')
                            for component in bridge['components']:component.update(company_cik=identity['cik'],as_of=identity['annual_end'])
                            for observation in bridge['observations']:observation.update(company_cik=identity['cik'])
                            bridge['shares'].update(company_cik=identity['cik'],observation_date=identity['annual_end'])
                    path=Path(tmp)/(kind+str(equity)+'.json');path.write_text(json.dumps(doc));before=path.read_bytes();out=Path(tmp)/(path.stem+'-result.json')
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(cli.main([str(path)]),0)
                        self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),0)
                    result=json.loads(out.read_text());anchor=result['reference_result']['stage_b']['stage_a']['anchor']
                    self.assertEqual(anchor['revenue'],revenue);self.assertEqual(anchor['annual_end'],identity['annual_end'])
                    self.assertEqual('stage_c' in result['reference_result'],equity)
                    self.assertEqual(result['selection']['scenario_label'],'Bull' if equity else None)
                    self.assertEqual(path.read_bytes(),before)
            folder=Path(tmp)
        self.assertFalse(folder.exists())
        self.assertEqual(hashes,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in packages})


if __name__=='__main__':
    unittest.main()
