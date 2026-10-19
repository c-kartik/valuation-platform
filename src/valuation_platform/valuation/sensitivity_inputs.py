"""Explicit WACC × growth grids over one complete case; no DCF formulas here."""

from dataclasses import dataclass
from datetime import date
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
import json
from pathlib import Path
import re

from .case_inputs import AnalystCase, CaseInputError, _strict_json, read_case, run_case
from .scenario_inputs import LABELS, read_scenario_set

SCHEMA = "analyst-sensitivity-request-v1"
RESULT_SCHEMA = "analyst-sensitivity-results-v1"
HELD_FIXED = (
    "All five annual operating inputs and period identities; terminal operating ratios; "
    "bridge components, shares, source bindings, dates, conventions, rationale and limitations."
)
LIMITATIONS = (
    "Only WACC and terminal growth change. Annual operating cash flows stay fixed; "
    "discount factors/PVs and terminal revenue/FCFF/value respond through the existing engine.",
    "Cutoff and input reviews are supplied declarations, not authenticated availability or approvals.",
    "Sensitivity is not probability analysis, a fair-value range or economic validation. "
    "Unbounded claims/awards omissions remain unbounded.",
)


class SensitivityInputError(CaseInputError):
    """Invalid request or failed execution; no partial successful table."""


@dataclass(frozen=True)
class SensitivityRequest:
    submitted_json: str
    sensitivity_name: str
    case: AnalystCase
    scenario_label: str | None
    analytical_date: date
    information_cutoff: date
    wacc_values: tuple[Decimal, ...]
    terminal_growth_values: tuple[Decimal, ...]


def read_sensitivity(text: str) -> SensitivityRequest:
    """Strict, calculation-free validation of the entire embedded source and axes."""
    # Decimal construction can set flags even for rejected exponent strings.
    # Isolate parsing/model validation as well as successful calculations.
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        return _read_sensitivity(text)


def _read_sensitivity(text: str) -> SensitivityRequest:
    try:
        doc = _strict_json(text)
    except CaseInputError as exc:
        raise SensitivityInputError(["sensitivity." + e for e in exc.errors]) from exc
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

    def axis(value, key):
        path = "sensitivity." + key
        if type(value) is not list or not 1 <= len(value) <= 11:
            errors.append(f"{path}: requires 1 to 11 explicit rate strings")
            return ()
        rates = []
        previous = None
        for i, raw in enumerate(value):
            field = f"{path}[{i}]"
            if type(raw) is not str or not re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", raw):
                errors.append(f'{field}: supply a finite fractional Decimal string, e.g. "0.09"')
                continue
            try:
                rate = Decimal(raw)
                if not rate.is_finite():
                    raise ValueError()
            except (ArithmeticError, ValueError):
                errors.append(f"{field}: invalid finite Decimal string")
                continue
            if key == "wacc_values" and rate <= 0:
                errors.append(f"{field}: WACC must be greater than zero")
            if key == "terminal_growth_values" and rate <= -1:
                errors.append(f"{field}: growth must be greater than -1")
            if previous is not None and rate <= previous:
                errors.append(f"{field}: axis must be strictly increasing and numerically unique")
            rates.append(rate)
            previous = rate
        return tuple(rates)

    doc = obj(doc, ("schema_version", "sensitivity_name", "source", "wacc_values", "terminal_growth_values"), "sensitivity")
    if doc.get("schema_version") != SCHEMA:
        errors.append(f"sensitivity.schema_version: requires {SCHEMA}")
    name = doc.get("sensitivity_name")
    if type(name) is not str or not name.strip():
        errors.append("sensitivity.sensitivity_name: required nonempty text")
    source = doc.get("source")
    kind = source.get("kind") if type(source) is dict else None
    names = (("kind", "case", "analytical_date", "information_cutoff") if kind == "single_case"
             else ("kind", "scenario_set", "scenario_label") if kind == "scenario_set" else ("kind",))
    source = obj(source, names, "sensitivity.source")
    case = analytical = cutoff = label = None
    if kind == "single_case":
        analytical = day(source.get("analytical_date"), "sensitivity.source.analytical_date")
        cutoff = day(source.get("information_cutoff"), "sensitivity.source.information_cutoff")
        try:
            case = read_case(json.dumps(source.get("case")))
        except CaseInputError as exc:
            errors.extend("sensitivity.source.case." + e.removeprefix("case.") for e in exc.errors)
    elif kind == "scenario_set":
        label = source.get("scenario_label")
        if type(label) is not str or label not in LABELS:
            errors.append("sensitivity.source.scenario_label: explicitly select Bear, Base or Bull")
        try:
            scenarios = read_scenario_set(json.dumps(source.get("scenario_set")))
            if type(label) is str and label in LABELS:
                selected = next(item for item in scenarios.scenarios if item.label == label)
                case, analytical, cutoff = selected.case, selected.analytical_date, selected.information_cutoff
        except CaseInputError as exc:
            errors.extend("sensitivity.source.scenario_set." + e for e in exc.errors)
    else:
        errors.append("sensitivity.source.kind: requires single_case or scenario_set")
    if analytical and cutoff and cutoff < analytical:
        errors.append("sensitivity.source.information_cutoff: must not precede analytical_date")
    if case and analytical and analytical != case.assumptions.anchor_fiscal_end:
        errors.append("sensitivity.source.analytical_date: must equal selected case.anchor.annual_end")
    waccs = axis(doc.get("wacc_values"), "wacc_values")
    growths = axis(doc.get("terminal_growth_values"), "terminal_growth_values")
    if not errors and max(waccs) <= min(growths):
        errors.append("sensitivity: all cells invalid (terminal growth >= WACC); no valuation table can be produced")
    if errors:
        raise SensitivityInputError(errors)
    return SensitivityRequest(text, name, case, label, analytical, cutoff, waccs, growths)


