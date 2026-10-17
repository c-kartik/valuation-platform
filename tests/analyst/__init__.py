"""Narrow preservation projection for the authorized additive MSFT review."""
import ast
import json


def preservation_projection(path,body):
    if path=='docs/company-data-preparation/msft-analyst-input-package.json':
        value=json.loads(body);value.pop('fy2026_completeness_attempt',None)
        return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    if path=='scripts/prepare_msft_analyst_package.py':
        tree=ast.parse(body)
        tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='attach_fy2026_attempt']
        for node in tree.body:
            if isinstance(node,ast.FunctionDef) and node.name=='build':
                call=node.body[-1].value
                if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='attach_fy2026_attempt':
                    assert len(call.args)==2 and not call.keywords
                    assert ast.dump(call.args[0])==ast.dump(ast.parse('filings[1]',mode='eval').body)
                    node.body[-1].value=call.args[1]
        return ast.dump(tree).encode()
    return body
