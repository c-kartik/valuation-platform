"""Stage C signed bridge arithmetic; no candidate selection or approval workflow.

Coverage, sources, decisions and class/award policies are supplied declarations.
Their structural validation authenticates no evidence or economic completeness.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import date
from decimal import Context, Decimal, DecimalException, ROUND_HALF_EVEN, localcontext
from enum import Enum
import json
import re

from valuation_platform.analyst.historical_inputs import ManualIdentity
from .discounting import (
    DiscountedYearResult, EnterpriseValueResult, discount_to_enterprise_value,
    enterprise_value_to_dict,
)
from .forecast import ForecastValidationError, ForecastYearResult


CONVENTION_VERSION = "meta-base-equity-bridge-v1"
RESULT_SCHEMA = "stage-c-equity-bridge-v1"
AWARD_POLICY = "sbc_expensed_no_duplicate_service_charge_v1"
CLASS_CONVENTIONS = ("single_common_class", "explicit_common_unit_equivalence")
ORIGINS = ("reported", "derived", "proxy", "manual_input", "analyst_override", "synthetic")


class BridgeValidationError(ForecastValidationError):
    """Invalid declared bridge inputs or inconsistent Stage B handoff."""


class ComponentRole(str, Enum):
    ELIGIBLE_ASSET = "ELIGIBLE_ASSET"
    FINANCING_CLAIM = "FINANCING_CLAIM"
    OTHER_EQUITY_CLAIM = "OTHER_EQUITY_CLAIM"


def _text(value: object) -> None:
    if type(value) is not str or not value.strip():
        raise BridgeValidationError("Explicit nonempty metadata required")


def _references(values: tuple[str, ...], *, required: bool = False) -> None:
    if type(values) is not tuple or (required and not values):
        raise BridgeValidationError("Immutable explicit references required")
    for value in values:
        _text(value)
    if len(set(values)) != len(values):
        raise BridgeValidationError("Repeated reference")


def _company_date(company_cik: int, as_of: date) -> None:
    if type(company_cik) is not int or company_cik <= 0 or type(as_of) is not date:
        raise BridgeValidationError("Positive company CIK and exact observation date required")


def _decimal(value: object, *, positive: bool = False, nonnegative: bool = False) -> None:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise BridgeValidationError("Finite Decimal amount required; missing is not zero")
    if (positive and value <= 0) or (nonnegative and value < 0):
        raise BridgeValidationError("Amount outside permitted sign domain")


def _precision(value: str) -> None:
    if type(value) is not str or not re.fullmatch(r"INF|-?\d+", value):
        raise BridgeValidationError("Original precision or explicit synthetic equivalent required")


@dataclass(frozen=True)
class BridgeComponent:
    component_id: str
    company_cik: int
    role: ComponentRole
    amount: Decimal
    as_of: date
    population_id: str
    origin: str
    precision: str
    source_references: tuple[str, ...]
    decision_references: tuple[str, ...]
    rationale: str
    overlap_references: tuple[str, ...] = ()
    alternative_references: tuple[str, ...] = ()
    overlaps_forecast: bool = False
    unit: str = "USD"
    scale: int = 1

    def __post_init__(self) -> None:
        for value in (self.component_id, self.population_id, self.rationale):
            _text(value)
        _company_date(self.company_cik, self.as_of)
        if type(self.role) is not ComponentRole or self.origin not in ORIGINS:
            raise BridgeValidationError("Explicit role and operand origin required")
        _decimal(self.amount, nonnegative=True)
        _precision(self.precision)
        if self.unit != "USD" or type(self.scale) is not int or self.scale != 1:
            raise BridgeValidationError("Numeric operands must be base USD, scale 1")
        _references(self.source_references, required=True)
        _references(self.decision_references, required=True)
        _references(self.overlap_references)
        _references(self.alternative_references)
        if type(self.overlaps_forecast) is not bool:
            raise BridgeValidationError("Explicit forecast-overlap declaration required")


@dataclass(frozen=True)
class BridgeObservation:
    """Support/exclusion/omission metadata, never a signed numeric operand.

    An omission has no monetary amount. Missing sources need not be fabricated:
    its decision reference and rationale carry the explicit assumption instead.
    Support may preserve dates/units different from selected fiscal-end operands.
    """

    observation_id: str
    company_cik: int
    role: ComponentRole
    disposition: str
    population_id: str
    value: Decimal | None
    as_of: date | None
    unit: str
    precision: str | None
    origin: str
    source_references: tuple[str, ...]
    decision_references: tuple[str, ...]
    rationale: str

    def __post_init__(self) -> None:
        for value in (self.observation_id, self.population_id, self.unit, self.rationale):
            _text(value)
        if (type(self.company_cik) is not int or self.company_cik <= 0
                or (self.as_of is not None and type(self.as_of) is not date)
                or type(self.role) is not ComponentRole
                or self.disposition not in ("SUPPORT", "EXCLUDED", "OMISSION")
                or self.origin not in (*ORIGINS, "unavailable")):
            raise BridgeValidationError("Invalid non-operand observation metadata")
        _references(self.source_references, required=self.value is not None)
        _references(self.decision_references, required=True)
        if self.value is not None:
            _decimal(self.value)
            _precision(self.precision)
        elif self.precision is not None:
            raise BridgeValidationError("No invented precision for an absent amount")
        if self.disposition == "OMISSION" and self.value is not None:
            raise BridgeValidationError("Omission decisions must preserve a null amount, not zero")


@dataclass(frozen=True)
class PopulationCoverage:
    """One of three fixed bridge roles; a declared review, not an approval seal."""

    role: ComponentRole
    population_ids: tuple[str, ...]
    omission_references: tuple[str, ...]
    review: ManualIdentity
    decision_references: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.role) is not ComponentRole or type(self.review) is not ManualIdentity:
            raise BridgeValidationError("Explicit role and coverage review identity required")
        self.review.__post_init__()
        _references(self.population_ids)
        _references(self.omission_references)
        _references(self.decision_references, required=True)
        if not self.population_ids and not self.omission_references:
            raise BridgeValidationError("Empty populations require an explicit referenced omission")


@dataclass(frozen=True)
class ValuationShares:
    company_cik: int
    shares: Decimal
    observation_date: date
    class_id: str
    equivalence_convention: str
    award_policy: str
    award_policy_references: tuple[str, ...]
    source_references: tuple[str, ...]
    decision_references: tuple[str, ...]
    precision: str
    rationale: str
    unit: str = "shares"
    scale: int = 1

    def __post_init__(self) -> None:
        _company_date(self.company_cik, self.observation_date)
        _decimal(self.shares, positive=True)
        _text(self.class_id)
        _text(self.rationale)
        _precision(self.precision)
        if (self.equivalence_convention not in CLASS_CONVENTIONS
                or self.award_policy != AWARD_POLICY):
            raise BridgeValidationError("Unsupported declared class or SBC/award convention")
        for refs in (self.award_policy_references, self.source_references, self.decision_references):
            _references(refs, required=True)
        if self.unit != "shares" or type(self.scale) is not int or self.scale != 1:
            raise BridgeValidationError("Denominator must be actual share units, scale 1")


@dataclass(frozen=True)
class BridgeInputs:
    components: tuple[BridgeComponent, ...]
    observations: tuple[BridgeObservation, ...]
    shares: ValuationShares
    coverage: tuple[PopulationCoverage, ...]
    input_basis: str
    valuation_class_id: str
    unresolved_requirements: tuple[str, ...]
    convention_version: str = CONVENTION_VERSION

    def __post_init__(self) -> None:
        if (self.convention_version != CONVENTION_VERSION
                or self.input_basis not in ("SYNTHETIC_FIXTURE", "MANUAL_INPUT")):
            raise BridgeValidationError("Supported bridge convention and explicit input basis required")
        for values, cls in ((self.components, BridgeComponent),
                            (self.observations, BridgeObservation), (self.coverage, PopulationCoverage)):
            if type(values) is not tuple or any(type(value) is not cls for value in values):
                raise BridgeValidationError("Immutable exact input tuples required")
            for value in values:
                value.__post_init__()
        if type(self.shares) is not ValuationShares:
            raise BridgeValidationError("Explicit ValuationShares required")
        self.shares.__post_init__()
        _text(self.valuation_class_id)
        if self.shares.class_id != self.valuation_class_id:
            raise BridgeValidationError("Declared share/output class mismatch")
        _references(self.unresolved_requirements)
        _validate_declarations(self)


def _validate_declarations(inputs: BridgeInputs) -> None:
    components = {item.component_id: item for item in inputs.components}
    notes = {item.observation_id: item for item in inputs.observations}
    if (len(components) != len(inputs.components) or len(notes) != len(inputs.observations)
            or components.keys() & notes.keys()):
        raise BridgeValidationError("Repeated component/observation ID")
    if len({item.population_id for item in inputs.components}) != len(inputs.components):
        raise BridgeValidationError("Repeated numeric population ID")
    for item in inputs.components:
        refs = set(item.overlap_references + item.alternative_references)
        if item.component_id in refs or not refs <= components.keys() | notes.keys():
            raise BridgeValidationError("Unresolved or self overlap/alternative reference")
        if refs & components.keys() or item.overlaps_forecast:
            raise BridgeValidationError("Declared numeric population/forecast overlap")
    if len(inputs.coverage) != 3 or {item.role for item in inputs.coverage} != set(ComponentRole):
        raise BridgeValidationError("Explicit coverage for all three bridge roles required")
    used_omissions = []
    for declaration in inputs.coverage:
        expected = {item.population_id for item in inputs.components if item.role is declaration.role}
        if set(declaration.population_ids) != expected:
            raise BridgeValidationError("Coverage must name exactly the supplied role operands")
        for ref in declaration.omission_references:
            note = notes.get(ref)
            if note is None or note.disposition != "OMISSION" or note.role is not declaration.role:
                raise BridgeValidationError("Coverage needs a matching explicit omission observation")
            used_omissions.append(ref)
    if (len(set(used_omissions)) != len(used_omissions)
            or set(used_omissions) != {k for k, v in notes.items() if v.disposition == "OMISSION"}):
        raise BridgeValidationError("Every omission decision must bind one coverage declaration")


def _validate_stage_b(stage_b: EnterpriseValueResult) -> None:
    if (type(stage_b) is not EnterpriseValueResult or type(stage_b.years) is not tuple
            or len(stage_b.years) != 5 or type(stage_b.terminal) is not ForecastYearResult):
        raise BridgeValidationError("Complete immutable Stage B result required")
    for year in (*stage_b.years, stage_b.terminal):
        cls = ForecastYearResult if year is stage_b.terminal else DiscountedYearResult
        if type(year) is not cls or type(year.period_index) is not int:
            raise BridgeValidationError("Exact ordered annual/terminal result structure required")
        for field in fields(year):
            if field.name not in ("period_index", "fiscal_year_label"):
                _decimal(getattr(year, field.name))
    for value in (stage_b.terminal_value, stage_b.pv_terminal_value,
                  stage_b.pv_explicit_fcff, stage_b.enterprise_value):
        _decimal(value)
    expected = discount_to_enterprise_value(stage_b.stage_a, stage_b.terminal_assumptions,
                                          convention_version=stage_b.convention_version)
    if stage_b != expected:
        raise BridgeValidationError("Stage B annuals/terminal/totals disagree with recomputation")


@dataclass(frozen=True)
class ComponentContribution:
    component: BridgeComponent
    signed_contribution: Decimal


@dataclass(frozen=True)
class BridgeResult:
    stage_b: EnterpriseValueResult
    inputs: BridgeInputs
    contributions: tuple[ComponentContribution, ...]
    eligible_assets: Decimal
    financing_claims: Decimal
    other_equity_claims: Decimal
    equity_value: Decimal
    valuation_shares: Decimal
    value_per_share: Decimal


def bridge_to_per_share(stage_b: EnterpriseValueResult, inputs: BridgeInputs) -> BridgeResult:
    """Pure arithmetic on supplied declarations; never loads actual candidates."""
    if type(inputs) is not BridgeInputs:
        raise BridgeValidationError("Explicit BridgeInputs required; no automatic selections")
    try:
        with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN)):
            inputs.__post_init__()
            if inputs.unresolved_requirements:
                raise BridgeValidationError("Unresolved required bridge inputs block calculation")
            _validate_stage_b(stage_b)
            period = stage_b.stage_a.anchor.period
            for item in (*inputs.components, inputs.shares):
                as_of = item.observation_date if type(item) is ValuationShares else item.as_of
                if item.company_cik != period.cik or as_of != period.annual_end:
                    raise BridgeValidationError("Company/date mismatch with fiscal-end analytical anchor")
            if any(note.company_cik != period.cik for note in inputs.observations):
                raise BridgeValidationError("Observation company mismatch")
            contributions = tuple(ComponentContribution(
                item, item.amount if item.role is ComponentRole.ELIGIBLE_ASSET else item.amount.copy_negate()
            ) for item in sorted(inputs.components, key=lambda c: c.component_id))
            totals = {role: sum((line.component.amount for line in contributions
                                if line.component.role is role), Decimal(0)) for role in ComponentRole}
            equity = (stage_b.enterprise_value + totals[ComponentRole.ELIGIBLE_ASSET]
                      - totals[ComponentRole.FINANCING_CLAIM] - totals[ComponentRole.OTHER_EQUITY_CLAIM])
            per_share = equity / inputs.shares.shares
            if not all(value.is_finite() for value in (*totals.values(), equity, per_share)):
                raise BridgeValidationError("Nonfinite bridge result")
            return BridgeResult(stage_b, inputs, contributions, totals[ComponentRole.ELIGIBLE_ASSET],
                                totals[ComponentRole.FINANCING_CLAIM], totals[ComponentRole.OTHER_EQUITY_CLAIM],
                                equity, inputs.shares.shares, per_share)
    except BridgeValidationError:
        raise
    except (ValueError, TypeError, AttributeError, DecimalException) as exc:
        raise BridgeValidationError("Invalid declared inputs, Stage B handoff or Decimal arithmetic") from exc


def _encode(value):
    """Only the fixed immutable bridge models; source/decision strings stay declarations."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if type(value) is date:
        return value.isoformat()
    if type(value) is tuple:
        return [_encode(item) for item in value]
    if type(value) in (BridgeComponent, BridgeObservation, PopulationCoverage,
                       ValuationShares, ManualIdentity, ComponentContribution):
        return {field.name: _encode(getattr(value, field.name)) for field in fields(value)}
    return value


