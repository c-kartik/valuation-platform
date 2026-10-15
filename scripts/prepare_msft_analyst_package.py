"""Two reviewed MSFT annuals: draft historical schedules, not a runtime adapter.

No retrieval, financial approval, forecast or valuation calculation. Original
registries/outputs are read-only. Exact source occurrences and statement tags
are checked before any point enters this separate company-specific package.
"""
from datetime import date
from decimal import Decimal, localcontext
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from valuation_platform.analyst import cash_flow_inputs as cash

OUTPUT = 'docs/company-data-preparation/msft-analyst-input-package.json'
BASELINE = 'daeb3b007a664cfe9fe31fe426d1f5ae40be503a'
ACCEPTED = 'existing_accepted_treatment'
SUPPORTED = 'source_supported_selection_or_calculation'
PROPOSED = 'proposed_pending_user_approval'
UNRESOLVED = 'unresolved_requirement'


class InlineFacts(HTMLParser):
    """One bounded pass over the retained inline document, including note prose."""
    def __init__(self):
        super().__init__(); self.stack = []; self.facts = {}; self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == 'ix:nonfraction': self.stack.append([dict(attrs), []])

    def handle_data(self, data):
        self.text.append(data)
        for item in self.stack: item[1].append(data)

    def handle_endtag(self, tag):
        if tag == 'ix:nonfraction' and self.stack:
            attrs, parts = self.stack.pop(); key = attrs['id']
            if key in self.facts: raise ValueError('Duplicate primary inline ID')
            self.facts[key] = (attrs, ''.join(parts).strip())


def inline_amount(attrs, text):
    if attrs.get('format') not in ('ixt:num-dot-decimal','ixt:numdotdecimal','ixt-sec:numwordsen'):
        raise ValueError('Unsupported selected inline transformation')
    text = text.replace(',', '').replace('\xa0', '').strip()
    if text in ('—', '–', '-') or (text=='no' and attrs.get('format')=='ixt-sec:numwordsen'):
        value = Decimal(0)  # explicitly displayed/tagged zero only, never absent evidence
    else: value = Decimal(text.strip('()'))
    if attrs.get('sign') == '-' or text.startswith('('): value = -value
    return value * Decimal(10) ** int(attrs.get('scale', '0'))


