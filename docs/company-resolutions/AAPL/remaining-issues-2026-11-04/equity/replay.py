"""Bind Apple anchor-date share/claims populations; never certify missing claims."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import runpy
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from valuation_platform.review.operating_fcff import serialized


def one(points,concept,*,unit='USD',dimension_suffix=None):
    candidates=[p for p in points if p['concept']==concept and p['scope']['end']=='2025-09-27' and p['scope']['cik']==320193 and p['scope']['start'] is None and p['unit']==unit and (not p['scope']['dimensions'] if dimension_suffix is None else len(p['scope']['dimensions'])==1 and p['scope']['dimensions'][0]['member'].endswith(dimension_suffix))]
    if not candidates or len({p['value'] for p in candidates})!=1:raise ValueError('Unique date/scope/units required for '+concept)
    return candidates[0]


def build():
    # Fresh source replay, not merely trusting a previously produced subtotal.
    module=runpy.run_path(str(ROOT/'docs/company-resolutions/implementation-2026-11-03/share-bridge/build.py'))
    source=next(c for c in module['build']()['companies'] if c['ticker']=='AAPL')
    p=source['source_points']
    cash={k:one(p,k) for k in ['CashAndCashEquivalentsAtCarryingValue','MarketableSecuritiesCurrent','MarketableSecuritiesNoncurrent']}
    debt={k:one(p,k) for k in ['CommercialPaper','LongTermDebtCurrent','LongTermDebtNoncurrent']}
    leases={k:one(p,k) for k in ['FinanceLeaseLiabilityCurrent','FinanceLeaseLiabilityNoncurrent']}
    shares=one(p,'CommonStockSharesOutstanding',unit='shares')
    issued=one(p,'CommonStockSharesIssued',unit='shares');assert shares['value']==issued['value']
    fair=one(p,'LongTermDebtFairValue',dimension_suffix='#FairValueInputsLevel2Member')
    face=one(p,'DebtInstrumentCarryingAmount')
    award=one(p,'ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber',unit='shares',dimension_suffix='#RestrictedStockUnitsRSUMember')
    cost=one(p,'EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized',dimension_suffix='#RestrictedStockUnitsRSUMember')
    subtotal=lambda d:sum((F(x['value']) for x in d.values()),F())
    gross=subtotal(cash);carrying=subtotal(debt);lease=subtotal(leases)
    assert gross==F(source['reported_cash_and_marketable_subtotal']['value_usd'])
    assert carrying==F(source['named_debt_carrying_subtotal']['value_usd'])
    termcarrying=F(debt['LongTermDebtCurrent']['value'])+F(debt['LongTermDebtNoncurrent']['value'])
    snapshot={'as_of':'2025-09-27','cash_and_securities_usd':str(gross),'named_debt_carrying_usd':str(carrying),'term_debt_fair_value_usd':fair['value'],'finance_lease_liability_usd':str(lease),'dated_common_shares':shares['value'],'fair_value_per_share_usd':None}
    return {'schema_version':'apple-equity-source-review-v1','company_status':'OPEN','source_replay':'PASS_PRIMARY_INSTANCE_MATCH',
        'anchor_support':snapshot,'sources':{'cash':cash,'debt':debt,'finance_leases':leases,'term_debt_fair_value':fair,'term_debt_face_principal':face,'dated_common_shares':shares,'common_shares_issued_control':issued,'unvested_rsus':award,'unrecognized_future_service_cost':cost},
        'adopted_population_choices':{'share_date':'2025-09-27','share_concept':'CommonStockSharesOutstanding','ordinary_common_population':shares['value'],'award_adjusted_denominator':None,'weighted_average_eps_shares_used':False,'later_cover_date_shares_used':False,'term_debt_measure':'DISCLOSED_ANCHOR_DATE_FAIR_VALUE_CANDIDATE','future_sbc':'REMAINS_EXPENSED_NO_AUTOMATIC_SECOND_SERVICE_CHARGE','operating_lease':'SERVICE_EXPENSE_POLICY_NO_AUTOMATIC_SECOND_DEBT_DEDUCTION','finance_lease':'FINANCING_CLAIM_REVIEW_SEPARATE_FROM_OPERATING_LEASE'},
        'debt_comparison':{'term_carrying_usd':str(termcarrying),'term_face_principal_usd':face['value'],'unamortized_net_discount_and_cost_arithmetic_usd':str(F(face['value'])-termcarrying),'term_fair_value_usd':fair['value'],'carrying_less_fair_value_usd':str(termcarrying-F(fair['value'])),'fair_value_precision':fair['precision'],'alternative_values_added_together':False},
        'diagnostic_only':{'one_billion_cash_or_claim_change_per_share':serialized(F(10**9)/F(shares['value'])),'debt_fair_vs_carrying_effect_per_share_before_other_adjustments':serialized((termcarrying-F(fair['value']))/F(shares['value'])),'these_are_sensitivities_not_fair_values':True},
        'unresolved_operands':{'eligible_excess_cash_usd':None,'operating_cash_requirement_usd':None,'complete_financing_claims_usd':None,'other_claims_after_forecast_overlap_usd':None,'pre_anchor_award_value_or_share_adjustment':None,'complete_common_equity_value_usd':None,'fair_value_per_share_usd':None},
        'remaining_reviews':['Review cash restrictions and operating needs; gross liquidity is not automatically excess cash.','Combine debt fair-value/CP/finance-lease decisions without overlap; carrying, principal and fair value are alternatives.','Review tax/legal/pension/contingent claims against forecast cash settlements; no automatic deduction of the entire unrecognized-tax-benefit balance.','Value the non-overlapping pre-anchor award claim; future service remains expensed and grant-date award values are not current fair value.'],
        'no_missing_claims_assumed_zero':True,'no_automatic_rsu_addition':True,'no_fair_value_per_share_published':True,
        'source_urls':sorted({r['url'] for point in [*cash.values(),*debt.values(),*leases.values(),fair,shares,award,cost] for r in point['sources'] if r['url'].endswith('.htm')}),
        'method_route_controls':{'FCFF':'Discount at matching WACC, then apply a separately reviewed equity bridge.','FCFE':'Discount at matching cost of equity; do not subtract already serviced debt again.','route_equality_not_asserted':'Requires compatible financing, interest/tax shield, timing, investment and ownership assumptions.'}}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');opts=a.parse_args();text=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    if opts.check:assert (HERE/'results.json').read_text()==text,'Apple equity review replay differs'
    else:(HERE/'results.json').write_text(text)
    print('PASS: dated Apple share/cash/debt source populations; missing claim/award values preserved.')
