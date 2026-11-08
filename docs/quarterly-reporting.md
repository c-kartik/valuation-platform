# Financial-statement overview — historical trends and cash-flow bridge

Implemented November 9, 2026 for GOOGL, then AAPL and META. This is the user's
replacement financial-statements-only direction after shelving market-price
features. It does not resume the original market-data roadmap or wider universe.
Production deployed November 9, 2026. [Release receipt](quarterly-reporting-release.json) records the source/build, Netlify release and live verification. [GitHub checkpoint #9](https://github.com/c-kartik/valuation-platform/issues/9).

## Architecture and separation

The additive `reporting.quarterly` consumer uses the existing typed
`sec.company_facts.fetch_company_facts`, `SECClient`, SEC submissions and
filing-XBRL parsers. No existing Python source is modified. None of its new
values are passed to DCF normalization, analyst packages, assumptions or the
JavaScript valuation engine. The existing 15 browser datasets remain unchanged.

`QuarterlyOverview` is above `valuation-main` in the workspace. Existing company
search selects the issuer; reporting controls affect only its charts/readouts.
A separate static `/research-data/<ticker>.json` request has loading, failure
and retry states; stale responses cannot bind to another issuer. A reporting
failure leaves the DCF available. There is no live SEC request from the browser,
market-price input, new subscription, or new server infrastructure.

## Scope and formula contract

- 20 consecutive fiscal quarters per issuer, prepared as of November 9, 2026.
- GOOGL/META: FY2021 Q4–FY2026 Q3, through September 30, 2026.
- AAPL: FY2022 Q1–FY2026 Q4, through September 26, 2026; fiscal dates and the
  53-week-year calendar are preserved rather than assigned calendar quarters.
- Trend groups: cash generation (revenue, CFO, cash PP&E purchases, FCF),
  revenue/profit (revenue, operating income, net income), and margins.
- FCF = reported CFO − cash purchases of property and equipment. It is not
  historical FCFF, standardized FCFE, total investment or parent-common cash.
- Operating margin = operating income / revenue; FCF margin = FCF / revenue.
  A zero denominator is unavailable, not a fabricated zero ratio.
- Bridge: net income + SBC + other operating reconciliation = CFO; CFO − cash
  capex = FCF. CFO is a subtotal, not an additional inflow.
- Other operating reconciliation = CFO − net income − SBC, a disclosed aggregate
  of all remaining noncash adjustments and operating asset/liability movements.
  It is not an independently sourced detailed working-capital decomposition.
  SBC add-back does not declare compensation economically free.

## Selection, revisions and gaps

Policy `quarterly-reported-usd-v1` accepts whole-entity standard US-GAAP USD
observations only. Periods come from actual start/end dates, not `fy`/`fp`/frame
labels alone. Annual durations and each quarter's duration are checked. The
first eligible disclosure is selected within each fiscal cohort; closed years
are anchored to the earliest eligible annual revenue filing, and annual operands
for every metric must come from that same accession. Explicit standard-tag
priority resolves supported aliases; conflicting same-priority observations fail.

Q1 uses the first-quarter amount. Q2/Q3 use successive fiscal YTD differences;
Q4 uses full year less nine months. Consequently a derived quarter can differ
from a separately printed standalone amount when presentations/revisions differ.
Every operand keeps its concept, value, units (package USD), period, filing date
and accession link. Arithmetic remains exact integer USD; display uses billions
and explicit decimal rounding. No reported zero is inferred from missing data.

This is a disclosed first-disclosure/cohort descriptive series, **not a
latest-restated statement or historical as-known research dataset**. Frozen
snapshots reproduce this release. A future revision-policy change needs a new
policy/version and affected issuer records. Custom-tag/unsupported calendars,
missing required metrics, incomplete latest periods and discontinuous history
stop package publication; they do not silently fall back to older history.

## Validation and its limits

- 60 displayed quarters, each with exact cash-flow identities.
- 42 annual metric tie-outs per issuer (seven prepared annual cohorts × six
  metrics), including preparatory history beyond the displayed 20 quarters.
  Q4 is derived, so these checks test arithmetic consistency rather than being
  independent certification of quarterly economic classification.
- Independent filing-XBRL comparison: 18 operand checks per issuer, 54 total,
  across eight distinct filings. Scope is the latest displayed quarter's YTD
  operands and latest annual totals, not manual re-extraction of all 60 quarters.
- 135 same-filing discrete-quarter comparisons are retained (45 per issuer).
  Twelve differences of $1 million occur: one Alphabet and eleven Meta; Apple
  has none. The display retains its explicit YTD-difference basis and exposes
  reported/derived operands for affected quarters rather than claiming equality.
- Source evidence and receipts are retained under `data/quarterly-reporting/`.
  Original sources can be re-parsed offline with the existing structural parser.
- Tests cover Apple fiscal dates, cutoff dates, gaps/missing inputs, conflicting
  facts, negative FCF, deterministic reproduction, issuer binding, UI selection,
  margins and reporting-failure isolation. Existing engine parity remains separate.

## Reproduction and refresh

Use the existing Python environment from the repository root; Node 22.12+ is
required for frontend builds/tests. No existing refresh command changes.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/prepare_quarterly_reporting.py --ticker GOOGL --as-of 2026-11-09
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/validate_quarterly_filings.py --ticker GOOGL
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/reporting -v
```

Repeat for AAPL/META. For a new snapshot, set `SEC_USER_AGENT` to an identifying
contact, set the actual review cutoff with `--as-of`, and add `--refresh` to both
preparation and independent-validation commands. Filing evidence is retained by
URL hash; Company Facts snapshots and public packages are versioned in Git.
Before refresh, commit the accepted source snapshot/package/receipt together;
do not discard earlier Git revisions. Validate changed operands and update issuer
records before committing/building/publishing new browser assets. A refreshed
Company Facts file alone is not a reviewed release. No automatic production
refresh or broader issuer acceptance is implied.

## Remaining boundaries

Detailed D&A/tax/investment/working-capital attribution, quarterly FCFF/FCFE,
quarterly forecast adoption, historical prices and exports of this new history
are not part of this consumer. Existing DCF Excel downloads retain their scope.
Other tickers require explicit preparation/financial sufficiency and validation;
three successful pilot packages do not establish whole-universe readiness.

## Mockup alignment — November 9, 2026

Review of the original `alphabet-trends-cashflow.html` mockup found that the
first live implementation flattened its separate panels, used point-heavy
straight segments, replaced shared hover readouts with native titles, and omitted
legend toggles. The reporting UI now restores the company introduction and
separate historical-trends/cash-bridge panels, with shape-preserving cubic curves,
one shared cursor-following tooltip, quarter crosshair and active-series markers.
Legend controls show/hide lines while retaining at least one visible series.

Hover previews the nearest real observation in the tooltip and metric cards;
leaving restores the selected quarter. Clicking/tapping selects the quarter for
the dropdown and cash bridge. Keyboard arrows/Home/End select quarters; Escape
hides the tooltip. Touch retains vertical page scrolling. Curves pass through
observations, flatten at turning points and do not create overshoot or values for
intermediate dates. Null observations remain gaps. No financial definition,
source package, preparation policy, DCF code or accepted input changed.

Validation: 474 frontend tests pass, including pointer-preview/restoration,
keyboard selection, legend controls and curve bounds/gaps. Browser checks cover
all three issuers, shared tooltip movement and a 390px phone viewport without
horizontal overflow. Physical iPhone/Safari testing remains outside these checks.
