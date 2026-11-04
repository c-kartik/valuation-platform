"""Source-bound Apple D&A population workpaper; never applies a balancing plug."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'src')]
from calculate_historical_fcff_from_filings import RetainedFiling
from reconcile_historical_fcff_adjustments import exact
from valuation_platform.review.operating_fcff import amount, serialized


def rounding_diagnostic(depreciation, amortization, combined):
    """Conservative closed precision envelopes, not estimates of true amounts."""
    values = [amount(point['value']) for point in (depreciation, amortization, combined)]
    errors = [Fraction(10) ** -int(point['precision']) / 2
              for point in (depreciation, amortization, combined)]
    delta = values[0] + values[1] - values[2]
    radius = sum(errors)
    return {'nominal_difference_usd': serialized(delta)['amount_usd'],
            'difference_lower_usd': serialized(delta - radius)['amount_usd'],
            'difference_upper_usd': serialized(delta + radius)['amount_usd'],
            'rounding_can_explain_difference': delta - radius <= 0 <= delta + radius,
            'envelope_method': 'Each reported decimals precision contributes half a displayed increment; closed bounds conservatively include rounding ties.'}


def guarded_addback(combined, proposed_extra, sourced_reconciliation=False,
                    investment_and_cash_population_reviewed=False):
    """A diagnostic difference cannot become an adopted add-back."""
    if amount(proposed_extra) and not (sourced_reconciliation and investment_and_cash_population_reviewed):
        raise ValueError('Additional add-back requires source reconciliation AND investment/cash population review')
    return amount(combined) + amount(proposed_extra)


def build():
    folder = ROOT / 'docs/company-resolutions/AAPL/implementation-2026-11-03'
    new_row = json.loads((folder / 'new-source-row.json').read_text())
    later = RetainedFiling(ROOT, new_row, {})
    original_rows = json.loads((ROOT / 'docs/company-data-preparation/aapl-analyst-input-package.json').read_text())['aapl_history_review']['periods']
    adopted = json.loads((ROOT / 'docs/company-resolutions/AAPL/operating-fcff-2026-11-04/adopted-history.json').read_text())
    annual, original_da = [], {}
    for row in original_rows:
        year = int(row['identity']['annual_end'][:4])
        filing = RetainedFiling(ROOT, row, {})
        da = exact(filing, row['identity'], 'DepreciationDepletionAndAmortization')
        ppe = exact(filing, row['identity'], 'PaymentsToAcquirePropertyPlantAndEquipment')
        active = next(p for p in adopted['periods'] if p['fiscal_year'] == year)
        assert amount(active['inputs']['da']) == amount(da['value'])
        assert amount(active['inputs']['cash_ppe']) == amount(ppe['value'])
        original_da[year] = da
        annual.append({'fiscal_year': year, 'reported_combined_da': da,
                       'reported_cash_ppe': ppe, 'adopted_da_usd': da['value'],
                       'additional_da_plug_usd': '0', 'adopted_fcff_usd': active['fcff']['amount_usd'],
                       'adopted_fcff_change_usd': '0'})
    comparative = []
    for year in (2024, 2025, 2026):
        identity = next((r['identity'] for r in original_rows if int(r['identity']['annual_end'][:4]) == year), new_row['identity'])
        points = {key: exact(later, identity, concept) for key, concept in {
            'combined_da': 'DepreciationDepletionAndAmortization',
            'ppe_depreciation': 'Depreciation',
            'intangible_amortization': 'AmortizationOfIntangibleAssets'}.items()}
        if year in original_da:
            assert amount(points['combined_da']['value']) == amount(original_da[year]['value'])
        comparative.append({'fiscal_year': year, 'target_identity': identity,
            'points': points, 'rounding': rounding_diagnostic(points['ppe_depreciation'], points['intangible_amortization'], points['combined_da']),
            'comparison_role': 'current five-year scope' if year != 2026 else 'later-year population diagnostic only; not added to scope'})
    root = ET.fromstring(later.primary.artifact.body)
    text = ' '.join(' '.join(root.itertext()).split())
    excerpts = []
    for label, marker, length in [
        ('depreciation_policy', 'Property, plant and equipment are stated at cost.', 220),
        ('depreciation_expense', 'Depreciation expense on property, plant and equipment was', 240),
        ('intangible_population', 'Amortizable intangible assets: Licensed intangible assets', 850),
        ('intangible_amortization', 'Amortization expense related to intangible assets was', 230),
        ('lease_cash_and_noncash', 'The Company made fixed cash payments related to operating leases', 540),
        ('finance_lease_asset_location', 'Finance leases Property, plant and equipment, net', 180),
        ('licensed_purchase_obligations', 'The Company’s unconditional purchase obligations primarily consist', 380),
    ]:
        assert text.count(marker) == 1, (label, text.count(marker))
        start = text.index(marker)
        excerpts.append({'label': label, 'source_url': later.primary.artifact.url,
                         'source_sha256': later.primary.artifact.sha256,
                         'locator': 'Unique normalized-text marker: ' + marker,
                         'text': text[start:start + length]})
    synthetic = next(p for p in comparative if p['fiscal_year'] == 2024)['rounding']['nominal_difference_usd']
    base = amount(next(p for p in annual if p['fiscal_year'] == 2024)['adopted_fcff_usd'])
    assert guarded_addback('11445000000', '0') == 11445000000
    return {'schema_version': 'apple-da-population-review-v1', 'date': '2026-11-04',
        'company_status': 'OPEN', 'policy_treatment_status': 'IMPLEMENTED_RETAIN_REPORTED_COMBINED_DA',
        'exact_expense_population_reconciliation_status': 'UNRESOLVED_NO_SOURCE_BOUND_BRIDGE',
        'source_replay_status': 'PASS', 'annual_adopted_inputs': annual,
        'later_comparative_points': comparative, 'source_excerpts': excerpts,
        'diagnostic_only': {'fiscal_year': 2024, 'unsupported_addback_usd': synthetic,
            'fcff_if_other_inputs_held_fixed_usd': serialized(base + amount(synthetic))['amount_usd'],
            'adopted': False, 'increment_applied_to_runtime_usd': '0',
            'is_valuation_or_forecast': False,
            'warning': 'Pure arithmetic sensitivity to the nominal rounded difference. No evidence that the additional amount is an appropriate EBIT add-back or that related cash investment is captured. Never carry it into perpetuity.'},
        'no_double_count_controls': {'additional_finance_lease_depreciation_usd': '0',
            'additional_intangible_amortization_usd': '0',
            'noncash_asset_additions_treated_as_cash_ppe_usd': '0',
            'lease_principal_deducted_as_extra_investment_usd': '0'},
        'validation': {'original_combined_da_points_rebound': 5,
            'original_cash_ppe_points_rebound': 5, 'later_comparative_primary_instance_points': 9,
            'original_and_later_da_compares_equal': 2,
            'five_year_fcff_changes': 0, 'synthetic_plugs_applied': 0},
        'closure_condition': 'A numerical, source-supported bridge between expense and cash-statement populations, with corresponding investment/cash treatment and independent review; accepting reported-combined convention does not prove that bridge.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    data = build()
    output = json.dumps(data, indent=2, sort_keys=True) + '\n'
    path = HERE / 'results.json'
    if args.write:
        path.write_text(output)
    elif path.read_text() != output:
        raise SystemExit('D&A workpaper replay differs')
    print(json.dumps(data['validation'], sort_keys=True))
