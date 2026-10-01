from datetime import date, datetime, timezone
from decimal import Decimal
from unittest import TestCase

from valuation_platform.normalization import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    BalanceSheetNormalizationError,
    EvidenceSourceKind,
    FilingXBRLEvidence,
    FinancialMetric,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedBalanceSheetValue,
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
GOOGLE_NAMESPACE = "http://www.google.com/20251231"
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
    value: object = 1,
    accession: str = "annual",
    start: date | None = None,
    end: date = REPORT_DATE,
    unit: str = "USD",
    relationship: ObservationRelationship = ObservationRelationship.CURRENT,
) -> SelectedFactObservation:
    return SelectedFactObservation(
        taxonomy="us-gaap",
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


def make_prefixed_filing_xbrl(prefix: str) -> SECFilingXBRL:
    selected = make_input(company_cik=1652044)
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
 xmlns:iso4217="{USD_NAMESPACE}" xmlns:{prefix}="{GOOGLE_NAMESPACE}">
  <xbrli:context id="current">
    <xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">1652044</xbrli:identifier></xbrli:entity>
    <xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period>
  </xbrli:context>
  <xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
  <{prefix}:AccruedRevenueShare contextRef="current" unitRef="USD" decimals="-6">10864000000</{prefix}:AccruedRevenueShare>
</xbrli:xbrl>""".encode()
    return parse_filing_xbrl_instance(
        content,
        company=selected.company,
        filing=selected.annual[0].filing,
        source_url="https://www.sec.gov/example_htm.xml",
        retrieved_at=RETRIEVED_AT,
    )


class AnnualBalanceSheetNormalizationTests(TestCase):
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
        self.assertEqual(result.value, 125)
        self.assertEqual(result.unit, "USD")
        self.assertEqual(result.balance_date, REPORT_DATE)
        self.assertEqual(result.confirming_sources, ())
        source = result.chosen_source
        self.assertIs(source.source_kind, EvidenceSourceKind.COMPANY_FACTS)
        self.assertEqual(source.source_url, "facts-source")
        self.assertEqual(source.taxonomy, "us-gaap")
        self.assertEqual(source.concept, RECEIVABLES)
        self.assertEqual(source.value, 125)
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
        meta_result = metric_result(
            make_input(
                make_selected("AccountsPayableTradeCurrent", value=8_894),
                company_cik=1326801,
            ),
            FinancialMetric.TRADE_ACCOUNTS_PAYABLE,
        )
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
                FinancialMetric.CUSTOMER_CONTRACT_LIABILITIES,
                FinancialMetric.EMPLOYEE_RELATED_LIABILITIES,
                FinancialMetric.ACCRUED_REVENUE_SHARE_LIABILITY,
                FinancialMetric.MEMBER_REWARDS_LIABILITY,
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
