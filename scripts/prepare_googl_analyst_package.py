"""One retained Alphabet FY2024 package and scoped user-approved selection view.

Reuse exact inspection and primary/instance validation, not peer assumptions.
Original partial/manual-note input and refreshed receipt history stay intact.
"""
from datetime import date, datetime, timezone
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import re
import sys

from prepare_msft_analyst_package import Filing, InlineFacts, ROOT, ACCEPTED, SUPPORTED, PROPOSED, inline_amount
from prepare_msft_analyst_package import APPROVED_SCOPE, relevant, digest, _json, ManualIdentity
from valuation_platform.analyst import googl_cash_flow_inputs as googl, cash_flow_inputs as cash
from valuation_platform.analyst import retained_components as inspect

OUTPUT='docs/company-data-preparation/googl-analyst-input-package.json'
BASELINE='44eab95cfbf38fa597927abb8ce7eb8f051d4a1e'
ACCEPTANCE_BASIS='3422da1a9a369055b0b7cdc6197610112b9fd47f'
ACCEPTANCE_PATH='docs/company-data-preparation/googl-analyst-treatment-acceptance.json'
USER_DECISIONS={
    'OPERATING-CAPITAL':'Select rounded partial current operating capital13342 USDm including reviewed manual-note3200; whole AP/fines alternatives non-default; inventory/supplier/other allocations unknown; no opening or delta/completeness.',
    'LEASE-FINANCING':'Operating service / finance asset financing; named term+CP+finance15859 USDm only, all-lease30437 non-default; principal405 already within repayments12701; no complete debt, lease cash or borrowing interest.',
    'DA-INVESTMENT':'CFO depreciation15311 and finance amortization413 separate; complete expense D&A null; cash PP&E52535, combined2931, Other2667, creditors and noncash additions separate with source signs; no sum or inclusion assumption.',
    'FINANCIAL-CLAIMS':'Select current financial95657, not unrestricted/excess; restricted266 and strategic/precision alternatives separate; NCI4200 includes redeemable1100, never5300; claims/commitments separate, no net debt or exhaustive coverage.',
    'HISTORICAL-SCHEDULES':'Revenue350018, EBIT112390, CFO125299; accepted rounded SBC expense22800 once versus add-back22785; historical tax roles and dated classes/source aggregate/EPS/awards separate; no future rate, interest proxy, rounding plug or dilution.'}
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


def build_proposal():
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


def approval_record(proposal):
    """Explicit user recording; replay never creates or renews acceptance."""
    record=dict(schema='googl-treatment-acceptance-audit-v1',version=1,sequence=1,previous='0'*64,
        action='ACCEPT_SCOPED_SELECTIONS',author='User, explicit Alphabet FY2024 approved-selection instruction',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Record only the approved Alphabet historical selections; preserve unavailable amounts, prior proposals and original blockers.',
        authority='Current user instruction: Implement the user-approved Alphabet FY2024 selections.',
        source_commit=ACCEPTANCE_BASIS,source_revision=digest(relevant(proposal)),decisions=USER_DECISIONS.copy(),
        financial_sufficiency='NOT_ASSESSED',phase1_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def accepted_view(proposal,audit_path=None):
    """Report-only selection overlay, not runtime policy or CF-movement override."""
    path=Path(audit_path) if audit_path is not None else ROOT/ACCEPTANCE_PATH
    record=_json(path.read_text())
    expected={'schema','version','sequence','previous','action','author','recorded_at_utc','rationale','authority',
        'source_commit','source_revision','decisions','financial_sufficiency','phase1_closed','valuation_consumption_approved','sha256'}
    if type(record) is not dict or set(record)!=expected or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):
        raise ValueError('Changed or malformed Alphabet acceptance audit')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    if (record['schema']!='googl-treatment-acceptance-audit-v1' or type(record['version']) is not int or record['version']!=1
        or type(record['sequence']) is not int or record['sequence']!=1 or record['previous']!='0'*64
        or record['action']!='ACCEPT_SCOPED_SELECTIONS' or record['source_commit']!=ACCEPTANCE_BASIS
        or record['decisions']!=USER_DECISIONS or record['financial_sufficiency']!='NOT_ASSESSED'
        or record['phase1_closed'] is not False or record['valuation_consumption_approved'] is not False):
        raise ValueError('Unregistered Alphabet acceptance scope')
    if record['source_revision']!=digest(relevant(proposal)):
        raise ValueError('Stale Alphabet acceptance: source, candidates, scope or evidence changed; explicit revalidation required')
    entries={e['input_id']:e for e in proposal['inputs']}
    def select(key,label):
        original=entries[key];selected=json.loads(json.dumps(original))
        selected.update(status=APPROVED_SCOPE,accepted=True)
        return dict(selected=selected,label=label,source_status=original['status'],
            source_reference='/inputs/'+str(next(i for i,e in enumerate(proposal['inputs']) if e['input_id']==key)),
            approval_sha256=record['sha256'],review=APPROVED_SCOPE)
    def fact(key):
        return dict(source_reference='/facts/'+key,observation=proposal['facts'][key])
    unknown={u['input_id']:u for u in proposal['unresolved_requirements']}
    view=dict(schema='googl-accepted-historical-view-v1',version=1,approval_audit=record,identity=proposal['identity'],
        operating_capital=select('proposed_rounded_partial','Partial current operating capital; inherited rounded precision'),
        manual_note_input=proposal['manual_note_input'],complete_operating_capital=False,opening_balance=None,
        book_delta_nwc=None,cash_delta_nwc=None,
        nondefault_history=[dict(default=False,observation=entries[k],source_reference='/inputs/'+str(next(i for i,e in enumerate(proposal['inputs']) if e['input_id']==k)))
            for k in ('whole_ap_partial','alternative_operating_fines','alternative_all_leases')],
        lease_classification=dict(operating='service_cost',finance='asset_financing',review=APPROVED_SCOPE,
            complete_lease_coverage=False,finance_amortization_inclusion_assumption=None),
        borrowings=select('proposed_financing','Named term-debt + CP + finance-lease liability subtotal'),complete_debt=False,
        finance_principal_already_in_debt_repayments=True,
        lease_cash_and_debt_repayments=[entries['reported:'+k] for k in ('OperatingLeasePayments',
            'FinanceLeaseInterestPaymentOnLiability','FinanceLeasePrincipalPayments','RepaymentsOfDebtAndCapitalLeaseObligations')],
        current_financial_balances=select('current_financial','Current financial balances; not unrestricted/excess cash'),
        separate_investments=[fact(k) for k in ('long_marketable','nonmarketable_parent','equity_method','listed_equity','restricted_combined')],
        precision_candidates=proposal['precision_candidates'],unrestricted_or_excess_cash=False,unknown_restrictions=None,operating_reserve=None,
        da_observations=[entries['reported:'+k] for k in ('Depreciation','FinanceLeaseRightOfUseAssetAmortization')],
        complete_expense_basis_da=unknown['expense_da'],additional_rou_addback=False,
        investment_columns=[entries['reported:'+k] for k in ('PaymentsToAcquirePropertyPlantAndEquipment',
            'AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets','PaymentsForProceedsFromOtherInvestingActivities',
            'RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability','RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability')],
        capital_creditor_observations=[fact('accrued_ppe'),fact('ap_note_source')],complete_reinvestment=False,
        separate_claims=[fact(k) for k in ('nci_vie','redeemable_nci','ec_fines','tax_current','tax_long','nol_dta','vie_funding','preferred_value')],
        nci_includes_redeemable=True,exhaustive_claims=False,overlap_relationships=proposal['overlap_relationships'],
        historical_income=[select('reported:NetCashProvidedByUsedInOperatingActivities','Consolidated reported CFO'),
            dict(**fact('revenue'),review=APPROVED_SCOPE),dict(**fact('ebit'),review=APPROVED_SCOPE)],
        sbc_expense_proxy=select('reported:AllocatedShareBasedCompensationExpense','Rounded recognized SBC expense proxy counted once'),
        sbc_cfo_addback=entries['reported:ShareBasedCompensation'],
        historical_taxes=[entries[k] for k in ('reported:IncomeTaxExpenseBenefit','reported:IncomeTaxesPaidNet','reported_etr',
            'reported:DeferredIncomeTaxExpenseBenefit','reported:DeferredIncomeTaxesAndTaxCredits')],
        separate_shares_and_awards=[fact(k) for k in ('year_end_a','year_end_b','year_end_c','cover_a','cover_b','cover_c',
            'reported_common_total','weighted_basic','weighted_diluted','rsu','future_sbc')],
        unresolved_requirements=proposal['unresolved_requirements'],original_bundle_unknowns=proposal['original_bundle_unknowns'],
        evidence_history=proposal['evidence_history'],prior_proposals_retained=True,
        decision_statuses={key:APPROVED_SCOPE for key in USER_DECISIONS},financial_sufficiency='NOT_ASSESSED',
        valuation_consumption_approved=False,phase1_closed=False,future_tax_assumption_approved=False,
        award_valuation_approved=False,dilution_estimate_approved=False,
        stopping_condition='Stop after Alphabet integration and consolidated pilot assessment; no automatic issuer work or closure.')
    result=json.loads(json.dumps(proposal));result['accepted_view']=json.loads(json.dumps(view))
    return result


