"""Universe accounting and offline evidence replay, without financial expansion."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import subprocess
import unittest
from tests.analyst.preparation_preservation import assert_preserved
import xml.etree.ElementTree as ET
from valuation_platform.analyst import retained_income_sweep as sweep
from valuation_platform.analyst import retained_income_batch as batch, historical_inputs as h
from valuation_platform.analyst import nvda_income_inputs as shared, retained_income_preparation as income

HEAD='d6ffbb3f50df695b28a2d72107b019fcf3399a29'


class SweepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.histories=sweep.build()
        cls.config,cls.refs=sweep.sources()
        cls.manifest=shared.pinned(shared.MANIFEST,shared.MANIFEST_SHA256)

    def test_complete_scope_unique_slots_and_offline_replay(self):
        doc=self.ledger
        self.assertEqual((doc['issuer_count'],doc['selected_periods'],doc['slots']),(42,199,398))
        self.assertEqual(len(doc['excluded_specialized']),8);self.assertIn('GE',doc['excluded_specialized'])
        self.assertEqual(len(doc['history_exceptions']),11)
        keys={(r['identity']['cik'],r['identity']['annual_end'],f['field']) for r in doc['rows'] for f in r['fields']}
        self.assertEqual(len(keys),398)
        self.assertEqual(doc,json.loads((shared.ROOT/'docs/retained-income-sweep-ledger.json').read_text()))
        self.assertEqual(doc,sweep.build()[0])
        self.assertEqual(sum(doc['outcomes'].values()),398)
        self.assertEqual(doc['summary']['XOM']['slots'],0)
        self.assertEqual(doc['summary']['GEV']['periods'],2);self.assertEqual(doc['summary']['SNDK']['periods'],2)

    def test_every_new_value_independently_matches_original_xml(self):
        count=0
        for history in self.histories.values():
            for annual in history.annuals:
                for v in annual.inputs:
                    if v.field not in income.POLICIES:
                        self.assertIsNone(v.value);self.assertFalse(v.sources);continue
                    if v.value is None:continue
                    for observation in (v,*v.alternatives):
                        for ref in observation.sources:
                            root=ET.fromstring(ref.receipt.artifact.body)
                            fact=list(root)[ref.occurrence_ordinal]
                            self.assertEqual(fact.tag,'{'+ref.namespace+'}'+ref.concept)
                            self.assertEqual(fact.get('contextRef'),ref.context_id)
                            self.assertEqual(fact.text,ref.raw_value)
                            self.assertEqual(Decimal(fact.text),observation.value)
                            self.assertEqual(fact.get('decimals'),observation.precision)
                            self.assertEqual(hashlib.sha256(ref.receipt.artifact.body).hexdigest(),ref.receipt.artifact.sha256)
                            self.assertEqual((observation.unit,observation.scale,observation.sign),('USD',1,1))
                            count+=1
        self.assertGreater(count,0)

    def test_missing_body_receipt_and_no_direct_are_distinct(self):
        baseline=json.loads(subprocess.check_output(['git','show','5d4f3808584a2712a054978420ca80bcbdb19c3f:docs/retained-income-sweep-ledger.json'],cwd=shared.ROOT))
        outcomes=baseline['outcomes']
        for status in ('MISSING_RETAINED_BODY','INSUFFICIENT_IDENTITY_BINDING'):
            self.assertGreater(outcomes.get(status,0),0)
        populated=next(r for r in self.ledger['rows'] if not r['reused'] and r.get('retained_source') and any(f['outcome']=='POPULATED' for f in r['fields']))
        selected=next(r for r in self.manifest['rows'] if r['identity']==populated['identity'])
        url=sweep.expected_reference(selected,self.refs)['url']
        changed=[(p,i,dict(a,retrieved_at_utc=None)) if a['source_url']==url else (p,i,a) for p,i,a in self.refs]
        _,_,_,fields=sweep.inspect_row(selected,changed,self.config)
        self.assertTrue(all(f['outcome']=='MISSING_RECEIPT' for f in fields))
        _,_,_,fields=sweep.inspect_row(selected,[],self.config)
        self.assertTrue(all(f['outcome']=='MISSING_RETAINED_BODY' for f in fields))
        # A usable instance with no eligible direct fact differs from no body.
        from valuation_platform.analyst import retained_components as components
        evidence,_,_,_=sweep.inspect_row(selected,self.refs,self.config)
        empty=replace(evidence,facts=())
        result=income.inspect(empty,h.Field.EBIT,sweep.LIMITATIONS)
        self.assertEqual(result.candidates,());self.assertIsNone(income.choose(result,h.Field.EBIT)[0])

    def test_conflicting_candidates_and_duplicate_sources_not_precedence(self):
        selected=next(r for r in self.manifest['rows'] if r['ticker']=='QCOM')
        evidence,results,_,_=sweep.inspect_row(selected,self.refs,self.config)
        result=results[h.Field.REVENUE];c=result.candidates[0]
        conflict=replace(result,candidates=(c,replace(c,value=c.value+1)),competing_values=(c.value,c.value+1))
        slot=batch.slot(h.Field.REVENUE,conflict,evidence)
        self.assertEqual(slot['status'],'CONFLICTING');self.assertEqual(len(slot['candidates']),2)
        url=sweep.expected_reference(selected,self.refs)['url'];ref=next(x for x in self.refs if x[2]['source_url']==url)
        with self.assertRaises(h.InputError):sweep.inspect_row(selected,self.refs+[ref],self.config)

    def test_derived_ebit_reference_not_direct_population(self):
        for name in ('LLY','JNJ','MRK','KLAC','IBM'):
            rows=[r for r in self.ledger['rows'] if r['issuer']==name]
            self.assertEqual(len(rows),5)
            for r in rows:
                self.assertEqual(r['existing_derived_ebit_reference']['policy_id'],'operating_income_component_derivation')
                self.assertNotEqual(next(f for f in r['fields'] if f['field']=='ebit')['outcome'],'POPULATED')

    def test_backlog_deduplicated_and_unknown_identity_not_fabricated(self):
        backlog=self.ledger['acquisition_backlog']
        keys={(r['identity']['cik'],r['identity']['accession']) for r in backlog}
        self.assertEqual(len(keys),len(backlog))
        for r in backlog:
            self.assertTrue(r['identity']['accession']);self.assertTrue(r['fields'])
        self.assertEqual(len(self.ledger['identity_backlog']),10)
        for r in self.ledger['identity_backlog']:
            self.assertIsNone(r['identity']['accession']);self.assertIsNone(r['identity']['annual_start'])

    def test_receipt_gap_does_not_bypass_original_body_digest(self):
        selected=next(r for r in self.manifest['rows'] if r['ticker']=='V')
        url=sweep.expected_reference(selected,self.refs)['url']
        changed=[(p,i,dict(a,sha256='0'*64)) if a['source_url']==url else (p,i,a) for p,i,a in self.refs]
        with self.assertRaisesRegex(h.InputError,'digest'):sweep.inspect_row(selected,changed,self.config)

    def test_serialization_and_frozen_existing_artifacts(self):
        for name in ('QCOM','JNJ','GOOGL'):
            history=self.histories[name];serialized=h.serialize(history)
            self.assertEqual(h.serialize(h.deserialize(serialized)),serialized)
        paths=[shared.MANIFEST,'docs/universe/phase-1h5-issuer-validation.json',
            'docs/retained-income-batch-ledger.json','docs/nvda-retained-income-ledger.json',
            'src/valuation_platform/analyst/pilot_historical_inputs.py',
            'src/valuation_platform/analyst/historical_inputs.py',
            'src/valuation_platform/analyst/retained_components.py',
            'src/valuation_platform/normalization/concepts.py']
        for path in paths:
            assert_preserved(self, shared.ROOT, path, HEAD)


if __name__=='__main__':unittest.main()
