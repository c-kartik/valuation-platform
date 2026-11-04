"""Compare actual reader output with the separately recomputed audit oracle."""
import json
from pathlib import Path

from valuation_platform.review.pilot_cashflows import read_cashflows

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
audit = json.loads((HERE/'results.json').read_text())
baseline = json.loads((ROOT/'docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json').read_text())
checks = []
for ticker in ('AAPL', 'META', 'GOOGL'):
    data = read_cashflows(ROOT, ticker)
    assert {k:v for k,v in data.items() if k != 'readiness'} == baseline['companies'][ticker]
    r = data['readiness']
    for p in r['periods']:
        expected = {a['metric']:a['classification'] for a in audit['availability_30_cells']
                    if a['ticker'] == ticker and a['year'] == p['fiscal_year']}
        ff = 'UNAVAILABLE_REQUIRED_INPUT' if expected['FCFF']=='MISSING_REQUIRED_INPUT' else expected['FCFF']
        assert p['fcff_historical_calculation'] == ff
        assert p['fcfe_historical_calculation'] == expected['FCFE']
        assert p['fcff_forecast_calibration'] == 'NOT_CLEARED_BASIS_BRIDGE_REQUIRED'
    assert r['counts']['parent_common_fcfe_available'] == 0
    assert r['prior_parent_common_review_passed'] is False
    assert r['history_gap_disables_manual_forecast'] is False
    assert r['financial_review_status'] == 'OPEN'
    checks.append({'ticker':ticker,'counts':r['counts'],'original_record_unchanged':True,
                   'classification_matches_independent_oracle':True,
                   'manual_forecast_not_disabled_by_history_gap':True})
result = {'verdict':'PASS_ADDITIVE_CONSUMER_CLASSIFICATION', 'companies':checks,
          'financial_completion':'OPEN', 'parent_common_review_passed':False}
(HERE/'consumer-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2))
