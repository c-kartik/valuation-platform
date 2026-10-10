"""Frozen 94-period acceptance regression and adversarial curated D&A checks."""

from dataclasses import FrozenInstanceError, replace
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from valuation_platform.normalization import (
    D_AND_A_POLICY, FinancialMetric, normalize_annual_financials,
    normalize_annual_balance_sheets, assemble_standardized_annual_history,
    standardized_history_to_dict,
)
from valuation_platform.normalization.d_and_a_scope import (
    D_AND_A_SCOPE_EQUIVALENCE_POLICY as POLICY, DAndAScopePolicyError,
    VerifiedDAndAArtifacts, apply_curated_d_and_a_scope_policy, _dimensions,
    verify_d_and_a_artifacts,
)
from valuation_platform.normalization.models import (
    AmbiguityReason, AmbiguousHistoricalMetric, EvidenceSourceKind, FactEvidence, HistoricalPeriod,
    MissingHistoricalMetric, MissingReason, NormalizedHistoricalValue,
)
from valuation_platform.normalization.output import HistoricalOutputError
from valuation_platform.sec import (
    SECCompanyIdentity, SECFiling, SECFilingXBRL, FilingXBRLContext,
    FilingXBRLFact, FilingXBRLUnit, FilingXBRLQName, FilingFactObservations,
    SelectedFactObservations,
)
from tests.normalization.test_pretax_scope import annual_period

NOW = datetime(2026, 10, 10, tzinfo=timezone.utc)
INVENTORY = json.loads((Path(__file__).resolve().parents[2] /
                       "docs/depreciation-amortization-inventory.json").read_text())["rows"]


def fixture(row):
    f = row["filing"]
    filing = SECFiling(f["accession_number"], f["form"],
                      date.fromisoformat(f["filing_date"]),
                      date.fromisoformat(f["report_date"]), f["primary_document"])
    company = SECCompanyIdentity(row["ticker"], row["cik"], f"{row['cik']:010d}",
                                 row["ticker"], "ticker-source", NOW)
    contexts = tuple(FilingXBRLContext(
        key, c["entity_identifier_scheme"], c["entity_identifier"],
        date.fromisoformat(c["start"]) if c["start"] else None,
        date.fromisoformat(c["end"]), _dimensions(c["dimensions"]),
    ) for key, c in row["contexts"].items())
    cmap = {c.context_id: c for c in contexts}
    units = tuple(FilingXBRLUnit(
        u["unit_id"], tuple(FilingXBRLQName(**q) for q in u["numerator_measures"]),
        tuple(FilingXBRLQName(**q) for q in u["denominator_measures"]),
    ) for u in row["units"].values())
    umap = {u.unit_id: u for u in units}
    facts = tuple(FilingXBRLFact(
        o["concept_key"].split("#")[0], o["concept_key"].split("#")[1],
        o["context_id"], cmap[o["context_id"]].start, cmap[o["context_id"]].end,
        cmap[o["context_id"]].dimensions, o["unit_ref"], umap.get(o["unit_ref"]),
        o["raw_value"], Decimal(o["numeric_value"]) if o["numeric_value"] else None,
        o["decimals"], o["is_nil"], filing.accession_number, row["source_url"],
    ) for o in row["occurrences"])
    instance = SECFilingXBRL(company, filing, contexts, units, facts, row["source_url"], NOW)
    entry = next((e for e in POLICY.entries if e.accession_number == filing.accession_number), None)
    period_entry = SimpleNamespace(company_cik=row["cik"],
                                   annual_start=date.fromisoformat(row["annual_start"]),
                                   annual_end=date.fromisoformat(row["annual_end"]),
                                   report_date=filing.report_date)
    period = annual_period(period_entry, filing)
    period = replace(period, filing=replace(period.filing, source_url=row["source_url"]))
    bucket = FilingFactObservations(filing, ())
    artifacts = VerifiedDAndAArtifacts(entry.accession_number, entry.artifact_digests) if entry else None
    return bucket, instance, period, artifacts


