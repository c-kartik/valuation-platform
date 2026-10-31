"""Explicit terminal methods. No market selection, normalization or new EBIT scope."""
from dataclasses import dataclass, replace
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext

from .assumptions import OperatingAssumptions, ValuationAssumptions, AssumptionValidationError
from .discounting import (
    DiscountedYearResult, DiscountingValidationError, EnterpriseValueResult,
    TerminalAssumptions, TIMING_NOTICE, _validate_stage_a, _discount_years,
    discount_to_enterprise_value,
)
from .forecast import ForecastResult, forecast_to_dict

EXIT_CONVENTION = "fiscal-end-year-five-ev-ebit-v1"
EXTENDED_EXIT_CONVENTION = "fiscal-end-terminal-ev-ebit-v2"


@dataclass(frozen=True)
class PerpetualGrowthMethod:
    terminal_growth: Decimal
    terminal: TerminalAssumptions


@dataclass(frozen=True)
class ExitMultipleMethod:
    exit_ev_ebit_multiple: Decimal

    def __post_init__(self):
        v = self.exit_ev_ebit_multiple
        if type(v) is not Decimal or not v.is_finite() or v <= 0:
            raise AssumptionValidationError("Final-year EV/EBIT must be a finite strictly positive Decimal", "exit_ev_ebit_multiple")


@dataclass(frozen=True)
class ExitEnterpriseValueResult:
    stage_a: ForecastResult
    terminal_assumptions: ExitMultipleMethod
    convention_version: str
    years: tuple[DiscountedYearResult, ...]
    terminal_value: Decimal
    pv_terminal_value: Decimal
    pv_explicit_fcff: Decimal
    enterprise_value: Decimal

    @property
    def analytical_date(self):
        return self.stage_a.anchor.period.annual_end


def with_growth(stage_a, growth):
    a = stage_a.assumptions
    assumptions = ValuationAssumptions(a.schema_version, a.company_cik, a.anchor_accession_number,
        a.anchor_fiscal_end, a.forecast_years, a.wacc, growth)
    return replace(stage_a, assumptions=assumptions)


def value_terminal(stage_a: ForecastResult, method: PerpetualGrowthMethod | ExitMultipleMethod) -> EnterpriseValueResult | ExitEnterpriseValueResult:
    """Same Stage A and annual PVs. A different method never changes operations."""
    if type(method) is PerpetualGrowthMethod:
        return discount_to_enterprise_value(with_growth(stage_a, method.terminal_growth), method.terminal)
    if type(method) is not ExitMultipleMethod:
        raise DiscountingValidationError("Unsupported terminal method")
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        a = stage_a.assumptions
        if type(a) is ValuationAssumptions:
            stage_a = replace(stage_a, assumptions=OperatingAssumptions(
                a.schema_version, a.company_cik, a.anchor_accession_number,
                a.anchor_fiscal_end, a.forecast_years, a.wacc))
        _validate_stage_a(stage_a)
        method.__post_init__()
        if stage_a.years[-1].ebit <= 0:
            raise DiscountingValidationError(f"exit_ev_ebit_multiple: exit multiple unsupported: year-{len(stage_a.years)} EBIT must be strictly positive")
        years = _discount_years(stage_a)
        tv = stage_a.years[-1].ebit * method.exit_ev_ebit_multiple
        pv = tv / (Decimal(1) + stage_a.assumptions.wacc) ** len(stage_a.years)
        explicit = sum((y.pv_fcff for y in years), Decimal(0))
        if not all(v.is_finite() for v in (tv, pv, explicit, explicit + pv)):
            raise DiscountingValidationError("Nonfinite exit terminal result")
        return ExitEnterpriseValueResult(stage_a, method, EXIT_CONVENTION if len(years) == 5 else EXTENDED_EXIT_CONVENTION, years, tv, pv, explicit, explicit + pv)


def exit_to_dict(result):
    if type(result) is not ExitEnterpriseValueResult:
        raise DiscountingValidationError("ExitEnterpriseValueResult required")
    return {
        "schema": "stage-b-exit-enterprise-value-v1", "convention_version": result.convention_version,
        "terminal_method": "exit_multiple",
        "numeric_policy": {"precision": 50, "rounding": "ROUND_HALF_EVEN", "unit": "USD", "intermediate_quantization": False},
        "timing": {"analytical_t0": result.analytical_date.isoformat(), "basis": "anchor_fiscal_end_analytical",
            "annual_discount_exponents": list(range(1, len(result.years) + 1)), "terminal_value_discount_exponent": len(result.years),
            "information_cutoff": "NOT_ESTABLISHED_BY_CALCULATOR", "notice": TIMING_NOTICE},
        "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR", "stage_a": forecast_to_dict(result.stage_a),
        "terminal_basis": {"metric": "EBIT", "definition": "Operating profit including SBC and operating-lease service costs; no earnings add-backs",
            "period_index": len(result.years), "fiscal_year_label": result.stage_a.years[-1].fiscal_year_label,
            **{("year_five_ebit" if len(result.years) == 5 else "final_year_ebit"): str(result.stage_a.years[-1].ebit)}, "wacc": str(result.stage_a.assumptions.wacc),
            "exit_ev_ebit_multiple": str(result.terminal_assumptions.exit_ev_ebit_multiple)},
        "years": [dict(period_index=y.period_index, fiscal_year_label=y.fiscal_year_label,
            fcff=str(y.fcff), discount_factor=str(y.discount_factor), pv_fcff=str(y.pv_fcff)) for y in result.years],
        **{k: str(getattr(result,k)) for k in ("terminal_value","pv_terminal_value","pv_explicit_fcff","enterprise_value")},
    }


def implied_multiple(result):
    """Exact cross-check only, never a suggested or automatically selected input."""
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        if result.terminal_value <= 0 or result.stage_a.years[-1].ebit <= 0:
            return {"value": None, "reason": "Positive terminal value and final-year EBIT required"}
        return {"value": str(result.terminal_value / result.stage_a.years[-1].ebit), "reason": None}
