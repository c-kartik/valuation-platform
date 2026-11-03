"""Exact, offline Meta M1–M3 schedules. No source-bank or runtime writes.
Run with the repository Python. Downloads are a separate extend_primary_review.py step.
"""
import csv,gzip,hashlib,json,re
from decimal import Decimal,localcontext
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
OLD=HERE.parent/'research'
def sha(b):return hashlib.sha256(b).hexdigest()
class Inline(HTMLParser):
 def __init__(self):super().__init__();self.facts=[];self.current=[]
 def handle_starttag(self,t,a):
  if t=='ix:nonfraction':
   self.current.append({'attrs':dict(a),'pieces':[]})
 def handle_endtag(self,t):
  if t=='ix:nonfraction':
   fact=self.current.pop();fact['text']=''.join(fact.pop('pieces'));self.facts.append(fact)
 def handle_data(self,d):
  for fact in self.current:fact['pieces'].append(d)
def parse(body):
 text=body.decode();p=Inline();p.feed(text);ctx={}
 for m in re.finditer(r'<xbrli:context\b[^>]*id="([^"]+)"[^>]*>(.*?)</xbrli:context>',text,re.S):
  c=m.group(2)
  def date(tag):
   q=re.search(r'<xbrli:'+tag+r'>(.*?)</xbrli:'+tag+r'>',c);return q.group(1) if q else None
  ctx[m.group(1)]={'start':date('startDate'),'end':date('endDate'),'instant':date('instant'),'dimensions':re.findall(r'<(?:xbrldi:)?explicitMember\b[^>]*>(.*?)</(?:xbrldi:)?explicitMember>',c,re.S)}
 for n,f in enumerate(p.facts):
  a=f['attrs'];f['context']=ctx.get(a.get('contextref'));f['ordinal']=n
  raw=f['text'].strip().replace(',','').replace('\u2212','-').replace('−','-')
  if raw in ('—','–','-','') or a.get('format')=='ixt:fixed-zero':raw='0'
  raw=raw.replace(' ','').replace('\n','').replace('\xa0','')
  if a.get('unitref','').lower() not in ('usd','usd1'):f['amount']=None;continue
  try:f['amount']=str(Decimal(raw)*(Decimal(10)**int(a.get('scale','0')))*(-1 if a.get('sign')=='-' else 1))
  except Exception as e:raise ValueError((raw,a)) from e
 return p.facts
sources={}
for s in json.loads((OLD/'source-manifest.json').read_text())['sources']:
 if s['source_type']!='SEC 10-K':continue
 b=(OLD/s['local_file']).read_bytes();b=gzip.decompress(b) if s.get('storage_encoding')=='gzip' else b
 assert sha(b)==s['sha256'];sources[s['id']]={'body':b,'facts':parse(b),'record':dict(s,path=str((OLD/s['local_file']).relative_to(REPO)))}
for s in json.loads((HERE/'retrieval-manifest.json').read_text())['sources']:
 if '-10q' not in s['id']:continue
 b=gzip.decompress((HERE/s['file']).read_bytes());assert sha(b)==s['sha256'];sources[s['id']]={'body':b,'facts':parse(b),'record':dict(s,path=str((HERE/s['file']).relative_to(REPO)))}
for s in json.loads((REPO/'data/preload/meta-v1/sources/manifest.json').read_text())['sources']:
 if s['id']!='q3-2026-10q':continue
 p=REPO/'data/preload/meta-v1/sources'/s['file'];b=p.read_bytes();assert sha(b)==s['sha256'];sources[s['id']]={'body':b,'facts':parse(b),'record':dict(s,path=str(p.relative_to(REPO)))}
points=[]
def point(sid,names,start,end,expected=None,dimensions=(),instant=None):
 if isinstance(names,str):names=[names]
 matches=[f for f in sources[sid]['facts'] if f['attrs'].get('name') in names and f['context'] and f['context']['start']==start and f['context']['end']==end and f['context']['instant']==instant and f['context']['dimensions']==list(dimensions) and f['attrs'].get('unitref','').lower() in ('usd','usd1')]
 if expected is not None:matches=[f for f in matches if Fraction(f['amount'])==Fraction(expected)]
 if not matches:raise ValueError((sid,names,start,end,expected,'No compatible inline point',[(f['attrs'],f['context'],f['amount']) for f in sources[sid]['facts'] if f['attrs'].get('name') in names]))
 vals={Fraction(f['amount']) for f in matches}
 if len(vals)!=1:raise ValueError((sid,names,start,end,'Competing source amounts'))
 out={'source_id':sid,'source_url':sources[sid]['record']['url'],'source_sha256':sources[sid]['record']['sha256'],'start':start,'end':end,'amount_usd':str(next(iter(vals))),'concepts':names,'occurrences':[{'ordinal':f['ordinal'],'attrs':f['attrs'],'display':f['text'],'context':f['context']} for f in matches]}
 points.append(out);return out
