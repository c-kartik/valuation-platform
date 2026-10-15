"""Two reviewed MSFT annuals: separate historical selections, not a runtime adapter.

Scoped user acceptance only; no sufficiency approval, retrieval or valuation. Original
registries/outputs are read-only. Exact source occurrences and statement tags
are checked before any point enters this separate company-specific package.
"""
from datetime import date, datetime, timezone
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
from valuation_platform.analyst.analyst_overrides import relevant, _json
from valuation_platform.analyst.prepared_assembly import digest
from valuation_platform.analyst.historical_inputs import ManualIdentity

OUTPUT = 'docs/company-data-preparation/msft-analyst-input-package.json'
BASELINE = 'daeb3b007a664cfe9fe31fe426d1f5ae40be503a'
ACCEPTED = 'existing_accepted_treatment'
SUPPORTED = 'source_supported_selection_or_calculation'
PROPOSED = 'proposed_pending_user_approval'
UNRESOLVED = 'unresolved_requirement'
ACCEPTANCE_PATH = 'docs/company-data-preparation/msft-analyst-treatment-acceptance.json'
ACCEPTANCE_BASIS = 'ce919800126d7a4ff35ffbe7e23e5b080db1c2b9'
APPROVED_SCOPE = 'accepted_for_stated_historical_preparation_scope'
USER_DECISIONS = {
    'operating_capital': 'Select named-only partial operating capital; residual-caption estimate remains non-default. Neither is complete current NWC or cash delta NWC.',
    'leases_da': 'Operating leases service costs; finance leases asset financing. Preserve rounded D&A and the explicitly unproved finance-amortization-inclusion assumption; no additional ROU add-back.',
    'investment': 'Keep cash PP&E, capital creditors, noncash finance additions and combined acquisition/intangible spending separate; no complete reinvestment subtotal.',
    'cash': 'Select current financial balances less identified restrictions; unknown restrictions and operating reserves remain unknown, not unrestricted or excess cash.',
    'borrowings': 'Select named term-debt-plus-finance-lease subtotal only. Reject zero additional FY2026 short borrowing; source remains null/unknown, no complete-debt certification.',
    'taxes_shares': 'Accept named historical schedules with original dates, precision and scope; no future tax rate, award valuation or forecast dilution approval.',
}


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
    if attrs.get('format') is None and re.fullmatch(r'[+-]?\d+(?:\.\d+)?',text.strip()):
        value=Decimal(text.strip())
        return (-value if attrs.get('sign')=='-' else value)*Decimal(10)**int(attrs.get('scale','0'))
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
            # explicitly reviewed class/location populations are checked separately.
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
    return accepted_view(resolve_decisions(filings, finish(filings)))


def approval_record(proposal):
    """Explicit one-time user-approved recording command, never normal replay.

    Reuse audit canonicalization/relevant-content revision and manual identity.
    This is a selection overlay, not a numeric override of generic CF movements.
    """
    record = dict(schema='msft-treatment-acceptance-audit-v1', version=1,
        sequence=1, previous='0'*64, action='ACCEPT_SCOPED_SELECTIONS',
        author='User, explicit MSFT FY2025–FY2026 treatment-set instruction',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Record the user-approved six-part treatment set; not financial sufficiency or Phase 2 authorization.',
        authority='Current user instruction: Implement the user-approved treatment set below in the separate MSFT analyst-input view for FY2025–2026.',
        source_commit=ACCEPTANCE_BASIS, source_revision=digest(relevant(proposal)),
        decisions=USER_DECISIONS.copy(), financial_sufficiency='NOT_ASSESSED',
        phase1_closed=False, valuation_consumption_approved=False)
    record['sha256'] = digest(record)
    return record


