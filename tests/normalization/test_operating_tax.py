"""Tests for pure operating-tax policy/readiness evaluation."""

from __future__ import annotations

import unittest
from dataclasses import replace
from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext

from valuation_platform.normalization.concepts import ConceptKey, FinancialMetric
from valuation_platform.normalization.models import (
    AmbiguityReason,
    AmbiguousHistoricalMetric,
    FactEvidence,
    EvidenceSourceKind,
    HistoricalFilingResult,
    HistoricalPeriod,
    MissingHistoricalMetric,
    MissingReason,
    NormalizedHistoricalFinancials,
    NormalizedHistoricalValue,
)
from valuation_platform.normalization.operating_tax import (
    OperatingTaxEvidenceRequirement,
    OperatingTaxPair,
    OperatingTaxPolicy,
    OperatingTaxReadinessContext,
    OperatingTaxReadinessError,
    OperatingTaxReadinessStatus,
    OperatingTaxRowDecision,
    OperatingTaxRowReference,
    StatutoryRateAnchor,
    TaxMonetaryBasis,
    evaluate_operating_tax_readiness,
)
from valuation_platform.normalization.tax_evidence import (
    SelectedTaxFiling,
    TaxBridgeStyle,
    TaxDisplayedUnit,
    TaxEvidenceStatus,
    TaxIncomeBase,
    TaxPairing,
    TaxProposedTreatment,
    TaxReconciliationRowInput,
    TaxRowSource,
    TaxSignEvidence,
    normalize_tax_reconciliation_bridge,
)
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity


REPORT_DATE = date(2025, 12, 31)
START_DATE = date(2025, 1, 1)
ACCESSION = "0000001000-26-000001"


