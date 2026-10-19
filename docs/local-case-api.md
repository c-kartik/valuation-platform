# Local single-case API

## Scope and local operation

This is a local-only FastAPI boundary over existing `read_case` / `run_case`.
It supports `analyst-case-v1` EV and explicit `analyst-case-v2` equity/share without
changing schemas, formulas, conventions, historical approvals or company templates.
[Phase 2 remains complete within its scope](phase2-completion-checkpoint.md);
[Phase 1 expansion stays paused](phase1-universe-pause-checkpoint.md). No UI, live
retrieval, other issuers, scenario/sensitivity/reverse HTTP routes, database, queue,
cache, authentication system or cloud deployment is added. Public launch is not approved.

Use the project Python 3.12 virtual environment. Historical/CLI requirements remain
in `requirements.txt`. API declarations are in [requirements-api.txt](../requirements-api.txt);
[requirements-api.lock](../requirements-api.lock) pins its transitive runtime versions.
[requirements-api-dev.lock](../requirements-api-dev.lock) adds HTTPX2 for tests.
These are version locks from the local Python 3.12 resolver, not wheel hashes or
proof of a Linux/container build. FastAPI 0.149.0, Uvicorn 0.54.0 and Starlette 1.9.0
were used; no system Python or cloud tooling was modified.

From the repository root, choose a **new directory outside the repository**:

```bash
.venv/bin/python -m pip install -r requirements-api.lock
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m valuation_platform.api.bundle /tmp/valuation-case-api
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/valuation-case-api/src VALUATION_APP_ROOT=/tmp/valuation-case-api .venv/bin/python -m uvicorn valuation_platform.api.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --limit-concurrency 16 --backlog 32 --timeout-keep-alive 5 --timeout-graceful-shutdown 2 --no-access-log
```

`VALUATION_APP_ROOT` is trusted server configuration, never an HTTP operand.
Use the bundle's `src` on `PYTHONPATH`, preserving its relative layout. There is no
developer-specific absolute resource path. The build rejects an existing destination
or one inside the source repository. It changes permissions only on its new copy;
never use chmod on working originals. Build replacement bundles offline at new paths;
keep a running bundle immutable. No runtime generation or approval activation.

Example calls from another terminal at the repository root:

```bash
curl -sS http://127.0.0.1:8000/health
curl -sS -H 'Content-Type: application/json' --data-binary @examples/valuation/synthetic-base.json http://127.0.0.1:8000/api/v1/cases/validate
curl -sS -H 'Content-Type: application/json' --data-binary @examples/valuation/synthetic-base.json http://127.0.0.1:8000/api/v1/cases/run
curl -sS -H 'Content-Type: application/json' --data-binary @examples/valuation/synthetic-equity.json http://127.0.0.1:8000/api/v1/cases/run
```

Only synthetic examples are runnable defaults. All six company single-case
templates remain 37-unset and all three scenario templates 111-unset. Company
eligibility, claims, awards and financial acceptance remain qualified. Neither
reference strings nor successful HTTP validation authenticate financial approval.

## HTTP contract and budget policy

| Route | Behavior |
| --- | --- |
| `GET /health` | Lightweight readiness flag, no valuation or per-request resource load. Successful startup is required for `ready`. |
| `POST /api/v1/cases/validate` | Structural/model validation only; no anchor loading, calculation, output saving or approval activation. Returns status, requested scope, `calculation_performed=false` and semantic-review limitation. |
| `POST /api/v1/cases/run` | Explicit direct A/B or A/B/C execution in a child process. Successful JSON is the **existing single-case result object**, with no API envelope or financial changes; formatting has no terminal newline. |

Accept UTF-8 `application/json`, optionally `charset=utf-8`; only absent/identity
Content-Encoding. Raw bytes go through a lexical depth guard, the **existing strict
JSON decoder**, bounded tree review and existing `read_case`. FastAPI/Pydantic does
not decode/coerce the financial body. Duplicate keys, nonfinite/floating JSON
rates, missing fields and unknown fields retain existing rejection. JSON depth
checking is not another JSON parser and never repairs malformed input.

All following limits are **HTTP execution budgets**, not financial conventions:

