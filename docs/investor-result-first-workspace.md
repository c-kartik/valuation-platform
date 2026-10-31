# Result-first investor workspace — local implementation and acceptance

Subsequent [chart/history extension](chart-history-and-current-year-estimate.md):
five reported years, responsive plots without horizontal panning, an 80KiB catalog
ceiling and a submitted FY2026E summary. Earlier three-year/64KiB statements below
record this milestone's original boundary. Historical FCFF remains unresolved.

Historical record: the [compact workspace](investor-compact-workspace.md) now
supersedes this page composition, visibility-triggered navigation and confirmed
cell-application interaction. The execution/history foundation below is retained;
its reported checks are not relabelled as later verification.

October 31, 2026 (Dubai). Started on clean `main` at
`cdfc3cc14906d9a07b2cb273c8bf04d051ac0456`, five commits ahead of local
`origin/main`. This supersedes the ordinary inline-entry interaction in the
[earlier workspace](investor-inline-workspace.md) and its rule against initial
calculation. The [preload policy](googl-preload-methodology.md),
[worked estimates](googl-preload-worked-model.md),
[terminal conventions](exit-multiple-terminal-review.md) and
[Phase 1 pause](phase1-universe-pause-checkpoint.md) remain authoritative.
Local implementation only; no push, deployment, evidence acquisition or financial approval.

## Execution and editing

A fresh workspace selects GOOGL, validates its proposed profile, populates inputs
and automatically submits Base through the existing local Python API. Acquisition,
offline preparation and profile GET remain calculation-free. Incomplete issuers
retain specific missing inputs and an editor action; no default exit multiple,
historical FCFF, market price or equity/share population is invented.

One tab-memory store shares the existing execution gate, revision tokens and
working sessions across StrictMode/component remounts. A 100ms unmount retirement
allows immediate remounts to reattach; leaving the workspace cancels outstanding
work. Context edits/cancellation retain the original immediate abort/revision
checks. A bounded 24-response cache stores only checked, current responses, keyed
by exact submitted JSON/provenance, profile content/version and route. Issuer,
anchor, terminal method, scope and economic operands are consequently bound.
Failed, mismatched and cancelled responses are not cached. Reverse execution stays
explicit. No persistent storage, queue, infrastructure or frontend DCF is added.

The main canvas shows EV, a compact shared terminal selector, a combined operating
plot, read-only active assumptions and signed valuation composition. Long profile
metadata and refresh/adoption controls live in Sources. Full Model is read-only;
its submitted rows, explanations and exports retain their original revision and
profile even after later changes. Market/equity preparation stays secondary.

Varying inputs show first → final plus accessible five-year paths, never an empty
constant field. The whole-model dialog contains every annual value, independent
terminal inputs, expandable sources and individual resets. Several edits, including
intentional equal-value input, submit with one **Update valuation**. Constant-row
replacement is explicit. Cancel discards only unapplied editor work; execution
failures retain the draft and server validation focuses the corresponding input.
The last submitted result remains identifiable while editing/calculating.

Scenario and sensitivity requests begin on first section visibility with complete
current inputs. Successful model updates refresh visible dependencies; hidden
results remain stale. One revision-bound attempt and explicit failed-state retry
prevent presentation changes or failures from causing retry storms. Ordinary
editor typing does not submit work. Custom grid ranges remain explicit; the default
5×5 subdivides the existing ±1pp WACC / ±0.5pp growth spans, or ±2× EV/EBIT only
with an entered multiple. No clamp or confidence interval; invalid cells keep reasons.
Inspection and the active pair have different markers; application is confirmed.

## Observations and charts

