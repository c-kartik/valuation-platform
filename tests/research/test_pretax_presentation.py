from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from valuation_platform.research.pretax_presentation import (
    EvidenceOutcome,
    PresentationEvidenceError,
    TARGET_CONCEPT,
    analyze_period,
    discover_artifacts,
    parse_presentation_memberships,
    parse_renderer_evidence,
    parse_role_definitions,
    serialize_inventory,
)
from valuation_platform.sec import (
    FilingXBRLContext, FilingXBRLFact, FilingXBRLUnit, FilingXBRLQName,
    ResolvedAnnualPeriod, SECCompanyIdentity, SECFiling, SECFilingXBRL,
    resolve_annual_period,
)
from scripts.run_pretax_presentation_diagnostic import CANDIDATE_ACCESSIONS, run_diagnostic


FIXTURES = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
SOURCE = "https://www.sec.gov/Archives/edgar/data/1/000000000126000001/test_htm.xml"


def fixture(name):
    return (FIXTURES / name).read_bytes()


def directory(*names):
    return {"directory": {"item": [{"name": name} for name in names]}}


def make_xbrl():
    company = SECCompanyIdentity("TEST", 1, "0000000001", "Test", "tickers", NOW)
    filing = SECFiling("0000000001-26-000001", "10-K", date(2026, 2, 1), date(2025, 12, 31), "test.htm")
    context = FilingXBRLContext("annual", "http://www.sec.gov/CIK", "0000000001", date(2025, 1, 1), date(2025, 12, 31), ())
    usd = FilingXBRLUnit("usd", (FilingXBRLQName("http://www.xbrl.org/2003/iso4217", "USD"),), ())
    def fact(concept, raw, namespace="http://xbrl.sec.gov/dei/2025", numeric=None):
        return FilingXBRLFact(namespace, concept, "annual", context.start, context.end, (), "usd" if numeric is not None else None, usd if numeric is not None else None, raw, numeric, "-6" if numeric is not None else None, False, filing.accession_number, SOURCE)
    facts = (
        fact("DocumentFiscalPeriodFocus", "FY"),
        fact("DocumentFiscalYearFocus", "2025"),
        fact("DocumentPeriodEndDate", "2025-12-31"),
        fact(TARGET_CONCEPT, "1000000000", "http://fasb.org/us-gaap/2025", Decimal("1000000000")),
    )
    return SECFilingXBRL(company, filing, (context,), (usd,), facts, SOURCE, NOW)


def inventory():
    return discover_artifacts(directory("test.htm", "test_htm.xml", "test.xsd", "test_pre.xml", "FilingSummary.xml", "MetaLinks.json", "R1.xml"), directory_url="https://www.sec.gov/Archives/edgar/data/1/000000000126000001", primary_document="test.htm")


class ArtifactDiscoveryTests(TestCase):
    def test_discovers_only_exact_directory_artifacts(self):
        result = inventory()
        self.assertEqual(result.instance_name, "test_htm.xml")
        self.assertEqual(result.schema_names, ("test.xsd",))
        self.assertEqual(result.presentation_names, ("test_pre.xml",))
        self.assertEqual(result.renderer_names, ("R1.xml",))
        self.assertIn("test.xsd", result.all_names)
        self.assertIn("https://www.sec.gov/Archives/edgar/data/1/000000000126000001/test.xsd", result.all_source_urls)

    def test_missing_ambiguous_and_unsafe_artifacts_are_explicit(self):
        cases = (
            directory("test_htm.xml", "test_pre.xml"),
            directory("test_htm.xml", "test.xsd"),
            directory("test_htm.xml", "test_htm.xml", "test.xsd", "test_pre.xml"),
            directory("../test_htm.xml", "test.xsd", "test_pre.xml"),
        )
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(PresentationEvidenceError):
                discover_artifacts(payload, directory_url="https://www.sec.gov/Archives/edgar/data/1/a", primary_document="test.htm")


