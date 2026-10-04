"""Validate whether signed tax evidence is ready for operating-tax calculation.

This module is pure and network-free.  It validates evidence and policy
coverage only; it does not calculate operating tax, NOPAT, or FCFF.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal, localcontext
from enum import Enum

from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity

from .concepts import FinancialMetric
from .models import (
    AmbiguousHistoricalMetric,
    EvidenceSourceKind,
    FactEvidence,
    HistoricalFilingResult,
    MissingHistoricalMetric,
    NormalizedHistoricalFinancials,
    NormalizedHistoricalValue,
    ResolvedHistoricalValue,
)


from .tax_evidence import (
    TaxBridgeStyle,
    TaxEvidenceStatus,
    TaxProposedTreatment,
    TaxReconciliationBridge,
    TaxReconciliationRow,
    TaxReconciliationStatus,
    TaxRowSource,
)


_EXPECTED_FINANCIAL_CONCEPTS = {
    FinancialMetric.OPERATING_INCOME: ("us-gaap", "OperatingIncomeLoss"),
    FinancialMetric.PRETAX_INCOME: (
        "us-gaap",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
        "ExtraordinaryItemsNoncontrollingInterest",
    ),
}


class OperatingTaxReadinessError(ValueError):
    """Raised when operating-tax inputs violate an ownership or policy invariant."""


class OperatingTaxReadinessStatus(str, Enum):
    """Typed outcome of operating-tax policy/readiness evaluation."""

    READY = "ready"
    MISSING_INPUT = "missing_input"
    AMBIGUOUS_INPUT = "ambiguous_input"
    UNSUPPORTED_POLICY = "unsupported_policy"
    POLICY_MISMATCH = "policy_mismatch"
    UNRECONCILED_BRIDGE = "unreconciled_bridge"
    METHODOLOGY_BLOCKED = "methodology_blocked"
    LOSS_POLICY_BLOCKED = "loss_policy_blocked"


class OperatingTaxLossPolicy(str, Enum):
    """Supported loss/zero-income readiness boundary."""

    BLOCK_NONPOSITIVE_OPERATING_OR_NEGATIVE_PRETAX = (
        "block_nonpositive_operating_or_negative_pretax"
    )


@dataclass(frozen=True)
class TaxMonetaryBasis:
    """Explicit currency and multiplier from displayed units to currency units."""

    currency: str
    scale: Decimal
    bridge_currency_label: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.currency, str) or not self.currency:
            raise OperatingTaxReadinessError("tax monetary currency must be non-empty")
        if (
            not isinstance(self.scale, Decimal)
            or not self.scale.is_finite()
            or self.scale <= 0
        ):
            raise OperatingTaxReadinessError(
                "tax monetary scale must be a positive finite Decimal"
            )
        if self.bridge_currency_label is not None and (
            not isinstance(self.bridge_currency_label, str) or not self.bridge_currency_label
        ):
            raise OperatingTaxReadinessError("bridge currency label must be non-empty")


@dataclass(frozen=True)
class StatutoryRateAnchor:
    """An explicitly evidenced statutory rate for one selected filing."""

    issuer_cik: int
    accession_number: str
    report_date: date
    rate: Decimal
    source: TaxRowSource

    def __post_init__(self) -> None:
        if (
            isinstance(self.issuer_cik, bool)
            or not isinstance(self.issuer_cik, int)
            or self.issuer_cik < 0
        ):
            raise OperatingTaxReadinessError(
                "statutory-rate CIK must be a nonnegative integer"
            )
        if not self.accession_number or not isinstance(self.report_date, date):
            raise OperatingTaxReadinessError("statutory-rate filing identity is invalid")
        if not isinstance(self.rate, Decimal) or not self.rate.is_finite():
            raise OperatingTaxReadinessError("statutory rate must be a finite Decimal")
        if not isinstance(self.source, TaxRowSource):
            raise OperatingTaxReadinessError("statutory rate requires source evidence")
        if self.source.accession_number != self.accession_number:
            raise OperatingTaxReadinessError("statutory-rate source accession does not match")
        if self.source.report_date != self.report_date:
            raise OperatingTaxReadinessError("statutory-rate source report date does not match")


@dataclass(frozen=True)
class OperatingTaxRowReference:
    """Stable bridge-row reference: position plus source and identity guards."""

    row_index: int
    displayed_label: str
    source_url: str
    table_identity: str
    taxonomy_namespace: str | None = None
    concept: str | None = None
    context_id: str | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.row_index, bool)
            or not isinstance(self.row_index, int)
            or self.row_index < 0
        ):
            raise OperatingTaxReadinessError(
                "tax row index must be a nonnegative integer"
            )
        if any(
            not isinstance(value, str) or not value
            for value in (self.displayed_label, self.source_url, self.table_identity)
        ):
            raise OperatingTaxReadinessError("tax row reference identity must be complete")
        if (self.taxonomy_namespace is None) != (self.concept is None):
            raise OperatingTaxReadinessError(
                "tax row taxonomy and concept must be supplied together"
            )

    @classmethod
    def from_bridge(
        cls,
        bridge: TaxReconciliationBridge,
        row_index: int,
    ) -> OperatingTaxRowReference:
        """Build a guarded reference to an existing normalized bridge row."""
        try:
            row = bridge.rows[row_index]
        except IndexError as exc:
            raise OperatingTaxReadinessError(
                "tax row index is outside the bridge"
            ) from exc
        return cls(
            row_index=row_index,
            displayed_label=row.displayed_label,
            source_url=row.source.source_url,
            table_identity=row.source.table_identity,
            taxonomy_namespace=row.source.taxonomy_namespace,
            concept=row.source.concept,
            context_id=row.source.context_id,
        )

    def matches(self, row: TaxReconciliationRow) -> bool:
        return (
            self.displayed_label == row.displayed_label
            and self.source_url == row.source.source_url
            and self.table_identity == row.source.table_identity
            and self.taxonomy_namespace == row.source.taxonomy_namespace
            and self.concept == row.source.concept
            and self.context_id == row.source.context_id
        )


@dataclass(frozen=True)
class OperatingTaxEvidenceRequirement:
    """Evidence states accepted by one explicit policy decision."""

    allowed_statuses: tuple[TaxEvidenceStatus, ...] = (TaxEvidenceStatus.RESOLVED,)
    require_signed_amount: bool = True

    def __post_init__(self) -> None:
        if not self.allowed_statuses or any(
            not isinstance(status, TaxEvidenceStatus) for status in self.allowed_statuses
        ):
            raise OperatingTaxReadinessError("tax evidence requirements are invalid")
        if len(set(self.allowed_statuses)) != len(self.allowed_statuses):
            raise OperatingTaxReadinessError(
                "tax evidence requirements contain duplicate statuses"
            )
        if not isinstance(self.require_signed_amount, bool):
            raise OperatingTaxReadinessError("signed-amount requirement must be Boolean")


@dataclass(frozen=True)
class OperatingTaxRowDecision:
    """One explicit treatment of one guarded bridge row."""

    row: OperatingTaxRowReference
    treatment: TaxProposedTreatment
    evidence_requirement: OperatingTaxEvidenceRequirement
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(self.row, OperatingTaxRowReference):
            raise OperatingTaxReadinessError(
                "tax row decision requires a row reference"
            )
        if not isinstance(self.treatment, TaxProposedTreatment):
            raise OperatingTaxReadinessError("tax row decision treatment is invalid")
        if not isinstance(self.evidence_requirement, OperatingTaxEvidenceRequirement):
            raise OperatingTaxReadinessError(
                "tax row decision evidence requirement is invalid"
            )
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            raise OperatingTaxReadinessError("tax row decision requires a rationale")


@dataclass(frozen=True)
class OperatingTaxPair:
    """Complete, exclusive membership for one approved paired-net treatment."""

    pair_id: str
    members: tuple[OperatingTaxRowReference, ...]
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(self.pair_id, str) or not self.pair_id:
            raise OperatingTaxReadinessError("tax pair ID must be non-empty")
        if len(self.members) < 2 or len(set(self.members)) != len(self.members):
            raise OperatingTaxReadinessError(
                "tax pair requires at least two distinct rows"
            )
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            raise OperatingTaxReadinessError("tax pair requires a rationale")


@dataclass(frozen=True)
class OperatingTaxPolicy:
    """Immutable versioned readiness policy for one issuer.

    A new version is required when treatment, pairing, allocation, supported
    periods, readiness, loss behavior, or future calculation semantics change.
    """

    policy_id: str
    version: str
    company_cik: int
    row_decisions: tuple[OperatingTaxRowDecision, ...]
    pairs: tuple[OperatingTaxPair, ...]
    rationale: str
    loss_policy: OperatingTaxLossPolicy = (
        OperatingTaxLossPolicy.BLOCK_NONPOSITIVE_OPERATING_OR_NEGATIVE_PRETAX
    )
    supported_accessions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (
            any(
                not isinstance(value, str) or not value
                for value in (self.policy_id, self.version)
            )
            or not isinstance(self.rationale, str)
            or not self.rationale.strip()
        ):
            raise OperatingTaxReadinessError(
                "operating-tax policy identity and rationale are required"
            )
        if (
            isinstance(self.company_cik, bool)
            or not isinstance(self.company_cik, int)
            or self.company_cik < 0
        ):
            raise OperatingTaxReadinessError(
                "operating-tax policy CIK must be a nonnegative integer"
            )
        if not all(
            isinstance(decision, OperatingTaxRowDecision)
            for decision in self.row_decisions
        ):
            raise OperatingTaxReadinessError(
                "operating-tax policy contains an invalid row decision"
            )
        references = tuple(decision.row for decision in self.row_decisions)
        if len(set(references)) != len(references):
            raise OperatingTaxReadinessError(
                "operating-tax policy contains conflicting row decisions"
            )
        if len(set(self.supported_accessions)) != len(self.supported_accessions) or any(
            not isinstance(accession, str) or not accession
            for accession in self.supported_accessions
        ):
            raise OperatingTaxReadinessError("operating-tax policy accessions are invalid")
        if self.loss_policy is not (
            OperatingTaxLossPolicy.BLOCK_NONPOSITIVE_OPERATING_OR_NEGATIVE_PRETAX
        ):
            raise OperatingTaxReadinessError(
                "operating-tax policy loss behavior is unsupported"
            )
        if not all(isinstance(pair, OperatingTaxPair) for pair in self.pairs):
            raise OperatingTaxReadinessError("operating-tax policy contains an invalid pair")
        pair_ids = tuple(pair.pair_id for pair in self.pairs)
        if len(set(pair_ids)) != len(pair_ids):
            raise OperatingTaxReadinessError("operating-tax policy contains duplicate pair IDs")
        paired_members = tuple(member for pair in self.pairs for member in pair.members)
        if len(set(paired_members)) != len(paired_members):
            raise OperatingTaxReadinessError("a tax row cannot belong to multiple pairs")
        if any(member not in references for member in paired_members):
            raise OperatingTaxReadinessError(
                "tax pair references a row without a policy decision"
            )


@dataclass(frozen=True)
class OperatingTaxReadinessContext:
    """Owned normalized inputs and filing evidence for readiness evaluation."""

    financials: NormalizedHistoricalFinancials
    filing_result: HistoricalFilingResult
    bridge: TaxReconciliationBridge
    bridge_monetary_basis: TaxMonetaryBasis
    statutory_anchor: StatutoryRateAnchor | None
    requested_policy_id: str
    requested_policy_version: str
    realizability_resolved: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.financials, NormalizedHistoricalFinancials):
            raise OperatingTaxReadinessError(
                "operating-tax context requires normalized financials"
            )
        if not isinstance(self.filing_result, HistoricalFilingResult):
            raise OperatingTaxReadinessError(
                "operating-tax context requires an annual filing result"
            )
        if not isinstance(self.bridge, TaxReconciliationBridge):
            raise OperatingTaxReadinessError("operating-tax context requires a tax bridge")
        if not isinstance(self.bridge_monetary_basis, TaxMonetaryBasis):
            raise OperatingTaxReadinessError(
                "operating-tax context requires a monetary basis"
            )
        if self.statutory_anchor is not None and not isinstance(
            self.statutory_anchor,
            StatutoryRateAnchor,
        ):
            raise OperatingTaxReadinessError("operating-tax statutory anchor is invalid")
        if any(
            not isinstance(value, str) or not value
            for value in (self.requested_policy_id, self.requested_policy_version)
        ):
            raise OperatingTaxReadinessError(
                "requested operating-tax policy identity is required"
            )
        if not isinstance(self.realizability_resolved, bool):
            raise OperatingTaxReadinessError("tax-benefit realizability state must be Boolean")


@dataclass(frozen=True)
class OperatingTaxReadinessIssue:
    """One typed reason a context is not calculation-ready."""

    status: OperatingTaxReadinessStatus
    message: str
    rows: tuple[OperatingTaxRowReference, ...] = ()

    def __post_init__(self) -> None:
        if self.status is OperatingTaxReadinessStatus.READY:
            raise OperatingTaxReadinessError("a readiness issue cannot have READY status")
        if not isinstance(self.message, str) or not self.message:
            raise OperatingTaxReadinessError("readiness issue requires a message")


@dataclass(frozen=True)
class OperatingTaxReadinessResult:
    """Readiness outcome retaining compact inputs, policy, and full tax bridge."""

    status: OperatingTaxReadinessStatus
    company: SECCompanyIdentity
    filing: SECFiling
    policy: OperatingTaxPolicy
    bridge: TaxReconciliationBridge
    bridge_monetary_basis: TaxMonetaryBasis
    operating_income: ResolvedHistoricalValue | None
    pretax_income: ResolvedHistoricalValue | None
    statutory_anchor: StatutoryRateAnchor | None
    row_decisions: tuple[OperatingTaxRowDecision, ...]
    pairs: tuple[OperatingTaxPair, ...]
    issues: tuple[OperatingTaxReadinessIssue, ...]

    def __post_init__(self) -> None:
        if self.status is OperatingTaxReadinessStatus.READY:
            if (
                self.issues
                or self.operating_income is None
                or self.pretax_income is None
                or self.statutory_anchor is None
            ):
                raise OperatingTaxReadinessError(
                    "READY operating-tax result must be complete and issue-free"
                )
        elif not self.issues or all(
            issue.status is not self.status for issue in self.issues
        ):
            raise OperatingTaxReadinessError(
                "blocked operating-tax result must retain its typed issue"
            )

    @property
    def is_ready(self) -> bool:
        return self.status is OperatingTaxReadinessStatus.READY


def evaluate_operating_tax_readiness(
    context: OperatingTaxReadinessContext,
    policy: OperatingTaxPolicy,
) -> OperatingTaxReadinessResult:
    """Validate readiness without calculating operating tax or NOPAT."""
    if not isinstance(context, OperatingTaxReadinessContext) or not isinstance(
        policy,
        OperatingTaxPolicy,
    ):
        raise OperatingTaxReadinessError(
            "operating-tax readiness requires typed context and policy"
        )
    _validate_ownership(context)
    decisions = tuple(sorted(policy.row_decisions, key=lambda decision: decision.row.row_index))
    pairs = tuple(
        sorted(
            (
                replace(
                    pair,
                    members=tuple(
                        sorted(pair.members, key=lambda member: member.row_index)
                    ),
                )
                for pair in policy.pairs
            ),
            key=lambda pair: pair.pair_id,
        )
    )
    operating_income, oi_issue = _metric(
        context.filing_result,
        FinancialMetric.OPERATING_INCOME,
    )
    pretax_income, pretax_issue = _metric(
        context.filing_result,
        FinancialMetric.PRETAX_INCOME,
    )

    if policy.company_cik != context.financials.company.cik:
        raise OperatingTaxReadinessError(
            "operating-tax policy issuer does not match context issuer"
        )
    if (
        policy.policy_id != context.requested_policy_id
        or policy.version != context.requested_policy_version
    ):
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            pretax_income,
            OperatingTaxReadinessStatus.POLICY_MISMATCH,
            "requested operating-tax policy identity/version does not match supplied policy",
        )
    if (
        policy.supported_accessions
        and context.filing_result.filing.accession_number
        not in policy.supported_accessions
    ):
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            pretax_income,
            OperatingTaxReadinessStatus.UNSUPPORTED_POLICY,
            "operating-tax policy does not support the selected filing",
        )
    if oi_issue is not None:
        return _result(
            context,
            policy,
            decisions,
            pairs,
            None,
            pretax_income,
            oi_issue,
            "reported Operating Income is not resolved",
        )
    if pretax_issue is not None:
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            None,
            pretax_issue,
            "Pretax Income is not resolved",
        )
    assert operating_income is not None and pretax_income is not None
    _validate_financial_inputs(context, operating_income, pretax_income)

    if context.statutory_anchor is None:
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            pretax_income,
            OperatingTaxReadinessStatus.MISSING_INPUT,
            "an evidenced statutory-rate anchor is required",
        )
    _validate_statutory_anchor(context, context.statutory_anchor)
    if context.bridge.reconciliation_status is TaxReconciliationStatus.UNRECONCILED:
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            pretax_income,
            OperatingTaxReadinessStatus.UNRECONCILED_BRIDGE,
            "tax reconciliation bridge is unreconciled",
        )
    if context.bridge.reconciliation_status is TaxReconciliationStatus.INCOMPLETE_EVIDENCE:
        ambiguous = any(
            row.evidence_status
            in (
                TaxEvidenceStatus.AMBIGUOUS_SIGN,
                TaxEvidenceStatus.COMPETING_EVIDENCE,
                TaxEvidenceStatus.SOURCE_CONFLICT,
            )
            for row in context.bridge.rows
        )
        status = (
            OperatingTaxReadinessStatus.AMBIGUOUS_INPUT
            if ambiguous
            else OperatingTaxReadinessStatus.MISSING_INPUT
        )
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            pretax_income,
            status,
            "tax reconciliation bridge has incomplete evidence",
        )
    if (
        operating_income.value <= 0
        or pretax_income.value < 0
        or not context.realizability_resolved
    ):
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            pretax_income,
            OperatingTaxReadinessStatus.LOSS_POLICY_BLOCKED,
            "nonpositive income or unresolved benefit realizability is not supported",
        )
    _validate_monetary_basis(context, pretax_income, context.statutory_anchor)

    row_issue = _validate_row_coverage(context.bridge, decisions, pairs)
    if row_issue is not None:
        return _result(
            context,
            policy,
            decisions,
            pairs,
            operating_income,
            pretax_income,
            row_issue.status,
            row_issue.message,
            row_issue.rows,
        )
    return OperatingTaxReadinessResult(
        status=OperatingTaxReadinessStatus.READY,
        company=context.financials.company,
        filing=context.filing_result.filing,
        policy=policy,
        bridge=context.bridge,
        bridge_monetary_basis=context.bridge_monetary_basis,
        operating_income=operating_income,
        pretax_income=pretax_income,
        statutory_anchor=context.statutory_anchor,
        row_decisions=decisions,
        pairs=pairs,
        issues=(),
    )


def _validate_ownership(context: OperatingTaxReadinessContext) -> None:
    financials = context.financials
    filing_result = context.filing_result
    if not isinstance(financials, NormalizedHistoricalFinancials) or not isinstance(
        filing_result,
        HistoricalFilingResult,
    ):
        raise OperatingTaxReadinessError(
            "operating-tax context requires normalized financial inputs"
        )
    if not any(result is filing_result for result in financials.annual):
        raise OperatingTaxReadinessError(
            "annual filing result is not owned by normalized financials"
        )
    filing = filing_result.filing
    if filing.form != "10-K" or filing.report_date is None:
        raise OperatingTaxReadinessError(
            "operating-tax readiness requires a selected 10-K with report date"
        )
    selected = context.bridge.selected_filing
    if selected.company.cik != financials.company.cik:
        raise OperatingTaxReadinessError("tax bridge issuer does not match normalized financials")
    if selected.filing != filing:
        raise OperatingTaxReadinessError(
            "tax bridge selected filing does not match financial filing"
        )


def _metric(
    filing_result: HistoricalFilingResult,
    metric: FinancialMetric,
) -> tuple[ResolvedHistoricalValue | None, OperatingTaxReadinessStatus | None]:
    matches = tuple(
        result for result in filing_result.metrics if result.metric is metric
    )
    if len(matches) != 1:
        raise OperatingTaxReadinessError(
            f"annual financial result must contain one {metric.value} result"
        )
    result = matches[0]
    if isinstance(result, MissingHistoricalMetric):
        return None, OperatingTaxReadinessStatus.MISSING_INPUT
    if isinstance(result, AmbiguousHistoricalMetric):
        return None, OperatingTaxReadinessStatus.AMBIGUOUS_INPUT
    return result, None


def _validate_financial_inputs(
    context: OperatingTaxReadinessContext,
    operating_income: ResolvedHistoricalValue,
    pretax_income: ResolvedHistoricalValue,
) -> None:
    report_date = context.filing_result.filing.report_date
    accession = context.filing_result.filing.accession_number
    for metric, value in (
        (FinancialMetric.OPERATING_INCOME, operating_income),
        (FinancialMetric.PRETAX_INCOME, pretax_income),
    ):
        if not isinstance(value, NormalizedHistoricalValue):
            raise OperatingTaxReadinessError(
                "Operating Income and Pretax Income must be direct normalized values"
            )
        if value.unit != "USD" or value.period.end != report_date:
            raise OperatingTaxReadinessError("financial input unit or period is incompatible")
        _validate_financial_evidence(
            context,
            metric,
            value,
            value.chosen_source,
            accession,
            report_date,
        )
        for confirming in value.confirming_sources:
            _validate_financial_evidence(
                context,
                metric,
                value,
                confirming,
                accession,
                report_date,
            )
    if operating_income.period != pretax_income.period:
        raise OperatingTaxReadinessError(
            "Operating Income and Pretax Income periods do not match"
        )
    if not _is_finite_numeric(operating_income.value) or not _is_finite_numeric(
        pretax_income.value
    ):
        raise OperatingTaxReadinessError("financial inputs must be numeric and non-Boolean")


def _validate_financial_evidence(
    context: OperatingTaxReadinessContext,
    metric: FinancialMetric,
    value: NormalizedHistoricalValue,
    evidence: FactEvidence,
    accession: str,
    report_date: date,
) -> None:
    expected_taxonomy, expected_concept = _EXPECTED_FINANCIAL_CONCEPTS[metric]
    if (
        value.metric is not metric
        or evidence.source_kind is not EvidenceSourceKind.COMPANY_FACTS
        or evidence.taxonomy != expected_taxonomy
        or evidence.concept != expected_concept
        or evidence.observation_form != "10-K"
        or evidence.observation_filed != context.filing_result.filing.filing_date
        or evidence.accession_number != accession
        or evidence.start != value.period.start
        or evidence.end != report_date
        or evidence.unit != value.unit
        or evidence.value != value.value
        or evidence.source_url != context.financials.company_facts_source_url
    ):
        raise OperatingTaxReadinessError(
            f"{metric.value} evidence does not match its approved selected-filing semantics"
        )


def _validate_statutory_anchor(
    context: OperatingTaxReadinessContext,
    anchor: StatutoryRateAnchor,
) -> None:
    selected = context.bridge.selected_filing
    if (
        anchor.issuer_cik != selected.issuer_cik
        or anchor.accession_number != selected.accession_number
        or anchor.report_date != selected.report_date
        or anchor.source.source_url != selected.source_url
    ):
        raise OperatingTaxReadinessError(
            "statutory-rate anchor does not belong to selected filing"
        )
    if (
        context.bridge.style is TaxBridgeStyle.RATE
        and anchor.rate != context.bridge.starting_value
    ):
        raise OperatingTaxReadinessError(
            "statutory-rate anchor does not match rate-bridge start"
        )


def _validate_monetary_basis(
    context: OperatingTaxReadinessContext,
    pretax_income: ResolvedHistoricalValue,
    anchor: StatutoryRateAnchor,
) -> None:
    basis = context.bridge_monetary_basis
    if basis.currency != pretax_income.unit:
        raise OperatingTaxReadinessError(
            "tax bridge currency does not match normalized financial inputs"
        )
    bridge = context.bridge
    pretax_decimal = _as_exact_decimal(pretax_income.value)
    if bridge.style is TaxBridgeStyle.DOLLAR:
        if (
            basis.bridge_currency_label is None
            or basis.bridge_currency_label != bridge.currency_code
        ):
            raise OperatingTaxReadinessError(
                "dollar bridge currency/scale label is not explicitly bound"
            )
        normalized_start = _exact_multiply(bridge.starting_value, basis.scale)
        expected_start = _exact_multiply(
            pretax_decimal,
            anchor.rate,
            Decimal("0.01"),
        )
        rounding_tolerance = _exact_multiply(
            bridge.displayed_precision,
            basis.scale,
            Decimal("0.5"),
        )
        difference = abs(_exact_subtract(normalized_start, expected_start))
        if difference > rounding_tolerance:
            raise OperatingTaxReadinessError(
                "dollar bridge scale is incompatible with Pretax Income and statutory rate"
            )
    else:
        if basis.bridge_currency_label is not None:
            raise OperatingTaxReadinessError(
                "rate bridge cannot use a dollar currency label"
            )
        assert bridge.pretax_income is not None
        scaled_bridge_pretax = _exact_multiply(
            bridge.pretax_income,
            basis.scale,
        )
        if scaled_bridge_pretax != pretax_decimal:
            raise OperatingTaxReadinessError(
                "tax bridge scale does not match normalized Pretax Income"
            )


def _is_finite_numeric(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        return False
    if isinstance(value, Decimal):
        return value.is_finite()
    return True


def _as_exact_decimal(value: int | Decimal) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise OperatingTaxReadinessError(
            "operating-tax monetary inputs must be exact integers or Decimals"
        )
    result = Decimal(value) if isinstance(value, int) else value
    if not result.is_finite():
        raise OperatingTaxReadinessError(
            "operating-tax monetary inputs must be finite"
        )
    return result


def _exact_multiply(*values: Decimal) -> Decimal:
    if not values:
        return Decimal(1)
    precision = sum(len(value.as_tuple().digits) for value in values) + 2
    with localcontext() as context:
        context.prec = max(context.prec, precision)
        result = Decimal(1)
        for value in values:
            result *= value
        return result


def _exact_subtract(left: Decimal, right: Decimal) -> Decimal:
    min_exponent = min(left.as_tuple().exponent, right.as_tuple().exponent)
    max_adjusted = max(
        left.adjusted() if left else min_exponent,
        right.adjusted() if right else min_exponent,
    )
    precision = max_adjusted - min_exponent + 3
    with localcontext() as context:
        context.prec = max(context.prec, precision)
        return left - right


def _validate_row_coverage(
    bridge: TaxReconciliationBridge,
    decisions: tuple[OperatingTaxRowDecision, ...],
    pairs: tuple[OperatingTaxPair, ...],
) -> OperatingTaxReadinessIssue | None:
    if len(decisions) != len(bridge.rows):
        return OperatingTaxReadinessIssue(
            OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED,
            "every bridge row must have exactly one policy decision",
        )
    decision_by_ref = {decision.row: decision for decision in decisions}
    paired_refs = {member for pair in pairs for member in pair.members}
    for decision in decisions:
        reference = decision.row
        if reference.row_index >= len(bridge.rows) or not reference.matches(
            bridge.rows[reference.row_index]
        ):
            return OperatingTaxReadinessIssue(
                OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED,
                "policy row reference does not match the normalized bridge",
                (reference,),
            )
        row = bridge.rows[reference.row_index]
        requirement = decision.evidence_requirement
        if row.evidence_status not in requirement.allowed_statuses:
            status = (
                OperatingTaxReadinessStatus.AMBIGUOUS_INPUT
                if row.evidence_status in (
                    TaxEvidenceStatus.AMBIGUOUS_SIGN,
                    TaxEvidenceStatus.COMPETING_EVIDENCE,
                    TaxEvidenceStatus.SOURCE_CONFLICT,
                )
                else OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED
            )
            return OperatingTaxReadinessIssue(
                status,
                "tax row does not meet policy evidence requirements",
                (reference,),
            )
        if requirement.require_signed_amount and row.signed_tax_amount is None:
            return OperatingTaxReadinessIssue(
                OperatingTaxReadinessStatus.MISSING_INPUT,
                "tax row lacks a required signed amount",
                (reference,),
            )
        if decision.treatment in (
            TaxProposedTreatment.METHODOLOGY_UNRESOLVED,
            TaxProposedTreatment.REQUIRES_PAIRED_INCOME_ADJUSTMENT,
        ):
            return OperatingTaxReadinessIssue(
                OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED,
                "tax row treatment is not calculation-ready",
                (reference,),
            )
        is_paired = decision.treatment is TaxProposedTreatment.INCLUDE_PAIRED_NET_EFFECT
        if is_paired != (reference in paired_refs):
            return OperatingTaxReadinessIssue(
                OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED,
                "paired-net decision has incomplete or inconsistent pair membership",
                (reference,),
            )
    if set(decision_by_ref) != {
        OperatingTaxRowReference.from_bridge(bridge, index)
        for index in range(len(bridge.rows))
    }:
        return OperatingTaxReadinessIssue(
            OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED,
            "policy does not cover the exact bridge row inventory",
        )
    return None


def _result(
    context: OperatingTaxReadinessContext,
    policy: OperatingTaxPolicy,
    decisions: tuple[OperatingTaxRowDecision, ...],
    pairs: tuple[OperatingTaxPair, ...],
    operating_income: ResolvedHistoricalValue | None,
    pretax_income: ResolvedHistoricalValue | None,
    status: OperatingTaxReadinessStatus,
    message: str,
    rows: tuple[OperatingTaxRowReference, ...] = (),
) -> OperatingTaxReadinessResult:
    return OperatingTaxReadinessResult(
        status=status,
        company=context.financials.company,
        filing=context.filing_result.filing,
        policy=policy,
        bridge=context.bridge,
        bridge_monetary_basis=context.bridge_monetary_basis,
        operating_income=operating_income,
        pretax_income=pretax_income,
        statutory_anchor=context.statutory_anchor,
        row_decisions=decisions,
        pairs=pairs,
        issues=(OperatingTaxReadinessIssue(status, message, rows),),
    )
