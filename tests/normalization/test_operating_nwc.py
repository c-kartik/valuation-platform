from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch

import valuation_platform.normalization.operating_nwc as operating_nwc_module

from valuation_platform.normalization import (
    AAPL_OPERATING_NWC_VALUATION_POLICY,
    AAPL_OPERATING_NWC_POLICY,
    CalculatedOperatingNWC,
    CalculatedOperatingNWCChange,
    COST_OPERATING_NWC_VALUATION_POLICY,
    COST_OPERATING_NWC_POLICY,
    GOOGL_OPERATING_NWC_VALUATION_POLICY,
    GOOGL_OPERATING_NWC_POLICY,
    META_OPERATING_NWC_VALUATION_POLICY,
    META_OPERATING_NWC_VALUATION_POLICY_V1,
    META_OPERATING_NWC_VALUATION_POLICY_V2,
    META_OPERATING_NWC_POLICY,
    MSFT_OPERATING_NWC_VALUATION_POLICY,
    MSFT_OPERATING_NWC_POLICY,
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    AnnualBalanceSheetFilingResult,
    BalanceSheetDerivationOperand,
    EvidenceSourceKind,
    DerivationOperation,
    DerivedBalanceSheetValue,
    FactEvidence,
    FinancialMetric,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedAnnualBalanceSheets,
    NormalizedBalanceSheetValue,
    OperatingNWCCompletenessError,
    OperatingNWCCalculationFormula,
    OperatingNWCChangeError,
    OperatingNWCComponent,
    OperatingNWCComponentContribution,
    OperatingNWCComponentClassification,
    OperatingNWCComponentPolicy,
    OperatingNWCPerimeterComponentPolicy,
    OperatingNWCPerimeterSide,
    OperatingNWCPerimeterTreatment,
    OperatingNWCPolicy,
    OperatingNWCReadinessError,
    OperatingNWCReadinessResult,
    OperatingNWCValuationPolicy,
    calculate_operating_nwc_level,
    calculate_operating_nwc_change,
    calculate_operating_nwc_changes,
    evaluate_operating_nwc_completeness,
    evaluate_operating_nwc_readiness,
    operating_nwc_policy_for_cik,
    operating_nwc_valuation_policy_for_cik,
    operating_nwc_valuation_policy_for_id_and_version,
)
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity


REPORT_DATE = date(2025, 12, 31)
RETRIEVED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)
FILING = SECFiling(
    accession_number="annual",
    form="10-K",
    filing_date=date(2026, 2, 1),
    report_date=REPORT_DATE,
    primary_document="annual.htm",
)


def make_evidence(
    metric: FinancialMetric,
    value: int | float | Decimal = 10,
    *,
    balance_date: date = REPORT_DATE,
    accession_number: str = "annual",
    filing_date: date = date(2026, 2, 1),
) -> FactEvidence:
    return FactEvidence(
        source_kind=EvidenceSourceKind.COMPANY_FACTS,
        source_url="facts-source",
        taxonomy="us-gaap",
        concept=metric.value,
        value=value,
        unit="USD",
        start=None,
        end=balance_date,
        accession_number=accession_number,
        observation_form="10-K",
        observation_filed=filing_date,
        fiscal_year=balance_date.year,
        fiscal_period="FY",
        frame=None,
    )


def make_resolved(
    metric: FinancialMetric,
    value: int | float | Decimal = 10,
    *,
    balance_date: date = REPORT_DATE,
    accession_number: str = "annual",
    filing_date: date = date(2026, 2, 1),
) -> NormalizedBalanceSheetValue:
    return NormalizedBalanceSheetValue(
        metric=metric,
        value=value,
        unit="USD",
        balance_date=balance_date,
        chosen_source=make_evidence(
            metric,
            value,
            balance_date=balance_date,
            accession_number=accession_number,
            filing_date=filing_date,
        ),
        confirming_sources=(),
    )


def make_missing(metric: FinancialMetric) -> MissingHistoricalMetric:
    return MissingHistoricalMetric(
        metric=metric,
        reason=MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        examined_concepts=(),
    )


def make_ambiguous(metric: FinancialMetric) -> AmbiguousHistoricalMetric:
    return AmbiguousHistoricalMetric(
        metric=metric,
        reason=AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
        candidates=(make_evidence(metric), make_evidence(metric, 11)),
    )


def required(
    component: OperatingNWCComponent,
    classification: OperatingNWCComponentClassification,
    metric: FinancialMetric,
) -> OperatingNWCComponentPolicy:
    return OperatingNWCComponentPolicy(component, classification, metric)


def classified(
    component: OperatingNWCComponent,
    classification: OperatingNWCComponentClassification,
) -> OperatingNWCComponentPolicy:
    return OperatingNWCComponentPolicy(component, classification)


def make_balance_sheets(
    filing_result: AnnualBalanceSheetFilingResult,
    company_cik: int,
) -> NormalizedAnnualBalanceSheets:
    company = SECCompanyIdentity(
        ticker="TEST",
        cik=company_cik,
        cik_padded=f"{company_cik:010d}",
        company_name="Test Company",
        source_url="ticker-source",
        retrieved_at=RETRIEVED_AT,
    )
    return NormalizedAnnualBalanceSheets(
        company=company,
        company_facts_source_url="facts-source",
        company_facts_retrieved_at=RETRIEVED_AT,
        annual=(filing_result,),
    )


def make_balance_sheet_series(
    filing_results: tuple[AnnualBalanceSheetFilingResult, ...],
    company_cik: int,
) -> NormalizedAnnualBalanceSheets:
    first = make_balance_sheets(filing_results[0], company_cik)
    return NormalizedAnnualBalanceSheets(
        company=first.company,
        company_facts_source_url=first.company_facts_source_url,
        company_facts_retrieved_at=first.company_facts_retrieved_at,
        annual=filing_results,
    )


def evaluate(
    filing_result: AnnualBalanceSheetFilingResult,
    policy: OperatingNWCPolicy,
    *,
    company_cik: int | None = None,
):
    balance_sheets = make_balance_sheets(
        filing_result,
        policy.company_cik if company_cik is None else company_cik,
    )
    return evaluate_operating_nwc_completeness(
        balance_sheets,
        filing_result,
        policy,
    )


def perimeter_component(
    component: OperatingNWCComponent,
    side: OperatingNWCPerimeterSide,
    treatment: OperatingNWCPerimeterTreatment,
    metric: FinancialMetric | None = None,
) -> OperatingNWCPerimeterComponentPolicy:
    return OperatingNWCPerimeterComponentPolicy(
        component=component,
        side=side,
        treatment=treatment,
        mandatory=treatment in (
            OperatingNWCPerimeterTreatment.REQUIRED,
            OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER,
        ),
        metric=metric,
        rationale="Synthetic test policy",
    )


def evaluate_readiness(
    filing_result: AnnualBalanceSheetFilingResult,
    policy: OperatingNWCValuationPolicy,
    *,
    company_cik: int | None = None,
):
    balance_sheets = make_balance_sheets(
        filing_result,
        policy.company_cik if company_cik is None else company_cik,
    )
    return evaluate_operating_nwc_readiness(
        balance_sheets,
        filing_result,
        policy,
    )


