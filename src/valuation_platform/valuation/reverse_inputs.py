"""Bounded constant-growth inversion; existing A/B/C own every valuation."""

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Context, Decimal, DecimalException, Inexact, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import json
from math import comb
from pathlib import Path
import re

from .case_inputs import AnalystCase, CaseInputError, _strict_json, read_case, _prepare_case_runner
from .forecast import _operating_year
from .scenario_inputs import LABELS, read_scenario_set

SCHEMA = "analyst-reverse-dcf-request-v1"
RESULT_SCHEMA = "analyst-reverse-dcf-results-v1"
INVESTOR_SCHEMA = "investor-reverse-dcf-request-v1"
INVESTOR_RESULT_SCHEMA = "investor-reverse-dcf-results-v1"
HELD_FIXED = (
    "Five annual margin/tax/D&A/investment/WC ratios, WACC, terminal growth and all "
    "terminal operating ratios, bridge/shares, dates, conventions and source metadata. "
    "Only annual revenue growth is replaced, in all five periods; revenue-dependent amounts recalculate."
)
LIMITATIONS = (
    "Conditional implied constant growth, not unique market expectations, an economic-plausibility endorsement or a price target.",
    "Uniqueness concerns the exact fixed-ratio mathematical model; the existing precision-50 forward engine verifies the numerical answer within the stated residual policy.",
    "Source/review/cutoff declarations authenticate no approvals; claims, awards and potentially unbounded omissions remain qualified.",
)


class ReverseInputError(CaseInputError):
    """Structural/execution error, distinct from a completed unsuccessful solve."""


@dataclass(frozen=True)
class SolverPolicy:
    """Technical controls, never company economics; no caller context dependency."""
    growth_tolerance: str = "1e-12"
    ev_absolute_tolerance: str = "1e-8"
    per_share_absolute_tolerance: str = "1e-10"
    relative_tolerance: str = "1e-12"
    max_iterations: int = 128
    exact_component_precision: int = 512
    certificate_decimal_extent: int = 4096

    def __post_init__(self):
        with localcontext(Context(prec=80, rounding=ROUND_HALF_EVEN)):
            try:
                for name in ("growth_tolerance", "ev_absolute_tolerance", "per_share_absolute_tolerance", "relative_tolerance"):
                    raw = getattr(self, name)
                    if type(raw) is not str or not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", raw):
                        raise ValueError("Technical tolerances require finite positive Decimal strings")
                    value = Decimal(raw)
                    if not value.is_finite() or not 0 < value < 1:
                        raise ValueError("Technical tolerances must be between zero and one")
                if type(self.max_iterations) is not int or not 1 <= self.max_iterations <= 256:
                    raise ValueError("Technical max_iterations must be 1..256")
                if (type(self.exact_component_precision) is not int or self.exact_component_precision != 512
                        or type(self.certificate_decimal_extent) is not int or self.certificate_decimal_extent != 4096):
                    raise ValueError("Exact certification limits are fixed in bounded-bisection-v1")
            except DecimalException as exc:
                raise ValueError("Invalid technical Decimal tolerance") from exc


DEFAULT_POLICY = SolverPolicy()


@dataclass(frozen=True)
class ReverseRequest:
    submitted_json: str
    reverse_dcf_name: str
    case: AnalystCase
    scenario_label: str | None
    analytical_date: date
    information_cutoff: date
    target_metric: str
    target_amount: Decimal
    lower_growth: Decimal
    upper_growth: Decimal


def read_reverse(text: str) -> ReverseRequest:
    """Strict structural/model validation only: no valuation, certificate or solve."""
    with localcontext(Context(prec=80, rounding=ROUND_HALF_EVEN)):
        return _read_reverse(text)


