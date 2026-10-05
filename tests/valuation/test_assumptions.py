from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime
from decimal import Decimal
import json
import unittest

from valuation_platform.valuation import (
    AssumptionValidationError,
    ForecastYearAssumptions,
    ValuationAssumptions,
    valuation_assumptions_to_dict,
)


class IntSubclass(int):
    pass


class TupleSubclass(tuple):
    pass


def forecast_year(index: int, **overrides: object) -> ForecastYearAssumptions:
    values: dict[str, object] = {
        "period_index": index,
        "fiscal_year_label": f"FY{2025 + index}",
        "revenue_growth": Decimal("0.10"),
        "operating_margin": Decimal("0.30"),
        "forecast_tax_rate": Decimal("0.20"),
        "d_and_a_percent_revenue": Decimal("0.05"),
        "capex_percent_revenue": Decimal("0.10"),
        "change_in_operating_nwc_percent_revenue": Decimal("0.01"),
    }
    values.update(overrides)
    return ForecastYearAssumptions(**values)  # type: ignore[arg-type]


def assumptions(**overrides: object) -> ValuationAssumptions:
    values: dict[str, object] = {
        "schema_version": "1",
        "company_cik": 1326801,
        "anchor_accession_number": "0001628280-26-003942",
        "anchor_fiscal_end": date(2025, 12, 31),
        "forecast_years": tuple(forecast_year(index) for index in range(1, 6)),
        "wacc": Decimal("0.09"),
        "terminal_growth": Decimal("0.03"),
    }
    values.update(overrides)
    return ValuationAssumptions(**values)  # type: ignore[arg-type]


class ForecastYearAssumptionTests(unittest.TestCase):
    def test_valid_rates_preserve_exact_decimals(self) -> None:
        item = forecast_year(
            1,
            revenue_growth=Decimal("-1"),
            operating_margin=Decimal("1.25"),
            forecast_tax_rate=Decimal("1"),
            d_and_a_percent_revenue=Decimal("0"),
            capex_percent_revenue=Decimal("0"),
            change_in_operating_nwc_percent_revenue=Decimal("-0.125"),
        )
        self.assertEqual(item.revenue_growth, Decimal("-1"))
        self.assertEqual(item.operating_margin, Decimal("1.25"))
        self.assertEqual(item.forecast_tax_rate, Decimal("1"))
        self.assertEqual(
            item.change_in_operating_nwc_percent_revenue, Decimal("-0.125")
        )

    def test_every_rate_rejects_invalid_numeric_types_and_nonfinite_decimals(self) -> None:
        fields = (
            "revenue_growth",
            "operating_margin",
            "forecast_tax_rate",
            "d_and_a_percent_revenue",
            "capex_percent_revenue",
            "change_in_operating_nwc_percent_revenue",
        )
        invalid = (
            True,
            1,
            0.1,
            "0.1",
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )
        for field in fields:
            for value in invalid:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(AssumptionValidationError):
                        forecast_year(1, **{field: value})

    def test_revenue_growth_domain(self) -> None:
        for value in (Decimal("0.1"), Decimal("0"), Decimal("-0.5"), Decimal("-1")):
            with self.subTest(value=value):
                self.assertEqual(forecast_year(1, revenue_growth=value).revenue_growth, value)
        with self.assertRaises(AssumptionValidationError):
            forecast_year(1, revenue_growth=Decimal("-1.0001"))

    def test_operating_margin_has_no_business_bound(self) -> None:
        for value in (Decimal("0.2"), Decimal("0"), Decimal("-0.5"), Decimal("1.2")):
            with self.subTest(value=value):
                self.assertEqual(forecast_year(1, operating_margin=value).operating_margin, value)

    def test_tax_rate_domain(self) -> None:
        for value in (Decimal("0"), Decimal("0.25"), Decimal("1")):
            self.assertEqual(forecast_year(1, forecast_tax_rate=value).forecast_tax_rate, value)
        for value in (Decimal("-0.01"), Decimal("1.01")):
            with self.assertRaises(AssumptionValidationError):
                forecast_year(1, forecast_tax_rate=value)

    def test_d_and_a_capex_and_change_in_nwc_domains(self) -> None:
        for field in ("d_and_a_percent_revenue", "capex_percent_revenue"):
            for value in (Decimal("0"), Decimal("0.1")):
                self.assertEqual(getattr(forecast_year(1, **{field: value}), field), value)
            with self.assertRaises(AssumptionValidationError):
                forecast_year(1, **{field: Decimal("-0.01")})
        for value in (Decimal("-0.1"), Decimal("0"), Decimal("0.1")):
            self.assertEqual(
                forecast_year(
                    1, change_in_operating_nwc_percent_revenue=value
                ).change_in_operating_nwc_percent_revenue,
                value,
            )

    def test_period_index_and_label_validation(self) -> None:
        for index in (0, 6, True):
            with self.assertRaises(AssumptionValidationError):
                forecast_year(index)  # type: ignore[arg-type]
        self.assertEqual(forecast_year(1).period_index, 1)
        for label in ("", "   ", 2026):
            with self.assertRaises(AssumptionValidationError):
                forecast_year(1, fiscal_year_label=label)


