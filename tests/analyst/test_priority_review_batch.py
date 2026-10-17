"""Exact-source company review; all new financial decisions remain inactive."""
from copy import deepcopy
from decimal import Decimal as D
import json
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_priority_review_batch as p
import tests.analyst.test_standard_review_batch as sources


class PriorityReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs();cls.packages={t:cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'] for t in p.TICKERS}
        cls.summary=cls.outputs[p.SUMMARY];cls.artifact_files={}

    _artifact=sources.StandardReviewBatchTests._artifact

    def test_original_bodies_receipts_and_every_fact_occurrence(self):
        sources.StandardReviewBatchTests.test_every_source_occurrence_primary_representation_and_receipt(self)

    def test_fifteen_exact_selections_real_fiscal_labels_and_fourteen_families(self):
        manifest=json.loads((ROOT/p.shared.MANIFEST).read_text())
        for t,package in self.packages.items():
            rows=package['periods']
            ids=sorted([r['identity'] for r in manifest['rows'] if r['identity']['cik']==rows[0]['identity']['cik']],key=lambda i:i['annual_end'])
            self.assertEqual([r['identity'] for r in rows],ids)
            self.assertEqual([r['fiscal_year'] for r in rows],list(range(2022,2027)) if t=='MU' else list(range(2021,2026)))
            for r in rows:
                self.assertEqual({c['field'] for c in r['family_checklist']},{f.value for f in p.shared.h.Field})
                self.assertEqual(len(r['family_checklist']),14)
                self.assertFalse(r['analyst_complete']);self.assertFalse(r['new_assumptions_active'])
                self.assertTrue(all(v is None for v in r['original_supporting_unknowns'].values()))
                _,body=self._artifact(next(s for s in r['sources'] if s['role']=='instance'))
                root=ET.fromstring(body)
                for occurrence in r['fiscal_year_evidence']['occurrences']:
                    node=root[occurrence['ordinal']]
                    self.assertTrue(node.tag.endswith('}DocumentFiscalYearFocus'))
                    self.assertEqual(node.text,str(r['fiscal_year']))
                    self.assertEqual(node.get('contextRef'),occurrence['context_id'])
        self.assertEqual(self.packages['JNJ']['periods'][0]['identity']['annual_end'],'2022-01-02')
        self.assertEqual(self.summary['family_slots'],210)

    def test_independently_transcribed_statement_values(self):
        expected={
            'MU':{'revenue':[30758,15540,25111,37378,133188],'ebit':[9702,-5745,1304,9770,99340],'cfo':[15181,1559,8507,17525,89675],
                  'cash_capex':[12067,7676,8386,15857,30712],'incentive_cash':[115,710,315,2005,3316]},
            'AMD':{'revenue':[16434,23601,22680,25785,34639],'ebit':[3648,1264,401,1900,3694],'cfo':[3521,3565,1667,3041,7709],
                   'cash_capex':[301,450,546,636,974]},
            'JNJ':{'revenue':[93775,94943,85159,88821,94193],'cfo':[23410,21194,22791,24266,24530],'cash_capex':[3652,4009,4543,4424,4832]}}
        for t,fields in expected.items():
            for k,values in fields.items():self.assertEqual([D(r['facts'][k]['value'])/1000000 for r in self.packages[t]['periods']],values,(t,k))

