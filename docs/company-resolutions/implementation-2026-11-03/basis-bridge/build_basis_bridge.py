"""Offline source-to-diagnostic bridge; writes only this workpaper directory.
Reverses the exact reported CFO SBC add-back once. This is not a complete
valuation normalization and never replaces reported historical FCFF/FCFE.
"""
from pathlib import Path
import sys,json,hashlib,csv
from fractions import Fraction
from decimal import Decimal,localcontext
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from calculate_historical_fcff_from_filings import RetainedFiling
from valuation_platform.valuation.consumer import ANCHORS
from valuation_platform.analyst import statement_delivery as statements

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def num(x):
 x=Fraction(x)
 with localcontext() as c:c.prec=60;v=str(Decimal(x.numerator)/Decimal(x.denominator))
 return {'amount_usd':v,'exact_fraction_usd':{'numerator':str(x.numerator),'denominator':str(x.denominator)}}

def cash_statement_point(filing,target,table_index,concept,expected=None):
 p=filing.extract(concept,target)
 if p.get('value') is None:raise ValueError('Missing exact '+concept)
 if expected is not None and Fraction(p['value'])!=Fraction(expected):raise ValueError('Reviewed SBC source amount changed')
 table=statements.parse({'body':filing.primary.artifact.body},improved=True)[table_index]
 contexts={o['context_id'] for o in p['occurrences']}
 matches=[]
 for ri,row in enumerate(table):
  for ci,cell in enumerate(row):
   for fact in cell['facts']:
    a=fact['attrs']
    if a.get('name','').split(':')[-1]==concept and a.get('contextref') in contexts:
     matches.append({'table':table_index,'row':ri,'column':ci,'caption':row[0]['text'],'display':cell['text'],'primary_xml_id':a.get('id'),'context_id':a['contextref'],'primary_attributes':a})
 if len(matches)!=1:raise ValueError('Exact named cash-flow statement cell required: '+str((concept,matches)))
 return dict(p,statement_cell=matches[0])

EXPECTED={'AAPL':['7906000000','9038000000','10833000000','11688000000','12863000000'],
'META':['9164000000','11992000000','14027000000','16690000000','20427000000'],
'GOOGL':['15376000000','19362000000','22460000000','22785000000','24953000000']}
GAPS={
'AAPL':['CFO cash movements mix tax, operating and noncurrent populations; complete EBIT-to-CFO bridge not established.','Complete income-recognized D&A/impairment/lease amortization and economic-investment alignment remain separate reviews.','Unclassified financing/lease principal and FY2024/25 adopted interest gaps are not filled by subtracting SBC.'],
'META':['Capitalized-interest cash, investment and tax/amortization bridge remains unresolved.','Net cash PP&E is not the forecast cash-plus-financed-assets perimeter.','Five residual Other financing classifications remain unresolved.'],
'GOOGL':['CFO SBC add-back differs from separately disclosed total SBC expense; cash-settled awards, timing and other noncash adjustments are not fully reconciled.','Cash/noncash/prepaid finance-lease investment timing and capitalized-interest/tax alignment remain unresolved.','Consolidated FCFE remains before outside ownership allocation; this diagnostic cannot establish parent-common FCFE.']}
manifest_cache={};allrows=[];inputs={};source_refs={}
for kind in ('aapl-fy2025','meta-fy2025','googl-fy2025'):
 spec=ANCHORS[kind];ticker=spec['ticker'];package_path=ROOT/spec['package'];package=json.loads(package_path.read_text());prefix=ticker.lower()
 rows=package['periods'] if ticker=='META' else package[prefix+'_history_review']['periods']
 mapping_path=ROOT/f'docs/company-resolutions/{ticker}/source-map.json';mapping=json.loads(mapping_path.read_text())['periods']
 inputs[str(package_path.relative_to(ROOT))]=sha(package_path);inputs[str(mapping_path.relative_to(ROOT))]=sha(mapping_path)
 for n,(row,m) in enumerate(zip(rows,mapping,strict=True)):
  target=row['identity'];assert m['identity']==target
  f=RetainedFiling(ROOT,row,manifest_cache);table=m['financing_rows'][0]['table']
  cfo=cash_statement_point(f,target,table,'NetCashProvidedByUsedInOperatingActivities')
  sbc=cash_statement_point(f,target,table,'ShareBasedCompensation',EXPECTED[ticker][n])
  expense=f.extract('AllocatedShareBasedCompensationExpense',target)
  if expense.get('value') is None:expense=None
  remaining=['Historical CFO tax benefits, cash taxes and normalized unlevered operating tax remain different; no automatic SBC tax-effect adjustment.','Other noncash adjustments, nonoperating income/cash, operating working-capital scope and investment/financing timing remain to be reconciled.','Outstanding awards and dilution must be treated separately from future compensation, without charging the same item twice.']+GAPS[ticker]
  actual=Fraction(cfo['value']);reversed=Fraction(sbc['value']);diagnostic=actual-reversed
  allrows.append({'ticker':ticker,'fiscal_year':int(target['annual_end'][:4]),'identity':target,'reported_cfo':num(actual),'reported_cfo_source':cfo,'reported_sbc_addback':num(reversed),'reported_sbc_addback_source':sbc,'sbc_addback_reversal':num(-reversed),'cfo_after_reversing_reported_sbc_addback':num(diagnostic),'diagnostic_formula':'reported CFO - exact reported SBC add-back','reported_total_sbc_expense_source':expense,'reported_expense_minus_addback_arithmetic_comparison_usd':None if expense is None else num(Fraction(expense['value'])-reversed),'expense_comparison_is_not_a_new_adjustment':True,'tax_adjustment_applied_usd':'0','additional_sbc_or_dilution_charge_applied_usd':'0','reported_historical_values_replaced':False,'historical_change_usd':'0','valuation_aligned_cfo_usd':None,'valuation_aligned_fcff_usd':None,'valuation_aligned_fcfe_usd':None,'status':'PARTIAL_BASIS_BRIDGE_NOT_VALUATION_ALIGNED','metric_label':'CFO after reversing reported SBC add-back — diagnostic','remaining_gaps':remaining,'basis_guardrails':{'not_actual_cash_paid':True,'no_cagr_join_to_forecast':True,'no_automatic_forecast_calibration':True,'not_parent_common_fcfe':True}})
  for ref in f.references:source_refs[ref['url'],ref['sha256']]=ref
