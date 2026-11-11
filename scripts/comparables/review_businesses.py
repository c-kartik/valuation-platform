"""Explicit dimensional business mappings and exact filing-total reconciliations."""
import json
from prepare import BASE, pick, load, write

R = 'RevenueFromContractWithCustomerExcludingAssessedTax'
O = 'OperatingIncomeLoss'
S = 'StatementBusinessSegmentsAxis'
P = 'ProductOrServiceAxis'
C = 'ConsolidationItemsAxis'

def rule(concept, **dimensions):
    return concept, dimensions

def segment(member): return rule(R, **{S: member})
def profit(member): return rule(O, **{S: member})
def product(member): return rule(R, **{P: member})

MAPPINGS = {
    'GOOGL': {
        'services': segment('GoogleServicesMember'), 'cloud': segment('GoogleCloudMember'),
        'other_bets': segment('AllOtherSegmentsMember'),
        'services_ebit': rule(O, **{S: 'GoogleServicesMember', C: 'OperatingSegmentsMember'}),
        'cloud_ebit': rule(O, **{S: 'GoogleCloudMember', C: 'OperatingSegmentsMember'}),
        'other_bets_ebit': rule(O, **{S: 'AllOtherSegmentsMember', C: 'OperatingSegmentsMember'}),
        'corporate_ebit': rule(O, **{C: 'CorporateNonSegmentMember'}),
        **{name: rule(R, **{P: member, S: 'GoogleServicesMember'}) for name, member in {
            'search': 'GoogleSearchOtherMember', 'youtube_ads': 'YouTubeAdvertisingRevenueMember',
            'network': 'GoogleNetworkMember', 'subscriptions_platforms_devices': 'SubscriptionsPlatformsAndDevicesRevenueMember'}.items()},
    },
    'META': {'family_of_apps': segment('FamilyOfAppsMember'), 'reality_labs': segment('RealityLabsMember'),
        'family_of_apps_ebit': profit('FamilyOfAppsMember'), 'reality_labs_ebit': profit('RealityLabsMember'),
        'advertising': rule(R, **{P: 'AdvertisingMember', S: 'FamilyOfAppsMember'}),
        'other_apps_revenue': rule(R, **{P: 'ServiceOtherMember', S: 'FamilyOfAppsMember'})},
    'AMZN': {'north_america': segment('NorthAmericaSegmentMember'), 'international': segment('InternationalSegmentMember'),
        'aws': segment('AmazonWebServicesSegmentMember'), 'north_america_ebit': profit('NorthAmericaSegmentMember'),
        'international_ebit': profit('InternationalSegmentMember'), 'aws_ebit': profit('AmazonWebServicesSegmentMember'),
        **{name: product(member) for name, member in {'online_stores':'OnlineStoresMember', 'physical_stores':'PhysicalStoresMember',
            'third_party_sellers':'ThirdPartySellerServicesMember', 'advertising':'AdvertisingServicesMember',
            'subscriptions':'SubscriptionServicesMember', 'aws_product':'AmazonWebServicesMember', 'other':'OtherServicesMember'}.items()}},
    'MSFT': {'agents_infra': segment('AgentsAndInfraMember'), 'devices_consumer': segment('DevicesAndConsumerMember'),
        'agents_infra_ebit': profit('AgentsAndInfraMember'), 'devices_consumer_ebit': profit('DevicesAndConsumerMember'),
        **{name: product(member) for name, member in {'azure':'AzureMember', 'm365':'MicrosoftThreeSixFiveCloudMember',
            'licensing':'ProductivityAndServerLicensingMember', 'search_ads':'SearchAndAdvertisingMember',
            'xbox':'XBOXMember', 'industry':'IndustrySolutionsMember', 'windows_devices':'WindowsOEMAndDevicesMember',
            'frontier_support':'FrontierAndSupportServicesMember'}.items()}},
    'RDDT': {'advertising': product('AdvertisingMember'), 'other_revenue': product('OtherRevenueMember')},
    'AAPL': {name: product(member) for name, member in {'iphone':'IPhoneMember', 'mac':'MacMember',
        'ipad':'IPadMember', 'wearables':'WearablesHomeandAccessoriesMember', 'services':'ServiceMember'}.items()},
    'DELL': {**{name: rule('Revenues', **{C:'OperatingSegmentsMember', S:member}) for name,member in {
        'client_solutions':'ClientSolutionsMember','infrastructure':'InfrastructureSolutionsGroupMember'}.items()},
        'corporate_revenue':rule('Revenues', **{C:'CorporateNonSegmentMember'}),
        'client_solutions_ebit':rule(O, **{C:'OperatingSegmentsMember', S:'ClientSolutionsMember'})},
    'HPQ': {**{name: rule('Revenues', **{C:'OperatingSegmentsMember', S:member}) for name,member in {
        'personal_systems':'PersonalSystemsMember','printing':'PrintingMember','corporate_investments':'CorporateInvestmentsMember'}.items()},
        'reconciling_revenue':rule('Revenues', **{C:'MaterialReconcilingItemsMember'}),
        'personal_systems_ebit':rule(O, **{C:'OperatingSegmentsMember',S:'PersonalSystemsMember'})},
    'SNAP': {'advertising':product('AdvertisingRevenueMember'), 'other_revenue':product('OtherRevenueMember')},
    'NFLX': {'reported_segment':rule('Revenues', **{S:'ReportableSegmentMember'}),
             'reported_segment_ebit':profit('ReportableSegmentMember')},
}
GROUPS = {
    'GOOGL': [('services_components', ['search', 'youtube_ads', 'network', 'subscriptions_platforms_devices'], 'services'),
              ('consolidated_revenue', ['services', 'cloud', 'other_bets', 'hedging'], 'revenue'),
              ('consolidated_ebit', ['services_ebit', 'cloud_ebit', 'other_bets_ebit', 'corporate_ebit'], 'ebit')],
    'META': [('apps_components', ['advertising', 'other_apps_revenue'], 'family_of_apps'),
             ('consolidated_revenue', ['family_of_apps', 'reality_labs'], 'revenue'),
             ('consolidated_ebit', ['family_of_apps_ebit', 'reality_labs_ebit'], 'ebit')],
    'AMZN': [('segment_revenue', ['north_america', 'international', 'aws'], 'revenue'),
             ('segment_ebit', ['north_america_ebit', 'international_ebit', 'aws_ebit'], 'ebit'),
             ('product_revenue', ['online_stores', 'physical_stores', 'third_party_sellers', 'advertising', 'subscriptions', 'aws_product', 'other'], 'revenue')],
    'MSFT': [('segment_revenue', ['agents_infra', 'devices_consumer'], 'revenue'),
             ('segment_ebit', ['agents_infra_ebit', 'devices_consumer_ebit'], 'ebit'),
             ('product_revenue', ['azure', 'm365', 'licensing', 'search_ads', 'xbox', 'industry', 'windows_devices', 'frontier_support'], 'revenue')],
    'RDDT': [('consolidated_revenue', ['advertising', 'other_revenue'], 'revenue')],
    'AAPL': [('product_revenue', ['iphone','mac','ipad','wearables','services'], 'revenue')],
    'DELL': [('segment_revenue', ['client_solutions','infrastructure','corporate_revenue'], 'revenue')],
    'HPQ': [('segment_revenue', ['personal_systems','printing','corporate_investments','reconciling_revenue'], 'revenue')],
    'SNAP': [('consolidated_revenue', ['advertising','other_revenue'], 'revenue')],
    'NFLX': [('single_segment_revenue',['reported_segment'],'revenue'),('single_segment_ebit',['reported_segment_ebit'],'ebit')],
}

