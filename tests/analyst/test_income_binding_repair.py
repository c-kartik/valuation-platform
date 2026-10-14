"""Official cutoff/annual replay, exact repair and unchanged prior bindings."""
import copy
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from tests.analyst.preparation_preservation import assert_preserved

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import repair_income_evidence_bindings as acquisition
from valuation_platform.analyst import repaired_income_preparation as repaired
from valuation_platform.analyst import approved_income_integration as approved, historical_inputs as h

BASELINE='eb99ab310fe6d3860d4cd3036e8a922189350d38'


class IncomeBindingRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload=repaired.load();cls.ledger,cls.histories=repaired.build()
        cls.before=json.loads((ROOT/'docs/approved-income-integration-ledger.json').read_text())

    def test_fixed_targets_actual_receipts_and_full_offline_selection_replay(self):
        self.assertEqual(acquisition.verify(self.payload),dict(requests=25,verified=20,unresolved=0,statuses={'VERIFIED':20}))
        self.assertEqual(len(acquisition.scope()),4)
        self.assertTrue(all(s['complete_frozen_history_match'] for s in self.payload['selection']))
        self.assertEqual(sum(a['source_url'].startswith('https://data.sec.gov/submissions/') for a in self.payload['attempts']),5)
        self.assertEqual(sum(a['source_url'].endswith('index.json') for a in self.payload['attempts']),10)
        self.assertEqual(sum(a['source_url'].endswith('_htm.xml') for a in self.payload['attempts']),10)
        self.assertFalse(any('/200406/' in a['source_url'] or '/319201/' in a['source_url'] for a in self.payload['attempts']))
        starts=[datetime.fromisoformat(a['request_started_at_utc']) for a in self.payload['attempts']]
        self.assertTrue(all((b-a).total_seconds()>=.49 for a,b in zip(starts,starts[1:])))
        for a in self.payload['artifacts']:
            self.assertEqual(hashlib.sha256(acquisition.body_of(a)).hexdigest(),a['sha256'])
            self.assertIn('original metadata gaps',a['refresh_history'])

    def test_cutoff_accession_date_primary_document_and_annual_tampering_rejected(self):
        for change in (lambda d:d.__setitem__('frozen_cutoff','2027-01-01T00:00:00+00:00'),
            lambda d:d['rows'][0]['filing'].__setitem__('filing_date','1900-01-01'),
            lambda d:d['rows'][0]['filing'].__setitem__('primary_document','unrelated.htm'),
            lambda d:d['rows'][0]['filing'].__setitem__('accession_number','0000000000-00-000000'),
            lambda d:d['rows'][-1]['identity'].__setitem__('annual_start','2026-01-01'),
            lambda d:d['artifacts'][0].__setitem__('retrieved_at_utc',None)):
            doc=copy.deepcopy(self.payload);change(doc)
            with self.assertRaises((ValueError,TypeError)):acquisition.verify(doc)

    def test_all_398_slots_and_exact_remaining_exceptions(self):
        self.assertEqual(self.ledger['outcomes'],dict(POPULATED=357,DERIVED=25,CONFLICTING_VALUES=11,NO_ELIGIBLE_DIRECT_CONCEPT=5))
        self.assertEqual(sum(self.ledger['outcomes'].values()),398)
        self.assertFalse(self.ledger['binding_repair_exceptions']);self.assertFalse(self.ledger['identity_backlog'])
        self.assertFalse(self.ledger['derivation_metadata_exceptions']);self.assertFalse(self.ledger['seed_identity_exceptions'])
        self.assertEqual(self.ledger,json.loads((ROOT/'docs/repaired-income-ledger.json').read_text()))
        self.assertEqual(self.ledger,repaired.build()[0])

    def test_337_direct_15_derived_11_conflicts_and_cvx_unchanged(self):
        after={(r['issuer'],r['identity']['annual_end']):r for r in self.ledger['rows']};counts={}
        for old in self.before['rows']:
            new=after[(old['issuer'],old['identity']['annual_end'])]
            for slot in old['fields']:
                if slot['outcome'] in ('POPULATED','DERIVED','CONFLICTING_VALUES') or old['issuer']=='CVX':
                    self.assertEqual(slot,next(f for f in new['fields'] if f['field']==slot['field']))
                    counts[slot['outcome']]=counts.get(slot['outcome'],0)+1
        self.assertEqual((counts['POPULATED'],counts['DERIVED'],counts['CONFLICTING_VALUES']),(337,15,11))
        self.assertEqual(self.before['history_exceptions'],self.ledger['history_exceptions'])

    def test_seed_sources_independently_match_original_fact_occurrences(self):
        import xml.etree.ElementTree as ET
        for name in ('META','COST'):
            history=self.histories[name];self.assertEqual(len(history.annuals),5)
            for annual in history.annuals:
                for v in annual.inputs:
                    if v.value is None:continue
                    self.assertIn(v.field,(h.Field.REVENUE,h.Field.EBIT));self.assertEqual(v.origin,h.Origin.REPORTED)
                    for observation in (v,*v.alternatives):
                        for source in observation.sources:
                            root=ET.fromstring(source.receipt.artifact.body);fact=list(root)[source.occurrence_ordinal]
                            self.assertEqual(fact.tag,'{'+source.namespace+'}'+source.concept)
                            self.assertEqual(fact.get('contextRef'),source.context_id)
                            self.assertEqual(Decimal(fact.text),observation.value)
                            self.assertEqual(fact.get('decimals'),observation.precision)
                            self.assertEqual(source.period,annual.period)
                            self.assertEqual((observation.scale,observation.sign,observation.unit),(1,1,'USD'))
        cost=self.histories['COST'].annuals[-1]
        self.assertEqual(str(cost.period.annual_start),'2025-09-01')
        self.assertEqual(cost.period.accession,'0000909832-26-000093')

    def test_ten_new_derivations_arithmetic_metadata_proof_and_serialization(self):
        for name in ('JNJ','KLAC'):
            history=self.histories[name];self.assertEqual(len(history.annuals),5)
            for annual in history.annuals:
                derived=next(v for v in annual.inputs if v.origin is h.Origin.DERIVED)
                proof=json.loads(next(f[len(approved.PROOF_FLAG):] for f in derived.flags if f.startswith(approved.PROOF_FLAG)))
                self.assertEqual((proof['policy_id'],proof['policy_version']),('operating_income_component_derivation','1'))
                self.assertEqual(sum((Decimal(o['contribution']) for o in proof['operands'] if o['contribution'] is not None),Decimal(0)),derived.value)
                self.assertTrue(all(v['passed'] for v in proof['validations']))
                metadata=next(r['filing'] for r in self.payload['rows'] if r['identity'] and r['identity']['accession']==annual.period.accession)
                self.assertTrue(all(o['observation_filed']==metadata['filing_date'] for p in proof['operands'] for o in p['occurrences']))
            one=replace(history,annuals=(history.annuals[-1],));payload=h.serialize(one)
            self.assertEqual(h.serialize(approved.validate_serialized_history(payload,include_repairs=True)),payload)
        one=replace(self.histories['META'],annuals=(self.histories['META'].annuals[-1],),history_exceptions=('Single-period serialization test, not an additional history registration.',))
        payload=h.serialize(one);self.assertEqual(h.serialize(h.deserialize(payload)),payload)

    def test_original_evidence_policies_and_seed_candidates_preserved(self):
        for path in ('docs/evidence/income-sweep-backlog-acquisition.json','docs/approved-income-integration-bindings.json',
            'docs/phase1-selected-filing-identity-manifest.json','src/valuation_platform/normalization/operating_income_derivation.py',
            'src/valuation_platform/analyst/historical_inputs.py','docs/approved-income-integration-ledger.json'):
            assert_preserved(self, ROOT, path, BASELINE)


if __name__=='__main__':unittest.main()
