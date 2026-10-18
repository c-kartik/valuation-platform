"""Stage B: annual fiscal-end analytical discounting and explicit terminal inputs.

No market data, equity bridge or economic-sustainability certification. The
analytical t=0 is the anchor fiscal end using later-filed information, not a
contemporaneous historical-information backtest or current market-date value.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import date
from decimal import Context, Decimal, DecimalException, ROUND_HALF_EVEN, localcontext
import json

from .assumptions import (
    AssumptionValidationError, ForecastYearAssumptions, ValuationAssumptions, _require_rate,
)
from .forecast import (
    CONVENTION_VERSION, SUPPORTED_CONVENTIONS, ForecastResult, ForecastValidationError, ForecastYearResult,
    RevenueAnchor, _operating_year, forecast_five_years, forecast_to_dict,
)


DISCOUNTING_CONVENTION_VERSION = "fiscal-end-annual-gordon-v1"
RESULT_SCHEMA = "stage-b-enterprise-value-v1"
TIMING_NOTICE = (
    "Analytical t=0 at the anchor fiscal end using later-filed information; "
    "not a contemporaneous historical-information backtest or a current market-date valuation."
)


class DiscountingValidationError(ForecastValidationError):
    """Invalid Stage A structure, terminal inputs, convention or arithmetic."""


@dataclass(frozen=True)
class TerminalAssumptions:
    """Explicit sustainable ratios under Stage A economics, never Year 5 defaults.

    WACC/g belong only to ValuationAssumptions. These rates cannot prove support
    for replacement/growth investment or perpetually sustainable WC cash needs.
    """

    operating_margin: Decimal
    operating_tax_rate: Decimal
    d_and_a_percent_revenue: Decimal
    investment_percent_revenue: Decimal
    working_capital_cash_requirement_percent_revenue: Decimal
    convention_version: str = CONVENTION_VERSION

    def __post_init__(self) -> None:
        for name in ("operating_margin", "operating_tax_rate", "d_and_a_percent_revenue",
                     "investment_percent_revenue", "working_capital_cash_requirement_percent_revenue"):
            _require_rate(getattr(self, name), "Terminal " + name)
        if not Decimal(0) <= self.operating_tax_rate <= Decimal(1):
            raise AssumptionValidationError("Terminal operating tax rate must be between 0 and 1", "operating_tax_rate")
        for name in ("d_and_a_percent_revenue", "investment_percent_revenue"):
            if getattr(self, name) < 0:
                raise AssumptionValidationError("Terminal D&A/investment ratios must not be negative", name)
        if self.convention_version not in SUPPORTED_CONVENTIONS:
            raise AssumptionValidationError("Unsupported declared terminal economic convention")


@dataclass(frozen=True)
class DiscountedYearResult:
    period_index: int
    fiscal_year_label: str
    fcff: Decimal
    discount_factor: Decimal
    pv_fcff: Decimal


@dataclass(frozen=True)
class EnterpriseValueResult:
    stage_a: ForecastResult
    terminal_assumptions: TerminalAssumptions
    convention_version: str
    years: tuple[DiscountedYearResult, ...]
    terminal: ForecastYearResult
    terminal_value: Decimal
    pv_terminal_value: Decimal
    pv_explicit_fcff: Decimal
    enterprise_value: Decimal

    @property
    def analytical_date(self) -> date:
        return self.stage_a.anchor.period.annual_end


def _validate_stage_a(stage_a: ForecastResult) -> None:
    """Narrow handoff check: frozen dataclasses have public unchecked constructors."""
    if (type(stage_a) is not ForecastResult or type(stage_a.anchor) is not RevenueAnchor
            or type(stage_a.assumptions) is not ValuationAssumptions
            or type(stage_a.years) is not tuple or len(stage_a.years) != 5):
        raise DiscountingValidationError("Complete immutable Stage A result required")
    # Revalidate nested models too: a frozen shell alone does not validate data.
    stage_a.anchor.period.__post_init__()
    stage_a.anchor.__post_init__()
    stage_a.assumptions.__post_init__()
    for item in stage_a.assumptions.forecast_years:
        if type(item) is not ForecastYearAssumptions:
            raise DiscountingValidationError("Exact forecast-year assumptions required")
        item.__post_init__()
    for year in stage_a.years:
        if type(year) is not ForecastYearResult or type(year.period_index) is not int:
            raise DiscountingValidationError("Exact ordered Stage A annual results required")
        for field in fields(year):
            if field.name not in ("period_index", "fiscal_year_label"):
                value = getattr(year, field.name)
                if not isinstance(value, Decimal) or not value.is_finite():
                    raise DiscountingValidationError("Finite Decimal Stage A components required")
    expected = forecast_five_years(stage_a.anchor, stage_a.assumptions,
                                  convention_version=stage_a.convention_version)
    if stage_a != expected:
        raise DiscountingValidationError("Stage A components/order/labels disagree with supplied assumptions")


def discount_to_enterprise_value(
    stage_a: ForecastResult,
    terminal: TerminalAssumptions,
    *,
    convention_version: str = DISCOUNTING_CONVENTION_VERSION,
) -> EnterpriseValueResult:
    """Discount years 1–5 and explicit terminal FCFF; preserve negative results.

    Only integer end-year exponents are supported. Structural checks/recomputation
    do not authenticate historical evidence or approve actual forecast inputs.
    """
    if convention_version != DISCOUNTING_CONVENTION_VERSION:
        raise DiscountingValidationError("Unsupported analytical discounting convention")
    if type(terminal) is not TerminalAssumptions:
        raise DiscountingValidationError("Explicit TerminalAssumptions required")
    try:
        with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
            _validate_stage_a(stage_a)
            terminal.__post_init__()
            wacc = stage_a.assumptions.wacc
            growth = stage_a.assumptions.terminal_growth
            base = Decimal(1) + wacc
            discounted = []
            for year in stage_a.years:
                factor = Decimal(1) / base ** year.period_index
                discounted.append(DiscountedYearResult(
                    year.period_index, year.fiscal_year_label, year.fcff, factor, year.fcff * factor,
                ))
            years = tuple(discounted)
            terminal_year = _operating_year(
                6, "Terminal year", stage_a.years[-1].revenue * (Decimal(1) + growth),
                operating_margin=terminal.operating_margin,
                operating_tax_rate=terminal.operating_tax_rate,
                d_and_a_ratio=terminal.d_and_a_percent_revenue,
                investment_ratio=terminal.investment_percent_revenue,
                working_capital_cash_ratio=terminal.working_capital_cash_requirement_percent_revenue,
            )
            terminal_value = terminal_year.fcff / (wacc - growth)
            pv_terminal = terminal_value / base ** 5
            pv_explicit = sum((year.pv_fcff for year in years), Decimal(0))
            ev = pv_explicit + pv_terminal
            if not all(value.is_finite() for value in (
                terminal_value, pv_terminal, pv_explicit, ev,
                *(y.discount_factor for y in years), *(y.pv_fcff for y in years),
            )):
                raise DiscountingValidationError("Nonfinite discounted result")
            return EnterpriseValueResult(stage_a, terminal, convention_version, years,
                                         terminal_year, terminal_value, pv_terminal, pv_explicit, ev)
    except DiscountingValidationError:
        raise
    except (ValueError, TypeError, AttributeError, DecimalException) as exc:
        raise DiscountingValidationError("Invalid Stage A/terminal inputs or Decimal arithmetic") from exc


def enterprise_value_to_dict(result: EnterpriseValueResult) -> dict[str, object]:
    """Retain the complete Stage A serialization, including all source dates."""
    if type(result) is not EnterpriseValueResult:
        raise DiscountingValidationError("EnterpriseValueResult required")
    terminal = result.terminal
    return {
        "schema": RESULT_SCHEMA,
        "convention_version": result.convention_version,
        "numeric_policy": {"precision": 50, "rounding": "ROUND_HALF_EVEN",
                           "unit": "USD", "intermediate_quantization": False},
        "timing": {"analytical_t0": result.analytical_date.isoformat(),
                   "basis": "anchor_fiscal_end_analytical", "annual_discount_exponents": [1, 2, 3, 4, 5],
                   "terminal_value_discount_exponent": 5,
                   "information_cutoff": "NOT_ESTABLISHED_BY_CALCULATOR", "notice": TIMING_NOTICE},
        "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR",
        "stage_a": forecast_to_dict(result.stage_a),
        "terminal_assumptions": {
            field.name: (str(getattr(result.terminal_assumptions, field.name))
                         if field.name != "convention_version" else result.terminal_assumptions.convention_version)
            for field in fields(result.terminal_assumptions)
        },
        "years": [{"period_index": year.period_index, "fiscal_year_label": year.fiscal_year_label,
                   "fcff": str(year.fcff), "discount_factor": str(year.discount_factor),
                   "pv_fcff": str(year.pv_fcff)} for year in result.years],
        "terminal": {field.name: (str(getattr(terminal, field.name))
                                  if isinstance(getattr(terminal, field.name), Decimal)
                                  else getattr(terminal, field.name)) for field in fields(terminal)},
        "terminal_value": str(result.terminal_value), "pv_terminal_value": str(result.pv_terminal_value),
        "pv_explicit_fcff": str(result.pv_explicit_fcff), "enterprise_value": str(result.enterprise_value),
    }


def serialize_enterprise_value(result: EnterpriseValueResult) -> str:
    return json.dumps(enterprise_value_to_dict(result), sort_keys=True, separators=(",", ":"))
