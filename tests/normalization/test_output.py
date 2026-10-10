from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal
import json
import unittest

from valuation_platform.normalization import (
    AmbiguousHistoricalMetric,
    AmbiguousOperatingNWCReadinessComponent,
    AmbiguousStandardizedMeasure,
    AmbiguityReason,
    AnnualBalanceSheetFilingResult,
    CalculatedOperatingNWC,
    CalculatedOperatingNWCChange,
    DerivedHistoricalValue,
    DerivedMetricOperand,
    DerivationOperation,
    EvidenceSourceKind,
    FactEvidence,
    FilingXBRLEvidence,
    FinancialMetric,
    HistoricalAvailability,
    HistoricalMeasure,
    HistoricalMeasureKind,
    HistoricalOutputError,
    HistoricalPeriod,
    HistoricalPolicyProvenance,
    HistoricalResolutionKind,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedAnnualBalanceSheets,
    NormalizedBalanceSheetValue,
    NormalizedHistoricalFinancials,
    NormalizedHistoricalValue,
    OperatingNWCCalculationFormula,
    OperatingNWCComponent,
    OperatingNWCComponentContribution,
    OperatingNWCPerimeterComponentPolicy,
    OperatingNWCPerimeterSide,
    OperatingNWCPerimeterTreatment,
    OperatingNWCReadinessResult,
    ResolvedHistoricalMeasure,
    ReviewedPolicyEvidence,
    UnavailableHistoricalMeasure,
    assemble_standardized_annual_history,
    derive_reported_effective_tax_rate,
    standardized_history_to_dict,
)
from valuation_platform.sec import SECCompanyIdentity, SECFiling


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def company(cik: int = 1326801, ticker: str = "META") -> SECCompanyIdentity:
    return SECCompanyIdentity(
        ticker=ticker,
        cik=cik,
        cik_padded=f"{cik:010d}",
        company_name=f"{ticker} Inc.",
        source_url="ticker-source",
        retrieved_at=NOW,
    )


def filing(year: int, *, accession: str | None = None) -> SECFiling:
    return SECFiling(
        accession or f"accession-{year}",
        "10-K",
        date(year + 1, 2, 1),
        date(year, 12, 31),
        f"annual-{year}.htm",
    )


def fact_evidence(
    metric: FinancialMetric,
    selected_filing: SECFiling,
    value: int = 100,
    *,
    unit: str = "USD",
    start: date | None = None,
) -> FactEvidence:
    return FactEvidence(
        EvidenceSourceKind.COMPANY_FACTS,
        "facts-source",
        "us-gaap",
        metric.value,
        value,
        unit,
        start,
        selected_filing.report_date,
        selected_filing.accession_number,
        selected_filing.form,
        selected_filing.filing_date,
        selected_filing.report_date.year,
        "FY",
        None,
    )


def historical_metric(
    metric: FinancialMetric,
    selected_filing: SECFiling,
    value: object = 100,
    *,
    start: date | None = None,
    unit: str | None = None,
):
    assert selected_filing.report_date is not None
    start = start or date(selected_filing.report_date.year, 1, 1)
    if unit is None:
        unit = {
            FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE: "pure",
            FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES: "shares",
        }.get(metric, "USD")
    evidence_value = value if isinstance(value, int) and not isinstance(value, bool) else 1
    return NormalizedHistoricalValue(
        metric,
        value,  # type: ignore[arg-type]
        unit,
        HistoricalPeriod(start, selected_filing.report_date),
        fact_evidence(
            metric,
            selected_filing,
            evidence_value,
            unit=unit,
            start=start,
        ),
        (),
    )


def historical_filing(selected_filing: SECFiling, *, base: int = 100):
    from valuation_platform.normalization import HistoricalFilingResult

    metrics = tuple(
        historical_metric(metric, selected_filing, base + index)
        for index, metric in enumerate(
            (
                FinancialMetric.REVENUE,
                FinancialMetric.OPERATING_INCOME,
                FinancialMetric.PRETAX_INCOME,
                FinancialMetric.INCOME_TAX_EXPENSE,
                FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
                FinancialMetric.D_AND_A,
                FinancialMetric.CAPEX,
                FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
            )
        )
    )
    return HistoricalFilingResult(selected_filing, metrics)


def balance_value(
    metric: FinancialMetric,
    selected_filing: SECFiling,
    value: object = 10,
    *,
    unit: str = "USD",
) -> NormalizedBalanceSheetValue:
    assert selected_filing.report_date is not None
    evidence_value = value if isinstance(value, int) and not isinstance(value, bool) else 1
    return NormalizedBalanceSheetValue(
        metric,
        value,  # type: ignore[arg-type]
        unit,
        selected_filing.report_date,
        fact_evidence(
            metric,
            selected_filing,
            evidence_value,
            unit=unit,
            start=None,
        ),
        (),
    )


