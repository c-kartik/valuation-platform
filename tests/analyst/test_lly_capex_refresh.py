"""Independent content review cannot masquerade as immutable v1 attestation."""
import base64
import copy
from dataclasses import replace
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('lly_refresh_review',ROOT/'scripts/validate_lly_capex_refresh.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
from valuation_platform.analyst import capex_evidence_repair as repair
from valuation_platform.analyst import historical_inputs as h
from valuation_platform.normalization import capex_scope as policy
from valuation_platform.normalization.models import MissingHistoricalMetric, MissingReason


class LLYRefreshReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=json.loads((ROOT/review.RECORD).read_text())
        cls.payload=json.loads((ROOT/repair.OUTPUT).read_text())
        cls.accepted=repair.capex.artifacts();cls.accepted.update(repair.verify(cls.payload))
        cls.entries=[e for e in policy.CAPEX_SCOPE_EQUIVALENCE_POLICY.entries if e.company_cik==59478]

    def test_fixed_old_new_entry_receipt_history_and_offline_review_replay(self):
        self.assertEqual(review.validate(self.record),self.record)
        reports=[a for e in self.record['entries'] for a in e['reports']]
        self.assertEqual(len(reports),15);self.assertEqual(len({a['source_url'] for a in reports}),15)
        self.assertEqual(self.record['requests'],0)
        self.assertEqual((self.record['historical_search']['searched_json_files'],len(self.record['historical_search']['matches'])),(73,0))
        for entry,record in zip(self.entries,self.record['entries']):
            self.assertEqual(record['identity']['accession'],entry.accession_number)
            self.assertEqual(len(record['unchanged_requirements']),7)
            for a,old in zip(record['reports'],json.loads(entry.reviewed_entry_json)['reviewed_evidence']):
                self.assertEqual((a['source_url'],a['historical_sha256']),(old['source_url'],old['sha256']))
                self.assertNotEqual(a['historical_sha256'],a['refreshed_sha256'])
                actual=self.payload['artifacts'][int(a['receipt_locator'].rsplit('/',1)[1])]
                self.assertEqual(review.sha(repair.body(actual)),a['refreshed_sha256'])
                self.assertEqual(actual['retrieved_at_utc'],a['retrieved_at_utc'])
                self.assertEqual(a['http_status'],200)
                self.assertIn('not recovered original metadata',a['refresh_history'])

    def test_independent_cash_table_amounts_scope_and_original_precision(self):
        expected=['(1,309.8)','(1,854.3)','(3,447.6)','(5,057.8)','(7,841)']
        for e,r,amount in zip(self.entries,self.record['entries'],expected):
            obs=r['observations'];self.assertEqual(obs['displayed_outflow'],amount)
            self.assertEqual(obs['display_decimals'],0 if e.annual_end.year==2025 else 1)
            self.assertEqual(obs['cash_caption'],'Purchases of property and equipment')
            self.assertIn('operating lease assets',obs['broader_long_lived_passage'])
            self.assertIn('Construction in progress',obs['physical_components'])
            self.assertEqual(obs['operand_occurrences'][0]['decimals'],'-6' if e.annual_end.year==2025 else '-5')
            self.assertEqual(r['checks']['contradicted'],[])
            self.assertEqual(r['content_review'],'SUPPORTED_EXISTING_FINANCIAL_SCOPE')
            self.assertEqual(r['operational_acceptance'],'BLOCKED_SCHEMA_TREATMENT_REQUIRED')
            self.assertEqual(obs['capitalized_interest_passage'] is None,e.annual_end.year==2025)

    def test_false_operational_acceptance_unsupported_refresh_identity_rejected(self):
        for field,value in [('activated_entries',5),('version','unreviewed-v2'),
                            ('historical_byte_equivalence','VERIFIED'),('renderer_only_change','YES')]:
            changed=copy.deepcopy(self.record);changed[field]=value
            with self.subTest(field=field),self.assertRaises(h.InputError):review.validate(changed)
        for field in ['historical_sha256','refreshed_sha256','receipt_locator']:
            changed=copy.deepcopy(self.record);changed['entries'][0]['reports'][0][field]='unreviewed'
            with self.subTest(field=field),self.assertRaises(h.InputError):review.validate(changed)
        changed=copy.deepcopy(self.record);changed['entries'][0]['operational_acceptance']='ACCEPTED'
        with self.assertRaises(h.InputError):review.validate(changed)

    def test_independent_report_checks_reject_wrong_amount_date_caption_and_notes(self):
        entry=self.entries[0]
        for old,new,suffix in [
            (b'(1,309.8)',b'(1,309.9)','R9.htm'),
            (b'Dec. 31, 2021',b'Dec. 31, 2020','R9.htm'),
            (b'Purchases of property and equipment',b'Purchases of business assets','R9.htm'),
            (b'include Eli Lilly and Company and all subsidiaries',b'include a division only','R11.htm'),
            (b'Construction in progress',b'Unclassified assets','R19.htm')]:
            changed=copy.deepcopy(self.payload)
            a=next(a for a in changed['artifacts'] if a['source_url'].endswith('/'+suffix) and entry.accession_number.replace('-','') in a['source_url'])
            raw=repair.body(a);self.assertIn(old,raw);raw=raw.replace(old,new)
            a['response_body_gzip_base64']=base64.b64encode(gzip.compress(raw,mtime=0)).decode()
            a['sha256']=review.sha(raw);a['byte_length']=len(raw)
            with self.subTest(suffix=suffix,old=old),self.assertRaises((h.InputError,StopIteration)):
                review.inspect_entry(entry,changed,self.accepted)

    def test_immutable_v1_rejects_fresh_digests_and_new_provenance(self):
        from tests.normalization.test_capex_scope import fixture,INVENTORY
        for entry,r in zip(self.entries,self.record['entries']):
            inv=next(r for r in INVENTORY if r['filing']['accession_number']==entry.accession_number)
            bucket,instance,annual,original=fixture(inv)
            bodies={u:self.accepted[u,d][0] for u,d in entry.artifact_digests if (u,d) in self.accepted}
            for a in r['reports']:
                actual=self.payload['artifacts'][int(a['receipt_locator'].rsplit('/',1)[1])]
                bodies[a['source_url']]=repair.body(actual)
            with self.assertRaisesRegex(policy.CapexScopePolicyError,'Missing or changed'):
                policy.verify_capex_artifacts(entry,bodies,instance)
            actual_digests=tuple((u,review.sha(bodies[u])) for u,d in entry.artifact_digests)
            attestation=policy.VerifiedCapexArtifacts(entry.accession_number,actual_digests)
            direct=MissingHistoricalMetric(repair.capex.FinancialMetric.CAPEX,
                MissingReason.NO_CONFIGURED_CONCEPT_OBSERVATION,repair.capex.CAPEX_POLICY.candidates)
            with self.assertRaisesRegex(policy.CapexScopePolicyError,'Incomplete or mismatched'):
                policy.apply_curated_capex_scope_policy(bucket,direct,entry.company_cik,annual,instance,attestation)
            # Existing synthetic fixture attestation is only a unit-test setup,
            # never evidence that the unavailable historical bodies were verified.
            old=policy.apply_curated_capex_scope_policy(bucket,direct,entry.company_cik,annual,instance,original)
            changed=replace(old.policy_provenance,capex_scope=replace(old.policy_provenance.capex_scope,
                verified_artifact_digests=actual_digests))
            with self.assertRaisesRegex(policy.CapexScopePolicyError,'Invalid Capex policy/audit provenance'):
                policy.validate_capex_scope_provenance(changed)
            from valuation_platform.normalization.output import _policy_reference,HistoricalOutputError
            with self.assertRaises(HistoricalOutputError):_policy_reference(changed,bucket.filing)

    def test_review_serialization_exact_closed_history_and_no_output_change(self):
        encoded=json.dumps(self.record,sort_keys=True,separators=(',',':'))
        self.assertEqual(encoded,json.dumps(review.validate(json.loads(encoded)),sort_keys=True,separators=(',',':')))
        paths=['docs/repaired-capex-ledger.json','docs/evidence/capex-binding-repair.json',
            review.REGISTRY,'src/valuation_platform/normalization/capex_scope.py',
            'src/valuation_platform/normalization/models.py','src/valuation_platform/normalization/output.py',
            'docs/pilot-historical-input-mappings.json','src/valuation_platform/analyst/pilot_historical_inputs.py']
        for p in paths:self.assertEqual((ROOT/p).read_bytes(),subprocess.check_output(['git','show',review.BASELINE+':'+p],cwd=ROOT))
        ledger=json.loads((ROOT/'docs/repaired-capex-ledger.json').read_text())
        self.assertEqual(sum(ledger['outcomes'].values()),199)
        self.assertEqual(ledger['outcomes'],dict(DIRECT=145,CURATED=15,EVIDENCE_GAP=5,UNAPPROVED_SCOPE=34))