def bridge_to_dict(result: BridgeResult) -> dict[str, object]:
    if type(result) is not BridgeResult:
        raise BridgeValidationError("BridgeResult required")
    inputs = result.inputs
    return {
        "schema": RESULT_SCHEMA, "convention_version": inputs.convention_version,
        "numeric_policy": {"precision": 50, "rounding": "ROUND_HALF_EVEN",
                           "amount_unit": "USD", "share_unit": "shares", "intermediate_quantization": False},
        "semantic_input_review": "NOT_ASSESSED_BY_CALCULATOR",
        "limitations": ["Source/decision/review references are declarations, not authenticated approvals.",
                        "Declared coverage/class/overlap checks cannot prove completeness or hidden economic overlap.",
                        "No automatic award valuation, dilution, proceeds or actual META selections."],
        "stage_b": enterprise_value_to_dict(result.stage_b),
        "inputs": {"input_basis": inputs.input_basis,
                   "valuation_class_id": inputs.valuation_class_id,
                   "convention_version": inputs.convention_version,
                   "components": [_encode(c) for c in sorted(inputs.components, key=lambda c: c.component_id)],
                   "observations": [_encode(n) for n in sorted(inputs.observations, key=lambda n: n.observation_id)],
                   "coverage": [_encode(c) for c in sorted(inputs.coverage, key=lambda c: c.role.value)],
                   "shares": _encode(inputs.shares),
                   "unresolved_requirements": _encode(inputs.unresolved_requirements)},
        "contributions": [_encode(line) for line in result.contributions],
        **{name: str(getattr(result, name)) for name in (
            "eligible_assets", "financing_claims", "other_equity_claims", "equity_value",
            "valuation_shares", "value_per_share")},
    }


def serialize_bridge(result: BridgeResult) -> str:
    return json.dumps(bridge_to_dict(result), sort_keys=True, separators=(",", ":"))
