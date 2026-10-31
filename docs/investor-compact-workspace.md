# Compact investor workspace — local implementation and acceptance

Subsequent [editor cleanup](assumptions-editor-cleanup.md) refines percentage display,
row density and the method selector. The checks below remain this earlier
checkpoint's historical record.

October 31, 2026 (Dubai). Started on clean `main` at
`3b714377e617a33117e0889d5bf3924c60cbb2c1`, six commits ahead of local
`origin/main`. This supersedes the composition and navigation in the
[result-first record](investor-result-first-workspace.md), retaining its execution
and source-bound chart foundation. The approved local solid-bar mockup was used
as a visual reference only; none of its illustrative economic arrays was copied.
No push, deployment, evidence acquisition or financial approval. The
[Phase 1 pause](phase1-universe-pause-checkpoint.md) remains in effect.

## Interaction

A compact company header precedes a narrow desktop summary column and a dominant
results area. Five views are DCF, Scenarios, Sensitivity, Full Model and Sources.
The sidebar shows effective growth/margin endpoints, annual-path disclosures,
forecast dates, FCFF identification, WACC, terminal parameter, qualified bridge
status and the selected case's EV. Incomplete inputs remain identified as such.
On narrow screens the results precede the stacked summary; charts and annual
input tables pan within their containers instead of widening the page.

**Edit all assumptions** opens one populated annual table, with independent
terminal inputs and a local terminal-method selector. A summary row focuses its
relevant operand. Generated/inherited, overridden, edited and reset states remain
distinct; source/rule and constant-row replacement controls are disclosed below
the table. Percentages remain reversible strings at full precision. Normal Tab
navigation includes reset controls. Update validates, applies and executes through
the existing API; method changes then use the existing shared Bear/Base/Bull
method transition. Cancel discards unapplied dialog edits and restores focus.
After a submitted calculation fails, entries and the previous result remain;
correction/retry is explicit and does not imply economic approval.

Complete proposed profiles still calculate Base on entry. The existing shared
gate, revision checks, StrictMode/remount deduplication and exact-request cache
are retained. Opening Scenarios or Sensitivity now triggers its complete/current
calculation, replacing intersection visibility as the trigger. Failed attempts do
not loop; a successful model update refreshes the open dependent view. Navigation
preserves inputs, overrides, ranges and valid results. Hidden dependencies retain
explicit stale status until recalculated.

DCF combines Revenue and FCFF on one signed USD-billions axis. Scenarios retain
two aligned plots, synchronized inspection, exact amounts and differences from
Base; the EV table follows both plots and inputs remain behind Show inputs.
Theme tokens supply solid navy Revenue, gold FCFF/Base, slate Bear, teal Bull and
neutral reported history. No patterned bar/legend fill remains. Fiscal-year
comparison guides still use the fixed model anchor, with no historical FCFF
substitution. Metric headings/guide labels stay visible during narrow panning.
Pointer movement inspects a column; scroll-induced mouse entry cannot override
keyboard selection. Tap/click and arrow/Home/End access remain supported.

Sensitivity opens its existing engine-generated 5×5 diagnostics. Ranges remain
behind Edit ranges; invalid cells keep their reason. **Review this pair** seeds
only WACC and growth/multiple in the shared editor, without applying them or
executing. Cancel leaves active inputs intact; Update is the explicit transition.
The outlined active pair and inspected pair are distinct. Full Model explicitly
names the selected case and uses that case's submitted result/revision, with
active inputs separate from returned rows and exact exports.

## Verification performed in this milestone

- Full frontend regression: **234 tests in 21 files passed** using
  `npm --prefix frontend test -- --maxWorkers=1`. An earlier concurrent run had
  one unchanged legacy App busy-recovery test exceed its 5s limit; the subsequent
  complete run passed without a timeout increase. Initial tests were updated for
  the new view/editor controls and complete synthetic response fixtures.
- **39 focused tests in three files passed** after final readout/presentation
  and type-check corrections, using the same command with
  `src/workspace/Workspace.test.tsx src/workspace/preload.test.tsx
  src/workspace/ScenarioCharts.test.tsx`. These cover effective fields, focus,
  multi-edit/update/cancel, shared method commit, inheritance, selected-case Full
  Model, initial/deduplicated/stale execution, automatic view dependencies,
  sensitivity draft review/update/invalid cells, and solid consistent palettes.
  Existing engine, solver, API contracts and financial tests were not changed.
