from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal

import unittest

from valuation_platform.normalization import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    DILUTED_WEIGHTED_AVERAGE_SHARES_POLICY,
    DerivationOperation,
    DerivedHistoricalValue,
    DilutedSharesDerivationError,
    EvidenceSourceKind,
    FinancialMetric,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedHistoricalValue,
    derive_googl_diluted_weighted_average_shares,
    normalize_annual_financials,
)
from valuation_platform.sec import (
    FilingFactObservations,
    FilingXBRLDimension,
    FilingXBRLFact,
    FilingXBRLQName,
    FilingXBRLUnit,
    ObservationRelationship,
    SECCompanyIdentity,
    SECFactObservation,
    SECFiling,
    SECFilingXBRL,
    SelectedFactObservation,
    SelectedFactObservations,
)


RETRIEVED_AT = datetime(2026, 2, 1, tzinfo=timezone.utc)
CONCEPT = "WeightedAverageNumberOfDilutedSharesOutstanding"
GOOGL_CIK = 1652044
GOOGL_2021_ACCESSION = "0001652044-22-000019"
US_GAAP = "http://fasb.org/us-gaap/2021-01-31"
XBRLI = "http://www.xbrl.org/2003/instance"


def company(cik: int = 1) -> SECCompanyIdentity:
    return SECCompanyIdentity(
        ticker="GOOGL" if cik == GOOGL_CIK else "TEST",
        cik=cik,
        cik_padded=f"{cik:010d}",
        company_name="Test",
        source_url="ticker-source",
        retrieved_at=RETRIEVED_AT,
    )


def filing(
    *,
    accession: str = "annual",
    form: str = "10-K",
    report_date: date | None = date(2025, 12, 31),
) -> SECFiling:
    return SECFiling(
        accession_number=accession,
        form=form,
        filing_date=date(2026, 1, 31),
        report_date=report_date,
        primary_document="annual.htm",
    )


def selected_fact(
    *,
    accession: str = "annual",
    value: object = 100,
    unit: str = "shares",
    start: date | None = date(2025, 1, 1),
    end: date = date(2025, 12, 31),
    relationship: ObservationRelationship = ObservationRelationship.CURRENT,
    form: str = "10-K",
    concept: str = CONCEPT,
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
            form=form,
            filed=date(2026, 1, 31),
            frame=None,
        ),
        relationship=relationship,
    )


def selected_input(
    *observations: SelectedFactObservation,
    cik: int = 1,
    selected_filing: SECFiling | None = None,
) -> SelectedFactObservations:
    selected_filing = selected_filing or filing()
    return SelectedFactObservations(
        company=company(cik),
        source_url="facts-source",
        retrieved_at=RETRIEVED_AT,
        annual=(FilingFactObservations(selected_filing, tuple(observations)),),
        interim=(),
    )


def normalize(
    selected: SelectedFactObservations,
    *artifacts: SECFilingXBRL,
):
    result = normalize_annual_financials(
        selected,
        policies=(DILUTED_WEIGHTED_AVERAGE_SHARES_POLICY,),
        filing_xbrl=tuple(artifacts),
    )
    return result.annual[0].metrics[0]


def dimension(
    share_class: str,
    report_date: date,
    namespace: str = US_GAAP,
) -> FilingXBRLDimension:
    if share_class == "A":
        member = FilingXBRLQName(namespace, "CommonClassAMember")
    elif share_class == "B":
        member = FilingXBRLQName(namespace, "CommonClassBMember")
    else:
        member = FilingXBRLQName(
            f"http://www.google.com/{report_date:%Y%m%d}",
            "CapitalClassCMember",
        )
    return FilingXBRLDimension(
        dimension=FilingXBRLQName(namespace, "StatementClassOfStockAxis"),
        explicit_member=member,
        typed_member_xml=None,
    )


