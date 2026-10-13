"""Offline retained-only CFO replay; no acquisition or financial adjustments."""
import json
from valuation_platform.analyst import retained_cfo_preparation as cfo
from valuation_platform.analyst import nvda_income_inputs as shared


if __name__=='__main__':
    ledger,_=cfo.build()
    if ledger!=json.loads((shared.ROOT/'docs/retained-cfo-ledger.json').read_text()):raise SystemExit('Retained CFO ledger differs')
    print(json.dumps(dict(periods=ledger['selected_periods'],issuers=ledger['issuer_count'],outcomes=ledger['outcomes'],
        artifact_exceptions=len(ledger['artifact_exceptions']),summary=ledger['summary']),indent=2))
