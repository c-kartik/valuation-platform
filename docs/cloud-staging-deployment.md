# Authenticated Cloud Run staging — first remote checkpoint

Subsequent [compiled-browser integration review](cloud-frontend-acceptance.md) tested
this same revision through an authenticated localhost proxy without redeployment.
The measurements below remain this original deployment's record.

## Result and exact artifact — 2026-10-20 (Asia/Dubai)

**Authenticated single-case staging API deployed and smoke-tested.** This resumes
and supersedes the [earlier billing deferral](cloud-staging-checkpoint.md), which
remains a historical record. No frontend/portfolio deployment, financial-policy
change or investment-readiness certification follows. [Phase 1 remains paused](phase1-universe-pause-checkpoint.md)
and [qualified Phase 2 completion](phase2-completion-checkpoint.md) is preserved.

| Binding | Recorded value |
| --- | --- |
| Repository / branch | [c-kartik/valuation-platform](https://github.com/c-kartik/valuation-platform) / main |
| Exact pushed source consumed | `ebf6139df600580f6aa92cd759a8a67fc7aea823` |
| Project / region / service | kartikchaturvedi-website / us-central1 / valuation-api-staging |
| Cloud Build | `0b8fa0af-651d-46aa-889d-0c27b757c9da` — SUCCESS |
| Image | `us-central1-docker.pkg.dev/kartikchaturvedi-website/valuation-staging/valuation-api` |
| Immutable image digest | `sha256:5b5421c09fc2611b1b1315fa032a982f3cf53bc02c98d26cc5c70f400e608bd0` |
| Tag / active revision | source-ebf6139 / valuation-api-staging-00001-2rk |
| Service URL | <https://valuation-api-staging-378340095652.us-central1.run.app> |
| Status URL used by authenticated smoke | <https://valuation-api-staging-ailnp3irra-uc.a.run.app> — same service |
| Image OS/architecture / size | linux/amd64; Docker inspect 306443051 bytes; registry imageSizeBytes 70818651 bytes |

The first request's expected starting HEAD was already superseded by the prior
local documentation commit. We verified clean `main`, fetched and preserved history:
GitHub already held `0d96989`; only the reviewed deferral documentation was pending.
A normal push advanced GitHub to **ebf6139**. No force push, visibility change or
continuous-deployment trigger. Rechecked workflows/webhooks were empty; the prior
full GitHub integration inspection and 13-commit scan remain attributed earlier
checks. This **new deployment documentation commit remains local**, is not the
image source and caused no second build/deployment.

## Build origin and reproducibility

No local Docker/SDK installation. Used the existing browser account and preinstalled
Cloud Shell gcloud; the user completed Cloud Shell authorization. Explicit account,
project and billing checks preceded provisioning. The deployer already had Owner;
no human Owner/Editor privilege was granted by this task.

The unchanged [image recipe](local-api-image.md) and [allowlisted builder](../src/valuation_platform/api/bundle.py)
produced an exclusive context from the clean pushed source: **89 files**, locked
API dependencies, 84 manifest entries plus manifest, Dockerfile/ignore/launcher.
Every context file path/hash was checked after upload. No `.git`, local environment,
unrelated corpus, frontend, tests, secrets or executable company forecast entered it.
A full remote GitHub clone was aborted because it fetched unnecessary corpus data;
its partial checkout was removed. **Cloud Build did not fetch GitHub.** It built
the locally generated context uploaded via Cloud Shell to the dedicated source bucket.

- Canonical sorted path/SHA256 context digest:
  `39eb3b88db07e21edffd066f5c2643c73abd3bf456c0c1d6e1f4c4132e42d41c`.
- Uploaded archive: 834137 bytes, SHA256
  `cb86b96a3de76a5d4dbb883bfdd630cb1eaa300541901afc4e1fbffb0a5694d9`.
- One explicit regional Cloud Build with Docker `--platform linux/amd64`, the
  existing two-stage Python 3.12.15 recipe, 900-second build ceiling and
  `CLOUD_LOGGING_ONLY`. Build time was 26.192s, source fetch 2.653s and push 11.024s;
  these are build-stage measurements, not application cold starts.
- Build-time manifest verification and dependency consistency succeeded. No
  build/startup/code/schema/formula changes or protection weakening were needed.
  The final digest is pinned in the service. Upstream base tag/OS and dependency
  artifacts are not hash-pinned; a future rebuild is not guaranteed bit-identical.

## Created resources and access

Enabled required Run, Build, Artifact Registry and IAM APIs. Created only:

| Resource | Scope / access |
| --- | --- |
| Artifact Registry `valuation-staging` | us-central1 Docker repository; one image digest, the active revision's image; no rollback image |
| Bucket `kartikchaturvedi-website-valuation-build-uscentral1` | us-central1 build source; uniform access and public-access prevention enforced; source archive retained for build provenance |
| `valuation-api-builder` service account | Artifact Registry Writer on that repository; Storage Object Viewer on that bucket; project Logs Writer only |
| `valuation-api-runtime` service account | Dedicated runtime identity; **no project IAM role bindings** |
| `valuation-api-staging` | One authenticated Cloud Run service and one revision, 100% traffic |

The user confirmed the specific build grants before they were applied. Required
Google-managed agents were established through API enablement; observed roles
include Artifact Registry, Cloud Build, Container Registry, Pub/Sub and Run service
agents. Repository inspection confirmed optional vulnerability scanning is disabled
(the scanning API is not enabled). No application Pub/Sub topic/queue or unrelated IAM/resource was created
or changed. No service-account keys were created/downloaded. Tokens were captured
only in script memory, never echoed or explicitly saved; the Docker helper config
contained a helper name only. Existing interactive credential storage was left intact.

Effective service/revision configuration was checked: **1 vCPU, 1 GiB**, concurrency
**1**, service and revision maximum **1**, minimum **0**, HTTP timeout **50s**,
request-based CPU throttling, startup CPU boost disabled, gen2 and one Uvicorn
worker. The unchanged calculation deadline is **35s** (CPU 30s soft/31s hard).
Private read-only resources remain outside any static route; financial-worker
network/mutation denials are software defense, not a general OS/network sandbox.

Invoker IAM checking is enabled. Service IAM contained no bindings; neither service
nor project policy had allUsers/allAuthenticatedUsers grants. The existing authorized
Owner account could invoke without an additional human role. Both service URL
aliases rejected anonymous health requests with **403**; the smoke also verified
anonymous catalog denial before execution and health denial after it. No public
invoker access, Firebase rewrite, domain mapping, CORS expansion or auth bypass.

## Newly executed verification

Temporary inputs came from existing synthetic fixtures, adapted only to each
retained META/GOOGL/AAPL anchor and declared manual conventions. Forecast and bridge
numbers remained **synthetic engineering assumptions**, not actual-company choices
or financial approvals. All nine company templates remain byte-unchanged/unset.

Six ordinary **local CLI executions** established canonical full-result SHA256
references. Each authenticated response was decoded and canonically hashed identically,
including full numerical strings, submitted inputs, provenance and limitations.
All **six unique cases plus three repeated/concurrent runs** matched their local
references; no comparison used rounded EV/share metrics.

| Unique case | Validation | Full JSON match | Run latency, ms |
| --- | --- | --- | ---: |
| AAPL equity/share | 200, no calculation | PASS | 4138.47 |
| AAPL EV | 200, no calculation | PASS | 2384.70 |
| GOOGL equity/share | 200, no calculation | PASS | 2822.71 |
| GOOGL EV | 200, no calculation | PASS | 2639.91 |
| META equity/share | 200, no calculation | PASS | 3182.91 |
| META EV | 200, no calculation | PASS | 2545.94 |

Further actual cloud checks:

- Ready health and three-entry catalog returned 200; catalog was 20283 bytes.
  Validation responses declared `calculation_performed=false`; input bytes remained
  unchanged. This does not independently instrument internal cloud call graphs.
- Unset WACC rejected 422 with its field identified; no traceback/private path.
  Body one byte over 256 KiB rejected 413. Manifest, source configuration, company
  package, example and OpenAPI path probes returned 404. Forced worker-500 sanitization
  was not exercised in Cloud Run; existing host tests remain earlier evidence.
- Two concurrent valid requests both matched CLI, at 2539.38 / 7137.79ms; recovery
  health returned 200. Cloud Run admission/queueing can serialize requests. This
  neither exercises every application busy path nor proves a global quota.
- First/repeated health: 148.38 / 735.86ms. A later repeat of the same AAPL equity
  input matched at 3627.25ms. These sparse HTTPS timings are not controlled cold/
  warm comparisons or a performance guarantee; deployment had already startup-probed.
- Deploy through ready/routed took 27.231s. Cloud Monitoring published one startup
  latency sample of **6842.252ms** (descriptor unit ms), distinct from deploy time.
- One published container memory-utilization sample had mean **0.0596063683**,
  approximately 5.96% / 61MiB of the configured 1GiB. This is sparse sampled
  utilization, **not peak RSS, worst-case memory or an exhaustion/recovery test**.
  The bounded error-log query found zero ERROR-or-higher entries at that time.

Cloud Shell also had an **already running remote** amd64 Docker daemon. The same
image was pulled, inspected and run as UID 10001 with read-only root, no network,
1 CPU / 1GiB, 64-PID limit and 16MiB scratch. A trusted temporary probe (no HTTP
policy/diagnostic route) verified manifest/resource integrity, rejection of a
modified scratch copy, read-only private-file denial and worker network denial.
It used a two-second test-only deadline and a sleeping worker that ignores SIGTERM:
busy rejected 503, deadline returned 504 after **2.526s** including forced kill/reap,
capacity recovered for a normal calculation, and shutdown reaped all children.
The probe container auto-removed; no container remained. This verifies Linux image
lifecycle behavior, **not forced deadline/abrupt instance-death behavior inside
Cloud Run**. Production timeout/policy and image code were unchanged.

No prior 254-test suite was claimed rerun. No implementation changed; new execution
checks above and final documentation links/whitespace/protected-byte checks were
performed: 442 local links/anchors passed, whitespace was clean, and all nine
templates remained byte-identical (six with 37 unset rates; three with 111).
Temporary local/remote cases, outputs, scripts, uploads, partial clone,
Docker helper config and remote image cache were removed. No local proxy/server,
keep-warm job or ongoing test load was started. Standard source-build archive and
active image remain in their dedicated cloud resources.

## Costs, limits and next scope

Existing billing was linked and the unchanged budget was **$10 monthly, all billing
account projects/services, alerts only at 50/90/100/150%**, not an enforced spend cap.
The console showed $0 before the experiment; actual attributable post-build charges
were not yet available and can lag by more than 24 hours. No zero-cost or hard-$10
claim. Ongoing costs can include image/source storage, invocation/startup CPU/memory,
requests, logs and transfer; see [Build](https://cloud.google.com/build/pricing),
[Registry](https://cloud.google.com/artifact-registry/pricing) and
[Run pricing](https://cloud.google.com/run/pricing). The source bucket has a **7-day
soft-delete policy**; deleting objects may retain billable soft-deleted bytes.
Min zero/max one limit capacity, not total spend.

This completes the **restricted authenticated staging experiment within its tested
scope**. Anonymous staging and public production remain not ready. Remaining work
includes Firebase/frontend routing and authentication design, explicit anonymous
exposure/abuse controls, broader workflows, representative load/peak-memory testing,
Cloud Run forced cleanup/abrupt-death behavior and production/domain migration.
No investment-ready, complete-claims or fully diluted fair-value claim is added.
The live website, separate portfolio repository, Netlify and DNS were unchanged.

## Teardown procedure — not executed

Review resource names/contents first; the commands below remove **only this staging
service and dedicated resources**, not the project, billing, budget or managed APIs:

```bash
gcloud run services delete valuation-api-staging --region=us-central1 --project=kartikchaturvedi-website
gcloud artifacts repositories delete valuation-staging --location=us-central1 --project=kartikchaturvedi-website
gcloud storage rm --recursive gs://kartikchaturvedi-website-valuation-build-uscentral1 --project=kartikchaturvedi-website
gcloud projects remove-iam-policy-binding kartikchaturvedi-website --member=serviceAccount:valuation-api-builder@kartikchaturvedi-website.iam.gserviceaccount.com --role=roles/logging.logWriter
gcloud iam service-accounts delete valuation-api-builder@kartikchaturvedi-website.iam.gserviceaccount.com --project=kartikchaturvedi-website
gcloud iam service-accounts delete valuation-api-runtime@kartikchaturvedi-website.iam.gserviceaccount.com --project=kartikchaturvedi-website
```

Repository/bucket-local grants disappear with those dedicated resources. Inspect
soft-delete retention and delayed charges afterward. Do not disable shared APIs or
remove Google-managed agent roles/unrelated grants as blanket cleanup.
