"""Operating-method arithmetic, actual source bindings and feasibility boundaries."""
from copy import deepcopy
from decimal import Inexact, ROUND_DOWN, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from valuation_platform.review.operating_fcff import calculate, amount
from valuation_platform.valuation.consumer import ANCHORS

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import test_operating_fcff_from_filings as review


def fraction(record):
    value = record["exact_fraction_usd"]
    return Fraction(int(value["numerator"]), int(value["denominator"]))


class OperatingArithmeticTests(unittest.TestCase):
    def test_cash_contribution_sign_and_nopat_not_cfo(self):
        result = calculate("100", "25", "100", ["10"], "20", ["-5", "2"])
        self.assertEqual(fraction(result["result"]), 62)
        self.assertEqual(fraction(result["working_capital_cash_use"]), 3)
        self.assertEqual(fraction(result["nopat"]), 75)
        self.assertFalse(result["sbc_addback"])
        self.assertFalse(result["interest_addback"])
        self.assertEqual(calculate("-100", "25", "100", ["10"], "20", ["0"])["result"]["amount_usd"], "-85")
        self.assertEqual(calculate("100", "-25", "100", ["0"], "0", ["0"])["result"]["amount_usd"], "125")
        self.assertEqual(calculate("100", "125", "100", ["0"], "0", ["0"])["result"]["amount_usd"], "-25")

    def test_missing_zero_and_invalid_operands_are_distinct(self):
        self.assertEqual(calculate("0", "0", "1", ["0"], "0", ["0"])["result"]["amount_usd"], "0")
        for args in [(None, "1", "2", ["0"], "0", ["0"]),
                     ("1", "1", "0", ["0"], "0", ["0"]),
                     ("1", "1", "2", ["0"], "-1", ["0"]),
                     ("1", "1", "2", [], "0", ["0"]),
                     ("1", "1", "2", ["0"], "0", []),
                     ("1", "1", "2", [None], "0", ["0"]),
                     ("NaN", "1", "2", ["0"], "0", ["0"])]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                calculate(*args)

    def test_exact_result_despite_hostile_decimal_context(self):
        expected = calculate("100", "1", "3", ["10"], "20", ["-5"])
        self.assertEqual(fraction(expected["result"]), Fraction(100)*Fraction(2,3)-15)
        with localcontext() as context:
            context.prec = 3; context.rounding = ROUND_DOWN; context.traps[Inexact] = True
            self.assertEqual(calculate("100", "1", "3", ["10"], "20", ["-5"]), expected)


class OperatingSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = review.build()

    def test_fifteen_results_and_no_false_fcff_certification(self):
        expected = {"GOOGL": ["52.86", "44.55", "47.90", "50.70", "40.92"],
                    "AAPL": ["89.74", "101.68", "91.46", "99.18", "86.26"],
                    "META": ["29.03", "9.80", "28.50", "40.90", "6.63"]}
        self.assertEqual(self.data["calculated_test_periods"], 15)
        self.assertEqual(self.data["certified_operating_fcff_periods"], 0)
        self.assertFalse(self.data["input_estimates_permitted"])
        for c in self.data["companies"]:
            self.assertEqual([p["operating_method_test"]["result"]["display_billions"] for p in c["periods"]], expected[c["ticker"]])
            for p in c["periods"]:
                self.assertIsNone(p["verified_operating_fcff"])
                self.assertFalse(p["operating_method_test"]["publishable"])
                self.assertFalse(p["operating_method_test"]["forecast_calibration_approved"])

    def test_independent_arithmetic_fifteen_full_cfo_checks_and_thirteen_prior_comparisons(self):
        comparisons = 0
        for c in self.data["companies"]:
            for p in c["periods"]:
                inputs, terms = p["inputs"], p["statement_terms"]
                self.assertEqual(sum((amount(t["cash_contribution_usd"]) for t in terms), Fraction()), amount(inputs["cfo_control"]["value"]))
                cash_fcf = amount(inputs["cfo_control"]["value"])-amount(inputs["cash_ppe"]["value"])
                ebit, tax, pretax = (amount(inputs[k]["value"]) for k in ("ebit", "tax_provision", "pretax_income"))
                noncash = sum((amount(t["cash_contribution_usd"]) for t in terms if t["role_in_test"] in ("reported_da_or_combined_impairment", "separate_operating_noncash_charge")),Fraction())
                movements = sum((amount(t["cash_contribution_usd"]) for t in terms if t["role_in_test"] in ("named_trade_movement", "mixed_asset_liability_movement")),Fraction())
                value = ebit*(1-tax/pretax)+noncash-amount(inputs["cash_ppe"]["value"])+movements
                self.assertEqual(fraction(p["operating_method_test"]["result"]), value)
                bridge = p["cash_fcf_bridge"]
                self.assertEqual(value+fraction(bridge["net_nonoperating_after_reported_etr"])+fraction(bridge["excluded_statement_adjustments_and_explicit_tax_movements"]), cash_fcf)
                self.assertFalse(bridge["residual_used"])
                comp = p["prior_method_comparison"]
                if comp:
                    comparisons += 1
                    old_value = cash_fcf+amount(comp["interest_source"]["value"])*(1-tax/pretax)
                    self.assertEqual(fraction(comp["prior_cfo_method"]), old_value)
                    self.assertEqual(fraction(comp["operating_test_minus_cfo_method"]), value-old_value)
        self.assertEqual(comparisons, 13)
        self.assertTrue(all(p["prior_method_comparison"] is None for p in self.data["companies"][1]["periods"][3:]))

    def test_tax_sbc_noncash_scope_and_reported_zero_classification(self):
        googl, apple, meta = self.data["companies"]
        for p in googl["periods"]:
            tax_rows = [t for t in p["statement_terms"] if t["role_in_test"] == "separate_income_tax_movement"]
            self.assertEqual(len(tax_rows), 1)
        self.assertEqual([p["operating_method_test"]["noncash_costs"]["amount_usd"] for p in googl["periods"][:2]], ["12441000000", "15928000000"])
        self.assertEqual(meta["periods"][1]["operating_method_test"]["noncash_costs"]["amount_usd"], "12245000000")
        for c in self.data["companies"]:
            for p in c["periods"]:
                sbc = [t for t in p["statement_terms"] if t["source"]["concept"] == "ShareBasedCompensation"]
                self.assertEqual(len(sbc), 1)
                self.assertEqual(sbc[0]["role_in_test"], "other_reconciliation_adjustment_not_in_test")
        zero = [t for t in meta["periods"][3]["statement_terms"] if "abandonment" in t["caption"].lower()][0]
        self.assertEqual(amount(zero["source"]["value"]), 0)
        self.assertTrue(zero["source"]["occurrences"])
        self.assertEqual(apple["periods"][4]["mixed_movement_exposure"]["amount_usd"], "-20273000000")

    def test_every_operand_primary_instance_identity_and_original_meta_precision(self):
        for c in self.data["companies"]:
            for p in c["periods"]:
                points = list(p["inputs"].values())+[t["source"] for t in p["statement_terms"]]
                for point in points:
                    self.assertEqual(point["evidence_depth"], "exact_primary_inline_and_instance_verified")
                    self.assertEqual(len(point["sources"]), 2)
                    for o in point["occurrences"]:
                        self.assertEqual(o["start"], p["identity"]["annual_start"])
                        self.assertEqual(o["end"], p["identity"]["annual_end"])
                        self.assertEqual(amount(o["raw_value"]), amount(point["value"]))
                        self.assertTrue(o["primary_locator"])
        charges = self.data["companies"][2]["periods"][1]["statement_terms"][4:6]
        self.assertEqual([t["source"]["value"] for t in charges], ["2218000000", "1341000000"])
        self.assertEqual([t["source"]["precision"] for t in charges], ["-6", "-6"])
        self.assertTrue(all(t["source"]["occurrences"][0]["dimensions"] for t in charges))

    def test_primary_selection_and_statement_sign_tampering_rejected(self):
        package = json.loads((ROOT/ANCHORS["meta-fy2025"]["package"]).read_text())
        row = package["periods"][1]
        filing = review.RetainedFiling(ROOT, row, {})
        point = row["independent_display_check"]["rows"][4]["fact"]
        bad = deepcopy(point); bad["value"] = "2220000000"
        with self.assertRaises(ValueError): review.point_from(filing, row["identity"], bad)
        bad = deepcopy(point); bad["primary_table"]["row"] += 1
        with self.assertRaises(ValueError): review.point_from(filing, row["identity"], bad)
        package = json.loads((ROOT/ANCHORS["aapl-fy2025"]["package"]).read_text())
        row = deepcopy(package["aapl_history_review"]["periods"][0])
        filing = review.RetainedFiling(ROOT, row, {})
        row["cfo_reconciliation"]["terms"][0]["multiplier"] = -1
        with self.assertRaises(ValueError): review.statement_terms(row, filing)

    def test_estimate_isolation_source_package_preservation_and_replay(self):
        paths = [ROOT/ANCHORS[k]["package"] for k in review.KINDS]
        paths += [ROOT/review.PRIOR_PATH, ROOT/"src/valuation_platform/review/history.py"]
        before = {p: p.read_bytes() for p in paths}
        with patch("valuation_platform.review.historical_fcff._estimates", side_effect=AssertionError("Estimate path forbidden")):
            self.assertEqual(review.build(), self.data)
        for p in paths: self.assertEqual(p.read_bytes(), before[p])
        for c, kind in zip(self.data["companies"], review.KINDS, strict=True):
            self.assertEqual(c["package_sha256"], hashlib.sha256((ROOT/ANCHORS[kind]["package"]).read_bytes()).hexdigest())
        self.assertEqual(json.loads((ROOT/review.JSON_PATH).read_text()), self.data)
        self.assertEqual((ROOT/review.CSV_PATH).read_bytes(), review.csv_output(self.data).encode())
        self.assertEqual((ROOT/review.REPORT_PATH).read_text(), review.render(self.data))


if __name__ == "__main__": unittest.main()
