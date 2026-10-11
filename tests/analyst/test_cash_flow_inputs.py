"""Exact registered reported inputs; no adjusted cash-flow or readiness result."""

import base64
import copy
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from valuation_platform.analyst import cash_flow_inputs as cf


ROOT = Path(__file__).resolve().parents[2]
CFO = 'NetCashProvidedByUsedInOperatingActivities'
PPE = 'PaymentsToAcquirePropertyPlantAndEquipment'


class CashFlowInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids = cf.registered_bundle_ids()
        cls.bundles = tuple(cf.load_msft_bundle(k) for k in cls.ids)
        cls.payload = json.loads(cf.serialize(cls.bundles[0]))

    def test_only_two_explicit_exact_frozen_registrations(self):
        self.assertEqual(self.ids, ('msft-reported-cash-flow-fy2025', 'msft-reported-cash-flow-fy2026'))
        self.assertEqual([b.period.accession for b in self.bundles],
                         ['0000950170-25-100235', '0001193125-26-323660'])
        for b in self.bundles:
            self.assertEqual(b.period.cik, 789019)
            self.assertEqual(b.period.form, '10-K')
            self.assertEqual(b.period.annual_start, date(b.period.annual_end.year - 1, 7, 1))
        for unregistered in ('MSFT', 'msft-reported-cash-flow-fy2024', 'msft-reported-cash-flow-fy2027'):
            with self.subTest(unregistered=unregistered), self.assertRaises(cf.CashFlowInputError):
                cf.load_msft_bundle(unregistered)

    def test_all_reviewed_inputs_and_occurrences_packaged(self):
        self.assertEqual([len(b.inputs) for b in self.bundles], [37, 38])
        self.assertEqual([sum(len(i.occurrences) for i in b.inputs) for b in self.bundles], [42, 43])
        for b in self.bundles:
            for i in b.inputs:
                self.assertEqual(i.source_kind, 'sec_reported')
                self.assertTrue(i.location_and_scope)
                self.assertEqual(tuple(o.ordinal for o in i.occurrences),
                                 tuple(sorted({o.ordinal for o in i.occurrences})))
                for o in i.occurrences:
                    self.assertEqual(o.entity_cik, b.period.cik)
                    self.assertEqual(o.end, b.period.annual_end)
                    self.assertEqual(o.dimensions, ())
                    self.assertEqual(o.normalized_unit, 'USD')
                    self.assertFalse(o.nil)
                    self.assertEqual(Decimal(o.raw_value), i.value_usd)

    def test_reported_cfo_and_cash_ppe_remain_separate(self):
        for b, cfo, ppe in zip(self.bundles, (136162000000, 182935000000), (64551000000, 115948000000)):
            self.assertEqual(b.input(CFO).value_usd, Decimal(cfo))
            self.assertEqual(b.input(CFO).kind, cf.InputKind.CASH_SUBTOTAL)
            self.assertEqual(b.input(PPE).value_usd, Decimal(ppe))
            self.assertEqual(b.input(PPE).displayed_value_usd, Decimal(-ppe))
            self.assertNotIn(PPE, b.cfo_terms)
            self.assertFalse(b.valuation_consumption_approved)
            self.assertFalse(b.is_complete_operating_nwc)
            self.assertFalse(hasattr(b, 'adjusted_subtotal'))
            self.assertFalse(hasattr(b, 'fcff'))

    def test_documented_fourteen_term_reported_cfo_bridge(self):
        for b in self.bundles:
            self.assertEqual(len(b.cfo_terms), 14)
            self.assertTrue(b.cfo_reconciles)
            self.assertEqual(sum(b.input(k).displayed_value_usd for k in b.cfo_terms), b.input(CFO).value_usd)
        # Reconciliation and sign conversion must not depend on global Decimal precision.
        with localcontext() as ctx:
            ctx.prec = 3
            self.assertTrue(self.bundles[0].cfo_reconciles)
            self.assertEqual(self.bundles[0].input(PPE).displayed_value_usd, Decimal('-64551000000'))

    def test_unknowns_are_explicit_none_not_zero_or_estimates(self):
        self.assertEqual([len(b.unknowns) for b in self.bundles], [10, 9])
        for b in self.bundles:
            unknown = {u.input_id: u for u in b.unknowns}
            for key in ('complete_operating_nwc', 'all_in_cash_interest', 'operating_only_cash_tax',
                        'acquisition_only_cash_purchases', 'joint_timing_compatibility'):
                self.assertIsNone(unknown[key].value_usd)
                self.assertTrue(unknown[key].reason)
            for u in b.unknowns:
                with self.assertRaises(cf.CashFlowInputError):
                    replace(u, value_usd=Decimal(0))
            with self.assertRaises(cf.CashFlowInputError):
                b.input('all_in_cash_interest')
        self.assertIsNone(next(u for u in self.bundles[0].unknowns
                              if u.input_id == 'DeferredIncomeTaxesAndTaxCredits').value_usd)

    def test_cash_interest_is_distinct_from_expense_and_lease_interest(self):
        for b, cash, expense, lease in zip(self.bundles, (1600000000, 1500000000),
                                           (2385000000, 3051000000), (1372000000, 2547000000)):
            self.assertEqual(b.input('InterestPaid').value_usd, Decimal(cash))
            self.assertIn('debt', b.input('InterestPaid').location_and_scope)
            self.assertEqual(b.input('InterestExpenseNonoperating').value_usd, Decimal(expense))
            self.assertEqual(b.input('InterestExpenseNonoperating').kind, cf.InputKind.ACCRUED_EXPENSE)
            self.assertEqual(b.input('FinanceLeaseInterestPaymentOnLiability').value_usd, Decimal(lease))

    def test_cash_tax_provision_and_deferred_roles_do_not_collapse(self):
        for b in self.bundles:
            self.assertNotEqual(b.input('IncomeTaxesPaidNet').value_usd, b.input('IncomeTaxExpenseBenefit').value_usd)
            self.assertEqual(b.input('IncomeTaxesPaidNet').kind, cf.InputKind.CASH_PAYMENT)
            self.assertEqual(b.input('IncomeTaxExpenseBenefit').kind, cf.InputKind.ACCRUED_EXPENSE)
        b = self.bundles[1]
        self.assertEqual(b.input('DeferredIncomeTaxExpenseBenefit').value_usd, Decimal(14424000000))
        self.assertEqual(b.input('DeferredIncomeTaxesAndTaxCredits').value_usd, Decimal(14189000000))
        self.assertNotIn('DeferredIncomeTaxExpenseBenefit', b.cfo_terms)
        self.assertIn('DeferredIncomeTaxesAndTaxCredits', b.cfo_terms)

    def test_cash_noncash_and_capital_creditor_basis_remain_distinct(self):
        b = self.bundles[0]
        self.assertEqual(b.input('PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable').kind,
                         cf.InputKind.BOOK_BALANCE)
        self.assertIsNone(b.input('PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable').occurrences[0].start)
        self.assertEqual(b.input('RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability').kind,
                         cf.InputKind.NONCASH_ADDITION)
        self.assertEqual(b.input('FinanceLeasePrincipalPayments').kind, cf.InputKind.CASH_PAYMENT)
        self.assertEqual(b.input('FinanceLeaseRightOfUseAssetAmortization').kind, cf.InputKind.NONCASH_EXPENSE)
        self.assertNotIn('FinanceLeasePrincipalPayments', b.cfo_terms)

    def test_sbc_note_confirmation_is_not_a_second_addback(self):
        for b in self.bundles:
            self.assertEqual(b.input('ShareBasedCompensation').value_usd,
                             b.input('AllocatedShareBasedCompensationExpense').value_usd)
            self.assertEqual(b.cfo_terms.count('ShareBasedCompensation'), 1)
            self.assertNotIn('AllocatedShareBasedCompensationExpense', b.cfo_terms)
            self.assertIn('not', b.input('EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense').location_and_scope)

    def test_recast_comparatives_never_replace_selected_values(self):
        self.assertEqual(self.bundles[0].input('DepreciationAmortizationAndOther').value_usd, Decimal(34153000000))
        self.assertEqual(self.bundles[1].input('DepreciationAmortizationAndOther').value_usd, Decimal(38534000000))
        for b in self.bundles:
            self.assertTrue(any('recasts' in s for s in b.limitations))
        self.assertNotIn(692, [o.ordinal for i in self.bundles[1].inputs for o in i.occurrences])
        self.assertNotIn(698, [o.ordinal for i in self.bundles[1].inputs for o in i.occurrences])

    def test_confirming_occurrences_count_once_and_dimensioned_income_excluded(self):
        for b, excluded in zip(self.bundles, (804, 811)):
            self.assertEqual(len(b.input('NetIncomeLoss').occurrences), 4)
            self.assertNotIn(excluded, [o.ordinal for o in b.input('NetIncomeLoss').occurrences])
            self.assertEqual(b.cfo_terms.count('NetIncomeLoss'), 1)
        item = self.bundles[0].input('IncomeTaxExpenseBenefit')
        with self.assertRaises(cf.CashFlowInputError):
            replace(self.bundles[0], inputs=tuple(replace(i, occurrences=i.occurrences[:1])
                                                 if i == item else i for i in self.bundles[0].inputs))

    def test_rounded_precision_and_original_representation_survive_roundtrip(self):
        for b in self.bundles:
            restored = cf.deserialize(cf.serialize(b))
            self.assertEqual(restored, b)
            self.assertTrue(restored.cfo_reconciles)
            self.assertEqual(restored.input('InterestPaid').occurrences[0].decimals, '-8')
            self.assertEqual(restored.input(PPE).occurrences[0].decimals, '-6')
            for receipt in restored.artifacts:
                self.assertEqual(receipt.artifact.representation, 'sec_response_body_bytes')
                self.assertEqual(receipt.artifact.digest_type, 'sha256_sec_response_body_bytes')
                self.assertEqual(hashlib.sha256(receipt.artifact.body).hexdigest(), receipt.artifact.sha256)
                self.assertTrue(receipt.retrieved_at_utc)
                self.assertEqual(receipt.http_status, 200)

    def test_immutable_models(self):
        with self.assertRaises(FrozenInstanceError):
            self.bundles[0].inputs = ()
        with self.assertRaises(cf.CashFlowInputError):
            replace(self.bundles[0], inputs=list(self.bundles[0].inputs))

    def test_invalid_occurrence_identity_unit_nil_dimensions_and_precision(self):
        o = self.bundles[0].input(PPE).occurrences[0]
        for changes in ({'nil': True}, {'dimensions': ('Axis=Member',)}, {'normalized_unit': 'EUR'},
                        {'decimals': 'rounded'}, {'ordinal': -1}, {'raw_value': 'NaN'}):
            with self.subTest(changes=changes), self.assertRaises(cf.CashFlowInputError):
                replace(o, **changes)
        for changes in ({'entity_cik': 320193}, {'end': date(2024, 6, 30)},
                        {'start': date(2024, 7, 2)}, {'context_id': 'broken'},
                        {'unit_id': 'broken'}, {'ordinal': o.ordinal + 1}, {'raw_value': '1'}):
            with self.subTest(changes=changes), self.assertRaises(cf.CashFlowInputError):
                altered = replace(o, **changes)
                item = replace(self.bundles[0].input(PPE), occurrences=(altered,))
                replace(self.bundles[0], inputs=tuple(item if i.input_id == PPE else i for i in self.bundles[0].inputs))

    def test_conflicting_numeric_occurrences_reject(self):
        item = self.bundles[0].input('IncomeTaxExpenseBenefit')
        with self.assertRaises(cf.CashFlowInputError):
            replace(item, occurrences=(item.occurrences[0], replace(item.occurrences[1], raw_value='1')))
        with self.assertRaises(cf.CashFlowInputError):
            replace(item, occurrences=tuple(reversed(item.occurrences)))

    def test_changed_subtotal_or_missing_bridge_is_not_certified(self):
        b = self.bundles[0]
        with self.assertRaises(cf.CashFlowInputError):
            replace(b, cfo_terms=b.cfo_terms[:-1])
        with self.assertRaises(cf.CashFlowInputError):
            replace(b, cfo_terms=b.cfo_terms + (PPE,))
        for flag in ('valuation_consumption_approved', 'is_complete_operating_nwc'):
            with self.assertRaises(cf.CashFlowInputError):
                replace(b, **{flag: True})

    def test_invalid_artifact_representations_and_bytes(self):
        a = self.bundles[0].artifacts[0].artifact
        for changes in ({'representation': 'parsed_json'}, {'digest_type': 'sha256_reserialized_json'},
                        {'body': a.body + b' '}, {'sha256': '0' * 64}, {'accession': '0000950170-25-100236'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(a, **changes)
        for changes in ({'byte_length': 1}, {'retrieved_at_utc': '2026-10-11'}, {'http_status': 404}):
            with self.assertRaises(cf.CashFlowInputError):
                replace(self.bundles[0].artifacts[0], **changes)

    def test_source_link_context_nil_and_unit_corruption_fail_not_disappear(self):
        b = self.bundles[0]
        receipt = b.artifacts[1]
        body = receipt.artifact.body
        # Hashes freshly computed only for structural model tests. Registry/serde
        # acceptance still pins the original digest and rejects any such refresh.
        needle = b'<us-gaap:PaymentsToAcquirePropertyPlantAndEquipment'
        start = body.index(needle)
        end = body.index(b'>', start)
        tag = body[start:end]
        for bad in (tag.replace(b'contextRef="C_7102029d-8d6c-44c5-b166-04cf41443b1e"', b'contextRef="broken"'),
                    tag.replace(b'unitRef="U_USD"', b'unitRef="broken"'), tag + b' xsi:nil="true"'):
            altered = body[:start] + bad + body[end:]
            a = replace(receipt.artifact, body=altered, sha256=hashlib.sha256(altered).hexdigest())
            r = replace(receipt, artifact=a, byte_length=len(altered))
            with self.subTest(bad=bad[-40:]), self.assertRaises(cf.CashFlowInputError):
                replace(b, artifacts=(b.artifacts[0], r))

    def test_serialization_is_closed_and_rechecks_all_reviewed_fields(self):
        for mutation in ('value', 'kind', 'scope', 'precision', 'ordinal', 'unknown_zero',
                         'unknown_removed', 'amended', 'future', 'approval', 'summary', 'extra'):
            d = copy.deepcopy(self.payload)
            v = d['bundle']
            if mutation == 'value': v['inputs'][0]['value_usd'] = '0'
            elif mutation == 'kind': v['inputs'][0]['kind'] = 'accrued_expense'
            elif mutation == 'scope': v['inputs'][1]['location_and_scope'] = 'all-in interest'
            elif mutation == 'precision': v['inputs'][1]['occurrences'][0]['decimals'] = 'INF'
            elif mutation == 'ordinal': v['inputs'][0]['occurrences'][0]['ordinal'] += 1
            elif mutation == 'unknown_zero': v['unknowns'][0]['value_usd'] = '0'
            elif mutation == 'unknown_removed': v['unknowns'].pop()
            elif mutation == 'amended': v['period']['form'] = '10-K/A'
            elif mutation == 'future': v['period']['annual_end'] = '2027-06-30'
            elif mutation == 'approval': v['valuation_consumption_approved'] = True
            elif mutation == 'summary': v['cfo_reconciles'] = False
            else: d['adjusted_subtotal'] = '1'
            with self.subTest(mutation=mutation), self.assertRaises(cf.CashFlowInputError):
                cf.deserialize(json.dumps(d))

    def test_serialized_evidence_metadata_and_raw_body_cannot_be_refreshed_implicitly(self):
        for mutation in ('representation', 'digest', 'body', 'length', 'time', 'missing'):
            d = copy.deepcopy(self.payload)
            a = d['artifacts'][0]
            if mutation == 'representation': a['representation'] = 'reserialized_html'
            elif mutation == 'digest': a['sha256'] = '0' * 64
            elif mutation == 'body': a['response_body_gzip_base64'] = base64.b64encode(gzip.compress(b'changed')).decode()
            elif mutation == 'length': a['byte_length'] = 1
            elif mutation == 'time': a['retrieved_at_utc'] = '2026-10-12T00:00:00+00:00'
            else: d['artifacts'].pop()
            with self.subTest(mutation=mutation), self.assertRaises(cf.CashFlowInputError):
                cf.deserialize(json.dumps(d))

    def test_registry_is_immutable_and_serialization_schema_distinct(self):
        with patch.object(cf, '_REGISTRY_SHA256', '0' * 64), self.assertRaises(cf.CashFlowInputError):
            cf.registered_bundle_ids()
        self.assertEqual(self.payload['schema'], 'reported-cash-flow-input-bundle-v1')
        self.assertNotEqual(self.payload['schema'], '5')
        text = json.dumps(self.payload)
        with self.assertRaises(cf.CashFlowInputError):
            cf.deserialize(text.replace('"schema":', '"schema":"bad","schema":', 1))

    def test_truncated_or_corrupted_compressed_originals_reject(self):
        encoded = self.payload['artifacts'][0]['response_body_gzip_base64']
        body = base64.b64decode(encoded)
        for bad in (body[:20], b'not gzip', body[:15] + b'broken' + body[21:]):
            d = copy.deepcopy(self.payload)
            d['artifacts'][0]['response_body_gzip_base64'] = base64.b64encode(bad).decode()
            with self.assertRaises(cf.CashFlowInputError):
                cf.deserialize(json.dumps(d))


if __name__ == '__main__':
    unittest.main()
