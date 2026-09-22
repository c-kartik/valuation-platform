"""HTTP transport for official SEC JSON resources."""

from __future__ import annotations

from typing import Any

import requests


DEFAULT_TIMEOUT_SECONDS = 10.0


class SECClientError(Exception):
    """Base exception for SEC transport failures."""


class SECRequestError(SECClientError):
    """Raised when an SEC HTTP request fails."""


class SECResponseError(SECClientError):
    """Raised when an SEC response cannot be decoded as JSON."""


class SECClient:
    """Small reusable client for conservative access to SEC JSON endpoints."""

    def __init__(
        self,
        user_agent: str,
        *,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        session: requests.Session | None = None,
    ) -> None:
        normalized_user_agent = user_agent.strip()
        if not normalized_user_agent:
            raise ValueError("An identifying SEC User-Agent is required")
        if timeout <= 0:
            raise ValueError("SEC request timeout must be greater than zero")

        self._user_agent = normalized_user_agent
        self._timeout = timeout
        self._session = session or requests.Session()

    def get_json(self, url: str) -> Any:
        """Fetch one SEC resource and decode its JSON response."""
        try:
            response = self._session.get(
                url,
                headers={
                    "User-Agent": self._user_agent,
                    "Accept": "application/json",
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SECRequestError(f"SEC request failed for {url}: {exc}") from exc

        try:
            return response.json()
        except (requests.exceptions.JSONDecodeError, ValueError) as exc:
            raise SECResponseError(
                f"SEC response from {url} was not valid JSON"
            ) from exc
