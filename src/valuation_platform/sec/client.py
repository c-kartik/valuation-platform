"""HTTP transport for official SEC resources."""

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
    """Small reusable client for conservative access to SEC endpoints."""

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
        response = self._get_response(url, accept="application/json")
        try:
            return response.json()
        except (requests.exceptions.JSONDecodeError, ValueError) as exc:
            raise SECResponseError(
                f"SEC response from {url} was not valid JSON"
            ) from exc

    def get_bytes(self, url: str) -> bytes:
        """Fetch one SEC resource as raw response bytes."""
        response = self._get_response(url, accept="application/octet-stream")
        return response.content

    def _get_response(self, url: str, *, accept: str) -> requests.Response:
        try:
            response = self._session.get(
                url,
                headers={
                    "User-Agent": self._user_agent,
                    "Accept": accept,
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SECRequestError(f"SEC request failed for {url}: {exc}") from exc
        return response
