"""Editable local A/B inputs; parsing is not calculation or economic approval."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import re

from valuation_platform.analyst.historical_inputs import ManualIdentity
from valuation_platform.analyst.nwc import Period
from .assumptions import ForecastYearAssumptions, ValuationAssumptions
from .consumer import IDENTITY, load_meta_revenue_anchor
from .discounting import (
    DISCOUNTING_CONVENTION_VERSION, TerminalAssumptions,
    discount_to_enterprise_value, enterprise_value_to_dict,
)
from .forecast import CONVENTION_VERSION, RevenueAnchor, forecast_five_years


CASE_SCHEMA = "analyst-case-v1"
RESULT_SCHEMA = "analyst-case-enterprise-value-v1"
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
    # Same duplicate-key rejection pattern as analyst_overrides._json, with
    # explicit float/NaN rejection before JSON can lose the submitted precision.
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise CaseInputError([f"Duplicate JSON key: {key}"])
            result[key] = value
        return result

    def number(token):
        raise CaseInputError([f"JSON number {token} is not allowed here; use fractional Decimal strings for rates"])

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_float=number, parse_constant=number)
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

    doc = obj(doc, ("schema_version", "case_name", "input_basis", "analyst", "scope",
                    "limitations", "conventions", "anchor", "forecast_years", "wacc",
                    "terminal_growth", "terminal"), "case")
    if doc.get("schema_version") != CASE_SCHEMA:
        errors.append(f"case.schema_version: supported version is {CASE_SCHEMA}")
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
    for key, expected in (("forecast", CONVENTION_VERSION), ("discounting", DISCOUNTING_CONVENTION_VERSION)):
        if conventions.get(key) != expected:
            errors.append(f"conventions.{key}: supported convention is {expected}")
    anchor = obj(doc.get("anchor"), ("kind", *IDENTITY), "anchor")
    kind = anchor.get("kind")
    expected = {"synthetic-fixture-v1": SYNTHETIC_IDENTITY, "meta-fy2025": IDENTITY}.get(kind) if type(kind) is str else None
    if expected is None:
        errors.append("anchor.kind: choose synthetic-fixture-v1 or pinned meta-fy2025")
    else:
        for key, value in expected.items():
            if type(anchor.get(key)) is not type(value) or anchor.get(key) != value:
                errors.append(f"anchor.{key}: {kind} requires {value!r}; no automatic refresh")
        basis = "SYNTHETIC_FIXTURE" if kind == "synthetic-fixture-v1" else "MANUAL_INPUT"
        if doc.get("input_basis") != basis:
            errors.append(f"case.input_basis: {kind} requires {basis}")
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
                    errors.append(f"{path}: {exc}")
    wacc = rate(doc.get("wacc"), "wacc")
    growth = rate(doc.get("terminal_growth"), "terminal_growth")
    raw_terminal = obj(doc.get("terminal"), TERMINAL_RATES, "terminal")
    terminal_rates = {key: rate(raw_terminal.get(key), "terminal." + key) for key in TERMINAL_RATES}
    terminal = None
    if all(v is not None for v in terminal_rates.values()):
        try:
            terminal = TerminalAssumptions(**terminal_rates, convention_version=CONVENTION_VERSION)
        except (ValueError, TypeError) as exc:
            errors.append(f"terminal: {exc}")
    if errors:
        raise CaseInputError(errors)
    try:
        assumptions = ValuationAssumptions(
            "1", anchor["cik"], anchor["accession"], date.fromisoformat(anchor["annual_end"]),
            tuple(annuals), wacc, growth,
        )
    except (ValueError, TypeError) as exc:
        raise CaseInputError([f"assumptions (wacc/terminal_growth/year labels): {exc}"]) from exc
    return AnalystCase(text, identity, kind, assumptions, terminal)


def load_case(path: Path) -> AnalystCase:
    return read_case(path.read_text(encoding="utf-8"))


def run_case(case: AnalystCase, repository_root: Path) -> dict[str, object]:
    """Explicit A/B run; no files written, no approvals or bridge/share intake."""
    if type(case) is not AnalystCase or read_case(case.submitted_json) != case:
        raise CaseInputError(["Validated AnalystCase required; submitted declarations disagree"])
    doc = _strict_json(case.submitted_json)
    if case.anchor_kind == "meta-fy2025":
        anchor = load_meta_revenue_anchor(repository_root)
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
    return {
        "schema_version": RESULT_SCHEMA,
        "case_name": doc["case_name"], "input_basis": doc["input_basis"],
        "submitted_inputs": doc,
        "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR",
        "limitations": [*doc["limitations"],
                        "Analyst identity, rationale and scope are submitted declarations, not authenticated approval.",
                        "No economic consistency, evidence completeness or actual META execution approval is inferred.",
                        "Enterprise value only; no bridge/share inputs or automatic historical forecasts."],
        "stage_b": enterprise_value_to_dict(stage_b),
    }
