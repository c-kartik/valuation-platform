# Trading comparables — peer financial preparation

Status: **OPEN — research preparation, no production integration or numerical exit default.**

User authorization: November 11, 2026. Prepare Alphabet and the six proposed peers using SEC financials; preserve the original Python/DCF pipeline. Apple and Netflix remain supporting operating references for a later increment, not members of this initial core financial package.

## Snapshot and observed coverage

Cutoff: 2026-11-11. Latest reported balance/quarter end: 2026-09-30 for all seven issuers. This is a financial-information cutoff, not an approved market-price valuation date. USD amounts are stored as integers. Microsoft fiscal years end in June; the others use December year ends.

| Issuer | Annual observations | Complete quarterly rows | First quarter start | TTM revenue, $bn | TTM EBIT, $bn | Filing checks |
|---|---:|---:|---|---:|---:|---:|
| GOOGL | 5 | 23 | 2021-01-01 | 471.098 | 156.976 | 28 |
| META | 5 | 23 | 2021-01-01 | 241.605 | 79.380 | 28 |
| PINS | 5 | 23 | 2021-01-01 | 4.680 | 0.196 | 25 |
| RDDT | 4 | 15 | 2023-01-01 | 3.089 | 0.908 | 21 |
| TTD | 5 | 23 | 2021-01-01 | 2.987 | 0.518 | 22 |
| MSFT | 6 | 25 | 2020-07-01 | 346.445 | 163.191 | 27 |
| AMZN | 5 | 23 | 2021-01-01 | 797.455 | 104.366 | 31 |

The 35 annual observations and 155 complete quarter rows are available-field preparation, not a claim that all eight metrics exist in every period. Missing observations remain null. Annual comparatives use the latest available same-filing observations in the frozen Company Facts snapshot; quarterly YTD operands can have different revision vintages. Same-filing discrete comparisons retain eleven $1m differences across Alphabet/Meta rather than silently rewriting figures.

## What was checked

- 182 selected operands match retained filing-level extracted XBRL: latest annual, current/prior YTD used for TTM, and latest balance candidates. No outstanding source errors or contradictory facts in this check scope.
- 32 exact business-component/segment-total reconciliations across Alphabet, Meta, Reddit, Microsoft and Amazon. Pinterest/Trade Desk have no approved component aggregation checks; zero checks is not a pass claim.
- 212 available annual-to-quarter arithmetic checks match; 68 combinations are explicitly incomplete. Q4 subtraction creates an arithmetic identity, not independent economic certification.
- Fifteen financial safety/snapshot tests pass. Frozen preparation and business review reproduce offline with identical output bytes.
- This is not independent manual certification of all historical quarterly rows, all footnote treatments or valuation readiness. The two SEC representations validate extraction consistency, not an external financial audit.

## Selection and financial conventions

Reuses the existing SEC transport, submissions parser and structural filing-XBRL parser through new scripts only. Company Facts is the consolidated selection index; retained filing XML supplies fact checks and dimensional business observations. Every selected operand retains concept, start/end, accession, filing date and source URL. Source bytes have SHA-256 receipts.

TTM = latest fiscal annual + current fiscal YTD - prior fiscal YTD disclosed in the same current interim filing. Quarters use actual fiscal start/end dates and successive YTD differences; annual Q4 is annual less nine months. Incomplete fiscal cohorts are retained as gaps. Ratios with missing/zero denominators are unavailable; negative EBIT is preserved.

EBIT means GAAP operating income with SBC retained. Cash FCF means reported CFO less gross cash-capex purchases, not FCFF/FCFE. Depreciation-only, reported D&A and intangible amortization are distinct raw fields. No EBITDA or enterprise value is published by this preparation.

Business mappings use exact concept/dimension sets and USD measures, preserve corporate costs and hedging, and never add segment and product aggregations together. AWS/Azure do not have observed standalone enterprise values. Historical Microsoft structures are not combined without recast-period review.

