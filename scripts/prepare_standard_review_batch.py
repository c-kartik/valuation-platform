"""Fixed retained COST/CAT/KO review, not financial acceptance or a resolver."""
from datetime import date
from decimal import Decimal
from pathlib import Path
import json
import re
import sys

from prepare_msft_analyst_package import Filing, InlineFacts, ROOT, digest, relevant, PROPOSED, SUPPORTED, inline_amount
from valuation_platform.analyst import cash_flow_inputs as cash, historical_inputs as h
from valuation_platform.analyst import retained_components as inspect, statement_delivery as documents
from valuation_platform.analyst import cfo_statement_reconciliation as cfo, preparation_delivery as delivery

BASELINE='7d0e3006f2d64691f4eb67c072ce6b5efbdbeff1'
TICKERS=('COST','CAT','KO')
LEDGER='docs/reported-population-delivery-ledger.json'
MANIFEST='docs/phase1-selected-filing-identity-manifest.json'
REVIEW_TIME='2026-10-17T17:09:55+00:00'
SPECS={
    'cfo':('NetCashProvidedByUsedInOperatingActivities',False),
    'da':('DepreciationDepletionAndAmortization',False),'depreciation':('Depreciation',False),
    'intangible_amortization':('AmortizationOfIntangibleAssets',False),'finance_amortization':('FinanceLeaseRightOfUseAssetAmortization',False),
    'sbc_expense':('AllocatedShareBasedCompensationExpense',False),'sbc_addback':('ShareBasedCompensation',False),
    'tax':('IncomeTaxExpenseBenefit',False),'pretax':('IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',False),
    'pretax_equity_scope':('IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments',False),
    'cash_tax':('IncomeTaxesPaidNet',False),'cash_tax_gross':('IncomeTaxesPaid',False),'cash_interest':('InterestPaidNet',False),'cash_interest_gross':('InterestPaid',False),
    'deferred_tax':('DeferredIncomeTaxExpenseBenefit',False),'deferred_movement':('IncreaseDecreaseInDeferredIncomeTaxes',False),
    'cash_capex':('PaymentsToAcquirePropertyPlantAndEquipment',False),'acquisition':('PaymentsToAcquireBusinessesNetOfCashAcquired',False),
    'investment_acquisitions':('PaymentsToAcquireBusinessesAndInterestInAffiliates',False),'sale_ppe':('ProceedsFromSaleOfPropertyPlantAndEquipment',False),
    'noncash_operating_rou':('RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability',False),
    'noncash_finance_rou':('RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability',False),
    'capital_creditors':('CapitalExpendituresIncurredButNotYetPaid',False),
    'cash':('CashAndCashEquivalentsAtCarryingValue',True),'current_investments':('ShortTermInvestments',True),
    'marketable_current':('MarketableSecuritiesCurrent',True),'marketable_long':('MarketableSecuritiesNoncurrent',True),
    'other_investments':('OtherLongTermInvestments',True),'equity_method':('EquityMethodInvestments',True),
    'other_current_investments':('OtherShortTermInvestments',True),'current_financial_parent':('CashCashEquivalentsAndShortTermInvestments',True),
    'restricted_cash':('RestrictedCashAndCashEquivalents',True),'restricted_cash_current':('RestrictedCashAndCashEquivalentsCurrent',True),
    'cash_restricted_parent':('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',True),
    'cp':('CommercialPaper',True),'short_borrowing':('ShortTermBorrowings',True),'debt_current':('LongTermDebtCurrent',True),
    'debt_long':('LongTermDebtNoncurrent',True),'debt_parent':('LongTermDebt',True),
    'debt_finance_parent':('LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities',True),
    'debt_finance_current':('LongTermDebtAndCapitalLeaseObligationsCurrent',True),'debt_finance_long':('LongTermDebtAndCapitalLeaseObligations',True),
    'other_short_borrowing':('OtherShortTermBorrowings',True),'gross_sbc_tax_benefit':('EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense',False),
    'net_sbc_expense':('AllocatedShareBasedCompensationExpenseNetOfTax',False),
    'op_lease':('OperatingLeaseLiability',True),'op_current':('OperatingLeaseLiabilityCurrent',True),'op_long':('OperatingLeaseLiabilityNoncurrent',True),
    'finance_lease':('FinanceLeaseLiability',True),'finance_current':('FinanceLeaseLiabilityCurrent',True),'finance_long':('FinanceLeaseLiabilityNoncurrent',True),
    'op_cash':('OperatingLeasePayments',False),'finance_interest_cash':('FinanceLeaseInterestPaymentOnLiability',False),'finance_principal_cash':('FinanceLeasePrincipalPayments',False),
    'op_lease_cost':('OperatingLeaseCost',False),'pension_expense':('DefinedBenefitPlanNetPeriodicBenefitCost',False),
    'retirement_expense':('DefinedContributionPlanCostRecognized',False),'pension_net':('DefinedBenefitPlanNetAssetLiability',True),
    'pension_liability':('DefinedBenefitPlanLiabilitiesNoncurrent',True),'preferred':('PreferredStockValue',True),
    'nci':('MinorityInterest',True),'redeemable_nci':('RedeemableNoncontrollingInterestEquityCarryingAmount',True),
    'postemployment_liability':('PensionAndOtherPostretirementAndPostemploymentBenefitPlansLiabilitiesNoncurrent',True),
    'nol_dta':('DeferredTaxAssetsTaxDeferredExpenseTaxLossCarryforwards',True),
    'equity':('StockholdersEquity',True),'total_equity':('StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',True)}


