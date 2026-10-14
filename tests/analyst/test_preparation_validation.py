"""Independent expectation cells and conservative coverage, not readiness."""
from dataclasses import replace
from decimal import Decimal
import json
from pathlib import Path
import unittest

from valuation_platform.analyst import preparation_validation as v, historical_inputs as h, prepared_assembly as a
from tests.analyst import test_prepared_assembly as existing
from tests.analyst.test_analyst_overrides import fixture
from tests.analyst.test_historical_inputs import reported


class PreparationValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        old=existing.PreparedAssemblyTests
        if not hasattr(old,'histories'):old.setUpClass()
        cls.histories=old.histories
        cls.fixtures=json.loads((a.ROOT/v.FIXTURES).read_text())['fixtures']
        cls.artifacts=v.statement_artifacts()
        cls.spot=v.spot_checks(cls.histories,cls.fixtures,cls.artifacts)
        cls.coverage=v.coverage(cls.histories,cls.spot)
        Path('/tmp/preparation-independent-results.json').write_text(a.canonical(cls.spot)+'\n')
        Path('/tmp/preparation-coverage-results.json').write_text(a.canonical(cls.coverage)+'\n')

    def test_exact_120_latest_field_identities_and_evidence_depth(self):
        rows=self.spot['rows'];self.assertEqual(len(rows),120)
        self.assertEqual(len({(r['ticker'],r['accession'],r['field']) for r in rows}),120)
        self.assertEqual(sum(self.spot['counts'].values()),120)
        for row in rows:
            p=self.histories[row['ticker']].bundle.annuals[-1].period
            self.assertEqual((row['accession'],row['annual_start'],row['annual_end']),(p.accession,str(p.annual_start),str(p.annual_end)))
            self.assertFalse(row['independent_complete_field'])
        self.assertTrue(all(r['available_artifacts'] for r in rows))
        self.assertTrue(any(r['source_conflicting'] for r in rows if r['ticker']=='WMT'))

    def test_independent_cells_not_output_seeded_and_scope_failures_visible(self):
        expected={(r['ticker'],r['field']):r for r in self.spot['rows']}
        unexpected=[r for r in self.spot['rows'] if r['status']=='FAILED' and
                    any(not e.startswith('APPROVED_PRIMITIVE_SCOPE_') for e in r['failures'])]
        self.assertFalse(unexpected,[(r['ticker'],r['field'],r['failures']) for r in unexpected])
        self.assertEqual(expected['HD',h.Field.DA.value]['status'],'CHECKED')
        self.assertEqual(expected['AMZN',h.Field.DA.value]['status'],'CHECKED')
        for row in self.spot['rows']:
            if row['status']=='CHECKED':self.assertTrue(row['fixture_ids'])
        self.assertTrue(all(f['evidence_kind']=='rendered_statement_or_note' for f in self.fixtures))
        self.assertTrue(all(f['path'] not in a.LEDGERS for f in self.fixtures))

    def test_exact_denominators_and_missing_target_slots_no_dates_invented(self):
        c=self.coverage
        self.assertEqual((c['totals']['issuers'],c['totals']['selected_periods'],c['totals']['target_periods']),(42,199,210))
        self.assertEqual((c['totals']['selected_field_inventory'],c['totals']['target_field_inventory']),(2786,2940))
        for f in h.Field:
            recent=c['fields'][f.value]['recent'];older=c['fields'][f.value]['older']
            self.assertEqual((recent['selected_denominator'],recent['target_denominator'],recent['missing_target_slots']),(121,126,5))
            self.assertEqual((older['selected_denominator'],older['target_denominator'],older['missing_target_slots']),(78,84,6))
            self.assertEqual((recent['proposed_target_percent'],older['proposed_target_percent']),(90,80))
        self.assertEqual(c['issuer_slots']['XOM']['selected'],0)
        self.assertEqual(c['issuer_slots']['GEV']['selected'],2);self.assertEqual(c['issuer_slots']['SNDK']['selected'],2)
        self.assertFalse(c['phase_closure']);self.assertEqual(c['financial_sufficiency'],'NOT_ASSESSED')

    def test_observations_are_not_usable_complete_fields_and_origins_separate(self):
        for field in (h.Field.CASH_INVESTMENTS,h.Field.DEBT_LEASES,h.Field.SHARES,h.Field.CF_WORKING_CAPITAL):
            for band in ('recent','older'):
                counts=self.coverage['fields'][field.value][band]['counts']
                self.assertEqual(counts['approved_complete_total'],0);self.assertGreater(counts['valued'],0)
        self.assertEqual(self.coverage['totals']['manual_overrides'],0)
        self.assertEqual(self.coverage['totals']['substantive_review_required']+self.coverage['totals']['confirmation_pending_only'],2786)
        self.assertLess(self.coverage['totals']['substantive_review_required'],2786)

    def test_missing_body_is_not_disclosure_absence_or_an_xml_confirmation(self):
        result=v.spot_checks(self.histories,[],[])
        self.assertEqual(result['counts'],{'NOT_VERIFIED':120})
        self.assertEqual(len(result['backlog']),120)
        self.assertTrue(all(r['action'] in ('EXACT_PRIMARY_BODY_MISSING','EXACT_PRIMARY_FILENAME_BINDING_REQUIRED') for r in result['backlog']))
        bad=[dict(f,evidence_kind='filing_xbrl_instance') for f in self.fixtures[:1]]
        report=v.spot_checks(self.histories,bad,self.artifacts)
        row=next(r for r in report['rows'] if r['ticker']==bad[0]['ticker'] and r['field']==bad[0]['field'])
        self.assertEqual(row['status'],'FAILED')

    def test_deterministic_reporting_tampered_receipt_and_manual_are_not_approvals(self):
        self.assertEqual(self.spot,v.spot_checks(self.histories,self.fixtures,self.artifacts))
        self.assertEqual(self.coverage,v.coverage(self.histories,self.spot))
        altered=[dict(f,sha256='0'*64) for f in self.fixtures[:1]]
        report=v.spot_checks(self.histories,altered,self.artifacts)
        row=next(r for r in report['rows'] if r['ticker']==altered[0]['ticker'] and r['field']==altered[0]['field'])
        self.assertEqual(row['status'],'FAILED')
        source=reported();manual=h.ManualIdentity('synthetic','2026-10-14T00:00:00+00:00','test only')
        override=replace(source,input_id='synthetic-override',origin=h.Origin.OVERRIDE,manual=manual,alternatives=(source,))
        report=v.coverage({'SYNTHETIC':fixture(override)})
        self.assertNotIn('separate_reported_tax_context',report)
        self.assertEqual(report['totals']['manual_overrides'],1)
        self.assertEqual(report['fields']['revenue']['recent']['counts']['approved_complete_total'],0)

    def test_original_artifacts_and_policies_preserved(self):
        import subprocess
        paths=[p for p in a.LEDGERS if p not in (a.da.LEDGER,a.bridge.LEDGER)]+['docs/pilot-historical-input-mappings.json','src/valuation_platform/analyst/historical_inputs.py']
        paths+=subprocess.check_output(['git','ls-tree','-r','--name-only','0e7970593399fc2289dccacb4e284fd04677868b','docs/evidence','docs/universe','src/valuation_platform/normalization'],cwd=a.ROOT).decode().splitlines()
        for path in paths:
            self.assertTrue((a.ROOT/path).read_bytes()==subprocess.check_output(['git','show','0e7970593399fc2289dccacb4e284fd04677868b:'+path],cwd=a.ROOT),path)


if __name__=='__main__':unittest.main()
