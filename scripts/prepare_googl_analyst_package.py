"""One retained Alphabet FY2024 decision package, never financial acceptance.

Reuse exact inspection and primary/instance validation, not peer assumptions.
Original partial/manual-note input and refreshed receipt history stay intact.
"""
from datetime import date
from decimal import Decimal
import hashlib
import json
import re
import sys

from prepare_msft_analyst_package import Filing, InlineFacts, ROOT, ACCEPTED, SUPPORTED, PROPOSED, inline_amount
from valuation_platform.analyst import googl_cash_flow_inputs as googl, cash_flow_inputs as cash
from valuation_platform.analyst import retained_components as inspect

OUTPUT='docs/company-data-preparation/googl-analyst-input-package.json'
BASELINE='44eab95cfbf38fa597927abb8ce7eb8f051d4a1e'
NWC_PATH='docs/company-data-preparation/googl-analyst-nwc-bundle.json'
NWC_SHA='a8a45520d79bdedbdeeae398c1ea16cbe3639e43fed4300998b109176e4aafdb'


class AlphabetFiling(Filing):
    def __init__(self):
        self.year=2024;self.bundle=googl.load_googl_bundle('googl-reported-cash-flow-fy2024')
        self.period=self.bundle.period
        self.root,self.contexts,self.units,self.namespaces=cash._instance(self.bundle.artifacts,self.period)
        self.primary,self.instance=self.bundle.artifacts
        self.inline=InlineFacts();self.inline.feed(self.primary.artifact.body.decode())
        self.text=re.sub(r'\s+',' ',' '.join(self.inline.text));self.facts={};self.entries=[]

    def entry(self,*args,**kwargs):
        super().entry(*args,**kwargs)
        self.entries[-1]['formula_version']='googl-draft-historical-v1'


def variants(f,evidence,key,concept):
    """Keep differing precision/value candidates; no implicit financial selection."""
    spec=inspect.SelectionSpec(key,(inspect.Selector(f.namespaces['us-gaap'],concept,()),),
        'instant','USD','precision_alternatives','Same-concept observations; no selected value or added aggregate',())
    result=inspect.inspect(evidence,spec);rows=[]
    for candidate in result.candidates:
        occurrences=[]
        for o in candidate.occurrences:
            node=f.root[o.ordinal];attrs,text=f.inline.facts[node.get('id')]
            if (attrs['name'].split(':')[-1]!=concept or attrs['contextref']!=o.context_id
                or attrs['unitref']!=o.unit_id or attrs['decimals']!=o.decimals
                or inline_amount(attrs,text)!=Decimal(o.raw_value)):
                raise ValueError('Primary/instance precision alternative mismatch')
            occurrences.append(dict(ordinal=o.ordinal,context_id=o.context_id,xml_id=node.get('id'),
                primary_locator='inline#'+node.get('id'),raw_value=o.raw_value,precision=o.decimals,
                unit_id=o.unit_id,start=None,end=str(o.end),dimensions=list(o.dimensions),
                primary_display=text,primary_scale=int(attrs.get('scale','0')),primary_sign=attrs.get('sign','+')))
        rows.append(dict(concept=concept,namespace=candidate.namespace,value=str(candidate.value),unit='USD',
            precision=candidate.precision,occurrences=occurrences,primary_source='FY2024-primary',instance_source='FY2024-instance'))
    return dict(candidates=rows,competing_values=[str(v) for v in result.competing_values],
        unresolved_requirements=list(result.unresolved_requirements),selected_value=None,
        treatment='Retain every representation; precision difference is not an adjustment or automatic selection.')


