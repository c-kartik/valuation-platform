"""One retained AAPL package with separate scoped acceptance, not runtime use.

Reuse the MSFT package's exact fact/inline checks, not its financial choices.
Original registries, pilot serializations and MSFT selections are read-only.
"""
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import re
import sys

from prepare_msft_analyst_package import (Filing, InlineFacts, ROOT, ACCEPTED, SUPPORTED, PROPOSED,
    inline_amount, relevant, digest, _json, ManualIdentity, APPROVED_SCOPE)
from valuation_platform.analyst import aapl_cash_flow_inputs as aapl, cash_flow_inputs as cash

OUTPUT='docs/company-data-preparation/aapl-analyst-input-package.json'
BASELINE='fc403d47ddd23daa387c3e3b872911853e97e8c8'
ACCEPTANCE_BASIS='36ef3d2fa63e712d1735e75d23ebeadc0f33bdcc'
ACCEPTANCE_PATH='docs/company-data-preparation/aapl-analyst-treatment-acceptance.json'
USER_DECISIONS={
    'operating_capital':'Select partial current operating capital -9159 USDm, including manufacturing vendor receivables and distribution accrual8919. Original -240 and alternatives non-default; employee, capital creditors and mixed captions unknown; no delta NWC.',
    'leases_borrowings':'Operating leases service, finance leases asset financing; named CP+term carrying+finance liability99887 USDm only. All-lease112377 non-default. No complete debt, cash/expense split or D&A overlap assumption.',
    'cash_investments':'Current financial balances54697 USDm selected; long-term marketable securities77723 separately. Not unrestricted/excess cash; restrictions, reserves and claims remain unknown.',
    'da_investment':'Keep CFO D&A11698 and rounded depreciation expense8000 distinct; complete expense D&A null. Cash PP&E12715, investing Other1480 and rounded noncash ROU2800 separate with source signs; no amortization residual, reinvestment sum or acquisition allocation.',
    'historical_schedules':'Retain revenue416161, EBIT133050, CFO111482, accepted SBC expense proxy12863 once, provision20719 and cash taxes43369 in distinct roles. Select fiscal-end common14773260000, original date/precision; cover, weighted averages and RSUs151574000 separate. No future rate, award valuation or dilution estimate.',
}


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


def build_proposal():
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


def weighted_average_support():
    """Already reviewed EPS populations; never closing shares or dilution estimates."""
    f=AppleFiling()
    for key,concept in [('weighted_basic','WeightedAverageNumberOfSharesOutstandingBasic'),
                        ('weighted_diluted','WeightedAverageNumberOfDilutedSharesOutstanding')]:
        f.fact(key,concept,'Income statement / Note 3 annual EPS duration population, not point-in-time shares',unit='shares')
    return f.facts


def approval_record(proposal,support):
    """Explicit recording only; normal replay cannot create/renew an approval."""
    record=dict(schema='aapl-treatment-acceptance-audit-v1',version=1,sequence=1,previous='0'*64,
        action='ACCEPT_SCOPED_SELECTIONS',author='User, explicit AAPL FY2025 approved-selection instruction',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Record the user-approved AAPL selections only; missing values, source limitations and original blockers remain.',
        authority='Current user instruction: Implement the user-approved AAPL FY2025 selections in a separate analyst view.',
        source_commit=ACCEPTANCE_BASIS,source_revision=digest(relevant(dict(proposal=proposal,weighted_average_observations=support))),
        decisions=USER_DECISIONS.copy(),financial_sufficiency='NOT_ASSESSED',phase1_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def accepted_view(proposal,support=None,audit_path=None):
    """MSFT's audit/revision/selection pattern, with AAPL-only target meanings.

    The generic numerical override contract has no book operating-capital field.
    Keep this report selection overlay separate instead of misusing CF movements.
    """
    if support is None:support=weighted_average_support()
    path=Path(audit_path) if audit_path is not None else ROOT/ACCEPTANCE_PATH
    record=_json(path.read_text())
    expected={'schema','version','sequence','previous','action','author','recorded_at_utc','rationale','authority',
        'source_commit','source_revision','decisions','financial_sufficiency','phase1_closed','valuation_consumption_approved','sha256'}
    if type(record) is not dict or set(record)!=expected or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):
        raise ValueError('Changed or malformed AAPL acceptance audit')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    if (record['schema']!='aapl-treatment-acceptance-audit-v1' or type(record['version']) is not int or record['version']!=1
        or type(record['sequence']) is not int or record['sequence']!=1 or record['previous']!='0'*64
        or record['action']!='ACCEPT_SCOPED_SELECTIONS' or record['source_commit']!=ACCEPTANCE_BASIS
        or record['decisions']!=USER_DECISIONS or record['financial_sufficiency']!='NOT_ASSESSED'
        or record['phase1_closed'] is not False or record['valuation_consumption_approved'] is not False):
        raise ValueError('Unregistered AAPL acceptance scope')
    if record['source_revision']!=digest(relevant(dict(proposal=proposal,weighted_average_observations=support))):
        raise ValueError('Stale AAPL acceptance: source, candidates, scope or evidence changed; explicit revalidation required')
    entries={e['input_id']:e for e in proposal['inputs']}
    def select(key,label):
        original=entries[key];selected=json.loads(json.dumps(original))
        selected.update(status=APPROVED_SCOPE,accepted=True)
        return dict(selected=selected,label=label,source_status=original['status'],
            source_reference='/inputs/'+str(next(i for i,e in enumerate(proposal['inputs']) if e['input_id']==key)),
            approval_sha256=record['sha256'],review=APPROVED_SCOPE)
    unknown={u['input_id']:u for u in proposal['unresolved_requirements']}
    view=dict(schema='aapl-accepted-historical-view-v1',version=1,approval_audit=record,identity=proposal['identity'],
        operating_capital=select('proposed_distribution_expanded','Partial current operating capital'),
        complete_operating_capital=False,book_delta_nwc=None,cash_delta_nwc=None,
        nondefault_history=[dict(default=False,source_reference='/inputs/'+str(next(i for i,e in enumerate(proposal['inputs']) if e['input_id']==key)),
            observation=entries[key]) for key in ('original_partial','alternative_without_vendor','alternative_all_leases','all_financial','named_borrowing')],
        lease_classification=dict(operating='service_cost',finance='asset_financing',review=APPROVED_SCOPE,
            complete_lease_coverage=False,finance_amortization_inclusion_assumption=None),
        borrowings=select('proposed_financing','Named CP + term-debt carrying + finance-lease liability subtotal'),complete_debt=False,
        current_financial_balances=select('current_financial','Current financial balances'),
        long_term_marketable_securities=dict(source_reference='/facts/long_securities',observation=proposal['facts']['long_securities'],review=APPROVED_SCOPE),
        unrestricted_or_excess_cash=False,unknown_restrictions=None,operating_reserve=None,
        da_observations=[entries['reported:DepreciationDepletionAndAmortization'],entries['depreciation_expense']],
        complete_expense_basis_da=unknown['expense_basis_da'],additional_rou_addback=False,
        investment_columns=[entries[k] for k in ('reported:PaymentsToAcquirePropertyPlantAndEquipment',
            'reported:PaymentsForProceedsFromOtherInvestingActivities','reported:RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities')],
        complete_reinvestment=False,
        historical_income=[select(k,entries[k]['label']) for k in ('revenue','ebit','reported:NetCashProvidedByUsedInOperatingActivities')],
        sbc_expense_proxy=select('reported:AllocatedShareBasedCompensationExpense','Recognized SBC expense proxy counted once'),
        sbc_cfo_addback=entries['reported:ShareBasedCompensation'],
        historical_taxes=[entries[k] for k in ('reported:IncomeTaxExpenseBenefit','reported:IncomeTaxesPaidNet','reported_etr','deferred_provision')],
        fiscal_end_common=select('year_end_common','Fiscal-end common shares; original date and precision'),
        separate_cover_awards=[entries[k] for k in ('cover_common','rsu','future_sbc')],
        weighted_average_observations=support,
        unresolved_requirements=proposal['unresolved_requirements'],original_bundle_unknowns=proposal['original_bundle_unknowns'],
        prior_proposals_retained=True,decision_statuses={key:APPROVED_SCOPE for key in USER_DECISIONS},
        financial_sufficiency='NOT_ASSESSED',valuation_consumption_approved=False,phase1_closed=False,
        future_tax_assumption_approved=False,award_valuation_approved=False,dilution_estimate_approved=False,
        stopping_condition='Stop after AAPL integration; no automatic Alphabet work or Phase 1 closure.')
    result=json.loads(json.dumps(proposal));result['accepted_view']=json.loads(json.dumps(view))
    return result


