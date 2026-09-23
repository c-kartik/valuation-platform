"""Normalize selected annual SEC facts into typed historical results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import TypeAlias

from valuation_platform.sec.company_facts import SECFactValue
from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationPeriodType,
    ObservationRelationship,
    SelectedFactObservation,
    SelectedFactObservations,
)
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity

from .concepts import (
    ANNUAL_METRIC_POLICIES,
    ConceptKey,
    FinancialMetric,
    MetricConceptPolicy,
)


class NormalizationError(Exception):
    """Raised when normalization input or configuration is structurally invalid."""


class MissingReason(str, Enum):
    """Expected reasons a selected filing has no normalized metric value."""

    NO_CONFIGURED_CONCEPT_OBSERVATION = "no_configured_concept_observation"
    NO_VALID_CURRENT_ANNUAL_OBSERVATION = "no_valid_current_annual_observation"


class AmbiguityReason(str, Enum):
    """Reasons available observations cannot produce one annual value."""

    CONFLICTING_CONCEPT_VALUES = "conflicting_concept_values"
    MULTIPLE_ANNUAL_PERIODS = "multiple_annual_periods"


@dataclass(frozen=True)
class HistoricalPeriod:
    """The actual economic duration represented by a normalized value."""

    start: date
    end: date


@dataclass(frozen=True)
class FactEvidence:
    """Compact SEC provenance for one candidate financial fact."""

    taxonomy: str
    concept: str
    value: int | float
    unit: str
    start: date | None
    end: date
    accession_number: str
    observation_form: str
    observation_filed: date
    fiscal_year: int | None
    fiscal_period: str | None
    frame: str | None


@dataclass(frozen=True)
class NormalizedHistoricalValue:
    """One resolved standardized annual financial value."""

    metric: FinancialMetric
    value: int | float
    unit: str
    period: HistoricalPeriod
    chosen_source: FactEvidence
    confirming_sources: tuple[FactEvidence, ...]


@dataclass(frozen=True)
class MissingHistoricalMetric:
    """A metric that has no usable observation in one selected filing."""

    metric: FinancialMetric
    reason: MissingReason
    examined_concepts: tuple[ConceptKey, ...]


@dataclass(frozen=True)
class AmbiguousHistoricalMetric:
    """A metric with competing observations that cannot be resolved safely."""

    metric: FinancialMetric
    reason: AmbiguityReason
    candidates: tuple[FactEvidence, ...]


HistoricalMetricResult: TypeAlias = (
    NormalizedHistoricalValue | MissingHistoricalMetric | AmbiguousHistoricalMetric
)


@dataclass(frozen=True)
class HistoricalFilingResult:
    """Normalized metric results for one selected annual filing."""

    filing: SECFiling
    metrics: tuple[HistoricalMetricResult, ...]


@dataclass(frozen=True)
class NormalizedHistoricalFinancials:
    """Compact annual financial history with company and SEC provenance."""

    company: SECCompanyIdentity
    company_facts_source_url: str
    company_facts_retrieved_at: datetime
    annual: tuple[HistoricalFilingResult, ...]


def normalize_annual_financials(
    selected_facts: SelectedFactObservations,
    policies: tuple[MetricConceptPolicy, ...] = ANNUAL_METRIC_POLICIES,
) -> NormalizedHistoricalFinancials:
    """Normalize configured metrics across selected annual filing buckets."""
    _validate_policies(policies)
    annual = tuple(
        HistoricalFilingResult(
            filing=bucket.filing,
            metrics=tuple(_resolve_metric(bucket, policy) for policy in policies),
        )
        for bucket in selected_facts.annual
    )
    return NormalizedHistoricalFinancials(
        company=selected_facts.company,
        company_facts_source_url=selected_facts.source_url,
        company_facts_retrieved_at=selected_facts.retrieved_at,
        annual=annual,
    )


def _resolve_metric(
    bucket: FilingFactObservations,
    policy: MetricConceptPolicy,
) -> HistoricalMetricResult:
    filing = bucket.filing
    if filing.form != "10-K":
        raise NormalizationError(
            f"Annual normalization requires exact 10-K, received {filing.form!r} "
            f"for accession {filing.accession_number!r}"
        )
    if filing.report_date is None:
        raise NormalizationError(
            f"Annual filing {filing.accession_number!r} has no report date"
        )

    configured = _configured_observations(bucket, policy)
    if not configured:
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
            examined_concepts=policy.candidates,
        )

    period_candidates = tuple(
        selected
        for selected in configured
        if selected.relationship is ObservationRelationship.CURRENT
        and selected.period_type is ObservationPeriodType.DURATION
        and selected.observation.end == filing.report_date
        and _is_numeric(selected.observation.value)
    )
    if not period_candidates:
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
            examined_concepts=policy.candidates,
        )

    usd_candidates = tuple(
        selected
        for selected in period_candidates
        if selected.observation.unit == "USD"
    )
    if not usd_candidates:
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
            examined_concepts=policy.candidates,
        )

    periods = {
        (selected.observation.start, selected.observation.end)
        for selected in usd_candidates
    }
    if len(periods) > 1:
        return _ambiguous(
            policy.metric,
            AmbiguityReason.MULTIPLE_ANNUAL_PERIODS,
            usd_candidates,
        )

    start, end = next(iter(periods))
    if start is None:
        raise NormalizationError(
            "Duration observation unexpectedly has no start date for "
            f"accession {filing.accession_number!r}"
        )

    by_concept = {
        ConceptKey(selected.taxonomy, selected.concept): selected
        for selected in usd_candidates
    }
    chosen = next(
        (
            by_concept[candidate]
            for candidate in policy.candidates
            if candidate in by_concept
        ),
        None,
    )
    if chosen is None:
        raise NormalizationError(
            f"No configured candidate remained for {policy.metric.value!r}"
        )

    chosen_value = chosen.observation.value
    if not _is_numeric(chosen_value):
        raise NormalizationError("Chosen annual financial value is not numeric")

    confirming = []
    conflicting = []
    chosen_key = ConceptKey(chosen.taxonomy, chosen.concept)
    for candidate_key in policy.candidates:
        other = by_concept.get(candidate_key)
        if other is None or candidate_key == chosen_key:
            continue
        if other.observation.value == chosen_value:
            confirming.append(other)
        else:
            conflicting.append(other)

    if conflicting:
        return _ambiguous(
            policy.metric,
            AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
            (chosen, *confirming, *conflicting),
        )

    observation = chosen.observation
    return NormalizedHistoricalValue(
        metric=policy.metric,
        value=chosen_value,
        unit=observation.unit,
        period=HistoricalPeriod(start=start, end=end),
        chosen_source=_fact_evidence(chosen),
        confirming_sources=tuple(_fact_evidence(item) for item in confirming),
    )


def _configured_observations(
    bucket: FilingFactObservations,
    policy: MetricConceptPolicy,
) -> tuple[SelectedFactObservation, ...]:
    accession = bucket.filing.accession_number
    matches = []
    for concept in policy.candidates:
        for selected in bucket.for_concept(concept.taxonomy, concept.name):
            if selected.observation.accession_number != accession:
                raise NormalizationError(
                    f"Fact accession {selected.observation.accession_number!r} does "
                    f"not match filing accession {accession!r}"
                )
            matches.append(selected)
    return tuple(matches)


def _ambiguous(
    metric: FinancialMetric,
    reason: AmbiguityReason,
    candidates: tuple[SelectedFactObservation, ...],
) -> AmbiguousHistoricalMetric:
    return AmbiguousHistoricalMetric(
        metric=metric,
        reason=reason,
        candidates=tuple(_fact_evidence(selected) for selected in candidates),
    )


def _fact_evidence(selected: SelectedFactObservation) -> FactEvidence:
    observation = selected.observation
    if not _is_numeric(observation.value):
        raise NormalizationError("Financial fact evidence value is not numeric")
    return FactEvidence(
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


def _is_numeric(value: SECFactValue) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_policies(policies: tuple[MetricConceptPolicy, ...]) -> None:
    if not isinstance(policies, tuple) or not policies:
        raise NormalizationError("At least one metric concept policy is required")
    if not all(isinstance(policy, MetricConceptPolicy) for policy in policies):
        raise NormalizationError("Metric concept policies contain an invalid policy")
    metrics = [policy.metric for policy in policies]
    if len(set(metrics)) != len(metrics):
        raise NormalizationError("Metric concept policies contain duplicate metrics")
