"""Independent primary/instance/Fraction audit of Apple's standardized overlay.

All arithmetic is recomputed here, without using production calculation helpers.
The final integration check then reads production outputs against that oracle.
"""
import base64
from datetime import date, timedelta
from fractions import Fraction as F
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
FOLDER = HERE.parent
INSTANCE = '{http://www.xbrl.org/2003/instance}'
cache = {}
trees = {}
primary = {}
hashes = set()
observations = []


def load(path):
    path = Path(path)
    if path not in cache:
        cache[path] = json.loads(path.read_text())
    return cache[path]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_body(source):
    filename, pointer = source['source_reference'].split('#', 1)
    artifact = load(ROOT/filename)
    for key in pointer.strip('/').split('/'):
        artifact = artifact[int(key)] if isinstance(artifact, list) else artifact[key]
    encoded = artifact['response_body_gzip_base64']
    data = gzip.decompress(base64.b64decode(''.join(encoded) if isinstance(encoded, list) else encoded))
    assert hashlib.sha256(data).hexdigest() == artifact['sha256'] == source['sha256']
    assert len(data) == artifact['byte_length'] == source['byte_length']
    assert artifact['source_url'] == source['url']
    assert source['http_status'] == 200
    hashes.add(source['sha256'])
    return data


class Inline(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = []
        self.points = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'ix:nonfraction':
            point = {'attrs': dict(attrs), 'text': []}
            self.active.append(point)

    def handle_endtag(self, tag):
        if tag == 'ix:nonfraction':
            point = self.active.pop()
            self.points[point['attrs']['id']] = point

    def handle_data(self, data):
        for point in self.active:
            point['text'].append(data)


def verify_point(point, identity, side, diagnostic_instant=None):
    assert point['source_identity'] == identity
    assert point['unit'] == 'USD' and point['evidence_depth'] == 'exact_primary_inline_and_instance_verified'
    expected = F(point['value'])
    files = {}
    for source in point['sources']:
        assert str(identity['cik']) in source['url'] and identity['accession'].replace('-', '') in source['url']
        body = source_body(source)
        if source['url'].endswith('.xml'):
            if source['sha256'] not in trees:
                trees[source['sha256']] = ET.fromstring(body)
            files['instance'] = trees[source['sha256']]
        else:
            if source['sha256'] not in primary:
                parser = Inline(); parser.feed(body.decode('utf-8'))
                primary[source['sha256']] = parser.points
            files['primary'] = primary[source['sha256']]
    assert set(files) == {'primary', 'instance'}
    tree = files['instance']
    for occurrence in point['occurrences']:
        item = files['primary'][occurrence['xml_id']]
        attrs = item['attrs']; context = occurrence['context_id']
        assert attrs['contextref'] == context
        assert attrs['name'].rsplit(':',1)[-1] == point['concept']
        text = ''.join(item['text']).replace(',', '').replace('\u00a0','').strip()
        value = F(0) if 'zero' in attrs.get('format','') else F(text)
        value *= 10**int(attrs.get('scale', '0'))
        if attrs.get('sign') == '-':
            value = -value
        assert value == expected, (point['concept'], value, expected)
        namespace = '{'+point['namespace']+'}'
        facts = [e for e in tree.iter(namespace+point['concept']) if e.attrib.get('contextRef') == context]
        assert facts and all(F(e.text.strip()) == expected for e in facts)
        units = {e.attrib['unitRef'] for e in facts}
        assert len(units) == 1
        unit = next(e for e in tree.iter(INSTANCE+'unit') if e.attrib['id'] in units)
        assert [e.text for e in unit.iter(INSTANCE+'measure')] == ['iso4217:USD']
        contexts = [e for e in tree.iter(INSTANCE+'context') if e.attrib['id'] == context]
        assert len(contexts) == 1
        c = contexts[0]
        assert int(next(c.iter(INSTANCE+'identifier')).text) == identity['cik'] == 320193
        assert not any(e.tag.endswith('explicitMember') or e.tag.endswith('typedMember') for e in c.iter())
        if side == 'annual':
            assert next(c.iter(INSTANCE+'startDate')).text == identity['annual_start']
            assert next(c.iter(INSTANCE+'endDate')).text == identity['annual_end']
            assert not list(c.iter(INSTANCE+'instant'))
        else:
            expected_date = diagnostic_instant or (identity['annual_end'] if side == 'closing' else str(date.fromisoformat(identity['annual_start'])-timedelta(days=1)))
            assert next(c.iter(INSTANCE+'instant')).text == expected_date == point.get('target_instant',point['as_of'])
            assert not list(c.iter(INSTANCE+'startDate'))
    observations.append({'fiscal_year':int(identity['annual_end'][:4]), 'side':side,
                         'concept':point['concept'],'value_usd':str(expected),
                         'primary_and_instance_match':True,'contexts_checked':len(point['occurrences'])})
    return expected


def nwc(b):
    # Independently spell out the economic population instead of importing signs.
    assets = b['current_assets'] - b['cash'] - b['current_securities']
    liabilities = b['current_liabilities'] - b['commercial_paper'] - b['current_term_debt'] - b['current_finance_lease'] - b['current_operating_lease']
    assert assets >= 0 and liabilities >= 0
    return assets - liabilities


ledger = load(FOLDER/'source-ledger.json')
overlay = load(FOLDER/'adopted-history.json')
assert sha(ROOT/ledger['package']) == ledger['package_sha256']
assert overlay['exact_unlevered_cash_flow_claim'] is False
assert overlay['forecast_calibration'] is False
assert overlay['basis'] == 'STANDARDIZED_EBIT_CURRENT_NWC_CASH_PPE'
expected = []
six_dates = {}
for source, adopted in zip(ledger['periods'],overlay['periods'],strict=True):
    identity = source['identity']
    assert identity == adopted['identity']
    assert identity['form'] == '10-K'
    annual = {key:verify_point(p,identity,'annual') for key,p in source['annual'].items()}
    balances = {side:{key:verify_point(p,identity,side) for key,p in source['balances'][side].items()} for side in ('opening','closing')}
    for side, items in balances.items():
        target = identity['annual_end'] if side=='closing' else str(date.fromisoformat(identity['annual_start'])-timedelta(days=1))
        if target in six_dates:
            assert six_dates[target] == items
        six_dates[target] = items
        assert {k:str(v) for k,v in items.items()} == adopted[side+'_balances']
    opening, closing = nwc(balances['opening']), nwc(balances['closing'])
    nopat = annual['ebit'] - annual['ebit']*annual['tax_provision']/annual['pretax_income']
    value = nopat + annual['da'] - annual['cash_ppe'] - (closing-opening)
    assert adopted['inputs'] == {**{k:str(v) for k,v in annual.items()}, 'opening_nwc':str(opening), 'closing_nwc':str(closing)}
    exact = adopted['fcff']['exact_fraction_usd']
    assert value == F(int(exact['numerator']),int(exact['denominator']))
    assert abs(value - F(adopted['fcff']['amount_usd'])) < F(1,10**30)
    expected.append({'fiscal_year':source['fiscal_year'],'opening_nwc_usd':str(opening),'closing_nwc_usd':str(closing),
                     'delta_nwc_usd':str(closing-opening),'fcff_exact_fraction_usd':str(value),
                     'fcff_serialized_usd':adopted['fcff']['amount_usd'],
                     'sbc_added_back':False,'tax_population':'INCLUDED_IN_AGGREGATE_ALL_YEARS',
                     'both_current_leases_excluded':True})
assert len(expected) == 5 and len(six_dates) == 6 and len(observations) == 105 and len(hashes) == 10
tax_diagnostics = []
for p in ledger['periods']:
    diagnostic = p['separately_disclosed_current_tax_diagnostic']
    assert p['tax_diagnostic_missing_means_zero'] is False
    if diagnostic is None:
        assert p['fiscal_year'] == 2021
        continue
    value = verify_point(diagnostic,diagnostic['source_identity'],'diagnostic',p['identity']['annual_end'])
    tax_diagnostics.append({'target_fiscal_year':p['fiscal_year'],'current_tax_usd':str(value),
                            'source_filing_year':int(diagnostic['source_identity']['annual_end'][:4]),
                            'used_as_formula_subtraction':False})
assert len(tax_diagnostics) == 4 and len(observations) == 109

# Verify the primary runtime consumer and actual chart catalog separately.
from valuation_platform.review.pilot_cashflows import read_cashflows
from valuation_platform.review.resolved_history import adopted_window
from valuation_platform.api.catalog import build_catalog
runtime = read_cashflows(ROOT,'AAPL')
legacy = load(ROOT/'docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json')
assert sha(ROOT/'docs/company-resolutions/implementation-2026-11-03/platform-cashflows.json') == '9b2a9d775745e9d4bd08efe60d49619c24f632b16a28fce5fcba014fe1f55d86'
for p, old, oracle in zip(runtime['periods'],legacy['companies']['AAPL']['periods'],expected,strict=True):
    assert p['legacy_cfo_fcff'] == old['fcff']
    assert p['fcfe'] == old['fcfe']
    assert p['fcff']['amount_usd'] == oracle['fcff_serialized_usd']
    assert p['fcff']['valuation_basis_aligned'] is False
    assert p['fcff']['exact_unlevered_cash_flow_claim'] is False
assert [p['legacy_cfo_fcff']['amount_usd'] for p in runtime['periods']][-2:] == [None,None]
for ticker in ('META','GOOGL'):
    company = read_cashflows(ROOT,ticker)
    assert {k:v for k,v in company.items() if k!='readiness'} == legacy['companies'][ticker]
history = adopted_window(ROOT,'aapl-fy2025')
assert [p['fcff'] for p in history] == [p['fcff_serialized_usd'] for p in expected]
catalog = json.loads(build_catalog(ROOT))
entry = next(e for e in catalog['entries'] if e['company']=='AAPL')
assert [p['fcff'] for p in entry['historical_window']] == [p['fcff_serialized_usd'] for p in expected]
assert entry['historical_fcff_policy']['cross_basis_cagr'] is False
assert entry['historical_fcff_policy']['forecast_calibration'] is False
result = {'verdict':'PASS_QUALIFIED_STANDARDIZED_APPLE_HISTORY', 'financial_company_status':'OPEN',
          'five_scoped_history_values_available':True, 'legacy_cfo_gaps_preserved':True,
          'fcfe_changed':False,'meta_googl_changed':False,'exact_cash_fcff_claim':False,
          'forecast_calibration_or_cross_basis_cagr_enabled':False,
          'source_points_checked':105,'annual_points':25,'instant_points':80,
          'additional_current_tax_diagnostics_checked':4,'tax_diagnostics':tax_diagnostics,
          'retained_body_hashes_checked':len(hashes),'distinct_balance_dates':sorted(six_dates),
          'primary_chart_catalog_matches':True,'history_reader_matches':True,
          'amounts':expected,'source_observations':observations,
          'qualification_requirements':['Broad Other current balances classified by model convention, not individual pure operating facts.',
              'Current-tax accruals remain included uniformly; no missing split treated as zero.',
              'Reported ETR allocation is not exact unlevered cash taxation.',
              'Cash-statement combined D&A is adopted without a 355M reconciliation plug; precise note populations remain different.',
              'Cash PP&E model omits a comprehensive economic-investment/finance-lease asset bridge.',
              'No automatic forecast calibration; existing forecast inputs and EV are a separate validation scope.'],
          'integration_scope_limits':['No browser visual interaction performed by this independent source audit.',
              'Readiness metadata and actual exports checked; no independent end-to-end live DCF engine parity claim.']}
(HERE/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:result[k] for k in ('verdict','source_points_checked','annual_points','instant_points','retained_body_hashes_checked','five_scoped_history_values_available','legacy_cfo_gaps_preserved','financial_company_status')},indent=2))
