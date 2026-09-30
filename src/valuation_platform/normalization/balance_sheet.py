"""Normalize selected annual SEC instant facts into primitive balances."""

from __future__ import annotations

from dataclasses import dataclass

from valuation_platform.sec.company_facts import SECFactValue
from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationPeriodType,
    ObservationRelationship,
    SelectedFactObservation,
    SelectedFactObservations,
)

from .concepts import ConceptKey, FinancialMetric
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    AnnualBalanceSheetFilingResult,
    BalanceSheetMetricResult,
    EvidenceSourceKind,
    FactEvidence,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedAnnualBalanceSheets,
    NormalizedBalanceSheetValue,
)


_META_CIK = 1326801
_GOOGL_CIK = 1652044
_MSFT_CIK = 789019
_AAPL_CIK = 320193
_COST_CIK = 909832


class BalanceSheetNormalizationError(Exception):
    """Raised when balance-sheet input or policy structure is invalid."""


@dataclass(frozen=True)
class BalanceSheetConceptCandidate:
    """One exact concept candidate, optionally restricted to validated CIKs."""

    concept: ConceptKey
    applicable_ciks: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.concept, ConceptKey):
            raise BalanceSheetNormalizationError(
                "Balance-sheet candidate concept must be a ConceptKey"
            )
        if self.applicable_ciks is not None and (
            not isinstance(self.applicable_ciks, tuple)
            or not self.applicable_ciks
            or any(
                not isinstance(cik, int) or isinstance(cik, bool) or cik < 0
                for cik in self.applicable_ciks
            )
            or len(set(self.applicable_ciks)) != len(self.applicable_ciks)
        ):
            raise BalanceSheetNormalizationError(
                "Candidate applicable CIKs must be unique nonnegative integers"
            )

    def applies_to(self, company_cik: int) -> bool:
        """Return whether this candidate is approved for the company."""
        return self.applicable_ciks is None or company_cik in self.applicable_ciks


@dataclass(frozen=True)
class BalanceSheetMetricPolicy:
    """Ordered direct-concept policy for one primitive balance."""

    metric: FinancialMetric
    candidates: tuple[BalanceSheetConceptCandidate, ...]
    allow_equal_value_confirmation: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.metric, FinancialMetric):
            raise BalanceSheetNormalizationError(
                "Balance-sheet policy metric must be a FinancialMetric"
            )
        if not isinstance(self.candidates, tuple) or not self.candidates:
            raise BalanceSheetNormalizationError(
                f"Balance-sheet policy for {self.metric.value!r} must have candidates"
            )
        if not all(
            isinstance(candidate, BalanceSheetConceptCandidate)
            for candidate in self.candidates
        ):
            raise BalanceSheetNormalizationError(
                f"Balance-sheet policy for {self.metric.value!r} has an invalid candidate"
            )
        concept_keys = tuple(candidate.concept for candidate in self.candidates)
        if len(set(concept_keys)) != len(concept_keys):
            raise BalanceSheetNormalizationError(
                f"Balance-sheet policy for {self.metric.value!r} has duplicate concepts"
            )
        if not isinstance(self.allow_equal_value_confirmation, bool):
            raise BalanceSheetNormalizationError(
                "Balance-sheet confirmation setting must be Boolean"
            )


OPERATING_RECEIVABLES_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.OPERATING_RECEIVABLES,
    candidates=(
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "AccountsReceivableNetCurrent")
        ),
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "ReceivablesNetCurrent"),
            applicable_ciks=(_COST_CIK,),
        ),
    ),
)

VENDOR_NONTRADE_RECEIVABLES_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.VENDOR_NONTRADE_RECEIVABLES,
    candidates=(
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "NontradeReceivablesCurrent"),
            applicable_ciks=(_AAPL_CIK,),
        ),
    ),
)

INVENTORY_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.INVENTORY,
    candidates=(
        BalanceSheetConceptCandidate(ConceptKey("us-gaap", "InventoryNet")),
    ),
)

TRADE_ACCOUNTS_PAYABLE_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
    candidates=(
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "AccountsPayableCurrent")
        ),
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "AccountsPayableTradeCurrent"),
            applicable_ciks=(_META_CIK,),
        ),
    ),
)

CUSTOMER_CONTRACT_LIABILITIES_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
    candidates=(
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "ContractWithCustomerLiabilityCurrent")
        ),
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "DeferredRevenueCurrent"),
            applicable_ciks=(_COST_CIK,),
        ),
    ),
)

EMPLOYEE_RELATED_LIABILITIES_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.EMPLOYEE_RELATED_LIABILITIES,
    candidates=(
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "EmployeeRelatedLiabilitiesCurrent"),
            applicable_ciks=(_META_CIK, _GOOGL_CIK, _MSFT_CIK, _COST_CIK),
        ),
    ),
)

MEMBER_REWARDS_LIABILITY_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.MEMBER_REWARDS_LIABILITY,
    candidates=(
        BalanceSheetConceptCandidate(
            ConceptKey("us-gaap", "AccruedLiabilitiesCurrent"),
            applicable_ciks=(_COST_CIK,),
        ),
    ),
)

ANNUAL_BALANCE_SHEET_POLICIES: tuple[BalanceSheetMetricPolicy, ...] = (
    OPERATING_RECEIVABLES_POLICY,
    VENDOR_NONTRADE_RECEIVABLES_POLICY,
    INVENTORY_POLICY,
    TRADE_ACCOUNTS_PAYABLE_POLICY,
    CUSTOMER_CONTRACT_LIABILITIES_POLICY,
    EMPLOYEE_RELATED_LIABILITIES_POLICY,
    MEMBER_REWARDS_LIABILITY_POLICY,
)


