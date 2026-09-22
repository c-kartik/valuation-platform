"""Select relevant filings and orchestrate the required SEC history."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .client import SECClient
from .submissions import SECFiling, fetch_submission_history, fetch_submissions
from .tickers import SECCompanyIdentity


class FilingSelectionError(Exception):
    """Raised when filing metadata cannot be selected unambiguously."""


@dataclass(frozen=True)
class SelectedFilings:
    """Annual and subsequent interim filings selected from SEC metadata."""

    annual: tuple[SECFiling, ...]
    interim: tuple[SECFiling, ...]
    requested_annual_periods: int

    @property
    def has_complete_annual_history(self) -> bool:
        """Whether the requested number of annual periods was available."""
        return len(self.annual) >= self.requested_annual_periods


def select_filings(
    filings: Iterable[SECFiling],
    annual_limit: int = 5,
) -> SelectedFilings:
    """Select annual filings and subsequent interim filings without I/O."""
    _validate_annual_limit(annual_limit)
    filing_records = tuple(filings)

    annual_by_report_date = _unique_filings_by_report_date(
        filing_records,
        form="10-K",
        context="annual",
    )
    annual_dates = sorted(annual_by_report_date)[-annual_limit:]
    annual = tuple(annual_by_report_date[report_date] for report_date in annual_dates)

    if not annual:
        return SelectedFilings(
            annual=(),
            interim=(),
            requested_annual_periods=annual_limit,
        )

    latest_annual_report_date = _required_report_date(annual[-1], "annual")

    relevant_quarters = (
        filing
        for filing in filing_records
        if filing.form == "10-Q"
        and _required_report_date(filing, "interim") > latest_annual_report_date
    )
    interim_by_report_date = _unique_filings_by_report_date(
        relevant_quarters,
        form="10-Q",
        context="interim",
    )
    interim = tuple(
        interim_by_report_date[report_date]
        for report_date in sorted(interim_by_report_date)
    )

    return SelectedFilings(
        annual=annual,
        interim=interim,
        requested_annual_periods=annual_limit,
    )


def load_and_select_filings(
    client: SECClient,
    company: SECCompanyIdentity,
    annual_limit: int = 5,
) -> SelectedFilings:
    """Load only enough SEC submissions history to satisfy the selector."""
    _validate_annual_limit(annual_limit)
    submissions = fetch_submissions(client, company)
    loaded_filings = list(submissions.filings)
    selected = select_filings(loaded_filings, annual_limit)

    if selected.has_complete_annual_history:
        return selected

    for history_file in submissions.history_files:
        loaded_filings.extend(fetch_submission_history(client, history_file))
        selected = select_filings(loaded_filings, annual_limit)
        if selected.has_complete_annual_history:
            break

    return selected


def _unique_filings_by_report_date(
    filings: Iterable[SECFiling],
    *,
    form: str,
    context: str,
) -> dict[date, SECFiling]:
    by_report_date: dict[date, SECFiling] = {}
    for filing in filings:
        if filing.form != form:
            continue

        report_date = _required_report_date(filing, context)
        if report_date in by_report_date:
            raise FilingSelectionError(
                f"Multiple exact {form} filings have report date {report_date}"
            )
        by_report_date[report_date] = filing

    return by_report_date


def _required_report_date(filing: SECFiling, context: str) -> date:
    if filing.report_date is None:
        raise FilingSelectionError(
            f"Exact {filing.form} {context} candidate "
            f"{filing.accession_number!r} has no report date"
        )
    return filing.report_date


def _validate_annual_limit(annual_limit: int) -> None:
    if (
        not isinstance(annual_limit, int)
        or isinstance(annual_limit, bool)
        or annual_limit <= 0
    ):
        raise ValueError("annual_limit must be a positive integer")
