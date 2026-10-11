"""Reviewed input bundles materialized into existing pure models; no retrieval.

This adapter is a reproducibility test, not a production registry/default loader.
The JSON carries explicit inputs and references original bodies without copying
the retained manifest. Runtime scenario serialization remains self-contained.
"""
import base64
import copy
from dataclasses import replace
from datetime import date
from decimal import Decimal
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from valuation_platform.analyst.nwc import (
    Amount, AnalystNWCError, Artifact, Component, Evidence, EvidenceKind,
    Occurrence, Period, Scenario, Treatment, change, evaluate,
    serialize, deserialize,
)

ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PATH = ROOT / 'docs/company-data-preparation/msft-analyst-nwc-bundles.json'
PPE = 'PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable'


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, text):
        self.parts.append(text)


def materialize(document, bundle, *, comparison=False):
    """Bind explicit reviewed inputs, then use only existing analyst models."""
    if document['bundle_contract'] != 'reviewed-msft-partial-nwc-inputs' or document['version'] != '1':
        raise AnalystNWCError('Unknown reviewed bundle contract')
    for key in ('inventory', 'artifact_manifest'):
        if hashlib.sha256((ROOT / document[key + '_path']).read_bytes()).hexdigest() != document[key + '_sha256']:
            raise AnalystNWCError('Referenced evidence file changed')
    inventory = json.loads((ROOT / document['inventory_path']).read_text())
    rows = [r for r in inventory['rows'] if r['ticker'] == 'MSFT' and r['annual_end'] in ('2025-06-30', '2026-06-30')]
    identity = bundle['period']
    row = next((r for r in rows if all(r[k] == v for k, v in identity.items())), None)
    if row is None or set(identity) != {'cik', 'accession', 'annual_start', 'annual_end'}:
        raise AnalystNWCError('Not an exact reviewed frozen identity')
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
        raise AnalystNWCError('Both exact statement and instance artifacts required')
    primary = next(a for a in artifacts if a.url == row['primary_url'])
    text = VisibleText()
    text.feed(primary.body.decode())
    if bundle['note_assertion'] not in re.sub(r'\s+', ' ', ' '.join(text.parts)):
        raise AnalystNWCError('Reviewed Note 6 assertion not retained')
    root = ET.fromstring(next(a.body for a in artifacts if a.url == row['instance_url']))
    forms = {f.text for f in root if f.tag.startswith('{http://xbrl.sec.gov/dei/') and f.tag.endswith('}DocumentType')}
    if forms != {'10-K'}:
        raise AnalystNWCError('Selected source is not a non-amended 10-K')
    terms = row['reported_driver_subtotal_terms'] + [{'concept': PPE, 'coefficient': 1}]
    if [(t['component_id'], t['coefficient']) for t in bundle['operands']] != [
            (t['concept'], t['coefficient']) for t in terms]:
        raise AnalystNWCError('Missing, reordered or changed reviewed equation')
    components = []
    for term in bundle['operands']:
        name = term['component_id']
        expected = [f for f in row['eligible_numeric_occurrences'] if f['concept'] == name and f['context']['start'] is None]
        if (term['occurrences'] != expected or term['value_usd'] != row['reported_component_values_usd'][name]
                or term['evidence_kind'] != 'reported' or term['treatment'] != 'required'):
            raise AnalystNWCError('Operand differs from exact retained selected occurrences')
        if comparison and name == PPE:
            continue
        occurrences = tuple(Occurrence(f['namespace'], name, f['context_id'], f['unit_id'], f['raw_value'],
            f['decimals'], f['occurrence_ordinal'], int(f['context']['entity']), date.fromisoformat(f['context']['end'])) for f in expected)
        e = Evidence(name, EvidenceKind.REPORTED, p, document['review_author'],
                     date.fromisoformat(document['reviewed_on']), term['rationale'],
                     (bundle['primary_url'], 'docs/company-data-preparation/MSFT.md'),
                     Amount.point(Decimal(term['value_usd'])), 'submitted', tuple(artifacts), occurrences)
        components.append(Component(name, term['coefficient'], Treatment.REQUIRED,
                                    tuple(term['scope_keys']), term['rationale'], (e,)))
    for omission in document['omissions']:
        e = Evidence('omit:' + omission['component_id'], EvidenceKind.CLASSIFICATION, p,
                     document['review_author'], date.fromisoformat(document['reviewed_on']),
                     omission['rationale'], (bundle['primary_url'], 'docs/analyst-operating-nwc-design.md'),
                     None, 'not_an_amount', (primary,))
        components.append(Component(omission['component_id'], 1, Treatment.OUTSIDE,
                                    tuple(omission['scope_keys']), omission['rationale'], (e,)))
    prefix = 'comparison_' if comparison else ''
    return Scenario(document[prefix + 'scenario_id'], document['version'], document[prefix + 'perimeter_id'],
                    p, tuple(components), tuple(document['limitations']), tuple(document['unresolved_effects']))


class MSFTBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(BUNDLE_PATH.read_text())
        cls.scenarios = [materialize(cls.document, b) for b in cls.document['bundles']]
        cls.comparisons = [materialize(cls.document, b, comparison=True) for b in cls.document['bundles']]

    def test_two_exact_frozen_bundles_and_twelve_occurrences(self):
        self.assertEqual([s.period.accession for s in self.scenarios],
                         ['0000950170-25-100235', '0001193125-26-323660'])
        self.assertEqual(sum(len(e.occurrences) for s in self.scenarios for c in s.components for e in c.evidence), 12)
        for s, b in zip(self.scenarios, self.document['bundles']):
            result = evaluate(s)
            self.assertEqual(result.amount.lower, Decimal(b['expected_adjusted_partial_usd']))
            ap = next(c.evidence[0].value.lower for c in s.components if c.component_id == 'AccountsPayableCurrent')
            ppe = next(c.evidence[0].value.lower for c in s.components if c.component_id == PPE)
            self.assertEqual(ap - ppe, Decimal(b['expected_adjusted_ap_usd']))

    def test_whole_ap_comparison_and_19_8bn_effect(self):
        for s, b in zip(self.comparisons, self.document['bundles']):
            self.assertEqual(evaluate(s).amount.lower, Decimal(b['expected_whole_ap_usd']))
        raw = change(*(evaluate(s) for s in self.comparisons))
        adjusted = change(*(evaluate(s) for s in self.scenarios))
        expected = self.document['expected_movement_usd']
        self.assertEqual(raw.amount.lower, Decimal(expected['whole_ap']))
        self.assertEqual(adjusted.amount.lower, Decimal(expected['adjusted_partial']))
        self.assertEqual(adjusted.amount.lower - raw.amount.lower, Decimal(expected['ppe_ap_exclusion_effect']))
        self.assertFalse(adjusted.cash_investment_certified)
        self.assertEqual(adjusted.unresolved_effects, tuple(sorted(self.document['unresolved_effects'])))

    def test_omissions_are_explicit_classifications_not_estimated_zeros(self):
        for s in self.scenarios:
            result = evaluate(s)
            self.assertEqual(result.status, 'partial_perimeter')
            self.assertFalse(result.fcff_ready)
            self.assertFalse(result.is_complete_operating_nwc)
            self.assertFalse(result.assumption_dependent)  # No numerical estimates, not no scope judgment.
            for c in s.components:
                if c.treatment is Treatment.OUTSIDE:
                    self.assertIn('omitted:' + c.component_id, result.reasons)
                    self.assertEqual(c.evidence[0].kind, EvidenceKind.CLASSIFICATION)
                    self.assertIsNone(c.evidence[0].value)
        for key in ('estimates', 'manual_inputs', 'external_inputs'):
            self.assertEqual(self.document[key], [])

    def test_rounded_points_and_exact_raw_representations_survive_serialization(self):
        s = self.scenarios[0]
        restored = deserialize(serialize(s))
        self.assertEqual(restored, s)
        self.assertEqual(evaluate(restored), evaluate(s))
        ppe = next(c.evidence[0] for c in restored.components if c.component_id == PPE)
        self.assertEqual(ppe.occurrences[0].decimals, '-8')
        self.assertEqual(ppe.occurrences[0].raw_value, '6900000000')
        self.assertIn('submitted_precision:' + PPE, evaluate(restored).reasons)
        self.assertEqual(ppe.value.lower, ppe.value.upper)  # No fabricated rounding interval.

    def test_unknown_required_allocation_cannot_be_omitted_silently(self):
        s = self.scenarios[0]
        cs = tuple(replace(c, treatment=Treatment.REQUIRED, evidence=())
                   if c.component_id == 'mixed_other_current_assets' else c for c in s.components)
        result = evaluate(replace(s, components=cs))
        self.assertEqual(result.status, 'input_unavailable')
        self.assertIsNone(result.amount)
        closing = self.scenarios[1]
        closing_components = tuple(replace(c, treatment=Treatment.REQUIRED, evidence=())
                                   if c.component_id == 'mixed_other_current_assets' else c for c in closing.components)
        self.assertIsNone(change(result, evaluate(replace(closing, components=closing_components))).amount)

    def test_no_earlier_future_or_amended_identity_extension(self):
        for year in ('2024', '2027'):
            b = copy.deepcopy(self.document['bundles'][0])
            b['period']['annual_end'] = year + '-06-30'
            with self.assertRaises(AnalystNWCError):
                materialize(self.document, b)
        b = copy.deepcopy(self.document['bundles'][0])
        b['form'] = '10-K/A'
        with self.assertRaises(AnalystNWCError):
            materialize(self.document, b)

    def test_changed_identity_digest_occurrence_or_equation_rejects(self):
        for mutation in ('cik', 'digest', 'ordinal', 'value', 'missing_operand'):
            b = copy.deepcopy(self.document['bundles'][0])
            if mutation == 'cik': b['period']['cik'] = 320193
            elif mutation == 'digest': b['artifacts'][0]['sha256'] = '0' * 64
            elif mutation == 'ordinal': b['operands'][0]['occurrences'][0]['occurrence_ordinal'] += 1
            elif mutation == 'value': b['operands'][0]['value_usd'] = '0'
            else: b['operands'].pop()
            with self.subTest(mutation=mutation), self.assertRaises(AnalystNWCError):
                materialize(self.document, b)

    def test_incompatible_comparison_and_adjusted_perimeters_do_not_mix(self):
        with self.assertRaises(AnalystNWCError):
            change(evaluate(self.comparisons[0]), evaluate(self.scenarios[1]))
        first = change(None, evaluate(self.scenarios[0]))
        self.assertEqual(first.status, 'opening_unavailable')
        self.assertIsNone(first.amount)


if __name__ == '__main__':
    unittest.main()
