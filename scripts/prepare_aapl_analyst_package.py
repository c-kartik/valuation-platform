"""One retained AAPL review package; no runtime treatment or user acceptance.

Reuse the MSFT package's exact fact/inline checks, not its financial choices.
Original registries, pilot serializations and MSFT selections are read-only.
"""
from datetime import date
from decimal import Decimal
import json
import re
import sys

from prepare_msft_analyst_package import Filing, InlineFacts, ROOT, ACCEPTED, SUPPORTED, PROPOSED, inline_amount
from valuation_platform.analyst import aapl_cash_flow_inputs as aapl, cash_flow_inputs as cash

OUTPUT='docs/company-data-preparation/aapl-analyst-input-package.json'
BASELINE='fc403d47ddd23daa387c3e3b872911853e97e8c8'


class AppleFiling(Filing):
    def __init__(self):
        self.year=2025
        self.bundle=aapl.load_aapl_bundle('aapl-reported-cash-flow-fy2025')
        self.period=self.bundle.period
        self.root,self.contexts,self.units,self.namespaces=cash._instance(self.bundle.artifacts,self.period)
        self.instance=next(r for r in self.bundle.artifacts if r.artifact.url.endswith('_htm.xml'))
        self.primary=next(r for r in self.bundle.artifacts if r.artifact.url.endswith('.htm'))
        self.inline=InlineFacts();self.inline.feed(self.primary.artifact.body.decode())
        self.text=re.sub(r'\s+',' ',' '.join(self.inline.text))
        self.facts={};self.entries=[]

    def entry(self,*args,**kwargs):
        super().entry(*args,**kwargs)
        self.entries[-1]['formula_version']='aapl-draft-historical-v1'


