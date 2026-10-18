"""Pure Stage A arithmetic. Structural validation is not semantic input review.

The six supplied rates cannot expose embedded economic overlap. This module
accepts no separate CFO, SBC, lease-principal or historical-NWC operands.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, DecimalException, ROUND_HALF_EVEN, localcontext
import json
import re

from valuation_platform.analyst.nwc import Period
from .assumptions import ValuationAssumptions, valuation_assumptions_to_dict


CONVENTION_VERSION = "meta-base-fcff-v1"
RESULT_SCHEMA = "stage-a-forecast-v1"


class ForecastValidationError(ValueError):
    """Invalid structural inputs, declared convention or numerical result."""


@dataclass(frozen=True)
class RevenueAnchor:
    """Base-USD revenue with immutable provenance, not a sufficiency certificate.

    Use consumer.prepare_meta_revenue_anchor for the accepted META boundary.
    Synthetic fixtures may construct this model with explicitly synthetic sources.
    """

    period: Period
    revenue: Decimal
    raw_value: str
    precision: str
    source_reference: str
    effective_reference: str
    approval_reference: str
    source_details_json: str
    approval_details_json: str
    unit: str = "USD"
    scale: int = 1
    sign_multiplier: int = 1

    def __post_init__(self) -> None:
        if type(self.period) is not Period:
            raise ForecastValidationError("Exact annual Period required")
        if (not isinstance(self.revenue, Decimal) or not self.revenue.is_finite()
                or self.revenue <= 0):
            raise ForecastValidationError("Positive finite revenue required")
        if (self.unit != "USD" or type(self.scale) is not int or self.scale != 1
                or type(self.sign_multiplier) is not int or self.sign_multiplier != 1):
            raise ForecastValidationError("Revenue must already be positive base USD, scale 1")
        for value in (self.raw_value, self.precision, self.source_reference,
                      self.effective_reference, self.approval_reference,
                      self.source_details_json, self.approval_details_json):
            if type(value) is not str or not value.strip():
                raise ForecastValidationError("Explicit source/approval metadata required")
        if not re.fullmatch(r"INF|-?\d+", self.precision):
            raise ForecastValidationError("Original SEC precision or synthetic equivalent required")
        try:
            with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
                raw = Decimal(self.raw_value)
                if not raw.is_finite() or raw != self.revenue:
                    raise ForecastValidationError("Raw base-USD revenue disagrees")
            for metadata in (self.source_details_json, self.approval_details_json):
                if type(json.loads(metadata)) is not dict:
                    raise ForecastValidationError("Source/approval metadata objects required")
        except (DecimalException, ValueError, TypeError) as exc:
            raise ForecastValidationError("Invalid revenue/provenance representation") from exc


@dataclass(frozen=True)
class ForecastYearResult:
    period_index: int
    fiscal_year_label: str
    revenue: Decimal
    ebit: Decimal
    tax: Decimal
    nopat: Decimal
    d_and_a: Decimal
    investment: Decimal
    working_capital_cash_requirement: Decimal
    fcff: Decimal


@dataclass(frozen=True)
class ForecastResult:
    anchor: RevenueAnchor
    assumptions: ValuationAssumptions
    convention_version: str
    years: tuple[ForecastYearResult, ...]


def _operating_year(
    period_index: int, fiscal_year_label: str, revenue: Decimal, *,
    operating_margin: Decimal, operating_tax_rate: Decimal,
    d_and_a_ratio: Decimal, investment_ratio: Decimal, working_capital_cash_ratio: Decimal,
) -> ForecastYearResult:
    """Shared approved equations; callers validate rates and supply local context."""
    ebit = revenue * operating_margin
    tax = max(ebit, Decimal(0)) * operating_tax_rate
    nopat = ebit - tax
    da = revenue * d_and_a_ratio
    investment = revenue * investment_ratio
    wc = revenue * working_capital_cash_ratio
    fcff = nopat + da - investment - wc
    if not all(v.is_finite() for v in (revenue, ebit, tax, nopat, da, investment, wc, fcff)):
        raise ForecastValidationError("Nonfinite forecast result")
    return ForecastYearResult(period_index, fiscal_year_label, revenue, ebit,
                              tax, nopat, da, investment, wc, fcff)


def forecast_five_years(
    anchor: RevenueAnchor,
    assumptions: ValuationAssumptions,
    *,
    convention_version: str = CONVENTION_VERSION,
) -> ForecastResult:
    """Calculate five periods; never infer rates or certify their economic scope.

    Under this approved convention investment includes cash PP&E plus new,
    non-overlapping finance-leased operating assets, excluding finance principal.
    Margins include SBC and operating-lease service costs. Actual input scope and
    EBIT/D&A/investment consistency require separate semantic review before use.
    WACC and terminal growth remain structurally validated but unused here.
    """
    if type(anchor) is not RevenueAnchor or type(assumptions) is not ValuationAssumptions:
        raise ForecastValidationError("RevenueAnchor and ValuationAssumptions required")
    if assumptions.schema_version != "1":
        raise ForecastValidationError("Unsupported assumption schema")
    if convention_version != CONVENTION_VERSION:
        raise ForecastValidationError("Unsupported declared forecast convention")
    if (assumptions.company_cik, assumptions.anchor_accession_number,
            assumptions.anchor_fiscal_end) != (
            anchor.period.cik, anchor.period.accession, anchor.period.annual_end):
        raise ForecastValidationError("Assumption/anchor identity mismatch")

    years = []
    # A fresh Context isolates precision, rounding, traps and flags from callers.
    try:
        with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
            revenue = anchor.revenue
            for item in assumptions.forecast_years:
                revenue = revenue * (Decimal(1) + item.revenue_growth)
                years.append(_operating_year(
                    item.period_index, item.fiscal_year_label, revenue,
                    operating_margin=item.operating_margin,
                    operating_tax_rate=item.forecast_tax_rate,
                    d_and_a_ratio=item.d_and_a_percent_revenue,
                    investment_ratio=item.capex_percent_revenue,
                    working_capital_cash_ratio=item.change_in_operating_nwc_percent_revenue,
                ))
    except DecimalException as exc:
        raise ForecastValidationError("Forecast Decimal arithmetic failed") from exc
    return ForecastResult(anchor, assumptions, convention_version, tuple(years))


def forecast_to_dict(result: ForecastResult) -> dict[str, object]:
    """Fresh JSON-ready output; exact Decimal strings, no display quantization."""
    if type(result) is not ForecastResult:
        raise ForecastValidationError("ForecastResult required")
    anchor = result.anchor
    return {
        "schema": RESULT_SCHEMA,
        "convention_version": result.convention_version,
        "numeric_policy": {"precision": 50, "rounding": "ROUND_HALF_EVEN",
                           "unit": "USD", "intermediate_quantization": False},
        "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR",
        "anchor": {
            "cik": anchor.period.cik, "accession": anchor.period.accession,
            "annual_start": anchor.period.annual_start.isoformat(),
            "annual_end": anchor.period.annual_end.isoformat(), "form": anchor.period.form,
            "revenue": str(anchor.revenue), "raw_value": anchor.raw_value,
            "unit": anchor.unit, "scale": anchor.scale,
            "sign_multiplier": anchor.sign_multiplier, "precision": anchor.precision,
            "source_reference": anchor.source_reference,
            "effective_reference": anchor.effective_reference,
            "approval_reference": anchor.approval_reference,
            "source_details": json.loads(anchor.source_details_json),
            "approval_details": json.loads(anchor.approval_details_json),
        },
        "assumptions": valuation_assumptions_to_dict(result.assumptions),
        "years": [
            {"period_index": year.period_index, "fiscal_year_label": year.fiscal_year_label,
             **{name: str(getattr(year, name)) for name in (
                 "revenue", "ebit", "tax", "nopat", "d_and_a", "investment",
                 "working_capital_cash_requirement", "fcff")}}
            for year in result.years
        ],
    }


def serialize_forecast(result: ForecastResult) -> str:
    return json.dumps(forecast_to_dict(result), sort_keys=True, separators=(",", ":"))