def build():
    f=AlphabetFiling();doc=googl._registry()
    nwc_body=(ROOT/NWC_PATH).read_bytes()
    if hashlib.sha256(nwc_body).hexdigest()!=NWC_SHA:raise ValueError('Original rounded-note scenario changed')
    old=json.loads(nwc_body);note=old['bundle']['rounded_note_input']
    accepted={'NetCashProvidedByUsedInOperatingActivities','PaymentsToAcquirePropertyPlantAndEquipment',
        'AllocatedShareBasedCompensationExpense','IncomeTaxesPaidNet','OperatingLeasePayments',
        'FinanceLeaseInterestPaymentOnLiability','FinanceLeasePrincipalPayments'}
    for item in f.bundle.inputs:
        f.fact(item.input_id,item.input_id,item.location_and_scope,namespace=item.occurrences[0].namespace)
        f.entry('reported:'+item.input_id,item.input_id,[item.input_id],[item.display_multiplier],
            scope=item.location_and_scope,role=item.kind.value,status=ACCEPTED if item.input_id in accepted else SUPPORTED,
            rationale='Retain Alphabet original role/precision; existing acceptance is scope-specific, no adjustment.',
            completeness='reported_population_only')
    specs=[
        ('revenue','RevenueFromContractWithCustomerExcludingAssessedTax','Income statement / Notes 2 and 15',False),
        ('ebit','OperatingIncomeLoss','Income statement / Note 15',False),
        ('pretax','IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest','Income statement / Note14',False),
        ('nonoperating','NonoperatingIncomeExpense','Income statement / Note7',False),
        ('ar','AccountsReceivableNetCurrent','Balance sheet net customer AR',True),
        ('ap','AccountsPayableCurrent','Whole supplier AP; remaining scope unproved',True),
        ('compensation','EmployeeRelatedLiabilitiesCurrent','Separate accrued compensation/benefits, not SBC expense',True),
        ('revenue_share','AccruedRevenueShare','Separate accrued partner revenue share',True),
        ('current_deferred','ContractWithCustomerLiabilityCurrent','Current customer advances, not backlog',True),
        ('customer_liability','AccruedCustomerLiabilitiesCurrent','Note7 subcaption inside accrued current parent',True),
        ('other_current_assets','OtherAssetsCurrent','Mixed other current assets; inventory allocation unproved',True),
        ('accrued_current_parent','AccruedLiabilitiesCurrent','Mixed accrued expenses/other current parent, overlaps customer/lease/tax/debt children',True),
        ('accrued_ppe','AccruedPurchasesOfPropertyAndEquipmentCurrent','Note7 separate accrued PP&E, not additional PP&E in AP',True),
        ('ap_note_source','CapitalExpendituresIncurredButNotYetPaid','Note7 duration-tagged source for reviewed rounded manual closing interpretation',False),
        ('cash','CashAndCashEquivalentsAtCarryingValue','Balance sheet / Note3 cash and equivalents',True),
        ('current_marketable','MarketableSecuritiesCurrent','Balance sheet current marketable securities',True),
        ('current_financial_parent','CashCashEquivalentsAndShortTermInvestments','Balance sheet named current cash/marketable parent',True),
        ('long_marketable','MarketableSecuritiesNoncurrent','Note3 long-term lock-up-restricted marketable equity within other noncurrent assets, not current cash',True),
        ('nonmarketable_parent','OtherLongTermInvestments','Balance sheet non-marketable securities, not unrestricted cash',True),
        ('equity_method','EquityMethodInvestments','Note3 rounded equity-method population; overlap with nonmarketable parent',True),
        ('listed_equity','EquitySecuritiesFvNi','Note3 fair-value equity population; overlap with financial captions unbridged',True),
        ('restricted_combined','CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents','Cash-flow closing combined cash/restricted caption, not standalone restricted cash',True),
        ('cp','CommercialPaper','Note6 CP point, source decimals INF and displayed2.3bn; not all debt',True),
        ('term_face','LongTermDebt','Note6 face/principal caption, not net carrying',True),
        ('debt_discount_signed','DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet','Note6 signed deduction from face',True),
        ('term_current','LongTermDebtCurrent','Note6 current term carrying within accrued current parent',True),
        ('term_long','LongTermDebtNoncurrent','Note6 net noncurrent term carrying',True),
        ('debt_fair','LongTermDebtFairValue','Note6 rounded fair-value observation, not carrying',True),
        ('op_current','OperatingLeaseLiabilityCurrent','Note4 current operating lease within accrued parent',True),
        ('op_long','OperatingLeaseLiabilityNoncurrent','Separate noncurrent operating lease face caption',True),
        ('op_total','OperatingLeaseLiability','Note4 discounted operating liability',True),
        ('finance_current','FinanceLeaseLiabilityCurrent','Note4 current finance liability within accrued parent',True),
        ('finance_long','FinanceLeaseLiabilityNoncurrent','Note4 finance noncurrent within other long-term liabilities, NOT term-debt caption',True),
        ('finance_total','FinanceLeaseLiability','Note4 discounted finance total',True),
        ('finance_rou','FinanceLeaseRightOfUseAsset','Note4 net finance asset within PP&E',True),
        ('finance_rou_gross','FinanceLeaseRightOfUseAssetBeforeAccumulatedAmortization','Note4 gross finance asset',True),
        ('finance_rou_accum','FinanceLeaseRightOfUseAssetAccumulatedAmortization','Note4 accumulated finance amortization',True),
        ('op_maturities','LesseeOperatingLeaseLiabilityPaymentsDue','Note4 future undiscounted maturities, not annual cash',True),
        ('finance_maturities','FinanceLeaseLiabilityPaymentsDue','Note4 future undiscounted maturities, not annual cash',True),
        ('op_imputed','LesseeOperatingLeaseLiabilityUndiscountedExcessAmount','Note4 future imputed interest, not current cash',True),
        ('finance_imputed','FinanceLeaseLiabilityUndiscountedExcessAmount','Note4 future imputed interest, not current cash',True),
        ('nci_vie','NoncontrollingInterestInVariableInterestEntity','Note5 rounded total NCI in consolidated subsidiaries, includes redeemable portion',True),
        ('redeemable_nci','RedeemableNoncontrollingInterestInVariableInterestEntity','Note5 redeemable NCI SUBSET of total NCI; do not add again',True),
        ('vie_funding','UnconsolidatedVariableInterestEntityFutureFundingCommitments','Note5 future funding commitment, not funded debt',True),
        ('ec_fines','LossContingencyAccrualCarryingValueCurrent','Note7 EC fines including FX/interest within accrued current parent',True),
        ('tax_current','AccruedIncomeTaxesCurrent','Note7 current tax within accrued current parent',True),
        ('tax_long','AccruedIncomeTaxesNoncurrent','Noncurrent taxes outside narrow capital schedule',True),
        ('nol_dta','DeferredTaxAssetsOperatingLossCarryforwards','Note14 gross loss DTA, before valuation allowance; not equity value',True),
        ('preferred_value','ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue','Balance sheet explicitly reported preferred stock value zero',True),
        ('reported_common_total','CommonStockSharesOutstanding','Reported aggregate year-end common observation, not a computed class sum',True),
        ('weighted_basic','WeightedAverageNumberOfSharesOutstandingBasic','Note12 annual weighted-average EPS count, not closing shares',False),
        ('weighted_diluted','WeightedAverageNumberOfDilutedSharesOutstanding','Note12 annual diluted EPS denominator, not point-in-time or forecast dilution',False),
    ]
    ext={'revenue_share','customer_liability','accrued_ppe','redeemable_nci','vie_funding'}
    for key,concept,scope,instant in specs:
        f.fact(key,concept,scope,namespace='goog' if key in ext else 'us-gaap',instant=instant,
            unit='shares' if key=='reported_common_total' or key.startswith('weighted_') else 'USD')
    for label,member in [('a','us-gaap:CommonClassAMember'),('b','us-gaap:CommonClassBMember'),('c','goog:CapitalClassCMember')]:
        dims=(('us-gaap:StatementClassOfStockAxis',member),)
        f.fact('year_end_'+label,'CommonStockSharesOutstanding','Balance sheet distinct year-end class '+label.upper(),instant=True,unit='shares',dimensions=dims)
        f.fact('cover_'+label,'EntityCommonStockSharesOutstanding','Cover distinct class '+label.upper()+', actual 2025-01-28 date',
            instant=True,unit='shares',namespace='dei',as_of='2025-01-28',dimensions=dims)
    awards=(('us-gaap:AwardTypeAxis','us-gaap:RestrictedStockUnitsRSUMember'),)
    for key,concept,unit in [('rsu','ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber','shares'),
        ('future_sbc','EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized','USD')]:
        f.fact(key,concept,'Note13 Alphabet unvested RSU population; future issuance Class C per note, actual dimensions retained',instant=True,unit=unit,dimensions=awards)
    if (note['value_usd']!=f.facts['ap_note_source']['value'] or note['source_occurrence']['decimals']!='-8'
        or note['scope_assertion'] not in f.text or note['source_occurrence']['context_id']!='c-1'):
        raise ValueError('Reviewed manual closing-note source or meaning changed')
    def calc(key,terms,scope,*,status=SUPPORTED,partial=False,formula=None):
        f.entry(key,scope,[k for k,c in terms],[c for k,c in terms],status=status,scope=scope,rationale=scope,
            completeness='partial' if partial else 'complete_for_named_population',
            formula=formula,unit='pure' if formula=='DIVIDE' else None,
            policy='annual_reported_effective_tax_rate_v1' if formula=='DIVIDE' else None)
    base=[('ar',1),('ap',-1),('current_deferred',-1),('compensation',-1),('revenue_share',-1),('customer_liability',-1)]
    calc('whole_ap_partial',base,'Whole-AP partial current book comparator excluding inventory/other assets',partial=True)
    calc('proposed_rounded_partial',base+[('ap_note_source',1)],'Recommended partial current operating-capital schedule with reviewed rounded manual closing-note adjustment',status=PROPOSED,partial=True)
    f.entries[-1].update(manual_operand_ids=[note['component_id']],manual_note_reference='/manual_note_input',
        role='partial_book_schedule_with_reviewed_manual_note',
        precision=dict(operand_decimals=[f.facts[k]['precision'] for k,c in base]+['-8'],
            treatment='Manual closing interpretation of duration-tagged rounded note; arithmetic does not create an instant XBRL fact or improve precision.'))
    calc('alternative_operating_fines',base+[('ap_note_source',1),('ec_fines',-1)],
        'Alternative classify EC fines as ordinary operating accrual, still rounded partial capital',status=PROPOSED,partial=True)
    f.entries[-1].update(manual_operand_ids=[note['component_id']],manual_note_reference='/manual_note_input',
        role='partial_book_alternative_with_reviewed_manual_note')
    calc('current_financial',[('cash',1),('current_marketable',1)],'Named current cash/marketable captions; not unrestricted/excess cash')
    calc('term_net',[('term_face',1),('debt_discount_signed',1)],'Note6 principal plus signed discount, net term carrying')
    calc('term_parts',[('term_current',1),('term_long',1)],'Term current plus noncurrent, not finance leases')
    calc('named_borrowing',[('term_current',1),('term_long',1),('cp',1)],'Named term carrying plus CP only')
    calc('proposed_financing',[('term_current',1),('term_long',1),('cp',1),('finance_total',1)],'Proposed term+CP+finance-lease financing subtotal only',status=PROPOSED)
    calc('alternative_all_leases',[('term_current',1),('term_long',1),('cp',1),('finance_total',1),('op_total',1)],'Alternative all-lease obligation perimeter, not complete debt',status=PROPOSED)
    for prefix in ('op','finance'):
        calc(prefix+'_partition',[(prefix+'_current',1),(prefix+'_long',1)],'Note4 discounted '+prefix+' liability partition')
        calc(prefix+'_discounted',[(prefix+'_maturities',1),(prefix+'_imputed',-1)],'Note4 future maturity less imputed interest; not historical cash')
    calc('finance_asset_partition',[('finance_rou_gross',1),('finance_rou_accum',-1)],'Note4 finance asset net partition, not expense D&A')
    calc('reported_etr',[('IncomeTaxExpenseBenefit',1),('pretax',1)],'Historical accounting provision / positive reported pretax; no future rate',formula='DIVIDE')
    entries={v['input_id']:v for v in f.entries};checks=[]
    val=lambda k:Decimal(f.facts[k]['value'])
    def eq(name,left,right):
        if left!=right:raise ValueError('Alphabet check failed: '+name)
        checks.append(dict(check_id=name,observed=str(left),expected=str(right),difference='0',result='PASS'))
    for key,parent in [('current_financial','current_financial_parent'),('term_net',None),('term_parts',None),
        ('op_partition','op_total'),('finance_partition','finance_total'),('op_discounted','op_total'),
        ('finance_discounted','finance_total'),('finance_asset_partition','finance_rou')]:
        eq(key,Decimal(entries[key]['value']),val(parent) if parent else Decimal('11882000000'))
    eq('rounded_partial_replays_original',Decimal(entries['proposed_rounded_partial']['value']),Decimal(old['bundle']['expected_partial_usd']))
    eq('ebit_to_pretax',val('ebit')+val('nonoperating'),val('pretax'))
    eq('tax_to_net',val('pretax')-val('IncomeTaxExpenseBenefit'),val('NetIncomeLoss'))
    eq('displayed_cfo',sum((Decimal(entries['reported:'+k]['value']) for k in f.bundle.cfo_terms),Decimal(0)),val('NetCashProvidedByUsedInOperatingActivities'))
    f.fact('debt_repayments','RepaymentsOfDebtAndCapitalLeaseObligations','Face financing debt repayments already includes finance principal405')
    passages=[]
    for marker in (note['scope_assertion'],'Finance lease liabilities are included in accrued expenses',
        'Total current portion of long-term debt is included within accrued expenses',
        'Financing cash flows used for financing leases are included within financing activities',
        'Net of effects of acquisitions','an RSU award is an agreement to issue shares of our Class C stock',
        'inventory and other costs related to the devices we sell',
        'We paid Character $ 2.7 billion in cash and canceled our convertible instruments.',
        'subject to long-term lock-up restrictions','of which $ 1.1 billion was redeemable noncontrolling interests'):
        match=re.search(re.escape(marker),f.text,re.I)
        if not match:raise ValueError('Required Alphabet scope passage absent: '+marker)
        passages.append(dict(source='FY2024-primary',offset=match.start(),exact_excerpt=f.text[max(0,match.start()-60):match.end()+230]))
    evidence=inspect.prepare(f.period,f.bundle.artifacts,tuple(inspect.ArtifactBinding(r.artifact.url,r.artifact.sha256,
        'instance' if r is f.instance else 'support') for r in f.bundle.artifacts))
    precision_candidates={key:variants(f,evidence,key,concept) for key,concept in (
        ('nonmarketable_equity','EquitySecuritiesWithoutReadilyDeterminableFairValueAmount'),('uncertain_tax','UnrecognizedTaxBenefits'))}
    sources=[];original_manifest=json.loads((ROOT/doc['artifact_manifest_path']).read_text())
    for kind,receipt in [('primary',f.primary),('instance',f.instance)]:
        a=receipt.artifact
        pointer='/artifacts/0' if kind=='instance' else '/artifacts/'+str(next(i for i,v in enumerate(original_manifest['artifacts']) if v['source_url']==a.url))
        sources.append(dict(source_id='FY2024-'+kind,url=a.url,accession=a.accession,sha256=a.sha256,
            retained_path=doc['refresh_manifest_path'] if kind=='instance' else doc['artifact_manifest_path'],retained_pointer=pointer,
            representation=a.representation,digest_type=a.digest_type,byte_length=receipt.byte_length,
            retrieved_at_utc=receipt.retrieved_at_utc,http_status=receipt.http_status,
            basis='explicit_refresh_not_recovered_original_metadata' if kind=='instance' else 'original_receipt'))
    return dict(schema='googl-draft-analyst-historical-package-v1',version=1,baseline_revision=BASELINE,
        issuer='Alphabet (GOOG/GOOGL)',phase='1',financial_sufficiency='NOT_ASSESSED',valuation_consumption_approved=False,
        new_sec_requests=0,identity=dict(cik=f.period.cik,accession=f.period.accession,form=f.period.form,
            annual_start=str(f.period.annual_start),annual_end=str(f.period.annual_end)),
        sources=sources,evidence_history=googl._history(doc,f.bundle.artifacts),facts=f.facts,inputs=f.entries,
        manual_note_input=note,original_nwc=dict(path=NWC_PATH,sha256=NWC_SHA),checks=checks,scope_passages=passages,
        precision_candidates=precision_candidates,original_bundle_unknowns=[dict(input_id=u.input_id,reason=u.reason) for u in f.bundle.unknowns],
        overlap_relationships=[dict(parent='accrued_current_parent',children=['customer_liability','op_current','finance_current','term_current','cp','accrued_ppe','ec_fines','tax_current'],coverage='partial; never add parent and children'),
            dict(parent='debt_repayments',child='FinanceLeasePrincipalPayments',amount_usd='405000000',handling='Already included in12701; never add405 again.'),
            dict(parent='nci_vie',child='redeemable_nci',handling='Note5 explicitly says of which;1100R included in4200R, no sum.'),
            dict(parent='nonmarketable_parent',children=['equity_method','precision_candidates/nonmarketable_equity'],coverage='overlapping/incomplete; no sum')],
        unresolved_requirements=UNKNOWN,approval_sheet=APPROVAL_SHEET,manual_inputs=[note['component_id']],estimates=[],
        preserved_acceptance_reference='docs/googl-treatment-acceptance-checklist.md',adjacent_book_movement=None,
        stopping_condition='One consolidated user review; no automatic research, treatment integration, Phase 1 closure or Phase 2.')


