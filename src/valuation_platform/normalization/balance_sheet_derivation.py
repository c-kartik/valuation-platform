"""Resolve evidence-backed derived annual balance-sheet values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationPeriodType,
    ObservationRelationship,
    SelectedFactObservation,
)
from valuation_platform.sec.submissions import SECFiling

from .concepts import ConceptKey, FinancialMetric
from .models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    BalanceSheetConceptDerivationOperand,
    BalanceSheetDerivationOperand,
    BalanceSheetDerivationStep,
    BalanceSheetMetricResult,
    DerivationOperation,
    DerivedBalanceSheetValue,
    EvidenceSourceKind,
    FactEvidence,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedBalanceSheetValue,
)


_COMBINED_PP_AND_E_CONCEPT = ConceptKey(
    "us-gaap",
    "CapitalExpendituresIncurredButNotYetPaid",
)

_GOOGL_CIK = 1652044
_GOOGL_DERIVATION_ACCESSIONS = (
    "0001652044-22-000019",
    "0001652044-23-000016",
    "0001652044-24-000022",
)
_DEBT_AND_FINANCE_LEASES_TOTAL = ConceptKey(
    "us-gaap",
    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
)
_DEBT_AND_FINANCE_LEASES_NONCURRENT = ConceptKey(
    "us-gaap",
    "LongTermDebtAndCapitalLeaseObligations",
)
_FINANCE_LEASE_TOTAL = ConceptKey("us-gaap", "FinanceLeaseLiability")
_FINANCE_LEASE_CURRENT = ConceptKey("us-gaap", "FinanceLeaseLiabilityCurrent")
_DEBT_DISCOUNT_AND_COSTS = ConceptKey(
    "us-gaap",
    "DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet",
)


class BalanceSheetDerivationError(ValueError):
    """Raised when balance-sheet derivation input is structurally invalid."""


@dataclass(frozen=True)
class BalanceSheetDerivationPolicy:
    """One exact issuer-scoped balance-sheet derivation."""

    policy_id: str
    metric: FinancialMetric
    company_cik: int
    operands: tuple[FinancialMetric, FinancialMetric, FinancialMetric]

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise BalanceSheetDerivationError("Derivation policy ID must not be empty")
        if self.metric is not FinancialMetric.TRADE_ACCOUNTS_PAYABLE:
            raise BalanceSheetDerivationError(
                "Adjusted trade-payables policy has an invalid result metric"
            )
        if self.company_cik != 1326801:
            raise BalanceSheetDerivationError(
                "Adjusted trade-payables policy must be scoped to META"
            )


META_ADJUSTED_TRADE_ACCOUNTS_PAYABLE_POLICY = BalanceSheetDerivationPolicy(
    policy_id="meta_adjusted_trade_accounts_payable_v1",
    metric=FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
    company_cik=1326801,
    operands=(
        FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        FinancialMetric.PP_AND_E_PAYABLE_COMBINED,
        FinancialMetric.ACCRUED_PP_AND_E_PURCHASES,
    ),
)


@dataclass(frozen=True)
class GoogleDebtDerivationPolicy:
    """One filing-scoped Google carrying-debt derivation."""

    policy_id: str
    metric: FinancialMetric
    company_cik: int
    supported_accessions: tuple[str, ...]
    operands: tuple[ConceptKey, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id:
            raise BalanceSheetDerivationError("Derivation policy ID must not be empty")
        if self.company_cik != _GOOGL_CIK:
            raise BalanceSheetDerivationError("Google debt policy has an invalid CIK")
        if self.metric not in (
            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
            FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
        ):
            raise BalanceSheetDerivationError("Google debt policy has an invalid metric")
        expected_operands = (
            (
                _DEBT_AND_FINANCE_LEASES_TOTAL,
                _DEBT_AND_FINANCE_LEASES_NONCURRENT,
                _FINANCE_LEASE_CURRENT,
                _DEBT_DISCOUNT_AND_COSTS,
            )
            if self.metric is FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT
            else (
                _DEBT_AND_FINANCE_LEASES_NONCURRENT,
                _FINANCE_LEASE_TOTAL,
                _FINANCE_LEASE_CURRENT,
            )
        )
        if (
            self.supported_accessions != _GOOGL_DERIVATION_ACCESSIONS
            or any(
                not isinstance(item, str) or not item
                for item in self.supported_accessions
            )
            or self.operands != expected_operands
        ):
            raise BalanceSheetDerivationError("Google debt policy is structurally invalid")


GOOGL_CURRENT_PORTION_OF_LONG_TERM_DEBT_DERIVATION_POLICY = GoogleDebtDerivationPolicy(
    policy_id="googl_current_portion_of_long_term_debt_v1",
    metric=FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
    company_cik=_GOOGL_CIK,
    supported_accessions=_GOOGL_DERIVATION_ACCESSIONS,
    operands=(
        _DEBT_AND_FINANCE_LEASES_TOTAL,
        _DEBT_AND_FINANCE_LEASES_NONCURRENT,
        _FINANCE_LEASE_CURRENT,
        _DEBT_DISCOUNT_AND_COSTS,
    ),
)

GOOGL_NONCURRENT_LONG_TERM_DEBT_DERIVATION_POLICY = GoogleDebtDerivationPolicy(
    policy_id="googl_noncurrent_long_term_debt_v1",
    metric=FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
    company_cik=_GOOGL_CIK,
    supported_accessions=_GOOGL_DERIVATION_ACCESSIONS,
    operands=(
        _DEBT_AND_FINANCE_LEASES_NONCURRENT,
        _FINANCE_LEASE_TOTAL,
        _FINANCE_LEASE_CURRENT,
    ),
)


GoogleDebtOperandResult = (
    BalanceSheetConceptDerivationOperand
    | MissingHistoricalMetric
    | AmbiguousHistoricalMetric
)


def derive_googl_debt(
    bucket: FilingFactObservations,
    direct_result: BalanceSheetMetricResult,
    source_url: str,
    company_cik: int,
    policy: GoogleDebtDerivationPolicy,
) -> BalanceSheetMetricResult:
    """Apply one validated Google carrying-debt identity with direct-first precedence."""
    filing = bucket.filing
    if company_cik != policy.company_cik:
        raise BalanceSheetDerivationError("Google debt derivation has an invalid CIK")
    if filing.form != "10-K" or filing.report_date is None:
        raise BalanceSheetDerivationError(
            "Google debt derivation requires an exact 10-K with a report date"
        )
    if direct_result.metric is not policy.metric:
        raise BalanceSheetDerivationError("Direct debt result does not match derivation policy")
    if isinstance(direct_result, AmbiguousHistoricalMetric):
        return direct_result
    if filing.accession_number not in policy.supported_accessions:
        return direct_result

    operand_results = tuple(
        _resolve_googl_concept_operand(bucket, concept, source_url, policy.metric)
        for concept in policy.operands
    )
    ambiguous = tuple(
        item for item in operand_results if isinstance(item, AmbiguousHistoricalMetric)
    )
    if ambiguous:
        if isinstance(direct_result, NormalizedBalanceSheetValue):
            return direct_result
        return AmbiguousHistoricalMetric(
            metric=policy.metric,
            reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
            candidates=tuple(
                candidate for item in ambiguous for candidate in item.candidates
            ),
        )
    if any(isinstance(item, MissingHistoricalMetric) for item in operand_results):
        return direct_result if isinstance(
            direct_result, NormalizedBalanceSheetValue
        ) else MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.MISSING_DERIVATION_OPERAND,
            examined_concepts=policy.operands,
        )
    operands = tuple(
        item
        for item in operand_results
        if isinstance(item, BalanceSheetConceptDerivationOperand)
    )
    if len(operands) != len(policy.operands):
        raise BalanceSheetDerivationError("Google debt operands were not resolved exactly")

    values = tuple(item.value for item in operands)
    if policy.metric is FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT:
        first = values[0] - values[1]
        second = first - values[2]
        value = second - values[3]
        steps = (
            BalanceSheetDerivationStep(
                name="combined_current_debt_and_finance_lease",
                operation=DerivationOperation.SUBTRACT,
                operand_names=(operands[0].name, operands[1].name),
                value=first,
            ),
            BalanceSheetDerivationStep(
                name="current_debt_before_discount_and_costs",
                operation=DerivationOperation.SUBTRACT,
                operand_names=(
                    "combined_current_debt_and_finance_lease",
                    operands[2].name,
                ),
                value=second,
            ),
            BalanceSheetDerivationStep(
                name=policy.metric.value,
                operation=DerivationOperation.SUBTRACT,
                operand_names=(
                    "current_debt_before_discount_and_costs",
                    operands[3].name,
                ),
                value=value,
            ),
        )
    else:
        noncurrent_finance_lease = values[1] - values[2]
        value = values[0] - noncurrent_finance_lease
        steps = (
            BalanceSheetDerivationStep(
                name="finance_lease_liability_noncurrent",
                operation=DerivationOperation.SUBTRACT,
                operand_names=(operands[1].name, operands[2].name),
                value=noncurrent_finance_lease,
            ),
            BalanceSheetDerivationStep(
                name=policy.metric.value,
                operation=DerivationOperation.SUBTRACT,
                operand_names=(operands[0].name, "finance_lease_liability_noncurrent"),
                value=value,
            ),
        )

    if isinstance(direct_result, NormalizedBalanceSheetValue):
        if direct_result.value == value:
            return direct_result
        return AmbiguousHistoricalMetric(
            metric=policy.metric,
            reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
            candidates=(
                direct_result.chosen_source,
                *direct_result.confirming_sources,
                *(item.chosen_source for item in operands),
            ),
        )
    return DerivedBalanceSheetValue(
        metric=policy.metric,
        value=value,
        unit="USD",
        balance_date=filing.report_date,
        policy_id=policy.policy_id,
        operation=DerivationOperation.SUBTRACT,
        operands=operands,
        steps=steps,
    )


def _resolve_googl_concept_operand(
    bucket: FilingFactObservations,
    concept: ConceptKey,
    source_url: str,
    target_metric: FinancialMetric,
) -> GoogleDebtOperandResult:
    filing = bucket.filing
    configured = bucket.for_concept(concept.taxonomy, concept.name)
    for selected in configured:
        if selected.observation.accession_number != filing.accession_number:
            raise BalanceSheetDerivationError(
                "Google debt operand accession does not match selected filing"
            )
    eligible = tuple(
        sorted(
            (
                selected
                for selected in configured
                if selected.relationship is ObservationRelationship.CURRENT
                and selected.period_type is ObservationPeriodType.INSTANT
                and selected.observation.start is None
                and selected.observation.end == filing.report_date
                and selected.observation.form == "10-K"
                and selected.observation.unit == "USD"
                and _is_integer_numeric(selected.observation.value)
            ),
            key=_selected_order_key,
        )
    )
    if not eligible:
        return MissingHistoricalMetric(
            metric=target_metric,
            reason=MissingReason.NO_VALID_DERIVATION_OPERANDS,
            examined_concepts=(concept,),
        )
    if len(eligible) > 1:
        return AmbiguousHistoricalMetric(
            metric=target_metric,
            reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
            candidates=tuple(_fact_evidence(item, source_url) for item in eligible),
        )
    evidence = _fact_evidence(eligible[0], source_url)
    if evidence.value < 0:
        return MissingHistoricalMetric(
            metric=target_metric,
            reason=MissingReason.NO_VALID_DERIVATION_OPERANDS,
            examined_concepts=(concept,),
        )
    return BalanceSheetConceptDerivationOperand(
        name=concept.name,
        value=Decimal(evidence.value),
        unit=evidence.unit,
        start=evidence.start,
        end=evidence.end,
        chosen_source=evidence,
    )


SpecialOperandResult = (
    BalanceSheetDerivationOperand
    | MissingHistoricalMetric
    | AmbiguousHistoricalMetric
)


def resolve_meta_combined_pp_and_e_payable(
    bucket: FilingFactObservations,
    source_url: str,
    company_cik: int,
) -> SpecialOperandResult:
    """Resolve META's duration-shaped combined unpaid-PP&E evidence."""
    filing = bucket.filing
    if company_cik != META_ADJUSTED_TRADE_ACCOUNTS_PAYABLE_POLICY.company_cik:
        raise BalanceSheetDerivationError(
            "Combined PP&E-payable evidence is approved only for META"
        )
    if filing.form != "10-K" or filing.report_date is None:
        raise BalanceSheetDerivationError(
            "META PP&E-payable evidence requires an exact 10-K with a report date"
        )
    configured = bucket.for_concept(
        _COMBINED_PP_AND_E_CONCEPT.taxonomy,
        _COMBINED_PP_AND_E_CONCEPT.name,
    )
    for selected in configured:
        if selected.observation.accession_number != filing.accession_number:
            raise BalanceSheetDerivationError(
                "Combined PP&E-payable accession does not match selected filing"
            )
    if not configured:
        return _missing_combined(MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION)

    eligible = tuple(
        sorted(
            (
                selected
                for selected in configured
                if _is_valid_combined_operand(
                    selected,
                    filing.report_date,
                )
            ),
            key=_selected_order_key,
        )
    )
    if not eligible:
        return _missing_combined(MissingReason.NO_VALID_DERIVATION_OPERANDS)
    if len(eligible) > 1:
        return AmbiguousHistoricalMetric(
            metric=FinancialMetric.PP_AND_E_PAYABLE_COMBINED,
            reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
            candidates=tuple(_fact_evidence(item, source_url) for item in eligible),
        )
    evidence = _fact_evidence(eligible[0], source_url)
    return BalanceSheetDerivationOperand(
        metric=FinancialMetric.PP_AND_E_PAYABLE_COMBINED,
        value=evidence.value,
        unit=evidence.unit,
        start=evidence.start,
        end=evidence.end,
        chosen_source=evidence,
        confirming_sources=(),
    )


