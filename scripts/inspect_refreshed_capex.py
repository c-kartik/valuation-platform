"""Offline five-entry preparation refresh replay; no legacy hash substitution."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import refreshed_capex as r

if __name__=='__main__':
    ledger,_=r.build()
    if ledger!=json.loads((r.review.ROOT/r.LEDGER).read_text()):raise SystemExit('Refresh ledger differs')
    print(json.dumps({k:ledger[k] for k in ('selected_periods','issuer_count','outcomes','refresh_version')},sort_keys=True))
