"""Assemble normalized annual results into a stable company-level output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TypeAlias

from valuation_platform.sec.submissions import SECFiling

from .concepts import FinancialMetric
from .models import (
    AmbiguousHistoricalMetric,
    BalanceSheetFactEvidence,
    DerivedBalanceSheetValue,
    DerivedHistoricalValue,
    EvidenceSourceKind,
    FactEvidence,
    FilingXBRLEvidence,
    HistoricalMetricResult,
    HistoricalPolicyProvenance,
    MissingHistoricalMetric,
    NormalizedAnnualBalanceSheets,
    NormalizedBalanceSheetValue,
    NormalizedHistoricalFinancials,
    NormalizedHistoricalValue,
    ReviewedPolicyEvidence,
)
from .operating_nwc import (
    CalculatedOperatingNWC,
    CalculatedOperatingNWCChange,
    OperatingNWCReadinessResult,
)


SCHEMA_VERSION = "2"


class HistoricalOutputError(ValueError):
    """Raised when normalized inputs cannot form one consistent output."""


class HistoricalMeasure(str, Enum):
    """Stable top-level fields in standardized annual history."""

    REVENUE = FinancialMetric.REVENUE.value
    OPERATING_INCOME = FinancialMetric.OPERATING_INCOME.value
    PRETAX_INCOME = FinancialMetric.PRETAX_INCOME.value
    INCOME_TAX_EXPENSE = FinancialMetric.INCOME_TAX_EXPENSE.value
    REPORTED_EFFECTIVE_TAX_RATE = FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE.value
    D_AND_A = FinancialMetric.D_AND_A.value
    CAPEX = FinancialMetric.CAPEX.value
    DILUTED_WEIGHTED_AVERAGE_SHARES = (
        FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES.value
    )
    CASH_AND_CASH_EQUIVALENTS = FinancialMetric.CASH_AND_CASH_EQUIVALENTS.value
    SHORT_TERM_INVESTMENTS = FinancialMetric.SHORT_TERM_INVESTMENTS.value
    LONG_TERM_MARKETABLE_SECURITIES = (
        FinancialMetric.LONG_TERM_MARKETABLE_SECURITIES.value
    )
    COMMERCIAL_PAPER = FinancialMetric.COMMERCIAL_PAPER.value
    SHORT_TERM_BORROWINGS = FinancialMetric.SHORT_TERM_BORROWINGS.value
    CURRENT_PORTION_OF_LONG_TERM_DEBT = (
        FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT.value
    )
    LONG_TERM_DEBT_NONCURRENT = FinancialMetric.LONG_TERM_DEBT_NONCURRENT.value
    OPERATING_NWC = "operating_nwc"
    CHANGE_IN_OPERATING_NWC = "change_in_operating_nwc"


class HistoricalMeasureKind(str, Enum):
    """Economic time shape of one standardized measure."""

    DURATION = "duration"
    INSTANT = "instant"
    INTERPERIOD_CHANGE = "interperiod_change"
    DIAGNOSTIC = "diagnostic"


class HistoricalResolutionKind(str, Enum):
    """How one resolved standardized value was produced."""

    DIRECT = "direct"
    DERIVED = "derived"
    CALCULATED = "calculated"


class HistoricalAvailability(str, Enum):
    """Why one standardized measure has no single resolved value."""

    MISSING = "missing"
    AMBIGUOUS = "ambiguous"
    NOT_COMPARABLE = "not_comparable"
    METHODOLOGY_BLOCKED = "methodology_blocked"
    UNSUPPORTED = "unsupported"
    NOT_APPLICABLE = "not_applicable"
    OUT_OF_PERIMETER = "out_of_perimeter"


@dataclass(frozen=True)
class HistoricalFilingReference:
    """Compact identity for one selected annual filing."""

    accession_number: str
    form: str
    filing_date: date
    report_date: date
    primary_document: str

    def __post_init__(self) -> None:
        if not self.accession_number or not self.form or not self.primary_document:
            raise HistoricalOutputError("Filing reference fields must not be empty")


@dataclass(frozen=True)
class HistoricalPolicyReference:
    """Policy identity retained for derived or calculated output."""

    policy_id: str
    version: str | None = None
    economic_scope: str | None = None
    company_cik: int | None = None
    accession_number: str | None = None
    report_date: date | None = None
    annual_start: date | None = None
    annual_end: date | None = None
    taxonomy: str | None = None
    concept: str | None = None
    unit: str | None = None
    reviewed_evidence: tuple[ReviewedPolicyEvidence, ...] = ()
    filing_xbrl_evidence: tuple[FilingXBRLEvidence, ...] = ()

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise HistoricalOutputError("Policy reference ID must not be empty")
        detailed = (
            self.company_cik,
            self.accession_number,
            self.report_date,
            self.annual_start,
            self.annual_end,
            self.taxonomy,
            self.concept,
            self.unit,
        )
        if (self.economic_scope is None) != (not self.reviewed_evidence) or (
            self.economic_scope is not None
            and (any(item is None for item in detailed) or not self.filing_xbrl_evidence)
        ):
            raise HistoricalOutputError(
                "Reviewed policy scope and evidence must be retained together"
            )


@dataclass(frozen=True)
class HistoricalSourceReference:
    """Compact pointer from a standardized value to SEC evidence."""

    source_kind: EvidenceSourceKind
    source_url: str
    accession_number: str
    taxonomy_or_namespace: str | None
    concept: str | None
    context_id: str | None = None

    def __post_init__(self) -> None:
        if not self.source_url or not self.accession_number:
            raise HistoricalOutputError("Source reference identity must not be empty")


@dataclass(frozen=True)
class ResolvedHistoricalMeasure:
    """One exact standardized value."""

    measure: HistoricalMeasure
    kind: HistoricalMeasureKind
    value: Decimal
    unit: str
    start: date | None
    end: date
    opening_date: date | None
    resolution: HistoricalResolutionKind
    policy: HistoricalPolicyReference | None
    sources: tuple[HistoricalSourceReference, ...]
    supporting_policies: tuple[HistoricalPolicyReference, ...] = ()

    @property
    def status(self) -> str:
        return "resolved"

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal) or not self.value.is_finite():
            raise HistoricalOutputError("Resolved standardized value must be Decimal")
        if not self.unit:
            raise HistoricalOutputError("Resolved standardized unit must not be empty")


@dataclass(frozen=True)
class UnavailableHistoricalMeasure:
    """One unavailable standardized value with an explicit reason."""

    measure: HistoricalMeasure
    kind: HistoricalMeasureKind
    status: HistoricalAvailability
    reason: str
    unit: str | None
    start: date | None
    end: date
    opening_date: date | None
    policy: HistoricalPolicyReference | None = None
    sources: tuple[HistoricalSourceReference, ...] = ()

    def __post_init__(self) -> None:
        if self.status is HistoricalAvailability.AMBIGUOUS:
            raise HistoricalOutputError(
                "Ambiguous output must use AmbiguousStandardizedMeasure"
            )
        if not self.reason:
            raise HistoricalOutputError("Unavailable output reason must not be empty")


@dataclass(frozen=True)
class AmbiguousStandardizedMeasure:
    """One standardized field with competing normalized evidence."""

    measure: HistoricalMeasure
    kind: HistoricalMeasureKind
    reason: str
    unit: str | None
    start: date | None
    end: date
    opening_date: date | None
    policy: HistoricalPolicyReference | None
    candidates: tuple[HistoricalSourceReference, ...]

    @property
    def status(self) -> HistoricalAvailability:
        return HistoricalAvailability.AMBIGUOUS

    def __post_init__(self) -> None:
        if not self.reason or not self.candidates:
            raise HistoricalOutputError(
                "Ambiguous output requires a reason and candidate evidence"
            )


StandardizedHistoricalMeasure: TypeAlias = (
    ResolvedHistoricalMeasure
    | UnavailableHistoricalMeasure
    | AmbiguousStandardizedMeasure
)


@dataclass(frozen=True)
class AnnualHistoricalRecord:
    """One selected fiscal year with duration and closing-instant fields."""

    filing: HistoricalFilingReference
    fiscal_start: date | None
    fiscal_end: date
    balance_date: date
    measures: tuple[StandardizedHistoricalMeasure, ...]

    def __post_init__(self) -> None:
        if self.filing.report_date != self.fiscal_end or self.balance_date != self.fiscal_end:
            raise HistoricalOutputError(
                "Annual record dates must match the selected filing report date"
            )
        identities = tuple(item.measure for item in self.measures)
        if len(set(identities)) != len(identities):
            raise HistoricalOutputError("Annual record contains duplicate measures")

    def for_measure(self, measure: HistoricalMeasure) -> StandardizedHistoricalMeasure:
        """Return the one result for ``measure``."""
        matches = tuple(item for item in self.measures if item.measure is measure)
        if len(matches) != 1:
            raise HistoricalOutputError(
                f"Annual record must contain exactly one {measure.value!r} measure"
            )
        return matches[0]


@dataclass(frozen=True)
class StandardizedHistoricalCompany:
    """Canonical period-centric standardized annual history for one company."""

    schema_version: str
    ticker: str
    company_cik: int
    company_name: str
    annual: tuple[AnnualHistoricalRecord, ...]

    def __post_init__(self) -> None:
        if not self.schema_version or not self.ticker or not self.company_name:
            raise HistoricalOutputError("Standardized company identity is incomplete")
        if (
            not isinstance(self.company_cik, int)
            or isinstance(self.company_cik, bool)
            or self.company_cik < 0
        ):
            raise HistoricalOutputError("Standardized company CIK is invalid")
        dates = tuple(record.fiscal_end for record in self.annual)
        if len(set(dates)) != len(dates) or any(
            current <= previous for previous, current in zip(dates, dates[1:])
        ):
            raise HistoricalOutputError(
                "Standardized annual records must have unique increasing periods"
            )

    @property
    def selected_filings(self) -> tuple[HistoricalFilingReference, ...]:
        return tuple(record.filing for record in self.annual)

    def series(
        self, measure: HistoricalMeasure
    ) -> tuple[StandardizedHistoricalMeasure, ...]:
        """Return one measure across canonical annual order."""
        return tuple(record.for_measure(measure) for record in self.annual)


_DURATION_ORDER = (
    FinancialMetric.REVENUE,
    FinancialMetric.OPERATING_INCOME,
    FinancialMetric.PRETAX_INCOME,
    FinancialMetric.INCOME_TAX_EXPENSE,
    FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
    FinancialMetric.D_AND_A,
    FinancialMetric.CAPEX,
    FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
)

_INSTANT_ORDER = (
    FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
    FinancialMetric.SHORT_TERM_INVESTMENTS,
    FinancialMetric.LONG_TERM_MARKETABLE_SECURITIES,
    FinancialMetric.COMMERCIAL_PAPER,
    FinancialMetric.SHORT_TERM_BORROWINGS,
    FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
    FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
)

_EXPECTED_UNITS = {
    **{metric: "USD" for metric in _DURATION_ORDER},
    FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE: "pure",
    FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES: "shares",
    **{metric: "USD" for metric in _INSTANT_ORDER},
}


def assemble_standardized_annual_history(
    historical: NormalizedHistoricalFinancials,
    balance_sheets: NormalizedAnnualBalanceSheets,
    *,
    operating_nwc_results: tuple[
        CalculatedOperatingNWC | OperatingNWCReadinessResult, ...
    ] = (),
    operating_nwc_changes: tuple[CalculatedOperatingNWCChange, ...] = (),
) -> StandardizedHistoricalCompany:
    """Assemble compatible normalized inputs without recalculating finances."""
    if not isinstance(historical, NormalizedHistoricalFinancials):
        raise HistoricalOutputError("Historical input has an invalid type")
    if not isinstance(balance_sheets, NormalizedAnnualBalanceSheets):
        raise HistoricalOutputError("Balance-sheet input has an invalid type")
    if historical.company.cik != balance_sheets.company.cik:
        raise HistoricalOutputError("Historical inputs belong to different companies")
    if not isinstance(operating_nwc_results, tuple) or not isinstance(
        operating_nwc_changes, tuple
    ):
        raise HistoricalOutputError("O-NWC inputs must be tuples")

    historical_filings = tuple(item.filing for item in historical.annual)
    _validate_filing_order(historical_filings)
    balance_by_accession = _index_filing_results(balance_sheets.annual)
    if set(balance_by_accession) != {
        filing.accession_number for filing in historical_filings
    }:
        raise HistoricalOutputError(
            "Historical and balance-sheet inputs contain different selected filings"
        )
    nwc_by_accession = _index_nwc_results(
        operating_nwc_results, historical.company.cik
    )
    changes_by_close = _index_nwc_changes(
        operating_nwc_changes, historical.company.cik
    )

    annual: list[AnnualHistoricalRecord] = []
    previous_nwc: CalculatedOperatingNWC | OperatingNWCReadinessResult | None = None
    previous_filing: SECFiling | None = None
    for historical_result in historical.annual:
        filing = historical_result.filing
        if filing.report_date is None:
            raise HistoricalOutputError("Selected annual filing has no report date")
        balance_result = balance_by_accession[filing.accession_number]
        if balance_result.filing != filing:
            raise HistoricalOutputError(
                "Historical and balance-sheet selected filing identities differ"
            )

        duration_by_metric = _index_metric_results(historical_result.metrics)
        instant_by_metric = _index_metric_results(balance_result.metrics)
        duration_measures = tuple(
            _map_duration_result(
                _required_metric(duration_by_metric, metric), filing, metric
            )
            for metric in _DURATION_ORDER
        )
        fiscal_start = _fiscal_start(duration_measures, filing.report_date)
        instant_measures = tuple(
            _map_instant_result(
                _required_metric(instant_by_metric, metric), filing, metric
            )
            for metric in _INSTANT_ORDER
        )

        nwc_result = nwc_by_accession.get(filing.accession_number)
        nwc_measure = _map_nwc_result(nwc_result, filing, historical.company.cik)
        change = changes_by_close.get(filing.report_date)
        change_measure = _map_nwc_change(
            change,
            filing,
            historical.company.cik,
            previous_filing,
            previous_nwc,
            nwc_result,
        )
        annual.append(
            AnnualHistoricalRecord(
                filing=_filing_reference(filing),
                fiscal_start=fiscal_start,
                fiscal_end=filing.report_date,
                balance_date=filing.report_date,
                measures=(
                    *duration_measures,
                    *instant_measures,
                    nwc_measure,
                    change_measure,
                ),
            )
        )
        previous_nwc = nwc_result
        previous_filing = filing

    if set(changes_by_close) - {item.fiscal_end for item in annual}:
        raise HistoricalOutputError("O-NWC change does not belong to selected history")
    if set(nwc_by_accession) - {
        item.filing.accession_number for item in annual
    }:
        raise HistoricalOutputError("O-NWC result does not belong to selected history")

    company = historical.company
    return StandardizedHistoricalCompany(
        schema_version=SCHEMA_VERSION,
        ticker=company.ticker,
        company_cik=company.cik,
        company_name=company.company_name,
        annual=tuple(annual),
    )


def standardized_history_to_dict(
    history: StandardizedHistoricalCompany,
) -> dict[str, object]:
    """Serialize standardized history with exact strings and stable ordering."""
    if not isinstance(history, StandardizedHistoricalCompany):
        raise HistoricalOutputError("Serializer requires standardized history")
    return {
        "schema_version": history.schema_version,
        "ticker": history.ticker,
        "company_cik": history.company_cik,
        "company_name": history.company_name,
        "annual": [
            {
                "filing": {
                    "accession_number": record.filing.accession_number,
                    "form": record.filing.form,
                    "filing_date": record.filing.filing_date.isoformat(),
                    "report_date": record.filing.report_date.isoformat(),
                    "primary_document": record.filing.primary_document,
                },
                "fiscal_start": _date_string(record.fiscal_start),
                "fiscal_end": record.fiscal_end.isoformat(),
                "balance_date": record.balance_date.isoformat(),
                "measures": [_serialize_measure(item) for item in record.measures],
            }
            for record in history.annual
        ],
    }


def _map_duration_result(
    result: HistoricalMetricResult,
    filing: SECFiling,
    metric: FinancialMetric,
) -> StandardizedHistoricalMeasure:
    measure = HistoricalMeasure(metric.value)
    kind = (
        HistoricalMeasureKind.DIAGNOSTIC
        if metric is FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE
        else HistoricalMeasureKind.DURATION
    )
    expected_unit = _EXPECTED_UNITS[metric]
    if isinstance(result, (NormalizedHistoricalValue, DerivedHistoricalValue)):
        if result.metric is not metric:
            raise HistoricalOutputError("Historical metric identity is inconsistent")
        _validate_duration(result.period.start, result.period.end, filing)
        value = _decimal(result.value)
        _require_unit(result.unit, expected_unit, metric)
        if isinstance(result, NormalizedHistoricalValue):
            sources = _sources_from_historical_direct(result, filing)
            resolution = HistoricalResolutionKind.DIRECT
            policy = _policy_reference(result.policy_provenance, filing)
            supporting_policies = ()
        else:
            sources = _sources_from_historical_derived(result, filing)
            resolution = HistoricalResolutionKind.DERIVED
            policy = HistoricalPolicyReference(result.policy_id)
            supporting_policies = _supporting_policy_references(result, filing)
        return ResolvedHistoricalMeasure(
            measure,
            kind,
            value,
            result.unit,
            result.period.start,
            result.period.end,
            None,
            resolution,
            policy,
            sources,
            supporting_policies,
        )
    if isinstance(result, MissingHistoricalMetric):
        return UnavailableHistoricalMeasure(
            measure,
            kind,
            HistoricalAvailability.MISSING,
            result.reason.value,
            expected_unit,
            None,
            _report_date(filing),
            None,
        )
    if isinstance(result, AmbiguousHistoricalMetric):
        return AmbiguousStandardizedMeasure(
            measure,
            kind,
            result.reason.value,
            expected_unit,
            None,
            _report_date(filing),
            None,
            None,
            _canonical_ambiguous_sources(result.candidates, filing),
        )
    raise HistoricalOutputError("Historical metric result has an invalid type")


def _map_instant_result(
    result: object,
    filing: SECFiling,
    metric: FinancialMetric,
) -> StandardizedHistoricalMeasure:
    measure = HistoricalMeasure(metric.value)
    report_date = _report_date(filing)
    if isinstance(result, (NormalizedBalanceSheetValue, DerivedBalanceSheetValue)):
        if result.metric is not metric or result.balance_date != report_date:
            raise HistoricalOutputError(
                "Balance-sheet metric does not match selected filing"
            )
        _require_unit(result.unit, "USD", metric)
        if isinstance(result, NormalizedBalanceSheetValue):
            sources = _sources_from_balance_direct(result, filing)
            resolution = HistoricalResolutionKind.DIRECT
            policy = None
        else:
            sources = _sources_from_balance_derived(result, filing)
            resolution = HistoricalResolutionKind.DERIVED
            policy = HistoricalPolicyReference(result.policy_id)
        return ResolvedHistoricalMeasure(
            measure,
            HistoricalMeasureKind.INSTANT,
            _decimal(result.value),
            result.unit,
            None,
            result.balance_date,
            None,
            resolution,
            policy,
            sources,
        )
    if isinstance(result, MissingHistoricalMetric):
        return UnavailableHistoricalMeasure(
            measure,
            HistoricalMeasureKind.INSTANT,
            HistoricalAvailability.MISSING,
            result.reason.value,
            "USD",
            None,
            report_date,
            None,
        )
    if isinstance(result, AmbiguousHistoricalMetric):
        return AmbiguousStandardizedMeasure(
            measure,
            HistoricalMeasureKind.INSTANT,
            result.reason.value,
            "USD",
            None,
            report_date,
            None,
            None,
            _canonical_ambiguous_sources(result.candidates, filing),
        )
    raise HistoricalOutputError("Balance-sheet metric result has an invalid type")


def _map_nwc_result(
    result: CalculatedOperatingNWC | OperatingNWCReadinessResult | None,
    filing: SECFiling,
    company_cik: int,
) -> StandardizedHistoricalMeasure:
    report_date = _report_date(filing)
    measure = HistoricalMeasure.OPERATING_NWC
    kind = HistoricalMeasureKind.INSTANT
    if result is None:
        return UnavailableHistoricalMeasure(
            measure,
            kind,
            HistoricalAvailability.MISSING,
            "operating_nwc_result_not_supplied",
            "USD",
            None,
            report_date,
            None,
        )
    _validate_nwc_ownership(result, filing, company_cik)
    policy = HistoricalPolicyReference(result.policy_id, result.policy_version)
    if isinstance(result, CalculatedOperatingNWC):
        _require_unit(result.unit, "USD", measure)
        return ResolvedHistoricalMeasure(
            measure,
            kind,
            _decimal(result.amount),
            result.unit,
            None,
            result.balance_date,
            None,
            HistoricalResolutionKind.CALCULATED,
            policy,
            _sources_from_nwc(result, filing),
        )
    if result.methodology_blockers:
        status = HistoricalAvailability.METHODOLOGY_BLOCKED
        reason = "operating_nwc_methodology_blocked"
    elif result.ambiguous_mandatory_components:
        return AmbiguousStandardizedMeasure(
            measure,
            kind,
            "operating_nwc_required_component_ambiguous",
            "USD",
            None,
            report_date,
            None,
            policy,
            _canonical_ambiguous_sources(
                tuple(
                    candidate
                    for component in result.ambiguous_mandatory_components
                    for candidate in component.result.candidates
                ),
                filing,
            ),
        )
    elif result.missing_mandatory_components:
        status = HistoricalAvailability.MISSING
        reason = "operating_nwc_required_component_missing"
    else:
        status = HistoricalAvailability.MISSING
        reason = "calculated_operating_nwc_not_supplied"
    return UnavailableHistoricalMeasure(
        measure,
        kind,
        status,
        reason,
        "USD",
        None,
        report_date,
        None,
        policy,
    )


def _map_nwc_change(
    change: CalculatedOperatingNWCChange | None,
    filing: SECFiling,
    company_cik: int,
    previous_filing: SECFiling | None,
    previous: CalculatedOperatingNWC | OperatingNWCReadinessResult | None,
    current: CalculatedOperatingNWC | OperatingNWCReadinessResult | None,
) -> StandardizedHistoricalMeasure:
    report_date = _report_date(filing)
    measure = HistoricalMeasure.CHANGE_IN_OPERATING_NWC
    kind = HistoricalMeasureKind.INTERPERIOD_CHANGE
    if previous_filing is None:
        if change is not None:
            raise HistoricalOutputError(
                "O-NWC change requires an immediately preceding selected period"
            )
        return UnavailableHistoricalMeasure(
            measure,
            kind,
            HistoricalAvailability.NOT_COMPARABLE,
            "no_opening_operating_nwc",
            "USD",
            None,
            report_date,
            None,
        )
    if change is not None:
        _validate_nwc_change(change, previous_filing, filing, company_cik)
        if current is None:
            raise HistoricalOutputError(
                "O-NWC change requires its supplied closing annual level"
            )
        if current != change.closing_level:
            raise HistoricalOutputError(
                "O-NWC change closing level differs from the supplied annual result"
            )
        if previous is not None and previous != change.opening_level:
            raise HistoricalOutputError(
                "O-NWC change opening level differs from the preceding annual result"
            )
        return ResolvedHistoricalMeasure(
            measure,
            kind,
            _decimal(change.change),
            change.unit,
            None,
            change.closing_balance_date,
            change.opening_balance_date,
            HistoricalResolutionKind.CALCULATED,
            HistoricalPolicyReference(change.policy_id, change.policy_version),
            (
                *_sources_from_nwc(change.opening_level, change.opening_level.filing),
                *_sources_from_nwc(change.closing_level, change.closing_level.filing),
            ),
        )
    if isinstance(current, OperatingNWCReadinessResult):
        nwc = _map_nwc_result(current, filing, company_cik)
        status = (
            nwc.status
            if isinstance(nwc, UnavailableHistoricalMeasure)
            else HistoricalAvailability.AMBIGUOUS
        )
        if status is HistoricalAvailability.AMBIGUOUS:
            return AmbiguousStandardizedMeasure(
                measure,
                kind,
                "closing_operating_nwc_ambiguous",
                "USD",
                None,
                report_date,
                None,
                HistoricalPolicyReference(current.policy_id, current.policy_version),
                nwc.candidates,
            )
        return UnavailableHistoricalMeasure(
            measure,
            kind,
            status,
            "closing_operating_nwc_unavailable",
            "USD",
            None,
            report_date,
            None,
            HistoricalPolicyReference(current.policy_id, current.policy_version),
        )
    if isinstance(previous, OperatingNWCReadinessResult):
        return UnavailableHistoricalMeasure(
            measure,
            kind,
            HistoricalAvailability.MISSING,
            "opening_operating_nwc_unavailable",
            "USD",
            None,
            report_date,
            None,
        )
    if isinstance(previous, CalculatedOperatingNWC) and isinstance(
        current, CalculatedOperatingNWC
    ):
        if (
            previous.policy_id != current.policy_id
            or previous.policy_version != current.policy_version
            or tuple(
                (item.component, item.side, item.source_result.metric)
                for item in previous.contributions
            )
            != tuple(
                (item.component, item.side, item.source_result.metric)
                for item in current.contributions
            )
        ):
            reason = "operating_nwc_policy_or_perimeter_changed"
        else:
            reason = "operating_nwc_change_not_supplied"
        return UnavailableHistoricalMeasure(
            measure,
            kind,
            HistoricalAvailability.NOT_COMPARABLE,
            reason,
            "USD",
            None,
            report_date,
            previous.balance_date,
            HistoricalPolicyReference(current.policy_id, current.policy_version),
        )
    return UnavailableHistoricalMeasure(
        measure,
        kind,
        HistoricalAvailability.MISSING,
        "operating_nwc_result_not_supplied",
        "USD",
        None,
        report_date,
        None,
    )


def _validate_filing_order(filings: tuple[SECFiling, ...]) -> None:
    dates: list[date] = []
    accessions: set[str] = set()
    for filing in filings:
        report_date = _report_date(filing)
        if filing.form != "10-K":
            raise HistoricalOutputError("Standardized annual output requires 10-Ks")
        if filing.accession_number in accessions:
            raise HistoricalOutputError("Selected annual filings contain a duplicate")
        accessions.add(filing.accession_number)
        dates.append(report_date)
    if len(set(dates)) != len(dates):
        raise HistoricalOutputError("Selected annual filings duplicate a report date")
    if any(current <= previous for previous, current in zip(dates, dates[1:])):
        raise HistoricalOutputError(
            "Selected annual filings must be in increasing report-date order"
        )


def _index_filing_results(results: tuple[object, ...]) -> dict[str, object]:
    indexed: dict[str, object] = {}
    for result in results:
        filing = getattr(result, "filing", None)
        if not isinstance(filing, SECFiling):
            raise HistoricalOutputError("Annual result has an invalid filing")
        if filing.accession_number in indexed:
            raise HistoricalOutputError("Annual results contain a duplicate filing")
        indexed[filing.accession_number] = result
    return indexed


def _index_metric_results(results: tuple[object, ...]) -> dict[FinancialMetric, object]:
    indexed: dict[FinancialMetric, object] = {}
    for result in results:
        metric = getattr(result, "metric", None)
        if not isinstance(metric, FinancialMetric):
            raise HistoricalOutputError("Normalized result has an invalid metric")
        if metric in indexed:
            raise HistoricalOutputError(
                f"Normalized results duplicate metric {metric.value!r}"
            )
        indexed[metric] = result
    return indexed


def _required_metric(
    indexed: dict[FinancialMetric, object], metric: FinancialMetric
) -> object:
    if metric not in indexed:
        raise HistoricalOutputError(
            f"Normalized results omit required metric {metric.value!r}"
        )
    return indexed[metric]


def _index_nwc_results(
    results: tuple[CalculatedOperatingNWC | OperatingNWCReadinessResult, ...],
    company_cik: int,
) -> dict[str, CalculatedOperatingNWC | OperatingNWCReadinessResult]:
    indexed: dict[str, CalculatedOperatingNWC | OperatingNWCReadinessResult] = {}
    for result in results:
        if not isinstance(result, (CalculatedOperatingNWC, OperatingNWCReadinessResult)):
            raise HistoricalOutputError("O-NWC result has an invalid type")
        if result.company_cik != company_cik:
            raise HistoricalOutputError("O-NWC result belongs to a different company")
        accession = result.filing.accession_number
        if accession in indexed:
            raise HistoricalOutputError("O-NWC results duplicate a selected filing")
        indexed[accession] = result
    return indexed


def _index_nwc_changes(
    changes: tuple[CalculatedOperatingNWCChange, ...], company_cik: int
) -> dict[date, CalculatedOperatingNWCChange]:
    indexed: dict[date, CalculatedOperatingNWCChange] = {}
    for change in changes:
        if not isinstance(change, CalculatedOperatingNWCChange):
            raise HistoricalOutputError("O-NWC change has an invalid type")
        if change.company_cik != company_cik:
            raise HistoricalOutputError("O-NWC change belongs to a different company")
        if change.closing_balance_date in indexed:
            raise HistoricalOutputError("O-NWC changes duplicate a closing period")
        indexed[change.closing_balance_date] = change
    return indexed


def _fiscal_start(
    measures: tuple[StandardizedHistoricalMeasure, ...], report_date: date
) -> date | None:
    periods = {
        (item.start, item.end)
        for item in measures
        if isinstance(item, ResolvedHistoricalMeasure)
    }
    if not periods:
        return None
    if len(periods) != 1:
        raise HistoricalOutputError("Resolved duration measures disagree on period")
    start, end = next(iter(periods))
    if start is None or end != report_date:
        raise HistoricalOutputError("Resolved duration period is invalid")
    return start


def _validate_duration(start: date, end: date, filing: SECFiling) -> None:
    if not isinstance(start, date) or end != _report_date(filing):
        raise HistoricalOutputError(
            "Resolved duration does not match selected filing report date"
        )


def _validate_nwc_ownership(
    result: CalculatedOperatingNWC | OperatingNWCReadinessResult,
    filing: SECFiling,
    company_cik: int,
) -> None:
    if result.company_cik != company_cik or result.filing != filing:
        raise HistoricalOutputError("O-NWC result does not match selected filing")
    if isinstance(result, CalculatedOperatingNWC) and result.balance_date != _report_date(
        filing
    ):
        raise HistoricalOutputError("O-NWC balance date does not match filing")


def _validate_nwc_change(
    change: CalculatedOperatingNWCChange,
    previous_filing: SECFiling,
    filing: SECFiling,
    company_cik: int,
) -> None:
    if (
        change.company_cik != company_cik
        or change.opening_level.company_cik != company_cik
        or change.closing_level.company_cik != company_cik
        or change.opening_level.filing != previous_filing
        or change.closing_level.filing != filing
        or change.opening_balance_date != _report_date(previous_filing)
        or change.closing_balance_date != _report_date(filing)
        or change.opening_level.balance_date != change.opening_balance_date
        or change.closing_level.balance_date != change.closing_balance_date
        or change.opening_amount != change.opening_level.amount
        or change.closing_amount != change.closing_level.amount
        or change.policy_id != change.opening_level.policy_id
        or change.policy_id != change.closing_level.policy_id
        or change.policy_version != change.opening_level.policy_version
        or change.policy_version != change.closing_level.policy_version
        or change.opening_level.formula != change.closing_level.formula
        or _nwc_perimeter_signature(change.opening_level)
        != _nwc_perimeter_signature(change.closing_level)
        or change.opening_level.unit != "USD"
        or change.closing_level.unit != "USD"
    ):
        raise HistoricalOutputError("O-NWC change does not match selected periods")
    _require_unit(change.unit, "USD", HistoricalMeasure.CHANGE_IN_OPERATING_NWC)


def _nwc_perimeter_signature(
    result: CalculatedOperatingNWC,
) -> tuple[tuple[object, object, FinancialMetric], ...]:
    return tuple(
        (item.component, item.side, item.source_result.metric)
        for item in result.contributions
    )


def _sources_from_historical_direct(
    result: NormalizedHistoricalValue, filing: SECFiling
) -> tuple[HistoricalSourceReference, ...]:
    return tuple(
        _source_reference(item, filing)
        for item in (result.chosen_source, *result.confirming_sources)
    )


def _sources_from_historical_derived(
    result: DerivedHistoricalValue, filing: SECFiling
) -> tuple[HistoricalSourceReference, ...]:
    evidence: list[BalanceSheetFactEvidence] = list(result.operands)
    for operand in result.metric_operands:
        evidence.extend((operand.chosen_source, *operand.confirming_sources))
    return tuple(_source_reference(item, filing) for item in evidence)


def _policy_reference(
    provenance: HistoricalPolicyProvenance | None,
    filing: SECFiling,
) -> HistoricalPolicyReference | None:
    if provenance is None:
        return None
    for evidence in provenance.filing_xbrl_evidence:
        _source_reference(evidence, filing)
    return HistoricalPolicyReference(
        policy_id=provenance.policy_id,
        version=provenance.policy_version,
        economic_scope=provenance.economic_scope,
        company_cik=provenance.company_cik,
        accession_number=provenance.accession_number,
        report_date=provenance.report_date,
        annual_start=provenance.annual_start,
        annual_end=provenance.annual_end,
        taxonomy=provenance.taxonomy,
        concept=provenance.concept,
        unit=provenance.unit,
        reviewed_evidence=provenance.reviewed_evidence,
        filing_xbrl_evidence=provenance.filing_xbrl_evidence,
    )


def _supporting_policy_references(
    result: DerivedHistoricalValue,
    filing: SECFiling,
) -> tuple[HistoricalPolicyReference, ...]:
    references = tuple(
        reference
        for operand in result.metric_operands
        if (reference := _policy_reference(operand.policy_provenance, filing))
        is not None
    )
    identities = tuple(
        (
            item.policy_id,
            item.version,
            item.economic_scope,
            item.reviewed_evidence,
            item.filing_xbrl_evidence,
        )
        for item in references
    )
    if len(set(identities)) != len(identities):
        raise HistoricalOutputError("Derived metric repeats policy provenance")
    return references


def _sources_from_balance_direct(
    result: NormalizedBalanceSheetValue, filing: SECFiling
) -> tuple[HistoricalSourceReference, ...]:
    return tuple(
        _source_reference(item, filing)
        for item in (result.chosen_source, *result.confirming_sources)
    )


def _sources_from_balance_derived(
    result: DerivedBalanceSheetValue, filing: SECFiling
) -> tuple[HistoricalSourceReference, ...]:
    evidence: list[BalanceSheetFactEvidence] = []
    for operand in result.operands:
        evidence.append(operand.chosen_source)
        evidence.extend(getattr(operand, "confirming_sources", ()))
    return tuple(_source_reference(item, filing) for item in evidence)


def _sources_from_nwc(
    result: CalculatedOperatingNWC, filing: SECFiling
) -> tuple[HistoricalSourceReference, ...]:
    sources: list[HistoricalSourceReference] = []
    for contribution in result.contributions:
        source_result = contribution.source_result
        if isinstance(source_result, NormalizedBalanceSheetValue):
            sources.extend(_sources_from_balance_direct(source_result, filing))
        else:
            sources.extend(_sources_from_balance_derived(source_result, filing))
    return tuple(sources)


def _source_reference(
    evidence: BalanceSheetFactEvidence, filing: SECFiling
) -> HistoricalSourceReference:
    if (
        evidence.accession_number != filing.accession_number
        or evidence.end != _report_date(filing)
        or evidence.observation_form != filing.form
    ):
        raise HistoricalOutputError("Evidence does not belong to selected filing")
    if isinstance(evidence, FactEvidence):
        taxonomy = evidence.taxonomy
        context_id = None
    elif isinstance(evidence, FilingXBRLEvidence):
        if (
            evidence.filing_report_date != filing.report_date
            or evidence.primary_document != filing.primary_document
        ):
            raise HistoricalOutputError(
                "Filing-XBRL evidence does not match selected filing"
            )
        taxonomy = evidence.namespace
        context_id = evidence.context_id
    else:
        raise HistoricalOutputError("Evidence has an invalid type")
    return HistoricalSourceReference(
        source_kind=evidence.source_kind,
        source_url=evidence.source_url,
        accession_number=evidence.accession_number,
        taxonomy_or_namespace=taxonomy,
        concept=evidence.concept,
        context_id=context_id,
    )


def _canonical_ambiguous_sources(
    evidence: tuple[BalanceSheetFactEvidence, ...],
    filing: SECFiling,
) -> tuple[HistoricalSourceReference, ...]:
    sources = tuple(_source_reference(item, filing) for item in evidence)
    return tuple(sorted(sources, key=_source_reference_sort_key))


def _source_reference_sort_key(
    source: HistoricalSourceReference,
) -> tuple[str, str, str, str, str, str]:
    return (
        source.source_kind.value,
        source.accession_number,
        source.taxonomy_or_namespace or "",
        source.concept or "",
        source.context_id or "",
        source.source_url,
    )


def _filing_reference(filing: SECFiling) -> HistoricalFilingReference:
    return HistoricalFilingReference(
        filing.accession_number,
        filing.form,
        filing.filing_date,
        _report_date(filing),
        filing.primary_document,
    )


def _report_date(filing: SECFiling) -> date:
    if filing.report_date is None:
        raise HistoricalOutputError("Selected annual filing has no report date")
    return filing.report_date


def _decimal(value: object) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise HistoricalOutputError("Standardized values must not use bool or float")
    if isinstance(value, int):
        value = Decimal(value)
    if not isinstance(value, Decimal) or not value.is_finite():
        raise HistoricalOutputError("Standardized value must be a finite Decimal")
    return value


def _require_unit(actual: str, expected: str, metric: object) -> None:
    if actual != expected:
        name = metric.value if isinstance(metric, Enum) else str(metric)
        raise HistoricalOutputError(
            f"Standardized measure {name!r} requires exact unit {expected!r}"
        )


def _date_string(value: date | None) -> str | None:
    return None if value is None else value.isoformat()


def _serialize_policy(
    policy: HistoricalPolicyReference | None,
) -> dict[str, object] | None:
    if policy is None:
        return None
    return {
        "policy_id": policy.policy_id,
        "version": policy.version,
        "economic_scope": policy.economic_scope,
        "entry_key": (
            None
            if policy.economic_scope is None
            else {
                "company_cik": policy.company_cik,
                "accession_number": policy.accession_number,
                "report_date": _date_string(policy.report_date),
                "annual_start": _date_string(policy.annual_start),
                "annual_end": _date_string(policy.annual_end),
                "taxonomy": policy.taxonomy,
                "concept": policy.concept,
                "unit": policy.unit,
                "economic_scope": policy.economic_scope,
            }
        ),
        "reviewed_evidence": [
            {
                "evidence_id": item.evidence_id,
                "source_url": item.source_url,
                "filing_location": item.filing_location,
                "research_artifact": item.research_artifact,
                "reviewed_on": item.reviewed_on.isoformat(),
                "review_status": item.review_status,
                "rationale": item.rationale,
                "content_digest": item.content_digest,
            }
            for item in policy.reviewed_evidence
        ],
        "filing_xbrl_evidence": [
            _serialize_filing_xbrl_evidence(item)
            for item in policy.filing_xbrl_evidence
        ],
    }


def _serialize_filing_xbrl_evidence(
    evidence: FilingXBRLEvidence,
) -> dict[str, object]:
    return {
        "occurrence_ordinal": evidence.occurrence_ordinal,
        "source_kind": evidence.source_kind.value,
        "source_url": evidence.source_url,
        "namespace": evidence.namespace,
        "concept": evidence.concept,
        "context_id": evidence.context_id,
        "unit_ref": evidence.unit_ref,
        "unit": evidence.unit,
        "start": _date_string(evidence.start),
        "end": evidence.end.isoformat(),
        "dimensions": [
            {
                "dimension": {
                    "namespace": item.dimension.namespace,
                    "local_name": item.dimension.local_name,
                },
                "explicit_member": (
                    None
                    if item.explicit_member is None
                    else {
                        "namespace": item.explicit_member.namespace,
                        "local_name": item.explicit_member.local_name,
                    }
                ),
                "typed_member_xml": item.typed_member_xml,
            }
            for item in evidence.dimensions
        ],
        "raw_value": evidence.raw_value,
        "numeric_value": str(evidence.value),
        "decimals": evidence.decimals,
        "is_nil": evidence.is_nil,
        "accession_number": evidence.accession_number,
        "observation_form": evidence.observation_form,
        "observation_filed": evidence.observation_filed.isoformat(),
        "filing_report_date": _date_string(evidence.filing_report_date),
        "primary_document": evidence.primary_document,
        "retrieved_at": evidence.retrieved_at.isoformat(),
    }


def _serialize_source(source: HistoricalSourceReference) -> dict[str, object]:
    return {
        "source_kind": source.source_kind.value,
        "source_url": source.source_url,
        "accession_number": source.accession_number,
        "taxonomy_or_namespace": source.taxonomy_or_namespace,
        "concept": source.concept,
        "context_id": source.context_id,
    }


def _serialize_measure(item: StandardizedHistoricalMeasure) -> dict[str, object]:
    common: dict[str, object] = {
        "measure": item.measure.value,
        "kind": item.kind.value,
        "start": _date_string(item.start),
        "end": item.end.isoformat(),
        "opening_date": _date_string(item.opening_date),
        "unit": item.unit,
        "policy": _serialize_policy(item.policy),
    }
    if isinstance(item, ResolvedHistoricalMeasure):
        return {
            **common,
            "status": "resolved",
            "resolution": item.resolution.value,
            "value": str(item.value),
            "sources": [_serialize_source(source) for source in item.sources],
            "supporting_policies": [
                _serialize_policy(policy) for policy in item.supporting_policies
            ],
        }
    if isinstance(item, UnavailableHistoricalMeasure):
        return {
            **common,
            "status": item.status.value,
            "reason": item.reason,
            "value": None,
            "sources": [_serialize_source(source) for source in item.sources],
        }
    return {
        **common,
        "status": HistoricalAvailability.AMBIGUOUS.value,
        "reason": item.reason,
        "value": None,
        "candidates": [
            _serialize_source(source) for source in item.candidates
        ],
    }
