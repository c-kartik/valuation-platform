"""Source-supported adjustments, explicit comparative overlays and no false cash allocations."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from valuation_platform.review.fcff_adjustments import tax_schedule, partition, named_investment
from valuation_platform.review.operating_fcff import amount
from valuation_platform.valuation.consumer import ANCHORS

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import reconcile_historical_fcff_adjustments as review


def rational(point):
    f=point['exact_fraction_usd'];return Fraction(int(f['numerator']),int(f['denominator']))


class ScheduleArithmeticTests(unittest.TestCase):
    def test_tax_current_deferred_cash_and_missing_cfo_line_are_distinct(self):
        t=tax_schedule('20',['21','2'],['-3'],'40')
        self.assertEqual(rational(t['current_provision']),23)
        self.assertEqual(rational(t['current_provision_minus_cash_paid']),-17)
        self.assertEqual(rational(t['provision_minus_cash_paid']),-20)
        self.assertIsNone(t['cfo_deferred_minus_note_deferred'])
        self.assertIsNone(t['unlevered_operating_cash_tax'])
        self.assertFalse(t['timing_difference_is_working_capital_adjustment'])
        self.assertEqual(rational(tax_schedule('20',['23'],['-3'],'40','-2')['cfo_deferred_minus_note_deferred']),1)
        for args in [('21',['23'],['-3'],'40'),('20',[],['-3'],'40'),('20',['23'],['-3'],'-1'),('20',['23'],[None],'40')]:
            with self.subTest(args=args),self.assertRaises(ValueError):tax_schedule(*args)

    def test_parent_controls_and_missing_finance_never_zero_filled(self):
        self.assertEqual(partition('10',['7','3'])['difference_usd'],'0')
        with self.assertRaises(ValueError):partition('10',['7','2'])
        with self.assertRaises(ValueError):partition('10',[])
        missing=named_investment('10',None)
        self.assertIsNone(missing['cash_ppe_plus_disclosed_finance_additions'])
        self.assertFalse(missing['finance_additions_missing_is_zero'])
        self.assertEqual(rational(named_investment('10','0')['cash_ppe_plus_disclosed_finance_additions']),10)
        self.assertEqual(rational(named_investment('10','2')['cash_ppe_plus_disclosed_finance_additions']),12)
        self.assertFalse(named_investment('10','2')['finance_principal_deducted'])
        with self.assertRaises(ValueError):named_investment('10','-1')


class SourceScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=review.build()

    def test_fifteen_tax_controls_independent_known_note_and_cash_values(self):
        self.assertEqual((self.data['tax_bridges_verified'],self.data['closing_liability_partitions_verified'],self.data['named_cash_plus_finance_investment_subtotals']),(15,14,9))
        current={'GOOGL':[12818,19554,19651,24953,18406], 'AAPL':[19301,18405,19765,32780,22058], 'META':[7305,8896,8199,13040,6719]}
        deferred={'GOOGL':[1883,-8198,-7729,-5256,8250], 'AAPL':[-4774,895,-3024,-3031,-1339], 'META':[609,-3277,131,-4737,18755]}
        cash={'GOOGL':[13412,18892,19164,27353,21526], 'AAPL':[25385,19573,18679,26102,43369], 'META':[8525,6407,6607,10554,7578]}
        for c in self.data['companies']:
            for i,p in enumerate(c['periods']):
                t=p['taxes']; inputs=t['inputs']
                cval=sum((amount(x['value']) for x in inputs['current_components']),Fraction())
                dval=sum((amount(x['value']) for x in inputs['deferred_components']),Fraction())
                self.assertEqual(cval,current[c['ticker']][i]*1000000)
                self.assertEqual(dval,deferred[c['ticker']][i]*1000000)
                self.assertEqual(amount(inputs['cash_paid']['value']),cash[c['ticker']][i]*1000000)
                self.assertEqual(cval+dval,amount(inputs['total_provision']['value']))
                self.assertIsNone(t['unlevered_operating_cash_tax'])
                self.assertIsNone(p['verified_operating_fcff'])
        meta=self.data['companies'][2]['periods']
        self.assertEqual([p['taxes']['cfo_deferred_minus_note_deferred']['amount_usd'] for p in meta],['0','-9000000','0','-1000000','-17000000'])
        for p in self.data['companies'][1]['periods'][2:]:self.assertIsNone(p['taxes']['inputs']['separate_cfo_deferred'])

    def test_more_precise_alphabet_cash_tax_comparative_preserves_original(self):
        t=self.data['companies'][0]['periods'][3]['taxes'];s=t['cash_tax_selection']
        self.assertEqual(s['original']['value'],'27400000000')
        self.assertEqual(s['original']['precision'],'-8')
        self.assertEqual(s['selected']['value'],'27353000000')
        self.assertEqual(s['selected']['precision'],'-6')
        self.assertEqual(s['selected']['source_identity']['annual_end'],'2025-12-31')
        self.assertEqual(s['selected']['target_identity']['annual_end'],'2024-12-31')
        self.assertNotEqual(s['selected']['source_identity']['accession'],s['original']['source_identity']['accession'])

    def test_liability_children_controls_roles_and_new_comparative_disclosures(self):
        for c in self.data['companies']:
            for p in c['periods']:
                n=p['working_capital']['liability_note_partition']
                if n:
                    self.assertEqual(sum((amount(x['value']) for x in n['children']),Fraction()),amount(n['parent']['value']))
                    self.assertFalse(n['control']['cash_movement_inferred'])
                    self.assertFalse(n['control']['residual_used'])
                self.assertIsNone(p['working_capital']['verified_operating_cash_working_capital'])
                for d in p['working_capital']['adjacent_book_changes_support_only']:
                    self.assertFalse(d['is_cash_movement']);self.assertFalse(d['cash_adjustment_applied'])
        apple=self.data['companies'][1]['periods'];googl=self.data['companies'][0]['periods']
        self.assertIsNone(apple[0]['working_capital']['liability_note_partition'])
        for p,concept,expected,source_year in [(apple[1],'AccruedIncomeTaxesCurrent',6552,'2023'),(apple[3],'AccruedDistributionAndMarketingCurrent',7679,'2025'),(googl[1],'AccruedIncomeTaxesCurrent',1632,'2023')]:
            n=p['working_capital']['liability_note_partition'];point=next(x for x in n['children'] if x['concept']==concept)
            self.assertEqual(amount(point['value']),expected*1000000)
            self.assertTrue(point['source_identity']['annual_end'].startswith(source_year))
            self.assertEqual(point['target_identity'],p['identity'])
            self.assertEqual(amount(p['working_capital']['comparative_selection']['original_parent']['value']),amount(n['parent']['value']))
        taxchange=next(x for x in apple[4]['working_capital']['adjacent_book_changes_support_only'] if x['concept']=='AccruedIncomeTaxesCurrent')
        self.assertEqual(rational(taxchange['book_change']),-13585000000)
        meta_tax=next(x for x in self.data['companies'][2]['periods'][4]['working_capital']['liability_note_partition']['children'] if x['concept']=='TaxesPayableCurrent')
        self.assertEqual(meta_tax['analyst_classification'],'MIXED_TAXES_NOT_ALL_INCOME_TAX')

    def test_discrete_tax_items_keep_event_dates_and_do_not_change_actual_cash(self):
        apple=self.data['companies'][1]['periods'];meta=self.data['companies'][2]['periods'][4]
        for p,charge,after in [(apple[3],10246,19503),(apple[4],-486,21205),(meta,15930,9544)]:
            r=p['taxes']['discrete_item_review']
            self.assertEqual(amount(r['reported_item']['value']),charge*1000000)
            self.assertEqual(rational(r['tax_provision_excluding_only_this_item']),after*1000000)
            self.assertFalse(r['historical_cash_flow_adjustment_applied']);self.assertFalse(r['future_operating_tax_rate_approved'])
        charge=meta['taxes']['discrete_item_review']['reported_item']
        self.assertEqual(charge['target_identity']['annual_start'],'2025-07-01')
        self.assertEqual(charge['target_identity']['annual_end'],'2025-09-30')
        self.assertEqual(charge['precision'],'-7')
        allowance=meta['taxes']['discrete_item_review']['identified_non_cash_valuation_allowance_charge']
        self.assertEqual(amount(allowance['value']),14030000000)
        self.assertEqual(allowance['as_of'],'2025-12-31')
        self.assertEqual(meta['taxes']['cash_paid']['amount_usd'],'7578000000')
        self.assertEqual(apple[4]['taxes']['cash_paid']['amount_usd'],'43369000000')

    def test_investment_nine_named_subtotals_and_six_unresolved_splits(self):
        expected={'GOOGL':[None,32062,32815,52848,93053], 'META':[18727,31654,27854,37437,70304], 'AAPL':[None]*5}
        for c in self.data['companies']:
            for i,p in enumerate(c['periods']):
                inv=p['investment'];n=expected[c['ticker']][i]
                if n is None:self.assertIsNone(inv['cash_ppe_plus_disclosed_finance_additions'])
                else:self.assertEqual(rational(inv['cash_ppe_plus_disclosed_finance_additions']),n*1000000)
                self.assertFalse(inv['finance_principal_deducted'])
                self.assertIsNone(inv['complete_model_aligned_operating_investment'])
                self.assertIsNone(p['noncash_costs_and_sbc']['complete_income_recognized_da'])
        for p in self.data['companies'][1]['periods']:
            self.assertIsNotNone(p['investment']['inputs']['combined_operating_and_finance_additions'])
        for p in self.data['companies'][0]['periods'][1:3]:
            f=p['investment']['inputs']['finance_asset_additions']
            self.assertEqual(f['source_identity']['annual_end'],'2024-12-31')
            self.assertEqual(f['target_identity'],p['identity'])

    def test_exact_fact_contexts_source_metadata_and_missing_inventory(self):
        def visit(value):
            if isinstance(value,dict):
                if value.get('evidence_depth')=='exact_primary_inline_and_instance_verified':yield value
                for child in value.values():yield from visit(child)
            elif isinstance(value,list):
                for child in value:yield from visit(child)
        for point in visit(self.data):
            self.assertEqual(len(point['sources']),2)
            for s in point['sources']:
                self.assertEqual(len(s['sha256']),64);self.assertEqual(s['http_status'],200)
            for o in point['occurrences']:
                self.assertEqual(amount(o['raw_value']),amount(point['value']))
                self.assertTrue(o['primary_locator'])
        spec=ANCHORS['aapl-fy2025'];package=json.loads((ROOT/spec['package']).read_text());row=package['aapl_history_review']['periods'][4]
        f=review.RetainedFiling(ROOT,row,{})
        self.assertIsNone(review.exact(f,row['identity'],'RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability',optional=True))
        with self.assertRaises(ValueError):review.exact(f,row['identity'],'RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability')
        bad=deepcopy(self.data['companies'][1]['periods'][4]['working_capital']['liability_note_partition'])
        bad['children'][0]['value']='0'
        with self.assertRaises(ValueError):partition(bad['parent']['value'],[x['value'] for x in bad['children']])

    def test_source_and_prior_artifact_preservation_estimate_isolation_and_replay(self):
        names=[ANCHORS[k]['package'] for k in review.KINDS]+['docs/company-data-preparation/historical-fcff-operating-test.json','docs/company-data-preparation/historical-fcff-filing-calculations.json','src/valuation_platform/review/history.py']
        before={n:(ROOT/n).read_bytes() for n in names}
        with patch('valuation_platform.review.historical_fcff._estimates',side_effect=AssertionError('No estimates permitted')):
            self.assertEqual(review.build(),self.data)
        for n in names:self.assertEqual((ROOT/n).read_bytes(),before[n])
        for c in self.data['companies']:
            self.assertEqual(hashlib.sha256((ROOT/c['package']).read_bytes()).hexdigest(),c['package_sha256'])
        for name,text in review.outputs(self.data).items():self.assertEqual((ROOT/name).read_bytes(),text.encode())
        self.assertFalse(self.data['live_integration']);self.assertFalse(self.data['complete_operating_fcff_publication_authorized'])


if __name__=='__main__':unittest.main()
