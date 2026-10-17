"""Narrow preservation projection for the authorized additive MSFT review."""
import ast
import json


def preservation_projection(path,body):
    if path=='docs/company-data-preparation/msft-analyst-input-package.json':
        value=json.loads(body)
        for key in ('fy2026_completeness_attempt','fy2026_operation_approval','fy2026_operations_view','fy2026_claim_assumption_approval','fy2026_claim_assumptions_view','fy2026_financing_approval','fy2026_analyst_checklist'):value.pop(key,None)
        return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    if path=='scripts/prepare_msft_analyst_package.py':
        tree=ast.parse(body)
        extensions={'attach_fy2026_attempt','fy2026_operations_record','review_fy2026_populations','apply_fy2026_operations','fy2026_claim_assumption_record','apply_fy2026_claim_assumptions','fy2026_financing_record','apply_fy2026_financing'}
        tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name not in extensions]
        tree.body=[n for n in tree.body if not isinstance(n,ast.Assign) or not any(isinstance(t,ast.Name) and t.id in ('FY2026_OPERATIONS_BASIS','FY2026_APPROVED_OPERATIONS','FY2026_CLAIMS_BASIS','FY2026_APPROVED_CLAIM_ASSUMPTIONS','FY2026_FINANCING_BASIS','FY2026_FINANCING_DECISION') for t in n.targets)]
        for node in tree.body:
            if isinstance(node,ast.FunctionDef) and node.name=='build':
                call=node.body[-1].value
                while isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id in ('attach_fy2026_attempt','apply_fy2026_operations','apply_fy2026_claim_assumptions','apply_fy2026_financing'):
                    assert len(call.args)==2 and not call.keywords
                    assert ast.dump(call.args[0])==ast.dump(ast.parse('filings[1]',mode='eval').body)
                    node.body[-1].value=call.args[1]
                    call=node.body[-1].value
        return ast.dump(tree).encode()
    return body
