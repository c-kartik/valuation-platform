# Local integrated investor workspace

This preserves the approved forward/equity foundation record. The subsequent
[scenario integration](integrated-investor-scenarios.md) supersedes scenario-pending
statements below: complete Bear/Base/Bull now uses the real engine locally.
Reverse/sensitivity integration remains pending. Startup/reference routes and
historical/economic qualifications remain unchanged.

## Scope and entry

The approved design now has a separate **local, real-engine** entry at
<http://127.0.0.1:5173/workspace/>. Forward FCFF/DCF and optional manual equity/share
calculations use the existing Python API. Reverse DCF, scenarios and sensitivity
say **Not connected yet**, have disabled actions and show no fixture analysis.
The existing calculator remains at <http://127.0.0.1:5173/>; the separate
[illustrative prototype](investor-experience-prototype.md) remains at
<http://127.0.0.1:5174/prototype/>. Inputs/results do not transfer between entries.

Starting state was clean `main` at `f35d9d4976a3e4bdc6d8f4cdc1ab78b4d10af2d2`,
eight ahead of local `origin/main`. This October 28, 2026 checkpoint adds no Python,
financial formula, API/schema, historical/source approval, template, deployment or
portfolio changes. No cloud inspection, research, publication or push.
[Phase 1 remains paused](phase1-universe-pause-checkpoint.md).

