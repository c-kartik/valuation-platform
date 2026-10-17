"""One retained AVGO/TSLA/LLY review. No approval activation or new resolver.

Explicit source choices below are company-review data. Existing extraction,
annual identity, receipt, arithmetic and policy verifiers remain authoritative.
"""
import json
import re
import sys
from collections import Counter
from decimal import Decimal as D

import prepare_standard_review_batch as shared
import prepare_trillion_review_batch as peer
from prepare_msft_analyst_package import ROOT, digest, relevant, PROPOSED
from valuation_platform.analyst import approved_income_integration as approved
from valuation_platform.analyst import refreshed_capex as refresh
from valuation_platform.normalization.output import _serialize_operating_income_derivation

BASELINE = 'dad351527cbbf30f4f6df5f19f43ca57484a0cfe'
REVIEW_TIME = '2026-10-17T18:51:31+00:00'
TICKERS = ('AVGO', 'TSLA', 'LLY')
SUMMARY = 'docs/company-data-preparation/large-company-review-batch.json'
LEDGERS = ('repaired-income-ledger', 'refreshed-capex-ledger',
           'retained-d-and-a-ledger', 'retained-reported-tax-context-ledger',
           'retained-claims-shares-ledger')
EXTRA = {
    'borrowing_current': ('DebtCurrent', True),
    'carrying_borrowing_parent': ('DebtLongtermAndShorttermCombinedAmount', True),
    'debt_discount': ('DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet', True),
    'other_ppe_cash': ('PaymentsToAcquireOtherPropertyPlantAndEquipment', False),
    'iprd_cash': ('PaymentsToAcquireInProcessResearchAndDevelopment', False),
    'iprd_expense': ('ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff', False),
    'noncurrent_investments': ('LongTermInvestments', True),
    'investment_cash': ('PaymentsToAcquireOtherInvestments', False),
    'unrecognized_tax_benefits': ('UnrecognizedTaxBenefits', True),
    'litigation_liability': ('LitigationReserve', True),
    'lessee_finance_assets': ('FinanceLeaseRightOfUseAsset', True),
    'restricted_current': ('RestrictedCashCurrent', True),
    'restricted_noncurrent': ('RestrictedCashNoncurrent', True),
    'benefit_liabilities': ('PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent', True),
    'lessor_net_receivable': ('SalesTypeLeaseNetInvestmentInLeaseAfterAllowanceForCreditLoss', True),
    'lessor_net_current': ('SalesTypeLeaseNetInvestmentInLeaseAfterAllowanceForCreditLossCurrent', True),
    'lessor_net_noncurrent': ('SalesTypeLeaseNetInvestmentInLeaseAfterAllowanceForCreditLossNoncurrent', True),
    'other_acquisition_cash': ('OtherPaymentsToAcquireBusinesses', False),
    'lessor_operating_vehicles': ('OperatingLeasesIncomeStatementLeaseRevenue', False),
}
EXTENSIONS = {
    'AVGO': [('acquisition_amortization_cogs', 'Amortizationofacquisitionrelatedintangibleassetscostofproductssold', False),
             ('acquisition_amortization_opex', 'Amortizationofacquisitionrelatedintangibleassetsoperatingexpenses', False),
             ('mixed_amortization_rou', 'Amortizationofintangibleandrightofuseassets', False)],
    'TSLA': [('mixed_da_impairment', 'DepreciationAmortizationAndImpairment', False),
             ('named_financing_current', 'LongTermDebtAndFinanceLeasesCurrent', True),
             ('named_financing_noncurrent', 'LongTermDebtAndFinanceLeasesNoncurrent', True),
             ('accrued_purchases', 'AccruedPurchases', True)],
    'LLY': [('asset_acquisition_cash', 'PaymentsForAssetAcquisitions', False)],
}


def ledger_row(ledger, identity):
    matches = [(i, r) for i, r in enumerate(ledger['rows']) if r.get('identity') == identity]
    if len(matches) != 1:
        raise ValueError('One exact retained ledger identity required')
    return matches[0]


