"""Pure, explicitly scoped analyst NWC arithmetic; never policy/FCFF approval."""

from __future__ import annotations

import base64
from dataclasses import dataclass, fields
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, localcontext
from enum import Enum
import hashlib
from io import BytesIO
import json
import re
import xml.etree.ElementTree as ET


class AnalystNWCError(ValueError):
    """Invalid evidence, scope, arithmetic or period linkage."""


class EvidenceKind(str, Enum):
    REPORTED = "reported"
    SEC_DERIVED = "sec_supported_derivation"
    CLASSIFICATION = "analyst_classification"
    ESTIMATE = "analyst_estimate"
    MANUAL = "manual_input"
    EXTERNAL = "external_input"


class Treatment(str, Enum):
    REQUIRED = "required"
    OUTSIDE = "outside_perimeter"


def _text(value: object) -> None:
    if type(value) is not str or not value.strip():
        raise AnalystNWCError("Nonempty explicit identity/rationale required")


def _strings(value: object, *, required: bool = True) -> None:
    if type(value) is not tuple or (required and not value):
        raise AnalystNWCError("Immutable explicit string tuple required")
    for item in value:
        _text(item)
    if len(set(value)) != len(value):
        raise AnalystNWCError("Duplicate identity/reference")


@dataclass(frozen=True)
class Period:
    cik: int
    accession: str
    annual_start: date
    annual_end: date
    form: str = "10-K"

    def __post_init__(self) -> None:
        if type(self.cik) is not int or self.cik <= 0:
            raise AnalystNWCError("Positive exact CIK required")
        if type(self.accession) is not str or not re.fullmatch(r"\d{10}-\d{2}-\d{6}", self.accession):
            raise AnalystNWCError("Exact accession required")
        if (type(self.annual_start) is not date or type(self.annual_end) is not date
                or self.annual_start > self.annual_end or self.form != "10-K"):
            raise AnalystNWCError("Valid exact non-amended annual period required")


@dataclass(frozen=True)
class Amount:
    lower: Decimal
    upper: Decimal
    dependencies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if any(type(v) is not Decimal or not v.is_finite() for v in (self.lower, self.upper)):
            raise AnalystNWCError("Finite exact Decimal endpoints required")
        if self.lower > self.upper:
            raise AnalystNWCError("Reversed interval")
        _strings(self.dependencies, required=self.lower != self.upper)

    @classmethod
    def point(cls, value: Decimal) -> Amount:
        return cls(value, value)


def _sum(terms: tuple[tuple[Amount, int], ...]) -> Amount:
    values = [v for amount, _ in terms for v in (amount.lower, amount.upper)]
    # Do not allow the ambient Decimal context to round reported arithmetic.
    with localcontext() as ctx:
        ctx.prec = max(28, sum(len(v.as_tuple().digits) + abs(v.as_tuple().exponent)
                               for v in values) + 10)
        lower = sum((a.lower if sign == 1 else -a.upper for a, sign in terms), Decimal(0))
        upper = sum((a.upper if sign == 1 else -a.lower for a, sign in terms), Decimal(0))
    dependencies = tuple(sorted({d for a, _ in terms for d in a.dependencies}))
    return Amount(lower, upper, dependencies)


@dataclass(frozen=True)
class Artifact:
    url: str
    accession: str
    representation: str
    digest_type: str
    sha256: str
    body: bytes

    def __post_init__(self) -> None:
        _text(self.accession)
        if not isinstance(self.url, str) or not re.fullmatch(
                r"https://www\.sec\.gov/Archives/edgar/data/[0-9]+/" +
                re.escape(self.accession.replace("-", "")) + r"/[^/?#]+", self.url):
            raise AnalystNWCError("Exact selected-accession SEC artifact URL required")
        _text(self.accession)
        if (self.representation != "sec_response_body_bytes"
                or self.digest_type != "sha256_sec_response_body_bytes"
                or type(self.body) is not bytes or not self.body
                or hashlib.sha256(self.body).hexdigest() != self.sha256):
            raise AnalystNWCError("Original response representation/digest mismatch")


