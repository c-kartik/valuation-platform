"""Retained-source workflow with synthetic decisions/changes in temporary storage."""
from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from valuation_platform.analyst import preparation_review as r, prepared_assembly as a
from valuation_platform.analyst import analyst_overrides as o, historical_inputs as h
from tests.analyst import test_prepared_assembly as assembly_tests


class PreparationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reuse a single retained assembly replay when run with assembly regressions.
        old=assembly_tests.PreparedAssemblyTests
        if not hasattr(old,'histories'):old.setUpClass()
        cls.histories=old.histories;cls.assembly_report=old.report

    def test_all_primary_items_and_nested_diagnostics_reconcile(self):
        for prepared in self.histories.values():
            full=r.primary_queue(prepared);latest=r.primary_queue(prepared,'latest')
            primary=full['primary_items'];info=full['informational_fields']
            self.assertEqual(len({(x['accession'],x['field']) for x in primary}),len(primary))
            cards={c['target_id']:c for c in a.review_queue(prepared)}
            retained={c['target_id']:c for x in (*primary,*info) for c in x['diagnostics']}
            retained.update({c['target_id']:c for g in full['history_exceptions'] for c in g['details']})
            self.assertEqual(cards,retained)
            for item in (*primary,*info):
                self.assertEqual({(c['target_id'],code) for c in item['diagnostics'] for code in c['codes']},
                    {(key,cause['cause']) for cause in item['causes'] for key in cause['diagnostic_ids']})
                for component in item['component_targets']:
                    b=component['binding'];p=next(y.period for y in prepared.bundle.annuals if y.period.accession==item['accession'])
                    self.assertEqual(component['target_id'],a.target(p,item['field'],{'channel':b['channel'],'input_id':b['input_id']}))
            self.assertEqual([x['priority'] for x in primary],sorted(x['priority'] for x in primary))
            for key in ('primary_items','original_diagnostics','invalid_evidence_diagnostics'):
                self.assertEqual(latest['counts'][key]+latest['outside_view_counts'][key],full['counts'][key])
            self.assertEqual(latest['history_exceptions'],full['history_exceptions'])
            if prepared.bundle.annuals:
                self.assertTrue(all(x['accession']==prepared.bundle.annuals[-1].period.accession for x in latest['primary_items']))
            else:self.assertFalse(latest['primary_items'])
        summary=r.summary(self.histories)
        Path('/tmp/preparation-workflow-summary.json').write_text(a.canonical(summary)+'\n')
        self.assertEqual(summary['totals']['full']['original_diagnostics']+summary['totals']['full']['history_exceptions'],self.assembly_report['review_count'])
        groups=json.loads((a.ROOT/'docs/grouped-preparation-review-summary.json').read_text())
        self.assertEqual(summary['totals']['full']['nested_actionable_causes'],groups['totals']['actionable'])

    def test_four_retained_end_to_end_cases(self):
        cases=(('META',h.Field.REVENUE,h.Origin.REPORTED),('MSFT',h.Field.DA,h.Origin.DERIVED),
               ('WMT',h.Field.REVENUE,h.Origin.UNAVAILABLE),('GOOGL',h.Field.SHARES,h.Origin.REPORTED))
        evidence=[]
        for ticker,field,origin in cases:
            with self.subTest(ticker=ticker),tempfile.TemporaryDirectory() as directory:
                prepared=self.histories[ticker]
                binding={(b['accession'],b['input_id']):b for b in json.loads(prepared.bindings_json)}
                eligible=[(annual,v) for annual in prepared.bundle.annuals for v in annual.inputs
                          if v.field is field and v.origin is origin and
                          (field is h.Field.SHARES or binding[(annual.period.accession,v.input_id)]['category'] in ('prepared_value','unresolved_requirement'))]
                annual,source=eligible[-1]
                a.validate_parent(prepared.original)
                if origin is h.Origin.DERIVED:
                    self.assertIsNotNone(source.formula)
                    self.assertTrue(all(any(v.input_id==key and v.value is not None for v in annual.inputs) for key in source.formula.operands))
                if ticker=='WMT':
                    self.assertEqual(source.quality,h.Quality.CONFLICTING);self.assertTrue(source.alternatives)
                if field is h.Field.SHARES:
                    self.assertNotEqual(source.as_of,annual.period.annual_end)
                    self.assertTrue(any(s.dimensions for s in source.sources))
                before=r.inspection_payload(prepared)
                display=next(v for y in before['bundle']['annuals'] if y['period']==h._encode(annual.period)
                             for v in y['inputs'] if v['input_id']==source.input_id)
                target=o.targets(prepared)[display['target_id']]
                store=o.AuditStore(directory)
                payload=dict(value='125.0',unit=source.unit,sign=source.sign,precision='synthetic test exact',
                    scope=source.scope,scope_status=source.scope_status.value,kind='NUMERICAL_ASSUMPTION')
                proposal=store.record('PROPOSE',target,author='Synthetic test author',rationale='Test only; not a financial assumption',payload=payload)
                store.record('ACCEPT',target,author='Synthetic test reviewer',rationale='Test workflow only',reference=proposal['sha256'])
                restarted=o.AuditStore(directory);over=o.overlay(prepared,restarted)
                self.assertEqual(len(over.values),1)
                self.assertTrue(over.values[0].alternatives==(source,), 'Exact period/field source alternative mismatch')
                self.assertEqual(over.values[0].unresolved_requirements,source.unresolved_requirements)
                shown=r.inspection_payload(prepared,store=restarted)
                effective=next(v for y in shown['bundle']['annuals'] if y['period']==h._encode(annual.period)
                               for v in y['inputs'] if v['input_id']==source.input_id)
                self.assertEqual(effective['original'],display['original'])
                self.assertEqual(effective['effective']['origin'],h.Origin.OVERRIDE.value)
                self.assertEqual(shown['queue'],before['queue'])
                self.assertEqual(o.deserialize_overlay(o.serialize_overlay(over),prepared,restarted),over)
                # A temporary in-memory view is deliberately NOT a new registered PreparedHistory.
                changed_source=replace(source,flags=(*source.flags,'synthetic_revision_change_only'))
                changed_annual=replace(annual,inputs=tuple(changed_source if v.input_id==source.input_id else v for v in annual.inputs))
                changed=SimpleNamespace(**vars(prepared));changed.bundle=replace(prepared.bundle,
                    annuals=tuple(changed_annual if y.period==annual.period else y for y in prepared.bundle.annuals))
                changed_target=o.targets(changed)[target.target_id]
                self.assertNotEqual(changed_target.revision,target.revision)
                stale=o.overlay(changed,restarted);self.assertFalse(stale.values);self.assertEqual(len(stale.stale),1)
                with self.assertRaises(h.InputError):restarted.record('ACCEPT',changed_target,author='Tester',rationale='No silent acceptance',reference=proposal['sha256'])
                restarted.record('REVALIDATE',changed_target,author='Synthetic reviewer',rationale='Test changed-revision review only',reference=proposal['sha256'])
                reviewed=o.overlay(changed,o.AuditStore(directory))
                self.assertEqual(len(reviewed.values),1)
                self.assertEqual(o.serialize_overlay(o.deserialize_overlay(o.serialize_overlay(reviewed),changed,restarted)),o.serialize_overlay(reviewed))
                self.assertEqual(r.inspection_payload(prepared),before)
                evidence.append(dict(ticker=ticker,accession=annual.period.accession,annual_end=str(annual.period.annual_end),
                    field=field.value,source_origin=origin.value,source_value=None if source.value is None else str(source.value),
                    as_of=None if source.as_of is None else str(source.as_of),target_id=target.target_id,
                    workflow='PASS_SYNTHETIC_ONLY'))
        Path('/tmp/preparation-workflow-cases.json').write_text(a.canonical(evidence)+'\n')

    def test_missing_acknowledgments_partial_components_and_no_certification(self):
        for ticker in ('META','MSFT','WMT','GOOGL'):
            prepared=self.histories[ticker]
            with tempfile.TemporaryDirectory() as directory:
                store=o.AuditStore(directory);catalog=o.targets(prepared)
                target=next(t for t in catalog.values() if t.source.value is None and t.source.field is h.Field.CFO_RESIDUAL)
                before=r.inspection_payload(prepared)
                store.record('ACKNOWLEDGE',target,author='Synthetic reviewer',rationale='Test missing input acknowledgment')
                result=r.inspection_payload(prepared,store=store)
                self.assertEqual(result['bundle'],before['bundle']);self.assertEqual(result['queue'],before['queue'])
                self.assertFalse(result['overlay']['values'])
                self.assertEqual(result['financial_sufficiency'],'NOT_ASSESSED')
                self.assertTrue(any(v.completeness is h.Completeness.PARTIAL for y in prepared.bundle.annuals for v in y.inputs))

    def test_latest_full_ordering_and_deterministic_payload(self):
        prepared=self.histories['GOOGL'];full=r.primary_queue(prepared)
        self.assertEqual(full,r.primary_queue(prepared))
        custom={field:100-rank for field,rank in a.PRIORITY.items()}
        other=r.primary_queue(prepared,priority=custom)
        self.assertEqual({v['target_id'] for v in full['primary_items']},{v['target_id'] for v in other['primary_items']})
        self.assertNotEqual(full['primary_items'][0]['field'],other['primary_items'][0]['field'])
        with self.assertRaises(h.InputError):r.primary_queue(prepared,'quarterly')
        with self.assertRaises(h.InputError):r.primary_queue(prepared,priority={})

    def test_read_only_local_entry_point(self):
        from scripts import assemble_prepared_inputs as cli
        with patch.object(cli.a,'build',return_value=(self.assembly_report,self.histories)):
            buffer=io.StringIO()
            with redirect_stdout(buffer):cli.main(['--ticker','GOOG','--view','latest','--section','queue'])
            self.assertEqual(json.loads(buffer.getvalue()),r.primary_queue(self.histories['GOOGL'],'latest'))
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaises(SystemExit):cli.main(['--ticker','META','--store',str(Path(directory)/'missing')])
                self.assertFalse((Path(directory)/'missing').exists())


if __name__=='__main__':unittest.main()
