"""Fixed NVDA source replay, independent raw-instance checks and typed gaps."""
import base64
from dataclasses import replace
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET

from valuation_platform.analyst import historical_inputs as h, retained_components as r
from valuation_platform.analyst import retained_income_preparation as income, nvda_income_inputs as n
from valuation_platform.analyst.cash_flow_inputs import _receipt, CashFlowInputError
from valuation_platform.sec.filing_xbrl import FilingXBRLDataError

ROOT=Path(__file__).resolve().parents[2]
HEAD='20c32606a5c333e9a62339657970c1e29de4fc80'
XI='{http://www.xbrl.org/2003/instance}'


class NvdaIncomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifacts=n.pinned(n.BODIES,n.BODIES_SHA256)['artifacts']
        cls.rows=n.selections();cls.ledger,cls.history=n.build()
        cls.expected=[('2022-01-30','26914000000','10041000000',4,2),('2023-01-29','26974000000','4224000000',4,2),
            ('2024-01-28','60922000000','32972000000',4,2),('2025-01-26','130497000000','81453000000',4,2),
            ('2026-01-25','215938000000','130387000000',3,1)]

    def changed(self,transform):
        row=self.rows[0][1];e,_,_=n.inspect_period(row,self.artifacts);old=e.instance
        body=transform(old.artifact.body.decode()).encode()
        receipt=replace(old,artifact=replace(old.artifact,body=body,sha256=hashlib.sha256(body).hexdigest()),byte_length=len(body))
        return r.prepare(e.period,(receipt,),(r.ArtifactBinding(receipt.artifact.url,receipt.artifact.sha256,'instance'),))

    def ebit(self,body):
        return re.search(r'<us-gaap:OperatingIncomeLoss\b[^>]*>10041000000</us-gaap:OperatingIncomeLoss>',body).group()

    def test_five_identities_and_ten_slots_reconcile(self):
        self.assertEqual(len(self.ledger['rows']),5)
        self.assertEqual(sum(len(row['fields']) for row in self.ledger['rows']),10)
        self.assertEqual(len({a.period.accession for a in self.history.annuals}),5)
        for (index,entry),row,annual in zip(self.rows,self.ledger['rows'],self.history.annuals):
            self.assertEqual(row['identity'],entry['identity']);self.assertEqual(annual.period,n.period(entry['identity']))
            self.assertEqual(row['identity_reference'],n.MANIFEST+'#/rows/'+str(index))
            self.assertTrue(all(s['status']=='POPULATED_REPORTED_DIRECT' for s in row['fields']))
        self.assertEqual(self.ledger,json.loads((ROOT/'docs/nvda-retained-income-ledger.json').read_text()))

    def test_all_values_independently_bind_original_instance(self):
        for annual,(end,revenue,ebit,nr,ne) in zip(self.history.annuals,self.expected):
            self.assertEqual(str(annual.period.annual_end),end)
            a=next(a for a in self.artifacts if a['accession']==annual.period.accession and a['source_url'].endswith('_htm.xml'))
            body=gzip.decompress(base64.b64decode(a['response_body_gzip_base64'],validate=True));root=ET.fromstring(body)
            contexts={c.attrib['id']:c for c in root.findall(XI+'context')}
            for field,expected,count in [(h.Field.REVENUE,revenue,nr),(h.Field.EBIT,ebit,ne)]:
                value=next(v for v in annual.inputs if v.field is field)
                self.assertEqual(value.value,Decimal(expected));self.assertEqual((value.unit,value.scale,value.sign,value.precision),('USD',1,1,'-6'))
                obs=(value,*value.alternatives)
                self.assertEqual(sum(len(v.sources) for v in obs),count)
                for v in obs:
                    for ref in v.sources:
                        f=list(root)[ref.occurrence_ordinal];c=contexts[ref.context_id]
                        self.assertEqual(f.tag,'{'+ref.namespace+'}'+ref.concept)
                        self.assertEqual(f.text,ref.raw_value);self.assertEqual(Decimal(f.text),Decimal(expected))
                        self.assertEqual(f.get('contextRef'),ref.context_id);self.assertEqual(f.get('decimals'),ref.decimals)
                        self.assertEqual(c.findtext(XI+'period/'+XI+'startDate'),str(annual.period.annual_start))
                        self.assertEqual(c.findtext(XI+'period/'+XI+'endDate'),end)
                        self.assertEqual(int(c.findtext(XI+'entity/'+XI+'identifier')),1045810)
                        self.assertFalse(c.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'))
                        self.assertEqual(ref.receipt.retrieved_at_utc,a['retrieved_at_utc'])
                        self.assertEqual(ref.receipt.http_status,200)
                        self.assertEqual(hashlib.sha256(ref.receipt.artifact.body).hexdigest(),a['sha256'])

    def test_two_approved_revenue_representations_preserved_and_precedence_logged(self):
        value=next(v for v in self.history.annuals[0].inputs if v.field is h.Field.REVENUE)
        self.assertEqual(value.sources[0].concept,'RevenueFromContractWithCustomerExcludingAssessedTax')
        self.assertEqual(len(value.sources),3);self.assertEqual(len(value.alternatives),1)
        self.assertEqual(value.alternatives[0].sources[0].concept,'Revenues')
        self.assertIn('policy order',value.selection_rationale)
        self.assertIs(value.completeness,h.Completeness.PARTIAL)

    def test_other_twelve_families_are_not_claimed_searched(self):
        for annual in self.history.annuals:
            unassessed=[v for v in annual.inputs if v.field not in income.POLICIES]
            self.assertEqual(len(unassessed),12)
            for value in unassessed:
                self.assertIsNone(value.value);self.assertFalse(value.sources)
                self.assertIs(value.review,h.Review.UNREVIEWED);self.assertIs(value.quality,h.Quality.UNASSESSED)
                self.assertIn('unassessed',value.null_reason)
                self.assertIsNone(value.formula);self.assertIsNone(value.manual)
                self.assertTrue(value.unresolved_requirements)

    def test_missing_receipts_or_bodies_are_explicit_not_guessed(self):
        row=self.rows[0][1];a=next(a for a in self.artifacts if a['source_url']==row['candidates'][0]['artifacts'][0]['url'])
        for changed in [None,dict(a,retrieved_at_utc=None),dict(a,response_body_gzip_base64=None)]:
            artifacts=[changed if x is a else x for x in self.artifacts] if changed else [x for x in self.artifacts if x is not a]
            e,results,_=n.inspect_period(row,artifacts);annual=income.annual(e,results,n.LIMITATIONS)
            self.assertFalse(e.receipts)
            self.assertTrue(e.unresolved_requirements)
            self.assertTrue(all(v.value is None for v in annual.inputs))

    def test_conflicts_and_duplicate_confirmations(self):
        for replacement,conflicting in [('10041000000',False),('10042000000',True)]:
            e=self.changed(lambda body:body.replace('</xbrl>',self.ebit(body).replace('10041000000',replacement)+'</xbrl>'))
            result=income.inspect(e,h.Field.EBIT,n.LIMITATIONS)
            selected,_=income.choose(result,h.Field.EBIT)
            if conflicting:
                self.assertIsNone(selected);self.assertEqual(len(result.candidates),2)
                annual=income.annual(e,{f:income.inspect(e,f,n.LIMITATIONS) for f in income.POLICIES},n.LIMITATIONS)
                value=next(v for v in annual.inputs if v.field is h.Field.EBIT)
                self.assertIsNone(value.value);self.assertEqual(len(value.alternatives),2)
            else:self.assertEqual(len(result.candidates[0].occurrences),3)

    def test_date_context_and_dimensions_mismatches_stay_missing(self):
        original=n.inspect_period(self.rows[0][1],self.artifacts)[0]
        c0=income.inspect(original,h.Field.EBIT,n.LIMITATIONS).candidates[0].occurrences[0].context_id
        other=next(c.context_id for c in original.contexts.values() if c.start is None)
        e=self.changed(lambda body:re.sub(r'<us-gaap:OperatingIncomeLoss\b[^>]*>10041000000</us-gaap:OperatingIncomeLoss>',
            lambda m:m.group().replace('contextRef="'+c0+'"','contextRef="'+other+'"'),body))
        self.assertFalse(income.inspect(e,h.Field.EBIT,n.LIMITATIONS).candidates)
        with self.assertRaises(CashFlowInputError):
            receipt=original.instance
            r.prepare(replace(original.period,annual_start=original.period.annual_start.replace(day=2)),(receipt,),
                (r.ArtifactBinding(receipt.artifact.url,receipt.artifact.sha256,'instance'),))

    def test_unit_precision_and_namespace_mismatches_fail_conservatively(self):
        e=n.inspect_period(self.rows[0][1],self.artifacts)[0]
        o=income.inspect(e,h.Field.EBIT,n.LIMITATIONS).candidates[0].occurrences[0]
        for old,new in [('decimals="-6"','decimals="bad"'),('unitRef="'+o.unit_id+'"','unitRef="missing"'),
                        ('contextRef="'+o.context_id+'"','contextRef="missing"')]:
            with self.assertRaises((h.InputError,FilingXBRLDataError)):
                changed=self.changed(lambda body:body.replace(self.ebit(body),self.ebit(body).replace(old,new)))
                income.inspect(changed,h.Field.EBIT,n.LIMITATIONS)

    def test_serialization_deterministic_and_tampered_sign_rejected(self):
        payload=h.serialize(self.history);restored=h.deserialize(payload)
        self.assertEqual(restored,self.history);self.assertEqual(h.serialize(restored),payload)
        del payload,restored
        v=self.history.annuals[0].inputs[0]
        with self.assertRaises(h.InputError):replace(v,sign=-1)
        with self.assertRaises(h.InputError):replace(v,period=replace(v.period,accession='0001045810-22-000037'))

    def test_original_sources_policies_and_pilot_artifacts_unchanged(self):
        for path in (n.MANIFEST,n.BODIES,'src/valuation_platform/analyst/retained_components.py',
            'src/valuation_platform/analyst/pilot_historical_inputs.py','src/valuation_platform/analyst/historical_inputs.py',
            'src/valuation_platform/normalization/concepts.py','docs/pilot-historical-input-mappings.json',
            'docs/company-data-preparation/msft-reported-cash-flow-bundles.json','docs/company-data-preparation/aapl-reported-cash-flow-bundle.json',
            'docs/company-data-preparation/googl-reported-cash-flow-bundle.json'):
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=ROOT))


if __name__=='__main__':unittest.main()
