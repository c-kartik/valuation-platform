"""SEC data access, identity resolution, and filing selection."""

from .client import SECClient, SECClientError, SECRequestError, SECResponseError
from .filing_selection import (
    FilingSelectionError,
    SelectedFilings,
    load_and_select_filings,
    select_filings,
)
from .submissions import (
    SECFiling,
    SECSubmissionHistoryFile,
    SECSubmissions,
    SubmissionsDataError,
    fetch_submission_history,
    fetch_submissions,
)
from .tickers import (
    SECCompanyIdentity,
    TickerDataError,
    TickerNotFoundError,
    TickerResolutionError,
    resolve_ticker,
)

__all__ = [
    "SECClient",
    "SECClientError",
    "SECCompanyIdentity",
    "FilingSelectionError",
    "SECFiling",
    "SECSubmissionHistoryFile",
    "SECRequestError",
    "SECResponseError",
    "SECSubmissions",
    "SelectedFilings",
    "SubmissionsDataError",
    "TickerDataError",
    "TickerNotFoundError",
    "TickerResolutionError",
    "fetch_submission_history",
    "fetch_submissions",
    "load_and_select_filings",
    "resolve_ticker",
    "select_filings",
]
