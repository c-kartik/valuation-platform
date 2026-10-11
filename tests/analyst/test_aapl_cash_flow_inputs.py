"""One reviewed reported history, not an analyst economic treatment."""

import base64
import copy
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
import unittest
from unittest.mock import patch

from valuation_platform.analyst import aapl_cash_flow_inputs as aapl
from valuation_platform.analyst import cash_flow_inputs as cf


class AaplCashFlowInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = aapl.load_aapl_bundle('aapl-reported-cash-flow-fy2025')
        cls.payload = json.loads(aapl.serialize(cls.bundle))

    def test_only_one_exact_frozen_registration(self):
        self.assertEqual(aapl.registered_bundle_ids(), ('aapl-reported-cash-flow-fy2025',))
        p = self.bundle.period
        self.assertEqual((p.cik, p.accession, p.annual_start, p.annual_end, p.form),
                         (320193, '0000320193-25-000079', date(2024, 9, 29), date(2025, 9, 27), '10-K'))
        for key in ('AAPL', 'aapl-reported-cash-flow-fy2024', 'aapl-reported-cash-flow-fy2023',
                    'aapl-reported-cash-flow-fy2026', 'msft-reported-cash-flow-fy2025'):
            with self.subTest(key=key), self.assertRaises(cf.CashFlowInputError):
                aapl.load_aapl_bundle(key)

    def test_core_inputs_are_separate_reported_roles(self):
        for name, value, kind, sign in (
            ('NetCashProvidedByUsedInOperatingActivities', 111482000000, cf.InputKind.CASH_SUBTOTAL, 1),
            ('PaymentsToAcquirePropertyPlantAndEquipment', 12715000000, cf.InputKind.CASH_PAYMENT, -1),
            ('IncomeTaxesPaidNet', 43369000000, cf.InputKind.CASH_PAYMENT, -1),
            ('IncomeTaxExpenseBenefit', 20719000000, cf.InputKind.ACCRUED_EXPENSE, 1),
            ('ShareBasedCompensation', 12863000000, cf.InputKind.RECONCILIATION, 1),
            ('AllocatedShareBasedCompensationExpense', 12863000000, cf.InputKind.NONCASH_EXPENSE, 1),
            ('OperatingLeasePayments', 2100000000, cf.InputKind.CASH_PAYMENT, -1)):
            i = self.bundle.input(name)
            self.assertEqual((i.value_usd, i.kind, i.display_multiplier), (Decimal(value), kind, sign))
        self.assertEqual(self.bundle.cfo_terms.count('ShareBasedCompensation'), 1)
        self.assertNotIn('AllocatedShareBasedCompensationExpense', self.bundle.cfo_terms)
        self.assertNotIn('OperatingLeasePayments', self.bundle.cfo_terms)
        self.assertIn('not an approved cost proxy',
                      self.bundle.input('AllocatedShareBasedCompensationExpense').location_and_scope)

    def test_ten_term_reported_bridge_and_raw_displayed_signs(self):
        self.assertEqual(len(self.bundle.cfo_terms), 10)
        self.assertTrue(self.bundle.cfo_reconciles)
        for key, raw, display in (('OtherNoncashIncomeExpense', 89000000, -89000000),
                                  ('IncreaseDecreaseInInventories', -1400000000, 1400000000),
                                  ('IncreaseDecreaseInOtherOperatingLiabilities', -11076000000, -11076000000)):
            self.assertEqual(self.bundle.input(key).value_usd, Decimal(raw))
            self.assertEqual(self.bundle.input(key).displayed_value_usd, Decimal(display))
        with localcontext() as ctx:
            ctx.prec = 3
            self.assertTrue(self.bundle.cfo_reconciles)
        with self.assertRaises(cf.CashFlowInputError):
            replace(self.bundle, cfo_terms=self.bundle.cfo_terms[:-1])
        with self.assertRaises(cf.CashFlowInputError):
            replace(self.bundle, cfo_terms=self.bundle.cfo_terms + ('AllocatedShareBasedCompensationExpense',))

    def test_all_confirmations_and_no_comparative_occurrences(self):
        self.assertEqual(len(self.bundle.inputs), 21)
        self.assertEqual(tuple(o.ordinal for o in self.bundle.input('NetIncomeLoss').occurrences),
                         (321, 336, 484, 613))
        self.assertEqual(tuple(o.ordinal for o in self.bundle.input('IncomeTaxExpenseBenefit').occurrences),
                         (318, 920, 948))
        self.assertEqual(sum(len(i.occurrences) for i in self.bundle.inputs), 26)
        for i in self.bundle.inputs:
            for o in i.occurrences:
                self.assertEqual((o.entity_cik, o.start, o.end, o.context_id, o.unit_id,
                                  o.normalized_unit, o.dimensions, o.nil),
                                 (320193, date(2024, 9, 29), date(2025, 9, 27), 'c-1', 'usd', 'USD', (), False))
                self.assertEqual(Decimal(o.raw_value), i.value_usd)
        item = self.bundle.input('NetIncomeLoss')
        with self.assertRaises(cf.CashFlowInputError):
            replace(self.bundle, inputs=tuple(replace(i, occurrences=i.occurrences[:1])
                                              if i == item else i for i in self.bundle.inputs))

    def test_unknowns_are_null_and_cannot_be_zero_defaults(self):
        unknowns = {u.input_id: u for u in self.bundle.unknowns}
        self.assertEqual(len(unknowns), 11)
        for name in ('cash_interest', 'complete_lease_cash_coverage', 'finance_lease_interest_cash',
                     'finance_lease_principal_cash', 'acquisition_only_cash_purchases',
                     'intangible_only_cash_purchases', 'complete_operating_nwc', 'joint_timing_compatibility'):
            self.assertIsNone(unknowns[name].value_usd)
            self.assertTrue(unknowns[name].reason)
        for u in self.bundle.unknowns:
            with self.assertRaises(cf.CashFlowInputError):
                replace(u, value_usd=Decimal(0))
        with self.assertRaises(cf.CashFlowInputError):
            self.bundle.input('InterestPaid')

    def test_lease_precision_cash_expense_and_noncash_remain_distinct(self):
        for name in ('OperatingLeasePayments', 'OperatingLeaseCost', 'VariableLeaseCost',
                     'RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities'):
            self.assertEqual(self.bundle.input(name).occurrences[0].decimals, '-8')
        self.assertEqual(self.bundle.input('VariableLeaseCost').kind, cf.InputKind.ACCRUED_EXPENSE)
        self.assertEqual(self.bundle.input('VariableLeaseCost').value_usd, Decimal(16100000000))
        self.assertEqual(self.bundle.input('RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities').kind,
                         cf.InputKind.NONCASH_ADDITION)
        self.assertEqual(self.bundle.input('PaymentsRelatedToTaxWithholdingForShareBasedCompensation').value_usd,
                         Decimal(5960000000))
        self.assertNotIn(1181, [o.ordinal for i in self.bundle.inputs for o in i.occurrences])

    def test_roundtrip_original_bytes_receipts_and_no_readiness(self):
        b = aapl.deserialize(aapl.serialize(self.bundle))
        self.assertEqual(b, self.bundle)
        self.assertFalse(b.is_complete_operating_nwc)
        self.assertFalse(b.valuation_consumption_approved)
        self.assertFalse(hasattr(b, 'adjusted_subtotal'))
        self.assertFalse(hasattr(b, 'fcff'))
        for r in b.artifacts:
            self.assertEqual(r.artifact.representation, 'sec_response_body_bytes')
            self.assertEqual(r.artifact.digest_type, 'sha256_sec_response_body_bytes')
            self.assertEqual(hashlib.sha256(r.artifact.body).hexdigest(), r.artifact.sha256)
            self.assertEqual(len(r.artifact.body), r.byte_length)
            self.assertEqual(r.http_status, 200)
            self.assertTrue(r.retrieved_at_utc)
        self.assertEqual(b.input('OperatingLeasePayments').occurrences[0].raw_value, '2100000000')
        self.assertEqual(b.input('OperatingLeasePayments').occurrences[0].decimals, '-8')

    def test_invalid_provenance_and_receipts(self):
        r = self.bundle.artifacts[0]
        for change in ({'representation': 'parsed_html'}, {'digest_type': 'sha256_reserialized_html'},
                       {'sha256': '0' * 64}, {'body': r.artifact.body + b' '},
                       {'accession': '0000320193-25-000080'}):
            with self.subTest(change=list(change)), self.assertRaises(ValueError):
                replace(r.artifact, **change)
        for change in ({'retrieved_at_utc': '2026-10-12'}, {'http_status': 404}, {'byte_length': 1}):
            with self.assertRaises(cf.CashFlowInputError):
                replace(r, **change)

    def test_serialization_rejects_changed_fields_unknowns_and_comparatives(self):
        for mutation in ('value', 'kind', 'scope', 'precision', 'ordinal', 'context', 'unit',
                         'nil', 'dimensions', 'unknown_zero', 'unknown_removed', 'amended',
                         'comparative', 'id', 'approval', 'summary', 'extra'):
            d = copy.deepcopy(self.payload)
            b = d['bundle']; i = b['inputs'][0]; o = i['occurrences'][0]
            if mutation == 'value': i['value_usd'] = '0'
            elif mutation == 'kind': i['kind'] = 'cash_payment'
            elif mutation == 'scope': i['location_and_scope'] = 'approved organic cash'
            elif mutation == 'precision': o['decimals'] = 'INF'
            elif mutation == 'ordinal': o['ordinal'] += 1
            elif mutation == 'context': o['context_id'] = 'c-18'
            elif mutation == 'unit': o['normalized_unit'] = 'EUR'
            elif mutation == 'nil': o['nil'] = True
            elif mutation == 'dimensions': o['dimensions'] = ['Axis=Member']
            elif mutation == 'unknown_zero': b['unknowns'][0]['value_usd'] = '0'
            elif mutation == 'unknown_removed': b['unknowns'].pop()
            elif mutation == 'amended': b['period']['form'] = '10-K/A'
            elif mutation == 'comparative': b['period']['annual_end'] = '2024-09-28'
            elif mutation == 'id': b['bundle_id'] = 'aapl-reported-cash-flow-fy2024'
            elif mutation == 'approval': b['valuation_consumption_approved'] = True
            elif mutation == 'summary': b['cfo_reconciles'] = False
            else: d['interest_total'] = '1'
            with self.subTest(mutation=mutation), self.assertRaises(cf.CashFlowInputError):
                aapl.deserialize(json.dumps(d))

    def test_serialization_rejects_changed_original_body_metadata_and_encoding(self):
        for mutation in ('representation', 'digest', 'body', 'length', 'time', 'missing', 'gzip'):
            d = copy.deepcopy(self.payload); r = d['artifacts'][0]
            if mutation == 'representation': r['representation'] = 'reserialized_html'
            elif mutation == 'digest': r['sha256'] = '0' * 64
            elif mutation == 'body': r['response_body_gzip_base64'] = base64.b64encode(gzip.compress(b'changed')).decode()
            elif mutation == 'length': r['byte_length'] = 1
            elif mutation == 'time': r['retrieved_at_utc'] = '2026-10-12T00:00:00+00:00'
            elif mutation == 'missing': d['artifacts'].pop()
            else: r['response_body_gzip_base64'] = base64.b64encode(b'not gzip').decode()
            with self.subTest(mutation=mutation), self.assertRaises(cf.CashFlowInputError):
                aapl.deserialize(json.dumps(d))

    def test_closed_immutable_registry_and_no_msft_contract_transfer(self):
        with patch.object(aapl, '_REGISTRY_SHA256', '0' * 64), self.assertRaises(cf.CashFlowInputError):
            aapl.registered_bundle_ids()
        self.assertEqual(self.payload['contract'], 'reviewed-aapl-reported-cash-flow-inputs')
        self.assertEqual(cf.registered_bundle_ids(),
                         ('msft-reported-cash-flow-fy2025', 'msft-reported-cash-flow-fy2026'))
        with self.assertRaises(cf.CashFlowInputError):
            cf.deserialize(json.dumps(self.payload))
        with self.assertRaises(cf.CashFlowInputError):
            cf.serialize(self.bundle)
        with self.assertRaises(FrozenInstanceError):
            self.bundle.version = '2'
        text = json.dumps(self.payload)
        with self.assertRaises(cf.CashFlowInputError):
            aapl.deserialize(text.replace('"schema":', '"schema":"bad","schema":', 1))

    def test_changed_model_scope_or_role_cannot_serialize_as_reviewed(self):
        item = self.bundle.input('AllocatedShareBasedCompensationExpense')
        for change in ({'kind': cf.InputKind.ACCRUED_EXPENSE}, {'location_and_scope': 'MSFT approved cost proxy'}):
            b = replace(self.bundle, inputs=tuple(replace(i, **change) if i == item else i for i in self.bundle.inputs))
            with self.assertRaises(cf.CashFlowInputError):
                aapl.serialize(b)

    def test_model_rejects_source_identity_and_occurrence_changes(self):
        item = self.bundle.input('OperatingLeasePayments')
        o = item.occurrences[0]
        for change in ({'context_id': 'c-18'}, {'ordinal': 1024}, {'unit_id': 'broken'},
                       {'start': date(2023, 10, 1)}, {'entity_cik': 789019}, {'decimals': '-6'},
                       {'nil': True}, {'dimensions': ('Axis=Member',)}, {'normalized_unit': 'EUR'}):
            with self.subTest(change=change), self.assertRaises(cf.CashFlowInputError):
                changed = replace(item, occurrences=(replace(o, **change),))
                replace(self.bundle, inputs=tuple(changed if i == item else i for i in self.bundle.inputs))

    def test_pinned_inventory_manifest_and_original_metadata_are_mandatory(self):
        for change in ('inventory_sha256', 'artifact_manifest_sha256'):
            doc = aapl._registry(); doc[change] = '0' * 64
            with patch.object(aapl, '_registry', return_value=doc), self.assertRaises(cf.CashFlowInputError):
                aapl.load_aapl_bundle('aapl-reported-cash-flow-fy2025')
        doc = aapl._registry(); doc['bundles'][0]['artifacts'][0]['retrieved_at_utc'] = '2026-10-12T00:00:00+00:00'
        with patch.object(aapl, '_registry', return_value=doc), self.assertRaises(cf.CashFlowInputError):
            aapl.load_aapl_bundle('aapl-reported-cash-flow-fy2025')

    def test_original_msft_serialized_identity_and_models_unchanged(self):
        for key, digest in (
            ('msft-reported-cash-flow-fy2025', '1d8f27c0f40d31cb31e2f592013416189b1c92b5d68f45fcd98d9e0456aacfad'),
            ('msft-reported-cash-flow-fy2026', '2dc19075d695bac0fe4755732f70cafbab7dd5b0e055b77c857f949e0cfd08ba')):
            bundle = cf.load_msft_bundle(key)
            self.assertEqual(hashlib.sha256(cf.serialize(bundle).encode()).hexdigest(), digest)
            with self.assertRaises(cf.CashFlowInputError):
                aapl.serialize(bundle)


if __name__ == '__main__':
    unittest.main()
