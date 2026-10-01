from datetime import date, datetime, timezone
from unittest import TestCase

from valuation_platform.normalization import (
    AAPL_OPERATING_NWC_POLICY,
    COST_OPERATING_NWC_POLICY,
    GOOGL_OPERATING_NWC_POLICY,
    META_OPERATING_NWC_POLICY,
    MSFT_OPERATING_NWC_POLICY,
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    AnnualBalanceSheetFilingResult,
    EvidenceSourceKind,
    FactEvidence,
    FinancialMetric,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedAnnualBalanceSheets,
    NormalizedBalanceSheetValue,
    OperatingNWCCompletenessError,
    OperatingNWCComponent,
    OperatingNWCComponentClassification,
    OperatingNWCComponentPolicy,
    OperatingNWCPolicy,
    evaluate_operating_nwc_completeness,
    operating_nwc_policy_for_cik,
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


def make_evidence(metric: FinancialMetric, value: int = 10) -> FactEvidence:
    return FactEvidence(
        source_kind=EvidenceSourceKind.COMPANY_FACTS,
        source_url="facts-source",
        taxonomy="us-gaap",
        concept=metric.value,
        value=value,
        unit="USD",
        start=None,
        end=REPORT_DATE,
        accession_number="annual",
        observation_form="10-K",
        observation_filed=date(2026, 2, 1),
        fiscal_year=2025,
        fiscal_period="FY",
        frame="CY2025Q4I",
    )


def make_resolved(
    metric: FinancialMetric,
    value: int = 10,
) -> NormalizedBalanceSheetValue:
    return NormalizedBalanceSheetValue(
        metric=metric,
        value=value,
        unit="USD",
        balance_date=REPORT_DATE,
        chosen_source=make_evidence(metric, value),
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


class OperatingNWCCompletenessTests(TestCase):
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
        contained = AnnualBalanceSheetFilingResult(
            FILING,
            (make_resolved(FinancialMetric.OPERATING_RECEIVABLES),),
        )
        balance_sheets = make_balance_sheets(contained, 1326801)
        external_filing = SECFiling(
            accession_number="external-annual",
            form="10-K",
            filing_date=date(2025, 2, 1),
            report_date=date(2024, 12, 31),
            primary_document="external-annual.htm",
        )
        external_result = AnnualBalanceSheetFilingResult(
            external_filing,
            (make_resolved(FinancialMetric.OPERATING_RECEIVABLES),),
        )

        with self.assertRaisesRegex(
            OperatingNWCCompletenessError,
            "filing result does not belong",
        ):
            evaluate_operating_nwc_completeness(
                balance_sheets,
                external_result,
                META_OPERATING_NWC_POLICY,
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
                (OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE, unresolved),
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
                (OperatingNWCComponent.ACCRUED_CUSTOMER_LIABILITIES, unresolved),
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
