import gc
from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest import TestCase
import weakref

from valuation_platform.normalization import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    CAPEX_POLICY,
    DerivationOperation,
    DerivationDiagnostic,
    DerivedHistoricalValue,
    FactEvidence,
    EvidenceSourceKind,
    FinancialMetric,
    HistoricalPeriod,
    INCOME_TAX_EXPENSE_POLICY,
    MissingHistoricalMetric,
    MissingReason,
    NormalizationError,
    NormalizedHistoricalValue,
    PRETAX_INCOME_POLICY,
    REVENUE_POLICY,
    derive_reported_effective_tax_rate,
    normalize_annual_financials,
)
from valuation_platform.sec.company_facts import SECFactObservation
from valuation_platform.sec import (
    AmbiguousAnnualPeriod,
    AnnualPeriodDataErrorResult,
    AnnualPeriodDEIEvidence,
    AnnualPeriodEvidenceTuple,
    AnnualPeriodFilingEvidence,
    AnnualPeriodNotFound,
    ResolvedAnnualPeriod,
    UnsupportedAnnualPeriod,
)
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
PRETAX_INCOME = (
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
    "ExtraordinaryItemsNoncontrollingInterest"
)
INCOME_TAX_EXPENSE = "IncomeTaxExpenseBenefit"
D_AND_A = "DepreciationDepletionAndAmortization"
CAPEX = "PaymentsToAcquirePropertyPlantAndEquipment"
DILUTED_SHARES = "WeightedAverageNumberOfDilutedSharesOutstanding"


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
    *,
    annual_periods=(),
):
    result = normalize_annual_financials(
        selected,
        annual_periods=annual_periods,
    )
    return next(item for item in result.annual[0].metrics if item.metric is metric)


def make_annual_period(
    *,
    start: date = date(2025, 1, 1),
    end: date = date(2025, 12, 31),
    accession: str = "annual",
    company_cik: int = 1,
) -> ResolvedAnnualPeriod:
    filing = make_filing(accession=accession, report_date=end)
    filing_evidence = AnnualPeriodFilingEvidence(
        registrant_cik=company_cik,
        accession_number=accession,
        form=filing.form,
        report_date=end,
        filing_date=filing.filing_date,
        primary_document=filing.primary_document,
        source_url="filing-xbrl-source",
        retrieved_at=RETRIEVED_AT,
    )
    evidence = AnnualPeriodEvidenceTuple(
        entity_identifier_scheme="http://www.sec.gov/CIK",
        entity_identifier_values=(f"{company_cik:010d}",),
        registrant_cik=company_cik,
        start=start,
        end=end,
        dimensions=(),
        context_ids=("annual-context",),
        dei_evidence=(
            AnnualPeriodDEIEvidence("DocumentFiscalPeriodFocus", "FY", ()),
            AnnualPeriodDEIEvidence("DocumentFiscalYearFocus", str(end.year), ()),
            AnnualPeriodDEIEvidence("DocumentPeriodEndDate", end.isoformat(), ()),
        ),
    )
    return ResolvedAnnualPeriod(filing=filing_evidence, evidence=evidence)


def unresolved_annual_period(
    result_type,
    *,
    accession: str = "annual",
    end: date = date(2025, 12, 31),
):
    resolved = make_annual_period(accession=accession, end=end)
    if result_type is AnnualPeriodNotFound:
        return AnnualPeriodNotFound(resolved.filing, "not found")
    if result_type is AmbiguousAnnualPeriod:
        return AmbiguousAnnualPeriod(
            resolved.filing,
            (
                resolved.evidence,
                replace(resolved.evidence, start=date(2025, 2, 1)),
            ),
        )
    if result_type is AnnualPeriodDataErrorResult:
        return AnnualPeriodDataErrorResult(resolved.filing, "contradictory DEI")
    if result_type is UnsupportedAnnualPeriod:
        return UnsupportedAnnualPeriod(resolved.filing, "unsupported artifact")
    raise AssertionError("Unsupported test result type")


