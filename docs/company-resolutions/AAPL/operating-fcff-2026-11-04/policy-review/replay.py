"""Independent Apple policy workpaper; no consumer or prior-source mutation."""
import hashlib
import json
from datetime import date
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
from calculate_historical_fcff_from_filings import RetainedFiling
from valuation_platform.valuation.consumer import ANCHORS
from valuation_platform.analyst import cash_flow_inputs as cash

FOLDER = Path(__file__).resolve().parent
CORE = {'AccountsReceivableNetCurrent': 1, 'NontradeReceivablesCurrent': 1,
        'InventoryNet': 1, 'AccountsPayableCurrent': -1,
        'ContractWithCustomerLiabilityCurrent': -1}


def point(filing, concept, instant):
    result = []
    for ordinal, fact in enumerate(filing.root):
        if fact.tag.split('}')[-1] != concept or not fact.get('contextRef'):
            continue
        if cash._context(filing.contexts[fact.get('contextRef')]) != (320193, None, instant):
            continue
        unit = filing.units.get(fact.get('unitRef'))
        if unit is None or len(unit) != 1 or unit[0].text.split(':')[-1] != 'USD':
            continue
        result.append({'value_usd': fact.text, 'context_id': fact.get('contextRef'),
                       'instance_ordinal': ordinal, 'decimals': fact.get('decimals')})
    if not result:
        return None
    assert len({Fraction(r['value_usd']) for r in result}) == 1
    return {'concept': concept, 'instant': instant.isoformat(), 'observations': result,
            'value_usd': result[0]['value_usd'], 'sources': filing.references}


def main():
    rows = json.loads((ROOT / ANCHORS['aapl-fy2025']['package']).read_text())['aapl_history_review']['periods']
    diagnostic_path = ROOT / 'docs/company-resolutions/execution-2026-11-04/step-1-apple-operating.json'
    diagnostic = json.loads(diagnostic_path.read_text())['periods']
    periods = []
    for row, prior in zip(rows, diagnostic, strict=True):
        filing = RetainedFiling(ROOT, row, {})
        ending = filing.period.annual_end
        beginning = date(2020, 9, 26) if filing.year == 2021 else date.fromisoformat(rows[filing.year-2022]['identity']['annual_end'])
        snapshots = []
        for instant in (beginning, ending):
            items = [dict(point(filing, name, instant), coefficient=coefficient) for name, coefficient in CORE.items()]
            total = sum(Fraction(p['value_usd']) * p['coefficient'] for p in items)
            exclusions = {name: point(filing, name, instant) for name in ('OtherAssetsCurrent', 'OtherLiabilitiesCurrent', 'AccruedIncomeTaxesCurrent', 'FinanceLeaseLiabilityCurrent', 'OperatingLeaseLiabilityCurrent')}
            broad = total + Fraction(exclusions['OtherAssetsCurrent']['value_usd']) - Fraction(exclusions['OtherLiabilitiesCurrent']['value_usd']) + Fraction(exclusions['FinanceLeaseLiabilityCurrent']['value_usd']) + Fraction(exclusions['OperatingLeaseLiabilityCurrent']['value_usd'])
            snapshots.append({'instant': instant.isoformat(), 'core_nwc_usd': str(total),
                              'broad_current_nwc_both_lease_liabilities_excluded_usd': str(broad),
                              'items': items, 'excluded_or_diagnostic': exclusions})
        delta = Fraction(snapshots[1]['core_nwc_usd']) - Fraction(snapshots[0]['core_nwc_usd'])
        v = {k: Fraction(value) for k,value in prior['filing_operands_usd'].items()}
        fcff = v['ebit']*(1-v['tax_provision']/v['pretax_income']) + v['cash_statement_da'] - v['cash_ppe'] - delta
        broad_delta = Fraction(snapshots[1]['broad_current_nwc_both_lease_liabilities_excluded_usd']) - Fraction(snapshots[0]['broad_current_nwc_both_lease_liabilities_excluded_usd'])
        broad_fcff = v['ebit']*(1-v['tax_provision']/v['pretax_income']) + v['cash_statement_da'] - v['cash_ppe'] - broad_delta
        periods.append({'fiscal_year': filing.year, 'snapshots': snapshots,
                        'core_delta_nwc_usd': str(delta),
                        'standardized_core_trade_fcff_exact_usd': {'numerator': str(fcff.numerator), 'denominator': str(fcff.denominator)},
                        'standardized_core_trade_fcff_display_billions': str(round(Decimal(fcff.numerator)/Decimal(fcff.denominator)/Decimal(10**9), 2)),
                        'broad_delta_nwc_usd': str(broad_delta),
                        'standardized_broad_current_fcff_exact_usd': {'numerator': str(broad_fcff.numerator), 'denominator': str(broad_fcff.denominator)},
                        'standardized_broad_current_fcff_display_billions': str(round(Decimal(broad_fcff.numerator)/Decimal(broad_fcff.denominator)/Decimal(10**9), 2)),
                        'eligible_as_exact_historical_cash_flow': False,
                        'policy_not_numerical_fact': 'Core trade NWC intentionally excludes entire mixed Other buckets; change is a balance-sheet model, not an observed cash movement.'})
    out = {'purpose': 'Policy comparison only; root must adopt one specifically named methodology before consumer changes.',
           'source_diagnostic_sha256': hashlib.sha256(diagnostic_path.read_bytes()).hexdigest(), 'periods': periods}
    (FOLDER/'results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'years': len(periods), 'core_trade_only_billions': [p['standardized_core_trade_fcff_display_billions'] for p in periods]}))


if __name__ == '__main__':
    main()
