"""Reconciliation roles and exact sources, never financial treatment approval."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
from valuation_platform.analyst import retained_tax_sbc as t, retained_working_capital as w
from valuation_platform.analyst import retained_cfo_preparation as cfo, retained_components as r
from valuation_platform.analyst import historical_inputs as h, pilot_historical_inputs as p, nvda_income_inputs as shared

HEAD='076c9974313145491f10d2acf53873089fae7c6f'


class TaxSBCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.histories=t.build()
        cls.a=p.load_history('AAPL').annuals[0];cls.e=cfo.prepare(cls.a)
        cls.f,cls.i=next((f,i) for f,i in cls.e.facts if f.concept=='ShareBasedCompensation'
            and f.start==cls.a.period.annual_start and f.end==cls.a.period.annual_end and not f.dimensions)

    def test_199_periods_two_independent_field_outcomes_and_replay(self):
        x=self.ledger
        self.assertEqual((x['selected_periods'],x['issuer_count']),(199,42))
        self.assertEqual(len({(v['identity']['cik'],v['identity']['accession']) for v in x['rows']}),199)
        self.assertEqual(x,json.loads((shared.ROOT/'docs/retained-tax-sbc-ledger.json').read_text()))
        for field in t.FIELDS:self.assertEqual(sum(x['outcomes'][field.value].values()),199)
        self.assertEqual(len(x['history_exceptions']),11);self.assertFalse(self.histories['XOM'].annuals)
        for name in ('GEV','SNDK'):self.assertEqual(len(self.histories[name].annuals),2)
        self.assertFalse(any(a.period.cik in h.SPECIALIZED_CIKS for v in self.histories.values() for a in v.annuals))

    def test_explicit_signs_positive_negative_and_actual_mixed_cash_sign(self):
        for rule in t.RULES:
            expected=-1 if rule.concept=='OtherNoncashIncomeExpense' else 1
            self.assertEqual(rule.sign,expected)
            for raw in (Decimal('15'),Decimal('-15')):
                fact=replace(self.f,concept=rule.concept,raw_value=str(raw),numeric_value=raw)
                values,rows,errors=t.inspect(replace(self.e,facts=((fact,self.i),)),rule.field)
                self.assertFalse(errors);self.assertEqual(len(values),1)
                self.assertEqual((values[0].value,values[0].sign),(raw*expected,expected))
                self.assertEqual(rows[0]['candidates'][0]['raw_value'],str(raw))
        for name,expected in (('AAPL',Decimal('-89000000')),('GOOGL',Decimal('3419000000'))):
            a=p.load_history(name).annuals[0]
            values,_,_=t.inspect(cfo.prepare(a),h.Field.DEFERRED_TAX)
            self.assertEqual(next(v.value for v in values if v.role=='unallocated_other_noncash_support'),expected)

    def test_provision_balance_cash_working_capital_and_awards_cannot_populate_reconciliation(self):
        for concept in ('DeferredIncomeTaxExpenseBenefit','IncomeTaxesPaidNet','IncomeTaxExpenseBenefit',
                        'DeferredIncomeTaxAssetsNet','IncreaseDecreaseInDeferredIncomeTaxes'):
            fact=replace(self.f,concept=concept)
            values,row=t.package(replace(self.e,facts=((fact,self.i),)),h.Field.DEFERRED_TAX)
            self.assertEqual(row['status'],'UNAVAILABLE');self.assertIsNone(values[0].value)
        for concept in ('AllocatedShareBasedCompensationExpense','PaymentsRelatedToTaxWithholdingForShareBasedCompensation',
                        'PaymentsForRepurchaseOfCommonStock','ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodGross'):
            fact=replace(self.f,concept=concept)
            values,row=t.package(replace(self.e,facts=((fact,self.i),)),h.Field.SBC)
            self.assertEqual(row['status'],'UNAVAILABLE')
        extension=replace(self.f,namespace='http://example.com/issuer')
        evidence=replace(self.e,facts=((extension,self.i),))
        self.assertEqual(t.package(evidence,h.Field.SBC)[1]['status'],'UNAVAILABLE')
        self.assertEqual(t.diagnostics(evidence)[0]['disposition'],'UNSUPPORTED_EXTENSION')
        arbitrary=replace(self.f,concept='SomeOtherShareBasedCompensationCombinedCaption')
        self.assertFalse(t.inspect(replace(self.e,facts=((arbitrary,self.i),)),h.Field.SBC)[0])

    def test_combined_credit_caption_and_expense_roles_nonadditive(self):
        combined=replace(self.f,concept='DeferredIncomeTaxesAndTaxCredits')
        provision=replace(self.f,concept='DeferredIncomeTaxExpenseBenefit',raw_value='17',numeric_value=Decimal('17'))
        values,row=t.package(replace(self.e,facts=((combined,self.i),(provision,self.i+10000))),h.Field.DEFERRED_TAX)
        self.assertEqual(row['status'],'POPULATED');self.assertEqual(len(values),2)
        self.assertTrue(row['observations'][0]['combined']);self.assertEqual(values[0].scope_status,h.Scope.MIXED)
        self.assertNotEqual(values[0].role,values[1].role)
        self.assertTrue(all(v.formula is None and v.completeness is h.Completeness.PARTIAL for v in values))
        note=replace(self.f,concept='AllocatedShareBasedCompensationExpense',raw_value='22800000000',numeric_value=Decimal('22800000000'),decimals='-8')
        addback=replace(self.f,raw_value='22785000000',numeric_value=Decimal('22785000000'),decimals='-6')
        values,row=t.package(replace(self.e,facts=((note,self.i),(addback,self.i+10000))),h.Field.SBC)
        self.assertEqual(row['status'],'POPULATED');self.assertEqual(len(values),2)
        self.assertEqual({v.precision for v in values},{'-6','-8'});self.assertFalse(any(v.alternatives for v in values))

    def test_duplicates_conflicts_and_precision_alternatives(self):
        f=self.f;i=self.i
        values,row=t.package(replace(self.e,facts=((f,i),(f,i+10000))),h.Field.SBC)
        self.assertEqual(row['status'],'POPULATED');self.assertEqual(len(values[0].sources),2)
        changed=replace(f,raw_value='1',numeric_value=Decimal('1'))
        values,row=t.package(replace(self.e,facts=((f,i),(changed,i+10000))),h.Field.SBC)
        self.assertEqual(row['status'],'CONFLICTING');self.assertIsNone(values[0].value)
        self.assertEqual(len(values[0].alternatives),2)
        precise=replace(f,decimals='INF')
        values,row=t.package(replace(self.e,facts=((f,i),(precise,i+10000))),h.Field.SBC)
        self.assertEqual(row['status'],'POPULATED');self.assertEqual(values[0].alternatives[0].precision,'INF')

    def test_dates_entity_units_nil_precision_missing_and_scope_exclusions(self):
        for bad in (replace(self.f,unit=None),replace(self.f,decimals=None),replace(self.f,is_nil=True)):
            values,row=t.package(replace(self.e,facts=((bad,self.i),)),h.Field.SBC)
            self.assertEqual(row['status'],'UNAVAILABLE');self.assertTrue(row['errors'])
        context=self.e.contexts[self.f.context_id]
        for bad in (replace(context,start=None),replace(context,end=context.start),replace(context,entity_identifier='999')):
            evidence=replace(self.e,contexts={**self.e.contexts,self.f.context_id:bad},facts=((self.f,self.i),))
            self.assertEqual(t.package(evidence,h.Field.SBC)[1]['status'],'UNAVAILABLE')
        empty=r.prepare(self.a.period,(),(r.ArtifactBinding(self.e.instance.artifact.url,self.e.instance.artifact.sha256,'instance'),))
        self.assertEqual(t.package(empty,h.Field.SBC)[1]['status'],'UNAVAILABLE')
        # Original-byte dimensions/currency/annual guards are covered by the
        # unchanged shared inspector regression suite, run alongside this one.

    def test_new_values_independently_match_xml_source_roles_units_precision(self):
        count=0
        for history in self.histories.values():
            for a in history.annuals:
                for value in a.inputs:
                    if not value.input_id.startswith('retained-tax-sbc:') or value.value is None:continue
                    for v in (value,*value.alternatives):
                        for s in v.sources:
                            fact=list(ET.fromstring(s.receipt.artifact.body))[s.occurrence_ordinal]
                            self.assertEqual(fact.tag,'{'+s.namespace+'}'+s.concept)
                            self.assertEqual((fact.get('contextRef'),fact.get('decimals')),(s.context_id,v.precision))
                            self.assertEqual(Decimal(fact.text)*v.sign,v.value)
                            self.assertEqual((s.start,s.end),(a.period.annual_start,a.period.annual_end))
                            self.assertFalse(s.dimensions);self.assertEqual((v.unit,v.scale),('USD',1))
                            self.assertEqual(hashlib.sha256(s.receipt.artifact.body).hexdigest(),s.receipt.artifact.sha256)
                            count+=1
        self.assertGreater(count,200)

    def test_serialization_independent_replay_rejects_role_or_evidence_change(self):
        a=self.histories['NVDA'].annuals[-1]
        history=replace(self.histories['NVDA'],annuals=(a,),history_exceptions=('Test one original selected period only.',))
        payload=h.serialize(history)
        self.assertEqual(payload,h.serialize(t.validate_history(payload)))
        v=next(v for v in a.inputs if v.field is h.Field.SBC and v.value is not None)
        altered=replace(history,annuals=(replace(a,inputs=tuple(replace(v,role='certified_economic_cost') if x==v else x for x in a.inputs)),))
        with self.assertRaises(h.InputError):t.validate_history(h.serialize(altered))

    def test_pilot_precision_and_all_existing_fields_and_artifacts_preserved(self):
        for name in ('AAPL','MSFT','GOOGL'):
            for a in p.load_history(name).annuals:
                self.assertEqual(a,next(v for v in self.histories[name].annuals if v.period==a.period))
        googl=p.load_history('GOOGL').annuals[0]
        sbc={v.role:(v.value,v.precision) for v in googl.inputs if v.field is h.Field.SBC}
        self.assertEqual(sbc['sbc_cfo_addback'],(Decimal('22785000000'),'-6'))
        self.assertEqual(sbc['sbc_note_expense'],(Decimal('22800000000'),'-8'))
        _,baseline=w.build()
        for name,history in baseline.items():
            for a in history.annuals:
                new=next(v for v in self.histories[name].annuals if v.period==a.period)
                self.assertEqual(tuple(v for v in a.inputs if v.field not in t.FIELDS),tuple(v for v in new.inputs if v.field not in t.FIELDS))
        for path in ('docs/retained-working-capital-ledger.json','docs/retained-cfo-ledger.json','docs/repaired-income-ledger.json',
            'docs/pilot-historical-input-mappings.json','src/valuation_platform/analyst/historical_inputs.py'):
            self.assertEqual((shared.ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=shared.ROOT))