class Filing:
    def __init__(self, year):
        self.year = year
        self.bundle = cash.load_msft_bundle(f'msft-reported-cash-flow-fy{year}')
        self.period = self.bundle.period
        self.root, self.contexts, self.units, self.namespaces = cash._instance(self.bundle.artifacts, self.period)
        self.instance = next(r for r in self.bundle.artifacts if r.artifact.url.endswith('_htm.xml'))
        self.primary = next(r for r in self.bundle.artifacts if r.artifact.url.endswith('.htm'))
        self.inline = InlineFacts(); self.inline.feed(self.primary.artifact.body.decode())
        self.text = re.sub(r'\s+', ' ', ' '.join(self.inline.text))
        self.facts = {}; self.entries = []

    def fact(self, key, concept, location, *, instant=False, namespace='us-gaap',
             unit='USD', as_of=None, dimensions=()):
        namespace = self.namespaces[namespace] if namespace in self.namespaces else namespace
        end = date.fromisoformat(as_of) if as_of else self.period.annual_end
        occurrences = []
        for ordinal, f in enumerate(self.root):
            if f.tag != '{'+namespace+'}'+concept: continue
            context = self.contexts[f.attrib['contextRef']]
            members = tuple((x.get('dimension'), x.text) for x in context.iter()
                            if x.tag.endswith('}explicitMember'))
            if members != dimensions: continue
            # The existing identity validator deliberately excludes dimensions;
            # the one explicitly classed award population is checked separately.
            if dimensions:
                xi = cash._XI
                start = context.findtext(xi+'period/'+xi+'startDate')
                stop = context.findtext(xi+'period/'+xi+'instant') or context.findtext(xi+'period/'+xi+'endDate')
                entity = context.findtext('.//'+xi+'identifier')
                identity = (int(entity), date.fromisoformat(start) if start else None, date.fromisoformat(stop))
            else: identity = cash._context(context)
            if identity != (self.period.cik, None if instant else self.period.annual_start, end): continue
            if f.get('{http://www.w3.org/2001/XMLSchema-instance}nil', 'false') not in ('false', '0'):
                raise ValueError('Nil selected fact')
            measures = list(self.units[f.attrib['unitRef']])
            if len(measures) != 1 or measures[0].tag != cash._XI+'measure': raise ValueError('Non-simple unit')
            measure = measures[0].text
            prefix, local = measure.split(':') if ':' in measure else ('', measure)
            expected_ns = 'http://www.xbrl.org/2003/iso4217' if unit == 'USD' else 'http://www.xbrl.org/2003/instance'
            if self.namespaces[prefix] != expected_ns or local != unit: raise ValueError('Wrong selected unit')
            value = Decimal(f.text)
            if not value.is_finite(): raise ValueError('Nonfinite selected fact')
            attrs, text = self.inline.facts[f.attrib['id']]
            if (attrs['name'].split(':')[-1] != concept or attrs['contextref'] != f.attrib['contextRef']
                    or attrs['unitref'] != f.attrib['unitRef'] or attrs['decimals'] != f.attrib['decimals']
                    or inline_amount(attrs, text) != value): raise ValueError('Primary/instance representation mismatch')
            occurrences.append(dict(ordinal=ordinal, xml_id=f.attrib['id'], context_id=f.attrib['contextRef'],
                raw_value=f.text, precision=f.attrib['decimals'], unit_id=f.attrib['unitRef'],
                start=str(identity[1]) if identity[1] else None, end=str(identity[2]),
                dimensions=[list(x) for x in members], primary_display=text, primary_scale=int(attrs.get('scale', '0')),
                primary_sign=attrs.get('sign', '+'), primary_format=attrs.get('format'),primary_locator='inline#'+f.attrib['id']))
        if not occurrences: raise ValueError('Required exact source fact absent: '+key)
        if len({Decimal(o['raw_value']) for o in occurrences}) != 1:
            raise ValueError('Competing eligible values: '+key)
        value = Decimal(occurrences[0]['raw_value'])
        self.facts[key] = dict(concept=concept, namespace=namespace, location=location, unit=unit,
            evidence_label='fact_source_reported',evidence_depth='exact_primary_inline_and_instance_verified',
            value=str(value), display_value=str(value / Decimal(1000000)) if unit=='USD' else str(value),
            display_unit='USD millions' if unit=='USD' else 'shares', precision=occurrences[0]['precision'],
            precision_variants=sorted({o['precision'] for o in occurrences}),
            as_of=str(end) if instant else None, occurrence_count=len(occurrences), occurrences=occurrences,
            instance_source=f'FY{self.year}-instance', primary_source=f'FY{self.year}-primary')
        return key

    def entry(self, key, label, operands, coefficients=None, *, status=SUPPORTED, scope,
              rationale, completeness='complete_for_named_population', role='reported_observation',
              limitations=(), formula=None, unit=None, policy=None, origin=None):
        if not operands or any(o not in self.facts for o in operands): raise ValueError('Unknown operand')
        if any(e['input_id']==key for e in self.entries):raise ValueError('Duplicate selected input ID')
        coefficients = coefficients or [1] * len(operands)
        if len(operands) != len(coefficients) or len(set(operands)) != len(operands): raise ValueError('Duplicate/missing operand')
        with localcontext() as ctx:
            ctx.prec = 34
            vals = [Decimal(self.facts[o]['value']) for o in operands]
            if formula=='DIVIDE' and (len(vals)!=2 or vals[1]<=0):raise ValueError('Existing ETR requires positive denominator')
            value = vals[0]/vals[1] if formula=='DIVIDE' else sum((v*c for v,c in zip(vals,coefficients)),Decimal(0))
        units = {self.facts[o]['unit'] for o in operands}
        if len(units)!=1: raise ValueError('Mixed units')
        actual_unit = unit or next(iter(units))
        self.entries.append(dict(input_id=key,label=label,status=status,origin=origin or ('derived' if len(operands)>1 else 'reported'),
            evidence_label='analyst_interpretation' if origin=='proxy' else ('derived_calculation' if len(operands)>1 else 'fact_source_reported'),
            value=str(value),unit=actual_unit,display_value=str(value/1000000) if actual_unit=='USD' else str(value),
            display_unit='USD millions' if actual_unit=='USD' else actual_unit,operands=list(operands),
            coefficients=list(coefficients),formula=formula or ('LINEAR_COMPONENTS' if len(operands)>1 else 'SELECT'),
            formula_version='msft-draft-historical-v1',policy=policy,role=role,scope=scope,
            completeness=completeness,rationale=rationale,limitations=list(limitations),
            source_dates=[dict(operand=o,as_of=self.facts[o]['as_of'],
                annual_start=None if self.facts[o]['as_of'] else str(self.period.annual_start),
                annual_end=str(self.period.annual_end)) for o in operands],
            precision={'operand_decimals':[self.facts[o]['precision'] for o in operands],
                'treatment':'Reported rounded points; calculation does not improve source precision.'}))


