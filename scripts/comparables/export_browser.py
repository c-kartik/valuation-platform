"""Project reviewed peer financials into an isolated public feature package.

Uses retained financial preparation and existing SEC parsers; no new retrieval,
DCF changes, market prices or valuation defaults. Reproduces offline.
"""
import json
from datetime import datetime, timezone
from prepare import BASE, ROOT, ISSUERS, EvidenceClient, SECCompanyIdentity, load, write, pick, FLOW
from review_businesses import MAPPINGS
from valuation_platform.sec.submissions import fetch_submissions
from valuation_platform.sec.filing_xbrl import fetch_filing_xbrl

NAMES = {'GOOGL': 'Alphabet', 'META': 'Meta', 'PINS': 'Pinterest', 'RDDT': 'Reddit',
         'TTD': 'The Trade Desk', 'MSFT': 'Microsoft', 'AMZN': 'Amazon'}
ROLES = {'GOOGL': 'Target company', 'META': 'Primary advertising reference',
         'PINS': 'Secondary advertising peer', 'RDDT': 'Secondary advertising peer',
         'TTD': 'Advertising technology reference', 'MSFT': 'Diversified platform benchmark',
         'AMZN': 'Diversified platform benchmark'}
NOTES = {
    'GOOGL': 'Search, YouTube ads and Network profit is not separately disclosed. Google Cloud includes Workspace. Comparable D&A remains under review.',
    'META': 'Consolidated operating income retains Reality Labs losses. Family of Apps is a separate management profit unit, not advertising-only profit.',
    'PINS': 'Total-company revenue is the available advertising proxy. Reported convertible debt requires claims review; missing standard debt tags do not mean zero debt.',
    'RDDT': 'Smaller, faster-growing platform. Complete prepared quarterly cohorts start in 2023. Other revenue is excluded from the advertising comparison.',
    'TTD': 'Net platform-fee revenue is different from gross advertiser spending. Revenue multiples and margins need accounting context.',
    'MSFT': 'June fiscal year end. Azure product revenue is disclosed; Azure-only EBIT is not. New segment definitions require consistent recast periods.',
    'AMZN': 'AWS is a separate profit segment; consolidated accounts include retail and logistics. Gross cash purchases differ from net capex and finance-lease investment.',
}

def quarter_instance(ticker, end):
    s = load(BASE / 'sources' / f'{ticker}-submissions.json.gz')
    identity = SECCompanyIdentity(ticker, ISSUERS[ticker], f'{ISSUERS[ticker]:010}', ticker, 'SEC', datetime.now(timezone.utc))
    class Client:
        def get_json(self, url): return s
    filing = next(f for f in fetch_submissions(Client(), identity).filings if f.form == '10-Q' and str(f.report_date) == end)
    return fetch_filing_xbrl(EvidenceClient(ticker, False), identity, filing)

def segment_growth(instance, mapping):
    concept, dimensions = mapping
    operands = []
    for year in (2025, 2026):
        matches = [f for f in instance.facts if f.concept == concept and '/us-gaap/' in f.namespace
            and not f.is_nil and f.numeric_value is not None and str(f.start) == f'{year}-07-01'
            and str(f.end) == f'{year}-09-30' and f.unit and not f.unit.is_divided
            and [m.local_name for m in f.unit.numerator_measures] == ['USD']
            and {d.dimension.local_name: d.explicit_member.local_name if d.explicit_member else d.typed_member_xml for d in f.dimensions} == dimensions]
        values = {int(f.numeric_value) for f in matches}
        if len(values) != 1:
            raise ValueError('Missing/conflicting same-filing comparative: ' + str(mapping))
        operands.append({'value': values.pop(), 'start': f'{year}-07-01', 'end': f'{year}-09-30',
            'concept': concept, 'dimensions': dimensions, 'contexts': sorted({f.context_id for f in matches}),
            'source_url': instance.source_url})
    prior, current = operands
    return {'prior': prior['value'], 'current': current['value'],
            'growth': current['value'] / prior['value'] - 1 if prior['value'] else None,
            'operands': operands}

