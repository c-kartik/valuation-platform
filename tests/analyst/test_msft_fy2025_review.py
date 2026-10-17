"""Proposal-only exact-period review, independent of FY2026 approvals."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_msft_analyst_package as p


class MSFTFY2025ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.view=cls.result['fy2025_completeness_review'];cls.f=p.Filing(2025)
        cls.prior=json.loads(subprocess.check_output(['git','show',cls.view['basis_commit']+':'+p.OUTPUT],cwd=ROOT))

    def test_entire_prior_package_and_fy2026_pass_preserved(self):
        parent={k:v for k,v in self.result.items() if k not in ('fy2025_completeness_review','fy2025_approval','msft_history_review')}
        self.assertTrue(parent==self.prior,'Prior source/approval/selection changed')
        self.assertEqual(self.view['parent_revision'],p.digest(p.relevant(parent)))
        self.assertTrue(self.result['fy2026_analyst_checklist']['analyst_complete'])
        self.assertEqual(self.result['fy2026_financing_approval'],self.prior['fy2026_financing_approval'])
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Exact review replay differs')

    def test_fourteen_families_and_all_decisions_accounted_for(self):
        v=self.view;fields=[r['field'] for r in v['checklist']]
        self.assertEqual(fields,[r['field'] for r in self.result['fy2026_analyst_checklist']['checklist']])
        self.assertEqual(len(fields),14);self.assertEqual(len(set(fields)),14)
        self.assertEqual(sum(r['status'].startswith('SATISFIED_') for r in v['checklist']),10)
        self.assertEqual(sum(r['status']=='PENDING_APPROVAL' for r in v['checklist']),4)
        expected={f'25-D{i}' for i in range(1,8)}
        self.assertEqual({d['decision_id'] for d in v['decisions']},expected)
        self.assertEqual({d for r in v['checklist'] for d in r['pending_decisions']},expected)
        self.assertTrue(all(d['status']==p.PROPOSED and d['accepted'] is False for d in v['decisions']))
        self.assertEqual(v['financial_approvals_added'],0);self.assertFalse(v['fy2026_authority_transferred'])
        self.assertFalse(v['analyst_complete']);self.assertFalse(v['phase_closed']);self.assertFalse(v['valuation_consumption_approved'])
        self.assertEqual({r['input_id'] for r in v['original_requirement_dispositions']},{r['input_id'] for r in self.result['periods'][0]['unresolved_requirements']})

    def test_cfo_control_and_independently_displayed_fy2025_figures(self):
        v=self.view;period=self.result['periods'][0];entries={e['input_id']:e for e in period['inputs']}
        terms=period['cfo_reconciliation']['terms']
        self.assertEqual(len(terms),14);self.assertEqual(v['cfo_control']['adjustments_excluding_net_income'],13)
        self.assertEqual(sum(Decimal(entries[k]['value']) for k in terms),Decimal('136162000000'))
        expected={'revenue':'281724','ebit':'128528','expense_da':'28000','sbc_cost_proxy':'11974','current_liquidity':'94565'}
        self.assertEqual({k:entries[k]['display_value'] for k in expected},expected)
        self.assertIn('Depreciation, amortization, and other 34,153',v['passages'][0]['exact_excerpt'])
        self.assertIn('Net cash from operations 136,162',v['passages'][0]['exact_excerpt'])
        self.assertEqual(entries['reported:DepreciationAmortizationAndOther']['value'],'34153000000')
        self.assertEqual(entries['reported:GainLossOnInvestmentsAndDerivativeInstruments']['value'],'609000000')
        self.assertEqual(entries['reported:DeferredIncomeTaxExpenseBenefit']['value'],'-7056000000')
        self.assertEqual(v['identity']['annual_start'],'2024-07-01')

    def test_exact_primary_new_observations_and_no_absence_zeros(self):
        for fact in self.view['observations'].values():
            for o in fact['occurrences']:
                node=self.f.root[o['ordinal']];attrs,text=self.f.inline.facts[node.get('id')]
                self.assertEqual(p.inline_amount(attrs,text),Decimal(o['raw_value']))
                self.assertEqual(o['end'],'2025-06-30');self.assertEqual(o['dimensions'],[])
        self.assertEqual(self.view['observations']['retirement_cost']['value'],'1800000000')
        self.assertEqual(self.view['observations']['retirement_cost']['precision'],'-8')
        for passage in self.view['passages']:
            self.assertIn(passage['exact_excerpt'],self.f.text)
            self.assertEqual(passage['source_body_sha256'],self.f.primary.artifact.sha256)
        cp=self.view['cp_scope'];self.assertEqual(cp['reported_cp_usd'],'0');self.assertIsNone(cp['broader_short_borrowing_usd'])
        self.assertIn('ONLY as CP',cp['historical_label_limitation'])
        self.assertIn('no commercial paper issued or outstanding',self.view['passages'][2]['exact_excerpt'])

    def test_evidence_references_and_round_trip(self):
        for row in self.view['checklist']+self.view['decisions']:
            for ref in row['evidence_references']:
                node=self.result
                for key in ref.split('/')[1:]:node=node[int(key)] if isinstance(node,list) else node[key]
                self.assertIsNotNone(node)
        self.assertEqual(self.view,json.loads(json.dumps(self.view)))
        self.assertEqual(len(self.result['periods'][0]['unresolved_requirements']),14)

    def test_wrong_period_tampering_and_incomplete_reconciliation_rejected(self):
        with self.assertRaisesRegex(ValueError,'Wrong FY2025'):p.attach_fy2025_review(p.Filing(2026),self.prior)
        changed=copy.deepcopy(self.prior);changed['periods'][0]['cfo_reconciliation']['terms'].pop()
        with self.assertRaisesRegex(ValueError,'reconciliation changed'):p.attach_fy2025_review(self.f,changed)
        f=p.Filing(2025);f.root=copy.deepcopy(f.root)
        ordinal=self.view['observations']['retirement_cost']['occurrences'][0]['ordinal'];f.root[ordinal].text='1'
        with self.assertRaisesRegex(ValueError,'representation mismatch'):p.attach_fy2025_review(f,self.prior)


if __name__=='__main__':unittest.main()
