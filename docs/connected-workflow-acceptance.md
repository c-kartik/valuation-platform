# Connected investor workflow — local acceptance, October 29, 2026

## Verdict and scope

**PASS for the exercised local software workflow, after two presentation fixes.**
No calculation defect was found. This accepts the approved connected experience
within the tests below, not economic completeness, investment readiness or a public
launch. **Cloud readiness: NOT ASSESSED in this review.** No hosted service, access,
billing, IAM, deployment, portfolio or DNS operation was performed.

Starting state was clean `main` at `3495cf359e94fee2ae35098194ca6cdb1685299b`,
11 ahead of local origin/main. The [integration record](integrated-investor-analyses.md)
retains its October 28 checks; they are not substituted for this review's checks.
[Phase 1 remains paused](phase1-universe-pause-checkpoint.md).

## Acceptance matrix

| Workflow/question | Newly exercised evidence | Result |
| --- | --- | --- |
| Company/case identity; facts versus forecasts | META desktop, GOOGL 390×844 journey; AAPL forward/equity/reverse date check. Historical revenue/precision/fiscal dates remain distinct from unset manual assumptions. Switching preserves separate cases without foreign notices. | PASS |
| Main/advanced/terminal inputs | Varied FY2027 growth `12.125000000000000001%`, META FY2028 margin 21%, independent terminal margin 22%; exact strings retained. Empty submission focuses a labeled input; no result produced. | PASS |
| Forward and optional equity | Explicit EV then dated synthetic bridge/share declarations; unresolved bridge blocks per-share while retaining EV. Explicit unbounded omissions remain visible. | PASS |
| Bear/Base/Bull | Explicit copies and independent 8%/18% Bear, 12%/24% Bull growth/margin edits; qualified shared-bridge comparison. Unexpected ordering remains neutral after differing WACC. | PASS |
| Sensitivity | Exact selected Base carried without re-entry; mixed valid/invalid cells, reasons/nulls, inspection, keyboard movement, cancelled/confirmed apply. Only WACC/g change; explicit recalculation required. | PASS |
| Reverse EV/share | Explicit dated targets/bounds, unreachable status without solution, certified EV and qualified share solutions, residual/bracket trace. Target edits and terminal edits withhold old success. | PASS |
| Exploratory case | Confirmed creation from successful reverse; no inherited forward result. Fresh EV and GOOGL equity run; original annual/terminal inputs and shared bridge retained. Exploratory edits preserve an independent current strict comparison. | PASS |
| Freshness and overview | Operating/terminal/WACC/grid/target edits stale relevant results. Bridge/share edits preserve operating EV, withhold stale grid share values and stale per-share reverse. Notes/name edits preserve financial results and earlier submitted trace. All four tools accessible from shared navigation/overview. | PASS |
| Recovery/admission | Real browser cancellation/late completion and explicit retry; real unavailable API retains target/bounds and recovers after verified restart. Regression checks cover double submission, busy, deadline, child cleanup and owner-safe late replies. | PASS within local process/client bounds |
| Keyboard/narrow layout | Enter/Tab/Escape activation, error focus, confirmation focus return, visible outline, matrix Home/End and internal horizontal scrolling. No horizontal page overflow observed. Native company selects used semantic selection; not a complete screen-reader audit. | PASS within exercised controls |
| Reload | Verified all company sessions/results disappear on reload, consistent with “Session only · no saving.” Cleared META returns to 0/37, only Base, no calculations. | PASS; no persistence or unsaved-work guard |

Browser review used **Chrome on desktop**, requested 1440×1000 and 390×844 viewport
overrides. It was **desktop resizing, not actual mobile hardware**, virtual-keyboard
or assistive-technology certification. Chrome initially was closed/unavailable;
reopening/reconnection succeeded before the walkthrough. No earlier screenshots or
browser actions were counted as newly performed.

## Demonstrated blockers and minimal fixes

1. **Wrong running-tool label after navigation.** BridgePanel rendered every
   non-equity job as “Calculating enterprise value,” including scenarios, grid and
   reverse. A focused rendering test failed for those three states. A five-entry
   display-label mapping now names the actual shared action; the live browser
   showed “Calculating reverse DCF” after navigating to the bridge during a solve.
   Gate, cancellation, inputs and calculation behavior are unchanged.
2. **False usable-EV wording when both results were stale.** Applying WACC/g after
   an equity calculation correctly staled EV/equity, but the overview still said
   “usable EV remains separate.” A reproducing workspace test failed. The message
   now says enterprise value also needs recalculation whenever EV is not current;
   bridge-only staleness still retains the usable-EV wording. Verified in the
   narrow-screen overview after confirmed application.

No redesign, formula, certified solver, schema, resource-limit or financial-policy
change. Remaining presentation friction is recorded below rather than expanded
into new features.

## New numerical and regression evidence

- **185 frontend tests passed** after both fixes. **228 focused Python tests passed**:
  184 valuation tests and 44 API/preparation checks, including calculation-free
  validation, strict intake, limits, busy admission, real deadline/CPU termination,
  disconnect/cancellation, reap/recovery and preparation preservation. No full
  historical suite, corpus review or research. Both production and isolated
  prototype builds passed; the existing prototype large-chunk warning remains.
- **18 complete runs through the actual Vite `/api` proxy** matched existing CLI
  JSON across all three retained anchors: forward, equity, scenarios, sensitivity
  and both reverse target scopes. Nine scenario results matched individual runs;
  six selected cells and six successful reverse results matched fresh forward runs.
  **1,527 independent exact-rational comparisons** checked annual/terminal FCFF,
  taxes, discounting, bridge signs/shares and EV; **24 additional known-root,
  bracket-width and residual checks** passed.
