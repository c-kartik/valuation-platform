"""Bounded inverse workflow: exact certificate, forward arithmetic and protections."""

from contextlib import redirect_stdout, redirect_stderr
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
from unittest.mock import patch

from valuation_platform.valuation import case_inputs as c, reverse_inputs as r, sensitivity_inputs as sensitivity
from tests.valuation.test_case_inputs import ROOT, EXAMPLES
from tests.valuation.test_scenarios import document as scenarios

SCRIPT=ROOT/'scripts/run_analyst_reverse_dcf.py'
spec=importlib.util.spec_from_file_location('reverse_cli',SCRIPT)
cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)


def document(equity=False, label=None):
    doc=json.loads((EXAMPLES/('synthetic-reverse-equity.json' if equity else 'synthetic-reverse-ev.json')).read_text())
    if label is not None:
        doc['source']=dict(kind='scenario_set',scenario_set=scenarios(equity),scenario_label=label)
    return doc


def selected(doc):
    if doc['source']['kind']=='single_case':return doc['source']['case']
    return next(x['case'] for x in doc['source']['scenario_set']['scenarios'] if x['label']==doc['source']['scenario_label'])


def parse(doc):return r.read_reverse(json.dumps(doc))


def execute(doc=None,**kwargs):return r.run_reverse(parse(document() if doc is None else doc),ROOT,**kwargs)


def target_from_forward(doc,growth):
    case=deepcopy(selected(doc))
    for y in case['forecast_years']:y['revenue_growth']=growth
    output=c.run_case(c.read_case(json.dumps(case)),ROOT)
    doc['target']['amount']=output['stage_b']['enterprise_value'] if doc['target']['metric']=='ENTERPRISE_VALUE' else output['stage_c']['value_per_share']
    return output


def zero_case(doc):
    case=selected(doc)
    for y in case['forecast_years']:
        for key in c.ANNUAL_RATES:y[key]='0'
    for key in c.TERMINAL_RATES:case['terminal'][key]='0'
    return case


