# Open Canvas company page

Deployed and live-verified at [the valuation page](https://kartikchaturvedi.com/valuation/).
Release identifiers and preservation checks: [release receipt](open-canvas-release.json).

The user approved the full-page Open Canvas mockup on November 9, 2026 and
requested implementation with real data and existing calculations. This release
changes presentation and interaction only; it adopts none of the mockup's
illustrative share counts, equity adjustments, scenario calculations or history.

## Data and calculation boundary

- Quarterly trends and the cash-flow bridge consume the unchanged, validated
  `frontend/public/research-data/{GOOGL,AAPL,META}.json` reporting packages.
- The combined annual revenue/FCFF line chart consumes the existing `chartRows`
  contract from `OperatingCharts.tsx`, using the matching catalog history and
  the selected, submitted `Result`. It retains all available historical years and
  all five or ten forecast years. A mismatched history falls back to its annual
  anchor; missing FCFF stays unavailable and creates a gap.
- Both series use one signed USD axis. Solid history and dashed forecasts have a
  shaded boundary. Revenue carries its historical anchor into the forecast;
  FCFF does not connect across its historical/forecast methodology change.
  Changes within historical FCFF basis also split the line. Curves are display
  guides through observations, with exact amounts retained in the source table.
- Axis positioning uses the existing Decimal `financialAxis`; only normalized
  screen coordinates are converted to JavaScript numbers. Chart interactions
  never submit or edit financial inputs. Existing submitted-margin inspection
  remains available from assumption controls.
- The per-share headline comes from the existing, validated `AppleAnalyst` or
  `CompanyAnalyst` output, bound to company, scenario, current operating result
  and current analyst status. Pending, stale, failed or unsupported analyst
  outputs do not appear as a current fair value. The page falls back to the
  actual enterprise value. A current manual Stage C override is explicitly
  labelled separately. No valuation formula is implemented in the page.
- The original Python modules, JavaScript calculation engine, preparation
  policies, catalog/annual input packages, accepted analyst conventions and
  model dates remain unchanged. A newer quarterly report does not re-anchor DCF.

## Interaction contract

The company page leads from quarterly history to its cash-flow bridge, then the
DCF canvas and model workspace. Company search and portfolio-home navigation
remain available. Assumptions, scenarios, sensitivity, full model, historical
cash flows, paired FCFF/FCFE and source qualifications retain their existing
components and actions. All full-model and equity editors remain available.

Quick WACC and terminal-growth/exit-multiple controls stage local drafts. Releasing
a pointer, completing a keyboard adjustment, or choosing **Apply rate changes**
submits only the changed rates through the existing `useWorkspace.updateValuation`
action and existing validation. Pending edits do not change the displayed result;
calculation failures remain explicit. Slider extents are UI exploration bounds,
not economic recommendations or new model defaults. All assumptions remain
editable through the full editor. Switching company/scenario resets the quick
control draft to that session. No request is made for each pointer-move event.

Excel export continues to use the existing workbook writer and immutable
click-time capture. Unapplied quick-rate edits are recorded as a pending model
editor draft, preserving submitted results and source inputs separately.

## Verification

- Full frontend suite: **480 tests, 42 suites**, including unchanged engine parity
  and financial checks. Six new tests cover retained/returned chart observations,
  absent/mismatched history, FCFF gaps, 10-year selection and margin inspection,
  quick-rate submission, existing required-input validation, exportable pending
  drafts, source immutability and busy/source-change handling.
- Existing workspace navigation tests now refer to the Assumptions tab and actual
  line geometry; current controls remain accessible throughout other views.
- Browser checks use actual GOOGL/AAPL/META packages and results: Base FCFF/share
  **$125.91 / $175.46 / $374.70** and EV **$1.42tn / $2.58tn / $944.60bn**.
- Alphabet quick WACC 8.94% → 8.95% produced **$125.68/share** through the unchanged
  engine; the accepted 8.94% rate was restored afterward.
- Actual Apple sensitivity and Meta scenarios, fiscal history selection,
  original model-editor open/cancel and company switching were exercised.
- META Base Excel downloaded through the page and reopened successfully: six
  expected sheets, correct company/scenario, current operating calculation and
  preserved model state. No workbook writer change was needed.
- Desktop and 390px browser checks include the DCF view and reporting bridge;
  no horizontal page overflow was observed. These are responsive browser checks,
  not physical iPhone/Safari acceptance.
- Asset verification retains 15 static assets, 396 original Python files and
  128 engine fixtures unchanged. Public-data and engine source diffs are empty.

The website remains a research/modeling portfolio tool. The broader universe,
market-data scope, refresh cadence and financial conventions are not expanded by
this UI release.