def derive_meta_adjusted_trade_accounts_payable(
    filing: SECFiling,
    results: tuple[BalanceSheetMetricResult, ...],
    combined_pp_and_e: SpecialOperandResult,
    company_cik: int,
    policy: BalanceSheetDerivationPolicy = (
        META_ADJUSTED_TRADE_ACCOUNTS_PAYABLE_POLICY
    ),
) -> BalanceSheetMetricResult:
    """Derive META trade AP after removing its evidenced PP&E portion."""
    if company_cik != policy.company_cik:
        raise BalanceSheetDerivationError(
            "Adjusted trade-payables derivation is approved only for META"
        )
    if filing.form != "10-K" or filing.report_date is None:
        raise BalanceSheetDerivationError(
            "Balance-sheet derivation requires an exact 10-K with a report date"
        )
    by_metric = {result.metric: result for result in results}
    if len(by_metric) != len(results):
        raise BalanceSheetDerivationError(
            "Balance-sheet derivation input contains duplicate metrics"
        )
    reported = by_metric.get(FinancialMetric.TRADE_ACCOUNTS_PAYABLE)
    accrued = by_metric.get(FinancialMetric.ACCRUED_PP_AND_E_PURCHASES)
    raw_operands = (reported, combined_pp_and_e, accrued)
    ambiguous = tuple(
        item for item in raw_operands if isinstance(item, AmbiguousHistoricalMetric)
    )
    if ambiguous:
        return AmbiguousHistoricalMetric(
            metric=policy.metric,
            reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
            candidates=tuple(
                candidate for item in ambiguous for candidate in item.candidates
            ),
        )
    if any(
        item is None or isinstance(item, MissingHistoricalMetric)
        for item in raw_operands
    ):
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.MISSING_DERIVATION_OPERAND,
            examined_concepts=(),
        )
    if not isinstance(reported, NormalizedBalanceSheetValue) or not isinstance(
        accrued,
        NormalizedBalanceSheetValue,
    ) or not isinstance(combined_pp_and_e, BalanceSheetDerivationOperand):
        return MissingHistoricalMetric(
            metric=policy.metric,
            reason=MissingReason.NO_VALID_DERIVATION_OPERANDS,
            examined_concepts=(),
        )

    operands = (
        _direct_operand(reported),
        combined_pp_and_e,
        _direct_operand(accrued),
    )
    if (
        any(item.unit != "USD" for item in operands)
        or any(item.end != filing.report_date for item in operands)
        or any(
            item.chosen_source.accession_number != filing.accession_number
            for item in operands
        )
        or operands[0].start is not None
        or operands[2].start is not None
        or operands[1].start is None
    ):
        return AmbiguousHistoricalMetric(
            metric=policy.metric,
            reason=AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
            candidates=tuple(item.chosen_source for item in operands),
        )

    reported_value, combined_value, accrued_value = (
        Decimal(str(item.value)) for item in operands
    )
    pp_and_e_in_trade_ap = combined_value - accrued_value
    adjusted_trade_ap = reported_value - pp_and_e_in_trade_ap
    return DerivedBalanceSheetValue(
        metric=policy.metric,
        value=adjusted_trade_ap,
        unit="USD",
        balance_date=filing.report_date,
        policy_id=policy.policy_id,
        operation=DerivationOperation.SUBTRACT,
        operands=operands,
        steps=(
            BalanceSheetDerivationStep(
                name="pp_and_e_in_trade_accounts_payable",
                operation=DerivationOperation.SUBTRACT,
                operand_names=(
                    FinancialMetric.PP_AND_E_PAYABLE_COMBINED.value,
                    FinancialMetric.ACCRUED_PP_AND_E_PURCHASES.value,
                ),
                value=pp_and_e_in_trade_ap,
            ),
            BalanceSheetDerivationStep(
                name="adjusted_trade_accounts_payable",
                operation=DerivationOperation.SUBTRACT,
                operand_names=(
                    FinancialMetric.TRADE_ACCOUNTS_PAYABLE.value,
                    "pp_and_e_in_trade_accounts_payable",
                ),
                value=adjusted_trade_ap,
            ),
        ),
    )


