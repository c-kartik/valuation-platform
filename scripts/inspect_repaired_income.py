"""Offline fixed binding-repair integration replay; no acquisition."""
import json
from valuation_platform.analyst import repaired_income_preparation as repaired
from valuation_platform.analyst import nvda_income_inputs as shared


if __name__=='__main__':
    ledger,_=repaired.build()
    if ledger!=json.loads((shared.ROOT/'docs/repaired-income-ledger.json').read_text()):raise SystemExit('Repaired ledger differs')
    print(json.dumps(dict(slots=ledger['slots'],outcomes=ledger['outcomes'],exceptions=ledger['binding_repair_exceptions'],summary=ledger['summary']),indent=2))