    def test_independent_display_checks_and_original_partials(self):
        for t,package in self.packages.items():
            for r in package['periods']:
                rec=r['cfo_reconciliation'];manual=r['independent_display_check']
                if rec['status']=='SUPPORTED':
                    pop=rec['populations'][0]
                    self.assertEqual(sum((D(x['value']) for x in pop['rows']),D(0)),D(pop['cfo']['value']))
                else:
                    self.assertEqual(t,'AMD');self.assertIn(r['fiscal_year'],[2022,2025])
                    self.assertEqual(rec['status'],'PARTIAL');self.assertEqual(manual['status'],'SUPPORTED')
                    self.assertEqual(D(manual['difference']),0);self.assertEqual(D(manual['parent_difference']),0);self.assertEqual(manual['tolerance'],'0')
                    for x in manual['rows']+[manual['cfo']]:self.assertEqual(abs(D(x['value'])),abs(D(x['fact']['value'])))
                self.assertFalse(any('residual' in x['input_id'] for x in r['calculations']))
        latest=self.packages['AMD']['periods'][-1]
        self.assertEqual(latest['proposed_cfo_fact'],'continuing_cfo')
        self.assertEqual(D(latest['facts']['continuing_cfo']['value'])/1000000,6493)
        self.assertEqual(D(latest['facts']['discontinued_cfo']['value'])/1000000,1216)
        self.assertEqual(latest['facts']['deferred_tax']['role'],'deferred_tax_expense_note_observation')
        self.assertEqual(D(latest['facts']['deferred_tax']['value'])/1000000,252)
        self.assertEqual(D(next(x for x in latest['independent_display_check']['rows'] if x['caption']=='Deferred income taxes')['value'])/1000000,248)
        inventory=next(x for x in self.packages['AMD']['periods'][1]['independent_display_check']['rows'] if D(x['value'])==189000000)
        self.assertTrue(inventory['fact']['occurrences'][0]['dimensions'])

    def test_proxy_gates_financing_overlap_and_incentive_alternative(self):
        values={'MU':([7116,7756,7780,8352,9503],[6906,13330,13397,14577,5179]),
                'AMD':([407,4174,3453,3064,3004],[313,2467,2468,1721,3222]),
                'JNJ':([7390,6970,7486,7339,7503],[33751,39659,29332,36634,47933])}
        for t,package in self.packages.items():
            for r,da,fin in zip(package['periods'],*values[t]):
                entries={x['input_id']:x for x in r['calculations']}
                self.assertEqual(D(entries['limited_da_proxy']['value'])/1000000,da)
                self.assertEqual(entries['limited_da_proxy']['origin'],'proxy')
                self.assertEqual(D(entries['named_financing']['value'])/1000000,fin)
                for x in entries.values():self.assertEqual(x['status'],p.PROPOSED)
                self.assertNotIn('finance_lease',entries['named_financing']['operands'])
                self.assertNotIn('finance_amortization',entries['limited_da_proxy']['operands'])
                self.assertEqual(r['cash_sign_multipliers']['cash_capex'],-1)
        self.assertEqual([D(next(x for x in r['calculations'] if x['input_id']=='net_incentive_cash_alternative')['value'])/1000000 for r in self.packages['MU']['periods']],[-11952,-6966,-8071,-13852,-27396])
        self.assertEqual(self.packages['AMD']['periods'][-1]['facts']['short_borrowing']['concept'],'ShortTermBorrowings')
        self.assertEqual(self.packages['AMD']['periods'][2]['facts']['reported_etr']['value'],'68')
        self.assertIn('UNSELECTED',self.packages['AMD']['periods'][2]['facts']['reported_etr']['selection_status'])

    def test_jnj_unchanged_approved_derivation_and_population_boundaries(self):
        ledger=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
        for r,ebit in zip(self.packages['JNJ']['periods'],[23395,23382,21207,20804,25287]):
            original=next(x for x in ledger['rows'] if x['identity']==r['identity'])['fields'][1]
            self.assertTrue(r['derived_ebit']['policy_proof']==original['provenance'],'Approved proof mismatch')
            self.assertEqual(D(r['derived_ebit']['value'])/1000000,ebit)
            self.assertTrue(r['derived_ebit']['official_metadata_binding'])
            self.assertTrue(all('JNJ-PERIMETER' in c['pending_decisions'] for c in r['family_checklist']))
        self.assertEqual([D(r['facts']['iprd_face_impairment']['value'])/1000000 for r in self.packages['JNJ']['periods']],[900,783,313,211,81])
        for r,amount in zip(self.packages['JNJ']['periods'][-2:],[11600,3400]):
            fact=r['facts']['talc_carrying_reserve'];self.assertEqual(D(fact['value'])/1000000,amount)
            self.assertEqual(fact['precision'],'-8');self.assertEqual(fact['occurrences'][0]['dimensions'],[['srt:LitigationCaseAxis','jnj:TalcMember']])
        last=self.packages['JNJ']['periods'][-1]
        self.assertEqual(D(last['facts']['talc_reversal']['value'])/1000000,7000)
        self.assertTrue(all(v['as_of']=='2026-02-06' for k,v in last['facts'].items() if k.startswith('shares:EntityCommon')))