def _verify_occurrences(evidence: Evidence) -> None:
    """Bind supplied instant facts to verified instance bytes, not parsed equality."""
    xi = "{http://www.xbrl.org/2003/instance}"
    matched = False
    for artifact in evidence.artifacts:
        if not artifact.url.endswith("_htm.xml"):
            continue
        if b"<!DOCTYPE" in artifact.body.upper() or b"<!ENTITY" in artifact.body.upper():
            raise AnalystNWCError("Unsafe instance")
        try:
            root = ET.fromstring(artifact.body)
            namespaces = dict(item for _, item in ET.iterparse(BytesIO(artifact.body), events=["start-ns"]))
            if root.tag != xi + "xbrl":
                raise AnalystNWCError("Not an extracted XBRL instance")
            contexts = {c.attrib["id"]: c for c in root.findall(xi + "context")}
            units = {u.attrib["id"]: u for u in root.findall(xi + "unit")}
            annuals = set()
            for f in root:
                if f.tag.startswith("{http://xbrl.sec.gov/dei/") and f.tag.endswith("}DocumentFiscalPeriodFocus") and f.text == "FY":
                    c = contexts[f.attrib["contextRef"]]
                    if (int(c.findtext(".//" + xi + "identifier")) == evidence.period.cik
                            and c.findtext(xi + "period/" + xi + "endDate") == evidence.period.annual_end.isoformat()
                            and c.find(".//" + xi + "segment") is None and c.find(".//" + xi + "scenario") is None):
                        annuals.add(c.findtext(xi + "period/" + xi + "startDate"))
            if annuals != {evidence.period.annual_start.isoformat()}:
                raise AnalystNWCError("Source annual context does not match exact period")
            all_occurrences = evidence.occurrences + evidence.competing_occurrences
            expected = set()
            qname = "{" + evidence.occurrences[0].namespace + "}" + evidence.occurrences[0].concept
            for ordinal, f in enumerate(root):
                if f.tag != qname:
                    continue
                c = contexts[f.attrib["contextRef"]]
                if (int(c.findtext(".//" + xi + "identifier")) != evidence.period.cik
                        or c.findtext(xi + "period/" + xi + "instant") != evidence.period.annual_end.isoformat()
                        or c.find(".//" + xi + "segment") is not None
                        or c.find(".//" + xi + "scenario") is not None):
                    continue
                u = units[f.attrib["unitRef"]]
                ms = list(u)
                if len(ms) != 1 or ms[0].tag != xi + "measure":
                    continue
                prefix, name = ms[0].text.split(":")
                if name != "USD" or namespaces[prefix] != "http://www.xbrl.org/2003/iso4217":
                    continue
                if f.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}nil", "false") not in ("false", "0"):
                    raise AnalystNWCError("Nil/numeric collision in eligible source facts")
                expected.add(ordinal)
            if expected != {o.ordinal for o in all_occurrences}:
                raise AnalystNWCError("Retain every confirming/competing eligible occurrence")
            for o in all_occurrences:
                fact = root[o.ordinal]
                context = contexts[o.context_id]
                unit = units[o.unit_id]
                measures = list(unit)
                if (fact.tag != "{" + o.namespace + "}" + o.concept
                        or fact.attrib.get("contextRef") != o.context_id
                        or fact.attrib.get("unitRef") != o.unit_id
                        or fact.text != o.raw_value or fact.attrib.get("decimals") != o.decimals
                        or fact.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}nil", "false") not in ("false", "0")
                        or int(context.findtext(".//" + xi + "identifier")) != o.entity_cik
                        or context.findtext(xi + "period/" + xi + "instant") != o.instant_end.isoformat()
                        or context.find(".//" + xi + "segment") is not None
                        or context.find(".//" + xi + "scenario") is not None
                        or len(measures) != 1 or measures[0].tag != xi + "measure"):
                    raise AnalystNWCError("Occurrence does not match source instance")
                measure = measures[0].text
                prefix, name = measure.split(":")
                if name != "USD" or namespaces[prefix] != "http://www.xbrl.org/2003/iso4217":
                    raise AnalystNWCError("Source unit is not exact USD")
            matched = True
        except (ET.ParseError, KeyError, IndexError, ValueError, TypeError, AttributeError) as exc:
            raise AnalystNWCError("Invalid source context/unit/fact linkage") from exc
    if not matched:
        raise AnalystNWCError("Reported occurrence requires verified source instance")


