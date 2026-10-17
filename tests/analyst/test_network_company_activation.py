"""Scoped user acceptance; immutable source review and independently tested facts."""
from copy import deepcopy
from datetime import datetime,timezone
from decimal import Decimal as D
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import activate_company_review_batches as a

class NetworkActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:json.loads((ROOT/f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json').read_text()) for t in a.NETWORK_TICKERS}
        cls.summary=json.loads((ROOT/'docs/company-data-preparation/network-retail-review-batch.json').read_text());cls.decisions=cls.summary['decisions']

    def test_exact_28_revision_bound_approvals_and_serialization(self):
        ids=[]
        for t,p in self.packages.items():
            r=p['history_approval'];ids.extend(x['decision_id'] for x in r['decisions'])
            self.assertEqual(r['source_commit'],a.NETWORK_BASELINE)
            self.assertEqual(r['source_revision'],a.digest(a.relevant(a.parent(p))))
            self.assertEqual(r['proposal_revision'],a.digest(a.relevant([x for x in self.decisions if x['ticker']==t])))
            self.assertEqual(r['identities'],[x['identity'] for x in p['periods']])
            at=datetime.fromisoformat(r['recorded_at_utc']);self.assertEqual(at.utcoffset(),timezone.utc.utcoffset(at));self.assertLessEqual(at,datetime.now(timezone.utc))
            self.assertTrue(a.activate(a.parent(p),self.decisions,r)==p,'Exact replay differs '+t)
            self.assertTrue(json.loads(json.dumps(p))==p)
        self.assertEqual(len(ids),28);self.assertEqual(set(ids),{x['decision_id'] for x in self.decisions})

    def test_existing14_family_checklist_and_unknowns(self):
        from valuation_platform.analyst.historical_inputs import Field
        for p in self.packages.values():
            v=p['current_history'];self.assertEqual(v['passed_family_slots'],70);self.assertTrue(v['company_completed_for_approved_historical_perimeter'])
            self.assertFalse(v['phase1_closed']);self.assertFalse(v['valuation_consumption_approved'])
            for source,r in zip(p['periods'],v['periods']):
                self.assertEqual(set(r['inputs']),{x.value for x in Field});self.assertEqual(r['passed_family_slots'],14)
                self.assertEqual(r['remaining_essential_inputs'],[])
                self.assertEqual(r['original_supporting_unknowns'],source['original_supporting_unknowns'])
                self.assertTrue(all(x is None for x in r['original_supporting_unknowns'].values()))
                self.assertFalse(r['complete_debt']);self.assertFalse(r['complete_reinvestment']);self.assertIsNone(r['complete_expense_basis_da'])
                self.assertIsNone(r['inputs']['unclassified_cfo_reconciliation_residual']['value'])
                self.assertFalse(r['inputs']['reported_cash_flow_working_capital_movements']['additional_deduction_permitted'])

    def test_literal_source_selections_arithmetic_sign_precision(self):
        expected={'V':([804,861,943,1034,1220],[20977,22450,20463,20836,25171],[16487,15689,16286,11975,17164],[-705,-970,-1059,-1257,-1482],[542,602,765,850,897]),
                  'INTC':([11792,13035,9602,11379,11706],[38101,42051,49266,50011,46585],[6930,28338,25034,22062,37416],[-18733,-24844,-25750,-23944,-14646],[2036,3128,3229,3410,2434]),
                  'WMT':([10658,10945,11853,12973,14203],[42831,44622,46891,45790,51523],[14760,8625,9867,9037,10727],[-13106,-16857,-20606,-23783,-26642],[1163,1578,2093,2769,3603])}
        for t,p in self.packages.items():
            for i,r in enumerate(p['current_history']['periods']):
                v=r['inputs'];values=(v['depreciation_amortization'],v['debt_lease_components']['selected'],v['cash_investment_components']['selected'],v['cash_capex'],v['stock_based_compensation']['selected'])
                for j,value in enumerate(values):self.assertEqual(D(value['value'])/1000000,expected[t][j][i],(t,i,j))
                self.assertEqual(v['cash_capex']['sign_multiplier'],-1)
                sbc=v['stock_based_compensation']['selected'];source=p['periods'][i]['facts'][p['periods'][i]['proposed_selections']['sbc']]
                self.assertEqual(sbc['precision'],source['precision']);self.assertEqual(sbc['origin'],'proxy')
                for c in p['periods'][i]['calculations']:
                    if c['input_id'] in ('current_financial_captions','named_financing','limited_da_proxy'):
                        self.assertEqual(sum((D(p['periods'][i]['facts'][k]['value']) for k in c['operands']),D(0)),D(c['value']))

    def test_visa_curated_scope_claims_and_uncombined_classes(self):
        p=self.packages['V']
        for source,r in zip(p['periods'],p['current_history']['periods']):
            v=r['inputs']
            for family,key in (('depreciation_amortization','d_and_a'),('cash_capex','capex')):
                replay=v[family]['curated_policy_replay'];original=source['curated_policy_replays'][key]
                self.assertEqual(replay['policy_sha256'],a.digest(original['policy']))
                self.assertEqual(replay['value'],original['value']);self.assertEqual(replay['version'],original['policy']['version'])
            self.assertTrue(any(k.startswith('claim:PreferredStockValueOutstanding:') for k in v['other_equity_bridge_claims_assets']['known_populations']))
            shares=v['point_in_time_shares'];self.assertGreater(len(shares['selected_populations']),1);self.assertTrue(shares['class_parent_overlap_not_additive']);self.assertFalse(shares['conversion_or_dilution_approved'])
            self.assertFalse(v['cash_investment_components']['unrestricted_or_excess_cash'])
        self.assertNotIn('client_cash_collateral',p['periods'][-1]['facts'])

    def test_intel_hierarchy_sbc_grants_and_nci(self):
        p=self.packages['INTC']
        for source,r in zip(p['periods'],p['current_history']['periods']):
            v=r['inputs'];h=source['cfo_reconciliation']['populations'][0]['hierarchy_proof']
            self.assertEqual(sum((D(x['value']) for x in h['children']),D(0)),D(h['parent']['value']))
            self.assertEqual(v['deferred_taxes']['displayed_rows'],[x for x in h['children'] if 'deferred' in x['caption'].lower()])
            self.assertEqual(v['reported_cash_flow_working_capital_movements']['rows'],source['movement_rows'])
            self.assertEqual(v['stock_based_compensation']['selected']['value'],source['facts']['face_sbc']['value'])
            self.assertEqual(v['stock_based_compensation']['addback']['value'],source['facts']['face_sbc']['value'])
            self.assertEqual(v['depreciation_amortization']['origin'],'proxy')
        v=p['current_history']['periods'][-1]['inputs']
        self.assertEqual(v['cash_capex']['other_disclosures']['capital_grant_cash']['sign_multiplier'],1)
        self.assertEqual(v['other_equity_bridge_claims_assets']['known_populations']['nci']['value'],'12079000000')

    def test_walmart_face_revenue_generic_conflicts_and_overlap(self):
        p=self.packages['WMT'];expected=[572754,611289,648125,680985,713163]
        for i,(source,r) in enumerate(zip(p['periods'],p['current_history']['periods'])):
            v=r['inputs'];self.assertEqual(D(v['revenue']['value'])/1000000,expected[i])
            self.assertEqual(D(v['revenue']['value']),D(source['facts']['net_sales']['value'])+D(source['facts']['membership_other']['value']))
            self.assertNotIn('revenue',source['facts']);self.assertIsNone(v['stock_based_compensation']['addback'])
            self.assertIn('accretion',v['depreciation_amortization']['qualification'])
            debt=v['debt_lease_components'];self.assertEqual(debt['selected']['operands'].count('finance_lease'),1)
            self.assertTrue(debt['supplier_finance_already_in_operating_ap']);self.assertTrue(debt['finance_leases_already_included'])
            self.assertIsNone(debt['additional_borrowing']);self.assertEqual(debt['no_additional_adjustment']['origin'],'analyst_assumption')

    def test_restart_stale_sources_and_incomplete_or_forged_authority(self):
        for t,p in self.packages.items():
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'audit.json';path.write_text(json.dumps(p))
                self.assertTrue(a.load_if_approved(path,a.parent(p),self.decisions)==p)
            for key in ('value','precision','scope'):
                q=deepcopy(a.parent(p));q['periods'][0]['facts']['cfo'][key]='1'
                with self.assertRaisesRegex(ValueError,'Stale'):a.activate(q,self.decisions,p['history_approval'])
            q=deepcopy(a.parent(p));q['periods'][0]['alternatives']['sbc']['competing_values'].append('1')
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(q,self.decisions,p['history_approval'])
            with self.assertRaises(ValueError):a.activate(a.parent(p),[d for d in self.decisions if d['decision_id']!=t+'-DA'],p['history_approval'])
            forged=deepcopy(p['history_approval']);forged['authority']='other';forged['sha256']=a.digest({k:v for k,v in forged.items() if k!='sha256'})
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(a.parent(p),self.decisions,forged)

    def test_source_snapshot_peers_and_frozen_preservation_counts(self):
        for t,p in self.packages.items():
            path=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'
            self.assertEqual(json.dumps(a.parent(p),sort_keys=True,indent=2).encode()+b'\n',subprocess.check_output(['git','show',a.NETWORK_BASELINE+':'+path],cwd=ROOT))
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta','avgo','tsla','lly','mu','amd','jnj'):
            path=f'docs/company-data-preparation/{t}-analyst-input-package.json'
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',a.NETWORK_BASELINE+':'+path],cwd=ROOT))
        self.assertEqual(subprocess.check_output(['git','diff','--name-only',a.NETWORK_BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True),'')
        self.assertEqual(self.summary['approval_activation']['current_company_counts'],dict(broadly_assessed=42,completed_scoped=16,approved_partial=2,pending_reviews=0,assessment_only=24))

if __name__=='__main__':unittest.main()