class OperatingNWCCompletenessTests(TestCase):
    def test_meta_policy_accepts_derived_adjusted_trade_payables(self) -> None:
        metrics = tuple(
            (
                DerivedBalanceSheetValue(
                    metric=component.metric,
                    value=10,
                    unit="USD",
                    balance_date=REPORT_DATE,
                    policy_id="meta_adjusted_trade_accounts_payable_v1",
                    operation=DerivationOperation.SUBTRACT,
                    operands=(),
                    steps=(),
                )
                if component.metric is FinancialMetric.TRADE_ACCOUNTS_PAYABLE
                else make_resolved(component.metric)
            )
            for component in META_OPERATING_NWC_POLICY.components
            if component.metric is not None
        )
        result = evaluate(
            AnnualBalanceSheetFilingResult(FILING, metrics),
            META_OPERATING_NWC_POLICY,
        )

        trade_payables = next(
            item
            for item in result.resolved_required_components
            if item.policy.component is OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE
        )
        self.assertIsInstance(trade_payables.result, DerivedBalanceSheetValue)
        self.assertFalse(result.is_complete)
        self.assertTrue(result.methodology_unresolved_components)

    def test_resolved_required_component_preserves_explicit_zero(self) -> None:
        component = required(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCComponentClassification.OPERATING_ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        policy = OperatingNWCPolicy("test", 1, (component,))
        filing = AnnualBalanceSheetFilingResult(
            FILING,
            (make_resolved(FinancialMetric.OPERATING_RECEIVABLES, 0),),
        )

        result = evaluate(filing, policy)

        self.assertTrue(result.is_complete)
        self.assertEqual(len(result.resolved_required_components), 1)
        self.assertEqual(result.resolved_required_components[0].result.value, 0)
        self.assertEqual(result.missing_required_components, ())

    def test_missing_and_ambiguous_required_components_block_completeness(self) -> None:
        receivables = required(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCComponentClassification.OPERATING_ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        payables = required(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            OperatingNWCComponentClassification.OPERATING_LIABILITY,
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )
        policy = OperatingNWCPolicy("test", 1, (receivables, payables))
        filing = AnnualBalanceSheetFilingResult(
            FILING,
            (
                make_missing(FinancialMetric.OPERATING_RECEIVABLES),
                make_ambiguous(FinancialMetric.TRADE_ACCOUNTS_PAYABLE),
            ),
        )

        result = evaluate(filing, policy)

        self.assertFalse(result.is_complete)
        self.assertEqual(
            tuple(item.policy.component for item in result.missing_required_components),
            (OperatingNWCComponent.OPERATING_RECEIVABLES,),
        )
        self.assertEqual(
            tuple(
                item.policy.component for item in result.ambiguous_required_components
            ),
            (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,),
        )
        self.assertIsInstance(
            result.missing_required_components[0].result,
            MissingHistoricalMetric,
        )
        self.assertIsInstance(
            result.ambiguous_required_components[0].result,
            AmbiguousHistoricalMetric,
        )

    def test_policy_only_classifications_are_grouped_without_zero(self) -> None:
        unresolved = classified(
            OperatingNWCComponent.OTHER_ACCRUED_LIABILITIES,
            OperatingNWCComponentClassification.METHODOLOGY_UNRESOLVED,
        )
        excluded = classified(
            OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
            OperatingNWCComponentClassification.EXCLUDED,
        )
        not_applicable = classified(
            OperatingNWCComponent.MEMBER_REWARDS_LIABILITY,
            OperatingNWCComponentClassification.NOT_APPLICABLE,
        )
        policy = OperatingNWCPolicy(
            "test",
            1,
            (unresolved, excluded, not_applicable),
        )

        result = evaluate(
            AnnualBalanceSheetFilingResult(FILING, ()),
            policy,
        )

        self.assertFalse(result.is_complete)
        self.assertEqual(result.methodology_unresolved_components, (unresolved,))
        self.assertEqual(result.excluded_components, (excluded,))
        self.assertEqual(result.not_applicable_components, (not_applicable,))
        self.assertFalse(hasattr(result, "value"))
        self.assertFalse(hasattr(result, "operating_nwc"))

    def test_multiple_simultaneous_blockers_preserve_policy_order(self) -> None:
        receivables = required(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCComponentClassification.OPERATING_ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        inventory = required(
            OperatingNWCComponent.INVENTORY,
            OperatingNWCComponentClassification.OPERATING_ASSET,
            FinancialMetric.INVENTORY,
        )
        payables = required(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            OperatingNWCComponentClassification.OPERATING_LIABILITY,
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )
        residual = classified(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            OperatingNWCComponentClassification.METHODOLOGY_UNRESOLVED,
        )
        policy = OperatingNWCPolicy(
            "test",
            1,
            (receivables, inventory, payables, residual),
        )
        metrics = (
            make_ambiguous(FinancialMetric.TRADE_ACCOUNTS_PAYABLE),
            make_missing(FinancialMetric.INVENTORY),
            make_resolved(FinancialMetric.OPERATING_RECEIVABLES),
        )

        forward = evaluate(
            AnnualBalanceSheetFilingResult(FILING, metrics),
            policy,
        )
        reverse = evaluate(
            AnnualBalanceSheetFilingResult(FILING, tuple(reversed(metrics))),
            policy,
        )

        self.assertEqual(forward, reverse)
        self.assertEqual(
            tuple(
                item.policy.component
                for item in forward.resolved_required_components
            ),
            (OperatingNWCComponent.OPERATING_RECEIVABLES,),
        )
        self.assertEqual(
            tuple(
                item.policy.component
                for item in forward.missing_required_components
            ),
            (OperatingNWCComponent.INVENTORY,),
        )
        self.assertEqual(
            tuple(
                item.policy.component
                for item in forward.ambiguous_required_components
            ),
            (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,),
        )
        self.assertEqual(forward.methodology_unresolved_components, (residual,))

    def test_cik_specific_policies_preserve_researched_differences(self) -> None:
        apple = operating_nwc_policy_for_cik(320193)
        cost = operating_nwc_policy_for_cik(909832)

        apple_vendor = next(
            item
            for item in apple.components
            if item.component
            is OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES
        )
        cost_vendor = next(
            item
            for item in cost.components
            if item.component
            is OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES
        )
        cost_rewards = next(
            item
            for item in cost.components
            if item.component is OperatingNWCComponent.MEMBER_REWARDS_LIABILITY
        )

        self.assertIs(
            apple_vendor.classification,
            OperatingNWCComponentClassification.OPERATING_ASSET,
        )
        self.assertIs(
            cost_vendor.classification,
            OperatingNWCComponentClassification.NOT_APPLICABLE,
        )
        self.assertIs(
            cost_rewards.classification,
            OperatingNWCComponentClassification.OPERATING_LIABILITY,
        )

    def test_company_policy_cik_mismatch_is_rejected(self) -> None:
        filing = AnnualBalanceSheetFilingResult(
            FILING,
            (make_resolved(FinancialMetric.OPERATING_RECEIVABLES),),
        )
        apple_balance_sheets = make_balance_sheets(filing, 320193)

        with self.assertRaisesRegex(
            OperatingNWCCompletenessError,
            "company does not match O-NWC policy company",
        ):
            evaluate_operating_nwc_completeness(
                apple_balance_sheets,
                filing,
                META_OPERATING_NWC_POLICY,
            )

    def test_filing_result_must_belong_to_balance_sheet_container(self) -> None:
        component = required(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCComponentClassification.OPERATING_ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        policy = OperatingNWCPolicy("identity-test", 1326801, (component,))
        contained = AnnualBalanceSheetFilingResult(
            FILING,
            (make_resolved(FinancialMetric.OPERATING_RECEIVABLES),),
        )
        balance_sheets = make_balance_sheets(contained, 1326801)

        accepted = evaluate_operating_nwc_completeness(
            balance_sheets,
            contained,
            policy,
        )
        self.assertTrue(accepted.is_complete)

        external_result = replace(contained)
        self.assertEqual(external_result, contained)
        self.assertIsNot(external_result, contained)

        with self.assertRaisesRegex(
            OperatingNWCCompletenessError,
            "filing result does not belong",
        ):
            evaluate_operating_nwc_completeness(
                balance_sheets,
                external_result,
                policy,
            )

    def test_duplicate_metric_results_are_rejected(self) -> None:
        component = required(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCComponentClassification.OPERATING_ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        policy = OperatingNWCPolicy("test", 1, (component,))
        filing = AnnualBalanceSheetFilingResult(
            FILING,
            (
                make_resolved(FinancialMetric.OPERATING_RECEIVABLES),
                make_missing(FinancialMetric.OPERATING_RECEIVABLES),
            ),
        )

        with self.assertRaisesRegex(
            OperatingNWCCompletenessError,
            "duplicate metric 'operating_receivables'",
        ):
            evaluate(filing, policy)

    def test_absent_required_configured_metric_is_rejected(self) -> None:
        component = required(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCComponentClassification.OPERATING_ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        policy = OperatingNWCPolicy("test", 1, (component,))

        with self.assertRaisesRegex(
            OperatingNWCCompletenessError,
            "omits required configured metric 'operating_receivables'",
        ):
            evaluate(AnnualBalanceSheetFilingResult(FILING, ()), policy)

    def test_unknown_cik_policy_lookup_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            OperatingNWCCompletenessError,
            "No Operating NWC policy is configured for CIK 999999",
        ):
            operating_nwc_policy_for_cik(999999)

    def test_built_in_policy_component_classifications(self) -> None:
        asset = OperatingNWCComponentClassification.OPERATING_ASSET
        liability = OperatingNWCComponentClassification.OPERATING_LIABILITY
        excluded = OperatingNWCComponentClassification.EXCLUDED
        not_applicable = OperatingNWCComponentClassification.NOT_APPLICABLE
        unresolved = OperatingNWCComponentClassification.METHODOLOGY_UNRESOLVED
        expected = {
            1326801: (
                (OperatingNWCComponent.OPERATING_RECEIVABLES, asset),
                (OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, not_applicable),
                (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, liability),
                (OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, liability),
                (OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, liability),
                (OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY, not_applicable),
                (OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, not_applicable),
                (OperatingNWCComponent.OTHER_ACCRUED_LIABILITIES, unresolved),
                (OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES, excluded),
                (OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, excluded),
            ),
            1652044: (
                (OperatingNWCComponent.OPERATING_RECEIVABLES, asset),
                (OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, not_applicable),
                (OperatingNWCComponent.INVENTORY, asset),
                (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, unresolved),
                (OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, liability),
                (OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, liability),
                (OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY, liability),
                (OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, not_applicable),
                (OperatingNWCComponent.ACCRUED_CUSTOMER_LIABILITIES, liability),
                (OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, unresolved),
                (OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES, excluded),
                (OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, excluded),
            ),
            789019: (
                (OperatingNWCComponent.OPERATING_RECEIVABLES, asset),
                (OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, not_applicable),
                (OperatingNWCComponent.INVENTORY, asset),
                (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, unresolved),
                (OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, liability),
                (OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, liability),
                (OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY, not_applicable),
                (OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, not_applicable),
                (OperatingNWCComponent.COMPONENT_PURCHASE_RECEIVABLES, excluded),
                (OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, unresolved),
                (OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES, excluded),
                (OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, excluded),
            ),
            320193: (
                (OperatingNWCComponent.OPERATING_RECEIVABLES, asset),
                (OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, asset),
                (OperatingNWCComponent.INVENTORY, asset),
                (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, liability),
                (OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, liability),
                (OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, unresolved),
                (OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY, not_applicable),
                (OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, not_applicable),
                (OperatingNWCComponent.DISTRIBUTION_AND_MARKETING_LIABILITY, unresolved),
                (OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, unresolved),
                (OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, excluded),
            ),
            909832: (
                (OperatingNWCComponent.OPERATING_RECEIVABLES, asset),
                (OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES, not_applicable),
                (OperatingNWCComponent.INVENTORY, asset),
                (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, liability),
                (OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES, liability),
                (OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES, liability),
                (OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY, not_applicable),
                (OperatingNWCComponent.MEMBER_REWARDS_LIABILITY, liability),
                (OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES, unresolved),
                (OperatingNWCComponent.OPERATING_LEASE_LIABILITIES, excluded),
            ),
        }

        for company_cik, classifications in expected.items():
            with self.subTest(company_cik=company_cik):
                policy = operating_nwc_policy_for_cik(company_cik)
                self.assertEqual(
                    tuple(
                        (component.component, component.classification)
                        for component in policy.components
                    ),
                    classifications,
                )

    def test_all_five_researched_policies_remain_incomplete(self) -> None:
        policies = (
            META_OPERATING_NWC_POLICY,
            GOOGL_OPERATING_NWC_POLICY,
            MSFT_OPERATING_NWC_POLICY,
            AAPL_OPERATING_NWC_POLICY,
            COST_OPERATING_NWC_POLICY,
        )
        for policy in policies:
            with self.subTest(policy=policy.policy_id):
                metrics = tuple(
                    make_resolved(component.metric)
                    for component in policy.components
                    if component.metric is not None
                )
                result = evaluate(
                    AnnualBalanceSheetFilingResult(FILING, metrics),
                    policy,
                )

                self.assertFalse(result.is_complete)
                self.assertTrue(result.methodology_unresolved_components)
                self.assertEqual(result.missing_required_components, ())
                self.assertEqual(result.ambiguous_required_components, ())


class OperatingNWCReadinessTests(TestCase):
    def test_reconstruction_incomplete_can_be_valuation_ready(self) -> None:
        metrics = tuple(
            make_resolved(component.metric)
            for component in COST_OPERATING_NWC_POLICY.components
            if component.metric is not None
        )
        filing_result = AnnualBalanceSheetFilingResult(FILING, metrics)
        balance_sheets = make_balance_sheets(filing_result, 909832)

        reconstruction = evaluate_operating_nwc_completeness(
            balance_sheets,
            filing_result,
            COST_OPERATING_NWC_POLICY,
        )
        readiness = evaluate_operating_nwc_readiness(
            balance_sheets,
            filing_result,
            COST_OPERATING_NWC_VALUATION_POLICY,
        )

        self.assertFalse(reconstruction.is_complete)
        self.assertTrue(reconstruction.methodology_unresolved_components)
        self.assertTrue(readiness.is_ready)
        self.assertTrue(readiness.configured_non_mandatory_components)
        self.assertFalse(hasattr(readiness, "value"))
        self.assertFalse(hasattr(readiness, "operating_nwc"))

    def test_initial_issuer_readiness_states_are_conservative(self) -> None:
        cases = (
            (META_OPERATING_NWC_VALUATION_POLICY, True),
            (GOOGL_OPERATING_NWC_VALUATION_POLICY, False),
            (MSFT_OPERATING_NWC_VALUATION_POLICY, False),
            (AAPL_OPERATING_NWC_VALUATION_POLICY, False),
            (COST_OPERATING_NWC_VALUATION_POLICY, True),
        )
        for policy, expected in cases:
            with self.subTest(policy=policy.policy_id):
                metrics = tuple(
                    make_resolved(component.metric)
                    for component in policy.components
                    if component.metric is not None
                )
                result = evaluate_readiness(
                    AnnualBalanceSheetFilingResult(FILING, metrics),
                    policy,
                )

                self.assertIs(result.is_ready, expected)
                self.assertIs(bool(result.methodology_blockers), not expected)

    def test_meta_v2_all_periods_are_ready_without_contract_liability(
        self,
    ) -> None:
        results = []
        for year in range(2021, 2026):
            filing = SECFiling(
                accession_number=f"meta-{year}",
                form="10-K",
                filing_date=date(year + 1, 2, 1),
                report_date=date(year, 12, 31),
                primary_document=f"meta-{year}.htm",
            )
            metrics = []
            for component in META_OPERATING_NWC_VALUATION_POLICY.components:
                if component.metric is None:
                    continue
                if component.metric is FinancialMetric.TRADE_ACCOUNTS_PAYABLE:
                    evidence = make_evidence(
                        component.metric,
                        balance_date=filing.report_date,
                        accession_number=filing.accession_number,
                        filing_date=filing.filing_date,
                    )
                    metrics.append(
                        DerivedBalanceSheetValue(
                            metric=component.metric,
                            value=10,
                            unit="USD",
                            balance_date=filing.report_date,
                            policy_id="meta_adjusted_trade_accounts_payable_v1",
                            operation=DerivationOperation.SUBTRACT,
                            operands=(
                                BalanceSheetDerivationOperand(
                                    metric=component.metric,
                                    value=10,
                                    unit="USD",
                                    start=None,
                                    end=filing.report_date,
                                    chosen_source=evidence,
                                    confirming_sources=(),
                                ),
                            ),
                            steps=(),
                        )
                    )
                else:
                    metrics.append(
                        make_resolved(
                            component.metric,
                            balance_date=filing.report_date,
                            accession_number=filing.accession_number,
                            filing_date=filing.filing_date,
                        )
                    )
            contract_metric = FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES
            metrics.append(
                make_missing(contract_metric)
                if year == 2025
                else make_resolved(
                    contract_metric,
                    value=year,
                    balance_date=filing.report_date,
                    accession_number=filing.accession_number,
                    filing_date=filing.filing_date,
                )
            )
            results.append(AnnualBalanceSheetFilingResult(filing, tuple(metrics)))
        balance_sheets = make_balance_sheet_series(tuple(results), 1326801)

        readiness = tuple(
            evaluate_operating_nwc_readiness(
                balance_sheets,
                filing_result,
                META_OPERATING_NWC_VALUATION_POLICY,
            )
            for filing_result in balance_sheets.annual
        )

        self.assertEqual(
            tuple(result.is_ready for result in readiness),
            (True, True, True, True, True),
        )
        self.assertTrue(
            all(
                result.policy_id == "meta_operating_nwc_valuation"
                and result.policy_version == "2"
                for result in readiness
            )
        )
        self.assertEqual(
            tuple(
                component.component
                for component in readiness[-1].configured_non_mandatory_components
            ),
            (
                OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                OperatingNWCComponent.OTHER_ACCRUED_LIABILITIES,
                OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
                OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
            ),
        )
        self.assertEqual(readiness[-1].missing_mandatory_components, ())
        self.assertFalse(
            any(
                item.policy.component
                is OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES
                for result in readiness
                for item in result.resolved_mandatory_components
            )
        )
        contract_policy = readiness[-1].configured_non_mandatory_components[0]
        self.assertIn("not treated as zero", contract_policy.rationale)
        derived = next(
            item
            for item in readiness[0].resolved_mandatory_components
            if item.policy.component is OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE
        )
        self.assertIsInstance(derived.result, DerivedBalanceSheetValue)

        reconstruction = evaluate_operating_nwc_completeness(
            balance_sheets,
            balance_sheets.annual[0],
            META_OPERATING_NWC_POLICY,
        )
        self.assertFalse(reconstruction.is_complete)
        self.assertTrue(reconstruction.methodology_unresolved_components)

    def test_meta_v2_still_requires_employee_liabilities(self) -> None:
        metrics = []
        for component in META_OPERATING_NWC_VALUATION_POLICY.components:
            if component.metric is None:
                continue
            metrics.append(
                make_missing(component.metric)
                if component.metric is FinancialMetric.EMPLOYEE_RELATED_LIABILITIES
                else make_resolved(component.metric)
            )

        result = evaluate_readiness(
            AnnualBalanceSheetFilingResult(FILING, tuple(metrics)),
            META_OPERATING_NWC_VALUATION_POLICY,
        )

        self.assertFalse(result.is_ready)
        self.assertEqual(
            tuple(item.policy.component for item in result.missing_mandatory_components),
            (OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,),
        )

    def test_all_five_cost_periods_are_ready(self) -> None:
        results = tuple(
            AnnualBalanceSheetFilingResult(
                SECFiling(
                    accession_number=f"cost-{year}",
                    form="10-K",
                    filing_date=date(year, 10, 1),
                    report_date=date(year, 8, 31),
                    primary_document=f"cost-{year}.htm",
                ),
                tuple(
                    make_resolved(
                        component.metric,
                        balance_date=date(year, 8, 31),
                        accession_number=f"cost-{year}",
                        filing_date=date(year, 10, 1),
                    )
                    for component in COST_OPERATING_NWC_VALUATION_POLICY.components
                    if component.metric is not None
                ),
            )
            for year in range(2021, 2026)
        )
        balance_sheets = make_balance_sheet_series(results, 909832)

        readiness = tuple(
            evaluate_operating_nwc_readiness(
                balance_sheets,
                filing_result,
                COST_OPERATING_NWC_VALUATION_POLICY,
            )
            for filing_result in results
        )

        self.assertTrue(all(result.is_ready for result in readiness))

    def test_zero_missing_ambiguity_and_methodology_blocker_are_distinct(self) -> None:
        asset = perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        liability = perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            OperatingNWCPerimeterSide.LIABILITY,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )
        blocker = perimeter_component(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            OperatingNWCPerimeterSide.LIABILITY,
            OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER,
        )
        policy = OperatingNWCValuationPolicy("test", "1", 1, (asset, liability, blocker))
        filing_result = AnnualBalanceSheetFilingResult(
            FILING,
            (
                make_resolved(FinancialMetric.OPERATING_RECEIVABLES, 0),
                make_ambiguous(FinancialMetric.TRADE_ACCOUNTS_PAYABLE),
            ),
        )

        result = evaluate_readiness(filing_result, policy)

        self.assertFalse(result.is_ready)
        self.assertEqual(result.resolved_mandatory_components[0].result.value, 0)
        self.assertEqual(result.missing_mandatory_components, ())
        self.assertEqual(len(result.ambiguous_mandatory_components), 1)
        self.assertEqual(result.methodology_blockers, (blocker,))

        missing_result = evaluate_readiness(
            AnnualBalanceSheetFilingResult(
                FILING,
                (
                    make_resolved(FinancialMetric.OPERATING_RECEIVABLES, 0),
                    make_missing(FinancialMetric.TRADE_ACCOUNTS_PAYABLE),
                ),
            ),
            policy,
        )
        self.assertEqual(len(missing_result.missing_mandatory_components), 1)

    def test_out_of_perimeter_gap_does_not_block_readiness(self) -> None:
        required_component = perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        outside = perimeter_component(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            OperatingNWCPerimeterSide.LIABILITY,
            OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER,
        )
        policy = OperatingNWCValuationPolicy(
            "test",
            "perimeter-v1",
            1,
            (required_component, outside),
        )

        result = evaluate_readiness(
            AnnualBalanceSheetFilingResult(
                FILING,
                (make_resolved(FinancialMetric.OPERATING_RECEIVABLES),),
            ),
            policy,
        )

        self.assertTrue(result.is_ready)
        self.assertEqual(result.policy_id, "test")
        self.assertEqual(result.policy_version, "perimeter-v1")
        self.assertEqual(result.configured_non_mandatory_components, (outside,))

    def test_readiness_rejects_wrong_company_and_external_filing(self) -> None:
        filing_result = AnnualBalanceSheetFilingResult(
            FILING,
            tuple(
                make_resolved(component.metric)
                for component in COST_OPERATING_NWC_VALUATION_POLICY.components
                if component.metric is not None
            ),
        )
        wrong_company = make_balance_sheets(filing_result, 320193)
        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "company does not match O-NWC valuation policy",
        ):
            evaluate_operating_nwc_readiness(
                wrong_company,
                filing_result,
                COST_OPERATING_NWC_VALUATION_POLICY,
            )

        contained = make_balance_sheets(filing_result, 909832)
        accepted = evaluate_operating_nwc_readiness(
            contained,
            filing_result,
            COST_OPERATING_NWC_VALUATION_POLICY,
        )
        self.assertTrue(accepted.is_ready)

        external = replace(filing_result)
        self.assertEqual(external, filing_result)
        self.assertIsNot(external, filing_result)
        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "filing result does not belong",
        ):
            evaluate_operating_nwc_readiness(
                contained,
                external,
                COST_OPERATING_NWC_VALUATION_POLICY,
            )

    def test_readiness_rejects_duplicate_or_absent_configured_metrics(self) -> None:
        required_component = perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        policy = OperatingNWCValuationPolicy("test", "1", 1, (required_component,))

        duplicate = AnnualBalanceSheetFilingResult(
            FILING,
            (
                make_resolved(FinancialMetric.OPERATING_RECEIVABLES),
                make_missing(FinancialMetric.OPERATING_RECEIVABLES),
            ),
        )
        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "duplicate metric 'operating_receivables'",
        ):
            evaluate_readiness(duplicate, policy)

        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "omits configured perimeter metric 'operating_receivables'",
        ):
            evaluate_readiness(AnnualBalanceSheetFilingResult(FILING, ()), policy)

    def test_readiness_output_is_deterministic_and_policy_ordered(self) -> None:
        policy = COST_OPERATING_NWC_VALUATION_POLICY
        metrics = tuple(
            make_resolved(component.metric)
            for component in policy.components
            if component.metric is not None
        )
        forward = evaluate_readiness(
            AnnualBalanceSheetFilingResult(FILING, metrics),
            policy,
        )
        reverse = evaluate_readiness(
            AnnualBalanceSheetFilingResult(FILING, tuple(reversed(metrics))),
            policy,
        )

        self.assertEqual(forward, reverse)
        self.assertEqual(
            tuple(item.policy.component for item in forward.resolved_mandatory_components),
            tuple(
                component.component
                for component in policy.components
                if component.metric is not None
            ),
        )

    def test_perimeter_component_constructor_rejects_contradictory_states(self) -> None:
        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "Required perimeter component must be mandatory",
        ):
            OperatingNWCPerimeterComponentPolicy(
                component=OperatingNWCComponent.OPERATING_RECEIVABLES,
                side=OperatingNWCPerimeterSide.ASSET,
                treatment=OperatingNWCPerimeterTreatment.REQUIRED,
                mandatory=False,
                metric=FinancialMetric.OPERATING_RECEIVABLES,
                rationale="Invalid required component",
            )

        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "Required perimeter component must be mandatory",
        ):
            OperatingNWCPerimeterComponentPolicy(
                component=OperatingNWCComponent.OPERATING_RECEIVABLES,
                side=OperatingNWCPerimeterSide.ASSET,
                treatment=OperatingNWCPerimeterTreatment.REQUIRED,
                mandatory=True,
                metric=FinancialMetric.INVENTORY,
                rationale="Invalid metric association",
            )

        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "Non-mandatory perimeter component cannot request",
        ):
            OperatingNWCPerimeterComponentPolicy(
                component=OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
                side=OperatingNWCPerimeterSide.LIABILITY,
                treatment=OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER,
                mandatory=False,
                metric=FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                rationale="Invalid outside component",
            )

    def test_valuation_policy_constructor_rejects_duplicate_configuration(self) -> None:
        receivables = perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "duplicate components",
        ):
            OperatingNWCValuationPolicy(
                "duplicate-components",
                "1",
                1,
                (receivables, receivables),
            )

        with patch.dict(
            operating_nwc_module._NORMALIZED_METRICS,
            {OperatingNWCComponent.INVENTORY: FinancialMetric.OPERATING_RECEIVABLES},
        ):
            inventory = perimeter_component(
                OperatingNWCComponent.INVENTORY,
                OperatingNWCPerimeterSide.ASSET,
                OperatingNWCPerimeterTreatment.REQUIRED,
                FinancialMetric.OPERATING_RECEIVABLES,
            )
            with self.assertRaisesRegex(
                OperatingNWCReadinessError,
                "duplicate configured metrics",
            ):
                OperatingNWCValuationPolicy(
                    "duplicate-metrics",
                    "1",
                    1,
                    (receivables, inventory),
                )

    def test_valuation_policy_registry_rejects_ambiguous_registrations(self) -> None:
        duplicate_cik = replace(
            META_OPERATING_NWC_VALUATION_POLICY,
            policy_id="duplicate-meta-cik",
        )
        with patch.object(
            operating_nwc_module,
            "OPERATING_NWC_VALUATION_POLICIES",
            (META_OPERATING_NWC_VALUATION_POLICY, duplicate_cik),
        ):
            with self.assertRaisesRegex(
                OperatingNWCReadinessError,
                "duplicate company CIKs",
            ):
                operating_nwc_valuation_policy_for_cik(1326801)

        duplicate_historical_identity = replace(
            META_OPERATING_NWC_VALUATION_POLICY_V2,
            company_cik=999999,
        )
        with patch.object(
            operating_nwc_module,
            "OPERATING_NWC_VALUATION_POLICY_VERSIONS",
            (
                META_OPERATING_NWC_VALUATION_POLICY_V1,
                META_OPERATING_NWC_VALUATION_POLICY_V2,
                duplicate_historical_identity,
            ),
        ):
            with self.assertRaisesRegex(
                OperatingNWCReadinessError,
                "history contains duplicate policy ID/version",
            ):
                operating_nwc_valuation_policy_for_id_and_version(
                    "meta_operating_nwc_valuation",
                    "2",
                )

        duplicate_identity = replace(
            META_OPERATING_NWC_VALUATION_POLICY,
            company_cik=999999,
        )
        with patch.object(
            operating_nwc_module,
            "OPERATING_NWC_VALUATION_POLICIES",
            (META_OPERATING_NWC_VALUATION_POLICY, duplicate_identity),
        ):
            with self.assertRaisesRegex(
                OperatingNWCReadinessError,
                "duplicate policy ID/version",
            ):
                operating_nwc_valuation_policy_for_cik(1326801)

    def test_valuation_policy_lookup_is_independent_of_registry_order(self) -> None:
        with (
            patch.object(
                operating_nwc_module,
                "OPERATING_NWC_VALUATION_POLICIES",
                tuple(
                    reversed(operating_nwc_module.OPERATING_NWC_VALUATION_POLICIES)
                ),
            ),
            patch.object(
                operating_nwc_module,
                "OPERATING_NWC_VALUATION_POLICY_VERSIONS",
                tuple(
                    reversed(
                        operating_nwc_module.OPERATING_NWC_VALUATION_POLICY_VERSIONS
                    )
                ),
            ),
        ):
            self.assertIs(
                operating_nwc_valuation_policy_for_cik(1326801),
                META_OPERATING_NWC_VALUATION_POLICY,
            )
            self.assertIs(
                operating_nwc_valuation_policy_for_id_and_version(
                    "meta_operating_nwc_valuation",
                    "2",
                ),
                META_OPERATING_NWC_VALUATION_POLICY_V2,
            )

    def test_active_policy_must_equal_its_versioned_definition(self) -> None:
        without_meta_v2 = tuple(
            policy
            for policy in operating_nwc_module.OPERATING_NWC_VALUATION_POLICY_VERSIONS
            if policy is not META_OPERATING_NWC_VALUATION_POLICY_V2
        )
        with patch.object(
            operating_nwc_module,
            "OPERATING_NWC_VALUATION_POLICY_VERSIONS",
            without_meta_v2,
        ):
            with self.assertRaisesRegex(
                OperatingNWCReadinessError,
                "missing from policy history",
            ):
                operating_nwc_valuation_policy_for_cik(1326801)

        contract_component = META_OPERATING_NWC_VALUATION_POLICY_V2.components[3]
        mismatched_meta_v2 = replace(
            META_OPERATING_NWC_VALUATION_POLICY_V2,
            components=(
                *META_OPERATING_NWC_VALUATION_POLICY_V2.components[:3],
                replace(
                    contract_component,
                    treatment=OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER,
                    mandatory=True,
                ),
                *META_OPERATING_NWC_VALUATION_POLICY_V2.components[4:],
            ),
        )
        mismatched_history = tuple(
            mismatched_meta_v2
            if policy is META_OPERATING_NWC_VALUATION_POLICY_V2
            else policy
            for policy in operating_nwc_module.OPERATING_NWC_VALUATION_POLICY_VERSIONS
        )
        with patch.object(
            operating_nwc_module,
            "OPERATING_NWC_VALUATION_POLICY_VERSIONS",
            mismatched_history,
        ):
            with self.assertRaisesRegex(
                OperatingNWCReadinessError,
                "differs from its policy-history definition",
            ):
                operating_nwc_valuation_policy_for_id_and_version(
                    "meta_operating_nwc_valuation",
                    "2",
                )

    def test_meta_active_and_explicit_version_lookups(self) -> None:
        self.assertIs(
            META_OPERATING_NWC_VALUATION_POLICY,
            META_OPERATING_NWC_VALUATION_POLICY_V2,
        )
        self.assertIs(
            operating_nwc_valuation_policy_for_cik(1326801),
            META_OPERATING_NWC_VALUATION_POLICY_V2,
        )
        self.assertIs(
            operating_nwc_valuation_policy_for_id_and_version(
                "meta_operating_nwc_valuation",
                "1",
            ),
            META_OPERATING_NWC_VALUATION_POLICY_V1,
        )
        self.assertIs(
            operating_nwc_valuation_policy_for_id_and_version(
                "meta_operating_nwc_valuation",
                "2",
            ),
            META_OPERATING_NWC_VALUATION_POLICY_V2,
        )

        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "No Operating NWC valuation policy",
        ):
            operating_nwc_valuation_policy_for_id_and_version(
                "meta_operating_nwc_valuation",
                "999",
            )

    def test_meta_v1_complete_ordered_perimeter_is_preserved(self) -> None:
        self.assertEqual(
            tuple(
                (
                    component.component,
                    component.side,
                    component.treatment,
                    component.mandatory,
                    component.metric,
                )
                for component in META_OPERATING_NWC_VALUATION_POLICY_V1.components
            ),
            (
                (
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCPerimeterSide.ASSET,
                    OperatingNWCPerimeterTreatment.REQUIRED,
                    True,
                    FinancialMetric.OPERATING_RECEIVABLES,
                ),
                (
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCPerimeterSide.LIABILITY,
                    OperatingNWCPerimeterTreatment.REQUIRED,
                    True,
                    FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                ),
                (
                    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                    OperatingNWCPerimeterSide.LIABILITY,
                    OperatingNWCPerimeterTreatment.REQUIRED,
                    True,
                    FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
                ),
                (
                    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
                    OperatingNWCPerimeterSide.LIABILITY,
                    OperatingNWCPerimeterTreatment.REQUIRED,
                    True,
                    FinancialMetric.EMPLOYEE_RELATED_LIABILITIES,
                ),
                (
                    OperatingNWCComponent.OTHER_ACCRUED_LIABILITIES,
                    OperatingNWCPerimeterSide.LIABILITY,
                    OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER,
                    False,
                    None,
                ),
                (
                    OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
                    OperatingNWCPerimeterSide.LIABILITY,
                    OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER,
                    False,
                    None,
                ),
                (
                    OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
                    OperatingNWCPerimeterSide.LIABILITY,
                    OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER,
                    False,
                    None,
                ),
            ),
        )

    def test_builtin_policy_lookup_and_versioned_perimeters(self) -> None:
        expected = {
            1326801: (
                (
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
                ),
                (),
                (
                    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                    OperatingNWCComponent.OTHER_ACCRUED_LIABILITIES,
                    OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
                    OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
                ),
            ),
            1652044: (
                (
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
                    OperatingNWCComponent.ACCRUED_REVENUE_SHARE_LIABILITY,
                    OperatingNWCComponent.ACCRUED_CUSTOMER_LIABILITIES,
                ),
                (
                    OperatingNWCComponent.INVENTORY,
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                ),
                (
                    OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
                    OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
                    OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
                ),
            ),
            789019: (
                (
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCComponent.INVENTORY,
                    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
                ),
                (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,),
                (
                    OperatingNWCComponent.COMPONENT_PURCHASE_RECEIVABLES,
                    OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
                    OperatingNWCComponent.ACCRUED_PP_AND_E_PURCHASES,
                    OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
                ),
            ),
            320193: (
                (
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES,
                    OperatingNWCComponent.INVENTORY,
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                ),
                (
                    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
                    OperatingNWCComponent.DISTRIBUTION_AND_MARKETING_LIABILITY,
                ),
                (
                    OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
                    OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
                ),
            ),
            909832: (
                (
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCComponent.INVENTORY,
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
                    OperatingNWCComponent.MEMBER_REWARDS_LIABILITY,
                ),
                (),
                (
                    OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
                    OperatingNWCComponent.OPERATING_LEASE_LIABILITIES,
                ),
            ),
        }
        for company_cik, (required, blockers, outside) in expected.items():
            with self.subTest(company_cik=company_cik):
                policy = operating_nwc_valuation_policy_for_cik(company_cik)
                self.assertEqual(
                    policy.version,
                    "2" if company_cik == 1326801 else "1",
                )
                self.assertEqual(
                    tuple(
                        component.component
                        for component in policy.components
                        if component.treatment
                        is OperatingNWCPerimeterTreatment.REQUIRED
                    ),
                    required,
                )
                self.assertEqual(
                    tuple(
                        component.component
                        for component in policy.components
                        if component.treatment
                        is OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER
                    ),
                    blockers,
                )
                self.assertEqual(
                    tuple(
                        component.component
                        for component in policy.components
                        if component.treatment
                        is OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER
                    ),
                    outside,
                )
                asset_components = {
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCComponent.VENDOR_NONTRADE_RECEIVABLES,
                    OperatingNWCComponent.INVENTORY,
                    OperatingNWCComponent.COMPONENT_PURCHASE_RECEIVABLES,
                }
                self.assertTrue(
                    all(
                        component.side
                        is (
                            OperatingNWCPerimeterSide.ASSET
                            if component.component in asset_components
                            else OperatingNWCPerimeterSide.LIABILITY
                        )
                        for component in policy.components
                    )
                )

        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "No Operating NWC valuation policy is configured",
        ):
            operating_nwc_valuation_policy_for_cik(999999)


