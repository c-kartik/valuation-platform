"""Real retained policy replay, not frozen-value import or synthetic approvals."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
from valuation_platform.analyst import retained_capex as c, retained_tax_sbc as prior
from valuation_platform.analyst import historical_inputs as h, retained_cfo_preparation as cfo
from valuation_platform.analyst import pilot_historical_inputs as p, nvda_income_inputs as shared
from valuation_platform.normalization.models import NormalizedHistoricalValue, AmbiguousHistoricalMetric, EvidenceSourceKind

HEAD='acb2af1dffbdd6a5b71cb608de2f087f8f8118e9'


class RetainedArtifactRepresentationTests(unittest.TestCase):
    def test_rejects_relabelled_or_missing_representation_without_hash_bypass(self):
        original=Path.read_bytes
        for label in ('parsed_json_utf8_bytes',None):
            def changed(path):
                raw=original(path)
                if path.name=='capex_amzn_response_bodies.json':
                    doc=json.loads(raw);doc[0]['representation']=label
                    return json.dumps(doc).encode()
                return raw
            with patch.object(Path,'read_bytes',changed):
                with self.assertRaises(h.InputError):c.artifacts()
        self.assertTrue(c.artifacts())  # Actual declared types and hashes all verify.


class RetainedCapexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.histories=c.build();cls.store=c.artifacts()
        cls.e=cfo.prepare(p.load_history('AAPL').annuals[0])
        cls.f,cls.i=next((f,i) for f,i in cls.e.facts if f.concept==c.DIRECT and not f.dimensions
            and (f.start,f.end)==(cls.e.period.annual_start,cls.e.period.annual_end))

    def test_scope_outcomes_exact_identities_and_offline_replay(self):
        x=self.ledger
        self.assertEqual((x['selected_periods'],x['issuer_count']),(199,42));self.assertEqual(sum(x['outcomes'].values()),199)
        self.assertEqual(x['outcomes'],dict(DIRECT=145,CURATED=5,EVIDENCE_GAP=15,UNAPPROVED_SCOPE=34))
        self.assertEqual(x['curated_versions'],{'3':5})
        self.assertEqual(x,json.loads((shared.ROOT/'docs/retained-capex-ledger.json').read_text()))
        self.assertEqual(len({(v['identity']['cik'],v['identity']['accession']) for v in x['rows']}),199)
        self.assertEqual(len(x['history_exceptions']),11);self.assertFalse(self.histories['XOM'].annuals)
        for name in ('GEV','SNDK'):self.assertEqual(len(self.histories[name].annuals),2)

    def test_exact_direct_resolver_sign_and_confirming_occurrences(self):
        v,row=c.package(self.e,self.store)
        self.assertEqual((v.value,v.sign,v.scale),(Decimal('-12715000000'),-1,1))
        result,_=c.direct_result(self.e)
        self.assertEqual(result.chosen_source.source_kind,EvidenceSourceKind.FILING_XBRL)
        duplicate=replace(self.e,facts=((self.f,self.i),(self.f,self.i+10000)))
        v,row=c.package(duplicate,self.store)
        self.assertEqual(row['status'],'DIRECT');self.assertEqual(len(v.sources),2)
        other=replace(self.f,decimals='INF')
        v,row=c.package(replace(self.e,facts=((self.f,self.i),(other,self.i+10000))),self.store)
        self.assertEqual(row['status'],'DIRECT');self.assertEqual(v.alternatives[0].precision,'INF')
        conflict=replace(self.f,raw_value='1',numeric_value=Decimal('1'))
        v,row=c.package(replace(self.e,facts=((self.f,self.i),(conflict,self.i+10000))),self.store)
        self.assertEqual(row['status'],'CONFLICTING');self.assertIsNone(v.value);self.assertEqual(len(v.alternatives),2)

    def test_exact_dates_entity_namespace_units_nil_and_non_integral_projection(self):
        context=self.e.contexts[self.f.context_id]
        for bad in (replace(context,start=None),replace(context,end=context.start),replace(context,entity_identifier='999')):
            e=replace(self.e,contexts={**self.e.contexts,self.f.context_id:bad},facts=((self.f,self.i),))
            self.assertIsNone(c.package(e,self.store)[0].value)
        for bad in (replace(self.f,namespace='http://example.org/issuer'),replace(self.f,unit=None),
                    replace(self.f,is_nil=True),replace(self.f,decimals=None),
                    replace(self.f,raw_value='0.12345',numeric_value=Decimal('0.12345'))):
            self.assertIsNone(c.package(replace(self.e,facts=((bad,self.i),)),self.store)[0].value)
        negative=replace(self.f,raw_value='-1',numeric_value=Decimal('-1'))
        v,row=c.package(replace(self.e,facts=((negative,self.i),)),self.store)
        self.assertIsNone(v.value);self.assertIn('Negative',v.null_reason)

    def test_all_applicable_versions_real_artifact_gates_and_no_implicit_software_approval(self):
        rows=self.ledger['rows']
        for issuer,count,version in (('AMZN',5,'1'),('LLY',5,'1'),('CVX',5,'2')):
            actual=[r for r in rows if r['issuer']==issuer]
            self.assertEqual(len(actual),count)
            for row in actual:
                self.assertEqual(row['status'],'EVIDENCE_GAP');self.assertEqual(row['policy']['registered_version'],version)
                self.assertTrue(row['approved_entry_evidence_gaps'])
        for a in self.histories['V'].annuals:
            v=next(v for v in a.inputs if v.field is h.Field.CAPEX)
            proof=json.loads(next(f[len(c.PROOF):] for f in v.flags if f.startswith(c.PROOF)))
            self.assertEqual(proof['version'],'3');self.assertEqual(len(proof['reviewed_evidence']),7)
            self.assertEqual(len(proof['capex_scope']['verified_artifact_digests']),13)
            self.assertEqual(len(proof['artifact_bindings']),13)
            e=cfo.prepare(a);entry=next(entry for policy in c.curated.CAPEX_SCOPE_POLICY_CATALOG.policies for entry in policy.entries if entry.accession_number==a.period.accession)
            absent=dict(self.store);key=next(k for k in absent if k[0]==entry.reviewed_evidence[0].source_url);del absent[key]
            self.assertEqual(c.package(e,absent)[1]['status'],'EVIDENCE_GAP')
        for name in ('NVDA','LRCX','QCOM','HD','VZ','PEP'):
            self.assertTrue(all(r['status']=='UNAPPROVED_SCOPE' for r in rows if r['issuer']==name))

    def test_non_cash_acquisition_proceeds_and_broad_support_never_substitute(self):
        for concept in c.SUPPORT:
            fact=replace(self.f,concept=concept)
            v,row=c.package(replace(self.e,facts=((fact,self.i),)),{})
            self.assertIsNone(v.value);self.assertTrue(row['support'])
            self.assertTrue(all(a.role=='support_only_raw_noncapex_population' for a in v.alternatives))
            self.assertTrue(all(a.sign==1 and a.formula is None for a in v.alternatives))
        for a in self.histories['NVDA'].annuals[:2]:
            v=next(v for v in a.inputs if v.field is h.Field.CAPEX)
            diagnostics=json.loads(next(f.split(':',1)[1] for f in v.flags if f.startswith('retained_capex_support:')))
            self.assertTrue(any(d['concept']=='PurchasesOfPropertyAndEquipmentAndIntangibleAssets' for d in diagnostics))

    def test_independent_actual_xml_values_policy_proof_and_serialization(self):
        for history in self.histories.values():
            for a in history.annuals:
                v=next(v for v in a.inputs if v.field is h.Field.CAPEX)
                if not v.input_id.startswith('retained-capex:') or v.value is None:continue
                self.assertLessEqual(v.value,0)
                for s in v.sources:
                    fact=list(ET.fromstring(s.receipt.artifact.body))[s.occurrence_ordinal]
                    self.assertEqual(Decimal(fact.text)*-1,v.value)
                    self.assertEqual(fact.tag,'{'+s.namespace+'}'+s.concept)
                    self.assertEqual((fact.get('contextRef'),fact.get('decimals')),(s.context_id,v.precision))
                    self.assertFalse(s.dimensions);self.assertEqual((s.start,s.end),(a.period.annual_start,a.period.annual_end))
                    self.assertEqual(hashlib.sha256(s.receipt.artifact.body).hexdigest(),s.receipt.artifact.sha256)
        a=self.histories['V'].annuals[-1]
        one=replace(self.histories['V'],annuals=(a,),history_exceptions=('Test one existing selected period.',))
        payload=h.serialize(one);self.assertEqual(payload,h.serialize(c.validate_history(payload)))
        v=next(v for v in a.inputs if v.field is h.Field.CAPEX)
        altered=replace(one,annuals=(replace(a,inputs=tuple(replace(v,selection_rationale='unreviewed') if i==v else i for i in a.inputs)),))
        with self.assertRaises(h.InputError):c.validate_history(h.serialize(altered))

    def test_all_prior_fields_pilot_bytes_and_frozen_policy_artifacts_preserved(self):
        _,baseline=prior.build()
        for name,history in baseline.items():
            for a in history.annuals:
                new=next(v for v in self.histories[name].annuals if v.period==a.period)
                self.assertEqual(tuple(v for v in a.inputs if v.field is not h.Field.CAPEX),tuple(v for v in new.inputs if v.field is not h.Field.CAPEX))
        for name in ('MSFT','AAPL','GOOGL'):
            for a in p.load_history(name).annuals:self.assertEqual(a,next(v for v in self.histories[name].annuals if v.period==a.period))
        paths=['docs/retained-tax-sbc-ledger.json','docs/retained-working-capital-ledger.json','docs/retained-cfo-ledger.json',
            'src/valuation_platform/normalization/concepts.py','src/valuation_platform/normalization/capex_scope.py',
            'src/valuation_platform/normalization/capex_scope_registry.json','src/valuation_platform/normalization/capex_scope_v2_registry.json',
            'src/valuation_platform/normalization/capex_scope_v3_registry.json','docs/pilot-historical-input-mappings.json']
        for path in paths:self.assertEqual((shared.ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=shared.ROOT))
