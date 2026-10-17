"""Exact approved effective selections; no source-null or generic-policy repair."""
from copy import deepcopy
from datetime import datetime,timezone
from decimal import Decimal as D
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import activate_company_review_batches as a

class SemiconductorSoftwareActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:json.loads((ROOT/f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json').read_text()) for t in a.SEMICON_SOFTWARE_TICKERS}
        cls.summary=json.loads((ROOT/'docs/company-data-preparation/semiconductor-software-review-batch.json').read_text());cls.decisions=cls.summary['decisions']

    def test_exact27_audits_authority_utc_revisions_and_serialization(self):
        ids=[]
        for t,p in self.packages.items():
            r=p['history_approval'];ids.extend(d['decision_id'] for d in r['decisions'])
            self.assertEqual(r['source_commit'],a.SEMICON_SOFTWARE_BASELINE);self.assertEqual(r['authority'],a.SEMICON_SOFTWARE_AUTHORITY)
            self.assertEqual(r['source_revision'],a.digest(a.relevant(a.parent(p))));self.assertEqual(r['proposal_revision'],a.digest(a.relevant([d for d in self.decisions if d['ticker']==t])))
            self.assertEqual(r['sha256'],a.digest({k:v for k,v in r.items() if k!='sha256'}));self.assertEqual(r['identities'],[x['identity'] for x in p['periods']])
            at=datetime.fromisoformat(r['recorded_at_utc']);self.assertEqual(at.utcoffset(),timezone.utc.utcoffset(at));self.assertLessEqual(at,datetime.now(timezone.utc))
            self.assertTrue(a.activate(a.parent(p),self.decisions,r)==p,'Exact overlay replay '+t);self.assertTrue(json.loads(json.dumps(p))==p,'Round trip '+t)
        self.assertEqual(len(ids),27);self.assertEqual(set(ids),{d['decision_id'] for d in self.decisions})

    def test_all_five_years14_families_approved_scope_not_perfect_disclosure(self):
        from valuation_platform.analyst.historical_inputs import Field
        for p in self.packages.values():
            view=p['current_history'];self.assertEqual(view['passed_family_slots'],70);self.assertTrue(view['company_completed_for_approved_historical_perimeter'])
            self.assertFalse(view['phase1_closed']);self.assertFalse(view['valuation_consumption_approved']);self.assertTrue(all(x['status']=='ACTIVE' for x in view['active_decisions']))
            for source,r in zip(p['periods'],view['periods']):
                self.assertEqual(set(r['inputs']),{f.value for f in Field});self.assertEqual(r['passed_family_slots'],14);self.assertEqual(r['remaining_essential_inputs'],[])
                self.assertEqual(r['original_supporting_unknowns'],source['original_supporting_unknowns']);self.assertTrue(all(x is None for x in r['original_supporting_unknowns'].values()))
                self.assertIsNone(r['complete_expense_basis_da']);self.assertFalse(r['complete_debt']);self.assertFalse(r['complete_reinvestment'])
                v=r['inputs'];self.assertIsNone(v['unclassified_cfo_reconciliation_residual']['value']);self.assertTrue(v['unclassified_cfo_reconciliation_residual']['not_reported_zero'])
                self.assertEqual(v['reported_cash_flow_working_capital_movements']['rows'],source['movement_rows']);self.assertFalse(v['reported_cash_flow_working_capital_movements']['additional_deduction_permitted'])
                self.assertTrue(all(x['caption'].strip().lower().startswith('deferred income tax') for x in v['deferred_taxes']['displayed_rows']))
                self.assertFalse(any('deferred revenue' in x['caption'].lower() for x in v['deferred_taxes']['displayed_rows']))
                self.assertIsNone(v['debt_lease_components']['additional_borrowing']);self.assertEqual(v['debt_lease_components']['no_additional_adjustment']['origin'],'analyst_assumption');self.assertTrue(v['stock_based_compensation']['count_once'])

    def test_exact_financial_values_signs_proxy_and_inherited_precision(self):
        expected={'LRCX':(['333.739','342.432','359.699','386.277','441.533'],['-546.034','-501.568','-396.670','-759.186','-966.405'],['5005.830','5011.541','4983.334','4484.505','3734.563']),
            'PLTR':(['14.897','22.522','33.354','31.587','26.145'],['-12.627','-40.027','-15.114','-12.634','-33.882'],[0]*5),
            'AMAT':([394,444,515,392,435],[-668,-787,-1106,-1190,-2260],[5452,5457,5663,6259,6555])}
        for t,p in self.packages.items():
            for i,(source,r) in enumerate(zip(p['periods'],p['current_history']['periods'])):
                v=r['inputs'];items=[v['depreciation_amortization'],v['cash_capex'],v['debt_lease_components']['selected']]
                for j,x in enumerate(items):self.assertEqual(D(x['value'])/1000000,D(expected[t][j][i]),(t,i,j))
                self.assertEqual(items[0]['origin'],'proxy');self.assertEqual(items[1]['sign_multiplier'],-1)
                da=next(c for c in source['calculations'] if c['input_id']=='limited_da_proxy');self.assertEqual(items[0]['precision'],da['precision'])
                self.assertFalse(items[0]['additional_rou_addback']);self.assertFalse(items[1]['complete_reinvestment'])

    def test_lrcx_broader_investment_plan_assets_claims_and_embedded_finance(self):
        p=self.packages['LRCX']
        for source,r in zip(p['periods'],p['current_history']['periods']):
            v=r['inputs'];inv=v['cash_capex'];self.assertEqual(inv['origin'],'proxy');self.assertEqual(inv['investment_perimeter'],'BROADER_COMBINED_PPE_INTANGIBLES_APPROVED_PROXY');self.assertIsNone(inv['pure_cash_ppe']);self.assertFalse(inv['pure_ppe_scope_approved'])
            debt=v['debt_lease_components'];self.assertTrue(debt['finance_leases_already_included']);self.assertEqual(debt['selected']['operands'],['debt_finance_current','debt_finance_long'])
            self.assertIn('inventory_transfers',inv['other_disclosures']);claims=v['other_equity_bridge_claims_assets'];self.assertTrue(claims['plan_assets_liabilities_not_automatically_netted'])
            for k in ('deferred_plan_obligation','deferred_plan_investments','accrued_compensation_caption'):self.assertEqual(claims['known_populations'][k]['value'],source['facts'][k]['value'])
            self.assertNotEqual(claims['known_populations']['accrued_compensation_caption']['value'],claims['known_populations']['deferred_plan_obligation']['value'])

    def test_pltr_face_tax_partial_proofs_zero_named_scope_and_classes(self):
        p=self.packages['PLTR'];self.assertEqual([r['cfo_reconciliation']['status'] for r in p['periods']],['PARTIAL']*4+['SUPPORTED'])
        for i,(source,r) in enumerate(zip(p['periods'],p['current_history']['periods'])):
            v=r['inputs'];self.assertEqual(v['reported_cfo']['original_parser_status'],source['cfo_reconciliation']['status'])
            self.assertEqual(v['reported_cfo']['value'],source['facts']['cfo']['value'])
            if i<4:self.assertTrue(v['reported_cfo']['independent_reconciliation_reference'].endswith('/independent_displayed_cfo'));self.assertEqual(source['independent_displayed_cfo']['difference'],'0')
            tax=v['reported_tax_context'];self.assertEqual(tax['provision']['value'],source['facts']['face_tax']['value']);self.assertTrue(tax['face_provision_selected']);self.assertFalse(tax['generic_tax_conflicts_cleared']);self.assertTrue(tax['no_new_ratio_computed']);self.assertFalse(tax['future_rate_approved'])
            if i>0:self.assertEqual(source['reported_tax_policy_replay']['fields']['provision']['status'],'CONFLICTING')
            debt=v['debt_lease_components'];self.assertEqual(D(debt['selected']['value']),0);self.assertFalse(debt['complete_debt']);self.assertIsNone(debt['additional_borrowing']);self.assertIsNone(debt['no_additional_adjustment']['value'])
            shares=v['point_in_time_shares'];self.assertGreaterEqual(len(shares['selected_populations']),4);self.assertFalse(shares['automatic_aggregation_or_dilution']);self.assertFalse(shares['conversion_or_dilution_approved'])
            self.assertIn('restricted_note_current',v['cash_investment_components']['other_balances']);self.assertFalse(v['cash_investment_components']['unrestricted_or_excess_cash'])

    def test_amat_incentive_stocks_not_cash_sbc_and_financing_overlap(self):
        p=self.packages['AMAT'];r=p['current_history']['periods'][-1];v=r['inputs']
        self.assertEqual(v['stock_based_compensation']['selected']['value'],'660000000');self.assertEqual(v['stock_based_compensation']['addback']['value'],'668000000')
        self.assertEqual(v['cash_capex']['value'],'-2260000000');self.assertIn('not annual cash receipts',v['cash_capex']['incentive_limitation'])
        debt=p['current_history']['periods'][3]['inputs']['debt_lease_components'];self.assertEqual(debt['selected']['operands'],['debt_long','face_short_debt']);self.assertNotIn('debt_current',debt['selected']['operands'])
        self.assertIn('finance_lease',p['current_history']['periods'][2]['inputs']['debt_lease_components']['selected']['operands'])
        for r in p['current_history']['periods']:self.assertIsNone(r['inputs']['debt_lease_components']['finance_leases_already_included'])

    def test_persistence_restart_stale_operands_evidence_and_missing_approval(self):
        for t,p in self.packages.items():
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'view.json';path.write_text(json.dumps(p));self.assertTrue(a.load_if_approved(path,a.parent(p),self.decisions)==p)
                path.write_text(json.dumps(a.parent(p)));self.assertNotIn('current_history',a.load_if_approved(path,a.parent(p),self.decisions))
            for kind in ('value','precision','scope','tax','evidence','alternative','identity','calculation'):
                changed=deepcopy(a.parent(p));r=changed['periods'][0]
                if kind in ('value','precision','scope'):r['facts']['cfo'][kind]='1'
                elif kind=='tax':r['reported_tax_policy_replay']['fields']['pretax']['value']='1'
                elif kind=='evidence':r['sources'][0]['sha256']='0'*64
                elif kind=='alternative':r['alternatives']['tax']['competing_values'].append('1')
                elif kind=='calculation':r['calculations'][0]['value']='1'
                else:r['identity']['annual_end']='2000-01-01'
                with self.assertRaisesRegex(ValueError,'exact approved' if kind=='identity' else 'Stale'):a.activate(changed,self.decisions,p['history_approval'])
            with self.assertRaises(ValueError):a.activate(a.parent(p),[d for d in self.decisions if d['decision_id']!=t+'-INV'],p['history_approval'])
            forged=deepcopy(p['history_approval']);forged['authority']='unapproved';forged['sha256']=a.digest({k:v for k,v in forged.items() if k!='sha256'})
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(a.parent(p),self.decisions,forged)

    def test_parent_source_history21_peers_frozen_and_company_counts(self):
        for t,p in self.packages.items():
            path=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json';self.assertEqual(json.dumps(a.parent(p),sort_keys=True,indent=2).encode()+b'\n',subprocess.check_output(['git','show',a.SEMICON_SOFTWARE_BASELINE+':'+path],cwd=ROOT))
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',a.SEMICON_SOFTWARE_BASELINE,'docs/company-data-preparation'],cwd=ROOT,text=True).splitlines()
        peers=[p for p in paths if p.endswith('-analyst-input-package.json') and not any('/'+t.lower()+'-' in p for t in a.SEMICON_SOFTWARE_TICKERS)]
        self.assertEqual(len(peers),21)
        for path in peers:self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',a.SEMICON_SOFTWARE_BASELINE+':'+path],cwd=ROOT))
        self.assertEqual(subprocess.check_output(['git','diff','--name-only',a.SEMICON_SOFTWARE_BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True),'')
        self.assertEqual(self.summary['approval_activation']['current_company_counts'],dict(broadly_assessed=42,completed_scoped=22,approved_partial=2,pending_reviews=0,assessment_only=18))

if __name__=='__main__':unittest.main()
