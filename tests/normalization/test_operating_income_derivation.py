from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import unittest
import json

from valuation_platform.normalization import (
    AmbiguousHistoricalMetric,
    DerivedHistoricalValue,
    EvidenceSourceKind,
    FactEvidence,
    FinancialMetric,
    HistoricalFilingResult,
    HistoricalPeriod,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedHistoricalValue,
    NormalizedHistoricalFinancials,
    OPERATING_INCOME_COMPONENT_DERIVATION_POLICY,
    OPERATING_INCOME_DERIVATION_POLICY_ID,
    OPERATING_INCOME_DERIVATION_POLICY_VERSION,
    OperatingIncomeDerivationPolicy,
    OperatingIncomeDerivationPolicyError,
    OperatingIncomeOperandState,
    OperatingTaxReadinessContext,
    OperatingTaxPolicy,
    OperatingTaxReadinessStatus,
    SelectedTaxFiling,
    TaxBridgeStyle,
    TaxMonetaryBasis,
    apply_curated_operating_income_derivation_policy,
    evaluate_operating_tax_readiness,
    normalize_annual_financials,
    normalize_tax_reconciliation_bridge,
    operating_income_derivation_entry_for,
)
from valuation_platform.normalization.operating_tax import (
    OperatingTaxReadinessError,
    _validate_financial_inputs,
)
from valuation_platform.normalization.operating_income_derivation import (
    OperatingIncomeSignedTerm,
    validate_operating_income_derivation_provenance,
)
from valuation_platform.normalization.output import (
    HistoricalResolutionKind,
    _map_duration_result,
    _serialize_measure,
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
ISO4217 = "http://www.xbrl.org/2003/iso4217"
CONTROLS = (
    (93410, "0000093410-22-000019", date(2021,1,1), date(2021,12,31)),
    (93410, "0000093410-23-000009", date(2022,1,1), date(2022,12,31)),
    (93410, "0000093410-24-000013", date(2023,1,1), date(2023,12,31)),
    (93410, "0000093410-25-000009", date(2024,1,1), date(2024,12,31)),
    (93410, "0000093410-26-000078", date(2025,1,1), date(2025,12,31)),
    (40545, "0000040545-22-000008", date(2021,1,1), date(2021,12,31)),
    (40545, "0000040545-23-000023", date(2022,1,1), date(2022,12,31)),
    (40545, "0000040545-24-000027", date(2023,1,1), date(2023,12,31)),
    (40545, "0000040545-25-000015", date(2024,1,1), date(2024,12,31)),
    (40545, "0000040545-26-000008", date(2025,1,1), date(2025,12,31)),
)


def company(cik: int) -> SECCompanyIdentity:
    return SECCompanyIdentity("TEST", cik, f"{cik:010d}", "Test", "ticker", NOW)


def filing(entry, *, form: str = "10-K", accession: str | None = None) -> SECFiling:
    return SECFiling(
        accession or entry.accession_number,
        form,
        entry.report_date + timedelta(days=45),
        entry.report_date,
        f"test-{entry.report_date:%Y%m%d}.htm",
    )


def annual_period(entry, selected_filing: SECFiling | None = None) -> ResolvedAnnualPeriod:
    selected_filing = selected_filing or filing(entry)
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
            AnnualPeriodDEIEvidence("DocumentFiscalYearFocus", str(entry.annual_end.year), ()),
            AnnualPeriodDEIEvidence("DocumentPeriodEndDate", entry.annual_end.isoformat(), ()),
        ),
    )
    return ResolvedAnnualPeriod(filing_evidence, evidence)


