"""Isolated analyst contracts and retained-evidence regression, no network."""
from dataclasses import replace
from datetime import date
from decimal import Decimal, localcontext
import base64
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from valuation_platform.analyst.nwc import (
    Amount, AnalystNWCError, Artifact, Component, Evidence, EvidenceKind,
    Occurrence, Period, Scenario, Treatment, change, deserialize, evaluate, serialize,
    serialize_evaluation, deserialize_evaluation,
)

ROOT = Path(__file__).resolve().parents[2]
P = Period(789019, "0000950170-25-100235", date(2024, 7, 1), date(2025, 6, 30))


def artifact(period=P, name="a", value="100", decimals="INF", extra=""):
    body = f'''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:iso4217="http://www.xbrl.org/2003/iso4217" xmlns:t="https://taxonomy" xmlns:dei="http://xbrl.sec.gov/dei/2024">
<xbrli:context id="c"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">{period.cik}</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:instant>{period.annual_end}</xbrli:instant></xbrli:period></xbrli:context>
<xbrli:context id="fy"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">{period.cik}</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:startDate>{period.annual_start}</xbrli:startDate><xbrli:endDate>{period.annual_end}</xbrli:endDate></xbrli:period></xbrli:context>
<xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
<dei:DocumentFiscalPeriodFocus contextRef="fy">FY</dei:DocumentFiscalPeriodFocus>
<t:{name} contextRef="c" unitRef="USD" decimals="{decimals}">{value}</t:{name}>{extra}</xbrli:xbrl>'''.encode()
    return Artifact(f"https://www.sec.gov/Archives/edgar/data/{period.cik}/{period.accession.replace('-', '')}/sample_htm.xml", period.accession,
                    "sec_response_body_bytes", "sha256_sec_response_body_bytes",
                    hashlib.sha256(body).hexdigest(), body)


def reported(value="100", period=P, name="a", decimals="INF"):
    return Evidence(name, EvidenceKind.REPORTED, period, "reviewer", date(2026, 10, 11),
                    "selected current balance", ("synthetic fixture",), Amount.point(Decimal(value)),
                    "submitted", (artifact(period, name, value, decimals),),
                    (Occurrence("https://taxonomy", name, "c", "USD", value,
                                decimals, 4, period.cik, period.annual_end),))


def classification(period=P, name="omit"):
    return Evidence(name, EvidenceKind.CLASSIFICATION, period, "analyst", date(2026, 10, 11),
                    "explicit measurable perimeter omission, not zero",
                    ("reviewed scenario",), None, "not_applicable")


def component(e=None, name="a", treatment=Treatment.REQUIRED, coefficient=1):
    return Component(name, coefficient, treatment, (name,), "explicit treatment", () if e is None else (e,))


def scenario(components=None, period=P):
    return Scenario("explicit-scenario", "1", "narrow", period,
                    components or (component(reported(period=period)),),
                    ("partial perimeter, no complete NWC",),
                    ("acquisitions", "FX", "reclassification", "timing"))


