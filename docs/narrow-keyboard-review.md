# Compiled EV calculator — narrow desktop keyboard review

Developer review by Codex, 2026-10-20 (Asia/Dubai). **PASS for the exercised desktop
keyboard journey at Chrome 390×844 responsive viewport**, after the focused fixes
below. This closes the narrow keyboard qualification in the
[prior cloud/browser review](cloud-frontend-acceptance.md). This is not an actual
mobile device, touch/virtual-keyboard test, assistive-technology audit or complete
accessibility certification. Phase 1 stays [paused](phase1-universe-pause-checkpoint.md).

Used the production Vite build, existing loopback preview on 4173 and a freshly
verified private API bundle on 8000, entirely locally. No HMR or authenticated cloud
proxy, cloud arithmetic repeat, tooling installation or cloud configuration change.
Node 22.14.0 build: **four files / 291006 bytes**; JS `index-Dm91Ibhh.js`, SHA256
`35ef29cc936bb653986990be198e34b90267b02880e7bd64b04ac21823360690`;
CSS `index-BUsYcr5G.css`, SHA256
`003a567a35e856bc8e56422f99e69900123bd011339d0a59623ba6a0aeeb3f16`.

## Findings and bounded changes

The old inline `alertdialog` confirmations left focus on the triggering selector/
Apply control, while Escape did not cancel. This could hide the confirmation from
a narrow-screen keyboard user and let Tab move into unrelated controls. Replaced
both with a native modal dialog: background is inert, initial focus is the safe
Keep action, Tab/Shift-Tab cycle explicitly between its two buttons, Escape cancels,
and closing restores the connected invoking control. The explicit cycle was added
after observing native Tab leave the last dialog button for Chrome's own controls.
No economic logic or input values changed. Added a narrow modal style and scroll
margin for focus visibility. Two meaningful regression tests verify safe focus,
Tab cycle, cancel/confirm restoration and preservation of draft/annual data.
jsdom only shims dialog open/close; actual browser checks establish native behavior.

## Final compiled-build observations

| Task | Actual keyboard observation |
| --- | --- |
| Company / blank basis | Tab entered Company; arrow/Enter selected META FY2025 with retained revenue 200966m USD and blank assumptions. Explicitly loaded the separately labeled synthetic $100 demo for the full workflow. No company forecast was supplied or saved. |
| Quick input / replacement | Typed growth 12%; Tab/Enter opened replacement. Keep received initial focus, Tab wrapped confirm → Keep, Escape restored Apply. Draft stayed 12 and old annual values stayed 10. Reopened and explicitly confirmed; five annual growth values became 12. |
| Focus / scrolling | Traversed compact input/Apply controls with Tab. Opened advanced editing with Enter; Tab entered the scrollable region and all 30 inputs, then exited to terminal copying. Focus automatically scrolled into view vertically/horizontally, with visible blue outline. Reverse traversal returned to Company. No trap in the exercised route; modal Escape provided its exit. |
| Annual refinement | Keyboard changed synthetic period-three growth to 15; other four stayed 12, margin 20. Varies by year appeared. |
| Terminal copy / independent editing | Keyboard activated year-five copy, then changed terminal margin 20 → 21. WACC/g and annual margins remained independent. |
| Validation / correction | Deliberate terminal tax 125 returned 422 and 0%–100% guidance. Tab reached the correction link; Enter focused the invalid field. Corrected to 25 without losing the other edits. |
| Run / review / recalculate | Keyboard calculated, entered the result table and expanded cash-flow/EV reconciliation. Independent terminal margin 21 → 22 immediately showed STALE RESULT. Explicit recalculation cleared stale state and updated EV. Units, terminal dependence and EV-only qualification remained visible. |
| Company cancellation | Navigated back to Company, requested META switch from the populated demo, received Keep focus and cancelled with Escape. Selector focus, growth path, terminal margin and current result were preserved. |

Synthetic engineering sheet only: unchanged demo rates except flat annual growth
12% with period three 15%, explicit terminal copy and terminal margin 21% then 22%.
Annual margin 20%, tax 25%, D&A 5%, investment 10%, full-revenue WC 2%, WACC 25%, g 5%.
Observed EV: **0.00005678 → 0.00005911 USD millions**; final contribution **50.03%**.
These are tiny synthetic fixture results, not company economics or financial approval.
Two successful browser calculations and one deliberate invalid validation were
observed on the final build. No new full-browser/CLI arithmetic comparison claim;
the affected API regression rechecked existing full JSON/CLI compatibility.

Representative actual screenshots emitted in chat show safe modal focus, focused
year-three input inside a horizontally scrolled table, the focused validation-error
link and focused result table. Only the deliberate 422 appeared in the console;
no application exception observed. No screenshots/cases/valuation outputs were
saved in the repository. Temporary private bundle and local servers were removed.
The [public-preview preparation](public-preview-preparation.md) records tests,
publication scope, residual abuse risks and deployment decisions; no public access
or Hosting configuration was changed remotely.