class PresentationParserTests(TestCase):
    def test_complete_role_definition_and_ordered_path_are_preserved(self):
        roles = parse_role_definitions({"schema": fixture("presentation_schema.xsd")})
        memberships = parse_presentation_memberships({"pre": fixture("presentation_pre.xml")}, roles)
        role = memberships[0].role
        self.assertEqual((role.sort_code, role.role_type, role.title), ("100100", "Statement", "Consolidated Statements of Operations"))
        path = memberships[0].paths[0]
        self.assertEqual(path.relationships[0].order, Decimal("12.5"))
        self.assertEqual(path.relationships[0].preferred_label, "http://www.xbrl.org/2003/role/totalLabel")

    def test_title_keywords_do_not_override_disclosure_type(self):
        schema = fixture("presentation_schema.xsd").replace(b"100100 - Statement - Consolidated Statements of Operations", b"100100 - Disclosure - Consolidated Statements of Operations")
        roles = parse_role_definitions({"schema": schema})
        xbrl = make_xbrl(); annual = resolve_annual_period(xbrl)
        result = analyze_period(ticker="TEST", filing_xbrl=xbrl, annual_period=annual, inventory=inventory(), schema_documents={"schema": schema}, presentation_documents={"pre": fixture("presentation_pre.xml")}, renderer=parse_renderer_evidence(filing_summary=None, metalinks=None, renderer_files={}))
        self.assertIn(EvidenceOutcome.DISCLOSURE_ONLY_MEMBER, result.outcomes)

    def test_multiple_roles_are_preserved_and_classified(self):
        # Build a clean second link without relying on document ordering.
        first = fixture("presentation_pre.xml").decode().replace("</link:linkbase>", "")
        link = first[first.index("  <link:presentationLink"):].replace("http://example.com/role/income", "http://example.com/role/note")
        pre = (first + link + "</link:linkbase>").encode()
        roles = parse_role_definitions({"schema": fixture("presentation_schema.xsd")})
        memberships = parse_presentation_memberships({"pre": pre}, roles)
        self.assertEqual(len(memberships), 2)
        xbrl = make_xbrl(); annual = resolve_annual_period(xbrl)
        result = analyze_period(ticker="TEST", filing_xbrl=xbrl, annual_period=annual, inventory=inventory(), schema_documents={"schema": fixture("presentation_schema.xsd")}, presentation_documents={"pre": pre}, renderer=parse_renderer_evidence(filing_summary=None, metalinks=None, renderer_files={}))
        self.assertIn(EvidenceOutcome.MULTIPLE_ROLE_MEMBERSHIP, result.outcomes)

    def test_malformed_role_and_graph_are_data_errors(self):
        malformed = fixture("presentation_schema.xsd").replace(b"100100 - Statement - ", b"Statement ")
        with self.assertRaises(PresentationEvidenceError):
            parse_role_definitions({"schema": malformed})
        roles = parse_role_definitions({"schema": fixture("presentation_schema.xsd")})
        with self.assertRaises(PresentationEvidenceError):
            parse_presentation_memberships({"pre": b"<bad"}, roles)


