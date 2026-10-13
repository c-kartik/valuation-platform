"""Synthetic decisions only; no real assumptions or analyst approvals registered."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from valuation_platform.analyst import analyst_overrides as o, historical_inputs as h
from valuation_platform.analyst import prepared_assembly as a
from tests.analyst.test_historical_inputs import history, reported, unknown


def fixture(value=None):
    bundle=history(value or reported())
    bindings=[dict(accession=y.period.accession,input_id=v.input_id,field=v.field.value,
                   category='support_observation',channel='synthetic') for y in bundle.annuals for v in y.inputs]
    return SimpleNamespace(bundle=bundle,bindings_json=a.canonical(bindings),diagnostics_json='[]',
        ticker='SYNTHETIC',aliases=('SYNTHETIC',),ledger_seals=(),original=None)


def target(prepared, field=h.Field.REVENUE):
    return o.targets(prepared)[a.target(prepared.bundle.annuals[0].period,field.value,{'kind':'field'})]


def payload(t, **changes):
    return dict(value='125.0',unit=t.source.unit,sign=t.source.sign,precision='-1',
                scope=t.source.scope,scope_status=t.source.scope_status.value,
                kind='NUMERICAL_ASSUMPTION',**changes)


class OverrideTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=o.AuditStore(self.tmp.name);self.prepared=fixture();self.t=target(self.prepared)

    def decide(self, t=None):
        t=t or self.t
        proposal=self.store.record('PROPOSE',t,author='Synthetic tester',rationale='Synthetic assumption; no issuer treatment',payload=payload(t))
        accepted=self.store.record('ACCEPT',t,author='Synthetic reviewer',rationale='Explicit synthetic acceptance',reference=proposal['sha256'])
        return proposal,accepted

    def test_persistence_restart_explicit_acceptance_and_immutable_history(self):
        p=self.store.record('PROPOSE',self.t,author='Tester',rationale='Synthetic',payload=payload(self.t))
        self.assertFalse(o.overlay(self.prepared,self.store).values)
        before=(Path(self.tmp.name)/'event-00000001.json').read_bytes()
        self.store.record('ACCEPT',self.t,author='Reviewer',rationale='Synthetic acceptance',reference=p['sha256'])
        restarted=o.AuditStore(self.tmp.name);result=o.overlay(self.prepared,restarted)
        self.assertEqual(len(result.values),1);self.assertEqual(result.values[0].origin,h.Origin.OVERRIDE)
        self.assertEqual(result.values[0].alternatives,(self.t.source,))
        self.assertEqual(result.values[0].completeness,self.t.source.completeness)
        self.assertEqual(result.values[0].sources,());self.assertIn('NUMERICAL_ASSUMPTION',result.values[0].flags)
        self.assertEqual(before,(Path(self.tmp.name)/'event-00000001.json').read_bytes())
        self.assertIn('+00:00',restarted.read()[-1]['manual']['timestamp_utc'])

    def test_relevant_revision_stale_and_explicit_revalidation(self):
        proposal,_=self.decide()
        changed=fixture(replace(self.t.source,value=self.t.source.value+1,
            sources=(replace(self.t.source.sources[0],raw_value='124.4'),)))
        changed_t=target(changed);self.assertNotEqual(changed_t.revision,self.t.revision)
        result=o.overlay(changed,self.store);self.assertFalse(result.values);self.assertEqual(len(result.stale),1)
        with self.assertRaises(h.InputError):self.store.record('ACCEPT',changed_t,author='Tester',rationale='No silent refresh',reference=proposal['sha256'])
        self.store.record('REVALIDATE',changed_t,author='Reviewer',rationale='Explicit changed-source review',reference=proposal['sha256'])
        self.assertEqual(len(o.overlay(changed,self.store).values),1)
        self.assertEqual(len(self.store.read()),3)
        self.assertEqual(self.store.read()[0]['source_snapshot']['input']['value'],'123.4')
        self.assertEqual(self.store.read()[-1]['source_snapshot']['input']['value'],'124.4')

    def test_transport_time_only_not_revision_but_candidates_scope_precision_are(self):
        s=self.t.source.sources[0]
        changed=fixture(replace(self.t.source,sources=(replace(s,receipt=replace(s.receipt,retrieved_at_utc='2026-10-13T00:00:00+00:00')),)))
        self.assertEqual(target(changed).revision,self.t.revision)
        for v in (replace(self.t.source,scope='new scope'),
                  replace(self.t.source,alternatives=(replace(self.t.source,input_id='competing'),)),
                  replace(self.t.source,precision='-2',sources=(replace(s,decimals='-2'),))):
            self.assertNotEqual(target(fixture(v)).revision,self.t.revision)

    def test_null_acknowledgment_no_number_no_requirement_removal(self):
        t=target(self.prepared,h.Field.EBIT)
        self.store.record('ACKNOWLEDGE',t,author='Tester',rationale='Missing evidence explicitly acknowledged')
        result=o.overlay(self.prepared,self.store)
        self.assertFalse(result.values);self.assertEqual(len(result.acknowledgments),1)
        self.assertIsNone(t.source.value);self.assertTrue(t.source.unresolved_requirements)
        with self.assertRaises(h.InputError):self.store.record('ACKNOWLEDGE',t,author='Tester',rationale='Invalid',payload=payload(t))

    def test_invalid_unit_sign_scope_numbers_and_provenance(self):
        for key,value in (('value','NaN'),('value','Infinity'),('value',1),('unit','shares'),('sign',-1),
                          ('scope','complete issuer total'),('scope_status','operating_only'),('kind','default')):
            p=payload(self.t);p[key]=value
            with self.assertRaises(h.InputError):self.store.record('PROPOSE',self.t,author='Tester',rationale='Synthetic',payload=p)
        for author,rationale in (('', 'why'),('Tester','')):
            with self.assertRaises(h.InputError):self.store.record('PROPOSE',self.t,author=author,rationale=rationale,payload=payload(self.t))

    def test_audit_tampering_and_missing_event_rejected(self):
        self.decide();path=Path(self.tmp.name)/'event-00000001.json';original=path.read_text()
        doc=json.loads(original);doc['payload']['value']='999';path.write_text(a.canonical(doc))
        with self.assertRaises(h.InputError):self.store.read()
        path.write_text(original);path.unlink()
        with self.assertRaises(h.InputError):self.store.read()

    def test_separate_serialization_current_source_binding_and_revocation(self):
        p,_=self.decide();result=o.overlay(self.prepared,self.store)
        text=o.serialize_overlay(result);self.assertEqual(o.deserialize_overlay(text,self.prepared,self.store),result)
        self.assertEqual(text,o.serialize_overlay(o.deserialize_overlay(text,self.prepared,self.store)))
        doc=json.loads(text);doc['values'][0]='tampered'
        with self.assertRaises(h.InputError):o.deserialize_overlay(a.canonical(doc),self.prepared,self.store)
        self.store.record('REVOKE',self.t,author='Reviewer',rationale='Synthetic withdrawal',reference=p['sha256'])
        self.assertFalse(o.overlay(self.prepared,self.store).values)

    def test_grouping_preserves_all_original_diagnostics_and_causes(self):
        cards=a.review_queue(self.prepared);groups=o.grouped_queue(self.prepared)
        self.assertEqual({c['target_id'] for c in cards},{c['target_id'] for g in groups for c in g['details']})
        self.assertEqual({(c['target_id'],code) for c in cards for code in c['codes']},
                         {(c['target_id'],g['cause']) for g in groups for c in g['details']})
        self.assertEqual(groups,o.grouped_queue(self.prepared))
        self.assertTrue(any(not g['actionable'] for g in groups))
        self.assertTrue(all(g['actionable'] for g in groups if g['cause'] not in ('HISTORY_EXCEPTION','PARTIAL_OR_UNREVIEWED_SCOPE')))

    def test_original_serialized_bytes_unchanged(self):
        before=h.serialize(self.prepared.bundle);self.decide();o.overlay(self.prepared,self.store)
        self.assertEqual(before,h.serialize(self.prepared.bundle))

    def test_date_class_and_cash_sign_changes_fail_closed(self):
        from datetime import timedelta
        from decimal import Decimal
        shares=reported(h.Field.SHARES);prepared=fixture(shares);t=target(prepared,h.Field.SHARES)
        self.decide(t)
        source=shares.sources[0]
        changed=fixture(replace(shares,as_of=shares.as_of+timedelta(days=1),
            sources=(replace(source,end=source.end+timedelta(days=1)),)))
        self.assertFalse(o.overlay(changed,self.store).values)
        changed=fixture(replace(shares,sources=(replace(source,dimensions=('class:other',)),)))
        self.assertFalse(o.overlay(changed,self.store).values)
        unknown_shares=fixture(replace(unknown(h.Field.SHARES),as_of=None))
        with self.assertRaises(h.InputError):self.decide(target(unknown_shares,h.Field.SHARES))
        capex=replace(reported(h.Field.CAPEX),value=Decimal('-123.4'),sign=-1)
        with self.assertRaises(h.InputError):self.decide(target(fixture(capex),h.Field.CAPEX))

    def test_evidence_and_invalid_diagnostic_changes_are_revisions(self):
        source=self.t.source.sources[0]
        receipt=source.receipt;body=b'changed synthetic original source'
        import hashlib
        artifact=replace(receipt.artifact,body=body,sha256=hashlib.sha256(body).hexdigest())
        changed=fixture(replace(self.t.source,sources=(replace(source,receipt=replace(receipt,artifact=artifact,byte_length=len(body))),)))
        self.assertNotEqual(target(changed).revision,self.t.revision)

    def test_dependent_derivation_is_flagged_not_recalculated(self):
        # A scoped synthetic formula demonstrates operand review, not a financial sum.
        revenue=replace(reported(),completeness=h.Completeness.COMPLETE)
        derived=replace(reported(h.Field.DA,'derived'),origin=h.Origin.DERIVED,
            formula=h.Formula('synthetic',1,h.FormulaKind.COMPONENT_TOTAL,'unchanged structural fixture',
                (revenue.input_id,),False,True,True,(revenue.sources[0].source_id,)))
        prepared=fixture(revenue);annual=prepared.bundle.annuals[0]
        prepared.bundle=replace(prepared.bundle,annuals=(replace(annual,inputs=tuple(derived if v.field is h.Field.DA else v for v in annual.inputs)),))
        bindings=json.loads(prepared.bindings_json)
        for b in bindings:
            if b['field']==h.Field.DA.value:b['input_id']='derived'
        prepared.bindings_json=a.canonical(bindings)
        self.decide(target(prepared));result=o.overlay(prepared,self.store)
        self.assertEqual(result.dependent_review,('derived',));self.assertEqual(derived.value,revenue.value)

    def test_no_partial_to_total_or_ambiguous_field_target(self):
        partial=reported(h.Field.CASH_INVESTMENTS);prepared=fixture(partial);t=target(prepared,h.Field.CASH_INVESTMENTS)
        self.decide(t);result=o.overlay(prepared,self.store)
        self.assertEqual(result.values[0].completeness,h.Completeness.PARTIAL)
        annual=prepared.bundle.annuals[0]
        prepared.bundle=replace(prepared.bundle,annuals=(replace(annual,inputs=(*annual.inputs,replace(partial,input_id='child'))),))
        bindings=json.loads(prepared.bindings_json);bindings.append(dict(accession=partial.period.accession,input_id='child',field=partial.field.value,category='component_observation',channel='synthetic'))
        prepared.bindings_json=a.canonical(bindings)
        self.assertNotIn(a.target(partial.period,partial.field.value,{'kind':'field'}),o.targets(prepared))
        self.assertFalse(o.overlay(prepared,self.store).values)

    def test_forged_population_binding_and_duplicate_targets_cannot_apply(self):
        wrong=replace(self.t,source=replace(self.t.source,input_id='different population'))
        self.decide(wrong)
        self.assertFalse(o.overlay(self.prepared,self.store).values)
        self.assertEqual(len(o.overlay(self.prepared,self.store).stale),1)
        self.decide()
        component=next(t for key,t in o.targets(self.prepared).items()
                       if t.source.input_id==self.t.source.input_id and key!=self.t.target_id)
        self.decide(component)
        with self.assertRaises(h.InputError):o.overlay(self.prepared,self.store)


if __name__=='__main__':unittest.main()