UNKNOWN=[dict(input_id=k,value=None,reason=v,status='unresolved_requirement') for k,v in (
    ('expense_da','Complete income-recognized D&A/finite-lived amortization and lease/inventory overlap unavailable. CFO depreciation15311 and finance ROU amortization413 do not prove completeness/non-overlap.'),
    ('inventory','No separately evidenced complete inventory amount in this retained perimeter. Device inventory costs exist; absence is not zero.'),
    ('supplier_ap','Rounded manual correction3200 does not prove remaining supplier AP operating-only; no residual allocation.'),
    ('other_operating_capital','Other current/noncurrent operating allocations and acquisition/FX/noncash/reclass cash bridge unavailable. One level, no delta NWC.'),
    ('cash_interest','Borrowing interest cash unavailable; expense268 and capitalized expense194 do not provide a cash bridge or lease-overlap proof.'),
    ('complete_lease_cash','Restricted cash classes accepted; complete variable/nonlease cash and expense conversion unproved. Principal405 already within debt repayments.'),
    ('investment_allocations','Combined acquisition/intangible cash2931 and Other2667 unallocated; no complete accrual/organic bridge from cash and capital creditors.'),
    ('cash_availability','Restricted/operating-reserve allocations unproved. Combined cash/restricted caption equality does not establish standalone restricted cash0.'),
    ('claims','NCI4200R includes redeemable1100R; other claims, valuation and exhaustive claim coverage unproved. No automatic all-claims total or valuation.'),
)]


