"""D1-D3 consent and four exact official retained populations, no inferred zeros."""
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


class MSFTOperationPopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.view=cls.result['fy2026_operations_view']
        cls.prior=json.loads(subprocess.check_output(['git','show',p.FY2026_OPERATIONS_BASIS+':'+p.OUTPUT],cwd=ROOT))
        cls.f=p.Filing(2026)

    def test_prior_parent_attempt_nulls_and_audit_unchanged(self):
        parent={k:v for k,v in self.result.items() if k not in ('fy2026_operation_approval','fy2026_operations_view','fy2026_claim_assumption_approval','fy2026_claim_assumptions_view','fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review','fy2025_approval','msft_history_review')}
        self.assertTrue(parent==self.prior,'Prior attempt/source/accepted view changed')
        self.assertEqual((ROOT/p.ACCEPTANCE_PATH).read_bytes(),subprocess.check_output(['git','show',p.FY2026_OPERATIONS_BASIS+':'+p.ACCEPTANCE_PATH],cwd=ROOT))
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Exact operation view replay differs')
        self.assertEqual(json.loads(json.dumps(self.result)),self.result)

    def test_approved_operations_are_not_values_or_waivers(self):
        v=self.view;r=self.result['fy2026_operation_approval']
        self.assertEqual(set(r['decisions']),{'D1','D2','D3'})
        self.assertEqual(r['previous'],self.result['accepted_view']['approval_audit']['sha256'])
        self.assertEqual(r['source_revision'],p.digest(p.relevant(self.prior['fy2026_completeness_attempt'])))
        self.assertIsNone(v['residual']['value']);self.assertFalse(v['residual']['zero_populated'])
        self.assertIsNone(v['pure_nol']['value']);self.assertFalse(v['unrelated_requirements_waived'])
        self.assertEqual(len(v['requirement_overlays']),3)
        self.assertFalse(v['analyst_complete']);self.assertFalse(v['valuation_consumption_approved'])
        self.assertTrue(all(x['status']==p.APPROVED_SCOPE for x in v['operation_requirements']))
        with self.assertRaisesRegex(ValueError,'already exists'):p.fy2026_operations_record(self.result)

    def test_balance_partitions_tie_to_primary_not_missing_tag_zeros(self):
        review=self.view['population_review'];obs=review['observations']
        expected={'current_total':'168825000000','liabilities':'315989000000','equity':'442387000000','balance_total':'758376000000'}
        self.assertEqual({c['parent']:c['amount_usd'] for c in review['checks']},expected)
        for key,item in obs.items():
            for o in item['occurrences']:
                node=self.f.root[o['ordinal']];attrs,text=self.f.inline.facts[node.get('id')]
                self.assertEqual(p.inline_amount(attrs,text),Decimal(o['raw_value']))
                self.assertEqual(o['end'],'2026-06-30')
                self.assertEqual(o['dimensions'],[])
        self.assertEqual(obs['other_current']['value'],'26738000000')
        self.assertEqual(obs['other_long']['value'],'65117000000')
        self.assertEqual(obs['retirement_cost']['value'],'1800000000')
        self.assertEqual(obs['retirement_cost']['precision'],'-8')
        self.assertEqual(obs['retirement_cost']['occurrences'][0]['start'],'2025-07-01')

    def test_population_dispositions_never_fill_missing_or_double_count(self):
        review=self.view['population_review'];rows=review['populations']
        self.assertEqual({r['population'] for r in rows},{'additional_short_borrowing','preferred_equity','noncontrolling_interests','pension_funded_status'})
        self.assertTrue(all(r['value_usd'] is None and r['resolved'] is False and r['proposal'] is None for r in rows))
        self.assertEqual(review['new_document_count'],0);self.assertEqual(review['new_requests'],0)
        for passage in review['passages']:
            self.assertIn(passage['exact_excerpt'],self.f.text)
            self.assertEqual(passage['source_body_sha256'],self.f.primary.artifact.sha256)
        self.assertIsNone(self.result['accepted_view']['periods'][1]['additional_short_borrowing']['value_usd'])
        self.assertEqual(self.result['accepted_view']['short_debt_zero_proposal_status'],'REJECTED_NOT_SELECTED')

    def test_persisted_restart_malformed_scope_and_stale_rejection(self):
        record=self.result['fy2026_operation_approval']
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'package.json';path.write_text(json.dumps({'fy2026_operation_approval':record}))
            with patch.object(p,'OUTPUT',str(path)):
                self.assertEqual(p.apply_fy2026_operations(self.f,self.prior)['fy2026_operations_view'],self.view)
                bad=copy.deepcopy(record);bad['decisions']['D1']='Approve operating-only cash delta'
                path.write_text(json.dumps({'fy2026_operation_approval':bad}))
                with self.assertRaisesRegex(ValueError,'Malformed'):p.apply_fy2026_operations(self.f,self.prior)
                bad['sha256']=p.digest({k:v for k,v in bad.items() if k!='sha256'})
                path.write_text(json.dumps({'fy2026_operation_approval':bad}))
                with self.assertRaisesRegex(ValueError,'Unregistered'):p.apply_fy2026_operations(self.f,self.prior)
                path.write_text(json.dumps({'fy2026_operation_approval':record}))
                bad=copy.deepcopy(self.prior);bad['fy2026_completeness_attempt']['purpose']='changed'
                with self.assertRaisesRegex(ValueError,'Stale FY2026 operation'):p.apply_fy2026_operations(self.f,bad)
                bad=copy.deepcopy(self.prior);bad['periods'][1]['facts']['ar']['value']='1'
                with self.assertRaisesRegex(ValueError,'Stale FY2026 parent'):p.apply_fy2026_operations(self.f,bad)
                path.write_text('{}')
                with self.assertRaises(KeyError):p.apply_fy2026_operations(self.f,self.prior)

    def test_changed_primary_and_wrong_date_rejected(self):
        f=p.Filing(2026);f.root=copy.deepcopy(f.root);f.root[642].text='1'
        with self.assertRaisesRegex(ValueError,'representation mismatch'):p.review_fy2026_populations(f)
        f=p.Filing(2025)
        with self.assertRaisesRegex(ValueError,'Wrong FY2026'):p.apply_fy2026_operations(f,self.prior)
        with self.assertRaisesRegex(ValueError,'Wrong FY2026'):p.review_fy2026_populations(f)


if __name__=='__main__':unittest.main()
