"""Replay only the fixed Capex evidence repair, offline by default."""
import json
from valuation_platform.analyst import capex_evidence_repair as r, nvda_income_inputs as shared
if __name__=='__main__':
    ledger,_=r.build()
    if ledger!=json.loads((shared.ROOT/'docs/repaired-capex-ledger.json').read_text()):raise SystemExit('Repaired Capex ledger differs')
    print(json.dumps({k:ledger[k] for k in ('selected_periods','issuer_count','outcomes','curated_versions','binding_repair')},indent=2))
