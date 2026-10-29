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

All nine fixed requests use **GOOGL's actual retained FY2025 revenue anchor
(USD 402,836,000,000; calendar fiscal end December 31, 2025) with
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

| Request | Local before s | Local after s | Private baseline s | Private after s |
| --- | ---: | ---: | ---: | ---: |
| Forward EV | 0.050742 | 0.048899 | 9.087694, first after idle | 2.644466 |
| Forward equity | 0.046289 | 0.048143 | 2.389371 | 2.673571 |
| 3×3 equity grid | 0.486929 | 0.061648 | 4.271124 | 2.796010 |
| 5×5 equity grid | 1.339025 | 0.085400 | 8.243249 | 3.056299 |
| 11×11 equity grid | 6.380636 | 0.286770 | 26.821809 | 3.613885 |
| Reachable reverse EV | 2.068700 | 0.072676 | 10.586593 | 3.062685 |
| Reachable reverse share | 2.148927 | 0.115984 | 10.914059 | 3.118356 |
| Demanding reverse | 6.516545 | 0.245338 | 28.380785, ITERATION_LIMIT | 4.070337 |
| Unreachable reverse | 0.165829 | 0.047782 | 2.415589, UNREACHABLE_TARGET | 2.856527 |

These are individual sequential samples, not distributions, worst-case guarantees,
production sizing or load tests. Local totals include strict preparation (~0.25–
0.77ms); cloud totals include loopback authenticated proxy/network/child execution/
JSON transfer. Baseline logs show an autoscaling instance start at 12:55:55.629763
UTC and Uvicorn ready at 12:56:01.551824 UTC, consistent with the first-request
cold penalty; following requests were sequential/warm. No forced scale-down.
Cloud before/after complete outputs equal the saved local-before outputs and
current CLI results. The new revision was already started by deployment before
its first measured request: 9.09→2.64s is **not** a controlled cold-start improvement.
The comparable warm 11×11 request improved 26.82→3.61s, ordinary reverse
10.59–10.91→3.06–3.12s and the demanding iteration-limit request 28.38→4.07s.
Forward requests show no established improvement; warm transport/child/import work
now dominates many samples. These observations support a compact 3×3 starting
interaction while leaving advanced 11×11 requests and all budgets unchanged.

Temporary local phase timers for 5×5: source preparation 1.261→0.047s,
financial forecast/discount/bridge calls ~0.010→0.009s, component serialization
~0.007→0.006s, final JSON encoding ~0.004s. Ordinary share reverse: source
2.086→0.053s; certificate ~0.000292→0.000273s; JSON ~0.005s. Manifest verification
was 0.016–0.018s locally. Three minimal local spawned-child entry probes
measured 0.043–0.049s, excluding application imports, manifest verification and
calculation; they do not measure Cloud Run cold startup. Timers overlap execution totals and are not additive
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

## Verified private release

| Binding | Verified value |
| --- | --- |
| Pushed code source | `377b5b837ce05c794becccb85d2757f8a762994d` — perf: reuse validated anchors within grid and reverse requests |
| Google build | `03e6bc36-0786-469b-a14a-dbbfad46622e`, SUCCESS; one remote build |
| Image | `us-central1-docker.pkg.dev/kartikchaturvedi-website/valuation-staging/valuation-api` |
| Immutable digest | `sha256:a55b17bd83ba521e95508085d46a414499cb8128d8b95298468ab70f47cf6507` |
| Service / revision / traffic | valuation-api-staging / `valuation-api-staging-00003-4mg` / 100% |
| Service ready | October 29, 13:04:18.917696 UTC / 17:04:18.917696 Dubai |
| Retained rollback | `valuation-api-staging-00002-q5m`, prior digest `sha256:fbca75a98dd81393d5056aa83b44ec259590a8f4dc7d4dc8a3364b7009d1f970` |
| Runtime manifest | 87 entries + manifest; canonical JSON SHA256 `58af8e7e0599acd57047c30f6011f9c71f954dc0c72f6d216f9ce94a20c1e820` |

The 92-file build context used the existing scoped builder, registry and source
bucket. Build took 23.577s, push 6.416s; no local Docker. Read-only registry
inspection verified linux/amd64, UID/GID 10001:10001, exact source label, and all
88 runtime COPY files' bytes/read-only modes against the local bundle (excluding
OCI whiteout metadata). Compressed layers total 68,542,383 bytes. Source archives,
images and previous revisions remain retained; no shared resource was deleted.

Runtime spec except image, revision settings and IAM were compared before/after:
unchanged identity `valuation-api-runtime@kartikchaturvedi-website.iam.gserviceaccount.com`,
gen2, request-based CPU, no startup boost, 1 vCPU/1 GiB, concurrency 1, min 0/max 1,
50s Cloud Run, one worker; 35s wall/30s child CPU, 256 KiB requests/2 MiB results,
11×11 grid and 128 default reverse iterations. Service IAM remains empty
(`etag: ACAB`), invoker checking enabled. Only image/source labels and generated
revision/operation metadata changed. Anonymous requests returned 403 before/after;
final actual `/health` was anonymous 403 and authenticated 200/ready. An initial
`/api/v1/health` probe was the wrong route (authenticated 404), corrected without
changing the application. GitHub workflows/hooks remained empty; pushes add no deployment.

