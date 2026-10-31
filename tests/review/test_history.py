from copy import deepcopy
from decimal import localcontext, Inexact, ROUND_DOWN
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from valuation_platform.review.history import historical_references, historical_window
from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor
from valuation_platform.api.catalog import CATALOG_MAX_BYTES, build_catalog

ROOT = Path(__file__).resolve().parents[2]


class HistoricalReferenceTests(unittest.TestCase):
    def test_retained_annual_ratios_match_independent_fractions_with_sources_and_periods(self):
        for kind in ANCHORS:
            load_revenue_anchor(kind, ROOT)  # Existing approval/source checks remain authoritative.
            refs = historical_references(ROOT, kind)
            for ref in refs:
                a, b = ref['operands']
                expected = Fraction(a['amount']) / Fraction(b['amount'])
                if ref['metric'] == 'revenue_growth': expected -= 1
                self.assertLess(abs(Fraction(ref['value']) - expected), Fraction('1e-48'))
                self.assertEqual(ref['classification'], 'DERIVED_HISTORICAL_REFERENCE')
                self.assertEqual(a['period_end'][:4], '2025')
                for operand in (a, b):
                    self.assertEqual(operand['unit'], 'USD'); self.assertEqual(operand['precision'], '-6')
                    self.assertTrue(operand['sources']); self.assertTrue(operand['accession'])
            if kind == 'aapl-fy2025': self.assertEqual(refs[1]['operands'][0]['period_end'], '2025-09-27')
            before = refs
            with localcontext() as ctx:
                ctx.prec = 3; ctx.rounding = ROUND_DOWN; ctx.traps[Inexact] = True
                saved = ctx.copy(); self.assertEqual(historical_references(ROOT, kind), before)
                self.assertEqual(ctx.flags, saved.flags)

    def test_missing_mismatched_adjusted_or_incompatible_populations_never_substitute(self):
        kind = 'meta-fy2025'; name = ANCHORS[kind]['package']
        original = json.loads((ROOT / name).read_text())
        edits = [lambda d: d['current_history']['periods'][3]['inputs']['revenue'].update(origin='manual_input'),
                 lambda d: d['periods'][3]['facts']['revenue'].update(unit='shares'),
                 lambda d: d['periods'][3]['facts']['revenue'].update(value='1'),
                 lambda d: d['periods'][3]['facts']['revenue'].update(occurrences=[])]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / name; path.parent.mkdir(parents=True)
            for edit in edits:
                d = deepcopy(original); edit(d); path.write_text(json.dumps(d))
                refs = historical_references(root, kind)
                self.assertIsNone(refs[0]['value']); self.assertTrue(refs[1]['value'])
        raw = build_catalog(ROOT); self.assertLess(len(raw), CATALOG_MAX_BYTES)
        for entry in json.loads(raw)['entries']:
            self.assertEqual(entry['historical_references'][0]['operands'][0]['amount'], entry['revenue'])
            self.assertIsNone(entry['template']['wacc'])


class HistoricalWindowTests(unittest.TestCase):
    def test_five_source_bound_periods_end_at_selected_anchor_without_fcff_invention(self):
        for kind in ANCHORS:
            window = historical_window(ROOT, kind)
            self.assertEqual([h['fiscal_year_label'] for h in window], ['FY2021', 'FY2022', 'FY2023', 'FY2024', 'FY2025'])
            self.assertEqual(window[-1]['revenue']['period_end'], ANCHORS[kind]['identity']['annual_end'])
            for h in window:
                self.assertIsNone(h['fcff'])
                self.assertEqual(h['revenue']['unit'], 'USD')
                self.assertEqual(h['revenue']['precision'], '-6')
                self.assertTrue(h['revenue']['concept'])
                self.assertIn(h['revenue']['accession'].replace('-', ''), h['revenue']['sources'][0])
        self.assertEqual([h['revenue']['amount'] for h in historical_window(ROOT, 'googl-fy2025')],
                         ['257637000000', '282836000000', '307394000000', '350018000000', '402836000000'])
        # Selection follows eligible period identities, not a globally fixed year list.
        with patch.dict(ANCHORS['googl-fy2025']['identity'], annual_end='2024-12-31'):
            self.assertEqual([h['fiscal_year_label'] for h in historical_window(ROOT, 'googl-fy2025')],
                             ['FY2021', 'FY2022', 'FY2023', 'FY2024'])

    def test_incompatible_or_missing_prior_year_stops_window_without_substitution(self):
        name = ANCHORS['googl-fy2025']['package']
        d = json.loads((ROOT / name).read_text())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / name; path.parent.mkdir(parents=True)
            d['googl_current_history']['periods'][3]['inputs']['revenue']['origin'] = 'manual_input'
            path.write_text(json.dumps(d))
            self.assertEqual([h['fiscal_year_label'] for h in historical_window(root, 'googl-fy2025')], ['FY2025'])
            d['googl_current_history']['periods'][4]['inputs']['revenue']['unit'] = 'shares'
            path.write_text(json.dumps(d))
            self.assertEqual(historical_window(root, 'googl-fy2025'), [])
