"""Resolve stock tickers using the SEC company ticker dataset."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .client import SECClient


COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


class TickerResolutionError(Exception):
    """Base exception for ticker identity resolution failures."""


class TickerNotFoundError(TickerResolutionError):
    """Raised when the SEC dataset contains no exact ticker match."""


class TickerDataError(TickerResolutionError):
    """Raised when the SEC ticker dataset is malformed or ambiguous."""


@dataclass(frozen=True)
class SECCompanyIdentity:
    """A company identity resolved from the official SEC ticker dataset."""

    ticker: str
    cik: int
    cik_padded: str
    company_name: str
    source_url: str
    retrieved_at: datetime


def resolve_ticker(ticker: str, client: SECClient) -> SECCompanyIdentity:
    """Resolve an exact ticker match to its SEC company identity."""
    normalized_ticker = ticker.strip().upper()
    if not normalized_ticker:
        raise TickerNotFoundError("Ticker must not be empty")

    payload = client.get_json(COMPANY_TICKERS_URL)
    records = _parse_records(payload)
    matches = [record for record in records if record["ticker"] == normalized_ticker]

    if not matches:
        raise TickerNotFoundError(
            f"Ticker {normalized_ticker!r} was not found in the SEC ticker dataset"
        )
    if len(matches) > 1:
        raise TickerDataError(
            f"SEC ticker dataset contains multiple matches for {normalized_ticker!r}"
        )

    match = matches[0]
    cik = match["cik"]
    return SECCompanyIdentity(
        ticker=match["ticker"],
        cik=cik,
        cik_padded=f"{cik:010d}",
        company_name=match["company_name"],
        source_url=COMPANY_TICKERS_URL,
        retrieved_at=datetime.now(timezone.utc),
    )


def _parse_records(payload: Any) -> list[dict[str, str | int]]:
    if not isinstance(payload, dict):
        raise TickerDataError("SEC ticker dataset must be a JSON object")

    records: list[dict[str, str | int]] = []
    for record_key, raw_record in payload.items():
        if not isinstance(raw_record, dict):
            raise TickerDataError(
                f"SEC ticker record {record_key!r} must be a JSON object"
            )

        cik = raw_record.get("cik_str")
        ticker = raw_record.get("ticker")
        company_name = raw_record.get("title")
        if (
            not isinstance(cik, int)
            or isinstance(cik, bool)
            or cik < 0
            or not isinstance(ticker, str)
            or not ticker
            or not isinstance(company_name, str)
            or not company_name
        ):
            raise TickerDataError(
                f"SEC ticker record {record_key!r} has invalid or missing fields"
            )

        records.append(
            {
                "cik": cik,
                "ticker": ticker.strip().upper(),
                "company_name": company_name,
            }
        )

    return records
