"""Shared inspection is structural; pilot acceptance/serialization are unchanged."""

import copy
from dataclasses import replace
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

from valuation_platform.analyst import retained_components as r, historical_inputs as h
from valuation_platform.analyst import pilot_historical_inputs as p, pilot_cash_investments as cash
from valuation_platform.analyst import pilot_direct_income as income, pilot_debt_leases as debt
from valuation_platform.analyst.cash_flow_inputs import CashFlowInputError
from valuation_platform.sec.filing_xbrl import FilingXBRLDataError

ROOT=Path(__file__).resolve().parents[2]
HEAD='0d8b3bdfd56a8e606290e0d6ef5a1d4c1e4b2105'


class RetainedComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources={bid:load(bid) for bid,(_,_,load) in p._SOURCES.items()}
        cls.evidence={bid:r.prepare(source.period,source.artifacts,cls.bindings(source.artifacts)) for bid,source in cls.sources.items()}

    @staticmethod
    def bindings(receipts):
        return tuple(r.ArtifactBinding(a.artifact.url,a.artifact.sha256,'instance' if a.artifact.url.endswith('_htm.xml') else 'support') for a in receipts)

    def spec(self, concept='LongTermDebtCurrent', period_kind='instant', dimensions=()):
        e=self.evidence['aapl-reported-cash-flow-fy2025']
        return r.SelectionSpec('explicit_test_component',(r.Selector(e.namespaces['us-gaap'],concept,dimensions),),
            period_kind,'USD','caller_supplied_reported_role','caller_supplied_scope_not_certified',('Completeness not established.',))

    def altered(self, transform):
        source=self.sources['aapl-reported-cash-flow-fy2025']
        old=next(a for a in source.artifacts if a.artifact.url.endswith('_htm.xml'))
        body=transform(old.artifact.body.decode()).encode()
        changed=replace(old,artifact=replace(old.artifact,body=body,sha256=hashlib.sha256(body).hexdigest()),byte_length=len(body))
        receipts=tuple(changed if a==old else a for a in source.artifacts)
        return r.prepare(source.period,receipts,self.bindings(receipts))

    def fact(self, body):
        return re.search(r'<us-gaap:LongTermDebtCurrent\b[^>]*contextRef="c-20"[^>]*>.*?</us-gaap:LongTermDebtCurrent>',body).group()

    def test_all_eight_direct_inspections_reproduce_committed_mapping(self):
        doc=json.loads(p.MAPPING_PATH.read_bytes())
        for row in doc['periods']:
            source=self.sources[row['bundle_id']];e=self.evidence[source.bundle_id]
            for field,policy in income.POLICIES.items():
                reviewed=income.reviewed(source,field)
                spec=r.SelectionSpec(field.value,tuple(r.Selector(e.namespaces['us-gaap'],key.name,()) for key in policy.candidates),
                    'annual','USD',row['fields'][field.value]['bindings'][0]['role'],reviewed.statement['statement_scope'],())
                result=r.inspect(e,spec)
                self.assertEqual([(c.concept,c.value,c.precision,[o.__dict__ for o in c.occurrences]) for c in result.candidates],
                    [(c.input_id,c.value_usd,c.occurrences[0].decimals,[o.__dict__ for o in c.occurrences]) for c in reviewed.candidates])
                self.assertEqual(row['fields'][field.value]['bindings'],[income.binding(source,field,reviewed)])

    def test_cash_and_debt_components_across_all_four_periods(self):
        doc=json.loads(p.MAPPING_PATH.read_bytes())
        for row in doc['periods']:
            source=self.sources[row['bundle_id']];e=self.evidence[source.bundle_id]
            for module,field in ((cash,h.Field.CASH_INVESTMENTS),(debt,h.Field.DEBT_LEASES)):
                review,components=module.inspect(source)
                self.assertEqual(module.mapping_entry(source,(review,components)),row['fields'][field.value])
                for component in components:
                    s=component.spec
                    result=r.inspect(e,r.SelectionSpec(s['component_id'],(r.Selector(s['namespace'],s['concept'],tuple(s.get('dimensions',()))),),
                        'instant','USD',s['role'],s['scope'],tuple(u['reason'] for u in review['unknowns'])))
                    self.assertEqual(result.specification.role,s['role']);self.assertEqual(result.specification.scope,s['scope'])
                    values=[c.value_usd if module is cash else c.value for c in component.candidates]
                    self.assertEqual([c.value for c in result.candidates],values)
                    for new,old in zip(result.candidates,component.candidates):
                        expected=([o.__dict__ for o in old.occurrences] if module is cash else list(old.occurrences))
                        actual=([o.__dict__ for o in new.occurrences] if module is cash else
                            [o.__dict__ | dict(start=None,end=str(o.end),dimensions=list(o.dimensions)) for o in new.occurrences])
                        self.assertEqual(actual,expected)
                    # Shared inspection supplies no gate override or financial selection.
                    self.assertFalse(hasattr(result,'selected'))

    def test_absent_artifacts_and_absent_selector_remain_requirements(self):
        source=self.sources['aapl-reported-cash-flow-fy2025']
        empty=r.prepare(source.period,(),self.bindings(source.artifacts))
        result=r.inspect(empty,self.spec())
        self.assertEqual(result.candidates,());self.assertEqual(result.evidence_receipts,())
        self.assertTrue(any('Missing retained instance' in s for s in result.unresolved_requirements))
        absent=r.inspect(self.evidence[source.bundle_id],self.spec('ExplicitlyUnboundConcept'))
        self.assertFalse(absent.candidates);self.assertIn('absence is not zero',absent.unresolved_requirements[-1])
        receipts=tuple(a for a in source.artifacts if a.artifact.url.endswith('_htm.xml'))
        partial=r.inspect(r.prepare(source.period,receipts,self.bindings(source.artifacts)),self.spec())
        self.assertTrue(partial.candidates)
        self.assertTrue(any('Missing retained support' in s for s in partial.unresolved_requirements))

    def test_equal_occurrences_with_different_context_unit_ids_confirm(self):
        def add(body):
            context=re.search(r'<context id="c-20".*?</context>',body,re.S).group().replace('id="c-20"','id="confirmation-context"')
            unit=re.search(r'<unit id="usd".*?</unit>',body,re.S).group().replace('id="usd"','id="confirmation-unit"')
            fact=self.fact(body).replace('contextRef="c-20"','contextRef="confirmation-context"').replace('unitRef="usd"','unitRef="confirmation-unit"')
            return body.replace('</xbrl>',context+unit+fact+'</xbrl>')
        result=r.inspect(self.altered(add),self.spec())
        self.assertEqual(len(result.candidates),1)
        self.assertEqual(len(result.candidates[0].occurrences),3)
        self.assertEqual(result.candidates[0].occurrences[-1].context_id,'confirmation-context')
        self.assertEqual(result.candidates[0].occurrences[-1].unit_id,'confirmation-unit')
        self.assertFalse(result.competing_values)

    def test_unequal_values_compete_and_equal_precision_variants_stay_distinct(self):
        for old,new,competing in [('12350000000','12351000000',True),('decimals="-6"','decimals="-8"',False)]:
            result=r.inspect(self.altered(lambda body:body.replace('</xbrl>',self.fact(body).replace(old,new)+'</xbrl>')),self.spec())
            self.assertEqual(len(result.candidates),2)
            self.assertEqual(bool(result.competing_values),competing)
            if competing:self.assertIn('Competing unequal',result.unresolved_requirements[-1])
            else:self.assertEqual([c.precision for c in result.candidates],['-6','-8'])

    def test_explicit_dimensions_and_annual_instant_boundaries(self):
        e=self.evidence['aapl-reported-cash-flow-fy2025']
        result=r.inspect(e,self.spec('LongTermDebtFairValue'))
        self.assertFalse(result.candidates)  # exact Level-2 note is dimensioned
        s=debt.review_for(self.sources['aapl-reported-cash-flow-fy2025'])['components'][5]
        result=r.inspect(e,self.spec(s['concept'],dimensions=tuple(s['dimensions'])))
        self.assertEqual(result.candidates[0].value,Decimal('80400000000'))
        self.assertEqual(result.candidates[0].occurrences[0].dimensions,tuple(s['dimensions']))
        self.assertFalse(r.inspect(e,self.spec(period_kind='annual')).candidates)
        self.assertFalse(r.inspect(e,self.spec('OperatingIncomeLoss')).candidates)
        annual=r.inspect(e,self.spec('OperatingIncomeLoss','annual'))
        self.assertEqual(annual.candidates[0].value,Decimal('133050000000'))
        changed=self.altered(lambda body:re.sub(r'<us-gaap:LongTermDebtCurrent\b[^>]*>.*?</us-gaap:LongTermDebtCurrent>',
            lambda m:m.group().replace('contextRef="c-20"','contextRef="c-21"'),body))
        self.assertFalse(r.inspect(changed,self.spec()).candidates)

    def test_units_nil_precision_and_broken_links_fail(self):
        for old,new in [('unitRef="usd"','unitRef="shares"'),('decimals="-6"','decimals="invalid"'),
                         ('contextRef="c-20"','contextRef="missing"'),('>12350000000',' xsi:nil="true">12350000000')]:
            with self.assertRaises((h.InputError,FilingXBRLDataError)):
                e=self.altered(lambda body:body.replace(self.fact(body),self.fact(body).replace(old,new)))
                r.inspect(e,self.spec())

    def test_equal_values_for_different_concepts_are_not_equivalent_candidates(self):
        e=self.evidence['googl-reported-cash-flow-fy2024']
        spec=r.SelectionSpec('explicit_parent_and_component',tuple(r.Selector(e.namespaces['us-gaap'],name,()) for name in
            ('LongTermDebtNoncurrent','LongTermDebtAndCapitalLeaseObligations')), 'instant','USD',
            'caller_supplied_role','Parent/component overlap must be reviewed.',('No non-overlap or completeness approval.',))
        result=r.inspect(e,spec)
        self.assertEqual(len(result.candidates),2)
        self.assertEqual({c.value for c in result.candidates},{Decimal('10883000000')})
        self.assertEqual({c.concept for c in result.candidates},{'LongTermDebtNoncurrent','LongTermDebtAndCapitalLeaseObligations'})
        self.assertFalse(result.competing_values)
        self.assertFalse(hasattr(result,'selected'))

    def test_exact_identity_receipt_digest_and_spec_validation(self):
        source=self.sources['aapl-reported-cash-flow-fy2025'];bindings=self.bindings(source.artifacts)
        with self.assertRaises(h.InputError):r.prepare(replace(source.period,accession='0000320193-25-000080'),source.artifacts,bindings)
        with self.assertRaises(CashFlowInputError):r.prepare(replace(source.period,annual_start=source.period.annual_start.replace(day=28)),source.artifacts,bindings)
        with self.assertRaises(h.InputError):r.prepare(source.period,source.artifacts,(replace(bindings[0],sha256='0'*64),*bindings[1:]))
        with self.assertRaises(h.InputError):r.ArtifactBinding(bindings[0].url,bindings[0].sha256,'instance','sha256_reserialized_json')
        with self.assertRaises(h.InputError):replace(self.spec(),unit='shares')
        with self.assertRaises(h.InputError):replace(self.spec(),selectors=())
        with self.assertRaises(h.InputError):replace(self.spec(),period_kind='quarterly')

    def test_source_references_and_raw_precision_do_not_authorize_consumption(self):
        result=r.inspect(self.evidence['aapl-reported-cash-flow-fy2025'],self.spec())
        self.assertIn('Completeness not established.',result.unresolved_requirements)
        candidate=result.candidates[0]
        for o,ref in zip(candidate.occurrences,candidate.evidence_references):
            self.assertEqual((ref.context_id,ref.occurrence_ordinal,ref.raw_value,ref.decimals,ref.dimensions),
                (o.context_id,o.ordinal,o.raw_value,o.decimals,o.dimensions))
            self.assertEqual(ref.receipt.artifact.accession,ref.period.accession)
            self.assertTrue(json.loads(ref.locator)['inspection_only'])
        with localcontext() as ctx:
            ctx.prec=3
            self.assertEqual(r.inspect(self.evidence['aapl-reported-cash-flow-fy2025'],self.spec()).candidates[0].value,Decimal('12350000000'))
        # Role/scope are supplied annotations, not classifications inferred from names.
        changed=r.inspect(self.evidence['aapl-reported-cash-flow-fy2025'],replace(self.spec(),role='unreviewed_role',scope='unknown interpretation'))
        self.assertEqual(changed.candidates[0].value,candidate.value)
        self.assertFalse(hasattr(changed,'completeness'))

    def test_frozen_artifacts_mappings_and_adapter_bytes_preserved(self):
        hashes={'MSFT':'e05f85125b6244c321fbdee6469fa89bb809533614bbcc9c5399d2b5c56eb8b5',
            'AAPL':'2772f34db57beb116f4fdb498f0016dc6502d7642b7bbc18f9e89e3645e66f83',
            'GOOGL':'f442e248f1ea2884967680db78c99076ee8beefdaae0bc050b6ee2f0c9b324d5'}
        for issuer,expected in hashes.items():
            payload=p.serialize(p.load_history(issuer))
            self.assertEqual(hashlib.sha256(payload.encode()).hexdigest(),expected)
            self.assertEqual(p.serialize(p.deserialize(payload)),payload)
        for path in ('docs/pilot-historical-input-mappings.json','docs/pilot-direct-income-evidence.json',
            'docs/pilot-cash-investment-evidence.json','docs/pilot-debt-lease-evidence.json',
            'src/valuation_platform/analyst/pilot_historical_inputs.py','src/valuation_platform/analyst/historical_inputs.py',
            'src/valuation_platform/normalization/balance_sheet.py','src/valuation_platform/sec/filing_xbrl.py',
            'docs/company-data-preparation/msft-reported-cash-flow-bundles.json',
            'docs/company-data-preparation/aapl-reported-cash-flow-bundle.json','docs/company-data-preparation/googl-reported-cash-flow-bundle.json'):
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',HEAD+':'+path],cwd=ROOT))


if __name__=='__main__':unittest.main()
