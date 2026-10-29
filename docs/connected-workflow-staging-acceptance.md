# Connected investor workspace — private staging acceptance, October 29, 2026

## Verdict and release binding

**PASS within this bounded authenticated staging review.** The built localhost
workspace exercised the connected case → EV/equity → scenarios → sensitivity →
certified reverse → separate exploratory/explicit-forward journey. This is software
acceptance, not financial completeness, investment readiness or public-launch
approval. [Phase 1 remains paused](phase1-universe-pause-checkpoint.md).
The [earlier local acceptance](connected-workflow-acceptance.md) retains its own
checks; they are not relabeled as cloud observations.

| Binding | Verified value |
| --- | --- |
| Repository / pushed image source | valuation-platform/main; `7b92ac58b3707a02820763630f1846d70e246b80` |
| Starting reviewed commit | `eb3d3de98fcdf268abc3e1d565847b1d3ca5919d`; clean main, 12 ahead before the harness fix |
| Project / number / region | kartikchaturvedi-website / 378340095652 / us-central1 |
| Cloud Build | `9043dad6-65d9-4d64-9284-488573234937`, SUCCESS; one image build |
| Image repository | `us-central1-docker.pkg.dev/kartikchaturvedi-website/valuation-staging/valuation-api` |
| Immutable digest | `sha256:fbca75a98dd81393d5056aa83b44ec259590a8f4dc7d4dc8a3364b7009d1f970` |
| Active service / revision / traffic | valuation-api-staging / `valuation-api-staging-00002-q5m` / 100% |
| Ready time | October 29, **11:01:56.523567 UTC / 15:01:56.523567 Dubai** |
| Previous rollback revision | `valuation-api-staging-00001-2rk`, retained; original [image binding](cloud-staging-deployment.md#result-and-exact-artifact--2026-10-20-asiadubai) |
| Authenticated proxy origin | `https://valuation-api-staging-ailnp3irra-uc.a.run.app` |
| Built frontend review | <http://127.0.0.1:4173/workspace/> → loopback 8001 → private staging; no local-API fallback |

Only this staging image/source label changed remotely. Runtime identity
`valuation-api-runtime@kartikchaturvedi-website.iam.gserviceaccount.com` and effective
configuration were preserved: gen2, 1 vCPU/1 GiB, request-based CPU, no startup CPU
boost, concurrency 1, min 0/max 1, 50s HTTP, one Uvicorn worker and disabled access
logging. Application ceilings remain 35s wall/30s child CPU, 256 KiB request, 2 MiB
response and the existing parser/certificate/iteration budgets. Service IAM is
byte-equivalent; invoker IAM checking remains enabled, no public principal binding.
Anonymous health returned **403 before and after deployment**. No new IAM grant,
API enablement, billing/cap change, Docker installation or other service update.
Official SDK 591.0.0/proxy 0.5.2 were installed temporarily outside the repository.
The component installer's optional system-Python step failed without a password;
existing Python 3.12 ran the CLI successfully, with no system-Python installation.

GitHub main advanced normally from `0a9282c` to the image source; workflows and
webhooks were empty. The final acceptance documentation is a later pushed commit,
**not a second image build**. No portfolio push or continuous deployment was added.

## Packaging and narrow harness fix

The existing [image recipe](local-api-image.md) produced **92 context files**:
87 allowlisted manifest entries plus manifest (88 runtime files), and four image
inputs. Canonical JSON path/byte-count/SHA256 manifest digest:
`913898bc9120c9c904ab48b5a8d945a733f6bac7453221b516df30b6cbfe5b31`.
Cloud Build used the existing scoped builder, regional registry/source bucket,
900s ceiling and CLOUD_LOGGING_ONLY. Source fetch took 2.945s, build 29.444s,
push 9.725s. The source archive and images remain for provenance/rollback.

Read-only registry manifest/config inspection verified **linux/amd64**, UID/GID
**10001:10001**, exact source label and **68,542,219 compressed layer bytes**.
The runtime COPY layer's **88 files matched local hashes and read-only file modes**;
OCI whiteout metadata was excluded from the file population. The 12 pinned resources
are the selected three packages, existing review/normalization registries and unset/
synthetic templates; no unrelated issuer historical package entered the image.
Build-time, startup and worker manifest verification remain active. This is not
an OS sandbox or inspection of live container process memory. Upstream base/wheel
artifacts remain version-locked rather than fully digest/hash-reproducible.

The old localhost harness exposed only cases and fixed upstream port 8000. Its
bounded fix adds the existing scenario/sensitivity/reverse validate/run routes
(**nine exact routes including catalog/cases**), `/workspace/` HTML and compiled
shared assets. `--proxy-port` accepts only a numeric **loopback** port; `--port`
selects its loopback listener. Defaults remain 8000/4173. Body/response/time budgets,
host/origin checks, credential dropping and no body logging remain. Static paths
exclude prototype/source/private files, JSON, maps, traversal and symlinks. No
arbitrary upstream host, frontend economics, engine or API policy changed.

The built artifact's eight files passed local-reference, allowlist and credential-
pattern inspection. The existing **Firebase** guard intentionally rejects this
new multi-entry artifact; its fixture tests pass, but public publication is **not**
approved by this localhost check. Initial browser navigation from Google's site
was rejected by the cross-site guard; direct address-bar navigation loaded the
preview. The guard was retained.

## Newly exercised acceptance

| Workflow | Hosted evidence | Result |
| --- | --- | --- |
| Catalog and validation | Three actual retained anchors; explicit validate routes declare calculation_performed=false. Local instrumentation tests separately prove no history load/calculation/spawn. | PASS; cloud internals not instrumented |
| EV / qualified equity | Both scopes on META/GOOGL/AAPL; missing browser bridge blocks equity while retaining EV. Dates, units, signed bridge and unbounded omissions visible. | PASS |
| Bear/Base/Bull | All anchors through API/CLI; META desktop independently edited/cutoff-declared shared-equity comparison and calculation-free validation. | PASS |
| Sensitivity | All anchors, mixed invalid cells/nulls; AAPL 11×11 equity; META inspect/cancel/confirm apply and explicit recalculation. GOOGL mobile 3×11 grid, Home/End focus and internal scroll. | PASS |
| Certified reverse | Both target scopes/all anchors through API/CLI; META EV/share, GOOGL share and AAPL September-dated EV in browser. Unreachable target and demanding iteration exhaustion expose no solution. | PASS |
| Exploratory / freshness | Cancelled/confirmed forks; fresh META EV/equity and GOOGL EV. Applied WACC/g changes only those fields; stale overview correctly withholds EV/share. Fork financial inputs/notes preserved; META shared bridge exact. | PASS |
| Ownership / recovery | Active GOOGL solve → AAPL switch → no foreign result; preserved GOOGL target retry. Real browser cancel and shared disabled submission state/correct tool label. Stopped only task proxy: unavailable message, entries retained, explicit retry succeeds after restart. | PASS within observed client/proxy behavior |
| Desktop / narrow / reload | Chrome 1440×1000 and 390×844; visible validation/focus/confirmation, internal matrix scrolling, no page-width overflow, no console application errors. Trial state cleared on reload. | PASS within resized-desktop scope |

Browser cancellation does not prove immediate Cloud Run worker termination. Resized
desktop does not certify mobile keyboards, assistive technology or all browsers.

**21 unique hosted complete JSON results matched their local CLIs**, plus two
concurrent repeats. **23 embedded cases/cells/reverse solutions** matched individual
forward runs; **1,641 independent exact-rational component comparisons** passed.
**17 browser-captured results** separately matched CLI JSON, with **11 embedded/
fresh-forward matches and 1,126 additional rational comparisons**. Checks covered
revenue compounding, loss tax, FCFF operands/signs, terminal/discount arithmetic,
EV and bridge/share reconciliation; reverse residual/tolerance and ≤1e−12 bracket
checks passed. Rational tolerance was `1e−30 + 1e−46 × |reference|`; financial
arithmetic used no float. Display rounding was not the comparison oracle.

**185 frontend tests, 65 focused Python tests and the production build passed**.
Python: 46 API/image/preparation tests, seven updated preview checks, 12 existing
publication-guard checks. Real-child busy, CPU/deadline, ignore-SIGTERM kill/reap,
disconnect/shutdown and recovery guarantees were exercised **locally**, not injected
into Cloud Run. The historical full suite, earlier 184-test valuation invocation,
prototype build and earlier acceptance counts were **not** rerun here.
Final checks covered **500 changed-document local links/anchors**, clean whitespace,
exact staged documentation scope, protected-source bytes and all nine unset templates.
No financial engine/interface defect was found. One temporary helper initially used
invalid leading-dot Decimal strings; the parser correctly rejected them, and the
helper was corrected without changing application parsing.

## Measurements, costs and operational limits

| Observation | Newly measured sample |
| --- | --- |
| Revision create → ready | 16.46s; image import 4.72s; reported container healthy 6.49s |
| Monitoring startup latency | One nonempty sample: **6,499.382ms**; deployment startup, not a controlled cold-request comparison |
| First authenticated health | **0.567s**, after deployment startup; not claimed cold |
| 21 full hosted runs | **2.383–32.727s**, largest response **386,855 bytes** |
| AAPL 11×11 equity grid | **28.383s / 368,562 bytes** |
| Demanding GOOGL reverse | **32.727s / 140,554 bytes**; ITERATION_LIMIT, no solution, unchanged 128-iteration ceiling |
| Two concurrent matching cases | **2.387 / 4.416s**, both 200; subsequent health ready. Cloud Run admission serialized them; no observed application 503 |
| Memory Monitoring sample | Distribution means **6.05–9.56%** of 1 GiB (largest mean about 98 MiB); not peak RSS/exhaustion proof |
| Billable-instance-time sample | **246.224 seconds** in published deltas through the sampled query; partial/lagged usage, not final attributable cost |
| Bounded revision log sample | 83 entries: 76 request metadata entries (72×200, 3×422, 1×403), four application startup lines; zero ERROR-or-higher. No submitted-body/assumption/token markers found; one platform403 advice names the Authorization header without a credential value. Later health checks are outside that sample. |

The large grid/reverse samples leave **limited margin below 35s**. They do not
establish worst-case admissible work, memory sufficiency or load/production readiness.
Forced production-deadline cleanup, abrupt instance death and memory exhaustion were
not directly observed in Cloud Run; local lifecycle tests remain separate evidence.
No limits were raised, grid reduced, solver weakened, keep-warm loop or open load
test added. The instance/process gate is not a distributed quota; gateway admission
may queue. Structured invalid requests and the real proxy-outage retry recovered.

Preflight Console showed the unchanged **USD10 monthly Cloud Run cap Configured**,
not Enforced, approximately **USD0.01/USD10**, project-wide across Cloud Run services.
No cap exhaustion/bypass was attempted. Estimated costs can lag/overshoot; builds,
registry/source storage and logs are outside that cap. No invoice/zero-cost claim.

## Software inputs, preservation and review session

All future values, bridges, targets and axes were **arbitrary synthetic software
choices on retained revenue**, not actual-company estimates/approvals or defaults.
API fixtures used 10% growth, 20% margin, 25% tax, 5% D&A, 10% investment, 2% full-
revenue WC, WACC 25%, g 5%; explicit terminal ratios 30/20/4/9/1% (margin/tax/D&A/
investment/WC). API bridge: USD10+2 assets −20 financing −3 claims; four synthetic
shares. Bear/Bull deliberately used 8/18% and 12/24% growth/margin.

Browser cases used the same annual baseline, independently entered terminal
20/25/5/10/2%; META additionally FY2027 growth 12.125000000000000001%, FY2028 margin
21%, terminal margin 22%, then explicitly applied WACC 16%/g 2%. Browser bridge was
USD100m assets −40m financing −10m claims, 20m synthetic issued shares, synthetic
single common class and explicit unbounded existing-award/population omissions.
Grid axes were WACC 2/16/30% and g 2/5% (GOOGL g 2–12% by one point). Reverse bounds
−20% to 30%, META EV target USD100,000m (also negative unreachable), share target
USD5,000; GOOGL USD10,000/share; AAPL USD200,000m EV. API known roots used constant
7.3456789123% growth; extreme probes used the existing synthetic regression values.
Cutoff February 5, 2026 was an **unverified test declaration**; analytical dates were
retained fiscal ends, including AAPL September 27. No current market data/research.

Historical/frozen/source approvals, formulas/certificate, all nine unset templates
(**15 case bodies × 37 numerical nulls**, unresolved bridge/share selections),
portfolio, Netlify/DNS and Firebase/live channels remain unchanged. No actual
company forecast/target/grid/case or valuation result was saved in the repository.
Temporary case/results/helpers, image context and task CLI credential/tooling files
were removed after verification; normal authentication storage was not removed.
The review proxy retains only an expiring identity token in its process, not browser
assets or repository/log files. Its OAuth account consent was not separately revoked.

Review process binding: Python compiled-preview **PID 84387** on loopback
4173 and official Cloud Run proxy **PID 85615** on loopback 8001. After
verification, the proxy was restarted with only a fresh in-memory identity token and
**no credential refresh**, then its temporary SDK/credential files were removed.
It automatically stops **October 29, 12:20:00 UTC / 16:20:00 Dubai** (55-minute
review window); token expiry is 12:25:00 UTC. Static preview remains running after
that deadline but API requests require a new authorized login/proxy session.
This is a localhost session deadline, not withdrawal of private staging.
To stop early, verify these listener PIDs with `lsof -nP -iTCP:4173 -iTCP:8001
-sTCP:LISTEN` and `ps -p 84387,85615 -o pid,comm`, then
`kill -TERM 84387 85615`. Do not print token-bearing process
arguments or stop the unrelated local review servers.

The existing local workspace <http://127.0.0.1:5173/workspace/>, prototype 5174 and
local API 8000 remain untouched. The staging preview is **4173 →8001 → staging**.
For a new authenticated session, with supported Google CLI and normal login:

```bash
gcloud run services proxy valuation-api-staging --project=kartikchaturvedi-website --region=us-central1 --port=8001
python3 scripts/preview_cloud_frontend.py --proxy-port 8001
```

The harness is trusted-workstation engineering tooling, not hosted authentication;
other local processes able to reach its proxy can use the operator's invocation.
Do not expose listeners beyond loopback or print token-bearing proxy arguments.

## Rollback and remaining public gates

Rollback was **not executed**. Review before using the existing previous revision:

```bash
gcloud run services update-traffic valuation-api-staging --project=kartikchaturvedi-website --region=us-central1 --to-revisions=valuation-api-staging-00001-2rk=100
```

This changes only staging traffic and preserves private IAM. The old revision has
only the earlier single-case API; connected analysis routes will be unavailable.
Retain both images/revisions; do not delete shared identities, storage or services.

Before any public preview: separately approve publication paths/routes, hosted
authentication or anonymous exposure, abuse/admission/cost controls, compatible
Hosting manifests/guards, representative resource/deadline/abrupt-death acceptance
and a named withdrawal/operations plan. No Firebase release/channel, public/production
API, live website, DNS or Netlify operation is authorized by this checkpoint.
Financial eligibility, claims/awards/funding/settlement completeness and sustainable
assumptions remain separate and potentially unbounded. Stop for review.
