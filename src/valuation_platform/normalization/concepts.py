"""Define standardized metrics and their ordered SEC concept candidates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConceptPolicyError(ValueError):
    """Raised when a metric concept policy is structurally invalid."""


class FinancialMetric(str, Enum):
    """Stable identifiers for standardized financial metrics."""

    REVENUE = "revenue"
    OPERATING_INCOME = "operating_income"


@dataclass(frozen=True)
class ConceptKey:
    """An exact taxonomy and concept-name pair."""

    taxonomy: str
    name: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.taxonomy, str)
            or not self.taxonomy
            or not isinstance(self.name, str)
            or not self.name
        ):
            raise ConceptPolicyError("Concept taxonomy and name must not be empty")


@dataclass(frozen=True)
class MetricConceptPolicy:
    """Ordered concept candidates for one standardized metric."""

    metric: FinancialMetric
    candidates: tuple[ConceptKey, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.metric, FinancialMetric):
            raise ConceptPolicyError("Concept policy metric must be a FinancialMetric")
        if not isinstance(self.candidates, tuple) or not self.candidates:
            raise ConceptPolicyError(
                f"Concept policy for {self.metric.value!r} must have candidates"
            )
        if not all(isinstance(candidate, ConceptKey) for candidate in self.candidates):
            raise ConceptPolicyError(
                f"Concept policy for {self.metric.value!r} has an invalid candidate"
            )
        if len(set(self.candidates)) != len(self.candidates):
            raise ConceptPolicyError(
                f"Concept policy for {self.metric.value!r} has duplicate candidates"
            )


REVENUE_POLICY = MetricConceptPolicy(
    metric=FinancialMetric.REVENUE,
    candidates=(
        ConceptKey(
            taxonomy="us-gaap",
            name="RevenueFromContractWithCustomerExcludingAssessedTax",
        ),
        ConceptKey(taxonomy="us-gaap", name="Revenues"),
    ),
)

OPERATING_INCOME_POLICY = MetricConceptPolicy(
    metric=FinancialMetric.OPERATING_INCOME,
    candidates=(ConceptKey(taxonomy="us-gaap", name="OperatingIncomeLoss"),),
)

ANNUAL_METRIC_POLICIES: tuple[MetricConceptPolicy, ...] = (
    REVENUE_POLICY,
    OPERATING_INCOME_POLICY,
)
