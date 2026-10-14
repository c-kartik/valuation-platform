"""Retained tax integration and synthetic decisions, never adjusted tax rates."""
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from valuation_platform.analyst import historical_inputs as h, prepared_assembly as a
from valuation_platform.analyst import retained_reported_tax as t, analyst_overrides as o, preparation_review as r
from tests.analyst import test_prepared_assembly as shared

BASE='a0bafc2314938255ff7614f5c5737debabd726bd'


class IntegratedTaxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not hasattr(shared.PreparedAssemblyTests,'histories'):shared.PreparedAssemblyTests.setUpClass()
        cls.histories=shared.PreparedAssemblyTests.histories
        cls.msft=cls.histories['MSFT']

    def test_all_periods_have_three_separate_components_and_exact_overlay_binding(self):
        for p in self.histories.values():
            self.assertEqual(len(p.bundle.annuals),len(p.tax_context))
            for annual,tax in zip(p.bundle.annuals,p.tax_context):
                expected=t.inputs(tax)
                for value in expected:self.assertEqual(next(v for v in annual.inputs if v.input_id==value.input_id),value)
                self.assertEqual(len({v.input_id for v in expected}),3)
                self.assertEqual(expected[2].unit,'pure')
                self.assertFalse(any(v.role=='accrued_tax_provision' for v in annual.inputs))
                self.assertTrue(all(v.completeness is not h.Completeness.COMPLETE for v in expected))
        totals={role:sum(a.quality(p)['fields'][h.Field.TAX.value]['components'][role]['populated'] for p in self.histories.values())
            for role in ('reported_income_tax_expense_benefit','reported_continuing_pretax_income','reported_effective_tax_rate')}
        self.assertEqual(tuple(totals.values()),(186,162,154))

    def test_exact_ma_repaired_joins_and_fail_closed_inventory_binding(self):
        ma=self.histories['MA']
        repaired=[v for v in ma.tax_context if json.loads(v.proof_json).get('registered_pretax_entry')]
        self.assertEqual(len(repaired),3)
        for v in repaired:
            proof=json.loads(v.proof_json)
            binding=proof['curated_metadata_basis'];self.assertEqual(binding['source'],'docs/depreciation-amortization-inventory.json')
            self.assertEqual(binding['filing']['accession_number'],v.period.accession)
            self.assertEqual(binding['instance_sha256'],v.receipt.artifact.sha256)
            self.assertIsNotNone(v.pretax.value);self.assertIsNotNone(json.loads(v.etr_json)['value'])
            with patch('valuation_platform.analyst.nvda_income_inputs.pinned',side_effect=h.InputError('changed sealed source')):
                with self.assertRaises(h.InputError):t.validate(v)

    def test_roundtrip_legacy_version_and_pilot_preservation(self):
        for name in ('MA','MSFT','AAPL','GOOGL','XOM'):
            p=self.histories[name];text=a.serialize(p)
            self.assertEqual(json.loads(text)['schema'],a.SCHEMA)
            self.assertEqual(a.deserialize(text),p)
        p=self.histories['AAPL']
        bundle,bindings=a.combine(p.original,p.d_and_a,p.instant,p.claims_shares)
        legacy=replace(p,bundle=bundle,bindings_json=bindings,diagnostics_json=a.diagnostics(p.original,False),
            ledger_seals=a.seals(False),tax_context=())
        text=a.serialize(legacy);self.assertEqual(json.loads(text)['schema'],a.LEGACY_SCHEMA)
        self.assertEqual(a.serialize(a.deserialize(text)),text)

    def test_changed_ratio_cannot_be_exported_as_verified_source_history(self):
        p=self.histories['AAPL'];entry=p.tax_context[-1]
        ratio=json.loads(entry.etr_json);ratio['value']='1'
        changed=replace(entry,etr_json=a.canonical(ratio))
        ts=(*p.tax_context[:-1],changed)
        bundle,bindings=a.combine(p.original,p.d_and_a,p.instant,p.claims_shares,ts)
        forged=replace(p,tax_context=ts,bundle=bundle,bindings_json=bindings)
        with self.assertRaises(h.InputError):a.serialize(forged)

    def test_stable_queue_and_no_provenance_reuse_overlap_inflation(self):
        p=self.msft;catalog=o.targets(p)
        self.assertEqual(catalog,o.targets(p))
        cards=a.review_queue(p)
        for card in cards:
            if card.get('payload',{}).get('binding',{}).get('channel')=='reported_tax':
                self.assertNotIn('OVERLAP_WARNING',card['codes'])
        groups=o.grouped_queue(p)
        self.assertEqual({(c['target_id'],code) for c in cards for code in c['codes']},
            {(c['target_id'],g['cause']) for g in groups for c in g['details']})
        self.assertEqual(len({(g['accession'],g['field'],g['cause'],g['actionable']) for g in groups}),len(groups))

    def decide(self,store,target):
        payload=dict(value='1',unit=target.source.unit,sign=target.source.sign,precision='synthetic_exact',
            scope=target.source.scope,scope_status=target.source.scope_status.value,kind='NUMERICAL_ASSUMPTION')
        proposal=store.record('PROPOSE',target,author='Synthetic tester',rationale='Test only, not an issuer assumption',payload=payload)
        store.record('ACCEPT',target,author='Synthetic reviewer',rationale='Test-only explicit decision',reference=proposal['sha256'])
        return proposal

    def test_operand_override_invalidates_only_its_period_without_recalculating_source_ratio(self):
        p=self.msft;period=p.bundle.annuals[-1].period
        catalog=o.targets(p);target=next(v for v in catalog.values() if v.source.period==period and
            v.source.role=='reported_income_tax_expense_benefit')
        with tempfile.TemporaryDirectory() as directory:
            store=o.AuditStore(directory);self.decide(store,target)
            restarted=o.AuditStore(directory);overlay=o.overlay(p,restarted)
            ratio=next(v for v in p.bundle.annuals[-1].inputs if v.unit=='pure')
            self.assertEqual(overlay.dependent_review,(period.accession+'#'+ratio.input_id,))
            view=r.inspection_payload(p,store=restarted)
            for annual in view['bundle']['annuals']:
                value=next(v for v in annual['inputs'] if v['original']['role']=='reported_effective_tax_rate')
                if value['original']['formula'] and annual['period']['fields']['accession']==period.accession:
                    self.assertIsNone(value['effective']['value']);self.assertIsNotNone(value['original']['value'])
                    self.assertEqual(value['effective_basis'],'DEPENDENT_ETR_INVALIDATED')
                else:self.assertEqual(value['effective'],value['original'])
            self.assertEqual(o.deserialize_overlay(o.serialize_overlay(overlay),p,restarted),overlay)
            ratio_target=next(v for v in catalog.values() if v.source.input_id==ratio.input_id and v.source.period==period)
            with self.assertRaises(h.InputError):self.decide(store,ratio_target)

    def test_changed_operand_evidence_stales_decision_and_explicit_revalidation_restores_only_patch(self):
        p=self.msft;catalog=o.targets(p);target=next(v for v in catalog.values() if
            v.source.period==p.bundle.annuals[-1].period and v.source.role=='reported_continuing_pretax_income')
        with tempfile.TemporaryDirectory() as directory:
            store=o.AuditStore(directory);proposal=self.decide(store,target)
            from types import SimpleNamespace
            def modified(change):
                annuals=tuple(replace(y,inputs=tuple(change(v) if v.input_id==target.source.input_id and v.period==target.source.period else v for v in y.inputs)) for y in p.bundle.annuals)
                return SimpleNamespace(**{**p.__dict__,'bundle':replace(p.bundle,annuals=annuals)})
            changed=modified(lambda v:replace(v,flags=v.flags+('synthetic_changed_scope_evidence',)))
            current=o.targets(changed)[target.target_id]
            self.assertNotEqual(current.revision,target.revision)
            self.assertFalse(o.overlay(changed,store).values);self.assertTrue(o.overlay(changed,store).stale)
            store.record('REVALIDATE',current,author='Synthetic reviewer',rationale='Test-only changed evidence review',reference=proposal['sha256'])
            self.assertTrue(o.overlay(changed,o.AuditStore(directory)).dependent_review)
            self.assertIsNotNone(next(v for v in changed.bundle.annuals[-1].inputs if v.unit=='pure').value)

    def test_original_artifacts_non_tax_values_and_negative_da_preserved(self):
        for path in a.LEDGERS:
            if path!=t.LEDGER:self.assertEqual((a.ROOT/path).read_bytes(),subprocess.check_output(['git','show',BASE+':'+path],cwd=a.ROOT))
        for path in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src/valuation_platform/normalization','docs/evidence','docs/universe'],cwd=a.ROOT,text=True).splitlines():
            self.assertEqual((a.ROOT/path).read_bytes(),subprocess.check_output(['git','show',BASE+':'+path],cwd=a.ROOT))
        for p in self.histories.values():
            legacy,_=a.combine(p.original,p.d_and_a,p.instant,p.claims_shares)
            for old,new in zip(legacy.annuals,p.bundle.annuals):
                self.assertEqual(tuple(v for v in old.inputs if v.field is not h.Field.TAX),tuple(v for v in new.inputs if v.field is not h.Field.TAX))


class TaxRevisionTests(unittest.TestCase):
    def test_proof_transport_only_ignored_but_evidence_and_operand_changes_retained(self):
        prefix='tax_context_proof:'
        first=dict(policy_id='existing',operand_value='123',body_digest='original',retrieved_at='2026-10-01T00:00:00+00:00')
        later=dict(first,retrieved_at='2026-10-02T00:00:00+00:00')
        self.assertEqual(o.relevant(prefix+a.canonical(first)),o.relevant(prefix+a.canonical(later)))
        for key,value in [('operand_value','124'),('body_digest','changed'),('policy_id','changed')]:
            self.assertNotEqual(o.relevant(prefix+a.canonical(first)),o.relevant(prefix+a.canonical(dict(later,**{key:value}))))


if __name__=='__main__':unittest.main()
