#!/usr/bin/env python3
"""One authorized 26-entry SEC pass; offline receipt replay is the default."""
import argparse
import base64
from collections import Counter
from datetime import date, datetime, timezone
import gzip
from functools import lru_cache
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from validate_preparation_bindings import ROOT, digest
sys.path.insert(0, str(ROOT / 'src'))
from valuation_platform.sec.client import SECClient
from valuation_platform.sec.submissions import fetch_submissions, fetch_submission_history, SECFiling
from valuation_platform.sec.filing_selection import select_filings
from valuation_platform.sec.filing_xbrl import fetch_filing_xbrl, parse_filing_xbrl_instance
from valuation_platform.sec.annual_period import resolve_annual_period, ResolvedAnnualPeriod
from valuation_platform.sec.tickers import SECCompanyIdentity

BASELINE = '149fe9a1f64105a49cfc537b57b695ff11313630'
RECEIPTS = 'docs/evidence/selected-filing-identity-acquisition.json'


@lru_cache(maxsize=4)
def pinned(path):
    # Reuse immutable Git-revision bytes within this offline process only.
    # No network cache, persistent storage or new retrieval behavior.
    return subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT)


def scope():
    m = json.loads(pinned('docs/phase1-selected-filing-identity-manifest.json'))
    rows = [r for r in m['rows'] if r['status'] == 'MISSING_BINDING']
    if len(rows) != 26 or len({(r['cik'], r['selected_annual_end']) for r in rows}) != 26:
        raise ValueError('Fixed 26-entry scope required')
    return rows


def cutoff():
    v = json.loads(pinned('docs/universe/phase-1h5-issuer-validation.json'))
    body = gzip.decompress(base64.b64decode(v['source_corpus']['original_body_gzip_base64'], validate=True))
    if digest(body) != v['source_corpus']['sha256']:
        raise ValueError('Frozen corpus digest mismatch')
    return datetime.fromisoformat(json.loads(body)['run_timestamp'])


def company(row):
    return SECCompanyIdentity(row['ticker'], row['cik'], f"{row['cik']:010d}", row['ticker'],
                              'Frozen issuer/CIK mapping; no ticker re-resolution', cutoff())


def body_of(receipt):
    if receipt['representation'] != 'sec_response_body_bytes' or receipt['digest_type'] != 'sha256_sec_response_body_bytes':
        raise ValueError('Incorrect response representation')
    encoded = receipt['response_body_gzip_base64']
    if isinstance(encoded, list):
        encoded = ''.join(encoded)  # Storage chunks only; digest is original decoded response bytes.
    body = gzip.decompress(base64.b64decode(encoded, validate=True))
    if len(body) != receipt['byte_length'] or digest(body) != receipt['sha256']:
        raise ValueError('Response digest/length mismatch')
    if receipt['http_status'] != 200 or not receipt['retrieved_at_utc']:
        raise ValueError('Missing successful new retrieval metadata')
    if datetime.fromisoformat(receipt['retrieved_at_utc']).tzinfo is None:
        raise ValueError('Retrieval timestamp must be timezone aware')
    return body


class ReplayClient:
    def __init__(self, artifacts):
        self.bodies = {}
        for a in artifacts:
            url = a['source_url']
            if not url.startswith(('https://data.sec.gov/submissions/', 'https://www.sec.gov/Archives/edgar/data/')):
                raise ValueError('Nonofficial evidence URL')
            if url in self.bodies:
                raise ValueError('Duplicate response identity')
            self.bodies[url] = body_of(a)

    def get_json(self, url):
        return json.loads(self.bodies[url])

    def get_bytes(self, url):
        return self.bodies[url]