def xbrl_fact(
    entry,
    definition,
    value: Decimal | None,
    *,
    context_id: str = "annual",
    unit_id: str = "usd",
    unit_namespace: str = ISO4217,
    unit_name: str = "USD",
    raw: str | None = None,
    decimals: str | None = "-6",
    dimensions: tuple[FilingXBRLDimension, ...] = (),
    nil: bool = False,
    start: date | None = None,
    end: date | None = None,
    accession: str | None = None,
) -> FilingXBRLFact:
    unit = FilingXBRLUnit(
        unit_id,
        (FilingXBRLQName(unit_namespace, unit_name),),
        (),
    )
    return FilingXBRLFact(
        definition.namespace,
        definition.concept,
        context_id,
        start or entry.annual_start,
        end or entry.annual_end,
        dimensions,
        unit_id,
        unit,
        None if nil else (str(value) if raw is None else raw),
        None if nil else value,
        decimals,
        nil,
        accession or entry.accession_number,
        "xbrl-source",
    )


def artifact(entry, *extra: FilingXBRLFact, omit: str | None = None) -> SECFilingXBRL:
    facts = []
    alternates = {item.operand_id: item for item in entry.reviewed_alternates}
    for definition in entry.operands:
        if definition.operand_id == omit:
            continue
        if definition.state is OperatingIncomeOperandState.REQUIRED:
            facts.append(xbrl_fact(entry, definition, definition.expected_value))
            if definition.operand_id in alternates:
                alternate = alternates[definition.operand_id]
                facts.append(
                    xbrl_fact(
                        entry,
                        definition,
                        alternate.value,
                        decimals=alternate.decimals,
                    )
                )
        elif definition.operand_id in alternates:
            alternate = alternates[definition.operand_id]
            facts.append(
                xbrl_fact(
                    entry,
                    definition,
                    alternate.value,
                    decimals=alternate.decimals,
                )
            )
    facts.extend(extra)
    contexts = {}
    units = {}
    for fact in facts:
        contexts.setdefault(
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
        if fact.unit is not None:
            units.setdefault(fact.unit.unit_id, fact.unit)
    return SECFilingXBRL(
        company(entry.company_cik),
        filing(entry),
        tuple(contexts.values()),
        tuple(units.values()),
        tuple(facts),
        "xbrl-source",
        NOW,
    )


def selected_input(entry, *observations: SelectedFactObservation) -> SelectedFactObservations:
    return SelectedFactObservations(
        company(entry.company_cik),
        "facts-source",
        NOW,
        (FilingFactObservations(filing(entry), tuple(observations)),),
        (),
    )


def normalize(entry, xbrl: SECFilingXBRL, *observations: SelectedFactObservation):
    output = normalize_annual_financials(
        selected_input(entry, *observations),
        filing_xbrl=(xbrl,),
        annual_periods=(annual_period(entry),),
    )
    return next(
        item
        for item in output.annual[0].metrics
        if item.metric is FinancialMetric.OPERATING_INCOME
    )


def direct_observation(entry, value: Decimal) -> SelectedFactObservation:
    return SelectedFactObservation(
        "us-gaap",
        "OperatingIncomeLoss",
        SECFactObservation(
            "USD",
            int(value),
            entry.annual_start,
            entry.annual_end,
            entry.accession_number,
            entry.annual_end.year,
            "FY",
            "10-K",
            filing(entry).filing_date,
            None,
        ),
        ObservationRelationship.CURRENT,
    )


class OperatingIncomeDerivationTests(unittest.TestCase):
    def test_registry_is_immutable_versioned_and_has_exact_25_entries(self) -> None:
        policy = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY
        self.assertEqual(policy.policy_id, OPERATING_INCOME_DERIVATION_POLICY_ID)
        self.assertEqual(policy.version, OPERATING_INCOME_DERIVATION_POLICY_VERSION)
        self.assertEqual(len(policy.entries), 25)
        self.assertEqual(len({entry.key for entry in policy.entries}), 25)
        with self.assertRaises(FrozenInstanceError):
            policy.version = "2"  # type: ignore[misc]

    def test_all_25_entries_resolve_exact_arithmetic_and_ordered_provenance(self) -> None:
        counts = {}
        for entry in OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries:
            with self.subTest(accession=entry.accession_number):
                result = normalize(entry, artifact(entry))
                self.assertIsInstance(result, DerivedHistoricalValue)
                assert isinstance(result, DerivedHistoricalValue)
                self.assertEqual(result.value, entry.expected_value)
                self.assertEqual(result.policy_id, OPERATING_INCOME_DERIVATION_POLICY_ID)
                self.assertEqual(result.policy_version, "1")
                provenance = result.derivation_provenance
                self.assertIsNotNone(provenance)
                assert provenance is not None
                self.assertEqual(provenance.accession_number, entry.accession_number)
                self.assertEqual(
                    [item.ordinal for item in provenance.operands],
                    list(range(1, len(entry.operands) + 1)),
                )
                contributions = {
                    item.operand_id: item.contribution
                    for item in provenance.operands
                    if item.contribution is not None
                }
                self.assertEqual(sum(contributions.values(), Decimal("0")), entry.expected_value)
                self.assertTrue(all(item.passed for item in provenance.validations))
                counts[entry.company_cik] = counts.get(entry.company_cik, 0) + 1
        self.assertEqual(counts, {59478: 5, 200406: 5, 310158: 5, 319201: 5, 51143: 5})

    def test_all_ten_cvx_ge_controls_are_unregistered_and_remain_missing(self) -> None:
        for cik, accession, start, end in CONTROLS:
            with self.subTest(accession=accession):
                self.assertIsNone(
                    operating_income_derivation_entry_for(cik, accession, end, start, end)
                )
                template = replace(OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0],
                                   company_cik=cik, accession_number=accession,
                                   report_date=end, annual_start=start, annual_end=end)
                self.assertIsInstance(normalize(template, artifact(template)), MissingHistoricalMetric)

    def test_configuration_rejects_mutable_unknown_duplicate_and_overlapping_terms(self) -> None:
        policy = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY
        entry = policy.entries[0]
        cases = (
            lambda: replace(policy, entries=list(policy.entries)),
            lambda: replace(policy, entries=policy.entries[:-1]),
            lambda: replace(policy, version="2"),
            lambda: replace(policy, entries=(entry, *policy.entries[1:-1], entry)),
            lambda: replace(entry, operands=list(entry.operands)),
            lambda: replace(entry, calculation_terms=(*entry.calculation_terms, entry.calculation_terms[0])),
            lambda: replace(entry, calculation_terms=(OperatingIncomeSignedTerm(1, "unknown", Decimal(1)),)),
            lambda: OperatingIncomeSignedTerm(1, "R", 1),
            lambda: OperatingIncomeSignedTerm(1, "R", Decimal(2)),
            lambda: replace(entry, operands=(entry.operands[0], replace(entry.operands[1], namespace=entry.operands[0].namespace, concept=entry.operands[0].concept), *entry.operands[2:])),
            lambda: replace(entry, form="10-K/A"),
            lambda: replace(entry, unit="EUR"),
        )
        for index, construct in enumerate(cases):
            with self.subTest(case=index), self.assertRaises(OperatingIncomeDerivationPolicyError):
                construct()

    def test_direct_survives_absent_or_incomplete_derivation(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        observation = direct_observation(entry, entry.expected_value)
        output = normalize_annual_financials(selected_input(entry, observation), annual_periods=(annual_period(entry),))
        result = next(item for item in output.annual[0].metrics if item.metric is FinancialMetric.OPERATING_INCOME)
        self.assertIsInstance(result, NormalizedHistoricalValue)
        incomplete = normalize(entry, artifact(entry, omit="R"), observation)
        self.assertIsInstance(incomplete, NormalizedHistoricalValue)
        self.assertEqual(incomplete.supporting_derivation_policies, ())

    def test_malformed_entity_context_unit_raw_and_source_are_data_errors(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        original = artifact(entry)
        cases = (
            replace(original, contexts=(replace(original.contexts[0], entity_identifier="0000000001"),)),
            replace(original, contexts=(replace(original.contexts[0], start=entry.annual_start + timedelta(days=1)),)),
            replace(original, units=()),
            replace(original, facts=(replace(original.facts[0], raw_value="broken"), *original.facts[1:])),
            replace(original, facts=(replace(original.facts[0], raw_value="1"), *original.facts[1:])),
            replace(original, facts=(replace(original.facts[0], source_url="other"), *original.facts[1:])),
        )
        for index, candidate in enumerate(cases):
            with self.subTest(case=index), self.assertRaises(OperatingIncomeDerivationPolicyError):
                normalize(entry, candidate)

    def test_wrong_concept_namespace_and_dimensioned_conflicts_are_excluded(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        original = artifact(entry)
        for field in (dict(concept="OtherConcept"), dict(namespace="other")):
            self.assertIsInstance(normalize(entry, replace(original, facts=(replace(original.facts[0], **field), *original.facts[1:]))), MissingHistoricalMetric)
        axis = FilingXBRLDimension(FilingXBRLQName("issuer", "Axis"), FilingXBRLQName("issuer", "Member"), None)
        extra = xbrl_fact(entry, entry.operands[0], Decimal(1), context_id="segment", dimensions=(axis,))
        self.assertIsInstance(normalize(entry, artifact(entry, extra)), DerivedHistoricalValue)

    def test_lly_alternate_cannot_replace_face_and_third_value_conflicts(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[2]
        original = artifact(entry)
        definition = next(item for item in entry.operands if item.operand_id == "A")
        without_face = replace(original, facts=tuple(item for item in original.facts if not (item.concept == definition.concept and item.numeric_value == definition.expected_value)))
        self.assertIsInstance(normalize(entry, without_face), MissingHistoricalMetric)
        conflict = xbrl_fact(entry, definition, Decimal(1), context_id="third")
        self.assertIsInstance(normalize(entry, artifact(entry, conflict)), AmbiguousHistoricalMetric)

    def test_provenance_rejects_partial_operands_and_altered_signs(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        result = normalize(entry, artifact(entry))
        provenance = result.derivation_provenance
        partial = replace(provenance, operands=provenance.operands[:-1])
        altered = replace(provenance.operands[0], coefficient=Decimal(-1), contribution=-provenance.operands[0].expected_value)
        for candidate in (partial, replace(provenance, operands=(altered, *provenance.operands[1:]))):
            with self.assertRaises(OperatingIncomeDerivationPolicyError):
                validate_operating_income_derivation_provenance(candidate)

    def test_equivalent_duplicate_contexts_confirm_and_preserve_order(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        definition = entry.operands[0]
        duplicate = xbrl_fact(
            entry,
            definition,
            definition.expected_value,
            context_id="annual-2",
            unit_id="usd-2",
            raw=f"{definition.expected_value}.0",
            decimals="-3",
        )
        result = normalize(entry, artifact(entry, duplicate))
        assert isinstance(result, DerivedHistoricalValue)
        operand = result.derivation_provenance.operands[0]  # type: ignore[union-attr]
        self.assertEqual([item.occurrence_ordinal for item in operand.occurrences], [1, 2])
        self.assertEqual([item.context_id for item in operand.occurrences], ["annual", "annual-2"])
        self.assertEqual([item.unit_ref for item in operand.occurrences], ["usd", "usd-2"])
        self.assertEqual(operand.occurrences[1].raw_value, f"{definition.expected_value}.0")

    def test_lly_lower_precision_occurrences_are_nonselected_provenance(self) -> None:
        for entry in OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[2:5]:
            with self.subTest(accession=entry.accession_number):
                result = normalize(entry, artifact(entry))
                assert isinstance(result, DerivedHistoricalValue)
                operand = next(
                    item
                    for item in result.derivation_provenance.operands  # type: ignore[union-attr]
                    if item.operand_id == "A"
                )
                self.assertEqual(len(operand.occurrences), 1)
                self.assertEqual(len(operand.reviewed_nonselected_occurrences), 1)
                self.assertNotEqual(
                    operand.occurrences[0].value,
                    operand.reviewed_nonselected_occurrences[0].value,
                )

    def test_unexpected_conflicting_value_is_ambiguous(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        definition = entry.operands[0]
        conflict = xbrl_fact(entry, definition, definition.expected_value + 1, context_id="conflict")
        self.assertIsInstance(normalize(entry, artifact(entry, conflict)), AmbiguousHistoricalMetric)

    def test_missing_dimensioned_nil_non_usd_wrong_period_and_wrong_accession_do_not_resolve(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        definition = entry.operands[0]
        axis = FilingXBRLDimension(
            FilingXBRLQName("issuer", "Axis"),
            FilingXBRLQName("issuer", "Member"),
            None,
        )
        cases = (
            artifact(entry, omit="R"),
            artifact(entry, xbrl_fact(entry, definition, definition.expected_value, context_id="dimensioned", dimensions=(axis,)), omit="R"),
            artifact(entry, xbrl_fact(entry, definition, None, nil=True), omit="R"),
            artifact(entry, xbrl_fact(entry, definition, definition.expected_value, unit_id="eur", unit_name="EUR"), omit="R"),
            artifact(entry, xbrl_fact(entry, definition, definition.expected_value, context_id="wrong-period", start=entry.annual_start + timedelta(days=1)), omit="R"),
        )
        for candidate in cases:
            with self.subTest(case=len(candidate.facts)):
                result = normalize(entry, candidate)
                self.assertNotIsInstance(result, DerivedHistoricalValue)
        wrong_accession = artifact(
            entry,
            xbrl_fact(
                entry,
                definition,
                definition.expected_value,
                accession="0000000000-00-000000",
            ),
            omit="R",
        )
        with self.assertRaises(OperatingIncomeDerivationPolicyError):
            normalize(entry, wrong_accession)

    def test_nil_numeric_collision_and_broken_context_are_data_errors(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        definition = entry.operands[0]
        nil = xbrl_fact(entry, definition, None, context_id="nil", nil=True)
        with self.assertRaises(OperatingIncomeDerivationPolicyError):
            normalize(entry, artifact(entry, nil))
        broken = replace(xbrl_fact(entry, definition, definition.expected_value), context_id="missing")
        xbrl = artifact(entry)
        xbrl = replace(xbrl, facts=(broken, *xbrl.facts[1:]))
        with self.assertRaises(OperatingIncomeDerivationPolicyError):
            normalize(entry, xbrl)

    def test_direct_precedence_equal_confirmation_and_conflict(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        equal = normalize(entry, artifact(entry), direct_observation(entry, entry.expected_value))
        self.assertIsInstance(equal, NormalizedHistoricalValue)
        assert isinstance(equal, NormalizedHistoricalValue)
        self.assertEqual(len(equal.supporting_derivation_policies), 1)
        conflict = normalize(entry, artifact(entry), direct_observation(entry, entry.expected_value + 1))
        self.assertIsInstance(conflict, AmbiguousHistoricalMetric)
        self.assertEqual(len(conflict.supporting_derivation_policies), 1)
        conflict_payload = _serialize_measure(_map_duration_result(conflict, filing(entry), FinancialMetric.OPERATING_INCOME))
        self.assertEqual(conflict_payload["supporting_policies"][0]["version"], "1")
        equal_payload = _serialize_measure(_map_duration_result(equal, filing(entry), FinancialMetric.OPERATING_INCOME))
        self.assertEqual(equal_payload["resolution"], "direct")
        self.assertEqual(json.loads(json.dumps(equal_payload)), equal_payload)

    def test_direct_ambiguity_is_never_replaced(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        observations = (
            direct_observation(entry, entry.expected_value),
            direct_observation(entry, entry.expected_value + 1),
        )
        result = normalize(entry, artifact(entry), *observations)
        self.assertIsInstance(result, AmbiguousHistoricalMetric)

    def test_future_amended_and_wrong_accession_are_not_registered(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        self.assertIsNone(
            operating_income_derivation_entry_for(
                entry.company_cik,
                "0000059478-27-000001",
                date(2026,12,31),
                date(2026,1,1),
                date(2026,12,31),
            )
        )
        direct = MissingHistoricalMetric(
            FinancialMetric.OPERATING_INCOME,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
            (),
        )
        amended_filing = filing(entry, form="10-K/A")
        bucket = FilingFactObservations(amended_filing, ())
        result = apply_curated_operating_income_derivation_policy(
            bucket,
            direct,
            entry.company_cik,
            annual_period(entry, amended_filing),
            None,
        )
        self.assertIs(result, direct)

    def test_ibm_validation_variances_are_exact_and_never_change_value(self) -> None:
        ibm = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[-5:]
        expected = ((-1000000,0),(1000000,-1000000),(0,-1000000),(1000000,0),(-1000000,1000000))
        for entry, variances in zip(ibm, expected):
            result = normalize(entry, artifact(entry))
            assert isinstance(result, DerivedHistoricalValue)
            self.assertEqual(result.value, entry.expected_value)
            provenance = result.derivation_provenance
            assert provenance is not None
            self.assertEqual(tuple(item.variance for item in provenance.validations), tuple(Decimal(x) for x in variances))
            self.assertEqual({item.display_scale for item in provenance.validations}, {Decimal("1000000")})

    def test_changed_ibm_gate_fails_without_plugging_value(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[-1]
        bad_validation = replace(entry.validations[-1], expected_variance=Decimal("0"))
        bad_entry = replace(entry, validations=(*entry.validations[:-1], bad_validation))
        policy = OperatingIncomeDerivationPolicy(
            OPERATING_INCOME_DERIVATION_POLICY_ID,
            OPERATING_INCOME_DERIVATION_POLICY_VERSION,
            FinancialMetric.OPERATING_INCOME,
            "test",
            (*OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[:-1], bad_entry),
        )
        direct = MissingHistoricalMetric(
            FinancialMetric.OPERATING_INCOME,
            MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
            (),
        )
        result = apply_curated_operating_income_derivation_policy(
            FilingFactObservations(filing(entry), ()),
            direct,
            entry.company_cik,
            annual_period(entry),
            artifact(entry),
            policy,
        )
        self.assertIsInstance(result, MissingHistoricalMetric)

    def test_ibm_other_display_scale_cannot_use_rounding_gate(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[-1]
        original = artifact(entry)
        changed = replace(original, facts=(replace(original.facts[0], decimals="-3"), *original.facts[1:]))
        self.assertIsInstance(normalize(entry, changed), MissingHistoricalMetric)

    def test_standardized_output_and_serialization_retain_complete_policy(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[2]
        result = normalize(entry, artifact(entry))
        assert isinstance(result, DerivedHistoricalValue)
        mapped = _map_duration_result(result, filing(entry), FinancialMetric.OPERATING_INCOME)
        self.assertEqual(mapped.resolution, HistoricalResolutionKind.DERIVED)
        payload = _serialize_measure(mapped)
        policy = payload["policy"]
        self.assertEqual(policy["policy_id"], OPERATING_INCOME_DERIVATION_POLICY_ID)
        self.assertEqual(policy["version"], "1")
        derivation = policy["operating_income_derivation"]
        self.assertEqual(derivation["calculated_value"], str(entry.expected_value))
        self.assertEqual([item["ordinal"] for item in derivation["operands"]], list(range(1,9)))
        acquired = next(item for item in derivation["operands"] if item["operand_id"] == "A")
        self.assertEqual(len(acquired["reviewed_nonselected_occurrences"]), 1)
        self.assertEqual(acquired["reviewed_nonselected_reasons"], ["REVIEWED_NON_FACE_PRECISION"])
        self.assertEqual(acquired["occurrences"][0]["entity_identifier"], "0000059478")
        self.assertEqual(json.loads(json.dumps(payload)), payload)
        self.assertTrue(all(item["passed"] for item in derivation["validations"]))

    def test_operating_tax_accepts_only_complete_active_derivation_provenance(self) -> None:
        entry = OPERATING_INCOME_COMPONENT_DERIVATION_POLICY.entries[0]
        operating_income = normalize(entry, artifact(entry))
        assert isinstance(operating_income, DerivedHistoricalValue)
        selected_filing = filing(entry)
        pretax_definition = next(item for item in entry.operands if item.operand_id == "T")
        pretax_source = FactEvidence(
            EvidenceSourceKind.COMPANY_FACTS,
            "facts-source",
            "us-gaap",
            pretax_definition.concept,
            int(pretax_definition.expected_value),  # type: ignore[arg-type]
            "USD",
            entry.annual_start,
            entry.annual_end,
            entry.accession_number,
            "10-K",
            selected_filing.filing_date,
            entry.annual_end.year,
            "FY",
            None,
        )
        pretax = NormalizedHistoricalValue(
            FinancialMetric.PRETAX_INCOME,
            pretax_definition.expected_value,
            "USD",
            HistoricalPeriod(entry.annual_start, entry.annual_end),
            pretax_source,
            (),
        )
        annual = HistoricalFilingResult(selected_filing, (operating_income, pretax))
        financials = NormalizedHistoricalFinancials(
            company(entry.company_cik),
            "facts-source",
            NOW,
            (annual,),
        )
        selected_tax = SelectedTaxFiling(
            company(entry.company_cik),
            selected_filing,
            "https://www.sec.gov/Archives/test.htm",
        )
        bridge = normalize_tax_reconciliation_bridge(
            selected_tax,
            style=TaxBridgeStyle.RATE,
            starting_value=Decimal("21"),
            reported_value=Decimal("21"),
            rows=(),
            displayed_precision=Decimal("0.1"),
            row_inventory_complete=True,
            pretax_income=pretax_definition.expected_value,
        )
        context = OperatingTaxReadinessContext(
            financials,
            annual,
            bridge,
            TaxMonetaryBasis("USD", Decimal("1")),
            None,
            "tax-policy",
            "1",
        )
        _validate_financial_inputs(context, operating_income, pretax)
        tax_policy = OperatingTaxPolicy(
            "tax-policy",
            "1",
            entry.company_cik,
            (),
            (),
            "Synthetic compatibility boundary; no tax approval is inferred.",
            supported_accessions=(entry.accession_number,),
        )
        readiness = evaluate_operating_tax_readiness(context, tax_policy)
        self.assertEqual(
            readiness.status,
            OperatingTaxReadinessStatus.MISSING_INPUT,
        )
        self.assertIs(readiness.operating_income, operating_income)
        serialized = readiness.serialize_financial_inputs()
        self.assertEqual(serialized["operating_income"]["policy"]["version"], "1")
        self.assertEqual(json.loads(json.dumps(serialized)), serialized)
        with self.assertRaises(OperatingTaxReadinessError):
            _validate_financial_inputs(
                context,
                replace(operating_income, policy_version=None),
                pretax,
            )
        partial = replace(operating_income.derivation_provenance, operands=operating_income.derivation_provenance.operands[:-1])
        with self.assertRaises(OperatingTaxReadinessError):
            _validate_financial_inputs(context, replace(operating_income, derivation_provenance=partial), pretax)


if __name__ == "__main__":
    unittest.main()