def xbrl_fact(
    share_class: str,
    value: object,
    *,
    accession: str = GOOGL_2021_ACCESSION,
    report_date: date = date(2021, 12, 31),
    start: date | None = date(2021, 1, 1),
    namespace: str = US_GAAP,
    concept: str = CONCEPT,
    unit_name: str = "shares",
    extra_dimensions: tuple[FilingXBRLDimension, ...] = (),
    context_id: str | None = None,
) -> FilingXBRLFact:
    unit = FilingXBRLUnit(
        unit_id=unit_name,
        numerator_measures=(FilingXBRLQName(XBRLI, unit_name),),
        denominator_measures=(),
    )
    return FilingXBRLFact(
        namespace=namespace,
        concept=concept,
        context_id=context_id or f"context-{share_class}-{value}",
        start=start,
        end=report_date,
        dimensions=(dimension(share_class, report_date, namespace), *extra_dimensions),
        unit_ref=unit_name,
        unit=unit,
        raw_value=str(value),
        numeric_value=value,  # type: ignore[arg-type]
        decimals="-3",
        is_nil=False,
        accession_number=accession,
        source_url="xbrl-source",
    )


def artifact(
    *facts: FilingXBRLFact,
    selected_filing: SECFiling | None = None,
    cik: int = GOOGL_CIK,
) -> SECFilingXBRL:
    selected_filing = selected_filing or filing(
        accession=GOOGL_2021_ACCESSION,
        report_date=date(2021, 12, 31),
    )
    return SECFilingXBRL(
        company=company(cik),
        filing=selected_filing,
        contexts=(),
        units=(),
        facts=tuple(facts),
        source_url="xbrl-source",
        retrieved_at=RETRIEVED_AT,
    )


def googl_selected(*observations: SelectedFactObservation) -> SelectedFactObservations:
    selected_filing = filing(
        accession=GOOGL_2021_ACCESSION,
        report_date=date(2021, 12, 31),
    )
    return selected_input(
        *observations,
        cik=GOOGL_CIK,
        selected_filing=selected_filing,
    )


def valid_googl_artifact(*extra: FilingXBRLFact) -> SECFilingXBRL:
    return artifact(
        xbrl_fact("A", Decimal(345_755_000)),
        xbrl_fact("C", Decimal(331_919_000)),
        *extra,
    )



