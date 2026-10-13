"""Offline claims/shares ledger replay; no network or financial arithmetic."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import retained_claims_shares as c
if __name__=='__main__':
    ledger,_,_,prior=c.build()
    root=c.bridge.parent.capex.shared.ROOT
    if ledger!=json.loads((root/c.LEDGER).read_text()) or prior!=json.loads((root/c.bridge.LEDGER).read_text()):
        raise SystemExit('Claim/share or prior bridge ledger differs')
    print(json.dumps(dict(summary=ledger['summary'],share_limits=ledger['share_limits']),sort_keys=True))
