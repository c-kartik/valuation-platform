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
    return activate_msft_history(filings[0],finish_msft_history(filings[0],attach_fy2025_review(filings[0],apply_fy2026_financing(filings[1],apply_fy2026_claim_assumptions(filings[1],apply_fy2026_operations(filings[1],attach_fy2026_attempt(filings[1],accepted_view(resolve_decisions(filings, finish(filings))))))))))


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


def attach_fy2026_attempt(filing,accepted):
    """Add this bounded review after audit verification; never amend its basis.

    No user approval is created. Original proposals and accepted_view remain exact.
    All findings apply only to the selected FY2026 identity and retained bodies.
    """
    if accepted_view({k:v for k,v in accepted.items() if k!='accepted_view'})!=accepted:
        raise ValueError('Changed accepted MSFT view')
    if accepted['periods'][1]['identity']!=dict(cik=789019,accession='0001193125-26-323660',
            form='10-K',annual_start='2025-07-01',annual_end='2026-06-30') or filing.year!=2026:
        raise ValueError('Wrong MSFT completeness-attempt identity')
    if (filing.period.cik,filing.period.accession,str(filing.period.annual_start),str(filing.period.annual_end))!=(789019,'0001193125-26-323660','2025-07-01','2026-06-30'):
        raise ValueError('Wrong retained MSFT filing')
    base=json.loads(json.dumps(accepted));period=base['periods'][1]
    resolution=base['decision_resolution']['periods'][1];view=base['accepted_view']['periods'][1]
    entries={e['input_id']:e for e in period['inputs']}
    # Independent primary + exact instance validation, including all dimensions.
    filing.fact('review_cp_investment','AvailableForSaleSecuritiesDebtSecurities',
        'Note 4: commercial-paper INVESTMENT fair value, not issued borrowing',instant=True,
        dimensions=(('us-gaap:FairValueByAssetClassAxis','us-gaap:DebtSecuritiesMember'),
                    ('us-gaap:FairValueByFairValueHierarchyLevelAxis','us-gaap:FairValueInputsLevel2Member'),
                    ('us-gaap:FinancialInstrumentAxis','us-gaap:CommercialPaperMember')))
    cp=filing.facts['review_cp_investment']
    if cp['value']!='2987000000' or cp['precision']!='-6':raise ValueError('Commercial-paper investment population changed')
    passages=[]
    for marker in ('NOTE 10 — DEBT','The components of long-term debt were as follows:',
        'Cash paid for interest on our debt','Changes in Fair Value Recorded in Other Comprehensive Income Commercial paper',
        'NOTE 17 — EMPLOYEE STOCK AND SAVINGS PLANS','loss carryforwards of',
        'primarily to facilitate the purchase of components'):
        match=re.search(re.escape(marker),filing.text,re.I)
        if match is None:raise ValueError('Required FY2026 review passage absent: '+marker)
        passages.append(dict(source='FY2026-primary',offset=match.start(),
            exact_excerpt=filing.text[max(0,match.start()-70):match.end()+300]))
    # This negative search documents bounded availability, never proves zero.
    lexical={term:len(list(re.finditer(re.escape(term),filing.text,re.I))) for term in
        ('commercial paper','short-term borrowing','short-term debt','noncontrolling','pension','preferred stock')}
    cfo_terms=period['cfo_reconciliation']['terms']
    cfo_sum=sum((Decimal(entries[k]['value']) for k in cfo_terms),Decimal(0))
    if cfo_sum!=Decimal(entries['reported:NetCashProvidedByUsedInOperatingActivities']['value']):
        raise ValueError('FY2026 independent displayed CFO check failed')
    movements=[e for e in period['inputs'] if e['input_id'].startswith('reported:IncreaseDecrease')]
    if len(cfo_terms)!=14 or len(movements)!=9:raise ValueError('FY2026 displayed population changed')
    if view['additional_short_borrowing']['value_usd'] is not None:raise ValueError('Rejected short-debt zero revived')
    def pointer(key):return '/periods/1/inputs/'+str(next(i for i,e in enumerate(period['inputs']) if e['input_id']==key))
    definitions=[
        ('revenue','SATISFIED_ACCEPTED','Reported consolidated sales, no new economic classification.',['revenue']),
        ('ebit','SATISFIED_ACCEPTED','Reported operating income; no CFO-to-EBIT conversion.',['ebit']),
        ('depreciation_amortization','SATISFIED_ACCEPTED_ASSUMPTION','Rounded39000 retains approved finance-amortization-inclusion assumption, not source-confirmed overlap; no ROU add-back.',['expense_da']),
        ('cash_capex','SATISFIED_ACCEPTED_NARROW','Required cash PP&E purchases115948 outflow; no accrual/organic/complete-reinvestment operation.',['reported:PaymentsToAcquirePropertyPlantAndEquipment']),
        ('reported_cash_flow_working_capital_movements','SATISFIED_REPORTED','All nine displayed cash-contribution rows selected as reported, including tax/noncurrent; not operating-only book delta NWC.',[e['input_id'] for e in movements]),
        ('deferred_taxes','SATISFIED_REPORTED','CFO14189 versus deferred provision14424 are separate source roles; no255 plug.',['reported:DeferredIncomeTaxesAndTaxCredits','reported:DeferredIncomeTaxExpenseBenefit']),
        ('stock_based_compensation','SATISFIED_ACCEPTED','Recognized12405 proxy once; linked12405 add-back is not a second cost.',['sbc_cost_proxy','reported:ShareBasedCompensation']),
        ('unclassified_cfo_reconciliation_residual','PENDING_D2_EXCLUSION','No unclassified remainder is populated. Propose no residual scalar where the independently bound fourteen displayed terms reconcile; mixed38534 D&A-and-other row remains unchanged.',['reported:DepreciationAmortizationAndOther']),
        ('reported_cfo','SATISFIED_ACCEPTED','Consolidated182935; independent displayed14-term equality, not organic/unlevered cash.',['reported:NetCashProvidedByUsedInOperatingActivities']),
        ('reported_tax_context','SATISFIED_ACCEPTED','Provision32185, Pretax165934, accounting ETR and cash21188 in distinct roles; no future rate.',['reported:IncomeTaxExpenseBenefit','reported_etr','reported:IncomeTaxesPaidNet']),
        ('cash_investment_components','SATISFIED_ACCEPTED_NAMED','Current restriction-adjusted73043 and separate reported LT investments36348; no unrestricted/excess or reserve calculation.',['current_liquidity','long_investments']),
        ('debt_lease_components','UNSOLVED_ESSENTIAL','Named term40294 + finance66594 =106888 retained; issued CP/additional short borrowing null. Note4 investment2987 cannot fill it.',['term_debt','finance_liability','operating_liability']),
        ('other_equity_bridge_claims_assets','UNSOLVED_ESSENTIAL_AND_PENDING_D3','Reported legal accrual553 and possible additional exposure400 separate; pure NOL DTA and preferred/NCI/pension completeness unestablished.',['loss_credit_dta']),
        ('point_in_time_shares','SATISFIED_ACCEPTED_DATED','June30 common7427m rounded; July23 exact cover7425545491 and nonvested78m separate; no forecast dilution.',['year_end_common','cover_common','nonvested_awards'])]
    checklist=[dict(field=field,status=status,importance='essential_historical',required_operation=why,
        evidence=[pointer(k) for k in keys],existing_view_reference='/accepted_view/periods/1',
        caveat='Status applies only to this named required input, never complete economic coverage.') for field,status,why,keys in definitions]
    dispositions={
        'complete_operating_nwc':('SUPPORTING_DISCLOSURE','Named partial operating capital remains accepted. All nine source cash movements exist; no book movement is substituted. D1 proposes the independently evidenced as-reported path, not complete NWC.'),
        'accrual_ppe_additions_cash_bridge':('SUPPORTING_DISCLOSURE','No accrual-addition operation is performed: required cash purchases and creditor/noncash stocks stay separate. Unknown bridge cannot change cash PP&E.'),
        'all_in_cash_interest':('SUPPORTING_DISCLOSURE','Debt cash1500R and finance interest2547 are retained separately. A total/unlevering operation would need overlap and capitalization evidence; no total is required or approved here.'),
        'operating_only_cash_tax':('PHASE2_OPERATION','Required historical provision/Pretax/ETR/net cash tax are present. Operating tax/tax shield is a different future operation, not a missing reported historical number.'),
        'acquisition_only_cash_purchases':('SUPPORTING_DISCLOSURE','Combined1743 is source-selected and remains unallocated. No acquisition-only/organic subtotal is performed; cannot relabel it acquisition-only.'),
        'discontinued_operations_cash_allocation':('SUPPORTING_DISCLOSURE','Consolidated source identity is retained, not relabeled continuing-only. No affirmative absence of discontinued effects is inferred.'),
        'component_acquisition_fx_reclassification_effects':('SUPPORTING_DISCLOSURE','Reported current-year cash movements do not require deriving cash from two book stocks; bridge required only for organic/comparable/book-to-cash claim, which is not made.'),
        'joint_timing_compatibility':('PHASE2_OPERATION','Joint EBIT/D&A/inventory/tax/lease compatibility remains a required gate before consumption, not resolved by this historical schedule.'),
        'pure_nol_dta':('PENDING_D3_EXCLUSION','Loss-and-credit DTA2124 is combined. Pure NOL has no supported value or allocation; D3 proposes no separate economic NOL asset operation, not a proxy2124 or zero.'),
        'preferred_nci_pension':('UNSOLVED_ESSENTIAL','One retained review finds no affirmative complete recognized-population/absence evidence. Search absence and investment preferred-stock wording cannot supply issuer-claim zeros.'),
        'outstanding_options_and_dilution':('PHASE2_OPERATION','Dated common and disclosed stock awards are present. Award valuation/incremental forecast dilution is a separate operation; complete economic award claim is not certified.'),
        'excess_unrestricted_cash':('PHASE2_OPERATION','73043 is accepted only as current balances less identified restrictions. Reserve/excess-cash valuation is not the selected historical population.'),
        'cfo_to_ebit_compatibility':('PHASE2_OPERATION','Both statements are reported independently; no transformation between them or FCFF is performed.'),
        'commercial_paper':('UNSOLVED_ESSENTIAL','No FY2026 issued CP/short-borrowing balance or explicit absence; net short-debt cash0 is a flow, not an ending balance or bound. Zero proposal stays rejected.')}
    if set(dispositions)!={u['input_id'] for u in period['unresolved_requirements']}:raise ValueError('Unaccounted original FY2026 requirement')
    evidence_routes={
        'complete_operating_nwc':['/accepted_view/periods/1/operating_capital','/periods/1/facts/component_receivables','/decision_resolution/periods/1/additional_facts/customer_finance'],
        'accrual_ppe_additions_cash_bridge':[pointer('reported:PaymentsToAcquirePropertyPlantAndEquipment'),pointer('reported:PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable'),pointer('reported:RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability')],
        'all_in_cash_interest':[pointer('reported:InterestPaid'),pointer('reported:FinanceLeaseInterestPaymentOnLiability'),pointer('reported:InterestExpenseNonoperating')],
        'operating_only_cash_tax':[pointer('reported:IncomeTaxesPaidNet'),pointer('reported:IncomeTaxExpenseBenefit')],
        'acquisition_only_cash_purchases':[pointer('reported:AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets')],
        'discontinued_operations_cash_allocation':['/periods/1/cfo_reconciliation'],
        'component_acquisition_fx_reclassification_effects':['/periods/1/cfo_reconciliation','/decision_resolution/periods/1/schedules/named_expansion'],
        'joint_timing_compatibility':['/accepted_view/periods/1/expense_da','/accepted_view/periods/1/lease_classification'],
        'pure_nol_dta':['/periods/1/facts/loss_credit_dta'],
        'preferred_nci_pension':['/decision_resolution/periods/1/additional_facts/legal_accrual'],
        'outstanding_options_and_dilution':['/accepted_view/periods/1/shares_awards'],
        'excess_unrestricted_cash':['/accepted_view/periods/1/cash'],
        'cfo_to_ebit_compatibility':['/periods/1/cfo_reconciliation',pointer('ebit')],
        'commercial_paper':['/accepted_view/periods/1/additional_short_borrowing','/decision_resolution/periods/1/additional_facts/short_debt_cash_net']}
    remaining=[dict(input_id=u['input_id'],original_reason=u['reason'],evidence=evidence_routes[u['input_id']],
        classification=dispositions[u['input_id']][0],disposition=dispositions[u['input_id']][1],
        original_reference='/periods/1/unresolved_requirements/'+str(i),original_null_preserved=True)
        for i,u in enumerate(period['unresolved_requirements'])]
    decisions=[dict(decision_id=key,status=PROPOSED,accepted=False,recommendation=why,numerical_consequence=effect,
        uncertainty=uncertainty,alternative=alternative) for key,why,effect,uncertainty,alternative in (
        ('D1','Approve the company-specific as-reported historical path: all9 disclosed CF movement rows plus independent14-term CFO control; partial book operating capital remains support, not reconstructed cash delta NWC.',
         'No new numerical value or aggregate. Retain partial capital-18600 and book movement7155 only in their original labels.',
         'Does not remove acquisition/FX/reclassification effects from the reported rows or approve an organic/EBIT cash conversion.',
         'Require complete reconstructed operating capital: matching facilitation obligations/current allocations and book-to-cash bridge remain unavailable, so that alternative stays incomplete.'),
        ('D2','Approve excluding a separately computed unclassified residual scalar for this exact complete displayed reconciliation; retain every mixed source row and its scope.',
         'No zero fill, D&A38534-versus39000 adjustment or residual-defined balance. Existing14-term182935 equality retained.',
         'Does not classify the mixed D&A-and-other contents or prove an economic adjustment.',
         'Require an individually classified remainder: complete mixed-row allocation is not evidenced, so leave the residual requirement unresolved.'),
        ('D3','Approve reporting the combined loss-and-credit DTA as a combined historical disclosure without requiring a standalone pure-NOL economic asset in this historical contract.',
         'Keep2124 combined only; pure NOL value remains null, no allocation/rate/valuation or tax shield.',
         'No supported pure-NOL allocation or uncertainty bound; not an assertion that a pure component is immaterial.',
         'Require pure-NOL asset: no defensible numerical alternative exists in retained evidence; remain incomplete.'))]
    attempt=dict(schema='msft-fy2026-completeness-attempt-v1',version=1,
        baseline='4cd8a48f33e80a1c86e9a3b34607b7413cdbbf4e',identity=period['identity'],
        base_package_revision=digest(relevant(base)),contract_status=PROPOSED,
        purpose='Company-specific consolidated as-reported income/cash movements and named fiscal-end balances/claims/shares; no economic conversion or valuation.',
        checklist=checklist,original_requirement_dispositions=remaining,decisions=decisions,
        supported_resolutions=[
            dict(fix='SOURCE_ROLE_BINDING',finding='Note4 CP2987 is an investment asset, explicitly classed; cannot populate the missing borrowing input.',observation=cp),
            dict(fix='RECONCILIATION_ROLE_BINDING',finding='Nine signed cash movements and all14 displayed terms bound independently; no residual or book reconstruction needed to verify this source equality. FY2026 includes deferred-tax14189 as its own term; FY2025 has13 terms.',
                movement_references=[pointer(e['input_id']) for e in movements],term_references=[pointer(k) for k in cfo_terms],
                sum_usd=str(cfo_sum),reported_cfo_usd=entries['reported:NetCashProvidedByUsedInOperatingActivities']['value']),
            dict(fix='CLAIM_OVERLAP_BINDING',finding='Legal accrual553 is recorded;400 is possible additional loss, not an expected-value liability or another553. No automatic additive claim.',
                references=['/decision_resolution/periods/1/additional_facts/legal_accrual','/decision_resolution/periods/1/additional_facts/legal_additional_exposure'])],
        retained_review=dict(passages=passages,lexical_counts=lexical,
            negative_search_limit='Search counts are availability diagnostics, not proof of zero or no obligation.',
            sources=[s for s in base['sources'] if s['source_id'].startswith('FY2026')]),
        unsolved_essential_inputs=[dict(input_id=k,value=None,reason=dispositions[k][1],
            stopping_condition='Retained scope exhausted once; no numerical proxy/bound is defensible. Remain incomplete unless exact evidence or an independently justified approved alternative is later supplied.')
            for k in ('commercial_paper','preferred_nci_pension')],
        conditional_essential_input=dict(input_id='pure_nol_dta',value=None,depends_on='D3',status='unresolved_under_existing_perimeter'),
        work_record=dict(started_at_utc='2026-10-17T07:38:00+00:00',implementation_checkpoint_at_utc='2026-10-17T07:45:51+00:00',
            observed_checkpoint_elapsed_seconds=471,elapsed_scope='Interactive retained review, reasoning, implementation and initial focused checks through checkpoint; includes tool waits, not professional reviewer labor or a completion SLA.',
            retained_selected_filings_inspected=1,sec_requests=0,
            performed=['Read exact FY2026 retained primary/instance and existing approved inputs; no acquisitions.',
                'Inspect debt/investment/claim/tax/stock-plan passages once for remaining questions; bind CP investment dimensions independently.',
                'Map14 inventory families and14 original null requirements to named operations; verify14 displayed CFO terms and9 movements.',
                'Append proposed decision-ready review only; preserve complete accepted parent and reject stale/tampered sources.'],
            reusable=['Operation-specific requirement classification, not a missing-component count.',
                'Parent-preserving report extension, exact source binding and audit/staleness tests.'],
            no_universe_extrapolation='One unusually well-prepared two-period pilot; no evidence for staffing, other issuers or an all-universe deadline.'),
        source_defaults_changed=False,approvals_added=0,analyst_complete=False,financial_sufficiency='NOT_ASSESSED',
        phase_closed=False,valuation_consumption_approved=False,
        stopping_condition='Stop after this one-period decision-ready attempt. Even approval of D1-D3 does not solve the two essential unknowns or certify completeness.')
    result=json.loads(json.dumps(base));result['fy2026_completeness_attempt']=attempt
    return result


