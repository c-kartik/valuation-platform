"""Retrieve and parse SEC submissions filing metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from .client import SECClient
from .tickers import SECCompanyIdentity


SUBMISSIONS_URL_TEMPLATE = "https://data.sec.gov/submissions/CIK{cik_padded}.json"
SUBMISSION_HISTORY_URL_TEMPLATE = "https://data.sec.gov/submissions/{name}"


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
class SECSubmissionHistoryFile:
    """Metadata for one supplemental SEC submissions history file."""

    name: str
    filing_from: date
    filing_to: date
    filing_count: int


@dataclass(frozen=True)
class SECSubmissions:
    """Recent SEC filing history for a resolved company."""

    company: SECCompanyIdentity
    filings: tuple[SECFiling, ...]
    history_files: tuple[SECSubmissionHistoryFile, ...]
    source_url: str
    retrieved_at: datetime


def fetch_submissions(
    client: SECClient,
    company: SECCompanyIdentity,
) -> SECSubmissions:
    """Fetch and parse the main SEC submissions response for a company."""
    source_url = SUBMISSIONS_URL_TEMPLATE.format(cik_padded=company.cik_padded)
    payload = client.get_json(source_url)
    filings, history_files = _parse_main_submissions(payload)

    return SECSubmissions(
        company=company,
        filings=filings,
        history_files=history_files,
        source_url=source_url,
        retrieved_at=datetime.now(timezone.utc),
    )


def fetch_submission_history(
    client: SECClient,
    history_file: SECSubmissionHistoryFile,
) -> tuple[SECFiling, ...]:
    """Fetch and parse one explicitly requested submissions history file."""
    source_url = SUBMISSION_HISTORY_URL_TEMPLATE.format(name=history_file.name)
    payload = client.get_json(source_url)
    if not isinstance(payload, dict):
        raise SubmissionsDataError(
            "SEC supplemental submissions response must be a JSON object"
        )
    return _parse_filing_columns(payload, "supplemental filing")


def _parse_main_submissions(
    payload: Any,
) -> tuple[tuple[SECFiling, ...], tuple[SECSubmissionHistoryFile, ...]]:
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

    history_files = _parse_history_files(filings.get("files", []))
    return _parse_filing_columns(recent, "recent filing"), history_files


def _parse_filing_columns(
    columns: dict[str, Any],
    context: str,
) -> tuple[SECFiling, ...]:
    accession_numbers = _required_string_column(
        columns, "accessionNumber", context
    )
    forms = _required_string_column(columns, "form", context)
    filing_dates = _required_string_column(columns, "filingDate", context)
    primary_documents = _required_string_column(
        columns, "primaryDocument", context
    )

    row_count = len(accession_numbers)
    required_lengths = {
        "accessionNumber": row_count,
        "form": len(forms),
        "filingDate": len(filing_dates),
        "primaryDocument": len(primary_documents),
    }
    if len(set(required_lengths.values())) != 1:
        raise SubmissionsDataError(
            f"SEC {context} columns have inconsistent lengths: {required_lengths}"
        )

    report_dates = _report_date_column(columns, row_count, context)

    parsed_filings = []
    for row_index in range(row_count):
        parsed_filings.append(
            SECFiling(
                accession_number=accession_numbers[row_index],
                form=forms[row_index],
                filing_date=_parse_date(
                    filing_dates[row_index], "filingDate", f"{context} row {row_index}"
                ),
                report_date=_parse_optional_date(
                    report_dates[row_index], f"{context} row {row_index}"
                ),
                primary_document=primary_documents[row_index],
            )
        )

    return tuple(parsed_filings)


def _parse_history_files(value: Any) -> tuple[SECSubmissionHistoryFile, ...]:
    if not isinstance(value, list):
        raise SubmissionsDataError("SEC submissions filings.files must be an array")

    history_files = []
    for entry_index, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise SubmissionsDataError(
                f"SEC submissions history file at index {entry_index} "
                "must be a JSON object"
            )

        name = entry.get("name")
        filing_from = entry.get("filingFrom")
        filing_to = entry.get("filingTo")
        filing_count = entry.get("filingCount")
        if not isinstance(name, str) or not name:
            raise SubmissionsDataError(
                f"SEC submissions history file at index {entry_index} "
                "has an invalid or missing name"
            )
        if not isinstance(filing_from, str) or not filing_from:
            raise SubmissionsDataError(
                f"SEC submissions history file at index {entry_index} "
                "has an invalid or missing filingFrom"
            )
        if not isinstance(filing_to, str) or not filing_to:
            raise SubmissionsDataError(
                f"SEC submissions history file at index {entry_index} "
                "has an invalid or missing filingTo"
            )
        if (
            not isinstance(filing_count, int)
            or isinstance(filing_count, bool)
            or filing_count < 0
        ):
            raise SubmissionsDataError(
                f"SEC submissions history file at index {entry_index} "
                "has an invalid or missing filingCount"
            )

        history_files.append(
            SECSubmissionHistoryFile(
                name=name,
                filing_from=_parse_date(
                    filing_from, "filingFrom", f"history file {entry_index}"
                ),
                filing_to=_parse_date(
                    filing_to, "filingTo", f"history file {entry_index}"
                ),
                filing_count=filing_count,
            )
        )

    return tuple(history_files)


def _required_string_column(
    columns: dict[str, Any],
    name: str,
    context: str,
) -> list[str]:
    column = columns.get(name)
    if not isinstance(column, list):
        raise SubmissionsDataError(
            f"SEC {context} field {name!r} must be an array"
        )

    for row_index, value in enumerate(column):
        if not isinstance(value, str) or not value:
            raise SubmissionsDataError(
                f"SEC {context} field {name!r} has an invalid value "
                f"at row {row_index}"
            )

    return column


def _report_date_column(
    columns: dict[str, Any],
    row_count: int,
    context: str,
) -> list[str | None]:
    if "reportDate" not in columns:
        return [None] * row_count

    column = columns["reportDate"]
    if not isinstance(column, list):
        raise SubmissionsDataError(
            f"SEC {context} field 'reportDate' must be an array"
        )
    if len(column) != row_count:
        raise SubmissionsDataError(
            f"SEC {context} columns have inconsistent lengths: "
            f"reportDate has {len(column)} rows; expected {row_count}"
        )

    for row_index, value in enumerate(column):
        if value is not None and not isinstance(value, str):
            raise SubmissionsDataError(
                f"SEC {context} field 'reportDate' has an invalid value "
                f"at row {row_index}"
            )

    return column


def _parse_date(value: str, field_name: str, location: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise SubmissionsDataError(
            f"SEC field {field_name!r} has an invalid date at {location}: {value!r}"
        ) from exc

    if parsed.isoformat() != value:
        raise SubmissionsDataError(
            f"SEC field {field_name!r} must use YYYY-MM-DD "
            f"at {location}: {value!r}"
        )
    return parsed


def _parse_optional_date(value: str | None, location: str) -> date | None:
    if value is None or value == "":
        return None
    return _parse_date(value, "reportDate", location)
