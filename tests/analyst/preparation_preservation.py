"""Reviewed mutable preparation code is not the immutable normalization freeze.

Keep exact source-byte assertions, but bind explicitly authorized additive code
to its reviewed milestone. Frozen financial artifacts/policies keep their old pins;
two explicitly reviewed mutable preparation-ledger transitions have separate pins.
Legacy behavior is separately compared with the historical implementation in
test_preparation_preservation; no financial expectation is regenerated.
"""
import subprocess

MODEL = 'src/valuation_platform/analyst/historical_inputs.py'
REVIEWED = {
    # Existing anchor-integration field-path metadata only; numerical validation
    # rules/formulas were preserved. Scenario work does not edit this source.
    'src/valuation_platform/valuation/assumptions.py': '1d2e918fe9efe912381193ff61738067275d86bf',
    MODEL: '61086107005f78592ed0dca05291d095b4ccff89',
    'src/valuation_platform/analyst/retained_components.py': '9b477defc6d2dba6e382ad8f27d26e8e6a575730',
    'src/valuation_platform/analyst/refreshed_capex.py': '61086107005f78592ed0dca05291d095b4ccff89',
    'src/valuation_platform/analyst/analyst_overrides.py': '61086107005f78592ed0dca05291d095b4ccff89',
    'src/valuation_platform/analyst/preparation_review.py': '61086107005f78592ed0dca05291d095b4ccff89',
    'src/valuation_platform/analyst/prepared_assembly.py': '61086107005f78592ed0dca05291d095b4ccff89',
    'src/valuation_platform/analyst/retained_reported_tax.py': '61086107005f78592ed0dca05291d095b4ccff89',
    'docs/retained-d-and-a-ledger.json': 'a10505f5cac930a97411f4f7019dd5e4637ac32c',
    'docs/retained-bridge-component-ledger.json': 'a0bafc2314938255ff7614f5c5737debabd726bd',
}


def assert_preserved(test, root, path, baseline):
    pin = REVIEWED.get(path, baseline)
    expected = subprocess.check_output(['git', 'show', pin + ':' + path], cwd=root)
    test.assertTrue((root / path).read_bytes() == expected, f'{path} differs from reviewed {pin}')
