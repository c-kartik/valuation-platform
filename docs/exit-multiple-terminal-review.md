# Exit-multiple terminal valuation — local acceptance

Subsequent UI status: the [result-first workspace](investor-result-first-workspace.md)
now calculates complete starting profiles automatically through the local API and
uses one on-demand editor. Earlier no-auto/inline-layout statements below are
historical; financial rules, preload estimates and calculation-free preparation
remain unchanged.

Subsequent status: the separately authorized [GOOGL proposed preload](googl-preload-methodology.md)
now supplies explicitly labeled estimates and Full Model. This record preserves
its earlier scope; it does not grant financial approval or change Phase 1’s pause.

October 30, 2026 (Dubai). Started on clean `main` at
`021796d220d7ee5d894e702d9d4ab5d3d2026156`, three commits ahead of local
`origin/main`. Extends the [direct-entry workspace](investor-inline-workspace.md)
without changing its same-page layout. Local implementation only; no deployment,
push, portfolio change, evidence acquisition or company forecast approval.
Phase 1 remains [paused](phase1-universe-pause-checkpoint.md).

## Financial boundary

Perpetual growth retains its five independent terminal operating ratios and
existing Gordon formula. The alternative `fiscal-end-year-five-ev-ebit-v1` uses
**final explicit year-five EBIT × a positive EV/EBIT multiple**, discounted by
`(1 + WACC)^5`. EV remains explicit-period FCFF PV plus terminal PV. The same
Stage A operating equations and shared annual discounting serve both methods.
No year-six EBIT, normalized earnings, SBC or service-lease add-back is introduced.
Exit requires positive year-five EBIT; zero/negative EBIT is unsupported. WACC
remains positive; growth below WACC applies only to Gordon. Negative FCFF/EV,
undefined zero-EV contribution and signed/over-100% contributions remain valid.
All financial arithmetic uses isolated Decimal precision 50, HALF_EVEN, without
intermediate quantization. Display rounding changes no stored input/result.

`OperatingAssumptions` separates the five annual paths/WACC from the legacy
Gordon `ValuationAssumptions`. Typed `PerpetualGrowthMethod` / `ExitMultipleMethod`
operands feed the shared execution. An exit result has a `terminal_basis` with
EBIT definition, fiscal-year label, period 5, exact EBIT, multiple and WACC. It
has no fabricated terminal-year revenue/FCFF. Stage C revalidates/recomputes
either exact result type before the unchanged qualified signed bridge.

## Versioned intake and local execution

Legacy analyst/investor v1/v2 requests and JSON retain their Gordon meaning.
New `analyst-case-v3` and `investor-case-v3` retain annual inputs and provenance,
require explicit `calculation_scope` (`ENTERPRISE_VALUE` or `EQUITY_PER_SHARE`),
and replace top-level `terminal_growth` / `terminal` with:

| Method | `terminal_valuation` operands |
| --- | --- |
| `perpetual_growth` | `method`, `terminal_growth`, five-ratio `terminal` object |
| `exit_multiple` | `method`, `exit_ev_ebit_multiple` |

`comparison_terminal_valuation` is explicitly the opposite method object or
`null`. Missing/invalid comparison economics produce `AWAITING_INPUTS`, without
blocking a valid selected method. Strict unknown fields, duplicate keys and
JSON-number rejection still apply; this is not a permissive alternate parser.
Validation-only constructs/validates models, without historical retrieval or
financial execution. Positive-EBIT feasibility checks use annual operand signs;
the engine also validates actual year-five EBIT.

The new result versions (`analyst-case-result-v3`, `investor-case-result-v3`)
include both individually valid terminal results, exact submitted input bindings,
Python-calculated Gordon implied year-five EV/EBIT and exit-minus-Gordon EV
difference. A nonpositive terminal value or EBIT makes the implied ratio
unavailable. Comparisons reuse the same annual forecast/WACC. Equity execution
requires the existing complete bridge; comparison does not invent a second bridge.

