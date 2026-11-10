# Company-page layout options

## Option 1 — Continuous Open Canvas

Frozen before the Chapter bands change on November 10, 2026.

- Source: GitHub tag `layout-option-1`, branch `layout/option-1`, commit `09ffc1d`.
- Portfolio deployment: matching tag/branch, commit `db98f18`.
- One continuous company page with individual feature navigation and the shared
  cash-flow period selector. This remains a recoverable revision on GitHub.

## Option 2 — Chapter bands (deployed)

The approved Chapter bands design groups the same existing features:

1. Financials: Historical trends (Cash generation, Revenue & profit, Margins)
   and Revenue mix, including their chart interactions and drill-downs.
2. Cash Flow Analysis: earnings-to-cash bridge and capital allocation, controlled
   by the existing shared Annual / Quarterly / TTM selector. Inside PP&E retains
   its independent balance date; all reconciliations/source disclosures remain.
3. Valuation: all existing DCF assumptions, models, scenarios, sensitivity,
   FCFF/FCFE views, source qualifications and Excel export remain available.

- Source and portfolio: tag `layout-option-2`, branch `layout/option-2`.
- Production: https://kartikchaturvedi.com/valuation/ .
- `main` carries Option 2. The numbered options are GitHub revisions; no public
  layout switcher or alternate calculation/data path has been introduced.

The layout changes only presentation and navigation, reusing the existing
components. No source financial packages, original Python modules, browser
valuation engine, workbook builder or financial calculations changed.

Validation: browser production build and all 508 frontend tests passed. Desktop
and 390px phone checks confirmed chapter navigation, all historical metric views,
shared cash periods and PP&E availability. Three chapter bands fit the narrow
viewport without horizontal page overflow. Source/data preservation was checked
against `layout-option-1` before publication.

## Saved revisions

Both repositories preserve annotated tags and snapshot branches with the same
labels. Use the source repository for implementation and the portfolio repository
for the matching deployable static files. Preserve current unrelated work when
reviewing or restoring a saved layout; changes to presentation do not authorize
changes to financial inputs or methodology.

FY2021 Q1 coverage correction: the expanded chart data and source audit are
recorded in `docs/fy2021-history-extension.md`; original layout tags stay frozen.
