"""Exact instant observations and unknown perimeters, never financial totals."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
from valuation_platform.analyst import retained_bridge_components as b
from valuation_platform.analyst import historical_inputs as h, retained_components as r
from valuation_platform.analyst import pilot_historical_inputs as pilot

HEAD='1220bd2ee2edaa3867de7eb7ba8066f5554a3b96'
ROOT=b.parent.capex.shared.ROOT


class RetainedBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.parents,cls.overlays=b.build()
        cls.a=cls.overlays['AAPL'][-1]
        cls.e=r.prepare(cls.a.period,(cls.a.receipt,),
            (r.ArtifactBinding(cls.a.receipt.artifact.url,cls.a.receipt.artifact.sha256,'instance'),))
        cls.fact,cls.ordinal=next((f,i) for f,i in cls.e.facts if f.concept=='CashAndCashEquivalentsAtCarryingValue'
            and cls.e.contexts[f.context_id].start is None and f.end==cls.a.period.annual_end and not f.dimensions)

    def test_complete_scope_offline_ledger_and_two_separate_denominators(self):
        self.assertEqual(self.ledger,json.loads((ROOT/b.LEDGER).read_text()))
        self.assertEqual((self.ledger['selected_periods'],self.ledger['issuer_count']),(199,42))
        self.assertEqual(len({(v['identity']['cik'],v['identity']['accession']) for v in self.ledger['rows']}),199)
        previous=json.loads((ROOT/'docs/retained-cfo-ledger.json').read_text())
        self.assertEqual({tuple(sorted(v['identity'].items())) for v in self.ledger['rows']},
            {tuple(sorted(v['identity'].items())) for v in previous['rows']})
        self.assertEqual(self.ledger['summary'][b.FIELDS[0].value],dict(component_populations=855,
            conflicting_periods=11,outcomes=dict(CONFLICTING=11,OBSERVATIONS=188),periods_with_observations=199))
        self.assertEqual(self.ledger['summary'][b.FIELDS[1].value],dict(component_populations=2056,
            conflicting_periods=31,outcomes=dict(CONFLICTING=31,OBSERVATIONS=168),periods_with_observations=199))
        self.assertFalse(self.ledger['evidence_backlog'])
        self.assertEqual(len(self.ledger['history_exceptions']),11)
        self.assertFalse(self.overlays['XOM'])
        for name in ('GEV','SNDK'): self.assertEqual(len(self.overlays[name]),2)
        self.assertFalse(any(v.period.cik in h.SPECIALIZED_CIKS for entries in self.overlays.values() for v in entries))
        for f in b.FIELDS:
            self.assertEqual(sum(self.ledger['summary'][f.value]['outcomes'].values()),199)

    def test_actual_xml_values_occurrence_context_unit_and_precision(self):
        for entries in self.overlays.values():
            for overlay in entries:
                root=ET.fromstring(overlay.receipt.artifact.body)
                for v in (*overlay.cash_investments,*overlay.debt_leases):
                    candidates=(v,*v.alternatives) if v.value is not None else v.alternatives
                    for a in candidates:
                        for s in a.sources:
                            fact=root[s.occurrence_ordinal]
                            self.assertEqual(fact.tag,'{'+s.namespace+'}'+s.concept)
                            self.assertEqual(fact.get('contextRef'),s.context_id)
                            self.assertEqual(fact.get('unitRef'),json.loads(s.locator)['unit_id'])
                            self.assertEqual(fact.get('decimals'),a.precision)
                            self.assertEqual(Decimal(fact.text.strip()),a.value)
                            self.assertEqual(s.receipt,overlay.receipt)
                            self.assertEqual(s.end,overlay.period.annual_end)
                            self.assertIsNone(s.start); self.assertFalse(s.dimensions)
                            self.assertEqual((a.scale,a.sign,a.as_of),(1,1,overlay.period.annual_end))
                self.assertEqual(hashlib.sha256(overlay.receipt.artifact.body).hexdigest(),overlay.receipt.artifact.sha256)

    def test_independently_reviewed_pilot_statement_amounts_are_observations(self):
        expected={'MSFT':[('30242000000','2999000000'),('20935000000','9227000000')],
                  'AAPL':[('35934000000','12350000000')], 'GOOGL':[('23466000000','999000000')]}
        for name,points in expected.items():
            pilot_periods={a.period for a in pilot.load_history(name).annuals}
            overlays=[v for v in self.overlays[name] if v.period in pilot_periods]
            self.assertEqual(len(overlays),len(points))
            for value,(cash,debt) in zip(overlays,points):
                self.assertEqual(next(v.value for v in value.cash_investments if v.role=='cash_equivalents_carrying'),Decimal(cash))
                self.assertEqual(next(v.value for v in value.debt_leases if v.role=='current_long_term_debt'),Decimal(debt))

    def test_confirmations_conflicts_and_precision_alternatives(self):
        f=self.fact; i=self.ordinal
        values,row=b.package(replace(self.e,facts=((f,i),(f,i+10000))),b.FIELDS[0])
        self.assertEqual(row['status'],'OBSERVATIONS'); self.assertEqual(len(values[1].sources),2)
        other=replace(f,raw_value='1',numeric_value=Decimal('1'))
        values,row=b.package(replace(self.e,facts=((f,i),(other,i+10000))),b.FIELDS[0])
        self.assertEqual(row['status'],'CONFLICTING'); self.assertIsNone(values[1].value)
        self.assertEqual(len(values[1].alternatives),2)
        values,row=b.package(replace(self.e,facts=((f,i),(replace(f,decimals='INF'),i+10000))),b.FIELDS[0])
        self.assertEqual(row['status'],'OBSERVATIONS'); self.assertEqual(values[1].alternatives[0].precision,'INF')

    def test_annual_instant_entity_unit_nil_precision_and_missing_evidence(self):
        c=self.e.contexts[self.fact.context_id]
        for bad in (replace(c,start=self.a.period.annual_start),replace(c,end=self.a.period.annual_start),replace(c,entity_identifier='999')):
            e=replace(self.e,contexts={**self.e.contexts,c.context_id:bad},facts=((self.fact,self.ordinal),))
            self.assertEqual(b.package(e,b.FIELDS[0])[1]['status'],'NO_ELIGIBLE_OBSERVATIONS')
        for f in (replace(self.fact,unit=None),replace(self.fact,is_nil=True),replace(self.fact,decimals='bad')):
            values,row=b.package(replace(self.e,facts=((f,self.ordinal),)),b.FIELDS[0])
            self.assertEqual(row['status'],'EVIDENCE_GAP'); self.assertTrue(row['errors'])
        absent=replace(self.e,instance=None,receipts=(),facts=(),namespaces={},unresolved_requirements=('Missing retained instance.',))
        value,rows=b.overlay(absent)
        for entry in rows.values():self.assertEqual(entry['status'],'EVIDENCE_GAP')
        self.assertEqual(b.deserialize(b.serialize(value)),value)

    def test_population_roles_overlap_and_excluded_cash_payments(self):
        by={v.concept:v for v in b.RULES}
        self.assertIn('cash',by['CashCashEquivalentsAndShortTermInvestments'].overlap)
        self.assertIn('equity_method',by['LongTermInvestments'].overlap)
        self.assertNotEqual(by['LongTermDebtFairValue'].role,by['DebtInstrumentCarryingAmount'].role)
        self.assertNotEqual(by['FinanceLeaseLiabilityPaymentsDue'].role,by['FinanceLeaseLiability'].role)
        self.assertIn('basis_unreviewed',by['LongTermDebt'].role)
        for name in b.EXCLUDED:
            f=replace(self.fact,concept=name)
            for field in b.FIELDS:self.assertFalse(b.inspect(replace(self.e,facts=((f,self.ordinal),)),field)[0])
        for name in ('OperatingLeaseLiability','FinanceLeaseLiability','LongTermDebtFairValue','LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths'):
            f=replace(self.fact,concept=name)
            values,rows=b.package(replace(self.e,facts=((f,self.ordinal),)),b.FIELDS[1])
            self.assertEqual(rows['status'],'OBSERVATIONS');self.assertIsNone(values[0].value)
            self.assertEqual(values[1].role,by[name].role)

    def test_dimensioned_extensions_and_unknown_concepts_not_financial_acceptance(self):
        context=self.e.contexts[self.fact.context_id]
        from valuation_platform.sec.filing_xbrl import FilingXBRLDimension,FilingXBRLQName
        dim=FilingXBRLDimension(FilingXBRLQName('http://example.com','Axis'),FilingXBRLQName('http://example.com','Member'),None)
        e=replace(self.e,contexts={**self.e.contexts,context.context_id:replace(context,dimensions=(dim,))},facts=((self.fact,self.ordinal),))
        self.assertEqual(b.package(e,b.FIELDS[0])[1]['status'],'NO_ELIGIBLE_OBSERVATIONS')
        self.assertEqual(b.diagnostics(e)[0]['disposition'],'DIMENSIONED_SCOPE_REQUIRES_REVIEW')
        e=replace(self.e,facts=((replace(self.fact,namespace='http://example.com/issuer'),self.ordinal),))
        self.assertEqual(b.package(e,b.FIELDS[0])[1]['status'],'NO_ELIGIBLE_OBSERVATIONS')
        self.assertEqual(b.diagnostics(e)[0]['disposition'],'UNSUPPORTED_EXTENSION')
        arbitrary=replace(self.fact,concept='CashAndEverythingElse')
        self.assertFalse(b.inspect(replace(self.e,facts=((arbitrary,self.ordinal),)),b.FIELDS[0])[0])

    def test_closed_serialization_replay_and_tampering(self):
        for name in ('MSFT','AAPL','GOOGL','NFLX'):
            value=self.overlays[name][-1];payload=b.serialize(value)
            self.assertEqual(b.deserialize(payload),value)
            self.assertEqual(b.serialize(b.deserialize(payload)),payload)
        valued=next(v for v in self.a.cash_investments if v.value is not None)
        bad=replace(self.a,cash_investments=tuple(replace(v,role='invented_cash_total') if v==valued else v for v in self.a.cash_investments))
        with self.assertRaises(h.InputError):b.serialize(bad)
        doc=json.loads(b.serialize(self.a));doc['schema']='unknown'
        with self.assertRaises(h.InputError):b.deserialize(json.dumps(doc))
        doc=json.loads(b.serialize(self.a));digest=next(iter(doc['original_bodies']));doc['original_bodies'][digest]=h._encode(b'changed')
        with self.assertRaises(h.InputError):b.deserialize(json.dumps(doc))

    def test_original_parents_pilots_fields_and_frozen_bytes_preserved(self):
        _,original=b.parent.build();self.assertEqual(self.parents,original)
        for name in ('MSFT','AAPL','GOOGL'):
            current=self.parents[name]; current=current.bundle if type(current) is b.parent.RefreshedHistory else current
            for annual in pilot.load_history(name).annuals:
                self.assertEqual(next(a for a in current.annuals if a.period==annual.period),annual)
                self.assertEqual(h.serialize(pilot.load_history(name)),subprocess.check_output([
                    str(ROOT/'.venv/bin/python'),'-c',
                    'from valuation_platform.analyst import pilot_historical_inputs as p,historical_inputs as h; print(h.serialize(p.load_history("'+name+'")),end="")'],cwd=ROOT).decode())
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',HEAD,'src','docs/evidence','docs/universe'],cwd=ROOT).decode().splitlines()
        # The authorized dated-share inspection path extends this shared API.
        # Its old USD outputs are pinned by ledger/payload replay, not by a
        # permanent source-byte freeze of the reusable inspector.
        paths=[path for path in paths if path!='src/valuation_platform/analyst/retained_components.py']
        paths += ['docs/retained-d-and-a-ledger.json','docs/pilot-historical-input-mappings.json','docs/refreshed-capex-ledger.json',
                  'docs/retained-tax-sbc-ledger.json','docs/retained-working-capital-ledger.json']
        for path in paths:
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=ROOT),path)
        for entries in self.overlays.values():
            for a in entries:
                for v in (*a.cash_investments,*a.debt_leases):
                    self.assertIsNot(v.completeness,h.Completeness.COMPLETE);self.assertIsNone(v.formula)


if __name__=='__main__':unittest.main()
