"""Apple's explicitly approved analyst consumer; reported facts remain immutable.

This is a valuation-use contract, not an exact cash reconstruction certificate.
All financial execution delegates to the existing operating and FCFE engines.
"""
from copy import deepcopy
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
import hashlib
import json

from valuation_platform.valuation.case_inputs import CaseInputError, _strict_json, read_case, run_case
from valuation_platform.valuation.discounting import TerminalAssumptions
from valuation_platform.valuation.fcfe import keys, number, run_fcfe
from .apple_operating_history import read_overlay

RESOURCE = 'docs/company-resolutions/AAPL/analyst-ready-2026-11-04/policy.json'
PIN = '10d68a552bf1e6a6ec2e381dd0cece81b376bfbf34ff6ce98bfc343ce75b4757'
SCHEMA = 'apple-analyst-request-v1'
READY = 'ANALYST_READY_WITH_QUALIFICATIONS'
DEFAULTS = {'operating_cash_reserve_ratio': '0.02', 'cost_of_equity': '0.08935',
            'pre_tax_cost_of_debt': '0.0565', 'rsu_vesting_fraction': '1',
            'additional_claims_usd': '0', 'historical_other_financing_fraction': '0'}


def read_apple_analyst(text):
    doc = _strict_json(text)
    keys(doc, ('schema_version', 'base_case', 'assumptions'), 'apple_analyst')
    if doc['schema_version'] != SCHEMA:
        raise CaseInputError(['apple_analyst: unsupported schema'])
    case = read_case(json.dumps(doc['base_case']))
    if (case.assumptions.company_cik != 320193 or doc['base_case']['anchor']['kind'] != 'aapl-fy2025'
            or doc['base_case']['anchor']['annual_end'] != '2025-09-27' or case.bridge is not None):
        raise CaseInputError(['base_case: Apple FY2025 operating case without a manual equity bridge required'])
    if type(case.terminal) is not TerminalAssumptions:
        raise CaseInputError(['base_case: perpetual growth with independent terminal inputs required'])
    keys(doc['assumptions'], DEFAULTS, 'assumptions')
    for key, value in doc['assumptions'].items():
        maximum = Decimal('1000000000000') if key == 'additional_claims_usd' else Decimal(1)
        minimum = Decimal('0.000001') if key == 'cost_of_equity' else Decimal(0)
        number(value, 'assumptions.' + key, minimum=minimum, maximum=maximum)
    growth = case.assumptions.terminal_growth
    if growth >= Decimal(doc['assumptions']['cost_of_equity']):
        raise CaseInputError(['cost_of_equity: must exceed terminal growth'])
    return doc


def read_policy(root):
    body = (root / RESOURCE).read_bytes()
    if hashlib.sha256(body).hexdigest() != PIN:
        raise ValueError('Apple analyst policy differs from reviewed source pin')
    policy = json.loads(body)
    if policy['schema_version'] != 'apple-analyst-policy-v1' or policy['ticker'] != 'AAPL' or policy['defaults'] != DEFAULTS:
        raise ValueError('Incompatible Apple analyst policy')
    actual = read_overlay(root)['periods']
    if len(policy['historical']) != 5:
        raise ValueError('Five Apple annuals required')
    for i, (p, old) in enumerate(zip(policy['historical'], actual, strict=True)):
        if p['fiscal_year'] != 2021 + i or p['identity'] != old['identity'] or p['fcff_usd'] != old['fcff']['amount_usd']:
            raise ValueError('Apple historical identities or operands changed')
    return policy


def analyst_history(policy, other_fraction):
    """Unknown financing is excluded by assumption, never reclassified as a fact."""
    result = []
    for p in policy['historical']:
        fcfe = (Decimal(p['cfo_usd']) - Decimal(p['cash_ppe_usd'])
                + Decimal(p['identified_net_borrowing_usd']) + other_fraction * Decimal(p['other_financing_usd']))
        result.append({**{k: p[k] for k in ('fiscal_year', 'identity', 'fcff_usd', 'other_financing_usd', 'source_urls')},
                       'cfo_usd': p['cfo_usd'], 'cash_ppe_usd': p['cash_ppe_usd'],
                       'identified_net_borrowing_usd': p['identified_net_borrowing_usd'],
                       'sbc_usd': p['sbc_usd'], 'fcfe_usd': str(fcfe),
                       'economic_fcfe_usd': str(fcfe - Decimal(p['sbc_usd'])),
                       'classification': 'STANDARDIZED_IDENTIFIED_FUNDING_FCFE_ESTIMATE',
                       'exact_full_fcfe_verified': False,
                       'historical_other_financing_fraction': str(other_fraction)})
    return result