def money(p):return Fraction(p['amount_usd'])
def number(x):
 x=Fraction(x)
 with localcontext() as c:c.prec=40;d=str(Decimal(x.numerator)/Decimal(x.denominator))
 return {'fraction':{'numerator':str(x.numerator),'denominator':str(x.denominator)},'decimal':d}
start=lambda y:f'{y}-01-01'
end=lambda y:f'{y}-12-31'
# Preserve the existing exact five-year scope; inputs/results remain independently source-replayed by the controlling script.
prior=json.loads((HERE.parent/'results.json').read_text());periods=[]
for row in prior['periods']:
 y=row['fiscal_year'];sid=f'meta-{y}-10k';i=row['inputs']
 for field,names in {'cfo':'us-gaap:NetCashProvidedByUsedInOperatingActivities','tax_provision':'us-gaap:IncomeTaxExpenseBenefit','pretax_income':'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'}.items():point(sid,names,start(y),end(y),i[field])
 interest=point('meta-2023-10k' if y<2023 else sid,['us-gaap:InterestExpense','us-gaap:InterestExpenseNonoperating'],start(y),end(y),i['interest_expense'])
 cap=point(sid,'us-gaap:InterestCostsCapitalized',start(y),end(y),dimensions=('us-gaap:ConstructionInProgressMember',)) if y>=2023 else None
 cash=point('meta-2023-10k' if y<2023 else sid,'us-gaap:InterestPaidNet',start(y),end(y))
 lease_cash=point(sid,'us-gaap:FinanceLeaseInterestPaymentOnLiability',start(y),end(y))
 lease_expense=point(sid,'us-gaap:FinanceLeaseInterestExpense',start(y),end(y))
 tax=point(sid,'us-gaap:IncomeTaxesPaidNet',start(y),end(y))
 current_tax=point(sid,'us-gaap:CurrentIncomeTaxExpenseBenefit',start(y),end(y),[7305000000,8896000000,8199000000,13040000000,6719000000][y-2021])
 deferred_tax=point(sid,['meta:TotalDeferredIncomeTaxExpenseBenefit','fb:TotalDeferredIncomeTaxExpenseBenefit','us-gaap:DeferredIncomeTaxExpenseBenefit'],start(y),end(y),[609000000,-3277000000,131000000,-4737000000,18755000000][y-2021])
 assert money(current_tax)+money(deferred_tax)==Fraction(i['tax_provision'])
 financing=row['financing'];unknown=financing['unallocated_other_usd'];assert len(unknown)==1
 periods.append({'fiscal_year':y,'cashflow_basis':'reported CFO; cash PP&E net of identified receipts; after-tax expensed interest convention','historical_fcff_usd':row['fcff']['amount_usd'],'historical_fcff_exact_fraction_usd':row['fcff']['exact_fraction_usd'],'provisional_fcfe_usd':row['fcfe']['amount_usd'],'parent_common_fcfe_usd':None,'unresolved_other_financing_usd':unknown[0],'net_borrowing_identified_usd':financing['net_borrowing']['amount_usd'],'financing_statement_tie_difference_usd':financing['statement_difference_usd'],'interest_expensed':interest,'interest_capitalized_incurred':cap,'cash_interest_excluding_capitalized':cash,'finance_lease_interest_cash_separately_reported':lease_cash,'finance_lease_interest_expense_separately_reported':lease_expense,'cash_interest_population_note':'The supplemental InterestPaidNet row is not proven to cover all financing cash; it reports0 in2021/22 while the lease note separately reports15/16M operating finance-lease cash. Keep populations separate, do not add without parent/child containment.','cash_interest_capitalized_usd':None,'capitalized_interest_investment_cash_adjustment_usd':None,'cash_tax':tax,'current_tax_expense_note':current_tax,'deferred_tax_expense_note':deferred_tax,'reported_tax_rate':number(Fraction(i['tax_provision'])/Fraction(i['pretax_income'])),'broader_unlevered_fcff_usd':None,'historical_change_usd':'0','m1_status':'OPEN_CLASSIFICATION','m2_status':'OPEN_CASH_TAX_INVESTMENT_ALIGNMENT'})
# Exact source-bound YTD checks and reclassification comparison.
quarter=[]
for y in range(2021,2026):
 for mm,dd in [('03','31'),('06','30'),('09','30')]:
  date=f'{y}-{mm}-{dd}';sid=f'meta-{date}-10q';other=point(sid,'us-gaap:ProceedsFromPaymentsForOtherFinancingActivities',start(y),date)
  od=point(sid,'us-gaap:ProceedsFromRepaymentsOfBankOverdrafts',start(y),date) if y<=2022 else None
  quarter.append({'date':date,'other':other,'overdraft':od,'other_plus_overdraft_usd':str(money(other)+(money(od) if od else 0)),'overdraft_absent_does_not_establish_zero':od is None})
