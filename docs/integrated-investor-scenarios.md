# Local investor scenario integration

## Current scope

The [workspace](http://127.0.0.1:5173/workspace/) now calculates complete
Bear/Base/Bull sets through the existing scenario engine. Forward EV and optional
manual equity/share remain independently available for the selected case. Reverse
and sensitivity remain **Not connected yet**. This follows the approved
[forward/equity foundation](integrated-investor-workspace.md); the reference
calculator `/` and isolated fixture prototype at port 5174 remain available.
Startup commands are unchanged: compatible private-bundle API on loopback 8000,
`npm --prefix frontend run dev`, optionally `npm --prefix frontend run dev:prototype`.

Starting `d3c08117e32bf22d8a83f7b70b6ac47f5ab4e88f` was clean main, nine ahead of
local origin/main. Local implementation only: no cloud calls, publication, push,
research, portfolio change or new actual-company forecast/approval.
[Phase 1 remains paused](phase1-universe-pause-checkpoint.md).

## API and execution contract

`POST /api/v1/scenarios/validate` and `/api/v1/scenarios/run` accept complete
`analyst-scenario-set-v1` or **`investor-scenario-set-v1`** documents. The latter
has the same narrow envelope: `schema_version`, `scenario_set_name`, `scenarios`.
Each of exactly three entries supplies `label`, `analytical_date`,
`information_cutoff`, and a complete existing `investor-case-v1` or `investor-case-v2`
case, including anonymous preparation timestamp and optional notes. No invented
analyst identity, rationale, source review or coverage declaration. Missing cases
are not inherited, filled or executed as partial comparisons.

The existing [scenario reader/runner](phase2-scenario-workflow.md) owns strict
parsing, required values, dates and exact comparability: anchor/company, input
basis, conventions, fiscal labels, output scope and declared dates match. Equity
sets require the **entire identical bridge/share payload**, including provenance,
coverage, class/award policy, omissions and review metadata. No weakened equality
or financial checks. Cutoff is explicitly entered and shared; it starts unset.
It must be on/after fiscal end and is an unverified declaration, not the catalog's
verified information availability or the preparation timestamp.

Validation performs no historical load, forecast, DCF, bridge or child spawn.
Run revalidates the whole set, then executes its three existing A/B/C cases
sequentially inside **one bounded child**, under the same server execution gate
as single-case requests. No three browser requests, queue or partial result on
failure. Existing ceilings remain: 256 KiB body, 4096 JSON nodes, depth 24,
64 numeric digits/exponent limits, 2 MiB result, 35s total deadline and 30s child
CPU. Existing body/transport/cleanup limits, cross-site rejection, no-store and
bounded sanitized errors remain. Memory/concurrency limits were not increased.

Results use `investor-scenario-results-v1` for the new envelope, preserving full
submitted snapshots and all three complete existing case results, always ordered
Bear/Base/Bull. Legacy envelope/result and single-case API/JSON remain compatible.
The scenario CLI accepts the new envelope too; its summary displays anonymous
preparation/notes without inventing analyst rationale. Legacy summary/JSON behavior
is preserved. Packaging adds only `scenario_inputs.py`: **85 allowlisted files**,
no new historical resources or dependency. A fresh verified immutable local API
bundle was built and the identified API process restarted; Vite servers reused.

## Case ownership, editing and review

Each company owns Base plus explicitly created Bear/Bull. Creation clones current
Base input strings, terminal values and notes, generates a new preparation timestamp
and case name, and starts without a result. Later edits never propagate into
siblings. Replacement/removal is confirmed; Base cannot be removed. There are no
automatic Bear/Bull economics, probabilities, weighted values or exploratory cases.

One selected-case editor reuses exact percentage conversion, confirmed annual
replacement and independent terminal editing. The company/anchor, currency,
conventions, bridge/share inputs and comparison price stay shared. Bridge metadata
uses the fixed Base preparation context while each outer case keeps its own
identity/notes. A sibling's invalid forecast does not block an otherwise valid
individual equity run. All company inputs/templates remain unset by default.

One client gate covers forward, equity, scenario validation/run and retries.
Snapshots/revision guards discard late replies after edits, company changes or
removed cases. Cancellation/failure retains inputs, releases ownership safely and
requires explicit retry. Browser abort is not a guarantee of immediate worker stop;
server admission remains per API process, not a global quota.

| Edit/action | Individual results | Three-case comparison |
| --- | --- | --- |
| Operating input in one case | That case's EV/equity stale; siblings preserved | Stale; independent recalculation does not refresh the set |
| Shared bridge/share edit | All share results stale; valid EVs preserved | EV remains usable; earlier share values withheld until rerun |
| Shared cutoff or output-scope change | Financial results preserved | Requires explicit validation/run of the new comparison |
| Notes, navigation, price | Financial results preserved | Financial result preserved; trace keeps submitted notes |
| Replace/remove case | Sibling inputs/results preserved | Invalidated; missing case blocks execution |

Scenario cards distinguish completeness, individual status and set freshness.
The overview links to the current set. Driver differences are explicit relative
to Base; annual/terminal assumptions remain reviewable. Server comparisons show
EV reconciliation, qualified equity/share where current, terminal contribution
and common-scale revenue/FCFF paths with exact values in the trace. Amounts are
USD millions; share output USD/share. Signed values and unexpected ordering are
preserved with neutral explanations. Manual declarations do not establish complete
claims coverage, fully diluted fair value or bounds on total company value.

## Verification — October 28, 2026

- **159 frontend tests passed**, including scenario state/copy/removal, exact
  serialization/shared bridge metadata, independent results, stale dependencies,
  missing values, late replies, locking/cancellation, failure recovery, response
  shape and legacy regression. A pending equity-set cancellation cannot promote an
  older stale EV comparison to current. Production and isolated prototype builds passed;
  the existing prototype large-chunk warning remains.
- **122 focused Python tests passed**, including scenario/CLI, case/equity intake,
  bridge/summary, API/catalog/public boundary, process failure/deadline/recovery,
  response budgets and preparation preservation. No full historical suite/corpus.
  Two obsolete source pins were narrowly corrected for already-approved anonymous
  `case_inputs.py` and the single-case CLI to the starting HEAD. Original numerical
  engine pins remain; no financial code/guard was altered to pass preservation.
- Actual Chrome **1440×1000 and 390×844** covered Base calculation, explicit copies,
  edits/comparison/overview, stale states, scenario-qualified invalid-tax correction,
  shared bridge staleness, company switching, unavailable-API explicit recovery,
  confirmation/Escape/focus and missing-case recovery after removal. No horizontal
  page overflow observed. Resized desktop is not mobile virtual-keyboard or full
  accessibility acceptance. Screenshots remain outside the repository.
- **Six browser-captured sets exactly matched scenario CLI JSON**, and all **18
  embedded results matched individual CLI runs**. Local HTTP reruns also matched;
  largest response **205,108 bytes**, measured runs **0.431–0.515s**, within existing
  unchanged bounds on this local sample, not load/production certification.
- **1,233 independent rational comparisons** covered annual/terminal FCFF, loss
  taxes, discounting, EV and selected signed bridge/share reconciliations. Absolute
  tolerance `1e-30` USD/components and `1e-40` USD/share. Identical inputs produced
  identical financial results; changed Bear inputs preserved Base and terminal
  inputs; negative Bull FCFF had no immediate loss-tax benefit. No float financial
  arithmetic or duplicated engine used for these independent checks.

Software choices only: annual growth 10%, margin 20%, tax 25%, D&A 5%, investment
10%, full-revenue WC 2%; WACC 25%, g 5%; terminal 20/25/5/10/2%, explicitly copied
once. META Bear margin 30% and Bull −5% deliberately tested unexpected ordering and
negative flows; AAPL Bear growth 11% tested independent propagation. Other copied
cases stayed identical. Shared META bridge used USD100m assets, USD40m financing,
USD10m claims, 20m **synthetic test** common shares and explicitly omitted awards.
Declared shared cutoff February 5, 2026 was a test declaration only, not verified
information availability. Actual retained revenue anchors were used for all three
issuers; **none of these choices are researched forecasts or actual bridge/share
selections**. Temporary inputs/results were removed and browser trials cleared.

Formulas, historical/source approvals, nine unset templates and portfolio are
unchanged. No hosted service/access/deadline was inspected or modified. Review
before separately scoping sensitivity or reverse integration. Economic review,
historical-context gaps and unbounded omissions remain explicit. To stop local
review, inspect listener identities on 5173/5174/8000 before SIGTERM; do not delete
the immutable API bundle while it is running.
