"""Offline, reproducible verification output for the registered preload universe.

Does not retain volatile generation times, alter sources, or create approvals.
Full dated profiles/requests remain available through prepare_preload.py export.
"""
import argparse
import csv
from io import StringIO
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from valuation_platform.preload.generate import generate, engine_request
from valuation_platform.preload.issuers import ISSUERS
from valuation_platform.valuation.case_inputs import read_case, run_case

JSON_PATH='docs/company-data-preparation/registered-preload-verification.json'
CSV_PATH='docs/company-data-preparation/registered-preload-forecasts.csv'


def build(root=ROOT):
    companies=[]
    for ticker in ISSUERS:
        profile=generate(root,ticker=ticker);economic=profile['economic']
        result=run_case(read_case(json.dumps(engine_request(profile))),root)['stage_b']
        companies.append({'ticker':ticker,'economic_hash':profile['economic_hash'],
            'classification':'PROPOSED_FORECAST_ESTIMATES_NOT_REPORTED_FACTS',
            'policy_version':economic['policy']['version'],'anchor':economic['anchor'],
            'anchor_revenue':economic['anchor_revenue'],'information_review':economic['dates']['information_review'],
            'sources':[{k:s[k] for k in ('id','url','sha256','bytes')} for s in economic['sources']],
            'wacc':economic['fields']['wacc']['value'],
            'annual_inputs':economic['scenarios']['Base'],
            'annual_forecast':result['stage_a']['years'],
            'pv_explicit_fcff':result['pv_explicit_fcff'],'pv_terminal_value':result['pv_terminal_value'],
            'enterprise_value':result['enterprise_value']})
    return {'schema_version':'registered-preload-verification-v1','companies':companies,
            'scope':'Registered five-year profiles only; no universe expansion, historical approval, equity bridge or ten-year defaults.'}


def outputs(data):
    stream=StringIO(newline='')
    columns=['ticker','fiscal_year_label','revenue','ebit','tax','nopat','d_and_a','investment','working_capital_cash_requirement','fcff']
    writer=csv.DictWriter(stream,columns,lineterminator='\n');writer.writeheader()
    for company in data['companies']:
        for year in company['annual_forecast']:
            writer.writerow({'ticker':company['ticker'],**{k:year[k] for k in columns[1:]}})
    return {JSON_PATH:json.dumps(data,indent=2,sort_keys=True)+'\n',CSV_PATH:stream.getvalue()}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data=build()
    for name,text in outputs(data).items():
        path=ROOT/name
        if args.check:
            if path.read_bytes()!=text.encode():raise SystemExit('Verification output differs: '+name)
        else:path.write_text(text)
    years=sum(len(company['annual_forecast']) for company in data['companies'])
    print(f"{len(data['companies'])} registered company profiles and {years} forecast years verified offline")


if __name__=='__main__':main()
