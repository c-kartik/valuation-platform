"""Model and evaluate annual Operating NWC evidence completeness."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from valuation_platform.sec.submissions import SECFiling

from .concepts import FinancialMetric
from .models import (
    AmbiguousHistoricalMetric,
    AnnualBalanceSheetFilingResult,
    DerivedBalanceSheetValue,
    MissingHistoricalMetric,
    NormalizedAnnualBalanceSheets,
    NormalizedBalanceSheetValue,
)


_META_CIK = 1326801
_GOOGL_CIK = 1652044
_MSFT_CIK = 789019
_AAPL_CIK = 320193
_COST_CIK = 909832


class OperatingNWCCompletenessError(ValueError):
    """Raised when an Operating NWC completeness input is invalid."""


class OperatingNWCReadinessError(ValueError):
    """Raised when an Operating NWC valuation-readiness input is invalid."""


class OperatingNWCComponentClassification(str, Enum):
    """Methodological treatment of one potential Operating NWC component."""

    OPERATING_ASSET = "operating_asset"
    OPERATING_LIABILITY = "operating_liability"
    EXCLUDED = "excluded"
    NOT_APPLICABLE = "not_applicable"
    METHODOLOGY_UNRESOLVED = "methodology_unresolved"


class OperatingNWCComponent(str, Enum):
    """Stable identities for researched Operating NWC components."""

    OPERATING_RECEIVABLES = "operating_receivables"
    VENDOR_NONTRADE_RECEIVABLES = "vendor_nontrade_receivables"
    INVENTORY = "inventory"
    TRADE_ACCOUNTS_PAYABLE = "trade_accounts_payable"
    CUSTOMER_CONTRACT_LIABILITIES = "customer_contract_liabilities"
    EMPLOYEE_RELATED_LIABILITIES = "employee_related_liabilities"
    ACCRUED_REVENUE_SHARE_LIABILITY = "accrued_revenue_share_liability"
    MEMBER_REWARDS_LIABILITY = "member_rewards_liability"
    ACCRUED_CUSTOMER_LIABILITIES = "accrued_customer_liabilities"
    COMPONENT_PURCHASE_RECEIVABLES = "component_purchase_receivables"
    DISTRIBUTION_AND_MARKETING_LIABILITY = (
        "distribution_and_marketing_liability"
    )
    OTHER_CURRENT_ASSETS = "other_current_assets"
    OTHER_ACCRUED_LIABILITIES = "other_accrued_liabilities"
    RESIDUAL_CURRENT_LIABILITIES = "residual_current_liabilities"
    ACCRUED_PP_AND_E_PURCHASES = "accrued_pp_and_e_purchases"
    OPERATING_LEASE_LIABILITIES = "operating_lease_liabilities"


class OperatingNWCPerimeterSide(str, Enum):
    """Economic side assigned to a component by a valuation perimeter."""

    ASSET = "asset"
    LIABILITY = "liability"


class OperatingNWCPerimeterTreatment(str, Enum):
    """Calculation-readiness treatment of one researched component."""

    REQUIRED = "required"
    METHODOLOGY_BLOCKER = "methodology_blocker"
    OUT_OF_PERIMETER = "out_of_perimeter"


_NORMALIZED_METRICS = {
    OperatingNWCComponent.OPERATING_RECEIVABLES: (
        FinancialMetric.OPERATING_RECEIVABLES
    ),
    OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES: (
        FinancialMetric.VENDOR_NONTRADE_RECEIVABLES
    ),
    OperatingNWCComponent.INVENTORY: FinancialMetric.INVENTORY,
    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE: (
        FinancialMetric.TRADE_ACCOUNTS_PAYABLE
    ),
    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES: (
        FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES
    ),
    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES: (
        FinancialMetric.EMPLOYEE_RELATED_LIABILITIES
    ),
    OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY: (
        FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY
    ),
    OperatingNWCComponent.ACCRUED_CUSTOMER_LIABILITIES: (
        FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES
    ),
    OperatingNWCComponent.MEMBER_REWARDS_LIABILITY: (
        FinancialMetric.MEMBER_REWARDS_LIABILITY
    ),
}


@dataclass(frozen=True)
class OperatingNWCComponentPolicy:
    """One issuer-specific component classification and normalized source."""

    component: OperatingNWCComponent
    classification: OperatingNWCComponentClassification
    metric: FinancialMetric | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.component, OperatingNWCComponent):
            raise OperatingNWCCompletenessError("O-NWC component is invalid")
        if not isinstance(
            self.classification,
            OperatingNWCComponentClassification,
        ):
            raise OperatingNWCCompletenessError(
                "O-NWC component classification is invalid"
            )
        required = self.classification in (
            OperatingNWCComponentClassification.OPERATING_ASSET,
            OperatingNWCComponentClassification.OPERATING_LIABILITY,
        )
        if required:
            expected_metric = _NORMALIZED_METRICS.get(self.component)
            if self.metric is not expected_metric:
                raise OperatingNWCCompletenessError(
                    "Required O-NWC component must identify its matching "
                    "normalized metric"
                )
        elif self.metric is not None:
            raise OperatingNWCCompletenessError(
                "Non-required O-NWC component cannot request a normalized metric"
            )


@dataclass(frozen=True)
class OperatingNWCPolicy:
    """Ordered Operating NWC component requirements for one issuer CIK."""

    policy_id: str
    company_cik: int
    components: tuple[OperatingNWCComponentPolicy, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id:
            raise OperatingNWCCompletenessError("O-NWC policy ID must not be empty")
        if (
            not isinstance(self.company_cik, int)
            or isinstance(self.company_cik, bool)
            or self.company_cik < 0
        ):
            raise OperatingNWCCompletenessError(
                "O-NWC policy CIK must be a nonnegative integer"
            )
        if not isinstance(self.components, tuple) or not self.components:
            raise OperatingNWCCompletenessError(
                "O-NWC policy must contain component classifications"
            )
        if not all(
            isinstance(component, OperatingNWCComponentPolicy)
            for component in self.components
        ):
            raise OperatingNWCCompletenessError(
                "O-NWC policy contains an invalid component"
            )
        identities = tuple(component.component for component in self.components)
        if len(set(identities)) != len(identities):
            raise OperatingNWCCompletenessError(
                "O-NWC policy contains duplicate components"
            )


@dataclass(frozen=True)
class ResolvedOperatingNWCComponent:
    """One required component with a resolved normalized balance."""

    policy: OperatingNWCComponentPolicy
    result: NormalizedBalanceSheetValue | DerivedBalanceSheetValue


@dataclass(frozen=True)
class MissingOperatingNWCComponent:
    """One required component whose SEC evidence is missing or ineligible."""

    policy: OperatingNWCComponentPolicy
    result: MissingHistoricalMetric


@dataclass(frozen=True)
class AmbiguousOperatingNWCComponent:
    """One required component with unresolved competing evidence."""

    policy: OperatingNWCComponentPolicy
    result: AmbiguousHistoricalMetric


@dataclass(frozen=True)
class OperatingNWCCompletenessResult:
    """Evidence status for one issuer-period without an O-NWC amount."""

    policy_id: str
    company_cik: int
    filing: SECFiling
    resolved_required_components: tuple[ResolvedOperatingNWCComponent, ...]
    missing_required_components: tuple[MissingOperatingNWCComponent, ...]
    ambiguous_required_components: tuple[AmbiguousOperatingNWCComponent, ...]
    methodology_unresolved_components: tuple[OperatingNWCComponentPolicy, ...]
    excluded_components: tuple[OperatingNWCComponentPolicy, ...]
    not_applicable_components: tuple[OperatingNWCComponentPolicy, ...]

    @property
    def is_complete(self) -> bool:
        """Return whether all required evidence and methodology are complete."""
        return not (
            self.missing_required_components
            or self.ambiguous_required_components
            or self.methodology_unresolved_components
        )


@dataclass(frozen=True)
class OperatingNWCPerimeterComponentPolicy:
    """One ordered component in a versioned valuation perimeter."""

    component: OperatingNWCComponent
    side: OperatingNWCPerimeterSide
    treatment: OperatingNWCPerimeterTreatment
    mandatory: bool
    metric: FinancialMetric | None
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(self.component, OperatingNWCComponent):
            raise OperatingNWCReadinessError("O-NWC perimeter component is invalid")
        if not isinstance(self.side, OperatingNWCPerimeterSide):
            raise OperatingNWCReadinessError("O-NWC perimeter side is invalid")
        if not isinstance(self.treatment, OperatingNWCPerimeterTreatment):
            raise OperatingNWCReadinessError("O-NWC perimeter treatment is invalid")
        if not isinstance(self.mandatory, bool):
            raise OperatingNWCReadinessError(
                "O-NWC perimeter mandatory setting must be Boolean"
            )
        if not isinstance(self.rationale, str) or not self.rationale:
            raise OperatingNWCReadinessError(
                "O-NWC perimeter component rationale must not be empty"
            )
        if self.treatment is OperatingNWCPerimeterTreatment.REQUIRED:
            if not self.mandatory or self.metric is not _NORMALIZED_METRICS.get(
                self.component
            ):
                raise OperatingNWCReadinessError(
                    "Required perimeter component must be mandatory and identify "
                    "its matching normalized metric"
                )
        elif self.treatment is OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER:
            if not self.mandatory or self.metric is not None:
                raise OperatingNWCReadinessError(
                    "Methodology blocker must be mandatory without a normalized metric"
                )
        elif self.mandatory or self.metric is not None:
            raise OperatingNWCReadinessError(
                "Non-mandatory perimeter component cannot request a normalized metric"
            )


@dataclass(frozen=True)
class OperatingNWCValuationPolicy:
    """Versioned issuer-specific component perimeter for future O-NWC arithmetic."""

    policy_id: str
    version: str
    company_cik: int
    components: tuple[OperatingNWCPerimeterComponentPolicy, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id:
            raise OperatingNWCReadinessError(
                "O-NWC valuation policy ID must not be empty"
            )
        if not isinstance(self.version, str) or not self.version:
            raise OperatingNWCReadinessError(
                "O-NWC valuation policy version must not be empty"
            )
        if (
            not isinstance(self.company_cik, int)
            or isinstance(self.company_cik, bool)
            or self.company_cik < 0
        ):
            raise OperatingNWCReadinessError(
                "O-NWC valuation policy CIK must be a nonnegative integer"
            )
        if not isinstance(self.components, tuple) or not self.components:
            raise OperatingNWCReadinessError(
                "O-NWC valuation policy must contain component definitions"
            )
        if not all(
            isinstance(component, OperatingNWCPerimeterComponentPolicy)
            for component in self.components
        ):
            raise OperatingNWCReadinessError(
                "O-NWC valuation policy contains an invalid component"
            )
        identities = tuple(component.component for component in self.components)
        if len(set(identities)) != len(identities):
            raise OperatingNWCReadinessError(
                "O-NWC valuation policy contains duplicate components"
            )
        metrics = tuple(
            component.metric
            for component in self.components
            if component.metric is not None
        )
        if len(set(metrics)) != len(metrics):
            raise OperatingNWCReadinessError(
                "O-NWC valuation policy contains duplicate configured metrics"
            )


@dataclass(frozen=True)
class ResolvedOperatingNWCReadinessComponent:
    """One mandatory perimeter component with resolved evidence."""

    policy: OperatingNWCPerimeterComponentPolicy
    result: NormalizedBalanceSheetValue | DerivedBalanceSheetValue


@dataclass(frozen=True)
class MissingOperatingNWCReadinessComponent:
    """One mandatory perimeter component with typed missing evidence."""

    policy: OperatingNWCPerimeterComponentPolicy
    result: MissingHistoricalMetric


@dataclass(frozen=True)
class AmbiguousOperatingNWCReadinessComponent:
    """One mandatory perimeter component with typed ambiguous evidence."""

    policy: OperatingNWCPerimeterComponentPolicy
    result: AmbiguousHistoricalMetric


@dataclass(frozen=True)
class OperatingNWCReadinessResult:
    """Valuation-perimeter readiness for one filing without O-NWC arithmetic."""

    policy_id: str
    policy_version: str
    company_cik: int
    filing: SECFiling
    resolved_mandatory_components: tuple[
        ResolvedOperatingNWCReadinessComponent, ...
    ]
    missing_mandatory_components: tuple[MissingOperatingNWCReadinessComponent, ...]
    ambiguous_mandatory_components: tuple[
        AmbiguousOperatingNWCReadinessComponent, ...
    ]
    methodology_blockers: tuple[OperatingNWCPerimeterComponentPolicy, ...]
    configured_non_mandatory_components: tuple[
        OperatingNWCPerimeterComponentPolicy, ...
    ]

    @property
    def is_ready(self) -> bool:
        """Return whether every mandatory perimeter component is usable."""
        return not (
            self.missing_mandatory_components
            or self.ambiguous_mandatory_components
            or self.methodology_blockers
        )


def _component(
    component: OperatingNWCComponent,
    classification: OperatingNWCComponentClassification,
) -> OperatingNWCComponentPolicy:
    metric = _NORMALIZED_METRICS.get(component)
    if classification not in (
        OperatingNWCComponentClassification.OPERATING_ASSET,
        OperatingNWCComponentClassification.OPERATING_LIABILITY,
    ):
        metric = None
    return OperatingNWCComponentPolicy(component, classification, metric)


_ASSET = OperatingNWCComponentClassification.OPERATING_ASSET
_LIABILITY = OperatingNWCComponentClassification.OPERATING_LIABILITY
_EXCLUDED = OperatingNWCComponentClassification.EXCLUDED
_NOT_APPLICABLE = OperatingNWCComponentClassification.NOT_APPLICABLE
_UNRESOLVED = OperatingNWCComponentClassification.METHODOLOGY_UNRESOLVED


META_OPERATING_NWC_POLICY = OperatingNWCPolicy(
    policy_id="meta_initial_operating_nwc",
    company_cik=_META_CIK,
    components=(
        _component(OperatingNWCComponent.OPERATING_RECEIVABLES, _ASSET),
        _component(OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, _NOT_APPLICABLE),
        _component(OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, _LIABILITY),
        _component(OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, _LIABILITY),
        _component(OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, _LIABILITY),
        _component(
            OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY,
            _NOT_APPLICABLE,
        ),
        _component(OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, _NOT_APPLICABLE),
        _component(OperatingNWCComponent.OTHER_ACCRUED_LIABILITIES, _UNRESOLVED),
        _component(OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES, _EXCLUDED),
        _component(OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, _EXCLUDED),
    ),
)


GOOGL_OPERATING_NWC_POLICY = OperatingNWCPolicy(
    policy_id="googl_initial_operating_nwc",
    company_cik=_GOOGL_CIK,
    components=(
        _component(OperatingNWCComponent.OPERATING_RECEIVABLES, _ASSET),
        _component(OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, _NOT_APPLICABLE),
        _component(OperatingNWCComponent.INVENTORY, _ASSET),
        _component(OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, _UNRESOLVED),
        _component(OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, _LIABILITY),
        _component(OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, _LIABILITY),
        _component(OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY, _LIABILITY),
        _component(OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, _NOT_APPLICABLE),
        _component(OperatingNWCComponent.ACCRUED_CUSTOMER_LIABILITIES, _LIABILITY),
        _component(OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, _UNRESOLVED),
        _component(OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES, _EXCLUDED),
        _component(OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, _EXCLUDED),
    ),
)


MSFT_OPERATING_NWC_POLICY = OperatingNWCPolicy(
    policy_id="msft_initial_operating_nwc",
    company_cik=_MSFT_CIK,
    components=(
        _component(OperatingNWCComponent.OPERATING_RECEIVABLES, _ASSET),
        _component(OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, _NOT_APPLICABLE),
        _component(OperatingNWCComponent.INVENTORY, _ASSET),
        _component(OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, _UNRESOLVED),
        _component(OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, _LIABILITY),
        _component(OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, _LIABILITY),
        _component(
            OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY,
            _NOT_APPLICABLE,
        ),
        _component(OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, _NOT_APPLICABLE),
        _component(OperatingNWCComponent.COMPONENT_PURCHASE_RECEIVABLES, _EXCLUDED),
        _component(OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, _UNRESOLVED),
        _component(OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES, _EXCLUDED),
        _component(OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, _EXCLUDED),
    ),
)


AAPL_OPERATING_NWC_POLICY = OperatingNWCPolicy(
    policy_id="aapl_initial_operating_nwc",
    company_cik=_AAPL_CIK,
    components=(
        _component(OperatingNWCComponent.OPERATING_RECEIVABLES, _ASSET),
        _component(OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, _ASSET),
        _component(OperatingNWCComponent.INVENTORY, _ASSET),
        _component(OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, _LIABILITY),
        _component(OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, _LIABILITY),
        _component(OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, _UNRESOLVED),
        _component(
            OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY,
            _NOT_APPLICABLE,
        ),
        _component(OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, _NOT_APPLICABLE),
        _component(
            OperatingNWCComponent.DISTRIBUTION_AND_MARKETING_LIABILITY,
            _UNRESOLVED,
        ),
        _component(OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, _UNRESOLVED),
        _component(OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, _EXCLUDED),
    ),
)


COST_OPERATING_NWC_POLICY = OperatingNWCPolicy(
    policy_id="cost_initial_operating_nwc",
    company_cik=_COST_CIK,
    components=(
        _component(OperatingNWCComponent.OPERATING_RECEIVABLES, _ASSET),
        _component(OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, _NOT_APPLICABLE),
        _component(OperatingNWCComponent.INVENTORY, _ASSET),
        _component(OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, _LIABILITY),
        _component(OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, _LIABILITY),
        _component(OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, _LIABILITY),
        _component(
            OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY,
            _NOT_APPLICABLE,
        ),
        _component(OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, _LIABILITY),
        _component(OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, _UNRESOLVED),
        _component(OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, _EXCLUDED),
    ),
)


OPERATING_NWC_POLICIES: tuple[OperatingNWCPolicy, ...] = (
    META_OPERATING_NWC_POLICY,
    GOOGL_OPERATING_NWC_POLICY,
    MSFT_OPERATING_NWC_POLICY,
    AAPL_OPERATING_NWC_POLICY,
    COST_OPERATING_NWC_POLICY,
)


_PERIMETER_ASSET = OperatingNWCPerimeterSide.ASSET
_PERIMETER_LIABILITY = OperatingNWCPerimeterSide.LIABILITY
_REQUIRED = OperatingNWCPerimeterTreatment.REQUIRED
_BLOCKER = OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER
_OUTSIDE = OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER


def _perimeter_component(
    component: OperatingNWCComponent,
    side: OperatingNWCPerimeterSide,
    treatment: OperatingNWCPerimeterTreatment,
    rationale: str,
) -> OperatingNWCPerimeterComponentPolicy:
    mandatory = treatment in (_REQUIRED, _BLOCKER)
    metric = _NORMALIZED_METRICS.get(component) if treatment is _REQUIRED else None
    return OperatingNWCPerimeterComponentPolicy(
        component=component,
        side=side,
        treatment=treatment,
        mandatory=mandatory,
        metric=metric,
        rationale=rationale,
    )


META_OPERATING_NWC_VALUATION_POLICY = OperatingNWCValuationPolicy(
    policy_id="meta_operating_nwc_valuation",
    version="1",
    company_cik=_META_CIK,
    components=(
        _perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Core operating collection balance",
        ),
        _perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Adjusted supplier payable excludes evidenced PP&E obligations",
        ),
        _perimeter_component(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Customer financing within the operating cycle",
        ),
        _perimeter_component(
            OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Recurring employee-related operating accrual",
        ),
        _perimeter_component(
            OperatingNWCComponent.OTHER_ACCRUED_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Mixed residual caption remains a reconstruction limitation",
        ),
        _perimeter_component(
            OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Investing obligation already reflected in adjusted trade AP",
        ),
        _perimeter_component(
            OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Integrated lease methodology remains deferred",
        ),
    ),
)


GOOGL_OPERATING_NWC_VALUATION_POLICY = OperatingNWCValuationPolicy(
    policy_id="googl_operating_nwc_valuation",
    version="1",
    company_cik=_GOOGL_CIK,
    components=(
        _perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Core operating collection balance",
        ),
        _perimeter_component(
            OperatingNWCComponent.INVENTORY,
            _PERIMETER_ASSET,
            _BLOCKER,
            "Materiality and stable-perimeter treatment remain unresolved",
        ),
        _perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            _PERIMETER_LIABILITY,
            _BLOCKER,
            "Supplier-payable methodology remains unresolved",
        ),
        _perimeter_component(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Customer financing within the operating cycle",
        ),
        _perimeter_component(
            OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Recurring employee-related operating accrual",
        ),
        _perimeter_component(
            OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Business-model-specific distribution obligation",
        ),
        _perimeter_component(
            OperatingNWCComponent.ACCRUED_CUSTOMER_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Distinct current customer obligation",
        ),
        _perimeter_component(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Mixed residual caption remains a reconstruction limitation",
        ),
        _perimeter_component(
            OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Investing obligations are outside operating working capital",
        ),
        _perimeter_component(
            OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Integrated lease methodology remains deferred",
        ),
    ),
)


MSFT_OPERATING_NWC_VALUATION_POLICY = OperatingNWCValuationPolicy(
    policy_id="msft_operating_nwc_valuation",
    version="1",
    company_cik=_MSFT_CIK,
    components=(
        _perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Core operating collection balance",
        ),
        _perimeter_component(
            OperatingNWCComponent.INVENTORY,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Consistently disclosed operating inventory",
        ),
        _perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            _PERIMETER_LIABILITY,
            _BLOCKER,
            "Supplier-payable methodology remains unresolved",
        ),
        _perimeter_component(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Customer financing within the operating cycle",
        ),
        _perimeter_component(
            OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Recurring employee-related operating accrual",
        ),
        _perimeter_component(
            OperatingNWCComponent.COMPONENT_PURCHASE_RECEIVABLES,
            _PERIMETER_ASSET,
            _OUTSIDE,
            "Strategic component-purchase balance is not customer receivables",
        ),
        _perimeter_component(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Mixed residual caption remains a reconstruction limitation",
        ),
        _perimeter_component(
            OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Investing obligations are outside operating working capital",
        ),
        _perimeter_component(
            OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Integrated lease methodology remains deferred",
        ),
    ),
)


AAPL_OPERATING_NWC_VALUATION_POLICY = OperatingNWCValuationPolicy(
    policy_id="aapl_operating_nwc_valuation",
    version="1",
    company_cik=_AAPL_CIK,
    components=(
        _perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Core operating collection balance",
        ),
        _perimeter_component(
            OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Evidence-backed operating supply-chain receivable",
        ),
        _perimeter_component(
            OperatingNWCComponent.INVENTORY,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Core operating inventory",
        ),
        _perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Core supplier financing",
        ),
        _perimeter_component(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Customer financing within the operating cycle",
        ),
        _perimeter_component(
            OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
            _PERIMETER_LIABILITY,
            _BLOCKER,
            "Materiality and evidence methodology remain unresolved",
        ),
        _perimeter_component(
            OperatingNWCComponent.DISTRIBUTION_AND_MARKETING_LIABILITY,
            _PERIMETER_LIABILITY,
            _BLOCKER,
            "Only one selected accession currently has exact evidence",
        ),
        _perimeter_component(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Mixed residual caption remains a reconstruction limitation",
        ),
        _perimeter_component(
            OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Integrated lease methodology remains deferred",
        ),
    ),
)


COST_OPERATING_NWC_VALUATION_POLICY = OperatingNWCValuationPolicy(
    policy_id="cost_operating_nwc_valuation",
    version="1",
    company_cik=_COST_CIK,
    components=(
        _perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Mixed caption is predominantly operating receivables",
        ),
        _perimeter_component(
            OperatingNWCComponent.INVENTORY,
            _PERIMETER_ASSET,
            _REQUIRED,
            "Core retail inventory",
        ),
        _perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Core supplier financing",
        ),
        _perimeter_component(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Evidence-backed deferred customer revenue",
        ),
        _perimeter_component(
            OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Recurring employee-related operating accrual",
        ),
        _perimeter_component(
            OperatingNWCComponent.MEMBER_REWARDS_LIABILITY,
            _PERIMETER_LIABILITY,
            _REQUIRED,
            "Business-model-specific member rewards obligation",
        ),
        _perimeter_component(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Mixed residual caption remains a reconstruction limitation",
        ),
        _perimeter_component(
            OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
            _PERIMETER_LIABILITY,
            _OUTSIDE,
            "Integrated lease methodology remains deferred",
        ),
    ),
)


OPERATING_NWC_VALUATION_POLICIES: tuple[OperatingNWCValuationPolicy, ...] = (
    META_OPERATING_NWC_VALUATION_POLICY,
    GOOGL_OPERATING_NWC_VALUATION_POLICY,
    MSFT_OPERATING_NWC_VALUATION_POLICY,
    AAPL_OPERATING_NWC_VALUATION_POLICY,
    COST_OPERATING_NWC_VALUATION_POLICY,
)


def _validate_operating_nwc_valuation_policy_registry(
    policies: tuple[OperatingNWCValuationPolicy, ...],
) -> None:
    """Reject ambiguous active-policy registrations."""
    company_ciks = tuple(policy.company_cik for policy in policies)
    if len(set(company_ciks)) != len(company_ciks):
        raise OperatingNWCReadinessError(
            "O-NWC valuation policy registry contains duplicate company CIKs"
        )
    identities = tuple((policy.policy_id, policy.version) for policy in policies)
    if len(set(identities)) != len(identities):
        raise OperatingNWCReadinessError(
            "O-NWC valuation policy registry contains duplicate policy ID/version"
        )


_validate_operating_nwc_valuation_policy_registry(OPERATING_NWC_VALUATION_POLICIES)


def operating_nwc_policy_for_cik(company_cik: int) -> OperatingNWCPolicy:
    """Return the researched Operating NWC policy for an exact company CIK."""
    matches = tuple(
        policy for policy in OPERATING_NWC_POLICIES if policy.company_cik == company_cik
    )
    if not matches:
        raise OperatingNWCCompletenessError(
            f"No Operating NWC policy is configured for CIK {company_cik!r}"
        )
    return matches[0]


def operating_nwc_valuation_policy_for_cik(
    company_cik: int,
) -> OperatingNWCValuationPolicy:
    """Return the versioned valuation perimeter for an exact company CIK."""
    _validate_operating_nwc_valuation_policy_registry(
        OPERATING_NWC_VALUATION_POLICIES
    )
    matches = tuple(
        policy
        for policy in OPERATING_NWC_VALUATION_POLICIES
        if policy.company_cik == company_cik
    )
    if not matches:
        raise OperatingNWCReadinessError(
            f"No Operating NWC valuation policy is configured for CIK {company_cik!r}"
        )
    return matches[0]


def evaluate_operating_nwc_completeness(
    balance_sheets: NormalizedAnnualBalanceSheets,
    filing_result: AnnualBalanceSheetFilingResult,
    policy: OperatingNWCPolicy,
) -> OperatingNWCCompletenessResult:
    """Classify one annual filing's evidence without calculating O-NWC."""
    if not isinstance(balance_sheets, NormalizedAnnualBalanceSheets):
        raise OperatingNWCCompletenessError(
            "O-NWC completeness requires normalized annual balance sheets"
        )
    if not isinstance(filing_result, AnnualBalanceSheetFilingResult):
        raise OperatingNWCCompletenessError(
            "O-NWC completeness requires an annual balance-sheet filing result"
        )
    if not isinstance(policy, OperatingNWCPolicy):
        raise OperatingNWCCompletenessError(
            "O-NWC completeness requires an Operating NWC policy"
        )
    if balance_sheets.company.cik != policy.company_cik:
        raise OperatingNWCCompletenessError(
            "Normalized balance-sheet company does not match O-NWC policy company"
        )
    if not any(result is filing_result for result in balance_sheets.annual):
        raise OperatingNWCCompletenessError(
            "Annual balance-sheet filing result does not belong to the supplied "
            "normalized balance sheets"
        )
    by_metric: dict[FinancialMetric, object] = {}
    for result in filing_result.metrics:
        if result.metric in by_metric:
            raise OperatingNWCCompletenessError(
                f"Annual balance-sheet result contains duplicate metric "
                f"{result.metric.value!r}"
            )
        by_metric[result.metric] = result

    resolved: list[ResolvedOperatingNWCComponent] = []
    missing: list[MissingOperatingNWCComponent] = []
    ambiguous: list[AmbiguousOperatingNWCComponent] = []
    unresolved: list[OperatingNWCComponentPolicy] = []
    excluded: list[OperatingNWCComponentPolicy] = []
    not_applicable: list[OperatingNWCComponentPolicy] = []

    for component in policy.components:
        if component.classification is _UNRESOLVED:
            unresolved.append(component)
            continue
        if component.classification is _EXCLUDED:
            excluded.append(component)
            continue
        if component.classification is _NOT_APPLICABLE:
            not_applicable.append(component)
            continue

        assert component.metric is not None
        result = by_metric.get(component.metric)
        if result is None:
            raise OperatingNWCCompletenessError(
                f"Annual balance-sheet result omits required configured metric "
                f"{component.metric.value!r}"
            )
        if isinstance(result, (NormalizedBalanceSheetValue, DerivedBalanceSheetValue)):
            resolved.append(ResolvedOperatingNWCComponent(component, result))
        elif isinstance(result, MissingHistoricalMetric):
            missing.append(MissingOperatingNWCComponent(component, result))
        elif isinstance(result, AmbiguousHistoricalMetric):
            ambiguous.append(AmbiguousOperatingNWCComponent(component, result))
        else:
            raise OperatingNWCCompletenessError(
                f"Required metric {component.metric.value!r} has an invalid result"
            )

    return OperatingNWCCompletenessResult(
        policy_id=policy.policy_id,
        company_cik=policy.company_cik,
        filing=filing_result.filing,
        resolved_required_components=tuple(resolved),
        missing_required_components=tuple(missing),
        ambiguous_required_components=tuple(ambiguous),
        methodology_unresolved_components=tuple(unresolved),
        excluded_components=tuple(excluded),
        not_applicable_components=tuple(not_applicable),
    )


