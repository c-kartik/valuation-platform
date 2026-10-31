"""Editable local A/B/C inputs; parsing is not calculation or economic approval."""

from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
import json
from pathlib import Path
import re

from valuation_platform.analyst.historical_inputs import ManualIdentity
from valuation_platform.analyst.nwc import Period
from .assumptions import ForecastYearAssumptions, OperatingAssumptions, ValuationAssumptions
from .terminal_methods import ExitMultipleMethod, PerpetualGrowthMethod, value_terminal, implied_multiple, EXIT_CONVENTION, EXTENDED_EXIT_CONVENTION
from .consumer import ANCHORS, IDENTITY, load_meta_revenue_anchor, load_revenue_anchor
from .discounting import (
    DISCOUNTING_CONVENTION_VERSION, TerminalAssumptions,
    discount_to_enterprise_value, enterprise_value_to_dict,
)
from .forecast import (
    CONVENTION_VERSION, SHARED_CONVENTION_VERSION, SUPPORTED_CONVENTIONS,
    RevenueAnchor, forecast_five_years, forecast_periods,
)
from .bridge import (
    BridgeComponent, BridgeObservation, PopulationCoverage, ValuationShares,
    BridgeInputs, ComponentRole, bridge_to_per_share, bridge_to_dict,
    SHARED_CONVENTION_VERSION as SHARED_BRIDGE_CONVENTION,
)


METHOD_CASE_SCHEMA = "analyst-case-v3"
METHOD_INVESTOR_SCHEMA = "investor-case-v3"
HORIZON_SCHEMAS = ("analyst-case-v4", "investor-case-v4")
METHOD_SCHEMAS = (METHOD_CASE_SCHEMA, METHOD_INVESTOR_SCHEMA, *HORIZON_SCHEMAS)
CASE_SCHEMA = "analyst-case-v1"
RESULT_SCHEMA = "analyst-case-enterprise-value-v1"
EQUITY_CASE_SCHEMA = "analyst-case-v2"
EQUITY_RESULT_SCHEMA = "analyst-case-equity-per-share-v1"
EQUITY_SCOPE = "EQUITY_PER_SHARE"
INVESTOR_CASE_SCHEMA = "investor-case-v1"
INVESTOR_RESULT_SCHEMA = "investor-case-enterprise-value-v1"
INVESTOR_EQUITY_CASE_SCHEMA = "investor-case-v2"
INVESTOR_EQUITY_RESULT_SCHEMA = "investor-case-equity-per-share-v1"
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
    analyst: ManualIdentity | None
    anchor_kind: str
    assumptions: ValuationAssumptions | OperatingAssumptions
    terminal: TerminalAssumptions | ExitMultipleMethod
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


def _read_terminal_method(raw, wacc, convention):
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
        return _decode_terminal_method(raw, wacc, convention)


