"""Explicit financing bridge and equity discounting, separate from FCFF/WACC.

Manual forecasts are assumptions, not historical disclosure certification.
Taxes follow the existing positive-income convention; no loss tax credit is
invented. Finance-asset funding offsets matching investment once, while its cash
principal is included in aggregate debt repayment once.
"""
from decimal import Context, Decimal, localcontext, ROUND_HALF_EVEN
import json

from .case_inputs import CaseInputError, _strict_json, read_case, run_case

SCHEMA = 'fcfe-forecast-request-v1'
FIELDS = ('interest_expense_usd', 'cash_debt_issued_usd', 'new_finance_asset_funding_usd', 'principal_repaid_usd')


def number(value, path, *, minimum=None, maximum=None):
    try:
        if type(value) is not str or len(value) > 128:
            raise ValueError()
        out = Decimal(value)
        if not out.is_finite() or abs(out.adjusted()) > 100:
            raise ValueError()
        if minimum is not None and out < minimum or maximum is not None and out > maximum:
            raise ValueError()
        return out
    except Exception as exc:
        raise CaseInputError([path + ': finite decimal string outside allowed range']) from exc


def keys(value, expected, path):
    if type(value) is not dict or set(value) != set(expected):
        raise CaseInputError([path + ': exact fields required: ' + ', '.join(expected)])


def read_fcfe(text):
    doc = _strict_json(text)
    keys(doc, ('schema_version','base_case','scope','cost_of_equity','opening_debt_usd','financing_years','terminal_growth','terminal_financing'), 'fcfe')
    if doc['schema_version'] != SCHEMA or doc['scope'] not in ('DECLARED_PARENT_COMMON','CONSOLIDATED_BEFORE_NCI_ATTRIBUTION'):
        raise CaseInputError(['fcfe: supported schema and explicit ownership scope required'])
    case = read_case(json.dumps(doc['base_case']))
    if case.bridge is not None:
        raise CaseInputError(['fcfe.base_case: use operating case without a debt-subtracting equity bridge'])
    from .discounting import TerminalAssumptions
    if type(case.terminal) is not TerminalAssumptions:
        raise CaseInputError(['fcfe.base_case: independent perpetual-growth operating terminal inputs required'])
    number(doc['cost_of_equity'], 'cost_of_equity', minimum=Decimal('0.000001'), maximum=Decimal(1))
    number(doc['opening_debt_usd'], 'opening_debt_usd', minimum=Decimal(0))
    growth = number(doc['terminal_growth'], 'terminal_growth', minimum=Decimal('-0.99'))
    if growth >= Decimal(doc['cost_of_equity']):
        raise CaseInputError(['terminal_growth: must be below cost of equity'])
    rows = doc['financing_years']
    if type(rows) is not list or len(rows) != len(case.assumptions.forecast_years):
        raise CaseInputError(['financing_years: one explicit row for every forecast year required'])
    for i, row in enumerate(rows):
        keys(row, ('period_index', *FIELDS), f'financing_years[{i}]')
        if type(row['period_index']) is not int or row['period_index'] != i + 1:
            raise CaseInputError(['financing_years: consecutive period indices required'])
        for field in FIELDS: number(row[field], field, minimum=Decimal(0))
    keys(doc['terminal_financing'], FIELDS, 'terminal_financing')
    for field in FIELDS: number(doc['terminal_financing'][field], field, minimum=Decimal(0))
    return doc


def financing_bridge(operating, tax_rate, financing, opening_debt):
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        return _financing_bridge(operating, tax_rate, financing, opening_debt)


def _financing_bridge(operating, tax_rate, financing, opening_debt):
    ebit, da, investment, wc, base_fcff = (Decimal(operating[k]) for k in ('ebit','d_and_a','investment','working_capital_cash_requirement','fcff'))
    if ebit - max(ebit, Decimal(0)) * tax_rate + da - investment - wc != base_fcff:
        raise CaseInputError(['fcfe: operating FCFF does not match supplied component basis'])
    interest, cash_issue, financed_assets, repayment = (Decimal(financing[k]) for k in FIELDS)
    if interest > 0 and opening_debt + cash_issue + financed_assets == 0:
        raise CaseInputError(['interest_expense_usd: interest requires an identified financing population'])
    if financed_assets > investment:
        raise CaseInputError(['new_finance_asset_funding_usd: exceeds matched operating investment'])
    closing = opening_debt + cash_issue + financed_assets - repayment
    if closing < 0:
        raise CaseInputError(['principal_repaid_usd: exceeds opening debt plus new financing'])
    unlevered_tax = max(ebit, Decimal(0)) * tax_rate
    equity_tax = max(ebit - interest, Decimal(0)) * tax_rate
    tax_shield = unlevered_tax - equity_tax
    net_income = ebit - interest - equity_tax
    borrowing = cash_issue + financed_assets - repayment
    fcfe = net_income + da - investment - wc + borrowing
    bridge_fcfe = base_fcff - interest + tax_shield + borrowing
    rounding = fcfe - bridge_fcfe
    # These independently ordered identities use 50 significant decimal digits.
    # Cancellation can expose a last-place difference even with identical source
    # operands. Bound only the arithmetic error: fewer than16 rounded operations,
    # each <= half one ULP at the largest intermediate magnitude. Do not use a
    # financial materiality threshold or alter either cash-flow calculation.
    intermediates = (ebit, da, investment, wc, base_fcff, interest, borrowing,
                     unlevered_tax, equity_tax, tax_shield, net_income, fcfe, bridge_fcfe)
    # The sum bounds every addition/subtraction intermediate, including values
    # whose order of magnitude can exceed that of any individual operand.
    magnitude = sum((v.copy_abs() for v in intermediates), Decimal(0))
    scale = magnitude.adjusted() if magnitude else 0
    envelope = Decimal(8).scaleb(scale - 49)
    if abs(rounding) > envelope:
        raise ValueError('Independent income/FCFF financing bridges disagree')
    result = {**{k: str(financing[k]) for k in FIELDS}, 'opening_debt_usd': str(opening_debt),
        'closing_debt_usd': str(closing), 'net_borrowing_usd': str(borrowing),
        'interest_tax_shield_usd': str(tax_shield), 'equity_tax_usd': str(equity_tax),
        'net_income_usd': str(net_income), 'fcff_usd': str(base_fcff), 'fcfe_usd': str(fcfe)}
    if rounding:
        result['income_bridge_rounding_difference_usd'] = str(rounding)
        result['income_bridge_rounding_envelope_usd'] = str(envelope)
        result['rounding_difference_is_cash_adjustment'] = False
    return result


