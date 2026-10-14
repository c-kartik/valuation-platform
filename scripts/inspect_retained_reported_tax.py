"""Offline exact annual reported-tax ledger replay; no network or writes."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import retained_reported_tax as tax, retained_cfo_preparation as cfo

if __name__=='__main__':
    _,histories=cfo.build()
    ledger,_=tax.build(histories)
    if ledger!=json.loads((tax.metadata.shared.ROOT/tax.LEDGER).read_text()):
        raise SystemExit('Retained reported-tax ledger differs from exact policy/source replay')
    print(json.dumps(dict(selected_periods=ledger['selected_periods'],issuers=ledger['issuers'],summary=ledger['summary']),sort_keys=True))