def build():
    filings = [Filing(y) for y in (2025,2026)]
    for f in filings: populate(f)
    return finish(filings)


def populate(f):
    """Company-specific reviewed selections, never a generic cascade/registry."""
    # All previously reviewed cash-flow inputs remain separate observations.
    for item in f.bundle.inputs:
        first=item.occurrences[0]
        location=item.location_and_scope.replace('Note 12','Note 11').replace('Note 14','Note 17')
        f.fact(item.input_id,item.input_id,location,
               instant=first.start is None,namespace=first.namespace)
        f.facts[item.input_id]['original_review_location']=item.location_and_scope
        f.entry('reported:'+item.input_id,item.input_id,[item.input_id],[item.display_multiplier],
            status=ACCEPTED if item.input_id in ('NetCashProvidedByUsedInOperatingActivities',
                'PaymentsToAcquirePropertyPlantAndEquipment','IncomeTaxesPaidNet',
                'AllocatedShareBasedCompensationExpense','OperatingLeasePayments',
                'FinanceLeaseInterestPaymentOnLiability','FinanceLeasePrincipalPayments') else SUPPORTED,
            scope=location,rationale='Retain exact independently reviewed input and its distinct role; no economic adjustment.',
            completeness='reported_population_only',role=item.kind.value,
            limitations=('Original MSFT accepted-input and interest-sidecar limitations remain.',))
    specs = [
        ('revenue','RevenueFromContractWithCustomerExcludingAssessedTax','Consolidated income statements; Note 18 segment confirmation',False),
        ('ebit','OperatingIncomeLoss','Consolidated income statements; operating-income total',False),
        ('nonoperating_income','NonoperatingIncomeExpense','Consolidated income statements and Note 3: other income (expense), net',False),
        ('pretax','IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest','Income statements and Note 11 Income Taxes',False),
        ('ar','AccountsReceivableNetCurrent','Consolidated balance sheets: accounts receivable, net',True),
        ('inventory','InventoryNet','Consolidated balance sheets: inventories',True),
        ('ap','AccountsPayableCurrent','Consolidated balance sheets: accounts payable',True),
        ('current_contract','ContractWithCustomerLiabilityCurrent','Balance sheets: short-term unearned revenue',True),
        ('compensation','EmployeeRelatedLiabilitiesCurrent','Balance sheets: accrued compensation',True),
        ('other_current_assets','OtherAssetsCurrent','Balance sheets: mixed other current assets; Note 1',True),
        ('other_current_liabilities','OtherLiabilitiesCurrent','Balance sheets: mixed other current liabilities',True),
        ('current_tax','AccruedIncomeTaxesCurrent','Balance sheets: short-term income taxes',True),
        ('noncurrent_contract','ContractWithCustomerLiabilityNoncurrent','Balance sheets: long-term unearned revenue',True),
        ('noncurrent_tax','AccruedIncomeTaxesNoncurrent','Balance sheets: long-term income taxes; not a separate debt claim by default',True),
        ('cash','CashAndCashEquivalentsAtCarryingValue','Balance sheets and Note 4: cash and cash equivalents',True),
        ('current_investments','ShortTermInvestments','Balance sheets/Note 4: short-term investments in reported current assets',True),
        ('long_investments','LongTermInvestments','Balance sheets/Note 4: equity and other investments, mixed long-term perimeter',True),
        ('current_debt','LongTermDebtCurrent','Balance sheets and Note 10: current portion of carrying term debt',True),
        ('noncurrent_debt','LongTermDebtNoncurrent','Balance sheets and Note 10: noncurrent carrying term debt',True),
    ]
    for key,concept,location,instant in specs: f.fact(key,concept,location,instant=instant)
    f.fact('AmortizationOfIntangibleAssets','AmortizationOfIntangibleAssets','Note 9: finite-lived intangible amortization expense')
    f.fact('component_receivables','OtherReceivablesRelatedToPurchaseOfComponents' if f.year==2025 else 'OtherReceivablesCurrentRelatedToPurchaseOfComponents',
        'Note 1: server-component facilitation receivables within other current assets',instant=True,namespace='msft')
    f.entry('revenue','Revenue',['revenue'],scope='Reported consolidated annual revenue',rationale='Selected face-statement total, confirming occurrences retained.')
    f.entry('ebit','EBIT / operating income',['ebit'],scope='Reported consolidated operating income',rationale='Existing direct operating-income semantics; no pretax residual.')
    f.entry('nonoperating_income','Reported other income (expense), net',['nonoperating_income'],
        scope='Reported nonoperating income statement population',rationale='Retain the disclosed bridge from operating to pretax income, not an operating adjustment.')
    f.entry('sbc_cost_proxy','Accepted SBC expense cost proxy',['AllocatedShareBasedCompensationExpense'],status=ACCEPTED,origin='proxy',
        role='accepted_recognized_expense_cost_proxy',scope='Recognized annual SBC expense, counted once',
        rationale='Existing user acceptance: an EBIT-based profile already expenses SBC; CFO add-back is a linked reconciliation role, not another cost.',
        limitations=('Not cash replacement compensation or outstanding-award value; no economic adjustment performed.',))
    f.entry('expense_da','Rounded depreciation plus intangible amortization',['Depreciation','AmortizationOfIntangibleAssets'],
        scope='Existing MSFT expense-component policy; no joint timing certification',
        rationale='Notes 6 and 9 disjoint PP&E depreciation and finite-lived intangible amortization; finance-lease amortization is not added again.',
        policy='msft_annual_d_and_a_v1',limitations=('Rounded components; lease/EBIT/inventory timing compatibility remains unproved.',))
    f.entry('adjusted_ap','AP excluding PP&E remaining in AP',['ap','PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable'],[1,-1],
        scope='Reported supplier AP less explicitly disclosed closing capital creditors',
        rationale='Note 6 explicitly places capital-creditor balance within AP; exclusion is a stock classification, not cash conversion.')
    f.entry('partial_nwc','Selected narrow current operating-capital subtotal',
        ['ar','inventory','ap','PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable','current_contract','compensation'],[1,1,-1,1,-1,-1],
        scope='AR + inventory - (AP - PP&E-in-AP) - current contract liabilities - accrued compensation',
        rationale='Face-statement captions are disjoint; AP subcomponent removed once. Explicit mixed-caption/noncurrent/tax/lease omissions remain.',
        completeness='partial',limitations=('Not complete Operating NWC or cash movement; acquisition/FX/reclassification and joint timing unbridged.',))
    f.entry('whole_ap_comparator','Diagnostic same perimeter using whole AP',
        ['ar','inventory','ap','current_contract','compensation'],[1,1,-1,-1,-1],scope='Diagnostic comparator, not selected operating treatment',
        rationale='Makes the source-supported capital-creditor exclusion effect visible; not a competing approved cash adjustment.',completeness='partial')
    f.entry('current_liquidity','Cash plus reported short-term investments',['cash','current_investments'],
        scope='Reported current cash/investment parent only',rationale='Same current-assets panel; Note 4 separately allocates columns without overlap; reported parent independently confirms the sum.',
        limitations=('Not unrestricted/excess cash; long-term/strategic/derivative populations excluded, not zero.',))
    f.entry('term_debt','Reported term-debt carrying total',['current_debt','noncurrent_debt'],scope='Note 10 current plus noncurrent term-debt carrying population, excluding leases',
        rationale='Note 10 explicitly subtracts current portion from total to present noncurrent balance; no principal/fair-value substitution.',
        limitations=('Not a certified borrowing-plus-lease total. FY2026 commercial-paper amount remains unavailable.',))
    f.entry('reported_etr','Historical reported accounting ETR',['IncomeTaxExpenseBenefit','pretax'],formula='DIVIDE',unit='pure',
        scope='Consolidated reported provision / eligible positive continuing pretax income',
        rationale='Existing annual_reported_effective_tax_rate_v1: positive denominator, no clamp or forecast interpretation.',
        policy='annual_reported_effective_tax_rate_v1',limitations=('No future operating-tax basis or rate approved.',))
    extra = [
        ('current_liquidity_parent','CashCashEquivalentsAndShortTermInvestments','Balance sheets: total cash, cash equivalents and short-term investments','us-gaap'),
        ('term_debt_parent','LongTermDebt','Note 10: total term debt before current-portion subtraction','us-gaap'),
        ('debt_face','DebtInstrumentCarryingAmount','Note 10: face/principal in this specific table, before discounts/costs/hedge/premium adjustments; tag name does not change caption','us-gaap'),
        ('debt_fair','LongTermDebtFairValue','Note 10: rounded estimated fair value, not carrying amount','us-gaap'),
        ('operating_liability','OperatingLeaseLiability','Note 13: discounted operating lease liabilities','us-gaap'),
        ('finance_liability','FinanceLeaseLiability','Note 13: discounted finance lease liabilities','us-gaap'),
        ('equity_method','EquityMethodInvestments','Note 4: rounded equity-method investments; overlaps long-term investment parent','us-gaap'),
        ('nonmarketable','EquitySecuritiesWithoutReadilyDeterminableFairValueAmount','Note 4: nonmarketable equity population; not an additional asset beyond investment captions','us-gaap'),
        ('loss_credit_dta','DeferredTaxAssetsOperatingLossAndTaxCreditCarryForwards','Note 11: combined loss-and-credit carryforward DTA, not pure NOL DTA','msft'),
        ('year_end_common','CommonStockSharesOutstanding','Balance sheets and Note 15: fiscal-year-end common shares, rounded','us-gaap'),
        ('tax_interest_accrued','UnrecognizedTaxBenefitsIncomeTaxPenaltiesAndInterestAccrued','Note 11: closing tax-position interest net of tax benefits, not annual borrowing interest cash','us-gaap'),
    ]
    for key,concept,location,namespace in extra:
        f.fact(key,concept,location,instant=True,namespace=namespace,unit='shares' if key=='year_end_common' else 'USD')
    for key in ('long_investments','debt_face','debt_fair','equity_method','nonmarketable','loss_credit_dta','year_end_common','operating_liability','finance_liability'):
        f.entry(key,f.facts[key]['location'],[key],scope=f.facts[key]['location'],
            rationale='Retained note/statement population selected as labelled, with no cross-basis substitution or economic netting.',
            completeness='reported_population_only',limitations=('No complete equity bridge, debt convention, excess-cash classification or dilution approval.',))
    for kind in ('operating','finance'):
        concept=kind.capitalize()+'LeaseLiability'
        for part,member in (('current','us-gaap:OtherCurrentLiabilitiesMember'),
                ('noncurrent','msft:OperatingLeaseLiabilitiesMember' if kind=='operating' else 'us-gaap:OtherNoncurrentLiabilitiesMember')):
            key=kind+'_'+part
            f.fact(key,concept,'Note 13: '+kind+' lease '+part+' recognized liability location',instant=True,
                dimensions=(('us-gaap:BalanceSheetLocationAxis',member),))
    f.entry('component_receivables','Server-component facilitation receivables',['component_receivables'],
        scope='Note 1 identified balance within mixed other current assets; excluded from selected narrow NWC',
        rationale='Known gross exposure, not a silently accepted operating allocation or a bound on all omitted balances.',
        completeness='partial',limitations=('Inclusion would require explicit operating/financing classification and matching-obligation review.',))
    if f.year==2025:
        f.fact('commercial_paper','CommercialPaper','Balance sheets and Note 10 explicit no commercial paper issued or outstanding',instant=True)
        f.entry('disclosed_borrowings','Disclosed CP plus term-debt carrying population',['commercial_paper','term_debt_parent'],
            scope='Disclosed zero commercial paper plus Note 10 term debt; leases separate',
            rationale='Affirmative zero, not tag absence; CP and term obligations are explicitly disjoint.',
            limitations=('Not economic debt including leases/other claims; not extended to FY2026.',))
    cover_date='2025-07-24' if f.year==2025 else '2026-07-23'
    f.fact('cover_common','EntityCommonStockSharesOutstanding','Cover page: actual observation date, unclassed common stock',instant=True,namespace='dei',unit='shares',as_of=cover_date)
    f.entry('cover_common','Separately dated cover common shares',['cover_common'],scope='Issuer common shares at the cover observation date',
        rationale='Retain actual July date; use rounded June 30 observation for an annual-end snapshot, not this later count.',
        limitations=('Not weighted-average or diluted shares; no award count added.',))
    award_dims=(('us-gaap:AwardTypeAxis','us-gaap:RestrictedStockMember'),)
    f.fact('nonvested_awards','ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber',
        'Note 17: nonvested restricted stock award balance at annual end',instant=True,unit='shares',dimensions=award_dims)
    f.fact('unrecognized_award_cost','EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized',
        'Note 17: future unrecognized compensation, not current expense or award market value',instant=True,dimensions=award_dims)
    for key in ('nonvested_awards','unrecognized_award_cost'):
        f.entry(key,f.facts[key]['location'],[key],scope=f.facts[key]['location'],
            rationale='Retain explicit award-class/date population separately from common shares and current SBC expense.',
            completeness='reported_population_only',limitations=('Not incremental dilution or a fair-value equity claim; outstanding option count not established.',))


