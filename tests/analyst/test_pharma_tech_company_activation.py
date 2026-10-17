"""Scope-specific effective selections and revision-bound approval history."""
from copy import deepcopy
from datetime import datetime,timezone
from decimal import Decimal as D
import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import activate_company_review_batches as a

class PharmaTechActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:json.loads((ROOT/f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json').read_text()) for t in a.PHARMA_TECH_TICKERS}
        cls.summary=json.loads((ROOT/'docs/company-data-preparation/pharma-network-tech-review-batch.json').read_text());cls.decisions=cls.summary['decisions']

    def test_exact28_authorizations_revisions_actual_utc_and_round_trip(self):
        ids=[]
        for t,p in self.packages.items():
            r=p['history_approval'];ids.extend(x['decision_id'] for x in r['decisions'])
            self.assertEqual(r['source_commit'],a.PHARMA_TECH_BASELINE)
            self.assertEqual(r['source_revision'],a.digest(a.relevant(a.parent(p))))
            self.assertEqual(r['proposal_revision'],a.digest(a.relevant([d for d in self.decisions if d['ticker']==t])))
            self.assertEqual(r['sha256'],a.digest({k:v for k,v in r.items() if k!='sha256'}))
            self.assertEqual(r['identities'],[x['identity'] for x in p['periods']])
            at=datetime.fromisoformat(r['recorded_at_utc']);self.assertEqual(at.utcoffset(),timezone.utc.utcoffset(at));self.assertLessEqual(at,datetime.now(timezone.utc))
            self.assertTrue(a.activate(a.parent(p),self.decisions,r)==p,'Effective replay '+t)
            self.assertTrue(json.loads(json.dumps(p))==p,'Round trip '+t)
        self.assertEqual(len(ids),28);self.assertEqual(set(ids),{d['decision_id'] for d in self.decisions})

    def test_five_times14_only_within_approved_perimeter_and_unknowns(self):
        from valuation_platform.analyst.historical_inputs import Field
        for p in self.packages.values():
            view=p['current_history'];self.assertEqual(view['passed_family_slots'],70);self.assertTrue(view['company_completed_for_approved_historical_perimeter'])
            self.assertFalse(view['phase1_closed']);self.assertFalse(view['valuation_consumption_approved'])
            self.assertTrue(all(d['status']=='ACTIVE' for d in view['active_decisions']))
            for source,r in zip(p['periods'],view['periods']):
                self.assertEqual(set(r['inputs']),{f.value for f in Field});self.assertEqual(r['passed_family_slots'],14);self.assertEqual(r['remaining_essential_inputs'],[])
                self.assertEqual(r['original_supporting_unknowns'],source['original_supporting_unknowns']);self.assertTrue(all(x is None for x in r['original_supporting_unknowns'].values()))
                self.assertIsNone(r['complete_expense_basis_da']);self.assertFalse(r['complete_debt']);self.assertFalse(r['complete_reinvestment'])
                v=r['inputs'];self.assertIsNone(v['unclassified_cfo_reconciliation_residual']['value']);self.assertTrue(v['unclassified_cfo_reconciliation_residual']['not_reported_zero'])
                self.assertEqual(v['reported_cash_flow_working_capital_movements']['rows'],source['movement_rows']);self.assertFalse(v['reported_cash_flow_working_capital_movements']['additional_deduction_permitted'])
                self.assertEqual(v['stock_based_compensation']['selected']['origin'],'proxy');self.assertTrue(v['stock_based_compensation']['count_once'])
                self.assertEqual(v['debt_lease_components']['no_additional_adjustment']['origin'],'analyst_assumption');self.assertIsNone(v['debt_lease_components']['additional_borrowing'])

    def test_literal_financial_selections_signs_and_inherited_precision(self):
        expected={'ABBV':([8521,8467,8698,8386,8139],[76684,63271,59385,67144,67496],[9830,9229,12816,5555,5257],[-787,-695,-777,-974,-1214]),
            'MA':([726,750,799,897,1143],[13901,14023,15681,18226,19000],[7894,7408,9180,8772,10898],[-407,-442,-371,-474,-489]),
            'CSCO':([1877,1631,2353,2902,2563],[9515,8391,30962,28093,29533],[19267,26146,17854,16110,15918],[-477,-849,-670,-905,-1410])}
        for t,p in self.packages.items():
            for i,r in enumerate(p['current_history']['periods']):
                v=r['inputs'];values=(v['depreciation_amortization'],v['debt_lease_components']['selected'],v['cash_investment_components']['selected'],v['cash_capex'])
                for j,value in enumerate(values):self.assertEqual(D(value['value'])/1000000,expected[t][j][i],(t,i,j))
                self.assertEqual(v['cash_capex']['sign_multiplier'],-1);self.assertFalse(v['cash_capex']['complete_reinvestment'])
                self.assertFalse(v['cash_investment_components']['unrestricted_or_excess_cash'])
                self.assertEqual(v['depreciation_amortization']['origin'],'reported' if t=='MA' else 'proxy')
                if t=='CSCO':
                    original=next(x for x in p['periods'][i]['calculations'] if x['input_id']=='limited_da_proxy')
                    self.assertEqual(v['depreciation_amortization']['precision'],original['precision'])
                    self.assertEqual(v['depreciation_amortization']['operand_precision'],['-8','-6'])
                    self.assertEqual(v['depreciation_amortization']['operands'],['da','purchased_amortization_total'])

    def test_abbv_embedded_financing_iprd_and_claim_overlap(self):
        p=self.packages['ABBV']
        for source,r in zip(p['periods'],p['current_history']['periods']):
            v=r['inputs'];debt=v['debt_lease_components'];self.assertTrue(debt['finance_leases_already_included'])
            self.assertNotIn('finance_lease',debt['selected']['operands']);self.assertNotIn('financing_liability',debt['selected']['operands'])
            self.assertNotIn('debt_parent',debt['selected']['operands'])
            claims=v['other_equity_bridge_claims_assets'];self.assertEqual(claims['known_populations']['benefit_liabilities']['value'],source['facts']['benefit_liabilities']['value'])
            self.assertTrue(any(k.startswith('claim:BusinessCombinationContingentConsiderationLiability') for k in claims['known_populations']))
            self.assertTrue(claims['net_funded_and_gross_claims_not_additive'])
            inv=v['cash_capex']['other_disclosures'];self.assertEqual(inv['investment_cash']['sign_multiplier'],-1);self.assertEqual(inv['iprd_expense']['value'],source['facts']['iprd_expense']['value'])
            self.assertFalse(v['depreciation_amortization']['additional_rou_addback'])
        source=p['periods'][3];debt=p['current_history']['periods'][3]['inputs']['debt_lease_components']
        self.assertNotIn('short_borrowing',source['facts']);self.assertNotIn('short_borrowing',debt['selected']['operands'])
        self.assertIsNone(debt['additional_borrowing']);self.assertIsNone(debt['no_additional_adjustment']['value'])
        self.assertEqual(debt['selected']['value'],'67144000000')

    def test_ma_net_revenue_expense_da_curated_tax_and_client_scope(self):
        p=self.packages['MA'];expected=[18884,22237,25098,28167,32791]
        for i,(source,r) in enumerate(zip(p['periods'],p['current_history']['periods'])):
            v=r['inputs'];self.assertEqual(D(v['revenue']['value'])/1000000,expected[i]);self.assertTrue(v['revenue']['generic_conflict_preserved'])
            self.assertEqual(v['depreciation_amortization']['value'],source['facts']['expense_da']['value']);self.assertEqual(v['depreciation_amortization']['origin'],'reported')
            tax=v['reported_tax_context'];self.assertEqual(tax['pretax']['value'],source['reported_tax_policy_replay']['fields']['pretax']['value'])
            self.assertEqual(tax['reported_etr']['value'],source['reported_tax_policy_replay']['etr']['value']);self.assertEqual(tax['reported_etr']['origin'],'derived')
            self.assertFalse(tax['generic_denominator_approval_changed']);self.assertFalse(tax['future_rate_approved'])
            if i<3:self.assertTrue(source['reported_tax_policy_replay']['proof']['curated_pretax'])
            cash=v['cash_investment_components'];self.assertNotIn('customer_collateral_asset',cash['selected']['operands']);self.assertIn('customer_collateral_asset',cash['other_balances'])
            self.assertEqual(cash['other_balances']['customer_collateral_asset']['value'],cash['other_balances']['customer_collateral_liability']['value'])
            self.assertIn('settlement_asset',cash['other_balances'])
            if 'litigation_restricted' in source['facts']:
                self.assertEqual(cash['other_balances']['litigation_restricted']['value'],source['facts']['litigation_restricted']['value'])
            else:
                self.assertNotIn('litigation_restricted',cash['other_balances'])
                self.assertTrue(any(x['input_id']=='litigation_restricted' and x['value'] is None for x in source['source_binding_exceptions']))
                self.assertTrue(cash['unresolved_populations_reference'].endswith('/source_binding_exceptions'))
        old=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text());old=next(x for x in old['rows'] if x['identity']==p['periods'][0]['identity'])
        self.assertIn('CONFLICT',old['fields'][0]['status'])

    def test_csco_1621_difference_unresolved_not_plug_or_rounding(self):
        p=self.packages['CSCO'];cash=p['current_history']['periods'][-1]['inputs']['cash_investment_components'];conflict=cash['retained_conflict']
        self.assertEqual(cash['selected']['value'],'15918000000');self.assertEqual(conflict['conflicting_parent']['value'],'14297000000')
        self.assertEqual(conflict['difference_usd'],'1621000000');self.assertEqual(D(cash['selected']['value'])-D(conflict['conflicting_parent']['value']),D(conflict['difference_usd']))
        self.assertEqual(conflict['status'],'UNRESOLVED_SOURCE_SCOPE_DIFFERENCE');self.assertFalse(conflict['conflict_cleared']);self.assertTrue(conflict['no_plug']);self.assertIsNone(conflict['rounding_explanation'])
        self.assertIsNone(cash['unknown_restrictions']);self.assertFalse(cash['unrestricted_or_excess_cash'])
        for r in p['current_history']['periods']:
            da=r['inputs']['depreciation_amortization'];self.assertNotIn('mixed_cfo_da',da['operands']);self.assertIn('impairment',da['qualification'])
            self.assertFalse(da['additional_rou_addback']);self.assertFalse(r['inputs']['debt_lease_components']['complete_debt'])

    def test_persistence_restart_stale_tax_evidence_candidates_and_incomplete_approval(self):
        for t,p in self.packages.items():
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'view.json';path.write_text(json.dumps(p));self.assertTrue(a.load_if_approved(path,a.parent(p),self.decisions)==p)
                path.write_text(json.dumps(a.parent(p)));self.assertNotIn('current_history',a.load_if_approved(path,a.parent(p),self.decisions))
            for kind in ('value','precision','scope','tax','evidence','alternative','identity'):
                changed=deepcopy(a.parent(p));r=changed['periods'][0]
                if kind in ('value','precision','scope'):r['facts']['cfo'][kind]='1'
                elif kind=='tax':r['reported_tax_policy_replay']['fields']['pretax']['value']='1'
                elif kind=='evidence':r['sources'][0]['sha256']='0'*64
                elif kind=='alternative':r['alternatives']['sbc']['competing_values'].append('1')
                else:r['identity']['annual_end']='2000-01-01'
                with self.assertRaisesRegex(ValueError,'exact approved' if kind=='identity' else 'Stale'):a.activate(changed,self.decisions,p['history_approval'])
            with self.assertRaises(ValueError):a.activate(a.parent(p),[d for d in self.decisions if d['decision_id']!=t+'-DA'],p['history_approval'])
            forged=deepcopy(p['history_approval']);forged['authority']='unapproved';forged['sha256']=a.digest({k:v for k,v in forged.items() if k!='sha256'})
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(a.parent(p),self.decisions,forged)

    def test_parent_eighteen_peers_frozen_pilot_preservation_and_counts(self):
        for t,p in self.packages.items():
            path=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'
            self.assertEqual(json.dumps(a.parent(p),sort_keys=True,indent=2).encode()+b'\n',subprocess.check_output(['git','show',a.PHARMA_TECH_BASELINE+':'+path],cwd=ROOT))
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta','avgo','tsla','lly','mu','amd','jnj','v','intc','wmt'):
            path=f'docs/company-data-preparation/{t}-analyst-input-package.json';self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',a.PHARMA_TECH_BASELINE+':'+path],cwd=ROOT))
        self.assertEqual(subprocess.check_output(['git','diff','--name-only',a.PHARMA_TECH_BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True),'')
        self.assertEqual(self.summary['approval_activation']['current_company_counts'],dict(broadly_assessed=42,completed_scoped=19,approved_partial=2,pending_reviews=0,assessment_only=21))

if __name__=='__main__':unittest.main()
