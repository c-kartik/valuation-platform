"""Explicit preload registrations, separate from historical-universe eligibility.

Adding a listing requires its own dataset/policy and an approved retained anchor;
being present in the Top 50 register never supplies default financial assumptions.
"""
ISSUERS = {
    'GOOGL': {'issuer': 'Alphabet Inc.', 'cik': 1652044, 'kind': 'googl-fy2025', 'dataset': 'googl-v1', 'listing_class': 'A', 'legacy_policy': True},
    'META': {'issuer': 'Meta Platforms, Inc.', 'cik': 1326801, 'kind': 'meta-fy2025', 'dataset': 'meta-v1', 'listing_class': 'A'},
    'AAPL': {'issuer': 'Apple Inc.', 'cik': 320193, 'kind': 'aapl-fy2025', 'dataset': 'aapl-v1', 'listing_class': 'Common'},
}
ALIASES = {'GOOG': 'GOOGL'}


def registration(ticker):
    if not isinstance(ticker, str):
        raise ValueError('UNSUPPORTED_PREPARATION: explicit ticker required')
    key = ALIASES.get(ticker.upper(), ticker.upper())
    if key not in ISSUERS:
        raise ValueError('UNSUPPORTED_PREPARATION: no reviewed preload registration')
    return ISSUERS[key]


def resolve_listing(ticker):
    spec = registration(ticker)
    return {'issuer': spec['issuer'], 'cik': spec['cik'], 'ticker': ticker.upper(),
            'listing_class': 'C' if ticker.upper() == 'GOOG' else spec['listing_class'],
            'class_equivalence': 'NOT_SELECTED'}


def routes():
    return {spec['kind']: '/api/v1/preloads/' + ticker.lower() for ticker, spec in ISSUERS.items()}
