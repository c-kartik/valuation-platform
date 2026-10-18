"""Retained revenue/provenance only; never forecast an actual company."""

from copy import deepcopy
from dataclasses import replace
from decimal import Decimal as D, Inexact, ROUND_DOWN, localcontext
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from valuation_platform.valuation import consumer as c
from valuation_platform.valuation.forecast import ForecastValidationError

ROOT = Path(__file__).resolve().parents[2]
KINDS = ("googl-fy2025", "aapl-fy2025")


class RetainedAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages = {kind: json.loads((ROOT / c.ANCHORS[kind]["package"]).read_text()) for kind in KINDS}

    def test_exact_retained_selections_sources_and_distinct_audits(self):
        for kind, revenue, start, end in (
            ("googl-fy2025", "402836000000", "2025-01-01", "2025-12-31"),
            ("aapl-fy2025", "416161000000", "2024-09-29", "2025-09-27"),
        ):
            with self.subTest(kind=kind):
                before = deepcopy(self.packages[kind])
                anchor = c.load_revenue_anchor(kind, ROOT)
                self.assertEqual((anchor.revenue, anchor.raw_value, anchor.precision,
                                  anchor.unit, anchor.scale, anchor.sign_multiplier),
                                 (D(revenue), revenue, "-6", "USD", 1, 1))
                self.assertEqual((anchor.period.annual_start.isoformat(), anchor.period.annual_end.isoformat()), (start, end))
                self.assertEqual(anchor.period.cik, c.ANCHORS[kind]["identity"]["cik"])
                prefix = kind.split("-")[0]
                row = before[prefix + "_history_review"]["periods"][4]
                self.assertEqual(json.loads(anchor.source_details_json), {"fact": row["facts"]["revenue"], "sources": row["sources"]})
                self.assertTrue(anchor.source_reference.endswith(f"#/{prefix}_history_review/periods/4/facts/revenue"))
                self.assertTrue(anchor.effective_reference.endswith(f"#/{prefix}_current_history/periods/4/inputs/revenue"))
                metadata = json.loads(anchor.approval_details_json)
                self.assertEqual(metadata["history_approval"]["sequence"], 2)
                self.assertEqual(metadata["prior_scoped_approval"]["sequence"], 1)
                self.assertEqual(metadata["history_approval"]["previous"], metadata["prior_scoped_approval"]["sha256"])
                self.assertEqual(metadata["revenue_acceptance"]["approval_reference"],
                                 "/accepted_view" if prefix == "aapl" else None)
                self.assertEqual(self.packages[kind], before)

    def test_no_network_writes_or_caller_decimal_dependency(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network forbidden")), \
                patch.object(Path, "write_text", side_effect=AssertionError("write forbidden")):
            for kind in (*KINDS, "meta-fy2025"):
                expected = c.load_revenue_anchor(kind, ROOT)
                with localcontext() as ctx:
                    ctx.prec = 3
                    ctx.rounding = ROUND_DOWN
                    ctx.traps[Inexact] = True
                    ctx.clear_flags()
                    before = ctx.copy()
                    self.assertEqual(c.load_revenue_anchor(kind, ROOT), expected)
                    self.assertEqual((ctx.prec, ctx.rounding, ctx.flags, ctx.traps),
                                     (before.prec, before.rounding, before.flags, before.traps))

    def test_optional_effective_context_is_not_a_gate(self):
        for kind in KINDS:
            prefix = kind.split("-")[0]
            package = deepcopy(self.packages[kind])
            expected = c.prepare_revenue_anchor(kind, package)
            view = package[prefix + "_current_history"]
            row = view["periods"][4]
            row["inputs"] = {"revenue": row["inputs"]["revenue"]}
            row["checklist"] = [x for x in row["checklist"] if x["field"] == "revenue"]
            row["analyst_complete"] = False
            view["financial_input_sufficiency"] = "NOT_ASSESSED"
            self.assertEqual(c.prepare_revenue_anchor(kind, package), expected)

    def test_effective_identity_unit_scale_selection_and_acceptance_rejected(self):
        for kind in KINDS:
            prefix = kind.split("-")[0]
            for field, value in (("cik", 1), ("accession", "wrong"), ("form", "10-Q"),
                                 ("annual_start", "2025-01-01" if prefix == "aapl" else "2024-01-01"),
                                 ("annual_end", "2024-12-31")):
                package = deepcopy(self.packages[kind])
                package[prefix + "_current_history"]["periods"][4]["identity"][field] = value
                with self.subTest(kind=kind, field=field), self.assertRaises(ForecastValidationError):
                    c.prepare_revenue_anchor(kind, package)
            for field, value in (("unit", "USD millions"), ("scale", 1000000), ("multiplier", -1),
                                 ("value", None), ("value", "0"), ("raw_value", "1"),
                                 ("value", "NaN"), ("precision", "-9"), ("source_reference", "other")):
                package = deepcopy(self.packages[kind])
                package[prefix + "_current_history"]["periods"][4]["inputs"]["revenue"][field] = value
                with self.subTest(kind=kind, field=field, value=value), self.assertRaises(ForecastValidationError):
                    c.prepare_revenue_anchor(kind, package)
            for field, value in (("status", "UNAPPROVED"), ("approval_reference", "/invented"),
                                 ("evidence_references", ["/wrong"])):
                package = deepcopy(self.packages[kind])
                row = package[prefix + "_current_history"]["periods"][4]
                next(x for x in row["checklist"] if x["field"] == "revenue")[field] = value
                with self.subTest(kind=kind, field=field), self.assertRaisesRegex(ForecastValidationError, "acceptance"):
                    c.prepare_revenue_anchor(kind, package)

    def test_missing_consumed_revenue_and_broken_binding_fail(self):
        for kind in KINDS:
            prefix = kind.split("-")[0]
            for key in ("revenue",):
                package = deepcopy(self.packages[kind])
                del package[prefix + "_current_history"]["periods"][4]["inputs"][key]
                with self.assertRaises(ForecastValidationError):
                    c.prepare_revenue_anchor(kind, package)
            for field, value in (("approval_sha256", "0" * 64), ("authoritative_current_view", False)):
                package = deepcopy(self.packages[kind])
                package[prefix + "_current_history"][field] = value
                with self.assertRaises(ForecastValidationError):
                    c.prepare_revenue_anchor(kind, package)

    def test_stale_source_review_proposals_audits_and_prior_chain_rejected(self):
        for kind in KINDS:
            prefix = kind.split("-")[0]
            mutations = [
                lambda p: p.update(issuer="wrong company"),
                lambda p: p[prefix + "_history_review"]["periods"][4]["facts"]["revenue"].update(value="1"),
                lambda p: p[prefix + "_history_review"]["periods"][4]["facts"]["revenue"].update(precision="-9"),
                lambda p: p[prefix + "_history_review"].update(source_revision="0" * 64),
                lambda p: p[prefix + "_history_review"].update(review_revision="0" * 64),
                lambda p: p[prefix + "_history_review"]["consolidated_proposals"][0].update(rationale="changed"),
                lambda p: p[prefix + "_history_approval"].update(sha256="0" * 64),
                lambda p: p[prefix + "_history_approval"].update(source_revision="0" * 64),
                lambda p: p[prefix + "_history_approval"].update(previous="0" * 64),
                lambda p: p["accepted_view"]["approval_audit"].update(rationale="changed"),
            ]
            for i, mutate in enumerate(mutations):
                package = deepcopy(self.packages[kind])
                mutate(package)
                with self.subTest(kind=kind, mutation=i), self.assertRaises(ForecastValidationError):
                    c.prepare_revenue_anchor(kind, package)

    def test_positive_finite_base_usd_model_and_explicit_dispatch(self):
        for kind in KINDS:
            anchor = c.load_revenue_anchor(kind, ROOT)
            for changes in ({"revenue": D("0")}, {"revenue": D("Infinity")}, {"scale": 6}):
                with self.assertRaises(ForecastValidationError):
                    replace(anchor, **changes)
        with self.assertRaisesRegex(ForecastValidationError, "Unsupported"):
            c.load_revenue_anchor("latest-aapl", ROOT)


if __name__ == "__main__":
    unittest.main()
