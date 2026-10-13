"""One parameterized batch suite: identities, original facts, gaps and replay."""
import base64
from dataclasses import replace
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET
from valuation_platform.analyst import retained_income_batch as b, retained_income_preparation as income
from valuation_platform.analyst import nvda_income_inputs as n, historical_inputs as h, retained_components as r

ROOT=Path(__file__).resolve().parents[2]
HEAD='3289ba191e17bc6b78e3b061f3530557bd4b5ad6'
XI='{http://www.xbrl.org/2003/instance}'


class RetainedIncomeBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.histories=b.build();cls.refs=b.catalog()

    def test_forty_exact_selections_eighty_slots_and_replay(self):
        selections=b.selections()
        self.assertEqual(len(selections),40);self.assertEqual(self.ledger['field_period_slots'],80)
        self.assertEqual(self.ledger,json.loads((ROOT/'docs/retained-income-batch-ledger.json').read_text()))
        self.assertEqual(self.ledger,b.build()[0])
        expected={name:(10,0,0) for name in b.ISSUERS}
        for name,c in self.ledger['summary'].items():
            self.assertEqual((c['populated'],c['conflicting'],c['unavailable']),expected[name])
            self.assertEqual(c['selected_periods'],5)
        for (i,selection),row in zip(selections,self.ledger['rows']):
            self.assertEqual(row['identity'],selection['identity'])
            self.assertEqual(row['identity_reference'],n.MANIFEST+'#/rows/'+str(i))
            self.assertEqual(row['expected_instance'],b.instance_reference(selection))
            self.assertEqual({s['field'] for s in row['fields']},{'revenue','ebit'})

    def test_every_populated_observation_independently_matches_original_fact(self):
        total=0
        for name,history in self.histories.items():
            for annual in history.annuals:
                for v in annual.inputs:
                    if v.value is None:continue
                    for observation in (v,*v.alternatives):
                        for ref in observation.sources:
                            original=next(a for _,_,a in self.refs if a['source_url']==ref.receipt.artifact.url)
                            encoded=original['response_body_gzip_base64']
                            if isinstance(encoded,list):encoded=''.join(encoded)
                            body=gzip.decompress(base64.b64decode(encoded,validate=True));root=ET.fromstring(body)
                            f=list(root)[ref.occurrence_ordinal]
                            context=next(c for c in root.findall(XI+'context') if c.get('id')==ref.context_id)
                            self.assertEqual(f.tag,'{'+ref.namespace+'}'+ref.concept)
                            self.assertEqual(Decimal(f.text),observation.value)
                            self.assertEqual(f.text,ref.raw_value);self.assertEqual(f.get('decimals'),observation.precision)
                            self.assertEqual(f.get('contextRef'),ref.context_id)
                            self.assertEqual(context.findtext(XI+'period/'+XI+'startDate'),str(annual.period.annual_start))
                            self.assertEqual(context.findtext(XI+'period/'+XI+'endDate'),str(annual.period.annual_end))
                            self.assertEqual(int(context.findtext(XI+'entity/'+XI+'identifier')),annual.period.cik)
                            self.assertFalse(context.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'))
                            unit=next(u for u in root.findall(XI+'unit') if u.get('id')==f.get('unitRef'))
                            self.assertTrue(unit.findtext(XI+'measure').endswith(':USD'))
                            self.assertEqual((observation.unit,observation.scale,observation.sign),('USD',1,1))
                            self.assertEqual(ref.receipt.retrieved_at_utc,original['retrieved_at_utc'])
                            self.assertEqual(ref.receipt.retrieval_mode,original['retrieval_mode'])
                            self.assertEqual(hashlib.sha256(body).hexdigest(),original['sha256'])
                            total+=1
        self.assertEqual(total,197)

    def test_negative_income_and_precision_not_converted_to_millions(self):
        pltr=self.histories['PLTR']
        self.assertEqual([next(v.value for v in a.inputs if v.field is h.Field.EBIT) for a in pltr.annuals[:2]],
            [Decimal('-411046000'),Decimal('-161201000')])
        for name in ('PLTR','NFLX'):
            for annual in self.histories[name].annuals:
                self.assertTrue(all(v.precision=='-3' for v in annual.inputs if v.value is not None))

    def test_missing_retained_evidence_is_not_missing_disclosure(self):
        baseline=json.loads(subprocess.check_output(['git','show','3bf319eda79b9c5e3e855f134ebb82d496cb004a:docs/retained-income-batch-ledger.json'],cwd=ROOT))
        missing=[row for row in baseline['rows'] if row['retained_source'] is None]
        self.assertEqual(len(missing),13)
        self.assertEqual({row['issuer'] for row in missing},{'AMZN','AVGO','AMAT'})
        for row in missing:
            self.assertTrue(all(s['status']=='UNAVAILABLE' and not s['candidates'] for s in row['fields']))
            self.assertTrue(all(any('Missing retained instance body' in req for req in s['unresolved_requirements']) for s in row['fields']))
        for history in self.histories.values():
            for annual in history.annuals:
                others=[v for v in annual.inputs if v.field not in income.POLICIES]
                self.assertEqual(len(others),12)
                self.assertTrue(all(v.value is None and v.review is h.Review.UNREVIEWED and not v.sources for v in others))

    def test_duplicate_source_and_incomplete_receipt_are_not_silent_precedence(self):
        row=next(row for _,row in b.selections() if row['ticker']=='CSCO');url=b.instance_reference(row)['url']
        ref=next(x for x in self.refs if x[2]['source_url']==url)
        with self.assertRaises(h.InputError):b.inspect_row(row,self.refs+[ref])
        changed=[(p,i,dict(a,retrieved_at_utc=None)) if a['source_url']==url else (p,i,a) for p,i,a in self.refs]
        evidence,results,_=b.inspect_row(row,changed)
        self.assertFalse(evidence.receipts)
        self.assertTrue(all(b.slot(f,result,evidence)['status']=='UNAVAILABLE' for f,result in results.items()))

    def test_financial_conflict_retains_candidates_and_null_output(self):
        row=next(row for _,row in b.selections() if row['ticker']=='PLTR')
        evidence,results,_=b.inspect_row(row,self.refs)
        result=results[h.Field.EBIT];c=result.candidates[0]
        # Retained candidate inspection semantics already have source-mutation tests;
        # exercise the common batch disposition and packaging without issuer copies.
        other=replace(c,value=c.value+Decimal('1000'))
        conflicting=replace(result,candidates=(c,other),competing_values=(c.value,other.value))
        slot=b.slot(h.Field.EBIT,conflicting,evidence)
        self.assertEqual(slot['status'],'CONFLICTING');self.assertIsNone(slot['selected'])
        self.assertEqual(len(slot['candidates']),2)
        self.assertIn('cannot override',slot['selection_rationale'])
        # Do not pass a fabricated source representation to models: their guards
        # independently reject a value that disagrees with its retained raw facts.
        with self.assertRaises(h.InputError):income.annual(evidence,results | {h.Field.EBIT:conflicting},b.LIMITATIONS)

    def test_serialization_all_eight_histories_and_nvda_bytes(self):
        for history in self.histories.values():
            payload=h.serialize(history);restored=h.deserialize(payload)
            self.assertEqual(restored,history);self.assertEqual(h.serialize(restored),payload)
            del payload,restored
        payload=h.serialize(n.load_history())
        self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(),'ea438857acb1485479b65390cdfdd45bc47eb313e522797e75ec31de6c6d0f52')

    def test_frozen_sources_policies_mappings_preserved(self):
        originals=tuple(path for path in b.SOURCES if path!='docs/evidence/retained-income-instance-acquisition.json')
        for path in (n.MANIFEST,n.BODIES,*originals,'docs/nvda-retained-income-ledger.json',
            'src/valuation_platform/analyst/retained_income_preparation.py','src/valuation_platform/analyst/retained_components.py',
            'src/valuation_platform/analyst/historical_inputs.py','src/valuation_platform/analyst/pilot_historical_inputs.py',
            'src/valuation_platform/normalization/concepts.py','docs/pilot-historical-input-mappings.json'):
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=ROOT))


if __name__=='__main__':unittest.main()
