"""Literal retained statement points; new interpretations never become approvals."""
import copy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_aapl_analyst_package as p


class ApplePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=p.build();cls.filing=p.AppleFiling()

    def test_exact_offline_replay_and_only_selected_period(self):
        self.assertTrue(self.result==json.loads((ROOT/p.OUTPUT).read_text()),'Package replay differs')
        self.assertEqual(self.result['identity'],dict(cik=320193,accession='0000320193-25-000079',form='10-K',
            annual_start='2024-09-29',annual_end='2025-09-27'))
        self.assertEqual(len(self.result['approval_sheet']),6)
        self.assertTrue(all(d['status']==p.PROPOSED and not d['accepted'] for d in self.result['approval_sheet']))
        self.assertEqual(self.result['financial_sufficiency'],'NOT_ASSESSED')
        self.assertFalse(self.result['valuation_consumption_approved'])
        self.assertEqual(self.result['new_sec_requests'],0)

    def test_independent_statement_amounts_and_all_confirmations(self):
        wanted=dict(revenue=(416161,[285,599,1210,1302]),ebit=(133050,[309,1233]),
            distribution=(8919,[880]),cash=(35934,[366,725]),current_securities=(18763,[368,726]),
            long_securities=(77723,[380,727]),term_parent=(90678,[1129]),depreciation_expense=(8000,[866]))
        for key,(value,ordinals) in wanted.items():
            fact=self.result['facts'][key]
            self.assertEqual(Decimal(fact['value'])/1000000,value)
            self.assertEqual([o['ordinal'] for o in fact['occurrences']],ordinals)
            for ordinal in ordinals:
                node=self.filing.root[ordinal];attrs,text=self.filing.inline.facts[node.get('id')]
                self.assertEqual(Decimal(node.text),p.inline_amount(attrs,text))
                self.assertEqual(attrs['contextref'],node.get('contextRef'))

    def test_operating_capital_known_omission_and_unknown_corrections(self):
        entries={e['input_id']:e for e in self.result['inputs']}
        for key,value in [('original_partial',-240),('proposed_distribution_expanded',-9159),('alternative_without_vendor',-42339)]:
            self.assertEqual(Decimal(entries[key]['value'])/1000000,value)
            self.assertEqual(entries[key]['completeness'],'partial')
            self.assertEqual(len(entries[key]['operands']),len(set(entries[key]['operands'])))
        proposed=entries['proposed_distribution_expanded']
        self.assertEqual(proposed['status'],p.PROPOSED)
        self.assertNotIn('other_current_liabilities',proposed['operands'])
        self.assertNotIn('other_current_residual',proposed['operands'])
        unknown={v['input_id']:v for v in self.result['unresolved_requirements']}
        for key in ('employee_accrual','capital_creditors','cash_interest','expense_basis_da'):
            self.assertIsNone(unknown[key]['value']);self.assertTrue(unknown[key]['reason'])
        self.assertIsNone(self.result['adjacent_book_movement'])
        self.assertFalse(self.result['estimates']);self.assertFalse(self.result['manual_inputs'])

    def test_da_sbc_roles_and_no_finance_amortization_assumption(self):
        e={v['input_id']:v for v in self.result['inputs']}
        self.assertEqual(e['reported:DepreciationDepletionAndAmortization']['value'],'11698000000')
        self.assertEqual(e['depreciation_expense']['precision']['operand_decimals'],['-8'])
        self.assertEqual(e['depreciation_expense']['role'],'expense_support_not_complete_da')
        self.assertNotIn('expense_da',e)
        self.assertNotEqual(e['reported:ShareBasedCompensation']['role'],e['reported:AllocatedShareBasedCompensationExpense']['role'])
        self.assertEqual(e['reported:AllocatedShareBasedCompensationExpense']['status'],p.ACCEPTED)
        self.assertEqual(e['reported:OperatingLeasePayments']['precision']['operand_decimals'],['-8'])

    def test_debt_lease_and_financial_scopes(self):
        e={v['input_id']:v for v in self.result['inputs']}
        for key,value in [('current_financial',54697),('all_financial',132420),('principal_bridge',90678),
            ('named_borrowing',98657),('proposed_financing',99887),('alternative_all_leases',112377)]:
            self.assertEqual(Decimal(e[key]['value'])/1000000,value)
        self.assertEqual(e['proposed_financing']['status'],p.PROPOSED)
        self.assertNotIn('op_total',e['proposed_financing']['operands'])
        self.assertEqual(self.result['facts']['finance_total']['value'],'1230000000')
        self.assertEqual(self.result['facts']['purchase_commitments']['value'],'13308000000')
        self.assertEqual(self.result['facts']['uncommenced_lease']['value'],'523000000')
        self.assertNotIn('purchase_commitments',e['proposed_financing']['operands'])
        self.assertNotIn('uncommenced_lease',e['proposed_financing']['operands'])
        self.assertEqual(self.result['facts']['debt_fair']['precision'],'-8')
        self.assertEqual(self.result['facts']['debt_fair']['occurrences'][0]['dimensions'],
            [['us-gaap:FairValueByFairValueHierarchyLevelAxis','us-gaap:FairValueInputsLevel2Member']])

    def test_tax_arithmetic_and_cash_roles(self):
        e={v['input_id']:v for v in self.result['inputs']}
        self.assertEqual(e['reported:IncomeTaxesPaidNet']['value'],'-43369000000')
        self.assertEqual(e['deferred_provision']['value'],'-1339000000')
        self.assertEqual(e['reported_etr']['policy'],'annual_reported_effective_tax_rate_v1')
        self.assertEqual(e['reported_etr']['value'],'0.1561000233558604374326635475291760')
        candidates=self.result['tax_uncertainty_candidates']
        self.assertEqual([(v['raw_value'],v['precision']) for v in candidates],[('23200000000','-8'),('23242000000','-6')])
        self.assertNotEqual(e['reported:OtherNoncashIncomeExpense']['value'],e['deferred_provision']['value'])

    def test_shares_dates_classes_and_precision(self):
        facts=self.result['facts']
        for key,value,end,precision in [('year_end_common','14773260000','2025-09-27','-3'),
            ('cover_common','14776353000','2025-10-17','-3'),('rsu','151574000','2025-09-27','-3'),
            ('future_sbc','21800000000','2025-09-27','-8')]:
            self.assertEqual((facts[key]['value'],facts[key]['as_of'],facts[key]['precision']),(value,end,precision))
        self.assertEqual(facts['rsu']['occurrences'][0]['dimensions'],
            [['us-gaap:AwardTypeAxis','us-gaap:RestrictedStockUnitsRSUMember']])

    def test_changed_raw_unit_precision_or_nil_cannot_populate(self):
        for attribute,value in [('unitRef','shares'),('decimals','-8'),('text','8918000000'),
            ('{http://www.w3.org/2001/XMLSchema-instance}nil','true')]:
            f=copy.copy(self.filing);f.root=copy.deepcopy(f.root);f.facts={}
            if attribute=='text':f.root[880].text=value
            else:f.root[880].set(attribute,value)
            with self.assertRaises(ValueError):
                f.fact('distribution','AccruedDistributionAndMarketingCurrent','Note6',namespace='aapl',instant=True)
        with self.assertRaisesRegex(ValueError,'absent'):
            self.filing.fact('wrong_duration','AccruedDistributionAndMarketingCurrent','Note6',namespace='aapl',instant=False)
        with self.assertRaisesRegex(ValueError,'absent'):
            self.filing.fact('wrong_share_date','EntityCommonStockSharesOutstanding','Cover',namespace='dei',unit='shares',instant=True,as_of='2025-09-27')

    def test_sources_receipts_passages_and_validation_checks(self):
        self.assertEqual(len(self.result['sources']),2)
        self.assertEqual([s['sha256'] for s in self.result['sources']],
            ['b0dbcbbd800fd1c819007d63d884a1f8b9a5994486d0b2974a4b5b8a6e6eb80e','e1076735f1c81bc96d5c1ff6e1a9d23515d6eacf52b405cb1f7da3e379ac533b'])
        self.assertTrue(all(s['digest_type']=='sha256_sec_response_body_bytes' and s['http_status']==200 for s in self.result['sources']))
        self.assertTrue(all(v['exact_excerpt'] in self.filing.text for v in self.result['scope_passages']))
        self.assertEqual(len(self.result['checks']),12)
        self.assertTrue(all(v['result']=='PASS' and v['difference']=='0' for v in self.result['checks']))
        self.assertEqual(next(c for c in self.result['checks'] if c['check_id']=='displayed_cfo')['observed'],'111482000000')

    def test_conflicting_eligible_population_is_not_silently_selected(self):
        f=copy.copy(self.filing);f.root=copy.deepcopy(f.root);f.inline=copy.deepcopy(f.inline);f.facts={}
        duplicate=copy.deepcopy(f.root[880]);duplicate.set('id','synthetic-conflict');duplicate.text='8918000000'
        f.root.append(duplicate)
        attrs,text=f.inline.facts['f-679'];attrs=dict(attrs,id='synthetic-conflict')
        f.inline.facts['synthetic-conflict']=(attrs,'8,918')
        with self.assertRaisesRegex(ValueError,'Competing eligible values'):
            f.fact('distribution','AccruedDistributionAndMarketingCurrent','Note6',namespace='aapl',instant=True)

    def test_wrong_instant_or_dimension_remains_absent_not_zero(self):
        for mode in ('date','dimension'):
            f=copy.copy(self.filing);f.contexts=copy.deepcopy(f.contexts);f.facts={}
            context=f.contexts['c-20']
            if mode=='date':context.find('.//'+p.cash._XI+'instant').text='2025-09-26'
            else:
                member=p.cash.ET.SubElement(context,'{http://xbrl.org/2006/xbrldi}explicitMember',dimension='us-gaap:AwardTypeAxis')
                member.text='us-gaap:RestrictedStockUnitsRSUMember'
            with self.assertRaisesRegex(ValueError,'absent'):
                f.fact('distribution','AccruedDistributionAndMarketingCurrent','Note6',namespace='aapl',instant=True)
            self.assertNotIn('distribution',f.facts)

    def test_serialization_and_all_prior_json_runtime_and_msft_helper_preserved(self):
        text=json.dumps(self.result,sort_keys=True,indent=2)+'\n'
        self.assertEqual(json.dumps(json.loads(text),sort_keys=True,indent=2)+'\n',text)
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',p.BASELINE],cwd=ROOT,text=True).splitlines()
        for path in paths:
            if not (path.startswith('src/') or path.endswith('.json') or path=='scripts/prepare_msft_analyst_package.py'):continue
            prior=subprocess.check_output(['git','show',p.BASELINE+':'+path],cwd=ROOT)
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),hashlib.sha256(prior).hexdigest(),path)


if __name__=='__main__':unittest.main()
