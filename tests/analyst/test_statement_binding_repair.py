"""Literal independent statements and fail-closed shared repair regressions."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import sys
import unittest
from valuation_platform.analyst import statement_delivery as s, historical_inputs as h
from valuation_platform.analyst import retained_components as r, cfo_statement_reconciliation as c
from valuation_platform.analyst import usable_bridge as b
sys.path.insert(0,str(s.ROOT/'scripts'))
import repair_preparation_statement_bindings as acquisition


class StatementBindingRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope,cls.catalog,_=s.scope();cls.records=s.repaired_records(cls.scope,cls.catalog)
        cls.evidence={}

    def source(self,accession):
        if accession not in self.evidence:
            identity=next(x['identity'] for x in self.scope if x['identity']['accession']==accession)
            from datetime import date
            p=h.Period(identity['cik'],accession,date.fromisoformat(identity['annual_start']),date.fromisoformat(identity['annual_end']),'10-K')
            inst=next(x for x in self.catalog if accession.replace('-','') in x['url'] and x['url'].endswith('_htm.xml'))
            receipt=s.receipt(inst,p)
            self.evidence[accession]=r.prepare(p,(receipt,),(r.ArtifactBinding(inst['url'],inst['sha256'],'instance'),))
        return self.evidence[accession],self.records[accession]

    def test_exact_eighteen_acquisition_receipts_and_index_replay(self):
        payload=json.loads((s.ROOT/acquisition.OUTPUT).read_text())
        self.assertEqual(acquisition.verify(payload),dict(targets=18,requests=36,bound=18))
        self.assertEqual(len({a['source_url'] for a in payload['attempts']}),36)
        self.assertTrue(all(a['http_status']==200 for a in payload['artifacts']))
        changed=copy.deepcopy(payload);changed['rows'][0]['identity']['annual_end']='2022-12-31'
        with self.assertRaises(ValueError):acquisition.verify(changed)
        changed=copy.deepcopy(payload);changed['artifacts'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):acquisition.verify(changed)

    def test_index_preserves_html_and_pdf_without_guessing_primary(self):
        payload=json.loads((s.ROOT/acquisition.OUTPUT).read_text())
        row=next(x for x in payload['rows'] if x['ticker']=='MCD')
        raw=next(x['body'] for x in self.catalog if x['url']==row['index']['url'])
        docs=s.index_documents(raw,63908,row['identity']['accession'])
        self.assertEqual(len([x for x in docs if x['type']=='10-K']),2)
        self.assertEqual([x['url'] for x in docs if x['type']=='10-K' and x['url'].endswith('.htm')],[row['primary']['url']])
        self.assertFalse(s.index_documents(raw,1,row['identity']['accession']))

    def test_explicit_split_parentheses_not_inferred_sign(self):
        record=dict(body=b'<table><tr><td><ix:nonFraction name="a:b">17</ix:nonFraction></td></tr><tr><td>(<ix:nonFraction name="a:b">18</ix:nonFraction></td><td>)</td></tr></table>')
        table=s.parse(record,improved=True)[0]
        self.assertEqual(table[0][0]['text'],'17')
        self.assertEqual(table[1][0]['text'],'(18)')
        self.assertEqual(table[1][0]['split_sign_cells'],[0,1])
        record['body']=record['body'].replace(b'<td>)</td>',b'<td>19</td>')
        with self.assertRaises(h.InputError):c.displayed(s.parse(record,improved=True)[0][1][0]['text'],Decimal(18))

    def test_msft_displayed_cash_contributions_and_precision_are_independent(self):
        e,record=self.source('0000950170-25-100235')
        result=c.inspect_statement(e,record,c.IMPROVED_VERSION)
        self.assertEqual(result['status'],'SUPPORTED')
        population=result['populations'][0]
        # Existing independent MSFT cash-flow evidence review: USD millions,
        # statement annual CFO 136162; deferred-tax contribution -7056.
        self.assertEqual(population['cfo']['value'],'136162000000')
        deferred=next(x for x in population['rows'] if x['concept']=='DeferredIncomeTaxExpenseBenefit')
        self.assertEqual(deferred['value'],'-7056000000')
        self.assertTrue(deferred['split_sign_cells'])
        self.assertEqual(population['difference'],'0')

    def test_displayed_wmt_addback_is_not_an_expense_scope_approval(self):
        e,record=self.source('0000104169-26-000055')
        result=c.inspect_statement(e,record,c.IMPROVED_VERSION)
        self.assertEqual(result['status'],'SUPPORTED')
        p=result['populations'][0]
        # Exact primary table 50 rows 6 and 18, USD millions; not assembly output.
        self.assertEqual(record['sha256'],'56a629bb262bef520f4ef1987b1f94931a210b8a620989092890d092afdf9e8d')
        self.assertEqual(p['cfo']['value'],'41565000000')
        row=next(x for x in p['rows'] if x['concept']=='DepreciationAmortizationAndAccretionNet')
        self.assertEqual(row['value'],'14203000000')
        self.assertTrue(row['competing_occurrences'])
        self.assertIn('no primitive',row['display_selection'])

    def test_explicit_adjustment_hierarchy_not_parent_plus_children(self):
        e,record=self.source('0000050863-22-000007')
        result=c.inspect_statement(e,record,c.IMPROVED_VERSION)
        p=result['populations'][0]
        # Exact independently inspected primary table 193, rows 4/23/24.
        self.assertEqual(record['sha256'],'ab98e524a4adc1ffa57c573dc6c0261da294aff2e8836155ca48e8306cd12d1a')
        self.assertEqual(result['status'],'SUPPORTED')
        self.assertEqual([x['value'] for x in p['rows']],['19868000000','10123000000'])
        self.assertEqual(p['cfo']['value'],'29991000000')
        self.assertEqual(p['hierarchy_proof']['status'],'SUPPORTED')
        self.assertGreater(len(p['hierarchy_proof']['children']),2)

    def test_incorporated_ibm_contexts_and_exact_document_binding(self):
        e,record=self.source('0000051143-26-000010')
        result=c.inspect_statement(e,record,c.IMPROVED_VERSION)
        self.assertEqual(record['document_type'],'EX-13')
        self.assertEqual(record['sha256'],'6ed07e3f17d0e22539962f1d9bda5e7d8c0f1d4260ba64473062ee217b4ed95c')
        self.assertEqual(result['status'],'SUPPORTED')
        self.assertEqual(result['populations'][0]['cfo']['value'],'13193000000')
        self.assertEqual(len(result['populations'][0]['cfo']['document_binding']['metadata']),2)
        self.assertFalse(any(x.source_id.startswith('statement-binding:') for x in result['populations'][0]['cfo']['sources']))
        changed=dict(record,selected_identity={**record['selected_identity'],'annual_end':'2024-12-31'})
        with self.assertRaises(h.InputError):c.inspect_statement(e,changed,c.IMPROVED_VERSION)
        changed=dict(record,body=record['body']+b' ')
        with self.assertRaises(h.InputError):c.inspect_statement(e,changed,c.IMPROVED_VERSION)
        changed=dict(record,index_record={**record['index_record'],'body':record['index_record']['body']+b' '})
        with self.assertRaises(h.InputError):c.inspect_statement(e,changed,c.IMPROVED_VERSION)

    def test_unsupported_hierarchy_remains_partial_not_residual_certified(self):
        e,record=self.source('0001628280-26-011430')
        self.assertEqual(c.inspect_statement(e,record,c.IMPROVED_VERSION)['status'],'PARTIAL')
        e,record=self.source('0001321655-25-000022')
        self.assertEqual(c.inspect_statement(e,record,c.IMPROVED_VERSION)['status'],'PARTIAL')

    def test_unmatched_display_and_ambiguous_nesting_fail_closed(self):
        e,record=self.source('0000104169-26-000055')
        table=s.parse(record,improved=True)[50]
        cell=next(x for x in table[6] if any(i['attrs'].get('contextref')=='c-1' for i in x['facts']))
        item=copy.deepcopy(next(i for i in cell['facts'] if i['attrs'].get('contextref')=='c-1'))
        item['text']='14,204'
        with self.assertRaises(h.InputError):c.bind_inline(e,record,50,6,cell,item,reviewed_display=True)
        parsed=s.parse(dict(body=b'<table><tr><td><ix:nonFraction name="us-gaap:ProfitLoss"><ix:nonFraction name="us-gaap:NetIncomeLoss">5</ix:nonFraction></ix:nonFraction></td></tr></table>'),improved=True)
        self.assertEqual([x['text'] for x in parsed[0][0][0]['facts']],['5','5'])
        self.assertEqual(parsed[0][0][0]['facts'][1]['nested_parent'],'us-gaap:ProfitLoss')

    def test_mcd_literal_display_failure_is_not_hidden_or_tolerance_widened(self):
        e,record=self.source('0000063908-25-000012')
        result=c.inspect_statement(e,record,c.IMPROVED_VERSION);p=result['populations'][0]
        self.assertEqual(result['status'],'FAILED')
        # Independently bound statement: 9446m leaf sum versus 9447m CFO;
        # twelve reported -5 precision amounts imply the unchanged 0.6m bound.
        self.assertEqual((p['difference'],p['tolerance'],p['cfo']['value']),('-1000000','600000','9447000000'))

    def test_explicit_current_noncurrent_partition_not_equal_values(self):
        e,record=self.source('0000950170-22-000796')
        result=c.inspect_statement(e,record,c.IMPROVED_VERSION);p=result['populations'][0]
        self.assertEqual(result['status'],'SUPPORTED')
        self.assertEqual(p['cfo']['value'],'11497000000')
        self.assertTrue(p['non_overlap_evidence']['taxonomy_possible_pairs'])
        self.assertFalse(p['non_overlap_evidence']['unresolved_pairs'])
        rows=[dict(namespace='http://fasb.org/us-gaap/2021',concept='IncreaseDecreaseInPrepaidDeferredExpenseAndOtherAssets',caption='Other assets'),
              dict(namespace='http://fasb.org/us-gaap/2021',concept='IncreaseDecreaseInOtherNoncurrentAssets',caption='Other non-current assets')]
        self.assertTrue(c.movement_overlap(rows,display_scope=True))
        rows[0]['caption']='Other current and noncurrent assets'
        self.assertTrue(c.movement_overlap(rows,display_scope=True))

    def test_competing_borrowing_preserves_prior_partial_target_not_a_total(self):
        e,record=self.source('0000097476-22-000009')
        values,proof=b.inspect(e,record,b.IMPROVED_VERSION)
        borrowing=[v for v in values if v.role=='reported_borrowing_total']
        self.assertEqual(len(borrowing),2)
        original=next(v for v in borrowing if v.input_id=='usable-bridge:reported_borrowing_total:1787')
        self.assertEqual(original.value,Decimal('7800000000'))
        self.assertTrue(all(v.completeness is h.Completeness.PARTIAL and v.scope_status is h.Scope.UNKNOWN for v in borrowing))
        self.assertTrue(all('competing_borrowing_populations' in v.flags for v in borrowing))
        self.assertTrue(any('Competing borrowing' in v for v in proof['requirements']))

    def test_complete_fixed_disposition_count_and_reopened_scope(self):
        p=json.loads((s.ROOT/'docs/statement-repair-disposition.json').read_text())
        self.assertEqual(len(p['rows']),59)
        self.assertEqual(len({r['identity']['fields']['accession'] for r in p['rows']}),59)
        self.assertEqual(p['prior_partial_final_counts'],{'SUPPORTED':35,'PARTIAL':24})
        self.assertEqual(len(p['binding_targets']),18)
        self.assertEqual(p['preserved_prior_population_input_count'],2487)


if __name__=='__main__':unittest.main()
