"""Source and economic-scope controls for FY2025 share-bridge preparation."""
from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import unittest

FOLDER=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pilot_share_bridge_build',FOLDER/'build.py')
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)


class ShareBridgeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=bridge.build();cls.companies={c['ticker']:c for c in cls.data['companies']}

    def test_named_cash_and_debt_subtotals_are_not_approved_operands(self):
        expected={'AAPL':(132420000000,98657000000),'META':(81592000000,58744000000),'GOOGL':(126843000000,48543000000)}
        for ticker,(cash,debt) in expected.items():
            c=self.companies[ticker]
            self.assertEqual(Fraction(c['reported_cash_and_marketable_subtotal']['value_usd']),cash)
            self.assertEqual(Fraction(c['named_debt_carrying_subtotal']['value_usd']),debt)
            self.assertIsNone(c['reported_cash_and_marketable_subtotal']['approved_eligible_amount_usd'])
            self.assertIsNone(c['named_debt_carrying_subtotal']['approved_financing_claim_usd'])
            self.assertFalse(c['named_debt_carrying_subtotal']['finance_lease_added'])

    def test_dated_class_counts_reconcile_without_economic_equivalence(self):
        expected={'AAPL':14773260000,'META':2530000000,'GOOGL':12088000000}
        for ticker,count in expected.items():
            c=self.companies[ticker];shares=c['shares']
            self.assertEqual(Fraction(shares['year_end_reported_total']['value']),count)
            self.assertEqual(shares['year_end_reported_total']['scope']['end'],c['as_of'])
            self.assertEqual(shares['class_equivalence'],'NOT_ADOPTED')
            self.assertIsNone(shares['approved_valuation_denominator'])
            self.assertFalse(shares['weighted_average_eps_shares_selected'])
        for ticker,n in [('META',2),('GOOGL',3)]:
            control=self.companies[ticker]['shares']['class_sum_control']
            self.assertEqual(len(control['class_sources']),n)
            self.assertEqual(control['difference_shares'],'0')
            self.assertFalse(control['economic_equivalence_inferred'])

    def test_later_cover_counts_do_not_replace_anchor_shares(self):
        c=self.companies['AAPL'];cover=c['shares']['cover_date_counts']
        self.assertEqual(len(cover),1)
        self.assertEqual(cover[0]['scope']['end'],'2025-10-17')
        self.assertEqual(Fraction(cover[0]['value']),14776353000)
        self.assertNotEqual(cover[0]['scope']['end'],c['as_of'])
        self.assertNotEqual(cover[0]['value'],c['shares']['year_end_reported_total']['value'])
        google=self.companies['GOOGL']['shares']['cover_primary_prose_support']
        self.assertEqual(google['date'],'2026-01-28')
        self.assertEqual(google['counts_shares'],{'Class A':'5822000000','Class B':'837000000','Class C':'5438000000'})
        self.assertFalse(google['used_as_anchor_denominator'])

    def test_existing_award_counts_are_not_automatically_added(self):
        for ticker,count in [('AAPL',151574000),('META',115552000),('GOOGL',282000000)]:
            c=self.companies[ticker];counts=[p for p in c['awards'] if p['unit']=='shares']
            self.assertEqual(len(counts),1);self.assertEqual(Fraction(counts[0]['value']),count)
            self.assertIsNone(c['shares']['award_adjusted_denominator'])
            self.assertIsNone(c['approved_bridge']['existing_award_value_usd'])

    def test_nci_book_and_explicit_preferred_zero_are_not_whole_claims_clearance(self):
        c=self.companies['GOOGL'];claims=c['claims']
        self.assertTrue(any(p['concept']=='NoncontrollingInterestInVariableInterestEntity' and Fraction(p['value'])==3400000000 for p in claims))
        self.assertTrue(any(p['concept']=='RedeemableNoncontrollingInterestInVariableInterestEntity' and Fraction(p['value'])==841000000 for p in claims))
        self.assertTrue(any(p['concept']=='PreferredStockSharesOutstanding' and Fraction(p['value'])==0 for p in claims))
        self.assertIsNone(c['approved_bridge']['nci_fair_value_usd'])
        for c in self.companies.values():self.assertTrue(all(v is None for v in c['approved_bridge'].values()))

    def test_missing_and_competing_claims_preserve_null(self):
        a=self.companies['AAPL']
        self.assertIsNone(bridge.unique(a['source_points'],'MissingConcept')['value'])
        tax=bridge.unique(a['source_points'],'UnrecognizedTaxBenefits',as_of=a['as_of'])
        self.assertEqual(tax['status'],'COMPETING_SOURCE_POPULATIONS')
        self.assertIsNone(tax['value'])
        self.assertEqual({Fraction(p['value']) for p in tax['observations']},{23200000000,23242000000})

    def test_primary_and_instance_class_scope_cannot_be_switched(self):
        path=bridge.Path(bridge.ANCHORS['meta-fy2025']['package']);package=json.loads((bridge.ROOT/path).read_text())
        filing=bridge.RetainedFiling(bridge.ROOT,package['periods'][-1],{})
        changed=deepcopy(filing)
        ctx=changed.contexts['c-9'];member=next(ctx.iter(bridge.DI+'explicitMember'));member.text='us-gaap:CommonClassBMember'
        with self.assertRaisesRegex(ValueError,'class, entity or unit mismatch'):
            bridge.verified_points(changed,'2025-12-31')

    def test_primary_instance_amount_mismatch_is_rejected(self):
        path=bridge.Path(bridge.ANCHORS['aapl-fy2025']['package']);package=json.loads((bridge.ROOT/path).read_text())
        filing=bridge.RetainedFiling(bridge.ROOT,package['aapl_history_review']['periods'][-1],{})
        node=next(n for n in filing.root if n.tag.endswith('}CommonStockSharesOutstanding') and n.get('contextRef')=='c-20')
        node.text='1'
        with self.assertRaisesRegex(ValueError,'numerical representation'):
            bridge.verified_points(filing,'2025-09-27')

    def test_replay_and_source_hashes_match_retained_evidence(self):
        self.assertEqual(json.loads((FOLDER/'source-schedules.json').read_text()),self.data)
        for path,digest in self.data['inputs_sha256'].items():self.assertEqual(bridge.sha(bridge.ROOT/path),digest)
        self.assertEqual(sum(len(c['source_points']) for c in self.data['companies']),171)
        self.assertEqual(self.data['validation']['per_share_ready_companies'],0)


if __name__=='__main__':unittest.main()