@dataclass(frozen=True)
class Occurrence:
    namespace: str
    concept: str
    context_id: str
    unit_id: str
    raw_value: str
    decimals: str
    ordinal: int
    entity_cik: int
    instant_end: date
    normalized_unit: str = "USD"
    dimensions: tuple[str, ...] = ()
    nil: bool = False

    def __post_init__(self) -> None:
        for value in (self.namespace, self.concept, self.context_id, self.unit_id,
                      self.raw_value, self.decimals):
            _text(value)
        if (type(self.ordinal) is not int or self.ordinal < 0
                or type(self.entity_cik) is not int or self.entity_cik <= 0
                or type(self.instant_end) is not date or self.normalized_unit != "USD"
                or type(self.dimensions) is not tuple or self.dimensions
                or type(self.nil) is not bool or self.nil):
            raise AnalystNWCError("Invalid nondimensional non-nil USD occurrence")
        if not re.fullmatch(r"INF|-?\d+", self.decimals):
            raise AnalystNWCError("Invalid submitted decimals")
        try:
            value = Decimal(self.raw_value)
        except Exception as exc:
            raise AnalystNWCError("Invalid raw numeric value") from exc
        if not value.is_finite():
            raise AnalystNWCError("Nonfinite occurrence")


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    kind: EvidenceKind
    period: Period
    author: str
    reviewed_on: date
    rationale: str
    references: tuple[str, ...]
    value: Amount | None
    precision: str
    artifacts: tuple[Artifact, ...] = ()
    occurrences: tuple[Occurrence, ...] = ()
    competing_occurrences: tuple[Occurrence, ...] = ()
    operands: tuple[Evidence, ...] = ()
    coefficients: tuple[int, ...] = ()
    assumptions: tuple[str, ...] = ()
    supersedes: Evidence | None = None

    def __post_init__(self) -> None:
        for item in (self.evidence_id, self.author, self.rationale, self.precision):
            _text(item)
        _strings(self.references)
        _strings(self.assumptions, required=False)
        if (type(self.kind) is not EvidenceKind or type(self.period) is not Period
                or type(self.reviewed_on) is not date
                or self.value is not None and type(self.value) is not Amount):
            raise AnalystNWCError("Invalid provenance types")
        for items, cls in ((self.artifacts, Artifact), (self.occurrences, Occurrence),
                           (self.competing_occurrences, Occurrence), (self.operands, Evidence)):
            if type(items) is not tuple or any(type(item) is not cls for item in items):
                raise AnalystNWCError("Immutable typed evidence required")
        if type(self.coefficients) is not tuple:
            raise AnalystNWCError("Immutable coefficients required")
        if any(a.accession != self.period.accession for a in self.artifacts):
            raise AnalystNWCError("Artifact/accession mismatch")
        if any(int(a.url.split("/data/")[1].split("/")[0]) != self.period.cik for a in self.artifacts):
            raise AnalystNWCError("Artifact/CIK mismatch")
        if self.kind in (EvidenceKind.REPORTED, EvidenceKind.SEC_DERIVED) and not self.artifacts:
            raise AnalystNWCError("SEC evidence requires verified original artifacts")
        if self.kind in (EvidenceKind.ESTIMATE, EvidenceKind.MANUAL, EvidenceKind.EXTERNAL):
            if not self.assumptions or self.value is None:
                raise AnalystNWCError("Explicit input assumptions/value required")
        if self.kind is EvidenceKind.CLASSIFICATION and self.value is not None:
            raise AnalystNWCError("Classification is not an amount")
        if self.kind is EvidenceKind.REPORTED:
            if self.value is None or self.value.lower != self.value.upper or not self.occurrences:
                raise AnalystNWCError("Reported evidence requires point/occurrences")
            if len({(o.namespace, o.concept) for o in self.occurrences}) != 1:
                raise AnalystNWCError("Different concepts cannot collapse")
        for o in self.occurrences:
            if (o.entity_cik != self.period.cik or o.instant_end != self.period.annual_end
                    or self.value is None or Decimal(o.raw_value) != self.value.lower
                    or self.value.lower != self.value.upper):
                raise AnalystNWCError("Occurrence/value/period mismatch")
        for o in self.competing_occurrences:
            if (self.kind is not EvidenceKind.REPORTED or o.entity_cik != self.period.cik
                    or o.instant_end != self.period.annual_end
                    or (o.namespace, o.concept) != (self.occurrences[0].namespace, self.occurrences[0].concept)
                    or Decimal(o.raw_value) == self.value.lower):
                raise AnalystNWCError("Invalid competing source occurrence")
        if tuple(sorted(o.ordinal for o in self.occurrences)) != tuple(o.ordinal for o in self.occurrences):
            raise AnalystNWCError("Occurrences must retain deterministic source order")
        if len({o.ordinal for o in self.occurrences}) != len(self.occurrences):
            raise AnalystNWCError("Duplicate occurrence identity")
        if (tuple(sorted(o.ordinal for o in self.competing_occurrences)) != tuple(o.ordinal for o in self.competing_occurrences)
                or len({o.ordinal for o in self.occurrences + self.competing_occurrences}) != len(self.occurrences + self.competing_occurrences)):
            raise AnalystNWCError("Invalid competing occurrence order/identity")
        if self.kind is EvidenceKind.REPORTED:
            _verify_occurrences(self)
        if self.kind is EvidenceKind.SEC_DERIVED:
            if (not self.operands or len(self.operands) != len(self.coefficients)
                    or any(o.period != self.period or o.value is None
                           or o.kind not in (EvidenceKind.REPORTED, EvidenceKind.SEC_DERIVED)
                           for o in self.operands)
                    or any(type(c) is not int or c not in (-1, 1) for c in self.coefficients)
                    or len({o.evidence_id for o in self.operands}) != len(self.operands)):
                raise AnalystNWCError("Explicit same-period SEC derivation operands required")
            if _sum(tuple((o.value, c) for o, c in zip(self.operands, self.coefficients))) != self.value:
                raise AnalystNWCError("Derivation does not reconcile")
            if any(o.competing_occurrences for o in self.operands):
                raise AnalystNWCError("Conflicting SEC operands cannot support a derivation")
        elif self.operands or self.coefficients:
            raise AnalystNWCError("Only SEC derivations accept arithmetic operands")
        if self.supersedes is not None:
            if (type(self.supersedes) is not Evidence or self.supersedes.period != self.period
                    or self.supersedes.evidence_id == self.evidence_id
                    or self.reviewed_on < self.supersedes.reviewed_on
                    or self.kind not in (EvidenceKind.ESTIMATE, EvidenceKind.MANUAL)):
                raise AnalystNWCError("Invalid override/original provenance")