def monetary(case,key,concept,instant=False,namespace='us-gaap'):
    """Reuse structural inspection/primary context checks when XML IDs differ.

    ID equality is not invented: both actual locators remain, with exact QName,
    context, USD, amount and decimals checked against the independent primary.
    """
    f=case['filing']
    try:return f.fact(key,concept,'Exact selected statement/note observation; not automatic completeness',instant=instant,namespace=namespace)
    except (ValueError,KeyError) as original:
        ns=f.namespaces.get(namespace,namespace)
        result=inspect.inspect(case['evidence'],inspect.SelectionSpec(key,(inspect.Selector(ns,concept,()),),'instant' if instant else 'annual','USD','source_observation','Exact named retained population; no economic scope acceptance',()))
        if not result.candidates or result.competing_values:raise ValueError(str(original)) from original
        bindings=documents.primary_bindings(case['record']);occurrences=[]
        for candidate in result.candidates:
            for o in candidate.occurrences:
                node=f.root[o.ordinal];ctx=case['evidence'].contexts[o.context_id]
                parsed=next(v for v,i in case['evidence'].facts if i==o.ordinal);matches=[]
                for primary_id,(attrs,text) in f.inline.facts.items():
                    name=attrs.get('name','');prefix,_,local=name.partition(':')
                    if (f.namespaces.get(prefix)!=ns or local!=concept or attrs.get('contextref')!=o.context_id or attrs.get('unitref')!=o.unit_id or attrs.get('decimals')!=o.decimals):continue
                    documents.check_primary_binding(bindings,attrs,ns,ctx,parsed.unit)
                    try:value=inline_amount(attrs,text)
                    except ValueError:
                        if attrs.get('format') not in ('ixt:fixed-zero','ixt:zerodash') or Decimal(o.raw_value)!=0:continue
                        value=cfo.displayed(text,Decimal(0))
                    if value==Decimal(o.raw_value):matches.append(dict(primary_locator='inline#'+primary_id,primary_display=text,primary_scale=int(attrs.get('scale','0')),primary_sign=attrs.get('sign','+'),primary_format=attrs.get('format')))
                if not matches:raise ValueError('No independently bound primary QName/context/amount/precision for '+key)
                occurrences.append(dict(ordinal=o.ordinal,xml_id=node.get('id'),context_id=o.context_id,raw_value=o.raw_value,precision=o.decimals,unit_id=o.unit_id,start=str(o.start) if o.start else None,end=str(o.end),dimensions=[],primary_confirmations=matches,**matches[0]))
        value=result.candidates[0].value
        f.facts[key]=dict(concept=concept,namespace=ns,location='Exact independently bound note/statement population; XML ID differences explicitly retained',unit='USD',value=str(value),display_value=str(value/1000000),display_unit='USD millions',precision=occurrences[0]['precision'],precision_variants=sorted({o['precision'] for o in occurrences}),as_of=str(f.period.annual_end) if instant else None,occurrences=occurrences,occurrence_count=len(occurrences),primary_source='primary',instance_source='instance')
        return key


