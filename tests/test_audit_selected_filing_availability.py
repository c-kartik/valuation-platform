import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import audit_selected_filing_availability as audit
from build_selected_filing_manifest import reviewed_avgo_annual_identity
from validate_preparation_bindings import digest


class AvailabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.audit()

    def test_scope_repair_counts_and_reproducibility(self):
        self.assertEqual(self.result, audit.audit())
        rows = self.result['rows']
        self.assertEqual(len(rows), 27)
        self.assertEqual(len({(r['cik'], r['annual_end']) for r in rows}), 27)
        self.assertEqual(self.result['disposition_counts'], {'REPAIRED': 1, 'VERIFIED_NEW_SEC_EVIDENCE': 26})
        self.assertEqual(self.result['manifest_status_counts'], {'VERIFIED_RETAINED_IDENTITY': 189})
        self.assertEqual(self.result['history_exception_count'], 11)
        self.assertEqual(self.result['selected_period_count'], 189)

    def test_all_scanned_revision_digests_recheck(self):
        for source in self.result['searched_sources']:
            self.assertEqual(digest(audit.retained(source['path'])), source['sha256_repository_file_bytes'])

    def test_no_false_missing_or_conflicting_reference_claims(self):
        self.assertEqual(self.result['broken_reference_count'], 0)
        self.assertEqual(self.result['conflicting_count'], 0)
        for r in self.result['rows']:
            self.assertTrue(r['bounded_action']); self.assertTrue(r['stopping_condition'])
            self.assertEqual(r['measure_fact_provenance'], 'NOT_ESTABLISHED')
            self.assertEqual(r['financial_input_sufficiency'], 'NOT_ASSESSED')
            if r['disposition'] == 'RETAINED_IDENTITY_ARTIFACT_UNAVAILABLE':
                self.assertIsNone(r['verified_identity'])
                self.assertEqual(r['missing_identity_fields'], ['accession', 'form', 'annual_start'])

    def test_broken_reference_is_not_absent_disclosure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(audit.availability(root, ['missing.json'])[0]['status'], 'BROKEN_REFERENCE')

    def test_aggregate_annual_ends_are_not_identity_candidates(self):
        self.assertEqual(audit.matching_rows({'cik': 123, 'annual_ends': ['2024-12-31']}, 123, '2024-12-31'), [])
        self.assertEqual(audit.matching_rows({'rows': [{'cik': 456, 'annual_end': '2024-12-31'}]}, 123, '2024-12-31'), [])

    def test_dei_duplicates_conflicts_and_context_mismatches_rejected(self):
        row = json.loads((ROOT / 'docs/depreciation-amortization-inventory.json').read_bytes())['rows'][5]
        for field, value in [('namespace', 'unknown'), ('context_id', 'wrong'), ('raw_value', 'wrong')]:
            bad = copy.deepcopy(row); bad['annual_dei_evidence'][0][field] = value
            self.assertFalse(reviewed_avgo_annual_identity(bad))
        bad = copy.deepcopy(row); bad['annual_dei_evidence'].append(bad['annual_dei_evidence'][0])
        self.assertFalse(reviewed_avgo_annual_identity(bad))
