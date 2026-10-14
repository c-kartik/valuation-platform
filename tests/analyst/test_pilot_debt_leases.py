"""Independent retained statement values and liability population boundaries."""

import copy
from dataclasses import replace
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace
import unittest
from tests.analyst.preparation_preservation import assert_preserved
from unittest.mock import patch

from valuation_platform.analyst import pilot_debt_leases as d, pilot_historical_inputs as p, historical_inputs as h
from valuation_platform.sec.filing_xbrl import FilingXBRLDataError
from valuation_platform.analyst.cash_flow_inputs import CashFlowInputError

ROOT = Path(__file__).resolve().parents[2]


class DebtLeaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {bid:load(bid) for bid,(_,_,load) in p._SOURCES.items()}
        # Independently transcribed balance-sheet/debt/lease-note amounts in USD millions.
        cls.expected = {
            'msft-reported-cash-flow-fy2025': (0,2999,40152,43151,49206,40400,3000,22861,5424,17437,46172,3172,43000,25481,60506),
            'msft-reported-cash-flow-fy2026': (None,9227,31067,40294,46136,36500,9250,21925,5393,16532,66594,4290,62304,24706,89686),
            'aapl-reported-cash-flow-fy2025': (7979,12350,78328,90678,91281,80400,12393,12490,1579,10911,1230,538,692,14725,1579,13720),
            'googl-reported-cash-flow-fy2024': (2300,999,10883,10883,12000,9000,1000,14578,2887,11691,1677,235,1442,17038,1888)}

    def mutation(self, transform):
        original=self.sources['aapl-reported-cash-flow-fy2025']
        receipt=next(r for r in original.artifacts if r.artifact.url.endswith('_htm.xml'))
        body=transform(receipt.artifact.body.decode()).encode()
        artifact=replace(receipt.artifact,body=body,sha256=hashlib.sha256(body).hexdigest())
        changed=replace(receipt,artifact=artifact,byte_length=len(body))
        source=SimpleNamespace(bundle_id=original.bundle_id,period=original.period,
            artifacts=tuple(changed if r==receipt else r for r in original.artifacts))
        review=copy.deepcopy(d.review_for(original));review['instance_sha256']=artifact.sha256
        return source,review

    def fact(self, body):
        return re.search(r'<us-gaap:LongTermDebtCurrent\b[^>]*contextRef="c-20"[^>]*>.*?</us-gaap:LongTermDebtCurrent>',body).group()

    def test_independent_values_and_primary_display_reconciliation(self):
        for bid,source in self.sources.items():
            review,components=d.inspect(source)
            self.assertEqual(len(components),len(self.expected[bid]))
            for component,millions in zip(components,self.expected[bid]):
                if millions is None:
                    self.assertIsNone(component.selected);self.assertFalse(component.candidates);continue
                expected=Decimal(str(millions)+'e6')
                self.assertEqual(component.candidates[component.selected].value,expected)
                for tag in component.spec['statements']:
                    display=Decimal(tag['displayed_value'].replace(',','')+'e'+tag['attributes']['scale'])
                    self.assertEqual(display,expected)
                for candidate in component.candidates:
                    for o in candidate.occurrences:
                        self.assertEqual(o['end'],str(source.period.annual_end))
                        self.assertEqual(o['entity_cik'],source.period.cik)
                        self.assertEqual(o['normalized_unit'],'USD')
                        self.assertEqual(o['dimensions'],component.spec['dimensions'])

    def test_all_occurrences_roles_and_receipts_survive_adapter(self):
        for bid,source in self.sources.items():
            review,components=d.inspect(source);annual=p.load_annual(bid)
            values=[v for v in annual.inputs if v.field is h.Field.DEBT_LEASES]
            self.assertEqual(len(values),len(components)+len(review['unknowns']))
            for c,v in zip(components,values):
                observations=(v,*v.alternatives) if v.value is not None else v.alternatives
                self.assertEqual(len(observations),len(c.candidates))
                for a,observed in zip(c.candidates,observations):
                    refs=[s for s in observed.sources if s.occurrence_ordinal is not None]
                    self.assertEqual([s.occurrence_ordinal for s in refs],[o['ordinal'] for o in a.occurrences])
                    self.assertEqual(observed.role,c.spec['role'])
                    self.assertEqual(observed.precision,a.precision)
                    self.assertEqual(observed.as_of,annual.period.annual_end)
                    for ref,o in zip(refs,a.occurrences):
                        self.assertIn(ref.receipt,source.artifacts)
                        self.assertEqual(ref.dimensions,tuple(o['dimensions']))
                        self.assertEqual(ref.raw_value,o['raw_value'])

    def test_location_dimensions_not_generic_issuer_or_segment_approval(self):
        for bid in ('msft-reported-cash-flow-fy2025','msft-reported-cash-flow-fy2026'):
            _,components=d.inspect(self.sources[bid]);by={c.spec['component_id']:c for c in components}
            for cid in ('operating_lease_current','finance_lease_current','finance_lease_noncurrent'):
                self.assertEqual(len(by[cid].spec['dimensions']),1)
                self.assertIn('BalanceSheetLocationAxis',by[cid].spec['dimensions'][0])
            self.assertFalse(by['finance_lease_total'].spec['dimensions'])
        source,review=self.mutation(lambda body:body.replace('<us-gaap:LongTermDebtCurrent contextRef="c-20"','<us-gaap:LongTermDebtCurrent contextRef="c-74"'))
        c=next(c for c in d.inspect(source,review)[1] if c.spec['component_id']=='current_debt')
        self.assertIsNone(c.selected)

    def test_principal_carrying_fair_value_maturity_and_lease_cash_are_separate(self):
        for source in self.sources.values():
            _,components=d.inspect(source);by={c.spec['component_id']:c for c in components}
            self.assertIn('principal',by['debt_principal'].spec['role'])
            self.assertIn('fair_value',by['debt_fair_value'].spec['role'])
            self.assertIn('maturity',by['principal_due_next_year'].spec['role'])
            self.assertIn('undiscounted',by['finance_lease_undiscounted'].spec['role'])
            self.assertIn('finance_lease_total',by['finance_lease_current'].spec['overlap_with'])
            for v in p.load_annual(source.bundle_id).inputs:
                if v.field is h.Field.DEBT_LEASES:
                    self.assertIsNone(v.formula);self.assertIsNot(v.completeness,h.Completeness.COMPLETE)
                    if v.value is not None:self.assertIn('separate_from_lease_cash_payments',v.flags)
        google=d.inspect(self.sources['googl-reported-cash-flow-fy2024'])[1]
        parent=next(c for c in google if c.spec['component_id']=='term_debt_parent')
        self.assertIn('Do not infer finance-lease inclusion',parent.spec['scope'])

    def test_explicit_reported_zero_vs_absent_and_precision(self):
        a=d.inspect(self.sources['msft-reported-cash-flow-fy2025'])[1][0]
        self.assertEqual([(c.value,c.precision) for c in a.candidates],[(Decimal(0),'-6'),(Decimal(0),'-9')])
        self.assertIsNone(d.inspect(self.sources['msft-reported-cash-flow-fy2026'])[1][0].selected)
        google=d.inspect(self.sources['googl-reported-cash-flow-fy2024'])[1]
        self.assertEqual(google[0].candidates[0].precision,'INF')  # preserve issuer representation, not calibrated accuracy
        self.assertEqual(google[5].candidates[0].precision,'-8')
        with localcontext() as ctx:
            ctx.prec=3
            self.assertEqual(d.inspect(self.sources['aapl-reported-cash-flow-fy2025'])[1][5].candidates[0].value,Decimal('80400000000'))

    def test_confirmations_and_distinct_conflicting_candidates(self):
        source,review=self.mutation(lambda body:body.replace('</xbrl>',self.fact(body)+'</xbrl>'))
        c=next(c for c in d.inspect(source,review)[1] if c.spec['component_id']=='current_debt')
        self.assertEqual(len(c.candidates[0].occurrences),3);self.assertEqual(c.selected,0)
        source,review=self.mutation(lambda body:body.replace('</xbrl>',self.fact(body).replace('12350000000','12351000000')+'</xbrl>'))
        c=next(c for c in d.inspect(source,review)[1] if c.spec['component_id']=='current_debt')
        self.assertIsNone(c.selected);self.assertEqual(len(c.candidates),2)
        self.assertIn('conflicting',c.reason)
        with patch.object(d,'review_for',return_value=review):
            values=d.values({},source,d.mapping_entry(source))
        value=next(v for v in values if ':current_debt:' in v.input_id)
        self.assertIsNone(value.value)
        self.assertEqual([a.value for a in value.alternatives],[Decimal('12350000000'),Decimal('12351000000')])
        self.assertIs(value.quality,h.Quality.CONFLICTING)

    def test_instant_and_entity_mismatch_excludes_not_zero(self):
        for old,new in [('contextRef="c-20"','contextRef="c-1"'),('0000320193','0000789019')]:
            source,review=self.mutation(lambda body,o=old,n=new:re.sub(r'<us-gaap:LongTermDebtCurrent\b[^>]*>.*?</us-gaap:LongTermDebtCurrent>',lambda m:m.group().replace(o,n),body) if 'context' in o else body.replace(o,n))
            if 'context' in old:
                c=next(c for c in d.inspect(source,review)[1] if c.spec['component_id']=='current_debt')
                self.assertIsNone(c.selected)
            else:
                with self.assertRaises(CashFlowInputError):d.inspect(source,review)

    def test_invalid_unit_nil_precision_and_broken_context_fail(self):
        for old,new in [('unitRef="usd"','unitRef="shares"'),('decimals="-6"','decimals="bad"'),('contextRef="c-20"','contextRef="missing"'),('>12350000000',' xsi:nil="true">12350000000')]:
            source,review=self.mutation(lambda body,o=old,n=new:body.replace(self.fact(body),self.fact(body).replace(o,n)))
            with self.assertRaises((h.InputError,FilingXBRLDataError)):d.inspect(source,review)

    def test_exact_receipts_period_note_and_namespace_binding(self):
        original=self.sources['aapl-reported-cash-flow-fy2025']
        for key,bad in [('accession','wrong'),('annual_end','2025-09-28'),('form','10-K/A')]:
            review=copy.deepcopy(d.review_for(original));review['period'][key]=bad
            with self.assertRaises(h.InputError):d.inspect(original,review)
        for key in ('instance_sha256','primary_sha256'):
            review=copy.deepcopy(d.review_for(original));review[key]='0'*64
            with self.assertRaises(h.InputError):d.inspect(original,review)
        for mutation in (lambda r:r['components'][0].__setitem__('namespace','wrong'),lambda r:r['scope_notes'][0].__setitem__('text','missing note')):
            review=copy.deepcopy(d.review_for(original));mutation(review)
            with self.assertRaises(h.InputError):d.inspect(original,review)

    def test_unavailable_requirements_no_totals_or_complete_perimeter(self):
        for source in self.sources.values():
            values=[v for v in p.load_annual(source.bundle_id).inputs if v.field is h.Field.DEBT_LEASES]
            for cid in ('other_short_term_borrowing','complete_debt_lease_aggregate','unrecognized_lease_commitments'):
                value=next(v for v in values if ':'+cid+':' in v.input_id)
                self.assertIsNone(value.value);self.assertTrue(value.null_reason and value.unresolved_requirements)

    def test_mapping_tamper_and_deterministic_serialization(self):
        history=p.load_history('MSFT');payload=p.serialize(history)
        self.assertEqual(payload,p.serialize(p.deserialize(payload)))
        changed=json.loads(payload)
        value=next(v for v in changed['history']['fields']['annuals'][0]['fields']['inputs'] if v['fields']['input_id'].startswith('debt_lease:finance_lease_current:'))
        value['fields']['role']='cash_payment'
        with self.assertRaises(h.InputError):p.deserialize(json.dumps(changed))
        source=self.sources['aapl-reported-cash-flow-fy2025'];entry=d.mapping_entry(source);entry['bindings'][0]['sign']=-1
        with self.assertRaises(h.InputError):d.values({},source,entry)

    def test_other_fields_and_frozen_original_artifacts_preserved(self):
        old=json.loads(subprocess.check_output(['git','show','2b949f8bed817d2a72e06fdee3aa4e5687362f1c:docs/pilot-historical-input-mappings.json'],cwd=ROOT))
        new=json.loads(p.MAPPING_PATH.read_bytes())
        for before,after in zip(old['periods'],new['periods']):
            for key in before:
                if key!='fields':self.assertEqual(before[key],after[key])
            for field in before['fields']:
                if field!=h.Field.DEBT_LEASES.value:self.assertEqual(before['fields'][field],after['fields'][field])
        protected=['src/valuation_platform/analyst/historical_inputs.py','src/valuation_platform/normalization/balance_sheet.py',
            'docs/company-data-preparation/msft-reported-cash-flow-bundles.json','docs/company-data-preparation/aapl-reported-cash-flow-bundle.json',
            'docs/company-data-preparation/googl-reported-cash-flow-bundle.json','docs/pilot-cash-investment-evidence.json']
        for path in protected:
            # Preserve financial artifacts at their original revision; the
            # helper binds additive preparation code to its reviewed milestone.
            pin=('1220bd2ee2edaa3867de7eb7ba8066f5554a3b96' if path=='src/valuation_platform/analyst/historical_inputs.py'
                 else '2b949f8bed817d2a72e06fdee3aa4e5687362f1c')
            assert_preserved(self, ROOT, path, pin)
        for source in self.sources.values():
            self.assertFalse(source.valuation_consumption_approved)
            for receipt in source.artifacts:self.assertEqual(hashlib.sha256(receipt.artifact.body).hexdigest(),receipt.artifact.sha256)


if __name__=='__main__':unittest.main()
