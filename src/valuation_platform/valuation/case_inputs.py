"""Editable local A/B/C inputs; parsing is not calculation or economic approval."""

from dataclasses import dataclass, fields
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re

from valuation_platform.analyst.historical_inputs import ManualIdentity
from valuation_platform.analyst.nwc import Period
from .assumptions import ForecastYearAssumptions, ValuationAssumptions
from .consumer import ANCHORS, IDENTITY, load_meta_revenue_anchor, load_revenue_anchor
from .discounting import (
    DISCOUNTING_CONVENTION_VERSION, TerminalAssumptions,
    discount_to_enterprise_value, enterprise_value_to_dict,
)
from .forecast import (
    CONVENTION_VERSION, SHARED_CONVENTION_VERSION, SUPPORTED_CONVENTIONS,
    RevenueAnchor, forecast_five_years,
)
from .bridge import (
    BridgeComponent, BridgeObservation, PopulationCoverage, ValuationShares,
    BridgeInputs, ComponentRole, bridge_to_per_share, bridge_to_dict,
    SHARED_CONVENTION_VERSION as SHARED_BRIDGE_CONVENTION,
)


CASE_SCHEMA = "analyst-case-v1"
RESULT_SCHEMA = "analyst-case-enterprise-value-v1"
EQUITY_CASE_SCHEMA = "analyst-case-v2"
EQUITY_RESULT_SCHEMA = "analyst-case-equity-per-share-v1"
EQUITY_SCOPE = "EQUITY_PER_SHARE"
ANNUAL_RATES = (
    "revenue_growth", "operating_margin", "forecast_tax_rate",
    "d_and_a_percent_revenue", "capex_percent_revenue",
    "change_in_operating_nwc_percent_revenue",
)
TERMINAL_RATES = (
    "operating_margin", "operating_tax_rate", "d_and_a_percent_revenue",
    "investment_percent_revenue", "working_capital_cash_requirement_percent_revenue",
)
SYNTHETIC_IDENTITY = {
    "cik": 123, "accession": "0000000123-26-000001", "form": "10-K",
    "annual_start": "2025-01-01", "annual_end": "2025-12-31",
}


class CaseInputError(ValueError):
    def __init__(self, errors):
        self.errors = tuple(errors)
        super().__init__("Case input errors:\n" + "\n".join("- " + e for e in self.errors))


def _strict_json(text):
    # Retain tokens/pairs until paths are known; never construct a float or
    # discard duplicate keys. Integers remain valid only where the schema allows.
    class Number(str):
        pass

    class Pairs(list):
        pass

    errors = []

    def decode(value, path):
        if type(value) is Number:
            errors.append(f"{path}: JSON number {value} is not allowed here; use finite fractional Decimal strings for rates")
        elif type(value) is Pairs:
            result = {}
            for key, child in value:
                location = f"{path}.{key}" if path else key
                if key in result:
                    errors.append(f"{location}: Duplicate JSON key: {key}")
                result[key] = decode(child, location)
            return result
        elif type(value) is list:
            return [decode(child, f"{path}[{i}]") for i, child in enumerate(value)]
        return value

    try:
        result = decode(json.loads(text, object_pairs_hook=Pairs,
                                   parse_float=Number, parse_constant=Number), "")
        if errors:
            raise CaseInputError(errors)
        return result
    except CaseInputError:
        raise
    except (ValueError, TypeError) as exc:
        raise CaseInputError([f"Malformed JSON: {exc}"]) from exc


@dataclass(frozen=True)
class AnalystCase:
    submitted_json: str
    analyst: ManualIdentity
    anchor_kind: str
    assumptions: ValuationAssumptions
    terminal: TerminalAssumptions
    bridge: BridgeInputs | None = None


