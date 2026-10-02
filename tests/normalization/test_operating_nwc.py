from dataclasses import replace
from datetime import date, datetime, timezone
from unittest import TestCase
from unittest.mock import patch

import valuation_platform.normalization.operating_nwc as operating_nwc_module

from valuation_platform.normalization import (
    AAPL_OPERATING_NWC_VALUATION_POLICY,
    AAPL_OPERATING_NWC_POLICY,
    COST_OPERATING_NWC_VALUATION_POLICY,
    COST_OPERATING_NWC_POLICY,
    GOOGL_OPERATING_NWC_VALUATION_POLICY,
    GOOGL_OPERATING_NWC_POLICY,
    META_OPERATING_NWC_VALUATION_POLICY,
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
    OperatingNWCComponent,
    OperatingNWCComponentClassification,
    OperatingNWCComponentPolicy,
    OperatingNWCPerimeterComponentPolicy,
    OperatingNWCPerimeterSide,
    OperatingNWCPerimeterTreatment,
    OperatingNWCPolicy,
    OperatingNWCReadinessError,
    OperatingNWCValuationPolicy,
    evaluate_operating_nwc_completeness,
    evaluate_operating_nwc_readiness,
    operating_nwc_policy_for_cik,
    operating_nwc_valuation_policy_for_cik,
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
    value: int = 10,
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
        frame="CY2025Q4I",
    )


def make_resolved(
    metric: FinancialMetric,
    value: int = 10,
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

    def test_meta_period_readiness_preserves_2025_missing_contract_liability(
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
                if (
                    year == 2025
                    and component.metric
                    is FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES
                ):
                    metrics.append(make_missing(component.metric))
                elif component.metric is FinancialMetric.TRADE_ACCOUNTS_PAYABLE:
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
            (True, True, True, True, False),
        )
        self.assertEqual(
            tuple(
                item.policy.component
                for item in readiness[-1].missing_mandatory_components
            ),
            (OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,),
        )
        derived = next(
            item
            for item in readiness[0].resolved_mandatory_components
            if item.policy.component is OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE
        )
        self.assertIsInstance(derived.result, DerivedBalanceSheetValue)

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
        with patch.object(
            operating_nwc_module,
            "OPERATING_NWC_VALUATION_POLICIES",
            tuple(reversed(operating_nwc_module.OPERATING_NWC_VALUATION_POLICIES)),
        ):
            self.assertIs(
                operating_nwc_valuation_policy_for_cik(1326801),
                META_OPERATING_NWC_VALUATION_POLICY,
            )

    def test_builtin_policy_lookup_and_versioned_perimeters(self) -> None:
        expected = {
            1326801: (
                (
                    OperatingNWCComponent.OPERATING_RECEIVABLES,
                    OperatingNWCComponent.TRADE_ACCOUNTS_PAYABLE,
                    OperatingNWCComponent.CUSTOMER_CONTRACT_LIABILITIES,
                    OperatingNWCComponent.EMPLOYEE_RELATED_LIABILITIES,
                ),
                (),
                (
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
                self.assertEqual(policy.version, "1")
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