def balance_filing(selected_filing: SECFiling, *, base: int = 10):
    metrics = tuple(
        balance_value(metric, selected_filing, base + index)
        for index, metric in enumerate(
            (
                FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
                FinancialMetric.SHORT_TERM_INVESTMENTS,
                FinancialMetric.LONG_TERM_MARKETABLE_SECURITIES,
                FinancialMetric.COMMERCIAL_PAPER,
                FinancialMetric.SHORT_TERM_BORROWINGS,
                FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
                FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
                FinancialMetric.OPERATING_RECEIVABLES,
            )
        )
    )
    return AnnualBalanceSheetFilingResult(selected_filing, metrics)


def inputs(
    filings: tuple[SECFiling, ...] = (filing(2024), filing(2025)),
    *,
    identity: SECCompanyIdentity | None = None,
):
    identity = identity or company()
    historical = NormalizedHistoricalFinancials(
        identity,
        "facts-source",
        NOW,
        tuple(historical_filing(item, base=100 * (index + 1)) for index, item in enumerate(filings)),
    )
    balances = NormalizedAnnualBalanceSheets(
        identity,
        "facts-source",
        NOW,
        tuple(balance_filing(item, base=10 * (index + 1)) for index, item in enumerate(filings)),
    )
    return historical, balances


def nwc_level(
    selected_filing: SECFiling,
    amount: int,
    *,
    identity: SECCompanyIdentity | None = None,
    policy_version: str = "2",
) -> CalculatedOperatingNWC:
    identity = identity or company()
    source = balance_value(
        FinancialMetric.OPERATING_RECEIVABLES,
        selected_filing,
        amount,
    )
    contribution = OperatingNWCComponentContribution(
        OperatingNWCComponent.OPERATING_RECEIVABLES,
        OperatingNWCPerimeterSide.ASSET,
        source,
        Decimal(amount),
        Decimal(amount),
    )
    assert selected_filing.report_date is not None
    return CalculatedOperatingNWC(
        identity.cik,
        selected_filing.report_date,
        selected_filing,
        "onwc-policy",
        policy_version,
        Decimal(amount),
        "USD",
        OperatingNWCCalculationFormula.REQUIRED_ASSETS_MINUS_REQUIRED_LIABILITIES,
        (contribution,),
    )


def nwc_change(
    opening: CalculatedOperatingNWC, closing: CalculatedOperatingNWC
) -> CalculatedOperatingNWCChange:
    return CalculatedOperatingNWCChange(
        opening.company_cik,
        opening.balance_date,
        closing.balance_date,
        opening.policy_id,
        opening.policy_version,
        "USD",
        opening.amount,
        closing.amount,
        closing.amount - opening.amount,
        opening,
        closing,
    )


def replace_historical_metric(
    historical: NormalizedHistoricalFinancials,
    annual_index: int,
    metric: FinancialMetric,
    replacement: object,
) -> NormalizedHistoricalFinancials:
    annual = list(historical.annual)
    original = annual[annual_index]
    annual[annual_index] = replace(
        original,
        metrics=tuple(
            replacement if item.metric is metric else item for item in original.metrics
        ),
    )
    return replace(historical, annual=tuple(annual))


def replace_balance_metric(
    balances: NormalizedAnnualBalanceSheets,
    annual_index: int,
    metric: FinancialMetric,
    replacement: object,
) -> NormalizedAnnualBalanceSheets:
    annual = list(balances.annual)
    original = annual[annual_index]
    annual[annual_index] = replace(
        original,
        metrics=tuple(
            replacement if item.metric is metric else item for item in original.metrics
        ),
    )
    return replace(balances, annual=tuple(annual))


