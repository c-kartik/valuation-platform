# Phase 2 — bounded constant-growth reverse DCF

## Approved scope and request

`analyst-reverse-dcf-request-v1` contains exactly `schema_version`,
`reverse_dcf_name`, `source`, `target` and `growth_bounds`.
`source` uses the [sensitivity source shape](phase2-sensitivity-workflow.md):

- `kind: "single_case"`, complete embedded existing v1 EV/v2 equity `case`,
  `analytical_date`, `information_cutoff`.
- `kind: "scenario_set"`, complete embedded `scenario_set`, explicit
  `scenario_label` Bear/Base/Bull. The entire set must pass existing
  [comparability validation](phase2-scenario-workflow.md); no implicit Base.

No external file resolution, inheritance or price retrieval. Analytical date is
fiscal end; cutoff is a supplied ISO date on/after it, not authenticated evidence
availability. `target` requires `metric` (`ENTERPRISE_VALUE` or `VALUE_PER_SHARE`),
finite Decimal-string `amount`, `unit` (`USD` or `USD/share`, scale 1) and `date`
equal to analytical date. Negative/zero targets are allowed. Per-share targets
require a complete equity/share case, including explicit omissions; no EV fallback.
There is no conversion of a current price into a historical target.

`growth_bounds` requires finite fractional Decimal-string `lower`/`upper`, strictly
ordered and each ≥−1 under existing annual-growth domains. No company targets,
bounds or economic defaults. One **constant annual revenue-growth rate replaces
all five growth rates**; it is not a shift to the original path. Annual margins,
operating tax/D&A/investment/WC ratios, WACC, terminal g/all terminal ratios,
bridge/shares, dates and conventions stay fixed. All revenue-dependent dollar
amounts recalculate. The answer is conditional implied growth, not unique market
expectations, an economic endorsement or a price target.

## Exact interval-wide uniqueness certificate

[reverse_inputs.py](../src/valuation_platform/valuation/reverse_inputs.py) provides
immutable `ReverseRequest`, `read_reverse` / `load_reverse`, `run_reverse`,
`SolverPolicy` and deterministic `serialize_reverse`. Structural validation is
calculation-free: no history load, certificate, root search or result writing.
Execution revalidates immutable inputs and calculates the original reference via
existing `run_case`; every solver valuation also uses that same existing A/B/C path.
No engine equations or existing interface/JSON bytes change.

Let x=1+h≥0, where h is solved growth. Nonnegative revenue makes the existing
positive-EBIT tax convention homogeneous even for negative margins. At a fixed
anchor revenue, the **shared `_operating_year`** generates each annual FCFF
component and the fixed-g terminal component. These calls use precision 512 with
`Inexact` trapped; a rounded coefficient is never treated as exact. Dividing those
exact components by rational discount powers from the existing Stage B timing
produces coefficients for `EV(x)=Σ a_i x^i`, degree ≤5; the terminal contribution
joins the degree-5 coefficient. For per-share targeting, existing signed bridge
components supply the constant term and positive fixed shares scale coefficients.
This representation is for certification only, not an alternate valuation engine.

The derivative, degree ≤4, is converted exactly to Bernstein form over the full
user interval, with rational arithmetic. Its coefficients bound the derivative
throughout that interval by the Bernstein convex-hull property. If all coefficients
are nonnegative with at least one positive, the derivative is positive throughout
the open interval, proving strict increase including endpoints. The analogous
nonpositive condition proves strict decrease. Endpoint derivative zeros are
permitted; all-zero derivative means a flat response and no unique root.

Mixed signs mean **uniqueness not certified**, even if samples look monotone or
endpoint values cross the target. Multiple roots are not thereby proven; this
version can reject truly monotone cases whose Bernstein enclosure is inconclusive.
There is no subdivision/sampling fallback. Inputs whose Decimal digit count plus
absolute exponent exceeds 4096, or whose shared components cannot be calculated
exactly within precision 512, also fail certification conservatively. Engine
arithmetic failures remain execution errors. Certificates expose rational power/
Bernstein coefficients, derivative enclosure, interval, direction and rationale.

## Solver and numerical policy

The fixed CLI policy `bounded-bisection-v1` is **technical**, separate from all
financial assumptions:

| Control | Default |
| --- | --- |
| Growth bracket width | ≤1e−12, absolute fractional growth |
| Absolute residual floor | 1e−8 USD for EV; 1e−10 USD/share |
| Relative residual tolerance | 1e−12 |
| Residual acceptance | `abs(achieved−target) ≤ absolute_floor + relative × max(abs(target),abs(achieved))` |
| Iteration limit | 128; Python `SolverPolicy` permits 1–256 |
| Solver / existing forward precision | 80 / 50, isolated Decimal HALF_EVEN |
| Exact shared-component precision / extent cap | 512 with Inexact trapped / 4096 |

