"""Separate assembly/round trips and synthetic-only analyst workflow."""
from dataclasses import replace
from decimal import Decimal
import hashlib
import json
import tempfile
import unittest

from valuation_platform.analyst import historical_inputs as h, prepared_assembly as a
from valuation_platform.analyst import preparation_delivery as d, analyst_overrides as o
from valuation_platform.analyst import preparation_review as review, preparation_validation as validation
from valuation_platform.analyst import pilot_historical_inputs as pilot


class PreparationDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.ledger,cls.histories,cls.summary=d.build()

    def test_all_selected_slots_history_exceptions_and_old_assembly_preserved(self):
        self.assertEqual(self.summary['original_assembly'],json.loads((a.ROOT/a.REPORT).read_text()))
        self.assertEqual((self.summary['histories'],self.summary['selected_annuals'],self.summary['history_deficits']),(42,199,11))
        keys={(row['identity']['fields']['cik'],row['identity']['fields']['accession']) for row in self.ledger['rows']}
        self.assertEqual(len(keys),199)
        self.assertEqual(sum(len(v.bundle.annuals)*len(h.Field) for v in self.histories.values()),2786)
        self.assertFalse(self.histories['XOM'].bundle.annuals)
        for t in ('GEV','SNDK'):self.assertEqual(len(self.histories[t].bundle.annuals),2)
        for p in self.histories.values():
            for original,assembled in zip(p.parent.bundle.annuals,p.bundle.annuals):
                self.assertEqual(set(v.field for v in assembled.inputs),set(h.Field))
                by_id={v.input_id:v for v in assembled.inputs}
                for v in original.inputs:self.assertEqual(by_id[v.input_id],v)

    def test_coverage_population_totals_not_whole_debt_or_financial_sufficiency(self):
        for field,result in self.summary['fields'].items():
            self.assertEqual((result['bands']['recent']['selected_denominator'],result['bands']['older']['selected_denominator']),(121,78))
            self.assertEqual((result['bands']['recent']['target_denominator'],result['bands']['older']['target_denominator']),(126,84))
        self.assertEqual(self.summary['fields'][h.Field.DEBT_LEASES.value]['usable'],0)
        for p in self.histories.values():
            for y in p.bundle.annuals:
                for v in y.inputs:
                    if v.role=='reported_borrowing_total':
                        self.assertEqual(v.completeness,h.Completeness.PARTIAL)
                        self.assertEqual(v.scope_status,h.Scope.UNKNOWN)
                        self.assertIn('borrowing_basis_and_full_population_unproved',v.flags)
        self.assertEqual(self.summary['financial_sufficiency'],'NOT_ASSESSED')
        self.assertFalse(self.summary['phase_closed'])
        self.assertEqual(sum(self.summary['cfo_checks'].values()),199)

    def test_supported_checks_require_complete_display_and_no_residual_proof(self):
        from valuation_platform.analyst import cfo_statement_reconciliation as c
        for row in self.ledger['rows']:
            result=row['reconciliation']
            if result['status']=='SUPPORTED':
                p=result['populations'][0]
                self.assertFalse(p['requirements']);self.assertTrue(p['rows'])
                self.assertEqual(c.check_rows(p['rows'],p['cfo'],complete=True,non_overlapping=True,scope=p['scope'])['status'],'SUPPORTED')
                self.assertNotIn('unclassified_remainder',{v['concept'] for v in p['rows']})

    def test_exact_deterministic_ledger_replay(self):
        self.assertEqual(self.ledger,json.loads((a.ROOT/d.LEDGER).read_text()))
        self.assertEqual(self.summary,json.loads((a.ROOT/d.SUMMARY).read_text()))

    def test_serialization_round_trip_original_and_new_proofs(self):
        p=self.histories['AAPL'];original=a.serialize(p.parent)
        text=d.serialize(p);decoded=d.deserialize(text)
        self.assertEqual(decoded,p);self.assertEqual(d.serialize(decoded),text)
        self.assertEqual(a.serialize(decoded.parent),original)
        document=json.loads(text);document['schema']='unapproved'
        with self.assertRaises(h.InputError):d.deserialize(json.dumps(document))
        document=json.loads(text);key=next(iter(document['original_bodies']))
        document['original_bodies'][key]=h._encode(b'tampered')
        with self.assertRaises(h.InputError):d.deserialize(json.dumps(document))

    def test_override_dependencies_restart_scope_revision_and_no_recalculation(self):
        p=self.histories['AAPL']
        v=next(v for y in reversed(p.bundle.annuals) for v in y.inputs if v.role=='cash_equivalents_reported')
        target=next(t for t in o.targets(p).values() if t.source==v)
        payload=dict(value=str(v.value+1),unit='USD',sign=1,precision=v.precision,scope=v.scope,
            scope_status=v.scope_status.value,kind='NUMERICAL_ASSUMPTION')
        with tempfile.TemporaryDirectory() as directory:
            store=o.AuditStore(directory)
            proposal=store.record('PROPOSE',target,author='Synthetic tester',rationale='Synthetic test only',payload=payload)
            store.record('ACCEPT',target,author='Synthetic reviewer',rationale='Synthetic test only',reference=proposal['sha256'])
            restarted=o.AuditStore(directory);result=d.overlay(p,restarted)
            root=next(v for y in p.bundle.annuals if y.period==target.source.period for v in y.inputs if v.role=='reported_current_liquidity')
            self.assertIn(v.period.accession+'#'+root.input_id,result.dependent_review)
            self.assertFalse(any(x.split('#')[0]!=v.period.accession for x in result.dependent_review))
            view=d.inspection_payload(p,store=restarted)
            row=next(v for y in view['bundle']['annuals'] for v in y['inputs'] if v['input_id']==root.input_id and v['original']['value']==str(root.value))
            self.assertEqual(row['original']['value'],str(root.value));self.assertIsNone(row['effective']['value'])
            self.assertEqual(d.deserialize_overlay(d.serialize_overlay(result),p,restarted).values,result.values)
            # Scope/evidence content, not refreshed transport time, is revision-bound.
            entries=json.loads(p.bindings_json)
            key=next(v for v in entries if v['input_id']==target.source.input_id and v['accession']==target.source.period.accession)
            changed=json.loads(json.dumps(key));changed['population_proof']['scope_change']='synthetic new scope'
            from types import SimpleNamespace
            altered=SimpleNamespace(**{name:getattr(p,name) for name in ('bundle','ticker','aliases','original','diagnostics_json','ledger_seals')},
                bindings_json=a.canonical([changed if v==key else v for v in entries]))
            newtarget=o.targets(altered)[target.target_id]
            self.assertNotEqual(newtarget.revision,target.revision)
            self.assertEqual(len(d.overlay(altered,restarted).stale),1)

    def test_review_keeps_every_original_diagnostic_and_component_target(self):
        for t in ('META','MSFT','WMT','GOOGL'):
            p=self.histories[t]
            parent={v['target_id'] for v in a.review_queue(p.parent)}
            new={v['target_id'] for v in a.review_queue(p)}
            self.assertTrue(parent.issubset(new))
            full=review.primary_queue(p,'full');latest=review.primary_queue(p,'latest')
            self.assertEqual(full,review.primary_queue(p,'full'))
            self.assertLessEqual(len(latest['primary_items']),len(full['primary_items']))

    def test_cfo_confirmation_alias_invalidates_remainder_but_not_expense_roles(self):
        p=self.histories['AAPL'];annual=p.bundle.annuals[-1]
        source=next(v for v in annual.inputs if v.role=='independently_reconciled_reported_cfo')
        aliases=d.population_aliases(annual,source)
        root=next(v for v in annual.inputs if v.role=='displayed_cfo_subtotal')
        self.assertIn(root.input_id,aliases)
        expense=next(v for v in annual.inputs if v.field is h.Field.SBC and 'expense' in v.role)
        self.assertFalse(d.population_aliases(annual,expense))
        target=next(t for t in o.targets(p).values() if t.source==source)
        with tempfile.TemporaryDirectory() as directory:
            store=o.AuditStore(directory)
            payload=dict(value=str(source.value+1),unit='USD',sign=1,precision=source.precision,
                scope=source.scope,scope_status=source.scope_status.value,kind='NUMERICAL_ASSUMPTION')
            proposal=store.record('PROPOSE',target,author='Synthetic',rationale='Test only',payload=payload)
            store.record('ACCEPT',target,author='Synthetic',rationale='Test only',reference=proposal['sha256'])
            result=d.overlay(p,store)
            self.assertIn(annual.period.accession+'#displayed-cfo:unclassified-remainder',result.dependent_review)

    def test_independent_fixtures_and_pilot_bytes_preserved(self):
        parents={t:p.parent for t,p in self.histories.items()}
        fixture=json.loads((a.ROOT/validation.FIXTURES).read_text())['fixtures']
        result=validation.spot_checks(parents,fixture,validation.statement_artifacts())
        self.assertEqual(result,json.loads((a.ROOT/'docs/preparation-independent-results.json').read_text()))
        pins={'MSFT':'e05f85125b6244c321fbdee6469fa89bb809533614bbcc9c5399d2b5c56eb8b5',
            'AAPL':'2772f34db57beb116f4fdb498f0016dc6502d7642b7bbc18f9e89e3645e66f83',
            'GOOGL':'f442e248f1ea2884967680db78c99076ee8beefdaae0bc050b6ee2f0c9b324d5'}
        for t,sha in pins.items():self.assertEqual(hashlib.sha256(pilot.serialize(pilot.load_history(t)).encode()).hexdigest(),sha)


if __name__=='__main__':unittest.main()
