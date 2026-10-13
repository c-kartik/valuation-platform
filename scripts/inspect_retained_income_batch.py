"""Replay the fixed eight-issuer ledger without retrieval or corpus execution."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst.retained_income_batch import build
if __name__=='__main__':
    ledger,_=build()
    expected=json.loads((Path(__file__).resolve().parents[1]/'docs/retained-income-batch-ledger.json').read_text())
    if ledger!=expected:raise SystemExit('Batch ledger differs from retained replay')
    print(json.dumps(dict(replay='PASS',periods=ledger['selected_periods'],slots=ledger['field_period_slots'],summary=ledger['summary']),sort_keys=True))
