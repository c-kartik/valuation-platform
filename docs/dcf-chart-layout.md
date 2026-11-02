# DCF chart layout and chronological CAGR

User-scoped refinement, 2026-10-31. Supersedes the historical signed-change-only
caption and the DCF above-chart legend/caption composition from the earlier
chart/history update. It retains the reported model anchor and exact returned data.

## Current refinement — one bottom-left readout, November 2

At the user's follow-up direction, the DCF selected-year line now replaces the
bottom-left Revenue/FCFF/Reported legend. It appears only once, below the graph:
`FY2027 · Forecast`, the Revenue swatch/value and FCFF swatch/value. Hover, tap and
keyboard year selection still update it. The unit/CAGR context remains at the
right (wrapping below on phone). Scenario case legends remain intact.

The former top-left readout is removed and its empty header space reclaimed;
sidebar inspection retains a fixed internal caption slot and reserved right axis.
No financial operands, calculations, source disclosures or unknowns change.
Verification: 16 affected chart/inspection checks, TypeScript and production build
pass. Actual desktop/390px phone review confirms one readout, no duplicate DCF
legend, updated reported/forecast values and no horizontal overflow. Screenshots:
this chat's `outputs/chart-footer-readout/`. Viewport override reset after review.

## Earlier refinement — compact overlay, November 2

The selected-year DCF readout now floats at the top left inside the chart canvas.
The external year/Basis/value panel and external inspection-caption spacer are
removed. The overlay shows `FY2027 · Forecast` or `FY2025 · Reported`, followed by
Revenue and FCFF values using a `B` suffix. Current-year header figures and scenario
chart readouts use the same suffix. USD context remains in the legend, accessible
chart title and exact-value titles; unknown historical FCFF remains Unavailable.

Reported bars, including the retained anchor, now use the same width as each
forecast bar: 27% of a year step for the DCF, 12% for grouped scenarios. Every
monetary bar has a subtle 1.5px horizontal/vertical corner radius. Heights retain
the original signed values and zero-inclusive domains. Region labels are
`Reported` and `Forecast`, with no lowercase history caption or unit suffix.

The 520/450px DCF canvas retains a fixed internal header area for the overlay and
sidebar inspection text. The right percentage-axis gutter remains permanently
reserved; showing the margin line changes neither bar coordinates nor plot size.
On phone widths the overlay wraps to two lines without horizontal page overflow.
Existing year hover/tap/keyboard selection, CAGR guides, source disclosures and
five-/ten-year markers remain. Scenario comparison keeps its three-case table.

Verification: all 270 frontend tests across 24 files, TypeScript, production and
prototype builds pass (existing prototype chunk advisory only). Updated checks
cover equal widths/rounded corners, in-chart DCF readout placement, capitalized
labels, signed B values and missing observations. Actual localhost desktop and
390px phone review confirms compact values, no overflow and stable margin-hover
geometry. Scenario Revenue/FCFF comparison still renders. Screenshots are in this
chat's `outputs/compact-chart-overlay/`; viewport overrides reset after review.
No calculations, source/preparation records, profiles, approvals, API contracts
or valuation origin changed. Phase 1 remains paused; no push or deployment.

## Earlier display and interaction

- Exact year Revenue/FCFF readout remains above the chart. The legend moves below
  the combined DCF plot, including USD billions and reference-year context.
- Remove the visible Revenue & FCFF heading, Shared USD billions axis heading and
  per-metric guide-caption block. SVG accessible title retains the metric/unit.
- DCF plot height increases from 382 to 520 layout pixels (450 below 500px wide).
  Forecast bars widen from 19% to 27% of a year step and the intra-pair gap reduces
  from 3% to 2%; reported bars widen from 28% to 42%. All years still fit the
  available width. Signed values keep their shared zero-based, unclipped domain.
- Selected-year endpoint guides place a white-backed CAGR label above the line's
  midpoint, not above the selected bar. Horizontal bounds keep labels within the
  plot; exact interval, metric and endpoints are available in the label title.
- Historical selection: earlier selected year is the starting value; reported
  anchor is the ending value. Forecast selection: anchor starts the comparison.
  Formula: `(ending / starting)^(1 / positive fiscal-year intervals) - 1`.
  Thus FY2024 revenue 350.018bn to FY2025 402.836bn displays 15.09% CAGR rather
  than a negative reverse comparison. Genuine chronological declines remain negative.
- No CAGR at the anchor or with unavailable/zero/negative endpoints. Missing
  historical FCFF stays unavailable. Existing exact readout, source disclosures,
  full-year mouse/tap/keyboard targets, forecast and ten-year boundaries remain.
- Scenario layout is retained; shared endpoint descriptions now also compare
  earlier-to-later years. No extra scenario charts or assumptions are introduced.

## Boundaries and verification

No engine/API/schema changes, new inputs, issuer source preparation, source
approval or resource-pin changes. The FY2025 analytical origin and FY2026E
presentation remain. Extra years 6–10 are still manual; Phase 1 stays paused.

- Focused chart/axis verification: 13 tests pass, covering chronological historical
  and forecast CAGR, true declines, missing/nonpositive endpoints, isolated Decimal
  context, floating label geometry, compact extreme annotations, tighter bar gaps,
  below-plot legend order, removal of the caption block, keyboard/tap synchronization
  and a fitted fifteen-year narrow plot with the ten-year boundary retained.
- TypeScript and production/prototype builds pass. The existing prototype chunk
  advisory remains. No dependency or runtime-bundle changes.
- Actual localhost desktop and 390px phone review: FY2028 shows 19.63% CAGR from
  FY2025; FY2024 shows 15.09% CAGR through FY2025. Floating labels sit above the
  lines; the exact Revenue/FCFF readout and legend retain their units. No horizontal
  overflow (phone chart width/scroll width both 328px). Both scenario plots still
  render after navigation; returned financial values remain unchanged.
- Previews are saved in this chat's `outputs/dcf-chart-layout/` directory. Viewport
  overrides reset after review. No trial assumptions entered, push or deployment.
- Final full frontend regression suite: 263 tests across 23 files pass.
