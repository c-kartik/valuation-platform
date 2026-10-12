"""Independent retained statement assertions and adversarial direct selection."""

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
from unittest.mock import patch

from valuation_platform.analyst import historical_inputs as h
from valuation_platform.analyst import pilot_historical_inputs as p
from valuation_platform.analyst import pilot_direct_income as d
from valuation_platform.analyst.cash_flow_inputs import CashFlowInputError
from valuation_platform.sec.filing_xbrl import FilingXBRLDataError

ROOT = Path(__file__).resolve().parents[2]


class DirectIncomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {bid: load(bid) for bid, (_, _, load) in p._SOURCES.items()}
        cls.mapping = json.loads(p.MAPPING_PATH.read_bytes())
        cls.expected = {
            'msft-reported-cash-flow-fy2025': ('281724000000', '128528000000', 4, 2),
            'msft-reported-cash-flow-fy2026': ('331839000000', '155237000000', 4, 2),
            'aapl-reported-cash-flow-fy2025': ('416161000000', '133050000000', 4, 2),
            'googl-reported-cash-flow-fy2024': ('350018000000', '112390000000', 5, 2),
        }

    def review(self, bid='aapl-reported-cash-flow-fy2025', field=h.Field.REVENUE):
        return copy.deepcopy(next(e for e in d.entries() if e['bundle_id'] == bid and e['field'] == field.value))

    def altered(self, transform, field=h.Field.REVENUE):
        original = self.sources['aapl-reported-cash-flow-fy2025']
        receipt = next(r for r in original.artifacts if r.artifact.url.endswith('_htm.xml'))
        body = transform(receipt.artifact.body.decode()).encode()
        artifact = replace(receipt.artifact, body=body, sha256=hashlib.sha256(body).hexdigest())
        changed = replace(receipt, artifact=artifact, byte_length=len(body))
        source = SimpleNamespace(bundle_id=original.bundle_id, period=original.period,
            artifacts=tuple(changed if r == receipt else r for r in original.artifacts))
        review = self.review(field=field)
        review['instance_sha256'] = artifact.sha256
        return source, review

    def change_facts(self, transform, field=h.Field.REVENUE):
        concept = 'RevenueFromContractWithCustomerExcludingAssessedTax' if field is h.Field.REVENUE else 'OperatingIncomeLoss'
        pattern = r'<us-gaap:' + concept + r'\b[^>]*contextRef="c-1"[^>]*>.*?</us-gaap:' + concept + r'>'
        def change(body):
            matches = list(re.finditer(pattern, body, re.S))
            self.assertTrue(matches)
            return re.sub(pattern, lambda m: transform(m.group()), body, flags=re.S)
        return self.altered(change, field)

    def test_eight_values_independently_match_primary_statement_and_instance(self):
        for bid, (revenue, ebit, nr, ne) in self.expected.items():
            for field, expected, count in ((h.Field.REVENUE, revenue, nr), (h.Field.EBIT, ebit, ne)):
                source = self.sources[bid]
                inspection = d.reviewed(source, field)
                self.assertIsNotNone(inspection.selected)
                selected = inspection.candidates[inspection.selected]
                # Independent expected dollars and directly decoded HTML representation,
                # not values copied back out of an adapter or corpus aggregate.
                self.assertEqual(selected.value_usd, Decimal(expected))
                primary = next(r.artifact.body for r in source.artifacts if r.artifact.url.endswith('.htm')).decode()
                tag = d._Inline(inspection.statement['statement_id'])
                tag.feed(primary)
                attrs, displayed = tag.matches[0]
                self.assertEqual(Decimal(displayed.replace(',', '') + 'e' + attrs['scale']), Decimal(expected))
                self.assertEqual((attrs['scale'], attrs['decimals']), ('6', '-6'))
                self.assertEqual(len(selected.occurrences), count)
                self.assertEqual(tuple(o.ordinal for o in selected.occurrences),
                                 tuple(sorted(o.ordinal for o in selected.occurrences)))
                self.assertTrue(all(o.start == source.period.annual_start and o.end == source.period.annual_end
                    and o.entity_cik == source.period.cik and not o.dimensions and not o.nil
                    and o.normalized_unit == 'USD' for o in selected.occurrences))

    def test_mapping_and_adapter_preserve_every_confirming_occurrence_and_statement(self):
        for row in self.mapping['periods']:
            source = self.sources[row['bundle_id']]
            annual = p.load_annual(source.bundle_id)
            for field in d.POLICIES:
                inspection = d.reviewed(source, field)
                value = next(v for v in annual.inputs if v.field is field)
                self.assertEqual(row['fields'][field.value]['bindings'], [d.binding(source, field, inspection)])
                self.assertEqual(value.value, inspection.candidates[inspection.selected].value_usd)
                self.assertEqual(len(value.sources), len(inspection.candidates[inspection.selected].occurrences) + 1)
                self.assertEqual(value.completeness, h.Completeness.COMPLETE)
                self.assertTrue(value.unresolved_requirements)  # no financial sufficiency
                self.assertEqual(json.loads(value.sources[-1].locator)['retained_direct_evidence']['statement_id'],
                                 inspection.statement['statement_id'])

    def test_same_context_duplicate_addition_confirms_without_loss(self):
        source, review = self.altered(lambda body: body.replace('</xbrl>',
            re.search(r'<us-gaap:OperatingIncomeLoss\b[^>]*contextRef="c-1"[^>]*>.*?</us-gaap:OperatingIncomeLoss>', body).group() + '</xbrl>'), h.Field.EBIT)
        result = d.inspect(source, h.Field.EBIT, review)
        self.assertIsNotNone(result.selected)
        self.assertEqual(len(result.candidates[0].occurrences), 3)

    def test_conflicting_same_or_competing_approved_concept_never_selects(self):
        for competing in (False, True):
            def change(body):
                fact = re.search(r'<us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax\b[^>]*contextRef="c-1"[^>]*>.*?</us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax>', body).group()
                fact = fact.replace('416161000000', '416162000000')
                if competing:
                    fact = fact.replace('RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues')
                return body.replace('</xbrl>', fact + '</xbrl>')
            source, review = self.altered(change)
            result = d.inspect(source, h.Field.REVENUE, review)
            self.assertIsNone(result.selected)
            self.assertEqual(len(result.candidates), 2)
            row = next(r for r in self.mapping['periods'] if r['bundle_id'] == source.bundle_id)
            value = p._direct_value(row, h.Field.REVENUE, row['fields']['revenue'], source, result)
            self.assertIsNone(value.value)
            self.assertEqual(value.quality, h.Quality.CONFLICTING)
            self.assertEqual(len(value.alternatives), 2)
            self.assertEqual(sum(len(v.sources) for v in value.alternatives), 5)
            self.assertIn('Conflicting', value.null_reason)

    def test_equivalent_context_and_unit_ids_confirm_and_keep_originals(self):
        def change(body):
            context = re.search(r'<context id="c-1">.*?</context>', body, re.S).group()
            unit = re.search(r'<unit id="usd">.*?</unit>', body, re.S).group()
            fact = re.search(r'<us-gaap:OperatingIncomeLoss\b[^>]*contextRef="c-1"[^>]*>.*?</us-gaap:OperatingIncomeLoss>', body).group()
            extra = context.replace('id="c-1"', 'id="confirm-context"') + unit.replace('id="usd"', 'id="confirm-usd"')
            extra += fact.replace('contextRef="c-1"', 'contextRef="confirm-context"').replace('unitRef="usd"', 'unitRef="confirm-usd"')
            return body.replace('</xbrl>', extra + '</xbrl>')
        source, review = self.altered(change, h.Field.EBIT)
        result = d.inspect(source, h.Field.EBIT, review)
        self.assertIsNotNone(result.selected)
        self.assertEqual(len(result.candidates[0].occurrences), 3)
        self.assertEqual(result.candidates[0].occurrences[-1].context_id, 'confirm-context')
        self.assertEqual(result.candidates[0].occurrences[-1].unit_id, 'confirm-usd')

    def test_different_raw_and_precision_equivalent_candidates_retained(self):
        def change(body):
            fact = re.search(r'<us-gaap:OperatingIncomeLoss\b[^>]*contextRef="c-1"[^>]*>.*?</us-gaap:OperatingIncomeLoss>', body).group()
            extra = fact.replace('133050000000', '133050000000.0').replace('decimals="-6"', 'decimals="-3"')
            return body.replace('</xbrl>', extra + '</xbrl>')
        source, review = self.altered(change, h.Field.EBIT)
        result = d.inspect(source, h.Field.EBIT, review)
        self.assertIsNotNone(result.selected)
        self.assertEqual(len(result.candidates), 2)
        self.assertEqual(result.candidates[1].occurrences[0].raw_value, '133050000000.0')
        row = next(r for r in self.mapping['periods'] if r['bundle_id'] == source.bundle_id)
        value = p._direct_value(row, h.Field.EBIT, row['fields']['ebit'], source, result)
        self.assertEqual(value.alternatives[0].precision, '-3')
        self.assertEqual(value.alternatives[0].sources[0].raw_value, '133050000000.0')

    def test_comparative_context_or_extension_cannot_supply_direct_value(self):
        for transform in (lambda fact: fact.replace('contextRef="c-1"', 'contextRef="c-18"'),
                          lambda fact: fact.replace('us-gaap:', 'aapl:')):
            source, review = self.change_facts(transform)
            result = d.inspect(source, h.Field.REVENUE, review)
            self.assertIsNone(result.selected)
            self.assertEqual(result.candidates, ())
            self.assertIn('No eligible', result.reason)

    def test_dimensioned_occurrences_remain_excluded(self):
        source = self.sources['aapl-reported-cash-flow-fy2025']
        result = d.reviewed(source, h.Field.EBIT)
        # Retained filing has numerous segment facts with the same concept.
        instance = next(r.artifact.body for r in source.artifacts if r.artifact.url.endswith('_htm.xml'))
        self.assertGreater(instance.count(b'<us-gaap:OperatingIncomeLoss '), 2)
        self.assertEqual(len(result.candidates[0].occurrences), 2)

    def test_equal_second_approved_concept_is_retained_not_discarded(self):
        def change(body):
            fact = re.search(r'<us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax\b[^>]*contextRef="c-1"[^>]*>.*?</us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax>', body).group()
            return body.replace('</xbrl>', fact.replace('RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues') + '</xbrl>')
        source, review = self.altered(change)
        result = d.inspect(source, h.Field.REVENUE, review)
        self.assertIsNotNone(result.selected)
        self.assertEqual([i.input_id for i in result.candidates],
                         ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'])
        row = next(r for r in self.mapping['periods'] if r['bundle_id'] == source.bundle_id)
        value = p._direct_value(row, h.Field.REVENUE, row['fields']['revenue'], source, result)
        self.assertEqual(value.alternatives[0].sources[0].concept, 'Revenues')
        self.assertEqual(value.alternatives[0].value, value.value)

    def test_adapter_keeps_inspection_conflict_unresolved_not_positive_mapping(self):
        def change(body):
            fact = re.search(r'<us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax\b[^>]*contextRef="c-1"[^>]*>.*?</us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax>', body).group()
            return body.replace('</xbrl>', fact.replace('416161000000', '416162000000') + '</xbrl>')
        source, review = self.altered(change)
        conflict = d.inspect(source, h.Field.REVENUE, review)
        original = self.sources[source.bundle_id]
        real_review = d.reviewed
        with patch.object(d, 'reviewed', side_effect=lambda s, f: conflict if f is h.Field.REVENUE else real_review(s, f)):
            annual = p.load_annual(original.bundle_id)
        value = next(v for v in annual.inputs if v.field is h.Field.REVENUE)
        self.assertIsNone(value.value)
        self.assertEqual(value.quality, h.Quality.CONFLICTING)
        self.assertEqual(len(value.alternatives), 2)
        # An injected inspection cannot acquire trusted serialized proof: replay
        # against actual pinned bodies must reconstruct the same candidates.
        real_annual = p.load_annual(original.bundle_id)
        history = p.load_history('AAPL')
        with self.assertRaises(h.InputError):
            p.serialize(replace(history, annuals=(annual,)))
        self.assertIsNotNone(next(v for v in real_annual.inputs if v.field is h.Field.REVENUE).value)

    def test_actual_entity_or_annual_dei_mismatch_not_metadata_only(self):
        for old, new in (('0000320193', '0000789019'), ('2024-09-29', '2024-09-28'),
                         ('2025-09-27', '2025-09-26')):
            source, review = self.altered(lambda body: body.replace(old, new))
            with self.assertRaises((h.InputError, CashFlowInputError, FilingXBRLDataError)):
                d.inspect(source, h.Field.REVENUE, review)

    def test_direct_serialization_preserves_locator_precision_and_rejects_tamper(self):
        history = p.load_history('GOOGL')
        text = p.serialize(history)
        self.assertEqual(p.serialize(p.deserialize(text)), text)
        doc = json.loads(text)
        ref = doc['history']['fields']['annuals'][0]['fields']['inputs'][0]['fields']['sources'][0]['fields']
        ref['occurrence_ordinal'] += 1
        with self.assertRaises(h.InputError):
            p.deserialize(json.dumps(doc))

    def test_nil_non_usd_missing_context_and_invalid_precision_fail_conservatively(self):
        for transform in (lambda s: s.replace('>416161000000', ' xsi:nil="true">416161000000'),
                          lambda s: s.replace('contextRef="c-1"', 'contextRef="broken"'),
                          lambda s: s.replace('unitRef="usd"', 'unitRef="shares"'),
                          lambda s: s.replace('decimals="-6"', 'decimals="bad"')):
            source, review = self.change_facts(transform)
            with self.assertRaises((h.InputError, CashFlowInputError, FilingXBRLDataError)):
                d.inspect(source, h.Field.REVENUE, review)

    def test_review_period_accession_entity_and_body_binding_rejected(self):
        source = self.sources['aapl-reported-cash-flow-fy2025']
        for key, value in (('accession', '0000320193-25-000080'), ('cik', 789019),
                           ('annual_start', '2024-01-01'), ('annual_end', '2025-12-31'), ('form', '10-K/A')):
            review = self.review()
            review['period'][key] = value
            with self.assertRaises(h.InputError):
                d.inspect(source, h.Field.REVENUE, review)
        review = self.review()
        review['instance_sha256'] = '0' * 64
        with self.assertRaises(h.InputError):
            d.inspect(source, h.Field.REVENUE, review)

    def test_statement_precision_context_scale_and_value_must_match(self):
        source = self.sources['aapl-reported-cash-flow-fy2025']
        for key, value in (('decimals', 'INF'), ('scale', '3'), ('contextref', 'c-18'), ('unitref', 'shares')):
            review = self.review()
            review['statement_attributes'][key] = value
            with self.assertRaises(h.InputError):
                d.inspect(source, h.Field.REVENUE, review)
        review = self.review()
        review['displayed_value'] = '416,162'
        with self.assertRaises(h.InputError):
            d.inspect(source, h.Field.REVENUE, review)

    def test_low_decimal_context_does_not_round_statement_or_instance(self):
        with localcontext() as ctx:
            ctx.prec = 3
            result = d.reviewed(self.sources['aapl-reported-cash-flow-fy2025'], h.Field.REVENUE)
            self.assertEqual(result.candidates[result.selected].value_usd, Decimal('416161000000'))

    def test_all_non_income_mapping_dispositions_and_original_artifacts_preserved(self):
        before = json.loads(subprocess.check_output(['git', 'show', 'e1f7d1c5310f2d6535e8f855382c066c9e422e53:docs/pilot-historical-input-mappings.json'], cwd=ROOT))
        for old, new in zip(before['periods'], self.mapping['periods']):
            for key in old:
                if key != 'fields':
                    self.assertEqual(old[key], new[key])
            for field in old['fields']:
                if field not in ('revenue', 'ebit'):
                    self.assertEqual(old['fields'][field], new['fields'][field])
        for source in self.sources.values():
            for receipt in source.artifacts:
                self.assertEqual(hashlib.sha256(receipt.artifact.body).hexdigest(), receipt.artifact.sha256)


if __name__ == '__main__':
    unittest.main()