def _read_bridge(raw, anchor, basis, errors):
    """Decode the six existing fixed models; no calculation or source retrieval."""
    def record(value, cls, path):
        names = {f.name for f in fields(cls)}
        if type(value) is not dict:
            errors.append(f"{path}: UNSET; required {cls.__name__} object")
            return None
        missing = names - value.keys()
        for name in sorted(missing):
            errors.append(f"{path}.{name}: missing required field")
        for name in sorted(value.keys() - names):
            errors.append(f"{path}.{name}: unknown field")
        if missing or value.keys() - names:
            return None
        data = dict(value)
        for name, value in data.items():
            location = f"{path}.{name}"
            nullable = cls is BridgeObservation and name in ("value", "as_of", "precision")
            if value is None and nullable:
                continue
            try:
                if name in ("amount", "shares", "value"):
                    if type(value) is not str or not re.fullmatch(
                            r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", value):
                        raise ValueError("UNSET/invalid; supply a finite Decimal string, not a JSON number")
                    data[name] = Decimal(value)
                elif name in ("as_of", "observation_date"):
                    if type(value) is not str:
                        raise ValueError("UNSET; supply YYYY-MM-DD")
                    data[name] = date.fromisoformat(value)
                    if data[name].isoformat() != value:
                        raise ValueError("supply YYYY-MM-DD")
                elif name == "role":
                    data[name] = ComponentRole(value)
                elif name.endswith("_references") or name == "population_ids":
                    if type(value) is not list:
                        raise ValueError("required array of explicit references")
                    data[name] = tuple(value)
                elif name == "review":
                    data[name] = record(value, ManualIdentity, location)
            except (ValueError, TypeError, ArithmeticError) as exc:
                errors.append(f"{location}: {exc}")
                return None
        try:
            return cls(**data)
        except (ValueError, TypeError, ArithmeticError) as exc:
            errors.append(f"{path}: {exc}")
            return None

    if type(raw) is not dict:
        errors.append("bridge: UNSET; required explicit Stage C inputs for EQUITY_PER_SHARE")
        return None
    names = {f.name for f in fields(BridgeInputs)}
    for name in sorted(names - raw.keys()):
        errors.append(f"bridge.{name}: missing required field")
    for name in sorted(raw.keys() - names):
        errors.append(f"bridge.{name}: unknown field")
    start = len(errors)
    decoded = {}
    for key, cls in (("components", BridgeComponent), ("observations", BridgeObservation),
                     ("coverage", PopulationCoverage)):
        values = raw.get(key)
        if type(values) is not list:
            errors.append(f"bridge.{key}: UNSET; required explicit array")
            continue
        decoded[key] = tuple(record(v, cls, f"bridge.{key}[{i}]") for i, v in enumerate(values))
    decoded["shares"] = record(raw.get("shares"), ValuationShares, "bridge.shares")
    unresolved = raw.get("unresolved_requirements")
    if type(unresolved) is not list or unresolved:
        errors.append(f"bridge.unresolved_requirements: must be an explicit empty array before calculation; pending: {unresolved!r}")
    if len(errors) != start or names != raw.keys():
        return None
    try:
        result = BridgeInputs(**decoded, input_basis=raw["input_basis"],
                              valuation_class_id=raw["valuation_class_id"],
                              unresolved_requirements=tuple(unresolved),
                              convention_version=raw["convention_version"])
        if result.input_basis != basis:
            raise ValueError("input_basis must match case.input_basis")
        for item in (*result.components, result.shares):
            observed = item.observation_date if type(item) is ValuationShares else item.as_of
            if item.company_cik != anchor.get("cik") or observed.isoformat() != anchor.get("annual_end"):
                raise ValueError("component/share company/date mismatch with anchor")
        if any(n.company_cik != anchor.get("cik") for n in result.observations):
            raise ValueError("observation company mismatch with anchor")
        return result
    except (ValueError, TypeError, ArithmeticError) as exc:
        errors.append(f"bridge: {exc}")
        return None


def read_case(text: str) -> AnalystCase:
    """Validate declarations/models only; no anchor reads or valuation calls."""
    doc = _strict_json(text)
    errors = []

    def obj(value, keys, path):
        if type(value) is not dict:
            errors.append(f"{path}: required JSON object")
            return {}
        for key in keys:
            if key not in value:
                errors.append(f"{path}.{key}: missing required field")
        for key in sorted(value.keys() - set(keys)):
            errors.append(f"{path}.{key}: unknown field")
        return value

    def text_field(value, path):
        if type(value) is not str or not value.strip():
            errors.append(f"{path}: required nonempty text (currently unset)")

    def rate(value, path):
        if value is None:
            errors.append(f"{path}: UNSET; supply a fractional Decimal string")
            return None
        if type(value) is not str or not re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", value):
            errors.append(f'{path}: use a finite fractional Decimal string, e.g. "0.12" for 12%; no % sign or JSON number')
            return None
        try:
            result = Decimal(value)
            if not result.is_finite():
                raise ValueError()
            return result
        except (ArithmeticError, ValueError):
            errors.append(f"{path}: invalid Decimal string")
            return None

    equity = type(doc) is dict and doc.get("schema_version") == EQUITY_CASE_SCHEMA
    extra = ("calculation_scope", "bridge") if equity else ()
    doc = obj(doc, ("schema_version", "case_name", "input_basis", "analyst", "scope",
                    "limitations", "conventions", "anchor", "forecast_years", "wacc",
                    "terminal_growth", "terminal", *extra), "case")
    if doc.get("schema_version") not in (CASE_SCHEMA, EQUITY_CASE_SCHEMA):
        errors.append(f"case.schema_version: supported versions are {CASE_SCHEMA}, {EQUITY_CASE_SCHEMA}")
    if equity and doc.get("calculation_scope") != EQUITY_SCOPE:
        errors.append(f"case.calculation_scope: {EQUITY_CASE_SCHEMA} requires {EQUITY_SCOPE}")
    text_field(doc.get("case_name"), "case.case_name")
    text_field(doc.get("scope"), "case.scope")
    limitations = doc.get("limitations")
    if type(limitations) is not list or not limitations:
        errors.append("case.limitations: required nonempty list of declared limitations")
    else:
        for i, value in enumerate(limitations):
            text_field(value, f"case.limitations[{i}]")
    analyst = obj(doc.get("analyst"), ("author", "timestamp_utc", "rationale"), "analyst")
    for key in ("author", "timestamp_utc", "rationale"):
        text_field(analyst.get(key), "analyst." + key)
    identity = None
    if all(type(analyst.get(k)) is str and analyst[k].strip() for k in ("author", "timestamp_utc", "rationale")):
        try:
            identity = ManualIdentity(**analyst)
        except (ValueError, TypeError) as exc:
            errors.append(f"analyst: {exc}")
    conventions = obj(doc.get("conventions"), ("forecast", "discounting"), "conventions")
    if conventions.get("forecast") not in SUPPORTED_CONVENTIONS:
        errors.append(f"conventions.forecast: choose {' or '.join(SUPPORTED_CONVENTIONS)}")
    if conventions.get("discounting") != DISCOUNTING_CONVENTION_VERSION:
        errors.append(f"conventions.discounting: supported convention is {DISCOUNTING_CONVENTION_VERSION}")
    anchor = obj(doc.get("anchor"), ("kind", *IDENTITY), "anchor")
    kind = anchor.get("kind")
    selections = {key: spec["identity"] for key, spec in ANCHORS.items()}
    selections["synthetic-fixture-v1"] = SYNTHETIC_IDENTITY
    expected = selections.get(kind) if type(kind) is str else None
    if expected is None:
        errors.append("anchor.kind: choose synthetic-fixture-v1 or pinned " + ", ".join(ANCHORS))
    else:
        for key, value in expected.items():
            if type(anchor.get(key)) is not type(value) or anchor.get(key) != value:
                errors.append(f"anchor.{key}: {kind} requires {value!r}; no automatic refresh")
        basis = "SYNTHETIC_FIXTURE" if kind == "synthetic-fixture-v1" else "MANUAL_INPUT"
        if doc.get("input_basis") != basis:
            errors.append(f"case.input_basis: {kind} requires {basis}")
        if kind in ("googl-fy2025", "aapl-fy2025"):
            if conventions.get("forecast") != SHARED_CONVENTION_VERSION:
                errors.append(f"conventions.forecast: {kind} requires {SHARED_CONVENTION_VERSION}; no META economic approval transfers")
            if equity and (type(doc.get("bridge")) is not dict or
                           doc["bridge"].get("convention_version") != SHARED_BRIDGE_CONVENTION):
                errors.append(f"bridge.convention_version: {kind} requires {SHARED_BRIDGE_CONVENTION}; actual selections remain unapproved")
    years = doc.get("forecast_years")
    annuals = []
    if type(years) is not list or len(years) != 5:
        errors.append("forecast_years: required array of five individually supplied years, ordered 1–5")
    else:
        for i, raw in enumerate(years):
            path = f"forecast_years[{i}]"
            raw = obj(raw, ("period_index", "fiscal_year_label", *ANNUAL_RATES), path)
            if type(raw.get("period_index")) is not int or raw.get("period_index") != i + 1:
                errors.append(f"{path}.period_index: must be {i + 1}")
            text_field(raw.get("fiscal_year_label"), path + ".fiscal_year_label")
            rates = {key: rate(raw.get(key), path + "." + key) for key in ANNUAL_RATES}
            if all(v is not None for v in rates.values()):
                try:
                    annuals.append(ForecastYearAssumptions(raw.get("period_index"), raw.get("fiscal_year_label"), **rates))
                except (ValueError, TypeError) as exc:
                    location = path + "." + exc.field if getattr(exc, "field", None) else path
                    errors.append(f"{location}: {exc}")
    wacc = rate(doc.get("wacc"), "wacc")
    growth = rate(doc.get("terminal_growth"), "terminal_growth")
    raw_terminal = obj(doc.get("terminal"), TERMINAL_RATES, "terminal")
    terminal_rates = {key: rate(raw_terminal.get(key), "terminal." + key) for key in TERMINAL_RATES}
    terminal = None
    if all(v is not None for v in terminal_rates.values()):
        try:
            terminal = TerminalAssumptions(**terminal_rates, convention_version=conventions.get("forecast"))
        except (ValueError, TypeError) as exc:
            location = "terminal." + exc.field if getattr(exc, "field", None) else "terminal"
            errors.append(f"{location}: {exc}")
    bridge = _read_bridge(doc.get("bridge"), anchor, doc.get("input_basis"), errors) if equity else None
    if errors:
        raise CaseInputError(errors)
    try:
        assumptions = ValuationAssumptions(
            "1", anchor["cik"], anchor["accession"], date.fromisoformat(anchor["annual_end"]),
            tuple(annuals), wacc, growth,
        )
    except (ValueError, TypeError) as exc:
        location = getattr(exc, "field", None) or "assumptions (wacc/terminal_growth/year labels)"
        raise CaseInputError([f"{location}: {exc}"]) from exc
    return AnalystCase(text, identity, kind, assumptions, terminal, bridge)


def load_case(path: Path) -> AnalystCase:
    return read_case(path.read_text(encoding="utf-8"))


def run_case(case: AnalystCase, repository_root: Path) -> dict[str, object]:
    """Explicit A/B or A/B/C run; no files written or approvals inferred."""
    if type(case) is not AnalystCase or read_case(case.submitted_json) != case:
        raise CaseInputError(["Validated AnalystCase required; submitted declarations disagree"])
    doc = _strict_json(case.submitted_json)
    if case.anchor_kind == "meta-fy2025":
        anchor = load_meta_revenue_anchor(repository_root)
    elif case.anchor_kind in ANCHORS:
        anchor = load_revenue_anchor(case.anchor_kind, repository_root)
    else:
        source = SYNTHETIC_IDENTITY
        anchor = RevenueAnchor(
            Period(source["cik"], source["accession"], date.fromisoformat(source["annual_start"]),
                   date.fromisoformat(source["annual_end"]), source["form"]),
            Decimal("100"), "100", "INF", "synthetic:revenue", "synthetic:effective",
            "synthetic:declaration", '{"basis":"SYNTHETIC_FIXTURE; not a SEC observation"}',
            '{"basis":"synthetic fixture; no actual-case approval"}',
        )
    stage_a = forecast_five_years(anchor, case.assumptions, convention_version=doc["conventions"]["forecast"])
    stage_b = discount_to_enterprise_value(stage_a, case.terminal,
                                          convention_version=doc["conventions"]["discounting"])
    result = {
        "schema_version": RESULT_SCHEMA,
        "case_name": doc["case_name"], "input_basis": doc["input_basis"],
        "submitted_inputs": doc,
        "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR",
        "limitations": [*doc["limitations"],
                        "Analyst identity, rationale and scope are submitted declarations, not authenticated approval.",
                        ("No economic consistency, evidence completeness or actual META execution approval is inferred."
                         if case.anchor_kind in ("meta-fy2025", "synthetic-fixture-v1") else
                         "No economic consistency, evidence completeness or company execution approval is inferred."),
                        "Enterprise value only; no bridge/share inputs or automatic historical forecasts."],
        "stage_b": enterprise_value_to_dict(stage_b),
    }
    if case.bridge is not None:
        stage_c = bridge_to_dict(bridge_to_per_share(stage_b, case.bridge))
        result["schema_version"] = EQUITY_RESULT_SCHEMA
        result["calculation_scope"] = EQUITY_SCOPE
        result["stage_c"] = stage_c
        result["limitations"][-1:] = stage_c["limitations"]
    return result
