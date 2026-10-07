"""Resolve an annual fiscal period from parsed filing-level DEI evidence."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
import re
from typing import TypeAlias

from .filing_xbrl import FilingXBRLDimension, FilingXBRLFact, SECFilingXBRL


SEC_CIK_SCHEME = "http://www.sec.gov/CIK"
DEI_NAMESPACE_PATTERN = re.compile(
    r"^http://xbrl\.sec\.gov/dei/[0-9]{4}(?:q[1-4])?$"
)
DEI_CONCEPTS = (
    "DocumentFiscalPeriodFocus",
    "DocumentFiscalYearFocus",
    "DocumentPeriodEndDate",
)


class AnnualPeriodResolutionStatus(str, Enum):
    """Possible outcomes from annual-period evidence resolution."""

    RESOLVED = "annual_period_resolved"
    NOT_FOUND = "annual_period_not_found"
    AMBIGUOUS = "annual_period_ambiguous"
    UNSUPPORTED = "annual_period_unsupported"
    DATA_ERROR = "annual_period_data_error"


@dataclass(frozen=True)
class AnnualPeriodFilingEvidence:
    """Selected filing identity and source metadata used by the resolver."""

    registrant_cik: int
    accession_number: str
    form: str
    report_date: date | None
    filing_date: date
    primary_document: str
    source_url: str
    retrieved_at: datetime


@dataclass(frozen=True)
class AnnualPeriodDEIFactOccurrence:
    """One raw DEI fact occurrence retained for audit."""

    namespace: str
    concept: str
    context_id: str
    raw_value: str
    normalized_value: str
    source_url: str


@dataclass(frozen=True)
class AnnualPeriodDEIEvidence:
    """Normalized value and all confirming occurrences for one DEI concept."""

    concept: str
    normalized_value: str
    occurrences: tuple[AnnualPeriodDEIFactOccurrence, ...]


@dataclass(frozen=True)
class AnnualPeriodEvidenceTuple:
    """One internally consistent normalized annual-period evidence tuple."""

    entity_identifier_scheme: str
    entity_identifier_values: tuple[str, ...]
    registrant_cik: int
    start: date
    end: date
    dimensions: tuple[FilingXBRLDimension, ...]
    context_ids: tuple[str, ...]
    dei_evidence: tuple[AnnualPeriodDEIEvidence, ...]


@dataclass(frozen=True)
class ResolvedAnnualPeriod:
    """One authoritative annual period with compact filing-XBRL provenance."""

    filing: AnnualPeriodFilingEvidence
    evidence: AnnualPeriodEvidenceTuple
    status: AnnualPeriodResolutionStatus = field(
        default=AnnualPeriodResolutionStatus.RESOLVED,
        init=False,
    )

    @property
    def start(self) -> date:
        return self.evidence.start

    @property
    def end(self) -> date:
        return self.evidence.end


@dataclass(frozen=True)
class AnnualPeriodNotFound:
    """A supported filing with no complete eligible annual DEI evidence."""

    filing: AnnualPeriodFilingEvidence
    reason: str
    status: AnnualPeriodResolutionStatus = field(
        default=AnnualPeriodResolutionStatus.NOT_FOUND,
        init=False,
    )


@dataclass(frozen=True)
class AmbiguousAnnualPeriod:
    """Multiple valid evidence tuples that imply different annual periods."""

    filing: AnnualPeriodFilingEvidence
    candidates: tuple[AnnualPeriodEvidenceTuple, ...]
    status: AnnualPeriodResolutionStatus = field(
        default=AnnualPeriodResolutionStatus.AMBIGUOUS,
        init=False,
    )


@dataclass(frozen=True)
class UnsupportedAnnualPeriod:
    """Valid filing evidence outside the approved exact-10-K grammar."""

    filing: AnnualPeriodFilingEvidence
    reason: str
    status: AnnualPeriodResolutionStatus = field(
        default=AnnualPeriodResolutionStatus.UNSUPPORTED,
        init=False,
    )


@dataclass(frozen=True)
class AnnualPeriodDataErrorResult:
    """Malformed or internally inconsistent supplied annual-period evidence."""

    filing: AnnualPeriodFilingEvidence
    reason: str
    context_ids: tuple[str, ...] = ()
    status: AnnualPeriodResolutionStatus = field(
        default=AnnualPeriodResolutionStatus.DATA_ERROR,
        init=False,
    )


AnnualPeriodResolution: TypeAlias = (
    ResolvedAnnualPeriod
    | AnnualPeriodNotFound
    | AmbiguousAnnualPeriod
    | UnsupportedAnnualPeriod
    | AnnualPeriodDataErrorResult
)


@dataclass(frozen=True)
class _StructuralContextKey:
    scheme: str
    registrant_cik: int
    start: date
    end: date
    dimensions: tuple[tuple[object, ...], ...]


def resolve_annual_period(filing_xbrl: SECFilingXBRL) -> AnnualPeriodResolution:
    """Resolve one exact 10-K annual period without performing network access."""
    filing_evidence = _filing_evidence(filing_xbrl)
    filing = filing_xbrl.filing
    if filing.form != "10-K":
        return UnsupportedAnnualPeriod(
            filing=filing_evidence,
            reason=f"Annual-period resolution does not support form {filing.form!r}",
        )
    if filing.report_date is None:
        return AnnualPeriodDataErrorResult(
            filing=filing_evidence,
            reason="Selected exact 10-K has no report date",
        )
    if not filing_xbrl.source_url or filing_xbrl.retrieved_at.tzinfo is None:
        return AnnualPeriodDataErrorResult(
            filing=filing_evidence,
            reason="Filing-XBRL source provenance is invalid",
        )

    contexts_by_id = {}
    for context in filing_xbrl.contexts:
        if not context.context_id or context.context_id in contexts_by_id:
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason="Filing-XBRL context IDs must be nonempty and unique",
            )
        contexts_by_id[context.context_id] = context

    facts_by_key: dict[
        _StructuralContextKey,
        dict[str, list[AnnualPeriodDEIFactOccurrence]],
    ] = defaultdict(lambda: defaultdict(list))
    context_ids_by_key: dict[_StructuralContextKey, set[str]] = defaultdict(set)
    entity_values_by_key: dict[_StructuralContextKey, set[str]] = defaultdict(set)
    values_by_context: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )

    for fact in filing_xbrl.facts:
        if not _is_relevant_dei_fact(fact):
            continue
        context = contexts_by_id.get(fact.context_id)
        if context is None:
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason=f"DEI fact references missing context {fact.context_id!r}",
                context_ids=(fact.context_id,),
            )
        if (
            fact.start != context.start
            or fact.end != context.end
            or fact.dimensions != context.dimensions
            or fact.accession_number != filing.accession_number
            or fact.source_url != filing_xbrl.source_url
        ):
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason="DEI fact linkage is inconsistent with filing-XBRL metadata",
                context_ids=(context.context_id,),
            )
        if fact.is_nil:
            continue
        if context.end != filing.report_date:
            continue
        normalized_value = _normalize_dei_value(fact.concept, fact.raw_value)
        if normalized_value is None:
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason=f"DEI concept {fact.concept!r} has a malformed value",
                context_ids=(context.context_id,),
            )
        values_by_context[context.context_id][fact.concept].add(normalized_value)
        if context.start is None or context.dimensions:
            continue
        if context.start >= context.end:
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason="Eligible annual duration must start before it ends",
                context_ids=(context.context_id,),
            )
        normalized_cik = _normalized_context_cik(
            context.entity_identifier_scheme,
            context.entity_identifier,
            filing_xbrl.company.cik,
            filing_xbrl.company.cik_padded,
        )
        if normalized_cik is None:
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason="Eligible DEI context has invalid SEC registrant identity",
                context_ids=(context.context_id,),
            )
        key = _StructuralContextKey(
            scheme=context.entity_identifier_scheme,
            registrant_cik=normalized_cik,
            start=context.start,
            end=context.end,
            dimensions=_dimension_key(context.dimensions),
        )
        facts_by_key[key][fact.concept].append(
            AnnualPeriodDEIFactOccurrence(
                namespace=fact.namespace,
                concept=fact.concept,
                context_id=context.context_id,
                raw_value=fact.raw_value or "",
                normalized_value=normalized_value,
                source_url=fact.source_url,
            )
        )
        context_ids_by_key[key].add(context.context_id)
        entity_values_by_key[key].add(context.entity_identifier)

    for context_id in sorted(values_by_context):
        context = contexts_by_id[context_id]
        if context.start is not None and not context.dimensions:
            continue
        values = values_by_context[context_id]
        if not all(concept in values for concept in DEI_CONCEPTS):
            continue
        if any(len(values[concept]) != 1 for concept in DEI_CONCEPTS):
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason="Ineligible DEI context contains contradictory values",
                context_ids=(context_id,),
            )
        if (
            next(iter(values["DocumentFiscalPeriodFocus"])) == "FY"
            and next(iter(values["DocumentPeriodEndDate"]))
            == filing.report_date.isoformat()
            and _normalized_context_cik(
                context.entity_identifier_scheme,
                context.entity_identifier,
                filing_xbrl.company.cik,
                filing_xbrl.company.cik_padded,
            )
            is None
        ):
            return AnnualPeriodDataErrorResult(
                filing=filing_evidence,
                reason="DEI context has invalid SEC registrant identity",
                context_ids=(context_id,),
            )

    candidates = []
    for key in sorted(facts_by_key, key=_structural_key_sort_key):
        by_concept = facts_by_key[key]
        evidence = []
        for concept in DEI_CONCEPTS:
            occurrences = by_concept.get(concept, [])
            if not occurrences:
                break
            values = {occurrence.normalized_value for occurrence in occurrences}
            if len(values) != 1:
                return AnnualPeriodDataErrorResult(
                    filing=filing_evidence,
                    reason=(
                        f"DEI concept {concept!r} has contradictory values in one "
                        "semantic context"
                    ),
                    context_ids=tuple(sorted(context_ids_by_key[key])),
                )
            normalized_value = next(iter(values))
            evidence.append(
                AnnualPeriodDEIEvidence(
                    concept=concept,
                    normalized_value=normalized_value,
                    occurrences=tuple(sorted(occurrences, key=_occurrence_sort_key)),
                )
            )
        else:
            values_by_concept = {
                item.concept: item.normalized_value for item in evidence
            }
            if values_by_concept["DocumentFiscalPeriodFocus"] != "FY":
                continue
            if values_by_concept["DocumentPeriodEndDate"] != filing.report_date.isoformat():
                continue
            candidates.append(
                AnnualPeriodEvidenceTuple(
                    entity_identifier_scheme=key.scheme,
                    entity_identifier_values=tuple(sorted(entity_values_by_key[key])),
                    registrant_cik=key.registrant_cik,
                    start=key.start,
                    end=key.end,
                    dimensions=(),
                    context_ids=tuple(sorted(context_ids_by_key[key])),
                    dei_evidence=tuple(evidence),
                )
            )

    candidates.sort(key=_candidate_sort_key)
    if not candidates:
        return AnnualPeriodNotFound(
            filing=filing_evidence,
            reason="No complete eligible DEI annual-period evidence was found",
        )
    distinct_periods = {(candidate.start, candidate.end) for candidate in candidates}
    if len(distinct_periods) > 1:
        return AmbiguousAnnualPeriod(
            filing=filing_evidence,
            candidates=tuple(candidates),
        )
    if len(candidates) != 1:
        return AnnualPeriodDataErrorResult(
            filing=filing_evidence,
            reason="Equivalent annual periods have inconsistent normalized DEI evidence",
            context_ids=tuple(
                sorted(
                    context_id
                    for candidate in candidates
                    for context_id in candidate.context_ids
                )
            ),
        )
    return ResolvedAnnualPeriod(
        filing=filing_evidence,
        evidence=candidates[0],
    )


def _filing_evidence(filing_xbrl: SECFilingXBRL) -> AnnualPeriodFilingEvidence:
    filing = filing_xbrl.filing
    return AnnualPeriodFilingEvidence(
        registrant_cik=filing_xbrl.company.cik,
        accession_number=filing.accession_number,
        form=filing.form,
        report_date=filing.report_date,
        filing_date=filing.filing_date,
        primary_document=filing.primary_document,
        source_url=filing_xbrl.source_url,
        retrieved_at=filing_xbrl.retrieved_at,
    )


def _is_relevant_dei_fact(fact: FilingXBRLFact) -> bool:
    return (
        fact.concept in DEI_CONCEPTS
        and DEI_NAMESPACE_PATTERN.fullmatch(fact.namespace) is not None
    )


def _normalized_context_cik(
    scheme: str,
    value: str,
    expected_cik: int,
    expected_cik_padded: str,
) -> int | None:
    if scheme != SEC_CIK_SCHEME or not value:
        return None
    if not all("0" <= character <= "9" for character in value):
        return None
    if value == expected_cik_padded:
        return expected_cik
    if value == "0" or value[0] != "0":
        normalized = int(value)
        return normalized if normalized == expected_cik else None
    return None


def _normalize_dei_value(concept: str, value: str | None) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    if concept == "DocumentFiscalPeriodFocus":
        return value if value in {"Q1", "Q2", "Q3", "FY"} else None
    if concept == "DocumentFiscalYearFocus":
        return value if re.fullmatch(r"[0-9]{4}", value) is not None else None
    if concept == "DocumentPeriodEndDate":
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
            return None
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            return None
    return None


def _dimension_key(
    dimensions: tuple[FilingXBRLDimension, ...],
) -> tuple[tuple[object, ...], ...]:
    return tuple(
        sorted(
            (
                dimension.dimension.namespace,
                dimension.dimension.local_name,
                (
                    dimension.explicit_member.namespace
                    if dimension.explicit_member is not None
                    else ""
                ),
                (
                    dimension.explicit_member.local_name
                    if dimension.explicit_member is not None
                    else ""
                ),
                dimension.typed_member_xml or "",
            )
            for dimension in dimensions
        )
    )


def _structural_key_sort_key(key: _StructuralContextKey) -> tuple[object, ...]:
    return (key.start, key.end, key.scheme, key.registrant_cik, key.dimensions)


def _occurrence_sort_key(
    occurrence: AnnualPeriodDEIFactOccurrence,
) -> tuple[str, ...]:
    return (
        occurrence.concept,
        occurrence.normalized_value,
        occurrence.namespace,
        occurrence.context_id,
        occurrence.raw_value,
        occurrence.source_url,
    )


def _candidate_sort_key(candidate: AnnualPeriodEvidenceTuple) -> tuple[object, ...]:
    return (
        candidate.start,
        candidate.end,
        candidate.entity_identifier_scheme,
        candidate.registrant_cik,
        candidate.context_ids,
    )
