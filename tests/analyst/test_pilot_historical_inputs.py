"""Exact pilot adapters; no source/field expansion or economic treatment."""

import copy
from dataclasses import replace
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from valuation_platform.analyst import historical_inputs as h
from valuation_platform.analyst import pilot_historical_inputs as p

ROOT = Path(__file__).resolve().parents[2]


class PilotAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads(p.MAPPING_PATH.read_bytes())
        cls.histories = {key: p.load_history(key) for key in ('MSFT', 'AAPL', 'GOOGL')}
        cls.payloads = {key: p.serialize(value) for key, value in cls.histories.items()}

    def row(self, annual):
        return next(r for r in self.mapping['periods'] if annual.bundle_id == 'pilot-preparation:' + r['bundle_id'])

    def reject_payload(self, issuer, mutation):
        doc = json.loads(self.payloads[issuer])
        mutation(doc)
        with self.assertRaises(h.InputError):
            p.deserialize(json.dumps(doc))

    def test_four_exact_periods_and_immutable_model_types(self):
        self.assertEqual([len(b.annuals) for b in self.histories.values()], [2, 1, 1])
        for history in self.histories.values():
            self.assertIs(type(history), h.HistoryBundle)
            self.assertTrue(history.history_exceptions)
            for annual in history.annuals:
                self.assertIs(type(annual), h.AnnualBundle)
                self.assertEqual(annual.period, p.first_period(self.row(annual)))
                self.assertEqual({v.field for v in annual.inputs}, set(h.Field))
        for bad in ('GOOG', 'GE', 'META', 'msft', None):
            with self.assertRaises(h.InputError):
                p.load_history(bad)
        for bad in ('msft-reported-cash-flow-fy2024', 'googl-reported-cash-flow-fy2023', 'AAPL'):
            with self.assertRaises(h.InputError):
                p.load_annual(bad)

    def test_all_bindings_roles_statuses_precision_requirements_reproduced(self):
        for history in self.histories.values():
            for annual in history.annuals:
                row = self.row(annual)
                for field in h.Field:
                    entry = row['fields'][field.value]
                    values = tuple(v for v in annual.inputs if v.field is field)
                    observations = values[0].alternatives if entry['status'] == 'limited_support' else values
                    if not entry['bindings']:
                        self.assertEqual(len(values), 1)
                        self.assertIsNone(values[0].value)
                        continue
                    self.assertEqual(len(observations), len(entry['bindings']))
                    for value, bind in zip(observations, entry['bindings']):
                        self.assertEqual(value.role, bind['role'])
                        self.assertEqual(value.origin.value, bind['origin'])
                        self.assertEqual(value.scope_status.value, entry['scope'])
                        self.assertEqual(value.quality.value, entry['quality'])
                        self.assertEqual(value.completeness.value, entry['completeness'])
                        self.assertEqual(value.review.value, entry['review'])
                        self.assertEqual((value.scale, value.sign, value.precision),
                                         (bind['scale'], bind['sign'], bind['precision']))
                        self.assertEqual(value.coverage_keys, (bind['population'],))
                        self.assertEqual(value.unresolved_requirements, tuple(entry['unresolved_requirements']))

    def test_support_only_da_never_populates_required_value(self):
        for history in self.histories.values():
            for annual in history.annuals:
                da = next(v for v in annual.inputs if v.field is h.Field.DA)
                self.assertIsNone(da.value)
                self.assertEqual(da.origin, h.Origin.UNAVAILABLE)
                self.assertEqual(da.completeness, h.Completeness.PARTIAL)
                self.assertTrue(da.null_reason)
                self.assertTrue(da.alternatives)
                for support in da.alternatives:
                    self.assertIsNotNone(support.value)
                    self.assertEqual(support.origin, h.Origin.REPORTED)
                    self.assertIn('support_only', support.flags)
                    self.assertIn('non_substitutable_for_required_da_primitive', support.flags)
                    self.assertNotEqual(support.completeness, h.Completeness.COMPLETE)

    def test_unavailable_fields_explicit_no_zero_or_invented_share_date(self):
        for history in self.histories.values():
            for annual in history.annuals:
                row = self.row(annual)
                nulls = [v for v in annual.inputs if v.value is None]
                self.assertEqual(len(nulls), 7 if row['issuer'] == 'AAPL' else 6)
                for v in nulls:
                    self.assertTrue(v.null_reason)
                    self.assertEqual(v.unresolved_requirements, tuple(row['fields'][v.field.value]['unresolved_requirements']))
                    self.assertIn(v.field, annual.unresolved_required_fields)
                shares = next(v for v in annual.inputs if v.field is h.Field.SHARES)
                self.assertIsNone(shares.as_of)
                for v in annual.inputs:
                    if v.field in (h.Field.CASH_INVESTMENTS, h.Field.DEBT_LEASES, h.Field.OTHER_BRIDGE):
                        self.assertEqual(v.as_of, annual.period.annual_end)

    def test_raw_sign_scale_and_full_receipt_binding(self):
        for history in self.histories.values():
            for annual in history.annuals:
                _, _, loader = p._SOURCES[self.row(annual)['bundle_id']]
                source = loader(self.row(annual)['bundle_id'])
                observed = [v for v in annual.inputs if v.value is not None]
                observed += list(next(v for v in annual.inputs if v.field is h.Field.DA).alternatives)
                for value in observed:
                    original_id = value.input_id.split(':', 1)[1]
                    if value.field in p.direct.POLICIES:
                        reviewed = p.direct.reviewed(source, value.field)
                        item = reviewed.candidates[reviewed.selected]
                    else:
                        item = source.input(original_id)
                    self.assertEqual(value.value, item.displayed_value_usd)
                    self.assertEqual(value.scope, item.location_and_scope)
                    refs = [s for s in value.sources if s.occurrence_ordinal is not None]
                    self.assertEqual(len(refs), len(item.occurrences))
                    for ref, occurrence in zip(refs, item.occurrences):
                        self.assertEqual(ref.raw_value, occurrence.raw_value)
                        self.assertEqual(ref.context_id, occurrence.context_id)
                        self.assertEqual((ref.namespace, ref.concept, ref.decimals, ref.dimensions),
                            (occurrence.namespace, occurrence.concept, occurrence.decimals, occurrence.dimensions))
                        self.assertIn(ref.receipt, source.artifacts)
                        locator = json.loads(ref.locator)
                        self.assertEqual(locator['unit_id'], occurrence.unit_id)
                        self.assertIs(locator['nil'], False)
                        self.assertEqual(locator['mapping_sha256'], p.MAPPING_SHA256)
                    with localcontext() as ctx:
                        ctx.prec = 3
                        self.assertEqual(value.value, item.displayed_value_usd)

    def test_expense_vs_addback_and_rounded_alphabet_values(self):
        for issuer, history in self.histories.items():
            for annual in history.annuals:
                sbc = {v.role: v for v in annual.inputs if v.field is h.Field.SBC}
                self.assertEqual(set(sbc), {'sbc_cfo_addback', 'sbc_note_expense'})
                self.assertEqual(sbc['sbc_cfo_addback'].coverage_keys, sbc['sbc_note_expense'].coverage_keys)
                self.assertNotEqual(sbc['sbc_cfo_addback'].flags, sbc['sbc_note_expense'].flags)
                if issuer == 'GOOGL':
                    self.assertEqual((sbc['sbc_note_expense'].value, sbc['sbc_note_expense'].precision),
                                     (Decimal('22800000000'), '-8'))
                    self.assertEqual((sbc['sbc_cfo_addback'].value, sbc['sbc_cfo_addback'].precision),
                                     (Decimal('22785000000'), '-6'))

    def test_no_totals_residuals_derivations_or_manual_entries(self):
        for history in self.histories.values():
            for annual in history.annuals:
                for v in annual.inputs:
                    self.assertIsNone(v.formula)
                    self.assertIsNone(v.manual)
                    self.assertIn(v.origin, (h.Origin.REPORTED, h.Origin.UNAVAILABLE))
                    self.assertIn('no_aggregation_or_valuation_authorization', v.flags)
                    if v.field is h.Field.CFO_RESIDUAL:
                        self.assertIsNone(v.value)
                        self.assertEqual(v.alternatives, ())

    def test_deterministic_serialization_and_exact_roundtrips(self):
        for issuer, history in self.histories.items():
            restored = p.deserialize(self.payloads[issuer])
            self.assertEqual(restored, history)
            self.assertEqual(p.serialize(restored), self.payloads[issuer])
            self.assertEqual(restored.annuals[0].inputs, history.annuals[0].inputs)

    def test_body_once_in_native_proofs_and_original_metadata_history(self):
        for issuer, text in self.payloads.items():
            doc = json.loads(text)
            self.assertEqual(doc['model_schema'], h.SCHEMA)
            self.assertNotIn('"bytes":', json.dumps(doc['history']))
            for proof in doc['source_proofs']:
                old = json.loads(proof['payload'])
                self.assertEqual(len(old['artifacts']), 2)
                for artifact in old['artifacts']:
                    self.assertEqual(artifact['digest_type'], 'sha256_sec_response_body_bytes')
                if issuer == 'GOOGL':
                    self.assertIsNone(old['evidence_history']['original_instance']['retrieved_at_utc'])
                    self.assertIsNone(old['evidence_history']['original_instance']['http_status'])

    def test_tampered_roles_nulls_precision_and_types_rejected(self):
        for key, value in (('role', 'complete_da'), ('null_reason', None), ('unresolved_requirements', []),
                           ('origin', {'enum': 'Origin', 'value': 'reported'})):
            self.reject_payload('GOOGL', lambda d, k=key, v=value:
                d['history']['fields']['annuals'][0]['fields']['inputs'][2]['fields'].__setitem__(k, v))
        for key, value in (('scale', True), ('sign', 1.0), ('precision', 'INF')):
            self.reject_payload('GOOGL', lambda d, k=key, v=value:
                d['history']['fields']['annuals'][0]['fields']['inputs'][3]['fields'].__setitem__(k, v))

    def test_mismatched_context_or_unit_binding_cannot_serialize(self):
        history = self.histories['GOOGL']
        annual = history.annuals[0]
        value = next(v for v in annual.inputs if v.field is h.Field.CAPEX)
        ref = value.sources[0]
        changed_ref = replace(ref, context_id='different-context')
        changed = replace(value, sources=(changed_ref,))
        bad = replace(history, annuals=(replace(annual, inputs=tuple(changed if v.input_id == value.input_id else v for v in annual.inputs)),))
        with self.assertRaises(h.InputError):
            p.serialize(bad)

    def test_source_receipt_or_body_tampering_rejected(self):
        def change(d):
            source = json.loads(d['source_proofs'][0]['payload'])
            source['artifacts'][1]['retrieved_at_utc'] = '2026-10-12T00:00:00Z'
            d['source_proofs'][0]['payload'] = json.dumps(source)
        self.reject_payload('GOOGL', change)
        self.reject_payload('AAPL', lambda d: d['source_proofs'][0].__setitem__('bundle_id', 'aapl-reported-cash-flow-fy2024'))

    def test_alternate_mapping_bytes_fail_closed(self):
        class BadPath:
            def read_bytes(self):
                return b'{}'
        with patch.object(p, 'MAPPING_PATH', BadPath()), self.assertRaises(h.InputError):
            p.load_history('AAPL')
        self.reject_payload('AAPL', lambda d: d.__setitem__('mapping_sha256', '0' * 64))

    def test_original_serializers_and_mapping_bytes_preserved(self):
        self.assertEqual(hashlib.sha256(p.MAPPING_PATH.read_bytes()).hexdigest(), p.MAPPING_SHA256)
        for issuer, text in self.payloads.items():
            for proof in json.loads(text)['source_proofs']:
                _, module, loader = p._SOURCES[proof['bundle_id']]
                self.assertEqual(proof['payload'], module.serialize(loader(proof['bundle_id'])))

    def test_unknowns_supplementary_refs_and_limits_survive(self):
        for history in self.histories.values():
            for annual in history.annuals:
                row = self.row(annual)
                _, _, loader = p._SOURCES[row['bundle_id']]
                old = loader(row['bundle_id'])
                for limitation in old.limitations:
                    self.assertIn(limitation, annual.limitations)
                unknowns = [json.loads(s.split(':', 1)[1]) for s in annual.limitations if s.startswith('reported_input_unknown:')]
                self.assertEqual({u['input_id'] for u in unknowns}, {u.input_id for u in old.unknowns})
                self.assertTrue(all(u['value_usd'] is None for u in unknowns))


if __name__ == '__main__':
    unittest.main()
