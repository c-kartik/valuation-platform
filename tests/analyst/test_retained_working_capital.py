"""Bounded mapping/sign inspection, not financial scope approval."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET
from valuation_platform.analyst import retained_working_capital as w, historical_inputs as h
from valuation_platform.analyst import retained_cfo_preparation as cfo, retained_components as r
from valuation_platform.analyst import pilot_historical_inputs as p, nvda_income_inputs as shared

HEAD='a3e5c1b3b9bd24035ceb96c1cab2b03aac88f744'


class RetainedMovementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.histories=w.build()
        cls.a=cls.histories['AAPL'].annuals[-1]
        cls.e=cfo.prepare(cls.a)
        cls.f,cls.ordinal=next((f,i) for f,i in cls.e.facts if f.concept=='IncreaseDecreaseInInventories'
            and f.start==cls.a.period.annual_start and f.end==cls.a.period.annual_end and not f.dimensions)

    def test_scope_counts_history_exceptions_and_offline_replay(self):
        self.assertEqual((self.ledger['selected_periods'],self.ledger['issuer_count']),(199,42))
        self.assertEqual(len({(v['identity']['cik'],v['identity']['accession']) for v in self.ledger['rows']}),199)
        self.assertEqual(self.ledger,json.loads((shared.ROOT/'docs/retained-working-capital-ledger.json').read_text()))
        self.assertEqual(len(self.ledger['history_exceptions']),11)
        self.assertFalse(self.histories['XOM'].annuals)
        for name in ('GEV','SNDK'):self.assertEqual(len(self.histories[name].annuals),2)
        self.assertEqual(self.ledger['period_outcomes']['partial_unknown'],199)
        self.assertEqual(self.ledger['period_outcomes']['with_observations']+self.ledger['period_outcomes']['no_eligible_observations'],199)
        self.assertFalse(any(v.period.cik in h.SPECIALIZED_CIKS for x in self.histories.values() for v in x.annuals))

    def test_every_rule_positive_negative_cash_sign_and_no_arbitrary_name_fallback(self):
        asset_account_movements={
            'IncreaseDecreaseInAccountsReceivable','IncreaseDecreaseInOtherReceivables',
            'IncreaseDecreaseInReceivables','IncreaseDecreaseInAccountsAndOtherReceivables',
            'IncreaseDecreaseInInventories','IncreaseDecreaseInPrepaidExpense',
            'IncreaseDecreaseInPrepaidDeferredExpenseAndOtherAssets','IncreaseDecreaseInOtherCurrentAssets',
            'IncreaseDecreaseInOtherNoncurrentAssets','IncreaseDecreaseInOtherOperatingAssets',
            'IncreaseDecreaseInOperatingCapital'}
        for rule in w.RULES:
            expected_sign=-1 if rule.concept in asset_account_movements else 1
            self.assertEqual(rule.sign,expected_sign)
            for raw in (Decimal('21'),Decimal('-21')):
                fact=replace(self.f,concept=rule.concept,raw_value=str(raw),numeric_value=raw)
                obs,ledger,errors=w.inspect(replace(self.e,facts=((fact,self.ordinal),)))
                self.assertFalse(errors);self.assertEqual(len(obs),1)
                self.assertEqual((obs[0].value,obs[0].sign),(raw*expected_sign,expected_sign))
                self.assertEqual(ledger[0]['candidates'][0]['raw_value'],str(raw))
                self.assertEqual(obs[0].completeness,h.Completeness.PARTIAL)
        unknown=replace(self.f,concept='IncreaseDecreaseInInventedOperatingAsset')
        ee=replace(self.e,facts=((unknown,self.ordinal),))
        self.assertFalse(w.inspect(ee)[0]);self.assertIsNone(w.unsupported(ee)[0]['normalized_sign'])
        extension=replace(self.f,namespace='http://example.org/issuer')
        ee=replace(self.e,facts=((extension,self.ordinal),))
        self.assertFalse(w.inspect(ee)[0]);self.assertEqual(w.unsupported(ee)[0]['disposition'],'UNSUPPORTED_EXTENSION')

    def test_actual_retained_aapl_inventory_negative_asset_movement_is_positive_cash(self):
        obs,_,_=w.inspect(self.e)
        value=next(v for v in obs if v.sources[0].concept=='IncreaseDecreaseInInventories')
        self.assertEqual(value.sources[0].raw_value,'-1400000000')
        self.assertEqual((value.value,value.sign),(Decimal('1400000000'),-1))
        for name in ('MSFT','GOOGL'):
            for a in self.histories[name].annuals:
                if any(v.field is h.Field.CF_WORKING_CAPITAL and v.value is not None and not v.input_id.startswith('retained-cf-movement:') for v in a.inputs):
                    evidence=cfo.prepare(a);inspected=w.inspect(evidence)[0]
                    for original in (v for v in a.inputs if v.field is h.Field.CF_WORKING_CAPITAL and v.value is not None):
                        if original.sources[0].namespace!=evidence.namespaces['us-gaap']:
                            self.assertTrue(any(v['concept']==original.sources[0].concept and v['disposition']=='UNSUPPORTED_EXTENSION'
                                for v in w.unsupported(evidence)))
                            continue  # Preserve reviewed extension, never reapprove generically.
                        same=[v for v in inspected if v.sources[0].concept==original.sources[0].concept]
                        self.assertTrue(same);self.assertEqual(same[0].value,original.value)

    def test_all_new_values_independently_replay_original_xml_and_precision(self):
        count=0;positive=negative=0
        for history in self.histories.values():
            for a in history.annuals:
                for value in a.inputs:
                    if not value.input_id.startswith('retained-cf-movement:') or value.value is None:continue
                    for v in (value,*value.alternatives):
                        for s in v.sources:
                            root=ET.fromstring(s.receipt.artifact.body);fact=list(root)[s.occurrence_ordinal]
                            self.assertEqual(fact.tag,'{'+s.namespace+'}'+s.concept)
                            self.assertEqual(fact.get('contextRef'),s.context_id)
                            self.assertEqual(Decimal(fact.text)*w.RULE_BY_CONCEPT[s.concept].sign,v.value)
                            self.assertEqual(fact.get('decimals'),v.precision)
                            self.assertEqual((s.start,s.end),(a.period.annual_start,a.period.annual_end))
                            self.assertFalse(s.dimensions);self.assertEqual(v.unit,'USD')
                            self.assertEqual(hashlib.sha256(s.receipt.artifact.body).hexdigest(),s.receipt.artifact.sha256)
                            count+=1;positive+=v.value>0;negative+=v.value<0
        self.assertGreater(count,500);self.assertGreater(positive,0);self.assertGreater(negative,0)

    def test_duplicates_conflicts_precision_and_parent_child_observations_never_sum(self):
        f=self.f;i=self.ordinal
        obs,rows,_=w.inspect(replace(self.e,facts=((f,i),(f,i+10000))))
        self.assertEqual(len(obs[0].sources),2);self.assertEqual(len(rows[0]['candidates'][0]['occurrences']),2)
        changed=replace(f,raw_value='123',numeric_value=Decimal('123'))
        obs,rows,_=w.inspect(replace(self.e,facts=((f,i),(changed,i+10000))))
        self.assertIsNone(obs[0].value);self.assertEqual(len(obs[0].alternatives),2)
        self.assertEqual(rows[0]['status'],'CONFLICTING')
        precise=replace(f,decimals='INF')
        obs,_,_=w.inspect(replace(self.e,facts=((f,i),(precise,i+10000))))
        self.assertEqual(obs[0].alternatives[0].precision,'INF')
        parent=replace(f,concept='IncreaseDecreaseInAccountsPayableAndAccruedLiabilities')
        child=replace(f,concept='IncreaseDecreaseInAccountsPayable')
        obs,rows,_=w.inspect(replace(self.e,facts=((parent,i),(child,i+10000))))
        self.assertEqual(len(obs),2);self.assertTrue(all(v.formula is None for v in obs))
        self.assertIn(child.concept,next(v for v in rows if v['concept']==parent.concept)['possible_children'])
        self.assertTrue(all(v.scope_status is h.Scope.MIXED for v in obs))

    def test_exact_dates_contexts_currency_precision_dimensions_and_missing_evidence(self):
        f=self.f;i=self.ordinal
        for bad in (replace(f,unit=None),replace(f,decimals=None),replace(f,is_nil=True)):
            obs,_,errors=w.inspect(replace(self.e,facts=((bad,i),)))
            self.assertTrue(errors);self.assertIsNone(obs[0].value)
        context=self.e.contexts[f.context_id]
        for bad in (replace(context,start=None),replace(context,entity_identifier='999'),replace(context,end=context.start)):
            ee=replace(self.e,contexts={**self.e.contexts,f.context_id:bad},facts=((f,i),))
            self.assertFalse(w.inspect(ee)[0])
        empty=r.prepare(self.a.period,(),(r.ArtifactBinding(self.e.instance.artifact.url,self.e.instance.artifact.sha256,'instance'),))
        self.assertFalse(w.inspect(empty)[0]);self.assertTrue(empty.unresolved_requirements)
        # Original-byte dimensional/unit/date mismatch cases are also exercised
        # by test_retained_components with this focused suite.

    def test_serialization_roundtrip_and_independent_evidence_mismatch_rejected(self):
        a=self.histories['NVDA'].annuals[-1]
        history=replace(self.histories['NVDA'],annuals=(a,),history_exceptions=('Test selected one original annual only.',))
        payload=h.serialize(history)
        self.assertEqual(payload,h.serialize(history));self.assertEqual(history,w.validate_history(payload))
        value=next(v for v in a.inputs if v.input_id.startswith('retained-cf-movement:') and v.value is not None)
        changed=replace(value,selection_rationale='Tampered unreviewed selection')
        altered=replace(history,annuals=(replace(a,inputs=tuple(changed if v==value else v for v in a.inputs)),))
        with self.assertRaises(h.InputError):w.validate_history(h.serialize(altered))

    def test_pilots_all_other_fields_and_frozen_original_artifacts_preserved(self):
        for name in ('MSFT','AAPL','GOOGL'):
            for a in p.load_history(name).annuals:
                self.assertEqual(a,next(v for v in self.histories[name].annuals if v.period==a.period))
        _,baseline=cfo.build()
        for name,history in baseline.items():
            for a in history.annuals:
                new=next(v for v in self.histories[name].annuals if v.period==a.period)
                self.assertEqual(tuple(v for v in a.inputs if v.field is not h.Field.CF_WORKING_CAPITAL),
                    tuple(v for v in new.inputs if v.field is not h.Field.CF_WORKING_CAPITAL))
        paths=['docs/pilot-historical-input-mappings.json','docs/retained-cfo-ledger.json','docs/repaired-income-ledger.json']
        for path in paths:
            self.assertEqual((shared.ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=shared.ROOT))
