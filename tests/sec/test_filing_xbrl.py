from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

from valuation_platform.sec.client import SECClient, SECRequestError
from valuation_platform.sec.filing_xbrl import (
    FilingXBRLDataError,
    FilingXBRLSourceError,
    discover_extracted_xbrl,
    fetch_filing_xbrl,
    parse_filing_xbrl_instance,
)
from valuation_platform.sec.submissions import SECFiling
from valuation_platform.sec.tickers import SECCompanyIdentity


FIXTURE = Path(__file__).parent / "fixtures" / "filing_xbrl_instance.xml"
RETRIEVED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_company() -> SECCompanyIdentity:
    return SECCompanyIdentity(
        ticker="TEST",
        cik=1,
        cik_padded="0000000001",
        company_name="Test Company",
        source_url="ticker-source",
        retrieved_at=RETRIEVED_AT,
    )


def make_filing(
    *,
    accession: str = "0000000001-26-000001",
    primary_document: str = "test-20251231.htm",
) -> SECFiling:
    return SECFiling(
        accession_number=accession,
        form="10-K",
        filing_date=date(2026, 2, 1),
        report_date=date(2025, 12, 31),
        primary_document=primary_document,
    )


def directory_payload(*names: str) -> dict[str, object]:
    return {"directory": {"item": [{"name": name} for name in names]}}


class FilingXBRLDiscoveryTests(TestCase):
    def setUp(self) -> None:
        self.client = Mock(spec=SECClient)
        self.company = make_company()
        self.filing = make_filing()

    def test_successful_discovery_uses_official_directory_metadata(self) -> None:
        self.client.get_json.return_value = directory_payload(
            "test-20251231.htm",
            "test-20251231_htm.xml",
        )

        artifact = discover_extracted_xbrl(
            self.client, self.company, self.filing
        )

        directory = (
            "https://www.sec.gov/Archives/edgar/data/1/000000000126000001"
        )
        self.client.get_json.assert_called_once_with(f"{directory}/index.json")
        self.assertEqual(artifact.name, "test-20251231_htm.xml")
        self.assertEqual(artifact.source_url, f"{directory}/{artifact.name}")
        self.assertEqual(artifact.directory_url, directory)

    def test_missing_extracted_instance_fails_explicitly(self) -> None:
        self.client.get_json.return_value = directory_payload("test-20251231.htm")

        with self.assertRaisesRegex(FilingXBRLSourceError, "no extracted"):
            discover_extracted_xbrl(self.client, self.company, self.filing)

    def test_nonmatching_instance_is_not_guessed(self) -> None:
        self.client.get_json.return_value = directory_payload(
            "other-document_htm.xml"
        )

        with self.assertRaisesRegex(FilingXBRLSourceError, "no extracted.*corresponding"):
            discover_extracted_xbrl(self.client, self.company, self.filing)

    def test_duplicate_matching_artifacts_are_ambiguous(self) -> None:
        self.client.get_json.return_value = directory_payload(
            "test-20251231_htm.xml",
            "test-20251231_htm.xml",
        )

        with self.assertRaisesRegex(FilingXBRLSourceError, "ambiguous"):
            discover_extracted_xbrl(self.client, self.company, self.filing)

    def test_malformed_directory_metadata_fails_explicitly(self) -> None:
        malformed = (
            None,
            {},
            {"directory": []},
            {"directory": {}},
            {"directory": {"item": [None]}},
            {"directory": {"item": [{}]}},
        )
        for payload in malformed:
            with self.subTest(payload=payload):
                self.client.get_json.return_value = payload
                with self.assertRaises(FilingXBRLSourceError):
                    discover_extracted_xbrl(self.client, self.company, self.filing)

    def test_unsafe_accession_primary_document_and_artifacts_are_rejected(self) -> None:
        cases = (
            make_filing(accession="000000000126000001"),
            make_filing(primary_document="../test.htm"),
            make_filing(primary_document="https://example.com/test.htm"),
            make_filing(primary_document="test.htm?x=1"),
            make_filing(primary_document="test.htm#fragment"),
            make_filing(primary_document="path\\test.htm"),
        )
        for filing in cases:
            with self.subTest(filing=filing):
                self.client.get_json.return_value = directory_payload(
                    "test_htm.xml"
                )
                with self.assertRaises(FilingXBRLSourceError):
                    discover_extracted_xbrl(self.client, self.company, filing)

        unsafe_artifacts = (
            "../test_htm.xml",
            "path/test_htm.xml",
            "path\\test_htm.xml",
            "https://example.com/test_htm.xml",
            "test_htm.xml?x=1",
            "test_htm.xml#fragment",
        )
        for artifact in unsafe_artifacts:
            with self.subTest(artifact=artifact):
                self.client.get_json.return_value = directory_payload(artifact)
                with self.assertRaises(FilingXBRLSourceError):
                    discover_extracted_xbrl(self.client, self.company, self.filing)

    def test_fetch_uses_client_and_parses_discovered_instance(self) -> None:
        self.client.get_json.return_value = directory_payload(
            "test-20251231_htm.xml"
        )
        self.client.get_bytes.return_value = FIXTURE.read_bytes()

        result = fetch_filing_xbrl(self.client, self.company, self.filing)

        self.client.get_bytes.assert_called_once_with(result.source_url)
        self.assertIs(result.company, self.company)
        self.assertIs(result.filing, self.filing)
        self.assertEqual(len(result.facts), 9)

    def test_transport_failure_propagates(self) -> None:
        self.client.get_json.side_effect = SECRequestError("failed")

        with self.assertRaisesRegex(SECRequestError, "failed"):
            discover_extracted_xbrl(self.client, self.company, self.filing)

        self.client.get_json.side_effect = None
        self.client.get_json.return_value = directory_payload(
            "test-20251231_htm.xml"
        )
        self.client.get_bytes.side_effect = SECRequestError("bytes failed")
        with self.assertRaisesRegex(SECRequestError, "bytes failed"):
            fetch_filing_xbrl(self.client, self.company, self.filing)


