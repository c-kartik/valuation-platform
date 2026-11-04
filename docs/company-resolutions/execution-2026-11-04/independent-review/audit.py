"""Independent Fraction-based review; imports no implementation calculation code.

Read retained original inputs, recompute bridges and availability, then compare
with the proposed execution artifacts. No financial data or implementation edits.
"""
import base64
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'docs/company-resolutions'
EXEC = HERE.parent
loaded = {}
parsed = {}
receipt_hashes = set()
source_observations = 0


def read(path):
    path = Path(path)
    if path not in loaded:
        loaded[path] = json.loads(path.read_text())
    return loaded[path]


def raw_source(source):
    reference = source.get('source_reference', source.get('retained_reference'))
    filename, pointer = reference.split('#', 1)
    artifact = read(ROOT / filename)
    for key in pointer.strip('/').split('/'):
        artifact = artifact[int(key)] if isinstance(artifact, list) else artifact[key]
    encoded = artifact['response_body_gzip_base64']
    data = gzip.decompress(base64.b64decode(''.join(encoded) if isinstance(encoded, list) else encoded))
    assert hashlib.sha256(data).hexdigest() == source['sha256'] == artifact['sha256']
    assert len(data) == artifact['byte_length']
    receipt_hashes.add(source['sha256'])
    return data


def verify_point(point):
    global source_observations
    value = Q(point['value'])
    instance_sources = [s for s in point['sources'] if s['url'].endswith('.xml')]
    assert instance_sources, 'Expected retained extracted XBRL instance'
    for source in point['sources']:
        data = raw_source(source)
        if source in instance_sources:
            if source['sha256'] not in parsed:
                parsed[source['sha256']] = ET.fromstring(data)
            tree = parsed[source['sha256']]
            qname = '{' + point['namespace'] + '}' + point['concept']
            occurrences = point['occurrences']
            for occurrence in occurrences:
                matches = [e for e in tree.iter(qname)
                           if e.attrib.get('contextRef') == occurrence['context_id']]
                assert matches and all(Q(e.text.strip()) == value for e in matches)
                contexts = [e for e in tree.iter('{http://www.xbrl.org/2003/instance}context')
                            if e.attrib.get('id') == occurrence['context_id']]
                assert len(contexts) == 1
                dates = {e.tag.rsplit('}', 1)[-1]: e.text for e in contexts[0].iter()
                         if e.tag.rsplit('}', 1)[-1] in ('startDate', 'endDate')}
                assert dates['startDate'] == point.get('target_annual_start', point['source_identity']['annual_start'])
                assert dates['endDate'] == point.get('target_annual_end', point['source_identity']['annual_end'])
                assert not any(e.tag.endswith('explicitMember') or e.tag.endswith('typedMember')
                               for e in contexts[0].iter()), 'Unexpected segment axis'
    source_observations += 1
    return value


def exact(serialized):
    f = serialized['exact_fraction_usd']
    result = Q(int(f['numerator']), int(f['denominator']))
    assert abs(result - Q(serialized['amount_usd'])) < Q(1, 10**30)
    return result


