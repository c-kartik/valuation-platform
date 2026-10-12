"""Exact retained year-end values, scope and conservative component preparation."""

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

from valuation_platform.analyst import pilot_cash_investments as c
from valuation_platform.analyst import pilot_historical_inputs as p
from valuation_platform.analyst import historical_inputs as h
from valuation_platform.analyst.cash_flow_inputs import CashFlowInputError

ROOT = Path(__file__).resolve().parents[2]


class CashInvestmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {bid: load(bid) for bid, (_, _, load) in p._SOURCES.items()}
        cls.expected = {
            'msft-reported-cash-flow-fy2025': dict(cash_equivalents='30242000000', current_investments='64323000000', long_term_investments_mixed='15405000000', cash_current_parent='94565000000', measurement_alternative='2900000000', equity_method='6000000000', cash_restricted_combined='30242000000'),
            'msft-reported-cash-flow-fy2026': dict(cash_equivalents='20935000000', current_investments='55908000000', long_term_investments_mixed='36348000000', cash_current_parent='76843000000', measurement_alternative='12400000000', equity_method='12000000000', cash_restricted_combined='20935000000'),
            'aapl-reported-cash-flow-fy2025': dict(cash_equivalents='35934000000', current_investments='18763000000', long_term_marketable='77723000000', cash_restricted_combined='35934000000'),
            'googl-reported-cash-flow-fy2024': dict(cash_equivalents='23466000000', current_investments='72191000000', long_term_marketable_restricted='266000000', nonmarketable_parent='37982000000', cash_current_parent='95657000000', equity_method='2000000000', cash_restricted_combined='23466000000'),
        }

    def mutated(self, transform):
        original = self.sources['aapl-reported-cash-flow-fy2025']
        receipt = next(r for r in original.artifacts if r.artifact.url.endswith('_htm.xml'))
        body = transform(receipt.artifact.body.decode()).encode()
        artifact = replace(receipt.artifact, body=body, sha256=hashlib.sha256(body).hexdigest())
        changed = replace(receipt, artifact=artifact, byte_length=len(body))
        source = SimpleNamespace(bundle_id=original.bundle_id, period=original.period,
            artifacts=tuple(changed if r == receipt else r for r in original.artifacts))
        review = copy.deepcopy(c.review_for(original)); review['instance_sha256'] = artifact.sha256
        return source, review

    def cash_fact(self, body):
        return re.search(r'<us-gaap:CashAndCashEquivalentsAtCarryingValue\b[^>]*contextRef="c-20"[^>]*>.*?</us-gaap:CashAndCashEquivalentsAtCarryingValue>', body).group()

    def test_values_match_independently_reviewed_retained_primary_tags(self):
        for bid, expected in self.expected.items():
            source = self.sources[bid]; review, components = c.inspect(source)
            primary = next(r.artifact.body for r in source.artifacts if r.artifact.url.endswith('.htm'))
            tags = c._Tags(); tags.feed(primary.decode())
            self.assertEqual({x.spec['component_id'] for x in components if x.selected is not None}, set(expected))
            for component in components:
                cid = component.spec['component_id']
                if cid not in expected: continue
                point = Decimal(expected[cid])
                self.assertEqual(component.candidates[component.selected].value_usd, point)
                for statement in component.spec['statements']:
                    attrs, displayed = tags.tags[statement['id']]
                    self.assertEqual(Decimal(displayed.replace(',', '') + 'e' + attrs['scale']), point)
                for item in component.candidates:
                    for occurrence in item.occurrences:
                        self.assertIsNone(occurrence.start)
                        self.assertEqual(occurrence.end, source.period.annual_end)
                        self.assertEqual(occurrence.entity_cik, source.period.cik)
                        self.assertEqual(occurrence.normalized_unit, 'USD')
                        self.assertFalse(occurrence.dimensions or occurrence.nil)

    def test_every_occurrence_and_instant_receipt_survives_adapter(self):
        for bid, source in self.sources.items():
            review, components = c.inspect(source)
            annual = p.load_annual(bid)
            inputs = [v for v in annual.inputs if v.field is h.Field.CASH_INVESTMENTS]
            self.assertEqual(len(inputs), len(components) + len(review['unknowns']))
            for component, value in zip(components, inputs):
                observations = (value, *value.alternatives) if value.value is not None else value.alternatives
                self.assertEqual(len(observations), len(component.candidates))
                for observed, item in zip(observations, component.candidates):
                    refs = [r for r in observed.sources if r.occurrence_ordinal is not None]
                    self.assertEqual([r.occurrence_ordinal for r in refs], [o.ordinal for o in item.occurrences])
                    self.assertEqual(observed.precision, item.occurrences[0].decimals)
                    for ref, occurrence in zip(refs, item.occurrences):
                        self.assertEqual(ref.context_id, occurrence.context_id)
                        self.assertEqual(ref.raw_value, occurrence.raw_value)
                        self.assertIn(ref.receipt, source.artifacts)
                        self.assertEqual(json.loads(ref.locator)['unit_id'], occurrence.unit_id)
                        self.assertEqual(ref.end, annual.period.annual_end)
                    self.assertIs(observed.completeness, h.Completeness.PARTIAL)
                    self.assertEqual(observed.as_of, annual.period.annual_end)
                    self.assertIsNone(observed.formula)

    def test_parent_overlap_restricted_and_strategic_scope_are_not_liquidity_equivalence(self):
        for bid, source in self.sources.items():
            review, components = c.inspect(source)
            by_id = {x.spec['component_id']: x for x in components}
            self.assertEqual(by_id['cash_restricted_combined'].spec['overlap_with'], ['cash_equivalents'])
            if bid.startswith('msft'):
                self.assertEqual(by_id['long_term_investments_mixed'].spec['scope_status'], 'mixed')
                self.assertIn('equity_method', by_id['long_term_investments_mixed'].spec['overlap_with'])
                self.assertEqual(by_id['cash_current_parent'].spec['overlap_with'], ['cash_equivalents', 'current_investments'])
            if bid.startswith('googl'):
                self.assertIn('lock-up', by_id['long_term_marketable_restricted'].spec['scope'])
                self.assertNotEqual(by_id['nonmarketable_parent'].spec['concept'], by_id['current_investments'].spec['concept'])
            values = [v for v in p.load_annual(bid).inputs if v.field is h.Field.CASH_INVESTMENTS]
            self.assertTrue(all(v.formula is None and v.completeness is not h.Completeness.COMPLETE for v in values))
            self.assertTrue(all('no_aggregation_or_valuation_authorization' in v.flags for v in values))
            aggregate = next(v for v in values if ':complete_cash_investment_aggregate:' in v.input_id)
            self.assertIsNone(aggregate.value)

    def test_alphabet_precision_conflict_retains_both_no_rounding_adjustment(self):
        values = [v for v in p.load_annual('googl-reported-cash-flow-fy2024').inputs if v.field is h.Field.CASH_INVESTMENTS]
        value = next(v for v in values if ':measurement_alternative:' in v.input_id)
        self.assertIsNone(value.value)
        self.assertIs(value.quality, h.Quality.CONFLICTING)
        self.assertEqual([(a.value, a.precision) for a in value.alternatives],
                         [(Decimal('35500000000'), '-8'), (Decimal('35531000000'), '-6')])
        self.assertTrue(all(a.formula is None for a in value.alternatives))

    def test_extension_captions_gated_and_not_equivalent_to_parent(self):
        for bid, point in (('aapl-reported-cash-flow-fy2025', '132420000000'), ('googl-reported-cash-flow-fy2024', '83250000000')):
            value = next(v for v in p.load_annual(bid).inputs if ':cash_marketable_extension:' in v.input_id)
            self.assertIsNone(value.value)
            self.assertEqual(value.alternatives[0].value, Decimal(point))
            self.assertIn('support_only', value.alternatives[0].flags)
            self.assertIn('separately gated', value.null_reason)

    def test_null_requirements_never_zero_or_complete(self):
        for bid in self.sources:
            annual = p.load_annual(bid)
            cash = [v for v in annual.inputs if v.field is h.Field.CASH_INVESTMENTS]
            self.assertEqual(sum(v.value is None for v in cash), 6 if bid.startswith('googl') else 5 if bid.startswith('aapl') else 4)
            for value in cash:
                if value.value is None:
                    self.assertIs(value.origin, h.Origin.UNAVAILABLE)
                    self.assertTrue(value.null_reason and value.unresolved_requirements)
                    self.assertIsNot(value.completeness, h.Completeness.COMPLETE)

    def test_same_or_equivalent_context_unit_duplicates_all_retained(self):
        def transform(body):
            fact = self.cash_fact(body)
            context = re.search(r'<context id="c-20">.*?</context>', body, re.S).group()
            unit = re.search(r'<unit id="usd">.*?</unit>', body, re.S).group()
            extra = context.replace('id="c-20"', 'id="confirmation"') + unit.replace('id="usd"', 'id="confirmation_usd"')
            extra += fact + fact.replace('contextRef="c-20"', 'contextRef="confirmation"').replace('unitRef="usd"', 'unitRef="confirmation_usd"')
            return body.replace('</xbrl>', extra + '</xbrl>')
        source, review = self.mutated(transform)
        _, components = c.inspect(source, review)
        cash = next(v for v in components if v.spec['component_id'] == 'cash_equivalents')
        self.assertIsNotNone(cash.selected)
        self.assertEqual(len(cash.candidates[0].occurrences), 4)
        self.assertEqual(cash.candidates[0].occurrences[-1].context_id, 'confirmation')

    def test_differing_eligible_values_are_not_selected_by_statement_or_precedence(self):
        source, review = self.mutated(lambda body: body.replace('</xbrl>', self.cash_fact(body).replace('35934000000', '35935000000') + '</xbrl>'))
        _, components = c.inspect(source, review)
        cash = next(v for v in components if v.spec['component_id'] == 'cash_equivalents')
        self.assertIsNone(cash.selected)
        self.assertEqual(len(cash.candidates), 2)
        self.assertEqual(sum(len(i.occurrences) for i in cash.candidates), 3)

    def test_comparative_instant_and_duration_cannot_supply_year_end_balance(self):
        for context in ('c-21', 'c-1'):
            def change(body):
                return re.sub(r'<us-gaap:CashAndCashEquivalentsAtCarryingValue\b[^>]*contextRef="c-20"[^>]*>.*?</us-gaap:CashAndCashEquivalentsAtCarryingValue>',
                              lambda m: m.group().replace('contextRef="c-20"', 'contextRef="'+context+'"'), body)
            source, review = self.mutated(change)
            _, components = c.inspect(source, review)
            cash = next(v for v in components if v.spec['component_id'] == 'cash_equivalents')
            self.assertIsNone(cash.selected)
            self.assertEqual(cash.candidates, ())

    def test_nil_non_usd_invalid_precision_and_broken_context_rejected(self):
        for old, new in (('unitRef="usd"','unitRef="shares"'), ('decimals="-6"','decimals="bad"'),
                         ('contextRef="c-20"','contextRef="missing"'), ('>35934000000',' xsi:nil="true">35934000000')):
            source, review = self.mutated(lambda body: body.replace(self.cash_fact(body), self.cash_fact(body).replace(old, new)))
            with self.assertRaises((h.InputError, CashFlowInputError, KeyError)):
                c.inspect(source, review)

    def test_exact_period_and_digest_namespace_scope_note_binding(self):
        source = self.sources['aapl-reported-cash-flow-fy2025']
        for key, bad in (('accession','0000320193-25-000080'),('annual_end','2025-09-28'),('form','10-K/A'),('cik',789019)):
            review = copy.deepcopy(c.review_for(source)); review['period'][key] = bad
            with self.assertRaises(h.InputError): c.inspect(source, review)
        for mutation in (lambda r: r.__setitem__('instance_sha256','0'*64),
                         lambda r: r['components'][0].__setitem__('namespace','http://issuer.invalid'),
                         lambda r: r['scope_notes'][0].__setitem__('text','unsupported scope assertion')):
            review = copy.deepcopy(c.review_for(source)); mutation(review)
            with self.assertRaises(h.InputError): c.inspect(source, review)

    def test_precision_and_nested_note_tags_not_silently_promoted(self):
        with localcontext() as ctx:
            ctx.prec = 3
            _, components = c.inspect(self.sources['msft-reported-cash-flow-fy2025'])
        item = next(v for v in components if v.spec['component_id'] == 'equity_method')
        self.assertEqual(item.candidates[0].value_usd, Decimal('6000000000'))
        self.assertEqual(item.candidates[0].occurrences[0].decimals, '-8')
        self.assertEqual(item.spec['statements'][0]['attributes']['scale'], '9')

    def test_deterministic_roundtrip_and_tampered_overlap_rejection(self):
        history = p.load_history('GOOGL'); payload = p.serialize(history)
        self.assertEqual(p.serialize(p.deserialize(payload)), payload)
        changed = json.loads(payload)
        cash = next(v for v in changed['history']['fields']['annuals'][0]['fields']['inputs']
                    if v['fields']['input_id'].startswith('cash_investment:cash_current_parent:'))
        cash['fields']['flags'] = ['no_overlap']
        with self.assertRaises(h.InputError): p.deserialize(json.dumps(changed))

    def test_all_other_mapping_fields_and_source_artifacts_preserved(self):
        old = json.loads(subprocess.check_output(['git','show','1a49f71fa8fb907a8dc9900bb463fc9656f37e48:docs/pilot-historical-input-mappings.json'],cwd=ROOT))
        new = json.loads(p.MAPPING_PATH.read_bytes())
        for before, after in zip(old['periods'],new['periods']):
            for key in before:
                if key != 'fields': self.assertEqual(before[key],after[key])
            for field in before['fields']:
                if field != h.Field.CASH_INVESTMENTS.value: self.assertEqual(before['fields'][field],after['fields'][field])
        for source in self.sources.values():
            for receipt in source.artifacts:
                self.assertEqual(hashlib.sha256(receipt.artifact.body).hexdigest(),receipt.artifact.sha256)
            self.assertFalse(source.valuation_consumption_approved)


if __name__ == '__main__':
    unittest.main()
