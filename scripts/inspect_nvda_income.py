"""Reproduce the fixed retained-only NVDA ledger; no network, writes or corpus."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst.nvda_income_inputs import build

if __name__=='__main__':
    ledger,_=build()
    expected=json.loads((Path(__file__).resolve().parents[1]/'docs/nvda-retained-income-ledger.json').read_text())
    if ledger!=expected:raise SystemExit('Committed NVDA ledger differs from retained replay')
    print(json.dumps({'periods':len(ledger['rows']),'slots':10,'populated':sum(f['selected'] is not None for row in ledger['rows'] for f in row['fields']),
        'receipt_exceptions':sum(bool(f['unresolved_requirements'][0].startswith('Missing retained')) for row in ledger['rows'] for f in row['fields']),
        'other_families':'unassessed','ledger_reproduction':'PASS'},sort_keys=True))
