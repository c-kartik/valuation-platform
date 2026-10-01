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

    annual_period = _full_fiscal_year_period(bucket, filing.report_date)
    if annual_period is None:
        return _missing_combined(MissingReason.NO_VALID_DERIVATION_OPERANDS)
    eligible = tuple(
        sorted(
            (
                selected
                for selected in configured
                if _is_valid_combined_operand(
                    selected,
                    filing.report_date,
                    annual_period,
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


def _full_fiscal_year_period(
    bucket: FilingFactObservations,
    report_date: date,
) -> tuple[date, date] | None:
    periods = {
        (item.observation.start, item.observation.end)
        for item in bucket.observations
        if item.concept != _COMBINED_PP_AND_E_CONCEPT.name
        and item.relationship is ObservationRelationship.CURRENT
        and item.period_type is ObservationPeriodType.DURATION
        and item.observation.start is not None
        and item.observation.end == report_date
        and item.observation.accession_number == bucket.filing.accession_number
        and item.observation.form == "10-K"
        and item.observation.fiscal_period == "FY"
    }
    return next(iter(periods)) if len(periods) == 1 else None


def _is_valid_combined_operand(
    selected: SelectedFactObservation,
    report_date: date,
    annual_period: tuple[date, date],
) -> bool:
    observation = selected.observation
    return (
        selected.relationship is ObservationRelationship.CURRENT
        and selected.period_type is ObservationPeriodType.DURATION
        and observation.start is not None
        and (observation.start, observation.end) == annual_period
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