def verify(payload):
    targets = {(r['cik'], r['selected_annual_end']) for r in scope()}
    if payload['baseline_revision'] != BASELINE or payload['frozen_run_cutoff'] != cutoff().isoformat():
        raise ValueError('Baseline/cutoff mismatch')
    if payload['baseline_manifest_sha256'] != digest(pinned('docs/phase1-selected-filing-identity-manifest.json')):
        raise ValueError('Baseline manifest hash mismatch')
    rows = payload['rows']
    if payload['scope_count'] != 26 or len(rows) != 26 or {(r['cik'], r['annual_end']) for r in rows} != targets:
        raise ValueError('Fixed scope changed or duplicated')
    if payload['request_count'] != len(payload['attempts']):
        raise ValueError('Request count mismatch')
    client = ReplayClient(payload['artifacts'])
    if len(payload['artifacts']) != len([a for a in payload['attempts'] if a['http_status'] is not None]):
        raise ValueError('Response/attempt accounting differs')
    for a in payload['artifacts']:
        matches = [x for x in payload['attempts'] if x['source_url'] == a['source_url']]
        if len(matches) != 1 or matches[0]['http_status'] != a['http_status'] or matches[0]['request_started_at_utc'] != a['request_started_at_utc']:
            raise ValueError('Receipt not bound to unique request attempt')
    claims = []
    for cik in dict.fromkeys(r['cik'] for r in rows):
        group = [r for r in rows if r['cik'] == cik]
        verified = [r for r in group if r['status'] == 'VERIFIED']
        if not verified:
            if any(r['identity'] is not None or not r['reason'] for r in group):
                raise ValueError('Unresolved evidence must not supply approved identity')
            continue
        submissions = fetch_submissions(client, company({'ticker': group[0]['ticker'], 'cik': cik}))
        if int(client.get_json(submissions.source_url)['cik']) != cik:
            raise ValueError('Submissions entity differs')
        filings = [f for f in submissions.filings if f.filing_date <= cutoff().date()]
        selected = select_filings(filings)
        for history in submissions.history_files:
            if selected.has_complete_annual_history:
                break
            filings.extend(f for f in fetch_submission_history(client, history) if f.filing_date <= cutoff().date())
            selected = select_filings(filings)
        expected = next(r['annual_ends'] for r in json.loads(pinned('docs/phase1-issuer-preparation-disposition.json'))['rows'] if r['cik'] == cik)
        if [f.report_date.isoformat() for f in selected.annual] != expected:
            raise ValueError('Frozen selected history not reproduced')
        for r in verified:
            f = next(f for f in selected.annual if f.report_date.isoformat() == r['annual_end'])
            metadata = {'accession_number': f.accession_number, 'form': f.form,
                        'primary_document': f.primary_document, 'filing_date': f.filing_date.isoformat(),
                        'report_date': f.report_date.isoformat()}
            if metadata != r['filing']:
                raise ValueError('Selected accession/form/document mismatch')
            x = fetch_filing_xbrl(client, company({'ticker': r['ticker'], 'cik': cik}), f)
            identity, evidence = annual_identity(x, r['annual_end'])
            if identity != r['identity'] or evidence != r['annual_evidence'] or x.source_url != r['instance_url']:
                raise ValueError('Annual identity/evidence mismatch')
            if not set(r['request_urls']).issubset(client.bodies):
                raise ValueError('Missing binding receipt')
            claims.append(r)
    if dict(Counter(r['status'] for r in rows)) != payload['status_counts']:
        raise ValueError('Status totals differ')
    return claims


class RecordingClient(SECClient):
    def __init__(self, user_agent):
        super().__init__(user_agent, timeout=15.0)
        self.receipts = []
        self.attempts = []
        self.last_started = 0.0

    def _get_response(self, url, *, accept):
        # Serial requests, at most two starts/second, no automatic retries.
        time.sleep(max(0.0, 0.5 - (time.monotonic() - self.last_started)))
        self.last_started = time.monotonic()
        started = datetime.now(timezone.utc).isoformat()
        attempt = {'source_url': url, 'request_started_at_utc': started,
                   'http_status': None, 'outcome': 'REQUESTED'}
        self.attempts.append(attempt)
        try:
            response = self._session.get(url, headers={'User-Agent': self._user_agent, 'Accept': accept}, timeout=self._timeout)
            attempt['http_status'] = response.status_code
            body = response.content
            self.receipts.append({'source_url': url, 'request_started_at_utc': started,
                'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'http_status': response.status_code,
                'retrieval_mode': 'new_authorized_fixed_scope_identity_acquisition',
                'representation': 'sec_response_body_bytes', 'digest_type': 'sha256_sec_response_body_bytes',
                'sha256': digest(body), 'byte_length': len(body), 'storage_encoding': 'gzip_base64',
                'response_body_gzip_base64': base64.b64encode(gzip.compress(body, mtime=0)).decode(),
                'response_headers': {k: v for k, v in response.headers.items() if k.lower() in
                                     {'content-type', 'last-modified', 'etag', 'content-encoding', 'date'}}})
            response.raise_for_status()
            attempt['outcome'] = 'SUCCESS'
            return response
        except Exception as exc:
            attempt['outcome'] = 'FAILURE'
            # Transport messages contain URLs, not request headers or User-Agent.
            attempt['error_type'] = type(exc).__name__
            attempt['reason'] = str(exc)
            raise


def annual_identity(xbrl, end):
    period = resolve_annual_period(xbrl)
    if not isinstance(period, ResolvedAnnualPeriod) or period.end.isoformat() != end:
        raise ValueError('Annual DEI resolution does not uniquely match frozen annual end')
    type_facts = [f for f in xbrl.facts if f.concept == 'DocumentType'
                  and f.namespace.startswith('http://xbrl.sec.gov/dei/')
                  and f.context_id in period.evidence.context_ids]
    if not type_facts or any(f.is_nil or f.raw_value != '10-K' for f in type_facts):
        raise ValueError('Exact annual-context DEI DocumentType not established')
    return {'cik': xbrl.company.cik, 'accession': xbrl.filing.accession_number, 'form': '10-K',
            'annual_start': period.start.isoformat(), 'annual_end': period.end.isoformat()}, {
            'context_ids': list(period.evidence.context_ids),
            'dei_occurrences': [{'namespace': f.namespace, 'concept': f.concept, 'context_id': f.context_id,
                                 'raw_value': f.raw_value} for f in xbrl.facts
                                if f.namespace.startswith('http://xbrl.sec.gov/dei/')
                                and f.context_id in period.evidence.context_ids
                                and f.concept in {'DocumentType', 'DocumentFiscalPeriodFocus',
                                                  'DocumentFiscalYearFocus', 'DocumentPeriodEndDate'}]}


