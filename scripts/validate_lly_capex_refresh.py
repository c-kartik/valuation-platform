"""Replay the historical, unactivated LLY content review offline."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst.lly_capex_refresh_review import *

if __name__=='__main__':
    x=validate(json.loads((ROOT/RECORD).read_text()))
    print(json.dumps(dict(reviewed_artifacts=15,content_supported_entries=5,activated_entries=0,
                         blocked_entries=5,requests=0,coverage=x['coverage']),sort_keys=True))
