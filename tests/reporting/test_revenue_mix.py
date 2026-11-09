"""Real retained filing coverage plus deliberate ambiguity/contradiction tests."""
import importlib.util
import json
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from valuation_platform.reporting.revenue_mix import prepare_mix, extract, RevenueMixError, REVENUE, segment

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prepare_revenue_mix', ROOT/'scripts/prepare_revenue_mix.py')
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

class RevenueMixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = {t: script.collect(t, verbose=False)[:2] for t in ('GOOGL','AAPL','META')}
        cls.packages = {t: prepare_mix(*parts) for t, parts in cls.corpus.items()}

    def test_all_quarters_reconcile_without_residual_plugs(self):
        for ticker,p in self.packages.items():
            self.assertEqual(len(p['rows']),20)
            self.assertEqual(p['validation']['quarter_total_checks'],20)
            for row in p['rows']:
                self.assertEqual(sum(row['values'][s['id']] for s in p['series']),row['total'])
                if p['detail']['series']:
                    self.assertEqual(sum(row['values'][s['id']] for s in p['detail']['series']),row['values'][p['detail']['parent']])
            for check in p['validation']['annual_category_checks']:
                self.assertEqual(check['sum_quarters'],check['reported_annual'])

    def test_offline_reproduction_matches_committed_packages(self):
        for ticker, p in self.packages.items():
            stored=json.loads((ROOT/f'frontend/public/revenue-mix/{ticker}.json').read_text())
            stored.pop('source_manifest_sha256')
            self.assertEqual(p,stored)
            self.assertEqual(p,prepare_mix(*self.corpus[ticker]))

    def test_alphabet_hedging_revenue_table_mapping_and_signed_amounts(self):
        p=self.packages['GOOGL']
        self.assertTrue(any(r['values']['hedging']<0 for r in p['rows']))
        row=next(r for r in p['rows'] if r['id']=='FY2022-Q2')
        self.assertEqual(row['evidence']['hedging']['operands'][0]['value'],653_000_000)
        self.assertEqual(row['evidence']['hedging']['operands'][0]['concept'],'GainLossOnOilAndGasHedgingActivity')
        self.assertEqual(p['rows'][-1]['values']['services'],96_302_000_000)
        self.assertEqual(p['rows'][-1]['values']['cloud'],30_709_000_000)

    def test_meta_recast_exception_and_reported_differences_remain_explicit(self):
        p=self.packages['META'];row=p['rows'][0]
        self.assertEqual(row['id'],'FY2021-Q4')
        self.assertEqual(row['evidence']['apps']['operands'][1]['accession'],'0001326801-22-000108')
        self.assertTrue(any('recast exception' in n for n in p['notes']))
        self.assertTrue(any(c['difference'] for c in p['validation']['direct_quarter_checks']))
        self.assertEqual(p['rows'][-1]['values']['advertising'],63_062_000_000)
        self.assertEqual(p['rows'][-1]['values']['other_apps'],1_096_000_000)

    def test_apple_products_and_actual_fiscal_calendar(self):
        p=self.packages['AAPL']
        self.assertEqual(p['kind'],'Products & services')
        self.assertEqual(p['rows'][-1]['end'],'2026-09-26')
        self.assertEqual(len(p['series']),5)
        self.assertEqual(p['detail']['series'],[])

    def test_missing_conflicting_extra_dimension_or_wrong_namespace_fails(self):
        report,instances=self.corpus['GOOGL'];o=report['rows'][-1]['evidence']['revenue']['operands'][0];instance=instances[o['accession']]
        dims=segment('GoogleCloudMember')
        original=extract(instance,o,[REVENUE],dims)
        matches=[f for f in instance.facts if f.context_id in original['context_ids'] and f.concept==REVENUE]
        remaining=tuple(f for f in instance.facts if f not in matches)
        with self.assertRaises(RevenueMixError):extract(replace(instance,facts=remaining),o,[REVENUE],dims)
        conflict=replace(matches[0],numeric_value=matches[0].numeric_value+Decimal(1))
        with self.assertRaises(RevenueMixError):extract(replace(instance,facts=instance.facts+(conflict,)),o,[REVENUE],dims)
        wrong=replace(matches[0],namespace='http://example.org/us-gaap/')
        with self.assertRaises(RevenueMixError):extract(replace(instance,facts=remaining+(wrong,)),o,[REVENUE],dims)
        dimension=matches[0].dimensions[0]
        wrong=replace(matches[0],dimensions=(replace(dimension,dimension=replace(dimension.dimension,namespace='http://example.org/')),))
        with self.assertRaises(RevenueMixError):extract(replace(instance,facts=remaining+(wrong,)),o,[REVENUE],dims)
        wrong=replace(matches[0],dimensions=matches[0].dimensions+(dimension,))
        with self.assertRaises(RevenueMixError):extract(replace(instance,facts=remaining+(wrong,)),o,[REVENUE],dims)

    def test_consolidated_source_contradiction_stops_publication(self):
        report,instances=self.corpus['GOOGL'];report=json.loads(json.dumps(report));report['rows'][-1]['evidence']['revenue']['operands'][0]['value']+=1
        with self.assertRaisesRegex(RevenueMixError,'contradicts'):prepare_mix(report,instances)

if __name__=='__main__':unittest.main()