| Control | Fixed production ceiling |
| --- | --- |
| Streamed request body | 256 KiB, checked before appending each chunk; Content-Length cannot bypass it |
| Body-read deadline | 10 seconds; malformed/mismatched Content-Length rejects |
| Nesting / nodes | 24 structural levels / 4,096 decoded value nodes |
| Object / general array | 64 members / 128 entries; key length 128 characters |
| Text | Scope/rationale 4,096; general text 2,048; identifiers such as `*_id`, accession/kind/schema/role/unit 128 characters |
| References | At most 64 per reference array; each reference <=1,024 characters; population-ID arrays <=64 |
| Bridge populations | <=64 components, <=128 observations; all usual coverage/omission/class checks still apply |
| Numeric strings | <=128 characters, <=64 stored coefficient digits (trailing zeros count), exponent and adjusted-exponent magnitude <=100 |
| JSON integers | Absolute value <=10^12; model validation still permits integers only at existing integer fields |
| Calculation result | <=2 MiB encoded UTF-8 JSON; incremental encoding stops before exceeding it |
| Public errors | <=20 detail strings, each <=200 characters; worker error messages <=8 KiB |
| Calculation deadline | 35 seconds, including process startup, verification, calculation and bounded IPC receive |
| Unix child CPU / core dump | 30-second soft / 31-second hard CPU limit; core dumps disabled |
| Calculation capacity | One active child per application process; no waiting execution queue |

A short extreme-exponent string fails before Decimal construction. These limits
also bound multiplication/exponent and echoed-provenance work for the single-case
engine. There is no reverse certification endpoint. The large-bound certificate
serialization finding in the assessment is not an authorized engine change here.
Ordinary documented examples and precision-50 derived manual rates fit. Budgets
may be tightened only by trusted Python server/test configuration; HTTP cannot
choose limits, execution policies, commands, filesystem paths, output destinations,
resource roots or URLs to fetch. Source-reference URL strings remain inert metadata.

Errors use `{"error":{"code":"...","message":"...","details":[...]}}`:

| HTTP status | Contract |
| --- | --- |
| 413 | `request_too_large` |
| 415 | `unsupported_representation` |
| 422 | `invalid_case`, `invalid_length` or `response_budget`; input field paths where available; no partial result or EV-only downgrade |
| 408 | `body_timeout` |
| 499 | `client_disconnected`, best-effort response if connection has gone |
| 503 | `busy`, `not_ready` or `shutting_down`, with `Retry-After: 1` |
| 504 | `deadline_exceeded`; child has been stopped/reaped before capacity is released |
| 500 | Fixed sanitized `calculation_failed`, `worker_failed` or `internal_error`; no exception text, traceback, local path or submitted body |

Unknown routes/methods retain framework 404/405 behavior. Runs return `Cache-Control:
no-store`. No CORS middleware, browser credentials or public access assumption is
configured. The documented Uvicorn command disables access logging; application
code logs no submitted assumptions or full bodies. Internal HTTP exceptions are
contained before server traceback logging. Startup failures report a generic
readiness failure, with no valuation result.

## Process lifecycle and private bundle

[Calculator](../src/valuation_platform/api/process.py) uses `multiprocessing` spawn,
one new OS process per accepted run. The child calls existing Python functions,
not a shell or CLI. Bounded byte messages cross a one-way pipe; the parent checks
message length and result size too. Blocking IPC receive runs in a helper thread;
the **calculation itself is terminable**, rather than merely cancelling a thread.

On deadline, ASGI disconnect, coroutine cancellation or application shutdown,
terminate the child, join for 0.5 seconds, then kill/join if needed. Cleanup is
shielded from request cancellation; capacity is released after reaping. Shutdown
rejects further work. Health/validation can respond while calculation runs.
An ordinary server-warm run still creates a fresh child, without cached anchors.

CPU/core restrictions were exercised on macOS using Unix `resource`. Linux has not
been verified; Windows is unsupported (the existing import chain uses `fcntl`).
**No memory/RSS cap is implemented or claimed.** Input/output budgets reduce exposure but are not a
proof of a process-memory maximum. Linux resource/container enforcement still
requires a separately authorized test. The worker also denies financial network
operations, subprocesses and filesystem mutation through a Python audit hook.
This is defense in depth for trusted code, **not an OS sandbox**.

