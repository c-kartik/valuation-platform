"""Apply curated exact-accession Pretax semantic-equivalence approvals."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from valuation_platform.sec.annual_period import (
    AnnualPeriodResolution,
    ResolvedAnnualPeriod,
)
from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationPeriodType,
    ObservationRelationship,
    SelectedFactObservation,
)
from valuation_platform.sec.filing_xbrl import (
    FilingXBRLContext,
    FilingXBRLFact,
    SECFilingXBRL,
)

from .concepts import ConceptKey, FinancialMetric
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    EvidenceSourceKind,
    FactEvidence,
    FilingXBRLEvidence,
    HistoricalMetricResult,
    HistoricalPeriod,
    HistoricalPolicyProvenance,
    MissingHistoricalMetric,
    NormalizedHistoricalValue,
    ReviewedPolicyEvidence,
)


PRETAX_SCOPE_POLICY_ID = "pretax_scope_equivalence"
PRETAX_SCOPE_POLICY_VERSION = "1"
PRETAX_SCOPE_CANDIDATE = ConceptKey(
    "us-gaap",
    (
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
        "MinorityInterestAndIncomeLossFromEquityMethodInvestments"
    ),
)
_USD_NAMESPACE = "http://www.xbrl.org/2003/iso4217"


class PretaxEconomicScope(str, Enum):
    """Reviewed economic scope of one candidate Pretax fact."""

    INCLUDED_PRETAX = "INCLUDED_PRETAX"


class PretaxScopePolicyError(ValueError):
    """Raised when curated Pretax policy inputs violate their boundary."""


@dataclass(frozen=True)
class _CandidateOccurrence:
    """One structurally reconciled candidate fact and its referenced context."""

    source_index: int
    fact: FilingXBRLFact
    context: FilingXBRLContext
    normalized_cik: int
    normalized_unit: str | None


@dataclass(frozen=True)
class PretaxScopePolicyEntry:
    """One exact filing fact approved as semantically equivalent Pretax."""

    company_cik: int
    accession_number: str
    report_date: date
    annual_start: date
    annual_end: date
    taxonomy: str
    concept: str
    unit: str
    economic_scope: PretaxEconomicScope
    expected_value: int
    reviewed_evidence: tuple[ReviewedPolicyEvidence, ...]

    @property
    def key(self) -> tuple[object, ...]:
        """Return the complete immutable semantic-approval key."""
        return (
            self.company_cik,
            self.accession_number,
            self.report_date,
            self.annual_start,
            self.annual_end,
            self.taxonomy,
            self.concept,
            self.unit,
            self.economic_scope,
        )

    def __post_init__(self) -> None:
        if (
            not isinstance(self.company_cik, int)
            or isinstance(self.company_cik, bool)
            or self.company_cik < 0
            or not self.accession_number
            or self.annual_start >= self.annual_end
            or self.annual_end != self.report_date
            or self.taxonomy != PRETAX_SCOPE_CANDIDATE.taxonomy
            or self.concept != PRETAX_SCOPE_CANDIDATE.name
            or self.unit != "USD"
            or self.economic_scope is not PretaxEconomicScope.INCLUDED_PRETAX
            or not isinstance(self.expected_value, int)
            or isinstance(self.expected_value, bool)
            or not self.reviewed_evidence
        ):
            raise PretaxScopePolicyError("Pretax scope-policy entry is invalid")
        if len({item.evidence_id for item in self.reviewed_evidence}) != len(
            self.reviewed_evidence
        ):
            raise PretaxScopePolicyError("Pretax reviewed evidence IDs must be unique")


@dataclass(frozen=True)
class PretaxScopePolicy:
    """Immutable versioned registry of manually reviewed Pretax approvals."""

    policy_id: str
    version: str
    entries: tuple[PretaxScopePolicyEntry, ...]

    def __post_init__(self) -> None:
        if (
            self.policy_id != PRETAX_SCOPE_POLICY_ID
            or self.version != PRETAX_SCOPE_POLICY_VERSION
            or not self.entries
            or len({entry.key for entry in self.entries}) != len(self.entries)
        ):
            raise PretaxScopePolicyError("Pretax scope policy is structurally invalid")


def _entry(
    ticker: str,
    cik: int,
    accession: str,
    start: date,
    end: date,
    value: int,
    filing_name: str,
    location: str,
) -> PretaxScopePolicyEntry:
    accession_path = accession.replace("-", "")
    filing_url = (
        f"https://www.sec.gov/Archives/edgar/data/{cik}/"
        f"{accession_path}/{filing_name}"
    )
    evidence = ReviewedPolicyEvidence(
        evidence_id=f"{ticker.lower()}-{end.year}-pretax-scope",
        source_url=filing_url,
        filing_location=location,
        research_artifact="docs/pretax-equity-method-note-evidence.md",
        reviewed_on=date(2026, 10, 9),
        review_status="approved",
        rationale=(
            "The selected filing directly binds equity-method activity to a "
            "component of consolidated earnings before income taxes."
        ),
        content_digest=(
            "MA: equity-method results are included in other income (expense), "
            "net; CVX: affiliate earnings enter before-tax consolidated earnings."
        ),
    )
    return PretaxScopePolicyEntry(
        company_cik=cik,
        accession_number=accession,
        report_date=end,
        annual_start=start,
        annual_end=end,
        taxonomy=PRETAX_SCOPE_CANDIDATE.taxonomy,
        concept=PRETAX_SCOPE_CANDIDATE.name,
        unit="USD",
        economic_scope=PretaxEconomicScope.INCLUDED_PRETAX,
        expected_value=value,
        reviewed_evidence=(evidence,),
    )


PRETAX_SCOPE_EQUIVALENCE_POLICY = PretaxScopePolicy(
    policy_id=PRETAX_SCOPE_POLICY_ID,
    version=PRETAX_SCOPE_POLICY_VERSION,
    entries=(
        _entry(
            "MA",
            1141391,
            "0001141391-22-000023",
            date(2021, 1, 1),
            date(2021, 12, 31),
            10_307_000_000,
            "ma-20211231.htm",
            "Note 1, Investments — Equity method; Consolidated Statement of Operations",
        ),
        _entry(
            "MA",
            1141391,
            "0001141391-23-000020",
            date(2022, 1, 1),
            date(2022, 12, 31),
            11_732_000_000,
            "ma-20221231.htm",
            "Note 1, Investments — Equity method; Consolidated Statement of Operations",
        ),
        _entry(
            "MA",
            1141391,
            "0001141391-24-000022",
            date(2023, 1, 1),
            date(2023, 12, 31),
            13_639_000_000,
            "ma-20231231.htm",
            "Note 1, Investments — Equity method; Consolidated Statement of Operations",
        ),
        _entry(
            "CVX",
            93410,
            "0000093410-22-000019",
            date(2021, 1, 1),
            date(2021, 12, 31),
            21_639_000_000,
            "cvx-20211231.htm",
            "Note 15, Investments and Advances; Consolidated Statement of Income",
        ),
        _entry(
            "CVX",
            93410,
            "0000093410-23-000009",
            date(2022, 1, 1),
            date(2022, 12, 31),
            49_674_000_000,
            "cvx-20221231.htm",
            "Note 15, Investments and Advances; Consolidated Statement of Income",
        ),
        _entry(
            "CVX",
            93410,
            "0000093410-24-000013",
            date(2023, 1, 1),
            date(2023, 12, 31),
            29_584_000_000,
            "cvx-20231231.htm",
            "Note 15, Investments and Advances; Consolidated Statement of Income",
        ),
        _entry(
            "CVX",
            93410,
            "0000093410-25-000009",
            date(2024, 1, 1),
            date(2024, 12, 31),
            27_506_000_000,
            "cvx-20241231.htm",
            "Note 15, Investments and Advances; Consolidated Statement of Income",
        ),
        _entry(
            "CVX",
            93410,
            "0000093410-26-000078",
            date(2025, 1, 1),
            date(2025, 12, 31),
            19_743_000_000,
            "cvx-20251231.htm",
            "Note 15, Investments and Advances; Consolidated Statement of Income",
        ),
    ),
)


def pretax_scope_entry_for(
    company_cik: int,
    accession_number: str,
    report_date: date,
    annual_start: date,
    annual_end: date,
    taxonomy: str,
    concept: str,
    unit: str,
    economic_scope: PretaxEconomicScope,
    policy: PretaxScopePolicy = PRETAX_SCOPE_EQUIVALENCE_POLICY,
) -> PretaxScopePolicyEntry | None:
    """Return an entry only for an exact complete-key match."""
    key = (
        company_cik,
        accession_number,
        report_date,
        annual_start,
        annual_end,
        taxonomy,
        concept,
        unit,
        economic_scope,
    )
    return next((entry for entry in policy.entries if entry.key == key), None)


def apply_curated_pretax_scope_policy(
    bucket: FilingFactObservations,
    direct_result: HistoricalMetricResult,
    company_cik: int,
    source_url: str,
    annual_period: AnnualPeriodResolution | None,
    filing_xbrl: SECFilingXBRL | None,
    policy: PretaxScopePolicy = PRETAX_SCOPE_EQUIVALENCE_POLICY,
) -> HistoricalMetricResult:
    """Apply current-concept-first, exact-accession curated Pretax approval."""
    if direct_result.metric is not FinancialMetric.PRETAX_INCOME:
        raise PretaxScopePolicyError("Curated Pretax policy received another metric")
    if isinstance(direct_result, AmbiguousHistoricalMetric):
        return direct_result
    filing = bucket.filing
    if (
        filing.form != "10-K"
        or filing.report_date is None
        or not isinstance(annual_period, ResolvedAnnualPeriod)
    ):
        return direct_result
    entry = pretax_scope_entry_for(
        company_cik,
        filing.accession_number,
        filing.report_date,
        annual_period.start,
        annual_period.end,
        PRETAX_SCOPE_CANDIDATE.taxonomy,
        PRETAX_SCOPE_CANDIDATE.name,
        "USD",
        PretaxEconomicScope.INCLUDED_PRETAX,
        policy,
    )
    if entry is None:
        return direct_result

    candidates = _eligible_company_facts_candidates(bucket, entry)
    if not candidates:
        return direct_result
    if _has_exact_duplicate(candidates):
        raise PretaxScopePolicyError("Curated Pretax candidate contains an exact duplicate")
    candidate_evidence = tuple(_fact_evidence(item, source_url) for item in candidates)
    values = {item.value for item in candidate_evidence}
    if len(values) != 1:
        return AmbiguousHistoricalMetric(
            metric=FinancialMetric.PRETAX_INCOME,
            reason=AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
            candidates=candidate_evidence,
        )
    value = next(iter(values))
    if value != entry.expected_value:
        return direct_result

    filing_occurrences = _eligible_filing_occurrences(filing_xbrl, entry)
    if not filing_occurrences:
        return direct_result
    signatures = {
        _semantic_signature(occurrence) for occurrence in filing_occurrences
    }
    filing_values = {occurrence.fact.numeric_value for occurrence in filing_occurrences}
    if filing_values != {Decimal(str(value))}:
        return AmbiguousHistoricalMetric(
            metric=FinancialMetric.PRETAX_INCOME,
            reason=AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
            candidates=candidate_evidence,
        )
    if len(signatures) != 1:
        raise PretaxScopePolicyError(
            "Curated Pretax facts have inconsistent eligible semantic signatures"
        )

    filing_evidence = tuple(
        _filing_xbrl_evidence(occurrence, filing_xbrl, ordinal)
        for ordinal, occurrence in enumerate(filing_occurrences, 1)
    )

    policy_provenance = HistoricalPolicyProvenance(
        policy_id=policy.policy_id,
        policy_version=policy.version,
        economic_scope=entry.economic_scope.value,
        company_cik=entry.company_cik,
        accession_number=entry.accession_number,
        report_date=entry.report_date,
        annual_start=entry.annual_start,
        annual_end=entry.annual_end,
        taxonomy=entry.taxonomy,
        concept=entry.concept,
        unit=entry.unit,
        reviewed_evidence=entry.reviewed_evidence,
        filing_xbrl_evidence=filing_evidence,
    )
    chosen = candidate_evidence[0]
    confirming = candidate_evidence[1:]
    if isinstance(direct_result, NormalizedHistoricalValue):
        if direct_result.value != value:
            return AmbiguousHistoricalMetric(
                metric=FinancialMetric.PRETAX_INCOME,
                reason=AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                candidates=(
                    direct_result.chosen_source,
                    *direct_result.confirming_sources,
                    *candidate_evidence,
                ),
            )
        return NormalizedHistoricalValue(
            metric=direct_result.metric,
            value=direct_result.value,
            unit=direct_result.unit,
            period=direct_result.period,
            chosen_source=direct_result.chosen_source,
            confirming_sources=(
                *direct_result.confirming_sources,
                *candidate_evidence,
            ),
        )
    if not isinstance(direct_result, MissingHistoricalMetric):
        raise PretaxScopePolicyError("Curated Pretax direct result is invalid")
    return NormalizedHistoricalValue(
        metric=FinancialMetric.PRETAX_INCOME,
        value=value,
        unit=entry.unit,
        period=HistoricalPeriod(entry.annual_start, entry.annual_end),
        chosen_source=chosen,
        confirming_sources=confirming,
        policy_provenance=policy_provenance,
    )


def _eligible_company_facts_candidates(
    bucket: FilingFactObservations,
    entry: PretaxScopePolicyEntry,
) -> tuple[SelectedFactObservation, ...]:
    return tuple(
        item
        for item in bucket.for_concept(entry.taxonomy, entry.concept)
        if item.observation.accession_number == entry.accession_number
        and item.relationship is ObservationRelationship.CURRENT
        and item.period_type is ObservationPeriodType.DURATION
        and item.observation.start == entry.annual_start
        and item.observation.end == entry.annual_end
        and item.observation.form == "10-K"
        and item.observation.unit == entry.unit
        and _is_numeric(item.observation.value)
    )


def _has_exact_duplicate(candidates: tuple[SelectedFactObservation, ...]) -> bool:
    signatures = tuple(
        (
            item.taxonomy,
            item.concept,
            item.observation.unit,
            item.observation.value,
            item.observation.start,
            item.observation.end,
            item.observation.accession_number,
            item.observation.form,
            item.observation.filed,
            item.observation.fiscal_year,
            item.observation.fiscal_period,
            item.observation.frame,
        )
        for item in candidates
    )
    return len(set(signatures)) != len(signatures)


def _eligible_filing_occurrences(
    filing_xbrl: SECFilingXBRL | None,
    entry: PretaxScopePolicyEntry,
) -> tuple[_CandidateOccurrence, ...]:
    if filing_xbrl is None or (
        filing_xbrl.company.cik != entry.company_cik
        or filing_xbrl.filing.accession_number != entry.accession_number
        or filing_xbrl.filing.report_date != entry.report_date
    ):
        return ()
    contexts_by_id = {context.context_id: context for context in filing_xbrl.contexts}
    if len(contexts_by_id) != len(filing_xbrl.contexts):
        raise PretaxScopePolicyError("Curated Pretax contexts are not unique")

    annual_occurrences = []
    for source_index, fact in enumerate(filing_xbrl.facts):
        if (
            fact.concept != entry.concept
            or not fact.namespace.startswith("http://fasb.org/us-gaap/")
            or fact.start != entry.annual_start
            or fact.end != entry.annual_end
        ):
            continue
        context = contexts_by_id.get(fact.context_id)
        if context is None:
            raise PretaxScopePolicyError(
                "Curated Pretax fact references a missing context"
            )
        if (
            fact.start != context.start
            or fact.end != context.end
            or fact.dimensions != context.dimensions
        ):
            raise PretaxScopePolicyError(
                "Curated Pretax fact/context linkage is inconsistent"
            )
        if (
            fact.accession_number != entry.accession_number
            or fact.source_url != filing_xbrl.source_url
        ):
            raise PretaxScopePolicyError(
                "Curated Pretax fact source or accession is inconsistent"
            )
        if fact.unit is not None and fact.unit_ref != fact.unit.unit_id:
            raise PretaxScopePolicyError(
                "Curated Pretax fact/unit linkage is inconsistent"
            )
        normalized_cik = _normalized_context_cik(context, entry.company_cik)
        if normalized_cik is None:
            raise PretaxScopePolicyError(
                "Curated Pretax fact has inconsistent entity identity"
            )
        annual_occurrences.append(
            _CandidateOccurrence(
                source_index=source_index,
                fact=fact,
                context=context,
                normalized_cik=normalized_cik,
                normalized_unit=_normalized_unit(fact),
            )
        )

    _validate_nil_numeric_collisions(tuple(annual_occurrences))
    if any(
        not occurrence.fact.dimensions
        and not occurrence.fact.is_nil
        and isinstance(occurrence.fact.numeric_value, Decimal)
        and occurrence.normalized_unit != entry.unit
        for occurrence in annual_occurrences
    ):
        return ()
    eligible = tuple(
        occurrence
        for occurrence in annual_occurrences
        if _is_eligible_occurrence(occurrence, entry)
    )
    return tuple(sorted(eligible, key=_occurrence_order_key))


def _is_eligible_occurrence(
    occurrence: _CandidateOccurrence,
    entry: PretaxScopePolicyEntry,
) -> bool:
    fact = occurrence.fact
    unit = fact.unit
    return (
        fact.concept == entry.concept
        and fact.accession_number == entry.accession_number
        and fact.start == entry.annual_start
        and fact.end == entry.annual_end
        and not fact.dimensions
        and fact.unit_ref is not None
        and unit is not None
        and occurrence.normalized_unit == entry.unit
        and isinstance(fact.numeric_value, Decimal)
        and fact.numeric_value.is_finite()
        and not fact.is_nil
    )


def _normalized_context_cik(
    context: FilingXBRLContext,
    expected_cik: int,
) -> int | None:
    value = context.entity_identifier
    if (
        context.entity_identifier_scheme != "http://www.sec.gov/CIK"
        or not value
        or not value.isdigit()
    ):
        return None
    normalized = int(value)
    return normalized if normalized == expected_cik else None


def _normalized_unit(fact: FilingXBRLFact) -> str | None:
    unit = fact.unit
    if (
        fact.unit_ref is None
        or unit is None
        or unit.denominator_measures
        or len(unit.numerator_measures) != 1
    ):
        return None
    measure = unit.numerator_measures[0]
    if measure.namespace == _USD_NAMESPACE and measure.local_name == "USD":
        return "USD"
    return None


def _semantic_signature(occurrence: _CandidateOccurrence) -> tuple[object, ...]:
    fact = occurrence.fact
    return (
        fact.namespace,
        fact.concept,
        occurrence.normalized_cik,
        fact.accession_number,
        fact.start,
        fact.end,
        fact.dimensions,
        occurrence.normalized_unit,
        fact.numeric_value,
        fact.is_nil,
    )


def _nil_collision_key(occurrence: _CandidateOccurrence) -> tuple[object, ...]:
    fact = occurrence.fact
    return (
        fact.namespace,
        fact.concept,
        occurrence.normalized_cik,
        fact.accession_number,
        fact.start,
        fact.end,
        fact.dimensions,
    )


def _validate_nil_numeric_collisions(
    occurrences: tuple[_CandidateOccurrence, ...],
) -> None:
    by_key: dict[tuple[object, ...], set[str]] = {}
    for occurrence in occurrences:
        statuses = by_key.setdefault(_nil_collision_key(occurrence), set())
        statuses.add(
            "nil"
            if occurrence.fact.is_nil
            else "numeric"
            if isinstance(occurrence.fact.numeric_value, Decimal)
            else "malformed"
        )
    if any(
        "nil" in statuses and "numeric" in statuses
        for statuses in by_key.values()
    ):
        raise PretaxScopePolicyError(
            "Curated Pretax semantic context contains nil and numeric facts"
        )


def _occurrence_order_key(
    occurrence: _CandidateOccurrence,
) -> tuple[object, ...]:
    fact = occurrence.fact
    return (
        fact.context_id,
        fact.unit_ref or "",
        fact.raw_value or "",
        fact.decimals or "",
        occurrence.source_index,
    )


def _filing_xbrl_evidence(
    occurrence: _CandidateOccurrence,
    filing_xbrl: SECFilingXBRL | None,
    ordinal: int,
) -> FilingXBRLEvidence:
    fact = occurrence.fact
    if filing_xbrl is None or fact.numeric_value is None:
        raise PretaxScopePolicyError("Pretax filing-XBRL evidence is unavailable")

    return FilingXBRLEvidence(
        source_kind=EvidenceSourceKind.FILING_XBRL,
        source_url=fact.source_url,
        namespace=fact.namespace,
        concept=fact.concept,
        raw_value=fact.raw_value,
        value=fact.numeric_value,
        unit="USD",
        start=fact.start,
        end=fact.end,
        accession_number=fact.accession_number,
        observation_form=filing_xbrl.filing.form,
        observation_filed=filing_xbrl.filing.filing_date,
        filing_report_date=filing_xbrl.filing.report_date,
        primary_document=filing_xbrl.filing.primary_document,
        retrieved_at=filing_xbrl.retrieved_at,
        context_id=fact.context_id,
        dimensions=fact.dimensions,
        decimals=fact.decimals,
        is_nil=fact.is_nil,
        unit_ref=fact.unit_ref,
        occurrence_ordinal=ordinal,
    )


def _fact_evidence(
    selected: SelectedFactObservation,
    source_url: str,
) -> FactEvidence:
    observation = selected.observation
    if not _is_numeric(observation.value):
        raise PretaxScopePolicyError("Curated Pretax evidence is not numeric")
    return FactEvidence(
        source_kind=EvidenceSourceKind.COMPANY_FACTS,
        source_url=source_url,
        taxonomy=selected.taxonomy,
        concept=selected.concept,
        value=observation.value,
        unit=observation.unit,
        start=observation.start,
        end=observation.end,
        accession_number=observation.accession_number,
        observation_form=observation.form,
        observation_filed=observation.filed,
        fiscal_year=observation.fiscal_year,
        fiscal_period=observation.fiscal_period,
        frame=observation.frame,
    )


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
