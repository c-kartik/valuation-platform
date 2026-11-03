"""Replay Apple A1-A8 implementation evidence; no source or consumer mutation.

The newly received FY2026 filing is evidence for explicitly bound FY2024/25
comparatives only. Its presence does not change the selected historical window.
"""
import argparse
from datetime import date
from decimal import Decimal
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

from calculate_historical_fcff_from_filings import RetainedFiling
from reconcile_historical_fcff_adjustments import exact, selector, CURRENT_APPLE, DEFERRED_APPLE
from prepare_trillion_review_batch import primary_fact
import resolve_apple_cashflows as prior
from test_operating_fcff_from_filings import statement_terms, classify, point_from
from valuation_platform.analyst import cash_flow_inputs as cash, statement_delivery as statements
from valuation_platform.review.operating_fcff import amount, serialized
from valuation_platform.valuation.consumer import ANCHORS

ROOT = Path(__file__).resolve().parents[1]
FOLDER = Path('docs/company-resolutions/AAPL/implementation-2026-11-03')
OUTPUT = FOLDER/'evidence-ledger.json'
MATRIX = FOLDER/'availability-matrix.json'
YEAR_TARGETS = {2024:('2023-10-01','2024-09-28'),2025:('2024-09-29','2025-09-27')}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sum_values(points):
    return sum((amount(p['value']) for p in points),Fraction())


def rate(numerator, denominator):
    value=amount(numerator)/amount(denominator)
    return {'exact_fraction':{'numerator':str(value.numerator),'denominator':str(value.denominator)},
            'decimal':serialized(value)['amount_usd'],'unit':'fraction'}