def accepted_view(proposal, audit_path=None):
    """Fail closed on a changed proposal/evidence revision or audit receipt.

    Original facts, proposed calculations/assumptions and old approval sheets
    are never rewritten. Persisted acceptance only selects a separate view.
    """
    path = Path(audit_path) if audit_path is not None else ROOT/ACCEPTANCE_PATH
    record = _json(path.read_text())
    expected = {'schema','version','sequence','previous','action','author','recorded_at_utc',
        'rationale','authority','source_commit','source_revision','decisions',
        'financial_sufficiency','phase1_closed','valuation_consumption_approved','sha256'}
    if set(record) != expected or record.get('sha256') != digest({k:v for k,v in record.items() if k != 'sha256'}):
        raise ValueError('Changed or malformed MSFT acceptance audit')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    if (record['schema']!='msft-treatment-acceptance-audit-v1' or type(record['version']) is not int or record['version']!=1
            or type(record['sequence']) is not int or record['sequence']!=1 or record['previous']!='0'*64 or record['action']!='ACCEPT_SCOPED_SELECTIONS'
            or record['source_commit']!=ACCEPTANCE_BASIS or record['decisions']!=USER_DECISIONS
            or record['financial_sufficiency']!='NOT_ASSESSED' or record['phase1_closed'] is not False
            or record['valuation_consumption_approved'] is not False):
        raise ValueError('Unregistered MSFT acceptance scope')
    if record['source_revision'] != digest(relevant(proposal)):
        raise ValueError('Stale MSFT acceptance: source, evidence or proposal changed; explicit revalidation required')
    result=json.loads(json.dumps(proposal)); rows=[]
    for index,(original,resolution) in enumerate(zip(proposal['periods'],proposal['decision_resolution']['periods'])):
        entries={e['input_id']:e for e in original['inputs']}; schedules=resolution['schedules']
        def select(item,ref,label,**limitations):
            parts=ref.split('/')
            if parts[0]=='periods':
                parts=['periods',str(index),'inputs',str(next(i for i,e in enumerate(original['inputs']) if e['input_id']==parts[-1]))]
            else:parts=['decision_resolution','periods',str(index),'schedules',parts[-1]]
            selected=json.loads(json.dumps(item))
            selected.update(status=APPROVED_SCOPE,accepted=True)
            return dict(selected=selected,source_reference='/'+'/'.join(parts),source_status=item['status'],label=label,
                review=APPROVED_SCOPE,approval_sha256=record['sha256'],**limitations)
        row=dict(fiscal_year=original['fiscal_year'],identity=original['identity'],
            operating_capital=select(schedules['named_expansion'],'decision_resolution/periods/schedules/named_expansion',
                'Named-only partial operating capital (includes noncurrent balances)',
                complete_current_nwc=False,cash_delta_nwc_certified=False),
            original_current_only_partial_nwc=entries['partial_nwc'],
            estimated_nondefault_alternative=dict(default=False,estimated=True,
                label='Residual-caption partial operating-capital estimate (includes noncurrent balances)',
                schedule=schedules['proposed_operating_capital'],
                adjacent_book_movement_usd=proposal['decision_resolution']['adjacent_book_movements_usd']['proposed_operating_capital']),
            lease_classification=dict(operating='service_cost',finance='asset_financing',review=APPROVED_SCOPE,
                complete_lease_coverage=False),
            expense_da=select(entries['expense_da'],'periods/inputs/expense_da','Original rounded expense D&A',
                assumption='Finance amortization already included; accepted assumption, NOT source-confirmed overlap.',
                source_confirmed_overlap=False,additional_rou_addback=False),
            investment_columns=[entries[key] for key in (
                'reported:PaymentsToAcquirePropertyPlantAndEquipment',
                'reported:PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable',
                'reported:RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability',
                'reported:AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets')],
            complete_reinvestment=False,
            cash=select(schedules['known_restriction_current_pool'] if original['fiscal_year']==2026 else entries['current_liquidity'],
                'decision_resolution/periods/schedules/known_restriction_current_pool' if original['fiscal_year']==2026 else 'periods/inputs/current_liquidity',
                'Current financial balances less identified restrictions',
                unknown_restrictions=None,operating_reserve=None,unrestricted_or_excess_cash=False),
            borrowings=select(schedules['term_and_finance_leases'],'decision_resolution/periods/schedules/term_and_finance_leases',
                'Named term-debt-plus-finance-lease subtotal only',complete_debt=False),
            additional_short_borrowing=dict(value_usd=None if original['fiscal_year']==2026 else '0',
                origin='unavailable' if original['fiscal_year']==2026 else 'reported',
                null_reason='Ending additional short borrowing unavailable; zero proposal rejected.' if original['fiscal_year']==2026 else None),
            taxes=[entries[k] for k in ('reported:IncomeTaxExpenseBenefit','reported:IncomeTaxesPaidNet',
                'reported:DeferredIncomeTaxExpenseBenefit','reported:IncreaseDecreaseInAccruedIncomeTaxesPayable','reported_etr')],
            additional_deferred_tax_cfo=[entries[k] for k in ('reported:DeferredIncomeTaxesAndTaxCredits',) if k in entries],
            pretax_fact=original['facts']['pretax'],
            shares_awards=[entries[k] for k in ('year_end_common','cover_common','nonvested_awards','unrecognized_award_cost')],
            unknowns=resolution['unavailable_amounts'],
            future_tax_rate_approved=False,award_valuation_approved=False,forecast_dilution_approved=False)
        rows.append(row)
    result['accepted_view']=json.loads(json.dumps(dict(schema='msft-accepted-historical-view-v1',version=1,
        approval_audit=record,periods=rows,financial_sufficiency='NOT_ASSESSED',
        selected_adjacent_book_movement_usd=proposal['decision_resolution']['adjacent_book_movements_usd']['named_expansion'],
        movement_is_cash_delta_nwc=False,complete_operating_capital=False,
        prior_proposals_retained=True,short_debt_zero_proposal_status='REJECTED_NOT_SELECTED',
        decision_statuses={key:APPROVED_SCOPE for key in USER_DECISIONS},
        investment_columns_review=APPROVED_SCOPE,tax_share_schedules_review=APPROVED_SCOPE,
        phase1_closed=False,valuation_consumption_approved=False,
        stopping_condition='Stop after MSFT integration. No automatic issuer work or research.')))
    return result


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


