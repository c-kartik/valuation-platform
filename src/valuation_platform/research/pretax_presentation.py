"""Pure parsing and evidence models for the Pretax presentation diagnostic."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
import json
import re
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from valuation_platform.sec.annual_period import ResolvedAnnualPeriod
from valuation_platform.sec.filing_xbrl import SECFilingXBRL


TARGET_CONCEPT = (
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAnd"
    "IncomeLossFromEquityMethodInvestments"
)
XLINK = "http://www.w3.org/1999/xlink"
LINK = "http://www.xbrl.org/2003/linkbase"


class EvidenceOutcome(str, Enum):
    PRIMARY_STATEMENT_MEMBER = "PRIMARY_STATEMENT_MEMBER"
    DISCLOSURE_ONLY_MEMBER = "DISCLOSURE_ONLY_MEMBER"
    MULTIPLE_ROLE_MEMBERSHIP = "MULTIPLE_ROLE_MEMBERSHIP"
    NO_PRESENTATION_MEMBERSHIP = "NO_PRESENTATION_MEMBERSHIP"
    PRESENTATION_DATA_ERROR = "PRESENTATION_DATA_ERROR"
    EQUITY_METHOD_SCOPE_UNRESOLVED = "EQUITY_METHOD_SCOPE_UNRESOLVED"


class EquityMethodScope(str, Enum):
    INCLUDED_PRETAX = "INCLUDED_PRETAX"
    SEPARATE_PRETAX = "SEPARATE_PRETAX"
    SEPARATE_NET_OF_TAX = "SEPARATE_NET_OF_TAX"
    NO_MATERIAL_ACTIVITY_FOUND = "NO_MATERIAL_ACTIVITY_FOUND"
    UNRESOLVED = "UNRESOLVED"


class PolicyDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    NEEDS_MORE_RESEARCH = "NEEDS_MORE_RESEARCH"


class PresentationEvidenceError(ValueError):
    """Malformed or inconsistent diagnostic input."""


@dataclass(frozen=True)
class ArtifactInventory:
    directory_url: str
    index_url: str
    instance_name: str
    schema_names: tuple[str, ...]
    presentation_names: tuple[str, ...]
    filing_summary_name: str | None
    metalinks_name: str | None
    renderer_names: tuple[str, ...]
    all_names: tuple[str, ...]
    all_source_urls: tuple[str, ...]

    def source_url(self, name: str) -> str:
        return f"{self.directory_url}/{name}"


@dataclass(frozen=True)
class RoleDefinition:
    role_uri: str
    definition: str
    sort_code: str
    role_type: str
    title: str
    source_url: str


@dataclass(frozen=True)
class PresentationStep:
    parent_href: str
    child_href: str
    order: Decimal
    preferred_label: str | None


@dataclass(frozen=True)
class PresentationPath:
    root_href: str
    ancestor_hrefs: tuple[str, ...]
    candidate_href: str
    relationships: tuple[PresentationStep, ...]


@dataclass(frozen=True)
class RoleMembership:
    role: RoleDefinition
    paths: tuple[PresentationPath, ...]


@dataclass(frozen=True)
class CandidateFactEvidence:
    namespace: str
    concept: str
    context_id: str
    start: date
    end: date
    unit_ref: str | None
    unit_numerator_measures: tuple[str, ...]
    unit_denominator_measures: tuple[str, ...]
    dimensions: tuple[str, ...]
    value: Decimal
    accession_number: str
    source_url: str


@dataclass(frozen=True)
class RendererReport:
    role_uri: str | None
    report_id: str | None
    menu_category: str | None
    short_name: str | None
    long_name: str | None
    html_file_name: str | None
    source_url: str


@dataclass(frozen=True)
class RendererEvidence:
    reports: tuple[RendererReport, ...]
    metalinks_contains_candidate: bool | None
    renderer_files_containing_candidate: tuple[str, ...]
    source_urls: tuple[str, ...]
    error: str | None
    submitted_role_uris: tuple[str, ...] = ()
    renderer_matching_role_uris: tuple[str, ...] = ()
    renderer_missing_role_uris: tuple[str, ...] = ()


@dataclass(frozen=True)
class PeriodEvidenceResult:
    ticker: str
    cik: int
    accession_number: str
    form: str
    report_date: date
    primary_document: str
    annual_start: date | None
    annual_end: date | None
    candidate_facts: tuple[CandidateFactEvidence, ...]
    memberships: tuple[RoleMembership, ...]
    renderer: RendererEvidence
    outcomes: tuple[EvidenceOutcome, ...]
    equity_method_scope: EquityMethodScope
    policy_decision: PolicyDecision
    artifact_inventory: ArtifactInventory | None
    error: str | None


@dataclass(frozen=True)
class EquityMethodMatrixEntry:
    ticker: str
    candidate_periods: int
    scope: EquityMethodScope
    direct_evidence: str
    policy_decision: PolicyDecision = PolicyDecision.NEEDS_MORE_RESEARCH


def discover_artifacts(
    payload: Any,
    *,
    directory_url: str,
    primary_document: str,
) -> ArtifactInventory:
    """Discover every relevant artifact from one exact filing index."""
    names = _directory_names(payload)
    primary = _basename(primary_document, "primary document")
    lowered = primary.lower()
    suffix = ".html" if lowered.endswith(".html") else ".htm" if lowered.endswith(".htm") else None
    if suffix is None:
        raise PresentationEvidenceError("Primary document is not HTML")
    instance_name = f"{primary[:-len(suffix)]}_htm.xml"
    if names.count(instance_name) != 1:
        raise PresentationEvidenceError(
            "Exact primary-document extracted instance is missing or ambiguous"
        )
    schemas = tuple(sorted(name for name in names if name.lower().endswith(".xsd")))
    presentations = tuple(
        sorted(name for name in names if name.lower().endswith("_pre.xml"))
    )
    if not schemas:
        raise PresentationEvidenceError("Filing directory contains no submitted schema")
    if not presentations:
        raise PresentationEvidenceError(
            "Filing directory contains no submitted presentation linkbase"
        )
    summaries = tuple(name for name in names if name.lower() == "filingsummary.xml")
    metalinks = tuple(name for name in names if name.lower() == "metalinks.json")
    if len(summaries) > 1 or len(metalinks) > 1:
        raise PresentationEvidenceError("Renderer artifacts are ambiguous")
    renderer_names = tuple(
        sorted(name for name in names if re.fullmatch(r"R\d+\.(?:htm|html|xml)", name, re.I))
    )
    directory = directory_url.rstrip("/")
    if not directory.startswith("https://www.sec.gov/Archives/edgar/data/"):
        raise PresentationEvidenceError("Filing directory URL is not an SEC archive directory")
    return ArtifactInventory(
        directory_url=directory,
        index_url=f"{directory}/index.json",
        instance_name=instance_name,
        schema_names=schemas,
        presentation_names=presentations,
        filing_summary_name=summaries[0] if summaries else None,
        metalinks_name=metalinks[0] if metalinks else None,
        renderer_names=renderer_names,
        all_names=tuple(sorted(names)),
        all_source_urls=tuple(f"{directory}/{name}" for name in sorted(names)),
    )


def parse_role_definitions(
    schema_documents: Mapping[str, bytes],
) -> tuple[RoleDefinition, ...]:
    """Parse complete SEC role definitions from all local schemas."""
    roles: dict[str, RoleDefinition] = {}
    grammar = re.compile(r"^\s*([^\s-]+)\s+-\s+([^-]+?)\s+-\s+(.+?)\s*$")
    for source_url in sorted(schema_documents):
        root = _xml(schema_documents[source_url], "submitted schema")
        for element in root.iter(f"{{{LINK}}}roleType"):
            role_uri = element.get("roleURI", "").strip()
            definition_element = element.find(f"{{{LINK}}}definition")
            definition = "" if definition_element is None else "".join(definition_element.itertext()).strip()
            match = grammar.fullmatch(definition)
            if not role_uri or match is None:
                raise PresentationEvidenceError(
                    f"Malformed role definition in {source_url}: {definition!r}"
                )
            parsed = RoleDefinition(
                role_uri=role_uri,
                definition=definition,
                sort_code=match.group(1),
                role_type=match.group(2).strip(),
                title=match.group(3).strip(),
                source_url=source_url,
            )
            if role_uri in roles and roles[role_uri] != parsed:
                raise PresentationEvidenceError(f"Conflicting definition for role {role_uri}")
            roles[role_uri] = parsed
    if not roles:
        raise PresentationEvidenceError("Submitted schemas contain no role definitions")
    return tuple(sorted(roles.values(), key=lambda role: (role.sort_code, role.role_uri)))


def parse_presentation_memberships(
    presentation_documents: Mapping[str, bytes],
    roles: Sequence[RoleDefinition],
    *,
    target_concept: str = TARGET_CONCEPT,
) -> tuple[RoleMembership, ...]:
    """Preserve every ordered root-to-candidate path in every submitted role."""
    roles_by_uri = {role.role_uri: role for role in roles}
    memberships: list[RoleMembership] = []
    for source_url in sorted(presentation_documents):
        root = _xml(presentation_documents[source_url], "presentation linkbase")
        for link in root.iter(f"{{{LINK}}}presentationLink"):
            role_uri = link.get(f"{{{XLINK}}}role", "")
            locations: dict[str, str] = {}
            for loc in link.findall(f"{{{LINK}}}loc"):
                label = loc.get(f"{{{XLINK}}}label", "")
                href = loc.get(f"{{{XLINK}}}href", "")
                if not label or not href or label in locations:
                    raise PresentationEvidenceError(f"Malformed locator in role {role_uri}")
                locations[label] = href
            edges: list[tuple[str, str, PresentationStep]] = []
            for arc in link.findall(f"{{{LINK}}}presentationArc"):
                parent_label = arc.get(f"{{{XLINK}}}from", "")
                child_label = arc.get(f"{{{XLINK}}}to", "")
                if parent_label not in locations or child_label not in locations:
                    raise PresentationEvidenceError(f"Presentation arc has missing locator in {role_uri}")
                try:
                    order = Decimal(arc.get("order", "0"))
                except InvalidOperation as exc:
                    raise PresentationEvidenceError(f"Invalid relationship order in {role_uri}") from exc
                step = PresentationStep(
                    parent_href=locations[parent_label],
                    child_href=locations[child_label],
                    order=order,
                    preferred_label=arc.get("preferredLabel"),
                )
                edges.append((parent_label, child_label, step))
            candidate_labels = tuple(
                sorted(label for label, href in locations.items() if _href_local_name(href) == target_concept)
            )
            if not candidate_labels:
                continue
            role = roles_by_uri.get(role_uri)
            if role is None:
                raise PresentationEvidenceError(
                    f"Candidate presentation role {role_uri!r} has no submitted definition"
                )
            paths: list[PresentationPath] = []
            incoming = {child for _, child, _ in edges}
            roots = sorted(set(locations) - incoming)
            adjacency: dict[str, list[tuple[str, PresentationStep]]] = {}
            for parent, child, step in edges:
                adjacency.setdefault(parent, []).append((child, step))
            for children in adjacency.values():
                children.sort(key=lambda item: (item[1].order, item[1].child_href))
            for graph_root in roots:
                _walk_paths(graph_root, graph_root, candidate_labels, locations, adjacency, (), (), paths)
            if not paths:
                # A located candidate with no root path is a cycle or disconnected graph.
                raise PresentationEvidenceError(f"Candidate has no rooted path in role {role_uri}")
            memberships.append(
                RoleMembership(
                    role=role,
                    paths=tuple(sorted(paths, key=_path_sort_key)),
                )
            )
    return tuple(sorted(memberships, key=lambda item: (item.role.sort_code, item.role.role_uri)))


def parse_renderer_evidence(
    *,
    filing_summary: tuple[str, bytes] | None,
    metalinks: tuple[str, bytes] | None,
    renderer_files: Mapping[str, bytes],
    target_concept: str = TARGET_CONCEPT,
) -> RendererEvidence:
    """Parse renderer artifacts without merging them into submitted evidence."""
    errors: list[str] = []
    reports: list[RendererReport] = []
    urls: list[str] = []
    if filing_summary is None:
        errors.append("FilingSummary.xml missing")
    else:
        url, content = filing_summary
        urls.append(url)
        try:
            root = _xml(content, "FilingSummary.xml")
            for report in root.iter("Report"):
                value = lambda name: _child_text(report, name)
                reports.append(RendererReport(
                    role_uri=value("Role"), report_id=value("ReportId"),
                    menu_category=value("MenuCategory"), short_name=value("ShortName"),
                    long_name=value("LongName"), html_file_name=value("HtmlFileName"),
                    source_url=url,
                ))
        except PresentationEvidenceError as exc:
            errors.append(str(exc))
    metalinks_match: bool | None = None
    if metalinks is None:
        errors.append("MetaLinks.json missing")
    else:
        url, content = metalinks
        urls.append(url)
        try:
            parsed = json.loads(content.decode("utf-8"))
            canonical = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
            metalinks_match = target_concept in canonical
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"Malformed MetaLinks.json: {exc}")
    containing = []
    for url in sorted(renderer_files):
        urls.append(url)
        try:
            text = renderer_files[url].decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"Renderer file is not UTF-8: {url}")
            continue
        if target_concept in text:
            containing.append(url)
    if not renderer_files:
        errors.append("No applicable R-files discovered")
    return RendererEvidence(
        reports=tuple(reports),
        metalinks_contains_candidate=metalinks_match,
        renderer_files_containing_candidate=tuple(containing),
        source_urls=tuple(sorted(set(urls))),
        error="; ".join(errors) or None,
    )


def analyze_period(
    *,
    ticker: str,
    filing_xbrl: SECFilingXBRL,
    annual_period: ResolvedAnnualPeriod,
    inventory: ArtifactInventory,
    schema_documents: Mapping[str, bytes],
    presentation_documents: Mapping[str, bytes],
    renderer: RendererEvidence,
) -> PeriodEvidenceResult:
    """Reconcile and classify one exact selected filing, without I/O."""
    filing = filing_xbrl.filing
    try:
        if annual_period.filing.accession_number != filing.accession_number:
            raise PresentationEvidenceError("Annual-period accession does not match selected filing")
        candidates = _candidate_facts(filing_xbrl, annual_period)
        roles = parse_role_definitions(schema_documents)
        memberships = parse_presentation_memberships(presentation_documents, roles)
        submitted_role_uris = tuple(sorted(membership.role.role_uri for membership in memberships))
        renderer_role_uris = {report.role_uri for report in renderer.reports if report.role_uri}
        matching_role_uris = tuple(role for role in submitted_role_uris if role in renderer_role_uris)
        missing_role_uris = tuple(role for role in submitted_role_uris if role not in renderer_role_uris)
        renderer_error_parts = tuple(part for part in (renderer.error, "Renderer is missing submitted candidate roles" if missing_role_uris else None) if part)
        renderer = replace(
            renderer,
            submitted_role_uris=submitted_role_uris,
            renderer_matching_role_uris=matching_role_uris,
            renderer_missing_role_uris=missing_role_uris,
            error="; ".join(renderer_error_parts) or None,
        )
        presentation = _presentation_outcome(memberships)
        outcomes = (presentation,) + ((EvidenceOutcome.PRESENTATION_DATA_ERROR,) if renderer.error else ()) + (EvidenceOutcome.EQUITY_METHOD_SCOPE_UNRESOLVED,)
        error = renderer.error
    except PresentationEvidenceError as exc:
        candidates = ()
        memberships = ()
        outcomes = (EvidenceOutcome.PRESENTATION_DATA_ERROR, EvidenceOutcome.EQUITY_METHOD_SCOPE_UNRESOLVED)
        error = str(exc)
    return PeriodEvidenceResult(
        ticker=ticker, cik=filing_xbrl.company.cik,
        accession_number=filing.accession_number, form=filing.form,
        report_date=filing.report_date or annual_period.end,
        primary_document=filing.primary_document,
        annual_start=annual_period.start, annual_end=annual_period.end,
        candidate_facts=candidates, memberships=memberships, renderer=renderer,
        outcomes=outcomes, equity_method_scope=EquityMethodScope.UNRESOLVED,
        policy_decision=PolicyDecision.NEEDS_MORE_RESEARCH,
        artifact_inventory=inventory, error=error,
    )


def failure_result(
    *,
    ticker: str,
    error: str,
    accession_number: str = "",
    report_date: date = date.min,
) -> PeriodEvidenceResult:
    """Return a typed placeholder so a failed requested period is never dropped."""
    empty_renderer = RendererEvidence((), None, (), (), "Retrieval did not reach renderer parsing")
    return PeriodEvidenceResult(
        ticker=ticker, cik=0, accession_number=accession_number, form="10-K",
        report_date=report_date, primary_document="", annual_start=None, annual_end=None,
        candidate_facts=(), memberships=(), renderer=empty_renderer,
        outcomes=(EvidenceOutcome.PRESENTATION_DATA_ERROR, EvidenceOutcome.EQUITY_METHOD_SCOPE_UNRESOLVED),
        equity_method_scope=EquityMethodScope.UNRESOLVED,
        policy_decision=PolicyDecision.NEEDS_MORE_RESEARCH,
        artifact_inventory=None, error=error,
    )


def serialize_inventory(results: Sequence[PeriodEvidenceResult]) -> str:
    """Serialize results deterministically for a reproducible research artifact."""
    ordered = sorted(results, key=lambda result: (result.ticker, result.report_date, result.accession_number))
    payload = {
        "period_results": ordered,
        "equity_method_matrix": equity_method_matrix(),
        "policy_decision": PolicyDecision.NEEDS_MORE_RESEARCH,
        "safe_new_pretax_resolutions": 0,
    }
    return json.dumps(payload, default=_json_default, indent=2, sort_keys=True) + "\n"


def equity_method_matrix() -> tuple[EquityMethodMatrixEntry, ...]:
    """Materialize the issuer-level semantic gate using direct Wave 7 evidence."""
    return (
        EquityMethodMatrixEntry("AMZN", 5, EquityMethodScope.SEPARATE_NET_OF_TAX, "2025 filing presents equity-method activity net of tax below the tax line"),
        EquityMethodMatrixEntry("MU", 5, EquityMethodScope.UNRESOLVED, "No direct equity-method scope evidence established"),
        EquityMethodMatrixEntry("MA", 3, EquityMethodScope.UNRESOLVED, "Tag transition supports presentation continuity, not economic scope"),
        EquityMethodMatrixEntry("CVX", 5, EquityMethodScope.INCLUDED_PRETAX, "2025 filing states affiliate net income enters before-tax consolidated earnings"),
        EquityMethodMatrixEntry("CAT", 5, EquityMethodScope.UNRESOLVED, "No direct equity-method scope evidence established"),
        EquityMethodMatrixEntry("PM", 5, EquityMethodScope.UNRESOLVED, "No direct equity-method scope evidence established"),
        EquityMethodMatrixEntry("LIN", 5, EquityMethodScope.UNRESOLVED, "No direct equity-method scope evidence established"),
    )


def _candidate_facts(xbrl: SECFilingXBRL, annual: ResolvedAnnualPeriod) -> tuple[CandidateFactEvidence, ...]:
    candidates = []
    contexts_by_id = {context.context_id: context for context in xbrl.contexts}
    for fact in xbrl.facts:
        if fact.concept != TARGET_CONCEPT or not fact.namespace.startswith("http://fasb.org/us-gaap/"):
            continue
        if fact.start != annual.start or fact.end != annual.end or fact.dimensions:
            continue
        if fact.is_nil or fact.numeric_value is None:
            continue
        if fact.accession_number != xbrl.filing.accession_number or fact.source_url != xbrl.source_url:
            raise PresentationEvidenceError("Candidate fact provenance is inconsistent")
        context = contexts_by_id.get(fact.context_id)
        annual_evidence = annual.evidence
        if (
            context is None
            or context.entity_identifier_scheme != annual_evidence.entity_identifier_scheme
            or context.entity_identifier not in annual_evidence.entity_identifier_values
            or context.start != annual_evidence.start
            or context.end != annual_evidence.end
            or context.dimensions != annual_evidence.dimensions
        ):
            raise PresentationEvidenceError(
                "Candidate fact context does not match authoritative annual context"
            )
        if fact.unit is None or fact.unit.is_divided or len(fact.unit.numerator_measures) != 1:
            raise PresentationEvidenceError("Candidate fact does not have one simple unit")
        measure = fact.unit.numerator_measures[0]
        if measure.namespace != "http://www.xbrl.org/2003/iso4217" or measure.local_name != "USD":
            raise PresentationEvidenceError("Candidate fact unit is not exact USD")
        candidates.append(CandidateFactEvidence(
            namespace=fact.namespace, concept=fact.concept, context_id=fact.context_id,
            start=fact.start, end=fact.end, unit_ref=fact.unit_ref,
            unit_numerator_measures=tuple(f"{item.namespace}:{item.local_name}" for item in fact.unit.numerator_measures),
            unit_denominator_measures=tuple(f"{item.namespace}:{item.local_name}" for item in fact.unit.denominator_measures),
            dimensions=tuple(_dimension_text(d) for d in fact.dimensions),
            value=fact.numeric_value, accession_number=fact.accession_number,
            source_url=fact.source_url,
        ))
    if not candidates:
        raise PresentationEvidenceError("No exact nondimensional annual candidate fact")
    signatures = {(item.value, item.unit_ref) for item in candidates}
    if len(signatures) != 1:
        raise PresentationEvidenceError("Conflicting exact annual candidate facts")
    return tuple(sorted(candidates, key=lambda item: (item.context_id, item.unit_ref or "")))


def _presentation_outcome(memberships: Sequence[RoleMembership]) -> EvidenceOutcome:
    if not memberships:
        return EvidenceOutcome.NO_PRESENTATION_MEMBERSHIP
    if len(memberships) > 1:
        return EvidenceOutcome.MULTIPLE_ROLE_MEMBERSHIP
    role_type = memberships[0].role.role_type
    if role_type == "Statement":
        return EvidenceOutcome.PRIMARY_STATEMENT_MEMBER
    if role_type == "Disclosure":
        return EvidenceOutcome.DISCLOSURE_ONLY_MEMBER
    raise PresentationEvidenceError(f"Unsupported role type {role_type!r}")


def _walk_paths(root: str, node: str, targets: Sequence[str], locations: Mapping[str, str], adjacency: Mapping[str, Sequence[tuple[str, PresentationStep]]], labels: tuple[str, ...], steps: tuple[PresentationStep, ...], output: list[PresentationPath]) -> None:
    if node in labels:
        raise PresentationEvidenceError("Cycle in submitted presentation graph")
    next_labels = labels + (node,)
    if node in targets:
        output.append(PresentationPath(locations[root], tuple(locations[label] for label in labels), locations[node], steps))
    for child, step in adjacency.get(node, ()):
        _walk_paths(root, child, targets, locations, adjacency, next_labels, steps + (step,), output)


def _path_sort_key(path: PresentationPath) -> tuple[Any, ...]:
    return (path.root_href, tuple(step.order for step in path.relationships), path.candidate_href)


def _href_local_name(href: str) -> str:
    fragment = urlsplit(href).fragment
    if not fragment:
        return ""
    return fragment.split("_", 1)[1] if "_" in fragment else fragment


def _directory_names(payload: Any) -> list[str]:
    try:
        items = payload["directory"]["item"]
    except (TypeError, KeyError) as exc:
        raise PresentationEvidenceError("Malformed filing directory index") from exc
    if not isinstance(items, list):
        raise PresentationEvidenceError("Malformed filing directory item list")
    names = []
    for item in items:
        if not isinstance(item, dict):
            raise PresentationEvidenceError("Malformed filing directory item")
        names.append(_basename(item.get("name"), "artifact"))
    return names


def _basename(value: Any, description: str) -> str:
    if not isinstance(value, str) or not value or any(part in value for part in ("/", "\\", "..", "?", "#")) or urlsplit(value).scheme:
        raise PresentationEvidenceError(f"Unsafe or missing {description} name")
    return value


def _xml(content: bytes, description: str) -> ET.Element:
    if not isinstance(content, bytes) or not content or b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
        raise PresentationEvidenceError(f"Invalid {description} bytes")
    try:
        return ET.fromstring(content)
    except ET.ParseError as exc:
        raise PresentationEvidenceError(f"Malformed {description}") from exc


def _child_text(element: ET.Element, name: str) -> str | None:
    child = element.find(name)
    if child is None or child.text is None or not child.text.strip():
        return None
    return child.text.strip()


def _dimension_text(dimension: Any) -> str:
    member = dimension.explicit_member
    return f"{dimension.dimension.namespace}:{dimension.dimension.local_name}={member.namespace}:{member.local_name}" if member else f"{dimension.dimension.namespace}:{dimension.dimension.local_name}={dimension.typed_member_xml}"


def _json_default(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, (date, Decimal, Enum)):
        return str(value.value if isinstance(value, Enum) else value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"Cannot serialize {type(value).__name__}")
