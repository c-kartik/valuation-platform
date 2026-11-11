## Apple and Meta extension — November 11, 2026

The user extends the same detachable section 6 to AAPL and META. Target-specific peer sets and direct business comparisons are implemented through the same container/config, with separate public packages. This supersedes the historical Alphabet-only limitation below for these two targets only. Dates, proxies, losses and missing operating-profit disclosures remain explicit. [Peer methodology, data and validation](trading-comparables-apple-meta.md). Original DCF contracts/defaults remain untouched.

# Detachable trading comparables — Alphabet

Implemented November 11, 2026 as section **06 / Relative valuation**, following DCF section 05 inside the existing **Valuation** chapter. Alphabet-only target acceptance; Apple/Meta target-specific comparables are not silently inferred from Alphabet's peers. The original Python source, JS DCF engine, approved datasets, assumptions and workbook exporter are unchanged.

## One disconnect point

Set `tradingComparables.enabled` to `false` in `frontend/src/features/trading-comparables/config.ts`, rebuild and publish. This removes the section, its lazy module/style loading, static-data request and Valuation-band link; the band returns to section 05. Turning it back on restores the same feature. No financial packages need deletion or migration. This is an isolated feature container, not a Docker service or hosted backend. Public static files are not access-controlled by this switch; disconnecting UI does not make a previously public data URL private.

All feature implementation lives in `frontend/src/features/trading-comparables/` (configuration, mount boundary, types, client, UI, styles and tests). Its sole dataset is `frontend/public/features/trading-comparables/GOOGL.json`. The two host connections are the mount in `Workspace.tsx` and optional navigation in `ChapterBand.tsx`. The mount accepts only a ticker, never DCF state or calculation callbacks. Code/styles are lazy-loaded separately; every style is scoped to `.tc-container`. Disabled and unsupported targets render nothing. Fetch cancellation, stale-response checks, retry and a React error boundary contain failures within section 6.

## Included interface

- Direct Google Cloud / AWS / Azure revenue and disclosed operating-profit comparisons.
- Direct Google advertising / Meta advertising / Reddit advertising / Pinterest company-revenue proxy.
- Same-quarter YoY growth from the prior/current periods in the same filing, including comparative/recast presentation. Google advertising growth uses summed component revenue.
- Separate Search, YouTube ads and Network revenue/growth table.
- Consolidated peer financials, selected-company CFO/capex/cash-FCF/SBC, TTM source operands and links.
- Reported services profit units and segment reconciliation, subscription/other exposures, and candid pending valuation/claim fields.

GCP-only revenue/profit remains unavailable; Google Cloud includes Workspace and other services. Azure-only operating profit is not inferred. Pinterest remains a clearly labelled total-company proxy. Segment allocations, corporate costs, hedging, net/gross revenue and Microsoft reporting changes remain explicit. No estimate is passed into DCF. No closing prices, market caps, EVs, trading multiples, EBITDA assumptions or terminal defaults are invented. Market-price use rights and financial-method review remain open; this is a complete rendering of the approved available-data scope, not completed trading valuation methodology.

## Data and reproduction

The feature reads a projection of the existing prepared SEC financials; it does not query SEC from the browser or change existing acquisition/normalization. `scripts/comparables/export_browser.py` reuses retained submissions, XML and explicit dimensional mappings from the isolated peer preparation. It extracts same-filing July–September 2025/2026 segment revenue, stores exact values, contexts, sources and growth arithmetic, and writes only the new feature's public JSON. No provider keys, private local paths, remote market requests or new services are present. Dataset cutoff is 2026-11-11 and the common reported quarter ends 2026-09-30; this is separate from the unchanged DCF analytical anchor.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/comparables/export_browser.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/comparables -v
cd frontend
npm test -- --maxWorkers=2
npm run build:browser
```

Use the repository's Node 22 runtime. New snapshots need reviewed sources/mappings and compatible data/schema updates; this does not promise automatic handling of all future reporting changes. Public feature data is independently versioned from the DCF manifest.

## Verification

- 522 frontend tests pass, including ten new isolation/UI/data-boundary tests; 19 Python financial/preparation/export tests pass.
- Production browser build succeeds with separate TradingComparables JS/CSS chunks.
- Export reproduces the committed JSON exactly offline, including weighted Google ad aggregation and same-filing comparative revenue.
- Actual desktop and 390px checks cover direct comparisons, tabs, balances and readable responsive layout. Tables scroll within the feature; there is no document-level horizontal overflow.
- Actual disconnect/reconnect check removes/restores the section and link while the DCF remains available at its existing Alphabet Base calculation ($1.42tn EV / $125.91 FCFF value per share under the unchanged default snapshot). This is preservation evidence, not an updated market valuation.
- Frontend tests reject unsupported issuers, incorrect growth, accidental market/default values and late loads after unmount. No production website change is implied by tests; publication is recorded separately.

## Publication

Published and live-verified on November 11, 2026 through the existing portfolio repository (`7a9a085`), using source implementation `d380d8a`. The live feature JSON matches the release bytes and the page loads the new entry. Section-6 navigation and the unchanged Alphabet default DCF were checked on production. See [release receipt](trading-comparables-release.json).
