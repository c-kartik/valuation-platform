"""Offline proposed-profile reproduction, explicit source acquisition, diff and engine export."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from valuation_platform.preload.generate import generate,engine_request
from valuation_platform.preload.profile import read_json,exclusive_json,refresh_diff,validate_profile


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    gen=commands.add_parser('generate');gen.add_argument('output',type=Path);gen.add_argument('--dataset',type=Path);gen.add_argument('--policy',type=Path);gen.add_argument('--ticker',choices=['GOOG','GOOGL'],default='GOOGL')
    diff=commands.add_parser('diff');diff.add_argument('previous',type=Path);diff.add_argument('candidate',type=Path);diff.add_argument('output',type=Path);diff.add_argument('--previous-result',type=Path);diff.add_argument('--candidate-result',type=Path)
    export=commands.add_parser('export');export.add_argument('profile',type=Path);export.add_argument('destination',type=Path);export.add_argument('--scenario',choices=['Base','Bear','Bull'],default='Base');export.add_argument('--method',choices=['perpetual_growth','exit_multiple'],default='perpetual_growth');export.add_argument('--run',action='store_true')
    acq=commands.add_parser('acquire');acq.add_argument('url');acq.add_argument('destination',type=Path);acq.add_argument('--published-at');acq.add_argument('--observation-date')
    args=parser.parse_args(argv)
    try:
        if args.command=='generate':
            profile=generate(ROOT,dataset=args.dataset,policy_path=args.policy,ticker=args.ticker);exclusive_json(args.output,profile);print('Proposed profile '+profile['economic_hash']+'; no calculation or network access')
        elif args.command=='diff':
            if bool(args.previous_result)!=bool(args.candidate_result):raise ValueError('Provide both result files or neither')
            exclusive_json(args.output,refresh_diff(read_json(args.previous),read_json(args.candidate),read_json(args.previous_result) if args.previous_result else None,read_json(args.candidate_result) if args.candidate_result else None));print('Reviewable refresh diff; no adoption or anchor promotion')
        elif args.command=='export':
            profile=validate_profile(read_json(args.profile));doc=engine_request(profile,args.scenario,args.method)
            if args.destination.exists() or args.destination.resolve().is_relative_to(ROOT):raise ValueError('Choose a NEW directory outside repository')
            # Validate before creating output; no results on incomplete request.
            from valuation_platform.valuation.case_inputs import read_case,run_case
            case=read_case(json.dumps(doc));result=run_case(case,ROOT) if args.run else None
            args.destination.mkdir(parents=True,exist_ok=False);exclusive_json(args.destination/'request.json',doc)
            if result is not None:exclusive_json(args.destination/'result.json',result)
            exclusive_json(args.destination/'provenance.json',profile)
            print('Exported request'+(' and existing-engine result' if args.run else '; not calculated'))
        else:
            from valuation_platform.preload.acquire import acquire
            receipt=acquire(args.url,args.destination,published_at=args.published_at,observation_date=args.observation_date);print('Acquired immutable unreviewed source '+receipt['sha256'])
    except (ValueError,OSError,TypeError,LookupError) as exc:parser.exit(2,str(exc)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
