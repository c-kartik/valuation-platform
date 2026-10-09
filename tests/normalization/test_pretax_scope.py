from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
import unittest

from valuation_platform.normalization import (
    AmbiguousHistoricalMetric,
    DerivedHistoricalValue,
    FinancialMetric,
    INCOME_TAX_EXPENSE_POLICY,
    MissingHistoricalMetric,
    NormalizationError,
    NormalizedHistoricalValue,
    PRETAX_INCOME_POLICY,
    PRETAX_SCOPE_CANDIDATE,
    PRETAX_SCOPE_EQUIVALENCE_POLICY,
    PretaxEconomicScope,
    PretaxScopePolicyError,
    normalize_annual_financials,
    pretax_scope_entry_for,
)
from valuation_platform.sec import (
    AnnualPeriodDEIEvidence,
    AnnualPeriodEvidenceTuple,
    AnnualPeriodFilingEvidence,
    FilingFactObservations,
    FilingXBRLContext,
    FilingXBRLDimension,
    FilingXBRLFact,
    FilingXBRLQName,
    FilingXBRLUnit,
    ObservationRelationship,
    ResolvedAnnualPeriod,
    SECCompanyIdentity,
    SECFactObservation,
    SECFiling,
    SECFilingXBRL,
    SelectedFactObservation,
    SelectedFactObservations,
)


NOW = datetime(2026, 10, 9, tzinfo=timezone.utc)
CURRENT_PRETAX = PRETAX_INCOME_POLICY.candidates[0].name
TAX = INCOME_TAX_EXPENSE_POLICY.candidates[0].name
US_GAAP = "http://fasb.org/us-gaap/2025"
XBRLI = "http://www.xbrl.org/2003/instance"
ISO4217 = "http://www.xbrl.org/2003/iso4217"

CASES = (
    (1018724, "0001018724-22-000005", date(2021, 1, 1), date(2021, 12, 31), False),
    (1018724, "0001018724-23-000004", date(2022, 1, 1), date(2022, 12, 31), False),
    (1018724, "0001018724-24-000008", date(2023, 1, 1), date(2023, 12, 31), False),
    (1018724, "0001018724-25-000004", date(2024, 1, 1), date(2024, 12, 31), False),
    (1018724, "0001018724-26-000004", date(2025, 1, 1), date(2025, 12, 31), False),
    (723125, "0000723125-21-000065", date(2020, 9, 4), date(2021, 9, 2), False),
    (723125, "0000723125-22-000048", date(2021, 9, 3), date(2022, 9, 1), False),
    (723125, "0000723125-23-000054", date(2022, 9, 2), date(2023, 8, 31), False),
    (723125, "0000723125-24-000027", date(2023, 9, 1), date(2024, 8, 29), False),
    (723125, "0000723125-25-000028", date(2024, 8, 30), date(2025, 8, 28), False),
    (1141391, "0001141391-22-000023", date(2021, 1, 1), date(2021, 12, 31), True),
    (1141391, "0001141391-23-000020", date(2022, 1, 1), date(2022, 12, 31), True),
    (1141391, "0001141391-24-000022", date(2023, 1, 1), date(2023, 12, 31), True),
    (93410, "0000093410-22-000019", date(2021, 1, 1), date(2021, 12, 31), True),
    (93410, "0000093410-23-000009", date(2022, 1, 1), date(2022, 12, 31), True),
    (93410, "0000093410-24-000013", date(2023, 1, 1), date(2023, 12, 31), True),
    (93410, "0000093410-25-000009", date(2024, 1, 1), date(2024, 12, 31), True),
    (93410, "0000093410-26-000078", date(2025, 1, 1), date(2025, 12, 31), True),
    (18230, "0000018230-22-000050", date(2021, 1, 1), date(2021, 12, 31), False),
    (18230, "0000018230-23-000011", date(2022, 1, 1), date(2022, 12, 31), False),
    (18230, "0000018230-24-000009", date(2023, 1, 1), date(2023, 12, 31), False),
    (18230, "0000018230-25-000008", date(2024, 1, 1), date(2024, 12, 31), False),
    (18230, "0000018230-26-000008", date(2025, 1, 1), date(2025, 12, 31), False),
    (1413329, "0001413329-22-000011", date(2021, 1, 1), date(2021, 12, 31), False),
    (1413329, "0001413329-23-000025", date(2022, 1, 1), date(2022, 12, 31), False),
    (1413329, "0001413329-24-000013", date(2023, 1, 1), date(2023, 12, 31), False),
    (1413329, "0001413329-25-000013", date(2024, 1, 1), date(2024, 12, 31), False),
    (1413329, "0001628280-26-005939", date(2025, 1, 1), date(2025, 12, 31), False),
    (1707925, "0001628280-22-004180", date(2021, 1, 1), date(2021, 12, 31), False),
    (1707925, "0001628280-23-005434", date(2022, 1, 1), date(2022, 12, 31), False),
    (1707925, "0001628280-24-007424", date(2023, 1, 1), date(2023, 12, 31), False),
    (1707925, "0001628280-25-007990", date(2024, 1, 1), date(2024, 12, 31), False),
    (1707925, "0001628280-26-011430", date(2025, 1, 1), date(2025, 12, 31), False),
)