- **20 new browser-captured JSON results** matched their CLIs exactly. Six embedded
  scenario cases, four selected grid cells and five reverse solutions matched
  individual forward executions. **507 additional rational checks** covered those
  grid cells/solutions, plus 15 exact residual/bracket checks. Snapshot comparisons
  confirmed both apply actions changed only WACC/g; both reverse forks changed only
  the five growth rates apart from generated identity/time, preserving notes and
  other financial inputs. GOOGL exploratory Stage C inputs matched its source
  reverse solution's shared bridge/share inputs exactly.
- Rational comparisons used `1e−30 + 1e−46 × |reference|` USD/component tolerance;
  no float financial arithmetic or duplicate engine oracle. Reverse checks enforce
  the existing ≤1e−12 growth bracket and returned scale-aware residual tolerance.
  Exact source strings/JSON equality were checked separately from rounded display.

Sample local measurements, **not worst-case guarantees**:

| Newly run sample | Elapsed / serialized bytes |
| --- | --- |
| 18 actual-proxy case/scenario/grid/reverse runs | 0.407–3.359s / 19,336–390,607 bytes |
| Maximum 11×11 EV grids, META/GOOGL/AAPL | 4.956 /6.875 /6.612s; 180,641 /205,325 /205,821 bytes |
| Maximum AAPL synthetic equity grid | 6.864s /368,562 bytes |
| Demanding reverse regression, three anchors | 5.158–7.891s /90,086–140,982 bytes; all `ITERATION_LIMIT`, null solution |

Existing ceilings remain 256 KiB request, 2 MiB result, 35s wall deadline, 30s child
CPU, bounded parser/numeric resources, 11×11 grid and default 128 reverse iterations.
Deadline/busy cleanup was exercised by automated real-child tests; the browser
manually exercised cancellation and unavailable/retry, not a forced 35s timeout.

## Temporary assumptions and limits

All future/bridge values were **arbitrary software choices**, not researched issuer
forecasts, reported balances, financial approvals or defaults. Actual retained
FY2025 revenue anchors/fiscal calendars were used. API probes started from existing
synthetic fixtures, then used 10% annual growth, 20% margin, 25% tax, 5% D&A, 10%
investment, 2% full-revenue WC; FY2027 growth 12.125000000000000001%, FY2028 margin
21%, terminal margin 22%, other fixture terminal ratios 20/4/9/1%
(tax/D&A/investment/WC), WACC 25%, g 5%.
Bear/Bull used 8/18% and 12/24% growth/margin. Synthetic net bridge +USD50m used
USD100m eligible assets, USD40m financing and USD10m claims, 20m synthetic shares.
Known-root API targets were generated at constant growth 7.3456789123%.

Browser META used that varied path; GOOGL varied FY2027 growth with annual margins
20%, terminal margin 22%; AAPL used uniform baseline rates with terminal margin
20%; browser terminal tax/D&A/investment/WC were 25/5/10/2%. Explicit terminal
copy was performed once before independent edits. Tested
WACC/g axes were 2/16/30% and 2/5%, with GOOGL g expanded explicitly to 2–12% by
1 point to exercise scrolling. Apply selected 16% WACC/2% g. Reverse bounds were
−20% to 30%; temporary EV targets 100,000 (META), 200,000 (GOOGL/AAPL) **USD millions**,
share targets 5,000/10,000 USD/share, plus an unreachable negative META EV target.
Dates were fiscal end and declared cutoff February 5, 2026, **not authenticated
source availability**. Browser populations/awards explicitly retained unbounded
omissions; no actual class-equivalence or existing-award valuation was selected.

Historical context remains revenue-only. Financial eligibility, sustainable
reinvestment, claims/awards/funding/settlement coverage and information sufficiency
remain unestablished, potentially unbounded. Neither grid ranges nor certified roots
bound total value or establish unique market beliefs. Verbose full-precision JSON
and technical certificates remain review friction; on narrow screens the inspector
is above the scrollable grid. Reload loses all work with no save or warning dialog.
The shared gate is per mounted client/API process, not distributed cloud admission.
Cloud/public-build compatibility, security/access, operational sizing and readiness
were not inspected or certified by these local checks.

## Final preservation and review environment

The current 87-file immutable API bundle was hash/allowlist verified and matched
checkout bytes/pinned resources before use and restart. Only the identified loopback
API was stopped for the unavailable test. An initial restart accidentally resolved
to system Python without Uvicorn; using the repository `.venv/bin/python` corrected
that launch. Health and explicit browser retry then passed. Workspace/prototype
processes were preserved; no bundle required a rebuild for these frontend labels.

Financial formulas, solver/certificate, all Python/API source, historical/frozen/
approval records, prototype fixtures, deployment files and portfolio remain unchanged.
All nine templates retain exact bytes: 15 case bodies each with 37 numerical nulls;
bridge/share selections remain unresolved. Temporary request/result files and helper
scripts were removed; trial browser sessions cleared. Review screenshots and test
logs stay outside the repository; the running immutable bundle is retained.

Only the two display fixes, their focused tests, this record and minimal current-doc
references belong to the local checkpoint. Nothing pushed or deployed. The
[workspace](http://127.0.0.1:5173/workspace/), [reference calculator](http://127.0.0.1:5173/)
and [prototype](http://127.0.0.1:5174/prototype/) remain running. Inspect listener and
process identities on 5173/5174/8000 before sending SIGTERM; do not delete the API
bundle while its process runs. Stop here for review; further features/publication
remain separately scoped.
