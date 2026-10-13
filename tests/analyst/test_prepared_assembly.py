"""Assembly is provenance-preserving packaging and review, not acceptance."""
from dataclasses import replace
import hashlib,json,subprocess,unittest
from valuation_platform.analyst import prepared_assembly as a,historical_inputs as h
from valuation_platform.analyst import pilot_historical_inputs as pilot

HEAD='9b477defc6d2dba6e382ad8f27d26e8e6a575730'


class PreparedAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report,cls.histories=a.build()

    def test_every_period_and_field_once_without_history_fabrication(self):
        self.assertEqual(self.report,json.loads((a.ROOT/a.REPORT).read_text()))
        self.assertEqual((self.report['issuer_count'],self.report['selected_periods'],self.report['field_slots']),(42,199,2786))
        actual=set()
        for v in self.histories.values():
            for annual in v.bundle.annuals:
                self.assertEqual(set(x.field for x in annual.inputs),set(h.Field))
                self.assertEqual(len({x.input_id for x in annual.inputs}),len(annual.inputs))
                actual.add((annual.period.cik,annual.period.accession))
        self.assertEqual(len(actual),199);self.assertFalse(self.histories['XOM'].bundle.annuals)
        for name in ('GEV','SNDK'):self.assertEqual(len(self.histories[name].bundle.annuals),2)
        self.assertEqual(self.report['history_target_deficits'],11)
        self.assertIs(a.for_ticker(self.histories,'GOOG'),self.histories['GOOGL'])
        for field,n in ((h.Field.REVENUE,188),(h.Field.EBIT,194),(h.Field.CFO,195),(h.Field.CAPEX,165),(h.Field.DA,115)):
            self.assertEqual(self.report['field_coverage'][field.value]['policy_prepared_value_periods'],n)

    def test_exact_parent_overlay_and_operand_agreement(self):
        for prepared in self.histories.values():
            expected,binding=a.combine(prepared.original,prepared.d_and_a,prepared.instant,prepared.claims_shares)
            self.assertEqual((expected,binding),(prepared.bundle,prepared.bindings_json))
            for original,assembled in zip(a.unwrap(prepared.original).annuals,prepared.bundle.annuals):
                retained={v.input_id:v for v in assembled.inputs}
                for v in original.inputs:
                    if v.field not in (h.Field.DA,h.Field.CASH_INVESTMENTS,h.Field.DEBT_LEASES,h.Field.OTHER_BRIDGE,h.Field.SHARES):
                        self.assertEqual(retained[v.input_id],v)
                for v in assembled.inputs:
                    if v.formula:self.assertTrue(all(o in retained for o in v.formula.operands))
        self.assertTrue(any(v.origin is h.Origin.DERIVED for p in self.histories.values() for y in p.bundle.annuals for v in y.inputs))

    def test_deterministic_priority_targets_click_payloads_and_no_acceptance(self):
        prepared=self.histories['GOOGL'];q=a.review_queue(prepared)
        self.assertEqual(q,a.review_queue(prepared));self.assertEqual(len({v['target_id'] for v in q}),len(q))
        custom={field:100-rank for field,rank in a.PRIORITY.items()}
        reordered=a.review_queue(prepared,custom)
        self.assertEqual({v['target_id'] for v in q},{v['target_id'] for v in reordered})
        self.assertNotEqual([v['target_id'] for v in q],[v['target_id'] for v in reordered])
        self.assertTrue(all(v['action']=='REVIEW_ONLY_NO_ACCEPTANCE_OR_BLOCKER_REMOVAL' for v in q))
        self.assertTrue(any(v['payload'].get('input',{}).get('sources') for v in q))
        self.assertTrue(any(v['payload'].get('input',{}).get('alternatives') for v in q))
        with self.assertRaises(h.InputError):a.review_queue(prepared,{})

    def test_invalid_evidence_overlap_dates_and_partial_population_controls(self):
        tsla=self.histories['TSLA'];q=a.review_queue(tsla)
        rejected=[v for v in q if 'INVALID_EVIDENCE' in v['codes']]
        self.assertTrue(rejected);self.assertTrue(all(v['payload']['accepted_value'] is False for v in rejected))
        self.assertTrue(any('OVERLAP_WARNING' in v['codes'] for v in a.review_queue(self.histories['GOOGL'])))
        for prepared in self.histories.values():
            for annual in prepared.bundle.annuals:
                for v in annual.inputs:
                    if v.field is h.Field.SHARES and v.value is not None:
                        self.assertEqual(v.as_of,v.sources[0].end);self.assertIsNone(v.formula)
                        self.assertIsNot(v.completeness,h.Completeness.COMPLETE)
                    if v.field is h.Field.CFO_RESIDUAL:self.assertIsNone(v.value);self.assertIsNone(v.formula)
        self.assertEqual(self.report['review_codes']['INVALID_EVIDENCE'],8)

    def test_refresh_identity_history_and_distinct_serialization(self):
        prepared=self.histories['LLY'];q=a.review_queue(prepared)
        refresh=[v['payload']['refresh_provenance'] for v in q if 'refresh_provenance' in v['payload']]
        self.assertEqual(len(refresh),5)
        for r in refresh:
            self.assertEqual(r['original_byte_equivalence'],'UNPROVED')
            self.assertEqual(len(r['artifacts']),3)
            self.assertTrue(all(v['historical_sha256']!=v['refreshed']['body_reference'] for v in r['artifacts']))
        payload=a.serialize(prepared);decoded=a.deserialize(payload)
        self.assertEqual(decoded,prepared);self.assertEqual(a.serialize(decoded),payload)
        with self.assertRaises(h.InputError):h.serialize(prepared.bundle)

    def test_roundtrip_conflicts_nulls_and_tampering(self):
        for name in ('XOM','AAPL','GOOGL'):
            p=self.histories[name];payload=a.serialize(p);decoded=a.deserialize(payload)
            self.assertEqual(decoded,p);self.assertEqual(a.review_queue(decoded),a.review_queue(p))
            self.assertEqual(a.serialize(decoded),payload)
        p=self.histories['AAPL'];doc=json.loads(a.serialize(p));doc['schema']='unsupported'
        with self.assertRaises(h.InputError):a.deserialize(json.dumps(doc))
        with self.assertRaises(h.InputError):replace(p,diagnostics_json='[]')
        with self.assertRaises(h.InputError):replace(p,aliases=('AAPL','GOOG'))
        annual=p.bundle.annuals[0];first=annual.inputs[0]
        changed=replace(annual,inputs=tuple(replace(v,role='approved_total') if v.input_id==first.input_id else v for v in annual.inputs))
        with self.assertRaises(h.InputError):replace(p,bundle=replace(p.bundle,annuals=(changed,*p.bundle.annuals[1:])))

    def test_quality_reports_periods_separately_from_component_counts(self):
        q=self.report['field_coverage']
        self.assertEqual(q[h.Field.DA.value]['periods_with_values'],199)
        self.assertEqual(q[h.Field.DA.value]['policy_prepared_value_periods'],115)
        self.assertEqual(q[h.Field.CASH_INVESTMENTS.value]['policy_prepared_value_periods'],0)
        self.assertGreater(q[h.Field.CASH_INVESTMENTS.value]['support_observations'],199)
        self.assertEqual(q[h.Field.TAX.value]['periods_with_values'],4)
        self.assertEqual(q[h.Field.CFO_RESIDUAL.value]['periods_with_values'],0)
        self.assertEqual(self.report['financial_sufficiency'],'NOT_ASSESSED')

    def test_original_pilots_ledgers_and_frozen_artifacts_preserved(self):
        hashes={'MSFT':'e05f85125b6244c321fbdee6469fa89bb809533614bbcc9c5399d2b5c56eb8b5',
            'AAPL':'2772f34db57beb116f4fdb498f0016dc6502d7642b7bbc18f9e89e3645e66f83',
            'GOOGL':'f442e248f1ea2884967680db78c99076ee8beefdaae0bc050b6ee2f0c9b324d5'}
        for name,digest in hashes.items():
            actual=hashlib.sha256(pilot.serialize(pilot.load_history(name)).encode()).hexdigest()
            self.assertEqual(actual,digest)
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',HEAD,'src/valuation_platform/normalization','docs/evidence','docs/universe'],cwd=a.ROOT).decode().splitlines()
        paths+=list(a.LEDGERS)+['docs/pilot-historical-input-mappings.json','src/valuation_platform/analyst/historical_inputs.py']
        for path in paths:self.assertEqual((a.ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=a.ROOT),path)

    def test_grouped_queue_full_diagnostic_preservation_and_summary(self):
        from valuation_platform.analyst import analyst_overrides as o
        per={}
        for name,prepared in self.histories.items():
            cards=a.review_queue(prepared);groups=o.grouped_queue(prepared)
            self.assertEqual({(c['target_id'],code) for c in cards for code in c['codes']},
                {(c['target_id'],g['cause']) for g in groups for c in g['details']})
            self.assertEqual(len({g['group_id'] for g in groups}),len(groups))
            for g in groups:
                if g['cause'] in ('CONFLICT','INVALID_EVIDENCE','OVERLAP_WARNING','MISSING_REQUIRED_VALUE','UNRESOLVED_REQUIREMENTS'):
                    self.assertTrue(g['actionable'])
            per[name]=o.queue_summary(prepared)
        report=dict(schema='grouped-preparation-review-v1',issuers=len(per),
            selected_periods=self.report['selected_periods'],per_issuer=per,
            totals={k:sum(v[k] for v in per.values()) for k in ('diagnostics','groups','actionable','informational')})
        self.assertEqual(report['totals']['diagnostics'],17605)
        # Generated test output is outside the repository; no analyst decisions persisted.
        from pathlib import Path
        Path('/tmp/grouped-preparation-review-summary.json').write_text(a.canonical(report)+'\n')


if __name__=='__main__':unittest.main()
