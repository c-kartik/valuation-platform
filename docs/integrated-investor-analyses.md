# Local sensitivity, reverse DCF and exploratory cases

## Scope and journey

The [workspace](http://127.0.0.1:5173/workspace/) connects selected manual case →
forward EV/optional equity → [Bear/Base/Bull comparison](integrated-investor-scenarios.md)
→ WACC × terminal-growth sensitivity → certified reverse DCF → explicitly created
exploratory case. Any complete selected individual case suffices for sensitivity
or reverse; a complete three-case comparison is not required. The [foundation](integrated-investor-workspace.md),
reference calculator `/` and separate fixture-only prototype at port 5174 remain.
Navy/gold presentation is shared; fixture outputs never stand in for API results.

This resumes uncommitted sensitivity work at `2d568271c446b7b85de6ea19c2a73be2f49cdef5`
(clean main before that work, ten ahead of local origin/main). Local-only milestone:
no publication, push, cloud calls, portfolio changes, evidence acquisition or actual
company forecast approvals. [Phase 1 remains paused](phase1-universe-pause-checkpoint.md).
All nine company templates stay unset. Software acceptance is not investment
readiness, complete claims coverage or certification of sustainable economics.

## HTTP and execution boundary

| Routes | Narrow request/result envelope | Existing engine |
| --- | --- | --- |
| `/api/v1/sensitivity/validate`, `/api/v1/sensitivity/run` | `investor-sensitivity-request-v1` / `investor-sensitivity-results-v1` | [Sensitivity reader/runner](phase2-sensitivity-workflow.md) |
| `/api/v1/reverse/validate`, `/api/v1/reverse/run` | `investor-reverse-dcf-request-v1` / `investor-reverse-dcf-results-v1` | [Reverse reader/certified solver](phase2-reverse-dcf-workflow.md) |

Both accept the existing legacy analyst envelope too. Investor versions require
existing investor v1/v2 source-case metadata: anonymous creation timestamp and
optional notes, not fabricated analyst rationale, evidence or approvals. Source
shape/strict parsing and financial validation are unchanged. The workspace submits
`source.kind=single_case` with the exact selected case and optional identical shared
bridge. Explicit analytical date is fiscal end; independently entered cutoff must
be on/after it and is unverified. CLI JSON remains compatible; new investor summary
branches faithfully identify anonymous preparation/notes. Original analyst summary
and JSON behavior remain available.

Validation parses/models only: no historical load, valuation, certificate, solve,
child spawn or result. Run revalidates and executes the existing engine inside
**one bounded child per whole grid/solve**, sharing the existing server admission
gate with forward/equity/scenarios. No browser fan-out, root-finding, queue or
partial-success fallback. The client gate covers all validation/run/retry paths.

Unchanged ceilings: **256 KiB request, 4096 JSON nodes, depth 24, 64 numeric digits,
absolute exponent/adjusted magnitude ≤100, 2 MiB result, 35s wall deadline, 30s
child CPU**, plus existing text/array/body-read/transport limits. Exact reverse
work remains in that terminable child: degree ≤5, derivative degree ≤4, exact
component precision 512, certificate extent 4096 and default maximum 128 iterations.
HTTP callers cannot tune the solver policy. Existing numeric/structural ceilings
bound rational operand sizes before solving; no larger limits were needed on the
measured samples below. Samples do not guarantee completion for every permitted
input; deadline, CPU, arithmetic, certificate and response failures still reject
safely rather than weaken certification. Existing cross-site/query rejection,
no-store, sanitized errors, disconnect/terminate/kill/reap and shutdown remain.
Audit restrictions are defense in depth, not an OS sandbox or distributed quota.

Private packaging adds only `sensitivity_inputs.py` and `reverse_inputs.py`:
**87 allowlisted files**, unchanged historical resources/hashes and dependencies.
A fresh immutable verified local bundle was built; only the identified review API
was restarted. Publication/deployment packaging is outside this milestone.

## Sensitivity review

Six range/step fields start blank, in percentage units: `10` means 10%, steps are
percentage points. Start/end must be ordered, positive step must reach the endpoint
exactly, with **1–11 explicit values per axis / at most 121 cells**. The visible
axis preview precedes explicit validation/calculation. No centered helper, company
grid, probability interval or economic range is selected automatically.

Only WACC and terminal g vary. Other annual rates, terminal operating ratios and
bridge/shares stay fixed; higher g changes terminal revenue/FCFF but does not add
supporting reinvestment automatically. Mixed g≥WACC cells retain null metrics and
reasons; all-invalid grids reject. The matrix labels WACC rows/g columns, exact
percentages, USD millions EV or qualified USD/share, and the submitted-case marker.
Arrow keys/Home/End move cell focus; the narrow-screen matrix scrolls internally.
Signed values and undefined zero-EV terminal contribution remain visible.

Inspecting a cell edits no case. Confirmed **Apply WACC/g** replaces only those two
fields in the selected case, stales dependent outputs and requires explicit forward
and grid recalculation. A separate confirmed exploratory action uses the same fork
mechanism as reverse. Invalid/stale cells cannot apply or fork. Full-precision
submitted inputs, returned components, dates, qualifications and provenance remain
in the expandable trace; display conversions/rounding use isolated Decimal only.

## Reverse review and certification

Targets, dates and lower/upper growth bounds start blank. Choose EV in **USD
millions** or qualified **USD/share**; transport uses base USD/scale 1. Signed/zero
targets are allowed. Target date must equal fiscal end; a manually entered price
is a target, not a live quote or authenticated observation. Per-share targeting
requires the existing complete bridge/share declarations, with no EV downgrade.

One constant annual revenue-growth rate **replaces all five rates**, at fixed
margins/tax/D&A/investment/full-revenue WC, WACC, terminal g/operating ratios and
selected bridge/shares. No alternate variable or automatic bound widening.
The unchanged interval-wide exact rational Bernstein certificate establishes
monotonicity before bisection. Success additionally requires existence, growth
bracket ≤1e−12, scale-aware residual tolerance and a fresh existing-engine forward
valuation. EV absolute residual floor is 1e−8 USD, shares 1e−10 USD/share, plus
relative tolerance 1e−12. These are technical controls, not financial assumptions.

The view shows target/date/units, supplied bounds, held-fixed scope, status/reason,
certificate direction, iteration/evaluation counts and final bracket. Only
`SUCCESS` shows current solved growth, achieved metric, signed residual, tolerance
and exploratory action. `UNREACHABLE_TARGET`, `FLAT_RESPONSE`,
`UNIQUENESS_NOT_CERTIFIED`, `ITERATION_LIMIT` and `NUMERICAL_VERIFICATION_FAILED`
retain diagnostics with **no solution**. Inconclusive certification does not prove
multiple roots. Earlier stale diagnostics are labeled; stale success exposes no
current solution/action. Full certificate and fresh forward result remain in JSON.

## Ownership, freshness and exploratory semantics

Each company/case owns grid settings, cutoff, output scope, reverse target/bounds/
dates, results and inspection state. A current individual EV is required to execute
analysis; validation remains independently calculation-free. Exact submitted/source
snapshots and reference Stage B must match before responses become current.

| Change/action | Effect |
| --- | --- |
| Operating/WACC/terminal edit | Selected EV/equity/grid/reverse stale; strict comparison stale only for Base/Bear/Bull edits |
| Grid settings/cutoff/scope | Only that case's grid stale |
| Reverse target/metric/bounds/dates | Only that case's reverse stale |
| Shared bridge/share edit | EV remains current; current operating grid cells retained but equity/share interpretations withheld; per-share reverse stale/cancelled, EV-only reverse preserved |
| Notes/name/navigation/comparison price | Financial outputs retained; original submitted trace stays unchanged |
| Switch/remove/replace during request | Cancel ownership and discard late replies; obsolete cleanup cannot unlock a successor |

Confirmed forks generate separate `Exploratory N` identities with creation time,
source name and submitted analysis provenance. Reverse forks change only five annual
growth inputs; sensitivity forks only WACC/g. All other assumptions, notes and the
company's shared bridge remain. No forward/analysis result is inherited. Explicit
forward calculation is required; original Base/Bear/Bull stay intact. Exploratory
cases are excluded from the strict three-case comparison and their operating edits
do not invalidate that financially independent comparison. There is no persistence,
scenario probability, automatic recommendation or account system.

Cancellation/unavailable/busy/error paths retain entries and require explicit retry.
Errors focus a relevant visible field or bounded issues region. Browser cancellation
is not a guarantee of immediate server cancellation; server admission still applies.
Overview cards summarize the selected current grid's tested axes and reverse status/
implied growth. Neither summary establishes a confidence interval or total-value bound.

## Verification — October 28, 2026

New checks for this checkpoint (prior acceptance documents remain attributed records):

- **179 frontend tests**: exact percentages/unit conversions, blank defaults,
  selected source/bridge, calculation-free validation, inspection/confirmation,
  per-case freshness, shared lock/cancellation, late/removed-case replies,
  unavailable recovery, reverse statuses, exploratory preservation and legacy UI.
  Both production and isolated prototype builds passed; the existing prototype
  large-chunk warning remains. No dependencies/build infrastructure added.
- **165 distinct focused Python tests**: 159 API/valuation checks, one added
  cross-anchor grid/CLI/arithmetic check and five preparation-preservation checks.
  Engine compatibility, invalid/all-invalid grids, zero/negative values, solver
  endpoints/unreachable/flat/inconclusive states, fresh verification, default
  iteration exhaustion, CPU/deadline/disconnect/cleanup and byte budgets covered.
  No full historical suite or new filing research. An interrupted test invocation
  used seven nonexistent module names; it was corrected, not counted as a pass.
- **4 full grid API/CLI comparisons**, **8 individual-cell CLI comparisons**,
  **6 reverse API/CLI comparisons** across all three anchors/both target scopes,
  and **6 fresh successful reverse-forward equalities** passed. **780 independent
  exact-rational comparisons** (444 grid +336 reverse) checked annual revenue/EBIT,
  operating tax, NOPAT, D&A/investment/WC/FCFF, discounting,
  terminal FCFF/value, PV/EV and signed bridge/shares. Tolerance:
  `1e−30 + 1e−46 × |reference|`; no duplicated valuation engine or float financial math.
- Four additional browser-captured sensitivity/reverse JSON results matched their
  CLIs exactly; six selected cells/solutions matched fresh individual CLI results.
- Actual Chrome at requested **1440×1000 and 390×844** exercised forward/scenarios,
  grid entry/calculation/inspection, cancel/confirm apply, stale overview/recalculation,
  per-case switching, reverse unreachable/recovery, qualified share solve, confirmed
  exploratory creation and fresh forward calculation. Keyboard cell navigation,
  invalid reasons/no apply, matrix scroll, focus return and unavailable API retry
  were checked. No horizontal page overflow observed. Screenshots remain outside
  the repository. Resized desktop is not mobile virtual-keyboard/full accessibility
  acceptance. Trial browser state and temporary inputs/results were cleared.

Sample bounded-worker measurements under unchanged default limits:

| Sample | Duration | Serialized response |
| --- | --- | --- |
| META/GOOGL/AAPL EV 11×11 grids | 4.207 / 6.389 / 6.353s | 180,641 / 205,325 / 205,821 bytes |
| AAPL synthetic equity 11×11 | 6.464s | 368,562 bytes |
| Six reachable reverse targets, both scopes/all anchors | 1.604–2.444s; 43 forward evaluations each | 52,717–250,385 bytes |
| Demanding reverse: 1e100 target/upper bound, −100% lower bound, 64-digit WACC separated from g by 1e−64 | 5.326–6.808s | 90,086–140,982 bytes; all `ITERATION_LIMIT`, no solution |

These are measured local examples, not universal work bounds, remote load tests or
production certification. No API ceiling was raised or grid size reduced.

Software inputs only: annual growth 10%, margin 20%, tax 25%, D&A 5%, investment
10%, full-revenue WC 2%; WACC 25%, g 5%, independently supplied terminal operating
ratios 20/25/5/10/2%. Browser tests explicitly copied terminal ratios once, applied
20% WACC/2% g, and used 100,000 USD-million EV /5,000 USD/share targets, plus an
unreachable negative EV target. Synthetic shared bridge: USD100m assets, USD40m
financing, USD10m claims, 20m synthetic common shares; existing awards explicitly
omitted. API tests use the retained synthetic example bridge as labeled. Cutoff
February 5, 2026 is only a software declaration. None are researched company
forecasts, actual bridge/share populations or permanent defaults. Only historical
revenue anchors are retained reported inputs; financial unknowns remain unresolved.

One old reverse preservation test pinned already-approved metadata adapters to a
pre-investor commit. Case/scenario adapter pins now use starting HEAD; original
forecast/discount/bridge/assumption/consumer byte pins remain. Sensitivity metrics
and reverse certificate/bisection ASTs remain pinned, allowing only envelope result
version selection. Legacy CLI JSON bytes are still independently compared.

Formulas, historical/frozen/source approvals, templates, prototype fixtures and
portfolio remain unchanged. No hosted resource, access or deadline was inspected
or modified. Review this local milestone before further features or publication.
Inspect listeners/process identities on 5173/5174/8000 before SIGTERM; preserve the
immutable API bundle while its review server runs.