# Compare reviewed numerical policies with committed baseline and present read-only preloads.
baseline=json.loads((HERE/'baseline-tax-policy.json').read_text());tax=[]
for p in baseline['policies']:
 path=ROOT/p['path'];current=json.loads(path.read_text());before=p['configuration'];after={k:current['configuration'][k] for k in ('tax_start','tax_endpoint','terminal_tax')}
 def path_values(config):
  a=Fraction(config['tax_start']);b=Fraction(config['tax_endpoint']);return {str(2026+i):str(Decimal((a+(b-a)*Fraction(i,4)).numerator)/Decimal((a+(b-a)*Fraction(i,4)).denominator)) for i in range(5)}
 before_path=path_values(before);after_path=path_values(after)
 if before!=after or before_path!=after_path:raise ValueError('Reviewed tax policy changed; fresh approval/reconciliation required')
 reviewed_path=ROOT/('docs/company-resolutions/AAPL/implementation-2026-11-03/evidence-ledger.json' if p['ticker']=='AAPL' else 'docs/company-resolutions/META/implementation-2026-11-03/review-results.json')
 tax.append({'ticker':p['ticker'],'baseline_git_commit':p['source_git_commit'],'baseline_policy_sha256':p['source_git_blob_sha256'],'current_policy_path':p['path'],'current_policy_sha256':sha(path),'configuration_before':before,'configuration_after':after,'annual_tax_before':before_path,'annual_tax_after':after_path,'terminal_tax_before':before['terminal_tax'],'terminal_tax_after':after['terminal_tax'],'annual_parameter_differences':['0']*5,'terminal_parameter_difference':'0','numeric_inputs_changed':False,'expected_tax_policy_only_ev_change_usd':'0','ev_claim_limit':'Separate controlled Base/Bear/Bull run_case output parity is retained in valuation-parity.json. This numerical parity does not certify the economic assumptions.','source_fact':False,'classification':'REVIEWED_EXPLICIT_OPERATING_TAX_CONVENTION','review_record':str(reviewed_path.relative_to(ROOT)),'review_record_sha256':sha(reviewed_path)})
result={'schema_version':'three-company-partial-sbc-basis-bridge-v1','scope':'AAPL/META/GOOGL original FY2021–FY2025 annual windows','issue':'S1','parent_status':'OPEN','historical_values_modified':False,'forecasts_modified':False,'source_points_verified':len(allrows)*2,'periods':allrows,'tax_policy_comparison':tax,'source_manifest':list(source_refs.values()),'input_sha256':inputs,'implementation':'Reported CFO is preserved. The separate diagnostic subtracts only the exact SBC add-back already included in CFO once. This restores that named expense component arithmetically while retaining historical tax/other accounting differences. It does not establish a fully valuation-aligned series or cash paid to employees.'}
(HERE/'schedules.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
with (HERE/'schedules.csv').open('w',newline='') as f:
 names=['ticker','fiscal_year','reported_cfo_usd','reported_sbc_addback_usd','sbc_reversal_usd','cfo_after_sbc_reversal_usd','historical_change_usd','status'];w=csv.DictWriter(f,fieldnames=names);w.writeheader()
 for p in allrows:w.writerow({'ticker':p['ticker'],'fiscal_year':p['fiscal_year'],'reported_cfo_usd':p['reported_cfo']['amount_usd'],'reported_sbc_addback_usd':p['reported_sbc_addback']['amount_usd'],'sbc_reversal_usd':p['sbc_addback_reversal']['amount_usd'],'cfo_after_sbc_reversal_usd':p['cfo_after_reversing_reported_sbc_addback']['amount_usd'],'historical_change_usd':p['historical_change_usd'],'status':p['status']})
print('Built15partialSBCbridges,30exactCFO/SBCsourcepoints,2unchangedtaxpolicycomparisons')
