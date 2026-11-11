# Apple and Meta comparables extension

Implemented November 11, 2026 in the existing detachable Trading Comparables section 6. All three targets (Alphabet, Apple, Meta) use the same mount, single disconnect flag, scoped CSS, lazy JS/CSS, abort/error boundary and read-only financial projection. No additional host/DCF integration or backend is introduced.

## Apple peer map

| Peer | Role | Boundary |
|---|---|---|
| Dell | Mac / Client Solutions operating reference | Not a handset peer; infrastructure and AI servers also affect Dell consolidated financials. |
| HP | Mac / Personal Systems operating reference | Broader PCs/computing; consolidated HP also includes Printing. |
| Microsoft | Enterprise ecosystem context | Microsoft 365 cloud is not identical to Apple's consumer Services. |
| Alphabet | Platform ecosystem context | Subscriptions/platforms/devices is a broader category, not pure subscriptions. |
| Amazon | Subscription ecosystem context | Prime and other subscription services; no standalone subscription EBIT. |
| Netflix | Consumer subscription reference | Total-company revenue includes ads; content investment is not reflected in PP&E cash capex alone. |

Direct comparisons: Mac versus Dell Client Solutions and HP Personal Systems; Services versus Google ecosystem, Microsoft 365 cloud, Amazon subscriptions and Netflix. Product revenue and YoY growth include iPhone, Mac, iPad, Wearables/Home/Accessories and Services. The product breakdown reconciles to Apple total revenue using the original approved `revenue-mix-expanded/AAPL.json` as a read-only source. Q4 remains annual less nine months, with the original source/revision basis and operand evidence retained. No Mac/iPhone/Services operating profit is invented.

Apple's latest quarter ends 2026-09-26; Dell/HP's latest available quarters end 2026-07-31. Dates are visible on every comparison card and consolidated TTM row. Each issuer is compared against its own prior fiscal quarter (Dell prior ends 2025-08-01). These are not presented as a common calendar quarter. Hardware segment profit is a management measure; Dell/HP corporate/reconciling differences remain outside the segment rather than disappearing from consolidated GAAP EBIT. iPhone has no approved separately traded US handset peer in this set; Dell/HP are specifically Mac references. Samsung is not forced into the US-GAAP preparation contract.

## Meta peer map

| Peer | Role | Boundary |
|---|---|---|
| Alphabet | Primary advertising reference | Use disclosed advertising sum, not consolidated Alphabet revenue as pure ads. |
| Snap | Social advertising peer | Disclosed ad revenue excludes subscriptions/other revenue; negative TTM EBIT remains negative. |
| Pinterest | Secondary advertising peer | Explicit total-company revenue proxy; no ad-only EBIT. |
| Reddit | Secondary advertising peer | Ad revenue excludes other revenue; scale/growth/maturity differ. |
| The Trade Desk | Advertising technology reference | Net platform revenue differs from gross advertiser spend; no pooled revenue-multiple assumption. |
| Amazon | Commerce advertising benchmark | Consolidated retail/cloud earnings differ; no ad-only EBIT or market value. |

Direct comparisons: Meta advertising versus Google advertising, Snap advertising, Reddit advertising and the labelled Pinterest proxy. Family of Apps versus Google Services compares reported management profit units, not pure ad margins. Family of Apps + Reality Labs exactly reconcile to consolidated Meta revenue and EBIT. Reality Labs losses remain in consolidated EBIT. No comparable-company median or exit multiple is selected automatically.

## Data and source evidence

Additional official SEC Company Facts/submissions/XML sources are frozen independently for AAPL, DELL, HPQ, NFLX and SNAP under `data/trading-comparables/`. Exact standard concepts/dimension mappings are in `review_businesses.py`; the new sources have 122 selected annual/YTD/balance filing matches and 16 available business reconciliations, with zero mismatches. Across the full 12-issuer peer preparation this is 304 selected matches and 48 business reconciliations, not complete all-history certification.

`export_targets.py` consumes prepared data and existing Apple reporting; it never changes original acquisition/normalization, DCF inputs, calculations or the shared reporting files. It stores separate `AAPL.json` / `META.json` feature packages. The original Alphabet feature package and financial observations remain byte-preserved. Public exports retain prior/current period dates, source operands/context IDs, date/revision basis and Apple's shared-source SHA256. Latest annual alone can form TTM (Apple); other issuers use annual + current YTD - same-filing prior YTD. Reporting dates are never invented to force alignment.

Only known target-specific peer sets pass the client contract. The presentation is data-driven inside the existing container; incorrect issuer bindings, malformed growth and stale responses are rejected. All market fields remain null. D&A, EV claims, market-date shares, allowed prices and terminal assumptions remain open review gates.

## Reproduce

```sh
# Offline, using retained evidence; add --refresh only for missing filing evidence.
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/comparables/prepare.py --as-of 2026-11-11
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/comparables/review_businesses.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/comparables/export_targets.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/comparables -v
```

For a future source/cutoff change, retain the old freeze and review mappings, fiscal calendars, projection schema, target peers and missing values before publishing. No original universe review or additional DCF acceptance is resumed here.

## Verification

527 frontend tests (including 15 feature tests) and 26 Python preparation/export tests pass; the production build retains a separate feature chunk and styles. Tests cover target-specific peer sets, Apple calendar/quarter derivations, same-filing growth, proxies, preserved negative earnings, private-path exclusion, source/cross-period reproduction, issuer switching and the common disable flag. Actual desktop/390px checks cover Apple and Meta. Toggling the common flag off removes each section/link while the existing DCF stays available, then reconnects without any data migration. Original 15 DCF assets, 396 Python source files and 128 parity/extra fixtures verify unchanged.

Existing local default DCF preservation observations: Apple Base $2.58tn EV / $175.46 FCFF per share; Meta Base $944.60bn EV / $374.70 FCFF per share. These are unchanged model-snapshot outputs, not updated current market valuations. Publication is recorded in a separate release receipt.

## Publication

Published and live-verified November 11, 2026 with source implementation `ec054e7` and portfolio `78a31e8`. Both public data files match the release bytes and the live entry loads the target-specific module. Apple hardware/services, Meta ad revenue/segment reconciliation and unchanged default DCF outputs were checked on production. [Release receipt](trading-comparables-apple-meta-release.json).