REVIEW_BASIS='fb571f1e40bc8a62fc55f4788ebe34d7a376b1f7'
PROPOSAL_AUTHOR='Repository MSFT analyst-treatment review; proposed, not user acceptance'
PROPOSAL_TIME='2026-10-15T14:53:18+00:00'


def resolve_decisions(filings, original):
    """One company-specific revision of this report, never a runtime overlay.

    Original facts/inputs stay intact. New source observations and proposed
    classification schedules occupy separate sections with explicit assumptions.
    """
    result=json.loads(json.dumps(original))
    result.update(schema='msft-draft-analyst-historical-package-v2',version='2',review_basis=REVIEW_BASIS,
        previous_approval_sheet=result['approval_sheet'],proposal_author=PROPOSAL_AUTHOR,
        proposed_at_utc=PROPOSAL_TIME)
    resolutions=[]
    for f in filings:
        original_keys=set(f.facts)
        def read(key,concept,location,*,dimensions=(),annual=False,namespace='us-gaap'):
            return f.fact(key,concept,location,instant=not annual,dimensions=dimensions,namespace=namespace)
        for key,concept,where in (
            ('long_ar','AccountsReceivableNetNoncurrent','Note 1: ordinary long-term contract receivables, not the customer financing program'),
            ('customer_finance','FinanceReceivablesNet','Note 1: combined current/noncurrent customer-finance receivables'),
            ('other_long_assets','OtherAssetsNoncurrent','Balance sheets: other long-term assets'),
            ('other_long_liabilities','OtherLiabilitiesNoncurrent','Balance sheets: other long-term liabilities'),
            ('derivative_current_liability','DerivativeLiabilitiesCurrent','Note 5: net carrying derivative liability located in other current liabilities'),
            ('derivative_long_liability','DerivativeLiabilitiesNoncurrent','Note 5: net carrying derivative liability located in other long-term liabilities'),
            ('debt_discount_cost','DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet','Note 10: subtract discount and issuance costs from face'),
            ('debt_hedge_adjustment','HedgeAccountingFairValueAdjustments','Note 10: signed hedge carrying adjustment'),
            ('ppe_gross','PropertyPlantAndEquipmentGross','Note 6: total recognized gross PP&E, includes finance leases per Note 1'),
            ('ppe_accumulated','AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment','Note 6: total accumulated PP&E depreciation'),
            ('ppe_net','PropertyPlantAndEquipmentNet','Note 6: total recognized PP&E net'),
            ('legal_accrual','LossContingencyAccrualAtCarryingValue','Note 14: accrued legal liabilities, not an incremental debt claim'),
            ('legal_additional_exposure','LossContingencyRangeOfPossibleLossPortionNotAccrued','Note 14: reasonably possible additional losses, not an expected-value provision'),
        ):read(key,concept,where,namespace='msft' if key in ('customer_finance','debt_hedge_adjustment') else 'us-gaap')
        read('debt_exchange_premium','PremiumOnDebtExchange1','Note 10: subtract debt-exchange premium',namespace='msft')
        for key,concept,member,where in (
            ('dta_in_other_assets','DeferredIncomeTaxAssetsNet','us-gaap:OtherNoncurrentAssetsMember','Note 11 Reported As: DTA actually within other long-term assets, not gross DTA'),
            ('derivative_current_asset','DerivativeAssetsCurrent','us-gaap:OtherCurrentAssetsMember','Note 5: net derivative carrying asset within OCA'),
            ('derivative_long_asset','DerivativeAssetsNoncurrent','us-gaap:OtherNoncurrentAssetsMember','Note 5: net derivative carrying asset within other LT assets'),
        ):read(key,concept,where,dimensions=(('us-gaap:BalanceSheetLocationAxis',member),))
        for key,concept in (('finance_ppe_gross','PropertyPlantAndEquipmentGross'),
            ('finance_ppe_accumulated','AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment'),
            ('finance_ppe_net','PropertyPlantAndEquipmentNet')):
            read(key,concept,'Note 13: recognized finance-lease PP&E subset of Note 6 total',
                dimensions=(('us-gaap:LeaseContractualTermAxis','msft:FinanceLeaseMember'),))
        for key,concept in (('short_debt_cash_net','ProceedsFromRepaymentsOfShortTermDebtMaturingInThreeMonthsOrLess'),
            ('long_debt_cash_proceeds','ProceedsFromDebtMaturingInMoreThanThreeMonths'),
            ('long_debt_cash_repayments','RepaymentsOfDebtMaturingInMoreThanThreeMonths')):
            read(key,concept,'Consolidated financing cash-flow row; not an ending-debt balance or gross short-debt bridge',annual=True)
        invest_dims={
            'long_debt_securities':(('us-gaap:FairValueByAssetClassAxis','us-gaap:DebtSecuritiesMember'),),
            'long_listed_equities':(('us-gaap:FairValueByFairValueHierarchyLevelAxis','us-gaap:FairValueInputsLevel1Member'),('us-gaap:FinancialInstrumentAxis','us-gaap:EquitySecuritiesMember')),
            'long_other_equities':(('us-gaap:FinancialInstrumentAxis','us-gaap:EquitySecuritiesMember'),('us-gaap:MeasurementInputTypeAxis','msft:OtherMeasurementMember')),
            'long_derivatives':(('us-gaap:FinancialInstrumentAxis','us-gaap:DerivativeMember'),),
        }
        for key,dims in invest_dims.items():read(key,'LongTermInvestments','Note 4: explicit disjoint long-term investment table row',dimensions=dims)
        if f.year==2026:
            read('restricted_total','RestrictedInvestments','Note 1: supplier-agreement restricted investment total')
            read('restricted_current','RestrictedInvestmentsCurrent','Note 1: supplier restriction inside short-term investments',
                dimensions=(('us-gaap:BalanceSheetLocationAxis','us-gaap:ShortTermInvestmentsMember'),))
            read('restricted_long','RestrictedInvestmentsNoncurrent','Note 1: supplier restriction inside equity and other investments',
                dimensions=(('us-gaap:BalanceSheetLocationAxis','msft:EquityAndOtherInvestmentsMember'),))
        # All below are named historical components/diagnostics, not FCFF or
        # an accepted economic adjustment. References name exact source operands.
        schedules={}
        def calc(key,terms,meaning,*,assumption=None):
            if len({k for k,c in terms})!=len(terms):raise ValueError('Duplicate economic operand')
            values={k:Decimal(f.facts[k]['value']) if k in f.facts else Decimal(schedules[k]['value_usd']) for k,c in terms}
            value=sum((values[k]*c for k,c in terms),Decimal(0))
            schedules[key]=dict(value_usd=str(value),value_millions=str(value/1000000),
                formula_version='msft-analyst-decision-resolution-v2',terms=[dict(operand=k,coefficient=c) for k,c in terms],
                meaning=meaning,status=PROPOSED if assumption else SUPPORTED,origin='proxy' if assumption else 'derived',
                assumption=assumption,accepted=False,precision='Retains every reported operand precision; rounding is not reduced by arithmetic.')
            return value
        # The original partial core is already source-bound, not a new source fact.
        old_entries={e['input_id']:e for e in f.entries}
        schedules['partial_nwc']=dict(value_usd=old_entries['partial_nwc']['value'],meaning='Original narrow partial core, unchanged',status=SUPPORTED,origin='derived',accepted=False)
        calc('named_expansion',[('partial_nwc',1),('long_ar',1),('noncurrent_contract',-1)],'Disclosed operating balance expansion; still a named-only partial perimeter')
        calc('residual_assets',[('other_current_assets',1),('other_long_assets',1),('dta_in_other_assets',-1),('component_receivables',-1),
            ('customer_finance',-1),('derivative_current_asset',-1),('derivative_long_asset',-1)],
            'Observed mixed-asset remainder after explicit disjoint financing/tax/investing exclusions; not a disclosed pure operating caption')
        calc('residual_current_liabilities',[('other_current_liabilities',1),('operating_current',-1),('finance_current',-1),('derivative_current_liability',-1)],
            'Other current liabilities excluding separately located recognized leases and derivatives')
        calc('residual_long_liabilities',[('other_long_liabilities',1),('finance_noncurrent',-1),('derivative_long_liability',-1)],
            'Other LT liabilities excluding finance leases and derivatives; operating noncurrent lease already lies outside this parent')
        proxy_assumption='Classify the explicitly displayed residual asset/accrual captions and AP after the identified PP&E exclusion as operating. This is a whole-caption analyst proxy, not proof of operating allocation or complete NWC; undisclosed components may be material. An unidentified matching facilitation obligation could require a further AP exclusion; it is not assigned zero.'
        calc('proposed_operating_capital',[('partial_nwc',1),('residual_assets',1),('residual_current_liabilities',-1),('residual_long_liabilities',-1),('noncurrent_contract',-1)],
            'Recommended expanded historical operating-capital proxy, including current/noncurrent ordinary operating balances; BOOK basis only',assumption=proxy_assumption)
        calc('alternative_include_facilitation',[('proposed_operating_capital',1),('component_receivables',1)],
            'Less-preferred classification alternative including capital-procurement facilitation as operating',assumption='Contrary to primary recommendation: treat facilitation as operating and do not invent a matching liability.')
        calc('alternative_include_customer_finance',[('proposed_operating_capital',1),('customer_finance',1)],
            'Customer-finance inclusion sensitivity, not an approval',assumption='Classify customer lending as operating rather than a separately financed asset.')
        calc('face_to_carrying',[('debt_face',1),('debt_discount_cost',-1),('debt_hedge_adjustment',1),('debt_exchange_premium',-1)],'Note 10 face-to-carrying reconciliation')
        calc('carrying_less_fair',[('term_debt_parent',1),('debt_fair',-1)],'Historical difference to separately reported rounded fair value, not a valuation gain')
        calc('term_and_finance_leases',[('term_debt_parent',1),('finance_liability',1)],
            'Named term-debt carrying plus recognized finance-lease financing subtotal; not an all-debt completeness assertion',
            assumption='Proposed GAAP-aligned historical classification: finance leases financing; operating leases service, outside this financing subtotal.')
        calc('long_investment_partition',[(k,1) for k in invest_dims],'Note 4 disjoint debt/listed-equity/other-equity/derivative partition')
        calc('current_plus_long_debt_securities',[('cash',1),('current_investments',1),('long_debt_securities',1)],'Broader financial-investment alternative BEFORE restrictions; not available cash')
        calc('cash_and_all_reported_investments',[('cash',1),('current_investments',1),('long_investments',1)],'All reported cash/investment captions; not a cash-like or strategic-value selection')
        calc('nonfinance_ppe_net',[('ppe_net',1),('finance_ppe_net',-1)],'Nonfinance PP&E net stock partition, not cash additions or owned-only D&A')
        calc('finance_ppe_partition',[('finance_ppe_gross',1),('finance_ppe_accumulated',-1)],'Note 13 recognized finance PP&E gross less accumulated depreciation')
        calc('restricted_finance_service',[('FinanceLeaseInterestPaymentOnLiability',1),('FinanceLeasePrincipalPayments',1)],
            'Sum of disjoint disclosed finance lease cash classes only; incomplete all-service coverage, not a new expense input')
        calc('restricted_all_lease_service',[('OperatingLeasePayments',1),('restricted_finance_service',1)],
            'Three disclosed liability-measurement payment classes only; borrowing-interest disclosure excluded, no all-interest claim')
        schedules['expense_da']=dict(value_usd=old_entries['expense_da']['value'],meaning='Original rounded expense-component policy value, unchanged',status=SUPPORTED,origin='derived',accepted=False)
        calc('conditional_da_if_rou_excluded',[('expense_da',1),('FinanceLeaseRightOfUseAssetAmortization',1)],
            'Mechanical alternative ONLY IF separate full income recognition AND exclusion from Note 6 depreciation were established; not selected D&A',
            assumption='Conditional non-overlap/full-income-recognition scenario, neither condition proved. Do not populate an approved value from this sum.')
        if f.year==2026:
            calc('known_restriction_current_pool',[('cash',1),('current_investments',1),('restricted_current',-1)],
                'Current financial pool excluding specifically disclosed supplier restriction; not proven excess cash')
            calc('restricted_partition',[('restricted_current',1),('restricted_long',1)],'Supplier restriction partition, outside mixed-other-asset NWC parents')
        availability='Propose treating the current financial pool as available after specifically disclosed restrictions, with no operating-reserve estimate. Other restrictions are not proved absent and the result is not excess cash.'
        calc('proposed_available_current_pool',
            [('known_restriction_current_pool',1)] if f.year==2026 else [('cash',1),('current_investments',1)],
            'Proposed current financial-asset availability proxy, not an unrestricted/excess-cash fact',assumption=availability)
        checks=[]
        for key,parent in (('face_to_carrying','term_debt_parent'),('long_investment_partition','long_investments'),
                           ('finance_ppe_partition','finance_ppe_net')):
            if Decimal(schedules[key]['value_usd'])!=Decimal(f.facts[parent]['value']):raise ValueError('Resolution parent mismatch: '+key)
            checks.append(dict(check=key,independent_parent=parent,result='PASS'))
        if f.year==2026:
            if schedules['restricted_partition']['value_usd']!=f.facts['restricted_total']['value']:raise ValueError('Restricted partition mismatch')
            checks.append(dict(check='restricted_partition',independent_parent='restricted_total',result='PASS'))
        passages=[]
        for marker in ('Finance leases are included in property and equipment','financing receivables, net were',
                       'generally do not include a significant financing component'):
            m=re.search(re.escape(marker),f.text,re.I)
            if not m:raise ValueError('Required classification passage absent: '+marker)
            passages.append(dict(source=f'FY{f.year}-primary',offset=m.start(),exact_excerpt=f.text[m.start():m.end()+220]))
        if f.year==2026:
            for marker in ('restricted investments pursuant to a supplier agreement','primarily to facilitate the purchase of components'):
                m=re.search(re.escape(marker),f.text,re.I)
                if not m:raise ValueError('Required FY2026 scope evidence absent: '+marker)
                passages.append(dict(source='FY2026-primary',offset=m.start(),exact_excerpt=f.text[max(0,m.start()-100):m.end()+150]))
        assumptions=[dict(assumption_id='RESIDUAL-OPERATING',status=PROPOSED,author=PROPOSAL_AUTHOR,timestamp_utc=PROPOSAL_TIME,
            rationale=proxy_assumption,source_keys=['residual_assets','residual_current_liabilities','residual_long_liabilities'],
            value=None,numeric_effect_schedule='proposed_operating_capital'),
            dict(assumption_id='FINANCE-AMORT-IN-DEPRECIATION',status=PROPOSED,author=PROPOSAL_AUTHOR,timestamp_utc=PROPOSAL_TIME,
                rationale='Recommend treating Note 6 depreciation as finance-lease inclusive for the proposed unchanged D&A schedule because Note 1 expressly puts finance assets in PP&E. Exact annual expense inclusion/capitalized allocation is not certified; no separate ROU add-on.',
                value=None,numeric_effect_schedule='expense_da',alternative='conditional_da_if_rou_excluded'),
            dict(assumption_id='CURRENT-FINANCIAL-AVAILABILITY',status=PROPOSED,author=PROPOSAL_AUTHOR,timestamp_utc=PROPOSAL_TIME,
                rationale=availability,source_amount_for_additional_restrictions=None,
                numeric_effect_schedule='proposed_available_current_pool')]
        if f.year==2026:
            assumptions.append(dict(assumption_id='UNREPORTED-SHORT-DEBT',status=PROPOSED,author=PROPOSAL_AUTHOR,timestamp_utc=PROPOSAL_TIME,
                value_usd='0',origin='analyst_assumption',source_value_usd=None,
                rationale='Recommend no additional unreported short-borrowing amount in the draft estimate: prior explicit CP zero, current net short-debt cash zero, long-debt issuance zero, and only term debt disclosed. Net zero is not gross/ending zero; acquired/noncash/offsetting or embedded exposure is unbridged.',
                evidence_keys=['short_debt_cash_net','long_debt_cash_proceeds','long_debt_cash_repayments'],
                resulting_borrowing_perimeter_usd=f.facts['term_debt_parent']['value'],
                limitation='No supported upper bound on missing short borrowing. Original source commercial-paper amount remains unavailable; explicit user approval required.'))
        resolutions.append(dict(fiscal_year=f.year,additional_facts={k:v for k,v in f.facts.items() if k not in original_keys},
            schedules=schedules,source_checks=checks,scope_passages=passages,assumptions=assumptions,
            historical_tax_and_share_schedule='FINALIZED_AS_REPORTED_FOR_NAMED_DISCLOSURES; no source defect found in existing provision/Pretax/ETR/cash-tax or dated-common/restricted-award points. Future rates, award valuation and forecast dilution are not historical completion prerequisites.',
            unavailable_amounts=['Complete residual operating/nonoperating allocations; matching facilitation obligations; cash acquisition/FX/noncash/reclassification bridge.',
                'Income-recognized versus capitalized finance ROU amortization and exact inclusion in Note 6 depreciation; complete accrual investment/organic allocation.',
                'All-interest overlap, capitalized expense/cash and gross/net basis; complete variable/short-term/nonlease cash.',
                'FY2025 restrictions, FY2026 restricted-long asset-class allocation, operating cash reserve; pure NOL DTA and exhaustive preferred/NCI/pension quantities.',
                'FY2026 ending short-debt source amount (analyst zero proposal is not a reported zero).' if f.year==2026 else 'No extra short-debt source defect: CP zero affirmatively reported.'],
            stopping_condition='Stop after this retained pass and consolidated review. Reopen only on exact allocation/roll-forward disclosure or a separately accepted analyst assumption, never by automatic searching.'))
    def val(i,key):return Decimal(resolutions[i]['schedules'][key]['value_usd'])
    movements={k:str(val(1,k)-val(0,k)) for k in ('named_expansion','proposed_operating_capital','alternative_include_facilitation','alternative_include_customer_finance')}
    result['decision_resolution']=dict(revision='2',periods=resolutions,adjacent_book_movements_usd=movements,
        named_only_vs_proxy_movement_difference_usd=str(Decimal(movements['proposed_operating_capital'])-Decimal(movements['named_expansion'])),
        accepted=False,runtime_integration=False,scope='Historical analyst proposals only; book movements are not cash delta NWC; no FCFF or enterprise-equity calculation.')
    result['approval_sheet']=concrete_approval_sheet()
    return result


