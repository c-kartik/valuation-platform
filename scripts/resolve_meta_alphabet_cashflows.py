"""Offline, source-bound replay of the approved META/GOOGL FY2021–25 decisions.

Original facts and adoption ledgers stay sealed. Only the separate Meta net
identified-receipts overlay is consumed by the public historical catalog.
"""
import argparse
import csv
from fractions import Fraction
from io import StringIO
import json
from pathlib import Path

from calculate_historical_fcff_from_filings import RetainedFiling
from resolve_apple_cashflows import verify_cell, sha
from valuation_platform.analyst import statement_delivery as statements
from valuation_platform.review.cfo_history import adopted_window
from valuation_platform.review.filing_fcff import calculate
from valuation_platform.review.operating_fcff import amount, serialized
from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('docs/company-resolutions')
IDS={'META':('META-FCFE-001','META-INV-001','META-FCFE-002','META-INT-001','META-TAX-001'),
     'GOOGL':('GOOGL-NCI-001','GOOGL-LEASE-001')}
FUNDING={'Proceeds from issuance of long-term debt, net','Principal payments on finance leases',
         'Net change in overdraft in cash pooling entities','Proceeds from issuance of debt, net of costs',
         'Repayments of debt'}
ROLES={'COMMON_EQUITY_OR_OTHER_OWNER_CASH','DIVIDENDS_NOT_NET_BORROWING','DEBT_FUNDING_OR_PRINCIPAL',
       'LEASE_PRINCIPAL','OTHER_FINANCING_EXCLUDED','NONCONTROLLING_CAPITAL_NOT_DEBT','FINANCING_TOTAL'}


def financing(filing,identity,mappings):
    cells=[verify_cell(filing,identity,m) for m in mappings]
    selected={(m['row'],m['column'],m['context_id']) for m in mappings}
    if len(selected)!=len(mappings) or len({m['table'] for m in mappings})!=1:
        raise ValueError('Duplicate financing cell or competing statement tables')
    table=statements.parse({'body':filing.primary.artifact.body},improved=True)[mappings[0]['table']]
    contexts={m['context_id'] for m in mappings}
    actual={(ri,ci,f['attrs']['contextref']) for ri in range(min(m['row'] for m in mappings),max(m['row'] for m in mappings)+1)
            for ci,cell in enumerate(table[ri]) for f in cell['facts'] if f['attrs'].get('contextref') in contexts}
    if actual!=selected:raise ValueError('Incomplete current-period financing population')
    total=[];cash=Fraction();net=Fraction();unknown=[];nci=Fraction()
    for m in cells:
        role=m['classification'];value=amount(m['signed_cash_usd']);inc=m['included_in_net_borrowing']
        if role not in ROLES or type(inc) is not bool or inc!=(role in ('DEBT_FUNDING_OR_PRINCIPAL','LEASE_PRINCIPAL')):
            raise ValueError('Unapproved financing inclusion')
        if inc != (m['caption'] in FUNDING):raise ValueError('Reviewed caption and funding classification disagree')
        if role=='FINANCING_TOTAL':total.append(value);continue
        cash+=value
        if inc:net+=value
        if role=='OTHER_FINANCING_EXCLUDED':unknown.append(m['signed_cash_usd'])
        if role=='NONCONTROLLING_CAPITAL_NOT_DEBT':nci+=value
    if total!=[cash]:raise ValueError('Financing statement does not close exactly')
    return dict(net_borrowing=serialized(net),total=serialized(cash),unallocated_other_usd=unknown,
                nci_contributions_excluded_from_debt=serialized(nci),source_rows=cells,statement_difference_usd='0')


def verified_narrative(filings,mapping):
    out=[]
    for point in mapping:
        filing=filings[int(point['source_identity']['annual_end'][:4])]
        if filing.source_identity!=point['source_identity'] or point['excerpt'] not in filing.text:
            raise ValueError('Narrative source identity or exact excerpt changed')
        out.append(dict(point,source=filing.references))
    return out


def investment_comparatives(filings,mapping,net_by_year):
    out=[]
    for m in mapping:
        f=filings[int(m['source_identity']['annual_end'][:4])]
        if f.source_identity!=m['source_identity']:raise ValueError('Comparative filing mismatch')
        base=verify_cell(f,m['target_identity'],m['cash_ppe'])
        receipts=[verify_cell(f,m['target_identity'],r) for r in m['receipts']]
        net=-amount(base['signed_cash_usd'])-sum((amount(r['signed_cash_usd']) for r in receipts),Fraction())
        if net!=net_by_year[int(m['target_identity']['annual_end'][:4])]:raise ValueError('Gross/net investment vintage mismatch')
        out.append(dict(target_identity=m['target_identity'],source_identity=m['source_identity'],base=base,receipts=receipts,
                        net_cash_investment=serialized(net),original_comparative_difference_usd='0'))
    return out


