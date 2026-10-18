"""Approved effective views, not merely acceptance flags; no new assumptions."""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal as D
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import activate_company_review_batches as a


class CompanyBatchActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:json.loads((ROOT/f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json').read_text()) for t in a.TICKERS}
        cls.decisions=[]
        for name in ('standard-review-batch','trillion-review-batch'):
            cls.decisions+=json.loads((ROOT/f'docs/company-data-preparation/{name}.json').read_text())['decisions']
        cls.replayed={t:a.activate(a.parent(p),cls.decisions,p['history_approval']) for t,p in cls.packages.items()}

    def test_all48_exact_authorizations_revisions_actual_utc_and_serialization(self):
        ids=[]
        for t,p in self.packages.items():
            audit=p['history_approval'];ids += [d['decision_id'] for d in audit['decisions']]
            self.assertEqual(audit['source_commit'],a.BASELINE)
            self.assertEqual(audit['source_revision'],a.digest(a.relevant(a.parent(p))))
            self.assertEqual(audit['sha256'],a.digest({k:v for k,v in audit.items() if k!='sha256'}))
            at=datetime.fromisoformat(audit['recorded_at_utc']);self.assertEqual(at.utcoffset(),timezone.utc.utcoffset(at))
            self.assertLessEqual(at,datetime.now(timezone.utc))
            self.assertTrue(self.replayed[t]==p,'Effective/audit replay differs: '+t)
            self.assertTrue(json.loads(json.dumps(p))==p,'Round trip differs: '+t)
            self.assertTrue(p['current_history']['new_assumptions_active'])
            self.assertFalse(p['current_history']['phase1_closed']);self.assertFalse(p['current_history']['valuation_consumption_approved'])
        self.assertEqual(len(ids),48);self.assertEqual(len(set(ids)),48)
        self.assertEqual(set(ids),{d['decision_id'] for d in self.decisions})

    def test_five_completed_histories_and_cat_incomplete_not_approval_only(self):
        for t,p in self.packages.items():
            view=p['current_history']
            if t=='CAT':continue
            self.assertTrue(view['company_completed_for_approved_historical_perimeter'])
            self.assertEqual(view['passed_family_slots'],70);self.assertEqual(len(view['periods']),5)
            for row in view['periods']:
                self.assertEqual(row['passed_family_slots'],14);self.assertTrue(row['analyst_complete'])
                self.assertEqual(len(row['inputs']),14);self.assertEqual(row['remaining_essential_inputs'],[])
                self.assertIsNone(row['complete_expense_basis_da']);self.assertFalse(row['complete_debt']);self.assertFalse(row['complete_reinvestment'])
                self.assertIsNone(row['inputs']['unclassified_cfo_reconciliation_residual']['value'])
                self.assertFalse(row['inputs']['reported_cash_flow_working_capital_movements']['additional_deduction_permitted'])

    def test_effective_values_precision_and_raw_source_unknowns(self):
        expected={
            'COST':([2028,2246,2334,2528,2780],[8273,7890,7395,7267,7575]),
            'KO':([1452,1260,1128,1075,1050],[42761,39149,42064,44522,45492]),
            'NVDA':([1174,1544,1508,1864,2843],[10946,10953,9709,8463,8468]),
            'AMZN':([23421,25528,30931,32905,42677],[81427,100898,85935,75805,89295]),
            'META':([7967,8686,11178,15498,18616],[581,10610,19075,29535,59928])}
        for t,(da,fin) in expected.items():
            p=self.packages[t]
            for old,row,d,f in zip(p['periods'],p['current_history']['periods'],da,fin):
                v=row['inputs'];self.assertEqual(D(v['depreciation_amortization']['value'])/1000000,d)
                self.assertEqual(v['depreciation_amortization']['origin'],'proxy')
                self.assertEqual(D(v['debt_lease_components']['selected']['value'])/1000000,f)
                self.assertIsNone(v['debt_lease_components']['additional_borrowing'])
                self.assertEqual(old['original_supporting_unknowns'],row['original_supporting_unknowns'])
                self.assertLess(D(v['cash_capex']['value']),0)
                self.assertFalse(v['cash_investment_components']['unrestricted_or_excess_cash'])
                self.assertFalse(v['reported_tax_context']['future_rate_approved'])
                self.assertEqual(v['depreciation_amortization']['approval_reference'],'/history_approval')
        cost=self.packages['COST']['current_history']['periods'][0]['inputs']['depreciation_amortization']
        self.assertIn('explicitly approved',cost['accepted_non_overlap_assumption'])
        for row in self.packages['AMZN']['current_history']['periods']:
            self.assertEqual(row['inputs']['depreciation_amortization']['prior_broad_da_status'],'NEGATIVE_REVIEW_PRESERVED_SUPPORT_ONLY')

    def test_nvda_extensions_amzn_expanded_and_meta_partial_originals(self):
        for i,row in enumerate(self.packages['NVDA']['current_history']['periods']):
            capex=row['inputs']['cash_capex'];self.assertEqual(capex['origin'],'proxy');self.assertIsNone(capex['pure_ppe_cash'])
            self.assertIn('extension',capex['scope'])
            old=self.packages['NVDA']['periods'][i]['facts']['combined_investment']
            self.assertIn('nvidia' if i<2 else 'fasb',old['namespace']);self.assertEqual(capex['precision'],old['precision'])
        amzn=self.packages['AMZN'];self.assertEqual(amzn['periods'][0]['calculations'][-1]['value'],'81427000000')
        expanded=amzn['current_history']['periods'][0]['inputs']['debt_lease_components']['selected']
        self.assertEqual(expanded['input_id'],'known_facility_expanded_financing')
        self.assertEqual(amzn['periods'][0]['supplemental_source_observations'][0]['fact']['as_of'],'2021-12-31')
        self.assertEqual(amzn['periods'][0]['supplemental_source_observations'][0]['source_identity']['annual_end'],'2022-12-31')
        for old,selected in zip(self.packages['META']['periods'],self.packages['META']['current_history']['periods']):
            if old['identity']['annual_end'][:4] in ('2022','2023','2024'):
                self.assertEqual(old['cfo_reconciliation']['status'],'PARTIAL');self.assertEqual(old['independent_display_check']['difference'],'0')
                self.assertIn('independent_display_check',selected['inputs']['reported_cfo']['independent_display_check_reference'])

    def test_ko_known_held_sale_not_default_expansion_or_hidden(self):
        debt=self.packages['KO']['current_history']['periods'][-1]['inputs']['debt_lease_components']
        self.assertEqual(D(debt['selected']['value'])/1000000,45492)
        self.assertEqual(D(debt['known_separate_held_sale']['value'])/1000000,1435)
        self.assertFalse(debt['expanded_alternative_selected']);self.assertFalse(debt['complete_debt'])
        self.assertIn('not be silently omitted',debt['known_separate_held_sale_treatment'])
        self.assertNotEqual(D(debt['selected']['value'])/1000000,46927)

    def test_cat_direct_perimeters_eliminations_and_unsupported_allocations(self):
        p=self.packages['CAT'];view=p['current_history'];self.assertFalse(view['company_completed_for_approved_historical_perimeter'])
        # Literal Financial Products column from the retained supplemental CF
        # tables, not consolidated-minus-industrial or an assembled expectation.
        for r,icfo,fcfo in zip(view['periods'],[7177,6358,11688,11437,12278],[1420,1517,1106,1445,1074]):
            for scope,amount in [('industrial',icfo),('financial_products',fcfo)]:
                s=r['perimeters'][scope];self.assertEqual(D(s['inputs']['reported_cfo']['value'])/1000000,amount)
                self.assertEqual(s['inputs']['reported_cfo']['perimeter'],scope)
                self.assertEqual(s['cfo_reconciliation']['status'],'SUPPORTED');self.assertEqual(s['cfo_reconciliation']['difference'],'0')
                self.assertEqual(s['passed_family_slots'],13);self.assertFalse(s['analyst_complete'])
                self.assertEqual({x['field'] for x in s['remaining_essential_inputs']},{'stock_based_compensation'})
                self.assertIsNone(s['inputs']['stock_based_compensation']['value']);self.assertIsNone(s['inputs']['debt_lease_components']['lessee_lease_allocation'])
                self.assertTrue(s['inputs']['debt_lease_components']['no_additional_adjustment']['approved'])
                self.assertTrue(s['inputs']['point_in_time_shares']['no_perimeter_allocation'])
            self.assertIsNone(r['perimeters']['eliminations']['passed_family_slots'])
            self.assertTrue(r['consolidated_descriptive_only'])
        first=view['periods'][0]['perimeters'];self.assertEqual(first['industrial']['inputs']['ebit']['value'],'6363000000')
        self.assertEqual(first['financial_products']['inputs']['ebit']['value'],'816000000')
        self.assertEqual(first['eliminations']['inputs']['ebit']['value'],'-301000000')
        self.assertEqual(first['industrial']['inputs']['debt_lease_components']['selected']['value'],'9826000000')
        # Primary colspan coordinates exclude adjacent footnote1 from(389).
        table=next(t for t in p['history_approval']['additional_perimeter_evidence'][0]['tables'] if t['kind']=='income')
        revenue=next(x for x in table['rows'] if x['caption']=='Revenues of Financial Products')
        self.assertEqual(revenue['values']['eliminations']['value'],'-389000000')

    def test_stale_values_scope_precision_candidates_periods_and_forged_audit(self):
        p=self.packages['AMZN'];base=a.parent(p);record=p['history_approval']
        for key,value in [('value','1'),('precision','-9'),('scope','Changed economic perimeter')]:
            changed=deepcopy(base);changed['periods'][0]['facts']['cfo'][key]=value
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(changed,self.decisions,record)
        changed=deepcopy(base);changed['periods'][0]['identity']['annual_end']='2022-12-31'
        with self.assertRaisesRegex(ValueError,'Stale'):a.activate(changed,self.decisions,record)
        changed=deepcopy(base);changed['periods'][0]['alternatives']['tax']['competing_values'].append('1')
        with self.assertRaisesRegex(ValueError,'Stale'):a.activate(changed,self.decisions,record)
        forged=deepcopy(record);forged['decisions'][0]['recommendation']='Approve another treatment';forged['sha256']=a.digest({k:v for k,v in forged.items() if k!='sha256'})
        with self.assertRaisesRegex(ValueError,'Stale|unregistered'):a.activate(base,self.decisions,forged)

    def test_persist_restart_and_missing_approval_does_not_activate(self):
        p=self.packages['COST'];base=a.parent(p)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'package.json';path.write_text(json.dumps(p))
            self.assertTrue(a.load_if_approved(path,base,self.decisions)==p)
            path.write_text(json.dumps(base));self.assertTrue(a.load_if_approved(path,base,self.decisions)==base)
            self.assertNotIn('current_history',a.load_if_approved(path,base,self.decisions))

    def test_all_original_sources_proposals_peers_frozen_bytes_preserved(self):
        for t,p in self.packages.items():
            name=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'
            baseline=subprocess.check_output(['git','show',a.BASELINE+':'+name],cwd=ROOT)
            self.assertEqual(json.dumps(a.parent(p),sort_keys=True,indent=2).encode()+b'\n',baseline,t)
            self.assertEqual(a.parent(p)['new_assumptions_active'],False) # preserved historical flag, not current-view status
        for t in ('msft','aapl','googl'):
            name=f'docs/company-data-preparation/{t}-analyst-input-package.json'
            self.assertEqual((ROOT/name).read_bytes(),subprocess.check_output(['git','show',a.BASELINE+':'+name],cwd=ROOT))
        # Stages A/B/C and editable inputs add separate modules; every pre-existing source,
        # evidence/universe artifact and fixture remains byte-preserved. Permit
        # only these additions, never modifications of the historical boundary.
        changes=subprocess.check_output(['git','diff','--name-status',a.BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True).splitlines()
        allowed={'A\tsrc/valuation_platform/valuation/consumer.py',
                 'A\tsrc/valuation_platform/valuation/forecast.py',
                 'A\tsrc/valuation_platform/valuation/discounting.py',
                 'A\tsrc/valuation_platform/valuation/bridge.py',
                 'A\tsrc/valuation_platform/valuation/case_inputs.py'}
        self.assertTrue(set(changes)<=allowed,changes)


if __name__=='__main__':unittest.main()
