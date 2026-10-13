"""Offline movement replay, no network, aggregation or financial acceptance."""
import json
from valuation_platform.analyst import retained_working_capital as movements
from valuation_platform.analyst import nvda_income_inputs as shared

if __name__ == '__main__':
    ledger, _ = movements.build()
    if ledger != json.loads((shared.ROOT/'docs/retained-working-capital-ledger.json').read_text()):
        raise SystemExit('Retained movement ledger differs')
    print(json.dumps({k:ledger[k] for k in ('selected_periods','issuer_count','period_outcomes','row_counts','summary')},indent=2))
