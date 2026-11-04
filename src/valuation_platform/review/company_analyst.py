"""Scoped Meta/Alphabet analyst consumers, distinct from immutable source facts.

Both use the existing operating/financing engines. Issuer-specific source and
judgment policies are pinned separately, so coverage cannot imply approval.
"""
from copy import deepcopy
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import hashlib
import json

from valuation_platform.valuation.case_inputs import CaseInputError, _strict_json, read_case, run_case
from valuation_platform.valuation.discounting import TerminalAssumptions
from valuation_platform.valuation.fcfe import keys, number, run_fcfe
from .pilot_cashflows import read_cashflows

SPECS = {
    'META': {'kind': 'meta-fy2025', 'cik': 1326801, 'name': 'Meta', 'resource': 'docs/company-resolutions/META/analyst-ready-2026-11-04/policy.json', 'pin': 'dd4c7b4fbf60a42ac41f02ceae6486fba656069e171d1187ae7cc4a7e917c5df'},
    'GOOGL': {'kind': 'googl-fy2025', 'cik': 1652044, 'name': 'Alphabet', 'resource': 'docs/company-resolutions/GOOGL/analyst-ready-2026-11-04/policy.json', 'pin': '426e8ff761793420dac6e9bc2368aff940978235c30f2b2617b98f62fd0a6a3d'},
}
ASSUMPTIONS = ('operating_cash_reserve_ratio', 'cost_of_equity', 'pre_tax_cost_of_debt',
               'rsu_vesting_fraction', 'additional_claims_usd', 'historical_other_financing_fraction',
               'nci_claim_usd', 'historical_minority_cash_share', 'additional_assets_usd')
READY = 'ANALYST_READY_WITH_QUALIFICATIONS'


def read_company_analyst(text):
    doc = _strict_json(text)
    keys(doc, ('schema_version', 'ticker', 'base_case', 'assumptions'), 'company_analyst')
    if doc['schema_version'] != 'company-analyst-request-v1' or doc['ticker'] not in SPECS:
        raise CaseInputError(['company_analyst: explicitly supported issuer and schema required'])
    spec = SPECS[doc['ticker']]; case = read_case(json.dumps(doc['base_case']))
    if (case.assumptions.company_cik != spec['cik'] or doc['base_case']['anchor']['kind'] != spec['kind']
            or doc['base_case']['anchor']['annual_end'] != '2025-12-31' or case.bridge is not None):
        raise CaseInputError(['base_case: matching FY2025 operating issuer without a manual equity bridge required'])
    if type(case.terminal) is not TerminalAssumptions:
        raise CaseInputError(['base_case: independent perpetual-growth terminal required'])
    keys(doc['assumptions'], ASSUMPTIONS, 'assumptions')
    for k, v in doc['assumptions'].items():
        maximum = Decimal('1000000000000') if k.endswith('_usd') else Decimal(1)
        minimum = Decimal('0.000001') if k == 'cost_of_equity' else Decimal(0)
        number(v, 'assumptions.'+k, minimum=minimum, maximum=maximum)
    if case.assumptions.terminal_growth >= Decimal(doc['assumptions']['cost_of_equity']):
        raise CaseInputError(['cost_of_equity: must exceed terminal growth'])
    if doc['ticker'] == 'META' and any(Decimal(doc['assumptions'][k]) != 0 for k in ('nci_claim_usd', 'historical_minority_cash_share')):
        raise CaseInputError(['META: this reviewed contract selects no separate consolidated minority population'])
    return doc