def _read_reverse(text):
    try:
        doc = _strict_json(text)
    except CaseInputError as exc:
        raise ReverseInputError(["reverse." + error for error in exc.errors]) from exc
    errors = []

    def obj(value, names, path):
        if type(value) is not dict:
            errors.append(f"{path}: required object")
            return {}
        for key in names:
            if key not in value:
                errors.append(f"{path}.{key}: missing required field")
        for key in sorted(value.keys() - set(names)):
            errors.append(f"{path}.{key}: unknown field")
        return value

    def day(value, path):
        try:
            if type(value) is not str:
                raise ValueError()
            result = date.fromisoformat(value)
            if result.isoformat() != value:
                raise ValueError()
            return result
        except ValueError:
            errors.append(f"{path}: supply YYYY-MM-DD")
            return None

    def number(value, path):
        try:
            if type(value) is not str or not re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", value):
                raise ValueError()
            result = Decimal(value)
            if not result.is_finite():
                raise ValueError()
            return result
        except (ValueError, ArithmeticError):
            errors.append(f"{path}: supply a finite Decimal string; rates are fractions, not percentages")
            return None

    doc = obj(doc, ("schema_version", "reverse_dcf_name", "source", "target", "growth_bounds"), "reverse")
    if doc.get("schema_version") not in (SCHEMA, INVESTOR_SCHEMA):
        errors.append(f"reverse.schema_version: requires {SCHEMA} or {INVESTOR_SCHEMA}")
    name = doc.get("reverse_dcf_name")
    if type(name) is not str or not name.strip():
        errors.append("reverse.reverse_dcf_name: required nonempty text")
    source = doc.get("source")
    kind = source.get("kind") if type(source) is dict else None
    names = (("kind", "case", "analytical_date", "information_cutoff") if kind == "single_case" else
             ("kind", "scenario_set", "scenario_label") if kind == "scenario_set" else ("kind",))
    source = obj(source, names, "reverse.source")
    case = analytical = cutoff = label = None
    if kind == "single_case":
        analytical = day(source.get("analytical_date"), "reverse.source.analytical_date")
        cutoff = day(source.get("information_cutoff"), "reverse.source.information_cutoff")
        try:
            case = read_case(json.dumps(source.get("case")))
        except CaseInputError as exc:
            errors.extend("reverse.source.case." + e.removeprefix("case.") for e in exc.errors)
    elif kind == "scenario_set":
        label = source.get("scenario_label")
        if type(label) is not str or label not in LABELS:
            errors.append("reverse.source.scenario_label: explicitly select Bear, Base or Bull")
        try:
            scenarios = read_scenario_set(json.dumps(source.get("scenario_set")))
            if type(label) is str and label in LABELS:
                selected = next(x for x in scenarios.scenarios if x.label == label)
                case, analytical, cutoff = selected.case, selected.analytical_date, selected.information_cutoff
        except CaseInputError as exc:
            errors.extend("reverse.source.scenario_set." + e for e in exc.errors)
    else:
        errors.append("reverse.source.kind: requires single_case or scenario_set")
    if case and doc.get("schema_version") == INVESTOR_SCHEMA and json.loads(case.submitted_json).get("schema_version") not in ("investor-case-v1", "investor-case-v2"):
        errors.append("reverse.source.case.schema_version: investor envelope requires investor case metadata")
    if case and analytical and analytical != case.assumptions.anchor_fiscal_end:
        errors.append("reverse.source.analytical_date: must equal selected case.anchor.annual_end")
    if analytical and cutoff and cutoff < analytical:
        errors.append("reverse.source.information_cutoff: must not precede analytical_date")
    target = obj(doc.get("target"), ("metric", "amount", "unit", "date"), "reverse.target")
    metric = target.get("metric")
    unit = {"ENTERPRISE_VALUE": "USD", "VALUE_PER_SHARE": "USD/share"}.get(metric) if type(metric) is str else None
    if unit is None:
        errors.append("reverse.target.metric: requires ENTERPRISE_VALUE or VALUE_PER_SHARE")
    elif target.get("unit") != unit:
        errors.append(f"reverse.target.unit: {metric} requires {unit} at scale 1")
    target_date = day(target.get("date"), "reverse.target.date")
    if analytical and target_date and target_date != analytical:
        errors.append("reverse.target.date: must equal analytical_date; no current-price conversion")
    amount = number(target.get("amount"), "reverse.target.amount")
    if metric == "VALUE_PER_SHARE" and case and case.bridge is None:
        errors.append("reverse.target.metric: VALUE_PER_SHARE requires a complete equity/share case")
    bounds = obj(doc.get("growth_bounds"), ("lower", "upper"), "reverse.growth_bounds")
    lo = number(bounds.get("lower"), "reverse.growth_bounds.lower")
    hi = number(bounds.get("upper"), "reverse.growth_bounds.upper")
    for value, field in ((lo, "lower"), (hi, "upper")):
        if value is not None and value < -1:
            errors.append(f"reverse.growth_bounds.{field}: annual growth must be >= -1")
    if lo is not None and hi is not None and lo >= hi:
        errors.append("reverse.growth_bounds: lower must be strictly below upper")
    if errors:
        raise ReverseInputError(errors)
    return ReverseRequest(text, name, case, label, analytical, cutoff, metric, amount, lo, hi)


