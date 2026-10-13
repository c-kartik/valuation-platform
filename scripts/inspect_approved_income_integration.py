"""Offline approved-policy integration replay; never acquires evidence."""
import json
from valuation_platform.analyst import approved_income_integration as integration
from valuation_platform.analyst import nvda_income_inputs as shared


if __name__=='__main__':
    ledger,_=integration.build()
    if ledger!=json.loads((shared.ROOT/'docs/approved-income-integration-ledger.json').read_text()):
        raise SystemExit('Approved integration ledger differs; no automatic refresh')
    print(json.dumps(dict(slots=ledger['slots'],outcomes=ledger['outcomes'],metadata_exceptions=len(ledger['derivation_metadata_exceptions']),
        seed_identity_gaps=len(ledger['identity_backlog']),summary=ledger['summary']),indent=2))
