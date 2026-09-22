from datetime import date, datetime, timezone
from unittest import TestCase
from unittest.mock import Mock

from valuation_platform.sec.client import SECClient
from valuation_platform.sec.submissions import (
    SUBMISSION_HISTORY_URL_TEMPLATE,
    SUBMISSIONS_URL_TEMPLATE,
    SECFiling,
    SECSubmissionHistoryFile,
    SECSubmissions,
    SubmissionsDataError,
    fetch_submission_history,
    fetch_submissions,
)
from valuation_platform.sec.tickers import SECCompanyIdentity


RECENT_FILINGS = {
    "accessionNumber": [
        "0001326801-24-000100",
        "0001326801-24-000050",
        "0001326801-24-000020",
    ],
    "form": ["10-K", "10-Q", "8-K"],
    "filingDate": ["2024-02-02", "2024-04-25", "2024-03-01"],
    "reportDate": ["2023-12-31", "2024-03-31", ""],
    "primaryDocument": ["meta-20231231.htm", "meta-20240331.htm", "meta-8k.htm"],
}

HISTORY_FILES = [
    {
        "name": "CIK0001326801-submissions-001.json",
        "filingFrom": "2017-05-10",
        "filingTo": "2024-06-11",
        "filingCount": 2001,
    },
    {
        "name": "CIK0001326801-submissions-002.json",
        "filingFrom": "2005-05-06",
        "filingTo": "2017-05-08",
        "filingCount": 1188,
    },
]


class FetchSubmissionsTests(TestCase):
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
        self.client.get_json.return_value = {"filings": {"recent": RECENT_FILINGS}}

    def test_fetches_padded_cik_url_through_existing_client(self) -> None:
        result = fetch_submissions(self.client, self.company)

        expected_url = SUBMISSIONS_URL_TEMPLATE.format(cik_padded="0001326801")
        self.client.get_json.assert_called_once_with(expected_url)
        self.assertEqual(result.source_url, expected_url)

    def test_valid_response_produces_typed_submissions(self) -> None:
        result = fetch_submissions(self.client, self.company)

        self.assertIsInstance(result, SECSubmissions)
        self.assertIs(result.company, self.company)
        self.assertIsInstance(result.filings, tuple)
        self.assertTrue(all(isinstance(filing, SECFiling) for filing in result.filings))
        self.assertEqual(result.history_files, ())
        self.assertIs(result.retrieved_at.tzinfo, timezone.utc)

    def test_history_files_are_typed_and_preserve_sec_order(self) -> None:
        self.client.get_json.return_value = {
            "filings": {"recent": RECENT_FILINGS, "files": HISTORY_FILES}
        }

        result = fetch_submissions(self.client, self.company)

        expected_url = SUBMISSIONS_URL_TEMPLATE.format(cik_padded="0001326801")
        self.client.get_json.assert_called_once_with(expected_url)
        self.assertEqual(
            result.history_files,
            (
                SECSubmissionHistoryFile(
                    name="CIK0001326801-submissions-001.json",
                    filing_from=date(2017, 5, 10),
                    filing_to=date(2024, 6, 11),
                    filing_count=2001,
                ),
                SECSubmissionHistoryFile(
                    name="CIK0001326801-submissions-002.json",
                    filing_from=date(2005, 5, 6),
                    filing_to=date(2017, 5, 8),
                    filing_count=1188,
                ),
            ),
        )

    def test_empty_history_files_returns_empty_tuple(self) -> None:
        self.client.get_json.return_value = {
            "filings": {"recent": RECENT_FILINGS, "files": []}
        }

        result = fetch_submissions(self.client, self.company)

        self.assertEqual(result.history_files, ())

    def test_malformed_history_file_metadata_fails_explicitly(self) -> None:
        malformed_files = [
            {},
            ["not an object"],
            [{**HISTORY_FILES[0], "name": ""}],
            [{**HISTORY_FILES[0], "filingFrom": "not-a-date"}],
            [{**HISTORY_FILES[0], "filingTo": None}],
            [{**HISTORY_FILES[0], "filingCount": "2001"}],
            [{**HISTORY_FILES[0], "filingCount": True}],
        ]

        for files in malformed_files:
            with self.subTest(files=files):
                self.client.get_json.return_value = {
                    "filings": {"recent": RECENT_FILINGS, "files": files}
                }
                with self.assertRaises(SubmissionsDataError):
                    fetch_submissions(self.client, self.company)

    def test_multiple_rows_preserve_column_relationships_and_forms(self) -> None:
        result = fetch_submissions(self.client, self.company)

        self.assertEqual(
            result.filings,
            (
                SECFiling(
                    accession_number="0001326801-24-000100",
                    form="10-K",
                    filing_date=date(2024, 2, 2),
                    report_date=date(2023, 12, 31),
                    primary_document="meta-20231231.htm",
                ),
                SECFiling(
                    accession_number="0001326801-24-000050",
                    form="10-Q",
                    filing_date=date(2024, 4, 25),
                    report_date=date(2024, 3, 31),
                    primary_document="meta-20240331.htm",
                ),
                SECFiling(
                    accession_number="0001326801-24-000020",
                    form="8-K",
                    filing_date=date(2024, 3, 1),
                    report_date=None,
                    primary_document="meta-8k.htm",
                ),
            ),
        )

    def test_missing_optional_report_date_column_becomes_none(self) -> None:
        recent = {key: value[:1] for key, value in RECENT_FILINGS.items()}
        del recent["reportDate"]
        self.client.get_json.return_value = {"filings": {"recent": recent}}

        result = fetch_submissions(self.client, self.company)

        self.assertIsNone(result.filings[0].report_date)

    def test_inconsistent_parallel_array_lengths_fail_explicitly(self) -> None:
        recent = {key: list(value) for key, value in RECENT_FILINGS.items()}
        recent["form"] = recent["form"][:-1]
        self.client.get_json.return_value = {"filings": {"recent": recent}}

        with self.assertRaisesRegex(SubmissionsDataError, "inconsistent lengths"):
            fetch_submissions(self.client, self.company)

    def test_inconsistent_report_date_length_fails_explicitly(self) -> None:
        recent = {key: list(value) for key, value in RECENT_FILINGS.items()}
        recent["reportDate"] = recent["reportDate"][:-1]
        self.client.get_json.return_value = {"filings": {"recent": recent}}

        with self.assertRaisesRegex(SubmissionsDataError, "inconsistent lengths"):
            fetch_submissions(self.client, self.company)

    def test_malformed_required_fields_fail_explicitly(self) -> None:
        malformed_recent_values = [
            {"form": None},
            {"accessionNumber": [""] * 3},
            {"filingDate": ["not-a-date"] * 3},
            {"primaryDocument": [None] * 3},
        ]

        for replacement in malformed_recent_values:
            with self.subTest(replacement=replacement):
                recent = {key: list(value) for key, value in RECENT_FILINGS.items()}
                recent.update(replacement)
                self.client.get_json.return_value = {"filings": {"recent": recent}}

                with self.assertRaises(SubmissionsDataError):
                    fetch_submissions(self.client, self.company)

    def test_malformed_response_structure_fails_explicitly(self) -> None:
        for payload in ([], {}, {"filings": []}, {"filings": {}}):
            with self.subTest(payload=payload):
                self.client.get_json.return_value = payload
                with self.assertRaises(SubmissionsDataError):
                    fetch_submissions(self.client, self.company)

    def test_empty_recent_filings_returns_empty_tuple(self) -> None:
        empty_recent = {
            "accessionNumber": [],
            "form": [],
            "filingDate": [],
            "reportDate": [],
            "primaryDocument": [],
        }
        self.client.get_json.return_value = {"filings": {"recent": empty_recent}}

        result = fetch_submissions(self.client, self.company)

        self.assertEqual(result.filings, ())


