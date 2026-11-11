"""Isolated, offline-first peer financial preparation. Never writes DCF assets.

Run PYTHONPATH=src .venv/bin/python scripts/comparables/prepare.py --as-of YYYY-MM-DD
Add --refresh to retrieve missing official SEC evidence with SEC_USER_AGENT.
"""
import argparse
import gzip
import hashlib
import json
import os
import time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from valuation_platform.sec.client import SECClient
from valuation_platform.sec.filing_xbrl import fetch_filing_xbrl
from valuation_platform.sec.submissions import fetch_submissions
from valuation_platform.sec.tickers import SECCompanyIdentity

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'data/trading-comparables'
ISSUERS = {'GOOGL': 1652044, 'META': 1326801, 'PINS': 1506293,
           'RDDT': 1713445, 'TTD': 1671933, 'MSFT': 789019, 'AMZN': 1018724}
FLOW = {
    'revenue': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues', 'SalesRevenueNet'],
    'ebit': ['OperatingIncomeLoss'],
    'cfo': ['NetCashProvidedByUsedInOperatingActivities'],
    'cash_capex': ['PaymentsToAcquirePropertyPlantAndEquipment'],
    'sbc': ['ShareBasedCompensation'],
    'reported_da': ['DepreciationDepletionAndAmortization'],
    'depreciation_only': ['Depreciation'],
    'intangible_amortization': ['AmortizationOfIntangibleAssets'],
}
BALANCE = {
    'cash': ['CashAndCashEquivalentsAtCarryingValue'],
    'short_term_investments': ['ShortTermInvestments', 'MarketableSecuritiesCurrent'],
    'long_term_investments_candidate': ['LongTermInvestments', 'MarketableSecuritiesNoncurrent'],
    'long_term_debt_current': ['LongTermDebtCurrent'],
    'long_term_debt_noncurrent': ['LongTermDebtNoncurrent'],
    'convertible_debt_noncurrent': ['ConvertibleDebtNoncurrent'],
    'short_term_borrowings': ['ShortTermBorrowings'],
    'finance_lease_current': ['FinanceLeaseLiabilityCurrent'],
    'finance_lease_noncurrent': ['FinanceLeaseLiabilityNoncurrent'],
    'operating_lease_current': ['OperatingLeaseLiabilityCurrent'],
    'operating_lease_noncurrent': ['OperatingLeaseLiabilityNoncurrent'],
    'noncontrolling_interests': ['MinorityInterest'],
}

def load(path):
    return json.loads(gzip.decompress(path.read_bytes()))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def observations(payload, tags, cutoff, unit='USD'):
    for tag in tags:
        for o in payload['facts'].get('us-gaap', {}).get(tag, {}).get('units', {}).get(unit, []):
            if o.get('filed', '9999') <= cutoff and o['end'] <= cutoff and o.get('form') in ('10-K', '10-Q'):
                yield tag, o

def pick(payload, tags, cutoff, start, end, accession=None):
    candidates = [(tag, o) for tag, o in observations(payload, tags, cutoff)
                  if o.get('start') == start and o['end'] == end
                  and (accession is None or o['accn'] == accession)]
    if not candidates:
        return {'value': None, 'status': 'MISSING', 'requested_tags': tags,
                'start': start, 'end': end, 'accession': accession}
    # Latest available disclosure, then explicit concept priority; conflicts fail closed.
    latest = max(o['filed'] for _, o in candidates)
    candidates = [(t, o) for t, o in candidates if o['filed'] == latest]
    priority = min(tags.index(t) for t, _ in candidates)
    candidates = [(t, o) for t, o in candidates if tags.index(t) == priority]
    values = {Decimal(str(o['val'])) for _, o in candidates}
    if len(values) != 1:
        return {'value': None, 'status': 'CONFLICT', 'candidates': candidates}
    tag, o = min(candidates, key=lambda v: v[1]['accn'])
    value = values.pop()
    if not value.is_finite() or value != value.to_integral_value():
        raise ValueError('Expected integer USD')
    return {'value': int(value), 'status': 'SEC_REPORTED', 'concept': tag,
            'start': start, 'end': end, 'accession': o['accn'], 'filed': o['filed'],
            'source_url': f"https://www.sec.gov/Archives/edgar/data/{payload['cik']}/{o['accn'].replace('-', '')}/"}

