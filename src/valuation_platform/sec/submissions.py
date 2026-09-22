"""Retrieve and parse recent SEC filing metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from .client import SECClient
from .tickers import SECCompanyIdentity


SUBMISSIONS_URL_TEMPLATE = "https://data.sec.gov/submissions/CIK{cik_padded}.json"


class SubmissionsDataError(Exception):
    """Raised when SEC submissions data is malformed or inconsistent."""


@dataclass(frozen=True)
class SECFiling:
    """Metadata for one filing in an SEC submissions response."""

    accession_number: str
    form: str
    filing_date: date
    report_date: date | None
    primary_document: str


@dataclass(frozen=True)
class SECSubmissions:
    """Recent SEC filing history for a resolved company."""

    company: SECCompanyIdentity
    filings: tuple[SECFiling, ...]
    source_url: str
    retrieved_at: datetime


def fetch_submissions(
    client: SECClient,
    company: SECCompanyIdentity,
) -> SECSubmissions:
    """Fetch and parse the main SEC submissions response for a company."""
    source_url = SUBMISSIONS_URL_TEMPLATE.format(cik_padded=company.cik_padded)
    payload = client.get_json(source_url)

    return SECSubmissions(
        company=company,
        filings=_parse_recent_filings(payload),
        source_url=source_url,
        retrieved_at=datetime.now(timezone.utc),
    )


def _parse_recent_filings(payload: Any) -> tuple[SECFiling, ...]:
    if not isinstance(payload, dict):
        raise SubmissionsDataError("SEC submissions response must be a JSON object")

    filings = payload.get("filings")
    if not isinstance(filings, dict):
        raise SubmissionsDataError("SEC submissions response must contain filings")

    recent = filings.get("recent")
    if not isinstance(recent, dict):
        raise SubmissionsDataError(
            "SEC submissions response must contain filings.recent"
        )

    accession_numbers = _required_string_column(recent, "accessionNumber")
    forms = _required_string_column(recent, "form")
    filing_dates = _required_string_column(recent, "filingDate")
    primary_documents = _required_string_column(recent, "primaryDocument")

    row_count = len(accession_numbers)
    required_lengths = {
        "accessionNumber": row_count,
        "form": len(forms),
        "filingDate": len(filing_dates),
        "primaryDocument": len(primary_documents),
    }
    if len(set(required_lengths.values())) != 1:
        raise SubmissionsDataError(
            f"SEC recent filing columns have inconsistent lengths: {required_lengths}"
        )

    report_dates = _report_date_column(recent, row_count)

    parsed_filings = []
    for row_index in range(row_count):
        parsed_filings.append(
            SECFiling(
                accession_number=accession_numbers[row_index],
                form=forms[row_index],
                filing_date=_parse_date(
                    filing_dates[row_index], "filingDate", row_index
                ),
                report_date=_parse_optional_date(report_dates[row_index], row_index),
                primary_document=primary_documents[row_index],
            )
        )

    return tuple(parsed_filings)


def _required_string_column(recent: dict[str, Any], name: str) -> list[str]:
    column = recent.get(name)
    if not isinstance(column, list):
        raise SubmissionsDataError(
            f"SEC recent filings field {name!r} must be an array"
        )

    for row_index, value in enumerate(column):
        if not isinstance(value, str) or not value:
            raise SubmissionsDataError(
                f"SEC recent filings field {name!r} has an invalid value "
                f"at row {row_index}"
            )

    return column


def _report_date_column(recent: dict[str, Any], row_count: int) -> list[str | None]:
    if "reportDate" not in recent:
        return [None] * row_count

    column = recent["reportDate"]
    if not isinstance(column, list):
        raise SubmissionsDataError(
            "SEC recent filings field 'reportDate' must be an array"
        )
    if len(column) != row_count:
        raise SubmissionsDataError(
            "SEC recent filing columns have inconsistent lengths: "
            f"reportDate has {len(column)} rows; expected {row_count}"
        )

    for row_index, value in enumerate(column):
        if value is not None and not isinstance(value, str):
            raise SubmissionsDataError(
                "SEC recent filings field 'reportDate' has an invalid value "
                f"at row {row_index}"
            )

    return column


def _parse_date(value: str, field_name: str, row_index: int) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise SubmissionsDataError(
            f"SEC recent filings field {field_name!r} has an invalid date "
            f"at row {row_index}: {value!r}"
        ) from exc

    if parsed.isoformat() != value:
        raise SubmissionsDataError(
            f"SEC recent filings field {field_name!r} must use YYYY-MM-DD "
            f"at row {row_index}: {value!r}"
        )
    return parsed


def _parse_optional_date(value: str | None, row_index: int) -> date | None:
    if value is None or value == "":
        return None
    return _parse_date(value, "reportDate", row_index)