`SolverPolicy` exposes positive tolerances <1 as Decimal strings and iteration
limits to Python callers; actual settings are serialized. The CLI does not accept
financially hidden tuning/defaults or infer any target/bounds. Exact coefficient
work is rational after shared component generation; no floats.

After certification, exact mathematical endpoint residuals establish target
reachability. Exactly established endpoint solutions still receive a fresh
forward check; they are exempt from the iterative width requirement. Otherwise
bisection follows **existing forward metric evaluations**, respecting increasing
or decreasing direction. Rounded equality at an interior point is not an exact
root proof: it builds a small surrounding bracket and must pass the same final
existence/width/residual checks. Endpoint signs alone never establish uniqueness.

Success requires a unique mathematical root in the final bracket, width tolerance,
residual tolerance and **fresh forward evaluation** at returned growth. The exact
polynomial verifies final bracket existence, not reported valuation amounts or
bisection values. Unverifiable numerical brackets reject. Uniqueness refers to
the exact fixed-ratio mathematical model; precision-50 forward values approximate
it under the explicitly reported numerical policy, not literal uniqueness of a
rounded finite-precision staircase or unique market beliefs.

## Result statuses, CLI and output

`analyst-reverse-dcf-results-v1` retains submitted source/target/bounds, selected
case/scenario, original growth path, original full reference/provenance, held-fixed
scope, actual numerical policy, certificate, iteration/evaluation counts and final
bracket/endpoint diagnostics. Only `SUCCESS` includes `solution`: constant growth,
achieved metric, signed/absolute residual, applied residual tolerance, endpoint
flag and full fresh forward result (annual revenue/FCFF, PV/EV and equity/share if
selected). No unsuccessful iterate is exposed as a solution.

| Status | Meaning |
| --- | --- |
| `SUCCESS` | All uniqueness/existence/numerical tests passed |
| `UNREACHABLE_TARGET` | Certified monotone mathematical endpoints exclude target; no nearest-bound success |
| `FLAT_RESPONSE` | Exact derivative zero; no unique solution, including when target matches |
| `UNIQUENESS_NOT_CERTIFIED` | Inconclusive interval or exact-certification resource limit; not proof of multiple roots |
| `ITERATION_LIMIT` | Both numerical conditions were not satisfied within limit |
| `NUMERICAL_VERIFICATION_FAILED` | Growth resolution, exact final-bracket existence or fresh residual check failed |

[run_analyst_reverse_dcf.py](../scripts/run_analyst_reverse_dcf.py) validates by
default; `--run` explicitly certifies/solves. `--format json|summary` defaults to
JSON. Summary labels target/date/units, selection/timing/cutoff, original/replaced
growth, bounds/certificate/policy/counts/status, successful revenue/FCFF in USD
millions, EV, qualified USD/share, fixed classes/awards and omissions/limitations.
Display rounding is isolated HALF_EVEN; JSON retains full precision and traceability.

Exit **0**: structural validation or successful solve. Exit **3**: completed
unsuccessful solve with explicit status and null solution. Exit **2**: malformed
request, source/arithmetic execution or I/O/output error; no result file created.
`--output` requires `--run`, exclusively creates a new file outside the repository
or under `output/`, and rejects inputs, overwrites and protected paths. Completed
unsuccessful diagnostics may be explicitly saved with exit 3; a file is not a
success assertion. Ordinary stdout runs and validation write nothing.

## Synthetic verification and subsequent acceptance

Runnable [EV](../examples/valuation/synthetic-reverse-ev.json) and
[per-share](../examples/valuation/synthetic-reverse-equity.json) requests use only
the synthetic revenue-100 fixture. Targets 77.577060352 USD EV and 16.644265088
USD/share have a hand-checkable 10% root within explicitly supplied 0–20% bounds;
net bridge −11 USD and 4 shares are synthetic. Nothing transfers to issuer defaults.
Temporary synthetic forward-generated targets exercise all three retained anchors
in both scopes, including explicit scenario selection; inputs/results are removed.
Six single-company templates remain 37-unset and three scenario templates 111-unset.

Engineering/synthetic integration was complete within the checks in
[project status](project-status.md). [Actual sensitivity acceptance](phase2-sensitivity-acceptance.md)
is a separate attributed record. **Subsequent status:** [reverse analyst acceptance](phase2-reverse-dcf-acceptance.md)
is complete with economic qualifications, and the [final three-company checkpoint](phase2-completion-checkpoint.md)
closes scoped Phase 2 software acceptance. Operating-driver sensitivities are
**DEFERRED, not a closure blocker**. [Phase 1 remains paused](phase1-universe-pause-checkpoint.md).
Claims, awards, funding, settlement and asset-accessibility limits are not solved
by a certified implied-growth calculation. See the [completion checklist](phase2-completion-checklist.md).