    def test_ledger_binding_serialization_and_revision_invalidation(self):
        cache={}
        for path,payload in self.outputs.items():
            self.assertTrue(json.loads(json.dumps(payload))==payload,'Round-trip differs '+path)
            self.assertTrue((ROOT/path).read_text()==json.dumps(payload,sort_keys=True,indent=2)+'\n','Exact replay differs '+path)
        for package in self.packages.values():
            original=deepcopy(package);revision=original.pop('review_revision')
            self.assertEqual(revision,p.digest(p.relevant(original)))
            changed=deepcopy(original);changed['periods'][0]['facts']['cfo']['value']='1'
            self.assertNotEqual(revision,p.digest(p.relevant(changed)))
            for r in package['periods']:
                for ref in r['preparation_ledger_evidence'].values():
                    path,pointer=ref['reference'].split('#')
                    if path not in cache:cache[path]=json.loads((ROOT/path).read_text())
                    item=cache[path]
                    for k in pointer.strip('/').split('/'):item=item[int(k)] if isinstance(item,list) else item[k]
                    self.assertEqual(p.digest(item),ref['record_sha256'])

    def test_all_twenty_eight_decisions_inactive_and_preservation(self):
        ds=self.summary['decisions'];ids={x['decision_id'] for x in ds}
        self.assertEqual(len(ds),28);self.assertEqual(len(ids),28)
        self.assertEqual(self.summary['evidence_acquisition_requirements'],[])
        for d in ds:self.assertFalse(d['accepted']);self.assertEqual(d['status'],p.PROPOSED)
        for package in self.packages.values():
            for r in package['periods']:
                for c in r['family_checklist']:self.assertTrue(set(c['pending_decisions'])<=ids)
        protected=['src','docs/evidence','docs/universe','tests/fixtures']
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta','avgo','tsla','lly'):protected.append(f'docs/company-data-preparation/{t}-analyst-input-package.json')
        self.assertEqual(subprocess.check_output(['git','diff',p.BASELINE,'--',*protected],cwd=ROOT),b'')

    def test_specific_share_selection_scope_and_proposals_change_with_sources(self):
        for t,package in self.packages.items():
            selected=next(d for d in self.summary['decisions'] if d['decision_id']==t+'-SHARES')
            concept='EntityCommonStockSharesOutstanding' if t=='JNJ' else 'CommonStockSharesOutstanding'
            for r in package['periods']:
                facts=[v for k,v in r['facts'].items() if k.startswith('shares:'+concept+':') and not v['occurrences'][0]['dimensions']]
                self.assertEqual(len(facts),1);self.assertIn(facts[0]['as_of'],selected['numerical_effect'])
                self.assertIn(facts[0]['value'],selected['numerical_effect'])
                if t!='JNJ':self.assertEqual(facts[0]['as_of'],r['identity']['annual_end'])
            changed=deepcopy(package)
            k=next(k for k in changed['periods'][0]['facts'] if k.startswith('shares:'+concept+':'))
            changed['periods'][0]['facts'][k]['value']='1'
            self.assertNotEqual(p.decisions(changed),p.decisions(package))


if __name__=='__main__':unittest.main()
