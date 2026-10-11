"""Reviewed one-level inputs, including a duration-tagged rounded note.

Test-only source binding/adapter, not a new historical parser or policy. The
existing pure evaluator receives an explicitly labeled manual note input; no
instant observation is fabricated from a duration fact.
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
BUNDLE_PATH = ROOT / 'docs/company-data-preparation/googl-analyst-nwc-bundle.json'
ASSERTION = ('Additional property and equipment purchases of $ 2.8 billion and $ 3.2 billion '
             'as of December 31, 2023 and 2024, respectively, were included in accounts payable.')


def verify_note(note, root, primary, visible, period):
    """Independently bind the actual duration occurrence and explicit closing note."""
    xi = '{http://www.xbrl.org/2003/instance}'
    source = note['source_occurrence']
    if (source['concept'] != 'CapitalExpendituresIncurredButNotYetPaid'
            or source['namespace'] != 'http://fasb.org/us-gaap/2024'
            or note['closing_basis'] != period.annual_end.isoformat()
            or note['precision'] != 'rounded' or note['evidence_kind'] != 'manual_input'
            or note['scope_assertion'] != ASSERTION or ASSERTION not in visible
            or note['coefficient'] != 1 or note['displayed_unit'] != 'USD billion'):
        raise AnalystNWCError('Only the reviewed rounded closing note is accepted')
    fact = root[source['occurrence_ordinal']]
    contexts = {c.attrib['id']: c for c in root.findall(xi + 'context')}
    c = contexts[fact.attrib['contextRef']]
    expected_context = {'entity': c.findtext('.//' + xi + 'identifier'),
                        'start': c.findtext(xi + 'period/' + xi + 'startDate'),
                        'end': c.findtext(xi + 'period/' + xi + 'endDate'), 'dimensions': []}
    if (fact.tag != '{' + source['namespace'] + '}' + source['concept']
            or c.find('.//' + xi + 'segment') is not None or c.find('.//' + xi + 'scenario') is not None
            or expected_context != source['context']
            or int(expected_context['entity']) != period.cik
            or expected_context['start'] != period.annual_start.isoformat()
            or expected_context['end'] != period.annual_end.isoformat()
            or fact.attrib['contextRef'] != source['context_id']
            or fact.attrib['unitRef'] != source['unit_id'] or fact.text != source['raw_value']
            or fact.attrib.get('decimals') != source['decimals'] or source['decimals'] != '-8'
            or fact.attrib.get('id') != source['source_fact_id']
            or fact.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}nil', 'false') != source['nil']):
        raise AnalystNWCError('Rounded note source identity/precision mismatch')
    unit = next(u for u in root.findall(xi + 'unit') if u.attrib['id'] == source['unit_id'])
    if (source['unit'] != ['iso4217:USD'] or len(unit) != 1
            or unit[0].tag != xi + 'measure' or unit[0].text != 'iso4217:USD' or source['nil'] != 'false'):
        raise AnalystNWCError('Rounded note unit/nil mismatch')
    selected = []
    for i, candidate in enumerate(root):
        if candidate.tag != fact.tag:
            continue
        context = contexts[candidate.attrib['contextRef']]
        if (int(context.findtext('.//' + xi + 'identifier')) == period.cik
                and context.findtext(xi + 'period/' + xi + 'startDate') == period.annual_start.isoformat()
                and context.findtext(xi + 'period/' + xi + 'endDate') == period.annual_end.isoformat()
                and context.find('.//' + xi + 'segment') is None and context.find('.//' + xi + 'scenario') is None):
            selected.append(i)
    if selected != [source['occurrence_ordinal']]:
        raise AnalystNWCError('Additional source occurrences require a new review')
    inline = next(f for f in ET.fromstring(primary.body).iter() if f.attrib.get('id') == source['source_fact_id'])
    if (not inline.tag.endswith('}nonFraction') or inline.attrib.get('name') != 'us-gaap:' + source['concept']
            or inline.attrib.get('contextRef') != source['context_id']
            or inline.attrib.get('unitRef') != source['unit_id']
            or inline.attrib.get('decimals') != source['decimals']
            or inline.attrib.get('scale') != note['inline_scale'] or inline.text != note['displayed_value']
            or Decimal(inline.text) * Decimal(10) ** int(note['inline_scale']) != Decimal(source['raw_value'])
            or Decimal(note['value_usd']) != Decimal(source['raw_value'])):
        raise AnalystNWCError('Displayed/instance rounded representations disagree')


def materialize(document):
    if document['bundle_contract'] != 'reviewed-googl-fy2024-partial-nwc-input' or document['version'] != '1':
        raise AnalystNWCError('Unknown reviewed bundle contract')
    for key in ('inventory', 'artifact_manifest'):
        if hashlib.sha256((ROOT / document[key + '_path']).read_bytes()).hexdigest() != document[key + '_sha256']:
            raise AnalystNWCError('Referenced evidence changed')
    row = next(r for r in json.loads((ROOT / document['inventory_path']).read_text())['rows']
               if r['ticker'] == 'GOOGL' and r['annual_end'] == '2024-12-31')
    b = document['bundle']
    if b['period'] != {k: row[k] for k in ('cik', 'accession', 'annual_start', 'annual_end')}:
        raise AnalystNWCError('Not the exact reviewed frozen FY2024 identity')
    p = Period(row['cik'], row['accession'], date.fromisoformat(row['annual_start']),
               date.fromisoformat(row['annual_end']), b['form'])
    manifest = json.loads((ROOT / document['artifact_manifest_path']).read_text())
    artifacts = []
    for ref in b['artifacts']:
        a = next(a for a in manifest['artifacts'] if a['source_url'] == ref['source_url'])
        if any(a[k] != v for k, v in ref.items()):
            raise AnalystNWCError('Artifact metadata mismatch')
        body = gzip.decompress(base64.b64decode(a['response_body_gzip_base64']))
        if len(body) != ref['byte_length']:
            raise AnalystNWCError('Body length mismatch')
        artifacts.append(Artifact(ref['source_url'], ref['accession'], ref['representation'], ref['digest_type'], ref['sha256'], body))
    if {a.url for a in artifacts} != {row['primary_url'], row['instance_url']} or (
            b['primary_url'], b['instance_url']) != (row['primary_url'], row['instance_url']):
        raise AnalystNWCError('Both exact statement and instance required')
    primary = next(a for a in artifacts if a.url == row['primary_url'])
    root = ET.fromstring(next(a.body for a in artifacts if a.url == row['instance_url']))
    forms = {f.text for f in root if f.tag.startswith('{http://xbrl.sec.gov/dei/') and f.tag.endswith('}DocumentType')}
    if forms != {'10-K'}:
        raise AnalystNWCError('Source is not a non-amended 10-K')
    text = VisibleText()
    text.feed(primary.body.decode())
    visible = re.sub(r'\s+', ' ', ' '.join(text.parts))
    if not b['note_assertions'] or any(a not in visible for a in b['note_assertions']):
        raise AnalystNWCError('Reviewed source assertions missing')
    if [(t['component_id'], t['coefficient']) for t in b['operands']] != [
            (t['concept'], t['coefficient']) for t in row['reported_driver_subtotal_terms']]:
        raise AnalystNWCError('Changed narrow equation')
    if {o['component_id'] for o in document['omissions']} != {
            'inventory', 'other_current_assets', 'separate_accrued_ppe', 'remaining_accrued_liabilities',
            'unidentified_supplier_scope', 'cash_investments_funding_tax_leases_noncurrent'}:
        raise AnalystNWCError('Reviewed omissions must remain explicit')

    def reported(term):
        name = term['component_id']
        expected = [f for f in row['eligible_numeric_occurrences'] if f['concept'] == name and f['context']['start'] is None]
        if (term['occurrences'] != expected or term['value_usd'] != row['reported_component_values_usd'][name]
                or term['evidence_kind'] != 'reported'):
            raise AnalystNWCError('Operand differs from selected retained occurrences')
        occurrences = tuple(Occurrence(f['namespace'], name, f['context_id'], f['unit_id'], f['raw_value'],
            f['decimals'], f['occurrence_ordinal'], int(f['context']['entity']), date.fromisoformat(f['context']['end'])) for f in expected)
        return Evidence(name, EvidenceKind.REPORTED, p, document['review_author'], date.fromisoformat(document['reviewed_on']),
                        term['rationale'], (b['primary_url'], 'docs/company-data-preparation/GOOGL.md'),
                        Amount.point(Decimal(term['value_usd'])), 'submitted', tuple(artifacts), occurrences)

    components = [Component(t['component_id'], t['coefficient'], Treatment.REQUIRED, tuple(t['scope_keys']),
                            t['rationale'], (reported(t),)) for t in b['operands']]
    note = b['rounded_note_input']
    verify_note(note, root, primary, visible, p)
    provenance = ('source_occurrence_json:' + json.dumps(note['source_occurrence'], sort_keys=True),
                  'inline_representation_json:' + json.dumps({k: note[k] for k in (
                      'displayed_value', 'displayed_unit', 'inline_scale', 'closing_basis', 'scope_assertion')}, sort_keys=True))
    e = Evidence(note['component_id'], EvidenceKind.MANUAL, p, document['review_author'],
                 date.fromisoformat(document['reviewed_on']), note['rationale'],
                 (b['primary_url'], b['instance_url'], 'docs/company-data-preparation/googl-analyst-nwc-bundle.json') + provenance,
                 Amount.point(Decimal(note['value_usd'])), note['precision'], tuple(artifacts),
                 assumptions=tuple(note['assumptions']))
    components.append(Component(note['component_id'], note['coefficient'], Treatment.REQUIRED,
                                tuple(note['scope_keys']), note['rationale'], (e,)))
    for omission in document['omissions']:
        e = Evidence('omit:' + omission['component_id'], EvidenceKind.CLASSIFICATION, p, document['review_author'],
                     date.fromisoformat(document['reviewed_on']), omission['rationale'],
                     (b['primary_url'], 'docs/analyst-operating-nwc-design.md'), None, 'not_an_amount', (primary,))
        if omission['component_id'] == 'separate_accrued_ppe' and 'reported_evidence' not in omission:
            raise AnalystNWCError('Separate accrued PP&E evidence must remain retained')
        evidence = (e, reported(omission['reported_evidence'])) if 'reported_evidence' in omission else (e,)
        components.append(Component(omission['component_id'], omission['coefficient'], Treatment.OUTSIDE,
                                    tuple(omission['scope_keys']), omission['rationale'], evidence))
    return Scenario(document['scenario_id'], document['version'], document['perimeter_id'], p, tuple(components),
                    tuple(document['limitations']), tuple(document['unresolved_effects']))


class GOOGLBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(BUNDLE_PATH.read_text())
        cls.scenario = materialize(cls.document)

    def test_exact_identity_equation_and_rounded_partial_result(self):
        s = self.scenario
        self.assertEqual(s.period, Period(1652044, '0001652044-25-000014', date(2024, 1, 1), date(2024, 12, 31)))
        result = evaluate(s)
        self.assertEqual(result.status, 'partial_perimeter')
        self.assertEqual(result.amount.lower, Decimal('13342000000'))
        self.assertEqual(result.amount.lower, Decimal(self.document['bundle']['expected_partial_usd']))
        ap = next(c.evidence[0].value.lower for c in s.components if c.component_id == 'AccountsPayableCurrent')
        self.assertEqual(ap - Decimal('3200000000'), Decimal(self.document['bundle']['expected_ap_after_known_exclusion_usd']))
        self.assertFalse(result.is_complete_operating_nwc)
        self.assertFalse(result.fcff_ready)

    def test_duration_note_is_labeled_manual_rounded_not_fabricated_instant(self):
        e = next(c.evidence[0] for c in self.scenario.components if c.component_id == 'reviewed_ppe_in_ap_note')
        self.assertEqual(e.kind, EvidenceKind.MANUAL)
        self.assertEqual(e.precision, 'rounded')
        self.assertEqual(e.occurrences, ())
        self.assertTrue(e.assumptions)
        self.assertTrue(evaluate(self.scenario).assumption_dependent)
        self.assertIn('submitted_precision:reviewed_ppe_in_ap_note', evaluate(self.scenario).reasons)
        source = json.loads(next(r.split(':', 1)[1] for r in e.references if r.startswith('source_occurrence_json:')))
        self.assertEqual(source['context']['start'], '2024-01-01')
        self.assertEqual(source['decimals'], '-8')
        self.assertEqual(source['occurrence_ordinal'], 1459)

    def test_inventory_and_remaining_supplier_scope_stay_unknown(self):
        for name in ('inventory', 'unidentified_supplier_scope'):
            c = next(c for c in self.scenario.components if c.component_id == name)
            self.assertIsNone(c.evidence[0].value)
            expanded = replace(self.scenario, components=tuple(
                replace(c, treatment=Treatment.REQUIRED) if c.component_id == name else c for c in self.scenario.components))
            self.assertEqual(evaluate(expanded).status, 'input_unavailable')
            self.assertIsNone(evaluate(expanded).amount)
        self.assertEqual(self.document['estimates'], [])
        self.assertEqual(self.document['manual_inputs'], ['reviewed_ppe_in_ap_note'])

    def test_separate_accrued_ppe_is_not_the_ap_correction(self):
        c = next(c for c in self.scenario.components if c.component_id == 'separate_accrued_ppe')
        self.assertEqual(c.treatment, Treatment.OUTSIDE)
        self.assertEqual(c.evidence[1].value.lower, Decimal('7104000000'))
        core = [c for c in self.scenario.components if c.treatment is Treatment.REQUIRED and c.component_id != 'reviewed_ppe_in_ap_note']
        self.assertEqual(sum(c.coefficient * c.evidence[0].value.lower for c in core), Decimal('10142000000'))
        self.assertNotIn('AccruedLiabilitiesCurrent', [c.component_id for c in core])

    def test_serialization_preserves_note_metadata_precision_omissions_and_evaluation(self):
        restored = deserialize(serialize(self.scenario))
        self.assertEqual(restored, self.scenario)
        result = evaluate(restored)
        self.assertEqual(deserialize_evaluation(serialize_evaluation(result)), result)
        self.assertEqual(result.amount.lower, result.amount.upper)  # Reported point, not invented economic interval.
        self.assertEqual(sum(r.startswith('submitted_precision:') for r in result.reasons), 7)

    def test_no_opening_level_delta_or_cash_certification(self):
        delta = change(None, evaluate(self.scenario))
        self.assertEqual(delta.status, 'opening_unavailable')
        self.assertIsNone(delta.amount)
        self.assertFalse(delta.cash_investment_certified)
        self.assertEqual(delta.unresolved_effects, tuple(self.document['unresolved_effects']))

    def test_other_periods_comparatives_amendments_and_identities_reject(self):
        for field, value in (('annual_end', '2023-12-31'), ('annual_end', '2025-12-31'),
                             ('annual_start', '2024-01-02'), ('cik', 320193), ('accession', '0001652044-26-000018')):
            d = copy.deepcopy(self.document)
            d['bundle']['period'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(AnalystNWCError):
                materialize(d)
        d = copy.deepcopy(self.document)
        d['bundle']['form'] = '10-K/A'
        with self.assertRaises(AnalystNWCError):
            materialize(d)

    def test_note_value_precision_context_scope_and_tag_changes_reject(self):
        for mutation in ('value', 'precision', 'instant', 'concept', 'decimals', 'ordinal', 'scope', 'unit', 'nil'):
            d = copy.deepcopy(self.document)
            n = d['bundle']['rounded_note_input']
            if mutation == 'value': n['value_usd'] = '2800000000'
            elif mutation == 'precision': n['precision'] = 'exact'
            elif mutation == 'instant': n['source_occurrence']['context']['start'] = None
            elif mutation == 'concept': n['source_occurrence']['concept'] = 'AccruedPurchasesOfPropertyAndEquipmentCurrent'
            elif mutation == 'decimals': n['source_occurrence']['decimals'] = 'INF'
            elif mutation == 'ordinal': n['source_occurrence']['occurrence_ordinal'] = 1458
            elif mutation == 'scope': n['scope_assertion'] = 'Invented closing-balance scope'
            elif mutation == 'unit': n['source_occurrence']['unit'] = ['iso4217:EUR']
            else: n['source_occurrence']['nil'] = 'true'
            with self.subTest(mutation=mutation), self.assertRaises(AnalystNWCError):
                materialize(d)

    def test_evidence_failures_omitted_inputs_and_changed_core_reject(self):
        for mutation in ('digest', 'representation', 'context', 'raw', 'missing_operand', 'missing_omission', 'missing_separate_ppe'):
            d = copy.deepcopy(self.document)
            b = d['bundle']
            if mutation == 'digest': b['artifacts'][0]['sha256'] = '0' * 64
            elif mutation == 'representation': b['artifacts'][0]['representation'] = 'parsed_text'
            elif mutation == 'context': b['operands'][0]['occurrences'][0]['context_id'] = 'c-1'
            elif mutation == 'raw': b['operands'][0]['occurrences'][0]['raw_value'] = '0'
            elif mutation == 'missing_operand': b['operands'].pop()
            elif mutation == 'missing_omission': d['omissions'].pop()
            else: del next(o for o in d['omissions'] if o['component_id'] == 'separate_accrued_ppe')['reported_evidence']
            with self.subTest(mutation=mutation), self.assertRaises(AnalystNWCError):
                materialize(d)


if __name__ == '__main__':
    unittest.main()
