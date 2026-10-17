"""Explicit25-decision acceptance: effective selections, not changed source facts."""
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


class LargeCompanyActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages={t:json.loads((ROOT/f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json').read_text()) for t in a.LARGE_TICKERS}
        cls.summary=json.loads((ROOT/'docs/company-data-preparation/large-company-review-batch.json').read_text())
        cls.decisions=cls.summary['decisions']
        cls.replayed={t:a.activate(a.parent(p),cls.decisions,p['history_approval']) for t,p in cls.packages.items()}

    def test_all25_authorizations_and_effective_round_trips(self):
        ids=[]
        for t,p in self.packages.items():
            record=p['history_approval'];ids += [d['decision_id'] for d in record['decisions']]
            self.assertEqual(record['source_commit'],a.LARGE_BASELINE)
            self.assertEqual(record['source_revision'],a.digest(a.relevant(a.parent(p))))
            self.assertEqual(record['sha256'],a.digest({k:v for k,v in record.items() if k!='sha256'}))
            self.assertEqual(record['proposal_revision'],a.digest(a.relevant([d for d in self.decisions if d['ticker']==t])))
            at=datetime.fromisoformat(record['recorded_at_utc']);self.assertEqual(at.utcoffset(),timezone.utc.utcoffset(at));self.assertLessEqual(at,datetime.now(timezone.utc))
            self.assertTrue(self.replayed[t]==p,'Exact effective/audit replay differs: '+t)
            self.assertTrue(json.loads(json.dumps(p))==p,'Round trip differs: '+t)
            self.assertTrue(p['current_history']['new_assumptions_active'])
            self.assertFalse(p['current_history']['phase1_closed']);self.assertFalse(p['current_history']['valuation_consumption_approved'])
        self.assertEqual(len(ids),25);self.assertEqual(len(set(ids)),25)
        self.assertEqual(set(ids),{d['decision_id'] for d in self.decisions})

    def test_five_year_checklists_and_operation_specific_nulls(self):
        from valuation_platform.analyst.historical_inputs import Field
        for p in self.packages.values():
            view=p['current_history'];self.assertEqual(view['passed_family_slots'],70)
            self.assertTrue(view['company_completed_for_approved_historical_perimeter'])
            for r in view['periods']:
                self.assertEqual(set(r['inputs']),{f.value for f in Field})
                self.assertEqual(r['passed_family_slots'],14);self.assertTrue(r['analyst_complete'])
                self.assertEqual(r['remaining_essential_inputs'],[])
                self.assertTrue(all(c['status']=='SATISFIED_WITHIN_APPROVED_HISTORICAL_PERIMETER' for c in r['checklist']))
                self.assertTrue(all(v is None for v in r['original_supporting_unknowns'].values()))
                self.assertIsNone(r['complete_expense_basis_da']);self.assertFalse(r['complete_debt']);self.assertFalse(r['complete_reinvestment'])
                residual=r['inputs']['unclassified_cfo_reconciliation_residual']
                self.assertIsNone(residual['value']);self.assertTrue(residual['not_reported_zero'])

    def test_literal_effective_financial_selections_and_precision(self):
        expected={
            'AVGO':([5942,4888,3749,9860,8636],[39730,39515,39229,67566,65136],[12163,12416,14189,9348,16178],[-443,-424,-452,-548,-623]),
            'TSLA':([2911,3747,4667,5368,6148],[6834,3099,5230,8213,8376],[17707,22185,29094,36563,44059],[-6482,-7158,-8898,-11339,-8527]),
            'LLY':([D('1547.6'),D('1522.5'),D('1527.3'),D('1766.6'),1997],[D('16884.7'),D('16238.6'),D('25225.3'),D('33644.2'),42503],[D('3908.6'),D('2211.8'),D('2927.7'),D('3423.2'),7373],[D('-1309.8'),D('-1854.3'),D('-3447.6'),D('-5057.8'),-7841])}
        for t,p in self.packages.items():
            for i,r in enumerate(p['current_history']['periods']):
                fields=r['inputs'];source=p['periods'][i]
                selected=(fields['depreciation_amortization'],fields['debt_lease_components']['selected'],fields['cash_investment_components']['selected'],fields['cash_capex'])
                for j,v in enumerate(selected):self.assertEqual(D(v['value'])/1000000,expected[t][j][i],(t,i,j))
                self.assertEqual(fields['depreciation_amortization']['origin'],'proxy')
                self.assertEqual(fields['depreciation_amortization']['precision'],next(c for c in source['calculations'] if c['input_id']=='limited_da_proxy')['precision'])
                self.assertEqual(fields['cash_capex']['sign_multiplier'],-1)
                self.assertFalse(fields['depreciation_amortization']['additional_rou_addback'])
        self.assertEqual([r['inputs']['cash_capex']['precision'] for r in self.packages['LLY']['current_history']['periods']],['-5']*4+['-6'])

    def test_lease_cp_parent_overlap_and_unbounded_omissions(self):
        for p in self.packages.values():
            for r in p['current_history']['periods']:
                debt=r['inputs']['debt_lease_components'];self.assertTrue(debt['finance_leases_already_included'])
                self.assertNotIn('finance_lease',debt['selected']['operands']);self.assertNotIn('cp',debt['selected']['operands'])
                self.assertNotIn('op_lease',debt['selected']['operands'])
                self.assertIsNone(debt['additional_borrowing']);self.assertIsNone(debt['no_additional_adjustment']['value'])
                self.assertEqual(debt['no_additional_adjustment']['origin'],'analyst_assumption')
                self.assertIn('unbounded',debt['no_additional_adjustment']['rationale'])
                claims=r['inputs']['other_equity_bridge_claims_assets'];self.assertIsNone(claims['additional_adjustment']['value'])
                self.assertEqual(claims['additional_adjustment']['origin'],'analyst_assumption')
                self.assertTrue(claims['net_funded_and_gross_claims_not_additive'])
                self.assertFalse(r['inputs']['cash_investment_components']['unrestricted_or_excess_cash'])

    def test_tsla_tax_comparatives_split_and_financing_assets(self):
        p=self.packages['TSLA'];rows=p['current_history']['periods']
        self.assertEqual([D(r['inputs']['reported_tax_context']['provision']['value'])/1000000 for r in rows],[699,1132,-5001,1837,1423])
        self.assertNotIn('tax',p['periods'][2]['facts']) # original generic conflict not rewritten
        self.assertIn('net of refunds',rows[2]['inputs']['reported_tax_context']['cash_taxes']['scope'])
        self.assertEqual(D(rows[2]['inputs']['cash_capex']['value']),D('-8898000000'))
        self.assertEqual(D(rows[3]['inputs']['cash_capex']['value']),D('-11339000000'))
        self.assertEqual(next(iter(rows[0]['inputs']['point_in_time_shares']['selected_populations'].values()))['as_of'],'2022-01-31')
        self.assertEqual(next(iter(rows[1]['inputs']['point_in_time_shares']['selected_populations'].values()))['value'],'3164000000')
        balances=rows[-1]['inputs']['cash_investment_components'];self.assertEqual(balances['other_balances']['lessor_net_receivable']['value'],'240000000')
        self.assertTrue(balances['parent_child_overlap_not_additive'])
        self.assertIn('financing assets and funding',rows[-1]['inputs']['debt_lease_components']['perimeter'])

    def test_lly_derived_refresh_investment_roles_and_cover_dates(self):
        p=self.packages['LLY']
        for source,r in zip(p['periods'],p['current_history']['periods']):
            v=r['inputs'];self.assertEqual(v['ebit']['origin'],'derived')
            self.assertTrue(v['ebit']['policy_proof']==source['derived_ebit']['policy_proof'])
            refresh=v['cash_capex']['refreshed_evidence'];self.assertTrue(refresh==source['refreshed_capex'])
            self.assertEqual(refresh['original_byte_equivalence'],'UNPROVED');self.assertEqual(len(refresh['artifacts']),3)
            shares=list(v['point_in_time_shares']['selected_populations'].values());self.assertEqual(len(shares),1)
            self.assertGreater(shares[0]['as_of'],source['identity']['annual_end'])
            self.assertFalse(v['point_in_time_shares']['automatic_aggregation_or_dilution'])
            self.assertFalse(v['cash_capex']['complete_reinvestment'])
        items=p['current_history']['periods'][1]['inputs']['cash_capex']['other_disclosures']
        self.assertEqual(D(items['iprd_cash']['value'])/1000000,D('-629.7'))
        self.assertEqual(D(items['iprd_expense']['value'])/1000000,D('908.5'))
        self.assertEqual(D(items['iprd_addback']['value'])/1000000,D('420.9'))

    def test_persistence_restart_and_no_approval_no_activation(self):
        for t,p in self.packages.items():
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'package.json';path.write_text(json.dumps(p))
                self.assertTrue(a.load_if_approved(path,a.parent(p),self.decisions)==p)
                path.write_text(json.dumps(a.parent(p)))
                self.assertTrue(a.load_if_approved(path,a.parent(p),self.decisions)==a.parent(p))
                self.assertNotIn('current_history',a.load_if_approved(path,a.parent(p),self.decisions))

    def test_stale_sources_precision_scope_alternatives_identity_and_missing_approval(self):
        for t,p in self.packages.items():
            for key,value in [('value','1'),('precision','-9'),('scope','Different population')]:
                changed=deepcopy(a.parent(p));changed['periods'][0]['facts']['cfo'][key]=value
                with self.assertRaisesRegex(ValueError,'Stale'):a.activate(changed,self.decisions,p['history_approval'])
            changed=deepcopy(a.parent(p));changed['periods'][0]['alternatives']['tax']['competing_values'].append('1')
            with self.assertRaisesRegex(ValueError,'Stale'):a.activate(changed,self.decisions,p['history_approval'])
            changed=deepcopy(a.parent(p));changed['periods'][0]['identity']['annual_end']='2000-01-01'
            with self.assertRaises(ValueError):a.activate(changed,self.decisions,p['history_approval'])
            with self.assertRaises(ValueError):a.activate(a.parent(p),[d for d in self.decisions if d['decision_id']!=t+'-DA'],p['history_approval'])
        p=self.packages['LLY'];changed=deepcopy(a.parent(p));changed['periods'][0]['refreshed_capex']['original_byte_equivalence']='PROVED'
        with self.assertRaisesRegex(ValueError,'Stale'):a.activate(changed,self.decisions,p['history_approval'])
        forged=deepcopy(p['history_approval']);forged['decisions'][0]['recommendation']='Different financial scope';forged['sha256']=a.digest({k:v for k,v in forged.items() if k!='sha256'})
        with self.assertRaisesRegex(ValueError,'Stale'):a.activate(a.parent(p),self.decisions,forged)

    def test_source_proposals_eight_completed_cat_and_frozen_preservation(self):
        for t,p in self.packages.items():
            path=f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'
            baseline=subprocess.check_output(['git','show',a.LARGE_BASELINE+':'+path],cwd=ROOT)
            self.assertEqual(json.dumps(a.parent(p),sort_keys=True,indent=2).encode()+b'\n',baseline,t)
            self.assertFalse(a.parent(p)['new_assumptions_active'])
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta'):
            path=f'docs/company-data-preparation/{t}-analyst-input-package.json'
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',a.LARGE_BASELINE+':'+path],cwd=ROOT))
        self.assertEqual(subprocess.check_output(['git','diff','--name-only',a.LARGE_BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True),'')
        counts=self.summary['approval_activation']['current_company_counts']
        self.assertEqual(counts,dict(broadly_assessed=42,completed_scoped=11,approved_partial=1,pending_reviews=0,assessment_only=30))


if __name__=='__main__':unittest.main()
