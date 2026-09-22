from datetime import date, datetime, timezone
from random import Random
from unittest import TestCase
from unittest.mock import Mock, call, patch

from valuation_platform.sec.client import SECClient
from valuation_platform.sec.filing_selection import (
    FilingSelectionError,
    load_and_select_filings,
    select_filings,
)
from valuation_platform.sec.submissions import (
    SECFiling,
    SECSubmissionHistoryFile,
    SECSubmissions,
)
from valuation_platform.sec.tickers import SECCompanyIdentity


def make_filing(
    form: str,
    report_date: date | None,
    *,
    accession_suffix: str = "1",
) -> SECFiling:
    report_label = report_date.isoformat() if report_date else "missing"
    filing_date = report_date or date(2020, 1, 1)
    return SECFiling(
        accession_number=f"{form}-{report_label}-{accession_suffix}",
        form=form,
        filing_date=filing_date,
        report_date=report_date,
        primary_document=f"{form}-{report_label}.htm",
    )


class SelectFilingsTests(TestCase):
    def test_selects_latest_five_annual_periods_in_chronological_order(self) -> None:
        filings = [
            make_filing("10-K", date(year, 12, 31))
            for year in range(2017, 2026)
        ]

        selected = select_filings(reversed(filings))

        self.assertEqual(
            [filing.report_date for filing in selected.annual],
            [date(year, 12, 31) for year in range(2021, 2026)],
        )
        self.assertTrue(selected.has_complete_annual_history)

    def test_selects_only_exact_quarters_after_latest_annual_period(self) -> None:
        annual = make_filing("10-K", date(2024, 12, 31))
        older_quarter = make_filing("10-Q", date(2024, 9, 30))
        first_quarter = make_filing("10-Q", date(2025, 3, 31))
        second_quarter = make_filing("10-Q", date(2025, 6, 30))
        amended_quarter = make_filing("10-Q/A", date(2025, 6, 30))

        selected = select_filings(
            [second_quarter, older_quarter, amended_quarter, annual, first_quarter],
            annual_limit=1,
        )

        self.assertEqual(selected.interim, (first_quarter, second_quarter))

    def test_excludes_annual_and_quarterly_amendments(self) -> None:
        annual = make_filing("10-K", date(2024, 12, 31))
        amended_annual = make_filing("10-K/A", date(2024, 12, 31))
        amended_quarter = make_filing("10-Q/A", date(2025, 3, 31))

        selected = select_filings(
            [amended_annual, amended_quarter, annual],
            annual_limit=1,
        )

        self.assertEqual(selected.annual, (annual,))
        self.assertEqual(selected.interim, ())

    def test_short_history_returns_available_and_reports_incomplete(self) -> None:
        filings = [
            make_filing("10-K", date(2023, 12, 31)),
            make_filing("10-K", date(2024, 12, 31)),
        ]

        selected = select_filings(filings, annual_limit=5)

        self.assertEqual(selected.annual, tuple(filings))
        self.assertEqual(selected.requested_annual_periods, 5)
        self.assertFalse(selected.has_complete_annual_history)

    def test_annual_limit_one_selects_latest_period(self) -> None:
        older = make_filing("10-K", date(2023, 12, 31))
        latest = make_filing("10-K", date(2024, 12, 31))

        selected = select_filings([latest, older], annual_limit=1)

        self.assertEqual(selected.annual, (latest,))
        self.assertTrue(selected.has_complete_annual_history)

    def test_invalid_annual_limit_is_rejected(self) -> None:
        for annual_limit in (0, -1, True, False, 1.5, "5"):
            with self.subTest(annual_limit=annual_limit):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    select_filings([], annual_limit=annual_limit)

    def test_duplicate_annual_report_date_fails_explicitly(self) -> None:
        filings = [
            make_filing("10-K", date(2024, 12, 31), accession_suffix="1"),
            make_filing("10-K", date(2024, 12, 31), accession_suffix="2"),
        ]

        with self.assertRaisesRegex(FilingSelectionError, "Multiple exact 10-K"):
            select_filings(filings)

    def test_duplicate_relevant_quarter_report_date_fails_explicitly(self) -> None:
        filings = [
            make_filing("10-K", date(2024, 12, 31)),
            make_filing("10-Q", date(2025, 3, 31), accession_suffix="1"),
            make_filing("10-Q", date(2025, 3, 31), accession_suffix="2"),
        ]

        with self.assertRaisesRegex(FilingSelectionError, "Multiple exact 10-Q"):
            select_filings(filings, annual_limit=1)

    def test_missing_report_date_for_exact_candidate_fails_explicitly(self) -> None:
        with self.assertRaisesRegex(FilingSelectionError, "has no report date"):
            select_filings([make_filing("10-K", None)])

    def test_input_order_does_not_affect_output(self) -> None:
        filings = [
            *(make_filing("10-K", date(year, 12, 31)) for year in range(2019, 2025)),
            make_filing("10-Q", date(2025, 3, 31)),
            make_filing("10-Q", date(2025, 6, 30)),
            make_filing("8-K", date(2025, 7, 1)),
        ]
        shuffled = list(filings)
        Random(42).shuffle(shuffled)

        self.assertEqual(select_filings(filings), select_filings(shuffled))


