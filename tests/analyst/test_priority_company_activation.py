"""Explicit user acceptance, scoped effective values and unclosed JNJ use gate."""
from copy import deepcopy
from datetime import datetime,timezone
from decimal import Decimal as D
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import activate_company_review_batches as a


class PriorityCompanyActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:json.loads((ROOT/f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json').read_text()) for t in a.PRIORITY_TICKERS}
        cls.summary=json.loads((ROOT/'docs/company-data-preparation/priority-review-batch.json').read_text())
        cls.decisions=cls.summary['decisions']

    def test_exact28_approvals_replay_identity_timestamp_and_source_revisions(self):
        ids=[]
        for t,p in self.packages.items():
            record=p['history_approval'];ids.extend(d['decision_id'] for d in record['decisions'])
            self.assertEqual(record['source_commit'],a.PRIORITY_BASELINE)
            self.assertEqual(record['source_revision'],a.digest(a.relevant(a.parent(p))))
            self.assertEqual(record['proposal_revision'],a.digest(a.relevant([d for d in self.decisions if d['ticker']==t])))
            self.assertEqual(record['sha256'],a.digest({k:v for k,v in record.items() if k!='sha256'}))
            at=datetime.fromisoformat(record['recorded_at_utc']);self.assertEqual(at.utcoffset(),timezone.utc.utcoffset(at));self.assertLessEqual(at,datetime.now(timezone.utc))
            self.assertTrue(a.activate(a.parent(p),self.decisions,record)==p,'Exact effective replay differs: '+t)
            self.assertTrue(json.loads(json.dumps(p))==p,'Round trip differs: '+t)
            self.assertEqual(record['identities'],[r['identity'] for r in p['periods']])
        self.assertEqual(len(ids),28);self.assertEqual(set(ids),{d['decision_id'] for d in self.decisions})

    def test_fourteen_family_outcomes_no_closure_or_false_complete_populations(self):
        from valuation_platform.analyst.historical_inputs import Field
        for t,p in self.packages.items():
            view=p['current_history'];self.assertEqual(view['passed_family_slots'],25 if t=='JNJ' else 70)
            self.assertEqual(view['company_completed_for_approved_historical_perimeter'],t!='JNJ')
            self.assertFalse(view['phase1_closed']);self.assertFalse(view['valuation_consumption_approved'])
            for source,r in zip(p['periods'],view['periods']):
                self.assertEqual(set(r['inputs']),{f.value for f in Field});self.assertEqual(len(r['checklist']),14)
                self.assertEqual(r['passed_family_slots'],5 if t=='JNJ' else 14)
                self.assertEqual(r['original_supporting_unknowns'],source['original_supporting_unknowns'])
                self.assertTrue(all(v is None for v in r['original_supporting_unknowns'].values()))
                self.assertIsNone(r['complete_expense_basis_da']);self.assertFalse(r['complete_debt']);self.assertFalse(r['complete_reinvestment'])
                residual=r['inputs']['unclassified_cfo_reconciliation_residual'];self.assertIsNone(residual['value']);self.assertTrue(residual['not_reported_zero'])

    def test_literal_financial_selections_origins_signs_precision_and_nondefaults(self):
        expected={'MU':([7116,7756,7780,8352,9503],[6906,13330,13397,14577,5179],[9331,9594,8106,10307,43434],[-12067,-7676,-8386,-15857,-30712]),
                  'AMD':([407,4174,3453,3064,3004],[313,2467,2468,1721,3222],[3608,5855,5773,5132,10552],[-301,-450,-546,-636,-974]),
                  'JNJ':([7390,6970,7486,7339,7503],[33751,39659,29332,36634,47933],[31608,23519,22927,24522,20102],[-3652,-4009,-4543,-4424,-4832])}
        for t,p in self.packages.items():
            for i,r in enumerate(p['current_history']['periods']):
                v=r['inputs'];selected=(v['depreciation_amortization'],v['debt_lease_components']['selected'],v['cash_investment_components']['selected'],v['cash_capex'])
                for j,value in enumerate(selected):self.assertEqual(D(value['value'])/1000000,expected[t][j][i],(t,i,j))
                self.assertEqual(v['depreciation_amortization']['origin'],'proxy');self.assertFalse(v['depreciation_amortization']['additional_rou_addback'])
                self.assertEqual(v['depreciation_amortization']['precision'],next(x['precision'] for x in p['periods'][i]['calculations'] if x['input_id']=='limited_da_proxy'))
                self.assertFalse(v['cash_investment_components']['unrestricted_or_excess_cash'])
                if t=='MU':
                    alt=v['cash_capex']['nondefault_incentive_net_alternative'];self.assertFalse(alt['selected'])
                    self.assertNotEqual(alt['value'],v['cash_capex']['value'])
                    self.assertEqual(v['cash_capex']['other_disclosures']['incentive_cash']['sign_multiplier'],1)

    def test_amd_continuing_cfo_rows_and_both_original_partial_proofs(self):
        p=self.packages['AMD'];rows=p['current_history']['periods']
        self.assertEqual([D(r['inputs']['reported_cfo']['value'])/1000000 for r in rows],[3521,3565,1667,3041,6493])
        for i in (1,4):
            v=rows[i]['inputs'];original=p['periods'][i]
            self.assertEqual(original['cfo_reconciliation']['status'],'PARTIAL')
            self.assertEqual(v['reported_cfo']['original_parser_status'],'PARTIAL')
            self.assertEqual(v['reported_cash_flow_working_capital_movements']['rows'],original['movement_rows'])
            self.assertIn('independent_display_check',v['reported_cfo']['independent_reconciliation_reference'])
        v=rows[-1]['inputs'];self.assertEqual(v['reported_cfo']['original_consolidated_observation']['value'],'7709000000')
        self.assertEqual(v['reported_cfo']['discontinued_observation']['value'],'1216000000')
        self.assertEqual(v['reported_cash_flow_working_capital_movements']['scope'],'Continuing operations')
        self.assertEqual(v['deferred_taxes']['scope'],'Continuing operations')
        self.assertEqual(v['deferred_taxes']['note_observation']['value'],'252000000')
        self.assertEqual(v['deferred_taxes']['displayed_rows'][0]['value'],'248000000')
        tax=rows[2]['inputs']['reported_tax_context'];self.assertIsNone(tax['reported_etr']);self.assertEqual(tax['original_etr_observation']['value'],'68')

    def test_tax_scope_sbc_finance_embedding_and_unbounded_omissions(self):
        mu=self.packages['MU']
        for source,r in zip(mu['periods'],mu['current_history']['periods']):
            v=r['inputs'];tax=v['reported_tax_context']
            self.assertIn('before-equity',tax['pretax']['scope']);self.assertFalse(tax['generic_denominator_approval_changed'])
            self.assertEqual(v['stock_based_compensation']['selected']['value'],source['facts']['sbc_expense']['value'])
            self.assertEqual(v['stock_based_compensation']['addback']['value'],source['facts']['sbc_addback']['value'])
            self.assertTrue(v['stock_based_compensation']['count_once']);self.assertTrue(v['debt_lease_components']['finance_leases_already_included'])
        for p in self.packages.values():
            for r in p['current_history']['periods']:
                debt=r['inputs']['debt_lease_components'];self.assertNotIn('finance_lease',debt['selected']['operands'])
                self.assertNotIn('debt_current',debt['selected']['operands']);self.assertIsNone(debt['additional_borrowing'])
                self.assertEqual(debt['no_additional_adjustment']['origin'],'analyst_assumption')
                self.assertIn('unbounded',debt['no_additional_adjustment']['rationale'])

    def test_jnj_open_requirement_exact_periods_families_claims_and_dates(self):
        p=self.packages['JNJ'];view=p['current_history'];req=view['open_analyst_use_requirements'][0]
        self.assertEqual(req['status'],'OPEN');self.assertEqual(req['affected_families'],list(a.JNJ_FLOW_FAMILIES))
        self.assertEqual(req['affected_identities'],[r['identity'] for r in p['periods']])
        self.assertFalse(view['company_completed_for_approved_historical_perimeter'])
        for r in view['periods']:
            self.assertEqual({x['field'] for x in r['remaining_essential_inputs']},set(a.JNJ_FLOW_FAMILIES))
            self.assertTrue(all(v['panel']=='ORIGINAL_AS_FILED_NOT_HOMOGENEOUS_CONTINUING_SERIES' for v in r['inputs'].values()))
            self.assertEqual(r['inputs']['ebit']['origin'],'derived')
            shares=list(r['inputs']['point_in_time_shares']['selected_populations'].values());self.assertEqual(len(shares),1)
            self.assertGreater(shares[0]['as_of'],r['identity']['annual_end'])
        claims=view['periods'][-2]['inputs']['other_equity_bridge_claims_assets']
        self.assertTrue(claims['carrying_nominal_and_expense_not_additive'])
        self.assertEqual(claims['known_populations']['talc_carrying_reserve']['value'],'11600000000')
        self.assertEqual(claims['known_populations']['talc_nominal_reserve']['value'],'13500000000')

    def test_persistence_restart_and_stale_or_incomplete_approval_rejection(self):
        for t,p in self.packages.items():
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'package.json';path.write_text(json.dumps(p))
                self.assertTrue(a.load_if_approved(path,a.parent(p),self.decisions)==p)
                path.write_text(json.dumps(a.parent(p)));self.assertNotIn('current_history',a.load_if_approved(path,a.parent(p),self.decisions))
            for change in ('value','precision','scope'):
                q=deepcopy(a.parent(p));q['periods'][0]['facts']['cfo'][change]='1'
                with self.assertRaisesRegex(ValueError,'Stale'):a.activate(q,self.decisions,p['history_approval'])
            q=deepcopy(a.parent(p));q['periods'][0]['identity']['annual_end']='2000-01-01'
            with self.assertRaises(ValueError):a.activate(q,self.decisions,p['history_approval'])
            q=deepcopy(a.parent(p));q['periods'][0]['alternatives']['tax']['competing_values'].append('1')
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(q,self.decisions,p['history_approval'])
            with self.assertRaises(ValueError):a.activate(a.parent(p),[d for d in self.decisions if d['decision_id']!=t+'-DA'],p['history_approval'])
        p=self.packages['JNJ'];forged=deepcopy(p['history_approval']);forged['open_analyst_use_requirements']=[]
        forged['sha256']=a.digest({k:v for k,v in forged.items() if k!='sha256'})
        with self.assertRaisesRegex(ValueError,'Stale'):a.activate(a.parent(p),self.decisions,forged)

    def test_source_proposal_unknowns_and_eleven_peers_cat_frozen_preservation(self):
        for t,p in self.packages.items():
            path=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'
            self.assertEqual(json.dumps(a.parent(p),sort_keys=True,indent=2).encode()+b'\n',subprocess.check_output(['git','show',a.PRIORITY_BASELINE+':'+path],cwd=ROOT))
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta','avgo','tsla','lly'):
            path=f'docs/company-data-preparation/{t}-analyst-input-package.json'
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',a.PRIORITY_BASELINE+':'+path],cwd=ROOT))
        self.assertEqual(subprocess.check_output(['git','diff','--name-only',a.PRIORITY_BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True),'')
        self.assertEqual(self.summary['approval_activation']['current_company_counts'],dict(broadly_assessed=42,completed_scoped=13,approved_partial=2,pending_reviews=0,assessment_only=27))


if __name__=='__main__':unittest.main()
