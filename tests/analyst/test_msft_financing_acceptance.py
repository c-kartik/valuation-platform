"""Explicit financing supersession and the existing exact-period checklist."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_msft_analyst_package as p


class MSFTFinancingAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.view=cls.result['fy2026_analyst_checklist'];cls.f=p.Filing(2026)
        cls.prior=json.loads(subprocess.check_output(['git','show',p.FY2026_FINANCING_BASIS+':'+p.OUTPUT],cwd=ROOT))

    def test_entire_prior_package_nulls_rejection_and_audits_preserved(self):
        parent={k:v for k,v in self.result.items() if k not in ('fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review')}
        self.assertTrue(parent==self.prior,'Prior sources, selections or audit history changed')
        self.assertEqual(self.result['accepted_view']['short_debt_zero_proposal_status'],'REJECTED_NOT_SELECTED')
        self.assertIsNone(self.result['accepted_view']['periods'][1]['additional_short_borrowing']['value_usd'])
        self.assertEqual(self.result['fy2026_operation_approval'],self.prior['fy2026_operation_approval'])
        self.assertEqual(self.result['fy2026_claim_assumption_approval'],self.prior['fy2026_claim_assumption_approval'])

    def test_financing_selection_and_explicit_supersession(self):
        r=self.result['fy2026_financing_approval'];v=self.view['financing']
        self.assertEqual(r['sequence'],4);self.assertEqual(r['previous'],self.prior['fy2026_claim_assumption_approval']['sha256'])
        self.assertEqual(r['source_revision'],p.digest(p.relevant(self.prior)))
        self.assertEqual(r['identity']['annual_end'],'2026-06-30')
        self.assertEqual(len(r['supersedes']),2)
        self.assertEqual(v['value_usd'],'106888000000');self.assertEqual(v['value_millions'],'106888')
        self.assertEqual(v['origin'],'analyst_assumption');self.assertIsNone(v['source_additional_short_borrowing'])
        self.assertFalse(v['reported_zero']);self.assertFalse(v['complete_debt']);self.assertFalse(v['immateriality_finding'])
        self.assertIn('Unquantified',v['omitted_borrowing']);self.assertIn('superseded',v['supersession'])
        terms=self.prior['accepted_view']['periods'][1]['borrowings']['selected']['terms']
        self.assertEqual([t['operand'] for t in terms],['term_debt_parent','finance_liability'])

    def test_exact_fourteen_requirements_reassessed_without_new_perimeter(self):
        v=self.view;old=self.prior['fy2026_completeness_attempt']['checklist']
        self.assertEqual(len(v['checklist']),14)
        self.assertEqual([r['field'] for r in v['checklist']],[r['field'] for r in old])
        self.assertTrue(all(r['status'].startswith('SATISFIED_') for r in v['checklist']))
        self.assertEqual(v['remaining_essential_inputs'],[]);self.assertTrue(v['analyst_complete'])
        for key in ('complete_issuer_history','whole_universe_closed','phase_closed','valuation_consumption_approved'):self.assertFalse(v[key])
        self.assertEqual(len(self.result['periods'][1]['unresolved_requirements']),14)
        self.assertIn('THIS_APPROVED_HISTORICAL_PERIMETER',v['financial_sufficiency'])
        for row in v['checklist']:
            for ref in row['evidence_references']:
                node=self.result
                for k in ref.split('/')[1:]:node=node[int(k)] if isinstance(node,list) else node[k]
                self.assertIsNotNone(node)

    def test_persist_restart_round_trip_and_replay(self):
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Package differs')
        self.assertTrue(self.result==json.loads(json.dumps(self.result)),'Round trip differs')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'package.json';path.write_text(json.dumps(self.result))
            with patch.object(p,'OUTPUT',str(path)):
                expected={k:v for k,v in self.result.items() if k!='fy2025_completeness_review'}
                self.assertTrue(p.apply_fy2026_financing(self.f,self.prior)==expected,'Prior financing restart differs')
        with self.assertRaisesRegex(ValueError,'already exists'):p.fy2026_financing_record(self.result)

    def test_tampered_scope_supersession_revision_and_missing_record_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'package.json'
            with patch.object(p,'OUTPUT',str(path)):
                for key,value,error in [('supersedes',[],'Unregistered'),('source_revision','0'*64,'Stale'),
                    ('decisions',{'financing':'complete debt106888'},'Unregistered'),('previous','0'*64,'Unregistered')]:
                    bad=copy.deepcopy(self.result);r=bad['fy2026_financing_approval'];r[key]=value
                    r['sha256']=p.digest({k:v for k,v in r.items() if k!='sha256'});path.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(ValueError,error):p.apply_fy2026_financing(self.f,self.prior)
                bad=copy.deepcopy(self.result);bad['fy2026_financing_approval']['sha256']='0'*64;path.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,'Malformed'):p.apply_fy2026_financing(self.f,self.prior)
                path.write_text(json.dumps(self.prior))
                with self.assertRaises(KeyError):p.apply_fy2026_financing(self.f,self.prior)

    def test_changed_source_checklist_and_other_period_fail_closed(self):
        changed=copy.deepcopy(self.prior);changed['fy2026_operations_view']['population_review']['populations'][0]['evidence_reason']='changed'
        with self.assertRaises(ValueError):p.apply_fy2026_financing(self.f,changed)
        changed=copy.deepcopy(self.prior);changed['accepted_view']['periods'][1]['borrowings']['selected']['value_usd']='1'
        with self.assertRaises(ValueError):p.apply_fy2026_financing(self.f,changed)
        changed=copy.deepcopy(self.prior);changed['fy2026_completeness_attempt']['checklist'].pop()
        with self.assertRaises(ValueError):p.apply_fy2026_financing(self.f,changed)
        with self.assertRaisesRegex(ValueError,'Wrong FY2026'):p.apply_fy2026_financing(p.Filing(2025),self.prior)


if __name__=='__main__':unittest.main()
