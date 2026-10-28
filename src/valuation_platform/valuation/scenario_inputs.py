"""Three complete editable cases; comparability/orchestration, no new formulas."""

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path

from .case_inputs import AnalystCase, CaseInputError, _strict_json, read_case, run_case


SCENARIO_SCHEMA = "analyst-scenario-set-v1"
RESULT_SCHEMA = "analyst-scenario-results-v1"
INVESTOR_SCHEMA = "investor-scenario-set-v1"
INVESTOR_RESULT_SCHEMA = "investor-scenario-results-v1"
LABELS = ("Bear", "Base", "Bull")


class ScenarioInputError(CaseInputError):
    """A complete scenario set failed validation; no partial execution allowed."""


@dataclass(frozen=True)
class ScenarioCase:
    label: str
    analytical_date: date
    information_cutoff: date
    case: AnalystCase


@dataclass(frozen=True)
class ScenarioSet:
    submitted_json: str
    scenario_set_name: str
    scenarios: tuple[ScenarioCase, ...]


def read_scenario_set(text: str) -> ScenarioSet:
    """Validate all embedded cases and declarations without history/calculations.

    Timing is explicit per entry because legacy case payloads have no cutoff
    field. Cutoffs are submitted declarations, not authenticated source availability.
    """
    try:
        doc = _strict_json(text)
    except CaseInputError as exc:
        raise ScenarioInputError(exc.errors) from exc
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
            errors.append(f"{path}: UNSET/invalid; supply YYYY-MM-DD")
            return None

    doc = obj(doc, ("schema_version", "scenario_set_name", "scenarios"), "scenario_set")
    investor = doc.get("schema_version") == INVESTOR_SCHEMA
    if doc.get("schema_version") not in (SCENARIO_SCHEMA, INVESTOR_SCHEMA):
        errors.append(f"scenario_set.schema_version: requires {SCENARIO_SCHEMA} or {INVESTOR_SCHEMA}")
    name = doc.get("scenario_set_name")
    if type(name) is not str or not name.strip():
        errors.append("scenario_set.scenario_set_name: required nonempty text")
    entries = doc.get("scenarios")
    if type(entries) is not list:
        errors.append("scenarios: required array with exactly Bear, Base and Bull")
        entries = []
    elif len(entries) != 3:
        errors.append("scenarios: required exactly three complete cases, Bear/Base/Bull")
    parsed = []
    labels = []
    for i, entry in enumerate(entries):
        path = f"scenarios[{i}]"
        entry = obj(entry, ("label", "analytical_date", "information_cutoff", "case"), path)
        label = entry.get("label")
        if type(label) is not str or label not in LABELS:
            errors.append(f"{path}.label: requires Bear, Base or Bull")
        elif label in labels:
            errors.append(f"{path}.label: duplicate {label}")
        else:
            labels.append(label)
        analytical = day(entry.get("analytical_date"), path + ".analytical_date")
        cutoff = day(entry.get("information_cutoff"), path + ".information_cutoff")
        if analytical and cutoff and cutoff < analytical:
            errors.append(f"{path}.information_cutoff: must not precede analytical_date")
        case = None
        try:
            case = read_case(json.dumps(entry.get("case")))
            if investor and json.loads(case.submitted_json)["schema_version"] not in ("investor-case-v1", "investor-case-v2"):
                errors.append(f"{path}.case.schema_version: investor scenario sets require investor-case-v1/v2")
        except CaseInputError as exc:
            errors.extend(f"{path}.case.{error.removeprefix('case.')}" for error in exc.errors)
        if case is not None and analytical and analytical != case.assumptions.anchor_fiscal_end:
            errors.append(f"{path}.analytical_date: must equal case.anchor.annual_end")
        if case is not None and analytical and cutoff and label in LABELS:
            parsed.append((path, ScenarioCase(label, analytical, cutoff, case)))
    for missing in LABELS:
        if missing not in labels:
            errors.append(f"scenarios: missing label {missing}")

    # Compare supplied declarations exactly, including full Stage C metadata.
    # Numerical equality alone would silently discard scope/provenance differences.
    if parsed:
        _, reference = next((x for x in parsed if x[1].label == "Bear"), parsed[0])
        baseline = json.loads(reference.case.submitted_json)
        for path, item in parsed:
            current = json.loads(item.case.submitted_json)
            for key in ("anchor", "input_basis", "conventions"):
                if current[key] != baseline[key]:
                    errors.append(f"{path}.case.{key}: must match {reference.label} for comparison")
            for key in ("analytical_date", "information_cutoff"):
                if getattr(item, key) != getattr(reference, key):
                    errors.append(f"{path}.{key}: must match {reference.label} for comparison")
            if (item.case.bridge is None) != (reference.case.bridge is None):
                errors.append(f"{path}.case.calculation_scope: cannot mix EV-only and EQUITY_PER_SHARE")
            elif current.get("bridge") != baseline.get("bridge"):
                errors.append(f"{path}.case.bridge: all bridge/share inputs must be identical to {reference.label}")
            periods = [(y.period_index, y.fiscal_year_label) for y in item.case.assumptions.forecast_years]
            expected = [(y.period_index, y.fiscal_year_label) for y in reference.case.assumptions.forecast_years]
            if periods != expected:
                errors.append(f"{path}.case.forecast_years: period identities/labels must match {reference.label}")
    if errors:
        raise ScenarioInputError(errors)
    by_label = {item.label: item for _, item in parsed}
    return ScenarioSet(text, name, tuple(by_label[label] for label in LABELS))


def load_scenario_set(path: Path) -> ScenarioSet:
    return read_scenario_set(path.read_text(encoding="utf-8"))


def run_scenario_set(scenarios: ScenarioSet, repository_root: Path) -> dict[str, object]:
    """Revalidate the complete set, then delegate each case to existing A/B/C.

    Failures never return partial results. No output is written by this function.
    """
    if type(scenarios) is not ScenarioSet or read_scenario_set(scenarios.submitted_json) != scenarios:
        raise ScenarioInputError(["scenario_set: validated immutable ScenarioSet required"])
    results = []
    for item in scenarios.scenarios:
        try:
            result = run_case(item.case, repository_root)
        except (ValueError, OSError) as exc:
            raise ScenarioInputError([f"scenarios.{item.label}.case: execution failed: {exc}"]) from exc
        results.append({"label": item.label, "analytical_date": item.analytical_date.isoformat(),
                        "information_cutoff": item.information_cutoff.isoformat(), "result": result})
    return {"schema_version": INVESTOR_RESULT_SCHEMA if _strict_json(scenarios.submitted_json)["schema_version"] == INVESTOR_SCHEMA else RESULT_SCHEMA, "scenario_set_name": scenarios.scenario_set_name,
            "submitted_inputs": _strict_json(scenarios.submitted_json), "scenarios": results,
            "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR",
            "limitations": ["Scenario labels imply no valuation ordering or approved economics.",
                            "Cutoffs and input reviews are declarations, not authenticated availability or approvals.",
                            "No probabilities, expected value or investment recommendation calculated."]}


def serialize_scenarios(result: dict[str, object]) -> str:
    """Stable JSON; existing full single-case results retain Decimal strings."""
    return json.dumps(result, sort_keys=True, indent=2) + "\n"
