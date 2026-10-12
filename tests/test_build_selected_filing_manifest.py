import copy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_selected_filing_manifest as manifest


class SelectedFilingManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = manifest.build(ROOT)
        cls.claim = manifest.candidate('retained.json', 'rows/0', 123,
                                       '0000000123-25-000001', '10-K',
                                       '2024-01-01', '2024-12-31', True)

    def classify(self, claims):
        return manifest.classify(123, '2024-12-31', claims)

    def test_unique_mapping_history_and_reproducibility(self):
        self.assertEqual(self.result, manifest.build(ROOT))
        rows = self.result['rows']
        self.assertEqual(len(rows), 189)
        self.assertEqual(len({(r['cik'], r['selected_annual_end']) for r in rows}), 189)
        self.assertEqual(self.result['issuer_count'], 40)
        self.assertEqual(len(self.result['history_exceptions']), 11)
        self.assertEqual(self.result['status_counts'], {'VERIFIED_RETAINED_IDENTITY': 163,
                                                      'MISSING_BINDING': 26})

    def test_history_deficits_do_not_invent_periods(self):
        exceptions = self.result['history_exceptions']
        self.assertEqual([sum(x['ticker'] == t for x in exceptions) for t in ('XOM', 'GEV', 'SNDK')], [5, 3, 3])
        for x in exceptions:
            self.assertIsNone(x['accession']); self.assertIsNone(x['annual_start']); self.assertIsNone(x['annual_end'])

    def test_missing_and_incomplete_stay_unbound(self):
        self.assertEqual(self.classify([])['status'], 'MISSING_BINDING')
        c = copy.deepcopy(self.claim); c['form'] = None
        r = self.classify([c]); self.assertEqual(r['status'], 'INCOMPLETE_BINDING')
        self.assertIsNone(r['identity'])

    def test_differing_accessions_or_dates_conflict(self):
        for field, value in [('accession', '0000000123-25-000002'), ('annual_start', '2024-01-02')]:
            c = copy.deepcopy(self.claim); c[field] = value
            r = self.classify([self.claim, c]); self.assertEqual(r['status'], 'CONFLICTING')
            self.assertIsNone(r['identity'])

    def test_equivalent_confirmation_keeps_all_sources(self):
        c = copy.deepcopy(self.claim); c['source'] = 'other.json'
        r = self.classify([self.claim, c]); self.assertEqual(r['status'], 'VERIFIED_RETAINED_IDENTITY')
        self.assertEqual(len(r['candidates']), 2)
        self.assertEqual(r['measure_fact_provenance'], 'NOT_ESTABLISHED')

    def test_malformed_entity_form_date_and_accession_cannot_verify(self):
        for field, value in [('cik', 456), ('form', '10-K/A'), ('accession', 'invalid'),
                             ('annual_start', None), ('annual_start', '2024-12-31'),
                             ('annual_end', '2025-12-31'), ('identity_evidence_sufficient', False)]:
            c = copy.deepcopy(self.claim); c[field] = value
            self.assertEqual(self.classify([c])['status'], 'INCOMPLETE_BINDING')

    def test_original_instance_metadata_gap_is_not_recovered(self):
        r = next(x for x in self.result['rows'] if x['ticker'] == 'GOOGL' and x['selected_annual_end'] == '2024-12-31')
        old = [a for c in r['candidates'] for a in c['artifacts']
               if a.get('manifest') and a['url'].endswith('_htm.xml')]
        self.assertTrue(old)
        self.assertIsNone(old[0]['retrieved_at_utc']); self.assertIsNone(old[0]['http_status'])
        self.assertEqual(r['measure_fact_provenance'], 'NOT_ESTABLISHED')

    def test_reviewed_dei_identity_does_not_change_production_resolver(self):
        r = next(x for x in self.result['rows'] if x['ticker'] == 'AVGO' and x['selected_annual_end'] == '2021-10-31')
        self.assertEqual(r['status'], 'VERIFIED_RETAINED_IDENTITY')
        import json
        row = json.loads((ROOT / 'docs/depreciation-amortization-inventory.json').read_bytes())['rows'][5]
        self.assertEqual(row['annual_resolver_status'], 'annual_period_not_found')
        self.assertTrue(manifest.reviewed_avgo_annual_identity(row))
        for field, value in [('filing', {**row['filing'], 'form': '10-K/A'}),
                             ('annual_dei_evidence', row['annual_dei_evidence'][:-1]),
                             ('annual_context_ids', ['missing'])]:
            bad = copy.deepcopy(row); bad[field] = value
            self.assertFalse(manifest.reviewed_avgo_annual_identity(bad))
        bad = copy.deepcopy(row)
        bad['contexts'][row['annual_context_ids'][0]]['dimensions'] = ['segment']
        self.assertFalse(manifest.reviewed_avgo_annual_identity(bad))

    def test_no_financial_sufficiency_or_policy_changes(self):
        self.assertEqual(self.result['financial_input_sufficiency'], 'NOT_ASSESSED')
        self.assertTrue(all(r['measure_fact_provenance'] == 'NOT_ESTABLISHED' for r in self.result['rows']))
