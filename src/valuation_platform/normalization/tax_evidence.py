"""Pure normalization and reconciliation of explicitly signed tax evidence.

This module records filing evidence. It does not infer displayed signs or
produce an operating-tax rate, operating tax expense, or NOPAT.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext
from enum import Enum

from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity


class TaxEvidenceNormalizationError(ValueError):
    """Raised when supplied filing or tax-row evidence is inconsistent."""


class TaxBridgeStyle(str, Enum):
    RATE = "rate"
    DOLLAR = "dollar"


class TaxDisplayedUnit(str, Enum):
    RATE = "rate"  # percentage points, e.g. Decimal("-1.6") means -1.6 pp
    CURRENCY = "currency"


class TaxSignEvidence(str, Enum):
    FILING_TABLE_PRESENTATION = "filing_table_presentation"
    CALCULATION_RELATIONSHIP = "calculation_relationship"


class TaxEvidenceStatus(str, Enum):
    RESOLVED = "resolved"
    MISSING_EVIDENCE = "missing_evidence"
    AMBIGUOUS_SIGN = "ambiguous_sign"
    COMPETING_EVIDENCE = "competing_evidence"
    SOURCE_CONFLICT = "source_conflict"
    METHODOLOGY_UNRESOLVED = "methodology_unresolved"


class TaxIncomeBase(str, Enum):
    INSIDE_OPERATING_INCOME = "inside_operating_income"
    OUTSIDE_OPERATING_INCOME = "outside_operating_income"
    MIXED = "mixed"
    INDETERMINABLE = "indeterminable"


class TaxPairing(str, Enum):
    NONE = "none"
    GROSS_TAX_WITH_CREDIT = "gross_tax_with_credit"
    NET_REPORTED_EVENT = "net_reported_event"
    OFFSETTING_REGIME_COMPONENTS = "offsetting_regime_components"
    OTHER = "other"


class TaxProposedTreatment(str, Enum):
    INCLUDE_OPERATING = "include_operating"
    EXCLUDE_OUTSIDE_OPERATING_BASE = "exclude_outside_operating_base"
    EXCLUDE_DISCRETE_TAX_ONLY = "exclude_discrete_tax_only"
    INCLUDE_PAIRED_NET_EFFECT = "include_paired_net_effect"
    REQUIRES_PAIRED_INCOME_ADJUSTMENT = "requires_paired_income_adjustment"
    METHODOLOGY_UNRESOLVED = "methodology_unresolved"
    INFORMATIONAL = "informational"


class TaxRowPrecision(str, Enum):
    AS_REPORTED = "as_reported"
    DOLLARIZED_FROM_DISPLAYED_RATE = "dollarized_from_displayed_rate"


class TaxReconciliationStatus(str, Enum):
    EXACT = "exact"
    MATCH_WITHIN_DISCLOSED_ROUNDING = "match_within_disclosed_rounding"
    UNRECONCILED = "unreconciled"
    INCOMPLETE_EVIDENCE = "incomplete_evidence"


@dataclass(frozen=True)
class SelectedTaxFiling:
    """Compact selected filing identity and original filing provenance."""

    company: SECCompanyIdentity
    filing: SECFiling
    source_url: str

    def __post_init__(self) -> None:
        if not isinstance(self.company, SECCompanyIdentity):
            raise TaxEvidenceNormalizationError("tax filing requires a company identity")
        if not isinstance(self.filing, SECFiling):
            raise TaxEvidenceNormalizationError("tax filing requires selected filing metadata")
        if self.filing.form != "10-K" or self.filing.report_date is None:
            raise TaxEvidenceNormalizationError(
                "tax reconciliation requires a selected 10-K with a report date"
            )
        if not isinstance(self.source_url, str) or not self.source_url:
            raise TaxEvidenceNormalizationError("filing source URL must be non-empty")

    @property
    def issuer_cik(self) -> int:
        return self.company.cik

    @property
    def accession_number(self) -> str:
        return self.filing.accession_number

    @property
    def report_date(self) -> date:
        assert self.filing.report_date is not None
        return self.filing.report_date


@dataclass(frozen=True)
class TaxRowSource:
    """Source locator for one displayed reconciliation row and optional XBRL fact."""

    accession_number: str
    source_url: str
    table_identity: str
    taxonomy_namespace: str | None = None
    concept: str | None = None
    raw_xbrl_value: Decimal | str | None = None
    context_id: str | None = None
    report_date: date | None = None

    def __post_init__(self) -> None:
        if not self.accession_number or not self.source_url or not self.table_identity:
            raise TaxEvidenceNormalizationError(
                "tax row source requires accession, source URL, and table identity"
            )
        if isinstance(self.raw_xbrl_value, Decimal):
            _require_finite(self.raw_xbrl_value, "raw XBRL value")
        elif self.raw_xbrl_value is not None and not isinstance(self.raw_xbrl_value, str):
            raise TaxEvidenceNormalizationError(
                "raw XBRL value must be Decimal, string, or None"
            )
        if (self.taxonomy_namespace is None) != (self.concept is None):
            raise TaxEvidenceNormalizationError(
                "taxonomy namespace and concept must be supplied together"
            )


@dataclass(frozen=True)
class TaxReconciliationRowInput:
    """Caller-supplied evidence; a resolved value requires explicit sign authority."""

    displayed_label: str
    source: TaxRowSource
    displayed_unit: TaxDisplayedUnit
    displayed_value: Decimal | None
    sign_evidence: TaxSignEvidence | None
    evidence_status: TaxEvidenceStatus = TaxEvidenceStatus.RESOLVED
    income_base: TaxIncomeBase = TaxIncomeBase.INDETERMINABLE
    pairing: TaxPairing = TaxPairing.NONE
    proposed_treatment: TaxProposedTreatment = (
        TaxProposedTreatment.METHODOLOGY_UNRESOLVED
    )
    rationale: str = ""
    linked_row_labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaxReconciliationRow:
    """One normalized row, retaining displayed sign separately from raw XBRL."""

    issuer_cik: int
    accession_number: str
    report_date: date
    displayed_label: str
    source: TaxRowSource
    displayed_unit: TaxDisplayedUnit
    displayed_value: Decimal | None
    sign_evidence: TaxSignEvidence | None
    evidence_status: TaxEvidenceStatus
    pretax_denominator: Decimal | None
    signed_tax_amount: Decimal | None
    precision: TaxRowPrecision
    income_base: TaxIncomeBase
    pairing: TaxPairing
    proposed_treatment: TaxProposedTreatment
    rationale: str
    linked_row_labels: tuple[str, ...]

    def __post_init__(self) -> None:
        if isinstance(self.issuer_cik, bool) or not isinstance(self.issuer_cik, int) or self.issuer_cik < 0:
            raise TaxEvidenceNormalizationError("row issuer CIK must be a nonnegative integer")
        if not isinstance(self.source, TaxRowSource):
            raise TaxEvidenceNormalizationError("normalized row requires typed source provenance")
        if self.accession_number != self.source.accession_number:
            raise TaxEvidenceNormalizationError("row accession does not match its source")
        if self.source.report_date is not None and self.report_date != self.source.report_date:
            raise TaxEvidenceNormalizationError("row report date does not match its source")
        if not isinstance(self.report_date, date):
            raise TaxEvidenceNormalizationError("row report date must be a date")
        if not isinstance(self.displayed_label, str) or not self.displayed_label.strip():
            raise TaxEvidenceNormalizationError("displayed row label must be non-empty")
        if not isinstance(self.displayed_unit, TaxDisplayedUnit):
            raise TaxEvidenceNormalizationError("row displayed unit must be explicit")
        if not isinstance(self.evidence_status, TaxEvidenceStatus):
            raise TaxEvidenceNormalizationError("row evidence status must be explicit")
        if self.sign_evidence is not None and not isinstance(self.sign_evidence, TaxSignEvidence):
            raise TaxEvidenceNormalizationError("row sign evidence has an invalid type")
        if not isinstance(self.precision, TaxRowPrecision):
            raise TaxEvidenceNormalizationError("row precision state has an invalid type")
        if not isinstance(self.income_base, TaxIncomeBase):
            raise TaxEvidenceNormalizationError("row income-base classification is invalid")
        if not isinstance(self.pairing, TaxPairing):
            raise TaxEvidenceNormalizationError("row pairing classification is invalid")
        if not isinstance(self.proposed_treatment, TaxProposedTreatment):
            raise TaxEvidenceNormalizationError("row treatment classification is invalid")
        if not isinstance(self.rationale, str):
            raise TaxEvidenceNormalizationError("row rationale must be a string")
        if (
            self.sign_evidence is TaxSignEvidence.CALCULATION_RELATIONSHIP
            and not self.rationale.strip()
        ):
            raise TaxEvidenceNormalizationError(
                "calculation-relationship sign evidence requires an auditable rationale"
            )
        if not isinstance(self.linked_row_labels, tuple) or any(
            not isinstance(label, str) or not label for label in self.linked_row_labels
        ):
            raise TaxEvidenceNormalizationError("linked row labels must be non-empty strings")
        if self.displayed_value is not None:
            _require_finite(self.displayed_value, "displayed row value")
        if self.pretax_denominator is not None:
            _require_finite(self.pretax_denominator, "row pretax denominator")
        if self.signed_tax_amount is not None:
            _require_finite(self.signed_tax_amount, "signed tax amount")
        if (
            self.displayed_unit is TaxDisplayedUnit.CURRENCY
            and self.pretax_denominator is not None
        ):
            raise TaxEvidenceNormalizationError(
                "dollar rows cannot retain a pretax rate denominator"
            )

        is_value_resolved = self.evidence_status in (
            TaxEvidenceStatus.RESOLVED,
            TaxEvidenceStatus.METHODOLOGY_UNRESOLVED,
        )
        if not is_value_resolved:
            if self.displayed_value is not None or self.sign_evidence is not None:
                raise TaxEvidenceNormalizationError(
                    "unresolved evidence cannot supply a normalized signed value"
                )
            if self.signed_tax_amount is not None:
                raise TaxEvidenceNormalizationError(
                    "unresolved evidence cannot supply a derived tax amount"
                )
            expected_precision = TaxRowPrecision.AS_REPORTED
        else:
            if self.displayed_value is None or self.sign_evidence is None:
                raise TaxEvidenceNormalizationError(
                    "resolved signed evidence requires a value and sign authority"
                )
            if self.displayed_unit is TaxDisplayedUnit.RATE:
                if self.pretax_denominator is None or self.pretax_denominator == 0:
                    raise TaxEvidenceNormalizationError(
                        "rate row requires a nonzero pretax denominator"
                    )
                expected_amount = _rate_to_tax_amount(
                    self.pretax_denominator, self.displayed_value
                )
                expected_precision = TaxRowPrecision.DOLLARIZED_FROM_DISPLAYED_RATE
            else:
                if self.pretax_denominator is not None:
                    raise TaxEvidenceNormalizationError(
                        "dollar row cannot retain a rate denominator"
                    )
                expected_amount = self.displayed_value
                expected_precision = TaxRowPrecision.AS_REPORTED
            if self.signed_tax_amount != expected_amount:
                raise TaxEvidenceNormalizationError(
                    "signed tax amount does not match displayed row evidence"
                )
        if self.precision is not expected_precision:
            raise TaxEvidenceNormalizationError(
                "row precision state does not match its displayed unit"
            )


@dataclass(frozen=True)
class TaxReconciliationBridge:
    """Ordered filing-level tax bridge and its arithmetic validation result."""

    selected_filing: SelectedTaxFiling
    style: TaxBridgeStyle
    rows: tuple[TaxReconciliationRow, ...]
    starting_value: Decimal
    reported_value: Decimal
    pretax_income: Decimal | None
    displayed_precision: Decimal
    currency_code: str | None
    row_inventory_complete: bool
    reconciliation_status: TaxReconciliationStatus
    reconstructed_value: Decimal | None
    difference: Decimal | None

    @property
    def statutory_rate(self) -> Decimal | None:
        """Reported statutory rate for a rate bridge, otherwise None."""
        return self.starting_value if self.style is TaxBridgeStyle.RATE else None

    @property
    def expected_statutory_tax_amount(self) -> Decimal | None:
        """Expected tax starting amount for a dollar bridge, otherwise None."""
        return self.starting_value if self.style is TaxBridgeStyle.DOLLAR else None

    @property
    def reported_effective_tax_rate(self) -> Decimal | None:
        """Reported ETR for a rate bridge, otherwise None."""
        return self.reported_value if self.style is TaxBridgeStyle.RATE else None

    @property
    def reported_tax_provision(self) -> Decimal | None:
        """Reported provision for a dollar bridge, otherwise None."""
        return self.reported_value if self.style is TaxBridgeStyle.DOLLAR else None

    def __post_init__(self) -> None:
        if not isinstance(self.selected_filing, SelectedTaxFiling):
            raise TaxEvidenceNormalizationError("bridge requires a selected tax filing")
        if not isinstance(self.style, TaxBridgeStyle):
            raise TaxEvidenceNormalizationError("bridge style must be explicit")
        _require_finite(self.starting_value, "bridge starting value")
        _require_finite(self.reported_value, "bridge reported value")
        _require_finite(self.displayed_precision, "displayed precision")
        if self.displayed_precision <= 0:
            raise TaxEvidenceNormalizationError("displayed precision must be positive")
        if self.style is TaxBridgeStyle.RATE:
            if self.pretax_income is None or self.pretax_income == 0:
                raise TaxEvidenceNormalizationError(
                    "rate bridge requires a nonzero pretax denominator"
                )
            _require_finite(self.pretax_income, "pretax denominator")
            if self.currency_code is not None:
                raise TaxEvidenceNormalizationError("rate bridge cannot declare a currency")
        else:
            if not isinstance(self.currency_code, str) or not self.currency_code:
                raise TaxEvidenceNormalizationError("dollar bridge requires a currency code")
            if self.pretax_income is not None:
                raise TaxEvidenceNormalizationError(
                    "dollar bridge cannot retain a pretax rate denominator"
                )
        if not isinstance(self.rows, tuple):
            raise TaxEvidenceNormalizationError("bridge rows must be an ordered tuple")
        for row in self.rows:
            if not isinstance(row, TaxReconciliationRow):
                raise TaxEvidenceNormalizationError(
                    "bridge rows must contain normalized tax rows"
                )
            if (
                row.issuer_cik != self.selected_filing.issuer_cik
                or row.accession_number != self.selected_filing.accession_number
                or row.report_date != self.selected_filing.report_date
                or row.source.accession_number != self.selected_filing.accession_number
                or (
                    row.source.report_date is not None
                    and row.source.report_date != self.selected_filing.report_date
                )
            ):
                raise TaxEvidenceNormalizationError(
                    "tax reconciliation row does not belong to selected filing"
                )
            expected_unit = (
                TaxDisplayedUnit.RATE
                if self.style is TaxBridgeStyle.RATE
                else TaxDisplayedUnit.CURRENCY
            )
            if row.displayed_unit is not expected_unit:
                raise TaxEvidenceNormalizationError(
                    "tax row unit does not match bridge style"
                )
            if self.style is TaxBridgeStyle.RATE:
                if row.pretax_denominator != self.pretax_income:
                    raise TaxEvidenceNormalizationError(
                        "rate row denominator does not match bridge denominator"
                    )
            elif row.pretax_denominator is not None:
                raise TaxEvidenceNormalizationError(
                    "dollar bridge rows cannot have pretax denominators"
                )
        if not isinstance(self.row_inventory_complete, bool):
            raise TaxEvidenceNormalizationError(
                "row inventory completeness must be explicitly declared"
            )
        has_incomplete_rows = not self.row_inventory_complete or any(
            row.evidence_status not in (
                TaxEvidenceStatus.RESOLVED,
                TaxEvidenceStatus.METHODOLOGY_UNRESOLVED,
            )
            for row in self.rows
        )
        if has_incomplete_rows:
            if (
                self.reconciliation_status is not TaxReconciliationStatus.INCOMPLETE_EVIDENCE
                or self.reconstructed_value is not None
                or self.difference is not None
            ):
                raise TaxEvidenceNormalizationError(
                    "incomplete row evidence cannot have a validated bridge total"
                )
        else:
            if self.reconstructed_value is None or self.difference is None:
                raise TaxEvidenceNormalizationError(
                    "complete row evidence requires bridge totals"
                )
            _require_finite(self.reconstructed_value, "reconstructed bridge value")
            _require_finite(self.difference, "bridge difference")
            expected = _exact_add(
                self.starting_value,
                _exact_sum(row.displayed_value for row in self.rows),
            )
            if expected != self.reconstructed_value:
                raise TaxEvidenceNormalizationError(
                    "reconstructed bridge value does not match its rows"
                )
            if self.difference != _exact_subtract(
                self.reconstructed_value, self.reported_value
            ):
                raise TaxEvidenceNormalizationError(
                    "bridge difference does not match reported value"
                )
            if self.difference == 0:
                expected_status = TaxReconciliationStatus.EXACT
            elif abs(self.difference) <= _cumulative_rounding_tolerance(
                self.displayed_precision, len(self.rows)
            ):
                expected_status = TaxReconciliationStatus.MATCH_WITHIN_DISCLOSED_ROUNDING
            else:
                expected_status = TaxReconciliationStatus.UNRECONCILED
            if self.reconciliation_status is not expected_status:
                raise TaxEvidenceNormalizationError(
                    "reconciliation status does not match bridge arithmetic"
                )


def normalize_tax_reconciliation_bridge(
    selected_filing: SelectedTaxFiling,
    *,
    style: TaxBridgeStyle,
    starting_value: Decimal,
    reported_value: Decimal,
    rows: tuple[TaxReconciliationRowInput, ...],
    displayed_precision: Decimal,
    row_inventory_complete: bool,
    pretax_income: Decimal | None = None,
    currency_code: str | None = None,
) -> TaxReconciliationBridge:
    """Normalize explicitly signed row evidence and validate the displayed bridge.

    Rate values are percentage points. Their signed tax amounts are retained as
    ``pretax_income * percentage_points / 100`` without quantization. Dollar
    values remain in the filing's supplied currency units and are not converted
    to rates.
    """
    if not isinstance(selected_filing, SelectedTaxFiling):
        raise TaxEvidenceNormalizationError("selected_filing has an invalid type")
    if not isinstance(style, TaxBridgeStyle):
        raise TaxEvidenceNormalizationError("bridge style must be explicit")
    if not isinstance(row_inventory_complete, bool):
        raise TaxEvidenceNormalizationError(
            "row_inventory_complete must be explicitly declared as Boolean"
        )
    _require_finite(starting_value, "bridge starting value")
    _require_finite(reported_value, "bridge reported value")
    _require_finite(displayed_precision, "displayed precision")
    if displayed_precision <= 0:
        raise TaxEvidenceNormalizationError("displayed precision must be positive")

    if style is TaxBridgeStyle.RATE:
        if pretax_income is None or not isinstance(pretax_income, Decimal):
            raise TaxEvidenceNormalizationError("rate bridge requires Decimal pretax income")
        _require_finite(pretax_income, "pretax denominator")
        if pretax_income == 0:
            raise TaxEvidenceNormalizationError("rate bridge pretax denominator cannot be zero")
        if currency_code is not None:
            raise TaxEvidenceNormalizationError("rate bridge cannot declare a currency")
    else:
        if not isinstance(currency_code, str) or not currency_code:
            raise TaxEvidenceNormalizationError("dollar bridge requires a currency code")
        if pretax_income is not None:
            raise TaxEvidenceNormalizationError(
                "dollar bridge does not convert or retain a pretax denominator"
            )

    normalized_rows: list[TaxReconciliationRow] = []
    for row_input in rows:
        _validate_row_input(row_input, selected_filing, style)
        amount: Decimal | None = None
        precision = TaxRowPrecision.AS_REPORTED
        if row_input.evidence_status in (
            TaxEvidenceStatus.RESOLVED,
            TaxEvidenceStatus.METHODOLOGY_UNRESOLVED,
        ):
            assert row_input.displayed_value is not None
            if style is TaxBridgeStyle.RATE:
                assert pretax_income is not None
                amount = _rate_to_tax_amount(pretax_income, row_input.displayed_value)
                precision = TaxRowPrecision.DOLLARIZED_FROM_DISPLAYED_RATE
            else:
                amount = row_input.displayed_value
        normalized_rows.append(
            TaxReconciliationRow(
                issuer_cik=selected_filing.issuer_cik,
                accession_number=selected_filing.accession_number,
                report_date=selected_filing.report_date,
                displayed_label=row_input.displayed_label,
                source=row_input.source,
                displayed_unit=row_input.displayed_unit,
                displayed_value=row_input.displayed_value,
                sign_evidence=row_input.sign_evidence,
                evidence_status=row_input.evidence_status,
                pretax_denominator=pretax_income if style is TaxBridgeStyle.RATE else None,
                signed_tax_amount=amount,
                precision=precision,
                income_base=row_input.income_base,
                pairing=row_input.pairing,
                proposed_treatment=row_input.proposed_treatment,
                rationale=row_input.rationale,
                linked_row_labels=row_input.linked_row_labels,
            )
        )

    if not row_inventory_complete or any(row.evidence_status not in (
        TaxEvidenceStatus.RESOLVED,
        TaxEvidenceStatus.METHODOLOGY_UNRESOLVED,
    ) for row in normalized_rows):
        status = TaxReconciliationStatus.INCOMPLETE_EVIDENCE
        reconstructed = difference = None
    else:
        adjustment_total = _exact_sum(row.displayed_value for row in normalized_rows)
        reconstructed = _exact_add(starting_value, adjustment_total)
        difference = _exact_subtract(reconstructed, reported_value)
        if difference == 0:
            status = TaxReconciliationStatus.EXACT
        elif abs(difference) <= _cumulative_rounding_tolerance(
            displayed_precision, len(normalized_rows)
        ):
            status = TaxReconciliationStatus.MATCH_WITHIN_DISCLOSED_ROUNDING
        else:
            status = TaxReconciliationStatus.UNRECONCILED

    return TaxReconciliationBridge(
        selected_filing=selected_filing,
        style=style,
        rows=tuple(normalized_rows),
        starting_value=starting_value,
        reported_value=reported_value,
        pretax_income=pretax_income,
        displayed_precision=displayed_precision,
        currency_code=currency_code,
        row_inventory_complete=row_inventory_complete,
        reconciliation_status=status,
        reconstructed_value=reconstructed,
        difference=difference,
    )


def _validate_row_input(
    row: TaxReconciliationRowInput,
    selected_filing: SelectedTaxFiling,
    style: TaxBridgeStyle,
) -> None:
    if not isinstance(row, TaxReconciliationRowInput):
        raise TaxEvidenceNormalizationError("rows must contain TaxReconciliationRowInput values")
    if not isinstance(row.displayed_label, str) or not row.displayed_label.strip():
        raise TaxEvidenceNormalizationError("displayed row label must be non-empty")
    if not isinstance(row.source, TaxRowSource):
        raise TaxEvidenceNormalizationError("tax row requires typed source provenance")
    if not isinstance(row.displayed_unit, TaxDisplayedUnit):
        raise TaxEvidenceNormalizationError("tax row displayed unit must be explicit")
    if not isinstance(row.evidence_status, TaxEvidenceStatus):
        raise TaxEvidenceNormalizationError("tax row evidence status must be explicit")
    if not isinstance(row.rationale, str):
        raise TaxEvidenceNormalizationError("tax row rationale must be a string")
    if row.sign_evidence is not None and not isinstance(row.sign_evidence, TaxSignEvidence):
        raise TaxEvidenceNormalizationError("tax row sign evidence has an invalid type")
    if (
        row.sign_evidence is TaxSignEvidence.CALCULATION_RELATIONSHIP
        and (not isinstance(row.rationale, str) or not row.rationale.strip())
    ):
        raise TaxEvidenceNormalizationError(
            "calculation-relationship sign evidence requires an auditable rationale"
        )
    if not isinstance(row.income_base, TaxIncomeBase):
        raise TaxEvidenceNormalizationError("tax row income-base classification is invalid")
    if not isinstance(row.pairing, TaxPairing):
        raise TaxEvidenceNormalizationError("tax row pairing classification is invalid")
    if not isinstance(row.proposed_treatment, TaxProposedTreatment):
        raise TaxEvidenceNormalizationError("tax row treatment classification is invalid")
    if not isinstance(row.linked_row_labels, tuple) or any(
        not isinstance(label, str) or not label for label in row.linked_row_labels
    ):
        raise TaxEvidenceNormalizationError("linked row labels must be non-empty strings")
    if row.source.accession_number != selected_filing.accession_number:
        raise TaxEvidenceNormalizationError("tax row accession does not match selected filing")
    if row.source.report_date is not None and row.source.report_date != selected_filing.report_date:
        raise TaxEvidenceNormalizationError("tax row report date does not match selected filing")
    expected_unit = TaxDisplayedUnit.RATE if style is TaxBridgeStyle.RATE else TaxDisplayedUnit.CURRENCY
    if row.displayed_unit is not expected_unit:
        raise TaxEvidenceNormalizationError("tax row unit does not match bridge style")
    if row.displayed_value is not None:
        _require_finite(row.displayed_value, "displayed row value")
    if row.evidence_status in (
        TaxEvidenceStatus.RESOLVED,
        TaxEvidenceStatus.METHODOLOGY_UNRESOLVED,
    ):
        if row.displayed_value is None:
            raise TaxEvidenceNormalizationError(
                "signed evidence state requires a displayed value"
            )
        if not isinstance(row.sign_evidence, TaxSignEvidence):
            raise TaxEvidenceNormalizationError(
                "displayed economic sign requires explicit sign evidence"
            )
    elif row.displayed_value is not None or row.sign_evidence is not None:
        raise TaxEvidenceNormalizationError(
            "unresolved sign/source evidence cannot supply a normalized signed value"
        )


def _require_finite(value: Decimal, label: str) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise TaxEvidenceNormalizationError(f"{label} must be a finite Decimal")


def _rate_to_tax_amount(pretax_income: Decimal, rate_points: Decimal) -> Decimal:
    """Multiply and divide by 100 at enough precision to keep Decimal exact."""
    precision = (
        len(pretax_income.as_tuple().digits)
        + len(rate_points.as_tuple().digits)
        + 3
    )
    with localcontext() as context:
        context.prec = max(context.prec, precision)
        return pretax_income * rate_points / Decimal(100)


def _exact_sum(values: Iterable[Decimal]) -> Decimal:
    """Sum finite Decimals without allowing the ambient context to round."""
    items = tuple(values)
    if not items:
        return Decimal(0)
    min_exponent = min(value.as_tuple().exponent for value in items)
    max_adjusted = max(
        (value.adjusted() for value in items if value), default=min_exponent
    )
    precision = max_adjusted - min_exponent + 2 + len(str(len(items)))
    with localcontext() as context:
        context.prec = max(context.prec, precision)
        return sum(items, Decimal(0))


def _exact_add(left: Decimal, right: Decimal) -> Decimal:
    return _exact_sum((left, right))


def _exact_subtract(left: Decimal, right: Decimal) -> Decimal:
    return _exact_add(left, right.copy_negate())


def _cumulative_rounding_tolerance(
    displayed_precision: Decimal,
    adjustment_count: int,
) -> Decimal:
    """Bound error when start, rows, and reported total share display precision.

    The model does not distinguish which displayed terms were rounded, so it
    conservatively counts the starting value, each adjustment, and the
    reported total as independently rounded terms.
    """
    terms = adjustment_count + 2
    digits = len(displayed_precision.as_tuple().digits) + len(str(terms)) + 2
    with localcontext() as context:
        context.prec = max(context.prec, digits)
        half_unit = displayed_precision / Decimal(2)
    return _exact_sum((half_unit,) * terms)
