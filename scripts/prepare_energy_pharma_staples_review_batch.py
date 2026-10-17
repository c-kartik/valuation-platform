"""Fixed retained CVX/MRK/PG review. Proposals, not approvals or new policies.

Reuse exact-source inspection, original policy replay and company review models.
The CVX EBIT perimeter exception is deliberately not solved by a new equation.
"""
import json
import re
import sys
from collections import Counter
from decimal import Decimal as D

import prepare_standard_review_batch as shared
import prepare_trillion_review_batch as peer
import prepare_large_company_review_batch as prior
from prepare_priority_review_batch import fiscal_focus
from prepare_msft_analyst_package import ROOT, digest, relevant, PROPOSED
from valuation_platform.analyst import retained_reported_tax as tax_policy
from valuation_platform.analyst import retained_capex as capex_policy
from valuation_platform.analyst import capex_evidence_repair as capex_repair

BASELINE = '956c5c488247eb27ad432b3d1a0fd942a4f29e6e'
REVIEW_TIME = '2026-10-17T21:51:27+00:00'
TICKERS = ('CVX', 'MRK', 'PG')
SUMMARY = 'docs/company-data-preparation/energy-pharma-staples-review-batch.json'
MARKERS = {
    'CVX': ('equity affiliates', 'before-tax', 'depletion', 'Asset Retirement',
            'reclassified', 'Hess', 'PDC', 'Renewable Energy Group',
            'stock-based compensation expense', 'restricted cash', 'pension'),
    'MRK': ('Organon', 'continuing operations', 'Total pretax share-based',
            'relates to continuing', 'accelerated depreciation', 'Pandion',
            'Prometheus', 'Imago', 'Verona', 'cloud computing', 'finance leases'),
    'PG': ('Cash and cash equivalents', 'Finance leases are not material',
           'manufacturing', 'amortization expense', 'Gillette', 'restructuring',
           'Employee Stock Ownership Plan', 'ESOP debt', 'liquidation value',
           'converted from inception', 'funded status', 'Acquisitions')}


def passages(f, ticker):
    out = []
    for marker in MARKERS[ticker]:
        hits = list(re.finditer(re.escape(marker), f.text, re.I))
        for m in dict.fromkeys(hits[:1] + hits[-2:]):
            out.append(dict(marker=marker, offset=m.start(),
                exact_excerpt=f.text[max(0, m.start()-100):m.end()+1800],
                source_sha256=f.primary.artifact.sha256))
    return out


def continuing_cfo(case):
    """Independent MRK displayed rows; original PARTIAL proof stays untouched."""
    f = case['filing']; matches = []
    concepts = ('NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
                'NetCashProvidedByUsedInOperatingActivities')
    for ti, table in enumerate(case['tables']):
        rows = []
        for ri, row in enumerate(table):
            caption = row[0]['text'].strip() if row else ''
            bound = []
            for ci, cell in enumerate(row):
                for item in cell['facts']:
                    try: fact = peer.primary_fact(case, item, ti, ri, ci, caption)
                    except (ValueError, KeyError): continue
                    value = shared.cfo.displayed(cell['text'], D(0)) * D(10)**int(item['attrs'].get('scale', '0'))
                    bound.append(dict(caption=caption, value=str(value), fact=fact))
            if bound: rows.append(bound)
        starts = [i for i, row in enumerate(rows) if row[0]['caption'].lower().startswith('net income')]
        ends = [i for i, row in enumerate(rows) if any(x['fact']['concept'] in concepts for x in row)]
        if not starts or not ends or starts[0] >= ends[0]: continue
        selected = rows[starts[0]:ends[0]+1]
        if any(len(row) != 1 for row in selected): raise ValueError('Ambiguous displayed CFO row')
        selected = [row[0] for row in selected]
        total = sum((D(x['value']) for x in selected[:-1]), D(0))
        diff = total-D(selected[-1]['value'])
        matches.append(dict(status='SUPPORTED' if diff == 0 else 'FAILED',
            rows=selected[:-1], cfo=selected[-1], row_sum=str(total),
            difference=str(diff), tolerance='0', primary_table=ti,
            basis='Independent literal current-year displayed-row check, original parser not replaced',
            scope='Original-as-filed continuing operations through FY2023; root presentation FY2024/25'))
    if len(matches) != 1 or matches[0]['status'] != 'SUPPORTED':
        raise ValueError('One independently exact MRK CFO statement required')
    return matches[0]