def funding_request(base_case, operating, assumptions, opening_debt):
    """Flat explicit net debt, then debt grows with the Gordon state.

    Gross maturity refinancing is netted, not forecast as a company debt schedule.
    One percent of estimated cash PP&E is financed, matching the existing Apple
    investment overlay (1/101 of total investment), and repaid in aggregate once.
    """
    debt = opening_debt; kd = Decimal(assumptions['pre_tax_cost_of_debt'])
    rows = []
    for i, row in enumerate(operating['stage_b']['stage_a']['years'], 1):
        financed = Decimal(row['investment']) / Decimal(101)
        rows.append({'period_index': i, 'interest_expense_usd': str(debt * kd),
                     'cash_debt_issued_usd': '0', 'new_finance_asset_funding_usd': str(financed),
                     'principal_repaid_usd': str(financed)})
    terminal = operating['stage_b']['terminal']; growth = read_case(json.dumps(base_case)).assumptions.terminal_growth
    financed = Decimal(terminal['investment']) / Decimal(101)
    net = debt * growth
    return {'schema_version': 'fcfe-forecast-request-v1', 'base_case': base_case,
            'scope': 'DECLARED_PARENT_COMMON', 'cost_of_equity': assumptions['cost_of_equity'],
            'opening_debt_usd': str(debt), 'financing_years': rows, 'terminal_growth': str(growth),
            'terminal_financing': {'interest_expense_usd': str(debt * kd),
                                   'cash_debt_issued_usd': str(max(net, Decimal(0))),
                                   'new_finance_asset_funding_usd': str(financed),
                                   'principal_repaid_usd': str(financed + max(-net, Decimal(0)))}}


def equity_bridge(ev, operating_equity, facts, anchor_revenue, assumptions, *, book_debt=False):
    value = lambda k: Decimal(facts[k]['value'])
    cash = sum((value(k) for k in ('CashAndCashEquivalentsAtCarryingValue', 'MarketableSecuritiesCurrent', 'MarketableSecuritiesNoncurrent')), Decimal(0))
    reserve = anchor_revenue * Decimal(assumptions['operating_cash_reserve_ratio'])
    if reserve > cash:
        raise CaseInputError(['operating_cash_reserve_ratio: implied reserve exceeds observed cash and securities'])
    lease = value('FinanceLeaseLiabilityCurrent') + value('FinanceLeaseLiabilityNoncurrent')
    term = value('LongTermDebtCurrent') + value('LongTermDebtNoncurrent') if book_debt else value('term_debt_fair_value')
    debt = term + value('CommercialPaper') + lease
    shares = value('dated_common_shares') + value('unvested_rsus') * Decimal(assumptions['rsu_vesting_fraction'])
    claims = Decimal(assumptions['additional_claims_usd']); eligible = cash - reserve
    fcff_equity = ev + eligible - debt - claims
    # Financing, including principal and interest, already enters discounted FCFE.
    fcfe_equity = operating_equity + eligible - claims
    if shares <= 0 or min(fcff_equity, fcfe_equity) <= 0:
        raise CaseInputError(['analyst equity: positive equity and dated shares required'])
    return {'gross_cash_usd': str(cash), 'operating_reserve_usd': str(reserve),
            'eligible_cash_usd': str(eligible), 'debt_claims_usd': str(debt),
            'additional_claims_usd': str(claims), 'valuation_shares': str(shares),
            'fcff_equity_value_usd': str(fcff_equity), 'fcfe_equity_value_usd': str(fcfe_equity),
            'fcff_value_per_share_usd': str(fcff_equity / shares),
            'fcfe_value_per_share_usd': str(fcfe_equity / shares),
            'debt_subtracted_after_fcfe_discounting': False,
            'debt_basis': 'CARRYING_VALUE_ALTERNATIVE' if book_debt else 'TERM_FAIR_VALUE_CP_AND_FINANCE_LEASE_CARRYING_PROXY',
            'shares_basis': 'DATED_COMMON_PLUS_EXPECTED_EXISTING_RSU_VESTING',
            'operating_lease_debt_deduction_usd': '0', 'separate_existing_rsu_claim_deduction_usd': '0'}