baseline = read(EXEC / 'baseline.json')
for name, digest in baseline['source_pins'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest
projection_path = BASE/'implementation-2026-11-03/platform-cashflows.json'
assert hashlib.sha256(projection_path.read_bytes()).hexdigest() == '9b2a9d775745e9d4bd08efe60d49619c24f632b16a28fce5fcba014fe1f55d86'
projection = read(projection_path)
apple_old = read(BASE/'AAPL/results.json')
apple_evidence = read(BASE/'AAPL/implementation-2026-11-03/evidence-ledger.json')
step1 = read(EXEC/'step-1-apple-operating.json')
apple_rows = []
for old, evidence, actual in zip(apple_old['periods'], apple_evidence['periods'], step1['periods'], strict=True):
    inputs = {name: verify_point(p) for name, p in old['operating_fcff_candidate']['inputs'].items()}
    terms = evidence['operating_bridge']['statement_terms']
    for term in terms:
        raw = verify_point(term['source'])
        assert raw * term['cash_sign'] == Q(term['cash_contribution_usd'])
    cash_tax = verify_point(evidence['tax_review']['cash_paid'])
    by_concept = {t['source']['concept']: Q(t['cash_contribution_usd']) for t in terms}
    ni = by_concept['NetIncomeLoss']
    da = by_concept['DepreciationDepletionAndAmortization']
    sbc = by_concept['ShareBasedCompensation']
    ebit = inputs['ebit']; provision = inputs['tax_provision']; pretax = inputs['pretax_income']
    cfo = inputs['cfo_control']; capex = inputs['cash_ppe']
    assert sum((Q(t['cash_contribution_usd']) for t in terms), Q()) == cfo
    assert ni == pretax - provision
    tax_conversion = provision - cash_tax
    operating_after_tax = ebit * (pretax - provision) / pretax
    after_tax_nonoperating = (pretax - ebit) * (pretax - provision) / pretax
    trade = sum((Q(t['cash_contribution_usd']) for t in terms if t['role'] == 'named_trade_movement'), Q())
    mixed = sum((Q(t['cash_contribution_usd']) for t in terms if t['role'] == 'mixed_asset_liability_movement'), Q())
    # Independent cash reconciliation derivation; do not call the generator.
    unclassified = cfo - ni - da - sbc - trade
    adjusted_unclassified = unclassified - tax_conversion
    diagnostic = cfo - capex - sbc - after_tax_nonoperating - tax_conversion
    broad = operating_after_tax + da + trade + mixed - capex
    assert diagnostic == operating_after_tax + da + trade + adjusted_unclassified - capex
    assert exact(actual['aggregate_before_tax_conversion']) == unclassified
    assert exact(actual['aggregate_after_tax_conversion_UNCLASSIFIED']) == adjusted_unclassified
    assert exact(actual['provision_minus_cash_tax']) == tax_conversion
    assert exact(actual['tax_timing_diagnostic_NOT_FCFF']) == diagnostic
    assert exact(actual['broad_statement_movement_diagnostic_NOT_FCFF']) == broad
    assert actual['verified_operating_fcff_usd'] is None
    assert actual['balancing_plug_used'] is False
    assert actual['eligible_for_forecast_calibration'] is False
    apple_rows.append({'fiscal_year': old['fiscal_year'], 'provision_minus_cash_tax_usd': str(tax_conversion),
                       'unclassified_after_conversion_usd': str(adjusted_unclassified),
                       'diagnostic_exact_fraction_usd': str(diagnostic), 'bridge_difference_usd': '0',
                       'certified_operating_fcff_usd': None})

counts = Counter()
strict_failures = []
metric_rows = []
step2 = read(EXEC/'step-2-financing.json')
step3 = read(EXEC/'step-3-alphabet-ownership.json')
google_schedule = read(BASE/'GOOGL/implementation-2026-11-03/schedules.json')
for ticker in ('AAPL', 'META', 'GOOGL'):
    originals = read(BASE/ticker/'results.json')['periods']
    company = projection['companies'][ticker]
    assert company['status'] == 'OPEN' and company['review_passed'] is False
    for i, (old, live) in enumerate(zip(originals, company['periods'], strict=True)):
        year = 2021+i
        assert old['fiscal_year'] == live['fiscal_year'] == year
        ff = live['fcff']; fe = live['fcfe']
        ops = ff['operands']
        cash_fcf = Q(ops['cfo']) - Q(ops['cash_ppe'])
        assert cash_fcf == Q(live['reported_cash_fcf_usd'])
        if ops['interest_expense'] is None:
            assert ticker == 'AAPL' and year >= 2024
            assert ff['amount_usd'] is None and ff['cleared'] is False
            expected_ff = 'MISSING_REQUIRED_INPUT'
            strict_failures.append([ticker, year, 'FCFF'])
            counts['missing_required_input'] += 1
        else:
            recomputed = cash_fcf + Q(ops['interest_expense']) * (1-Q(ops['tax_provision'])/Q(ops['pretax_income']))
            assert abs(recomputed - Q(ff['amount_usd'])) < Q(1,10**30)
            assert ff['cleared'] is True and ff['valuation_basis_aligned'] is False
            expected_ff = 'AVAILABLE_STATED_CONVENTION'
            counts['fcff_available'] += 1
        funding = old['financing_source_rows'] if ticker == 'AAPL' else old['financing']['source_rows']
        components = []
        totals = []
        debt = Q()
        for row in funding:
            assert verify_point(row['source']) == Q(row['raw_value_usd'])
            signed = Q(row['raw_value_usd']) * row['cash_sign']
            assert signed == Q(row['signed_cash_usd'])
            if row['classification'] == 'FINANCING_TOTAL':
                totals.append(signed)
            else:
                components.append(signed)
                if row['included_in_net_borrowing']:
                    assert row['classification'] in ('DEBT_FUNDING_OR_PRINCIPAL', 'LEASE_PRINCIPAL')
                    debt += signed
                if row['classification'] == 'NONCONTROLLING_CAPITAL_NOT_DEBT':
                    assert row['included_in_net_borrowing'] is False
        assert len(totals) == 1 and sum(components, Q()) == totals[0]
        assert debt == Q(live['identified_net_borrowing_usd'])
        assert cash_fcf + debt == Q(fe['amount_usd'])
        for receipt in old.get('investment_receipt_sources', []):
            assert verify_point(receipt['source']) == Q(receipt['raw_value_usd'])
        assert fe['cleared'] is False and fe['parent_common_amount_usd'] is None
        strict_failures.append([ticker, year, 'PARENT_COMMON_FCFE'])
        if ticker in ('AAPL', 'META'):
            actual = step2['companies'][ticker]['periods'][i]
            assert Q(actual['provisional_fcfe_usd']) == cash_fcf + debt
            assert actual['complete_fcfe_usd'] is None and actual['unknown_assumed_zero'] is False
            assert actual['debt_content_of_other_usd'] is None and actual['other_net_is_uncertainty_bound'] is False
            expected_fe = 'PROVISIONAL_INCOMPLETE_FINANCING'; counts['provisional_fcfe'] += 1
        else:
            actual = step3['periods'][i]; own = google_schedule['periods'][i]['ownership_schedule']
            assert Q(actual['consolidated_fcfe_usd']) == cash_fcf + debt
            assert actual['parent_common_fcfe_usd'] is None and actual['nci_fair_value_usd'] is None
            assert own['book_nci_used_as_fair_value'] is False
            assert own['outside_capital_included_in_borrowing'] is False
            assert google_schedule['periods'][i]['lease_schedule']['additional_cash_deduction_usd'] == '0'
            assert actual['parent_value_bridge']['status'] == 'NOT_POPULATED_NO_VALUE_INFERRED'
            assert actual['parent_value_bridge']['parent_common_value_usd'] is None
            expected_fe = 'AVAILABLE_CONSOLIDATED_STATED_CONVENTION'; counts['consolidated_fcfe_available'] += 1
        metric_rows.extend([{'ticker': ticker, 'year': year, 'metric': 'FCFF', 'classification': expected_ff},
                            {'ticker': ticker, 'year': year, 'metric': 'FCFE', 'classification': expected_fe}])
assert len(metric_rows) == 30 and len(strict_failures) == 17
assert dict(counts) == {'fcff_available': 13, 'provisional_fcfe': 10, 'missing_required_input': 2, 'consolidated_fcfe_available': 5}
input_source_checks = []
concepts = {'cfo': {'NetCashProvidedByUsedInOperatingActivities'},
            'cash_ppe': {'PaymentsToAcquirePropertyPlantAndEquipment'},
            'tax_provision': {'IncomeTaxExpenseBenefit'},
            'pretax_income': {'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
                             'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'},
            'interest_expense': {'InterestExpense', 'InterestExpenseNonoperating'}}
for ticker, cik in [('AAPL', 320193), ('META', 1326801), ('GOOGL', 1652044)]:
    for old, p in zip(read(BASE/ticker/'results.json')['periods'], projection['companies'][ticker]['periods'], strict=True):
        for key, value in p['fcff']['operands'].items():
            if value is None or key not in concepts:
                continue
            expected = Q(value)
            if key == 'cash_ppe' and ticker != 'AAPL':
                expected += exact(old['identified_receipts'])
            matches = []
            for digest, tree in parsed.items():
                contexts = set()
                for c in tree.iter('{http://www.xbrl.org/2003/instance}context'):
                    fields = {e.tag.rsplit('}',1)[-1]: e.text for e in c.iter()}
                    if fields.get('startDate') != p['annual_start'] or fields.get('endDate') != p['annual_end']:
                        continue
                    if int(fields.get('identifier', '0')) != cik:
                        continue
                    if any(e.tag.endswith('explicitMember') or e.tag.endswith('typedMember') for e in c.iter()):
                        continue
                    contexts.add(c.attrib['id'])
                for e in tree.iter():
                    if e.attrib.get('contextRef') in contexts and e.tag.rsplit('}',1)[-1] in concepts[key] and Q(e.text.strip()) == expected:
                        matches.append({'source_instance_sha256': digest, 'concept': e.tag, 'context_id': e.attrib['contextRef']})
            assert matches, (ticker, p['fiscal_year'], key, str(expected), 'No corresponding retained source fact')
            input_source_checks.append({'ticker': ticker, 'fiscal_year': p['fiscal_year'], 'operand': key,
                                        'gross_reported_value_usd': str(expected), 'retained_source_matches': matches})
report = {'verdict': 'PASS_RECOMPUTATION_WITH_OPEN_FINANCIAL_GAPS', 'implementation_scope': 'Three companies, FY2021–FY2025',
          'no_implementation_calculation_imports': True, 'arithmetic': 'fractions.Fraction',
          'apple_exact_bridges': apple_rows, 'availability_30_cells': metric_rows,
          'counts': dict(counts), 'strict_parent_common_failed_cells': strict_failures,
          'strict_failure_count': len(strict_failures), 'source_observations_rechecked': source_observations,
          'retained_source_body_hashes_rechecked': len(receipt_hashes),
          'cash_formula_operand_source_checks': input_source_checks,
          'source_values_unchanged': True, 'parent_common_amounts_created': 0,
          'financial_completion': 'OPEN',
          'scope_limitations': ['Source facts verified against retained extracted XBRL instances and receipt hashes; no new public filing acquisition.',
                                'Approved economic classifications were audited, not independently re-adopted.',
                                'Exact cash identities do not establish pure operating working capital or expense-aligned D&A.',
                                'No browser interaction, market-input certification, parent valuation or per-share certification in this arithmetic audit.']}
(HERE/'results.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
print(json.dumps({key: report[key] for key in ('verdict','counts','strict_failure_count','source_observations_rechecked','retained_source_body_hashes_rechecked','financial_completion')}, indent=2))
