"""Immutable, manually supplied assumptions for future valuation work."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


class AssumptionValidationError(ValueError):
    """Raised when a manual valuation assumption is structurally invalid."""


@dataclass(frozen=True)
class ForecastYearAssumptions:
    """Manual rates for one ordinal explicit forecast period."""

    period_index: int
    fiscal_year_label: str
    revenue_growth: Decimal
    operating_margin: Decimal
    forecast_tax_rate: Decimal
    d_and_a_percent_revenue: Decimal
    capex_percent_revenue: Decimal
    change_in_operating_nwc_percent_revenue: Decimal

    def __post_init__(self) -> None:
        if (
            type(self.period_index) is not int
            or self.period_index not in range(1, 6)
        ):
            raise AssumptionValidationError(
                "Forecast period index must be an integer from 1 through 5"
            )
        _require_nonempty_string(self.fiscal_year_label, "Fiscal-year label")

        _require_rate(self.revenue_growth, "Revenue growth")
        if self.revenue_growth < Decimal("-1"):
            raise AssumptionValidationError("Revenue growth must be at least -1")

        _require_rate(self.operating_margin, "Operating margin")

        _require_rate(self.forecast_tax_rate, "Forecast tax rate")
        if not Decimal("0") <= self.forecast_tax_rate <= Decimal("1"):
            raise AssumptionValidationError(
                "Forecast tax rate must be between 0 and 1"
            )

        _require_rate(self.d_and_a_percent_revenue, "D&A percent of revenue")
        if self.d_and_a_percent_revenue < Decimal("0"):
            raise AssumptionValidationError(
                "D&A percent of revenue must not be negative"
            )

        _require_rate(self.capex_percent_revenue, "Capex percent of revenue")
        if self.capex_percent_revenue < Decimal("0"):
            raise AssumptionValidationError(
                "Capex percent of revenue must not be negative"
            )

        _require_rate(
            self.change_in_operating_nwc_percent_revenue,
            "Change in Operating NWC percent of revenue",
        )


@dataclass(frozen=True)
class ValuationAssumptions:
    """One company-bound set of five explicit forecast-year assumptions."""

    schema_version: str
    company_cik: int
    anchor_accession_number: str
    anchor_fiscal_end: date
    forecast_years: tuple[ForecastYearAssumptions, ...]
    wacc: Decimal
    terminal_growth: Decimal

    def __post_init__(self) -> None:
        _require_nonempty_string(self.schema_version, "Schema version")
        if (
            type(self.company_cik) is not int
            or self.company_cik <= 0
        ):
            raise AssumptionValidationError("Company CIK must be a positive integer")
        _require_nonempty_string(
            self.anchor_accession_number, "Anchor accession number"
        )
        if type(self.anchor_fiscal_end) is not date:
            raise AssumptionValidationError("Anchor fiscal end must be an exact date")
        if type(self.forecast_years) is not tuple or not all(
            isinstance(item, ForecastYearAssumptions) for item in self.forecast_years
        ):
            raise AssumptionValidationError(
                "Forecast years must be a tuple of forecast-year assumptions"
            )
        if tuple(item.period_index for item in self.forecast_years) != (1, 2, 3, 4, 5):
            raise AssumptionValidationError(
                "Forecast years must use ordered period indices 1 through 5"
            )
        labels = tuple(item.fiscal_year_label for item in self.forecast_years)
        if len(set(labels)) != len(labels):
            raise AssumptionValidationError("Forecast fiscal-year labels must be unique")

        _require_rate(self.wacc, "WACC")
        if self.wacc <= Decimal("0"):
            raise AssumptionValidationError("WACC must be greater than zero")

        _require_rate(self.terminal_growth, "Terminal growth")
        if self.terminal_growth <= Decimal("-1"):
            raise AssumptionValidationError("Terminal growth must be greater than -1")
        if self.terminal_growth >= self.wacc:
            raise AssumptionValidationError(
                "Terminal growth must be less than WACC"
            )


def valuation_assumptions_to_dict(
    assumptions: ValuationAssumptions,
) -> dict[str, object]:
    """Serialize assumptions with stable fields and exact Decimal strings."""
    if not isinstance(assumptions, ValuationAssumptions):
        raise AssumptionValidationError(
            "Serializer requires ValuationAssumptions"
        )
    return {
        "schema_version": assumptions.schema_version,
        "company_cik": assumptions.company_cik,
        "anchor_accession_number": assumptions.anchor_accession_number,
        "anchor_fiscal_end": assumptions.anchor_fiscal_end.isoformat(),
        "forecast_years": [
            {
                "period_index": item.period_index,
                "fiscal_year_label": item.fiscal_year_label,
                "revenue_growth": str(item.revenue_growth),
                "operating_margin": str(item.operating_margin),
                "forecast_tax_rate": str(item.forecast_tax_rate),
                "d_and_a_percent_revenue": str(item.d_and_a_percent_revenue),
                "capex_percent_revenue": str(item.capex_percent_revenue),
                "change_in_operating_nwc_percent_revenue": str(
                    item.change_in_operating_nwc_percent_revenue
                ),
            }
            for item in assumptions.forecast_years
        ],
        "wacc": str(assumptions.wacc),
        "terminal_growth": str(assumptions.terminal_growth),
    }


def _require_rate(value: object, name: str) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise AssumptionValidationError(f"{name} must be a finite Decimal")


def _require_nonempty_string(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise AssumptionValidationError(f"{name} must be a nonempty string")
