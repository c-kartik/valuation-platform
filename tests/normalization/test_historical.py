import gc
from datetime import date, datetime, timezone
from unittest import TestCase
import weakref

from valuation_platform.normalization import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    DerivationOperation,
    DerivedHistoricalValue,
    EvidenceSourceKind,
    FinancialMetric,
    HistoricalPeriod,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedHistoricalValue,
    normalize_annual_financials,
)
from valuation_platform.sec.company_facts import SECFactObservation
from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationRelationship,
    SelectedFactObservation,
    SelectedFactObservations,
)
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity


RETRIEVED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)
RFC = "RevenueFromContractWithCustomerExcludingAssessedTax"
REVENUES = "Revenues"
OPERATING_INCOME = "OperatingIncomeLoss"
D_AND_A = "DepreciationDepletionAndAmortization"
CAPEX = "PaymentsToAcquirePropertyPlantAndEquipment"


def make_filing(
    accession: str = "annual",
    report_date: date | None = date(2025, 12, 31),
) -> SECFiling:
    return SECFiling(
        accession_number=accession,
        form="10-K",
        filing_date=date(2026, 2, 1),
        report_date=report_date,
        primary_document="annual.htm",
    )


def make_selected(
    concept: str,
    *,
    accession: str = "annual",
    value: object = 1,
    unit: str = "USD",
    start: date | None = date(2025, 1, 1),
    end: date = date(2025, 12, 31),
    relationship: ObservationRelationship = ObservationRelationship.CURRENT,
    taxonomy: str = "us-gaap",
) -> SelectedFactObservation:
    observation = SECFactObservation(
        unit=unit,
        value=value,  # type: ignore[arg-type]
        start=start,
        end=end,
        accession_number=accession,
        fiscal_year=2025,
        fiscal_period="FY",
        form="10-K",
        filed=date(2026, 2, 1),
        frame="CY2025",
    )
    return SelectedFactObservation(
        taxonomy=taxonomy,
        concept=concept,
        observation=observation,
        relationship=relationship,
    )


def make_input(
    *observations: SelectedFactObservation,
    filing: SECFiling | None = None,
    additional_filings: tuple[FilingFactObservations, ...] = (),
    company_cik: int = 1,
) -> SelectedFactObservations:
    company = SECCompanyIdentity(
        ticker="TEST",
        cik=company_cik,
        cik_padded=f"{company_cik:010d}",
        company_name="Test Company",
        source_url="ticker-source",
        retrieved_at=RETRIEVED_AT,
    )
    bucket = FilingFactObservations(
        filing=filing or make_filing(),
        observations=tuple(observations),
    )
    return SelectedFactObservations(
        company=company,
        source_url="facts-source",
        retrieved_at=RETRIEVED_AT,
        annual=(bucket, *additional_filings),
        interim=(),
    )


def metric_result(
    selected: SelectedFactObservations,
    metric: FinancialMetric,
):
    result = normalize_annual_financials(selected)
    return next(item for item in result.annual[0].metrics if item.metric is metric)


