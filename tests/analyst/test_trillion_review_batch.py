"""One fixed retained review replay; no active analyst approvals."""
from copy import deepcopy
from dataclasses import replace
from datetime import date
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_trillion_review_batch as p
import tests.analyst.test_standard_review_batch as standard_tests


class TrillionReviewBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs=p.outputs()
        cls.packages={t:cls.outputs[f'docs/company-data-preparation/{t.lower()}-analyst-input-package.json'] for t in p.TICKERS}
        cls.summary=cls.outputs[p.SUMMARY];cls.artifact_files={}

    _artifact=standard_tests.StandardReviewBatchTests._artifact

    def test_exact_replay_serialization_scope_and_inactive_decisions(self):
        for path,payload in self.outputs.items():
            self.assertEqual((ROOT/path).read_text(),json.dumps(payload,sort_keys=True,indent=2)+'\n',path)
            self.assertTrue(json.loads(json.dumps(payload))==payload,'Round-trip payload differs: '+path)
        self.assertEqual(len(self.summary['decisions']),25)
        self.assertEqual(self.summary['evidence_acquisition_requirements'],[])
        for d in self.summary['decisions']:
            self.assertFalse(d['accepted']);self.assertEqual(d['status'],p.PROPOSED);self.assertEqual(len(d['identities']),5)
        self.assertFalse(self.summary['new_assumptions_active'])
        self.assertEqual((self.summary['completed_company_packages'],self.summary['reviewed_pending_company_packages'],self.summary['broad_assessment_only']),(3,6,33))

    def test_exact_selected_identities_and_fourteen_family_accounting(self):
        income=json.loads((ROOT/'docs/repaired-income-ledger.json').read_text())
        manifest=json.loads((ROOT/p.shared.MANIFEST).read_text())
        all_ids=[]
        for t,package in self.packages.items():
            self.assertEqual(len(package['periods']),5);self.assertEqual(package['family_slots'],70)
            self.assertFalse(package['analyst_complete'])
            expected=sorted([r['identity'] for r in income['rows'] if r['issuer']==t],key=lambda x:x['annual_end'])
            self.assertEqual([r['identity'] for r in package['periods']],expected)
            if t!='META':
                self.assertEqual(expected,sorted([r['identity'] for r in manifest['rows'] if r['identity']['cik']==expected[0]['cik']],key=lambda x:x['annual_end']))
            for r in package['periods']:
                all_ids.append(r['identity']['accession'])
                self.assertEqual({c['field'] for c in r['family_checklist']},{f.value for f in p.shared.h.Field})
                self.assertFalse(any(c['financial_complete'] for c in r['family_checklist']))
                self.assertIsNone(r['original_supporting_unknowns']['complete_expense_da'])
        self.assertEqual(len(set(all_ids)),15);self.assertEqual(self.summary['family_slots'],210)

    def test_every_raw_occurrence_and_original_receipt(self):
        # Reuses the existing source test, not expected values generated from
        # this assembly. It opens every original XML/primary body and locator.
        standard_tests.StandardReviewBatchTests.test_every_source_occurrence_primary_representation_and_receipt(self)

    def test_literal_source_statement_amounts_and_cash_signs(self):
        literals={
            'NVDA':{'revenue':[26914,26974,60922,130497,215938],'ebit':[10041,4224,32972,81453,130387],
                    'cfo':[9108,5641,28090,64089,102718],'combined_investment':[976,1833,1069,3236,6042]},
            'AMZN':{'revenue':[469822,513983,574785,637959,716924],'ebit':[24879,12248,36852,68593,79975],
                    'cfo':[46327,46752,84946,115877,139514],'productive_cash':[61053,63645,52729,82999,131819]},
            'META':{'revenue':[117929,116609,134902,164501,200966],'ebit':[46753,28944,46751,69380,83276],
                    'cfo':[57683,50475,71113,91328,115800],'cash_capex':[18567,31431,27266,37256,69691]}}
        for t,fields in literals.items():
            for key,expected in fields.items():
                self.assertEqual([D(r['facts'][key]['value'])/1000000 for r in self.packages[t]['periods']],expected,(t,key))
                if key in ('combined_investment','productive_cash','cash_capex'):
                    for r in self.packages[t]['periods']:self.assertEqual(r['cash_sign_multipliers'][key],-1)

    def test_nvda_scope_extension_gates_and_non_cash_not_cash_split(self):
        for i,r in enumerate(self.packages['NVDA']['periods']):
            self.assertNotIn('cash_capex',r['facts']);self.assertIsNone(r['original_supporting_unknowns']['pure_ppe_cash'])
            fact=r['facts']['combined_investment'];self.assertIn('nvidia' if i<2 else 'fasb',fact['namespace'])
            self.assertEqual(D(r['facts']['capital_creditors']['value'])/1000000,[258,374,170,525,820][i])
            self.assertEqual(r['preparation_ledger_evidence']['refreshed-capex-ledger']['source_record']['status'],'UNAPPROVED_SCOPE')
        self.assertEqual(self.packages['NVDA']['periods'][-1]['facts']['groq_payment']['value'],'13000000000')
        self.assertTrue(all(not c['accepted'] for c in self.summary['decisions'] if c['ticker']=='NVDA'))

    def test_amzn_negative_da_history_and_narrow_proxy_operands(self):
        expected=[23421,25528,30931,32905,42677]
        broad=[34296,41921,48663,52795,65756]
        for r,value,old in zip(self.packages['AMZN']['periods'],expected,broad):
            self.assertEqual(r['preparation_ledger_evidence']['retained-d-and-a-ledger']['source_record']['status'],'SCOPE_DOWNGRADED')
            proxy=next(c for c in r['calculations'] if c['input_id']=='limited_expense_da_proxy')
            self.assertEqual(D(proxy['value'])/1000000,value);self.assertEqual(proxy['origin'],'proxy');self.assertEqual(proxy['status'],p.PROPOSED)
            self.assertEqual(proxy['operands'],['ppe_da','intangible_amortization'])
            self.assertEqual(D(r['facts']['da']['value'])/1000000,old)
            self.assertGreaterEqual(len(r['alternatives']['depreciation']['candidates']),2)
            self.assertEqual(r['facts']['da']['role'],'cfo_reconciliation_observation')
            self.assertEqual(r['facts']['ppe_da']['role'],'recognized_expense_observation')

    def test_amzn_financing_populations_comparative_binding_and_tax_precision(self):
        for r,value in zip(self.packages['AMZN']['periods'],[81109,100898,85935,75805,89295]):
            calc=next(c for c in r['calculations'] if c['input_id']=='named_financing')
            self.assertEqual(D(calc['value'])/1000000,value)
            self.assertNotIn('debt_parent',calc['operands']);self.assertNotIn('op_lease',calc['operands'])
            self.assertFalse('working_credit' in calc['operands'] and 'short_borrowing' in calc['operands'])
            self.assertEqual(r['facts']['financing_long']['precision'],'-8')
            self.assertGreaterEqual(len(r['alternatives']['selected_tax']['candidates']),2)
        first=self.packages['AMZN']['periods'][0]
        extra=first['supplemental_source_observations'][0]
        self.assertEqual(extra['source_identity']['annual_end'],'2022-12-31');self.assertEqual(extra['fact']['as_of'],'2021-12-31')
        self.assertEqual(extra['fact']['value'],'318000000')
        self.assertEqual(next(c['value'] for c in first['calculations'] if c['input_id']=='known_facility_expanded_financing'),'81427000000')
        self.assertEqual([r['facts']['selected_tax']['value'] for r in self.packages['AMZN']['periods']],['4791000000','-3217000000','7120000000','9265000000','19087000000'])

    def test_independent_display_sums_preserve_original_meta_partials(self):
        proofs=json.loads((ROOT/p.shared.LEDGER).read_text())
        for t,package in self.packages.items():
            for r in package['periods']:
                original=next(x for x in proofs['rows'] if x['identity']['fields']['accession']==r['identity']['accession'])
                self.assertEqual(r['cfo_reconciliation'],original['reconciliation'])
                manual=r['independent_display_check']
                if manual:
                    self.assertEqual(r['cfo_reconciliation']['status'],'PARTIAL');self.assertEqual(manual['status'],'SUPPORTED')
                    self.assertEqual(sum((D(x['value']) for x in manual['rows']),D(0)),D(r['facts']['cfo']['value']))
                    self.assertEqual(manual['difference'],'0');self.assertEqual(manual['tolerance'],'0')
                else:self.assertEqual(r['cfo_reconciliation']['status'],'SUPPORTED')
                self.assertFalse(any('residual' in c['input_id'] for c in r['calculations']))
        self.assertEqual(sum(r['independent_display_check'] is not None for r in self.packages['META']['periods']),3)

    def test_share_dates_classes_splits_and_no_automatic_totals(self):
        for t,values in [('NVDA',[2506,2466,2464,24477,24304]),('AMZN',[509,10242,10383,10593,10731])]:
            for r,value in zip(self.packages[t]['periods'],values):
                facts=[v for k,v in r['facts'].items() if k.startswith('shares:CommonStockSharesOutstanding:')]
                self.assertTrue(any(D(x['value'])/1000000==value for x in facts))
                self.assertTrue(all(x['as_of']==r['identity']['annual_end'] for x in facts))
        for r in self.packages['META']['periods']:
            facts=[v for k,v in r['facts'].items() if k.startswith('shares:CommonStockSharesOutstanding:')]
            self.assertEqual(len(facts),3)  # source A, B and independently reported aggregate, not our sum
            self.assertFalse(any('shares' in c['input_id'] for c in r['calculations']))
        self.assertFalse(any(x['new_assumptions_active'] for p_ in self.packages.values() for x in p_['periods']))

    def test_primary_binding_fail_closed_and_receipt_tamper(self):
        r=self.packages['META']['periods'][1];sources={s['role']:s for s in r['sources']}
        receipts=[]
        for role in ('primary','instance'):
            a,body=self._artifact(sources[role]);receipts.append(p.shared.cash._receipt(dict(a,accession=r['identity']['accession']),body))
            with self.assertRaises((ValueError,p.shared.h.InputError)):
                p.shared.cash._receipt(dict(a,accession=r['identity']['accession']),body+b'tampered')
        root,contexts,units,namespaces=p.shared.cash._instance(tuple(receipts),p.shared.cash.Period(r['identity']['cik'],r['identity']['accession'],date.fromisoformat(r['identity']['annual_start']),date.fromisoformat(r['identity']['annual_end'])))
        f=types.SimpleNamespace(root=root,contexts=contexts,units=units,namespaces=namespaces,period=p.shared.cash.Period(r['identity']['cik'],r['identity']['accession'],date.fromisoformat(r['identity']['annual_start']),date.fromisoformat(r['identity']['annual_end'])))
        inline=p.shared.InlineFacts();inline.feed(receipts[0].artifact.body.decode())
        fact=r['independent_display_check']['rows'][0]['fact'];o=fact['occurrences'][0]
        attrs,text=inline.facts[o['primary_locator'].removeprefix('inline#')];item=dict(attrs=attrs,text=text)
        self.assertEqual(p.primary_fact(dict(filing=f),item,0,0,0,'actual source')['value'],fact['value'])
        f.period=replace(f.period,annual_start=date(2021,1,1))
        with self.assertRaises(ValueError):p.primary_fact(dict(filing=f),item,0,0,0,'wrong annual')
        f.period=replace(f.period,annual_start=date(2022,1,1));f.namespaces=dict(namespaces,iso4217='urn:wrong-unit')
        # Alter the actual USD unit namespace prefix, not a guessed alias.
        measure=units[attrs['unitref']][0].text;f.namespaces[measure.split(':')[0]]='urn:wrong-unit'
        with self.assertRaises(ValueError):p.primary_fact(dict(filing=f),item,0,0,0,'wrong unit')

    def test_revision_binding_and_all_prior_package_bytes_unchanged(self):
        for package in self.packages.values():
            value=deepcopy(package);value.pop('history_approval',None);value.pop('current_history',None);revision=value.pop('review_revision');self.assertEqual(p.digest(p.relevant(value)),revision)
            value['periods'][0]['facts']['cfo']['value']='1';self.assertNotEqual(p.digest(p.relevant(value)),revision)
        names=[f'docs/company-data-preparation/{t}-analyst-input-package.json' for t in ('msft','aapl','googl','cost','cat','ko')]
        names+=['docs/company-data-preparation/standard-review-batch.json']
        for name in names:
            original=subprocess.check_output(['git','show',p.BASELINE+':'+name],cwd=ROOT)
            current=json.loads((ROOT/name).read_text())
            # Only additive approved views/audits may differ; original proposal
            # snapshots remain exact, not replaced by newly accepted numbers.
            for key in ('history_approval','current_history','approval_activation'):current.pop(key,None)
            self.assertEqual(json.dumps(current,sort_keys=True,indent=2).encode()+b'\n',original,name)
        diff=subprocess.check_output(['git','diff','--name-only',p.BASELINE,'--','src','docs/evidence','docs/universe','tests/fixtures'],cwd=ROOT,text=True)
        self.assertEqual(diff,'')


if __name__=='__main__':unittest.main()