APPROVAL_SHEET = [
    dict(decision_id='NWC-PERIMETER',status=PROPOSED,
        recommendation='Use the source-supported narrow NWC levels and +6,892m adjacent BOOK movement as a partial diagnostic only; retain cash-flow movements as the separate cash evidence.',
        alternative='Require a complete operating-capital level: mixed/noncurrent allocations and cash bridge would remain unresolved; no numerical estimate recommended.',
        numeric_comparison='Whole-AP diagnostic movement -12,908m versus capital-creditor-excluded +6,892m: +19,800m difference, not cash.',
        blocks='Does not block this historical draft. Blocks complete NWC/cash-change claims and later EBIT-based consumption without an aligned movement contract.'),
    dict(decision_id='LEASE-METHOD',status=PROPOSED,
        recommendation='Preserve the accepted restricted three-payment dataset. Retain the prior cash-service direction in principle; require one precise whole-method lease treatment before future consumption.',
        alternative='Financing treatment is possible only as a consistently replacing method covering expense/amortization, principal, assets, debt and tax; not silently selected here.',
        numeric_comparison='Payment classes and recognized liabilities are separately populated; no combined service or interest total.',
        blocks='Missing comprehensive coverage and interest overlap do not block reported packaging; block any certified total or future unlevering/lease adjustment.'),
    dict(decision_id='INVESTMENT-TIMING',status=PROPOSED,
        recommendation='Select reported cash PP&E as narrow historical investment and keep capital creditors, noncash lease additions and combined acquisition/intangible purchases separate.',
        alternative='A complete accrual/organic reinvestment schedule needs independently supported allocations; do not use cash plus creditor movement as a complete bridge.',
        numeric_comparison='Rounded capital creditors 6,900m/26,700m; combined cash purchases 5,978m/1,743m are visible but unallocated.',
        blocks='Does not block narrow reported investment. Complete reinvestment and D&A/EBIT/book-capital timing compatibility remain unproved, not demonstrated incompatible.'),
    dict(decision_id='TAX-BASIS',status=PROPOSED,
        recommendation='Keep reported provision, positive continuing Pretax, accounting ETR, deferred items and cash tax separate. Approve no operating/future tax rate now.',
        alternative='A later operating-tax policy needs an explicit justified basis and analyst acceptance; reported ETR or cash tax is not automatically that basis.',
        numeric_comparison='Historical ETR points are calculated only from the stated provision/Pretax operands; no numerical future recommendation.',
        blocks='Not a historical data blocker; future operating-tax treatment remains a separate decision.'),
    dict(decision_id='BALANCE-SCOPE',status=PROPOSED,
        recommendation='Use the evidenced current-liquidity and term-debt carrying populations for historical review; keep strategic/equity-method investments, leases and other claims separate.',
        alternative='Excess-cash or all-borrowing/economic-debt totals require availability, valuation and scope decisions; FY2026 absent CP is not zero.',
        numeric_comparison='Current liquidity 94,565m/76,843m; term debt 43,151m/40,294m; mixed long-term investments 15,405m/36,348m are not added or netted.',
        blocks='Does not block named source populations. Broader balance-sheet/equity-bridge completeness remains unresolved.'),
    dict(decision_id='SHARES-AWARDS',status=PROPOSED,
        recommendation='Select the rounded June 30 common-share observation for the fiscal-end historical snapshot; keep exact later cover observations and nonvested awards separately.',
        alternative='A later dated share denominator or outstanding-award economic method must specify date/classes and prevent double counting the already accepted SBC cost proxy.',
        numeric_comparison='June30 common 7,434m/7,427m; nonvested awards 82m/78m are not incremental diluted shares. No dilution estimate.',
        blocks='Does not block dated historical observations; blocks diluted/fully adjusted share or equity-claim use.')
]


