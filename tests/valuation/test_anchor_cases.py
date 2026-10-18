"""Company intake checks; only synthetic fixtures reach financial calculations."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal as D, Inexact, ROUND_DOWN, localcontext
import hashlib
import io
import json
import socket
import tempfile
import unittest
from unittest.mock import patch

from tests.valuation.test_case_inputs import ROOT, EXAMPLES, cli, document, parse
from tests.valuation.test_equity_case_inputs import equity_document
from valuation_platform.valuation import case_inputs as c
from valuation_platform.valuation.consumer import ANCHORS


class AnchorCaseTests(unittest.TestCase):
    def test_new_templates_all_37_unset_no_financial_acceptance_or_calculation(self):
        for kind in ("googl-fy2025", "aapl-fy2025"):
            for equity in (False, True):
                path = EXAMPLES / (kind + ("-equity-unset.json" if equity else "-unset.json"))
                doc = json.loads(path.read_text())
                self.assertEqual(doc["anchor"], {"kind": kind, **ANCHORS[kind]["identity"]})
                self.assertEqual(doc["analyst"], dict(author=None, timestamp_utc=None, rationale=None))
                values = [year[key] for year in doc["forecast_years"] for key in c.ANNUAL_RATES]
                values += [doc["wacc"], doc["terminal_growth"], *doc["terminal"].values()]
                self.assertEqual(values, [None] * 37)
                self.assertEqual([y["fiscal_year_label"] for y in doc["forecast_years"]], [f"FY{i}" for i in range(2026, 2031)])
                self.assertEqual(doc["conventions"]["forecast"], "manual-fcff-v1")
                with patch.object(c, "load_revenue_anchor") as anchor, patch.object(c, "forecast_five_years") as a:
                    with self.assertRaises(c.CaseInputError) as fail:
                        c.load_case(path)
                    self.assertEqual(sum("UNSET; supply a fractional" in e for e in fail.exception.errors), 37)
                    anchor.assert_not_called()
                    a.assert_not_called()
                if equity:
                    b = doc["bridge"]
                    self.assertIsNone(b["components"])
                    self.assertTrue(b["unresolved_requirements"])
                    self.assertEqual(b["shares"]["company_cik"], doc["anchor"]["cik"])
                    self.assertEqual(b["shares"]["observation_date"], doc["anchor"]["annual_end"])
                    for key in ("shares", "class_id", "award_policy", "equivalence_convention"):
                        self.assertIsNone(b["shares"][key])
                    self.assertIn("bridge.unresolved_requirements", str(fail.exception))

    def test_anchor_metadata_paths_and_no_meta_convention_transfer(self):
        # Deliberately invalid validation fixtures, never executed as forecasts.
        for kind in ("googl-fy2025", "aapl-fy2025"):
            doc = json.loads((EXAMPLES / (kind + "-unset.json")).read_text())
            for field, value in (("cik", 1326801), ("accession", "wrong"), ("form", "10-Q"),
                                 ("annual_start", "wrong"), ("annual_end", "wrong"),
                                 ("unit", "USD millions"), ("scale", 1000000)):
                changed = deepcopy(doc)
                changed["anchor"][field] = value
                with self.subTest(kind=kind, field=field), self.assertRaises(c.CaseInputError) as fail:
                    parse(changed)
                self.assertIn("anchor." + field, str(fail.exception))
            doc["conventions"]["forecast"] = "meta-base-fcff-v1"
            with self.assertRaises(c.CaseInputError) as fail:
                parse(doc)
            self.assertIn("no META economic approval transfers", str(fail.exception))
            doc = json.loads((EXAMPLES / (kind + "-equity-unset.json")).read_text())
            doc["bridge"]["convention_version"] = "meta-base-equity-bridge-v1"
            with self.assertRaises(c.CaseInputError) as fail:
                parse(doc)
            self.assertIn("bridge.convention_version", str(fail.exception))

    def test_aapl_calendar_uses_ordinal_periods_without_changing_arithmetic(self):
        # Synthetic CIK/revenue only, with a September fiscal end to exercise the
        # calendar handoff. No AAPL assumptions or valuation are constructed.
        from datetime import date
        from valuation_platform.valuation.forecast import forecast_five_years
        from valuation_platform.valuation.discounting import discount_to_enterprise_value, enterprise_value_to_dict
        from tests.valuation.test_forecast import synthetic_anchor, synthetic_assumptions
        from valuation_platform.valuation.discounting import TerminalAssumptions
        anchor = synthetic_anchor()
        anchor = replace(anchor, period=replace(anchor.period, annual_start=date(2024, 9, 29), annual_end=date(2025, 9, 27)))
        assumptions = synthetic_assumptions(anchor_fiscal_end=date(2025, 9, 27))
        forecast = forecast_five_years(anchor, assumptions, convention_version="manual-fcff-v1")
        terminal = TerminalAssumptions(D(".20"), D(".25"), D(".05"), D(".10"), D(".02"), "manual-fcff-v1")
        result = enterprise_value_to_dict(discount_to_enterprise_value(forecast, terminal))
        self.assertEqual(result["timing"]["analytical_t0"], "2025-09-27")
        self.assertEqual([y["period_index"] for y in result["years"]], [1, 2, 3, 4, 5])
        self.assertEqual(D(result["stage_a"]["years"][0]["revenue"]), D("110"))

    def test_shared_declarations_synthetic_a_b_c_and_decimal_isolation(self):
        doc = equity_document()
        doc["conventions"]["forecast"] = "manual-fcff-v1"
        doc["bridge"]["convention_version"] = "manual-equity-bridge-v1"
        with patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            baseline = c.run_case(parse(doc), ROOT)
            with localcontext() as ctx:
                ctx.prec = 3
                ctx.rounding = ROUND_DOWN
                ctx.traps[Inexact] = True
                ctx.clear_flags()
                before = ctx.copy()
                result = c.run_case(parse(doc), ROOT)
                summary = cli.render_summary(result)
                self.assertEqual((ctx.prec, ctx.rounding, ctx.traps, ctx.flags),
                                 (before.prec, before.rounding, before.traps, before.flags))
        self.assertEqual(result, baseline)
        self.assertEqual(D(result["stage_c"]["value_per_share"]), D("16.644265088"))
        self.assertIn("Value per share (USD/share): 16.64426509", summary)
        self.assertIn("actual company selections", " ".join(result["limitations"]))
        self.assertEqual(result["stage_b"]["stage_a"]["convention_version"], "manual-fcff-v1")
        self.assertEqual(result["stage_b"]["terminal_assumptions"]["convention_version"], "manual-fcff-v1")

    def test_existing_examples_and_ev_json_byte_compatible_with_starting_checkpoint(self):
        hashes = {
            "meta-fy2025-equity-unset.json": "f59093977c0c607adb18821690be15109121fb538209b68144734593280b4ba1",
            "meta-fy2025-unset.json": "9ff2d831f7a8e8939dd6c8f51254b8c8d9ad0cf3883c2bf0d7e0f2895499ac47",
            "synthetic-base.json": "2c7d5bc9e2983e5feb6ff31e13ac20aad4ab145efc38b33b13d4b221a5308e37",
            "synthetic-equity.json": "7c8dbf37d1cf9016fa0cb05c274045ec4a8b8da801e32f968f3bab59c1d78459",
        }
        for filename, expected in hashes.items():
            self.assertEqual(hashlib.sha256((EXAMPLES / filename).read_bytes()).hexdigest(), expected)
        for filename, expected in (
            ("synthetic-base.json", "f2e6852ecb94d4533ed051501f07b37888f677df2fc7b9a07a1c1b98a99912c3"),
            ("synthetic-equity.json", "2a0e4ffc2e2d614f3e410b9e2cadff7c033e414da712218fc2b5f40c323ea5b3"),
        ):
            result = c.run_case(c.load_case(EXAMPLES / filename), ROOT)
            payload = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)

    def test_float_nonfinite_duplicate_and_integer_rate_paths(self):
        for token in ("0.12", "1e-2", "NaN", "Infinity", "-Infinity", "12"):
            doc = document()
            doc["forecast_years"][2]["revenue_growth"] = "TOKEN"
            text = json.dumps(doc).replace('"TOKEN"', token)
            with self.subTest(token=token), self.assertRaises(c.CaseInputError) as fail:
                c.read_case(text)
            self.assertIn("forecast_years[2].revenue_growth", str(fail.exception))
        text = json.dumps(document()).replace('"revenue_growth": "0.10"', '"revenue_growth": "0.10", "revenue_growth": "0.20"', 1)
        with self.assertRaises(c.CaseInputError) as fail:
            c.read_case(text)
        self.assertIn("forecast_years[0].revenue_growth: Duplicate JSON key", str(fail.exception))

    def test_annual_terminal_wacc_scope_and_cross_company_errors(self):
        variants = []
        doc = document(); doc["forecast_years"][2]["forecast_tax_rate"] = "1.1"
        variants.append((doc, "forecast_years[2].forecast_tax_rate"))
        doc = document(); doc["forecast_years"][1]["d_and_a_percent_revenue"] = "-0.1"
        variants.append((doc, "forecast_years[1].d_and_a_percent_revenue"))
        doc = document(); doc["terminal"]["investment_percent_revenue"] = "-0.1"
        variants.append((doc, "terminal.investment_percent_revenue"))
        doc = document(); doc["terminal"]["operating_tax_rate"] = "1.1"
        variants.append((doc, "terminal.operating_tax_rate"))
        doc = document(); doc["wacc"] = "0"
        variants.append((doc, "wacc:"))
        doc = document(); doc["terminal_growth"] = doc["wacc"]
        variants.append((doc, "terminal_growth (relative to wacc)"))
        doc = document(); del doc["forecast_years"][1]
        variants.append((doc, "forecast_years:"))
        doc = document(); del doc["terminal"]["d_and_a_percent_revenue"]
        variants.append((doc, "terminal.d_and_a_percent_revenue"))
        doc = document(); doc["forecast_years"][1]["unknown"] = "1"
        variants.append((doc, "forecast_years[1].unknown"))
        doc = equity_document(); doc["bridge"] = None
        variants.append((doc, "bridge: UNSET"))
        doc = equity_document(); doc["bridge"]["shares"]["company_cik"] = 320193
        variants.append((doc, "company/date mismatch"))
        for doc, message in variants:
            with self.subTest(message=message), patch.object(c, "forecast_five_years") as engine:
                with self.assertRaises(c.CaseInputError) as fail:
                    parse(doc)
                self.assertIn(message, str(fail.exception))
                engine.assert_not_called()

    def test_dispatch_routes_new_anchors_and_stops_before_actual_company_calculation(self):
        # Public run dispatch exercised with sentinels; no actual-company rates,
        # historical retrieval or financial calculations are executed.
        base = parse(document())
        for kind in ("googl-fy2025", "aapl-fy2025"):
            case = replace(base, anchor_kind=kind)
            with patch.object(c, "read_case", return_value=case), \
                    patch.object(c, "load_revenue_anchor", side_effect=ValueError("STOP at revenue boundary")) as loader, \
                    patch.object(c, "forecast_five_years") as engine:
                with self.assertRaisesRegex(ValueError, "STOP at revenue boundary"):
                    c.run_case(case, ROOT)
                loader.assert_called_once_with(kind, ROOT)
                engine.assert_not_called()

    def test_cli_validation_no_calculation_or_result_write(self):
        for kind in ("meta-fy2025", "googl-fy2025", "aapl-fy2025"):
            path = EXAMPLES / (kind + "-unset.json")
            before = path.read_bytes()
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err, \
                    patch.object(cli, "run_case") as run:
                self.assertEqual(cli.main([str(path), "--format", "summary"]), 2)
                self.assertIn("forecast_years[2].revenue_growth", err.getvalue())
                run.assert_not_called()
            self.assertEqual(path.read_bytes(), before)
        with tempfile.TemporaryDirectory() as tmp:
            output = ROOT / "README.md"
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                cli.main([str(EXAMPLES / "synthetic-base.json"), "--output", str(output)])


if __name__ == "__main__":
    unittest.main()
