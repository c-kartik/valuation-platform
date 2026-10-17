"""Fixed fifteen-period retained-source batch; no automatic financial approval."""
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_standard_review_batch as p


class StandardReviewBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs();cls.summary=cls.outputs['docs/company-data-preparation/standard-review-batch.json']
        cls.packages={t:cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'] for t in p.TICKERS}
        cls.artifact_files={}

    def test_exact_frozen_fifteen_identity_bindings(self):
        accs={'COST':['0000909832-22-000021','0000909832-23-000042','0000909832-24-000049','0000909832-25-000101','0000909832-26-000093'],
            'CAT':['0000018230-22-000050','0000018230-23-000011','0000018230-24-000009','0000018230-25-000008','0000018230-26-000008'],
            'KO':['0000021344-22-000009','0000021344-23-000011','0000021344-24-000009','0000021344-25-000011','0001628280-26-010047']}
        for t,package in self.packages.items():
            self.assertEqual([r['identity']['accession'] for r in package['periods']],accs[t])
            self.assertEqual(len(package['periods']),5);self.assertEqual(package['family_slots'],70)
            for r in package['periods']:
                self.assertEqual(len({c['field'] for c in r['family_checklist']}),14)
                self.assertEqual(r['identity']['form'],'10-K')
                self.assertTrue(all(not c['financial_complete'] for c in r['family_checklist']))
        self.assertEqual(self.packages['COST']['periods'][1]['identity']['annual_start'],'2022-08-29')
        self.assertEqual(self.packages['COST']['periods'][1]['identity']['annual_end'],'2023-09-03')
        self.assertEqual(self.summary['family_slots'],210)

    def test_literal_retained_income_da_cfo_and_capex_values(self):
        expectations={
            'COST':{'revenue':[226954,242290,254453,275235,303154],'ebit':[7793,8114,9285,10383,11685],'cfo':[7392,11068,11339,13335,15817],'da':[1900,2077,2237,2426,2674],'cash_capex':[3891,4323,4710,5498,6435]},
            'CAT':{'revenue':[50971,59427,67060,64809,67589],'ebit':[6878,7904,12966,13072,11151],'cfo':[7198,7766,12885,12035,11739],'da':[2352,2219,2144,2153,2262],'cash_capex':[1093,1296,1597,1988,2821]},
            'KO':{'revenue':[38655,43004,45754,47061,47941],'ebit':[10308,10909,11311,9992,13762],'cfo':[12625,11018,11599,6805,7408],'da':[1452,1260,1128,1075,1050],'cash_capex':[1367,1484,1852,2064,2112]}}
        for t,fields in expectations.items():
            for k,values in fields.items():self.assertEqual([D(r['facts'][k]['value'])/1000000 for r in self.packages[t]['periods']],values,(t,k))

    def _artifact(self,source):
        if source['path'] not in self.artifact_files:self.artifact_files[source['path']]=json.loads((ROOT/source['path']).read_text())
        doc=self.artifact_files[source['path']];a=doc['artifacts'][int(source['pointer'].split('/')[-1])]
        encoded=a['response_body_gzip_base64'];body=p.cash.gzip.decompress(p.cash.base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded,validate=True))
        return a,body

    def test_every_source_occurrence_primary_representation_and_receipt(self):
        count=0
        for package in self.packages.values():
            for r in package['periods']:
                sources={s['role']:s for s in r['sources']};primary,html=self._artifact(sources['primary']);instance,body=self._artifact(sources['instance'])
                for s,raw in [(sources['primary'],html),(sources['instance'],body)]:
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),s['sha256']);self.assertEqual(len(raw),s['byte_length']);self.assertEqual(s['http_status'],200)
                root=ET.fromstring(body);inline=p.InlineFacts();inline.feed(html.decode())
                text=' '.join(' '.join(inline.text).split())
                for excerpt in r['passages']:self.assertIn(excerpt['exact_excerpt'],text)
                for key,fact in r['facts'].items():
                    if fact.get('representation')=='primary_note_table_not_XBRL':
                        self.assertEqual(fact['occurrences'],[]);self.assertIn('note_evidence',fact);continue
                    for o in fact['occurrences']:
                        node=root[o['ordinal']];self.assertEqual(node.text,o['raw_value']);self.assertEqual(node.get('contextRef'),o['context_id']);self.assertEqual(node.get('unitRef'),o['unit_id']);self.assertEqual(node.get('decimals'),o['precision'])
                        self.assertEqual(D(node.text),D(fact['value']));self.assertEqual(node.tag,'{'+fact['namespace']+'}'+fact['concept'])
                        attrs,text=inline.facts[o['primary_locator'].removeprefix('inline#')]
                        self.assertEqual(attrs['contextref'],o['context_id']);self.assertEqual(attrs['decimals'],o['precision'])
                        if attrs.get('format') in ('ixt:fixed-zero','ixt:zerodash'):self.assertEqual(D(node.text),0)
                        else:self.assertEqual(p.inline_amount(attrs,text),D(node.text))
                        count+=1
        self.assertGreater(count,600)

    def test_independent_cfo_replay_movement_signs_and_no_residual(self):
        expected_counts={'COST':[9,8,8,8,9],'CAT':[13,14,15,15,14],'KO':[10]*5}
        for t,package in self.packages.items():
            for r,n in zip(package['periods'],expected_counts[t]):
                reconciliation=r['cfo_reconciliation'];self.assertEqual(reconciliation['status'],'SUPPORTED')
                pop=reconciliation['populations'][0];self.assertEqual(len(pop['rows']),n)
                self.assertEqual(sum((D(x['value']) for x in pop['rows']),D(0)),D(pop['cfo']['value']))
                for x in pop['rows']:self.assertEqual(D(x['raw'])*x['sign'],D(x['value']))
                self.assertEqual(r['cash_sign_multipliers']['cash_capex'],-1)
                self.assertFalse(any('residual' in x['input_id'] for x in r['calculations']))
        self.assertEqual([len(r['movement_rows']) for r in self.packages['KO']['periods']],[1]*5)
        self.assertEqual([len(r['movement_rows']) for r in self.packages['CAT']['periods']],[7]*5)

    def test_cat_dual_perimeter_not_a_consolidated_operating_company_approval(self):
        cat=self.packages['CAT'];self.assertEqual(cat['scope_gate'],'CAPTIVE_FINANCE_PERIMETER_PENDING')
        self.assertEqual(cat['outcomes']['PROPOSED_PENDING_APPROVAL'],70)
        expected={'consolidated':[37789,36993,37878,38409,43330],'industrial':[9826,9652,9670,8777,10990],'financial_products':[27989,27372,28255,29799,33617]}
        for scope,values in expected.items():self.assertEqual([next(D(x['value'])/1000000 for x in r['calculations'] if x['input_id']=='named_borrowing_'+scope) for r in cat['periods']],values)
        for r,amount in zip(cat['periods'],[7177,6358,11688,11437,12278]):
            row=next(x for x in r['supplemental_populations'] if x['caption']=='Net cash provided by (used for) operating activities')
            self.assertEqual(D(row['values']['industrial']['value_usd'])/1000000,amount)
            self.assertIn('Machinery',row['header']);self.assertIn('FinancialProducts',row['header'])
            self.assertTrue(all('CAT-PERIMETER' in c['pending_decisions'] for c in r['family_checklist']))
        self.assertIn('Power',cat['periods'][-1]['supplemental_populations'][0]['header'])

    def test_cost_finance_note_not_residual_and_proxy_assumption_not_accepted(self):
        for r,da,fin in zip(self.packages['COST']['periods'],[2028,2246,2334,2528,2780],[8273,7890,7395,7267,7575]):
            entries={x['input_id']:x for x in r['calculations']}
            proxy=entries['limited_finance_inclusive_da_proxy'];self.assertEqual(proxy['origin'],'proxy');self.assertEqual(proxy['status'],p.PROPOSED)
            self.assertEqual(D(proxy['value'])/1000000,da);self.assertEqual(proxy['operands'],['da','finance_amortization'])
            self.assertEqual(D(entries['named_financing']['value'])/1000000,fin)
            self.assertEqual(len(r['lease_note_populations']),2)
            self.assertEqual(r['facts']['finance_note_current']['representation'],'primary_note_table_not_XBRL')
            self.assertEqual(D(entries['gross_sbc_expense']['value']),D(r['facts']['sbc_addback']['value']))
            self.assertEqual(r['facts']['preferred']['value'],'0')
        self.assertEqual(self.packages['COST']['periods'][0]['facts']['other_short_borrowing']['value'],'88000000')
        self.assertEqual(self.packages['COST']['outcomes'],dict(SOURCE_SUPPORTED=32,PROPOSED_PENDING_APPROVAL=38))

    def test_ko_sbc_pension_and_financing_overlaps_are_explicit(self):
        rows=self.packages['KO']['periods']
        self.assertEqual([D(r['facts']['sbc_expense']['value'])/1000000 for r in rows],[337,361,251,286,279])
        self.assertEqual([D(r['facts']['sbc_addback']['value'])/1000000 for r in rows],[337,356,254,286,279])
        for r,fin in zip(rows,[42761,39149,42064,44522,45492]):
            c=next(x for x in r['calculations'] if x['input_id']=='named_financing');self.assertEqual(D(c['value'])/1000000,fin)
            if 'short_borrowing' in c['operands']:self.assertNotIn('cp',c['operands'])
            self.assertNotIn('op_lease',c['operands'])
        for r,amount in zip(rows,[325,782,716,390,295]):self.assertEqual(D(r['facts']['PensionPlansDefinedBenefitMember:DefinedBenefitPlanFundedStatusOfPlan']['value'])/1000000,amount)
        for r,amount in zip(rows,[-277,-122,-121,-116,-112]):self.assertEqual(D(r['facts']['OtherPostretirementBenefitPlansDefinedBenefitMember:DefinedBenefitPlanFundedStatusOfPlan']['value'])/1000000,amount)
        self.assertEqual(next(x for x in rows[-1]['calculations'] if x['input_id']=='held_sale_named_borrowing')['value'],'1435000000')
        self.assertTrue(rows[-1]['facts']['held_sale_short']['namespace'].startswith('http://www.thecocacolacompany.com/'))

    def test_dated_shares_awards_and_raw_precision_never_summed(self):
        for package in self.packages.values():
            for r in package['periods']:
                shares={k:v for k,v in r['facts'].items() if k.startswith('shares:')}
                self.assertTrue(shares)
                for k,v in shares.items():self.assertEqual(v['unit'],'shares');self.assertIn(v['as_of'],k);self.assertIsNotNone(v['precision'])
                self.assertFalse(any(any(k.startswith('shares:') for k in x.get('operands',[]) if isinstance(k,str)) for x in r['calculations']))
        cost=self.packages['COST']['periods'][-1]
        common=next(v for k,v in cost['facts'].items() if k.startswith('shares:CommonStockSharesOutstanding') and not v['occurrences'][0]['dimensions'])
        self.assertEqual(common['value'],'443266000');self.assertEqual(common['as_of'],'2026-08-30')

    def test_one_consolidated_inactive_table_and_no_sufficiency(self):
        table=self.summary['decisions'];ids={r['decision_id'] for r in table};self.assertEqual(len(table),23);self.assertEqual(len(ids),23)
        for package in self.packages.values():
            self.assertFalse(package['analyst_complete']);self.assertFalse(package['new_assumptions_active']);self.assertFalse(package['phase1_closed'])
            for r in package['periods']:
                self.assertTrue(all(v is None for v in r['original_supporting_unknowns'].values()))
                for family in r['family_checklist']:self.assertTrue(set(family['pending_decisions'])<=ids)
        for r in table:self.assertFalse(r['accepted']);self.assertEqual(r['status'],p.PROPOSED);self.assertEqual(len(r['identities']),5)
        self.assertEqual(self.summary['evidence_acquisition_requirements'],[]);self.assertEqual(self.summary['new_sec_requests'],0)

    def test_exact_batch_serialization_replay_revisions_and_original_artifacts(self):
        for name,value in self.outputs.items():
            self.assertTrue(json.loads((ROOT/name).read_text())==value,'Batch replay differs: '+name)
            self.assertTrue(json.loads(json.dumps(value))==value,'Round trip differs: '+name)
        for package in self.packages.values():self.assertEqual(package['review_revision'],p.digest(p.relevant({k:v for k,v in package.items() if k!='review_revision'})))
        for t in ['aapl','msft','googl']:
            name=f'docs/company-data-preparation/{t}-analyst-input-package.json';self.assertEqual((ROOT/name).read_bytes(),subprocess.check_output(['git','show',p.BASELINE+':'+name],cwd=ROOT))
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',p.BASELINE,'src','docs/evidence','docs/universe'],cwd=ROOT,text=True).splitlines()
        for name in paths:self.assertTrue((ROOT/name).read_bytes()==subprocess.check_output(['git','show',p.BASELINE+':'+name],cwd=ROOT),'Preservation differs: '+name)

    def test_tampered_receipt_wrong_period_and_conflict_fail_closed(self):
        r=self.packages['COST']['periods'][0];s=next(s for s in r['sources'] if s['role']=='instance');a,body=self._artifact(s)
        with self.assertRaises(ValueError):p.cash._receipt(dict(a,accession=r['identity']['accession']),body+b'changed')
        with self.assertRaises(ValueError):p.cash._receipt(dict(a,accession=r['identity']['accession'],http_status=500),body)
        receipt=p.cash._receipt(dict(a,accession=r['identity']['accession']),body)
        period=p.cash.Period(r['identity']['cik'],r['identity']['accession'],p.date(2022,1,1),p.date(2022,12,31))
        with self.assertRaises(ValueError):p.cash._instance((receipt,),period)
        fake=types.SimpleNamespace(namespaces={'us-gaap':'namespace'},fact=lambda *a,**k:(_ for _ in ()).throw(ValueError('Conflicting original')))
        with patch.object(p.inspect,'inspect',return_value=types.SimpleNamespace(candidates=('candidate',),competing_values=('1','2'))):
            with self.assertRaisesRegex(ValueError,'Conflicting'):p.monetary({'filing':fake,'evidence':None},'cash','CashAndCashEquivalentsAtCarryingValue',True)


if __name__=='__main__':unittest.main()