def derive(operands, coefficients, method):
    available = all(o['value'] is not None for o in operands)
    return {'value': sum(o['value'] * c for o, c in zip(operands, coefficients)) if available else None,
            'status': 'SEC_SUPPORTED_DERIVATION' if available else 'MISSING_OPERAND',
            'method': method, 'coefficients': coefficients, 'operands': operands}

def ratio(a, b):
    return a / b if a is not None and b not in (None, 0) else None

def filing_values_agree(matches, expected):
    """Require an exact fact and reject contradictory duplicates at their precision.

    A rounded note can repeat a statement fact in the same context. Do not
    discard the duplicate or accept an arbitrary monetary tolerance.
    """
    expected = Decimal(expected)
    if not any(f.numeric_value == expected for f in matches):
        return False
    for f in matches:
        if f.numeric_value == expected: continue
        if f.decimals in (None, 'INF'):
            return False
        tolerance = Decimal(10) ** (-int(f.decimals)) / 2
        if abs(f.numeric_value - expected) > tolerance:
            return False
    return True

class EvidenceClient:
    def __init__(self, ticker, refresh):
        self.directory = BASE / 'sources' / ticker
        self.directory.mkdir(parents=True, exist_ok=True)
        self.refresh = refresh
        self.client = SECClient(os.environ.get('SEC_USER_AGENT', 'offline reproduction'), timeout=60)
        self.manifest = {}
    def get_bytes(self, url):
        path = self.directory / (hashlib.sha256(url.encode()).hexdigest() + '.gz')
        if not path.exists():
            if not self.refresh:
                raise ValueError('Missing retained evidence: ' + url)
            raw = self.client.get_bytes(url)
            path.write_bytes(gzip.compress(raw, mtime=0))
            time.sleep(.25)
        self.manifest[url] = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        return gzip.decompress(path.read_bytes())
    def get_json(self, url):
        return json.loads(self.get_bytes(url))

def leaves(value):
    if isinstance(value, dict):
        if value.get('status') == 'SEC_REPORTED':
            yield value
        for o in value.get('operands', []):
            yield from leaves(o)

