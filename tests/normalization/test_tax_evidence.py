"""Tests for explicit signed income-tax reconciliation evidence."""

from __future__ import annotations

import unittest
from dataclasses import fields, replace
from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone
from decimal import Decimal

from valuation_platform.normalization.tax_evidence import (
    SelectedTaxFiling,
    TaxBridgeStyle,
    TaxDisplayedUnit,
    TaxEvidenceNormalizationError,
    TaxEvidenceStatus,
    TaxIncomeBase,
    TaxPairing,
    TaxProposedTreatment,
    TaxReconciliationRowInput,
    TaxReconciliationStatus,
    TaxRowPrecision,
    TaxRowSource,
    TaxSignEvidence,
    normalize_tax_reconciliation_bridge,
)
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity


def make_filing(
    *, cik: int = 1326801, accession: str = "0001326801-26-000001",
    report_date: date = date(2025, 12, 31), form: str = "10-K",
) -> SelectedTaxFiling:
    ticker, company_name, document = {
        1326801: ("META", "Meta Platforms, Inc.", "meta-20251231.htm"),
        789019: ("MSFT", "Microsoft Corporation", "msft-20260630.htm"),
        320193: ("AAPL", "Apple Inc.", "aapl-20240928.htm"),
    }.get(cik, ("TEST", "Test Company", "filing.htm"))
    company = SECCompanyIdentity(
        ticker=ticker,
        cik=cik,
        cik_padded=f"{cik:010d}",
        company_name=company_name,
        source_url="https://www.sec.gov/files/company_tickers.json",
        retrieved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    filing = SECFiling(
        accession_number=accession,
        form=form,
        filing_date=date(2026, 2, 1),
        report_date=report_date,
        primary_document=document,
    )
    return SelectedTaxFiling(
        company=company,
        filing=filing,
        source_url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{document}",
    )


def make_row(
    label: str,
    value: Decimal | None,
    *,
    filing: SelectedTaxFiling | None = None,
    unit: TaxDisplayedUnit = TaxDisplayedUnit.RATE,
    raw: Decimal | str | None = None,
    status: TaxEvidenceStatus = TaxEvidenceStatus.RESOLVED,
    sign: TaxSignEvidence | None = TaxSignEvidence.FILING_TABLE_PRESENTATION,
    treatment: TaxProposedTreatment = TaxProposedTreatment.METHODOLOGY_UNRESOLVED,
    pairing: TaxPairing = TaxPairing.NONE,
    rationale: str = "Explicitly supplied filing-table sign evidence.",
) -> TaxReconciliationRowInput:
    selected = filing or make_filing()
    return TaxReconciliationRowInput(
        displayed_label=label,
        source=TaxRowSource(
            accession_number=selected.accession_number,
            source_url=selected.source_url,
            table_identity="Income tax rate reconciliation",
            taxonomy_namespace="http://fasb.org/us-gaap/2025" if raw is not None else None,
            concept="ExampleTaxReconciliationConcept" if raw is not None else None,
            raw_xbrl_value=raw,
            context_id="FY2025" if raw is not None else None,
            report_date=selected.report_date,
        ),
        displayed_unit=unit,
        displayed_value=value,
        sign_evidence=sign,
        evidence_status=status,
        income_base=TaxIncomeBase.INDETERMINABLE,
        pairing=pairing,
        proposed_treatment=treatment,
        rationale=rationale,
    )


def rate_bridge(
    rows: tuple[TaxReconciliationRowInput, ...],
    *,
    starting: Decimal = Decimal("21.0"),
    reported: Decimal = Decimal("18.0"),
    pretax: Decimal = Decimal("100.0"),
    precision: Decimal = Decimal("0.1"),
    filing: SelectedTaxFiling | None = None,
):
    return normalize_tax_reconciliation_bridge(
        filing or make_filing(),
        style=TaxBridgeStyle.RATE,
        starting_value=starting,
        reported_value=reported,
        rows=rows,
        displayed_precision=precision,
        row_inventory_complete=True,
        pretax_income=pretax,
    )


class TaxEvidenceNormalizationTests(unittest.TestCase):
    def test_positive_negative_and_zero_rate_rows_use_exact_decimal(self) -> None:
        bridge = rate_bridge((
            make_row("State", Decimal("1.2")),
            make_row("Credit", Decimal("-4.2")),
            make_row("Zero", Decimal("0.0")),
        ), reported=Decimal("18.0"))
        self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.EXACT)
        self.assertEqual(
            tuple(row.signed_tax_amount for row in bridge.rows),
            (Decimal("1.200"), Decimal("-4.200"), Decimal("0.000")),
        )
        self.assertEqual(bridge.rows[2].displayed_value, Decimal("0.0"))

    def test_raw_positive_magnitude_does_not_override_explicit_negative_sign(self) -> None:
        cases = (
            ("META", 1326801, "0001326801-22-000018", date(2021, 12, 31), "Excess tax benefits related to share-based compensation", "-2.2"),
            ("GOOGL", 1652044, "0001652044-22-000019", date(2021, 12, 31), "Stock-based compensation", "-2.5"),
            ("COST", 909832, "0000909832-21-000014", date(2021, 8, 29), "Employee stock ownership plan (ESOP)", "-1.3"),
        )
        for ticker, cik, accession, report_date, label, displayed in cases:
            with self.subTest(ticker=ticker):
                selected = make_filing(cik=cik, accession=accession, report_date=report_date)
                row = make_row(
                    label,
                    Decimal(displayed),
                    filing=selected,
                    raw=abs(Decimal(displayed)),
                    treatment=TaxProposedTreatment.EXCLUDE_DISCRETE_TAX_ONLY,
                )
                bridge = rate_bridge((row,), starting=Decimal("21.0"), reported=Decimal("18.8"), filing=selected)
                normalized = bridge.rows[0]
                self.assertGreater(normalized.source.raw_xbrl_value, Decimal(0))
                self.assertLess(normalized.displayed_value, Decimal(0))
                self.assertEqual(normalized.signed_tax_amount, Decimal(displayed) * Decimal(1))
                self.assertEqual(normalized.source.concept, "ExampleTaxReconciliationConcept")

    def test_zero_and_negative_raw_values_remain_independent_evidence(self) -> None:
        selected = make_filing()
        rows = (
            make_row("Zero raw", Decimal("-1.0"), filing=selected, raw=Decimal("0")),
            make_row("Negative raw", Decimal("1.0"), filing=selected, raw=Decimal("-2")),
        )
        bridge = rate_bridge(
            rows, starting=Decimal("21"), reported=Decimal("21"), filing=selected
        )
        self.assertEqual(bridge.rows[0].source.raw_xbrl_value, Decimal("0"))
        self.assertEqual(bridge.rows[0].displayed_value, Decimal("-1.0"))
        self.assertEqual(bridge.rows[1].source.raw_xbrl_value, Decimal("-2"))
        self.assertEqual(bridge.rows[1].displayed_value, Decimal("1.0"))

    def test_conflicting_sign_evidence_state_cannot_contribute(self) -> None:
        row = make_row(
            "Conflicting sources", None, raw=Decimal("2"),
            status=TaxEvidenceStatus.SOURCE_CONFLICT, sign=None,
        )
        bridge = rate_bridge((row,))
        self.assertEqual(
            bridge.reconciliation_status,
            TaxReconciliationStatus.INCOMPLETE_EVIDENCE,
        )
        self.assertIsNone(bridge.rows[0].displayed_value)
        self.assertIsNone(bridge.rows[0].signed_tax_amount)

    def test_calculation_relationship_sign_requires_auditable_rationale(self) -> None:
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((make_row(
                "Calculated", Decimal("-1"),
                sign=TaxSignEvidence.CALCULATION_RELATIONSHIP,
                rationale="",
            ),))
        bridge = rate_bridge((make_row(
            "Calculated", Decimal("-1"),
            sign=TaxSignEvidence.CALCULATION_RELATIONSHIP,
            rationale="Computed from the filing relationship: net expense less credit.",
        ),))
        self.assertEqual(
            bridge.rows[0].sign_evidence,
            TaxSignEvidence.CALCULATION_RELATIONSHIP,
        )

    def test_rate_dollarization_has_no_rounding_or_float_conversion(self) -> None:
        bridge = rate_bridge((make_row("Adjustment", Decimal("-0.1")),), reported=Decimal("20.9"), pretax=Decimal("3"))
        row = bridge.rows[0]
        self.assertEqual(row.signed_tax_amount, Decimal("-0.003"))
        self.assertIs(type(row.signed_tax_amount), Decimal)
        self.assertEqual(row.precision, TaxRowPrecision.DOLLARIZED_FROM_DISPLAYED_RATE)

    def test_decimal_calculation_exceeds_default_context_without_rounding(self) -> None:
        rate = Decimal("0.123456789012345678901234567890123")
        pretax = Decimal("3")
        bridge = rate_bridge(
            (make_row("Precise", rate),),
            starting=Decimal("21"),
            reported=Decimal("21.123456789012345678901234567890123"),
            pretax=pretax,
            precision=Decimal("0.000000000000000000000000000000001"),
        )
        self.assertEqual(bridge.rows[0].signed_tax_amount, Decimal("0.00370370367037037036703703703670369"))
        self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.EXACT)

    def test_float_values_are_rejected(self) -> None:
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((make_row("Bad", 0.1),))  # type: ignore[arg-type]

    def test_dollar_bridge_preserves_apple_style_amount_without_rate_conversion(self) -> None:
        selected = make_filing(cik=320193, accession="0000320193-24-000123", report_date=date(2024, 9, 28))
        rows = (
            make_row("State", Decimal("1.162"), filing=selected, unit=TaxDisplayedUnit.CURRENCY),
            make_row("State Aid Decision", Decimal("10.246"), filing=selected, unit=TaxDisplayedUnit.CURRENCY, pairing=TaxPairing.NET_REPORTED_EVENT),
            make_row("Foreign earnings", Decimal("-5.311"), filing=selected, unit=TaxDisplayedUnit.CURRENCY),
            make_row("R&D credit", Decimal("-1.397"), filing=selected, unit=TaxDisplayedUnit.CURRENCY),
            make_row("Excess equity award benefits", Decimal("-0.893"), filing=selected, unit=TaxDisplayedUnit.CURRENCY),
            make_row("Other", Decimal("0.010"), filing=selected, unit=TaxDisplayedUnit.CURRENCY),
        )
        bridge = normalize_tax_reconciliation_bridge(
            selected,
            style=TaxBridgeStyle.DOLLAR,
            starting_value=Decimal("25.932"),
            reported_value=Decimal("29.749"),
            rows=rows,
            displayed_precision=Decimal("0.001"),
            row_inventory_complete=True,
            currency_code="USD billions",
        )
        self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.EXACT)
        self.assertEqual(bridge.reconstructed_value, Decimal("29.749"))
        self.assertIsNone(bridge.pretax_income)
        self.assertEqual(bridge.rows[1].signed_tax_amount, Decimal("10.246"))
        self.assertEqual(bridge.rows[1].pairing, TaxPairing.NET_REPORTED_EVENT)
        self.assertEqual(len(bridge.rows), 6)  # underlying event components are not separate bridge rows

    def test_meta_2025_signed_rate_bridge_preserves_distinct_evidence_rows(self) -> None:
        selected = make_filing()
        labels_values = (
            ("State and local", "-0.2", TaxProposedTreatment.METHODOLOGY_UNRESOLVED),
            ("Foreign effects", "1.7", TaxProposedTreatment.METHODOLOGY_UNRESOLVED),
            ("Research credits", "-4.6", TaxProposedTreatment.INCLUDE_OPERATING),
            ("U.S. foreign credits", "-1.6", TaxProposedTreatment.METHODOLOGY_UNRESOLVED),
            ("Valuation allowances", "13.9", TaxProposedTreatment.EXCLUDE_DISCRETE_TAX_ONLY),
            ("Unrecognized tax benefits", "3.6", TaxProposedTreatment.EXCLUDE_DISCRETE_TAX_ONLY),
            ("Excess SBC", "-5.0", TaxProposedTreatment.EXCLUDE_DISCRETE_TAX_ONLY),
            ("Other", "0.8", TaxProposedTreatment.METHODOLOGY_UNRESOLVED),
        )
        rows = tuple(
            make_row(
                label,
                Decimal(value),
                filing=selected,
                raw=abs(Decimal(value)),
                treatment=treatment,
                pairing=(TaxPairing.GROSS_TAX_WITH_CREDIT if label in ("Foreign effects", "U.S. foreign credits") else TaxPairing.NONE),
            )
            for label, value, treatment in labels_values
        )
        bridge = rate_bridge(
            rows,
            starting=Decimal("21.0"),
            reported=Decimal("29.6"),
            pretax=Decimal("85.932"),
            filing=selected,
        )
        self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.EXACT)
        self.assertEqual(bridge.statutory_rate, Decimal("21.0"))
        self.assertEqual(bridge.reported_effective_tax_rate, Decimal("29.6"))
        self.assertEqual(bridge.rows[4].signed_tax_amount, Decimal("11.944548"))
        self.assertEqual(bridge.rows[5].signed_tax_amount, Decimal("3.093552"))
        self.assertEqual(bridge.rows[6].signed_tax_amount, Decimal("-4.296600"))
        self.assertEqual(bridge.rows[1].pairing, TaxPairing.GROSS_TAX_WITH_CREDIT)
        self.assertEqual(bridge.rows[3].pairing, TaxPairing.GROSS_TAX_WITH_CREDIT)

    def test_msft_fy2026_keeps_gross_foreign_and_credit_rows_separate(self) -> None:
        selected = make_filing(cik=789019, accession="0001193125-26-323660", report_date=date(2026, 6, 30))
        amounts = (
            ("State and local", "2.573"),
            ("Ireland statutory rate difference", "-4.301"),
            ("Ireland other", ".809"),
            ("Other foreign jurisdictions", "3.248"),
            ("GILTI", "5.068"),
            ("FDII", "-.603"),
            ("Other cross-border", ".799"),
            ("Research and development credit", "-1.453"),
            ("Foreign tax credits", "-9.151"),
            ("Other tax credits", "-.014"),
            ("Changes in unrecognized tax benefits", "1.094"),
            ("Other reconciling items, net", "-.730"),
        )
        rows = tuple(
            make_row(label, Decimal(value), filing=selected, unit=TaxDisplayedUnit.CURRENCY)
            for label, value in amounts
        )
        bridge = normalize_tax_reconciliation_bridge(
            selected,
            style=TaxBridgeStyle.DOLLAR,
            starting_value=Decimal("34.846"),
            reported_value=Decimal("32.185"),
            rows=rows,
            displayed_precision=Decimal("0.001"),
            row_inventory_complete=True,
            currency_code="USD billions",
        )
        self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.EXACT)
        self.assertEqual(bridge.expected_statutory_tax_amount, Decimal("34.846"))
        self.assertEqual(bridge.reported_tax_provision, Decimal("32.185"))
        self.assertEqual(len(bridge.rows), 12)
        self.assertEqual(bridge.rows[4].displayed_label, "GILTI")
        self.assertEqual(bridge.rows[8].displayed_label, "Foreign tax credits")

    def test_rate_bridge_exact_rounded_and_unreconciled(self) -> None:
        exact = rate_bridge((make_row("Row", Decimal("-3.0")),), reported=Decimal("18.0"))
        rounded = rate_bridge((make_row("Row", Decimal("-3.0")),), reported=Decimal("18.1"), precision=Decimal("0.1"))
        bad = rate_bridge((make_row("Row", Decimal("-2.8")),), reported=Decimal("18.0"))
        self.assertEqual(exact.reconciliation_status, TaxReconciliationStatus.EXACT)
        self.assertEqual(rounded.reconciliation_status, TaxReconciliationStatus.MATCH_WITHIN_DISCLOSED_ROUNDING)
        self.assertEqual(bad.reconciliation_status, TaxReconciliationStatus.UNRECONCILED)
        self.assertEqual(rounded.difference, Decimal("-0.1"))

    def test_multiple_rounded_rate_rows_use_cumulative_error_bound(self) -> None:
        rows = tuple(make_row(label, Decimal("-1.0")) for label in ("A", "B", "C"))
        within_bound = rate_bridge(
            rows, starting=Decimal("21.0"), reported=Decimal("17.8"),
            precision=Decimal("0.1"),
        )
        outside_bound = rate_bridge(
            rows, starting=Decimal("21.0"), reported=Decimal("17.7"),
            precision=Decimal("0.1"),
        )
        self.assertEqual(within_bound.difference, Decimal("0.2"))
        self.assertEqual(
            within_bound.reconciliation_status,
            TaxReconciliationStatus.MATCH_WITHIN_DISCLOSED_ROUNDING,
        )
        self.assertEqual(outside_bound.difference, Decimal("0.3"))
        self.assertEqual(
            outside_bound.reconciliation_status,
            TaxReconciliationStatus.UNRECONCILED,
        )

    def test_dollar_rounded_bridge_uses_explicit_currency_precision(self) -> None:
        selected = make_filing()
        row = make_row("Rounding", Decimal("0.000"), filing=selected,
                       unit=TaxDisplayedUnit.CURRENCY)
        bridge = normalize_tax_reconciliation_bridge(
            selected, style=TaxBridgeStyle.DOLLAR,
            starting_value=Decimal("100.000"), reported_value=Decimal("100.001"),
            rows=(row,), displayed_precision=Decimal("0.001"),
            row_inventory_complete=True, currency_code="USD millions",
        )
        self.assertEqual(
            bridge.reconciliation_status,
            TaxReconciliationStatus.MATCH_WITHIN_DISCLOSED_ROUNDING,
        )

    def test_incomplete_row_evidence_prevents_bridge_validation(self) -> None:
        for status in (
            TaxEvidenceStatus.MISSING_EVIDENCE,
            TaxEvidenceStatus.AMBIGUOUS_SIGN,
            TaxEvidenceStatus.COMPETING_EVIDENCE,
            TaxEvidenceStatus.SOURCE_CONFLICT,
        ):
            with self.subTest(status=status):
                row = make_row("Unresolved", None, status=status, sign=None)
                bridge = rate_bridge((row,))
                self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.INCOMPLETE_EVIDENCE)
                self.assertIsNone(bridge.reconstructed_value)
                self.assertIsNone(bridge.rows[0].signed_tax_amount)

    def test_incomplete_row_inventory_cannot_validate_even_an_empty_bridge(self) -> None:
        bridge = normalize_tax_reconciliation_bridge(
            make_filing(),
            style=TaxBridgeStyle.RATE,
            starting_value=Decimal("21"),
            reported_value=Decimal("21"),
            rows=(),
            pretax_income=Decimal("100"),
            displayed_precision=Decimal("0.1"),
            row_inventory_complete=False,
        )
        self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.INCOMPLETE_EVIDENCE)
        self.assertIsNone(bridge.reconstructed_value)

    def test_methodology_unresolved_preserves_signed_row_and_arithmetic(self) -> None:
        row = make_row(
            "Other", Decimal("-3.0"),
            status=TaxEvidenceStatus.METHODOLOGY_UNRESOLVED,
            sign=TaxSignEvidence.FILING_TABLE_PRESENTATION,
        )
        bridge = rate_bridge((row,))
        self.assertEqual(bridge.reconciliation_status, TaxReconciliationStatus.EXACT)
        self.assertEqual(bridge.rows[0].evidence_status, TaxEvidenceStatus.METHODOLOGY_UNRESOLVED)
        self.assertEqual(bridge.rows[0].displayed_value, Decimal("-3.0"))

    def test_row_order_and_explicit_other_are_preserved_without_synthetic_residual(self) -> None:
        rows = (make_row("State", Decimal("1.0")), make_row("Other", Decimal("-4.0")))
        bridge = rate_bridge(rows, reported=Decimal("18.0"))
        self.assertEqual(tuple(row.displayed_label for row in bridge.rows), ("State", "Other"))
        self.assertEqual(len(bridge.rows), 2)
        self.assertFalse(any(row.displayed_label == "Synthetic Other" for row in bridge.rows))

    def test_filing_accession_issuer_and_report_date_ownership_are_enforced(self) -> None:
        selected = make_filing()
        wrong_accession = make_row("State", Decimal("1"))
        wrong_source = TaxRowSource(
            accession_number="0001326801-25-999999",
            source_url=selected.source_url,
            table_identity="Tax table",
        )
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((TaxReconciliationRowInput(
                "State", wrong_source, TaxDisplayedUnit.RATE, Decimal("1"),
                TaxSignEvidence.FILING_TABLE_PRESENTATION,
            ),), filing=selected)
        wrong_date_source = TaxRowSource(
            accession_number=selected.accession_number,
            source_url=selected.source_url,
            table_identity="Tax table",
            report_date=date(2024, 12, 31),
        )
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((TaxReconciliationRowInput(
                "State", wrong_date_source, TaxDisplayedUnit.RATE, Decimal("1"),
                TaxSignEvidence.FILING_TABLE_PRESENTATION,
            ),), filing=selected)
        other_issuer = make_filing(cik=320193, accession="0000320193-26-000001")
        with self.assertRaises(TaxEvidenceNormalizationError):
            normalize_tax_reconciliation_bridge(
                other_issuer,
                style=TaxBridgeStyle.RATE,
                starting_value=Decimal("21"),
                reported_value=Decimal("18"),
                rows=(wrong_accession,),
                pretax_income=Decimal("100"),
                displayed_precision=Decimal("0.1"),
                row_inventory_complete=True,
            )

    def test_non_10k_and_missing_report_date_are_rejected(self) -> None:
        base = make_filing()
        invalid_filings = (
            SECFiling("0001326801-26-000001", "10-Q", date(2026, 2, 1), date(2025, 12, 31), "meta.htm"),
            SECFiling("0001326801-26-000001", "10-K", date(2026, 2, 1), None, "meta.htm"),
        )
        for filing in invalid_filings:
            with self.subTest(filing=filing):
                with self.assertRaises(TaxEvidenceNormalizationError):
                    SelectedTaxFiling(base.company, filing, base.source_url)

    def test_unit_mismatch_and_nonfinite_decimals_are_rejected(self) -> None:
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((make_row("USD where rate required", Decimal("1"), unit=TaxDisplayedUnit.CURRENCY),))
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((make_row("NaN", Decimal("NaN")),))
        with self.assertRaises(TaxEvidenceNormalizationError):
            TaxRowSource("a", "url", "table", raw_xbrl_value=Decimal("Infinity"))

    def test_missing_explicit_sign_evidence_is_rejected(self) -> None:
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((make_row("No sign", Decimal("-1"), sign=None),))

    def test_rate_bridge_requires_nonzero_pretax_and_no_currency(self) -> None:
        with self.assertRaises(TaxEvidenceNormalizationError):
            rate_bridge((), pretax=Decimal("0"))
        with self.assertRaises(TaxEvidenceNormalizationError):
            normalize_tax_reconciliation_bridge(
                make_filing(), style=TaxBridgeStyle.RATE,
                starting_value=Decimal("21"), reported_value=Decimal("21"),
                rows=(), displayed_precision=Decimal("0.1"),
                pretax_income=Decimal("100"), currency_code="USD",
                row_inventory_complete=True,
            )

    def test_dollar_bridge_rejects_rate_rows_and_never_synthesizes_other(self) -> None:
        with self.assertRaises(TaxEvidenceNormalizationError):
            normalize_tax_reconciliation_bridge(
                make_filing(), style=TaxBridgeStyle.DOLLAR,
                starting_value=Decimal("10"), reported_value=Decimal("10"),
                rows=(make_row("Wrong unit", Decimal("0")),),
                displayed_precision=Decimal("1"), currency_code="USD millions",
                row_inventory_complete=True,
            )

    def test_bridge_models_are_immutable(self) -> None:
        bridge = rate_bridge(())
        with self.assertRaises(FrozenInstanceError):
            bridge.rows = ()  # type: ignore[misc]

    def test_direct_row_construction_enforces_source_and_arithmetic_integrity(self) -> None:
        rate = rate_bridge((make_row("Rate", Decimal("1.0")),)).rows[0]
        rate_copy = type(rate)(*(getattr(rate, field.name) for field in fields(rate)))
        self.assertEqual(rate_copy, rate)
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(rate, source=replace(rate.source, accession_number="other-accession"))
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(rate, source=replace(rate.source, report_date=date(2024, 12, 31)))
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(rate, signed_tax_amount=Decimal("999"))
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(
                rate,
                sign_evidence=TaxSignEvidence.CALCULATION_RELATIONSHIP,
                rationale="",
            )
        rate_bridge_result = rate_bridge((make_row("Rate", Decimal("1.0")),))
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(rate_bridge_result, pretax_income=Decimal("200"))

        selected = make_filing()
        dollar_input = make_row(
            "Dollar", Decimal("5"), filing=selected,
            unit=TaxDisplayedUnit.CURRENCY,
        )
        dollar_bridge = normalize_tax_reconciliation_bridge(
            selected, style=TaxBridgeStyle.DOLLAR,
            starting_value=Decimal("10"), reported_value=Decimal("15"),
            rows=(dollar_input,), displayed_precision=Decimal("1"),
            row_inventory_complete=True, currency_code="USD millions",
        )
        dollar = dollar_bridge.rows[0]
        dollar_copy = type(dollar)(*(getattr(dollar, field.name) for field in fields(dollar)))
        self.assertEqual(dollar_copy, dollar)
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(dollar_bridge, pretax_income=Decimal("100"))
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(dollar, signed_tax_amount=Decimal("6"))
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(dollar, pretax_denominator=Decimal("100"))

    def test_bridge_rejects_row_whose_source_was_altered_after_normalization(self) -> None:
        bridge = rate_bridge((make_row("Rate", Decimal("1.0")),), reported=Decimal("22"))
        malformed_row = object.__new__(type(bridge.rows[0]))
        for field in fields(bridge.rows[0]):
            object.__setattr__(malformed_row, field.name, getattr(bridge.rows[0], field.name))
        object.__setattr__(
            malformed_row,
            "source",
            replace(bridge.rows[0].source, accession_number="different-accession"),
        )
        with self.assertRaises(TaxEvidenceNormalizationError):
            replace(bridge, rows=(malformed_row,))


if __name__ == "__main__":
    unittest.main()