def finish(filings):
    periods=[];sources=[]
    for f in filings:
        for kind,receipt in (('primary',f.primary),('instance',f.instance)):
            a=receipt.artifact
            sources.append(dict(source_id=f'FY{f.year}-{kind}',url=a.url,accession=a.accession,
                retained_path='docs/evidence/analyst-operating-nwc-response-bodies.json',
                retained_pointer='/artifacts/'+str((18 if f.year==2025 else 20)+(kind=='instance')),
                sha256=a.sha256,representation=a.representation,digest_type=a.digest_type,
                byte_length=receipt.byte_length,retrieved_at_utc=receipt.retrieved_at_utc,http_status=receipt.http_status))
        entries={e['input_id']:e for e in f.entries}
        checks=[]
        def eq(name,left,right):
            if left!=right:raise ValueError('Independent population check failed: '+name)
            checks.append(dict(check_id=name,left=str(left),right=str(right),difference='0',result='PASS'))
        eq('current_liquidity_parent',Decimal(entries['current_liquidity']['value']),Decimal(f.facts['current_liquidity_parent']['value']))
        eq('term_debt_parent',Decimal(entries['term_debt']['value']),Decimal(f.facts['term_debt_parent']['value']))
        eq('ebit_to_reported_pretax',Decimal(f.facts['ebit']['value'])+Decimal(f.facts['nonoperating_income']['value']),Decimal(f.facts['pretax']['value']))
        eq('pretax_tax_to_reported_net_income',Decimal(f.facts['pretax']['value'])-Decimal(f.facts['IncomeTaxExpenseBenefit']['value']),Decimal(f.facts['NetIncomeLoss']['value']))
        for kind in ('operating','finance'):
            eq(kind+'_lease_partition',sum((Decimal(f.facts[kind+'_'+part]['value']) for part in ('current','noncurrent')),Decimal(0)),
                Decimal(f.facts[kind+'_liability']['value']))
        cfo_terms=[next(e for e in f.entries if e['input_id']=='reported:'+name) for name in f.bundle.cfo_terms]
        eq('complete_displayed_cfo',sum((Decimal(e['value']) for e in cfo_terms),Decimal(0)),
            Decimal(entries['reported:NetCashProvidedByUsedInOperatingActivities']['value']))
        # The independent primary headings correct older review prose citations,
        # without changing any original registry identities, facts or receipts.
        for heading in ('NOTE 11 — INCOME TAXES','NOTE 17 — EMPLOYEE STOCK AND SAVINGS PLANS'):
            if heading not in f.text:raise ValueError('Required note heading changed')
        original_unknowns=[dict(input_id=v.input_id,status=v.status,reason=v.reason,value=None) for v in f.bundle.unknowns]
        unknowns={v.input_id:dict(input_id=v.input_id,status=UNRESOLVED,reason=v.reason,value=None)
            for v in f.bundle.unknowns if v.input_id!='sbc_economic_treatment'}
        unknowns.update((key,dict(input_id=key,status=UNRESOLVED,value=None,reason=reason)) for key,reason in (
            ('complete_operating_nwc','Mixed other current assets/liabilities, current customer-financing allocation and noncurrent operating accounts remain incomplete; no zero or uncertainty bound.'),
            ('pure_nol_dta','Only a combined loss-and-credit carryforward DTA is established; no pure NOL allocation.'),
            ('preferred_nci_pension','No affirmative complete preferred/NCI/pension population or absence established by this bounded review; not zero.'),
            ('outstanding_options_and_dilution','Restricted stock awards are disclosed, but a complete option/award economic claim and incremental dilution are not established.'),
            ('excess_unrestricted_cash','Current-liquidity reported population does not prove unrestricted/excess availability or strategic investment valuation.'),
            ('cfo_to_ebit_compatibility','No operating-only tax/interest/lease or complete book-to-cash/FX/acquisition bridge; reported CFO check does not approve EBIT-based consumption.'),
        ))
        if f.year==2026:unknowns['commercial_paper']=dict(input_id='commercial_paper',status=UNRESOLVED,value=None,
            reason='No FY2026 borrowing CP fact or affirmative no-outstanding disclosure; term-debt table is not proof of absent other borrowing.')
        scope_reviews=[]
        for marker,meaning in (
            ('purchases of property and equipment remaining in accounts payable','Capital-creditor stock is explicitly within AP; exclude once from narrow book perimeter.'),
            ('The components of long-term debt were as follows','Term-debt table has an explicit carrying/current/noncurrent partition, not all-debt or lease scope.'),
            ('Intangible assets amortization expense','Note 9 expense population, distinct from mixed CFO adjustment.'),
            ('Nonvested balance, end of year','Restricted-stock award balance, not incremental diluted common shares.'),
        ):
            match=re.search(re.escape(marker),f.text,re.I)
            if match is None:raise ValueError('Reviewed scope assertion absent: '+marker)
            scope_reviews.append(dict(primary_source=f'FY{f.year}-primary',
                normalized_visible_text_offset=match.start(),exact_excerpt=f.text[match.start():match.end()+140],meaning=meaning))
        periods.append(dict(fiscal_year=f.year,identity=dict(cik=f.period.cik,accession=f.period.accession,form=f.period.form,
            annual_start=str(f.period.annual_start),annual_end=str(f.period.annual_end)),facts=f.facts,inputs=f.entries,
            cfo_reconciliation=dict(terms=[e['input_id'] for e in cfo_terms],check='complete_displayed_cfo',
                scope='Reported consolidated reconciliation only; not unlevered/organic cash or book delta NWC.'),
            checks=checks,scope_reviews=scope_reviews,original_bundle_unknowns=original_unknowns,
            unresolved_requirements=list(unknowns.values()),
            accepted_sbc_disposition='Original bundle SBC unknown retained as source history; subsequent accepted recognized-expense proxy is recorded separately. No award/dilution or cash adjustment approved.'))
    def selected(i,key):return Decimal(next(e['value'] for e in periods[i]['inputs'] if e['input_id']==key))
    movement=selected(1,'partial_nwc')-selected(0,'partial_nwc')
    comparator=selected(1,'whole_ap_comparator')-selected(0,'whole_ap_comparator')
    creditor=Decimal(filings[1].facts['PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable']['value'])-Decimal(filings[0].facts['PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable']['value'])
    if movement-comparator!=creditor:raise ValueError('Capital-creditor classification movement differs')
    comparative=[]
    f=filings[1]
    for ordinal,concept,expected in ((692,'DepreciationAmortizationAndOther','29433000000'),
                                    (698,'GainLossOnInvestmentsAndDerivativeInstruments','-5329000000')):
        fact=f.root[ordinal];context=f.contexts[fact.attrib['contextRef']]
        if (fact.tag!='{'+f.namespaces['msft']+'}'+concept or fact.text!=expected or
                cash._context(context)!=(789019,date(2024,7,1),date(2025,6,30))):raise ValueError('Recast comparative source changed')
        attrs,text=f.inline.facts[fact.attrib['id']]
        if inline_amount(attrs,text)!=Decimal(expected):raise ValueError('Comparative primary changed')
        comparative.append(dict(concept=concept,raw_value=expected,unit='USD',precision=fact.attrib['decimals'],
            ordinal=ordinal,context_id=fact.attrib['contextRef'],primary_locator='inline#'+fact.attrib['id'],
            instance_source='FY2026-instance',primary_source='FY2026-primary',
            start='2024-07-01',end='2025-06-30',role='comparative_support_only_not_selected_period_input'))
    return dict(schema='msft-draft-analyst-historical-package-v1',version='1',baseline_revision=BASELINE,
        issuer='MSFT',phase='1',financial_sufficiency='NOT_ASSESSED',valuation_consumption_approved=False,
        original_artifacts_modified=False,new_sec_requests=0,sources=sources,periods=periods,
        adjacent_book_movement=dict(from_end='2025-06-30',to_end='2026-06-30',value_usd=str(movement),
            formula='FY2026.partial_nwc - FY2025.partial_nwc',whole_ap_comparator_usd=str(comparator),
            capital_creditor_exclusion_effect_usd=str(creditor),status=SUPPORTED,completeness='partial',
            precision='Rounded PP&E-in-AP operands decimals -8; no improved precision or supported allocation range.',
            limitations=['Not cash delta NWC. Acquisition/FX/noncash/reclassification effects unbridged.',
                'No FY2025 annual movement selected from an unregistered FY2024 package.']),
        separately_identified_omitted_asset_growth=dict(value_usd=str(Decimal(filings[1].facts['component_receivables']['value'])-Decimal(filings[0].facts['component_receivables']['value'])),
            formula='FY2026.component_receivables - FY2025.component_receivables',status=SUPPORTED,
            limitation='Gross server-facilitation receivable growth only; not accepted as operating, cash, a matching-liability allocation or a bound on full NWC.'),
        approval_sheet=APPROVAL_SHEET,comparative_support=comparative,
        citation_corrections=['Selected primaries place income taxes in Note 11, unearned revenue in Note 12, and employee stock/SBC in Note 17.',
            'Older review prose note numbers are retained as history; this draft cites actual headings and inline IDs. Amounts and original evidence are unchanged.'],
        preserved_acceptance_reference='docs/msft-treatment-acceptance-checklist.md',
        stopping_condition='User review of one consolidated sheet; no automatic additional research, override, policy change or Phase 2 work.')


if __name__ == '__main__':
    result=build()
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--check' in sys.argv:
        if (ROOT/OUTPUT).read_text()!=text: raise SystemExit('Package replay differs')
        print('Exact two-period package replay passed')
    else: print(text,end='')
