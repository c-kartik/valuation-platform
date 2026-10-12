"""Executable four-period mapping decisions; no adapter or financial calculator."""

import copy
from decimal import Decimal, localcontext
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("pilot_mapping_checks", ROOT / "scripts/validate_pilot_input_mappings.py")
mapping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapping)


class PilotMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = mapping.load_document()
        cls.bundles = mapping.load_bundles()

    def reject(self, mutation):
        doc = copy.deepcopy(self.doc)
        mutation(doc)
        with self.assertRaises(mapping.MappingError):
            mapping.validate(doc, self.bundles)

    def test_four_periods_fifty_six_field_families(self):
        report = mapping.validate(self.doc, self.bundles)
        self.assertEqual(len(report), 4)
        self.assertEqual(sum(r['field_families'] for r in report.values()), 56)
        for key, r in report.items():
            self.assertEqual((r['mapped'], r['limited_support'], r['unavailable']),
                             (7, 1, 6) if key.startswith('aapl') else (8, 1, 5))
        self.assertEqual(sum(r['mapped_source_inputs'] for r in report.values()), 69)

    def test_exact_period_registry_and_input_pointer(self):
        for key, value in (('accession', '0000950170-25-100236'), ('annual_start', '2024-01-01'),
                           ('annual_end', '2025-12-31'), ('cik', 320193), ('form', '10-K/A')):
            self.reject(lambda d, k=key, v=value: d['periods'][0]['period'].__setitem__(k, v))
        self.reject(lambda d: d['periods'][0].__setitem__('registry_sha256', '0' * 64))
        self.reject(lambda d: d['periods'][0]['fields']['cash_capex']['bindings'][0].__setitem__(
            'registry_pointer', '/bundles/1/inputs/0'))

    def test_every_confirming_occurrence_and_context_retained(self):
        for key, value in (('occurrence_ordinals', []), ('context_id', 'wrong-context')):
            self.reject(lambda d, k=key, v=value: d['periods'][0]['fields']['reported_tax_context']['bindings'][1].__setitem__(k, v))
        for row in self.doc['periods']:
            for f in row['fields'].values():
                for bind in f['bindings']:
                    if 'retained_direct' in bind:
                        self.assertTrue(bind['retained_direct']['candidates'])
                        continue
                    item = self.bundles[row['bundle_id']].input(bind['input_id'])
                    self.assertEqual(bind['occurrence_ordinals'], [o.ordinal for o in item.occurrences])
                    self.assertTrue(all(o.context_id == bind['context_id'] for o in item.occurrences))

    def test_sign_scale_precision_no_implicit_conversion(self):
        for key, value in (('scale', 1000000), ('scale', True), ('sign', 1), ('precision', 'INF'), ('unit', 'shares')):
            self.reject(lambda d, k=key, v=value: d['periods'][0]['fields']['cash_capex']['bindings'][0].__setitem__(k, v))
        with localcontext() as ctx:
            ctx.prec = 3
            for b in self.bundles.values():
                payment = b.input('PaymentsToAcquirePropertyPlantAndEquipment')
                self.assertEqual(payment.displayed_value_usd, payment.value_usd.copy_negate())
                self.assertTrue(b.cfo_reconciles)
            a = self.bundles['aapl-reported-cash-flow-fy2025']
            self.assertEqual(a.input('IncreaseDecreaseInInventories').value_usd, Decimal('-1400000000'))
            self.assertEqual(a.input('IncreaseDecreaseInInventories').displayed_value_usd, Decimal('1400000000'))

    def test_sbc_distinct_roles_and_shared_population_not_additive(self):
        for row in self.doc['periods']:
            f = row['fields']['stock_based_compensation']
            self.assertEqual(f['aggregation'], 'none')
            self.assertEqual({x['role'] for x in f['bindings']}, {'sbc_cfo_addback', 'sbc_note_expense'})
            self.assertEqual({x['population'] for x in f['bindings']}, {'recognized_sbc'})
            b = self.bundles[row['bundle_id']]
            self.assertIn('ShareBasedCompensation', b.cfo_terms)
            self.assertNotIn('AllocatedShareBasedCompensationExpense', b.cfo_terms)
        self.reject(lambda d: d['periods'][0]['fields']['stock_based_compensation'].__setitem__('aggregation', 'sum'))
        self.reject(lambda d: d['periods'][0]['fields']['stock_based_compensation']['bindings'][0].__setitem__('role', 'economic_cost'))

    def test_alphabet_rounded_expense_never_becomes_adjustment(self):
        row = self.doc['periods'][3]
        b = self.bundles[row['bundle_id']]
        binds = {v['role']: v for v in row['fields']['stock_based_compensation']['bindings']}
        self.assertEqual(b.input(binds['sbc_note_expense']['input_id']).value_usd, Decimal('22800000000'))
        self.assertEqual(b.input(binds['sbc_cfo_addback']['input_id']).value_usd, Decimal('22785000000'))
        self.assertEqual(binds['sbc_note_expense']['precision'], '-8')
        self.assertEqual(binds['sbc_cfo_addback']['precision'], '-6')
        self.reject(lambda d: d['periods'][3]['fields']['stock_based_compensation']['bindings'][1].__setitem__('precision', '-6'))

    def test_cash_movements_are_not_book_delta_nwc(self):
        for row in self.doc['periods']:
            f = row['fields']['reported_cash_flow_working_capital_movements']
            self.assertEqual(f['completeness'], 'partial')
            self.assertEqual(f['aggregation'], 'none')
            self.assertTrue(all(b['role'] == 'reported_cash_flow_movement' for b in f['bindings']))
            self.assertTrue(all(b['input_id'].startswith('IncreaseDecreaseIn') for b in f['bindings']))
        self.reject(lambda d: d['periods'][0]['fields']['reported_cash_flow_working_capital_movements']['bindings'][0].__setitem__('role', 'book_delta_nwc'))

    def test_da_related_facts_do_not_approve_primitive_or_totals(self):
        for row in self.doc['periods']:
            f = row['fields']['depreciation_amortization']
            self.assertEqual((f['status'], f['completeness'], f['aggregation']), ('limited_support', 'partial', 'none'))
        self.reject(lambda d: d['periods'][0]['fields']['depreciation_amortization'].__setitem__('completeness', 'complete'))
        self.reject(lambda d: d['periods'][0]['fields']['depreciation_amortization'].__setitem__('status', 'mapped'))

    def test_deferred_tax_provision_and_cfo_adjustment_remain_distinct(self):
        b = self.bundles['msft-reported-cash-flow-fy2026']
        self.assertEqual(b.input('DeferredIncomeTaxesAndTaxCredits').value_usd, Decimal('14189000000'))
        self.assertEqual(b.input('DeferredIncomeTaxExpenseBenefit').value_usd, Decimal('14424000000'))
        self.assertNotIn('DeferredIncomeTaxExpenseBenefit', b.cfo_terms)
        g = self.bundles['googl-reported-cash-flow-fy2024']
        self.assertEqual(g.input('DeferredIncomeTaxesAndTaxCredits').value_usd, Decimal('-5257000000'))
        self.assertEqual(g.input('DeferredIncomeTaxExpenseBenefit').value_usd, Decimal('-5256000000'))
        aapl = self.doc['periods'][2]['fields']['deferred_taxes']
        self.assertEqual(aapl['status'], 'unavailable')
        self.assertIsNotNone(aapl['null_reason'])

    def test_no_residual_defined_reconciliation(self):
        for row in self.doc['periods']:
            f = row['fields']['unclassified_cfo_reconciliation_residual']
            self.assertEqual(f['status'], 'unavailable')
            self.assertEqual(f['bindings'], [])
            self.assertEqual(row['reported_cfo_check']['kind'], 'independent_reported_statement_check')
            self.assertIsNone(row['reported_cfo_check']['residual_operand'])
        self.reject(lambda d: d['periods'][0]['reported_cfo_check'].__setitem__('residual_operand', 'CFO-minus-known'))
        self.reject(lambda d: d['periods'][0]['reported_cfo_check'].__setitem__('kind', 'residual_balanced'))

    def test_duplicate_sources_and_overlapping_population_sums_rejected(self):
        self.reject(lambda d: d['periods'][0]['fields']['cash_capex']['bindings'].append(
            copy.deepcopy(d['periods'][0]['fields']['cash_capex']['bindings'][0])))
        self.reject(lambda d: d['periods'][0]['fields']['deferred_taxes'].__setitem__('aggregation', 'sum'))
        self.reject(lambda d: d['periods'][0]['fields']['depreciation_amortization'].__setitem__('aggregation', 'sum'))

    def test_null_requirements_cannot_be_acknowledged_away(self):
        for field in ('unclassified_cfo_reconciliation_residual',
                      'cash_investment_components', 'debt_lease_components', 'other_equity_bridge_claims_assets',
                      'point_in_time_shares'):
            self.reject(lambda d, f=field: d['periods'][0]['fields'][f].__setitem__('null_reason', None))
            self.reject(lambda d, f=field: d['periods'][0]['fields'][f].__setitem__('unresolved_requirements', []))
        self.reject(lambda d: d['periods'][0]['fields']['revenue'].__setitem__('status', 'accepted_complete'))

    def test_absent_field_or_injected_corpus_value_rejected(self):
        self.reject(lambda d: d['periods'][0]['fields'].pop('ebit'))
        self.reject(lambda d: d['periods'][0]['fields']['revenue'].__setitem__('value', 1))
        self.reject(lambda d: d['periods'][0]['fields']['stock_based_compensation'].__setitem__('origin', 'proxy'))

    def test_supplementary_disclosures_are_not_lost_or_reclassified(self):
        self.reject(lambda d: d['periods'][0]['supplementary_input_ids'].clear())
        for row in self.doc['periods']:
            self.assertIn('OperatingLeasePayments', row['supplementary_input_ids'])
            self.assertIn('PaymentsForProceedsFromOtherInvestingActivities', row['supplementary_input_ids'])
            self.assertEqual(row['fields']['debt_lease_components']['bindings'], [])

    def test_reproducible_report_and_original_bundle_flags(self):
        self.assertEqual(mapping.validate(self.doc, self.bundles), mapping.validate(self.doc, self.bundles))
        for b in self.bundles.values():
            self.assertFalse(b.is_complete_operating_nwc)
            self.assertFalse(b.valuation_consumption_approved)
            self.assertTrue(b.cfo_reconciles)

    def test_only_four_registered_periods_no_comparatives(self):
        self.reject(lambda d: d['periods'][3].__setitem__('bundle_id', 'googl-reported-cash-flow-fy2023'))
        self.reject(lambda d: d['periods'].append(copy.deepcopy(d['periods'][0])))


if __name__ == '__main__':
    unittest.main()