class ReconciliationAndSerializationTests(TestCase):
    def test_exact_fact_context_and_renderer_separation(self):
        xbrl = make_xbrl(); annual = resolve_annual_period(xbrl)
        renderer = parse_renderer_evidence(filing_summary=("summary", fixture("FilingSummary.xml")), metalinks=("meta", fixture("MetaLinks.json")), renderer_files={"R1": fixture("R1.xml")})
        result = analyze_period(ticker="TEST", filing_xbrl=xbrl, annual_period=annual, inventory=inventory(), schema_documents={"schema": fixture("presentation_schema.xsd")}, presentation_documents={"pre": fixture("presentation_pre.xml")}, renderer=renderer)
        self.assertEqual(result.candidate_facts[0].context_id, "annual")
        self.assertEqual(result.candidate_facts[0].unit_ref, "usd")
        self.assertEqual(result.candidate_facts[0].unit_numerator_measures, ("http://www.xbrl.org/2003/iso4217:USD",))
        self.assertIn(EvidenceOutcome.PRIMARY_STATEMENT_MEMBER, result.outcomes)
        self.assertIn(EvidenceOutcome.EQUITY_METHOD_SCOPE_UNRESOLVED, result.outcomes)
        self.assertTrue(result.renderer.metalinks_contains_candidate)
        self.assertEqual(result.renderer.submitted_role_uris, ("http://example.com/role/income",))
        self.assertEqual(result.renderer.renderer_matching_role_uris, ("http://example.com/role/income",))
        self.assertEqual(result.renderer.renderer_missing_role_uris, ())
        self.assertNotEqual(result.memberships[0].role.source_url, result.renderer.source_urls[0])

        conflicting = replace(annual, filing=replace(annual.filing, accession_number="0000000001-26-999999"))
        error = analyze_period(ticker="TEST", filing_xbrl=xbrl, annual_period=conflicting, inventory=inventory(), schema_documents={"schema": fixture("presentation_schema.xsd")}, presentation_documents={"pre": fixture("presentation_pre.xml")}, renderer=renderer)
        self.assertIn(EvidenceOutcome.PRESENTATION_DATA_ERROR, error.outcomes)

    def test_serialization_is_deterministic_and_scope_is_never_inferred(self):
        xbrl = make_xbrl(); annual = resolve_annual_period(xbrl)
        result = analyze_period(ticker="TEST", filing_xbrl=xbrl, annual_period=annual, inventory=inventory(), schema_documents={"schema": fixture("presentation_schema.xsd")}, presentation_documents={"pre": fixture("presentation_pre.xml")}, renderer=parse_renderer_evidence(filing_summary=None, metalinks=None, renderer_files={}))
        earlier = replace(
            result,
            ticker="AAA",
            accession_number="0000000001-25-000001",
            report_date=date(2024, 12, 31),
        )
        forward = serialize_inventory((result, earlier))
        reverse = serialize_inventory((earlier, result))
        self.assertEqual(forward, reverse)
        self.assertLess(forward.index('"ticker": "AAA"'), forward.index('"ticker": "TEST"'))
        self.assertIn('"equity_method_scope": "UNRESOLVED"', forward)

    def test_malformed_renderer_artifacts_become_typed_data_error(self):
        xbrl = make_xbrl(); annual = resolve_annual_period(xbrl)
        renderer = parse_renderer_evidence(
            filing_summary=("summary", b"<bad"),
            metalinks=("meta", b"{"),
            renderer_files={"R1": b"\xff"},
        )
        result = analyze_period(
            ticker="TEST",
            filing_xbrl=xbrl,
            annual_period=annual,
            inventory=inventory(),
            schema_documents={"schema": fixture("presentation_schema.xsd")},
            presentation_documents={"pre": fixture("presentation_pre.xml")},
            renderer=renderer,
        )
        self.assertIn(EvidenceOutcome.PRESENTATION_DATA_ERROR, result.outcomes)
        self.assertIsNotNone(result.error)

    def test_frozen_request_set_is_exactly_33_and_excludes_extensions(self):
        self.assertEqual(sum(map(len, CANDIDATE_ACCESSIONS.values())), 33)
        self.assertEqual(set(CANDIDATE_ACCESSIONS), {"AMZN", "MU", "MA", "CVX", "CAT", "PM", "LIN"})
        self.assertTrue({"ORCL", "MCD", "PG"}.isdisjoint(CANDIDATE_ACCESSIONS))

    @patch("scripts.run_pretax_presentation_diagnostic.resolve_ticker", side_effect=RuntimeError("offline"))
    def test_orchestrator_emits_one_typed_failure_for_every_requested_period(self, _resolve):
        results = run_diagnostic(Mock())
        self.assertEqual(len(results), 33)
        self.assertEqual({result.accession_number for result in results}, {accession for accessions in CANDIDATE_ACCESSIONS.values() for accession in accessions})
        self.assertTrue(all(EvidenceOutcome.PRESENTATION_DATA_ERROR in result.outcomes for result in results))
