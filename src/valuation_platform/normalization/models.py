"""Shared immutable models for direct and derived financial normalization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import re
from typing import TypeAlias

from valuation_platform.sec.filing_xbrl import (
    FilingXBRLContext, FilingXBRLDimension, FilingXBRLFact,
)
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
    CURATED_D_AND_A_EVIDENCE_MISMATCH = "curated_d_and_a_evidence_mismatch"
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
class DAndAOccurrenceAudit:
    """Original instance ordering and an explicit curated eligibility decision."""

    original_instance_ordinal: int
    fact: FilingXBRLFact
    context: FilingXBRLContext
    disposition: str


@dataclass(frozen=True)
class DAndAScopeAudit:
    """Immutable reviewed entry and separately typed support, not operands."""

    reviewed_entry_json: str
    verified_artifact_digests: tuple[tuple[str, str], ...]
    confirming_original_ordinals: tuple[int, ...]
    supporting_facts: tuple[FilingXBRLEvidence, ...]
    occurrences: tuple[DAndAOccurrenceAudit, ...]


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
    d_and_a_scope: DAndAScopeAudit | None = None

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
    entity_identifier_scheme: str | None = None
    entity_identifier: str | None = None


@dataclass(frozen=True)
class OperatingIncomeOperandEvidence:
    """One ordered reviewed operand and all of its filing occurrences."""

    ordinal: int
    operand_id: str
    economic_role: str
    namespace: str
    concept: str
    expected_value: Decimal | None
    coefficient: Decimal | None
    contribution: Decimal | None
    occurrences: tuple[FilingXBRLEvidence, ...]
    reviewed_nonselected_occurrences: tuple[FilingXBRLEvidence, ...] = ()
    absence_reviewed: bool = False
    reviewed_nonselected_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (
            not isinstance(self.occurrences, tuple)
            or not isinstance(self.reviewed_nonselected_occurrences, tuple)
            or not isinstance(self.reviewed_nonselected_reasons, tuple)
            or len(self.reviewed_nonselected_reasons) != len(self.reviewed_nonselected_occurrences)
            or any(not item for item in self.reviewed_nonselected_reasons)
            or not isinstance(self.ordinal, int)
            or isinstance(self.ordinal, bool)
            or self.ordinal < 1
            or not self.operand_id
            or not self.economic_role
            or not self.namespace
            or not self.concept
        ):
            raise ValueError("Operating Income operand evidence is incomplete")
        if self.absence_reviewed:
            if any(
                item is not None
                for item in (
                    self.expected_value,
                    self.coefficient,
                    self.contribution,
                )
            ) or self.occurrences:
                raise ValueError("Reviewed absence cannot contain numeric evidence")
            if tuple(
                item.occurrence_ordinal
                for item in self.reviewed_nonselected_occurrences
            ) != tuple(range(1, len(self.reviewed_nonselected_occurrences) + 1)):
                raise ValueError("Reviewed absence occurrence order is invalid")
            return
        if (
            self.expected_value is None
            or not self.expected_value.is_finite()
            or self.coefficient not in (Decimal("1"), Decimal("-1"), None)
            or (
                self.coefficient is None
                and self.contribution is not None
            )
            or (
                self.coefficient is not None
                and self.contribution
                != self.coefficient * self.expected_value
            )
            or not self.occurrences
        ):
            raise ValueError("Operating Income operand arithmetic is invalid")
        for collection in (
            self.occurrences,
            self.reviewed_nonselected_occurrences,
        ):
            if tuple(item.occurrence_ordinal for item in collection) != tuple(
                range(1, len(collection) + 1)
            ):
                raise ValueError("Operating Income occurrence order is invalid")


@dataclass(frozen=True)
class OperatingIncomeValidationEvidence:
    """One exact filing-arithmetic validation retained with a derivation."""

    validation_id: str
    reported_operand_id: str
    calculated_value: Decimal
    reported_value: Decimal
    variance: Decimal
    expected_variance: Decimal
    display_scale: Decimal
    passed: bool

    def __post_init__(self) -> None:
        if (
            not self.validation_id
            or not self.reported_operand_id
            or not all(
                isinstance(item, Decimal) and item.is_finite()
                for item in (
                    self.calculated_value,
                    self.reported_value,
                    self.variance,
                    self.expected_variance,
                    self.display_scale,
                )
            )
            or self.display_scale <= 0
            or self.variance != self.calculated_value - self.reported_value
            or self.passed != (self.variance == self.expected_variance)
        ):
            raise ValueError("Operating Income validation evidence is invalid")


@dataclass(frozen=True)
class OperatingIncomeDerivationPolicyProvenance:
    """Complete curated-policy provenance for one Operating Income result."""

    policy_id: str
    policy_version: str
    company_cik: int
    accession_number: str
    report_date: date
    annual_start: date
    annual_end: date
    formula_id: str
    perimeter_id: str
    unit: str
    calculated_value: Decimal
    reviewed_evidence: tuple[ReviewedPolicyEvidence, ...]
    operands: tuple[OperatingIncomeOperandEvidence, ...]
    validations: tuple[OperatingIncomeValidationEvidence, ...]

    def __post_init__(self) -> None:
        if (
            not self.policy_id
            or not self.policy_version
            or not isinstance(self.company_cik, int)
            or isinstance(self.company_cik, bool)
            or self.company_cik < 0
            or re.fullmatch(r"[0-9]{10}-[0-9]{2}-[0-9]{6}", self.accession_number)
            is None
            or self.annual_start >= self.annual_end
            or self.annual_end != self.report_date
            or not self.formula_id
            or not self.perimeter_id
            or self.unit != "USD"
            or not isinstance(self.calculated_value, Decimal)
            or not self.calculated_value.is_finite()
            or not self.reviewed_evidence
            or not self.operands
            or not self.validations
            or not all(isinstance(items, tuple) for items in (
                self.reviewed_evidence, self.operands, self.validations,
            ))
            or not all(item.passed for item in self.validations)
        ):
            raise ValueError("Operating Income derivation provenance is incomplete")
        ordinals = tuple(item.ordinal for item in self.operands)
        if ordinals != tuple(range(1, len(self.operands) + 1)):
            raise ValueError("Operating Income operand ordinals must be consecutive")
        if len({item.operand_id for item in self.operands}) != len(self.operands):
            raise ValueError("Operating Income operand identities must be unique")


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
    supporting_derivation_policies: tuple[
        OperatingIncomeDerivationPolicyProvenance, ...
    ] = ()


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
    policy_version: str | None = None
    derivation_provenance: OperatingIncomeDerivationPolicyProvenance | None = None


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
    supporting_derivation_policies: tuple[OperatingIncomeDerivationPolicyProvenance, ...] = ()


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
