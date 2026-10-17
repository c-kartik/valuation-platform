"""Exact user-approved judgments, not reported zeros or source-gap repairs."""
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


class MSFTClaimAssumptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.view=cls.result['fy2026_claim_assumptions_view']
        cls.prior=json.loads(subprocess.check_output(['git','show',p.FY2026_CLAIMS_BASIS+':'+p.OUTPUT],cwd=ROOT))
        cls.f=p.Filing(2026)

    def test_entire_prior_package_and_audit_history_preserved(self):
        parent={k:v for k,v in self.result.items() if k not in ('fy2026_claim_assumption_approval','fy2026_claim_assumptions_view','fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review','fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
        self.assertTrue(parent==self.prior,'Original facts, nulls, D1-D3 or proposal history changed')
        self.assertEqual((ROOT/p.ACCEPTANCE_PATH).read_bytes(),subprocess.check_output(['git','show',p.FY2026_CLAIMS_BASIS+':'+p.ACCEPTANCE_PATH],cwd=ROOT))
        self.assertEqual(self.result,json.loads(json.dumps(self.result)))
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Replay differs')

    def test_three_approved_assumptions_are_not_reported_values(self):
        view=self.view;record=self.result['fy2026_claim_assumption_approval']
        self.assertEqual(len(view['assumptions']),3)
        self.assertEqual({r['population'] for r in view['assumptions']},set(p.FY2026_APPROVED_CLAIM_ASSUMPTIONS))
        self.assertEqual(record['sequence'],3)
        self.assertEqual(record['previous'],self.prior['fy2026_operation_approval']['sha256'])
        self.assertEqual(record['source_revision'],p.digest(p.relevant(self.prior)))
        self.assertEqual(view['identity']['annual_end'],'2026-06-30')
        for row in view['assumptions']:
            self.assertEqual(row['origin'],'analyst_assumption')
            self.assertEqual(row['status'],'ADDRESSED_BY_APPROVED_ASSUMPTION')
            self.assertIsNone(row['source_value']);self.assertIsNone(row['adjustment_value'])
            self.assertFalse(row['reported_zero']);self.assertFalse(row['immateriality_finding'])
            self.assertFalse(row['source_gap_resolved'])
            self.assertIn('not bounded',row['uncertainty'])
            self.assertIn('potentially undisclosed claim',row['economic_consequence'])
            source=self.result
            for key in row['evidence_reference'].split('/')[1:]:source=source[int(key)] if isinstance(source,list) else source[key]
            self.assertEqual(source['population'],row['population'])
            self.assertEqual(source['evidence_reason'],row['rationale'])
            self.assertIsNone(source['value_usd']);self.assertFalse(source['resolved'])
        self.assertIn('international',view['assumptions'][-1]['uncertainty'])

    def test_only_claim_operation_addressed_short_debt_still_essential(self):
        v=self.view
        self.assertEqual([r['input_id'] for r in v['remaining_essential_inputs']],['commercial_paper'])
        self.assertIsNone(v['remaining_essential_inputs'][0]['value'])
        self.assertIsNone(self.result['accepted_view']['periods'][1]['additional_short_borrowing']['value_usd'])
        self.assertEqual(v['short_debt_zero_status'],'REJECTED_NOT_SELECTED')
        for key in ('named_debt_subtotal_complete','unrelated_requirements_waived','analyst_complete','phase_closed','valuation_consumption_approved'):
            self.assertFalse(v[key])
        self.assertEqual(v['financial_sufficiency'],'NOT_ASSESSED')

    def test_persistence_staleness_and_invalid_authorization_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'package.json';path.write_text(json.dumps(self.result))
            with patch.object(p,'OUTPUT',str(path)):
                expected={k:v for k,v in self.result.items() if k not in ('fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review','fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
                self.assertTrue(p.apply_fy2026_claim_assumptions(self.f,self.prior)==expected,'Prior claim overlay changed')
                for key,value,error in [('decisions',{'preferred_equity':'reported zero'},'Unregistered'),
                                        ('source_revision','0'*64,'Stale'),('previous','0'*64,'Unregistered'),
                                        ('recorded_at_utc','2026-10-17T08:00:00','UTC')]:
                    bad=copy.deepcopy(self.result);record=bad['fy2026_claim_assumption_approval']
                    record[key]=value;record['sha256']=p.digest({k:v for k,v in record.items() if k!='sha256'})
                    path.write_text(json.dumps(bad))
                    with self.assertRaises(ValueError):p.apply_fy2026_claim_assumptions(self.f,self.prior)
                path.write_text(json.dumps(self.result))
                changed=copy.deepcopy(self.prior)
                changed['fy2026_operations_view']['population_review']['populations'][1]['evidence_reason']='changed'
                with self.assertRaisesRegex(ValueError,'Changed operation/source'):p.apply_fy2026_claim_assumptions(self.f,changed)
                changed=copy.deepcopy(self.result);changed.pop('fy2026_claim_assumption_approval');path.write_text(json.dumps(changed))
                with self.assertRaises(KeyError):p.apply_fy2026_claim_assumptions(self.f,self.prior)

    def test_no_implicit_renewal_or_other_period(self):
        with self.assertRaisesRegex(ValueError,'already exists'):p.fy2026_claim_assumption_record(self.result)
        with self.assertRaisesRegex(ValueError,'Wrong FY2026'):p.apply_fy2026_claim_assumptions(p.Filing(2025),self.prior)


if __name__=='__main__':unittest.main()
