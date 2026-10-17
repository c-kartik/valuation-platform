"""Retained source checks for one review batch; no user decisions fabricated."""
from copy import deepcopy
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_large_company_review_batch as p
import tests.analyst.test_standard_review_batch as source_tests


class LargeCompanyReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs()
        cls.packages={t:cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'] for t in p.TICKERS}
        cls.summary=cls.outputs[p.SUMMARY];cls.artifact_files={}

    _artifact=source_tests.StandardReviewBatchTests._artifact

    def test_exact_source_bindings_receipts_and_confirmations(self):
        source_tests.StandardReviewBatchTests.test_every_source_occurrence_primary_representation_and_receipt(self)

    def test_scope_fifteen_selections_and_all_families(self):
        manifest=json.loads((ROOT/p.shared.MANIFEST).read_text())
        for t,package in self.packages.items():
            rows=package['periods'];self.assertEqual(len(rows),5)
            ids=sorted([r['identity'] for r in manifest['rows'] if r['identity']['cik']==rows[0]['identity']['cik']],key=lambda i:i['annual_end'])
            self.assertEqual([r['identity'] for r in rows],ids)
            for r in rows:
                self.assertEqual({c['field'] for c in r['family_checklist']},{f.value for f in p.shared.h.Field})
                self.assertEqual(len(r['family_checklist']),14)
                self.assertFalse(r['analyst_complete']);self.assertFalse(r['new_assumptions_active'])
                self.assertTrue(all(v is None for v in r['original_supporting_unknowns'].values()))
        self.assertEqual(self.summary['selected_periods'],15);self.assertEqual(self.summary['family_slots'],210)

    def test_literal_statement_values_and_precision_roles(self):
        # Expected numbers transcribed from retained original displayed rows,
        # not assembled output or frozen normalization result values.
        values={
            'AVGO':{'revenue':[27450,33203,35819,51574,63887], 'ebit':[8519,14225,16207,13463,25484],
                    'cfo':[13764,16736,18085,19962,27537], 'cash_capex':[443,424,452,548,623],
                    'mixed_amortization_rou':[5502,4455,3333,9417,8201]},
            'TSLA':{'revenue':[53823,81462,96773,97690,94827], 'ebit':[6523,13656,8891,7076,4355],
                    'cfo':[11497,14724,13256,14923,14747], 'mixed_da_impairment':[2911,3747,4667,5368,6148],
                    'cash_capex':[6482,7158,8898,11339,8527]},
            'LLY':{'revenue':[D('28318.4'),D('28541.4'),D('34124.1'),D('45042.7'),65179],
                   'cfo':[D('7260.7'),D('7084.4'),D('4240.1'),D('8817.9'),16813],
                   'other_ppe_cash':[D('1309.8'),D('1854.3'),D('3447.6'),D('5057.8'),7841]}}
        for t,fields in values.items():
            for key,expected in fields.items():
                self.assertEqual([D(r['facts'][key]['value'])/1000000 for r in self.packages[t]['periods']],expected,(t,key))
        for r in self.packages['LLY']['periods']:
            self.assertEqual(r['facts']['da']['role'],'cfo_reconciliation_observation')
            self.assertEqual(r['facts']['intangible_amortization']['role'],'recognized_expense_observation')
        self.assertEqual([r['facts']['other_ppe_cash']['precision'] for r in self.packages['LLY']['periods']],['-5']*4+['-6'])

    def test_proposed_da_arithmetic_does_not_certify_scope(self):
        expected={'AVGO':[5942,4888,3749,9860,8636],'TSLA':[2911,3747,4667,5368,6148],
                  'LLY':[D('1547.6'),D('1522.5'),D('1527.3'),D('1766.6'),1997]}
        for t,package in self.packages.items():
            for r,value in zip(package['periods'],expected[t]):
                x=next(x for x in r['calculations'] if x['input_id']=='limited_da_proxy')
                self.assertEqual(D(x['value'])/1000000,value);self.assertEqual(x['origin'],'proxy')
                self.assertEqual(x['status'],p.PROPOSED);self.assertEqual(x['completeness'],'partial_named_population_only')
                self.assertNotIn('finance_amortization',x['operands'])
                self.assertNotIn('mixed_amortization_rou',x['operands'])
                self.assertIsNone(r['original_supporting_unknowns']['complete_expense_da'])
        self.assertIn('negative',next(d for d in self.summary['decisions'] if d['decision_id']=='TSLA-DA')['uncertainty_and_alternative'])

    def test_financing_overlap_and_carrying_scope(self):
        expected={'AVGO':[39730,39515,39229,67566,65136], 'TSLA':[6834,3099,5230,8213,8376],
                  'LLY':[D('16884.7'),D('16238.6'),D('25225.3'),D('33644.2'),42503]}
        for t,package in self.packages.items():
            for r,value in zip(package['periods'],expected[t]):
                x=next(x for x in r['calculations'] if x['input_id']=='named_financing')
                self.assertEqual(D(x['value'])/1000000,value,(t,r['identity']))
                self.assertNotIn('finance_lease',x['operands']);self.assertNotIn('cp',x['operands'])
                self.assertNotIn('op_lease',x['operands']);self.assertEqual(x['status'],p.PROPOSED)
        # TSLA note LongTermDebt is noncurrent, not the complete debt parent.
        self.assertEqual(D(self.packages['TSLA']['periods'][-1]['facts']['debt_parent']['value'])/1000000,6584)

    def test_cfo_rows_and_cash_signs(self):
        for package in self.packages.values():
            for r in package['periods']:
                rec=r['cfo_reconciliation'];self.assertEqual(rec['status'],'SUPPORTED')
                pop=rec['populations'][0]
                self.assertEqual(sum((D(x['value']) for x in pop['rows']),D(0)),D(pop['cfo']['value']))
                self.assertFalse(any('residual' in x['input_id'] for x in r['calculations']))
                for key,multiplier in r['cash_sign_multipliers'].items():
                    self.assertEqual(multiplier,-1);self.assertGreaterEqual(D(r['facts'][key]['value']),0)

    def test_lly_existing_derivation_and_refresh_generations(self):
        ledger=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
        for r in self.packages['LLY']['periods']:
            original=next(x for x in ledger['rows'] if x['identity']==r['identity'])['fields'][1]
            derived=r['derived_ebit'];self.assertEqual(derived['origin'],'derived')
            self.assertTrue(derived['policy_proof']==original['provenance'],'Exact policy proof changed')
            self.assertEqual(derived['value'],original['value_usd'])
            refresh=r['refreshed_capex'];self.assertEqual(len(refresh['artifacts']),3)
            self.assertEqual(refresh['original_byte_equivalence'],'UNPROVED')
            self.assertEqual(refresh['acceptance_basis'],p.refresh.BASIS)
            self.assertEqual(set(refresh['supported_requirements']),set(p.refresh.REQUIRED))
            for a in refresh['artifacts']:
                self.assertNotEqual(a['historical_sha256'],a['refreshed_sha256'])
                self.assertEqual(a['historical_status'],p.refresh.HISTORICAL_STATUS)
        self.assertNotIn('ebit',self.packages['LLY']['periods'][0]['facts'])
        r=self.packages['LLY']['periods'][1]
        self.assertEqual(D(r['facts']['iprd_expense']['value'])/1000000,D('908.5'))
        self.assertEqual(D(r['facts']['iprd_addback']['value'])/1000000,D('420.9'))
        for r in self.packages['LLY']['periods'][2:]:
            self.assertEqual(r['facts']['iprd_addback']['role'],'cfo_reconciliation_observation')

    def test_source_ledger_references_and_revision_changes(self):
        cache={}
        for package in self.packages.values():
            original=deepcopy(package);revision=original.pop('review_revision')
            self.assertEqual(revision,p.digest(p.relevant(original)))
            changed=deepcopy(original);changed['periods'][0]['facts']['cfo']['value']='1'
            self.assertNotEqual(revision,p.digest(p.relevant(changed)))
            for r in package['periods']:
                for evidence in r['preparation_ledger_evidence'].values():
                    path,pointer=evidence['reference'].split('#')
                    if path not in cache:cache[path]=json.loads((ROOT/path).read_text())
                    item=cache[path]
                    for key in pointer.strip('/').split('/'):item=item[int(key)] if isinstance(item,list) else item[key]
                    self.assertEqual(p.digest(item),evidence['record_sha256'])

    def test_serialization_one_inactive_approval_table_and_preservation(self):
        for path,payload in self.outputs.items():
            self.assertTrue(json.loads(json.dumps(payload))==payload,'Round-trip differs '+path)
            self.assertEqual((ROOT/path).read_text(),json.dumps(payload,sort_keys=True,indent=2)+'\n',path)
        table=self.summary['decisions'];self.assertEqual(len(table),25)
        self.assertEqual(len({d['decision_id'] for d in table}),25)
        ids={d['decision_id'] for d in table}
        for d in table:self.assertFalse(d['accepted']);self.assertEqual(d['status'],p.PROPOSED)
        for package in self.packages.values():
            self.assertFalse(package['new_assumptions_active']);self.assertNotIn('history_approval',package)
            for r in package['periods']:
                for c in r['family_checklist']:self.assertTrue(set(c['pending_decisions'])<=ids)
        self.assertEqual(self.summary['evidence_acquisition_requirements'],[])
        self.assertEqual(self.summary['new_sec_requests'],0)
        protected=['src','docs/evidence','tests/fixtures']
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta'):
            protected.append('docs/company-data-preparation/'+t+'-analyst-input-package.json')
        result=subprocess.check_output(['git','diff',p.BASELINE,'--',*protected],cwd=ROOT)
        self.assertEqual(result,b'','Prior runtime/source/accepted packages changed')


if __name__=='__main__':unittest.main()
