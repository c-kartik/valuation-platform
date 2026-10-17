"""One retained Alphabet package: literal source tie-outs, not treatment approval."""
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tests.analyst import preservation_projection

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_googl_analyst_package as p


class AlphabetPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.filing=p.AlphabetFiling()

    def test_exact_replay_selected_identity_and_prior_proposals(self):
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Alphabet exact replay differs')
        self.assertEqual(self.result['identity'],dict(cik=1652044,accession='0001652044-25-000014',form='10-K',annual_start='2024-01-01',annual_end='2024-12-31'))
        self.assertEqual(len(self.result['approval_sheet']),6)
        self.assertTrue(all(v['status']==p.PROPOSED and v['accepted'] is False for v in self.result['approval_sheet']))
        self.assertFalse(self.result['valuation_consumption_approved'])
        self.assertEqual(self.result['financial_sufficiency'],'NOT_ASSESSED')
        self.assertEqual(self.result['new_sec_requests'],0)

    def test_literal_income_cfo_tax_and_cash_signs(self):
        e={v['input_id']:v for v in self.result['inputs']}
        facts=self.result['facts']
        for key,amount in [('revenue',350018),('ebit',112390),('pretax',119815),
            ('NetCashProvidedByUsedInOperatingActivities',125299),('IncomeTaxExpenseBenefit',19697),
            ('AllocatedShareBasedCompensationExpense',22800),('ShareBasedCompensation',22785)]:
            self.assertEqual(Decimal(facts[key]['value'])/1000000,amount)
            for o in facts[key]['occurrences']:
                n=self.filing.root[o['ordinal']];attrs,text=self.filing.inline.facts[n.get('id')]
                self.assertEqual(Decimal(n.text),p.inline_amount(attrs,text))
                self.assertEqual(attrs['contextref'],n.get('contextRef'))
        self.assertEqual(e['reported:IncomeTaxesPaidNet']['value'],'-27400000000')
        self.assertEqual(e['reported:PaymentsToAcquirePropertyPlantAndEquipment']['value'],'-52535000000')
        self.assertEqual(e['reported:AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets']['value'],'-2931000000')
        self.assertEqual(e['reported_etr']['value'],'0.1643951091265701289487960605934148')
        self.assertEqual(e['reported_etr']['policy'],'annual_reported_effective_tax_rate_v1')

    def test_manual_rounded_note_never_becomes_exact_instant(self):
        old=json.loads((ROOT/p.NWC_PATH).read_text())
        self.assertEqual(self.result['manual_note_input'],old['bundle']['rounded_note_input'])
        source=self.result['facts']['ap_note_source']
        self.assertIsNone(source['as_of'])
        self.assertEqual(source['precision'],'-8')
        self.assertEqual(source['occurrences'][0]['start'],'2024-01-01')
        self.assertEqual(source['occurrences'][0]['ordinal'],1459)
        self.assertEqual(self.result['manual_note_input']['closing_basis'],'2024-12-31')
        self.assertEqual(self.result['manual_inputs'],['reviewed_ppe_in_ap_note'])
        e={v['input_id']:v for v in self.result['inputs']}
        for key,value in [('proposed_rounded_partial',13342),('whole_ap_partial',10142),('alternative_operating_fines',7020)]:
            self.assertEqual(Decimal(e[key]['value'])/1000000,value)
            self.assertEqual(e[key]['completeness'],'partial')
            self.assertNotIn('accrued_ppe',e[key]['operands'])
            self.assertNotIn('accrued_current_parent',e[key]['operands'])
        self.assertIsNone(self.result['adjacent_book_movement'])
        self.assertFalse(self.result['estimates'])

    def test_da_sbc_deferred_observations_do_not_merge_or_adjust(self):
        e={v['input_id']:v for v in self.result['inputs']}
        self.assertNotEqual(e['reported:ShareBasedCompensation']['role'],e['reported:AllocatedShareBasedCompensationExpense']['role'])
        self.assertEqual(e['reported:AllocatedShareBasedCompensationExpense']['precision']['operand_decimals'],['-8'])
        self.assertEqual(e['reported:ShareBasedCompensation']['precision']['operand_decimals'],['-6'])
        self.assertEqual(self.result['facts']['Depreciation']['value'],'15311000000')
        self.assertEqual(self.result['facts']['FinanceLeaseRightOfUseAssetAmortization']['value'],'413000000')
        self.assertEqual(e['reported:DeferredIncomeTaxesAndTaxCredits']['value'],'-5257000000')
        self.assertEqual(e['reported:DeferredIncomeTaxExpenseBenefit']['value'],'-5256000000')
        self.assertNotIn('expense_da',e)
        self.assertFalse(any('Depreciation' in v['operands'] and 'FinanceLeaseRightOfUseAssetAmortization' in v['operands'] for v in e.values()))
        self.assertTrue(all(v['value'] is None for v in self.result['unresolved_requirements']))

    def test_debt_basis_scope_and_finance_cash_overlap(self):
        e={v['input_id']:v for v in self.result['inputs']}
        for key,amount in [('term_net',11882),('term_parts',11882),('named_borrowing',14182),
            ('proposed_financing',15859),('alternative_all_leases',30437),('op_partition',14578),('finance_partition',1677)]:
            self.assertEqual(Decimal(e[key]['value'])/1000000,amount)
        self.assertEqual(self.result['facts']['debt_discount_signed']['value'],'-118000000')
        self.assertNotIn('op_total',e['proposed_financing']['operands'])
        self.assertNotIn('finance_long',e['term_net']['operands'])
        self.assertEqual(self.result['facts']['debt_repayments']['value'],'12701000000')
        self.assertEqual(self.result['facts']['FinanceLeasePrincipalPayments']['value'],'405000000')
        link=next(v for v in self.result['overlap_relationships'] if v['parent']=='debt_repayments')
        self.assertIn('never add405',link['handling'])
        self.assertFalse(any('debt_repayments' in v['operands'] and 'FinanceLeasePrincipalPayments' in v['operands'] for v in e.values()))

    def test_precision_competitors_restricted_populations_and_nci_subset(self):
        candidate=self.result['precision_candidates']['nonmarketable_equity']
        self.assertEqual([(v['value'],v['precision']) for v in candidate['candidates']],[('35500000000','-8'),('35531000000','-6')])
        self.assertIsNone(candidate['selected_value'])
        self.assertEqual(len(candidate['competing_values']),2)
        self.assertTrue(candidate['unresolved_requirements'])
        for row in candidate['candidates']:
            for o in row['occurrences']:
                node=self.filing.root[o['ordinal']]
                self.assertEqual(node.text,o['raw_value'])
                self.assertEqual(node.get('decimals'),o['precision'])
        self.assertIn('lock-up',self.result['facts']['long_marketable']['location'])
        self.assertEqual(self.result['facts']['long_marketable']['value'],'266000000')
        self.assertEqual(self.result['facts']['nonmarketable_parent']['value'],'37982000000')
        nci=next(v for v in self.result['overlap_relationships'] if v['parent']=='nci_vie')
        self.assertEqual(nci['child'],'redeemable_nci')
        self.assertIn('includes redeemable',self.result['facts']['nci_vie']['location'])
        self.assertEqual(self.result['facts']['preferred_value']['value'],'0')

    def test_class_dates_dimensions_and_awards_remain_separate(self):
        f=self.result['facts']
        for letter,closing,cover in [('a','5835000000','5833000000'),('b','861000000','860000000'),('c','5515000000','5497000000')]:
            self.assertEqual(f['year_end_'+letter]['value'],closing)
            self.assertEqual(f['cover_'+letter]['value'],cover)
            self.assertEqual(f['year_end_'+letter]['as_of'],'2024-12-31')
            self.assertEqual(f['cover_'+letter]['as_of'],'2025-01-28')
            self.assertEqual(f['year_end_'+letter]['precision'],'-3')
            self.assertEqual(f['cover_'+letter]['precision'],'INF')
            self.assertTrue(f['year_end_'+letter]['occurrences'][0]['dimensions'])
        self.assertEqual(f['rsu']['value'],'299000000');self.assertEqual(f['rsu']['precision'],'INF')
        self.assertEqual(f['rsu']['occurrences'][0]['dimensions'],[['us-gaap:AwardTypeAxis','us-gaap:RestrictedStockUnitsRSUMember']])
        self.assertEqual(f['future_sbc']['value'],'34800000000')
        self.assertEqual(f['weighted_diluted']['as_of'],None)
        self.assertFalse(any(set(v['operands']) & {'rsu','year_end_a','year_end_b','year_end_c'} for v in self.result['inputs']))

    def test_original_gap_and_refreshed_receipt_survive_roundtrip(self):
        history=self.result['evidence_history']
        self.assertIsNone(history['original_instance']['retrieved_at_utc']);self.assertIsNone(history['original_instance']['http_status'])
        self.assertEqual(history['body_comparison'],'byte_identical')
        receipt=self.result['sources'][1]
        self.assertEqual(receipt['retained_path'],'docs/evidence/googl-fy2024-instance-provenance-refresh.json')
        self.assertEqual(receipt['retrieved_at_utc'],'2026-10-11T21:10:46.050735+00:00')
        self.assertEqual(receipt['http_status'],200)
        self.assertEqual(receipt['sha256'],history['original_instance']['sha256'])
        self.assertEqual(json.loads(json.dumps(self.result)),self.result)

    def test_scope_passages_and_actual_arithmetic_checks(self):
        self.assertEqual(len(self.result['checks']),12)
        self.assertTrue(all(v['result']=='PASS' and v['difference']=='0' for v in self.result['checks']))
        self.assertTrue(all(v['exact_excerpt'] in self.filing.text for v in self.result['scope_passages']))
        self.assertTrue(any('Financing cash flows used for financing leases' in v['exact_excerpt'] for v in self.result['scope_passages']))
        self.assertEqual(next(v for v in self.result['checks'] if v['check_id']=='displayed_cfo')['observed'],'125299000000')

    def test_bad_date_unit_precision_and_nil_cannot_populate(self):
        for attr,value in [('unitRef','shares'),('decimals','-8'),('text','7986000000'),
            ('{http://www.w3.org/2001/XMLSchema-instance}nil','true')]:
            f=copy.copy(self.filing);f.root=copy.deepcopy(f.root);f.facts={}
            if attr=='text':f.root[470].text=value
            else:f.root[470].set(attr,value)
            with self.assertRaises(ValueError):f.fact('ap','AccountsPayableCurrent','BS',instant=True)
        with self.assertRaisesRegex(ValueError,'absent'):self.filing.fact('ap_annual','AccountsPayableCurrent','BS',instant=False)
        with self.assertRaisesRegex(ValueError,'absent'):
            self.filing.fact('wrong_class','CommonStockSharesOutstanding','BS',instant=True,unit='shares',dimensions=(('us-gaap:StatementClassOfStockAxis','us-gaap:NonexistentMember'),))

    def test_all_original_json_runtime_and_prior_report_helpers_preserved(self):
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',p.BASELINE],cwd=ROOT,text=True).splitlines()
        for path in paths:
            if not (path.startswith('src/') or path.endswith('.json') or path in ('scripts/prepare_msft_analyst_package.py','scripts/prepare_aapl_analyst_package.py')):continue
            before=subprocess.check_output(['git','show',p.BASELINE+':'+path],cwd=ROOT)
            self.assertEqual(preservation_projection(path,(ROOT/path).read_bytes()),preservation_projection(path,before),path)

    def test_missing_inventory_and_duration_note_are_not_zero_or_instant(self):
        with self.assertRaisesRegex(ValueError,'absent'):
            self.filing.fact('inventory','InventoryNet','No eligible current inventory observation',instant=True)
        with self.assertRaisesRegex(ValueError,'absent'):
            self.filing.fact('fake_instant_note','CapitalExpendituresIncurredButNotYetPaid','Note7 duration source',instant=True)
        self.assertNotIn('inventory',self.filing.facts)
        self.assertNotIn('fake_instant_note',self.filing.facts)

    def test_precision_alternative_requires_actual_primary_binding(self):
        f=copy.copy(self.filing);f.inline=copy.deepcopy(f.inline)
        attrs,text=f.inline.facts['f-640'];f.inline.facts['f-640']=(attrs,'35.6')
        evidence=p.inspect.prepare(f.period,f.bundle.artifacts,tuple(p.inspect.ArtifactBinding(r.artifact.url,r.artifact.sha256,
            'instance' if r is f.instance else 'support') for r in f.bundle.artifacts))
        with self.assertRaisesRegex(ValueError,'precision alternative mismatch'):
            p.variants(f,evidence,'nonmarketable_equity','EquitySecuritiesWithoutReadilyDeterminableFairValueAmount')


    def test_accepted_selections_precision_and_nondefault_history(self):
        v=self.result['accepted_view']
        for key,amount in [('operating_capital','13342000000'),('borrowings','15859000000'),
                           ('current_financial_balances','95657000000'),('sbc_expense_proxy','22800000000')]:
            selected=v[key]
            self.assertEqual(selected['selected']['value'],amount)
            self.assertEqual(selected['review'],p.APPROVED_SCOPE)
            self.assertTrue(selected['selected']['accepted'])
            self.assertEqual(selected['approval_sha256'],v['approval_audit']['sha256'])
        self.assertIn('-8',v['operating_capital']['selected']['precision']['operand_decimals'])
        self.assertEqual(v['manual_note_input'],self.result['manual_note_input'])
        self.assertEqual([x['observation']['value'] for x in v['nondefault_history']],
                         ['10142000000','7020000000','30437000000'])
        self.assertTrue(all(x['default'] is False for x in v['nondefault_history']))
        self.assertEqual(v['lease_classification']['operating'],'service_cost')
        self.assertEqual(v['lease_classification']['finance'],'asset_financing')
        self.assertIsNone(v['lease_classification']['finance_amortization_inclusion_assumption'])

    def test_accepted_nulls_roles_overlap_and_history_survive_round_trip(self):
        v=json.loads(json.dumps(self.result))['accepted_view']
        self.assertEqual(v['unresolved_requirements'],self.result['unresolved_requirements'])
        self.assertTrue(all(x['value'] is None for x in v['unresolved_requirements']))
        self.assertIsNone(v['complete_expense_basis_da']['value'])
        self.assertEqual([x['value'] for x in v['da_observations']],['15311000000','413000000'])
        self.assertEqual(v['sbc_cfo_addback']['value'],'22785000000')
        self.assertEqual([x['value'] for x in v['investment_columns'][:3]],
                         ['-52535000000','-2931000000','-2667000000'])
        self.assertTrue(v['finance_principal_already_in_debt_repayments'])
        self.assertEqual(v['lease_cash_and_debt_repayments'][2]['value'],'-405000000')
        self.assertEqual(v['lease_cash_and_debt_repayments'][3]['value'],'-12701000000')
        self.assertTrue(v['nci_includes_redeemable'])
        self.assertEqual([x['observation']['value'] for x in v['separate_claims'][:2]],['4200000000','1100000000'])
        self.assertEqual(v['overlap_relationships'],self.result['overlap_relationships'])
        self.assertEqual(v['evidence_history'],self.result['evidence_history'])
        self.assertEqual(v['precision_candidates'],self.result['precision_candidates'])
        self.assertEqual(len(v['separate_shares_and_awards']),11)
        for key in ('book_delta_nwc','cash_delta_nwc','opening_balance','unknown_restrictions','operating_reserve'):
            self.assertIsNone(v[key])
        for key in ('complete_operating_capital','complete_debt','complete_reinvestment','unrestricted_or_excess_cash',
                    'phase1_closed','valuation_consumption_approved','future_tax_assumption_approved',
                    'award_valuation_approved','dilution_estimate_approved'):
            self.assertIs(v[key],False)

    def test_original_proposal_and_peer_views_unchanged(self):
        original=json.loads(subprocess.check_output(['git','show',p.ACCEPTANCE_BASIS+':'+p.OUTPUT],cwd=ROOT))
        proposal={k:v for k,v in self.result.items() if k not in ('accepted_view','googl_history_review')}
        self.assertTrue(proposal==original,'Original Alphabet proposal changed')
        for path in ('scripts/prepare_aapl_analyst_package.py','scripts/prepare_msft_analyst_package.py',
            'docs/company-data-preparation/aapl-analyst-input-package.json',
            'docs/company-data-preparation/msft-analyst-input-package.json',
            'docs/company-data-preparation/aapl-analyst-treatment-acceptance.json',
            'docs/company-data-preparation/msft-analyst-treatment-acceptance.json'):
            expected=subprocess.check_output(['git','show',p.ACCEPTANCE_BASIS+':'+path],cwd=ROOT)
            self.assertEqual(preservation_projection(path,(ROOT/path).read_bytes()),preservation_projection(path,expected),path)

    def test_audit_persistence_staleness_and_tamper_rejection(self):
        proposal={k:v for k,v in self.result.items() if k not in ('accepted_view','googl_history_review')}
        audit=json.loads((ROOT/p.ACCEPTANCE_PATH).read_text())
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'audit.json';path.write_text(json.dumps(audit))
            self.assertTrue(p.accepted_view(proposal,path)=={k:v for k,v in self.result.items() if k!='googl_history_review'},'Persisted replay differs')
            for key in ('facts','inputs','manual_note_input','sources','precision_candidates','unresolved_requirements'):
                changed=copy.deepcopy(proposal)
                changed[key]=dict(changed=changed[key])
                with self.assertRaisesRegex(ValueError,'Stale Alphabet acceptance'):
                    p.accepted_view(changed,path)
            bad=copy.deepcopy(audit);bad['decisions']['DA-INVESTMENT']='approve complete D&A'
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'malformed Alphabet'):
                p.accepted_view(proposal,path)
            bad['sha256']=p.digest({k:v for k,v in bad.items() if k!='sha256'})
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'Unregistered Alphabet'):
                p.accepted_view(proposal,path)
            path.unlink()
            with self.assertRaises(FileNotFoundError):p.accepted_view(proposal,path)

    def test_no_replay_auto_approval_or_aliasing(self):
        run=subprocess.run([sys.executable,str(ROOT/'scripts/prepare_googl_analyst_package.py'),
                            '--record-approved-treatment-set'],capture_output=True,text=True,cwd=ROOT)
        self.assertNotEqual(run.returncode,0)
        self.assertIn('already exists',run.stderr)
        proposal={k:copy.deepcopy(v) for k,v in self.result.items() if k not in ('accepted_view','googl_history_review')}
        out=p.accepted_view(proposal)
        out['accepted_view']['unresolved_requirements'].clear()
        self.assertEqual(len(proposal['unresolved_requirements']),9)
        self.assertEqual(len(out['unresolved_requirements']),9)


if __name__=='__main__':unittest.main()