VALUES_BY_ACCESSION = {
    "0001018724-22-000005": 38_151_000_000,
    "0001018724-23-000004": -5_936_000_000,
    "0001018724-24-000008": 37_557_000_000,
    "0001018724-25-000004": 68_614_000_000,
    "0001018724-26-000004": 97_311_000_000,
    "0000723125-21-000065": 6_218_000_000,
    "0000723125-22-000048": 9_571_000_000,
    "0000723125-23-000054": -5_658_000_000,
    "0000723125-24-000027": 1_240_000_000,
    "0000723125-25-000028": 9_654_000_000,
    "0001141391-22-000023": 10_307_000_000,
    "0001141391-23-000020": 11_732_000_000,
    "0001141391-24-000022": 13_639_000_000,
    "0000093410-22-000019": 21_639_000_000,
    "0000093410-23-000009": 49_674_000_000,
    "0000093410-24-000013": 29_584_000_000,
    "0000093410-25-000009": 27_506_000_000,
    "0000093410-26-000078": 19_743_000_000,
    "0000018230-22-000050": 8_204_000_000,
    "0000018230-23-000011": 8_752_000_000,
    "0000018230-24-000009": 13_050_000_000,
    "0000018230-25-000008": 13_373_000_000,
    "0000018230-26-000008": 11_541_000_000,
    "0001413329-22-000011": 12_232_000_000,
    "0001413329-23-000025": 11_634_000_000,
    "0001413329-24-000013": 10_450_000_000,
    "0001413329-25-000013": 12_199_000_000,
    "0001628280-26-005939": 13_880_000_000,
    "0001628280-22-004180": 5_099_000_000,
    "0001628280-23-005434": 5_543_000_000,
    "0001628280-24-007424": 7_988_000_000,
    "0001628280-25-007990": 8_569_000_000,
    "0001628280-26-011430": 8_897_000_000,
}


def company(cik: int) -> SECCompanyIdentity:
    return SECCompanyIdentity("TEST", cik, f"{cik:010d}", "Test", "ticker-source", NOW)


def filing(entry, *, accession: str | None = None, form: str = "10-K") -> SECFiling:
    return SECFiling(
        accession or entry.accession_number,
        form,
        date(entry.report_date.year + 1, 2, 1),
        entry.report_date,
        f"test-{entry.report_date:%Y%m%d}.htm",
    )


def selected(entry, concept: str, value: object, *, unit: str = "USD", form: str = "10-K"):
    return SelectedFactObservation(
        "us-gaap",
        concept,
        SECFactObservation(
            unit,
            value,  # type: ignore[arg-type]
            entry.annual_start,
            entry.annual_end,
            entry.accession_number,
            entry.report_date.year,
            "FY",
            form,
            date(entry.report_date.year + 1, 2, 1),
            None,
        ),
        ObservationRelationship.CURRENT,
    )


