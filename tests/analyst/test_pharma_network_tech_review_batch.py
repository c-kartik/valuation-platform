"""Retained independent source bindings and inactive company proposals."""
from copy import deepcopy
from datetime import date
from decimal import Decimal as D,localcontext
from io import BytesIO
import json,subprocess,sys,types,unittest
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_pharma_network_tech_review_batch as p
import activate_company_review_batches as accepted
import tests.analyst.test_standard_review_batch as source_tests


class PharmaNetworkTechReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs();cls.packages={t:accepted.parent(cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json']) for t in p.TICKERS}
        cls.summary=cls.outputs[p.SUMMARY];cls.artifact_files={}
    _artifact=source_tests.StandardReviewBatchTests._artifact

    def test_all_occurrences_receipts_and_independent_primary(self):
        source_tests.StandardReviewBatchTests.test_every_source_occurrence_primary_representation_and_receipt(self)

    def test_exact_frozen15_annuals_and210_families(self):
        manifest=json.loads((ROOT/p.shared.MANIFEST).read_text());identities=[]
        for t,v in self.packages.items():
            expected=sorted([r['identity'] for r in manifest['rows'] if r['identity']['cik']==v['periods'][0]['identity']['cik']],key=lambda x:x['annual_end'])
            self.assertEqual([r['identity'] for r in v['periods']],expected)
            self.assertEqual([r['fiscal_year'] for r in v['periods']],list(range(2022,2027)) if t=='CSCO' else list(range(2021,2026)))
            for r in v['periods']:
                identities.append(r['identity']['accession']);self.assertEqual({c['field'] for c in r['family_checklist']},{f.value for f in p.shared.h.Field})
                self.assertTrue(all(not c['financial_complete'] for c in r['family_checklist']))
        self.assertEqual(len(set(identities)),15);self.assertEqual(self.summary['family_slots'],210)
        self.assertEqual(sum(v['outcomes']['SOURCE_SUPPORTED'] for v in self.packages.values()),25)

    def test_independent_literal_schedules_and_calculation_scope(self):
        expected={'ABBV':{'depreciation':[803,778,752,764,762],'cfo_intangible_amortization':[7718,7689,7946,7622,7377],'cash_capex':[787,695,777,974,1214],'investment_cash':[1377,539,1223,3024,5237],'iprd_expense':[962,697,778,2757,5016]},
            'MA':{'face_revenue':[18884,22237,25098,28167,32791],'expense_da':[726,750,799,897,1143],'cash':[7421,7008,8588,8442,10566],'current_financial_investments':[473,400,592,330,332]},
            'CSCO':{'da':[800,700,700,700,700],'purchased_amortization_total':[1077,931,1653,2202,1863],'mixed_cfo_da':[1957,1726,2507,2811,2540],'cash_capex':[477,849,670,905,1410]}}
        calculations={'ABBV':([8521,8467,8698,8386,8139],[76684,63271,59385,67144,67496]),'MA':([726,750,799,897,1143],[13901,14023,15681,18226,19000]),'CSCO':([1877,1631,2353,2902,2563],[9515,8391,30962,28093,29533])}
        for t,fields in expected.items():
            for key,values in fields.items():self.assertEqual([D(r['facts'][key]['value'])/1000000 for r in self.packages[t]['periods']],values,(t,key))
            for i,r in enumerate(self.packages[t]['periods']):
                cs={c['input_id']:c for c in r['calculations']}
                for j,key in enumerate(('limited_da_proxy','named_financing')):self.assertEqual(D(cs[key]['value'])/1000000,calculations[t][j][i])
                for c in cs.values():
                    self.assertEqual(c['status'],p.PROPOSED);self.assertEqual(c['completeness'],'partial_named_population_only')
                    self.assertEqual(sum((D(r['facts'][k]['value'])*co for k,co in zip(c['operands'],c['coefficients'])),D(0)),D(c['value']))
                self.assertEqual(r['cash_sign_multipliers']['cash_capex'],-1)

    def test_abbv_precision_acquisition_contingent_and_embedded_financing(self):
        for r in self.packages['ABBV']['periods']:
            facts=r['facts'];self.assertEqual(facts['cfo_intangible_amortization']['precision'],'-6')
            self.assertTrue(any(D(c['value'])!=D(facts['cfo_intangible_amortization']['value']) for c in r['alternatives']['intangible_amortization']['candidates']))
            self.assertEqual(D(facts['debt_carrying_parent']['value']),D(facts['debt_finance_current']['value'])+D(facts['debt_finance_long']['value']))
            fin=next(c for c in r['calculations'] if c['input_id']=='named_financing')
            self.assertNotIn('finance_lease',fin['operands']);self.assertNotIn('financing_liability',fin['operands'])
            self.assertTrue(any(k.startswith('claim:BusinessCombinationContingentConsiderationLiability') for k in facts))
        r=self.packages['ABBV']['periods'][3];self.assertNotIn('short_borrowing',r['facts']);self.assertIsNone(r['original_supporting_unknowns']['additional_unidentified_borrowing'])
        r=self.packages['ABBV']['periods'][0];self.assertNotEqual(r['facts']['upfront_collaboration_adjustment']['value'],r['facts']['iprd_expense']['value'])

    def test_ma_net_revenue_curated_tax_and_client_populations(self):
        rows=self.packages['MA']['periods'];r=rows[0]
        self.assertEqual(D(r['facts']['gross_revenue']['value'])-D(r['facts']['rebates']['value']),D(r['facts']['face_revenue']['value']))
        original=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
        original=next(x for x in original['rows'] if x['identity']==r['identity'])
        self.assertIn('CONFLICT',original['fields'][0]['status'])
        for i,r in enumerate(rows):
            tax=r['reported_tax_policy_replay'];self.assertEqual(tax['fields']['pretax']['status'],'POPULATED')
            if i<3:self.assertTrue(tax['proof']['curated_pretax']);self.assertTrue(tax['proof']['curated_metadata_basis'])
            self.assertEqual(r['facts']['customer_collateral_asset']['value'],r['facts']['customer_collateral_liability']['value'])
            cash=next(c for c in r['calculations'] if c['input_id']=='current_financial_captions')
            self.assertNotIn('customer_collateral_asset',cash['operands']);self.assertNotIn('litigation_restricted',cash['operands'])
            self.assertIn('settlement_asset',r['facts']);self.assertIn('settlement_liability',r['facts'])
            with localcontext() as ctx:
                ctx.prec=34
                self.assertEqual(D(tax['etr']['value']),D(tax['fields']['provision']['value'])/D(tax['fields']['pretax']['value']))

    def test_csco_note_total_is_not_opex_or_cfo_other_and_precision(self):
        rows=self.packages['CSCO']['periods']
        for i,r in enumerate(rows):
            total=r['facts']['purchased_amortization_total'];self.assertIn('including source impairment',total['scope'])
            self.assertEqual(r['facts']['da']['precision'],'-8')
            proxy=next(c for c in r['calculations'] if c['input_id']=='limited_da_proxy');self.assertEqual(proxy['operands'],['da','purchased_amortization_total'])
            self.assertNotIn('mixed_cfo_da',proxy['operands']);self.assertNotIn('finance_amortization',proxy['operands'])
            if i<4:self.assertTrue(total['occurrences'][0]['dimensions'])
            self.assertNotEqual(total['value'],r['facts']['intangible_amortization']['value'])
        self.assertNotEqual(rows[-1]['facts']['current_financial_parent']['value'],next(c['value'] for c in rows[-1]['calculations'] if c['input_id']=='current_financial_captions'))

    def test_cfo_movements_tax_roles_and_no_residual(self):
        for t,v in self.packages.items():
            for r in v['periods']:
                rec=r['cfo_reconciliation'];self.assertEqual(rec['status'],'SUPPORTED');pop=rec['populations'][0]
                self.assertEqual(sum((D(x['value']) for x in pop['rows']),D(0)),D(pop['cfo']['value']))
                self.assertGreater(len(r['movement_rows']),0)
                for x in pop['rows']:self.assertEqual(D(x['raw'])*x['sign'],D(x['value']))
                self.assertFalse(any('residual' in c['input_id'] for c in r['calculations']))
                self.assertEqual(r['facts']['sbc_expense']['role'],'recognized_expense_observation')
                self.assertEqual(r['facts']['sbc_addback']['role'],'cfo_reconciliation_observation')

    def test_actual_primary_binding_rejects_wrong_identity_duration_unit(self):
        r=self.packages['MA']['periods'][0];fact=r['facts']['face_revenue'];_,xml=self._artifact(next(s for s in r['sources'] if s['role']=='instance'));_,html=self._artifact(next(s for s in r['sources'] if s['role']=='primary'))
        root=ET.fromstring(xml);ns={v[0]:v[1] for _,v in ET.iterparse(BytesIO(xml),events=['start-ns'])};xi=p.shared.cash._XI
        contexts={n.get('id'):n for n in root.findall(xi+'context')};units={n.get('id'):n for n in root.findall(xi+'unit')}
        inline=p.shared.InlineFacts();inline.feed(html.decode());o=fact['occurrences'][0];attrs,text=inline.facts[o['primary_locator'].removeprefix('inline#')]
        identity=r['identity'];period=p.shared.cash.Period(identity['cik'],identity['accession'],date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']))
        f=types.SimpleNamespace(root=root,contexts=contexts,units=units,namespaces=ns,period=period);case={'filing':f};item=dict(attrs=attrs,text=text)
        self.assertEqual(p.peer.primary_fact(case,item,0,0,0,'Net revenue')['value'],fact['value'])
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong instant',instant=True)
        f.period=p.shared.cash.Period(period.cik,period.accession,period.annual_start,date(2021,12,30))
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong date')
        f.period=period;units[attrs['unitref']]=ET.fromstring('<unit xmlns="http://www.xbrl.org/2003/instance"><measure>xbrli:shares</measure></unit>')
        with self.assertRaises(ValueError):p.peer.primary_fact(case,item,0,0,0,'Wrong unit')

    def test_inactive_approvals_nulls_dates_serialization_replay_and_revisions(self):
        ds=self.summary['decisions'];ids={d['decision_id'] for d in ds};self.assertEqual(len(ids),28)
        for d in ds:self.assertFalse(d['accepted']);self.assertEqual(d['status'],p.PROPOSED)
        for path,payload in self.outputs.items():
            self.assertTrue(json.loads(json.dumps(payload))==payload,'Round trip '+path)
            self.assertTrue((ROOT/path).read_text()==json.dumps(payload,sort_keys=True,indent=2)+'\n','Exact replay '+path)
        for v in self.packages.values():
            parent=deepcopy(v);revision=parent.pop('review_revision');self.assertEqual(revision,p.digest(p.relevant(parent)))
            changed=deepcopy(parent);changed['periods'][0]['facts']['cfo']['value']='1';self.assertNotEqual(revision,p.digest(p.relevant(changed)))
            self.assertNotIn('history_approval',v);self.assertFalse(v['analyst_complete']);self.assertFalse(v['new_assumptions_active'])
            for r in v['periods']:
                self.assertTrue(all(x is None for x in r['original_supporting_unknowns'].values()))
                self.assertTrue(all(set(c['pending_decisions'])<=ids for c in r['family_checklist']))
                self.assertTrue(any(k.startswith('shares:') and f['as_of'] for k,f in r['facts'].items()))

    def test_eighteen_prior_packages_frozen_pilot_policy_and_count_preservation(self):
        protected=['src','docs/evidence','docs/universe','tests/fixtures','docs/repaired-income-ledger.json','docs/retained-d-and-a-ledger.json','docs/retained-reported-tax-context-ledger.json']
        for t in ('msft','aapl','googl','cost','cat','ko','nvda','amzn','meta','avgo','tsla','lly','mu','amd','jnj','v','intc','wmt'):protected.append(f'docs/company-data-preparation/{t}-analyst-input-package.json')
        self.assertEqual(subprocess.check_output(['git','diff',p.BASELINE,'--',*protected],cwd=ROOT),b'')
        s=self.summary;self.assertEqual(s['completed_company_packages']+s['approved_partial_company_packages']+s['pending_review_company_packages']+s['broad_assessment_only'],42)
        self.assertEqual(s['evidence_acquisition_requirements'],[]);self.assertEqual(s['new_sec_requests'],0)

if __name__=='__main__':unittest.main()