def acquire():
    rows = scope(); limit = cutoff()
    client = RecordingClient(os.environ.get('SEC_USER_AGENT', '').strip())
    results = []
    global_failure = None
    for cik in dict.fromkeys(r['cik'] for r in rows):
        group = [r for r in rows if r['cik'] == cik]
        if global_failure:
            results.extend({'ticker': r['ticker'], 'cik': cik, 'annual_end': r['selected_annual_end'],
                            'status': 'UNRESOLVED', 'identity': None, 'reason': global_failure,
                            'request_urls': [], 'filing': None} for r in group)
            continue
        begin = len(client.attempts)
        try:
            submissions = fetch_submissions(client, company(group[0]))
            first_payload = client.receipts[-1]
            if int(json.loads(body_of(first_payload))['cik']) != cik:
                raise ValueError('SEC submissions CIK differs')
            filings = [f for f in submissions.filings if f.filing_date <= limit.date()]
            selected = select_filings(filings)
            for history in submissions.history_files:
                if selected.has_complete_annual_history:
                    break
                filings.extend(f for f in fetch_submission_history(client, history) if f.filing_date <= limit.date())
                selected = select_filings(filings)
            by_end = {f.report_date.isoformat(): f for f in selected.annual}
            # Reproduce frozen selected ends, not a plausible same-year candidate.
            frozen = json.loads(pinned('docs/phase1-issuer-preparation-disposition.json'))
            expected = next(r['annual_ends'] for r in frozen['rows'] if r['cik'] == cik)
            if sorted(by_end) != expected:
                raise ValueError('Official submissions selection does not reproduce frozen selected ends')
            metadata_urls = [a['source_url'] for a in client.attempts[begin:]]
        except Exception as exc:
            reason = f'Selected identity metadata unavailable: {type(exc).__name__}: {exc}'
            results.extend({'ticker': r['ticker'], 'cik': cik, 'annual_end': r['selected_annual_end'],
                            'status': 'UNRESOLVED', 'identity': None, 'reason': reason,
                            'request_urls': [a['source_url'] for a in client.attempts[begin:]], 'filing': None} for r in group)
            if client.attempts and client.attempts[-1]['outcome'] == 'FAILURE':
                global_failure = 'Pass stopped after transport/access failure; no repeated retries. ' + reason
            continue
        for r in group:
            start = len(client.attempts)
            filing = by_end[r['selected_annual_end']]
            result = {'ticker': r['ticker'], 'cik': cik, 'annual_end': r['selected_annual_end'],
                      'status': 'UNRESOLVED', 'identity': None,
                      'filing': {'accession_number': filing.accession_number, 'form': filing.form,
                                 'filing_date': filing.filing_date.isoformat(), 'report_date': filing.report_date.isoformat(),
                                 'primary_document': filing.primary_document}, 'reason': None}
            try:
                if global_failure:
                    raise ValueError(global_failure)
                xbrl = fetch_filing_xbrl(client, company(r), filing)
                identity, evidence = annual_identity(xbrl, r['selected_annual_end'])
                result.update(status='VERIFIED', identity=identity, annual_evidence=evidence,
                              instance_url=xbrl.source_url,
                              reason='Unique exact 10-K selected under unchanged selector at frozen cutoff; annual DEI/context agrees')
            except Exception as exc:
                result['reason'] = f'{type(exc).__name__}: {exc}'
                if client.attempts and client.attempts[-1]['outcome'] == 'FAILURE':
                    global_failure = 'Pass stopped after transport/access failure; no repeated retries. ' + result['reason']
            result['request_urls'] = metadata_urls + [a['source_url'] for a in client.attempts[start:]]
            results.append(result)
    return {'version': 'selected-filing-sec-acquisition-v1', 'baseline_revision': BASELINE,
            'frozen_run_cutoff': limit.isoformat(), 'scope_count': 26,
            'baseline_manifest_sha256': digest(pinned('docs/phase1-selected-filing-identity-manifest.json')),
            'request_count': len(client.attempts), 'attempts': client.attempts, 'artifacts': client.receipts,
            'status_counts': dict(Counter(r['status'] for r in results)), 'rows': results,
            'limits': 'New evidence, not recovered original receipts. Identity only; fact provenance and financial sufficiency not certified.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire', action='store_true')
    args = parser.parse_args()
    if args.acquire:
        print(json.dumps(acquire(), indent=2))
    else:
        payload = json.loads((ROOT / RECEIPTS).read_bytes())
        verify(payload)
        print(json.dumps({'status_counts': payload['status_counts'], 'scope_count': payload['scope_count'],
                          'request_count': payload['request_count']}, indent=2))
