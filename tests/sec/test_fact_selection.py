import gc
from datetime import date, datetime, timezone
from random import Random
from unittest import TestCase
import weakref

from valuation_platform.sec.company_facts import (
    SECCompanyFacts,
    SECFactConcept,
    SECFactObservation,
)
from valuation_platform.sec.fact_selection import (
    FactSelectionError,
    ObservationPeriodType,
    ObservationRelationship,
    select_fact_observations,
)
from valuation_platform.sec.filing_selection import SelectedFilings
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity


RETRIEVED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_filing(
    accession: str,
    report_date: date | None,
    *,
    form: str = "10-K",
) -> SECFiling:
    return SECFiling(
        accession_number=accession,
        form=form,
        filing_date=date(2026, 2, 1),
        report_date=report_date,
        primary_document=f"{accession}.htm",
    )


def make_observation(
    accession: str,
    end: date,
    *,
    start: date | None = None,
    unit: str = "USD",
    value: int = 1,
    form: str = "10-K",
    filed: date = date(2026, 2, 1),
) -> SECFactObservation:
    return SECFactObservation(
        unit=unit,
        value=value,
        start=start,
        end=end,
        accession_number=accession,
        fiscal_year=2025,
        fiscal_period="FY",
        form=form,
        filed=filed,
        frame=None,
    )


def make_concept(
    name: str,
    *observations: SECFactObservation,
    taxonomy: str = "us-gaap",
) -> SECFactConcept:
    return SECFactConcept(
        taxonomy=taxonomy,
        name=name,
        label=name,
        description=f"{name} description",
        observations=tuple(observations),
    )


def make_company_facts(*concepts: SECFactConcept) -> SECCompanyFacts:
    company = SECCompanyIdentity(
        ticker="TEST",
        cik=1,
        cik_padded="0000000001",
        company_name="Test Company",
        source_url="ticker-source",
        retrieved_at=RETRIEVED_AT,
    )
    return SECCompanyFacts(
        company=company,
        entity_name="Test Company",
        concepts=tuple(concepts),
        source_url="facts-source",
        retrieved_at=RETRIEVED_AT,
    )


def make_selected(
    *,
    annual: tuple[SECFiling, ...] = (),
    interim: tuple[SECFiling, ...] = (),
) -> SelectedFilings:
    return SelectedFilings(
        annual=annual,
        interim=interim,
        requested_annual_periods=max(1, len(annual)),
    )


