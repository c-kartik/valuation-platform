from contextlib import redirect_stderr
from datetime import date, datetime, timezone
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from scripts.validate_company_facts import (
    DEFAULT_TICKERS,
    ValidationFailure,
    ValidationSuccess,
    main,
    run,
    validate_company_facts,
)
from valuation_platform.sec import (
    SECClient,
    SECCompanyFacts,
    SECCompanyIdentity,
    SECFactConcept,
    SECFactObservation,
)


def make_company(ticker: str, cik: int) -> SECCompanyIdentity:
    return SECCompanyIdentity(
        ticker=ticker,
        cik=cik,
        cik_padded=f"{cik:010d}",
        company_name=f"{ticker} Company",
        source_url="ticker-source",
        retrieved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def make_facts(company: SECCompanyIdentity, observation_count: int) -> SECCompanyFacts:
    observations = tuple(
        SECFactObservation(
            unit="USD",
            value=index,
            start=date(2025, 1, 1),
            end=date(2025, 12, 31),
            accession_number=f"accession-{index}",
            fiscal_year=2025,
            fiscal_period="FY",
            form="10-K",
            filed=date(2026, 1, 1),
            frame=None,
        )
        for index in range(observation_count)
    )
    return SECCompanyFacts(
        company=company,
        entity_name=f"{company.ticker} Entity",
        concepts=(
            SECFactConcept(
                taxonomy="us-gaap",
                name="Revenue",
                label=None,
                description="Revenue",
                observations=observations,
            ),
            SECFactConcept(
                taxonomy="dei",
                name="EntityName",
                label="Entity Name",
                description=None,
                observations=(),
            ),
        ),
        source_url="facts-source",
        retrieved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


class ValidateCompanyFactsTests(TestCase):
    def setUp(self) -> None:
        self.client = Mock(spec=SECClient)
        self.companies = {
            "META": make_company("META", 1326801),
            "AAPL": make_company("AAPL", 320193),
            "MSFT": make_company("MSFT", 789019),
        }

    @patch("scripts.validate_company_facts.fetch_company_facts")
    @patch("scripts.validate_company_facts.resolve_ticker")
    def test_multiple_successes_and_summary_counts(
        self, resolve_mock: Mock, fetch_mock: Mock
    ) -> None:
        resolve_mock.side_effect = lambda ticker, client: self.companies[ticker]
        fetch_mock.side_effect = lambda client, company: make_facts(
            company, 2 if company.ticker == "META" else 3
        )
        output = StringIO()

        status = run(self.client, ("META", "AAPL"), output)

        self.assertEqual(status, 0)
        report = output.getvalue()
        self.assertIn("Companies attempted: 2", report)
        self.assertIn("Companies succeeded: 2", report)
        self.assertIn("Companies failed: 0", report)
        self.assertIn("Total concepts parsed: 4", report)
        self.assertIn("Total observations parsed: 5", report)
        self.assertIn("META | success | 2 | 2 | 1 | 1", report)
        self.assertIn("AAPL | success | 2 | 3 | 1 | 1", report)

    @patch("scripts.validate_company_facts.fetch_company_facts")
    @patch("scripts.validate_company_facts.resolve_ticker")
    def test_ticker_failure_does_not_stop_later_ticker(
        self, resolve_mock: Mock, fetch_mock: Mock
    ) -> None:
        def resolve(ticker: str, client: SECClient) -> SECCompanyIdentity:
            if ticker == "BAD":
                raise LookupError("unknown ticker")
            return self.companies[ticker]

        resolve_mock.side_effect = resolve
        fetch_mock.side_effect = lambda client, company: make_facts(company, 1)

        results = validate_company_facts(self.client, ("BAD", "MSFT"))

        self.assertIsInstance(results[0], ValidationFailure)
        self.assertEqual(results[0].stage, "ticker resolution")
        self.assertIsInstance(results[1], ValidationSuccess)
        fetch_mock.assert_called_once_with(self.client, self.companies["MSFT"])

    @patch("scripts.validate_company_facts.fetch_company_facts")
    @patch("scripts.validate_company_facts.resolve_ticker")
    def test_company_facts_failure_does_not_stop_later_ticker(
        self, resolve_mock: Mock, fetch_mock: Mock
    ) -> None:
        resolve_mock.side_effect = lambda ticker, client: self.companies[ticker]

        def fetch(client: SECClient, company: SECCompanyIdentity) -> SECCompanyFacts:
            if company.ticker == "META":
                raise ValueError("malformed facts")
            return make_facts(company, 1)

        fetch_mock.side_effect = fetch

        results = validate_company_facts(self.client, ("META", "AAPL"))

        self.assertIsInstance(results[0], ValidationFailure)
        self.assertEqual(results[0].stage, "Company Facts retrieval/parsing")
        self.assertEqual(results[0].exception_type, "ValueError")
        self.assertEqual(results[0].message, "malformed facts")
        self.assertIsInstance(results[1], ValidationSuccess)
        self.assertEqual(fetch_mock.call_count, 2)

    @patch("scripts.validate_company_facts.fetch_company_facts")
    @patch("scripts.validate_company_facts.resolve_ticker")
    def test_nonzero_status_when_any_company_fails(
        self, resolve_mock: Mock, fetch_mock: Mock
    ) -> None:
        resolve_mock.side_effect = LookupError("unknown ticker")
        output = StringIO()

        status = run(self.client, ("BAD",), output)

        self.assertEqual(status, 1)
        self.assertIn(
            "BAD | ticker resolution | LookupError: unknown ticker",
            output.getvalue(),
        )
        fetch_mock.assert_not_called()

    def test_cli_uses_default_corpus_and_requires_user_agent(self) -> None:
        with patch("scripts.validate_company_facts.run", return_value=0) as run_mock:
            status = main([], environ={"SEC_USER_AGENT": "Project contact@example.com"})

        self.assertEqual(status, 0)
        self.assertEqual(run_mock.call_args.args[1], DEFAULT_TICKERS)

        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            main([], environ={})
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("SEC_USER_AGENT", stderr.getvalue())