def _is_valid_combined_operand(
    selected: SelectedFactObservation,
    report_date: date,
) -> bool:
    observation = selected.observation
    return (
        selected.relationship is ObservationRelationship.CURRENT
        and selected.period_type is ObservationPeriodType.DURATION
        and observation.start is not None
        and observation.end == report_date
        and observation.form == "10-K"
        and observation.fiscal_period == "FY"
        and observation.unit == "USD"
        and _is_numeric(observation.value)
    )


def _missing_combined(reason: MissingReason) -> MissingHistoricalMetric:
    return MissingHistoricalMetric(
        metric=FinancialMetric.PP_AND_E_PAYABLE_COMBINED,
        reason=reason,
        examined_concepts=(_COMBINED_PP_AND_E_CONCEPT,),
    )


def _direct_operand(value: NormalizedBalanceSheetValue) -> BalanceSheetDerivationOperand:
    source = value.chosen_source
    return BalanceSheetDerivationOperand(
        metric=value.metric,
        value=value.value,
        unit=value.unit,
        start=source.start,
        end=value.balance_date,
        chosen_source=source,
        confirming_sources=value.confirming_sources,
    )


def _fact_evidence(
    selected: SelectedFactObservation,
    source_url: str,
) -> FactEvidence:
    observation = selected.observation
    if not _is_numeric(observation.value):
        raise BalanceSheetDerivationError(
            "Combined PP&E-payable evidence value is not numeric"
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


def _selected_order_key(item: SelectedFactObservation) -> tuple[object, ...]:
    observation = item.observation
    return (
        item.taxonomy,
        item.concept,
        observation.unit,
        observation.start,
        observation.end,
        str(observation.value),
        observation.accession_number,
    )


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_integer_numeric(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