class ReverseTests(unittest.TestCase):
    def test_known_roots_independent_arithmetic_and_full_trace(self):
        for equity in (False,True):
            doc=document(equity);before=deepcopy(doc);out=execute(doc);sol=out['solution']
            self.assertEqual(out['status'],'SUCCESS');self.assertEqual(D(sol['constant_annual_growth']),D('0.1'))
            # Independent closed-form synthetic FCFF and bridge, no engine oracle.
            revenues=[F(100)*F(11,10)**i for i in range(1,6)]
            pv=sum(revenue*F(8,100)/F(5,4)**i for i,revenue in enumerate(revenues,1))
            terminal=revenues[-1]*F(105,100)*F(18,100)
            ev=pv+terminal/F(1,5)/F(5,4)**5
            self.assertEqual(ev,F('77.577060352'))
            forward=sol['forward_result'];self.assertEqual(F(forward['stage_b']['enterprise_value']),ev)
            for year,revenue in zip(forward['stage_b']['stage_a']['years'],revenues):
                self.assertEqual(F(year['revenue']),revenue);self.assertEqual(F(year['fcff']),revenue*F(8,100))
            if equity:
                self.assertEqual(F(forward['stage_c']['equity_value']),ev-11)
                self.assertEqual(F(forward['stage_c']['value_per_share']),(ev-11)/4)
            self.assertEqual(out['selected_case'],selected(doc));self.assertEqual(out['submitted_inputs'],doc)
            self.assertEqual(doc,before);self.assertLessEqual(D(out['final_bracket']['width']),D(r.DEFAULT_POLICY.growth_tolerance))
            self.assertEqual(D(sol['signed_residual']),0)
            self.assertEqual(out['monotonicity']['direction'],'INCREASING')

    def test_replacement_not_shift_and_all_other_inputs_remain_fixed(self):
        doc=document(True)
        for y,g in zip(selected(doc)['forecast_years'],['0','0.2','-0.1','0.4','0.3']):y['revenue_growth']=g
        out=execute(doc);forward=out['solution']['forward_result'];actual=deepcopy(forward['submitted_inputs'])
        self.assertEqual(out['original_growth_path'],['0','0.2','-0.1','0.4','0.3'])
        self.assertEqual([y['revenue_growth'] for y in actual['forecast_years']],['0.10']*5)
        for y,old in zip(actual['forecast_years'],selected(doc)['forecast_years']):y['revenue_growth']=old['revenue_growth']
        self.assertEqual(actual,selected(doc));self.assertEqual(forward['stage_c']['inputs'],out['reference_result']['stage_c']['inputs'])

    def test_decreasing_negative_equity_and_signed_target(self):
        doc=document(True);case=zero_case(doc)
        for y in case['forecast_years']:y['capex_percent_revenue']='0.08'
        case['terminal']['investment_percent_revenue']='0.18'
        case['wacc']='0.25';case['terminal_growth']='0.05'
        target_from_forward(doc,'0.07');out=execute(doc)
        self.assertEqual(out['status'],'SUCCESS');self.assertEqual(out['monotonicity']['direction'],'DECREASING')
        self.assertLess(D(out['solution']['achieved_metric']),0)
        self.assertLessEqual(abs(D(out['solution']['constant_annual_growth'])-D('0.07')),D('1e-12'))
        self.assertLessEqual(D(out['solution']['absolute_residual']),D(out['solution']['residual_tolerance']))

    def test_exact_endpoints_including_minus_one_and_zero_derivative_at_endpoint(self):
        for bound in ('0.00','0.20','-1'):
            doc=document();doc['growth_bounds']['lower']='-1' if bound=='-1' else '0.00'
            target_from_forward(doc,bound);out=execute(doc)
            self.assertEqual(out['status'],'SUCCESS');self.assertTrue(out['solution']['exact_endpoint'])
            self.assertEqual(D(out['solution']['constant_annual_growth']),D(bound));self.assertEqual(out['iterations'],0)
            self.assertEqual(D(out['final_bracket']['width']),0)
        doc=document();case=zero_case(doc);case['terminal']['operating_margin']='0.1'
        doc['growth_bounds']['lower']='-1';target_from_forward(doc,'-1');out=execute(doc)
        self.assertEqual(out['status'],'SUCCESS');self.assertEqual(out['monotonicity']['direction'],'INCREASING')
        bounds=out['monotonicity']['derivative_enclosure'];self.assertEqual(int(bounds[0]['numerator']),0)

    def test_unreachable_never_returns_nearest_bound(self):
        for amount in ('100000','-100000'):
            doc=document();doc['target']['amount']=amount;out=execute(doc)
            self.assertEqual(out['status'],'UNREACHABLE_TARGET');self.assertIsNone(out['solution'])
            self.assertIsNotNone(out['final_bracket']);self.assertEqual(out['iterations'],0)

    def test_flat_response_is_not_a_unique_solution_even_if_target_matches(self):
        for amount in ('0','10'):
            doc=document();zero_case(doc);doc['target']['amount']=amount;out=execute(doc)
            self.assertEqual(out['status'],'FLAT_RESPONSE');self.assertIsNone(out['solution'])
            self.assertEqual(out['evaluations'],1)

    def test_exact_certificate_rejects_nonmonotonic_interval_despite_endpoint_signs(self):
        doc=document();case=zero_case(doc)
        # V(x)=100*x - 40*x²: derivative changes sign at x=1.25.
        case['wacc']='0.25';case['terminal_growth']='0.05'
        case['forecast_years'][0]['d_and_a_percent_revenue']='1.25'
        case['forecast_years'][1]['capex_percent_revenue']='0.625'
        doc['growth_bounds']=dict(lower='0',upper='1');doc['target']['amount']='55'
        out=execute(doc)
        self.assertEqual(out['status'],'UNIQUENESS_NOT_CERTIFIED');self.assertIsNone(out['solution'])
        self.assertIn('multiple roots are not proven',out['reason'])
        # Endpoints: 60 >55 >40; crossing alone does not prove uniqueness.
        cert=out['monotonicity'];lo,hi=cert['derivative_enclosure']
        self.assertLess(F(int(lo['numerator']),int(lo['denominator'])),0)
        self.assertGreater(F(int(hi['numerator']),int(hi['denominator'])),0)

    def test_conservative_enclosure_failure_does_not_assert_multiple_roots(self):
        doc=document();case=zero_case(doc)
        # A positive quadratic derivative can still have a mixed Bernstein hull.
        case['wacc']='0.25';case['terminal_growth']='0.05'
        # V(x)=3*x^3-9*x²+9.03*x,
        # derivative 9*(x-1)^2+0.03. All rates terminate exactly.
        case['forecast_years'][0]['d_and_a_percent_revenue']='0.112875'
        case['forecast_years'][1]['capex_percent_revenue']='0.140625'
        case['forecast_years'][2]['d_and_a_percent_revenue']='0.05859375'
        doc['growth_bounds']=dict(lower='-1',upper='1');doc['target']['amount']='3.03';out=execute(doc)
        self.assertEqual(out['status'],'UNIQUENESS_NOT_CERTIFIED');self.assertIsNone(out['solution'])
        self.assertIn('unsupported',out['reason']);self.assertNotIn('multiple solutions proven',out['reason'])

    def test_exact_rational_certificate_matches_shared_synthetic_coefficients(self):
        out=execute();coefficients=out['monotonicity']['polynomial_coefficients_ascending']
        actual=[F(int(x['numerator']),int(x['denominator'])) for x in coefficients]
        expected=[F(0)]+[F(8)/F(5,4)**i for i in range(1,6)]
        expected[5]+=F('18.9')/F('0.20')/F(5,4)**5
        self.assertEqual(actual,expected)
        for item in out['monotonicity']['derivative_bernstein_coefficients']:
            self.assertGreaterEqual(F(int(item['numerator']),int(item['denominator'])),0)

    def test_iteration_limit_and_fresh_verification_failure_expose_no_solution(self):
        doc=document();target_from_forward(doc,'0.073')
        out=execute(doc,policy=r.SolverPolicy(max_iterations=1))
        self.assertEqual(out['status'],'ITERATION_LIMIT');self.assertIsNone(out['solution'])
        self.assertEqual(out['iterations'],1)
        real=r.run_case;calls=[]
        def changed(case,root):
            result=real(case,root);calls.append(result)
            # Synthetic exact-midpoint path has seven evaluations, the seventh
            # is an independent fresh verification and must not reuse the first.
            if len(calls)==7:result['stage_b']['enterprise_value']='999'
            return result
        with patch.object(r,'run_case',side_effect=changed):out=execute()
        self.assertEqual(len(calls),7);self.assertEqual(out['status'],'NUMERICAL_VERIFICATION_FAILED');self.assertIsNone(out['solution'])

    def test_both_bracket_and_scale_aware_residual_required(self):
        doc=document();target_from_forward(doc,'0.073456789123')
        out=execute(doc);self.assertEqual(out['status'],'SUCCESS')
        sol=out['solution'];self.assertLessEqual(D(out['final_bracket']['width']),D('1e-12'))
        with localcontext(Context(prec=80)):
            expected=D('1e-8')+D('1e-12')*max(abs(D(doc['target']['amount'])),abs(D(sol['achieved_metric'])))
            self.assertEqual(D(sol['residual_tolerance']),expected)
        self.assertLessEqual(D(sol['absolute_residual']),D(sol['residual_tolerance']))
        # Tight residual policy may require more work after the bracket is small.
        strict=r.SolverPolicy(ev_absolute_tolerance='1e-40',relative_tolerance='1e-40',max_iterations=256)
        tighter=execute(doc,policy=strict);self.assertEqual(tighter['status'],'SUCCESS')
        self.assertGreater(tighter['iterations'],out['iterations'])

    def test_technical_policy_and_exact_certificate_resource_failures(self):
        with localcontext() as ctx:
            ctx.prec=3;ctx.traps[Inexact]=True;ctx.clear_flags();snapshot=ctx.copy()
            for kwargs in (dict(max_iterations=0),dict(max_iterations=257),dict(max_iterations=True),
                           dict(growth_tolerance='NaN'),dict(relative_tolerance='1e999999999999999999999'),
                           dict(exact_component_precision=10),dict(exact_component_precision=512.0),
                           dict(certificate_decimal_extent=4096.0),dict(relative_tolerance='0')):
                with self.assertRaises(ValueError):r.SolverPolicy(**kwargs)
            self.assertEqual((ctx.prec,ctx.flags,ctx.traps),(snapshot.prec,snapshot.flags,snapshot.traps))
        for value in ('1e-4097','0.'+'1'*600):
            doc=document();selected(doc)['forecast_years'][0]['d_and_a_percent_revenue']=value
            out=execute(doc)
            self.assertEqual(out['status'],'UNIQUENESS_NOT_CERTIFIED');self.assertIsNone(out['solution'])
            self.assertIn('technical limit' if value.startswith('1e') else 'precision cap',out['reason'])

    def test_field_qualified_structure_types_bounds_units_and_dates(self):
        edits=[(lambda d:d.update(extra=1),'reverse.extra'),
               (lambda d:d.update(schema_version='bad'),'schema_version'),
               (lambda d:d['target'].update(metric='PRICE'),'target.metric'),
               (lambda d:d['target'].update(unit='USD billions'),'target.unit'),
               (lambda d:d['target'].update(amount=10),'target.amount'),
               (lambda d:d['target'].update(amount=None),'target.amount'),
               (lambda d:d['target'].update(date='2026-01-01'),'target.date'),
               (lambda d:d['growth_bounds'].update(lower='-1.001'),'growth_bounds.lower'),
               (lambda d:d['growth_bounds'].update(lower='0.2'),'strictly below'),
               (lambda d:d['growth_bounds'].update(lower='0.3'),'strictly below'),
               (lambda d:d['growth_bounds'].update(upper='NaN'),'growth_bounds.upper'),
               (lambda d:d['growth_bounds'].update(upper=True),'growth_bounds.upper'),
               (lambda d:d['source'].update(information_cutoff='2025-01-01'),'information_cutoff'),
               (lambda d:d['source'].update(analytical_date='2025-12-30'),'analytical_date'),
               (lambda d:d['source'].update(case_file='x'),'case_file')]
        for edit,pattern in edits:
            doc=document();edit(doc)
            with self.subTest(pattern=pattern),patch.object(r,'run_case') as run,self.assertRaisesRegex(r.ReverseInputError,pattern):parse(doc)
            run.assert_not_called()
        doc=document();doc['target'].update(metric='VALUE_PER_SHARE',unit='USD/share')
        with self.assertRaisesRegex(r.ReverseInputError,'requires a complete equity'):parse(doc)
        doc=document(True);selected(doc)['bridge']['unresolved_requirements']=['Awards pending']
        with self.assertRaisesRegex(r.ReverseInputError,'bridge.unresolved_requirements'):parse(doc)
        for raw in ('{}','null','[]','{'):
            with self.assertRaises(r.ReverseInputError):r.read_reverse(raw)

    def test_strict_duplicate_keys_nonfinite_and_numeric_strings(self):
        raw=json.dumps(document())
        for modified,pattern in [(raw.replace('"amount": "77.577060352"','"amount": "1", "amount": "2"'),'target.amount'),
                                 (raw.replace('"lower": "0.00"','"lower": NaN'),'growth_bounds.lower'),
                                 (raw.replace('"upper": "0.20"','"upper": 0.20'),'growth_bounds.upper')]:
            with self.assertRaisesRegex(r.ReverseInputError,pattern):r.read_reverse(modified)

    def test_explicit_scenario_selection_validates_every_case(self):
        for label in ('Bear','Base','Bull'):
            doc=document(True,label);target_from_forward(doc,'0.1');out=execute(doc)
            self.assertEqual(out['status'],'SUCCESS');self.assertEqual(out['selection']['scenario_label'],label)
            self.assertEqual(out['selected_case'],selected(doc))
        doc=document(label='Base');doc['source'].pop('scenario_label')
        with self.assertRaisesRegex(r.ReverseInputError,'scenario_label'):parse(doc)
        doc=document(label='Base');doc['source']['scenario_set']['scenarios'][2]['case']['wacc']=None
        with self.assertRaisesRegex(r.ReverseInputError,r'scenario_set.scenarios\[2\].case.wacc'):parse(doc)

    def test_input_context_immutability_and_deterministic_output(self):
        raw=json.dumps(document(True));request=r.read_reverse(raw);result=r.run_reverse(request,ROOT);before=deepcopy(result)
        with self.assertRaises(FrozenInstanceError):request.target_amount=D(0)
        with patch.object(r,'run_case') as run,self.assertRaises(r.ReverseInputError):r.run_reverse(replace(request,lower_growth=D('-0.9')),ROOT)
        run.assert_not_called()
        with localcontext() as ctx:
            ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;ctx.clear_flags();ctx.flags[Rounded]=True;snapshot=ctx.copy()
            self.assertEqual(r.read_reverse(raw),request)
            bad=document();bad['target']['amount']='1e999999999999999999999'
            with self.assertRaises(r.ReverseInputError):parse(bad)
            again=r.run_reverse(request,ROOT);self.assertEqual(again,result)
            self.assertEqual(r.serialize_reverse(again),r.serialize_reverse(result));cli.render_summary(result)
            self.assertEqual((ctx.prec,ctx.rounding,ctx.flags,ctx.traps),(snapshot.prec,snapshot.rounding,snapshot.flags,snapshot.traps))
        self.assertEqual(result,before);self.assertEqual(request.submitted_json,raw)

    def test_validation_calculation_free_and_no_writes(self):
        with patch.object(r,'run_case') as run,patch.object(r,'_certificate') as certify,patch.object(c,'load_revenue_anchor') as load,patch.object(Path,'write_text',side_effect=AssertionError('no writes')):
            parse(document(label='Base'))
            with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(EXAMPLES/'synthetic-reverse-ev.json')]),0)
            for mock in (run,certify,load):mock.assert_not_called()

    def test_cli_exit_status_output_protections_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'request.json';path.write_text(json.dumps(document(True)));before=path.read_bytes()
            command=[sys.executable,str(SCRIPT),str(path)]
            valid=subprocess.run(command,capture_output=True,text=True,cwd=tmp)
            self.assertEqual(valid.returncode,0,valid.stderr);self.assertEqual(list(Path(tmp).iterdir()),[path])
            run=subprocess.run(command+['--run'],capture_output=True,text=True,cwd=tmp)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(run.stdout,r.serialize_reverse(execute(document(True))))
            summary=cli.render_summary(json.loads(run.stdout))
            for text in ('10.00000000%','16.64426509 USD/share','Status: SUCCESS','USD millions','Fixed shares: 4','2026-01-31','Conditional implied constant growth','INCREASING','Original annual growth path','extra-unknown'):self.assertIn(text,summary)
            for fmt in ('json','summary'):
                out=Path(tmp)/('result.'+fmt)
                with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(path),'--run','--format',fmt,'--output',str(out)]),0)
                content=out.read_bytes()
                with patch.object(cli,'run_reverse') as engine,redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),2);engine.assert_not_called()
                self.assertEqual(out.read_bytes(),content)
            for bad in (path,ROOT/'docs/forbidden-reverse.json'):
                with patch.object(cli,'run_reverse') as engine,redirect_stderr(io.StringIO()):
                    self.assertEqual(cli.main([str(path),'--run','--output',str(bad)]),2);engine.assert_not_called()
            with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):cli.main([str(path),'--output',str(Path(tmp)/'no')])
            self.assertEqual(path.read_bytes(),before)
            doc=document();doc['target']['amount']='9999';path.write_text(json.dumps(doc));out=Path(tmp)/'unsolved.json'
            with redirect_stdout(io.StringIO()):self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),3)
            failure=json.loads(out.read_text());self.assertEqual(failure['status'],'UNREACHABLE_TARGET');self.assertIsNone(failure['solution'])
            self.assertIn('No solved growth',cli.render_summary(failure))
            path.write_text('{}');out=Path(tmp)/'invalid.json'
            with redirect_stderr(io.StringIO()):self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),2)
            self.assertFalse(out.exists())

    def test_existing_case_scenario_sensitivity_interfaces_and_json_bytes_unchanged(self):
        for path in ('case_inputs.py','scenario_inputs.py','sensitivity_inputs.py','forecast.py','discounting.py','bridge.py','assumptions.py','consumer.py'):
            name='src/valuation_platform/valuation/'+path
            self.assertEqual((ROOT/name).read_bytes(),subprocess.check_output(['git','show','a571965:'+name],cwd=ROOT))
        for script,example in (('run_analyst_case.py','synthetic-equity.json'),('run_analyst_scenarios.py','synthetic-scenarios-equity.json'),('run_analyst_sensitivity.py','synthetic-sensitivity-equity.json')):
            name='scripts/'+script;source=subprocess.check_output(['git','show','a571965:'+name],cwd=ROOT)
            old={'__file__':str(ROOT/name),'__name__':'legacy'};exec(compile(source,'legacy','exec'),old)
            spec=importlib.util.spec_from_file_location('current_'+script,ROOT/name);current=importlib.util.module_from_spec(spec);spec.loader.exec_module(current)
            a,b=io.StringIO(),io.StringIO()
            with redirect_stdout(a):self.assertEqual(old['main']([str(EXAMPLES/example),'--run']),0)
            with redirect_stdout(b):self.assertEqual(current.main([str(EXAMPLES/example),'--run']),0)
            self.assertEqual(a.getvalue(),b.getvalue())

    def test_three_retained_anchors_temporary_synthetic_targets_both_scopes(self):
        packages=[ROOT/x['package'] for x in c.ANCHORS.values()];hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in packages}
        with tempfile.TemporaryDirectory() as tmp,patch.object(socket,'socket',side_effect=AssertionError('no network')):
            for kind,anchor in c.ANCHORS.items():
                for equity in (False,True):
                    doc=document(equity,'Base' if equity else None);identity=anchor['identity']
                    entries=doc['source']['scenario_set']['scenarios'] if equity else [doc['source']]
                    for entry in entries:
                        entry.update(analytical_date=identity['annual_end'],information_cutoff='2026-02-05');case=entry['case']
                        case.update(anchor=dict(kind=kind,**identity),input_basis='MANUAL_INPUT',case_name='SYNTHETIC reverse integration on retained '+kind)
                        case['analyst']['rationale']='SYNTHETIC operating/bridge assumptions and forward-generated target; engineering only, not an analyst reverse valuation.'
                        case['conventions']['forecast']='manual-fcff-v1'
                        if equity:
                            bridge=case['bridge'];bridge.update(input_basis='MANUAL_INPUT',convention_version='manual-equity-bridge-v1')
                            for x in bridge['components']:x.update(company_cik=identity['cik'],as_of=identity['annual_end'])
                            for x in bridge['observations']:x['company_cik']=identity['cik']
                            bridge['shares'].update(company_cik=identity['cik'],observation_date=identity['annual_end'])
                    doc['target']['date']=identity['annual_end'];expected=target_from_forward(doc,'0.07')
                    path=Path(tmp)/(kind+str(equity)+'.json');path.write_text(json.dumps(doc));before=path.read_bytes();out=Path(tmp)/(path.stem+'-result.json')
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(cli.main([str(path)]),0);self.assertEqual(cli.main([str(path),'--run','--output',str(out)]),0)
                    result=json.loads(out.read_text());self.assertEqual(result['status'],'SUCCESS')
                    self.assertEqual(result['reference_result']['stage_b']['stage_a']['anchor'],expected['stage_b']['stage_a']['anchor'])
                    self.assertLessEqual(abs(D(result['solution']['constant_annual_growth'])-D('0.07')),D('1e-12'))
                    self.assertEqual(path.read_bytes(),before)
            folder=Path(tmp)
        self.assertFalse(folder.exists());self.assertEqual(hashes,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in packages})


if __name__=='__main__':unittest.main()