def build():
    return activate_company_history(review_company_history(accepted_view(build_proposal())))


def review_company_history(package):
    """Bounded retained-source review, never new approval or a peer assumption."""
    parent={k:v for k,v in package.items() if k!='googl_history_review'}
    reviewed=accepted_view(build_proposal())
    if reviewed!=parent:raise ValueError('Changed original Alphabet source/approval')
    manifest=_json((ROOT/'docs/phase1-selected-filing-identity-manifest.json').read_text())
    selected=[(i,r) for i,r in enumerate(manifest['rows']) if r['ticker']=='GOOGL']
    if len(selected)!=5 or len({r['identity']['accession'] for i,r in selected})!=5:raise ValueError('Frozen Alphabet selections differ')
    old_path='docs/evidence/analyst-operating-nwc-response-bodies.json';old=_json((ROOT/old_path).read_text())['artifacts']
    refresh_path='docs/evidence/income-sweep-backlog-acquisition.json';refresh_body=(ROOT/refresh_path).read_bytes()
    config=_json((ROOT/'docs/retained-income-sweep-sources.json').read_text())
    if hashlib.sha256(refresh_body).hexdigest()!=config[refresh_path]:raise ValueError('Pinned retained receipt batch changed')
    refresh=_json(refresh_body.decode());rows=[];acquisition=[]
    for index,selection in selected:
        identity=selection['identity'];year=int(identity['annual_end'][:4]);original=[(i,a) for i,a in enumerate(old) if a.get('accession')==identity['accession']]
        primary=next(((i,a) for i,a in original if a['source_url'].endswith('.htm')),None)
        instance=next(((i,a) for i,a in original if a['source_url'].endswith('_htm.xml')),None)
        if primary is None or instance is None:raise ValueError('Retained selected primary/instance reference absent: '+identity['accession'])
        receipts=[];sources=[]
        for kind,(i,a) in [('primary',primary),('instance',instance)]:
            path=old_path;pointer='/artifacts/'+str(i);basis='original_receipt';original_a=a
            if kind=='instance' and year==2024:
                path='docs/evidence/googl-fy2024-instance-provenance-refresh.json';a=_json((ROOT/path).read_text())['artifacts'][0];pointer='/artifacts/0';basis='explicit_FY2024_refresh_not_recovered_original_metadata'
            elif kind=='instance':
                proof=[r for r in refresh['rows'] if r['identity']==identity and r['status']=='VERIFIED']
                matches=[(j,v) for j,v in enumerate(refresh['artifacts']) if v['source_url']==a['source_url']]
                if len(proof)!=1 or len(matches)!=1:raise ValueError('Exact previously verified instance receipt unavailable: '+identity['accession'])
                j,a=matches[0];path=refresh_path;pointer='/artifacts/'+str(j);basis='existing_authorized_refresh_not_recovered_original_metadata'
            encoded=a['response_body_gzip_base64']
            body=cash.gzip.decompress(cash.base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded,validate=True))
            receipt=cash._receipt(dict(a,accession=identity['accession']),body)
            original_body=cash.gzip.decompress(cash.base64.b64decode(original_a['response_body_gzip_base64'],validate=True))
            if body!=original_body:raise ValueError('Refreshed selected body differs from original; no new acceptance authorized')
            receipts.append(receipt);sources.append(dict(source_id=f'FY{year}-'+kind,path=path,pointer=pointer,
                **{k:a[k] for k in ('source_url','sha256','representation','digest_type','retrieved_at_utc','http_status','byte_length')},basis=basis,
                prior_reference=old_path+'#/artifacts/'+str(i),original_retrieved_at_utc=original_a['retrieved_at_utc'],original_http_status=original_a['http_status'],original_sha256=original_a['sha256'],byte_equivalence_verified=True))
        f=AlphabetFiling.__new__(AlphabetFiling);f.year=year;f.period=cash.Period(identity['cik'],identity['accession'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']))
        f.primary,f.instance=receipts;f.root,f.contexts,f.units,f.namespaces=cash._instance(tuple(receipts),f.period)
        f.inline=InlineFacts();f.inline.feed(f.primary.artifact.body.decode());f.text=re.sub(r'\s+',' ',' '.join(f.inline.text));f.facts={};f.entries=[];exceptions=[]
        for key,spec in reviewed['facts'].items():
            if key.startswith('cover_'):continue
            try:f.fact(key,spec['concept'],'Selected primary population '+key+'; duration note is not a closing AP adjustment',
                instant=spec['as_of'] is not None,namespace='goog' if spec['namespace'].startswith('http://www.google.com/') else 'us-gaap',unit=spec['unit'],
                dimensions=tuple(tuple(x) for x in spec['occurrences'][0]['dimensions']))
            except ValueError as exc:exceptions.append(dict(input_id=key,value=None,reason=str(exc),kind='RETAINED_BINDING_OR_SCOPE'))
        for key,concept in [('ppe_depreciation_impairment','DepreciationAndImpairmentOnDispositionOfPropertyAndEquipment'),
            ('intangible_amortization_impairment','AmortizationAndImpairmentOfIntangibleAssets'),
            ('combined_nonc_debt','LongTermDebtAndCapitalLeaseObligations'),('debt_before_costs','LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities'),
            ('retirement_expense','DefinedContributionPlanCostRecognized'),
            ('equity','StockholdersEquity'),('common_capital','CommonStocksIncludingAdditionalPaidInCapital'),('retained','RetainedEarningsAccumulatedDeficit'),('oci','AccumulatedOtherComprehensiveIncomeLossNetOfTax')]:
            try:f.fact(key,concept,'Exact selected statement/note population; preserve caption-specific scope',instant=key in ('equity','common_capital','retained','oci','combined_nonc_debt','debt_before_costs'),namespace='goog' if key in ('ppe_depreciation_impairment','intangible_amortization_impairment') else 'us-gaap')
            except ValueError as exc:exceptions.append(dict(input_id=key,value=None,reason=str(exc),kind='RETAINED_BINDING_OR_SCOPE'))
        for label,member in [('a','us-gaap:CommonClassAMember'),('b','us-gaap:CommonClassBMember'),('c','goog:CapitalClassCMember')]:
            dates=set();dims=(('us-gaap:StatementClassOfStockAxis',member),)
            for node in f.root:
                if not node.tag.endswith('}EntityCommonStockSharesOutstanding'):continue
                c=f.contexts[node.get('contextRef')];members=tuple((v.get('dimension'),v.text) for v in c.iter() if v.tag.endswith('}explicitMember'))
                if members==dims:
                    stamp=c.findtext(cash._XI+'period/'+cash._XI+'instant')
                    if stamp:dates.add(stamp)
            for stamp in sorted(dates):f.fact('cover_'+label+'_'+stamp,'EntityCommonStockSharesOutstanding','Actual class/date, not fiscal-end/dilution',instant=True,namespace='dei',unit='shares',as_of=stamp,dimensions=dims)
        evidence=inspect.prepare(f.period,tuple(receipts),tuple(inspect.ArtifactBinding(r.artifact.url,r.artifact.sha256,'instance' if r is f.instance else 'support') for r in receipts))
        from valuation_platform.analyst import retained_income_preparation as direct_income
        from valuation_platform.analyst.historical_inputs import Field
        income=direct_income.inspect(evidence,Field.REVENUE,());chosen,reason=direct_income.choose(income,Field.REVENUE)
        if chosen is not None:f.fact('revenue',income.candidates[chosen].concept,'Approved direct revenue semantics, independently bound primary/instance')
        income_selection=dict(policy=direct_income.POLICIES[Field.REVENUE].policy_id if hasattr(direct_income.POLICIES[Field.REVENUE],'policy_id') else 'existing_REVENUE_POLICY',
            rationale=reason,candidates=[dict(concept=c.concept,value=str(c.value),precision=c.precision) for c in income.candidates])
        # Existing inspector verifies date/unit/context. Only an explicitly tagged
        # fixed-zero + instance zero is a zero, never a missing population.
        for key,concept in [('cp','CommercialPaper'),('term_current','LongTermDebtCurrent')]:
            if key in f.facts:continue
            found=inspect.inspect(evidence,inspect.SelectionSpec(key,(inspect.Selector(f.namespaces['us-gaap'],concept,()),),'instant','USD','reported_zero','Exact declared fixed-zero observation, not absence',()))
            if not found.candidates:continue
            if found.competing_values or any(c.value!=0 for c in found.candidates):continue
            occurrences=[]
            for c in found.candidates:
                for o in c.occurrences:
                    node=f.root[o.ordinal];attrs,text=f.inline.facts[node.get('id')]
                    if (attrs.get('format')!='ixt:fixed-zero' or text.strip() not in ('no','—','-','0') or Decimal(o.raw_value)!=0
                        or attrs.get('contextref')!=o.context_id or attrs.get('unitref')!=o.unit_id or attrs.get('decimals')!=o.decimals):raise ValueError('Unproved explicit zero observation')
                    occurrences.append(dict(ordinal=o.ordinal,context_id=o.context_id,raw_value=o.raw_value,precision=o.decimals,unit_id=o.unit_id,
                        start=None,end=str(o.end),dimensions=[],primary_locator='inline#'+node.get('id'),primary_display=text,primary_format=attrs['format'],primary_scale=int(attrs.get('scale','0')),primary_sign=attrs.get('sign','+')))
            f.facts[key]=dict(concept=concept,namespace=f.namespaces['us-gaap'],location='Explicit fixed-zero selected note/table',unit='USD',value='0',display_value='0',display_unit='USD millions',
                precision=occurrences[0]['precision'],precision_variants=sorted({o['precision'] for o in occurrences}),as_of=identity['annual_end'],occurrences=occurrences,occurrence_count=len(occurrences),
                primary_source=f'FY{year}-primary',instance_source=f'FY{year}-instance',source_reported_zero=True)
        da_key='Depreciation' if 'Depreciation' in f.facts else 'ppe_depreciation_impairment'
        terms=[('NetIncomeLoss',1),(da_key,1)]
        if 'intangible_amortization_impairment' in f.facts:terms.append(('intangible_amortization_impairment',1))
        terms += [('ShareBasedCompensation',1),('DeferredIncomeTaxesAndTaxCredits',1),('DebtAndEquitySecuritiesGainLoss',-1),('OtherNoncashIncomeExpense',-1),
            ('IncreaseDecreaseInAccountsReceivable',-1),('IncreaseDecreaseInIncomeTaxes',1),('IncreaseDecreaseInOtherOperatingAssets',-1),
            ('IncreaseDecreaseInAccountsPayable',1),('IncreaseDecreaseInAccruedLiabilities',1),('IncreaseDecreaseInAccruedRevenueShare',1),('IncreaseDecreaseInContractWithCustomerLiability',1)]
        cf=[dict(fact=k,multiplier=c,contribution_usd=str(Decimal(f.facts[k]['value'])*c)) for k,c in terms]
        total=sum((Decimal(t['contribution_usd']) for t in cf),Decimal(0))
        if total!=Decimal(f.facts['NetCashProvidedByUsedInOperatingActivities']['value']):raise ValueError('Displayed selected Alphabet CFO does not reconcile: '+str(year))
        start=f.text.find('Adjustments:');stop=f.text.find('Investing activities',start)
        if start<0 or stop<0 or 'Net cash provided by operating activities' not in f.text[start:stop]:raise ValueError('Independent CFO display unavailable')
        cfo_display=f.text[max(0,start-100):stop]
        def calc(key,terms,scope,formula=None):
            if any(k not in f.facts for k,c in terms):return
            f.entry(key,scope,[k for k,c in terms],[c for k,c in terms],scope=scope,rationale='Retained source arithmetic only, not analyst approval',
                completeness='complete_for_named_population',formula=formula,unit='pure' if formula=='DIVIDE' else None,policy='annual_reported_effective_tax_rate_v1' if formula=='DIVIDE' else None)
        calc('current_financial',[('cash',1),('current_marketable',1)],'Named current cash/marketable parent; no unrestricted/excess assertion')
        calc('reported_etr',[('IncomeTaxExpenseBenefit',1),('pretax',1)],'Existing positive-denominator historical ETR, not a future rate','DIVIDE')
        if year<=2023:
            # The source table already includes finance leases and, where stated,
            # other financing. LongTermDebt is its future-maturity schedule here.
            calc('named_financing',[('debt_before_costs',1),('debt_discount_signed',-1),('cp',1)],'Selected debt table net of costs, INCLUDING finance leases/other; no added finance liability')
        else:calc('named_financing',[('term_current',1),('term_long',1),('cp',1),('finance_total',1)],'Named net term + CP + separately reported finance leases, no current-maturity duplication')
        checks=[]
        for label,parent_key,children in [('current_financial','current_financial_parent',['cash','current_marketable']),('equity','equity',['common_capital','retained','oci']),
            ('operating_lease','op_total',['op_current','op_long']),('finance_lease','finance_total',['finance_current','finance_long'])]:
            if all(k in f.facts for k in [parent_key,*children]):
                difference=Decimal(f.facts[parent_key]['value'])-sum((Decimal(f.facts[k]['value']) for k in children),Decimal(0))
                checks.append(dict(check_id=label,parent=parent_key,children=children,difference_usd=str(difference),status='EXACT' if not difference else 'SOURCE_DIFFERENCE_UNRESOLVED',not_an_adjustment=True))
        precision={}
        for key,concept in [('nonmarketable_equity','EquitySecuritiesWithoutReadilyDeterminableFairValueAmount'),('uncertain_tax','UnrecognizedTaxBenefits')]:
            precision[key]=variants(f,evidence,key,concept)
            for c in precision[key]['candidates']:c.update(primary_source=f'FY{year}-primary',instance_source=f'FY{year}-instance')
        passages=[]
        for marker in ('Adjustments:','Adjustments to reconcile','Changes in assets and liabilities','Net cash provided by operating activities',
            'Depreciation','amortization of intangible','useful lives','share-based compensation expense','total stock-based compensation expense',
            'noncontrolling interests','redeemable noncontrolling','Finance lease liabilities are included','financing leases are included',
            'Net of effects of acquisitions','stock split','Cash, Cash Equivalents','pension','retirement','Note 1.',
            'Total long-term debt','Total noncontrolling interests','finance lease costs were not material','Future finance lease payments',
            'total SBC expense was','total stock-based compensation expense was','valuation-based compensation charge related to Waymo'):
            m=re.search(re.escape(marker),f.text,re.I)
            if m:passages.append(dict(marker=marker,offset=m.start(),exact_excerpt=f.text[max(0,m.start()-90):m.end()+1800],source_sha256=f.primary.artifact.sha256))
        passages.append(dict(marker='independently_displayed_cfo',offset=max(0,start-100),exact_excerpt=cfo_display,source_sha256=f.primary.artifact.sha256))
        rows.append(dict(identity=identity,source_manifest_reference='docs/phase1-selected-filing-identity-manifest.json#/rows/'+str(index),sources=sources,
            facts=f.facts,calculations=f.entries,exceptions=exceptions,precision_candidates=precision,passages=passages,partition_checks=checks,
            income_selection=income_selection,da_proxy_source=da_key,cfo_reconciliation=dict(terms=cf,value_usd=str(total),supported=True,residual_used=False),new_assumptions_active=False,analyst_complete=False,
            existing_approval_reference='/accepted_view' if year==2024 else None,original_metadata_gaps_preserved=True))
    from valuation_platform.analyst.historical_inputs import Field
    family_facts={'revenue':['revenue'],'ebit':['ebit'],'depreciation_amortization':[],
        'cash_capex':['PaymentsToAcquirePropertyPlantAndEquipment'],'reported_cash_flow_working_capital_movements':[],
        'deferred_taxes':['DeferredIncomeTaxesAndTaxCredits','DeferredIncomeTaxExpenseBenefit'],
        'stock_based_compensation':['AllocatedShareBasedCompensationExpense','ShareBasedCompensation'],
        'unclassified_cfo_reconciliation_residual':['OtherNoncashIncomeExpense'],'reported_cfo':['NetCashProvidedByUsedInOperatingActivities'],
        'reported_tax_context':['IncomeTaxExpenseBenefit','pretax','IncomeTaxesPaidNet'],
        'cash_investment_components':['cash','current_marketable','nonmarketable_parent'],
        'debt_lease_components':['cp','finance_total','op_total'],
        'other_equity_bridge_claims_assets':['nci_vie','preferred_value','ec_fines','nol_dta'],
        'point_in_time_shares':['year_end_a','year_end_b','year_end_c','reported_common_total','rsu']}
    pending={'depreciation_amortization':['G1'],'stock_based_compensation':['G2'],'debt_lease_components':['G3'],
        'cash_investment_components':['G4'],'other_equity_bridge_claims_assets':['G5','G6'],
        'unclassified_cfo_reconciliation_residual':['G7'],'point_in_time_shares':['G8']}
    existing={'revenue','ebit','cash_capex','deferred_taxes','stock_based_compensation','reported_cfo','reported_tax_context','cash_investment_components','point_in_time_shares'}
    for i,row in enumerate(rows):
        base=f'/googl_history_review/periods/{i}';year=int(row['identity']['annual_end'][:4]);facts=row['facts'];checklist=[]
        row['movement_rows']=[dict(t,already_in_reported_cfo=True,not_book_delta_nwc=True) for t in row['cfo_reconciliation']['terms'] if t['fact'].startswith('IncreaseDecrease')]
        for field in Field:
            keys=family_facts[field.value]
            if field is Field.DA:keys=[row['da_proxy_source']]
            elif field is Field.CF_WORKING_CAPITAL:keys=[t['fact'] for t in row['movement_rows']]
            decisions=[] if year==2024 and field.value in existing else pending.get(field.value,[])
            status='PROPOSED_PENDING_APPROVAL' if decisions else 'EXISTING_SCOPED_APPROVAL' if year==2024 and field.value in existing else 'SOURCE_SUPPORTED'
            if not keys or any(k not in facts for k in keys):status='ESSENTIAL_EVIDENCE_EXCEPTION'
            checklist.append(dict(field=field.value,status=status,pending_decisions=decisions,evidence_references=[base+'/facts/'+k for k in keys if k in facts],
                existing_approval_reference='/accepted_view' if year==2024 else None,completeness='Named historical population only, no economic completeness'))
        row['family_checklist']=checklist;source=facts[row['da_proxy_source']]
        row['proposed_da_proxy']=dict(value_usd=source['value'],unit='USD',precision=source['precision'],origin='proxy',status=PROPOSED,accepted=False,
            source_reference=base+'/facts/'+row['da_proxy_source'],author='Analyst preparation review, pending user approval',recorded_at_utc='2026-10-17T16:13:48+00:00',
            scope='PP&E noncash-cost proxy; FY2021/22 includes impairment, later reported depreciation; not complete expense D&A',
            complete_expense_da=None,finance_amortization_inclusion_assumption=None,intangible_amortization_allocation=None,additional_rou_addback=False)
        row['cash_signs']={k:-1 for k in ['PaymentsToAcquirePropertyPlantAndEquipment','AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets','PaymentsForProceedsFromOtherInvestingActivities','IncomeTaxesPaidNet','OperatingLeasePayments','FinanceLeaseInterestPaymentOnLiability','FinanceLeasePrincipalPayments']}
        row['source_scope_overrides']=dict(term_face='Future principal/payment schedule including finance leases, not pure notes or carrying amount' if year<=2023 else 'Reported term face/principal, not carrying',
            combined_nonc_debt='Reported noncurrent debt INCLUDING finance leases/other' if year<=2023 else 'Reported noncurrent term debt; finance leases separately presented',
            sbc='Total expense includes awards not expected to settle in Alphabet stock; add-back is a different reconciliation population',
            shares='FY2021 as-reported pre20:1 split; FY2022 onward post-split. Do not use later restated comparatives as original selections.')
        row['supporting_unknowns']={k:None for k in ['complete_expense_da','inventory_completeness','supplier_ap_scope','cash_borrowing_interest','complete_lease_cash','acquisition_allocation','unrestricted_cash','operating_reserve','pension_funded_status','additional_borrowing']}
        row['book_nwc_support']='Existing FY2024 rounded manual3200 correction remains authorized only there; do not extend duration-tag interpretations or infer inventory/supplier allocations.'
    identities=[r['identity'] for r in rows];other=[r for r in identities if r['annual_end']!='2024-12-31']
    specs=[
        ('G1',identities,'Select reported PP&E noncash-cost observations as explicitly limited historical proxies, not complete expense D&A; no extra ROU addition or assumed finance/intangible inclusion.',
         '11555/15287/11946/15311/21136 USDm. FY2021/22 captions INCLUDE impairment; separate intangible amortization/impairment886/641 remains support. Early broad two-caption alternative12441/15928 includes impairment, not pure D&A.',
         'Alternative leave D&A required input unresolved. Later finance amortization413/553 stays separate with unproved overlap; no sum, residual amortization or invented zero. Useful-life changes reduce comparability; omitted intangible/timing effects unquantified.'),
        ('G2',other,'Use rounded total recognized SBC expense as cost proxy once in other years, preserving FY2024 approval and distinct CFO add-backs. Retain Other Bets/valuation-based scope, not just Alphabet-share awards.',
         'Total15700/19500/22100/22800/27100R versus add-back15376/19362/22460/22785/24953. Differences324/138/-360/15/2147 are not rounding adjustments. Stock-settled-only alternative15000/18800/21700/22000/24100R has narrower scope.',
         'FY2025 includes increased Waymo valuation-based compensation; no supported allocation to the add-back gap. No duplicate charge, award valuation or assumption that every difference is rounding. Alternative narrower proxy omits other compensation.'),
        ('G3',identities,'Operating leases service, finance asset financing; select the period-specific named reported debt/finance population with no additional undisclosed borrowing adjustment. Respect the changed debt table perimeter.',
         '14930/14999/14616/15859/51043 USDm. FY2021-23 debt table already includes finance leases/other: before-costs15086/15142/14746 less156/143/130, CP explicitly0. FY2024 term11882+CP2300+finance1677; FY2025 term48543+CP0+finance2500.',
         'Omitted borrowing unbounded, not complete debt or immateriality. Never add older finance2086/2142/1746 again. Early LongTermDebt15440/15312/14862 is a future-payment schedule, not carrying. FY2024/25 finance principal405/1988 already in debt repayments12701/32427; early separate cash splits unavailable. FY2025 operating lease parent15954 versus components15953 is an unresolved1m source difference, not a plug or amended tolerance.'),
        ('G4',other,'Select gross named current cash/marketable balances in other periods, keeping strategic/nonmarketable/restricted observations and precision alternatives separately. Preserve FY2024 selected95657.',
         '139649/113762/110916/95657/126843 USDm. Nonmarketable parent29549/30492/31008/37982/68687 separate. Candidate pairs27571/27600R,28529/28500R,28766/28800R,35531/35500R,64094/64100R remain unselected alternatives, not amounts to add.',
         'Not unrestricted/excess cash; unknown restrictions/reserves remain. Long restricted marketable803/1400/266 in FY2022/23/24 only; absent FY2021/25 binding is not zero. Equity-method holdings overlap parents; FY2025 unbound subamount is not a residual-derived allocation.'),
        ('G5',identities,'Retain disclosed total NCI INCLUDING redeemable subsets, source-reported preferred0, legal/tax claims and gross NOL DTA separately; no all-claims sum or pure-NOL economic-value operation.',
         'NCI4300/3800/3400/4200/3400R; redeemable unknown/1100R/1100R/1100R/841 is included, never added. Fines9799/9106/9525/6322/15594; gross NOL DTA1790/2557/2965/3472/4953 before valuation/realizability.',
         'Source-preferred zero is actual tagged presentation, not an inferred no-claims assumption. Existing claims remain; no exhaustive undisclosed-claim coverage or deduction. UTB precision alternatives are not recognized liability totals or amounts to add to tax captions; no economic tax-asset valuation.'),
        ('G6',identities,'Propose no separately selected pension funded-status or other unidentified claim adjustment, preserving source unknowns and the disclosed recognized claims.',
         'No new quantified adjustment; omitted net obligations/assets remain unbounded. No invented pension amount or retirement expense.',
         'Retained disclosures do not establish full funded-status coverage. This is a new weak-evidence analyst omission, not a peer approval or immateriality finding. Alternative keep requirement blocked; explicit user acceptance is essential if this omission is to satisfy the historical perimeter.'),
        ('G7',identities,'No separate residual scalar for independently bound displayed CFO; preserve every mixed row and source sign.',
         '14/14/13/13/13 terms independently tie91652/91495/101746/125299/164713. Other-213/+1030/+4330/+3419/+2108 retained; no residual0 or balancing item.',
         'CFO is consolidated, not organic/unlevered cash. Seven movements are net of acquisition effects as stated, not book delta NWC or proof of all FX/reclassification allocations. Alternative classify all mixed subamounts unsupported.'),
        ('G8',other,'Retain each actual dated A/B/C common population and independently reported aggregate as source observations; no automatic class/award sum or economic class equivalence. Preserve FY2024 accepted view.',
         'A/B/C millions:300.737/44.665/316.719;5964/883/6002;5899/870/5691;5835/861/5515;5822/837/5429. Reported aggregate662.121/12849/12460/12211/12088 independently observed. FY2022 executed20:1 split; FY2021 remains original pre-split.',
         'Alternative explicitly split-normalized FY2021 classes would be20x the original, not extra shares or forecast dilution; not selected here. Cover dates and annual EPS/RSUs remain separate; early EPS nondimensional totals unbound are supporting gaps, not invented issuer totals.'),
        ('G9',identities,'Retain reported cash PP&E and combined acquisition/intangible, other investing, capital-creditor and noncash-lease observations separately; no new investment subtotal. This is source-supported packaging, not a new assumption request.',
         'Cash PP&E-24640/-31485/-32251/-52535/-91447; combined purchases-2618/-6969/-495/-2931/-1592. FY2024 manual AP3200R remains only FY2024, not a template for duration tags15090 in FY2025 or earlier absent bindings.',
         'Acquisition allocations, supplier AP/inventory completeness and reinvestment scope stay unknown. Gross accruals, unrecorded commitments, finance cash payments and sale proceeds are not additive purchases. Mandiant2022 and Character2024 affect comparability; no organic normalization.')]
    proposals=[dict(decision_id=k,periods=periods,recommendation=rec,numerical_consequence=n,uncertainty_and_alternative=u,status=SUPPORTED if k=='G9' else PROPOSED,
        approval_required=k!='G9',accepted=False,evidence_reference='/googl_history_review/periods') for k,periods,rec,n,u in specs]
    result=json.loads(json.dumps(parent));result['googl_history_review']=dict(version=1,periods=rows,source_revision=digest(relevant(parent)),
        review_revision=digest(relevant(dict(periods=rows,proposals=proposals,parent_revision=digest(relevant(parent))))),family_slots=70,consolidated_proposals=proposals,
        outcomes={status:sum(c['status']==status for r in rows for c in r['family_checklist']) for status in ['SOURCE_SUPPORTED','EXISTING_SCOPED_APPROVAL','PROPOSED_PENDING_APPROVAL','ESSENTIAL_EVIDENCE_EXCEPTION']},
        evidence_acquisition_requirements=acquisition,new_sec_requests=0,new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False,
        evidence_limits='All ten selected bodies and usable original/refreshed receipts verified; original instance timestamp/status gaps remain null. No acquisition required; unavailable allocations are not repaired by inventing metadata.',
        source_path='User-instructed reported movements and independently reconciled CFO; complete reconstructed NWC/book delta not required, movements not additional deductions.',
        company_counts=dict(broad_evidence_assessment=42,completed_company_wide_packages=2,partial_company_packages=1,broad_assessment_only=39),
        comparability=['FY2021/22 impairment-inclusive asset captions versus later depreciation; useful-life estimates change in2021/2023; no recast.',
            'FY2024 debt presentation separates finance leases from term borrowing; earlier combined debt already includes them.',
            'FY2021 shares as reported pre-split; FY2022 execution20:1 and later comparative restatements do not overwrite originals.',
            'Acquisitions/combined purchases and2025 valuation-based Other Bets compensation/investment gains remain consolidated, no economic adjustments.',
            'FY2025 operating liability1m source partition difference remains unresolved; no balancing item or invented tolerance.'],
        stopping_condition='One consolidated G1-G8 approval/exception review; G9 source context only. No new assumption active, follow-on research or Phase1/Phase2 closure.')
    return result


def history_approval_record(package):
    if 'googl_history_approval' in package:raise ValueError('Immutable Alphabet history approval already exists')
    review=package['googl_history_review']
    record=dict(schema='googl-treatment-acceptance-audit-v1',version=1,sequence=2,
        previous=package['accepted_view']['approval_audit']['sha256'],action='ACCEPT_FY2021_FY2025_G1_G8',
        author='User, explicit approval of Alphabet G1-G8 across frozen FY2021-FY2025',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Accept limited D&A proxies including early impairment and omitted components, SBC expense once, named financing and gross financial balances, known claims without overlap and unbounded unidentified/pension omission, no CFO residual and dated classes/split boundary. Historical preparation only.',
        authority='Current user instruction: explicitly approves Alphabet G1-G8; preserve source unknowns, alternatives, prior decisions and FY2025 operating-lease1m discrepancy without changing financing.',
        source_commit='2b6b6504129b1eda1d595f54f34b0eded4acbc8b',source_revision=digest(relevant(package)),
        review_revision=review['review_revision'],identities=[r['identity'] for r in review['periods']],
        decisions={r['decision_id']:{k:v for k,v in r.items() if k not in ('decision_id','status','accepted','approval_required')} for r in review['consolidated_proposals'] if r['approval_required']},
        financial_sufficiency='ONLY_APPROVED_HISTORICAL_PERIMETER',phase1_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def activate_company_history(package):
    parent={k:v for k,v in package.items() if k not in ('googl_history_approval','googl_current_history')}
    if review_company_history(parent)!=parent:raise ValueError('Changed Alphabet source/company review')
    record=_json((ROOT/OUTPUT).read_text())['googl_history_approval'];expected=history_approval_record(parent)
    if type(record) is not dict or set(record)!=set(expected) or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed Alphabet history approval')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    for k in set(expected)-{'recorded_at_utc','sha256','source_revision','review_revision'}:
        if type(record[k]) is not type(expected[k]) or record[k]!=expected[k]:raise ValueError('Unregistered Alphabet history approval: '+k)
    if any(record[k]!=expected[k] for k in ('source_revision','review_revision')):raise ValueError('Stale Alphabet history approval; explicit revalidation required')
    if set(record['decisions'])!={f'G{i}' for i in range(1,9)} or parent['googl_history_review']['outcomes']['ESSENTIAL_EVIDENCE_EXCEPTION']:raise ValueError('Incomplete Alphabet authorization/evidence')
    periods=[]
    for i,row in enumerate(parent['googl_history_review']['periods']):
        base=f'/googl_history_review/periods/{i}';facts=row['facts'];calcs={c['input_id']:c for c in row['calculations']}
        def fact(key,multiplier=1):
            f=facts[key]
            return dict(value=str(Decimal(f['value'])*multiplier),unit=f['unit'],precision=f['precision'],origin='reported',raw_value=f['value'],multiplier=multiplier,as_of=f['as_of'],source_reference=base+'/facts/'+key)
        def calculation(key):
            return dict(calcs[key],source_reference=base+'/calculations/'+str(next(j for j,c in enumerate(row['calculations']) if c['input_id']==key)),review=APPROVED_SCOPE)
        def observations(keys):return {k:fact(k) for k in keys if k in facts}
        checklist=[]
        if len(row['family_checklist'])!=14 or len({r['field'] for r in row['family_checklist']})!=14 or not row['cfo_reconciliation']['supported']:raise ValueError('Alphabet checklist/reconciliation incomplete')
        for r in row['family_checklist']:
            if r['status'] not in ('SOURCE_SUPPORTED','EXISTING_SCOPED_APPROVAL','PROPOSED_PENDING_APPROVAL') or any(k not in record['decisions'] for k in r['pending_decisions']):raise ValueError('Unresolved Alphabet family')
            checklist.append(dict(r,status='SATISFIED_BY_EXPLICIT_APPROVAL' if r['pending_decisions'] else 'SATISFIED_WITHIN_SOURCE_OR_PRIOR_SCOPE',approval_reference='/googl_history_approval' if r['pending_decisions'] else r['existing_approval_reference']))
        inputs=dict(revenue=fact('revenue'),ebit=fact('ebit'),
            depreciation_amortization=dict(row['proposed_da_proxy'],accepted=True,status=APPROVED_SCOPE,approval_reference='/googl_history_approval'),
            cash_capex=fact('PaymentsToAcquirePropertyPlantAndEquipment',-1),
            reported_cash_flow_working_capital_movements=dict(rows=row['movement_rows'],source_reference=base+'/cfo_reconciliation',additional_deduction_permitted=False),
            deferred_taxes=dict(selected=fact('DeferredIncomeTaxesAndTaxCredits'),provision=fact('DeferredIncomeTaxExpenseBenefit'),interchangeable=False),
            stock_based_compensation=dict(selected=fact('AllocatedShareBasedCompensationExpense'),origin='proxy',count_once=True,addback=fact('ShareBasedCompensation'),rounding_adjustment=None),
            unclassified_cfo_reconciliation_residual=dict(value=None,disposition='APPROVED_NO_SEPARATE_OPERATION',not_reported_zero=True,mixed_rows_reference=base+'/cfo_reconciliation'),
            reported_cfo=fact('NetCashProvidedByUsedInOperatingActivities'),
            reported_tax_context=dict(provision=fact('IncomeTaxExpenseBenefit'),pretax=fact('pretax'),reported_etr=calculation('reported_etr'),cash_taxes=fact('IncomeTaxesPaidNet',-1),future_rate_approved=False),
            cash_investment_components=dict(selected=calculation('current_financial'),separate_observations=observations(['long_marketable','nonmarketable_parent','equity_method','listed_equity','restricted_combined']),
                precision_alternatives_reference=base+'/precision_candidates',unknown_restrictions=None,operating_reserve=None,unrestricted_or_excess_cash=False),
            debt_lease_components=dict(selected=calculation('named_financing'),additional_borrowing=None,no_additional_adjustment='Approved analyst assumption; omitted borrowing unbounded, not reported zero',complete_debt=False,
                lease_classification=dict(operating='service_cost',finance='asset_financing'),operating_lease=fact('op_total'),finance_lease=fact('finance_total'),
                early_finance_already_in_named_debt=i<3,current_maturities_already_included=True,source_partition_checks=row['partition_checks'],source_scope_reference=base+'/source_scope_overrides',
                lease_cash_observations=observations(['OperatingLeasePayments','FinanceLeaseInterestPaymentOnLiability','FinanceLeasePrincipalPayments','RepaymentsOfDebtAndCapitalLeaseObligations']),
                finance_principal_already_in_debt_repayments=True if i>=3 else None,complete_lease_cash=False,borrowing_cash_interest=None),
            other_equity_bridge_claims_assets=dict(known_claims=observations(['nci_vie','redeemable_nci','preferred_value','ec_fines','tax_current','tax_long','nol_dta','vie_funding']),nci_includes_redeemable=True,
                pension=None,unidentified_claims=None,pure_nol_economic_value=None,no_additional_adjustment='Approved analyst omission; potential undisclosed net obligation/asset unbounded, no immateriality finding',exhaustive_claims=False),
            point_in_time_shares=dict(classes=observations(['year_end_a','year_end_b','year_end_c']),independently_reported_aggregate=fact('reported_common_total'),
                cover=observations([k for k in facts if k.startswith('cover_')]),awards=observations(['rsu','future_sbc']),eps_denominators=observations(['weighted_basic','weighted_diluted']),
                original_pre_split=i==0,aggregation_or_dilution_approved=False))
        periods.append(dict(identity=row['identity'],inputs=inputs,checklist=checklist,analyst_complete=True,remaining_essential_inputs=[],
            supporting_unknowns=row['supporting_unknowns'],sources_reference=base+'/sources',supporting_investment_reference=base+'/facts',complete_expense_basis_da=None,
            original_metadata_gaps_preserved=True,source_comparability_reference='/googl_history_review/comparability'))
    if len(periods)!=5:raise ValueError('Five selected Alphabet annuals required')
    result=json.loads(json.dumps(parent));result['googl_history_approval']=record
    result['googl_current_history']=dict(version=1,authoritative_current_view=True,periods=periods,company_completed_for_approved_historical_perimeter=True,
        family_slots=70,passed_family_slots=70,complete_expense_basis_da=None,complete_debt=False,complete_reinvestment=False,phase1_closed=False,valuation_consumption_approved=False,
        approval_sha256=record['sha256'],historical_proposal_snapshot='/googl_history_review',
        company_counts=dict(broad_evidence_assessment=42,company_analyst_packages=3,completed_company_wide_packages=3,partial_company_packages=0,broad_assessment_only=39))
    return result


if __name__=='__main__':
    if '--record-approved-treatment-set' in sys.argv:
        if (ROOT/ACCEPTANCE_PATH).exists():raise SystemExit('Immutable Alphabet acceptance record already exists')
        print(json.dumps(approval_record(build_proposal()),sort_keys=True,indent=2))
        raise SystemExit(0)
    text=json.dumps(build(),sort_keys=True,indent=2)+'\n'
    if '--check' in sys.argv:
        if (ROOT/OUTPUT).read_text()!=text:raise SystemExit('Alphabet package replay differs')
        print('Exact Alphabet FY2024 package replay passed')
    else:print(text,end='')