def _decode_terminal_method(raw, wacc, convention):
    """Strict method-specific operands. No dummy growth or unused terminal ratios."""
    def number(v, path):
        if type(v) is not str or not re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?", v):
            raise CaseInputError([path + ": UNSET/invalid; supply an exact finite Decimal string"])
        result = Decimal(v)
        if not result.is_finite():
            raise CaseInputError([path + ": finite Decimal required"])
        return result
    try:
        if type(raw) is not dict:
            raise CaseInputError(["terminal_valuation: required method-specific object"])
        method = raw.get("method")
        if method == "exit_multiple":
            if raw.keys() != {"method", "exit_ev_ebit_multiple"}:
                raise CaseInputError(["exit_ev_ebit_multiple: exit method requires only method and exit_ev_ebit_multiple"])
            return ExitMultipleMethod(number(raw["exit_ev_ebit_multiple"], "exit_ev_ebit_multiple"))
        if method != "perpetual_growth" or raw.keys() != {"method", "terminal_growth", "terminal"}:
            raise CaseInputError(["terminal_valuation: choose perpetual_growth or exit_multiple with exact method-specific fields"])
        growth = number(raw["terminal_growth"], "terminal_growth")
        if growth <= -1 or (wacc is not None and growth >= wacc):
            raise CaseInputError(["terminal_growth: must be greater than -1 and less than WACC"])
        ratios = raw["terminal"]
        if type(ratios) is not dict or ratios.keys() != set(TERMINAL_RATES):
            raise CaseInputError(["terminal: five explicit terminal operating ratios required"])
        terminal = TerminalAssumptions(**{k:number(ratios[k], "terminal."+k) for k in TERMINAL_RATES}, convention_version=convention)
        return PerpetualGrowthMethod(growth, terminal)
    except CaseInputError:
        raise
    except (ValueError, TypeError, ArithmeticError) as exc:
        raise CaseInputError([str(getattr(exc, "field", None) or "terminal_valuation")+": "+str(exc)]) from exc


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

    method_case = type(doc) is dict and doc.get("schema_version") in METHOD_SCHEMAS
    investor = type(doc) is dict and doc.get("schema_version") in (INVESTOR_CASE_SCHEMA, INVESTOR_EQUITY_CASE_SCHEMA, METHOD_INVESTOR_SCHEMA, "investor-case-v4")
    equity = type(doc) is dict and doc.get("schema_version") in (EQUITY_CASE_SCHEMA, INVESTOR_EQUITY_CASE_SCHEMA)
    equity = equity or (method_case and doc.get("calculation_scope") == EQUITY_SCOPE)
    extended = method_case and doc.get("schema_version") in HORIZON_SCHEMAS
    horizon = 10 if extended else 5
    extra = ("calculation_scope", "bridge") if equity else (("calculation_scope",) if method_case else ())
    if extended:
        extra += ("forecast_horizon",)
        if type(doc.get("forecast_horizon")) is not int or doc.get("forecast_horizon") != 10:
            errors.append("forecast_horizon: v4 requires the explicit integer 10")
    terminal_keys = ("terminal_valuation", "comparison_terminal_valuation") if method_case else ("terminal_growth", "terminal")
    metadata = ("preparation",) if investor else ("analyst", "scope")
    doc = obj(doc, ("schema_version", "case_name", "input_basis", *metadata,
                    "limitations", "conventions", "anchor", "forecast_years", "wacc",
                    *terminal_keys, *extra), "case")
    if doc.get("schema_version") not in (CASE_SCHEMA, EQUITY_CASE_SCHEMA, INVESTOR_CASE_SCHEMA, INVESTOR_EQUITY_CASE_SCHEMA, *METHOD_SCHEMAS):
        errors.append(f"case.schema_version: supported versions are {CASE_SCHEMA}, {EQUITY_CASE_SCHEMA}, {INVESTOR_CASE_SCHEMA}, {INVESTOR_EQUITY_CASE_SCHEMA}")
    if method_case and doc.get("calculation_scope") not in ("ENTERPRISE_VALUE", EQUITY_SCOPE):
        errors.append("case.calculation_scope: choose ENTERPRISE_VALUE or EQUITY_PER_SHARE")
    if equity and doc.get("calculation_scope") != EQUITY_SCOPE:
        errors.append(f"case.calculation_scope: {doc.get('schema_version')} requires {EQUITY_SCOPE}")
    text_field(doc.get("case_name"), "case.case_name")
    if not investor:
        text_field(doc.get("scope"), "case.scope")
    limitations = doc.get("limitations")
    if type(limitations) is not list or not limitations:
        errors.append("case.limitations: required nonempty list of declared limitations")
    else:
        for i, value in enumerate(limitations):
            text_field(value, f"case.limitations[{i}]")
    identity = None
    if investor:
        preparation = obj(doc.get("preparation"), ("provenance", "timestamp_utc", "notes"), "preparation")
        if preparation.get("provenance") != "ANONYMOUS_INVESTOR":
            errors.append("preparation.provenance: must be ANONYMOUS_INVESTOR; no authenticated identity")
        try:
            stamp = datetime.fromisoformat(preparation.get("timestamp_utc"))
            if stamp.utcoffset() is None or stamp.utcoffset().total_seconds() != 0:
                raise ValueError()
        except (ValueError, TypeError):
            errors.append("preparation.timestamp_utc: required UTC preparation timestamp; not an information cutoff")
        notes = preparation.get("notes")
        if notes is not None and (type(notes) is not str or not notes.strip() or len(notes) > 2048):
            errors.append("preparation.notes: use null for absent notes or nonempty text up to 2048 characters")
    else:
        analyst = obj(doc.get("analyst"), ("author", "timestamp_utc", "rationale"), "analyst")
        for key in ("author", "timestamp_utc", "rationale"):
            text_field(analyst.get(key), "analyst." + key)
        if all(type(analyst.get(k)) is str and analyst[k].strip() for k in ("author", "timestamp_utc", "rationale")):
            try:
                identity = ManualIdentity(**analyst)
            except (ValueError, TypeError) as exc:
                errors.append(f"analyst: {exc}")
    conventions = obj(doc.get("conventions"), ("forecast", "discounting"), "conventions")
    if conventions.get("forecast") not in SUPPORTED_CONVENTIONS:
        errors.append(f"conventions.forecast: choose {' or '.join(SUPPORTED_CONVENTIONS)}")
    exit_case = method_case and type(doc.get("terminal_valuation")) is dict and doc["terminal_valuation"].get("method") == "exit_multiple"
    expected_discounting = (EXTENDED_EXIT_CONVENTION if extended else EXIT_CONVENTION) if exit_case else DISCOUNTING_CONVENTION_VERSION
    if conventions.get("discounting") != expected_discounting:
        errors.append(f"conventions.discounting: supported convention is {expected_discounting}")
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
    if type(years) is not list or len(years) != horizon:
        errors.append(f"forecast_years: required array of {horizon} individually supplied years, ordered 1–{horizon}")
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
    growth = None
    terminal = None
    if method_case:
        try:
            method = _read_terminal_method(doc.get("terminal_valuation"), wacc, conventions.get("forecast"))
            if type(method) is ExitMultipleMethod:
                terminal = method
            else:
                growth, terminal = method.terminal_growth, method.terminal
        except CaseInputError as exc:
            errors.extend(exc.errors)
        # Opposite-method omissions/errors are comparison status, never a selected-case blocker.
        comparison = doc.get("comparison_terminal_valuation")
        if comparison is not None and type(comparison) is not dict:
            errors.append("comparison_terminal_valuation: required object or null")
        elif type(comparison) is dict:
            allowed = {"method", "exit_ev_ebit_multiple"} if comparison.get("method") == "exit_multiple" else {"method", "terminal_growth", "terminal"}
            if comparison.keys() - allowed:
                errors.append("comparison_terminal_valuation: unknown fields")
            if type(comparison.get("terminal")) is dict and comparison["terminal"].keys() - set(TERMINAL_RATES):
                errors.append("comparison_terminal_valuation.terminal: unknown fields")
    else:
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
    if exit_case and len(annuals) == horizon and (annuals[-1].operating_margin <= 0 or any(y.revenue_growth == -1 for y in annuals)):
        errors.append(f"forecast_years[{horizon-1}].operating_margin: exit multiple unsupported: year-{horizon} EBIT must be strictly positive")
    bridge = _read_bridge(doc.get("bridge"), anchor, doc.get("input_basis"), errors) if equity else None
    if errors:
        raise CaseInputError(errors)
    try:
        assumption_type = OperatingAssumptions if exit_case else ValuationAssumptions
        assumptions = assumption_type(
            "2" if extended else "1", anchor["cik"], anchor["accession"], date.fromisoformat(anchor["annual_end"]),
            tuple(annuals), wacc, *((growth,) if not exit_case else ()),
        )
    except (ValueError, TypeError) as exc:
        location = getattr(exc, "field", None) or "assumptions (wacc/terminal_growth/year labels)"
        raise CaseInputError([f"{location}: {exc}"]) from exc
    return AnalystCase(text, identity, kind, assumptions, terminal, bridge)


