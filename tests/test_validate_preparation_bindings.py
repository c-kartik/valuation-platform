import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preparation_bindings', ROOT / 'scripts/validate_preparation_bindings.py')
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)


class PreparationBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = binding.run(ROOT, verify_pilots=False)
        d = json.loads((ROOT / 'docs/phase1-issuer-preparation-disposition.json').read_text())
        v = json.loads((ROOT / 'docs/universe/phase-1h5-issuer-validation.json').read_text())
        cls.row = d['rows'][0]
        cls.validation = next(r for r in v['rows'] if r['cik'] == cls.row['cik'])
        cls.corpus = {k: cls.validation[k] for k in ('cik', 'typed_status_counts', 'measure_status_counts')}
        cls.corpus.update(selected_annual_periods=cls.validation['selected_annual_end_dates'],
                          selected_annual_filings=cls.validation['history_period_count'])

    def evaluate(self, row=None, validation=None, corpus=None):
        return binding.bind_row(ROOT, row or self.row, validation or self.validation, corpus or self.corpus)

    def test_accounting_is_not_financial_sufficiency(self):
        self.assertEqual(self.report['counts'], {'PASS': 40})
        self.assertEqual(self.report['financial_sufficiency_counts'], {'NOT_ASSESSED': 40})
        for r in self.report['rows']:
            self.assertIsNone(r['consumer_contract'])
            self.assertEqual(r['exact_history_and_fact_binding'], 'INSUFFICIENT_FOR_WHOLE_HISTORY')
            self.assertEqual(r['independently_reviewed_packages'], [])

    def test_history_exceptions_and_counts_remain_explicit(self):
        self.assertEqual(self.report['selected_periods'], 189)
        histories = {r['ticker']: r['selected_periods'] for r in self.report['rows']}
        self.assertEqual((histories['XOM'], histories['GEV'], histories['SNDK']), (0, 2, 2))
        self.assertTrue(all(r['history_target'] == 5 for r in self.report['rows']))

    def test_mismatched_issuer_is_failure_not_new_provenance(self):
        row = copy.deepcopy(self.row); row['cik'] += 1
        r = self.evaluate(row=row)
        self.assertEqual(r['evidence_accounted'], 'FAIL')
        self.assertIn('validation_mismatch:cik', r['errors'])
        self.assertEqual(r['financial_input_sufficiency'], 'NOT_ASSESSED')

    def test_changed_history_or_measure_state_fails(self):
        for field, value in [('annual_ends', []), ('selected_periods', 4), ('states', {})]:
            row = copy.deepcopy(self.row); row[field] = value
            self.assertEqual(self.evaluate(row=row)['evidence_accounted'], 'FAIL')

    def test_changed_classification_fails(self):
        row = copy.deepcopy(self.row); row['classification'] = 'SUPPORTED'
        self.assertIn('classification_mismatch', self.evaluate(row=row)['errors'])

    def test_missing_record_or_reference_fails(self):
        row = copy.deepcopy(self.row); row['record'] = 'company-data-preparation/NOT_PRESENT.md'
        self.assertIn('missing_record', self.evaluate(row=row)['errors'])
        row = copy.deepcopy(self.row); row['references'].append('does-not-exist.json')
        self.assertTrue(any(x.startswith('missing_evidence_reference:') for x in self.evaluate(row=row)['errors']))

    def test_corpus_disagreement_cannot_pass(self):
        corpus = copy.deepcopy(self.corpus); corpus['typed_status_counts']['resolved'] += 1
        self.assertIn('corpus_mismatch:typed_status_counts', self.evaluate(corpus=corpus)['errors'])

    def test_evidence_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            binding.local(ROOT, '../outside.json')

    def test_sparse_zero_buckets_are_counts_not_financial_zeros(self):
        corpus = copy.deepcopy(self.corpus)
        corpus['typed_status_counts'] = {k: v for k, v in corpus['typed_status_counts'].items() if v}
        self.assertEqual(self.evaluate(corpus=corpus)['evidence_accounted'], 'PASS')

    def test_wrong_corpus_annual_history_fails(self):
        corpus = copy.deepcopy(self.corpus); corpus['selected_annual_periods'] = []
        self.assertIn('corpus_history_mismatch', self.evaluate(corpus=corpus)['errors'])

    def test_conflicts_are_not_cleared(self):
        results = {r['ticker']: r for r in self.report['rows']}
        self.assertEqual([results[t]['states']['ambiguous'] for t in ('WMT', 'MA', 'CVX')], [5, 1, 5])
        self.assertTrue(all(r['support_classification_unchanged'] == 'GENERALIZATION_REQUIRED' for r in results.values()))
