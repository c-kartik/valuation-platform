# Phase 2 — explicit WACC × terminal-growth sensitivity

## Bounded request contract

`analyst-sensitivity-request-v1` has exactly `schema_version`, `sensitivity_name`,
`source`, `wacc_values` and `terminal_growth_values`. The source is either:

- `kind: "single_case"`, a complete embedded `case` using existing v1 EV/v2 equity
  intake, plus explicit `analytical_date` and `information_cutoff` ISO dates.
- `kind: "scenario_set"`, a complete embedded `scenario_set` and explicit
  `scenario_label` of Bear, Base or Bull. **The entire set is validated** under
  [existing comparability rules](phase2-scenario-workflow.md), even though only the
  selected case calculates. No implicit Base selection or external file resolution.

Analytical date equals fiscal-end anchor; cutoff is on/after it. These are submitted
information-scope declarations, not authenticated source-availability claims.
Each axis contains **1–11 explicit, finite, absolute fractional Decimal strings**,
strictly increasing and numerically unique (`"0.09"` means 9%, not a shift).
WACC must be >0 and growth >−1. No built-in grids, generated ranges or centres.
Malformed axes/requests fail before calculation. A pair g≥WACC is an **invalid
cell**, retained with status/reason and null metrics/changes. Mixed grids calculate
all valid cells; an all-invalid grid rejects without a successful result/file.

## Execution and result boundary

[sensitivity_inputs.py](../src/valuation_platform/valuation/sensitivity_inputs.py)
provides immutable `SensitivityRequest`, strict `read_sensitivity` /
`load_sensitivity`, `run_sensitivity` and deterministic `serialize_sensitivity`.
Validation reads no historical package and runs no financial calculations. Execution
revalidates the immutable request, runs the **original selected reference case**
separately, then submits fresh complete cases to existing `read_case` / `run_case`
for each valid cell. Only `wacc` and `terminal_growth` change. No DCF or bridge
formula is duplicated; existing Stages A–C calculate all financial components.

Annual operating inputs/flows, all five terminal operating ratios, bridge/shares,
conventions, dates and metadata stay fixed. Discount factors/PVs respond to WACC;
g changes terminal revenue **and FCFF**, as well as the Gordon denominator.
Reinvestment ratios do not adjust automatically to support each g; economic
consistency is an analyst review question. Operating-driver sensitivities and
reverse DCF are unimplemented.

`analyst-sensitivity-results-v1` retains the full submitted request, selected case,
source/scenario identity/dates, full original reference result and row-major grid.
Each valid cell identifies both exact rate strings, terminal revenue/FCFF/value,
explicit PV, terminal PV, EV, terminal PV/EV and optional equity/USD-share values.
EV-only cells have null equity/share fields. Each scope-appropriate value also
has absolute and fractional change from reference: `(cell − reference) / reference`
uses the **signed denominator**, null with explanation when reference is zero.
Terminal contribution is null when EV is zero; negative/over-100% ratios remain
unclamped with an explanation. JSON amounts are base USD, shares actual shares,
per-share values USD/share. Derived ratios/deltas use isolated Decimal precision
50/HALF_EVEN; JSON retains engine precision. Inputs/caller context are immutable.
Any execution failure rejects the whole result, with no partial file written.

The reference pair need not appear on the grid. If present, its cell reconciles to
reference. To reproduce any valid cell, take `selected_case`, replace only its
WACC/g with that cell's strings and execute the existing single-case interface;
no hidden defaults or external-path lookup is needed. Full source/provenance,
rationale and limitations remain in the reference/submitted payloads.

## CLI, examples and acceptance

[run_analyst_sensitivity.py](../scripts/run_analyst_sensitivity.py) validates by
default; `--run` calculates and `--format json|summary` defaults to JSON.
`--output` requires `--run` and exclusively creates a **new** file outside the
repository or under `output/`. Existing inputs/files and source/history paths are
protected. Ordinary stdout runs/validation write nothing. Existing single-case
and scenario CLI contracts/JSON are unchanged.

The summary labels company/case/scenario, fiscal/analytical dates/cutoff, reference
rates/EV and qualified share value, WACC-row/g-column EV matrix in USD millions,
and a separate USD/share matrix when applicable. Exact rate fractions accompany
rounded percent labels to distinguish closely spaced axes; invalid markers have
a legend. Display rounding is HALF_EVEN, eight decimal places for money/share,
two for percentages, in an isolated Decimal context. JSON retains full precision,
cell reconciliation/contributions/changes and complete traceability. Held-fixed
scope, terminal numerator effects, supplied limitations and omissions are disclosed.
Sensitivity is **not probability analysis or a fair-value range**.

Runnable [synthetic EV](../examples/valuation/synthetic-sensitivity-ev.json) and
[synthetic equity](../examples/valuation/synthetic-sensitivity-equity.json) requests
use the revenue-100 fixture, with mixed valid/invalid grids. No actual company grid,
forecast or output is saved. All six single-company templates stay 37-unset and
three scenario templates 111-unset; no previous trial assumptions become defaults.
Temporary integration uses synthetic forecasts/bridges with all three retained
revenue anchors, both scopes and explicit scenario selection; files are removed.

Engineering/synthetic integration is complete after the focused checks recorded in
[project status](project-status.md). The [qualified scenario acceptance](phase2-scenario-acceptance.md)
is a separate attributed record; **actual analyst sensitivity review remains
pending**, including user-selected grid/rationale, economic consistency, funding
and unbounded claims/awards qualifications. The
[completion checklist](phase2-completion-checklist.md) retains the remaining scoped
work. [Phase 1 expansion stays paused](phase1-universe-pause-checkpoint.md).
