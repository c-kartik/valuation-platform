# Assumptions editor cleanup — local verification

October 31, 2026 (Dubai). Started on clean `main` at
`ffa48215cb4cb2f098d0c0e490383dbfd9fc9e31`, seven commits ahead of local
`origin/main`. This refines only the assumptions dialog in the
[compact workspace](investor-compact-workspace.md). The approved snug-editor
mockup supplied visual guidance, not financial values or demonstration logic.
The main workspace/charts, economic conventions and [Phase 1 pause](phase1-universe-pause-checkpoint.md)
are unchanged. Local commit only; no push, deployment or new financial approval.

## Behavior and precision

All editor percentages display two decimal places, including annual paths, WACC,
growth, independent terminal ratios, optional comparison fields and constant-row
replacement controls. Display uses isolated Decimal arithmetic, with HALF_EVEN
rounding consistent with existing presentation. Opening, focusing/blurring and
updating untouched fields retain their exact underlying strings. This includes
nonzero values too small to display at two decimals; display zero is not a new
financial zero. No engine result, source or proposed profile is rounded.

Only explicitly edited percentage operands commit at two decimal places. While
typing, intermediate strings remain editable. Valid edits format on blur; Update
also normalizes edited paths, including keyboard/programmatic submission without
blur. Empty/invalid strings remain empty/invalid and validation identifies them.
Unchanged operands and sensitivity-review seeds keep their full precision.
Multiples, currency and share counts do not use percentage rounding.

Reset restores the full-precision generated/inherited estimate, clears that field's
override intent and displays two decimals. Repetitive per-cell status lines are
removed; internal provenance, inheritance and explicit equal-value override
semantics remain, with source/rule/operand disclosures available below the table.
Annual controls are approximately 96×34px at desktop, with snug rows and wrapped
labels; mobile uses 100×40px fields and 32px Reset targets, with 44px controls on a
coarse pointer. Scrolling stays inside the editor/table. Errors expand normally.

A labelled native radio group replaces only the editor's method dropdown. Navy
segments identify the selected method; arrows, Tab and visible focus work without
custom keyboard emulation. Method-specific and optional comparison drafts survive
switches. Cancel discards the pending switch. A method-changing Update executes
the candidate through the existing checked API path and commits the shared method
only on success. Failure/cancellation/stale responses do not commit it. Obsolete
scenario work is cancelled before that Update, preventing a false success from
an older current EV. Ordinary same-method failure behavior remains unchanged:
submitted entries and the dialog remain available for correction/explicit retry.
No multiple is supplied when the required exit input is missing.

## Checks performed here

- Full frontend regression: **248 tests in 22 files passed** via
  `npm --prefix frontend test -- --maxWorkers=1`.
- After the final method busy-work safeguard, replacement-control reuse and CSS
  refinement, **48 focused tests in three files passed** using the same command
  with `src/workspace/ModelEditor.test.tsx src/workspace/Workspace.test.tsx
  src/workspace/preload.test.tsx`. The full run predates the final added regression;
  a 249-test complete rerun is not claimed.
- Tests compare the complete untouched request and original rate strings, and
  verify one-field/terminal edits, intermediate strings, HALF_EVEN ties and caller
  Decimal-context isolation, reset precision/provenance, invalid/empty handling,
  method draft retention, missing multiple, Cancel, checked successful commit,
  failed/late method responses and cancellation of obsolete scenario work.
- The normal frontend build and prototype build passed. The prototype's existing
  chunk-size advisory remains. Financial engine/API code is unchanged; no full
  Python suite, corpus research or new evidence acquisition was performed.
- Actual Chrome + the real loopback Python API at verified **1440×900** and
  **390×844**: populated two-decimal fields, no repeated Generated lines, wrapped
  labels, Reset, Tab/focus restoration, native radio arrow navigation, missing
  multiple focus, draft retention across method switches and readable validation.
- An untouched Update after focus/blur preserved all 13 unrounded rendered chart
  observations and displayed EV. A temporary software-only 24.126% growth entry
  displayed/committed 24.13%; Reset restored every original returned chart amount.
  An unexecuted 15.123456789× multiple retained its digits across method switches
  before Cancel. Invalid 10% WACC remained invalid text, with visible error/focus;
  Reset displayed the original 8.94% without reducing its underlying 8.9408%.
  These were interaction diagnostics, not company forecast selections/defaults.
- Mobile measured 390×844, root width 390px; its annual table panned internally to
  the final year with about 430.56px scroll, without page overflow. Desktop fields
  measured about 96×34px and rows 74.53px. No errors or labels were hidden to save space.
  Existing 90% browser zoom was retained; captures use the observed page offset to
  avoid the screenshot service's zoom/scroll framing mismatch. Temporary viewport
  overrides were reset. No old user tab was deliberately reloaded.

No trial case/output was saved. The review tab returns to the unchanged proposed
GOOGL profile, with no trial overrides or exit selection. Frontend 5175 and the
existing unchanged local Python API 8002 remain running; no server restart or cloud
change was required. Browser download delivery was not tested in this milestone.
Underlying financial sufficiency, actual equity/award/claims choices and exit
selection remain unresolved as recorded in the linked compact-workspace report.

Preservation checks confirmed all nine templates byte-identical: 15 embedded
case bodies × 37 numerical nulls = 555 unset inputs. All 109 immutable API runtime
files match repository bytes and their manifest. Engine/API financial contracts,
preload policy/values, source/history/approval records and the source mirror are
unchanged. All 582 changed-document local links and 66 anchors resolved; whitespace
checks passed. No temporary case/output, credential or build artifact is included.

## Screenshots and review

- [Desktop annual table](assets/assumptions-editor-desktop.jpg)
- [Desktop method segments and independent ratios](assets/assumptions-editor-terminal.jpg)
- [Mobile annual table](assets/assumptions-editor-mobile.jpg)
- [Mobile terminal inputs](assets/assumptions-editor-mobile-terminal.jpg)

Open <http://127.0.0.1:5175/workspace/> → **Edit all assumptions**.
All captures show the unchanged proposed starting model, not diagnostic edits.

## Constant-rate disclosure spacing follow-up

The replacement percentage and “Replace these five annual values” button now sit
on the same row, with the label above and draft/terminal-scope note below. All six
meanings/source sections use a tighter heading-to-caption gap (about 12px in the
observed desktop layout). Source disclosures and replacement behavior are retained.
The button can wrap its text on narrow screens without moving below the field.

Verification: the existing 14 workspace interaction tests passed, including
explicit row replacement and independent terminal values; TypeScript checking and
the frontend production build passed using the installed Node 22 runtime. Actual
Chrome desktop and a temporary phone-width viewport confirmed side-by-side
controls and readable wrapped captions. The viewport override was reset and the
review draft was cancelled. No financial inputs, formulas or source records changed.