def prepare(ticker, cutoff, refresh=False):
    facts_path = BASE / 'sources' / f'{ticker}-companyfacts.json.gz'
    facts = load(facts_path)
    tags = {k: list(v) for k, v in FLOW.items()}
    if ticker == 'AMZN':
        tags['cash_capex'] = ['PaymentsToAcquireProductiveAssets']
    # Do not substitute depreciation-only or note-only D&A into EBITDA.
    annual_periods = sorted({(o['start'], o['end']) for _, o in observations(facts, tags['revenue'], cutoff)
        if o.get('start') and o['form'] == '10-K' and 330 <= (date.fromisoformat(o['end']) - date.fromisoformat(o['start'])).days <= 380
        and o['end'][:4] >= '2021'})
    annuals = []
    for start, end in annual_periods:
        anchor = pick(facts, tags['revenue'], cutoff, start, end)
        annuals.append({'start': start, 'end': end,
                       'metrics': {m: pick(facts, ts, cutoff, start, end, anchor['accession']) for m, ts in tags.items()}})
    if not annuals:
        raise ValueError(ticker + ': no annual cohort')
    annual = annuals[-1]
    current_start = str(date.fromisoformat(annual['end']) + timedelta(days=1))
    interim_ends = sorted({o['end'] for _, o in observations(facts, tags['revenue'], cutoff)
        if o.get('start') == current_start and o['form'] == '10-Q'})
    latest_end = interim_ends[-1] if interim_ends else annual['end']
    latest_anchor = pick(facts, tags['revenue'], cutoff, current_start, latest_end) if interim_ends else annual['metrics']['revenue']
    latest_acc = latest_anchor['accession']
    ttm = {}
    for metric, ts in tags.items():
        if not interim_ends:
            ttm[metric] = derive([annual['metrics'][metric]], [1], 'latest annual')
            continue
        # Prior-year YTD must be disclosed in the same interim filing as current YTD.
        prior = [(o['start'], o['end']) for _, o in observations(facts, tags['revenue'], cutoff)
                 if o['accn'] == latest_acc and o.get('start') == annual['start']
                 and 350 <= (date.fromisoformat(latest_end) - date.fromisoformat(o['end'])).days <= 378]
        if len(set(prior)) != 1:
            raise ValueError('Ambiguous prior-year YTD calendar')
        ps, pe = prior[0]
        ttm[metric] = derive([annual['metrics'][metric],
            pick(facts, ts, cutoff, current_start, latest_end, latest_acc),
            pick(facts, ts, cutoff, ps, pe, latest_acc)], [1, 1, -1], 'annual + current fiscal YTD - same-filing prior fiscal YTD')
    quarters = []
    for cohort in annuals + ([{'start': current_start, 'end': latest_end, 'metrics': None}] if interim_ends else []):
        start, end = cohort['start'], cohort['end']
        ends = sorted({o['end'] for _, o in observations(facts, tags['revenue'], cutoff)
            if o.get('start') == start and o['form'] == '10-Q' and o['end'] < end}) + [end]
        previous = None
        for q, qend in enumerate(ends, 1):
            qstart = start if previous is None else str(date.fromisoformat(previous['end']) + timedelta(days=1))
            if not 70 <= (date.fromisoformat(qend) - date.fromisoformat(qstart)).days <= 110:
                quarters.append({'start': qstart, 'end': qend, 'status': 'INCOMPLETE_QUARTER_COHORT'})
                previous = None
                break
            anchor = pick(facts, tags['revenue'], cutoff, start, qend)
            current = {m: pick(facts, ts, cutoff, start, qend, anchor['accession']) for m, ts in tags.items()}
            metrics = {m: derive([o] + ([previous['metrics'][m]] if previous else []), [1, -1] if previous else [1],
                                'successive fiscal YTD difference' if previous else 'reported first fiscal quarter') for m, o in current.items()}
            differences = {}
            for m in ('revenue', 'ebit'):
                direct = pick(facts, tags[m], cutoff, qstart, qend, anchor['accession'])
                if direct['value'] is not None and metrics[m]['value'] is not None:
                    differences[m] = {'reported': direct, 'difference_usd': metrics[m]['value'] - direct['value']}
            quarters.append({'start': qstart, 'end': qend, 'quarter': q, 'metrics': metrics, 'same_filing_discrete_checks': differences})
            previous = {'end': qend, 'metrics': current}
    balance = {m: pick(facts, ts, cutoff, None, latest_end, latest_acc) for m, ts in BALANCE.items()}
    identity = SECCompanyIdentity(ticker, ISSUERS[ticker], f'{ISSUERS[ticker]:010}', facts['entityName'], 'SEC', datetime.now(timezone.utc))
    submissions_path = BASE / 'sources' / f'{ticker}-submissions.json.gz'
    class SubmissionsClient:
        def get_json(self, url): return load(submissions_path)
    filings = fetch_submissions(SubmissionsClient(), identity).filings
    client = EvidenceClient(ticker, refresh)
    checks, segment_candidates, share_candidates, errors = [], [], [], []
    financial_candidates = []
    selected = [annual['metrics'], ttm, balance]
    operands = {json.dumps(o, sort_keys=True): o for group in selected for v in group.values() for o in leaves(v)}
    for accession in sorted({o['accession'] for o in operands.values()}):
        filing = next((f for f in filings if f.accession_number == accession), None)
        if filing is None:
            errors.append({'accession': accession, 'error': 'Not in retained recent submissions; historical lookup required'})
            continue
        try:
            instance = fetch_filing_xbrl(client, identity, filing)
        except Exception as exc:
            errors.append({'accession': accession, 'error': str(exc)})
            continue
        for o in operands.values():
            if o['accession'] != accession: continue
            matches = [f for f in instance.facts if not f.dimensions and not f.is_nil and f.numeric_value is not None
                and '/us-gaap/' in f.namespace
                and f.concept == o['concept'] and f.start == (date.fromisoformat(o['start']) if o['start'] else None)
                and str(f.end) == o['end'] and f.unit and not f.unit.is_divided
                and len(f.unit.numerator_measures) == 1 and f.unit.numerator_measures[0].local_name == 'USD']
            values = {f.numeric_value for f in matches}
            checks.append({**o, 'status': 'MATCH' if filing_values_agree(matches, o['value']) else 'MISMATCH',
                           'filing_values': sorted(str(v) for v in values), 'instance_url': instance.source_url,
                           'filing_precisions': [{'value': str(f.numeric_value), 'decimals': f.decimals} for f in matches],
                           'contexts': [f.context_id for f in matches]})
        # Capture exact dimensional facts for review; do not approve dimension mappings by string similarity.
        for f in instance.facts:
            if f.is_nil or f.numeric_value is None: continue
            if str(f.end) != filing.report_date.isoformat(): continue
            if not f.dimensions and any(k in f.concept for k in (
                'Depreciation', 'Amortization', 'Debt', 'Borrowing', 'LeaseLiability',
                'MarketableSecurities', 'ShortTermInvestment', 'InvestmentsCurrent',
                'NoncontrollingInterest', 'MinorityInterest', 'CashAndCashEquivalents',
                'RevenueNotFromContractWithCustomer')):
                financial_candidates.append({'concept': f.concept, 'namespace': f.namespace,
                    'value': str(f.numeric_value), 'start': str(f.start) if f.start else None,
                    'end': str(f.end), 'accession': accession, 'context': f.context_id,
                    'source_url': instance.source_url, 'status': 'SCOPE_REVIEW_REQUIRED'})
            if f.dimensions and (f.concept in set(sum(tags.values(), [])) or 'Revenue' in f.concept or 'OperatingIncome' in f.concept):
                segment_candidates.append({'concept': f.concept, 'namespace': f.namespace, 'value': str(f.numeric_value),
                    'start': str(f.start) if f.start else None, 'end': str(f.end), 'accession': accession,
                    'context': f.context_id, 'unit': f.unit_ref,
                    'unit_measures': [m.local_name for m in f.unit.numerator_measures] if f.unit and not f.unit.is_divided else [],
                    'source_url': instance.source_url,
                    'dimensions': [{'axis': d.dimension.local_name, 'member': d.explicit_member.local_name if d.explicit_member else d.typed_member_xml} for d in f.dimensions],
                    'status': 'UNREVIEWED_DIMENSIONAL_CANDIDATE'})
            if 'CommonStock' in f.concept and 'SharesOutstanding' in f.concept:
                share_candidates.append({'concept': f.concept, 'value': str(f.numeric_value), 'end': str(f.end),
                    'accession': accession, 'context': f.context_id, 'source_url': instance.source_url,
                    'dimensions': [{'axis': d.dimension.local_name, 'member': d.explicit_member.local_name if d.explicit_member else d.typed_member_xml} for d in f.dimensions],
                    'status': 'CLASS_REVIEW_REQUIRED_NOT_MARKET_CAP_INPUT'})
    values = {k: v['value'] for k, v in ttm.items()}
    metrics = {'ebit_margin': ratio(values['ebit'], values['revenue']),
               'cash_capex_to_revenue': ratio(values['cash_capex'], values['revenue']),
               'sbc_to_revenue': ratio(values['sbc'], values['revenue']),
               'cfo_to_ebit': ratio(values['cfo'], values['ebit']) if values['ebit'] and values['ebit'] > 0 else None,
               'fcf': derive([ttm['cfo'], ttm['cash_capex']], [1, -1], 'reported CFO less gross cash PP&E purchases; not FCFF/FCFE')}
    if interim_ends:
        operands = ttm['revenue']['operands']
        metrics['same_filing_ytd_revenue_growth'] = (ratio(operands[1]['value'], operands[2]['value']) - 1
            if operands[2]['value'] and operands[1]['value'] is not None else None)
    annual_checks = []
    for a in annuals:
        cohort = [q for q in quarters if q.get('metrics') and a['start'] <= q['start'] and q['end'] <= a['end']]
        for m, observation in a['metrics'].items():
            qs = [q['metrics'][m]['value'] for q in cohort]
            available = len(qs) == 4 and all(v is not None for v in qs) and observation['value'] is not None
            annual_checks.append({'start': a['start'], 'end': a['end'], 'metric': m,
                'status': 'MATCH' if available and sum(qs) == observation['value'] else 'MISMATCH' if available else 'INCOMPLETE',
                'annual_value': observation['value'], 'quarter_sum': sum(qs) if available else None,
                'scope': 'Arithmetic consistency, not independent quarterly certification'})
    package = {'schema_version': 1, 'policy': 'peer-financial-preparation-v1', 'ticker': ticker, 'company': facts['entityName'],
        'as_of': cutoff, 'currency': 'USD', 'latest_period_end': latest_end,
        'annuals': annuals, 'quarters': quarters, 'ttm': ttm, 'balance_sheet_candidates': balance,
        'derived_metrics': metrics, 'share_candidates': share_candidates,
        'segment_candidates': segment_candidates, 'financial_scope_candidates': financial_candidates,
        'validation': {'scope': 'Latest annual, current/prior YTD TTM operands and latest balance candidates; historical quarters are arithmetic/source-index preparation, not independently re-extracted.',
                       'checks': checks, 'errors': errors, 'annual_quarter_checks': annual_checks,
                       'matches': sum(c['status'] == 'MATCH' for c in checks),
                       'mismatches': sum(c['status'] != 'MATCH' for c in checks)},
        'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [facts_path, submissions_path]},
        'filing_source_manifest': client.manifest,
        'status': 'VALIDATION_FAILED' if errors or any(c['status'] != 'MATCH' for c in checks) else 'PREPARED_WITH_OPEN_REVIEW_ITEMS',
        'open_items': ['Dimensional business mapping and reconciliation require review.',
                       'D&A scope must be reconciled to EBIT before deriving comparable EBITDA; no EBITDA published.',
                       'Debt, finance leases, investments and NCI require economic classification before an EV bridge.',
                       'Point-in-time class-level share counts require separate review; EPS weighted averages are not market cap shares.',
                       'Market prices, usage rights, valuation date and exit multiple are not selected.',
                       'Historical annuals use latest available same-filing observations as of cutoff; interim operands may have different revision vintages.',
                       'Missing tags remain null; no assumption of zero debt or absent claims.']}
    write(BASE / 'prepared' / f'{ticker}.json', package)
    return {'ticker': ticker, 'annuals': len(annuals), 'quarters': len([q for q in quarters if 'metrics' in q]),
            'latest_end': latest_end, 'ttm_revenue': values['revenue'], 'ttm_ebit': values['ebit'],
            'filing_matches': package['validation']['matches'], 'filing_mismatches': package['validation']['mismatches'],
            'source_errors': errors, 'missing_ttm_metrics': [k for k, v in values.items() if v is None]}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', type=date.fromisoformat, required=True)
    parser.add_argument('--ticker', choices=list(ISSUERS), action='append')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    if args.refresh and not os.environ.get('SEC_USER_AGENT'):
        parser.error('SEC_USER_AGENT required')
    summary = []
    for ticker in args.ticker or ISSUERS:
        result = prepare(ticker, str(args.as_of), args.refresh)
        summary.append(result)
        print(json.dumps(result), flush=True)
    write(BASE / 'preparation-summary.json', {'as_of': str(args.as_of), 'issuers': summary})
    if any(r['filing_mismatches'] or r['source_errors'] for r in summary):
        raise SystemExit('Filing validation failed; packages are review evidence, not accepted inputs')
