#!/usr/bin/env python3
"""Retained filing identity joins only; no retrieval or financial approval."""
from collections import Counter
import base64
import gzip
from datetime import date
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from validate_preparation_bindings import ROOT, digest, local

SOURCES = ('docs/capex-inventory.json', 'docs/depreciation-amortization-inventory.json',
           'docs/analyst-operating-nwc-inventory.json')
TABLES = ('docs/operating-income-concepts.md', 'docs/pretax-income-concepts.md')
REGISTRIES = ('docs/company-data-preparation/msft-reported-cash-flow-bundles.json',
              'docs/company-data-preparation/aapl-reported-cash-flow-bundle.json',
              'docs/company-data-preparation/googl-reported-cash-flow-bundle.json')


def candidate(source, index, cik, accession, form, start, end, verified, artifacts=()):
    return {'source': source, 'locator': index, 'cik': cik, 'accession': accession,
            'form': form, 'annual_start': start, 'annual_end': end,
            'identity_evidence_sufficient': verified, 'artifacts': list(artifacts)}


def classify(cik, end, candidates):
    issues = []
    valid = []
    for c in candidates:
        try:
            correct = (c['cik'] == cik and c['annual_end'] == end and c['form'] == '10-K'
                       and re.fullmatch(r'\d{10}-\d{2}-\d{6}', c['accession'] or '')
                       and date.fromisoformat(c['annual_start']) < date.fromisoformat(end))
        except (ValueError, TypeError):
            correct = False
        if correct and c['identity_evidence_sufficient']:
            valid.append(c)
        else:
            issues.append({'source': c['source'], 'locator': c['locator'],
                           'reason': 'Incomplete, malformed, unresolved or mismatched identity; not implicitly approved'})
    signatures = {(c['accession'], c['form'], c['annual_start'], c['annual_end']) for c in valid}
    if len(signatures) > 1:
        status, identity = 'CONFLICTING', None
    elif len(signatures) == 1:
        accession, form, start, annual_end = next(iter(signatures))
        status = 'VERIFIED_RETAINED_IDENTITY'
        identity = {'cik': cik, 'accession': accession, 'form': form,
                    'annual_start': start, 'annual_end': annual_end}
    else:
        status, identity = ('INCOMPLETE_BINDING' if candidates else 'MISSING_BINDING'), None
    return {'status': status, 'identity': identity, 'candidates': candidates,
            'binding_issues': issues, 'measure_fact_provenance': 'NOT_ESTABLISHED'}


def collect(root, ticker_ciks):
    claims = []
    hashes = {}
    manifest_path = 'docs/evidence/analyst-operating-nwc-response-bodies.json'
    manifest_body = local(root, manifest_path).read_bytes()
    hashes[manifest_path] = digest(manifest_body)
    retained = json.loads(manifest_body)['artifacts']
    for source in SOURCES:
        p = local(root, source); hashes[source] = digest(p.read_bytes())
        for i, row in enumerate(json.loads(p.read_bytes())['rows']):
            filing = row.get('filing', {})
            accession = filing.get('accession_number', row.get('accession'))
            sufficient = (row.get('annual_resolver_status') == 'annual_period_resolved'
                          and filing.get('report_date') == row['annual_end'])
            if sufficient:
                contexts = row['contexts']
                contexts = contexts.values() if isinstance(contexts, dict) else contexts
                matching = [c for c in contexts if c.get('start') == row['annual_start']
                            and c.get('end') == row['annual_end'] and not c.get('dimensions')
                            and str(c.get('entity_identifier', '')).isdigit()
                            and int(c['entity_identifier']) == row['cik']]
                sufficient = bool(matching) and any(e['concept'] == 'DocumentFiscalPeriodFocus'
                                                   and e['raw_value'] == 'FY' for e in row['annual_dei_evidence'])
            artifacts = []
            if source.endswith('analyst-operating-nwc-inventory.json'):
                entries = [a for a in retained if a['source_url'] == row['instance_url']]
                if len(entries) == 1:
                    a = entries[0]
                    body = gzip.decompress(base64.b64decode(a['response_body_gzip_base64'], validate=True))
                    if digest(body) != a['sha256'] or len(body) != a['byte_length']:
                        raise ValueError('Retained instance digest/length differs')
                    xml = ET.fromstring(body)
                    ns = {'x': 'http://www.xbrl.org/2003/instance'}
                    eligible = []
                    for c in xml.findall('x:context', ns):
                        entity = c.find('x:entity/x:identifier', ns)
                        start = c.find('x:period/x:startDate', ns); end = c.find('x:period/x:endDate', ns)
                        dimensional = any(x.tag.endswith(('explicitMember', 'typedMember')) for x in c.iter())
                        if (entity is not None and (entity.text or '').isdigit()
                                and int(entity.text) == row['cik'] and start is not None and end is not None
                                and start.text == row['annual_start'] and end.text == row['annual_end'] and not dimensional):
                            eligible.append(c.get('id'))
                    dei = {(f.tag.rsplit('}', 1)[-1], f.text) for f in xml
                           if f.tag.startswith('{http://xbrl.sec.gov/dei/') and f.get('contextRef') in eligible}
                    sufficient = {('DocumentType', '10-K'), ('DocumentFiscalPeriodFocus', 'FY'),
                                  ('DocumentPeriodEndDate', row['annual_end'])}.issubset(dei)
                    if sufficient:
                        filing['form'] = '10-K'  # Read from the retained DEI fact, not a default.
                    artifacts.append({'url': a['source_url'], 'sha256': a['sha256'],
                                      'representation': a['representation'], 'digest_type': a['digest_type'],
                                      'retrieved_at_utc': a['retrieved_at_utc'], 'http_status': a['http_status'],
                                      'verification': 'Original retained bytes and exact annual DEI/entity context checked',
                                      'manifest': manifest_path})
            if row.get('instance_sha256'):
                artifacts.append({'url': row['source_url'], 'sha256': row['instance_sha256'],
                                  'digest_basis': 'retained_inventory_instance_fingerprint_not_reverified_body_or_receipt'})
            claims.append(candidate(source, 'rows/' + str(i), row['cik'], accession,
                                    filing.get('form'), row['annual_start'], row['annual_end'],
                                    sufficient, artifacts))
    for source in TABLES:
        p = local(root, source); hashes[source] = digest(p.read_bytes())
        # These reviewed inventories explicitly state selected 10-K and DEI annual basis.
        for lineno, line in enumerate(p.read_text().splitlines(), 1):
            cells = [x.strip() for x in line.split('|')]
            if len(cells) < 5 or cells[1] not in ticker_ciks:
                continue
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', cells[2] if 'operating-income' in source else cells[4])
            acc = re.fullmatch(r'`(\d{10}-\d{2}-\d{6})`', cells[3])
            if len(dates) == 2 and acc:
                claims.append(candidate(source, 'line/' + str(lineno), ticker_ciks[cells[1]],
                                        acc[1], '10-K', dates[0], dates[1], True))
    for source in REGISTRIES:
        p = local(root, source); hashes[source] = digest(p.read_bytes())
        for i, bundle in enumerate(json.loads(p.read_bytes())['bundles']):
            period = bundle['period']
            # No inferred form: actual registry artifacts are bound to existing reviewed loaders.
            artifacts = [{k: a[k] for k in ('source_url', 'sha256', 'representation', 'digest_type',
                                           'retrieved_at_utc', 'http_status')} for a in bundle['artifacts']]
            claims.append(candidate(source, 'bundles/' + str(i), period['cik'], period['accession'],
                                    '10-K', period['annual_start'], period['annual_end'], True, artifacts))
    return claims, hashes


