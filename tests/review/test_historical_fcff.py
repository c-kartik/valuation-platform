"""Independent cash FCF arithmetic and fail-closed pilot reconciliation."""
from copy import deepcopy
from decimal import Inexact, ROUND_DOWN, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from valuation_platform.review.historical_fcff import KINDS, REQUIREMENTS, _alphabet_comparatives, _proof, build_review, prepare_company
from valuation_platform.valuation.consumer import ANCHORS

ROOT = Path(__file__).resolve().parents[2]
MILLION = 1000000


class HistoricalFCFFReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = build_review(ROOT)

    def test_fifteen_period_cash_fcf_matches_independent_filing_totals(self):
        # Retained original-as-selected filings, not later restated comparatives.
        expected = {
            "GOOGL": [67012, 60010, 69495, 72764, 73266],
            "AAPL": [92953, 111443, 99584, 108807, 98767],
            "META": [39116, 19044, 43847, 54072, 46109],
        }
        for company in self.review["companies"]:
            self.assertEqual([p["fiscal_year_label"] for p in company["periods"]],
                             ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025"])
            for period, amount in zip(company["periods"], expected[company["ticker"]], strict=True):
                inputs = period["inputs"]
                calculated = (Fraction(inputs["reported_cfo"]["raw_value"])
                              - Fraction(inputs["signed_cash_ppe"]["raw_value"]))
                self.assertEqual(calculated, amount * MILLION)
                self.assertEqual(Fraction(period["cash_fcf"]["amount_usd"]), calculated)
                self.assertEqual(period["cash_fcf"]["precision"], "-6")
                self.assertFalse(period["cash_fcf"]["valuation_input"])
                self.assertIn("NOT_FCFF", period["cash_fcf"]["classification"])
                proof = period["cfo_check"]
                self.assertEqual(proof["row_sum_usd"], inputs["reported_cfo"]["amount_usd"])
                self.assertEqual(proof["difference_usd"], "0")
                self.assertFalse(proof["additional_working_capital_deduction"])

    def test_no_adjustment_activated_and_no_intermediate_published_as_fcff(self):
        self.assertFalse(self.review["chart_publication_enabled"])
        self.assertEqual(self.review["methodology_status"], "PROPOSED_NOT_ACTIVATED")
        for company in self.review["companies"]:
            for period in company["periods"]:
                self.assertIsNone(period["fcff"])
                self.assertEqual({x["id"] for x in period["adjustments"]}, set(REQUIREMENTS))
                self.assertTrue(all(x["amount_usd"] is None and x["status"] == "UNRESOLVED"
                                    for x in period["adjustments"]))

    def test_source_identities_pointers_and_occurrence_precision_are_retained(self):
        for company in self.review["companies"]:
            payload = (ROOT / company["package"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), company["package_sha256"])
            package = json.loads(payload)
            for period in company["periods"]:
                inputs = period["inputs"]
                points = [inputs[k] for k in ("reported_cfo", "signed_cash_ppe", "cfo_sbc_addback", "ebit")]
                points += list(inputs["reported_tax_context"].values())
                points += [p for p in period["supporting_observations"].values() if p and
                           p["classification"] != "LATER_REPORTED_COMPARATIVE_REVIEW_ONLY"]
                for point in points:
                    doc, pointer = point["source_reference"].split("#")
                    self.assertEqual(doc, company["package"])
                    fact = package
                    for key in pointer.strip("/").split("/"):
                        fact = fact[int(key)] if isinstance(fact, list) else fact[key]
                    matching = [o for o in fact["occurrences"] if o["ordinal"] == point["occurrence_ordinal"]]
                    self.assertEqual(matching[0]["precision"], point["precision"])
                    self.assertEqual(matching[0]["start"], None if point["as_of"] else period["identity"]["annual_start"])
                    self.assertEqual(matching[0]["end"], period["identity"]["annual_end"])
                    for url in point["sources"]:
                        self.assertTrue(url.startswith("https://www.sec.gov/Archives/edgar/data/"))
                        self.assertIn(period["identity"]["accession"].replace("-", ""), url)

    def test_company_specific_support_does_not_become_zero_or_a_lease_allocation(self):
        googl, aapl, meta = self.review["companies"]
        self.assertEqual([p["supporting_observations"]["finance_additions_candidate"] is not None
                          for p in googl["periods"]], [False, False, False, True, True])
        for period in aapl["periods"]:
            support = period["supporting_observations"]
            self.assertNotIn("finance_additions_candidate", support)
            self.assertEqual(support["combined_lease_additions_support"]["precision"], "-8")
        for company in (meta, aapl):
            observed = [p["supporting_observations"]["cash_interest_candidate"] is not None
                        for p in company["periods"]]
            self.assertEqual(observed, [False, False, True, True, True] if company is meta
                             else [True, True, True, False, False])
        self.assertIn("independent_display_check", meta["periods"][1]["cfo_check"]["source_reference"])
        self.assertEqual(meta["periods"][0]["inputs"]["signed_cash_ppe"]["raw_value"], "18567000000")

    def test_wrong_effective_value_unit_sign_pointer_or_origin_rejected(self):
        kind = "googl-fy2025"
        name = ANCHORS[kind]["package"]
        original = json.loads((ROOT / name).read_text())
        mutations = [dict(value="0"), dict(unit="shares"), dict(multiplier=1),
                     dict(source_reference="/googl_history_review/periods/1/facts/PaymentsToAcquirePropertyPlantAndEquipment"),
                     dict(origin="manual_input"), dict(raw_value="NaN")]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / name
            path.parent.mkdir(parents=True)
            for mutation in mutations:
                bad = deepcopy(original)
                bad["googl_current_history"]["periods"][0]["inputs"]["cash_capex"].update(mutation)
                path.write_text(json.dumps(bad))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    prepare_company(root, kind)

    def test_stale_source_or_approval_rejected_without_reapproval(self):
        kind = "aapl-fy2025"
        name = ANCHORS[kind]["package"]
        original = json.loads((ROOT / name).read_text())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / name
            path.parent.mkdir(parents=True)
            for change in ("source", "approval"):
                bad = deepcopy(original)
                if change == "source":
                    bad["aapl_history_review"]["periods"][0]["facts"]["NetCashProvidedByUsedInOperatingActivities"]["value"] = "0"
                else:
                    bad["aapl_history_approval"]["sha256"] = "0" * 64
                path.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    prepare_company(root, kind)

    def test_independent_cfo_arithmetic_cannot_be_replaced_by_a_residual(self):
        d = json.loads((ROOT / ANCHORS["googl-fy2025"]["package"]).read_text())
        row = d["googl_history_review"]["periods"][4]
        from decimal import Decimal
        for mutation in ("residual", "duplicate", "term", "total"):
            bad = deepcopy(row)
            check = bad["cfo_reconciliation"]
            if mutation == "residual": check["residual_used"] = True
            if mutation == "duplicate": check["terms"].append(check["terms"][0])
            if mutation == "term": check["terms"][0]["contribution_usd"] = "0"
            if mutation == "total": check["value_usd"] = "0"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                _proof(bad, Decimal("164713000000"))

    def test_replay_read_only_and_independent_of_ambient_decimal_context(self):
        paths = [ROOT / ANCHORS[k]["package"] for k in KINDS]
        before = [p.read_bytes() for p in paths]
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.rounding = ROUND_DOWN
            ctx.traps[Inexact] = True
            saved = ctx.copy()
            self.assertEqual(build_review(ROOT), self.review)
            self.assertEqual(ctx.flags, saved.flags)
        self.assertEqual(before, [p.read_bytes() for p in paths])
        artifact = ROOT / "docs/company-data-preparation/historical-fcff-pilot-review.json"
        self.assertEqual(json.loads(artifact.read_text()), self.review)

    def test_other_companies_not_implicitly_enabled(self):
        with self.assertRaisesRegex(ValueError, "Three-issuer"):
            prepare_company(ROOT, "msft-fy2025")

    def test_estimate_arithmetic_independent_fraction_check_and_no_double_interest_or_sbc(self):
        for company in self.review["companies"]:
            for period in company["periods"]:
                e, inp = period["fcff_estimate_for_review"], period["inputs"]
                tax = inp["reported_tax_context"]
                rate = Fraction(tax["provision"]["amount_usd"]) / Fraction(tax["pretax"]["amount_usd"])
                net = Fraction(tax["pretax"]["amount_usd"]) - Fraction(inp["ebit"]["amount_usd"])
                corrections = sum((Fraction(x["amount_usd"]) for x in period["identified_nonoperating_cfo_contributions"]), Fraction(0))
                expected = (Fraction(period["cash_fcf"]["amount_usd"]) - Fraction(inp["cfo_sbc_addback"]["amount_usd"])
                            - (net + corrections) * (1 - rate) - Fraction(e["financed_investment_estimate_usd"]))
                self.assertLess(abs(Fraction(e["amount_usd"]) - expected), Fraction("1e-35"))
                self.assertFalse(e["chart_publication_enabled"])
                self.assertFalse(e["valuation_input"])
                self.assertEqual(e["classification"], "REVIEW_ESTIMATE_NOT_ACCEPTED_FCFF")
                self.assertGreater(len(e["assumptions"]), 4)
        # Alphabet FY2025 24,620m gains were already removed from CFO.
        e = self.review["companies"][0]["periods"][4]["fcff_estimate_for_review"]
        self.assertEqual(e["net_nonoperating_cash_proxy_usd"], "5167000000")
        # META note deferred tax18,755 is not an extra cash-flow add-back.
        e = self.review["companies"][2]["periods"][4]["fcff_estimate_for_review"]
        self.assertEqual(e["identified_nonoperating_cfo_contributions_usd"], "-1138000000")

    def test_lease_estimates_keep_later_source_identity_and_distinguish_stock_allocation(self):
        googl, aapl, meta = self.review["companies"]
        for i, expected in ((1, "577000000"), (2, "564000000")):
            p = googl["periods"][i]
            support = p["supporting_observations"]["later_finance_additions_comparative"]
            self.assertEqual(support["source_accession"], "0001652044-25-000014")
            self.assertNotEqual(support["source_accession"], p["identity"]["accession"])
            self.assertEqual(support["fact_period_end"], p["identity"]["annual_end"])
            self.assertEqual(support["amount_usd"], expected)
            self.assertEqual(p["fcff_estimate_for_review"]["financed_investment_estimate_usd"], expected)
        self.assertEqual(googl["periods"][0]["fcff_estimate_for_review"]["finance_estimate_basis"]["kind"], "ANALYST_BACKCAST_ESTIMATE")
        for p in aapl["periods"]:
            e, support = p["fcff_estimate_for_review"], p["supporting_observations"]
            expected = (Fraction(support["combined_lease_additions_support"]["amount_usd"])
                        * Fraction(support["finance_asset_stock_support"]["amount_usd"])
                        / (Fraction(support["finance_asset_stock_support"]["amount_usd"])
                           + Fraction(support["operating_asset_stock_support"]["amount_usd"])))
            self.assertLess(abs(Fraction(e["financed_investment_estimate_usd"]) - expected), Fraction("1e-35"))
            self.assertEqual(e["finance_estimate_basis"]["kind"], "ANALYST_ALLOCATION_ESTIMATE")
        self.assertTrue(all(p["fcff_estimate_for_review"]["finance_estimate_basis"]["kind"] == "REPORTED_SUPPORT" for p in meta["periods"]))

    def test_later_comparative_receipt_tampering_rejected(self):
        name = ANCHORS["googl-fy2025"]["package"]
        package = json.loads((ROOT / name).read_text())
        source_row = package["googl_history_review"]["periods"][3]
        source = next(s for s in source_row["sources"] if s["source_id"] == "FY2024-instance")
        manifest = json.loads((ROOT / source["path"]).read_text())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / source["path"]
            path.parent.mkdir(parents=True)
            for field, value in (("source_url", "https://example.com/changed.xml"),
                                 ("accession", "0001652044-24-000022"),
                                 ("sha256", "0" * 64), ("byte_length", 0)):
                bad = deepcopy(manifest)
                bad["artifacts"][0][field] = value
                path.write_text(json.dumps(bad))
                with self.subTest(field=field), self.assertRaises(ValueError):
                    _alphabet_comparatives(root, source_row, deepcopy(self.review["companies"][0]))


if __name__ == "__main__":
    unittest.main()
