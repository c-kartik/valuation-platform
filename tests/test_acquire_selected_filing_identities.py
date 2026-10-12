import copy
from datetime import date
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import acquire_selected_filing_identities as acquisition
from valuation_platform.sec.filing_selection import select_filings, FilingSelectionError
from valuation_platform.sec.submissions import SECFiling


class AcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / acquisition.RECEIPTS).read_bytes())

    def test_offline_reproducible_replay_exact_scope(self):
        a = acquisition.verify(self.payload)
        self.assertEqual(a, acquisition.verify(self.payload))
        self.assertEqual(len(a), 26)
        self.assertEqual(len({(r['cik'], r['annual_end']) for r in a}), 26)
        self.assertEqual(self.payload['request_count'], 60)
        self.assertEqual(len(self.payload['artifacts']), 60)

    def test_every_body_digest_and_new_receipt_metadata(self):
        for a in self.payload['artifacts']:
            self.assertTrue(acquisition.body_of(a))
            self.assertEqual(a['retrieval_mode'], 'new_authorized_fixed_scope_identity_acquisition')
            self.assertEqual(a['http_status'], 200)
            self.assertNotIn('User-Agent', a['response_headers'])

    def test_digest_representation_precision_and_metadata_failures(self):
        artifact = self.payload['artifacts'][0]
        for field, value in [('sha256', '0'*64), ('byte_length', 0), ('representation', 'reserialized_json'),
                             ('digest_type', 'repository_file_bytes'), ('http_status', None),
                             ('retrieved_at_utc', None), ('retrieved_at_utc', '2026-10-12T00:00:00')]:
            bad = copy.deepcopy(artifact); bad[field] = value
            with self.assertRaises(ValueError): acquisition.body_of(bad)

    def test_wrong_scope_cutoff_and_request_accounting_rejected(self):
        for field, value in [('rows', self.payload['rows'][:-1]), ('frozen_run_cutoff', '2026-01-01'),
                             ('baseline_manifest_sha256', '0'*64), ('request_count', 0)]:
            bad = {**self.payload, field: value}
            with self.assertRaises(ValueError): acquisition.verify(bad)

    def test_wrong_accession_form_dates_or_dei_evidence_cannot_bind(self):
        for key, value in [('accession', '0000000000-26-000001'), ('form', '10-K/A'),
                           ('annual_start', '2025-01-01')]:
            rows = copy.deepcopy(self.payload['rows']); rows[0]['identity'][key] = value
            with self.assertRaises(ValueError): acquisition.verify({**self.payload, 'rows': rows})

    def test_duplicate_or_nonofficial_artifact_rejected(self):
        with self.assertRaises(ValueError): acquisition.ReplayClient([self.payload['artifacts'][0]]*2)
        a = {**self.payload['artifacts'][0], 'source_url': 'https://example.com/metadata'}
        with self.assertRaises(ValueError): acquisition.ReplayClient([a])

    def test_selector_never_guesses_amended_or_conflicting_accessions(self):
        f = SECFiling('0000000123-25-000001', '10-K', date(2025,2,1), date(2024,12,31), 'a.htm')
        amendment = SECFiling('0000000123-25-000002', '10-K/A', f.filing_date, f.report_date, 'b.htm')
        self.assertEqual(select_filings([f, amendment]).annual, (f,))
        duplicate = SECFiling(amendment.accession_number, '10-K', f.filing_date, f.report_date, 'b.htm')
        with self.assertRaises(FilingSelectionError): select_filings([f, duplicate])

    def test_old_163_identities_and_history_exceptions_are_preserved(self):
        from build_selected_filing_manifest import build
        old = json.loads(acquisition.pinned('docs/phase1-selected-filing-identity-manifest.json'))
        new = build()
        self.assertEqual(old['history_exceptions'], new['history_exceptions'])
        for before, after in zip(old['rows'], new['rows']):
            if before['status'] == 'VERIFIED_RETAINED_IDENTITY': self.assertEqual(before, after)
            self.assertEqual(after['measure_fact_provenance'], 'NOT_ESTABLISHED')
        self.assertEqual(new['financial_input_sufficiency'], 'NOT_ASSESSED')

    def test_explicit_unresolved_entries_cannot_certify_identity(self):
        rows = copy.deepcopy(self.payload['rows'])
        for r in rows:
            r.update(status='UNRESOLVED', identity=None, reason='Exact selection not established')
        p = {**self.payload, 'rows': rows, 'status_counts': {'UNRESOLVED': 26}}
        self.assertEqual(acquisition.verify(p), [])
        rows[0]['identity'] = self.payload['rows'][0]['identity']
        with self.assertRaises(ValueError): acquisition.verify(p)
