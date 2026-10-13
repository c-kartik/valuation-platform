"""Fixed evidence repair: byte binding, not fresh economic approval."""
import copy
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import subprocess
import unittest
from valuation_platform.analyst import capex_evidence_repair as r, retained_capex as c
from valuation_platform.analyst import historical_inputs as h, nvda_income_inputs as shared, pilot_historical_inputs as p


class CapexBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload=json.loads((shared.ROOT/r.OUTPUT).read_text())
        cls.ledger,cls.histories=r.build()

    def test_fixed_85_15_scope_reconciles_immutable_entries_and_local_search(self):
        targets=r.scope();self.assertEqual(len(targets),85)
        self.assertEqual(len({t['source_url'] for t in targets}),85)
        self.assertEqual(len({t['identity']['accession'] for t in targets}),15)
        self.assertFalse(self.payload['local_search']['matches'])
        self.assertEqual(self.payload['local_search']['searched_json_files'],71)
        for t in targets:
            entry=next(e for policy in c.curated.CAPEX_SCOPE_POLICY_CATALOG.policies for e in policy.entries if e.accession_number==t['identity']['accession'])
            self.assertIn((t['source_url'],t['sha256']),entry.artifact_digests)

    def test_actual_receipts_85_requests_70_verified_15_mismatches_rate_and_history(self):
        x=self.payload;accepted=r.verify(x)
        self.assertEqual(len(accepted),70);self.assertEqual(x['request_count'],85)
        self.assertEqual({a['http_status'] for a in x['attempts']},{200})
        self.assertEqual(sum(row['status']=='BYTE_MISMATCH' for row in x['rows']),15)
        starts=[datetime.fromisoformat(a['request_started_at_utc']) for a in x['attempts']]
        self.assertTrue(all((b-a).total_seconds()>=0.499 for a,b in zip(starts,starts[1:])))
        for row in x['rows']:
            t=row['target'];a=next(a for a in x['artifacts'] if a['source_url']==t['source_url'])
            self.assertEqual(hashlib.sha256(r.body(a)).hexdigest(),a['sha256'])
            self.assertEqual(a['prior_expected_sha256'],t['sha256'])
            self.assertIn('not recovered original metadata',a['refresh_history'])
            if row['status']=='BYTE_MISMATCH':
                self.assertEqual(t['issuer'],'LLY');self.assertNotEqual(a['sha256'],t['sha256'])
                self.assertNotIn((t['source_url'],t['sha256']),accepted)

    def test_mismatch_and_representation_relabel_rejected(self):
        wrong=copy.deepcopy(self.payload)
        next(row for row in wrong['rows'] if row['status']=='BYTE_MISMATCH')['status']='VERIFIED_REFRESH'
        with self.assertRaises(h.InputError):r.verify(wrong)
        for field,value in (('representation','retained_reserialized_json_utf8_bytes'),('digest_type','sha256_parsed_json')):
            wrong=copy.deepcopy(self.payload);wrong['artifacts'][0][field]=value
            with self.assertRaises(h.InputError):r.verify(wrong)
        wrong=copy.deepcopy(self.payload);wrong['artifacts'][0]['prior_expected_sha256']='0'*64
        with self.assertRaises(h.InputError):r.verify(wrong)
        wrong=copy.deepcopy(self.payload);wrong['attempts'][0]['http_status']=404
        with self.assertRaises(h.InputError):r.verify(wrong)

    def test_offline_199_replay_versions_and_unapproved_scope_preserved(self):
        x=self.ledger
        self.assertEqual(x,json.loads((shared.ROOT/'docs/repaired-capex-ledger.json').read_text()))
        self.assertEqual(x['outcomes'],dict(DIRECT=145,CURATED=15,EVIDENCE_GAP=5,UNAPPROVED_SCOPE=34))
        self.assertEqual(x['curated_versions'],{'1':5,'2':5,'3':5})
        self.assertEqual((x['selected_periods'],x['issuer_count'],len(x['history_exceptions'])),(199,42,11))
        self.assertEqual({row['issuer'] for row in x['rows'] if row['status']=='EVIDENCE_GAP'},{'LLY'})
        self.assertTrue(all(len(row['approved_entry_evidence_gaps'])==3 for row in x['rows'] if row['issuer']=='LLY'))

    def test_all_150_populated_bindings_34_scope_and_other_fields_unchanged(self):
        old,baseline=c.build()
        for oldrow,new in zip(old['rows'],self.ledger['rows']):
            if oldrow['status'] in ('DIRECT','CURATED','UNAPPROVED_SCOPE'):self.assertEqual(oldrow,new)
        for name,history in baseline.items():
            for oldannual in history.annuals:
                annual=next(a for a in self.histories[name].annuals if a.period==oldannual.period)
                self.assertEqual(tuple(v for v in oldannual.inputs if v.field is not h.Field.CAPEX),tuple(v for v in annual.inputs if v.field is not h.Field.CAPEX))
                if name not in ('AMZN','LLY','CVX'):self.assertEqual(oldannual,annual)
        for name in ('AAPL','MSFT','GOOGL'):
            for a in p.load_history(name).annuals:self.assertEqual(a,next(v for v in self.histories[name].annuals if v.period==a.period))
        for path in ('src/valuation_platform/normalization/capex_scope.py','src/valuation_platform/normalization/capex_scope_registry.json',
                     'src/valuation_platform/normalization/capex_scope_v2_registry.json','src/valuation_platform/normalization/capex_scope_v3_registry.json',
                     'docs/retained-capex-ledger.json','docs/retained-tax-sbc-ledger.json','docs/pilot-historical-input-mappings.json'):
            self.assertEqual((shared.ROOT/path).read_bytes(),r.pinned(path))

    def test_provenance_serialization_replay_without_synthetic_attestations(self):
        for name,version in (('AMZN','1'),('CVX','2')):
            a=self.histories[name].annuals[-1];v=next(v for v in a.inputs if v.field is h.Field.CAPEX)
            proof=json.loads(next(f[len(c.PROOF):] for f in v.flags if f.startswith(c.PROOF)))
            self.assertEqual(proof['version'],version);self.assertTrue(proof['artifact_bindings'])
            self.assertLess(v.value,0);self.assertEqual(v.sign,-1)
            one=replace(self.histories[name],annuals=(a,),history_exceptions=('Test one registered original period.',))
            serialized=h.serialize(one);self.assertEqual(serialized,h.serialize(r.validate_history(serialized)))
            altered=replace(one,annuals=(replace(a,inputs=tuple(replace(v,selection_rationale='unreviewed replacement') if i==v else i for i in a.inputs)),))
            with self.assertRaises(h.InputError):r.validate_history(h.serialize(altered))