def load_reverse(path: Path) -> ReverseRequest:
    return read_reverse(path.read_text(encoding="utf-8"))


def _rational(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _certificate(request, reference, policy):
    """Exact mathematical representation, used ONLY for proof, never valuation output.

    Shared _operating_year runs at fixed revenue with Inexact trapped. Financial
    equations are not copied here. Timing/exponents come from Stage B. The degree-5
    polynomial is a homogeneity derivation of those shared components, not sampled
    interpolation. Bridge constants come from existing signed contributions.
    """
    doc = json.loads(request.case.submitted_json)
    decimals = [request.lower_growth, request.upper_growth, request.target_amount,
                *[getattr(y, field) for y in request.case.assumptions.forecast_years
                  for field in ("operating_margin", "forecast_tax_rate", "d_and_a_percent_revenue", "capex_percent_revenue", "change_in_operating_nwc_percent_revenue")]]
    # Reject extreme coefficient sizes conservatively, without huge integer powers.
    decimals += [Decimal(reference["stage_b"]["stage_a"]["anchor"]["revenue"]), request.case.assumptions.wacc,
                 request.case.assumptions.terminal_growth, *[Decimal(doc["terminal"][k]) for k in doc["terminal"]]]
    if request.case.bridge:
        decimals += [request.case.bridge.shares.shares, *[c.amount for c in request.case.bridge.components]]
    if any(len(x.as_tuple().digits) + abs(x.as_tuple().exponent) > policy.certificate_decimal_extent for x in decimals):
        return None, {"direction": "UNSUPPORTED", "reason": "Exact certificate decimal extent exceeds technical limit; no claim of multiple roots."}
    try:
        with localcontext(Context(prec=policy.exact_component_precision, rounding=ROUND_HALF_EVEN)) as context:
            context.traps[Inexact] = True
            seed = Decimal(reference["stage_b"]["stage_a"]["anchor"]["revenue"])
            fixed = []
            for y in request.case.assumptions.forecast_years:
                fixed.append(_operating_year(y.period_index, y.fiscal_year_label, seed,
                    operating_margin=y.operating_margin, operating_tax_rate=y.forecast_tax_rate,
                    d_and_a_ratio=y.d_and_a_percent_revenue, investment_ratio=y.capex_percent_revenue,
                    working_capital_cash_ratio=y.change_in_operating_nwc_percent_revenue).fcff)
            t = request.case.terminal
            terminal = _operating_year(6, "Terminal year", seed * (1 + request.case.assumptions.terminal_growth),
                operating_margin=t.operating_margin, operating_tax_rate=t.operating_tax_rate,
                d_and_a_ratio=t.d_and_a_percent_revenue, investment_ratio=t.investment_percent_revenue,
                working_capital_cash_ratio=t.working_capital_cash_requirement_percent_revenue).fcff
    except (ArithmeticError, ValueError):
        return None, {"direction": "UNSUPPORTED", "reason": "Shared operating components could not be established exactly within precision cap; no claim of multiple roots."}
    timing = reference["stage_b"]["timing"]
    if timing["annual_discount_exponents"] != [1, 2, 3, 4, 5] or timing["terminal_value_discount_exponent"] != 5:
        return None, {"direction": "UNSUPPORTED", "reason": "Unsupported engine timing for degree-five certificate."}
    w, g = Fraction(request.case.assumptions.wacc), Fraction(request.case.assumptions.terminal_growth)
    coefficients = [Fraction(0)] + [Fraction(v) / (1 + w) ** i for i, v in zip(timing["annual_discount_exponents"], fixed)]
    coefficients[5] += Fraction(terminal) / (w - g) / (1 + w) ** timing["terminal_value_discount_exponent"]
    if request.target_metric == "VALUE_PER_SHARE":
        c = reference["stage_c"]
        coefficients[0] = sum((Fraction(x["signed_contribution"]) for x in c["contributions"]), Fraction(0))
        shares = Fraction(c["valuation_shares"])
        coefficients = [value / shares for value in coefficients]
    # Derivative power coefficients → Bernstein basis on x = a + (b-a)t, t∈[0,1].
    derivative = [i * coefficients[i] for i in range(1, 6)]
    a, b = 1 + Fraction(request.lower_growth), 1 + Fraction(request.upper_growth)
    powers = [sum((derivative[j] * comb(j, k) * a ** (j-k) * (b-a) ** k for j in range(k, 5)), Fraction(0)) for k in range(5)]
    bernstein = [sum((powers[j] * Fraction(comb(k, j), comb(4, j)) for j in range(k+1)), Fraction(0)) for k in range(5)]
    lower, upper = min(bernstein), max(bernstein)
    direction = ("FLAT" if all(v == 0 for v in bernstein) else
                 "INCREASING" if lower >= 0 else "DECREASING" if upper <= 0 else "NOT_CERTIFIED")
    evidence = {"method": "exact-rational-bernstein-derivative-v1", "direction": direction,
                "variable": "x = 1 + constant annual growth", "x_interval": [_rational(a), _rational(b)],
                "polynomial_coefficients_ascending": [_rational(v) for v in coefficients],
                "derivative_bernstein_coefficients": [_rational(v) for v in bernstein],
                "derivative_enclosure": [_rational(lower), _rational(upper)],
                "reason": ("All derivative Bernstein coefficients share a weak sign, at least one strict: derivative has that strict sign throughout the open interval, hence strict monotonicity including endpoints."
                           if direction in ("INCREASING", "DECREASING") else
                           "Exact derivative is identically zero: no unique solution." if direction == "FLAT" else
                           "Derivative enclosure straddles zero. Uniqueness is unsupported; multiple roots are not proven. No sampled-monotonicity fallback."),
                "component_source": "Shared _operating_year at fixed anchor revenue with Inexact trapped; exact rational discount/timing homogeneity and engine signed bridge components. Proof only; every reported valuation uses run_case."}
    return coefficients, evidence


def _proof_residual(coefficients, growth, target):
    """Exact endpoint/bracket existence check; never the solver's valuation oracle."""
    x = 1 + Fraction(growth)
    return sum((value * x ** i for i, value in enumerate(coefficients)), Fraction(0)) - Fraction(target)


def run_reverse(request: ReverseRequest, repository_root: Path, *, policy: SolverPolicy = DEFAULT_POLICY) -> dict[str, object]:
    if type(request) is not ReverseRequest or read_reverse(request.submitted_json) != request:
        raise ReverseInputError(["reverse: validated immutable ReverseRequest required"])
    if type(policy) is not SolverPolicy:
        raise ReverseInputError(["reverse: explicit SolverPolicy required"])
    with localcontext(Context(prec=80, rounding=ROUND_HALF_EVEN)):
        policy.__post_init__()
        return _run_reverse(request, repository_root, policy)


def _run_reverse(request, root, policy):
    evaluations = 0
    original = json.loads(request.case.submitted_json)
    try:
        execute = _prepare_case_runner(request.case, root)
        reference = execute(request.case)
        evaluations += 1
        coefficients, evidence = _certificate(request, reference, policy)
        result = {"schema_version": INVESTOR_RESULT_SCHEMA if json.loads(request.submitted_json)["schema_version"] == INVESTOR_SCHEMA else RESULT_SCHEMA, "reverse_dcf_name": request.reverse_dcf_name,
                  "submitted_inputs": _strict_json(request.submitted_json), "selected_case": original,
                  "selection": {"scenario_label": request.scenario_label, "analytical_date": request.analytical_date.isoformat(), "information_cutoff": request.information_cutoff.isoformat()},
                  "original_growth_path": [y["revenue_growth"] for y in original["forecast_years"]],
                  "reference_result": reference, "held_fixed": HELD_FIXED,
                  "numerical_policy": {"version": "bounded-bisection-v1", **asdict(policy), "solver_precision": 80,
                                       "forward_precision": 50, "rounding": "ROUND_HALF_EVEN",
                                       "residual_test": "absolute <= unit_absolute_tolerance + relative_tolerance * max(abs(target), abs(achieved))"},
                  "monotonicity": evidence, "iterations": 0, "evaluations": evaluations,
                  "status": None, "reason": None, "solution": None, "final_bracket": None,
                  "limitations": list(LIMITATIONS), "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR"}

        def finish(status, reason, bracket=None, solution=None):
            result.update(status=status, reason=reason, evaluations=evaluations, final_bracket=bracket, solution=solution)
            return result

        if evidence["direction"] == "FLAT":
            return finish("FLAT_RESPONSE", evidence["reason"])
        if evidence["direction"] not in ("INCREASING", "DECREASING"):
            return finish("UNIQUENESS_NOT_CERTIFIED", evidence["reason"])
        target = request.target_amount
        atol = Decimal(policy.ev_absolute_tolerance if request.target_metric == "ENTERPRISE_VALUE" else policy.per_share_absolute_tolerance)
        rtol, gtol = Decimal(policy.relative_tolerance), Decimal(policy.growth_tolerance)

        def evaluate(growth):
            nonlocal evaluations
            doc = json.loads(request.case.submitted_json)
            for y in doc["forecast_years"]:
                y["revenue_growth"] = str(growth)
            forward = execute(read_case(json.dumps(doc)))
            evaluations += 1
            value = Decimal(forward["stage_b"]["enterprise_value"] if request.target_metric == "ENTERPRISE_VALUE" else forward["stage_c"]["value_per_share"])
            return value, forward

        def bracket_info(lo, hi, lv, hv):
            return {"lower_growth": str(lo), "upper_growth": str(hi), "width": str(hi-lo),
                    "lower_achieved_metric": str(lv), "upper_achieved_metric": str(hv)}

        def verified(growth, lo, hi, lv, hv, endpoint=False):
            # Fresh forward evaluation: no reused midpoint valuation is accepted.
            achieved, forward = evaluate(growth)
            residual = achieved-target
            tolerance = atol + rtol * max(abs(target), abs(achieved))
            left, right = _proof_residual(coefficients, lo, target), _proof_residual(coefficients, hi, target)
            exists = min(left, right) <= 0 <= max(left, right)
            if not exists or abs(residual) > tolerance or (not endpoint and hi-lo > gtol):
                return finish("NUMERICAL_VERIFICATION_FAILED", "Fresh residual, exact final-bracket existence or growth-width check failed; no solution exposed.", bracket_info(lo, hi, lv, hv))
            return finish("SUCCESS", "Unique mathematical solution certified; fresh existing-engine valuation meets residual and growth-bracket policy.",
                          bracket_info(lo, hi, lv, hv), {"constant_annual_growth": str(growth), "achieved_metric": str(achieved),
                          "signed_residual": str(residual), "absolute_residual": str(abs(residual)), "residual_tolerance": str(tolerance),
                          "exact_endpoint": endpoint, "forward_result": forward})

        lo, hi = request.lower_growth, request.upper_growth
        lv, _ = evaluate(lo)
        hv, _ = evaluate(hi)
        left, right = _proof_residual(coefficients, lo, target), _proof_residual(coefficients, hi, target)
        if left == 0:
            return verified(lo, lo, lo, lv, lv, True)
        if right == 0:
            return verified(hi, hi, hi, hv, hv, True)
        if min(left, right) > 0 or max(left, right) < 0:
            return finish("UNREACHABLE_TARGET", "Certified monotone mathematical endpoint values do not bracket the target; no nearest-bound solution.", bracket_info(lo, hi, lv, hv))
        increasing = evidence["direction"] == "INCREASING"
        for iteration in range(1, policy.max_iterations+1):
            result["iterations"] = iteration
            mid = (lo+hi)/2
            if mid == lo or mid == hi:
                return finish("NUMERICAL_VERIFICATION_FAILED", "Solver precision cannot shrink growth bracket further.", bracket_info(lo, hi, lv, hv))
            mv, _ = evaluate(mid)
            if hi-lo <= gtol and abs(mv-target) <= atol + rtol * max(abs(target), abs(mv)):
                return verified(mid, lo, hi, lv, hv)
            if mv == target:
                # Rounded equality is not an exact endpoint proof. Build a small
                # surrounding bracket, then certify its existence and re-evaluate.
                lo, hi = max(lo, mid-gtol/4), min(hi, mid+gtol/4)
                lv, _ = evaluate(lo)
                hv, _ = evaluate(hi)
                return verified(mid, lo, hi, lv, hv)
            if (mv < target) == increasing:
                lo, lv = mid, mv
            else:
                hi, hv = mid, mv
        return finish("ITERATION_LIMIT", "Iteration limit reached before both acceptance tests; no approximate solution exposed.", bracket_info(lo, hi, lv, hv))
    except (ValueError, OSError, ArithmeticError) as exc:
        raise ReverseInputError([f"reverse.run: execution failed: {exc}"]) from exc


def serialize_reverse(result: dict[str, object]) -> str:
    return json.dumps(result, sort_keys=True, indent=2) + "\n"
