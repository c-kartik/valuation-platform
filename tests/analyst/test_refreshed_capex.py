"""Preparation evidence refresh, not successful legacy fingerprint verification."""
import copy
from dataclasses import FrozenInstanceError,replace
from decimal import Decimal
import json
import subprocess
import unittest
from unittest.mock import patch
from valuation_platform.analyst import refreshed_capex as r, historical_inputs as h
from valuation_platform.analyst import capex_evidence_repair as prior, retained_capex as c
from valuation_platform.analyst import retained_cfo_preparation as cfo, pilot_historical_inputs as pilots
from valuation_platform.normalization.models import NormalizedHistoricalValue,HistoricalPeriod

HEAD='ce4d395213427fb50247e392607b23e0dfb3fa9b'


class RefreshTransportGateTests(unittest.TestCase):
    def test_malformed_envelope_and_model_fields_fail_closed(self):
        for doc in [[],dict(schema=r.SCHEMA,history=None,original_bodies=[]),
                    dict(schema=r.SCHEMA,history=dict(type='RefreshedHistory',fields=[]),original_bodies={})]:
            with self.subTest(doc=doc),self.assertRaises(h.InputError):r.deserialize(json.dumps(doc))

    def test_v2_body_integrity_and_missing_reference_reject_before_acceptance(self):
        doc=dict(schema=r.SCHEMA,history=None,original_bodies={r.review.sha(b'original'):h._encode(b'tampered')})
        with self.assertRaisesRegex(h.InputError,'Invalid refreshed'):r.deserialize(json.dumps(doc))
        with self.assertRaisesRegex(h.InputError,'Missing serialized'):
            r._decode(dict(body_reference='0'*64),{},set())

    def test_original_index_representation_gate_is_not_waived_by_refresh(self):
        with patch.object(r.review.policy,'_validate_representation_records',side_effect=h.InputError('Original representation proof failed')):
            with self.assertRaisesRegex(h.InputError,'Original representation proof failed'):r.audits()
        self.assertEqual(len(r.audits()),5)


class RefreshedCapexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.histories=r.build();cls.wrapped=cls.histories['LLY']
        cls.audit=cls.wrapped.refresh_audits[0];cls.annual=cls.wrapped.bundle.annuals[0]
        cls.evidence=cfo.prepare(cls.annual)

    def test_all_five_exact_approvals_199_period_reconciliation(self):
        self.assertEqual(self.ledger,json.loads((r.review.ROOT/r.LEDGER).read_text()))
        self.assertEqual(self.ledger['outcomes'],dict(DIRECT=145,CURATED=15,CURATED_REFRESH=5,UNAPPROVED_SCOPE=34))
        self.assertEqual((self.ledger['selected_periods'],self.ledger['issuer_count'],len(self.ledger['history_exceptions'])),(199,42,11))
        self.assertEqual(len(self.wrapped.refresh_audits),5)
        for a,magnitude in zip(self.wrapped.bundle.annuals,['1309800000','1854300000','3447600000','5057800000','7841000000']):
            v=next(v for v in a.inputs if v.field is h.Field.CAPEX)
            self.assertEqual((v.value,v.sign,v.scale),(-Decimal(magnitude),-1,1))
            self.assertEqual(v.role,'approved_reported_cash_capex_outflow_refreshed_evidence')
            self.assertFalse(any(f.startswith(c.PROOF) for f in v.flags))
            self.assertEqual(v.sources[0].decimals,'-6' if a.period.annual_end.year==2025 else '-5')
            self.assertEqual(v.review,h.Review.ACCEPTED);self.assertEqual(v.completeness,h.Completeness.PARTIAL)

    def test_original_and_new_evidence_history_explicit_and_immutable(self):
        for audit in self.wrapped.refresh_audits:
            self.assertEqual(audit.original_byte_equivalence,'UNPROVED')
            self.assertEqual(audit.acceptance_basis,r.BASIS)
            self.assertEqual((audit.financial_policy_id,audit.financial_policy_version),('capex_scope_equivalence','1'))
            self.assertEqual(len(audit.artifacts),3)
            for a in audit.artifacts:
                self.assertEqual(a.historical_status,r.HISTORICAL_STATUS)
                self.assertNotEqual(a.historical_sha256,a.refreshed_receipt.artifact.sha256)
                self.assertTrue(a.supported_requirements)
        with self.assertRaises(FrozenInstanceError):self.audit.original_byte_equivalence='PROVED'

    def test_exact_review_entry_and_requirements_fail_closed(self):
        for kw in [dict(refresh_version='unregistered'),dict(review_sha256='0'*64),dict(original_byte_equivalence='PROVED'),
            dict(acceptance_basis='VERIFIED_ORIGINAL'),dict(supported_requirements=()),dict(original_entry_json='{}'),
            dict(review_entry_json='{}'),dict(financial_policy_version='2')]:
            with self.subTest(kw=kw),self.assertRaises(h.InputError):replace(self.audit,**kw)
        unknown=replace(self.audit.period,accession='0000059478-27-999999')
        with self.assertRaises(h.InputError):replace(self.audit,period=unknown)
        record=copy.deepcopy(r.registered_review());record['entries'][0]['checks']['supported'].remove(r.REQUIRED[0])
        with patch.object(r,'registered_review',return_value=record),self.assertRaisesRegex(h.InputError,'assertions missing'):
            replace(self.audit)

    def test_tampered_body_digest_receipt_and_artifact_pair_rejected(self):
        a=self.audit.artifacts[0];receipt=a.refreshed_receipt;artifact=receipt.artifact
        with self.assertRaises(ValueError):replace(artifact,body=artifact.body+b'changed')
        changed=replace(artifact,body=artifact.body+b'changed',sha256=r.review.sha(artifact.body+b'changed'))
        altered=replace(a,refreshed_receipt=replace(receipt,artifact=changed,byte_length=len(changed.body)))
        with self.assertRaises(h.InputError):replace(self.audit,artifacts=(altered,*self.audit.artifacts[1:]))
        altered=replace(a,historical_sha256='0'*64)
        with self.assertRaises(h.InputError):replace(self.audit,artifacts=(altered,*self.audit.artifacts[1:]))
        altered=replace(a,refreshed_receipt=replace(receipt,retrieved_at_utc='2026-01-01T00:00:00+00:00'))
        with self.assertRaises(h.InputError):replace(self.audit,artifacts=(altered,*self.audit.artifacts[1:]))
        with self.assertRaises(h.InputError):replace(self.audit,artifacts=self.audit.artifacts[:2])

    def test_financial_conflict_and_mismatched_instance_never_populate(self):
        _,entry=r.matching(self.audit.period)
        result=c.inspect(self.evidence,entry.concept);candidate=result.candidates[0]
        fact=next(f for f,i in self.evidence.facts if f.concept==entry.concept and f.start==entry.annual_start)
        changed=replace(fact,raw_value='1',numeric_value=Decimal('1'))
        evidence=replace(self.evidence,facts=tuple((changed,i) if f is fact else (f,i) for f,i in self.evidence.facts))
        with self.assertRaisesRegex(h.InputError,'Competing or malformed'):r.package(evidence,self.audit)
        with self.assertRaises(h.InputError):r.package(replace(self.evidence,instance=None),self.audit)
        source=getattr(c,'__compact')(candidate,self.evidence)
        direct=NormalizedHistoricalValue(c.FinancialMetric.CAPEX,entry.expected_value+1,'USD',HistoricalPeriod(entry.annual_start,entry.annual_end),source,())
        with patch.object(c,'direct_result',return_value=(direct,result)),self.assertRaisesRegex(h.InputError,'Conflicting eligible'):
            r.package(self.evidence,self.audit)
        absent=replace(result,candidates=())
        with patch.object(c,'inspect',return_value=absent),self.assertRaises(h.InputError):r.package(self.evidence,self.audit)

    def test_v2_deterministic_roundtrip_typed_proof_and_no_v1_downgrade(self):
        payload=r.serialize(self.wrapped)
        self.assertEqual(json.loads(payload)['schema'],r.SCHEMA)
        self.assertEqual(payload,r.serialize(r.validate_history(payload)))
        self.assertEqual(r.deserialize(payload),self.wrapped)
        with self.assertRaises(h.InputError):h.serialize(self.wrapped.bundle)
        downgraded=json.dumps(dict(schema=h.SCHEMA,bundle=h._encode(self.wrapped.bundle)))
        with self.assertRaises(h.InputError):h.deserialize(downgraded)
        with self.assertRaises(h.InputError):r.deserialize(payload.replace(r.SCHEMA,'future-version',1))
        with self.assertRaises(h.InputError):r.deserialize(payload[:-1]+',"schema":"'+r.SCHEMA+'"}')

    def test_missing_or_orphaned_provenance_and_altered_values_rejected(self):
        with self.assertRaises(h.InputError):replace(self.wrapped,refresh_audits=self.wrapped.refresh_audits[:4])
        with self.assertRaises(h.InputError):replace(self.wrapped,refresh_audits=tuple(reversed(self.wrapped.refresh_audits)))
        v=next(v for v in self.annual.inputs if v.field is h.Field.CAPEX)
        changed=replace(v,selection_rationale='silent alternative')
        a=replace(self.annual,inputs=tuple(changed if i==v else i for i in self.annual.inputs))
        with self.assertRaises(h.InputError):replace(self.wrapped,bundle=replace(self.wrapped.bundle,annuals=(a,*self.wrapped.bundle.annuals[1:])))

    def test_all_160_results_other_fields_and_34_scope_cases_preserved(self):
        old,histories=prior.build()
        for oldrow,newrow in zip(old['rows'],self.ledger['rows']):
            if oldrow['issuer']!='LLY':self.assertEqual(oldrow,newrow)
            else:
                self.assertEqual(newrow['original_legacy_evidence_gaps'],oldrow['approved_entry_evidence_gaps'])
                self.assertEqual(newrow['policy']['legacy_attestation'],'NOT_SATISFIED_OR_CLAIMED')
        for name,history in histories.items():
            new=self.histories[name]
            if name!='LLY':self.assertEqual(history,new)
            else:
                for a,b in zip(history.annuals,new.bundle.annuals):
                    self.assertEqual(tuple(v for v in a.inputs if v.field is not h.Field.CAPEX),tuple(v for v in b.inputs if v.field is not h.Field.CAPEX))
        for name in ('MSFT','AAPL','GOOGL'):
            before=pilots.load_history(name)
            self.assertEqual(r.serialize(before),h.serialize(before))
            self.assertEqual(r.deserialize(h.serialize(before)),before)
        for path in ['docs/evidence/lly-capex-refresh-review-v1.json','docs/evidence/capex-binding-repair.json',
            'docs/repaired-capex-ledger.json','src/valuation_platform/normalization/models.py',
            'src/valuation_platform/normalization/output.py','src/valuation_platform/normalization/capex_scope.py',
            'src/valuation_platform/normalization/capex_scope_registry.json',
            'src/valuation_platform/normalization/capex_scope_v2_registry.json','src/valuation_platform/normalization/capex_scope_v3_registry.json']:
            self.assertEqual((r.review.ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=r.review.ROOT))
