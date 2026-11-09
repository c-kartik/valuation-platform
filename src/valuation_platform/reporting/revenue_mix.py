"""Versioned, filing-dimensional revenue reporting; isolated from valuation.

Exact member/axis sets prevent summing geographic and segment facts together.
Aliases below are issuer-reviewed taxonomy changes, never fuzzy tag matches.
"""
from datetime import date

POLICY = 'filing-dimensional-revenue-mix-v1'
REVENUE = 'RevenueFromContractWithCustomerExcludingAssessedTax'
SEGMENT = 'StatementBusinessSegmentsAxis'
PRODUCT = 'ProductOrServiceAxis'

class RevenueMixError(ValueError):
    pass

# id, display label, permitted exact member sets (one member per named axis).
def segment(*members):
    return [{SEGMENT: m} for m in members]

def product(*members):
    return [{PRODUCT: m} for m in members]

def service_detail(*members):
    return [{SEGMENT: s, PRODUCT: m} for s in ('GoogleServicesMember', 'GoogleServicesSegmentMember') for m in members]

CONFIG = {
    'GOOGL': {
        'kind': 'Reportable segments',
        'series': [
            ('services', 'Google Services', segment('GoogleServicesMember', 'GoogleServicesSegmentMember')),
            ('cloud', 'Google Cloud', segment('GoogleCloudMember', 'GoogleCloudSegmentMember')),
            ('other_bets', 'Other Bets', segment('AllOtherSegmentsMember')),
        ],
        'detail_parent': 'services',
        'detail': [
            ('search', 'Search & other', service_detail('GoogleSearchOtherMember')),
            ('youtube', 'YouTube ads', service_detail('YouTubeAdvertisingRevenueMember')),
            ('network', 'Google Network', service_detail('GoogleNetworkMember', 'GoogleNetworkMembersPropertiesMember')),
            ('subscriptions', 'Subscriptions, platforms & devices', service_detail('SubscriptionsPlatformsAndDevicesRevenueMember', 'OtherRevenuesMember')),
        ],
        'notes': [
            'Google Services detail is a decomposition of Google Services, never added to its parent again.',
            'Subscriptions, platforms & devices includes the earlier Google other revenues category; taxonomy aliases retain the source concept/member for each observation. Historical scope follows each filing, not a claim of constant business composition.',
            'Hedging gains/losses are a separate signed revenue adjustment, not an operating segment. Negative amounts are plotted below zero.',
        ],
    },
    'AAPL': {
        'kind': 'Products & services',
        'series': [
            ('iphone', 'iPhone', product('IPhoneMember')),
            ('mac', 'Mac', product('MacMember')),
            ('ipad', 'iPad', product('IPadMember')),
            ('wearables', 'Wearables, Home & Accessories', product('WearablesHomeandAccessoriesMember')),
            ('services', 'Services', product('ServiceMember')),
        ],
        'detail': [],
        'notes': ['These are product/service revenue categories. Apple’s reportable operating segments are geographic; these categories are not labelled operating segments.'],
    },
    'META': {
        'kind': 'Reportable segments',
        'series': [
            ('apps', 'Family of Apps', segment('FamilyOfAppsMember')),
            ('reality', 'Reality Labs', segment('RealityLabsMember')),
        ],
        'detail_parent': 'apps',
        'detail': [
            ('advertising', 'Advertising', [{SEGMENT: 'FamilyOfAppsMember', PRODUCT: 'AdvertisingMember'}]),
            ('other_apps', 'Other FoA revenue', [{SEGMENT: 'FamilyOfAppsMember', PRODUCT: 'ServiceOtherMember'}]),
        ],
        'notes': ['Meta does not disclose a revenue split by Facebook, Instagram and WhatsApp in this dataset. Family of Apps detail is advertising and other FoA revenue, not a per-app allocation.'],
    },
}


