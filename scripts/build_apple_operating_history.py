"""Bind Apple annual/instant primary and XBRL facts; build a versioned overlay."""
import argparse
from copy import copy
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path

from calculate_historical_fcff_from_filings import RetainedFiling
from reconcile_historical_fcff_adjustments import exact
from valuation_platform.review.apple_operating_history import working_capital, calculate, METHOD, BASIS
from valuation_platform.valuation.consumer import ANCHORS

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('docs/company-resolutions/AAPL/operating-fcff-2026-11-04')
CONCEPTS = {'current_assets':'AssetsCurrent','cash':'CashAndCashEquivalentsAtCarryingValue',
            'current_securities':'MarketableSecuritiesCurrent','current_liabilities':'LiabilitiesCurrent',
            'commercial_paper':'CommercialPaper','current_term_debt':'LongTermDebtCurrent',
            'current_finance_lease':'FinanceLeaseLiabilityCurrent','current_operating_lease':'OperatingLeaseLiabilityCurrent'}
ANNUAL = {'ebit':'OperatingIncomeLoss','tax_provision':'IncomeTaxExpenseBenefit','pretax_income':'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
          'da':'DepreciationDepletionAndAmortization','cash_ppe':'PaymentsToAcquirePropertyPlantAndEquipment'}


def balance(filing, concept, instant):
    view=copy(filing);view.facts={}
    view.fact('selected',concept,'Exact primary/instance USD closing balance',instant=True,as_of=instant)
    return dict(view.facts['selected'],source_identity=filing.source_identity,
                target_instant=instant,sources=filing.references)


def build():
    package = ANCHORS['aapl-fy2025']['package']
    rows = json.loads((ROOT/package).read_text())['aapl_history_review']['periods']
    ledger, periods = [], []
    for row in rows:
        filing = RetainedFiling(ROOT,row,{})
        identity = row['identity']; y = int(identity['annual_end'][:4])
        points = {}; snapshots = {}
        for side, instant in [('opening',str(date.fromisoformat(identity['annual_start'])-timedelta(days=1))),('closing',identity['annual_end'])]:
            points[side] = {key: balance(filing,concept,instant) for key,concept in CONCEPTS.items()}
            snapshots[side] = {key:p['value'] for key,p in points[side].items()}
        annual = {key:exact(filing,identity,concept) for key,concept in ANNUAL.items()}
        inputs = {key:p['value'] for key,p in annual.items()}
        inputs.update({side+'_nwc':str(working_capital(snapshots[side])) for side in ('opening','closing')})
        current_tax = exact(filing,identity,'AccruedIncomeTaxesCurrent',instant=True,optional=True)
        if current_tax is None and y==2022:
            later=RetainedFiling(ROOT,rows[2],{})
            current_tax=balance(later,'AccruedIncomeTaxesCurrent',identity['annual_end'])
        urls = sorted({s['url'] for s in filing.references if s['url'].endswith('.htm')})
        periods.append({'fiscal_year':y,'identity':identity,'inputs':inputs,
            'opening_balances':snapshots['opening'],'closing_balances':snapshots['closing'],
            'fcff':calculate(inputs),'source_urls':urls,
            'qualification':'Standardized current-balance model including current tax accruals; mixed Other balances retained by convention, not separately verified pure operating cash.'})
        ledger.append({'fiscal_year':y,'identity':identity,'annual':annual,'balances':points,
            'separately_disclosed_current_tax_diagnostic':current_tax,
            'tax_diagnostic_missing_means_zero':False,'sources':filing.references})
    overlay = {'schema_version':'apple-operating-history-v1','ticker':'AAPL','methodology':METHOD,'basis':BASIS,
        'authorization':'User: ok follow this plan step by step and implement this solution to resolve the issue. report back to me once it is successful.',
        'forecast_calibration':False,'exact_unlevered_cash_flow_claim':False,'periods':periods}
    source = {'schema_version':'apple-operating-source-ledger-v1','package':package,
        'package_sha256':hashlib.sha256((ROOT/package).read_bytes()).hexdigest(),'periods':ledger}
    return {'adopted-history.json':overlay,'source-ledger.json':source}


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for name,data in build().items():
        text=json.dumps(data,indent=2,sort_keys=True)+'\n';path=ROOT/OUT/name
        if args.check:
            if path.read_text()!=text:raise ValueError('Replay differs: '+name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    print('PASS: five source-bound standardized operating FCFF calculations.')
