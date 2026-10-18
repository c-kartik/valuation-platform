"""Independent synthetic arithmetic; never run actual META forecast assumptions."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from datetime import date
from decimal import Decimal as D, Inexact, ROUND_DOWN, getcontext, localcontext
import json
from pathlib import Path
import unittest

from valuation_platform.analyst.nwc import Period
from valuation_platform.valuation.assumptions import ForecastYearAssumptions, ValuationAssumptions
from valuation_platform.valuation.consumer import (
    load_meta_revenue_anchor, prepare_meta_revenue_anchor,
)
from valuation_platform.valuation.forecast import (
    CONVENTION_VERSION, ForecastValidationError, RevenueAnchor,
    forecast_five_years, forecast_to_dict, serialize_forecast,
)


ROOT = Path(__file__).resolve().parents[2]


def synthetic_anchor(revenue="100"):
    return RevenueAnchor(
        Period(123, "0000000123-26-000001", date(2025, 1, 1), date(2025, 12, 31)),
        D(revenue), revenue, "INF", "synthetic:revenue", "synthetic:effective",
        "synthetic:approval", '{"basis":"synthetic; no SEC fact"}',
        '{"basis":"synthetic fixture; no actual-case approval"}',
    )


def synthetic_year(index, **changes):
    values = dict(
        period_index=index, fiscal_year_label=f"Synthetic period {index}",
        revenue_growth=D(".10"), operating_margin=D(".20"),
        forecast_tax_rate=D(".25"), d_and_a_percent_revenue=D(".05"),
        capex_percent_revenue=D(".10"), change_in_operating_nwc_percent_revenue=D(".02"),
    )
    values.update(changes)
    return ForecastYearAssumptions(**values)


def synthetic_assumptions(**changes):
    values = dict(
        schema_version="1", company_cik=123,
        anchor_accession_number="0000000123-26-000001", anchor_fiscal_end=date(2025, 12, 31),
        forecast_years=tuple(synthetic_year(i) for i in range(1, 6)),
        wacc=D(".09"), terminal_growth=D(".03"),
    )
    values.update(changes)
    return ValuationAssumptions(**values)


class ForecastTests(unittest.TestCase):
    def test_hand_calculated_five_year_components_and_compounding(self):
        result = forecast_five_years(synthetic_anchor(), synthetic_assumptions())
        # Hand calculation: recurring growth 10%; EBIT 20%; tax 25%;
        # DA 5%, investment 10%, WC cash 2% of full revenue => FCFF 8% of revenue.
        expected = (
            ("110", "22", "5.5", "16.5", "5.5", "11", "2.2", "8.8"),
            ("121", "24.2", "6.05", "18.15", "6.05", "12.1", "2.42", "9.68"),
            ("133.1", "26.62", "6.655", "19.965", "6.655", "13.31", "2.662", "10.648"),
            ("146.41", "29.282", "7.3205", "21.9615", "7.3205", "14.641", "2.9282", "11.7128"),
            ("161.051", "32.2102", "8.05255", "24.15765", "8.05255", "16.1051", "3.22102", "12.88408"),
        )
        for year, numbers in zip(result.years, expected):
            actual = tuple(getattr(year, field) for field in (
                "revenue", "ebit", "tax", "nopat", "d_and_a", "investment",
                "working_capital_cash_requirement", "fcff"))
            self.assertEqual(actual, tuple(D(v) for v in numbers))
        self.assertEqual(tuple(y.period_index for y in result.years), (1, 2, 3, 4, 5))

    def test_loss_zero_ebit_and_wc_release_hand_cases(self):
        cases = (
            ({"operating_margin": D("-.20")}, "-22", "0", "-22", "-29.7"),
            ({"operating_margin": D("0")}, "0", "0", "0", "-7.7"),
            ({"change_in_operating_nwc_percent_revenue": D("-.02")},
             "22", "5.5", "16.5", "13.2"),
        )
        for changes, ebit, tax, nopat, fcff in cases:
            with self.subTest(changes=changes):
                assumptions = synthetic_assumptions(forecast_years=tuple(
                    synthetic_year(i, **changes) for i in range(1, 6)))
                first = forecast_five_years(synthetic_anchor(), assumptions).years[0]
                self.assertEqual((first.ebit, first.tax, first.nopat, first.fcff),
                                 tuple(D(v) for v in (ebit, tax, nopat, fcff)))

    def test_full_revenue_wc_with_zero_growth_then_minus_100_percent(self):
        years = (synthetic_year(1, revenue_growth=D(0)),
                 synthetic_year(2, revenue_growth=D(-1)),
                 *(synthetic_year(i) for i in range(3, 6)))
        result = forecast_five_years(synthetic_anchor(), synthetic_assumptions(forecast_years=years))
        self.assertEqual(result.years[0].working_capital_cash_requirement, D(2))
        self.assertEqual(result.years[0].fcff, D(8))
        for year in result.years[1:]:
            self.assertEqual((year.revenue, year.ebit, year.tax, year.fcff), (D(0),) * 4)

    def test_schema_identity_and_declared_convention_rejected(self):
        for changes in ({"schema_version": "2"}, {"company_cik": 456},
                        {"anchor_accession_number": "0000000123-26-000002"},
                        {"anchor_fiscal_end": date(2024, 12, 31)}):
            with self.subTest(changes=changes), self.assertRaises(ForecastValidationError):
                forecast_five_years(synthetic_anchor(), synthetic_assumptions(**changes))
        with self.assertRaisesRegex(ForecastValidationError, "convention"):
            forecast_five_years(synthetic_anchor(), synthetic_assumptions(),
                                convention_version="cash-only-with-finance-principal")
        for anchor, assumptions in ((None, synthetic_assumptions()), (synthetic_anchor(), None)):
            with self.assertRaises(ForecastValidationError):
                forecast_five_years(anchor, assumptions)

    def test_anchor_numeric_units_scale_and_missing_metadata(self):
        for changes in ({"revenue": None}, {"revenue": D(0)}, {"revenue": D("NaN")},
                        {"raw_value": "101"}, {"unit": "USD millions"}, {"scale": 1000000},
                        {"precision": ""}, {"source_reference": ""},
                        {"source_details_json": "[]"}, {"sign_multiplier": -1}):
            with self.subTest(changes=changes), self.assertRaises(ForecastValidationError):
                replace(synthetic_anchor(), **changes)

    def test_output_immutable_deterministic_and_copies_metadata(self):
        anchor = synthetic_anchor()
        assumptions = synthetic_assumptions()
        before = deepcopy((anchor, assumptions))
        result = forecast_five_years(anchor, assumptions)
        payload = forecast_to_dict(result)
        self.assertEqual(json.loads(serialize_forecast(result)), payload)
        self.assertEqual(serialize_forecast(result), serialize_forecast(
            forecast_five_years(anchor, assumptions)))
        self.assertIs(result.anchor, anchor)
        self.assertIs(result.assumptions, assumptions)
        self.assertEqual((anchor, assumptions), before)
        self.assertEqual(payload["convention_version"], CONVENTION_VERSION)
        self.assertEqual(payload["anchor"]["precision"], "INF")
        self.assertEqual(payload["semantic_input_review"], "NOT_ASSESSED_BY_CALCULATOR")
        self.assertIsInstance(payload["years"][0]["fcff"], str)
        payload["anchor"]["source_details"]["basis"] = "changed copy"
        self.assertNotEqual(payload, forecast_to_dict(result))
        for value, field in ((result, "convention_version"), (result.years[0], "fcff"),
                             (anchor, "revenue")):
            with self.assertRaises(FrozenInstanceError):
                setattr(value, field, None)

    def test_local_precision_rounding_and_flags_are_isolated(self):
        assumptions = synthetic_assumptions(forecast_years=tuple(
            synthetic_year(i, revenue_growth=D(".123456789012345678901234567890123456789"))
            for i in range(1, 6)))
        with localcontext() as caller:
            caller.prec = 3
            caller.rounding = ROUND_DOWN
            caller.traps[Inexact] = True
            caller.clear_flags()
            before = caller.copy()
            result = forecast_five_years(synthetic_anchor(), assumptions)
            # One + growth fits 50 digits; multiplication by 100 shifts exactly.
            self.assertEqual(result.years[0].revenue,
                             D("112.345678901234567890123456789012345678900"))
            self.assertEqual((caller.prec, caller.rounding, caller.traps, caller.flags),
                             (before.prec, before.rounding, before.traps, before.flags))
        with localcontext() as caller:
            caller.prec = 80
            self.assertEqual(result, forecast_five_years(synthetic_anchor(), assumptions))
            self.assertLessEqual(len(result.years[-1].revenue.as_tuple().digits), 50)

    def test_arithmetic_overflow_rejected_without_changing_caller(self):
        before = getcontext().copy()
        with self.assertRaisesRegex(ForecastValidationError, "arithmetic"):
            forecast_five_years(synthetic_anchor("1e999999"), synthetic_assumptions(
                forecast_years=tuple(synthetic_year(i, revenue_growth=D(99)) for i in range(1, 6))))
        self.assertEqual(getcontext().flags, before.flags)

    def test_fiftieth_digit_ties_round_half_even(self):
        for last, rounded in (("2", "2"), ("3", "4")):
            years = tuple(synthetic_year(
                i, revenue_growth=D(0), operating_margin=D("0." + "1" * 49 + last + "5"),
                forecast_tax_rate=D(0), d_and_a_percent_revenue=D(0),
                capex_percent_revenue=D(0), change_in_operating_nwc_percent_revenue=D(0),
            ) for i in range(1, 6))
            first = forecast_five_years(synthetic_anchor("1"),
                synthetic_assumptions(forecast_years=years)).years[0]
            self.assertEqual(first.fcff, D("0." + "1" * 49 + rounded))

    def test_explicit_operand_boundary_and_unused_wacc_g(self):
        baseline = forecast_five_years(synthetic_anchor(), synthetic_assumptions())
        changed = forecast_five_years(synthetic_anchor(), synthetic_assumptions(
            wacc=D(".5"), terminal_growth=D("-.1")))
        self.assertEqual(baseline.years, changed.years)
        for operand in ("cfo", "movement_rows", "sbc_addback", "finance_principal",
                        "finance_amortization", "capital_creditors", "historical_nwc"):
            with self.subTest(operand=operand), self.assertRaises(TypeError):
                forecast_five_years(synthetic_anchor(), synthetic_assumptions(), **{operand: D(1)})
        self.assertNotIn("sbc_addback", {f.name for f in fields(baseline.years[0])})
        # There is deliberately no test claiming to infer hidden ratio overlap.


class METAAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads((ROOT / "docs/company-data-preparation/meta-analyst-input-package.json").read_text())
        cls.decisions = json.loads((ROOT / "docs/company-data-preparation/trillion-review-batch.json").read_text())["decisions"]

    def test_retained_anchor_precision_sources_and_no_mutation(self):
        before = deepcopy((self.package, self.decisions))
        anchor = prepare_meta_revenue_anchor(self.package, self.decisions)
        self.assertEqual(anchor, load_meta_revenue_anchor(ROOT))
        self.assertEqual(anchor.revenue, D("200966000000"))
        self.assertEqual((anchor.period.cik, anchor.period.accession, anchor.period.annual_start,
                          anchor.period.annual_end, anchor.period.form),
                         (1326801, "0001628280-26-003942", date(2025, 1, 1), date(2025, 12, 31), "10-K"))
        self.assertEqual((anchor.unit, anchor.scale, anchor.precision), ("USD", 1, "-6"))
        detail = json.loads(anchor.source_details_json)
        self.assertEqual(detail["fact"], self.package["periods"][4]["facts"]["revenue"])
        self.assertEqual(detail["sources"], self.package["periods"][4]["sources"])
        self.assertEqual(json.loads(anchor.approval_details_json)["sha256"],
                         self.package["history_approval"]["sha256"])
        self.assertEqual((self.package, self.decisions), before)
        self.assertFalse(self.package["current_history"]["valuation_consumption_approved"])
        # No forecast is run with this real anchor.

    def test_stale_source_review_proposal_and_audit_rejected(self):
        for area, key, value in (
            ("root", "review_revision", "changed"),
            ("fact", "value", "100"), ("fact", "precision", "-3"),
            ("audit", "source_revision", "changed"), ("audit", "author", "forged"),
        ):
            p = deepcopy(self.package)
            target = p if area == "root" else p["history_approval"] if area == "audit" else p["periods"][4]["facts"]["revenue"]
            target[key] = value
            with self.subTest(area=area, key=key), self.assertRaises(ForecastValidationError):
                prepare_meta_revenue_anchor(p, self.decisions)
        decisions = deepcopy(self.decisions)
        next(d for d in decisions if d["ticker"] == "META")["recommendation"] = "changed"
        with self.assertRaisesRegex(ForecastValidationError, "Stale"):
            prepare_meta_revenue_anchor(self.package, decisions)

    def test_effective_identity_revenue_and_missing_bindings_rejected(self):
        for field, value in (("cik", 1), ("accession", "wrong"), ("annual_start", "2024-01-01"),
                             ("annual_end", "2024-12-31"), ("form", "10-K/A")):
            p = deepcopy(self.package)
            p["current_history"]["periods"][4]["identity"][field] = value
            with self.subTest(field=field), self.assertRaises(ForecastValidationError):
                prepare_meta_revenue_anchor(p, self.decisions)
        for field, value in (("value", None), ("unit", "pure"), ("precision", "-3"),
                             ("raw_value", "1"), ("sign_multiplier", -1)):
            p = deepcopy(self.package)
            p["current_history"]["periods"][4]["inputs"]["revenue"][field] = value
            with self.subTest(field=field), self.assertRaises(ForecastValidationError):
                prepare_meta_revenue_anchor(p, self.decisions)
        for missing in ("history_approval", "current_history"):
            p = deepcopy(self.package)
            del p[missing]
            with self.assertRaises(ForecastValidationError):
                prepare_meta_revenue_anchor(p, self.decisions)
        p = deepcopy(self.package)
        del p["current_history"]["periods"][4]["inputs"]["revenue"]
        with self.assertRaises(ForecastValidationError):
            prepare_meta_revenue_anchor(p, self.decisions)

    def test_optional_context_missing_or_conflicting_does_not_gate_revenue(self):
        p = deepcopy(self.package)
        for row in p["current_history"]["periods"]:
            row["inputs"] = {"revenue": row["inputs"]["revenue"]}
            row["complete_expense_basis_da"] = None
        self.assertEqual(prepare_meta_revenue_anchor(p, self.decisions),
                         prepare_meta_revenue_anchor(self.package, self.decisions))
        p["current_history"]["periods"][4]["inputs"]["reported_cfo"] = {"value": "conflict"}
        self.assertEqual(prepare_meta_revenue_anchor(p, self.decisions).revenue, D("200966000000"))


if __name__ == "__main__":
    unittest.main()
