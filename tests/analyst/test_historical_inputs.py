"""WP0 metadata invariants, not issuer financial approvals."""
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import unittest

from valuation_platform.analyst import historical_inputs as h
from valuation_platform.analyst.nwc import Artifact, Period
from valuation_platform.analyst.cash_flow_inputs import Receipt


P = Period(320193, "0000320193-25-000079", date(2024, 9, 29), date(2025, 9, 27))


def unknown(field):
    return h.InputValue(field.value, field, P,
        date(2025, 10, 1) if field is h.Field.SHARES else
        P.annual_end if field in (h.Field.CASH_INVESTMENTS, h.Field.DEBT_LEASES, h.Field.OTHER_BRIDGE) else None,
        None, "shares" if field is h.Field.SHARES else "USD", 1, 1, "unknown",
        "explicitly unprepared", h.Origin.UNAVAILABLE, h.Quality.UNASSESSED, "unknown", h.Scope.UNKNOWN,
        h.Completeness.UNKNOWN, h.Review.UNREVIEWED, (), None, None, (),
        "no selection made", (), ("required evidence missing",), "not researched", ())


def reported(field=h.Field.REVENUE, input_id="reported"):
    v = unknown(field)
    body = b"synthetic retained note for structural tests only"
    artifact = Artifact("https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/note.htm",
        P.accession, "sec_response_body_bytes", "sha256_sec_response_body_bytes",
        hashlib.sha256(body).hexdigest(), body)
    receipt = Receipt(artifact, len(body), "2026-10-12T00:00:00+00:00", 200, "test fixture")
    source = h.SourceReference("scope-note", P, receipt, "page 1, table row",
        "", "", "", None, None if v.as_of else P.annual_start,
        v.as_of or P.annual_end, v.unit, "123.4", "-1", ())
    return replace(v, input_id=input_id, value=Decimal("123.4"), precision="-1",
        role="reported subtotal", origin=h.Origin.REPORTED, quality=h.Quality.LIMITED,
        completeness=h.Completeness.PARTIAL, sources=(source,), null_reason=None,
        coverage_keys=("population-a",))


def annual(*values):
    replaced = {v.field for v in values}
    return h.AnnualBundle("test-annual", 1, P,
        tuple(unknown(f) for f in h.Field if f not in replaced) + values,
        ("structural test; no fact review or sufficiency approval",))


def history(*values):
    return h.HistoryBundle("test-history", 1, P.cik, (annual(*values),), ("one selected period",))


