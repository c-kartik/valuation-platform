from dataclasses import replace
from datetime import date, datetime, timezone
from unittest import TestCase

from valuation_platform.sec import (
    AmbiguousAnnualPeriod,
    AnnualPeriodDataErrorResult,
    AnnualPeriodNotFound,
    AnnualPeriodResolutionStatus,
    FilingXBRLContext,
    FilingXBRLDimension,
    FilingXBRLFact,
    FilingXBRLQName,
    ResolvedAnnualPeriod,
    SECCompanyIdentity,
    SECFiling,
    SECFilingXBRL,
    UnsupportedAnnualPeriod,
    resolve_annual_period,
)


DEI_NAMESPACE = "http://xbrl.sec.gov/dei/2025"
SEC_CIK_SCHEME = "http://www.sec.gov/CIK"
SOURCE_URL = "https://www.sec.gov/Archives/edgar/data/1/test_htm.xml"
RETRIEVED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_company() -> SECCompanyIdentity:
    return SECCompanyIdentity(
        ticker="TEST",
        cik=1,
        cik_padded="0000000001",
        company_name="Test Company",
        source_url="ticker-source",
        retrieved_at=RETRIEVED_AT,
    )


def make_filing(
    *,
    form: str = "10-K",
    report_date: date | None = date(2025, 12, 31),
) -> SECFiling:
    return SECFiling(
        accession_number="0000000001-26-000001",
        form=form,
        filing_date=date(2026, 2, 1),
        report_date=report_date,
        primary_document="test-20251231.htm",
    )


def make_context(
    context_id: str,
    *,
    start: date = date(2025, 1, 1),
    end: date = date(2025, 12, 31),
    scheme: str = SEC_CIK_SCHEME,
    identifier: str = "0000000001",
    dimensions: tuple[FilingXBRLDimension, ...] = (),
) -> FilingXBRLContext:
    return FilingXBRLContext(
        context_id=context_id,
        entity_identifier_scheme=scheme,
        entity_identifier=identifier,
        start=start,
        end=end,
        dimensions=dimensions,
    )


def make_fact(
    context: FilingXBRLContext,
    concept: str,
    value: str,
    *,
    namespace: str = DEI_NAMESPACE,
) -> FilingXBRLFact:
    return FilingXBRLFact(
        namespace=namespace,
        concept=concept,
        context_id=context.context_id,
        start=context.start,
        end=context.end,
        dimensions=context.dimensions,
        unit_ref=None,
        unit=None,
        raw_value=value,
        numeric_value=None,
        decimals=None,
        is_nil=False,
        accession_number="0000000001-26-000001",
        source_url=SOURCE_URL,
    )


def make_dei_facts(
    context: FilingXBRLContext,
    *,
    fiscal_period: str = "FY",
    fiscal_year: str = "2025",
    document_end: str = "2025-12-31",
) -> tuple[FilingXBRLFact, ...]:
    return (
        make_fact(context, "DocumentFiscalPeriodFocus", fiscal_period),
        make_fact(context, "DocumentFiscalYearFocus", fiscal_year),
        make_fact(context, "DocumentPeriodEndDate", document_end),
    )


def make_xbrl(
    contexts: tuple[FilingXBRLContext, ...],
    facts: tuple[FilingXBRLFact, ...],
    *,
    filing: SECFiling | None = None,
) -> SECFilingXBRL:
    return SECFilingXBRL(
        company=make_company(),
        filing=filing or make_filing(),
        contexts=contexts,
        units=(),
        facts=facts,
        source_url=SOURCE_URL,
        retrieved_at=RETRIEVED_AT,
    )