class DilutedSharesNormalizationTests(unittest.TestCase):
    def test_direct_shares_resolve_as_decimal_with_provenance(self) -> None:
        result = normalize(selected_input(selected_fact(value=123)))
        assert isinstance(result, NormalizedHistoricalValue)
        assert result.value == Decimal(123)
        assert isinstance(result.value, Decimal)
        assert result.unit == "shares"
        assert result.period.start == date(2025, 1, 1)
        assert result.chosen_source.concept == CONCEPT
        assert result.chosen_source.accession_number == "annual"
    
    
    def test_direct_rejects_noninteger_values(self) -> None:
        for value in (True, 1.5, "1"):
            assert isinstance(
                normalize(selected_input(selected_fact(value=value))),
                MissingHistoricalMetric,
            )
    
    
    def test_direct_rejects_wrong_units(self) -> None:
        for unit in ("USD", "USD/shares"):
            assert isinstance(
                normalize(selected_input(selected_fact(unit=unit))),
                MissingHistoricalMetric,
            )
    
    
    def test_direct_zero_is_valid(self) -> None:
        result = normalize(selected_input(selected_fact(value=0)))
        assert isinstance(result, NormalizedHistoricalValue)
        assert result.value == Decimal(0)
    
    
    def test_direct_preserves_noncalendar_52_and_53_week_periods(self) -> None:
        cases = (
            (date(2024, 7, 1), date(2025, 6, 30)),
            (date(2023, 9, 4), date(2024, 9, 1)),
            (date(2022, 8, 29), date(2023, 9, 3)),
        )
        for start, end in cases:
            result = normalize(
                selected_input(
                    selected_fact(start=start, end=end),
                    selected_filing=filing(report_date=end),
                )
            )
            assert isinstance(result, NormalizedHistoricalValue)
            assert result.period.start == start
            assert result.period.end == end
    
    
    def test_direct_rejects_structurally_ineligible_observations(self) -> None:
        cases = (
            (selected_fact(accession="later"), filing()),
            (selected_fact(form="10-Q"), filing()),
            (selected_fact(start=None), filing()),
            (selected_fact(end=date(2024, 12, 31)), filing()),
            (
                selected_fact(relationship=ObservationRelationship.COMPARATIVE),
                filing(),
            ),
        )
        for observation, selected_filing in cases:
            if observation.observation.accession_number != selected_filing.accession_number:
                with unittest.TestCase().assertRaisesRegex(
                    Exception, "does not match filing accession"
                ):
                    normalize(selected_input(observation, selected_filing=selected_filing))
            else:
                assert isinstance(
                    normalize(selected_input(observation, selected_filing=selected_filing)),
                    MissingHistoricalMetric,
                )
    
    
    def test_later_comparative_filing_cannot_backfill_selected_period(self) -> None:
        earlier_filing = filing(
            accession="earlier",
            report_date=date(2021, 12, 31),
        )
        later_filing = filing(
            accession="later",
            report_date=date(2022, 12, 31),
        )
        comparative = selected_fact(
            accession="later",
            value=999,
            start=date(2021, 1, 1),
            end=date(2021, 12, 31),
            relationship=ObservationRelationship.COMPARATIVE,
        )
        selected = SelectedFactObservations(
            company=company(),
            source_url="facts-source",
            retrieved_at=RETRIEVED_AT,
            annual=(
                FilingFactObservations(earlier_filing, ()),
                FilingFactObservations(later_filing, (comparative,)),
            ),
            interim=(),
        )
        output = normalize_annual_financials(
            selected,
            policies=(DILUTED_WEIGHTED_AVERAGE_SHARES_POLICY,),
        )
        assert isinstance(output.annual[0].metrics[0], MissingHistoricalMetric)
        assert isinstance(output.annual[1].metrics[0], MissingHistoricalMetric)
    
    
    def test_multiple_direct_candidates_are_deterministically_ambiguous(self) -> None:
        first = selected_fact(value=100)
        second = selected_fact(value=101)
        forward = normalize(selected_input(first, second))
        reverse = normalize(selected_input(second, first))
        assert isinstance(forward, AmbiguousHistoricalMetric)
        assert forward == reverse
        assert forward.reason is AmbiguityReason.CONFLICTING_CONCEPT_VALUES
        equal = normalize(selected_input(first, first))
        assert isinstance(equal, AmbiguousHistoricalMetric)


    def test_wrong_direct_concept_and_dimensional_filing_fact_do_not_resolve(self) -> None:
        wrong_concept = normalize(
            selected_input(selected_fact(concept="WeightedAverageNumberOfSharesOutstandingBasic"))
        )
        assert isinstance(wrong_concept, MissingHistoricalMetric)
        selected = selected_input()
        unrelated_artifact = artifact(
            xbrl_fact("A", Decimal(100)),
            selected_filing=selected.annual[0].filing,
            cik=1,
        )
        result = normalize(selected, unrelated_artifact)
        assert isinstance(result, MissingHistoricalMetric)
    
    
    def test_googl_derivation_adds_class_a_and_c_and_preserves_provenance(self) -> None:
        result = normalize(googl_selected(), valid_googl_artifact())
        assert isinstance(result, DerivedHistoricalValue)
        assert result.value == Decimal(677_674_000)
        assert result.operation is DerivationOperation.ADD
        assert result.period == result.period.__class__(date(2021, 1, 1), date(2021, 12, 31))
        assert [item.value for item in result.operands] == [
            Decimal(345_755_000),
            Decimal(331_919_000),
        ]
        for item in result.operands:
            assert item.source_kind is EvidenceSourceKind.FILING_XBRL
            assert item.accession_number == GOOGL_2021_ACCESSION
            assert item.source_url == "xbrl-source"
            assert item.context_id.startswith("context-")
            assert item.dimensions
            assert item.filing_report_date == date(2021, 12, 31)
            assert item.primary_document == "annual.htm"
    
    
    def test_class_b_is_never_added(self) -> None:
        class_b = xbrl_fact("B", Decimal(45_430_000))
        result = normalize(googl_selected(), valid_googl_artifact(class_b))
        assert isinstance(result, DerivedHistoricalValue)
        assert result.value == Decimal(677_674_000)
        assert all(
            item.dimensions[0].explicit_member.local_name != "CommonClassBMember"
            for item in result.operands
        )
    
    
    def test_zero_derived_operand_is_preserved(self) -> None:
        result = normalize(
            googl_selected(),
            artifact(
                xbrl_fact("A", Decimal(0)),
                xbrl_fact("C", Decimal(3)),
            ),
        )
        assert isinstance(result, DerivedHistoricalValue)
        assert result.value == Decimal(3)
    
    
    def test_derivation_is_cik_and_accession_scoped(self) -> None:
        wrong_cik = selected_input(
            selected_filing=filing(
                accession=GOOGL_2021_ACCESSION,
                report_date=date(2021, 12, 31),
            )
        )
        assert isinstance(normalize(wrong_cik), MissingHistoricalMetric)
        unsupported = googl_selected()
        unsupported_filing = replace(
            unsupported.annual[0].filing,
            accession_number="0001652044-25-000014",
        )
        unsupported = replace(
            unsupported,
            annual=(FilingFactObservations(unsupported_filing, ()),),
        )
        assert isinstance(normalize(unsupported), MissingHistoricalMetric)
    
    
    def test_invalid_class_a_operand_is_missing(self) -> None:
        bad_facts = (
            xbrl_fact("A", Decimal(1), accession="wrong"),
            xbrl_fact("A", Decimal(1), report_date=date(2020, 12, 31)),
            xbrl_fact("A", Decimal(1), start=None),
            xbrl_fact("A", Decimal(1), unit_name="USD"),
            xbrl_fact("A", Decimal(1), concept="WrongConcept"),
            xbrl_fact("A", Decimal("1.5")),
            xbrl_fact("A", 1),
            xbrl_fact("A", True),
            xbrl_fact("A", 1.0),
            xbrl_fact("A", "1"),
        )
        for bad_fact in bad_facts:
            result = normalize(
                googl_selected(),
                artifact(bad_fact, xbrl_fact("C", Decimal(2))),
            )
            assert isinstance(result, MissingHistoricalMetric)
    
    
    def test_wrong_axis_member_namespace_and_extra_dimension_are_rejected(self) -> None:
        correct = xbrl_fact("A", Decimal(1))
        wrong_axis = replace(
            correct,
            dimensions=(
                replace(correct.dimensions[0], dimension=FilingXBRLQName(US_GAAP, "OtherAxis")),
            ),
        )
        wrong_member = replace(
            correct,
            dimensions=(
                replace(
                    correct.dimensions[0],
                    explicit_member=FilingXBRLQName(US_GAAP, "OtherMember"),
                ),
            ),
        )
        extra = FilingXBRLDimension(
            FilingXBRLQName(US_GAAP, "OtherAxis"),
            FilingXBRLQName(US_GAAP, "OtherMember"),
            None,
        )
        for invalid in (wrong_axis, wrong_member, replace(correct, dimensions=(*correct.dimensions, extra))):
            assert isinstance(
                normalize(googl_selected(), artifact(invalid, xbrl_fact("C", Decimal(2)))),
                MissingHistoricalMetric,
            )
    
    
    def test_wrong_google_class_c_namespace_is_rejected(self) -> None:
        class_c = xbrl_fact("C", Decimal(2))
        member = class_c.dimensions[0].explicit_member
        assert member is not None
        wrong = replace(
            class_c,
            dimensions=(
                replace(
                    class_c.dimensions[0],
                    explicit_member=replace(member, namespace="http://www.google.com/20201231"),
                ),
            ),
        )
        assert isinstance(
            normalize(googl_selected(), artifact(xbrl_fact("A", Decimal(1)), wrong)),
            MissingHistoricalMetric,
        )
    
    
    def test_missing_and_ambiguous_operands_remain_typed(self) -> None:
        missing = normalize(
            googl_selected(),
            artifact(xbrl_fact("A", Decimal(1))),
        )
        assert isinstance(missing, MissingHistoricalMetric)
        duplicate_a = replace(xbrl_fact("A", Decimal(2)), context_id="other")
        ambiguous = normalize(
            googl_selected(),
            artifact(
                xbrl_fact("A", Decimal(1)),
                duplicate_a,
                xbrl_fact("C", Decimal(3)),
            ),
        )
        assert isinstance(ambiguous, AmbiguousHistoricalMetric)
        assert ambiguous.reason is AmbiguityReason.INCOMPATIBLE_DERIVATION_OPERANDS
    
    
    def test_derived_ambiguity_is_deterministic(self) -> None:
        facts = (
            xbrl_fact("A", Decimal(2), context_id="z"),
            xbrl_fact("A", Decimal(1), context_id="a"),
            xbrl_fact("C", Decimal(3)),
        )
        forward = normalize(googl_selected(), artifact(*facts))
        reverse = normalize(googl_selected(), artifact(*reversed(facts)))
        assert isinstance(forward, AmbiguousHistoricalMetric)
        assert forward == reverse
    
    
    def test_direct_result_and_ambiguity_take_precedence_over_derivation(self) -> None:
        direct = selected_fact(
            accession=GOOGL_2021_ACCESSION,
            value=10,
            start=date(2021, 1, 1),
            end=date(2021, 12, 31),
        )
        resolved = normalize(googl_selected(direct), valid_googl_artifact())
        assert isinstance(resolved, NormalizedHistoricalValue)
        assert resolved.value == Decimal(10)
        other = replace(
            direct,
            observation=replace(direct.observation, value=11),
        )
        ambiguous = normalize(googl_selected(direct, other), valid_googl_artifact())
        assert isinstance(ambiguous, AmbiguousHistoricalMetric)
    
    
    def test_public_derivation_rejects_10_q_filing(self) -> None:
        bad_filing = filing(
            accession=GOOGL_2021_ACCESSION,
            form="10-Q",
            report_date=date(2021, 12, 31),
        )
        with self.assertRaisesRegex(
            DilutedSharesDerivationError,
            "requires an exact 10-K with a report date",
        ):
            derive_googl_diluted_weighted_average_shares(
                FilingFactObservations(bad_filing, ()),
                self._missing_direct_result(),
                artifact(
                    xbrl_fact("A", Decimal(345_755_000)),
                    xbrl_fact("C", Decimal(331_919_000)),
                    selected_filing=bad_filing,
                ),
                GOOGL_CIK,
            )

    def test_public_derivation_rejects_missing_report_date(self) -> None:
        bad_filing = filing(
            accession=GOOGL_2021_ACCESSION,
            report_date=None,
        )
        with self.assertRaisesRegex(
            DilutedSharesDerivationError,
            "requires an exact 10-K with a report date",
        ):
            derive_googl_diluted_weighted_average_shares(
                FilingFactObservations(bad_filing, ()),
                self._missing_direct_result(),
                artifact(
                    xbrl_fact("A", Decimal(345_755_000)),
                    xbrl_fact("C", Decimal(331_919_000)),
                    selected_filing=bad_filing,
                ),
                GOOGL_CIK,
            )

    def test_public_derivation_accepts_valid_10_k_boundary(self) -> None:
        selected_filing = filing(
            accession=GOOGL_2021_ACCESSION,
            report_date=date(2021, 12, 31),
        )
        result = derive_googl_diluted_weighted_average_shares(
            FilingFactObservations(selected_filing, ()),
            self._missing_direct_result(),
            valid_googl_artifact(),
            GOOGL_CIK,
        )
        assert isinstance(result, DerivedHistoricalValue)
        assert result.value == Decimal(677_674_000)

    @staticmethod
    def _missing_direct_result() -> MissingHistoricalMetric:
        return MissingHistoricalMetric(
            metric=FinancialMetric.DILUTED_WEIGHTED_AVERAGE_SHARES,
            reason=MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
            examined_concepts=DILUTED_WEIGHTED_AVERAGE_SHARES_POLICY.candidates,
        )
    
    
    def test_original_selected_filing_split_basis_is_preserved(self) -> None:
        result = normalize(googl_selected(), valid_googl_artifact())
        assert isinstance(result, DerivedHistoricalValue)
        assert result.value == Decimal(677_674_000)
        assert result.value != Decimal(677_674_000) * 20
    
        filing_2022 = filing(
            accession="0001652044-23-000016",
            report_date=date(2022, 12, 31),
        )
        selected_2022 = selected_input(cik=GOOGL_CIK, selected_filing=filing_2022)
        namespace_2022 = "http://fasb.org/us-gaap/2022"
        artifact_2022 = artifact(
            xbrl_fact(
                "A",
                Decimal(6_881_000_000),
                accession=filing_2022.accession_number,
                report_date=date(2022, 12, 31),
                start=date(2022, 1, 1),
                namespace=namespace_2022,
            ),
            xbrl_fact(
                "C",
                Decimal(6_278_000_000),
                accession=filing_2022.accession_number,
                report_date=date(2022, 12, 31),
                start=date(2022, 1, 1),
                namespace=namespace_2022,
            ),
            selected_filing=filing_2022,
        )
        result_2022 = normalize(selected_2022, artifact_2022)
        assert isinstance(result_2022, DerivedHistoricalValue)
        assert result_2022.value == Decimal(13_159_000_000)
    