def normalize_annual_balance_sheets(
    selected_facts: SelectedFactObservations,
    policies: tuple[
        BalanceSheetMetricPolicy, ...
    ] = ANNUAL_BALANCE_SHEET_POLICIES,
) -> NormalizedAnnualBalanceSheets:
    """Normalize configured instant metrics across selected annual filings."""
    _validate_policies(policies)
    annual = tuple(
        AnnualBalanceSheetFilingResult(
            filing=bucket.filing,
            metrics=tuple(
                _resolve_metric(
                    bucket,
                    policy,
                    selected_facts.company.cik,
                    selected_facts.source_url,
                )
                for policy in policies
            ),
        )
        for bucket in selected_facts.annual
    )
    return NormalizedAnnualBalanceSheets(
        company=selected_facts.company,
        company_facts_source_url=selected_facts.source_url,
        company_facts_retrieved_at=selected_facts.retrieved_at,
        annual=annual,
    )


def _resolve_metric(
    bucket: FilingFactObservations,
    policy: BalanceSheetMetricPolicy,
    company_cik: int,
    source_url: str,
) -> BalanceSheetMetricResult:
    filing = bucket.filing
    if filing.form != "10-K":
        raise BalanceSheetNormalizationError(
            f"Annual balance-sheet normalization requires exact 10-K, received "
            f"{filing.form!r} for accession {filing.accession_number!r}"
        )
    if filing.report_date is None:
        raise BalanceSheetNormalizationError(
            f"Annual filing {filing.accession_number!r} has no report date"
        )

    candidates = tuple(
        candidate
        for candidate in policy.candidates
        if candidate.applies_to(company_cik)
    )
    configured = _configured_observations(bucket, candidates)
    examined = tuple(candidate.concept for candidate in candidates)
    if not configured:
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
            examined_concepts=examined,
        )

    eligible = tuple(
        selected
        for selected in configured
        if selected.relationship is ObservationRelationship.CURRENT
        and selected.period_type is ObservationPeriodType.INSTANT
        and selected.observation.start is None
        and selected.observation.end == filing.report_date
        and selected.observation.unit == "USD"
        and _is_numeric(selected.observation.value)
    )
    if not eligible:
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_VALID_CURRENT_INSTANT_OBSERVATION,
            examined_concepts=examined,
        )

    by_concept: dict[ConceptKey, list[SelectedFactObservation]] = {}
    for selected in eligible:
        key = ConceptKey(selected.taxonomy, selected.concept)
        by_concept.setdefault(key, []).append(selected)

    if any(len(observations) > 1 for observations in by_concept.values()):
        return _ambiguous(policy.metric, eligible, source_url)

    present = tuple(
        by_concept[candidate.concept][0]
        for candidate in candidates
        if candidate.concept in by_concept
    )
    chosen = present[0]
    alternatives = present[1:]
    confirming = tuple(
        alternative
        for alternative in alternatives
        if policy.allow_equal_value_confirmation
        and alternative.observation.value == chosen.observation.value
    )
    unresolved = tuple(
        alternative
        for alternative in alternatives
        if alternative not in confirming
    )
    if unresolved:
        return _ambiguous(
            policy.metric,
            (chosen, *confirming, *unresolved),
            source_url,
        )

    observation = chosen.observation
    value = observation.value
    if not _is_numeric(value):
        raise BalanceSheetNormalizationError(
            "Chosen balance-sheet value is not numeric"
        )
    return NormalizedBalanceSheetValue(
        metric=policy.metric,
        value=value,
        unit=observation.unit,
        balance_date=observation.end,
        chosen_source=_fact_evidence(chosen, source_url),
        confirming_sources=tuple(
            _fact_evidence(item, source_url) for item in confirming
        ),
    )


def _configured_observations(
    bucket: FilingFactObservations,
    candidates: tuple[BalanceSheetConceptCandidate, ...],
) -> tuple[SelectedFactObservation, ...]:
    accession = bucket.filing.accession_number
    matches = []
    for candidate in candidates:
        for selected in bucket.for_concept(
            candidate.concept.taxonomy,
            candidate.concept.name,
        ):
            if selected.observation.accession_number != accession:
                raise BalanceSheetNormalizationError(
                    f"Fact accession {selected.observation.accession_number!r} does "
                    f"not match filing accession {accession!r}"
                )
            matches.append(selected)
    return tuple(matches)


def _ambiguous(
    metric: FinancialMetric,
    candidates: tuple[SelectedFactObservation, ...],
    source_url: str,
) -> AmbiguousHistoricalMetric:
    return AmbiguousHistoricalMetric(
        metric=metric,
        reason=AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
        candidates=tuple(
            _fact_evidence(candidate, source_url) for candidate in candidates
        ),
    )


def _fact_evidence(
    selected: SelectedFactObservation,
    source_url: str,
) -> FactEvidence:
    observation = selected.observation
    if not _is_numeric(observation.value):
        raise BalanceSheetNormalizationError(
            "Balance-sheet evidence value is not numeric"
        )
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


def _validate_policies(
    policies: tuple[BalanceSheetMetricPolicy, ...],
) -> None:
    if not isinstance(policies, tuple):
        raise BalanceSheetNormalizationError(
            "Balance-sheet policies must be a tuple"
        )
    if not all(isinstance(policy, BalanceSheetMetricPolicy) for policy in policies):
        raise BalanceSheetNormalizationError(
            "Balance-sheet policies contain an invalid policy"
        )
    metrics = tuple(policy.metric for policy in policies)
    if len(set(metrics)) != len(metrics):
        raise BalanceSheetNormalizationError(
            "Balance-sheet policies contain duplicate metrics"
        )
