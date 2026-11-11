"""Financial safety cases for the isolated peer-preparation consumer."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('peer_prepare', Path(__file__).resolve().parents[2] / 'scripts/comparables/prepare.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PeerPreparationTests(unittest.TestCase):
    def payload(self, rows):
        return {'cik': 123, 'facts': {'us-gaap': {'OperatingIncomeLoss': {'units': {'USD': rows}}}}}

    def fact(self, value, filed='2026-10-30', accession='0000000123-26-000001'):
        return {'val': value, 'start': '2026-01-01', 'end': '2026-09-30',
                'filed': filed, 'accn': accession, 'form': '10-Q'}

    def pick(self, rows, **kwargs):
        return module.pick(self.payload(rows), ['OperatingIncomeLoss'], '2026-11-11', '2026-01-01', '2026-09-30', **kwargs)

    def test_cutoff_excludes_later_revision(self):
        result = self.pick([self.fact(100), self.fact(150, filed='2026-12-01')])
        self.assertEqual(result['value'], 100)

    def test_same_priority_conflict_is_not_arbitrarily_selected(self):
        self.assertEqual(self.pick([self.fact(100), self.fact(150)])['status'], 'CONFLICT')

    def test_missing_is_not_zero(self):
        self.assertIsNone(self.pick([])['value'])

    def test_required_accession_never_falls_back(self):
        self.assertIsNone(self.pick([self.fact(100)], accession='different')['value'])

    def test_negative_earnings_preserved(self):
        self.assertEqual(self.pick([self.fact(-100)])['value'], -100)

    def test_ttm_requires_all_operands(self):
        result = module.derive([{'value': 100}, {'value': 40}, {'value': None}], [1, 1, -1], 'TTM')
        self.assertIsNone(result['value'])

    def test_ttm_uses_annual_plus_ytd_less_prior_ytd(self):
        result = module.derive([{'value': 100}, {'value': 50}, {'value': 30}], [1, 1, -1], 'TTM')
        self.assertEqual(result['value'], 120)

    def test_zero_revenue_does_not_create_infinite_margin(self):
        self.assertIsNone(module.ratio(10, 0))

    def test_fcf_preserves_negative_result(self):
        self.assertEqual(module.derive([{'value': 20}, {'value': 30}], [1, -1], 'FCF')['value'], -10)

    def test_no_dcf_paths_written_by_consumer(self):
        self.assertEqual(module.BASE, module.ROOT / 'data/trading-comparables')

    def test_rounded_note_duplicate_requires_declared_precision(self):
        from types import SimpleNamespace
        from decimal import Decimal
        facts = [SimpleNamespace(numeric_value=Decimal('41860000000'), decimals='-6'),
                 SimpleNamespace(numeric_value=Decimal('41900000000'), decimals='-8')]
        self.assertTrue(module.filing_values_agree(facts, 41860000000))
        facts[1].decimals = '-6'
        self.assertFalse(module.filing_values_agree(facts, 41860000000))

    def test_rounded_only_evidence_is_not_an_exact_match(self):
        from types import SimpleNamespace
        from decimal import Decimal
        self.assertFalse(module.filing_values_agree([SimpleNamespace(numeric_value=Decimal('41900000000'), decimals='-8')], 41860000000))

class FrozenPreparationTests(unittest.TestCase):
    def test_source_hashes_and_financial_reconciliations(self):
        import hashlib
        import json
        for ticker in module.ISSUERS:
            with self.subTest(ticker=ticker):
                d = json.loads((module.BASE / 'prepared' / f'{ticker}.json').read_text())
                self.assertFalse(d['validation']['errors'])
                self.assertGreater(d['validation']['matches'], 0)
                self.assertEqual(d['validation']['mismatches'], 0)
                for relative, expected in d['source_hashes'].items():
                    self.assertEqual(hashlib.sha256((module.ROOT / relative).read_bytes()).hexdigest(), expected)
                for check in d['validation']['annual_quarter_checks']:
                    self.assertNotEqual(check['status'], 'MISMATCH')
                for metric in d['ttm'].values():
                    if metric['value'] is not None:
                        self.assertEqual(metric['value'], sum(o['value'] * c for o, c in zip(metric['operands'], metric['coefficients'])))
                business = json.loads((module.BASE / 'business-review' / f'{ticker}.json').read_text())
                self.assertEqual(business['mismatches'], 0)

    def test_convertible_debt_is_not_assumed_absent(self):
        import json
        d = json.loads((module.BASE / 'prepared/PINS.json').read_text())
        self.assertGreater(d['balance_sheet_candidates']['convertible_debt_noncurrent']['value'], 0)

    def test_missing_total_da_does_not_publish_ebitda(self):
        import json
        for ticker in ['GOOGL', 'MSFT']:
            d = json.loads((module.BASE / 'prepared' / f'{ticker}.json').read_text())
            self.assertIsNone(d['ttm']['reported_da']['value'])
            self.assertNotIn('ebitda', d['derived_metrics'])

if __name__ == '__main__':
    unittest.main()
