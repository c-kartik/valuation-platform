import copy
from dataclasses import replace
from datetime import date
from decimal import Decimal, localcontext
import hashlib
import json
import unittest
from unittest.mock import patch

from valuation_platform.analyst import googl_cash_flow_inputs as g
from valuation_platform.analyst import cash_flow_inputs as cf
from valuation_platform.analyst import aapl_cash_flow_inputs as a


class AlphabetReportedInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = g.load_googl_bundle('googl-reported-cash-flow-fy2024')
        cls.payload = json.loads(g.serialize(cls.b))

    def test_exact_registration(self):
        self.assertEqual(g.registered_bundle_ids(), ('googl-reported-cash-flow-fy2024',))
        self.assertEqual((self.b.period.cik, self.b.period.accession,
                          self.b.period.annual_start, self.b.period.annual_end),
                         (1652044, '0001652044-25-000014', date(2024, 1, 1), date(2024, 12, 31)))
        for name in ('GOOG', 'googl-reported-cash-flow-fy2023', 'googl-reported-cash-flow-fy2025'):
            with self.assertRaises(cf.CashFlowInputError):
                g.load_googl_bundle(name)

    def test_inputs_precision_and_roles(self):
        for name, value in (('NetCashProvidedByUsedInOperatingActivities', 125299000000),
                            ('PaymentsToAcquirePropertyPlantAndEquipment', 52535000000),
                            ('IncomeTaxesPaidNet', 27400000000),
                            ('ShareBasedCompensation', 22785000000),
                            ('AllocatedShareBasedCompensationExpense', 22800000000)):
            self.assertEqual(self.b.input(name).value_usd, Decimal(value))
        self.assertEqual(self.b.input('ShareBasedCompensation').kind, cf.InputKind.RECONCILIATION)
        expense = self.b.input('AllocatedShareBasedCompensationExpense')
        self.assertEqual(expense.kind, cf.InputKind.NONCASH_EXPENSE)
        self.assertEqual(expense.occurrences[0].decimals, '-8')
        self.assertEqual(self.b.input('ShareBasedCompensation').occurrences[0].decimals, '-6')
        self.assertNotIn(expense.input_id, self.b.cfo_terms)
        self.assertEqual(self.b.input('InterestExpenseNonoperating').kind, cf.InputKind.ACCRUED_EXPENSE)
        self.assertEqual(self.b.input('RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability').kind,
                         cf.InputKind.NONCASH_ADDITION)

    def test_reported_bridge_only(self):
        self.assertEqual(len(self.b.cfo_terms), 13)
        with localcontext() as ctx:
            ctx.prec = 3
            self.assertTrue(self.b.cfo_reconciles)
        self.assertEqual(self.b.input('OtherNoncashIncomeExpense').displayed_value_usd, Decimal(3419000000))
        with self.assertRaises(cf.CashFlowInputError):
            replace(self.b, cfo_terms=self.b.cfo_terms[:-1])
        self.assertFalse(self.b.valuation_consumption_approved)
        self.assertFalse(self.b.is_complete_operating_nwc)
        self.assertFalse(hasattr(self.b, 'fcff'))

    def test_all_occurrences_and_unknowns(self):
        self.assertEqual((len(self.b.inputs), sum(len(i.occurrences) for i in self.b.inputs)), (34, 38))
        self.assertEqual(tuple(o.ordinal for o in self.b.input('NetIncomeLoss').occurrences), (571, 580, 682, 692))
        for i in self.b.inputs:
            for o in i.occurrences:
                self.assertEqual((o.context_id, o.normalized_unit, o.dimensions, o.nil), ('c-1', 'USD', (), False))
                self.assertEqual(o.end, date(2024, 12, 31))
        self.assertEqual(len(self.b.unknowns), 12)
        for u in self.b.unknowns:
            self.assertIsNone(u.value_usd)
            with self.assertRaises(cf.CashFlowInputError):
                replace(u, value_usd=Decimal(0))

    def test_refresh_not_original_metadata_recovery(self):
        history = self.payload['evidence_history']
        self.assertIsNone(history['original_instance']['retrieved_at_utc'])
        self.assertIsNone(history['original_instance']['http_status'])
        fresh = self.b.artifacts[1]
        self.assertEqual(fresh.retrieved_at_utc, '2026-10-11T21:10:46.050735+00:00')
        self.assertEqual(fresh.http_status, 200)
        self.assertEqual(fresh.artifact.sha256, history['original_instance']['sha256'])
        self.assertEqual(hashlib.sha256(fresh.artifact.body).hexdigest(), fresh.artifact.sha256)
        self.assertEqual(g.deserialize(g.serialize(self.b)), self.b)

    def test_history_and_receipt_tampering(self):
        for mutation in ('old_time', 'old_status', 'history_removed', 'fresh_time', 'fresh_digest', 'contract'):
            d = copy.deepcopy(self.payload)
            if mutation == 'old_time': d['evidence_history']['original_instance']['retrieved_at_utc'] = self.b.artifacts[1].retrieved_at_utc
            elif mutation == 'old_status': d['evidence_history']['original_instance']['http_status'] = 200
            elif mutation == 'history_removed': del d['evidence_history']
            elif mutation == 'fresh_time': d['artifacts'][1]['retrieved_at_utc'] = '2026-10-12T00:00:00+00:00'
            elif mutation == 'fresh_digest': d['artifacts'][1]['sha256'] = '0' * 64
            else: d['contract'] = 'reviewed-aapl-reported-cash-flow-inputs'
            with self.subTest(mutation=mutation), self.assertRaises(cf.CashFlowInputError):
                g.deserialize(json.dumps(d))

    def test_value_role_occurrence_precision_and_unknown_tampering(self):
        for field, value in (('kind', 'cash_payment'), ('value_usd', '0'), ('location_and_scope', 'complete operating cash')):
            d = copy.deepcopy(self.payload); d['bundle']['inputs'][0][field] = value
            with self.assertRaises(cf.CashFlowInputError): g.deserialize(json.dumps(d))
        for field, value in (('decimals', 'INF'), ('ordinal', 0), ('nil', True), ('normalized_unit', 'EUR'), ('dimensions', ['Axis=Member'])):
            d = copy.deepcopy(self.payload); d['bundle']['inputs'][0]['occurrences'][0][field] = value
            with self.assertRaises(cf.CashFlowInputError): g.deserialize(json.dumps(d))
        d = copy.deepcopy(self.payload); d['bundle']['unknowns'][0]['value_usd'] = '0'
        with self.assertRaises(cf.CashFlowInputError): g.deserialize(json.dumps(d))

    def test_pinned_evidence_and_registry(self):
        with patch.object(g, '_REGISTRY_SHA256', '0' * 64), self.assertRaises(cf.CashFlowInputError):
            g.registered_bundle_ids()
        doc = g._registry(); doc['refresh_manifest_sha256'] = '0' * 64
        with patch.object(g, '_registry', return_value=doc), self.assertRaises(cf.CashFlowInputError):
            g.load_googl_bundle(self.b.bundle_id)

    def test_no_other_contract_transfer(self):
        for adapter in (cf, a):
            with self.assertRaises(cf.CashFlowInputError): adapter.deserialize(g.serialize(self.b))
            with self.assertRaises(cf.CashFlowInputError): adapter.serialize(self.b)
        self.assertEqual(cf.registered_bundle_ids(), ('msft-reported-cash-flow-fy2025', 'msft-reported-cash-flow-fy2026'))
        self.assertEqual(a.registered_bundle_ids(), ('aapl-reported-cash-flow-fy2025',))

    def test_msft_serialized_bytes_preserved(self):
        for year, digest in ((2025, '1d8f27c0f40d31cb31e2f592013416189b1c92b5d68f45fcd98d9e0456aacfad'),
                             (2026, '2dc19075d695bac0fe4755732f70cafbab7dd5b0e055b77c857f949e0cfd08ba')):
            b = cf.load_msft_bundle(f'msft-reported-cash-flow-fy{year}')
            self.assertEqual(hashlib.sha256(cf.serialize(b).encode()).hexdigest(), digest)
