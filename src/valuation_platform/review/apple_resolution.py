"""Pinned Apple issue outcomes and source support; never a financial-clearance override."""
from decimal import Decimal
import hashlib
import json

RESOURCE='docs/company-resolutions/AAPL/remaining-issues-2026-11-04/platform-resolution.json'
PIN='cc4d491bbc9dc569780f7b08a0fec26e5cade0ce4c2dc0ee4fb65e9e68e24539'
OUTCOMES=('EVIDENCE_BLOCKED','AGGREGATE_ADOPTED_RECONCILIATION_OPEN','POLICY_ADOPTED','PARTIAL_SOURCE_BOUND')


def validate(data):
    if (data.get('schema_version')!='apple-resolution-progress-v1' or data.get('ticker')!='AAPL'
        or data.get('company_status')!='OPEN' or data.get('company_complete') is not False):
        raise ValueError('This resolution version does not clear Apple')
    stages=data['stages']
    if [s['id'] for s in stages]!=['financing','da','tax','equity'] or tuple(s['outcome'] for s in stages)!=OUTCOMES:
        raise ValueError('Execution outcomes differ from reviewed source limits')
    for s in stages:
        if any(type(s[k]) is not str or not s[k].strip() for k in ('label','detail')):raise ValueError('Explicit decision details required')
    a=data['anchor_support']
    if a['as_of']!='2025-09-27' or a['fair_value_per_share_usd'] is not None:
        raise ValueError('Dated source support is not a complete share valuation')
    for k in ('cash_and_securities_usd','named_debt_carrying_usd','term_debt_fair_value_usd','finance_lease_liability_usd','dated_common_shares'):
        if type(a[k]) is not str or not Decimal(a[k]).is_finite() or Decimal(a[k])<=0:raise ValueError('Positive finite source observation required')
    share=data['share_population']
    if (share['concept']!='CommonStockSharesOutstanding' or share['as_of']!=a['as_of']
        or share['shares']!=a['dated_common_shares'] or share['award_adjusted_shares'] is not None):
        raise ValueError('No EPS/cover-date/automatic award denominator substitution')
    if any(data['readiness'][k] is not False for k in ('exact_fcfe','exact_expense_alignment','complete_equity_bridge','fair_value_per_share','automatic_history_calibration')):
        raise ValueError('Unknown financial populations cannot be cleared')
    if not data['remaining_evidence'] or not all(type(x) is str and x.strip() for x in data['remaining_evidence']):raise ValueError('Remaining evidence must be explicit')
    if not data['source_urls'] or any(not u.startswith('https://www.sec.gov/Archives/edgar/data/320193/') for u in data['source_urls']):raise ValueError('Apple SEC sources required')
    return data


def read_resolution(root):
    body=(root/RESOURCE).read_bytes()
    if hashlib.sha256(body).hexdigest()!=PIN:raise ValueError('Apple resolution differs from reviewed source pin')
    return validate(json.loads(body))
