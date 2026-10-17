"""One-period retained review: no approvals, financial defaults or phase closure."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import unittest
from tests.analyst import preservation_projection

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_msft_analyst_package as p


class MSFTCompletionAttemptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.attempt=cls.result['fy2026_completeness_attempt']
        cls.original=json.loads(subprocess.check_output(['git','show',cls.attempt['baseline']+':'+p.OUTPUT],cwd=ROOT))

    def test_exact_replay_and_original_approved_payload_preserved(self):
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Attempt replay differs')
        parent={k:v for k,v in self.result.items() if k not in ('fy2026_completeness_attempt','fy2026_operation_approval','fy2026_operations_view','fy2026_claim_assumption_approval','fy2026_claim_assumptions_view','fy2026_financing_approval','fy2026_analyst_checklist','fy2025_completeness_review','fy2025_approval','msft_history_review','msft_history_approval','msft_current_history')}
        self.assertTrue(parent==self.original,'Prior facts/proposals/accepted view changed')
        self.assertEqual(self.attempt['base_package_revision'],p.digest(p.relevant(parent)))
        self.assertEqual(json.loads(json.dumps(self.result)),self.result)

    def test_every_family_and_original_requirement_accounted_for(self):
        self.assertEqual(len({r['field'] for r in self.attempt['checklist']}),14)
        original=self.original['periods'][1]['unresolved_requirements']
        mapped=self.attempt['original_requirement_dispositions']
        self.assertEqual({r['input_id'] for r in original},{r['input_id'] for r in mapped})
        for r in mapped:self.assertTrue(r['original_null_preserved'])
        self.assertEqual(len(original),14)
        self.assertFalse(self.attempt['analyst_complete'])
        self.assertEqual(self.attempt['approvals_added'],0)
        self.assertTrue(all(not d['accepted'] and d['status']==p.PROPOSED for d in self.attempt['decisions']))
        self.assertEqual({r['input_id'] for r in self.attempt['unsolved_essential_inputs']},{'commercial_paper','preferred_nci_pension'})
        self.assertTrue(all(r['value'] is None for r in self.attempt['unsolved_essential_inputs']))

    def test_primary_bound_commercial_paper_asset_is_not_missing_borrowing(self):
        fact=self.attempt['supported_resolutions'][0]['observation'];f=p.Filing(2026)
        self.assertEqual(fact['value'],'2987000000');self.assertEqual(fact['precision'],'-6')
        for o in fact['occurrences']:
            node=f.root[o['ordinal']];attrs,text=f.inline.facts[node.get('id')]
            self.assertEqual(Decimal(node.text),Decimal('2987000000'))
            self.assertEqual(p.inline_amount(attrs,text),Decimal('2987000000'))
            self.assertIn(['us-gaap:FinancialInstrumentAxis','us-gaap:CommercialPaperMember'],o['dimensions'])
            self.assertEqual(o['end'],'2026-06-30')
        self.assertIsNone(self.result['accepted_view']['periods'][1]['additional_short_borrowing']['value_usd'])

    def test_independent_displayed_fourteen_terms_and_nine_movements(self):
        facts=self.result['periods'][1]['facts'];fix=self.attempt['supported_resolutions'][1]
        self.assertEqual(len(fix['term_references']),14)
        self.assertEqual(len(fix['movement_references']),9)
        expected=[133749,38534,12405,-11047,14189,-12737,-461,-2627,-3964,5268,9361,-1875,6847,-4707]
        entries={e['input_id']:e for e in self.result['periods'][1]['inputs']}
        ids=self.result['periods'][1]['cfo_reconciliation']['terms']
        f=p.Filing(2026)
        for key,amount in zip(ids,expected):
            self.assertEqual(Decimal(entries[key]['value']),Decimal(amount)*1000000)
            source=facts[key.removeprefix('reported:')]
            for o in source['occurrences']:
                attrs,text=f.inline.facts[f.root[o['ordinal']].get('id')]
                self.assertEqual(p.inline_amount(attrs,text),Decimal(o['raw_value']))
        self.assertEqual(sum(expected),182935)
        self.assertEqual(fix['sum_usd'],'182935000000')
        self.assertEqual(fix['reported_cfo_usd'],'182935000000')
        self.assertFalse(any('residual' in e['input_id'] for e in entries.values()))

    def test_original_assumption_precision_and_claims_are_not_promoted(self):
        v=self.result['accepted_view']['periods'][1]
        self.assertFalse(v['expense_da']['source_confirmed_overlap'])
        self.assertFalse(v['borrowings']['complete_debt'])
        self.assertFalse(v['cash']['unrestricted_or_excess_cash'])
        self.assertEqual(v,self.original['accepted_view']['periods'][1])
        r=self.result['decision_resolution']['periods'][1]['additional_facts']
        self.assertEqual(r['legal_accrual']['value'],'553000000')
        self.assertEqual(r['legal_additional_exposure']['value'],'400000000')

    def test_operation_evidence_pointers_and_measured_window(self):
        def walk(value):
            if isinstance(value,dict):
                for x in value.values():walk(x)
            elif isinstance(value,list):
                for x in value:walk(x)
            elif isinstance(value,str) and value.startswith(('/periods/','/accepted_view/','/decision_resolution/')):
                cursor=self.result
                for token in value.split('/')[1:]:cursor=cursor[int(token)] if isinstance(cursor,list) else cursor[token]
        walk(self.attempt)
        from datetime import datetime
        w=self.attempt['work_record']
        self.assertEqual((datetime.fromisoformat(w['implementation_checkpoint_at_utc'])-datetime.fromisoformat(w['started_at_utc'])).total_seconds(),471)
        self.assertEqual(w['sec_requests'],0)

    def test_stale_accepted_source_and_wrong_period_rejected(self):
        f=p.Filing(2026)
        changed=copy.deepcopy(self.original);changed['periods'][1]['facts']['ar']['value']='1'
        with self.assertRaisesRegex(ValueError,'Stale MSFT acceptance'):p.attach_fy2026_attempt(f,changed)
        changed=copy.deepcopy(self.original);changed['accepted_view']['periods'][1]['additional_short_borrowing']['value_usd']='0'
        with self.assertRaisesRegex(ValueError,'Changed accepted MSFT view'):p.attach_fy2026_attempt(f,changed)
        f.year=2025
        with self.assertRaisesRegex(ValueError,'Wrong MSFT'):p.attach_fy2026_attempt(f,self.original)

    def test_projection_cannot_hide_an_old_fact_or_policy_change(self):
        path=p.OUTPUT;before=(ROOT/path).read_bytes();changed=copy.deepcopy(self.result)
        changed['periods'][1]['facts']['ar']['value']='1'
        self.assertNotEqual(preservation_projection(path,before),preservation_projection(path,json.dumps(changed).encode()))
        path='scripts/prepare_msft_analyst_package.py';before=(ROOT/path).read_bytes()
        self.assertNotEqual(preservation_projection(path,before),preservation_projection(path,before.replace(b'FloatValue',b'OtherValue') if b'FloatValue' in before else before.replace(b'class Filing:',b'class ChangedFiling:')))


if __name__=='__main__':unittest.main()