def run_apple_analyst(doc, root):
    doc = read_apple_analyst(json.dumps(doc))
    policy = read_policy(root)
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        return _run(doc, policy, root)


def _run(doc, policy, root):
    assumptions = doc['assumptions']; base = doc['base_case']
    operating = run_case(read_case(json.dumps(base)), root)
    stage = operating['stage_b']; ev = Decimal(stage['enterprise_value'])
    anchor_revenue = Decimal(stage['stage_a']['anchor']['revenue'])
    facts = policy['facts']
    book_debt = sum((Decimal(facts[k]['value']) for k in ('LongTermDebtCurrent', 'LongTermDebtNoncurrent', 'CommercialPaper', 'FinanceLeaseLiabilityCurrent', 'FinanceLeaseLiabilityNoncurrent')), Decimal(0))
    financing = funding_request(base, operating, assumptions, book_debt)
    fcfe = run_fcfe(financing, root)
    operating_equity = Decimal(fcfe['equity_value_usd'])
    bridge = equity_bridge(ev, operating_equity, facts, anchor_revenue, assumptions)
    sensitivities = []
    def sensitivity(label, replacement=None, *, book=False, equity=None, value=ev):
        a = {**assumptions, **(replacement or {})}
        b = equity_bridge(value, operating_equity if equity is None else equity, facts, anchor_revenue, a, book_debt=book)
        sensitivities.append({'label': label, 'classification': 'ILLUSTRATIVE_ANALYST_SENSITIVITY_NOT_A_BOUND',
                              **{k: b[k] for k in ('fcff_value_per_share_usd', 'fcfe_value_per_share_usd')}})
    sensitivity('No operating cash reserve', {'operating_cash_reserve_ratio': '0'})
    sensitivity('Operating cash reserve 5% of anchor revenue', {'operating_cash_reserve_ratio': '0.05'})
    sensitivity('Debt bridge at carrying value; FCFE financing held fixed', book=True)
    sensitivity('No existing RSU vesting', {'rsu_vesting_fraction': '0'})
    sensitivity('Additional claim stress of 23.242B; not an exposure bound', {'additional_claims_usd': str(Decimal(assumptions['additional_claims_usd']) + Decimal('23242000000'))})
    higher_ke = deepcopy(financing); higher_ke['cost_of_equity'] = str(Decimal(assumptions['cost_of_equity']) + Decimal('0.01'))
    if Decimal(higher_ke['cost_of_equity']) <= 1:
        sensitivity('Cost of equity +1 percentage point; FCFF WACC held fixed', equity=Decimal(run_fcfe(higher_ke, root)['equity_value_usd']))
    higher_wacc = deepcopy(base); higher_wacc['wacc'] = str(Decimal(base['wacc']) + Decimal('0.01'))
    if Decimal(higher_wacc['wacc']) <= 1:
        sensitivity('FCFF WACC +1 percentage point; FCFE cost of equity held fixed', value=Decimal(run_case(read_case(json.dumps(higher_wacc)), root)['stage_b']['enterprise_value']))
    readiness = [
        ('historical_fcff', 'Historical FCFF · five years', 'Five reproducible standardized EBIT/NWC calculations; reported D&A and tax conventions retained.'),
        ('fcff_valuation', 'FCFF forecast and enterprise value', 'Selected operating forecast, WACC and terminal inputs calculate; history is context, not automatic calibration.'),
        ('historical_fcfe', 'Historical FCFE · five years', 'Identified-funding CFO-based estimates under the explicit Other-financing exclusion policy; economic SBC variant shown separately.'),
        ('fcfe_valuation', 'FCFE forecast and equity value', 'Explicit net-debt rollover, matched financed investment, interest, terminal financing and cost of equity calculate.'),
        ('per_share', 'Fair value per share · both methods', 'Date-matched cash/debt/shares plus disclosed reserve, RSU and additional-claim assumptions; debt deducted only in FCFF bridge.'),
    ]
    qualifications = [
        'Analyst-ready means usable under these disclosed assumptions; it does not certify exact historical cash flows or a market trading recommendation.',
        'Analytical origin 2025-09-27 uses later-filed information. This is not a current-date valuation or contemporaneous backtest; no current-price upside claim is made.',
        'Historical FCFE = reported CFO - cash PP&E + identified term-debt/CP net borrowing. The chosen fraction of net Other is an assumption; unknown gross financing and lease principal remain unidentified. No extra guessed principal deduction is made.',
        'The economic FCFE companion subtracts reported SBC from CFO-based FCFE. Historical FCFF, CFO-based FCFE and forward operating cash flows still have different tax, noncash and investment populations; no automatic cross-basis CAGR or calibration.',
        'Reported combined D&A is retained. The FY2024 355M note difference is a source qualification; it has zero forecast valuation impact when forward inputs are held fixed and history calibration is disabled.',
        'Historical current taxes remain within the defined NWC convention. Forward tax and working capital are independent normalized analyst assumptions, not issuer-certified operating cash taxes.',
        'Explicit forecast financing debt stays at carrying value by net rollover. Interest equals the assumed debt cost times opening carrying debt. Matching new financed assets and principal are included once; no gross maturity schedule or repurchase-driven share shrinkage is predicted.',
        'FCFF uses the submitted WACC (saved Base targets 15% debt); FCFE uses the submitted cost of equity and flat explicit debt. These are different financing assumptions, so the two valuations need not match. Their difference is quantified, not forced away.',
        'The operating cash reserve is an analyst liquidity haircut, not an observed Apple requirement. Future operating margins and working-capital drivers are assumed inclusive of ongoing operational liquidity costs.',
        'Term debt uses disclosed fair value; CP and finance leases use carrying proxies. Operating leases remain service expenses and are not deducted as debt again. Compare the carrying-debt sensitivity.',
        'Existing unvested RSUs enter expected shares; future compensation remains in operating margins as a future-grant expense proxy. No separate settlement of the same RSUs, grant-date value deduction, exercise proceeds or future-cost cash deduction is added. Vesting assumptions are editable.',
        'Zero additional non-operating claims is a base-case assumption, not evidence of no exposure. Ordinary tax/legal settlements are assumed captured by forecast expenses and taxes; do not deduct the already-settled Ireland escrow again. The 23.242B claim stress is illustrative, not a proven maximum.',
        'Small net Other is not a bound on potentially offsetting gross financing. Changing its allocation only stress-tests the disclosed net caption; it does not establish exact historical FCFE.',
    ]
    return {'schema_version': 'apple-analyst-result-v1', 'ticker': 'AAPL',
            'policy_version': policy['version'], 'model_origin': policy['anchor_date'],
            'submitted_inputs': doc, 'assumptions': assumptions,
            'readiness': [{'id': k, 'label': label, 'status': READY, 'detail': detail} for k, label, detail in readiness],
            'historical': analyst_history(policy, Decimal(assumptions['historical_other_financing_fraction'])),
            'fcff': {'enterprise_value_usd': str(ev), 'equity_value_usd': bridge['fcff_equity_value_usd'],
                     'value_per_share_usd': bridge['fcff_value_per_share_usd'], 'wacc': base['wacc']},
            'fcfe': {'operating_equity_value_usd': str(operating_equity), 'equity_value_usd': bridge['fcfe_equity_value_usd'],
                     'value_per_share_usd': bridge['fcfe_value_per_share_usd'], 'cost_of_equity': assumptions['cost_of_equity'],
                     'years': fcfe['years'], 'terminal': fcfe['terminal'],
                     'pv_explicit_fcfe_usd': fcfe['pv_explicit_fcfe_usd'], 'pv_terminal_equity_usd': fcfe['pv_terminal_equity_usd'],
                     'financing_inputs': financing, 'debt_subtracted_after_fcfe_discounting': False},
            'bridge': bridge, 'valuation_difference_fcfe_minus_fcff_usd': str(Decimal(bridge['fcfe_equity_value_usd']) - Decimal(bridge['fcff_equity_value_usd'])),
            'qualifications': qualifications, 'sensitivities': sensitivities,
            'historical_other_allocation_stress': [{'fiscal_year': p['fiscal_year'], 'default_fcfe_usd': p['fcfe_usd'],
                'all_net_other_as_financing_fcfe_usd': str(Decimal(p['cfo_usd']) - Decimal(p['cash_ppe_usd']) + Decimal(p['identified_net_borrowing_usd']) + Decimal(p['other_financing_usd'])),
                'is_bound': False} for p in analyst_history(policy, Decimal(assumptions['historical_other_financing_fraction']))],
            'source_urls': sorted(set(u for p in policy['historical'] for u in p['source_urls'])) + policy['methodology_sources'],
            'exact_full_historical_fcfe_claim': False, 'automatic_history_calibration': False,
            'discount_basis': policy['discount_basis']}