class HistoricalInputTests(unittest.TestCase):
    def test_immutable_and_typed(self):
        v = unknown(h.Field.EBIT)
        with self.assertRaises(FrozenInstanceError):
            v.value = Decimal(0)
        for changes in ({"flags": []}, {"origin": "reported"}, {"scale": True}, {"sign": 0}, {"value": 1.0}):
            with self.assertRaises(h.InputError):
                replace(v, **changes)

    def test_null_reason_and_acknowledgment_do_not_resolve(self):
        for changes in ({"null_reason": None}, {"null_reason": ""},
                        {"unresolved_requirements": ()}, {"completeness": h.Completeness.COMPLETE}):
            with self.assertRaises(h.InputError):
                replace(unknown(h.Field.EBIT), **changes)
        v = replace(unknown(h.Field.EBIT), review=h.Review.ACCEPTED)
        self.assertIn(h.Field.EBIT, annual(v).unresolved_required_fields)

    def test_origin_is_not_quality(self):
        v = reported()
        self.assertEqual(v.origin, h.Origin.REPORTED)
        self.assertEqual(v.quality, h.Quality.LIMITED)
        self.assertEqual(replace(v, quality=h.Quality.CONFLICTING).value, v.value)

    def test_reported_provenance_scale_sign_precision(self):
        v = reported()
        for changes in ({"sources": ()}, {"value": Decimal("123.5")},
                        {"precision": "INF"}, {"scale": 1000}, {"sign": -1}):
            with self.assertRaises(h.InputError):
                replace(v, **changes)
        self.assertEqual(replace(v, value=Decimal("-123400"), scale=1000, sign=-1).value, Decimal("-123400"))

    def test_receipt_digest_and_representation(self):
        s = reported().sources[0]
        for changes in ({"body": b"different"}, {"representation": "parsed_json"}, {"sha256": "0" * 64}):
            with self.assertRaises(ValueError):
                replace(s.receipt.artifact, **changes)

    def test_exact_source_period_binding(self):
        v = reported()
        with self.assertRaises(h.InputError):
            replace(v.sources[0], period=replace(P, accession="0000320193-24-000123"))
        with self.assertRaises(h.InputError):
            replace(v, sources=(replace(v.sources[0], start=date(2024, 1, 1)),))
        with self.assertRaises(h.InputError):
            replace(v, sources=(replace(v.sources[0], unit="shares"),))

    def test_occurrence_and_note_references(self):
        s = reported().sources[0]
        exact = replace(s, namespace="http://fasb.org/us-gaap/2025", concept="Revenue",
                        context_id="annual", occurrence_ordinal=2)
        self.assertEqual(exact.occurrence_ordinal, 2)
        for changes in ({"occurrence_ordinal": -1}, {"context_id": "invented"},
                        {"raw_value": "NaN"}, {"decimals": "rounded"}):
            with self.assertRaises(h.InputError):
                replace(s, **changes)

    def test_manual_identity_no_fabricated_sec_provenance(self):
        m = h.ManualIdentity("analyst", "2026-10-12T00:00:00Z", "explicit illustrative classification")
        v = replace(unknown(h.Field.EBIT), value=Decimal(42), origin=h.Origin.PROXY,
                    manual=m, null_reason=None)
        self.assertEqual(v.sources, ())
        for changes in ({"manual": None}, {"origin": h.Origin.REPORTED}):
            with self.assertRaises(h.InputError):
                replace(v, **changes)
        for stamp in ("", "2026-10-12", "2026-10-12T00:00:00+04:00"):
            with self.assertRaises(h.InputError):
                h.ManualIdentity("analyst", stamp, "rationale")

    def test_override_and_alternatives_preserved(self):
        original = reported(h.Field.EBIT)
        override = replace(original, input_id="override", value=Decimal(42), origin=h.Origin.OVERRIDE,
            manual=h.ManualIdentity("analyst", "2026-10-12T00:00:00Z", "explicit override"),
            alternatives=(original,), selection_rationale="candidate selected, not economic equivalence")
        self.assertEqual(h.deserialize(h.serialize(history(override))).annuals[0].inputs[-1].alternatives, (original,))
        for changes in ({"alternatives": ()}, {"alternatives": (reported(h.Field.CFO),)}):
            with self.assertRaises(h.InputError):
                replace(override, **changes)

    def test_partial_totals_remain_partial(self):
        f = h.Formula("partial", 1, h.FormulaKind.COMPONENT_TOTAL, "a", ("a",), False, False, True, ("scope-note",))
        v = replace(reported(h.Field.CASH_INVESTMENTS), input_id="sum", origin=h.Origin.DERIVED, formula=f)
        self.assertEqual(v.completeness, h.Completeness.PARTIAL)
        with self.assertRaises(h.InputError):
            replace(v, completeness=h.Completeness.COMPLETE)
        with self.assertRaises(h.InputError):
            replace(f, non_overlapping=False)

    def test_operating_expense_scope_required(self):
        with self.assertRaises(h.InputError):
            h.Formula("ebit", 1, h.FormulaKind.OPERATING_EXPENSE_BRIDGE, "revenue-expenses",
                      ("a",), False, True, True, ("scope-note",))

    def test_cfo_remainder_not_an_adjustment(self):
        f = h.Formula("remainder", 1, h.FormulaKind.CFO_REMAINDER, "CFO-less-identified-rows",
                      ("a",), False, False, True, ("scope-note",))
        with self.assertRaises(h.InputError):
            replace(reported(h.Field.EBIT), origin=h.Origin.DERIVED, formula=f)
        v = replace(reported(h.Field.CFO_RESIDUAL), origin=h.Origin.DERIVED, formula=f)
        self.assertEqual(v.field, h.Field.CFO_RESIDUAL)

    def test_cash_debt_known_double_counting_rejected(self):
        a = reported(h.Field.CASH_INVESTMENTS, "a")
        b = replace(a, input_id="b", sources=(), origin=h.Origin.PROXY,
                    manual=h.ManualIdentity("analyst", "2026-10-12T00:00:00Z", "synthetic operand"))
        f = h.Formula("sum", 1, h.FormulaKind.COMPONENT_TOTAL, "a+b", ("a", "b"),
                      False, False, True, ("scope-note",))
        total = replace(a, input_id="total", origin=h.Origin.DERIVED, formula=f)
        with self.assertRaises(h.InputError):
            annual(a, b, total)
        annual(a, replace(b, coverage_keys=("population-b",)), total)

    def test_missing_and_cyclic_formula_operands(self):
        a = reported(h.Field.REVENUE, "a")
        f = h.Formula("sum", 1, h.FormulaKind.COMPONENT_TOTAL, "b", ("b",),
                      False, False, True, ("scope-note",))
        with self.assertRaises(h.InputError):
            annual(replace(a, origin=h.Origin.DERIVED, formula=f))
        b = replace(a, input_id="b", origin=h.Origin.DERIVED, formula=replace(f, operands=("a",)))
        with self.assertRaises(h.InputError):
            annual(replace(a, origin=h.Origin.DERIVED, formula=f), b)

    def test_scope_reference_must_bind(self):
        a = reported(h.Field.REVENUE, "a")
        f = h.Formula("sum", 1, h.FormulaKind.COMPONENT_TOTAL, "a", ("a",),
                      False, False, True, ("nonexistent",))
        with self.assertRaises(h.InputError):
            annual(a, replace(a, input_id="total", origin=h.Origin.DERIVED, formula=f))

    def test_all_required_fields_explicit(self):
        b = annual()
        self.assertEqual(set(b.unresolved_required_fields), set(h.Field))
        with self.assertRaises(h.InputError):
            replace(b, inputs=b.inputs[:-1])

    def test_bridge_and_separately_dated_shares(self):
        v = reported(h.Field.SHARES)
        self.assertEqual(v.as_of, date(2025, 10, 1))
        for field in (h.Field.CASH_INVESTMENTS, h.Field.DEBT_LEASES, h.Field.OTHER_BRIDGE):
            with self.assertRaises(h.InputError):
                replace(unknown(field), as_of=date(2025, 10, 1))
        with self.assertRaises(h.InputError):
            replace(unknown(h.Field.CFO), as_of=P.annual_end)
        self.assertIsNone(replace(unknown(h.Field.SHARES), as_of=None).as_of)
        with self.assertRaises(h.InputError):
            replace(v, as_of=None)

    def test_complete_totals_cannot_hide_partial_operands(self):
        a = reported(h.Field.CASH_INVESTMENTS, "a")
        f = h.Formula("sum", 1, h.FormulaKind.COMPONENT_TOTAL, "a", ("a",),
                      False, True, True, ("scope-note",))
        total = replace(a, input_id="total", origin=h.Origin.DERIVED, formula=f,
                        completeness=h.Completeness.COMPLETE)
        with self.assertRaises(h.InputError):
            annual(a, total)
        annual(replace(a, completeness=h.Completeness.COMPLETE), total)

    def test_operating_expense_bridge_operand_scope(self):
        revenue = reported(h.Field.REVENUE, "revenue")
        expense = replace(reported(h.Field.EBIT, "expense"), sources=(), origin=h.Origin.PROXY,
            manual=h.ManualIdentity("analyst", "2026-10-12T00:00:00Z", "synthetic classification"),
            coverage_keys=("operating-costs",))
        f = h.Formula("ebit", 1, h.FormulaKind.OPERATING_EXPENSE_BRIDGE, "revenue-expense",
                      ("revenue", "expense"), True, False, True, ("scope-note",))
        result = replace(reported(h.Field.EBIT, "result"), origin=h.Origin.DERIVED, formula=f)
        with self.assertRaises(h.InputError):
            annual(revenue, expense, result)
        annual(revenue, replace(expense, role="operating_expense", scope_status=h.Scope.OPERATING_ONLY), result)

    def test_empty_short_and_specialized_histories(self):
        b = h.HistoryBundle("empty", 1, 2115436, (), ("no selected history",))
        self.assertEqual(b.annuals, ())
        with self.assertRaises(h.InputError):
            replace(b, history_exceptions=())
        for cik in h.SPECIALIZED_CIKS:
            with self.assertRaises(h.InputError):
                replace(b, cik=cik)
        with self.assertRaises(h.InputError):
            replace(history(), annuals=(annual(), annual()))

    def test_coverage_not_sufficiency_or_scores(self):
        result = h.coverage(history(reported()))
        self.assertEqual(result['revenue']['reported'], 1)
        self.assertEqual(result['revenue']['completeness:partial'], 1)
        self.assertEqual(result['ebit']['unavailable'], 1)
        self.assertNotIn("ready", result)

    def test_closed_deterministic_serialization(self):
        b = history(reported())
        payload = h.serialize(b)
        self.assertEqual(h.deserialize(payload), b)
        self.assertEqual(h.serialize(h.deserialize(payload)), payload)
        for text in (payload.replace(h.SCHEMA, "schema-5"),
                     payload.replace('"schema":', '"schema":"bad","schema":', 1)):
            with self.assertRaises(h.InputError):
                h.deserialize(text)
        doc = json.loads(payload)
        doc['bundle']['fields']['confidence'] = 1
        with self.assertRaises(h.InputError):
            h.deserialize(json.dumps(doc))

    def test_frozen_exclusion_mapping(self):
        root = Path(__file__).resolve().parents[2]
        rows = json.loads((root / 'docs/universe/phase-1h5-issuer-validation.json').read_text())['rows']
        self.assertEqual(h.SPECIALIZED_CIKS, frozenset(r['cik'] for r in rows
            if r['classification'] == 'SPECIALIZED_METHODOLOGY_REQUIRED'))

    def test_frozen_pilot_artifact_preservation(self):
        root = Path(__file__).resolve().parents[2] / 'docs/company-data-preparation'
        expected = {
            'aapl-analyst-nwc-bundle.json': '85226f5213247abfc7aedf0ec11f0d99ff69c7f1a9746e4db7dd764e0d7f45c2',
            'aapl-reported-cash-flow-bundle.json': 'd185b995c566d6bfb3b165627283b5ab52edc8ead1e62332d3d9458d0667b747',
            'googl-analyst-nwc-bundle.json': 'a8a45520d79bdedbdeeae398c1ea16cbe3639e43fed4300998b109176e4aafdb',
            'googl-reported-cash-flow-bundle.json': '97ca73213b6bb46dfdaec67f930d3abd0cfbd6d1a17e50047998c0b2764f509f',
            'msft-analyst-nwc-bundles.json': '4242d8bd0ca6a5b1dac2d08f60b0cfb18bdc6466862d1c4185e7046922c906c1',
            'msft-reported-cash-flow-bundles.json': 'c3c35e020066f0887d9d8fe493f975afe9e6f0ea4b1785d2f341691ebb49d993',
            'msft-cash-interest-annotations.json': '5d01dfc0880fa38f7d421f7ee75fb7ed57e6b346f9984e2ec979d0a124d719bc',
        }
        for filename, digest in expected.items():
            self.assertEqual(hashlib.sha256((root / filename).read_bytes()).hexdigest(), digest)
        from valuation_platform.normalization.output import SCHEMA_VERSION
        self.assertEqual(SCHEMA_VERSION, '5')


if __name__ == '__main__':
    unittest.main()
