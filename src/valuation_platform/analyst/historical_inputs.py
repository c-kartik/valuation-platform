"""WP0 structural preparation contract; no resolution or financial calculation."""

from __future__ import annotations

import base64
from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import Enum
import json
import re

from valuation_platform.analyst.nwc import Artifact, Period
from valuation_platform.analyst.cash_flow_inputs import Receipt


SCHEMA = "historical-input-preparation-v1"
# Frozen Phase 1H.5 exclusions, including GE (40545), despite generic execution.
SPECIALIZED_CIKS = frozenset({1067983, 19617, 70858, 731766, 40545, 886982, 72971, 895421})


class InputError(ValueError):
    """Invalid structural contract; not an economic equivalence assessment."""


class Field(str, Enum):
    REVENUE = "revenue"
    EBIT = "ebit"
    DA = "depreciation_amortization"
    CAPEX = "cash_capex"
    CF_WORKING_CAPITAL = "reported_cash_flow_working_capital_movements"
    DEFERRED_TAX = "deferred_taxes"
    SBC = "stock_based_compensation"
    CFO_RESIDUAL = "unclassified_cfo_reconciliation_residual"
    CFO = "reported_cfo"
    TAX = "reported_tax_context"
    CASH_INVESTMENTS = "cash_investment_components"
    DEBT_LEASES = "debt_lease_components"
    OTHER_BRIDGE = "other_equity_bridge_claims_assets"
    SHARES = "point_in_time_shares"


class Origin(str, Enum):
    REPORTED = "reported"
    DERIVED = "derived"
    PROXY = "proxy"
    OVERRIDE = "analyst_override"
    UNAVAILABLE = "unavailable"


class Quality(str, Enum):
    UNASSESSED = "unassessed"
    SUPPORTED = "supported"
    LIMITED = "limited"
    CONFLICTING = "conflicting"


class Completeness(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class Review(str, Enum):
    UNREVIEWED = "unreviewed"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted_for_stated_preparation_scope"


class Scope(str, Enum):
    UNKNOWN = "unknown"
    CONSOLIDATED_REPORTED = "consolidated_reported"
    OPERATING_ONLY = "operating_only"
    MIXED = "mixed"
    RESTRICTED = "restricted"


class FormulaKind(str, Enum):
    COMPONENT_TOTAL = "component_total"
    OPERATING_EXPENSE_BRIDGE = "revenue_minus_operating_expenses"
    CFO_REMAINDER = "cfo_reconciliation_remainder"


def _text(v: object) -> None:
    if type(v) is not str or not v.strip():
        raise InputError("Explicit nonempty identity, reason or scope required")


def _strings(v: object) -> None:
    if type(v) is not tuple:
        raise InputError("Immutable tuple required")
    for x in v:
        _text(x)
    if len(set(v)) != len(v):
        raise InputError("Duplicate reference")


def _typed(v: object, cls: type) -> None:
    if type(v) is not tuple or any(type(x) is not cls for x in v):
        raise InputError("Immutable typed tuple required")


@dataclass(frozen=True)
class ManualIdentity:
    author: str
    timestamp_utc: str
    rationale: str

    def __post_init__(self) -> None:
        for v in (self.author, self.timestamp_utc, self.rationale):
            _text(v)
        try:
            stamp = datetime.fromisoformat(self.timestamp_utc)
            if stamp.utcoffset() is None or stamp.utcoffset().total_seconds() != 0:
                raise ValueError()
        except ValueError as exc:
            raise InputError("Actual UTC manual-entry timestamp required") from exc


@dataclass(frozen=True)
class SourceReference:
    """Exact retained source locator; hash integrity is not fact/scope review."""

    source_id: str
    period: Period
    receipt: Receipt
    locator: str
    namespace: str
    concept: str
    context_id: str
    occurrence_ordinal: int | None
    start: date | None
    end: date
    unit: str
    raw_value: str
    decimals: str
    dimensions: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.period) is not Period or type(self.receipt) is not Receipt:
            raise InputError("Exact period and retained original-body receipt required")
        if self.receipt.artifact.accession != self.period.accession:
            raise InputError("Source accession mismatch")
        for v in (self.source_id, self.locator, self.unit, self.raw_value, self.decimals):
            _text(v)
        if self.unit not in ("USD", "shares") or not re.fullmatch(r"INF|-?\d+", self.decimals):
            raise InputError("Explicit normalized unit and reported precision required")
        if type(self.end) is not date or (self.start is not None and
                (type(self.start) is not date or self.start != self.period.annual_start or self.end != self.period.annual_end)):
            raise InputError("Source annual dates mismatch")
        _strings(self.dimensions)
        if self.occurrence_ordinal is not None:
            if type(self.occurrence_ordinal) is not int or self.occurrence_ordinal < 0:
                raise InputError("Invalid occurrence ordinal")
            for v in (self.namespace, self.concept, self.context_id):
                _text(v)
        elif any((self.namespace, self.concept, self.context_id)):
            raise InputError("Note source uses locator, not fabricated occurrence identity")
        try:
            if not Decimal(self.raw_value).is_finite():
                raise ValueError()
        except Exception as exc:
            raise InputError("Finite original numeric representation required") from exc


