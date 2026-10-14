"""One parameterized retained-only pass: facts, scope, exceptions and preservation."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from tests.analyst.preparation_preservation import assert_preserved
import xml.etree.ElementTree as ET
from valuation_platform.analyst import retained_cfo_preparation as cfo, historical_inputs as h
from valuation_platform.analyst import pilot_historical_inputs as pilot, nvda_income_inputs as shared

HEAD='cae308100800bd64dfd7ed6b7397eb116c034b40'


class RetainedCFOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ledger,cls.histories=cfo.build()

    def sample(self):
        a=self.histories['QCOM'].annuals[-1]
        return a,cfo.prepare(a)

    def test_199_unique_slots_42_issuers_history_exceptions_and_replay(self):
        ledger=self.ledger
        self.assertEqual((ledger['selected_periods'],ledger['issuer_count']),(199,42))
        self.assertEqual(ledger['outcomes'],dict(POPULATED=195,UNAVAILABLE=4))
        self.assertEqual(len({(r['identity']['cik'],r['identity']['accession']) for r in ledger['rows']}),199)
        self.assertEqual(ledger,json.loads((shared.ROOT/'docs/retained-cfo-ledger.json').read_text()))
        self.assertEqual(ledger,cfo.build()[0]);self.assertFalse(ledger['artifact_exceptions'])
        self.assertEqual(len(ledger['history_exceptions']),11)
        self.assertEqual(self.histories['XOM'].annuals,());self.assertTrue(self.histories['XOM'].history_exceptions)
        self.assertEqual(len(self.histories['GEV'].annuals),2);self.assertEqual(len(self.histories['SNDK'].annuals),2)
        self.assertFalse(any(a.period.cik in h.SPECIALIZED_CIKS for x in self.histories.values() for a in x.annuals))

    def test_all_new_populated_values_independently_match_actual_xml(self):
        count=0
        for history in self.histories.values():
            for annual in history.annuals:
                value=next(v for v in annual.inputs if v.field is h.Field.CFO)
                if value.value is None or not value.input_id.startswith('retained-cfo:'):continue
                self.assertIn('cfo_reconciliation_not_validated',value.flags)
                self.assertEqual(value.scope_status,h.Scope.CONSOLIDATED_REPORTED)
                for candidate in (value,*value.alternatives):
                    for source in candidate.sources:
                        root=ET.fromstring(source.receipt.artifact.body);f=list(root)[source.occurrence_ordinal]
                        context=next(c for c in root.findall('{http://www.xbrl.org/2003/instance}context') if c.get('id')==source.context_id)
                        self.assertEqual(f.tag,'{'+source.namespace+'}'+source.concept)
                        self.assertEqual(f.get('contextRef'),source.context_id)
                        self.assertEqual(f.get('decimals'),candidate.precision)
                        self.assertEqual(Decimal(f.text),candidate.value)
                        self.assertEqual(context.findtext('{http://www.xbrl.org/2003/instance}period/{http://www.xbrl.org/2003/instance}startDate'),str(annual.period.annual_start))
                        self.assertEqual(context.findtext('{http://www.xbrl.org/2003/instance}period/{http://www.xbrl.org/2003/instance}endDate'),str(annual.period.annual_end))
                        self.assertFalse(source.dimensions);self.assertEqual((candidate.unit,candidate.scale,candidate.sign),('USD',1,1))
                        self.assertEqual(hashlib.sha256(source.receipt.artifact.body).hexdigest(),source.receipt.artifact.sha256)
                        count+=1
        self.assertGreaterEqual(count,191)

    def test_scope_alternatives_never_substitute_or_sum(self):
        a,e=self.sample();fact,index=next((f,i) for f,i in e.facts if f.concept==cfo.CONCEPT and f.start==a.period.annual_start and f.end==a.period.annual_end and not f.dimensions)
        scoped=replace(fact,concept=cfo.CONCEPT+'ContinuingOperations')
        synthetic=replace(e,facts=((fact,index),(scoped,index+10000)))
        result,error=cfo.inspect(synthetic);value,status,_=cfo.select(synthetic,result,error)
        self.assertEqual(status,'POPULATED');self.assertEqual(value.value,fact.numeric_value)
        self.assertEqual(len(value.alternatives),1);self.assertIn('non_substitutable_scope_alternative',value.alternatives[0].flags)
        only=replace(e,facts=((scoped,index),));result,error=cfo.inspect(only);value,status,_=cfo.select(only,result,error)
        self.assertEqual(status,'UNAVAILABLE');self.assertIsNone(value.value);self.assertEqual(len(value.alternatives),1)

    def test_duplicates_conflicting_values_and_precision_representations(self):
        a,e=self.sample();fact,index=next((f,i) for f,i in e.facts if f.concept==cfo.CONCEPT and f.start==a.period.annual_start and f.end==a.period.annual_end and not f.dimensions)
        duplicate=replace(e,facts=((fact,index),(fact,index+10000)))
        result,error=cfo.inspect(duplicate);value,status,_=cfo.select(duplicate,result,error)
        self.assertEqual(status,'POPULATED');self.assertEqual(len(value.sources),2)
        conflict=replace(fact,raw_value=str(fact.numeric_value+1),numeric_value=fact.numeric_value+1)
        changed=replace(e,facts=((fact,index),(conflict,index+10000)))
        result,error=cfo.inspect(changed);value,status,_=cfo.select(changed,result,error)
        self.assertEqual(status,'CONFLICTING');self.assertIsNone(value.value);self.assertEqual(len(value.alternatives),2)
        precision=replace(fact,decimals='INF')
        changed=replace(e,facts=((fact,index),(precision,index+10000)))
        result,error=cfo.inspect(changed);value,status,_=cfo.select(changed,result,error)
        self.assertEqual(status,'POPULATED');self.assertEqual(value.alternatives[0].precision,'INF')

    def test_dates_dimension_unit_precision_and_missing_receipts(self):
        a,e=self.sample()
        contexts={k:replace(c,start=None) for k,c in e.contexts.items()}
        changed=replace(e,contexts=contexts);result,error=cfo.inspect(changed);value,status,_=cfo.select(changed,result,error)
        self.assertEqual(status,'UNAVAILABLE')
        fact,index=next((f,i) for f,i in e.facts if f.concept==cfo.CONCEPT and f.start==a.period.annual_start and f.end==a.period.annual_end and not f.dimensions)
        for bad in (replace(fact,unit=None),replace(fact,decimals=None),replace(fact,is_nil=True)):
            changed=replace(e,facts=((bad,index),));result,error=cfo.inspect(changed);value,status,_=cfo.select(changed,result,error)
            self.assertEqual(status,'UNAVAILABLE');self.assertIn('invalid unit/nil/numeric/precision',value.null_reason)
        changed=replace(e,unresolved_requirements=('Missing retained instance body: test',))
        result,error=cfo.inspect(changed);_,status,_=cfo.select(changed,result,error);self.assertEqual(status,'UNAVAILABLE')
        # Dimension and exact annual mismatch guards have original-byte mutation
        # coverage in the existing shared inspection suite, run with these tests.

    def test_specific_unavailable_slots_not_zero_or_disclosure_absence(self):
        actual={(r['issuer'],r['identity']['annual_end']) for r in self.ledger['rows'] if r['status']=='UNAVAILABLE'}
        self.assertEqual(actual,{('MRK','2021-12-31'),('MRK','2022-12-31'),('MRK','2023-12-31'),('LIN','2021-12-31')})
        for r in self.ledger['rows']:
            if r['status']=='UNAVAILABLE':self.assertIsNone(r['value_usd']);self.assertTrue(r['unresolved_requirements'])

    def test_income_results_and_pilot_values_artifacts_preserved(self):
        income=json.loads((shared.ROOT/'docs/repaired-income-ledger.json').read_text())
        for old,new in zip(income['rows'],self.ledger['rows']):self.assertEqual(old['fields'],new['income_fields'])
        self.assertEqual(self.ledger['income_outcomes'],income['outcomes'])
        self.assertEqual(sum(len(r['fields']) for r in self.ledger['unresolved_income_reviews']),16)
        for name in ('MSFT','AAPL','GOOGL'):
            for a in pilot.load_history(name).annuals:
                new=next(v for v in self.histories[name].annuals if v.period==a.period);self.assertEqual(new,a)
        for path in ('docs/repaired-income-ledger.json','docs/pilot-historical-input-mappings.json','src/valuation_platform/analyst/historical_inputs.py',
            'src/valuation_platform/normalization/operating_income_derivation.py'):
            assert_preserved(self, shared.ROOT, path, HEAD)

    def test_serialization_replay_and_actual_fact_tampering_rejected(self):
        history=self.histories['QCOM'];one=replace(history,annuals=(history.annuals[-1],),history_exceptions=('Single-period test, not additional registration.',))
        payload=h.serialize(one);self.assertEqual(h.serialize(cfo.validate_history(payload)),payload)
        annual=one.annuals[0];value=next(v for v in annual.inputs if v.field is h.Field.CFO)
        changed=replace(value,value=value.value+1,sources=tuple(replace(s,raw_value=str(Decimal(s.raw_value)+1)) for s in value.sources))
        changed_annual=replace(annual,inputs=tuple(changed if v.field is h.Field.CFO else v for v in annual.inputs))
        with self.assertRaises(h.InputError):cfo.validate_history(h.serialize(replace(one,annuals=(changed_annual,))))


if __name__=='__main__':unittest.main()
