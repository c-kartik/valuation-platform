# Project Status

## Current — proposed production backend and cost controls

The [production plan](public-preview-preparation.md#production-backend-and-cost-policy--proposed-october-22)
prepares a separate `valuation-api`: request-based 1 vCPU/1GiB, service/revision
min 0/max 1, concurrency 1, 50s HTTP and unchanged child/parser/cleanup limits.
The [review JSON](../deploy/api/production-plan.json) is non-executable, with launch,
public-access, budget authority and approved image unset. No build or deployment.

Read-only inspection confirmed direct USD billing and budget/spend-cap permissions.
The existing USD10 alert covers **all account projects/services**, at
**50/90/100/150%**, not a dedicated project cap. Console inventory showed no spend
cap; its unsaved definition offers enforcement. Public Budget REST inspection
returned `SERVICE_DISABLED`; no API was enabled. A separate USD10 monthly Cloud Run
cap is eligible in principle but pauses **all project Cloud Run workloads** and
counts gross estimated usage before credits. Proposed project alerts: 50/80/100%.
Neither control was changed or enforcement-tested.

Illustrative 1k/10k monthly calculations consume approximately **USD0.16/1.61 gross
compute/requests**, potentially USD0 payable if shared free allowances remain.
Hosting/transfer/storage/logs/builds are separate; no USD10 total-bill guarantee.
Service max/tag caveats, a best-effort per-action rather than shared EV/equity
client lock, operator/availability choices and the staged launch authorizations
remain explicit. Private services, preview access/deadlines, live Hosting,
Netlify/DNS, portfolio, financial code/approvals and nine unset templates are
unchanged. Phase 1 remains paused; no repository push.

## Earlier — isolated combined portfolio/calculator preview

The [combined preview](combined-site-preview.md#verification-record) serves the
portfolio root and approved calculator at `/valuation/` in a separate channel.
Fourteen allowlisted files are assembled from two explicit clean source commits;
no permanent portfolio copy or API/financial changes. Eighteen focused checks,
TypeScript/Vite build, local/hosted file hashes, desktop/390×844 page/navigation
review and two complete synthetic browser-to-CLI JSON comparisons passed. A
Hosting slash-redirect loop was withdrawn and corrected before final acceptance.

Combined expiry: **October 23, 2026, 13:10:39.991846463 Dubai /
09:10:39.991846463 UTC**. The existing backend withdrawal remains **14:17:28 Dubai /
10:17:28 UTC** that day. Standalone preview, live Hosting, all Cloud Run
services/IAM, Netlify and DNS remain unchanged. Both repositories have local-only
checkpoints; neither was pushed. All nine unset templates and the Phase 1 pause
are preserved. Production/domain migration remains separately scoped.

## Earlier — fresh hosted redesigned equity preview

The [October 22 hosted release](firebase-public-preview.md#october-22-redesigned-equity-preview)
deploys the approved compact investor and optional equity/share flow from clean
pushed source `0f5200d` through one new remote build, pinned revision
`valuation-api-preview-00002-kq7`. The old deadline was missed; old backend access
was revoked and anonymous denial verified at **October 22, 14:07:05 Dubai /
10:07:05 UTC** before building/reopening. The old channel was deleted and tag retired.

Fresh checks: **82 frontend + 113 focused Python tests**, build/publication checks,
15 successful actual hosted Chrome submissions matching full CLI JSON and legacy
financial components, plus nine independent rational equity/share reconciliations.
Desktop/390×844, annual replacement, independent terminal edits, stale results,
coverage/errors, signs/fractional shares and clean reload passed. Tests used
synthetic economics only; actual-company economic selections remain unapproved.

**Manual backend withdrawal: October 23, 2026, 14:17:28.069 Dubai /
10:17:28.069 UTC.** Hosting expires seven seconds later; it does not revoke backend
access. No shutdown automation or hard spend cap. Exact resources, source/digest,
qualifications and [withdrawal commands](firebase-public-preview.md#withdrawal-runbook-for-this-release)
are recorded. Private services, live Hosting, Netlify/DNS/portfolio, formulas,
historical/source approvals and all nine unset templates are unchanged. Phase 1
remains paused. Local review servers were preserved.

## Earlier — optional equity workflow acceptance

The [local investor walkthrough](equity-workflow-acceptance.md) passed synthetic
EV → manual bridge → issued-share review through all three retained anchors.
It fixed generic share-sign guidance, hidden overlap-error focus and a fractional
share denominator rounding to zero. Financial formulas/domains and all nine
unset templates remain unchanged. Actual-company economic selections remain open.

Fresh checks: **82 frontend + 101 focused Python tests**, production build,
33 browser/HTTP-to-CLI JSON comparisons with equivalent legacy financial matches,
30 independent rational bridge reconciliations, 25 invalid HTTP rejections,
links/whitespace and protected-scope checks. Actual desktop/390×844 Chrome review
covered qualified results, stale edits, switching, keyboard errors, local outage
and explicit retry. Timing/race/busy coverage is automated; mobile keyboard and
complete accessibility acceptance remain unverified. Trial captures/cases/outputs
were temporary and removed. Phase 1 remains paused.

Local checkpoint only; loopback frontend/API remain running for review. No push or
hosted changes. Public-preview backend withdrawal remains **October 22, 2026,
13:04:19 Dubai / 09:04:19 UTC**; no extension.

## Earlier — optional manual equity/share calculator

The [optional second step](local-calculator-ui.md#optional-cash-debt-and-shares)
adds manual eligible assets, financing/other claims and dated shares to EV using
the existing Stage C engine. Coverage, class/equivalence, award and non-overlap
choices are explicit and initially unset. Unassessed requirements block equity;
null-valued omissions remain prominent on a provisional reference. No financial
review or automatic company selections are inferred. Bridge edits stale only
equity; operating edits and EV refresh require explicit per-share recalculation.
The [anonymous v2 extension](local-case-api.md#optional-anonymous-equityshare-extension-local)
preserves investor v1 EV and legacy analyst JSON behavior.

78 frontend tests and 101 distinct focused Python checks passed, plus production
build, local links/whitespace and protected-scope checks. A temporary synthetic CLI
comparison matched complete Stage B/C components with intentional metadata
differences. Desktop and 390×844 browser review exercised the optional flow,
qualifications and editing. No actual-company case, bridge selection or output
was saved; all nine templates and historical approvals remain unchanged.
Phase 1 stays [paused](phase1-universe-pause-checkpoint.md).

Local commit only, with compatible loopback API/frontend running for review.
No push or hosted changes. The public preview still has its **October 22, 2026
13:04:19 Dubai / 09:04:19 UTC** manual backend-withdrawal deadline; no extension.

## Earlier — compact local investor calculator

The [calculator redesign](local-calculator-ui.md#compact-investor-redesign-verification-local)
replaces the oversized workbench with a compact company/revenue summary, grouped
eight-rate grid, keyboard/touch help, independent long-term editor and one
Calculate action. Source/timing qualifications and full-precision traces remain
accessible; desktop results sit alongside inputs and narrow results follow the
action. Readable USD headlines use display-only Decimal scaling. Direct entry,
progressive errors, anonymous metadata and financial conventions are preserved.

**64 frontend + five preservation checks passed**, plus production build,
links/whitespace and protected-scope checks. Desktop and 390×844 Chrome review
covered unset selection, synthetic engineering inputs, keyboard/help, annual
refinement/cancellation, invalid recovery, recalculation and signed results.
Before/after screenshots were captured. This is local developer verification,
not mobile virtual-keyboard testing or investment acceptance. No actual-company
case/default/output was saved; all nine templates and historical approvals remain
unchanged. Phase 1 remains [paused](phase1-universe-pause-checkpoint.md).

Local commit only; requested loopback frontend/API remain running for review.
No push, deployment or cloud changes. The hosted preview is unchanged, including
its **October 22, 2026 13:04:19 Dubai / 09:04:19 UTC** manual backend-withdrawal
deadline. Further changes await user review.

## Earlier — local direct-entry investor workflow

The [calculator](local-calculator-ui.md) now uses plain-language profit, tax, D&A,
operating investment, cash-needs, discount-rate and long-term-growth labels.
Uniform main entries directly update five annual values, with no Apply bookkeeping.
Differing annual paths require an explicit confirmed replacement. Long-term copy
confirms changed populated values and stays independent of later annual edits.
Neutral initial guidance becomes inline touched/left or submitted error review;
submission groups uniform-year errors, expands/focuses the first field and keeps
service failures separate. Anonymous metadata and optional notes remain approved
and unchanged; no financial defaults or economic approvals are added.

**60 frontend + 72 focused Python tests passed (132 total)**, plus production
build, local links/whitespace and protected-scope checks. An actual Python pipeline
comparison matched complete financial components for equivalent old/new entry.
Actual compiled Chrome desktop and 390×844 keyboard walkthroughs exercised unset
selections, synthetic direct entry, partial/missing/domain error recovery,
annual replacement cancel/confirm, long-term independence, modal focus and
recalculation. Representative screenshots were captured. This is developer
verification, not mobile virtual-keyboard or investment acceptance. All nine
unset templates, formulas, historical/source approvals and Phase 1 pause remain
unchanged. No actual-company economic case or output was saved.

The checkpoint is local only, followed by the requested localhost frontend/API
review servers. No push, remote build or cloud/deployment changes. The hosted
preview remains on its prior version with the same **October 22, 2026 13:04:19
Dubai / 09:04:19 UTC** manual backend-withdrawal deadline; this work does not
extend its window.

## Earlier — local investor calculation without analyst paperwork

The [local workbench](local-calculator-ui.md) now supports company → enter/apply
assumptions → calculate without required identity, rationale or scope/cutoff entry.
Collapsed Analysis details holds an editable generated name, a stable UTC
preparation timestamp, explicit anonymous investor provenance and nullable optional
personal notes. No rationale, verified identity/cutoff or financial approval is
invented. The narrow [investor metadata contract](local-case-api.md#anonymous-investor-metadata-local-update)
reuses all financial/source validation and A/B calculations; legacy analyst v1/v2
CLI/API requirements and JSON remain compatible. Runtime template instructions
are separated from current completeness and enduring financial limitations.

**59 frontend + 72 focused Python tests passed (131 total)**, covering case inputs,
CLI/summary, API/catalog/public boundary and preparation preservation; production
frontend build passed. Actual local compiled-build Chrome desktop and 390×844
walkthroughs exercised unset selections, explicitly synthetic inputs, no-details
calculation, notes, stale edits and recalculation. These are developer workflow
checks, not mobile virtual-keyboard testing or investment acceptance. All nine
unset templates and financial formulas/history/approvals are unchanged. No actual
company forecasts or cases were saved; temporary bundle/session removed.

This checkpoint is local only: no push, remote build, deployment or cloud changes.
The existing public preview below is unchanged and does not support the new version.
Its **October 22, 2026 13:04:19 Dubai / 09:04:19 UTC** manual backend-withdrawal
deadline remains in force; this work does not extend it. Phase 1 stays paused.

## Deployed preview — one-day anonymous window unchanged

The [hosted acceptance/withdrawal record](firebase-public-preview.md) binds Firebase
channel ev-public-review to valuation-api-preview revision 00001-mf4, reusing the
reviewed immutable image without a rebuild. Name/tag length passed local and Cloud
Run validateOnly checks. Six successful actual Chrome submissions matched complete
CLI JSON; synthetic demo and retained META/GOOGL/AAPL anchors, explicit apply,
terminal/annual refinement, stale/recalculate, validation/correction, root reload,
desktop and 390×844 keyboard focus passed. Four affected local config tests/build/
publication checks passed; the prior 95-test suite was not repeated unchanged.
No financial-input, actual forecast, per-share or production-readiness approval.

**Manual backend withdrawal: October 22, 2026, 13:04:19.869 Dubai / 09:04:19.869 UTC**,
earlier than Hosting expiry at 13:04:55.672076339 Dubai / 09:04:55.672076339 UTC.
No automation enforces it. Direct backend access is anonymous; max one and budget
alerts are not hard spend/global quotas. Existing local-branding copy remains a
minor hosted-preview limitation. Private staging and the failed-attempt service are
unchanged/private; live Hosting still has no release. Retained resources/costs and
withdrawal commands are explicit. Netlify/DNS/portfolio, nine unset templates,
financial formulas/source approvals and Phase 1 pause remain unchanged.

## Earlier — public-preview attempt blocked; access withdrawn

The [deployment/withdrawal record](public-preview-preparation.md#deployment-attempt-and-withdrawal--2026-10-21)
records the authorized one-day attempt from clean source 02888f4. Firebase enrollment
and default site are verified. One remote build succeeded; the isolated backend
was deployed, briefly made public, then returned to authenticated access. Firebase
CLI revision pinning failed because its generated tag plus the required service name
exceeds Cloud Run's 46-character combined limit. No Hosting release or hosted-browser
acceptance occurred. The empty preview channel was removed; both backend URLs now
return anonymous 403. Original private staging JSON/IAM/revision are unchanged.

95 focused local tests, locked build and publication guard passed. No new hosted
arithmetic/browser PASS is claimed. Source archive, new authenticated image/service
and unreleased Hosting version remain and can cost money. The original October 22
12:40:18.819 Dubai withdrawal deadline was satisfied early on October 21 at 12:44:31.114.
Next separately authorize a shorter isolated name, a fresh window and all hosted
acceptance checks; no second build is needed merely for documentation. Netlify/DNS,
live Hosting releases, portfolio, nine unset templates, financial approvals/formulas
and Phase 1 pause remain unchanged. No automated deployment trigger was introduced.

## Earlier — anonymous preview prepared locally; deployment blocked

The [public-preview assessment](public-preview-preparation.md) records enforced
request/parser/result budgets, worker deadlines/cleanup and residual anonymous
availability/cost risks. Added early known cross-site browser rejection and uniform
no-store/nosniff across application responses. These changes are **local only**;
the current authenticated cloud revision is unchanged. No distributed quota, hard
total spending cap, peak-memory bound or bot-resistance guarantee is claimed.

The [narrow desktop keyboard journey](narrow-keyboard-review.md) passed at 390×844
after replacing inline confirmations with safe-focus native modals, explicit Tab
cycle, Escape cancellation and trigger restoration. This is not a mobile virtual-
keyboard/device test. **95 focused tests passed**, with build and publication guard.
Prior cloud arithmetic/image evidence was not rerun.

[Firebase preview configuration](../firebase.preview.json) prepares root calculator
assets and ordered `/api` rewrite with pinTag to the **unprovisioned**
`valuation-api-public-preview`. Existing Firebase site identity is unresolved;
read-only Console navigation reached add-Firebase onboarding and was stopped.
The publication guard rejects deployment until reviewed. Next authorization must
name an existing site/channel and approve the new service's anonymous/direct access,
bounded settings, monitored residual costs and withdrawal plan. No cloud build,
provisioning, IAM/public grant, Hosting deployment, Netlify/DNS change or push.
All nine unset templates, financial formulas, historical approvals and Phase 1 pause
remain unchanged; qualified Phase 2 software closure persists.

## Earlier — compiled frontend / authenticated cloud integration verified

The [browser/cloud review](cloud-frontend-acceptance.md) exercised the unchanged
compiled frontend against revision `valuation-api-staging-00001-2rk` through the
official authenticated loopback proxy. Eleven captured successful browser runs
matched full local CLI JSON; 682 independent arithmetic comparisons, four valid
validation-only submissions and 84 focused automated tests passed. Synthetic demo
and retained META/GOOGL/AAPL anchors, annual edits, negative flows, error recovery,
desktop keyboard use and narrow layout were checked. Narrow keyboard and forced
remote late-response/busy/deadline faults remain qualified; host tests cover those
logic paths. Sparse timings/metrics are not peak-memory or load guarantees.

Added a bounded localhost compiled-preview harness and six tests; no financial,
API/frontend contract, history/approval or nine-template changes. Temporary test
captures/inputs, SDK/configuration and servers were removed. Anonymous Cloud Run
still returns 403; no IAM, cloud build/redeployment, push or website/DNS change.
Next separately decide Firebase preview access and hosted API authentication/routing.
Phase 1 stays paused and qualified Phase 2 software closure is unchanged.

## Earlier — authenticated Cloud Run staging API verified

The [deployment checkpoint](cloud-staging-deployment.md) supersedes the earlier
billing deferral below. Pushed source `ebf6139df600580f6aa92cd759a8a67fc7aea823`
produced one successful remote Cloud Build and one authenticated us-central1 service,
`valuation-api-staging`, revision `valuation-api-staging-00001-2rk`. Its image digest,
context origin, dedicated resources/IAM, measured behavior and teardown are recorded.
One vCPU/1GiB, min 0/max 1, concurrency 1, request-based billing, 50s HTTP and the
unchanged 35s calculation deadline are retained; runtime has no project roles.

Six synthetic retained-anchor EV/equity cases and three repeats matched full local
CLI results; validation, invalid/oversized input, private-route rejection and final
anonymous 403 checks passed. A trusted same-image probe on preinstalled **remote**
Cloud Shell Docker verified linux/amd64, read-only resources, tamper rejection,
forced deadline kill/reap/recovery and shutdown. No local Docker/SDK installation,
financial/code changes or repeat of the earlier 254-test suite occurred.

This closes the bounded authenticated experiment, not anonymous staging, public
production or investment readiness. Sparse sampled memory/startup measurements do
not establish peak-memory bounds or forced cleanup inside Cloud Run. Existing $10
billing alerts are not a hard spending cap. Active service/image and source-build
storage remain; temporary trial files and remote cache were removed. Deployment
documentation is committed **locally only**, without rebuilding or pushing it.
The live website, Netlify, DNS, historical/frozen approvals and nine unset templates
are unchanged. Qualified Phase 2 completion and the Phase 1 pause persist.

## Earlier — reviewed source pushed; GCP staging deferred

The [push/staging checkpoint](cloud-staging-checkpoint.md) records the normal push
of reviewed source `0d9698996ecdd50f897f1991c37a950ff317a4f1` to the existing
`c-kartik/valuation-platform` main branch. Available GitHub configuration showed no
deployment triggers. The authorized GCP project had no linked billing account;
the user then deferred GCP setup. No remote build, image, IAM/API/resource changes
or service deployment occurred. Cloud Shell credential authorization was not
accepted and its panel was closed. Deployment identifiers, authentication tests,
cloud timings/memory and actual charges therefore remain unavailable.

This is a local-only documentation checkpoint after the source push. No new
financial/code changes or local valuation tests occurred; the prior checks below
retain their original attribution. The live website, Netlify, DNS and separate
portfolio repository are unchanged. Phase 1 remains paused and qualified Phase 2
closure persists. Resume only after billing linkage and the user's direction.

## Earlier — compiled EV walkthrough and local API image candidate

The [developer investor walkthrough](local-workbench-acceptance.md) completed
continuous synthetic engineering sessions on all three retained anchors through
the compiled frontend and packaged API. Fourteen actual browser submissions matched
CLI full result JSON; an independent exact-rational oracle passed 882 equalities.
**254 affected tests passed** (54 frontend, 21 API/catalog/launcher, 174 valuation/CLI,
five preservation), plus build, dependency, link, whitespace and protected-scope
checks. No human participant testing or economic acceptance is claimed.

Observed missing/tax diagnostics now speak percentage units; backend failures use
service/retry guidance without blaming valid assumptions. No financial formulas,
API schemas, source approvals, historical/frozen artifacts or nine unset templates
changed. Temporary engineering cases/captures/bundles/servers are removed.

A [local API image recipe](local-api-image.md) prepares 89 allowlisted files separately
from four compiled frontend files; it is not a deployment. No Docker/Podman/Colima
executable was available, so Linux/image execution remains a gate. Restricted cloud
experimentation is **not yet ready** pending Linux tests and configuration/access/
budget approval; anonymous staging and public production are **not ready**. No
cloud login, provisioning, deployment, push or separate website change occurred.
Phase 1 remains paused; qualified Phase 2 closure and financial unknowns persist.
Next bounded step: test the local image matrix with an already available runtime.

## Earlier — quick EV workbench with advanced annual editing

The [local workbench](local-calculator-ui.md) supersedes the original four-section
presentation below. Select a retained company, enter eight compact required rates,
explicitly apply six annual values, supply/copy five terminal operating ratios and
complete Case details, then Calculate. Advanced annual edits remain authoritative;
quick drafts are independent, visibly unapplied and block submission. Replacing
annual values needs confirmation; collapsing preserves inputs. Terminal copying
is one-time only and does not copy growth/WACC or follow later annual edits.

Reported history/source limitations remain separate from forecast assumptions.
Missing cash-flow, terminal and metadata requirements are visible without a
technical trace. Authored rationale/scope remain explicit; cutoff remains unenforced
free text. Result review shows EV, the expressly authorized display-only terminal
contribution ratio, revenue/FCFF trends and a compact forecast table. Components,
reconciliation, full-precision table/provenance expand. Ratio/coordinate/display
arithmetic never changes financial operands or the API contract. Existing revision,
abort, stale-result, error-recovery and company-switch protection are preserved.

**52 frontend + 19 API/catalog + 174 valuation/CLI + five preservation tests
passed (250 total)**; TypeScript/Vite build, Python dependency check and full npm
audit passed. New frontend CLI-display tests use the existing Python virtual
environment; the only new dependency is Node type declarations for those tests.
Safari desktop and 390×844 checks included keyboard input, explicit apply/copy,
advanced edits and results. A responsive grid overflow was corrected and rechecked;
no unexpected browser-console errors were observed. Screenshots were emitted,
not added to the repository.

Developer checks exercised actual Safari and the packaged API, explicit synthetic
flat paths on all three retained anchors, terminal copying, META annual refinement
and confirmation/collapse behavior. Four separate proxy/API cases matched CLI full
JSON; browser EV/contribution displays matched. No investor acceptance, company
forecasts/defaults or financial approvals follow. See that milestone's
[verification record](local-calculator-ui.md#quick-workbench-verification).
Financial engine/API code, historical/frozen resources, approvals and all six
37-unset plus three 111-unset templates are byte-unchanged. Phase 2 qualified
completion and Phase 1 pause remain intact. No hosting/cloud/website changes.

Next bounded UI work may address JSON import/export or richer case-detail
usability. Equity/share and other screens, production deployment and public
admission controls remain separate scope.

## Earlier — first local EV-only React/TypeScript calculator

The [local calculator](local-calculator-ui.md) connects manual single-case entry
to the existing packaged Python API. Four sections cover retained basis/metadata,
five annual forecasts, independent terminal/discount assumptions and explicit
Validate/Calculate review. All 37 company rates start unset; no analyst declarations
are silently completed. The separate $100 synthetic fixture is explicit. API/model
semantics remain authoritative; no formulas, schemas, historical resources or
financial approvals change. Phase 1 remains paused.

A bounded versioned read-only catalog projects three retained anchors and unchanged
templates from existing verified resources, without private package/audit exposure.
The bundle now has 84 entries with original pins preserved. Both development
servers bind to loopback; Vite proxies `/api` without CORS expansion. Inputs remain
in memory; edits cancel/invalidate old requests/results, populated switching needs
confirmation and field/resource/busy/deadline errors preserve entries. The UI
renders returned full-precision strings in USD millions with display-only rounding.
Terminal contribution is explicitly deferred because the current result contract
supplies no ratio; no financial diagnostics are added in JS. Single-case cutoff
is disclosed in free text, not enforced by a new field.

**35 frontend + 19 API/catalog + 174 valuation/CLI + five preservation tests
passed (233 total)**; TypeScript/Vite build, Python dependency check and npm full dependency
audit passed. Safari desktop/390×844 responsive checks covered keyboard
entry, labels, field errors, stale results and populated switching; a fresh load
had no console errors after adding the missing favicon. This is not exhaustive
browser/accessibility certification. Details are in the [UI verification record](local-calculator-ui.md#earlier-four-section-verification-record).
Actual Safari sessions used the synthetic demo and synthetic forecasts on all
three retained anchors; separate proxy/API results matched CLI full JSON in four
cases. No company economics/defaults were saved. No full historical suite,
research, cloud provisioning, deployment or personal-website change.

Next bounded UI milestone: an explicit server presentation contract for terminal
contribution and focused review/navigation improvements; import/export and
bridge/share entry require separate scope. Public deployment remains behind the
existing API launch checks. Software acceptance does not certify investment readiness.

## Earlier application milestone — local-only single-case API implemented and verified

The [local API](local-case-api.md) adds lightweight `/health`, structural
`/api/v1/cases/validate` and explicit `/api/v1/cases/run` for existing EV/equity
case payloads. Raw strict parsing preserves duplicate/type/unknown-field rejection;
HTTP budgets bound 256-KiB streaming bodies, nesting/nodes/text/numeric magnitudes,
bridge populations and 2-MiB results. Existing financial readers/formulas/schemas
are unchanged. One spawned calculation per API process has a server-controlled
35-second wall deadline, Unix CPU limits, bounded IPC and real terminate/kill/reap
cleanup on timeout, disconnect, cancellation and shutdown; excess work returns busy.
There is no execution queue, client policy/root/path choice or scope downgrade.

An offline allowlisted builder preserves exact resource bytes/layout, pins eight
required resources and generates a deterministic 79-entry private runtime manifest.
Startup and workers verify it; normal source/audit checks remain active. New copies
are read-only, and worker audit hooks deny mutation/network operations; no working
original is chmod'd. Isolated six-case API execution used synthetic assumptions on
all three retained anchors without `.git`, unrelated corpus or SEC response archives.

Verification: **17 API/process/bundle tests + 174 valuation/CLI/adapter tests + five
preparation-preservation tests = 196 passed**; dependency check passed. Real-child
tests cover deadline/forced kill/reap, CPU exhaustion, busy recovery, health,
disconnect, cancellation, shutdown and output limits. No preservation pin/allowlist
or economic rule was relaxed. Actual localhost Uvicorn profiling over three fresh
server starts/36 calculations observed readiness 0.508–0.823s, validation 1.60–6.74ms,
runs 0.393–1.241s, sampled parent/tree RSS maxima 74.6/150.4 MiB; a separate trusted
0.5s deadline probe returned 504 in 0.506s. These are macOS measurements, not Cloud
Run, a memory cap or worst-case proof. Temporary profiles/bundles/cases are removed.

API dependencies/locks are separate from historical CLI requirements. No system
Python/cloud tooling, resources, login, deployment, UI, live retrieval, database,
queue or cache. No company assumptions/defaults are saved; six 37-unset and three
111-unset templates, historical/frozen data, approvals and engines remain unchanged.
Phase 2 remains complete within its existing scope; Phase 1 remains paused.

Next separately scoped launch work includes admission/distributed-abuse policy,
container size, Linux enforcement/memory, cold starts, Firebase routing and billed
transfer checks. One API process/worker is the supported local start; scaling it
does not create a global quota. No public launch is authorized by this checkpoint.

## Earlier milestone — scoped Phase 2 software COMPLETE; economic acceptance qualified

The [final three-company checkpoint](phase2-completion-checkpoint.md) closes the
local analyst-controlled workflow for retained META, GOOGL and AAPL FY2025 anchors:
editable five-year FCFF → EV → explicit equity/share; complete Bear/Base/Bull;
explicit WACC × g sensitivities; certified bounded constant-growth reverse DCF;
traceable inputs/limitations, strict validation and protected JSON/summary output.
The [reverse acceptance record](phase2-reverse-dcf-acceptance.md) attributes the
preceding report's 1,668 arithmetic and 405 certificate equalities; those prior
checks are not represented as newly executed here. Earlier records below preserve
their historical boundaries, superseded by this latest status.

**Newly executed:** one continuous linked CLI/reader session per company, using
reconstructed disclosed provisional economics, not authenticated replays of deleted
original cases. Single-case EV/equity JSON/summary and assumption edits, complete
scenarios/isolated edits, explicit Base-selected 2×2 WACC/g grids and known-growth /
Base-EV / equivalent-unrounded-share reverse targets passed. Twelve cells matched
separate single-case submissions; nine reverse successes matched ordinary forward
execution; unreachable requests exposed no solution. **162 CLI invocations**, twelve
instrumented calculation-free validations and **1,737 independent exact-rational
comparisons** passed. Oracle tolerance was `1e−32 + 1e−46 × |reference|`, maximum
absolute difference about 1.047e−37. No correctness defect/fix was required.

Against the same unchanged code, documented unittest invocations passed **174
valuation/CLI/adapter tests + five preparation-preservation tests = 179**. Tests
cover stale/mismatched bindings, dates/units/scope, no downgrade, validation without
calculation/writes, compatibility, deterministic serialization, caller Decimal/input
isolation, certificate/failure policy and output protections. No full slow Phase 1
suite or evidence acquisition. Code/formulas/tests/pins/allowlists, historical/frozen
artifacts and approvals are unchanged. All six 37-unset and three 111-unset templates
remain byte-preserved. Temporary cases, outputs and scripts were removed; only
Markdown records/references enter this local checkpoint. No push.

**Operating-driver sensitivities DEFERRED, not a closure blocker.** The scoped
GOOGL ERP reconciliation is recorded; further broad market-input harmonization
is outside this software checkpoint. No standing company Base/default, financial
approval, investment-readiness or fully diluted fair-value certification follows.
META's reverse expense/outlook conflict, GOOGL terminal dependence, AAPL terminal
productivity, funding, asset eligibility, ventures, claims/awards and potentially
unbounded omissions persist. No arbitrary-ticker/latest-filing support, UI or
deployment. The [checklist](phase2-completion-checklist.md) distinguishes software
closure from financial sufficiency; every historical unknown/all 42 issuers need
not be resolved for this scoped milestone. Phase 1 expansion remains paused.

Recommended next bounded milestone: separately scope a local case-entry/review UI
over the existing validated interfaces for these three anchors, using synthetic/
unset inputs and explicit validation/run/traceable output. No Phase 3 implementation
starts here.

## Earlier milestone — qualified sensitivity acceptance and bounded reverse-DCF engineering complete

The [sensitivity acceptance record](phase2-sensitivity-acceptance.md) records the
preceding temporary META/GOOGL/AAPL review: all Base references reproduced, 75
cells matched single-case execution, 375 component comparisons and 375 independent
rational comparisons reportedly passed, with no correctness defect. Those checks
are attributed prior results, **not rerun actual-company trials in this milestone**.
Software acceptance is complete; economic acceptance remains qualified by terminal
dependence/productivity, early funding, asset accessibility, settlements, incomplete
claims/awards and potentially unbounded omissions. No standing company inputs,
grids or financial approvals follow. Phase 1 universe expansion remains paused.

The [approved reverse workflow](phase2-reverse-dcf-workflow.md) adds
`analyst-reverse-dcf-request-v1`: complete embedded single case or explicit scenario
selection from a fully validated set, dated EV/USD or qualified USD/share target,
and explicit growth bounds. One constant annual growth **replaces all five annual
rates**; terminal g, other ratios, WACC and bridge/shares stay fixed. Revenue-dependent
amounts recalculate through unchanged existing A/B/C. A degree-five mathematical
representation derived from shared exact operating components supports rational
Bernstein derivative bounds across the full interval. Increasing/decreasing proofs
are supported; sampled monotonicity is insufficient. Flat, unsupported uniqueness,
unreachable, iteration-limit and numerical-verification failures expose no solution.
Bisection uses existing forward evaluations and success requires residual and width
checks, exact bracket existence and a fresh forward execution. This is conditional
implied growth, not market expectations, a financial endorsement or price target.

The dedicated CLI validates structure without valuation/certification by default;
`--run`, JSON/summary and explicit protected/new-file-only output follow existing
patterns. Exit 0 means validation/success; completed unsuccessful solves have
structured diagnostics, null solution and exit 3; malformed/execution/I/O errors
have exit 2 and no result file. Actual technical settings, original growth path,
source/scenario, certificate, bracket, counts, forward components and provenance
remain traceable. Existing case/scenario/sensitivity sources/JSON are unchanged.

**New verification:** 174 valuation/CLI tests (20 new reverse tests) and five
preparation-preservation tests passed using documented `PYTHONPATH=src` unittest
invocations. Checks include independent synthetic arithmetic, positive/negative
responses, exact endpoints (including −100% growth), flat/unreachable/nonmonotone
and truly monotone-but-uncertifiable cases, residual/width/fresh-verification and
iteration limits, technical resource caps, strict fields/date/unit/scope, explicit
scenario selection, immutable inputs/Decimal contexts, deterministic output and
file protection. Legacy case/scenario/sensitivity JSON bytes and original engine
sources remain unchanged. No full historical suite or actual-company reverse
valuation was run.

Six temporary integrations exercised all three retained anchors in both EV and
per-share scope, including scenario selection, using **synthetic** operating/bridge
assumptions and forward-generated targets. Temporary inputs/results were removed;
packages were byte-preserved. Two runnable synthetic examples are added. Six
single-company templates remain 37-unset; three scenario templates remain 111-unset;
no company forecasts/targets/bounds became defaults. Historical/frozen artifacts,
source approvals and preservation pins/allowlists remain unchanged. Links/anchors,
whitespace and staged/protected scope are checked for the local checkpoint; no
new evidence, extra issuers, infrastructure, UI or push.

Actual three-company reverse-DCF analyst review and final analyst/regression
acceptance remain pending under the [completion checklist](phase2-completion-checklist.md).
Operating-driver sensitivity remains unimplemented/out of scope. Broader dated
market-input judgments and financial completeness remain separate from the
scoped engine's software completion.

## Earlier milestone — qualified scenario acceptance and WACC × g sensitivity engineering complete

The [scenario acceptance record](phase2-scenario-acceptance.md) attributes the supplied
META/GOOGL/AAPL review: software acceptance complete, economic acceptance qualified,
investment readiness not established. Base inputs were reconstructed, not exact
replays; Bear/Bull are agent estimates. Fixed dates/cutoffs/WACC/g/bridges, funding
flags, GOOGL Bear's 99.26% terminal dependence, AAPL's qualified incremental-return
diagnostics and potentially unbounded omissions remain explicit. Prior 657 rational
comparisons, preservation-pin AST review, six checks and isolated mutation probes
are attributed records, **not rerun checks in this milestone**. No actual-company
cases, outputs, scenarios or grids were saved as defaults.

The [bounded sensitivity workflow](phase2-sensitivity-workflow.md) adds
`analyst-sensitivity-request-v1`: one complete embedded single case with explicit
dates/cutoff, or an explicit Bear/Base/Bull selection from a fully validated set.
WACC rows/g columns each contain 1–11 strictly increasing unique fractional Decimal
strings. Invalid g≥WACC cells remain null with reasons; all-invalid grids reject.
The original reference is separate. Valid cells change only WACC/g and revalidate/
execute through existing A/B/C; g changes terminal revenue/FCFF, not just the Gordon
spread. Operating paths, terminal ratios, bridge/shares and metadata stay fixed.
JSON retains reference/provenance, reproducible cells, PV/EV reconciliation,
contribution and signed-reference absolute/fractional changes; zero denominators
are undefined, negative and over-100% ratios are retained.

The dedicated CLI validates without calculation by default, supports explicit
`--run`, JSON/summary, and existing new-file-only/protected-path output behavior.
Summary shows exact axes with display percentages, USD-million EV and separate
qualified USD/share matrices. Inputs and caller Decimal context remain immutable.
Existing engines/readers/single-case and scenario CLIs remain byte-unchanged.

**Newly performed verification:** 154 valuation/CLI checks (12 new sensitivity tests)
and five preparation-preservation checks passed using the documented `PYTHONPATH=src`
unittest invocation. Independent rational synthetic-cell arithmetic covers the g
numerator effect, PV/EV/bridge/share and signed reference changes; valid cells match
separate single-case submissions. Checks also cover mixed/all-invalid grids, strict
field-qualified errors, zero/negative values, Decimal isolation, summary rounding,
validation without calculation, deterministic JSON and file protections. Legacy
single-case JSON byte compatibility and unchanged source pins pass. No full
historical suite or prior actual-company valuation rerun was performed.

Temporary engineering requests exercised all three retained revenue anchors with
**synthetic** operating/bridge inputs, both output scopes and explicit scenario
selection, without network access; input bytes/packages were unchanged and temporary
files/results removed. Two synthetic request examples are runnable. Six existing
single-case templates remain 37-unset and three scenario templates 111-unset;
historical/frozen data, approvals and all preservation pins/allowlists are unchanged.
Local links/anchors, whitespace and staged/protected scope are checked for the
checkpoint. No evidence acquisition, historical research, additional company or push.

Actual analyst sensitivity review remains pending: choose justified grids and
review economic consistency/funding/terminal dependence without interpreting a
table as probabilities or total-value bounds. Broader market-input judgments,
operating-driver sensitivity, bounded reverse DCF and final three-company analyst/
regression checkpoint remain under the [completion checklist](phase2-completion-checklist.md).
Phase 1 universe expansion stays paused.

## Earlier milestone — editable Bear/Base/Bull engineering and synthetic integration complete

The [bounded scenario workflow](phase2-scenario-workflow.md) wraps exactly three
complete existing analyst cases in `analyst-scenario-set-v1`. Each independently
supplies all 37 inputs and rationale. Validation checks matching company/anchor,
fiscal periods, date/cutoff, basis, conventions, output scope and period labels;
equity sets require identical entire bridge/share payloads. No inheritance,
patches, automatic forecasts, probabilities or valuation ordering. Complete-set
validation performs no calculation/retrieval; explicit execution reuses existing
Stages A–C and retains full results/provenance in Bear/Base/Bull order.

The [dedicated CLI](../scripts/run_analyst_scenarios.py) supports validation by
default, `--run`, JSON/summary and explicit protected/new-file-only output. Summary
compares five annual revenue/FCFF paths, WACC/g, terminal economics, PV/EV and,
when requested, the fixed bridge, dated shares, qualified USD/share and omissions.
Negative values and undefined/signed/over-100% terminal contributions are preserved.
Single-case CLI/JSON, assumption validation rules and all engine formulas are
byte-unchanged from starting HEAD `9da4a348858fb6e5ec1cc72e1c04746afc4b92ec`.

Verification: **147 distinct focused checks passed** across invocations: 142
valuation checks (including 17 new scenario tests) and five preparation-preservation
checks. The initial
preparation-preservation run exposed a pre-existing stale assumptions-file pin:
it predated `1d2e918`'s error-field metadata. The diff was reviewed and only that
test pin advanced to the existing integration commit; no source rule/formula,
historical or frozen pin changed. Existing single-case JSON output bytes match
the starting implementation. No full historical suite was run.

Temporary, explicitly synthetic forecast/bridge assumptions exercised both scopes
on all three real retained revenue anchors without network access; inputs were
unchanged, packages/approvals preserved and trial files/results removed. Two
runnable synthetic examples and three incomplete EV-only company scenario
templates were added. Each new company template has **111 numerical inputs unset**
and unset analyst rationale/cutoff; all six existing templates remain unchanged,
37-unset each. No prior actual-company forecasts/results became executable cases,
financial approvals or defaults. Local links/anchors, whitespace and staged/
protected scope checked; no evidence acquisition, company reviews or push.

[P2-04](phase2-completion-checklist.md) is complete for engineering/synthetic
integration only. Actual META/GOOGL/AAPL economic scenario acceptance remains
pending, alongside broader market judgments and existing eligibility/claims/
awards limitations. Sensitivity tables, bounded reverse DCF and final
three-company analyst acceptance/regression remain later separately scoped work.
Phase 1 universe expansion stays paused.

## Earlier milestone — GOOGL ERP reconciled and temporary trial rerun

The [2026-10-19 reconciliation](phase2-googl-aapl-milestones.md#googl-erp-reconciliation--2026-10-19)
supersedes only GOOGL's ERP/WACC and resulting trial reference. Damodaran's
January workbook verifies **4.23% T12m ERP over unadjusted Treasury**, the same
specified variant as META/AAPL, distinct from sustainable payout/net cash yield.
Start-2026 measurement is separate from the January 23 author publication record,
within both relevant cutoffs; no December 31 publication or first-upload claim.
Treasury/beta/spread/weights/shield remain unchanged. WACC is **8.73522% unrounded,
8.74% applied**, replacing 9.57% in the temporary GOOGL case.

The disclosed original economic inputs reproduced **1,178.675bn USD EV /97.08
USD/basic-equivalent share** at prior reported precision. Removed original JSON
bytes/full-precision outputs were not recovered or authenticated. Reconciled trial:
**1,387.933bn EV**, **1,382.810bn equity reference**, **114.40 USD/basic-equivalent
share**, **93.014656% terminal contribution**. Annual operating flows, terminal
FCFF, signed bridge and 12.088bn issued A/B/C denominator are unchanged.

Four cases (original reconstruction, reconciled, and two separate diagnostics)
passed calculation-free validation and explicit CLI JSON/summary execution.
**292 new independent rational output comparisons**, plus two WACC equalities,
passed; maximum difference approximately **8.69e−38**, under documented tolerances.
The earlier 219/26 GOOGL checks remain attributed, not rerun. All 573 tracked files
were byte-unchanged after runs, before documentation updates; temporary cases,
outputs, workbooks and scripts removed. No engine/interface defect found.

[P2-03](phase2-completion-checklist.md) marks the specific ERP reconciliation
complete; broader market judgments/comparability remain open. No META/AAPL rerun,
financial acceptance, standing Base case, defaults or investment-readiness claim.
Claims/awards, eligibility, settlement non-overlap and carrying proxies retain
unbounded limitations. Phase 1 remains paused; scenarios, sensitivities, bounded
reverse DCF and final three-company acceptance/regression remain separately scoped.
Only documentation is checkpointed; six templates remain 37-unset, protected
code/history/approvals/frozen artifacts unchanged. No full-suite run or push.

## Earlier milestone — three-company scope-qualified trials recorded; remaining Phase 2 scoped

The [GOOGL/AAPL milestone record](phase2-googl-aapl-milestones.md) preserves the two
supplied reports as attributed historical trial records, alongside the unchanged
[META milestone](phase2-meta-milestone.md). The existing editable single-case
historical anchor → manual forecast → FCFF/DCF → EV → equity/share workflow has
now been exercised in temporary, scope-qualified trials for **META, GOOGL and AAPL**.
Reported GOOGL results were **1,178.675bn USD EV / 97.08 USD per dated basic-common
equivalent share** (2025-12-31 analytical date, 2026-02-05 cutoff); AAPL results
were **1,865.092bn USD EV / 124.92 USD per fiscal-end basic share** (2025-09-27 /
2025-10-31). All are temporary assumption-led results, not defaults, standing Base
cases, fully diluted values or investment-readiness certification.

Each report attributes 219 independent arithmetic checks to its prior trial,
with 26 GOOGL / 33 AAPL inline observations checked. These checks were **not rerun
or independently authenticated at this documentation checkpoint**. The reports
state temporary files were removed and no actual case/default was saved. Claims,
awards, reserve/asset eligibility, financing proxies and settlement overlap remain
qualified; omissions may be unbounded and do not bound total company value.

The [completion checklist](phase2-completion-checklist.md) limits remaining work
to these three issuers: market-input methodology reconciliation, editable
Bear/Base/Bull scenarios, reusable sensitivity tables, bounded reverse DCF, then
final analyst acceptance/regression. AAPL used the same specified Damodaran ERP
variant as META with an earlier dated observation; GOOGL used a 5% judgment.
The cases are not yet harmonized for comparison. Reconciliation and any affected
temporary reruns need separate scope; prior results are unchanged. Future feature
economics/ranges/conventions are not approved here. Complete historical sufficiency
or all 42 issuers is not a software-completion prerequisite.

This checkpoint changes documentation only. All six issuer templates retain 37
unset numerical inputs each; equity templates retain unresolved actual bridge/share
selections. Protected code, schemas, examples, historical/frozen artifacts and
source approvals are unchanged, including the META milestone and Phase 1 pause.
Validation is limited to retained-reference/report consistency, changed local
links/anchors, static unset-template checks, protected/staged scope and whitespace;
no tests, valuation execution or evidence acquisition are performed. Nothing pushed.

## Earlier milestone — GOOGL/AAPL revenue-anchor engineering integration

The synthetic-only scope and next financial-review step below describe that
earlier milestone; the current trial records/checklist above supersede its next step.

The [integration record](phase2-anchor-integration.md) documents explicit read-only
META/GOOGL/AAPL revenue dispatch, exact filing/calendar/precision selections and
source/review/audit/effective-view checks. GOOGL FY2025 revenue is 402836000000 USD;
AAPL is 416161000000 USD for 2024-09-29–2025-09-27. These are retained reported
anchors only: no actual-company forecast or valuation is executed. Optional
historical D&A/NWC/debt/share completeness is not a revenue-only prerequisite.
No preparation, historical source, approval or frozen artifact changes.

New GOOGL/AAPL v1 EV and v2 equity/share templates retain all **37 numerical
inputs and analyst metadata unset**, with actual bridge/share requirements
unresolved. Shared technical names `manual-fcff-v1` / `manual-equity-bridge-v1`
reuse existing arithmetic without transferring META financial acceptance. Legacy
examples and complete synthetic JSON bytes remain identical. Validation-only
stays calculation-free; strict malformed-number/duplicate errors now identify
paths such as `forecast_years[2].revenue_growth`. Bounds, conventions, annual/
terminal and missing Stage C errors identify the affected input.

Verification: **147 focused tests PASS**: 134 anchor/intake/valuation/CLI/summary/
approval/preservation checks (16 new), plus 13 existing GOOGL/AAPL historical
acceptance/replay/staleness checks. Manually checked
all six incomplete company templates: expected exit 2, 37 unset numerical inputs,
no calculations. Synthetic validation, JSON/summary execution, explicit new-file
output and overwrite rejection pass; input bytes unchanged and temporary outputs
removed. Calculation-function ASTs and original assumption validation rules are
preserved. **392 local link destinations** and whitespace checks pass. Full offline
discovery was attempted with socket connections disabled, then interrupted at the
approximate two-hour engineering budget while an unrelated historical income
binding setup reparsed retained XML (`test_income_binding_repair`). It did not
complete; no full-suite pass or complete failure classification is claimed.

The [META milestone](phase2-meta-milestone.md) remains unchanged. GOOGL/AAPL
engineering integration is not financial sufficiency, an investment valuation or
approval of historical omissions for valuation use. Next: separately scoped
financial input review for one issuer, retaining unresolved D&A/investment/tax/WC,
WACC/terminal and any equity/share decisions. Phase 1 expansion remains paused;
scenarios, sensitivities and reverse DCF remain later capabilities. Nothing pushed.

## Earlier milestone — META scope-qualified end-to-end testing milestone complete

The [milestone record](phase2-meta-milestone.md) documents historical anchor →
manual forecast → FCFF/DCF → EV → explicit equity bridge → value/share, with
editable assumptions separate from formulas. Synthetic tests and separately
authorized temporary META-anchored trials exercised this first-company workflow.
Temporary assumption-led results were approximately **945.742bn USD EV** and
**369.42 USD per dated basic common share**, before omitted legacy/venture claims
and awards, with **90.02% terminal contribution**. These are historical validation
records, not a permanent Base case, defaults, approved target or fully diluted
fair value. The prior trial's reported **694 independent comparisons** are
attributed to that temporary trial; they are not rerun at this checkpoint.

Historical/financial-input sufficiency, complete claims coverage and investment
readiness are not certified. Awards, financing/other claims, venture economics,
unpaid acquisition obligations and settlement overlap remain open; some omissions
are unbounded, so diagnostic alternatives do not bound total META value.
Both META templates retain all 37 forecast inputs unset and unresolved actual
bridge/share selections. Historical artifacts and approvals remain unchanged.
Phase 1 expansion remains paused.

At that milestone, next was **separately scoped GOOGL validation**, inspecting its approved historical
package and generalizing only the necessary consumer boundary; no work had begun.
The current integration/trial records above supersede that next step.
Scenarios, sensitivities and reverse DCF remain later capabilities. Completing
every eligible company is not a prerequisite for defined Phase 2 engine milestones.

Checkpoint verification: **118 affected tests PASS**, EV-only JSON compatibility
and engine/historical preservation confirmed; local links and whitespace checked.
Only reviewed implementation, synthetic examples/tests, incomplete templates and
milestone documentation belong in the local checkpoint; no temporary META case
or valuation output is retained. Nothing is pushed.

## Earlier milestone — editable equity/share cases, synthetic verification only

`analyst-case-v2` adds explicit `EQUITY_PER_SHARE` scope and editable Stage C
intake through the existing models and `bridge_to_per_share`. V1 cases retain
EV-only JSON behavior. Validation remains calculation-free; missing/unresolved
bridge data fail explicitly with no EV-only downgrade. References, coverage and
class/award declarations are not authenticated approvals or proof of hidden
economic non-overlap. JSON preserves submitted inputs and full A/B/C provenance;
the existing summary now includes signed components, subtotals, equity, actual
shares/class/award basis, USD/share and exclusions/unknown omissions. Output
creation/protections and isolated Decimal display rounding are preserved.

[Usage](../README.md#editable-analyst-inputs--forecast-through-value-per-share),
[synthetic example](../examples/valuation/synthetic-equity.json) and
[incomplete META extension](../examples/valuation/meta-fy2025-equity-unset.json).
The original synthetic EV example and 37-unset META forecast template remain
unchanged; no prior temporary forecast or actual bridge/share proposal is saved.
Actual META eligibility, financing/claims coverage, awards and per-share execution
remain pending; Phase 1 expansion stays paused.

**118 focused tests PASS** (12 new equity-interface +16 EV-interface +13 summary
+21 bridge +15 discounting +14 forecast +18 assumptions +9 company
approval/preservation). Only synthetic numerical cases execute; no full suite,
new evidence, historical/frozen changes, formula changes, commit or push.
No preservation allowance change was needed.

## Earlier milestone — analyst-facing CLI summary, presentation only

[CLI](../scripts/run_analyst_case.py) adds explicit `--format summary|json`;
JSON remains the default, byte-identical full-precision output. Validation-only
behavior stays calculation-free, and both formats share the unchanged exclusive
output creation and protected-path rules. The summary renders existing A/B
components, annual percentage inputs, USD-million cash flows, explicit terminal
inputs, EV reconciliation and discounted terminal contribution; zero EV produces
an undefined ratio and signed/>100% ratios retain an explanation. Only display
scaling/percentages use isolated precision-50/HALF_EVEN arithmetic. Analyst
rationale, supplied limitations and later-filed timing remain visible; no input
approval or economic validation is implied. [Usage](../README.md#editable-analyst-inputs--forecast-through-value-per-share).

**85 focused tests PASS** (13 summary +16 case interface +14 forecast +15
discounting +18 assumption +9 company approval/preservation). Only synthetic
cases execute. Engine formulas/schemas, historical/frozen data, Phase 1's pause
and the META template's 37 unset inputs remain unchanged. No actual META
valuation, evidence acquisition, infrastructure, commit or push.

## Earlier milestone — editable local analyst cases, synthetic verification only

[Case reader](../src/valuation_platform/valuation/case_inputs.py) and
[CLI](../scripts/run_analyst_case.py) add versioned local JSON inputs through EV,
reusing the existing assumption/terminal models and unchanged A/B engine.
Analysts can edit each annual rate, WACC/g and every terminal ratio independently;
no averages, defaults, terminal copies, policies or approval workflow are created.
Validation performs no calculation. Explicit `--run` uses only the fixed synthetic
fixture or existing pinned META boundary; stdout is default, and explicit output
must be a new file outside protected source/history paths. Exact submitted rate
strings, identity/date/rationale/scope/limitations and complete A/B provenance
survive. [Examples and commands](../README.md#editable-analyst-inputs--forecast-through-value-per-share)
include a runnable synthetic case and META FY2025 template with 37 null numerical
entries and unset analyst metadata. Actual META inputs/execution remain pending;
the [consolidated review](phase2-meta-base-input-review.md) is unchanged.

**93 focused tests PASS** (16 case interface +77 valuation/assumption/company
approval-preservation checks). Execution tests use synthetic values only; no full
suite, actual META valuation, evidence acquisition, historical approval/frozen
change, commit or push. Preservation permits only the five named added valuation
modules; all pre-existing historical source bytes remain protected.

## Current — Phase 2 Stages A–C implemented and synthetically verified

[Consumer contract](phase2-meta-base-consumer-contract.md): the user approves
P2M-01–13 mathematical/interface conventions and P2M-14 Stages A–C implementation/
synthetic verification only. Earlier proposals, clarifications and Stage A/B
authority are preserved there. Added a
narrow read-only META FY2025 revenue adapter with pinned audit/revision/source
bindings, and a separate pure five-year forecast through FCFF. Immutable results
retain every component, supplied assumptions, approved convention version and
source precision, with deterministic Decimal-string serialization and isolated
precision-50/HALF_EVEN arithmetic. Existing assumption models and all historical
facts/approvals/frozen artifacts are unchanged; no issuer preparation treatment
changes, so issuer records remain untouched.

Stage B adds `TerminalAssumptions` (five explicit sustainable operating/
reinvestment ratios, no duplicated WACC/g) and `discount_to_enterprise_value`.
It revalidates/recomputes the Stage A handoff, uses shared operating equations,
discounts years 1–5 and explicit Gordon terminal cash flow through EV, retaining
zero/negative mathematical results. Immutable output retains all Stage A
provenance, terminal components, factors/PVs, assumptions and versions. Analytical
t=0 is anchor fiscal end using later-filed information, not a contemporaneous
backtest/current market-date valuation; only integer end-year exponents apply.

Stage C adds `BridgeComponent`, non-additive `BridgeObservation`, fixed-role
`PopulationCoverage` reusing `ManualIdentity`, `ValuationShares`, `BridgeInputs`
and `bridge_to_per_share`. It revalidates/recomputes the Stage B handoff, requires
explicit reviewed coverage/omissions and compatible declared class/award policy,
then returns signed components/subtotals, equity and raw per-share arithmetic.
It preserves full A/B provenance, supplied source/decision/review declarations,
null unknowns and deterministic immutable output with isolated Decimal arithmetic.
No candidate loader, evidence authentication or automatic award/dilution engine.

Actual META rates, reviewed scope/rationale, population/share/award selections,
unresolved requirements and execution remain pending; financial-input sufficiency
remains NOT_ASSESSED. Code checks structure/declared compatibility and explicit operands,
not hidden duplication or economic completeness. Phase 1 expansion stays paused.
**77 focused tests PASS** (21 Stage C +15 Stage B +14 Stage A +18 existing assumption +9
company approval/preservation); checks are recorded in the contract. No full-suite/corpus
run, evidence acquisition, company review, commit or push.

[Stage C decision sheet](phase2-meta-base-consumer-contract.md#7-proposed-stage-c-decision-sheet)
preserves its original proposal history: implementation conventions are now
approved and synthetically verified; retained META population/share candidates
remain **PROPOSED**, and unresolved actual-use requirements remain open. No actual
META input/valuation approval follows.

[First actual META input review](phase2-meta-base-input-review.md) is prepared for
one consolidated review only: all 37 forecast/WACC/terminal entries are UNSET;
retained bridge/share candidates remain proposed, and actual-input consistency,
coverage, award treatment and execution authority remain pending. It recommends
reviewing an EV-only first case before resolving equity/per-share inputs; no
actual calculation, financial acceptance or historical approval change is made.

## Current — universe expansion paused; authoritative resumption checkpoint

[Pause checkpoint and Phase 2 handoff](phase1-universe-pause-checkpoint.md) is the authoritative current
resumption document: **24 completed scoped histories, 3 partial CAT/JNJ/CVX,
15 assessment-only; 42 eligible issuers, 8 specialized exclusions; 199 selected
annuals / 210 target slots, 11 deficits**. Full-universe analyst completion is
not claimed. PM/HD/NFLX are retained next candidates, not an active review queue.
The user intends separately scoped Phase 2 work in separate chats, initially
one company and a traceable Base case; this documentation authorizes no engine,
economic convention or financial acceptance. Historical source/approval records
below remain intact. Older assessment estimates/status snapshots do not override
current accepted package views. No company review or acquisition resumes automatically.

## Latest accepted milestone — CVX/MRK/PG approved scoped histories, CVX EBIT remains OPEN

The user explicitly approves all29 recommendations in the retained batch,
excluding CVX-PERIMETER. Existing revision-bound audits/effective views now select
MRK FY2021–2025 and PG FY2022–2026 at14/14 each year,70/70 each company.
CVX FY2021–2025 remains PARTIAL at13/14 each year,65/70: required EBIT is null
in all5 years because its affiliate/operating-business perimeter is unproved.
No source zero, substitute EBIT equation, exclusion or scope waiver is authorized.
[Current schedules, dispositions and validation](energy-pharma-staples-review-batch-results.md)
/ [machine audit and current counts](company-data-preparation/energy-pharma-staples-review-batch.json)
`/approval_activation`. All original facts, nulls, proposals, alternatives and
earlier approvals remain unchanged beneath the separate accepted views.

CVX retains depletion-inclusive DD&A, exact approved Capex, FY2023 SBC benefit−100,
named financing, ARO/claims and separate affiliate/restricted holdings; it is not
joint-use eligible as a complete operating-income package. MRK continuing panels
retain source-compatible existing EBIT derivations, continuing13122/discontinued987
in FY2021, original PARTIAL5 plus exact independent CFO proofs, and broader4448/4388
investment proxies without reversing prior pure-PP&E findings. PG uses exact first2
Pretax extensions, preserving generic nulls; ESOP preferred/pension/funding overlap,
broader cash QName and unexplained borrowing−1/+1 remain explicit. PG displayed CFO
differences+1m in FY2024–2026 are SUPPORTED under the unchanged existing precision
rule, not exact ties, plugs or proved rounding explanations.

**42 broadly assessed;27 packages =24 completed scoped histories +3 approved partial
CAT/JNJ/CVX;0 pending recommendations;15 assessment-only.** CAT SBC/JNJ scope,
history exceptions,22 previously completed packages and frozen/pilot bytes remain.
Known carrying captions are not complete debt/reinvestment, unrestricted cash or
verified pure expense D&A. Approval is not financial-sufficiency certification,
whole-universe/Phase1 closure or Phase2 use. No acquisition/research is launched.
Next unreviewed five-period frozen-order candidates: PM, HD, NFLX, identified only;
XOM's empty history remains an exception, not a reviewable invented history.

## Historical checkpoint — CVX/MRK/PG retained review, pending consolidated approval

[ONE decision/exception sheet](energy-pharma-staples-review-batch-results.md) /
[machine review](company-data-preparation/energy-pharma-staples-review-batch.json).
CVX/MRK FY2021–2025 and PG FY2022–2026 cover15 exact annuals/210 families:
20 source-supported slots,185 proposed treatments,5 essential CVX EBIT exceptions.
Twenty-nine proposed decisions remain INACTIVE; the additional CVX perimeter row is
an OPEN exception, not an approval that can waive EBIT. No company completion.

CVX's mixed-tax affiliate/operating-benefit perimeter remains unproved; face Sales,
energy depletion-inclusive DD&A and exact replayed Capex do not repair EBIT.
MRK's original-as-filed continuing panels preserve Organon and acquisition scope;
five independently exact CFO checks coexist with original PARTIAL5, and first2
broader capital-expenditure proxies do not reverse the pure-PP&E NO-GO. PG exact
pretax extensions, broader cash QName, ESOP preferred/pension funding, D&A and
current borrowing/CP overlap are explicitly reviewed, not generic policies.

**42 broadly assessed;27 packages =22 completed scoped histories +2 approved partial
CAT/JNJ +3 pending CVX/MRK/PG;15 assessment-only.** CAT SBC/JNJ scope and all
original financial/history exceptions remain.0 missing essential artifact targets,
0 acquisitions. Sources, accepted views, frozen artifacts/pilot bytes are unchanged.
Validation is recorded in the batch results. Stop for ONE consolidated review;
no automatic approval, next-company cycle, Phase1 closure or Phase2 use.

## Historical checkpoint — LRCX/PLTR/AMAT approved historical completion

The user explicitly approves all27 LRCX/PLTR/AMAT recommendations. Effective
revision-bound analyst views/audits now select LRCX FY2022–2026 and PLTR/AMAT
FY2021–2025, each14/14 per year,70/70 per company.
[Authoritative schedules/dispositions/validation](semiconductor-software-review-batch-results.md)
/ [machine current counts](company-data-preparation/semiconductor-software-review-batch.json)
`/approval_activation`. Original source facts, nulls, proposals, alternatives,
timestamps and prior approvals remain unchanged; relevant revision changes reject
stale acceptance. Actual UTC, exact authority and source/decision hashes bind each audit.

LRCX accepts limited D&A and a broader combined PP&E/intangible investment proxy;
pure PP&E remains unknown. Plan obligations/assets are separate, not netted, and
finance leases are not added twice. PLTR preserves original PARTIAL4 and separate
exact displayed CFO proofs, selects face taxes without clearing rounded alternatives,
and treats no additional financing as an unbounded omission, not exhaustive debt zero.
AMAT preserves manufacturing/limited D&A, PP&E/software cash scope, noncash incentive
stock balances, SBC expense660/add-back668 and current-maturity/lease overlap limits.

**42 broadly assessed;24 packages =22 completed scoped histories +2 approved partial
CAT/JNJ;0 pending;18 assessment-only.** Nineteen previous completed histories,
CAT SBC/JNJ OPEN scope, XOM/history exceptions and frozen/pilot bytes remain unchanged.
No exhaustive debt/reinvestment, unrestricted cash, complete expense D&A, source
zero or immateriality claim is introduced. No Phase1 closure or Phase2 approval.
Next candidates CVX/MRK/PG are identified only from the existing retained backlog;
XOM remains empty and no new company review/acquisition is launched.

## Historical checkpoint — LRCX/PLTR/AMAT retained review, pending consolidated approval

[ONE27-decision sheet](semiconductor-software-review-batch-results.md) /
[machine review](company-data-preparation/semiconductor-software-review-batch.json)
and three company schedules/matrices cover LRCX FY2022–2026 and PLTR/AMAT
FY2021–2025:15 exact annuals/210 existing-family slots,30 source-supported income
observations and180 proposed company choices. All new treatments are INACTIVE.
Nineteen completed scoped histories remain unchanged; no new company completion.

LRCX's prior negative pure-PP&E split stands; broader combined productive-asset
investment and limited CFO D&A are proposed explicitly. Deferred-plan obligations
and correlated holdings, embedded finance leases, FY2024 53weeks and October2024
split remain separate. PLTR has five exact independent displayed CFO checks,
coexisting with original PARTIAL4/SUPPORTED1; face tax versus rounded prose,
expense/APIC/add-back, strategic customer investments and A/B/F voting/classes
are not conflated. AMAT preserves first-two direct D&A policies and later limited
proxies, manufacturing/inventory timing, gross investment versus incentives,
SBC660/668 and current-maturity/finance overlaps. No inferred zero or scope waiver.

**42 broadly assessed;24 packages =19 completed scoped histories +2 approved partial
CAT/JNJ +3 pending LRCX/PLTR/AMAT;18 assessment-only.** CAT SBC/JNJ OPEN scope,
XOM/history exceptions, original sources/ledgers, accepted views and frozen artifacts
remain unchanged.0 essential new acquisition targets/0 requests. Complete expense
D&A/reinvestment/debt, additional claims/restrictions/reserves and omission risks
remain explicit; proposals do not establish completeness or materiality.

A narrow no-inline-ID binding repair preserves actual parser/table locators,
exact context/unit/precision/value checks and existing ID-bearing serialized
outputs. Final focused validation is recorded in the batch results. No full-suite
or corpus rerun, financial acceptance, Phase1 closure or Phase2 use. Stop for one
consolidated user review; no automatic next-company research.

## Historical checkpoint — ABBV/MA/CSCO approved scoped historical completion

The user's explicit28-decision approval now activates ABBV/MA FY2021–2025 and
CSCO FY2022–2026 via existing revision-bound analyst views/audits.
[Authoritative schedules/dispositions/validation](pharma-network-tech-review-batch-results.md)
/ [machine current counts](company-data-preparation/pharma-network-tech-review-batch.json)
`/approval_activation`. Each company passes14/14 per year,70/70. Original facts,
source nulls, alternatives and proposal history are unchanged; relevant-content
revisions reject stale approval. Exact identities, actual UTC, authority and audit
SHA bind the accepted choices, not a new generic financial policy.

ABBV retains limited D&A, separate PP&E/acquisition/IPR&D, embedded financing/claim
overlaps and FY2024 additional-borrowing omission. MA selects face Net revenue
and face D&A, preserving generic gross/net ambiguity, exact curated Pretax and
client/settlement/restricted/corporate populations. CSCO selects rounded
impairment-inclusive D&A and FY2026 face financial15,918 while parent14,297 and
unexplained1,621 remain UNRESOLVED; no plug, rounding explanation or conflict clearance.

**42 broadly assessed;21 packages =19 completed scoped histories +2 partial CAT/JNJ;
0 pending;21 assessment-only.** CAT SBC/JNJ OPEN scope and prior16 complete packages,
frozen policies/outputs, pilot bytes and XOM/history exceptions remain unchanged.
Omissions are unbounded analyst assumptions, not reported zeros/immateriality.
No complete debt/reinvestment, Phase1 closure or Phase2 readiness certification.
Next unreviewed frozen-order candidates LRCX/PLTR/AMAT are identified only; stop
without new reviews, acquisitions or Phase2 work.

## Historical checkpoint — ABBV/MA/CSCO company review, pending one consolidated approval

[ONE28-decision sheet](pharma-network-tech-review-batch-results.md) /
[machine review](company-data-preparation/pharma-network-tech-review-batch.json)
and three source schedules/matrices cover ABBV/MA FY2021–2025 and CSCO FY2022–2026.
15 exact annuals/210 existing families:25 source observations/185 pending company
choices. All15 displayed CFO proofs remain SUPPORTED; movements stay within CFO,
not complete NWC/book delta or extra deductions. New treatments are inactive.

ABBV separates exact CFO amortization from rounded note expense, impairment/IPR&D,
cash investment and contingency roles; financing/claims parent overlaps remain.
MA proposes face net Revenue, preserving gross/rebate generic conflict; exact
curated Pretax approvals replay, corporate/client/settlement/restrictions and
claims remain separate. CSCO proposes rounded PPE plus total acquired-amortization
proxy, not opex-only or mixed CFO-other; Splunk/calendar and FY2026 cash-parent
scope alternatives remain explicit. No new financial policy or inferred zero.

**42 broadly assessed;21 packages =16 completed scoped histories +2 partial CAT/JNJ
+3 pending ABBV/MA/CSCO;21 assessment-only.** Prior18 accepted/partial package
JSONs, CAT SBC, JNJ OPEN scope, XOM/history boundaries and frozen artifacts remain.
No essential new acquisition target identified; zero requests. Source unknowns,
proxy precision and unbounded proposed omissions remain. Stop for consolidated
review; no automatic acceptance/completion, Phase1 closure or Phase2 use.

## Historical checkpoint — V/INTC/WMT approved scoped historical completion

The user-approved28 V/INTC/WMT treatments are now effective through revision-bound
analyst views. [Authoritative schedules, dispositions and validation](network-retail-review-batch-results.md)
/ [machine counts](company-data-preparation/network-retail-review-batch.json) `/approval_activation`.
V/INTC FY2021–2025 and WMT FY2022–2026 each satisfy14/14 per selected year (70/70),
with curated/limited-proxy/assumption labels and unbounded omissions retained.
Visa preferred/client/settlement/classes, Intel exact SBC/grants/NCI, Walmart face
Total revenues/generic conflicts/supplier-finance/lease/split boundaries remain explicit.
Original source snapshots, unknowns, proposals and alternatives are unchanged;
no new generic financial policy or reported zero. Relevant evidence changes reject stale audits.

**42 broad assessments;18 packages =16 completed scoped histories +2 partial CAT/JNJ;
0 pending reviews;24 assessment-only.** CAT SBC and JNJ OPEN scope requirements remain.
Prior13 completed histories, frozen artifacts, XOM and other history exceptions are preserved.
Scope completion is not exhaustive debt/reinvestment/expense disclosure, Phase1 closure
or Phase2 readiness. Next unreviewed retained-backlog candidates: ABBV, MA, CSCO,
identified only; no automatic new review, research or acquisitions.

## Historical checkpoint — V/INTC/WMT retained company review, pending one approval

[Three source schedules/14-family matrices and ONE28-decision sheet](network-retail-review-batch-results.md)
/ [machine review](company-data-preparation/network-retail-review-batch.json)
cover15 exact selected annuals: V/INTC FY2021–2025, WMT FY2022–2026.
25 source-observation slots/185 pending choices; none of the new company
judgments is active. All15 original displayed CFO checks replay SUPPORTED,
including Intel's independently bound child/adjustment-parent hierarchy.

Visa D&A v1/Capex v3 replay exact original artifacts within their existing scope;
client/settlement/escrow, investment and participating-preferred/class populations
stay separate. Intel proposes limited depreciation/intangible proxy, exact CFO
SBC over retained rounded alternatives, gross Capex/separate grants and related
co-investment NCI/funding. WMT proposes face Total revenues (including membership/
other income) while preserving every genuine generic Revenue conflict, exact
face cash/SBC, source D&A scope and supplier-finance/AP/lease non-overlap.
Calendar/split, acquisition, tax and missing-allocation limitations remain.

**42 broadly assessed;18 packages =13 completed scoped histories +2 approved
partial CAT/JNJ +3 pending V/INTC/WMT;24 assessment-only.** Prior13 complete
packages, CAT SBC exception, JNJ OPEN scope gate, XOM empty history and frozen
artifacts remain unchanged. All30 primary/instance pairs retained; Visa policy
artifacts replay; no essential new acquisition target identified, zero requests.
Legacy original report metadata gaps remain null. Field availability is not
complete disclosure or financial sufficiency. Focused checks/replay/preservation
and final lightweight results are recorded in the batch sheet. Stop for one
consolidated approval; no next-company review, Phase1 closure or Phase2 work.

## Current — MU/AMD complete within approved scope; JNJ historical selections active, scope OPEN

The user's explicit instruction activates all18 MU/AMD recommendations and ten
JNJ original-as-filed selections through existing revision-bound audits/effective
views. [Authoritative schedules and dispositions](priority-review-batch-results.md)
/ [machine current counts](company-data-preparation/priority-review-batch.json)
`/approval_activation`. Original source/proposal snapshots, nulls and alternatives
remain unchanged; actual UTC, user authority, rationale, identities, source/review/
proposal revisions and audit SHA256 bind every selection and reject stale sources.

MU FY2022–2026 and AMD FY2021–2025 each pass14/14 per year (70/70). Scoped
historical completion is recorded, not complete financial disclosure. MU retains
limited manufacturing D&A, gross PP&E/separate incentives, SBC differences,
tax scopes and embedded finance safeguards. AMD retains exact approved extension
proxies without generic policy changes; FY2025 continuing CFO6,493 versus separate
discontinued1,216/consolidated7,709, original PARTIALs and tax-tag anomaly persist.

JNJ remains **partial**. Its five original-as-filed panels are selected, while
`JNJ-ORIGINAL-AS-FILED-SCOPE` remains OPEN across nine flow families per year:
Revenue, EBIT, D&A, Capex, movements, deferred taxes, SBC, CFO and tax context.
This history-wide compatibility gate is45 family-period slots, not a demonstrated
error in all amounts.5/14 other limited-use operations per year satisfy the
approved scope;25/70 eligible-use slots, no completion. Resolution requires a
supported continuing/discontinued bridge/allocations or a separately justified
explicit analyst-use treatment; none is approved or researched here. Kenvue,
original presentations, dated cover shares and pension/talc overlaps remain.

**42 broadly assessed;15 packages =13 completed scoped histories +2 approved
partial CAT/JNJ;0 pending reviews;27 assessment-only.** Eleven prior completed
packages, CAT dual-perimeter/SBC exception, XOM empty history, frozen policies/
outputs and pilot bytes are unchanged. No source zeros, materiality findings,
complete debt/reinvestment, Phase1 closure or Phase2 authority are implied.
Final focused/replay/preservation and lightweight results are recorded in the
batch sheet. No acquisitions/full-suite/corpus run. Next candidates V/INTC/WMT
are identified from existing backlog/frozen order only; do not execute them here.

## Historical — MU/AMD/JNJ retained company review before explicit approval

[ONE consolidated decision sheet](priority-review-batch-results.md) and three
five-year schedules now cover15 exact frozen annuals/210 existing-family slots.
MU FY2022–2026 and AMD FY2021–2025 each have10 source-observation/60 pending
slots; JNJ FY2021–2025 has70 pending slots because its original-as-filed
continuing/consolidated perimeter requires a substantive explicit decision.
All28 recommendations remain inactive; no audit authorization or company
completion is inferred. Exact fiscal labels come from retained DEI, including
JNJ FY2021 ending2022-01-02 and FY2022 ending2023-01-01.

MU keeps incentive cash, manufacturing/capitalized D&A and inventory timing
separate. AMD proposes narrow exact D&A populations without reversing extension
gates; original two PARTIAL CFO proofs remain, alongside independently bound
display checks. FY2025 continuing6,493/discontinued1,216/consolidated7,709 are
not overlapping additions. JNJ replays five approved EBIT proofs, preserves
Kenvue original presentations and separately binds pension/talc populations.
No homogeneous continuing-only series or unsupported allocation is invented.

**42 broadly assessed;15 packages =11 completed scoped histories +1 approved
partial CAT +3 pending MU/AMD/JNJ;27 assessment-only.** Prior completed package
bytes, CAT dual-perimeter/SBC exception, XOM empty history, source evidence,
frozen financial policies/outputs and pilot artifacts remain unchanged.
All30 required primary/instance receipts are retained; no essential acquisition
target identified, no SEC request. Missing scope/allocations and unbounded
omission proposals remain explicit. Focused results and replay/link checks are
recorded in the decision sheet. Stop for consolidated approval; no other company,
automatic research chain, Phase1 closure or Phase2 implementation.

## Current — AVGO/TSLA/LLY effective approvals; eleven scoped histories completed

The user's explicit25-recommendation approval is now active through the existing
revision-bound company audit/analyst overlay. Each FY2021–2025 selection for
AVGO, TSLA and LLY passes the existing14-family checklist:70/70 per company,
210/210 across the batch. [Authoritative schedules and validation](large-company-review-batch-results.md)
/ [machine effective status](company-data-preparation/large-company-review-batch.json).
No remaining essential exception under those expressly approved historical
perimeters; original facts, nulls, proposal history and alternatives are preserved.

AVGO limited acquisition-amortization/depreciation excludes overlapping ROU;
embedded finance leases are not added again. TSLA's impairment-inclusive proxy,
consolidated manufacturing/energy/leasing financing assets/funding, tax benefit,
Capex gross/net/comparative and split boundaries remain. LLY retains limited
D&A, separate PP&E/cash-IPR&D/expense-IPR&D/acquisition populations, unchanged
derived EBIT and explicitly reviewed refreshed evidence with unavailable original
fingerprints/UNPROVED byte equivalence. Cover shares retain actual later dates.
Omission assumptions are analyst choices of unbounded possible exposure, not
reported zeros or immateriality; complete expense/reinvestment/debt remains unproved.

**42 broadly assessed;12 packages =11 completed scoped histories +1 approved
partial CAT;0 pending reviews;30 assessment-only.** Eight earlier completed views
and CAT's dual perimeters/SBC allocation exception are byte-unchanged. Original
financial blockers, support classes, history deficits and frozen/pilot artifacts
remain. No financial-sufficiency/Phase1 closure or Phase2 permission follows.
Focused checks/current replay/preservation, compileall and links/diff checks are
recorded in the batch results; no SEC/full-suite/corpus run.

[Updated market-cap-priority tracker](trillion-review-batch-results.md) recommends
MU, AMD and JNJ next using the retained snapshot order and five-year availability;
XOM's empty history is not invented. Recommendations only—stop after this
implementation, without acquisitions or another company review.

## Historical — AVGO/TSLA/LLY review before explicit approval

Delivered [three schedules and14-family matrices plus ONE approval sheet](large-company-review-batch-results.md)
and [machine decisions](company-data-preparation/large-company-review-batch.json).
15 exact annuals /210 family slots:50 source-observation,160 pending company-choice
slots; all15 independently displayed CFO checks SUPPORTED. No new acceptance,
financial-policy/runtime change, research acquisition or phase closure.

AVGO proposes narrow depreciation/acquisition-amortization proxy, not mixed ROU,
with VMware/restructuring/53-week and split boundaries. TSLA proposes explicit
impairment-inclusive limited proxy and consolidated manufacturing/energy/leasing
perimeter; finance receivables/funding, net cash-purchase captions and tax conflicts
remain separately evidenced. LLY replays approved EBIT operands and five exact
refreshed-Capex reviews, preserving unavailable originals/UNPROVED equivalence;
cash/licensing/IPR&D, expense milestones and CFO addbacks are not interchangeable.
Named financing already includes finance leases; no second addition or complete-
debt claim. Restrictions, claims, allocations and complete expense scope remain
unknown; only explicit future user approval can activate proposed assumptions.

42 broadly assessed;12 packages = **8 completed scoped histories +1 approved
partial CAT +3 pending reviews**;30 assessment-only. Completed peers and CAT's
dual perimeters/SBC exception are unchanged. Frozen artifacts, source histories,
financial blockers and support classes persist. No requests/full-suite/corpus run.
Focused results/replay/preservation and final checks are recorded in batch results.
Stop for consolidated approval, not another company or Phase2 implementation.

## Current — six-company approvals implemented; eight scoped histories complete

Explicit user approval activates all23 standard-batch and25 trillion-batch
recommendations through revision-bound company audits and separate effective
`current_history` views. Original proposals/source nulls/flags remain historical;
the active view, not an edited reported fact, selects the approved values.
[Standard results](standard-review-batch-results.md) /
[trillion results](trillion-review-batch-results.md) and six authoritative schedules
record sources, assumptions, precision, alternatives, actual UTC authorization
records and stale-content rejection. No acquisition or generic financial policy.

COST, KO, NVDA, AMZN and META each satisfy five selected years×14 families within
their approved historical perimeters. COST's finance-amortization non-overlap is
an accepted assumption. NVDA combined PP&E/intangible proxy includes exact extension
years without supplying pure PP&E. AMZN selects narrow D&A and2021 expanded
financing81,427 including the later-source-bound318; broad D&A rejection persists.
META independent display checks coexist with three original parser PARTIALs.
KO named financing stays45,492 in2025, with held-sale borrowing1,435 separately
visible; conditional46,927 is not selected or silently combined.

CAT's industrial and Financial Products supplemental perimeters are active,
each13/14 in all five years. Consolidated observations remain descriptive and
direct consolidating adjustments are support, not a standalone company. Exact
essential gap: perimeter SBC expense allocation. Consolidated expense cannot
fill it. CAT-FIN's approved named-funding/no-unidentified-adjustment treatment
is active; unallocated lease detail remains a supporting unknown, not a demand
for complete-debt proof. Named funding,
tax/cash/operating inputs and independently reconciled perimeter CFO are active;
CAT-SBC is approved but its effective perimeter number remains blocked. No
standalone subtraction, funding/asset mixing, support reclassification or segment
valuation. CAT is not completed; continue no further batch automatically.

Counts:42 broadly evidence-assessed;9 company packages = **8 completed scoped
histories** (MSFT/AAPL/Alphabet/COST/KO/NVDA/AMZN/META) + **1 approved partial CAT**;
33 assessment-only. Original five-year deficits, source unknowns, financial
blockers and frozen/pilot outputs persist. Scoped completion does not certify
complete economic balances, financial sufficiency, whole-universe completion,
Phase1 closure or Phase2 readiness. Validation below is historical unless the
current approval results sections explicitly identify it as current.

## Current — NVDA/AMZN/META consolidated review, proposals inactive

[ONE decision/exception sheet](trillion-review-batch-results.md) and
[machine batch](company-data-preparation/trillion-review-batch.json) cover15
exact selected annuals/210 families: NVDA FY2022–26 20 source-supported/50
pending; AMZN FY2021–25 20/50; META FY2021–25 25/45. These are review
dispositions, not missing-fact counts or complete-field approvals. All25 new
judgments remain inactive; COST/CAT/KO proposals remain unchanged/inactive.

NVDA proposes combined cash PP&E/intangible purchases976/1,833/1,069/3,236/
6,042m with separate extension gates; original pure-PP&E rejection remains.
AMZN's five negative broad-D&A reviews persist; proposed narrow expense proxies
23,421/25,528/30,931/32,905/42,677 are a distinct inactive analyst operation,
not a frozen equation or source completeness finding. Named financing retains
separate facility financing, CP/working borrowing and the2021-end318 comparative
explicitly bound to its FY2022 source. META's three shared CFO parser PARTIALs
remain beside separate exact primary-row/dimension arithmetic, not overwritten
proofs or altered tolerances. All30 selected bodies and actual receipts retained;
no acquisition target/request, accepted assumption or company-completion claim.

42 broad assessments;9 company packages =3 completed scoped MSFT/AAPL/Alphabet
+6 reviewed/pending COST/CAT/KO/NVDA/AMZN/META;33 broad-only.40 generalization
records plus2 supported seeds and all frozen support classes persist. Financial
perimeters, unbounded omissions and class/split comparability need consolidated
review, not automatic research. Validation is in the
[batch results](trillion-review-batch-results.md#validation-and-preservation).
No Phase1 closure/Phase2 authority. Older sections retain dated checkpoints;
their candidate instructions/counts do not supersede this current state.

## Current — COST/CAT/KO one retained-evidence review batch, all choices pending

[ONE batch approval/exception table](standard-review-batch-results.md) and three
company packages cover15 exact frozen annuals/210 family slots: COST FY2022–26
32 source-supported/38 pending; CAT FY2021–25 0/70 (financial perimeter gate,
not missing facts); KO FY2021–25 35/35. All15 displayed CFOs independently replay
exactly against the existing source-bound ledger. All30 primary/instance bodies
and actual receipts retained; no acquisition list or new SEC request.

COST proposes limited D&A+finance-amortization proxies2,028/2,246/2,334/2,528/
2,780, not complete expense D&A; direct note finance components repair missing
old selectors, and known FY2022 short borrowing88 is included. Mixed FY2023–25
deferred-tax/impairment rows remain mixed, no invented pure component or zero.
CAT needs an explicit industrial/captive-financing perimeter, not ordinary
consolidated operating-only use. Supplemental industrial CFO7,177/6,358/11,688/
11,437/12,278 and funding/cash/lessor assets differ from consolidated scopes;
intercompany eliminations and financial receivable/insurance populations prevent
mechanical mixing. No support reclassification or analyst-complete result.
KO retains reported CFO impacts from IRS deposit6.0bn in2024 and fairlife6.1bn
operating cash in2025; D&A proxy/expense roles, restricted cash, pension gross/net
and held-sale debt1,435m stay explicit. No normalized CFO, unproved lease addition,
claim netting, future tax rate or economic adjustment.

All23 company/period-bound proposals are inactive, in ONE consolidated table;
review does not record approval. Counts42 broadly assessed;6 company packages =
3 previously completed MSFT/AAPL/Alphabet +3 reviewed/pending COST/CAT/KO;
36 broad-only. Original completed views, evidence, frozen policies/outputs and
pilot bytes remain unchanged. Stop for consolidated user review, not another
company/research queue, Phase1 closure or Phase2 implementation.

Validation:16 distinct focused gates are satisfied:15 cases (including five
legacy/pilot/frozen preservation tests) passed on the final executable code in
`/tmp/standard-review-batch-final-tests.log`; its remaining exact generated-file
replay gate passed after regeneration in30.754s in
`/tmp/standard-review-batch-final-replay.log`. Do not describe that earlier16-test
command as an all-green run: it rejected a stale CAT support snapshot after
leased-to-others rows were added. Regeneration preserved the exact equality check.
An earlier financial/source test also exposed KO held-sale facts' extension
namespace; the selector was corrected, not the expected1,435m amount or scope.
No source assertion/financial expectation was weakened to obtain a pass.

All15 annual CFOs replay exactly; original body/receipt, raw occurrence, unit,
precision, sign, primary table/inline, CAT supplemental and COST note arithmetic,
KO overlap/benefit/share roles, inactive proposals and serialization checks pass.
All three completed company package replays, compileall,745 affected/new local
links,604 batch/field/selection references,15-period/210-slot reconciliation and
diff checks pass. Original three completed JSON views, runtime/normalization,
source/evidence, original pilots and frozen artifacts remain unchanged. No
acquisition/full-suite/corpus run. Logs also:
`/tmp/standard-review-completed-peer-replays.log`,
`/tmp/standard-review-batch-links.log`. No remaining technical failure is known;
financial judgments/perimeter requirements in the ONE decision table remain open.

## Current — Alphabet approved five-year historical perimeter completed

[Authoritative Alphabet schedule](company-data-preparation/GOOGL-analyst-input-package.md)
and additive current JSON overlay record explicit G1–G8 user approval, sequence2,
linked to the previous FY2024 audit and exact five-year source/review revisions.
All five selected FY2021–25 periods pass14/14 (70/70) within the approved perimeter.
Original facts/nulls/proposals/alternatives and completed MSFT/AAPL views persist.
Counts:42 broad assessments;3 completed company packages MSFT/AAPL/Alphabet;
0 partial company packages;39 broad-only. These are not42 complete issuers.

Accepted D&A11,555/15,287/11,946/15,311/21,136 are labeled limited proxies, with
early impairment inclusion and omitted components, not verified complete expense
D&A (still null). Named financing14,930/14,999/14,616/15,859/51,043 retains early
finance inclusion, source unknown extra borrowing and approved unbounded omission.
Gross current financial balances retain known restrictions and unknown reserves;
claims/pension omissions remain assumptions, not zeros/immateriality. FY2025
operating lease parent15,954/components15,953m difference remains unresolved and
never changes financing51,043. No residual scalar; movements already in CFO are
not extra deductions. Dated share classes, original pre-split2021 and2022 split
boundary stay distinct. No complete debt/reinvestment certification, support-class
change, Phase1 closure or Phase2 authority. Prior review/count sections are dated
history, not the authoritative current outcome.

Validation:72 focused approval/company-review/package/cash/NWC/peer and legacy
preservation tests pass in112.871s. All five14-family checks, exact G1–G8 wording
and prior-audit linkage, proxy/null distinctions, named amounts, lease discrepancy,
SBC precision, source receipt history, JSON round trips, persisted restart and
stale/tampered/changed-identity rejection pass. All three exact package replays,
compileall,600 affected local-path links,300 current-view internal references,
three candidate/backlog joins and diff checks pass. MSFT/AAPL JSON bytes, previous
Alphabet package (excluding only two additive current/audit keys), frozen/runtime
source, original evidence and pilot hashes remain exact. Logs:
`/tmp/googl-history-accepted-tests.log`, `/tmp/googl-history-accepted-replays.log`,
`/tmp/googl-history-accepted-links.log`. No acquisitions/full-suite/corpus rerun.

Next recommended standard-review candidates from the existing backlog: **COST,
CAT, KO**. Each has five retained selected annuals, supported displayed CFOs and
prepared scalar evidence; COST additionally has eight CHECKED latest independent
fixtures. Reuse the company-wide source/overlap/approval mechanics, not accepted
financial assumptions. Exact backlog rows4/3/6, rationale and outstanding scope
checks are in the [current assessment](analyst-complete-historical-assessment.md).
None has been reviewed/approved by this milestone; do not execute automatically.

## Historical — Alphabet five-year review, one consolidated approval table

[Alphabet company package](company-data-preparation/GOOGL-analyst-input-package.md)
and its additive JSON review bind the five exact FY2021–25 annual selections and
70 family slots:29 source-supported,9 original FY2024 scoped approvals,32 pending
new treatment slots. No new judgment is active; G1–G8 await one consolidated user
review, G9 is source packaging context only. All five independently displayed CFOs
reconcile (14/14/13/13/13 terms, seven acquisition-excluded movement rows each).
Ten retained bodies/usable receipts verify; original instance metadata gaps remain
null and explicit refresh history survives. No new acquisition requirement.

Critical limits: early D&A includes impairment; complete expense D&A unknown.
Early debt captions already include finance leases/other, unlike FY2024 onward;
no double addition. FY2025 operating lease parent15,954 versus components15,953m
is a retained1m source difference, not a balancing adjustment. Pension/extra
borrowing omissions remain unbounded proposed assumptions, not zero/immateriality.
Rounded SBC expense and CFO add-back remain distinct;2025 Waymo valuation-based
compensation, acquisitions, useful lives and2022 share split limit comparability.

Counts unchanged:42 broad assessments;2 completed MSFT/AAPL packages,1 partial
Alphabet,39 broad-only. AAPL's five-year approval and MSFT completion are preserved;
no whole-universe sufficiency, frozen-blocker removal, Phase1 closure or Phase2.
Prior dated assessments below are historical snapshots, not current defaults.

Validation:70 focused tests pass in60.129s (nine new company-history checks plus
Alphabet package/audit/cash/NWC, AAPL history acceptance/review and MSFT history
acceptance regressions); five additional legacy serialization/frozen/pilot
preservation tests pass in21.207s. All three exact package replays, compileall,
576 affected local-path links, five manifest joins/175 family fact references
and diff checks pass. An initial test used default28-digit decimal precision
against the existing34-digit ETR result; its independent arithmetic now uses
that existing precision, without changing financial values or assertions.
Prior Alphabet package after stripping only the additive review key and both
completed peer JSON packages remain exact. No SEC requests, full-suite or corpus
rerun. Logs: `/tmp/googl-company-final-tests.log`,
`/tmp/alphabet-company-preservation-tests.log`,
`/tmp/alphabet-five-year-package-replays.log`, `/tmp/alphabet-company-links.log`.

## Current milestone — AAPL approved five-year historical-input completion

[Authoritative schedule](company-data-preparation/AAPL-analyst-input-package.md)
and current JSON overlay record explicit A2–A10 approval exactly as proposed,
sequence2 at2026-10-17T15:56:35.868488+00:00, linked to previous FY2025 audit and
exact company review revision. All five selected FY2021–25 periods pass14/14
(70/70) within the approved historical-input perimeter. Prior sources/nulls,
approvals/proposals, alternatives and MSFT completed result remain unchanged.

CFO-D&A11,284/11,104/11,519/11,445/11,698 are approved proxies, **not verified
expense D&A**, which stays unknown. Gross current financial balances retain known
restrictions; FY2024 gross65,171 is selected,49,371R non-default. Named financing
and no preferred/NCI/pension/additional-borrowing adjustments retain source nulls
and explicitly accepted unbounded omission risk, not immateriality or complete
debt. Reported movements explain independently reconciled CFO, not extra
deductions; complete reconstructed NWC is not required. No reinvestment total,
forecast, valuation or Phase1 closure. Counts:42 broad assessments,2 completed
company packages (MSFT/AAPL),1 partial Alphabet,39 broad-only.

Validation:82 focused tests pass in54.446s (6 new history-acceptance tests plus
existing AAPL history/package/audit, MSFT completion, Alphabet package, AAPL cash
and NWC preservation). All-three package replays, compileall,579 affected local
path links and diff checks pass. Restart testing exposed JSON-map-order-dependent
exception ordering; replay now uses the original reviewed specification order,
preserving the exact prior review/financial data rather than weakening equality
or changing approval hashes. Corrected restart/tamper/stale gates pass; prior
package after stripping only two additive keys remains exact. No full-suite,
corpus run or SEC request. Logs: `/tmp/aapl-history-approved-final-tests.log`,
`/tmp/aapl-approved-final-replays.log`, `/tmp/aapl-approved-links.log`.
Part2 Alphabet company review is separately authorized; no new Alphabet judgment
has been approved.

## Prior checkpoints

## Current milestone — AAPL one five-year retained-evidence company review

[Existing package](company-data-preparation/AAPL-analyst-input-package.md) /
[JSON](company-data-preparation/aapl-analyst-input-package.json) add only
`/aapl_history_review`, preserving the whole previous FY2025 payload and audit.
Manifest confirms FY2021–25 rows5–9, ten original primary/instance receipts and
authoritative dates, including53-week FY2023. All70 family slots accounted for:
27 source-supported/8 previously scoped approvals/35 pending new treatments.
No newly active numerical assumption or analyst-completeness result.

All five independently displayed CFOs tie104,038/122,151/110,543/118,254/111,482m;
selected displays have12/12/10/10/10 terms,7/7/6/6/6 movements. Earlier separate
deferred-tax/revenue rows and later comparative regroupings are preserved. Follow
the instructed reported-movement/CFO path without requiring reconstructed NWC or
deducting rows again; no Phase2 formula. Existing FY2025 partial operating capital
and other approvals stay within original scope, not extended to older annuals.

One consolidated table has nine pending judgments A2–A10 (A1 is source-supported
context, not another methodology approval): explicit CFO-D&A proxy versus unknown
complete expense D&A, SBC once, lease/financing convention and unbounded additional
borrowing omission, gross financial balances/known restrictions, preferred/NCI/
pension omissions, deferred-tax/claims and residual operation scope, dated shares.
No MSFT financial assumption is transferred. Source nulls and alternative
perimeters/precision persist. Source-supported principal/carrying bridges and
FY2024 restricted-current alternative49,371R are separately identified, not
complete debt/excess cash or accepted new adjustments. No amount is deemed
immaterial, no amortization inferred by subtraction, and no balancing item.

All ten bodies/receipts are retained; no exact additional artifact identified.
Remaining gaps are disclosure/scope/timing or user choices, not an acquisition
queue. MSFT completed5×14/14, Alphabet accepted view, original AAPL approvals,
pilot bytes and frozen policies/outputs stay unchanged. Counts remain42 broad
assessments,1 completed company-wide MSFT,2 partial AAPL/Alphabet,39 broad-only.
No universe/Phase1 closure; stop for consolidated AAPL review.

Validation: **104 focused tests pass in52.020s**, including10 new company-history
checks and existing AAPL package/acceptance, MSFT five-year acceptance/history,
MSFT/Alphabet package preservation, original AAPL cash-input and NWC-bundle tests.
All three exact package replays, compileall (`src scripts tests`),574 affected
Markdown local-path links and `git diff --check` pass. Tests pin selected statement
values,12/10-term CFO arithmetic, signs, rounded precision, manual-note versus
XBRL provenance, principal alternatives/hedge signs, restriction dates/scope,
dated shares/awards, inactive proposals, serialization and receipt/date rejection.
Original AAPL package equals prior HEAD after removing only the one additive
review; its audit and MSFT/Alphabet package bytes are unchanged. Existing approval
restart/stale/tamper tests and original/frozen/pilot preservation pass. Local-path
checks do not verify live URLs/all historical anchors. Durable local logs:
`/tmp/aapl-company-history-final-tests.log`,
`/tmp/aapl-company-history-package-replays.log`,
`/tmp/aapl-company-history-links-and-counts.log`. An initial focused invocation
named a nonexistent NWC test module; the corrected final104-test gate above passes,
without changing source assertions. No full-suite/corpus run or SEC requests.
Earlier checkpoints below retain their then-current scope.

## Prior milestone — MSFT approved five-year historical-input completion

[Authoritative current schedule](company-data-preparation/MSFT-analyst-input-package.md)
and [JSON](company-data-preparation/msft-analyst-input-package.json)
`/msft_current_history` activate exact user H1–H9 approval, E1 supporting
limitations and E2 FY2024 faceCP6,693m (rounded6,700 alternative, no adjustment).
Revision-bound audit sequence6 at2026-10-17T15:20:51.650842+00:00 links the exact
preceding package and sequence5, preserving all earlier source/approval/proposal
history. All five frozen FY2022–FY2026 periods pass the existing14 families:
**70/70; MSFT completed for the approved historical-input perimeter**.

Reported movements and independently reconciled14-term CFO are the active path;
complete reconstructed NWC/book delta is not required, supporting movements
already in CFO are not additional deductions. Approved unproved finance-D&A
overlap, named financing/no extra adjustment, SBC proxy once, claim assumptions
and operation exclusions remain explicit. Source borrowing/claims and older
capital-creditor/equity-method subamounts stay unknown. No complete debt,
reinvestment, unrestricted/excess cash, organic cash, FCFF or Phase2 certification.
Acquisition/presentation/precision, restriction/reserve and timing limits persist.

Company counts:42 broad evidence-assessed;3 company analyst packages comprise
1 completed company-wide MSFT and2 partial AAPL/Alphabet;39 broad-only. Original
40-register/42 non-specialized/199-period/210-target/11-deficit inventory,
eight specialized exclusions, frozen classifications/outputs and original four
pilot bundles are unchanged. No universe/Phase1 closure or automatic next issuer.
Next company-level backlog batch identified: AAPL frozen FY2021–25; not begun.

Validation: **161 focused tests pass in117.223s**, including8 new whole-history
acceptance checks plus all earlier MSFT approvals, three issuer packages, original
input/sidecar/NWC and assessment preservation. All three exact package replays,
compileall (`src scripts tests`),576 affected Markdown local-path links and
`git diff --check` pass. Exact preceding MSFT package equality after stripping
only the two new keys proves original sources/proposals/audits unchanged; frozen,
pilot and AAPL/Alphabet preservation tests pass. Receipt/source replay,70-slot
accounting, cash signs/precision, E1 unknowns, CP alternatives, audit restart,
tamper/stale rejection and current source references are covered. Logs retained
in `/tmp/msft-history-acceptance-tests.log`, `/tmp/msft-history-package-replays.log`
and `/tmp/msft-history-links-and-preservation.log` (local diagnostics, not source
evidence). Link validation checks local paths, not live URLs/all historical
anchors. No full-suite/corpus run or SEC requests. Earlier milestones below are
historical checkpoints.

## Prior milestone — MSFT company-history batch and FY2025 acceptance

[Updated existing package](company-data-preparation/MSFT-analyst-input-package.md) /
[JSON](company-data-preparation/msft-analyst-input-package.json) record explicit
approval25-D1–25-D7 at2026-10-17T14:46:27.138553+00:00, sequence5 linking prior
audit/revision. FY2025 scoped14/14 now passes, named89,323m financing/no extra
borrowing adjustment; source unknowns and CP-only zero preserved. FY2026 scoped
14/14 remains exact. No original facts/audits/proposals or AAPL/Alphabet changed.

Manifest selects FY2022–26. All remaining FY2022–24 are reviewed together, using
six retained exact primary/instance bodies/receipts and existing fact/context/
precision/sign/provenance machinery. All70 period/family slots covered. Older
14-term CFO displays independently tie89,035/87,582/118,548. Proposed expense
D&A14,600/13,500/20,000R, current financial104,757/111,262/75,543 and named
financing64,683/64,304/78,775 remain inactive. FY2024 includes faceCP6,693; rounded
note6,700 remains alternative, no plug. Older MSFT extension namespaces and actual
note numbers, acquisition scope, dated shares/awards and rounded precision retained.

ONE H1–H9/E1–E2 approval/exception table consolidates all older choices and named
binding/scope gaps. No missing original body or identified new official artifact;
no SEC acquisition/research queue. Supporting creditor/equity-method gaps remain,
not zero/immateriality. No older-period assumption approval or issuer certification.

Contract/methodology clarify active reported-movement/reconciled-CFO path: complete
reconstructed NWC/book ΔNWC is not prerequisite; NWC stays supporting; movements
already included in CFO are not additional deductions. No Phase2 formula,
valuation consumption, universe/Phase1 closure or automatic next company.

Validation:153 focused tests pass in90.114s (seven new company-batch tests plus
all earlier approval/package/input/sidecar/NWC/assessment preservation). All-three
exact package replays, compileall,606 links and diff checks pass. Five identities/
70 slots reconcile; older24 source-supported versus18 pending family treatments.
Entire prior package/audit/proposal history preserved after stripping only two
additive keys; original pilot/frozen/AAPL/Alphabet sources unchanged. Receipt,
source arithmetic, CP precision, audit persistence/staleness and serialization
tested. No full-suite/corpus rerun; stop for the consolidated MSFT table.

## Prior milestone — bounded MSFT FY2025 analyst-input review

[Existing package](company-data-preparation/MSFT-analyst-input-package.md) /
[JSON](company-data-preparation/msft-analyst-input-package.json) add one revision-
bound proposal-only review:14 families,10 satisfied within prior scope and4
pending. Seven decisions are consolidated: FY2025 reported-movement path, residual
exclusion, combined DTA/no pure NOL, presentation-based preferred/NCI/retirement
assumptions, and named89,323 financing/no extra broader borrowing adjustment.
None is active or inherited from FY2026. Source CP0 is affirmative CP-only proof,
not a complete borrowing balance. Missing claims/other borrowing have no bound.

Retained statement/notes/inline instances verify 14-term136,162 CFO equality,
equity343,479 and balance619,003 partitions. Earlier prose13 terms is corrected:
13 adjustments plus net income,14 terms; source numbers remain unchanged. New
review preserves selected FY2025 presentation versus later comparative presentation.
Original14 nulls are dispositioned; no filling, invented estimates, new required
fields, research or financial approvals. FY2025 remains pending, FY2026 14/14 PASS
and all old views/audits/sources/pilot/frozen bytes persist. No Phase2 or phase
closure. Stop for all seven decisions together, not sequential memos/next issuer.

Current validation:146 focused tests pass in79.219s (six new FY2025 tests plus
existing financial-selection/approval, three packages, input/sidecar/NWC and
assessment preservation). All-three exact package replays, compileall,558 links
and diff checks pass. Exact primary/source facts,14-term arithmetic, proposal/
null accounting and wrong-period/tamper rejection tested. Entire prior package,
FY2026 PASS and audit chain preserved after stripping one additive review key.
No full-suite/corpus rerun or SEC acquisition. Stop pending consolidated approval.

## Prior milestone — MSFT FY2026 financing acceptance and scoped checklist PASS

[Existing package](company-data-preparation/MSFT-analyst-input-package.md) /
[JSON](company-data-preparation/msft-analyst-input-package.json) append sequence4
user approval recorded2026-10-17T08:33:44.502600+00:00, exact source revision and
supersession links. Active106,888m named financing/no additional short-borrowing
adjustment is an approved analyst assumption. Source null, rejected-adjustment
history and failed bridge remain. No reported zero, complete debt, immateriality
or supported bound on omitted borrowing. Current maturities/CP assets not added.

The existing14-row FY2026 checklist passes **only under the explicitly approved
historical perimeter/assumptions/exclusions**; no essential requirement remains
there. D1–D3 and prior claim/input approvals persist. Source/partial-scope gaps,
six expanded-operation supporting limitations and five Phase2 operations remain
explicit, not newly waived or certified. No whole-history/Phase1/universe closure
or Phase2 readiness. Next existing target identified only: B1 MSFT FY2025,
requiring independent assessment, not automatic transfer/execution. No SEC
request, research, new policy or valuation calculation.

Validation:140 focused tests in71.555s, all-three exact package replays,
compileall,551 affected links/retained review anchor and diff checks pass.
Entire prior package equals baseline after stripping only two additive keys;
original nulls/audits/rejections, frozen/pilot artifacts and other issuer views
preserved. Supersession, stale-source/revision, persistence/restart and round-trip
checks pass. No full-suite/corpus rerun; stop after this exact-period milestone.

## Prior milestone — bounded MSFT FY2026 short-borrowing bridge review

[Existing MSFT package](company-data-preparation/MSFT-analyst-input-package.md)
records outcome3: **unresolved**, no new assumption/approval or runtime integration.
Opening FY2025 zero covers CP only, while FY2026 reported net0 covers ≤90-day debt
cash flows; prior CP tenors28–152 days establish a concrete population mismatch.
FY2026 >3-month cash proceeds0/repayments3,000 and disclosed term-table movements
do not close the missing issued-short-borrowing bridge. Noncash/acquisition/FX/
reclassification and broader opening-population coverage remain unquantified.
Current term9,227 remains inside named106,888m financing; CP investment excluded.

One bounded retained review of debt/liquidity/cash flow, acquisition/FX policies
and lease financing adds exact scope/precision and descriptive change checks.
No named existing incremental official document established; required disclosure
and stop condition documented without an acquisition queue. All four body digests,
existing fact occurrences and arithmetic verified. Original package JSON/audits,
nulls/rejected zero, prior assumptions and frozen/pilot data unchanged. No SEC
requests, executable changes, tests/full-suite/corpus or Phase2 work/closure.
481 affected local links and diff checks pass. Only four Markdown files change;
earlier test results below remain historical validation of unchanged code.

## Prior milestone — MSFT FY2026 approved claim assumptions

[Existing package](company-data-preparation/MSFT-analyst-input-package.md) /
[JSON](company-data-preparation/msft-analyst-input-package.json) append sequence3
explicit user approval recorded2026-10-17T08:23:38.084820+00:00. No additional
preferred/NCI adjustment, and retirement expense without a separate pension
adjustment, are approved **analyst assumptions** for FY2026 only. Exact prior
package revision, evidence/rationale and sequence2 predecessor are bound through
the existing embedded audit/overlay mechanism. Original nulls, sources, rejected
alternatives, D1–D3, accepted selections and all prior package keys are unchanged.

No adjustment economically omits a potentially undisclosed claim; size is not
bounded. International retirement coverage remains incomplete. Only those three
adjustment requirements are addressed, not source disclosure gaps. Additional
issued short borrowing remains the essential historical requirement for this
attempt: null, rejected zero unchanged, named106,888m financing incomplete.
Expanded-scope supporting gaps remain visible; tax/economic/timing/dilution
consumption decisions remain Phase2. No automatic completeness/sufficiency or
Phase1 closure, research, acquisition, generic policy or valuation changes.

Validation:134 focused tests pass in67.643s (five new assumption tests plus
operations/attempt, MSFT/AAPL/Alphabet, original inputs/sidecars/NWC and assessment
preservation). All-three exact package replays, compileall,488 local links and
diff checks pass. Entire prior package and audit chain remain equal after
stripping only the two additive keys; source/pilot/frozen and other accepted
views preserved. Persistence/restart, stale/malformed authorization and changed
source rejection pass. No full-suite/corpus rerun. Stop after this milestone.

## Prior milestone — MSFT FY2026 operation approval and targeted official review

[Existing package](company-data-preparation/MSFT-analyst-input-package.md) /
[JSON](company-data-preparation/msft-analyst-input-package.json) embed the explicit
D1–D3 consent (recorded2026-10-17T08:04:57.424386+00:00), source commit/revision
and original-audit hash link. Effective operation view accepts nine reported CF
movements/14-term CFO reconciliation; excludes a separate residual **without zero**;
retains combined loss/credit DTA, no pure-NOL economic asset. Old audit file,
accepted parent, nulls and prior decisions are preserved exactly. No new sidecar.

Fixed review reuses the exact official annual primary/instance. Full displayed
current liabilities168825m, liabilities315989m, equity442387m and balance758376m
tie to independently retained child populations. Relevant consolidation, debt,
lease, equity and savings-plan disclosures are reviewed together, not keyword
absence. No separate issued CP/short borrowing, preferred/NCI or pension funded
status amount established:all four stay null. Named106888m financing unchanged;
CP2987m is investment assets, common authorization24000m is not preferred issued,
and retirement expense1800R is not pension debt or an extra adjustment.

**Neither gap group resolved.** D1–D3 acceptance does not waive unrelated missing
populations. No supported new numerical proposal, uncertainty bound or materiality
claim. Zero new documents/HTTP requests:exact annual already retained; no precise
incremental official source identified for the missing June30 allocations/claims.
No earlier/later balances substituted. No source/policy/frozen/pilot value changes,
SEC acquisition, Phase2 calculation, analyst completeness or phase closure.

Current validation:129 focused tests pass in62.950s, including six new approval/
population tests and relevant package/input/sidecar/NWC/assessment preservation.
All-three exact package replays, compileall,472 affected local links and diff
checks pass. Entire prior package/attempt is unchanged after stripping only the
two additive keys; original audit and AAPL/Alphabet/frozen/source bytes preserved.
Measured review-through-verification window638s,2026-10-17 08:01:44–08:12:22 UTC,
includes reasoning and waits, not hypothetical reviewer effort. No full-suite or
corpus rerun; stop after this fixed pass, without a new research queue.

## Prior milestone — one-period MSFT FY2026 completeness attempt

[Existing package](company-data-preparation/MSFT-analyst-input-package.md) /
[JSON](company-data-preparation/msft-analyst-input-package.json) append a decision-ready
review for exact `0001193125-26-323660`, FY2026 only, after unchanged acceptance
verification. Proposed historical purpose identifies required named observations
and operations, not a demand for every conceivable component. Eleven named
requirements are satisfied in their scoped sense, residual exclusion pending and
two essential financial populations unresolved. This is **not eleven complete
generic field families** or a completeness approval.

The14 original nulls now have explicit operation/evidence/reason dispositions:
6 supporting,5 future-operation requirements,1 pending pure-NOL exclusion and
2 unsolved essentials. All originals remain. Correct descriptive CFO count to14
in FY2026 (deferred-tax14189 separate), versus13 in FY2025; original182935m
equality already correct. Bind dimensioned Note4 CP2987m as investment assets,
never a substitute for missing issued debt. Keep legal553m accrual and400m
possible additional loss separate; no artificial953m deduction.

Proposed D1 reported-movement path, D2 no residual scalar in complete displayed
reconciliation, D3 combined DTA disclosure/no separate pure-NOL economic asset
remain pending. Even acceptance would not resolve short borrowing or complete
recognized preferred/NCI/pension populations. No defensible number/bound supplied;
short borrowing remains null, rejected zero not revived. Settled partial capital,
rounded D&A inclusion assumption, named financing/current financial balances and
all prior proposals/accepted views/frozen values persist unchanged.

Actual measured implementation checkpoint471s (2026-10-17 07:38–07:45:51 UTC)
includes interactive reasoning and waits, not reviewer-days or a new all42 deadline.
No SEC requests, universe reassessment, generic policy change, economic calculation,
financial sufficiency, phase closure or automatic next research/company work.

Final current-tree validation: **123 focused tests pass in59.790s** (new attempt8,
MSFT package21, AAPL17, Alphabet18, original inputs22, sidecars24, NWC8,
historical assessment preservation5). All-three package replays, exact original
accepted parent and extraction/audit logic, original pilot/frozen artifacts,
source/class/date/unit/precision/pointers, persisted audit/stale rejection,
compileall,467 affected local links and diff checks pass. Historical assessment
tests now pin their stated original baseline; no new universe inventory generated.
An intermediate test-only uncached JSON parsing bottleneck was interrupted and
fixed by memoizing the identical baseline; no weakened financial checks or new
expected values. Only the completed final run is claimed current. Instrumented
review-through-verification window813s,07:38–07:51:33 UTC includes reasoning,
waits and the interruption, not hypothetical human reviewer budgets.

## Prior milestone — analyst-complete historical-input work assessment

[Consolidated assessment](analyst-complete-historical-assessment.md) /
[reproducible JSON](analyst-complete-historical-assessment.json) join current
coverage, exact population/CFO proofs, issuer records, frozen mappings and scoped
pilot approvals. **42 histories / 199 selected annuals / 210 target slots / 11
deficits / 2,786 field-family slots** reconcile. Previous40-record189-period
cohort plus META/COST ten periods explains the scope difference; no new selection.
No issuer has demonstrated analyst completeness under the user's stricter target;
this is not a support reclassification or a finding every value is wrong.

Planning groups:3 approved-partial pilots,9 standard-review candidates,27 complex
selection cases,3 history boundaries. Five-year target preserved; no deficit is
invented as a period or automatically called a nonexistent business year. Exact
field/null/conflict/support pointers, independent sample depth and scoped approved
periods stay separate. Alphabet2024 approval does not extend to selected2025.
Original NWC/D&A/financial/timing blockers and accepted views are unchanged.

Eight shared tasks deduplicate controls, required-perimeter decisions, income,
expense D&A, investment, CFO/roles/tax, financial populations/shares and history.
First **proposed** finite completion attempt:MSFT FY2026 only; required short
borrowing and other scope gaps need defensible evidence/alternatives, not zero
or acknowledgment. Stop INCOMPLETE if an essential input remains unsupported.
No backlog execution or research authority is implied. Future economics stay
Phase2; neither financial shortfalls nor Phase1 closure are accepted here.

Conditional workload, not completion promise:latest-selected financial review
140/280/522 person-days, full available history414/855/1,547; separate shared and
issuer integration effort is detailed in the report. At two reviewers/four
focused days each weekly, latest review alone is17.5/35/65.25 team-weeks.
External disclosures/user decisions and all42 completion date remain **not
estimable**. These are task-based low-confidence planning budgets, not a forced
6–12-week estimate or financial numerical assumptions. Individual records need
no new financial conclusion:existing records are linked, not re-reviewed/rewritten.

Validation:five focused assessment tests pass (2.303s), exact retained replay and
source pointers,42 mappings/199 accessions/210 targets/11 deficits/2,786 field
slots, deduplicated tasks and latest-target batch coverage, original source and
accepted-view digests, compileall,406 affected local links and diff checks pass.
No financial/runtime/policy/accepted-view changes, SEC requests, full-suite or
corpus rerun. Stop after assessment for user review, not backlog execution.

## Prior milestone — approved Alphabet FY2024 historical selections

[Package](company-data-preparation/GOOGL-analyst-input-package.md) /
[JSON](company-data-preparation/googl-analyst-input-package.json) add an isolated
accepted view and [immutable user audit](company-data-preparation/googl-analyst-treatment-acceptance.json).
Exact five scoped decisions bind the prior proposal/source revision and actual
UTC recording time; replay cannot create or renew acceptance. Original proposal
sheet remains prior history. Changed evidence/scope/candidates fail closed.

Select rounded partial current capital13,342m, named term/CP/finance15,859m and
current financial95,657m only. WholeAP/fines/all-lease alternatives non-default.
Operating service/finance asset financing classification accepted, no D&A overlap
assumption. Required expense D&A null; CFO15311/finance amortization413 distinct.
Principal405 already inside repayments12701; NCI4200R includes redeemable1100R.
Investment cash/noncash/creditors, tax/SBC roles, precision alternatives and dated
share classes/source aggregate/awards stay separate. Unknowns never cleared.

[Consolidated pilot assessment](phase1-preparation-pilot-gap-assessment.md) now
distinguishes four exact accepted periods from whole histories, original blockers,
assumption-dependent treatments and remaining delivery-contract/user decisions.
Frozen/pilot artifacts, original receipt gaps and accepted AAPL/MSFT bytes remain.
No SEC requests, full-suite/corpus rerun, Phase 2 authority or Phase 1 closure.

Validation: **18 Alphabet integration tests (5.866s)** plus **57 preservation
tests** (reported-input10 in3.289s, partial-NWC9 in6.210s, accepted AAPL17
in5.487s, accepted MSFT21 in7.600s) pass. All three exact package replays,
prior-proposal equality and original runtime/JSON/pilot/frozen/peer bytes,
audit restart/staleness/tamper/missing rejection, rounding/null/overlap checks,
compileall, **473 affected local links** and `git diff --check` pass.
Two initial older-module invocations lacked `PYTHONPATH=src` and failed import
before running tests; corrected invocations above passed without source changes.
These are bounded current checks, not a claim of a new full-suite run.

## Prior milestone — Alphabet FY2024 consolidated analyst review draft

[Package](company-data-preparation/GOOGL-analyst-input-package.md) /
[JSON](company-data-preparation/googl-analyst-input-package.json) reuse retained
source/inspection machinery, not peer financial assumptions. Exact selected
`0001652044-25-000014`, FY2024 only; explicit refreshed instance receipt and
original null timestamp/status history remain distinct. Six new material
recommendations proposed for one consolidated review; original approvals remain.

Rounded manual AP3200m is still a duration source plus reviewed closing reading,
not an exact instant. Proposed partial capital13342m versus wholeAP10142m;
inventory/supplier and mixed allocations unknown; separate accrued PP&E7104m
not added to correction. No book/cash movement or complete NWC. CFO125299m,
Revenue350018m, EBIT112390m retained; CFO depreciation15311m versus finance
ROU expense413m does not establish complete expense D&A/non-overlap.

Propose Alphabet-specific operating-service/finance-financing; principal405m
already within repayments12701m. Investment cash/combined purchases/noncash/
creditors separate. Current financial95657m, locked long marketable266m and
nonmarketable/precision35500R/35531 observations retained separately. Named
term/CP14182m, proposed plusfinance15859m versus all-lease30437m, no complete
debt/excess cash. NCI4200R includes redeemable1100R; other claims/commitments
not automatically summed. Accepted SBC22800R proxy once, add-back22785m and
tax/cash/deferred roles distinct. Shares retain class/date/source precision,
awards separate, no dilution/aggregation.

All prior JSON/runtime/source/pilot/frozen artifacts and accepted AAPL/MSFT
views preserved. Financial sufficiency NOT_ASSESSED, original blockers remain.
No SEC requests, new financial policy/registry, full-suite/corpus rerun,
Phase 1 closure or Phase 2 calculations. Validation: **13 focused tests (5.319s)**;
**57 preservation tests** (Alphabet reported10 in3.209s, partial-NWC9 in6.111s,
accepted AAPL17 in5.403s, accepted MSFT21 in7.479s) pass. All three exact package
replays, twelve recorded arithmetic/source checks, original JSON/runtime/prior
helper byte preservation, manual precision/receipt/class/overlap/conflict/null
checks, compileall, **444 affected local links** and diff checks pass.
Stop for one consolidated user review, not implementation or a research chain.

## Prior milestone — approved AAPL FY2025 historical selections

[Existing package](company-data-preparation/AAPL-analyst-input-package.md) /
[JSON](company-data-preparation/aapl-analyst-input-package.json) add a separately
versioned analyst selection view, with persisted exact user-approval/source
revision and UTC recording provenance. Partial current operating capital−9159m
includes vendor receivables and distribution8919m; original−240 and alternatives
remain non-default history. Employee/capital creditors/mixed allocations remain
unknown, no ΔNWC/completeness approval.

Operating-service/finance-asset-financing historical classification; named
CP+term carrying+finance subtotal99887m only, all-lease112377m non-default.
Current financial54697m and LT marketable77723m separate, not unrestricted/excess
cash. CFO D&A11698m versus rounded expense8000m distinct; complete expense D&A
null, no finance-amortization overlap assumption. Cash PP&E−12715m, Other−1480m
and noncash ROU+2800m rounded separate, no reinvestment total/allocation.
Income/CFO/SBC-proxy/tax roles retained; fiscal-end common14773260000 selected
with original date/precision, cover/weighted averages/RSUs separate. No future
tax, award valuation or dilution approval.

Minimal report-only integration reuses MSFT audit/relevant-revision/strict-JSON/
manual UTC utilities, not MSFT financial assumptions. Missing, tampered or stale
financial/evidence content fails closed; explicit revalidation required. Original
proposal payload, policies/outputs, source bodies, scenarios/bundles, pilot bytes
and accepted MSFT view preserved. Financial sufficiency NOT_ASSESSED, original
blockers remain; no SEC requests, full-suite/corpus rerun, Phase 2 work or Phase 1
closure. Validation: **17 AAPL package/integration tests (5.509s)**, **15 original
AAPL cash-flow tests (2.591s)**, **eight AAPL partial-NWC tests (2.138s)** and
**21 accepted MSFT package tests (7.776s)** pass. Both exact package replays,
original proposal/source/JSON/runtime preservation, persistent audit restart,
stale/tampered/missing audit rejection, precision/null/non-default/source checks,
compileall, **445 changed-document local links** and diff checks pass. Stop after AAPL.

## Prior milestone — AAPL FY2025 consolidated analyst review draft

[Package](company-data-preparation/AAPL-analyst-input-package.md) /
[JSON](company-data-preparation/aapl-analyst-input-package.json) reuse verified
selected primary/instance evidence and existing reporting helpers, not MSFT
financial assumptions. Existing accepted CFO/cash-PP&E/SBC-proxy/cash-tax/
restricted fixed-lease inputs remain accepted only within their original scope.
Six new recommendations remain proposed for one consolidated user review.

Proposed partial current operating capital−9159m includes distribution8919m,
versus original−240m, with operating vendor receivables33180m. Employee and
capital-creditor allocations unknown, no cash/book movement. CFO D&A11698m
versus PP&E expense8000m rounded does not establish expense-basis D&A or an
amortization residual. Proposed AAPL-specific operating-service/finance-financing
classification does not assume finance amortization inclusion. Investment
columns remain separate; cash-interest/lease/acquisition scope gaps explicit.

Named financial current54697m/allreported132420m; carrying borrowing98657m,
proposed with finance leases99887m versus all-lease112377m; neither unrestricted
cash nor complete debt. Provision20719m, Pretax132729m and historical ETR,
cash taxes43369m and deferred provision−1339m stay distinct. Fiscal-end common,
later cover, RSUs and future expense retain dates/classes/rounding, no dilution.
Commitments/tax contingencies are separately evidenced disclosures, not new debt.

Original source bodies, AAPL scenarios/bundles, accepted MSFT view, all frozen
policies/results and pilot serialization remain unchanged. Financial sufficiency
NOT_ASSESSED and original blockers persist. No SEC requests, runtime/policy/
schema changes, full-suite/corpus rerun, Phase 1 closure or Phase 2 calculation.
Validation: **12 focused package tests (4.788s)**, **15 original AAPL cash-flow
tests (2.563s)**, **eight AAPL partial-NWC tests (2.248s)** and **21 accepted MSFT
package tests (7.947s)** pass. AAPL and MSFT exact offline package replay,
original JSON/runtime/MSFT-helper byte preservation, twelve recorded arithmetic/
parent/CFO checks, compileall, **429 affected local links** and diff checks pass.
Stop for one consolidated review; no full-suite/corpus rerun.

## Prior milestone — approved MSFT historical selections

The [existing package](company-data-preparation/MSFT-analyst-input-package.md)
and JSON add a separate accepted view, with immutable user-authority audit and
relevant source/proposal revision. Named-only partial operating capital
−25,755 / −18,600 USDm and book movement +7,155 selected; broader estimate
−23,427 / −3,372 (+20,055) remains non-default. Both include noncurrent balances,
not complete current NWC or cash ΔNWC; original current-only partial NWC remains.

Operating-service/finance-financing historical classification accepted; D&A
28,000 / 39,000 retains explicitly unproved finance-amortization inclusion as
an accepted assumption. Investment columns separate. Current financial balances
less identified restrictions 94,565 / 73,043 selected, not unrestricted/excess
cash. Named term+finance subtotal 89,323 / 106,888 is not complete debt; FY2026
extra short borrowing null, zero proposal rejected but retained. Named historical
tax/share schedules accepted without future rates/award valuation/dilution.

The report-only overlay reuses existing revision/digest/strict-JSON/manual UTC
utilities; no generic numeric override mislabels book operating capital. Missing
audit or changed facts/scope/precision/alternatives/evidence fails closed; explicit
future revalidation required. Original proposal/source sections and all earlier
facts, accepted inputs, pilots/sidecars, frozen policies/output bytes preserved.
No SEC requests, full-suite/corpus rerun or Phase 2 work. Financial sufficiency
NOT_ASSESSED, original blockers retained, no Phase 1 closure. Stop after MSFT.
Validation: **21 package/integration tests (7.791s)**; **54 existing preservation
tests** (22 cash-flow in 5.930s, 24 interest annotations in 18.084s, eight NWC in
7.205s) pass. Exact package replay, approval persistence/restart, stale-content
rejection, source/proposal equality to the preceding commit, original JSON/runtime
byte checks, compileall, **445 changed-document local links** and diff checks pass.

## Prior milestone — concrete MSFT analyst decisions, revision 2

The [same two-period package](company-data-preparation/MSFT-analyst-input-package.md)
and [JSON](company-data-preparation/msft-analyst-input-package.json) replace six
deferrals with concrete proposed treatments and source/assumption-separated
schedules. Proposed operating-capital proxy −23427m/−3372m, **book** movement
+20055m; named-only alternative −25755m/−18600m, +7155m. Residual operating
classification is explicitly estimated; no cash bridge or complete NWC claim.
Facilitation exclusion is supported by investing narrative, with no invented
matching liability. GAAP-aligned operating-service/finance-financing lease method
is recommended, not accepted; named term+finance liabilities89323m/106888m,
original EBIT/D&A unchanged, conditional D&A scope alternative separately gated.

Known FY2026 supplier restriction11300m=3800m current+7500m long is separated;
proposed available-current pool94565m/73043m carries explicit availability
assumptions, not excess cash. FY2026 zero extra-short-borrowing is an explicit
proposal supported by statement/flow context, **not a source zero or net-to-stock
inference**; source CP still null. Debt basis reconciliations, investment partitions
and known other-claim observations now have exact retained evidence. Tax/share
histories are finalized as reported for named scope; future rates/award valuation/
forecast dilution are not Phase 1 historical-preparation requirements.

No user acceptance, runtime or frozen-policy/schema change, frozen/pilot mutation, full-suite
or corpus rerun, SEC requests or Phase 1 closure. Original two-period facts/inputs,
accepted treatments and source receipts are preserved; new facts/proposals occupy
separate JSON sections with prior sheet history and actual UTC proposal metadata.
Current validation: **17 package tests (7.355s)** and **54 existing cash-flow,
sidecar and NWC preservation tests (31.632s)** pass, including exact original
period/input preservation and all 57 newly bound source facts. Offline replay,
compileall, affected links and diff checks pass. Stop for consolidated review;
financial sufficiency remains NOT_ASSESSED and Phase 2 remains prohibited.

## Prior revision — MSFT two-period analyst input package

[Selected schedules and one approval sheet](company-data-preparation/MSFT-analyst-input-package.md)
with [reproducible data](company-data-preparation/msft-analyst-input-package.json)
deliver a separate company-specific **draft**, not runtime integration or financial
sufficiency. Exact reviewed FY2025/FY2026 bodies support source selections and
historical component arithmetic now: expense D&A 28000m/39000m, partial NWC
−28245m/−21353m and adjacent book movement +6892m, current liquidity
94565m/76843m, term-debt carrying totals 43151m/40294m, recognized leases,
June 30 and separately dated cover shares, and restricted-stock awards 82m/78m.
Both complete displayed CFO bridges reproduce 136162m/182935m. Tax/SBC roles,
noncash investment, parent/subset overlaps and exact rounded precision remain.

FY2025 commercial paper is expressly zero; FY2026 absent CP is not zero.
Mixed NWC/capital creditors, acquisition/FX/timing, complete interest/lease/debt,
other claims and operating-tax requirements stay explicit. Six proposed judgments
await consolidated review; no new numerical assumption or acceptance is created.
Previously accepted MSFT choices are preserved, including restricted lease data
**not** being a comprehensive modeling convention. No future tax rate approved.
All original JSONs/runtime source, pilot bytes, five-period history, blockers,
schemas, policies and frozen outputs remain unchanged. No SEC requests or full
suite/corpus rerun. Bounded validation passes: **12 package tests in 7.345s** and
**54 existing cash-flow/sidecar/NWC tests in 31.336s**, exact offline replay,
four receipt/pointer bindings, fourteen source arithmetic/parent checks, original
JSON/runtime byte preservation, compileall, 425 affected links and diff checks;
the 1117-test suite below is the preceding runtime milestone, not a claim that
this new report helper was in that run. Phase 1 remains open; financial sufficiency
NOT_ASSESSED. Stop for user review; no automatic next task or Phase 2 authority.

## Current bounded statement-repair milestone

[Results and stopping conditions](statement-binding-repair-results.md) /
[59-case disposition](statement-repair-disposition.json) /
[v2 delivery ledger](reported-population-delivery-ledger.json).
18/18 exact statement bindings established: 36 unique SEC requests, all HTTP 200;
five IBM primaries reused, annual reports explicitly incorporated/indexed.
42 histories / 199 annuals / eleven deficits remain. CFO: **174 supported / 24
partial / one failed / zero not assessed**. Thirty-five of the prior 59 partial
cases now reconcile; 24 retain exact scope/hierarchy requirements. MCD FY2024
has a −1m difference outside the unchanged 0.6m precision bound, retained FAILED.
Current reported liquidity 46; dated unclassed common-share selections 162;
43 partial borrowing observations across 33 periods; recognized finance leases
92 and operating leases 186. No complete combined-debt field or dilution estimate.
All 2,487 prior population inputs preserve values and stable IDs; original parent,
pilot and frozen outputs remain unchanged. Current validation: **1,117 full-suite
tests passed in 7116.733s**, plus 44 focused tests. Exact ledger replay, legacy/v2
serialization, receipt rejection, override/queue and preservation checks pass;
all 182 Python files and 87 JSON artifacts match the pre-run seal. Compileall,
receipt/count/digest checks, local links and diff checks pass. No recovery requests
or duplicate acquisitions. Prior 1,101-test success covers v1 only. Phase 1 stays open;
financial sufficiency NOT_ASSESSED and material shortfalls remain unaccepted.

### Prior reported-population v1 milestone

## Prior v1 Milestone

Separate reported-population delivery and independent CFO reconciliation,
with completed final full-suite validation on the final implementation. Phase 1 only.
[Implemented contract/results](reported-population-delivery.md) /
[199-period ledger](reported-population-delivery-ledger.json) /
[coverage](reported-population-delivery-summary.json). No Phase 1 closure,
financial-shortfall acceptance or Phase 2 authority.

42 histories / 199 annuals / fourteen families / eleven target-history deficits
remain. Narrow current-liquidity selections: 46; actual-date unclassed issuer
shares: 86. Separate partial reported borrowing captions: 23; recognized finance leases: 81;
operating leases: 169. No complete borrowing-plus-finance-lease total is inferred.
Independent CFO checks: 122 SUPPORTED / 59 PARTIAL / zero FAILED / 18 NOT_ASSESSED.
Residuals remain partial/unclassified, not validation by construction or FCFF.

139 exact selected primaries acquired with actual raw-body receipts; all 139
annual DEI identities verified on offline replay. Original parser outcomes/history
are retained. Thirteen primary filename/body gaps (CAT five, MCD five, PM three)
and five IBM independent financial-statement bindings remain explicit. No further
SEC requests or new research chain. All frozen/pilot/original preparation outputs
are separate and preserved. Final suite: **1,101 tests passed in 6298.428 seconds**;
all 180 Python file digests match the pre-run source seal. Final focused runs:
19 source/acquisition tests and nine delivery/replay tests passed. Compileall,
local links, integrity/count checks and diff checks pass. Recovery made no SEC
requests or duplicate test runs. See the [acceptance report](phase1-delivery-acceptance-report.md)
for exact validation binding and finite outstanding user decisions. Stop for review;
do not accept 90%/80% shortfalls or close Phase 1 automatically.

## Prior integrated technical-validation milestone

Final integrated technical-validation and user delivery review, Phase 1 only.
[Acceptance report](phase1-delivery-acceptance-report.md) separates technical
replay, the independent 120-slot sample and financial coverage. No Phase 1 closure,
financial-shortfall acceptance or Phase 2 authority is recorded. The complete
suite is run once; only demonstrated test/implementation repairs receive focused
reruns. No SEC requests or live corpus execution.

Retained assembly/coverage/sample replay agrees with committed reports: 42
histories, 199 annuals, fourteen families/2,786 selected slots versus 210 annuals/
2,940 target slots. Eleven history deficits remain. Recent selected/target 121/126,
older 78/84; all complete-field 90%/80% comparisons remain short, not accepted.
119 CHECKED / zero FAILED / one NOT_VERIFIED is sample depth, not complete-field
approval. The finite closure checklist retains aggregate/share and CFO-reconciliation
obligations separately from future consumer-specific sufficiency/timing gates.
Stop for user review after this validation milestone.

Single full suite: 1,068 tests / 1,057 passed / eleven obsolete preservation-pin
failures / zero errors. Test-only repairs bind mutable preparation code/ledgers
to explicitly reviewed milestones while preserving strict frozen/financial pins.
Fourteen distinct focused checks pass (nine affected methods plus five new
compatibility/transition/assertion-loop checks). No financial expectations, runtime
source, policies or ledgers changed. The initial suite remains FAILED; a second
full run after repair is NOT_ASSESSED/not executed under the once-only scope.
No known implementation defect remains. Compileall, retained receipt/identity
checks, forty-register accounting, affected local links and diff checks pass.

### Prior reported-tax integration — preserved results

Completed bounded **reported-tax assembly/review/override integration**.
[Current contract and finite decisions](integrated-reported-tax-preparation.md).
199 annuals / 42 histories retain distinct provision, Pretax and pure-unit reported
ETR components, exact source/policy proof, alternatives and null requirements.
Coverage: provision 186 populated / 13 conflicting; Pretax 162 populated / 37
unavailable; ETR 154 populated / 13 conflicting / 32 unavailable. Three MA metadata
gaps repaired by joining the manifest-sealed retained D&A inventory to the exact
instances; original approvals/annual checks replay, no SEC requests or new policy.

Assembly v2 / pure-containing generic preparation v3 preserve legacy support and
original pilot bytes; frozen schema 5, registries/results, non-tax values and seven
D&A negative reviews unchanged. Monetary analyst patches are revision-bound and
persist through restart; same-period dependent ETR is suppressed in the effective
view while original source history remains. No adjusted ratio or direct rate
override is allowed. Intentional operand-source reuse does not inflate overlap
warnings. Reported cash taxes and deferred-tax CFO adjustments remain distinct.

Quality remains partial, financial sufficiency NOT_ASSESSED; no forecast rate,
economic adjustment, Phase 1 closure or automatic blocker removal. Proposed
90%/80% shortfalls are not accepted. Stop after focused validation and local commit.
Remaining finite decisions: accept/reject delivery coverage limitations, disposition
existing tax conflicts/missing scopes, and define independent closure-validation
acceptance. Any adjusted/operating-tax treatment requires a separate future contract;
no new research queue or Phase 2 start is authorized.

Verified 76 distinct focused tests pass, including original-ratio export tampering,
transport-versus-relevant-proof revisions, synthetic persistence/revalidation and
same-period invalidation. Compileall, affected links and diff checks pass. Queue
2,786 primaries / 8,247 nested actionable / 18,012 annual diagnostics plus three
history cards; eight invalid-evidence locations preserved. Independent 120-check
results remain 119 CHECKED / zero FAILED / one NOT_VERIFIED (CVX EBIT). No full suite
or corpus rerun. Stop after this local milestone; no automatic phase closure.

### Prior borrowing/separate-tax milestone — preserved decisions

Completed bounded **ORCL borrowing mapping and separate reported-tax preparation**.
[Results/limits](retained-reported-tax-context-results.md) /
[199-period source ledger](retained-reported-tax-context-ledger.json).
Shared noncurrent notes/loans carrying mapping adds five ORCL observations; no
debt total or lease inclusion inferred. Independent checks: 119 CHECKED / zero
FAILED / one NOT_VERIFIED (CVX EBIT).

Tax provision 186 populated / 13 conflicting; Pretax 159 populated / 40 unavailable
(154 direct + five existing CVX curated replays); ETR 151 populated / 13 incompatible /
35 missing operands. Three registered MA periods remain evidence-blocked by filing
metadata, not financially rejected. No conflicting population selected away, clamp,
rate assumption or new policy. Pure-unit ETR has separate serialization with USD
operands/provenance; accepted pilot and assembled tax observations stay unchanged.
The overlay is not yet in the persistent review container and is not a complete
operating-tax consumer input. Coverage reports its components separately.

42 histories / 199 selected / eleven history deficits; previous scalar values,
seven D&A negative reviews, income conflicts/CVX gaps and frozen schema 5/results
unchanged. All 42 records describe actual component outcomes, not whole-history
statement review or support reclassification. Unaccepted 90%/80% shortfalls remain.
Focused replay/preservation/independent checks, compileall, links and diff checks;
**85 distinct focused tests pass** (51 integration/curated regressions, nine bridge,
25 existing tax-policy tests); 2,768 affected local links and 42 record checks pass.
no SEC requests, full suite or corpus run. Stop after commit; Phase 1 not closed.

Next bounded step: explicit additive tax-overlay review-container integration,
preserving pure-versus-USD units and revision-bound source identities. No metadata
acquisition, operating-tax allocation or broad research queue authorized.

### Prior milestone — preserved decisions

Completed **fixed independent-document acquisition and preparation-only D&A scope
repair**. [Detailed source/decisions](preparation-independent-repair-results.md),
[receipts](evidence/independent-validation-document-acquisition.json),
[exact 120 outcomes](preparation-independent-results.json).
Ten exact requests / ten HTTP 200 / zero failures or retries; no other filings,
indexes or notes requested. Original bytes, UTC receipts and typed digests retained;
exact primary DEI CIK, 10-K and annual dates independently replay. Configuration
remains external and undisclosed; prior evidence/fingerprints are unchanged.

118 CHECKED / zero current FAILED / two NOT_VERIFIED. Checks include support-only
and expected unresolved populations, not complete-field approval. CVX EBIT is
still unregistered/perimeter-unresolved; ORCL's 122,342m noncurrent borrowing note
concept is outside the current component map. WMT cash is confirmed as an existing
competing alternative, not selected; original income conflicts remain.

105 former direct D&A occurrences accounted for: seven exact negative scope
dispositions, 35 retained captions without the same demonstrated defect, 63 without
independent rendered captions. Only AMZN's five and HD's latest two are downgraded.
No replacement equation, scope allocation, zero or financial approval. Seven
original values/occurrences/precision/proofs remain support-only with missing
required D&A and exact reasons. Frozen generic/curated policies, schema 5 and
normalization values remain unchanged; their discrepancy is explicit.

Preparation D&A 108 = 98 direct + five MSFT derived + five Visa curated; 91
unresolved, support in 199 periods (1,327 observations, not totals). Revenue 188,
EBIT 194, CFO 195, cash Capex 165 and all other prepared fields/pilot bytes unchanged.
42 histories/199 selected versus 210 target, forty-issuer cohort 189/200 and eleven
history deficits preserved. Coverage definitions unchanged; no 90%/80% shortfall
accepted. Queue 2,786 primary / 8,315 actionable / 17,609 annual diagnostics;
three history cards separate. 1,936 substantive locations / 850 confirmation-only
locations under the documented reporting definition. No sufficiency certification.

Focused acquisition, validation, D&A, preservation, assembly and review workflow
tests; compileall, identities/digests/counts, affected links and diff checks.
**33 distinct focused tests pass** (nine assembly, seven validation, four repair,
eight D&A, five workflow); updated 18-test assembly/repair/workflow run passes.
No full-suite/corpus rerun, assumptions, economic calculations or Phase 2 code.
Initial diagnostic-count assertion (17,605) was updated for the seven newly explicit
missing requirements (17,612 including history cards); no diagnostic was hidden.

**Stop for user review.** The fixed evidence acquisition is complete, not Phase 1.
Required D&A/completeness and the two unverified field populations remain unresolved.
No further research/acquisition or financial mapping expansion is authorized here.


## Previous milestone

Completed **independent retained-evidence spot checks and explicit coverage
reporting**, not closure/readiness. [Definitions and source citations](preparation-coverage-validation.md),
[coverage ledger](preparation-coverage-results.json),
[independent results/backlog](preparation-independent-results.json).
42 histories / 199 selected periods versus 210 target slots; forty-issuer cohort
189/200. Recent 121/126, older 78/84; all fourteen fields accounted for. Missing
five-year slots remain XOM five, GEV three, SNDK three, with no invented dates.

120 latest field slots across fifteen issuers: **53 CHECKED / 2 FAILED /
65 NOT_VERIFIED**. CHECKED is a documented observation or expected-null sample,
not complete field confirmation. HD's D&A caption excludes intangible amortization;
AMZN's combined caption includes content/lease/other scope whose equivalence is
unproved. No replacement equation or value is approved. Ten exact independent
primary-document targets remain in the deduplicated backlog; no requests made.

Coverage separates policy values, declared complete totals, support, conflicts,
missing requirements and manual origins. No component family becomes a usable
complete field. All fields fall below 90%/80% declared-complete targets; no
shortfall is accepted for the user. Existing 2,786 inventory locations remain:
1931 substantive review locations versus 855 policy-value locations pending
independent confirmation only. No queue diagnostics are discarded.

Validation: **27 focused tests pass** (nine assembly, seven new reporting/independent
checks, eleven shared inspection). Initial fixture role labels omitted existing
pilot cash-PP&E roles; Chevron's face total was incorrectly used for its narrower
approved component. Literal retained supplemental-note evidence corrected that
fixture, not source values or policies. Compileall, affected local/source links,
denominator reconciliation, deterministic reporting and diff checks pass.
Pilot bytes, original ledgers, policies, registries, schema 5 and corpus artifacts
are unchanged. No SEC requests, full-suite/corpus rerun or real overrides.

**Stop for review:** user disposition of the two D&A scope failures, explicit
coverage definition/shortfalls and independent-evidence backlog. No automatic
acceptance, additional acquisition/research or Phase 2 work; no phase is closed.


## Previous milestone

Latest milestone: **bounded end-to-end preparation/review validation and primary
field-family presentation**. [Workflow](preparation-review-workflow.md) /
[exact counts](preparation-workflow-summary.json). Full-history queue: 2,786
primary items, 8,308 nested actionable causes, 1,575 informational causes and
17,602 original annual diagnostics; three history-exception cards stay separate.
All eight invalid-evidence locations and stable component IDs remain reachable.
Latest views: 574 primary items / 1,701 actionable causes / 3,527 diagnostics,
with explicit full-history/outside-view counts. One item per annual/field does
not mean one financial gap or complete inputs. All forty records plus META/COST
seed notes document the shared presentation change, not new financial coverage.
Read-only local ticker inspection now exposes source/effective bundle values,
full-history quality and full/latest queues. Separate temporary synthetic
META/MSFT/WMT/Alphabet workflows exercise persistence/restart, stale rejection,
explicit revalidation and overlay round trips. No real analyst decisions,
financial treatments, source edits, extraction expansion or support changes.
Frozen/pilot/ledger outputs persist; sufficiency remains NOT_ASSESSED.
**28 focused tests pass**: nine assembly, fourteen override and five new
end-to-end/presentation tests. The initial test-only lookup omitted period from
reused input IDs; exact period-plus-ID binding was corrected and the complete
focused run passed. Production target matching/financial selection was unchanged.
Compileall, affected links, forty-plus-two mappings, counts/reproducibility and
diff checks pass. No SEC requests or full-suite/corpus rerun.
Next independent gate: bounded retained-source/financial-input spot checks and
explicit coverage denominators/material-shortfall disposition before any qualified
analyst-reviewable acceptance. Do not reopen research or start Phase 2. Stop.

Previously completed milestone: **revision-bound persistent analyst overrides and grouped review**.
[Control contract](analyst-override-review-controls.md) /
[exact summary](grouped-preparation-review-summary.json). Separate opt-in local
audit and analyst-origin overlay preserve original values/evidence/alternatives,
history and unresolved requirements. Runtime UTC identity, explicit assumptions,
relevant-content revisions, stale blocking and explicit revalidation are enforced;
acknowledgment supplies no value. No real overrides or analyst decisions registered.
All 17,605 original diagnostic cards remain in 9,886 cause groups: 8,308 actionable /
1,578 informational, with source-detail click-through and explicit next actions.
Grouping does not accept/discard issues or reduce financial requirements.
All 42 preparation mechanisms are documented without new issuer values/support
claims. Frozen/pilot/ledger outputs remain unchanged; sufficiency NOT_ASSESSED.
No SEC requests, financial calculations, full-suite or corpus rerun.
**58 unique focused tests pass**: fourteen synthetic override, nine assembly/
grouping, 24 model and eleven shared regression tests. Original pilot/frozen/
ledger preservation, compileall, 2,459 affected local links, forty-plus-two
mappings, diagnostic membership/count reconciliation and diff checks pass.
Next bounded validation milestone: end-to-end local review delivery checks against
199 annual field denominators using representative synthetic decisions, restart/
stale recovery and current grouped diagnostics. No new extraction/research or
automatic financial acceptance. Stop pending authorization.

Previously completed milestone: **isolated historical-input assembly and review**.
[Results](prepared-assembly-results.md) / [quality summary](prepared-assembly-summary.json).
42 histories / 199 annuals / 2,786 field-family slots; all fourteen contract
families accounted for. XOM empty, GEV/SNDK short; eleven target-year deficits
persist. Policy-prepared value periods: Revenue 188, EBIT 194, CFO 195, Capex 165,
D&A 115; support-only/component counts and alternatives remain separately visible.
17,605 deterministic review cards: missing requirements, 119 conflicts, eight
invalid-evidence locations, overlap and partial-scope warnings; codes overlap.
Priority is field importance, not confidence. No acceptance, blocker removal,
total, residual or financial sufficiency calculation. Derived formulas/operands,
typed LLY refresh history, dated/class shares and original parent/pilot bytes
survive separate closed assembly serialization. Existing financial policies,
frozen outputs and support classes remain unchanged; sufficiency NOT_ASSESSED.
No SEC request, new extraction/research or full-suite/corpus rerun. Focused
validation results are recorded in the results document.
**43 unique focused tests pass**: eight assembly, 24 immutable input models and
eleven shared regressions. A pilot-versus-candidate ledger-shape mismatch in
round-trip validation was fixed and rerun successfully, without changing values,
conflicts or evidence rules. Compileall, 2,367 affected local links, exact
40-plus-two mappings, period/field/review reconciliation and diff checks pass.
Next bounded milestone, only when authorized: revision-bound persistent analyst
overrides with author/actual UTC time/rationale, permitted Phase 1 targets,
retained alternatives and stale/conflicting-input rejection. No forecasts,
economic adjustments, automatic approvals or valuation calculations. Stop.

Previously completed milestone: **retained other-bridge claims/assets and dated
shares inspection**. [Results](retained-claims-shares-results.md) /
[ledger](retained-claims-shares-ledger.json) accounts for 398 field slots over
199 selected periods / 42 non-specialized issuers. Bridge: observations in 199,
143 observation-only / 48 conflicting / eight invalid-evidence outcomes, 8,404
populations; 49 periods contain a conflicting component including invalid TSLA
2021. Nil/invalid preferred or pension populations remain explicit, not zero;
no retained body/receipt is missing. Shares: 199 observation periods, 241 distinct
date/class populations, zero numeric conflicts; 25 dimensioned periods and 188
non-year-end dates. No date coercion, class sum, weighted-average substitution,
netting, duplicate investment addition or complete financial coverage claim.
The additive shared dated-instant/share-unit path preserves old USD inspection
and prior ledger output. Separate overlays/serialization preserve parent/pilot
bytes, all prior fields, frozen policies/registries/schema/corpus and eleven
history exceptions. Family completeness and financial sufficiency remain unknown.
Validation results are recorded in the results document; no SEC requests,
full-suite/corpus rerun or new issuer research. Phase 2 remains prohibited.
**20 focused tests pass** (eight new, eleven shared, one full parent/pilot/frozen
preservation check), with old USD ledger and pilot payload hashes unchanged.
Only the mutable shared inspector is excluded from its old source-byte freeze;
financial policies/models/schemas/evidence remain pinned. Compileall, 2,276
affected links, exact mappings/identities, 398 slots and diff checks pass.
Next bounded milestone, only when authorized: opt-in bundle assembly and review
controls, with source-selection logs, overlap warnings and explicit unresolved
requirements. No formulas, estimates, automatic approvals or research queue.
Stop after this inspection batch.

Previously completed milestone: **retained year-end cash/investment and debt/lease
component inspection**. [Results](retained-bridge-component-results.md) /
[199-period ledger](retained-bridge-component-ledger.json), 42 non-specialized
issuers. Both families have observations in 199 periods, not complete balances:
cash 188 observation-only / eleven conflicting; debt 168 observation-only /
31 conflicting; no no-eligible or evidence-gap periods. 855 cash and 2,056 debt
concept populations retain exact year-end source/context/unit/precision and
confirmations/alternatives. Explicit family-perimeter requirements remain null;
dimensioned/extensions and measurement/scope limits are diagnostics, not approval.
Separate immutable overlays/serialization replay actual retained bodies; all
original parent/pilot values and bytes, prior D&A and other prepared fields,
frozen policies/registries/schema/corpus and eleven history deficits remain.
Financial sufficiency NOT_ASSESSED; no aggregates, economic treatment, SEC
requests or full-suite/corpus rerun. Focused validation results follow below.
**46 unique focused tests pass**: nine new cohort/overlay tests, eleven shared
inspection regressions, fourteen pilot cash and twelve pilot debt tests. The
ledger replay's tuple/list report-shape mismatch was corrected and rerun; two
pre-v2 preparation-model source pins were updated to the approved starting
baseline (LLY anti-downgrade guard), leaving old payload hashes and all other
artifact pins unchanged. All three affected tests pass on rerun. Compileall,
2,182 affected local links, exact 40-plus-two mappings, 199 identities, eleven
history exceptions, baseline preservation and diff checks pass.
Next bounded field step, only when authorized: retained year-end other
equity-bridge claims/assets inspection with explicit scope/unknowns, no bridge
calculation or issuer research loop. Stop after this batch.

Previously completed milestone: **retained D&A preparation overlays**.
[Results](retained-d-and-a-results.md) / [199-period ledger](retained-d-and-a-ledger.json).
42 issuers: **105 direct / five existing MSFT derivations / five Visa v1 curated /
84 unapproved scope-completeness / zero conflicts or evidence gaps**. 115 approved
required values are separate from support-only availability in 199 periods
(1,320 populations; no completeness claim). All 45 Visa original artifact
requirements match retained bytes; deduplicated evidence backlog zero. No new
scope, fallback, equation, registry, refresh, lease adjustment or economic charge.
Exact annual overlays preserve all original parent histories and four pilot
support-only distinctions/bytes, including LLY Capex v2. Prior fields and frozen
policies/registries/schema/corpus remain unchanged; eleven history deficits
persist. 61 unique focused tests, compileall, 2,093 affected links, forty-plus-two
mapping/count reconciliation and diff checks pass. Zero SEC requests; no
full-suite/corpus rerun. Stop after this pass.
Next bounded step, only when authorized: retained year-end cash/investment
components for the same cohort, without sums or completeness inference. Do not
reopen exhausted D&A research or automatically approve consumer timing/readiness.

Previously completed milestone: **isolated LLY preparation refresh integration**.
[Contract/results](lly-capex-preparation-refresh.md) /
[199-period ledger](refreshed-capex-ledger.json). Five reviewed entries accepted,
zero blocked through explicitly identified preparation refresh v1, not the legacy
digest verifier. Typed preparation-v2 audits retain original approval/entry,
unavailable historical bodies/fingerprints, unproved byte equivalence and exact
review/refresh receipt identities. V1 bytes/version support remain; no migration,
replacement hashes, new financial scope or legacy proof claim. Current coverage:
**145 direct / fifteen legacy curated / five curated refresh / 34 unapproved =
199; 165 populated**. All prior 160 values, other fields/pilots, frozen schema 5,
registries/policies/corpus and history exceptions preserved. Unknown incentive/
noncash/interest allocations and consumer timing/sufficiency remain explicit.
58 unique focused tests, compileall, 363 affected links, ledger/serialization
replay and diff checks pass. Zero SEC requests; no full-suite/corpus rerun.
Stop after integration; Phase 2
remains prohibited. Deferred retained D&A preparation under existing approvals
is a separate bounded field milestone, not automatic financial readiness.

Previously completed milestone: **bounded LLY retained-report refresh review**.
[Disposition](lly-capex-refresh-review-results.md) /
[immutable additive review record](evidence/lly-capex-refresh-review-v1.json).
Fifteen refreshed reports independently support the five existing LLY amounts
and financial scope; no financial contradiction found. One retained-source check
finds no historical bodies, so historical byte equivalence/renderer-only changes
are not established. **Zero entries activated; five remain operationally blocked**:
immutable v1 attestation/output provenance cannot carry different report digests
without a separately designed provenance/schema treatment. The explicit stop
condition applies; no policy, schema, hash, input or fallback changed. Zero SEC
requests. Existing preparation stays **160 populated / five evidence gaps /
34 unapproved scope = 199**, with all prior fields/pilots/frozen outputs exact.
29 unique focused tests, compileall, 310 affected links, identity/digest/coverage
replay and diff checks pass; no full-suite/corpus rerun. Next prerequisite is
explicit additive evidence-generation/provenance design, not repeat acquisition
or financial research. Phase 2 remains prohibited.

Previously completed milestone: **fixed Capex original-artifact binding repair**.
[Results](capex-binding-repair-results.md) / [receipts](evidence/capex-binding-repair.json)
/ [current ledger](repaired-capex-ledger.json). Exactly 85 requirements / fifteen
AMZN/LLY/CVX approvals reconciled; zero verified local bodies reused. 85 SEC
requests, all HTTP 200, no retries/transport failures: seventy raw fingerprints
match; fifteen LLY report fingerprints differ and remain blocked. New receipts
are refreshes, not recovered metadata; no registry hashes or semantics changed.
Current preparation: **145 direct / fifteen curated / five LLY evidence gaps /
34 unapproved scope / zero conflicts = 199 periods**. Ten resolutions added;
all prior 150 populated bindings, 34 scope cases, other fields, pilot annuals,
frozen outputs/classifications and eleven history deficits preserved. Full
policy/occurrence/precision/audit provenance survives separate serialization.
Financial sufficiency remains NOT_ASSESSED; Phase 2 prohibited. Stop after this
pass. Remaining bounded closure prerequisite is explicit disposition of fifteen
LLY historical report fingerprints, not further unapproved acquisition or scope
research. 61 focused tests, compileall, 436 affected local links, source-digest/
count reconciliation and diff checks pass. No full-suite/corpus rerun.

Previously completed milestone: **retained approved cash-Capex preparation**.
[Results](retained-capex-results.md) / [199-period ledger](retained-capex-ledger.json).
42 non-specialized issuers: **145 direct / five Visa v3 curated / zero conflicts /
15 approved-entry evidence gaps / 34 unapproved-scope periods**. 85 original
artifact requirements (AMZN 30, LLY 40, CVX 15) prevent v1/v2 replay; no synthetic
attestation or financial denial. Visa verifies unchanged v3 raw evidence/scope.
Only accepted payment magnitudes are negative cash outflows. Broader combined
captions, raw support and noncash/creditor/lease/acquisition/proceeds populations
remain separate, not substituted or summed. Original pilot annuals, all prior
fields, frozen schema/policies/corpus, classifications and eleven history deficits
remain unchanged. No SEC requests, new financial research or full suite/corpus.
**Stop after Capex.** Next authorized bounded step: fixed raw-artifact repair for
fifteen registered approvals under existing digest/validation gates; no new scope.
D&A/timing integration remains separate, with no consumer sufficiency approval.
66 unique focused tests pass (eight new preparation/representation checks and
58 v1/v2/v3/shared regressions). Exact replay, actual-source/sign/precision,
serialization, prior-field/pilot/frozen preservation, counts, compileall,
1,976 affected links and diff checks pass. No full suite/corpus or SEC requests.


Previously completed milestone: **retained deferred-tax and SBC reconciliation observations**.
[Results](retained-tax-sbc-results.md) / [199-period ledger](retained-tax-sbc-ledger.json).
42 non-specialized issuers; deferred-tax CFO role **39 populated / zero conflicting
/ 160 unavailable**; SBC **164 / five / 30**. Deferred provision and note-expense
support do not fill reconciliation gaps. Broader tax/credit captions and mixed
noncash support stay unallocated; no pure-component completeness claim.
Five INTC exact/rounded SBC populations remain unresolved; original four pilot
annuals, Alphabet's distinct SBC precision, all income/CFO/movement results,
eleven history deficits and frozen-v1 remain unchanged. No SEC requests,
issuer research, economic treatment, full suite/corpus or Phase 2. **Stop here.**
Next authorized bounded step: retained cash Capex under existing direct/curated
policies, with no new scope fallback; D&A/timing limitations remain separate.
46 unique focused tests pass: nine new role/sign/replay/preservation tests
(final rerun) and 37 shared/pilot mapping/Alphabet bundle regressions. All 199
receipt bindings, two independent 199-slot outcome totals, forty-plus-two record
mapping, eleven history exceptions, compileall, 1,892 affected links and diff
checks pass. No mapped evidence errors; no full suite/corpus or SEC requests.


Previously completed milestone: **retained cash-flow working-capital movement inspection**.
[Results](retained-working-capital-results.md) / [199-period ledger](retained-working-capital-ledger.json).
42 issuers / 199 periods have mapped observations; five KO reported totals,
all 199 partial/unknown complete-family coverage, zero without eligible rows.
983 observed populations / one conflicting NFLX FY2021 contract-liability
population; 421 discovery-only unsupported/dimensioned occurrences. Explicit
standard account-movement signs, exact retained annual/CIK/USD/precision proof
and all confirming occurrences survive separate serialization. No sum,
completeness, book ΔNWC, additional CFO or valuation approval. Original four
pilot annuals, all CFO/income outputs, sixteen unresolved income reviews and
frozen baseline stay unchanged. Eleven history deficits remain. No SEC requests,
full suite/corpus or issuer research. **Stop after this pass.** Next bounded step,
only when authorized: deferred-tax CFO reconciliation observations, separate from
provision/cash-tax and working-capital tax roles.
43 unique focused tests pass: eight new movement tests (final rerun) plus 35
existing shared/CFO/pilot mapping regressions. Ledger/source/sign/serialization
replay, frozen/pilot/non-movement preservation, compileall, 1,798 affected local
links, register/count reconciliation and diff checks pass.

Previously completed milestone: **retained-only reported CFO extraction**.

[Coverage/limitations](retained-cfo-results.md) / [199-slot ledger](retained-cfo-ledger.json).
42 non-specialized issuers / 199 frozen periods: **195 populated / zero conflicting
/ four unavailable CFO slots**. Four original pilot CFO inputs/annuals reused
verbatim; 191 new reported subtotals use the shared exact annual/CIK/USD/precision
inspection. MRK 2021–2023 and LIN 2021 have only narrower continuing-operation
scope, not eligible consolidated roots; no substitution or sum. Artifact backlog
zero; no SEC requests. XOM empty, GEV/SNDK short histories and eleven target
deficits stay explicit. All income 357 direct / 25 derived / eleven conflicts /
five CVX EBIT gaps unchanged; sixteen unresolved income slots remain active review
requirements, not abandoned/accepted. CFO is not FCFF/organic cash/book ΔNWC;
no complete reconciliation or consumer sufficiency/timing claim. Frozen schemas,
policies, corpus and original pilot serialization unchanged. Focused checks only,
no full suite/corpus. **Stop after CFO.** Next bounded step is reported cash-flow
working-capital movement rows, not aggregate or book ΔNWC, only when authorized.
19 focused tests (eight CFO / eleven shared/pilot), final offline replay,
compileall, 1,708 affected local links and diff/count/preservation checks pass.

Previously completed milestone: **fixed official income binding repair/replay**.
[Results](income-binding-repair-results.md) / [additive ledger](repaired-income-ledger.json).
Twenty targets verify: ten JNJ/KLAC exact filing metadata bindings and ten seed
annual identities/instances (nine documented candidates plus COST FY2026).
25 successful requests: five submissions records, ten indexes, ten instances;
no retries/failures, no JNJ/KLAC body acquisition. Unchanged selection at frozen
cutoff reproduces all four five-year histories. COST FY2026 is accession
0000909832-26-000093, filed 2026-10-07, annual 2025-09-01–2026-08-30; not a new
period or calendar inference. Current 398 slots: **357 direct / 25 derived /
11 conflicts / five unregistered CVX EBIT**. All prior 337 direct/fifteen derived
bindings and eleven conflicts preserved; official metadata/annual-source gaps
in this fixed scope close. Monetary and metadata provenance remain separately
bound through serialization. Forty-cohort manifest, eleven history deficits,
frozen schema/policies/registries/corpus and original pilot outputs unchanged.
Other families and financial sufficiency/timing remain unassessed. No SEC
research beyond this fixed pass, full-suite/corpus or Phase 2 work.
**Stop after repair/replay.**
48 focused tests (seven repair / eight prior integration / twenty-two active-policy
/ eleven shared) pass, as do both offline replays, compileall, 357 local links,
rate/digest/count and diff checks. No full-suite or corpus rerun.

Previously completed milestone: **existing-evidence income/approved EBIT integration**.
[Results and remaining requirements](approved-income-integration-results.md) /
[additive 398-slot ledger](approved-income-integration-ledger.json). 337 direct
bindings and eleven conflicts unchanged; fifteen approved derived EBIT inputs
(LLY/MRK/IBM five each) replay actual operands and immutable policy/version,
equations, precision alternates and entry-specific bridge gates. JNJ/KLAC ten
approved periods lack actual filing-date/submission-bound metadata needed by
existing provenance serialization; no date fabricated or model weakened. CVX
five remain unregistered. Retained annual-diagnostic records supply nine META/
COST identity candidates, not fresh frozen-selection/body verification: eighteen
slots lack original instance/receipt, COST FY2026's two lack accession/start.
337 direct + 15 derived + 11 conflicts + 15 no-direct/unintegrated + 18 body gaps
+ 2 identity gaps = 398 across 199 periods. Frozen 189-period cohort manifest,
eleven history deficits, schema 5, policies/registries, pilot outputs and production
unchanged. Supported-seed notes are supplemental, not new forty-register members.
Financial sufficiency/timing unassessed; Phase 2 prohibited. Focused validation
only, no SEC, full-suite or corpus execution. **Stop after this integration.**
41 focused tests (eight integration / twenty-two active-policy / eleven shared),
final binding/serialization rerun, offline replay, compileall, 478 local links
and diff checks pass. No essential metadata or seed fact evidence was invented.

Previously completed milestone: **fixed 119-accession sweep evidence acquisition**.
[Actual acquisition/replay](income-sweep-acquisition-results.md) and separately
[retained refresh receipts](evidence/income-sweep-backlog-acquisition.json):
96 missing-body and 23 incomplete-receipt targets matched the frozen manifest;
all 119 verified through existing exact annual/filing checks. 148 HTTP-200
requests (119 instances, 29 indexes), zero failures/retries. All 23 retained
original bodies identical; 96 prior bodies unavailable, with 67 matching claimed
fingerprints and 29 absent fingerprints. Original metadata gaps remain preserved.
Current sweep: **337 populated / 11 conflicting / 30 direct-concept absent /
20 insufficient identity = 398**, 42 non-specialized issuers/199 periods.
All 140 prior populated bindings unchanged; exact-accession artifact backlog zero.
META/COST ten identity gaps excluded; eleven target history deficits unchanged.
Existing derived EBIT remains separate. No policies, frozen outputs, support
classes, original pilot serialization or twelve other family dispositions change.
Focused receipt/replay/sweep/preservation checks only, no full suite/corpus.
34 focused tests, both offline replays, 1,051 local links, rate/digest/count
checks, compileall and diff checks pass.
Financial sufficiency NOT_ASSESSED; Phase 2 prohibited.
**Stop after acquisition and sweep; no follow-on research or implementation.**

Previously completed milestone: **retained-only direct Revenue/EBIT universe sweep**.
[Coverage, exceptions and preservation](retained-income-sweep-results.md) /
[offline ledger](retained-income-sweep-ledger.json). All 42 non-specialized
issuers (eight excluded, including GE): 199 selected periods / 398 slots.
140 populated (98 preserved + 42 newly supported), 192 missing-body, 46
incomplete-receipt, 20 insufficient-identity slots. META/COST's ten selected
years lack exact filing/start bindings in the inspected retained records; no
accessions inferred. Deduplicated backlog: 119 exact-accession artifact entries
(96 bodies, 23 receipts), plus ten separate selection-identity gaps; unknown
instance filenames/digests remain null. Eleven target history deficits remain
XOM five / GEV three / SNDK three. Existing derived EBIT policy references are
retained, not integrated as direct values. No new direct concepts or treatments.
New partial packages keep other families unassessed/null; original pilot,
NVDA/batch packages, schema 5, policies, classifications and production remain
unchanged. Financial sufficiency NOT_ASSESSED. Focused offline scope/occurrence,
exception, conflict, digest, serialization and preservation validation only;
27 focused tests pass (eight sweep / nineteen shared and batch regressions),
with final offline replay, compileall, affected links and diff checks. No SEC
requests, full-suite/corpus rerun or Phase 2 work.
**Stop after the sweep; no evidence acquisition.** Any next fixed backlog
disposition/acquisition plan requires separate authorization.

Previously completed milestone: **fixed 13-instance SEC acquisition and Revenue/EBIT replay**.
[Verified acquisition/results](retained-income-acquisition-results.md) /
[new original-body receipts](evidence/retained-income-instance-acquisition.json).
Exact reconciliation: AMZN five, AVGO five, AMAT three missing instances / 26
slots. 13 successful direct requests, no indexes/retries; all identities/dates
and original-byte digests verify. New receipts preserve old unverified history.
Unchanged direct rules move the original batch from 54/0/26 to **80 populated /
zero conflicting / zero unavailable** across the same 40 periods/80 slots.
197 occurrences; original 54 populated bindings unchanged. Twelve other families
per annual remain unassessed/null. Pilot/NVDA outputs, frozen policies/schema 5,
production counts, support classifications and financial blockers persist.
56 focused tests, final offline 13/13 receipt replay, all-80-slot batch replay,
original 54/pilot/NVDA preservation, compileall, 328 affected local links and
diff/digest checks pass. No full suite/corpus or Phase 2 work.
**Stop after this fixed acquisition/replay.**

Previously completed milestone: **fixed eight-issuer retained Revenue/EBIT batch**.
[Results and evidence gaps](retained-income-batch-results.md) /
[reproducible ledger](retained-income-batch-ledger.json). AMZN, AVGO, CSCO, KO,
HD, NFLX, PLTR and AMAT: 40 frozen selected periods / 80 slots = 54 populated,
zero conflicting, 26 unavailable due to missing full retained bodies/receipts.
126 occurrences retained; negatives and precision preserved. One shared path
and existing direct policies only. Forty annuals retain twelve other unassessed
null families each; no whole-issuer readiness or support change. Pilot/NVDA
serialization, frozen-v1 policies/outputs and financial blockers persist.
No SEC/full suite/corpus or Phase 2 work. Main expansion constraint is complete
selected-instance/receipt availability, not further issuer-specific rules.
53 focused tests (8 batch / 45 regression), exact replay, independent original
fact checks, all eight history round trips and pilot/NVDA byte preservation,
compileall, 514 affected local links and diff/digest checks pass.
**Stop after this fixed batch; no acquisition or research chain.**

Previously completed milestone: **NVDA five-period retained Revenue/EBIT preparation**.
[Results and limitations](nvda-retained-income-results.md) /
[reproducible ten-slot ledger](nvda-retained-income-ledger.json).
Five exact frozen periods: ten populated direct slots, 28 occurrences, one equal
approved Revenue alternative retained. All five original instance bodies and
receipt metadata verify; absent R3 income-statement/primary bodies remain an
explicit independent-review limitation. Existing approved semantics only;
no issuer-specific policy, fallback or financial treatment. Five isolated
annual bundles keep twelve other families per annual unassessed/unavailable.
No support reclassification, original blocker removal, pilot/frozen output
changes, SEC/full suite/corpus or Phase 2 work. Financial sufficiency NOT_ASSESSED.
93 focused tests (10 NVDA / 83 regression), exact retained ledger replay,
deterministic serialization, unchanged pilot hashes, compileall, 278 relevant
local links and diff checks pass.
Shared approach is ready for a fixed retained-only multi-issuer Revenue/EBIT
batch with candidate/exception ledgers and no research chain; do not start it.
**Stop after NVDA.**

Previously completed milestone: **reusable retained-component inspection interface**.
[API contract, routing and byte-preservation results](retained-component-inspection.md).
Shared exact-period retained receipt/context/unit/precision inspection now serves
all four pilot Revenue/EBIT, cash/investment and debt/lease regressions. Financial
policy/statement interpretation and selection stay outside the shared API in
unchanged mapping data and pilot inspectors. Candidates, all confirmations and
conflicts, source references, supplied roles/scopes and unresolved requirements
remain explicit. No accepted/completed status, zero inference or aggregation.
Mapping/annual/history versions 4, serialized outputs, frozen-v1, original
artifacts, classifications and financial blockers remain unchanged. No SEC,
new fields/periods/issuer approvals, full-suite/corpus or Phase 2 work.
112 focused tests (11 new / 101 regression), four mapping/CFO checks, exact
pre-refactor serialized history hashes/round trips, compileall, 405 relevant
local links and diff checks pass. All pilot occurrences and dispositions persist.
Next concrete bounded application, only if authorized: retained direct Revenue/
EBIT candidate and exception ledger for NVDA's five frozen selections using
existing selectors and bodies; no new approval or retrieval/research loop.
**Stop after this interface milestone.**

Previously completed milestone: **retained year-end debt/lease component integration**.
[Evidence/results](pilot-debt-lease-evidence.md) /
[reviewed mapping evidence](pilot-debt-lease-evidence.json). Same four periods;
60 available components, one missing MSFT FY2026 commercial-paper component,
12 further null scope requirements and 80 fact occurrences. Carrying amounts,
principal, fair values, discounted operating/finance liabilities and undiscounted
future payments are separate; parents/dimensional locations/possible overlap
remain explicit. No sums, debt completeness, lease toggle or financing convention.
Mapping and isolated annual/history versions 4 preserve schemas, native bundles,
sidecars, policies/outputs and all non-debt field dispositions. Financial
sufficiency NOT_ASSESSED; NWC/D&A/timing blockers unchanged. Current top-level
reported/null counts 153/49, family counts 10/1/3, 10/1/3, 9/1/4, 10/1/3.
101 focused tests, four mapping/CFO checks, compileall, 426 local links and
diff/digest checks passed; results are recorded in the results document.
No SEC/full suite/corpus.
Phase 2 remains prohibited. **Stop after this milestone.**
Next bounded step, only if authorized: reusable retained-instance direct-component
inspection interface reproducing all four existing pilot mappings and meanings
without new issuer/period registrations, financial treatment or policy changes.

Previously completed milestone: **retained year-end cash/investment component integration**.
[Evidence/results](pilot-cash-investment-evidence.md) /
[reviewed matrix](pilot-cash-investment-evidence.json). Same four pilot periods:
25 available reported observations, three gated/conflicting component slots with
four support alternatives, and 16 explicit additional null requirements. Forty
fact occurrences retained. Every cash/investment family stays partial; no
aggregate, unrestricted-cash or financial-sufficiency certification. Mixed MSFT
long-term, AAPL marketable, Alphabet lock-up/non-marketable scopes are distinct.
Alphabet's 35,500m/35,531m representations remain unresolved; AAPL/Alphabet
combined extensions remain support-only, not concept-policy approvals.
Mapping and preparation annual/history versions advance to 3; schemas, original
native bundles/sidecars, all non-cash mappings and frozen outputs remain unchanged.
89 focused tests, four mapping/CFO checks, compileall, 408 local links and diff
checks passed; results are recorded in the linked results document. No SEC,
full suite or corpus run. Phase 2 remains prohibited. **Stop after this milestone.**
Next smallest field step, only if authorized: retained year-end debt/lease
component mappings for these same periods, preserving overlap and unknowns,
without net debt, adjustments or valuation use.

Previously completed milestone: **retained direct Revenue/EBIT mapping and adapter integration**.
[Evidence, exact selections and limitations](pilot-direct-income-evidence.md) /
[statement matrix](pilot-direct-income-evidence.json). All eight reported totals
are available for the same four exact periods, using existing direct concepts,
25 confirming occurrences and separately verified retained face-statement tags.
No competing differing eligible values; conflicts would remain unresolved with
all candidates retained. No new fallback, derivation, receipt or period approval.
Mapping version 2 and isolated preparation annual/history bundle version 2 keep
original native bundles/sidecars and all non-income mappings unchanged.
Family counts MSFT 2025/2026 8/1/5 each, AAPL 7/1/6, Alphabet 8/1/5; 68 top-level
reported observations / 25 null required slots / nine D&A support observations.
Reported total completeness is not economic/timing/consumer readiness. Original
D&A/NWC/bridge/share/tax/lease limitations persist; financial sufficiency unknown.
Frozen schema 5, policies/outputs and 1905/1483/11/27/42 baseline remain unchanged.
75 focused tests, four mapping/CFO checks, compileall, 394 local links and diff
pass; results are recorded in the evidence/results document. No SEC requests,
full suite or corpus rerun. Phase 2 prohibited. **Stop after this milestone.**
Next smallest authorized step would be retained fiscal-year-end cash/investment
component mappings for these same periods, with restrictions/unknowns explicit,
no totals or inference from cash-flow disclosures.

Previously completed milestone: **isolated four-pilot historical-input adapter**.
[Delivery/limitations](pilot-historical-input-adapter.md). Existing immutable
AnnualBundle/HistoryBundle models now package only MSFT FY2025/FY2026, AAPL FY2025,
Alphabet FY2024 from unchanged pinned mappings and source-verifying bundles.
Mapped/support-only/unavailable families retain 6/1/7, 6/1/7, 5/1/8, 6/1/7.
60 top-level reported observations and 33 null required slots; nine separately
labeled support-only D&A observations preserve evidence under four null D&A slots.
No complete primitive, sum, residual, estimate, readiness or valuation approval.
Roles/signs/scale/rounding and every unresolved requirement remain; Alphabet SBC
expense/add-back and original/refresh receipt history are distinct.

Separate adapter serialization carries original native source proofs once per
period plus exact typed metadata, reverified on round trip. Core schemas/models,
original policies/outputs/mappings/bundles/scenarios/sidecars remain unchanged.
Baseline 1905/1483/11/27/42 retained; no corpus/full-suite or SEC requests. Three
issuer records/index and architecture explain delivery and limitations. Focused
tests (**58 passed**), deterministic serialization/preservation, compileall, links and diff pass.
Phase 2 remains prohibited; financial sufficiency NOT_ASSESSED. **Stop here.**
Next bounded step toward generic coverage, if authorized: retained-source direct
Revenue/EBIT mapping design for the same four exact periods, no new issuers,
component bridges, retrieval or cascades; unavailable/conflicts remain explicit.

Previously completed milestone: **four-pilot executable retained-evidence field
mappings and treatment checks**, no adapter. [Summary](pilot-historical-input-mappings.md)
and [matrix](pilot-historical-input-mappings.json) cover all 56 WP0 field-family
slots: 23 restricted mapped / four D&A support-only / 29 unavailable bindings.
MSFT FY2025/FY2026 and Alphabet FY2024 each 6/1/7; AAPL FY2025 5/1/8.
69 bound source inputs retain 76 confirming occurrences; 61 supplementary inputs
remain visible. Original pinned loaders verify exact source receipts/facts and
periods, not counts-only corpus evidence. All four independent reported CFO
checks pass; no residual equation/value or unsupported component sum approved.
SBC expense/add-back, deferred provision/reconciliation and cash/expense roles
stay separate. Bridge/share and revenue/EBIT gaps remain specific package limitations.

Three issuer records/index updated with decisions and limits. Frozen schema 5,
policies/outputs, original bundles/scenarios/sidecars and 1905/1483/11/27/42 baseline
unchanged; no blockers removed, treatment transfer or period extension. New
focused tests and existing model/preservation checks (**43 passed**), compileall, local links
and diff pass; no SEC, full-suite or corpus run. Phase 2 remains prohibited.
**Stop after mappings.** Next bounded implementation, only if authorized:
isolated explicit adapter for the four tested reported mappings, with unavailable
requirements/support-only observations preserved, no sums, assumptions or residuals.

Previously completed milestone: **WP0 — revised Phase 1 historical-input contract
and isolated immutable model foundation**. [Contract](dcf-input-contract.md) /
[decision](wp0-historical-input-decision.md). User-approved analyst-reviewable
preparation extends, rather than retroactively alters, qualified facts/gaps closure.
Annual income/cash fields, fiscal-year-end bridge components and separately dated
point shares retain independent origin/quality/scope/completeness/review, source
identity, precision, alternatives and unresolved requirements. Models/closed
serialization are structural, not fact/equation/scope certification; no issuer
values or new approvals. Five annual periods, three-period readiness and proposed
90% recent/80% older coverage remain targets, not claims. Material shortfalls
require explicit user acceptance; required nulls remain unresolved.

Frozen schema 5, policies/registries/outputs and all pilot bundles/sidecars remain
unchanged. Baseline 1905/1483/11/27/42; 43 executions/seven skips, classes 2/40/8;
40 records/189 identities/11 exceptions/four reviewed periods preserved. GE and
seven other specialized issuers are excluded from new generic bundles without
changing existing outputs. Focused model/preservation tests, compileall, relevant
local links and diff checks pass; **27 focused tests** (24 new model + three
existing pilot-preservation checks); no SEC request, full suite or corpus rerun.
Phase 2 remains prohibited. **Stop after WP0.** Next bounded authorized task would
be one four-pilot-period retained field-treatment/mapping design with explicit
missing requirements, scope/equation tests and bridge/share evidence limits.
Subsequent field-treatment changes must update affected issuer records; none
changed here, so only shared register guidance is updated.

Previously completed milestone: **consolidated Phase 1 blocker-disposition review**.
[Review/proposed delivery contract](phase1-blocker-disposition-review.md) and
[JSON matrix](phase1-blocker-disposition-review.json) account for 40 issuers,
189 selected identities, 11 history exceptions and all 354 unresolved metric/
state groups (1391 missing / 11 ambiguous / 27 blocked / 39 not-comparable cohort
states). Retained alternative packaging remains four exact pilot periods only;
37 other issuers have no reviewed reported package. Cash reconciliation movements
are not reconstructed book ΔNWC or certified cash operating investment. Complete
NWC is not a prerequisite to reproduce evidenced reported CFO; original blockers,
Alphabet D&A, tax/lease/investment/organic/timing limits persist. No financial
policy or whole-issuer sufficiency approval. No repairable integrity defect found;
qualified facts/gaps closure remains valid. Baseline 1905/1483/11/27/42 unchanged.
Workbook reference inspected read-only, not adopted. Matrix/source/period/link/
baseline/diff checks pass; no SEC requests, tests or corpus. **Stop for user review**
of the restricted delivery contract. If accepted, one bounded four-period retained-
input delivery index/check is proposed using unchanged bundle machinery. Further
history packaging requires a named finite scope; no new research chain or Phase 2.

Previously completed milestone: **qualified Phase 1 evidence-accounted preparation closure**.
[Closure checklist](phase1-preparation-closure-checklist.md) applies the user's
approved facts/gaps standard: 40 evidence-accounted records, 189 verified selected
identities and all 11 target-history exceptions explicitly accepted as limitations
(XOM five, GEV/SNDK three each), not five-year completeness. No essential remaining
defect or new repair/research task. All 680 measure rows/3213 cohort states reconcile;
four pilot reported-input periods remain the only independently reviewed packages.
Whole-history fact/policy joins and unreverified receipt detail stay explicit,
not certified. Financial sufficiency remains 40 NOT_ASSESSED; future consumer and
timing gates are separate from preparation closure, not a Phase 1 exit requirement.
Frozen classifications, financial blockers, source outputs and 1905/1483/11/27/42
baseline unchanged. Existing focused checks/identity replay/digests/links/diff pass;
no SEC requests, source changes, full suite or corpus. Phase 2 remains postponed.
**No essential Phase 1 preparation work remains under the approved standard.**
Stop; retain deferred coverage and evidence limits. Subsequent consumer-specific
work requires separate authorization, not an automatically started milestone.

Previously completed milestone: **authorized fixed 26-entry SEC identity acquisition**.
[Results/closure](phase1-selected-filing-sec-acquisition.md): 26/26 verified from
60 successful serial SEC requests; new original-body receipts, exact selection
replay at frozen cutoff and annual DEI/context checks. Current manifest now
189 verified / 0 missing/incomplete/conflicting across 40 issuers; prior 163
identity records and 11 history exceptions unchanged. New receipts are not
recovered original metadata. Exception ledger records 26 VERIFIED_NEW_SEC_EVIDENCE
plus AVGO's retained-evidence repair; financial facts/policies/blockers unchanged.
Focused tests, offline replay/reproducibility, digests/counts, links, compileall
and diff pass; no full suite/corpus. External configuration sourced per acquisition
command without exposing or copying it. Fixed pass is closed; no more SEC requests.
Next decision: one bounded measure-level fact/policy-binding acceptance scope.
History exceptions and consumer-specific sufficiency remain separate prerequisites;
financial sufficiency NOT_ASSESSED, baseline 1905/1483/11/27/42 unchanged, Phase 2 postponed.

Previously completed milestone: **retained identity-source availability audit**.
[Audit and closure](phase1-selected-filing-availability.md) and
[27-entry ledger](phase1-selected-filing-availability.json): one AVGO identity
repaired using previously reviewed legacy-namespace DEI/context evidence;
26 missing bindings remain unavailable in retained sources, 0 broken references,
0 conflicting identities. Manifest now 163 verified / 26 missing / 0 incomplete /
0 conflicting, 40 issuers / 189 periods / 11 history exceptions unchanged.
No raw-body/receipt inference, production resolver change or fact-provenance
certification. Financial sufficiency remains NOT_ASSESSED; frozen-v1 and pilots
unchanged. Focused tests, reproducibility, source hashes/counts, links, compileall
and diff check pass; no SEC/full-suite/corpus. Phase 2 remains postponed.
Next closure task: disposition the 26 unavailable-source exceptions explicitly,
either retain identity limitations or separately authorize one fixed-scope metadata
acquisition. Retained-source search is exhausted; no new issuer research cycle.

Previously completed milestone: **retained selected-filing identity manifest**.
[Results](phase1-selected-filing-identity-manifest.md) and
[JSON manifest](phase1-selected-filing-identity-manifest.json) reconcile 40 issuers,
189 selected periods and 11 history exceptions: 162 verified retained identities,
26 missing, 1 incomplete (AVGO 2021 annual evidence unresolved), 0 conflicts.
Exact identity is not complete measure-level provenance or financial sufficiency.
Retained reviewed inventories/tables and NWC instance-byte/DEI checks supply
identities; digest types/receipt gaps remain explicit, no inferred dates/forms.
All affected records updated; five-year target, short/empty histories, support
classes, financial blockers and frozen-v1 unchanged. Phase 2 postponed.
Nine focused manifest tests and eleven existing binding tests, reproducibility,
unique mappings/counts, links, compileall and diff check pass. No SEC/full-suite/
corpus. Baseline remains **1905/1483/11/27/42 = 3468**.
Single next Phase 1 milestone: **one retained-source availability audit for
27 unresolved identity bindings**, stopping at a source/missing-evidence ledger;
no retrieval, new research, annual-policy change or guessing.

Previously completed milestone: **shared offline preparation evidence-binding pass**.
User approves independent evidence-accounted and financial-input sufficiency
statuses. [Results/backlog](phase1-preparation-evidence-bindings.md) and
[ledger](phase1-preparation-evidence-bindings.json): 40 limited-accounting PASS,
0 FAIL/0 unassessed; financial sufficiency 40 NOT_ASSESSED, 0 PASS/FAIL. Complete
whole-history exact fact binding remains insufficient for all 40. Four registered
pilot packages independently verify at their exact periods only.
Minimal offline validator binds frozen universe/validation/original-corpus bytes,
40 register/record mappings, history/measure counts, declared policy/evidence
references and existing pilot receipts/round trips. Eleven focused tests pass.
Counts-only corpus evidence is not per-fact provenance; broken/missing bindings
fail and insufficient links are explained, never fabricated. All records and
AGENTS/register guidance now distinguish both statuses. No financial policy,
support, frozen-v1, bundle, scenario or sidecar changes; no SEC/full-suite/corpus.
Single next Phase 1 milestone: **retained selected-filing identity manifest for
189 selected periods and 11 target-history exceptions**, joining existing evidence
only, marking missing/conflicting accession/annual bindings and stopping after
one pass. No retrieval, pilot extension or financial certification. Phase 2 postponed.
Coverage remains 680 register measure rows and baseline **1905/1483/11/27/42 =3468**;
local references, compileall and diff check pass.

Previously completed milestone: **retained-evidence disposition of all 40 preparation
issuers**. [Assessment and completion decision](phase1-issuer-preparation-disposition.md)
and [machine-checkable matrix](phase1-issuer-preparation-disposition.json) preserve
all 17 measure states, review depth, evidence references, essential/deferred work
and explicit stop/reopening criteria. Groups: 3 closed pilots, 3 history boundaries,
3 revenue-conflict issuers, 31 other frozen-gap issuers without reviewed input
packages. These are preparation groups, not support reclassifications.
History target remains five years: 37 five-period / 2 two-period / 1 empty histories
give 189 periods among the 40; only four reported-input periods across three
issuers have pilot acceptance. No original blocker is cleared by CFO packaging.
Single next Phase 1 milestone: **explicit preparation acceptance-contract decision**:
complete required inputs versus five-year evidence-accounted facts/gaps, required
input families and short-history exception handling. Recommended latter requires
user acceptance, not silent lowering of coverage; neither is valuation readiness.
After that choice, propose one reusable retained-evidence binding ledger and
finite grouped exceptions backlog, not 40 research cycles. Phase 2 postponed.
Validated 40 identities/680 record measures, frozen history/state counts, pilot
identities and evidence/local links; diff check passed. No issuer financial
conclusion/source/policy/artifact changes, SEC requests, tests or corpus rerun.
Frozen baseline remains **1905/1483/11/27/42 = 3468**.

Previously completed milestone: **Alphabet acceptance and three-pilot consolidation**.
[Alphabet checklist](googl-treatment-acceptance-checklist.md) records explicit
user approval and closes qualified FY2024 preparation only. Rounded SBC expense
22,800m proxy once remains distinct from 22,785m add-back; restricted leases are
not a modeling convention. No interest proxy/allocation/tax rate or blocker removal.
[Gap assessment](phase1-preparation-pilot-gap-assessment.md) reconciles MSFT
FY2025–2026, AAPL FY2025 and Alphabet FY2024: 3 pilots / 4 exact reported-input
periods. Preparation packaging/acceptance improves; original frozen blockers,
coverage counts, classifications and timing gates do not change. Phase 2 postponed.
Single next Phase 1 milestone: **retained-evidence disposition matrix for all
40 GENERALIZATION_REQUIRED issuers**, with 3 qualified pilot closures and 37
without equivalent closure, explicit review depth/17-measure links, named scope,
essential-versus-deferred needs and stop criteria. No fresh issuer research.
Exact identities/registry hashes, counts, acceptance consistency, relevant links
and diff check validated. No SEC requests, tests or corpus rerun; baseline
**1905/1483/11/27/42 = 3468** preserved, not remeasured.

Previously completed milestone: **Alphabet FY2024 analyst-treatment decision memo**.
[Proposed recommendations](googl-analyst-treatment-decision.md) independently
recommend consolidated reported CFO, separate narrow PP&E, rounded recognized
SBC expense as a labeled cost proxy once, reported taxes without an operating
rate and restricted lease dataset preparation only. No cash-interest proxy,
investment allocation, lease modeling convention or completeness approval.
All recommendations remain **proposed pending user review**. Existing D&A/NWC
blockers, receipt history, timing gates and immutable bundles remain unchanged.
Registry identity/hash, source/precision/reference consistency, local links and
diff check validated; no SEC requests, tests or corpus rerun. Phase 2 postponed.
Single next Phase 1 milestone: **user review and one FY2024 treatment-acceptance/
input checklist**, closing only qualified historical preparation if accepted;
not financial completeness, numerical adjustment or valuation readiness.

Previously completed milestone: **isolated Alphabet FY2024 reported-input bundle**.
[Implementation and validation](googl-alternative-historical-cash-flow-inputs.md#implemented-isolated-fy2024-reported-input-bundle)
retain 34 reported inputs, 38 confirming occurrences, 12 explicit unknowns and
the thirteen-term reported CFO bridge. One exact annual registration uses the
authorized refreshed instance receipt; serialization separately preserves the
original body's null receipt fields and history. SBC 22,785m add-back and rounded
22,800m expense remain distinct; no numerical adjustment or analyst proxy.
Focused tests: 10 passed; relevant analyst tests: 137 passed. Compileall, local
links and diff check pass. No shared model, frozen-v1, policy, existing bundle,
scenario or sidecar changes; no SEC request/full-suite/corpus rerun.
Baseline **1905/1483/11/27/42 = 3468** unchanged, not rerun.
Single next Phase 1 milestone: **bounded Alphabet analyst-treatment decision
memo**, independently assessing permitted reported-input use, SBC precision,
restricted leases/embedded financing principal, taxes and unavailable interest/
investment allocation. Recommendations require user review, not valuation
readiness or another broad research cycle. Phase 2 remains postponed.

Previously completed milestone: **Alphabet FY2024 exact-instance provenance repair**.
[Verification and refresh history](googl-alternative-historical-cash-flow-inputs.md#exact-instance-provenance-repair--authorized-refresh)
record unrecoverable original timestamp/status after bounded retained-record
inspection, followed by one user-authorized exact SEC instance refresh. HTTP 200,
actual receipt UTC 2026-10-11T21:10:46.050735+00:00; response is byte-for-byte
identical to the original (same 2,703,015-byte body/SHA-256). New receipt is a
separate retrieval event, not recovered original metadata. Additive retained
evidence links the original body/null fields and preserves old artifacts.

Thirty relevant facts/identity/context/unit/precision and all three reported CFO
bridges independently revalidated; existing Artifact/Receipt validation accepts
the new receipt. Links and diff check pass. No source, policy, schema or bundle
implementation; no full suite/corpus. Baseline **1,905/1,483/11/27/42 = 3,468**
unchanged. Original NWC, D&A, cash-scope and timing limitations remain.
Single next Phase 1 milestone: **one isolated Alphabet FY2024 reported-input
bundle**, explicitly bound to the refreshed instance receipt and retained primary
body, preserving original metadata-gap history, unknowns and rounded source roles.
No comparative registrations, transferred analyst treatments or economic
calculation. Stop after evidence repair; Phase 2 postponed.

Previously completed milestone: **AAPL FY2025 acceptance and independent Alphabet
FY2024 reported cash-flow evidence review**, documentation-only Phase 1.
[AAPL acceptance](aapl-treatment-acceptance-checklist.md) closes its pilot only for
qualified historical preparation: consolidated CFO/narrow PP&E, SBC cost proxy
once, reported cash taxes and restricted rounded fixed-lease dataset. No tax
basis/rate, completeness or valuation readiness; unknowns/NWC/timing persist.

[Alphabet matrix](googl-alternative-historical-cash-flow-inputs.md) verifies CFO
125,299m, cash PP&E 52,535m, rounded tax cash 27,400m, separate SBC precision,
three lease payment classes and combined acquisition/intangible cash. No
automatic treatment transfer, total, organic or complete reinvestment claim.
Missing cash borrowing interest, allocations and separate D&A issue persist.
Both original bodies/digests verify; **instance retrieval timestamp/status are
unrecorded**, explicitly a future packaging prerequisite, not fabricated data.
Exact identities, facts, all three reported CFO columns, provenance, relevant
links and diff check validated. No SEC requests, tests/corpus or artifact/source
changes; baseline **1,905/1,483/11/27/42 = 3,468** retained.

Single next Phase 1 milestone: **bounded exact Alphabet FY2024 instance receipt-
provenance recovery/verification before bundle implementation**, preserving old
evidence history and mandatory receipt checks. No broad research/annotation
cycle. Stop after this review; Phase 2 remains postponed.

Previously completed milestone: **bounded AAPL FY2025 analyst-treatment decision
memo**, documentation-only Phase 1. [Recommendations pending user review](aapl-analyst-treatment-decision.md)
retain consolidated reported CFO and separate narrow cash PP&E; propose SBC
recognized-expense economic-cost proxy once; preserve reported cash taxes with
no operating-tax rate; propose only the rounded fixed operating-lease dataset,
not a complete cash-service convention. Cash interest and acquisition/intangible
allocations remain unknown, with no invented proxy or zero. No MSFT approval
transfer, completeness claim, adjusted calculation or blocker removal.

Registry points/roles/precision, evidence references, proposed decision boundaries,
established methodological references, local links and diff check validated.
Source, evidence, frozen-v1 and all bundles/scenarios unchanged. No SEC requests,
tests or corpus rerun. Baseline **1,905/1,483/11/27/42 = 3,468** carried forward.
The pilot can close after acceptance **only for qualified one-period historical
input preparation**, not economic consumption or valuation readiness. **Stop for
user review.** Single next Phase 1 milestone: one FY2025 treatment-acceptance/input
checklist recording choices and durable disclosure limits; no new sidecar,
research cycle or numerical implementation. Phase 2 remains postponed.

Previously completed milestone: **one isolated AAPL FY2025 reported-input bundle**.
[Results and provenance](aapl-alternative-historical-cash-flow-inputs.md#implemented-isolated-fy2025-reported-input-bundle)
record twenty-one inputs/twenty-six confirming occurrences and eleven explicit
null unknowns. CFO, PP&E cash, net cash taxes, SBC expense/add-back and rounded
fixed operating-lease cash remain distinct; only the ten-term reported CFO
reconciliation is computed. Own immutable version-1 registry/serialization
contract; existing shared models, MSFT contracts and analyst scenarios unchanged.
No comparative bundles, inferred zeros, MSFT treatment transfer, economic totals
or valuation consumption. Frozen baseline **1,905/1,483/11/27/42 = 3,468** and
NWC blockers preserved. **15 focused / 127 relevant analyst tests passed**
(127 includes the new 15); MSFT serialized-byte preservation, compileall, local
links and diff check pass. No full-suite rerun because shared code is unchanged.
No SEC requests or corpus rerun; Phase 2 postponed.
Next Phase 1 milestone: **one bounded AAPL analyst-treatment decision memo**,
using retained evidence to distinguish proposed choices from unavailable
disclosures and permitted partial-data use. Stop after this implementation.

Previously completed milestone: **bounded AAPL FY2025 alternative reported cash-flow
input review**, documentation-only Phase 1, plus MSFT restricted-dataset
acceptance. The [AAPL matrix](aapl-alternative-historical-cash-flow-inputs.md)
verifies the selected 2025 accession, annual/ comparative contexts and reported
CFO reconciliation. CFO 111,482m, narrow cash PP&E 12,715m, net cash taxes 43,369m
and SBC expense/add-back 12,863m are supported; cash interest, complete lease cash
and acquisition/intangible allocations remain unknown. Comparative columns are
not newly registered periods/bundles. PARTIAL GO only for separate reported-input
packaging; MSFT analyst choices do not automatically apply to AAPL.

The user accepts [MSFT's restricted reported lease dataset](msft-treatment-acceptance-checklist.md)
for separate preparation only: operating payments/finance interest already in
CFO, finance principal outside CFO. Additional coverage/borrowing overlap stay
unknown. Its two-period preparation pilot is closed; no totals, adjustments,
modeling consumption approval or further lease research.

Two AAPL original-response hashes/lengths, exact observations, all three source
CFO column sums, references/local links and diff check validated. No SEC requests,
tests/corpus, production or existing bundle/scenario changes. Frozen baseline
**1,905/1,483/11/27/42 = 3,468** and NWC blockers unchanged. Single next Phase 1
milestone: **one isolated AAPL FY2025 reported-input bundle with explicit
interest/lease/investment unknowns**, no comparative registration or economic
treatment. Stop after this review; Phase 2 remains postponed.

Previously completed milestone: **MSFT FY2025–2026 treatment acceptance/input
checklist**, documentation-only Phase 1. [User-approved treatments](msft-treatment-acceptance-checklist.md)
accept recognized SBC expense as a labeled cost proxy counted once, consolidated
reported CFO history, separate narrow cash PP&E and reported cash taxes. No
operating-tax rate is approved. Lease cash-service is accepted in principle;
the three Note 13 cash-payment classes define a restricted perimeter, with
comprehensive coverage, borrowing-interest overlap and future-consumer
consistency unresolved. No sum or economic adjustment is authorized.
This closes the MSFT pilot **only for two-period reported-input preparation with
explicit accepted/conditional choices**, not complete NWC, reinvestment, interest
or FCFF readiness. Frozen-v1, schemas, values, bundles, sidecars and blockers
unchanged; baseline **1,905/1,483/11/27/42 = 3,468** carried forward.
Identities, retained evidence/digests, precision, status consistency and local
links checked; diff check passes. No SEC requests, tests or corpus rerun.
**Stop pending review.** Single next Phase 1 milestone: user decision accepting
the precise restricted lease-service perimeter and exclusions, or explicitly
requiring unavailable comprehensive coverage. No new annotation/research cycle;
Phase 2 remains postponed.

Previously completed milestone: **bounded MSFT analyst-treatment decision memo**,
documentation only, Phase 1. [Proposed recommendations](msft-analyst-treatment-decision.md)
use reported consolidated CFO as historical input basis, recognized SBC expense
as an explicitly accepted economic-cost proxy counted once, a consistently
applied lease cash-service convention, separate reported taxes/unpopulated
analyst operating-tax assumption, and narrow evidenced cash PP&E with combined
investment retained unallocated. These are proposed pending user review, not
registered policies, numerical adjustments or consumption approval.
Complete book NWC is unnecessary to reproduce reported CFO; cash-interest
completeness, organic cash/investment separation and integrated compatibility
are not thereby proved. Missing disclosures remain unknown, not zero or waived.
Primary methodological references, two frozen identities, reported points/
precision, evidence references, internal consistency, local links and diff check
validated. No SEC requests, tests/corpus, source/schema/policy/bundle/sidecar
changes. Baseline **1,905/1,483/11/27/42 = 3,468** unchanged.
**Stop for user review.** Smallest subsequent Phase 1 milestone, conditional on
that review: one two-period analyst-treatment acceptance/input checklist,
recording accepted choices/proxies, required missing inputs and future-consumer
checks. No automatic calculator, research/annotation cycle or blocker removal;
Phase 2 stays postponed.

Previously completed milestone: **two immutable MSFT FY2025–2026 cash-interest
annotation sidecars**, isolated Phase 1 implementation. [Implementation](msft-cash-interest-scope-annotation-design.md#implemented-isolated-version-1-sidecars)
and [registry](company-data-preparation/msft-cash-interest-annotations.json)
retain eleven exact input bindings, ten null unknowns, seven note/Item 7
locators, two research-only tax facts and four nonnumeric relationships per set.
Independent version-1 schema/registry; explicit verified parent required.
Absent/malformed/conflicting attachments cannot modify reported values, infer
zero or authorize summation/certification/consumption. No new amounts/calculator.
Validation: **24 focused and 142 relevant existing tests pass**, including
evidence/precision/conflict/serialization and parent serialized-byte preservation.
Compileall, exact two-set mapping, provenance, local links and diff check pass.
Parent source/registry/evidence, schemas, NWC blockers/scenarios and frozen-v1
artifacts unchanged; baseline **1,905/1,483/11/27/42 = 3,468** is carried forward.
No SEC requests or corpus rerun; no full-suite repeat because no existing shared
implementation changed. **Packaging sequence complete. Stop for user review**
of the [finite MSFT disposition table](company-data-preparation/MSFT.md#post-implementation-finite-disposition).
No further research or implementation starts automatically. Phase 2 remains
postponed; any later data milestone is conditional on that disposition.

Previously completed milestone: **MSFT FY2025–2026 additive cash-interest scope/unknown
annotation design**, documentation only. The [separate contract](msft-cash-interest-scope-annotation-design.md)
binds only the two immutable v1 reported bundles: eleven existing input
annotations and ten granular unknowns per period, plus research-only tax-interest
evidence. Exact parent/registry/period/input/occurrence and original-body identities
are mandatory. Separate schema/version, review locators, cash/accrual/noncash
roles and reported rounding survive serialization; missing/invalid/conflicting
attachments cannot alter parent values, infer zero, remove blockers or authorize
a total. All certification/summation/consumption flags remain false.
No model, registry, schema, policy or bundle implementation changed. Frozen-v1
baseline **1,905/1,483/11/27/42 = 3,468** and Phase 2 postponement remain.
Validation: two frozen identities, 22 input mappings, 20 issue IDs, four
research-only tax occurrences, precision/roles, pinned digests/body references,
version consistency, local links and diff check. No SEC requests/tests/corpus.
**Single next Phase 1 milestone:** implement only this isolated two-set sidecar
and focused binding/serialization/preservation tests. This closes the current
packaging sequence; the [finite blocker ledger](msft-cash-interest-scope-annotation-design.md#finite-blocker-disposition-and-next-milestone)
separates retained-evidence resolutions, analyst decisions and unavailable
disclosures. After implementation, request disposition of remaining limitations,
not another automatic annotation/research cycle or Phase 2 start.

Previously completed milestone: **bounded MSFT FY2025–2026 cash-interest completeness
review**, documentation-only Phase 1. [Two-period conclusions](msft-alternative-historical-cash-flow-inputs.md#cash-interest-completeness-review)
retain debt cash 1600m/1500m (rounded) and finance-lease cash 1372m/2547m as
separate disclosed inputs. Item 7 positively establishes finance-lease interest
and debt-interest capitalization effects on recognized aggregate expense
2385m/3051m; it is not debt-only, gross-incurred interest or cash paid.
No certified debt/lease cash sum, gross/net capitalization basis or complete
cash/accrual bridge. Operating-lease cash is not a disclosed interest split;
tax-position interest remains separately tax-scoped. **HOLD for all-in cash
interest**, not a declaration of incompatibility. Bounded research closes with
precise evidence gaps, not another broad issuer search.
Both frozen identities, four original-byte hashes/metadata, primary-note/Item 7
assertions, occurrences/precision, supported lease arithmetic, links and diff
checks pass. No SEC requests, tests, full suite, corpus or implementation changes;
immutable bundles, frozen schema 5, NWC blockers/scenarios and production
1,905/1,483/11/27/42 = 3,468 states remain unchanged.
**Single next Phase 1 milestone:** design additive MSFT cash-interest scope/unknown
annotations for the same two bundles, preserving v1, with no totals, estimates,
tax-shield calculation or valuation approval. Phase 2 remains postponed.

Previously completed milestone: **isolated MSFT FY2025–2026 reported cash-flow input
bundles**, strictly Phase 1. [Reviewed registry](company-data-preparation/msft-reported-cash-flow-bundles.json)
and [implemented boundary](msft-alternative-historical-cash-flow-inputs.md#implemented-isolated-reported-input-bundles)
package 37/38 scoped reported inputs, 42/43 confirming occurrences and 10/9
explicit unknowns. CFO 136,162m/182,935m and cash PP&E 64,551m/115,948m remain
separate; both fourteen-term reported CFO checks pass. Immutable original-byte
evidence/retrieval receipts, exact identities, raw/display signs, decimals and
scope labels survive separate schema `reported-cash-flow-input-bundle-v1`.
Only two bundles registered; registry/inventory/manifest hashes are pinned.
Deserialization rechecks evidence, all reviewed fields and statement arithmetic.
No default estimate, inferred zero, adjusted subtotal, CFO-minus-Capex calculation,
historical policy change or valuation consumer. Frozen schema 5, values/blockers,
partial NWC bundles and 1,905/1,483/11/27/42 = 3,468 remain unchanged.
No SEC requests or corpus rerun; Phase 2 remains postponed.
Validation: **22 focused tests and 120 relevant existing tests passed** (analyst
NWC foundation, three reviewed issuer bundle sets and Operating-NWC policies).
Compileall, exact registry mapping, original-body/occurrence binding, serialization,
local links/anchors and diff checks pass. Prior NWC models/bundles, frozen validation
artifacts and retained evidence are byte-identical to starting HEAD. Full suite
not rerun: no existing shared implementation changed; the new module is isolated.
**Single next Phase 1 milestone:** bounded same-period MSFT cash-interest
perimeter/completeness review (debt/finance-lease overlap and capitalized-interest
evidence), retaining explicit unknowns wherever not established. No adjusted
subtotal, implicit combination or broad issuer research cycle.

Previously completed milestone: **MSFT FY2025–2026 alternative reported historical
cash-flow input review**, strictly within the **Phase 1 blocker-resolution
extension**. [Evidence/input matrix](msft-alternative-historical-cash-flow-inputs.md)
supports PARTIAL GO for isolated reported inputs: CFO 136,162m/182,935m and cash
PP&E purchases 64,551m/115,948m, with distinct interest, tax, lease, SBC, investing
and noncash disclosures. Both complete reported CFO bridges reconcile.
FY2026 recasts FY2025 adjustment lines by cancelling −4,720m/+4,720m; selected
FY2025 sources are preserved. Debt cash interest is rounded and debt-scoped;
cash taxes are not expense taxes; cash purchases are not accrual/lease additions.
No adjusted subtotal, complete NWC or FCFF approval. Existing MSFT blockers and
partial bundles remain. Four retained original bodies, identities, occurrences,
precision, arithmetic, provenance and local links validated; diff check passes.
No new SEC requests, production changes, tests or corpus rerun. Frozen baseline
1,905/1,483/11/27/42 = 3,468 unchanged. Authoritative methodological references
inform proposed labels; SBC economics, tax/interest/lease and acquisition cash
treatments require explicit review before adjusted use, not estimates now.
**Single next Phase 1 milestone:** isolated two-period MSFT reported cash-flow
input bundles/provenance contract, with separate scoped facts and unknowns,
no adjusted calculation, period extension or blocker removal. Phase 2 remains
postponed, including forecasts, FCFF, DCF, WACC, terminal value and sensitivities.
This supersedes the immediately preceding pilot valuation-input decision as
the next task; prior partial-scenario results and limitations are retained.

Previously completed milestone: **reviewed Alphabet FY2024 rounded partial analyst-NWC
bundle**. [Detailed register](company-data-preparation/GOOGL.md#reviewed-fy2024-partial-input-bundle)
and [version-1 input](company-data-preparation/googl-analyst-nwc-bundle.json) bind
one frozen 10-K period and two original bodies. Six included instant facts plus
the rounded 3.2bn PP&E-in-AP note yield **13,342m at reported precision**.
The note is duration-tagged; explicit source-verified `manual_input` with rounded
precision/interpretation provenance preserves that fact, never inventing an
instant occurrence. Separate 7,104m accrued PP&E is retained but excluded.
Inventory and remaining AP scope unresolved; no opening/ΔNWC or NWC/FCFF certification.
**66 relevant tests passed** (57 existing + nine Alphabet), including provenance,
note precision/scope, failures, omissions and scenario/evaluation serialization.
Links, compileall and diff checks pass. No production source changes, SEC requests,
full suite or corpus rerun; frozen v1 and 1,905/1,483/11/27/42 = 3,468 unchanged.
The bounded three-issuer bundle pass is complete. [Remaining obstacles/decision](analyst-operating-nwc-design.md#remaining-obstacles-and-bounded-valuation-use-decision)
retain **diagnostic-only use / HOLD for forecast/FCFF consumption**; Phase 2 postponed.
Single next milestone: **MSFT FY2025–2026 pilot valuation-input acceptance decision**
under the existing timing contract, defining allowed perimeter, indispensable
missing inputs/assumption authority and cash/timing gates. No default estimates,
automatic approval, valuation code or broad research cycle.

Previously completed milestone: **reviewed explicit AAPL FY2025 narrow reported-driver
partial bundle**. [Detailed register review](company-data-preparation/AAPL.md#reviewed-fy2025-partial-input-bundle)
and [version-1 input](company-data-preparation/aapl-analyst-nwc-bundle.json) bind
one frozen 10-K period, two original-body digests and six exact occurrences.
Existing evaluator yields **−240m** from five included balances; known 8,919m
distribution/marketing is retained but explicitly omitted. Employee/investing-in-AP
allocations stay unknown; no operating-only AP, complete NWC or FCFF certification.
No opening bundle or ΔNWC; scope/precision/comparability limitations remain explicit.
**57 relevant tests passed** (41 foundation + eight MSFT + eight AAPL), covering
identity/evidence failures, omissions, unknown inputs and serialization.
Provenance, local links, compileall and diff checks passed. No production source
change, SEC request, full suite or corpus rerun. Frozen v1, AAPL blockers and
1,905/1,483/11/27/42 = 3,468 states unchanged. Phase 2 remains postponed.
Single next milestone: review one explicit GOOGL FY2024 partial bundle using
retained evidence; expose inventory omission and rounded PP&E-in-AP scope without
approving the conditional FY2025 allocation, cash ΔNWC or period extension.

Previously completed milestone: **reviewed explicit MSFT FY2025–2026 partial analyst
NWC input bundles**. [Detailed record](company-data-preparation/MSFT.md#reviewed-fy20252026-partial-input-bundles)
and [version-1 inputs](company-data-preparation/msft-analyst-nwc-bundles.json)
bind two frozen 10-K periods, four retained original-body digests and twelve
occurrences; Note 6 supports PP&E-in-AP exclusions of 6,900m/26,700m. Existing pure
evaluator yields partial levels −28,245m/−21,353m and +6,892m adjacent book movement,
versus −12,908m whole-AP diagnostic: +19,800m effect at submitted precision.
Explicit omissions, scope judgments and unresolved acquisition/FX/reclassification/
timing effects remain; no complete NWC, cash bridge or FCFF certification.
**49 relevant tests passed** (41 existing + eight bundle tests), provenance,
arithmetic, precision, serialization and local links validated; diff check passed.
No production source changes, SEC requests, full suite or corpus rerun. Frozen v1
and 1,905/1,483/11/27/42 = 3,468 states unchanged; MSFT v1 blockers remain.
AGENTS.md and the [register index](company-data-preparation/index.md#standing-maintenance-requirement)
now require affected issuer records to be updated in every data-preparation
milestone, retaining prior decisions and evidence. Phase 2 stays postponed.
Single next milestone: review one explicit AAPL FY2025 partial bundle from retained
evidence; expose unknown AP/employee/distribution scope, no estimates or extension.

Previously completed milestone: **isolated analyst-NWC scenario/provenance foundation
and company preparation register**. [Forty-issuer register](company-data-preparation/index.md)
tracks all seventeen measures, carried-forward evidence/states and unreviewed
details; Alphabet has one GOOG/GOOGL record. AAPL/MSFT/GOOGL retain detailed
limitations and no approved estimates. [Implemented boundary](analyst-operating-nwc-design.md#implemented-isolated-foundation)
provides immutable explicit scenarios, verified reported occurrences, labeled
omissions/overrides/ranges, partial book results and separate serialization.
No complete NWC/FCFF certification or automatic blocker removal.
**41 focused tests / 640 complete-suite tests passed**; fifteen retained driver
sums/twelve changes and MSFT's 19,800m effect reconcile. Register identities,
measure counts and evidence links checked; compileall and diff checks passed.
No SEC request/corpus rerun; schema 5, historical v1 sources/registries/evidence
and all baseline states remain unchanged. Phase 2 remains postponed.
Next bounded milestone: review and publish explicit MSFT FY2025–2026 partial
scenario input bundles with classified omissions and retained provenance; no
earlier-period estimates, cash bridge or forecast consumption.

Previously completed milestone: **post-freeze analyst Operating NWC methodology/design
for AAPL/MSFT/GOOGL**, [decision/contract](analyst-operating-nwc-design.md) and
[fifteen-period inventory](analyst-operating-nwc-inventory.json). **Phase 2 remains
postponed by explicit direction.** Frozen historical v1 and all current blockers
are unchanged. GO for a separate assumption/scenario layer, not automatic
normalized NWC or cash ΔNWC approval. AAPL employee/distribution allocations,
earlier MSFT supplier AP, and GOOGL AP/inventory completeness remain uncertain;
specific later PP&E-in-AP disclosures support partial adjustments only.
Thirty-four response bodies/digests retained (five reused/29 targeted retrievals);
15 driver sums/12 adjacent movements verified, not certified cash investment.
No production policies, schemas or code changed; no full tests/corpus rerun.
Next bounded implementation: isolated analyst-NWC scenario/assumption-provenance
models and pure reported-driver/override evaluator, without default estimates
or blocker removal. Timing readiness is still required before eventual forecast
historical-ratio/FCFF consumption, but Phase 2 start is not authorized here.

Previously completed milestone: **Phase 1H.6 — historical-normalization-v1 scope
freeze**. [Frozen contract, versions, exclusions and artifact digests](historical-normalization-v1-freeze.md).
**Phase 1H complete with qualified scope, not complete Top 50 support.**
Baseline remains 50 issuers / 51 securities; 2 supported / 40 generalization /
8 specialized; execution 43 completions / seven skips; 204 × 17 = 3,468 states,
1,905/1,483/11/27/42. Capex 167/37/0 = 147 direct + 20 curated.
Schema 5 and immutable exact-accession policies are frozen without production
changes. XOM has no history; GEV/SNDK two periods each; GE's specialized
classification remains separate from execution. No integrated FCFF certification.
Next: **Phase 2 — implement the bounded financial timing-readiness valuation
boundary** from the existing design, before historical-ratio forecast/FCFF use;
no FCFF calculator or invented adjustments. Phase 2A assumptions already exist.
Counts, versions, retained evidence bytes and links verified; no SEC requests,
tests or corpus rerun. No push or tag.

Previously completed milestone: **Phase 1H.5 — S&P 500 Top 50 historical coverage
validation**, documentation-only [all-company matrix](universe/phase-1h5-issuer-validation.md)
and [machine-checkable evidence/decisions](universe/phase-1h5-issuer-validation.json).
All 50 CIKs / 51 security entries reconcile: **2 SUPPORTED / 40
GENERALIZATION_REQUIRED / 8 SPECIALIZED_METHODOLOGY_REQUIRED**. GE is explicitly
reassessed for consolidated industrial/insurance scope; its existing generic
execution remains unchanged. Classification is not execution dispatch: **43
generic completions / seven specialized skips**, 204 periods × 17 measures =
3,468 states, **1,905/1,483/11/27/42**. META/COST support is historical core scope,
not full-field or integrated FCFF certification. XOM has zero periods; GEV/SNDK
two each; original selected-accession and separation limits remain explicit.
Capex stays 167/37/0; 57 original gaps = 20 curated approvals + 37 unapproved.
No new policy, SEC request, test or corpus rerun. Original validated corpus bytes
are retained with explicit digest/run provenance; all counts and links verified.
**Ready for Phase 1H.6 with explicit limitations, not yet frozen.** Single next
milestone: freeze historical normalization v1 supported scope, policy/provenance
contracts and exclusions. Valuation remains paused until that freeze; joint
timing readiness must precede later FCFF consumption.

Previously completed milestone: **Phase 1H.4 Wave 46**, documentation-only
[generalization exit consolidation](phase-1h-generalization-exit-plan.md).
**Proceed to Phase 1H.5 with documented exclusions; no further implementation
or issuer research is an essential prerequisite.** All 17 measure rows reconcile
to 1,905 resolved / 1,483 missing / 11 ambiguous / 27 methodology-blocked /
42 not-comparable = 3,468 states across 204 periods, 43 completions and seven
specialized skips. Capex research is closed: 57 = 20 curated + 37 unapproved
(17 concept, 17 derivation, 3 methodology); 147 direct results separate/unchanged.
Debt variants and share-scale research remain bounded deferred options, not exit
requirements. No 100% coverage or universal FCFF readiness criterion is added.
Pipeline completion is not supported-company status; XOM's empty history and
GEV/SNDK's two-period histories remain explicit limitations.
Single next milestone: **Phase 1H.5 — S&P 500 Top 50 validation pass**, reassessing
all 51 security rows / 50 issuers, classifying support and documenting typed
exclusions. This pass and Phase 1H.6 freeze are not yet complete; valuation remains
paused. No SEC requests, code/policy changes, tests or corpus rerun in Wave 46.

Previously completed milestone: **Phase 1H.4 Wave 45**, documentation-only
[GE Capex perimeter research](capex-ge-perimeter.md) and
[three-row supplement](capex-ge-scope-inventory.json). All three retain
`METHODOLOGY_BLOCKER` / `BUSINESS_AND_ASSET_PERIMETER_GATED`; consolidated
continuing PP&E/software cash is not an evidenced industrial-only perimeter.
NO-GO, zero safe new coverage/equations. Forty-two verified bodies: thirty-nine
reused, three primary-filing retrievals. Current Capex research pass closes:
57 original identities = 20 curated approvals + 37 unapproved (17 concept,
17 derivation, 3 methodology). The 147 direct results remain separate/unchanged.
Production remains Capex 167/37/0 and aggregate 1,905/1,483/11/27/42 = 3,468;
no tests or corpus rerun. Prior issuer decisions and policies unchanged.
Next bounded milestone: consolidate remaining Phase 1H.4 failure priorities and
evidence-exhausted exclusions across measures, then select one reusable task
before Phase 1H.5 validation. This does not close Phase 1H.4 or authorize freeze.

Previously completed milestone: **Phase 1H.4 Wave 44**, documentation-only
[GEV cash/perimeter research](capex-gev-cash-perimeter.md) and
[two-row supplement](capex-gev-scope-inventory.json). Both retain `DERIVATION` /
`COMPONENT_SCOPE_UNPROVED`; reported cash additions combine PP&E/internal-use
software without exhaustive eligible cash mapping. The 2024 spin-off and parent
cash caveats are retained separately from historical value validity. NO-GO,
zero safe new coverage or equations. Thirty-two verified original bodies:
twenty reused, twelve targeted retrievals. Production remains Capex 167/37/0;
aggregate 1,905/1,483/11/27/42 = 3,468. No tests or corpus rerun.
Next bounded milestone: three frozen GE Capex cash/perimeter periods, no
predecessor reconstruction or specialized implementation. Reopen GEV only with
new complete cash-scope evidence. Prior issuer decisions unchanged.

Previously completed milestone: **Phase 1H.4 Wave 43**, documentation-only
[PEP component/perimeter research](capex-pep-component-perimeter.md) and
[five-row supplement](capex-pep-scope-inventory.json). All five retain
`CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`: exact annual cash spending and
software-in-PP&E scope are evidenced, but exhaustive eligible purchase cash
and any non-overlapping equation are not. NO-GO; zero safe additional coverage.
Seventy reviewed original bodies have typed verified digests; historical
fingerprints remain separate. Frozen inventory, methodology, policies and prior
issuer decisions unchanged. Production carried forward: Capex 167/37/0;
aggregate 1,905/1,483/11/27/42 = 3,468. No tests or corpus rerun.
Next bounded milestone: documentation-only cash/perimeter research for two
frozen GEV Capex periods. Reopen PEP only with new complete cash-scope evidence.

Previously completed milestone: **Phase 1H.4 Wave 42**, documentation-only
[VZ component/perimeter research](capex-vz-component-perimeter.md) and
[five-row supplement](capex-vz-scope-inventory.json). All five retain
`DERIVATION` / `COMPONENT_SCOPE_UNPROVED`: cash/software inclusion and specific
spectrum/acquisition/lease/noncash exclusions are evidenced, but exhaustive
eligible cash scope and any non-overlapping equation are not. NO-GO, zero safe
additional coverage. Seventy original bodies retain typed verified digests:
fifty reused and twenty specific-gap retrievals. Frozen inventory, methodology,
policies and prior issuer decisions unchanged. Production carried forward:
Capex 167/37/0, aggregate 1,905/1,483/11/27/42 = 3,468; no tests or corpus rerun.
Next bounded milestone: documentation-only component/perimeter research for
five frozen PEP periods. Reopen VZ only with new complete cash-scope evidence.

Previously completed milestone: **Phase 1H.4 Wave 41**, documentation-only
[MRK scope research](capex-mrk-scope.md) and
[two-row supplement](capex-mrk-scope-inventory.json). Both frozen 2021–2022
periods retain `CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`: internal-use software
versus cloud-service capitalization and separate acquisition/Organon cash are
evidenced; exhaustive cash PP&E scope and any justified perimeter bridge are not.
NO-GO for acceptance/derivation, zero safe coverage. All 26 original bodies were
reused with verified typed digests; no new SEC requests or evidence refresh.
Prior issuer decisions and frozen inventory/policies unchanged. Production
carried forward: Capex 167/37/0, aggregate 1,905/1,483/11/27/42 = 3,468.
No tests or corpus rerun. Reopen MRK only for new exact-period scope evidence.
Next bounded milestone: documentation-only component/perimeter research for
five frozen VZ other-productive-asset cash periods, including licenses/intangibles.

Previously completed milestone: **Phase 1H.4 Wave 40**, documentation-only
[HD scope research](capex-hd-scope.md) and
[five-row supplement](capex-hd-scope-inventory.json). All five retain
`CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`: software/construction capitalization
and separate cash/acquisition/lease/noncash lines are evidenced, but exhaustive
eligible cash purchase scope is not. NO-GO for acceptance/derivation, zero safe
coverage. Fifty-eight current response bodies have typed verified digests;
historical report hashes are preserved separately, not certified from extracted
text equality. Frozen inventory and policies unchanged; QCOM not reopened.
Production carried forward: Capex 167/37/0, aggregate 1,905/1,483/11/27/42 = 3,468.
No tests or corpus rerun. Next bounded milestone: documentation-only scope
research for two frozen MRK Capex periods (2021–2022), including acquisition/IPR&D cash
separation. Reopen HD only for new exact-period completeness evidence.

Previously completed milestone: **Phase 1H.4 Wave 39**, documentation-only
[QCOM scope research](capex-qcom-scope.md) and
[five-row supplement](capex-qcom-scope-inventory.json). All five exact selected
periods retain `CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`: cash purchase values
and separate acquisitions are evidenced, but a complete eligible PP&E/software
cash perimeter is not. NO-GO for acceptance/derivation; zero safe additional
coverage. Fifty-nine current SEC response bodies retain typed verified digests;
ten historical report fingerprints differ and remain explicitly unverified,
not replaced on extracted-text equality. Frozen inventory/policies unchanged.
Production carried forward: Capex 167/37/0, aggregate 1,905/1,483/11/27/42 = 3,468.
No tests or corpus rerun. Reopen QCOM only for new exact-period completeness
evidence. Next bounded milestone: documentation-only scope research for five
frozen HD cash PP&E candidates, without transferring Visa/QCOM conclusions.

Previously completed milestone: **Phase 1H.4 Wave 38**, five Visa curated Capex v3
entries implemented and [validated](capex-visa-scope-evidence-results.md).
Immutable v1/v2 registries, fifteen prior approvals and all 147 direct results
are unchanged. The original 57 identities reconcile to five new Visa results,
fifteen prior approvals and 37 unchanged unapproved controls. Capex is
**167 resolved / 37 missing / 0 ambiguous**; aggregate is
**1,905/1,483/11/27/42 = 3,468**. All other measures, 43 issuer completions and
seven specialized skips are unchanged. Focused tests: 47 passed; complete suite:
599 passed once. Five retained-accession checks and one corpus gate passed;
65 mandatory Visa response bodies remain byte-verified, with schema-5 provenance.
No generic fallback, adjustment equation, primitive expansion or FCFF readiness
approval. Next bounded milestone: documentation-only scope research for the
five frozen QCOM Capex periods, using the existing cash PP&E primitive.

Previously completed milestone: **Phase 1H.4 Wave 37**, documentation-only
[Visa scope acceptance design](capex-visa-scope-evidence-design.md) and
[machine-checkable matrix](capex-visa-scope-evidence-matrix.json).
PARTIAL GO for five additive `capex_scope_equivalence_v3` reported-value designs,
alongside unchanged ten-entry v1 and five-entry v2. Five/fifteen/37 reconciles
the original 57 inventory identities; 147 direct results are separate.
All 65 original artifacts and 35 entry-associated reviews are mandatory;
unverified discovery fingerprints remain ancillary. Exact matching, conservative
failure, confirming occurrences, precedence and schema-5 provenance are specified.
No generic fallback, primitive expansion, equation or production approval.
Production remains Capex 162/42/0, aggregate 1,900/1,488/11/27/42 = 3,468.
Next bounded milestone: implement only five Visa v3 entries with focused/57-row
checks, targeted live validation, then one full suite and one corpus gate;
preserve fifteen approvals, 147 direct results and all other states/execution.
No tests, corpus, SEC retrieval or runtime changes in this design milestone.

Previously completed milestone: **Phase 1H.4 Wave 36**, documentation-only
[Visa software methodology review](capex-visa-software-methodology.md).
PARTIAL GO for five exact-accession reported-value scope designs: the evidenced
capitalized operational software cost perimeter is eligible under existing
cash PP&E methodology, not a general software/intangible expansion. The updated
[five-row supplement](capex-visa-technology-inventory.json) preserves Wave 35's
decisions and all operands/evidence. Five candidates, zero equations/production
approvals; no acquisition fair-value adjustment or missing-as-zero. Existing
147 direct and fifteen curated results remain unchanged, not retrospectively
recertified. No tests, corpus, new SEC retrieval or evidence refresh.
Next bounded milestone: documentation-only design of five Visa exact-accession
scope entries alongside immutable v1/v2, with five/fifteen/37 inventory and
147 direct-preservation gates. No implementation or consumer-readiness approval.

Previously completed milestone: **Phase 1H.4 Wave 35**, documentation-only
[Visa Capex technology research](capex-visa-technology-perimeter.md) and
[five-row supplement](capex-visa-technology-inventory.json). All five retain
`CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`, zero approved additional coverage
or equations. Consolidated cash purchases are evidenced, but the purchased/
developed software asset perimeter needs an explicit current-primitive
methodology decision; no complete cash split supports an exclusion. Acquisition
and book values, noncash lease additions and D&A approvals are not cash operands.
Sixty-five original bodies retain typed digests; historical unverified discovery
fingerprints remain separate. Production and frozen inventory unchanged; no
tests or corpus rerun. Next bounded milestone: methodology review of these
five Visa technology perimeters with explicit existing-policy impact assessment,
not a primitive change to force coverage or broader issuer research.

Previously completed milestone: **Phase 1H.4 Wave 34**, documentation-only
[LRCX component-completeness research](capex-lrcx-component-completeness.md)
and [five-row supplement](capex-lrcx-component-inventory.json). All five retain
`DERIVATION` / `COMPONENT_SCOPE_UNPROVED`; NO-GO for direct acceptance or a
complete cash equation, zero safe additional coverage. Selected asset,
lease/commitment and acquisition notes do not establish the intangible cash
split. Sixty-two original bodies are retained with typed digests; historical
unverified discovery fingerprints remain separate. Existing approvals,
frozen inventory and production unchanged; no tests or corpus rerun.
Next bounded milestone: documentation-only research of five frozen Visa Capex
cash-technology/software and PP&E perimeter controls. D&A approvals do not
approve their cash scope. Reopen LRCX only with new exact-period cash evidence.

Previously completed milestone: **Phase 1H.4 Wave 33**, the documentation-only
[NVDA combined Capex scope research](capex-nvda-combined-scope.md) and
[five-row supplement](capex-nvda-combined-inventory.json). All five frozen
periods retain `DERIVATION` / `COMPONENT_SCOPE_UNPROVED`, with zero safe additional
coverage or approved equation. Two issuer extensions remain separately gated.
The selected statements/notes distinguish intangible classes, noncash additions,
leases and separate acquisition/Groq cash but do not exhaust the PP&E-only cash
split. Fifty-five original bodies have typed digests; ten unavailable old
renderer fingerprints are preserved separately from newly reviewed bodies.
Production, frozen inventory and existing approvals are unchanged; no tests or
corpus rerun. Next bounded milestone: documentation-only component-completeness
research for the five frozen LRCX combined Capex/intangible periods. Do not
reopen NVDA without genuinely new exact-period cash-allocation evidence.

Latest production milestone: **Phase 1H.4 Wave 32**, the
[five-entry CVX curated Capex v2 implementation](capex-cvx-scope-evidence-results.md).
Verified production: Capex **162 resolved / 42 missing / 0 ambiguous**;
aggregate **1,900 resolved / 1,488 missing / 11 ambiguous / 27 methodology-blocked /
42 not-comparable**, total **3,468** across 204 annual periods. All 147 direct
Capex results, ten immutable v1 approvals, 42 controls, other measures,
43 generic completions and seven specialized skips are unchanged. The 31 focused
and 583 complete tests and five targeted artifact checks were reused; after a
bounded successful SEC connectivity check, the resumed corpus gate passed.
No generic fallback, adjustment equation or FCFF-readiness approval was added.
Its bounded NVDA follow-up is completed in Wave 33 above; no new cash equation
or scope acceptance is supported by matching totals, balances or residuals.

Phase 1H expands historical normalization beyond the original five-company
corpus. Phase 1H.1 froze the S&P 500 Top 50 Index snapshot effective 2026-10-02
at `docs/universe/sp500-top-50-2026-10-02.csv`. Its 51 securities represent 50
unique SEC issuers because Alphabet has two included share classes. The
preliminary security classification contains six supported-seed rows (five
issuers), 38 operating-company candidates, and seven
specialized-methodology candidates.

Phase 1H.2 executed the current production pipeline for all 43 generic issuers.
Forty-one reached standardized output, while GEV and SNDK failed at Company
Facts parsing with the existing invalid-CIK validation error. The seven
specialized issuers remained represented as explicit skips. XOM reached
standardized output with zero selected annual periods; this and all typed
missing or ambiguous results remained evidence rather than automatic
methodology conclusions.

Phase 1H.3 completed the root-cause analysis in
`docs/universe/sp500-top-50-failure-taxonomy.md`. It reconciles all 3,400
standardized measure states for the 40 five-period histories, inventories all
24 ambiguities and 27 methodology blockers, diagnoses GEV/SNDK as one
zero-padded Company Facts CIK schema case, and diagnoses XOM as a ticker/CIK
registrant-succession case. The post-smoke issuer classification is two
`SUPPORTED`, 41 `GENERALIZATION_REQUIRED`, and seven
`SPECIALIZED_METHODOLOGY_REQUIRED`.

Phase 1H.4 Wave 1A implemented the first shared schema fix. Company Facts now
accepts an exact ten-digit padded CIK only when it equals the requested
company's `cik_padded`; arbitrary leading-zero strings and identity mismatches
remain invalid. Live reruns moved both GEV and SNDK through Company Facts and
all later stages to standardized output, with two annual periods each. The
full corpus rerun completed all 43 generic attempts with no stage failures and
left every five-issuer seed result unchanged. No issuer hardcode was added.

Phase 1H.4 Wave 1B completed the registrant-succession design in
`docs/sec-identity-linkage.md`. Official XOM filings establish the human-reviewed
edge from predecessor CIK 34088 to current successor CIK 2115436, effective
2026-07-01. The design nevertheless reached **NO-GO** for a generic automated
resolver: public structured SEC sources discover candidates but do not encode
the directed legal edge, while the decisive relationship remains in variable
narrative filing text. Cross-listing alone is explicitly rejected. No source
or test code changed, no issuer mapping was added, and XOM remains unresolved
in production.

Phase 1H.4 Wave 2 generalized the exact standard
`us-gaap:CashAndCashEquivalentsAtCarryingValue` Company Facts policy by removing
its five-seed-CIK restriction while preserving the existing selected-accession,
current-instant, report-date, USD, integer, and ambiguity rules. A live corpus
rerun increased cash coverage from 25 resolved / 179 missing / 0 ambiguous to
185 resolved / 19 missing / 0 ambiguous across the 204 selected periods. The
160 new resolutions span 34 issuers. The difference from the Phase 1H.3
estimate of 158 is SNDK's two exact eligible periods, which became available
after Wave 1A fixed its padded Company Facts CIK.

The 19 remaining cash gaps are INTC (four periods), CVX (three), PG (five), GE
(five), and GEV (two). Their selected filings expose broader restricted-cash
captions; PG also uses `CashEquivalentsAtCarryingValue`, and GE has a
disposal-group-inclusive caption. Wave 2 does not treat those concepts as the
same primitive, derive unrestricted cash, consume filing XBRL, or combine cash
with investments. Aggregate standardized states reconciled exactly to 1,823
resolved, 1,549 missing, 27 ambiguous, 27 methodology-blocked, and 42
not-comparable, with all 3,468 states and all other measure statuses unchanged.

Phase 1H.4 Wave 3 researched annual-period association and reached a blocked
result. A selected 10-K can contain both fiscal-year and Q4 durations, and a
unique current diluted-share duration ending on the report date does not prove
annuality. No source evaluated in that wave established the fiscal-year start,
so no automatic period filter was added. The 11 full-year/Q4
revenue collisions across JNJ, ABBV, GE, and ORCL remain typed ambiguity, as do
JNJ pretax and downstream reported ETR, plus SNDK pretax, income-tax expense,
and downstream reported ETR.

The other 11 revenue ambiguities are genuine full-year concept conflicts: five
WMT periods, one MA period, and five CVX periods. Filing presentation shows WMT
net sales versus total revenues, MA gross versus net revenue, and CVX sales and
other operating revenues versus revenues and other income. Those economic
definitions differ, so Wave 3 adds no global or issuer-specific precedence and
does not select by size or concept order. The corpus therefore remains at the
Wave 2 baseline: 1,823 resolved, 1,549 missing, 27 ambiguous, 27
methodology-blocked, and 42 not-comparable across 204 periods and 3,468 states.

Phase 1H.4 Wave 4 found authoritative annual-period evidence and records a
**GO** design in `docs/annual-period-evidence.md`. SEC staff guidance for EDGAR
validation describes the DEI required context for an exact 10-K as the
dimensionless duration matching the year of the submission reporting period;
the EDGAR Filer Manual and applicable filing requirements remain controlling.
A read-only diagnostic verified one consistent
DEI FY context across 42 selected filings for JNJ, ABBV, GE, ORCL, WMT, COST,
SNDK, META, and MSFT, including non-calendar and 52/53-week histories. All
eligible non-parenthetical duration-statement anchors independently matched the
same period. No production filter was added in this research milestone, so the
Wave 2 corpus totals and all 22 revenue ambiguities remain unchanged.

Phase 1H.4 Wave 5 implements the pure, network-free SEC-layer annual-period
resolver. Filing-XBRL contexts now preserve the raw entity-identifier scheme;
the resolver requires `http://www.sec.gov/CIK` plus a value matching the filing
registrant. It groups equivalent context IDs by normalized entity, dimensions,
period, and DEI values; identical duplicates confirm, conflicting same-context
DEI values are data errors, and different valid periods remain ambiguity. Its
immutable result types distinguish resolved, not-found, ambiguous, unsupported,
and data-error outcomes while retaining all confirming context IDs and DEI
provenance.

Thirteen focused annual-period tests and 18 filing-XBRL tests pass. Read-only
validation against the same 42 selected exact 10-Ks resolved all 42 and matched
every Wave 4 start/end date, including JNJ's annual/Q4 collision, COST's 53-week
year, SNDK's non-calendar year, and valid year-quarter SEC DEI namespaces. No
normalization integration was added, so all 22 revenue ambiguities and the Wave
2 standardized corpus totals remain unchanged.

Phase 1H.4 Wave 6 explicitly integrates typed annual-period results into annual
normalization for Revenue, Pretax Income, and Income Tax Expense only. A
resolved result filters CURRENT duration candidates to its exact `(start, end)`
before ambiguity evaluation. Not-found, ambiguous, and unsupported results
retain prior candidate behavior, while a data-error result stops normalization.
Each filing result retains the annual-period outcome beside existing metric
provenance; the standardized-output schema is unchanged.

The full 204-period corpus rerun resolved 11 annual/Q4 Revenue ambiguities, JNJ
Pretax Income and downstream Reported ETR, and SNDK Pretax Income, Income Tax
Expense, and downstream Reported ETR. Revenue is now 193 resolved / 0 missing /
11 ambiguous. The remaining conflicts are five WMT periods, one MA period, and
five CVX periods whose competing concepts span the same authoritative annual
period. Aggregate states reconcile to 1,839 resolved, 1,549 missing, 11
ambiguous, 27 methodology-blocked, and 42 not-comparable across 3,468 states.
All other measure states and the five-company seed metric results are unchanged;
all 43 generic attempts completed and seven specialized issuers remained
skipped. Seventy-five historical-normalization tests, 17 corpus-runner tests,
304 normalization tests, and 461 tests overall pass.

Phase 1H.4 Wave 7 inventories all 45 remaining Pretax Income gaps in
`docs/pretax-income-concepts.md` and reaches **PARTIAL GO FOR FURTHER
RESEARCH/DESIGN ONLY** for one recurring standard concept. The concept
`IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments`
is an exact annual Company Facts observation in 33 periods across seven
issuers, but its taxonomy definition excludes equity-method income or loss.
It remains `NEEDS_MORE_RESEARCH` and is not approved for normalization: being
the reported tax denominator does not prove equivalence to the current Pretax
scope. Current filing-XBRL tooling does not preserve presentation roles or
statement placement needed to make that evidence machine-checkable. The other
12 gaps use issuer extensions across ORCL, MCD, and PG;
domestic/foreign components and extension local-name matching remain
unapproved. Structural candidate coverage is 33 periods, safe new resolutions
are zero, and no production policy or corpus result changed. Independent review
confirmed that numerical equality, tax-denominator status, and primary-statement
placement are not sufficient evidence of semantic equivalence.

Phase 1H.4 Wave 8 defines Pretax presentation-evidence research in
`docs/pretax-presentation-evidence-design.md` and reaches **PARTIAL GO FOR A
READ-ONLY RESEARCH DIAGNOSTIC**. Filer-submitted presentation roles can classify
ordered `Statement` membership, while the extracted instance binds the exact
fact and annual context. SEC render artifacts remain corroborating derivatives,
and equity-method note evidence remains a separate semantic gate. The design
does not change `PRETAX_INCOME_POLICY`, the current Pretax primitive, production
models, or corpus results.

Phase 1H.4 Wave 9 implements the development-only, read-only diagnostic and
records its live results in `docs/pretax-presentation-evidence-results.md`. All
33 frozen standard-concept candidate periods reconciled to the exact selected
10-K, authoritative annual context, exact USD fact, submitted schemas and
presentation linkbases, and SEC-renderer artifacts. Every candidate belongs to
one submitted `Statement` role and one to three submitted `Disclosure` roles;
all 33 therefore classify as `MULTIPLE_ROLE_MEMBERSHIP`. MetaLinks and an
applicable R-file corroborated all 33, with zero presentation data errors.

The evidence-pattern decision is **NEEDS_MORE_RESEARCH**. Statement membership
is established but equity-method scope remains a separate semantic gate. The
issuer matrix retains direct evidence of `SEPARATE_NET_OF_TAX` for AMZN and
`INCLUDED_PRETAX` for CVX while MU, MA, CAT, PM, and LIN remain `UNRESOLVED`;
these classifications do not approve any period. Safe new Pretax resolutions
remain zero, and production policies, standardized outputs, and corpus totals
are unchanged.

Phase 1H.4 Wave 10 completes exact-period equity-method note research in
`docs/pretax-equity-method-note-evidence.md` using the 33 frozen selected
accessions. Direct filing evidence classifies eight periods as `INCLUDED_PRETAX`
(MA three and CVX five), 20 as `SEPARATE_NET_OF_TAX` (AMZN, MU, CAT, and PM
five each), and five as `UNRESOLVED` (LIN). Linde directly reports mixed
treatment: corporate-investee income is after tax while partnership/LLC
investee income enters Pretax. No period is `SEPARATE_PRETAX` or
`NO_MATERIAL_ACTIVITY_FOUND`.

The same candidate concept therefore has issuer-dependent economics. Manual
exact-accession evidence establishes inclusion for eight periods, but no
deterministic, machine-checkable economic-equivalence rule was established.
Safe new production Pretax resolutions remain zero; `PRETAX_INCOME_POLICY`,
the 159 resolved / 45 missing / 0 ambiguous Pretax corpus result, and all
aggregate corpus totals remain unchanged. The 12 issuer-extension periods were
excluded as required.

Phase 1H.4 Wave 11 completes the separately reviewed scope-evidence design in
`docs/pretax-scope-evidence-design.md` and reaches **PARTIAL GO**. No automated
structured-evidence rule separates the eight MA/CVX positives from the 20
separate-net-of-tax and five LIN mixed-treatment controls: all 33 share the
same candidate and multiple-role presentation pattern, while MA's tag
transition and CVX's taxonomy/presentation mismatch require manually reviewed
filing evidence.

A curated, immutable `pretax_scope_equivalence_v1` registry is methodologically
acceptable for the eight exact CIK/accession/period/concept facts, provided a
later implementation retains policy version and reviewed evidence provenance,
keeps the current approved concept first, and defaults every future, amended,
or unregistered filing to missing. This is deterministic execution of manual
research, not automated discovery or a generic concept fallback. Wave 11 adds
no registry or source behavior: all 33 remain production missing, safe new
Pretax resolutions remain zero, and Pretax remains 159 resolved / 45 missing /
0 ambiguous.

Phase 1H.4 Wave 12 implements and validates that exact boundary. The immutable
`pretax_scope_equivalence_v1` registry contains only the eight reviewed MA/CVX
CIK-accession-period facts. The generic `PRETAX_INCOME_POLICY` remains
unchanged and retains precedence. The curated resolver groups eligible
nondimensional filing-XBRL occurrences by a complete semantic signature,
allowing MA's three repeated occurrences and CVX's two repeated nondimensional
occurrences to confirm one value while excluding CVX's dimensioned facts. It
retains every occurrence, original representation, and deterministic ordinal
through normalized Pretax, standardized-output schema version 2, serialization,
and Reported ETR supporting-policy provenance.

Focused validation passes 122 tests, the complete suite passes 491 tests, and
targeted live normalization resolves exactly eight Pretax and eight Reported
ETR periods. The full 204-period corpus produces Pretax and Reported ETR at
167 resolved / 37 missing / 0 ambiguous each. All 25 controls and all 12
ORCL/MCD/PG issuer-extension periods remain missing. Aggregate states reconcile
exactly to 1,855 resolved, 1,533 missing, 11 ambiguous, 27
methodology-blocked, and 42 not-comparable across 3,468 states; the only corpus
changes are the eight Pretax and eight corresponding Reported ETR resolutions.

Phase 1H.4 Wave 13 completes the exact selected-filing
[Operating Income concept inventory](operating-income-concepts.md). All 35
missing periods—five
each for LLY, JNJ, CVX, MRK, GE, KLAC, and IBM—reconcile to their frozen
selected accessions, authoritative annual periods, submitted income-statement
roles, and SEC-rendered face statements. None reports a consolidated Operating
Income subtotal, none has an exact Company Facts observation, and none has an
exact annual nondimensional filing-XBRL Operating Income fact. GE 2024 and 2025
contain only economically distinct dimensioned segment and reconciliation
`OperatingIncomeLoss` facts.

Wave 13 reaches **NO-GO FOR DIRECT CONCEPT-POLICY EXPANSION**. Safe potential
direct coverage is zero. Twenty-five LLY/JNJ/MRK/KLAC/IBM periods have
component patterns that require separate derivation-evidence design; CVX has no
reported consolidated Operating Income, while GE requires separate
business/perimeter and segment-reconciliation research. No source, test, or
policy changes were made, all 35 periods remain missing, and production counts
remain unchanged.

Phase 1H.4 Wave 14 completes the
[Operating Income component-derivation evidence design](operating-income-derivation-design.md)
for those 25 exact LLY/JNJ/MRK/KLAC/IBM periods and reaches **PARTIAL GO**. All
25 are `DERIVATION_APPROVED`: each candidate starts from Revenue or an
independently reconciled Gross Profit, includes a complete and non-overlapping
operating-cost perimeter, and bridges through every separately reported
non-operating item to Pretax. Twenty-two Pretax bridges reconcile exactly; IBM
2022, 2023, and 2025 differ by only one displayed $1 million unit because its
face statements round every independently reported line to whole millions.

The reviewed perimeter includes acquired IPR&D, restructuring, operating-asset
impairments, pension service cost, and IBM IP/custom-development income. It
excludes interest, non-service pension components, and reviewed other
non-operating activity. No generic cross-issuer concept rule is approved:
changing concepts, issuer extensions, explicit row absence, LLY's differing-
precision IPR&D occurrences, and IBM's rounding boundary require a curated
exact-accession policy design. Safe potential coverage is 25 periods; CVX and
GE remain outside the pass. Production code, tests, policies, and counts remain
unchanged.

Phase 1H.4 Wave 15 completes the
[curated Operating Income derivation-policy design](operating-income-derivation-policy-design.md)
and reaches **PARTIAL GO** for a later narrow implementation. The proposed
immutable `operating_income_component_derivation_v1` registry contains only
the 25 reviewed exact CIK/accession/period equations. It freezes ordered signed
filing-XBRL operands, explicit row absence, exact-value and occurrence rules,
reviewed lower-precision LLY evidence, independent Gross Profit and Pretax
validation, direct-result precedence, complete provenance and serialization,
and an Operating Tax compatibility boundary.

IBM's three one-million Pretax differences remain validation-only signed
variances at the filing's whole-million display scale; no derived value is
rounded, normalized, or plugged. Equivalent occurrences may confirm only when
their complete semantic signature and exact `Decimal` agree. Unexpected values
remain ambiguous, structural evidence faults remain errors, and future,
amended, or unregistered filings produce no derivation. The ten CVX/GE periods
are frozen negative controls. No production code, test, policy, or corpus count
changes in this design wave.

The current validated standardized-output corpus contains 204 selected annual
periods across the 43 generic issuer attempts. All 43 attempts complete through
standardized output, while the seven specialized issuers remain explicit
skips. Validation means the production historical pipeline was run and checked
against expected filing evidence, not that every metric resolved; missing,
ambiguous, methodology-blocked, and not-comparable states remain explicit and
are never inferred as zero.

Phase 1H.4 Wave 16 implements and validates
`operating_income_component_derivation_v1` for exactly the 25 reviewed
LLY/JNJ/MRK/KLAC/IBM equations. The generic direct policy remains first;
filing-XBRL operands, exact identities, ordered signed arithmetic, every
confirming occurrence and reviewed nonselected evidence remain mandatory.
IBM's exact signed rounding variances are validation gates only. Standardized
output schema 3 and Operating Tax supporting-input serialization retain the
complete immutable provenance; no tax policy becomes ready automatically.

Validation: 163 focused tests and 513 complete-suite tests pass. Targeted live
validation resolves all 25 positives and keeps all ten CVX/GE controls missing.
The full 43-issuer run completes with seven specialized skips, 204 periods and
3,468 measure states. Operating Income is **194 resolved / 10 missing / 0
ambiguous** (169 direct, 25 derived). Aggregate states are **1,880 resolved /
1,508 missing / 11 ambiguous / 27 methodology-blocked / 42 not-comparable**.
Same-input comparisons preserve all 169 direct Operating Income results, all
25 seed annual financial results and 1,428 other financial results. All
non-Operating-Income metric states, execution stages and selected periods match
the prior validated corpus. Pretax and Reported ETR each remain 167 resolved /
37 missing / 0 ambiguous. Compile checks and `git diff --check` pass.
See the [Wave 16 evidence/results record](operating-income-derivation-policy-design.md#wave-16-implementation-and-verified-results).

Phase 1H.4 Wave 17 completes the
[CVX/GE business-perimeter research](operating-income-cvx-ge-perimeter.md)
for exactly ten frozen selected filings (five per issuer). All five CVX periods
are `BUSINESS_PERIMETER_UNRESOLVED`: mixed-tax equity-affiliate earnings and
incomplete Other/benefit allocations do not establish a complete consolidated
operating equation. All five GE periods are research-classified
`SPECIALIZED_METHODOLOGY_REQUIRED` for the mixed industrial/insurance
consolidated perimeter; the selected five-period series is also not comparable
on a common continuing-business basis after HealthCare/Vernova separations and
insurance-accounting changes. Segment profit is not a substitute.

The decision is NO-GO, with zero safe additional coverage. These research
classifications do not change production states or reclassify universe
execution: all ten remain missing, 43 generic issuers execute and seven are
skipped. Operating Income remains 194 resolved / 10 missing / 0 ambiguous;
aggregate states remain 1,880 / 1,508 / 11 / 27 / 42 across 3,468 states.
Only additional selected-filing notes were retrieved; no production code,
tests, policies, full test suite or corpus were changed or run.

Phase 1H.4 Wave 18 completes the
[D&A concept/component inventory](depreciation-amortization-concepts.md)
and its [machine-checkable evidence](depreciation-amortization-inventory.json)
for all 94 missing periods across 21 issuers. Every frozen CIK/accession/annual
period matches selected filing-XBRL and explicit annual DEI evidence. The
inventory retains 1,374 exact-period numeric occurrences, including dimensions,
units, raw representations, deterministic ordinals, presentation/calculation
relationships and selected statement/note sources. AVGO 2021's older DEI
namespace is reviewed separately without changing the production resolver.

Primary research categories reconcile to 31 `CONCEPT_POLICY`, 33 `DERIVATION`,
five `ISSUER_EXTENSION` and 25 `METHODOLOGY_BLOCKER` periods. PARTIAL GO is for
scope-evidence/policy design only: five Visa periods have supported potential
coverage; 89 remain unapproved. Cash-flow impairment/accretion, embedded lease
expense, incomplete amortization, financing/contract costs, source precision
and mixed-business scope prevent a generic fallback or automatic MSFT-style
sum. No production result changes: D&A stays 110 resolved / 94 missing / 0
ambiguous, Operating Income 194 / 10 / 0 and aggregate 1,880 / 1,508 / 11 / 27 /
42 across 3,468 states. No tests or corpus runs were performed.

Phase 1H.4 Wave 19 completes the
[D&A scope-evidence acceptance design](depreciation-amortization-scope-evidence-design.md).
PARTIAL GO approves a five-entry exact-accession Visa design, not a generic
combined-concept rule or production registration. Asset/finite-lived notes,
separate incentive/lease treatment and operating presentation establish scope;
2025's rounded property disclosure is corroboration, never a residual operand.
All 89 controls remain unapproved, not freshly reviewed denials. Immutable
versioning, direct precedence, exact semantic confirmation, structural-error
boundaries and complete occurrence/support serialization are specified.
Production counts remain unchanged; no tests or corpus reruns.

Phase 1H.4 Wave 20 implements the
[five-entry curated D&A scope policy](depreciation-amortization-scope-evidence-design.md#wave-20-implementation-and-verified-results).
Focused tests pass 200 checks; the complete suite passes 552 tests. All five
selected Visa accessions resolve with two confirming occurrences each, exact
reviewed artifact verification and separately typed asset-note support in
schema 4. The full 94-period regression preserves all 89 no-entry controls.
One corpus reconciliation confirms 43/43 generic completions, seven skips and
204 periods: D&A is now **115 resolved / 89 missing / 0 ambiguous**. Aggregate
states are **1,885 resolved / 1,503 missing / 11 ambiguous /
27 methodology-blocked / 42 not-comparable**, totaling **3,468**. Exactly five
D&A missing-to-resolved changes occur; all other metrics and execution states
are unchanged. The research inventory and generic/MSFT policies are unchanged.
No generic fallback, residual or lease adjustment is introduced.

Phase 1H.4 Wave 21 completes the
[D&A component-completeness design](depreciation-amortization-component-derivation-design.md)
and its [33-period matrix](depreciation-amortization-component-derivation-matrix.json).
All exact Wave 18 derivation identities reconcile: six issuers with five
periods, GEV two and PM one. Decision: **NO-GO for derivation implementation**;
**0 approved / 19 further research / 14 methodology-blocked** research outcomes.
Documented software containment, rounded observations, manufacturing/grant
scope, embedded leases and GEV's 2024 impairment prevent a safe equation.
Only 23 specific selected-filing lease-note gaps were retrieved; committed
statement/asset evidence was reused. No production policy, code, tests,
inventory or corpus changes; no tests/corpus rerun. The five Visa approvals,
all 89 missing controls and the Wave 20 counts above remain unchanged.
AMD's five extension periods remain outside this pass. Safe new coverage is zero.

## Completed

- Completed Milestone 0 — development environment and repository setup
- Created GitHub repository
- Cloned repository locally
- Connected local repository to GitHub remote
- Configured Git identity
- Set up Python 3.12 virtual environment
- Configured VS Code to use the project virtual environment
- Created initial repository structure
- Created initial project documentation
- Added a reusable SEC JSON HTTP client with identifying User-Agent support
- Added exact ticker → SEC company identity resolution using the official SEC
  `company_tickers.json` dataset
- Added deterministic unit tests for SEC transport and ticker resolution
- Added typed recent-filing metadata retrieval from the official SEC
  Submissions API
- Added explicit validation for SEC parallel-array structure, required fields,
  and filing dates
- Added deterministic unit tests for submissions retrieval and parsing
- Added typed metadata for supplemental SEC submissions history files
- Added explicit, on-demand retrieval and shared parsing for individual
  supplemental history files
- Added deterministic unit tests for supplemental metadata and retrieval
- Added a pure, deterministic selector for exact 10-K annual periods and exact
  10-Q filings after the latest selected annual period
- Added incremental history orchestration that stops retrieving supplemental
  files as soon as the requested annual coverage is available
- Added explicit ambiguity handling for duplicate reporting periods
- Added deterministic unit tests for selection and orchestration
- Added complete Company Facts retrieval through the existing SEC client
- Added immutable models for concepts and unit-tagged fact observations
- Added explicit Company Facts validation while preserving optional context,
  observation ordering, and repeated comparative facts
- Added deterministic unit tests for Company Facts parsing and errors
- Added a development-only cross-company Company Facts validation harness that
  uses the production SEC APIs sequentially, reports per-stage failures without
  stopping the run, and defaults to a repeatable 20-company corpus
- Validated Company Facts across all 20 corpus companies: 11,181 concepts and
  528,990 observations parsed with no failures
- Added narrowly validated canonical decimal-string CIK support after XOM
  exposed that live SEC representation, with mismatch regression coverage
- Added pure Company Facts observation selection anchored to selected filing
  accessions, preserving annual/interim grouping and deterministic ordering
- Added structural current, comparative, and after-report-date relationships,
  plus instant/duration classification without YTD or discrete-quarter inference
- Added explicit exact-observation ambiguity handling while preserving
  same-end/different-start periods, multiple units, and legitimate absence
- Added compact selection output that retains only matched observations and
  Company Facts source metadata rather than the full parsed observation graph
- Added deterministic tests for calendar, non-calendar, 52/53-week, and interim
  period shapes, ambiguity, absence, provenance, ordering, and ownership
- Added a pure top-level normalization package with stable metric identities
  and ordered, metric-specific SEC concept policies
- Added immutable annual normalized, missing, and ambiguous result models with
  compact SEC provenance and no retained Company Facts graph
- Added annual Revenue normalization using an evidence-based
  `RevenueFromContractWithCustomerExcludingAssessedTax` → `Revenues` policy
- Added annual Operating Income normalization using `OperatingIncomeLoss`
- Preserved actual calendar, non-calendar, 52-week, and 53-week economic period
  dates without inferring fiscal boundaries
- Validated five annual periods each for META, GOOGL, MSFT, AAPL, and COST: all
  50 Revenue/Operating Income values resolved, with no ambiguity or face-
  statement mismatch
- Confirmed GOOGL Revenue fallback behavior and retained equal COST Revenue
  observations as confirming provenance
- Added direct annual Capex normalization using only
  `PaymentsToAcquirePropertyPlantAndEquipment`, preserving positive expenditure
  magnitudes and actual fiscal boundaries
- Validated 25 annual Capex periods across META, GOOGL, MSFT, AAPL, and COST
  alongside the existing 50 Revenue and Operating Income values
- Confirmed that direct DDA covers META, AAPL, and COST but not GOOGL or MSFT;
  a fallback is inappropriate, aggregation requires complete non-overlapping
  evidence, and some relevant issuer-extension facts are absent from Company
  Facts
- Added explicit on-demand discovery and retrieval of the SEC-generated
  extracted XBRL instance corresponding to a selected filing's primary document
- Added immutable filing-level context, dimension, unit, and fact models that
  preserve standard and issuer-extension concepts without financial selection
- Added structural parsing for duration, instant, comparative, explicit- and
  typed-dimensional contexts, simple and divided units, numeric, nil, and
  nonnumeric facts
- Kept filing-level XBRL separate from Company Facts selection and historical
  normalization; Revenue, Operating Income, and Capex behavior is unchanged
- Live-validated exact nondimensional issuer-extension facts from the selected
  GOOGL 2021 and MSFT 2022 extracted instances, including dates, USD units, and
  decimals
- Established an FCFF D&A definition that excludes impairment, stock
  compensation, restructuring, unspecified other noncash items, and unsupported
  lease adjustments from direct D&A
- Added direct annual D&A normalization using only
  `DepreciationDepletionAndAmortization` through the generic annual resolver
- Validated direct D&A for all five selected META, AAPL, and COST periods:
  15/25 direct coverage across the five-company corpus, with GOOGL and MSFT
  returning typed missing results as intended
- Added provenance-distinct derived historical values with ordered operands,
  source identity, and an explicit addition operation
- Added a Company Facts derivation policy scoped to Microsoft CIK `789019` for
  `Depreciation` plus `AmortizationOfIntangibleAssets`
- Preserved direct-first precedence and direct ambiguity while keeping derived
  coverage gaps typed rather than exceptional
- Validated all five selected MSFT periods as derived D&A, producing 20/25
  evidence-backed D&A periods across META, GOOGL, MSFT, AAPL, and COST; GOOGL
  remains unresolved
- Added direct annual Pretax Income normalization using only
  `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`
- Added direct annual Income Tax Expense normalization using only
  `IncomeTaxExpenseBenefit`, preserving reported expense and benefit signs
- Ordered normalized metrics as Revenue, Operating Income, Pretax Income,
  Income Tax Expense, D&A, and Capex
- Validated both tax-related metrics across five selected annual periods for
  META, GOOGL, MSFT, AAPL, and COST: 25/25 resolved for each, with no missing or
  ambiguous results and exact selected-filing face-statement agreement
- Added derived annual Reported Effective Tax Rate from the direct normalized
  Income Tax Expense and Pretax Income results
- Added 34-digit `Decimal` division, ordered normalized-metric provenance,
  explicit negative-denominator diagnostics, and typed zero-denominator results
- Preserved negative and above-100% rates without clamping and applied no
  arbitrary near-zero threshold
- Validated Reported ETR for all 25 selected periods with agreement to SEC's
  structured disclosed rate after normal presentation rounding
- Added a separate annual instant balance-sheet normalization path with typed
  resolved, missing, and ambiguous results and compact Company Facts provenance
- Added primitive policies for Operating Receivables, Inventory, Trade Accounts
  Payable, and Customer Contract Liabilities, including only the evidence-backed
  CIK-scoped COST and META alternatives
- Validated 25 selected annual periods across META, GOOGL, MSFT, AAPL, and COST:
  Operating Receivables 25/25, Inventory 17/25, Trade Accounts Payable 25/25,
  and Customer Contract Liabilities 24/25, with nine explicit missing results
  and no ambiguity
- Preserved META inventory as missing in all five periods, GOOGL inventory as
  missing for 2023-2025, and META 2025 customer liabilities as missing rather
  than substituting unsupported concepts or zero
- Added Apple CIK-scoped Vendor Non-Trade Receivables from
  `NontradeReceivablesCurrent` and validated 5/25 overall: all 5/5 applicable
  Apple periods resolved and 20 non-applicable periods remained typed missing
- Added `EmployeeRelatedLiabilitiesCurrent` only for META, GOOGL, MSFT, and
  COST, validating 20/25 overall: all 20/20 applicable periods resolved and all
  five Apple periods remained typed missing
- Added Costco CIK-scoped Member Rewards Liability from
  `AccruedLiabilitiesCurrent` and validated 5/25 overall: all 5/5 applicable
  Costco periods resolved and 20 non-applicable periods remained typed missing,
  without generalizing that broad concept to other issuers
- No new primitive result was ambiguous
- At the primitive-normalization milestone, kept filing-level XBRL explicit/on
  demand and deferred broad current residuals, Operating NWC, and its change
- Added an explicit Company Facts versus filing-XBRL source distinction to
  annual balance-sheet policies while keeping normalization network-free
- Added GOOGL CIK `1652044` Accrued Revenue-Share Liability from exact
  `AccruedRevenueShare` filing-XBRL facts under the Google issuer namespace whose
  date exactly matches the selected 10-K report date
- Preserved filing-level namespace, source URL, context, dimensions, decimals,
  nil state, raw value, parsed value, accession, and filing metadata in compact
  normalized provenance; multiple eligible facts remain ambiguous
- Live-validated all five selected GOOGL accessions at $8.996bn, $8.370bn,
  $8.876bn, $9.802bn, and $10.864bn for 2021–2025, with no missing or ambiguous
  results
- Added GOOGL CIK `1652044` Accrued Customer Liabilities from exact
  `AccruedCustomerLiabilitiesCurrent` selected-filing XBRL facts, distinct from
  customer contract liabilities and accrued revenue share
- Live-validated all five original selected GOOGL accessions at $3.505bn,
  $3.619bn, $4.140bn, $4.304bn, and $5.029bn for 2021–2025, with no missing or
  ambiguous results
- Made accrued customer liabilities a required GOOGL operating-liability
  component while preserving unresolved trade-payables and residual-liability
  blockers, so GOOGL remains incomplete
- Added a pure META CIK `1326801` derivation that subtracts PP&E included in
  trade accounts payable using reported trade AP, combined unpaid PP&E, and
  separately accrued PP&E evidence
- Preserved duration-shaped `CapitalExpendituresIncurredButNotYetPaid` Company
  Facts observations as special selected-accession/full-fiscal-year derivation
  operands rather than direct instant balance-sheet values; eligibility is
  evaluated only among target-concept observations, with multiple eligible
  target periods unresolved and unrelated duration facts ignored
- Used explicit filing XBRL for report-date-specific Facebook namespace
  `PropertyAndEquipmentAccruedLiabilitiesCurrent`; normalization performs no
  retrieval
- Live-validated adjusted META trade AP for 2021–2025 at $2.071bn, $4.592bn,
  $2.957bn, $3.142bn, and $3.965bn, with all five periods resolved and complete
  three-fact/two-step provenance
- Made derived adjusted trade AP the required META operating-liability evidence
  without counting either PP&E operand separately; other accrued liabilities
  remain unresolved, so META remains incomplete
- Kept Apple accrued distribution and marketing unresolved at 1/5 exact
  selected-accession coverage and excluded broad residual liability captions
- Added immutable Operating NWC component classifications distinct from
  normalized financial metric identities
- Added CIK-specific META, GOOGL, MSFT, AAPL, and COST policies for required
  operating assets and liabilities, exclusions, non-applicable components, and
  methodology-unresolved balances
- Added pure annual completeness evaluation that preserves resolved, missing,
  and ambiguous normalized evidence without calculating an Operating NWC value
- Preserved explicit SEC zero as resolved while keeping missing evidence,
  issuer non-applicability, and methodology uncertainty as distinct states
- Explicitly deferred and excluded operating-lease current liabilities under
  the initial methodology; no lease arithmetic or capitalization was added
- Confirmed all five issuer policies remain incomplete because material
  component-classification or evidence blockers remain
- Preserved strict reconstruction completeness as an audit diagnostic without
  weakening its missing, ambiguous, unresolved, excluded, or not-applicable
  classifications
- Added immutable versioned issuer-specific valuation perimeters and a separate
  pure readiness evaluator that preserves direct, derived, missing, and
  ambiguous evidence without calculating Operating NWC
- Made COST ready for all five selected annual periods and META ready for
  2021–2024; META 2025 remains not ready because required customer contract
  liabilities are typed missing
- Kept GOOGL not ready for its trade-AP and inventory methodology decisions,
  MSFT not ready for trade AP, and AAPL not ready for employee and distribution-
  and-marketing liability decisions
- Kept broad mixed residual captions visible as reconstruction limitations but
  outside the initial valuation perimeters; omitted balances and movements are
  not treated as zero and will remain absent from future arithmetic
- Defined perimeter version changes around economic component or mandatory-
  treatment changes rather than incidental code changes
- Confirmed the selected META 2025 filing reports $1.080bn of total deferred
  revenue but does not quantify an exact current-only amount; neither the total
  balance nor qualitative timing disclosure is used as a substitute
- Added META valuation policy v2 with operating receivables, adjusted trade AP,
  and employee-related liabilities as required components
- Kept customer contract liabilities normalized and visible but outside the
  META v2 valuation perimeter for every period; excluded balances and movements
  are omitted rather than treated as zero or economically irrelevant
- Made META v2 the sole active default while retaining META v1 through explicit
  policy ID/version lookup and rejecting duplicate historical identities
- Confirmed META v2 removes customer contract liabilities as a readiness blocker
  while strict reconstruction remains incomplete; every remaining required
  normalized component must still resolve for a period to calculate
- Preserved COST v1 readiness and the existing GOOGL, MSFT, and AAPL blockers
- Added pure annual Operating NWC level calculation as required operating assets
  minus required operating liabilities for valuation-ready periods only
- Added ordered `Decimal` component contributions that preserve positive source
  balances, apply asset/liability signs separately, and retain complete direct
  or derived normalized provenance
- Kept missing, ambiguous, and methodology-blocked periods nonnumeric; no
  partial result or zero substitution is produced
- Corrected META's special combined unpaid-PP&E eligibility to consider only
  observations of the configured target concept; unrelated duration facts no
  longer create false period ambiguity, while competing target facts remain
  deterministically ambiguous
- Live-validated META v2 and COST v1 levels for all five selected periods, with
  exact agreement between every result and its signed component contributions;
  META 2021–2025 is $8.816bn, $4.283bn, $6.553bn, $7.502bn, and $8.653bn
- Kept GOOGL, MSFT, and AAPL blocked
- Preserved exact policy ID/version selection and kept out-of-perimeter evidence
  outside arithmetic without treating it as economically zero
- Added immutable annual ΔNWC results calculated as closing O-NWC minus opening
  O-NWC using exact `Decimal` arithmetic without rounding
- Required the same company CIK, exact policy ID/version, calculation formula,
  and actual ordered component/side/normalized-metric perimeter so explicit
  policy-definition changes cannot become economic working-capital movements
- Preserved actual opening and closing fiscal dates and both complete calculated
  O-NWC levels with their component-level SEC provenance
- Added ordered adjacent-series calculation: five compatible annual levels
  produce four changes, while reversed dates or an intervening policy change
  fail explicitly rather than being sorted or skipped
- Live-validated META v2 annual ΔNWC at -$4.533bn, $2.270bn, $0.949bn, and
  $1.151bn and COST v1 at $1.897bn, -$1.146bn, -$0.471bn, and -$1.417bn for
  their four respective 2022–2025 fiscal periods
- Added immutable caller-driven tax reconciliation evidence and bridge models
  that preserve explicit filing-displayed signs separately from raw XBRL values
- Supported both percentage-point rate bridges and reported dollar bridges,
  exact Decimal rate dollarization, disclosed-precision validation, row order,
  and typed evidence problems without synthetic residual rows
- Kept diagnostic income-base, pairing, and proposed-treatment classifications
  separate from operating-tax policy; operating tax, NOPAT, and forecast tax
  assumptions remain unimplemented
- Added immutable operating-tax readiness policies, guarded bridge-row
  decisions, explicit evidence requirements, and exclusive paired-row
  membership without a generalized rule engine
- Added company, selected-filing, accession, report-date, economic-period,
  monetary-scale, statutory-anchor, and exact policy-version integrity checks
- Added typed ready, missing, ambiguous, unsupported, policy-mismatch,
  unreconciled, methodology-blocked, and loss-policy-blocked outcomes
- Proved readiness with a fully evidenced synthetic case. Completed methodology
  review leaves all 25 real validation periods blocked by unresolved
  foreign/state allocation, combined or embedded SBC, Other-row, and
  operating-income linkage decisions. Representative blocker regressions are
  automated; the repository does not persist and replay all 25 full bridges.
- Conservatively blocked zero/negative Operating Income, negative Pretax Income,
  and unresolved benefit realizability; explicit zero adjustments remain valid
- Completed the 25-period first-ready screening and jurisdictional-attribution
  methodology review without introducing a materiality waiver or forcing a real
  issuer period ready
- Adopted strict direct linkage for historical operating tax: complete state,
  foreign, jurisdictional, and other reconciliation effects require explicit
  reported-Operating-Income linkage or an exact reproducible operating
  allocation; paired gross-tax and credit effects also require complete common-
  base evidence
- Rejected caption recurrence, state/foreign labels, net presentation, absence
  of disclosed contamination, proportional Operating Income/Pretax Income
  allocation, unsupported geographic or revenue allocation, and direct
  application of reconciliation percentages to Operating Income
- Made historical operating tax and historical NOPAT optional analytical
  outputs while preserving reported tax expense, Reported ETR, signed bridge
  evidence, and typed readiness; a manual forecast tax-rate assumption keeps
  unresolved historical tax outside the DCF critical path
- Added annual Cash and Cash Equivalents from exact selected-filing
  `CashAndCashEquivalentsAtCarryingValue` observations for the five validation
  issuers
- Added CIK-scoped annual Short-Term Investments policies for META, GOOGL,
  MSFT, AAPL, and COST, including the narrow META 2021 available-for-sale debt
  fallback
- Added Apple-only annual Long-Term Marketable Securities without treating
  other issuers' strategic, non-marketable, or mixed investment captions as
  equivalents
- Preserved gross reported balances without subtracting restrictions or
  deriving unrestricted, excess, or total liquid cash
- Validated 25/25 cash values, 25/25 short-term investment values, and 5/5
  applicable Apple long-term marketable-security values with no missing or
  ambiguous results
- Added annual Commercial Paper using `CommercialPaper` for GOOGL, MSFT, and
  AAPL, with 12 direct, 13 missing, and no ambiguous values across 25 periods
- Added COST-only annual Short-Term Borrowings using
  `OtherShortTermBorrowings`, resolving the evidenced 2022 balance while the
  other 24 periods remain typed missing rather than inferred zero
- Added direct annual Current Portion of Long-Term Debt using
  `LongTermDebtCurrent` and Non-Current Long-Term Debt using
  `LongTermDebtNoncurrent`
- Added accession-scoped GOOGL 2021–2023 carrying-debt derivations that remove
  finance-lease liabilities from combined debt-and-lease facts and retain all
  Company Facts operands and arithmetic steps
- Validated Current Portion of Long-Term Debt as 19 direct, 1 derived, and 5
  missing; validated Non-Current Long-Term Debt as 21 direct, 3 derived, and 1
  missing, with no ambiguity or value mismatch across the 25-period corpus
- Kept commercial paper and short-term borrowings separate and prohibited
  total debt, net debt, lease debt, maturity-principal, and fair-value
  substitutions
- Added annual Diluted Weighted-Average Shares from only
  `WeightedAverageNumberOfDilutedSharesOutstanding`, requiring the selected
  10-K's current duration, unit `shares`, integer non-Boolean input, and exact
  `Decimal` output
- Added a GOOGL CIK- and accession-scoped filing-XBRL derivation for selected
  2021–2023 filings that adds the Class A denominator, which includes Class B
  conversion, to the separate Class C denominator while retaining full
  dimensional provenance
- Validated 22 direct and three derived diluted-share periods with no missing,
  ambiguity, or value mismatch; preserved GOOGL 2021 at 677,674,000 on the
  original pre-split filing basis
- Kept basic shares, period-end shares, split-restated series, current fully
  diluted shares, forecast dilution, and future valuation-share policy outside
  this milestone
- Added an immutable period-centric standardized company history with selected
  filing references, actual fiscal durations, closing balance dates, and
  deterministic top-level measure ordering
- Added pure assembly and explicit serialization that preserve direct, derived,
  calculated, missing, ambiguous, not-comparable, and methodology-blocked
  outcomes; exact Decimal values serialize as strings
- Aligned duration and instant results by company, accession, filing identity,
  and report date, rejecting conflicting fiscal starts, duplicate periods,
  unit mismatches, binary floats, and later-filing evidence
- Exposed existing Operating NWC levels and changes without repeating their
  arithmetic, retaining policy ID/version and component-level SEC references
- Live-assembled five annual records for META, GOOGL, MSFT, AAPL, and COST;
  standardized values matched their immediate normalized inputs while
  preserving GOOGL blockers and derived shares, MSFT June periods, Apple
  long-term securities, and COST's 53-week year
- Kept cash, investment, and debt primitives separate and left historical
  NOPAT, forecast assumptions, FCFF, equity bridges, valuation shares, and DCF
  outside the standardized historical boundary
- Added a separate `valuation` package with immutable five-year manual
  assumption models bound to company CIK, latest historical accession, and
  fiscal-end date without retaining normalization or SEC objects
- Required ordered forecast indices 1–5 and descriptive labels without
  synthesizing future dates or assuming calendar fiscal years
- Added strict finite-Decimal fraction validation for per-year revenue growth,
  operating margin, forecast tax rate, D&A/revenue, Capex/revenue, and
  ΔNWC/revenue, plus one manual WACC and terminal-growth rate
- Chose direct ΔNWC as a percentage of revenue so unresolved historical O-NWC
  does not block manual forward assumptions; no forecast O-NWC level is added
- Added deterministic explicit serialization with Decimal strings and preserved
  the boundary around manual forecast tax, unresolved loss-period tax policy,
  valuation shares, and the enterprise-to-equity bridge
- Kept all forecast calculations, NOPAT, FCFF, discounting, terminal value, DCF,
  scenarios, sensitivity analysis, and reverse DCF unimplemented
- Froze the dated and sourced 2026-10-02 S&P 500 Top 50 universe as 51
  securities representing 50 SEC issuers, preserving both Alphabet share
  classes and the explicit Invesco `BRK/B` to SEC/project `BRK-B` ticker mapping
- Reconciled all five validated issuers to the snapshot and live-prechecked all
  51 canonical project tickers through the existing SEC resolver with no
  unresolved tickers
- Classified 38 securities as operating-company candidates and seven issuers
  as specialized-methodology candidates without assigning
  `GENERALIZATION_REQUIRED` before pipeline evidence exists
- Added a deterministic development corpus runner that validates and consumes
  the frozen snapshot, groups its 51 securities into 50 CIK-based issuer
  records, uses GOOGL as Alphabet's single execution ticker, and retains GOOG
  as a separate reporting row
- Added explicit ticker-resolution, submissions, filing-selection, Company
  Facts, filing-association, normalization, standardized-output, complete, and
  specialized-skip stages with issuer-boundary exception capture
- Added an ephemeral JSON result containing snapshot and commit identity,
  selected annual dates, per-stage status, typed availability counts, and
  per-measure direct/derived/calculated summaries
- Live-attempted all 43 generic issuers: 41 reached standardized output, GEV
  and SNDK failed at Company Facts parsing, and all seven specialized issuers
  were preserved as explicit skips
- Recorded 1,636 resolved, 1,673 missing, 24 ambiguous, 27
  methodology-blocked, 40 not-comparable, and no unsupported, not-applicable,
  or out-of-perimeter standardized measures across completed issuers
- Preserved all five seed regressions and their 25 annual periods, including
  GOOGL missing D&A, three derived GOOGL diluted-share periods,
  GOOGL/MSFT/AAPL blocked O-NWC, and each seed's first non-comparable ΔNWC
- Recorded XOM as completing the pipeline with zero selected annual periods;
  no later comparative filing, zero, alias, or policy change was introduced
- Classified all Phase 1H.2 results into an operational root-cause taxonomy,
  reconciled the 17-measure coverage matrix, and preserved the complete
  ambiguity and methodology-blocker inventories
- Established that GEV and SNDK share a strict Company Facts representation
  issue, while XOM requires official-evidence registrant-succession handling
  rather than a filing-selector relaxation or ticker hardcode
- Assigned all 50 issuers a post-smoke planning status: two `SUPPORTED`, 41
  `GENERALIZATION_REQUIRED`, and seven
  `SPECIALIZED_METHODOLOGY_REQUIRED`
- Generalized Company Facts CIK parsing to accept the exact SEC ten-digit
  padded representation only when it matches `company.cik_padded`, with no
  GEV/SNDK-specific branch and with canonical/mismatch protections preserved
- Live-reran GEV and SNDK through complete standardized output with two annual
  periods each, then completed all 43 generic corpus attempts with no failures;
  the five seed histories and typed states remained unchanged
- Completed the registrant-succession identity-linkage design with exact
  terminology, official SEC evidence hierarchy, deterministic acceptance and
  rejection gates, bounded chain semantics, provenance, Company Facts and
  filing-selection interactions, and adversarial cases
- Recorded a NO-GO decision for automated linkage because public structured SEC
  sources do not encode the directed predecessor/successor CIK edge; retained
  XOM as unresolved rather than adding a ticker, name, or issuer hardcode
- Generalized the exact standard cash Company Facts policy beyond the seed CIKs,
  resolving 160 additional issuer-periods without accepting broader
  restricted-cash or combined cash-and-investment captions

## Next Step

Current next step: **user review of the consolidated restricted reported-input
delivery contract and finite backlog** in
[the blocker review](phase1-blocker-disposition-review.md). Do not implement until
reviewed. Recommended bounded follow-up, if accepted: four-period retained-input
delivery index/check for existing AAPL/MSFT/Alphabet packages, with signed
movement references and explicit unknowns, no new schema/framework or financial
calculation. Qualified facts/gaps closure stands; five-year target/history
exceptions, original metric blockers and future sufficiency gates persist.
Phase 2 remains postponed; do not automatically extend the four pilot periods.

Historical next-step wording below is superseded by later completed milestones,
qualified closure and the current review, not authority for new work.
Previously proposed next step: **review and publish explicit MSFT FY2025–2026 partial
scenario input bundles**, using the [implemented isolated evaluator](analyst-operating-nwc-design.md#implemented-isolated-foundation).
Classify omissions and retain provenance; no default/earlier-period estimates,
cash ΔNWC approval or forecast consumption. Phase 2 remains postponed; this
additive layer cannot overwrite frozen facts or remove blockers.
The eventual financial timing-readiness boundary remains required under the
[existing design](financial-timing-readiness-design.md), not implemented here.
The [historical v1 freeze](historical-normalization-v1-freeze.md) completes Phase
1H with qualified scope. Keep historical resolution independent from readiness;
no integrated FCFF certification, new economic adjustments or FCFF calculator.
The gate precedes forecast consumption of historical ratios and FCFF use;
independent forecast-anchor, consumer-convention and tax/Capex checks remain.
The [Wave 46 exit plan](phase-1h-generalization-exit-plan.md) was executed by
this validation pass, not an unfulfilled coverage mandate. The chronological
Wave 22–45 notes below preserve historical research routing, not pending tasks.
Reopen exhausted issuer work only on its specified new evidence. No additional
coverage implementation is required before validation.

Wave 22 completes [targeted TXN 2021–2023 evidence research](depreciation-amortization-component-derivation-design.md#wave-22--targeted-txn-completeness-follow-up).
Reported software/PP&E asset separation, signs and explicit zero operands are
confirmed, but all three remain further research: no exhaustive current-expense
versus inventory/preproduction bridge, and no explicit 2023 incentive netting
bridge. Safe new coverage is zero; the 33-period matrix remains 0 approved /
19 further research / 14 methodology-blocked. Production remains D&A 115/89/0
and aggregate 1,885/1,503/11/27/42 = 3,468; no tests or corpus rerun.

Wave 23 completes the [TXN methodology review](depreciation-amortization-component-derivation-design.md#wave-23--txn-methodology-review).
For new derivation approvals the target is qualifying recurring expense in
consolidated continuing operating income, net of demonstrated expense
reductions; this clarifies an incomplete timing specification, not runtime
policy equivalence. Expense D&A plus unadjusted book inventory changes is not
automatically cash-consistent. Missing allocation/incentive bridges keep all
three TXN periods further research; no equation or coverage is approved.
Existing policies and counts are preserved, not retrospectively certified.

Wave 24 completes the [approved D&A timing-basis/consumer audit](depreciation-amortization-timing-audit.md).
All three D&A families, five curated Visa identities, five active/six addressable
NWC valuation policies and five reconstruction policies reconcile. Visa's
expense basis is supported; generic/MSFT timing and all joint future FCFF
bridges remain insufficiently evidenced. No approved numeric incompatibility
is established. Book NWC/readiness has no D&A/EBIT timing linkage; no FCFF
calculator exists. Approvals, corpus counts and source code remain unchanged.

Wave 25 completes the [financial timing-evidence/readiness contract design](financial-timing-readiness-design.md).
It preserves resolved historical values independently from consumer unknowns;
Visa's five expense-basis entries and generic/MSFT insufficient-evidence mapping
are unchanged. Integrated FCFF compatibility remains unproved. The proposed
gate distinguishes absent evidence, proved incompatibility, ambiguous evidence
and unavailable inputs; no economic adjustment, schema or evaluator is approved
for implementation during Phase 1H. Freeze scope must document the limitations;
executable joint readiness belongs at the valuation boundary after 1H.6.

Wave 26 completes the [selected-filing Capex inventory](capex-concepts.md) and
[57-period evidence matrix](capex-inventory.json): 13 issuers, 37 concept-policy /
17 component-derivation / three methodology-gated periods. Ten AMZN/LLY reported
gross cash PP&E candidates support exact-period scope design; 47 remain
unapproved, with no component equation or generic fallback approved.
Wave 27 completes the [Capex scope-evidence acceptance design](capex-scope-evidence-design.md)
and [57-row matrix](capex-scope-evidence-matrix.json): PARTIAL GO, five AMZN /
five LLY exact-accession acceptances and 47 unapproved controls, not fresh
economic denials. Immutable reviewed-byte evidence, exact operand identity,
direct precedence, semantic duplicate/conflict rules and full provenance are
specified; no generic fallback or incentive gross-up is approved.
Wave 28 completes the [ten-entry curated Capex policy](capex-scope-evidence-results.md),
including independently verified LLY response/retained-JSON fingerprints and
an explicitly authorized 15-artifact AMZN refresh preserving old unverified
fingerprints. No acceptance relaxation. Focused tests: 160; complete suite: 569;
ten positive / 47 control regression and ten-accession targeted validation pass.
One corpus reconciliation yields Capex 157/47/0, D&A 115/89/0 and aggregate
1,895/1,493/11/27/42 = 3,468. Other measure states, 43 generic completions and
seven specialized skips are unchanged; schema 5 retains the Capex audit.
Wave 29 completes the [five-period CVX Capex acquisition/perimeter review](capex-cvx-acquisition-perimeter.md)
and [exact evidence supplement](capex-cvx-perimeter-inventory.json). Separate
business-combination cash/stock consideration, noncash acquired PP&E,
investment/dry-hole components and proceeds are identified. All five remain
scope-research gaps: capitalized construction/development/mineral and lease
inputs require an explicit decision against the existing primitive. NO-GO for
acceptance or derivation; zero safe additional coverage, not proved economic
incompatibility. The frozen inventory, acceptance matrix and policies remain
unchanged. Thirty-six retained original report bodies and five instance hashes
were verified; no SEC retrieval, tests or corpus rerun. Production remains
Capex 157/47/0 and aggregate 1,895/1,493/11/27/42 = 3,468.
Wave 30 completes that [bounded CVX methodology review](capex-cvx-acquisition-perimeter.md).
Cash development/construction and proved mineral-property costs within the
selected recognized PP&E perimeter are eligible; capitalized cash lease/service
inputs do not require a hypothetical materials-only adjustment. Noncash ROU/ARO,
financing principal, expensed exploration/dry holes and separate acquisitions
remain excluded. R12 independently establishes the complete reported PP&E cash
component: PARTIAL GO for five exact-accession reported-value scope designs,
zero component equations or production approvals. The separate lease/mineral
allocation is unproved and exhausted in the retained evidence, so no adjusted
equation is approved or broad research repeated. The primitive is clarified,
not expanded; existing policies, counts and the 36-body evidence are unchanged.
The updated supplement preserves Wave 29's decision and immutable digest.
Wave 31 completes the [five-entry CVX scope acceptance design](capex-cvx-scope-evidence-design.md)
and [machine-checkable matrix](capex-cvx-scope-evidence-matrix.json). PARTIAL GO:
five exact reported-value designs, ten unchanged published AMZN/LLY approvals,
42 unapproved controls, 147 existing direct results preserved. Proposed v2 is
a disjoint immutable five-entry set alongside v1, with exact published-catalog
dispatch; no v1 relabeling or evidence mutation. Typed mandatory raw-body
evidence, selected-instance re-parsing, conservative occurrence/conflict and
direct-precedence rules, complete schema-5 provenance and regression gates are
specified. No generic fallback or mineral/lease equation. Production remains
Capex 157/47/0 and aggregate 1,895/1,493/11/27/42 = 3,468; no tests or corpus run.
Wave 32 completes that five-entry extension and published catalog with
[verified results](capex-cvx-scope-evidence-results.md). V1 identity/evidence and
all 147 direct results are preserved. Exactly five CVX missing states resolve;
Capex is 162/42/0 and aggregate is 1,900/1,488/11/27/42 = 3,468. The 42 controls,
other measures, completion and skips remain unchanged. Next research only the
five NVDA combined-asset cash-component gaps; keep other gaps and readiness
outside that bounded pass.
Do not implement a sum or infer TXN allocations; further TXN work
requires a genuine new expense/inventory and incentive bridge, not repeated
concept research. TXN 2024–2025 absent intangible operands are not
zero. Preserve Wave 20's five Visa entries and all 89 unapproved controls;
no generic sum, cash-flow fallback or isolated lease adjustment. The 14
methodology-gated proposals, remaining research periods and five AMD extension
periods remain separate; do not generalize MSFT's two operands.
Wave 17 leaves the ten CVX/GE Operating Income gaps unresolved; dedicated CVX
energy/affiliate and GE industrial/insurance carve-out or common-perimeter
recast research are separate, unapproved methodology paths. Preserve the
completed 25-entry Operating Income policy and all typed missing controls. The
Phase 2A assumptions model is implemented, but
forecast, FCFF, DCF, equity-bridge, per-share, reverse-DCF, scenario, and
sensitivity work is intentionally paused through Phase 1H.

## Phase 1H Roadmap

1. **Phase 1H.1 — Universe definition (complete):** froze the dated and sourced
   2026-10-02 S&P 500 Top 50 list, existing coverage, and preliminary
   specialized-methodology flags.
2. **Phase 1H.2 — Automated corpus smoke test (complete):** ran the existing
   historical pipeline across all 43 generic issuers and preserved structured
   typed results, stage failures, and seven specialized skips.
3. **Phase 1H.3 — Failure taxonomy (complete):** classified retrieval,
   identity, filing-selection, schema, concept-policy, issuer-extension,
   dimensional, derivation, period-association, methodology, and specialized
   business-model issues and ranked the reusable backlog.
4. **Phase 1H.4 — Generalization waves (in progress):** Wave 1A fixed exact
   padded Company Facts CIK handling. Wave 1B completed the
   registrant-succession design and reached NO-GO for automated linkage, leaving
   XOM unresolved. Wave 2 generalized the exact standard cash policy, resolving
   160 additional periods while leaving 19 broader-caption cases missing. Wave
   3 rejected annual-looking heuristic evidence. Wave 4 found a standards-backed
   authority in the filing-XBRL DEI required context and documented a GO design.
   Wave 5 implemented and validated the pure resolver. Wave 6 integrates it for
   Revenue, Pretax Income, and Income Tax Expense, resolving all known annual/Q4
   collisions while retaining 11 same-period economic Revenue conflicts. Wave
   7 reaches PARTIAL GO for further research/design only: a 33-period standard
   Pretax variant remains unapproved because its equity-method scope differs.
   Wave 8 defines a read-only presentation-evidence diagnostic without changing
   production policy. Wave 9 implements it and validates all 33 periods as
   multiple-role members with statement membership established but equity-
   method scope still unapproved. Wave 10 completes exact-period note research:
   eight periods are included in Pretax, 20 are separate net of tax, and five have
   mixed treatment and remain unresolved. No machine-checkable equivalence rule
   or production resolution is established. Wave 11 rejects an automated rule
   but approves the design boundary for a curated, versioned exact-accession
   registry with mandatory provenance and conservative defaults. Wave 12
   implements that boundary for only the eight reviewed MA/CVX facts, preserves
   all confirming occurrences through Reported ETR and serialization, and
   leaves all 25 controls and 12 issuer-extension periods unresolved. Wave 13
   finds no consolidated face-statement Operating Income subtotal in any of 35
   missing periods and rejects direct policy expansion; two GE periods contain
   only dimensioned segment/reconciliation facts. Wave 14 approves exact
   component-derivation evidence for all 25 LLY/JNJ/MRK/KLAC/IBM periods. Wave
   15 freezes the immutable exact-accession policy/model, arithmetic, evidence,
   provenance, serialization, Operating Tax, and regression design while
   keeping CVX and GE as negative controls. Wave 16 implements and validates
   all 25 exact derivations, retaining all 169 direct results and reducing
   Operating Income gaps to the ten CVX/GE controls. Wave 17 completes their
   business/perimeter research with NO-GO and zero additional coverage: CVX
   remains unresolved, GE requires specialized mixed-business treatment and
   has no common five-period continuing perimeter. Wave 18 inventories all
   94 D&A gaps across 21 issuers and reaches PARTIAL GO for scoped evidence
   design with five Visa candidates, not production expansion. Wave 19 freezes
   their curated scope-equivalence acceptance design; Wave 20 implements only
   those five entries with 89 unchanged controls. Wave 21 completes the 33-period
   component review with no approved equation (19 research / 14 methodology-gated).
   Wave 22 closes reported TXN 2021–2023 asset-separation/sign questions but
   retains all three unresolved. Wave 23 clarifies new-acceptance expense basis
   and its NWC timing limitation without approving an equation. Next audit
   existing-policy timing compatibility and consumer contract. Wave 24 completes
   that audit without revoking approvals; Wave 25 designs the separate
   valuation-boundary timing contract. Wave 26 inventories the 57 missing Capex
   periods; Wave 27 designs exact-accession scope acceptance for ten AMZN/LLY
   candidates without a generic fallback. Next implement only that reviewed
   ten-entry policy. Wave 28 completes it with exactly ten new Capex resolutions;
   Wave 29 completes five CVX acquisition/perimeter reviews with no new approval;
   Wave 30 clarifies that perimeter and supports five reported-value designs,
   not any adjusted equation. Wave 31 designs only the five exact CVX entries
   under a disjoint immutable v2 catalog, preserving v1. Wave 32 implements and
   validates exactly those five entries, retaining all direct/v1 results.
   Wave 33 completes that research for the five frozen NVDA combined PP&E/
   intangible Capex periods: all remain component-scope unproved, zero coverage,
   with extensions separately gated. Next research only five LRCX combined
   cash-component periods; do not infer intangible payments from book residuals.
   Waves 34–45 finish the bounded remaining Capex issuer pass, including Visa
   v3 acceptance/implementation and unresolved QCOM, HD, MRK, VZ, PEP, GEV and
   GE research. Wave 46 consolidates coverage and exclusions and recommends
   proceeding to Phase 1H.5. Broader extension, debt/lease, D&A and working-capital
   improvements are deferred backlog, not an open-ended pre-validation sequence.
5. **Phase 1H.5 — S&P 500 Top 50 validation pass:** assign every constituent
   `SUPPORTED`, `GENERALIZATION_REQUIRED`, or
   `SPECIALIZED_METHODOLOGY_REQUIRED` and document unresolved typed states.
   **Complete:** 2 supported / 40 generalization / 8 specialized issuer decisions;
   all fifty companies / fifty-one security mappings and production counts
   reconcile. Eight specialized decisions do not change the seven execution skips.
6. **Phase 1H.6 — Freeze historical normalization v1:** record supported scope
   and exclusions, including timing-basis unknowns and lack of integrated FCFF
   certification, then resume Phase 2 forecast and DCF development. The proposed
   timing gate must precede FCFF consumption at that later valuation boundary;
   universal timing readiness is not an added historical-freeze criterion.
   **Complete:** [historical v1 contract and evidence digests](historical-normalization-v1-freeze.md)
   freeze qualified scope, schema 5, exact policies and typed exclusions.
   Phase 2 remains postponed by the subsequent explicit direction. The bounded
   analyst-NWC layer is separate post-freeze work; eventual Phase 2 consumption
   still requires timing readiness, not universal historical field coverage.

The near-term target is S&P 500 Top 50 validation, the medium-term goal is broader
S&P 500 coverage, and specialized financial methodologies remain separate
long-term work. The repository does not currently claim S&P 500 Top 50 or
broader S&P 500 support.

## Current Repository Structure

```text
valuation-platform/
├── AGENTS.md
├── README.md
├── docs/
│   ├── architecture.md
│   ├── financial-methodology.md
│   ├── project-status.md
│   ├── sec-identity-linkage.md
│   └── universe/
│       ├── sp500-top-50-2026-10-02.csv
│       └── sp500-top-50-2026-10-02.md
├── scripts/
│   └── validate_company_facts.py
├── src/
│   └── valuation_platform/
│       ├── __init__.py
│       ├── normalization/
│       │   ├── __init__.py
│       │   ├── balance_sheet.py
│       │   ├── concepts.py
│       │   ├── derived.py
│       │   ├── diluted_shares.py
│       │   ├── historical.py
│       │   ├── models.py
│       │   ├── output.py
│       │   ├── operating_nwc.py
│       │   └── pretax_scope.py
│       ├── valuation/
│       │   ├── __init__.py
│       │   └── assumptions.py
│       └── sec/
│           ├── __init__.py
│           ├── client.py
│           ├── company_facts.py
│           ├── fact_selection.py
│           ├── filing_selection.py
│           ├── filing_xbrl.py
│           ├── submissions.py
│           └── tickers.py
├── tests/
│   ├── __init__.py
│   ├── test_validate_company_facts.py
│   ├── normalization/
│   │   ├── __init__.py
│   │   ├── test_balance_sheet.py
│   │   ├── test_diluted_shares.py
│   │   ├── test_historical.py
│   │   ├── test_output.py
│   │   ├── test_operating_nwc.py
│   │   └── test_pretax_scope.py
│   ├── valuation/
│   │   ├── __init__.py
│   │   └── test_assumptions.py
│   └── sec/
│       ├── __init__.py
│       ├── test_client.py
│       ├── test_company_facts.py
│       ├── test_fact_selection.py
│       ├── test_filing_selection.py
│       ├── test_filing_xbrl.py
│       ├── test_submissions.py
│       └── test_tickers.py
├── .gitignore
└── requirements.txt
```
