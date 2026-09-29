"""Resolve evidence-backed derived annual financial values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationPeriodType,
    ObservationRelationship,
    SelectedFactObservation,
)

from .concepts import ConceptKey, FinancialMetric
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    DerivationOperation,
    DerivedHistoricalValue,
    EvidenceSourceKind,
    FactEvidence,
    HistoricalMetricResult,
    HistoricalPeriod,
    MissingHistoricalMetric,
    MissingReason,
)


class DerivationPolicyError(ValueError):
    """Raised when a financial derivation policy is structurally invalid."""


@dataclass(frozen=True)
class MetricDerivationPolicy:
    """An evidence-backed derivation approved for specific SEC companies."""

    policy_id: str
    metric: FinancialMetric
    operation: DerivationOperation
    operands: tuple[ConceptKey, ...]
    applicable_ciks: frozenset[int]
    source_kind: EvidenceSourceKind = EvidenceSourceKind.COMPANY_FACTS

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id:
            raise DerivationPolicyError("Derivation policy ID must not be empty")
        if not isinstance(self.metric, FinancialMetric):
            raise DerivationPolicyError(
                "Derivation policy metric must be a FinancialMetric"
            )
        if self.operation is not DerivationOperation.ADD:
            raise DerivationPolicyError("Derivation policy operation must be ADD")
        if (
            not isinstance(self.operands, tuple)
            or len(self.operands) < 2
            or not all(isinstance(operand, ConceptKey) for operand in self.operands)
        ):
            raise DerivationPolicyError(
                "ADD derivation policy must have at least two concept operands"
            )
        if len(set(self.operands)) != len(self.operands):
            raise DerivationPolicyError(
                "Derivation policy must not contain duplicate operands"
            )
        if (
            not isinstance(self.applicable_ciks, frozenset)
            or not self.applicable_ciks
            or not all(
                isinstance(cik, int) and not isinstance(cik, bool) and cik >= 0
                for cik in self.applicable_ciks
            )
        ):
            raise DerivationPolicyError(
                "Derivation policy must have nonnegative integer CIKs"
            )
        if self.source_kind is not EvidenceSourceKind.COMPANY_FACTS:
            raise DerivationPolicyError(
                "Only Company Facts derivation operands are supported"
            )


MSFT_D_AND_A_DERIVATION_POLICY = MetricDerivationPolicy(
    policy_id="msft_annual_d_and_a_v1",
    metric=FinancialMetric.D_AND_A,
    operation=DerivationOperation.ADD,
    operands=(
        ConceptKey(taxonomy="us-gaap", name="Depreciation"),
        ConceptKey(taxonomy="us-gaap", name="AmortizationOfIntangibleAssets"),
    ),
    applicable_ciks=frozenset({789019}),
)

ANNUAL_DERIVATION_POLICIES: tuple[MetricDerivationPolicy, ...] = (
    MSFT_D_AND_A_DERIVATION_POLICY,
)


def applicable_derivation_policy(
    metric: FinancialMetric,
    cik: int,
    policies: tuple[MetricDerivationPolicy, ...],
) -> MetricDerivationPolicy | None:
    """Return the unique policy approved for a metric and SEC company."""
    _validate_policies(policies)
    matches = tuple(
        policy
        for policy in policies
        if policy.metric is metric and cik in policy.applicable_ciks
    )
    if len(matches) > 1:
        raise DerivationPolicyError(
            f"Multiple derivation policies apply to {metric.value!r} for CIK {cik}"
        )
    return matches[0] if matches else None


def derive_annual_metric(
    bucket: FilingFactObservations,
    policy: MetricDerivationPolicy,
    source_url: str,
) -> HistoricalMetricResult:
    """Resolve one approved same-period additive annual derivation."""
    filing = bucket.filing
    if filing.form != "10-K" or filing.report_date is None:
        raise DerivationPolicyError(
            "Annual derivation requires an exact 10-K with a report date"
        )

    chosen_operands = []
    for concept in policy.operands:
        configured = bucket.for_concept(concept.taxonomy, concept.name)
        for selected in configured:
            if selected.observation.accession_number != filing.accession_number:
                raise DerivationPolicyError(
                    "Derivation operand accession does not match selected filing"
                )
        candidates = tuple(
            selected
            for selected in configured
            if _is_valid_annual_operand(selected, filing.report_date)
        )
        if not candidates:
            return MissingHistoricalMetric(
                metric=policy.metric,
                reason=MissingReason.NO_VALID_DERIVATION_OPERANDS,
                examined_concepts=policy.operands,
            )
        if len(candidates) > 1:
            return _ambiguous(policy, candidates, source_url)
        chosen_operands.append(candidates[0])

    periods = {
        (selected.observation.start, selected.observation.end)
        for selected in chosen_operands
    }
    if len(periods) != 1:
        return _ambiguous(policy, tuple(chosen_operands), source_url)

    start, end = next(iter(periods))
    if start is None:
        raise DerivationPolicyError("Duration derivation operand has no start date")

    values = tuple(selected.observation.value for selected in chosen_operands)
    if not all(_is_numeric(value) for value in values):
        raise DerivationPolicyError("Chosen derivation operand is not numeric")

    return DerivedHistoricalValue(
        metric=policy.metric,
        value=sum(values),
        unit="USD",
        period=HistoricalPeriod(start=start, end=end),
        policy_id=policy.policy_id,
        operation=policy.operation,
        operands=tuple(
            _fact_evidence(selected, source_url) for selected in chosen_operands
        ),
    )


def _is_valid_annual_operand(
    selected: SelectedFactObservation,
    report_date: date,
) -> bool:
    observation = selected.observation
    return (
        selected.relationship is ObservationRelationship.CURRENT
        and selected.period_type is ObservationPeriodType.DURATION
        and observation.end == report_date
        and observation.unit == "USD"
        and _is_numeric(observation.value)
    )


def _ambiguous(
    policy: MetricDerivationPolicy,
    candidates: tuple[SelectedFactObservation, ...],
    source_url: str,
) -> AmbiguousHistoricalMetric:
    return AmbiguousHistoricalMetric(
        metric=policy.metric,
        reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
        candidates=tuple(
            _fact_evidence(selected, source_url) for selected in candidates
        ),
    )


def _fact_evidence(
    selected: SelectedFactObservation,
    source_url: str,
) -> FactEvidence:
    observation = selected.observation
    if not _is_numeric(observation.value):
        raise DerivationPolicyError("Derivation evidence value is not numeric")
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


def _validate_policies(policies: tuple[MetricDerivationPolicy, ...]) -> None:
    if not isinstance(policies, tuple):
        raise DerivationPolicyError("Derivation policies must be a tuple")
    if not all(isinstance(policy, MetricDerivationPolicy) for policy in policies):
        raise DerivationPolicyError("Derivation policies contain an invalid policy")