def company(cik: int = 1000) -> SECCompanyIdentity:
    return SECCompanyIdentity(
        ticker="TEST",
        cik=cik,
        cik_padded=f"{cik:010d}",
        company_name="Test Company",
        source_url="https://www.sec.gov/files/company_tickers.json",
        retrieved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def filing(accession: str = ACCESSION, report_date: date = REPORT_DATE) -> SECFiling:
    return SECFiling(
        accession_number=accession,
        form="10-K",
        filing_date=date(2026, 2, 1),
        report_date=report_date,
        primary_document="test-20251231.htm",
    )


def evidence(metric: FinancialMetric, value: int | Decimal) -> FactEvidence:
    concepts = {
        FinancialMetric.OPERATING_INCOME: "OperatingIncomeLoss",
        FinancialMetric.PRETAX_INCOME: "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    }
    return FactEvidence(
        source_kind=EvidenceSourceKind.COMPANY_FACTS,
        source_url="https://data.sec.gov/api/xbrl/companyfacts/CIK0000001000.json",
        taxonomy="us-gaap",
        concept=concepts[metric],
        value=value,
        unit="USD",
        start=START_DATE,
        end=REPORT_DATE,
        accession_number=ACCESSION,
        observation_form="10-K",
        observation_filed=date(2026, 2, 1),
        fiscal_year=2025,
        fiscal_period="FY",
        frame=None,
    )


def normalized_value(
    metric: FinancialMetric,
    value: int | Decimal,
) -> NormalizedHistoricalValue:
    source = evidence(metric, value)
    return NormalizedHistoricalValue(
        metric=metric,
        value=value,
        unit="USD",
        period=HistoricalPeriod(START_DATE, REPORT_DATE),
        chosen_source=source,
        confirming_sources=(),
    )


def financials(
    *, operating_income: object = 800_000_000, pretax_income: object = 1_000_000_000,
    cik: int = 1000,
) -> tuple[NormalizedHistoricalFinancials, HistoricalFilingResult]:
    def result(metric: FinancialMetric, supplied: object):
        if supplied == "missing":
            return MissingHistoricalMetric(metric, MissingReason.NO_VALID_CURRENT_ANNUAL_OBSERVATION, (ConceptKey("us-gaap", "Missing"),))
        if supplied == "ambiguous":
            return AmbiguousHistoricalMetric(metric, AmbiguityReason.MULTIPLE_ANNUAL_PERIODS, ())
        assert isinstance(supplied, (int, Decimal)) and not isinstance(supplied, bool)
        return normalized_value(metric, supplied)

    annual = HistoricalFilingResult(
        filing=filing(),
        metrics=(
            result(FinancialMetric.OPERATING_INCOME, operating_income),
            result(FinancialMetric.PRETAX_INCOME, pretax_income),
        ),
    )
    container = NormalizedHistoricalFinancials(
        company=company(cik),
        company_facts_source_url="https://data.sec.gov/api/xbrl/companyfacts/CIK0000001000.json",
        company_facts_retrieved_at=datetime(2026, 2, 2, tzinfo=timezone.utc),
        annual=(annual,),
    )
    return container, annual


def source(
    label: str,
    *,
    accession: str = ACCESSION,
    source_url: str = "https://www.sec.gov/Archives/test.htm",
) -> TaxRowSource:
    return TaxRowSource(
        accession_number=accession,
        source_url=source_url,
        table_identity="Income tax rate reconciliation",
        taxonomy_namespace="http://fasb.org/us-gaap/2025",
        concept=f"{label.replace(' ', '')}TaxEffect",
        raw_xbrl_value=Decimal("1"),
        context_id=f"ctx-{label}",
        report_date=REPORT_DATE,
    )


def row(
    label: str,
    value: str,
    *,
    treatment: TaxProposedTreatment = TaxProposedTreatment.INCLUDE_OPERATING,
    status: TaxEvidenceStatus = TaxEvidenceStatus.RESOLVED,
) -> TaxReconciliationRowInput:
    return TaxReconciliationRowInput(
        displayed_label=label,
        source=source(label),
        displayed_unit=TaxDisplayedUnit.RATE,
        displayed_value=Decimal(value),
        sign_evidence=TaxSignEvidence.FILING_TABLE_PRESENTATION,
        evidence_status=status,
        income_base=TaxIncomeBase.INSIDE_OPERATING_INCOME,
        pairing=TaxPairing.NONE,
        proposed_treatment=treatment,
        rationale="Synthetic evidence.",
    )


def bridge(
    rows: tuple[TaxReconciliationRowInput, ...] | None = None,
    *, reported: str = "22.0", complete: bool = True, cik: int = 1000,
):
    inputs = rows or (
        row("State", "1.0"),
        row("Foreign tax", "2.0", treatment=TaxProposedTreatment.INCLUDE_PAIRED_NET_EFFECT),
        row("Foreign credit", "-2.0", treatment=TaxProposedTreatment.INCLUDE_PAIRED_NET_EFFECT),
        row("Zero", "0.0", treatment=TaxProposedTreatment.EXCLUDE_DISCRETE_TAX_ONLY),
    )
    selected = SelectedTaxFiling(
        company=company(cik),
        filing=filing(),
        source_url="https://www.sec.gov/Archives/test.htm",
    )
    return normalize_tax_reconciliation_bridge(
        selected,
        style=TaxBridgeStyle.RATE,
        starting_value=Decimal("21.0"),
        reported_value=Decimal(reported),
        rows=inputs,
        displayed_precision=Decimal("0.1"),
        row_inventory_complete=complete,
        pretax_income=Decimal("1000"),
    )


def anchor(rate: Decimal = Decimal("21.0")) -> StatutoryRateAnchor:
    return StatutoryRateAnchor(
        1000,
        ACCESSION,
        REPORT_DATE,
        rate,
        source("Statutory rate"),
    )


def dollar_bridge(
    starting: Decimal,
    *,
    precision: Decimal,
    currency_code: str = "USD millions",
):
    selected = SelectedTaxFiling(
        company(),
        filing(),
        "https://www.sec.gov/Archives/test.htm",
    )
    return normalize_tax_reconciliation_bridge(
        selected,
        style=TaxBridgeStyle.DOLLAR,
        starting_value=starting,
        reported_value=starting,
        rows=(),
        displayed_precision=precision,
        row_inventory_complete=True,
        currency_code=currency_code,
    )


def context_with_replaced_evidence(
    readiness_context: OperatingTaxReadinessContext,
    metric: FinancialMetric,
    *,
    chosen_source: FactEvidence | None = None,
    confirming_sources: tuple[FactEvidence, ...] | None = None,
) -> OperatingTaxReadinessContext:
    metrics = list(readiness_context.filing_result.metrics)
    index = next(
        index for index, result in enumerate(metrics) if result.metric is metric
    )
    value = metrics[index]
    assert isinstance(value, NormalizedHistoricalValue)
    metrics[index] = replace(
        value,
        chosen_source=chosen_source or value.chosen_source,
        confirming_sources=(
            value.confirming_sources
            if confirming_sources is None
            else confirming_sources
        ),
    )
    filing_result = replace(
        readiness_context.filing_result,
        metrics=tuple(metrics),
    )
    financials = replace(readiness_context.financials, annual=(filing_result,))
    return replace(
        readiness_context,
        financials=financials,
        filing_result=filing_result,
    )


def policy(tax_bridge=None, *, decisions=None, pairs=None, company_cik: int = 1000, version: str = "1") -> OperatingTaxPolicy:
    tax_bridge = tax_bridge or bridge()
    refs = tuple(OperatingTaxRowReference.from_bridge(tax_bridge, index) for index in range(len(tax_bridge.rows)))
    if decisions is None:
        decisions = tuple(
            OperatingTaxRowDecision(
                reference,
                TaxProposedTreatment.INCLUDE_PAIRED_NET_EFFECT if index in (1, 2) else (
                    TaxProposedTreatment.EXCLUDE_DISCRETE_TAX_ONLY if index == 3 else TaxProposedTreatment.INCLUDE_OPERATING
                ),
                OperatingTaxEvidenceRequirement(),
                "Synthetic approved treatment.",
            )
            for index, reference in enumerate(refs)
        )
    if pairs is None:
        pairs = (OperatingTaxPair("foreign-net", (refs[1], refs[2]), "Synthetic exclusive pair."),)
    return OperatingTaxPolicy("synthetic-operating-tax", version, company_cik, tuple(decisions), tuple(pairs), "Synthetic readiness policy.")


def context(
    tax_bridge=None,
    *,
    operating_income: object = 800_000_000,
    pretax_income: object = 1_000_000_000,
    statutory_anchor=anchor(),
    basis: TaxMonetaryBasis = TaxMonetaryBasis("USD", Decimal("1000000")),
    requested_version: str = "1",
    realizability_resolved: bool = True,
) -> OperatingTaxReadinessContext:
    financial_container, annual = financials(operating_income=operating_income, pretax_income=pretax_income)
    return OperatingTaxReadinessContext(
        financial_container,
        annual,
        tax_bridge or bridge(),
        basis,
        statutory_anchor,
        "synthetic-operating-tax",
        requested_version,
        realizability_resolved,
    )


class OperatingTaxReadinessTests(unittest.TestCase):
    def test_fully_evidenced_synthetic_case_is_ready_and_preserves_zero(self) -> None:
        tax_bridge = bridge()
        result = evaluate_operating_tax_readiness(context(tax_bridge), policy(tax_bridge))
        self.assertEqual(result.status, OperatingTaxReadinessStatus.READY)
        self.assertTrue(result.is_ready)
        self.assertEqual(result.bridge.rows[3].signed_tax_amount, Decimal("0.0"))
        self.assertFalse(hasattr(result, "context"))
        self.assertEqual(tuple(decision.row.row_index for decision in result.row_decisions), (0, 1, 2, 3))
        self.assertEqual(result.pairs[0].pair_id, "foreign-net")
        self.assertFalse(hasattr(result, "operating_tax_expense"))
        with self.assertRaises(FrozenInstanceError):
            result.status = OperatingTaxReadinessStatus.MISSING_INPUT  # type: ignore[misc]
        self.assertEqual(
            result,
            evaluate_operating_tax_readiness(context(tax_bridge), policy(tax_bridge)),
        )

    def test_required_financial_metrics_enforce_exact_semantic_provenance(self) -> None:
        tax_bridge = bridge()
        valid_context = context(tax_bridge)
        operating_income = valid_context.filing_result.metrics[0]
        pretax_income = valid_context.filing_result.metrics[1]
        assert isinstance(operating_income, NormalizedHistoricalValue)
        assert isinstance(pretax_income, NormalizedHistoricalValue)
        malformed = (
            (
                FinancialMetric.OPERATING_INCOME,
                replace(operating_income.chosen_source, concept="Revenues"),
                "operating income backed by revenue",
            ),
            (
                FinancialMetric.OPERATING_INCOME,
                replace(operating_income.chosen_source, taxonomy="ifrs-full"),
                "operating income with wrong taxonomy",
            ),
            (
                FinancialMetric.OPERATING_INCOME,
                replace(operating_income.chosen_source, observation_form="10-Q"),
                "operating income with wrong form",
            ),
            (
                FinancialMetric.OPERATING_INCOME,
                replace(
                    operating_income.chosen_source,
                    source_kind=EvidenceSourceKind.FILING_XBRL,
                ),
                "operating income with wrong source kind",
            ),
            (
                FinancialMetric.PRETAX_INCOME,
                replace(pretax_income.chosen_source, concept="IncomeLossFromContinuingOperations"),
                "pretax income with wrong concept",
            ),
            (
                FinancialMetric.PRETAX_INCOME,
                replace(pretax_income.chosen_source, observation_form="10-Q"),
                "pretax income with wrong form",
            ),
        )
        for metric, bad_source, label in malformed:
            with self.subTest(label=label):
                bad_context = context_with_replaced_evidence(
                    valid_context,
                    metric,
                    chosen_source=bad_source,
                )
                with self.assertRaises(OperatingTaxReadinessError):
                    evaluate_operating_tax_readiness(
                        bad_context,
                        policy(tax_bridge),
                    )

        self.assertEqual(
            evaluate_operating_tax_readiness(
                valid_context,
                policy(tax_bridge),
            ).status,
            OperatingTaxReadinessStatus.READY,
        )

    def test_all_confirming_financial_sources_must_be_semantically_coherent(self) -> None:
        tax_bridge = bridge()
        valid_context = context(tax_bridge)
        operating_income = valid_context.filing_result.metrics[0]
        assert isinstance(operating_income, NormalizedHistoricalValue)
        valid = operating_income.chosen_source
        invalid_sources = (
            replace(valid, concept="Revenues"),
            replace(valid, accession_number="different-accession"),
            replace(valid, observation_form="10-Q"),
        )
        for invalid in invalid_sources:
            for confirming_sources in ((valid, invalid), (invalid, valid)):
                with self.subTest(
                    invalid_field=(invalid.concept, invalid.accession_number, invalid.observation_form),
                    reversed=confirming_sources[0] is invalid,
                ):
                    bad_context = context_with_replaced_evidence(
                        valid_context,
                        FinancialMetric.OPERATING_INCOME,
                        confirming_sources=confirming_sources,
                    )
                    with self.assertRaises(OperatingTaxReadinessError):
                        evaluate_operating_tax_readiness(
                            bad_context,
                            policy(tax_bridge),
                        )

    def test_statutory_anchor_requires_exact_selected_filing_source_url(self) -> None:
        tax_bridge = bridge()
        valid_context = context(tax_bridge)
        self.assertEqual(
            evaluate_operating_tax_readiness(
                valid_context,
                policy(tax_bridge),
            ).status,
            OperatingTaxReadinessStatus.READY,
        )
        assert valid_context.statutory_anchor is not None
        for unrelated_url in (
            "https://example.com/not-the-selected-filing",
            " https://www.sec.gov/Archives/test.htm ",
        ):
            with self.subTest(source_url=unrelated_url):
                bad_source = replace(
                    valid_context.statutory_anchor.source,
                    source_url=unrelated_url,
                )
                bad_anchor = replace(
                    valid_context.statutory_anchor,
                    source=bad_source,
                )
                with self.assertRaises(OperatingTaxReadinessError):
                    evaluate_operating_tax_readiness(
                        replace(valid_context, statutory_anchor=bad_anchor),
                        policy(tax_bridge),
                    )

    def test_policy_decision_order_does_not_change_meaning(self) -> None:
        tax_bridge = bridge()
        first = policy(tax_bridge)
        reversed_pair = replace(first.pairs[0], members=tuple(reversed(first.pairs[0].members)))
        second = replace(
            first,
            row_decisions=tuple(reversed(first.row_decisions)),
            pairs=(reversed_pair,),
        )
        result_one = evaluate_operating_tax_readiness(context(tax_bridge), first)
        result_two = evaluate_operating_tax_readiness(context(tax_bridge), second)
        self.assertEqual(result_one.status, result_two.status)
        self.assertEqual(result_one.row_decisions, result_two.row_decisions)
        self.assertEqual(result_one.pairs, result_two.pairs)

    def test_unresolved_row_and_representative_real_corpus_blockers_remain_blocked(self) -> None:
        blockers = (
            "META foreign and Other", "META combined SBC 2022-2024",
            "GOOGL foreign/state/SBC/Other", "MSFT foreign-credit allocation and Other",
            "AAPL foreign/state/Other and FY2025 presentation",
            "COST embedded SBC/Other and foreign/state",
        )
        for label in blockers:
            with self.subTest(label=label):
                tax_bridge = bridge((row(label, "1.0", treatment=TaxProposedTreatment.METHODOLOGY_UNRESOLVED, status=TaxEvidenceStatus.METHODOLOGY_UNRESOLVED),), reported="22.0")
                ref = OperatingTaxRowReference.from_bridge(tax_bridge, 0)
                unresolved_policy = policy(tax_bridge, decisions=(OperatingTaxRowDecision(ref, TaxProposedTreatment.METHODOLOGY_UNRESOLVED, OperatingTaxEvidenceRequirement((TaxEvidenceStatus.METHODOLOGY_UNRESOLVED,)), "Research remains unresolved."),), pairs=())
                result = evaluate_operating_tax_readiness(context(tax_bridge), unresolved_policy)
                self.assertEqual(result.status, OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED)

    def test_unreconciled_and_incomplete_bridges_are_typed(self) -> None:
        unreconciled = bridge(reported="30.0")
        self.assertEqual(evaluate_operating_tax_readiness(context(unreconciled), policy(unreconciled)).status, OperatingTaxReadinessStatus.UNRECONCILED_BRIDGE)
        missing_row = row("Missing", "1.0")
        missing_row = replace(missing_row, displayed_value=None, sign_evidence=None, evidence_status=TaxEvidenceStatus.MISSING_EVIDENCE)
        incomplete = bridge((missing_row,), complete=False)
        self.assertEqual(evaluate_operating_tax_readiness(context(incomplete), policy(incomplete, decisions=(), pairs=())).status, OperatingTaxReadinessStatus.MISSING_INPUT)
        ambiguous_row = replace(
            missing_row,
            evidence_status=TaxEvidenceStatus.SOURCE_CONFLICT,
        )
        ambiguous = bridge((ambiguous_row,), complete=False)
        self.assertEqual(
            evaluate_operating_tax_readiness(
                context(ambiguous),
                policy(ambiguous, decisions=(), pairs=()),
            ).status,
            OperatingTaxReadinessStatus.AMBIGUOUS_INPUT,
        )

    def test_missing_and_ambiguous_financial_inputs_are_typed(self) -> None:
        tax_bridge = bridge()
        self.assertEqual(evaluate_operating_tax_readiness(context(tax_bridge, operating_income="missing"), policy(tax_bridge)).status, OperatingTaxReadinessStatus.MISSING_INPUT)
        self.assertEqual(evaluate_operating_tax_readiness(context(tax_bridge, pretax_income="ambiguous"), policy(tax_bridge)).status, OperatingTaxReadinessStatus.AMBIGUOUS_INPUT)

    def test_missing_statutory_anchor_is_typed(self) -> None:
        tax_bridge = bridge()
        result = evaluate_operating_tax_readiness(context(tax_bridge, statutory_anchor=None), policy(tax_bridge))
        self.assertEqual(result.status, OperatingTaxReadinessStatus.MISSING_INPUT)

    def test_policy_version_and_supported_accession_fail_explicitly(self) -> None:
        tax_bridge = bridge()
        wrong_id = evaluate_operating_tax_readiness(
            replace(context(tax_bridge), requested_policy_id="other-policy"),
            policy(tax_bridge),
        )
        self.assertEqual(
            wrong_id.status,
            OperatingTaxReadinessStatus.POLICY_MISMATCH,
        )
        mismatch = evaluate_operating_tax_readiness(context(tax_bridge, requested_version="2"), policy(tax_bridge))
        self.assertEqual(mismatch.status, OperatingTaxReadinessStatus.POLICY_MISMATCH)
        unsupported = replace(policy(tax_bridge), supported_accessions=("other-accession",))
        self.assertEqual(evaluate_operating_tax_readiness(context(tax_bridge), unsupported).status, OperatingTaxReadinessStatus.UNSUPPORTED_POLICY)

    def test_issuer_filing_report_date_and_ownership_mismatches_raise(self) -> None:
        tax_bridge = bridge()
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(context(tax_bridge), policy(tax_bridge, company_cik=2000))
        other_company_bridge = bridge(cik=2000)
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(
                context(other_company_bridge),
                policy(other_company_bridge, company_cik=1000),
            )
        financial_container, annual = financials()
        external = replace(annual, filing=filing("different-accession"))
        bad_context = replace(context(tax_bridge), financials=financial_container, filing_result=external)
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(bad_context, policy(tax_bridge))
        mismatched = replace(annual, filing=filing("different-accession"))
        mismatched_container = replace(financial_container, annual=(mismatched,))
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(
                replace(context(tax_bridge), financials=mismatched_container, filing_result=mismatched),
                policy(tax_bridge),
            )
        wrong_date = replace(annual, filing=filing(report_date=date(2025, 12, 30)))
        wrong_date_container = replace(financial_container, annual=(wrong_date,))
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(
                replace(context(tax_bridge), financials=wrong_date_container, filing_result=wrong_date),
                policy(tax_bridge),
            )

    def test_pair_membership_is_complete_exclusive_and_deterministic(self) -> None:
        tax_bridge = bridge()
        refs = tuple(OperatingTaxRowReference.from_bridge(tax_bridge, index) for index in range(4))
        with self.assertRaises(OperatingTaxReadinessError):
            policy(tax_bridge, pairs=(OperatingTaxPair("one", (refs[1], refs[2]), "One."), OperatingTaxPair("two", (refs[1], refs[0]), "Two.")))
        incomplete = policy(tax_bridge, pairs=())
        self.assertEqual(evaluate_operating_tax_readiness(context(tax_bridge), incomplete).status, OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED)

    def test_duplicate_decision_and_unsupported_row_identity_are_rejected_or_blocked(self) -> None:
        tax_bridge = bridge()
        valid = policy(tax_bridge)
        with self.assertRaises(OperatingTaxReadinessError):
            replace(valid, row_decisions=(valid.row_decisions[0], valid.row_decisions[0]))
        bad_ref = replace(valid.row_decisions[0].row, displayed_label="Different")
        bad_decisions = (replace(valid.row_decisions[0], row=bad_ref),) + valid.row_decisions[1:]
        bad_policy = replace(valid, row_decisions=bad_decisions)
        self.assertEqual(evaluate_operating_tax_readiness(context(tax_bridge), bad_policy).status, OperatingTaxReadinessStatus.METHODOLOGY_BLOCKED)

    def test_currency_and_scale_mismatches_raise(self) -> None:
        tax_bridge = bridge()
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(context(tax_bridge, basis=TaxMonetaryBasis("EUR", Decimal("1000000"))), policy(tax_bridge))
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(context(tax_bridge, basis=TaxMonetaryBasis("USD", Decimal("1"))), policy(tax_bridge))

    def test_dollar_bridge_requires_exact_currency_scale_label(self) -> None:
        inputs = (replace(row("State", "1.0"), displayed_unit=TaxDisplayedUnit.CURRENCY),)
        selected = SelectedTaxFiling(company(), filing(), "https://www.sec.gov/Archives/test.htm")
        dollar_bridge = normalize_tax_reconciliation_bridge(
            selected, style=TaxBridgeStyle.DOLLAR, starting_value=Decimal("210"), reported_value=Decimal("211"),
            rows=inputs, displayed_precision=Decimal("1"), row_inventory_complete=True, currency_code="USD millions",
        )
        ref = OperatingTaxRowReference.from_bridge(dollar_bridge, 0)
        dollar_policy = policy(dollar_bridge, decisions=(OperatingTaxRowDecision(ref, TaxProposedTreatment.INCLUDE_OPERATING, OperatingTaxEvidenceRequirement(), "Approved."),), pairs=())
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(context(dollar_bridge), dollar_policy)
        valid_context = context(dollar_bridge, basis=TaxMonetaryBasis("USD", Decimal("1000000"), "USD millions"))
        self.assertEqual(evaluate_operating_tax_readiness(valid_context, dollar_policy).status, OperatingTaxReadinessStatus.READY)
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(
                context(
                    dollar_bridge,
                    basis=TaxMonetaryBasis("USD", Decimal("1"), "USD millions"),
                ),
                dollar_policy,
            )
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(
                context(
                    dollar_bridge,
                    basis=TaxMonetaryBasis(
                        "USD",
                        Decimal("1000000"),
                        "USD thousands",
                    ),
                ),
                dollar_policy,
            )

    def test_dollar_bridge_allows_zero_pretax_income(self) -> None:
        tax_bridge = dollar_bridge(Decimal("0"), precision=Decimal("1"))
        readiness_policy = policy(tax_bridge, decisions=(), pairs=())
        result = evaluate_operating_tax_readiness(
            context(
                tax_bridge,
                pretax_income=0,
                basis=TaxMonetaryBasis(
                    "USD",
                    Decimal("1000000"),
                    "USD millions",
                ),
            ),
            readiness_policy,
        )
        self.assertEqual(result.status, OperatingTaxReadinessStatus.READY)

    def test_dollar_bridge_uses_exact_local_decimal_precision(self) -> None:
        pretax_income = int("9" * 40)
        statutory_rate = Decimal("21.12345678901234567890123456789")
        scale = Decimal("1000000")
        precision = Decimal("0.00000000001")
        with localcontext() as decimal_context:
            decimal_context.prec = 200
            exact_start = (
                Decimal(pretax_income)
                * statutory_rate
                * Decimal("0.01")
                / scale
            )

        def evaluate(
            starting_value: Decimal,
            monetary_scale: Decimal = scale,
        ):
            tax_bridge = dollar_bridge(starting_value, precision=precision)
            readiness_policy = policy(tax_bridge, decisions=(), pairs=())
            return evaluate_operating_tax_readiness(
                context(
                    tax_bridge,
                    pretax_income=pretax_income,
                    statutory_anchor=anchor(statutory_rate),
                    basis=TaxMonetaryBasis(
                        "USD",
                        monetary_scale,
                        "USD millions",
                    ),
                ),
                readiness_policy,
            )

        self.assertEqual(
            evaluate(exact_start).status,
            OperatingTaxReadinessStatus.READY,
        )

        with localcontext() as decimal_context:
            decimal_context.prec = 200
            hidden_mismatch = exact_start + Decimal("1e-10")
            inside_rounding_tolerance = exact_start + Decimal("4e-12")

        with self.assertRaises(OperatingTaxReadinessError):
            evaluate(hidden_mismatch)
        self.assertEqual(
            evaluate(inside_rounding_tolerance).status,
            OperatingTaxReadinessStatus.READY,
        )
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate(exact_start, Decimal("1000"))

    def test_zero_negative_income_and_realizability_are_conservatively_blocked(self) -> None:
        tax_bridge = bridge()
        for kwargs in (
            {"operating_income": 0}, {"operating_income": -1}, {"pretax_income": -1}, {"realizability_resolved": False},
        ):
            with self.subTest(kwargs=kwargs):
                result = evaluate_operating_tax_readiness(context(tax_bridge, **kwargs), policy(tax_bridge))
                self.assertEqual(result.status, OperatingTaxReadinessStatus.LOSS_POLICY_BLOCKED)

    def test_statutory_anchor_must_match_selected_filing_and_rate_bridge(self) -> None:
        tax_bridge = bridge()
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(context(tax_bridge, statutory_anchor=replace(anchor(), rate=Decimal("20"))), policy(tax_bridge))
        with self.assertRaises(OperatingTaxReadinessError):
            evaluate_operating_tax_readiness(context(tax_bridge, statutory_anchor=replace(anchor(), accession_number="other")), policy(tax_bridge))


if __name__ == "__main__":
    unittest.main()
