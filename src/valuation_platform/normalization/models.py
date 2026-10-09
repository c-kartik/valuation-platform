"""Shared immutable models for direct and derived financial normalization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import re
from typing import TypeAlias

from valuation_platform.sec.filing_xbrl import FilingXBRLDimension
from valuation_platform.sec.annual_period import AnnualPeriodResolution
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
class ReviewedPolicyEvidence:
    """One reviewed filing reference supporting a curated policy decision."""

    evidence_id: str
    source_url: str
    filing_location: str
    research_artifact: str
    reviewed_on: date
    review_status: str
    rationale: str
    content_digest: str

    def __post_init__(self) -> None:
        if (
            not self.evidence_id
            or not self.source_url.startswith("https://www.sec.gov/Archives/")
            or not self.filing_location
            or not self.research_artifact.startswith("docs/")
            or self.review_status != "approved"
            or not self.rationale
            or not self.content_digest
        ):
            raise ValueError("Reviewed policy evidence is incomplete")


@dataclass(frozen=True)
class HistoricalPolicyProvenance:
    """Versioned policy identity and reviewed evidence retained with a value."""

    policy_id: str
    policy_version: str
    economic_scope: str
    company_cik: int
    accession_number: str
    report_date: date
    annual_start: date
    annual_end: date
    taxonomy: str
    concept: str
    unit: str
    reviewed_evidence: tuple[ReviewedPolicyEvidence, ...]
    filing_xbrl_evidence: tuple[FilingXBRLEvidence, ...]

    def __post_init__(self) -> None:
        if (
            not self.policy_id
            or not self.policy_version
            or not self.economic_scope
            or not isinstance(self.company_cik, int)
            or isinstance(self.company_cik, bool)
            or self.company_cik < 0
            or re.fullmatch(r"[0-9]{10}-[0-9]{2}-[0-9]{6}", self.accession_number)
            is None
            or self.annual_start >= self.annual_end
            or self.annual_end != self.report_date
            or not self.taxonomy
            or not self.concept
            or not self.unit
            or not self.reviewed_evidence
            or not self.filing_xbrl_evidence
        ):
            raise ValueError("Historical policy provenance is incomplete")
        for evidence in self.filing_xbrl_evidence:
            if (
                evidence.accession_number != self.accession_number
                or evidence.start != self.annual_start
                or evidence.end != self.annual_end
                or evidence.concept != self.concept
                or evidence.unit != self.unit
                or evidence.dimensions
                or evidence.unit_ref is None
                or evidence.occurrence_ordinal is None
            ):
                raise ValueError("Policy filing-XBRL evidence does not match its key")
        if tuple(
            evidence.occurrence_ordinal for evidence in self.filing_xbrl_evidence
        ) != tuple(range(1, len(self.filing_xbrl_evidence) + 1)):
            raise ValueError(
                "Policy filing-XBRL evidence ordinals must be consecutive"
            )


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
    unit_ref: str | None = None
    occurrence_ordinal: int | None = None


BalanceSheetFactEvidence: TypeAlias = FactEvidence | FilingXBRLEvidence


@dataclass(frozen=True)
class NormalizedHistoricalValue:
    """One resolved direct annual financial value."""

    metric: FinancialMetric
    value: int | float | Decimal
    unit: str
    period: HistoricalPeriod
    chosen_source: FactEvidence
    confirming_sources: tuple[FactEvidence, ...]
    policy_provenance: HistoricalPolicyProvenance | None = None


@dataclass(frozen=True)
class DerivedMetricOperand:
    """One resolved direct normalized metric used in a derivation."""

    metric: FinancialMetric
    value: int | float
    unit: str
    period: HistoricalPeriod
    chosen_source: FactEvidence
    confirming_sources: tuple[FactEvidence, ...]
    policy_provenance: HistoricalPolicyProvenance | None = None


@dataclass(frozen=True)
class DerivedHistoricalValue:
    """One resolved annual value calculated from approved SEC operands."""

    metric: FinancialMetric
    value: int | float | Decimal
    unit: str
    period: HistoricalPeriod
    policy_id: str
    operation: DerivationOperation
    operands: tuple[BalanceSheetFactEvidence, ...]
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
    annual_period: AnnualPeriodResolution | None = None


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