The catalog adds at most three consecutive compatible annual revenue observations
ending at each retained model anchor. It reuses accepted-view identity, reported
fact/precision, annual duration and exact undimensioned occurrence checks. A gap
stops the window. No historical package, value, approval or sufficiency status changes.
For GOOGL these are FY2023/2024/2025 revenue USD307.394/350.018/402.836bn.
Each observation retains dates, precision, concept, accession and a retained HTML
filing link; the unchanged package retains the complete evidence. The catalog
remains **65,215 bytes within its original 64KiB limit**; no budget was increased.

DCF uses adjacent Revenue/FCFF bars on one zero-inclusive USD axis. Scenarios use
two aligned grouped plots, stable Bear/Base/Bull ordering and independent sensible
metric axes. History is one neutral common series. Historical FCFF remains
unavailable, never zero, CFO, a residual or forecast-derived cash flow.

Both views use full-year pointer/click/focus/keyboard targets, exact USD data
and display-only rounding. Scenario readouts include dollar differences from Base.
The two scenario plots share one horizontal scrolling stage, preventing axis drift.
Groups occupy about 42% of each fiscal slot; narrow charts pan within the page.

The fiscal anchor and Base scenario are distinct. Every revenue guide begins at
FY2025, including selections before that date. Observed comparisons verified:

| Selected observation | Display comparison with fixed FY2025 |
| --- | --- |
| FY2023 | −USD95.442bn; −23.69% |
| FY2024 | −USD52.818bn; −13.11% |
| FY2025 | Baseline, USD402.836bn |
| FY2028 Base | 19.63% endpoint CAGR over three fiscal-year intervals |
| FY2030 Base | 15.30% endpoint CAGR over five fiscal-year intervals |

These use actual displayed endpoints, not a headline assumption. No FCFF guide is
drawn without anchor FCFF; no forecast year substitutes for FY2025. Zero/negative
endpoints use dollar changes instead of misleading CAGR. All guide/axis arithmetic
uses an isolated Decimal context and changes no stored input or financial output.

## Verification performed here

- Full frontend regression: **227 tests in 21 files passed**. Subsequent focused
  runs passed **30 tests in two files** after adding checked-cache recovery and
  exact export/editor-snapshot checks, then **five chart tests** after tightening
  full anchor-identity compatibility. There are now 230 tests; a 230-test full run
  is not claimed. Commands used `npm --prefix frontend test -- --maxWorkers=1`,
  with the relevant test-file paths for focused runs. No test timeout was enlarged.
- Meaningful coverage includes initial Base/dedup under StrictMode and an in-flight
  remount, context/method late-response rejection, explicit retries, provenance,
  equal-value overrides, resets/adoption/inheritance, multi-edit/cancel/validation,
  exact submitted exports, visibility-driven scenario/grid refresh, 5×5 axes,
  inspection versus application, three-year history, fixed-anchor comparisons,
  signed bars and isolated display Decimal arithmetic. Existing financial-engine
  and solver tests were not modified.
