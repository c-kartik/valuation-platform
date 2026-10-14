"""Read-only local bundle/quality/field-review inspection; no acquisition or decisions."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import prepared_assembly as a
from valuation_platform.analyst import preparation_review as review, analyst_overrides as overrides

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ticker',help='Exact eligible ticker/alias, e.g. GOOG or GOOGL')
    parser.add_argument('--view',choices=('full','latest'),default='full')
    parser.add_argument('--section',choices=('all','bundle','quality','queue'),default='all')
    parser.add_argument('--prepared',type=Path,help='Existing separate assembled-history payload; otherwise replay retained ledgers')
    parser.add_argument('--store',type=Path,help='Existing audit store, read-only; never creates a decision')
    args=parser.parse_args(argv)
    if args.prepared:
        if not args.ticker: parser.error('--prepared requires --ticker')
        prepared=a.deserialize(args.prepared.read_text())
        if args.ticker not in prepared.aliases: parser.error('Ticker differs from prepared history')
    else:
        report,histories=a.build()
        if report!=json.loads((a.ROOT/a.REPORT).read_text()):raise SystemExit('Assembly summary differs')
        if not args.ticker:
            if args.store: parser.error('--store requires --ticker')
            print(a.canonical({k:report[k] for k in ('issuer_count','selected_periods','field_slots','review_count','review_codes')}))
            return
        prepared=a.for_ticker(histories,args.ticker)
    if args.store is not None and not args.store.is_dir(): parser.error('Existing store directory required')
    payload=review.inspection_payload(prepared,args.view,None if args.store is None else overrides.AuditStore(args.store))
    if args.section=='all':result=payload
    elif args.section=='quality':
        result=dict(ticker=prepared.ticker,scope='full_history',requested_view=args.view,summary=payload['quality_full_history'])
    else:result=payload[args.section]
    print(a.canonical(result))

if __name__=='__main__':main()
