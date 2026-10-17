"""User-approved G1-G8, exact revision binding and preserved source uncertainty."""
import copy
from decimal import Decimal as D
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_googl_analyst_package as p


class AlphabetHistoryAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.view=cls.result['googl_current_history']
        cls.prior=json.loads(subprocess.check_output(['git','show','2b6b650:'+p.OUTPUT],cwd=ROOT))

    def test_exact_user_authorization_original_snapshot_and_audit_chain(self):
        self.assertTrue({k:v for k,v in self.result.items() if k not in ('googl_history_approval','googl_current_history')}==self.prior,'Original Alphabet review changed')
        audit=self.result['googl_history_approval'];self.assertEqual(audit['sequence'],2)
        self.assertEqual(audit['previous'],self.prior['accepted_view']['approval_audit']['sha256'])
        self.assertEqual(audit['source_revision'],p.digest(p.relevant(self.prior)))
        self.assertEqual(audit['review_revision'],self.prior['googl_history_review']['review_revision'])
        self.assertEqual(set(audit['decisions']),{f'G{i}' for i in range(1,9)})
        for r in self.prior['googl_history_review']['consolidated_proposals'][:8]:
            self.assertEqual(audit['decisions'][r['decision_id']],{k:v for k,v in r.items() if k not in ('decision_id','status','accepted','approval_required')})
        p.ManualIdentity(audit['author'],audit['recorded_at_utc'],audit['rationale'])
        self.assertEqual(audit['sha256'],p.digest({k:v for k,v in audit.items() if k!='sha256'}))

    def test_five_times_fourteen_only_within_approved_historical_perimeter(self):
        self.assertEqual(self.view['passed_family_slots'],70)
        self.assertEqual([r['identity'] for r in self.view['periods']],[r['identity'] for r in self.prior['googl_history_review']['periods']])
        for r in self.view['periods']:
            self.assertEqual(len(r['checklist']),14);self.assertEqual({c['field'] for c in r['checklist']},set(r['inputs']))
            self.assertTrue(all(c['status'].startswith('SATISFIED') for c in r['checklist']))
            self.assertTrue(r['analyst_complete']);self.assertEqual(r['remaining_essential_inputs'],[])
        self.assertTrue(self.view['company_completed_for_approved_historical_perimeter'])
        for k in ['complete_debt','complete_reinvestment','phase1_closed','valuation_consumption_approved']:self.assertFalse(self.view[k])

    def test_proxies_precision_distinct_roles_nulls_and_no_additional_charges(self):
        for r,n in zip(self.view['periods'],[11555,15287,11946,15311,21136]):
            x=r['inputs'];da=x['depreciation_amortization'];self.assertTrue(da['accepted']);self.assertEqual(da['origin'],'proxy')
            self.assertEqual(D(da['value_usd']),D(n)*1000000);self.assertEqual(da['precision'],'-6')
            self.assertIsNone(da['complete_expense_da']);self.assertIsNone(r['complete_expense_basis_da'])
            self.assertIsNone(da['finance_amortization_inclusion_assumption']);self.assertFalse(da['additional_rou_addback'])
            sbc=x['stock_based_compensation'];self.assertEqual(sbc['origin'],'proxy');self.assertTrue(sbc['count_once'])
            self.assertEqual(sbc['selected']['precision'],'-8');self.assertEqual(sbc['addback']['precision'],'-6');self.assertIsNone(sbc['rounding_adjustment'])
            self.assertFalse(x['reported_cash_flow_working_capital_movements']['additional_deduction_permitted'])
            self.assertIsNone(x['unclassified_cfo_reconciliation_residual']['value']);self.assertTrue(x['unclassified_cfo_reconciliation_residual']['not_reported_zero'])
            self.assertTrue(all(v is None for v in r['supporting_unknowns'].values()))
        self.assertEqual(self.view['periods'][3]['inputs']['stock_based_compensation']['addback']['value'],'22785000000')

    def test_named_financing_and_one_million_difference_not_plugged(self):
        for i,(r,amount) in enumerate(zip(self.view['periods'],[14930,14999,14616,15859,51043])):
            d=r['inputs']['debt_lease_components'];self.assertEqual(D(d['selected']['value']),D(amount)*1000000)
            self.assertIsNone(d['additional_borrowing']);self.assertFalse(d['complete_debt'])
            self.assertEqual(d['early_finance_already_in_named_debt'],i<3)
            self.assertEqual(d['finance_principal_already_in_debt_repayments'],None if i<3 else True)
            if i<3:self.assertNotIn('finance_total',d['selected']['operands'])
        d=self.view['periods'][-1]['inputs']['debt_lease_components']
        discrepancy=next(c for c in d['source_partition_checks'] if c['check_id']=='operating_lease')
        self.assertEqual(discrepancy['difference_usd'],'1000000');self.assertEqual(discrepancy['status'],'SOURCE_DIFFERENCE_UNRESOLVED')
        self.assertNotIn('op_total',d['selected']['operands']);self.assertEqual(d['operating_lease']['value'],'15954000000')

    def test_current_gross_balances_known_claim_overlap_and_share_split(self):
        for i,(r,amount) in enumerate(zip(self.view['periods'],[139649,113762,110916,95657,126843])):
            x=r['inputs'];cash=x['cash_investment_components'];self.assertEqual(D(cash['selected']['value']),D(amount)*1000000)
            self.assertFalse(cash['unrestricted_or_excess_cash']);self.assertIsNone(cash['unknown_restrictions']);self.assertIsNone(cash['operating_reserve'])
            self.assertIn('nonmarketable_parent',cash['separate_observations'])
            claim=x['other_equity_bridge_claims_assets'];self.assertTrue(claim['nci_includes_redeemable']);self.assertFalse(claim['exhaustive_claims'])
            for k in ['pension','unidentified_claims','pure_nol_economic_value']:self.assertIsNone(claim[k])
            self.assertEqual(claim['known_claims']['preferred_value']['value'],'0')
            shares=x['point_in_time_shares'];self.assertEqual(shares['original_pre_split'],i==0);self.assertFalse(shares['aggregation_or_dilution_approved'])
            self.assertEqual(set(shares['classes']),{'year_end_a','year_end_b','year_end_c'})
        self.assertNotIn('redeemable_nci',self.view['periods'][0]['inputs']['other_equity_bridge_claims_assets']['known_claims'])
        self.assertEqual(self.view['periods'][3]['inputs']['cash_investment_components']['separate_observations']['long_marketable']['value'],'266000000')

    def test_serialization_persistence_staleness_and_tamper_rejection(self):
        self.assertTrue(json.loads((ROOT/p.OUTPUT).read_text())==self.result,'Replay differs')
        self.assertTrue(json.loads(json.dumps(self.result))==self.result,'Round trip differs')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'package.json';path.write_text(json.dumps(self.result,sort_keys=True))
            with patch.object(p,'OUTPUT',str(path)):
                self.assertTrue(p.activate_company_history(json.loads(json.dumps(self.prior,sort_keys=True)))==self.result,'Restart differs')
                for key,value,error in [('source_revision','0'*64,'Stale'),('review_revision','0'*64,'Stale'),('decisions',{},'Unregistered'),('identities',[],'Unregistered'),('previous','0'*64,'Unregistered'),('phase1_closed',True,'Unregistered')]:
                    bad=copy.deepcopy(self.result);a=bad['googl_history_approval'];a[key]=value;a['sha256']=p.digest({k:v for k,v in a.items() if k!='sha256'});path.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(ValueError,error):p.activate_company_history(self.prior)
                bad=copy.deepcopy(self.result);bad['googl_history_approval']['sha256']='0'*64;path.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,'Malformed'):p.activate_company_history(self.prior)
                path.write_text(json.dumps(self.result));changed=copy.deepcopy(self.prior);changed['googl_history_review']['periods'][4]['facts']['op_total']['value']='0'
                with self.assertRaisesRegex(ValueError,'Changed Alphabet'):p.activate_company_history(changed)
        with self.assertRaisesRegex(ValueError,'already exists'):p.history_approval_record(self.result)

    def test_previous_views_audits_and_completed_peers_are_exact(self):
        for name in ['msft','aapl']:
            path='docs/company-data-preparation/'+name+'-analyst-input-package.json'
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show','2b6b650:'+path],cwd=ROOT))
        self.assertEqual(self.result['accepted_view'],self.prior['accepted_view'])
        self.assertEqual(self.view['company_counts'],dict(broad_evidence_assessment=42,company_analyst_packages=3,completed_company_wide_packages=3,partial_company_packages=0,broad_assessment_only=39))


if __name__=='__main__':unittest.main()
