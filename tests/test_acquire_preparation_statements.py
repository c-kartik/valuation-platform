"""Offline only: fixed authorized responses, actual receipts, no SEC calls."""
from datetime import datetime
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import acquire_preparation_statements as acquisition


class PreparationStatementAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.payload=json.loads((ROOT/acquisition.s.ACQUISITION).read_text())

    def one(self):
        p=self.payload;t=p['targets'][0];url=t['url']
        return dict(p,targets=[t],rows=[p['rows'][0]],
            artifacts=[r for r in p['artifacts'] if r['source_url']==url],
            attempts=[r for r in p['attempts'] if r['source_url']==url],request_count=1,
            retained_revalidation=[r for r in p['retained_revalidation'] if r['url']==url],
            scope_sha256=hashlib.sha256(acquisition.s.canonical([t]).encode()).hexdigest())

    def test_fixed_scope_every_actual_body_receipt_and_offline_dei_replay(self):
        r=acquisition.verify(self.payload)
        self.assertEqual((r['targets'],r['requests'],r['verified'],r['failed'],r['initially_verified']),(139,139,139,0,132))
        self.assertEqual(len({v['identity']['accession'] for v in self.payload['targets']}),139)
        for artifact in self.payload['artifacts']:
            self.assertEqual(artifact['http_status'],200)
            self.assertEqual(datetime.fromisoformat(artifact['retrieved_at_utc']).utcoffset().total_seconds(),0)
            self.assertEqual(artifact['digest_type'],'sha256_sec_response_body_bytes')
            self.assertIn('original bodies/fingerprints',artifact['refresh_history'])

    def test_changed_exact_target_digest_and_revalidation_are_rejected(self):
        p=copy.deepcopy(self.one());p['targets'][0]['identity']['cik']=1
        with self.assertRaises(ValueError):acquisition.verify(p)
        p=copy.deepcopy(self.one());p['artifacts'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):acquisition.verify(p)
        p=copy.deepcopy(self.one());p['retained_revalidation'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):acquisition.verify(p)

    def test_initial_parser_failures_are_not_falsely_relabelled_transport_failures(self):
        self.assertEqual(sum(r['http_status']==200 for r in self.payload['attempts']),139)
        failed=[r for r in self.payload['rows'] if r['status']!='PRIMARY_IDENTITY_VERIFIED']
        self.assertEqual(len(failed),7)
        self.assertTrue(all(r['url'] in {a['source_url'] for a in self.payload['artifacts']} for r in failed))
        self.assertEqual(len(self.payload['retained_revalidation']),139)


if __name__=='__main__':unittest.main()
