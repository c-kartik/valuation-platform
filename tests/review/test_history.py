from copy import deepcopy
from decimal import localcontext, Inexact, ROUND_DOWN
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
from valuation_platform.review.history import historical_references
from valuation_platform.valuation.consumer import ANCHORS, load_revenue_anchor
from valuation_platform.api.catalog import build_catalog

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
        raw = build_catalog(ROOT); self.assertLess(len(raw), 64 * 1024)
        for entry in json.loads(raw)['entries']:
            self.assertEqual(entry['historical_references'][0]['operands'][0]['amount'], entry['revenue'])
            self.assertIsNone(entry['template']['wacc'])