def annual_period(entry, selected_filing: SECFiling) -> ResolvedAnnualPeriod:
    filing_evidence = AnnualPeriodFilingEvidence(
        entry.company_cik,
        selected_filing.accession_number,
        selected_filing.form,
        selected_filing.report_date,
        selected_filing.filing_date,
        selected_filing.primary_document,
        "xbrl-source",
        NOW,
    )
    evidence = AnnualPeriodEvidenceTuple(
        "http://www.sec.gov/CIK",
        (f"{entry.company_cik:010d}",),
        entry.company_cik,
        entry.annual_start,
        entry.annual_end,
        (),
        ("annual",),
        (
            AnnualPeriodDEIEvidence("DocumentFiscalPeriodFocus", "FY", ()),
            AnnualPeriodDEIEvidence("DocumentFiscalYearFocus", str(entry.report_date.year), ()),
            AnnualPeriodDEIEvidence("DocumentPeriodEndDate", entry.report_date.isoformat(), ()),
        ),
    )
    return ResolvedAnnualPeriod(filing_evidence, evidence)


def xbrl_fact(
    entry,
    value: int | Decimal | None,
    *,
    context_id: str = "annual",
    dimensions: tuple[FilingXBRLDimension, ...] = (),
    unit_id: str = "usd",
    unit_namespace: str = ISO4217,
    unit_name: str = "USD",
    raw_value: str | None = None,
    decimals: str | None = "-6",
    is_nil: bool = False,
    namespace: str = US_GAAP,
    concept: str | None = None,
    start: date | None = None,
    end: date | None = None,
    accession: str | None = None,
    source_url: str = "xbrl-source",
) -> FilingXBRLFact:
    unit = FilingXBRLUnit(
        unit_id,
        (FilingXBRLQName(unit_namespace, unit_name),),
        (),
    )
    numeric = None if value is None else Decimal(value)
    return FilingXBRLFact(
        namespace,
        concept or entry.concept,
        context_id,
        start or entry.annual_start,
        end or entry.annual_end,
        dimensions,
        unit_id,
        unit,
        str(value) if raw_value is None and value is not None else raw_value,
        numeric,
        decimals,
        is_nil,
        accession or entry.accession_number,
        source_url,
    )


def artifact(
    entry,
    selected_filing: SECFiling,
    *facts: FilingXBRLFact,
    contexts: tuple[FilingXBRLContext, ...] | None = None,
) -> SECFilingXBRL:
    if contexts is None:
        by_id = {}
        for fact in facts:
            by_id.setdefault(
                fact.context_id,
                FilingXBRLContext(
                    fact.context_id,
                    "http://www.sec.gov/CIK",
                    f"{entry.company_cik:010d}",
                    fact.start,
                    fact.end,
                    fact.dimensions,
                ),
            )
        contexts = tuple(by_id.values())
    units = tuple(
        {fact.unit_ref: fact.unit for fact in facts if fact.unit is not None}.values()
    )
    return SECFilingXBRL(
        company(entry.company_cik),
        selected_filing,
        contexts,
        units,
        tuple(facts),
        "xbrl-source",
        NOW,
    )


def normalize(entry, *observations, facts=None, selected_filing=None, contexts=None):
    selected_filing = selected_filing or filing(entry)
    input_value = SelectedFactObservations(
        company(entry.company_cik),
        "facts-source",
        NOW,
        (FilingFactObservations(selected_filing, tuple(observations)),),
        (),
    )
    xbrl = artifact(
        entry,
        selected_filing,
        *(facts if facts is not None else (xbrl_fact(entry, entry.expected_value),)),
        contexts=contexts,
    )
    result = normalize_annual_financials(
        input_value,
        policies=(PRETAX_INCOME_POLICY, INCOME_TAX_EXPENSE_POLICY),
        filing_xbrl=(xbrl,),
        annual_periods=(annual_period(entry, selected_filing),),
    )
    return {item.metric: item for item in result.annual[0].metrics}