def build(root=ROOT):
    root = root.resolve()
    p = root / 'docs/phase1-issuer-preparation-disposition.json'
    d = json.loads(p.read_bytes())
    vpath = root / 'docs' / d['validation_reference']
    if digest(vpath.read_bytes()) != d['validation_sha256']:
        raise ValueError('Pinned validation changed')
    v = json.loads(vpath.read_bytes())
    vr = {r['cik']: r for r in v['rows'] if r['classification'] == 'GENERALIZATION_REQUIRED'}
    if len(d['rows']) != 40 or len({r['cik'] for r in d['rows']}) != 40 or {r['cik'] for r in d['rows']} != set(vr):
        raise ValueError('Forty unique frozen issuer mappings required')
    claims, hashes = collect(root, {r['ticker']: r['cik'] for r in d['rows']})
    rows, exceptions = [], []
    for issuer in d['rows']:
        if issuer['annual_ends'] != vr[issuer['cik']]['selected_annual_end_dates']:
            raise ValueError('Selected annual ends changed')
        for end in issuer['annual_ends']:
            matches = [c for c in claims if c['cik'] == issuer['cik'] and c['annual_end'] == end]
            rows.append({'ticker': issuer['ticker'], 'cik': issuer['cik'], 'selected_annual_end': end,
                         'selected_end_reference': d['validation_reference'], **classify(issuer['cik'], end, matches)})
        for slot in range(5 - issuer['selected_periods']):
            exceptions.append({'ticker': issuer['ticker'], 'cik': issuer['cik'], 'unfilled_target_slot': slot + 1,
                               'status': 'HISTORY_EXCEPTION', 'accession': None, 'annual_start': None,
                               'annual_end': None, 'reason': vr[issuer['cik']]['history_assessment'],
                               'reference': issuer['record'], 'limitation': 'Target deficit only; no absent fiscal year/date or predecessor identity inferred'})
    if len(rows) != 189 or len(exceptions) != 11 or len({(r['cik'], r['selected_annual_end']) for r in rows}) != 189:
        raise ValueError('Expected 189 selected identities and 11 explicit history exceptions')
    return {'version': 'retained-selected-filing-identity-v1',
            'verification_basis': 'Consistency of retained reviewed filing/DEI evidence with frozen selected annual ends; no fresh retrieval or universal raw-body revalidation',
            'disposition_sha256': digest(p.read_bytes()), 'validation_sha256': digest(vpath.read_bytes()),
            'source_repository_file_sha256': hashes, 'issuer_count': 40, 'history_target': 200,
            'selected_period_count': len(rows), 'history_exception_count': len(exceptions),
            'status_counts': dict(Counter(r['status'] for r in rows)),
            'financial_input_sufficiency': 'NOT_ASSESSED', 'rows': rows, 'history_exceptions': exceptions}


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
