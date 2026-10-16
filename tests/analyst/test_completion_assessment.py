"""Focused retained assessment checks, never financial approval or ledger replay."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('completion_assessment',ROOT/'scripts/assess_analyst_completion.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


class CompletionAssessmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=a.validate(a.build())

    def test_exact_scope_and_reproducibility(self):
        d=self.data
        self.assertEqual((d['issuer_count'],d['selected_periods'],d['target_slots'],d['target_deficits']),(42,199,210,11))
        self.assertEqual(d['field_period_slots'],2786)
        self.assertEqual(a.load(a.OUTPUT),d)
        self.assertEqual(a.build(),d)
        self.assertFalse(any(r['frozen_classification']=='SPECIALIZED_METHODOLOGY_REQUIRED' for r in d['rows']))

    def test_history_gaps_not_fabricated_preexistence(self):
        rows={r['ticker']:r for r in self.data['rows']}
        self.assertEqual({t:rows[t]['history']['target_deficit'] for t in ('XOM','GEV','SNDK')},{'XOM':5,'GEV':3,'SNDK':3})
        self.assertEqual(rows['XOM']['period_limitations'],[])
        self.assertTrue(all(r['history']['proven_unavailable_preexistence_slot_count'] is None for r in rows.values()))

    def test_approval_depth_and_no_completion_by_acknowledgment(self):
        rows={r['ticker']:r for r in self.data['rows']}
        self.assertEqual(self.data['approved_pilot_periods'],4)
        self.assertFalse(rows['GOOGL']['pilot']['latest_selected_approved'])
        self.assertEqual(rows['GOOGL']['history']['latest_selected'],'2025-12-31')
        self.assertIsNone(rows['MSFT']['pilot']['accepted_short_borrowing']['value_usd'])
        self.assertTrue(all(not r['analyst_complete_latest'] and not r['analyst_complete_full_available_history'] for r in rows.values()))
        self.assertEqual(self.data['financial_approvals_added'],0)

    def test_deduplicated_actions_and_exact_references(self):
        d=self.data
        self.assertEqual(len(d['shared_tasks']),8)
        for r in d['rows']:
            self.assertEqual(len(r['requirements']),14)
            for req in r['requirements']:
                self.assertEqual(req['approval'],'PROPOSED_ONLY')
                self.assertIn(req['task_id'],d['shared_tasks'])
        bad=copy.deepcopy(d);bad['rows'][0]['requirements'][0]['exact_field_period_references'][0]['pointer']='/rows/999999'
        with self.assertRaises((IndexError,KeyError)):a.validate(bad)

    def test_exact_failed_reconciliation_and_preservation(self):
        failed=[p for r in self.data['rows'] for p in r['period_limitations'] if p['cfo_status']=='FAILED']
        self.assertEqual(len(failed),1)
        self.assertEqual(failed[0]['identity']['cik'],63908)
        for path,sha in self.data['source_sha256'].items():
            before=subprocess.check_output(['git','show',a.BASELINE+':'+path],cwd=ROOT)
            self.assertEqual(hashlib.sha256(before).hexdigest(),sha,path)
            self.assertEqual(a.seal(path),sha,path)


if __name__=='__main__':unittest.main()
