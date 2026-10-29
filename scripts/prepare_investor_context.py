"""Explicit bounded refresh into a NEW outside/review snapshot directory; no approvals."""
import argparse
from datetime import datetime,timezone
import hashlib,json,os,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.sec.client import SECClient
from valuation_platform.review.prepare import COMPANIES,prepare_context

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('destination',type=Path);args=parser.parse_args()
    if args.destination.exists():parser.error('Choose a new directory; existing snapshots are never overwritten')
    client=SECClient(os.environ.get('SEC_USER_AGENT',''));args.destination.mkdir(parents=True)
    for ticker,cik in COMPANIES.items():
        payloads=[];sources=[]
        for url in (f'https://data.sec.gov/submissions/CIK{cik:010d}.json',f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'):
            raw=client.get_bytes(url);payloads.append(json.loads(raw));sources.append({'url':url,'checked_at':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)});time.sleep(.25)
        doc=prepare_context(ticker,*payloads,sources)
        (args.destination/(ticker.lower()+'.json')).write_text(json.dumps(doc,sort_keys=True,indent=2)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