class DAndAScopeTests(unittest.TestCase):
    def setUp(self):
        self.entry = POLICY.entries[0]
        row = next(r for r in INVENTORY if r["filing"]["accession_number"] == self.entry.accession_number)
        self.bucket, self.instance, self.period, self.artifacts = fixture(row)
        self.missing = MissingHistoricalMetric(FinancialMetric.D_AND_A,
                                              MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,
                                              D_AND_A_POLICY.candidates)
        self.index = next(i for i, f in enumerate(self.instance.facts)
                          if f.concept == self.entry.concept and not f.dimensions)
        self.fact = self.instance.facts[self.index]

    def resolve(self, instance=None, direct=None, artifacts=None, bucket=None, period=None):
        return apply_curated_d_and_a_scope_policy(
            bucket or self.bucket, direct or self.missing, 1403161,
            period or self.period, instance or self.instance,
            self.artifacts if artifacts is None else artifacts,
        )

    def changed(self, **kwargs):
        facts = list(self.instance.facts)
        facts[self.index] = replace(self.fact, **kwargs)
        return replace(self.instance, facts=tuple(facts))

    def direct(self, value):
        source = FactEvidence(EvidenceSourceKind.COMPANY_FACTS, "company-facts",
                              "us-gaap", D_AND_A_POLICY.candidates[0].name, value, "USD",
                              self.entry.annual_start, self.entry.annual_end,
                              self.entry.accession_number, "10-K", self.entry.filed,
                              None, None, None)
        return NormalizedHistoricalValue(FinancialMetric.D_AND_A, value, "USD",
                                         HistoricalPeriod(self.entry.annual_start, self.entry.annual_end),
                                         source, ())

    def test_exact_94_period_regression(self):
        approved = controls = 0
        for row in INVENTORY:
            with self.subTest(accession=row["filing"]["accession_number"]):
                bucket, instance, period, artifacts = fixture(row)
                selected = SelectedFactObservations(instance.company, "company-facts", NOW, (bucket,), ())
                baseline = normalize_annual_financials(selected, policies=(D_AND_A_POLICY,),
                                                      filing_xbrl=(instance,), annual_periods=(period,))
                current = normalize_annual_financials(
                    selected, policies=(D_AND_A_POLICY,), filing_xbrl=(instance,),
                    annual_periods=(period,), d_and_a_artifacts=(artifacts,) if artifacts else (),
                )
                old, new = baseline.annual[0].metrics[0], current.annual[0].metrics[0]
                self.assertIsInstance(old, MissingHistoricalMetric)
                if row["ticker"] == "V":
                    self.assertIsInstance(new, NormalizedHistoricalValue)
                    self.assertEqual(len(new.policy_provenance.filing_xbrl_evidence), 2)
                    approved += 1
                else:
                    self.assertEqual(old, new)
                    controls += 1
        self.assertEqual((approved, controls), (5, 89))

    def test_policy_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            self.entry.expected_value = Decimal(0)
        with self.assertRaises(FrozenInstanceError):
            POLICY.version = "2"

    def test_invalid_models(self):
        changes = (
            {"company_cik": True}, {"form": "10-K/A"}, {"namespace": "extension"},
            {"expected_value": Decimal("1")}, {"unit": "EUR"}, {"concept": "Depreciation"},
            {"economic_scope": "NOT_REVIEWED"}, {"reviewed_evidence": ()}, {"support": ()},
            {"instance_digest": "bad"}, {"primary_document": "other.htm"},
            {"filed": date(2000, 1, 1)}, {"annual_start": self.entry.annual_end},
            {"reviewed_entry_json": "{}"},
        )
        for change in changes:
            with self.subTest(change=change), self.assertRaises(DAndAScopePolicyError):
                replace(self.entry, **change)
        with self.assertRaises(DAndAScopePolicyError):
            replace(POLICY, entries=(self.entry,) * 5)
        with self.assertRaises(DAndAScopePolicyError):
            replace(POLICY, version="2")
        with self.assertRaises(DAndAScopePolicyError):
            replace(POLICY, entries=list(POLICY.entries))

    def test_missing_and_swapped_review(self):
        for evidence in ((), (self.entry.reviewed_evidence[0],) * 5,
                         POLICY.entries[1].reviewed_evidence):
            with self.subTest(evidence=evidence), self.assertRaises(DAndAScopePolicyError):
                replace(self.entry, reviewed_evidence=evidence)

    def test_missing_artifacts_no_implicit_approval(self):
        result = apply_curated_d_and_a_scope_policy(self.bucket, self.missing, 1403161,
                                                  self.period, self.instance)
        self.assertEqual(result, self.missing)

    def test_incomplete_and_swapped_artifacts(self):
        for a in (replace(self.artifacts, digests=self.artifacts.digests[:-1]),
                  VerifiedDAndAArtifacts(POLICY.entries[1].accession_number,
                                        POLICY.entries[1].artifact_digests)):
            with self.subTest(a=a), self.assertRaises(DAndAScopePolicyError):
                self.resolve(artifacts=a)
        with self.assertRaises(DAndAScopePolicyError):
            verify_d_and_a_artifacts(self.entry, {}, self.instance)

    def test_three_same_context_confirm(self):
        instance = replace(self.instance, facts=(*self.instance.facts, self.fact))
        r = self.resolve(instance)
        self.assertEqual(len(r.policy_provenance.filing_xbrl_evidence), 3)
        self.assertEqual(tuple(e.occurrence_ordinal for e in r.policy_provenance.filing_xbrl_evidence),
                         (1, 2, 3))

    def test_different_contexts_confirm(self):
        c = next(c for c in self.instance.contexts if c.context_id == self.fact.context_id)
        instance = replace(self.changed(context_id="equivalent"),
                           contexts=(*self.instance.contexts, replace(c, context_id="equivalent")))
        r = self.resolve(instance)
        self.assertEqual(r.policy_provenance.filing_xbrl_evidence[0].context_id, "equivalent")
        self.assertEqual(len(r.policy_provenance.filing_xbrl_evidence), 2)

    def test_different_usd_unit_ids_confirm(self):
        u = replace(self.fact.unit, unit_id="usd-other")
        instance = replace(self.changed(unit_ref=u.unit_id, unit=u), units=(*self.instance.units, u))
        self.assertIsInstance(self.resolve(instance), NormalizedHistoricalValue)

    def test_raw_and_decimals_exact_decimal_confirm(self):
        r = self.resolve(self.changed(raw_value="804000000.00",
                                      numeric_value=Decimal("804000000.00"), decimals="-4"))
        e = r.policy_provenance.filing_xbrl_evidence[0]
        self.assertEqual((e.raw_value, e.decimals, str(e.value)), ("804000000.00", "-4", "804000000.00"))

    def test_conflicting_eligible_values_ambiguous(self):
        self.assertIsInstance(self.resolve(self.changed(numeric_value=Decimal(9), raw_value="9")),
                              AmbiguousHistoricalMetric)

    def test_single_changed_value_missing(self):
        instance = replace(self.instance, facts=tuple(
            replace(f, numeric_value=Decimal(9), raw_value="9") if f.concept == self.entry.concept
            and not f.dimensions else f for f in self.instance.facts))
        result = self.resolve(instance)
        self.assertIsInstance(result, MissingHistoricalMetric)
        self.assertEqual(result.reason, MissingReason.CURATED_D_AND_A_EVIDENCE_MISMATCH)

    def test_current_concept_precedence_equal_policy_preserved(self):
        direct = self.direct(self.entry.expected_value)
        r = self.resolve(direct=direct)
        self.assertEqual(r.chosen_source, direct.chosen_source)
        self.assertIsNotNone(r.policy_provenance.d_and_a_scope)
        self.assertEqual(len(r.confirming_sources), 2)

    def test_current_concept_conflict(self):
        self.assertIsInstance(self.resolve(direct=self.direct(1)), AmbiguousHistoricalMetric)

    def test_direct_ambiguity_never_repaired(self):
        ambiguous = AmbiguousHistoricalMetric(FinancialMetric.D_AND_A,
                                             AmbiguityReason.CONFLICTING_CONCEPT_VALUES,
                                             (self.direct(1).chosen_source,))
        self.assertIs(self.resolve(direct=ambiguous), ambiguous)

    def test_wrong_entity_does_not_confirm_or_conflict(self):
        c = next(c for c in self.instance.contexts if c.context_id == self.fact.context_id)
        bad = replace(c, context_id="wrong-entity", entity_identifier="0000000001")
        instance = replace(self.changed(context_id=bad.context_id, numeric_value=Decimal(9)),
                           contexts=(*self.instance.contexts, bad))
        r = self.resolve(instance)
        self.assertEqual(len(r.policy_provenance.filing_xbrl_evidence), 1)
        self.assertIn("EXCLUDED_ENTITY", [a.disposition for a in r.policy_provenance.d_and_a_scope.occurrences])

    def test_wrong_period_does_not_confirm(self):
        c = next(c for c in self.instance.contexts if c.context_id == self.fact.context_id)
        c = replace(c, context_id="wrong-period", start=date(2021, 1, 1))
        instance = replace(self.changed(context_id=c.context_id, start=c.start),
                           contexts=(*self.instance.contexts, c))
        self.assertEqual(len(self.resolve(instance).policy_provenance.filing_xbrl_evidence), 1)

    def test_wrong_concept_namespace_excluded(self):
        for kw in ({"concept": "Depreciation"}, {"namespace": "http://issuer/extension"}):
            with self.subTest(kw=kw):
                r = self.resolve(self.changed(**kw))
                self.assertEqual(len(r.policy_provenance.filing_xbrl_evidence), 1)

    def test_non_usd_does_not_conflict(self):
        u = replace(self.fact.unit, unit_id="eur",
                    numerator_measures=(FilingXBRLQName("http://www.xbrl.org/2003/iso4217", "EUR"),))
        instance = replace(self.changed(unit_ref="eur", unit=u, numeric_value=Decimal(9)),
                           units=(*self.instance.units, u))
        self.assertEqual(len(self.resolve(instance).policy_provenance.filing_xbrl_evidence), 1)

    def test_dimensioned_does_not_conflict(self):
        prop = next(f for f in self.instance.facts if f.concept == self.entry.concept and f.dimensions)
        instance = replace(self.instance, facts=(*self.instance.facts,
                           replace(prop, numeric_value=Decimal(1), namespace="http://extension")))
        self.assertEqual(len(self.resolve(instance).policy_provenance.filing_xbrl_evidence), 2)

    def test_missing_or_changed_support_cannot_resolve(self):
        for remove in (True, False):
            facts = tuple(f for f in self.instance.facts if f.concept != "AmortizationOfIntangibleAssets") if remove else tuple(
                replace(f, numeric_value=Decimal(1)) if f.concept == "AmortizationOfIntangibleAssets" else f
                for f in self.instance.facts)
            self.assertIsInstance(self.resolve(replace(self.instance, facts=facts)), MissingHistoricalMetric)

    def test_nil_numeric_collision_data_error(self):
        with self.assertRaisesRegex(DAndAScopePolicyError, "nil/numeric"):
            self.resolve(self.changed(is_nil=True, numeric_value=None, raw_value=None))

    def test_all_nil_missing(self):
        instance = replace(self.instance, facts=tuple(
            replace(f, is_nil=True, numeric_value=None, raw_value=None)
            if f.concept == self.entry.concept and not f.dimensions else f
            for f in self.instance.facts))
        self.assertEqual(self.resolve(instance), self.missing)

    def test_broken_context_unit_and_source_data_errors(self):
        for kw in ({"context_id": "missing"}, {"start": date(2021, 1, 1)},
                   {"unit_ref": "missing"}, {"source_url": "other-source"},
                   {"accession_number": POLICY.entries[1].accession_number},
                   {"numeric_value": None}, {"numeric_value": Decimal("NaN")}):
            with self.subTest(kw=kw), self.assertRaises(DAndAScopePolicyError):
                self.resolve(self.changed(**kw))

    def test_duplicate_context_and_unit_definitions_data_errors(self):
        for instance in (replace(self.instance, contexts=(*self.instance.contexts, self.instance.contexts[0])),
                         replace(self.instance, units=(*self.instance.units, self.instance.units[0]))):
            with self.assertRaises(DAndAScopePolicyError):
                self.resolve(instance)

    def test_amended_future_unregistered_wrong_dates_missing(self):
        for change in ({"form": "10-K/A"}, {"accession_number": "0001403161-26-000001"},
                       {"filing_date": date(2026, 1, 1)}, {"primary_document": "other.htm"},
                       {"report_date": date(2021, 9, 29)}):
            bucket = replace(self.bucket, filing=replace(self.bucket.filing, **change))
            self.assertEqual(self.resolve(bucket=bucket), self.missing)

    def test_other_metric_rejected(self):
        with self.assertRaises(DAndAScopePolicyError):
            self.resolve(direct=replace(self.missing, metric=FinancialMetric.PRETAX_INCOME))

    def test_normalization_standardized_serialization_exact_provenance(self):
        selected = SelectedFactObservations(self.instance.company, "company-facts", NOW, (self.bucket,), ())
        history = normalize_annual_financials(
            selected, filing_xbrl=(self.instance,), annual_periods=(self.period,),
            d_and_a_artifacts=(self.artifacts,),
        )
        balance = normalize_annual_balance_sheets(selected)
        output = assemble_standardized_annual_history(history, balance)
        payload = json.loads(json.dumps(standardized_history_to_dict(output)))
        self.assertEqual(payload["schema_version"], "4")
        m = next(m for m in payload["annual"][0]["measures"]
                 if m["measure"] == FinancialMetric.D_AND_A.value)
        p = m["policy"]
        self.assertEqual(p["policy_id"], POLICY.policy_id)
        self.assertEqual(len(p["filing_xbrl_evidence"]), 2)
        self.assertEqual([e["occurrence_ordinal"] for e in p["filing_xbrl_evidence"]], [1, 2])
        audit = p["d_and_a_scope"]
        self.assertEqual(audit["reviewed_entry"]["filing"]["accession_number"], self.entry.accession_number)
        self.assertEqual(len(audit["verified_artifact_digests"]), 9)
        self.assertEqual(len(audit["supporting_facts"]), 2)
        self.assertTrue(audit["supporting_facts"][0]["dimensions"])
        self.assertEqual(audit["confirming_original_ordinals"],
                         [a["original_instance_ordinal"] for a in audit["occurrences"]
                          if a["disposition"] == "ELIGIBLE"])
        self.assertEqual([e["numeric_value"] for e in p["filing_xbrl_evidence"]],
                         ["804000000", "804000000"])
        etr = next(m for m in payload["annual"][0]["measures"]
                   if m["measure"] == FinancialMetric.REPORTED_EFFECTIVE_TAX_RATE.value)
        self.assertEqual(etr["status"], "missing")

    def test_generic_policy_unchanged(self):
        self.assertEqual(tuple(c.name for c in D_AND_A_POLICY.candidates),
                         ("DepreciationDepletionAndAmortization",))

    def test_malformed_annual_authority_rejected(self):
        for period in (
            replace(self.period, filing=replace(self.period.filing, registrant_cik=1)),
            replace(self.period, evidence=replace(self.period.evidence, registrant_cik=1)),
            replace(self.period, filing=replace(self.period.filing, source_url="other")),
        ):
            with self.assertRaises(DAndAScopePolicyError):
                self.resolve(period=period)

    def test_missing_numeric_unit_structural_error(self):
        with self.assertRaises(DAndAScopePolicyError):
            self.resolve(self.changed(unit_ref=None, unit=None))

    def test_nil_support_collision_structural_error(self):
        f = next(f for f in self.instance.facts if f.concept == "AmortizationOfIntangibleAssets")
        with self.assertRaises(DAndAScopePolicyError):
            self.resolve(replace(self.instance, facts=(*self.instance.facts,
                         replace(f, is_nil=True, numeric_value=None, raw_value=None))))

    def test_all_non_usd_missing(self):
        u = replace(self.fact.unit, unit_id="eur",
                    numerator_measures=(FilingXBRLQName("http://www.xbrl.org/2003/iso4217", "EUR"),))
        facts = tuple(replace(f, unit_ref="eur", unit=u)
                      if f.concept == self.entry.concept and not f.dimensions else f
                      for f in self.instance.facts)
        self.assertEqual(self.resolve(replace(self.instance, facts=facts,
                                             units=(*self.instance.units, u))), self.missing)

    def test_forged_instance_metadata_structural_error(self):
        for instance in (replace(self.instance, source_url="other"),
                         replace(self.instance, company=replace(self.instance.company, cik=1)),
                         replace(self.instance, filing=replace(self.instance.filing, primary_document="other"))):
            with self.assertRaises(DAndAScopePolicyError):
                self.resolve(instance)

    def test_duplicate_bundle_normalization_error(self):
        from valuation_platform.normalization.historical import NormalizationError
        selected = SelectedFactObservations(self.instance.company, "company-facts", NOW, (self.bucket,), ())
        with self.assertRaises(NormalizationError):
            normalize_annual_financials(selected, d_and_a_artifacts=(self.artifacts, self.artifacts))

    def test_incomplete_provenance_rejected_at_output_boundary(self):
        from valuation_platform.normalization.output import _policy_reference
        p = self.resolve().policy_provenance
        bad_audits = (
            None,
            replace(p.d_and_a_scope, supporting_facts=()),
            replace(p.d_and_a_scope, confirming_original_ordinals=(999,)),
            replace(p.d_and_a_scope, verified_artifact_digests=()),
            replace(p.d_and_a_scope, occurrences=tuple(reversed(p.d_and_a_scope.occurrences))),
        )
        for audit in bad_audits:
            with self.subTest(audit=audit), self.assertRaises(HistoricalOutputError):
                _policy_reference(replace(p, d_and_a_scope=audit), self.bucket.filing)

    def test_derived_consumer_retains_policy_support(self):
        from valuation_platform.normalization.models import DerivedMetricOperand, DerivedHistoricalValue, DerivationOperation
        from valuation_platform.normalization.output import _supporting_policy_references
        direct = self.resolve()
        operand = DerivedMetricOperand(
            direct.metric, direct.value, direct.unit, direct.period,
            direct.chosen_source, direct.confirming_sources, direct.policy_provenance,
        )
        derived = DerivedHistoricalValue(
            FinancialMetric.D_AND_A, direct.value, "USD", direct.period,
            "test-consumer", DerivationOperation.ADD, (), (operand,),
        )
        support = _supporting_policy_references(derived, self.bucket.filing)
        self.assertEqual(support[0].d_and_a_scope, direct.policy_provenance.d_and_a_scope)

    def test_raw_serialization_and_order_repeatable(self):
        from valuation_platform.normalization.output import _policy_reference, _serialize_policy
        r = self.resolve(self.changed(raw_value="804000000.00", numeric_value=Decimal("804000000.00"), decimals="-4"))
        p = _policy_reference(r.policy_provenance, self.bucket.filing)
        one = _serialize_policy(p)
        two = json.loads(json.dumps(_serialize_policy(p)))
        self.assertEqual(one, two)
        self.assertEqual(one["filing_xbrl_evidence"][0]["numeric_value"], "804000000.00")
        self.assertEqual(one["filing_xbrl_evidence"][0]["raw_value"], "804000000.00")

    def test_2025_exact_combined_not_rounded_sum(self):
        row = next(r for r in INVENTORY if r["filing"]["accession_number"] == POLICY.entries[-1].accession_number)
        b, x, p, a = fixture(row)
        r = apply_curated_d_and_a_scope_policy(b, self.missing, 1403161, p, x, a)
        self.assertEqual(r.value, Decimal(1220000000))
        self.assertNotEqual(r.value, Decimal(1178000000))


if __name__ == "__main__":
    unittest.main()