def build():
    f=AppleFiling()
    accepted={'NetCashProvidedByUsedInOperatingActivities','PaymentsToAcquirePropertyPlantAndEquipment',
        'IncomeTaxesPaidNet','AllocatedShareBasedCompensationExpense','OperatingLeasePayments'}
    for item in f.bundle.inputs:
        f.fact(item.input_id,item.input_id,item.location_and_scope,namespace=item.occurrences[0].namespace)
        f.entry('reported:'+item.input_id,item.input_id,[item.input_id],[item.display_multiplier],
            scope=item.location_and_scope,role=item.kind.value,
            status=ACCEPTED if item.input_id in accepted else SUPPORTED,
            rationale='Original reported role and signs retained; acceptance only within AAPL checklist scope.',
            completeness='reported_population_only',limitations=('No extra deduction/add-back to reported CFO.',))
    specs=[
        ('revenue','RevenueFromContractWithCustomerExcludingAssessedTax','Income statement / Notes 2 and 13',False),
        ('ebit','OperatingIncomeLoss','Income statement / Note 13',False),
        ('nonoperating','NonoperatingIncomeExpense','Income statement: other income/(expense), net',False),
        ('pretax','IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest','Income statement / Note 7',False),
        ('depreciation_expense','Depreciation','Note 5: PP&E depreciation EXPENSE, not complete D&A',False),
        ('ar','AccountsReceivableNetCurrent','Balance sheet: net customer receivables',True),
        ('vendor_ar','NontradeReceivablesCurrent','Balance sheet / Note 4: component sales to manufacturing vendors',True),
        ('inventory','InventoryNet','Balance sheet; FIFO under Note 1',True),
        ('ap','AccountsPayableCurrent','Balance sheet: whole AP; capital creditor allocation unknown',True),
        ('current_deferred','ContractWithCustomerLiabilityCurrent','Balance sheet: current deferred revenue',True),
        ('other_current_assets','OtherAssetsCurrent','Balance sheet: mixed other current assets',True),
        ('other_long_assets','OtherAssetsNoncurrent','Balance sheet / Note 6 mixed noncurrent assets',True),
        ('dta_location','DeferredIncomeTaxAssetsNet','Note 6: DTA located in other noncurrent assets',True),
        ('other_long_asset_residual','OtherAssetsMiscellaneousNoncurrent','Note 6 residual, not pure operating assets',True),
        ('other_current_liabilities','OtherLiabilitiesCurrent','Balance sheet / Note 6 parent, not additive to children',True),
        ('tax_current','AccruedIncomeTaxesCurrent','Note 6: income taxes within other current liabilities',True),
        ('distribution','AccruedDistributionAndMarketingCurrent','Note 6: distribution/marketing accrual within other current liabilities',True),
        ('other_current_residual','OtherAccruedLiabilitiesCurrent','Note 6 remaining mixed liabilities, not employee accrual',True),
        ('other_long_liabilities','OtherLiabilitiesNoncurrent','Balance sheet: mixed other noncurrent liabilities',True),
        ('cash','CashAndCashEquivalentsAtCarryingValue','Balance sheet / Note 3 cash and equivalents',True),
        ('current_securities','MarketableSecuritiesCurrent','Balance sheet / Note 3 current marketable securities',True),
        ('long_securities','MarketableSecuritiesNoncurrent','Balance sheet / Note 3 noncurrent marketable securities',True),
        ('financial_parent','CashCashEquivalentsAndMarketableSecurities','Note 3 reported cash/equivalents/marketable securities parent',True),
        ('cp','CommercialPaper','Balance sheet carrying CP, not rounded Note 9 alternative',True),
        ('current_debt','LongTermDebtCurrent','Balance sheet / Note 9 current net carrying term debt',True),
        ('long_debt','LongTermDebtNoncurrent','Balance sheet / Note 9 noncurrent net carrying term debt',True),
        ('term_parent','LongTermDebt','Note 9 net carrying total',True),
        ('principal','DebtInstrumentCarryingAmount','Note 9 principal caption, not net carrying despite tag name',True),
        ('discount','DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet','Note 9 unamortized premium/discount/issuance net deduction',True),
        ('hedge','HedgeAccountingAdjustmentsRelatedToLongTermDebt','Note 9 hedge basis deduction',True),
        ('op_rou','OperatingLeaseRightOfUseAsset','Note 8 operating asset in other noncurrent assets',True),
        ('finance_rou','FinanceLeaseRightOfUseAsset','Note 8 finance asset in PP&E',True),
        ('op_current','OperatingLeaseLiabilityCurrent','Note 8 within mixed current liabilities',True),
        ('op_long','OperatingLeaseLiabilityNoncurrent','Note 8 within mixed noncurrent liabilities',True),
        ('finance_current','FinanceLeaseLiabilityCurrent','Note 8 within mixed current liabilities',True),
        ('finance_long','FinanceLeaseLiabilityNoncurrent','Note 8 within mixed noncurrent liabilities',True),
        ('op_total','OperatingLeaseLiability','Note 8 discounted operating liability',True),
        ('finance_total','FinanceLeaseLiability','Note 8 discounted finance liability',True),
        ('op_undiscounted','LesseeOperatingLeaseLiabilityPaymentsDue','Note 8 undiscounted maturities, not historical cash',True),
        ('finance_undiscounted','FinanceLeaseLiabilityPaymentsDue','Note 8 undiscounted maturities, not principal paid',True),
        ('op_imputed','LesseeOperatingLeaseLiabilityUndiscountedExcessAmount','Note 8 future imputed interest, not annual cash interest',True),
        ('finance_imputed','FinanceLeaseLiabilityUndiscountedExcessAmount','Note 8 future imputed interest, not annual cash interest',True),
        ('deferred_federal','DeferredFederalIncomeTaxExpenseBenefit','Note 7 deferred provision component, not CFO adjustment',False),
        ('deferred_state','DeferredStateAndLocalIncomeTaxExpenseBenefit','Note 7 deferred provision component',False),
        ('deferred_foreign','DeferredForeignIncomeTaxExpenseBenefit','Note 7 deferred provision component',False),
        ('tax_credit_dta','DeferredTaxAssetsTaxCreditCarryforwards','Note 7 gross tax-credit DTA, not pure NOL or equity value',True),
        ('purchase_commitments','UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount','Note 12 future purchase obligations over one year, not funded debt or current expense',True),
        ('year_end_common','CommonStockSharesOutstanding','Balance sheet: fiscal-end common, not weighted average',True),
    ]
    extensions={'distribution','hedge','financial_parent'}
    for key,concept,location,instant in specs:
        f.fact(key,concept,location,instant=instant,namespace='aapl' if key in extensions else 'us-gaap',
               unit='shares' if key=='year_end_common' else 'USD')
    f.fact('debt_fair','LongTermDebtFairValue','Note 9 rounded Level 2 fair value, not carrying',instant=True,
        dimensions=(('us-gaap:FairValueByFairValueHierarchyLevelAxis','us-gaap:FairValueInputsLevel2Member'),))
    f.fact('uncommenced_lease','UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount',
        'Note 8 uncommenced operating leases; not recognized debt or annual cash',instant=True,
        dimensions=(('us-gaap:UnrecordedUnconditionalPurchaseObligationByCategoryOfItemPurchasedAxis','us-gaap:OperatingLeaseLeaseNotYetCommencedMember'),))
    f.fact('cover_common','EntityCommonStockSharesOutstanding','Cover observation 2025-10-17',instant=True,
        namespace='dei',unit='shares',as_of='2025-10-17')
    award_dims=(('us-gaap:AwardTypeAxis','us-gaap:RestrictedStockUnitsRSUMember'),)
    for key,concept,unit in (
        ('rsu','ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber','shares'),
        ('future_sbc','EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized','USD')):
        f.fact(key,concept,'Note 11 nonvested RSU population; not incremental diluted shares or a new current cost',
               instant=True,unit=unit,dimensions=award_dims)
    for key in ('revenue','ebit','pretax','depreciation_expense','year_end_common','cover_common','rsu','future_sbc'):
        f.entry(key,f.facts[key]['location'],[key],scope=f.facts[key]['location'],
            rationale='Retain the named reported population, date and precision only.',
            completeness='reported_population_only',
            role='expense_support_not_complete_da' if key=='depreciation_expense' else 'reported_observation')
    def calc(key,label,terms,scope,*,status=SUPPORTED,partial=False,role='historical_component_calculation',policy=None,formula=None):
        f.entry(key,label,[k for k,c in terms],[c for k,c in terms],scope=scope,status=status,role=role,
            rationale=label,completeness='partial' if partial else 'complete_for_named_population',
            limitations=('No full financial-input sufficiency or valuation use.',),policy=policy,formula=formula,
            unit='pure' if formula=='DIVIDE' else None)
    calc('original_partial','Original reviewed current-only partial NWC',
        [('ar',1),('vendor_ar',1),('inventory',1),('ap',-1),('current_deferred',-1)],
        'Original narrow reported-driver scenario, whole AP not operating certified',partial=True)
    calc('proposed_distribution_expanded','Recommended include known distribution/marketing operating accrual',
        [('ar',1),('vendor_ar',1),('inventory',1),('ap',-1),('current_deferred',-1),('distribution',-1)],
        'Proposed partial current operating capital, no employee/capital creditor estimate',status=PROPOSED,partial=True)
    calc('alternative_without_vendor','Alternative exclude vendor supply-chain balance',
        [('ar',1),('inventory',1),('ap',-1),('current_deferred',-1),('distribution',-1)],
        'Less preferred because Note 4 ties components to product costs; still partial',status=PROPOSED,partial=True)
    calc('current_financial','Named current financial balances',[('cash',1),('current_securities',1)],'Not unrestricted/excess cash')
    calc('all_financial','All reported cash and marketable securities',[('cash',1),('current_securities',1),('long_securities',1)],'Not a valuation or availability assertion')
    calc('term_carrying','Term current plus noncurrent',[('current_debt',1),('long_debt',1)],'Net carrying amount; excludes CP and leases')
    calc('principal_bridge','Principal less issuance and hedge deductions',[('principal',1),('discount',-1),('hedge',-1)],'Note 9 principal-to-carrying bridge')
    calc('named_borrowing','Named CP plus term borrowing',[('cp',1),('term_parent',1)],'Disjoint carrying captions, not complete economic debt')
    calc('proposed_financing','Proposed named borrowing plus finance leases',[('cp',1),('term_parent',1),('finance_total',1)],
        'Historical financing subtotal only; operating leases service costs',status=PROPOSED)
    calc('alternative_all_leases','Alternative include operating lease obligations too',
        [('cp',1),('term_parent',1),('finance_total',1),('op_total',1)],'Alternative obligation scope, not accepted total debt',status=PROPOSED)
    calc('operating_partition','Operating liability partition',[('op_current',1),('op_long',1)],'Discounted liabilities, not cash')
    calc('finance_partition','Finance liability partition',[('finance_current',1),('finance_long',1)],'Discounted liabilities, not cash')
    calc('op_discounted','Operating maturity less imputed interest',[('op_undiscounted',1),('op_imputed',-1)],'Discounted lease total')
    calc('finance_discounted','Finance maturity less imputed interest',[('finance_undiscounted',1),('finance_imputed',-1)],'Discounted lease total')
    calc('reported_etr','Existing historical accounting ETR',[('IncomeTaxExpenseBenefit',1),('pretax',1)],
        'Provision / positive reported pretax, no future operating rate',policy='annual_reported_effective_tax_rate_v1',formula='DIVIDE')
    calc('deferred_provision','Deferred provision components',[('deferred_federal',1),('deferred_state',1),('deferred_foreign',1)],
        'Note 7 provision, not separately reported pure CFO deferred tax')
    # Numeric checks complement the statement/notes: agreement alone never proves scope.
    entries={e['input_id']:e for e in f.entries};checks=[]
    def eq(key,left,right):
        if left!=right:raise ValueError('AAPL exact check failed: '+key)
        checks.append(dict(check_id=key,observed=str(left),expected=str(right),difference='0',result='PASS'))
    val=lambda key:Decimal(f.facts[key]['value'])
    for key,parent in [('all_financial','financial_parent'),('term_carrying','term_parent'),
        ('principal_bridge','term_parent'),('operating_partition','op_total'),('finance_partition','finance_total'),
        ('op_discounted','op_total'),('finance_discounted','finance_total')]:eq(key,Decimal(entries[key]['value']),val(parent))
    eq('original_partial',Decimal(entries['original_partial']['value']),Decimal('-240000000'))
    eq('distribution_effect',Decimal(entries['proposed_distribution_expanded']['value'])-Decimal(entries['original_partial']['value']),-val('distribution'))
    eq('pretax_income',val('ebit')+val('nonoperating'),val('pretax'))
    eq('net_income',val('pretax')-val('IncomeTaxExpenseBenefit'),val('NetIncomeLoss'))
    eq('displayed_cfo',sum((Decimal(entries['reported:'+k]['value']) for k in f.bundle.cfo_terms),Decimal(0)),val('NetCashProvidedByUsedInOperatingActivities'))
    passages=[]
    for marker in ('Depreciation expense on property, plant and equipment','resulting from the sale of components',
        'Accrued distribution and marketing','variable lease payments','Finance leases','Balance as of September 27, 2025 151,574',
        'The Company’s unconditional purchase obligations primarily consist of supplier arrangements',
        'In the opinion of management, there was not at least a reasonable possibility'):
        m=re.search(re.escape(marker),f.text,re.I)
        if not m:raise ValueError('Required retained passage absent: '+marker)
        passages.append(dict(source='FY2025-primary',offset=m.start(),exact_excerpt=f.text[max(0,m.start()-60):m.end()+240]))
    tax_candidates=[]
    for ordinal in (987,1010):
        fact=f.root[ordinal];attrs,text=f.inline.facts[fact.attrib['id']]
        if (fact.tag!='{'+f.namespaces['us-gaap']+'}UnrecognizedTaxBenefits' or fact.get('unitRef')!='usd'
            or cash._context(f.contexts[fact.get('contextRef')])!=(f.period.cik,None,f.period.annual_end)
            or attrs['name'].split(':')[-1]!='UnrecognizedTaxBenefits'
            or attrs['contextref']!=fact.get('contextRef') or attrs['unitref']!=fact.get('unitRef')
            or attrs['decimals']!=fact.get('decimals') or inline_amount(attrs,text)!=Decimal(fact.text)):
            raise ValueError('Unrecognized tax alternative evidence changed')
        tax_candidates.append(dict(concept='UnrecognizedTaxBenefits',namespace=f.namespaces['us-gaap'],
            ordinal=ordinal,context_id=fact.get('contextRef'),unit='USD',raw_value=fact.text,
            precision=fact.get('decimals'),primary_locator='inline#'+fact.get('id'),
            role='rounded_narrative_alternative' if ordinal==987 else 'more_precise_rollforward_observation',
            instance_source='FY2025-instance',primary_source='FY2025-primary',as_of=str(f.period.annual_end)))
    manifest=json.loads((ROOT/'docs/evidence/analyst-operating-nwc-response-bodies.json').read_text())
    sources=[]
    for kind,receipt in [('primary',f.primary),('instance',f.instance)]:
        a=receipt.artifact
        ix=next(i for i,v in enumerate(manifest['artifacts']) if v['source_url']==a.url)
        sources.append(dict(source_id='FY2025-'+kind,url=a.url,accession=a.accession,sha256=a.sha256,
            retained_path='docs/evidence/analyst-operating-nwc-response-bodies.json',retained_pointer='/artifacts/'+str(ix),
            representation=a.representation,digest_type=a.digest_type,byte_length=receipt.byte_length,
            retrieved_at_utc=receipt.retrieved_at_utc,http_status=receipt.http_status))
    return dict(schema='aapl-draft-analyst-historical-package-v1',version=1,baseline_revision=BASELINE,issuer='AAPL',
        phase='1',financial_sufficiency='NOT_ASSESSED',valuation_consumption_approved=False,new_sec_requests=0,
        identity=dict(cik=f.period.cik,accession=f.period.accession,form=f.period.form,
            annual_start=str(f.period.annual_start),annual_end=str(f.period.annual_end)),
        sources=sources,facts=f.facts,inputs=f.entries,checks=checks,scope_passages=passages,
        tax_uncertainty_candidates=tax_candidates,
        original_bundle_unknowns=[dict(input_id=u.input_id,reason=u.reason) for u in f.bundle.unknowns],
        original_nwc_reference='docs/company-data-preparation/aapl-analyst-nwc-bundle.json',
        preserved_acceptance_reference='docs/aapl-treatment-acceptance-checklist.md',
        unresolved_requirements=UNKNOWN,approval_sheet=APPROVAL_SHEET,
        estimates=[],manual_inputs=[],adjacent_book_movement=None,
        stopping_condition='One consolidated user review. No automatic research, override, policy integration, Phase 1 closure or Phase 2.')


