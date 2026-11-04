"""Read-only public projection of the reviewed pilot cash-flow evidence.

The separately pinned projection is generated offline. No missing operand is
inferred here; a provisional number cannot become a cleared parent cash flow.
"""
from decimal import Decimal
import json
from urllib.parse import urlparse
from .cashflow_readiness import readiness

RESOURCE = 'docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json'
TICKERS = ('AAPL', 'META', 'GOOGL')


def finite(value):
    if type(value) is not str or not Decimal(value).is_finite():
        raise ValueError('Finite decimal string required')
    return Decimal(value)


def read_cashflows(root, ticker):
    if ticker not in TICKERS:
        raise ValueError('Unsupported reviewed issuer')
    payload = json.loads((root / RESOURCE).read_text())
    if payload['schema_version'] != 'pilot-cashflow-projection-v1':
        raise ValueError('Unsupported cash-flow projection')
    company = payload['companies'][ticker]
    if company['status'] != 'OPEN' or company['review_passed'] is not False:
        raise ValueError('This pinned review retains unresolved company roadblocks')
    if company['ticker'] != ticker or len(company['periods']) != 5:
        raise ValueError('Five issuer periods required')
    if [p['fiscal_year'] for p in company['periods']] != list(range(2021, 2026)):
        raise ValueError('Exact annual target sequence required')
    for period in company['periods']:
        fcff, fcfe = period['fcff'], period['fcfe']
        for metric in (fcff, fcfe):
            if metric['amount_usd'] is not None:
                finite(metric['amount_usd'])
            if not metric['basis'] or not metric['status'] or not metric['source_urls']:
                raise ValueError('Cash flow needs basis, status and source')
            for url in metric['source_urls']:
                parsed = urlparse(url)
                if parsed.scheme != 'https' or parsed.netloc != 'www.sec.gov' or not parsed.path.startswith('/Archives/'):
                    raise ValueError('Retained SEC filing source required')
        expected_status = 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION' if ticker == 'GOOGL' else 'PROVISIONAL_FINANCING_SCOPE_UNRESOLVED'
        if fcfe['status'] != expected_status or fcfe['cleared'] is not False or fcfe['parent_common_amount_usd'] is not None:
            raise ValueError('This evidence version does not clear parent-common FCFE')
        if fcff['status'] != ('UNAVAILABLE_MISSING_INTEREST' if fcff['amount_usd'] is None else 'AVAILABLE_UNDER_REPORTED_CASH_CONVENTION'):
            raise ValueError('FCFF amount/status disagree')
        if fcfe['status'] == 'PROVISIONAL_FINANCING_SCOPE_UNRESOLVED':
            if fcfe['parent_common_amount_usd'] is not None or fcfe['cleared']:
                raise ValueError('Unclassified financing cannot clear parent FCFE')
        if fcfe['status'] == 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION':
            if fcfe['scope'] != 'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION' or fcfe['parent_common_amount_usd'] is not None:
                raise ValueError('Consolidated cash cannot be relabeled as parent-common')
        if fcff['amount_usd'] is None and fcff['cleared']:
            raise ValueError('Missing FCFF cannot be cleared')
        if not company['review_passed'] and company['status'] != 'OPEN':
            raise ValueError('Failed review must retain an open company status')
    company['readiness'] = readiness(company)
    return company