def load_case(path: Path) -> AnalystCase:
    return read_case(path.read_text(encoding="utf-8"))


def run_case(case: AnalystCase, repository_root: Path) -> dict[str, object]:
    """Explicit A/B or A/B/C run; no files written or approvals inferred."""
    return _prepare_case_runner(case, repository_root)(case)


def _validated_case_document(case):
    if type(case) is not AnalystCase or read_case(case.submitted_json) != case:
        raise CaseInputError(["Validated AnalystCase required; submitted declarations disagree"])
    return _strict_json(case.submitted_json)


def _prepare_case_runner(case: AnalystCase, repository_root: Path):
    """One request-local, source-validated immutable anchor; no shared cache.

    Only candidates with the identical declared anchor can use this closure.
    Every candidate is still reparsed/validated and executes the same A/B/C
    formulas. A later request always reloads and revalidates source/approvals.
    """
    declaration = _validated_case_document(case)["anchor"]
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

    def execute(candidate):
        doc = _validated_case_document(candidate)
        if doc["anchor"] != declaration:
            raise CaseInputError(["Prepared execution requires the identical historical anchor declaration"])
        return _run_case(candidate, anchor, doc)

    return execute


def _run_case(case, anchor, doc):
    """Shared financial execution; anchor supplied only by the validated closure."""
    stage_a = (forecast_five_years if len(case.assumptions.forecast_years) == 5 else forecast_periods)(anchor, case.assumptions, convention_version=doc["conventions"]["forecast"])
    method_case = doc["schema_version"] in METHOD_SCHEMAS
    stage_b = value_terminal(stage_a, case.terminal) if type(case.terminal) is ExitMultipleMethod else discount_to_enterprise_value(stage_a, case.terminal,
                                          convention_version=doc["conventions"]["discounting"])
    result = {
        "schema_version": INVESTOR_RESULT_SCHEMA if doc["schema_version"] in (INVESTOR_CASE_SCHEMA, INVESTOR_EQUITY_CASE_SCHEMA, METHOD_INVESTOR_SCHEMA, "investor-case-v4") else RESULT_SCHEMA,
        "case_name": doc["case_name"], "input_basis": doc["input_basis"],
        "submitted_inputs": doc,
        "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR",
        "limitations": [*doc["limitations"],
                        ("Anonymous investor preparation; no verified identity or supplied investment rationale. Optional personal notes are not evidence or approval. Preparation timestamp is not a valuation date, information cutoff or evidence review. Forecast inputs are user-entered and not independently reviewed."
                         if doc["schema_version"] in (INVESTOR_CASE_SCHEMA, INVESTOR_EQUITY_CASE_SCHEMA, METHOD_INVESTOR_SCHEMA, "investor-case-v4") else
                         "Analyst identity, rationale and scope are submitted declarations, not authenticated approval."),
                        ("No economic consistency, evidence completeness or actual META execution approval is inferred."
                         if case.anchor_kind in ("meta-fy2025", "synthetic-fixture-v1") else
                         "No economic consistency, evidence completeness or company execution approval is inferred."),
                        "Enterprise value only; no bridge/share inputs or automatic historical forecasts."],
        "stage_b": enterprise_value_to_dict(stage_b),
    }
    if case.bridge is not None:
        stage_c = bridge_to_dict(bridge_to_per_share(stage_b, case.bridge))
        result["schema_version"] = INVESTOR_EQUITY_RESULT_SCHEMA if doc["schema_version"] == INVESTOR_EQUITY_CASE_SCHEMA else EQUITY_RESULT_SCHEMA
        result["calculation_scope"] = EQUITY_SCOPE
        result["stage_c"] = stage_c
        result["limitations"][-1:] = stage_c["limitations"]
    if method_case:
        version = "v4" if doc["schema_version"] in HORIZON_SCHEMAS else "v3"
        result["schema_version"] = ("investor-case-result-" if "preparation" in doc else "analyst-case-result-") + version
        selected = doc["terminal_valuation"]["method"]
        result["stage_b"]["terminal_method"] = selected
        comparison = {"selected_method": selected, "submitted_inputs": doc,
                      "results": {selected: {"status": "CURRENT", "stage_b": result["stage_b"]}},
                      "ev_difference_exit_minus_perpetual": None}
        if selected == "perpetual_growth":
            comparison["implied_year_five_ev_ebit" if len(stage_a.years) == 5 else "implied_final_year_ev_ebit"] = implied_multiple(stage_b)
        opposite = "perpetual_growth" if selected == "exit_multiple" else "exit_multiple"
        try:
            raw = doc["comparison_terminal_valuation"]
            if type(raw) is not dict or raw.get("method") != opposite:
                raise CaseInputError(["Opposite method inputs not supplied"])
            method = _read_terminal_method(raw, case.assumptions.wacc, stage_a.convention_version)
            other = value_terminal(stage_a, method)
            other_dict = enterprise_value_to_dict(other)
            other_dict["terminal_method"] = opposite
            comparison["results"][opposite] = {"status": "CURRENT", "stage_b": other_dict}
            if opposite == "perpetual_growth":
                comparison["implied_year_five_ev_ebit" if len(stage_a.years) == 5 else "implied_final_year_ev_ebit"] = implied_multiple(other)
            with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
                comparison["ev_difference_exit_minus_perpetual"] = str(
                    Decimal(comparison["results"]["exit_multiple"]["stage_b"]["enterprise_value"]) -
                    Decimal(comparison["results"]["perpetual_growth"]["stage_b"]["enterprise_value"]))
        except (ValueError, ArithmeticError) as exc:
            comparison["results"][opposite] = {"status": "AWAITING_INPUTS", "reason": str(exc)}
        result["terminal_comparison"] = comparison
    return result