- **37 focused Python checks passed** via the documented unittest invocation:
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest
  tests.review.test_history tests.api.test_catalog tests.api.test_preload
  tests.preload.test_preload tests.analyst.test_preparation_preservation -q`.
  This includes source-bound window/gap selection, calculation-free GET/preparation,
  real preload API/CLI agreement and preservation. No historical corpus research
  or full Python suite was rerun.
- Both `npm --prefix frontend run build` and `build:prototype` passed after final
  implementation changes. The existing prototype chunk-size advisory remains.
- Actual Chrome + local Python API review at verified **1440×900** and **390×844**
  covered fresh automatic Base without Calculate, combined bars, FY2023/24/25 and
  future selection, fixed-guide readouts, multi-edit/Tab/update, separate Cancel,
  source/reset controls, grouped scenarios and populated-path disclosures, missing
  exit input and an explicitly entered multiple, both method grids, range edits,
  inspection/confirmed application, a real API outage/explicit recovery, real
  invalid-tax focus and incomplete META/company switching. Method-only changes
  preserved every displayed operating revenue/FCFF value exactly.
- Narrow root width was **373px within 390px**. Charts had 345px viewports and
  820px content; observed horizontal scroll reached 474.44px. Scenario SVGs shared
  the same x coordinate before and after panning, and fiscal selection synchronized.
  Mobile editor geometry was approximately 390×844 with the footer within the
  viewport; entering then cancelling a mobile edit preserved the applied inputs.
- Export Blob contents and revision/provenance bindings passed exact JSON tests.
  A supported browser download-event wait timed out again. **Actual file arrival
  remains unverified**; no browser security setting or download restriction was
  bypassed. This limitation is not reported as a successful download.

Browser-only software choices were FY2027 growth19.5%, margin31.25%, WACC9/9.1%,
a cancelled9.5%, exit15×, inspected/applied8.6% WACC/2.75% growth and custom
8–10% WACC ×2.5–3.5% growth axes. Invalid tax101% tested error focus; a mobile
24% growth edit was cancelled. These were interaction diagnostics, not researched
or approved forecasts. All were reset/discarded. The final tab has the original
proposed profile, zero overrides and an unset exit multiple; no actual-company
case or valuation JSON was saved in the repository. Screenshots depict only the
unchanged proposed starting model or read-only inspection, not the trial overrides.

The conditional starting EV remains approximately USD1.421564tn, with negative
explicit PV and over100% terminal contribution, as documented in the unchanged
worked model. This is not investment readiness, an approved value/share result
or completion of historical FCFF, awards, claims, exit or market preparation.

Final preservation inspection confirmed the valuation/preload Python modules,
all source/configuration data, frozen JSON packages/approvals, resource pins and
examples unchanged. All nine templates are byte-identical: 15 embedded case bodies
×37 numerical nulls =555 unset inputs. Issuer-record additions leave their complete
prior text intact. The runtime sources match reviewed source; health is ready and
the Vite-proxied catalog matches the API byte-for-byte. All 1,094 local links and
86 anchors across 13 changed Markdown files resolved; whitespace checks passed.
No temporary case, result JSON, credential, build output or unrelated file belongs
to the checkpoint.

## Screenshots and local handoff

Captured from the actual local platform and visually inspected. Existing browser
90% zoom was retained; viewport overrides were temporary and reset. The screenshot
service's pixel dimensions can differ from the verified CSS viewport. No mockup
or Sites project was published.

- [Desktop combined DCF](assets/result-first-desktop.jpg)
- [FY2023 selected; FY2025 fixed anchor](assets/result-first-history.jpg)
- [Grouped scenario comparison](assets/result-first-scenarios.jpg)
- [5×5 sensitivity and separate markers](assets/result-first-sensitivity.jpg)
- [Whole-model editor](assets/result-first-editor.jpg)
- [Narrow page](assets/result-first-mobile.jpg), [contained panning](assets/result-first-mobile-pan.jpg)
- [Full-height mobile editor](assets/result-first-mobile-editor.jpg)

Review <http://127.0.0.1:5175/workspace/> → loopback Python API8002, no cloud
fallback. Verified API **PID73325** runs the immutable reviewed runtime
`/tmp/valuation-result-first-20261031/runtime2` (109 files plus manifest, unchanged
24 resource pins). Vite listener **PID99992**, npm launcher **PID99976**, port5175,
remain running. Only this identified API was stopped/restarted for outage testing;
unrelated servers and old user tabs were not deliberately refreshed or closed.
Logs/check receipts are outside the repository in `/tmp/valuation-result-first-20261031/`
and `/tmp/result-first-*.log`. Reverify PID/cwd before stopping a process.

Try a fresh page: wait for Base → inspect historical/future years → Edit assumptions
→ change several annual fields → Update once → open/cancel another session → visit
Scenario comparison and Sensitivity → inspect a cell without applying → Edit ranges
for explicit custom settings. Switching to Exit multiple demonstrates the missing
input until you enter a multiple. Reload clears unsaved tab work.
