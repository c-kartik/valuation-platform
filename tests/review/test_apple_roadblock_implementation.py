"""Independent checks for Apple A1-A8 source implementation and availability."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import implement_apple_roadblocks as apple


class AppleRoadblockImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=apple.build()

    def test_actual_metric_availability_does_not_clear_missing_operands(self):
        periods=self.data['periods']
        self.assertEqual([p['fiscal_year'] for p in periods],[2021,2022,2023,2024,2025])
        expected_fcfe=[105618,111320,89683,102809,90284]
        for p,n in zip(periods,expected_fcfe,strict=True):
            a=p['availability']
            self.assertEqual(Fraction(a['fcfe_identified_funding']['value_usd']),n*1000000)
            self.assertEqual(a['fcfe_identified_funding']['status'],'PROVISIONAL_UNCLASSIFIED_FINANCING')
            self.assertIsNone(a['fcfe_verified']['value_usd'])
            self.assertIsNone(a['fcff_valuation_aligned']['value_usd'])
        self.assertTrue(all(p['availability']['fcff_reported_cfo_basis']['value_usd'] is not None for p in periods[:3]))
        self.assertTrue(all(p['availability']['fcff_reported_cfo_basis']['value_usd'] is None for p in periods[3:]))
        self.assertEqual(self.data['parent_status'],'OPEN')

    def test_credit_magnitude_is_negative_reconciliation_contribution(self):
        table=self.data['periods'][0]['tax_review']['etr_note']
        credit=next(p for p in table['components'] if p['primary_table']['caption']=='Research and development credit, net')
        self.assertEqual(Fraction(credit['value']),1033000000)
        self.assertEqual(Fraction(credit['reconciliation_contribution_usd']),-1033000000)
        self.assertEqual(sum(Fraction(p['reconciliation_contribution_usd']) for p in table['components']),14527000000)
        for p in self.data['periods']:self.assertEqual(p['tax_review']['etr_note']['difference_usd'],'0')

    def test_state_aid_accounting_adjustment_never_rewrites_historical_cash(self):
        for i,provision,charge,pretax in [(3,29749,10246,123485),(4,20719,-486,132729)]:
            tax=self.data['periods'][i]['tax_review'];rate=tax['state_aid_only_adjusted_rate']['exact_fraction']
            self.assertEqual(Fraction(int(rate['numerator']),int(rate['denominator'])),Fraction(provision-charge,pretax))
            self.assertEqual(tax['historical_cash_adjustment_usd'],'0')
            self.assertIsNone(tax['fully_normalized_operating_tax_rate'])

    def test_later_amortization_does_not_force_da_equality(self):
        a,b=[p['new_comparative_support'] for p in self.data['periods'][-2:]]
        self.assertEqual(Fraction(a['note_sum_minus_cash_statement_da']['amount_usd']),355000000)
        self.assertFalse(a['note_sum_rounding_compatible_with_cf_da'])
        self.assertEqual(Fraction(b['note_sum_minus_cash_statement_da']['amount_usd']),2000000)
        self.assertTrue(b['note_sum_rounding_compatible_with_cf_da'])
        self.assertTrue(all(not p['supports_complete_expense_alignment'] for p in (a,b)))
        self.assertEqual(a['source_identity']['accession'],'0000320193-26-000026')
        self.assertEqual(a['target_identity']['annual_end'],'2024-09-28')

    def test_book_intangible_reclassification_is_not_cash_investment(self):
        b=self.data['periods'][-1]['new_comparative_support']['noncurrent_asset_presentation']
        self.assertEqual(Fraction(b['original_other_noncurrent_assets']['value']),83727000000)
        self.assertEqual(Fraction(b['later_other_noncurrent_assets']['value']),72634000000)
        self.assertEqual(Fraction(b['separately_shown_intangibles']['value']),11093000000)
        self.assertFalse(b['cash_investment_inferred'])

    def test_new_api_absence_is_bounded_and_cannot_be_zero(self):
        for y in ['2024','2025']:
            search=self.data['current_companyfacts_search'][y]
            self.assertEqual(search['gross_expensed_interest_observations'],[])
            p=self.data['periods'][int(y)-2021]
            self.assertIsNone(p['interest_expense'])
            self.assertIsNone(p['missing_input_inventory']['FinanceLeasePrincipalPayments'])

    def test_source_body_tamper_fails_before_parsing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);folder=root/apple.FOLDER;(folder/'new-sources').mkdir(parents=True)
            manifest=json.loads((ROOT/apple.FOLDER/'new-source-manifest.json').read_text())
            (folder/'new-source-manifest.json').write_text(json.dumps(manifest))
            (folder/manifest[0]['file']).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'hash/length'):apple.verify_new_sources(root)

    def test_forward_policy_and_publication_unchanged(self):
        policy=self.data['forecast_tax_policy_reconciliation']
        self.assertEqual((policy['tax_start_after'],policy['tax_endpoint_after'],policy['terminal_tax_after']),('0.18','0.20','0.20'))
        self.assertFalse(policy['source_fact'])
        self.assertEqual(policy['forecast_numeric_change'],'0')
        self.assertFalse(self.data['publication']['fully_resolved_company'])
        self.assertEqual(json.loads((ROOT/apple.OUTPUT).read_text()),self.data)


if __name__=='__main__':unittest.main()