def dollar_rows(filing, identity, caption):
    """Bind all exact annual USD cells in the uniquely named note table."""
    tables=statements.parse({'body':filing.primary.artifact.body},improved=True)
    target=(identity['cik'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']))
    candidates=[]
    for ti,table in enumerate(tables):
        if not any(row and row[0]['text'].strip()==caption for row in table):continue
        points=[]
        for ri,row in enumerate(table):
            for ci,cell in enumerate(row):
                for item in cell['facts']:
                    attrs=item['attrs']
                    if cash._context(filing.contexts[attrs['contextref']])!=target:continue
                    unit=filing.units.get(attrs.get('unitref'))
                    if unit is None or len(unit)!=1 or unit[0].text.rsplit(':',1)[-1]!='USD':continue
                    point=primary_fact({'filing':filing},item,ti,ri,ci,row[0]['text'].strip())
                    # Tax-credit tags can be positive magnitudes even when
                    # presented as a negative reconciliation contribution.
                    from prepare_standard_review_batch import cfo
                    signed=cfo.displayed(cell['text'],Decimal(0))*Decimal(10)**int(attrs.get('scale','0'))
                    if abs(amount(str(signed)))!=abs(amount(point['value'])):
                        raise ValueError('Tax reconciliation display/source magnitude differs')
                    point['reconciliation_contribution_usd']=str(signed)
                    points.append(dict(point,source_identity=filing.source_identity,target_identity=identity,sources=filing.references))
        candidates.append(points)
    if len(candidates)!=1:raise ValueError('Unique source tax reconciliation required')
    points=candidates[0]
    totals=[p for p in points if p['primary_table']['caption']=='Provision for income taxes']
    if len(totals)!=1:raise ValueError('Unique tax total required')
    components=[p for p in points if p not in totals]
    if sum((amount(p['reconciliation_contribution_usd']) for p in components),Fraction())!=amount(totals[0]['value']):
        raise ValueError('Tax-note component sum differs')
    return {'components':components,'total':totals[0],'difference_usd':'0'}


def inventory(filing, identity):
    names=('InterestExpense','InterestExpenseNonoperating','InterestExpenseDebt','InterestPaid','InterestPaidNet',
        'FinanceLeasePrincipalPayments','RepaymentsOfCapitalLeaseObligations','RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability',
        'CapitalExpendituresIncurredButNotYetPaid','AmortizationOfIntangibleAssets','FinanceLeaseRightOfUseAssetAmortization')
    return {name:exact(filing,identity,name,optional=True) for name in names}


def statement_point(filing,identity,concept):
    """Recheck statement-specific facts, including inline fixed-zero debt rows."""
    view=selector(filing,identity)
    tables=statements.parse({'body':filing.primary.artifact.body},improved=True)
    target=(identity['cik'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']))
    choices=[]
    for ti,table in enumerate(tables):
        if not any(row and row[0]['text'].strip()=='Financing activities:' for row in table):continue
        for ri,row in enumerate(table):
            for ci,cell in enumerate(row):
                for item in cell['facts']:
                    attrs=item['attrs'];prefix,local=attrs['name'].split(':')
                    if local!=concept or cash._context(filing.contexts[attrs['contextref']])!=target:continue
                    choices.append(prior.operating.table_point(view,identity,
                        {'table':ti,'row':ri,'column':ci,'caption':row[0]['text'].strip()},
                        concept,filing.namespaces[prefix],{attrs['contextref']}))
    if len(choices)!=1:raise ValueError('Unique financing-statement current-period cell required')
    return choices[0]


def prose_evidence(filing):
    """Evidence excerpts retain original body hash and deterministic text offsets."""
    patterns={'lease_note':r'Note [0-9]+ [–-] Leases','depreciation':r'Depreciation expense on property',
        'intangible_amortization':r'Amortization expense related to intangible assets',
        'state_aid':r'one-time income tax charge','scope':r'accounts of Apple Inc. and its wholly owned subsidiaries',
        'capitalized_interest':r'capitalized interest','principal_cash':r'finance.lease principal|principal payments on finance',
        'interest_expense':r'interest expense','operating_cfo_explanation':r'cash generated by operating activities'}
    text=filing.text
    result={}
    for key,pattern in patterns.items():
        hits=list(re.finditer(pattern,text,re.I))
        result[key]={'occurrences':len(hits),'excerpts':[{'offset':m.start(),'text':text[max(0,m.start()-100):m.end()+1000]} for m in hits[:8]]}
    return {'source_identity':filing.source_identity,'sources':filing.references,'matches':result,
        'absence_limit':'No match in this retained primary is a bounded search result, not universal public nondisclosure.'}


def verify_new_sources(root):
    manifest=json.loads((root/FOLDER/'new-source-manifest.json').read_text())
    for source in manifest:
        if source['status']!=200:raise ValueError('Successful retained response required')
        path=root/FOLDER/source['file']
        if path.stat().st_size!=source['byte_length'] or digest(path)!=source['sha256']:
            raise ValueError('New official response hash/length changed')
    submissions=json.loads((root/FOLDER/'new-sources/submissions.json').read_text())
    recent=submissions['filings']['recent'];i=recent['accessionNumber'].index('0000320193-26-000026')
    if (int(submissions['cik']),recent['form'][i],recent['filingDate'][i],recent['reportDate'][i],recent['primaryDocument'][i]) != (
        320193,'10-K','2026-11-03','2026-09-26','aapl-20260926.htm'):
        raise ValueError('New filing identity/submissions discrepancy')
    return manifest


def companyfacts_search(root):
    data=json.loads((root/FOLDER/'new-sources/companyfacts.json').read_text())
    if data['cik']!=320193:raise ValueError('Company Facts entity mismatch')
    found={}
    for year,(start,end) in YEAR_TARGETS.items():
        selected=[]
        for concept,item in data['facts']['us-gaap'].items():
            if not re.search(r'InterestExpense|InterestPaid|FinanceLeasePrincipal|RepaymentsOfCapitalLease|CapitalExpendituresIncurredButNotYetPaid|AmortizationOfIntangibleAssets',concept):continue
            for obs in item.get('units',{}).get('USD',[]):
                if obs.get('start')==start and obs.get('end')==end:
                    selected.append({'concept':concept,'observation':obs})
        found[str(year)]={'exact_annual_standard_usd_observations':selected,
            'gross_expensed_interest_observations':[o for o in selected if o['concept'] in ('InterestExpense','InterestExpenseNonoperating','InterestExpenseDebt')],
            'scope':'SEC Company Facts us-gaap USD exact annual durations; custom tags and other source types require primary/instance search.'}
    return found


def build(root=ROOT):
    manifest=verify_new_sources(root)
    old=prior.build(root)
    package_path=Path(ANCHORS['aapl-fy2025']['package'])
    rows=json.loads((root/package_path).read_text())['aapl_history_review']['periods']
    filings={int(r['identity']['annual_end'][:4]):RetainedFiling(root,r,{}) for r in rows}
    fresh_row=json.loads((root/FOLDER/'new-source-row.json').read_text())
    fresh=RetainedFiling(root,fresh_row,{})
    all_results=[]
    for row,existing in zip(rows,old['periods'],strict=True):
        identity=row['identity'];year=int(identity['annual_end'][:4]);filing=filings[year]
        terms,cfo=statement_terms(row,filing)
        for term in terms:term['role']=classify(term)
        trade=[t for t in terms if t['role']=='named_trade_movement']
        mixed=[t for t in terms if t['role']=='mixed_asset_liability_movement']
        da=[t for t in terms if t['role']=='reported_da_or_combined_impairment']
        sbc=[t for t in terms if t['source']['concept']=='ShareBasedCompensation']
        if len(da)!=1 or len(sbc)!=1:raise ValueError('Apple source population changed')
        provision=exact(filing,identity,'IncomeTaxExpenseBenefit');pretax=point_from(filing,identity,row['facts']['pretax'])
        current=[exact(filing,identity,c) for c in CURRENT_APPLE]
        deferred=[exact(filing,identity,c) for c in DEFERRED_APPLE]
        if sum_values(current+deferred)!=amount(provision['value']):raise ValueError('Provision components do not tie')
        state=exact(filing,identity,'EffectiveIncomeTaxRateReconciliationImpactOfTheStateAidDecisionAmount',namespace='aapl',optional=True)
        tax_without_identified_state_aid=amount(provision['value'])-(amount(state['value']) if state is not None else Fraction())
        # A missing discrete-item line is not a zero fact: for earlier years
        # we retain the reported provision and explicitly apply no adjustment.
        tax={'reported_provision':provision,'reported_pretax':pretax,'cash_paid':exact(filing,identity,'IncomeTaxesPaidNet'),
            'current_components':current,'deferred_components':deferred,'component_difference_usd':'0',
            'etr_note':dollar_rows(filing,identity,'Computed expected tax'),
            'reported_etr':rate(provision['value'],pretax['value']),
            'state_aid_item':state,'state_aid_only_adjusted_rate':rate(str(tax_without_identified_state_aid),pretax['value']),
            'adjustment_applied':state is not None,'historical_cash_adjustment_usd':'0',
            'fully_normalized_operating_tax_rate':None,
            'policy':'Reported provision/pretax is approved as an allocation convention for the unadjusted EBIT diagnostic; allocated tax is not reported operating cash tax.'}
        inv=inventory(filing,identity)
        new_comparative=None
        if year in YEAR_TARGETS:
            target=dict(identity)
            new_inv=inventory(fresh,target)
            dep=exact(fresh,target,'Depreciation')
            amort=new_inv['AmortizationOfIntangibleAssets']
            cf_da=exact(fresh,target,'DepreciationDepletionAndAmortization')
            if amount(cf_da['value'])!=amount(da[0]['cash_contribution_usd']):raise ValueError('Later cash D&A differs')
            difference=sum_values([dep,amort])-amount(cf_da['value'])
            # Two notes each rounded to the nearest 100m; the cash statement
            # is at million precision. Intervals are source-precision checks,
            # not an estimate or an inferred operating-cost allocation.
            allowance=Fraction(100500000)
            new_comparative={'source_identity':fresh.source_identity,'target_identity':target,
                'depreciation':dep,'intangible_amortization':amort,'cash_statement_da':cf_da,
                'note_sum_minus_cash_statement_da':serialized(difference),
                'combined_rounding_halfwidth_usd':str(allowance),
                'note_sum_rounding_compatible_with_cf_da':abs(difference)<=allowance,
                'supports_complete_expense_alignment':False,'interest_and_lease_inventory':new_inv,
                'use':'Explicit later comparative support only; no historical total replaced or residual amortization inferred.'}
            new_comparative['cash_statement_repeat_checks']={}
            for concept in ('NetCashProvidedByUsedInOperatingActivities','PaymentsToAcquirePropertyPlantAndEquipment',
                'ProceedsFromIssuanceOfLongTermDebt','RepaymentsOfLongTermDebt','ProceedsFromRepaymentsOfCommercialPaper',
                'ProceedsFromPaymentsForOtherFinancingActivities'):
                original=statement_point(filing,identity,concept);later=statement_point(fresh,target,concept)
                if amount(original['value'])!=amount(later['value']):raise ValueError('Later cash comparative changed; manual review required')
                new_comparative['cash_statement_repeat_checks'][concept]={'original':original,'later':later,'difference_usd':'0'}
            if year==2025:
                old_other_assets=exact(filing,identity,'OtherAssetsNoncurrent',instant=True)
                later_other_assets=exact(fresh,target,'OtherAssetsNoncurrent',instant=True)
                intangible=exact(fresh,target,'IntangibleAssetExcludingGoodwillAfterAccumulatedAmortizationNoncurrent',namespace='aapl',instant=True)
                if amount(old_other_assets['value'])-amount(later_other_assets['value'])!=amount(intangible['value']):
                    raise ValueError('Explicit intangible balance reclassification does not tie')
                new_comparative['noncurrent_asset_presentation']={'original_other_noncurrent_assets':old_other_assets,
                    'later_other_noncurrent_assets':later_other_assets,'separately_shown_intangibles':intangible,
                    'difference_usd':'0','cash_investment_inferred':False,
                    'interpretation':'83.727B original Other noncurrent assets =72.634B later Other +11.093B separately shown intangibles. This is a book presentation bridge, not cash investment.'}
        interest=filing.total_interest(identity)
        fcff=existing['platform_after']['fcff_usd']
        all_results.append({'fiscal_year':year,'identity':identity,'source_urls':[s['url'] for s in filing.references],
            'availability':{'reported_cfo_cash_ppe_fcf':{'value_usd':existing['reported_cash_fcf']['amount_usd'],'status':'AVAILABLE_REPORTED_CASH_PERIMETER'},
                'fcff_reported_cfo_basis':{'value_usd':fcff,'status':'AVAILABLE_EXPLICIT_REPORTED_ETR_CONVENTION' if fcff is not None else 'UNAVAILABLE_REQUIRED_INTEREST',
                    'basis':'reported CFO + gross expensed interest * (1 - provision/pretax) - cash PP&E',
                    'comparability':'SBC add-back remains in reported CFO; not forecast-comparable operating FCFF'},
                'fcff_valuation_aligned':{'value_usd':None,'status':'UNAVAILABLE_INPUT_ALIGNMENT','blocking_ids':['A4','A5','A6']},
                'fcfe_identified_funding':{'value_usd':existing['fcfe']['amount_usd'],'status':'PROVISIONAL_UNCLASSIFIED_FINANCING','blocking_ids':['A2','A3'],
                    'unknown_is_zero':False,'ownership':'Consolidated wholly owned subsidiaries under filing basis; no minority attribution assumption needed'},
                'fcfe_verified':{'value_usd':None,'status':'UNAVAILABLE_UNCLASSIFIED_FINANCING','blocking_ids':['A2','A3']}},
            'interest_expense':interest,'missing_input_inventory':inv,
            'funding_review':existing['financing'],'financing_source_rows':existing['financing_source_rows'],
            'operating_bridge':{'statement_terms':terms,'trade_cash_rows':trade,'mixed_cash_rows':mixed,
                'mixed_cash_sum':serialized(sum((amount(t['cash_contribution_usd']) for t in mixed),Fraction())),
                'expense_da_source':da[0],'sbc_remains_expensed':sbc[0],
                'complete_operating_cash_working_capital':None,'complete_expense_aligned_da':None,
                'complete_economic_investment':None,
                'no_book_delta_substitution':True,'no_mixed_row_residual_allocation':True,
                'exact_existing_cfo_bridge':existing['operating_fcff_candidate']['cash_fcf_bridge']},
            'tax_review':tax,'new_comparative_support':new_comparative})
    policy_path=Path('data/preload/aapl-v1/policy.json');policy=json.loads((root/policy_path).read_text())
    conf=policy['configuration']
    if (conf['tax_start'],conf['tax_endpoint'],conf['terminal_tax'])!=('0.18','0.20','0.20'):
        raise ValueError('Reviewed preloaded forecast tax policy changed')
    forecast={'policy_source':str(policy_path),'policy_sha256':digest(root/policy_path),
        'choice':'RETAIN_EXISTING_EXPLICIT_FORECAST_CONVENTION','source_fact':False,
        'tax_start_before':'0.18','tax_start_after':'0.18','tax_endpoint_before':'0.20','tax_endpoint_after':'0.20',
        'terminal_tax_before':'0.20','terminal_tax_after':'0.20','historical_cash_changed':False,
        'forecast_numeric_change':'0','valuation_numeric_change':'0',
        'valuation_effect_basis':'No source, assumption, method or data consumer is mutated by this schedule. Root integration must independently compare generated Base/Bear/Bull valuations.',
        'rationale':'Keep the existing explicit forecast path and independent terminal 20% assumption after review of the historical note reconciliation. Do not calibrate forecasts to State Aid-distorted reported ETR or claim the State Aid-only adjustment is a sustainable operating tax rate.',
        'retained_uncertainties':['Future geographic profit mix and foreign tax rules','R&D capitalization and credit realization','Valuation allowance realizability','Operating versus nonoperating tax allocation'],
        'no_automatic_cfo_state_aid_addback':True}
    inputs=[package_path,prior.SOURCE_MAP,prior.DECISIONS,Path('scripts/resolve_apple_cashflows.py'),
        Path('scripts/reconcile_historical_fcff_adjustments.py'),Path('scripts/test_operating_fcff_from_filings.py'),policy_path,
        FOLDER/'new-source-manifest.json',FOLDER/'new-source-row.json',FOLDER/'new-source-receipts.json']
    return {'schema_version':'apple-open-roadblock-implementation-v1','review_date':'2026-11-03','ticker':'AAPL',
        'parent_status':'OPEN','historical_scope':'FY2021-FY2025 original annuals; FY2026 is later comparative evidence only',
        'inputs_sha256':{str(p):digest(root/p) for p in inputs},'new_official_sources':manifest,
        'current_companyfacts_search':companyfacts_search(root),
        'periods':all_results,'forecast_tax_policy_reconciliation':forecast,
        'source_searches':[prose_evidence(f) for f in filings.values()]+[prose_evidence(fresh)],
        'outcomes':{
            'A1':'OPEN: no gross-expensed-interest fact in 2024/25 originals, new 2026 comparatives or current SEC Company Facts exact-period inventory',
            'A2':'OPEN: all original and latest comparative Other financing amounts agree; no complete cash decomposition',
            'A3':'OPEN: stocks, future maturities and combined ROU additions do not form a complete cash principal roll-forward',
            'A4':'OPEN: exact EBIT-to-CFO bridge and named/mixed cash schedule implemented; mixed rows remain unallocated',
            'A5':'OPEN: new 2026 amortization comparatives bound; 2024 note sum is incompatible with cash-statement D&A beyond displayed rounding',
            'A6':'OPEN: cash PP&E remains explicit basis; new licensed/owned intangible and combined ROU disclosures do not quantify complete cash/noncash investment',
            'A7':'APPROVED_ALLOCATION_CONVENTION_IMPLEMENTED: provision/pretax is used only as a labeled historical EBIT allocation, not operating cash tax; tax/mixed-movement alignment remains A4',
            'A8':'EXISTING_NUMERIC_POLICY_RECONCILED_RETAINED: 18% to 20%, independent terminal20%; State Aid-only adjusted accounting rates are not sustainable operating-tax facts; root valuation parity verification pending'},
        'validation':{'financing_statement_exact_checks':5,'cfo_statement_exact_checks':5,'tax_note_exact_component_checks':5,
            'current_plus_deferred_tax_exact_checks':5,'new_comparative_da_checks':2,'new_verified_fcff_periods':0,'new_verified_fcfe_periods':0},
        'publication':{'historical_numeric_changes':False,'forecast_numeric_changes':False,'cleared_fcfe_values':False,
            'fully_resolved_company':False,'current_report_integration':'Root consumer must retain separate method, ownership, financing and valuation-readiness fields.'}}


def main():
    parser=argparse.ArgumentParser(description=__doc__);g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');args=parser.parse_args()
    data=build()
    matrix={'schema_version':'company-cashflow-availability-v1','ticker':'AAPL','parent_status':'OPEN',
        'periods':[{'fiscal_year':p['fiscal_year'],'identity':p['identity'],'metrics':p['availability']} for p in data['periods']],
        'metric_contract':'Distinct reported-cash convention, provisional identified-funding FCFE and unavailable valuation-aligned/verified scopes. Never fallback across them.'}
    for path,value in ((OUTPUT,data),(MATRIX,matrix)):
        payload=json.dumps(value,indent=2,sort_keys=True)+'\n'
        if args.write:(ROOT/path).write_text(payload)
        elif (ROOT/path).read_text()!=payload:raise SystemExit('Apple implementation evidence changed; review before write: '+str(path))
    print(json.dumps(data['validation'],sort_keys=True))


if __name__=='__main__':main()