class FetchSubmissionHistoryTests(TestCase):
    def setUp(self) -> None:
        self.client = Mock(spec=SECClient)
        self.history_file = SECSubmissionHistoryFile(
            name="CIK0001326801-submissions-001.json",
            filing_from=date(2017, 5, 10),
            filing_to=date(2024, 6, 11),
            filing_count=2001,
        )
        self.client.get_json.return_value = RECENT_FILINGS

    def test_fetches_sec_filename_url_through_existing_client(self) -> None:
        result = fetch_submission_history(self.client, self.history_file)

        expected_url = SUBMISSION_HISTORY_URL_TEMPLATE.format(
            name="CIK0001326801-submissions-001.json"
        )
        self.client.get_json.assert_called_once_with(expected_url)
        self.assertEqual(len(result), 3)

    def test_supplemental_rows_parse_with_relationships_preserved(self) -> None:
        result = fetch_submission_history(self.client, self.history_file)

        self.assertEqual(
            result,
            (
                SECFiling(
                    accession_number="0001326801-24-000100",
                    form="10-K",
                    filing_date=date(2024, 2, 2),
                    report_date=date(2023, 12, 31),
                    primary_document="meta-20231231.htm",
                ),
                SECFiling(
                    accession_number="0001326801-24-000050",
                    form="10-Q",
                    filing_date=date(2024, 4, 25),
                    report_date=date(2024, 3, 31),
                    primary_document="meta-20240331.htm",
                ),
                SECFiling(
                    accession_number="0001326801-24-000020",
                    form="8-K",
                    filing_date=date(2024, 3, 1),
                    report_date=None,
                    primary_document="meta-8k.htm",
                ),
            ),
        )

    def test_missing_report_date_column_becomes_none(self) -> None:
        payload = {key: value[:1] for key, value in RECENT_FILINGS.items()}
        del payload["reportDate"]
        self.client.get_json.return_value = payload

        result = fetch_submission_history(self.client, self.history_file)

        self.assertIsNone(result[0].report_date)

    def test_malformed_or_inconsistent_arrays_fail_explicitly(self) -> None:
        malformed_payloads = [
            [],
            {**RECENT_FILINGS, "form": RECENT_FILINGS["form"][:-1]},
            {**RECENT_FILINGS, "filingDate": ["not-a-date"] * 3},
            {**RECENT_FILINGS, "reportDate": RECENT_FILINGS["reportDate"][:-1]},
        ]

        for payload in malformed_payloads:
            with self.subTest(payload=payload):
                self.client.get_json.return_value = payload
                with self.assertRaises(SubmissionsDataError):
                    fetch_submission_history(self.client, self.history_file)

    def test_empty_supplemental_arrays_return_empty_tuple(self) -> None:
        self.client.get_json.return_value = {
            "accessionNumber": [],
            "form": [],
            "filingDate": [],
            "reportDate": [],
            "primaryDocument": [],
        }

        result = fetch_submission_history(self.client, self.history_file)

        self.assertEqual(result, ())
