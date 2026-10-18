"""Presentation checks on synthetic result components; no actual META runs."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from decimal import Decimal, Inexact, ROUND_DOWN, Rounded, localcontext
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.valuation.test_case_inputs import ROOT, EXAMPLES, cli, document, parse
from valuation_platform.valuation import case_inputs as c


def result():
    return c.run_case(c.load_case(EXAMPLES / "synthetic-base.json"), ROOT)


def values(report, label):
    """Check meaningful cells without freezing padding or column widths."""
    row = next(line for line in report.splitlines() if line.split("|")[0].strip() == label)
    return [cell.strip() for cell in row.split("|")[1:]]


def signed_case(annual_margin, terminal_margin):
    doc = document()
    for year in doc["forecast_years"]:
        for key in c.ANNUAL_RATES:
            year[key] = "0"
        year["operating_margin"] = annual_margin
    doc["wacc"] = "0.25"
    doc["terminal_growth"] = "0"
    doc["terminal"] = {key: "0" for key in c.TERMINAL_RATES}
    doc["terminal"]["operating_margin"] = terminal_margin
    return c.run_case(parse(doc), ROOT)


class CaseSummaryTests(unittest.TestCase):
    def test_identity_timing_meanings_and_supplied_limitations(self):
        payload = result()
        report = cli.render_summary(payload)
        doc = payload["submitted_inputs"]
        self.assertIn(payload["case_name"], report)
        self.assertIn(doc["analyst"]["author"], report)
        self.assertIn(doc["analyst"]["timestamp_utc"], report)
        self.assertIn(doc["analyst"]["rationale"], report)
        self.assertIn(doc["scope"], report)
        self.assertIn("SYNTHETIC_FIXTURE", report)
        self.assertIn("CIK 123", report)
        self.assertIn("0000000123-26-000001", report)
        self.assertIn("2025-01-01 to 2025-12-31", report)
        self.assertIn("Fiscal-end analytical date: 2025-12-31", report)
        self.assertIn(payload["stage_b"]["timing"]["notice"], report)
        self.assertIn("USD millions", report)
        self.assertIn("not equity value or per-share value", report)
        self.assertIn("not authenticated or economically validated", report)
        self.assertIn("cash PP&E plus non-overlapping new finance-leased operating assets", report)
        self.assertIn("excludes finance principal", report)
        self.assertIn("full forecast revenue: positive uses cash; negative releases cash", report)
        self.assertIn("SBC, operating-lease service costs", report)
        for limitation in payload["limitations"]:
            self.assertIn(limitation, report)
        # Presentation-only manual basis label, still using a synthetic payload.
        payload["input_basis"] = "MANUAL_INPUT"
        self.assertIn("MANUAL_INPUT (supplied declarations; not economic approval)", cli.render_summary(payload))

    def test_annual_percentages_and_independent_terminal_inputs(self):
        payload = result()
        report = cli.render_summary(payload)
        expected = {"Revenue growth":"10.00%", "Operating margin":"20.00%",
                    "Operating tax rate":"25.00%", "D&A / revenue":"5.00%",
                    "Investment / revenue":"10.00%", "WC cash / full revenue":"2.00%"}
        for label, value in expected.items():
            self.assertEqual(values(report, label), [value] * 5)
        self.assertIn("WACC: 25.00% | Terminal growth: 5.00%", report)
        terminal = report.split("Explicit terminal assumptions (%)", 1)[1]
        for expected in ("Operating margin: 30.00%", "Operating tax rate: 20.00%",
                         "D&A / revenue: 4.00%", "Investment / revenue: 9.00%", "WC cash / full revenue: 1.00%"):
            self.assertIn(expected, terminal)

    def test_annual_cash_components_and_discounting_independent_expectations(self):
        report = cli.render_summary(result())
        # Hand fixture: R=110, EBIT=22, tax=5.5, NOPAT=16.5, DA=5.5,
        # investment=11, WC=2.2, FCFF=8.8; dollar/1e6 display conversion.
        first = {"Revenue":"0.00011000", "EBIT":"0.00002200", "Operating tax":"0.00000550",
                 "NOPAT":"0.00001650", "D&A":"0.00000550", "Investment":"0.00001100",
                 "Working-capital cash requirement":"0.00000220", "FCFF":"0.00000880",
                 "Discounted FCFF":"0.00000704"}
        for label, expected in first.items():
            self.assertEqual(values(report, label)[0], expected)
        self.assertEqual(values(report, "Revenue"), ["0.00011000", "0.00012100", "0.00013310", "0.00014641", "0.00016105"])
        self.assertEqual(values(report, "FCFF"), ["0.00000880", "0.00000968", "0.00001065", "0.00001171", "0.00001288"])
        self.assertEqual(values(report, "Discounted FCFF"), ["0.00000704", "0.00000620", "0.00000545", "0.00000480", "0.00000422"])
        self.assertEqual(values(report, "Discount factor (unitless)"), ["0.800000", "0.640000", "0.512000", "0.409600", "0.327680"])

    def test_reconciliation_and_terminal_contribution_independent_expectations(self):
        report = cli.render_summary(result())
        # Independent retained hand result: PV explicit=27.7063942144 USD,
        # PV TV=49.8706661376 USD, EV=77.5770603520 USD; contribution ->64.29%.
        for expected in ("Terminal FCFF: 0.00003044", "Terminal value at end of Year 5: 0.00015219",
                         "Explicit-period PV: 0.00002771", "+ Discounted terminal value: 0.00004987",
                         "= Enterprise value (EV): 0.00007758", "EV contribution: 64.29%"):
            self.assertIn(expected, report)

    def test_zero_ev_ratio_is_undefined_even_if_terminal_pv_is_nonzero(self):
        payload = signed_case("0", "0")
        self.assertEqual(Decimal(payload["stage_b"]["enterprise_value"]), Decimal(0))
        self.assertIn("undefined (EV is zero)", cli.render_summary(payload))
        # Presentation boundary: do not infer zero/zero or reconstruct EV from
        # altered components. The renderer consumes the supplied EV unchanged.
        payload["stage_b"]["pv_terminal_value"] = "10"
        self.assertIn("undefined (EV is zero)", cli.render_summary(payload))

    def test_negative_ev_is_preserved_with_signed_ratio_explanation(self):
        payload = signed_case("-0.10", "-0.10")
        # Five -10 flows plus -10 perpetuity at 25% => EV -40, PV TV -13.1072.
        self.assertEqual(Decimal(payload["stage_b"]["enterprise_value"]), Decimal(-40))
        report = cli.render_summary(payload)
        self.assertIn("Enterprise value (EV): -0.00004000", report)
        self.assertIn("EV contribution: 32.77%", report)
        self.assertIn("EV is negative", report)

    def test_negative_and_above_100_contributions_are_not_clamped(self):
        # PV explicit 134.464, PV TV -13.1072, EV 121.3568 => -10.80%.
        negative = signed_case("0.50", "-0.10")
        self.assertEqual(Decimal(negative["stage_b"]["enterprise_value"]), Decimal("121.3568"))
        report = cli.render_summary(negative)
        self.assertIn("EV contribution: -10.80%", report)
        self.assertIn("offsetting explicit/terminal PVs", report)
        self.assertIn("not clamped", report)
        # PV explicit -26.8928, PV TV 131.072, EV 104.1792 =>125.81%.
        above = signed_case("-0.10", "1.00")
        self.assertEqual(Decimal(above["stage_b"]["enterprise_value"]), Decimal("104.1792"))
        report = cli.render_summary(above)
        self.assertIn("EV contribution: 125.81%", report)
        self.assertIn("not clamped", report)

    def test_half_even_display_rounding_and_no_result_mutation_or_dcf_calls(self):
        payload = result()
        # Supplied presentation operands, not recomputed DCF results: cent ties
        # in base USD map to the eighth decimal of USD millions.
        payload["stage_b"]["stage_a"]["years"][0]["revenue"] = "1234567.885"
        payload["stage_b"]["stage_a"]["years"][1]["revenue"] = "1234567.895"
        payload["submitted_inputs"]["forecast_years"][0]["revenue_growth"] = "0.12345"
        payload["submitted_inputs"]["forecast_years"][1]["revenue_growth"] = "0.12355"
        before = deepcopy(payload)
        with patch.object(cli, "run_case") as runner, patch.object(c, "forecast_five_years") as forecast, patch.object(c, "discount_to_enterprise_value") as discount:
            report = cli.render_summary(payload)
            runner.assert_not_called(); forecast.assert_not_called(); discount.assert_not_called()
        self.assertEqual(values(report, "Revenue")[:2], ["1.23456788", "1.23456790"])
        self.assertEqual(values(report, "Revenue growth")[:2], ["12.34%", "12.36%"])
        self.assertIn("Rounded components may not sum", report)
        self.assertEqual(payload, before)

    def test_decimal_precision_rounding_traps_flags_and_exponents_isolated(self):
        payload = result()
        expected = cli.render_summary(payload)
        with localcontext() as caller:
            caller.prec = 3; caller.rounding = ROUND_DOWN
            caller.Emax = 3; caller.Emin = -3
            caller.traps[Inexact] = True; caller.clear_flags(); caller.flags[Rounded] = True
            before = caller.copy()
            self.assertEqual(cli.render_summary(payload), expected)
            self.assertEqual((caller.prec, caller.rounding, caller.Emax, caller.Emin, caller.traps, caller.flags),
                             (before.prec, before.rounding, before.Emax, before.Emin, before.traps, before.flags))

    def test_default_and_explicit_json_output_remain_byte_identical(self):
        source = EXAMPLES / "synthetic-base.json"
        expected = json.dumps(result(), sort_keys=True, indent=2) + "\n"
        for suffix in ([], ["--format", "json"]):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(cli.main([str(source), "--run", *suffix]), 0)
            self.assertEqual(stdout.getvalue(), expected)
            self.assertEqual(Decimal(json.loads(stdout.getvalue())["stage_b"]["enterprise_value"]), Decimal("77.5770603520"))

    def test_format_selection_validation_does_not_calculate_or_render(self):
        for fmt in ("summary", "json"):
            with patch.object(cli, "run_case") as runner, patch.object(cli, "render_summary") as renderer:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    self.assertEqual(cli.main([str(EXAMPLES / "synthetic-base.json"), "--format", fmt]), 0)
                self.assertIn("no calculation", stdout.getvalue())
                runner.assert_not_called(); renderer.assert_not_called()
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failure:
            cli.main([str(EXAMPLES / "synthetic-base.json"), "--format", "html"])
        self.assertEqual(failure.exception.code, 2)

    def test_summary_stdout_explicit_save_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp); source = folder / "case.json"
            source.write_text(json.dumps(document()))
            original = source.read_bytes(); stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(cli.main([str(source), "--run", "--format", "summary"]), 0)
            self.assertEqual(set(folder.iterdir()), {source})
            self.assertIn("ENTERPRISE VALUE ONLY", stdout.getvalue())
            target = folder / "review.txt"
            with redirect_stdout(io.StringIO()) as saved_stdout:
                self.assertEqual(cli.main([str(source), "--run", "--format", "summary", "--output", str(target)]), 0)
            self.assertEqual(saved_stdout.getvalue(), "")
            saved = target.read_bytes()
            self.assertEqual(target.read_text(), stdout.getvalue())
            for dest in (target, source):
                with redirect_stderr(io.StringIO()), patch.object(cli, "run_case") as runner:
                    self.assertEqual(cli.main([str(source), "--run", "--format", "summary", "--output", str(dest)]), 2)
                    runner.assert_not_called()
            self.assertEqual(target.read_bytes(), saved)
            self.assertEqual(source.read_bytes(), original)

    def test_protected_paths_and_output_requires_run_for_both_formats(self):
        source = EXAMPLES / "synthetic-base.json"
        dest = ROOT / "docs/evidence/forbidden-summary.txt"
        for fmt in ("summary", "json"):
            with patch.object(cli, "run_case") as runner, redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main([str(source), "--run", "--format", fmt, "--output", str(dest)]), 2)
                with self.assertRaises(SystemExit):
                    cli.main([str(source), "--format", fmt, "--output", str(dest)])
                runner.assert_not_called()
        self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