def note_rows(case):
    """Keep actual displayed note cells/headers; never infer values from names.

    This supporting payload includes comparative/dimensional populations, which
    are NOT selected annual facts. The original primary digest/locators bind it.
    """
    captions = re.compile(r'^(Total debt|Total short.term debt|Total long.term debt|'
        r'Short.term borrowings|Short.term commercial paper|Current portion of debt|'
        r'Debt and finance leases|Net investment in sales.type leases|Gross lease receivables|'
        r'Accrued purchases|Funded status|Net asset \(liability\)|Net amount recognized|'
        r'Other noncurrent assets|Other noncurrent liabilities|Noncontrolling interests|'
        r'Redeemable noncontrolling interests|Preferred stock|Acquired in.process|'
        r'Purchases of in.process|Cash paid for acquisitions|Purchases of property|'
        r'Finance leases|Total finance lease|Depreciation|Amortization expense|'
        r'Amortization of acquisition.related|Non.cash|Total pension)', re.I)
    rows = []
    for ti, table in enumerate(case['tables']):
        header = ' | '.join(c['text'] for r in table[:3] for c in r)
        for ri, row in enumerate(table):
            caption = row[0]['text'].strip() if row else ''
            if captions.search(caption):
                rows.append(dict(table=ti, row=ri, caption=caption, header=header,
                    cells=row, source_sha256=case['filing'].primary.artifact.sha256,
                    role='supporting_displayed_population_not_automatic_selected_fact'))
    return rows


def excerpts(f, ticker):
    markers = {
        'AVGO': ['VMware', 'ten-for-one', '10-for-1', '53 weeks',
                 'amortization of intangible and right-of-use assets', 'restructuring',
                 'finance leases', 'defined benefit', 'preferred stock'],
        'TSLA': ['depreciation, amortization and impairment', 'depreciation and amortization expense',
                 'non-recourse', 'sales-type leases', 'three-for-one', 'three -for-one',
                 'restricted cash', 'digital assets', 'tax valuation allowance', 'noncontrolling interests'],
        'LLY': ['acquired in-process research and development', 'Finance leases are included',
                'Funded status', 'Note 16: Contingencies', 'Note 15: Retirement',
                'intangible assets with finite lives', 'common stock held in treasury',
                'shares of common stock outstanding', 'IPR&D'],
    }[ticker]
    result = []
    for marker in markers:
        hits = list(re.finditer(r'(?<!\w)' + re.escape(marker) + r'(?!\w)', f.text, re.I))
        for m in dict.fromkeys(hits[:1] + hits[-2:]):
            result.append(dict(marker=marker, offset=m.start(),
                exact_excerpt=f.text[max(0, m.start()-100):m.end()+1800],
                source_sha256=f.primary.artifact.sha256))
    return result


def prepare_income(case, row):
    """Direct facts or exact unchanged registered derivation, never copied EBIT."""
    f = case['filing']
    for slot in row['fields']:
        if slot['status'] in ('POPULATED', 'POPULATED_REPORTED_DIRECT'):
            candidate = slot['candidates'][slot['selected']]
            shared.monetary(case, slot['field'], candidate['concept'], namespace=candidate['namespace'])
        elif slot['status'] == 'POPULATED_DERIVED':
            metadata = next(m['filing'] for m in approved.bindings()['filings']
                if m['filing']['accession_number'] == f.period.accession)
            result = approved.execute(case['evidence'], metadata)
            proof = _serialize_operating_income_derivation(result.derivation_provenance)
            if proof != slot['provenance'] or str(result.value) != slot['value_usd']:
                raise ValueError('Registered EBIT resolver/proof differs from retained integration')
            operand_keys = []
            for operand in proof['operands']:
                key = 'ebit_operand:' + operand['operand_id']
                try:
                    shared.monetary(case, key, operand['concept'], namespace=operand['namespace'])
                except ValueError:
                    # The unchanged registered policy explicitly reviews these
                    # competing note/face precision populations. Do not introduce
                    # generic precedence, or select merely the desired number.
                    bindings=[]
                    for ti,table in enumerate(case['tables']):
                        for ri,row_cells in enumerate(table):
                            for ci,cell in enumerate(row_cells):
                                for item in cell['facts']:
                                    a=item['attrs'];prefix,_,local=a['name'].partition(':')
                                    if local!=operand['concept'] or f.namespaces[prefix]!=operand['namespace']:continue
                                    if not any(a['contextref']==o['context_id'] and a['unitref']==o['unit_ref'] and a['decimals']==o['decimals'] for o in operand['occurrences']):continue
                                    fact=peer.primary_fact(case,item,ti,ri,ci,row_cells[0]['text'])
                                    if D(fact['value'])==D(operand['expected_value']):bindings.append(fact)
                    if not bindings:raise ValueError('Registered selected operand lacks exact displayed confirmation')
                    f.facts[key]=dict(bindings[0],confirming_primary_tables=[b['primary_table'] for b in bindings],
                        selection_rationale='Exact unchanged approved derivation operand occurrences/precision gates; not generic precedence',
                        policy_id=proof['policy_id'],policy_version=proof['policy_version'],
                        reviewed_nonselected_occurrences=operand['reviewed_nonselected_occurrences'])
                if D(f.facts[key]['value']) != D(operand['expected_value']):
                    raise ValueError('Registered EBIT operand differs from independent primary')
                operand_keys.append(key)
            case['derived_ebit'] = dict(input_id='ebit', value=str(result.value), unit='USD',
                origin='derived', status='SOURCE_SUPPORTED', precision=slot['precision'],
                policy_id=proof['policy_id'], policy_version=proof['policy_version'],
                policy_proof=proof, operand_observations=operand_keys,
                metadata=metadata, scope='Exact existing approved operating perimeter; not adjusted EBIT')