`investor-scenario-set-v3` requires comparable complete cases using one method;
multiple-only edits change value, leaving revenue/FCFF paths unchanged.
`investor-sensitivity-request-v3` explicitly supplies `wacc_values` and
`exit_ev_ebit_multiple_values`, up to 11 each. It returns exact WACC/multiple
cells, year-five EBIT and PV reconciliation, with no Gordon pair restriction or
unused terminal FCFF. Gordon retains its existing WACC × growth envelope.
The CLI readers accept these contracts through the existing scripts:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/run_analyst_case.py examples/valuation/synthetic-exit.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/run_analyst_case.py examples/valuation/synthetic-exit.json --run --format summary
```

JSON remains the default. `--output` still requires explicit execution, exclusive
creation and protected-path checks. Scenario/sensitivity scripts also support
method-aware JSON/summary output. API routes, validated anchor reuse, terminable
worker, single-execution gates and all resource ceilings remain unchanged. The
private local bundle adds one module (96 allowlisted files plus manifest), with
the same 15 resource pins.

Exit reverse DCF is explicitly unsupported. There is no new solver, fallback,
weakened certificate or automatic root. A selected Gordon analysis maps its real
operands to the existing certified request, preserving legacy solver output.
Market-implied-growth review explicitly reports exit unsupported; existing price
rights, timing, shares and perimeter blockers remain. No quote is fabricated.

## Interaction and exact review data

The inline method selector defaults to perpetual growth. No exit multiple is
preloaded. Exit shows `Year-five EV/EBIT`, × units, actual fiscal label and
current/stale calculated EBIT; its 32 required numbers exclude six Gordon inputs.
Gordon retains 37. Optional comparison fields preserve the opposite draft.
Method/multiple edits cancel/invalidate dependent work. Previous results retain
their original method labels; current differences/implied multiples are withheld
when stale. One Calculate action runs the selected method and valid comparison.

All three scenarios share the visible method; untouched multiples follow Base,
explicit Bear/Bull overrides stay fixed and reset explicitly. Each method keeps
its own intentional grid settings. Exit has no generated multiple range; axes
must be entered. Inspection/confirmed application uses × rather than percentages
and never writes a multiple into growth. Revenue/FCFF charts remain unchanged.
The single explanatory market-multiple note is in Sources & methodology.

Exact DCF downloads wrap the full calculation in selected-case, input-revision
and current/stale metadata. Calculations retain method operands, convention,
source/provenance, comparison input bindings and unrounded results. Scenario/grid
exports retain full submitted case and method-specific axes. Export generation
and object-URL lifecycle are tested. Actual browser file arrival remains
**unverified**: the supported download event timed out; no browser security
restriction was bypassed.

## Verification and limits

The synthetic example uses a USD100 anchor, annual growth/margin/tax/D&A/
investment/WC rates 10/20/25/5/10/2%, WACC 25%, multiple 15×, and independent
Gordon growth/terminal ratios 5% and 30/20/4/9/1%. These are arbitrary software
inputs, not company estimates or permanent defaults. Exact exit EV is
**186.0259692544 USD** versus Gordon **77.577060352 USD**, with identical
explicit PV **27.7063942144 USD**, exit terminal PV **158.31957504 USD**, and
Gordon implied multiple **4.725×**. Display rounds only. Desktop interaction also
used WACC 24% and multiples 12/16/20×; no researched range is implied.

Validation performed in this checkpoint:

- **199 valuation tests passed**, including independent rational exit equations,
  identical annual components/PVs, fifth-period discounting, strict parsing,
  missing comparison operands, zero/negative EV, unavailable implied multiples,
  qualified bridge handoff/tampering, exact grid/single-case agreement, scenario
  method consistency, calculation-free intake and output protection. Legacy JSON
  was compared with an isolated starting checkout, not just an old CLI importing
  the new engine. Whole-file engine/orchestration pins were narrowed for this
  authorized extension; historical consumer/source pins and certified reverse
  arithmetic/proof AST checks remain pinned.
- The initial affected API/catalog/history invocation passed **41 runnable
  checks**, but also had a collection error naming nonexistent `test_comparison`.
  The correct review/context modules then passed **11 checks**. This was a test
  command typo, not an application failure. A final **27-check affected rerun**
  and **four terminal API checks** passed (overlapping earlier coverage), including
  exact API/CLI agreement in both methods/scopes, comparison review, validation
  without execution, worker dispatch, maximum **11×11 exit grid** within unchanged
  budgets and explicit reverse-method rejection. The final typed-dispatch/solver regression
  rerun passed **35 checks**; these overlap the earlier groups.
- **211 frontend tests passed** across 20 files with one worker. Coverage includes
  raw multiple/percentage distinction, 32/37 completeness, opposite drafts,
  shared-method inheritance and same-value overrides, cancellation/late responses,
  per-method axes, explicit application, exact export data, malformed-response
  rejection, display-context isolation and legacy workflows. A long bridge test
  was separated into cancellation and populated-intake checks, with queries
  scoped to its dialog; runtime financial/service budgets were not increased.
- Main and separate prototype builds passed. The prototype retains its existing
  >500 kB chunk warning; no new dependency or build configuration was added.
- Actual **1440×900 and 390×844 CSS** browser review exercised both terminal
  methods, full/incomplete/invalid comparison states, inherited 15→16× Base with
  a fixed 12× Bear override, method-specific grids, inspection and confirmed
  application, percentage-notation and nonpositive-EBIT errors, and explicit
  outage/retry. Applying 24% WACC/12× left the saved Gordon growth at 5%.
  Multiple-only scenario runs produced identical Revenue and FCFF polyline
  coordinates, with different EVs. Both methods also ran three-case/grid flows
  at narrow width. Comparison fits without horizontal overflow; grid overflow
  stays contained. At 390px, page width was 373px. Screenshots were inspected.
- Stopping only the verified task-local API produced the sanitized unavailable
  state with the 15× input retained. Explicit retry against the final verified
  runtime restored **186.0259692544 USD**. Temporary browser inputs/results were
  cleared by reloading only the dedicated software-test tab, then selecting META:
  **0/37 entered**, perpetual growth, no exit multiple or calculation. Existing
  user tabs were not refreshed. No actual-company case/output was saved in the repository.
- Nine existing templates are byte-identical: **15 case bodies × 37 null numbers
  = 555 unset inputs**, including unresolved bridge/share declarations. Frozen
  history/approvals are unchanged. All 15 resource pins remain identical and
  all 96 runtime source/resource files match reviewed source. Final health, proxy
  catalog byte equality and full synthetic v3 local API/CLI equality also passed. Changed local
  documentation links and whitespace were checked. No historical corpus run.

### Local handoff

Review: <http://127.0.0.1:5175/workspace/> → local API **8002**, no cloud fallback.
The read-only bundle is `/tmp/valuation-exit-20261030/runtime-reviewed`. API PID
**27633**, Vite listener **99992**, npm process group **99976** are checkpoint
observations; check identity before stopping them. `kill -TERM 27633` and
`kill -TERM -- -99976` stop only these verified local processes. Logs, screenshots
and preservation receipts remain outside the repository in
`/tmp/valuation-exit-20261030/`. Temporary test-case directories were removed by
the test harness; the new committed example is explicitly synthetic. Browser
viewport overrides were reset. No hosted service, access, DNS or production site
was changed.

No actual META/GOOGL/AAPL valuation, input acceptance or preload methodology is
established. Existing eligibility, claims, awards and financial sufficiency
limitations remain case-specific and potentially unbounded.
