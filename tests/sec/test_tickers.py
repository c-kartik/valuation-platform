from datetime import timezone
from unittest import TestCase
from unittest.mock import Mock

from valuation_platform.sec.tickers import (
    COMPANY_TICKERS_URL,
    TickerDataError,
    TickerNotFoundError,
    resolve_ticker,
)


SEC_RESPONSE = {
    "0": {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA CORP"},
    "1": {
        "cik_str": 1326801,
        "ticker": "META",
        "title": "Meta Platforms, Inc.",
    },
}


class ResolveTickerTests(TestCase):
    def setUp(self) -> None:
        self.client = Mock()
        self.client.get_json.return_value = SEC_RESPONSE

    def test_meta_resolves_with_identity_and_provenance(self) -> None:
        identity = resolve_ticker("META", self.client)

        self.assertEqual(identity.ticker, "META")
        self.assertEqual(identity.cik, 1326801)
        self.assertEqual(identity.cik_padded, "0001326801")
        self.assertEqual(identity.company_name, "Meta Platforms, Inc.")
        self.assertEqual(identity.source_url, COMPANY_TICKERS_URL)
        self.assertIs(identity.retrieved_at.tzinfo, timezone.utc)
        self.client.get_json.assert_called_once_with(COMPANY_TICKERS_URL)

    def test_lowercase_ticker_is_normalized(self) -> None:
        self.assertEqual(resolve_ticker("meta", self.client).ticker, "META")

    def test_surrounding_whitespace_is_stripped(self) -> None:
        self.assertEqual(resolve_ticker("  META\n", self.client).ticker, "META")

    def test_unknown_ticker_raises_domain_error(self) -> None:
        with self.assertRaisesRegex(TickerNotFoundError, "'UNKNOWN'"):
            resolve_ticker("unknown", self.client)

    def test_malformed_response_raises_domain_error(self) -> None:
        malformed_responses = [
            [],
            {"0": "not an object"},
            {"0": {"cik_str": "1326801", "ticker": "META", "title": "Meta"}},
            {"0": {"cik_str": 1326801, "title": "Meta"}},
        ]

        for response in malformed_responses:
            with self.subTest(response=response):
                self.client.get_json.return_value = response
                with self.assertRaises(TickerDataError):
                    resolve_ticker("META", self.client)

    def test_duplicate_exact_matches_fail_as_ambiguous(self) -> None:
        self.client.get_json.return_value = {
            "0": SEC_RESPONSE["1"],
            "1": SEC_RESPONSE["1"],
        }

        with self.assertRaisesRegex(TickerDataError, "multiple matches"):
            resolve_ticker("META", self.client)
