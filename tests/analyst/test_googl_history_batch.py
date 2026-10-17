"""Five retained filings, one pending decision table; no new acceptance."""
import copy
from decimal import Decimal as D, localcontext
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
import prepare_googl_analyst_package as p


class AlphabetHistoryBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.review=cls.result['googl_history_review'];cls.rows=cls.review['periods']

    def test_exact_frozen_selections_and_seventy_requirements(self):
        expected=['0001652044-22-000019','0001652044-23-000016','0001652044-24-000022','0001652044-25-000014','0001652044-26-000018']
        self.assertEqual([r['identity']['accession'] for r in self.rows],expected)
        for year,r in zip(range(2021,2026),self.rows):
            self.assertEqual(r['identity']['annual_start'],f'{year}-01-01');self.assertEqual(r['identity']['annual_end'],f'{year}-12-31')
            self.assertEqual(len({c['field'] for c in r['family_checklist']}),14)
            self.assertFalse(r['analyst_complete']);self.assertFalse(r['new_assumptions_active'])
        self.assertEqual(self.review['outcomes'],dict(SOURCE_SUPPORTED=29,EXISTING_SCOPED_APPROVAL=9,PROPOSED_PENDING_APPROVAL=32,ESSENTIAL_EVIDENCE_EXCEPTION=0))

    def test_literal_source_amounts_not_peer_or_comparative_selections(self):
        expected={'revenue':[257637,282836,307394,350018,402836],'ebit':[78714,74842,84293,112390,129039],
            'NetCashProvidedByUsedInOperatingActivities':[91652,91495,101746,125299,164713],
            'PaymentsToAcquirePropertyPlantAndEquipment':[24640,31485,32251,52535,91447],
            'IncomeTaxExpenseBenefit':[14701,11356,11922,19697,26656],
            'IncomeTaxesPaidNet':[13412,18892,19164,27400,21526]}
        for key,amounts in expected.items():
            self.assertEqual([D(r['facts'][key]['value'])/1000000 for r in self.rows],list(map(D,amounts)),key)
        for r in self.rows:
            calc={v['input_id']:v for v in r['calculations']}
            with localcontext() as context:
                context.prec=34
                self.assertEqual(D(calc['reported_etr']['value']),D(r['facts']['IncomeTaxExpenseBenefit']['value'])/D(r['facts']['pretax']['value']))
            self.assertEqual(r['cash_signs']['PaymentsToAcquirePropertyPlantAndEquipment'],-1)

    def test_exact_receipts_and_every_occurrence_rebind_to_original_body(self):
        import xml.etree.ElementTree as ET
        for r in self.rows:
            bodies=[]
            for s in r['sources']:
                a=json.loads((ROOT/s['path']).read_text())['artifacts'][int(s['pointer'].split('/')[-1])]
                encoded=a['response_body_gzip_base64'];body=p.cash.gzip.decompress(p.cash.base64.b64decode(''.join(encoded) if isinstance(encoded,list) else encoded,validate=True))
                self.assertEqual(hashlib.sha256(body).hexdigest(),s['sha256']);self.assertEqual(len(body),s['byte_length']);self.assertEqual(s['http_status'],200)
                self.assertTrue(s['byte_equivalence_verified']);bodies.append(body)
            self.assertIsNone(r['sources'][1]['original_retrieved_at_utc']);self.assertIsNone(r['sources'][1]['original_http_status'])
            root=ET.fromstring(bodies[1]);inline=p.InlineFacts();inline.feed(bodies[0].decode())
            for fact in r['facts'].values():
                for occurrence in fact['occurrences']:
                    node=root[occurrence['ordinal']]
                    self.assertEqual(node.text,occurrence['raw_value']);self.assertEqual(node.get('decimals'),occurrence['precision'])
                    self.assertEqual(node.get('contextRef'),occurrence['context_id']);self.assertEqual(node.get('unitRef'),occurrence['unit_id'])
                    self.assertEqual(D(node.text),D(fact['value']))
                    attrs,display=inline.facts[node.get('id')]
                    if attrs.get('format')=='ixt:fixed-zero':self.assertEqual(D(node.text),0)
                    else:self.assertEqual(p.inline_amount(attrs,display),D(node.text))

    def test_independent_displayed_cfo_signs_and_no_computed_residual(self):
        for r,count in zip(self.rows,[14,14,13,13,13]):
            cf=r['cfo_reconciliation'];self.assertEqual(len(cf['terms']),count)
            self.assertEqual(sum((D(t['contribution_usd']) for t in cf['terms']),D(0)),D(r['facts']['NetCashProvidedByUsedInOperatingActivities']['value']))
            self.assertFalse(cf['residual_used']);self.assertEqual(len(r['movement_rows']),7)
            display=next(x for x in r['passages'] if x['marker']=='independently_displayed_cfo')['exact_excerpt']
            self.assertIn('Net cash provided by operating activities',display)
            for t in r['movement_rows']:
                self.assertTrue(t['already_in_reported_cfo']);self.assertTrue(t['not_book_delta_nwc'])
                self.assertEqual(t['multiplier'],-1 if t['fact'] in ('IncreaseDecreaseInAccountsReceivable','IncreaseDecreaseInOtherOperatingAssets') else 1)

    def test_da_scope_and_sbc_precision_proposals_not_active(self):
        self.assertEqual([D(r['proposed_da_proxy']['value_usd'])/1000000 for r in self.rows],[11555,15287,11946,15311,21136])
        for r in self.rows:
            proxy=r['proposed_da_proxy'];self.assertFalse(proxy['accepted']);self.assertIsNone(proxy['complete_expense_da']);self.assertIsNone(proxy['finance_amortization_inclusion_assumption'])
            self.assertFalse(proxy['additional_rou_addback']);self.assertEqual(r['facts']['AllocatedShareBasedCompensationExpense']['precision'],'-8')
            self.assertEqual(r['facts']['ShareBasedCompensation']['precision'],'-6')
        for r in self.rows[:2]:self.assertIn('Impairment',r['facts'][r['da_proxy_source']]['concept'])
        self.assertEqual([D(r['facts']['ShareBasedCompensation']['value'])/1000000 for r in self.rows],[15376,19362,22460,22785,24953])

    def test_debt_population_change_zero_observation_and_unresolved_lease_partition(self):
        self.assertEqual([next(D(x['value'])/1000000 for x in r['calculations'] if x['input_id']=='named_financing') for r in self.rows],[14930,14999,14616,15859,51043])
        for r in self.rows[:3]:
            c=next(x for x in r['calculations'] if x['input_id']=='named_financing')
            self.assertEqual(c['operands'],['debt_before_costs','debt_discount_signed','cp'])
            self.assertNotIn('finance_total',c['operands']);self.assertIn('future',r['source_scope_overrides']['term_face'].lower())
        self.assertNotIn('term_current',self.rows[1]['facts'])
        for i in [0,1,2,4]:
            cp=self.rows[i]['facts']['cp'];self.assertEqual(cp['value'],'0');self.assertTrue(cp['source_reported_zero'])
        discrepancy=next(c for c in self.rows[-1]['partition_checks'] if c['check_id']=='operating_lease')
        self.assertEqual(discrepancy['difference_usd'],'1000000');self.assertEqual(discrepancy['status'],'SOURCE_DIFFERENCE_UNRESOLVED');self.assertTrue(discrepancy['not_an_adjustment'])

    def test_claim_overlap_and_separately_dated_classes(self):
        self.assertNotIn('redeemable_nci',self.rows[0]['facts'])
        self.assertEqual([D(r['facts']['nci_vie']['value'])/1000000 for r in self.rows],[4300,3800,3400,4200,3400])
        for r in self.rows:self.assertEqual(r['facts']['preferred_value']['value'],'0');self.assertIsNone(r['supporting_unknowns']['pension_funded_status'])
        for r,cover in zip(self.rows,['2022-01-25','2023-01-26','2024-01-23','2025-01-28','2026-01-28']):
            for letter in 'abc':
                self.assertEqual(r['facts']['year_end_'+letter]['as_of'],r['identity']['annual_end'])
                self.assertEqual(r['facts']['cover_'+letter+'_'+cover]['as_of'],cover)
                self.assertTrue(r['facts']['year_end_'+letter]['occurrences'][0]['dimensions'])
        self.assertEqual(self.rows[0]['facts']['year_end_a']['value'],'300737000');self.assertEqual(self.rows[1]['facts']['year_end_a']['value'],'5964000000')

    def test_one_inactive_approval_table_no_new_evidence_or_inferred_nulls(self):
        table=self.review['consolidated_proposals'];self.assertEqual([r['decision_id'] for r in table],[f'G{i}' for i in range(1,10)])
        self.assertTrue(all(r['approval_required'] and not r['accepted'] for r in table[:8]));self.assertFalse(table[-1]['approval_required'])
        self.assertEqual(self.review['evidence_acquisition_requirements'],[]);self.assertEqual(self.review['new_sec_requests'],0)
        for r in self.rows:self.assertTrue(all(v is None for v in r['supporting_unknowns'].values()))
        self.assertFalse(self.review['analyst_complete']);self.assertFalse(self.review['phase1_closed'])

    def test_original_payload_peer_views_restart_and_revision_guard(self):
        prior=json.loads(subprocess.check_output(['git','show','685bd4c:'+p.OUTPUT],cwd=ROOT))
        parent={k:v for k,v in self.result.items() if k!='googl_history_review'}
        self.assertTrue(parent==prior,'Original Alphabet facts/approval changed')
        self.assertTrue(json.loads((ROOT/p.OUTPUT).read_text())==self.result,'Exact replay differs')
        self.assertTrue(p.review_company_history(json.loads(json.dumps(parent,sort_keys=True)))==self.result,'Restart differs')
        changed=copy.deepcopy(parent);changed['facts']['revenue']['value']='1'
        with self.assertRaisesRegex(ValueError,'Changed original Alphabet'):p.review_company_history(changed)
        for name in ['msft','aapl']:
            path='docs/company-data-preparation/'+name+'-analyst-input-package.json'
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show','685bd4c:'+path],cwd=ROOT))
        with patch.object(p.hashlib,'sha256',return_value=type('BadDigest',(),{'hexdigest':lambda self:'0'*64})()):
            with self.assertRaises(ValueError):p.review_company_history(parent)


if __name__=='__main__':unittest.main()
