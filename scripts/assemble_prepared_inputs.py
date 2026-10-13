"""Replay isolated assembly/review summary; no acquisition or overrides."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import prepared_assembly as a
if __name__=='__main__':
    report,_=a.build()
    if report!=json.loads((a.ROOT/a.REPORT).read_text()):raise SystemExit('Assembly summary differs')
    print(json.dumps({k:report[k] for k in ('issuer_count','selected_periods','field_slots','review_count','review_codes')},sort_keys=True))
