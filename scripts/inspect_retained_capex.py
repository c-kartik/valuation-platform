"""Offline existing-policy Capex replay. No acquisition or new scope approval."""
import json
from valuation_platform.analyst import retained_capex as c, nvda_income_inputs as shared

if __name__=='__main__':
    ledger,_=c.build()
    if ledger!=json.loads((shared.ROOT/'docs/retained-capex-ledger.json').read_text()):raise SystemExit('Retained Capex ledger differs')
    print(json.dumps({k:ledger[k] for k in ('selected_periods','issuer_count','outcomes','curated_versions','summary')},indent=2))
