# Six-row sidebar and profit-to-cash editor

October 31, 2026. User-approved layout; local workspace only.

## Behavior

The left sidebar contains six summary rows: Revenue growth, Operating margin,
Cash flow conversion, Forecast period, Discount rate and Terminal value. Business
assumptions and valuation settings form two cards. The tax/D&A and investment/WC
summary rows are replaced by one conversion entry. The FCFF model is a badge near
the company name. Equity & per-share settings sit inside the valuation result card,
below its Bear/Base/Bull selector; the original optional bridge editor is reused.
Edit all assumptions and Sources & methodology remain below the sidebar.

Conversion is a display-only summary of the final explicit forecast year's
**returned FCFF / returned operating profit (EBIT)**, with the exact year labelled.
It does not use net income, NOPAT, cash-flow margin or an average of annual ratios.
Negative conversion and conversion over100% are preserved. A zero/negative EBIT,
missing result or nonfinite operand produces an explicit unavailable/not-calculated
state instead of an invented denominator. A stale result is labelled with its own
submitted year and previous-result status. The same display applies to five-/ten-
year horizons, either terminal method and each selected scenario.

The conversion row opens one on-demand “From operating profit to cash flow” view
inside the existing whole-model draft dialog. A fiscal-year selector displays the
submitted EBIT, operating tax, D&A, investment, WC cash requirement and FCFF with
signs and explanations. Values are returned operands, not a client-side FCFF
calculation. Pending typing does not change that breakdown. The form exposes four
annual driver rows with plain-language labels and their precise percentage bases;
source/reset and constant-replacement disclosures remain accessible.

“Edit all assumptions in this draft” expands the same draft without losing edits.
Required errors outside this focused view automatically expand it and focus the
relevant input. Cancel discards only the current dialog draft and restores its
opener. Update uses the unchanged validation/execution path. Existing two-decimal
editing rules, original full-precision values, resets, override intent and scenario
inheritance remain. No extra editable conversion percentage or aggregate financial
forecasting rule is introduced.

## Financial boundary

This user request authorizes presentation of an existing calculated relationship.
It changes no engine formula, transport/schema, preload policy, source selection,
historical input/approval, fiscal anchor, WACC/terminal convention or resource pin.
No raw filing residual or Alpha Spread Net CapEx is substituted. Historical FCFF
and longer-horizon preload methodology remain unresolved. Phase 1 remains paused.
The optional cash/claims/share declarations do not become financially approved by
moving their entry point.

## Verification

- Full frontend run: 257 tests in 23 files pass. Final affected Workspace and
  presentation checks: 25 tests pass, including the forty-field ten-year focused
  form and final-year summary, validation outside the focused view, Cancel/focus
  restoration, signed ratio/zero/negative EBIT and isolated Decimal rounding.
- TypeScript and production/prototype builds pass. The prototype's pre-existing
  chunk-size advisory remains; no dependencies added.
- Actual desktop and 390px-phone browser review covers the six rows, year switching,
  negative FY2026 conversion, unchanged submitted values while typing, local
  validation focus, source Reset, expanding the same draft, Cancel and an unchanged
  Update. Annual inputs pan within their table; the mobile editor body and page
  retain their own width. Equity/share entry opens from the result card and restores
  focus on Cancel. Unset META does not inherit GOOGL's conversion/result.
- Default Base estimates restored after temporary software checks; no trial inputs
  retained. Screenshots are in this chat's `outputs/six-row-sidebar/` directory.
- API, runtime bundle, all source/profile resource pins, nine unset templates and
  Python valuation formulas unchanged. No push or deployment. Local review:
  <http://127.0.0.1:5175/workspace/>.
