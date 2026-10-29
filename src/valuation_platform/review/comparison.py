"""Conditional market reconciliation; shared engine, exact operands, no new DCF timing."""
from decimal import Decimal as D, Context, ROUND_HALF_EVEN, localcontext
import json
from .sources import MarketOpening
from valuation_platform.valuation.case_inputs import _prepare_case_runner
from valuation_platform.valuation.reverse_inputs import read_reverse,_run_reverse,DEFAULT_POLICY

SEARCH_BOUNDS={'lower':'-0.5','upper':'0.5'}
TICKERS={1326801:'META',1652044:'GOOGL',320193:'AAPL'}


def revenue_cagr(forward):
    with localcontext(Context(prec=50,rounding=ROUND_HALF_EVEN)):
        a=forward['stage_b']['stage_a'];start=D(a['anchor']['revenue']);end=D(a['years'][-1]['revenue'])
        return str((end/start)**(D(1)/D(5))-1) if start>0 and end>=0 else None


def run_review(case,root,market=None,unavailable='Opening-price reference unavailable.',bounds=None):
    execute=_prepare_case_runner(case,root);forward=execute(case)
    with localcontext(Context(prec=220,rounding=ROUND_HALF_EVEN)):
        cagr=revenue_cagr(forward)
        review={'schema_version':'investor-market-review-v1','status':'UNAVAILABLE','reasons':[],
            'market':market.to_dict() if market else None,'model_ev':forward['stage_b']['enterprise_value'],
            'forecast_cagr':cagr,'market_cap':None,'market_implied_ev':None,'ev_relative_difference':None,
            'market_implied_growth':None,'growth_gap_percentage_points':None,'reverse':None,
            'equity_difference':None,'per_share_difference':None,'search_bounds':bounds or SEARCH_BOUNDS,
            'limitations':['CAGR summarizes starting-to-final revenue; it does not preserve cash-flow timing or fully explain a value difference.',
                'EV is operating enterprise value, not market capitalization or shareholder upside.']}
        if market is None:review['reasons'].append(unavailable)
        else:
            if TICKERS.get(case.assumptions.company_cik)!=market.ticker:review['reasons'].append('Price company does not match the model.')
            if market.session_date!=case.assumptions.anchor_fiscal_end:review['reasons'].append('Market opening and fiscal-end model origin differ. Current-date stub/rolling forecast convention is not approved.')
            if not market.split_compatible:review['reasons'].append('Unadjusted price versus dated share/split basis is not verified.')
        if case.bridge is None:review['reasons'].append('Complete the dated cash, claims and share bridge to reconcile market equity to model EV.')
        elif market:
            shares=case.bridge.shares
            if shares.observation_date!=market.session_date:review['reasons'].append('Dated share denominator and opening observation differ.')
            if market.ticker in ('META','GOOGL') and shares.equivalence_convention!='explicit_common_unit_equivalence':review['reasons'].append('Explicit all-economic-class equivalence is required; one listed-class price is not automatically a consolidated market value.')
            if market.ticker=='AAPL' and shares.equivalence_convention=='single_common_class' and market.share_class!='Common':review['reasons'].append('Common-class price mismatch.')
        if review['reasons']:return {'schema_version':'investor-review-result-v1','result':forward,'review':review}
        c=forward['stage_c'];cap=market.price*D(c['valuation_shares'])
        target=cap-D(c['eligible_assets'])+D(c['financing_claims'])+D(c['other_equity_claims'])
        review.update(status='SCOPE_QUALIFIED',market_cap=str(cap),market_implied_ev=str(target),
            ev_relative_difference=None if target==0 else str(D(review['model_ev'])/target-1),
            equity_difference=None if cap==0 else str(D(c['equity_value'])/cap-1),
            per_share_difference=str(D(c['value_per_share'])/market.price-1))
        review['limitations'].extend(['Opening-reference market cap is derived from the submitted dated shares, not a current provider market-cap feed.',
            'Same selected financial perimeter; declarations/omissions are not authenticated approval and may be unbounded.'])
        original=json.loads(case.submitted_json)
        document={'schema_version':'investor-reverse-dcf-request-v2','reverse_dcf_name':'Displayed opening-reference market-implied growth',
            'source':{'kind':'single_case','case':original,'analytical_date':case.assumptions.anchor_fiscal_end.isoformat(),'information_cutoff':None},
            'target':{'metric':'ENTERPRISE_VALUE','amount':str(target),'unit':'USD','date':market.session_date.isoformat()},'growth_bounds':bounds or SEARCH_BOUNDS}
        from valuation_platform.api.budget import check_tree, BudgetError
        try:check_tree(document)
        except BudgetError:
            review['reasons'].append('Market-derived target exceeds the existing service numeric budget; no reverse solution calculated.')
            return {'schema_version':'investor-review-result-v1','result':forward,'review':review}
        request=read_reverse(json.dumps(document))
        with localcontext(Context(prec=80,rounding=ROUND_HALF_EVEN)):
            reverse=_run_reverse(request,root,DEFAULT_POLICY,execute=execute)
        review['reverse']=reverse
        if reverse['status']=='SUCCESS':
            growth=D(reverse['solution']['constant_annual_growth']);review['market_implied_growth']=str(growth)
            review['growth_gap_percentage_points']=str((D(cagr)-growth)*100) if cagr is not None else None
        return {'schema_version':'investor-review-result-v1','result':forward,'review':review}
