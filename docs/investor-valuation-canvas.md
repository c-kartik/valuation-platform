# Investor valuation canvas — local acceptance

October 29, 2026. Starting checkpoint: `5f2fd028350ace7fa45275a7403d87eeaf6ee6ee`,
clean `main`, one commit ahead of local `origin/main`. Local implementation and
checkpoint only; no push, deployment or cloud changes. Phase 1 expansion remains
[paused](phase1-universe-pause-checkpoint.md).

## Design and interaction boundary

The accessible public [Alphabet reference page](https://www.alphaspread.com/security/nasdaq/googl/dcf-valuation/base-case)
was inspected, including its result-first layout, clickable growth editor and
public Bear switch. Adopted principles: compact assumptions beside a financial
chart, focused editing with retained company/result context, scenario switching
and visual value composition. Authenticated saving, premium capabilities and
the provider's full model/data methodology were not inspected. No branding,
source code, forecasts or proprietary economics were copied.

Our model retains FCFF, operating margin, constant WACC and perpetual growth;
the reference's FCFE/net-margin/cost-of-equity/exit-multiple choices are not added.
No forecast horizon, financial convention, persistence or dependency is added.

The main page now has a compact company/data header, current or clearly previous
EV, sticky scenario/action context, compact assumption rows and a prominent
revenue/FCFF chart. Scenario comparison, sensitivity, breakdown and sources are
secondary exploration within the same company page. Optional equity/share remains
distinct and qualified. Market unavailability is a compact disclosure, with no
developer configuration instructions in the investor flow.

Click a row to open a desktop side sheet or narrow full-height editor. Six
sections expose every annual, WACC, terminal and optional bridge input. Drafts
survive section switching; Apply commits working inputs and invalidates affected
results; Cancel/Escape discards drafts and returns focus. Background scroll locks
while editing and restores on close. Calculation is explicit, never per keystroke.
Blank required inputs remain incomplete; syntax and Python domain errors point
back to the relevant editor. Constant/per-year controls and explicit one-time
year-five copying preserve independent terminal assumptions. An explicitly entered
same-value Bear/Bull override remains fixed when Base changes.

The chart shows one reported revenue anchor, no invented historical FCFF, and
five calculated years. Hover, focus, arrows, tap-style selection, metric controls
and an optional table expose exact returned components through display rounding.
Scenario comparison uses three cases for one selected metric. Composition shows
returned five-year and terminal PVs: positive eligible components get a stacked
bar; negative/zero EV or contributions outside 0–100% get signed values. Sensitivity
retains explicit editable axes, inspection without mutation and confirmed application.

## Source-bound historical references

`review/history.py` derives only FY2024→FY2025 annual revenue growth and FY2025
EBIT/revenue from retained, pinned annual packages after existing anchor checks.
It checks effective-view identity, reported origin, USD/precision, raw/sign/value
agreement and exact undimensioned annual occurrences. Growth requires consecutive
fiscal periods; isolated Decimal arithmetic preserves caller context. Missing or
incompatible operands produce unavailable references, never estimates.

The additive catalog projection carries formula, exact operands, source precision,
accession, fiscal dates and SEC links. Rounded displays are META 22.17% / 41.44%,
GOOGL 15.09% / 32.03%, AAPL 6.43% / 31.97% (growth / operating margin).
AAPL's fiscal end is September 27, 2025. Fiscal lengths may differ; no day-count
adjustment, average, CAGR, TTM or forecast calibration is implied. References do
not fill inputs. The relevant [issuer register](company-data-preparation/index.md)
and three records document this narrow derivation without changing earlier approvals.

FY2025 revenue remains the calculation anchor. Separately dated, newer annual/
interim context remains preparation-incomplete and is not used by the DCF. Unknown
cutoffs, tax/D&A/investment scope, claims and awards are not resolved by presentation.
The offline bundle adds one module: 95 manifest entries plus its manifest;
existing resource pins and execution safeguards are unchanged. Catalog size is
60,056 bytes, below its existing 64 KiB limit.

## Verification performed at this checkpoint

- 197 frontend tests passed across 17 files. Coverage includes editor drafts,
  focus/scroll restoration, no per-keystroke calls, annual/constant/terminal inputs,
  explicit overrides, stale/current states, shared gate/cancel/late responses,
  retry, bridge integration, chart and signed composition, sensitivity and exports.
- Nine historical-reference/catalog/preparation-preservation Python tests passed;
  new ratios independently match rational arithmetic within `1e-48`, including
  hostile caller Decimal context and unavailable-source cases.
- 29 affected API/review/compatibility Python tests passed, including strict
  intake, source preparation, cancellation/recovery and existing execution limits,
  reverse checks and unchanged legacy case/scenario/sensitivity JSON bytes.
- Six complete live local API outputs matched the CLI: three single-case anchors,
  synthetic AAPL equity, GOOGL scenario comparison and META 3×3 sensitivity.
  This reused the established arithmetic contracts; the prior record's 1,161
  independent comparisons were not rerun or counted as new checks here.
- Both frontend builds passed. The existing prototype build still emits its
  greater-than-500-KiB chunk advisory; no dependency or unrelated bundling change.
- Actual Chrome review at verified CSS 1440×900 and 390×844 covered company/scenario
  context, constant/annual editing, independent terminal inputs, Cancel/Escape/Tab
  and focus return, invalid tax correction, negative FCFF/EV, chart keyboard/tap
  readouts, comparison metric switching, sensitivity inspection/confirmed apply,
  optional equity, unavailable market state, and real local outage/explicit retry.
  Screenshots were inspected. A demonstrated narrow-sheet header clipping issue
  was fixed with background scroll locking. No entire-page horizontal overflow
  was observed at 390 pixels, including the contained financial table/grid.

Invocations: `npm --prefix frontend test`, `npm --prefix frontend run build`,
`npm --prefix frontend run build:prototype`; Python with
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest`
and these bounded groups:
`tests.review.test_history tests.api.test_catalog tests.analyst.test_preparation_preservation`;
`tests.api.test_cases tests.review.test_review tests.valuation.test_reverse.ReverseTests.test_existing_case_scenario_sensitivity_interfaces_and_json_bytes_unchanged`.
After the build caught an unsupported test-helper selector option, that helper
was corrected and its 13 workspace tests rerun successfully; both builds then passed.
No full historical suite or corpus research was performed. Final preservation
inspection checked all valuation modules, 15 existing resource pins, nine template
bytes and append-only issuer updates; 1,027 local links and 85 anchors resolved,
and whitespace checks passed.

Browser inputs were arbitrary **software-test choices**, not forecasts: five annual
growth 10%, margin 20%, operating tax 25%, D&A/revenue 5%, investment/revenue 10%,
full-revenue WC cash requirement 2%, WACC 25%, terminal growth 5% and independently
entered terminal ratios 20%/25%/5%/10%/2%. With retained revenue anchors this yielded
rounded EVs META $100.22bn, GOOGL $200.90bn and AAPL $207.54bn. GOOGL Bear/Bull
growth 8%/12% and Bull margin 22% exercised differences; Bear margin −10% produced
EV −$144.13bn and terminal contribution −56.52%. These are software observations,
not investment results. Synthetic AAPL bridge amounts $100m assets, $40m financing,
$10m claims and 20m dated synthetic common units exercised qualified equity output;
they are not actual AAPL selections. Trial inputs/results were cleared afterward.

Export serialization, exact contents and Blob-link lifecycle pass automated tests.
The supported browser link-download attempt did not establish downloaded-file
delivery. Prior download observation/inspection limitations were not bypassed;
actual Chrome file arrival remains **unverified**, not accepted as completed.

## Outstanding limits and local review

Genuine market comparison remains unavailable: provider key/display rights and a
supported current-date timing/bridge/share/split perimeter are outstanding. No
price, upside or market-implied growth was invented. The certified reverse engine
and legacy interfaces remain unchanged. This is software acceptance of the exercised
workflow, not complete financial sufficiency or investment readiness.

All nine company templates remain byte-identical with 37 unset numerical inputs
per case (15 case bodies, 555 nulls); actual bridge/share selections stay unresolved.
No company case, output or forecast policy is saved. Historical/frozen data,
approvals, valuation formulas/solver, portfolio and hosted services are unchanged.

Review at <http://127.0.0.1:5175/workspace/> → verified local Python API 8002,
without cloud fallback. Runtime: `/tmp/valuation-canvas-20261029/runtime`, an
immutable verified bundle. API PID **6910**; Vite listener **99992**, npm launcher/
process group **99976**. Other existing servers were preserved. To stop only these
review servers, first verify those process identities and runtime directory with
`ps`/`lsof`; then `kill -TERM 6910` and `kill -TERM -- -99976`. PIDs are a checkpoint
observation, not persistent service identifiers. Screenshots and bounded check logs
remain outside the repository under `/tmp/valuation-canvas-20261029/`.
