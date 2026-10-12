#!/usr/bin/env python3
"""Bounded retained-repository availability audit, not financial research."""
from collections import Counter
import json
import subprocess

from build_selected_filing_manifest import ROOT, build
from validate_preparation_bindings import digest, local

REVISION = '56b24f11d66e88f73001f7959e3478fdbf764e5a'
MANIFEST = 'docs/phase1-selected-filing-identity-manifest.json'


def retained(path):
    return subprocess.check_output(['git', 'show', REVISION + ':' + path], cwd=ROOT)


def matching_rows(value, cik, end, locator=''):
    """Exact declared identity candidates only; aggregate references aren't facts."""
    found = []
    if isinstance(value, dict):
        if value.get('cik') == cik and value.get('annual_end') == end:
            found.append(locator)
        for key, child in value.items():
            found.extend(matching_rows(child, cik, end, locator + '/' + key))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            found.extend(matching_rows(child, cik, end, locator + '/' + str(i)))
    return found


def availability(root, references):
    return [{'path': p, 'status': 'AVAILABLE' if local(root, p).is_file() else 'BROKEN_REFERENCE',
             'sha256_repository_file_bytes': digest(local(root, p).read_bytes())
             if local(root, p).is_file() else None} for p in sorted(set(references))]


def audit():
    before = json.loads(retained(MANIFEST))
    unresolved = [r for r in before['rows'] if r['status'] != 'VERIFIED_RETAINED_IDENTITY']
    if len(unresolved) != 27:
        raise ValueError('Pinned audit scope must be 26 missing and one incomplete')
    after = build()
    now = {(r['cik'], r['selected_annual_end']): r for r in after['rows']}
    disposition = json.loads(retained('docs/phase1-issuer-preparation-disposition.json'))
    issuers = {r['cik']: r for r in disposition['rows']}
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', REVISION], cwd=ROOT,
                                    text=True).splitlines()
    # One closed search of committed research, evidence, registries and fixtures.
    # Preparation/aggregate reports are references, not new exact-identity claims.
    paths = [p for p in paths if p.endswith(('.json', '.md')) and (
        (p.startswith('docs/') and not p.startswith(('docs/company-data-preparation/', 'docs/universe/'))
         and not p.startswith(('docs/phase1-', 'docs/project-status', 'docs/historical-normalization')))
        or p.startswith(('src/valuation_platform/normalization/', 'tests/fixtures/')))]
    catalog, contents = [], {}
    for p in sorted(paths):
        body = retained(p)
        catalog.append({'path': p, 'revision': REVISION,
                        'sha256_repository_file_bytes': digest(body)})
        contents[p] = json.loads(body) if p.endswith('.json') else body.decode()
    rows = []
    for old in unresolved:
        cik, end = old['cik'], old['selected_annual_end']
        current = now[cik, end]
        issuer = issuers[cik]
        refs = ['docs/' + p for p in issuer['references']]
        refs += ['docs/' + r['reference'] for r in issuer['retained_research']]
        refs += [c['source'] for c in old['candidates']]
        bindings = availability(ROOT, refs)
        hits = []
        for p, content in contents.items():
            if isinstance(content, (dict, list)):
                locators = matching_rows(content, cik, end)
            else:
                locators = ['line/' + str(i) for i, line in enumerate(content.splitlines(), 1)
                            if old['ticker'] in line and end in line]
            if locators:
                hits.append({'path': p, 'revision': REVISION, 'locators': locators,
                             'sha256_repository_file_bytes': next(c['sha256_repository_file_bytes']
                                 for c in catalog if c['path'] == p),
                             'meaning': 'Search hit only; not implicit annual identity proof'})
        repaired = current['status'] == 'VERIFIED_RETAINED_IDENTITY'
        if repaired:
            reason = ('Retained D&A row/5 has four same-context DEI facts, exact SEC CIK, '
                      'nondimensional annual duration and filing metadata; reviewed research explains '
                      'legacy DEI namespace. Production resolver status remains unchanged.')
            action = 'Closed identity-only repair; no new financial approval or resolver change'
            stop = 'Stop; reopen only on contradictory retained selected-identity evidence'
        else:
            reason = ('Aggregate selected end/history and issuer records exist; no exact selected '
                      'accession/form/annual-start evidence in the closed retained source set. '
                      'No required identity artifact located; not proof SEC disclosure is absent.')
            action = 'Retain missing binding; no further retained-source search in this pass'
            stop = ('Reopen only when an exact selected-filing metadata/DEI artifact is supplied '
                    'or separately authorized retrieval proves CIK/accession/form/annual dates')
        rows.append({'ticker': old['ticker'], 'cik': cik, 'annual_end': end,
                     'prior_status': old['status'], 'current_status': current['status'],
                     'disposition': 'REPAIRED' if repaired else 'RETAINED_IDENTITY_ARTIFACT_UNAVAILABLE',
                     'reference_bindings': bindings, 'retained_search_hits': hits,
                     'existing_candidates': old['candidates'], 'verified_identity': current['identity'],
                     'missing_identity_fields': [] if repaired else ['accession', 'form', 'annual_start'],
                     'artifact_digest_limit': 'Repository bytes verified; inventory-recorded instance hashes are not reverified response bodies',
                     'conflicting_evidence': False, 'reason': reason, 'bounded_action': action,
                     'stopping_condition': stop, 'measure_fact_provenance': 'NOT_ESTABLISHED',
                     'financial_input_sufficiency': 'NOT_ASSESSED'})
    return {'version': 'retained-identity-availability-v1', 'baseline_revision': REVISION,
            'baseline_manifest_sha256': digest(retained(MANIFEST)),
            'search_scope': 'One closed scan of pinned committed research/evidence JSON/Markdown, policy registries and retained fixture JSON; current declared references checked separately. No /tmp artifacts or external URLs fetched.',
            'searched_sources': catalog, 'scope_count': len(rows),
            'disposition_counts': dict(Counter(r['disposition'] for r in rows)),
            'broken_reference_count': sum(b['status'] == 'BROKEN_REFERENCE' for r in rows for b in r['reference_bindings']),
            'conflicting_count': sum(r['conflicting_evidence'] for r in rows),
            'selected_period_count': after['selected_period_count'],
            'history_exception_count': after['history_exception_count'],
            'manifest_status_counts': after['status_counts'], 'rows': rows}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