class SelectFactObservationsTests(TestCase):
    def test_meta_style_annual_classifies_current_and_comparatives(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        facts = make_company_facts(
            make_concept(
                "Revenue",
                make_observation(
                    "annual", date(2023, 12, 31), start=date(2023, 1, 1)
                ),
                make_observation(
                    "annual", date(2024, 12, 31), start=date(2024, 1, 1)
                ),
                make_observation(
                    "annual", date(2025, 12, 31), start=date(2025, 1, 1)
                ),
            )
        )

        result = select_fact_observations(make_selected(annual=(filing,)), facts)

        observations = result.annual[0].observations
        self.assertEqual(
            [selected.relationship for selected in observations],
            [
                ObservationRelationship.COMPARATIVE,
                ObservationRelationship.COMPARATIVE,
                ObservationRelationship.CURRENT,
            ],
        )
        self.assertTrue(
            all(
                selected.period_type is ObservationPeriodType.DURATION
                for selected in observations
            )
        )

    def test_non_calendar_and_week_based_annual_durations_are_preserved(self) -> None:
        cases = [
            ("msft", date(2024, 7, 1), date(2025, 6, 30), 365),
            ("cost-52", date(2024, 9, 2), date(2025, 8, 31), 364),
            ("cost-53", date(2022, 8, 29), date(2023, 9, 3), 371),
        ]

        for accession, start, end, expected_days in cases:
            with self.subTest(accession=accession):
                filing = make_filing(accession, end)
                observation = make_observation(accession, end, start=start)

                result = select_fact_observations(
                    make_selected(annual=(filing,)),
                    make_company_facts(make_concept("Revenue", observation)),
                )

                selected = result.annual[0].observations[0]
                self.assertEqual(
                    (selected.observation.end - start).days + 1,
                    expected_days,
                )
                self.assertIs(selected.relationship, ObservationRelationship.CURRENT)

    def test_q1_duration_is_current_without_semantic_period_label(self) -> None:
        filing = make_filing("q1", date(2025, 3, 31), form="10-Q")
        observation = make_observation(
            "q1",
            date(2025, 3, 31),
            start=date(2025, 1, 1),
            form="10-Q",
        )

        result = select_fact_observations(
            make_selected(interim=(filing,)),
            make_company_facts(make_concept("Revenue", observation)),
        )

        selected = result.interim[0].observations[0]
        self.assertIs(selected.period_type, ObservationPeriodType.DURATION)
        self.assertIs(selected.relationship, ObservationRelationship.CURRENT)

    def test_q2_and_q3_same_end_different_starts_are_preserved(self) -> None:
        cases = [
            (
                "q2",
                date(2025, 6, 30),
                (date(2025, 1, 1), date(2025, 4, 1)),
            ),
            (
                "q3",
                date(2026, 5, 10),
                (date(2025, 9, 1), date(2026, 2, 16)),
            ),
        ]

        for accession, end, starts in cases:
            with self.subTest(accession=accession):
                filing = make_filing(accession, end, form="10-Q")
                facts = make_company_facts(
                    make_concept(
                        "Revenue",
                        *(
                            make_observation(
                                accession, end, start=start, form="10-Q"
                            )
                            for start in starts
                        ),
                    )
                )

                result = select_fact_observations(
                    make_selected(interim=(filing,)), facts
                )

                self.assertEqual(
                    [item.observation.start for item in result.interim[0].observations],
                    list(starts),
                )

    def test_q2_only_ytd_shaped_duration_is_preserved(self) -> None:
        filing = make_filing("q2", date(2025, 6, 30), form="10-Q")
        observation = make_observation(
            "q2", date(2025, 6, 30), start=date(2025, 1, 1), form="10-Q"
        )

        result = select_fact_observations(
            make_selected(interim=(filing,)),
            make_company_facts(make_concept("Capex", observation)),
        )

        self.assertEqual(
            result.interim[0].observations[0].observation.start,
            date(2025, 1, 1),
        )

    def test_instant_relationships_include_after_report_date(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        facts = make_company_facts(
            make_concept(
                "Cash",
                make_observation("annual", date(2024, 12, 31)),
                make_observation("annual", date(2025, 12, 31)),
                make_observation(
                    "annual",
                    date(2026, 1, 20),
                    unit="shares",
                    form="10-Q",
                    filed=date(2026, 1, 25),
                ),
            )
        )

        result = select_fact_observations(make_selected(annual=(filing,)), facts)

        observations = result.annual[0].observations
        self.assertEqual(
            [selected.relationship for selected in observations],
            [
                ObservationRelationship.COMPARATIVE,
                ObservationRelationship.CURRENT,
                ObservationRelationship.AFTER_REPORT_DATE,
            ],
        )
        self.assertTrue(
            all(
                selected.period_type is ObservationPeriodType.INSTANT
                for selected in observations
            )
        )
        self.assertEqual(observations[-1].observation.form, "10-Q")

    def test_comparative_duration_without_current_is_preserved(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        comparative = make_observation(
            "annual", date(2024, 12, 31), start=date(2024, 1, 1)
        )

        result = select_fact_observations(
            make_selected(annual=(filing,)),
            make_company_facts(make_concept("Revenue", comparative)),
        )

        self.assertEqual(len(result.annual[0].observations), 1)
        self.assertIs(
            result.annual[0].observations[0].relationship,
            ObservationRelationship.COMPARATIVE,
        )

    def test_exact_concept_lookup_and_missing_concept(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        facts = make_company_facts(
            make_concept("Revenue", make_observation("annual", date(2025, 12, 31)))
        )

        bucket = select_fact_observations(
            make_selected(annual=(filing,)), facts
        ).annual[0]

        self.assertEqual(len(bucket.for_concept("us-gaap", "Revenue")), 1)
        self.assertEqual(bucket.for_concept("US-GAAP", "Revenue"), ())
        self.assertEqual(bucket.for_concept("us-gaap", "Revenues"), ())

    def test_global_concept_without_selected_accession_is_absent(self) -> None:
        filing = make_filing("selected", date(2025, 12, 31))
        facts = make_company_facts(
            make_concept(
                "Revenue",
                make_observation("other", date(2025, 12, 31)),
            )
        )

        bucket = select_fact_observations(
            make_selected(annual=(filing,)), facts
        ).annual[0]

        self.assertEqual(bucket.observations, ())
        self.assertEqual(bucket.for_concept("us-gaap", "Revenue"), ())

    def test_selected_filing_without_observations_still_appears(self) -> None:
        filing = make_filing("selected", date(2025, 12, 31))

        result = select_fact_observations(
            make_selected(annual=(filing,)), make_company_facts()
        )

        self.assertEqual(result.annual[0].filing, filing)
        self.assertEqual(result.annual[0].observations, ())

    def test_exact_duplicate_raises_for_same_or_conflicting_values(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        first = make_observation(
            "annual", date(2025, 12, 31), start=date(2025, 1, 1), value=1
        )

        for second_value in (1, 2):
            with self.subTest(second_value=second_value):
                facts = make_company_facts(
                    make_concept(
                        "Revenue",
                        first,
                        make_observation(
                            "annual",
                            date(2025, 12, 31),
                            start=date(2025, 1, 1),
                            value=second_value,
                        ),
                    )
                )

                with self.assertRaises(FactSelectionError) as raised:
                    select_fact_observations(make_selected(annual=(filing,)), facts)

                message = str(raised.exception)
                for expected in (
                    "annual",
                    "2 observations",
                    "us-gaap",
                    "Revenue",
                    "USD",
                    "2025, 1, 1",
                    "2025, 12, 31",
                ):
                    self.assertIn(expected, message)

    def test_multiple_units_are_preserved(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        facts = make_company_facts(
            make_concept(
                "Metric",
                make_observation("annual", date(2025, 12, 31), unit="USD"),
                make_observation("annual", date(2025, 12, 31), unit="shares"),
            )
        )

        result = select_fact_observations(make_selected(annual=(filing,)), facts)

        self.assertEqual(
            [item.observation.unit for item in result.annual[0].observations],
            ["USD", "shares"],
        )

    def test_duplicate_selected_accession_raises(self) -> None:
        annual = make_filing("duplicate", date(2025, 12, 31))
        interim = make_filing("duplicate", date(2026, 3, 31), form="10-Q")

        with self.assertRaisesRegex(FactSelectionError, "duplicate accession"):
            select_fact_observations(
                make_selected(annual=(annual,), interim=(interim,)),
                make_company_facts(),
            )

    def test_missing_selected_report_date_raises(self) -> None:
        filing = make_filing("annual", None)

        with self.assertRaisesRegex(FactSelectionError, "no report date"):
            select_fact_observations(
                make_selected(annual=(filing,)), make_company_facts()
            )

    def test_ordering_is_independent_of_company_facts_input_order(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        concepts = [
            make_concept(
                "Zulu",
                make_observation("annual", date(2025, 12, 31), unit="shares"),
                make_observation("annual", date(2024, 12, 31), unit="USD"),
            ),
            make_concept(
                "Alpha",
                make_observation(
                    "annual", date(2025, 12, 31), start=date(2025, 4, 1)
                ),
                make_observation("annual", date(2025, 12, 31)),
                make_observation(
                    "annual", date(2025, 12, 31), start=date(2025, 1, 1)
                ),
            ),
        ]
        shuffled = list(concepts)
        Random(42).shuffle(shuffled)
        reversed_observations = tuple(
            make_concept(
                concept.name,
                *reversed(concept.observations),
                taxonomy=concept.taxonomy,
            )
            for concept in shuffled
        )

        first = select_fact_observations(
            make_selected(annual=(filing,)), make_company_facts(*concepts)
        )
        second = select_fact_observations(
            make_selected(annual=(filing,)),
            make_company_facts(*reversed_observations),
        )

        first_keys = [
            (
                item.taxonomy,
                item.concept,
                item.observation.unit,
                item.observation.end,
                item.observation.start,
            )
            for item in first.annual[0].observations
        ]
        second_keys = [
            (
                item.taxonomy,
                item.concept,
                item.observation.unit,
                item.observation.end,
                item.observation.start,
            )
            for item in second.annual[0].observations
        ]
        self.assertEqual(first_keys, second_keys)
        self.assertIsNone(first_keys[0][-1])

    def test_annual_and_interim_grouping_preserves_filing_order(self) -> None:
        annual = (
            make_filing("annual-1", date(2024, 12, 31)),
            make_filing("annual-2", date(2025, 12, 31)),
        )
        interim = (
            make_filing("q1", date(2026, 3, 31), form="10-Q"),
            make_filing("q2", date(2026, 6, 30), form="10-Q"),
        )

        result = select_fact_observations(
            make_selected(annual=annual, interim=interim), make_company_facts()
        )

        self.assertEqual(tuple(bucket.filing for bucket in result.annual), annual)
        self.assertEqual(tuple(bucket.filing for bucket in result.interim), interim)

    def test_no_selected_filings_returns_compact_empty_result(self) -> None:
        facts = make_company_facts(make_concept("Unused"))

        result = select_fact_observations(make_selected(), facts)

        self.assertIs(result.company, facts.company)
        self.assertEqual(result.source_url, "facts-source")
        self.assertEqual(result.retrieved_at, RETRIEVED_AT)
        self.assertEqual(result.annual, ())
        self.assertEqual(result.interim, ())

    def test_output_does_not_retain_company_facts_or_concept_objects(self) -> None:
        filing = make_filing("annual", date(2025, 12, 31))
        observation = make_observation("annual", date(2025, 12, 31))
        concept = make_concept("Cash", observation)
        facts = make_company_facts(concept)
        facts_reference = weakref.ref(facts)
        concept_reference = weakref.ref(concept)

        result = select_fact_observations(make_selected(annual=(filing,)), facts)
        del facts
        del concept
        gc.collect()

        self.assertIsNone(facts_reference())
        self.assertIsNone(concept_reference())
        self.assertIs(result.annual[0].observations[0].observation, observation)
