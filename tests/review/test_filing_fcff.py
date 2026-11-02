"""Verifiable source operands, explicit tax convention and actual disclosure gaps."""
from copy import deepcopy
from decimal import Decimal, Inexact, ROUND_DOWN, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from valuation_platform.review.filing_fcff import calculate
from valuation_platform.valuation.consumer import ANCHORS

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import calculate_historical_fcff_from_filings as review


class FilingFCFFArithmeticTests(unittest.TestCase):
    def test_independent_simple_loss_and_reported_tax_credit_arithmetic(self):
        self.assertEqual(calculate("100", "20", "10", "25", "100")["amount_usd"], "87.5")
        self.assertEqual(calculate("-100", "20", "10", "25", "100")["amount_usd"], "-112.5")
        self.assertEqual(calculate("100", "20", "10", "-25", "100")["amount_usd"], "92.5")
        # A reported zero is acceptable; an absent interest operand is not.
        self.assertEqual(calculate("100", "20", "0", "25", "100")["amount_usd"], "80")
        with self.assertRaisesRegex(ValueError, "missing"):
            calculate("100", "20", None, "25", "100")

    def test_invalid_financial_operands_never_coerced_or_clipped(self):
        cases = [(100, "20", "10", "25", "100"), ("NaN", "20", "10", "25", "100"),
                 ("100", "-20", "10", "25", "100"), ("100", "20", "-10", "25", "100"),
                 ("100", "20", "10", "25", "0")]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                calculate(*args)

    def test_fraction_is_exact_despite_nonterminating_etr_or_hostile_context(self):
        expected = Fraction(100) + Fraction(10) * (1 - Fraction(1, 3)) - Fraction(20)
        before = calculate("100", "20", "10", "1", "3")
        ratio = before["exact_fraction_usd"]
        self.assertEqual(Fraction(int(ratio["numerator"]), int(ratio["denominator"])), expected)
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.rounding = ROUND_DOWN
            ctx.traps[Inexact] = True
            flags = ctx.flags.copy()
            self.assertEqual(calculate("100", "20", "10", "1", "3"), before)
            self.assertEqual(ctx.flags, flags)


class FilingFCFFEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = review.build()

    def test_independent_filing_operand_values_and_thirteen_calculations(self):
        interest = {"GOOGL": [346, 357, 308, 268, 736],
                    "AAPL": [2645, 2931, 3933, None, None],
                    "META": [23, 185, 446, 715, 1165]}
        display = {"GOOGL": ["67.30", "60.31", "69.76", "72.99", "73.88"],
                   "AAPL": ["95.25", "113.90", "102.94", None, None],
                   "META": ["39.14", "19.19", "44.21", "54.70", "46.93"]}
        self.assertEqual((self.data["calculated_periods"], self.data["missing_periods"]), (13, 2))
        self.assertFalse(self.data["input_estimates_permitted"])
        for company in self.data["companies"]:
            for i, period in enumerate(company["periods"]):
                inputs, result = period["inputs"], period["fcff"]
                target = interest[company["ticker"]][i]
                if target is None:
                    self.assertIsNone(result)
                    continue
                self.assertEqual(Decimal(inputs["interest_expense"]["value"]), target * 1000000)
                self.assertEqual(result["display_billions"], display[company["ticker"]][i])
                cfo, capex, intr, tax, pretax = (Fraction(inputs[k]["value"]) for k in (
                    "cfo", "cash_ppe", "interest_expense", "tax_provision", "pretax_income"))
                expected = cfo + intr * (1 - tax / pretax) - capex
                exact = result["exact_fraction_usd"]
                self.assertEqual(Fraction(int(exact["numerator"]), int(exact["denominator"])), expected)
                self.assertIn("allocation convention", result["tax_notice"])

    def test_later_meta_total_interest_distinct_from_lease_or_notes_only(self):
        meta = self.data["companies"][2]
        for p in meta["periods"][:2]:
            interest = p["inputs"]["interest_expense"]
            self.assertEqual(interest["source_identity"]["accession"], "0001326801-24-000012")
            self.assertNotEqual(interest["source_identity"]["accession"], p["identity"]["accession"])
            self.assertEqual(interest["occurrences"][0]["start"], p["identity"]["annual_start"])
        self.assertEqual(meta["periods"][0]["inputs"]["cash_ppe"]["value"], "18567000000")

    def test_apple_recent_missing_interest_is_proven_gap_not_zero_or_other_income(self):
        for p in self.data["companies"][1]["periods"][3:]:
            self.assertEqual(p["status"], "MISSING_REQUIRED_INTEREST_DISCLOSURE")
            self.assertIsNone(p["inputs"]["interest_expense"])
            self.assertIsNone(p["fcff"])
            self.assertEqual(p["interest_search"]["current_filing_annual_monetary_facts"], [])
            self.assertEqual(p["interest_search"]["primary_inline_interest_cost_fact_count"], 0)
            self.assertFalse(p["interest_search"]["primary_cash_interest_caption_present"])
            self.assertFalse(p["interest_search"]["missing_is_zero"])
        self.assertEqual([p["cash_fcf_usd"] for p in self.data["companies"][1]["periods"][3:]],
                         ["108807000000", "98767000000"])

    def test_every_used_amount_has_exact_primary_inline_and_instance_proof(self):
        for company in self.data["companies"]:
            for p in company["periods"]:
                for point in p["inputs"].values():
                    if point is None: continue
                    self.assertEqual(point["evidence_depth"], "exact_primary_inline_and_instance_verified")
                    for o in point["occurrences"]:
                        self.assertEqual(o["start"], p["identity"]["annual_start"])
                        self.assertEqual(o["end"], p["identity"]["annual_end"])
                        self.assertEqual(o["dimensions"], [])
                        self.assertTrue(o["primary_locator"])
                        self.assertEqual(Fraction(o["raw_value"]), Fraction(point["value"]))
                    self.assertEqual(len(point["sources"]), 2)
                    for source in point["sources"]:
                        self.assertEqual(len(source["sha256"]), 64)
                        self.assertEqual(source["http_status"], 200)
                        self.assertTrue(source["url"].startswith("https://www.sec.gov/Archives/edgar/data/"))

    def test_source_receipt_tampering_rejected_before_a_fact_can_be_selected(self):
        package = json.loads((ROOT / ANCHORS["aapl-fy2025"]["package"]).read_text())
        row = package["aapl_history_review"]["periods"][4]
        manifests = {s["path"]: json.loads((ROOT / s["path"]).read_text()) for s in row["sources"]}
        source = row["sources"][0]
        index = int(source["pointer"].rsplit("/", 1)[-1])
        for field, value in (("sha256", "0" * 64), ("byte_length", 0), ("source_url", "https://example.com/changed.htm")):
            bad = deepcopy(manifests)
            bad[source["path"]]["artifacts"][index][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                review.RetainedFiling(ROOT, row, bad)

    def test_output_replay_estimate_isolation_and_original_packages_unchanged(self):
        before = {kind: (ROOT / ANCHORS[kind]["package"]).read_bytes() for kind in review.KINDS}
        with patch("valuation_platform.review.historical_fcff._estimates", side_effect=AssertionError("Estimate path forbidden")):
            self.assertEqual(review.build(), self.data)
        for company, kind in zip(self.data["companies"], review.KINDS, strict=True):
            payload = (ROOT / ANCHORS[kind]["package"]).read_bytes()
            self.assertEqual(payload, before[kind])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), company["package_sha256"])
        self.assertEqual(json.loads((ROOT / review.JSON_PATH).read_text()), self.data)
        self.assertEqual((ROOT / review.CSV_PATH).read_bytes(), review.csv_output(self.data).encode())
        self.assertEqual((ROOT / review.REPORT_PATH).read_text(), review.render(self.data))


if __name__ == "__main__":
    unittest.main()