@dataclass(frozen=True)
class Component:
    component_id: str
    coefficient: int
    treatment: Treatment
    scope_keys: tuple[str, ...]
    rationale: str
    evidence: tuple[Evidence, ...]
    allocation_ceiling: Decimal | None = None

    def __post_init__(self) -> None:
        _text(self.component_id)
        _text(self.rationale)
        _strings(self.scope_keys)
        if (type(self.coefficient) is not int or self.coefficient not in (-1, 1)
                or type(self.treatment) is not Treatment or type(self.evidence) is not tuple
                or any(type(e) is not Evidence for e in self.evidence)):
            raise AnalystNWCError("Explicit component treatment/evidence required")
        if self.treatment is Treatment.OUTSIDE and (not self.evidence or not any(
                e.kind is EvidenceKind.CLASSIFICATION for e in self.evidence)):
            raise AnalystNWCError("Omission requires classification provenance")
        if self.allocation_ceiling is not None:
            if type(self.allocation_ceiling) is not Decimal or not self.allocation_ceiling.is_finite() or self.allocation_ceiling < 0:
                raise AnalystNWCError("Invalid mixed-caption allocation ceiling")
            for e in self.evidence:
                if e.value is not None and not Decimal(0) <= e.value.lower <= e.value.upper <= self.allocation_ceiling:
                    raise AnalystNWCError("Allocation outside disclosed gross balance")


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    version: str
    perimeter_id: str
    period: Period
    components: tuple[Component, ...]
    limitations: tuple[str, ...]
    unresolved_effects: tuple[str, ...]

    def __post_init__(self) -> None:
        for v in (self.scenario_id, self.version, self.perimeter_id):
            _text(v)
        if type(self.period) is not Period or type(self.components) is not tuple or not self.components:
            raise AnalystNWCError("Explicit scenario period/components required")
        if any(type(c) is not Component for c in self.components):
            raise AnalystNWCError("Invalid component")
        _strings(self.limitations)
        _strings(self.unresolved_effects)
        ids = [c.component_id for c in self.components]
        keys = [k for c in self.components if c.treatment is Treatment.REQUIRED for k in c.scope_keys]
        if len(set(ids)) != len(ids) or len(set(keys)) != len(keys):
            raise AnalystNWCError("Duplicate/overlapping economic component scope")
        evidence = [e for c in self.components for e in c.evidence]
        if any(e.period != self.period for e in evidence):
            raise AnalystNWCError("No implicit extension across filings/periods")
        if len({e.evidence_id for e in evidence}) != len(evidence):
            raise AnalystNWCError("Evidence cannot be counted twice")