def read_policy(root, ticker):
    spec = SPECS[ticker]; body = (root / spec['resource']).read_bytes()
    if hashlib.sha256(body).hexdigest() != spec['pin']:
        raise ValueError('Analyst source policy differs from its reviewed pin')
    p = json.loads(body)
    if p['schema_version'] != 'company-analyst-policy-v1' or p['ticker'] != ticker or p['anchor_date'] != '2025-12-31':
        raise ValueError('Issuer analyst policy identity mismatch')
    if set(p['defaults']) != set(ASSUMPTIONS): raise ValueError('Explicit issuer defaults required')
    legacy = read_cashflows(root, ticker)['periods']
    if len(p['historical']) != 5: raise ValueError('Five annual source records required')
    for i, (new, old) in enumerate(zip(p['historical'], legacy, strict=True)):
        if (new['fiscal_year'] != 2021+i or new['identity']['cik'] != spec['cik']
                or new['identity']['annual_end'] != old['annual_end'] or new['identity']['accession'] != old['accession']
                or Decimal(new['fcff_usd']) != Decimal(old['fcff']['amount_usd'])
                or Fraction(new['cfo_usd'])-Fraction(new['cash_ppe_usd']) != Fraction(old['reported_cash_fcf_usd'])
                or Decimal(new['identified_net_borrowing_usd']) != Decimal(old['identified_net_borrowing_usd'])):
            raise ValueError('Current analyst policy and preserved issuer source history disagree')
    return p


def analyst_profile(root, ticker):
    p = read_policy(root, ticker)
    return {'schema_version': 'company-analyst-profile-v1', 'ticker': ticker, 'name': SPECS[ticker]['name'],
            'model_origin': p['anchor_date'], 'policy_version': p['version'], 'defaults': p['defaults'],
            'assumption_status': 'CONFIGURED_ANALYST_CONVENTIONS_NOT_REPORTED_FACTS'}


def history(policy, assumptions):
    other = Decimal(assumptions['historical_other_financing_fraction'])
    minority = Decimal(assumptions['historical_minority_cash_share'])
    out = []
    for p in policy['historical']:
        consolidated = Decimal(p['cfo_usd']) - Decimal(p['cash_ppe_usd']) + Decimal(p['identified_net_borrowing_usd']) + Decimal(p['other_financing_usd'])*other
        parent = consolidated*(1-minority)
        # Compensation proxy is allocated on the same declared cash-share basis.
        economic = (consolidated-Decimal(p['sbc_usd']))*(1-minority)
        projected = {k:p[k] for k in ('fiscal_year','identity','fcff_usd','cfo_usd','cash_ppe_usd','identified_net_borrowing_usd','other_financing_usd','sbc_usd','source_urls')}
        out.append({**projected, 'consolidated_fcfe_usd': str(consolidated), 'fcfe_usd': str(parent),
                    'parent_common_fcfe_estimate_usd': str(parent), 'economic_fcfe_usd': str(economic),
                    'exact_parent_cash_verified': False,
                    'historical_minority_cash_share': str(minority),
                    'scope': 'UNALLOCATED_CONSOLIDATED_PROXY' if policy['ticker']=='GOOGL' and minority==0 else 'PARENT_COMMON_ANALYST_ESTIMATE',
                    'classification': 'STANDARDIZED_DERIVED_ESTIMATE_WITH_DECLARED_ASSUMPTIONS'})
    return out


def funding_request(base, operating, assumptions, opening_debt, financed_fraction):
    kd = Decimal(assumptions['pre_tax_cost_of_debt']); fraction = Decimal(financed_fraction)
    def funding(investment, net=Decimal(0)):
        financed = Decimal(investment)*fraction/(1+fraction)
        return {'interest_expense_usd': str(opening_debt*kd), 'cash_debt_issued_usd': str(max(net, Decimal(0))),
                'new_finance_asset_funding_usd': str(financed), 'principal_repaid_usd': str(financed+max(-net, Decimal(0)))}
    growth = read_case(json.dumps(base)).assumptions.terminal_growth
    return {'schema_version': 'fcfe-forecast-request-v1', 'base_case': base,
            'scope': 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION', 'cost_of_equity': assumptions['cost_of_equity'],
            'opening_debt_usd': str(opening_debt),
            'financing_years': [dict(period_index=i, **funding(y['investment'])) for i,y in enumerate(operating['stage_b']['stage_a']['years'],1)],
            'terminal_growth': str(growth),
            'terminal_financing': funding(operating['stage_b']['terminal']['investment'], opening_debt*growth)}


