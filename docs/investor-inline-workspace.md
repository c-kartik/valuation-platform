# Direct-entry investor workspace — local review

October 29–30, 2026 (Dubai). Started on clean `main` at
`3019e2bae5ef3d9c801c708a4fdd170021bf9778`, two commits ahead of local
`origin/main`. This supersedes the ordinary focused-editor/exclusive-exploration
interaction in the [canvas checkpoint](investor-valuation-canvas.md), preserving
that record's historical scope. Local implementation only; Phase 1 remains
[paused](phase1-universe-pause-checkpoint.md).

## Interaction and state

Eight ordinary DCF percentage inputs are directly editable beside the chart:
growth, operating margin, operating tax, D&A/revenue, investment/revenue,
full-revenue WC cash requirement, WACC and terminal growth. Type, Tab, then
Calculate. No Apply/modal or valuation request intervenes. Raw decimal strings,
including intermediate blanks, minus signs and decimal points, survive typing;
syntax is checked on blur/calculation. Economic edits immediately stale affected
results, retaining their previous values with explicit labels. Notes remain
nonfinancial and returned provenance still describes the submitted run.

Annual paths expand inline. A varying path is labeled as varying; neither its
first year nor an average is presented as a constant. A typed replacement remains
unapplied and blocks calculation until explicitly used for that driver’s five
years or discarded. Independent terminal ratios expand nearby; copying year-five
ratios is an explicit one-time action. The optional detailed cash/claims/share
sheet remains separate and does not validate unrelated unfinished forecast fields.
Required-input links reveal and focus the actual inline input, including collapsed
annual/terminal detail. Collapsed detail mounts on demand; working values remain
in the case state rather than in the disclosure.

Stable anchors `#dcf`, `#scenario-comparison`, `#sensitivity` and
`#sources-methodology` navigate four sections on one page. All analyses remain
mounted; anchor navigation causes no calculation or state reset. Dividers,
headings, keyboard focus, sticky-context scroll offsets and reduced-motion rules
retain the existing navy/gold/serif design. Composition belongs within DCF, below
the forecast chart, with detailed reconciliation expandable. Existing signed,
zero-EV and over-100% terminal-contribution behavior is retained.

The scenario table contains direct inputs, separated case headings/status lines
and expandable cash-flow, terminal and annual detail. Both editing surfaces call
the same existing draft/revision updater, now with an optional target case label.
Untouched Bear/Bull values follow Base; explicit overrides remain fixed even when
numerically equal to Base. Resetting overrides remains explicit. No scenario
economics, probabilities or financial defaults are generated.

## Charts and sensitivity

Scenario revenue and FCFF now use two aligned line charts with independent,
clearly named USD-billion scales, shared fiscal positions, selected year/readout
and data table. Color, dash and marker shape distinguish cases. Lines join the
five returned forecast points only; the single retained revenue anchor is shown
as reported history, and historical FCFF stays unavailable. Keyboard arrows,
Home/End, pointer and tap-style selection synchronize both metrics. Stale charts
retain previous returned values with a clear notice. The single-case chart keeps
its bars and metric controls.

`chartAxis.ts` supplies display-only Decimal domains and ticks: outward rounding,
zero included, clean steps 1/2/2.5/5/10 × powers of ten, common scale per compared
metric, and label precision derived from the step. Extremely small/large scales
use one explicit decimal tick multiplier rather than clipped digits, repeated
scientific tick labels or false zeros. Coordinates alone become bounded JS
numbers. Finite/length/exponent guards and isolated Decimal configuration protect
presentation; no input, result, export or financial operand is rounded or changed.

Sensitivity controls and preview sit above a full-width matrix; inspection sits
directly below. Blank custom settings allow a calculation-free 3×3 preview from
entered WACC/g. Existing offsets retain their diagnostic meaning, not researched
company ranges. Editing stores the complete proposed settings; custom axes survive
source-case changes/recalculation and case/company switching. Explicit recentering
replaces them. Calculation, invalid-pair/null handling, 11×11 capacity, cancellation,
retry, stale responses, optional equity eligibility and confirmed pair application
retain their existing contracts. A pair not present on custom axes has no current-
case outline. No fake matrix appears before calculation.

## Verification and remaining boundaries

Verification results and actual local browser checks are recorded below at this
checkpoint; prior financial-arithmetic campaigns remain attributed to their own
records and are not claimed as rerun. No Python engine, API schema, transport,
execution ceiling, historical derivation or source binding changed in this task.

**Preload methodology remains deferred.** No company defaults, historical
calibration, GOOG estimates, automatic forecasts, scenario-generation rules or
new WACC/terminal policy are installed. Historical references remain context only;
FY2025 anchors and later-filed-information timing remain unchanged. Current market
access/display rights and comparable date/share/financial perimeter remain
unresolved. This is software acceptance, not financial-input approval or
investment readiness. Export contents/lifecycle have regression coverage; actual
browser file arrival was not reverified and remains an outstanding observation
limit from the earlier checkpoint.