Rollback, **only if separately needed/authorized**, uses the retained revision:

```sh
gcloud run services update-traffic valuation-api-staging \
  --to-revisions valuation-api-staging-00002-q5m=100 \
  --project kartikchaturvedi-website --region us-central1
```

All nine hosted benchmark results completed with unchanged JSON/statuses and no
timeout; demanding inputs still expose ITERATION_LIMIT/no solution, unreachable
inputs UNREACHABLE_TARGET/no solution. Cloud samples are not a proof that all
permitted requests finish within budget. No certification shortcut/work-bound
change was needed. Existing API tests separately exercised forced deadlines and
cleanup; these were not forced in Cloud Run.

Actual compiled-browser review observed immediate forward/grid/reverse running
states, no invented progress, shared disabled submission controls, explicit 3×3
recommendation with empty axes, mixed invalid cells and an advanced 11×11 grid.
Browser software inputs used the same annual rates, with explicitly copied terminal
20/25/5/10/2% ratios; the first mixed grid was WACC 2/16/30%, g 2/3.5/5%, and
the advanced grid used the benchmark 11×11 axes. These were separate software
trials, not actual-company economics or automatically selected defaults.
Real cancellation preserved axes, stale values stayed withheld after late completion,
and explicit retry completed on the new revision. The hosted grid and certified
reverse traces matched CLI JSON; two selected cells and a fresh reverse forward
run passed **165 additional independent rational component comparisons** using
the same tolerance. Solved-variable/bounds/held-fixed declarations were visible.
Stopping only the task proxy demonstrated sanitized unavailable failure, unchanged
target/bounds/dates, stale-result withholding and successful explicit retry after
restart. No browser application console errors were observed. Busy/timeout and
all-workflow ownership/late-response protections are additionally covered by the
frontend/API regressions; no fabricated cloud timeout/busy observation is claimed.
Browser cancellation does not establish immediate remote termination. Cloud Run
may queue before the per-process application admission gate. This review does not
certify every device, browser, concurrent workload or worst-case input.

Read-only Cloud Monitoring for the new revision had one nonempty startup sample
**6,739.868ms**, three memory-distribution means **6.0837%**, two CPU means
**15.26–37.45%**, and a partial **34.263s** billable-instance delta sum. Empty
zero-count distributions were excluded, rather than interpreted as zero use.
Sparse/lagged means are not peaks/RSS, per-request CPU, an invoice, comparable total
cost or production sizing. Earlier-revision metrics included the preceding review
and idle window; they are not a controlled cost comparison. The sampled new-revision
platform logs contained 30 entries/13 requests (12×200, 1×403), no ERROR+ entries
and no submitted-body/test-note/token markers; later recovery/health calls fall
outside that sample. No assumptions/tokens were added to application logging.

## Review session, cleanup and remaining decisions

The compiled frontend remains at <http://127.0.0.1:4173/workspace/> (existing
harness PID **84387**), using only official authenticated loopback proxy 8001,
PID **90964**, to `valuation-api-staging-ailnp3irra-uc.a.run.app` / revision
`valuation-api-staging-00003-4mg`. No local API fallback. The proxy started at
**13:07:53.659902 UTC / 17:07:53.659902 Dubai**, with a fixed 3,300s lifetime:
**14:02:53.659902 UTC / 18:02:53.659902 Dubai, October 29**. Its single in-memory
identity token expires at 14:07:53 UTC; it cannot refresh after task tooling removal.
This is the localhost review expiry, not public access or service deletion.
Frontend assets/logs contain no credentials. `/workspace/` and authenticated
`/health` returned 200; both loopback listeners were verified.

Browser trial state was cleared. Temporary cases/results/profiles/timers/build
context/SDK and task-only CLI credentials were removed; normal auth stores and
unrelated local API/workspace/prototype processes remain. The detached bounded
proxy retains its running executable mapping and token until exit; it needs no
credential files. No actual-company case/output or forecast policy was saved.

The final documentation is a later pushed checkpoint; it does not require a second
image build. Public artifact publication/authentication/abuse/operational acceptance
remain separately scoped, including the existing Firebase guard's rejection of
the multi-entry build. Cold starts and fixed child/import/transport overhead remain.
No financial or solver-contract decision is required by these samples; broader
performance guarantees or public migration would need separate scope. No resource,
billing/cap/IAM, Firebase/Hosting/public-service, Netlify/DNS/portfolio, financial
formula, historical/frozen/approval or nine-template change. Phase 1 remains paused.