def concrete_approval_sheet():
    return [dict(decision_id=key,status=PROPOSED,recommendation=recommendation,alternative=alternative,
        numeric_consequence=numeric,unavailable=unavailable,evidence=evidence,accepted=False)
        for key,recommendation,alternative,numeric,unavailable,evidence in (
        ('NWC-PERIMETER','Exclude capital-procurement facilitation, customer finance, tax, derivative and lease balances; include ordinary long-term contract AR and advances. Recommend the broader explicitly estimated residual-caption operating proxy for review.',
         'Named-only operating expansion avoids the residual classification assumption; facilitation-inclusion alternative is less consistent with the investing narrative.',
         'Proxy -23,427m/-3,372m, book movement +20,055m; named-only -25,755m/-18,600m, +7,155m. Facilitation inclusion adds 8,200m/27,800m, changing movement by +19,600m.',
         'Residual operating allocations, exact matching facilitation obligation and cash acquisition/FX/noncash/reclass bridge.',
         'Notes 1/5/11/12/13, balance sheets and FY2026 Item 7 investing discussion; decision_resolution source keys/primary IDs.'),
        ('LEASE-METHOD','Recommend GAAP-aligned hybrid historical classification: operating leases service/operating cost; finance leases assets and financing. Keep reported EBIT and expense D&A unchanged; classify finance liability with term borrowing, not operating lease liability.',
         'All-lease cash-service is the prior direction in principle, but adopting it now would need a verified profit/loss amortization conversion; this recommendation explicitly changes that proposed direction, not the accepted restricted dataset.',
         'Term plus finance lease subtotal 89,323m/106,888m versus term-only 43,151m/40,294m. Restricted finance cash service 3,655m/5,648m; three-class restricted service 8,586m/12,091m, not comprehensive.',
         'Annual income-recognized/capitalized ROU expense allocation, complete service coverage and interest cash overlap. No guessed EBIT adjustment.',
         'Notes 1/6/9/13: finance assets expressly inside PP&E; liability location partitions, cost/cash and noncash additions.'),
        ('INVESTMENT-TIMING','Retain cash PP&E as the selected cash purchase series; keep capital creditors, noncash finance ROU additions and 100% of combined acquisition/intangible/other purchases as separate investment columns. No organic allocation.',
         'Broader cash-investment classification could include the whole combined purchases caption; adds 5,978m/1,743m but must not be labelled PP&E or organic reinvestment.',
         'Cash PP&E 64,551m/115,948m; noncash finance additions 20,511m/24,608m; capital creditors 6,900m/26,700m. Nonfinance PP&E net stock 160,951m/245,795m; no stock-to-cash bridge.',
         'Complete accrual additions, cash/noncash acquisition and capitalized-interest allocations, FX/disposal/reclass bridge; no capital-creditor stock change assumed to equal expenditure.',
         'Notes 6/7/9/13 and investing cash-flow captions; original narrow cash-PP&E acceptance preserved.'),
        ('TAX-BASIS','Finalize the reported historical provision, Pretax, accounting ETR, cash taxes and distinct deferred roles. Exclude tax balances from operating-capital proxy; no separate NOL equity addition.',
         'Cash-tax series is a historical cash observation, not a replacement for provision/ETR. Future operating-tax rate is outside Phase 1 and not required to finish these schedules.',
         'Provision 21,795m/32,185m; Pretax 123,627m/165,934m; ETR 17.6296440098%/19.3962659853%; cash tax 28,700m/21,188m. FY2026 deferred CFO 14,189m versus note provision 14,424m remain separate.',
         'Pure NOL DTA allocation and operating-only cash-tax allocation are unavailable but do not invalidate named historical reported points.',
         'Income statements, Note 11 and cash-flow statement; original exact policy/occurrence proofs retained.'),
        ('BALANCE-SCOPE','Exclude identified supplier restrictions from the proposed available-current-financial pool; classify long-term debt/equity/derivative holdings separately as nonoperating investments. Use term carrying values. Propose explicit FY2026 unreported-short-debt zero estimate, never a source zero.',
         'Current-only reported liquidity avoids availability assumptions. Broader pool including long debt securities adds 2,460m/9,108m before restrictions; do not add overlapping strategic/equity-method subsets.',
         'Reported current 94,565m/76,843m; FY2026 known-restriction-excluded 73,043m. Long investment partition 15,405m/36,348m; FY2026 supplier restriction 11,300m=3,800m+7,500m. Face-to-carrying bridges explicitly reconciled.',
         'FY2025 restriction amount, FY2026 restricted-long category, operating reserve, ending CP evidence and exhaustive other claims; no materiality or true unrestricted-cash claim.',
         'Notes 1/4/5/10/11/14 and financing cash flows: current short net0 and long issuance0 do not prove ending CP0.'),
        ('SHARES-AWARDS','Finalize June 30 rounded common shares for historical fiscal-end snapshots, retain exact July cover shares and restricted awards separately. No common-plus-award sum or extra current SBC charge.',
         'Later-dated cover snapshots remain a valid separately dated disclosure; they cannot silently replace the fiscal-end count.',
         'Year-end common 7,434m/7,427m; dated covers 7,433,166,379/7,425,545,491; restricted awards 82m/78m, unrecognized cost21,600m/24,800m.',
         'No remaining source defect for these named historical observations. Complete option economic value and forecast dilution are Phase 2, not historical schedule completion requirements.',
         'Cover, balance sheets, Notes 15/17; source dates, exact class dimensions and rounding retained.'),
    )]


if __name__ == '__main__':
    if '--record-approved-treatment-set' in sys.argv:
        if (ROOT/ACCEPTANCE_PATH).exists():raise SystemExit('Immutable acceptance record already exists')
        filings=[Filing(y) for y in (2025,2026)]
        for f in filings:populate(f)
        print(json.dumps(approval_record(resolve_decisions(filings,finish(filings))),sort_keys=True,indent=2))
        raise SystemExit(0)
    result=build()
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--check' in sys.argv:
        if (ROOT/OUTPUT).read_text()!=text: raise SystemExit('Package replay differs')
        print('Exact two-period package replay passed')
    else: print(text,end='')
