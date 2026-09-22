from datetime import date, datetime, timezone
from unittest import TestCase
from unittest.mock import Mock

from valuation_platform.sec.client import SECClient
from valuation_platform.sec.company_facts import (
    COMPANY_FACTS_URL_TEMPLATE,
    CompanyFactsDataError,
    SECCompanyFacts,
    SECFactConcept,
    SECFactObservation,
    fetch_company_facts,
)
from valuation_platform.sec.tickers import SECCompanyIdentity


DURATION_OBSERVATION = {
    "start": "2023-01-01",
    "end": "2023-12-31",
    "val": 134_902_000_000,
    "accn": "0001326801-24-000012",
    "fy": 2023,
    "fp": "FY",
    "form": "10-K",
    "filed": "2024-02-02",
    "frame": "CY2023",
}

COMPARATIVE_OBSERVATION = {
    "start": "2023-01-01",
    "end": "2023-12-31",
    "val": 134_902_000_000,
    "accn": "0001326801-25-000017",
    "fy": 2024,
    "fp": "FY",
    "form": "10-K",
    "filed": "2025-01-30",
}

INSTANT_OBSERVATION = {
    "end": "2024-12-31",
    "val": "Meta Platforms, Inc.",
    "accn": "0001326801-25-000017",
    "form": "10-K",
    "filed": "2025-01-30",
}

COMPANY_FACTS_RESPONSE = {
    "cik": 1326801,
    "entityName": "Meta Platforms, Inc.",
    "facts": {
        "us-gaap": {
            "Revenue": {
                "label": "Revenue",
                "description": "Revenue description",
                "units": {
                    "pure": [
                        {
                            **DURATION_OBSERVATION,
                            "val": 12.5,
                            "accn": "float-observation",
                        }
                    ],
                    "USD": [DURATION_OBSERVATION, COMPARATIVE_OBSERVATION],
                },
            },
            "OperatingIncomeLoss": {
                "label": "Operating Income (Loss)",
                "description": "Operating income description",
                "units": {"USD": []},
            },
        },
        "dei": {
            "EntityRegistrantName": {
                "label": "Entity Registrant Name",
                "description": "Registrant name",
                "units": {"pure": [INSTANT_OBSERVATION]},
            }
        },
    },
}


