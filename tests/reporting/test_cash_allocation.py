"""Additive cash-allocation consumer: financial gates and reproducibility."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('cash_preparation',ROOT/'scripts/prepare_cash_allocation.py')
cash=importlib.util.module_from_spec(spec);spec.loader.exec_module(cash)

class CashAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package=cash.prepare()

    def test_deterministic_offline_package_matches_committed_source(self):
        self.assertEqual(self.package,json.loads((ROOT/'frontend/public/cash-allocation/GOOGL.json').read_text()))
        self.assertEqual(cash.prepare(),self.package)
        self.assertEqual([len(self.package[k]) for k in ['annual','quarterly','ttm','ppe']],[5,20,17,2])

    def test_every_period_reconciles_without_missing_caption_zeros(self):
        for r in list(self.package['reported_periods'].values())+self.package['annual']+self.package['quarterly']+self.package['ttm']:
            cash.reconcile(r)
        annual=self.package['annual']
        self.assertIsNone(annual[0]['values']['dividends'])
        self.assertIsNone(annual[0]['evidence']['dividends'])
        self.assertEqual(annual[-1]['values']['ppe'],-91447000000)
        self.assertEqual(annual[-1]['values']['cfo'],164713000000)
        self.assertTrue(any(sum(r['values'][k] for k in ['cfo','investing','financing'])<0 for r in self.package['quarterly']))
        self.assertEqual(self.package['ttm'][0]['id'],'FY2022-Q3')

    def test_ppe_scope_and_exact_reconciliation(self):
        for r in self.package['ppe']:
            v=r['values'];self.assertEqual(v['technical']+v['office']+v['other'],v['service'])
            self.assertEqual(v['service']+v['pending']-v['depreciation'],v['net'])
            self.assertTrue(all(e['instant']==r['date'] for e in r['evidence'].values()))
        self.assertEqual(self.package['ppe'][1]['values']['net'],246597000000)

    def test_parser_rejects_ambiguous_missing_unit_wrong_entity_and_extra_dimensions(self):
        template='''<xbrl xmlns="http://www.xbrl.org/2003/instance" xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:iso4217="http://www.xbrl.org/2003/iso4217" xmlns:us-gaap="http://fasb.org/us-gaap/2025" xmlns:xbrldi="http://xbrl.org/2006/xbrldi"><context id="c"><entity><identifier scheme="SEC">1652044</identifier>{segment}</entity><period><startDate>2025-01-01</startDate><endDate>2025-12-31</endDate></period></context><unit id="u"><measure>{unit}</measure></unit><us-gaap:NetCashProvidedByUsedInOperatingActivities contextRef="c" unitRef="u">1000000</us-gaap:NetCashProvidedByUsedInOperatingActivities>{extra}</xbrl>'''
        def instance(**kwargs):
            return cash.Instance(template.format(segment=kwargs.get('segment',''),unit=kwargs.get('unit','iso4217:USD'),extra=kwargs.get('extra','')).replace('1652044',kwargs.get('entity','1652044')).encode(),'https://www.sec.gov/Archives/edgar/data/1652044/x.xml','2026-02-01')
        select=lambda ins:ins.fact('NetCashProvidedByUsedInOperatingActivities',start='2025-01-01',end='2025-12-31')
        self.assertEqual(select(instance())['value'],1000000)
        for ins in [instance(unit='xbrli:pure'),instance(entity='1'),instance(segment='<segment><xbrldi:explicitMember dimension="us-gaap:Axis">us-gaap:Member</xbrldi:explicitMember></segment>'),instance(extra='<us-gaap:NetCashProvidedByUsedInOperatingActivities contextRef="c" unitRef="u">2000000</us-gaap:NetCashProvidedByUsedInOperatingActivities>')]:
            with self.assertRaises(ValueError):select(ins)
        self.assertIsNone(instance().fact('PaymentsOfDividends',start='2025-01-01',end='2025-12-31',optional=True))

    def test_broken_subtotal_and_closing_balance_fail(self):
        for key in ['ppe','buybacks','fx','closing']:
            r=json.loads(json.dumps(self.package['annual'][-1]));r['values'][key]+=1
            with self.assertRaises(ValueError):cash.reconcile(r)

if __name__=='__main__':unittest.main()
