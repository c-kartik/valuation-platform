# Sidebar chart inspection

Implemented November 2, 2026 after approval of the **Focus on hover** mockup.
This is a transient DCF display state. Existing sidebar clicks still open their
respective assumption editors.

## Behavior

| Sidebar row | Inspection |
| --- | --- |
| Revenue growth | Emphasize forecast revenue bars and their endpoint guide. |
| Operating margin | Dim monetary bars and overlay submitted annual operating margins, with a right percentage axis. |
| Cash flow conversion | Emphasize forecast FCFF bars and their endpoint guide when available. |
| Forecast period | Emphasize the forecast window and add a bracket above it. |
| Discount rate | Highlight EV and the PV reconciliation; explain that undiscounted operating paths are unchanged. |
| Terminal value | Highlight the terminal boundary, final-year input and terminal PV contribution; distinguish perpetual growth from exit EV/EBIT. |

Mouse entry and keyboard focus use the same preview. Leaving restores the other
active input source, if any. Preview is suppressed while an editor is open and
cleared across company, case or analysis-view changes. Cancel retains existing
focus restoration. Preview adds no calculation request or draft mutation.

## Stable chart and financial boundary

The DCF plot always reserves its right-axis gutter, inspection-caption height and
margin legend footprint. Showing the axis changes neither plot bounds, year hit
targets nor bar positions/sizes. The separate percentage domain never rescales
the USD bars. The existing selected-year Revenue/FCFF readout, chronological CAGR
guides, solid colors, below-chart legend and five-/ten-year boundaries remain.
Scenario plots retain their existing layout.

`chartInspection.ts` matches each returned fiscal-year label to the corresponding
`submitted_inputs.forecast_years[].operating_margin`. It uses that exact submitted
fraction, not an unsaved draft or EBIT/revenue reconstruction. All submitted years
are shown (five or ten). Historical margins are not inferred. Missing or invalid
observations remain gaps; signed and above-100% margins remain in the independent,
zero-inclusive percentage domain. Compact labels retain exact operands in titles.
Stale results explicitly identify their previous submitted assumptions.

No financial formula, API/schema, source profile, resource pin, issuer treatment,
approval, nine unset templates or historical FCFF gap changes. Extra-year inputs
remain manual. Phase 1 remains paused. No push or deployment.

## Verification

- All **270 frontend tests across 24 files** pass, including six new chart tests
  and one workspace interaction regression. Coverage includes stable geometry at
  328/960px, five/ten years, all six previews/reset, submitted precision, null gaps,
  signed/extreme margins, stale results, scenario preservation, request counts,
  editor focus and case/view isolation.
- TypeScript, production build and prototype build pass. The existing prototype
  chunk-size advisory remains; no dependency or runtime-bundle change.
- Actual localhost GOOGL review: operating-margin focus shows FY2026–FY2030
  31.81%, 31.10%, 30.40%, 29.70%, 29.00%. Desktop SVG bounds were identical before
  and during inspection. At 390px phone width, margin/cash previews retain identical
  plot boundaries and every bar coordinate, with no horizontal page overflow.
  Clicking margin opens the populated FY2026 margin field; Cancel restores focus.
  Browser review exercised keyboard focus (the same preview path); mouse handlers
  are covered by the interaction tests. No trial assumptions were entered.
- Screenshots: this chat's `outputs/sidebar-chart-inspection/desktop-margin.png`
  and `phone-margin.png`. Viewport overrides reset after review.

Local review: <http://127.0.0.1:5175/workspace/>. Hover a sidebar row, or tab to it.
