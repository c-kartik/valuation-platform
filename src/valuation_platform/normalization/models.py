"""Shared immutable models for direct and derived financial normalization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TypeAlias

from valuation_platform.sec.filing_xbrl import FilingXBRLDimension
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity

from .concepts import ConceptKey, FinancialMetric


class MissingReason(str, Enum):
    """Expected reasons a selected filing has no normalized metric value."""

    NO_CONFIGURED_CONCEPT_OBSERVATION = "no_configured_concept_observation"
    NO_VALID_CURRENT_ANNUAL_OBSERVATION = "no_valid_current_annual_observation"
    NO_VALID_DERIVATION_OPERANDS = "no_valid_derivation_operands"
    MISSING_DERIVATION_OPERAND = "missing_derivation_operand"
    ZERO_DERIVATION_DENOMINATOR = "zero_derivation_denominator"
    NO_VALID_CURRENT_INSTANT_OBSERVATION = (
        "no_valid_current_instant_observation"
    )


class AmbiguityReason(str, Enum):
    """Reasons available observations cannot produce one annual value."""

    CONFLICTING_CONCEPT_VALUES = "conflicting_concept_values"
    MULTIPLE_ANNUAL_PERIODS = "multiple_annual_periods"
    INCOMPATIBLE_DERIVATION_OPERANDS = "incompatible_derivation_operands"


class EvidenceSourceKind(str, Enum):
    """SEC source that supplied one normalized fact observation."""

    COMPANY_FACTS = "company_facts"
    FILING_XBRL = "filing_xbrl"


class DerivationOperation(str, Enum):
    """Supported arithmetic operations for derived historical values."""

    ADD = "add"
    DIVIDE = "divide"
    SUBTRACT = "subtract"


class DerivationDiagnostic(str, Enum):
    """Analytical cautions attached to a valid derived value."""

    NEGATIVE_DENOMINATOR = "negative_denominator"


@dataclass(frozen=True)
class HistoricalPeriod:
    """The actual economic duration represented by a normalized value."""

    start: date
    end: date


@dataclass(frozen=True)
class FactEvidence:
    """Compact SEC provenance for one candidate or operand fact."""

    source_kind: EvidenceSourceKind
    source_url: str
    taxonomy: str
    concept: str
    value: int | float
    unit: str
    start: date | None
    end: date
    accession_number: str
    observation_form: str
    observation_filed: date
    fiscal_year: int | None
    fiscal_period: str | None
    frame: str | None


@dataclass(frozen=True)
class FilingXBRLEvidence:
    """Compact provenance for one filing-level extracted XBRL fact."""

    source_kind: EvidenceSourceKind
    source_url: str
    namespace: str
    concept: str
    raw_value: str | None
    value: Decimal
    unit: str
    start: date | None
    end: date
    accession_number: str
    observation_form: str
    observation_filed: date
    filing_report_date: date | None
    primary_document: str
    retrieved_at: datetime
    context_id: str
    dimensions: tuple[FilingXBRLDimension, ...]
    decimals: str | None
    is_nil: bool


BalanceSheetFactEvidence: TypeAlias = FactEvidence | FilingXBRLEvidence


@dataclass(frozen=True)
class NormalizedHistoricalValue:
    """One resolved direct annual financial value."""

    metric: FinancialMetric
    value: int | float
    unit: str
    period: HistoricalPeriod
    chosen_source: FactEvidence
    confirming_sources: tuple[FactEvidence, ...]


@dataclass(frozen=True)
class DerivedMetricOperand:
    """One resolved direct normalized metric used in a derivation."""

    metric: FinancialMetric
    value: int | float
    unit: str
    period: HistoricalPeriod
    chosen_source: FactEvidence
    confirming_sources: tuple[FactEvidence, ...]


@dataclass(frozen=True)
class DerivedHistoricalValue:
    """One resolved annual value calculated from approved SEC operands."""

    metric: FinancialMetric
    value: int | float | Decimal
    unit: str
    period: HistoricalPeriod
    policy_id: str
    operation: DerivationOperation
    operands: tuple[FactEvidence, ...]
    metric_operands: tuple[DerivedMetricOperand, ...] = ()
    diagnostics: tuple[DerivationDiagnostic, ...] = ()


@dataclass(frozen=True)
class MissingHistoricalMetric:
    """A metric that has no usable direct or derived value for one filing."""

    metric: FinancialMetric
    reason: MissingReason
    examined_concepts: tuple[ConceptKey, ...]


@dataclass(frozen=True)
class AmbiguousHistoricalMetric:
    """A metric with competing observations that cannot be resolved safely."""

    metric: FinancialMetric
    reason: AmbiguityReason
    candidates: tuple[BalanceSheetFactEvidence, ...]


ResolvedHistoricalValue: TypeAlias = (
    NormalizedHistoricalValue | DerivedHistoricalValue
)

HistoricalMetricResult: TypeAlias = (
    ResolvedHistoricalValue | MissingHistoricalMetric | AmbiguousHistoricalMetric
)


@dataclass(frozen=True)
class HistoricalFilingResult:
    """Normalized metric results for one selected annual filing."""

    filing: SECFiling
    metrics: tuple[HistoricalMetricResult, ...]


@dataclass(frozen=True)
class NormalizedHistoricalFinancials:
    """Compact annual financial history with company and SEC provenance."""

    company: SECCompanyIdentity
    company_facts_source_url: str
    company_facts_retrieved_at: datetime
    annual: tuple[HistoricalFilingResult, ...]


@dataclass(frozen=True)
class NormalizedBalanceSheetValue:
    """One resolved direct annual balance-sheet snapshot."""

    metric: FinancialMetric
    value: int | float | Decimal
    unit: str
    balance_date: date
    chosen_source: BalanceSheetFactEvidence
    confirming_sources: tuple[BalanceSheetFactEvidence, ...]


@dataclass(frozen=True)
class BalanceSheetDerivationOperand:
    """One evidence-backed operand used by a balance-sheet derivation."""

    metric: FinancialMetric
    value: int | float | Decimal
    unit: str
    start: date | None
    end: date
    chosen_source: BalanceSheetFactEvidence
    confirming_sources: tuple[BalanceSheetFactEvidence, ...]


@dataclass(frozen=True)
class BalanceSheetConceptDerivationOperand:
    """One concept-specific source operand used by a balance-sheet derivation."""

    name: str
    value: Decimal
    unit: str
    start: date | None
    end: date
    chosen_source: FactEvidence


BalanceSheetDerivedOperand: TypeAlias = (
    BalanceSheetDerivationOperand | BalanceSheetConceptDerivationOperand
)


@dataclass(frozen=True)
class BalanceSheetDerivationStep:
    """One ordered arithmetic step retained in derived-balance provenance."""

    name: str
    operation: DerivationOperation
    operand_names: tuple[str, str]
    value: Decimal


@dataclass(frozen=True)
class DerivedBalanceSheetValue:
    """One balance derived from approved primitive and special evidence."""

    metric: FinancialMetric
    value: Decimal
    unit: str
    balance_date: date
    policy_id: str
    operation: DerivationOperation
    operands: tuple[BalanceSheetDerivedOperand, ...]
    steps: tuple[BalanceSheetDerivationStep, ...]


ResolvedBalanceSheetValue: TypeAlias = (
    NormalizedBalanceSheetValue | DerivedBalanceSheetValue
)


BalanceSheetMetricResult: TypeAlias = (
    ResolvedBalanceSheetValue | MissingHistoricalMetric | AmbiguousHistoricalMetric
)


@dataclass(frozen=True)
class AnnualBalanceSheetFilingResult:
    """Normalized primitive balances for one selected annual filing."""

    filing: SECFiling
    metrics: tuple[BalanceSheetMetricResult, ...]


@dataclass(frozen=True)
class NormalizedAnnualBalanceSheets:
    """Compact annual balance-sheet snapshots with SEC provenance."""

    company: SECCompanyIdentity
    company_facts_source_url: str
    company_facts_retrieved_at: datetime
    annual: tuple[AnnualBalanceSheetFilingResult, ...]
