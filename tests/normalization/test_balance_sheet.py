from datetime import date, datetime, timezone
from decimal import Decimal
from unittest import TestCase

from valuation_platform.normalization import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    BalanceSheetDerivationError,
    GOOGL_CURRENT_PORTION_OF_LONG_TERM_DEBT_DERIVATION_POLICY,
    BalanceSheetNormalizationError,
    CASH_AND_CASH_EQUIVALENTS_POLICY,
    EvidenceSourceKind,
    FilingXBRLEvidence,
    FinancialMetric,
    DerivedBalanceSheetValue,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedBalanceSheetValue,
    TRADE_ACCOUNTS_PAYABLE_POLICY,
    derive_googl_debt,
    normalize_annual_balance_sheets,
)
from valuation_platform.sec.company_facts import SECFactObservation
from valuation_platform.sec.fact_selection import (
    FilingFactObservations,
    ObservationRelationship,
    SelectedFactObservation,
    SelectedFactObservations,
)
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.filing_xbrl import (
    FilingXBRLDimension,
    FilingXBRLFact,
    FilingXBRLQName,
    FilingXBRLUnit,
    SECFilingXBRL,
    parse_filing_xbrl_instance,
)
from valuation_platform.sec.tickers import SECCompanyIdentity


RETRIEVED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)
REPORT_DATE = date(2025, 12, 31)
RECEIVABLES = "AccountsReceivableNetCurrent"
INVENTORY = "InventoryNet"
PAYABLES = "AccountsPayableCurrent"
CONTRACT_LIABILITIES = "ContractWithCustomerLiabilityCurrent"
VENDOR_RECEIVABLES = "NontradeReceivablesCurrent"
EMPLOYEE_LIABILITIES = "EmployeeRelatedLiabilitiesCurrent"
MEMBER_REWARDS = "AccruedLiabilitiesCurrent"
ACCRUED_REVENUE_SHARE = "AccruedRevenueShare"
ACCRUED_CUSTOMER_LIABILITIES = "AccruedCustomerLiabilitiesCurrent"
ACCRUED_PP_AND_E = "PropertyAndEquipmentAccruedLiabilitiesCurrent"
COMBINED_PP_AND_E = "CapitalExpendituresIncurredButNotYetPaid"
META_TRADE_PAYABLES = "AccountsPayableTradeCurrent"
CASH = "CashAndCashEquivalentsAtCarryingValue"
MARKETABLE_CURRENT = "MarketableSecuritiesCurrent"
META_MARKETABLE_FALLBACK = "AvailableForSaleSecuritiesDebtSecuritiesCurrent"
SHORT_TERM_INVESTMENTS = "ShortTermInvestments"
MARKETABLE_NONCURRENT = "MarketableSecuritiesNoncurrent"
COMMERCIAL_PAPER = "CommercialPaper"
SHORT_TERM_BORROWINGS = "OtherShortTermBorrowings"
CURRENT_LONG_TERM_DEBT = "LongTermDebtCurrent"
NONCURRENT_LONG_TERM_DEBT = "LongTermDebtNoncurrent"
DEBT_AND_LEASES_TOTAL = "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"
DEBT_AND_LEASES_NONCURRENT = "LongTermDebtAndCapitalLeaseObligations"
FINANCE_LEASE_TOTAL = "FinanceLeaseLiability"
FINANCE_LEASE_CURRENT = "FinanceLeaseLiabilityCurrent"
DEBT_DISCOUNT_AND_COSTS = "DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet"
GOOGLE_NAMESPACE = "http://www.google.com/20251231"
META_NAMESPACE = "http://www.facebook.com/20251231"
USD_NAMESPACE = "http://www.xbrl.org/2003/iso4217"


def make_filing(
    *,
    accession: str = "annual",
    report_date: date | None = REPORT_DATE,
    form: str = "10-K",
) -> SECFiling:
    return SECFiling(
        accession_number=accession,
        form=form,
        filing_date=date(2026, 2, 1),
        report_date=report_date,
        primary_document="annual.htm",
    )


def make_selected(
    concept: str,
    *,
    taxonomy: str = "us-gaap",
    value: object = 1,
    accession: str = "annual",
    start: date | None = None,
    end: date = REPORT_DATE,
    unit: str = "USD",
    relationship: ObservationRelationship = ObservationRelationship.CURRENT,
) -> SelectedFactObservation:
    return SelectedFactObservation(
        taxonomy=taxonomy,
        concept=concept,
        observation=SECFactObservation(
            unit=unit,
            value=value,  # type: ignore[arg-type]
            start=start,
            end=end,
            accession_number=accession,
            fiscal_year=2025,
            fiscal_period="FY",
            form="10-K",
            filed=date(2026, 2, 1),
            frame="CY2025Q4I",
        ),
        relationship=relationship,
    )


def make_input(
    *observations: SelectedFactObservation,
    company_cik: int = 1,
    filing: SECFiling | None = None,
    additional_filings: tuple[FilingFactObservations, ...] = (),
) -> SelectedFactObservations:
    company = SECCompanyIdentity(
        ticker="TEST",
        cik=company_cik,
        cik_padded=f"{company_cik:010d}",
        company_name="Test Company",
        source_url="ticker-source",
        retrieved_at=RETRIEVED_AT,
    )
    return SelectedFactObservations(
        company=company,
        source_url="facts-source",
        retrieved_at=RETRIEVED_AT,
        annual=(
            FilingFactObservations(
                filing=filing or make_filing(),
                observations=tuple(observations),
            ),
            *additional_filings,
        ),
        interim=(),
    )


def metric_result(
    selected: SelectedFactObservations,
    metric: FinancialMetric,
    *,
    filing_xbrl: tuple[SECFilingXBRL, ...] = (),
):
    result = normalize_annual_balance_sheets(
        selected,
        filing_xbrl=filing_xbrl,
    )
    return next(item for item in result.annual[0].metrics if item.metric is metric)


def make_filing_xbrl_fact(
    *,
    namespace: str = GOOGLE_NAMESPACE,
    concept: str = ACCRUED_REVENUE_SHARE,
    accession: str = "annual",
    start: date | None = None,
    end: date = REPORT_DATE,
    dimensions: tuple[FilingXBRLDimension, ...] = (),
    numeric_value: object = Decimal("10864000000"),
    raw_value: str | None = "10864000000",
    unit: FilingXBRLUnit | None = None,
    is_nil: bool = False,
    context_id: str = "current",
) -> FilingXBRLFact:
    usd_unit = FilingXBRLUnit(
        unit_id="USD",
        numerator_measures=(FilingXBRLQName(USD_NAMESPACE, "USD"),),
        denominator_measures=(),
    )
    return FilingXBRLFact(
        namespace=namespace,
        concept=concept,
        context_id=context_id,
        start=start,
        end=end,
        dimensions=dimensions,
        unit_ref=(unit or usd_unit).unit_id,
        unit=usd_unit if unit is None else unit,
        raw_value=raw_value,
        numeric_value=numeric_value,  # type: ignore[arg-type]
        decimals="-6",
        is_nil=is_nil,
        accession_number=accession,
        source_url="https://www.sec.gov/example_htm.xml",
    )


def make_filing_xbrl(
    *facts: FilingXBRLFact,
    company_cik: int = 1652044,
    filing: SECFiling | None = None,
) -> SECFilingXBRL:
    selected = make_input(company_cik=company_cik, filing=filing)
    filing_value = filing or make_filing()
    return SECFilingXBRL(
        company=selected.company,
        filing=filing_value,
        contexts=(),
        units=(),
        facts=facts,
        source_url="https://www.sec.gov/example_htm.xml",
        retrieved_at=RETRIEVED_AT,
    )


def make_prefixed_filing_xbrl(
    prefix: str,
    concept: str = ACCRUED_REVENUE_SHARE,
) -> SECFilingXBRL:
    selected = make_input(company_cik=1652044)
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
 xmlns:iso4217="{USD_NAMESPACE}" xmlns:{prefix}="{GOOGLE_NAMESPACE}">
  <xbrli:context id="current">
    <xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">1652044</xbrli:identifier></xbrli:entity>
    <xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period>
  </xbrli:context>
  <xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
  <{prefix}:{concept} contextRef="current" unitRef="USD" decimals="-6">10864000000</{prefix}:{concept}>