comparisons=[]
for mm,dd in [('03','31'),('06','30'),('09','30')]:
 old=next(r for r in quarter if r['date']==f'2022-{mm}-{dd}');later=point(f'meta-2023-{mm}-{dd}-10q','us-gaap:ProceedsFromPaymentsForOtherFinancingActivities','2022-01-01',f'2022-{mm}-{dd}')
 assert money(later)==Fraction(old['other_plus_overdraft_usd'])
 comparisons.append({'period_end':f'2022-{mm}-{dd}','old_other_usd':old['other']['amount_usd'],'old_overdraft_usd':old['overdraft']['amount_usd'],'later_other_usd':later['amount_usd'],'later_source':later,'difference_usd':'0','annual_debt_change_justified_usd':None})
# Isolate the FY2025 tax event, not all of it is a nonrecurring cash tax.
provision=Fraction(prior['periods'][-1]['inputs']['tax_provision']);pretax=Fraction(prior['periods'][-1]['inputs']['pretax_income'])
charge=point('meta-2025-10k','meta:IncomeTaxExpenseBenefitDiscreteChargeRelatedToNewLegislation','2025-07-01','2025-09-30')
va=point('meta-2025-10k','meta:DeferredTaxAssetsValuationAllowanceDiscreteChargeRelatedToNewLegislation',None,None,instant='2025-12-31')
ytdtax=point('q3-2026-10q','us-gaap:IncomeTaxExpenseBenefit','2026-01-01','2026-09-30','1028000000')
ytdpre=point('q3-2026-10q','us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest','2026-01-01','2026-09-30','53509000000')
# Source text names8.03bn discrete benefit. It is a reported contextual amount, not a changed historical input.
benefit=point('q3-2026-10q','meta:IncomeTaxExpenseBenefitDiscreteChargeRelatedToNewLegislation','2026-01-01','2026-03-31','-8030000000')
policy=json.loads((REPO/'data/preload/meta-v1/policy.json').read_text())
assert (policy['configuration']['tax_start'],policy['configuration']['tax_endpoint'],policy['configuration']['terminal_tax'])==('0.16','0.20','0.20')
taxreview={'reported2025_provision_usd':str(provision),'reported2025_pretax_usd':str(pretax),'obbba_charge':charge,'noncash_valuation_allowance_charge':va,'other_obbba_charge_derived_usd':str(money(charge)-money(va)),'reported2025_etr':number(provision/pretax),'2025_etr_excluding_only_non_cash_va':number((provision-money(va))/pretax),'2025_etr_excluding_entire_obbba_charge_diagnostic_not_selected':number((provision-money(charge))/pretax),'2026_ytd_reported_tax':ytdtax,'2026_ytd_pretax':ytdpre,'2026_ytd_discrete_benefit':benefit,'2026_ytd_reported_etr':number(money(ytdtax)/money(ytdpre)),'2026_ytd_etr_before_named_discrete_benefit_context_not_operating_tax':number((money(ytdtax)-money(benefit))/money(ytdpre)),'selected_forward_policy':{'classification':'EXPLICIT_MODELLING_CONVENTION_REAFFIRMED_UNDER_APPROVED_TAX_REVIEW','operating_tax_annual':{'2026':'0.16','2027':'0.17','2028':'0.18','2029':'0.19','2030':'0.20'},'terminal_tax':'0.20','guide_context':'Latest retained Q3 2026 filing guides Q4 2026 consolidated ETR15–17%;16% midpoint is contextual support, not reported unlevered annual tax. Long-run20% and fade remain explicit analyst assumptions.','historical_cfo_change_usd':'0','numeric_preload_change':False,'ev_change_from_this_policy_review_usd':'0','no_automatic_charge_addback':True,'no_automatic_reversal_copy':True},'source_policy_sha256':sha((REPO/'data/preload/meta-v1/policy.json').read_bytes())}
result={'schema_version':'meta-m1-m3-implementation-review-v1','date':'2026-11-03','parent_status':'OPEN','source_bank_modified':False,'runtime_modified_by_this_script':False,'historical_values_changed':False,'periods':periods,'quarterly_financing':quarter,'comparative_presentations':comparisons,'tax_review':taxreview,'open_issues':['M1: annual debt content in Other not completely disclosed; full-year cash-pool cash/FX/noncash roll-forward absent.','M2: incurred capitalized interest is disclosed in2023–25 but actual capitalized-interest cash and related tax/asset amortization not separately bound; broader unlevered replacement remains unavailable.'],'selected_policies':['Preserve reported cash basis; no invented interest-cash, debt residual or zero components.','Retain tax path16/17/18/19/20% andterminal20% as explicit analyst operating convention; no historical cash adjustment.']}
(HERE/'review-results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
(HERE/'numeric-source-points.json').write_text(json.dumps(points,indent=2)+'\n')
(HERE/'all-primary-source-manifest.json').write_text(json.dumps({'sources':[v['record'] for v in sources.values()]},indent=2)+'\n')
print('Built',len(periods),'annual periods,',len(quarter),'quarterlies,',len(points),'exact source points')