APPROVAL_SHEET=[dict(decision_id=k,status=PROPOSED,recommendation=r,numeric_effect=n,alternative=a,limitations=l,accepted=False)
    for k,r,n,a,l in (
    ('OPERATING-CAPITAL','Retain rounded corrected partial current operating-capital perimeter, inventory/other mixed captions unresolved.',
     '13342 USDm; whole-AP comparator10142; rounded difference3200.',
     'Whole AP10142 avoids manual correction but includes known capital obligation3200; treating fines as ordinary accrual gives7020R (-6322). Do not add separate accrued PP&E7104 to AP correction.',
     'Manual closing interpretation retained, not an instant fact or numerical estimate. No zero inventory, complete operating AP or movement.'),
    ('LEASE-DA','Operating leases service, finance leases asset financing based on Alphabet Note1/4 locations. Leave complete expense D&A unresolved.',
     'Finance liability1677 separate from term/CP; CFO depreciation15311 and finance ROU amortization413 support only, no sum.',
     'All-lease obligations add14578; cash-service conversion needs verified annual expense/cash/overlap basis.',
     'No inherited D&A inclusion assumption. Three accepted restricted cash classes stay separate; finance principal405 already inside12701 debt repayments.'),
    ('INVESTMENT','Keep accepted cash PP&E52535, combined acquisition/intangible2931, Other2667, noncash op2510/finance313 and capital creditors separately.',
     'Cash purchases negative; additions/stocks positive. Manual AP3200R distinct from accrued PP&E7104.',
     'Broader combined purchase scope adds2931 but cannot be called organic/PP&E or allocated using Character2700R.',
     'No complete reinvestment or cash/accrual bridge; canceled instruments and recognized intangibles are not proven cash.'),
    ('CASH-DEBT-CLAIMS','Use reported current financial parent95657; strategic/nonmarketable and noncurrent marketable components separate. Propose named term+CP+finance subtotal.',
     'Term net11882+CP2300=14182; plusfinance1677=15859; all-lease30437.',
     'Term principal12000 versus carrying11882, fair9000R; investment35500R/35531 both retained, not summed or silently substituted.',
     'Not excess/unrestricted cash or complete debt. NCI4200R includes redeemable1100R; commitments1500R are future funding, not debt. Lock-up restricted long marketable266 separate. EC fines6322 separate recorded claim, no double count.'),
    ('SBC-TAX','Preserve accepted rounded SBC expense22800R once and separate CFO add-back22785. Retain historical provision/ETR/cash/deferred roles.',
     'Provision19697; Pretax119815; cash tax27400R; deferred provision-5256 versus CFO-5257.',
     'No15 SBC rounding adjustment or1 deferred-tax plug; no cash-interest proxy or future operating rate.',
     'Original approvals retained, not reopened. Expense, cash, credits and deferred balances have different scopes.'),
    ('SHARES-AWARDS','Keep year-end and cover class A/B/C observations separate; retain reported issuer total as source observation only and RSUs separately.',
     'Year-end A5835m/B861m/C5515m; cover2025-01-28 A5833m/B860m/C5497m; RSUs299m, futurecost34800R USDm.',
     'Reported total12211m is not a new class sum or diluted total; later class counts are alternative dates, not a dilution bridge.',
     'No class equivalence, automatic class/award sum, RSU valuation or forecast dilution; stock plans authorize Class C issuance but source dimensions stay unchanged.'),
)]


if __name__=='__main__':
    text=json.dumps(build(),sort_keys=True,indent=2)+'\n'
    if '--check' in sys.argv:
        if (ROOT/OUTPUT).read_text()!=text:raise SystemExit('Alphabet package replay differs')
        print('Exact Alphabet FY2024 package replay passed')
    else:print(text,end='')