def observe(case):
    f=case['filing'];errors=[]
    for key,(concept,instant) in SPECS.items():
        try:monetary(case,key,concept,instant)
        except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
    # Select only the already inspected exact income populations; the primary
    # is independently checked here rather than copying the frozen result.
    income=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
    row=next(r for r in income['rows'] if r['identity']==case['identity'])
    for slot in row['fields']:
        if slot['status']!='POPULATED':continue
        candidate=slot['candidates'][slot['selected']]
        try:f.fact(slot['field'],candidate['concept'],'Existing direct income policy plus exact primary population')
        except (ValueError,KeyError) as exc:errors.append(dict(input_id=slot['field'],value=None,reason=str(exc)))
    # Explicit reviewed populations, not a substring-based financial resolver.
    extra={'COST':[(k,'us-gaap',co,None) for k,co in [('capital_lease_current','CapitalLeaseObligationsCurrent'),('capital_lease_long','CapitalLeaseObligationsNoncurrent')]],
        'CAT':[], 'KO':[(k,'ko',co,None) for k,co in [('combined_acquisitions','AcquisitionsOfBusinessesEquityMethodInvestmentsAndNonmarketableSecurities'),('irs_estimate','RecordedEstimateOfTaxLiability'),('irs_possible','IncrementalTaxAndInterestLiability')]]}.get(case['ticker'],[])
    if case['ticker']=='KO':
        extra += [(k,'ko',co,None) for k,co in [('held_sale_cash','DisposalGroupIncludingDiscontinuedOperationsCashCashEquivalentsAndShortTermInvestments'),
            ('held_sale_short','DisposalGroupIncludingDiscontinuedOperationLoansAndNotesPayable'),('held_sale_current_debt','DisposalGroupIncludingDiscontinuedOperationCurrentMaturitiesOfLongTermDebt'),
            ('held_sale_long_debt','DisposalGroupIncludingDiscontinuedOperationLongTermDebt')]]
        for member in ['PensionPlansDefinedBenefitMember','OtherPostretirementBenefitPlansDefinedBenefitMember']:
            for co in ['DefinedBenefitPlanFundedStatusOfPlan','DefinedBenefitPlanAmountsRecognizedInBalanceSheet','DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent','PensionAndOtherPostretirementDefinedBenefitPlansCurrentLiabilities','PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent']:
                extra.append((member+':'+co,'us-gaap',co,(('us-gaap:RetirementPlanTypeAxis','us-gaap:'+member),)))
    for key,ns,co,dims in extra:
        try:
            if dims:f.fact(key,co,'Exact note population; no netting or parent/child addition',namespace=ns,instant=True,dimensions=dims)
            else:monetary(case,key,co,key!='combined_acquisitions',ns)
        except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
    try:f.fact('reported_etr','EffectiveIncomeTaxRateContinuingOperations','Issuer reported accounting ETR, not forecast rate',unit='pure')
    except (ValueError,KeyError) as exc:errors.append(dict(input_id='reported_etr',value=None,reason=str(exc)))
    for key,co in [('weighted_basic','WeightedAverageNumberOfSharesOutstandingBasic'),('weighted_diluted','WeightedAverageNumberOfDilutedSharesOutstanding')]:
        try:f.fact(key,co,'Annual EPS denominator; not dated common shares/dilution estimate',unit='shares')
        except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
    for node in f.root:
        if not node.get('contextRef'):continue
        local=node.tag.split('}')[-1]
        if local not in ('CommonStockSharesOutstanding','EntityCommonStockSharesOutstanding','ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber'):continue
        context=f.contexts[node.get('contextRef')];end=context.findtext(cash._XI+'period/'+cash._XI+'instant')
        if not end or (local!='EntityCommonStockSharesOutstanding' and end!=str(f.period.annual_end)):continue
        dims=tuple((x.get('dimension'),x.text) for x in context.iter() if x.tag.endswith('}explicitMember'))
        namespace=node.tag[1:].split('}')[0];key='shares:'+local+':'+end+':'+digest(dims)[:8]
        if key in f.facts:continue
        try:f.fact(key,local,'Actual dated/classed shares or awards; no aggregation/dilution',instant=True,namespace=namespace,unit='shares',as_of=end,dimensions=dims)
        except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
    return errors


