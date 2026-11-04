"""Build a lean, source-linked Apple decision record for the private platform."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'docs/company-resolutions/AAPL/remaining-issues-2026-11-04'


def build():
    stages={n:json.loads((FOLDER/n/'results.json').read_text()) for n in ('financing','da','tax','equity')}
    approval=json.loads((FOLDER/'approval.json').read_text())
    if approval['parent_company_status']!='OPEN':raise ValueError('No full company clearance approved')
    f=stages['financing'];e=stages['equity']
    assert all(p['full_fcfe_usd'] is None and p['actual_finance_lease_principal_usd'] is None and p['financing_statement_difference_usd']=='0' for p in f['periods'])
    assert e['no_missing_claims_assumed_zero'] and e['unresolved_operands']['fair_value_per_share_usd'] is None
    assert all(p['additional_da_plug_usd']=='0' for p in stages['da']['annual_adopted_inputs'])
    return {'schema_version':'apple-resolution-progress-v1','ticker':'AAPL','date':'2026-11-04','company_status':'OPEN','company_complete':False,
        'stages':[
            {'id':'financing','label':'Historical FCFE financing','outcome':'EVIDENCE_BLOCKED','detail':'Five financing statements reconcile. Other financing and actual finance-lease principal/containment remain unidentified. FCFE stays provisional; an issuer evidence request is prepared and unsent.'},
            {'id':'da','label':'Depreciation and amortization','outcome':'AGGREGATE_ADOPTED_RECONCILIATION_OPEN','detail':'Reported combined D&A is retained with no plug. The FY2024 $355m note-versus-cash-statement difference is not explained by rounding; exact expense-population alignment remains open.'},
            {'id':'tax','label':'Tax and working capital','outcome':'POLICY_ADOPTED','detail':'The all-year tax-inclusive historical NWC convention is recorded under the approved plan. Forward tax remains an explicit 18% to 20% assumption, terminal 20%, with separate incremental operating WC. Exact operating cash taxes and automatic historical calibration are not certified.'},
            {'id':'equity','label':'Equity and dated shares','outcome':'PARTIAL_SOURCE_BOUND','detail':'The 2025-09-27 common-share population is selected as dated support, with separate cash, debt fair/carrying values and lease observations. Eligible cash, complete claims and non-overlapping award treatment remain unresolved; fair value per share is not published.'}],
        'anchor_support':e['anchor_support'],
        'share_population':{'concept':'CommonStockSharesOutstanding','as_of':e['anchor_support']['as_of'],'shares':e['anchor_support']['dated_common_shares'],'award_adjusted_shares':None},
        'readiness':{'exact_fcfe':False,'exact_expense_alignment':False,'complete_equity_bridge':False,'fair_value_per_share':False,'automatic_history_calibration':False},
        'current_open_issue_ids':['A2','A3','A5','S1','S2','S3'],
        'policy_outcomes':{'A7':'ADOPTED_REPORTED_ETR_ALLOCATION_NOT_OBSERVED_OPERATING_CASH_TAX','historical_current_tax_nwc':'ADOPTED_UNIFORM_STANDARDIZED_POPULATION','dated_common_share_population':'DATE_MATCHED_SOURCE_SELECTED_BEFORE_AWARD_ADJUSTMENT','A1':'CURRENT_SELECTED_FCFF_GAP_RESOLVED_LEGACY_INTEREST_STILL_MISSING'},
        'remaining_evidence':['Apple consolidated Other-financing components and actual finance-lease principal cash with containing captions.','Supported D&A expense-population reconciliation for the FY2024 note difference.','Cash eligibility, claims/forecast overlap and existing-award valuation or denominator treatment before verified value per share.','History-to-forecast economic investment/tax/expense alignment; explicit forward financing assumptions for FCFE.'],
        'source_urls':e['source_urls']+['https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm'],
        'stage_workpaper_sha256':{n:hashlib.sha256((FOLDER/n/'results.json').read_bytes()).hexdigest() for n in stages},
        'approval_record':'docs/company-resolutions/AAPL/remaining-issues-2026-11-04/approval.json',
        'report':'docs/company-resolutions/AAPL/remaining-issues-2026-11-04/report.html'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();body=json.dumps(build(),indent=2,sort_keys=True)+'\n';path=FOLDER/'platform-resolution.json'
    if a.check:assert path.read_text()==body,'Apple progress differs from stage workpapers'
    else:path.write_text(body)
    print('PASS: four ordered stage outcomes, source support and unresolved financial gates; SHA256 '+hashlib.sha256(body.encode()).hexdigest())
