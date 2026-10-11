"""One explicit retained-evidence AAPL level; never a default or NWC policy.

The adapter is test-only input reproducibility, following the MSFT convention.
Existing production scenario/evaluation/serialization models remain unchanged.
"""
import base64
import copy
from dataclasses import replace
from datetime import date
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from valuation_platform.analyst.nwc import (
    Amount, AnalystNWCError, Artifact, Component, Evidence, EvidenceKind,
    Occurrence, Period, Scenario, Treatment, change, evaluate, serialize,
    deserialize, serialize_evaluation, deserialize_evaluation,
)
from tests.analyst.test_msft_bundles import VisibleText

ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = ROOT / 'docs/company-data-preparation/aapl-analyst-nwc-bundle.json'


def materialize(document):
    """Construct existing models from the explicitly reviewed one-period input."""
    if document['bundle_contract'] != 'reviewed-aapl-fy2025-partial-nwc-input' or document['version'] != '1':
        raise AnalystNWCError('Unknown reviewed bundle contract')
    for key in ('inventory', 'artifact_manifest'):
        path = ROOT / document[key + '_path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != document[key + '_sha256']:
            raise AnalystNWCError('Referenced evidence changed')
    inventory = json.loads((ROOT / document['inventory_path']).read_text())
    row = next(r for r in inventory['rows'] if r['ticker'] == 'AAPL' and r['annual_end'] == '2025-09-27')
    bundle = document['bundle']
    identity = bundle['period']
    if identity != {k: row[k] for k in ('cik', 'accession', 'annual_start', 'annual_end')}:
        raise AnalystNWCError('Not the exact reviewed frozen FY2025 identity')
    p = Period(identity['cik'], identity['accession'], date.fromisoformat(identity['annual_start']),
               date.fromisoformat(identity['annual_end']), bundle['form'])
    manifest = json.loads((ROOT / document['artifact_manifest_path']).read_text())
    artifacts = []
    for ref in bundle['artifacts']:
        source = next(a for a in manifest['artifacts'] if a['source_url'] == ref['source_url'])
        if any(source[k] != v for k, v in ref.items()):
            raise AnalystNWCError('Artifact metadata mismatch')
        body = gzip.decompress(base64.b64decode(source['response_body_gzip_base64']))
        if len(body) != ref['byte_length']:
            raise AnalystNWCError('Body length mismatch')
        artifacts.append(Artifact(ref['source_url'], ref['accession'], ref['representation'],
                                  ref['digest_type'], ref['sha256'], body))
    if {a.url for a in artifacts} != {row['primary_url'], row['instance_url']} or (
            bundle['primary_url'], bundle['instance_url']) != (row['primary_url'], row['instance_url']):
        raise AnalystNWCError('Both exact retained statement and instance required')
    primary = next(a for a in artifacts if a.url == row['primary_url'])
    text = VisibleText()
    text.feed(primary.body.decode())
    visible = re.sub(r'\s+', ' ', ' '.join(text.parts))
    if not bundle['note_assertions'] or any(a not in visible for a in bundle['note_assertions']):
        raise AnalystNWCError('Reviewed scope assertions not retained')
    root = ET.fromstring(next(a.body for a in artifacts if a.url == row['instance_url']))
    forms = {f.text for f in root if f.tag.startswith('{http://xbrl.sec.gov/dei/') and f.tag.endswith('}DocumentType')}
    if forms != {'10-K'}:
        raise AnalystNWCError('Source is not a non-amended 10-K')
    if [(t['component_id'], t['coefficient']) for t in bundle['operands']] != [
            (t['concept'], t['coefficient']) for t in row['reported_driver_subtotal_terms']]:
        raise AnalystNWCError('Missing, reordered or changed narrow equation')
    if {o['component_id'] for o in document['omissions']} != {
            'employee_accruals', 'distribution_marketing', 'investing_in_ap_correction',
            'mixed_other_current_assets', 'remaining_other_current_liabilities',
            'cash_investments_funding_and_income_taxes', 'leases_and_noncurrent_balances'}:
        raise AnalystNWCError('Reviewed omissions must remain explicit')
    distribution = next(o for o in document['omissions'] if o['component_id'] == 'distribution_marketing')
    if 'reported_evidence' not in distribution:
        raise AnalystNWCError('Known omitted distribution fact must be retained')

    def reported(term):
        name = term['component_id']
        expected = [f for f in row['eligible_numeric_occurrences'] if f['concept'] == name and f['context']['start'] is None]
        if (term['occurrences'] != expected or term['value_usd'] != row['reported_component_values_usd'][name]
                or term['evidence_kind'] != 'reported'):
            raise AnalystNWCError('Operand differs from exact selected retained occurrences')
        occurrences = tuple(Occurrence(f['namespace'], name, f['context_id'], f['unit_id'], f['raw_value'],
            f['decimals'], f['occurrence_ordinal'], int(f['context']['entity']), date.fromisoformat(f['context']['end'])) for f in expected)
        return Evidence(name, EvidenceKind.REPORTED, p, document['review_author'],
                        date.fromisoformat(document['reviewed_on']), term['rationale'],
                        (bundle['primary_url'], 'docs/company-data-preparation/AAPL.md'),
                        Amount.point(Decimal(term['value_usd'])), 'submitted', tuple(artifacts), occurrences)

    components = [Component(t['component_id'], t['coefficient'], Treatment.REQUIRED,
                            tuple(t['scope_keys']), t['rationale'], (reported(t),)) for t in bundle['operands']]
    for omission in document['omissions']:
        e = Evidence('omit:' + omission['component_id'], EvidenceKind.CLASSIFICATION, p,
                     document['review_author'], date.fromisoformat(document['reviewed_on']),
                     omission['rationale'], (bundle['primary_url'], 'docs/analyst-operating-nwc-design.md'),
                     None, 'not_an_amount', (primary,))
        evidence = (e, reported(omission['reported_evidence'])) if 'reported_evidence' in omission else (e,)
        components.append(Component(omission['component_id'], omission['coefficient'], Treatment.OUTSIDE,
                                    tuple(omission['scope_keys']), omission['rationale'], evidence))
    return Scenario(document['scenario_id'], document['version'], document['perimeter_id'], p,
                    tuple(components), tuple(document['limitations']), tuple(document['unresolved_effects']))


class AAPLBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(BUNDLE_PATH.read_text())
        cls.scenario = materialize(cls.document)

    def test_exact_identity_operands_and_partial_sum(self):
        s = self.scenario
        self.assertEqual(s.period, Period(320193, '0000320193-25-000079', date(2024, 9, 29), date(2025, 9, 27)))
        result = evaluate(s)
        self.assertEqual(result.status, 'partial_perimeter')
        self.assertEqual(result.amount, Amount.point(Decimal('-240000000')))
        self.assertEqual(str(result.amount.lower), self.document['bundle']['expected_partial_usd'])
        self.assertFalse(result.is_complete_operating_nwc)
        self.assertFalse(result.fcff_ready)
        self.assertFalse(result.assumption_dependent)  # Scope judgments remain; no numerical estimates.
        observations = [o for c in s.components for e in c.evidence for o in e.occurrences]
        self.assertEqual(len(observations), 6)  # Five included and one explicitly omitted known fact.
        self.assertEqual([o.ordinal for o in observations], [370, 372, 374, 390, 394, 880])
        self.assertTrue(all(o.decimals == '-6' and o.context_id == 'c-20' for o in observations))

    def test_known_distribution_retained_but_not_subtracted(self):
        c = next(c for c in self.scenario.components if c.component_id == 'distribution_marketing')
        self.assertEqual(c.treatment, Treatment.OUTSIDE)
        self.assertEqual(c.evidence[0].kind, EvidenceKind.CLASSIFICATION)
        self.assertEqual(c.evidence[1].kind, EvidenceKind.REPORTED)
        self.assertEqual(c.evidence[1].value.lower, Decimal('8919000000'))
        self.assertEqual(c.evidence[1].occurrences[0].namespace, 'http://www.apple.com/20250927')
        self.assertIn('omitted:distribution_marketing', evaluate(self.scenario).reasons)
        self.assertNotEqual(evaluate(self.scenario).amount.lower, Decimal('-9159000000'))

    def test_unknown_employee_and_ap_allocations_are_not_zero_estimates(self):
        for name in ('employee_accruals', 'investing_in_ap_correction'):
            c = next(c for c in self.scenario.components if c.component_id == name)
            self.assertIsNone(c.evidence[0].value)
            self.assertEqual(c.evidence[0].kind, EvidenceKind.CLASSIFICATION)
            expanded = replace(self.scenario, components=tuple(
                replace(x, treatment=Treatment.REQUIRED) if x.component_id == name else x for x in self.scenario.components))
            result = evaluate(expanded)
            self.assertEqual(result.status, 'input_unavailable')
            self.assertIsNone(result.amount)
        for key in ('estimates', 'manual_inputs', 'external_inputs'):
            self.assertEqual(self.document[key], [])

    def test_one_level_has_no_delta_or_cash_certification(self):
        delta = change(None, evaluate(self.scenario))
        self.assertEqual(delta.status, self.document['bundle']['expected_change_status'])
        self.assertIsNone(delta.amount)
        self.assertIsNone(self.document['bundle']['opening_bundle'])
        self.assertIsNone(self.document['bundle']['expected_change_usd'])
        self.assertFalse(delta.cash_investment_certified)
        self.assertEqual(delta.unresolved_effects, tuple(self.document['unresolved_effects']))

    def test_scenario_and_evaluation_serialization_reverify_sources_and_omissions(self):
        restored = deserialize(serialize(self.scenario))
        self.assertEqual(restored, self.scenario)
        result = evaluate(restored)
        self.assertEqual(deserialize_evaluation(serialize_evaluation(result)), result)
        self.assertEqual(sum(reason.startswith('submitted_precision:') for reason in result.reasons), 5)
        self.assertEqual(result.amount.lower, result.amount.upper)  # No invented rounding interval.
        known = next(c for c in restored.components if c.component_id == 'distribution_marketing')
        self.assertEqual(known.evidence[1].occurrences[0].raw_value, '8919000000')

    def test_no_earlier_future_amended_or_foreign_issuer_extension(self):
        for field, value in (('annual_end', '2024-09-28'), ('annual_end', '2026-09-26'),
                             ('annual_start', '2024-09-30'), ('cik', 789019),
                             ('accession', '0000320193-24-000123')):
            d = copy.deepcopy(self.document)
            d['bundle']['period'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(AnalystNWCError):
                materialize(d)
        d = copy.deepcopy(self.document)
        d['bundle']['form'] = '10-K/A'
        with self.assertRaises(AnalystNWCError):
            materialize(d)

    def test_provenance_representation_and_occurrence_tampering_reject(self):
        for mutation in ('digest', 'representation', 'context', 'ordinal', 'dimension', 'unit', 'nil', 'value', 'missing_operand'):
            d = copy.deepcopy(self.document)
            b = d['bundle']
            if mutation == 'digest': b['artifacts'][0]['sha256'] = '0' * 64
            elif mutation == 'representation': b['artifacts'][0]['representation'] = 'parsed_text'
            elif mutation == 'context': b['operands'][0]['occurrences'][0]['context_id'] = 'c-21'
            elif mutation == 'ordinal': b['operands'][0]['occurrences'][0]['occurrence_ordinal'] += 1
            elif mutation == 'dimension': b['operands'][0]['occurrences'][0]['context']['dimensions'] = ['segment']
            elif mutation == 'unit': b['operands'][0]['occurrences'][0]['unit'] = ['iso4217:EUR']
            elif mutation == 'nil': b['operands'][0]['occurrences'][0]['nil'] = 'true'
            elif mutation == 'value': b['operands'][0]['value_usd'] = '0'
            else: b['operands'].pop()
            with self.subTest(mutation=mutation), self.assertRaises(AnalystNWCError):
                materialize(d)

    def test_source_assertions_and_known_omitted_evidence_are_mandatory(self):
        d = copy.deepcopy(self.document)
        d['bundle']['note_assertions'][0] = 'Unsupported scope assertion'
        with self.assertRaises(AnalystNWCError):
            materialize(d)
        d = copy.deepcopy(self.document)
        omitted = next(o for o in d['omissions'] if o['component_id'] == 'distribution_marketing')
        del omitted['reported_evidence']
        with self.assertRaises(AnalystNWCError):
            materialize(d)
        d = copy.deepcopy(self.document)
        d['omissions'] = [o for o in d['omissions'] if o['component_id'] != 'employee_accruals']
        with self.assertRaises(AnalystNWCError):
            materialize(d)
        d = copy.deepcopy(self.document)
        omitted = next(o for o in d['omissions'] if o['component_id'] == 'distribution_marketing')
        omitted['reported_evidence']['value_usd'] = '7679000000'  # Later filing's prior-year comparative is not current.
        with self.assertRaises(AnalystNWCError):
            materialize(d)


if __name__ == '__main__':
    unittest.main()
