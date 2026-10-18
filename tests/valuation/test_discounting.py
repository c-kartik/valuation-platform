"""Stage B hand fixtures; no actual META forecast assumptions or valuation."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from decimal import Decimal as D, Inexact, ROUND_DOWN, Rounded, localcontext
import json
import unittest

from tests.valuation.test_forecast import synthetic_anchor, synthetic_assumptions, synthetic_year
from valuation_platform.valuation.assumptions import AssumptionValidationError
from valuation_platform.valuation.forecast import (
    forecast_five_years, forecast_to_dict,
)
from valuation_platform.valuation.discounting import (
    DISCOUNTING_CONVENTION_VERSION, DiscountingValidationError, TerminalAssumptions,
    discount_to_enterprise_value, enterprise_value_to_dict, serialize_enterprise_value,
)


def terminal_assumptions(**changes):
    # Terminal margin/DA/investment/WC differ from Year 5: 30%/4%/9%/1%.
    values = dict(operating_margin=D(".30"), operating_tax_rate=D(".20"),
                  d_and_a_percent_revenue=D(".04"), investment_percent_revenue=D(".09"),
                  working_capital_cash_requirement_percent_revenue=D(".01"))
    values.update(changes)
    return TerminalAssumptions(**values)


def stage_a(**changes):
    values = dict(wacc=D(".25"), terminal_growth=D(".05"))
    values.update(changes)
    return forecast_five_years(synthetic_anchor(), synthetic_assumptions(**values))


class TerminalAssumptionTests(unittest.TestCase):
    def test_five_required_rates_and_no_duplicate_wacc_growth(self):
        value = terminal_assumptions()
        self.assertEqual({f.name for f in fields(value)}, {
            "operating_margin", "operating_tax_rate", "d_and_a_percent_revenue",
            "investment_percent_revenue", "working_capital_cash_requirement_percent_revenue",
            "convention_version",
        })
        for missing in (f.name for f in fields(value) if f.name != "convention_version"):
            kwargs = {f.name: getattr(value, f.name) for f in fields(value) if f.name != missing}
            with self.subTest(missing=missing), self.assertRaises(TypeError):
                TerminalAssumptions(**kwargs)
        for extra in ("wacc", "terminal_growth", "revenue_growth"):
            with self.subTest(extra=extra), self.assertRaises(TypeError):
                terminal_assumptions(**{extra: D(".1")})

    def test_every_rate_rejects_missing_wrong_types_and_nonfinite(self):
        for name in (f.name for f in fields(TerminalAssumptions) if f.name != "convention_version"):
            for value in (None, True, 1, .1, "0.1", D("NaN"), D("sNaN"), D("Infinity"), D("-Infinity")):
                with self.subTest(field=name, value=value), self.assertRaises(AssumptionValidationError):
                    terminal_assumptions(**{name: value})

    def test_rate_domains_and_compatibility(self):
        for name in ("d_and_a_percent_revenue", "investment_percent_revenue"):
            with self.assertRaises(AssumptionValidationError):
                terminal_assumptions(**{name: D("-.01")})
            self.assertEqual(getattr(terminal_assumptions(**{name: D(0)}), name), D(0))
        for rate in (D("-.01"), D("1.01")):
            with self.assertRaises(AssumptionValidationError):
                terminal_assumptions(operating_tax_rate=rate)
        for rate in (D(0), D(1)):
            self.assertEqual(terminal_assumptions(operating_tax_rate=rate).operating_tax_rate, rate)
        for margin in (D("-.5"), D("1.2")):
            self.assertEqual(terminal_assumptions(operating_margin=margin).operating_margin, margin)
        self.assertEqual(terminal_assumptions(
            working_capital_cash_requirement_percent_revenue=D("-.02")
        ).working_capital_cash_requirement_percent_revenue, D("-.02"))
        with self.assertRaises(AssumptionValidationError):
            terminal_assumptions(convention_version="cash-pp&e-plus-finance-principal")


class DiscountingTests(unittest.TestCase):
    def test_integrated_hand_calculated_stage_a_to_enterprise_value(self):
        # Stage A hand schedule is independently specified in test_forecast.
        # WACC 25% gives exact factors: .8, .64, .512, .4096, .32768.
        a = stage_a()
        result = discount_to_enterprise_value(a, terminal_assumptions())
        expected = (
            ("8.8", ".8", "7.04"),
            ("9.68", ".64", "6.1952"),
            ("10.648", ".512", "5.451776"),
            ("11.7128", ".4096", "4.79756288"),
            ("12.88408", ".32768", "4.2218553344"),
        )
        for year, numbers in zip(result.years, expected):
            self.assertEqual((year.fcff, year.discount_factor, year.pv_fcff), tuple(D(v) for v in numbers))
        # Revenue 161.051 * 1.05; terminal FCFF margin .30*.80+.04-.09-.01 = .18.
        terminal = result.terminal
        self.assertEqual(tuple(getattr(terminal, name) for name in (
            "revenue", "ebit", "tax", "nopat", "d_and_a", "investment",
            "working_capital_cash_requirement", "fcff")), tuple(D(v) for v in (
                "169.10355", "50.731065", "10.146213", "40.584852", "6.764142",
                "15.2193195", "1.6910355", "30.438639")))
        # TV = 30.438639 / .20; terminal PV = TV * .32768; EV adds annual PVs.
        self.assertEqual(result.terminal_value, D("152.193195"))
        self.assertEqual(result.pv_terminal_value, D("49.8706661376"))
        self.assertEqual(result.pv_explicit_fcff, D("27.7063942144"))
        self.assertEqual(result.enterprise_value, D("77.5770603520"))
        self.assertNotEqual(terminal.ebit, terminal.revenue * a.assumptions.forecast_years[-1].operating_margin)
        self.assertNotEqual(terminal.fcff, a.years[-1].fcff * D("1.05"))

    def test_zero_and_negative_growth_exact_hand_cases(self):
        years = tuple(synthetic_year(i, revenue_growth=D(0)) for i in range(1, 6))
        for growth, revenue, fcff, tv, pv_tv, ev in (
            ("0", "100", "18", "72", "23.59296", "45.10720"),
            ("-.25", "75", "13.5", "27", "8.84736", "30.36160"),
        ):
            with self.subTest(growth=growth):
                result = discount_to_enterprise_value(stage_a(
                    forecast_years=years, terminal_growth=D(growth)), terminal_assumptions())
                self.assertEqual((result.terminal.revenue, result.terminal.fcff, result.terminal_value,
                                  result.pv_terminal_value, result.enterprise_value),
                                 tuple(D(v) for v in (revenue, fcff, tv, pv_tv, ev)))
                self.assertEqual(result.pv_explicit_fcff, D("21.51424"))

    def test_negative_forecast_terminal_and_ev_not_clipped(self):
        years = tuple(synthetic_year(i, revenue_growth=D(0), operating_margin=D("-.20"))
                      for i in range(1, 6))
        result = discount_to_enterprise_value(stage_a(forecast_years=years, terminal_growth=D(0)),
                                              terminal_assumptions(operating_margin=D("-.20")))
        self.assertTrue(all(year.fcff == D(-27) and year.pv_fcff < 0 for year in result.years))
        self.assertEqual((result.terminal.ebit, result.terminal.tax, result.terminal.nopat,
                          result.terminal.fcff), (D(-20), D(0), D(-20), D(-26)))
        self.assertEqual((result.terminal_value, result.pv_terminal_value,
                          result.pv_explicit_fcff, result.enterprise_value),
                         (D(-104), D("-34.07872"), D("-72.61056"), D("-106.68928")))

    def test_zero_terminal_and_signed_working_capital(self):
        a = stage_a(terminal_growth=D(0))
        zero = terminal_assumptions(operating_margin=D(0), d_and_a_percent_revenue=D(0),
                                   investment_percent_revenue=D(0),
                                   working_capital_cash_requirement_percent_revenue=D(0))
        result = discount_to_enterprise_value(a, zero)
        self.assertEqual((result.terminal.fcff, result.terminal_value, result.pv_terminal_value), (D(0),) * 3)
        self.assertEqual(result.enterprise_value, result.pv_explicit_fcff)
        release = discount_to_enterprise_value(a, terminal_assumptions(
            working_capital_cash_requirement_percent_revenue=D("-.01")))
        self.assertEqual(release.terminal.working_capital_cash_requirement, D("-1.61051"))
        self.assertEqual(release.terminal.fcff, D("32.2102"))

    def test_terminal_equations_share_stage_a_loss_and_investment_conventions(self):
        a = stage_a()
        assumptions = terminal_assumptions(operating_margin=D("-.20"))
        result = discount_to_enterprise_value(a, assumptions)
        # Same revenue and five ratios through Stage A must give identical components.
        anchor = replace(synthetic_anchor(), revenue=result.terminal.revenue,
                         raw_value=str(result.terminal.revenue))
        years = tuple(synthetic_year(i, revenue_growth=D(0), operating_margin=D("-.20"),
                      forecast_tax_rate=D(".20"), d_and_a_percent_revenue=D(".04"),
                      capex_percent_revenue=D(".09"), change_in_operating_nwc_percent_revenue=D(".01"))
                      for i in range(1, 6))
        comparison = forecast_five_years(anchor, synthetic_assumptions(forecast_years=years)).years[0]
        for field in fields(comparison):
            if field.name not in ("period_index", "fiscal_year_label"):
                self.assertEqual(getattr(comparison, field.name), getattr(result.terminal, field.name))

    def test_invalid_wacc_growth_even_in_forged_stage_a_rejected(self):
        for field, value in (("wacc", D(0)), ("wacc", D("-.1")), ("wacc", None),
                             ("wacc", D("Infinity")), ("terminal_growth", D(-1)),
                             ("terminal_growth", D("-1.1")), ("terminal_growth", D(".25")),
                             ("terminal_growth", D(".3")), ("terminal_growth", D("NaN"))):
            a = deepcopy(stage_a())
            object.__setattr__(a.assumptions, field, value)
            with self.subTest(field=field, value=value), self.assertRaises(DiscountingValidationError):
                discount_to_enterprise_value(a, terminal_assumptions())

    def test_required_terminal_and_unsupported_timing_or_economics(self):
        for missing in (None, {}, ()):
            with self.assertRaises(DiscountingValidationError):
                discount_to_enterprise_value(stage_a(), missing)
        for convention in ("mid-year", "stub", "", None):
            with self.assertRaisesRegex(DiscountingValidationError, "convention"):
                discount_to_enterprise_value(stage_a(), terminal_assumptions(), convention_version=convention)
        terminal = terminal_assumptions()
        object.__setattr__(terminal, "convention_version", "other")
        with self.assertRaises(DiscountingValidationError):
            discount_to_enterprise_value(stage_a(), terminal)

    def test_malformed_stage_a_structure_order_labels_and_components(self):
        a = stage_a()
        malformed = (
            None, {}, replace(a, anchor=None), replace(a, assumptions=None),
            replace(a, convention_version="unsupported"),
            replace(a, assumptions=replace(a.assumptions, schema_version="2")),
            replace(a, years=list(a.years)), replace(a, years=a.years[:-1]),
            replace(a, years=(a.years[1], a.years[0], *a.years[2:])),
            replace(a, years=(replace(a.years[0], period_index=True), *a.years[1:])),
            replace(a, years=(replace(a.years[0], fiscal_year_label="wrong"), *a.years[1:])),
            replace(a, years=(replace(a.years[0], fcff=D(999)), *a.years[1:])),
            replace(a, years=(replace(a.years[0], revenue=D(999)), *a.years[1:])),
            replace(a, years=(replace(a.years[0], tax=D("NaN")), *a.years[1:])),
            replace(a, years=(replace(a.years[0], investment=11), *a.years[1:])),
            replace(a, years=(None, *a.years[1:])),
        )
        for index, value in enumerate(malformed):
            with self.subTest(index=index), self.assertRaises(DiscountingValidationError):
                discount_to_enterprise_value(value, terminal_assumptions())

    def test_nested_anchor_and_rate_models_revalidated(self):
        for target, field, value in (("anchor", "precision", "bad"),
                                     ("anchor", "unit", "shares"),
                                     ("year", "operating_margin", None),
                                     ("terminal", "investment_percent_revenue", D(-1))):
            a = deepcopy(stage_a())
            terminal = terminal_assumptions()
            model = a.anchor if target == "anchor" else a.assumptions.forecast_years[0] if target == "year" else terminal
            object.__setattr__(model, field, value)
            with self.subTest(target=target, field=field), self.assertRaises(DiscountingValidationError):
                discount_to_enterprise_value(a, terminal)

    def test_immutable_deterministic_serialization_and_full_provenance(self):
        anchor = replace(synthetic_anchor(), source_details_json=json.dumps({
            "basis": "synthetic fixture", "filing_date": "2026-02-01",
            "source_annual_end": "2025-12-31", "source_precision": "INF"}))
        a = forecast_five_years(anchor, synthetic_assumptions(wacc=D(".25"), terminal_growth=D(".05")))
        terminal = terminal_assumptions()
        before = deepcopy((a, terminal))
        result = discount_to_enterprise_value(a, terminal)
        payload = enterprise_value_to_dict(result)
        self.assertEqual(payload["stage_a"], forecast_to_dict(a))
        self.assertEqual(payload["terminal_assumptions"]["operating_margin"], "0.30")
        self.assertEqual(payload["timing"]["analytical_t0"], "2025-12-31")
        self.assertEqual(payload["timing"]["annual_discount_exponents"], [1, 2, 3, 4, 5])
        self.assertEqual(payload["stage_a"]["anchor"]["source_details"]["filing_date"], "2026-02-01")
        self.assertIn("later-filed information", payload["timing"]["notice"])
        self.assertEqual(payload["semantic_input_review"], "NOT_ASSESSED_BY_CALCULATOR")
        self.assertEqual(json.loads(serialize_enterprise_value(result)), payload)
        self.assertEqual(serialize_enterprise_value(result), serialize_enterprise_value(
            discount_to_enterprise_value(a, terminal)))
        self.assertEqual((a, terminal), before)
        self.assertIs(result.stage_a, a)
        payload["stage_a"]["anchor"]["source_details"]["filing_date"] = "changed"
        self.assertNotEqual(payload, enterprise_value_to_dict(result))
        for model, field in ((result, "enterprise_value"), (result.years[0], "pv_fcff"),
                             (result.terminal, "fcff"), (terminal, "operating_margin")):
            with self.assertRaises(FrozenInstanceError):
                setattr(model, field, None)

    def test_precision_traps_flags_and_context_isolation(self):
        a = stage_a(wacc=D(".09"), terminal_growth=D(".03"))
        terminal = terminal_assumptions()
        with localcontext() as caller:
            caller.prec = 3
            caller.rounding = ROUND_DOWN
            caller.traps[Inexact] = True
            caller.clear_flags()
            caller.flags[Rounded] = True
            before = caller.copy()
            result = discount_to_enterprise_value(a, terminal)
            self.assertEqual(result.years[0].discount_factor,
                             D("0.91743119266055045871559633027522935779816513761468"))
            self.assertEqual((caller.prec, caller.rounding, caller.traps, caller.flags),
                             (before.prec, before.rounding, before.traps, before.flags))
            # Error paths also leave the caller's flags/traps untouched.
            bad = replace(a, years=(replace(a.years[0], fcff=D("sNaN")), *a.years[1:]))
            with self.assertRaises(DiscountingValidationError):
                discount_to_enterprise_value(bad, terminal)
            self.assertEqual(caller.flags, before.flags)
        with localcontext() as caller:
            caller.prec = 80
            self.assertEqual(result, discount_to_enterprise_value(a, terminal))

    def test_terminal_half_even_ties_and_arithmetic_overflow(self):
        a = forecast_five_years(synthetic_anchor("1"), synthetic_assumptions(
            forecast_years=tuple(synthetic_year(i, revenue_growth=D(0)) for i in range(1, 6)),
            wacc=D(".25"), terminal_growth=D(0)))
        for last, rounded in (("2", "2"), ("3", "4")):
            terminal = terminal_assumptions(operating_margin=D("0." + "1" * 49 + last + "5"))
            self.assertEqual(discount_to_enterprise_value(a, terminal).terminal.ebit,
                             D("0." + "1" * 49 + rounded))
        # Valid finite input but the terminal multiplication overflows the local policy.
        with self.assertRaises(DiscountingValidationError):
            discount_to_enterprise_value(stage_a(), terminal_assumptions(operating_margin=D("1e999999")))


if __name__ == "__main__":
    unittest.main()