FY2026_OPERATIONS_BASIS='81c6836549109c87e374f3ce0247011134e11ffe'
FY2026_APPROVED_OPERATIONS={
    'D1':'Retain nine reported cash-movement rows and independent14-term CFO reconciliation for historical preparation only; no operating-only cash delta NWC, complete NWC or EBIT-based FCFF readiness.',
    'D2':'No separately computed residual for this fully bound displayed reconciliation; preserve mixed rows, never populate a zero.',
    'D3':'Retain combined loss-and-credit DTA without a separate pure-NOL economic-asset operation; no invented allocation or valuation.'}


def fy2026_operations_record(package):
    """One explicit recording operation; no new sidecar or automatic renewal."""
    if 'fy2026_operation_approval' in package:raise ValueError('Immutable FY2026 operation approval already exists')
    attempt=package['fy2026_completeness_attempt']
    if attempt['identity']['accession']!='0001193125-26-323660':raise ValueError('Wrong operation approval identity')
    record=dict(schema='msft-operation-acceptance-audit-v1',version=1,sequence=2,
        previous=package['accepted_view']['approval_audit']['sha256'],
        action='ACCEPT_OPERATION_REQUIREMENTS',author='User, explicit MSFT FY2026 D1-D3 instruction',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Accept only the three stated operation requirements; preserve original nulls and unrelated population gaps.',
        source_commit=FY2026_OPERATIONS_BASIS,source_revision=digest(relevant(attempt)),
        decisions=FY2026_APPROVED_OPERATIONS.copy(),analyst_completeness_approved=False,
        financial_sufficiency='NOT_ASSESSED',phase_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def review_fy2026_populations(f):
    """Affirmative reported partitions, not a zero-from-absence rule."""
    if (f.period.cik,f.period.accession,str(f.period.annual_start),str(f.period.annual_end))!=(789019,'0001193125-26-323660','2025-07-01','2026-06-30'):
        raise ValueError('Wrong FY2026 population filing')
    specs=[('ap','AccountsPayableCurrent'),('term_current','LongTermDebtCurrent'),
        ('compensation','EmployeeRelatedLiabilitiesCurrent'),('tax_current','AccruedIncomeTaxesCurrent'),
        ('unearned_current','ContractWithCustomerLiabilityCurrent'),('other_current','OtherLiabilitiesCurrent'),
        ('current_total','LiabilitiesCurrent'),('term_long','LongTermDebtNoncurrent'),
        ('tax_long','AccruedIncomeTaxesNoncurrent'),('unearned_long','ContractWithCustomerLiabilityNoncurrent'),
        ('deferred_tax','DeferredIncomeTaxLiabilitiesNet'),('op_lease_long','OperatingLeaseLiabilityNoncurrent'),
        ('other_long','OtherLiabilitiesNoncurrent'),('liabilities','Liabilities'),
        ('common_capital','CommonStocksIncludingAdditionalPaidInCapital'),('retained','RetainedEarningsAccumulatedDeficit'),
        ('oci','AccumulatedOtherComprehensiveIncomeLossNetOfTax'),('equity','StockholdersEquity'),
        ('balance_total','LiabilitiesAndStockholdersEquity'),('assets','Assets')]
    for key,concept in specs:f.fact('population_'+key,concept,'FY2026 consolidated balance-sheet displayed population',instant=True)
    f.fact('population_retirement_cost','DefinedContributionPlanCostRecognized',
        'Note17: employer-funded retirement benefits expensed as contributed; annual expense, not closing funded status')
    obs={key:f.facts['population_'+key] for key,concept in specs}
    obs['retirement_cost']=f.facts['population_retirement_cost']
    checks=[]
    for name,children,parent in [
        ('current_liability_display',['ap','term_current','compensation','tax_current','unearned_current','other_current'],'current_total'),
        ('liability_display',['current_total','term_long','tax_long','unearned_long','deferred_tax','op_lease_long','other_long'],'liabilities'),
        ('equity_display',['common_capital','retained','oci'],'equity'),
        ('balance_display',['liabilities','equity'],'balance_total')]:
        amount=sum((Decimal(obs[k]['value']) for k in children),Decimal(0))
        if amount!=Decimal(obs[parent]['value']):raise ValueError('Reported population partition changed: '+name)
        checks.append(dict(check=name,operands=children,parent=parent,amount_usd=str(amount),result='PASS',
            limit='Complete displayed partition only; not proof that mixed captions contain no embedded obligations.'))
    if obs['balance_total']['value']!=obs['assets']['value']:raise ValueError('Balance-sheet totals differ')
    passages=[]
    for start,end in [('Liabilities and stockholders’ equity Current liabilities:','Refer to accompanying notes.'),
        ('Principles of Consolidation','Recast of Certain Prior Period Information'),
        ('NOTE 10 — DEBT','NOTE 11 — INCOME TAXES'),
        ('NOTE 15 — STOCKHOLDERS’ EQUITY','Share Repurchases'),
        ('Savings Plans We have savings plans','NOTE 18 — SEGMENT INFORMATION AND GEOGRAPHIC DATA')]:
        begin=f.text.find(start);finish=f.text.find(end,begin)
        if begin<0 or finish<begin:raise ValueError('Required population disclosure absent: '+start)
        passages.append(dict(source='FY2026-primary',offset=begin,exact_excerpt=f.text[begin:finish],
            source_body_sha256=f.primary.artifact.sha256))
    common=f.text.find('Common stock and paid-in capital – shares authorized')
    if common<0 or '24,000' not in f.text[common:common+130]:raise ValueError('Common authorization population differs')
    populations=[dict(population=k,value_usd=None,status=status,evidence_reason=reason,non_overlap=overlap,
        resolved=False,proposal=None,uncertainty='No supported numerical bound; no immateriality or zero assumption.')
        for k,status,reason,overlap in (
        ('additional_short_borrowing','NOT_SEPARATELY_REPORTED_POSSIBLE_EMBEDDED',
            'Full current/noncurrent display and term Note10 reviewed. No separately displayed issued CP/short debt; other current26738 and other long65117 remain mixed. Term40294 is not all-borrowing coverage; net borrowing cash0 is not ending0. Investment CP2987 is an asset.',
            'Retain named term+finance106888. Do not add current9227 again or reuse asset CP; no complete debt amount.'),
        ('preferred_equity','NOT_SEPARATELY_PRESENTED_ISSUANCE_UNPROVED',
            'Common capital117406 + retained328265 + OCI(-3284) exhausts displayed equity442387; Note15 describes common share roll-forward. Authorized24000m is COMMON shares, not outstanding preferred. This proves presentation, not a separate affirmative outstanding-preferred zero.',
            'No extra preferred deduction or balance selected; no subtraction from already selected common/financial balances.'),
        ('noncontrolling_interests','NOT_SEPARATELY_PRESENTED_EMBEDDED_COVERAGE_UNPROVED',
            'Note1 includes Microsoft and subsidiaries, eliminating intercompany balances. Balance/equity statements and Note15 have no separately identified NCI population. Full equity partition is affirmative displayed coverage, not proof an embedded NCI amount is zero.',
            'No residual equity deduction or invented NCI. Do not assign any part of common capital/retained earnings to NCI.'),
        ('pension_funded_status','NO_SEPARATE_FUNDED_STATUS_DISCLOSURE',
            'Note17 describes US401(k) and international savings plans;1800R employer-funded retirement benefits for all plans expensed as contributed. No funded-status/benefit-obligation/plan-asset bridge identifies a separate recognized pension balance or its location in mixed liabilities.',
            'Retirement expense1800R is not pension debt, plan assets, contributions payable or a new adjustment. Do not add expense to66594 finance leases or other liabilities.'))]
    return dict(schema='msft-fy2026-recognized-population-review-v1',observations=obs,checks=checks,
        passages=passages,populations=populations,new_document_count=0,new_requests=0,
        acquisition_disposition='Exact selected official annual primary/instance already retained. No precise additional official document was established that answers these June30 outstanding/embedded/funded-status questions; duplicate IR annual, authorization-only exhibits or other-date balances would not supply that missing evidence. No speculative acquisition.',
        stopping_condition='Stop this fixed pass: presentation scope clarified, amounts unresolved. Reopen only for exact FY2026-end issued/embedded balance or plan funded-status evidence, or a specifically justified proposal; no automatic acquisition/research cycle.')


def apply_fy2026_operations(filing,package):
    if (filing.period.cik,filing.period.accession,str(filing.period.annual_start),str(filing.period.annual_end))!=(789019,'0001193125-26-323660','2025-07-01','2026-06-30'):
        raise ValueError('Wrong FY2026 operation filing')
    parent={k:v for k,v in package.items() if k not in ('fy2026_completeness_attempt','fy2026_operation_approval','fy2026_operations_view','fy2026_claim_assumption_approval','fy2026_claim_assumptions_view','fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review','fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
    if package['fy2026_completeness_attempt']['base_package_revision']!=digest(relevant(parent)):
        raise ValueError('Stale FY2026 parent package')
    if accepted_view({k:v for k,v in parent.items() if k!='accepted_view'})!=parent:
        raise ValueError('Changed original accepted parent')
    saved=_json((ROOT/OUTPUT).read_text())
    record=saved['fy2026_operation_approval']
    expected={'schema','version','sequence','previous','action','author','recorded_at_utc','rationale','source_commit',
        'source_revision','decisions','analyst_completeness_approved','financial_sufficiency','phase_closed','valuation_consumption_approved','sha256'}
    if type(record) is not dict or set(record)!=expected or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed FY2026 operation audit')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    if (record['schema']!='msft-operation-acceptance-audit-v1' or type(record['version']) is not int or record['version']!=1
        or type(record['sequence']) is not int or record['sequence']!=2 or record['previous']!=package['accepted_view']['approval_audit']['sha256']
        or record['action']!='ACCEPT_OPERATION_REQUIREMENTS' or record['source_commit']!=FY2026_OPERATIONS_BASIS
        or record['decisions']!=FY2026_APPROVED_OPERATIONS or record['analyst_completeness_approved'] is not False
        or record['financial_sufficiency']!='NOT_ASSESSED' or record['phase_closed'] is not False or record['valuation_consumption_approved'] is not False):
        raise ValueError('Unregistered FY2026 operation scope')
    if record['source_revision']!=digest(relevant(package['fy2026_completeness_attempt'])):raise ValueError('Stale FY2026 operation approval; explicit revalidation required')
    result=json.loads(json.dumps(package));result['fy2026_operation_approval']=record
    result['fy2026_operations_view']=dict(schema='msft-fy2026-approved-operations-view-v1',version=1,
        identity=package['fy2026_completeness_attempt']['identity'],audit_sha256=record['sha256'],
        operation_requirements=[dict(decision_id=k,status=APPROVED_SCOPE,scope=v,
            source_reference='/fy2026_completeness_attempt/decisions/'+str(i)) for i,(k,v) in enumerate(FY2026_APPROVED_OPERATIONS.items())],
        residual=dict(operation='excluded_for_fully_bound_display_only',value=None,zero_populated=False),
        pure_nol=dict(operation='no_separate_economic_asset',value=None,combined_dta_reference='/periods/1/facts/loss_credit_dta'),
        requirement_overlays=[dict(source_reference='/fy2026_completeness_attempt/conditional_essential_input',
            decision_id='D3',operation_requirement='SATISFIED_BY_APPROVED_EXCLUSION',original_value=None),
            dict(field='unclassified_cfo_reconciliation_residual',decision_id='D2',
                operation_requirement='SATISFIED_BY_APPROVED_EXCLUSION',original_value=None),
            dict(field='reported_cash_flow_working_capital_movements',decision_id='D1',
                operation_requirement='ACCEPTED_AS_REPORTED_ONLY',book_or_operating_only_cash_delta=False)],
        original_nulls_preserved=True,book_delta_is_cash_delta=False,unrelated_requirements_waived=False,
        population_review=review_fy2026_populations(filing),analyst_complete=False,financial_sufficiency='NOT_ASSESSED',
        phase_closed=False,valuation_consumption_approved=False)
    return result


FY2026_CLAIMS_BASIS='a681803387f54bd690f2c61476662104ef4c83c6'
FY2026_APPROVED_CLAIM_ASSUMPTIONS={
    'preferred_equity':'No additional preferred-equity adjustment selected, relying on reviewed common-equity presentation.',
    'noncontrolling_interests':'No additional NCI adjustment selected, relying on reviewed consolidated-equity presentation.',
    'pension_funded_status':'Retain disclosed retirement expense without a separate pension adjustment, acknowledging incomplete coverage of international arrangements.'}


def fy2026_claim_assumption_record(package):
    """Explicit user authorization, appended to the existing embedded audit chain."""
    if 'fy2026_claim_assumption_approval' in package:raise ValueError('Immutable claim approval already exists')
    record=dict(schema='msft-operation-acceptance-audit-v1',version=1,sequence=3,
        previous=package['fy2026_operation_approval']['sha256'],action='ACCEPT_ANALYST_ASSUMPTIONS',
        author='User, explicit MSFT FY2026 preferred-equity/NCI/retirement instruction',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Approve only the three named analyst assumptions; preserve reported nulls, unbounded omitted-claim risk and unresolved additional short borrowing.',
        source_commit=FY2026_CLAIMS_BASIS,source_revision=digest(relevant(package)),
        decisions=FY2026_APPROVED_CLAIM_ASSUMPTIONS.copy(),analyst_completeness_approved=False,
        financial_sufficiency='NOT_ASSESSED',phase_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def apply_fy2026_claim_assumptions(filing,package):
    """No numerical override: requirements addressed by approved analyst judgments."""
    if (filing.period.cik,filing.period.accession,str(filing.period.annual_start),str(filing.period.annual_end))!=(789019,'0001193125-26-323660','2025-07-01','2026-06-30'):
        raise ValueError('Wrong FY2026 claim filing')
    parent={k:v for k,v in package.items() if k not in ('fy2026_claim_assumption_approval','fy2026_claim_assumptions_view','fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review','fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
    # Replay the already-approved operations and source review, not a stale saved view.
    if apply_fy2026_operations(filing,parent)!=parent:raise ValueError('Changed operation/source view')
    record=_json((ROOT/OUTPUT).read_text())['fy2026_claim_assumption_approval']
    expected=set(parent['fy2026_operation_approval'])
    if type(record) is not dict or set(record)!=expected or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed claim audit')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    if (record['schema']!='msft-operation-acceptance-audit-v1' or type(record['version']) is not int or record['version']!=1
        or type(record['sequence']) is not int or record['sequence']!=3 or record['previous']!=parent['fy2026_operation_approval']['sha256']
        or record['action']!='ACCEPT_ANALYST_ASSUMPTIONS' or record['source_commit']!=FY2026_CLAIMS_BASIS
        or record['decisions']!=FY2026_APPROVED_CLAIM_ASSUMPTIONS or record['analyst_completeness_approved'] is not False
        or record['financial_sufficiency']!='NOT_ASSESSED' or record['phase_closed'] is not False or record['valuation_consumption_approved'] is not False):
        raise ValueError('Unregistered claim assumption scope')
    if record['source_revision']!=digest(relevant(parent)):raise ValueError('Stale claim approval; explicit revalidation required')
    rows=[]
    for i,source in enumerate(parent['fy2026_operations_view']['population_review']['populations']):
        population=source['population']
        if population not in FY2026_APPROVED_CLAIM_ASSUMPTIONS:continue
        rows.append(dict(population=population,origin='analyst_assumption',status='ADDRESSED_BY_APPROVED_ASSUMPTION',
            treatment=record['decisions'][population],source_value=None,adjustment_value=None,reported_zero=False,
            immateriality_finding=False,source_gap_resolved=False,
            evidence_reference='/fy2026_operations_view/population_review/populations/'+str(i),
            rationale=source['evidence_reason'],non_overlap=source['non_overlap'],
            economic_consequence='No incremental adjustment economically omits a potentially undisclosed claim; not proof of zero.',
            uncertainty='Potential omitted amount is not bounded by available evidence; international retirement coverage remains incomplete.' if population=='pension_funded_status' else 'Potential omitted amount is not bounded by available evidence.'))
    if {r['population'] for r in rows}!=set(FY2026_APPROVED_CLAIM_ASSUMPTIONS):raise ValueError('Incomplete claim evidence')
    result=json.loads(json.dumps(parent));result['fy2026_claim_assumption_approval']=record
    result['fy2026_claim_assumptions_view']=dict(version=1,identity=parent['fy2026_operations_view']['identity'],
        audit_sha256=record['sha256'],assumptions=rows,
        addressed_requirement_reference='/fy2026_completeness_attempt/unsolved_essential_inputs/1',
        remaining_essential_inputs=[parent['fy2026_completeness_attempt']['unsolved_essential_inputs'][0]],
        additional_short_borrowing_reference='/accepted_view/periods/1/additional_short_borrowing',
        short_debt_zero_status='REJECTED_NOT_SELECTED',named_debt_subtotal_complete=False,
        original_nulls_preserved=True,unrelated_requirements_waived=False,
        analyst_complete=False,financial_sufficiency='NOT_ASSESSED',phase_closed=False,valuation_consumption_approved=False)
    return result


FY2026_FINANCING_BASIS='43027e15d3c459fdb8871f5809b5d56bdc279db8'
FY2026_FINANCING_DECISION='Select106888 USDm named term-debt-plus-finance-lease financing input with no additional short-borrowing adjustment. Analyst assumption, not reported zero, complete debt or immateriality; omitted borrowing remains unquantified.'


def fy2026_financing_record(package):
    if 'fy2026_financing_approval' in package:raise ValueError('Immutable financing approval already exists')
    record=dict(schema='msft-operation-acceptance-audit-v1',version=1,sequence=4,
        previous=package['fy2026_claim_assumption_approval']['sha256'],action='ACCEPT_FINANCING_ASSUMPTION',
        author='User, explicit MSFT FY2026 financing assumption and supersession instruction',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Explicitly supersede the rejected no-additional-borrowing adjustment while preserving its history and source null; accept unquantified omitted-borrowing risk for this named financing input only.',
        source_commit=FY2026_FINANCING_BASIS,source_revision=digest(relevant(package)),
        identity=package['fy2026_claim_assumptions_view']['identity'],
        decisions={'financing':FY2026_FINANCING_DECISION},
        supersedes=['/accepted_view/short_debt_zero_proposal_status','/fy2026_claim_assumptions_view/short_debt_zero_status'],
        evidence_references=['/accepted_view/periods/1/borrowings','/accepted_view/periods/1/additional_short_borrowing',
            '/fy2026_operations_view/population_review/populations/0',
            'docs/company-data-preparation/MSFT-analyst-input-package.md#current-bounded-short-borrowing-bridge-review--unresolved'],
        analyst_completeness_approved=False,financial_sufficiency='NOT_ASSESSED',phase_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def apply_fy2026_financing(filing,package):
    parent={k:v for k,v in package.items() if k not in ('fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review','fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
    if apply_fy2026_claim_assumptions(filing,parent)!=parent:raise ValueError('Changed claim/source view')
    record=_json((ROOT/OUTPUT).read_text())['fy2026_financing_approval']
    expected=fy2026_financing_record(parent)
    if type(record) is not dict or set(record)!=set(expected) or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed financing audit')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    for key in set(expected)-{'sha256','recorded_at_utc','source_revision'}:
        if type(record[key]) is not type(expected[key]) or record[key]!=expected[key]:raise ValueError('Unregistered financing scope: '+key)
    if record['source_revision']!=expected['source_revision']:raise ValueError('Stale financing approval; explicit revalidation required')
    selected=parent['accepted_view']['periods'][1]['borrowings']['selected']
    if selected['value_usd']!='106888000000' or selected['terms']!=[dict(coefficient=1,operand='term_debt_parent'),dict(coefficient=1,operand='finance_liability')]:raise ValueError('Changed named financing population')
    if parent['accepted_view']['periods'][1]['additional_short_borrowing']['value_usd'] is not None:raise ValueError('Source short borrowing must remain null')
    # Reassess the existing fourteen rows; do not invent new requirements or drop one.
    statuses={
        'revenue':'SATISFIED_ACCEPTED','ebit':'SATISFIED_ACCEPTED','depreciation_amortization':'SATISFIED_ACCEPTED_ASSUMPTION',
        'cash_capex':'SATISFIED_ACCEPTED_NARROW','reported_cash_flow_working_capital_movements':'SATISFIED_REPORTED',
        'deferred_taxes':'SATISFIED_REPORTED','stock_based_compensation':'SATISFIED_ACCEPTED',
        'unclassified_cfo_reconciliation_residual':'PENDING_D2_EXCLUSION','reported_cfo':'SATISFIED_ACCEPTED',
        'reported_tax_context':'SATISFIED_ACCEPTED','cash_investment_components':'SATISFIED_ACCEPTED_NAMED',
        'debt_lease_components':'UNSOLVED_ESSENTIAL','other_equity_bridge_claims_assets':'UNSOLVED_ESSENTIAL_AND_PENDING_D3',
        'point_in_time_shares':'SATISFIED_ACCEPTED_DATED'}
    original=parent['fy2026_completeness_attempt']['checklist']
    if len(original)!=14 or {r['field']:r['status'] for r in original}!=statuses:raise ValueError('Changed existing completeness checklist')
    rows=[]
    for i,row in enumerate(original):
        field=row['field'];status='SATISFIED_WITHIN_ACCEPTED_SCOPE';basis='Existing verified source selection and accepted historical scope'
        references=[f'/fy2026_completeness_attempt/checklist/{i}']+row['evidence']
        if field=='depreciation_amortization':status='SATISFIED_BY_APPROVED_ASSUMPTION';basis='Existing rounded39000 D&A; unproved finance-amortization inclusion assumption preserved'
        if field=='reported_cash_flow_working_capital_movements':references+=['/fy2026_operation_approval/decisions/D1'];basis='D1 accepts nine reported rows, not operating-only cash delta NWC'
        if field=='unclassified_cfo_reconciliation_residual':status='SATISFIED_BY_APPROVED_EXCLUSION';references+=['/fy2026_operation_approval/decisions/D2'];basis='D2: no separate residual for independently bound14-term display; no zero'
        if field=='debt_lease_components':status='SATISFIED_BY_APPROVED_ASSUMPTION';references+=['/fy2026_financing_approval'];basis=FY2026_FINANCING_DECISION
        if field=='other_equity_bridge_claims_assets':status='SATISFIED_BY_APPROVED_ASSUMPTIONS_AND_EXCLUSION';references+=['/fy2026_claim_assumptions_view','/fy2026_operation_approval/decisions/D3'];basis='Approved preferred/NCI/retirement assumptions; D3 excludes separate pure-NOL operation; legal accrual/exposure stay separate'
        rows.append(dict(field=field,status=status,basis=basis,evidence_references=references))
    result=json.loads(json.dumps(parent));result['fy2026_financing_approval']=record
    result['fy2026_analyst_checklist']=dict(version=1,identity=record['identity'],audit_sha256=record['sha256'],
        perimeter='Existing MSFT FY2026 consolidated as-reported historical income/cash movements and named financial populations, with explicitly approved classifications, assumptions and exclusions; not complete generic field totals.',
        financing=dict(value_usd=selected['value_usd'],value_millions=selected['value_millions'],unit='USD',
            label='Selected analyst financing: named term-debt-plus-finance-lease subtotal',origin='analyst_assumption',
            precision=selected['precision'],source_reference='/accepted_view/periods/1/borrowings',
            additional_adjustment='No additional short-borrowing adjustment selected',source_additional_short_borrowing=None,
            complete_debt=False,reported_zero=False,immateriality_finding=False,omitted_borrowing='Unquantified; no supported bound',
            supersession='Prior rejected adjustment knowingly superseded by sequence4; original rejection and failed-bridge reviews remain history'),
        checklist=rows,remaining_essential_inputs=[],analyst_complete=True,
        financial_sufficiency='SATISFIED_ONLY_FOR_THIS_APPROVED_HISTORICAL_PERIMETER',
        complete_issuer_history=False,whole_universe_closed=False,phase_closed=False,valuation_consumption_approved=False,
        original_nulls_preserved=True,supporting_and_phase2_requirements_reference='/fy2026_completeness_attempt/original_requirement_dispositions')
    return result


def attach_fy2025_review(filing,package):
    """One proposal-only FY2025 review; FY2026 authority is not transferred."""
    base={k:v for k,v in package.items() if k!='fy2025_completeness_review'}
    period=base['periods'][0];view=base['accepted_view']['periods'][0]
    identity=dict(cik=789019,accession='0000950170-25-100235',form='10-K',annual_start='2024-07-01',annual_end='2025-06-30')
    if period['identity']!=identity or (filing.period.cik,filing.period.accession,str(filing.period.annual_start),str(filing.period.annual_end))!=(789019,identity['accession'],identity['annual_start'],identity['annual_end']):raise ValueError('Wrong FY2025 review filing')
    entries={e['input_id']:e for e in period['inputs']}
    terms=period['cfo_reconciliation']['terms'];movements=[e for e in period['inputs'] if e['input_id'].startswith('reported:IncreaseDecrease')]
    if len(terms)!=14 or len(movements)!=9 or sum((Decimal(entries[k]['value']) for k in terms),Decimal(0))!=Decimal(entries['reported:NetCashProvidedByUsedInOperatingActivities']['value']):raise ValueError('FY2025 displayed reconciliation changed')
    observations={}
    for key,concept,instant in [('current_liabilities','LiabilitiesCurrent',True),('liabilities','Liabilities',True),
        ('equity','StockholdersEquity',True),('common_capital','CommonStocksIncludingAdditionalPaidInCapital',True),
        ('retained','RetainedEarningsAccumulatedDeficit',True),('oci','AccumulatedOtherComprehensiveIncomeLossNetOfTax',True),
        ('balance_total','LiabilitiesAndStockholdersEquity',True),('retirement_cost','DefinedContributionPlanCostRecognized',False)]:
        filing.fact('fy2025_review_'+key,concept,'FY2025 consolidated presentation / Note17 annual retirement expense',instant=instant)
        observations[key]=filing.facts['fy2025_review_'+key]
    if sum((Decimal(observations[k]['value']) for k in ('common_capital','retained','oci')),Decimal(0))!=Decimal(observations['equity']['value']):raise ValueError('FY2025 equity partition differs')
    if Decimal(observations['liabilities']['value'])+Decimal(observations['equity']['value'])!=Decimal(observations['balance_total']['value']):raise ValueError('FY2025 balance partition differs')
    passages=[]
    for start,end in [('CASH FLOWS','Refer to accompanying notes.'),('Principles of Consolidation','Recast of Certain Prior Period Information'),
        ('NOTE 10 — DEBT','NOTE 11'),('NOTE 15 — STOCKHOLDERS','Share Repurchases'),('Savings Plans We have savings plans','NOTE 18')]:
        a=filing.text.find(start);b=filing.text.find(end,a+len(start))
        if a<0 or b<a:raise ValueError('Required FY2025 disclosure absent: '+start)
        passages.append(dict(source='FY2025-primary',offset=a,exact_excerpt=filing.text[a:b],source_body_sha256=filing.primary.artifact.sha256))
    def pointer(key):return '/periods/0/inputs/'+str(next(i for i,e in enumerate(period['inputs']) if e['input_id']==key))
    definitions=[
        ('revenue','SATISFIED_ACCEPTED',['revenue'],[]),('ebit','SATISFIED_ACCEPTED',['ebit'],[]),
        ('depreciation_amortization','SATISFIED_APPROVED_ASSUMPTION',['expense_da'],[]),
        ('cash_capex','SATISFIED_ACCEPTED_NARROW',['reported:PaymentsToAcquirePropertyPlantAndEquipment'],[]),
        ('reported_cash_flow_working_capital_movements','PENDING_APPROVAL',[e['input_id'] for e in movements],['25-D1']),
        ('deferred_taxes','SATISFIED_REPORTED',['reported:DeferredIncomeTaxExpenseBenefit'],[]),
        ('stock_based_compensation','SATISFIED_ACCEPTED',['sbc_cost_proxy','reported:ShareBasedCompensation'],[]),
        ('unclassified_cfo_reconciliation_residual','PENDING_APPROVAL',['reported:DepreciationAmortizationAndOther'],['25-D2']),
        ('reported_cfo','SATISFIED_ACCEPTED',['reported:NetCashProvidedByUsedInOperatingActivities'],[]),
        ('reported_tax_context','SATISFIED_ACCEPTED',['reported:IncomeTaxExpenseBenefit','reported_etr','reported:IncomeTaxesPaidNet'],[]),
        ('cash_investment_components','SATISFIED_ACCEPTED_NAMED',['current_liquidity','long_investments'],[]),
        ('debt_lease_components','PENDING_APPROVAL',['disclosed_borrowings','finance_liability'],['25-D7']),
        ('other_equity_bridge_claims_assets','PENDING_APPROVAL',['loss_credit_dta'],['25-D3','25-D4','25-D5','25-D6']),
        ('point_in_time_shares','SATISFIED_ACCEPTED_DATED',['year_end_common','cover_common','nonvested_awards'],[])]
    checklist=[dict(field=field,status=status,evidence_references=[pointer(k) for k in keys],
        existing_approval_reference='/accepted_view/periods/0',pending_decisions=decisions) for field,status,keys,decisions in definitions]
    proposals=[dict(decision_id=k,status=PROPOSED,accepted=False,recommendation=treatment,numerical_consequence=effect,
        evidence_references=refs,uncertainty=risk,alternative=alternative)
        for k,treatment,effect,refs,risk,alternative in [
        ('25-D1','Use nine reported CF movement rows and independently bound14-term CFO control; retain partial book capital as support, not cash delta NWC.',
         'Retain reported CFO136162 and nine signed rows; partial operating capital-25755 stays partial, no new total.',
         ['/periods/0/cfo_reconciliation','/accepted_view/periods/0/operating_capital'],
         'Consolidated tax/noncurrent/acquisition/FX effects not removed; no EBIT/organic compatibility.',
         'A complete reconstructed book-to-cash operating-capital bridge remains unavailable; do not substitute book movement.'),
        ('25-D2','No separately computed residual for this independently bound display; preserve the mixed D&A-and-other row.',
         'No residual value or zero; mixed34153 remains distinct from rounded expense D&A28000; no6153 adjustment.',
         [pointer('reported:DepreciationAmortizationAndOther'),'/periods/0/cfo_reconciliation'],
         'Mixed row is not pure D&A or an economic adjustment.', 'Keep residual requirement unresolved instead; do not manufacture a balancing item.'),
        ('25-D3','Retain combined loss-and-credit DTA without a separate pure-NOL economic-asset operation.',
         'Retain2114 combined DTA; pure-NOL allocation stays null, no benefit value or zero.',
         ['/periods/0/facts/loss_credit_dta'], 'Credits/losses not separated; no pure-NOL value or economic benefit established.',
         'Separate pure-NOL operation remains unsupported; combined2114 cannot serve as pure NOL.'),
        ('25-D4','No additional preferred-equity adjustment, relying on reviewed FY2025 common-equity presentation.',
         'No additional adjustment proposed; source preferred amount remains unavailable, not reported zero.',
         ['/fy2025_completeness_review/observations/equity','/fy2025_completeness_review/passages/3'],
         'Economically omits potentially undisclosed claim of unbounded amount; no immateriality finding.',
         'Require exact outstanding preferred claim or approved estimate; no defensible numeric estimate is disclosed.'),
        ('25-D5','No additional NCI adjustment, relying on reviewed FY2025 consolidated-equity presentation.',
         'No additional adjustment proposed; NCI amount remains unavailable.',
         ['/fy2025_completeness_review/observations/equity','/fy2025_completeness_review/passages/1'],
         'Economically omits potentially undisclosed minority claim; amount unbounded, no ownership-by-ownership absence proof.',
         'Keep essential claim operation unresolved pending quantified ownership/claim evidence, not an invented residual.'),
        ('25-D6','Retain disclosed FY2025 retirement expense without separate pension adjustment, acknowledging incomplete international-plan coverage.',
         'Retain1800 rounded expense; funded-status amount remains null; no extra charge/debt.',
         ['/fy2025_completeness_review/observations/retirement_cost','/fy2025_completeness_review/passages/4'],
         'Potential undisclosed funded obligation/surplus unbounded; contribution expense is not closing pension debt.',
         'Require recognized funded-status/plan-assets bridge for a separate pension operation; no available estimate.'),
        ('25-D7','Select named89323 term-debt-plus-finance-lease financing with no adjustment for additional borrowing beyond the expressly reported CP zero.',
         'Retain43151 term+46172 finance=89323; CP0 source-confirmed only. Broader short borrowing remains unquantified.',
         ['/accepted_view/periods/0/borrowings','/periods/0/facts/commercial_paper','/fy2025_completeness_review/passages/2'],
         'No adjustment economically omits potentially undisclosed other short borrowing; no supported bound or complete-debt assertion. Current term2999 already included; CP investment assets excluded.',
         'Require quantified broader short borrowing or an independently justified estimate; CP0 alone cannot establish that total.')]]
    supporting={'complete_operating_nwc','accrual_ppe_additions_cash_bridge','all_in_cash_interest','acquisition_only_cash_purchases','discontinued_operations_cash_allocation','component_acquisition_fx_reclassification_effects'}
    future={'operating_only_cash_tax','joint_timing_compatibility','outstanding_options_and_dilution','excess_unrestricted_cash','cfo_to_ebit_compatibility'}
    expected_nulls=supporting|future|{'DeferredIncomeTaxesAndTaxCredits','pure_nol_dta','preferred_nci_pension'}
    if {u['input_id'] for u in period['unresolved_requirements']}!=expected_nulls:raise ValueError('Unaccounted FY2025 original requirement')
    dispositions=[dict(input_id=u['input_id'],original_reference='/periods/0/unresolved_requirements/'+str(i),original_null_preserved=True,
        classification='SUPPORTING_UNDER_PROPOSED_D1' if u['input_id'] in supporting else 'PHASE2_OPERATION' if u['input_id'] in future else
            'USE_REPORTED_FY2025_DEFERRED_TAX_ROLE_NOT_UNREPORTED_FY2026_CONCEPT' if u['input_id']=='DeferredIncomeTaxesAndTaxCredits' else 'PENDING_CONSOLIDATED_APPROVAL')
        for i,u in enumerate(period['unresolved_requirements'])]
    result=json.loads(json.dumps(base));result['fy2025_completeness_review']=dict(version=1,identity=identity,
        basis_commit='2d62dbc38810bb54864ac207bc81fdf0b3b03795',parent_revision=digest(relevant(base)),
        review_status='PENDING_CONSOLIDATED_USER_APPROVAL',financial_approvals_added=0,observations=observations,passages=passages,
        checklist=checklist,satisfied_families=10,pending_families=4,decisions=proposals,original_requirement_dispositions=dispositions,
        cfo_control=dict(terms_reference='/periods/0/cfo_reconciliation',term_count=14,adjustments_excluding_net_income=13,
            amount_usd=str(sum((Decimal(entries[k]['value']) for k in terms),Decimal(0))),independently_bound=True,
            correction='Earlier prose FY2025 has13 means adjustments, not terms including net income;14 displayed terms tie. Original numerical data unchanged.'),
        cp_scope=dict(source_reference='/periods/0/facts/commercial_paper',reported_cp_usd='0',broader_short_borrowing_usd=None,
            historical_label_limitation='Existing additional_short_borrowing reported0 field is supported ONLY as CP; do not read its historical broad label as an all-short-borrowing fact.'),
        essential_requirements_pending=['reported_movement_perimeter','separate_residual_exclusion','pure_nol_operation','preferred_nci_pension_adjustments','broader_borrowing_treatment'],
        no_defensible_numerical_estimate_for_missing_claims=True,analyst_complete=False,financial_sufficiency='PENDING_APPROVAL_FOR_PROPOSED_HISTORICAL_PERIMETER',
        original_nulls_preserved=True,fy2026_authority_transferred=False,phase_closed=False,valuation_consumption_approved=False,
        stopping_condition='Stop for all seven FY2025 decisions together; no automatic next memo, research or company. FY2026 approvals do not apply.')
    return result


def fy2025_acceptance_record(package):
    if 'fy2025_approval' in package:raise ValueError('Immutable FY2025 approval already exists')
    review=package['fy2025_completeness_review']
    record=dict(schema='msft-operation-acceptance-audit-v1',version=1,sequence=5,
        previous=package['fy2026_financing_approval']['sha256'],action='ACCEPT_FY2025_DECISIONS',
        author='User, explicit approval of FY2025 decisions25-D1 through25-D7 exactly as proposed',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),rationale='Accept only the seven exact FY2025 proposals, including89323 USDm named financing/no additional borrowing adjustment; preserve source unknowns and unbounded omitted claims.',
        source_commit='b170bb16128f12b5558d578a08341cd9129e3882',source_revision=digest(relevant(package)),identity=review['identity'],
        decisions={r['decision_id']:{k:v for k,v in r.items() if k not in ('decision_id','status','accepted')} for r in review['decisions']},
        financial_sufficiency='NOT_ASSESSED_OUTSIDE_APPROVED_HISTORICAL_PERIMETER',phase_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def review_msft_remaining(manifest):
    """The three older frozen filings, not new registrations or financial approvals."""
    artifact_path='docs/evidence/analyst-operating-nwc-response-bodies.json'
    doc=_json((ROOT/artifact_path).read_text());rows=[]
    for selected in manifest:
        identity=selected['identity'];year=int(identity['annual_end'][:4])
        if year>=2025:continue
        refs=[(i,a) for i,a in enumerate(doc['artifacts']) if a['accession']==identity['accession']]
        exceptions=[];receipts=[]
        for i,a in refs:
            body=cash.gzip.decompress(cash.base64.b64decode(a['response_body_gzip_base64'],validate=True))
            receipts.append(cash._receipt(a,body))
        primaries=[r for r in receipts if r.artifact.url.endswith('.htm')];instances=[r for r in receipts if r.artifact.url.endswith('_htm.xml')]
        if len(primaries)!=1 or len(instances)!=1:raise ValueError('Exact older primary/instance pair unavailable')
        f=Filing.__new__(Filing);f.year=year
        f.period=cash.Period(identity['cik'],identity['accession'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']))
        f.primary=primaries[0];f.instance=instances[0];f.root,f.contexts,f.units,f.namespaces=cash._instance(tuple(receipts),f.period)
        f.inline=InlineFacts();f.inline.feed(f.primary.artifact.body.decode());f.text=re.sub(r'\s+',' ',' '.join(f.inline.text));f.facts={};f.entries=[]
        specs=[('revenue','RevenueFromContractWithCustomerExcludingAssessedTax',False),('ebit','OperatingIncomeLoss',False),
            ('cfo','NetCashProvidedByUsedInOperatingActivities',False),('depreciation','Depreciation',False),('amortization','AmortizationOfIntangibleAssets',False),
            ('capex','PaymentsToAcquirePropertyPlantAndEquipment',False),('sbc_expense','AllocatedShareBasedCompensationExpense',False),
            ('provision','IncomeTaxExpenseBenefit',False),('pretax','IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',False),
            ('cash_taxes','IncomeTaxesPaidNet',False),('cash','CashAndCashEquivalentsAtCarryingValue',True),('current_investments','ShortTermInvestments',True),
            ('current_financial_parent','CashCashEquivalentsAndShortTermInvestments',True),('long_investments','LongTermInvestments',True),
            ('term_debt','LongTermDebt',True),('current_term','LongTermDebtCurrent',True),('noncurrent_term','LongTermDebtNoncurrent',True),
            ('commercial_paper','CommercialPaper',True),('finance_liability','FinanceLeaseLiability',True),('operating_liability','OperatingLeaseLiability',True),
            ('retirement_expense','DefinedContributionPlanCostRecognized',False),('common','CommonStockSharesOutstanding',True),
            ('equity','StockholdersEquity',True),('common_capital','CommonStocksIncludingAdditionalPaidInCapital',True),('retained','RetainedEarningsAccumulatedDeficit',True),
            ('oci','AccumulatedOtherComprehensiveIncomeLossNetOfTax',True),('liabilities','Liabilities',True),('balance_total','LiabilitiesAndStockholdersEquity',True),
            ('acquisition_combined','AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets',False),
            ('capital_creditors','PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable',True),
            ('finance_additions','RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability',False),('finance_principal','FinanceLeasePrincipalPayments',False),
            ('operating_payments','OperatingLeasePayments',False),('finance_interest_cash','FinanceLeaseInterestPaymentOnLiability',False),
            ('finance_amortization','FinanceLeaseRightOfUseAssetAmortization',False),('operating_cost','OperatingLeaseCost',False),
            ('borrowing_interest_cash','InterestPaid',False),('interest_expense','InterestExpense',False),
            ('debt_face','DebtInstrumentCarryingAmount',True),('debt_fair','LongTermDebtFairValue',True),
            ('legal_accrual','LossContingencyAccrualAtCarryingValue',True),('legal_additional_exposure','LossContingencyRangeOfPossibleLossPortionNotAccrued',True),
            ('equity_method','EquityMethodInvestments',True),('nonmarketable','EquitySecuritiesWithoutReadilyDeterminableFairValueAmount',True)]
        for key,concept,instant in specs:
            try:f.fact(key,concept,'Exact selected statement/note observation; no analyst approval implied',instant=instant,unit='shares' if key=='common' else 'USD',namespace='msft' if key=='acquisition_combined' else 'us-gaap')
            except ValueError as exc:exceptions.append(dict(input_id=key,reason=str(exc),required_artifact=None,kind='RETAINED_FACT_BINDING_OR_SCOPE'))
        try:f.fact('loss_credit_dta','DeferredTaxAssetsOperatingLossAndTaxCreditCarryForwards','Combined loss-and-credit DTA, not pure NOL',instant=True,namespace='msft')
        except ValueError as exc:exceptions.append(dict(input_id='loss_credit_dta',reason=str(exc),required_artifact=None,kind='RETAINED_FACT_BINDING_OR_SCOPE'))
        cover_dates=set()
        for node in f.root:
            if node.tag.startswith('{http://xbrl.sec.gov/dei/') and node.tag.endswith('}EntityCommonStockSharesOutstanding'):
                context=cash._context(f.contexts[node.get('contextRef')])
                if context and context[0]==f.period.cik and context[1] is None:cover_dates.add(str(context[2]))
        for stamp in sorted(cover_dates):f.fact('cover_common_'+stamp,'EntityCommonStockSharesOutstanding','Cover observation, not annual-end/diluted shares',instant=True,namespace='dei',unit='shares',as_of=stamp)
        for key,concept,unit in [('nonvested_awards','ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber','shares'),
            ('unrecognized_award_cost','EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized','USD')]:
            try:f.fact(key,concept,'Restricted stock awards, not dilution or economic value',instant=True,unit=unit,dimensions=(('us-gaap:AwardTypeAxis','us-gaap:RestrictedStockMember'),))
            except ValueError as exc:exceptions.append(dict(input_id=key,reason=str(exc),required_artifact=None,kind='AWARD_SCOPE_BINDING'))
        terms=[('net_income','NetIncomeLoss',1),('mixed_da','DepreciationAmortizationAndOther',1),('sbc_addback','ShareBasedCompensation',1),
            ('investment_loss','GainLossOnInvestmentsAndDerivativeInstruments',-1),('deferred_tax','DeferredIncomeTaxExpenseBenefit',1),
            ('receivables','IncreaseDecreaseInAccountsReceivable',-1),('inventory','IncreaseDecreaseInInventories',-1),
            ('other_current_assets','IncreaseDecreaseInOtherCurrentAssets',-1),('other_noncurrent_assets','IncreaseDecreaseInOtherNoncurrentAssets',-1),
            ('payables','IncreaseDecreaseInAccountsPayable',1),('contract_liabilities','IncreaseDecreaseInContractWithCustomerLiability',1),
            ('tax_movements','IncreaseDecreaseInAccruedIncomeTaxesPayable',1),('other_current_liabilities','IncreaseDecreaseInOtherCurrentLiabilities',1),
            ('other_noncurrent_liabilities','IncreaseDecreaseInOtherNoncurrentLiabilities',1)]
        cf=[]
        for key,concept,sign in terms:
            try:
                f.fact(key,concept,'Selected displayed CFO reconciliation; contribution sign explicit',namespace='msft' if key in ('mixed_da','investment_loss') else 'us-gaap')
                cf.append(dict(fact=key,multiplier=sign,contribution_usd=str(Decimal(f.facts[key]['value'])*sign)))
            except ValueError as exc:exceptions.append(dict(input_id=key,reason=str(exc),required_artifact=None,kind='CFO_RECONCILIATION_BINDING'))
        total=sum((Decimal(r['contribution_usd']) for r in cf),Decimal(0))
        supported=len(cf)==14 and 'cfo' in f.facts and total==Decimal(f.facts['cfo']['value'])
        if not supported:exceptions.append(dict(input_id='cfo_reconciliation',reason='Complete displayed14-term equality not established',kind='SCOPE_OR_RECONCILIATION',required_artifact=None))
        cp_candidates=[];face_cp=None
        for o in cash._occurrences(f.root,f.contexts,f.units,f.namespaces,f.namespaces['us-gaap'],'CommercialPaper',f.period,True):
            node=f.root[o.ordinal];attrs,text=f.inline.facts[node.get('id')]
            if inline_amount(attrs,text)!=Decimal(o.raw_value):raise ValueError('CP primary/instance mismatch')
            cp_candidates.append(dict(cash._occurrence_dict(o),primary_locator='inline#'+node.get('id'),primary_display=text))
        balance=f.text[f.text.find('BALANCE SHEETS'):f.text.find('CASH FLOWS')]
        if year==2024:
            precise=[o for o in cp_candidates if o['raw_value']=='6693000000' and o['decimals']=='-6']
            if len(precise)!=1 or 'Short-term debt 6,693 0' not in balance:raise ValueError('FY2024 face CP not independently established')
            face_cp=precise[0]
            for e in exceptions:
                if e['input_id']=='commercial_paper':e.update(kind='PRECISION_ALTERNATIVES_RETAINED',disposition='Reviewed face short-term debt6693, taggedCP, selected in draft; note6700 rounded remains alternative, no7m economic adjustment.')
        calc={}
        for key,operands in [('expense_da',('depreciation','amortization')),('current_financial',('cash','current_investments')),('named_financing',('term_debt','finance_liability'))]:
            if all(o in f.facts for o in operands):calc[key]=dict(value_usd=str(sum((Decimal(f.facts[o]['value']) for o in operands),Decimal(0))),operands=list(operands),origin='derived_draft',accepted=False,
                precision='Retain operand precision; no improved precision or completeness claim')
        if face_cp and 'named_financing' in calc:
            calc['named_financing']['value_usd']=str(Decimal(calc['named_financing']['value_usd'])+Decimal(face_cp['raw_value']))
            calc['named_financing']['operands'].append('face_cp_observation')
        if 'provision' in f.facts and 'pretax' in f.facts:
            with localcontext() as ctx:
                ctx.prec=34
                if Decimal(f.facts['pretax']['value'])<=0:raise ValueError('Reported ETR denominator ineligible')
                calc['reported_etr']=dict(value=str(Decimal(f.facts['provision']['value'])/Decimal(f.facts['pretax']['value'])),origin='derived',policy='annual_reported_effective_tax_rate_v1',operands=['provision','pretax'],scope='Reported accounting ratio, not future tax rate')
        checks={}
        for key,parent,children in [('term_partition','term_debt',('current_term','noncurrent_term')),('cash_partition','current_financial_parent',('cash','current_investments')),('equity_partition','equity',('common_capital','retained','oci')),('balance_partition','balance_total',('liabilities','equity'))]:
            checks[key]=all(k in f.facts for k in (parent,*children)) and sum((Decimal(f.facts[k]['value']) for k in children),Decimal(0))==Decimal(f.facts[parent]['value'])
        passages=[]
        for marker in ['CASH FLOWS','Principles of Consolidation','— DEBT','Savings Plans','— STOCKHOLDERS','— BUSINESS COMBINATIONS','Restricted']:
            a=f.text.find(marker)
            if a>=0:passages.append(dict(source='primary',offset=a,exact_excerpt=f.text[max(0,a-20):a+2400],sha256=f.primary.artifact.sha256))
        note_observations=[]
        legal=re.search(r'As of June 30, '+str(year)+r', we accrued aggregate legal liabilities of \$ ([\d,]+) million',f.text)
        if legal:
            note_observations.append(dict(input_id='legal_accrual',origin='reported_note_transcription',value_usd=str(Decimal(legal.group(1).replace(',',''))*1000000),unit='USD',precision='-6',
                as_of=identity['annual_end'],offset=legal.start(),exact_excerpt=legal.group(0),sha256=f.primary.artifact.sha256,not_an_estimate=True))
            for e in exceptions:
                if e['input_id']=='legal_accrual':e.update(kind='NOTE_SUPPORTED_XBRL_BINDING_ABSENT',disposition='Exact dated note amount retained separately; no invented XBRL occurrence.')
        rows.append(dict(identity=identity,source_manifest_reference='docs/phase1-selected-filing-identity-manifest.json#/rows/'+str(selected['manifest_index']),
            sources=[dict(path=artifact_path,pointer='/artifacts/'+str(i),**{k:a[k] for k in ('source_url','sha256','representation','digest_type','retrieved_at_utc','http_status','byte_length')}) for i,a in refs],
            facts=f.facts,calculations=calc,cp_candidates=cp_candidates,face_cp_observation=face_cp,cfo_reconciliation=dict(terms=cf,value_usd=str(total),supported=supported,independent_display='Exact primary inline/instance rows; sum checked against independently reported CFO'),
            partition_checks=checks,passages=passages,note_observations=note_observations,exceptions=exceptions,assumptions_active=False,analyst_complete=False))
    if len(rows)==3:
        later=rows[2]
        paragraph=next(p for p in later['passages'] if 'As of June 30, 2023, we had no commercial paper issued or outstanding.' in p['exact_excerpt'])
        rows[1]['comparative_cp_confirmation']=dict(source_identity=later['identity'],source_primary=later['sources'][0],
            as_of='2023-06-30',reported_cp_usd='0',basis='Explicit retained FY2024 Note11 dated statement and comparative short-debt face0, not FY2023 selected-instance fact or proof of broader borrowing.',
            exact_excerpt='As of June 30, 2023, we had no commercial paper issued or outstanding.',passage_offset=paragraph['offset'])
    return rows


def finish_msft_history(filing,package):
    parent={k:v for k,v in package.items() if k not in ('fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
    if attach_fy2025_review(filing,parent)!=parent:raise ValueError('Changed FY2025 review/source')
    record=_json((ROOT/OUTPUT).read_text())['fy2025_approval'];expected=fy2025_acceptance_record(parent)
    if type(record) is not dict or set(record)!=set(expected) or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed FY2025 acceptance')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    for k in set(expected)-{'recorded_at_utc','sha256','source_revision'}:
        if type(record[k]) is not type(expected[k]) or record[k]!=expected[k]:raise ValueError('Unregistered FY2025 acceptance: '+k)
    if record['source_revision']!=expected['source_revision']:raise ValueError('Stale FY2025 acceptance; explicit revalidation required')
    original=parent['fy2025_completeness_review'];checklist=[]
    if len(original['checklist'])!=14 or set(record['decisions'])!={f'25-D{i}' for i in range(1,8)}:raise ValueError('Incomplete FY2025 authorization')
    for row in original['checklist']:
        checklist.append(dict(row,status=row['status'] if not row['pending_decisions'] else 'SATISFIED_BY_EXPLICIT_FY2025_APPROVAL',approval_reference='/fy2025_approval'))
    manifest=[dict(r,manifest_index=i) for i,r in enumerate(_json((ROOT/'docs/phase1-selected-filing-identity-manifest.json').read_text())['rows']) if r['ticker']=='MSFT']
    identities=[r['identity'] for r in manifest]
    if len(identities)!=5 or len({r['accession'] for r in identities})!=5:raise ValueError('Frozen MSFT history differs')
    rows=review_msft_remaining(manifest)
    families=[r['field'] for r in parent['fy2026_analyst_checklist']['checklist']]
    mapping={'revenue':['revenue'],'ebit':['ebit'],'depreciation_amortization':['depreciation','amortization','finance_amortization'],
        'cash_capex':['capex','acquisition_combined','finance_additions'],'reported_cash_flow_working_capital_movements':[r['fact'] for r in rows[0]['cfo_reconciliation']['terms'][5:]],
        'deferred_taxes':['deferred_tax'],'stock_based_compensation':['sbc_expense','sbc_addback'],
        'unclassified_cfo_reconciliation_residual':['mixed_da'],'reported_cfo':['cfo'],'reported_tax_context':['provision','pretax','cash_taxes'],
        'cash_investment_components':['cash','current_investments','long_investments','nonmarketable'],
        'debt_lease_components':['term_debt','current_term','noncurrent_term','finance_liability','operating_liability'],
        'other_equity_bridge_claims_assets':['loss_credit_dta','retirement_expense','equity','legal_additional_exposure'],
        'point_in_time_shares':['common','nonvested_awards']}
    decision_fields={'depreciation_amortization':['H1'],'stock_based_compensation':['H2'],'debt_lease_components':['H3'],
        'cash_investment_components':['H4'],'other_equity_bridge_claims_assets':['H5','H6','H7','H8'],'unclassified_cfo_reconciliation_residual':['H9']}
    coverage=[]
    for i,row in enumerate(rows):
        row['family_coverage']=[dict(field=field,status='PENDING_ANALYST_APPROVAL' if field in decision_fields else
            'SOURCE_SUPPORTED' if all(k in row['facts'] for k in mapping[field]) else 'EVIDENCE_EXCEPTION',
            decisions=decision_fields.get(field,[]),fact_references=['/msft_history_review/remaining_periods/'+str(i)+'/facts/'+k for k in mapping[field] if k in row['facts']],
            completeness='Named observations only; component availability is not complete economic coverage') for field in families]
        coverage.append(dict(identity=row['identity'],analyst_complete=False,families=row['family_coverage']))
    for year,fieldref in [(2025,'/msft_history_review/accepted_fy2025'),(2026,'/fy2026_analyst_checklist')]:
        coverage.append(dict(identity=next(r for r in identities if r['annual_end']==f'{year}-06-30'),analyst_complete=True,checklist_reference=fieldref+'/checklist'))
    proposal_specs=[
        ('H1','Extend operating leases as service/finance leases as asset financing and the explicitly unproved finance-amortization inclusion assumption to each older year; no extra ROU add-back.',
         'Rounded D&A14600/13500/20000; finance amortization980/1352/1800 remains separate, not added. Alternative financing convention requires aligned expense/assets/taxes, not a local plug.',
         'Expense/ROU overlap and timing are not source-proved; FY2023 depreciation precision-9 must remain coarse.'),
        ('H2','Use each year recognized SBC expense as a labeled cost proxy once, preserving the separate CFO add-back.',
         '7502/9611/10734; no duplicate cost or award valuation. Alternative economic replacement-cost basis unavailable.',
         'Recognized expense is not cash replacement cost or outstanding-award value.'),
        ('H3','Select each named term+finance subtotal, including FY2024 face-issuedCP, with no additional undisclosed-borrowing adjustment.',
         '64683/64304/78775; FY2024 includes faceCP6693, note6700 retained alternative (+7), not an extra liability. Operating liabilities13717/15137/19077 excluded under proposed service convention.',
         'FY2022 CP unknown, FY2023 zero separately corroborated only by FY2024 dated disclosure; no broader borrowing zero or complete debt. Omitted additional borrowing unbounded; current term already included.'),
        ('H4','Select reported current financial balances only, keeping long-term/restricted/strategic observations separate, not excess cash.',
         '104757/111262/75543; LT6891/9879/14600 separate. Alternative unrestricted/excess pool cannot be quantified.',
         'Restrictions, operating reserves and full investment allocation remain unknown; no FY2026 restriction deduction is transferred.'),
        ('H5','No additional preferred-equity adjustment based on each reviewed common-equity presentation.',
         'No extra adjustment; source preferred balances remain unknown, not reported zeros. Alternative quantified preferred claim unavailable.',
         'Economically omits a potentially undisclosed preferred claim of unbounded size; no immateriality finding.'),
        ('H6','No additional NCI adjustment based on each consolidated-equity presentation and consolidation policy.',
         'No extra adjustment; source NCI balances remain unknown. Alternative quantified ownership bridge unavailable.',
         'Economically omits a potentially undisclosed minority claim of unbounded size.'),
        ('H7','Retain each year retirement expense without separate pension adjustment; acknowledge incomplete international coverage.',
         'Retirement1400/1600/1700 rounded expense, not closing liability; no extra charge. Alternative funded-status bridge unavailable.',
         'Potential undisclosed funded obligation/surplus is unbounded; not proof all plans are defined contribution.'),
        ('H8','Retain combined loss/credit DTA without a separate pure-NOL economic asset; retain recorded legal accruals/exposures separately.',
         'DTA1546/1441/1741; legal364/617/641 versus possible additional600 each year, never added into one claim. No pure-NOL allocation or value.',
         'Loss/credit allocation unavailable; no tax benefit valuation or inferred claim zero.'),
        ('H9','No separate residual scalar for each independently bound14-term displayed CFO reconciliation; retain mixed rows.',
         'CFO89035/87582/118548; mixed14460/13861/22287 remain distinct from expense D&A, no residual zero or subtraction-based adjustment.',
         'Mixed-caption contents remain unclassified; source equality is not EBIT/FCFF or organic cash compatibility.')]
    proposals=[dict(decision_id=k,status=PROPOSED,accepted=False,periods=[r['identity'] for r in rows],recommendation=t,numerical_consequence=n,uncertainty=u,
        evidence_reference='/msft_history_review/remaining_periods') for k,t,n,u in proposal_specs]
    result=json.loads(json.dumps(parent));result['fy2025_approval']=record
    result['msft_history_review']=dict(version=1,selected_identities=identities,remaining_periods=rows,
        accepted_fy2025=dict(identity=record['identity'],checklist=checklist,analyst_complete=True,remaining_essential_inputs=[],
            financing_usd='89323000000',source_commercial_paper_usd='0',source_broader_borrowing_usd=None,
            financing_basis='Approved no-additional-borrowing adjustment beyond explicit CP0; not complete debt or immateriality, omitted borrowing unquantified',
            decisions_accepted=list(record['decisions']),audit_sha256=record['sha256']),
        fy2026_result_reference='/fy2026_analyst_checklist',period_family_coverage=coverage,consolidated_proposals=proposals,
        evidence_acquisition_requirements=[],artifact_pair_count=3,
        evidence_limits='All six older exact primary/instance bodies/receipts present. Remaining exceptions are named-concept/coverage gaps or retained precision alternatives, not a missing-body acquisition queue. No acquisition authorized here.',
        stopping_condition='One company batch finished; stop for H1-H9 together and review of retained binding/coverage exceptions. No annual memo cycle or automatic new research.',
        new_older_period_approvals=0,phase_closed=False,valuation_consumption_approved=False)
    return result


def msft_history_acceptance_record(package):
    if 'msft_history_approval' in package:raise ValueError('Immutable history approval already exists')
    review=package['msft_history_review']
    record=dict(schema='msft-operation-acceptance-audit-v1',version=1,sequence=6,
        previous=package['fy2025_approval']['sha256'],action='ACCEPT_FY2022_FY2024_CONSOLIDATED_PACKAGE',
        author='User, explicit approval of consolidated MSFT FY2022-FY2024 H1-H9 exactly as proposed and E1/E2 dispositions',
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        rationale='Activate only the reviewed three-year package alongside existing FY2025/FY2026 approvals. Supporting unknowns remain unknown; no complete debt/reinvestment, immateriality or Phase2 certification.',
        source_commit='5ac9ea2c0d4f710182082b343760f26660fabd35',source_revision=digest(relevant(package)),
        identities=[r['identity'] for r in review['remaining_periods']],
        decisions={r['decision_id']:{k:v for k,v in r.items() if k not in ('decision_id','status','accepted')} for r in review['consolidated_proposals']},
        exceptions=dict(E1='Accepted supporting limitation: capital-creditor and equity-method subamount bindings remain unknown, not zero; no complete reinvestment/assets claim.',
            E2='Select FY2024 face-statement CP6693 USDm; retain rounded note6700 USDm as non-default precision alternative, without a7m adjustment.'),
        financial_sufficiency='ONLY_APPROVED_HISTORICAL_INPUT_PERIMETER',phase_closed=False,valuation_consumption_approved=False)
    record['sha256']=digest(record)
    return record


def activate_msft_history(filing,package):
    """Additive current view; never mutate the source/proposal/audit snapshots."""
    parent={k:v for k,v in package.items() if k not in ('msft_history_approval','msft_current_history')}
    if finish_msft_history(filing,parent)!=parent:raise ValueError('Changed preceding company review/source')
    record=_json((ROOT/OUTPUT).read_text())['msft_history_approval'];expected=msft_history_acceptance_record(parent)
    if type(record) is not dict or set(record)!=set(expected) or record['sha256']!=digest({k:v for k,v in record.items() if k!='sha256'}):raise ValueError('Malformed history acceptance')
    ManualIdentity(record['author'],record['recorded_at_utc'],record['rationale'])
    for k in set(expected)-{'recorded_at_utc','sha256','source_revision'}:
        if type(record[k]) is not type(expected[k]) or record[k]!=expected[k]:raise ValueError('Unregistered history acceptance: '+k)
    if record['source_revision']!=expected['source_revision']:raise ValueError('Stale history acceptance; explicit revalidation required')
    if set(record['decisions'])!={f'H{i}' for i in range(1,10)}:raise ValueError('Incomplete history authorization')
    families=[r['field'] for r in parent['fy2026_analyst_checklist']['checklist']];periods=[]
    def selection(value,reference,unit='USD',precision=None,origin='reported',**scope):
        return dict(value=value,unit=unit,precision=precision,origin=origin,source_reference=reference,**scope)
    for i,row in enumerate(parent['msft_history_review']['remaining_periods']):
        base=f'/msft_history_review/remaining_periods/{i}';facts=row['facts'];calc=row['calculations']
        if [r['field'] for r in row['family_coverage']]!=families or not all(row['partition_checks'].values()) or not row['cfo_reconciliation']['supported'] or len(row['cfo_reconciliation']['terms'])!=14:raise ValueError('Incomplete older source/checklist binding')
        if any(r['status'] not in ('SOURCE_SUPPORTED','PENDING_ANALYST_APPROVAL') or not r['fact_references'] for r in row['family_coverage']):raise ValueError('Unresolved essential history requirement')
        def fact(key,multiplier=1):
            f=facts[key]
            return selection(str(Decimal(f['value'])*multiplier),base+'/facts/'+key,f['unit'],f['precision'],raw_value=f['value'],multiplier=multiplier)
        def calculation(key):
            c=calc[key]
            return selection(c['value_usd'],base+'/calculations/'+key,precision=[facts[k]['precision'] if k in facts else row['face_cp_observation']['decimals'] for k in c['operands']],origin='derived',accepted_under='/msft_history_approval',scope='Named approved population only; retains operand precision')
        inputs=dict(revenue=fact('revenue'),ebit=fact('ebit'),depreciation_amortization=calculation('expense_da'),cash_capex=fact('capex',-1),
            reported_cash_flow_working_capital_movements=dict(value=None,rows=[dict(fact(t['fact'],t['multiplier']),role='already_in_reported_cfo') for t in row['cfo_reconciliation']['terms'][5:]],additional_deduction_permitted=False,book_delta_nwc=False),
            deferred_taxes=fact('deferred_tax'),stock_based_compensation=dict(selected=fact('sbc_expense'),addback=fact('sbc_addback'),economic_proxy_once=True),
            unclassified_cfo_reconciliation_residual=dict(value=None,disposition='APPROVED_NO_SEPARATE_OPERATION',not_reported_zero=True,mixed_observation=fact('mixed_da')),
            reported_cfo=fact('cfo'),reported_tax_context=dict(provision=fact('provision'),pretax=fact('pretax'),cash_taxes=fact('cash_taxes',-1),reported_etr=dict(calc['reported_etr'],unit='pure',source_reference=base+'/calculations/reported_etr')),
            cash_investment_components=dict(selected=calculation('current_financial'),long_term=fact('long_investments'),nonmarketable=fact('nonmarketable'),restrictions=None,operating_reserve=None,unrestricted_or_excess_cash=False),
            debt_lease_components=dict(selected=calculation('named_financing'),term=fact('term_debt'),finance_lease=fact('finance_liability'),operating_lease=fact('operating_liability'),additional_borrowing=None,no_additional_adjustment='approved analyst assumption; omitted amount unbounded',complete_debt=False,precision_alternatives_reference=base+'/cp_candidates'),
            other_equity_bridge_claims_assets=dict(preferred=None,nci=None,pension=None,pure_nol=None,loss_credit_dta=fact('loss_credit_dta'),retirement_expense=fact('retirement_expense'),legal_reference=base+'/note_observations',additional_exposure=fact('legal_additional_exposure'),no_additional_claim_adjustments='approved analyst assumptions; omitted size unbounded'),
            point_in_time_shares=dict(selected=fact('common'),observation_date=row['identity']['annual_end'],cover=[fact(k) for k in facts if k.startswith('cover_common_')],awards=fact('nonvested_awards'),aggregation_or_dilution_approved=False))
        inputs['depreciation_amortization'].update(finance_amortization_included='approved unproved assumption',additional_rou_addback=False)
        checklist=[dict(field=r['field'],status='SATISFIED_BY_EXPLICIT_HISTORY_APPROVAL' if r['decisions'] else 'SATISFIED_WITHIN_REVIEWED_SOURCE_SCOPE',evidence_references=r['fact_references'],decisions=r['decisions']) for r in row['family_coverage']]
        periods.append(dict(identity=row['identity'],inputs=inputs,checklist=checklist,analyst_complete=True,remaining_essential_inputs=[],approval_reference='/msft_history_approval',
            sources_reference=base+'/sources',supporting_limitations_reference=base+'/exceptions',cfo_reconciliation_reference=base+'/cfo_reconciliation',supporting_investment_references=[base+'/facts/acquisition_combined',base+'/facts/finance_additions'],
            capital_creditors=None,equity_method_subamount=None))
    for i,row in enumerate(parent['periods']):
        base=f'/periods/{i}';accepted=parent['accepted_view']['periods'][i]
        original=parent['msft_history_review']['accepted_fy2025'] if i==0 else parent['fy2026_analyst_checklist']
        if not original['analyst_complete'] or original['remaining_essential_inputs'] or len(original['checklist'])!=14 or any(not r['status'].startswith('SATISFIED') for r in original['checklist']):raise ValueError('Prior period checklist not satisfied')
        def input_value(key):
            j,v=next((j,v) for j,v in enumerate(row['inputs']) if v['input_id']==key)
            return dict(v,source_reference=base+'/inputs/'+str(j))
        def observed(key):return input_value('reported:'+key)
        movements=[input_value(k) for k in row['cfo_reconciliation']['terms'][5:]]
        inputs=dict(revenue=input_value('revenue'),ebit=input_value('ebit'),depreciation_amortization=dict(accepted['expense_da'],source_reference=f'/accepted_view/periods/{i}/expense_da'),cash_capex=observed('PaymentsToAcquirePropertyPlantAndEquipment'),
            reported_cash_flow_working_capital_movements=dict(value=None,rows=movements,additional_deduction_permitted=False,book_delta_nwc=False),
            deferred_taxes=observed('DeferredIncomeTaxExpenseBenefit' if i==0 else 'DeferredIncomeTaxesAndTaxCredits'),
            stock_based_compensation=dict(selected=input_value('sbc_cost_proxy'),addback=observed('ShareBasedCompensation'),economic_proxy_once=True),
            unclassified_cfo_reconciliation_residual=dict(value=None,disposition='APPROVED_NO_SEPARATE_OPERATION',not_reported_zero=True,mixed_observation=observed('DepreciationAmortizationAndOther')),
            reported_cfo=observed('NetCashProvidedByUsedInOperatingActivities'),reported_tax_context=dict(provision=observed('IncomeTaxExpenseBenefit'),pretax=dict(row['facts']['pretax'],source_reference=base+'/facts/pretax'),cash_taxes=observed('IncomeTaxesPaidNet'),reported_etr=input_value('reported_etr')),
            cash_investment_components=dict(accepted['cash'],source_reference=f'/accepted_view/periods/{i}/cash',long_term=input_value('long_investments')),
            debt_lease_components=dict(selected=accepted['borrowings']['selected'],source_reference=f'/accepted_view/periods/{i}/borrowings',no_additional_adjustment_approval='/fy2025_approval' if i==0 else '/fy2026_financing_approval',additional_borrowing=None,complete_debt=False),
            other_equity_bridge_claims_assets=dict(preferred=None,nci=None,pension=None,pure_nol=None,source_reference='/fy2025_completeness_review' if i==0 else '/fy2026_claim_assumptions_view',loss_credit_dta=input_value('loss_credit_dta')),
            point_in_time_shares=dict(selected=input_value('year_end_common'),observation_date=row['identity']['annual_end'],cover=input_value('cover_common'),awards=input_value('nonvested_awards'),aggregation_or_dilution_approved=False))
        periods.append(dict(identity=row['identity'],inputs=inputs,checklist=original['checklist'],analyst_complete=True,remaining_essential_inputs=[],sources_reference='/sources',cfo_reconciliation_reference=base+'/cfo_reconciliation',supporting_limitations_reference=base+'/unresolved_requirements',supporting_investment_reference=f'/accepted_view/periods/{i}/investment_columns'))
    if len(periods)!=5 or any(set(r['inputs'])!=set(families) for r in periods) or [r['identity'] for r in periods]!=parent['msft_history_review']['selected_identities']:raise ValueError('Five-year identity/family accounting differs')
    result=json.loads(json.dumps(parent));result['msft_history_approval']=record
    result['msft_current_history']=dict(version=1,authoritative_current_view=True,periods=periods,company_completed_for_approved_historical_perimeter=True,
        family_slots=70,passed_family_slots=70,complete_debt=False,complete_reinvestment=False,phase_closed=False,valuation_consumption_approved=False,
        historical_proposal_snapshot='/msft_history_review',approval_sha256=record['sha256'],
        active_path='Reported movements already included in independently reconciled CFO; no reconstructed complete NWC/book delta prerequisite or extra deduction.',
        company_counts=dict(broad_evidence_assessment=42,company_analyst_packages=3,completed_company_wide_packages=1,partial_company_packages=2,broad_assessment_only=39),
        next_company_batch='AAPL frozen FY2021-FY2025, existing completion-assessment B1; not started',
        comparability=['Exact accession presentations retained; Nuance FY2022 and Activision FY2024 acquisitions remain within consolidated scope, not organic.',
            'FY2024 CP face6693 versus rounded6700 alternative: select face, no adjustment; current term maturities already included.',
            'FY2023 coarse depreciation precision-9 retained; expense D&A and mixed CFO observations differ.',
            'FY2025 selected mixed34153/gain609 differs from FY2026 comparative29433/5329; no recast or plug.',
            'Capital creditors/equity-method subamounts unknown in older years (E1); no complete reinvestment or investment allocation.'])
    return result


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