@dataclass(frozen=True)
class Result:
    scenario: Scenario
    status: str
    amount: Amount | None
    reasons: tuple[str, ...]
    assumption_dependent: bool
    is_complete_operating_nwc: bool = False
    fcff_ready: bool = False

    def __post_init__(self) -> None:
        if (type(self.scenario) is not Scenario or self.status not in (
                "partial_perimeter", "input_unavailable", "ambiguous_evidence")
                or type(self.assumption_dependent) is not bool
                or self.is_complete_operating_nwc is not False or self.fcff_ready is not False):
            raise AnalystNWCError("Only isolated, non-certified analyst results are supported")


def evaluate(scenario: Scenario) -> Result:
    """Compute only the explicitly selected partial book perimeter."""
    if type(scenario) is not Scenario:
        raise AnalystNWCError("Scenario required")
    terms = []
    reasons = []
    conflicting = False
    estimated = False
    for c in scenario.components:
        if c.treatment is Treatment.OUTSIDE:
            reasons.append("omitted:" + c.component_id)
            continue
        superseded = {e.supersedes.evidence_id for e in c.evidence if e.supersedes is not None}
        candidates = [e for e in c.evidence if e.value is not None and e.evidence_id not in superseded]
        if not candidates:
            reasons.append("unavailable:" + c.component_id)
            continue
        values = {e.value for e in candidates}
        if len(values) != 1 or any(e.competing_occurrences for e in candidates):
            conflicting = True
            reasons.append("conflicting:" + c.component_id)
            continue
        estimated |= any(e.kind in (EvidenceKind.ESTIMATE, EvidenceKind.MANUAL, EvidenceKind.EXTERNAL)
                         for e in candidates)
        if any(e.precision == "rounded" or any(o.decimals != "INF" and int(o.decimals) < 0
                                              for o in e.occurrences) for e in candidates):
            reasons.append("submitted_precision:" + c.component_id)
        terms.append((candidates[0].value, c.coefficient))
    status = "ambiguous_evidence" if conflicting else "input_unavailable" if any(
        r.startswith("unavailable:") for r in reasons) else "partial_perimeter"
    return Result(scenario, status, _sum(tuple(terms)) if status == "partial_perimeter" else None,
                  tuple(reasons), estimated)


@dataclass(frozen=True)
class Change:
    opening: Result | None
    closing: Result
    status: str
    amount: Amount | None
    unresolved_effects: tuple[str, ...]
    cash_investment_certified: bool = False


def change(opening: Result | None, closing: Result) -> Change:
    """Book scenario movement only; unknown cash effects remain exposed."""
    if type(closing) is not Result or evaluate(closing.scenario) != closing:
        raise AnalystNWCError("Closing result must reproduce")
    if opening is None:
        return Change(None, closing, "opening_unavailable", None, closing.scenario.unresolved_effects)
    if type(opening) is not Result or evaluate(opening.scenario) != opening:
        raise AnalystNWCError("Opening result must reproduce")
    a, b = opening.scenario, closing.scenario
    def perimeter(s: Scenario) -> tuple:
        return tuple((c.component_id, c.coefficient, c.treatment, c.scope_keys) for c in s.components)
    if ((a.period.cik, a.scenario_id, a.version, a.perimeter_id, perimeter(a)) !=
            (b.period.cik, b.scenario_id, b.version, b.perimeter_id, perimeter(b))
            or a.period.annual_end + timedelta(days=1) != b.period.annual_start
            or a.period.annual_end >= b.period.annual_end):
        raise AnalystNWCError("Nonadjacent periods or incompatible scenario/perimeter")
    effects = tuple(sorted(set(a.unresolved_effects + b.unresolved_effects)))
    if opening.amount is None or closing.amount is None:
        return Change(opening, closing, "input_unavailable", None, effects)
    return Change(opening, closing, "partial_book_movement",
                  _sum(((closing.amount, 1), (opening.amount, -1))), effects)


