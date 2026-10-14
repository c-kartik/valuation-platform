"""Existing accounting-policy replay, not operating-tax acceptance."""
from dataclasses import replace
from decimal import Decimal, localcontext
import json
import base64
import subprocess
import unittest
from types import SimpleNamespace
from valuation_platform.analyst import retained_reported_tax as t, retained_bridge_components as b
from valuation_platform.analyst import historical_inputs as h, retained_cfo_preparation as cfo
from tests.analyst import test_prepared_assembly as shared

BASE='a10505f5cac930a97411f4f7019dd5e4637ac32c'


class ReportedTaxPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if hasattr(shared.PreparedAssemblyTests,'histories'):
            cls.histories=shared.PreparedAssemblyTests.histories
        else:
            # Tax replay needs existing source parents, not a second replay of
            # unrelated D&A/claims. Assembly preservation is tested separately.
            _,parents=cfo.build()
            cls.histories={name:SimpleNamespace(bundle=p,instant=tuple(b.overlay(cfo.prepare(a))[0]
                for a in p.annuals) if name=='ORCL' else ()) for name,p in parents.items()}
        cls.ledger,cls.overlays=t.build(cls.histories)
        cls.msft=cls.overlays['MSFT'][-1]
        cls.e=cfo.prepare(cls.histories['MSFT'].bundle.annuals[-1])

    def test_all_199_identities_replay_and_components_reconcile_separately(self):
        self.assertEqual(self.ledger,json.loads((shared.a.ROOT/t.LEDGER).read_text()))
        self.assertEqual((len(self.ledger['rows']),len(self.overlays)),(199,42))
        expected={a.period.accession for p in self.histories.values() for a in p.bundle.annuals}
        self.assertEqual({r['identity']['accession'] for r in self.ledger['rows']},expected)
        for counts in self.ledger['summary'].values():self.assertEqual(sum(counts.values()),199)
        self.assertFalse(self.overlays['XOM'])
        for ticker in ('GEV','SNDK'):self.assertEqual(len(self.overlays[ticker]),2)
        self.assertFalse(any(v.period.cik in h.SPECIALIZED_CIKS for entries in self.overlays.values() for v in entries))

    def test_independently_reviewed_pilot_provision_and_distinct_cash_roles(self):
        # Literal provision values from committed selected-filing evidence reviews,
        # not expectations generated from the adapter or assembled output.
        expected={'MSFT':{ '2025-06-30':'21795000000','2026-06-30':'32185000000'},
                  'AAPL':{'2025-09-27':'20719000000'},'GOOGL':{'2024-12-31':'19697000000'}}
        for ticker,periods in expected.items():
            for end,value in periods.items():
                v=next(o for o in self.overlays[ticker] if str(o.period.annual_end)==end)
                self.assertEqual(v.provision.value,Decimal(value))
                self.assertEqual(v.provision.sources[0].concept,'IncomeTaxExpenseBenefit')
                self.assertIn('not cash taxes',t.LIMITS[0])
                self.assertTrue(v.provision.sources)

    def test_exact_operands_occurrences_policy_and_etr_arithmetic(self):
        for entries in self.overlays.values():
            for v in entries:
                ratio=json.loads(v.etr_json)
                self.assertEqual(ratio['unit'],'pure')
                if ratio['value'] is not None:
                    self.assertIsNotNone(v.provision.value);self.assertNotEqual(v.pretax.value,0)
                    with localcontext() as ctx:
                        ctx.prec=34
                        self.assertEqual(Decimal(ratio['value']),v.provision.value/v.pretax.value)
                for operand in (v.provision,v.pretax):
                    for source in operand.sources:
                        self.assertEqual(source.period,v.period);self.assertEqual(source.unit,'USD')
                        self.assertEqual((source.start,source.end),(v.period.annual_start,v.period.annual_end))
                        self.assertEqual(Decimal(source.raw_value),operand.value)
                        self.assertFalse(source.dimensions)

    def test_zero_negative_denominator_duplicates_conflicts_and_unit_date_guards(self):
        p=t.PRETAX_INCOME_POLICY.candidates[0].name
        f,i=next((f,i) for f,i in self.e.facts if f.concept==p and f.start==self.e.period.annual_start and not f.dimensions)
        other=tuple((x,j) for x,j in self.e.facts if x.concept!=p)
        def with_value(value):return replace(self.e,facts=other+((replace(f,numeric_value=Decimal(value),raw_value=value),i),))
        v,_=t.package(with_value('0'));self.assertEqual(json.loads(v.etr_json)['reason'],'zero_derivation_denominator')
        v,_=t.package(with_value('-1'));self.assertEqual(json.loads(v.etr_json)['diagnostics'],['negative_denominator'])
        v,_=t.package(replace(self.e,facts=other+((f,i),(f,i+100000))))
        self.assertEqual(len(v.pretax.sources),2)
        v,_=t.package(replace(self.e,facts=other+((f,i),(replace(f,numeric_value=Decimal('1'),raw_value='1'),i+100000))))
        self.assertIsNone(v.pretax.value);self.assertIsNone(json.loads(v.etr_json)['value'])
        c=self.e.contexts[f.context_id]
        v,_=t.package(replace(self.e,facts=other+((f,i),),contexts=dict(self.e.contexts,**{c.context_id:replace(c,end=c.end.replace(day=29))})))
        self.assertIsNone(v.pretax.value)
        with self.assertRaises(h.InputError):t.package(replace(self.e,facts=other+((replace(f,decimals='invalid'),i),)))
        with self.assertRaises(h.InputError):t.package(replace(self.e,facts=other+((replace(f,unit=None),i),)))

    def test_serialization_replays_and_tampering_fails_closed(self):
        for ticker in ('MSFT','AAPL','GOOGL','CVX','MA'):
            v=self.overlays[ticker][-1]
            self.assertEqual(t.deserialize(t.serialize(v)),v)
        with self.assertRaises(h.InputError):t.serialize(replace(self.msft,etr_json='{}'))
        with self.assertRaises(h.InputError):t.serialize(replace(self.msft,provision=replace(self.msft.provision,value=Decimal(1))))
        doc=json.loads(t.serialize(self.msft));doc['schema']='unregistered'
        with self.assertRaises(h.InputError):t.deserialize(json.dumps(doc))
        doc=json.loads(t.serialize(self.msft));key=next(iter(doc['original_bodies']))
        doc['original_bodies'][key]={'bytes':base64.b64encode(b'changed retained body').decode()}
        with self.assertRaises(h.InputError):t.deserialize(json.dumps(doc))

    def test_exact_curated_matching_and_unavailable_metadata_not_fabricated(self):
        for v in self.overlays['CVX']:
            if json.loads(v.proof_json).get('curated_pretax'):
                proof=json.loads(v.proof_json)['curated_pretax']
                self.assertIn('pretax_scope',json.dumps(proof))
                self.assertEqual(json.loads(v.etr_json)['curated_operand_provenance'],proof)
        for v in self.overlays['MA']:
            proof=json.loads(v.proof_json)
            if proof['evidence_gaps']:
                self.assertIsNone(v.pretax.value);self.assertIsNone(json.loads(v.etr_json)['value'])

    def test_independent_orcl_borrowing_and_reusable_noncurrent_rule(self):
        p=self.histories['ORCL'];overlay=p.instant[-1]
        v=next(v for v in overlay.debt_leases if v.role=='noncurrent_notes_loans_carrying')
        # Independently inspected retained primary balance-sheet row333, USD m.
        self.assertEqual(v.value,Decimal('122342000000'));self.assertEqual(v.as_of,overlay.period.annual_end)
        self.assertEqual(v.sources[0].concept,'LongTermNotesAndLoans')
        self.assertIn('Lease inclusion',v.scope);self.assertIn('possible_overlap:',v.flags[-1])
        self.assertIs(v.completeness,h.Completeness.PARTIAL)
        e=cfo.prepare(p.bundle.annuals[-1]);f,i=next((f,i) for f,i in e.facts if f.concept=='LongTermNotesAndLoans' and f.end==e.period.annual_end and not f.dimensions)
        c=e.contexts[f.context_id]
        for context in (replace(c,start=e.period.annual_start),replace(c,end=c.end.replace(day=30))):
            values,rows,errors=b.inspect(replace(e,facts=((f,i),),contexts={c.context_id:context}),h.Field.DEBT_LEASES)
            self.assertFalse(values)

    def test_previous_pilot_frozen_and_other_ledger_bytes_preserved(self):
        paths=list(shared.a.LEDGERS)
        paths=[p for p in paths if p!=b.LEDGER]
        paths+=['docs/pilot-historical-input-mappings.json','src/valuation_platform/analyst/historical_inputs.py']
        paths += subprocess.check_output(['git','ls-files','src/valuation_platform/normalization','tests/fixtures'],cwd=shared.a.ROOT,text=True).splitlines()
        for path in paths:self.assertEqual((shared.a.ROOT/path).read_bytes(),subprocess.check_output(['git','show',BASE+':'+path],cwd=shared.a.ROOT),path)
        old=json.loads(subprocess.check_output(['git','show',BASE+':'+b.LEDGER],cwd=shared.a.ROOT))
        new=json.loads((shared.a.ROOT/b.LEDGER).read_text())
        self.assertEqual(len(old['rows']),len(new['rows']))
        for before,after in zip(old['rows'],new['rows']):
            self.assertEqual(before['identity'],after['identity'])
            for field in b.FIELDS:
                original=before['fields'][field.value]['observations']
                retained=[r for r in after['fields'][field.value]['observations'] if r['concept']!='LongTermNotesAndLoans']
                self.assertEqual(original,retained)


if __name__=='__main__':unittest.main()