@dataclass(frozen=True)
class Formula:
    formula_id: str
    version: int
    kind: FormulaKind
    expression: str
    operands: tuple[str, ...]
    operating_only: bool
    complete_coverage: bool
    non_overlapping: bool
    scope_evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for v in (self.formula_id, self.expression):
            _text(v)
        _strings(self.operands)
        _strings(self.scope_evidence_ids)
        if not self.operands or not self.scope_evidence_ids or type(self.version) is not int or self.version < 1:
            raise InputError("Versioned formula, exact operands and scope evidence required")
        if type(self.kind) is not FormulaKind or any(type(v) is not bool for v in
                (self.operating_only, self.complete_coverage, self.non_overlapping)):
            raise InputError("Explicit formula scope declarations required")
        if not self.non_overlapping:
            raise InputError("Known overlapping components cannot be totaled")
        if self.kind is FormulaKind.OPERATING_EXPENSE_BRIDGE and not self.operating_only:
            raise InputError("Revenue-minus-expenses requires operating-only expense scope")


@dataclass(frozen=True)
class InputValue:
    input_id: str
    field: Field
    period: Period
    as_of: date | None
    value: Decimal | None
    unit: str
    scale: int
    sign: int
    precision: str
    role: str
    origin: Origin
    quality: Quality
    scope: str
    scope_status: Scope
    completeness: Completeness
    review: Review
    sources: tuple[SourceReference, ...]
    manual: ManualIdentity | None
    formula: Formula | None
    alternatives: tuple[InputValue, ...]
    selection_rationale: str
    flags: tuple[str, ...]
    unresolved_requirements: tuple[str, ...]
    null_reason: str | None
    coverage_keys: tuple[str, ...]

    def __post_init__(self) -> None:
        for v in (self.input_id, self.precision, self.role, self.scope, self.selection_rationale):
            _text(v)
        for v, cls in ((self.field, Field), (self.origin, Origin), (self.quality, Quality),
                       (self.completeness, Completeness), (self.review, Review), (self.period, Period),
                       (self.scope_status, Scope)):
            if type(v) is not cls:
                raise InputError("Explicit typed identity/status required")
        if self.unit != ("shares" if self.field is Field.SHARES else "USD"):
            raise InputError("Field/unit mismatch")
        if type(self.scale) is not int or self.scale < 1 or type(self.sign) is not int or self.sign not in (-1, 1):
            raise InputError("Explicit positive scale and sign multiplier required")
        bridge = self.field in (Field.CASH_INVESTMENTS, Field.DEBT_LEASES, Field.OTHER_BRIDGE, Field.SHARES)
        if bridge:
            unknown_share_date = self.field is Field.SHARES and self.value is None and self.as_of is None
            if not unknown_share_date and (type(self.as_of) is not date or
                    (self.field is not Field.SHARES and self.as_of != self.period.annual_end)):
                raise InputError("FY-end bridge or separately dated point-in-time shares required")
        elif self.as_of is not None:
            raise InputError("Historical flows require authoritative annual period")
        _typed(self.sources, SourceReference)
        _typed(self.alternatives, InputValue)
        for refs in (self.flags, self.unresolved_requirements, self.coverage_keys):
            _strings(refs)
        if len({s.source_id for s in self.sources}) != len(self.sources):
            raise InputError("Duplicate source identity")
        for s in self.sources:
            if s.period != self.period or s.unit != self.unit or (bridge and (s.start is not None or s.end != self.as_of)) or (not bridge and s.start is None):
                raise InputError("Source/target period, date or unit mismatch")
        if self.value is None:
            if self.origin is not Origin.UNAVAILABLE or self.null_reason is None or not self.unresolved_requirements:
                raise InputError("Unavailable required value needs null reason and unresolved requirement")
            _text(self.null_reason)
            if self.completeness is Completeness.COMPLETE:
                raise InputError("Acknowledgment cannot resolve a missing value")
        elif type(self.value) is not Decimal or not self.value.is_finite() or self.origin is Origin.UNAVAILABLE or self.null_reason is not None:
            raise InputError("Finite Decimal or explicitly unavailable value required")
        if self.manual is not None and type(self.manual) is not ManualIdentity:
            raise InputError("Invalid manual provenance")
        if self.formula is not None and type(self.formula) is not Formula:
            raise InputError("Invalid formula provenance")
        if self.origin is Origin.REPORTED and (not self.sources or self.manual is not None or self.formula is not None):
            raise InputError("Reported value requires source evidence, not manual/derived identity")
        if self.origin is Origin.REPORTED:
            for s in self.sources:
                raw = Decimal(s.raw_value)
                with localcontext() as ctx:
                    ctx.prec = max(28, len(raw.as_tuple().digits) + len(str(self.scale)) + 4)
                    if raw * self.scale * self.sign != self.value or s.decimals != self.precision:
                        raise InputError("Reported representation, sign, scale or precision mismatch")
        if self.origin in (Origin.PROXY, Origin.OVERRIDE) and self.manual is None:
            raise InputError("Explicit author, timestamp and rationale required for analyst inputs")
        if self.origin is Origin.DERIVED and self.formula is None:
            raise InputError("Derived value requires formula/version")
        if self.formula is not None:
            if self.origin is not Origin.DERIVED:
                raise InputError("Formula belongs only to derived inputs")
            if not self.formula.complete_coverage and self.completeness is not Completeness.PARTIAL:
                raise InputError("Partial component sums must remain partial")
            if self.formula.kind is FormulaKind.CFO_REMAINDER and self.field is not Field.CFO_RESIDUAL:
                raise InputError("CFO remainder is not an approved operating adjustment")
            if self.formula.kind is FormulaKind.OPERATING_EXPENSE_BRIDGE and self.field is not Field.EBIT:
                raise InputError("Operating expense bridge belongs only to EBIT")
        if self.origin is Origin.OVERRIDE and not self.alternatives:
            raise InputError("Override must preserve displaced alternatives")
        for a in self.alternatives:
            if (a.field, a.period, a.as_of, a.unit) != (self.field, self.period, self.as_of, self.unit) or a.input_id == self.input_id:
                raise InputError("Alternatives must retain same target identity and distinct candidate IDs")
        if len({a.input_id for a in self.alternatives}) != len(self.alternatives):
            raise InputError("Duplicate alternative identity")


