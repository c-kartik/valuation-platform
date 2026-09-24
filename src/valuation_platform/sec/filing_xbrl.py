"""Discover, retrieve, and structurally parse SEC extracted XBRL instances."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO
import re
from typing import Any
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from .client import SECClient
from .submissions import SECFiling
from .tickers import SECCompanyIdentity


ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"
XBRLI_NAMESPACE = "http://www.xbrl.org/2003/instance"
XBRLDI_NAMESPACE = "http://xbrl.org/2006/xbrldi"
LINK_NAMESPACE = "http://www.xbrl.org/2003/linkbase"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
ACCESSION_PATTERN = re.compile(r"^[0-9]{10}-[0-9]{2}-[0-9]{6}$")


class FilingXBRLError(Exception):
    """Base error for filing-level extracted XBRL processing."""


class FilingXBRLSourceError(FilingXBRLError):
    """Raised when a filing XBRL artifact cannot be identified safely."""


class FilingXBRLDataError(FilingXBRLError):
    """Raised when an extracted XBRL instance is structurally invalid."""


@dataclass(frozen=True)
class FilingXBRLQName:
    """Namespace URI and local name identifying an XBRL name."""

    namespace: str
    local_name: str


@dataclass(frozen=True)
class FilingXBRLDimension:
    """One explicit or typed dimension attached to an XBRL context."""

    dimension: FilingXBRLQName
    explicit_member: FilingXBRLQName | None
    typed_member_xml: str | None


@dataclass(frozen=True)
class FilingXBRLContext:
    """Entity, period, and dimensional information for an XBRL context."""

    context_id: str
    entity_identifier: str
    start: date | None
    end: date
    dimensions: tuple[FilingXBRLDimension, ...]

    @property
    def is_instant(self) -> bool:
        """Return whether this context represents an instant."""
        return self.start is None


@dataclass(frozen=True)
class FilingXBRLUnit:
    """A simple or divided XBRL unit."""

    unit_id: str
    numerator_measures: tuple[FilingXBRLQName, ...]
    denominator_measures: tuple[FilingXBRLQName, ...]

    @property
    def is_divided(self) -> bool:
        """Return whether this unit has a denominator."""
        return bool(self.denominator_measures)


@dataclass(frozen=True)
class SECExtractedXBRLArtifact:
    """One SEC-generated extracted instance discovered for a filing."""

    name: str
    source_url: str
    directory_url: str


@dataclass(frozen=True)
class FilingXBRLFact:
    """One unselected fact from an SEC extracted XBRL instance."""

    namespace: str
    concept: str
    context_id: str
    start: date | None
    end: date
    dimensions: tuple[FilingXBRLDimension, ...]
    unit_ref: str | None
    unit: FilingXBRLUnit | None
    raw_value: str | None
    numeric_value: Decimal | None
    decimals: str | None
    is_nil: bool
    accession_number: str
    source_url: str


@dataclass(frozen=True)
class SECFilingXBRL:
    """Structural facts and contexts parsed from one filing instance."""

    company: SECCompanyIdentity
    filing: SECFiling
    contexts: tuple[FilingXBRLContext, ...]
    units: tuple[FilingXBRLUnit, ...]
    facts: tuple[FilingXBRLFact, ...]
    source_url: str
    retrieved_at: datetime


def discover_extracted_xbrl(
    client: SECClient,
    company: SECCompanyIdentity,
    filing: SECFiling,
) -> SECExtractedXBRLArtifact:
    """Discover the extracted instance corresponding to a primary document."""
    directory_url = _filing_directory_url(company, filing)
    payload = client.get_json(f"{directory_url}/index.json")
    names = _parse_directory_names(payload)
    primary_document = _validate_basename(
        filing.primary_document,
        "primary document",
    )
    primary_stem = _primary_document_stem(primary_document)
    expected_name = f"{primary_stem}_htm.xml"
    matches = tuple(name for name in names if name == expected_name)
    if len(matches) > 1:
        raise FilingXBRLSourceError(
            f"SEC filing directory has ambiguous extracted instances for "
            f"{filing.accession_number!r}"
        )
    if not matches:
        extracted_names = tuple(name for name in names if name.endswith("_htm.xml"))
        if not extracted_names:
            raise FilingXBRLSourceError(
                f"SEC filing {filing.accession_number!r} has no extracted XBRL instance"
            )
        raise FilingXBRLSourceError(
            "SEC filing directory has no extracted XBRL instance corresponding to "
            f"primary document {primary_document!r}"
        )
    artifact_name = _validate_basename(matches[0], "extracted XBRL artifact")
    return SECExtractedXBRLArtifact(
        name=artifact_name,
        source_url=f"{directory_url}/{artifact_name}",
        directory_url=directory_url,
    )


def fetch_filing_xbrl(
    client: SECClient,
    company: SECCompanyIdentity,
    filing: SECFiling,
) -> SECFilingXBRL:
    """Discover, retrieve, and parse one SEC extracted XBRL instance."""
    artifact = discover_extracted_xbrl(client, company, filing)
    content = client.get_bytes(artifact.source_url)
    return parse_filing_xbrl_instance(
        content,
        company=company,
        filing=filing,
        source_url=artifact.source_url,
    )


def parse_filing_xbrl_instance(
    content: bytes,
    *,
    company: SECCompanyIdentity,
    filing: SECFiling,
    source_url: str,
    retrieved_at: datetime | None = None,
) -> SECFilingXBRL:
    """Parse one SEC extracted XBRL instance without financial selection."""
    if not isinstance(content, bytes) or not content:
        raise FilingXBRLDataError("Extracted XBRL instance must be nonempty bytes")
    upper_content = content.upper()
    if b"<!DOCTYPE" in upper_content or b"<!ENTITY" in upper_content:
        raise FilingXBRLDataError("Extracted XBRL instance contains a prohibited DTD")
    namespace_map = _namespace_map(content)
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise FilingXBRLDataError("Extracted XBRL instance is not valid XML") from exc
    if root.tag != f"{{{XBRLI_NAMESPACE}}}xbrl":
        raise FilingXBRLDataError("Extracted XBRL document root must be xbrli:xbrl")

    contexts = _parse_contexts(root, namespace_map)
    units = _parse_units(root, namespace_map)
    context_by_id = {context.context_id: context for context in contexts}
    unit_by_id = {unit.unit_id: unit for unit in units}
    facts = _parse_facts(
        root,
        context_by_id,
        unit_by_id,
        filing.accession_number,
        source_url,
    )
    timestamp = retrieved_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise FilingXBRLDataError("Retrieved timestamp must be timezone-aware")
    return SECFilingXBRL(
        company=company,
        filing=filing,
        contexts=contexts,
        units=units,
        facts=facts,
        source_url=source_url,
        retrieved_at=timestamp,
    )


def _filing_directory_url(
    company: SECCompanyIdentity,
    filing: SECFiling,
) -> str:
    accession = filing.accession_number
    if not isinstance(accession, str) or ACCESSION_PATTERN.fullmatch(accession) is None:
        raise FilingXBRLSourceError(
            f"Filing accession {accession!r} is not canonical"
        )
    accession_path = accession.replace("-", "")
    return f"{ARCHIVES_BASE_URL}/{company.cik}/{accession_path}"


def _validate_basename(value: Any, description: str) -> str:
    if not isinstance(value, str) or not value:
        raise FilingXBRLSourceError(f"SEC {description} must be a nonempty filename")
    if (
        "/" in value
        or "\\" in value
        or ".." in value
        or urlsplit(value).scheme
        or "?" in value
        or "#" in value
    ):
        raise FilingXBRLSourceError(f"SEC {description} is not a safe basename")
    return value


def _primary_document_stem(primary_document: str) -> str:
    lowered = primary_document.lower()
    for suffix in (".html", ".htm"):
        if lowered.endswith(suffix):
            return primary_document[: -len(suffix)]
    raise FilingXBRLSourceError(
        f"Primary document {primary_document!r} is not an HTML document"
    )


def _parse_directory_names(payload: Any) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        raise FilingXBRLSourceError("SEC filing directory metadata must be an object")
    directory = payload.get("directory")
    if not isinstance(directory, dict):
        raise FilingXBRLSourceError("SEC filing directory metadata has no directory")
    items = directory.get("item")
    if not isinstance(items, list):
        raise FilingXBRLSourceError("SEC filing directory metadata has no item list")
    names = []
    for item in items:
        if not isinstance(item, dict):
            raise FilingXBRLSourceError("SEC filing directory item must be an object")
        name = _validate_basename(item.get("name"), "filing artifact")
        names.append(name)
    return tuple(names)


def _namespace_map(content: bytes) -> dict[str, str]:
    namespaces: dict[str, str] = {
        "xml": "http://www.w3.org/XML/1998/namespace",
    }
    try:
        for _, (prefix, namespace) in ET.iterparse(
            BytesIO(content), events=("start-ns",)
        ):
            key = prefix or ""
            existing = namespaces.get(key)
            if existing is not None and existing != namespace:
                raise FilingXBRLDataError(
                    f"XML namespace prefix {key!r} is bound inconsistently"
                )
            namespaces[key] = namespace
    except ET.ParseError as exc:
        raise FilingXBRLDataError("Extracted XBRL instance is not valid XML") from exc
    return namespaces


def _parse_contexts(
    root: ET.Element,
    namespaces: dict[str, str],
) -> tuple[FilingXBRLContext, ...]:
    contexts = []
    seen = set()
    for element in root.findall(f"{{{XBRLI_NAMESPACE}}}context"):
        context_id = element.get("id")
        if not context_id or context_id in seen:
            raise FilingXBRLDataError("XBRL context IDs must be nonempty and unique")
        seen.add(context_id)
        identifier = element.find(
            f"{{{XBRLI_NAMESPACE}}}entity/{{{XBRLI_NAMESPACE}}}identifier"
        )
        if identifier is None or not (identifier.text or "").strip():
            raise FilingXBRLDataError(f"XBRL context {context_id!r} has no entity")
        period = element.find(f"{{{XBRLI_NAMESPACE}}}period")
        if period is None:
            raise FilingXBRLDataError(f"XBRL context {context_id!r} has no period")
        start_element = period.find(f"{{{XBRLI_NAMESPACE}}}startDate")
        end_element = period.find(f"{{{XBRLI_NAMESPACE}}}endDate")
        instant_element = period.find(f"{{{XBRLI_NAMESPACE}}}instant")
        if instant_element is not None and start_element is None and end_element is None:
            start = None
            end = _parse_date(instant_element.text, context_id)
        elif instant_element is None and start_element is not None and end_element is not None:
            start = _parse_date(start_element.text, context_id)
            end = _parse_date(end_element.text, context_id)
            if start > end:
                raise FilingXBRLDataError(
                    f"XBRL context {context_id!r} starts after it ends"
                )
        else:
            raise FilingXBRLDataError(
                f"XBRL context {context_id!r} has an invalid period"
            )
        dimensions = _parse_dimensions(element, namespaces)
        contexts.append(
            FilingXBRLContext(
                context_id=context_id,
                entity_identifier=(identifier.text or "").strip(),
                start=start,
                end=end,
                dimensions=dimensions,
            )
        )
    return tuple(contexts)


def _parse_dimensions(
    context: ET.Element,
    namespaces: dict[str, str],
) -> tuple[FilingXBRLDimension, ...]:
    dimensions = []
    for member in context.iter():
        if member.tag == f"{{{XBRLDI_NAMESPACE}}}explicitMember":
            dimension = _parse_lexical_qname(member.get("dimension"), namespaces)
            explicit = _parse_lexical_qname(member.text, namespaces)
            dimensions.append(
                FilingXBRLDimension(
                    dimension=dimension,
                    explicit_member=explicit,
                    typed_member_xml=None,
                )
            )
        elif member.tag == f"{{{XBRLDI_NAMESPACE}}}typedMember":
            dimension = _parse_lexical_qname(member.get("dimension"), namespaces)
            children = list(member)
            if len(children) != 1:
                raise FilingXBRLDataError(
                    "Typed XBRL dimension must contain exactly one value element"
                )
            dimensions.append(
                FilingXBRLDimension(
                    dimension=dimension,
                    explicit_member=None,
                    typed_member_xml=ET.tostring(children[0], encoding="unicode"),
                )
            )
    return tuple(dimensions)


def _parse_units(
    root: ET.Element,
    namespaces: dict[str, str],
) -> tuple[FilingXBRLUnit, ...]:
    units = []
    seen = set()
    for element in root.findall(f"{{{XBRLI_NAMESPACE}}}unit"):
        unit_id = element.get("id")
        if not unit_id or unit_id in seen:
            raise FilingXBRLDataError("XBRL unit IDs must be nonempty and unique")
        seen.add(unit_id)
        direct_measures = element.findall(f"{{{XBRLI_NAMESPACE}}}measure")
        divide = element.find(f"{{{XBRLI_NAMESPACE}}}divide")
        if direct_measures and divide is None:
            numerator = tuple(
                _parse_lexical_qname(measure.text, namespaces)
                for measure in direct_measures
            )
            denominator: tuple[FilingXBRLQName, ...] = ()
        elif not direct_measures and divide is not None:
            numerator_elements = divide.findall(
                f"{{{XBRLI_NAMESPACE}}}unitNumerator/{{{XBRLI_NAMESPACE}}}measure"
            )
            denominator_elements = divide.findall(
                f"{{{XBRLI_NAMESPACE}}}unitDenominator/{{{XBRLI_NAMESPACE}}}measure"
            )
            if not numerator_elements or not denominator_elements:
                raise FilingXBRLDataError(f"XBRL unit {unit_id!r} has invalid division")
            numerator = tuple(
                _parse_lexical_qname(measure.text, namespaces)
                for measure in numerator_elements
            )
            denominator = tuple(
                _parse_lexical_qname(measure.text, namespaces)
                for measure in denominator_elements
            )
        else:
            raise FilingXBRLDataError(f"XBRL unit {unit_id!r} is malformed")
        units.append(
            FilingXBRLUnit(
                unit_id=unit_id,
                numerator_measures=numerator,
                denominator_measures=denominator,
            )
        )
    return tuple(units)


def _parse_facts(
    root: ET.Element,
    contexts: dict[str, FilingXBRLContext],
    units: dict[str, FilingXBRLUnit],
    accession_number: str,
    source_url: str,
) -> tuple[FilingXBRLFact, ...]:
    facts = []
    for element in root:
        context_id = element.get("contextRef")
        if context_id is None:
            namespace, concept = _expanded_name(element.tag)
            if namespace in (XBRLI_NAMESPACE, LINK_NAMESPACE):
                continue
            raise FilingXBRLDataError(
                f"XBRL fact {concept!r} has no context reference"
            )
        context = contexts.get(context_id)
        if context is None:
            raise FilingXBRLDataError(
                f"XBRL fact references missing context {context_id!r}"
            )
        namespace, concept = _expanded_name(element.tag)
        unit_ref = element.get("unitRef")
        unit = units.get(unit_ref) if unit_ref is not None else None
        if unit_ref is not None and unit is None:
            raise FilingXBRLDataError(
                f"XBRL fact references missing unit {unit_ref!r}"
            )
        nil_text = element.get(f"{{{XSI_NAMESPACE}}}nil")
        if nil_text not in (None, "true", "false", "1", "0"):
            raise FilingXBRLDataError("XBRL fact has an invalid xsi:nil value")
        is_nil = nil_text in ("true", "1")
        raw_value = None if is_nil else "".join(element.itertext()).strip()
        numeric_value = _numeric_value(raw_value, unit_ref, element, is_nil)
        facts.append(
            FilingXBRLFact(
                namespace=namespace,
                concept=concept,
                context_id=context_id,
                start=context.start,
                end=context.end,
                dimensions=context.dimensions,
                unit_ref=unit_ref,
                unit=unit,
                raw_value=raw_value,
                numeric_value=numeric_value,
                decimals=element.get("decimals"),
                is_nil=is_nil,
                accession_number=accession_number,
                source_url=source_url,
            )
        )
    return tuple(facts)


def _numeric_value(
    raw_value: str | None,
    unit_ref: str | None,
    element: ET.Element,
    is_nil: bool,
) -> Decimal | None:
    if is_nil or unit_ref is None or raw_value is None or list(element):
        return None
    try:
        value = Decimal(raw_value)
    except InvalidOperation:
        return None
    return value if value.is_finite() else None


def _parse_date(value: str | None, context_id: str) -> date:
    if not isinstance(value, str):
        raise FilingXBRLDataError(f"XBRL context {context_id!r} has no date")
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value.strip()) is None:
        raise FilingXBRLDataError(
            f"XBRL context {context_id!r} has an invalid date"
        )
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise FilingXBRLDataError(
            f"XBRL context {context_id!r} has an invalid date"
        ) from exc


def _parse_lexical_qname(
    value: str | None,
    namespaces: dict[str, str],
) -> FilingXBRLQName:
    if not isinstance(value, str) or not value.strip():
        raise FilingXBRLDataError("XBRL QName must not be empty")
    lexical = value.strip()
    if ":" in lexical:
        prefix, local_name = lexical.split(":", 1)
    else:
        prefix, local_name = "", lexical
    namespace = namespaces.get(prefix)
    if namespace is None or not local_name:
        raise FilingXBRLDataError(f"XBRL QName {lexical!r} has an unknown namespace")
    return FilingXBRLQName(namespace=namespace, local_name=local_name)


def _expanded_name(value: str) -> tuple[str, str]:
    if not value.startswith("{") or "}" not in value:
        raise FilingXBRLDataError("XBRL fact name must be namespace-qualified")
    namespace, local_name = value[1:].split("}", 1)
    if not namespace or not local_name:
        raise FilingXBRLDataError("XBRL fact name is malformed")
    return namespace, local_name