def _matches_dimensions(fact, permitted, ticker):
    if any(d.explicit_member is None for d in fact.dimensions):
        return False
    issuer_namespace = {'GOOGL': 'http://www.google.com/', 'AAPL': 'http://www.apple.com/', 'META': 'http://www.facebook.com/'}[ticker]
    for d in fact.dimensions:
        if not (d.dimension.namespace.startswith('http://fasb.org/us-gaap/') or d.dimension.namespace.startswith('http://fasb.org/srt/')):
            return False
        if not (d.explicit_member.namespace.startswith('http://fasb.org/us-gaap/') or d.explicit_member.namespace.startswith(issuer_namespace)):
            return False
    actual = {d.dimension.local_name: d.explicit_member.local_name for d in fact.dimensions}
    # Exact dimensions only: exclude additional geographic/channel dimensions.
    return len(actual) == len(fact.dimensions) and actual in permitted


def extract(instance, operand, concepts, dimensions):
    candidates = [f for f in instance.facts
        if f.concept in concepts and f.namespace.startswith('http://fasb.org/us-gaap/')
        and f.start == date.fromisoformat(operand['start']) and f.end == date.fromisoformat(operand['end'])
        and not f.is_nil and f.numeric_value is not None
        and f.unit and not f.unit.is_divided
        and len(f.unit.numerator_measures) == 1 and f.unit.numerator_measures[0].local_name == 'USD'
        and _matches_dimensions(f, dimensions, instance.company.ticker)]
    if not candidates:
        raise RevenueMixError(f"Missing {concepts}/{dimensions}: {operand['accession']} {operand['start']}–{operand['end']}")
    values = {f.numeric_value for f in candidates}
    if len(values) != 1:
        raise RevenueMixError(f'Conflicting dimensional facts: {values}')
    value = next(iter(values))
    if not value.is_finite() or value != value.to_integral_value():
        raise RevenueMixError('Expected exact integer USD')
    f = sorted(candidates, key=lambda f: (f.concept, f.context_id))[0]
    return {'value': int(value), 'concept': f.concept, 'namespace': f.namespace,
        'start': operand['start'], 'end': operand['end'], 'filed': str(instance.filing.filing_date),
        'accession': instance.filing.accession_number, 'source_url': instance.source_url,
        'context_ids': sorted({f.context_id for f in candidates}),
        'dimensions': [{'axis': d.dimension.local_name, 'axis_namespace': d.dimension.namespace,
                        'member': d.explicit_member.local_name, 'member_namespace': d.explicit_member.namespace}
                       for d in f.dimensions]}