def evaluate_operating_nwc_readiness(
    balance_sheets: NormalizedAnnualBalanceSheets,
    filing_result: AnnualBalanceSheetFilingResult,
    policy: OperatingNWCValuationPolicy,
) -> OperatingNWCReadinessResult:
    """Evaluate a valuation perimeter without calculating Operating NWC."""
    if not isinstance(balance_sheets, NormalizedAnnualBalanceSheets):
        raise OperatingNWCReadinessError(
            "O-NWC readiness requires normalized annual balance sheets"
        )
    if not isinstance(filing_result, AnnualBalanceSheetFilingResult):
        raise OperatingNWCReadinessError(
            "O-NWC readiness requires an annual balance-sheet filing result"
        )
    if not isinstance(policy, OperatingNWCValuationPolicy):
        raise OperatingNWCReadinessError(
            "O-NWC readiness requires an Operating NWC valuation policy"
        )
    if balance_sheets.company.cik != policy.company_cik:
        raise OperatingNWCReadinessError(
            "Normalized balance-sheet company does not match O-NWC valuation policy"
        )
    if not any(result is filing_result for result in balance_sheets.annual):
        raise OperatingNWCReadinessError(
            "Annual balance-sheet filing result does not belong to the supplied "
            "normalized balance sheets"
        )

    by_metric: dict[FinancialMetric, object] = {}
    for result in filing_result.metrics:
        if result.metric in by_metric:
            raise OperatingNWCReadinessError(
                f"Annual balance-sheet result contains duplicate metric "
                f"{result.metric.value!r}"
            )
        by_metric[result.metric] = result

    resolved: list[ResolvedOperatingNWCReadinessComponent] = []
    missing: list[MissingOperatingNWCReadinessComponent] = []
    ambiguous: list[AmbiguousOperatingNWCReadinessComponent] = []
    blockers: list[OperatingNWCPerimeterComponentPolicy] = []
    non_mandatory: list[OperatingNWCPerimeterComponentPolicy] = []

    for component in policy.components:
        if component.treatment is _BLOCKER:
            blockers.append(component)
            continue
        if not component.mandatory:
            non_mandatory.append(component)
            continue

        assert component.metric is not None
        result = by_metric.get(component.metric)
        if result is None:
            raise OperatingNWCReadinessError(
                f"Annual balance-sheet result omits configured perimeter metric "
                f"{component.metric.value!r}"
            )
        if isinstance(result, (NormalizedBalanceSheetValue, DerivedBalanceSheetValue)):
            resolved.append(ResolvedOperatingNWCReadinessComponent(component, result))
        elif isinstance(result, MissingHistoricalMetric):
            missing.append(MissingOperatingNWCReadinessComponent(component, result))
        elif isinstance(result, AmbiguousHistoricalMetric):
            ambiguous.append(
                AmbiguousOperatingNWCReadinessComponent(component, result)
            )
        else:
            raise OperatingNWCReadinessError(
                f"Perimeter metric {component.metric.value!r} has an invalid result"
            )

    return OperatingNWCReadinessResult(
        policy_id=policy.policy_id,
        policy_version=policy.version,
        company_cik=policy.company_cik,
        filing=filing_result.filing,
        resolved_mandatory_components=tuple(resolved),
        missing_mandatory_components=tuple(missing),
        ambiguous_mandatory_components=tuple(ambiguous),
        methodology_blockers=tuple(blockers),
        configured_non_mandatory_components=tuple(non_mandatory),
    )