class LoadAndSelectFilingsTests(TestCase):
    def setUp(self) -> None:
        self.client = Mock(spec=SECClient)
        self.company = SECCompanyIdentity(
            ticker="META",
            cik=1326801,
            cik_padded="0001326801",
            company_name="Meta Platforms, Inc.",
            source_url="https://www.sec.gov/files/company_tickers.json",
            retrieved_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        self.history_files = tuple(
            SECSubmissionHistoryFile(
                name=f"history-{index}.json",
                filing_from=date(2010 + index, 1, 1),
                filing_to=date(2010 + index, 12, 31),
                filing_count=1,
            )
            for index in range(1, 4)
        )

    def submissions(
        self,
        filings: tuple[SECFiling, ...],
        history_files: tuple[SECSubmissionHistoryFile, ...] | None = None,
    ) -> SECSubmissions:
        return SECSubmissions(
            company=self.company,
            filings=filings,
            history_files=history_files or (),
            source_url="https://data.sec.gov/submissions/CIK0001326801.json",
            retrieved_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

    def test_does_not_fetch_history_when_recent_is_sufficient(self) -> None:
        recent = tuple(
            make_filing("10-K", date(year, 12, 31)) for year in range(2020, 2025)
        )

        with (
            patch(
                "valuation_platform.sec.filing_selection.fetch_submissions",
                return_value=self.submissions(recent, self.history_files),
            ) as fetch_main,
            patch(
                "valuation_platform.sec.filing_selection.fetch_submission_history"
            ) as fetch_history,
        ):
            selected = load_and_select_filings(self.client, self.company)

        fetch_main.assert_called_once_with(self.client, self.company)
        fetch_history.assert_not_called()
        self.assertTrue(selected.has_complete_annual_history)

    def test_fetches_one_at_a_time_and_stops_when_sufficient(self) -> None:
        recent = tuple(
            make_filing("10-K", date(year, 12, 31)) for year in range(2023, 2025)
        )
        first_history = tuple(
            make_filing("10-K", date(year, 12, 31)) for year in range(2020, 2023)
        )

        with (
            patch(
                "valuation_platform.sec.filing_selection.fetch_submissions",
                return_value=self.submissions(recent, self.history_files),
            ),
            patch(
                "valuation_platform.sec.filing_selection.fetch_submission_history",
                return_value=first_history,
            ) as fetch_history,
        ):
            selected = load_and_select_filings(self.client, self.company)

        fetch_history.assert_called_once_with(self.client, self.history_files[0])
        self.assertTrue(selected.has_complete_annual_history)

    def test_fetches_multiple_history_files_when_required(self) -> None:
        recent = (make_filing("10-K", date(2024, 12, 31)),)
        history_results = [
            (
                make_filing("10-K", date(2023, 12, 31)),
                make_filing("10-K", date(2022, 12, 31)),
            ),
            (
                make_filing("10-K", date(2021, 12, 31)),
                make_filing("10-K", date(2020, 12, 31)),
            ),
        ]

        with (
            patch(
                "valuation_platform.sec.filing_selection.fetch_submissions",
                return_value=self.submissions(recent, self.history_files),
            ),
            patch(
                "valuation_platform.sec.filing_selection.fetch_submission_history",
                side_effect=history_results,
            ) as fetch_history,
        ):
            selected = load_and_select_filings(self.client, self.company)

        self.assertEqual(
            fetch_history.call_args_list,
            [
                call(self.client, self.history_files[0]),
                call(self.client, self.history_files[1]),
            ],
        )
        self.assertTrue(selected.has_complete_annual_history)

    def test_returns_all_available_history_when_request_cannot_be_met(self) -> None:
        recent = (make_filing("10-K", date(2024, 12, 31)),)
        available_history = [
            (make_filing("10-K", date(2023, 12, 31)),),
            (),
            (make_filing("8-K", date(2022, 12, 31)),),
        ]

        with (
            patch(
                "valuation_platform.sec.filing_selection.fetch_submissions",
                return_value=self.submissions(recent, self.history_files),
            ),
            patch(
                "valuation_platform.sec.filing_selection.fetch_submission_history",
                side_effect=available_history,
            ) as fetch_history,
        ):
            selected = load_and_select_filings(self.client, self.company)

        self.assertEqual(fetch_history.call_count, 3)
        self.assertEqual(len(selected.annual), 2)
        self.assertFalse(selected.has_complete_annual_history)

    def test_invalid_limit_is_rejected_before_retrieval(self) -> None:
        with patch(
            "valuation_platform.sec.filing_selection.fetch_submissions"
        ) as fetch_main:
            with self.assertRaises(ValueError):
                load_and_select_filings(self.client, self.company, annual_limit=True)

        fetch_main.assert_not_called()