def build():
    peers, businesses, growth = {}, {}, {}
    filing_checks, business_checks = 0, 0
    for ticker in NAMES:
        prepared = json.loads((BASE / 'prepared' / f'{ticker}.json').read_text())
        if prepared['validation']['errors'] or prepared['validation']['mismatches']:
            raise ValueError('Unvalidated source package: ' + ticker)
        review = json.loads((BASE / 'business-review' / f'{ticker}.json').read_text())
        if review['mismatches']:
            raise ValueError('Business reconciliation failed: ' + ticker)
        filing_checks += prepared['validation']['matches']
        business_checks += review['matches']
        periods = [r for r in review['periods'] if r['start'] == '2026-07-01' and r['end'] == '2026-09-30']
        if periods:
            businesses[ticker] = {k: v['value'] for k, v in periods[0]['fields'].items()}
        quarters = {r['end']: r for r in prepared['quarters'] if 'metrics' in r}
        current, prior = [quarters[end]['metrics']['revenue']['value'] for end in ['2026-09-30', '2025-09-30']]
        peers[ticker] = {'name': NAMES[ticker], 'role': ROLES[ticker], 'note': NOTES[ticker],
            'ttm': {k: prepared['ttm'][k]['value'] for k in ['revenue', 'ebit', 'cfo', 'cash_capex', 'sbc']},
            'quarter_growth': current / prior - 1, 'quarter_revenue': current,
            'revenue_operands': prepared['ttm']['revenue']['operands'],
            'balances': {k: prepared['balance_sheet_candidates'][k]['value'] for k in [
                'cash', 'short_term_investments', 'long_term_debt_current', 'long_term_debt_noncurrent', 'convertible_debt_noncurrent']},
            'financials_url': prepared['ttm']['revenue']['operands'][1]['source_url']}
        fields = {'GOOGL': ['cloud', 'search', 'youtube_ads', 'network'], 'META': ['advertising'],
                  'RDDT': ['advertising'], 'AMZN': ['aws'], 'MSFT': ['azure']}.get(ticker, [])
        if fields:
            instance = quarter_instance(ticker, '2026-09-30')
            for field in fields:
                growth[ticker + '_' + field] = segment_growth(instance, MAPPINGS[ticker][field])
    components = [growth['GOOGL_' + k] for k in ['search', 'youtube_ads', 'network']]
    prior, current = [sum(c[k] for c in components) for k in ['prior', 'current']]
    growth['GOOGL_advertising'] = {'prior': prior, 'current': current, 'growth': current / prior - 1,
        'operands': [], 'components': ['GOOGL_search', 'GOOGL_youtube_ads', 'GOOGL_network']}
    pins = load(BASE / 'sources/PINS-companyfacts.json.gz')
    accession = peers['PINS']['revenue_operands'][1]['accession']
    operands = [pick(pins, FLOW['revenue'], '2026-11-11', f'{year}-07-01', f'{year}-09-30', accession) for year in [2025, 2026]]
    if any(o['value'] is None for o in operands):
        raise ValueError('Missing same-filing Pinterest comparison')
    growth['PINS_total'] = {'prior': operands[0]['value'], 'current': operands[1]['value'],
        'growth': operands[1]['value'] / operands[0]['value'] - 1, 'operands': operands}
    return {'schema_version': 1, 'target': 'GOOGL', 'as_of': '2026-11-11', 'quarter_start': '2026-07-01',
        'quarter_end': '2026-09-30', 'currency': 'USD', 'peers': peers, 'businesses': businesses,
        'growth': growth, 'validation': {'selected_filing_checks': filing_checks, 'business_reconciliations': business_checks},
        'limitations': ['GCP-only revenue/profit is not separately disclosed; Google Cloud includes Workspace.',
                       'Pinterest advertising uses an explicitly labelled total-company revenue proxy.',
                       'Growth is nominal USD, not constant currency; segment comparisons use same-filing prior quarters.',
                       'EV classifications, market-date shares, prices and comparable D&A remain under review.'],
        'market': {'valuation_date': None, 'prices': None, 'multiples': None, 'exit_default': None}}

if __name__ == '__main__':
    package = build()
    destination = ROOT / 'frontend/public/features/trading-comparables/GOOGL.json'
    write(destination, package)
    print(json.dumps({'target': package['target'], 'peers': len(package['peers']), 'growth_comparisons': len(package['growth'])}))