</xbrli:xbrl>""".encode()
    return parse_filing_xbrl_instance(
        content,
        company=selected.company,
        filing=selected.annual[0].filing,
        source_url="https://www.sec.gov/example_htm.xml",
        retrieved_at=RETRIEVED_AT,
    )


class AnnualBalanceSheetNormalizationTests(TestCase):
    def test_public_googl_debt_derivation_validates_selected_filing(self) -> None:
        accession = "0001652044-23-000016"
        direct = MissingHistoricalMetric(
            metric=FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
            reason=MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
            examined_concepts=(),
        )

        for filing in (
            make_filing(accession=accession, form="10-Q"),
            make_filing(accession=accession, report_date=None),
        ):
            with self.subTest(form=filing.form, report_date=filing.report_date):
                bucket = make_input(
                    company_cik=1652044,
                    filing=filing,
                ).annual[0]
                with self.assertRaisesRegex(
                    BalanceSheetDerivationError,
                    "requires an exact 10-K with a report date",
                ):
                    derive_googl_debt(
                        bucket,
                        direct,
                        "facts-source",
                        1652044,
                        GOOGL_CURRENT_PORTION_OF_LONG_TERM_DEBT_DERIVATION_POLICY,
                    )

        filing = make_filing(accession=accession)
        bucket = make_input(
            make_selected(DEBT_AND_LEASES_TOTAL, value=15_142, accession=accession),
            make_selected(DEBT_AND_LEASES_NONCURRENT, value=14_701, accession=accession),
            make_selected(FINANCE_LEASE_CURRENT, value=298, accession=accession),
            make_selected(DEBT_DISCOUNT_AND_COSTS, value=143, accession=accession),
            company_cik=1652044,
            filing=filing,
        ).annual[0]
        result = derive_googl_debt(
            bucket,
            direct,
            "facts-source",
            1652044,
            GOOGL_CURRENT_PORTION_OF_LONG_TERM_DEBT_DERIVATION_POLICY,
        )

        self.assertIsInstance(result, DerivedBalanceSheetValue)
        self.assertEqual(result.value, Decimal("0"))

    def test_direct_debt_primitives_resolve_as_decimal_with_exact_concepts(self) -> None:
        cases = (
            (1652044, FinancialMetric.COMMERCIAL_PAPER, COMMERCIAL_PAPER, 0),
            (909832, FinancialMetric.SHORT_TERM_BORROWINGS, SHORT_TERM_BORROWINGS, 88_000_000),
            (789019, FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT, CURRENT_LONG_TERM_DEBT, 2_749_000_000),
            (1326801, FinancialMetric.LONG_TERM_DEBT_NONCURRENT, NONCURRENT_LONG_TERM_DEBT, 9_923_000_000),
        )
        for cik, metric, concept, value in cases:
            with self.subTest(metric=metric):
                result = metric_result(
                    make_input(make_selected(concept, value=value), company_cik=cik),
                    metric,
                )
                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.value, Decimal(value))
                self.assertIsInstance(result.value, Decimal)
                self.assertEqual(result.chosen_source.concept, concept)
                self.assertEqual(result.chosen_source.accession_number, "annual")

    def test_commercial_paper_and_short_term_borrowings_are_issuer_scoped(self) -> None:
        for cik in (1652044, 789019, 320193):
            result = metric_result(
                make_input(make_selected(COMMERCIAL_PAPER, value=0), company_cik=cik),
                FinancialMetric.COMMERCIAL_PAPER,
            )
            self.assertIsInstance(result, NormalizedBalanceSheetValue)
            self.assertEqual(result.value, Decimal("0"))
        for cik in (1326801, 909832):
            result = metric_result(
                make_input(make_selected(COMMERCIAL_PAPER, value=1), company_cik=cik),
                FinancialMetric.COMMERCIAL_PAPER,
            )
            self.assertIsInstance(result, MissingHistoricalMetric)

        cost = metric_result(
            make_input(make_selected(SHORT_TERM_BORROWINGS, value=88), company_cik=909832),
            FinancialMetric.SHORT_TERM_BORROWINGS,
        )
        other = metric_result(
            make_input(make_selected(SHORT_TERM_BORROWINGS, value=88), company_cik=320193),
            FinancialMetric.SHORT_TERM_BORROWINGS,
        )
        absent = metric_result(
            make_input(company_cik=909832),
            FinancialMetric.SHORT_TERM_BORROWINGS,
        )
        self.assertIsInstance(cost, NormalizedBalanceSheetValue)
        self.assertIsInstance(other, MissingHistoricalMetric)
        self.assertIsInstance(absent, MissingHistoricalMetric)

    def test_debt_primitives_reject_structurally_ineligible_values(self) -> None:
        invalid = (
            make_selected(CURRENT_LONG_TERM_DEBT, accession="other"),
            make_selected(CURRENT_LONG_TERM_DEBT, end=date(2025, 12, 30)),
            make_selected(CURRENT_LONG_TERM_DEBT, start=date(2025, 1, 1)),
            make_selected(CURRENT_LONG_TERM_DEBT, unit="EUR"),
            make_selected(CURRENT_LONG_TERM_DEBT, value="1"),
            make_selected(CURRENT_LONG_TERM_DEBT, value=True),
            make_selected(CURRENT_LONG_TERM_DEBT, value=1.0),
            make_selected(
                CURRENT_LONG_TERM_DEBT,
                relationship=ObservationRelationship.COMPARATIVE,
            ),
        )
        for observation in invalid:
            with self.subTest(observation=observation):
                if observation.observation.accession_number == "other":
                    with self.assertRaisesRegex(
                        BalanceSheetNormalizationError,
                        "does not match filing accession",
                    ):
                        metric_result(
                            make_input(observation, company_cik=789019),
                            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
                        )
                else:
                    result = metric_result(
                        make_input(observation, company_cik=789019),
                        FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
                    )
                    self.assertIsInstance(result, MissingHistoricalMetric)

    def test_debt_subtotals_fair_values_and_lease_combined_facts_are_not_direct(self) -> None:
        for concept in (
            "LongTermDebt",
            "LongTermDebtFairValue",
            "LongTermDebtMaturitiesRepaymentsOfPrincipal",
            DEBT_AND_LEASES_TOTAL,
            DEBT_AND_LEASES_NONCURRENT,
        ):
            result = metric_result(
                make_input(make_selected(concept), company_cik=789019),
                FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
            )
            self.assertIsInstance(result, MissingHistoricalMetric)

    def test_multiple_eligible_debt_facts_are_deterministically_ambiguous(self) -> None:
        facts = (
            make_selected(NONCURRENT_LONG_TERM_DEBT, value=10),
            make_selected(NONCURRENT_LONG_TERM_DEBT, value=11),
        )
        results = tuple(
            metric_result(
                make_input(*ordered, company_cik=320193),
                FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
            )
            for ordered in (facts, tuple(reversed(facts)))
        )
        self.assertEqual(results[0], results[1])
        self.assertIsInstance(results[0], AmbiguousHistoricalMetric)

    def test_debt_primitives_preserve_noncalendar_and_week_based_dates(self) -> None:
        for report_date in (date(2025, 6, 30), date(2025, 9, 27), date(2023, 9, 3)):
            result = metric_result(
                make_input(
                    make_selected(NONCURRENT_LONG_TERM_DEBT, end=report_date),
                    company_cik=320193,
                    filing=make_filing(report_date=report_date),
                ),
                FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
            )
            self.assertIsInstance(result, NormalizedBalanceSheetValue)
            self.assertEqual(result.balance_date, report_date)

    def test_googl_debt_derivations_preserve_formula_and_provenance(self) -> None:
        filing = make_filing(
            accession="0001652044-23-000016",
            report_date=date(2022, 12, 31),
        )
        facts = (
            make_selected(DEBT_AND_LEASES_TOTAL, value=15_142_000_000, accession=filing.accession_number, end=filing.report_date),
            make_selected(DEBT_AND_LEASES_NONCURRENT, value=14_701_000_000, accession=filing.accession_number, end=filing.report_date),
            make_selected(FINANCE_LEASE_TOTAL, value=2_142_000_000, accession=filing.accession_number, end=filing.report_date),
            make_selected(FINANCE_LEASE_CURRENT, value=298_000_000, accession=filing.accession_number, end=filing.report_date),
            make_selected(DEBT_DISCOUNT_AND_COSTS, value=143_000_000, accession=filing.accession_number, end=filing.report_date),
        )
        output = normalize_annual_balance_sheets(
            make_input(*facts, company_cik=1652044, filing=filing)
        )
        by_metric = {item.metric: item for item in output.annual[0].metrics}
        current = by_metric[FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT]
        noncurrent = by_metric[FinancialMetric.LONG_TERM_DEBT_NONCURRENT]
        self.assertIsInstance(current, DerivedBalanceSheetValue)
        self.assertIsInstance(noncurrent, DerivedBalanceSheetValue)
        assert isinstance(current, DerivedBalanceSheetValue)
        assert isinstance(noncurrent, DerivedBalanceSheetValue)
        self.assertEqual(current.value, Decimal("0"))
        self.assertEqual(noncurrent.value, Decimal("12857000000"))
        self.assertEqual(
            current.policy_id,
            "googl_current_portion_of_long_term_debt_v1",
        )
        self.assertEqual(
            noncurrent.policy_id,
            "googl_noncurrent_long_term_debt_v1",
        )
        self.assertTrue(current.steps)
        self.assertTrue(noncurrent.steps)
        self.assertEqual(
            tuple(operand.name for operand in current.operands),
            (DEBT_AND_LEASES_TOTAL, DEBT_AND_LEASES_NONCURRENT, FINANCE_LEASE_CURRENT, DEBT_DISCOUNT_AND_COSTS),
        )
        self.assertEqual(
            tuple(operand.name for operand in noncurrent.operands),
            (DEBT_AND_LEASES_NONCURRENT, FINANCE_LEASE_TOTAL, FINANCE_LEASE_CURRENT),
        )
        for operand in (*current.operands, *noncurrent.operands):
            self.assertEqual(operand.chosen_source.source_url, "facts-source")
            self.assertEqual(operand.chosen_source.accession_number, filing.accession_number)
            self.assertEqual(operand.end, filing.report_date)
            self.assertEqual(operand.unit, "USD")

    def test_googl_validated_2021_through_2023_debt_identities(self) -> None:
        cases = (
            (
                "0001652044-22-000019",
                date(2021, 12, 31),
                (15_086, 14_817, 2_086, 113, 156, 0),
                (Decimal("0"), Decimal("12844")),
            ),
            (
                "0001652044-23-000016",
                date(2022, 12, 31),
                (15_142, 14_701, 2_142, 298, 143, None),
                (Decimal("0"), Decimal("12857")),
            ),
            (
                "0001652044-24-000022",
                date(2023, 12, 31),
                (14_746, 13_253, 1_746, 363, 130, 1_000),
                (Decimal("1000"), Decimal("11870")),
            ),
        )
        for accession, report_date, values, expected in cases:
            with self.subTest(accession=accession):
                total, noncurrent_combined, lease_total, lease_current, discount, direct_current = values
                filing = make_filing(accession=accession, report_date=report_date)
                observations = [
                    make_selected(DEBT_AND_LEASES_TOTAL, value=total, accession=accession, end=report_date),
                    make_selected(DEBT_AND_LEASES_NONCURRENT, value=noncurrent_combined, accession=accession, end=report_date),
                    make_selected(FINANCE_LEASE_TOTAL, value=lease_total, accession=accession, end=report_date),
                    make_selected(FINANCE_LEASE_CURRENT, value=lease_current, accession=accession, end=report_date),
                    make_selected(DEBT_DISCOUNT_AND_COSTS, value=discount, accession=accession, end=report_date),
                ]
                if direct_current is not None:
                    observations.append(
                        make_selected(CURRENT_LONG_TERM_DEBT, value=direct_current, accession=accession, end=report_date)
                    )
                output = normalize_annual_balance_sheets(
                    make_input(*observations, company_cik=1652044, filing=filing)
                )
                by_metric = {item.metric: item for item in output.annual[0].metrics}
                self.assertEqual(
                    by_metric[FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT].value,
                    expected[0],
                )
                self.assertEqual(
                    by_metric[FinancialMetric.LONG_TERM_DEBT_NONCURRENT].value,
                    expected[1],
                )

    def test_googl_debt_derivation_rejects_negative_operand_sign(self) -> None:
        filing = make_filing(accession="0001652044-23-000016")
        result = metric_result(
            make_input(
                make_selected(DEBT_AND_LEASES_TOTAL, value=15_142, accession=filing.accession_number),
                make_selected(DEBT_AND_LEASES_NONCURRENT, value=14_701, accession=filing.accession_number),
                make_selected(FINANCE_LEASE_CURRENT, value=298, accession=filing.accession_number),
                make_selected(DEBT_DISCOUNT_AND_COSTS, value=-143, accession=filing.accession_number),
                company_cik=1652044,
                filing=filing,
            ),
            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
        )
        self.assertIsInstance(result, MissingHistoricalMetric)

    def test_googl_debt_derivation_is_accession_and_cik_scoped(self) -> None:
        facts = (
            make_selected(DEBT_AND_LEASES_TOTAL, value=15_142),
            make_selected(DEBT_AND_LEASES_NONCURRENT, value=14_701),
            make_selected(FINANCE_LEASE_CURRENT, value=298),
            make_selected(DEBT_DISCOUNT_AND_COSTS, value=143),
        )
        for selected in (
            make_input(*facts, company_cik=1652044),
            make_input(*facts, company_cik=320193),
        ):
            result = metric_result(
                selected,
                FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
            )
            self.assertIsInstance(result, MissingHistoricalMetric)

        filing = make_filing(accession="0001652044-23-000016")
        with self.assertRaisesRegex(
            BalanceSheetDerivationError,
            "does not match selected filing",
        ):
            metric_result(
                make_input(
                    make_selected(DEBT_AND_LEASES_TOTAL, value=15_142, accession="other"),
                    company_cik=1652044,
                    filing=filing,
                ),
                FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
            )

    def test_googl_debt_derivation_requires_every_unambiguous_operand(self) -> None:
        filing = make_filing(accession="0001652044-23-000016")
        fixed = (
            make_selected(DEBT_AND_LEASES_TOTAL, value=15_142, accession=filing.accession_number),
            make_selected(DEBT_AND_LEASES_NONCURRENT, value=14_701, accession=filing.accession_number),
            make_selected(FINANCE_LEASE_CURRENT, value=298, accession=filing.accession_number),
        )
        missing = metric_result(
            make_input(*fixed, company_cik=1652044, filing=filing),
            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
        )
        ambiguous_facts = (
            *fixed,
            make_selected(DEBT_DISCOUNT_AND_COSTS, value=143, accession=filing.accession_number),
            make_selected(DEBT_DISCOUNT_AND_COSTS, value=144, accession=filing.accession_number),
        )
        forward = metric_result(
            make_input(*ambiguous_facts, company_cik=1652044, filing=filing),
            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
        )
        reverse = metric_result(
            make_input(*reversed(ambiguous_facts), company_cik=1652044, filing=filing),
            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
        )
        self.assertIsInstance(missing, MissingHistoricalMetric)
        self.assertIsInstance(forward, AmbiguousHistoricalMetric)
        self.assertEqual(forward, reverse)

    def test_googl_direct_debt_precedes_matching_derivation_and_conflict_is_ambiguous(self) -> None:
        filing = make_filing(accession="0001652044-24-000022")
        operands = (
            make_selected(DEBT_AND_LEASES_TOTAL, value=14_746, accession=filing.accession_number),
            make_selected(DEBT_AND_LEASES_NONCURRENT, value=13_253, accession=filing.accession_number),
            make_selected(FINANCE_LEASE_CURRENT, value=363, accession=filing.accession_number),
            make_selected(DEBT_DISCOUNT_AND_COSTS, value=130, accession=filing.accession_number),
        )
        matching = metric_result(
            make_input(
                *operands,
                make_selected(CURRENT_LONG_TERM_DEBT, value=1_000, accession=filing.accession_number),
                company_cik=1652044,
                filing=filing,
            ),
            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
        )
        conflict = metric_result(
            make_input(
                *operands,
                make_selected(CURRENT_LONG_TERM_DEBT, value=999, accession=filing.accession_number),
                company_cik=1652044,
                filing=filing,
            ),
            FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
        )
        self.assertIsInstance(matching, NormalizedBalanceSheetValue)
        self.assertIsInstance(conflict, AmbiguousHistoricalMetric)

    def test_reported_cash_resolves_with_exact_provenance_and_zero(self) -> None:
        for value in (35_873_000_000, 0):
            with self.subTest(value=value):
                result = metric_result(
                    make_input(
                        make_selected(CASH, value=value),
                        company_cik=1326801,
                    ),
                    FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
                )

                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertIsInstance(result.value, Decimal)
                self.assertEqual(result.value, Decimal(value))
                self.assertEqual(result.unit, "USD")
                self.assertEqual(result.balance_date, REPORT_DATE)
                self.assertEqual(result.chosen_source.taxonomy, "us-gaap")
                self.assertEqual(result.chosen_source.concept, CASH)
                self.assertEqual(result.chosen_source.accession_number, "annual")
                self.assertEqual(result.chosen_source.source_url, "facts-source")
                self.assertEqual(result.chosen_source.value, value)
                self.assertIs(type(result.chosen_source.value), int)

    def test_standard_cash_policy_applies_beyond_seed_ciks(self) -> None:
        for cik in (1045810, 310158, 1996810):
            with self.subTest(cik=cik):
                result = metric_result(
                    make_input(
                        make_selected(CASH, value=123),
                        company_cik=cik,
                    ),
                    FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
                )

                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.value, Decimal("123"))
                self.assertEqual(result.chosen_source.taxonomy, "us-gaap")
                self.assertEqual(result.chosen_source.concept, CASH)

    def test_reported_cash_rejects_unapproved_and_structurally_invalid_facts(self) -> None:
        cases = (
            make_selected("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"),
            make_selected("CashEquivalentsAtCarryingValue"),
            make_selected("CashAndCashEquivalentsFairValueDisclosure"),
            make_selected("Cash"),
            make_selected(CASH, taxonomy="example-extension"),
            make_selected(CASH, relationship=ObservationRelationship.COMPARATIVE),
            make_selected(CASH, start=date(2025, 1, 1)),
            make_selected(CASH, end=date(2025, 12, 30)),
            make_selected(CASH, unit="EUR"),
            make_selected(CASH, value="100"),
            make_selected(CASH, value=100.5),
            make_selected(CASH, value=True),
        )
        for observation in cases:
            with self.subTest(observation=observation):
                result = normalize_annual_balance_sheets(
                    make_input(observation, company_cik=1326801),
                    policies=(CASH_AND_CASH_EQUIVALENTS_POLICY,),
                ).annual[0].metrics[0]
                self.assertIsInstance(result, MissingHistoricalMetric)

    def test_reported_cash_requires_selected_accession(self) -> None:
        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "does not match filing accession",
        ):
            normalize_annual_balance_sheets(
                make_input(
                    make_selected(CASH, accession="other"),
                    company_cik=1326801,
                ),
                policies=(CASH_AND_CASH_EQUIVALENTS_POLICY,),
            )

    def test_duplicate_eligible_cash_facts_are_ambiguous(self) -> None:
        observations = (
            make_selected(CASH, value=10),
            make_selected(CASH, value=11),
        )
        results = tuple(
            metric_result(
                make_input(*ordered, company_cik=1045810),
                FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
            )
            for ordered in (observations, tuple(reversed(observations)))
        )

        self.assertEqual(results[0], results[1])
        self.assertIsInstance(results[0], AmbiguousHistoricalMetric)
        assert isinstance(results[0], AmbiguousHistoricalMetric)
        self.assertEqual(
            tuple(item.value for item in results[0].candidates),
            (10, 11),
        )

    def test_dimensional_filing_xbrl_cash_does_not_bypass_company_facts_policy(
        self,
    ) -> None:
        dimension = FilingXBRLDimension(
            dimension=FilingXBRLQName("http://example.com", "Axis"),
            explicit_member=FilingXBRLQName("http://example.com", "Member"),
            typed_member_xml=None,
        )
        fact = make_filing_xbrl_fact(
            namespace="http://fasb.org/us-gaap/2025",
            concept=CASH,
            dimensions=(dimension,),
            numeric_value=Decimal("123"),
            raw_value="123",
        )
        result = metric_result(
            make_input(company_cik=1045810),
            FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
            filing_xbrl=(
                make_filing_xbrl(
                    fact,
                    company_cik=1045810,
                ),
            ),
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_short_term_investment_concepts_are_cik_scoped(self) -> None:
        cases = (
            (1326801, MARKETABLE_CURRENT),
            (1652044, MARKETABLE_CURRENT),
            (789019, SHORT_TERM_INVESTMENTS),
            (320193, MARKETABLE_CURRENT),
            (909832, SHORT_TERM_INVESTMENTS),
        )
        for cik, concept in cases:
            with self.subTest(cik=cik, concept=concept):
                result = metric_result(
                    make_input(make_selected(concept, value=123), company_cik=cik),
                    FinancialMetric.SHORT_TERM_INVESTMENTS,
                )
                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertIsInstance(result.value, Decimal)
                self.assertEqual(result.value, Decimal("123"))
                self.assertEqual(result.chosen_source.concept, concept)

        rejected = metric_result(
            make_input(
                make_selected(META_MARKETABLE_FALLBACK, value=123),
                company_cik=1652044,
            ),
            FinancialMetric.SHORT_TERM_INVESTMENTS,
        )
        self.assertIsInstance(rejected, MissingHistoricalMetric)

    def test_meta_short_term_fallback_ignores_ineligible_primary(self) -> None:
        result = metric_result(
            make_input(
                make_selected(MARKETABLE_CURRENT, value=26_057, unit="EUR"),
                make_selected(META_MARKETABLE_FALLBACK, value=31_397),
                company_cik=1326801,
            ),
            FinancialMetric.SHORT_TERM_INVESTMENTS,
        )

        self.assertIsInstance(result, NormalizedBalanceSheetValue)
        assert isinstance(result, NormalizedBalanceSheetValue)
        self.assertIsInstance(result.value, Decimal)
        self.assertEqual(result.value, Decimal("31397"))
        self.assertEqual(result.chosen_source.value, 31_397)
        self.assertIs(type(result.chosen_source.value), int)
        self.assertEqual(result.chosen_source.concept, META_MARKETABLE_FALLBACK)

    def test_meta_conflicting_short_term_concepts_are_deterministically_ambiguous(self) -> None:
        observations = (
            make_selected(MARKETABLE_CURRENT, value=26_057),
            make_selected(META_MARKETABLE_FALLBACK, value=26_032),
        )
        results = tuple(
            metric_result(
                make_input(*ordered, company_cik=1326801),
                FinancialMetric.SHORT_TERM_INVESTMENTS,
            )
            for ordered in (observations, tuple(reversed(observations)))
        )

        self.assertEqual(results[0], results[1])
        self.assertIsInstance(results[0], AmbiguousHistoricalMetric)
        assert isinstance(results[0], AmbiguousHistoricalMetric)
        self.assertEqual(
            tuple(item.concept for item in results[0].candidates),
            (MARKETABLE_CURRENT, META_MARKETABLE_FALLBACK),
        )

    def test_combined_cash_and_short_term_investments_is_not_a_primitive(self) -> None:
        result = metric_result(
            make_input(
                make_selected("CashCashEquivalentsAndShortTermInvestments"),
                company_cik=789019,
            ),
            FinancialMetric.SHORT_TERM_INVESTMENTS,
        )
        self.assertIsInstance(result, MissingHistoricalMetric)

    def test_apple_long_term_marketable_securities_are_cik_scoped(self) -> None:
        apple_result = metric_result(
            make_input(
                make_selected(MARKETABLE_NONCURRENT, value=77_723),
                company_cik=320193,
            ),
            FinancialMetric.LONG_TERM_MARKETABLE_SECURITIES,
        )
        self.assertIsInstance(apple_result, NormalizedBalanceSheetValue)
        assert isinstance(apple_result, NormalizedBalanceSheetValue)
        self.assertIsInstance(apple_result.value, Decimal)
        self.assertEqual(apple_result.value, Decimal("77723"))
        self.assertEqual(apple_result.chosen_source.concept, MARKETABLE_NONCURRENT)

        for cik, concept in (
            (1326801, MARKETABLE_NONCURRENT),
            (1652044, "OtherLongTermInvestments"),
            (789019, "LongTermInvestments"),
            (909832, MARKETABLE_NONCURRENT),
        ):
            with self.subTest(cik=cik, concept=concept):
                result = metric_result(
                    make_input(make_selected(concept), company_cik=cik),
                    FinancialMetric.LONG_TERM_MARKETABLE_SECURITIES,
                )
                self.assertIsInstance(result, MissingHistoricalMetric)

    def test_apple_long_term_marketable_securities_preserve_zero_and_week_date(self) -> None:
        report_date = date(2025, 9, 27)
        result = metric_result(
            make_input(
                make_selected(MARKETABLE_NONCURRENT, value=0, end=report_date),
                company_cik=320193,
                filing=make_filing(report_date=report_date),
            ),
            FinancialMetric.LONG_TERM_MARKETABLE_SECURITIES,
        )

        self.assertIsInstance(result, NormalizedBalanceSheetValue)
        assert isinstance(result, NormalizedBalanceSheetValue)
        self.assertIsInstance(result.value, Decimal)
        self.assertEqual(result.value, Decimal("0"))
        self.assertEqual(result.balance_date, report_date)

    def test_meta_adjusted_trade_payables_preserve_two_stage_provenance(self) -> None:
        selected = make_input(
            make_selected("Revenues", value=1, start=date(2025, 1, 1)),
            make_selected(META_TRADE_PAYABLES, value=8_894_000_000),
            make_selected(COMBINED_PP_AND_E, value=9_331_000_000, start=date(2025, 1, 1)),
            company_cik=1326801,
        )
        accrued = make_filing_xbrl_fact(
            namespace=META_NAMESPACE,
            concept=ACCRUED_PP_AND_E,
            numeric_value=Decimal("4402000000"),
            raw_value="4402000000",
        )
        result = metric_result(
            selected,
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            filing_xbrl=(make_filing_xbrl(accrued, company_cik=1326801),),
        )

        self.assertIsInstance(result, DerivedBalanceSheetValue)
        assert isinstance(result, DerivedBalanceSheetValue)
        self.assertEqual(result.value, Decimal("3965000000"))
        self.assertEqual(
            tuple(operand.metric for operand in result.operands),
            (
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                FinancialMetric.PP_AND_E_PAYABLE_COMBINED,
                FinancialMetric.ACCRUED_PP_AND_E_PURCHASES,
            ),
        )
        self.assertEqual(
            tuple(operand.value for operand in result.operands),
            (8_894_000_000, 9_331_000_000, Decimal("4402000000")),
        )
        self.assertEqual(
            tuple((operand.start, operand.end, operand.unit) for operand in result.operands),
            (
                (None, REPORT_DATE, "USD"),
                (date(2025, 1, 1), REPORT_DATE, "USD"),
                (None, REPORT_DATE, "USD"),
            ),
        )
        self.assertIs(
            result.operands[0].chosen_source.source_kind,
            EvidenceSourceKind.COMPANY_FACTS,
        )
        self.assertIs(
            result.operands[1].chosen_source.source_kind,
            EvidenceSourceKind.COMPANY_FACTS,
        )
        self.assertIs(
            result.operands[2].chosen_source.source_kind,
            EvidenceSourceKind.FILING_XBRL,
        )
        reported_source = result.operands[0].chosen_source
        combined_source = result.operands[1].chosen_source
        accrued_source = result.operands[2].chosen_source
        self.assertEqual(reported_source.source_url, "facts-source")
        self.assertEqual(reported_source.taxonomy, "us-gaap")
        self.assertEqual(reported_source.concept, META_TRADE_PAYABLES)
        self.assertEqual(reported_source.accession_number, "annual")
        self.assertEqual(reported_source.observation_form, "10-K")
        self.assertEqual(reported_source.observation_filed, date(2026, 2, 1))
        self.assertEqual(combined_source.source_url, "facts-source")
        self.assertEqual(combined_source.taxonomy, "us-gaap")
        self.assertEqual(result.operands[1].chosen_source.concept, COMBINED_PP_AND_E)
        self.assertEqual(combined_source.accession_number, "annual")
        self.assertEqual(combined_source.start, date(2025, 1, 1))
        self.assertEqual(combined_source.end, REPORT_DATE)
        self.assertEqual(accrued_source.source_url, "https://www.sec.gov/example_htm.xml")
        self.assertEqual(accrued_source.namespace, META_NAMESPACE)
        self.assertEqual(result.operands[2].chosen_source.concept, ACCRUED_PP_AND_E)
        self.assertEqual(accrued_source.accession_number, "annual")
        self.assertEqual(accrued_source.context_id, "current")
        self.assertEqual(accrued_source.observation_form, "10-K")
        self.assertEqual(accrued_source.observation_filed, date(2026, 2, 1))
        self.assertEqual(accrued_source.filing_report_date, REPORT_DATE)
        self.assertEqual(accrued_source.primary_document, "annual.htm")
        self.assertEqual(accrued_source.retrieved_at, RETRIEVED_AT)
        self.assertEqual(accrued_source.dimensions, ())
        self.assertEqual(
            tuple((step.name, step.value) for step in result.steps),
            (
                ("pp_and_e_in_trade_accounts_payable", Decimal("4929000000")),
                ("adjusted_trade_accounts_payable", Decimal("3965000000")),
            ),
        )

    def test_meta_target_period_is_not_invalidated_by_unrelated_durations(self) -> None:
        annual_start = date(2025, 1, 1)
        unrelated = (
            make_selected("Revenues", start=annual_start),
            make_selected("PaymentsOfDividendsCommonStock", start=date(2025, 10, 1)),
        )
        for observations in (unrelated, tuple(reversed(unrelated))):
            selected = make_input(
                *observations,
                make_selected(META_TRADE_PAYABLES, value=100),
                make_selected(COMBINED_PP_AND_E, value=50, start=annual_start),
                company_cik=1326801,
            )
            accrued = make_filing_xbrl_fact(
                namespace=META_NAMESPACE,
                concept=ACCRUED_PP_AND_E,
                numeric_value=Decimal("20"),
                raw_value="20",
            )

            result = metric_result(
                selected,
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                filing_xbrl=(make_filing_xbrl(accrued, company_cik=1326801),),
            )

            self.assertIsInstance(result, DerivedBalanceSheetValue)
            self.assertEqual(result.value, Decimal("70"))

    def test_meta_target_period_does_not_assume_calendar_year_length(self) -> None:
        for start, end in (
            (date(2024, 9, 2), date(2025, 8, 31)),
            (date(2024, 9, 29), date(2025, 9, 27)),
        ):
            filing = make_filing(report_date=end)
            selected = make_input(
                make_selected(META_TRADE_PAYABLES, value=100, end=end),
                make_selected(COMBINED_PP_AND_E, value=50, start=start, end=end),
                company_cik=1326801,
                filing=filing,
            )
            accrued = make_filing_xbrl_fact(
                namespace=f"http://www.facebook.com/{end:%Y%m%d}",
                concept=ACCRUED_PP_AND_E,
                end=end,
                numeric_value=Decimal("20"),
                raw_value="20",
            )

            result = metric_result(
                selected,
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                filing_xbrl=(
                    make_filing_xbrl(
                        accrued,
                        company_cik=1326801,
                        filing=filing,
                    ),
                ),
            )

            self.assertIsInstance(result, DerivedBalanceSheetValue)
            self.assertEqual(result.value, Decimal("70"))
            self.assertEqual(result.operands[1].start, start)
            self.assertEqual(result.operands[1].end, end)

    def test_meta_competing_target_periods_are_ambiguous_and_order_independent(self) -> None:
        target_facts = (
            make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1)),
            make_selected(COMBINED_PP_AND_E, value=20, start=date(2025, 10, 1)),
        )
        fixed = (
            make_selected(META_TRADE_PAYABLES, value=100),
        )
        accrued = make_filing_xbrl_fact(
            namespace=META_NAMESPACE,
            concept=ACCRUED_PP_AND_E,
            numeric_value=Decimal("20"),
            raw_value="20",
        )
        artifact = (make_filing_xbrl(accrued, company_cik=1326801),)

        forward = metric_result(
            make_input(*target_facts, *fixed, company_cik=1326801),
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            filing_xbrl=artifact,
        )
        reverse = metric_result(
            make_input(*reversed(target_facts), *fixed, company_cik=1326801),
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            filing_xbrl=artifact,
        )

        self.assertIsInstance(forward, AmbiguousHistoricalMetric)
        assert isinstance(forward, AmbiguousHistoricalMetric)
        self.assertEqual(
            forward.reason,
            AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS,
        )
        self.assertEqual(len(forward.candidates), 2)
        self.assertEqual(forward, reverse)

    def test_meta_derivation_requires_valid_target_duration_and_all_operands(self) -> None:
        base = (make_selected(META_TRADE_PAYABLES, value=100),)
        artifact = make_filing_xbrl(
            make_filing_xbrl_fact(
                namespace=META_NAMESPACE,
                concept=ACCRUED_PP_AND_E,
                numeric_value=Decimal("20"),
                raw_value="20",
            ),
            company_cik=1326801,
        )
        cases = (
            base,
            (
                *base,
                make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1)),
            ),
            (
                make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1)),
            ),
            (*base, make_selected(COMBINED_PP_AND_E, value=50)),
            (*base, make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1), relationship=ObservationRelationship.COMPARATIVE)),
            (*base, make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1), end=date(2025, 12, 30))),
            (*base, make_selected(COMBINED_PP_AND_E, value=True, start=date(2025, 1, 1))),
            (*base, make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1), unit="EUR")),
        )
        artifacts = (
            (artifact,),
            (),
            (artifact,),
            (artifact,),
            (artifact,),
            (artifact,),
            (artifact,),
            (artifact,),
        )
        for observations, filing_xbrl in zip(cases, artifacts, strict=True):
            result = metric_result(
                make_input(*observations, company_cik=1326801),
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                filing_xbrl=filing_xbrl,
            )
            self.assertIsInstance(result, MissingHistoricalMetric)

    def test_meta_derivation_preserves_operand_ambiguity_deterministically(self) -> None:
        anchor = make_selected("Revenues", value=1, start=date(2025, 1, 1))
        reported = make_selected(META_TRADE_PAYABLES, value=100)
        combined = make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1))
        accrued = make_filing_xbrl_fact(
            namespace=META_NAMESPACE,
            concept=ACCRUED_PP_AND_E,
            numeric_value=Decimal("20"),
            raw_value="20",
            context_id="a",
        )
        cases = (
            (
                (anchor, reported, make_selected(META_TRADE_PAYABLES, value=101), combined),
                (accrued,),
            ),
            (
                (anchor, reported, combined, make_selected(COMBINED_PP_AND_E, value=51, start=date(2025, 1, 1))),
                (accrued,),
            ),
            (
                (anchor, reported, combined),
                (
                    accrued,
                    make_filing_xbrl_fact(
                        namespace=META_NAMESPACE,
                        concept=ACCRUED_PP_AND_E,
                        numeric_value=Decimal("21"),
                        raw_value="21",
                        context_id="b",
                    ),
                ),
            ),
        )
        for observations, facts in cases:
            forward = metric_result(
                make_input(*observations, company_cik=1326801),
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                filing_xbrl=(make_filing_xbrl(*facts, company_cik=1326801),),
            )
            reverse = metric_result(
                make_input(*reversed(observations), company_cik=1326801),
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                filing_xbrl=(make_filing_xbrl(*reversed(facts), company_cik=1326801),),
            )
            self.assertIsInstance(forward, AmbiguousHistoricalMetric)
            self.assertEqual(forward, reverse)

    def test_meta_derivation_is_cik_scoped_and_namespace_bound(self) -> None:
        observations = (
            make_selected("Revenues", value=1, start=date(2025, 1, 1)),
            make_selected(META_TRADE_PAYABLES, value=100),
            make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1)),
        )
        wrong_namespace = make_filing_xbrl_fact(
            namespace="http://www.facebook.com/20241231",
            concept=ACCRUED_PP_AND_E,
        )
        meta_result = metric_result(
            make_input(*observations, company_cik=1326801),
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
            filing_xbrl=(make_filing_xbrl(wrong_namespace, company_cik=1326801),),
        )
        other_result = metric_result(
            make_input(*observations, company_cik=1652044),
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )
        self.assertIsInstance(meta_result, MissingHistoricalMetric)
        self.assertNotIsInstance(other_result, DerivedBalanceSheetValue)

    def test_meta_derivation_preserves_zero_and_negative_results(self) -> None:
        cases = (
            (100, 20, Decimal("20"), Decimal("100"), Decimal("0")),
            (100, 10, Decimal("20"), Decimal("110"), Decimal("-10")),
            (10, 100, Decimal("20"), Decimal("-70"), Decimal("80")),
        )
        for reported, combined, accrued, adjusted, intermediate in cases:
            selected = make_input(
                make_selected("Revenues", value=1, start=date(2025, 1, 1)),
                make_selected(META_TRADE_PAYABLES, value=reported),
                make_selected(COMBINED_PP_AND_E, value=combined, start=date(2025, 1, 1)),
                company_cik=1326801,
            )
            fact = make_filing_xbrl_fact(
                namespace=META_NAMESPACE,
                concept=ACCRUED_PP_AND_E,
                numeric_value=accrued,
                raw_value=str(accrued),
            )
            result = metric_result(
                selected,
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                filing_xbrl=(make_filing_xbrl(fact, company_cik=1326801),),
            )
            self.assertIsInstance(result, DerivedBalanceSheetValue)
            self.assertEqual(result.value, adjusted)
            self.assertEqual(result.steps[0].value, intermediate)

    def test_meta_accrued_pp_and_e_prefix_is_irrelevant(self) -> None:
        selected = make_input(
            make_selected("Revenues", value=1, start=date(2025, 1, 1)),
            make_selected(META_TRADE_PAYABLES, value=100),
            make_selected(COMBINED_PP_AND_E, value=50, start=date(2025, 1, 1)),
            company_cik=1326801,
        )
        results = []
        for prefix in ("meta", "arbitrary"):
            content = f'''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
 xmlns:iso4217="{USD_NAMESPACE}" xmlns:{prefix}="{META_NAMESPACE}">
<xbrli:context id="current"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">1326801</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period></xbrli:context>
<xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
<{prefix}:{ACCRUED_PP_AND_E} contextRef="current" unitRef="USD" decimals="-6">20</{prefix}:{ACCRUED_PP_AND_E}>
</xbrli:xbrl>'''.encode()
            artifact = parse_filing_xbrl_instance(
                content,
                company=selected.company,
                filing=selected.annual[0].filing,
                source_url="https://www.sec.gov/meta.xml",
                retrieved_at=RETRIEVED_AT,
            )
            results.append(metric_result(selected, FinancialMetric.TRADE_ACCOUNTS_PAYABLE, filing_xbrl=(artifact,)))
        self.assertEqual(results[0], results[1])
        self.assertIsInstance(results[0], DerivedBalanceSheetValue)

    def test_google_accrued_customer_liabilities_resolve_with_full_provenance(self) -> None:
        fact = make_filing_xbrl_fact(
            concept=ACCRUED_CUSTOMER_LIABILITIES,
            numeric_value=Decimal("5029000000"),
            raw_value="5029000000",
        )
        result = metric_result(
            make_input(company_cik=1652044),
            FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
            filing_xbrl=(make_filing_xbrl(fact),),
        )

        self.assertIsInstance(result, NormalizedBalanceSheetValue)
        assert isinstance(result, NormalizedBalanceSheetValue)
        self.assertEqual(result.value, Decimal("5029000000"))
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.balance_date, REPORT_DATE)
        self.assertEqual(result.confirming_sources, ())
        self.assertIsInstance(result.chosen_source, FilingXBRLEvidence)
        source = result.chosen_source
        assert isinstance(source, FilingXBRLEvidence)
        self.assertIs(source.source_kind, EvidenceSourceKind.FILING_XBRL)
        self.assertEqual(source.namespace, GOOGLE_NAMESPACE)
        self.assertEqual(source.concept, ACCRUED_CUSTOMER_LIABILITIES)
        self.assertEqual(source.raw_value, "5029000000")
        self.assertEqual(source.value, Decimal("5029000000"))
        self.assertEqual(source.source_url, "https://www.sec.gov/example_htm.xml")
        self.assertIsNone(source.start)
        self.assertEqual(source.end, REPORT_DATE)
        self.assertEqual(source.accession_number, "annual")
        self.assertEqual(source.observation_form, "10-K")
        self.assertEqual(source.observation_filed, date(2026, 2, 1))
        self.assertEqual(source.filing_report_date, REPORT_DATE)
        self.assertEqual(source.primary_document, "annual.htm")
        self.assertEqual(source.retrieved_at, RETRIEVED_AT)
        self.assertEqual(source.context_id, "current")
        self.assertEqual(source.dimensions, ())
        self.assertEqual(source.decimals, "-6")
        self.assertFalse(source.is_nil)

    def test_google_accrued_customer_liabilities_are_cik_scoped_and_not_substituted(self) -> None:
        customer_fact = make_filing_xbrl_fact(
            concept=ACCRUED_CUSTOMER_LIABILITIES,
        )
        non_google = metric_result(
            make_input(company_cik=320193),
            FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
            filing_xbrl=(make_filing_xbrl(customer_fact, company_cik=320193),),
        )
        contract_fact = make_selected(CONTRACT_LIABILITIES, value=99)
        no_substitution = metric_result(
            make_input(contract_fact, company_cik=1652044),
            FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
        )

        self.assertIsInstance(non_google, MissingHistoricalMetric)
        self.assertIsInstance(no_substitution, MissingHistoricalMetric)
        self.assertIs(
            non_google.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )
        self.assertIs(
            no_substitution.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_google_accrued_customer_liabilities_share_filing_xbrl_safeguards(self) -> None:
        dimension = FilingXBRLDimension(
            dimension=FilingXBRLQName("http://example.com", "Axis"),
            explicit_member=FilingXBRLQName("http://example.com", "Member"),
            typed_member_xml=None,
        )
        eur = FilingXBRLUnit(
            unit_id="EUR",
            numerator_measures=(FilingXBRLQName(USD_NAMESPACE, "EUR"),),
            denominator_measures=(),
        )
        cases = (
            make_filing_xbrl_fact(
                concept=ACCRUED_CUSTOMER_LIABILITIES,
                accession="other",
            ),
            make_filing_xbrl_fact(
                concept=ACCRUED_CUSTOMER_LIABILITIES,
                end=date(2024, 12, 31),
            ),
            make_filing_xbrl_fact(
                concept=ACCRUED_CUSTOMER_LIABILITIES,
                namespace="http://www.google.com/20241231",
            ),
            make_filing_xbrl_fact(
                concept=ACCRUED_CUSTOMER_LIABILITIES,
                dimensions=(dimension,),
            ),
            make_filing_xbrl_fact(concept=ACCRUED_CUSTOMER_LIABILITIES, unit=eur),
            make_filing_xbrl_fact(
                concept=ACCRUED_CUSTOMER_LIABILITIES,
                is_nil=True,
                numeric_value=None,
                raw_value=None,
            ),
            make_filing_xbrl_fact(
                concept=ACCRUED_CUSTOMER_LIABILITIES,
                numeric_value="10",
            ),
        )
        for fact in cases:
            with self.subTest(fact=fact):
                result = metric_result(
                    make_input(company_cik=1652044),
                    FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
                    filing_xbrl=(make_filing_xbrl(fact),),
                )
                self.assertIsInstance(result, MissingHistoricalMetric)

    def test_google_accrued_customer_liability_prefix_is_irrelevant(self) -> None:
        results = tuple(
            metric_result(
                make_input(company_cik=1652044),
                FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
                filing_xbrl=(
                    make_prefixed_filing_xbrl(
                        prefix,
                        ACCRUED_CUSTOMER_LIABILITIES,
                    ),
                ),
            )
            for prefix in ("goog", "arbitrary")
        )
        self.assertEqual(results[0], results[1])
        self.assertIsInstance(results[0], NormalizedBalanceSheetValue)

    def test_google_accrued_customer_liability_zero_negative_and_ambiguity(self) -> None:
        for value in (Decimal("0"), Decimal("-10")):
            result = metric_result(
                make_input(company_cik=1652044),
                FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
                filing_xbrl=(
                    make_filing_xbrl(
                        make_filing_xbrl_fact(
                            concept=ACCRUED_CUSTOMER_LIABILITIES,
                            numeric_value=value,
                            raw_value=str(value),
                        )
                    ),
                ),
            )
            self.assertIsInstance(result, NormalizedBalanceSheetValue)
            self.assertEqual(result.value, value)

        for values in (
            ((Decimal("10"), "a"), (Decimal("11"), "b")),
            ((Decimal("10"), "a"), (Decimal("10"), "equivalent")),
        ):
            facts = tuple(
                make_filing_xbrl_fact(
                    concept=ACCRUED_CUSTOMER_LIABILITIES,
                    numeric_value=value,
                    raw_value=str(value),
                    context_id=context,
                )
                for value, context in values
            )
            forward = metric_result(
                make_input(company_cik=1652044),
                FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
                filing_xbrl=(make_filing_xbrl(*facts),),
            )
            reverse = metric_result(
                make_input(company_cik=1652044),
                FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
                filing_xbrl=(make_filing_xbrl(*reversed(facts)),),
            )
            self.assertIsInstance(forward, AmbiguousHistoricalMetric)
            self.assertEqual(forward, reverse)

    def test_google_accrued_revenue_share_resolves_with_full_provenance(self) -> None:
        fact = make_filing_xbrl_fact()
        artifact = make_filing_xbrl(fact)
        result = metric_result(
            make_input(company_cik=1652044),
            FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
            filing_xbrl=(artifact,),
        )

        self.assertIsInstance(result, NormalizedBalanceSheetValue)
        assert isinstance(result, NormalizedBalanceSheetValue)
        self.assertEqual(result.value, Decimal("10864000000"))
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.balance_date, REPORT_DATE)
        self.assertEqual(result.confirming_sources, ())
        self.assertIsInstance(result.chosen_source, FilingXBRLEvidence)
        source = result.chosen_source
        assert isinstance(source, FilingXBRLEvidence)
        self.assertIs(source.source_kind, EvidenceSourceKind.FILING_XBRL)
        self.assertEqual(source.namespace, GOOGLE_NAMESPACE)
        self.assertEqual(source.concept, ACCRUED_REVENUE_SHARE)
        self.assertEqual(source.raw_value, "10864000000")
        self.assertEqual(source.value, Decimal("10864000000"))
        self.assertEqual(source.unit, "USD")
        self.assertIsNone(source.start)
        self.assertEqual(source.end, REPORT_DATE)
        self.assertEqual(source.accession_number, "annual")
        self.assertEqual(source.observation_form, "10-K")
        self.assertEqual(source.observation_filed, date(2026, 2, 1))
        self.assertEqual(source.filing_report_date, REPORT_DATE)
        self.assertEqual(source.primary_document, "annual.htm")
        self.assertEqual(source.retrieved_at, RETRIEVED_AT)
        self.assertEqual(source.context_id, "current")
        self.assertEqual(source.dimensions, ())
        self.assertEqual(source.decimals, "-6")
        self.assertFalse(source.is_nil)
        self.assertEqual(source.source_url, "https://www.sec.gov/example_htm.xml")

    def test_filing_xbrl_candidate_is_cik_scoped(self) -> None:
        fact = make_filing_xbrl_fact()
        artifact = make_filing_xbrl(fact, company_cik=320193)
        result = metric_result(
            make_input(company_cik=320193),
            FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
            filing_xbrl=(artifact,),
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_filing_xbrl_namespace_matches_report_date(self) -> None:
        accepted = make_filing_xbrl_fact(namespace=GOOGLE_NAMESPACE)
        rejected_namespaces = (
            "http://www.google.com/99999999",
            "http://www.google.com/20241231",
            "http://www.apple.com/20251231",
        )
        accepted_result = metric_result(
            make_input(company_cik=1652044),
            FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
            filing_xbrl=(make_filing_xbrl(accepted),),
        )
        self.assertIsInstance(accepted_result, NormalizedBalanceSheetValue)

        for namespace in rejected_namespaces:
            with self.subTest(namespace=namespace):
                result = metric_result(
                    make_input(company_cik=1652044),
                    FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                    filing_xbrl=(
                        make_filing_xbrl(
                            make_filing_xbrl_fact(namespace=namespace)
                        ),
                    ),
                )
                self.assertIsInstance(result, MissingHistoricalMetric)

    def test_filing_xbrl_prefix_does_not_affect_semantic_matching(self) -> None:
        results = tuple(
            metric_result(
                make_input(company_cik=1652044),
                FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                filing_xbrl=(make_prefixed_filing_xbrl(prefix),),
            )
            for prefix in ("goog", "arbitrary")
        )

        self.assertEqual(results[0], results[1])
        self.assertIsInstance(results[0], NormalizedBalanceSheetValue)

    def test_missing_filing_xbrl_artifact_is_typed_missing(self) -> None:
        result = metric_result(
            make_input(company_cik=1652044),
            FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_filing_xbrl_artifact_company_mismatch_is_rejected(self) -> None:
        artifact = make_filing_xbrl(
            make_filing_xbrl_fact(),
            company_cik=320193,
        )

        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "company does not match selected company",
        ):
            normalize_annual_balance_sheets(
                make_input(company_cik=1652044),
                filing_xbrl=(artifact,),
            )

    def test_filing_xbrl_artifact_metadata_mismatch_is_rejected(self) -> None:
        mismatched_filing = SECFiling(
            accession_number="annual",
            form="10-K",
            filing_date=date(2026, 2, 2),
            report_date=REPORT_DATE,
            primary_document="annual.htm",
        )
        artifact = make_filing_xbrl(
            make_filing_xbrl_fact(),
            filing=mismatched_filing,
        )

        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "filing metadata does not match selected filing",
        ):
            normalize_annual_balance_sheets(
                make_input(company_cik=1652044),
                filing_xbrl=(artifact,),
            )

    def test_duplicate_filing_xbrl_artifacts_are_rejected(self) -> None:
        artifact = make_filing_xbrl(make_filing_xbrl_fact())

        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "duplicate accession",
        ):
            normalize_annual_balance_sheets(
                make_input(company_cik=1652044),
                filing_xbrl=(artifact, artifact),
            )

    def test_different_accession_artifact_cannot_satisfy_selected_filing(self) -> None:
        other_filing = make_filing(accession="other")
        artifact = make_filing_xbrl(
            make_filing_xbrl_fact(accession="other"),
            filing=other_filing,
        )
        result = metric_result(
            make_input(company_cik=1652044),
            FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
            filing_xbrl=(artifact,),
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_filing_xbrl_structural_failures_are_ineligible(self) -> None:
        eur_unit = FilingXBRLUnit(
            unit_id="EUR",
            numerator_measures=(FilingXBRLQName(USD_NAMESPACE, "EUR"),),
            denominator_measures=(),
        )
        dimension = FilingXBRLDimension(
            dimension=FilingXBRLQName("http://example.com", "Axis"),
            explicit_member=FilingXBRLQName("http://example.com", "Member"),
            typed_member_xml=None,
        )
        cases = (
            make_filing_xbrl_fact(accession="other"),
            make_filing_xbrl_fact(end=date(2024, 12, 31)),
            make_filing_xbrl_fact(start=date(2025, 1, 1)),
            make_filing_xbrl_fact(dimensions=(dimension,)),
            make_filing_xbrl_fact(unit=eur_unit),
            make_filing_xbrl_fact(is_nil=True, numeric_value=None, raw_value=None),
            make_filing_xbrl_fact(numeric_value="10864000000"),
            make_filing_xbrl_fact(numeric_value=True),
        )
        for fact in cases:
            with self.subTest(fact=fact):
                result = metric_result(
                    make_input(company_cik=1652044),
                    FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                    filing_xbrl=(make_filing_xbrl(fact),),
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_VALID_CURRENT_INSTANT_OBSERVATION,
                )

    def test_filing_xbrl_zero_and_negative_values_are_preserved(self) -> None:
        for value in (Decimal("0"), Decimal("-10")):
            with self.subTest(value=value):
                fact = make_filing_xbrl_fact(
                    numeric_value=value,
                    raw_value=str(value),
                )
                result = metric_result(
                    make_input(company_cik=1652044),
                    FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                    filing_xbrl=(make_filing_xbrl(fact),),
                )
                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.value, value)

    def test_multiple_filing_xbrl_facts_are_ambiguous_without_overwrite(self) -> None:
        first = make_filing_xbrl_fact(
            numeric_value=Decimal("10"),
            raw_value="10",
            context_id="first",
        )
        second = make_filing_xbrl_fact(
            numeric_value=Decimal("11"),
            raw_value="11",
            context_id="second",
        )
        equivalent = make_filing_xbrl_fact(
            numeric_value=Decimal("10"),
            raw_value="10",
            context_id="equivalent-context",
        )
        for facts in ((first, second), (first, equivalent)):
            with self.subTest(facts=facts):
                forward = metric_result(
                    make_input(company_cik=1652044),
                    FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                    filing_xbrl=(make_filing_xbrl(*facts),),
                )
                reverse = metric_result(
                    make_input(company_cik=1652044),
                    FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                    filing_xbrl=(make_filing_xbrl(*reversed(facts)),),
                )
                self.assertIsInstance(forward, AmbiguousHistoricalMetric)
                self.assertIsInstance(reverse, AmbiguousHistoricalMetric)
                self.assertEqual(forward, reverse)
                assert isinstance(forward, AmbiguousHistoricalMetric)
                self.assertEqual(len(forward.candidates), 2)

    def test_company_facts_policies_do_not_use_filing_xbrl_automatically(self) -> None:
        artifact = make_filing_xbrl(
            make_filing_xbrl_fact(concept=INVENTORY),
            company_cik=1652044,
        )
        result = metric_result(
            make_input(company_cik=1652044),
            FinancialMetric.INVENTORY,
            filing_xbrl=(artifact,),
        )

        self.assertIsInstance(result, MissingHistoricalMetric)

    def test_apple_distribution_and_marketing_remains_unsupported(self) -> None:
        artifact = make_filing_xbrl(
            make_filing_xbrl_fact(
                namespace="http://www.apple.com/20250927",
                concept="AccruedDistributionAndMarketingCurrent",
            ),
            company_cik=320193,
        )
        output = normalize_annual_balance_sheets(
            make_input(company_cik=320193),
            filing_xbrl=(artifact,),
        )

        self.assertNotIn(
            "AccruedDistributionAndMarketingCurrent",
            tuple(
                candidate.name
                for policy in output.annual[0].metrics
                if isinstance(policy, MissingHistoricalMetric)
                for candidate in policy.examined_concepts
            ),
        )

    def test_current_instant_receivable_resolves_with_provenance(self) -> None:
        result = metric_result(
            make_input(make_selected(RECEIVABLES, value=125)),
            FinancialMetric.OPERATING_RECEIVABLES,
        )

        self.assertIsInstance(result, NormalizedBalanceSheetValue)
        assert isinstance(result, NormalizedBalanceSheetValue)
        self.assertIsInstance(result.value, Decimal)
        self.assertEqual(result.value, Decimal("125"))
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.balance_date, REPORT_DATE)
        self.assertEqual(result.confirming_sources, ())
        source = result.chosen_source
        self.assertIs(source.source_kind, EvidenceSourceKind.COMPANY_FACTS)
        self.assertEqual(source.source_url, "facts-source")
        self.assertEqual(source.taxonomy, "us-gaap")
        self.assertEqual(source.concept, RECEIVABLES)
        self.assertEqual(source.value, 125)
        self.assertIs(type(source.value), int)
        self.assertEqual(source.unit, "USD")
        self.assertIsNone(source.start)
        self.assertEqual(source.end, REPORT_DATE)
        self.assertEqual(source.accession_number, "annual")
        self.assertEqual(source.observation_form, "10-K")
        self.assertEqual(source.observation_filed, date(2026, 2, 1))
        self.assertEqual(source.fiscal_year, 2025)
        self.assertEqual(source.fiscal_period, "FY")
        self.assertEqual(source.frame, "CY2025Q4I")

    def test_exact_selected_accession_is_required(self) -> None:
        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "does not match filing accession",
        ):
            normalize_annual_balance_sheets(
                make_input(make_selected(RECEIVABLES, accession="other"))
            )

    def test_zero_and_negative_values_are_preserved(self) -> None:
        for value in (0, -10):
            with self.subTest(value=value):
                result = metric_result(
                    make_input(make_selected(INVENTORY, value=value)),
                    FinancialMetric.INVENTORY,
                )
                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.value, value)

    def test_structurally_invalid_observations_are_typed_missing(self) -> None:
        cases = (
            make_selected(
                RECEIVABLES,
                relationship=ObservationRelationship.COMPARATIVE,
            ),
            make_selected(RECEIVABLES, start=date(2025, 1, 1)),
            make_selected(RECEIVABLES, end=date(2025, 12, 30)),
            make_selected(RECEIVABLES, unit="EUR"),
            make_selected(RECEIVABLES, value="100"),
            make_selected(RECEIVABLES, value=True),
        )
        for observation in cases:
            with self.subTest(observation=observation):
                result = metric_result(
                    make_input(observation),
                    FinancialMetric.OPERATING_RECEIVABLES,
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_VALID_CURRENT_INSTANT_OBSERVATION,
                )

    def test_missing_inventory_is_not_zero(self) -> None:
        result = metric_result(make_input(), FinancialMetric.INVENTORY)

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_multiple_eligible_observations_for_one_concept_are_ambiguous(self) -> None:
        result = metric_result(
            make_input(
                make_selected(INVENTORY, value=10),
                make_selected(INVENTORY, value=11),
            ),
            FinancialMetric.INVENTORY,
        )

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertIs(result.reason, AmbiguityReason.CONFLICTING_CONCEPT_VALUES)
        self.assertEqual(tuple(item.value for item in result.candidates), (10, 11))

    def test_cost_receivables_fallback_is_cik_scoped(self) -> None:
        cost_result = metric_result(
            make_input(
                make_selected("ReceivablesNetCurrent", value=3_203),
                company_cik=909832,
            ),
            FinancialMetric.OPERATING_RECEIVABLES,
        )
        other_result = metric_result(
            make_input(make_selected("ReceivablesNetCurrent", value=3_203)),
            FinancialMetric.OPERATING_RECEIVABLES,
        )

        self.assertIsInstance(cost_result, NormalizedBalanceSheetValue)
        assert isinstance(cost_result, NormalizedBalanceSheetValue)
        self.assertEqual(cost_result.chosen_source.concept, "ReceivablesNetCurrent")
        self.assertIsInstance(other_result, MissingHistoricalMetric)

    def test_eligible_scoped_fallback_ignores_ineligible_primary(self) -> None:
        primary = make_selected(RECEIVABLES, value=4_000, unit="EUR")
        fallback = make_selected("ReceivablesNetCurrent", value=3_203)

        for observations in ((primary, fallback), (fallback, primary)):
            with self.subTest(observations=observations):
                result = metric_result(
                    make_input(*observations, company_cik=909832),
                    FinancialMetric.OPERATING_RECEIVABLES,
                )

                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.value, 3_203)
                self.assertEqual(
                    result.chosen_source.concept,
                    "ReceivablesNetCurrent",
                )
                self.assertEqual(result.confirming_sources, ())

    def test_meta_trade_payables_fallback_is_cik_scoped(self) -> None:
        meta_output = normalize_annual_balance_sheets(
            make_input(
                make_selected("AccountsPayableTradeCurrent", value=8_894),
                company_cik=1326801,
            ),
            policies=(TRADE_ACCOUNTS_PAYABLE_POLICY,),
        )
        meta_result = meta_output.annual[0].metrics[0]
        other_result = metric_result(
            make_input(make_selected("AccountsPayableTradeCurrent", value=8_894)),
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )

        self.assertIsInstance(meta_result, NormalizedBalanceSheetValue)
        assert isinstance(meta_result, NormalizedBalanceSheetValue)
        self.assertEqual(
            meta_result.chosen_source.concept,
            "AccountsPayableTradeCurrent",
        )
        self.assertIsInstance(other_result, MissingHistoricalMetric)

    def test_cost_deferred_revenue_fallback_is_cik_scoped(self) -> None:
        cost_result = metric_result(
            make_input(
                make_selected("DeferredRevenueCurrent", value=2_854),
                company_cik=909832,
            ),
            FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
        )
        other_result = metric_result(
            make_input(make_selected("DeferredRevenueCurrent", value=2_854)),
            FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
        )

        self.assertIsInstance(cost_result, NormalizedBalanceSheetValue)
        assert isinstance(cost_result, NormalizedBalanceSheetValue)
        self.assertEqual(cost_result.chosen_source.concept, "DeferredRevenueCurrent")
        self.assertIsInstance(other_result, MissingHistoricalMetric)

    def test_apple_vendor_nontrade_receivables_are_cik_scoped(self) -> None:
        apple_result = metric_result(
            make_input(
                make_selected(VENDOR_RECEIVABLES, value=33_180),
                company_cik=320193,
            ),
            FinancialMetric.VENDOR_NONTRADE_RECEIVABLES,
        )
        other_result = metric_result(
            make_input(make_selected(VENDOR_RECEIVABLES, value=33_180)),
            FinancialMetric.VENDOR_NONTRADE_RECEIVABLES,
        )

        self.assertIsInstance(apple_result, NormalizedBalanceSheetValue)
        assert isinstance(apple_result, NormalizedBalanceSheetValue)
        self.assertEqual(apple_result.value, 33_180)
        self.assertEqual(apple_result.chosen_source.concept, VENDOR_RECEIVABLES)
        self.assertIsInstance(other_result, MissingHistoricalMetric)

    def test_employee_related_liabilities_are_supported_for_approved_ciks(self) -> None:
        for cik in (1326801, 1652044, 789019, 909832):
            with self.subTest(cik=cik):
                result = metric_result(
                    make_input(
                        make_selected(EMPLOYEE_LIABILITIES, value=7_151),
                        company_cik=cik,
                    ),
                    FinancialMetric.EMPLOYEE_RELATED_LIABILITIES,
                )
                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.chosen_source.concept, EMPLOYEE_LIABILITIES)

    def test_apple_employee_related_liabilities_remain_missing(self) -> None:
        result = metric_result(
            make_input(
                make_selected(EMPLOYEE_LIABILITIES, value=7_151),
                company_cik=320193,
            ),
            FinancialMetric.EMPLOYEE_RELATED_LIABILITIES,
        )

        self.assertIsInstance(result, MissingHistoricalMetric)
        assert isinstance(result, MissingHistoricalMetric)
        self.assertIs(
            result.reason,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
        )

    def test_cost_member_rewards_are_cik_scoped(self) -> None:
        cost_result = metric_result(
            make_input(
                make_selected(MEMBER_REWARDS, value=2_677),
                company_cik=909832,
            ),
            FinancialMetric.MEMBER_REWARDS_LIABILITY,
        )
        other_result = metric_result(
            make_input(make_selected(MEMBER_REWARDS, value=2_677)),
            FinancialMetric.MEMBER_REWARDS_LIABILITY,
        )

        self.assertIsInstance(cost_result, NormalizedBalanceSheetValue)
        assert isinstance(cost_result, NormalizedBalanceSheetValue)
        self.assertEqual(cost_result.value, 2_677)
        self.assertEqual(cost_result.chosen_source.concept, MEMBER_REWARDS)
        self.assertIsInstance(other_result, MissingHistoricalMetric)

    def test_new_primitive_values_preserve_zero_negative_and_balance_date(self) -> None:
        report_date = date(2023, 9, 3)
        for value in (0, -10):
            with self.subTest(value=value):
                result = metric_result(
                    make_input(
                        make_selected(
                            MEMBER_REWARDS,
                            value=value,
                            end=report_date,
                        ),
                        company_cik=909832,
                        filing=make_filing(report_date=report_date),
                    ),
                    FinancialMetric.MEMBER_REWARDS_LIABILITY,
                )
                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.value, value)
                self.assertEqual(result.balance_date, report_date)

    def test_new_primitive_structural_failures_are_ineligible(self) -> None:
        cases = (
            make_selected(
                EMPLOYEE_LIABILITIES,
                relationship=ObservationRelationship.COMPARATIVE,
            ),
            make_selected(EMPLOYEE_LIABILITIES, start=date(2025, 1, 1)),
            make_selected(EMPLOYEE_LIABILITIES, end=date(2025, 12, 30)),
            make_selected(EMPLOYEE_LIABILITIES, unit="EUR"),
            make_selected(EMPLOYEE_LIABILITIES, value="100"),
            make_selected(EMPLOYEE_LIABILITIES, value=True),
        )
        for observation in cases:
            with self.subTest(observation=observation):
                result = metric_result(
                    make_input(observation, company_cik=1326801),
                    FinancialMetric.EMPLOYEE_RELATED_LIABILITIES,
                )
                self.assertIsInstance(result, MissingHistoricalMetric)
                assert isinstance(result, MissingHistoricalMetric)
                self.assertIs(
                    result.reason,
                    MissingReason.NO_VALID_CURRENT_INSTANT_OBSERVATION,
                )

    def test_new_primitive_requires_selected_accession(self) -> None:
        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "does not match filing accession",
        ):
            normalize_annual_balance_sheets(
                make_input(
                    make_selected(EMPLOYEE_LIABILITIES, accession="other"),
                    company_cik=1326801,
                )
            )

    def test_multiple_member_rewards_observations_are_ambiguous(self) -> None:
        result = metric_result(
            make_input(
                make_selected(MEMBER_REWARDS, value=10),
                make_selected(MEMBER_REWARDS, value=11),
                company_cik=909832,
            ),
            FinancialMetric.MEMBER_REWARDS_LIABILITY,
        )

        self.assertIsInstance(result, AmbiguousHistoricalMetric)
        assert isinstance(result, AmbiguousHistoricalMetric)
        self.assertEqual(tuple(item.value for item in result.candidates), (10, 11))

    def test_priority_does_not_hide_overlapping_approved_concepts(self) -> None:
        for values in ((10, 11), (10, 10)):
            with self.subTest(values=values):
                result = metric_result(
                    make_input(
                        make_selected(RECEIVABLES, value=values[0]),
                        make_selected("ReceivablesNetCurrent", value=values[1]),
                        company_cik=909832,
                    ),
                    FinancialMetric.OPERATING_RECEIVABLES,
                )
                self.assertIsInstance(result, AmbiguousHistoricalMetric)
                assert isinstance(result, AmbiguousHistoricalMetric)
                self.assertEqual(
                    tuple(item.concept for item in result.candidates),
                    (RECEIVABLES, "ReceivablesNetCurrent"),
                )

    def test_unapproved_concepts_and_broad_residuals_are_not_fallbacks(self) -> None:
        cases = (
            ("AccountsNotesAndLoansReceivableNetCurrent", FinancialMetric.OPERATING_RECEIVABLES),
            ("NontradeReceivablesCurrent", FinancialMetric.OPERATING_RECEIVABLES),
            ("OtherAssetsCurrent", FinancialMetric.OPERATING_RECEIVABLES),
            ("OtherLiabilitiesCurrent", FinancialMetric.TRADE_ACCOUNTS_PAYABLE),
        )
        for concept, metric in cases:
            with self.subTest(concept=concept):
                result = metric_result(make_input(make_selected(concept)), metric)
                self.assertIsInstance(result, MissingHistoricalMetric)

    def test_metrics_resolve_independently_in_deterministic_order(self) -> None:
        output = normalize_annual_balance_sheets(
            make_input(
                make_selected(RECEIVABLES, value=100),
                make_selected(PAYABLES, value=40),
            )
        )

        self.assertEqual(
            tuple(result.metric for result in output.annual[0].metrics),
            (
                FinancialMetric.OPERATING_RECEIVABLES,
                FinancialMetric.VENDOR_NONTRADE_RECEIVABLES,
                FinancialMetric.INVENTORY,
                FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
                FinancialMetric.ACCRUED_PP_AND_E_PURCHASES,
                FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
                FinancialMetric.EMPLOYEE_RELATED_LIABILITIES,
                FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                FinancialMetric.ACCRUED_CUSTOMER_LIABILITIES,
                FinancialMetric.MEMBER_REWARDS_LIABILITY,
                FinancialMetric.CASH_AND_CASH_EQUIVALENTS,
                FinancialMetric.SHORT_TERM_INVESTMENTS,
                FinancialMetric.LONG_TERM_MARKETABLE_SECURITIES,
                FinancialMetric.COMMERCIAL_PAPER,
                FinancialMetric.SHORT_TERM_BORROWINGS,
                FinancialMetric.CURRENT_PORTION_OF_LONG_TERM_DEBT,
                FinancialMetric.LONG_TERM_DEBT_NONCURRENT,
            ),
        )
        by_metric = {item.metric: item for item in output.annual[0].metrics}
        self.assertIsInstance(
            by_metric[FinancialMetric.OPERATING_RECEIVABLES],
            NormalizedBalanceSheetValue,
        )
        self.assertIsInstance(
            by_metric[FinancialMetric.TRADE_ACCOUNTS_PAYABLE],
            NormalizedBalanceSheetValue,
        )
        self.assertIsInstance(
            by_metric[FinancialMetric.INVENTORY],
            MissingHistoricalMetric,
        )
        self.assertIsInstance(
            by_metric[FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES],
            MissingHistoricalMetric,
        )

    def test_non_calendar_and_week_based_balance_dates_are_preserved(self) -> None:
        dates = (
            date(2025, 6, 30),
            date(2025, 9, 27),
            date(2023, 9, 3),
        )
        for report_date in dates:
            with self.subTest(report_date=report_date):
                result = metric_result(
                    make_input(
                        make_selected(INVENTORY, end=report_date),
                        filing=make_filing(report_date=report_date),
                    ),
                    FinancialMetric.INVENTORY,
                )
                self.assertIsInstance(result, NormalizedBalanceSheetValue)
                assert isinstance(result, NormalizedBalanceSheetValue)
                self.assertEqual(result.balance_date, report_date)

    def test_non_10_k_selected_filing_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "requires exact 10-K",
        ):
            normalize_annual_balance_sheets(
                make_input(filing=make_filing(form="10-Q"))
            )

    def test_selected_filing_without_report_date_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            BalanceSheetNormalizationError,
            "has no report date",
        ):
            normalize_annual_balance_sheets(
                make_input(filing=make_filing(report_date=None))
            )

    def test_output_preserves_filing_and_company_source_metadata(self) -> None:
        output = normalize_annual_balance_sheets(
            make_input(make_selected(INVENTORY, value=25))
        )

        self.assertEqual(output.company.ticker, "TEST")
        self.assertEqual(output.company_facts_source_url, "facts-source")
        self.assertEqual(output.company_facts_retrieved_at, RETRIEVED_AT)
        self.assertEqual(output.annual[0].filing.accession_number, "annual")