class FilingXBRLParserTests(TestCase):
    def parse(self, content: bytes | None = None):
        return parse_filing_xbrl_instance(
            FIXTURE.read_bytes() if content is None else content,
            company=make_company(),
            filing=make_filing(),
            source_url="https://www.sec.gov/instance.xml",
            retrieved_at=RETRIEVED_AT,
        )

    def test_parses_standard_and_extension_duration_facts(self) -> None:
        result = self.parse()
        revenue = next(
            fact
            for fact in result.facts
            if fact.concept == "Revenues" and fact.context_id == "current"
        )
        extension = next(
            fact
            for fact in result.facts
            if fact.concept == "DepreciationAmortizationAndOther"
        )

        self.assertEqual(revenue.namespace, "http://fasb.org/us-gaap/2025")
        self.assertEqual(revenue.numeric_value, Decimal("1000000000"))
        self.assertEqual(revenue.raw_value, "1000000000")
        self.assertEqual(revenue.decimals, "-6")
        self.assertEqual(revenue.start, date(2025, 1, 1))
        self.assertEqual(revenue.end, date(2025, 12, 31))
        self.assertEqual(extension.namespace, "http://example.com/2025")
        self.assertEqual(extension.accession_number, "0000000001-26-000001")
        self.assertEqual(extension.source_url, result.source_url)

    def test_root_link_structural_element_is_not_parsed_as_a_fact(self) -> None:
        fixture = FIXTURE.read_text()
        fixture = fixture.replace(
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            '    xmlns:link="http://www.xbrl.org/2003/linkbase"\n'
            '    xmlns:xlink="http://www.w3.org/1999/xlink"',
        ).replace(
            "  <xbrli:context",
            '  <link:schemaRef xlink:type="simple" xlink:href="test-20251231.xsd"/>\n'
            "  <xbrli:context",
            1,
        )

        result = self.parse(fixture.encode())

        self.assertFalse(any(fact.concept == "schemaRef" for fact in result.facts))
        self.assertTrue(any(fact.concept == "Revenues" for fact in result.facts))

    def test_preserves_instant_comparative_and_duplicate_concept_contexts(self) -> None:
        result = self.parse()
        instant = next(
            fact
            for fact in result.facts
            if fact.concept == "CashAndCashEquivalentsAtCarryingValue"
        )
        revenues = tuple(fact for fact in result.facts if fact.concept == "Revenues")

        self.assertIsNone(instant.start)
        self.assertEqual(instant.end, date(2025, 12, 31))
        self.assertEqual(instant.decimals, "INF")
        self.assertEqual(len(revenues), 3)
        self.assertEqual(
            tuple(fact.context_id for fact in revenues),
            ("current", "comparative", "explicit"),
        )
        self.assertEqual(revenues[1].start, date(2024, 1, 1))

    def test_parses_explicit_and_typed_dimensions(self) -> None:
        result = self.parse()
        explicit = next(c for c in result.contexts if c.context_id == "explicit")
        typed = next(c for c in result.contexts if c.context_id == "typed")

        explicit_dimension = explicit.dimensions[0]
        self.assertEqual(
            explicit_dimension.dimension.local_name,
            "StatementBusinessSegmentsAxis",
        )
        self.assertEqual(explicit_dimension.explicit_member.local_name, "CloudMember")
        self.assertIsNone(explicit_dimension.typed_member_xml)
        typed_dimension = typed.dimensions[0]
        self.assertEqual(typed_dimension.dimension.local_name, "CustomerAxis")
        self.assertIsNone(typed_dimension.explicit_member)
        self.assertIn("Customer A", typed_dimension.typed_member_xml)

    def test_parses_simple_and_divided_units(self) -> None:
        result = self.parse()
        usd = next(unit for unit in result.units if unit.unit_id == "usd")
        divided = next(
            unit for unit in result.units if unit.unit_id == "usdPerShare"
        )

        self.assertEqual(usd.numerator_measures[0].local_name, "USD")
        self.assertFalse(usd.is_divided)
        self.assertTrue(divided.is_divided)
        self.assertEqual(divided.numerator_measures[0].local_name, "USD")
        self.assertEqual(divided.denominator_measures[0].local_name, "shares")

    def test_preserves_nil_and_nonnumeric_facts(self) -> None:
        result = self.parse()
        nil_fact = next(
            fact for fact in result.facts if fact.concept == "OperatingIncomeLoss"
        )
        name = next(
            fact for fact in result.facts if fact.concept == "EntityRegistrantName"
        )

        self.assertTrue(nil_fact.is_nil)
        self.assertIsNone(nil_fact.raw_value)
        self.assertIsNone(nil_fact.numeric_value)
        self.assertFalse(name.is_nil)
        self.assertEqual(name.raw_value, "Example Company")
        self.assertIsNone(name.numeric_value)

    def test_missing_context_and_unit_references_fail_explicitly(self) -> None:
        fixture = FIXTURE.read_text()
        cases = (
            fixture.replace('contextRef="current"', 'contextRef="missing"', 1),
            fixture.replace(' contextRef="current"', "", 1),
            fixture.replace('unitRef="usd"', 'unitRef="missing"', 1),
        )
        for xml in cases:
            with self.subTest():
                with self.assertRaises(FilingXBRLDataError):
                    self.parse(xml.encode())

    def test_malformed_dates_fail_explicitly(self) -> None:
        malformed = FIXTURE.read_text().replace("2025-01-01", "not-a-date", 1)

        with self.assertRaisesRegex(FilingXBRLDataError, "invalid date"):
            self.parse(malformed.encode())

    def test_malformed_xml_and_dtd_are_rejected(self) -> None:
        for content in (b"<not-xbrl/>", b"<!DOCTYPE x [<!ENTITY a 'x'>]><x/>"):
            with self.subTest(content=content):
                with self.assertRaises(FilingXBRLDataError):
                    self.parse(content)