@dataclass(frozen=True)
class AnnualBundle:
    bundle_id: str
    version: int
    period: Period
    inputs: tuple[InputValue, ...]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.bundle_id)
        if type(self.version) is not int or self.version < 1 or type(self.period) is not Period:
            raise InputError("Explicit version and annual period required")
        if self.period.cik in SPECIALIZED_CIKS:
            raise InputError("Specialized issuer excluded from generic preparation contract")
        _typed(self.inputs, InputValue)
        _strings(self.limitations)
        by_id = {v.input_id: v for v in self.inputs}
        if len(by_id) != len(self.inputs) or any(v.period != self.period for v in self.inputs):
            raise InputError("Duplicate input or cross-period bundle")
        if {v.field for v in self.inputs} != set(Field):
            raise InputError("Every required field must have a value or explicit unavailable entry")
        for v in self.inputs:
            if v.formula is None:
                continue
            if v.input_id in v.formula.operands or any(o not in by_id for o in v.formula.operands):
                raise InputError("Exact retained operands required; no self reference")
            operands = [by_id[o] for o in v.formula.operands]
            source_ids = {s.source_id for item in self.inputs for s in item.sources}
            if any(ref not in source_ids for ref in v.formula.scope_evidence_ids):
                raise InputError("Formula scope references must bind retained evidence")
            if any(o.value is None for o in operands):
                raise InputError("Missing operands cannot yield a derived value")
            if v.formula.kind is FormulaKind.OPERATING_EXPENSE_BRIDGE:
                if (len(operands) < 2 or operands[0].field is not Field.REVENUE or
                        any(o.scope_status is not Scope.OPERATING_ONLY or o.role != "operating_expense"
                            for o in operands[1:])):
                    raise InputError("Revenue followed by explicitly operating-only expense operands required")
            if v.formula.kind in (FormulaKind.COMPONENT_TOTAL, FormulaKind.OPERATING_EXPENSE_BRIDGE):
                keys = [k for o in operands for k in o.coverage_keys]
                if any(not o.coverage_keys for o in operands) or len(keys) != len(set(keys)):
                    raise InputError("Component totals require explicit non-overlapping coverage keys")
                if v.completeness is Completeness.COMPLETE and any(o.completeness is not Completeness.COMPLETE for o in operands):
                    raise InputError("Incomplete operands cannot establish complete coverage")
        visiting, visited = set(), set()
        def visit(key: str) -> None:
            if key in visiting:
                raise InputError("Cyclic derivation provenance")
            if key in visited:
                return
            visiting.add(key)
            f = by_id[key].formula
            for operand in (() if f is None else f.operands):
                visit(operand)
            visiting.remove(key)
            visited.add(key)
        for key in by_id:
            visit(key)

    @property
    def unresolved_required_fields(self) -> tuple[Field, ...]:
        return tuple(f for f in Field if any(v.field is f and
                     (v.value is None or v.unresolved_requirements) for v in self.inputs))


