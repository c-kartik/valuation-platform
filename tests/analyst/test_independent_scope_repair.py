"""Acquired primary identity and exact negative D&A dispositions; no approvals."""
import base64
from copy import deepcopy
import gzip
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from valuation_platform.analyst import da_scope_dispositions as s, retained_d_and_a as d, prepared_assembly as a
from valuation_platform.analyst import historical_inputs as h, retained_components as r, retained_cfo_preparation as cfo
from tests.analyst import test_prepared_assembly as shared
sys.path.insert(0,str(a.ROOT/'scripts'))
import acquire_independent_documents as acquisition

BASELINE=acquisition.BASELINE

class IndependentScopeRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not hasattr(shared.PreparedAssemblyTests,'histories'):shared.PreparedAssemblyTests.setUpClass()
        cls.histories=shared.PreparedAssemblyTests.histories
        from valuation_platform.analyst import analyst_overrides as o
        per={k:o.queue_summary(p) for k,p in cls.histories.items()}
        report=dict(schema='grouped-preparation-review-v1',issuers=len(per),selected_periods=199,
            per_issuer=per,totals={key:sum(v[key] for v in per.values()) for key in ('diagnostics','groups','actionable','informational')})
        Path('/tmp/grouped-preparation-review-summary.json').write_text(a.canonical(report)+'\n')

    def test_ten_exact_receipts_identity_and_offline_integrity(self):
        payload=json.loads((a.ROOT/acquisition.OUTPUT).read_text())
        self.assertEqual(len(acquisition.verify(payload)),10)
        self.assertEqual(len(payload['attempts']),10)
        self.assertTrue(all(x['outcome']=='SUCCESS' for x in payload['attempts']))
        for key,value in [('http_status',403),('representation','parsed_json'),('sha256','0'*64),('accession','unregistered')]:
            bad=deepcopy(payload);bad['artifacts'][0][key]=value
            with self.assertRaises(ValueError):acquisition.verify(bad)
        bad=deepcopy(payload);bad['artifacts'][0]['response_body_gzip_base64']=base64.b64encode(gzip.compress(b'changed')).decode()
        with self.assertRaises(ValueError):acquisition.verify(bad)

    def test_seven_downgrades_source_support_and_frozen_discrepancy(self):
        reviews=s.entries();self.assertEqual(len(reviews),7)
        for entry in reviews:
            overlay=next(o for o in self.histories[entry['ticker']].d_and_a if o.period.accession==entry['accession'])
            self.assertIsNone(overlay.required_value.value)
            self.assertTrue(overlay.required_value.unresolved_requirements)
            old=next(v for v in overlay.support_only if 'scope_disqualified' in v.flags)
            self.assertEqual(str(old.value),entry['value_usd']);self.assertTrue(old.sources)
            self.assertEqual(json.loads(overlay.policy_json)['preparation_scope_disposition'],entry)
            evidence=r.prepare(overlay.period,(overlay.receipt,),(r.ArtifactBinding(overlay.receipt.artifact.url,overlay.receipt.artifact.sha256,'instance'),))
            resolved,*_=d.resolve(evidence,d.artifact_store())
            self.assertEqual(str(resolved.value),entry['value_usd']) # Legacy verifier/policy unchanged.
            self.assertEqual(d.deserialize(d.serialize(overlay)),overlay)
        self.assertEqual(sum(o.required_value.value is not None for o in self.histories['HD'].d_and_a),3)
        self.assertTrue(all(o.required_value.value is None for o in self.histories['AMZN'].d_and_a))

    def test_changed_identity_amount_or_negative_record_body_fails_closed(self):
        entry=s.entries()[0];overlay=self.histories[entry['ticker']].d_and_a[0]
        with self.assertRaises(h.InputError):s.disposition(overlay.period,d.DIRECT,'1')
        with patch.object(s,'entries',return_value=[dict(entry,cik=999)]):
            with self.assertRaises(h.InputError):s.disposition(overlay.period,d.DIRECT,entry['value_usd'])
        with patch.object(s,'entries',return_value=[dict(entry,sha256='0'*64)]):
            with self.assertRaises(h.InputError):s.disposition(overlay.period,d.DIRECT,entry['value_usd'])
        original=Path.read_text
        def altered(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path==s.ROOT/entry['path']:
                doc=json.loads(text);items=doc if isinstance(doc,list) else doc['artifacts']
                artifact=items[entry['artifact_index']]
                key='response_body_gzip_base64' if 'response_body_gzip_base64' in artifact else 'body_gzip_base64'
                artifact[key]=base64.b64encode(gzip.compress(b'altered statement')).decode()
                return json.dumps(doc)
            return text
        with patch.object(Path,'read_text',altered):
            with self.assertRaises(h.InputError):s.disposition(overlay.period,d.DIRECT,entry['value_usd'])

    def test_previous_fields_and_undeclared_da_cases_preserved(self):
        old=json.loads(subprocess.check_output(['git','show',BASELINE+':'+d.LEDGER],cwd=a.ROOT))
        new=json.loads((a.ROOT/d.LEDGER).read_text());changed={r['accession'] for r in s.entries()}
        prior={r['identity']['accession']:r for r in old['rows']}
        for row in new['rows']:
            if row['identity']['accession'] not in changed:self.assertEqual(row,prior[row['identity']['accession']])
        for path in a.LEDGERS:
            if path!=d.LEDGER:self.assertEqual((a.ROOT/path).read_bytes(),subprocess.check_output(['git','show',BASELINE+':'+path],cwd=a.ROOT))
