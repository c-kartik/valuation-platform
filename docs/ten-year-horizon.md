# Five- and ten-year forecast horizons

October 31, 2026. User-scoped extension of the local investor workspace. Five
years remains the default. No new GOOGL forecast assumptions or financial approvals
are established, and Phase 1 remains paused.

## Behavior

Open **Forecast period** in the sidebar, or **Edit all assumptions**, then choose
**5 years / 10 years**. This is an unapplied whole-model draft. Years 1–5 retain
their original unrounded values. New years 6–10 are empty, require six explicit
annual inputs each, and have no generated Reset target. Update validates all
active inputs and calculates; Cancel preserves the previous horizon/result.
A successful horizon-changing Update commits the shared horizon across cases.
Base's additional-year entries flow to nonoverridden Bear/Bull fields without
applying the five-year profile's diagnostic offsets to those new years.

Shortening the horizon parks additional-year entries in tab memory; expanding it
restores them. Parked entries do not enter requests, validation or calculations.
Profile adoption refreshes only profile-defined fields and preserves additional
manual years. Full reload clears tab memory as before.

Charts show ordinary fiscal-year bars throughout. A dotted vertical line **after
the fifth explicit forecast year** appears only on ten-year DCF and scenario
charts, in addition to the history/forecast divider and fixed historical anchor.
There is no transition-period label or shading. For FY2025 origin it is between
FY2030 and FY2031. The FY2025 comparison anchor stays fixed. Wider ten-year plots
pan internally, retaining bar spacing. Full Model, scenarios, sensitivity and
exports use the submitted horizon and values.

## Financial and wire contract

The annual FCFF equations, precision-50 HALF_EVEN arithmetic, scalar WACC and
fiscal-end discount timing are unchanged. With N explicit years:

- Explicit PV = sum of FCFF_t / (1 + WACC)^t for t = 1 through N.
- Perpetual-growth terminal FCFF is the independently specified year N+1, with
  revenue based on year N and terminal growth. TV_N = FCFF_(N+1)/(WACC − g).
- Exit TV_N = year-N EBIT × the explicitly supplied EV/EBIT multiple.
- Either terminal value discounts by (1 + WACC)^N. Equity handoff remains qualified.

Legacy case versions v1/v2/v3 remain five-year. New `investor-case-v4` and
`analyst-case-v4` use the v3 method-aware shape plus required integer
`forecast_horizon: 10` and exactly ten ordered explicit annual rows. Their internal
assumption schema is `2`; schema `1` retains the five-year engine boundary.
The legacy `forecast_five_years` entry point stays five-year; `forecast_periods`
serves the extended case. New result envelopes end in v4. Exit uses
`fiscal-end-terminal-ev-ebit-v2`, `final_year_ebit` and `implied_final_year_ev_ebit`;
five-year exit output retains its existing field names and convention identifier.
Gordon retains the general annual-discounting convention, with actual exponents
and terminal period recorded in its result.

Existing scenario/sensitivity envelopes accept complete v4 embedded cases;
comparisons still require identical period identities and financial perimeter.
Ten-year exit sensitivity reports final-year EBIT. Fiscal-end revenue CAGR uses
the actual horizon. The degree-five certified reverse solver is **not extended**:
ten-year reverse and market-implied growth remain explicitly unsupported. No
certificate or financial claim is extrapolated to degree ten.

## Additional-year preload methodology — unresolved

The current GOOGL policy prepares five annual forecast years only. No six-to-ten
preloads, consensus observations, automatic fades, repeated year-five values or
new terminal selections are approved by this implementation. A horizon choice
alone cannot manufacture five more years of economic inputs.

Before enabling proposed additional-year estimates, agree a versioned policy for:

1. Revenue growth: the year-ten target, its support, and the path from year five.
2. Operating margin: an independently justified target and annual path.
3. Operating tax: the long-run operating tax basis and normalization rules.
4. D&A and investment together: asset cohorts/useful lives, replacement versus
   expansion investment, acquisition perimeter and reconciliation to the
   engine's expense-aligned D&A/new-operating-investment definitions. An isolated
   ratio fade does not resolve the existing GOOGL weaknesses.
5. Working-capital cash needs: annual cash requirements consistent with revenue
   and operating drivers, translated into the engine's **full-revenue** ratio.
   Historical CFO movements are not automatic forecast inputs.
6. Terminal economics: assess the independent sustainable ratios and growth
   against year-eleven conditions; retaining an existing proposed ratio confers
   no new financial review.
7. Scenarios: decide which additional-year operating assumptions respond to the
   case and how. Current extra years simply inherit manually entered Base values
   unless explicitly overridden.

Each generated value would need rule/configuration version, source/observation
and information-review dates, exact operands, scope, judgment classification,
refresh diff and override-preserving adoption. These are policy decisions for
review, not financial defaults implemented here.

## Verification

- 253 frontend tests in 23 files passed with one worker and 20-second test timeout.
  The preceding full run found one obsolete literal expecting “Year-five EBIT”
  after the description became “Final-year EBIT”; its value assertion was retained
  and the complete suite rerun passed.
- 206 valuation tests, including seven new ten-year tests, passed. Independent
  rational calculations check all ten annual PVs, year-eleven terminal FCFF and
  year-ten exit discounting. Existing five-year tests remain passing.
- 66 API tests and 15 market/review tests passed. Additional live ten-year Gordon
  and exit API outputs matched the CLI's full calculation dictionaries exactly.
- TypeScript checking, production and prototype builds, and ten-year CLI summary checks passed. The prototype retains its existing chunk-size advisory.
- Actual Chrome/local API: empty extra-year validation, populated manual ten-year
  Update, both terminal methods, scenarios, 5×5 sensitivities, ten-year Full Model,
  and dotted markers (one DCF, two scenario plots). At 390×844 CSS pixels, no
  page horizontal overflow; chart panning and year selection remained available.
- Browser test inputs for years 6–10 were growth 5%, margin 29%, tax 21%, D&A 16%,
  investment 23%, WC 0.58%, and a separately tested 15× exit multiple. These were
  arbitrary software-test inputs, not researched forecasts or new preloads.
  The isolated tab was reloaded and returned to the unchanged five-year profile;
  no trial input/result file or browser download-delivery claim is retained.

The verified read-only API bundle has 109 files at
`/tmp/valuation-ten-year-20261031/runtime`; local API 8002 was restarted against
it (PID 81712 at verification), while Vite 5175 remained running. Frozen historical
records and the nine unset templates were not changed. No push or deployment.