@dataclass(frozen=True)
class HistoryBundle:
    history_id: str
    version: int
    cik: int
    annuals: tuple[AnnualBundle, ...]
    history_exceptions: tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.history_id)
        if type(self.version) is not int or self.version < 1 or type(self.cik) is not int or self.cik <= 0 or self.cik in SPECIALIZED_CIKS:
            raise InputError("Eligible issuer and explicit version required")
        _typed(self.annuals, AnnualBundle)
        _strings(self.history_exceptions)
        periods = [a.period for a in self.annuals]
        if (len(periods) > 5 or any(p.cik != self.cik for p in periods)
                or len(set(p.accession for p in periods)) != len(periods)
                or len({a.bundle_id for a in self.annuals}) != len(periods)):
            raise InputError("Unique exact issuer filings, at most five annual periods")
        if any(a.annual_end >= b.annual_start for a, b in zip(periods, periods[1:])):
            raise InputError("Chronological non-overlapping annual periods required")
        if len(periods) < 5 and not self.history_exceptions:
            raise InputError("Short/empty history requires explicit exception, never fabricated periods")


def coverage(history: HistoryBundle) -> dict[str, dict[str, int]]:
    """Count field/origin/completeness entries, not scores or financial sufficiency."""
    if type(history) is not HistoryBundle:
        raise InputError("History bundle required")
    result = {}
    for f in Field:
        rows = [v for a in history.annuals for v in a.inputs if v.field is f]
        result[f.value] = {"entries": len(rows), "available": sum(v.value is not None for v in rows)}
        for cls in (Origin, Completeness):
            for status in cls:
                result[f.value][status.value if cls is Origin else "completeness:" + status.value] = sum(
                    (v.origin if cls is Origin else v.completeness) is status for v in rows)
    return result