class AnnualHistoricalNormalizationTests(TestCase):
    def test_rfc_revenue_resolves_with_compact_provenance(self) -> None:
        selected = make_input(make_selected(RFC, value=100))

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 100)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.period.start, date(2025, 1, 1))
        self.assertEqual(result.period.end, date(2025, 12, 31))
        self.assertEqual(result.chosen_source.concept, RFC)
        self.assertIs(
            result.chosen_source.source_kind,
            EvidenceSourceKind.COMPANY_FACTS,
        )
        self.assertEqual(result.chosen_source.source_url, "facts-source")
        self.assertEqual(result.chosen_source.accession_number, "annual")
        self.assertEqual(result.chosen_source.observation_form, "10-K")
        self.assertEqual(result.chosen_source.fiscal_year, 2025)
        self.assertEqual(result.chosen_source.fiscal_period, "FY")
        self.assertEqual(result.chosen_source.frame, "CY2025")
        self.assertEqual(result.confirming_sources, ())

    def test_revenues_fallback_resolves_when_rfc_is_not_valid(self) -> None:
        selected = make_input(
            make_selected(
                RFC,
                value=90,
                end=date(2024, 12, 31),
                relationship=ObservationRelationship.COMPARATIVE,
            ),
            make_selected(REVENUES, value=100),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 100)
        self.assertEqual(result.chosen_source.concept, REVENUES)

    def test_zero_rfc_does_not_trigger_fallback(self) -> None:
        selected = make_input(
            make_selected(RFC, value=0),
            make_selected(REVENUES, value=0),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 0)
        self.assertEqual(result.chosen_source.concept, RFC)
        self.assertEqual(result.confirming_sources[0].concept, REVENUES)

    def test_equal_revenue_candidates_retain_confirmation(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100),
            make_selected(REVENUES, value=100),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.chosen_source.concept, RFC)
        self.assertEqual(
            tuple(source.concept for source in result.confirming_sources),
            (REVENUES,),
        )

    def test_conflicting_revenue_candidates_are_ambiguous(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100),
            make_selected(REVENUES, value=101),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.CONFLICTING_CONCEPT_VALUES)
        self.assertEqual(
            tuple(candidate.concept for candidate in result.candidates),
            (RFC, REVENUES),
        )

    def test_operating_income_resolves(self) -> None:
        result = metric_result(
            make_input(make_selected(OPERATING_INCOME, value=40)),
            FinancialMetric.OPERATING_INCOME,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 40)
        self.assertEqual(result.chosen_source.concept, OPERATING_INCOME)

    def test_direct_d_and_a_resolves_with_exact_provenance(self) -> None:
        result = metric_result(
            make_input(make_selected(D_AND_A, value=18_616_000_000)),
            FinancialMetric.D_AND_A,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertIs(result.metric, FinancialMetric.D_AND_A)
        self.assertEqual(result.value, 18_616_000_000)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(
            result.period,
            HistoricalPeriod(date(2025, 1, 1), date(2025, 12, 31)),
        )
        self.assertEqual(result.chosen_source.taxonomy, "us-gaap")
        self.assertEqual(result.chosen_source.concept, D_AND_A)
        self.assertEqual(result.chosen_source.accession_number, "annual")
        self.assertEqual(result.confirming_sources, ())

    def test_zero_direct_d_and_a_is_valid(self) -> None:
        result = metric_result(
            make_input(make_selected(D_AND_A, value=0)),
            FinancialMetric.D_AND_A,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 0)

    def test_unapproved_d_and_a_concepts_are_not_fallbacks(self) -> None:
        cases = (
            ("us-gaap", "Depreciation"),
            ("us-gaap", "AmortizationOfIntangibleAssets"),
            (
                "goog",
                "DepreciationAndImpairmentOnDispositionOfPropertyAndEquipment",
            ),
            ("goog", "AmortizationAndImpairmentOfIntangibleAssets"),
            ("msft", "DepreciationAmortizationAndOther"),
            ("us-gaap", "FinanceLeaseRightOfUseAssetAmortization"),
        )

        for taxonomy, concept in cases:
            with self.subTest(taxonomy=taxonomy, concept=concept):
                result = metric_result(
                    make_input(make_selected(concept, taxonomy=taxonomy)),
                    FinancialMetric.D_AND_A,
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
                )

    def test_invalid_direct_d_and_a_observations_are_missing(self) -> None:
        cases = (
            make_selected(
                D_AND_A,
                relationship=ObservationRelationship.COMPARATIVE,
                end=date(2024, 12, 31),
            ),
            make_selected(D_AND_A, start=None),
            make_selected(D_AND_A, unit="EUR"),
            make_selected(D_AND_A, value="100"),
            make_selected(D_AND_A, value=True),
        )

        for observation in cases:
            with self.subTest(observation=observation):
                result = metric_result(
                    make_input(observation), FinancialMetric.D_AND_A
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
                )

    def test_direct_d_and_a_preserves_non_calendar_and_week_based_periods(self) -> None:
        periods = (
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2024, 9, 29), date(2025, 9, 27)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )

        for start, end in periods:
            with self.subTest(start=start, end=end):
                result = metric_result(
                    make_input(
                        make_selected(D_AND_A, start=start, end=end),
                        filing=make_filing(report_date=end),
                    ),
                    FinancialMetric.D_AND_A,
                )
                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.period, HistoricalPeriod(start, end))

    def test_msft_d_and_a_derives_from_approved_components(self) -> None:
        result = metric_result(
            make_input(
                make_selected("Depreciation", value=22_000_000_000),
                make_selected(
                    "AmortizationOfIntangibleAssets",
                    value=6_000_000_000,
                ),
                company_cik=789019,
            ),
            FinancialMetric.D_AND_A,
        )

        self.assertIsInstance(result, DerivedHistoricalValue)
        assert isinstance(result, DerivedHistoricalValue)
        self.assertEqual(result.value, 28_000_000_000)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(
            result.period,
            HistoricalPeriod(date(2025, 1, 1), date(2025, 12, 31)),
        )
        self.assertEqual(result.policy_id, "msft_annual_d_and_a_v1")
        self.assertIs(result.operation, DerivationOperation.ADD)
        self.assertEqual(
            tuple(operand.concept for operand in result.operands),
            ("Depreciation", "AmortizationOfIntangibleAssets"),
        )
        self.assertTrue(
            all(
                operand.source_kind is EvidenceSourceKind.COMPANY_FACTS
                and operand.source_url == "facts-source"
                and operand.accession_number == "annual"
                for operand in result.operands
            )
        )

    def test_msft_derivation_requires_complete_valid_operands(self) -> None:
        cases = (
            (make_selected("Depreciation", value=10),),
            (
                make_selected("Depreciation", value=10),
                make_selected("AmortizationOfIntangibleAssets", unit="EUR"),
            ),
            (
                make_selected("Depreciation", value=10),
                make_selected("AmortizationOfIntangibleAssets", value=True),
            ),
            (
                make_selected("Depreciation", value=10),
                make_selected("AmortizationOfIntangibleAssets", value="2"),
            ),
        )

        for observations in cases:
            with self.subTest(observations=observations):
                result = metric_result(
                    make_input(*observations, company_cik=789019),
                    FinancialMetric.D_AND_A,
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_VALID_DERIVATION_OPERANDS,
                )

    def test_msft_derivation_preserves_ambiguous_operand_candidates(self) -> None:
        depreciation_candidates = (
            make_selected(
                "Depreciation",
                value=22,
                start=date(2025, 1, 1),
            ),
            make_selected(
                "Depreciation",
                value=21,
                start=date(2025, 2, 1),
            ),
        )
        amortization = make_selected("AmortizationOfIntangibleAssets", value=6)

        for ordered_candidates in (
            depreciation_candidates,
            tuple(reversed(depreciation_candidates)),
        ):
            with self.subTest(ordered_candidates=ordered_candidates):
                result = metric_result(
                    make_input(
                        *ordered_candidates,
                        amortization,
                        company_cik=789019,
                    ),
                    FinancialMetric.D_AND_A,
                )

                self.assertIsInstance(result, AmbiguousHistoricalMetric)
                assert isinstance(result, AmbiguousHistoricalMetric)
                self.assertIs(
                    result.reason,
                    AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
                )
                self.assertEqual(
                    {
                        (candidate.concept, candidate.value, candidate.start)
                        for candidate in result.candidates
                    },
                    {
                        ("Depreciation", 22, date(2025, 1, 1)),
                        ("Depreciation", 21, date(2025, 2, 1)),
                    },
                )

    def test_msft_derivation_rejects_mismatched_economic_periods(self) -> None:
        result = metric_result(
            make_input(
                make_selected("Depreciation", value=10),
                make_selected(
                    "AmortizationOfIntangibleAssets",
                    value=2,
                    start=date(2025, 2, 1),
                ),
                company_cik=789019,
            ),
            FinancialMetric.D_AND_A,
        )

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(
            result.reason,
            AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
        )
        self.assertEqual(len(result.candidates), 2)

    def test_direct_d_and_a_takes_precedence_for_msft_cik(self) -> None:
        result = metric_result(
            make_input(
                make_selected(D_AND_A, value=30),
                make_selected("Depreciation", value=22),
                make_selected("AmortizationOfIntangibleAssets", value=6),
                company_cik=789019,
            ),
            FinancialMetric.D_AND_A,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 30)
        self.assertEqual(result.chosen_source.concept, D_AND_A)

    def test_validated_issuer_ciks_keep_direct_d_and_a_behavior(self) -> None:
        cases = (
            (1326801, 18_616_000_000),
            (320193, 11_698_000_000),
            (909832, 2_426_000_000),
        )

        for cik, value in cases:
            with self.subTest(cik=cik):
                result = metric_result(
                    make_input(
                        make_selected(D_AND_A, value=value),
                        company_cik=cik,
                    ),
                    FinancialMetric.D_AND_A,
                )
                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.value, value)
                self.assertEqual(result.chosen_source.concept, D_AND_A)

    def test_direct_d_and_a_ambiguity_is_not_overridden(self) -> None:
        result = metric_result(
            make_input(
                make_selected(D_AND_A, value=30),
                make_selected(D_AND_A, value=29, start=date(2025, 2, 1)),
                make_selected("Depreciation", value=22),
                make_selected("AmortizationOfIntangibleAssets", value=6),
                company_cik=789019,
            ),
            FinancialMetric.D_AND_A,
        )

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)

    def test_d_and_a_derivation_is_scoped_to_msft_cik(self) -> None:
        components = (
            make_selected("Depreciation", value=22),
            make_selected("AmortizationOfIntangibleAssets", value=6),
        )

        for cik in (1, 1652044):
            with self.subTest(cik=cik):
                result = metric_result(
                    make_input(*components, company_cik=cik),
                    FinancialMetric.D_AND_A,
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
                )

    def test_capex_resolves_as_positive_magnitude_with_provenance(self) -> None:
        result = metric_result(
            make_input(make_selected(CAPEX, value=31_431_000_000)),
            FinancialMetric.CAPEX,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 31_431_000_000)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.chosen_source.taxonomy, "us-gaap")
        self.assertEqual(result.chosen_source.concept, CAPEX)
        self.assertEqual(result.chosen_source.accession_number, "annual")

    def test_zero_capex_is_valid(self) -> None:
        result = metric_result(
            make_input(make_selected(CAPEX, value=0)),
            FinancialMetric.CAPEX,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 0)

    def test_unapproved_capex_concept_is_not_a_fallback(self) -> None:
        result = metric_result(
            make_input(make_selected("PaymentsToAcquireProductiveAssets", value=10)),
            FinancialMetric.CAPEX,
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_invalid_capex_observations_are_missing(self) -> None:
        cases = (
            make_selected(
                CAPEX,
                relationship=ObservationRelationship.COMPARATIVE,
                end=date(2024, 12, 31),
            ),
            make_selected(CAPEX, start=None),
            make_selected(CAPEX, unit="EUR"),
            make_selected(CAPEX, value="100"),
            make_selected(CAPEX, value=True),
        )

        for observation in cases:
            with self.subTest(observation=observation):
                result = metric_result(
                    make_input(observation), FinancialMetric.CAPEX
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
                )

    def test_capex_preserves_non_calendar_and_week_based_periods(self) -> None:
        periods = (
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2024, 9, 29), date(2025, 9, 27)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )

        for start, end in periods:
            with self.subTest(start=start, end=end):
                result = metric_result(
                    make_input(
                        make_selected(CAPEX, start=start, end=end),
                        filing=make_filing(report_date=end),
                    ),
                    FinancialMetric.CAPEX,
                )
                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.period, HistoricalPeriod(start, end))

    def test_no_configured_concept_is_missing(self) -> None:
        result = metric_result(
            make_input(make_selected("OtherConcept")),
            FinancialMetric.REVENUE,
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_invalid_annual_shapes_are_missing(self) -> None:
        cases = (
            make_selected(
                RFC,
                relationship=ObservationRelationship.COMPARATIVE,
                end=date(2024, 12, 31),
            ),
            make_selected(
                RFC,
                relationship=ObservationRelationship.AFTER_REPORT_DATE,
                end=date(2026, 1, 15),
            ),
            make_selected(RFC, start=None),
            make_selected(RFC, unit="EUR"),
            make_selected(RFC, value="100"),
            make_selected(RFC, value=True),
        )

        for observation in cases:
            with self.subTest(observation=observation):
                result = metric_result(
                    make_input(observation), FinancialMetric.REVENUE
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
                )

    def test_multiple_valid_starts_are_ambiguous(self) -> None:
        selected = make_input(
            make_selected(RFC, start=date(2025, 1, 1)),
            make_selected(REVENUES, start=date(2025, 2, 1)),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)
        self.assertEqual(len(result.candidates), 2)

    def test_non_usd_candidate_does_not_conflict_with_usd_candidate(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100, unit="USD"),
            make_selected(REVENUES, value=101, unit="EUR"),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 100)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.chosen_source.concept, RFC)
        self.assertEqual(result.confirming_sources, ())

    def test_non_usd_primary_does_not_prevent_usd_fallback(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100, unit="EUR"),
            make_selected(REVENUES, value=101, unit="USD"),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 101)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.chosen_source.concept, REVENUES)
        self.assertEqual(result.confirming_sources, ())

    def test_calendar_non_calendar_and_week_based_periods_are_preserved(self) -> None:
        cases = (
            (date(2025, 1, 1), date(2025, 12, 31)),
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2024, 9, 2), date(2025, 8, 31)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )

        for start, end in cases:
            with self.subTest(start=start, end=end):
                filing = make_filing(report_date=end)
                result = metric_result(
                    make_input(
                        make_selected(RFC, start=start, end=end),
                        filing=filing,
                    ),
                    FinancialMetric.REVENUE,
                )
                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.period.start, start)
                self.assertEqual(result.period.end, end)

    def test_missing_capex_does_not_prevent_other_metrics(self) -> None:
        output = normalize_annual_financials(
            make_input(
                make_selected(RFC, value=100),
                make_selected(OPERATING_INCOME, value=40),
            )
        )

        revenue, operating_income, d_and_a, capex = output.annual[0].metrics
        self.assertIsInstance(revenue, NormalizedHistoricalValue)
        self.assertIsInstance(operating_income, NormalizedHistoricalValue)
        self.assertIsInstance(d_and_a, MissingHistoricalMetric)
        self.assertIsInstance(capex, MissingHistoricalMetric)

    def test_missing_d_and_a_does_not_prevent_other_direct_metrics(self) -> None:
        output = normalize_annual_financials(
            make_input(
                make_selected(RFC, value=100),
                make_selected(OPERATING_INCOME, value=40),
                make_selected(CAPEX, value=20),
            )
        )

        revenue, operating_income, d_and_a, capex = output.annual[0].metrics
        self.assertIsInstance(revenue, NormalizedHistoricalValue)
        self.assertIsInstance(operating_income, NormalizedHistoricalValue)
        self.assertIsInstance(d_and_a, MissingHistoricalMetric)
        self.assertIsInstance(capex, NormalizedHistoricalValue)

    def test_missing_revenue_does_not_prevent_operating_income(self) -> None:
        output = normalize_annual_financials(
            make_input(make_selected(OPERATING_INCOME, value=40))
        )

        revenue, operating_income, _, _ = output.annual[0].metrics
        self.assertIsInstance(revenue, MissingHistoricalMetric)
        self.assertIsInstance(operating_income, NormalizedHistoricalValue)

    def test_metric_and_filing_order_is_deterministic(self) -> None:
        first = make_filing("first", date(2024, 12, 31))
        second = make_filing("second", date(2025, 12, 31))
        first_bucket = FilingFactObservations(
            filing=first,
            observations=(
                make_selected(
                    RFC,
                    accession="first",
                    start=date(2024, 1, 1),
                    end=date(2024, 12, 31),
                ),
            ),
        )
        selected = make_input(
            make_selected(RFC, accession="second"),
            filing=second,
            additional_filings=(first_bucket,),
        )

        output = normalize_annual_financials(selected)

        self.assertEqual(
            tuple(item.filing.accession_number for item in output.annual),
            ("second", "first"),
        )
        self.assertEqual(
            tuple(item.metric for item in output.annual[0].metrics),
            (
                FinancialMetric.REVENUE,
                FinancialMetric.OPERATING_INCOME,
                FinancialMetric.D_AND_A,
                FinancialMetric.CAPEX,
            ),
        )

    def test_output_owns_only_compact_copied_evidence(self) -> None:
        observation = make_selected(RFC, value=100)
        selected = make_input(observation)
        selected_reference = weakref.ref(selected)
        bucket_reference = weakref.ref(selected.annual[0])
        observation_reference = weakref.ref(observation)

        output = normalize_annual_financials(selected)
        del selected
        del observation
        gc.collect()

        self.assertIsNone(selected_reference())
        self.assertIsNone(bucket_reference())
        self.assertIsNone(observation_reference())
        self.assertEqual(output.company.ticker, "TEST")
        self.assertEqual(output.company_facts_source_url, "facts-source")
        self.assertEqual(output.company_facts_retrieved_at, RETRIEVED_AT)
        normalized = output.annual[0].metrics[0]
        self.assertIsInstance(normalized, NormalizedHistoricalValue)
        assert isinstance(normalized, NormalizedHistoricalValue)
        self.assertEqual(normalized.chosen_source.value, 100)
