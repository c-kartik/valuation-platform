"""Consumer separation must not turn provisional cash into financial clearance."""
import json
from pathlib import Path
import unittest

from valuation_platform.review.pilot_cashflows import read_cashflows, RESOURCE

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/company-resolutions/execution-2026-11-04'


class ReadinessTests(unittest.TestCase):
    def test_thirty_cells_keep_old_amounts_and_distinct_ownership_gates(self):
        original = json.loads((ROOT / RESOURCE).read_text())
        totals = dict(available_stated_convention=0, provisional_financing=0,
                      missing_required_input=0, parent_common_fcfe_available=0)
        for ticker in ('AAPL', 'META', 'GOOGL'):
            current = read_cashflows(ROOT, ticker)
            before = original['companies'][ticker]
            # The full old record, including amounts, methods, flags and gaps,
            # must survive unchanged; only the additive contract is new.
            if ticker=='AAPL':
                for p,old in zip(current['periods'],before['periods'],strict=True):
                    self.assertEqual(p['legacy_cfo_fcff'],old['fcff'])
                    self.assertEqual(p['fcfe'],old['fcfe'])
            else:self.assertEqual({k: v for k, v in current.items() if k != 'readiness'}, before)
            r = current['readiness']
            for key in totals:
                totals[key] += r['counts'][key]
            self.assertFalse(r['history_gap_disables_manual_forecast'])
            self.assertFalse(r['prior_parent_common_review_passed'])
            self.assertEqual(r['financial_review_status'], 'OPEN')
            for p in r['periods']:
                if ticker == 'AAPL':
                    self.assertEqual(p['fcff_historical_calculation'], 'AVAILABLE_STATED_CONVENTION')
                if ticker == 'GOOGL':
                    self.assertEqual(p['fcfe_historical_calculation'], 'AVAILABLE_CONSOLIDATED_STATED_CONVENTION')
                    self.assertEqual(p['parent_common_fcfe'], 'UNAVAILABLE_OWNERSHIP_ATTRIBUTION')
                else:
                    self.assertEqual(p['fcfe_historical_calculation'], 'PROVISIONAL_INCOMPLETE_FINANCING')
        self.assertEqual(totals, dict(available_stated_convention=20, provisional_financing=10,
                                     missing_required_input=0, parent_common_fcfe_available=0))

    def test_workpapers_have_exact_tax_bridges_and_do_not_publish_diagnostics(self):
        data = json.loads((OUT / 'step-1-apple-operating.json').read_text())
        self.assertEqual([p['provision_minus_cash_tax']['amount_usd'] for p in data['periods']],
                         ['-10858000000', '-273000000', '-1938000000', '3647000000', '-22650000000'])
        self.assertEqual(data['periods'][-1]['aggregate_after_tax_conversion_UNCLASSIFIED']['amount_usd'], '2288000000')
        for p in data['periods']:
            self.assertEqual(p['bridge_difference_usd'], '0')
            self.assertIsNone(p['verified_operating_fcff_usd'])
            self.assertFalse(p['eligible_for_forecast_calibration'])
            self.assertFalse(p['balancing_plug_used'])

    def test_financing_and_ownership_qualification_survives_review(self):
        funding = json.loads((OUT / 'step-2-financing.json').read_text())
        self.assertEqual(funding['outgoing_messages_sent'], 0)
        self.assertEqual(funding['companies']['META']['periods'][-1]['other_financing_net_usd'], '2220000000')
        for c in funding['companies'].values():
            self.assertEqual(c['clarification_request']['status'], 'DRAFT_NOT_SENT')
            for p in c['periods']:
                self.assertIsNone(p['complete_fcfe_usd'])
                self.assertIsNone(p['debt_content_of_other_usd'])
                self.assertFalse(p['other_net_is_uncertainty_bound'])
        own = json.loads((OUT / 'step-3-alphabet-ownership.json').read_text())
        for p in own['periods']:
            self.assertIsNone(p['parent_common_fcfe_usd'])
            self.assertIsNone(p['nci_fair_value_usd'])
            self.assertIsNone(p['parent_value_bridge']['parent_common_value_usd'])
            self.assertTrue(p['lease_cash_counted_once'])


if __name__ == '__main__':
    unittest.main()