def run_fcfe(doc, root):
    # Reparse even when called outside the HTTP boundary.
    doc = read_fcfe(json.dumps(doc))
    case = read_case(json.dumps(doc['base_case'])); base = run_case(case, root)
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        debt = Decimal(doc['opening_debt_usd']); ke = Decimal(doc['cost_of_equity']); growth = Decimal(doc['terminal_growth'])
        rows = []; pv = Decimal(0)
        for i, (operating, funding, assumptions) in enumerate(zip(base['stage_b']['stage_a']['years'], doc['financing_years'], case.assumptions.forecast_years, strict=True), 1):
            row = financing_bridge(operating, assumptions.forecast_tax_rate, funding, debt)
            debt = Decimal(row['closing_debt_usd']); factor = Decimal(1) / (1 + ke) ** i
            value = Decimal(row['fcfe_usd']) * factor; pv += value
            rows.append({'period_index':i, 'fiscal_year_label':operating['fiscal_year_label'], **row,
                         'discount_factor':str(factor), 'pv_fcfe_usd':str(value)})
        from .forecast import _operating_year
        from dataclasses import asdict
        t = case.terminal; revenue = Decimal(base['stage_b']['stage_a']['years'][-1]['revenue']) * (1 + growth)
        terminal_operating = asdict(_operating_year(len(rows)+1,'Independent FCFE terminal',revenue,
            operating_margin=t.operating_margin, operating_tax_rate=t.operating_tax_rate,
            d_and_a_ratio=t.d_and_a_percent_revenue,investment_ratio=t.investment_percent_revenue,
            working_capital_cash_ratio=t.working_capital_cash_requirement_percent_revenue))
        terminal = financing_bridge(terminal_operating,t.operating_tax_rate,doc['terminal_financing'],debt)
        # Constant capital structure in the Gordon state requires debt to grow
        # with the same long-run rate; it cannot be an arbitrary borrowing plug.
        required_borrowing = debt * growth
        if abs(Decimal(terminal['net_borrowing_usd']) - required_borrowing) > Decimal('0.000001'):
            raise CaseInputError(['terminal_financing: net financing must equal final debt × terminal growth for the declared stable-capital-structure terminal'])
        if Decimal(terminal['fcfe_usd']) <= 0:
            raise CaseInputError(['terminal_financing: positive sustainable terminal FCFE required'])
        tv = Decimal(terminal['fcfe_usd']) / (ke-growth); pvtv = tv / (1+ke)**len(rows)
        equity = pv + pvtv
    return {'schema_version':'fcfe-forecast-result-v1', 'submitted_inputs':doc,
        'scope':doc['scope'], 'semantic_input_review':'USER_ASSUMPTIONS_NOT_INDEPENDENTLY_CERTIFIED',
        'years':rows,'terminal':terminal,'cost_of_equity':doc['cost_of_equity'],
        'pv_explicit_fcfe_usd':str(pv),'terminal_equity_value_usd':str(tv),
        'pv_terminal_equity_usd':str(pvtv),'equity_value_usd':str(equity),
        'value_per_share':None, 'debt_subtracted_after_fcfe_discounting':False,
        'limitations':['Forward financing is supplied explicitly; no historical gap or NCI attribution is auto-filled.',
            'WACC in the linked operating case is used only for its separate FCFF reference; FCFE discounting uses cost of equity.',
            'Terminal financing declares stable capital structure; economic sustainability and ownership require separate review.',
            'Consolidated FCFE is before minority allocation. No common-share value is certified by this calculator.']}


def equity_cost(risk_free, beta, equity_risk_premium):
    with localcontext(Context(prec=50)):
        return number(risk_free,'risk_free') + number(beta,'beta') * number(equity_risk_premium,'equity_risk_premium',minimum=Decimal(0))


def weighted_cost(ke, kd, tax, market_equity, market_debt):
    with localcontext(Context(prec=50)):
        ke,kd,tax,e,d=(number(v,n,minimum=Decimal(0)) for v,n in zip((ke,kd,tax,market_equity,market_debt),('cost_of_equity','cost_of_debt','tax','market_equity','market_debt')))
        if tax>1 or e+d<=0:raise ValueError('Valid tax rate and positive total market capital required')
        return (ke*e+kd*(1-tax)*d)/(e+d)