UNKNOWN=[
    dict(input_id=key,value=None,status='unresolved_requirement',reason=reason) for key,reason in (
    ('expense_basis_da','CFO D&A 11698 and PP&E depreciation expense 8000 rounded are different populations. Complete income-recognized amortization and inventory/finance-lease timing bridge unavailable; no residual-derived amortization.'),
    ('employee_accrual','Current employee cash accrual not isolated. Do not assign mixed remaining liabilities to employees.'),
    ('capital_creditors','Investing/noncash amount inside whole AP unknown; no assumed zero or cash-plus-AP bridge.'),
    ('complete_operating_capital','Other current/noncurrent balances remain mixed; no complete operating allocation or cash movement bridge.'),
    ('cash_interest','Annual borrowing/finance-lease interest paid and capitalization/gross-net basis unavailable; no proxy.'),
    ('complete_lease_cash','Fixed operating cash only. Variable cost 16100 rounded is expense, finance principal/interest cash unavailable.'),
    ('acquisition_intangible','Investing Other 1480 is mixed; no acquisition/intangible allocation or complete cash reinvestment.'),
    ('restriction_reserve','Cash/marketable captions do not establish unrestricted/excess cash or operating reserve. No MSFT supplier restriction imported.'),
    ('other_claims','No exhaustive preferred/NCI/pension/strategic-investment or contingent-claim quantification established in this bounded review; not zero or immaterial.'),
    ('comparability','One reviewed level; acquisitions, FX, reclassification and inventory/lease timing not bridged. No book or cash delta NWC.'),
)]