class AnalystNWCTests(unittest.TestCase):
    def test_point_is_partial_not_ready(self):
        result = evaluate(scenario())
        self.assertEqual(result.amount.lower, Decimal(100))
        self.assertEqual(result.status, "partial_perimeter")
        self.assertFalse(result.is_complete_operating_nwc)
        self.assertFalse(result.fcff_ready)

    def test_missing_required_does_not_become_zero(self):
        result = evaluate(scenario((component(reported()), component(name="missing"))))
        self.assertEqual(result.status, "input_unavailable")
        self.assertIsNone(result.amount)
        self.assertIn("unavailable:missing", result.reasons)

    def test_explicit_omission_retained_not_summed(self):
        result = evaluate(scenario((component(reported()), component(classification(), "other", Treatment.OUTSIDE))))
        self.assertEqual(result.amount.lower, Decimal(100))
        self.assertIn("omitted:other", result.reasons)

    def test_omission_needs_provenance(self):
        with self.assertRaises(AnalystNWCError):
            component(None, treatment=Treatment.OUTSIDE)

    def test_conflicting_values_ambiguous(self):
        c = replace(component(reported()), evidence=(reported(), reported("101", name="b")))
        self.assertEqual(evaluate(scenario((c,))).status, "ambiguous_evidence")

    def test_equal_confirmations_preserved(self):
        e = reported()
        e = replace(e, artifacts=(artifact(extra='<t:a contextRef="c" unitRef="USD" decimals="-1">100.0</t:a>'),),
                    occurrences=e.occurrences + (replace(e.occurrences[0], ordinal=5, raw_value="100.0", decimals="-1"),))
        result = evaluate(scenario((component(e),)))
        self.assertEqual(len(result.scenario.components[0].evidence[0].occurrences), 2)
        self.assertEqual(result.amount.lower, Decimal(100))
        self.assertIn("submitted_precision:a", result.reasons)

    def test_rounded_point_is_not_invented_interval(self):
        result = evaluate(scenario((component(reported("3200000000", decimals="-8")),)))
        self.assertEqual(result.amount.lower, result.amount.upper)
        self.assertIn("submitted_precision:a", result.reasons)
        self.assertEqual(deserialize(serialize(result.scenario)), result.scenario)

    def test_invalid_occurrences(self):
        o = reported().occurrences[0]
        for kwargs in ({"nil": True}, {"dimensions": ("segment",)}, {"normalized_unit": "EUR"},
                       {"context_id": ""}, {"raw_value": "NaN"}, {"decimals": "bogus"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AnalystNWCError):
                replace(o, **kwargs)

    def test_raw_value_entity_period_and_concept_mismatch(self):
        e = reported()
        for kwargs in ({"raw_value": "101"}, {"entity_cik": 1}, {"instant_end": date(2025, 6, 29)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AnalystNWCError):
                replace(e, occurrences=(replace(e.occurrences[0], **kwargs),))
        with self.assertRaises(AnalystNWCError):
            replace(e, occurrences=e.occurrences + (replace(e.occurrences[0], ordinal=5, concept="different"),))

    def test_occurrence_order_and_multiplicity(self):
        e = reported()
        for occurrences in ((e.occurrences[0], e.occurrences[0]),
                            (replace(e.occurrences[0], ordinal=5), e.occurrences[0])):
            with self.assertRaises(AnalystNWCError):
                replace(e, occurrences=occurrences)

    def test_artifact_representation_and_digest(self):
        a = artifact()
        for kwargs in ({"body": b"changed"}, {"sha256": "0" * 64},
                       {"representation": "parsed_json"}, {"digest_type": "sha256_json"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AnalystNWCError):
                replace(a, **kwargs)
        with self.assertRaises(AnalystNWCError):
            replace(reported(), artifacts=(replace(a, accession="0000950170-24-087843"),))

    def test_provenance_and_immutability(self):
        e = reported()
        for kwargs in ({"references": ()}, {"author": ""}, {"reviewed_on": "2026-10-11"},
                       {"artifacts": ()}, {"kind": "reported"}, {"coefficients": []}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AnalystNWCError):
                replace(e, **kwargs)
        with self.assertRaises(AttributeError):
            e.author = "mutated"

    def test_period_and_no_amended_approval(self):
        for kwargs in ({"form": "10-K/A"}, {"cik": True}, {"accession": "bad"},
                       {"annual_start": date(2026, 1, 1)}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AnalystNWCError):
                replace(P, **kwargs)

    def test_no_period_extension(self):
        with self.assertRaises(AnalystNWCError):
            replace(scenario(), period=replace(P, accession="0001193125-26-323660"))

    def test_no_overlap(self):
        a = component(reported())
        for b in (replace(a, component_id="b", evidence=(reported(name="b"),)), a):
            with self.assertRaises(AnalystNWCError):
                scenario((a, b))

    def test_no_default_completeness(self):
        with self.assertRaises(AnalystNWCError):
            replace(scenario(), limitations=())
        with self.assertRaises(AnalystNWCError):
            replace(scenario(), unresolved_effects=())

    def test_estimate_requires_assumption_even_for_zero(self):
        with self.assertRaises(AnalystNWCError):
            replace(reported("0"), kind=EvidenceKind.ESTIMATE, occurrences=(), artifacts=())
        e = replace(reported("0"), kind=EvidenceKind.ESTIMATE, occurrences=(), artifacts=(), assumptions=("explicit assumed zero, not reported absence",))
        result = evaluate(scenario((component(e),)))
        self.assertTrue(result.assumption_dependent)
        self.assertEqual(result.amount.lower, Decimal(0))

    def test_manual_external_inputs_remain_labeled(self):
        for kind in (EvidenceKind.MANUAL, EvidenceKind.EXTERNAL):
            e = replace(reported(), kind=kind, occurrences=(), artifacts=(), assumptions=("explicit supplied input",))
            self.assertTrue(evaluate(scenario((component(e),))).assumption_dependent)

    def test_override_retains_original(self):
        old = reported()
        e = replace(reported("90", name="override"), kind=EvidenceKind.ESTIMATE,
                    occurrences=(), artifacts=(), assumptions=("analyst allocation",), supersedes=old)
        s = scenario((replace(component(e), evidence=(old, e)),))
        result = evaluate(s)
        self.assertEqual(result.amount.lower, Decimal(90))
        self.assertTrue(result.assumption_dependent)
        self.assertEqual(deserialize(serialize(s)), s)

    def test_invalid_override(self):
        with self.assertRaises(AnalystNWCError):
            replace(reported(), supersedes=reported(name="other"))

    def test_interval_and_allocation_bound(self):
        e = replace(reported(), kind=EvidenceKind.ESTIMATE, artifacts=(), occurrences=(),
                    value=Amount(Decimal(10), Decimal(20), ("allocation",)), assumptions=("range",))
        c = replace(component(e, coefficient=-1), allocation_ceiling=Decimal(20))
        result = evaluate(scenario((c,)))
        self.assertEqual(result.amount, Amount(Decimal(-20), Decimal(-10), ("allocation",)))
        with self.assertRaises(AnalystNWCError):
            replace(c, allocation_ceiling=Decimal(19))
        with self.assertRaises(AnalystNWCError):
            Amount(Decimal(10), Decimal(20))

    def test_nonfinite_float_or_reversed_amount(self):
        for pair in ((1.0, Decimal(2)), (Decimal('NaN'), Decimal(2)), (Decimal(2), Decimal(1))):
            with self.subTest(pair=pair), self.assertRaises(AnalystNWCError):
                Amount(*pair)

    def test_derivation_reconciles_and_keeps_operands(self):
        a, b = reported("100"), reported("20", name="b")
        e = Evidence("adjusted", EvidenceKind.SEC_DERIVED, P, "reviewer", date(2026, 10, 11),
                     "subtract independently isolated investing balance", ("source note",),
                     Amount.point(Decimal(80)), "submitted", (artifact(),), operands=(a, b), coefficients=(1, -1))
        self.assertEqual(evaluate(scenario((component(e),))).amount.lower, Decimal(80))
        with self.assertRaises(AnalystNWCError):
            replace(e, value=Amount.point(Decimal(81)))
        with self.assertRaises(AnalystNWCError):
            replace(e, coefficients=(1, 0))

    def test_exact_arithmetic_independent_of_decimal_context(self):
        with localcontext() as ctx:
            ctx.prec = 2
            r = evaluate(scenario((component(reported("12345678901234567890.12345")),)))
        self.assertEqual(str(r.amount.lower), "12345678901234567890.12345")

    def test_opening_missing_and_unknown_effects(self):
        r = evaluate(scenario())
        d = change(None, r)
        self.assertEqual(d.status, "opening_unavailable")
        self.assertIsNone(d.amount)
        self.assertIn("FX", d.unresolved_effects)
        self.assertFalse(d.cash_investment_certified)

    def test_change_is_only_book_movement(self):
        q = Period(P.cik, "0001193125-26-323660", date(2025, 7, 1), date(2026, 6, 30))
        a = evaluate(scenario())
        b = evaluate(scenario((component(reported("110", q)),), q))
        d = change(a, b)
        self.assertEqual(d.amount.lower, Decimal(10))
        self.assertEqual(d.status, "partial_book_movement")
        self.assertFalse(d.cash_investment_certified)

    def test_unavailable_input_blocks_change(self):
        q = Period(P.cik, "0001193125-26-323660", date(2025, 7, 1), date(2026, 6, 30))
        self.assertIsNone(change(evaluate(scenario((component(),))), evaluate(scenario(period=q))).amount)

    def test_change_rejects_scope_and_alignment(self):
        a = evaluate(scenario())
        q = Period(P.cik, "0001193125-26-323660", date(2025, 7, 1), date(2026, 6, 30))
        s = scenario(period=q)
        for kwargs in ({"version": "2"}, {"scenario_id": "different"}, {"perimeter_id": "expanded"},
                       {"period": replace(q, annual_start=date(2025, 7, 2))}):
            with self.subTest(kwargs=kwargs), self.assertRaises(AnalystNWCError):
                # Changed period evidence must be explicit too, never implicit extension.
                change(a, evaluate(replace(s, **kwargs)))
        with self.assertRaises(AnalystNWCError):
            change(a, replace(a, fcff_ready=True))

    def test_serialization_revalidates_tampering(self):
        s = scenario()
        self.assertEqual(serialize(deserialize(serialize(s))), serialize(s))
        d = json.loads(serialize(s))
        d['analyst_schema_version'] = '5'
        with self.assertRaises(AnalystNWCError):
            deserialize(json.dumps(d))
        with self.assertRaises(AnalystNWCError):
            deserialize(serialize(s).replace(hashlib.sha256(artifact().body).hexdigest(), '0' * 64))

    def test_verified_bytes_must_actually_contain_the_claimed_fact(self):
        e = reported()
        with self.assertRaises(AnalystNWCError):
            replace(e, artifacts=(artifact(value="999"),))
        with self.assertRaises(AnalystNWCError):
            replace(e, period=replace(P, annual_start=date(2024, 7, 2)))
        for old, new in ((b'contextRef="c"', b'contextRef="broken"'),
                         (b'iso4217:USD', b'iso4217:EUR')):
            a = artifact()
            body = a.body.replace(old, new)
            with self.assertRaises(AnalystNWCError):
                replace(e, artifacts=(replace(a, body=body, sha256=hashlib.sha256(body).hexdigest()),))

    def test_hidden_conflicts_and_duplicates_cannot_be_discarded(self):
        extra = '<t:a contextRef="c" unitRef="USD" decimals="INF">101</t:a>'
        with self.assertRaises(AnalystNWCError):
            replace(reported(), artifacts=(artifact(extra=extra),))
        e = reported()
        e = replace(e, artifacts=(artifact(extra=extra),),
                    competing_occurrences=(replace(e.occurrences[0], ordinal=5, raw_value="101"),))
        result = evaluate(scenario((component(e),)))
        self.assertEqual(result.status, "ambiguous_evidence")
        self.assertIsNone(result.amount)
        self.assertEqual(deserialize_evaluation(serialize_evaluation(result)), result)
        with self.assertRaises(AnalystNWCError):
            replace(reported(), artifacts=(artifact(extra=extra.replace('101', '100')),))

    def test_equivalent_context_and_unit_ids_can_confirm(self):
        e = reported()
        a = artifact()
        extra = ('<xbrli:context id="c2"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">789019</xbrli:identifier></xbrli:entity>'
                 '<xbrli:period><xbrli:instant>2025-06-30</xbrli:instant></xbrli:period></xbrli:context>'
                 '<xbrli:unit id="USD2"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>'
                 '<t:a contextRef="c2" unitRef="USD2" decimals="-1">100.0</t:a>')
        e = replace(e, artifacts=(artifact(extra=extra),), occurrences=e.occurrences + (
            replace(e.occurrences[0], context_id='c2', unit_id='USD2', ordinal=7, raw_value='100.0', decimals='-1'),))
        self.assertEqual(evaluate(scenario((component(e),))).amount.lower, Decimal(100))

    def test_evaluation_roundtrip_recalculates_and_rejects_forged_totals(self):
        result = evaluate(scenario())
        self.assertEqual(deserialize_evaluation(serialize_evaluation(result)), result)
        d = json.loads(serialize_evaluation(result))
        d['evaluation']['fields']['amount']['fields']['lower'] = {'decimal': '999'}
        with self.assertRaises(AnalystNWCError):
            deserialize_evaluation(json.dumps(d))
        d = change(None, result)
        self.assertEqual(deserialize_evaluation(serialize_evaluation(d)), d)

    def test_reversed_period_order_rejected(self):
        q = Period(P.cik, "0001193125-26-323660", date(2025, 7, 1), date(2026, 6, 30))
        with self.assertRaises(AnalystNWCError):
            change(evaluate(scenario(period=q)), evaluate(scenario()))

    def test_shared_interval_dependencies_do_not_invent_covariance(self):
        e = replace(reported(), kind=EvidenceKind.ESTIMATE, artifacts=(), occurrences=(),
                    value=Amount(Decimal(10), Decimal(20), ('shared-assumption',)), assumptions=('range',))
        q = Period(P.cik, "0001193125-26-323660", date(2025, 7, 1), date(2026, 6, 30))
        closing = replace(e, period=q)
        a = evaluate(scenario((component(e),)))
        b = evaluate(scenario((component(closing),), q))
        self.assertEqual(change(a, b).amount, Amount(Decimal(-10), Decimal(10), ('shared-assumption',)))

    def test_nil_source_collision_is_a_data_error(self):
        extra = '<t:a xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" contextRef="c" unitRef="USD" decimals="INF" xsi:nil="true"/>'
        with self.assertRaises(AnalystNWCError):
            replace(reported(), artifacts=(artifact(extra=extra),))

    def test_dimensioned_source_facts_do_not_conflict_with_consolidated_fact(self):
        extra = ('<xbrli:context id="segment"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">789019</xbrli:identifier>'
                 '<xbrli:segment><t:member>business segment</t:member></xbrli:segment></xbrli:entity>'
                 '<xbrli:period><xbrli:instant>2025-06-30</xbrli:instant></xbrli:period></xbrli:context>'
                 '<t:a contextRef="segment" unitRef="USD" decimals="INF">999</t:a>')
        e = replace(reported(), artifacts=(artifact(extra=extra),))
        self.assertEqual(evaluate(scenario((component(e),))).amount.lower, Decimal(100))


class RetainedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads((ROOT / 'docs/analyst-operating-nwc-inventory.json').read_text())
        manifest = json.loads((ROOT / 'docs/evidence/analyst-operating-nwc-response-bodies.json').read_text())
        cls.artifacts = {}
        for a in manifest['artifacts']:
            if a['accession']:
                cls.artifacts[a['source_url']] = Artifact(a['source_url'], a['accession'], a['representation'],
                    a['digest_type'], a['sha256'], gzip.decompress(base64.b64decode(a['response_body_gzip_base64'])))

    def scenario_from_row(self, row, adjusted=False):
        p = Period(row['cik'], row['accession'], date.fromisoformat(row['annual_start']), date.fromisoformat(row['annual_end']))
        components = []
        terms = list(row['reported_driver_subtotal_terms'])
        if adjusted:
            terms.append({'concept': 'PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable', 'coefficient': 1})
        for term in terms:
            name = term['concept']
            fs = [f for f in row['eligible_numeric_occurrences'] if f['concept'] == name and f['context']['start'] is None]
            occurrences = tuple(Occurrence(f['namespace'], name, f['context_id'], f['unit_id'], f['raw_value'],
                f['decimals'], f['occurrence_ordinal'], int(f['context']['entity']), date.fromisoformat(f['context']['end'])) for f in fs)
            e = Evidence(name, EvidenceKind.REPORTED, p, 'retained evidence review', date(2026, 10, 11),
                         'reported selected closing operand; not full perimeter approval', (row['primary_url'],),
                         Amount.point(Decimal(row['reported_component_values_usd'][name])), 'submitted',
                         (self.artifacts[row['instance_url']],), occurrences)
            components.append(component(e, name, coefficient=term['coefficient']))
        return Scenario('explicit-adjusted' if adjusted else 'reported-driver', '1', row['ticker']+'-narrow', p,
                        tuple(components), ('omitted mixed captions and unproved completeness',),
                        ('acquisition', 'FX', 'reclassification', 'timing'))

    def test_all_fifteen_reported_driver_sums_and_twelve_changes(self):
        previous = {}
        for row in self.inventory['rows']:
            with self.subTest(row=row['accession']):
                result = evaluate(self.scenario_from_row(row))
                self.assertEqual(result.amount.lower, Decimal(row['reported_driver_subtotal_usd']))
                d = change(previous.get(row['ticker']), result)
                expected = row['adjacent_reported_driver_subtotal_change_usd']
                self.assertEqual(d.amount.lower if d.amount else None, Decimal(expected) if expected else None)
                self.assertFalse(d.cash_investment_certified)
                previous[row['ticker']] = result

    def test_msft_19_8bn_effect_only_two_supported_periods(self):
        rows = [r for r in self.inventory['rows'] if r['ticker'] == 'MSFT']
        raw = [evaluate(self.scenario_from_row(r)) for r in rows[-2:]]
        adjusted = [evaluate(self.scenario_from_row(r, True)) for r in rows[-2:]]
        self.assertEqual(change(*raw).amount.lower, Decimal('-12908000000'))
        self.assertEqual(change(*adjusted).amount.lower, Decimal('6892000000'))
        self.assertEqual(change(*adjusted).amount.lower - change(*raw).amount.lower, Decimal('19800000000'))
        for r in adjusted:
            self.assertFalse(r.fcff_ready)
            self.assertFalse(r.is_complete_operating_nwc)
        for row in rows[:3]:
            self.assertIsNone(row['reported_component_values_usd']['PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable'])

    def test_frozen_validation_and_output_schema_untouched(self):
        p = ROOT / 'docs/universe/phase-1h5-issuer-validation.json'
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), '1d7b538fa757eef51ef1fcc9edeb42a9fef3cebdd8882a9caf7abd822b6ab089')
        from valuation_platform.normalization.output import SCHEMA_VERSION
        from valuation_platform.normalization.operating_nwc import OPERATING_NWC_VALUATION_POLICIES
        self.assertEqual(SCHEMA_VERSION, '5')
        self.assertEqual(len(OPERATING_NWC_VALUATION_POLICIES), 5)

    def test_register_exact_forty_mapping_and_seventeen_measures(self):
        matrix = json.loads((ROOT / 'docs/universe/phase-1h5-issuer-validation.json').read_text())
        expected = {r['execution_ticker'] for r in matrix['rows'] if r['classification'] == 'GENERALIZATION_REQUIRED'}
        files = {p.stem: p for p in (ROOT / 'docs/company-data-preparation').glob('*.md') if p.stem != 'index'}
        self.assertEqual(set(files), expected)
        self.assertEqual(len(files), 40)
        for path in files.values():
            self.assertEqual(sum(line.startswith('| `') for line in path.read_text().splitlines()), 17)
        self.assertNotIn('GOOG', files)


if __name__ == '__main__':
    unittest.main()