class PretaxScopePolicyTests(unittest.TestCase):
    def test_exact_33_case_boundary_matches_eight_positive_entries(self) -> None:
        self.assertEqual(len(CASES), 33)
        self.assertEqual(len({item[1] for item in CASES}), 33)
        self.assertEqual(set(VALUES_BY_ACCESSION), {item[1] for item in CASES})
        self.assertEqual(sum(item[4] for item in CASES), 8)
        resolved = 0
        missing = 0
        for cik, accession, start, end, allowed in CASES:
            entry = pretax_scope_entry_for(
                cik,
                accession,
                end,
                start,
                end,
                PRETAX_SCOPE_CANDIDATE.taxonomy,
                PRETAX_SCOPE_CANDIDATE.name,
                "USD",
                PretaxEconomicScope.INCLUDED_PRETAX,
            )
            with self.subTest(accession=accession):
                self.assertIs(entry is not None, allowed)
                case = entry or SimpleNamespace(
                    company_cik=cik,
                    accession_number=accession,
                    report_date=end,
                    annual_start=start,
                    annual_end=end,
                    taxonomy=PRETAX_SCOPE_CANDIDATE.taxonomy,
                    concept=PRETAX_SCOPE_CANDIDATE.name,
                    expected_value=VALUES_BY_ACCESSION[accession],
                )
                result = normalize(
                    case,
                    selected(case, case.concept, case.expected_value),
                )[FinancialMetric.PRETAX_INCOME]
                if allowed:
                    self.assertIsInstance(result, NormalizedHistoricalValue)
                    resolved += 1
                else:
                    self.assertIsInstance(result, MissingHistoricalMetric)
                    missing += 1
        self.assertEqual((resolved, missing), (8, 25))

    def test_registry_is_exactly_the_reviewed_boundary(self) -> None:
        self.assertEqual(len(PRETAX_SCOPE_EQUIVALENCE_POLICY.entries), 8)
        self.assertEqual(
            {entry.company_cik for entry in PRETAX_SCOPE_EQUIVALENCE_POLICY.entries},
            {93410, 1141391},
        )
        self.assertNotIn(PRETAX_SCOPE_CANDIDATE, PRETAX_INCOME_POLICY.candidates)

    def test_policy_entry_evidence_and_normalized_provenance_are_immutable(self) -> None:
        policy = PRETAX_SCOPE_EQUIVALENCE_POLICY
        entry = policy.entries[0]
        result = normalize(
            entry,
            selected(entry, entry.concept, entry.expected_value),
        )[FinancialMetric.PRETAX_INCOME]
        assert isinstance(result, NormalizedHistoricalValue)
        objects_and_fields = (
            (policy, "version", "2"),
            (entry, "unit", "EUR"),
            (entry.reviewed_evidence[0], "review_status", "rejected"),
            (result.policy_provenance, "policy_version", "2"),
        )
        for value, field, replacement in objects_and_fields:
            with self.subTest(type=type(value).__name__, field=field):
                with self.assertRaises(FrozenInstanceError):
                    setattr(value, field, replacement)

    def test_complete_key_rejects_each_incorrect_field(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        exact = (
            entry.company_cik,
            entry.accession_number,
            entry.report_date,
            entry.annual_start,
            entry.annual_end,
            entry.taxonomy,
            entry.concept,
            entry.unit,
            entry.economic_scope,
        )
        replacements = (
            1,
            "0001141391-22-999999",
            date(2021, 12, 30),
            date(2021, 1, 2),
            date(2021, 12, 30),
            "dei",
            "WrongConcept",
            "EUR",
            "SEPARATE_NET_OF_TAX",
        )
        for index, replacement in enumerate(replacements):
            key = list(exact)
            key[index] = replacement
            with self.subTest(field=index):
                self.assertIsNone(pretax_scope_entry_for(*key))

    def test_all_eight_entries_resolve_and_retain_etr_operand_provenance(self) -> None:
        for entry in PRETAX_SCOPE_EQUIVALENCE_POLICY.entries:
            with self.subTest(accession=entry.accession_number):
                results = normalize(
                    entry,
                    selected(entry, entry.concept, entry.expected_value),
                    selected(entry, TAX, 1_000_000_000),
                )
                pretax = results[FinancialMetric.PRETAX_INCOME]
                etr = results[FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE]
                self.assertIsInstance(pretax, NormalizedHistoricalValue)
                self.assertIsInstance(etr, DerivedHistoricalValue)
                assert isinstance(pretax, NormalizedHistoricalValue)
                assert isinstance(etr, DerivedHistoricalValue)
                self.assertEqual(pretax.value, entry.expected_value)
                self.assertEqual(pretax.policy_provenance.policy_id, "pretax_scope_equivalence")
                self.assertEqual(pretax.policy_provenance.policy_version, "1")
                self.assertEqual(pretax.policy_provenance.accession_number, entry.accession_number)
                self.assertEqual(len(pretax.policy_provenance.reviewed_evidence), 1)
                self.assertEqual(len(pretax.policy_provenance.filing_xbrl_evidence), 1)
                denominator = etr.metric_operands[1]
                self.assertEqual(denominator.policy_provenance, pretax.policy_provenance)

    def test_unregistered_is_missing_and_amended_form_is_rejected(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        selected_filing = replace(
            filing(entry), accession_number="0001141391-26-999999"
        )
        observation = replace(
            selected(entry, entry.concept, entry.expected_value),
            observation=replace(
                selected(entry, entry.concept, entry.expected_value).observation,
                accession_number=selected_filing.accession_number,
            ),
        )
        input_value = SelectedFactObservations(
            company(entry.company_cik),
            "facts-source",
            NOW,
            (FilingFactObservations(selected_filing, (observation,)),),
            (),
        )
        result = normalize_annual_financials(
            input_value,
            policies=(PRETAX_INCOME_POLICY,),
        ).annual[0].metrics[0]
        self.assertIsInstance(result, MissingHistoricalMetric)

        amended = replace(
            filing(entry),
            accession_number="0001141391-22-000024",
            form="10-K/A",
        )
        amended_observation = replace(
            observation,
            observation=replace(
                observation.observation,
                accession_number=amended.accession_number,
                form=amended.form,
            ),
        )
        amended_input = SelectedFactObservations(
            company(entry.company_cik),
            "facts-source",
            NOW,
            (FilingFactObservations(amended, (amended_observation,)),),
            (),
        )
        with self.assertRaises(NormalizationError):
            normalize_annual_financials(
                amended_input,
                policies=(PRETAX_INCOME_POLICY,),
            )

    def test_malformed_or_unverified_candidate_does_not_override_missing(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        dimension = FilingXBRLDimension(
            FilingXBRLQName(US_GAAP, "SomeAxis"),
            FilingXBRLQName(US_GAAP, "SomeMember"),
            None,
        )
        cases = (
            (selected(entry, entry.concept, entry.expected_value, unit="EUR"), None),
            (selected(entry, entry.concept, "bad"), None),
            (selected(entry, entry.concept, entry.expected_value + 1), None),
            (
                selected(entry, entry.concept, entry.expected_value),
                (xbrl_fact(entry, entry.expected_value, dimensions=(dimension,)),),
            ),
        )
        for observation, facts in cases:
            with self.subTest(value=observation.observation.value, facts=facts):
                result = normalize(entry, observation, facts=facts or ())[FinancialMetric.PRETAX_INCOME]
                self.assertIsInstance(result, MissingHistoricalMetric)

    def test_ma_style_same_context_occurrences_confirm_in_source_order(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        facts = tuple(xbrl_fact(entry, entry.expected_value) for _ in range(3))
        result = normalize(
            entry,
            selected(entry, entry.concept, entry.expected_value),
            facts=facts,
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        evidence = result.policy_provenance.filing_xbrl_evidence
        self.assertEqual(len(evidence), 3)
        self.assertEqual(
            tuple(item.occurrence_ordinal for item in evidence),
            (1, 2, 3),
        )
        self.assertEqual({item.context_id for item in evidence}, {"annual"})

    def test_cvx_style_dimensioned_facts_do_not_conflict(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[3]
        affiliate_dimension = FilingXBRLDimension(
            FilingXBRLQName(US_GAAP, "EquityMethodInvestmentAxis"),
            FilingXBRLQName(US_GAAP, "AffiliatesMember"),
            None,
        )
        parent_dimension = FilingXBRLDimension(
            FilingXBRLQName(US_GAAP, "ConsolidatedEntitiesAxis"),
            FilingXBRLQName(US_GAAP, "ParentCompanyMember"),
            None,
        )
        result = normalize(
            entry,
            selected(entry, entry.concept, entry.expected_value),
            facts=(
                xbrl_fact(entry, entry.expected_value),
                xbrl_fact(
                    entry,
                    15_175_000_000,
                    context_id="affiliate",
                    dimensions=(affiliate_dimension,),
                ),
                xbrl_fact(
                    entry,
                    6_984_000_000,
                    context_id="parent",
                    dimensions=(parent_dimension,),
                ),
                xbrl_fact(entry, entry.expected_value),
            ),
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        evidence = result.policy_provenance.filing_xbrl_evidence
        self.assertEqual(len(evidence), 2)
        self.assertTrue(all(not item.dimensions for item in evidence))

    def test_equivalent_context_and_unit_ids_confirm(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        result = normalize(
            entry,
            selected(entry, entry.concept, entry.expected_value),
            facts=(
                xbrl_fact(
                    entry,
                    entry.expected_value,
                    context_id="context-b",
                    unit_id="usd-b",
                ),
                xbrl_fact(
                    entry,
                    entry.expected_value,
                    context_id="context-a",
                    unit_id="usd-a",
                ),
            ),
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        evidence = result.policy_provenance.filing_xbrl_evidence
        self.assertEqual(
            tuple((item.context_id, item.unit_ref) for item in evidence),
            (("context-a", "usd-a"), ("context-b", "usd-b")),
        )

    def test_lexical_and_decimals_differences_confirm_exact_decimal(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        result = normalize(
            entry,
            selected(entry, entry.concept, entry.expected_value),
            facts=(
                xbrl_fact(
                    entry,
                    entry.expected_value,
                    raw_value=f"{entry.expected_value}.0",
                    decimals="-3",
                ),
                xbrl_fact(
                    entry,
                    entry.expected_value,
                    raw_value=str(entry.expected_value),
                    decimals="-6",
                ),
            ),
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        evidence = result.policy_provenance.filing_xbrl_evidence
        self.assertEqual(
            {(item.raw_value, item.decimals) for item in evidence},
            {
                (f"{entry.expected_value}.0", "-3"),
                (str(entry.expected_value), "-6"),
            },
        )

    def test_structural_candidate_errors_are_not_collapsed(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        observation = selected(entry, entry.concept, entry.expected_value)
        valid = xbrl_fact(entry, entry.expected_value)
        wrong_entity_context = FilingXBRLContext(
            "annual",
            "http://www.sec.gov/CIK",
            "0000000001",
            entry.annual_start,
            entry.annual_end,
            (),
        )
        broken_context = FilingXBRLContext(
            "annual",
            "http://www.sec.gov/CIK",
            f"{entry.company_cik:010d}",
            date(2021, 1, 2),
            entry.annual_end,
            (),
        )
        cases = (
            ("missing-context", (valid,), ()),
            ("wrong-entity", (valid,), (wrong_entity_context,)),
            ("broken-link", (valid,), (broken_context,)),
            (
                "wrong-accession",
                (
                    xbrl_fact(
                        entry,
                        entry.expected_value,
                        accession="0001141391-22-999999",
                    ),
                ),
                None,
            ),
            (
                "wrong-source",
                (
                    xbrl_fact(
                        entry,
                        entry.expected_value,
                        source_url="other-source",
                    ),
                ),
                None,
            ),
            (
                "broken-unit-link",
                (replace(valid, unit_ref="other-unit"),),
                None,
            ),
            (
                "nil-numeric",
                (
                    valid,
                    xbrl_fact(entry, None, raw_value=None, is_nil=True),
                ),
                None,
            ),
        )
        for name, facts, contexts in cases:
            with self.subTest(case=name):
                with self.assertRaises(PretaxScopePolicyError):
                    normalize(
                        entry,
                        observation,
                        facts=facts,
                        contexts=contexts,
                    )

    def test_ineligible_fact_differences_do_not_resolve(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        observation = selected(entry, entry.concept, entry.expected_value)
        valid = xbrl_fact(entry, entry.expected_value)
        dimension = FilingXBRLDimension(
            FilingXBRLQName(US_GAAP, "SomeAxis"),
            FilingXBRLQName(US_GAAP, "SomeMember"),
            None,
        )
        cases = (
            xbrl_fact(entry, entry.expected_value, concept="WrongConcept"),
            xbrl_fact(
                entry,
                entry.expected_value,
                start=date(2021, 1, 2),
            ),
            xbrl_fact(
                entry,
                entry.expected_value,
                unit_id="eur",
                unit_name="EUR",
            ),
            xbrl_fact(entry, entry.expected_value, dimensions=(dimension,)),
            xbrl_fact(entry, None, raw_value=None, is_nil=True),
        )
        for fact in cases:
            with self.subTest(concept=fact.concept, context=fact.context_id):
                result = normalize(
                    entry,
                    observation,
                    facts=(fact,),
                )[FinancialMetric.PRETAX_INCOME]
                self.assertIsInstance(result, MissingHistoricalMetric)

        mixed_units = normalize(
            entry,
            observation,
            facts=(
                valid,
                xbrl_fact(
                    entry,
                    entry.expected_value,
                    context_id="eur-context",
                    unit_id="eur",
                    unit_name="EUR",
                ),
            ),
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(mixed_units, MissingHistoricalMetric)

    def test_conflicting_candidate_facts_are_ambiguous(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        result = normalize(
            entry,
            selected(entry, entry.concept, entry.expected_value),
            facts=(
                xbrl_fact(entry, entry.expected_value, context_id="a"),
                xbrl_fact(entry, entry.expected_value + 1, context_id="b"),
            ),
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(result, AmbiguousHistoricalMetric)

    def test_exact_duplicate_candidate_is_a_structural_data_error(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        observation = selected(entry, entry.concept, entry.expected_value)
        with self.assertRaises(PretaxScopePolicyError):
            normalize(entry, observation, observation)

    def test_current_concept_wins_equal_collision_and_conflict_is_ambiguous(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        for current_value, expected_type in (
            (entry.expected_value, NormalizedHistoricalValue),
            (entry.expected_value + 1, AmbiguousHistoricalMetric),
        ):
            with self.subTest(current_value=current_value):
                result = normalize(
                    entry,
                    selected(entry, CURRENT_PRETAX, current_value),
                    selected(entry, entry.concept, entry.expected_value),
                )[FinancialMetric.PRETAX_INCOME]
                self.assertIsInstance(result, expected_type)
                if isinstance(result, NormalizedHistoricalValue):
                    self.assertEqual(result.chosen_source.concept, CURRENT_PRETAX)
                    self.assertEqual(result.confirming_sources[0].concept, entry.concept)
                    self.assertIsNone(result.policy_provenance)

    def test_current_concept_ambiguity_is_never_replaced(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        current = selected(entry, CURRENT_PRETAX, entry.expected_value)
        duplicate_current = replace(
            current,
            observation=replace(current.observation, frame="CY2021"),
        )
        result = normalize(
            entry,
            current,
            duplicate_current,
            selected(entry, entry.concept, entry.expected_value),
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(result, AmbiguousHistoricalMetric)

    def test_current_concept_is_not_blocked_by_malformed_candidate(self) -> None:
        entry = PRETAX_SCOPE_EQUIVALENCE_POLICY.entries[0]
        result = normalize(
            entry,
            selected(entry, CURRENT_PRETAX, entry.expected_value),
            selected(entry, entry.concept, entry.expected_value + 1),
        )[FinancialMetric.PRETAX_INCOME]
        self.assertIsInstance(result, NormalizedHistoricalValue)
        assert isinstance(result, NormalizedHistoricalValue)
        self.assertEqual(result.chosen_source.concept, CURRENT_PRETAX)


if __name__ == "__main__":
    unittest.main()