_TYPES = {c.__name__: c for c in (Period, Artifact, Receipt, ManualIdentity, SourceReference,
                                 Formula, InputValue, AnnualBundle, HistoryBundle)}
_ENUMS = {c.__name__: c for c in (Field, Origin, Quality, Completeness, Review, Scope, FormulaKind)}


def _encode(v):
    if type(v) in _TYPES.values():
        return {"type": type(v).__name__, "fields": {f.name: _encode(getattr(v, f.name)) for f in fields(v)}}
    if type(v) in _ENUMS.values():
        return {"enum": type(v).__name__, "value": v.value}
    if type(v) is Decimal:
        return {"decimal": str(v)}
    if type(v) is date:
        return {"date": v.isoformat()}
    if type(v) is bytes:
        return {"bytes": base64.b64encode(v).decode("ascii")}
    if type(v) is tuple:
        return [_encode(x) for x in v]
    if v is None or type(v) in (str, int, bool):
        return v
    raise InputError("Unsupported serialization type")


def _decode(v):
    if type(v) is list:
        return tuple(_decode(x) for x in v)
    if type(v) is not dict:
        if v is None or type(v) in (str, int, bool):
            return v
        raise InputError("Unsupported serialized scalar")
    if set(v) == {"type", "fields"} and v["type"] in _TYPES:
        cls = _TYPES[v["type"]]
        if type(v["fields"]) is not dict or set(v["fields"]) != {f.name for f in fields(cls)}:
            raise InputError("Exact schema fields required")
        return cls(**{k: _decode(x) for k, x in v["fields"].items()})
    if set(v) == {"enum", "value"} and v["enum"] in _ENUMS:
        return _ENUMS[v["enum"]](v["value"])
    if set(v) == {"decimal"} and type(v["decimal"]) is str:
        return Decimal(v["decimal"])
    if set(v) == {"date"}:
        return date.fromisoformat(v["date"])
    if set(v) == {"bytes"}:
        return base64.b64decode(v["bytes"], validate=True)
    raise InputError("Unknown serialization shape")


def serialize(bundle: HistoryBundle) -> str:
    if type(bundle) is not HistoryBundle:
        raise InputError("Isolated history bundle required")
    return json.dumps({"schema": SCHEMA, "bundle": _encode(bundle)}, sort_keys=True, separators=(",", ":"))


def deserialize(payload: str) -> HistoryBundle:
    try:
        def unique(pairs):
            result = {}
            for k, v in pairs:
                if k in result:
                    raise InputError("Duplicate serialized key")
                result[k] = v
            return result
        envelope = json.loads(payload, object_pairs_hook=unique)
        if type(envelope) is not dict or set(envelope) != {"schema", "bundle"} or envelope["schema"] != SCHEMA:
            raise InputError("Separate versioned preparation schema required")
        result = _decode(envelope["bundle"])
        if type(result) is not HistoryBundle:
            raise InputError("History bundle required")
        return result
    except (ValueError, TypeError, KeyError) as exc:
        raise InputError("Invalid preparation serialization") from exc