def equity_bridge(ev, operating_equity, support, revenue, assumptions, *, carrying_debt=False):
    cash = Decimal(support['gross_cash_usd']); reserve = revenue*Decimal(assumptions['operating_cash_reserve_ratio'])
    if reserve > cash: raise CaseInputError(['operating_cash_reserve_ratio: reserve exceeds observed cash and marketable securities'])
    debt = Decimal(support['financing_debt_carrying_usd' if carrying_debt else 'financing_debt_fair_proxy_usd'])
    shares = Decimal(support['dated_common_shares']) + Decimal(support['unvested_rsus'])*Decimal(assumptions['rsu_vesting_fraction'])
    claims, nci, assets = (Decimal(assumptions[k]) for k in ('additional_claims_usd','nci_claim_usd','additional_assets_usd'))
    fcff_equity = ev+cash-reserve+assets-debt-claims-nci
    fcfe_equity = operating_equity+cash-reserve+assets-claims-nci
    if shares <= 0 or min(fcff_equity, fcfe_equity) <= 0: raise CaseInputError(['analyst equity: positive common equity and dated shares required'])
    return {'gross_cash_usd':str(cash),'operating_reserve_usd':str(reserve),'eligible_cash_usd':str(cash-reserve),
            'additional_assets_usd':str(assets),'debt_claims_usd':str(debt),'additional_claims_usd':str(claims),
            'nci_claim_usd':str(nci),'valuation_shares':str(shares),
            'fcff_equity_value_usd':str(fcff_equity),'fcfe_equity_value_usd':str(fcfe_equity),
            'fcff_value_per_share_usd':str(fcff_equity/shares),'fcfe_value_per_share_usd':str(fcfe_equity/shares),
            'debt_subtracted_after_fcfe_discounting':False,'operating_lease_debt_deduction_usd':'0',
            'separate_existing_rsu_claim_deduction_usd':'0',
            'debt_basis':'CARRYING_ALTERNATIVE' if carrying_debt else 'DISCLOSED_TERM_FAIR_VALUE_PLUS_FINANCE_LEASE_CARRYING_PROXY'}


def run_company_analyst(doc, root):
    doc = read_company_analyst(json.dumps(doc)); policy = read_policy(root, doc['ticker'])
    with localcontext(Context(prec=50,rounding=ROUND_HALF_EVEN)):
        return _run(doc, policy, root)