def build():
    return activate_company_history(review_company_history(accepted_view(build_proposal())))


def review_company_history(package):
    """One retained-only company review; all new judgments remain inactive."""
    parent={k:v for k,v in package.items() if k not in ('aapl_history_review','aapl_history_approval','aapl_current_history')}
    reviewed=accepted_view(build_proposal())
    if reviewed!=parent:raise ValueError('Changed prior AAPL source/approval')
    manifest=_json((ROOT/'docs/phase1-selected-filing-identity-manifest.json').read_text())
    selected=[(i,r) for i,r in enumerate(manifest['rows']) if r['ticker']=='AAPL']
    if len(selected)!=5 or len({r['identity']['accession'] for i,r in selected})!=5:raise ValueError('Frozen AAPL selection differs')
    artifact_path='docs/evidence/analyst-operating-nwc-response-bodies.json'
    artifacts=_json((ROOT/artifact_path).read_text())['artifacts'];rows=[]
    for index,selection in selected:
        identity=selection['identity'];year=int(identity['annual_end'][:4]);refs=[(i,a) for i,a in enumerate(artifacts) if a.get('accession')==identity['accession']]
        receipts=[cash._receipt(a,cash.gzip.decompress(cash.base64.b64decode(a['response_body_gzip_base64'],validate=True))) for i,a in refs]
        primaries=[r for r in receipts if r.artifact.url.endswith('.htm')];instances=[r for r in receipts if r.artifact.url.endswith('_htm.xml')]
        if len(primaries)!=1 or len(instances)!=1:raise ValueError('Exact selected primary/instance pair unavailable: '+identity['accession'])
        f=AppleFiling.__new__(AppleFiling);f.year=year;f.period=cash.Period(identity['cik'],identity['accession'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']))
        f.primary=primaries[0];f.instance=instances[0];f.root,f.contexts,f.units,f.namespaces=cash._instance(tuple(receipts),f.period)
        f.inline=InlineFacts();f.inline.feed(f.primary.artifact.body.decode());f.text=re.sub(r'\s+',' ',' '.join(f.inline.text));f.facts={};f.entries=[];exceptions=[]
        # Reuse the reviewed AAPL concept/population specifications, not FY2025 values.
        # JSON key order is not a source revision. Retain the original reviewed
        # specification order so restart reproduces the exact exception history.
        for key,spec in reviewed['facts'].items():
            if key=='cover_common':continue
            try:f.fact(key,spec['concept'],'Selected FY'+str(year)+' primary reported population: '+key,instant=spec['as_of'] is not None,
                namespace='aapl' if spec['namespace'].startswith('http://www.apple.com/') else 'us-gaap',unit=spec['unit'],
                dimensions=tuple(tuple(v) for v in spec['occurrences'][0]['dimensions']))
            except ValueError as exc:
                alternatives=[]
                if 'Competing eligible values' in str(exc):
                    ns=f.namespaces['aapl'] if spec['namespace'].startswith('http://www.apple.com/') else f.namespaces['us-gaap']
                    for o in cash._occurrences(f.root,f.contexts,f.units,f.namespaces,ns,spec['concept'],f.period,spec['as_of'] is not None):
                        node=f.root[o.ordinal];attrs,text=f.inline.facts[node.get('id')]
                        if inline_amount(attrs,text)!=Decimal(o.raw_value):raise ValueError('Competing primary/instance representation mismatch')
                        alternatives.append(dict(cash._occurrence_dict(o),primary_locator='inline#'+node.get('id'),primary_display=text))
                exceptions.append(dict(input_id=key,reason=str(exc),kind='RETAINED_BINDING_OR_SCOPE',value=None,alternatives=alternatives))
        cover_dates=set()
        for node in f.root:
            if node.tag.startswith('{http://xbrl.sec.gov/dei/') and node.tag.endswith('}EntityCommonStockSharesOutstanding'):
                context=cash._context(f.contexts[node.get('contextRef')])
                if context and context[0]==f.period.cik and context[1] is None:cover_dates.add(str(context[2]))
        for stamp in sorted(cover_dates):f.fact('cover_common_'+stamp,'EntityCommonStockSharesOutstanding','Actual cover date, not year-end or dilution',instant=True,namespace='dei',unit='shares',as_of=stamp)
        for key,concept,instant in [('deferred_cfo','DeferredIncomeTaxExpenseBenefit',False),('deferred_revenue_movement','IncreaseDecreaseInContractWithCustomerLiability',False),
            ('acquisition_cash','PaymentsToAcquireBusinessesNetOfCashAcquired',False),('cash_interest_net','InterestPaidNet',False),
            ('equity','StockholdersEquity',True),('common_capital','CommonStocksIncludingAdditionalPaidInCapital',True),
            ('retained','RetainedEarningsAccumulatedDeficit',True),('oci','AccumulatedOtherComprehensiveIncomeLossNetOfTax',True),
            ('liabilities','Liabilities',True),('balance_total','LiabilitiesAndStockholdersEquity',True),
            ('tax_benefits','UnrecognizedTaxBenefits',True)]:
            try:f.fact(key,concept,'Selected primary named population, not an economic adjustment',instant=instant)
            except ValueError as exc:exceptions.append(dict(input_id=key,reason=str(exc),kind='RETAINED_BINDING_OR_SCOPE',value=None))
        # Independently displayed reconciliation: no residual-defined balancing item.
        begin=f.text.find('Adjustments to reconcile');end=f.text.find('Investing activities:',begin)
        if begin<0 or end<0:raise ValueError('Displayed AAPL operating reconciliation absent')
        cfo_display=f.text[max(0,begin-100):end]
        terms=[('NetIncomeLoss',1),('DepreciationDepletionAndAmortization',1),('ShareBasedCompensation',1)]
        if 'Deferred income tax' in cfo_display:terms.append(('deferred_cfo',1))
        terms += [('OtherNoncashIncomeExpense',-1),('IncreaseDecreaseInAccountsReceivable',-1),('IncreaseDecreaseInInventories',-1),
            ('IncreaseDecreaseInOtherReceivables',-1),('IncreaseDecreaseInOtherOperatingAssets',-1),('IncreaseDecreaseInAccountsPayable',1)]
        if 'Deferred revenue' in cfo_display:terms.append(('deferred_revenue_movement',1))
        terms.append(('IncreaseDecreaseInOtherOperatingLiabilities',1))
        cf=[dict(fact=k,multiplier=c,contribution_usd=str(Decimal(f.facts[k]['value'])*c)) for k,c in terms]
        total=sum((Decimal(r['contribution_usd']) for r in cf),Decimal(0))
        if total!=Decimal(f.facts['NetCashProvidedByUsedInOperatingActivities']['value']):raise ValueError('Selected AAPL displayed CFO does not reconcile')
        def calc(key,operands,coefficients=None,*,partial=False,formula=None,unit=None):
            if any(k not in f.facts for k in operands):return
            f.entry(key,key,operands,coefficients,scope='Named population only; original operand precision; no economic completeness',
                rationale='Source-bound arithmetic, not approval of financial use',completeness='partial' if partial else 'complete_for_named_population',
                formula=formula,unit=unit,policy='annual_reported_effective_tax_rate_v1' if formula=='DIVIDE' else None)
        calc('current_financial',['cash','current_securities']);calc('all_financial',['cash','current_securities','long_securities'])
        calc('term_carrying',['current_debt','long_debt']);calc('named_financing',['cp','current_debt','long_debt','finance_total'])
        calc('all_lease_alternative',['cp','current_debt','long_debt','finance_total','op_total'])
        calc('original_partial',['ar','vendor_ar','inventory','ap','current_deferred'],[1,1,1,-1,-1],partial=True)
        calc('distribution_partial',['ar','vendor_ar','inventory','ap','current_deferred','distribution'],[1,1,1,-1,-1,-1],partial=True)
        calc('reported_etr',['IncomeTaxExpenseBenefit','pretax'],formula='DIVIDE',unit='pure')
        calc('deferred_provision',['deferred_federal','deferred_state','deferred_foreign'])
        checks=[]
        def partition(key,parent_key,children):
            if not all(k in f.facts for k in [parent_key,*children]):return
            lhs=Decimal(f.facts[parent_key]['value']);rhs=sum((Decimal(f.facts[k]['value']) for k in children),Decimal(0))
            if lhs!=rhs:raise ValueError('AAPL population partition differs: '+key)
            checks.append(dict(check_id=key,left=str(lhs),right=str(rhs),result='PASS'))
        for key,par,children in [('financial_partition','financial_parent',['cash','current_securities','long_securities']),
            ('term_partition','term_parent',['current_debt','long_debt']),('equity_partition','equity',['common_capital','retained','oci']),
            ('balance_partition','balance_total',['liabilities','equity']),('operating_partition','op_total',['op_current','op_long']),
            ('finance_partition','finance_total',['finance_current','finance_long'])]:partition(key,par,children)
        passages=[]
        for marker in ('Adjustments to reconcile','Depreciation expense','Depreciation and amortization expense','amortization of intangible',
            'business acquisitions','business combinations','commercial paper','Commercial Paper','Preferred Stock','preferred stock','Noncontrolling','pension',
            'Retirement','Finance leases','Operating Leases','operating leases','Accrued distribution','Other current liabilities','manufacturing vendors',
            'total unrecognized compensation','wholly owned subsidiaries','total shareholders’ equity','Total term debt','restricted from general use','As a result, during the fourth quarter of 2024'):
            found=re.search(re.escape(marker),f.text,re.I)
            if found:passages.append(dict(marker=marker,offset=found.start(),exact_excerpt=f.text[max(0,found.start()-80):found.end()+1800],source_sha256=f.primary.artifact.sha256))
        passages.append(dict(marker='independently_displayed_cfo',offset=max(0,begin-100),exact_excerpt=cfo_display,source_sha256=f.primary.artifact.sha256))
        # Narrow dated note transcriptions: source observations, not estimated allocations.
        note_observations=[]
        for key,pattern in [('restricted_securities',r'As of September \d+, '+str(year)+r'[^.]{0,90}total marketable securities included \$ ([\d.]+) billion'),
            ('unrecognized_compensation',r'As of September \d+, '+str(year)+r', the total unrecognized compensation cost[^$]{0,120}\$ ([\d.]+) billion')]:
            match=re.search(pattern,f.text,re.I)
            if match:note_observations.append(dict(input_id=key,value_usd=str(Decimal(match.group(1))*1000000000),unit='USD',precision='-8',as_of=identity['annual_end'],
                origin='reported_note_transcription',not_estimate=True,source_sha256=f.primary.artifact.sha256,offset=match.start(),exact_excerpt=f.text[match.start():match.end()+180],
                scope='Total marketable securities; current/noncurrent split not established' if key=='restricted_securities' else ('Outstanding RSUs and stock options' if year<=2022 else 'Outstanding RSUs')))
        if year==2024:
            match=re.search(r'As of September 28, 2024, cash and cash equivalents included \$ ([\d.]+) billion held in escrow',f.text)
            if not match:raise ValueError('FY2024 reported cash restriction absent')
            note_observations.append(dict(input_id='restricted_cash',value_usd=str(Decimal(match.group(1))*1000000000),unit='USD',precision='-8',
                as_of=identity['annual_end'],origin='reported_note_transcription',not_estimate=True,source_sha256=f.primary.artifact.sha256,
                offset=match.start(),exact_excerpt=match.group(0),scope='Within reported current cash/equivalents, not another asset'))
        debt_note=[]
        for key,pattern,coefficient in [('principal',r'Total term debt(?: principal)? ([\d,]+)',1),
            ('discount',r'Unamortized premium/\(discount\) and issuance costs, net \( ([\d,]+) \)',-1),
            ('hedge',r'Hedge accounting fair value adjustments (\( )?([\d,]+)',1)]:
            match=re.search(pattern,f.text)
            if not match:raise ValueError('Independent debt-note bridge caption unavailable: '+key)
            number=match.group(2 if key=='hedge' else 1).replace(',','');sign=-1 if key=='hedge' and match.group(1) else coefficient
            debt_note.append(dict(input_id=key,raw_display_number=number,multiplier=sign,contribution_usd=str(Decimal(number)*1000000*sign),
                unit='USD',precision='-6',as_of=identity['annual_end'],origin='reported_note_transcription',source_sha256=f.primary.artifact.sha256,
                offset=match.start(),exact_excerpt=match.group(0),scope='Selected term-debt note; carrying/principal/fair value are different populations'))
        carrying=sum((Decimal(n['contribution_usd']) for n in debt_note),Decimal(0))
        if carrying!=Decimal(f.facts['current_debt']['value'])+Decimal(f.facts['long_debt']['value']):raise ValueError('Independent term carrying bridge differs FY'+str(year)+': '+str([(n['input_id'],n['contribution_usd']) for n in debt_note]))
        note_observations.extend(debt_note)
        tax_candidates=[]
        for o in cash._occurrences(f.root,f.contexts,f.units,f.namespaces,f.namespaces['us-gaap'],'UnrecognizedTaxBenefits',f.period,True):
            node=f.root[o.ordinal];attrs,text=f.inline.facts[node.get('id')]
            if inline_amount(attrs,text)!=Decimal(o.raw_value):raise ValueError('Tax-stock alternative source mismatch')
            tax_candidates.append(dict(cash._occurrence_dict(o),primary_locator='inline#'+node.get('id'),primary_display=text))
        for key,concept in [('weighted_basic','WeightedAverageNumberOfSharesOutstandingBasic'),('weighted_diluted','WeightedAverageNumberOfDilutedSharesOutstanding')]:
            f.fact(key,concept,'Annual EPS duration population, not closing shares or dilution estimate',unit='shares')
        rows.append(dict(identity=identity,source_manifest_reference='docs/phase1-selected-filing-identity-manifest.json#/rows/'+str(index),
            sources=[dict(path=artifact_path,pointer='/artifacts/'+str(i),**{k:a[k] for k in ('source_url','sha256','representation','digest_type','retrieved_at_utc','http_status','byte_length')}) for i,a in refs],
            facts=f.facts,calculations=f.entries,exceptions=exceptions,passages=passages,note_observations=note_observations,partition_checks=checks,
            cfo_reconciliation=dict(terms=cf,value_usd=str(total),supported=True,displayed_source_reference='passages/independently_displayed_cfo',residual_used=False),
            term_carrying_bridge=dict(value_usd=str(carrying),terms=debt_note,supported=True,current_maturities_already_included=True),tax_stock_candidates=tax_candidates,
            analyst_complete=False,new_assumptions_active=False,existing_approval_reference='/accepted_view' if year==2025 else None))
    from valuation_platform.analyst.historical_inputs import Field
    fields=[v.value for v in Field]
    if len(fields)!=14:raise ValueError('Historical family contract changed')
    family_facts={
        'revenue':['revenue'],'ebit':['ebit'],'depreciation_amortization':['DepreciationDepletionAndAmortization','depreciation_expense'],
        'cash_capex':['PaymentsToAcquirePropertyPlantAndEquipment','PaymentsForProceedsFromOtherInvestingActivities','RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities'],
        'reported_cash_flow_working_capital_movements':[r['fact'] for r in rows[-1]['cfo_reconciliation']['terms'][4:]],
        'deferred_taxes':['deferred_federal','deferred_state','deferred_foreign','OtherNoncashIncomeExpense'],
        'stock_based_compensation':['AllocatedShareBasedCompensationExpense','ShareBasedCompensation'],
        'unclassified_cfo_reconciliation_residual':['OtherNoncashIncomeExpense'],
        'reported_cfo':['NetCashProvidedByUsedInOperatingActivities'],
        'reported_tax_context':['IncomeTaxExpenseBenefit','pretax','IncomeTaxesPaidNet'],
        'cash_investment_components':['cash','current_securities','long_securities','financial_parent'],
        'debt_lease_components':['cp','current_debt','long_debt','finance_total','op_total'],
        'other_equity_bridge_claims_assets':['equity','common_capital','retained','oci','tax_credit_dta'],
        'point_in_time_shares':['year_end_common','rsu']}
    pending={'depreciation_amortization':['A2'],
        'unclassified_cfo_reconciliation_residual':['A9'],'stock_based_compensation':['A3'],
        'cash_investment_components':['A5'],'debt_lease_components':['A4'],'other_equity_bridge_claims_assets':['A6','A7','A8'],
        'point_in_time_shares':['A10']}
    accepted_fields={'revenue','ebit','cash_capex','stock_based_compensation','reported_cfo','reported_tax_context','cash_investment_components','point_in_time_shares'}
    for i,row in enumerate(rows):
        year=int(row['identity']['annual_end'][:4]);base=f'/aapl_history_review/periods/{i}';facts=row['facts'];checklist=[]
        for field in fields:
            keys=family_facts[field]
            if field=='reported_cash_flow_working_capital_movements':keys=[t['fact'] for t in row['cfo_reconciliation']['terms'] if t['fact'].startswith('IncreaseDecrease') or t['fact']=='deferred_revenue_movement']
            if field=='deferred_taxes' and year<=2022:keys=['deferred_cfo',*keys]
            decisions=[] if year==2025 and field in accepted_fields else pending.get(field,[])
            if field=='deferred_taxes' and year>=2023:decisions=['A8']
            status='PROPOSED_PENDING_APPROVAL' if decisions else 'EXISTING_SCOPED_APPROVAL' if year==2025 and field in accepted_fields else 'SOURCE_SUPPORTED'
            if any(k not in facts for k in keys):status='ESSENTIAL_EVIDENCE_EXCEPTION'
            checklist.append(dict(field=field,status=status,pending_decisions=decisions,evidence_references=[base+'/facts/'+k for k in keys if k in facts],
                existing_approval_reference='/accepted_view' if year==2025 and field in accepted_fields|{'debt_lease_components'} else None,
                completeness='Named historical input/operation only; no complete debt/reinvestment or operating-only cash claim'))
        row['family_checklist']=checklist
        row['cfo_reconciliation']['displayed_source_reference']=base+'/passages/'+str(next(j for j,p in enumerate(row['passages']) if p['marker']=='independently_displayed_cfo'))
        row['movement_rows']=[dict(t,already_in_reported_cfo=True,not_book_delta_nwc=True) for t in row['cfo_reconciliation']['terms'] if t['fact'].startswith('IncreaseDecrease') or t['fact']=='deferred_revenue_movement']
        row['proposed_da_proxy']=dict(value_usd=facts['DepreciationDepletionAndAmortization']['value'],unit='USD',precision=facts['DepreciationDepletionAndAmortization']['precision'],
            origin='proxy',accepted=False,status=PROPOSED,source_reference=base+'/facts/DepreciationDepletionAndAmortization',
            rationale='Use explicitly displayed depreciation/amortization cash-reconciliation amount as a historical noncash-cost proxy, NOT verified complete income-recognized D&A. No balancing subtraction or extra ROU add-back.',
            author='Analyst preparation review, pending user approval',recorded_at_utc='2026-10-17T15:33:27+00:00',
            expense_basis_da=None,finance_amortization_inclusion_assumption=None,inventory_lease_timing_bridge=None)
        row['cash_signs']={k:-1 for k in ['PaymentsToAcquirePropertyPlantAndEquipment','PaymentsForProceedsFromOtherInvestingActivities','IncomeTaxesPaidNet','OperatingLeasePayments']}
        row['cash_signs'].update(acquisition_cash=-1,cash_interest_net=-1)
        row['supporting_unknowns']={k:None for k in ['employee_accrual','capital_creditors','unallocated_other_investing','finance_lease_interest_cash','finance_lease_principal_cash','complete_lease_cash','preferred','nci','pension_funded_status','pure_nol_dta','complete_expense_basis_da','operating_reserve','additional_borrowing']}
        row['complete_nwc_required_for_proposed_path']=False;row['additional_movement_deduction_permitted']=False
    identities=[r['identity'] for r in rows]
    # Later evidence corroborates only the stated FY2024 population, not a new period.
    primary2025=next(a for i,a in enumerate(artifacts) if a.get('accession')==identities[-1]['accession'] and a['source_url'].endswith('.htm'))
    inline=InlineFacts();inline.feed(cash.gzip.decompress(cash.base64.b64decode(primary2025['response_body_gzip_base64'],validate=True)).decode())
    text=re.sub(r'\s+',' ',' '.join(inline.text))
    match=re.search(r'As of September 28, 2024, current marketable securities included \$ ([\d.]+) billion held in escrow',text)
    if not match:raise ValueError('FY2024 current restricted-securities comparative binding absent')
    rows[3]['comparative_scope_support']=dict(source_identity=identities[-1],as_of='2024-09-28',value_usd=str(Decimal(match.group(1))*1000000000),precision='-8',unit='USD',
        origin='reported_note_transcription',scope='Within FY2024 current marketable securities',source_sha256=primary2025['sha256'],offset=match.start(),exact_excerpt=match.group(0))
    restriction=next(n for n in rows[3]['note_observations'] if n['input_id']=='restricted_cash')
    gross=next(c for c in rows[3]['calculations'] if c['input_id']=='current_financial')
    rows[3]['restricted_current_alternative']=dict(value_usd=str(Decimal(gross['value'])-Decimal(restriction['value_usd'])-Decimal(rows[3]['comparative_scope_support']['value_usd'])),
        unit='USD',precision=['-6','-8','-8'],status=PROPOSED,accepted=False,default=False,origin='derived',
        operands=['current_financial','note_observations/restricted_cash','comparative_scope_support'],unknown_restrictions=None,operating_reserve=None,unrestricted_or_excess_cash=False)
    specs=[
        ('A1',identities,'Retain the user-instructed reported cash-movement/reconciled-CFO preparation path for all five years; reconstructed NWC/book delta is not prerequisite. Keep NWC schedules as supporting history only. This source-supported operational row requests no new approval.',
         'CFO104038/122151/110543/118254/111482 USDm;12/12/10/10/10 independently bound displayed terms;7/7/6/6/6 movement rows already in CFO, no second deduction.',
         'Alternative EBIT/book-NWC path needs unavailable employee/capital-creditor/mixed allocations; no invented estimate. Consolidated movements remain affected by tax, acquisition, FX and reclassification scope.'),
        ('A2',identities,'Select each explicitly labeled CFO D&A amount as a historical noncash-cost proxy; do not call it complete expense D&A, infer amortization or assume finance amortization is included.',
         'Proposed proxy11284/11104/11519/11445/11698 versus PP&E note9500/8700/8500/8200/8000R. Differences1784/2404/3019/3245/3698 are population differences, NOT amortization. No extra ROU add-back.',
         'Alternative keep required D&A unresolved; PP&E-only note is not complete intangible D&A. CFO versus income/inventory/lease timing is unbridged and its effect unquantified. FY2021/22 note says PP&E depreciation AND amortization, unlike later depreciation-only prose.'),
        ('A3',identities[:4],'Extend recognized SBC expense as a labeled economic-cost proxy once to FY2021-FY2024; keep separate add-back and awards. FY2025 approval remains unchanged.',
         '7906/9038/10833/11688 USDm; FY2025 accepted12863. No duplicate expense or rounding adjustment.',
         'Alternative economic replacement-cost/award-value basis unavailable; recognized expense is neither cash replacement cost nor outstanding-award value.'),
        ('A4',identities,'Use operating leases as service/finance leases as financing; select each named CP + term carrying + finance liability, with no additional undisclosed-borrowing adjustment. FY2025 named subtotal/convention already accepted; broader no-extra-adjustment assumption is newly proposed.',
         '125567/121010/112112/107525/99887 USDm. All-lease alternatives136522/132480/123930/119059/112377. Current term maturities already included; principal/fair value and commitments are not additive.',
         'No extra adjustment economically omits unquantified possible borrowing; not source zero, complete debt or immateriality. Alternative retain named subtotal as partial only; all-lease alternative requires aligned economics. Finance cash/expense splits remain unavailable; no MSFT D&A-inclusion assumption.'),
        ('A5',identities[:4],'Select named current financial balances, retaining LT/restricted/strategic observations separately; do not call any current balance unrestricted or excess. FY2025 accepted54697 unchanged.',
         '62639/48304/61555/65171 USDm; LT127877/120805/100544/91479 separate. FY2021-23 restricted total marketable17900/12700/13800R not allocated to current/LT. FY2024 known2600R cash and13200R marketable escrow stay visible.',
         'Alternative FY2024 current less15800R identified escrow is49371R, with current-securities location explicitly corroborated by FY2025 dated comparative note. It is non-default pending a choice, not a rounding adjustment. Unknown restrictions/reserves and strategic holdings remain unquantified; gross balances must not be used as available cash.'),
        ('A6',identities,'No additional preferred-equity or NCI adjustment selected, relying on each common-equity partition and wholly-owned consolidated presentation; preserve source nulls.',
         'No extra claim adjustment, not a reported zero. Source common/APIC+retained+OCI equals reported equity in all five selected filings.',
         'Alternative quantify separate claims if evidenced; current evidence cannot bound omitted preferred/minority claims. Presentation supports an analyst choice, not an immateriality finding or exhaustive ownership proof.'),
        ('A7',identities,'Propose no separate pension funded-status adjustment while retaining the recognized balance-sheet liabilities; disclose absent quantified funded status and do not invent retirement expense.',
         'No extra adjustment selected would omit a potentially unreported net claim/surplus of unbounded size; source remains null.',
         'Weaker evidence than common-equity choices: benefits/stock-plan notes do not establish pension population completeness. Alternative leave this essential claim decision blocked. User must explicitly accept this unbounded omission; no audit opinion/keyword absence establishes zero.'),
        ('A8',identities,'Retain reported provision/pretax/ETR and cash taxes; retain FY2021/22 explicit deferred-tax CFO rows. For FY2023-25 no separate pure-deferred CFO operation or pure-NOL economic-asset operation; retain mixed Other and reported tax-credit DTA without allocations.',
         'CFO deferred -4774/+895 then pure component unknown within Other-2227/-2266/-89; deferred provision -4774/+895/-3024/-3031/-1339 is a separate role, not a replacement. Cash taxes25385/19573/18679/26102/43369 outflows remain reported.',
         'Alternative pure operating-tax/deferred bridge is unavailable and unnecessary only under approved consolidated-CFO path; future rate/valuation is separate. Tax-credit DTA4262/6962/8302/8856/8643 is not pure NOL or an approved valued asset. Ireland FY2024 charge/FY2025 settlement remains historical, not normalized.'),
        ('A9',identities,'No separately computed residual scalar for each fully bound displayed reconciliation; retain signed mixed Other rows, not a residual-defined zero.',
         'Other contributions -147/+111/-2227/-2266/-89 USDm; full CFO displays tie independently, no plug or new adjustment.',
         'Alternative classify every mixed subcomponent cannot be supported from retained disclosures. Source equality does not certify operating-only cash or EBIT-based FCFF readiness.'),
        ('A10',identities[:4],'Select fiscal-end common shares at each original date/precision; keep later cover observations, EPS denominators and award populations separate. FY2025 selection unchanged.',
         '16426786000/15943425000/15550061000/15116786000 shares; FY2025 accepted14773260000. Awards240427000/201501000/180247000/163326000/151574000 separate, never added.',
         'Alternative later cover dates differ and annual diluted weighted averages are not closing shares. Unrecognized compensation in FY2021/22 includes RSUs AND options, later RSUs only. No award valuation/dilution estimate.')]
    proposals=[dict(decision_id=k,periods=periods,recommendation=rec,numerical_consequence=effect,uncertainty_and_alternative=risk,
        evidence_reference='/aapl_history_review/periods',status=SUPPORTED if k=='A1' else PROPOSED,approval_required=k!='A1',accepted=False) for k,periods,rec,effect,risk in specs]
    result=json.loads(json.dumps(parent));result['aapl_history_review']=dict(version=1,periods=rows,source_revision=digest(relevant(parent)),
        review_revision=digest(relevant(dict(periods=rows,proposals=proposals,parent_revision=digest(relevant(parent))))),
        consolidated_proposals=proposals,family_slots=70,
        outcomes={status:sum(r['status']==status for p in rows for r in p['family_checklist']) for status in ['SOURCE_SUPPORTED','EXISTING_SCOPED_APPROVAL','PROPOSED_PENDING_APPROVAL','ESSENTIAL_EVIDENCE_EXCEPTION']},
        analyst_complete=False,company_completed=False,new_assumptions_active=False,
        source_path='User-instructed reported movements and independently reconciled CFO; complete reconstructed NWC/book delta is not prerequisite; movements are not additional deductions. No Phase2 formula.',
        evidence_acquisition_requirements=[],new_sec_requests=0,phase_closed=False,valuation_consumption_approved=False,
        evidence_limits='All ten exact selected primary/instance bodies/receipts available. Missing subamounts are disclosure/scope limitations, not missing documents. No additional exact artifact established; do not create an acquisition/research queue.',
        comparability=['FY2023 is53 weeks; others52 weeks, no annualization.',
            'FY2021/22 selected CFO separately displays deferred tax and deferred revenue; FY2023 comparisons combine them into Other and other liabilities. Retain selected accessions, no recast or balancing item.',
            'FY2021/22 PP&E note says depreciation and amortization, later depreciation only; no subtraction-based intangible amortization.',
            'FY2021/22 acquisition payments33/306 are separate; later investing Other remains mixed, not zero acquisitions.',
            'FY2024 Ireland net tax charge10200R and escrow15800R; FY2025 tax cash settlement and comparative classification retained without normalization.',
            'FY2025 newly isolated distribution accrual8919 has no isolated prior selected-tag equivalent; earlier employee/investing-AP allocations remain unknown.'],
        stopping_condition='One company batch complete; stop for consolidated A1-A10 review and explicit uncertainty choices. No new approval, extraction queue, company completeness or Phase2 authority.')
    return result


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


def history_approval_record(package):
    if 'aapl_history_approval' in package:raise ValueError('Immutable AAPL history approval already exists')
    review=package['aapl_history_review']
    record=dict(schema='aapl-treatment-acceptance-audit-v1',version=1,sequence=2,
        previous=package['accepted_view']['approval_audit']['sha256'],action='ACCEPT_FY2021_FY2025_A2_A10',
        author='User, explicit approval of AAPL A2-A10 exactly as proposed across FY2021-FY2025',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Accept labeled CFO-D&A proxies, named financing/no additional borrowing and claim/pension omissions with unbounded uncertainty, gross current financial balances with known restrictions; historical perimeter only.',
        authority='Current user instruction Part1: explicitly approves A2-A10 exactly as proposed; preserve facts, unknowns, alternatives and earlier decisions.',
        source_commit='d6e0ea51b19a4786a11d816d16c8678f8e7b99ba',source_revision=digest(relevant(package)),
        review_revision=review['review_revision'],identities=[r['identity'] for r in review['periods']],
        decisions={r['decision_id']:{k:v for k,v in r.items() if k not in ('decision_id','status','accepted','approval_required')} for r in review['consolidated_proposals'] if r['approval_required']},
        financial_sufficiency='ONLY_APPROVED_HISTORICAL_PERIMETER',phase1_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def activate_company_history(package):
    parent={k:v for k,v in package.items() if k not in ('aapl_history_approval','aapl_current_history')}
    if review_company_history(parent)!=parent:raise ValueError('Changed AAPL source/company review')
    record=_json((ROOT/OUTPUT).read_text())['aapl_history_approval'];expected=history_approval_record(parent)
    if type(record) is not dict or set(record)!=set(expected) or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed AAPL history approval')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    for k in set(expected)-{'recorded_at_utc','sha256','source_revision','review_revision'}:
        if type(record[k]) is not type(expected[k]) or record[k]!=expected[k]:raise ValueError('Unregistered AAPL history approval: '+k)
    if any(record[k]!=expected[k] for k in ('source_revision','review_revision')):raise ValueError('Stale AAPL history approval; explicit revalidation required')
    if set(record['decisions'])!={f'A{i}' for i in range(2,11)} or parent['aapl_history_review']['outcomes']['ESSENTIAL_EVIDENCE_EXCEPTION']:raise ValueError('Incomplete AAPL authorization/evidence')
    periods=[]
    for i,row in enumerate(parent['aapl_history_review']['periods']):
        base=f'/aapl_history_review/periods/{i}';facts=row['facts'];calcs={c['input_id']:c for c in row['calculations']}
        def fact(key,multiplier=1):
            f=facts[key]
            return dict(value=str(Decimal(f['value'])*multiplier),unit=f['unit'],precision=f['precision'],origin='reported',raw_value=f['value'],multiplier=multiplier,as_of=f['as_of'],source_reference=base+'/facts/'+key)
        def calculation(key):
            return dict(calcs[key],source_reference=base+'/calculations/'+str(next(j for j,c in enumerate(row['calculations']) if c['input_id']==key)),review=APPROVED_SCOPE)
        checklist=[]
        if len(row['family_checklist'])!=14 or len({r['field'] for r in row['family_checklist']})!=14 or not row['cfo_reconciliation']['supported']:raise ValueError('AAPL checklist/reconciliation incomplete')
        for r in row['family_checklist']:
            if r['status'] not in ('SOURCE_SUPPORTED','EXISTING_SCOPED_APPROVAL','PROPOSED_PENDING_APPROVAL') or any(k not in record['decisions'] for k in r['pending_decisions']):raise ValueError('Unresolved AAPL family')
            checklist.append(dict(r,status='SATISFIED_BY_EXPLICIT_APPROVAL' if r['pending_decisions'] else 'SATISFIED_WITHIN_SOURCE_OR_PRIOR_SCOPE',approval_reference='/aapl_history_approval' if r['pending_decisions'] else r['existing_approval_reference']))
        inputs=dict(revenue=fact('revenue'),ebit=fact('ebit'),depreciation_amortization=dict(row['proposed_da_proxy'],accepted=True,status=APPROVED_SCOPE,approval_reference='/aapl_history_approval'),
            cash_capex=fact('PaymentsToAcquirePropertyPlantAndEquipment',-1),reported_cash_flow_working_capital_movements=dict(rows=row['movement_rows'],source_reference=base+'/cfo_reconciliation',additional_deduction_permitted=False),
            deferred_taxes=dict(selected=fact('deferred_cfo') if 'deferred_cfo' in facts else None,mixed_other=fact('OtherNoncashIncomeExpense',-1),deferred_provision=calculation('deferred_provision'),separate_pure_cfo_operation='reported_row' if 'deferred_cfo' in facts else 'APPROVED_EXCLUSION_UNKNOWN_COMPONENT'),
            stock_based_compensation=dict(selected=fact('AllocatedShareBasedCompensationExpense'),origin='proxy',count_once=True,addback=fact('ShareBasedCompensation')),
            unclassified_cfo_reconciliation_residual=dict(value=None,disposition='APPROVED_NO_SEPARATE_OPERATION',not_reported_zero=True),reported_cfo=fact('NetCashProvidedByUsedInOperatingActivities'),
            reported_tax_context=dict(provision=fact('IncomeTaxExpenseBenefit'),pretax=fact('pretax'),reported_etr=calculation('reported_etr'),cash_taxes=fact('IncomeTaxesPaidNet',-1),future_rate_approved=False),
            cash_investment_components=dict(selected=calculation('current_financial'),long_term=fact('long_securities'),known_restrictions_reference=base+'/note_observations',known_restriction_scope_support=base+'/comparative_scope_support' if i==3 else None,alternative_reference=base+'/restricted_current_alternative' if i==3 else None,unknown_restrictions=None,operating_reserve=None,unrestricted_or_excess_cash=False),
            debt_lease_components=dict(selected=calculation('named_financing'),additional_borrowing=None,no_additional_adjustment='Approved analyst assumption; omitted borrowing unbounded, not reported zero',complete_debt=False,operating_lease=fact('op_total'),all_lease_alternative=dict(calculation('all_lease_alternative'),default=False,selected=False),current_maturities_already_included=True),
            other_equity_bridge_claims_assets=dict(preferred=None,nci=None,pension=None,pure_nol=None,no_additional_adjustments='Approved analyst omissions, potentially undisclosed amounts unbounded, no immateriality finding',tax_credit_dta=fact('tax_credit_dta'),source_reference=base+'/partition_checks'),
            point_in_time_shares=dict(selected=fact('year_end_common'),cover=[fact(k) for k in facts if k.startswith('cover_common_')],awards=fact('rsu'),weighted_basic=fact('weighted_basic'),weighted_diluted=fact('weighted_diluted'),aggregation_or_dilution_approved=False))
        periods.append(dict(identity=row['identity'],inputs=inputs,checklist=checklist,analyst_complete=True,remaining_essential_inputs=[],
            supporting_unknowns=row['supporting_unknowns'],sources_reference=base+'/sources',supporting_investment_reference=base+'/facts',complete_expense_basis_da=None))
    if len(periods)!=5:raise ValueError('Five selected AAPL annuals required')
    result=json.loads(json.dumps(parent));result['aapl_history_approval']=record
    result['aapl_current_history']=dict(version=1,authoritative_current_view=True,periods=periods,company_completed_for_approved_historical_perimeter=True,
        family_slots=70,passed_family_slots=70,complete_expense_basis_da=None,complete_debt=False,complete_reinvestment=False,phase1_closed=False,valuation_consumption_approved=False,
        approval_sha256=record['sha256'],historical_proposal_snapshot='/aapl_history_review',
        company_counts=dict(broad_evidence_assessment=42,company_analyst_packages=3,completed_company_wide_packages=2,partial_company_packages=1,broad_assessment_only=39))
    return result


if __name__=='__main__':
    if '--record-approved-treatment-set' in sys.argv:
        if (ROOT/ACCEPTANCE_PATH).exists():raise SystemExit('Immutable AAPL acceptance record already exists')
        print(json.dumps(approval_record(build_proposal(),weighted_average_support()),sort_keys=True,indent=2))
        raise SystemExit(0)
    text=json.dumps(build(),sort_keys=True,indent=2)+'\n'
    if '--check' in sys.argv:
        if (ROOT/OUTPUT).read_text()!=text:raise SystemExit('AAPL package replay differs')
        print('Exact AAPL FY2025 package replay passed')
    else:print(text,end='')