Repeated filing facts must include an exact match; other repetitions must agree within their declared XBRL precision. Coarse note rounding is recorded, not accepted using an arbitrary dollar tolerance.

## Issuer-specific findings

- **GOOGL:** Search, YouTube ads and Network have revenue but no standalone EBIT. Google Cloud includes Workspace. Hedging is separately reconciled. Depreciation-only and intangible amortization are retained separately; a comparable total D&A is not yet approved.
- **META:** Family of Apps and Reality Labs revenue and operating profit reconcile to consolidated totals. Retain Reality Labs losses in consolidated EBIT. Cash-flow SBC and allocated income-statement SBC can differ; do not silently interchange them.
- **PINS:** Single operating segment; do not infer advertising product-level EBIT. The September 2026 filing reports $982.091m ConvertibleDebtNoncurrent: absent standard LongTermDebt tags do not mean zero debt. Investments and lease presentation need classification.
- **RDDT:** Annual observations start in 2022; complete available fiscal-quarter cohorts start in 2023. Earlier S-1/comparative source history is not manufactured. Advertising plus other revenue reconciles; separate advertising EBIT is unavailable.
- **TTD:** Revenue is reported net of supplier advertising inventory and related costs. Gross advertising spend is not revenue. Keep it outside a mechanically pooled EV/revenue comparison. No product-level EBIT is inferred.
- **MSFT:** FY2027 Agents and Infra / Devices and Consumer mapping reconciles for September 2026. Prior Intelligent Cloud structure is retained separately, not spliced. Azure product revenue is available in the new disclosure; Azure-only EBIT is unavailable. DepreciationAmortizationAndOther is not pure D&A.
- **AMZN:** AWS revenue and EBIT reconcile with the other segments. Advertising revenue is a product category, not a standalone EBIT segment. PaymentsToAcquireProductiveAssets is the explicit cash-capex candidate; gross cash purchases differ from headline net capex and finance-lease investment. One depreciation fact is repeated at a coarser declared note precision; both values and precisions are retained.

## Remaining gates before trading multiples

1. Reconcile D&A scope to EBIT before comparable EBITDA, particularly Alphabet/Microsoft. No blanket substitution of a cash-flow line containing “other”.
2. Review debt and convertible debt, finance leases, operating leases, restricted cash, eligible investments and NCI for a consistent EV bridge. Raw balances are candidates, not approved additions/deductions; missing is not zero.
3. Review actual share classes, cover-page dates, buybacks and corporate actions. Retained balance-date share facts are not automatically the market-date denominator. Weighted-average EPS shares are never substituted.
4. Set a market snapshot date and permitted closing-price source. No prices, price rights, market caps, EV multiples, selected peer median or exit defaults are supplied here.
5. Review growth/maturity fit, outliers, segment allocation differences and historical revisions before choosing which peers can influence a terminal multiple.

## Files and reproduction

- `data/trading-comparables/sources/`: frozen Company Facts, submissions, filing XML and discovery responses.
- `data/trading-comparables/prepared/<ticker>.json`: consolidated annual/quarter/TTM fields, balance/claim candidates, source evidence and gaps.
- `data/trading-comparables/business-review/<ticker>.json`: explicit dimensional mappings and reconciliation receipts.
- `scripts/comparables/`: additive capture, preparation and business review. Existing `src/`, approved DCF inputs, frontend and production assets are untouched.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/comparables/prepare.py --as-of 2026-11-11
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/comparables/review_businesses.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/comparables -v
```

For a later snapshot, use `capture_sources.py --output <new-empty-directory>` with identifying `SEC_USER_AGENT`, review the new sources/cutoff and deliberately promote them as a new snapshot together with outputs. Existing freezes cannot be overwritten by the capture command. `prepare.py --refresh` retrieves only missing filing evidence; it does not silently replace Company Facts. No new cloud service or paid provider is required for these SEC financials.
