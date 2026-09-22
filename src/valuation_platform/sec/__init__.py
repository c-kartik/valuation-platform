"""SEC data access, filing selection, and Company Facts retrieval."""

from .client import SECClient, SECClientError, SECRequestError, SECResponseError
from .company_facts import (
    CompanyFactsDataError,
    SECCompanyFacts,
    SECFactConcept,
    SECFactObservation,
    SECFactValue,
    fetch_company_facts,
)
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
    "CompanyFactsDataError",
    "FilingSelectionError",
    "SECClient",
    "SECClientError",
    "SECCompanyFacts",
    "SECCompanyIdentity",
    "SECFactConcept",
    "SECFactObservation",
    "SECFactValue",
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
    "fetch_company_facts",
    "fetch_submission_history",
    "fetch_submissions",
    "load_and_select_filings",
    "resolve_ticker",
    "select_filings",
]