def make_normalized_value(
    metric: FinancialMetric,
    value: object,
    *,
    unit: str = "USD",
    start: date = date(2025, 1, 1),
    end: date = date(2025, 12, 31),
    accession: str = "annual",
    source_url: str = "facts-source",
) -> NormalizedHistoricalValue:
    concept = {
        FinancialMetric.PRETAX_INCOME: PRETAX_INCOME,
        FinancialMetric.INCOME_TAX_EXPENSE: INCOME_TAX_EXPENSE,
    }[metric]
    evidence = FactEvidence(
        source_kind=EvidenceSourceKind.COMPANY_FACTS,
        source_url=source_url,
        taxonomy="us-gaap",
        concept=concept,
        value=value,  # type: ignore[arg-type]
        unit=unit,
        start=start,
        end=end,
        accession_number=accession,
        observation_form="10-K",
        observation_filed=date(2026, 2, 1),
        fiscal_year=2025,
        fiscal_period="FY",
        frame="CY2025",
    )
    return NormalizedHistoricalValue(
        metric=metric,
        value=value,  # type: ignore[arg-type]
        unit=unit,
        period=HistoricalPeriod(start, end),
        chosen_source=evidence,
        confirming_sources=(),
    )


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

    def test_authoritative_period_resolves_annual_and_q4_revenue_candidates(self) -> None:
        annual_period = make_annual_period()
        cases = (
            (
                make_selected(RFC, value=100),
                make_selected(RFC, value=25, start=date(2025, 10, 1)),
            ),
            (
                make_selected(RFC, value=100),
                make_selected(REVENUES, value=25, start=date(2025, 10, 1)),
            ),
        )
        for observations in cases:
            with self.subTest(concepts=tuple(item.concept for item in observations)):
                output = normalize_annual_financials(
                    make_input(*observations),
                    annual_periods=(annual_period,),
                )
                result = next(
                    item
                    for item in output.annual[0].metrics
                    if item.metric is FinancialMetric.REVENUE
                )

                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.value, 100)
                self.assertEqual(result.period, HistoricalPeriod(date(2025, 1, 1), date(2025, 12, 31)))
                self.assertIs(output.annual[0].annual_period, annual_period)
                self.assertEqual(annual_period.evidence.context_ids, ("annual-context",))

    def test_authoritative_period_preserves_true_revenue_concept_conflict(self) -> None:
        result = metric_result(
            make_input(
                make_selected(RFC, value=100),
                make_selected(REVENUES, value=101),
                make_selected(REVENUES, value=25, start=date(2025, 10, 1)),
            ),
            FinancialMetric.REVENUE,
            annual_periods=(make_annual_period(),),
        )

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.CONFLICTING_CONCEPT_VALUES)
        self.assertEqual(
            tuple(candidate.concept for candidate in result.candidates),
            (RFC, REVENUES),
        )

    def test_unresolved_annual_period_preserves_prior_revenue_ambiguity(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100),
            make_selected(RFC, value=25, start=date(2025, 10, 1)),
        )
        for result_type in (
            AnnualPeriodNotFound,
            AmbiguousAnnualPeriod,
            UnsupportedAnnualPeriod,
        ):
            with self.subTest(result_type=result_type):
                result = metric_result(
                    selected,
                    FinancialMetric.REVENUE,
                    annual_periods=(unresolved_annual_period(result_type),),
                )
                self.assertIsInstance(result, AmbiguousHistoricalMetric)
                assert isinstance(result, AmbiguousHistoricalMetric)
                self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)

    def test_annual_period_data_error_stops_normalization(self) -> None:
        with self.assertRaisesRegex(NormalizationError, "contradictory DEI"):
            normalize_annual_financials(
                make_input(make_selected(RFC, value=100)),
                annual_periods=(
                    unresolved_annual_period(AnnualPeriodDataErrorResult),
                ),
            )

    def test_annual_period_input_must_belong_to_selected_company_and_filing(self) -> None:
        selected = make_input(make_selected(RFC, value=100))
        valid = make_annual_period()
        cases = (
            (valid, valid),
            (replace(valid, filing=replace(valid.filing, registrant_cik=2)),),
            (replace(valid, filing=replace(valid.filing, primary_document="other.htm")),),
            (
                replace(
                    valid,
                    evidence=replace(valid.evidence, end=date(2025, 12, 30)),
                ),
            ),
            (make_annual_period(accession="other"),),
        )
        for annual_periods in cases:
            with self.subTest(annual_periods=annual_periods):
                with self.assertRaises(NormalizationError):
                    normalize_annual_financials(
                        selected,
                        annual_periods=annual_periods,
                    )

    def test_authoritative_period_supports_noncalendar_and_53_week_years(self) -> None:
        periods = (
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )
        for start, end in periods:
            with self.subTest(start=start, end=end):
                filing = make_filing(report_date=end)
                result = metric_result(
                    make_input(
                        make_selected(RFC, value=100, start=start, end=end),
                        make_selected(
                            RFC,
                            value=25,
                            start=end.replace(month=max(1, end.month - 2)),
                            end=end,
                        ),
                        filing=filing,
                    ),
                    FinancialMetric.REVENUE,
                    annual_periods=(make_annual_period(start=start, end=end),),
                )
                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.period, HistoricalPeriod(start, end))

    def test_authoritative_period_filter_is_input_order_independent(self) -> None:
        observations = (
            make_selected(RFC, value=100),
            make_selected(RFC, value=25, start=date(2025, 10, 1)),
            make_selected(REVENUES, value=100),
        )
        annual_period = make_annual_period()

        forward = normalize_annual_financials(
            make_input(*observations),
            annual_periods=(annual_period,),
        )
        reverse = normalize_annual_financials(
            make_input(*reversed(observations)),
            annual_periods=(annual_period,),
        )

        self.assertEqual(forward, reverse)

    def test_authoritative_period_filter_is_limited_to_approved_metrics(self) -> None:
        cases = (
            (OPERATING_INCOME, FinancialMetric.OPERATING_INCOME, "USD"),
            (D_AND_A, FinancialMetric.D_AND_A, "USD"),
            (CAPEX, FinancialMetric.CAPEX, "USD"),
            (
                DILUTED_SHARES,
                FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
                "shares",
            ),
        )
        for concept, metric, unit in cases:
            with self.subTest(metric=metric):
                result = metric_result(
                    make_input(
                        make_selected(concept, value=100, unit=unit),
                        make_selected(
                            concept,
                            value=25,
                            unit=unit,
                            start=date(2025, 10, 1),
                        ),
                    ),
                    metric,
                    annual_periods=(make_annual_period(),),
                )
                self.assertIsInstance(result, AmbiguousHistoricalMetric)
                assert isinstance(result, AmbiguousHistoricalMetric)
                self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)

    def test_operating_income_resolves(self) -> None:
        result = metric_result(
            make_input(make_selected(OPERATING_INCOME, value=40)),
            FinancialMetric.OPERATING_INCOME,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 40)
        self.assertEqual(result.chosen_source.concept, OPERATING_INCOME)

    def test_pretax_income_resolves_with_selected_filing_provenance(self) -> None:
        result = metric_result(
            make_input(make_selected(PRETAX_INCOME, value=85_932_000_000)),
            FinancialMetric.PRETAX_INCOME,
        )

        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.value, 85_932_000_000)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.period, HistoricalPeriod(date(2025, 1, 1), date(2025, 12, 31)))
        self.assertEqual(result.chosen_source.taxonomy, "us-gaap")
        self.assertEqual(result.chosen_source.concept, PRETAX_INCOME)
        self.assertEqual(result.chosen_source.accession_number, "annual")
        self.assertEqual(result.chosen_source.source_url, "facts-source")
        self.assertIs(result.chosen_source.source_kind, EvidenceSourceKind.COMPANY_FACTS)

    def test_pretax_income_preserves_zero_and_negative_values(self) -> None:
        for value in (0, -100):
            with self.subTest(value=value):
                result = metric_result(
                    make_input(make_selected(PRETAX_INCOME, value=value)),
                    FinancialMetric.PRETAX_INCOME,
                )
                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.value, value)

    def test_unapproved_pretax_income_concept_is_not_a_fallback(self) -> None:
        result = metric_result(
            make_input(make_selected("IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments")),
            FinancialMetric.PRETAX_INCOME,
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(result.reason, MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION)

    def test_invalid_pretax_income_observations_are_missing(self) -> None:
        cases = (
            make_selected(PRETAX_INCOME, relationship=ObservationRelationship.COMPARATIVE, end=date(2024, 12, 31)),
            make_selected(PRETAX_INCOME, start=None),
            make_selected(PRETAX_INCOME, unit="EUR"),
            make_selected(PRETAX_INCOME, value="100"),
            make_selected(PRETAX_INCOME, value=True),
        )
        for observation in cases:
            with self.subTest(observation=observation):
                result = metric_result(make_input(observation), FinancialMetric.PRETAX_INCOME)
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(result.reason, MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION)

    def test_income_tax_expense_preserves_expense_zero_and_benefit_signs(self) -> None:
        for value in (25_474_000_000, 0, -5_021_000_000):
            with self.subTest(value=value):
                result = metric_result(
                    make_input(make_selected(INCOME_TAX_EXPENSE, value=value)),
                    FinancialMetric.INCOME_TAX_EXPENSE,
                )
                self.assertIsInstance(result, NormalizedHistoricalValue)
                assert isinstance(result, NormalizedHistoricalValue)
                self.assertEqual(result.value, value)
                self.assertEqual(result.chosen_source.concept, INCOME_TAX_EXPENSE)
                self.assertEqual(result.chosen_source.accession_number, "annual")

    def test_unapproved_income_tax_concept_is_not_a_fallback(self) -> None:
        result = metric_result(
            make_input(make_selected("IncomeTaxExpenseBenefitContinuingOperations")),
            FinancialMetric.INCOME_TAX_EXPENSE,
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(result.reason, MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION)

    def test_invalid_income_tax_expense_observations_are_missing(self) -> None:
        cases = (
            make_selected(INCOME_TAX_EXPENSE, relationship=ObservationRelationship.COMPARATIVE, end=date(2024, 12, 31)),
            make_selected(INCOME_TAX_EXPENSE, start=None),
            make_selected(INCOME_TAX_EXPENSE, unit="EUR"),
            make_selected(INCOME_TAX_EXPENSE, value="100"),
            make_selected(INCOME_TAX_EXPENSE, value=True),
        )
        for observation in cases:
            with self.subTest(observation=observation):
                result = metric_result(make_input(observation), FinancialMetric.INCOME_TAX_EXPENSE)
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(result.reason, MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION)

    def test_tax_metrics_preserve_non_calendar_and_week_based_periods(self) -> None:
        periods = (
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2024, 9, 29), date(2025, 9, 27)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )
        for concept, metric in (
            (PRETAX_INCOME, FinancialMetric.PRETAX_INCOME),
            (INCOME_TAX_EXPENSE, FinancialMetric.INCOME_TAX_EXPENSE),
        ):
            for start, end in periods:
                with self.subTest(metric=metric, start=start, end=end):
                    result = metric_result(
                        make_input(make_selected(concept, start=start, end=end), filing=make_filing(report_date=end)),
                        metric,
                    )
                    self.assertIsInstance(result, NormalizedHistoricalValue)
                    assert isinstance(result, NormalizedHistoricalValue)
                    self.assertEqual(result.period, HistoricalPeriod(start, end))

    def test_authoritative_period_filters_pretax_and_tax_before_etr(self) -> None:
        annual_period = make_annual_period()
        output = normalize_annual_financials(
            make_input(
                make_selected(PRETAX_INCOME, value=100),
                make_selected(
                    PRETAX_INCOME,
                    value=30,
                    start=date(2025, 10, 1),
                ),
                make_selected(INCOME_TAX_EXPENSE, value=20),
                make_selected(
                    INCOME_TAX_EXPENSE,
                    value=6,
                    start=date(2025, 10, 1),
                ),
            ),
            annual_periods=(annual_period,),
        )
        by_metric = {item.metric: item for item in output.annual[0].metrics}

        self.assertEqual(by_metric[FinancialMetric.PRETAX_INCOME].value, 100)
        self.assertEqual(by_metric[FinancialMetric.INCOME_TAX_EXPENSE].value, 20)
        self.assertEqual(
            by_metric[FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE].value,
            Decimal("0.2"),
        )

    def test_unresolved_period_and_same_period_tax_conflict_remain_ambiguous(self) -> None:
        pretax = make_input(
            make_selected(PRETAX_INCOME, value=100),
            make_selected(PRETAX_INCOME, value=30, start=date(2025, 10, 1)),
        )
        unresolved = metric_result(
            pretax,
            FinancialMetric.PRETAX_INCOME,
            annual_periods=(unresolved_annual_period(AnnualPeriodNotFound),),
        )
        same_period = metric_result(
            make_input(
                make_selected(INCOME_TAX_EXPENSE, value=20),
                make_selected(INCOME_TAX_EXPENSE, value=21),
            ),
            FinancialMetric.INCOME_TAX_EXPENSE,
            annual_periods=(make_annual_period(),),
        )

        self.assertIsInstance(unresolved, AmbiguousHistoricalMetric)
        self.assertIsInstance(same_period, AmbiguousHistoricalMetric)

    def test_reported_etr_derives_decimal_with_ordered_operand_provenance(self) -> None:
        pretax = make_normalized_value(FinancialMetric.PRETAX_INCOME, 10)
        tax = make_normalized_value(FinancialMetric.INCOME_TAX_EXPENSE, 1)
        confirming_tax_source = replace(
            tax.chosen_source,
            source_url="confirming-facts-source",
            frame=None,
        )
        tax = replace(tax, confirming_sources=(confirming_tax_source,))

        result = derive_reported_effective_tax_rate(
            "annual",
            date(2025, 12, 31),
            (pretax, tax),
        )

        self.assertIsInstance(result, DerivedHistoricalValue)
        assert isinstance(result, DerivedHistoricalValue)
        self.assertEqual(result.value, Decimal("0.1"))
        self.assertIsInstance(result.value, Decimal)
        self.assertEqual(result.unit, "pure")
        self.assertIs(result.operation, DerivationOperation.DIVIDE)
        self.assertEqual(result.operands, ())
        self.assertEqual(result.diagnostics, ())
        self.assertEqual(
            tuple(operand.metric for operand in result.metric_operands),
            (
                FinancialMetric.INCOME_TAX_EXPENSE,
                FinancialMetric.PRETAX_INCOME,
            ),
        )
        numerator, denominator = result.metric_operands
        self.assertEqual(
            (
                numerator.metric,
                numerator.value,
                numerator.unit,
                numerator.period,
            ),
            (
                FinancialMetric.INCOME_TAX_EXPENSE,
                1,
                "USD",
                HistoricalPeriod(date(2025, 1, 1), date(2025, 12, 31)),
            ),
        )
        self.assertEqual(
            (
                denominator.metric,
                denominator.value,
                denominator.unit,
                denominator.period,
            ),
            (
                FinancialMetric.PRETAX_INCOME,
                10,
                "USD",
                HistoricalPeriod(date(2025, 1, 1), date(2025, 12, 31)),
            ),
        )
        for operand, concept in (
            (numerator, INCOME_TAX_EXPENSE),
            (denominator, PRETAX_INCOME),
        ):
            source = operand.chosen_source
            self.assertIs(source.source_kind, EvidenceSourceKind.COMPANY_FACTS)
            self.assertEqual(source.source_url, "facts-source")
            self.assertEqual(source.taxonomy, "us-gaap")
            self.assertEqual(source.concept, concept)
            self.assertEqual(source.value, operand.value)
            self.assertEqual(source.unit, "USD")
            self.assertEqual(source.start, date(2025, 1, 1))
            self.assertEqual(source.end, date(2025, 12, 31))
            self.assertEqual(source.accession_number, "annual")
            self.assertEqual(source.observation_form, "10-K")
            self.assertEqual(source.observation_filed, date(2026, 2, 1))
            self.assertEqual(source.fiscal_year, 2025)
            self.assertEqual(source.fiscal_period, "FY")
            self.assertEqual(source.frame, "CY2025")
        self.assertEqual(
            numerator.confirming_sources,
            (confirming_tax_source,),
        )
        self.assertEqual(denominator.confirming_sources, ())

    def test_reported_etr_requires_both_configured_direct_policies(self) -> None:
        selected = make_input(
            make_selected(RFC, value=200),
            make_selected(PRETAX_INCOME, value=100),
            make_selected(INCOME_TAX_EXPENSE, value=20),
            make_selected(CAPEX, value=30),
        )
        cases = (
            (
                (INCOME_TAX_EXPENSE_POLICY,),
                (FinancialMetric.INCOME_TAX_EXPENSE,),
            ),
            (
                (PRETAX_INCOME_POLICY,),
                (FinancialMetric.PRETAX_INCOME,),
            ),
            (
                (REVENUE_POLICY, CAPEX_POLICY),
                (FinancialMetric.REVENUE, FinancialMetric.CAPEX),
            ),
        )

        for policies, expected_metrics in cases:
            with self.subTest(policies=policies):
                output = normalize_annual_financials(selected, policies=policies)
                self.assertEqual(
                    tuple(result.metric for result in output.annual[0].metrics),
                    expected_metrics,
                )

    def test_custom_policies_with_both_tax_operands_include_reported_etr(self) -> None:
        output = normalize_annual_financials(
            make_input(
                make_selected(PRETAX_INCOME, value=100),
                make_selected(INCOME_TAX_EXPENSE, value=20),
            ),
            policies=(PRETAX_INCOME_POLICY, INCOME_TAX_EXPENSE_POLICY),
        )

        pretax, tax, reported_etr = output.annual[0].metrics
        self.assertIsInstance(pretax, NormalizedHistoricalValue)
        self.assertIsInstance(tax, NormalizedHistoricalValue)
        self.assertIsInstance(reported_etr, DerivedHistoricalValue)
        assert isinstance(reported_etr, DerivedHistoricalValue)
        self.assertEqual(reported_etr.value, Decimal("0.2"))
        self.assertEqual(
            tuple(result.metric for result in output.annual[0].metrics),
            (
                FinancialMetric.PRETAX_INCOME,
                FinancialMetric.INCOME_TAX_EXPENSE,
                FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
            ),
        )

    def test_custom_tax_policies_include_typed_missing_reported_etr(self) -> None:
        output = normalize_annual_financials(
            make_input(make_selected(PRETAX_INCOME, value=100)),
            policies=(PRETAX_INCOME_POLICY, INCOME_TAX_EXPENSE_POLICY),
        )

        reported_etr = output.annual[0].metrics[-1]
        self.assertIsInstance(reported_etr, MissingHistoricalMetric)
        assert isinstance(reported_etr, MissingHistoricalMetric)
        self.assertIs(
            reported_etr.reason,
            MissingReason.MISSING_DERIVATION_OPERAND,
        )

    def test_reported_etr_preserves_valid_extreme_values(self) -> None:
        cases = (
            (0, 100, Decimal("0")),
            (-20, 100, Decimal("-0.2")),
            (2, 1, Decimal("2")),
            (1, 0.0001, Decimal("1E+4")),
        )
        for tax, pretax, expected in cases:
            with self.subTest(tax=tax, pretax=pretax):
                result = metric_result(
                    make_input(
                        make_selected(PRETAX_INCOME, value=pretax),
                        make_selected(INCOME_TAX_EXPENSE, value=tax),
                    ),
                    FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
                )
                self.assertIsInstance(result, DerivedHistoricalValue)
                assert isinstance(result, DerivedHistoricalValue)
                self.assertEqual(result.value, expected)
                self.assertEqual(result.diagnostics, ())

    def test_negative_pretax_income_has_diagnostic(self) -> None:
        result = metric_result(
            make_input(
                make_selected(PRETAX_INCOME, value=-100),
                make_selected(INCOME_TAX_EXPENSE, value=20),
            ),
            FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
        )

        self.assertIsInstance(result, DerivedHistoricalValue)
        assert isinstance(result, DerivedHistoricalValue)
        self.assertEqual(result.value, Decimal("-0.2"))
        self.assertEqual(
            result.diagnostics,
            (DerivationDiagnostic.NEGATIVE_DENOMINATOR,),
        )

    def test_zero_pretax_income_is_typed_missing(self) -> None:
        result = metric_result(
            make_input(
                make_selected(PRETAX_INCOME, value=0),
                make_selected(INCOME_TAX_EXPENSE, value=20),
            ),
            FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(result.reason, MissingReason.ZERO_DERIVATION_DENOMINATOR)

    def test_missing_reported_etr_operand_is_typed_missing(self) -> None:
        for observation in (
            make_selected(PRETAX_INCOME, value=100),
            make_selected(INCOME_TAX_EXPENSE, value=20),
        ):
            with self.subTest(concept=observation.concept):
                result = metric_result(
                    make_input(observation),
                    FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(result.reason, MissingReason.MISSING_DERIVATION_OPERAND)

    def test_ambiguous_reported_etr_operand_preserves_ambiguity(self) -> None:
        cases = (
            (
                make_selected(PRETAX_INCOME, value=100),
                make_selected(PRETAX_INCOME, value=90, start=date(2025, 2, 1)),
                make_selected(INCOME_TAX_EXPENSE, value=20),
            ),
            (
                make_selected(PRETAX_INCOME, value=100),
                make_selected(INCOME_TAX_EXPENSE, value=20),
                make_selected(INCOME_TAX_EXPENSE, value=19, start=date(2025, 2, 1)),
            ),
        )
        for observations in cases:
            with self.subTest(observations=observations):
                result = metric_result(
                    make_input(*observations),
                    FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
                )
                self.assertIsInstance(result, AmbiguousHistoricalMetric)
                assert isinstance(result, AmbiguousHistoricalMetric)
                self.assertIs(result.reason, AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS)
                self.assertEqual(len(result.candidates), 2)

    def test_reported_etr_rejects_mismatched_economic_periods(self) -> None:
        result = metric_result(
            make_input(
                make_selected(PRETAX_INCOME, value=100),
                make_selected(INCOME_TAX_EXPENSE, value=20, start=date(2025, 2, 1)),
            ),
            FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
        )

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS)

    def test_reported_etr_validates_normalized_operand_structure(self) -> None:
        pretax = make_normalized_value(FinancialMetric.PRETAX_INCOME, 100)
        cases = (
            (
                make_normalized_value(
                    FinancialMetric.INCOME_TAX_EXPENSE,
                    20,
                    accession="other",
                ),
                pretax,
            ),
            (
                make_normalized_value(
                    FinancialMetric.INCOME_TAX_EXPENSE,
                    20,
                    unit="EUR",
                ),
                pretax,
            ),
        )
        for numerator, denominator in cases:
            with self.subTest(numerator=numerator):
                result = derive_reported_effective_tax_rate(
                    "annual",
                    date(2025, 12, 31),
                    (denominator, numerator),
                )
                self.assertIsInstance(result, AmbiguousHistoricalMetric)
                assert isinstance(result, AmbiguousHistoricalMetric)
                self.assertIs(result.reason, AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS)

    def test_reported_etr_allows_independent_operand_source_urls(self) -> None:
        result = derive_reported_effective_tax_rate(
            "annual",
            date(2025, 12, 31),
            (
                make_normalized_value(
                    FinancialMetric.PRETAX_INCOME,
                    100,
                    source_url="pretax-source",
                ),
                make_normalized_value(
                    FinancialMetric.INCOME_TAX_EXPENSE,
                    20,
                    source_url="tax-source",
                ),
            ),
        )

        self.assertIsInstance(result, DerivedHistoricalValue)
        assert isinstance(result, DerivedHistoricalValue)
        self.assertEqual(result.value, Decimal("0.2"))
        self.assertEqual(
            tuple(
                operand.chosen_source.source_url
                for operand in result.metric_operands
            ),
            ("tax-source", "pretax-source"),
        )

    def test_reported_etr_accepts_only_direct_normalized_operands(self) -> None:
        direct_pretax = make_normalized_value(FinancialMetric.PRETAX_INCOME, 100)
        derived_pretax = DerivedHistoricalValue(
            metric=FinancialMetric.PRETAX_INCOME,
            value=100,
            unit="USD",
            period=direct_pretax.period,
            policy_id="synthetic",
            operation=DerivationOperation.ADD,
            operands=(direct_pretax.chosen_source,),
        )
        result = derive_reported_effective_tax_rate(
            "annual",
            date(2025, 12, 31),
            (
                derived_pretax,
                make_normalized_value(FinancialMetric.INCOME_TAX_EXPENSE, 20),
            ),
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(result.reason, MissingReason.NO_VALID_DERIVATION_OPERANDS)

    def test_calculated_reported_etr_only_matches_disclosed_rate_after_rounding(self) -> None:
        result = metric_result(
            make_input(
                make_selected(PRETAX_INCOME, value=47_284_000_000),
                make_selected(INCOME_TAX_EXPENSE, value=7_914_000_000),
                make_selected(
                    "EffectiveIncomeTaxRateContinuingOperations",
                    value=0.167,
                    unit="pure",
                ),
            ),
            FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
        )

        self.assertIsInstance(result, DerivedHistoricalValue)
        assert isinstance(result, DerivedHistoricalValue)
        self.assertNotEqual(result.value, Decimal("0.167"))
        self.assertEqual(result.value.quantize(Decimal("0.001")), Decimal("0.167"))
        self.assertEqual(
            tuple(operand.metric for operand in result.metric_operands),
            (
                FinancialMetric.INCOME_TAX_EXPENSE,
                FinancialMetric.PRETAX_INCOME,
            ),
        )

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

    def test_q4_only_diluted_shares_does_not_establish_annual_period(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100, start=date(2025, 1, 1)),
            make_selected(RFC, value=25, start=date(2025, 10, 1)),
            make_selected(
                DILUTED_SHARES,
                value=10,
                unit="shares",
                start=date(2025, 10, 1),
            ),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)
        self.assertEqual(tuple(item.value for item in result.candidates), (100, 25))
        self.assertNotEqual(getattr(result, "value", None), 25)

    def test_unique_diluted_share_period_does_not_choose_revenue_period(self) -> None:
        annual_start = date(2024, 7, 1)
        report_date = date(2025, 6, 30)
        filing = make_filing(report_date=report_date)
        observations = (
            make_selected(RFC, value=25, start=date(2025, 4, 1), end=report_date),
            make_selected(REVENUES, value=100, start=annual_start, end=report_date),
            make_selected(
                DILUTED_SHARES,
                value=10,
                unit="shares",
                start=annual_start,
                end=report_date,
            ),
        )

        results = []
        for ordered in (observations, tuple(reversed(observations))):
            with self.subTest(order=ordered):
                result = metric_result(
                    make_input(*ordered, filing=filing),
                    FinancialMetric.REVENUE,
                )
                self.assertIsInstance(result, AmbiguousHistoricalMetric)
                assert isinstance(result, AmbiguousHistoricalMetric)
                self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)
                results.append(result)
        self.assertEqual(results[0], results[1])

    def test_diluted_shares_does_not_hide_full_year_concept_conflict(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100),
            make_selected(REVENUES, value=101),
            make_selected(DILUTED_SHARES, value=10, unit="shares"),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.CONFLICTING_CONCEPT_VALUES)
        self.assertEqual(tuple(item.value for item in result.candidates), (100, 101))

    def test_multiple_diluted_share_periods_do_not_choose_annuality(self) -> None:
        observations = (
            make_selected(RFC, value=100, start=date(2025, 1, 1)),
            make_selected(REVENUES, value=25, start=date(2025, 10, 1)),
            make_selected(
                DILUTED_SHARES,
                value=10,
                unit="shares",
                start=date(2025, 1, 1),
            ),
            make_selected(
                DILUTED_SHARES,
                value=3,
                unit="shares",
                start=date(2025, 10, 1),
            ),
        )
        results = tuple(
            metric_result(make_input(*ordered), FinancialMetric.REVENUE)
            for ordered in (observations, tuple(reversed(observations)))
        )

        self.assertEqual(results[0], results[1])
        for result in results:
            self.assertIsInstance(result, AmbiguousHistoricalMetric)
            assert isinstance(result, AmbiguousHistoricalMetric)
            self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)

    def test_wrong_accession_diluted_share_observation_is_rejected(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100, start=date(2025, 1, 1)),
            make_selected(RFC, value=25, start=date(2025, 10, 1)),
            make_selected(
                DILUTED_SHARES,
                accession="other",
                value=10,
                unit="shares",
                start=date(2025, 1, 1),
            ),
        )

        with self.assertRaisesRegex(NormalizationError, "does not match filing"):
            metric_result(selected, FinancialMetric.REVENUE)

    def test_comparative_diluted_share_observation_does_not_choose_period(self) -> None:
        selected = make_input(
            make_selected(RFC, value=100, start=date(2025, 1, 1)),
            make_selected(RFC, value=25, start=date(2025, 10, 1)),
            make_selected(
                DILUTED_SHARES,
                value=10,
                unit="shares",
                start=date(2025, 1, 1),
                relationship=ObservationRelationship.COMPARATIVE,
            ),
        )

        result = metric_result(selected, FinancialMetric.REVENUE)

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS)

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

        by_metric = {result.metric: result for result in output.annual[0].metrics}
        revenue = by_metric[FinancialMetric.REVENUE]
        operating_income = by_metric[FinancialMetric.OPERATING_INCOME]
        pretax = by_metric[FinancialMetric.PRETAX_INCOME]
        tax = by_metric[FinancialMetric.INCOME_TAX_EXPENSE]
        etr = by_metric[FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE]
        d_and_a = by_metric[FinancialMetric.D_AND_A]
        capex = by_metric[FinancialMetric.CAPEX]
        self.assertIsInstance(revenue, NormalizedHistoricalValue)
        self.assertIsInstance(operating_income, NormalizedHistoricalValue)
        self.assertIsInstance(pretax, MissingHistoricalMetric)
        self.assertIsInstance(tax, MissingHistoricalMetric)
        self.assertIsInstance(etr, MissingHistoricalMetric)
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

        by_metric = {result.metric: result for result in output.annual[0].metrics}
        revenue = by_metric[FinancialMetric.REVENUE]
        operating_income = by_metric[FinancialMetric.OPERATING_INCOME]
        pretax = by_metric[FinancialMetric.PRETAX_INCOME]
        tax = by_metric[FinancialMetric.INCOME_TAX_EXPENSE]
        etr = by_metric[FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE]
        d_and_a = by_metric[FinancialMetric.D_AND_A]
        capex = by_metric[FinancialMetric.CAPEX]
        self.assertIsInstance(revenue, NormalizedHistoricalValue)
        self.assertIsInstance(operating_income, NormalizedHistoricalValue)
        self.assertIsInstance(pretax, MissingHistoricalMetric)
        self.assertIsInstance(tax, MissingHistoricalMetric)
        self.assertIsInstance(etr, MissingHistoricalMetric)
        self.assertIsInstance(d_and_a, MissingHistoricalMetric)
        self.assertIsInstance(capex, NormalizedHistoricalValue)

    def test_missing_revenue_does_not_prevent_operating_income(self) -> None:
        output = normalize_annual_financials(
            make_input(make_selected(OPERATING_INCOME, value=40))
        )

        by_metric = {result.metric: result for result in output.annual[0].metrics}
        revenue = by_metric[FinancialMetric.REVENUE]
        operating_income = by_metric[FinancialMetric.OPERATING_INCOME]
        self.assertIsInstance(revenue, MissingHistoricalMetric)
        self.assertIsInstance(operating_income, NormalizedHistoricalValue)

    def test_missing_tax_metrics_do_not_prevent_other_metrics(self) -> None:
        output = normalize_annual_financials(
            make_input(
                make_selected(RFC, value=100),
                make_selected(OPERATING_INCOME, value=40),
                make_selected(D_AND_A, value=10),
                make_selected(CAPEX, value=20),
            )
        )
        by_metric = {result.metric: result for result in output.annual[0].metrics}
        self.assertIsInstance(by_metric[FinancialMetric.PRETAX_INCOME], MissingHistoricalMetric)
        self.assertIsInstance(by_metric[FinancialMetric.INCOME_TAX_EXPENSE], MissingHistoricalMetric)
        for metric in (FinancialMetric.REVENUE, FinancialMetric.OPERATING_INCOME, FinancialMetric.D_AND_A, FinancialMetric.CAPEX):
            self.assertIsInstance(by_metric[metric], NormalizedHistoricalValue)

    def test_each_missing_tax_metric_does_not_prevent_the_other(self) -> None:
        cases = (
            (PRETAX_INCOME, FinancialMetric.PRETAX_INCOME, FinancialMetric.INCOME_TAX_EXPENSE),
            (INCOME_TAX_EXPENSE, FinancialMetric.INCOME_TAX_EXPENSE, FinancialMetric.PRETAX_INCOME),
        )
        for concept, present, missing in cases:
            with self.subTest(present=present):
                output = normalize_annual_financials(make_input(make_selected(concept, value=10)))
                by_metric = {result.metric: result for result in output.annual[0].metrics}
                self.assertIsInstance(by_metric[present], NormalizedHistoricalValue)
                self.assertIsInstance(by_metric[missing], MissingHistoricalMetric)

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
                FinancialMetric.PRETAX_INCOME,
                FinancialMetric.INCOME_TAX_EXPENSE,
                FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
                FinancialMetric.D_AND_A,
                FinancialMetric.CAPEX,
                FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
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