class OperatingNWCCalculationTests(TestCase):
    def test_asset_minus_liability_decimal_arithmetic_and_ordering(self) -> None:
        asset = perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        liability = perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            OperatingNWCPerimeterSide.LIABILITY,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )
        outside = perimeter_component(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            OperatingNWCPerimeterSide.LIABILITY,
            OperatingNWCPerimeterTreatment.OUT_OF_PERIMETER,
        )
        policy = OperatingNWCValuationPolicy(
            "calculation-test",
            "7",
            1,
            (asset, liability, outside),
        )
        receivables = make_resolved(
            FinancialMetric.OPERATING_RECEIVABLES,
            Decimal("100.10"),
        )
        payables = make_resolved(
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            Decimal("40.05"),
        )
        excluded = make_resolved(
            FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
            Decimal("999.99"),
        )
        filing_result = AnnualBalanceSheetFilingResult(
            FILING,
            (excluded, payables, receivables),
        )
        balance_sheets = make_balance_sheets(filing_result, 1)

        result = calculate_operating_nwc_level(
            balance_sheets,
            filing_result,
            policy,
        )

        self.assertIsInstance(result, CalculatedOperatingNWC)
        assert isinstance(result, CalculatedOperatingNWC)
        self.assertEqual(result.amount, Decimal("60.05"))
        self.assertIsInstance(result.amount, Decimal)
        self.assertEqual(result.company_cik, 1)
        self.assertEqual(result.balance_date, REPORT_DATE)
        self.assertIs(result.filing, FILING)
        self.assertEqual(result.policy_id, "calculation-test")
        self.assertEqual(result.policy_version, "7")
        self.assertEqual(result.unit, "USD")
        self.assertIs(
            result.formula,
            OperatingNWCCalculationFormula.REQUIRED_ASSETS_MINUS_REQUIRED_LIABILITIES,
        )
        self.assertEqual(
            tuple(contribution.component for contribution in result.contributions),
            (
                OperatingNWCComponent.OPERATING_RECEIVABLES,
                OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            ),
        )
        self.assertEqual(
            tuple(contribution.balance for contribution in result.contributions),
            (Decimal("100.10"), Decimal("40.05")),
        )
        self.assertEqual(
            tuple(
                contribution.signed_contribution
                for contribution in result.contributions
            ),
            (Decimal("100.10"), Decimal("-40.05")),
        )
        self.assertEqual(
            sum(
                (
                    contribution.signed_contribution
                    for contribution in result.contributions
                ),
                start=Decimal(0),
            ),
            result.amount,
        )
        self.assertIs(result.contributions[0].source_result, receivables)
        self.assertIs(result.contributions[1].source_result, payables)
        self.assertNotIn(
            FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
            tuple(
                contribution.source_result.metric
                for contribution in result.contributions
            ),
        )

        reversed_filing = AnnualBalanceSheetFilingResult(
            FILING,
            tuple(reversed(filing_result.metrics)),
        )
        reversed_balance_sheets = make_balance_sheets(reversed_filing, 1)
        deterministic = calculate_operating_nwc_level(
            reversed_balance_sheets,
            reversed_filing,
            policy,
        )
        self.assertEqual(deterministic, result)

    def test_explicit_zero_and_missing_outside_component_are_accepted(self) -> None:
        metrics = []
        for component in META_OPERATING_NWC_VALUATION_POLICY_V2.components:
            if component.metric is None:
                continue
            value = (
                Decimal("0")
                if component.metric is FinancialMetric.OPERATING_RECEIVABLES
                else Decimal("10")
            )
            metrics.append(make_resolved(component.metric, value))
        metrics.append(make_missing(FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES))
        filing_result = AnnualBalanceSheetFilingResult(FILING, tuple(metrics))
        balance_sheets = make_balance_sheets(filing_result, 1326801)

        result = calculate_operating_nwc_level(
            balance_sheets,
            filing_result,
            META_OPERATING_NWC_VALUATION_POLICY_V2,
        )

        self.assertIsInstance(result, CalculatedOperatingNWC)
        assert isinstance(result, CalculatedOperatingNWC)
        self.assertEqual(result.contributions[0].balance, Decimal("0"))
        self.assertEqual(result.amount, Decimal("-20"))

    def test_not_ready_results_never_produce_partial_amounts(self) -> None:
        required_asset = perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        blocker = perimeter_component(
            OperatingNWCComponent.RESIDUAL_CURRENT_LIABILITIES,
            OperatingNWCPerimeterSide.LIABILITY,
            OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER,
        )
        policies_and_metrics = (
            (
                OperatingNWCValuationPolicy("missing", "1", 1, (required_asset,)),
                (make_missing(FinancialMetric.OPERATING_RECEIVABLES),),
            ),
            (
                OperatingNWCValuationPolicy("ambiguous", "1", 1, (required_asset,)),
                (make_ambiguous(FinancialMetric.OPERATING_RECEIVABLES),),
            ),
            (
                OperatingNWCValuationPolicy(
                    "blocker",
                    "1",
                    1,
                    (required_asset, blocker),
                ),
                (make_resolved(FinancialMetric.OPERATING_RECEIVABLES),),
            ),
        )
        for policy, metrics in policies_and_metrics:
            with self.subTest(policy=policy.policy_id):
                filing_result = AnnualBalanceSheetFilingResult(FILING, metrics)
                result = calculate_operating_nwc_level(
                    make_balance_sheets(filing_result, 1),
                    filing_result,
                    policy,
                )
                self.assertIsInstance(result, OperatingNWCReadinessResult)
                self.assertFalse(result.is_ready)
                self.assertFalse(hasattr(result, "amount"))

    def test_ownership_boundaries_are_enforced(self) -> None:
        filing_result = AnnualBalanceSheetFilingResult(
            FILING,
            tuple(
                make_resolved(component.metric)
                for component in COST_OPERATING_NWC_VALUATION_POLICY.components
                if component.metric is not None
            ),
        )
        correct = make_balance_sheets(filing_result, 909832)
        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "company does not match",
        ):
            calculate_operating_nwc_level(
                make_balance_sheets(filing_result, 1326801),
                filing_result,
                COST_OPERATING_NWC_VALUATION_POLICY,
            )
        with self.assertRaisesRegex(
            OperatingNWCReadinessError,
            "does not belong",
        ):
            calculate_operating_nwc_level(
                correct,
                replace(filing_result),
                COST_OPERATING_NWC_VALUATION_POLICY,
            )

    def test_direct_component_provenance_must_match_selected_filing(self) -> None:
        component = perimeter_component(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        policy = OperatingNWCValuationPolicy("direct-integrity", "1", 1, (component,))
        valid = make_resolved(
            FinancialMetric.OPERATING_RECEIVABLES,
            Decimal("0"),
        )
        wrong_date = date(2024, 12, 31)
        bad_confirmation = replace(
            valid.chosen_source,
            accession_number="different-accession",
        )
        cases = (
            replace(valid, balance_date=wrong_date),
            replace(
                valid,
                chosen_source=replace(
                    valid.chosen_source,
                    accession_number="different-accession",
                ),
            ),
            replace(
                valid,
                unit="EUR",
                chosen_source=replace(valid.chosen_source, unit="EUR"),
            ),
            replace(
                valid,
                chosen_source=replace(valid.chosen_source, end=wrong_date),
            ),
            replace(valid, confirming_sources=(bad_confirmation,)),
            replace(
                valid,
                confirming_sources=(valid.chosen_source, bad_confirmation),
            ),
            replace(
                valid,
                confirming_sources=(bad_confirmation, valid.chosen_source),
            ),
        )
        for result in cases:
            with self.subTest(result=result):
                filing_result = AnnualBalanceSheetFilingResult(FILING, (result,))
                balance_sheets = make_balance_sheets(filing_result, 1)
                with self.assertRaises(OperatingNWCReadinessError):
                    evaluate_operating_nwc_readiness(
                        balance_sheets,
                        filing_result,
                        policy,
                    )
                with self.assertRaises(OperatingNWCReadinessError):
                    calculate_operating_nwc_level(
                        balance_sheets,
                        filing_result,
                        policy,
                    )

        valid_filing = AnnualBalanceSheetFilingResult(FILING, (valid,))
        calculated = calculate_operating_nwc_level(
            make_balance_sheets(valid_filing, 1),
            valid_filing,
            policy,
        )
        self.assertIsInstance(calculated, CalculatedOperatingNWC)
        self.assertEqual(calculated.amount, Decimal("0"))

    def test_derived_component_provenance_must_match_selected_filing(self) -> None:
        component = perimeter_component(
            OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
            OperatingNWCPerimeterSide.LIABILITY,
            OperatingNWCPerimeterTreatment.REQUIRED,
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )
        policy = OperatingNWCValuationPolicy("derived-integrity", "1", 1, (component,))
        source = make_evidence(
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            Decimal("10"),
        )
        operand = BalanceSheetDerivationOperand(
            metric=FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            value=Decimal("10"),
            unit="USD",
            start=None,
            end=REPORT_DATE,
            chosen_source=source,
            confirming_sources=(),
        )
        valid = DerivedBalanceSheetValue(
            metric=FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            value=Decimal("10"),
            unit="USD",
            balance_date=REPORT_DATE,
            policy_id="synthetic-derived",
            operation=DerivationOperation.SUBTRACT,
            operands=(operand,),
            steps=(),
        )
        wrong_date = date(2024, 12, 31)
        cases = (
            replace(valid, balance_date=wrong_date),
            replace(
                valid,
                operands=(
                    replace(
                        operand,
                        chosen_source=replace(
                            source,
                            accession_number="different-accession",
                        ),
                    ),
                ),
            ),
            replace(valid, operands=(replace(operand, end=wrong_date),)),
            replace(
                valid,
                unit="EUR",
                operands=(
                    replace(
                        operand,
                        unit="EUR",
                        chosen_source=replace(source, unit="EUR"),
                    ),
                ),
            ),
        )
        for result in cases:
            with self.subTest(result=result):
                filing_result = AnnualBalanceSheetFilingResult(FILING, (result,))
                balance_sheets = make_balance_sheets(filing_result, 1)
                with self.assertRaises(OperatingNWCReadinessError):
                    evaluate_operating_nwc_readiness(
                        balance_sheets,
                        filing_result,
                        policy,
                    )
                with self.assertRaises(OperatingNWCReadinessError):
                    calculate_operating_nwc_level(
                        balance_sheets,
                        filing_result,
                        policy,
                    )

        valid_filing = AnnualBalanceSheetFilingResult(FILING, (valid,))
        calculated = calculate_operating_nwc_level(
            make_balance_sheets(valid_filing, 1),
            valid_filing,
            policy,
        )
        self.assertIsInstance(calculated, CalculatedOperatingNWC)
        self.assertEqual(calculated.amount, Decimal("-10"))

    def test_explicit_meta_policy_version_is_never_replaced(self) -> None:
        metrics = tuple(
            make_resolved(component.metric, Decimal("10"))
            for component in META_OPERATING_NWC_VALUATION_POLICY_V1.components
            if component.metric is not None
        )
        filing_result = AnnualBalanceSheetFilingResult(FILING, metrics)
        balance_sheets = make_balance_sheets(filing_result, 1326801)

        v1 = calculate_operating_nwc_level(
            balance_sheets,
            filing_result,
            META_OPERATING_NWC_VALUATION_POLICY_V1,
        )
        v2 = calculate_operating_nwc_level(
            balance_sheets,
            filing_result,
            META_OPERATING_NWC_VALUATION_POLICY_V2,
        )

        self.assertIsInstance(v1, CalculatedOperatingNWC)
        self.assertIsInstance(v2, CalculatedOperatingNWC)
        assert isinstance(v1, CalculatedOperatingNWC)
        assert isinstance(v2, CalculatedOperatingNWC)
        self.assertEqual(v1.policy_version, "1")
        self.assertEqual(v2.policy_version, "2")
        self.assertEqual(v1.amount, Decimal("-20"))
        self.assertEqual(v2.amount, Decimal("-10"))
        self.assertIn(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            tuple(item.component for item in v1.contributions),
        )
        self.assertNotIn(
            OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
            tuple(item.component for item in v2.contributions),
        )

    def test_meta_and_cost_five_period_calculation_coverage(self) -> None:
        cases = (
            (
                META_OPERATING_NWC_VALUATION_POLICY_V2,
                1326801,
                tuple(date(year, 12, 31) for year in range(2021, 2026)),
            ),
            (
                COST_OPERATING_NWC_VALUATION_POLICY,
                909832,
                (
                    date(2021, 8, 29),
                    date(2022, 8, 28),
                    date(2023, 9, 3),
                    date(2024, 9, 1),
                    date(2025, 8, 31),
                ),
            ),
        )
        for policy, company_cik, report_dates in cases:
            with self.subTest(policy=policy.policy_id):
                results = []
                for report_date in report_dates:
                    filing = SECFiling(
                        accession_number=f"{company_cik}-{report_date.year}",
                        form="10-K",
                        filing_date=report_date + timedelta(days=40),
                        report_date=report_date,
                        primary_document=f"{company_cik}-{report_date.year}.htm",
                    )
                    metrics = []
                    for index, component in enumerate(policy.components, start=1):
                        if component.metric is None:
                            continue
                        if (
                            company_cik == 1326801
                            and component.metric
                            is FinancialMetric.TRADE_ACCOUNTS_PAYABLE
                        ):
                            metrics.append(
                                DerivedBalanceSheetValue(
                                    metric=component.metric,
                                    value=Decimal(index),
                                    unit="USD",
                                    balance_date=report_date,
                                    policy_id=(
                                        "meta_adjusted_trade_accounts_payable_v1"
                                    ),
                                    operation=DerivationOperation.SUBTRACT,
                                    operands=(
                                        BalanceSheetDerivationOperand(
                                            metric=component.metric,
                                            value=Decimal(index),
                                            unit="USD",
                                            start=None,
                                            end=report_date,
                                            chosen_source=make_evidence(
                                                component.metric,
                                                index,
                                                balance_date=report_date,
                                                accession_number=(
                                                    filing.accession_number
                                                ),
                                                filing_date=filing.filing_date,
                                            ),
                                            confirming_sources=(),
                                        ),
                                    ),
                                    steps=(),
                                )
                            )
                        else:
                            metrics.append(
                                make_resolved(
                                    component.metric,
                                    Decimal(index),
                                    balance_date=report_date,
                                    accession_number=filing.accession_number,
                                    filing_date=filing.filing_date,
                                )
                            )
                    if company_cik == 1326801:
                        metrics.append(
                            make_missing(
                                FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES
                            )
                        )
                    results.append(
                        AnnualBalanceSheetFilingResult(filing, tuple(metrics))
                    )
                balance_sheets = make_balance_sheet_series(
                    tuple(results),
                    company_cik,
                )
                calculated = tuple(
                    calculate_operating_nwc_level(
                        balance_sheets,
                        filing_result,
                        policy,
                    )
                    for filing_result in balance_sheets.annual
                )
                self.assertTrue(
                    all(isinstance(result, CalculatedOperatingNWC) for result in calculated)
                )
                self.assertEqual(len(calculated), 5)
                if company_cik == 1326801:
                    self.assertTrue(
                        all(
                            isinstance(result, CalculatedOperatingNWC)
                            and isinstance(
                                result.contributions[1].source_result,
                                DerivedBalanceSheetValue,
                            )
                            for result in calculated
                        )
                    )
                    for result, filing_result in zip(
                        calculated,
                        balance_sheets.annual,
                        strict=True,
                    ):
                        assert isinstance(result, CalculatedOperatingNWC)
                        derived_source = next(
                            metric
                            for metric in filing_result.metrics
                            if metric.metric
                            is FinancialMetric.TRADE_ACCOUNTS_PAYABLE
                        )
                        contribution = next(
                            item
                            for item in result.contributions
                            if item.component
                            is OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE
                        )
                        self.assertIs(contribution.source_result, derived_source)
                        self.assertIsInstance(
                            contribution.source_result,
                            DerivedBalanceSheetValue,
                        )
                        self.assertTrue(contribution.source_result.operands)

    def test_blocked_issuers_do_not_calculate(self) -> None:
        for policy in (
            GOOGL_OPERATING_NWC_VALUATION_POLICY,
            MSFT_OPERATING_NWC_VALUATION_POLICY,
            AAPL_OPERATING_NWC_VALUATION_POLICY,
        ):
            with self.subTest(policy=policy.policy_id):
                filing_result = AnnualBalanceSheetFilingResult(
                    FILING,
                    tuple(
                        make_resolved(component.metric)
                        for component in policy.components
                        if component.metric is not None
                    ),
                )
                result = calculate_operating_nwc_level(
                    make_balance_sheets(filing_result, policy.company_cik),
                    filing_result,
                    policy,
                )
                self.assertIsInstance(result, OperatingNWCReadinessResult)
                self.assertFalse(result.is_ready)
                self.assertTrue(result.methodology_blockers)


def make_calculated_level(
    amount: Decimal,
    balance_date: date,
    *,
    company_cik: int = 1326801,
    policy_id: str = "meta_operating_nwc_valuation",
    policy_version: str = "2",
    unit: str = "USD",
    contributions: tuple[OperatingNWCComponentContribution, ...] = (),
) -> CalculatedOperatingNWC:
    filing = SECFiling(
        accession_number=f"{company_cik}-{balance_date.isoformat()}",
        form="10-K",
        filing_date=balance_date + timedelta(days=40),
        report_date=balance_date,
        primary_document=f"{company_cik}-{balance_date.year}.htm",
    )
    return CalculatedOperatingNWC(
        company_cik=company_cik,
        balance_date=balance_date,
        filing=filing,
        policy_id=policy_id,
        policy_version=policy_version,
        amount=amount,
        unit=unit,
        formula=(
            OperatingNWCCalculationFormula.REQUIRED_ASSETS_MINUS_REQUIRED_LIABILITIES
        ),
        contributions=contributions,
    )


def make_change_contribution(
    component: OperatingNWCComponent,
    side: OperatingNWCPerimeterSide,
    metric: FinancialMetric,
    value: Decimal,
    balance_date: date,
) -> OperatingNWCComponentContribution:
    source_result = make_resolved(
        metric,
        value,
        balance_date=balance_date,
        accession_number=f"annual-{balance_date.isoformat()}",
        filing_date=balance_date + timedelta(days=40),
    )
    return OperatingNWCComponentContribution(
        component=component,
        side=side,
        source_result=source_result,
        balance=value,
        signed_contribution=(
            value if side is OperatingNWCPerimeterSide.ASSET else -value
        ),
    )


class OperatingNWCChangeTests(TestCase):
    def test_same_policy_identity_with_different_component_is_rejected(self) -> None:
        opening_date = date(2024, 12, 31)
        closing_date = date(2025, 12, 31)
        opening = make_calculated_level(
            Decimal("100"),
            opening_date,
            contributions=(
                make_change_contribution(
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCPerimeterSide.ASSET,
                    FinancialMetric.OPERATING_RECEIVABLES,
                    Decimal("100"),
                    opening_date,
                ),
            ),
        )
        closing = make_calculated_level(
            Decimal("-40"),
            closing_date,
            contributions=(
                make_change_contribution(
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCPerimeterSide.LIABILITY,
                    FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                    Decimal("40"),
                    closing_date,
                ),
            ),
        )

        with self.assertRaisesRegex(
            OperatingNWCChangeError, "ordered calculation perimeter"
        ):
            calculate_operating_nwc_change(opening, closing)

    def test_component_side_and_normalized_metric_are_part_of_perimeter(self) -> None:
        opening_date = date(2024, 12, 31)
        closing_date = date(2025, 12, 31)
        opening_contribution = make_change_contribution(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
            Decimal("100"),
            opening_date,
        )
        opening = make_calculated_level(
            Decimal("100"), opening_date, contributions=(opening_contribution,)
        )
        closing_base = make_change_contribution(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            FinancialMetric.OPERATING_RECEIVABLES,
            Decimal("110"),
            closing_date,
        )
        closings = (
            make_calculated_level(
                Decimal("-110"),
                closing_date,
                contributions=(
                    replace(
                        closing_base,
                        side=OperatingNWCPerimeterSide.LIABILITY,
                        signed_contribution=Decimal("-110"),
                    ),
                ),
            ),
            make_calculated_level(
                Decimal("110"),
                closing_date,
                contributions=(
                    replace(
                        closing_base,
                        source_result=make_resolved(
                            FinancialMetric.INVENTORY,
                            Decimal("110"),
                            balance_date=closing_date,
                            accession_number="annual-2025-12-31",
                            filing_date=closing_date + timedelta(days=40),
                        ),
                    ),
                ),
            ),
        )

        for closing in closings:
            with self.subTest(contribution=closing.contributions[0]):
                with self.assertRaisesRegex(
                    OperatingNWCChangeError, "ordered calculation perimeter"
                ):
                    calculate_operating_nwc_change(opening, closing)

    def test_same_perimeter_allows_different_values_and_annual_evidence(self) -> None:
        opening_date = date(2024, 12, 31)
        closing_date = date(2025, 12, 31)
        opening = make_calculated_level(
            Decimal("100"),
            opening_date,
            contributions=(
                make_change_contribution(
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCPerimeterSide.ASSET,
                    FinancialMetric.OPERATING_RECEIVABLES,
                    Decimal("100"),
                    opening_date,
                ),
            ),
        )
        closing = make_calculated_level(
            Decimal("135"),
            closing_date,
            contributions=(
                make_change_contribution(
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCPerimeterSide.ASSET,
                    FinancialMetric.OPERATING_RECEIVABLES,
                    Decimal("135"),
                    closing_date,
                ),
            ),
        )

        result = calculate_operating_nwc_change(opening, closing)

        self.assertEqual(result.change, Decimal("35"))
        self.assertNotEqual(
            result.opening_level.contributions[0].source_result.chosen_source,
            result.closing_level.contributions[0].source_result.chosen_source,
        )

    def test_contribution_order_is_part_of_perimeter(self) -> None:
        opening_date = date(2024, 12, 31)
        closing_date = date(2025, 12, 31)

        def perimeter(balance_date: date) -> tuple[OperatingNWCComponentContribution, ...]:
            return (
                make_change_contribution(
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCPerimeterSide.ASSET,
                    FinancialMetric.OPERATING_RECEIVABLES,
                    Decimal("100"),
                    balance_date,
                ),
                make_change_contribution(
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCPerimeterSide.LIABILITY,
                    FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                    Decimal("40"),
                    balance_date,
                ),
            )

        opening = make_calculated_level(
            Decimal("60"), opening_date, contributions=perimeter(opening_date)
        )
        closing = make_calculated_level(
            Decimal("60"),
            closing_date,
            contributions=tuple(reversed(perimeter(closing_date))),
        )

        with self.assertRaisesRegex(
            OperatingNWCChangeError, "ordered calculation perimeter"
        ):
            calculate_operating_nwc_change(opening, closing)

    def test_series_rejects_same_identity_perimeter_change_in_middle(self) -> None:
        dates = (date(2023, 12, 31), date(2024, 12, 31), date(2025, 12, 31))
        levels = tuple(
            make_calculated_level(
                Decimal("100"),
                balance_date,
                contributions=(
                    make_change_contribution(
                        component,
                        side,
                        metric,
                        Decimal("100"),
                        balance_date,
                    ),
                ),
            )
            for balance_date, component, side, metric in (
                (
                    dates[0],
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCPerimeterSide.ASSET,
                    FinancialMetric.OPERATING_RECEIVABLES,
                ),
                (
                    dates[1],
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCPerimeterSide.ASSET,
                    FinancialMetric.OPERATING_RECEIVABLES,
                ),
                (
                    dates[2],
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCPerimeterSide.LIABILITY,
                    FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                ),
            )
        )

        with self.assertRaisesRegex(
            OperatingNWCChangeError, "ordered calculation perimeter"
        ):
            calculate_operating_nwc_changes(levels)

    def test_positive_negative_zero_and_exact_decimal_changes(self) -> None:
        cases = (
            (Decimal("1.01"), Decimal("2.03"), Decimal("1.02")),
            (Decimal("2.03"), Decimal("1.01"), Decimal("-1.02")),
            (Decimal("1.01"), Decimal("1.01"), Decimal("0.00")),
        )
        for opening_amount, closing_amount, expected in cases:
            with self.subTest(expected=expected):
                opening = make_calculated_level(
                    opening_amount,
                    date(2024, 12, 31),
                )
                closing = make_calculated_level(
                    closing_amount,
                    date(2025, 12, 31),
                )

                result = calculate_operating_nwc_change(opening, closing)

                self.assertIsInstance(result, CalculatedOperatingNWCChange)
                self.assertEqual(result.change, expected)
                self.assertIsInstance(result.change, Decimal)
                self.assertEqual(result.opening_amount, opening_amount)
                self.assertEqual(result.closing_amount, closing_amount)
                self.assertIs(result.opening_level, opening)
                self.assertIs(result.closing_level, closing)
                self.assertEqual(result.company_cik, 1326801)
                self.assertEqual(result.policy_id, "meta_operating_nwc_valuation")
                self.assertEqual(result.policy_version, "2")
                self.assertEqual(result.unit, "USD")

    def test_incompatible_company_policy_version_and_unit_are_rejected(self) -> None:
        opening = make_calculated_level(Decimal("1"), date(2024, 12, 31))
        cases = (
            make_calculated_level(
                Decimal("2"),
                date(2025, 12, 31),
                company_cik=909832,
            ),
            make_calculated_level(
                Decimal("2"),
                date(2025, 12, 31),
                policy_id="different-policy",
            ),
            make_calculated_level(
                Decimal("2"),
                date(2025, 12, 31),
                policy_version="1",
            ),
            make_calculated_level(
                Decimal("2"),
                date(2025, 12, 31),
                unit="EUR",
            ),
        )
        for closing in cases:
            with self.subTest(closing=closing):
                with self.assertRaises(OperatingNWCChangeError):
                    calculate_operating_nwc_change(opening, closing)

    def test_level_amounts_must_be_finite_decimals(self) -> None:
        opening = make_calculated_level(Decimal("1"), date(2024, 12, 31))
        closing = make_calculated_level(Decimal("2"), date(2025, 12, 31))
        for malformed in (
            replace(opening, amount=1.0),
            replace(opening, amount=Decimal("NaN")),
            replace(closing, amount=Decimal("Infinity")),
        ):
            with self.subTest(amount=malformed.amount):
                with self.assertRaises(OperatingNWCChangeError):
                    calculate_operating_nwc_change(malformed, closing)

    def test_meta_v1_and_v2_are_not_comparable(self) -> None:
        opening = make_calculated_level(
            Decimal("1"),
            date(2024, 12, 31),
            policy_version="1",
        )
        closing = make_calculated_level(
            Decimal("2"),
            date(2025, 12, 31),
            policy_version="2",
        )

        with self.assertRaisesRegex(OperatingNWCChangeError, "policy version"):
            calculate_operating_nwc_change(opening, closing)

    def test_equal_reversed_and_malformed_level_dates_are_rejected(self) -> None:
        earlier = make_calculated_level(Decimal("1"), date(2024, 12, 31))
        later = make_calculated_level(Decimal("2"), date(2025, 12, 31))
        equal = make_calculated_level(Decimal("2"), date(2024, 12, 31))
        malformed = replace(
            later,
            filing=replace(later.filing, report_date=date(2025, 12, 30)),
        )
        for opening, closing in (
            (earlier, equal),
            (later, earlier),
            (earlier, malformed),
        ):
            with self.subTest(opening=opening.balance_date, closing=closing.balance_date):
                with self.assertRaises(OperatingNWCChangeError):
                    calculate_operating_nwc_change(opening, closing)

    def test_actual_non_calendar_and_week_based_dates_are_preserved(self) -> None:
        opening = make_calculated_level(
            Decimal("-7783000000"),
            date(2024, 9, 1),
            company_cik=909832,
            policy_id="cost_operating_nwc_valuation",
            policy_version="1",
        )
        closing = make_calculated_level(
            Decimal("-9200000000"),
            date(2025, 8, 31),
            company_cik=909832,
            policy_id="cost_operating_nwc_valuation",
            policy_version="1",
        )

        result = calculate_operating_nwc_change(opening, closing)

        self.assertEqual(result.opening_balance_date, date(2024, 9, 1))
        self.assertEqual(result.closing_balance_date, date(2025, 8, 31))
        self.assertEqual(result.change, Decimal("-1417000000"))

    def test_five_levels_produce_four_ordered_adjacent_changes(self) -> None:
        levels = tuple(
            make_calculated_level(Decimal(amount), balance_date)
            for amount, balance_date in (
                ("8816000000", date(2021, 12, 31)),
                ("4283000000", date(2022, 12, 31)),
                ("6553000000", date(2023, 12, 31)),
                ("7502000000", date(2024, 12, 31)),
                ("8653000000", date(2025, 12, 31)),
            )
        )

        results = calculate_operating_nwc_changes(levels)

        self.assertEqual(len(results), 4)
        self.assertEqual(
            tuple(result.change for result in results),
            (
                Decimal("-4533000000"),
                Decimal("2270000000"),
                Decimal("949000000"),
                Decimal("1151000000"),
            ),
        )
        self.assertEqual(
            tuple(result.opening_level for result in results),
            levels[:-1],
        )
        self.assertEqual(
            tuple(result.closing_level for result in results),
            levels[1:],
        )

    def test_series_rejects_policy_change_and_does_not_sort(self) -> None:
        levels = (
            make_calculated_level(Decimal("1"), date(2023, 12, 31)),
            make_calculated_level(Decimal("2"), date(2024, 12, 31)),
            make_calculated_level(
                Decimal("3"),
                date(2025, 12, 31),
                policy_version="3",
            ),
        )
        with self.assertRaisesRegex(OperatingNWCChangeError, "policy version"):
            calculate_operating_nwc_changes(levels)

        reversed_levels = tuple(reversed(levels[:2]))
        with self.assertRaisesRegex(OperatingNWCChangeError, "closing date"):
            calculate_operating_nwc_changes(reversed_levels)

    def test_series_with_fewer_than_two_levels_has_no_change(self) -> None:
        self.assertEqual(calculate_operating_nwc_changes(()), ())
        level = make_calculated_level(Decimal("1"), date(2025, 12, 31))
        self.assertEqual(calculate_operating_nwc_changes((level,)), ())