_TYPES = {c.__name__: c for c in (Period, Amount, Artifact, Occurrence, Evidence, Component, Scenario, Result, Change)}
_ENUMS = {c.__name__: c for c in (EvidenceKind, Treatment)}


def _encode(value: object) -> object:
    if type(value) in _TYPES.values():
        return {"type": type(value).__name__, "fields": {f.name: _encode(getattr(value, f.name)) for f in fields(value)}}
    if type(value) in _ENUMS.values():
        return {"enum": type(value).__name__, "value": value.value}
    if type(value) is Decimal:
        return {"decimal": str(value)}
    if type(value) is date:
        return {"date": value.isoformat()}
    if type(value) is bytes:
        return {"bytes": base64.b64encode(value).decode("ascii")}
    if type(value) is tuple:
        return [_encode(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise AnalystNWCError("Unsupported serialization type")


def _decode(value: object) -> object:
    if type(value) is list:
        return tuple(_decode(v) for v in value)
    if type(value) is not dict:
        return value
    if set(value) == {"type", "fields"} and value["type"] in _TYPES:
        cls = _TYPES[value["type"]]
        if type(value["fields"]) is not dict or set(value["fields"]) != {f.name for f in fields(cls)}:
            raise AnalystNWCError("Missing/unexpected serialized fields")
        return cls(**{k: _decode(v) for k, v in value["fields"].items()})
    if set(value) == {"enum", "value"} and value["enum"] in _ENUMS:
        return _ENUMS[value["enum"]](value["value"])
    if set(value) == {"decimal"}:
        return Decimal(value["decimal"])
    if set(value) == {"date"}:
        return date.fromisoformat(value["date"])
    if set(value) == {"bytes"}:
        return base64.b64decode(value["bytes"], validate=True)
    raise AnalystNWCError("Unknown serialization representation")


def serialize(scenario: Scenario) -> str:
    if type(scenario) is not Scenario:
        raise AnalystNWCError("Scenario required")
    return json.dumps({"analyst_schema_version": "1", "scenario": _encode(scenario)},
                      sort_keys=True, separators=(",", ":"))


def deserialize(payload: str) -> Scenario:
    try:
        doc = json.loads(payload)
        if set(doc) != {"analyst_schema_version", "scenario"} or doc["analyst_schema_version"] != "1":
            raise AnalystNWCError("Invalid isolated analyst schema")
        scenario = _decode(doc["scenario"])
        if type(scenario) is not Scenario:
            raise AnalystNWCError("Scenario required")
        return scenario
    except (ValueError, TypeError, KeyError, InvalidOperation) as exc:
        raise AnalystNWCError("Invalid serialized analyst provenance") from exc


def _validate_evaluation(result: Result | Change) -> None:
    if type(result) is Result and evaluate(result.scenario) == result:
        return
    if type(result) is Change and change(result.opening, result.closing) == result:
        return
    raise AnalystNWCError("Evaluation summary does not reproduce")


def serialize_evaluation(result: Result | Change) -> str:
    _validate_evaluation(result)
    return json.dumps({"analyst_schema_version": "1", "evaluation": _encode(result)},
                      sort_keys=True, separators=(",", ":"))


def deserialize_evaluation(payload: str) -> Result | Change:
    try:
        doc = json.loads(payload)
        if set(doc) != {"analyst_schema_version", "evaluation"} or doc["analyst_schema_version"] != "1":
            raise AnalystNWCError("Invalid isolated analyst schema")
        result = _decode(doc["evaluation"])
        _validate_evaluation(result)
        return result
    except (ValueError, TypeError, KeyError, InvalidOperation) as exc:
        raise AnalystNWCError("Invalid serialized analyst evaluation") from exc
