"""Offline fixed-scope acquisition replay and original-slot preservation."""
import base64
import copy
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import acquire_retained_income_instances as a
from valuation_platform.analyst import retained_income_batch as b


class IncomeInstanceAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload=json.loads((ROOT/a.OUTPUT).read_text())
        cls.ledger,cls.histories=b.build()

    def test_scope_requests_and_original_bodies_replay(self):
        self.assertEqual(a.verify(self.payload),dict(requests=13,verified=13,unresolved=0))
        self.assertEqual(len(a.scope()),13)
        self.assertEqual(len(self.payload['artifacts']),13)
        self.assertTrue(all(x['http_status']==200 and x['outcome']=='SUCCESS' for x in self.payload['attempts']))
        self.assertTrue(all(x['source_url'].endswith('_htm.xml') for x in self.payload['attempts']))
        stamps=[datetime.fromisoformat(x['request_started_at_utc']) for x in self.payload['attempts']]
        self.assertTrue(all((later-earlier).total_seconds()>=0.49 for earlier,later in zip(stamps,stamps[1:])))
        for receipt in self.payload['artifacts']:
            body=a.body_of(receipt)
            self.assertEqual(hashlib.sha256(body).hexdigest(),receipt['sha256'])
            self.assertEqual(len(body),receipt['byte_length'])
            self.assertEqual(receipt['prior_fingerprint'],receipt['sha256'])
            self.assertIn('unavailable',receipt['prior_fingerprint_status'])
            self.assertIn('not recovered',receipt['refresh_history'])

    def test_all_original_80_slots_and_54_populated_bindings_preserved(self):
        baseline=json.loads(a.pinned(a.BASELINE_LEDGER))
        self.assertEqual(self.ledger['field_period_slots'],80)
        self.assertEqual(sum(v['populated'] for v in self.ledger['summary'].values()),80)
        self.assertEqual(sum(v['unavailable']+v['conflicting'] for v in self.ledger['summary'].values()),0)
        original=0
        for before,after in zip(baseline['rows'],self.ledger['rows']):
            self.assertEqual(before['identity'],after['identity'])
            self.assertEqual(before['expected_instance'],after['expected_instance'])
            for old,new in zip(before['fields'],after['fields']):
                if old['status']=='POPULATED':
                    self.assertEqual(old,new);original+=1
                else:self.assertEqual(new['status'],'POPULATED')
        self.assertEqual(original,54)

    def test_wrong_identity_timestamp_digest_and_requests_rejected(self):
        for mutation in (lambda d:d['rows'][0]['identity'].__setitem__('annual_start','2020-01-01'),
                         lambda d:d['artifacts'][0].__setitem__('retrieved_at_utc',None),
                         lambda d:d['artifacts'][0].__setitem__('sha256','0'*64),
                         lambda d:d['attempts'][0].__setitem__('source_url','https://www.sec.gov/outside-fixed-scope')):
            doc=copy.deepcopy(self.payload);mutation(doc)
            with self.assertRaises((ValueError,TypeError)):a.verify(doc)


if __name__=='__main__':unittest.main()
