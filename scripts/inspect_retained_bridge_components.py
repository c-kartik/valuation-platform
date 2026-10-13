"""Offline exact-year-end component ledger replay; no network."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import retained_bridge_components as b
if __name__=='__main__':
    ledger,_,_=b.build()
    if ledger!=json.loads((b.parent.capex.shared.ROOT/b.LEDGER).read_text()):
        raise SystemExit('Retained bridge component ledger differs')
    print(json.dumps(dict(selected_periods=ledger['selected_periods'],issuer_count=ledger['issuer_count'],summary=ledger['summary']),sort_keys=True))