class FetchCompanyFactsTests(TestCase):
    def setUp(self) -> None:
        self.company = SECCompanyIdentity(
            ticker="META",
            cik=1326801,
            cik_padded="0001326801",
            company_name="Meta Platforms, Inc.",
            source_url="https://www.sec.gov/files/company_tickers.json",
            retrieved_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        self.client = Mock(spec=SECClient)
        self.client.get_json.return_value = COMPANY_FACTS_RESPONSE

    def test_fetches_padded_cik_url_once_through_existing_client(self) -> None:
        result = fetch_company_facts(self.client, self.company)

        expected_url = COMPANY_FACTS_URL_TEMPLATE.format(
            cik_padded="0001326801"
        )
        self.client.get_json.assert_called_once_with(expected_url)
        self.assertEqual(result.source_url, expected_url)

    def test_parses_company_metadata_and_multiple_namespaces(self) -> None:
        result = fetch_company_facts(self.client, self.company)

        self.assertIsInstance(result, SECCompanyFacts)
        self.assertIs(result.company, self.company)
        self.assertEqual(result.entity_name, "Meta Platforms, Inc.")
        self.assertEqual(
            [(concept.taxonomy, concept.name) for concept in result.concepts],
            [
                ("dei", "EntityRegistrantName"),
                ("us-gaap", "OperatingIncomeLoss"),
                ("us-gaap", "Revenue"),
            ],
        )
        self.assertIs(result.retrieved_at.tzinfo, timezone.utc)

    def test_parses_concept_metadata_and_multiple_unit_buckets(self) -> None:
        result = fetch_company_facts(self.client, self.company)
        revenue = result.concepts[2]

        self.assertIsInstance(revenue, SECFactConcept)
        self.assertEqual(revenue.taxonomy, "us-gaap")
        self.assertEqual(revenue.name, "Revenue")
        self.assertEqual(revenue.label, "Revenue")
        self.assertEqual(revenue.description, "Revenue description")
        self.assertEqual(
            [observation.unit for observation in revenue.observations],
            ["USD", "USD", "pure"],
        )

    def test_optional_concept_label_and_description(self) -> None:
        cases = [
            (
                "missing label",
                {"description": "Description", "units": {}},
                None,
                "Description",
            ),
            (
                "null label",
                {"label": None, "description": "Description", "units": {}},
                None,
                "Description",
            ),
            (
                "missing description",
                {"label": "Label", "units": {}},
                "Label",
                None,
            ),
            (
                "null description",
                {"label": "Label", "description": None, "units": {}},
                "Label",
                None,
            ),
            (
                "string metadata",
                {
                    "label": "Exact label",
                    "description": "Exact description",
                    "units": {},
                },
                "Exact label",
                "Exact description",
            ),
        ]

        for case_name, concept_data, expected_label, expected_description in cases:
            with self.subTest(case=case_name):
                self.client.get_json.return_value = {
                    "cik": 1326801,
                    "entityName": "Meta",
                    "facts": {
                        "srt": {
                            "StockRepurchaseProgramAuthorizedAmount1": concept_data
                        }
                    },
                }

                concept = fetch_company_facts(
                    self.client, self.company
                ).concepts[0]

                self.assertEqual(concept.label, expected_label)
                self.assertEqual(concept.description, expected_description)

    def test_invalid_concept_label_or_description_type_fails_explicitly(self) -> None:
        malformed_concepts = [
            {"label": 123, "description": "Description", "units": {}},
            {"label": "Label", "description": ["Description"], "units": {}},
        ]

        for concept_data in malformed_concepts:
            with self.subTest(concept_data=concept_data):
                self.client.get_json.return_value = {
                    "cik": 1326801,
                    "entityName": "Meta",
                    "facts": {"srt": {"Concept": concept_data}},
                }

                with self.assertRaises(CompanyFactsDataError):
                    fetch_company_facts(self.client, self.company)

    def test_preserves_observation_order_and_repeated_periods(self) -> None:
        result = fetch_company_facts(self.client, self.company)
        revenue = result.concepts[2]

        self.assertEqual(len(revenue.observations), 3)
        self.assertEqual(
            [observation.accession_number for observation in revenue.observations[:2]],
            ["0001326801-24-000012", "0001326801-25-000017"],
        )
        self.assertEqual(
            [observation.end for observation in revenue.observations[:2]],
            [date(2023, 12, 31), date(2023, 12, 31)],
        )

    def test_parses_duration_observation_and_provenance(self) -> None:
        result = fetch_company_facts(self.client, self.company)
        observation = result.concepts[2].observations[0]

        self.assertIsInstance(observation, SECFactObservation)
        self.assertEqual(observation.unit, "USD")
        self.assertEqual(observation.value, 134_902_000_000)
        self.assertIs(type(observation.value), int)
        self.assertEqual(observation.start, date(2023, 1, 1))
        self.assertEqual(observation.end, date(2023, 12, 31))
        self.assertEqual(observation.accession_number, "0001326801-24-000012")
        self.assertEqual(observation.fiscal_year, 2023)
        self.assertEqual(observation.fiscal_period, "FY")
        self.assertEqual(observation.form, "10-K")
        self.assertEqual(observation.filed, date(2024, 2, 2))
        self.assertEqual(observation.frame, "CY2023")

    def test_preserves_non_integer_numeric_value(self) -> None:
        observation = fetch_company_facts(
            self.client, self.company
        ).concepts[2].observations[2]

        self.assertEqual(observation.value, 12.5)
        self.assertIs(type(observation.value), float)

    def test_supports_instant_and_optional_observation_fields(self) -> None:
        result = fetch_company_facts(self.client, self.company)
        observation = result.concepts[0].observations[0]

        self.assertIsNone(observation.start)
        self.assertIsNone(observation.fiscal_year)
        self.assertIsNone(observation.fiscal_period)
        self.assertIsNone(observation.frame)
        self.assertEqual(observation.value, "Meta Platforms, Inc.")

    def test_empty_facts_returns_empty_concepts(self) -> None:
        self.client.get_json.return_value = {
            "cik": 1326801,
            "entityName": "Meta Platforms, Inc.",
            "facts": {},
        }

        result = fetch_company_facts(self.client, self.company)

        self.assertEqual(result.concepts, ())

    def test_mismatched_returned_cik_fails_explicitly(self) -> None:
        self.client.get_json.return_value = {
            **COMPANY_FACTS_RESPONSE,
            "cik": 999999,
        }

        with self.assertRaisesRegex(CompanyFactsDataError, "does not match"):
            fetch_company_facts(self.client, self.company)

    def test_malformed_top_level_structure_fails_explicitly(self) -> None:
        malformed_payloads = [
            [],
            {"entityName": "Meta", "facts": {}},
            {"cik": 1326801, "facts": {}},
            {"cik": 1326801, "entityName": "Meta", "facts": []},
        ]

        for payload in malformed_payloads:
            with self.subTest(payload=payload):
                self.client.get_json.return_value = payload
                with self.assertRaises(CompanyFactsDataError):
                    fetch_company_facts(self.client, self.company)

    def test_malformed_concept_structure_fails_explicitly(self) -> None:
        malformed_concepts = [
            [],
            {"Revenue": []},
        ]

        for concepts in malformed_concepts:
            with self.subTest(concepts=concepts):
                self.client.get_json.return_value = {
                    "cik": 1326801,
                    "entityName": "Meta",
                    "facts": {"us-gaap": concepts},
                }
                with self.assertRaises(CompanyFactsDataError):
                    fetch_company_facts(self.client, self.company)

    def test_malformed_units_structure_fails_explicitly(self) -> None:
        malformed_units = [[], {"USD": {}}, {1: []}]

        for units in malformed_units:
            with self.subTest(units=units):
                self.client.get_json.return_value = {
                    "cik": 1326801,
                    "entityName": "Meta",
                    "facts": {
                        "us-gaap": {
                            "Revenue": {
                                "label": "Revenue",
                                "description": "description",
                                "units": units,
                            }
                        }
                    },
                }
                with self.assertRaises(CompanyFactsDataError):
                    fetch_company_facts(self.client, self.company)

    def test_malformed_observation_fails_explicitly(self) -> None:
        malformed_observations = [
            "not an object",
            {key: value for key, value in DURATION_OBSERVATION.items() if key != "val"},
            {**DURATION_OBSERVATION, "val": {}},
            {**DURATION_OBSERVATION, "end": "2023-13-01"},
            {**DURATION_OBSERVATION, "filed": "20240202"},
            {**DURATION_OBSERVATION, "fy": True},
            {**DURATION_OBSERVATION, "fp": 2023},
            {**DURATION_OBSERVATION, "frame": 2023},
        ]

        for observation in malformed_observations:
            with self.subTest(observation=observation):
                self.client.get_json.return_value = {
                    "cik": 1326801,
                    "entityName": "Meta",
                    "facts": {
                        "us-gaap": {
                            "Revenue": {
                                "label": "Revenue",
                                "description": "description",
                                "units": {"USD": [observation]},
                            }
                        }
                    },
                }
                with self.assertRaises(CompanyFactsDataError):
                    fetch_company_facts(self.client, self.company)