class ValuationAssumptionTests(unittest.TestCase):
    def test_valid_five_year_object_is_immutable_and_ordered(self) -> None:
        value = assumptions()
        self.assertEqual(tuple(item.period_index for item in value.forecast_years), (1, 2, 3, 4, 5))
        self.assertIsInstance(value.forecast_years, tuple)
        with self.assertRaises(FrozenInstanceError):
            value.wacc = Decimal("0.10")  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            value.forecast_years[0].revenue_growth = Decimal("0")  # type: ignore[misc]

    def test_forecast_year_collection_must_be_exact_ordered_tuple(self) -> None:
        years = assumptions().forecast_years
        invalid = (
            years[:4],
            (*years, replace(years[-1], period_index=5, fiscal_year_label="FY2031")),
            (years[0], years[1], years[3], years[4], years[4]),
            (years[0], years[1], years[1], years[3], years[4]),
            (years[1], years[0], *years[2:]),
            list(years),
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(AssumptionValidationError):
                    assumptions(forecast_years=value)

    def test_labels_must_be_unique(self) -> None:
        years = assumptions().forecast_years
        duplicate = (*years[:4], replace(years[4], fiscal_year_label=years[0].fiscal_year_label))
        with self.assertRaises(AssumptionValidationError):
            assumptions(forecast_years=duplicate)

    def test_wacc_and_terminal_growth_domains(self) -> None:
        for value in (Decimal("0"), Decimal("-0.01")):
            with self.assertRaises(AssumptionValidationError):
                assumptions(wacc=value, terminal_growth=Decimal("-0.5"))
        for value in (Decimal("0.03"), Decimal("0"), Decimal("-0.5")):
            self.assertEqual(assumptions(terminal_growth=value).terminal_growth, value)
        for value in (Decimal("-1"), Decimal("-1.01"), Decimal("0.09"), Decimal("0.10")):
            with self.assertRaises(AssumptionValidationError):
                assumptions(terminal_growth=value)

    def test_wacc_and_terminal_growth_reject_invalid_numeric_types(self) -> None:
        invalid = (
            True,
            1,
            0.1,
            "0.1",
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        )
        for field in ("wacc", "terminal_growth"):
            for value in invalid:
                with self.subTest(field=field, value=value):
                    with self.assertRaises(AssumptionValidationError):
                        assumptions(**{field: value})

    def test_anchor_identity_and_noncalendar_dates(self) -> None:
        for value in (0, -1, True):
            with self.assertRaises(AssumptionValidationError):
                assumptions(company_cik=value)
        self.assertEqual(assumptions(company_cik=1326801).company_cik, 1326801)
        with self.assertRaises(AssumptionValidationError):
            assumptions(anchor_accession_number="")
        with self.assertRaises(AssumptionValidationError):
            assumptions(anchor_fiscal_end=datetime(2025, 12, 31))
        for value in (
            date(2025, 12, 31),
            date(2025, 6, 30),
            date(2025, 9, 27),
            date(2025, 8, 31),
        ):
            self.assertEqual(assumptions(anchor_fiscal_end=value).anchor_fiscal_end, value)

    def test_structural_fields_require_exact_builtin_types(self) -> None:
        with self.assertRaises(AssumptionValidationError):
            forecast_year(IntSubclass(1))  # type: ignore[arg-type]
        with self.assertRaises(AssumptionValidationError):
            assumptions(company_cik=IntSubclass(1326801))
        with self.assertRaises(AssumptionValidationError):
            assumptions(forecast_years=TupleSubclass(assumptions().forecast_years))

    def test_nonempty_string_metadata_is_required_without_rewriting(self) -> None:
        for field in ("schema_version", "anchor_accession_number"):
            for value in ("", "   ", 1):
                with self.assertRaises(AssumptionValidationError):
                    assumptions(**{field: value})
        value = assumptions(schema_version=" 1 ", anchor_accession_number=" accession ")
        self.assertEqual(value.schema_version, " 1 ")
        self.assertEqual(value.anchor_accession_number, " accession ")

    def test_serializer_is_deterministic_and_uses_exact_strings(self) -> None:
        value = assumptions()
        first = valuation_assumptions_to_dict(value)
        second = valuation_assumptions_to_dict(value)
        self.assertEqual(first, second)
        self.assertEqual(first["anchor_fiscal_end"], "2025-12-31")
        self.assertEqual(first["forecast_years"][0]["revenue_growth"], "0.10")
        self.assertEqual(first["wacc"], "0.09")
        self.assertEqual(first["terminal_growth"], "0.03")
        self.assertEqual(json.loads(json.dumps(first)), first)

    def test_scope_exclusions_and_no_upstream_objects(self) -> None:
        value = assumptions()
        payload = valuation_assumptions_to_dict(value)
        self.assertFalse(hasattr(value, "historical"))
        self.assertFalse(hasattr(value, "company_facts"))
        self.assertFalse(hasattr(value, "filing"))
        forbidden = (
            "forecast_revenue",
            "ebit",
            "nopat",
            "d_and_a_amount",
            "capex_amount",
            "change_in_operating_nwc_amount",
            "fcff",
            "discount_factor",
            "terminal_value",
            "enterprise_value",
            "cash",
            "debt",
            "share_count",
            "scenario",
        )
        serialized = json.dumps(payload).lower()
        for field in forbidden:
            self.assertNotIn(f'"{field}"', serialized)

    def test_serializer_rejects_wrong_type(self) -> None:
        with self.assertRaises(AssumptionValidationError):
            valuation_assumptions_to_dict(object())  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