def _run(doc, policy, root):
    ticker = doc['ticker']; name = SPECS[ticker]['name']; a = doc['assumptions']; base = doc['base_case']
    operating = run_case(read_case(json.dumps(base)),root); stage = operating['stage_b']
    ev = Decimal(stage['enterprise_value']); revenue = Decimal(stage['stage_a']['anchor']['revenue'])
    support = policy['anchor_support']
    funding = funding_request(base,operating,a,Decimal(support['financing_debt_carrying_usd']),policy['financed_fraction_cash_ppe'])
    fcfe = run_fcfe(funding,root); operating_equity = Decimal(fcfe['equity_value_usd'])
    bridge = equity_bridge(ev,operating_equity,support,revenue,a)
    sensitivities=[]
    def stress(label,replace=None,*,carrying=False,value=ev,equity=operating_equity):
        changed={**a,**(replace or {})}; b=equity_bridge(value,equity,support,revenue,changed,carrying_debt=carrying)
        sensitivities.append({'label':label,'classification':'ILLUSTRATIVE_ANALYST_SENSITIVITY_NOT_A_BOUND',
                              **{k:b[k] for k in ('fcff_value_per_share_usd','fcfe_value_per_share_usd')}})
    stress('No operating cash reserve',{'operating_cash_reserve_ratio':'0'})
    stress('Operating cash reserve 5% of anchor revenue',{'operating_cash_reserve_ratio':'0.05'})
    stress('Debt bridge at carrying value; FCFE financing held fixed',carrying=True)
    stress('No existing RSU vesting',{'rsu_vesting_fraction':'0'})
    stress('Exclude non-operating investment value',{'additional_assets_usd':'0'})
    stress('Non-operating investments at half the selected value',{'additional_assets_usd':str(Decimal(a['additional_assets_usd'])/2)})
    stress('Additional 10B claim; illustrative only',{'additional_claims_usd':str(Decimal(a['additional_claims_usd'])+Decimal('10000000000'))})
    if ticker=='GOOGL':
        book=Decimal(support['nci_book_proxy_usd'])
        stress('No separate minority-interest equity claim',{'nci_claim_usd':'0'})
        for multiple in (5,10): stress(f'Minority claim at {multiple}× reported book proxy; not a bound',{'nci_claim_usd':str(book*multiple)})
    higher=deepcopy(funding);higher['cost_of_equity']=str(Decimal(a['cost_of_equity'])+Decimal('.01'))
    if Decimal(higher['cost_of_equity'])<=1: stress('Cost of equity +1 percentage point; FCFF held fixed',equity=Decimal(run_fcfe(higher,root)['equity_value_usd']))
    higher=deepcopy(base);higher['wacc']=str(Decimal(base['wacc'])+Decimal('.01'))
    if Decimal(higher['wacc'])<=1: stress('FCFF WACC +1 percentage point; FCFE held fixed',value=Decimal(run_case(read_case(json.dumps(higher)),root)['stage_b']['enterprise_value']))
    historical=history(policy,a)
    qualifications=[
        'Analyst-ready means usable under these explicit conventions, not exact historical cash reconstruction, issuer-certified assumptions or an investment recommendation.',
        'Analytical origin 2025-12-31 uses later-filed information; no current-date fair value, historical backtest or current-price upside is asserted.',
        'Historical FCFF preserves the adopted reported-CFO/expensed-interest/reported-tax/cash-investment convention. It retains SBC addbacks, unlike forward EBIT cash flows. No automatic cross-basis CAGR or forecast calibration.',
        'Historical FCFE includes identified financing once. Net Other allocation is a selected assumption and not a bound on unidentified offsetting gross financing. The economic companion subtracts reported SBC once; it does not normalize all accounting differences.',
        'Flat explicit carrying debt is maintained by net rollover; interest is debt cost times opening debt. Matched financed-asset investment and aggregate principal enter once; gross maturity/refinancing schedules are not predicted. Terminal debt grows at the terminal growth rate.',
        'FCFF uses the submitted target-weight WACC; FCFE uses CAPM/configured cost of equity and flat explicit debt. These financing assumptions differ, so valuation differences are shown rather than forced to zero.',
        'Liquid cash and securities exclude restricted balances and separately shown nonmarketable holdings. The selected operating reserve is an analyst haircut; ongoing liquidity costs are assumed included in forward margins/WC.',
        'Separate non-operating financial investments use an editable carrying-value proxy, not an observed market value. Operating EBIT forecasts exclude their investment returns; the same holdings are not added twice. Exclusion and haircut sensitivities show this valuation judgment.',
        'Term debt uses disclosed fair value and finance leases carrying proxies. Operating leases remain service expenses; no second operating-lease debt deduction. FCFE does not subtract debt again.',
        'Dated common shares across all economic classes plus expected existing RSU vesting form the denominator. Equal per-share economic participation is an explicit analyst assumption; voting/control rights are not claimed identical. Future SBC in margins proxies future grants; no separate settlement/award-value deduction for the same existing RSUs.',
        'Zero additional non-operating claims is an explicit base assumption, not proof of no tax/legal exposure. Ordinary settlements are assumed within forecast tax/expenses; stresses are illustrative, not bounds.',
        'FCFE financing identities are checked at 50-digit arithmetic precision. A last-place associativity residual, when present, is exported with its calculated rounding envelope and is not a cash adjustment; financial component mismatches still fail validation.',
    ]
    if ticker=='META':
        qualifications += [
            'Meta cash investment nets only identified PP&E receipts. The 2022/2023 245M/221M corrections remain; no second disposal deduction is made.',
            'Reported interest expense and cash investment retain their stated scope. Disclosed incurred capitalized interest is not automatically added to FCFF or deducted from capex; it is not proof of cash paid. Exact economic interest/investment alignment remains a qualification.',
            'FY2025 exceptional tax/valuation-allowance charges are not added to reported CFO. Forward 16% to 20%, terminal 20%, remain the separate saved analyst tax policy.',
            'The 27.524B nonmarketable investment total already contains 7.448B equity-method holdings; these are added once. Disclosed venture commitments/maximum guarantee exposure are not expected cash losses and are not automatically deducted in full; the additional-claim input permits a separately assessed loss assumption.',
        ]
    else:
        qualifications += [
            'Alphabet historical FCFE is consolidated before minority attribution. With zero selected minority cash share, the displayed parent proxy is explicitly unallocated consolidated cash, not verified parent cash. Alternative historical allocations are scenarios, not issuer disclosures.',
            'Forward valuation discounts consolidated operating FCFE and deducts one selected minority-interest claim in the equity bridge. The historical cash-allocation assumption does not change forward cash flows, preventing a second minority deduction.',
            'The default minority claim uses disclosed book NCI as a valuation proxy; redeemable NCI is already included. It is not observed fair value. 5×/10× proxy stresses are not bounds; later Waymo financing valuations are not backdated.',
            'Finance-lease cash, including prepayments, remains within debt repayments once. Historical cash capex and new noncash assets are separate populations; no rounded prepayment subtraction invents exact principal.',
            'Class A/B/C economic-per-share equivalence is assumed for valuation only. Different voting/control rights and possible market price premiums are not modeled.',
        ]
    labels=[('historical_fcff','Historical FCFF · five years','Five adopted reported-cash-convention calculations with explicit interest/tax/investment qualifications.'),
            ('fcff_valuation','FCFF forecast and enterprise value','Current selected operating forecast, WACC and independent terminal calculate.'),
            ('historical_fcfe','Historical FCFE · five years','Standardized identified-financing estimates; consolidated scope and any historical minority allocation are explicit.'),
            ('fcfe_valuation','FCFE forecast and equity value','Explicit financing, cost of equity and terminal debt growth; minority value deducted once when applicable.'),
            ('per_share','Fair value per share · both methods','Dated cash/debt/shares plus editable investment, reserve, awards and claim assumptions.')]
    return {'schema_version':'company-analyst-result-v1','ticker':ticker,'name':name,'policy_version':policy['version'],
            'model_origin':policy['anchor_date'],'submitted_inputs':doc,'assumptions':a,
            'readiness':[dict(id=k,label=label,status=READY,detail=detail) for k,label,detail in labels],
            'historical':historical,
            'fcff':{'enterprise_value_usd':str(ev),'equity_value_usd':bridge['fcff_equity_value_usd'],'value_per_share_usd':bridge['fcff_value_per_share_usd'],'wacc':base['wacc']},
            'fcfe':{'operating_equity_value_usd':str(operating_equity),'equity_value_usd':bridge['fcfe_equity_value_usd'],'value_per_share_usd':bridge['fcfe_value_per_share_usd'],
                    'cost_of_equity':a['cost_of_equity'],'years':fcfe['years'],'terminal':fcfe['terminal'],
                    'pv_explicit_fcfe_usd':fcfe['pv_explicit_fcfe_usd'],'pv_terminal_equity_usd':fcfe['pv_terminal_equity_usd'],
                    'financing_inputs':funding,'debt_subtracted_after_fcfe_discounting':False},
            'bridge':bridge,'valuation_difference_fcfe_minus_fcff_usd':str(Decimal(bridge['fcfe_equity_value_usd'])-Decimal(bridge['fcff_equity_value_usd'])),
            'historical_minorities_stress':[{'fiscal_year':p['fiscal_year'],'consolidated_fcfe_usd':p['consolidated_fcfe_usd'],
                'one_percent_minority_parent_proxy_usd':str(Decimal(p['consolidated_fcfe_usd'])*Decimal('.99')),
                'five_percent_minority_parent_proxy_usd':str(Decimal(p['consolidated_fcfe_usd'])*Decimal('.95')),'is_bound':False} for p in historical] if ticker=='GOOGL' else [],
            'qualifications':qualifications,'sensitivities':sensitivities,
            'source_urls':sorted(set(u for p in policy['historical'] for u in p['source_urls']))+policy['methodology_sources'],
            'discount_basis':policy['discount_basis'],'exact_full_historical_fcfe_claim':False,'automatic_history_calibration':False}
