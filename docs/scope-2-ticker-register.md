# Scope 2 — ticker readiness register

Planning checkpoint: November 7, 2026. Scope 2 implementation has not started.
This register separates product acceptance from historical preparation phases.

| Ticker | Scope 1 named DCF consumer | S2.0 data | S2.1 overview | S2.2 return drivers | S2.3 events | S2.4 dip finder |
| --- | --- | --- | --- | --- | --- | --- |
| AAPL | ANALYST_READY_WITH_QUALIFICATIONS | NOT_ASSESSED | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED |
| META | ANALYST_READY_WITH_QUALIFICATIONS | NOT_ASSESSED | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED |
| GOOGL | ANALYST_READY_WITH_QUALIFICATIONS | NOT_ASSESSED | NOT_STARTED | NOT_STARTED | NOT_STARTED | NOT_STARTED |

Scope 1 references: [AAPL](company-resolutions/AAPL/analyst-ready-2026-11-04/README.md),
[META](company-resolutions/META/analyst-ready-2026-11-04/README.md),
[GOOGL](company-resolutions/GOOGL/analyst-ready-2026-11-04/README.md).
Accepted financial/source qualifications remain in those records.

Shared unresolved gates: market provider/public-use rights and budget; adjustment
and availability contracts; metric definitions/coverage; benchmark and event rules;
current-date valuation/freshness policy. These are planning dependencies, not
newly discovered defects in the accepted fiscal-end DCF consumers.

All other tickers remain under their existing preparation/classification/pause
records, with no Scope 1 or Scope 2 promotion implied here. Add a row only for a
specifically authorized issuer, following [onboarding](ticker-onboarding-checklist.md).
Do not copy a pilot's completion badge or financial assumptions.

Per-feature status must link to a source package, method version, tests and named
consumer acceptance before it changes to ready. Historical DCF curves (S2.4H)
remain a separately scoped deferred milestone for every issuer.

## Financial-statements-only consumer — November 9, 2026

GOOGL/AAPL/META each have 20-quarter descriptive reporting prepared and integrated
locally under [the separate reporting contract](quarterly-reporting.md). This
does not change original market-feature readiness cells. Filing checks cover
latest-quarter/latest-annual operands; Other remains grouped.
