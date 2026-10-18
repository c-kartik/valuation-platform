"""Synthetic Stage C inputs only; no actual META balances/shares/valuation."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal as D, Inexact, ROUND_DOWN, Rounded, localcontext
import json
import unittest

from tests.valuation.test_discounting import stage_a, terminal_assumptions
from tests.valuation.test_forecast import synthetic_year
from valuation_platform.analyst.historical_inputs import ManualIdentity
from valuation_platform.valuation.bridge import (
    AWARD_POLICY, BridgeComponent, BridgeInputs, BridgeObservation, BridgeValidationError,
    ComponentRole as Role, PopulationCoverage, ValuationShares,
    bridge_to_dict, bridge_to_per_share, serialize_bridge,
)
from valuation_platform.valuation.discounting import discount_to_enterprise_value, enterprise_value_to_dict


DAY = date(2025, 12, 31)
REVIEW = ManualIdentity("Synthetic fixture author", "2000-01-01T00:00:00+00:00",
                        "Synthetic coverage/omission assumptions only; not an actual approval.")


def component(identifier, role, amount, **changes):
    values = dict(component_id=identifier, company_cik=123, role=role, amount=D(amount), as_of=DAY,
                  population_id="synthetic-population:" + identifier, origin="synthetic", precision="INF",
                  source_references=("synthetic:source:" + identifier,),
                  decision_references=("synthetic:decision:" + identifier,), rationale="Synthetic magnitude only.")
    values.update(changes)
    return BridgeComponent(**values)


def observation(identifier, role, disposition="OMISSION", **changes):
    values = dict(observation_id=identifier, company_cik=123, role=role, disposition=disposition,
                  population_id="synthetic-population:" + identifier, value=None, as_of=None,
                  unit="USD", precision=None, origin="synthetic", source_references=(),
                  decision_references=("synthetic:decision:" + identifier,),
                  rationale="Explicit synthetic omission assumption; unknown amount, not a reported zero.")
    values.update(changes)
    return BridgeObservation(**values)


def valuation_shares(**changes):
    values = dict(company_cik=123, shares=D(4), observation_date=DAY, class_id="synthetic-common",
                  equivalence_convention="single_common_class", award_policy=AWARD_POLICY,
                  award_policy_references=("synthetic:award-policy",),
                  source_references=("synthetic:share-source",),
                  decision_references=("synthetic:share-decision",), precision="INF",
                  rationale="Synthetic share basis; no actual issuance or award selection.")
    values.update(changes)
    return ValuationShares(**values)


def inputs(components=None, observations=(), **changes):
    if components is None:
        components = (component("asset-a", Role.ELIGIBLE_ASSET, "10"),
                      component("asset-b", Role.ELIGIBLE_ASSET, "2"),
                      component("financing", Role.FINANCING_CLAIM, "20"),
                      component("claim", Role.OTHER_EQUITY_CLAIM, "3"))
    coverage = tuple(PopulationCoverage(
        role, tuple(c.population_id for c in components if c.role is role),
        tuple(n.observation_id for n in observations if n.role is role and n.disposition == "OMISSION"),
        REVIEW, ("synthetic:coverage:" + role.value,),
    ) for role in Role)
    values = dict(components=components, observations=observations, shares=valuation_shares(),
                  coverage=coverage, input_basis="SYNTHETIC_FIXTURE", valuation_class_id="synthetic-common",
                  unresolved_requirements=())
    values.update(changes)
    return BridgeInputs(**values)


def flat_stage_b():
    # Five annual FCFFs of 8, g=0 and terminal FCFF=8 at WACC=.25:
    # finite five-year PV + perpetuity terminal PV = 8/.25 = 32 exactly.
    years = tuple(synthetic_year(i, revenue_growth=D(0)) for i in range(1, 6))
    a = stage_a(forecast_years=years, terminal_growth=D(0))
    terminal = terminal_assumptions(operating_margin=D(".20"), operating_tax_rate=D(".25"),
                                   d_and_a_percent_revenue=D(".05"), investment_percent_revenue=D(".10"),
                                   working_capital_cash_requirement_percent_revenue=D(".02"))
    return discount_to_enterprise_value(a, terminal)


class BridgeTests(unittest.TestCase):
    def test_independent_signed_bridge_and_subtotals(self):
        b = flat_stage_b()
        self.assertEqual(b.enterprise_value, D(32))
        result = bridge_to_per_share(b, inputs())
        self.assertEqual((result.eligible_assets, result.financing_claims, result.other_equity_claims),
                         (D(12), D(20), D(3)))
        # 32 + (10+2) -20 -3 =21; 21/4 =5.25.
        self.assertEqual((result.equity_value, result.valuation_shares, result.value_per_share),
                         (D(21), D(4), D("5.25")))
        self.assertEqual({x.component.component_id: x.signed_contribution for x in result.contributions},
                         {"asset-a": D(10), "asset-b": D(2), "financing": D(-20), "claim": D(-3)})

    def test_integrated_a_b_c_existing_independent_fixture(self):
        b = discount_to_enterprise_value(stage_a(), terminal_assumptions())
        self.assertEqual(b.enterprise_value, D("77.5770603520"))
        result = bridge_to_per_share(b, inputs())
        # 77.5770603520 +12 -20 -3 =66.5770603520; divide by4.
        self.assertEqual(result.equity_value, D("66.5770603520"))
        self.assertEqual(result.value_per_share, D("16.6442650880"))

    def test_negative_equity_and_per_share_not_clipped(self):
        data = inputs()
        changed = replace(data, components=tuple(replace(c, amount=D(100))
                          if c.role is Role.FINANCING_CLAIM else c for c in data.components))
        result = bridge_to_per_share(flat_stage_b(), changed)
        self.assertEqual((result.equity_value, result.value_per_share), (D(-59), D("-14.75")))

    def test_non_operands_and_null_omission_retained_without_zero_conversion(self):
        notes = (observation("support", Role.ELIGIBLE_ASSET, "SUPPORT", value=D(999), precision="-3",
                             source_references=("synthetic:support",), as_of=date(2026, 1, 23)),
                 observation("excluded", Role.FINANCING_CLAIM, "EXCLUDED", value=D(999), precision="INF",
                             source_references=("synthetic:excluded",)),
                 observation("extra-unknown", Role.OTHER_EQUITY_CLAIM))
        result = bridge_to_per_share(flat_stage_b(), inputs(observations=notes))
        self.assertEqual(result.equity_value, D(21))
        payload = bridge_to_dict(result)
        by_id = {v["observation_id"]: v for v in payload["inputs"]["observations"]}
        self.assertIsNone(by_id["extra-unknown"]["value"])
        self.assertEqual(by_id["extra-unknown"]["source_references"], [])
        self.assertEqual(len(result.contributions), 4)
        with self.assertRaises(BridgeValidationError):
            replace(notes[-1], value=D(0), precision="INF", source_references=("synthetic:fake-zero",))

    def test_empty_populations_require_explicit_reviewed_omissions(self):
        with self.assertRaisesRegex(BridgeValidationError, "Empty populations"):
            PopulationCoverage(Role.OTHER_EQUITY_CLAIM, (), (), REVIEW, ("synthetic:review",))
        with self.assertRaises(BridgeValidationError):
            replace(inputs(), coverage=())
        omissions = tuple(observation("omit:" + role.value, role) for role in Role)
        declared = inputs(components=(), observations=omissions)
        result = bridge_to_per_share(flat_stage_b(), declared)
        self.assertEqual(result.equity_value, D(32))
        self.assertEqual(result.value_per_share, D(8))
        self.assertEqual(result.contributions, ())
        self.assertTrue(all(n.value is None for n in result.inputs.observations))
        with self.assertRaises(BridgeValidationError):
            PopulationCoverage(Role.ELIGIBLE_ASSET, ("p",), (), None, ("synthetic:review",))

    def test_coverage_links_and_exact_role_population_bindings(self):
        data = inputs()
        bad_declarations = (
            replace(data.coverage[0], population_ids=("missing-population",)),
            replace(data.coverage[0], omission_references=("missing-omission",)),
        )
        for bad in bad_declarations:
            with self.assertRaises(BridgeValidationError):
                replace(data, coverage=(bad, *data.coverage[1:]))
        notes = (observation("excluded", Role.ELIGIBLE_ASSET, "EXCLUDED"),)
        valid = inputs(observations=notes)
        with self.assertRaises(BridgeValidationError):
            replace(valid, coverage=(replace(valid.coverage[0], omission_references=("excluded",)),
                                     *valid.coverage[1:]))
        omission = observation("omit", Role.FINANCING_CLAIM)
        valid = inputs(observations=(omission,))
        with self.assertRaises(BridgeValidationError):
            replace(valid, observations=())

    def test_unresolved_required_items_block_even_with_review_declarations(self):
        data = replace(inputs(), unresolved_requirements=("eligible cash reserve unknown",))
        with self.assertRaisesRegex(BridgeValidationError, "Unresolved required"):
            bridge_to_per_share(flat_stage_b(), data)

    def test_missing_nonfinite_negative_or_wrong_numeric_operand(self):
        source = inputs().components[0]
        for amount in (None, True, 1, .1, "1", D(-1), D("NaN"), D("sNaN"), D("Infinity")):
            with self.subTest(amount=amount), self.assertRaises(BridgeValidationError):
                replace(source, amount=amount)
        # A supplied reported/synthetic zero is valid; it is not inferred from absence.
        self.assertEqual(replace(source, amount=D(0)).amount, D(0))

    def test_company_date_unit_scale_and_observation_company(self):
        data = inputs()
        for change in ({"company_cik": 456}, {"as_of": date(2026, 1, 23)}):
            bad = replace(data, components=(replace(data.components[0], **change), *data.components[1:]))
            with self.assertRaisesRegex(BridgeValidationError, "Company/date"):
                bridge_to_per_share(flat_stage_b(), bad)
        for change in ({"unit": "USD millions"}, {"unit": "shares"}, {"scale": 1000000},
                       {"scale": True}, {"as_of": None}, {"company_cik": True}):
            with self.subTest(change=change), self.assertRaises(BridgeValidationError):
                replace(data.components[0], **change)
        foreign = observation("foreign", Role.ELIGIBLE_ASSET, "SUPPORT", company_cik=456)
        with self.assertRaisesRegex(BridgeValidationError, "Observation company"):
            bridge_to_per_share(flat_stage_b(), inputs(observations=(foreign,)))

    def test_invalid_shares_declared_class_and_award_conventions(self):
        for value in (None, True, 1, .1, "4", D(0), D(-1), D("NaN"), D("Infinity")):
            with self.subTest(value=value), self.assertRaises(BridgeValidationError):
                valuation_shares(shares=value)
        for change in ({"unit": "USD"}, {"scale": 1000000}, {"equivalence_convention": "infer-class-sum"},
                       {"award_policy": "sbc_addback_plus_full_dilution"}, {"award_policy_references": ()}):
            with self.subTest(change=change), self.assertRaises(BridgeValidationError):
                valuation_shares(**change)
        with self.assertRaisesRegex(BridgeValidationError, "class mismatch"):
            replace(inputs(), shares=valuation_shares(class_id="different-common-class"))
        for change in ({"company_cik": 456}, {"observation_date": date(2026, 1, 23)}):
            with self.assertRaises(BridgeValidationError):
                bridge_to_per_share(flat_stage_b(), replace(inputs(), shares=valuation_shares(**change)))

    def test_duplicate_ids_and_numeric_population_identity(self):
        data = inputs()
        for changed in (replace(data.components[1], component_id=data.components[0].component_id),
                        replace(data.components[1], population_id=data.components[0].population_id)):
            with self.assertRaises(BridgeValidationError):
                replace(data, components=(data.components[0], changed, *data.components[2:]))
        note = observation("asset-a", Role.ELIGIBLE_ASSET, "SUPPORT")
        with self.assertRaises(BridgeValidationError):
            inputs(observations=(note,))

    def test_declared_parent_child_alternatives_and_embedded_finance_lease(self):
        data = inputs()
        for change in ({"overlap_references": ("asset-b",)},
                       {"alternative_references": ("asset-b",)}, {"overlaps_forecast": True}):
            with self.subTest(change=change), self.assertRaisesRegex(BridgeValidationError, "overlap"):
                replace(data, components=(replace(data.components[0], **change), *data.components[1:]))
        for reference_field in ("overlap_references", "alternative_references"):
            parent = component("named-financing", Role.FINANCING_CLAIM, "20",
                               **{reference_field: ("embedded-lease",)})
            child = component("embedded-lease", Role.FINANCING_CLAIM, "2")
            with self.assertRaisesRegex(BridgeValidationError, "overlap"):
                inputs(components=(*data.components[:2], parent, child, data.components[-1]))
        fair = component("notes-fair", Role.FINANCING_CLAIM, "20", alternative_references=("notes-face",))
        face = component("notes-face", Role.FINANCING_CLAIM, "21")
        with self.assertRaises(BridgeValidationError):
            inputs(components=(*data.components[:2], fair, face, data.components[-1]))

    def test_overlap_with_support_is_nonadditive_and_dangling_refs_fail(self):
        data = inputs()
        support = observation("embedded-lease", Role.FINANCING_CLAIM, "SUPPORT", value=D(2), precision="INF",
                              source_references=("synthetic:lease",))
        parent = replace(data.components[2], overlap_references=("embedded-lease",))
        valid = inputs(components=(*data.components[:2], parent, data.components[-1]), observations=(support,))
        self.assertEqual(bridge_to_per_share(flat_stage_b(), valid).financing_claims, D(20))
        with self.assertRaisesRegex(BridgeValidationError, "reference"):
            replace(valid, observations=())
        with self.assertRaisesRegex(BridgeValidationError, "reference"):
            replace(data, components=(replace(data.components[0], overlap_references=("asset-a",)),
                                      *data.components[1:]))

    def test_references_and_immutable_input_collections_validated_consistently(self):
        source = inputs().components[0]
        for change in ({"source_references": ()}, {"decision_references": (" ",)},
                       {"overlap_references": ["asset-b"]}, {"source_references": ("x", "x")},
                       {"precision": "unknown"}, {"origin": "unavailable"}):
            with self.subTest(change=change), self.assertRaises(BridgeValidationError):
                replace(source, **change)
        with self.assertRaises(BridgeValidationError):
            replace(inputs(), components=list(inputs().components))
        with self.assertRaises(BridgeValidationError):
            replace(inputs(), input_basis="")
        with self.assertRaises(BridgeValidationError):
            replace(inputs(), convention_version="unsupported")

    def test_malformed_or_altered_stage_b_rejected(self):
        b = flat_stage_b()
        malformed = [None, {}, replace(b, stage_a=None), replace(b, terminal_assumptions=None),
                     replace(b, convention_version="unsupported"), replace(b, years=list(b.years)),
                     replace(b, years=b.years[:-1]), replace(b, terminal=None),
                     replace(b, years=(b.years[1], b.years[0], *b.years[2:])),
                     replace(b, years=(replace(b.years[0], period_index=True), *b.years[1:])),
                     replace(b, years=(replace(b.years[0], discount_factor=D(99)), *b.years[1:])),
                     replace(b, years=(replace(b.years[0], pv_fcff=D("NaN")), *b.years[1:])),
                     replace(b, terminal=replace(b.terminal, fcff=D(99))),
                     replace(b, terminal=replace(b.terminal, tax=1))]
        for field in ("terminal_value", "pv_terminal_value", "pv_explicit_fcff", "enterprise_value"):
            malformed.append(replace(b, **{field: D(99)}))
            malformed.append(replace(b, **{field: None}))
        for index, value in enumerate(malformed):
            with self.subTest(index=index), self.assertRaises(BridgeValidationError):
                bridge_to_per_share(value, inputs())

    def test_public_bridge_inputs_revalidated(self):
        bad = deepcopy(inputs())
        object.__setattr__(bad.components[0], "amount", None)
        with self.assertRaises(BridgeValidationError):
            bridge_to_per_share(flat_stage_b(), bad)

    def test_immutable_traceable_deterministic_output_and_no_source_mutation(self):
        b, data = flat_stage_b(), inputs(observations=(observation("unknown", Role.OTHER_EQUITY_CLAIM),))
        before = deepcopy((b, data))
        result = bridge_to_per_share(b, data)
        payload = bridge_to_dict(result)
        self.assertIs(result.stage_b, b)
        self.assertIs(result.inputs, data)
        self.assertEqual(payload["stage_b"], enterprise_value_to_dict(b))
        self.assertEqual(payload["inputs"]["input_basis"], "SYNTHETIC_FIXTURE")
        self.assertEqual(payload["inputs"]["coverage"][0]["review"]["author"], REVIEW.author)
        self.assertEqual(payload["semantic_input_review"], "NOT_ASSESSED_BY_CALCULATOR")
        self.assertIn("not authenticated approvals", payload["limitations"][0])
        self.assertEqual(json.loads(serialize_bridge(result)), payload)
        self.assertEqual(serialize_bridge(result), serialize_bridge(bridge_to_per_share(b, data)))
        self.assertEqual((b, data), before)
        payload["stage_b"]["stage_a"]["anchor"]["source_details"]["basis"] = "changed copy"
        self.assertNotEqual(payload, bridge_to_dict(result))
        for model, field in ((result, "equity_value"), (result.contributions[0], "signed_contribution"),
                             (data, "input_basis"), (data.components[0], "amount"), (data.shares, "shares")):
            with self.assertRaises(FrozenInstanceError):
                setattr(model, field, None)

    def test_component_order_does_not_change_arithmetic(self):
        data = inputs()
        original = bridge_to_per_share(flat_stage_b(), data)
        permuted = bridge_to_per_share(flat_stage_b(), replace(data, components=tuple(reversed(data.components))))
        self.assertEqual(original.contributions, permuted.contributions)
        self.assertEqual(original.value_per_share, permuted.value_per_share)

    def test_caller_context_and_error_flags_isolated(self):
        b = flat_stage_b()
        data = replace(inputs(), shares=valuation_shares(shares=D(63)))
        with localcontext() as caller:
            caller.prec = 3
            caller.rounding = ROUND_DOWN
            caller.traps[Inexact] = True
            caller.clear_flags()
            caller.flags[Rounded] = True
            before = caller.copy()
            result = bridge_to_per_share(b, data)
            self.assertEqual(result.value_per_share, D("0." + "3" * 50))  # 21/63 =1/3
            bad = replace(b, enterprise_value=D("sNaN"))
            with self.assertRaises(BridgeValidationError):
                bridge_to_per_share(bad, data)
            self.assertEqual((caller.prec, caller.rounding, caller.traps, caller.flags),
                             (before.prec, before.rounding, before.traps, before.flags))
        with localcontext() as caller:
            caller.prec = 80
            self.assertEqual(result, bridge_to_per_share(b, data))

    def test_arithmetic_overflow_rejected(self):
        data = inputs()
        huge = tuple(replace(c, amount=D("9e999999")) if c.role is Role.ELIGIBLE_ASSET else c
                     for c in data.components)
        with self.assertRaises(BridgeValidationError):
            bridge_to_per_share(flat_stage_b(), replace(data, components=huge))

    def test_no_automatic_actual_candidate_or_share_selection(self):
        with self.assertRaises(BridgeValidationError):
            bridge_to_per_share(flat_stage_b(), None)
        with self.assertRaises(TypeError):
            bridge_to_per_share(flat_stage_b())
        data = inputs()
        result = bridge_to_per_share(flat_stage_b(), data)
        self.assertTrue(all(c.origin == "synthetic" and c.company_cik == 123 for c in data.components))
        self.assertEqual(len(result.contributions), len(data.components))
        self.assertEqual(result.valuation_shares, data.shares.shares)
        # This checks explicit operands/declarations, not hidden economic duplication.


if __name__ == "__main__":
    unittest.main()
