"""Normalize selected annual SEC instant facts into primitive balances."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from valuation_platform.sec.company_facts import SECFactValue
from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationPeriodType,
    ObservationRelationship,
    SelectedFactObservation,
    SelectedFactObservations,
)
from valuation_platform.sec.filing_xbrl import FilingXBRLFact, SECFilingXBRL
from valuation_platform.sec.submissions import SECFiling

from .concepts import ConceptKey, FinancialMetric
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    AnnualBalanceSheetFilingResult,
    BalanceSheetMetricResult,
    EvidenceSourceKind,
    FactEvidence,
    FilingXBRLEvidence,
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


class FilingXBRLNamespaceFamily(str, Enum):
    """Strict issuer namespace families approved for balance-sheet facts."""

    ALPHABET_GOOGLE = "alphabet_google"


@dataclass(frozen=True)
class BalanceSheetConceptCandidate:
    """One exact concept candidate, optionally restricted to validated CIKs."""

    concept: ConceptKey
    applicable_ciks: tuple[int, ...] | None = None
    source_kind: EvidenceSourceKind = EvidenceSourceKind.COMPANY_FACTS
    filing_xbrl_namespace_family: FilingXBRLNamespaceFamily | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.concept, ConceptKey):
            raise BalanceSheetNormalizationError(
                "Balance-sheet candidate concept must be a ConceptKey"
            )
        if not isinstance(self.source_kind, EvidenceSourceKind):
            raise BalanceSheetNormalizationError(
                "Balance-sheet candidate source kind is invalid"
            )
        if self.source_kind is EvidenceSourceKind.COMPANY_FACTS:
            if self.filing_xbrl_namespace_family is not None:
                raise BalanceSheetNormalizationError(
                    "Company Facts candidate cannot configure a filing-XBRL namespace"
                )
        elif not isinstance(
            self.filing_xbrl_namespace_family,
            FilingXBRLNamespaceFamily,
        ):
            raise BalanceSheetNormalizationError(
                "Filing-XBRL candidate must configure an approved namespace family"
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

ACCRUED_REVENUE_SHARE_LIABILITY_POLICY = BalanceSheetMetricPolicy(
    metric=FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
    candidates=(
        BalanceSheetConceptCandidate(
            ConceptKey("alphabet-google", "AccruedRevenueShare"),
            applicable_ciks=(_GOOGL_CIK,),
            source_kind=EvidenceSourceKind.FILING_XBRL,
            filing_xbrl_namespace_family=(
                FilingXBRLNamespaceFamily.ALPHABET_GOOGLE
            ),
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
    ACCRUED_REVENUE_SHARE_LIABILITY_POLICY,
    MEMBER_REWARDS_LIABILITY_POLICY,
)


def normalize_annual_balance_sheets(
    selected_facts: SelectedFactObservations,
    policies: tuple[
        BalanceSheetMetricPolicy, ...
    ] = ANNUAL_BALANCE_SHEET_POLICIES,
    *,
    filing_xbrl: tuple[SECFilingXBRL, ...] = (),
) -> NormalizedAnnualBalanceSheets:
    """Normalize configured instant metrics across selected annual filings."""
    _validate_policies(policies)
    filing_xbrl_by_accession = _validate_filing_xbrl(
        filing_xbrl,
        selected_facts.company.cik,
    )
    annual = tuple(
        AnnualBalanceSheetFilingResult(
            filing=bucket.filing,
            metrics=tuple(
                _resolve_metric(
                    bucket,
                    policy,
                    selected_facts.company.cik,
                    selected_facts.source_url,
                    filing_xbrl_by_accession.get(bucket.filing.accession_number),
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
    filing_xbrl: SECFilingXBRL | None,
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
    if filing_xbrl is not None and filing_xbrl.filing != filing:
        raise BalanceSheetNormalizationError(
            "Filing-XBRL filing metadata does not match selected filing"
        )

    candidates = tuple(
        candidate
        for candidate in policy.candidates
        if candidate.applies_to(company_cik)
    )
    company_facts_candidates = tuple(
        candidate
        for candidate in candidates
        if candidate.source_kind is EvidenceSourceKind.COMPANY_FACTS
    )
    filing_xbrl_candidates = tuple(
        candidate
        for candidate in candidates
        if candidate.source_kind is EvidenceSourceKind.FILING_XBRL
    )
    configured = _configured_observations(bucket, company_facts_candidates)
    configured_xbrl = _configured_filing_xbrl_facts(
        filing_xbrl,
        filing_xbrl_candidates,
        filing.report_date,
    )
    examined = tuple(candidate.concept for candidate in candidates)
    if not configured and not configured_xbrl:
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
    eligible_xbrl = tuple(
        sorted(
            (
                fact
                for fact in configured_xbrl
                if fact.accession_number == filing.accession_number
                and fact.start is None
                and fact.end == filing.report_date
                and not fact.dimensions
                and _filing_xbrl_unit_is_usd(fact)
                and not fact.is_nil
                and _is_filing_xbrl_numeric(fact.numeric_value)
            ),
            key=_filing_xbrl_fact_order_key,
        )
    )
    if not eligible and not eligible_xbrl:
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
    if len(eligible_xbrl) > 1:
        assert filing_xbrl is not None
        return _ambiguous_filing_xbrl(
            policy.metric,
            eligible_xbrl,
            filing,
            filing_xbrl.retrieved_at,
        )

    if eligible_xbrl:
        if eligible:
            raise BalanceSheetNormalizationError(
                "One balance-sheet policy cannot resolve Company Facts and "
                "filing-XBRL evidence together"
            )
        fact = eligible_xbrl[0]
        value = fact.numeric_value
        if not _is_filing_xbrl_numeric(value):
            raise BalanceSheetNormalizationError(
                "Chosen filing-XBRL balance-sheet value is not numeric"
            )
        return NormalizedBalanceSheetValue(
            metric=policy.metric,
            value=value,
            unit="USD",
            balance_date=fact.end,
            chosen_source=_filing_xbrl_evidence(
                fact,
                filing,
                filing_xbrl.retrieved_at,
            ),
            confirming_sources=(),
        )

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


def _configured_filing_xbrl_facts(
    filing_xbrl: SECFilingXBRL | None,
    candidates: tuple[BalanceSheetConceptCandidate, ...],
    report_date: date,
) -> tuple[FilingXBRLFact, ...]:
    if filing_xbrl is None or not candidates:
        return ()
    matches = []
    for candidate in candidates:
        for fact in filing_xbrl.facts:
            if (
                fact.concept == candidate.concept.name
                and _namespace_matches(candidate, fact.namespace, report_date)
            ):
                matches.append(fact)
    return tuple(matches)


def _namespace_matches(
    candidate: BalanceSheetConceptCandidate,
    namespace: str,
    report_date: date,
) -> bool:
    family = candidate.filing_xbrl_namespace_family
    if family is FilingXBRLNamespaceFamily.ALPHABET_GOOGLE:
        return namespace == f"http://www.google.com/{report_date:%Y%m%d}"
    return False


def _filing_xbrl_fact_order_key(fact: FilingXBRLFact) -> tuple[object, ...]:
    """Return a stable order for preserved eligible filing facts."""
    unit = fact.unit
    unit_key = () if unit is None else (
        tuple(
            (measure.namespace, measure.local_name)
            for measure in unit.numerator_measures
        ),
        tuple(
            (measure.namespace, measure.local_name)
            for measure in unit.denominator_measures
        ),
    )
    dimensions_key = tuple(
        (
            dimension.dimension.namespace,
            dimension.dimension.local_name,
            None
            if dimension.explicit_member is None
            else dimension.explicit_member.namespace,
            None
            if dimension.explicit_member is None
            else dimension.explicit_member.local_name,
            dimension.typed_member_xml,
        )
        for dimension in fact.dimensions
    )
    return (
        fact.namespace,
        fact.concept,
        "" if fact.start is None else fact.start.isoformat(),
        fact.end.isoformat(),
        unit_key,
        dimensions_key,
        "" if fact.numeric_value is None else str(fact.numeric_value),
        "" if fact.raw_value is None else fact.raw_value,
        fact.context_id,
    )


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


def _ambiguous_filing_xbrl(
    metric: FinancialMetric,
    candidates: tuple[FilingXBRLFact, ...],
    filing: SECFiling,
    retrieved_at: datetime,
) -> AmbiguousHistoricalMetric:
    return AmbiguousHistoricalMetric(
        metric=metric,
        reason=AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
        candidates=tuple(
            _filing_xbrl_evidence(candidate, filing, retrieved_at)
            for candidate in candidates
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


def _filing_xbrl_evidence(
    fact: FilingXBRLFact,
    filing: SECFiling,
    retrieved_at: datetime,
) -> FilingXBRLEvidence:
    value = fact.numeric_value
    if not _is_filing_xbrl_numeric(value):
        raise BalanceSheetNormalizationError(
            "Filing-XBRL balance-sheet evidence value is not numeric"
        )
    if not isinstance(retrieved_at, datetime) or retrieved_at.tzinfo is None:
        raise BalanceSheetNormalizationError(
            "Filing-XBRL retrieval timestamp must be timezone-aware"
        )
    return FilingXBRLEvidence(
        source_kind=EvidenceSourceKind.FILING_XBRL,
        source_url=fact.source_url,
        namespace=fact.namespace,
        concept=fact.concept,
        raw_value=fact.raw_value,
        value=value,
        unit="USD",
        start=fact.start,
        end=fact.end,
        accession_number=fact.accession_number,
        observation_form=filing.form,
        observation_filed=filing.filing_date,
        filing_report_date=filing.report_date,
        primary_document=filing.primary_document,
        retrieved_at=retrieved_at,
        context_id=fact.context_id,
        dimensions=fact.dimensions,
        decimals=fact.decimals,
        is_nil=fact.is_nil,
    )


def _filing_xbrl_unit_is_usd(fact: FilingXBRLFact) -> bool:
    unit = fact.unit
    return (
        unit is not None
        and not unit.is_divided
        and len(unit.numerator_measures) == 1
        and unit.numerator_measures[0].namespace
        == "http://www.xbrl.org/2003/iso4217"
        and unit.numerator_measures[0].local_name == "USD"
    )


def _is_filing_xbrl_numeric(value: object) -> bool:
    return isinstance(value, Decimal) and not isinstance(value, bool)


def _validate_filing_xbrl(
    filings: tuple[SECFilingXBRL, ...],
    company_cik: int,
) -> dict[str, SECFilingXBRL]:
    if not isinstance(filings, tuple):
        raise BalanceSheetNormalizationError("Filing-XBRL input must be a tuple")
    by_accession: dict[str, SECFilingXBRL] = {}
    for filing_xbrl in filings:
        if not isinstance(filing_xbrl, SECFilingXBRL):
            raise BalanceSheetNormalizationError(
                "Filing-XBRL input contains an invalid artifact"
            )
        if filing_xbrl.company.cik != company_cik:
            raise BalanceSheetNormalizationError(
                "Filing-XBRL company does not match selected company"
            )
        accession = filing_xbrl.filing.accession_number
        if accession in by_accession:
            raise BalanceSheetNormalizationError(
                f"Filing-XBRL input contains duplicate accession {accession!r}"
            )
        by_accession[accession] = filing_xbrl
    return by_accession


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
