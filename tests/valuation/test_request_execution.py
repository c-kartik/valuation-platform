"""Request-local source reuse; synthetic economics, retained anchors, no cache."""
from dataclasses import replace
import ast
import subprocess
import json
from unittest import TestCase
from unittest.mock import patch
from valuation_platform.valuation import case_inputs as c, sensitivity_inputs as s, reverse_inputs as r
from tests.api.test_sensitivity import document as grid
from tests.api.test_reverse import document as reverse
from tests.valuation.test_case_inputs import ROOT, EXAMPLES


class RequestExecutionTests(TestCase):
    def test_each_grid_or_solve_validates_source_once_and_next_request_reloads(self):
        for kind in c.ANCHORS:
            for make,read,run in ((grid,s.read_sensitivity,s.run_sensitivity),(reverse,r.read_reverse,r.run_reverse)):
                with self.subTest(kind=kind,tool=run.__name__):
                    request=read(json.dumps(make(True,kind)))
                    name='load_meta_revenue_anchor' if kind=='meta-fy2025' else 'load_revenue_anchor'
                    with patch.object(c,name,wraps=getattr(c,name)) as loader:
                        first=run(request,ROOT);self.assertEqual(loader.call_count,1)
                        self.assertEqual(run(request,ROOT),first);self.assertEqual(loader.call_count,2)
                        loader.side_effect=ValueError('changed approval/source binding')
                        with self.assertRaisesRegex(ValueError,'changed approval/source binding'):run(request,ROOT)
                        self.assertEqual(loader.call_count,3)

    def test_bound_runner_revalidates_candidate_and_rejects_changed_anchor(self):
        case=c.load_case(EXAMPLES/'synthetic-base.json');before=case.submitted_json
        execute=c._prepare_case_runner(case,ROOT)
        self.assertEqual(execute(case),c.run_case(case,ROOT))
        with self.assertRaises(c.CaseInputError):execute(replace(case,anchor_kind='meta-fy2025'))
        changed=grid(False,'googl-fy2025')['source']['case']
        with self.assertRaisesRegex(c.CaseInputError,'identical historical anchor'):execute(c.read_case(json.dumps(changed)))
        # Independent candidate remains strictly validated and fully recalculated.
        changed=json.loads(before);changed['forecast_years'][0]['operating_margin']='-0.1'
        candidate=c.read_case(json.dumps(changed))
        self.assertEqual(execute(candidate),c.run_case(candidate,ROOT))
        self.assertEqual(case.submitted_json,before)

    def test_standalone_case_still_reloads_and_rejects_invalid_source(self):
        case=c.read_case(json.dumps(grid(False,'googl-fy2025')['source']['case']))
        with patch.object(c,'load_revenue_anchor',wraps=c.load_revenue_anchor) as loader:
            out=c.run_case(case,ROOT);self.assertEqual(c.run_case(case,ROOT),out)
            self.assertEqual(loader.call_count,2)
            loader.side_effect=ValueError('stale source')
            with self.assertRaisesRegex(ValueError,'stale source'):c.run_case(case,ROOT)

    def test_shared_execution_and_all_other_case_functions_preserve_reviewed_ast(self):
        path='src/valuation_platform/valuation/case_inputs.py'
        old=ast.parse(subprocess.check_output(['git','show','d4d1d7c:'+path],cwd=ROOT))
        current=ast.parse((ROOT/path).read_text())
        funcs=lambda tree:{x.name:x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
        before,after=funcs(old),funcs(current)
        for name,node in before.items():
            if name!='run_case':self.assertEqual(ast.dump(node),ast.dump(after[name]),name)
        old_run=before['run_case']
        start=next(i for i,x in enumerate(old_run.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='stage_a' for t in x.targets))
        self.assertEqual([ast.dump(x) for x in old_run.body[start:]],[ast.dump(x) for x in after['_run_case'].body[1:]])