No push, deployment, cloud/IAM/billing, portfolio, infrastructure, frozen-history,
approval or company-template changes. Temporary software inputs/results are
cleared from the task's dedicated test tab before handoff; no actual-company case
or valuation output is saved in the repository.

### Checks completed

- Full frontend regression: **202 tests in 19 files passed**, using
  `npm --prefix frontend test -- --maxWorkers=1`. Default concurrent runs exposed
  test timeouts, including an unchanged prototype journey; bounded test concurrency
  passed without changing test timeouts or application execution budgets.
- After the final measured sticky-offset fix, **18 affected tests in three files
  passed** (`Workspace.test.tsx`, `chartAxis.test.ts`, `ScenarioCharts.test.tsx`,
  with `--maxWorkers=1`). Both `npm --prefix frontend run build` and
  `npm --prefix frontend run build:prototype` passed. The existing prototype chunk
  advisory above 500 KiB remains; no dependencies or build infrastructure changed.
- Coverage includes direct entry/DOM order, raw precision and intermediate states,
  no typing/navigation requests, annual replacement safeguards, terminal independence,
  two-surface inheritance and explicit overrides, stable anchors, exact exports,
  synchronized line readouts/data, axis extremes/Decimal isolation, signed composition,
  custom-grid state and existing cancellation/late-response protection.
- Actual Chrome review at verified **1440×900** and **390×844 CSS pixels** covered
  blank and complete DCF, annual-path edits across sections/cases/companies,
  intentional constant replacement, keyboard Tab, directly edited scenario columns,
  synchronized keyboard/tap chart readouts, negative FCFF, sensitivity preview/
  calculation/inspection/confirmed application and custom-axis retention. An actual
  invalid-tax response focused the inline tax field. Stale results stayed visible;
  a real local API outage preserved inputs and explicit retry restored the same EV.
- Mobile root scroll width was **373px within a 390px viewport**. Financial tables
  scroll within their containers. A demonstrated wrapped-control/readout overlap was
  fixed by measuring the sticky controls: observed bottom 168.21px, readout top
  176.997px after the fix. Desktop/narrow screenshots were inspected. Existing 90%
  browser zoom was accounted for in viewport/clip coordinates; no browser setting
  or security restriction was changed.
- An explicit **11×11** run of the existing $100 synthetic fixture verified all
  121 cells, keyboard/click inspection of the final pair and a readable minimum
  column width for larger grids. At 390px, the matrix scrolled inside its 345px
  container (1,207px content); the page stayed 373px wide. Seven existing sensitivity
  regression tests were rerun after that final table-layout adjustment.

Software inputs were deliberately arbitrary: annual growth 10%, margin 20%, tax
25%, expense D&A/revenue 5%, investment/revenue 10%, full-revenue WC cash requirement
2%, WACC 25%, terminal growth 5%, and explicit terminal ratios 20/25/5/10/2%.
GOOGL/AAPL retained anchors produced rounded software-check EVs $200.90bn/$207.54bn.
Bear growth 8%/margin −10% and Bull growth 12%/margin 22% exercised signed paths;
a later layout-only AAPL check kept 10% growth across cases and changed Bear margin
to −10%. These are not researched forecasts, preloads, approved scenarios or
investment cases. The initial 9% year-two growth edit, 26% WACC change and custom
23/25/27% WACC × 4.5/5/5.5% g grid were temporary interaction tests. No trial values
were inserted into a company template. Values/results were cleared before handoff.

The Python engine/API did not change, so no broad Python or financial-arithmetic
campaign was rerun. Prior CLI/API equivalence and independent checks remain
attributed to the earlier records. This task exercised the unchanged local API
through the browser for single-case, scenario and sensitivity calculations.

Final preservation inspection found every tracked Python/source-data/example/
Python-test/script byte unchanged, including formulas, solver and 15 resource pins.
All nine templates remain byte-identical: 15 embedded case bodies × 37 unset
numerical inputs = 555 nulls, with unresolved bridge/share selections unchanged.
The runtime's 95 files match reviewed source, and the frontend proxy catalog
matches the local API exactly. All 543 local links and 66 anchors in changed
documentation resolved; whitespace checks passed. Portfolio remained clean at
`a115327325754cb741b696fa115f38a30e63c866`.

### Local handoff

Review: <http://127.0.0.1:5175/workspace/> → **local** Python API 8002, no cloud
fallback. The existing immutable bundle `/tmp/valuation-canvas-20261029/runtime`
was verified and reused (95 files plus manifest). Only the verified review API
was restarted for the outage check: prior PID 6910, current PID **15368**. Vite
listener **99992**, npm launcher/process group **99976**, and unrelated servers
remain running. Check identity with `ps`/`lsof` before stopping just these servers:
`kill -TERM 15368`; `kill -TERM -- -99976`. PIDs are checkpoint observations.
Screenshots, check logs and process metadata remain outside the repository in
`/tmp/valuation-inline-20261029/`; task-only debugging copies were removed.
