from unittest import TestCase
from unittest.mock import Mock

import requests

from valuation_platform.sec.client import (
    SECClient,
    SECRequestError,
    SECResponseError,
)


class SECClientTests(TestCase):
    def test_get_json_sends_required_headers_and_timeout(self) -> None:
        response = Mock()
        response.json.return_value = {"ok": True}
        session = Mock()
        session.get.return_value = response
        client = SECClient(
            "Valuation Platform contact@example.com",
            timeout=7.5,
            session=session,
        )

        result = client.get_json("https://www.sec.gov/example.json")

        self.assertEqual(result, {"ok": True})
        session.get.assert_called_once_with(
            "https://www.sec.gov/example.json",
            headers={
                "User-Agent": "Valuation Platform contact@example.com",
                "Accept": "application/json",
            },
            timeout=7.5,
        )
        response.raise_for_status.assert_called_once_with()

    def test_http_error_is_wrapped_in_domain_error(self) -> None:
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("503 unavailable")
        session = Mock()
        session.get.return_value = response
        client = SECClient("Valuation Platform contact@example.com", session=session)

        with self.assertRaisesRegex(SECRequestError, "SEC request failed"):
            client.get_json("https://www.sec.gov/example.json")

    def test_get_bytes_uses_shared_transport_behavior(self) -> None:
        response = Mock()
        response.content = b"<xbrl/>"
        session = Mock()
        session.get.return_value = response
        client = SECClient(
            "Valuation Platform contact@example.com",
            timeout=7.5,
            session=session,
        )

        result = client.get_bytes("https://www.sec.gov/example.xml")

        self.assertEqual(result, b"<xbrl/>")
        session.get.assert_called_once_with(
            "https://www.sec.gov/example.xml",
            headers={
                "User-Agent": "Valuation Platform contact@example.com",
                "Accept": "application/octet-stream",
            },
            timeout=7.5,
        )
        response.raise_for_status.assert_called_once_with()

    def test_invalid_json_is_wrapped_in_domain_error(self) -> None:
        response = Mock()
        response.json.side_effect = ValueError("invalid JSON")
        session = Mock()
        session.get.return_value = response
        client = SECClient("Valuation Platform contact@example.com", session=session)

        with self.assertRaisesRegex(SECResponseError, "was not valid JSON"):
            client.get_json("https://www.sec.gov/example.json")

    def test_identifying_user_agent_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "User-Agent"):
            SECClient("   ")
