"""The adopted historical basis removes reconstruction gates, not missing facts."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from valuation_platform.api.catalog import build_catalog, CATALOG_MAX_BYTES
from valuation_platform.review.cfo_history import adopted_window, policy, LEDGER, LEDGER_SHA256
from valuation_platform.valuation.consumer import ANCHORS

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import adopt_historical_cfo_fcff as adoption


class AdoptedCFOHistoryTests(unittest.TestCase):
    def test_catalog_uses_apple_standardized_overlay_and_preserves_other_issuers(self):
        raw = build_catalog(ROOT)
        self.assertLess(len(raw), CATALOG_MAX_BYTES)
        entries = json.loads(raw)["entries"]
        expected = {"GOOGL": ["67.30", "60.31", "69.76", "72.99", "73.88"],
                    "AAPL": ["93.41", "108.44", "99.84", "115.68", "95.12"],
                    "META": ["39.14", "19.44", "44.44", "54.70", "46.93"]}
        from decimal import Decimal, Context, localcontext
        for entry in entries:
            from valuation_platform.review.resolved_history import policy as resolved_policy
            self.assertEqual(entry["historical_fcff_policy"], resolved_policy(entry["kind"]))
            for period, wanted in zip(entry["historical_window"], expected[entry["company"]], strict=True):
                if wanted is None:
                    self.assertIsNone(period["fcff"])
                    self.assertEqual(period["fcff_calculation"]["status"], "MISSING_INTEREST_DISCLOSURE")
                else:
                    with localcontext(Context(prec=60)):
                        self.assertEqual(f'{Decimal(period["fcff"])/1000000000:.2f}', wanted)
                    self.assertEqual(period["fcff_calculation"]["status"], "CALCULATED_STANDARDIZED_CONVENTION" if entry['company']=='AAPL' else "CALCULATED")
                self.assertEqual(period["fcff_basis"], "REPORTED_CFO_NET_IDENTIFIED_PPE" if entry["company"]=="META" else "STANDARDIZED_EBIT_CURRENT_NWC_CASH_PPE" if entry['company']=='AAPL' else "REPORTED_CFO_CASH_PPE")
                self.assertTrue(period["fcff_calculation"]["sources"])
        self.assertNotIn("/Users/", raw.decode())

    def test_adoption_never_mutates_forecast_templates_or_acceptance(self):
        before = {s["package"]: (ROOT/s["package"]).read_bytes() for s in ANCHORS.values()}
        for entry in json.loads(build_catalog(ROOT))["entries"]:
            original = json.loads((ROOT/f'examples/valuation/{entry["kind"]}-unset.json').read_text())
            self.assertEqual(entry["template"], original)
            self.assertFalse(entry["historical_fcff_policy"]["forecast_calibration"])
            self.assertFalse(entry["historical_fcff_policy"]["cross_basis_cagr"])
        for name, value in before.items():
            self.assertEqual((ROOT/name).read_bytes(), value)

    def test_period_dates_and_later_meta_interest_source_are_preserved(self):
        for kind in ANCHORS:
            rows = adopted_window(ROOT, kind)
            self.assertEqual([p["fiscal_year_label"] for p in rows], [f"FY{y}" for y in range(2021, 2026)])
            self.assertEqual(rows[-1]["revenue"]["period_end"], ANCHORS[kind]["identity"]["annual_end"])
        rows = adopted_window(ROOT, "meta-fy2025")
        self.assertTrue(any("000132680124000012" in u for u in rows[0]["fcff_calculation"]["sources"]))
        self.assertEqual(rows[0]["fcff_calculation"]["inputs"]["interest_expense"], "23000000")
        self.assertEqual(rows[0]["fcff_calculation"]["inputs"]["cash_ppe"], "18567000000")

    def test_corrupted_ledger_or_changed_accepted_package_is_rejected(self):
        name = ANCHORS["googl-fy2025"]["package"]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for filename in (name, LEDGER):
                path = root/filename; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT/filename).read_bytes())
            (root/LEDGER).write_bytes((root/LEDGER).read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError, "reviewed pin"):
                adopted_window(root, "googl-fy2025")
            (root/LEDGER).write_bytes((ROOT/LEDGER).read_bytes())
            (root/name).write_bytes((root/name).read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError, "package changed"):
                adopted_window(root, "googl-fy2025")

    def test_recomputed_results_reject_internal_arithmetic_or_period_mismatches(self):
        original = json.loads((ROOT/LEDGER).read_text())
        edits = [lambda p: p["fcff"].update(amount_usd="0"),
                 lambda p: p["identity"].update(cik=1),
                 lambda p: p["inputs"]["cfo"].update(target_annual_end="2025-01-01")]
        name = ANCHORS["googl-fy2025"]["package"]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/name).parent.mkdir(parents=True, exist_ok=True)
            (root/name).write_bytes((ROOT/name).read_bytes())
            for edit in edits:
                data = deepcopy(original); edit(data["companies"][0]["periods"][0])
                payload = json.dumps(data).encode(); (root/LEDGER).write_bytes(payload)
                with patch("valuation_platform.review.cfo_history.LEDGER_SHA256", hashlib.sha256(payload).hexdigest()):
                    with self.assertRaises(ValueError):
                        adopted_window(root, "googl-fy2025")

    def test_source_evidence_replay_and_no_estimate_or_detailed_reconstruction_dependency(self):
        with patch("valuation_platform.review.historical_fcff._estimates", side_effect=AssertionError("No estimates")):
            data = adoption.build(ROOT)
        self.assertEqual((data["calculated"], data["missing"]), (13, 2))
        self.assertEqual(hashlib.sha256((ROOT/LEDGER).read_bytes()).hexdigest(), LEDGER_SHA256)
        for name, text in adoption.outputs(data).items():
            self.assertEqual((ROOT/name).read_bytes(), text.encode())


if __name__ == "__main__":
    unittest.main()
