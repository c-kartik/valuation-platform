"""Approved D&A replay versus non-additive support, not a coverage target."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import subprocess
import unittest
from valuation_platform.analyst import retained_d_and_a as d,historical_inputs as h
from valuation_platform.analyst import refreshed_capex as parent,retained_cfo_preparation as cfo,retained_components as inspect
from valuation_platform.analyst import pilot_historical_inputs as pilots

HEAD='78b15277293d35442eb178b962a44713a8271881'


class RetainedDAndATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.parents,cls.overlays=d.build();cls.store=d.artifact_store()
        cls.a=cls.overlays['AAPL'][-1]
        cls.e=inspect.prepare(cls.a.period,(cls.a.receipt,),
            (inspect.ArtifactBinding(cls.a.receipt.artifact.url,cls.a.receipt.artifact.sha256,'instance'),))

    def test_199_approved_and_support_counts_independent(self):
        self.assertEqual(self.ledger,json.loads((d.capex.shared.ROOT/d.LEDGER).read_text()))
        self.assertEqual(self.ledger['outcomes'],dict(DIRECT=98,DERIVED_APPROVED=5,CURATED=5,UNAPPROVED_SCOPE_COMPLETENESS=84,SCOPE_DOWNGRADED=7))
        self.assertEqual((self.ledger['selected_periods'],self.ledger['issuer_count'],self.ledger['support_periods'],self.ledger['support_observations']),(199,42,199,1327))
        self.assertEqual(len(self.ledger['history_exceptions']),11);self.assertFalse(self.overlays['XOM'])
        self.assertEqual(len(self.overlays['GEV']),2);self.assertEqual(len(self.overlays['SNDK']),2)
        self.assertEqual(self.ledger['evidence_backlog'],[])
        self.assertTrue(all(not r['support_complete'] for r in self.ledger['rows']))

    def test_actual_raw_values_contexts_precision_and_occurrences(self):
        import xml.etree.ElementTree as ET
        for entries in self.overlays.values():
            for a in entries:
                root=ET.fromstring(a.receipt.artifact.body)
                for v in (a.required_value,*a.support_only,*a.operands):
                    for source in v.sources:
                        self.assertEqual(source.receipt,a.receipt)
                        fact=list(root)[source.occurrence_ordinal]
                        self.assertEqual(fact.tag,'{'+source.namespace+'}'+source.concept)
                        self.assertEqual(fact.text,source.raw_value)
                        self.assertEqual((fact.get('contextRef'),fact.get('decimals')),(source.context_id,source.decimals))
                        if v.origin is h.Origin.REPORTED:self.assertEqual(Decimal(source.raw_value)*v.sign*v.scale,v.value)
                        self.assertEqual(hashlib.sha256(source.receipt.artifact.body).hexdigest(),source.receipt.artifact.sha256)

    def test_generic_duplicate_conflict_unit_context_and_precision(self):
        fact,ordinal=next((f,i) for f,i in self.e.facts if f.concept==d.DIRECT and not f.dimensions and f.start==self.e.period.annual_start)
        duplicate=replace(self.e,facts=((fact,ordinal),(fact,ordinal+10000)))
        overlay,row=d.package(duplicate,self.store)
        self.assertEqual(row['status'],'DIRECT');self.assertEqual(len(overlay.required_value.sources),2)
        different=replace(fact,raw_value='1',numeric_value=Decimal('1'))
        overlay,row=d.package(replace(self.e,facts=((fact,ordinal),(different,ordinal+10000))),self.store)
        self.assertEqual(row['status'],'CONFLICTING');self.assertIsNone(overlay.required_value.value)
        precision=replace(fact,decimals='INF')
        overlay,row=d.package(replace(self.e,facts=((fact,ordinal),(precision,ordinal+10000))),self.store)
        self.assertEqual(row['status'],'DIRECT');self.assertEqual(overlay.required_value.alternatives[0].precision,'INF')
        for bad in (replace(fact,unit=None),replace(fact,is_nil=True)):
            self.assertIsNone(d.package(replace(self.e,facts=((bad,ordinal),)),self.store)[0].required_value.value)
        context=self.e.contexts[fact.context_id]
        for bad in (replace(context,end=context.start),replace(context,entity_identifier='999')):
            e=replace(self.e,contexts={**self.e.contexts,fact.context_id:bad},facts=((fact,ordinal),))
            self.assertIsNone(d.package(e,self.store)[0].required_value.value)

    def test_msft_existing_equation_only_and_no_generic_sum(self):
        for a in self.overlays['MSFT']:
            v=a.required_value;self.assertEqual(v.origin,h.Origin.DERIVED)
            self.assertEqual(v.formula.formula_id,'msft_annual_d_and_a_v1')
            self.assertEqual(v.value,sum(o.value for o in a.operands))
            self.assertEqual([o.sources[0].concept for o in a.operands],['Depreciation','AmortizationOfIntangibleAssets'])
            self.assertEqual(json.loads(a.policy_json)['source_kind'],'filing_xbrl')
        for name in ('GOOGL','AMD','TXN','AVGO','MRK'):
            for a in self.overlays[name]:
                self.assertIsNone(a.required_value.value);self.assertFalse(a.operands)
                self.assertTrue(a.support_only);self.assertTrue(all(v.formula is None for v in a.support_only))

    def test_curated_five_actual_artifacts_and_missing_proof(self):
        for a in self.overlays['V']:
            proof=json.loads(a.policy_json);self.assertEqual(proof['policy_id'],'d_and_a_scope_equivalence');self.assertEqual(proof['version'],'1')
            self.assertEqual(len(proof['d_and_a_scope']['verified_artifact_digests']),9)
            self.assertTrue(proof['d_and_a_scope']['supporting_facts'])
            e=inspect.prepare(a.period,(a.receipt,),(inspect.ArtifactBinding(a.receipt.artifact.url,a.receipt.artifact.sha256,'instance'),))
            entry=next(e for e in d.curated.D_AND_A_SCOPE_EQUIVALENCE_POLICY.entries if e.accession_number==a.period.accession)
            absent=dict(self.store);del absent[entry.artifact_digests[-1]]
            overlay,row=d.package(e,absent);self.assertEqual(row['status'],'EVIDENCE_GAP')
            self.assertIsNone(overlay.required_value.value);self.assertEqual(len(row['approved_entry_evidence_gaps']),1)
            changed=replace(e,period=replace(e.period,accession='0001403161-27-999999'))
            with self.assertRaises(ValueError):d.package(changed,self.store)

    def test_mixed_scope_extension_and_component_observations_remain_support(self):
        roles={v.role for aa in self.overlays.values() for a in aa for v in a.support_only}
        self.assertTrue(any('impairment' in r for r in roles));self.assertTrue(any('accretion' in r for r in roles))
        self.assertTrue(any('lease' in r for r in roles));self.assertTrue(any('issuer_extension_unapproved' in r for r in roles))
        self.assertTrue(all('support_only' in v.flags and v.completeness is h.Completeness.PARTIAL
            for aa in self.overlays.values() for a in aa for v in a.support_only))

    def test_serialization_replay_nulls_and_tampering_rejection(self):
        for name in ('AAPL','MSFT','V','GOOGL'):
            a=self.overlays[name][-1];s=d.serialize(a)
            self.assertEqual(s,d.serialize(d.deserialize(s)))
            with self.assertRaises(h.InputError):d.serialize(replace(a,policy_json='{}'))
            with self.assertRaises(h.InputError):d.deserialize(s.replace(d.SCHEMA,'unregistered',1))
        absent,row=d.package(replace(self.e,instance=None),self.store)
        self.assertEqual(row['status'],'EVIDENCE_GAP');self.assertIsNone(absent.required_value.value)
        self.assertEqual(d.deserialize(d.serialize(absent)),absent)

    def test_original_parents_pilots_capex_v2_and_frozen_artifacts_preserved(self):
        _,original=parent.build()
        self.assertEqual(original,self.parents)
        for name in ('AAPL','MSFT','GOOGL'):
            for a in pilots.load_history(name).annuals:
                self.assertEqual(a,next(v for v in self.parents[name].annuals if v.period==a.period))
        for path in ['src/valuation_platform/normalization/concepts.py','src/valuation_platform/normalization/derived.py',
            'src/valuation_platform/normalization/d_and_a_scope.py','src/valuation_platform/normalization/d_and_a_scope_registry.json',
            'src/valuation_platform/normalization/models.py','src/valuation_platform/normalization/output.py',
            'docs/refreshed-capex-ledger.json','docs/retained-tax-sbc-ledger.json','docs/retained-working-capital-ledger.json',
            'docs/retained-cfo-ledger.json','docs/pilot-historical-input-mappings.json']:
            self.assertEqual((d.capex.shared.ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=d.capex.shared.ROOT))
