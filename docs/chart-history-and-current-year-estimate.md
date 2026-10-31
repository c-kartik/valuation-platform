# Chart fit, five-year history and FY2026E display

October 31, 2026. Scoped UI/history projection update; Phase 1 remains paused.

## Delivered behavior

DCF and scenario charts use the measured container width rather than an 820px
minimum or a 95px-per-year minimum. All bars fit without horizontal chart panning.
Year labels shorten on smaller screens and rotate on very narrow charts; every
year retains its full accessible label, tap/focus target, arrow navigation and
exact readout. Units, zero baseline, signed values and submitted amounts do not
change. Ten-year charts retain the dotted boundary after forecast year five.

The historical projection now selects up to five consecutive compatible reported
annuals, FY2021–FY2025 for retained META/GOOGL/AAPL. Existing source identity,
accepted-value, undimensioned occurrence, unit and period checks still apply;
the window stops at a gap. No source packages, approvals or templates change.
The fixed catalog response ceiling increases from 64 to 80 KiB to accommodate
six additional source-bound revenue observations (actual catalog: 68,564 bytes).

The user selected **show FY2026E while retaining the reported FY2025 anchor**.
The header shows revenue and FCFF for the selected case's submitted estimate in
the profile information-review year. It is explicitly labelled E/estimate, keeps
stale status when appropriate and identifies FY2025 as the reported anchor.
Values come from the returned result; typing in a draft cannot change this card.
Other companies without a submitted starting profile do not acquire a fabricated
current-year estimate. This does not move valuation timing or forecast labels.

## Why historical FCFF remains unavailable

The former chart data projection deliberately populated only revenue and null
FCFF. This is an integration/financial-definition gap, not a claim that Alphabet
had no cash flow. FCFF is a derivation, not a single reported filing fact.

The retained GOOGL preparation already identifies reconciled CFO and cash PP&E,
but complete expense D&A is unresolved. CFO PP&E depreciation and finance ROU
amortization cannot automatically be summed as complete, non-overlapping expense
D&A. Historical tax, SBC, nonoperating cash, finance additions and acquisition/
capital-creditor scopes need a named reconciliation to the forecast definition.
Reported CFO minus cash PP&E is a useful separate FCF measure; displaying it as
this model's FCFF would silently change the definition. No zeros, forecast ratios
or unsupported estimates fill historical bars. The displayed gap states why.

Next financial work: prepare a five-year source/operand bridge, choose the
historical FCFF tax/lease/SBC/nonoperating treatment explicitly, reconcile it to
CFO, and publish values with provenance and any bounded limitations. No historical
financial sufficiency or new economic convention is approved by this UI update.

## FY2026 estimate basis checked

The existing preload already estimates full-year FY2026 from reported nine-month
revenue plus an estimated Q4. The versioned rule is:

`357269m + 113828m * 127577m / 102346m = 499158.617141852…m`

The nine-month and current/prior Q3 figures are in the
[Q3 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000084/goog-20260930.htm).
Prior Q4 revenue is in the
[Q4/FY2025 earnings release](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000012/googexhibit991q42025.htm).
This quarter-momentum extension is an estimate, not management guidance or a
reported annual. The existing policy's acquisition and seasonality limitations
remain. The FY2026 FCFF estimate additionally uses configured expense D&A,
operating tax, investment and working-capital assumptions. It is not a
nine-month reported FCFF extrapolation. See [preload policy](googl-preload-methodology.md).

FY2025 is the reported anchor year; Base is the central scenario. These are
different concepts. Moving the valuation origin to FY2026E would instead require
an estimated-anchor contract, FY2027 onward forecasts and a timing/stub-period
decision. The user chose to retain the current origin.

## Verification

- 254 frontend tests in 23 files pass, including a fifteen-year narrow-container
  case and a hidden-section zero-width observation regression.
- 15 review/history and 66 API tests pass. Tests verify five source-bound years,
  stop-on-gap behavior, exact retained revenue and catalog response bounds.
- TypeScript and both production/prototype builds pass. The prototype's existing
  chunk-size advisory remains; no dependencies were added.
- Actual desktop (1440px) and phone (390px) DCF/scenario checks confirm chart
  scrollWidth equals clientWidth, exact year selection and synchronized scenario
  selection. Mobile readout tables also fit without horizontal scrolling.
- Local API serves the new verified read-only 109-file runtime at
  `/tmp/valuation-five-year-history-20261031/runtime`; all allowlisted bytes match
  the repository. API PID82982, Vite PID99992; review on port5175.
- No valuation formula, profile policy, frozen record, approval, resource pin or
  unset template changes. Nothing pushed or deployed. Historical FCFF remains
  explicitly unfinished, not silently replaced by reported FCF.
