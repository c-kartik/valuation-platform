"""Independent source expectations, not numbers obtained from assembled output."""
from dataclasses import replace
from decimal import Decimal
import copy
import hashlib
import json
import unittest

from valuation_platform.analyst import historical_inputs as h, statement_delivery as s
from valuation_platform.analyst import pilot_historical_inputs as pilot, retained_components as r
from valuation_platform.analyst import cfo_statement_reconciliation as cfo, usable_bridge as bridge
from valuation_platform.analyst import preparation_delivery as delivery


class StatementDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=pilot._SOURCES['aapl-reported-cash-flow-fy2025'][2]('aapl-reported-cash-flow-fy2025')
        cls.e=r.prepare(source.period,source.artifacts,tuple(r.ArtifactBinding(a.artifact.url,a.artifact.sha256,
            'instance' if a.artifact.url.endswith('_htm.xml') else 'support') for a in source.artifacts))
        catalog,_=s.records()
        cls.record=next(a for a in catalog if a['url']=='https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm')
        cls.checked=cfo.inspect_statement(cls.e,cls.record)
        cls.values,cls.proof=bridge.inspect(cls.e,cls.record)

    def test_independent_aapl_display_all_ten_operands_and_cfo(self):
        p=self.checked['populations'][0]
        # Primary cash-flow statement, table 26 rows 6..18, USD millions.
        expected=('112010','11698','12863','-89','-6682','-347','1400','-9197','902','-11076')
        self.assertEqual([v['value'] for v in p['rows']],[str(Decimal(v)*1000000) for v in expected])
        self.assertEqual(p['cfo']['value'],'111482000000')
        self.assertEqual((self.checked['status'],p['difference'],p['tolerance']),('SUPPORTED','0','5500000'))
        self.assertEqual(self.record['sha256'],'b0dbcbbd800fd1c819007d63d884a1f8b9a5994486d0b2974a4b5b8a6e6eb80e')
        self.assertTrue(all(len(v['sources'])>=2 for v in p['rows']))

    def test_display_inventory_sign_is_not_taxonomy_debit_sign(self):
        v=next(v for v in self.checked['populations'][0]['rows'] if v['concept']=='IncreaseDecreaseInInventories')
        self.assertEqual((v['raw'],v['sign'],v['value']),('-1400000000',-1,'1400000000'))

    def test_precision_bound_not_percentage_and_no_residual_validation(self):
        p=self.checked['populations'][0];rows=copy.copy(p['rows'])
        rows[0]=dict(rows[0],value=str(Decimal(rows[0]['value'])+6000000))
        self.assertEqual(cfo.check_rows(rows,p['cfo'],complete=True,non_overlapping=True,scope='CONSOLIDATED')['status'],'FAILED')
        self.assertEqual(cfo.check_rows(rows,p['cfo'],complete=False,non_overlapping=True,scope='CONSOLIDATED')['status'],'PARTIAL')
        with self.assertRaises(h.InputError):cfo.check_rows([*p['rows'],p['rows'][0]],p['cfo'],complete=True,non_overlapping=True,scope='CONSOLIDATED')
        self.assertEqual(cfo.uncertainty('INF'),0)
        with self.assertRaises(h.InputError):cfo.uncertainty('unknown')
        self.assertEqual(cfo.display_scale('-2'),Decimal('0.01'))
        self.assertEqual(Decimal('123')*cfo.display_scale('-2'),Decimal('1.23'))

    def test_independent_current_liquidity_not_parent_plus_children(self):
        values={v.role:v for v in self.values}
        self.assertEqual(values['cash_equivalents_reported'].value,Decimal('35934000000'))
        self.assertEqual(values['current_marketable_reported'].value,Decimal('18763000000'))
        total=values['reported_current_liquidity']
        self.assertEqual(total.value,Decimal('54697000000'))
        self.assertEqual(len(total.formula.operands),2)
        self.assertTrue(total.formula.complete_coverage and total.formula.non_overlapping)
        self.assertFalse(any(v.role=='reported_borrowing_total' for v in self.values))

    def test_independent_lease_liabilities_are_not_lease_cash_service(self):
        values={v.role:v for v in self.values}
        self.assertEqual(values['reported_finance_lease_liability'].value,Decimal('1230000000'))
        self.assertEqual(values['reported_operating_lease_liability'].value,Decimal('12490000000'))
        self.assertEqual(values['reported_finance_lease_liability'].as_of,self.e.period.annual_end)
        self.assertIn('not undiscounted payments',values['reported_finance_lease_liability'].scope)

    def test_shares_actual_cover_date_not_year_end_or_diluted(self):
        v=next(v for v in self.values if v.role=='issuer_common_shares')
        self.assertEqual(str(v.as_of),'2025-10-17')
        self.assertEqual(v.value,Decimal('14776353000'))
        self.assertNotEqual(v.as_of,self.e.period.annual_end)
        self.assertEqual(v.unit,'shares');self.assertIsNone(v.formula)

    def test_overlapping_or_incomplete_components_cannot_total(self):
        a=next(v for v in self.values if v.role=='cash_equivalents_reported')
        with self.assertRaises(h.InputError):bridge.total((a,a),h.Field.CASH_INVESTMENTS,'invalid','overlap')
        with self.assertRaises(h.InputError):bridge.total((replace(a,completeness=h.Completeness.PARTIAL),),a.field,'invalid','partial')

    def test_primary_identity_dates_and_units_checked_independently(self):
        identity=dict(cik=self.e.period.cik,accession=self.e.period.accession,annual_start=str(self.e.period.annual_start),annual_end=str(self.e.period.annual_end))
        self.assertTrue(s.verify_primary(self.record,identity))
        with self.assertRaises(h.InputError):s.verify_primary(self.record,dict(identity,annual_end='2025-09-28'))
        with self.assertRaises(h.InputError):s.verify_primary(self.record,dict(identity,cik=1))
        p=self.checked['populations'][0]['rows'][0]
        bindings=s.primary_bindings(self.record)
        attrs=dict(name='us-gaap:'+p['concept'],contextref=p['context_id'],unitref='no-unit')
        f=next(f for f,i in self.e.facts if i==p['ordinal'])
        with self.assertRaises(h.InputError):s.check_primary_binding(bindings,attrs,p['namespace'],self.e.contexts[p['context_id']],f.unit)

    def test_inline_sign_mismatch_rejected_not_equal_absolute_value(self):
        tables=s.parse(self.record);p=self.checked['populations'][0]['rows'][0]
        cell=next(c for c in tables[p['table']][p['row']] if any(i['attrs'].get('contextref')==p['context_id'] for i in c['facts']))
        item=copy.deepcopy(next(i for i in cell['facts'] if i['attrs'].get('contextref')==p['context_id']))
        item['attrs']['sign']='-'
        with self.assertRaises(h.InputError):cfo.bind_inline(self.e,self.record,p['table'],p['row'],cell,item)
        item['attrs'].pop('sign');item['attrs']['decimals']='INF'
        with self.assertRaises(h.InputError):cfo.bind_inline(self.e,self.record,p['table'],p['row'],cell,item)

    def test_missing_statement_not_assessed_and_no_inferred_zero(self):
        self.assertEqual(cfo.inspect_statement(self.e,None)['status'],'NOT_ASSESSED')
        values,proof=bridge.inspect(self.e,None)
        self.assertEqual(values,());self.assertTrue(proof['requirements'])

    def test_income_bridge_parent_is_not_an_additive_adjustment(self):
        self.assertIn('IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest',cfo.INCOME_PARENTS)
        self.assertNotIn('NetIncomeLossAttributableToNoncontrollingInterest',cfo.INCOME_PARENTS)

    def test_explicit_movement_parent_children_are_not_a_leaf_sum(self):
        rows=[dict(namespace='http://fasb.org/us-gaap/2025',concept=c) for c in ('IncreaseDecreaseInReceivables','IncreaseDecreaseInAccountsReceivable')]
        self.assertTrue(cfo.movement_overlap(rows))
        self.assertFalse(cfo.movement_overlap(rows[1:]))

    def test_extension_local_name_cannot_gain_standard_population_semantics(self):
        row=copy.copy(self.checked['populations'][0]['rows'][0])
        row.update(namespace='https://example.test/issuer',concept='CashAndCashEquivalentsAtCarryingValue')
        self.assertIsNone(bridge.unique([row],row['concept'],h.Field.CASH_INVESTMENTS,'cash','unreviewed'))

    def test_multiclass_cover_is_not_one_class_or_an_automatic_sum(self):
        source=pilot._SOURCES['googl-reported-cash-flow-fy2024'][2]('googl-reported-cash-flow-fy2024')
        e=r.prepare(source.period,source.artifacts,tuple(r.ArtifactBinding(a.artifact.url,a.artifact.sha256,
            'instance' if a.artifact.url.endswith('_htm.xml') else 'support') for a in source.artifacts))
        primary=next(a for a in source.artifacts if a.artifact.url.endswith('.htm'))
        record=dict(url=primary.artifact.url,sha256=primary.artifact.sha256,body=primary.artifact.body,
            retrieved_at_utc=primary.retrieved_at_utc,http_status=200,path='existing-reviewed-bundle',locator='primary')
        values,proof=bridge.inspect_shares(e,record)
        self.assertFalse(values);self.assertTrue(proof['class_dimensions']);self.assertTrue(proof['requirements'])

    def test_prior_current_liquidity_note_is_exact_not_a_generic_short_term_rule(self):
        source=pilot._SOURCES['msft-reported-cash-flow-fy2025'][2]('msft-reported-cash-flow-fy2025')
        e=r.prepare(source.period,source.artifacts,tuple(r.ArtifactBinding(a.artifact.url,a.artifact.sha256,
            'instance' if a.artifact.url.endswith('_htm.xml') else 'support') for a in source.artifacts))
        primary=next(a for a in source.artifacts if a.artifact.url.endswith('.htm'))
        record=dict(url=primary.artifact.url,sha256=primary.artifact.sha256,body=primary.artifact.body,
            retrieved_at_utc=primary.retrieved_at_utc,http_status=200,path='existing-reviewed-bundle',locator='primary')
        proof=bridge.reviewed_current_scope(e,record)
        self.assertIsNotNone(proof);self.assertIn('highly liquid nature',proof['excerpt'])
        self.assertIsNone(bridge.reviewed_current_scope(e,dict(record,sha256='0'*64)))

    def test_remainder_is_explicit_partial_and_not_validation_proof(self):
        inputs=delivery.reconciliation_inputs(self.checked,self.e.period)
        v=next(v for v in inputs if v.formula)
        self.assertEqual(v.formula.kind,h.FormulaKind.CFO_REMAINDER)
        self.assertEqual(v.field,h.Field.CFO_RESIDUAL)
        self.assertEqual(v.completeness,h.Completeness.PARTIAL)
        self.assertIn('not_independent_validation',v.flags)
        self.assertEqual(v.value,Decimal('-89000000'))
        self.assertEqual(delivery.reconciliation_inputs(dict(self.checked,status='PARTIAL'),self.e.period),())


if __name__=='__main__':unittest.main()