def build_company(ticker,root=ROOT):
    folder=BASE/ticker;maps=json.loads((root/folder/'source-map.json').read_text());dec=json.loads((root/folder/'decisions.json').read_text())
    if tuple(d['id'] for d in dec['decisions'])!=IDS[ticker] or any(d['authorization']!='USER_APPROVED_TREATMENT' for d in dec['decisions']):
        raise ValueError('Exact scoped manual approval required')
    if dec['ticker']!=ticker or dec['fiscal_years']!=list(range(2021,2026)) or dec['estimates_permitted'] or dec['automatic_fcfe_publication']:
        raise ValueError('Unsupported period, estimate or automatic FCFE adoption')
    kind={'META':'meta-fy2025','GOOGL':'googl-fy2025'}[ticker];spec=ANCHORS[kind];load_revenue_anchor(kind,root)
    package=json.loads((root/spec['package']).read_text());rows=package['periods'] if ticker=='META' else package['googl_history_review']['periods']
    if [m['identity'] for m in maps['periods']]!=[r['identity'] for r in rows]:raise ValueError('Accepted period mapping mismatch')
    filings={int(r['identity']['annual_end'][:4]):RetainedFiling(root,r,{}) for r in rows}
    before=adopted_window(root,kind);periods=[];net_by_year={}
    for row,m,old in zip(rows,maps['periods'],before,strict=True):
        identity=row['identity'];year=int(identity['annual_end'][:4]);f=filings[year]
        funding=financing(f,identity,m['financing_rows']);inputs=dict(old['fcff_calculation']['inputs'])
        receipts=[verify_cell(f,identity,p) for p in m['investment_receipts']]
        if any(p['concept']!='ProceedsFromSaleOfPropertyPlantAndEquipment' or amount(p['signed_cash_usd'])<0 for p in receipts):
            raise ValueError('Only identified positive fixed-asset receipts approved')
        receipt=sum((amount(p['signed_cash_usd']) for p in receipts),Fraction());netcapex=amount(inputs['cash_ppe'])-receipt
        net_by_year[year]=netcapex;inputs['cash_ppe']=str(netcapex)
        fcff=calculate(*(inputs[k] for k in ('cfo','cash_ppe','interest_expense','tax_provision','pretax_income')))
        if amount(fcff['amount_usd'])-amount(old['fcff'])!=receipt:raise ValueError('Unexpected FCFF treatment delta')
        net=amount(funding['net_borrowing']['amount_usd']);fcfe=serialized(amount(inputs['cfo'])-netcapex+net)
        label='PROVISIONAL_FINANCING_SCOPE_UNRESOLVED' if ticker=='META' else 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'
        periods.append(dict(fiscal_year=year,identity=identity,inputs=inputs,investment_receipt_sources=receipts,
            net_cash_investment=serialized(netcapex),identified_receipts=serialized(receipt),financing=funding,
            fcff=fcff,platform_before_usd=old['fcff'],platform_change_usd=str(receipt),
            fcfe=dict(fcfe,status=label,formula='reported CFO - cash PP&E net of identified receipts + identified net borrowing',
                      publishable_as_parent_common=False,omitted_other_assumed_zero=False),parent_common_fcfe_usd=None,
            source_urls=old['fcff_calculation']['sources'],forecast_inputs_changed=False))
    controls={}
    if ticker=='META':
        controls['investment_comparatives']=investment_comparatives(filings,maps['investment_comparatives'],net_by_year)
        b=maps['overdraft_comparative'];later=filings[int(b['source_identity']['annual_end'][:4])]
        if later.source_identity!=b['source_identity']:raise ValueError('Overdraft comparative filing mismatch')
        other=verify_cell(later,b['target_identity'],b['other']);first=periods[0]['financing']['source_rows']
        original=[r for r in first if r['caption'] in ('Net change in overdraft in cash pooling entities','Other financing activities')]
        if len(original)!=2 or sum((amount(r['signed_cash_usd']) for r in original),Fraction())!=amount(other['signed_cash_usd']):raise ValueError('Overdraft presentation does not reconcile')
        controls['overdraft_bridge']=dict(original=original,later=other,difference_usd='0',fcfe_change_usd='0')
        research=folder/'research/source-manifest.json';controls['research_manifest_sha256']=sha(root/research)
        controls['remaining_other_is_not_assumed_zero']=True
    else:
        controls['nci_narrative']=verified_narrative(filings,maps['nci_narrative'])
        if len(controls['nci_narrative'])!=5:raise ValueError('Five annual NCI narrative bindings required')
        controls['lease_narrative']=verified_narrative(filings,maps['lease_narrative'])
        controls['lease_cash_containment']=[]
        for m in maps['lease_cash']:
            f=filings[int(m['source_identity']['annual_end'][:4])]
            if f.source_identity!=m['source_identity']:raise ValueError('Lease comparative source mismatch')
            cell=verify_cell(f,m['target_identity'],m['cell']);y=int(m['target_identity']['annual_end'][:4])
            parent=next(r for r in periods[y-2021]['financing']['source_rows'] if r['caption']=='Repayments of debt')
            if parent['concept']!='RepaymentsOfDebtAndCapitalLeaseObligations' or amount(cell['signed_cash_usd'])>-amount(parent['signed_cash_usd']):raise ValueError('Lease parent containment mismatch')
            controls['lease_cash_containment'].append(dict(fiscal_year=y,component=cell,parent=parent,additional_deduction_usd='0'))
        controls['parent_common_fcfe_usd']=None;controls['nci_fair_value_usd']=None;controls['nci_book_value_used_as_fair_value']=False
    paths=[folder/'source-map.json',folder/'decisions.json',Path(spec['package']),Path('scripts/resolve_meta_alphabet_cashflows.py'),Path('scripts/resolve_apple_cashflows.py')]
    return dict(schema_version='company-cashflow-resolution-v1',ticker=ticker,review_date='2026-11-03',decisions=dec,
                inputs_sha256={str(p):sha(root/p) for p in paths},periods=periods,controls=controls,
                validation=dict(financing_statements=5,source_mismatches=0,estimated_operands=0,forecast_changes=0),
                limitations=['Historical CFO basis differs from SBC-expensed EBIT forecast and finance-asset investment scope.',
                             'Reported provision/pretax is an explicit historical tax allocation, not a recurring forecast rate.',
                             'Other financing unresolved; full FCFE not certified.' if ticker=='META' else 'Parent-common attribution and NCI fair value unresolved.'])


