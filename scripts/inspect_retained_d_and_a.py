"""Replay the retained D&A overlays; never acquire evidence or alter parents."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import retained_d_and_a as d
if __name__=='__main__':
    ledger,_,_=d.build()
    if ledger!=json.loads((d.capex.shared.ROOT/d.LEDGER).read_text()):raise SystemExit('D&A ledger differs')
    print(json.dumps({k:ledger[k] for k in ('outcomes','selected_periods','issuer_count','support_periods','support_observations')},sort_keys=True))
