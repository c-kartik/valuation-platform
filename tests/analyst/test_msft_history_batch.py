"""FY2025 explicit acceptance; all other frozen years reviewed together only."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_msft_analyst_package as p


class MSFTHistoryBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.batch=cls.result['msft_history_review'];cls.f=p.Filing(2025)
        cls.prior=json.loads(subprocess.check_output(['git','show','b170bb1:'+p.OUTPUT],cwd=ROOT))

    def test_exact_authorization_and_all_prior_history_preserved(self):
        parent={k:v for k,v in self.result.items() if k not in ('fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
        self.assertTrue(parent==self.prior,'Prior facts, proposals, approvals or FY2026 PASS changed')
        record=self.result['fy2025_approval'];self.assertEqual(record['sequence'],5)
        self.assertEqual(record['previous'],self.prior['fy2026_financing_approval']['sha256'])
        self.assertEqual(record['source_revision'],p.digest(p.relevant(self.prior)))
        for d in self.prior['fy2025_completeness_review']['decisions']:
            self.assertEqual(record['decisions'][d['decision_id']],{k:v for k,v in d.items() if k not in ('decision_id','status','accepted')})
        self.assertTrue(self.batch['accepted_fy2025']['analyst_complete'])
        self.assertEqual(self.batch['accepted_fy2025']['financing_usd'],'89323000000')
        self.assertEqual(self.batch['accepted_fy2025']['source_commercial_paper_usd'],'0')
        self.assertIsNone(self.batch['accepted_fy2025']['source_broader_borrowing_usd'])
        self.assertEqual(self.batch['accepted_fy2025']['remaining_essential_inputs'],[])
        self.assertTrue(self.result['fy2026_analyst_checklist']['analyst_complete'])

    def test_frozen_scope_and_all_seventy_family_slots(self):
        manifest=json.loads((ROOT/'docs/phase1-selected-filing-identity-manifest.json').read_text())
        identities=[r['identity'] for r in manifest['rows'] if r['ticker']=='MSFT']
        self.assertEqual(self.batch['selected_identities'],identities)
        self.assertEqual(len(self.batch['remaining_periods']),3)
        expected=[r['field'] for r in self.result['fy2026_analyst_checklist']['checklist']]
        coverage=self.batch['period_family_coverage'];self.assertEqual(len(coverage),5)
        for row in coverage:
            if 'families' in row:fields=[r['field'] for r in row['families']]
            else:
                node=self.result
                for k in row['checklist_reference'].split('/')[1:]:node=node[k]
                fields=[r['field'] for r in node]
            self.assertEqual(fields,expected)
        self.assertEqual(sum(14 for _ in coverage),70)
        self.assertEqual(sum(row['analyst_complete'] for row in coverage),2)

    def test_actual_selected_year_values_and_independent_display_equalities(self):
        expected=[('198270','83383','89035','23886','14600000000.0','64683000000'),
                  ('211915','88523','87582','28107','13500000000','64304000000'),
                  ('245122','109433','118548','44477','20000000000','78775000000')]
        for row,points in zip(self.batch['remaining_periods'],expected):
            f=row['facts'];actual=tuple(f[k]['display_value'] for k in ('revenue','ebit','cfo','capex'))
            self.assertEqual(actual,points[:4]);self.assertEqual(row['calculations']['expense_da']['value_usd'],points[4])
            self.assertEqual(row['calculations']['named_financing']['value_usd'],points[5])
            self.assertEqual(len(row['cfo_reconciliation']['terms']),14)
            self.assertTrue(row['cfo_reconciliation']['supported'])
            self.assertEqual(sum(Decimal(x['contribution_usd']) for x in row['cfo_reconciliation']['terms']),Decimal(f['cfo']['value']))
            self.assertTrue(all(row['partition_checks'].values()))
            self.assertIn('Net cash from operations '+format(int(f['cfo']['display_value']),','),row['passages'][0]['exact_excerpt'])

    def test_cp_precision_noncash_roles_and_comparability(self):
        rows=self.batch['remaining_periods'];r=rows[2]
        self.assertEqual({x['raw_value'] for x in r['cp_candidates']},{'6693000000','6700000000'})
        self.assertEqual(r['face_cp_observation']['raw_value'],'6693000000')
        self.assertEqual(r['face_cp_observation']['decimals'],'-6')
        self.assertIn('face_cp_observation',r['calculations']['named_financing']['operands'])
        self.assertEqual(rows[1]['comparative_cp_confirmation']['as_of'],'2023-06-30')
        self.assertEqual(rows[1]['comparative_cp_confirmation']['source_identity'],r['identity'])
        self.assertNotIn('commercial_paper',rows[0]['facts']);self.assertNotIn('commercial_paper',rows[1]['facts'])
        self.assertEqual(rows[0]['note_observations'][0]['value_usd'],'364000000')
        self.assertEqual(rows[1]['facts']['depreciation']['precision'],'-9')
        self.assertEqual([x['facts']['acquisition_combined']['display_value'] for x in rows],['22038','1670','69132'])

    def test_single_consolidated_proposal_table_no_older_approval(self):
        proposals=self.batch['consolidated_proposals'];self.assertEqual(len(proposals),9)
        self.assertEqual({d['decision_id'] for d in proposals},{'H'+str(i) for i in range(1,10)})
        self.assertTrue(all(d['status']==p.PROPOSED and d['accepted'] is False and len(d['periods'])==3 for d in proposals))
        self.assertTrue(all(not r['assumptions_active'] and not r['analyst_complete'] for r in self.batch['remaining_periods']))
        self.assertEqual(self.batch['new_older_period_approvals'],0)
        self.assertEqual(self.batch['evidence_acquisition_requirements'],[])
        self.assertFalse(self.batch['phase_closed']);self.assertFalse(self.batch['valuation_consumption_approved'])

    def test_replay_serialization_and_receipt_bindings(self):
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Company batch replay differs')
        self.assertTrue(self.result==json.loads(json.dumps(self.result)),'Round trip differs')
        for row in self.batch['remaining_periods']:
            self.assertEqual(len(row['sources']),2)
            for source in row['sources']:
                self.assertEqual(source['http_status'],200);self.assertEqual(source['digest_type'],'sha256_sec_response_body_bytes')
                self.assertTrue(source['retrieved_at_utc']);self.assertTrue(source['sha256'])

    def test_persisted_authorization_staleness_and_scope_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'package.json';path.write_text(json.dumps(self.result))
            with patch.object(p,'OUTPUT',str(path)):
                self.assertTrue(p.finish_msft_history(self.f,self.prior)=={k:v for k,v in self.result.items() if k not in ('msft_history_approval','msft_current_history')},'Restart differs')
                for key,value,error in [('source_revision','0'*64,'Stale'),('decisions',{},'Unregistered'),('previous','0'*64,'Unregistered')]:
                    bad=copy.deepcopy(self.result);record=bad['fy2025_approval'];record[key]=value
                    record['sha256']=p.digest({k:v for k,v in record.items() if k!='sha256'});path.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(ValueError,error):p.finish_msft_history(self.f,self.prior)
                path.write_text(json.dumps(self.result))
                changed=copy.deepcopy(self.prior);changed['fy2025_completeness_review']['decisions'][0]['recommendation']='changed'
                with self.assertRaisesRegex(ValueError,'Changed FY2025'):p.finish_msft_history(self.f,changed)
        with self.assertRaisesRegex(ValueError,'already exists'):p.fy2025_acceptance_record(self.result)


if __name__=='__main__':unittest.main()
