#!/usr/bin/env python3
"""Offline preparation accounting, never financial sufficiency certification."""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICIES = (
    'src/valuation_platform/normalization/concepts.py',
    'src/valuation_platform/normalization/balance_sheet.py',
    'src/valuation_platform/normalization/derived.py',
    'src/valuation_platform/normalization/diluted_shares.py',
    'src/valuation_platform/normalization/operating_nwc.py',
)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def local(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Evidence path escapes repository')
    return path


def links(root, record):
    errors = []
    for target in re.findall(r'\]\(([^)]+)\)', record.read_text()):
        if '://' in target:
            continue  # Not an HTTP check or validation of external contents.
        name, _, anchor = target.partition('#')
        path = local(root, str(record.parent.relative_to(root) / name)) if name else record
        if not path.is_file():
            errors.append('broken_reference:' + target)
        elif anchor and path.suffix == '.md':
            slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-')
                     for h in re.findall(r'^#+\s+(.+)$', path.read_text(), re.M)]
            if anchor not in slugs:
                errors.append('broken_anchor:' + target)
    return errors


def bind_row(root, row, validation, corpus):
    """PASS accounts for available evidence and explicit gaps, not complete facts."""
    errors = []
    for key, vk in [('cik', 'cik'), ('annual_ends', 'selected_annual_end_dates'),
                    ('states', 'typed_status_counts'), ('all_measure_states', 'measure_status_counts')]:
        if row[key] != validation[vk]:
            errors.append('validation_mismatch:' + key)
    if row['selected_periods'] != validation['history_period_count']:
        errors.append('history_count_mismatch')
    if (corpus['selected_annual_periods'] != row['annual_ends']
            or corpus['selected_annual_filings'] != row['selected_periods']):
        errors.append('corpus_history_mismatch')
    if validation['classification'] != row['classification']:
        errors.append('classification_mismatch')
    for key in ('cik', 'typed_status_counts', 'measure_status_counts'):
        # Runner omits zero-count status buckets; compare counts, never values.
        if (Counter(corpus[key]) != Counter(validation[key]) if key == 'typed_status_counts'
                else corpus[key] != validation[key]):
            errors.append('corpus_mismatch:' + key)
    if sum(row['states'].values()) != 17 * row['selected_periods']:
        errors.append('state_total_mismatch')
    record = local(root, 'docs/' + row['record'])
    record_hash = None
    if not record.is_file():
        errors.append('missing_record')
    else:
        record_hash = digest(record.read_bytes())
        errors.extend(links(root, record))
        if f'CIK `{row["cik"]}`' not in record.read_text():
            errors.append('record_identity_mismatch')
        measures = re.findall(r'^\| `([^`]+)` \| ([0-9/]+) \|', record.read_text(), re.M)
        if len(measures) != 17 or len({m for m, _ in measures}) != 17:
            errors.append('record_measure_set_mismatch')
        for measure, counts in measures:
            expected = [validation['measure_status_counts'].get(measure + ':' + s, 0)
                        for s in ('resolved', 'missing', 'ambiguous', 'methodology_blocked', 'not_comparable')]
            if list(map(int, counts.split('/'))) != expected:
                errors.append('record_measure_mismatch:' + measure)
    refs = []
    for name in row['references'] + [x['reference'] for x in row['retained_research']]:
        p = local(root, 'docs/' + name)
        refs.append({'path': 'docs/' + name, 'sha256': digest(p.read_bytes()) if p.is_file() else None})
        if not p.is_file():
            errors.append('missing_evidence_reference:' + name)
    for name in POLICIES:
        if not local(root, name).is_file():
            errors.append('missing_policy_reference:' + name)
    return {
        'ticker': row['ticker'], 'cik': row['cik'], 'record': row['record'],
        'record_sha256': record_hash,
        'evidence_accounted': 'FAIL' if errors else 'PASS',
        'accounting_scope': 'Available aggregate coverage, linked policies/research and explicitly recorded binding limitations only',
        'financial_input_sufficiency': 'NOT_ASSESSED', 'consumer_contract': None,
        'history_target': 5, 'selected_periods': row['selected_periods'],
        'annual_ends': row['annual_ends'], 'states': row['states'],
        'support_classification_unchanged': row['classification'],
        'aggregate_binding': 'verified_retained_corpus_and_validation_counts',
        'policy_binding': 'documented_frozen_family_references_not_per_fact_policy_verification',
        'exact_history_and_fact_binding': 'INSUFFICIENT_FOR_WHOLE_HISTORY',
        'limitations': ['Compact corpus has counts, not selected accession/annual-start or exact fact occurrences.',
                        'Linked research is retained evidence, not a new independent fact-level verification.',
                        'Generic policy file existence is not proof of per-output policy application.',
                        'Five-year exceptions, revenue conflicts and original financial blockers remain.'],
        'independently_reviewed_packages': [], 'evidence_references': refs,
        'errors': errors,
    }