def decisions(package):
    ticker=package['ticker'];rows=package['periods']
    def values(key,calc=False):
        out=[]
        for r in rows:
            item=next((x for x in r['calculations'] if x['input_id']==key),{}) if calc else r['facts'].get(key,{})
            out.append(str(Decimal(item['value'])/1000000) if item.get('value') is not None else 'unknown')
        return '/'.join(out)+' USDm'
    shared=[('CF','Use source-bound reported CFO and displayed movements; no separate residual scalar or second movement deduction.',values('cfo'),
        'Alternative require supported mixed-row allocations, not a residual plug. Consolidated CFO is not organic/unlevered cash; acquisitions/FX/reclasses retain stated scopes. COST FY2023-25 mixed impairment/deferred-tax/other row does not establish pure deferred taxes; propose no separate pure-CFO-deferred operation, source amount remains unknown.' if ticker=='COST' else 'Alternative require separately evidenced allocations. Mixed rows stay mixed; no zero, book delta NWC or extra deductions. CFO may include material nonrecurring/acquisition/financing-business effects.'),
        ('DA','Select a labeled limited historical D&A proxy; retain expense/impairment/ROU observations separately.',values('limited_finance_inclusive_da_proxy',True) if ticker=='COST' else values('da'),
        'COST proposes D&A + separately reported finance amortization, supported by separate CFO lease-ROU line and finance assets in other noncurrent assets, with explicit non-overlap assumption. Alternative D&A-only1900/2077/2237/2426/2674 omits128/169/97/102/106; never add operating ROU. Complete expense D&A unknown.' if ticker=='COST' else 'CAT consolidated proxy includes leased-to-others/Financial Products depreciation; industrial supplemental1550/1439/1361/1368/1497 is a DIFFERENT perimeter, not a substitute without CAT-PERIMETER. KO depreciation includes finance assets; no extra finance amortization or subtraction-based intangible estimate. CFO versus expense-basis completeness unproved.'),
        ('SBC','Use recognized gross SBC expense as labeled cost proxy once; preserve add-back/mixed CFO roles.',values('gross_sbc_expense',True) if ticker=='COST' else values('sbc_expense'),
        'COST derives gross note expense from net expense + related expense tax benefit, not exercise cash benefits. KO expense337/361/251/286/279 differs from CFO337/356/254/286/279, no plugs. CAT expense200/193/208/223/242 is separately reported; no invented standalone add-back from Other. Alternative keep reported expense only without economic-cost proxy; awards remain separate.'),
        ('CASH','Select gross named current financial balances only; retain restrictions, strategic/insurance holdings and alternatives separately.',values('cash') if ticker=='CAT' else values('gross_current_financial',True),
        'Not unrestricted/excess cash; unknown reserves/restrictions remain. CAT consolidated cash versus industrial8428/6042/6106/6165/9333 requires perimeter choice; do not move Financial Products cash into industrial balances. KO restrictedcash138/455/326/660/740 and equity-method holdings remain separate; held-sale populations are not automatically added. Alternative no liquid-balance selection pending reserve restrictions.'),
        ('FIN','Use source-named carrying borrowing/finance populations, operating LESSEE leases service and finance LESSEE leases asset financing, with no unidentified-borrowing adjustment only if expressly approved. CAT lessor receivables/leased-to-others assets remain financing-business operations, not lessee debt adjustments.',values('named_borrowing_consolidated',True) if ticker=='CAT' else values('named_financing',True),
        'CAT consolidated/industrial/Financial Products columns and eliminations must remain separate; do not deduct funding debt without its financing assets. COST FY2022 known short borrowing88 is included, not omitted; finance note245+1383,129+1303,147+1351,78+1401,94+1319 is outside term debt. KO named reported long-term borrowing parent is not certified complete finance-lease coverage merely from its tag name; no duplicate CP or unproved lease addition. FY2025 held-sale loans187/current debt398/long debt850 remain separate recognized populations; expanded46927 alternative depends on their separate balance-sheet classification, not adding all held-sale liabilities1437. Missing finance coverage/other borrowing stays unquantified, no immateriality inference. Alternative retain requirement pending a broader defensible perimeter.'),
        ('CLAIMS','Retain known NCI, pension/benefit and other claims separately without parent/child netting; propose no additional unidentified claim adjustment.',values('nci')+'; postemployment '+values('postemployment_liability'),
        'Potential unidentified claims unbounded; no immateriality assumption. COST retirement824/889/963/1061/1174 includes international plans: source says some immaterial, not valuation proof; no funded-status allocation. CAT recognized postemployment5592/4203/4098/3757/3838 remains. KO pension net assets325/782/716/390/295 and OPEB liabilities277/122/121/116/112 plus gross recognized components are separate, not netted; IRS/contingent consideration/held-sale claims remain, no automatic valuation deduction. Alternative leave unspecified-claim operation unresolved.'),
        ('SHARES','Select the actual fiscal-end reported common population; preserve cover date/class observations, EPS and awards separately. No automatic class sum/dilution.',
         'Exact dated shares/awards in each period facts; no numerical dilution estimate.',
         'COST unclassed and CommonClassA confirmations have the same amount, not additional shares. CAT/KO common observations and separately dated cover counts are not interchangeable. Alternative retain class/date scope unresolved; no forecast shares/award valuation approved.')]
    if ticker=='CAT':
        shared=[('PERIMETER','Do NOT approve generic consolidated operating-company preparation. Retain consolidated history as descriptive; propose separate industrial and captive-financing historical perimeters using supplemental columns, with intercompany eliminations explicit.',
            'Consolidated CFO7198/7766/12885/12035/11739 versus industrial7177/6358/11688/11437/12278. Named borrowing37789/36993/37878/38409/43330 versus industrial9826/9652/9670/8777/10990 and Financial Products27989/27372/28255/29799/33617.',
            'Alternative a specifically approved consolidated financial-services-inclusive contract, not ordinary operating-only inputs. Neither is active; do not reconstruct standalone figures by subtraction. Financial-products receivables, leased assets, funding and eliminations change economics. Source2025 industrial caption changes to Machinery, Power & Energy; retain accession-specific names.'),
            ('TAX','Retain reported provision and issuer ETR with its before-tax/equity-affiliate scope; leave the generic denied denominator/ETR unchanged.',values('pretax_equity_scope')+'; issuer ETR ratios in facts/reported_etr',
             'Generic pretax policy excludes this before-equity-affiliate concept; after-tax affiliate income must not be added without a supported tax bridge. Alternative approve a separately scoped historical ratio only; no new generic resolver/rate/forecast assumption.')]+shared
    return [dict(decision_id=ticker+'-'+key,ticker=ticker,identities=[r['identity'] for r in rows],recommendation=rec,numerical_effect=n,
        uncertainty_and_alternative=alt,evidence_references=[f'docs/company-data-preparation/{ticker.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)],
        status=PROPOSED,accepted=False,author=package['review_author'],recorded_at_utc=REVIEW_TIME) for key,rec,n,alt in shared]


def passages(f):
    out=[]
    for marker in ['Property and Equipment','depreciation and amortization','Amortization expense related','Amortization of lease assets','OperatingandFinancing',
        'components of lease expense','Total lease liabilities','short-term borrowings','Short-Term Borrowings','Loans and Notes Payable',
        'retirement plans','Obligations and Funded Status','Net asset (liability) recognized','no shares issued and outstanding','Total noncontrolling interests',
        'net of related tax benefits','net of tax benefits','stock-based compensation expense','restricted cash','membership fees',
        '53-week','Financial Products','Supplemental Data for Financial Position','Supplemental Data for Cash Flow',
        'Supplemental Data for Statement of Cash Flow','IRS','litigation deposit','contingent consideration','fairlife','held for sale','$6.1 billion','IRS Tax Litigation Deposit','interest income of $ 217']:
        match=re.search(r'(?<!\w)'+re.escape(marker)+r'(?!\w)',f.text,re.I)
        if match:out.append(dict(marker=marker,offset=match.start(),exact_excerpt=f.text[max(0,match.start()-90):match.end()+1800],source_sha256=f.primary.artifact.sha256))
    return out


def supplemental(case):
    if case['ticker']!='CAT':return []
    out=[];f=case['filing']
    for ti,table in enumerate(documents.parse(case['record'],improved=True)):
        header=' '.join(c['text'] for row in table[:6] for c in row)
        if 'Supplemental Data for' not in header or not ('Financial Position' in header or 'Cash Flow' in header):continue
        if 'FinancialProducts' not in header or 'Consolidating' not in header or 'Machinery' not in header:continue
        for ri,row in enumerate(table):
            caption=row[0]['text'].strip() if row else ''
            allowed=['Cash and cash equivalents','Short-term borrowings','Long-term debt due within one year','Long-term debt due after one year',
                'Depreciation and amortization','Net cash provided by (used for) operating activities','Capital expenditures—excluding equipment leased to others','Capital expenditures - excluding equipment leased to others',
                'Expenditures for equipment leased to others','Expenditures for equipment leased to others, net']
            if caption not in allowed:continue
            numbers=[]
            for ci,cell in enumerate(row[1:],1):
                token=cell['text'].strip()
                if re.fullmatch(r'\(?[\d,]+\)?|—|–|-',token):numbers.append((ci,token))
            if len(numbers)<6:raise ValueError('Supplemental current/prior population columns unavailable')
            values={}
            for scope,j in [('consolidated',0),('industrial',2),('financial_products',4)]:
                ci,token=numbers[j];value=cfo.displayed(token,Decimal(0))*1000000
                values[scope]=dict(value_usd=str(value),column=ci,display=token)
            out.append(dict(caption=caption,origin='reported',representation='primary_note_table_not_fabricated_XBRL',unit='USD',precision='-6',
                table=ti,row=ri,header=header,display_cells=[cell['text'] for cell in row],values=values,
                source_url=f.primary.artifact.url,source_sha256=f.primary.artifact.sha256,scope='Supplemental consolidating columns; eliminations/intercompany relationships remain; not standalone financials'))
    if not out:raise ValueError('Retained CAT supplemental populations unavailable')
    return out


def cost_lease_note(case):
    if case['ticker']!='COST':return []
    f=case['filing'];out=[]
    for ti,table in enumerate(documents.parse(case['record'],improved=True)):
        flat=' '.join(c['text'] for row in table for c in row)
        if len(table)>30 or 'Total lease liabilities' not in flat or 'Finance lease' not in flat or 'Operating lease' not in flat:continue
        years=[c['text'].strip() for row in table[:3] for c in row if re.fullmatch(r'20\d{2}',c['text'].strip())]
        if not years or years[0]!=str(f.year):raise ValueError('Lease note first column is not exact selected fiscal year')
        scope=None
        for ri,row in enumerate(table):
            caption=row[0]['text'] if row else ''
            if caption in ('Current','Long-term'):scope=caption
            if not caption.startswith('Finance lease liabilities'):continue
            if scope not in ('Current','Long-term'):raise ValueError('Lease note lacks current/noncurrent heading')
            cells=[(ci,c['text'].strip()) for ci,c in enumerate(row[1:],1) if re.fullmatch(r'\(?[\d,]+\)?|—|–|-',c['text'].strip())]
            if not cells:raise ValueError('Lease note numeric cell absent')
            ci,display=cells[0];value=cfo.displayed(display,Decimal(0))*1000000;key='finance_note_'+('current' if scope=='Current' else 'long')
            note=dict(table=ti,row=ri,column=ci,caption=caption,section=scope,display=display,display_cells=[c['text'] for c in row],header=years,source_url=f.primary.artifact.url,source_sha256=f.primary.artifact.sha256)
            f.facts[key]=dict(value=str(value),unit='USD',precision='-6',as_of=str(f.period.annual_end),origin='reported',representation='primary_note_table_not_XBRL',occurrences=[],occurrence_count=0,note_evidence=note)
            out.append(note)
    if len(out)!=2:raise ValueError('Unique two-part finance lease note required')
    return out


def build():
    cases,missing=load();packages={};all_decisions=[]
    for case in cases:
        f=case['filing'];errors=observe(case);ticker=case['ticker'];year=f.year
        reconciliation=delivery.plain(cfo.inspect_statement(case['evidence'],case['record'],version=cfo.IMPROVED_VERSION))
        if reconciliation!=case['proof']['reconciliation']:raise ValueError('Committed independent CFO replay differs: '+case['identity']['accession'])
        pop=reconciliation['populations'][0];notes=supplemental(case);lease_notes=cost_lease_note(case)
        def calc(key,operands,coefficients=None,scope='',status=SUPPORTED,origin=None):
            if any(k not in f.facts for k in operands):return
            f.entry(key,key,operands,coefficients,status=status,scope=scope,rationale='Exact named source arithmetic; no financial acceptance',origin=origin)
            f.entries[-1]['formula_version']='retained-standard-review-batch-v1'
        if ticker=='COST':
            calc('gross_current_financial',['cash','current_investments'],scope='Cash/equivalents + reported short-term investments; no unrestricted/excess claim')
            calc('limited_finance_inclusive_da_proxy',['da','finance_amortization'],status=PROPOSED,origin='proxy',scope='Limited D&A plus separately disclosed finance amortization; proposed non-overlap assumption; excludes operating lease service amortization')
            calc('gross_sbc_expense',['net_sbc_expense','gross_sbc_tax_benefit'],scope='Note recognized expense net of tax plus related expense tax benefit, not cash exercise benefit')
            finance=['finance_note_current','finance_note_long']
            short=['other_short_borrowing'] if 'other_short_borrowing' in f.facts else []
            calc('named_financing',['debt_current','debt_long']+finance+short,status=PROPOSED,scope='Named net term debt + directly disclosed finance liabilities + known short borrowing; unquantified borrowing not inferred zero')
        elif ticker=='KO':
            calc('gross_current_financial',['cash','other_current_investments'],scope='Reported current cash plus other short-term investments; restrictions/held-sale/strategic excluded')
            debt=['debt_finance_parent'] if 'debt_finance_parent' in f.facts else ['debt_current','debt_long']
            short=['short_borrowing'] if 'short_borrowing' in f.facts else ['cp','other_short_borrowing']
            calc('named_financing',debt+short,status=PROPOSED,scope='Named reported term carrying + short borrowing; tag name does not certify lease scope. CP not added again to parent; known held-sale borrowing separate')
            calc('held_sale_named_borrowing',['held_sale_short','held_sale_current_debt','held_sale_long_debt'],scope='Separate recognized held-sale borrowing captions, not all held-sale liabilities')
        else:
            mapping={'cash':'Cash and cash equivalents','short':'Short-term borrowings','current_debt':'Long-term debt due within one year','long_debt':'Long-term debt due after one year','cfo':'Net cash provided by (used for) operating activities'}
            for key,caption in mapping.items():
                row=next((x for x in notes if x['caption']==caption),None)
                if row and key in ('cash','cfo') and Decimal(row['values']['consolidated']['value_usd'])!=Decimal(f.facts[key]['value']):raise ValueError('CAT supplemental/consolidated source amount differs')
            for scope in ['consolidated','industrial','financial_products']:
                rows=[next((x for x in notes if x['caption']==mapping[k]),None) for k in ['short','current_debt','long_debt']]
                if all(rows):f.entries.append(dict(input_id='named_borrowing_'+scope,value=str(sum((Decimal(x['values'][scope]['value_usd']) for x in rows),Decimal(0))),unit='USD',origin='derived',status=PROPOSED,
                    operands=[dict(caption=x['caption'],table=x['table'],row=x['row'],**x['values'][scope]) for x in rows],precision='-6',scope='Named supplemental borrowing components, not complete debt; not summed across scopes',formula='LINEAR_COMPONENTS',formula_version='retained-standard-review-batch-v1'))
        movements=[x for x in pop['rows'] if x.get('role')=='displayed_movement']
        from valuation_platform.analyst.historical_inputs import Field
        review_ids={'depreciation_amortization':'DA','stock_based_compensation':'SBC','unclassified_cfo_reconciliation_residual':'CF','cash_investment_components':'CASH','debt_lease_components':'FIN','other_equity_bridge_claims_assets':'CLAIMS','point_in_time_shares':'SHARES'}
        checklist=[]
        family_keys={'revenue':['revenue'],'ebit':['ebit'],'depreciation_amortization':['da','depreciation','intangible_amortization','finance_amortization'],
            'cash_capex':['cash_capex'],'reported_cash_flow_working_capital_movements':[],
            'deferred_taxes':['deferred_tax','deferred_movement'],'stock_based_compensation':['sbc_expense','sbc_addback','net_sbc_expense','gross_sbc_tax_benefit'],
            'unclassified_cfo_reconciliation_residual':[],'reported_cfo':['cfo'],'reported_tax_context':['tax','pretax','pretax_equity_scope','reported_etr','cash_tax','cash_tax_gross'],
            'cash_investment_components':['cash','current_investments','other_current_investments','restricted_cash','equity_method'],
            'debt_lease_components':['short_borrowing','other_short_borrowing','cp','debt_current','debt_long','debt_finance_parent','finance_note_current','finance_note_long','op_lease'],
            'other_equity_bridge_claims_assets':['nci','redeemable_nci','postemployment_liability','retirement_expense','preferred','irs_estimate','irs_possible'],
            'point_in_time_shares':[k for k in f.facts if k.startswith('shares:')]}
        for field in Field:
            required=[ticker+'-'+review_ids[field.value]] if field.value in review_ids else []
            if ticker=='CAT':required=['CAT-PERIMETER']+required
            if field is Field.TAX and ticker=='CAT':required.append('CAT-TAX')
            if field is Field.DEFERRED_TAX and ticker=='COST' and year in (2023,2024,2025):required.append('COST-CF')
            status='PROPOSED_PENDING_APPROVAL' if required else 'SOURCE_SUPPORTED'
            references=['/facts/'+k for k in family_keys[field.value] if k in f.facts]
            if field in (Field.CFO,Field.CF_WORKING_CAPITAL,Field.CFO_RESIDUAL,Field.DEFERRED_TAX):references.append('/cfo_reconciliation')
            checklist.append(dict(field=field.value,status=status,pending_decisions=required,period_relative_evidence_references=references,financial_complete=False))
        period=dict(identity=case['identity'],selection_reference=case['manifest_reference'],prior_population_reference=case['proof_reference'],sources=case['sources'],facts=f.facts,calculations=f.entries,
            source_binding_exceptions=errors,passages=passages(f),supplemental_populations=notes,lease_note_populations=lease_notes,cfo_reconciliation=reconciliation,movement_rows=movements,
            precision='Raw source decimal precision retained in facts/rows; arithmetic never improves it',family_checklist=checklist,
            original_supporting_unknowns=dict(complete_expense_da=None,complete_reinvestment=None,additional_borrowing=None,unknown_cash_restrictions=None,operating_reserve=None),
            new_assumptions_active=False,analyst_complete=False)
        period['cash_sign_multipliers']={k:-1 for k in ['cash_capex','cash_tax','cash_tax_gross','cash_interest','cash_interest_gross','op_cash','finance_interest_cash','finance_principal_cash','acquisition','investment_acquisitions','combined_acquisitions'] if k in f.facts}
        if 'sale_ppe' in f.facts:period['cash_sign_multipliers']['sale_ppe']=1
        period['income_perimeter']=('Reported total revenue includes membership fees; not merchandise net sales alone' if ticker=='COST' else 'Consolidated includes Financial Products; supplemental industrial/financing and eliminations are different scopes, not standalone' if ticker=='CAT' else 'Reported net operating revenue/operating income; equity-method returns, refranchising and exceptional operating charges not normalized')
        packages.setdefault(ticker,dict(schema='company-analyst-review-v1',version=1,ticker=ticker,source_commit=BASELINE,review_author='Analyst preparation review; all judgments pending user approval',review_recorded_at_utc=REVIEW_TIME,periods=[],new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(period)
    for ticker,package in packages.items():
        package['periods'].sort(key=lambda r:r['identity']['annual_end'])
        package['family_slots']=70;package['evidence_acquisition_requirements']=[x for x in missing if x['ticker']==ticker]
        package['approval_table_reference']='docs/company-data-preparation/standard-review-batch.json#/decisions'
        package['decision_ids']=[x['decision_id'] for x in decisions(package)]
        package['scope_gate']='CAPTIVE_FINANCE_PERIMETER_PENDING' if ticker=='CAT' else 'CONSOLIDATED_HISTORICAL_PROPOSALS_PENDING'
        package['remaining_essential_requirements']=['Explicit company-specific approval of listed proxy/classification/omission treatments; acknowledgement alone cannot fill source nulls.']
        if ticker=='CAT':package['remaining_essential_requirements'].append('Approve an industrial/captive-financing historical perimeter and essential allocation/claim relationships, or keep CAT outside generic operating-only completion. Consolidated observations alone do not satisfy that requirement.')
        package['outcomes']={s:sum(c['status']==s for r in package['periods'] for c in r['family_checklist']) for s in ['SOURCE_SUPPORTED','PROPOSED_PENDING_APPROVAL']}
        package['review_revision']=digest(relevant(package))
    return packages,missing


def load(tickers=TICKERS):
    """Join only the fifteen existing selected proof bindings to actual receipts."""
    ledger=json.loads((ROOT/LEDGER).read_text());manifest=json.loads((ROOT/MANIFEST).read_text())
    income=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
    selected=[]
    for i,r in enumerate(income['rows']):
        if r['issuer'] not in tickers:continue
        matches=[(j,m) for j,m in enumerate(manifest['rows']) if m['identity']['accession']==r['identity']['accession']]
        if r['issuer'] not in ('COST','META') and (len(matches)!=1 or matches[0][1]['identity']!=r['identity']):raise ValueError('Frozen manifest/income join differs')
        selected.append((r['identity_reference'],dict(ticker=r['issuer'],identity=r['identity'])))
    if len(selected)!=15 or any(sum(r['ticker']==t for i,r in selected)!=5 for t in tickers):raise ValueError('Fixed fifteen selected periods required')
    proofs={r['identity']['fields']['accession']:(i,r) for i,r in enumerate(ledger['rows']) if r['ticker'] in tickers}
    needed={(s['url'],s['body_reference']) for i,r in proofs.values() for s in r['reconciliation']['populations'][0]['cfo']['sources']}
    catalog={key:[] for key in needed}
    for path in sorted((ROOT/'docs/evidence').glob('*.json')):
        doc=json.loads(path.read_bytes());artifacts=doc if isinstance(doc,list) else doc.get('artifacts',[])
        if not isinstance(artifacts,list):continue
        for i,a in enumerate(artifacts):
            key=(a.get('source_url'),a.get('sha256'))
            if key not in needed or not a.get('response_body_gzip_base64'):continue
            if a.get('representation')!='sec_response_body_bytes' or a.get('digest_type')!='sha256_sec_response_body_bytes':continue
            encoded=a['response_body_gzip_base64'];body=cash.gzip.decompress(cash.base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded,validate=True))
            catalog[key].append(dict(artifact=a,body=body,path=str(path.relative_to(ROOT)),pointer='/artifacts/'+str(i)))
    result=[];missing=[]
    for mi,row in selected:
        identity=row['identity'];pi,proof=proofs[identity['accession']];refs=proof['reconciliation']['populations'][0]['cfo']['sources'];bound=[]
        for role in ('primary','instance'):
            ref=next(s for s in refs if s['url'].endswith('_htm.xml')==(role=='instance'))
            candidates=catalog[(ref['url'],ref['body_reference'])]
            exact=[a for a in candidates if a['artifact'].get('retrieved_at_utc')==ref['retrieved_at_utc'] and a['artifact'].get('http_status')==ref['http_status']]
            if not exact:
                missing.append(dict(ticker=row['ticker'],identity=identity,url=ref['url'],sha256=ref['body_reference'],role=role,reason='Exact committed proof receipt/body unavailable',affected_fields='all source-dependent families'));continue
            a=exact[0];receipt=cash._receipt(dict(a['artifact'],accession=identity['accession']),a['body'])
            bound.append((role,a,receipt))
        if len(bound)!=2:continue
        f=Filing.__new__(Filing);f.year=int(identity['annual_end'][:4]);f.period=cash.Period(identity['cik'],identity['accession'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']))
        f.primary=bound[0][2];f.instance=bound[1][2];f.root,f.contexts,f.units,f.namespaces=cash._instance((f.primary,f.instance),f.period)
        record=dict(url=f.primary.artifact.url,sha256=f.primary.artifact.sha256,body=f.primary.artifact.body,path=bound[0][1]['path'],locator=bound[0][1]['pointer'],retrieved_at_utc=f.primary.retrieved_at_utc,http_status=200,retrieval_mode=f.primary.retrieval_mode)
        documents.verify_primary(record,identity)
        f.inline=InlineFacts();f.inline.feed(f.primary.artifact.body.decode());f.text=re.sub(r'\s+',' ',' '.join(f.inline.text));f.facts={};f.entries=[]
        evidence=inspect.prepare(f.period,(f.primary,f.instance),tuple(inspect.ArtifactBinding(r.artifact.url,r.artifact.sha256,'instance' if r is f.instance else 'support') for r in (f.primary,f.instance)))
        sources=[dict(role=role,path=a['path'],pointer=a['pointer'],url=r.artifact.url,sha256=r.artifact.sha256,representation=r.artifact.representation,digest_type=r.artifact.digest_type,
            retrieved_at_utc=r.retrieved_at_utc,http_status=r.http_status,byte_length=r.byte_length) for role,a,r in bound]
        result.append(dict(ticker=row['ticker'],identity=identity,manifest_reference=mi,proof_reference=LEDGER+'#/rows/'+str(pi),proof=proof,filing=f,evidence=evidence,record=record,sources=sources))
    return result,missing


def outputs():
    packages,missing=build()
    import activate_company_review_batches as accepted
    packages={t:accepted.load_if_approved(f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json',p,decisions(p)) for t,p in packages.items()}
    summary=dict(schema='retained-standard-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),selected_periods=15,family_slots=210,
        companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},
        decisions=[x for t in TICKERS for x in decisions(packages[t])],evidence_acquisition_requirements=missing,new_sec_requests=0,new_assumptions_active=False,
        completed_company_packages=3,reviewed_pending_company_packages=3,broad_assessment_only=36,phase1_closed=False,valuation_consumption_approved=False)
    if accepted.summary_activation(packages):summary['approval_activation']=accepted.summary_activation(packages)
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},'docs/company-data-preparation/standard-review-batch.json':summary}


if __name__=='__main__' and '--inspect' in sys.argv:
    cases,missing=load();print('bound',len(cases),'missing',missing)
    for c in cases:
        f=c['filing'];print('\n',c['ticker'],c['identity'])
        for marker in ('depreciation and amortization','amortization expense','finance leases','finance lease','short-term borrowings','preferred stock','noncontrolling interests','funded status','defined benefit','retirement plans','restricted cash','Financial Products','Machinery, Energy','membership fees','IRS','bottling'):
            m=re.search(re.escape(marker),f.text,re.I)
            if m:print(marker,':',f.text[max(0,m.start()-80):m.end()+1000])
elif __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,payload in result.items():
            if (ROOT/path).read_text()!=json.dumps(payload,sort_keys=True,indent=2)+'\n':raise SystemExit('Batch package replay differs: '+path)
        print('Exact COST/CAT/KO replay:15 source periods/210 historical family slots; '+
            ('effective approved views present (CAT perimeter gaps retained)' if 'approval_activation' in result['docs/company-data-preparation/standard-review-batch.json'] else 'review proposals inactive'))
    else:print(json.dumps(result,sort_keys=True,indent=2))
