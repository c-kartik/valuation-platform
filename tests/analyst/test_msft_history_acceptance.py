"""Scoped company-history acceptance, separate from frozen/source histories."""
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


class MSFTHistoryAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.view=cls.result['msft_current_history'];cls.f=p.Filing(2025)
        cls.prior=json.loads(subprocess.check_output(['git','show','5ac9ea2:'+p.OUTPUT],cwd=ROOT))

    def test_exact_approval_and_entire_prior_snapshot_preserved(self):
        self.assertTrue({k:v for k,v in self.result.items() if k not in ('msft_history_approval','msft_current_history')}==self.prior,'Prior source/proposal/acceptance changed')
        audit=self.result['msft_history_approval']
        self.assertEqual(audit['sequence'],6);self.assertEqual(audit['previous'],self.prior['fy2025_approval']['sha256'])
        self.assertEqual(audit['source_revision'],p.digest(p.relevant(self.prior)))
        self.assertEqual(audit['sha256'],p.digest({k:v for k,v in audit.items() if k!='sha256'}))
        for row in self.prior['msft_history_review']['consolidated_proposals']:
            self.assertEqual(audit['decisions'][row['decision_id']],{k:v for k,v in row.items() if k not in ('decision_id','status','accepted')})
        self.assertEqual(set(audit['exceptions']),{'E1','E2'})
        self.assertIn('unknown',audit['exceptions']['E1']);self.assertIn('non-default',audit['exceptions']['E2'])
        p.ManualIdentity(audit['author'],audit['recorded_at_utc'],audit['rationale'])
        with self.assertRaisesRegex(ValueError,'already exists'):p.msft_history_acceptance_record(self.result)

    def test_five_selected_identities_and_seventy_passes(self):
        rows=self.view['periods'];self.assertEqual([r['identity'] for r in rows],self.prior['msft_history_review']['selected_identities'])
        fields=[r['field'] for r in self.prior['fy2026_analyst_checklist']['checklist']]
        self.assertEqual(self.view['family_slots'],70);self.assertEqual(self.view['passed_family_slots'],70)
        for row in rows:
            self.assertEqual([r['field'] for r in row['checklist']],fields)
            self.assertEqual(set(row['inputs']),set(fields));self.assertEqual(row['remaining_essential_inputs'],[])
            self.assertTrue(row['analyst_complete']);self.assertTrue(all(r['status'].startswith('SATISFIED') for r in row['checklist']))
        self.assertTrue(self.view['company_completed_for_approved_historical_perimeter'])
        for key in ('phase_closed','valuation_consumption_approved','complete_debt','complete_reinvestment'):self.assertFalse(self.view[key])

    def test_source_selected_amounts_cash_sign_precision_and_roles(self):
        for i,expected in enumerate([('198270','83383','-23886','89035'),('211915','88523','-28107','87582'),('245122','109433','-44477','118548'),('281724','128528','-64551','136162'),('331839','155237','-115948','182935')]):
            inputs=self.view['periods'][i]['inputs']
            self.assertEqual(tuple(str(Decimal(inputs[k]['value'])/1000000) for k in ('revenue','ebit','cash_capex','reported_cfo')),expected)
            self.assertTrue(inputs['stock_based_compensation']['economic_proxy_once'])
            self.assertNotEqual(inputs['depreciation_amortization'],inputs['unclassified_cfo_reconciliation_residual']['mixed_observation'])
        self.assertIn('-9',self.view['periods'][1]['inputs']['depreciation_amortization']['precision'])
        self.assertEqual([r['inputs']['deferred_taxes']['value'] for r in self.view['periods']],['-5702000000','-6059000000','-4738000000','-7056000000','14189000000'])

    def test_named_financing_and_cp_alternatives_no_double_count(self):
        expected=['64683000000','64304000000','78775000000','89323000000','106888000000']
        for r,value in zip(self.view['periods'],expected):
            debt=r['inputs']['debt_lease_components'];self.assertEqual(debt['selected'].get('value',debt['selected'].get('value_usd')),value)
            self.assertIsNone(debt['additional_borrowing']);self.assertFalse(debt['complete_debt'])
        old=self.prior['msft_history_review']['remaining_periods'][2]
        self.assertEqual(old['face_cp_observation']['raw_value'],'6693000000')
        self.assertEqual({c['raw_value'] for c in old['cp_candidates']},{'6693000000','6700000000'})
        self.assertEqual(Decimal(old['facts']['term_debt']['value'])+Decimal(old['facts']['finance_liability']['value'])+Decimal(old['face_cp_observation']['raw_value']),Decimal(expected[2]))
        self.assertNotIn('current_term',old['calculations']['named_financing']['operands'])

    def test_unknowns_exclusions_and_independent_cfo_not_cash_delta(self):
        for row in self.view['periods']:
            inputs=row['inputs'];movements=inputs['reported_cash_flow_working_capital_movements']
            self.assertEqual(len(movements['rows']),9);self.assertFalse(movements['additional_deduction_permitted']);self.assertFalse(movements['book_delta_nwc'])
            self.assertIsNone(inputs['unclassified_cfo_reconciliation_residual']['value'])
            for key in ('preferred','nci','pension','pure_nol'):self.assertIsNone(inputs['other_equity_bridge_claims_assets'][key])
        for row,prior in zip(self.view['periods'][:3],self.prior['msft_history_review']['remaining_periods']):
            self.assertIsNone(row['capital_creditors']);self.assertIsNone(row['equity_method_subamount'])
            self.assertEqual(sum(Decimal(t['contribution_usd']) for t in prior['cfo_reconciliation']['terms']),Decimal(row['inputs']['reported_cfo']['value']))
            self.assertEqual(len(prior['cfo_reconciliation']['terms']),14)
        self.assertFalse(self.view['periods'][0]['inputs']['point_in_time_shares']['aggregation_or_dilution_approved'])

    def test_all_current_source_references_resolve(self):
        def visit(node):
            if isinstance(node,dict):
                for k,v in node.items():
                    if k.endswith('_reference') and isinstance(v,str) and v.startswith('/'):
                        target=self.result
                        for part in v.split('/')[1:]:target=target[int(part)] if isinstance(target,list) else target[part]
                        self.assertIsNotNone(target)
                    visit(v)
            elif isinstance(node,list):
                for v in node:visit(v)
        visit(self.view)

    def test_persistence_serialization_stale_and_unregistered_rejection(self):
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Replay differs')
        self.assertTrue(json.loads(json.dumps(self.result))==self.result,'Round trip differs')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'package.json'
            with patch.object(p,'OUTPUT',str(path)):
                path.write_text(json.dumps(self.result))
                self.assertTrue(p.activate_msft_history(self.f,self.prior)==self.result,'Restart differs')
                for key,value,error in [('source_revision','0'*64,'Stale'),('decisions',{},'Unregistered'),('exceptions',{},'Unregistered'),('identities',[],'Unregistered'),('previous','0'*64,'Unregistered')]:
                    bad=copy.deepcopy(self.result);a=bad['msft_history_approval'];a[key]=value;a['sha256']=p.digest({k:v for k,v in a.items() if k!='sha256'});path.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(ValueError,error):p.activate_msft_history(self.f,self.prior)
                bad=copy.deepcopy(self.result);bad['msft_history_approval']['sha256']='0'*64;path.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,'Malformed'):p.activate_msft_history(self.f,self.prior)
                path.write_text(json.dumps(self.result));changed=copy.deepcopy(self.prior);changed['msft_history_review']['remaining_periods'][0]['facts']['cfo']['value']='1'
                with self.assertRaisesRegex(ValueError,'Changed preceding'):p.activate_msft_history(self.f,changed)

    def test_company_counts_do_not_extrapolate_pilots_or_execute_next_batch(self):
        self.assertEqual(self.view['company_counts'],dict(broad_evidence_assessment=42,company_analyst_packages=3,completed_company_wide_packages=1,partial_company_packages=2,broad_assessment_only=39))
        self.assertIn('AAPL frozen FY2021-FY2025',self.view['next_company_batch']);self.assertIn('not started',self.view['next_company_batch'])


if __name__=='__main__':unittest.main()
