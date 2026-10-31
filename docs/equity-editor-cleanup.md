# Optional equity editor cleanup

User-authorized UI refinement, 2026-10-31. Replaces the compact workspace's old
bridge-only AssumptionEditor with a dedicated EquityEditor; other consumers retain
the shared legacy EquityFields presentation.

## Interaction

- Primary entries: Cash & investments, Debt, Other claims / adjustments, Shares
  outstanding. Amounts remain USD millions and shares remain millions of shares.
  Choosing an explicit claims amount reveals its numeric field; blank stays missing.
- Advanced adjustments & sources is initially collapsed, with a live count of
  required details. Share date, asset/financing/claims coverage, share basis,
  included classes, equivalence, awards and date/non-overlap declarations retain
  their existing meanings and validation. Component references are nested here.
- Calculate value per share validates the existing contract, opens/focuses missing
  details, saves entries through the existing workspace bridge revision path and
  runs the existing engine. Successful results focus the breakdown and collapse
  advanced settings. Failures retain entries; retry is explicit.
- Save inputs accepts incomplete drafts after numeric syntax checks, without a
  calculation. Cancel before either action discards local edits; after calculation,
  Cancel closes the panel and discards only subsequent unapplied changes. Closing
  during calculation cancels acceptance of the pending response; saved entries stay.
- The breakdown shows enterprise value, assets, debt, claims, equity, shares and
  per-share value from the returned Stage C result only. Before calculation,
  only the existing EV is populated; the rest show em dashes. Local edits and stale
  operating inputs mark previous results. Explicit omissions retain their unbounded
  effect qualification and exact returned values/basis remain available on demand.

## Boundaries

No financial formula, API/schema, issuer/profile resource, source approval, fiscal
anchor, coverage convention, share equivalence, award treatment, or template value
changes. No client-side valuation arithmetic, balance preloads or implied filing
verification. Phase 1 remains paused. Historical FCFF and years 6–10 preparation
remain unresolved. No new dependency, push or deployment.

## Verification

- Full frontend suite: 260 tests across 23 files passed. Affected Workspace,
  legacy EquityStep and equity contract checks pass (36 tests); final Workspace
  checks cover the completed interaction and success focus.
- TypeScript and both production/prototype builds pass. The existing prototype
  bundle-size advisory remains; no dependencies added.
- Desktop and actual 390px phone review: four initial controls, collapsed details,
  required-date focus, date/class/coverage/award declarations, successful localhost
  Stage C response, and retained manual/provisional qualification. Editor body fits
  its width and header/footer remain within the viewport. Screenshots are in the
  chat's `outputs/equity-editor-cleanup/` directory.
- Temporary software-test inputs cleared by reloading only the isolated review
  tab. Original GOOGL preload calculation restored; bridge fields remain unset.
- Engine/API/runtime bundle and resource pins unchanged. Shared preparation
  register guidance updated; issuer facts/records unchanged.