def load_sensitivity(path: Path) -> SensitivityRequest:
    return read_sensitivity(path.read_text(encoding="utf-8"))


def _metrics(result):
    """Project existing engine components; only the contribution is new arithmetic."""
    b = result["stage_b"]
    ev = Decimal(b["enterprise_value"])
    metrics = {key: b[key] for key in ("enterprise_value", "pv_explicit_fcff", "pv_terminal_value")}
    metrics.update(terminal_revenue=b["terminal"]["revenue"], terminal_fcff=b["terminal"]["fcff"],
                   terminal_value=b["terminal_value"],
                   terminal_contribution=None if ev.is_zero() else str(Decimal(b["pv_terminal_value"]) / ev),
                   terminal_contribution_note="undefined: EV is zero" if ev.is_zero() else
                   "Signed terminal PV / EV; negative or >100% ratios are retained (offsetting PVs); negative EV is an arithmetic ratio.",
                   equity_value=None, value_per_share=None)
    if "stage_c" in result:
        metrics.update(equity_value=result["stage_c"]["equity_value"], value_per_share=result["stage_c"]["value_per_share"])
    return metrics


def run_sensitivity(request: SensitivityRequest, repository_root: Path) -> dict[str, object]:
    """Revalidate, execute reference and each valid cell via existing run_case only."""
    if type(request) is not SensitivityRequest or read_sensitivity(request.submitted_json) != request:
        raise SensitivityInputError(["sensitivity: validated immutable SensitivityRequest required"])
    original = json.loads(request.case.submitted_json)
    try:
        reference = run_case(request.case, repository_root)
        with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
            reference_metrics = _metrics(reference)
            change_keys = ("enterprise_value",) if request.case.bridge is None else ("enterprise_value", "equity_value", "value_per_share")
            rows = []
            for i, wacc in enumerate(request.wacc_values):
                row = []
                for j, growth in enumerate(request.terminal_growth_values):
                    cell = {"wacc": str(wacc), "terminal_growth": str(growth)}
                    if growth >= wacc:
                        cell.update(status="INVALID", reason="terminal growth >= WACC", metrics={key: None for key in reference_metrics}, changes=None)
                    else:
                        # json.loads provides a fresh complete case: no nested mutation.
                        doc = json.loads(request.case.submitted_json)
                        doc.update(wacc=str(wacc), terminal_growth=str(growth))
                        try:
                            result = run_case(read_case(json.dumps(doc)), repository_root)
                        except (ValueError, OSError) as exc:
                            raise SensitivityInputError([f"sensitivity.cells[{i}][{j}]: execution failed: {exc}"]) from exc
                        metrics = _metrics(result)
                        changes = {}
                        for key in change_keys:
                            ref = Decimal(reference_metrics[key])
                            delta = Decimal(metrics[key]) - ref
                            changes[key] = {"absolute": str(delta),
                                            "fractional_change": None if ref.is_zero() else str(delta / ref),
                                            "note": "undefined: reference is zero" if ref.is_zero() else "absolute change / signed reference; fraction, not percent units"}
                        cell.update(status="VALID", reason=None, metrics=metrics, changes=changes)
                    row.append(cell)
                rows.append(row)
    except (ValueError, OSError, ArithmeticError) as exc:
        if isinstance(exc, SensitivityInputError):
            raise
        raise SensitivityInputError([f"sensitivity.reference_or_grid: execution failed: {exc}"]) from exc
    return {"schema_version": RESULT_SCHEMA, "sensitivity_name": request.sensitivity_name,
            "submitted_inputs": _strict_json(request.submitted_json), "selected_case": original,
            "selection": {"source_kind": _strict_json(request.submitted_json)["source"]["kind"],
                          "scenario_label": request.scenario_label, "analytical_date": request.analytical_date.isoformat(),
                          "information_cutoff": request.information_cutoff.isoformat()},
            "reference_result": reference, "reference_metrics": reference_metrics,
            "wacc_values": [str(x) for x in request.wacc_values],
            "terminal_growth_values": [str(x) for x in request.terminal_growth_values],
            "cells": rows, "held_fixed": HELD_FIXED,
            "cell_reproduction": "Start from selected_case; replace only wacc and terminal_growth with the cell's strings; read_case then run_case. Rows are WACC, columns terminal growth.",
            "numeric_policy": "Derived contributions/deltas: isolated Decimal precision 50, HALF_EVEN; changes are fractional; amounts base USD, shares actual, value/share USD/share.",
            "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR", "limitations": list(LIMITATIONS)}


def serialize_sensitivity(result: dict[str, object]) -> str:
    return json.dumps(result, sort_keys=True, indent=2) + "\n"