def run(root=ROOT, verify_pilots=True):
    root = root.resolve()
    dp = root / 'docs/phase1-issuer-preparation-disposition.json'
    d = json.loads(dp.read_bytes())
    vp = root / 'docs' / d['validation_reference']
    if digest(vp.read_bytes()) != d['validation_sha256']:
        raise ValueError('Pinned validation bytes changed')
    v = json.loads(vp.read_bytes())
    body = gzip.decompress(base64.b64decode(v['source_corpus']['original_body_gzip_base64'], validate=True))
    if digest(body) != v['source_corpus']['sha256'] or len(body) != v['source_corpus']['byte_length']:
        raise ValueError('Original retained corpus digest/length mismatch')
    corpus = {x['cik']: x for x in json.loads(body)['issuers']}
    universe = root / 'docs/universe/sp500-top-50-2026-10-02.csv'
    if digest(universe.read_bytes()) != v['frozen_universe_sha256']:
        raise ValueError('Frozen universe identity bytes changed')
    vr = {x['cik']: x for x in v['rows'] if x['classification'] == 'GENERALIZATION_REQUIRED'}
    if len(d['rows']) != 40 or len({r['cik'] for r in d['rows']}) != 40 or {r['cik'] for r in d['rows']} != set(vr):
        raise ValueError('Exactly forty unique generalization issuers required')
    index = (root / 'docs/company-data-preparation/index.md').read_text()
    mapping = re.findall(r'\| [A-Z, /]+ \| (\d+) \| (\d+) \| \[[^]]+\]\(([^)]+)\)', index)
    if len(mapping) != 40 or {(int(c), int(n), 'company-data-preparation/' + p) for c, n, p in mapping} != {(r['cik'], r['selected_periods'], r['record']) for r in d['rows']}:
        raise ValueError('Register mapping differs from disposition')
    results = [bind_row(root, r, vr[r['cik']], corpus[r['cik']]) for r in d['rows']]
    if verify_pilots:
        sys.path.insert(0, str(root / 'src'))
        from valuation_platform.analyst import cash_flow_inputs as msft
        from valuation_platform.analyst import aapl_cash_flow_inputs as aapl
        from valuation_platform.analyst import googl_cash_flow_inputs as googl
        adapters = {789019: (msft, msft.load_msft_bundle), 320193: (aapl, aapl.load_aapl_bundle),
                    1652044: (googl, googl.load_googl_bundle)}
        for row, result in zip(d['rows'], results):
            for package in row['input_packages']:
                try:
                    adapter, loader = adapters[row['cik']]
                    bundle = loader(package['id'])
                    if adapter.deserialize(adapter.serialize(bundle)) != bundle:
                        raise ValueError('Round trip differs')
                    expected = package['period']
                    actual = {'cik': bundle.period.cik, 'accession': bundle.period.accession,
                              'annual_start': bundle.period.annual_start.isoformat(),
                              'annual_end': bundle.period.annual_end.isoformat()}
                    if actual != expected:
                        raise ValueError('Reviewed identity differs')
                    result['independently_reviewed_packages'].append({**package, 'binding': 'PASS',
                        'input_count': len(bundle.inputs), 'occurrences': sum(len(i.occurrences) for i in bundle.inputs),
                        'unknown_count': len(bundle.unknowns), 'financial_sufficiency': 'NOT_ASSESSED'})
                except (ValueError, OSError, KeyError) as exc:
                    result['errors'].append('pilot_binding:' + str(exc))
                    result['evidence_accounted'] = 'FAIL'
    else:
        for result in results:
            result['limitations'].append('Pilot receipt/fact binding not executed in this invocation.')
    return {'version': 'preparation-evidence-binding-v1', 'scope': 'Phase 1 accounting only; no financial consumer approved',
            'disposition_sha256': digest(dp.read_bytes()), 'validation_sha256': digest(vp.read_bytes()),
            'corpus_sha256': digest(body), 'policy_references': list(POLICIES),
            'frozen_contract': {'path': 'docs/historical-normalization-v1-freeze.md',
                                'sha256_repository_file_bytes': digest((root / 'docs/historical-normalization-v1-freeze.md').read_bytes())},
            'policy_reference_hashes': {p: digest(local(root, p).read_bytes()) for p in POLICIES if local(root, p).is_file()},
            'counts': dict(Counter(r['evidence_accounted'] for r in results)),
            'financial_sufficiency_counts': dict(Counter(r['financial_input_sufficiency'] for r in results)),
            'selected_periods': sum(r['selected_periods'] for r in results), 'rows': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        report = run(args.root)
        print(json.dumps(report, indent=2))
        sys.exit(1 if report['counts'].get('FAIL') else 0)
    except (ValueError, OSError, KeyError) as exc:
        print('Binding validation failed: ' + str(exc), file=sys.stderr)
        sys.exit(1)
