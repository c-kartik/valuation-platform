# Connected workspace — bounded performance review, October 29, 2026

## Scope and correctness boundary

This review starts from clean, synchronized main `d4d1d7c`. It follows the
[private staging acceptance](connected-workflow-staging-acceptance.md), whose
measurements/checks remain historical records. Only authenticated
`valuation-api-staging` in `kartikchaturvedi-website` (378340095652), us-central1,
is authorized for update. [Phase 1 remains paused](phase1-universe-pause-checkpoint.md).
Software responsiveness is separate from financial completeness/investment readiness.

The demonstrated bottleneck is repeated preparation of the identical retained
revenue/source/approval snapshot, rather than DCF arithmetic or exact certification.
Local cProfile: 5×5 executed 26 anchor loads (2.952s of 3.049s); ordinary reverse
executed 43 loads (5.108s of 5.275s). Profiling overhead makes these diagnostic
figures unsuitable for comparison with ordinary request latencies.

`case_inputs._prepare_case_runner` now creates a private request-local closure over
one source-validated, immutable RevenueAnchor. Sensitivity and reverse use it for
reference and every candidate. Each candidate is still strictly reparsed/model-
validated, must declare the identical anchor, and executes the original shared
A→B→C body. Standalone `run_case` still loads sources on every call; subsequent
requests always reload/revalidate. There is no cross-request cache or persistence.
API manifest verification remains per child, with read-only bundled resources.
Source mutation midway through an external CLI request is not monitored: one
validated snapshot intentionally binds the entire request. No issuer treatment,
source hash, approval, financial formula, precision, solver proof/tolerance, fresh
final forward evaluation or unsuccessful status changed.

The client now distinguishes timeout from busy and unavailable, including its
50s waiting deadline and HTML 504 gateways. Inputs remain available for explicit
retry. Cancellation discards client results; it does not promise immediate server
termination. Source/owner revision guards, immediate tool-specific running text,
shared gate and stale-result behavior are retained. Sensitivity recommends three
explicitly entered values per axis (3×3); larger grids are advanced. All axes remain
unset. There is no truncation, cap reduction or new solver/API work bound.

## Comparable temporary benchmark

All nine fixed requests use **GOOGL's actual retained FY2025 revenue anchor with
arbitrary synthetic software-test economics**, not researched company forecasts.
Annual growth/margin/tax/D&A/investment/full-revenue WC are 10/20/25/5/10/2%; WACC/g
25/5%; explicit terminal margin/tax/D&A/investment/WC 30/20/4/9/1%. Qualified bridge
is +10+2−20−3 **USD**, four actual shares, with synthetic provenance/omissions.
Grids use explicit Decimal axes WACC 20–30%, g 3–5%, each evenly divided into
3/5/11 points. No company values become defaults. Reverse EV/share targets come
from a known 7.3456789123% constant-growth forward run, bounds 0–20%.

The demanding diagnostic uses bounds −100% to 1e100 (fraction), target 1e100
USD/share, g 25%, and WACC 25% plus 1e−64 (fraction); its intentionally extreme
permitted inputs exhaust 128 iterations, exposing no solution. The unsuccessful
EV target is −100,000 USD. Tests separately cover flat/uncertified/verification-
failure outcomes. Temporary requests/results remain outside the repository.

| Request | Local before s | Local after s | Private baseline s |
| --- | ---: | ---: | ---: |
| Forward EV | 0.050742 | 0.048899 | 9.087694, first after idle |
| Forward equity | 0.046289 | 0.048143 | 2.389371 |
| 3×3 equity grid | 0.486929 | 0.061648 | 4.271124 |
| 5×5 equity grid | 1.339025 | 0.085400 | 8.243249 |
| 11×11 equity grid | 6.380636 | 0.286770 | 26.821809 |
| Reachable reverse EV | 2.068700 | 0.072676 | 10.586593 |
| Reachable reverse share | 2.148927 | 0.115984 | 10.914059 |
| Demanding reverse | 6.516545 | 0.245338 | 28.380785, ITERATION_LIMIT |
| Unreachable reverse | 0.165829 | 0.047782 | 2.415589, UNREACHABLE_TARGET |

These are individual sequential samples, not distributions, worst-case guarantees,
production sizing or load tests. Local totals include strict preparation (~0.25–
0.77ms); cloud totals include loopback authenticated proxy/network/child execution/
JSON transfer. Baseline logs show an autoscaling instance start at 12:55:55.629763
UTC and Uvicorn ready at 12:56:01.551824 UTC, consistent with the first-request
cold penalty; following requests were sequential/warm. No forced scale-down.
Cloud baseline complete outputs equal the saved local-before outputs.

Temporary local phase timers for 5×5: source preparation 1.261→0.047s,
financial forecast/discount/bridge calls ~0.010→0.009s, component serialization
~0.007→0.006s, final JSON encoding ~0.004s. Ordinary share reverse: source
2.086→0.053s; certificate ~0.000292→0.000273s; JSON ~0.005s. Manifest verification
was 0.016–0.018s locally. Timers overlap execution totals and are not additive
cloud CPU measurements; parsing, validation and wrapper work account for the
remainder. Cloud phase attribution is inference from local instrumentation,
not instrumented production tracing.

## Local verification and preserved scope

The focused valuation checks cover strict declarations/anchor mismatch, one load
per grid/solve on all three retained anchors, reload and invalid-source failure on
later requests, unchanged standalone behavior and candidate recalculation.
Preservation checks retain original formula/consumer byte pins; the extracted
shared execution body and all other case functions match starting ASTs. Wrapper
AST comparison normalizes only envelope selection and request-local preparation/
call routing; certificate, metrics and bisection remain pinned. Fresh verification
fault injection still withholds a solution. No source/approval treatment changed.

188 valuation tests passed. 57 focused API/preview/preparation tests passed,
including unchanged validation-only behavior, legacy case/scenario compatibility,
request/result/parser/CPU/deadline limits, real child disconnect/cancel/kill/reap,
busy and recovery. 187 frontend tests passed, followed by 87 affected tests after completing
HTTP/client timeout handling. Production and prototype builds passed; the existing
prototype >500 kB chunk warning remains. No historical corpus research/full suite was run.
Nine complete benchmark results matched CLI JSON; six selected grid cells matched
individual forward runs, both successful reverse results matched fresh forward
runs, and **566 independent exact-rational component comparisons** passed with
`1e−30 + 1e−46 × |exact reference|` tolerance. The CLI's unsuccessful reverse exit
code 3 remains intentional. All nine templates retain 37 UNSET numerical inputs
per case, including each scenario; no actual case/output/default is saved.

## Private staging follow-through

Local verification precedes the scoped code push, one existing-process Google
remote build and private-only image update. Final release bindings, comparable
cloud-after measurements, browser recovery checks and bounded review expiry will
be recorded after verification. Until that addendum, the baseline revision is
`valuation-api-staging-00002-q5m`, digest
`sha256:fbca75a98dd81393d5056aa83b44ec259590a8f4dc7d4dc8a3364b7009d1f970`;
service IAM is empty (`etag: ACAB`), invocation protected.

No resource/identity/IAM/billing/cap/public-service/Hosting/Firebase/Netlify/DNS/
portfolio change is part of this milestone. Existing ceilings remain 1 vCPU/1 GiB,
concurrency 1, min 0/max 1, 50s Cloud Run, 35s application wall/30s child CPU,
256 KiB requests/2 MiB results, 11×11 grid and 128 default reverse iterations.
