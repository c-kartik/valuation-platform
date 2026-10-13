"""Fixed scope, refresh history, offline replay and preserved populated bindings."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import acquire_income_sweep_backlog as acquisition
from valuation_platform.analyst import retained_income_sweep as sweep
from valuation_platform.analyst import historical_inputs as h


class SweepAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload=json.loads((ROOT/acquisition.OUTPUT).read_text())
        cls.before=json.loads(acquisition.pinned(acquisition.LEDGER))
        cls.after,cls.histories=sweep.build()

    def test_fixed_manifest_scope_and_complete_offline_receipt_replay(self):
        targets=acquisition.scope();self.assertEqual(len(targets),119)
        self.assertEqual(Counter(t['reasons'][0] for t in targets),dict(MISSING_RETAINED_BODY=96,MISSING_RECEIPT=23))
        result=acquisition.verify(self.payload)
        self.assertEqual(result['unattempted'],0)
        self.assertEqual(result['verified']+result['failed'],119)
        self.assertEqual(len({(t['identity']['cik'],t['identity']['accession']) for t in targets}),119)
        self.assertFalse(any(t['issuer'] in ('META','COST','GE') for t in targets))

    def test_all_140_populated_fields_and_receipt_bindings_preserved(self):
        lookup={(r['identity']['cik'],r['identity']['annual_end']):r for r in self.after['rows']}
        count=0
        for old in self.before['rows']:
            new=lookup[(old['identity']['cik'],old['identity']['annual_end'])]
            for f in old['fields']:
                if f['outcome']!='POPULATED':continue
                self.assertEqual(f,next(x for x in new['fields'] if x['field']==f['field']));count+=1
        self.assertEqual(count,140)
        self.assertEqual(self.before['identity_backlog'],self.after['identity_backlog'])
        self.assertEqual(self.before['history_exceptions'],self.after['history_exceptions'])
        self.assertEqual(self.before['excluded_specialized'],self.after['excluded_specialized'])
        self.assertEqual(sum(self.after['outcomes'].values()),398)

    def test_refresh_is_not_recovered_metadata_or_fingerprint_equality(self):
        verified=[r for r in self.payload['rows'] if r['status']=='VERIFIED']
        for row in verified:
            v=row['verification'];self.assertIn('not recovered',v['prior_history']['original_metadata_status'])
            self.assertIn(v['byte_comparison'],('IDENTICAL_ORIGINAL_BYTES','DIFFERENT_ORIGINAL_BYTES','PRIOR_BODY_UNAVAILABLE'))
            receipt=next(a for a in self.payload['artifacts'] if a['source_url']==row['instance_url'])
            self.assertIn('refresh',receipt['retrieval_mode']);self.assertIn('not recovered',receipt['refresh_history'])
        self.assertEqual(sum(r['verification']['byte_comparison'] in ('IDENTICAL_ORIGINAL_BYTES','DIFFERENT_ORIGINAL_BYTES')
            for r in verified),sum(t['reasons']==['MISSING_RECEIPT'] and any(r['identity']==t['identity'] for r in verified) for t in acquisition.scope()))

    def test_wrong_identity_timestamp_body_and_index_selection_rejected(self):
        first=next(r for r in self.payload['rows'] if r['status']=='VERIFIED')
        target=next(t for t in acquisition.scope() if t['identity']==first['identity'])
        receipt=next(a for a in self.payload['artifacts'] if a['source_url']==first['instance_url'])
        for key,value in (('retrieved_at_utc',None),('sha256','0'*64),('source_url','https://www.sec.gov/outside.xml')):
            changed=dict(receipt,**{key:value})
            with self.assertRaises((ValueError,TypeError)):acquisition.verification(target,changed)
        changed=copy.deepcopy(target);changed['identity']['annual_start']='1900-01-01'
        with self.assertRaises(ValueError):acquisition.verification(changed,receipt)
        with self.assertRaises(ValueError):acquisition.instance_url(target,json.dumps({'directory':{'item':[{'name':'a_htm.xml'},{'name':'b_htm.xml'}]}}).encode())

    def test_completed_failures_and_successes_are_not_resumed(self):
        # Resume verifies the completed prefix, never repeats it; offline default
        # cannot initiate network requests. Truncated prefix stays exact ordered scope.
        partial=copy.deepcopy(self.payload);partial['rows']=partial['rows'][:2]
        directories={acquisition.directory(t) for t in acquisition.scope()[:2]}
        partial['artifacts']=[a for a in partial['artifacts'] if a['source_url'].rsplit('/',1)[0] in directories]
        partial['attempts']=[a for a in partial['attempts'] if a['source_url'].rsplit('/',1)[0] in directories]
        partial['request_count']=len(partial['attempts'])
        result=acquisition.verify(partial);self.assertEqual(result['unattempted'],117)
        self.assertEqual([r['identity'] for r in partial['rows']],[t['identity'] for t in acquisition.scope()[:2]])

    def test_resume_replays_only_unfinished_target_and_does_not_retry_failure(self):
        partial=dict(self.payload,rows=self.payload['rows'][:-1],attempts=[],artifacts=[],request_count=0)
        # Prefix receipt validity is separately tested by full offline replay;
        # isolate resume control flow with a deliberately failing transport.
        class Client:
            def __init__(self,_):self.attempts=[];self.receipts=[];self.calls=[]
            def get_bytes(self,url):self.calls.append(url);raise RuntimeError('test transport unavailable')
        client=Client(None)
        with tempfile.TemporaryDirectory() as folder:
            checkpoint=Path(folder)/'checkpoint.json';checkpoint.write_text(json.dumps(partial))
            with patch.dict('os.environ',{'SEC_USER_AGENT':'synthetic-test-only'}),patch.object(acquisition,'RecordingClient',return_value=client),patch.object(acquisition,'verify',return_value={}):
                acquisition.acquire(checkpoint)
                self.assertEqual(len(client.calls),1)
                completed=json.loads(checkpoint.read_text());self.assertEqual(len(completed['rows']),119)
                self.assertEqual(completed['rows'][-1]['status'],'UNRESOLVED')
                acquisition.acquire(checkpoint);self.assertEqual(len(client.calls),1)

    def test_new_histories_remain_partial_and_roundtrip_without_derived_ebit(self):
        history=self.histories['LLY'];payload=h.serialize(history)
        self.assertEqual(h.serialize(h.deserialize(payload)),payload)
        for annual in history.annuals:
            ebit=next(v for v in annual.inputs if v.field is h.Field.EBIT)
            self.assertIsNone(ebit.value)
            self.assertTrue(all(v.value is None for v in annual.inputs if v.field not in (h.Field.REVENUE,h.Field.EBIT)))


if __name__=='__main__':unittest.main()
