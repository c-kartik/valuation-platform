"""Reviewed classification, source containment and numeric adoption regressions."""
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import resolve_meta_alphabet_cashflows as resolution
from valuation_platform.review import resolved_history as live
from valuation_platform.review.cfo_history import adopted_window as original


class MetaAlphabetResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta=resolution.build_company('META');cls.google=resolution.build_company('GOOGL')
        cls.mapping=json.loads((ROOT/resolution.BASE/'META/source-map.json').read_text())
        spec=resolution.ANCHORS['meta-fy2025'];rows=json.loads((ROOT/spec['package']).read_text())['periods']
        cls.row=rows[0];cls.filing=resolution.RetainedFiling(ROOT,cls.row,{})

    def test_meta_net_investment_and_provisional_fcfe_independent_numbers(self):
        cfo=[57683,50475,71113,91328,115800];netppe=[18567,31186,27045,37256,69691]
        funding=[-663,9071,7397,8463,27382];expected=[38453,28360,51465,62535,73491]
        for i,p in enumerate(self.meta['periods']):
            self.assertEqual((cfo[i]-netppe[i]+funding[i])*1000000,Fraction(p['fcfe']['amount_usd']))
            self.assertEqual(Fraction(p['fcfe']['amount_usd']),expected[i]*1000000)
            self.assertEqual(Fraction(p['net_cash_investment']['amount_usd']),netppe[i]*1000000)
            self.assertFalse(p['fcfe']['publishable_as_parent_common']);self.assertFalse(p['fcfe']['omitted_other_assumed_zero'])
            self.assertEqual(p['financing']['unallocated_other_usd'],[str([-13,344,-111,-277,2220][i]*1000000)])

    def test_actual_catalog_overlay_exact_increases_and_original_ledger_preserved(self):
        before=original(ROOT,'meta-fy2025');after=live.adopted_window(ROOT,'meta-fy2025')
        self.assertEqual([Fraction(a['fcff'])-Fraction(b['fcff']) for a,b in zip(after,before)],list(map(Fraction,[0,245000000,221000000,0,0])))
        self.assertTrue(all(a['fcff_basis']==live.BASIS for a in after))
        self.assertEqual(original(ROOT,'meta-fy2025'),before)
        for kind in ('aapl-fy2025','googl-fy2025'):self.assertEqual(live.adopted_window(ROOT,kind),original(ROOT,kind))

    def test_vintage_receipts_and_overdraft_are_not_double_counted(self):
        for c in self.meta['controls']['investment_comparatives']:self.assertEqual(c['original_comparative_difference_usd'],'0')
        b=self.meta['controls']['overdraft_bridge']
        self.assertEqual(sorted(int(c['signed_cash_usd']) for c in b['original']),[-13000000,14000000])
        self.assertEqual(b['later']['signed_cash_usd'],'1000000');self.assertEqual(b['fcfe_change_usd'],'0')

    def test_google_nci_is_not_debt_or_automatically_parent_equity(self):
        expected=[65776,58814,68735,73652,105403]
        for i,p in enumerate(self.google['periods']):
            self.assertEqual(Fraction(p['fcfe']['amount_usd']),expected[i]*1000000)
            self.assertEqual(p['fcfe']['status'],'CONSOLIDATED_BEFORE_NCI_ATTRIBUTION')
            self.assertIsNone(p['parent_common_fcfe_usd']);self.assertEqual(p['platform_change_usd'],'0')
            self.assertEqual(Fraction(p['financing']['nci_contributions_excluded_from_debt']['amount_usd']),[310,35,8,1154,400][i]*1000000)
        self.assertIsNone(self.google['controls']['nci_fair_value_usd'])
        self.assertFalse(self.google['controls']['nci_book_value_used_as_fair_value'])

    def test_google_lease_parent_once_and_no_prepayment_principal_estimate(self):
        leases=self.google['controls']['lease_cash_containment']
        self.assertEqual([x['component']['raw_value_usd'] for x in leases],['586000000','705000000','405000000','1988000000'])
        self.assertTrue(all(x['additional_deduction_usd']=='0' for x in leases))
        self.assertTrue(any('prepayments' in x['excerpt'].lower() for x in self.google['controls']['lease_narrative']))

    def test_financing_omissions_duplicates_and_equity_reclassification_fail(self):
        maps=self.mapping['periods'][0]['financing_rows']
        for rows in (maps+maps[:1],maps[:-2]+maps[-1:]):
            with self.assertRaises(ValueError):resolution.financing(self.filing,self.row['identity'],rows)
        changed=deepcopy(maps);changed[0]['classification']='DEBT_FUNDING_OR_PRINCIPAL';changed[0]['included_in_net_borrowing']=True
        with self.assertRaises(ValueError):resolution.financing(self.filing,self.row['identity'],changed)

    def test_retained_meta_later_interest_and_reported_tax_preserved(self):
        for i,value in enumerate(['23000000','185000000']):
            p=self.meta['periods'][i];self.assertEqual(p['inputs']['interest_expense'],value)
            self.assertTrue(any('000132680124000012' in s for s in p['source_urls']))
        p=self.meta['periods'][-1];self.assertEqual(p['inputs']['tax_provision'],'25474000000')
        self.assertTrue(all(not p['forecast_inputs_changed'] for p in self.meta['periods']))

    def test_overlay_tamper_or_period_and_arithmetic_change_rejected(self):
        from valuation_platform.valuation.consumer import ANCHORS
        from valuation_platform.review.cfo_history import LEDGER
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in (ANCHORS['meta-fy2025']['package'],LEDGER,live.OVERLAY):
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((ROOT/name).read_bytes())
            path=root/live.OVERLAY;payload=path.read_bytes();path.write_bytes(payload+b' ')
            with self.assertRaisesRegex(ValueError,'reviewed pin'):live.adopted_window(root,'meta-fy2025')
            for field,value in [('net_cash_ppe_usd','1'),('fcff_usd','0')]:
                data=json.loads(payload);data['periods'][1][field]=value;body=json.dumps(data).encode();path.write_bytes(body)
                with patch.object(live,'OVERLAY_SHA256',hashlib.sha256(body).hexdigest()),self.assertRaises(ValueError):live.adopted_window(root,'meta-fy2025')

    def test_results_source_pins_csv_and_overlay_reproduce(self):
        for ticker,data in [('META',self.meta),('GOOGL',self.google)]:
            for path,value in resolution.outputs(ticker,data).items():self.assertEqual((ROOT/path).read_text(),value)
            for path,digest in data['inputs_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)

    def test_private_bundle_catalog_runs_without_source_checkout_imports(self):
        from valuation_platform.api.bundle import build_bundle,remove_bundle
        with tempfile.TemporaryDirectory() as d:
            bundle=Path(d)/'private';build_bundle(ROOT,bundle)
            try:
                code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'src'));from valuation_platform.api.catalog import build_catalog;print(len(build_catalog(Path(sys.argv[1]))))"
                completed=subprocess.run([sys.executable,'-I','-c',code,str(bundle)],cwd=d,capture_output=True,text=True,check=True)
                self.assertEqual(int(completed.stdout.strip()),81564)
            finally:remove_bundle(bundle)

    def test_meta_research_hashes_and_exact_excerpts(self):
        path=ROOT/'docs/company-resolutions/META/research/verify_sources.py';spec=importlib.util.spec_from_file_location('verify_meta_research',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertEqual(module.verify(),{'source_hashes_verified':15,'exact_excerpts_verified':18})

if __name__=='__main__':unittest.main()