def csv_text(data):
    s=StringIO(newline='');w=csv.writer(s,lineterminator='\n');w.writerow(['fiscal_year','net_cash_investment_usd','net_borrowing_usd','fcff_usd','fcff_change_usd','fcfe_usd','fcfe_status','parent_common_fcfe_usd'])
    for p in data['periods']:w.writerow([p['fiscal_year'],p['net_cash_investment']['amount_usd'],p['financing']['net_borrowing']['amount_usd'],p['fcff']['amount_usd'],p['platform_change_usd'],p['fcfe']['amount_usd'],p['fcfe']['status'],''])
    return s.getvalue()


def outputs(ticker,data):
    folder=BASE/ticker;out={folder/'results.json':json.dumps(data,indent=2,sort_keys=True)+'\n',folder/'results.csv':csv_text(data)}
    if ticker=='META':
        overlay=dict(schema_version='approved-meta-net-investment-v1',decision_id='META-INV-001',periods=[dict(identity=p['identity'],original_cash_ppe_usd=str(amount(p['inputs']['cash_ppe'])+amount(p['identified_receipts']['amount_usd'])),identified_receipts_usd=p['identified_receipts']['amount_usd'],net_cash_ppe_usd=p['inputs']['cash_ppe'],fcff_usd=p['fcff']['amount_usd'],source_urls=sorted({r['source']['sources'][0]['url'] for r in p['investment_receipt_sources']})) for p in data['periods']])
        out[folder/'adopted-history.json']=json.dumps(overlay,indent=2,sort_keys=True)+'\n'
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--check',action='store_true');g.add_argument('--write',action='store_true');args=p.parse_args()
    for ticker in IDS:
        data=build_company(ticker)
        for path,value in outputs(ticker,data).items():
            if args.check:
                if (ROOT/path).read_text()!=value:raise SystemExit(f'Reviewed resolution changed: {path}')
            else:(ROOT/path).write_text(value)
        print(ticker,json.dumps(data['validation'],sort_keys=True))

if __name__=='__main__':main()