APPROVAL_SHEET=[dict(decision_id=key,status=PROPOSED,recommendation=rec,numerical_effect=effect,
    alternative=alt,limitations=limit,accepted=False) for key,rec,effect,alt,limit in (
    ('OPERATING-CAPITAL','Include identified distribution/marketing accrual; retain operating vendor receivables and whole AP only as partial driver.',
     '-240 - 8919 = -9159 USDm; no annual movement.',
     'Retain original -240 omitting distribution (+8919 vs proposed); exclude vendor receivables -> -42339 (-33180 vs proposed).',
     'Employee E and capital-creditor K unknown: corrected level would be -9159-E+K before other omitted balances, not a computed estimate.'),
    ('DA-LEASE','Use AAPL source classifications: operating/variable lease costs operating; finance assets/obligations financing. Keep CFO D&A support separate from expense D&A.',
     'CFO add-back11698, PP&E expense8000R; no approved expense D&A, additional ROU add-back or EBIT conversion.',
     'All-lease service convention would require unavailable finance cash/expense split; all-lease liability scope adds12490.',
     'No MSFT finance-amortization inclusion assumption. Fixed cash2100R accepted only as restricted data; variable expense16100R is not cash.'),
    ('INVESTMENT','Keep accepted cash PP&E12715 separate; investing Other1480 and combined noncash ROU2800R support only.',
     'No adjustment or complete reinvestment subtotal.',
     'Broader investing-cash scope includes Other1480 but cannot call it acquisition-only, gross purchases or organic reinvestment.',
     'Capital creditors and acquisition/intangible cash allocation unknown; securities activity is financial investment, not PP&E.'),
    ('FINANCIAL-BALANCES','Use named current financial balances54697; keep noncurrent securities77723 separate. Proposed financing subtotal includes CP/term carrying plus finance leases.',
     'All reported financial captions132420; named borrowing98657; plus finance1230 ->99887.',
     'All-lease obligations ->112377 (+12490); principal91281 versus net term90678 difference603; fair80400R distinct.',
     'No unrestricted/excess cash, complete debt, net-debt or equity-bridge claim. Strategic/restricted/other-claim allocations unproved.'),
    ('TAX-SBC','Preserve accepted SBC expense proxy12863 once, separate matching add-back. Preserve tax provision/cash and historical ETR.',
     'Provision20719; pretax132729; cash43369; deferred provision -1339 distinct from CFO mixed Other -89.',
     'No duplicate SBC cost. Historical cash taxes exceed provision22650, not a recurring tax estimate or allocation.',
     'No operating tax rate, cash-interest proxy or Ireland cash decomposition; future economic policies remain unapproved.'),
    ('SHARES-AWARDS','Use fiscal-end common as dated historical snapshot; retain later cover and nonvested RSUs separately.',
     '2025-09-27 common14773260000; 2025-10-17 cover14776353000; RSUs151574000; unrecognized compensation21800R USDm.',
     'Cover count differs +3093000 shares at a later date, not dilution; annual weighted-average diluted15004697000 is a different population.',
     'No common+award total, award valuation, forecast dilution or extra SBC charge; source rounding remains.'),
)]


if __name__=='__main__':
    text=json.dumps(build(),sort_keys=True,indent=2)+'\n'
    if '--check' in sys.argv:
        if (ROOT/OUTPUT).read_text()!=text:raise SystemExit('AAPL package replay differs')
        print('Exact AAPL FY2025 package replay passed')
    else:print(text,end='')