- **37 Python API/preload/preservation checks passed**:
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest
  tests.review.test_history tests.api.test_catalog tests.api.test_preload
  tests.preload.test_preload tests.analyst.test_preparation_preservation -q`.
  This includes real preload API/CLI agreement, source-bound historical windows,
  calculation-free preparation/GET and preservation; no full Python suite/research.
- Both `npm --prefix frontend run build` and `build:prototype` passed. The existing
  prototype chunk-size advisory remains; no dependency/build configuration changed.
- Actual Chrome review used the real local Python API at verified **1440×900** and
  **390×844** CSS viewports. Fresh GOOGL Base appeared without Calculate. Review
  covered populated annual editing, normal Tab, Update propagation, Cancel/focus
  restoration, source resets, shared scenario inheritance/plots, Bear Full Model,
  sensitivity review without application, missing exit input, server tax-error
  focus, and a real API stop/restart with preserved draft and explicit retry.
  The narrow editor measured 390×844 with its footer inside the viewport.
- FY2023/FY2024 selection showed −23.69%/−13.11% relative to fixed FY2025;
  FY2025 showed baseline; FY2030 showed 15.30% endpoint CAGR over five intervals.
  Historical FCFF remained unavailable. Negative forecast FCFF remained below
  zero. Mobile End selection remained FY2030 after focus-driven panning.
- The narrow page root stayed within 390px; chart/grid viewports measured 331px,
  chart content 820px. The two scenario SVG x coordinates remained equal after
  panning and their fiscal selection synchronized. A custom 2–4% WACC grid with
  unchanged 2.5–3.5% growth produced 14 explicit invalid cells; no zero substitution
  or Review action was offered. Default diagnostic axes were restored afterward.
- Component tests exercise pointer-move inspection. The live walkthrough used
  column clicks/taps and keyboard actions; isolated live mouse hover was not
  separately exercised. Exact export Blob tests passed; browser download-file
  delivery was not retested or claimed verified.

Browser-only software choices were FY2026 growth 22%, FY2027 margin 31%, WACC 9.2%,
invalid tax 101%, a cancelled exit-method change with its multiple unset, a
cancelled 24% mobile growth edit, and an inspected Bear 9.4408%/3.25% pair. These
were interaction diagnostics, not proposed forecast policy or financial acceptance.
The changed annual/WACC/tax values were reset to the existing estimate, optional
exit remained unset, and custom ranges were recentered. No company case/result
JSON was saved in the repository. Screenshots show the unchanged proposed profile.

The existing conditional GOOGL output remains approximately USD1.421564tn EV,
negative explicit PV and 100.01% displayed terminal contribution, consistent with
the unchanged [worked model](googl-preload-worked-model.md). This is not an
investment-ready valuation. META/AAPL remain incomplete; historical FCFF, actual
claims/shares/awards, market preparation and exit selection remain unresolved.
The [preload policy](googl-preload-methodology.md),
[prior preload acceptance](googl-preload-acceptance.md) and
[terminal conventions](exit-multiple-terminal-review.md) remain authoritative.

## Preservation and handoff

Engine/API financial contracts, preload rules/values, source bindings, approvals,
frozen packages and all nine templates are unchanged. The templates remain
byte-identical to starting HEAD: 15 embedded bodies × 37 numerical nulls = 555 unset
forecast inputs. No mockup, sources mirror, temporary case, valuation JSON,
credential, build output or unrelated file belongs to this checkpoint. Final checks resolved 585 local links and 66 anchors across the changed
Markdown files; whitespace checks passed. All 109 runtime files match their
manifest and current repository bytes, and health reports ready.

Local review: <http://127.0.0.1:5175/workspace/> → loopback Python API 8002.
The unchanged immutable runtime at
`/tmp/valuation-result-first-20261031/runtime2` was reused, not rebuilt or deployed.
Only verified local API PID 73325 was stopped for the outage test; replacement
PID 75254 and existing Vite PID 99992 (npm launcher 99976) remain running.
Recheck PID/cwd before stopping anything. Logs and check receipts remain outside
Git under `/tmp/valuation-compact-20261031/` and `/tmp/compact-*.log`.
Temporary viewport overrides were reset; no old user tab was deliberately reloaded.

Actual platform screenshots, visually inspected:

- [Desktop DCF](assets/compact-workspace-desktop.jpg)
- [Both scenario plots and reconciliation](assets/compact-workspace-scenarios.jpg)
- [Sensitivity and separate inspection](assets/compact-workspace-sensitivity.jpg)
- [Mobile page, panned to forecast years](assets/compact-workspace-mobile.jpg)
- [Full-width mobile editor](assets/compact-workspace-mobile-editor.jpg)