def prepare_mix(report, instances):
    ticker = report['ticker']
    config = CONFIG[ticker]
    definitions = config['series'] + config['detail']
    rows = []
    operand_checks = 0
    direct_checks = []
    for quarter in report['rows']:
        totals = []
        sourced = {key: [] for key, _, _ in definitions}
        if ticker == 'GOOGL':
            sourced['hedging'] = []
        for operand in quarter['evidence']['revenue']['operands']:
            # Meta began FoA/RL reporting in Q4 2021. Use its first comparable
            # nine-month segment disclosure for the Q4 subtraction, explicitly
            # reconciled to the original consolidated operand below.
            source_accession = ('0001326801-22-000108' if ticker == 'META' and
                operand['start'] == '2021-01-01' and operand['end'] == '2021-09-30'
                else operand['accession'])
            instance = instances[source_accession]
            if str(instance.filing.filing_date) > report['as_of']:
                raise RevenueMixError('Source filed after package cutoff')
            total = extract(instance, operand, [operand['concept'].split(':')[-1]], [{}])
            if total['value'] != operand['value']:
                raise RevenueMixError('Filing total contradicts accepted quarterly operand')
            totals.append(total)
            values = {}
            for key, _, dims in definitions:
                fact = extract(instance, operand, [REVENUE], dims)
                sourced[key].append(fact)
                values[key] = fact['value']
            if ticker == 'GOOGL':
                try:
                    hedge = extract(instance, operand, ['RevenueNotFromContractWithCustomer'], [{}])
                except RevenueMixError as error:
                    if not str(error).startswith('Missing '):
                        raise
                    # Older Alphabet revenue tables use this misleading standard
                    # tag. Retained disaggregation tables confirm its revenue-hedge
                    # role; the derivative-note SalesMember amount is different.
                    hedge = extract(instance, operand, ['GainLossOnOilAndGasHedgingActivity'], [{}])
                sourced['hedging'].append(hedge)
                values['hedging'] = hedge['value']
            top_keys = [s[0] for s in config['series']] + (['hedging'] if ticker == 'GOOGL' else [])
            if sum(values[k] for k in top_keys) != total['value']:
                raise RevenueMixError(f"{ticker} {quarter['id']} cumulative components do not reconcile: {values} vs {total['value']}")
            if config['detail'] and sum(values[k] for k, _, _ in config['detail']) != values[config['detail_parent']]:
                raise RevenueMixError('Detail does not reconcile to its parent')
            operand_checks += 1
        values = {k: facts[0]['value'] - (facts[1]['value'] if len(facts) == 2 else 0) for k, facts in sourced.items()}
        total = totals[0]['value'] - (totals[1]['value'] if len(totals) == 2 else 0)
        if total != quarter['values']['revenue'] or sum(values[k] for k in top_keys) != total:
            raise RevenueMixError('Discrete quarter does not reconcile')
        if any(values[k] < 0 for k, _, _ in definitions):
            raise RevenueMixError('Negative operating revenue category requires review')
        evidence = {k: {'method': 'reported first quarter' if len(facts) == 1 else 'full year minus nine months' if quarter['quarter'] == 4 else 'successive YTD difference', 'operands': facts} for k, facts in sourced.items()}
        for key, _, dims in definitions:
            discrete = dict(quarter['evidence']['revenue']['operands'][0], start=quarter['start'])
            try:
                direct = extract(instances[discrete['accession']], discrete, [REVENUE], dims)
            except RevenueMixError as error:
                if str(error).startswith('Missing '):
                    continue
                raise
            direct_checks.append({'quarter': quarter['id'], 'series': key, 'derived': values[key], 'reported': direct['value'], 'difference': values[key] - direct['value']})
        rows.append({key: quarter[key] for key in ('id', 'start', 'end', 'fiscal_year', 'quarter')} |
                    {'total': total, 'values': values, 'evidence': evidence, 'total_evidence': totals})
    series = [{'id': key, 'label': label, 'role': 'segment' if ticker != 'AAPL' else 'product'} for key, label, _ in config['series']]
    if ticker == 'GOOGL':
        series.append({'id': 'hedging', 'label': 'Hedging gains / losses', 'role': 'adjustment'})
    annual_checks = []
    for year in sorted({r['fiscal_year'] for r in rows}):
        cohort = [r for r in rows if r['fiscal_year'] == year]
        if len(cohort) != 4:
            continue
        annual = cohort[-1]
        for key in annual['values']:
            total = sum(r['values'][key] for r in cohort)
            reported = annual['evidence'][key]['operands'][0]['value']
            if total != reported:
                raise RevenueMixError('Annual category reconciliation failed')
            annual_checks.append({'fiscal_year': year, 'series': key, 'sum_quarters': total, 'reported_annual': reported})
    return {'schema_version': 1, 'policy': POLICY, 'ticker': ticker, 'as_of': report['as_of'], 'currency': 'USD',
        'kind': config['kind'], 'series': series,
        'detail': {'parent': config.get('detail_parent'), 'series': [{'id': k, 'label': label} for k, label, _ in config['detail']]},
        'basis': 'Same fiscal YTD operands as the accepted consolidated quarterly history. Q2/Q3 are successive YTD differences; Q4 is annual less nine months. Exact integer USD; not latest-restated or as-known history.',
        'notes': config['notes'] + (['FY2021 Q4 uses annual 2021 less comparative nine-month 2021 segment data disclosed in the 2022 Q3 filing, because FoA/RL reporting began in Q4 2021. The comparative consolidated total must match the original nine-month total; this is a disclosed recast exception, not an as-known series.'] if ticker == 'META' else []), 'rows': rows,
        'validation': {'quarter_total_checks': len(rows), 'operand_total_checks': operand_checks,
                       'parent_detail_checks': len(rows) if config['detail'] else 0,
                       'direct_quarter_checks': direct_checks, 'annual_category_checks': annual_checks}}