def build():
    cases, missing = shared.load(TICKERS)
    ledgers = {name: json.loads((ROOT / ('docs/' + name + '.json')).read_text()) for name in LEDGERS}
    # Existing exact refresh review is independently replayed; no new acceptance.
    refresh_audits = {a.period.accession: a for a in refresh.audits()}
    packages = {}
    for case in cases:
        ticker = case['ticker']; f = case['filing']
        case['tables'] = shared.documents.parse(case['record'], improved=True)
        errors = shared.observe(case)
        income_index, income_row = ledger_row(ledgers['repaired-income-ledger'], case['identity'])
        prepare_income(case, income_row)
        for key, (concept, instant) in EXTRA.items():
            try: shared.monetary(case, key, concept, instant)
            except (ValueError, KeyError) as exc: errors.append(dict(input_id=key, value=None, reason=str(exc)))
        for key, concept, instant in EXTENSIONS[ticker]:
            try: shared.monetary(case, key, concept, instant, ticker.lower())
            except (ValueError, KeyError) as exc: errors.append(dict(input_id=key, value=None, reason=str(exc)))
        if ticker=='LLY':
            # Expense includes development milestones in2022; the smaller CFO
            # acquired-IPR&D observation is not equivalent and is kept separate.
            f.facts['iprd_expense']=dict(f.facts['ebit_operand:A'])
            if f.year<2023:
                for key,concept in [('iprd_addback','AcquiredInProcessResearchAndDevelopment'),('iprd_cash','PurchasedInProcessResearchAndDevelopment')]:
                    try:shared.monetary(case,key,concept,namespace='lly')
                    except (ValueError,KeyError) as exc:errors.append(dict(input_id=key,value=None,reason=str(exc)))
            else:
                peer.displayed_selection(case,'iprd_addback',f.facts['iprd_expense']['concept'],
                    ('Acquired in-process research and development','Acquired in-process research and development (Note 3)'))
            if f.year==2025:
                # Note7 explicitly labels this carrying population short-term
                # investments. Its measurement-basis dimension is not an issuer
                # or segment aggregate and must not be dropped.
                f.fact('current_investments','AvailableForSaleSecuritiesDebtSecuritiesCurrent',
                    'Note7 short-term investments carrying amount, not fair-value alternative',instant=True,
                    dimensions=(('us-gaap:FairValueByMeasurementBasisAxis','us-gaap:CarryingReportedAmountFairValueDisclosureMember'),))
        # Exact face provision, not generic precedence over rounded note candidates.
        peer.displayed_selection(case, 'face_tax', 'IncomeTaxExpenseBenefit', (
            'Provision for income taxes', 'Provision for (benefit from) income taxes', '(Benefit from) provision for income taxes',
            'Provision for (benefit from) income taxes (Note 14)', 'Income taxes', 'Income taxes (Note 14)'))
        alternatives = {key: peer.candidates(case, key, concept, instant)
            for key, (concept, instant) in {**shared.SPECS, **EXTRA}.items()
            if key in ('tax', 'depreciation', 'intangible_amortization', 'debt_parent', 'cash',
                       'cash_tax', 'cash_tax_gross', 'noncurrent_investments')}
        # Exact retirement-plan populations, not consolidated guessed allocation.
        for member in ('PensionPlansDefinedBenefitMember', 'OtherPostretirementBenefitPlansDefinedBenefitMember','DefinedBenefitPostretirementHealthCoverageMember'):
            for concept in ('DefinedBenefitPlanFundedStatusOfPlan', 'DefinedBenefitPlanAmountsRecognizedInBalanceSheet',
                'PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent','DefinedBenefitPlanAssetsForPlanBenefitsNoncurrent'):
                key = member + ':' + concept
                try:
                    f.fact(key, concept, 'Exact separately disclosed benefit-plan population, no netting',
                        instant=True, dimensions=(('us-gaap:RetirementPlanTypeAxis', 'us-gaap:' + member),))
                except (ValueError, KeyError) as exc: errors.append(dict(input_id=key, value=None, reason=str(exc)))
        rec = shared.delivery.plain(shared.cfo.inspect_statement(case['evidence'], case['record'], version=shared.cfo.IMPROVED_VERSION))
        if rec != case['proof']['reconciliation']:
            raise ValueError('Original independently displayed CFO proof changed')
        def calc(key, operands, scope, origin='derived'):
            if not operands or any(k not in f.facts for k in operands): return
            f.entry(key, key, operands, status=PROPOSED, origin=origin, scope=scope,
                completeness='partial_named_population_only',
                rationale='Company-specific proposal pending user approval; not an approved complete total')
            f.entries[-1]['formula_version'] = 'retained-large-company-review-v1'
        if ticker == 'AVGO':
            calc('limited_da_proxy', ['depreciation', 'acquisition_amortization_cogs', 'acquisition_amortization_opex'],
                 'Depreciation plus separately reported acquisition amortization; no operating ROU or impairment addition', 'proxy')
            if 'debt_finance_current' in f.facts and 'debt_finance_long' in f.facts:
                calc('named_financing', ['debt_finance_current', 'debt_finance_long'], 'Current/noncurrent carrying captions ALREADY include finance lease liabilities')
            else:
                calc('named_financing', ['debt_current', 'debt_long'], '2021 carrying captions include finance liabilities; note parent has different lease scope')
            calc('gross_current_financial', ['cash'], 'Cash equivalents only; no unobserved investment balance inferred zero')
        elif ticker == 'TSLA':
            calc('limited_da_proxy', ['mixed_da_impairment'], 'Explicitly impairment-inclusive CFO proxy, not pure expense D&A', 'proxy')
            calc('named_financing', ['named_financing_current', 'named_financing_noncurrent'], 'Carrying debt/finance lease face captions, including nonrecourse funding; no second finance parent addition')
            calc('gross_current_financial', ['cash', 'current_investments' if 'current_investments' in f.facts else 'marketable_current'], 'Current named cash and investments; restricted cash and digital/lessor assets separate')
        else:
            calc('limited_da_proxy', ['da'], 'CFO D&A as limited historical proxy, no acquired IPR&D/impairment add-back', 'proxy')
            calc('named_financing', ['borrowing_current', 'debt_long'], 'Combined short borrowing/current maturities + noncurrent carrying debt; CP and embedded finance leases NOT incremental')
            calc('gross_current_financial', ['cash', 'current_investments'], 'Named current cash and short investments; noncurrent/strategic holdings remain separate')
        ledger_refs = {}
        for name, ledger in ledgers.items():
            i, row = ledger_row(ledger, case['identity'])
            # Exact locator + relevant record digest avoids duplicating embedded
            # refresh bodies. Full original proof remains in its existing ledger.
            ledger_refs[name] = dict(reference='docs/' + name + '.json#/rows/' + str(i),
                record_sha256=digest(row), status=row.get('status'), value_usd=row.get('value_usd'))
        refreshed = None
        if ticker == 'LLY':
            audit = refresh_audits[f.period.accession]
            selected = refresh.package(case['evidence'], audit)
            # Verify primary amount independently, not just the report verifier.
            if D(f.facts['other_ppe_cash']['value']) != -selected.value:
                raise ValueError('Refreshed Capex differs from exact primary/instance cash population')
            original_row = ledger_row(ledgers['refreshed-capex-ledger'], case['identity'])[1]
            if str(selected.value) != original_row['value_usd']:
                raise ValueError('Reviewed refresh changed original preparation value')
            refreshed = dict(refresh_id=audit.refresh_id, refresh_version=audit.refresh_version,
                review_path=audit.review_path, review_sha256=audit.review_sha256,
                original_entry_sha256=audit.original_entry_sha256,
                acceptance_basis=audit.acceptance_basis, original_byte_equivalence=audit.original_byte_equivalence,
                value_usd=str(selected.value), supported_requirements=list(audit.supported_requirements),
                artifacts=[dict(historical_sha256=a.historical_sha256, historical_status=a.historical_status,
                    historical_digest_type=a.historical_digest_type, refreshed_sha256=a.refreshed_receipt.artifact.sha256,
                    url=a.refreshed_receipt.artifact.url, receipt_path=a.receipt_path,
                    receipt_locator=a.receipt_locator, receipt_document_sha256=a.receipt_document_sha256,
                    retrieved_at_utc=a.refreshed_receipt.retrieved_at_utc, http_status=a.refreshed_receipt.http_status)
                    for a in audit.artifacts])
        for key, fact in f.facts.items():
            fact.setdefault('origin', 'reported')
            fact['role'] = ('cfo_reconciliation_observation' if key in ('da', 'mixed_amortization_rou', 'mixed_da_impairment', 'sbc_addback', 'deferred_tax', 'deferred_movement','iprd_addback') else
                'recognized_expense_observation' if key in ('depreciation', 'acquisition_amortization_cogs', 'acquisition_amortization_opex', 'intangible_amortization', 'finance_amortization', 'sbc_expense', 'iprd_expense') else
                'separate_dated_shares_or_awards' if key.startswith('shares:') else 'separate_reported_observation')
        if ticker=='TSLA' and 'cash_tax_gross' in f.facts:
            # Tag name alone cannot establish gross scope: the actual caption
            # explicitly says net of refunds despite IncomeTaxesPaid tagging.
            f.facts['cash_tax_gross']['scope']='Displayed cash paid for income taxes, net of refunds; source concept IncomeTaxesPaid does not make this gross'
        for error in errors:
            error['disposition'] = 'superseded_by_exact_review_binding' if error['input_id'] in f.facts else 'unselected_or_unavailable_selector_not_financial_zero'
        from valuation_platform.analyst.historical_inputs import Field
        mapping = {Field.CFO:'CF',Field.CF_WORKING_CAPITAL:'CF',Field.CFO_RESIDUAL:'CF',
            Field.DA:'DA',Field.CAPEX:'INV',Field.SBC:'SBC',Field.CASH_INVESTMENTS:'CASH',
            Field.DEBT_LEASES:'FIN',Field.OTHER_BRIDGE:'CLAIMS',Field.SHARES:'SHARES'}
        if ticker == 'TSLA': mapping[Field.TAX] = 'TAX'
        # AVGO displayed deferred-taxes-and-other-noncash row is NOT pure note provision.
        if ticker == 'AVGO': mapping[Field.DEFERRED_TAX] = 'CF'
        checklist = [dict(field=field.value, status='PROPOSED_PENDING_APPROVAL' if field in mapping else 'SOURCE_SUPPORTED',
            pending_decisions=[ticker+'-'+mapping[field]] if field in mapping else [], financial_complete=False,
            evidence_references=['/facts','/preparation_ledger_evidence','/cfo_reconciliation'],
            rationale='Reported observations are supported; any proxy, no-separate operation or omission needs this company approval.' if field in mapping else 'Exact existing source/policy observation; not future financial sufficiency.') for field in Field]
        period = dict(identity=case['identity'],selection_reference=case['manifest_reference'],prior_population_reference=case['proof_reference'],
            sources=case['sources'],facts=f.facts,calculations=f.entries,derived_ebit=case.get('derived_ebit'),
            cfo_reconciliation=rec,movement_rows=[r for r in rec['populations'][0]['rows'] if r.get('role')=='displayed_movement'],
            alternatives=alternatives,source_binding_exceptions=errors,passages=excerpts(f,ticker),
            supporting_note_rows=note_rows(case),preparation_ledger_evidence=ledger_refs,refreshed_capex=refreshed,
            family_checklist=checklist,analyst_complete=False,new_assumptions_active=False,
            original_supporting_unknowns=dict(complete_expense_da=None,complete_reinvestment=None,additional_unidentified_borrowing=None,
                unknown_restrictions=None,operating_reserve=None,unidentified_claims=None,complete_lease_cash=None),
            cash_sign_multipliers={k:-1 for k in ('cash_capex','other_ppe_cash','iprd_cash','asset_acquisition_cash','acquisition','other_acquisition_cash','cash_tax','cash_tax_gross','cash_interest','op_cash','finance_interest_cash','finance_principal_cash') if k in f.facts})
        packages.setdefault(ticker,dict(schema='company-analyst-review-v1',version=1,ticker=ticker,source_commit=BASELINE,
            review_author='Retained-evidence company review; not user approval',review_recorded_at_utc=REVIEW_TIME,periods=[],
            new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(period)
    for ticker, package in packages.items():
        package['periods'].sort(key=lambda r:r['identity']['annual_end'])
        package.update(family_slots=70,approval_table_reference=SUMMARY+'#/decisions',
            evidence_acquisition_requirements=[m for m in missing if m['ticker']==ticker],
            outcomes=dict(Counter(c['status'] for r in package['periods'] for c in r['family_checklist'])))
        package['review_revision']=digest(relevant(package))
    return packages, missing


def decisions(p):
    t=p['ticker']
    def nums(key,calc=False):
        values=[]
        for r in p['periods']:
            x=next((x for x in r['calculations'] if x['input_id']==key),{}) if calc else r['facts'].get(key,{})
            values.append(str(D(x['value'])/1000000) if x.get('value') is not None else 'unknown')
        return '/'.join(values)+' USDm'
    common=[
        ('CF','Use source-bound displayed cash movements and independently reconciled consolidated CFO, without a separate CFO residual operation.',nums('cfo'),
         'Supporting movements already in CFO: no second deduction, book delta NWC or organic/unlevered-cash claim. Alternative separately evidenced allocations; stop at displayed mixed populations, not a balancing plug. AVGO mixed deferred/other noncash taxes stay mixed; note deferred tax is not substituted for that row.'),
        ('SBC','Use separately recognized SBC expense once as a labeled historical cost proxy; retain reconciliation, awards and tax/withholding cash separately.',nums('sbc_expense'),
         'No duplicate charge, rounding plug or forecast dilution. AVGO2024 expense5670 versus addback5741 differs71; preserve acquisition/compensation scope, not an adjustment. TSLA2025 awards/legal vesting conditions remain source uncertainty, not a diluted-share estimate. Alternative retain expense only without an economic-cost selection.'),
        ('CASH','Select gross named CURRENT financial captions only; restrictions, long investments, strategic holdings and finance receivables remain separate.',nums('gross_current_financial',True),
         'Not excess/unrestricted cash. No reserve estimate, absent-investment zero or restricted-cash parent addition. TSLA digital assets and collateral/lessor receivables are not equivalent cash; LLY noncurrent investments include strategic holdings. Alternative defer liquid-balance operation; omitted restrictions/reserves unbounded.'),
        ('CLAIMS','Retain named recognized NCI/redeemable claims and benefit-plan populations separately; propose no additional unidentified preferred/NCI/pension adjustment beyond those known disclosures.',
         'NCI '+nums('nci')+'; redeemable '+nums('redeemable_nci'),
         'Presentation-based analyst assumption, not reported zero or immateriality; undisclosed exposure unbounded. Never omit identified pension liabilities/strategic assets or add net funded status to its gross assets/liabilities. TSLA nonrecourse consolidated funding and NCI are different populations. Alternative leave additional-claims operation unresolved; no valuation netting.'),
        ('SHARES','Select separately dated common populations, keeping cover dates, class/award boundaries and EPS denominators separate; no automatic restatement/aggregation.',
         'Actual source dates/classes/precision in facts/shares:*; no estimate of dilution.',
         {'AVGO':'2024 ten-for-one split and VMware equity consideration break comparability with original2021–23 observations; preserve original counts, no invented split-restated schedule.',
          'TSLA':'2021 original shares predate2022 three-for-one; retain actual cover date if year-end population is not independently bound.2025 award issuance changes dated counts; weighted averages are not closing shares.',
          'LLY':'Selected annuals supply later dated cover counts; these are not fiscal-end or diluted counts. Awards/performance shares may have different conditions, no automatic award total.'}[t]+' Alternative require a separately designed comparison/award operation, not Phase1 numerical dilution.')]
    specifics={
        'AVGO':[
            ('DA','Select depreciation plus the two separately expensed acquisition-intangible amortization captions as a LIMITED historical proxy.',nums('limited_da_proxy',True),
             'Exclude combined intangible/ROU CFO row5502/4455/3333/9417/8201; it includes operating ROU. Do not add finance amortization16/18/16/27/unknown again or impairments/restructuring. Alternative mixed CFO proxy6041/4984/3835/10010/8775 is broader by99/96/86/150/139; not pure D&A. Complete expense coverage/overlap still unproved.'),
            ('INV','Keep cash PP&E separate from acquisition consideration, noncash ROU, unpaid capex and restructuring; no complete reinvestment sum.',nums('cash_capex')+'; acquisition cash '+nums('acquisition'),
             'VMware closes in FY2024:25978 net acquisition cash is not ordinary cash PP&E548; acquired intangibles are not a new PP&E allocation.53-week FY2024 and integration/held-sale populations affect comparability; no organic normalization. Alternative broader acquisition-inclusive investment requires explicit purpose/allocations, not accepted here.'),
            ('FIN','Select named current/noncurrent debt CARRYING captions including embedded finance leases, operating leases service; propose no additional unidentified-borrowing adjustment.',nums('named_financing',True),
             '2021 note parent39665 excludes finance65; face39730 includes it.2022–25 parent current/noncurrent already finance-inclusive: do not add finance59/49/39/unknown.2025 face65136 differs principal67120; retain discounts/hedge/fair-value observations, not a plug. Source non-disclosure is not zero; omission unbounded. Alternative additional borrowing operation unresolved.')],
        'TSLA':[
            ('DA','Select the displayed impairment-inclusive CFO row as a LIMITED historical proxy, explicitly not pure expense D&A.',nums('limited_da_proxy',True),
             'Includes manufacturing, energy, leased vehicles/solar and impairment; complete source D&A remains unproved and frozen negative scope is unchanged. Depreciation1910/2420/3330/4120/5030 and finance amort415/493/506/409/118 are SUPPORT, not incremental. Alternative depreciation-only omits other amortization/leased populations; do not infer residual amortization.'),
            ('INV','Retain exact originally selected PP&E cash caption, including any stated net-of-sales scope; keep leased-vehicle movement and noncash equipment separate.',nums('cash_capex'),
             '2025 caption explicitly net of sales; original2024/2023 amounts11339/8898 differ later11342/8899 comparatives. Do not silently restate. Noncash finance additions486/58/10/144/0 and operating additions818/1059/2170/1808/1643 are not cash. Accrued purchases are mixed, not a pure unpaid-capex allocation. Alternative broader leased-asset investment requires sourced non-overlap, no new sum.'),
            ('FIN','Use consolidated manufacturing/energy/leasing perimeter, named face debt+finance carrying captions, with operating lessee leases service; retain financing assets and related funding, not a netted industrial-only view.',nums('named_financing',True),
             'Nonrecourse lending/vehicle/solar funding remains alongside related assets and NCI; no separate captive carve-out inferred by subtraction. LongTermDebt tag alone is NONCURRENT here, not whole debt; note principal/fair value/capacity are alternatives. Finance1492/1054/573/335/223 already inside face subtotal; no second add. Propose no unidentified-borrowing adjustment, unbounded omission; alternative a separately sourced narrower operating perimeter, not automatically substituted.'),
            ('TAX','Select exact face-statement provision with existing pretax/reported accounting tax context; preserve competing rounded candidates and original generic conflicts.',nums('face_tax')+'; cash net (IncomeTaxesPaidNet tag) '+nums('cash_tax')+'; cash net (IncomeTaxesPaid tag) '+nums('cash_tax_gross'),
             '2023 valuation-allowance release makes provision negative; no rate clamp, rounding adjustment, forecast rate or tax-shield operation. Actual earlier cash caption says net of refunds despite IncomeTaxesPaid tag; retain that scope without rewriting original ledger. Alternative keep generic conflict unresolved; any new denominator/economic rate requires separate approval.')],
        'LLY':[
            ('DA','Use CFO D&A as a LIMITED historical proxy; preserve depreciation and finite-lived intangible expense separately.',nums('limited_da_proxy',True),
             'Expense components do not prove complete non-overlap or justify a new sum; no acquired/IPR&D, impairment or ROU add-on and no balancing amortization. Alternative retain component observations without proxy selection.2025 USDm rounding versus earlier0.1m affects comparability.'),
            ('INV','Retain reviewed refreshed-evidence cash PP&E under unchanged original policy; keep cash IPR&D/licensing, asset acquisitions and expense IPR&D separately.',nums('other_ppe_cash')+'; cash IPRD '+nums('iprd_cash')+'; expensed IPRD '+nums('iprd_expense'),
             'Prior fingerprints remain mismatched/unavailable; original byte equivalence UNPROVED, independently reviewed refresh is the basis.2022 expense908.5 includes development milestones; CFO acquired-IPRD420.9 is a different population, difference487.6 NOT an adjustment. Cash IPRD and expensed IPRD differ in timing/recognition; do not reverse EBIT charge or double-count CFO addback. Acquisition/licensing/success milestones not exhaustive ordinary capex; alternative explicit broader investment contract needs sourced allocations, no new equation.'),
            ('FIN','Select combined short-borrowing/current maturities plus noncurrent carrying debt, operating leases service; finance leases already embedded, no added estimate.',nums('named_financing',True),
             'Do not add CP0/1498/6189.4/4337.6/0 or gross long-note principal again. Source says finance leases embedded/not material to financial statements, not valuation immateriality; missing amount stays unknown. Propose no additional unidentified-borrowing adjustment, unbounded omission. Alternative leave that operation unresolved; current maturities not duplicated.')]
    }[t]
    return [dict(decision_id=t+'-'+key,ticker=t,identities=[r['identity'] for r in p['periods']],
        recommendation=rec,numerical_effect=number,uncertainty_and_alternative=limit,
        status=PROPOSED,accepted=False,author=p['review_author'],recorded_at_utc=REVIEW_TIME,
        evidence_references=[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)])
        for key,rec,number,limit in common+specifics]


def outputs():
    packages, missing = build()
    import activate_company_review_batches as accepted
    packages={t:accepted.load_if_approved(f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json',p,decisions(p)) for t,p in packages.items()}
    summary=dict(schema='retained-large-company-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),
        selected_periods=15,family_slots=210,companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},
        decisions=[d for t in TICKERS for d in decisions(packages[t])],evidence_acquisition_requirements=missing,
        new_sec_requests=0,new_assumptions_active=False,completed_company_packages=8,
        approved_partial_company_packages=1,pending_review_company_packages=3,broad_assessment_only=30,phase1_closed=False)
    activation=accepted.summary_activation(packages)
    if activation:
        activation['current_company_counts']=dict(broadly_assessed=42,completed_scoped=8+sum(p['current_history']['company_completed_for_approved_historical_perimeter'] for p in packages.values()),approved_partial=1+sum(not p['current_history']['company_completed_for_approved_historical_perimeter'] for p in packages.values()),pending_reviews=0,assessment_only=30)
        summary['approval_activation']=activation
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},SUMMARY:summary}


if __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,payload in result.items():
            if (ROOT/path).read_text()!=json.dumps(payload,sort_keys=True,indent=2)+'\n':
                raise SystemExit('Company batch replay differs: '+path)
        print('Exact AVGO/TSLA/LLY replay:15 selected periods/210 family slots; '+('approved effective views present' if 'approval_activation' in result[SUMMARY] else 'proposals inactive'))
    else:print(json.dumps(result,sort_keys=True,indent=2))
