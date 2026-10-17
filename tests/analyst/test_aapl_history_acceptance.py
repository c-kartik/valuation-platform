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
import prepare_aapl_analyst_package as p


class AppleHistoryAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.view=cls.result['aapl_current_history']
        cls.prior=json.loads(subprocess.check_output(['git','show','d6e0ea5:'+p.OUTPUT],cwd=ROOT))

    def test_exact_authorization_chain_and_prior_snapshot(self):
        self.assertTrue({k:v for k,v in self.result.items() if k not in ('aapl_history_approval','aapl_current_history')}==self.prior,'Prior AAPL history changed')
        a=self.result['aapl_history_approval'];self.assertEqual(a['sequence'],2)
        self.assertEqual(a['previous'],self.prior['accepted_view']['approval_audit']['sha256'])
        self.assertEqual(a['source_revision'],p.digest(p.relevant(self.prior)))
        self.assertEqual(set(a['decisions']),{f'A{i}' for i in range(2,11)})
        for r in self.prior['aapl_history_review']['consolidated_proposals'][1:]:
            self.assertEqual(a['decisions'][r['decision_id']],{k:v for k,v in r.items() if k not in ('decision_id','status','accepted','approval_required')})
        p.ManualIdentity(a['author'],a['recorded_at_utc'],a['rationale'])
        self.assertEqual(a['sha256'],p.digest({k:v for k,v in a.items() if k!='sha256'}))

    def test_all_five_existing_checklists_and_scope(self):
        self.assertEqual([r['identity'] for r in self.view['periods']],[r['identity'] for r in self.prior['aapl_history_review']['periods']])
        self.assertEqual(self.view['passed_family_slots'],70)
        for r in self.view['periods']:
            self.assertTrue(r['analyst_complete']);self.assertEqual(r['remaining_essential_inputs'],[])
            self.assertEqual(len(r['checklist']),14);self.assertEqual({x['field'] for x in r['checklist']},set(r['inputs']))
            self.assertTrue(all(c['status'].startswith('SATISFIED') for c in r['checklist']))
        self.assertTrue(self.view['company_completed_for_approved_historical_perimeter'])
        for k in ['complete_debt','complete_reinvestment','phase1_closed','valuation_consumption_approved']:self.assertFalse(self.view[k])

    def test_approved_proxies_unknowns_and_no_extra_charges(self):
        for r,n in zip(self.view['periods'],[11284,11104,11519,11445,11698]):
            x=r['inputs'];da=x['depreciation_amortization'];self.assertTrue(da['accepted']);self.assertEqual(da['origin'],'proxy')
            self.assertEqual(Decimal(da['value_usd']),Decimal(n)*1000000);self.assertIsNone(da['expense_basis_da'])
            self.assertIsNone(da['finance_amortization_inclusion_assumption']);self.assertIsNone(r['complete_expense_basis_da'])
            self.assertTrue(x['stock_based_compensation']['count_once']);self.assertFalse(x['reported_cash_flow_working_capital_movements']['additional_deduction_permitted'])
            self.assertIsNone(x['unclassified_cfo_reconciliation_residual']['value'])
            for k in ['preferred','nci','pension','pure_nol']:self.assertIsNone(x['other_equity_bridge_claims_assets'][k])
            self.assertTrue(all(v is None for v in r['supporting_unknowns'].values()))

    def test_named_selections_rounding_and_nondefault_alternatives(self):
        for r,c,d in zip(self.view['periods'],[62639,48304,61555,65171,54697],[125567,121010,112112,107525,99887]):
            x=r['inputs'];self.assertEqual(Decimal(x['cash_investment_components']['selected']['value']),Decimal(c)*1000000)
            self.assertEqual(Decimal(x['debt_lease_components']['selected']['value']),Decimal(d)*1000000)
            self.assertIsNone(x['debt_lease_components']['additional_borrowing']);self.assertFalse(x['debt_lease_components']['all_lease_alternative']['default'])
            self.assertFalse(x['cash_investment_components']['unrestricted_or_excess_cash']);self.assertTrue(x['debt_lease_components']['current_maturities_already_included'])
        alt=self.result['aapl_history_review']['periods'][3]['restricted_current_alternative']
        self.assertEqual(Decimal(alt['value_usd']),Decimal('49371000000'));self.assertFalse(alt['default']);self.assertFalse(alt['accepted'])
        self.assertEqual(self.view['periods'][3]['inputs']['depreciation_amortization']['precision'],'-6')

    def test_round_trip_and_audit_restart_rejection(self):
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Replay differs')
        self.assertTrue(json.loads(json.dumps(self.result))==self.result,'Round trip differs')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'package.json';path.write_text(json.dumps(self.result))
            with patch.object(p,'OUTPUT',str(path)):
                self.assertTrue(p.activate_company_history(self.prior)==self.result,'Restart differs')
                for key,value,error in [('source_revision','0'*64,'Stale'),('review_revision','0'*64,'Stale'),('decisions',{},'Unregistered'),('identities',[],'Unregistered'),('previous','0'*64,'Unregistered'),('phase1_closed',True,'Unregistered')]:
                    bad=copy.deepcopy(self.result);a=bad['aapl_history_approval'];a[key]=value;a['sha256']=p.digest({k:v for k,v in a.items() if k!='sha256'});path.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(ValueError,error):p.activate_company_history(self.prior)
                bad=copy.deepcopy(self.result);bad['aapl_history_approval']['sha256']='0'*64;path.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,'Malformed'):p.activate_company_history(self.prior)
                path.write_text(json.dumps(self.result));changed=copy.deepcopy(self.prior);changed['aapl_history_review']['periods'][0]['facts']['revenue']['value']='1'
                with self.assertRaisesRegex(ValueError,'Changed AAPL'):p.activate_company_history(changed)
        with self.assertRaisesRegex(ValueError,'already exists'):p.history_approval_record(self.result)

    def test_peers_and_company_counts(self):
        self.assertEqual(self.view['company_counts'],dict(broad_evidence_assessment=42,company_analyst_packages=3,completed_company_wide_packages=2,partial_company_packages=1,broad_assessment_only=39))
        for name in ['msft','googl']:
            path='docs/company-data-preparation/'+name+'-analyst-input-package.json'
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show','d6e0ea5:'+path],cwd=ROOT))


if __name__=='__main__':unittest.main()