Use Node 22.12+ and the existing dependencies. Start the compatible local API with
the [private-bundle instructions](local-case-api.md#scope-and-local-operation), then:

```bash
npm --prefix frontend run dev
# Integrated workspace: http://127.0.0.1:5173/workspace/
# Reference calculator: http://127.0.0.1:5173/

npm --prefix frontend run dev:prototype
# Separate illustrative reference: http://127.0.0.1:5174/prototype/
```

The existing Vite server supplies both integrated and reference entries, using
the unchanged loopback `/api` proxy to port 8000. The default production build now
emits both HTML entries and shared chunks; this is not a reviewed publication
artifact. Existing deployment/combined-preview allowlists are unchanged and must
be reviewed separately before any future publication.

## Input, result and request boundary

The bounded catalog supplies META, GOOGL and AAPL, their retained FY2025 revenue
anchors, fiscal dates, USD/base scale, source precision, filing links and limitations.
Company sessions begin with **37 unset forecast inputs and an unset bridge**.
No historical averages, previous temporary forecasts, shares or bridge selections
are defaults. The explicit synthetic demonstration retains its actual USD100
synthetic identity; it is not the prototype's fictional USD1bn company.

Only revenue is available as historical context through this catalog. Historical
growth/margins/expenses and multi-year history are marked unavailable; no new
figures are inferred. The fiscal-end analytical notice preserves later-filed
information and the absence of a verified information cutoff/filing-acceptance
timestamp. A richer historical-context consumer is a separate milestone.

The workspace reuses `model.ts`, `equity.ts`, `api.ts`, `execution.ts`, `Results.tsx`
and existing isolated-Decimal display helpers. Narrow shared extractions are
`caseExecution.ts`, `diagnostics.ts` and `EquityFields.tsx`, also consumed by the
reference calculator. It imports prototype **CSS only**, never fixture financial
outputs or prototype calculation state. Financial amounts come only from successful
`investor-case-v1` / `investor-case-v2` API runs; no browser FCFF/DCF/bridge engine.

Uniform percentage entry, independent annual values, blocking replacement
proposals with confirmation, and explicit one-time terminal copying preserve the
existing exact textual conversion. All five terminal ratios remain independent.
Draft creation generates anonymous preparation metadata; optional notes are not
evidence, identity verification or financial approval. Submitted traces retain the
metadata/notes sent with that run even if the current notes are later edited.

Each company has a separate in-memory Base session. Operating edits stale EV and
equity; bridge edits stale equity only. Notes, navigation and price edits do not
change financial dependencies. Empty, incomplete, calculating, current, stale and
failed states are explicit. Old figures remain qualified and are excluded from
current overview headlines. Reload clears all sessions; there is no persistence.

EV and equity share one synchronous submission gate **per mounted client**.
Explicit retry, abort/revision guards, company binding and owner-checked cleanup
discard obsolete results and prevent accidental concurrent submissions. No queued
or automatic calculation on typing/navigation, new endpoint or altered API budget.
Browser cancellation does not guarantee immediate worker termination. The separate
reference entry is a separate mounted client, not a deployment-wide lock.

Manual equity uses the existing signed server reconciliation, dated share basis,
coverage/class/award declarations and overlap checks. Missing declarations block
equity while retaining current EV. Omitted awards/claims may remain unbounded;
the result is not fully diluted fair value or complete claims certification.
Negative EV, FCFF and share results are preserved. Display-only price comparisons
require a positive finite price, current share result and exact selected fiscal-end
date (including AAPL's September date); no current quote is fetched or implied.

## Verification — October 28, 2026

- **146 distinct frontend tests passed**: the 144-test full frontend run followed
  by 18 affected presentation/workspace checks after two additional tests. Includes
  legacy compatibility, catalog/company binding, exact serialization, missing
  inputs, annual replacement/terminal independence, metadata, result rendering,
  stale dependencies, late replies, shared lock/cancellation/cleanup, explicit
  service/catalog retry and isolated Decimal price-display checks.
- **101 focused Python tests passed** using the documented `PYTHONPATH=src`
  virtual-environment invocation: valuation investor-equity, case/equity intake,
  bridge, summary, API cases/catalog/public boundary and preparation preservation.
  No full historical suite or corpus run.
- TypeScript/default multi-entry production build and separate prototype build
  passed. The fixture-only prototype retains its existing large-chunk warning.
- Actual Chrome desktop **1440×1000** and **390×844** covered unset company entry,
  validation/focus, confirmed terminal copy/annual replacement, live EV/equity,
  operating versus bridge edits, date-restricted price display, company switching,
  charts and unavailable-API recovery. Dialogs return focus. No narrow page overflow
  was observed. This is resized desktop testing, not mobile virtual-keyboard or
  full accessibility certification. Representative screenshots are outside the repo.
- **Eight complete browser-captured API JSON responses equaled equivalent CLI
  runs**: EV and equity for each of the three retained anchors, plus negative-FCFF
  EV/equity for AAPL. This checks interface compatibility, not independent economics.
  A separate `fractions.Fraction` calculation passed **572 numerical comparisons**
  covering annual/terminal operands, loss taxes, discounting, EV, signed components,
  equity and shares. Absolute tolerances: `1e-30` for amounts/components and `1e-40`
  USD/share. Units, company and dates were checked; no float financial arithmetic.

These temporary software choices were deliberately arbitrary: annual growth 10%,
margin 20%, tax 25%, D&A 5%, investment 10%, full-revenue WC cash requirement 2%;
WACC 25%, growth 5%; terminal 20/25/5/10/2% explicitly copied once. The negative
test changed annual margins to −5% while retaining terminal margin 20%. Bridge:
USD100m assets, USD40m financing, USD10m other claims and 20m synthetic test common
shares, dated to each anchor, with existing awards explicitly omitted. These are
**not researched company forecasts, actual share/claim selections or investment
valuations**. Temporary case/response files were removed; no actual case or output
was added to the repository, and browser trial sessions were cleared for review.

The pre-existing API PID had a missing temporary runtime manifest: health/catalog
worked but calculation failed safely. Only that API was stopped; a fresh verified
84-file read-only bundle was built offline from unchanged sources and the same
bounded loopback command restarted. Entries survived both the initial failure and
a retry while the API was stopped; recovery required an explicit retry. This was
a local runtime-artifact problem, not a formula or API-contract defect. Frontend
and prototype servers were reused.

## Review and next boundary

Review this forward/equity integration before connecting another workflow. The
recommended next bounded integration is editable Bear/Base/Bull through the
existing strict scenario engine, separately scoping its API adapter, shared bridge,
request budget/errors and comparison state. No scenario economics, sensitivity
ranges or reverse intervals are approved by this checkpoint.

Hosted services, old preview access/deadlines and migration plans were not inspected
or changed. Their prior records remain historical; this checkpoint neither verifies
withdrawal nor extends access. To stop local review, identify the current listeners
on ports 5173/5174/8000 and inspect their commands before sending SIGTERM to those
specific processes. Keep the API's immutable `/tmp` bundle while it is running;
never remove a live bundle. No shutdown affects hosted services.
