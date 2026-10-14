"""Read-only, separate reported-population preparation/review; no valuation."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from valuation_platform.analyst import preparation_delivery as d, prepared_assembly as a
from valuation_platform.analyst import analyst_overrides as o


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ticker');p.add_argument('--view',choices=('full','latest'),default='full')
    p.add_argument('--prepared',type=Path);p.add_argument('--store',type=Path)
    p.add_argument('--replay',action='store_true')
    args=p.parse_args()
    if args.prepared:
        prepared=d.deserialize(args.prepared.read_text())
        if args.ticker not in prepared.aliases:p.error('Exact ticker required with prepared payload')
    else:
        ledger,histories,summary=d.build()
        if args.replay:
            for path,result in ((d.LEDGER,ledger),(d.SUMMARY,summary)):
                if json.loads((a.ROOT/path).read_text())!=result:raise SystemExit('Committed delivery differs: '+path)
        if not args.ticker:
            print(a.canonical(summary));return
        prepared=a.for_ticker(histories,args.ticker)
    if args.store and not args.store.is_dir():p.error('Existing audit store required')
    print(a.canonical(d.inspection_payload(prepared,args.view,None if not args.store else o.AuditStore(args.store))))


if __name__=='__main__':main()