class StandardizedOutputTests(unittest.TestCase):
    def test_complete_five_period_meta_style_assembly(self) -> None:
        selected_filings = tuple(filing(year) for year in range(2021, 2026))
        historical, balances = inputs(selected_filings)
        levels = tuple(
            nwc_level(item.filing, 1_000 + index)
            for index, item in enumerate(balances.annual)
        )
        changes = tuple(
            nwc_change(opening, closing)
            for opening, closing in zip(levels, levels[1:])
        )
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=levels,
            operating_nwc_changes=changes,
        )
        self.assertEqual(len(output.annual), 5)
        self.assertEqual(len(output.annual[0].measures), 17)
        self.assertIs(
            output.annual[0]
            .for_measure(HistoricalMeasure.CHANGE_IN_OPERATING_NWC)
            .status,
            HistoricalAvailability.NOT_COMPARABLE,
        )
        self.assertEqual(
            tuple(
                item.for_measure(HistoricalMeasure.CHANGE_IN_OPERATING_NWC).value
                for item in output.annual[1:]
            ),
            (Decimal(1), Decimal(1), Decimal(1), Decimal(1)),
        )

    def test_complete_period_centric_assembly_and_accessors(self) -> None:
        historical, balances = inputs()
        levels = tuple(
            nwc_level(item.filing, amount)
            for item, amount in zip(balances.annual, (50, 60))
        )
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=levels,
            operating_nwc_changes=(nwc_change(*levels),),
        )
        self.assertEqual(output.ticker, "META")
        self.assertEqual(output.company_cik, 1326801)
        self.assertEqual(len(output.annual), 2)
        self.assertEqual(output.selected_filings[0].report_date, date(2024, 12, 31))
        revenue = output.annual[0].for_measure(HistoricalMeasure.REVENUE)
        self.assertIsInstance(revenue, ResolvedHistoricalMeasure)
        self.assertEqual(revenue.value, Decimal(100))
        self.assertEqual(
            tuple(item.value for item in output.series(HistoricalMeasure.REVENUE)),
            (Decimal(100), Decimal(200)),
        )
        self.assertEqual(
            tuple(item.measure for item in output.annual[0].measures),
            tuple(HistoricalMeasure),
        )

    def test_first_change_is_not_comparable_and_later_change_is_preserved(self) -> None:
        historical, balances = inputs()
        opening = nwc_level(balances.annual[0].filing, 50)
        closing = nwc_level(balances.annual[1].filing, 60)
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=(opening, closing),
            operating_nwc_changes=(nwc_change(opening, closing),),
        )
        first, second = output.series(HistoricalMeasure.CHANGE_IN_OPERATING_NWC)
        self.assertIsInstance(first, UnavailableHistoricalMeasure)
        self.assertIs(first.status, HistoricalAvailability.NOT_COMPARABLE)
        self.assertEqual(first.reason, "no_opening_operating_nwc")
        self.assertIsInstance(second, ResolvedHistoricalMeasure)
        self.assertEqual(second.value, Decimal(10))
        self.assertEqual(second.opening_date, date(2024, 12, 31))
        onwc = output.annual[1].for_measure(HistoricalMeasure.OPERATING_NWC)
        self.assertEqual(onwc.policy.policy_id, "onwc-policy")
        self.assertEqual(onwc.policy.version, "2")

    def test_policy_change_without_upstream_change_is_not_comparable(self) -> None:
        historical, balances = inputs()
        opening = nwc_level(balances.annual[0].filing, 50, policy_version="1")
        closing = nwc_level(balances.annual[1].filing, 60, policy_version="2")
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=(opening, closing),
        )
        change = output.annual[1].for_measure(
            HistoricalMeasure.CHANGE_IN_OPERATING_NWC
        )
        self.assertIsInstance(change, UnavailableHistoricalMeasure)
        self.assertIs(change.status, HistoricalAvailability.NOT_COMPARABLE)
        self.assertEqual(change.reason, "operating_nwc_policy_or_perimeter_changed")

    def test_company_mismatch_is_rejected(self) -> None:
        historical, balances = inputs()
        other = replace(balances, company=company(1, "OTHER"))
        with self.assertRaisesRegex(HistoricalOutputError, "different companies"):
            assemble_standardized_annual_history(historical, other)

    def test_filing_identity_mismatch_is_rejected(self) -> None:
        historical, balances = inputs()
        changed = replace(
            balances.annual[0].filing,
            primary_document="different.htm",
        )
        annual = (replace(balances.annual[0], filing=changed), *balances.annual[1:])
        with self.assertRaisesRegex(HistoricalOutputError, "identities differ"):
            assemble_standardized_annual_history(
                historical, replace(balances, annual=annual)
            )

    def test_duplicate_accession_and_report_date_are_rejected(self) -> None:
        first, second = filing(2024), filing(2025)
        for filings in (
            (first, replace(second, accession_number=first.accession_number)),
            (first, replace(second, report_date=first.report_date)),
        ):
            historical, balances = inputs(filings)
            with self.assertRaises(HistoricalOutputError):
                assemble_standardized_annual_history(historical, balances)

    def test_non_chronological_input_is_rejected(self) -> None:
        historical, balances = inputs((filing(2025), filing(2024)))
        with self.assertRaisesRegex(HistoricalOutputError, "increasing"):
            assemble_standardized_annual_history(historical, balances)

    def test_duration_end_and_instant_date_mismatches_are_rejected(self) -> None:
        historical, balances = inputs()
        revenue = historical.annual[0].metrics[0]
        assert isinstance(revenue, NormalizedHistoricalValue)
        bad_revenue = replace(
            revenue,
            period=HistoricalPeriod(revenue.period.start, date(2023, 12, 31)),
        )
        with self.assertRaisesRegex(HistoricalOutputError, "duration"):
            assemble_standardized_annual_history(
                replace_historical_metric(
                    historical, 0, FinancialMetric.REVENUE, bad_revenue
                ),
                balances,
            )
        cash = balances.annual[0].metrics[0]
        assert isinstance(cash, NormalizedBalanceSheetValue)
        bad_cash = replace(cash, balance_date=date(2023, 12, 31))
        with self.assertRaisesRegex(HistoricalOutputError, "Balance-sheet metric"):
            assemble_standardized_annual_history(
                historical,
                replace_balance_metric(
                    balances,
                    0,
                    FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
                    bad_cash,
                ),
            )

    def test_conflicting_resolved_fiscal_starts_are_rejected(self) -> None:
        historical, balances = inputs()
        operating = historical.annual[0].metrics[1]
        assert isinstance(operating, NormalizedHistoricalValue)
        changed = replace(
            operating,
            period=HistoricalPeriod(date(2024, 2, 1), operating.period.end),
        )
        historical = replace_historical_metric(
            historical, 0, FinancialMetric.OPERATING_INCOME, changed
        )
        with self.assertRaisesRegex(HistoricalOutputError, "disagree"):
            assemble_standardized_annual_history(historical, balances)

    def test_all_unavailable_duration_measures_leave_fiscal_start_unknown(self) -> None:
        historical, balances = inputs((filing(2025),))
        missing = tuple(
            MissingHistoricalMetric(
                item.metric,
                MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION,
                (),
            )
            for item in historical.annual[0].metrics
        )
        historical = replace(
            historical,
            annual=(replace(historical.annual[0], metrics=missing),),
        )
        output = assemble_standardized_annual_history(historical, balances)
        self.assertIsNone(output.annual[0].fiscal_start)

    def test_duplicate_metric_and_evidence_accession_mismatch_are_rejected(self) -> None:
        historical, balances = inputs()
        duplicated = replace(
            historical.annual[0],
            metrics=(
                *historical.annual[0].metrics,
                historical.annual[0].metrics[0],
            ),
        )
        with self.assertRaisesRegex(HistoricalOutputError, "duplicate metric"):
            assemble_standardized_annual_history(
                replace(
                    historical,
                    annual=(duplicated, *historical.annual[1:]),
                ),
                balances,
            )
        revenue = historical.annual[0].metrics[0]
        assert isinstance(revenue, NormalizedHistoricalValue)
        mismatched = replace(
            revenue,
            chosen_source=replace(
                revenue.chosen_source,
                accession_number="later-comparative-accession",
            ),
        )
        with self.assertRaisesRegex(HistoricalOutputError, "does not belong"):
            assemble_standardized_annual_history(
                replace_historical_metric(
                    historical,
                    0,
                    FinancialMetric.REVENUE,
                    mismatched,
                ),
                balances,
            )

    def test_float_boolean_and_wrong_unit_are_rejected(self) -> None:
        historical, balances = inputs()
        for value in (1.5, True):
            replacement = historical_metric(
                FinancialMetric.REVENUE,
                historical.annual[0].filing,
                value,
            )
            with self.assertRaisesRegex(HistoricalOutputError, "bool or float"):
                assemble_standardized_annual_history(
                    replace_historical_metric(
                        historical, 0, FinancialMetric.REVENUE, replacement
                    ),
                    balances,
                )
        wrong_unit = historical_metric(
            FinancialMetric.REVENUE,
            historical.annual[0].filing,
            1,
            unit="shares",
        )
        with self.assertRaisesRegex(HistoricalOutputError, "exact unit"):
            assemble_standardized_annual_history(
                replace_historical_metric(
                    historical, 0, FinancialMetric.REVENUE, wrong_unit
                ),
                balances,
            )

    def test_integer_becomes_decimal_and_decimal_is_preserved(self) -> None:
        historical, balances = inputs()
        precise = Decimal("0.1234567890123456789")
        etr = historical_metric(
            FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
            historical.annual[0].filing,
            precise,
        )
        output = assemble_standardized_annual_history(
            replace_historical_metric(
                historical, 0, FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE, etr
            ),
            balances,
        )
        self.assertEqual(
            output.annual[0].for_measure(HistoricalMeasure.REVENUE).value,
            Decimal(100),
        )
        self.assertEqual(
            output.annual[0]
            .for_measure(HistoricalMeasure.REPORTED_EFFECTIVE_TAX_RATE)
            .value,
            precise,
        )

    def test_direct_and_derived_provenance_are_compact(self) -> None:
        historical, balances = inputs()
        direct = assemble_standardized_annual_history(historical, balances).annual[
            0
        ].for_measure(HistoricalMeasure.REVENUE)
        self.assertIsInstance(direct, ResolvedHistoricalMeasure)
        self.assertIs(direct.resolution, HistoricalResolutionKind.DIRECT)
        self.assertEqual(direct.sources[0].accession_number, "accession-2024")
        self.assertEqual(direct.sources[0].concept, "revenue")

        selected_filing = historical.annual[0].filing
        assert selected_filing.report_date is not None
        operand = fact_evidence(
            FinancialMetric.D_AND_A,
            selected_filing,
            start=date(2024, 1, 1),
        )
        derived = DerivedHistoricalValue(
            FinancialMetric.D_AND_A,
            Decimal(100),
            "USD",
            HistoricalPeriod(date(2024, 1, 1), selected_filing.report_date),
            "derived-policy",
            DerivationOperation.ADD,
            (operand,),
        )
        output = assemble_standardized_annual_history(
            replace_historical_metric(
                historical, 0, FinancialMetric.D_AND_A, derived
            ),
            balances,
        )
        result = output.annual[0].for_measure(HistoricalMeasure.D_AND_A)
        self.assertIsInstance(result, ResolvedHistoricalMeasure)
        self.assertIs(result.resolution, HistoricalResolutionKind.DERIVED)
        self.assertEqual(result.policy.policy_id, "derived-policy")
        self.assertEqual(len(result.sources), 1)

    def test_derived_diluted_shares_remain_derived_on_original_filing_basis(self) -> None:
        historical, balances = inputs()
        selected_filing = historical.annual[0].filing
        assert selected_filing.report_date is not None
        operands = (
            fact_evidence(
                FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
                selected_filing,
                345_755_000,
                unit="shares",
                start=date(2024, 1, 1),
            ),
            fact_evidence(
                FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
                selected_filing,
                331_919_000,
                unit="shares",
                start=date(2024, 1, 1),
            ),
        )
        derived = DerivedHistoricalValue(
            FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
            Decimal(677_674_000),
            "shares",
            HistoricalPeriod(date(2024, 1, 1), selected_filing.report_date),
            "googl_annual_diluted_weighted_average_shares_v1",
            DerivationOperation.ADD,
            operands,
        )
        output = assemble_standardized_annual_history(
            replace_historical_metric(
                historical,
                0,
                FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
                derived,
            ),
            balances,
        )
        result = output.annual[0].for_measure(
            HistoricalMeasure.DILUTED_WEIGHTED_AVERAGE_SHARES
        )
        self.assertIsInstance(result, ResolvedHistoricalMeasure)
        self.assertEqual(result.value, Decimal(677_674_000))
        self.assertIs(result.resolution, HistoricalResolutionKind.DERIVED)
        self.assertEqual(len(result.sources), 2)

    def test_googl_style_missing_d_and_a_and_blocked_onwc_are_preserved(self) -> None:
        identity = company(1652044, "GOOGL")
        historical, balances = inputs((filing(2025),), identity=identity)
        missing = MissingHistoricalMetric(
            FinancialMetric.D_AND_A,
            MissingReason.NO_VALID_DERIVATION_OPERANDS,
            (),
        )
        historical = replace_historical_metric(
            historical, 0, FinancialMetric.D_AND_A, missing
        )
        blocker = OperatingNWCPerimeterComponentPolicy(
            OperatingNWCComponent.OTHER_CURRENT_ASSETS,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER,
            True,
            None,
            "Unresolved component",
        )
        readiness = OperatingNWCReadinessResult(
            "googl-policy",
            "1",
            identity.cik,
            balances.annual[0].filing,
            (),
            (),
            (),
            (blocker,),
            (),
        )
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=(readiness,),
        )
        d_and_a = output.annual[0].for_measure(HistoricalMeasure.D_AND_A)
        onwc = output.annual[0].for_measure(HistoricalMeasure.OPERATING_NWC)
        self.assertIs(d_and_a.status, HistoricalAvailability.MISSING)
        self.assertIs(onwc.status, HistoricalAvailability.METHODOLOGY_BLOCKED)

    def test_apple_long_term_securities_and_cost_policy_metadata_are_preserved(self) -> None:
        apple = company(320193, "AAPL")
        historical, balances = inputs((filing(2025),), identity=apple)
        output = assemble_standardized_annual_history(historical, balances)
        securities = output.annual[0].for_measure(
            HistoricalMeasure.LONG_TERM_MARKETABLE_SECURITIES
        )
        self.assertIsInstance(securities, ResolvedHistoricalMeasure)

        cost = company(909832, "COST")
        cost_filing = replace(
            filing(2023),
            report_date=date(2023, 9, 3),
        )
        historical, balances = inputs((cost_filing,), identity=cost)
        metrics = tuple(
            replace(
                item,
                period=HistoricalPeriod(date(2022, 8, 29), date(2023, 9, 3)),
            )
            for item in historical.annual[0].metrics
        )
        historical = replace(
            historical,
            annual=(replace(historical.annual[0], metrics=metrics),),
        )
        level = nwc_level(cost_filing, 500, identity=cost, policy_version="1")
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=(level,),
        )
        onwc = output.annual[0].for_measure(HistoricalMeasure.OPERATING_NWC)
        self.assertEqual(output.annual[0].fiscal_start, date(2022, 8, 29))
        self.assertEqual(onwc.policy.version, "1")

    def test_missing_and_ambiguous_results_remain_typed(self) -> None:
        historical, balances = inputs()
        missing = MissingHistoricalMetric(
            FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
            MissingReason.NO_VALID_CURRENT_INSTANT_OBSERVATION,
            (),
        )
        balances = replace_balance_metric(
            balances, 0, FinancialMetric.LONG_TERM_DEBT_NONCURRENT, missing
        )
        candidate = fact_evidence(
            FinancialMetric.REVENUE,
            historical.annual[0].filing,
            start=date(2024, 1, 1),
        )
        ambiguous = AmbiguousHistoricalMetric(
            FinancialMetric.REVENUE,
            AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
            (candidate,),
        )
        historical = replace_historical_metric(
            historical, 0, FinancialMetric.REVENUE, ambiguous
        )
        output = assemble_standardized_annual_history(historical, balances)
        debt = output.annual[0].for_measure(
            HistoricalMeasure.LONG_TERM_DEBT_NONCURRENT
        )
        revenue = output.annual[0].for_measure(HistoricalMeasure.REVENUE)
        self.assertIsInstance(debt, UnavailableHistoricalMeasure)
        self.assertIs(debt.status, HistoricalAvailability.MISSING)
        self.assertIsInstance(revenue, AmbiguousStandardizedMeasure)
        self.assertIs(revenue.status, HistoricalAvailability.AMBIGUOUS)

    def test_ambiguous_duration_and_instant_order_is_canonical(self) -> None:
        historical, balances = inputs()
        selected_filing = historical.annual[0].filing
        duration_a = fact_evidence(
            FinancialMetric.REVENUE,
            selected_filing,
            100,
            start=date(2024, 1, 1),
        )
        duration_b = replace(duration_a, concept="alternate-revenue", value=101)
        instant_a = fact_evidence(
            FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
            selected_filing,
            10,
        )
        instant_b = replace(instant_a, concept="alternate-cash", value=11)

        outputs = []
        for duration_candidates, instant_candidates in (
            ((duration_a, duration_b), (instant_a, instant_b)),
            ((duration_b, duration_a), (instant_b, instant_a)),
        ):
            ambiguous_duration = AmbiguousHistoricalMetric(
                FinancialMetric.REVENUE,
                AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                duration_candidates,
            )
            ambiguous_instant = AmbiguousHistoricalMetric(
                FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
                AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                instant_candidates,
            )
            outputs.append(
                assemble_standardized_annual_history(
                    replace_historical_metric(
                        historical,
                        0,
                        FinancialMetric.REVENUE,
                        ambiguous_duration,
                    ),
                    replace_balance_metric(
                        balances,
                        0,
                        FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
                        ambiguous_instant,
                    ),
                )
            )

        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(
            standardized_history_to_dict(outputs[0]),
            standardized_history_to_dict(outputs[1]),
        )

    def test_ambiguous_operating_nwc_order_is_canonical(self) -> None:
        historical, balances = inputs((filing(2025),))
        selected_filing = balances.annual[0].filing
        candidate_a = fact_evidence(
            FinancialMetric.OPERATING_RECEIVABLES,
            selected_filing,
            10,
        )
        candidate_b = replace(candidate_a, concept="alternate-receivables", value=11)
        policy = OperatingNWCPerimeterComponentPolicy(
            OperatingNWCComponent.OPERATING_RECEIVABLES,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.REQUIRED,
            True,
            FinancialMetric.OPERATING_RECEIVABLES,
            "Required operating receivables",
        )

        outputs = []
        for candidates in ((candidate_a, candidate_b), (candidate_b, candidate_a)):
            ambiguous = AmbiguousHistoricalMetric(
                FinancialMetric.OPERATING_RECEIVABLES,
                AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                candidates,
            )
            readiness = OperatingNWCReadinessResult(
                "onwc-policy",
                "2",
                historical.company.cik,
                selected_filing,
                (),
                (),
                (AmbiguousOperatingNWCReadinessComponent(policy, ambiguous),),
                (),
                (),
            )
            outputs.append(
                assemble_standardized_annual_history(
                    historical,
                    balances,
                    operating_nwc_results=(readiness,),
                )
            )

        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(
            standardized_history_to_dict(outputs[0]),
            standardized_history_to_dict(outputs[1]),
        )

    def test_methodology_blocked_onwc_remains_blocked(self) -> None:
        historical, balances = inputs()
        selected_filing = balances.annual[0].filing
        blocker = OperatingNWCPerimeterComponentPolicy(
            OperatingNWCComponent.OTHER_CURRENT_ASSETS,
            OperatingNWCPerimeterSide.ASSET,
            OperatingNWCPerimeterTreatment.METHODOLOGY_BLOCKER,
            True,
            None,
            "Unresolved component",
        )
        readiness = OperatingNWCReadinessResult(
            "blocked-policy",
            "1",
            historical.company.cik,
            selected_filing,
            (),
            (),
            (),
            (blocker,),
            (),
        )
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=(readiness,),
        )
        result = output.annual[0].for_measure(HistoricalMeasure.OPERATING_NWC)
        self.assertIsInstance(result, UnavailableHistoricalMeasure)
        self.assertIs(result.status, HistoricalAvailability.METHODOLOGY_BLOCKED)
        self.assertEqual(result.policy.policy_id, "blocked-policy")

    def test_supplied_change_must_match_adjacent_supplied_levels(self) -> None:
        historical, balances = inputs()
        opening = nwc_level(balances.annual[0].filing, 50)
        closing = nwc_level(balances.annual[1].filing, 60)
        other_opening = nwc_level(balances.annual[0].filing, 49)
        with self.assertRaisesRegex(HistoricalOutputError, "opening level differs"):
            assemble_standardized_annual_history(
                historical,
                balances,
                operating_nwc_results=(opening, closing),
                operating_nwc_changes=(nwc_change(other_opening, closing),),
            )
        with self.assertRaisesRegex(HistoricalOutputError, "closing annual level"):
            assemble_standardized_annual_history(
                historical,
                balances,
                operating_nwc_changes=(nwc_change(opening, closing),),
            )

    def test_change_embedded_opening_must_match_preceding_selected_period(self) -> None:
        historical, balances = inputs()
        nonadjacent_opening = nwc_level(filing(2023), 40)
        closing = nwc_level(balances.annual[1].filing, 60)
        with self.assertRaisesRegex(HistoricalOutputError, "selected periods"):
            assemble_standardized_annual_history(
                historical,
                balances,
                operating_nwc_results=(closing,),
                operating_nwc_changes=(nwc_change(nonadjacent_opening, closing),),
            )

    def test_adjacent_embedded_opening_can_stand_without_separate_level(self) -> None:
        historical, balances = inputs()
        opening = nwc_level(balances.annual[0].filing, 50)
        closing = nwc_level(balances.annual[1].filing, 60)
        output = assemble_standardized_annual_history(
            historical,
            balances,
            operating_nwc_results=(closing,),
            operating_nwc_changes=(nwc_change(opening, closing),),
        )
        change = output.annual[1].for_measure(
            HistoricalMeasure.CHANGE_IN_OPERATING_NWC
        )
        self.assertIsInstance(change, ResolvedHistoricalMeasure)
        self.assertEqual(change.value, Decimal(10))
        self.assertEqual(change.opening_date, balances.annual[0].filing.report_date)

    def test_noncalendar_and_week_based_periods_are_preserved(self) -> None:
        cases = (
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2023, 9, 30), date(2024, 9, 28)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )
        for index, (start, end) in enumerate(cases):
            selected_filing = replace(
                filing(2025, accession=f"special-{index}"), report_date=end
            )
            historical, balances = inputs((selected_filing,))
            metrics = tuple(
                replace(item, period=HistoricalPeriod(start, end))
                for item in historical.annual[0].metrics
            )
            historical = replace(
                historical,
                annual=(replace(historical.annual[0], metrics=metrics),),
            )
            output = assemble_standardized_annual_history(historical, balances)
            self.assertEqual(output.annual[0].fiscal_start, start)
            self.assertEqual(output.annual[0].fiscal_end, end)

    def test_curated_policy_and_etr_operand_provenance_serialize_in_schema_v3(self) -> None:
        selected_filing = filing(
            2025,
            accession="0001326801-26-000001",
        )
        historical, balances = inputs((selected_filing,))
        pretax = next(
            item
            for item in historical.annual[0].metrics
            if item.metric is FinancialMetric.PRETAX_INCOME
        )
        tax = next(
            item
            for item in historical.annual[0].metrics
            if item.metric is FinancialMetric.INCOME_TAX_EXPENSE
        )
        assert isinstance(pretax, NormalizedHistoricalValue)
        assert isinstance(tax, NormalizedHistoricalValue)
        xbrl_evidence = FilingXBRLEvidence(
            EvidenceSourceKind.FILING_XBRL,
            "xbrl-source",
            "http://fasb.org/us-gaap/2025",
            "PretaxCandidate",
            "102",
            Decimal(102),
            "USD",
            pretax.period.start,
            pretax.period.end,
            selected_filing.accession_number,
            selected_filing.form,
            selected_filing.filing_date,
            selected_filing.report_date,
            selected_filing.primary_document,
            NOW,
            "annual-context",
            (),
            "-6",
            False,
            "usd",
            1,
        )
        confirming_xbrl_evidence = replace(
            xbrl_evidence,
            context_id="annual-context-confirming",
            unit_ref="usd-confirming",
            raw_value="102.0",
            decimals="-3",
            occurrence_ordinal=2,
        )
        policy = HistoricalPolicyProvenance(
            "pretax_scope_equivalence",
            "1",
            "INCLUDED_PRETAX",
            historical.company.cik,
            selected_filing.accession_number,
            selected_filing.report_date,
            pretax.period.start,
            pretax.period.end,
            "us-gaap",
            "PretaxCandidate",
            "USD",
            (
                ReviewedPolicyEvidence(
                    "test-evidence",
                    "https://www.sec.gov/Archives/test.htm",
                    "Note 1",
                    "docs/pretax-equity-method-note-evidence.md",
                    date(2026, 10, 9),
                    "approved",
                    "Exact filing evidence establishes included Pretax scope.",
                    "Reviewed note-to-statement binding.",
                ),
            ),
            (xbrl_evidence, confirming_xbrl_evidence),
        )
        pretax = replace(pretax, policy_provenance=policy)
        etr = derive_reported_effective_tax_rate(
            selected_filing.accession_number,
            selected_filing.report_date,
            (pretax, tax),
        )
        historical = replace_historical_metric(
            historical,
            0,
            FinancialMetric.PRETAX_INCOME,
            pretax,
        )
        historical = replace_historical_metric(
            historical,
            0,
            FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE,
            etr,
        )

        payload = standardized_history_to_dict(
            assemble_standardized_annual_history(historical, balances)
        )
        self.assertEqual(payload["schema_version"], "4")
        measures = {
            item["measure"]: item for item in payload["annual"][0]["measures"]
        }
        pretax_payload = measures[FinancialMetric.PRETAX_INCOME.value]
        self.assertEqual(
            pretax_payload["policy"]["entry_key"]["accession_number"],
            selected_filing.accession_number,
        )
        self.assertEqual(
            pretax_payload["policy"]["reviewed_evidence"][0]["review_status"],
            "approved",
        )
        etr_payload = measures[FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE.value]
        self.assertEqual(
            etr_payload["supporting_policies"][0]["policy_id"],
            "pretax_scope_equivalence",
        )
        self.assertEqual(
            etr_payload["supporting_policies"][0]["filing_xbrl_evidence"][0][
                "context_id"
            ],
            "annual-context",
        )
        self.assertEqual(
            [
                item["occurrence_ordinal"]
                for item in etr_payload["supporting_policies"][0][
                    "filing_xbrl_evidence"
                ]
            ],
            [1, 2],
        )
        self.assertEqual(
            etr_payload["supporting_policies"][0]["filing_xbrl_evidence"][1][
                "raw_value"
            ],
            "102.0",
        )

    def test_serialization_is_deterministic_and_uses_decimal_strings(self) -> None:
        historical, balances = inputs()
        output = assemble_standardized_annual_history(historical, balances)
        first = standardized_history_to_dict(output)
        second = standardized_history_to_dict(output)
        self.assertEqual(first, second)
        payload = json.dumps(first)
        self.assertIn('"value": "100"', payload)
        self.assertNotIn("fcff", payload)
        self.assertNotIn("total_debt", payload)
        self.assertNotIn("net_debt", payload)
        self.assertNotIn("valuation", payload)

    def test_output_does_not_retain_raw_sec_graphs_or_upstream_containers(self) -> None:
        historical, balances = inputs()
        output = assemble_standardized_annual_history(historical, balances)
        self.assertFalse(hasattr(output, "company_facts"))
        self.assertFalse(hasattr(output, "filing_xbrl"))
        self.assertFalse(hasattr(output, "historical"))
        self.assertFalse(hasattr(output, "balance_sheets"))


if __name__ == "__main__":
    unittest.main()
