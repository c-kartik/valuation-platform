"""Exact nonnumeric sidecars; no interest sum, zero allocation or certification."""

import copy
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from valuation_platform.analyst import cash_flow_inputs as cf
from valuation_platform.analyst import cash_interest_annotations as ca


ROOT = Path(__file__).resolve().parents[2]


class CashInterestAnnotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids = ca.registered_annotation_ids()
        cls.parents = tuple(cf.load_msft_bundle(i) for i in cf.registered_bundle_ids())
        cls.sidecars = tuple(ca.load_msft_annotations(i, b) for i, b in zip(cls.ids, cls.parents))
        cls.payloads = tuple(ca.serialize(a) for a in cls.sidecars)

    def test_exact_two_v1_registrations(self):
        self.assertEqual(self.ids, ('msft-cash-interest-scope-fy2025', 'msft-cash-interest-scope-fy2026'))
        for a, b in zip(self.sidecars, self.parents):
            self.assertEqual(a.version, '1')
            self.assertIs(a.parent, b)
            self.assertEqual(a.parent.period.cik, 789019)
            self.assertEqual(a.parent.period.form, '10-K')
            self.assertEqual(a.parent.period.annual_start, date(a.parent.period.annual_end.year - 1, 7, 1))
        for identity in ('MSFT', 'msft-cash-interest-scope-fy2024', 'msft-cash-interest-scope-fy2027'):
            with self.subTest(identity=identity), self.assertRaises(ca.AnnotationError):
                ca.load_msft_annotations(identity, self.parents[0])

    def test_all_22_input_snapshots_and_ordered_occurrences(self):
        for a in self.sidecars:
            self.assertEqual(len(a.annotations), 11)
            self.assertEqual(len({v.assertion_id for v in a.annotations}), 11)
            for v in a.annotations:
                self.assertEqual(v.subject.kind, 'reported_input')
                self.assertEqual(v.binding, a.parent.input(v.subject.identity))
                self.assertEqual(v.instance, a.parent.artifacts[1])
                self.assertEqual(v.state, ca.AssertionState.SUPPORTED)
                self.assertTrue(v.rationale)
                self.assertTrue(v.evidence_ids)
                self.assertEqual(v.binding.occurrences, a.parent.input(v.subject.identity).occurrences)

    def test_20_granular_unknowns_preserve_parent_unknown(self):
        for a in self.sidecars:
            self.assertEqual(len(a.unknowns), 10)
            self.assertEqual(len({u.issue_id for u in a.unknowns}), 10)
            self.assertIsNone(next(u for u in a.parent.unknowns if u.input_id == 'all_in_cash_interest').value_usd)
            for u in a.unknowns:
                self.assertIsNone(u.value_usd)
                self.assertEqual(u.subject, ca.Subject('bundle_unknown', 'all_in_cash_interest'))
                self.assertNotEqual(u.state, ca.AssertionState.SUPPORTED)
                self.assertTrue(u.affected_subjects)
                self.assertTrue(u.reopening_requirement)
                with self.assertRaises(ca.AnnotationError):
                    replace(u, value_usd=Decimal(0))
        self.assertEqual(self.sidecars[0].unknowns, self.sidecars[1].unknowns)

    def test_reported_rounding_and_cash_accrual_noncash_roles(self):
        for a in self.sidecars:
            bound = {v.binding.input_id: v.binding for v in a.annotations}
            self.assertEqual(bound['InterestPaid'].occurrences[0].decimals, '-8')
            self.assertEqual(bound['FinanceLeaseInterestPaymentOnLiability'].occurrences[0].decimals, '-6')
            self.assertEqual(bound['InterestPaid'].kind, cf.InputKind.CASH_PAYMENT)
            self.assertEqual(bound['InterestPaid'].display_multiplier, -1)
            self.assertEqual(bound['InterestExpenseNonoperating'].kind, cf.InputKind.ACCRUED_EXPENSE)
            self.assertEqual(bound['FinanceLeaseRightOfUseAssetAmortization'].kind, cf.InputKind.NONCASH_EXPENSE)
            self.assertEqual(bound['RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability'].kind,
                             cf.InputKind.NONCASH_ADDITION)
            self.assertFalse(hasattr(a, 'interest_total'))
            self.assertFalse(hasattr(a, 'adjusted_subtotal'))

    def test_equal_fy2026_cash_cost_still_different_bases_and_unknown_overlap(self):
        a = self.sidecars[1]
        self.assertEqual(a.parent.input('FinanceLeaseInterestExpense').value_usd,
                         a.parent.input('FinanceLeaseInterestPaymentOnLiability').value_usd)
        self.assertIn('different_recognition_bases', [r.claim for r in a.relations])
        self.assertIn('overlap_unquantified', [r.claim for r in a.relations])
        self.assertIn('lease_effect_evidenced_full_allocation_unknown', [r.claim for r in a.relations])
        self.assertFalse(a.summation_authorized)

    def test_14_note_and_item7_locators_bind_original_bodies(self):
        for a in self.sidecars:
            self.assertEqual(len(a.evidence), 7)
            for e in a.evidence:
                self.assertEqual(e.primary, a.parent.artifacts[0])
                t = ca._text(e.primary.artifact.body)
                self.assertEqual(t[e.primary_offset:e.primary_offset + len(e.locator)], e.locator)
                self.assertEqual(e.primary.artifact.digest_type, 'sha256_sec_response_body_bytes')
            mda = next(e for e in a.evidence if e.evidence_id == 'aggregate_expense_effects')
            self.assertIn('capitalization of debt interest expense', mda.locator)
            self.assertIn('finance lease interest expense', mda.locator)

    def test_four_tax_occurrences_are_research_not_parent_inputs_or_cash(self):
        for a in self.sidecars:
            self.assertEqual(len(a.research), 2)
            for e in a.research:
                self.assertEqual(e.subject.kind, 'research_only')
                self.assertEqual(e.occurrence.decimals, '-8')
                self.assertNotIn(e.subject.identity, [i.input_id for i in a.parent.inputs])
                self.assertEqual(e.occurrence.end, a.parent.period.annual_end)
            self.assertEqual(a.research[0].occurrence.start, a.parent.period.annual_start)
            self.assertIsNone(a.research[1].occurrence.start)

    def test_separate_serialization_exact_roundtrip_no_copied_bodies(self):
        for a, payload in zip(self.sidecars, self.payloads):
            restored = ca.deserialize(payload, a.parent)
            self.assertEqual(restored, a)
            self.assertEqual(ca.serialize(restored), payload)
            self.assertEqual(json.loads(payload)['schema'], 'cash-interest-scope-annotations-v1')
            self.assertNotIn('response_body_gzip_base64', payload)
            self.assertNotIn('registry_digest_placeholder', payload.lower())
            self.assertNotIn('reported-cash-flow-input-bundle-v1', payload)

    def test_detached_payload_and_wrong_parent_cannot_validate(self):
        with self.assertRaises(ca.AnnotationError):
            ca.deserialize(self.payloads[0], None)
        with self.assertRaises(ca.AnnotationError):
            ca.deserialize(self.payloads[0], self.parents[1])

    def test_missing_annotation_is_not_provided_not_default(self):
        result = ca.attach((), self.parents[0])
        self.assertEqual(result.state, ca.AttachmentState.NOT_PROVIDED)
        self.assertIsNone(result.annotations)
        self.assertFalse(self.parents[0].valuation_consumption_approved)

    def test_valid_attachment_explicit_opt_in(self):
        result = ca.attach((self.payloads[0],), self.parents[0])
        self.assertEqual(result.state, ca.AttachmentState.VALIDATED)
        self.assertEqual(result.annotations, self.sidecars[0])

    def test_malformed_attachment_fails_without_partial_acceptance(self):
        for payloads in ([], ('broken JSON',), ('null',), ('[]',), ('{}',), (True,)):
            with self.subTest(payloads=payloads):
                result = ca.attach(payloads, self.parents[0])
                self.assertEqual(result.state, ca.AttachmentState.INVALID)
                self.assertIsNone(result.annotations)
                self.assertTrue(result.reasons)

    def test_multiple_versions_conflict_without_last_write_wins(self):
        newer = json.loads(self.payloads[0]); newer['annotations']['version'] = '2'
        for payloads in ((self.payloads[0], json.dumps(newer)),
                         (json.dumps(newer), self.payloads[0]), self.payloads):
            result = ca.attach(payloads, self.parents[0])
            self.assertEqual(result.state, ca.AttachmentState.CONFLICTING)
            self.assertIsNone(result.annotations)
            self.assertEqual(len(result.identities), 2)
            self.assertTrue(result.reasons)

    def test_contradictory_assertions_conflict_with_diagnostics(self):
        d = json.loads(self.payloads[0]);v = d['annotations']
        altered = copy.deepcopy(v['annotations'][0]);altered['claim'] = 'all_in_cash_interest'
        v['annotations'].append(altered)
        result = ca.attach((json.dumps(d),), self.parents[0])
        self.assertEqual(result.state, ca.AttachmentState.CONFLICTING)
        self.assertIsNone(result.annotations)
        self.assertTrue(result.identities)

    def test_duplicate_json_keys_and_nonfinite_numeric_extras_reject(self):
        for payload in (self.payloads[0].replace('"schema":', '"schema":"bad","schema":', 1),
                        self.payloads[0][:-1] + ',"estimated_interest":NaN}'):
            with self.assertRaises(ca.AnnotationError):
                ca.deserialize(payload, self.parents[0])

    def test_closed_binding_precision_and_conservative_unknown_schema(self):
        mutations = {
            'parent_version': lambda v: v['parent'].__setitem__('version', '2'),
            'amended': lambda v: v['parent']['period'].__setitem__('form', '10-K/A'),
            'future': lambda v: v['parent']['period'].__setitem__('annual_end', '2027-06-30'),
            'cik': lambda v: v['parent']['period'].__setitem__('cik', 1),
            'registry': lambda v: v['parent'].__setitem__('registry_sha256', '0'*64),
            'amount': lambda v: v['annotations'][0]['binding'].__setitem__('value_usd', '0'),
            'kind': lambda v: v['annotations'][0]['binding'].__setitem__('kind', 'accrued_expense'),
            'sign': lambda v: v['annotations'][0]['binding'].__setitem__('display_multiplier', 1),
            'scope': lambda v: v['annotations'][0].__setitem__('rationale', 'certified total'),
            'missing_input': lambda v: v['annotations'].pop(),
            'missing_unknown': lambda v: v['unknowns'].pop(),
            'unknown_zero': lambda v: v['unknowns'][0].__setitem__('value_usd', '0'),
            'unknown_resolved': lambda v: v['unknowns'][0].__setitem__('state', 'evidence_supported'),
            'dangling_subject': lambda v: v['unknowns'][0]['subject'].__setitem__('identity', 'new'),
            'relation_sum': lambda v: v['relations'][0].__setitem__('operator', '+'),
            'tax_as_input': lambda v: v['research'][0]['subject'].__setitem__('kind', 'reported_input'),
            'numeric_total': lambda v: v.__setitem__('interest_total', '2972000000'),
            'missing_evidence': lambda v: v['evidence'].pop(),
            'extra': lambda v: v.__setitem__('external_estimate', '1'),
        }
        for key, mutate in mutations.items():
            d = json.loads(self.payloads[0]);mutate(d['annotations'])
            with self.subTest(key=key), self.assertRaises(ca.AnnotationError):
                ca.deserialize(json.dumps(d), self.parents[0])

    def test_occurrence_identity_representation_and_precision_tampering_rejects(self):
        fields = {'namespace':'wrong', 'concept':'InterestExpenseNonoperating', 'entity_cik':1,
                  'context_id':'broken', 'start':'2024-07-02', 'end':'2026-06-30',
                  'dimensions':['Axis=Member'], 'unit_id':'other', 'normalized_unit':'EUR',
                  'raw_value':'1600000000.0', 'decimals':'INF', 'nil':True, 'ordinal':1644}
        for key, value in fields.items():
            d=json.loads(self.payloads[0]);d['annotations']['annotations'][0]['binding']['occurrences'][0][key]=value
            with self.subTest(key=key), self.assertRaises(ca.AnnotationError):
                ca.deserialize(json.dumps(d), self.parents[0])
        d=json.loads(self.payloads[0]);d['annotations']['annotations'][0]['binding']['occurrences']=[]
        with self.assertRaises(ca.AnnotationError):
            ca.deserialize(json.dumps(d), self.parents[0])

    def test_source_locator_artifact_metadata_and_representation_tampering_rejects(self):
        for change in ('offset','locator','block','context','digest','representation','time','length','extraction'):
            d=json.loads(self.payloads[0]);v=d['annotations'];e=v['evidence'][0]
            if change=='offset':e['primary_offset']+=1
            elif change=='locator':e['locator']='a matching amount is sufficient'
            elif change=='block':e['text_block_ordinal']+=1
            elif change=='context':e['text_block_context']='broken'
            elif change=='extraction':e['extraction_version']='rendered-text-v2'
            elif change=='digest':v['parent']['artifacts'][0]['sha256']='0'*64
            elif change=='representation':v['parent']['artifacts'][0]['representation']='parsed_html'
            elif change=='time':v['parent']['artifacts'][0]['retrieved_at_utc']='2026-10-12T00:00:00+00:00'
            else:v['parent']['artifacts'][0]['byte_length']=1
            with self.subTest(change=change), self.assertRaises(ca.AnnotationError):
                ca.deserialize(json.dumps(d),self.parents[0])

    def test_actual_original_body_change_cannot_be_relabelled_or_implicitly_refreshed(self):
        b=self.parents[0];r=b.artifacts[0];body=r.artifact.body+b' '
        artifact=replace(r.artifact,body=body,sha256=hashlib.sha256(body).hexdigest())
        receipt=replace(r,artifact=artifact,byte_length=len(body))
        altered=replace(b,artifacts=(receipt,b.artifacts[1]))
        with self.assertRaises(ca.AnnotationError):
            ca.load_msft_annotations(self.ids[0],altered)

    def test_public_immutable_models_cannot_accept_changes_as_valid_sidecars(self):
        a=self.sidecars[0]
        with self.assertRaises(FrozenInstanceError):a.version='2'
        with self.assertRaises(ca.AnnotationError):replace(a,annotations=list(a.annotations))
        with self.assertRaises(ca.AnnotationError):replace(a.annotations[0],evidence_ids=['debt_cash'])
        with self.assertRaises(ca.AnnotationError):replace(a.unknowns[0],affected_subjects=list(a.unknowns[0].affected_subjects))
        with self.assertRaises(ca.AnnotationError):replace(a,unknowns=a.unknowns[:-1])
        with self.assertRaises(ca.AnnotationConflict):replace(a,annotations=a.annotations+(a.annotations[0],))
        for change in ({'locator':'unverified'}, {'primary_offset':a.evidence[0].primary_offset+1},
                       {'text_block_ordinal':a.evidence[0].text_block_ordinal+1}):
            with self.subTest(change=change), self.assertRaises(ca.AnnotationError):
                replace(a,evidence=(replace(a.evidence[0],**change),)+a.evidence[1:])

    def test_no_certification_flag_or_bool_integer_coercion(self):
        for flag in ('certified_interest_total','summation_authorized','valuation_consumption_approved','is_complete_operating_nwc'):
            for value in (True,0):
                with self.subTest(flag=flag,value=value), self.assertRaises(ca.AnnotationError):
                    replace(self.sidecars[0],**{flag:value})
                d=json.loads(self.payloads[0]);d['annotations'][flag]=value
                with self.assertRaises(ca.AnnotationError):ca.deserialize(json.dumps(d),self.parents[0])

    def test_registry_identity_pinned(self):
        self.assertEqual(hashlib.sha256(ca._REGISTRY_PATH.read_bytes()).hexdigest(),ca._REGISTRY_SHA256)
        with patch.object(ca,'_REGISTRY_SHA256','0'*64), self.assertRaises(ca.AnnotationError):
            ca.registered_annotation_ids()

    def test_forged_parent_types_and_identity_reject_without_modifying_original(self):
        for change in ('input_type', 'version', 'accession'):
            parent = copy.copy(self.parents[0])
            if change == 'input_type':
                item = copy.copy(parent.inputs[0])
                object.__setattr__(item, 'value_usd', int(item.value_usd))
                object.__setattr__(parent, 'inputs', (item,) + parent.inputs[1:])
            elif change == 'version':
                object.__setattr__(parent, 'version', '2')
            else:
                period = copy.copy(parent.period)
                object.__setattr__(period, 'accession', '0000950170-25-100236')
                object.__setattr__(parent, 'period', period)
            with self.subTest(change=change), self.assertRaises(ca.AnnotationError):
                ca.load_msft_annotations(self.ids[0], parent)
        self.assertEqual(self.parents[0].version, '1')

    def test_parent_serialized_bytes_and_original_evidence_preserved(self):
        # Recorded before any implementation edit, using the untouched v1 serializer.
        hashes=('1d8f27c0f40d31cb31e2f592013416189b1c92b5d68f45fcd98d9e0456aacfad',
                '2dc19075d695bac0fe4755732f70cafbab7dd5b0e055b77c857f949e0cfd08ba')
        for parent,payload,expected in zip(self.parents,self.payloads,hashes):
            self.assertEqual(hashlib.sha256(cf.serialize(parent).encode()).hexdigest(),expected)
            ca.deserialize(payload,parent)
            self.assertEqual(hashlib.sha256(cf.serialize(parent).encode()).hexdigest(),expected)
            for r in parent.artifacts:
                self.assertEqual(hashlib.sha256(r.artifact.body).hexdigest(),r.artifact.sha256)
            self.assertFalse(parent.is_complete_operating_nwc)
            self.assertFalse(parent.valuation_consumption_approved)
        self.assertEqual(hashlib.sha256(cf._REGISTRY_PATH.read_bytes()).hexdigest(),ca._PARENT_SHA256)


if __name__=='__main__':
    unittest.main()
