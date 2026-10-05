"""Normalize selected annual SEC facts into typed historical results."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from valuation_platform.sec.company_facts import SECFactValue
from valuation_platform.sec.filing_xbrl import SECFilingXBRL
from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationPeriodType,
    ObservationRelationship,
    SelectedFactObservation,
    SelectedFactObservations,
)
from .concepts import (
    ANNUAL_METRIC_POLICIES,
    ConceptKey,
    FinancialMetric,
    MetricConceptPolicy,
)
from .derived import (
    ANNUAL_DERIVATION_POLICIES,
    MetricDerivationPolicy,
    applicable_derivation_policy,
    derive_annual_metric,
    derive_reported_effective_tax_rate,
)
from .diluted_shares import (
    GOOGL_DILUTED_SHARES_DERIVATION_POLICY,
    derive_googl_diluted_weighted_average_shares,
)
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    EvidenceSourceKind,
    FactEvidence,
    HistoricalFilingResult,
    HistoricalMetricResult,
    HistoricalPeriod,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedHistoricalFinancials,
    NormalizedHistoricalValue,
)


class NormalizationError(Exception):
    """Raised when normalization input or configuration is structurally invalid."""


def normalize_annual_financials(
    selected_facts: SelectedFactObservations,
    policies: tuple[MetricConceptPolicy, ...] = ANNUAL_METRIC_POLICIES,
    derivation_policies: tuple[
        MetricDerivationPolicy, ...
    ] = ANNUAL_DERIVATION_POLICIES,
    *,
    filing_xbrl: tuple[SECFilingXBRL, ...] = (),
) -> NormalizedHistoricalFinancials:
    """Normalize configured metrics across selected annual filing buckets."""
    _validate_policies(policies)
    filing_xbrl_by_accession = _validate_filing_xbrl(
        filing_xbrl,
        selected_facts.company.cik,
    )
    annual = tuple(
        HistoricalFilingResult(
            filing=bucket.filing,
            metrics=_resolve_filing_metrics(
                bucket,
                selected_facts.company.cik,
                selected_facts.source_url,
                policies,
                derivation_policies,
                filing_xbrl_by_accession.get(bucket.filing.accession_number),
            ),
        )
        for bucket in selected_facts.annual
    )
    return NormalizedHistoricalFinancials(
        company=selected_facts.company,
        company_facts_source_url=selected_facts.source_url,
        company_facts_retrieved_at=selected_facts.retrieved_at,
        annual=annual,
    )


def _resolve_filing_metrics(
    bucket: FilingFactObservations,
    company_cik: int,
    source_url: str,
    policies: tuple[MetricConceptPolicy, ...],
    derivation_policies: tuple[MetricDerivationPolicy, ...],
    filing_xbrl: SECFilingXBRL | None,
) -> tuple[HistoricalMetricResult, ...]:
    direct_results = tuple(
        _resolve_with_derivation(
            bucket,
            policy,
            company_cik,
            source_url,
            derivation_policies,
            filing_xbrl,
        )
        for policy in policies
    )
    configured_metrics = {policy.metric for policy in policies}
    required_etr_metrics = {
        FinancialMetric.PRETAX_INCOME,
        FinancialMetric.INCOME_TAX_EXPENSE,
    }
    if not required_etr_metrics.issubset(configured_metrics):
        return direct_results

    filing = bucket.filing
    if filing.report_date is None:
        raise NormalizationError(
            f"Annual filing {filing.accession_number!r} has no report date"
        )
    reported_etr = derive_reported_effective_tax_rate(
        filing.accession_number,
        filing.report_date,
        direct_results,
    )
    ordered = []
    for result in direct_results:
        ordered.append(result)
        if result.metric is FinancialMetric.INCOME_TAX_EXPENSE:
            ordered.append(reported_etr)
    return tuple(ordered)


def _resolve_with_derivation(
    bucket: FilingFactObservations,
    policy: MetricConceptPolicy,
    company_cik: int,
    source_url: str,
    derivation_policies: tuple[MetricDerivationPolicy, ...],
    filing_xbrl: SECFilingXBRL | None,
) -> HistoricalMetricResult:
    direct = _resolve_metric(bucket, policy, source_url)
    if policy.metric is FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES:
        return derive_googl_diluted_weighted_average_shares(
            bucket,
            direct,
            filing_xbrl,
            company_cik,
            GOOGL_DILUTED_SHARES_DERIVATION_POLICY,
        )
    if not isinstance(direct, MissingHistoricalMetric):
        return direct
    derivation_policy = applicable_derivation_policy(
        policy.metric,
        company_cik,
        derivation_policies,
    )
    if derivation_policy is None:
        return direct
    return derive_annual_metric(bucket, derivation_policy, source_url)


def _resolve_metric(
    bucket: FilingFactObservations,
    policy: MetricConceptPolicy,
    source_url: str,
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
        and _is_policy_numeric(selected.observation.value, policy)
        and (
            policy.required_observation_form is None
            or selected.observation.form == policy.required_observation_form
        )
    )
    if not period_candidates:
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
            examined_concepts=policy.candidates,
        )

    supported_candidates = tuple(
        selected
        for selected in period_candidates
        if selected.observation.unit == policy.unit
    )
    if not supported_candidates:
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
            examined_concepts=policy.candidates,
        )

    periods = {
        (selected.observation.start, selected.observation.end)
        for selected in supported_candidates
    }
    if len(periods) > 1:
        return _ambiguous(
            policy.metric,
            AmbiguityReason.MULTIPLE_ANNUAL_PERIODS,
            supported_candidates,
            source_url,
        )

    start, end = next(iter(periods))
    if start is None:
        raise NormalizationError(
            "Duration observation unexpectedly has no start date for "
            f"accession {filing.accession_number!r}"
        )

    for candidate in policy.candidates:
        same_concept = tuple(
            selected
            for selected in supported_candidates
            if ConceptKey(selected.taxonomy, selected.concept) == candidate
        )
        if len(same_concept) > 1:
            return _ambiguous(
                policy.metric,
                AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                same_concept,
                source_url,
            )

    by_concept = {
        ConceptKey(selected.taxonomy, selected.concept): selected
        for selected in supported_candidates
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
    if not _is_policy_numeric(chosen_value, policy):
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
            source_url,
        )

    observation = chosen.observation
    return NormalizedHistoricalValue(
        metric=policy.metric,
        value=Decimal(chosen_value) if policy.decimal_output else chosen_value,
        unit=observation.unit,
        period=HistoricalPeriod(start=start, end=end),
        chosen_source=_fact_evidence(chosen, source_url),
        confirming_sources=tuple(
            _fact_evidence(item, source_url) for item in confirming
        ),
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
    source_url: str,
) -> AmbiguousHistoricalMetric:
    return AmbiguousHistoricalMetric(
        metric=metric,
        reason=reason,
        candidates=tuple(
            _fact_evidence(selected, source_url)
            for selected in sorted(candidates, key=_selected_order_key)
        ),
    )


def _selected_order_key(selected: SelectedFactObservation) -> tuple[object, ...]:
    observation = selected.observation
    return (
        selected.taxonomy,
        selected.concept,
        observation.unit,
        observation.start or date.min,
        observation.end,
        str(observation.value),
        observation.accession_number,
    )


def _fact_evidence(
    selected: SelectedFactObservation,
    source_url: str,
) -> FactEvidence:
    observation = selected.observation
    if not _is_numeric(observation.value):
        raise NormalizationError("Financial fact evidence value is not numeric")
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


def _is_numeric(value: SECFactValue) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_policy_numeric(
    value: SECFactValue,
    policy: MetricConceptPolicy,
) -> bool:
    if policy.integer_only:
        return isinstance(value, int) and not isinstance(value, bool)
    return _is_numeric(value)


def _validate_filing_xbrl(
    filings: tuple[SECFilingXBRL, ...],
    company_cik: int,
) -> dict[str, SECFilingXBRL]:
    if not isinstance(filings, tuple):
        raise NormalizationError("Filing-XBRL input must be a tuple")
    by_accession: dict[str, SECFilingXBRL] = {}
    for filing_xbrl in filings:
        if not isinstance(filing_xbrl, SECFilingXBRL):
            raise NormalizationError("Filing-XBRL input contains an invalid artifact")
        if filing_xbrl.company.cik != company_cik:
            raise NormalizationError(
                "Filing-XBRL company does not match selected company"
            )
        accession = filing_xbrl.filing.accession_number
        if accession in by_accession:
            raise NormalizationError(
                f"Filing-XBRL input contains duplicate accession {accession!r}"
            )
        by_accession[accession] = filing_xbrl
    return by_accession


def _validate_policies(policies: tuple[MetricConceptPolicy, ...]) -> None:
    if not isinstance(policies, tuple) or not policies:
        raise NormalizationError("At least one metric concept policy is required")
    if not all(isinstance(policy, MetricConceptPolicy) for policy in policies):
        raise NormalizationError("Metric concept policies contain an invalid policy")
    metrics = [policy.metric for policy in policies]
    if len(set(metrics)) != len(metrics):
        raise NormalizationError("Metric concept policies contain duplicate metrics")
