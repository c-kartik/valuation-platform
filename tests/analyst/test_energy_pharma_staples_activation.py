"""Exact approval activation; unavailable EBIT is never an accepted zero."""
from copy import deepcopy
from datetime import datetime,timezone
from decimal import Decimal as D
import json,subprocess,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import activate_company_review_batches as a


class EnergyPharmaStaplesActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:json.loads((ROOT/f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json').read_text()) for t in a.ENERGY_PHARMA_STAPLES_TICKERS}
        cls.summary=json.loads((ROOT/'docs/company-data-preparation/energy-pharma-staples-review-batch.json').read_text())
        cls.decisions=cls.summary['decisions']

    def test_exact29_audits_authority_time_identity_revisions_and_replay(self):
        ids=[]
        for t,p in self.packages.items():
            r=p['history_approval'];ids.extend(d['decision_id'] for d in r['decisions'])
            self.assertEqual(r['source_commit'],a.ENERGY_PHARMA_STAPLES_BASELINE)
            self.assertEqual(r['authority'],a.ENERGY_PHARMA_STAPLES_AUTHORITY)
            self.assertEqual(r['source_revision'],a.digest(a.relevant(a.parent(p))))
            expected=[d for d in self.decisions if d['ticker']==t and d['decision_id']!='CVX-PERIMETER']
            self.assertEqual(r['decisions'],expected);self.assertEqual(r['proposal_revision'],a.digest(a.relevant(expected)))
            self.assertEqual(r['identities'],[x['identity'] for x in p['periods']])
            self.assertEqual(r['sha256'],a.digest({k:v for k,v in r.items() if k!='sha256'}))
            at=datetime.fromisoformat(r['recorded_at_utc']);self.assertEqual(at.utcoffset(),timezone.utc.utcoffset(at));self.assertLessEqual(at,datetime.now(timezone.utc))
            self.assertTrue(a.activate(a.parent(p),self.decisions,r)==p,'Exact approval replay '+t)
            self.assertTrue(json.loads(json.dumps(p))==p,'Roundtrip '+t)
        self.assertEqual(len(ids),29);self.assertNotIn('CVX-PERIMETER',ids)
        self.assertTrue(all(d['accepted'] is False for d in self.decisions))

    def test_five_year_checklists_exact_open_exception_no_perimeter_waiver(self):
        from valuation_platform.analyst.historical_inputs import Field
        for t,p in self.packages.items():
            view=p['current_history'];expected=65 if t=='CVX' else 70
            self.assertEqual(view['passed_family_slots'],expected);self.assertEqual(view['family_slots'],70)
            self.assertEqual(view['company_completed_for_approved_historical_perimeter'],t!='CVX')
            self.assertFalse(view['phase1_closed']);self.assertFalse(view['valuation_consumption_approved'])
            for source,r in zip(p['periods'],view['periods']):
                self.assertEqual(set(r['inputs']),{f.value for f in Field});self.assertEqual(r['passed_family_slots'],13 if t=='CVX' else 14)
                self.assertEqual(r['original_supporting_unknowns'],source['original_supporting_unknowns'])
                self.assertTrue(all(v is None for v in r['original_supporting_unknowns'].values()))
                self.assertIsNone(r['complete_expense_basis_da']);self.assertFalse(r['complete_debt']);self.assertFalse(r['complete_reinvestment'])
                if t=='CVX':
                    self.assertEqual([x['field'] for x in r['remaining_essential_inputs']],['ebit'])
                    ebit=r['inputs']['ebit'];self.assertIsNone(ebit['value']);self.assertEqual(ebit['origin'],'unavailable')
                    self.assertEqual(ebit['review'],'OPEN_ESSENTIAL_REQUIREMENT_NOT_APPROVED');self.assertTrue(ebit['not_reported_zero'])
                    self.assertIsNone(source['proposed_selections']['ebit']);self.assertNotIn('ebit',source['facts']);self.assertIsNone(source['derived_ebit'])
                else:self.assertEqual(r['remaining_essential_inputs'],[])
        cvx=self.packages['CVX'];req=cvx['history_approval']['open_analyst_use_requirements'][0]
        self.assertEqual(req['affected_families'],['ebit']);self.assertTrue(req['explicitly_not_approved']);self.assertEqual(req['status'],'OPEN')
        self.assertEqual(req['review_decision'],next(d for d in self.decisions if d['decision_id']=='CVX-PERIMETER'))
        self.assertEqual(cvx['current_history']['joint_use_eligibility'],'NOT_ELIGIBLE_OPEN_EBIT_BUSINESS_PERIMETER')

    def test_literal_selected_cash_da_financing_and_signs(self):
        expected={'CVX':([17925,16319,17326,17282,20132],[-7515,-10349,-14788,-15544,-16830],[31369,23339,20836,24541,40758],[5675,17901,8223,6781,6293]),
                  'MRK':([3214,3909,3872,4499,5838],[-4448,-4388,-3863,-3372,-4112],[33102,30691,35055,37111,49339],[8096,13192,7093,13689,14565]),
                  'PG':([2807,2714,2896,2847,3160],[-3156,-3062,-3322,-3773,-4409],[31493,34607,32460,34508,34138],[7214,8246,9482,9556,9942])}
        for t,p in self.packages.items():
            for i,(source,r) in enumerate(zip(p['periods'],p['current_history']['periods'])):
                v=r['inputs'];values=[v['depreciation_amortization'],v['cash_capex'],v['debt_lease_components']['selected'],v['cash_investment_components']['selected']]
                for j,value in enumerate(values):self.assertEqual(D(value['value'])/1000000,expected[t][j][i],(t,i,j))
                self.assertEqual(values[0]['origin'],'proxy');self.assertEqual(values[1]['sign_multiplier'],-1)
                self.assertEqual(values[0]['precision'],next(c['precision'] for c in source['calculations'] if c['input_id']=='limited_da_proxy'))
                self.assertFalse(values[0]['additional_rou_addback']);self.assertFalse(values[1]['complete_reinvestment'])
                self.assertFalse(v['cash_investment_components']['unrestricted_or_excess_cash'])
                debt=v['debt_lease_components'];self.assertIsNone(debt['additional_borrowing']);self.assertIsNone(debt['no_additional_adjustment']['value']);self.assertEqual(debt['no_additional_adjustment']['origin'],'analyst_assumption')

    def test_cvx_curated_scope_depletion_negative_sbc_and_nonoverlap(self):
        p=self.packages['CVX']
        for source,r in zip(p['periods'],p['current_history']['periods']):
            v=r['inputs'];capex=v['cash_capex'];proof=source['existing_capex_policy_replay']['policy']
            self.assertEqual(capex['curated_policy_replay']['policy_sha256'],a.digest(proof));self.assertEqual(capex['curated_policy_replay']['version'],'2')
            self.assertTrue(v['revenue']['generic_conflict_preserved']);self.assertEqual(v['revenue']['value'],source['facts']['face_revenue']['value'])
            self.assertIn('Depletion-inclusive',v['depreciation_amortization']['qualification'])
            debt=v['debt_lease_components'];self.assertTrue(debt['finance_leases_already_included']);self.assertEqual(debt['selected']['operands'],['short_borrowing','debt_finance_long'])
            self.assertNotIn('cp',debt['selected']['operands']);self.assertNotIn('finance_lease',debt['selected']['operands'])
            tax=v['deferred_taxes'];self.assertTrue(all(x['caption'].startswith('Deferred income tax') for x in tax['displayed_rows']))
            self.assertFalse(any('other deferred charges' in x['caption'] for x in tax['displayed_rows']))
            self.assertIn('asset_retirement',v['other_equity_bridge_claims_assets']['known_populations'])
        self.assertEqual(p['current_history']['periods'][2]['inputs']['stock_based_compensation']['selected']['value'],'-100000000')

    def test_mrk_continuing_scope_derivation_proxy_and_original_parser(self):
        p=self.packages['MRK'];rows=p['current_history']['periods']
        self.assertEqual([D(r['inputs']['reported_cfo']['value'])/1000000 for r in rows],[13122,19095,13006,21468,16472])
        self.assertEqual([D(r['inputs']['ebit']['value'])/1000000 for r in rows],[12538,17945,2355,19912,21218])
        for i,(source,r) in enumerate(zip(p['periods'],rows)):
            v=r['inputs'];self.assertEqual(v['reported_cfo']['original_parser_status'],'PARTIAL');self.assertEqual(source['cfo_reconciliation']['status'],'PARTIAL')
            self.assertEqual(v['ebit']['policy_proof'],source['derived_ebit']['policy_proof']);self.assertEqual(v['ebit']['origin'],'derived')
            self.assertEqual(v['reported_cash_flow_working_capital_movements']['rows'],source['movement_rows'])
            self.assertFalse(v['reported_cash_flow_working_capital_movements']['additional_deduction_permitted'])
            if i<3:self.assertIn('continuing',v['reported_cfo']['perimeter'])
            if i<2:
                inv=v['cash_capex'];self.assertEqual(inv['origin'],'proxy');self.assertFalse(inv['pure_ppe_scope_approved']);self.assertIsNone(inv['pure_cash_ppe'])
                self.assertTrue(inv['prior_negative_findings_preserved']);self.assertNotIn('cash_capex',source['facts'])
        first=rows[0]['inputs'];self.assertEqual(first['reported_cfo']['discontinued_observation']['value'],'987000000')
        self.assertEqual(first['stock_based_compensation']['selected']['value'],'479000000');self.assertEqual(p['periods'][0]['facts']['sbc_expense']['value'],'498000000')

    def test_pg_extension_tax_esop_and_unexplained_borrowing_differences(self):
        p=self.packages['PG'];rows=p['current_history']['periods']
        for source,r in zip(p['periods'],rows):
            v=r['inputs'];tax=v['reported_tax_context']
            self.assertFalse(tax['generic_denominator_approval_changed']);self.assertTrue(tax['no_new_ratio_computed']);self.assertFalse(tax['future_rate_approved'])
            self.assertEqual(tax['original_policy_etr'],source['reported_tax_policy_replay']['etr'])
            if source['fiscal_year']<2024:
                self.assertTrue(tax['pretax']['company_specific_selection']);self.assertEqual(tax['pretax']['value'],source['facts']['pretax_extension']['value'])
                self.assertEqual(source['reported_tax_policy_replay']['fields']['pretax']['status'],'UNAVAILABLE');self.assertIsNone(tax['original_policy_etr']['value'])
                self.assertEqual(tax['reported_etr']['origin'],'reported')
            debt=v['debt_lease_components'];self.assertEqual(debt['selected']['operands'],['face_current_borrowing','debt_long'])
            check=debt['retained_component_check'];self.assertTrue(check['no_plug']);self.assertIsNone(check['rounding_explanation']);self.assertFalse(check['conflict_cleared'])
            self.assertEqual(check['face_parent']['value'],source['facts']['face_current_borrowing']['value'])
            claims=v['other_equity_bridge_claims_assets'];self.assertTrue(claims['preferred_population_retained']);self.assertTrue(claims['plan_assets_liabilities_not_automatically_netted'])
            self.assertTrue(any(k.startswith('claim:PreferredStockValue:') for k in claims['known_populations']))
            self.assertIn('not a no-preferred assumption',claims['additional_adjustment']['rationale'])
        self.assertEqual([D(r['inputs']['debt_lease_components']['retained_component_check']['difference_usd'])/1000000 for r in rows],[0,0,0,-1,1])

    def test_pg_cfo_uses_unchanged_precision_proof_without_balancing_or_expansion(self):
        p=self.packages['PG'];rows=p['current_history']['periods']
        self.assertEqual([D(r['inputs']['reported_cfo']['displayed_precision_check']['difference'])/1000000 for r in rows],[0,0,1,1,1])
        self.assertEqual([D(r['inputs']['reported_cfo']['displayed_precision_check']['tolerance'])/1000000 for r in rows],[6,6,6,D('5.5'),D('5.5')])
        for source,r in zip(p['periods'],rows):
            check=r['inputs']['reported_cfo']['displayed_precision_check'];pop=source['cfo_reconciliation']['populations'][0]
            for k in ('status','difference','tolerance','precision_rule'):self.assertEqual(check[k],pop[k])
            self.assertTrue(check['unchanged_existing_rule']);self.assertTrue(check['no_plug']);self.assertIsNone(check['source_discrepancy_cause'])
            self.assertEqual(r['inputs']['reported_cfo']['value'],source['facts']['selected_cfo']['value'])
            self.assertIsNone(r['inputs']['unclassified_cfo_reconciliation_residual']['value'])
        changed=deepcopy(a.parent(p));pop=changed['periods'][2]['cfo_reconciliation']['populations'][0]
        pop['rows'][0]['value']=str(D(pop['rows'][0]['value'])+1000000000)
        pop.update(status='SUPPORTED',difference='1001000000',tolerance='9999999999')
        with self.assertRaisesRegex(ValueError,'displayed-precision'):a.large_view(changed,p['history_approval'])

    def test_persistence_restart_stale_changes_missing_authorization_and_no_zero(self):
        for t,p in self.packages.items():
            path=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'
            with tempfile.TemporaryDirectory() as temp:
                file=Path(temp)/'view.json';file.write_text(json.dumps(p));self.assertTrue(a.load_if_approved(file,a.parent(p),self.decisions)==p)
                file.write_text(json.dumps(a.parent(p)));self.assertNotIn('current_history',a.load_if_approved(file,a.parent(p),self.decisions))
            for kind in ('value','precision','scope','identity','evidence','alternative','calculation','tax'):
                changed=deepcopy(a.parent(p));r=changed['periods'][0]
                if kind in ('value','precision','scope'):r['facts']['selected_cfo'][kind]='1'
                elif kind=='identity':r['identity']['annual_end']='2000-01-01'
                elif kind=='evidence':r['sources'][0]['sha256']='0'*64
                elif kind=='alternative':r['alternatives']['revenue']['competing_values'].append('1')
                elif kind=='calculation':r['calculations'][0]['value']='1'
                else:r['reported_tax_policy_replay']['fields']['pretax']['value']='1'
                with self.assertRaises(ValueError):a.activate(changed,self.decisions,p['history_approval'])
            with self.assertRaises(ValueError):a.activate(a.parent(p),[d for d in self.decisions if d['decision_id']!=t+'-INV'],p['history_approval'])
            forged=deepcopy(p['history_approval']);forged['authority']='unapproved';forged['sha256']=a.digest({k:v for k,v in forged.items() if k!='sha256'})
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(a.parent(p),self.decisions,forged)
        cvx=self.packages['CVX'];bad=deepcopy(self.decisions);next(d for d in bad if d['decision_id']=='CVX-PERIMETER').update(status='ACCEPTED',accepted=True)
        with self.assertRaisesRegex(ValueError,'OPEN CVX'):a.approval(a.parent(cvx),bad,cvx['history_approval']['recorded_at_utc'])
        changed=deepcopy(a.parent(cvx));changed['periods'][0]['facts']['ebit']={'value':'0'}
        with self.assertRaisesRegex(ValueError,'EBIT null'):a.large_view(changed,cvx['history_approval'])

    def test_dated_shares_awards_and_source_nulls_not_aggregated(self):
        for p in self.packages.values():
            for source,r in zip(p['periods'],p['current_history']['periods']):
                shares=r['inputs']['point_in_time_shares'];self.assertFalse(shares['automatic_aggregation_or_dilution']);self.assertFalse(shares['conversion_or_dilution_approved'])
                for k,v in shares['selected_populations'].items():
                    self.assertEqual(v['as_of'],source['facts'][k]['as_of']);self.assertEqual(v['value'],source['facts'][k]['value']);self.assertEqual(v['unit'],'shares')
                self.assertFalse(any('shares' in c['input_id'] for c in source['calculations']))

    def test_parent_sources24_peers_frozen_and_counts_unchanged(self):
        for t,p in self.packages.items():
            path=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'
            self.assertTrue((json.dumps(a.parent(p),sort_keys=True,indent=2)+'\n').encode()==subprocess.check_output(['git','show',a.ENERGY_PHARMA_STAPLES_BASELINE+':'+path],cwd=ROOT),'Original parent changed '+t)
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',a.ENERGY_PHARMA_STAPLES_BASELINE,'docs/company-data-preparation'],cwd=ROOT,text=True).splitlines()
        peers=[x for x in paths if x.endswith('-analyst-input-package.json') and not any('/'+t.lower()+'-' in x for t in a.ENERGY_PHARMA_STAPLES_TICKERS)]
        self.assertEqual(len(peers),24)
        for path in peers:self.assertTrue((ROOT/path).read_bytes()==subprocess.check_output(['git','show',a.ENERGY_PHARMA_STAPLES_BASELINE+':'+path],cwd=ROOT),'Peer changed '+path)
        self.assertEqual(subprocess.check_output(['git','diff','--name-only',a.ENERGY_PHARMA_STAPLES_BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True),'')
        self.assertEqual(self.summary['approval_activation']['current_company_counts'],dict(broadly_assessed=42,completed_scoped=24,approved_partial=3,pending_reviews=0,assessment_only=15))


if __name__=='__main__':unittest.main()