def select(rows, mapping, start, end, accession):
    concept, dimensions = mapping
    selected = [r for r in rows if r['concept'] == concept and r['start'] == start and r['end'] == end
                and r['accession'] == accession and r['unit_measures'] == ['USD'] and '/us-gaap/' in r['namespace']
                and {d['axis']: d['member'] for d in r['dimensions']} == dimensions]
    values = {int(r['value']) for r in selected}
    return {'value': next(iter(values)) if len(values) == 1 else None,
            'status': 'FILING_DIMENSION_MATCH' if len(values) == 1 else 'UNAVAILABLE_OR_CONFLICT', 'evidence': selected}

def review(ticker):
    d = json.loads((BASE / 'prepared' / f'{ticker}.json').read_text())
    facts = load(BASE / 'sources' / f'{ticker}-companyfacts.json.gz')
    rows = d['segment_candidates']
    results = []
    periods = sorted({(r['start'], r['end'], r['accession']) for r in rows if r['start']})
    for start, end, accession in periods:
        selected = {name: select(rows, mapping, start, end, accession) for name, mapping in MAPPINGS.get(ticker, {}).items()}
        if ticker == 'GOOGL':
            selected['hedging'] = pick(facts, ['RevenueNotFromContractWithCustomer'], d['as_of'], start, end, accession)
        selected['revenue'] = pick(facts, ['Revenues'] if ticker in ('GOOGL','DELL','HPQ','NFLX') else [R], d['as_of'], start, end, accession)
        selected['ebit'] = pick(facts, [O], d['as_of'], start, end, accession)
        checks = []
        for name, components, target in GROUPS.get(ticker, []):
            values = [selected[c]['value'] for c in components]
            total = selected[target]['value']
            available = all(v is not None for v in values) and total is not None
            checks.append({'name': name, 'components': components, 'target': target,
                'sum': sum(values) if available else None, 'reported_total': total,
                'difference_usd': sum(values) - total if available else None,
                'status': 'MATCH' if available and sum(values) == total else 'MISMATCH' if available else 'UNAVAILABLE'})
        if any(c['status'] != 'UNAVAILABLE' for c in checks):
            results.append({'start': start, 'end': end, 'accession': accession, 'fields': selected, 'reconciliations': checks})
    receipt = {'ticker': ticker, 'as_of': d['as_of'], 'policy': 'explicit-business-dimensions-v1', 'periods': results,
        'scope': 'Exact reconciliation for available latest annual and latest interim dimensional disclosures only; no inferred segment values or segment market multiples.',
        'matches': sum(c['status'] == 'MATCH' for r in results for c in r['reconciliations']),
        'mismatches': sum(c['status'] == 'MISMATCH' for r in results for c in r['reconciliations']),
        'limitations': ['Microsoft old/new reporting structures are not spliced; unmatched old structure remains unavailable.',
                       'Pinterest and Trade Desk product-level profit breakdowns are not inferred.',
                       'Segment operating income is a management allocation measure, not standalone company EBIT.',
                       'AWS/Azure have no separately traded enterprise value.']}
    write(BASE / 'business-review' / f'{ticker}.json', receipt)
    return {k: receipt[k] for k in ['ticker', 'matches', 'mismatches']}

if __name__ == '__main__':
    failures = 0
    from prepare import ISSUERS
    for t in ISSUERS:
        result = review(t)
        failures += result['mismatches']
        print(json.dumps(result))
    if failures:
        raise SystemExit('Business reconciliation failed')
