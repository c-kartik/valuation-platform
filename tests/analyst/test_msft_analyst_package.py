"""Independent retained MSFT statement points and draft-only package boundaries."""
import copy
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_msft_analyst_package as package


class MSFTAnalystPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filings=[package.Filing(y) for y in (2025,2026)]
        for f in cls.filings:package.populate(f)
        cls.result=package.finish(cls.filings)

    def test_exact_package_replay_and_registered_identity(self):
        self.assertEqual(self.result,json.loads((ROOT/package.OUTPUT).read_text()))
        self.assertEqual([p['identity']['accession'] for p in self.result['periods']],
            ['0000950170-25-100235','0001193125-26-323660'])
        self.assertEqual([p['identity']['annual_start'] for p in self.result['periods']],['2024-07-01','2025-07-01'])
        self.assertEqual([p['identity']['annual_end'] for p in self.result['periods']],['2025-06-30','2026-06-30'])
        self.assertFalse(self.result['valuation_consumption_approved'])
        self.assertEqual(self.result['financial_sufficiency'],'NOT_ASSESSED')
        self.assertEqual(self.result['new_sec_requests'],0)

    def test_independently_inspected_income_tax_and_investment_points(self):
        # Face income statements, Notes 6/9/11 and cash-flow statements; USD m.
        expected=[dict(revenue=281724,ebit=128528,pretax=123627,expense_da=28000,
            **{'reported:PaymentsToAcquirePropertyPlantAndEquipment':-64551,
               'reported:IncomeTaxExpenseBenefit':21795,'reported:IncomeTaxesPaidNet':-28700}),
            dict(revenue=331839,ebit=155237,pretax=165934,expense_da=39000,
            **{'reported:PaymentsToAcquirePropertyPlantAndEquipment':-115948,
               'reported:IncomeTaxExpenseBenefit':32185,'reported:IncomeTaxesPaidNet':-21188})]
        for p,wanted in zip(self.result['periods'],expected):
            entries={e['input_id']:e for e in p['inputs']}
            self.assertEqual(Decimal(p['facts']['pretax']['value'])/1000000,wanted.pop('pretax'))
            for key,value in wanted.items():self.assertEqual(Decimal(entries[key]['value'])/1000000,value)
            self.assertEqual(entries['expense_da']['precision']['operand_decimals'],['-8','-8'])
            self.assertEqual(entries['reported_etr']['policy'],'annual_reported_effective_tax_rate_v1')
            self.assertEqual(Decimal(entries['reported_etr']['value']),Decimal('0.1762964400980368366133611589701279')
                if p['fiscal_year']==2025 else Decimal('0.1939626598527125242566321549531742'))

    def test_source_supported_partial_nwc_and_book_movement_not_cash(self):
        for p,nwc,ap,whole in zip(self.result['periods'],(-28245,-21353),(20824,15716),(-35145,-48053)):
            e={v['input_id']:v for v in p['inputs']}
            self.assertEqual(Decimal(e['partial_nwc']['value'])/1000000,nwc)
            self.assertEqual(Decimal(e['adjusted_ap']['value'])/1000000,ap)
            self.assertEqual(Decimal(e['whole_ap_comparator']['value'])/1000000,whole)
            self.assertEqual(e['partial_nwc']['completeness'],'partial')
            self.assertNotIn('component_receivables',e['partial_nwc']['operands'])
            self.assertEqual(len(e['partial_nwc']['operands']),len(set(e['partial_nwc']['operands'])))
        movement=self.result['adjacent_book_movement']
        self.assertEqual(Decimal(movement['value_usd'])/1000000,6892)
        self.assertEqual(Decimal(movement['capital_creditor_exclusion_effect_usd'])/1000000,19800)
        self.assertIn('Not cash delta NWC',movement['limitations'][0])

    def test_actual_parent_populations_and_not_inferred_cp_zero(self):
        expected=[(94565,43151,22861,46172),(76843,40294,21925,66594)]
        for p,values in zip(self.result['periods'],expected):
            e={v['input_id']:v for v in p['inputs']}
            for key,value in zip(('current_liquidity','term_debt','operating_liability','finance_liability'),values):
                self.assertEqual(Decimal(e[key]['value'])/1000000,value)
            self.assertEqual(len(p['checks']),7)
            self.assertTrue(all(c['result']=='PASS' and c['difference']=='0' for c in p['checks']))
        first,second=self.result['periods']
        self.assertEqual(first['facts']['commercial_paper']['value'],'0')
        self.assertEqual(first['facts']['commercial_paper']['precision_variants'],['-6','-9'])
        self.assertNotIn('commercial_paper',second['facts'])
        self.assertTrue(any(u['input_id']=='commercial_paper' and u['value'] is None for u in second['unresolved_requirements']))

    def test_shares_dates_award_class_and_non_overlap(self):
        for p,end_common,cover,obs,awards in zip(self.result['periods'],(7434000000,7427000000),
                (7433166379,7425545491),('2025-07-24','2026-07-23'),(82000000,78000000)):
            facts=p['facts'];entries={v['input_id']:v for v in p['inputs']}
            self.assertEqual(Decimal(facts['year_end_common']['value']),end_common)
            self.assertEqual(Decimal(facts['cover_common']['value']),cover)
            self.assertEqual(facts['cover_common']['as_of'],obs)
            self.assertEqual(facts['year_end_common']['precision'],'-6')
            self.assertEqual(facts['cover_common']['precision'],'0')
            self.assertEqual(Decimal(facts['nonvested_awards']['value']),awards)
            self.assertEqual(facts['nonvested_awards']['occurrences'][0]['dimensions'],
                [['us-gaap:AwardTypeAxis','us-gaap:RestrictedStockMember']])
            self.assertEqual(entries['year_end_common']['operands'],['year_end_common'])
            self.assertEqual(entries['cover_common']['operands'],['cover_common'])
            self.assertFalse(any('diluted' in e['input_id'] for e in p['inputs']))

    def test_cfo_signs_roles_and_recast_not_an_adjustment(self):
        for p,cfo,dep,expense,sbc in zip(self.result['periods'],(136162,182935),(34153,38534),(28000,39000),(11974,12405)):
            e={v['input_id']:v for v in p['inputs']}
            self.assertEqual(Decimal(e['reported:NetCashProvidedByUsedInOperatingActivities']['value'])/1000000,cfo)
            self.assertEqual(Decimal(e['reported:DepreciationAmortizationAndOther']['value'])/1000000,dep)
            self.assertEqual(Decimal(e['expense_da']['value'])/1000000,expense)
            self.assertEqual(Decimal(e['sbc_cost_proxy']['value'])/1000000,sbc)
            self.assertEqual(e['sbc_cost_proxy']['origin'],'proxy')
            self.assertEqual(e['sbc_cost_proxy']['status'],package.ACCEPTED)
            self.assertEqual(e['reported:ShareBasedCompensation']['role'],'reported_reconciliation_item')
            self.assertEqual(e['reported:AllocatedShareBasedCompensationExpense']['role'],'noncash_expense')
            self.assertEqual(len(p['cfo_reconciliation']['terms']),14)
            self.assertFalse(any('residual' in i for i in e))
            self.assertEqual(Decimal(e['nonoperating_income']['value'])/1000000,-4901 if p['fiscal_year']==2025 else 10697)
            self.assertTrue(all(e[t]['role'] in ('reported_reconciliation_item','accrued_income') for t in p['cfo_reconciliation']['terms']))
            self.assertTrue(all(e[t]['role']=='cash_payment' for t in ('reported:OperatingLeasePayments',
                'reported:FinanceLeaseInterestPaymentOnLiability','reported:FinanceLeasePrincipalPayments')))
        comparative=self.result['comparative_support']
        self.assertEqual([(c['raw_value'],c['ordinal']) for c in comparative],[('29433000000',692),('-5329000000',698)])
        self.assertTrue(all(c['start']=='2024-07-01' and c['end']=='2025-06-30' for c in comparative))
        self.assertEqual(Decimal(self.result['separately_identified_omitted_asset_growth']['value_usd'])/1000000,19600)

    def test_receipts_and_every_value_has_exact_primary_and_instance_binding(self):
        sources={s['source_id']:s for s in self.result['sources']}
        self.assertEqual(len(sources),4)
        for p,f in zip(self.result['periods'],self.filings):
            for value in p['facts'].values():
                self.assertTrue(value['occurrences'])
                for o in value['occurrences']:
                    raw=f.root[o['ordinal']]
                    self.assertEqual(raw.attrib['id'],o['xml_id'])
                    self.assertEqual(raw.attrib['contextRef'],o['context_id'])
                    self.assertEqual(raw.text,o['raw_value'])
                for kind in ('primary','instance'):
                    source=sources[value[kind+'_source']]
                    receipt=getattr(f,kind)
                    self.assertEqual(source['sha256'],hashlib.sha256(receipt.artifact.body).hexdigest())
                    self.assertEqual(source['http_status'],200)
                    self.assertTrue(source['retrieved_at_utc'])
                    self.assertEqual(source['digest_type'],'sha256_sec_response_body_bytes')
            self.assertEqual(len(p['unresolved_requirements']),len({u['input_id'] for u in p['unresolved_requirements']}))
            self.assertTrue(all(u['value'] is None for u in p['unresolved_requirements']))

    def test_wrong_dates_units_values_nil_and_precision_cannot_populate(self):
        original=self.filings[0]
        for change in ('value','precision','nil','unit','date'):
            f=copy.copy(original);f.facts={};f.entries=[]
            f.root=copy.deepcopy(original.root);f.contexts=copy.deepcopy(original.contexts)
            node=f.root[536]  # independently inspected FY2025 revenue face occurrence
            if change=='value':node.text='1'
            elif change=='precision':node.set('decimals','-9')
            elif change=='nil':node.set('{http://www.w3.org/2001/XMLSchema-instance}nil','true')
            elif change=='unit':node.set('unitRef','U_shares')
            elif change=='date':
                # Exclude every same-date candidate; do not manufacture another period.
                for context in f.contexts.values():
                    end=context.find(package.cash._XI+'period/'+package.cash._XI+'endDate')
                    if end is not None and end.text=='2025-06-30':end.text='2025-06-29'
            with self.subTest(change=change),self.assertRaises((ValueError,KeyError)):
                f.fact('bad','RevenueFromContractWithCustomerExcludingAssessedTax','Synthetic rejection only')

    def test_no_duplicate_selected_id_or_ineligible_etr_denominator(self):
        f=copy.copy(self.filings[0]);f.entries=copy.deepcopy(f.entries);f.facts=copy.deepcopy(f.facts)
        with self.assertRaises(ValueError):f.entry('revenue','duplicate',['revenue'],scope='test',rationale='test')
        for value in ('0','-1'):
            f.facts['pretax']['value']=value
            with self.assertRaises(ValueError):
                f.entry('bad-etr','synthetic',['IncomeTaxExpenseBenefit','pretax'],formula='DIVIDE',unit='pure',scope='test',rationale='test')
        self.assertEqual(package.inline_amount({'format':'ixt-sec:numwordsen'},'no'),0)
        with self.assertRaises((ValueError,InvalidOperation)):package.inline_amount({'format':'ixt:num-dot-decimal'},'no')

    def test_one_pending_sheet_and_no_new_numeric_assumptions(self):
        self.assertEqual(len(self.result['approval_sheet']),6)
        self.assertTrue(all(d['status']==package.PROPOSED for d in self.result['approval_sheet']))
        self.assertTrue(all(e['origin'] in ('reported','derived','proxy') for p in self.result['periods'] for e in p['inputs']))
        self.assertTrue(all('value' not in d for d in self.result['approval_sheet']))
        self.assertFalse(any(u['input_id']=='sbc_economic_treatment' for p in self.result['periods'] for u in p['unresolved_requirements']))
        self.assertTrue(all(any(u['input_id']=='sbc_economic_treatment' for u in p['original_bundle_unknowns']) for p in self.result['periods']))

    def test_original_json_artifacts_and_runtime_source_are_byte_preserved(self):
        # All pre-existing JSONs and runtime source, not only numeric samples.
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',package.BASELINE],cwd=ROOT,text=True).splitlines()
        selected=[p for p in paths if p.startswith('src/') or (p.startswith('docs/') and p.endswith('.json'))]
        for path in selected:
            prior=subprocess.check_output(['git','show',package.BASELINE+':'+path],cwd=ROOT)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),hashlib.sha256(prior).hexdigest(),path)

    def test_deterministic_json_round_trip(self):
        text=json.dumps(self.result,sort_keys=True,indent=2)+'\n'
        self.assertEqual(json.dumps(json.loads(text),sort_keys=True,indent=2)+'\n',text)


if __name__=='__main__':unittest.main()
