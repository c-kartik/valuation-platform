"""SEC data access and identity resolution."""

from .client import SECClient, SECClientError, SECRequestError, SECResponseError
from .submissions import (
    SECFiling,
    SECSubmissions,
    SubmissionsDataError,
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
    "SECFiling",
    "SECRequestError",
    "SECResponseError",
    "SECSubmissions",
    "SubmissionsDataError",
    "TickerDataError",
    "TickerNotFoundError",
    "TickerResolutionError",
    "fetch_submissions",
    "resolve_ticker",
]
