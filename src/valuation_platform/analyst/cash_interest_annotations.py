"""Two reviewed nonnumeric sidecars; no interest aggregation or consumption gate.

Parent models and serializers are unchanged. The parent module's exact registry
builders are reused read-only to verify existing models without copying bodies
into the sidecar JSON or relaxing the original reviewed contract.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from valuation_platform.analyst import cash_flow_inputs as cf


class AnnotationError(ValueError):
    """An attachment cannot be verified; parent financial values are unaffected."""


class AnnotationConflict(AnnotationError):
    """Contradictory assertions or unselected multiple versions; never merged."""


class AssertionState(str, Enum):
    SUPPORTED = "evidence_supported"
    UNRESOLVED = "unresolved_scope"
    UNAVAILABLE = "unavailable_disclosure"


class AttachmentState(str, Enum):
    VALIDATED = "validated"
    NOT_PROVIDED = "not_provided"
    INVALID = "invalid"
    CONFLICTING = "conflicting"


def _strings(*values):
    if any(type(v) is not str or not v.strip() for v in values):
        raise AnnotationError("Explicit nonempty text required")


def _entries(values, cls):
    if type(values) is not tuple or not values or any(type(v) is not cls for v in values):
        raise AnnotationError("Immutable typed entries required")
    if cls is str:
        _strings(*values)


@dataclass(frozen=True)
class Subject:
    kind: str
    identity: str

    def __post_init__(self):
        if type(self.kind) is not str or self.kind not in ("reported_input", "bundle_unknown", "research_only"):
            raise AnnotationError("Unknown subject type")
        if type(self.identity) is not str or not self.identity.strip():
            raise AnnotationError("Exact subject identity required")


@dataclass(frozen=True)
class TextEvidence:
    evidence_id: str
    section: str
    primary: cf.Receipt
    locator: str
    primary_offset: int
    extraction_version: str
    text_block_namespace: str | None
    text_block_concept: str | None
    text_block_context: str | None
    text_block_ordinal: int | None

    def __post_init__(self):
        _strings(self.evidence_id, self.section, self.locator, self.extraction_version)
        if type(self.primary) is not cf.Receipt or type(self.primary_offset) is not int or self.primary_offset < 0:
            raise AnnotationError("Typed source receipt and text offset required")
        if self.text_block_ordinal is None:
            if any(v is not None for v in (self.text_block_namespace, self.text_block_concept, self.text_block_context)):
                raise AnnotationError("Incomplete optional text-block binding")
        else:
            _strings(self.text_block_namespace, self.text_block_concept, self.text_block_context)
            if type(self.text_block_ordinal) is not int or self.text_block_ordinal < 0:
                raise AnnotationError("Exact text-block ordinal required")


@dataclass(frozen=True)
class ResearchEvidence:
    evidence_id: str
    subject: Subject
    occurrence: cf.Occurrence
    instance: cf.Receipt
    evidence_ids: tuple[str, ...]
    rationale: str

    def __post_init__(self):
        _strings(self.evidence_id, self.rationale)
        _entries(self.evidence_ids, str)
        if (type(self.subject) is not Subject or self.subject.kind != "research_only"
                or type(self.occurrence) is not cf.Occurrence or type(self.instance) is not cf.Receipt):
            raise AnnotationError("Research evidence is not a reported input")


@dataclass(frozen=True)
class InputAnnotation:
    assertion_id: str
    subject: Subject
    binding: cf.ReportedInput
    instance: cf.Receipt
    claim: str
    state: AssertionState
    rationale: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self):
        _strings(self.assertion_id, self.claim, self.rationale)
        _entries(self.evidence_ids, str)
        if (type(self.subject) is not Subject or self.subject.kind != "reported_input"
                or type(self.binding) is not cf.ReportedInput or type(self.instance) is not cf.Receipt
                or type(self.state) is not AssertionState):
            raise AnnotationError("Typed reported-input annotation required")


@dataclass(frozen=True)
class ScopeUnknown:
    issue_id: str
    subject: Subject
    affected_subjects: tuple[Subject, ...]
    state: AssertionState
    reason: str
    evidence_ids: tuple[str, ...]
    reopening_requirement: str
    value_usd: None = None

    def __post_init__(self):
        _strings(self.issue_id, self.reason, self.reopening_requirement)
        _entries(self.affected_subjects, Subject)
        _entries(self.evidence_ids, str)
        if (type(self.subject) is not Subject or self.subject.kind != "bundle_unknown"
                or type(self.state) is not AssertionState or self.state is AssertionState.SUPPORTED
                or self.value_usd is not None):
            raise AnnotationError("Unknown issue is not an amount or resolved assertion")


@dataclass(frozen=True)
class Relation:
    relation_id: str
    subjects: tuple[Subject, ...]
    claim: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self):
        _strings(self.relation_id, self.claim)
        _entries(self.subjects, Subject)
        _entries(self.evidence_ids, str)


_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _ROOT / "docs/company-data-preparation/msft-cash-interest-annotations.json"
_REGISTRY_SHA256 = "5d01dfc0880fa38f7d421f7ee75fb7ed57e6b346f9984e2ec979d0a124d719bc"
_PARENT_SHA256 = "c3c35e020066f0887d9d8fe493f975afe9e6f0ea4b1785d2f341691ebb49d993"
_CONTRACT = "reviewed-msft-cash-interest-scope-annotations"
_SCHEMA = "cash-interest-scope-annotations-v1"
_EXTRACTION = "html-text-nodes-whitespace-v1"


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AnnotationError("Duplicate JSON key")
        result[key] = value
    return result


def _registry():
    body = _REGISTRY_PATH.read_bytes()
    if hashlib.sha256(body).hexdigest() != _REGISTRY_SHA256:
        raise AnnotationError("Immutable annotation registry changed")
    return json.loads(body, object_pairs_hook=_unique)


def _spec(identity):
    doc = _registry()
    for spec in doc["sets"]:
        if spec["annotation_id"] == identity:
            return doc, spec
    raise AnnotationError("Only two exact reviewed annotation sets registered")


def registered_annotation_ids() -> tuple[str, ...]:
    return tuple(s["annotation_id"] for s in _registry()["sets"])


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def _text(body):
    """Deterministic text nodes, not rendering or a new digest representation."""
    parser = _Text()
    parser.feed(body.decode("utf-8") if type(body) is bytes else body)
    return " ".join(" ".join(parser.parts).split())


def _receipt_view(receipt):
    a = receipt.artifact
    return {"source_url": a.url, "accession": a.accession,
            "representation": a.representation, "digest_type": a.digest_type,
            "sha256": a.sha256, "byte_length": receipt.byte_length,
            "retrieved_at_utc": receipt.retrieved_at_utc,
            "http_status": receipt.http_status, "retrieval_mode": receipt.retrieval_mode}


def _input_view(i):
    return {"input_id": i.input_id, "kind": i.kind.value,
            "source_kind": i.source_kind, "value_usd": str(i.value_usd),
            "display_multiplier": i.display_multiplier,
            "location_and_scope": i.location_and_scope,
            "occurrences": [cf._occurrence_dict(o) for o in i.occurrences]}


def _parent_view(parent):
    return {"bundle_id": parent.bundle_id, "version": parent.version,
            "registry_sha256": _PARENT_SHA256,
            "period": {"cik": parent.period.cik, "accession": parent.period.accession,
                       "annual_start": parent.period.annual_start.isoformat(),
                       "annual_end": parent.period.annual_end.isoformat(), "form": parent.period.form},
            "artifacts": [_receipt_view(r) for r in parent.artifacts]}


def _verify_parent(parent):
    if type(parent) is not cf.ReportedCashFlowBundle:
        raise AnnotationError("Verified parent and original bodies required")
    if hashlib.sha256(cf._REGISTRY_PATH.read_bytes()).hexdigest() != _PARENT_SHA256:
        raise AnnotationError("Parent registry differs from reviewed identity")
    doc, spec = cf._spec(parent.bundle_id)
    for key in ("inventory", "artifact_manifest"):
        if hashlib.sha256((_ROOT / doc[key + "_path"]).read_bytes()).hexdigest() != doc[key + "_sha256"]:
            raise AnnotationError("Parent inventory/manifest identity changed")
    if len(parent.artifacts) != len(spec["artifacts"]):
        raise AnnotationError("Both original parent receipts required")
    for receipt, ref in zip(parent.artifacts, spec["artifacts"]):
        # Reconstruct Artifact/Receipt to recheck raw bytes and typed metadata.
        if receipt != cf._receipt(ref, receipt.artifact.body):
            raise AnnotationError("Exact parent original-byte receipts required")
    # Frozen dataclasses are not a substitute for checking callers that bypass
    # construction (including numeric/enum type coercion in a forged parent).
    for value in parent.inputs:
        value.__post_init__()
        for occurrence in value.occurrences:
            occurrence.__post_init__()
    for unknown in parent.unknowns:
        unknown.__post_init__()
    if parent != cf._build(doc, spec, parent.artifacts):
        raise AnnotationError("Parent values/roles/occurrences differ from review")


@dataclass(frozen=True)
class CashInterestAnnotations:
    annotation_id: str
    version: str
    parent: cf.ReportedCashFlowBundle
    review_author: str
    reviewed_on: date
    evidence_reference: str
    evidence: tuple[TextEvidence, ...]
    research: tuple[ResearchEvidence, ...]
    annotations: tuple[InputAnnotation, ...]
    unknowns: tuple[ScopeUnknown, ...]
    relations: tuple[Relation, ...]
    limitations: tuple[str, ...]
    certified_interest_total: bool = False
    summation_authorized: bool = False
    valuation_consumption_approved: bool = False
    is_complete_operating_nwc: bool = False

    def __post_init__(self):
        try:
            for seq, cls in ((self.evidence, TextEvidence), (self.research, ResearchEvidence),
                             (self.annotations, InputAnnotation), (self.unknowns, ScopeUnknown),
                             (self.relations, Relation), (self.limitations, str)):
                if type(seq) is not tuple or not seq or any(type(v) is not cls for v in seq):
                    raise AnnotationError("Immutable typed complete annotation tuples required")
            if any(flag is not False for flag in (self.certified_interest_total, self.summation_authorized,
                                                  self.valuation_consumption_approved, self.is_complete_operating_nwc)):
                raise AnnotationError("Certification and summation are prohibited")
            if any(u.value_usd is not None for u in self.unknowns):
                raise AnnotationError("Unknowns are never amounts or zeros")
            ids = [a.assertion_id for a in self.annotations]
            if len(ids) != len(set(ids)):
                raise AnnotationConflict("Duplicate/conflicting assertion identities")
            doc, spec = _spec(self.annotation_id)
            _verify_parent(self.parent)
            _verify_evidence(self)
            if _canonical(_view(self)) != _canonical(spec):
                raise AnnotationError("Annotation binding/scope/unknowns differ from exact review")
            if doc["contract"] != _CONTRACT or doc["version"] != "1":
                raise AnnotationError("Unknown reviewed contract/version")
        except AnnotationError:
            raise
        except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, ET.ParseError) as exc:
            raise AnnotationError("Invalid parent/evidence/annotation structure") from exc


def _view(sidecar):
    return {"annotation_id": sidecar.annotation_id, "version": sidecar.version,
            "parent": _parent_view(sidecar.parent), "review_author": sidecar.review_author,
            "reviewed_on": sidecar.reviewed_on.isoformat(), "evidence_reference": sidecar.evidence_reference,
            "evidence": [{**{k: v for k, v in asdict(e).items() if k != "primary"},
                          "primary_sha256": e.primary.artifact.sha256} for e in sidecar.evidence],
            "research": [{"evidence_id": e.evidence_id, "subject": asdict(e.subject),
                          "occurrence": cf._occurrence_dict(e.occurrence),
                          "instance_sha256": e.instance.artifact.sha256,
                          "evidence_ids": list(e.evidence_ids), "rationale": e.rationale}
                         for e in sidecar.research],
            "annotations": [{"assertion_id": a.assertion_id, "subject": asdict(a.subject),
                             "binding": _input_view(a.binding), "instance_sha256": a.instance.artifact.sha256,
                             "claim": a.claim, "state": a.state.value, "rationale": a.rationale,
                             "evidence_ids": list(a.evidence_ids)} for a in sidecar.annotations],
            "unknowns": [{**asdict(u), "state": u.state.value} for u in sidecar.unknowns],
            "relations": [asdict(r) for r in sidecar.relations], "limitations": list(sidecar.limitations),
            "certified_interest_total": sidecar.certified_interest_total,
            "summation_authorized": sidecar.summation_authorized,
            "valuation_consumption_approved": sidecar.valuation_consumption_approved,
            "is_complete_operating_nwc": sidecar.is_complete_operating_nwc}


def _verify_evidence(sidecar):
    primary, instance = sidecar.parent.artifacts
    source = cf._instance(sidecar.parent.artifacts, sidecar.parent.period)
    root, contexts, _, _ = source
    text = _text(primary.artifact.body)
    for e in sidecar.evidence:
        if (e.primary != primary or e.extraction_version != _EXTRACTION
                or type(e.primary_offset) is not int or e.primary_offset < 0
                or not e.locator or text[e.primary_offset:e.primary_offset + len(e.locator)] != e.locator):
            raise AnnotationError("Exact primary-body text locator required")
        if e.text_block_ordinal is not None:
            if type(e.text_block_ordinal) is not int or e.text_block_ordinal < 0:
                raise AnnotationError("Exact text-block ordinal required")
            f = root[e.text_block_ordinal]
            if (f.tag != "{" + e.text_block_namespace + "}" + e.text_block_concept
                    or f.attrib["contextRef"] != e.text_block_context
                    or cf._context(contexts[e.text_block_context]) !=
                    (sidecar.parent.period.cik, sidecar.parent.period.annual_start, sidecar.parent.period.annual_end)
                    or e.locator not in _text(f.text)):
                raise AnnotationError("Locator must agree with selected note/context")
    for r in sidecar.research:
        o = r.occurrence
        if (r.instance != instance or cf._occurrences(*source, o.namespace, o.concept,
                                                    sidecar.parent.period, o.start is None) != (o,)):
            raise AnnotationError("Exact research-only occurrence required")
    for a in sidecar.annotations:
        if (a.instance != instance or a.subject != Subject("reported_input", a.binding.input_id)
                or a.binding != sidecar.parent.input(a.binding.input_id)):
            raise AnnotationError("Exact parent input/instance binding required")
    # Closed registry comparison below also checks subject/relationship references,
    # controlled claims, evidence IDs, complete issue lists and all locators.


def _build(spec, parent):
    primary, instance = parent.artifacts
    evidence = tuple(TextEvidence(**{k: v for k, v in e.items() if k != "primary_sha256"}, primary=primary)
                     for e in spec["evidence"])
    research = []
    for e in spec["research"]:
        o = e["occurrence"]
        research.append(ResearchEvidence(e["evidence_id"], Subject(**e["subject"]),
                       cf.Occurrence(**{**o, "start": date.fromisoformat(o["start"]) if o["start"] else None,
                                        "end": date.fromisoformat(o["end"]), "dimensions": tuple(o["dimensions"])}),
                       instance, tuple(e["evidence_ids"]), e["rationale"]))
    annotations = tuple(InputAnnotation(a["assertion_id"], Subject(**a["subject"]),
                        parent.input(a["binding"]["input_id"]), instance, a["claim"], AssertionState(a["state"]),
                        a["rationale"], tuple(a["evidence_ids"])) for a in spec["annotations"])
    unknowns = tuple(ScopeUnknown(u["issue_id"], Subject(**u["subject"]),
                     tuple(Subject(**s) for s in u["affected_subjects"]), AssertionState(u["state"]),
                     u["reason"], tuple(u["evidence_ids"]), u["reopening_requirement"], u["value_usd"])
                     for u in spec["unknowns"])
    relations = tuple(Relation(r["relation_id"], tuple(Subject(**s) for s in r["subjects"]),
                              r["claim"], tuple(r["evidence_ids"])) for r in spec["relations"])
    return CashInterestAnnotations(spec["annotation_id"], spec["version"], parent,
             spec["review_author"], date.fromisoformat(spec["reviewed_on"]), spec["evidence_reference"],
             evidence, tuple(research), annotations, unknowns, relations, tuple(spec["limitations"]))


def load_msft_annotations(annotation_id: str, parent: cf.ReportedCashFlowBundle) -> CashInterestAnnotations:
    """Explicit opt-in; does not retrieve evidence or auto-load missing attachments."""
    try:
        _, spec = _spec(annotation_id)
        return _build(spec, parent)
    except AnnotationError:
        raise
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        raise AnnotationError("Cannot bind reviewed annotation set") from exc


def serialize(sidecar: CashInterestAnnotations) -> str:
    if type(sidecar) is not CashInterestAnnotations:
        raise AnnotationError("Verified annotation set required")
    # Revalidate even if a caller bypassed dataclass frozen protection.
    sidecar.__post_init__()
    return _canonical({"schema": _SCHEMA, "contract": _CONTRACT, "version": "1",
                       "registry_sha256": _REGISTRY_SHA256, "annotations": _view(sidecar)})


def deserialize(payload: str, parent: cf.ReportedCashFlowBundle) -> CashInterestAnnotations:
    """Closed sidecar schema; caller must supply the original verified parent."""
    try:
        data = json.loads(payload, object_pairs_hook=_unique)
        if (set(data) != {"schema", "contract", "version", "registry_sha256", "annotations"}
                or data["schema"] != _SCHEMA or data["contract"] != _CONTRACT
                or data["version"] != "1" or data["registry_sha256"] != _REGISTRY_SHA256):
            raise AnnotationError("Unknown or malformed sidecar serialization")
        value = data["annotations"]
        seen = {}
        for a in value["annotations"]:
            if a["assertion_id"] in seen and _canonical(a) != seen[a["assertion_id"]]:
                raise AnnotationConflict("Conflicting assertions; no merge")
            seen[a["assertion_id"]] = _canonical(a)
        _, spec = _spec(value["annotation_id"])
        if _canonical(value) != _canonical(spec):
            raise AnnotationError("Serialized identity/scope/precision/unknowns differ from review")
        return _build(spec, parent)
    except AnnotationError:
        raise
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        raise AnnotationError("Invalid serialized annotation attachment") from exc


@dataclass(frozen=True)
class AttachmentResult:
    state: AttachmentState
    annotations: CashInterestAnnotations | None
    identities: tuple[str, ...]
    reasons: tuple[str, ...]


def attach(payloads: tuple[str, ...], parent: cf.ReportedCashFlowBundle) -> AttachmentResult:
    """All-or-nothing diagnostic; absent attachments never create defaults."""
    if type(payloads) is not tuple or any(type(p) is not str for p in payloads):
        return AttachmentResult(AttachmentState.INVALID, None, (), ("Immutable string payload tuple required",))
    if not payloads:
        return AttachmentResult(AttachmentState.NOT_PROVIDED, None, (), ("No annotation supplied",))
    identities = []
    for payload in payloads:
        try:
            a = json.loads(payload, object_pairs_hook=_unique)["annotations"]
            identities.append(str(a["annotation_id"]) + "/" + str(a["version"]))
        except (ValueError, KeyError, TypeError):
            identities.append("malformed_attachment")
    if len(payloads) != 1:
        return AttachmentResult(AttachmentState.CONFLICTING, None, tuple(identities),
                                ("Multiple attachments/versions supplied; select explicitly, never merge",))
    try:
        result = deserialize(payloads[0], parent)
        return AttachmentResult(AttachmentState.VALIDATED, result, tuple(identities), ())
    except AnnotationConflict as exc:
        return AttachmentResult(AttachmentState.CONFLICTING, None, tuple(identities), (str(exc),))
    except AnnotationError as exc:
        return AttachmentResult(AttachmentState.INVALID, None, tuple(identities), (str(exc),))
