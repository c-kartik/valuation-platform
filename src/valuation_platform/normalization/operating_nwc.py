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
    if filing_result not in balance_sheets.annual:
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