class AnnualPeriodResolutionTests(TestCase):
    def test_resolves_clean_annual_context_with_complete_provenance(self) -> None:
        context = make_context("annual")

        result = resolve_annual_period(
            make_xbrl((context,), make_dei_facts(context))
        )

        self.assertIsInstance(result, ResolvedAnnualPeriod)
        self.assertEqual(result.status, AnnualPeriodResolutionStatus.RESOLVED)
        self.assertEqual(result.start, date(2025, 1, 1))
        self.assertEqual(result.end, date(2025, 12, 31))
        self.assertEqual(result.filing.registrant_cik, 1)
        self.assertEqual(result.filing.accession_number, "0000000001-26-000001")
        self.assertEqual(result.filing.form, "10-K")
        self.assertEqual(result.filing.report_date, date(2025, 12, 31))
        self.assertEqual(result.filing.source_url, SOURCE_URL)
        self.assertEqual(result.filing.retrieved_at, RETRIEVED_AT)
        self.assertEqual(result.evidence.entity_identifier_scheme, SEC_CIK_SCHEME)
        self.assertEqual(result.evidence.entity_identifier_values, ("0000000001",))
        self.assertEqual(result.evidence.context_ids, ("annual",))
        self.assertEqual(
            tuple(item.concept for item in result.evidence.dei_evidence),
            (
                "DocumentFiscalPeriodFocus",
                "DocumentFiscalYearFocus",
                "DocumentPeriodEndDate",
            ),
        )

    def test_resolves_noncalendar_and_53_week_periods_without_length_rules(self) -> None:
        cases = (
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )
        for start, end in cases:
            with self.subTest(start=start, end=end):
                filing = make_filing(report_date=end)
                context = make_context("annual", start=start, end=end)
                facts = make_dei_facts(
                    context,
                    fiscal_year=str(end.year),
                    document_end=end.isoformat(),
                )

                result = resolve_annual_period(
                    make_xbrl((context,), facts, filing=filing)
                )

                self.assertIsInstance(result, ResolvedAnnualPeriod)
                self.assertEqual((result.start, result.end), (start, end))

    def test_resolves_standard_quarter_versioned_dei_namespace(self) -> None:
        context = make_context("annual")
        facts = tuple(
            replace(fact, namespace="http://xbrl.sec.gov/dei/2021q4")
            for fact in make_dei_facts(context)
        )

        result = resolve_annual_period(make_xbrl((context,), facts))

        self.assertIsInstance(result, ResolvedAnnualPeriod)

    def test_equivalent_context_ids_and_identical_facts_confirm(self) -> None:
        first = make_context("z-context")
        second = make_context("a-context")
        first_facts = make_dei_facts(first)
        facts = first_facts + (first_facts[0],) + make_dei_facts(second)

        result = resolve_annual_period(make_xbrl((first, second), facts))

        self.assertIsInstance(result, ResolvedAnnualPeriod)
        self.assertEqual(result.evidence.context_ids, ("a-context", "z-context"))
        period_focus = result.evidence.dei_evidence[0]
        self.assertEqual(len(period_focus.occurrences), 3)

    def test_resolution_is_independent_of_context_and_fact_order(self) -> None:
        first = make_context("z-context")
        second = make_context("a-context")
        facts = make_dei_facts(first) + make_dei_facts(second)
        forward = resolve_annual_period(make_xbrl((first, second), facts))
        reverse = resolve_annual_period(
            make_xbrl((second, first), tuple(reversed(facts)))
        )

        self.assertEqual(forward, reverse)

    def test_not_found_when_tuple_is_absent_incomplete_or_not_fy(self) -> None:
        context = make_context("annual")
        complete = make_dei_facts(context)
        cases = (
            (),
            complete[:-1],
            make_dei_facts(context, fiscal_period="Q3"),
        )
        for facts in cases:
            with self.subTest(facts=facts):
                result = resolve_annual_period(make_xbrl((context,), facts))
                self.assertIsInstance(result, AnnualPeriodNotFound)
                self.assertEqual(
                    result.status,
                    AnnualPeriodResolutionStatus.NOT_FOUND,
                )

    def test_different_valid_periods_are_ambiguous_and_deterministic(self) -> None:
        first = make_context("first", start=date(2025, 1, 1))
        second = make_context("second", start=date(2025, 2, 1))
        facts = make_dei_facts(first) + make_dei_facts(second)
        forward = resolve_annual_period(make_xbrl((first, second), facts))
        reverse = resolve_annual_period(
            make_xbrl((second, first), tuple(reversed(facts)))
        )

        self.assertIsInstance(forward, AmbiguousAnnualPeriod)
        self.assertEqual(forward.status, AnnualPeriodResolutionStatus.AMBIGUOUS)
        self.assertEqual(forward, reverse)
        self.assertEqual(
            tuple(candidate.start for candidate in forward.candidates),
            (date(2025, 1, 1), date(2025, 2, 1)),
        )

    def test_unsupported_forms_return_typed_result(self) -> None:
        context = make_context("annual")
        for form in ("10-K/A", "10-Q"):
            with self.subTest(form=form):
                result = resolve_annual_period(
                    make_xbrl(
                        (context,),
                        make_dei_facts(context),
                        filing=make_filing(form=form),
                    )
                )
                self.assertIsInstance(result, UnsupportedAnnualPeriod)
                self.assertEqual(
                    result.status,
                    AnnualPeriodResolutionStatus.UNSUPPORTED,
                )

    def test_wrong_scheme_and_cik_are_data_errors(self) -> None:
        contexts = (
            make_context("wrong-scheme", scheme="https://example.com/CIK"),
            make_context("wrong-cik", identifier="0000000002"),
        )
        for context in contexts:
            with self.subTest(context=context.context_id):
                result = resolve_annual_period(
                    make_xbrl((context,), make_dei_facts(context))
                )
                self.assertIsInstance(result, AnnualPeriodDataErrorResult)
                self.assertEqual(
                    result.status,
                    AnnualPeriodResolutionStatus.DATA_ERROR,
                )

    def test_contradictory_dei_values_are_data_errors(self) -> None:
        context = make_context("annual")
        cases = (
            make_dei_facts(context)
            + (make_fact(context, "DocumentFiscalPeriodFocus", "Q1"),),
            make_dei_facts(context)
            + (make_fact(context, "DocumentFiscalYearFocus", "2024"),),
            make_dei_facts(context)
            + (make_fact(context, "DocumentPeriodEndDate", "2025-12-30"),),
        )
        for facts in cases:
            with self.subTest(facts=facts):
                result = resolve_annual_period(make_xbrl((context,), facts))
                self.assertIsInstance(result, AnnualPeriodDataErrorResult)

    def test_invalid_duration_is_data_error(self) -> None:
        context = make_context(
            "annual",
            start=date(2025, 12, 31),
            end=date(2025, 12, 31),
        )

        result = resolve_annual_period(
            make_xbrl((context,), make_dei_facts(context))
        )

        self.assertIsInstance(result, AnnualPeriodDataErrorResult)

    def test_ineligible_contexts_and_report_mismatch_are_not_found(self) -> None:
        dimension = FilingXBRLDimension(
            dimension=FilingXBRLQName("http://fasb.org/us-gaap/2025", "Axis"),
            explicit_member=FilingXBRLQName(
                "http://example.com/2025",
                "Member",
            ),
            typed_member_xml=None,
        )
        dimensioned = make_context("dimensioned", dimensions=(dimension,))
        instant = replace(make_context("instant"), start=None)
        wrong_end = make_context("wrong-end", end=date(2025, 12, 30))

        dimensioned_result = resolve_annual_period(
            make_xbrl((dimensioned,), make_dei_facts(dimensioned))
        )
        instant_result = resolve_annual_period(
            make_xbrl((instant,), make_dei_facts(instant))
        )
        mismatched_result = resolve_annual_period(
            make_xbrl((wrong_end,), make_dei_facts(wrong_end))
        )

        self.assertIsInstance(dimensioned_result, AnnualPeriodNotFound)
        self.assertIsInstance(instant_result, AnnualPeriodNotFound)
        self.assertIsInstance(mismatched_result, AnnualPeriodNotFound)

    def test_missing_report_date_and_inconsistent_fact_linkage_are_data_errors(self) -> None:
        context = make_context("annual")
        missing_report = resolve_annual_period(
            make_xbrl(
                (context,),
                make_dei_facts(context),
                filing=make_filing(report_date=None),
            )
        )
        inconsistent_fact = replace(
            make_dei_facts(context)[0],
            accession_number="0000000001-26-999999",
        )
        inconsistent = resolve_annual_period(
            make_xbrl(
                (context,),
                (inconsistent_fact,) + make_dei_facts(context)[1:],
            )
        )

        self.assertIsInstance(missing_report, AnnualPeriodDataErrorResult)
        self.assertIsInstance(inconsistent, AnnualPeriodDataErrorResult)