[bundle-files.json](../src/valuation_platform/api/bundle-files.json) contains an
explicit 70-Python-file closure and SHA256 pins for eight original resources:
three company packages, `trillion-review-batch.json`, three CapEx registries and
the D&A registry. No second financial-data copy is tracked. The offline builder
copies exact bytes in the existing layout and creates deterministic
`runtime-manifest.json`: `local-case-runtime-v1`, sorted logical paths, byte counts
and hashes, no timestamps or developer paths. It includes the allowlist metadata
itself. Startup/readiness verifies exact manifest membership/content and the pinned
resources **before financial imports**; registry imports may then read the four
verified registries. Each worker verifies the bundle again, and normal adapters
still enforce source/review/audit/effective bindings during the run.

The bundle has 79 manifest entries (70 Python + eight resources + allowlist),
plus its generated manifest; dependencies are installed from the separate lock.
Files are copied as 0444 and directories as 0555. Local permission checks and
worker audit checks rejected attempted resource writes; the working repository
was never chmod'd. These controls assume a trusted service owner: an administrator
can change permissions/code. Keep all bundle/Python/private files outside any
future static hosting directory. No `.git`, unrelated corpus or SEC response
archives are required for execution; retained provenance remains intact.

## Verification and measured local API behavior

New focused coverage: both synthetic scopes equal existing engine and CLI JSON;
calculation-free validation instrumented against financial loaders/calculators;
strict parsing, field errors, no downgrade, streamed oversize/misleading lengths,
encoding, depth/nodes/text/numeric/population budgets, sanitized failures and
bounded serialization/IPC. Real children exercise busy recovery, responsive health,
wall deadline with forced kill/reap, CPU exhaustion, disconnect, cancellation and
shutdown. Caller context/inputs remain unchanged. Bundle checks cover deterministic
manifests, missing/tampered resources (including altered generated hashes), isolated
six-case execution and actual write/network denials. All retained-anchor executions
use explicitly **synthetic** forecast/bridge inputs, not analyst forecasts.

Commands actually run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.api.test_cases -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/valuation -t . -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.analyst.test_preparation_preservation -v
.venv/bin/python -m pip check
```

Results: **17 API/process/bundle tests, 174 valuation/CLI/adapter tests and five
preparation-preservation tests passed (196 total)**; dependency check passed.
No full historical suite or new company financial review. Financial source,
engine, schema and preservation pins/allowlists are unchanged.

Actual localhost Uvicorn profiling used the installed environment and isolated
bundle on Apple M1, eight logical CPUs, 8 GiB RAM, Python 3.12.3/macOS. The final profiling pass used three fresh
server starts ran both scopes on all three retained anchors, twice per case
(**36 HTTP calculations**, plus validations). Readiness was observed via `/health`;
HTTP timings include process spawn, resource checks, calculation and serialization.
Memory was sampled with `ps` approximately every 20 ms over the server process tree,
including its helper/worker; brief unsampled peaks are possible.

| Local measurement | Observed |
| --- | --- |
| Fresh process launch → ready | 0.508–0.823 seconds |
| Structural validation HTTP | 1.60–6.74 ms |
| EV first / server-warm HTTP execution | 0.393–0.739 / 0.395–1.241 seconds |
| Equity/share first / server-warm HTTP execution | 0.402–0.927 / 0.411–1.201 seconds |
| Sampled maximum parent / parent-plus-descendants RSS | 74.6 / 150.4 MiB |
| Separate trusted 0.5-second deadline probe | 504 in 0.506 seconds, approximately 6 ms termination/response overhead |

This is **not Cloud Run measurement** or a worst-case memory proof. The deadline
profile used a separate temporary blocking-worker test factory, not an HTTP policy
option; lifecycle tests also exercise a child that ignores terminate and requires
kill. Temporary profiling scripts, cases/results and private bundles are removed
after verification. No actual company case/default or saved valuation output enters
the repository.

## Remaining launch boundary

A public release needs separately scoped admission/distributed-abuse controls and
load testing. One active calculation is **per API process**, not deployment-wide;
multiple workers/instances multiply capacity, memory and spending. An in-memory
limiter is not a global quota. Uvicorn's documented connection/concurrency/backlog
settings bound local admission, not a distributed spending ceiling. No database,
queue or cache is added to address hypothetical traffic.

Still unverified: container/image size, Linux CPU/permission enforcement and memory
behavior (including abrupt parent/container death), actual cloud cold starts,
multi-instance load, Firebase routing and billed transfer hops. Future cloud timeouts
must leave room for body intake, the 35-second
calculation deadline and cleanup within the proposed 50-second HTTP window.
No cloud resources/accounts, login, deployment, DNS change or push occurred.