def build():
    cases, missing = shared.load(TICKERS); packages = {}
    ledgers = {n: json.loads((ROOT/('docs/'+n+'.json')).read_text())
               for n in prior.LEDGERS + ('retained-bridge-component-ledger', 'retained-tax-sbc-ledger')}
    store = capex_policy.artifacts()
    for key, value in capex_repair.verify(json.loads((ROOT/capex_repair.OUTPUT).read_text())).items():
        store.setdefault(key, value)
    for case in cases:
        t = case['ticker']; f = case['filing']; focus = fiscal_focus(case)
        case['tables'] = shared.documents.parse(case['record'], improved=True)
        errors = shared.observe(case)
        prior.prepare_income(case, prior.ledger_row(ledgers['repaired-income-ledger'], case['identity'])[1])
        def bind(key, concept, instant=False, ns='us-gaap'):
            try: shared.monetary(case, key, concept, instant, ns)
            except (ValueError, KeyError) as exc:
                errors.append(dict(input_id=key, value=None, reason=str(exc),
                    disposition='Unselected/absent binding; not zero or proof of absent disclosure'))
        def displayed(key, concept, captions, instant=False):
            if not peer.displayed_selection(case, key, concept, captions, instant=instant):
                errors.append(dict(input_id=key, value=None, reason='Exact reviewed displayed population unavailable'))
        extra = {**prior.EXTRA, 'combined_da': ('DepreciationAndAmortization', False),
            'productive_cash': ('PaymentsToAcquireProductiveAssets', False),
            'amortization_cfo': ('AdjustmentForAmortization', False),
            'asset_retirement': ('AssetRetirementObligation', True),
            'pension_noncurrent': ('DefinedBenefitPensionPlanLiabilitiesNoncurrent', True),
            'debt_fair_value': ('LongTermDebtFairValue', True),
            'redeemable_nci': ('RedeemableNoncontrollingInterestEquityCarryingAmount', True)}
        for key, (co, inst) in extra.items(): bind(key, co, inst)
        if t == 'CVX':
            displayed('face_revenue', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                ('Sales and other operating revenues', 'Sales and other operating revenues (1)'))
            # Direct eligible sales are independently bound even when the footnote
            # marker changes the face caption. Broader Revenues remains alternative.
            if 'face_revenue' not in f.facts: bind('face_revenue', 'RevenueFromContractWithCustomerExcludingAssessedTax')
            bind('broader_revenue', 'Revenues')
            if f.year == 2021:
                bind('face_cash', 'CashandCashEquivalentsExcludingTimeDepositsatCarryingValue', True, 'cvx')
            elif f.year >= 2024:
                bind('face_cash', 'CashAndCashEquivalentsExcludingTimeDeposits', True, 'cvx')
            else: bind('face_cash', 'CashAndCashEquivalentsAtCarryingValue', True)
            bind('named_sbc_expense', 'CompensationExpenseForStockAppreciationRightsRestrictedStockPerformanceUnitsAndRestrictedStockUnits', ns='cvx')
        if t == 'MRK':
            bind('continuing_cfo', 'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations')
            bind('discontinued_cfo', 'CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations')
            displayed('face_current_borrowing', 'DebtCurrent', ('Loans payable and current portion of long-term debt',), True)
            # CFO source and recognized expense are separate roles even when equal.
            pattern = (r'Total pretax share-based compensation expense(?: from continuing operations)? was \$\s*([\d,]+)\s*million in\s*'+str(f.year)
                       if f.year < 2025 else r'Total pretax share-based compensation cost recorded in 2025, 2024 and 2023 was \$\s*([\d,]+)\s*million')
            hits = list(re.finditer(pattern, f.text))
            if len(hits) != 1: raise ValueError('Exact continuing expense prose not unique '+str(f.year))
            m = hits[0]
            f.facts['continuing_sbc_expense'] = dict(value=str(D(m.group(1).replace(',', ''))*1000000),
                unit='USD', precision='-6', origin='reported', as_of=None,
                annual_start=str(f.period.annual_start), annual_end=str(f.period.annual_end),
                representation='primary_note_prose_not_XBRL', occurrences=[], occurrence_count=0,
                scope='Explicit continuing-operation expense, not consolidated498 or an inferred allocation',
                note_evidence=dict(offset=m.start(), exact_excerpt=m.group(), source_sha256=f.primary.artifact.sha256,
                    raw_display=m.group(1).replace(',', ''), display_scale=6))
        if t == 'PG':
            displayed('face_cash', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', ('Cash and cash equivalents',), True)
            displayed('face_current_borrowing', 'DebtCurrent', ('Debt due within one year',), True)
            displayed('named_sbc_expense', 'ShareBasedCompensation', ('Share-based compensation expense',))
            if f.year < 2024: bind('pretax_extension', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxes', ns='pg')
        # Retain plan/class-specific carrying populations, not an invented net sum.
        claim_concepts = ('PreferredStockValue', 'PreferredStockCarryingValue',
            'DefinedBenefitPlanFundedStatusOfPlan', 'DefinedBenefitPlanAmountsRecognizedInBalanceSheet',
            'PensionAndOtherPostretirementDefinedBenefitPlansCurrentLiabilities',
            'PensionAndOtherPostretirementDefinedBenefitPlansLiabilitiesNoncurrent',
            'EmployeeStockOwnershipPlanDebt', 'EmployeeStockOwnershipPlanLiability')
        for concept in claim_concepts:
            seen = set()
            for node in f.root:
                if node.tag.split('}')[-1] != concept or not node.get('contextRef'): continue
                ctx = f.contexts[node.get('contextRef')]
                if ctx.findtext(shared.cash._XI+'period/'+shared.cash._XI+'instant') != str(f.period.annual_end): continue
                dims = tuple((x.get('dimension'), x.text) for x in ctx.iter() if x.tag.endswith('}explicitMember'))
                if dims in seen: continue
                seen.add(dims); key = 'claim:'+concept+':'+digest(dims)[:8]
                try: f.fact(key, concept, 'Exact plan/class carrying population; parent/asset/claim overlap not netted', instant=True, dimensions=dims)
                except ValueError as exc: errors.append(dict(input_id=key, value=None, reason=str(exc)))
        rec = shared.delivery.plain(shared.cfo.inspect_statement(case['evidence'], case['record'], version=shared.cfo.IMPROVED_VERSION))
        if rec != case['proof']['reconciliation']: raise ValueError('Original CFO proof changed')
        manual = continuing_cfo(case) if t == 'MRK' else None
        if manual:
            f.facts['selected_cfo'] = dict(manual['cfo']['fact'])
            for key, concept in [('depreciation_cfo', 'Depreciation'), ('amortization_cfo', 'AdjustmentForAmortization')]:
                exact = [x['fact'] for x in manual['rows'] if x['fact']['concept'] == concept]
                if len(exact) != 1: raise ValueError('One exact displayed continuing D&A component required')
                f.facts[key] = dict(exact[0], selection_rationale='Exact continuing CFO row; segment/note populations remain alternatives')
        else: f.facts['selected_cfo'] = dict(f.facts['cfo'])
        pop = rec['populations'][0]
        detail = manual['rows'] if manual else (pop.get('hierarchy_proof') or {}).get('children', pop['rows'])
        movement_captions = {
            'CVX': ('Net decrease (increase) in operating working capital', 'Decrease (increase) in long-term receivables', 'Net decrease (increase) in other deferred charges'),
            'MRK': ('Accounts receivable', 'Inventories', 'Accounts payable', 'Accrued and other current liabilities', 'Other assets and liabilities', 'Other assets', 'Other liabilities', 'Accounts receivable, net'),
            'PG': ('Change in accounts receivable', 'Change in inventories', 'Change in accounts payable, accrued and other liabilities', 'Change in accounts payable and accrued and other liabilities', 'Change in other operating assets and liabilities', 'Change in accounts payable')}
        movements = [x for x in detail if x['caption'] in movement_captions[t]]
        if t == 'MRK':
            concepts = ('IncreaseDecreaseInAccountsReceivable', 'IncreaseDecreaseInInventories',
                'IncreaseDecreaseInAccountsPayableTrade', 'IncreaseDecreaseInAccruedLiabilities',
                'IncreaseDecreaseInAccruedIncomeTaxesPayable', 'IncreaseDecreaseInOtherOperatingLiabilities',
                'IncreaseDecreaseInOtherOperatingCapitalNet')
            movements = [x for x in detail if x['fact']['concept'] in concepts]
        tax_result, tax_replay = tax_policy.package(case['evidence']); tax_replay['issuer'] = t
        if tax_replay != prior.ledger_row(ledgers['retained-reported-tax-context-ledger'], case['identity'])[1]:
            raise ValueError('Existing reported-tax proof changed')
        capex_replay = None
        if t == 'CVX':
            result, inspection, proof, gaps, entry = capex_policy.replay(case['evidence'], store)
            old = prior.ledger_row(ledgers['refreshed-capex-ledger'], case['identity'])[1]
            if gaps or proof != old['policy'] or D(str(result.value)) != abs(D(old['value_usd'])):
                raise ValueError('Existing CVX Capex approval failed exact replay')
            capex_replay = dict(value=str(result.value), policy=proof, existing_approval=True, gaps=gaps)
        def calc(key, operands, scope, origin='derived'):
            if not operands or any(k not in f.facts for k in operands): return
            f.entry(key, key, operands, status=PROPOSED, scope=scope, origin=origin,
                completeness='partial_named_population_only', rationale='Inactive exact company review, not generic policy or complete coverage')
            f.entries[-1]['formula_version'] = 'energy-pharma-staples-review-v1'
        da_ops = ['depreciation_cfo', 'amortization_cfo'] if t == 'MRK' else ['da']
        calc('limited_da_proxy', da_ops, 'Limited continuing CFO D&A' if t == 'MRK' else 'Depletion-inclusive consolidated energy DD&A, incompatible with unproved industrial EBIT' if t == 'CVX' else 'Manufacturing/corporate CFO D&A, not complete period expense D&A', 'proxy')
        cash_ops = ['face_cash', 'marketable_current'] if t == 'CVX' else ['cash']+(['current_investments'] if 'current_investments' in f.facts else ['marketable_current'] if 'marketable_current' in f.facts else []) if t == 'MRK' else ['face_cash']
        calc('current_financial_captions', cash_ops, 'Gross named financial captions, not unrestricted/excess; cash restriction scope preserved')
        fin_ops = ['short_borrowing', 'debt_finance_long'] if t == 'CVX' else ['face_current_borrowing', 'debt_long']
        calc('named_financing', fin_ops, 'Named carrying captions only; CP/current maturities and embedded finance not added again')
        for key, fact in f.facts.items():
            fact.setdefault('origin', 'reported')
            fact['role'] = 'cfo_reconciliation_observation' if key in ('da','combined_da','depreciation_cfo','amortization_cfo','sbc_addback','deferred_tax','deferred_movement') else 'recognized_expense_observation' if key in ('sbc_expense','named_sbc_expense','continuing_sbc_expense','depreciation','intangible_amortization') else 'separate_reported_observation'
        for error in errors:
            error['binding_disposition'] = ('Initial selector diagnostic; subsequent exact reviewed binding available'
                if error['input_id'] in f.facts else 'Unresolved selector; no absent-to-zero inference')
        refs = {}
        for n, ledger in ledgers.items():
            i, row = prior.ledger_row(ledger, case['identity']); refs[n] = dict(reference='docs/'+n+'.json#/rows/'+str(i), record_sha256=digest(row))
        from valuation_platform.analyst.historical_inputs import Field
        policy = {Field.DA:'DA', Field.CAPEX:'INV', Field.CFO:'CF', Field.CF_WORKING_CAPITAL:'CF', Field.CFO_RESIDUAL:'CF', Field.DEFERRED_TAX:'CF', Field.SBC:'SBC', Field.TAX:'TAX', Field.CASH_INVESTMENTS:'CASH', Field.DEBT_LEASES:'FIN', Field.OTHER_BRIDGE:'CLAIMS', Field.SHARES:'SHARES'}
        checklist = [dict(field=field.value, status='SOURCE_SUPPORTED' if field in (Field.REVENUE,Field.EBIT) else 'PROPOSED_PENDING_APPROVAL', pending_decisions=[] if field in (Field.REVENUE,Field.EBIT) else [t+'-'+policy[field]], financial_complete=False) for field in Field]
        if t == 'CVX':
            for c in checklist:
                if c['field'] == Field.EBIT.value:
                    c.update(status='ESSENTIAL_EXCEPTION', pending_decisions=['CVX-PERIMETER'], reason='BUSINESS_PERIMETER_UNRESOLVED; affiliate mixed tax/financing and incomplete operating benefit allocation')
                elif c['field'] == Field.REVENUE.value:
                    c.update(status='PROPOSED_PENDING_APPROVAL', pending_decisions=['CVX-REV'])
        notes = prior.note_rows(case)
        cfo_table = manual['primary_table'] if manual else pop['table']
        for ti, table in enumerate(case['tables']):
            for ri, row in enumerate(table):
                caption = row[0]['text'].strip() if row else ''
                if ti == cfo_table or re.match(r'^(Debt due|Loans payable|Total|Preferred|Convertible|Reserve for ESOP|SERIES|TOTAL SERIES|Funded status|Net amount recognized|Noncontrolling|Depreciation|Amortization|Capital|Cash paid|Purchases|Acquisitions|Restricted|Non.cash)', caption, re.I):
                    notes.append(dict(table=ti, row=ri, caption=caption, header=' | '.join(c['text'] for rr in table[:3] for c in rr), cells=row, source_sha256=f.primary.artifact.sha256, role='Supporting display including comparative/dimensioned populations, not automatic selection'))
        row = dict(identity=case['identity'], fiscal_year=focus['fiscal_year'], fiscal_year_evidence=focus,
            selection_reference=case['manifest_reference'], prior_population_reference=case['proof_reference'], sources=case['sources'], facts=f.facts,
            calculations=f.entries, derived_ebit=case.get('derived_ebit'), existing_capex_policy_replay=capex_replay,
            source_binding_exceptions=errors, cfo_reconciliation=rec, independent_displayed_cfo=manual,
            movement_rows=movements, reported_tax_policy_replay=tax_replay, supporting_note_rows=notes,
            passages=passages(f,t), preparation_ledger_evidence=refs,
            alternatives={key: peer.candidates(case,key,co,inst) for key,co,inst in [('revenue','Revenues',False),('cash','CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',True),('sbc','ShareBasedCompensation',False),('da','DepreciationDepletionAndAmortization',False),('intangible_amortization','AmortizationOfIntangibleAssets',False)]},
            family_checklist=checklist, new_assumptions_active=False, analyst_complete=False,
            original_supporting_unknowns=dict(complete_expense_da=None, pure_cash_ppe=None, complete_reinvestment=None, additional_unidentified_borrowing=None, unknown_restrictions=None, operating_reserve=None, unidentified_claims=None, complete_lease_cash=None, **({'industrial_ebit':None} if t=='CVX' else {})),
            proposed_selections=dict(revenue='face_revenue' if t=='CVX' else 'revenue', ebit=None if t=='CVX' else 'derived_ebit' if t=='MRK' else 'ebit', cfo='selected_cfo', da='limited_da_proxy', capex='existing_capex_policy_replay' if t=='CVX' else 'productive_cash' if t=='MRK' and f.year<2023 else 'cash_capex', sbc='continuing_sbc_expense' if t=='MRK' else 'named_sbc_expense', pretax='pretax_extension' if t=='PG' and f.year<2024 else 'reported_tax_policy_replay'),
            cash_sign_multipliers={k:-1 for k in ('cash_capex','productive_cash','acquisition','cash_tax','cash_tax_gross','op_cash','finance_principal_cash','finance_interest_cash','iprd_cash','investment_cash') if k in f.facts},
            population_relationships=[dict(parent='named_financing', components=fin_ops, relationship='Nonoverlapping named face captions; CP/current term already children, finance inclusion not inferred from absence'),dict(parent='current_financial_captions', components=['cash_restricted_parent','restricted_current','restricted_noncurrent','equity_method'], relationship='Different populations; no automatic addition or second restriction deduction'),dict(parent='limited_da_proxy', components=['intangible_amortization','finance_amortization'], relationship='No second component/ROU addition or inferred expense completeness'),dict(parent='equity/pension/ESOP', components=['preferred','nci','claim:*'], relationship='Carrying, funded status, plan assets, preferred conversion and financing/reserves overlap; never automatically net/add')])
        packages.setdefault(t,dict(schema='company-analyst-review-v1',version=1,ticker=t,source_commit=BASELINE,review_author='Retained company review; no user acceptance',review_recorded_at_utc=REVIEW_TIME,periods=[],new_assumptions_active=False,analyst_complete=False,phase1_closed=False,valuation_consumption_approved=False))['periods'].append(row)
    for t,p in packages.items():
        p['periods'].sort(key=lambda r:r['identity']['annual_end'])
        p.update(family_slots=70,outcomes=dict(Counter(c['status'] for r in p['periods'] for c in r['family_checklist'])),approval_table_reference=SUMMARY+'#/decisions',evidence_acquisition_requirements=[x for x in missing if x['ticker']==t])
        p['review_revision']=digest(relevant(p))
    return packages,missing


def decisions(p):
    t=p['ticker']
    def nums(key,calc=False):
        values=[]
        for r in p['periods']:
            v=next((x for x in r['calculations'] if x['input_id']==key),{}) if calc else r['facts'].get(key,{})
            values.append(str(D(v['value'])/1000000) if v.get('value') is not None else 'unknown')
        return '/'.join(values)+' USDm'
    da = {'CVX':'Depletion-inclusive energy DD&A; cannot establish compatible industrial EBIT. Retain dry-hole exploration, ARO accretion/settlements, impairments and affiliate distributions separately. Alternative strict matched industrial D&A remains unavailable.',
          'MRK':'Depreciation plus separately reported CFO amortization, excluding separate impairments. Segment depreciation excludes accelerated164/182/203/261/287; do not use a residual or call the proxy complete expense D&A. Manufacturing/inventory timing remains.',
          'PG':'Manufacturing depreciation may be inventoried; SG&A includes corporate D&A. Intangible amortization312/327/338/320/308 is not a second addition to combined D&A. Keep FY2024 Gillette impairment1341, disposal/restructuring rows separate; no normalization adjustment.'}
    inv = {'CVX':'Retain exact five existing curated cash-investment v2 approvals7515/10349/14788/15544/16830 with replayed proof. Do not substitute total capital/exploratory expenditure, affiliate capital budgets or ARO additions. Hess/PDC/REG acquisition and noncash populations stay separate.',
           'MRK':'Select broader continuing capital-expenditures proxy4448/4388 for FY2021/22, not pure PP&E; preserve prior negative scope findings. Later direct PP&E3863/3372/4112. Pandion1556 add-back versus1554 cash; Prometheus10217 versus10705; Imago1192 versus1327; acquired R&D, licensing and acquisitions remain distinct, no allocation or complete reinvestment claim.',
           'PG':'Select direct cash PP&E3156/3062/3322/3773/4409, retaining source capitalized software scope. Acquisition cash1381/765/21/11/85, noncash operating ROU217/213/357/261/168, disposals and creditors remain separate. Alternative broader investment requires defined acquisition/intangible allocation, not a new sum.'}
    cash = {'CVX':'Face cash excludes time deposits/restricted populations; current securities35/223/45/0/0 added once. Restricted current333/630/275/281/174 and noncurrent822/813/822/1200/818 remain separate. Affiliate holdings40357/44610/46113/46618/43037 are strategic, not cash. Alternative broader cash/restricted parent changes scope, not free liquidity.',
            'MRK':'Gross face cash plus disclosed current short-term investments only. FY2021 no independently bound investment zero is inserted. Restricted cash in Other assets remains separate and not deducted twice. Alternative cash-only is a narrower observed perimeter, not an operating reserve estimate.',
            'PG':'Select actual face cash caption, preserving broader cash/restricted QName and unknown restrictions rather than silently treating concepts equivalent. No current investment or unrestricted/excess-cash completeness inferred. Alternative broader liquidity is unavailable without evidenced components.'}
    fin = {'CVX':'Short borrowing plus noncurrent debt/finance captions; CP0/0/0/5386/4642 and finance497/448/634/604/1445 are already children. Note19 reclassification to long-term prevents adding CP again. Different carrying/principal/fair-value measures remain separate.',
           'MRK':'Exact face Loans payable/current debt includes puttable notes, CP and FY2025 foreign facility63; rounded maturity observations are not the face total. Finance subamounts remain unknown, never zero. No ending borrowing from net financing flows.',
           'PG':'DebtCurrent includes CP/current maturities/other short debt; add only noncurrent debt. Do not add4805/6236/3327/4108/4837 CP again. FY2025 child sum9512 versus face9513 differs−1m; FY2026 child sum11297 versus face11296 differs+1m. Preserve these unexplained differences: no plug or inferred rounding explanation, and do not replace the selected face parent with a component sum. Source finance-leases-not-material language does not prove zero or valuation immateriality. ESOP funding/reserve overlaps require no second debt addition.'}
    claims = {'CVX':'Retain ARO12808/12701/13833/12667/14988; noncurrent pension/benefit6248/4357/4082/3857/4111; NCI873/960/972/839/5726 and redeemable populations without adding equity parents/children twice. Pension noncurrent carrying is not full funded status. No industrial EBIT perimeter is repaired by this omission proposal.',
              'MRK':'Retain NCI73/67/54/59/56, pension assets/liabilities/funded status by plan and known litigation/tax claims. Original-as-filed Organon continuing panels preserve acquisition/separation scope; no recast splice or claim allocation.',
              'PG':'Retain ESOP convertible preferred, NCI265/288/272/272/230, plan funded statuses and noncurrent pension3139/3116/2884/3026/2204. ESOP preferred is also plan funding; reserves/Company advances and guaranteed debt overlap. SeriesA/B one-for-one conversion and diluted EPS convention do not authorize a valuation deduction or share aggregation. Do not approve no-preferred treatment.'}
    rows=[('CF','Select reported movement detail and independently reconciled CFO under original-as-filed scope; no separately computed residual or second movement deduction.',nums('selected_cfo'),'MRK original PARTIAL5 remains alongside independent exact continuing/root checks; FY2021 discontinued CFO987 is separate. Cash movements are not book delta NWC, operating-only cash NWC or FCFF. Mixed rows remain visible.'),
          ('DA','Use explicitly limited historical D&A proxy, not verified complete expense D&A.',nums('limited_da_proxy',True),da[t]),
          ('INV',inv[t], '7515/10349/14788/15544/16830 USDm' if t=='CVX' else nums('productive_cash')+' broader first2; direct '+nums('cash_capex'),'Payment magnitudes; cash sign−1. Noncash, acquisition/IPR&D, incentives and creditor timing remain separate. No generic policy expansion or complete reinvestment sum.'),
          ('SBC','Select source expense as a labeled cost proxy once, preserving add-back/award/capitalization roles.',nums('continuing_sbc_expense' if t=='MRK' else 'named_sbc_expense')+'; CFO add-back '+nums('sbc_addback'),'CVX liability-award remeasurement benefit−100 stays negative; named extension scope is explicit. MRK2021 total498 versus continuing479 differs19, not an allocation inferred by subtraction. PG exact face caption is expense; absence of Allocated tag does not mean absent cost. No duplicate charge.'),
          ('TAX','Retain original provision, cash/deferred roles and unchanged approved policy Pretax/ETR. PG first2 explicit pretax-extension selection proposed.',nums('tax')+' provision; pretax extension '+nums('pretax_extension'),'CVX affiliate after-tax/before-tax incompatibility remains an EBIT exception. MRK tax follows continuing panels. PG2022/23 exact pg extension17995/18353 has independent face confirmation; generic policy nulls stay. Issuer reported rates retained without new ratio, future rate or tax-scope equivalence.'),
          ('CASH','Select named gross current financial captions, not unrestricted/excess cash.',nums('current_financial_captions',True),cash[t]+' Unknown restrictions/reserves remain unquantified. No immateriality finding.'),
          ('FIN','Treat operating leases as service cost and finance leases as asset financing; select named carrying financing with no additional unidentified-borrowing adjustment only if approved.',nums('named_financing',True),fin[t]+' Potential omitted exposure unbounded. Alternative retain unidentified operation unresolved; not complete debt or reported zero.'),
          ('CLAIMS','Retain known claim/asset populations without overlap; propose no additional unidentified claim or separate pure-NOL adjustment beyond disclosed populations.', 'Source-bound claims retained, no bridge/valuation calculation.',claims[t]+' Additional unknown claim amounts are unbounded; no non-disclosure/audit immateriality inference. Alternative leave omission operation unresolved.'),
          ('SHARES','Retain actual dated common/class observations, preferred conversions, EPS denominators and awards separately; no class/dilution sum.', 'Exact source counts/dates/precision in shares:*; no numerical dilution assumption.','MRK Jan31 cover observations are not fiscal-end counts. PG common closing shares coexist with ESOP preferred and actual later covers; diluted EPS is an annual average. CVX Hess2025 consideration changes comparability. Alternative cover or recast history requires explicit different date/scope, never silent replacement.')]
    if t=='MRK': rows.insert(0,('PERIMETER','Select original-as-filed continuing-operation panels FY2021–23 and root presentation FY2024–25; retain Organon separately.', 'Continuing CFO13122/19095/13006; root21468/16472, not FY2021 implied consolidated14109.','Approved EBIT derivations, continuing sales, taxes, CFO D&A and Capex align in retained statements. FY2021 broader SBC498 alternative is not selected; independent continuing expense479. Acquisition/separation comparability persists, no recast splice.'))
    if t=='CVX':
        rows.insert(0,('REV','Select explicit face Sales and other operating revenues, preserving broader Revenues alternative and unchanged generic conflict.',nums('face_revenue')+'; broader '+nums('broader_revenue'),'Sales selection does not solve affiliate/industrial operating perimeter. Alternative broader revenue includes non-sales/affiliate income and changes intended scope.'))
        rows.append(('PERIMETER','OPEN essential EBIT/business-perimeter exception: retain required EBIT null for all five years; do not approve an incomplete industrial equation.', 'No defensible EBIT numerical selection established.','Mixed-tax affiliate earnings, operating/nonoperating Other and incomplete benefit allocation prevent exact approved operating perimeter. Neither Pretax+interest, segment after-tax income nor expressionC with unknown U_operating is a substitute. Requires a defensible matched historical operation and explicit scope approval; no specific missing artifact proved, no automatic research queue.'))
    return [dict(decision_id=t+'-'+key,ticker=t,identities=[r['identity'] for r in p['periods']],recommendation=rec,numerical_effect=num,uncertainty_and_alternative=alt,status='OPEN_ESSENTIAL_EXCEPTION' if key=='PERIMETER' and t=='CVX' else PROPOSED,accepted=False,author=p['review_author'],recorded_at_utc=REVIEW_TIME,evidence_references=[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json#/periods/{i}' for i in range(5)]) for key,rec,num,alt in rows]


def outputs():
    packages,missing=build()
    summary=dict(schema='retained-energy-pharma-staples-review-batch-v1',source_commit=BASELINE,tickers=list(TICKERS),selected_periods=15,family_slots=210,companies={t:dict(periods=5,outcomes=p['outcomes'],review_revision=p['review_revision']) for t,p in packages.items()},decisions=[d for t in TICKERS for d in decisions(packages[t])],evidence_acquisition_requirements=missing,new_sec_requests=0,new_assumptions_active=False,completed_company_packages=22,approved_partial_company_packages=2,pending_review_company_packages=3,broad_assessment_only=15,phase1_closed=False,valuation_consumption_approved=False)
    return {**{f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json':p for t,p in packages.items()},SUMMARY:summary}


if __name__=='__main__':
    result=outputs()
    if '--check' in sys.argv:
        for path,payload in result.items():
            if (ROOT/path).read_text()!=json.dumps(payload,sort_keys=True,indent=2)+'\n': raise SystemExit('Review differs: '+path)
        print('Exact CVX/MRK/PG replay:15 annuals/210 families; proposals inactive, CVX EBIT5 OPEN')
    else: print(json.dumps(result,sort_keys=True,indent=2))
