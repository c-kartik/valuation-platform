"""Replay the fixed retained-only sweep; never acquires evidence."""
import json
from valuation_platform.analyst import retained_income_sweep as sweep
from valuation_platform.analyst import nvda_income_inputs as shared


if __name__=='__main__':
    ledger,_=sweep.build()
    expected=json.loads((shared.ROOT/'docs/retained-income-sweep-ledger.json').read_text())
    if ledger!=expected:raise SystemExit('Retained sweep ledger differs; no silent refresh')
    print(json.dumps(dict(issuers=ledger['issuer_count'],periods=ledger['selected_periods'],slots=ledger['slots'],
        outcomes=ledger['outcomes'],artifact_backlog=len(ledger['acquisition_backlog']),
        identity_backlog=len(ledger['identity_backlog']),summary=ledger['summary']),indent=2))
