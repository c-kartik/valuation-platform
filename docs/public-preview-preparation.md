# Backend launch preparation and preview history

## Production backend and cost policy — proposed October 22

**Preparation only; production and billing changes are NOT authorized.** Inspected
2026-10-22, starting valuation `a8bc1105473480406b830b7f335933d67953ebe3`, clean
`main`, three ahead of `origin/main`; portfolio
`a115327325754cb741b696fa115f38a30e63c866`, clean `main`, two ahead. No push,
application build, calculation, deployment, API enablement or cloud write occurred.
The [combined preview](combined-site-preview.md) remains separate from production.
Phase 1 stays [paused](phase1-universe-pause-checkpoint.md).

**Existing deadlines remain October 23: combined Hosting 13:10:39.991846463 Dubai /
09:10:39.991846463 UTC; manual backend withdrawal 14:17:28 Dubai / 10:17:28 UTC.**
Initial clock was October 22, 16:13:28 Dubai / 12:13:28 UTC, before both deadlines.
Planning, Hosting expiry and a proposed monthly cap do not revoke anonymous access.

### Proposed production configuration

The [non-executable production plan](../deploy/api/production-plan.json) is a review
document, **not** a Cloud Run/Firebase manifest or deploy script. `execute=false`,
authorizations and `approved_image=null` deliberately leave execution unresolved.
No existing deploy command consumes it. Generate an actual command only under a
subsequent authorized release; never pass this review JSON to a provider API.

| Setting | Recommendation / future supported setting |
| --- | --- |
| Separate target | `kartikchaturvedi-website` (`378340095652`), `valuation-api`, us-central1. Read-only GET returned 404 for that service. |
| Billing / allocation | Request-based; 1 vCPU / **1 GiB**, CPU throttling on, startup boost off, gen2. Keep tested memory. |
| Service scaling | Min 0 / **max 1**: `--min=0 --max=1`, or v2 service `scaling.minInstanceCount=0`, `maxInstanceCount=1`. |
| Revision backstop | Min 0 / max 1: `--min-instances=0 --max-instances=1`; independently verify both levels. |
| Admission / HTTP | Concurrency 1, HTTP timeout 50s, PORT 8080; keep the existing image's one-worker launcher and probe behavior. |
| Runtime | Reuse `valuation-api-runtime@kartikchaturvedi-website.iam.gserviceaccount.com`; fresh project-policy read found **zero project roles** for it. No keys or extra runtime roles needed for packaged reads/stdout. |
| Access | Initially authenticated, invoker IAM check enabled, default URL retained; ingress `all` permits later Hosting integration but does not itself grant invocation. Public production invocation needs separate authorization. |
| Release artifact | Candidate existing immutable digest `sha256:b1a0f6d846a0af17afa0c98c36b9e3d808d64539b46c5d6361ff6c0d395331f8` in `valuation-staging/valuation-api`; no rebuild if approved unchanged. Full URI in the plan. |

The [current preview record](firebase-public-preview.md#october-22-redesigned-equity-preview)
binds that image to source `0f5200d` and prior hosted tests. Fresh read-only service
inspection confirmed `valuation-api-preview-00002-kq7`, the candidate digest,
1 CPU/1GiB, service/revision max 1, no configured minimum (zero), concurrency 1,
50s, gen2 and request-based allocation. Its existing tag remains
`fh-c2ae005fc1524503`. Private service revisions remain `valuation-api-staging-00001-2rk`
and `valuation-api-public-preview-00001-hdj`; no service or IAM change was made.

The unchanged [launcher](../deploy/api/start.py), [image](../deploy/api/Dockerfile)
and [HTTP budgets](local-case-api.md#http-contract-and-budget-policy) retain one
child, 35s wall deadline, 30/31s soft/hard child CPU limits, terminate → 0.5s join →
kill/reap cleanup, 10s body read, 256KiB input, 2MiB result and existing parser/
numeric ceilings. No request-body/assumption logging. Packaged files are read-only
under nonroot UID10001; this does **not** make Cloud Run's entire filesystem
read-only or establish a peak-memory proof. Existing Linux/remote test qualifications
in the [staging record](cloud-staging-deployment.md#newly-executed-verification)
remain attributed; none were rerun here.

Service max and revision max are distinct. Tagged zero-percent revisions can
start outside the service-level limit. Keep only the **current production Hosting
tag**, attached to the revision also receiving 100% traffic; inventory/remove
obsolete production tags during separately authorized releases. Retain prior image
digests/Hosting files for manual rollback, rather than claiming automatic rollback
works after a historical pin is removed. Never remove tags still used by the
standalone/combined previews or private services as blanket cleanup. Even properly
configured maxima may be exceeded briefly. [Maximum-instance semantics](https://docs.cloud.google.com/run/docs/configuring/max-instances),
[exact CLI flags](https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy).
Production's max-one is not project-wide: preview/private services have separate
limits and can run concurrently. The proposed 13-character service name plus the
current 19-character Firebase tag pattern totals 32, below the previously observed
46-character combined-name limit; verify the future CLI's actual generated tag.

Cloud Run may queue requests before the application, eventually returning 429
when no slot becomes available (documented pending window: at least 10s or 3.5×
average startup time). Application overlap rejects 503 with `Retry-After: 1`;
there is no application waiting queue. Cold starts and platform queues can affect
catalog/health as well as runs. Min zero trades availability/latency for idle cost;
50s is not a completion SLA for cold starts plus maximal body/child work.
[Autoscaling and queue behavior](https://docs.cloud.google.com/run/docs/about-instance-autoscaling).

### Verified budget state and proposed changes

Read-only console inspection found one **`$10 Monthly Budget Alert`**: **all billing
account projects/services**, monthly, specified amount USD10, actual-spend alerts
**50/90/100/150%**. It covers this project today but is not explicitly project-bound.
Billing-admin/user email notifications are on; project-owner notifications,
Monitoring email channels and Pub/Sub are off. Savings-program/other-savings
filters are selected. No personal recipient address was copied. No Cloud Run
spend cap was displayed; status is Not applicable for the existing alerts budget.

Cloud Billing GET verified an open, linked **direct** account, currency **USD**.
The console lists the current signed-in account as Billing Account Administrator.
A read-only `testIamPermissions` verified budget get/list/create/update and
`billing.budgets.configureSpendCap`. The unsaved Create Budget definition offers
enabled spend-cap enforcement; it was canceled without selecting/saving a budget.
This supports eligibility and configuration authority, **not a tested budget
creation**. Public Budget REST listing returned 403 `SERVICE_DISABLED` for its
request consumer; console inventory supplies the observed settings. A quota-project
retry also failed; no API was enabled or permission broadened. Use the existing
console for the smallest future change; any REST prerequisite is separate scope.

**USD10 is a valid proposed amount**: the documented specified amount is
nonnegative and must match the account currency. Scope the cap to
`projects/378340095652` and billing product `services/152E-C115-5142` (Cloud Run),
calendar `MONTH`, excluding credits/savings. This means a Google billing product,
**not only the named `valuation-api` service**. [Budget fields/currency/calendar](https://docs.cloud.google.com/billing/docs/reference/budget/rest/v1/billingAccounts.budgets),
[spend-cap API constraints](https://docs.cloud.google.com/billing/docs/how-to/budget-api-spend-cap).

Recommend the cap for this small anonymous launch **if project-wide Cloud Run
outages are acceptable**. Google pauses Cloud Run services (5xx), jobs and worker
pools project-wide, including the existing private and preview workloads. A cap
does not delete resources. Static Hosting remains independent; builds, image/source
storage, logging and separately billed transfer can continue charging. Cloud Run's
own guidance notes VPC connector VM costs are outside its cap; none is proposed.
[Cloud Run cap behavior](https://docs.cloud.google.com/run/docs/tips/services-cost-optimization).
If private/staging availability must never be affected, this shared-project cap is
unsuitable; choose the alerts/manual-withdrawal fallback within the present scope.

Enforcement uses **gross estimated list-price usage before credits**, is delayed
without a guaranteed delay bound, and can overshoot; in-flight HTTP work can finish
and charge. It automatically resets/unpauses next month on Google's budget calendar
(documented Pacific time, not Dubai midnight). Manual lifting suspends enforcement
for the rest of the period unless the target is increased; recovery can take up to
an hour. Recheck existing current-month gross usage before enabling: this is not a
fresh USD10 allowance from creation. The payable invoice can be much lower than
the cap's usage counter. **This is not a USD10 total-project ceiling.**
[Spend-cap limitations and recovery](https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps).

Exact future console steps, **only after separate budget authorization**:

1. Edit the existing alerts-only budget; explicitly select only this project,
   all services, Monthly / Specified USD10, all savings/credits included to track
   net reported costs. Replace rules with actual **50/80/100%**; retain billing
   admin/user mail, enable project-owner mail once project-scoped; no Pub/Sub or
   extra notification infrastructure. Review scope/recipients, then Save and
   re-read. This intentionally replaces the account-wide scope; do not imply an
   additional whole-account umbrella remains. [Alert-budget configuration](https://docs.cloud.google.com/billing/docs/how-to/budgets).
2. Separately Create new → **Spend cap enforcement** → name `valuation-cloud-run-monthly-cap`;
   select project `kartikchaturvedi-website`, product **Cloud Run**, Monthly,
   Specified USD10. Review gross-before-savings basis and fixed 50/80/100% notices
   to billing administrators/project owners, then Finish only with authorization.
   Re-read project/product/amount/status **Configured**. Keep the alerts budget;
   do not try to convert or delete it. If eligibility/permissions or saving fails,
   stop and retain scaling limits + alerts + manual withdrawal; no improvised
   shutdown automation. [Console cap procedure](https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps).

### Low-traffic estimate, not a bill ceiling

No new workload/timing measurement was performed. Prior synthetic staging HTTPS
runs were **2.385–4.138s**; a later proxy/cloud review observed **2.312–4.566s**,
including one corresponding Run log at **2.360s**. A single startup sample was
**6.842s**. These sparse measurements from the earlier image are a planning basis,
not billed CPU time, a current-image benchmark or a cold-start distribution.
See [staging](cloud-staging-deployment.md#newly-executed-verification) and
[frontend timings](cloud-frontend-acceptance.md#timings-cloud-checks-and-limits).

Assume **one 4s run + four 0.2s validations + one 0.2s catalog call** per completed
calculation, plus **1s average startup/shutdown allocation** (illustrative 10% cold
sessions × 10s). Thus six requests and **6 allocated vCPU-seconds / GiB-seconds**
per calculation. Keep 1GiB charged allocation regardless of lower sampled RSS.
Assume 10KiB POST bodies and 225KiB total uncompressed responses per calculation
(200KiB run + 25KiB auxiliary); these are estimates within the existing ceilings.
Background editing, retries, errors and bots can substantially increase usage.

| Monthly completed calculations | Allocated seconds / requests | CPU / RAM / requests before free tier | Gross Run compute/request cap consumption | Payable compute/requests if allowances unused |
| --- | --- | --- | --- | --- |
| 1,000 | 6,000 / 6,000 | USD0.144 / 0.015 / 0.0024 | **USD0.1614** | approximately USD0 |
| 10,000 | 60,000 / 60,000 | USD1.440 / 0.150 / 0.0240 | **USD1.6140** | approximately USD0 |

Uses us-central1 request-based list prices: CPU USD0.000024/vCPU-s, RAM
USD0.0000025/GiB-s, requests USD0.40/million. Monthly no-cost allowances are
180,000 vCPU-s, 360,000 GiB-s and 2 million requests, shared across the billing
account. Remaining allowances/discounts were **not** independently measured. If
already consumed, use the before-free amounts. Non-minimum idle instances are
uncharged in request-based mode; startup/shutdown and active/abusive requests are
not free merely because minimum is zero. [Run pricing](https://cloud.google.com/run/pricing).

All-cold diagnostic (15 allocated seconds/calculation) gives **USD0.3999 / 3.999**
gross compute/requests at 1k/10k. At 35s runs plus 2s auxiliary/startup allowance,
10k gives **USD9.829** before network/other Cloud Run usage. These arithmetic
diagnostics show why free credits and a max-one setting cannot substitute for
gross-cap monitoring. No fixed maximum bill or sustainable request count follows.

Website traffic is independent of calculations. For illustration only, assume
1,000/10,000 uncached full-site visits × **1.5MB** (the combined artifact is 1.384MB),
plus the API responses above: **1.7304 / 17.304GB** Hosting transfer. At USD0.15/GB,
gross transfer is **USD0.260 / 2.596**; with the project's unused 10GB allowance,
approximately **USD0 / 1.096** payable. Browser caching/compression can lower this;
CDN hits still count. Retained Hosting versions share 10GB storage, then
USD0.026/GB. No temporary-domain sitemap/canonical changes are proposed.
[Hosting pricing](https://firebase.google.com/docs/hosting/usage-quotas-pricing).

| Other component | Explicit planning assumption / separate cost |
| --- | --- |
| Run transfer | The compute table excludes egress. Do not silently add an internet rate to an exempt CDN leg. Confirm the charged SKU/path in billing after launch; for a chargeable direct North America→Europe leg at USD0.12/GiB, 225KiB/calc adds about USD0.026 / 0.257 before eligible free transfer. That is a named-route diagnostic, not a verified Dubai/Hosting tariff. Any Run-attributed transfer also consumes its cap; Hosting-attributed transfer does not. [Run transfer rules](https://cloud.google.com/run/pricing), [network pricing](https://cloud.google.com/vpc/network-pricing). |
| Builds | Initial immutable-image reuse: **zero builds**. Later assumption: four manual e2-standard-2 builds/month × two minutes × USD0.006/min = **USD0.048 gross**; approximately zero if the shared 2,500-minute eligible allowance remains. Prior new-image remote build lasted about 33s, not a required rebuild duration. [Build pricing](https://cloud.google.com/build/pricing). |
| Registry | Illustrative **1GiB total retained layers**, not measured usage: about USD0.10/month gross, USD0.05 after the account's unused first 0.5GiB. Initial image reuse adds no new image bytes. Retain current + one known-good rollback digest and account separately for existing preview/private dependencies. [Registry pricing](https://cloud.google.com/artifact-registry/pricing). |
| Source bucket | Small source archives and operations remain separately billable. No new archive is needed for image reuse. Actual storage class/bytes, account allowance and retained soft-deleted objects determine cost; the earlier record observed seven-day soft-delete. Do not invent a measured footprint or alter retention here. [Storage pricing](https://cloud.google.com/storage/pricing). |
| Logs | Assume 1KiB metadata/request: about 0.0057/0.0572GiB at 1k/10k; about USD0.003/0.029 gross at USD0.50/GiB, approximately zero within 50GiB/project/month. Actual platform volume/retention can differ. Keep body/assumption logs disabled, not platform error visibility. [Observability pricing](https://cloud.google.com/products/observability/pricing). |

Taxes, sustained abuse, other workloads, exhausted allowances and extra transfer
are outside these illustrative payable figures. A whole-project alert and a
Cloud Run cap track different populations and cost bases; neither caps the entire
invoice at USD10. Gross Run consumption includes **all** project Run workloads,
not just the new service or successful calculations.

### Operating policy and exact future changes

Start anonymous, with no accounts or saved cases, **only after launch authorization**.
At that time add service-only `allUsers / roles/run.invoker` to the new production
service, retaining IAM checks. Firebase routing requires public invocation and
the default Run URL; direct requests remain possible. Origin/Fetch-Metadata checks
and absence of CORS are not authentication or distributed abuse protection.
No database, gateway, load balancer, Redis, CAPTCHA or auth system is required by
this minimum proposal. [Hosting/Run integration](https://firebase.google.com/docs/hosting/cloud-run).

Policy: one calculation at a time per browser client; preserve inputs and require
explicit retry for busy/outage responses, avoiding automatic retry loops. Current
buttons have per-action busy/abort guards, but **no shared EV/equity client mutex**:
starting EV during an equity request can briefly overlap before cancellation.
Do not certify a strict per-client quota from these guards. Server admission
remains one child/process; Cloud Run may queue instead of exposing app 503s.
Accept this bounded UX limitation or separately scope a strict shared guard;
it is not a reason to add distributed infrastructure. There is no per-user/global
distributed quota, identity, availability SLA or hard-dollar guarantee.

Reuse the existing registry, source bucket, builder and unprivileged runtime
identity. Future changes are **one separate Run service/revisions**, any explicitly
approved service-only invoker grant, two reviewed budget edits/creation steps,
then production-routing Hosting preview/version and separately approved live/domain
changes. No new build resource/identity/API is presently necessary for image reuse.
The future deployer needs Run create/update/get/operations, repository image read,
`actAs` on the runtime identity and, for public transition/withdrawal, service IAM
get/set. Hosting release authority is needed later. Recheck existing permissions;
grant only a missing scoped permission under separate authorization, never new
Owner/Editor/runtime project roles by default. Existing builder grants remain
as previously [recorded](cloud-staging-deployment.md#created-resources-and-access).

Use existing console signals: requests and 429/5xx rates, latency, active instances,
memory/restarts, gross Run cap progress and project billed spend. Recommended human
review: daily during initial launch and promptly after budget/error notices; name
an available operator before public launch. Do not poll/keep warm or add monitoring
infrastructure. Sparse prior memory samples do not justify lowering memory.

Rollback is manual: choose the known-good immutable image, deploy it as a new
production revision with the same limits, verify it, route 100%, and issue a
matching Hosting pin/release. Preserve a matching static release, but verify its
tag still exists before any Hosting rollback. Emergency withdrawal removes
**only production service-level anonymous invoker access**, verifies default and
every tagged URL deny anonymous requests, and leaves the static portfolio online.
First check for any other grant/bypass; do not assume removing one binding defeats
project-level public access. Do not disable project billing or touch private
services. Existing requests may finish. If appropriate, separately release a
calculator-unavailable static page while retaining portfolio pages; no such change
is implemented now. A monthly cap's automatic reset is **not** access withdrawal.

Retain current + one known-good rollback image/Hosting release, with known source
bindings. Inventory dependencies before any later preview-tag/release/image/source
cleanup; expired channels do not themselves remove Run access or all stored bytes.
No cleanup, automated deletion policy or monitoring resource was created today.

### Concrete launch sequence and decisions

| Stage | Required next authority / verification |
| --- | --- |
| A | Approve the proposed allocation/scaling/tag policy, anonymous/direct-URL risk, low availability under max-one and project-wide cap outages; choose the human operator and accept or scope the cross-action client limitation. Approve the immutable production image after a source/resource match. |
| B | Separately authorize the explicit project-alert update and USD10 Cloud Run cap; recheck current-month gross spend, then configure/re-read. Alternatively explicitly accept limits + existing alerts + manual withdrawal. No budget change is authorized by this plan. |
| C | Authorize private-first deployment of `valuation-api`; preserve all private staging services. Verify effective service/revision settings, digest, identity, health and anonymous denial; run bounded synthetic smoke/CLI comparisons under that future task. |
| D | Separately authorize production anonymous invocation when needed for Hosting, then a combined-site preview pinned to that exact production revision. Verify routes/pages/PDF, JSON errors, EV/equity equivalence, cold/busy/retry behavior and cost signals; do not reuse expired preview authority. |
| E | Approve Firebase **live release and domain migration separately** after the preview review. Capture current DNS/Netlify rollback settings read-only. Wait for Firebase's verified domain-specific instructions; DNS provider, registrar and exact records are unresolved. Review production crawler headers/canonicals; do not ship preview noindex unintentionally. |
| F | After authorized cutover verify HTTPS/certificate, every existing page/link/download, `/valuation/` entry/direct refresh, API routing and bounded synthetic calculations. Retain signed source/image/Hosting bindings. |
| G | Keep Netlify, saved prior DNS values and a known-good release for rollback. Do not push the portfolio repository while its active Netlify push webhook has an unreviewed live effect. Later cleanup is separately scoped. |

The blockers are **authorization and policy choices**, not a need to rebuild the
financial engine: production image/configuration, public-invocation/cap availability
acceptance, operator, future smoke/preview acceptance and live/domain approval.
Eligibility/permissions support a USD10 cap, but its actual creation/enforcement
was not tested. Exact DNS instructions and a future live release remain unresolved.
Strict cross-action client serialization, peak-load/memory certification and
stronger abuse protection remain explicit qualifications/possible follow-ups,
not invented mandatory infrastructure. No financial-input sufficiency or
investment readiness follows.

Validation for this planning checkpoint: JSON/static consistency with the unchanged
launcher/API ceilings, independent Decimal cost arithmetic, official source review,
read-only console/API inspection, changed links/anchors, whitespace, staged secret
patterns, protected-byte scope and all nine unset templates. No financial tests,
new app/image build, valuation execution or full historical suite were needed.

## Earlier preview preparation record

> **Historical October 21: the shorter-name retry was deployed and verified within its bounded scope.**
> [Active preview and manual withdrawal record](firebase-public-preview.md).
> Withdraw backend access by **October 22, 2026, 13:04:19.869 Dubai / 09:04:19.869 UTC**.
> The failed-name attempt and earlier inspection records below are historical.

> **Earlier checkpoint, 2026-10-21: deployment BLOCKED; anonymous access withdrawn.**
> Firebase/site identity is verified. The attempt failed on the combined service/tag
> name limit; no Hosting release or hosted-browser acceptance occurred.
> See the [attempt and withdrawal record](#deployment-attempt-and-withdrawal--2026-10-21).
> Earlier preparation/inspection statements below retain their original scope.

Reviewed 2026-10-20 (Asia/Dubai), starting clean `main` at
`70a9b4fea6a5e1046ae1eb4c742a51b90c35df6a`, two ahead of `origin/main`.
**No deployment/public access is authorized or performed.** Phase 1 remains
[paused](phase1-universe-pause-checkpoint.md); qualified financial/software limits persist.

## Recommendation and present blockers

Smallest practical experiment: an **anonymous, one-day preview channel on a verified
existing Hosting site**, same-origin `/api` to a separate proposed Cloud Run service
`valuation-api-public-preview` in `kartikchaturvedi-website`, us-central1. Keep
`valuation-api-staging` authenticated and unchanged. Reuse the existing no-project-role
runtime identity, one Uvicorn worker, 1 vCPU/1GiB, request-based billing, min 0,
service/revision max 1, concurrency 1 and 50s HTTP/35s calculation limits.
Monitor while sharing and be willing to withdraw the preview if abuse or costs rise.

This is defensible for a bounded personal experiment **only with explicit acceptance
of availability and spending risk**. It does not guarantee fair access against a bot
or a dollar ceiling. If uninterrupted public availability or an enforced total budget
is required, the current proposal is insufficient; choose stronger admission/cost
controls before exposure. No evidence presently requires a gateway, load balancer,
Redis, database, CAPTCHA or user-account system merely to test the calculator.

Deployment is presently **blocked**: the existing Firebase project/site association
and site ID are unverified. Installed Firebase CLI 11.3.0 has no local login;
read-only `hosting:sites:list` failed authentication. No login/provisioning was
attempted. Read-only Console navigation to the named project's Hosting page redirected
to onboarding for adding Firebase to an existing Cloud project; stopped before
Continue and closed the tab. This did not verify an existing site or association.
No `.firebaserc`, site or target was created. Use an up-to-date CLI with
Cloud Run `pinTag` support in the future authorized step; this old installation's
code has no `pinTag` handling. The literal unresolved site in
[firebase.preview.json](../firebase.preview.json) and the local publication guard
deliberately prevent treating this as deploy-ready. No identifiers are guessed.

## Read-only Firebase inspection — 2026-10-20 (Asia/Dubai)

This follow-up started clean at `14ba781b1d9e55dc596dcf7c79b8cccafd56ca2c`,
three ahead of the local `origin/main`. Only this document changes; no application
checks, financial runs, installation, login or cloud mutation occurred. The 95 tests
and build below belong to the preceding preparation checkpoint, not this inspection.

| Question | Verified observation / limitation |
| --- | --- |
| Cloud project identity | Signed-in Cloud Console **Settings** shows name Personal Website, ID `kartikchaturvedi-website`, number `378340095652`. |
| Firebase enabled? | Hosting navigation again redirects to the add-Firebase **Get started** form. Cloud **Labels** shows no labels, including no `firebase:enabled`; Firebase Management API and Firebase Hosting API library pages each offer **enable this API**. This supports an incomplete/unavailable Firebase setup, but is not an authenticated Firebase project-resource lookup or proof the project was never enabled. |
| Hosting initialized / sites | **Unverified**, not an empty inventory. No site listing is available through the observed Console state. No site ID is verified; do not substitute the Cloud project ID. |
| Default / custom domains | **Unavailable** without a verified site inventory and domain listing. No custom-domain association or absence is established. |
| Live releases / preview channels | **Unavailable**; no release/version/channel IDs or collision check can be recorded. The proposed `ev-public-review` name is not verified unused. |
| Local tooling / permissions | Firebase CLI remains **11.3.0**; fresh `firebase login:list --json` returned success without accounts. No `gcloud` is on PATH. The prior unauthenticated site-list failure remains attributed to preparation. There is no new `PERMISSION_DENIED` result establishing insufficient IAM; the blockers are unavailable authenticated CLI access and Console onboarding. |
| Checkout selection | No `.firebaserc`, Hosting targets or default `firebase.json`; the sole prepared config is `firebase.preview.json`, with explicit `hosting.site=UNRESOLVED_EXISTING_HOSTING_SITE`. It selects **no verified destination** and its deploy guard fails closed. No config identifier was changed. |

Read-only pages used: Cloud Console project Settings, Labels, and the API library
entries for `firebase.googleapis.com` and `firebasehosting.googleapis.com`, plus the
Firebase Hosting URL. No Enable, Continue, Save, setup confirmation or Cloud Shell
action was taken; task tabs were closed. Existing private staging was not modified
or reauthenticated/retested in this follow-up. Its recorded configuration remains
in the [deployment checkpoint](cloud-staging-deployment.md).

### Onboarding meaning and the smallest destination

The observed **Continue** belongs to an informational add-Firebase form. Its notice
says adding Firebase cannot be fully undone and billing, IAM and resources are shared
with Google Cloud. It does not show what the next button or screen will do. Do not
claim Continue alone completes setup. Official documentation says completed onboarding
adds Firebase configuration, enables APIs, creates managed service accounts and a
restricted Browser API key, and adds the project label. Existing billing implies
Blaze; adding Firebase is not a separate billing account. Terms acceptance may be
required; Analytics and AI assistance are optional. None was accepted or enabled.
[Adding Firebase: effects, permissions and terms](https://firebase.google.com/docs/projects/use-firebase-with-existing-cloud-project).

**Recommendation remains conditional:** reuse a verified suitable site and create
only its `ev-public-review` preview channel, expiring **one day after deployment**.
First record that site's live version, domains and channels; require the channel name
to be unused rather than overwrite another preview. Preview deployment publishes a
separate public preview URL, not the site's live channel or custom-domain release.
`firebase deploy --only hosting` would publish live and is outside this plan.
[Channel lifecycle](https://firebase.google.com/docs/hosting/manage-hosting-resources).

If inspection confirms Firebase has not been added, authorize that one-time setup
first, then inspect any resulting default site. Do not create an additional site if
an unused suitable default site suffices. If no suitable site exists, separately
approve creation of **one calculator-only site**, proposed ID `kc-valuation-preview`
(global availability unverified), with no custom domains or live deployment. Its
prospective default domains would be `kc-valuation-preview.web.app` and
`kc-valuation-preview.firebaseapp.com`; these are **not verified existing domains**.
Site IDs are global and at most 30 characters; do not silently choose a different ID
on collision. [Sites and default-domain rules](https://firebase.google.com/docs/hosting/multisites).

Once verified, an explicit site in this single-site config plus explicit `--project`
and `--config` would remove default-project/target ambiguity. No target or initialization wizard is needed to regenerate the prepared local files. Within that
preview origin the calculator is at `/`, API rewrite precedes SPA fallback, and
`pinTag` binds the latest backend revision at deploy time. A dedicated new backend
and a deployment freeze prevent another application's revision being pinned. These
are configuration/documentation checks, not an executed CDN test.
[Cloud Run pinning](https://firebase.google.com/docs/hosting/cloud-run).

### Required actions and permissions — ordered, not executed

Use existing authorized access; **do not grant Owner/Editor to solve this inspection**.
Permissions below describe future operations, not evidence of current effective IAM.

| Order / scope | Required action and minimum access | Change / billing or access consequence |
| --- | --- | --- |
| 1 — read-only access | User supplies an authenticated current Firebase CLI session (or authorizes its update and interactive login); use Hosting Viewer for read-only inventory (`firebase.projects.get`, `firebasehosting.sites.get/list`, project get/list). Existing browser login is not a CLI login. | No resource creation; interactive credential handling is a separate step. Inventory sites, domains, live version and channels before selecting anything. No new IAM grant is requested now. |
| 2 — conditional one-time setup | Only if confirmed needed: add Firebase to this exact project. Required: `firebase.projects.update`, project get, `serviceusage.services.enable/get`; user handles any Firebase Terms. Then inspect default site; create one named site only if needed, using Hosting Admin's site-create capability. | Project-wide APIs/managed identities/key/configuration; not fully reversible. Shared existing billing/IAM. Site creation reserves default domains; no DNS or live content deployment. No Analytics, database, Auth application, SDK or workflow setup. |
| 3 — local preparation | Resolve only the verified `hosting.site`, use current pinTag-capable CLI, locked frontend build and publication checks; prepare allowlisted backend context from reviewed source. | Local artifacts only. No remote permission required until submission; keep private files outside public root. |
| 4 — build / private new service | Build submitter needs build-create/read, source-upload and `iam.serviceAccounts.actAs` on the existing builder; reuse its scoped registry-write, source-read and log-write grants. Deployer needs Run create/update/get, operations get, registry download and actAs on the existing runtime identity. | New image/source/log storage and compute charges; new **authenticated** service first. No change to old staging, runtime project roles, billing linkage or shared APIs is proposed. Confirm service name unused first. |
| 5 — public preview deployment | Service-only `run.services.getIamPolicy/setIamPolicy` to grant `allUsers` `roles/run.invoker`; Hosting Admin for channel/version/release writes. Pinning also needs Run service get/update for revision tags; Hosting-only access is insufficient. | New service becomes anonymously invokable, including direct URLs; Hosting creates preview content/release and backend tag. Separate explicit exposure authorization required. |
| 6 — verify / manually withdraw | Read service/revision/IAM/log/usage state; Hosting Admin for channel deletion and service policy set/get to remove public invoker. Reuse existing monitoring access. | Withdrawing public access ends anonymous calculations; retained images, versions and storage can still cost money. Service deletion/storage cleanup requires its own reviewed scope. |

Hosting uses predefined product roles; custom roles cannot currently control its
resources. No broad new grants are implied by the operation list.
[Hosting roles](https://docs.cloud.google.com/iam/docs/roles-permissions/firebasehosting),
[Hosting access restriction](https://firebase.google.com/docs/projects/iam/permissions),
[Run deployment permissions](https://docs.cloud.google.com/run/docs/reference/iam/roles).

### Concrete authorization checklist for a future step

- **Inspection/tool access first:** current Firebase CLI login and read-only inventory;
  exact project above is verified, site/domains/live version/channel collisions remain
  unresolved. Do not initialize Firebase merely to discover them.
- **Separate one-time setup approval, if needed:** add Firebase with its documented
  project-wide effects and user-handled terms; then verify/reuse default site, or
  separately approve the named calculator-only site. This grants no deployment authority.
- **Build/deploy/public approval later:** channel `ev-public-review`, `--expires=1d`,
  exact verified site, calculator at preview root; separate new service
  `valuation-api-public-preview` in us-central1 with the resource/deadline settings
  above and existing runtime identity. Preserve authenticated `valuation-api-staging`.
- **Source/image:** build runtime changes from reviewed commit
  `14ba781b1d9e55dc596dcf7c79b8cccafd56ca2c` (or explicitly reviewed successor including
  resolved site). Record exact new image digest; **none exists from this inspection**.
  The current staging digest/source `ebf6139` lacks new HTTP protections.
- **Exposure/cost acceptance:** anonymous Hosting URL **and direct backend invocation**;
  no login/bot/global-quota promise. Build, registry/source/Hosting storage, Run
  CPU/memory/requests, transfer and logs can charge. Existing $10 alerts are not a
  cap; no optional spend-cap budget was configured or verified. Name a human to
  monitor the one-day window and withdraw early if needed.
- **Before sharing:** verify new digest/revision/limits/IAM, synthetic CLI equality,
  validation/errors/oversize, same-origin routing, no-store/CSP, cross-site handling,
  no private bytes, desktop browser journey; confirm old staging denies anonymous
  access and recorded live Hosting release/custom domains remain unchanged.
- **Withdrawal:** at the recorded one-day deadline, or earlier, remove the **new
  service's** allUsers binding and delete only the verified preview channel using
  the commands below. Check channel unavailable and default/tagged backend URLs
  deny anonymous health/catalog/run. **Hosting expiry alone does not disable the
  backend.** If backend denial cannot be verified, investigate remaining effective
  invoker grants and withdraw the new service under explicit shutdown authority;
  never modify old staging. No scheduler or automatic shutdown was created.

Next user action: authorize only the current CLI authentication/read-only inventory
step, or provide its resulting project/site/domain/channel inventory. If that confirms
missing Firebase setup, request the distinct one-time setup scope above before any
Continue/Enable action. Public build/deployment remains a later authorization.

Documentation checks: all nine local links/anchors in this document resolve;
whitespace and the staged one-document scope were reviewed. Configuration, code,
templates, financial/history/source approvals and frozen artifacts are unchanged.
No application tests or financial checks were rerun.

## Implemented attack surface, inspected in code

| Surface | Already enforced / newly verified locally | Residual risk |
| --- | --- | --- |
| Bytes / slow upload | 256KiB, counted before appending streamed chunks, regardless of Content-Length; 10s absolute body-intake deadline. Encoding/type/duplicate or misleading length rejects. Local tests exercise missing length, chunked oversize and stalled receive. | Platform connections can be occupied and billed before/while application rejection; these are not edge bandwidth quotas. |
| Malformed / deep / expensive JSON | Existing strict parser; depth 24, nodes 4096, object 64, general arrays 128; bounded text/references; Decimal strings 128 chars / 64 digits, exponent/adjusted magnitude ≤100. Short huge exponents reject before Decimal construction. | Bounded parsing occurs in parent before the financial child; not a proof of maximum RSS under all concurrent inputs. |
| Execution / cleanup | One spawned child per process, immediate busy 503 within application, 35s wall and Unix 30s soft/31s hard CPU. Terminate, join, kill/reap on deadline/disconnect/cancel/shutdown before releasing slot. Focused host tests cover these paths. | Cloud Run may queue before admission. Multiple processes/revisions/instances multiply capacity. No distributed quota or measured worst-case memory; OOM can restart an instance. |
| Admission / memory | Launcher: one worker, Uvicorn concurrency 16, backlog 32, keepalive 5s. Proposed public service retains 1GiB external container limit and max 1. | App input/output bounds are not a per-child memory cap. These cloud settings are proposals for the new service, not deployed here. Rejects/restarts still consume resources. |
| Response / catalog | Incremental result limit 2MiB; errors ≤20×200 chars; catalog ≤64KiB startup-built projection. No source/evidence file route, arbitrary ticker/retrieval, destination/URL execution or query operands. Source-reference strings are inert. Worker verifies private bundle and denies network/subprocess/mutation. | Public result JSON includes existing detailed historical provenance and user-submitted declarations; review that intended public contract. API also accepts existing v2 equity cases although this UI exposes EV only. Audit hook is not an OS sandbox. |
| Disclosure / logs | Fixed internal-error messages, no traceback/body in application logs; access logging disabled. React renders submitted text as text; no HTML execution. Catalog excludes package/audit bodies and developer paths. | Platform request logs still include request metadata/URLs; do not put assumptions or secrets in query strings. Platform error responses outside the app are not controlled here. |
| Browser / caching | Relative `/api`, JSON POST, credentials omitted, no-store fetch, 50s client abort and revision guards; no auto-retry/autosave. New response middleware sets **no-store + nosniff on all app responses**, including errors/404/405/health. | Client abort is not a global quota; a malicious client can keep submitting valid work. Dynamic middleware changes are local, absent from the deployed image. |
| Cross-site / direct calls | No CORS allowance. New early rejection of `Sec-Fetch-Site: cross-site` precedes body reads/parsing. Same-origin/headerless clients retain existing JSON behavior. | **CORS is neither authentication nor abuse control.** Fetch Metadata only deters ordinary cross-site browser use; scripts can omit/spoof it. Firebase forwarding must be checked after deployment. Direct anonymous `run.app` callers would have the same application limits. |

New tests cover pre-parser cross-site rejection and uniform safe headers, including
unexpected failures; existing valid EV/equity cases still match ordinary CLI/full JSON.
No financial formulas, schemas, resource pins, approvals or templates changed.
No rate-limit framework was added: **per-process rate limits are not distributed
quotas**, reset on restart and can let one bot exhaust shared capacity. A small
in-memory limiter could later smooth accidental bursts, but does not resolve the
material anonymous-client spending/availability problem by itself.

## Hosting, direct access and cost decisions

Firebase's documented Cloud Run rewrite uses an unauthenticated backend. A preview
URL is public/shareable, not an access restriction. `pinTag: true` supports Cloud Run
rewrites on preview channels and binds the release to the service's most recent
revision at deployment; Hosting rollback restores that release's backend pin. Pinning
creates Cloud Run tags, subject to tag limits. Hosting's timeout is 60s, outside
the proposed Run 50s and child 35s ceilings. These are documented capabilities,
not a new remote test. [Cloud Run integration](https://firebase.google.com/docs/hosting/cloud-run),
[preview visibility](https://firebase.google.com/docs/hosting/test-preview-deploy).

For this simple integration, plan on public ingress to the **new** service, including
its direct URL. Do not promise Firebase-only origin restriction: Google lists
Firebase Hosting as dependent on the default `run.app` URL. Disabling it can break
the rewrite. Host/CORS checks or a public frontend secret would not authenticate
callers. A load-balancer/Cloud Armor design would add services/charges and must also
close direct-origin bypass; that is deferred, not silently configured.
[Ingress behavior](https://docs.cloud.google.com/run/docs/securing/ingress),
[Armor integration](https://docs.cloud.google.com/armor/docs/integrating-cloud-armor).

| Cost/control | Practical consequence / proposed treatment |
| --- | --- |
| Cloud Run CPU/memory/requests/network | Min zero avoids a permanently warm allocation, not sustained anonymous load. At listed request-based active rates, one 1-vCPU/1GiB allocation continuously active for 30 days is approximately **$68.69 compute-only**, before free tiers, requests/network/logging/tax. This diagnostic is **not a total spending cap or forecast**. [Run pricing](https://cloud.google.com/run/pricing) |
| Scaling / alerts | Max instances manages scaling but may briefly be exceeded; it does not cap request, storage, transfer or logging charges. Existing $10 alerts are notifications, not a hard cap. [Maximum instances](https://docs.cloud.google.com/run/docs/configuring/max-instances), [alerts-only budgets](https://docs.cloud.google.com/billing/docs/how-to/budgets) |
| Optional spend-cap budget | Current Google docs include Cloud Run in eligible single-project/single-service monthly spend caps. Enforcement is delayed, in-flight work can finish and persistent storage charges remain. Eligibility/configuration is unverified here; no change made. Could be useful if separately approved, but not a hard all-service invoice ceiling. [Spend caps](https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps) |
| Firebase Hosting | Adds stored versions plus CDN transfer, including cache hits. Listed allowances: 10GB storage and 10GB/month transfer; Blaze overages $0.026/GB storage and $0.15/GB transfer. Project allowances may be shared. Expiring preview does not remove the Cloud Run service. [Hosting usage/pricing](https://firebase.google.com/docs/hosting/usage-quotas-pricing) |
| Build-independent storage / logs | Existing image/source bucket remain chargeable independent of builds/traffic. A new image and Hosting versions add storage; source-bucket soft-delete retention persists. Platform logs can grow on rejected traffic. Avoid body logging; review usage and retained versions/images after trial. [Registry pricing](https://cloud.google.com/artifact-registry/pricing), [Storage pricing](https://cloud.google.com/storage/pricing), [Observability pricing](https://cloud.google.com/products/observability/pricing) |

No paid gateway/Armor/Redis/database/Auth/App Check is part of the minimum proposal.
App Check or a challenge is an optional future barrier with SDK/backend verification,
provider quotas/costs and UX implications, not user identity or a complete bot defense.
Review need from actual abuse/traffic rather than adding it by default.
[Custom-backend App Check](https://firebase.google.com/docs/app-check/custom-resource-backend).

## Prepared static/routing boundary

[Configuration](../firebase.preview.json) hosts the calculator at **`/` of its preview
origin**, not the portfolio domain or a `/calculator` mount. Vite's existing root asset
base and relative API calls remain unchanged. No extra Hosting site, target, custom
domain, Firebase web SDK, Functions, data store or automatic workflow is introduced.

Ordered rewrites: **`/api{,/**}` → `valuation-api-public-preview` / us-central1 /
pinTag**, then `**` → `/index.html`. API errors must remain API responses, never SPA
HTML. Static matches precede rewrites in Firebase; the artifact guard excludes any
`api/` file. The SPA fallback does not publish a requested repository file: it serves
the same public index, without source bytes. [Hosting ordering/configuration](https://firebase.google.com/docs/hosting/full-config).

Public root is **only `frontend/dist`**: index, favicon, one hashed JS and one hashed
CSS. [Read-only guard](../scripts/check_firebase_preview.py) rejects extra files,
source maps, symlinks, private/credential markers, nonlocal index references, unexpected
root/size and unresolved deploy site. It is an exact artifact check, not a universal
secret scanner, remote identity check or Firebase emulator. No repository/evidence,
private bundle, case, credential, node_modules or source tree is published.

Header plan: no-store for index/fallback/API; immutable year-long cache only for hashed
`/assets/**`; same-origin CSP, nosniff, no-referrer and noindex/nofollow. Noindex is not
access control. The API now owns no-store on all app responses; do not rely only on
Hosting headers for dynamic content. Verify headers through the actual CDN, including
4xx/5xx, before sharing. [Dynamic cache behavior](https://firebase.google.com/docs/hosting/manage-cache).

## Future sequence — proposal only, do not execute in this checkpoint

1. Complete the separately authorized inspection and, only if required, one-time
   Firebase setup described above. Then obtain approval for one-day anonymous exposure
   of the **new service only**, direct URL access, bounded settings above, monitored
   cost/availability risk and shutdown authority. If no verified suitable site exists,
   **stop** for the named setup/site scope; do not initialize/create one implicitly.
   Review existing live channel/config/domains and record its version without changing it.
   Check the proposed new Cloud Run name is unused; if it exists, stop rather than
   overwrite or silently reuse it. No authenticated remote absence check was performed here.
2. Replace only the unresolved `hosting.site` after verifying it. No `firebase init`,
   `.firebaserc` target mutation or deployment to `live`. Run locked build, focused
   checks and `python3 scripts/check_firebase_preview.py --for-deploy` again.
3. Prepare the allowlisted image context via the [existing recipe](local-api-image.md#prepare-an-exclusive-allowlisted-build-context).
   Authorize a new regional build from the reviewed commit using the existing scoped
   builder/repository/source bucket, logging-only build configuration and 900s ceiling.
   Inspect exact contents and resulting digest/Linux checks. **Do not reuse the current
   staging digest:** it lacks this checkpoint's HTTP protection changes. Review the new
   digest before any public grant; no build or Linux-image execution occurred here.
4. Deploy that reviewed digest **initially authenticated** to the new name, using
   existing zero-project-role runtime identity and no new roles for it. For a current
   gcloud, the proposed command is below; neither variables nor commands were run:

   ```bash
   gcloud run deploy valuation-api-public-preview --project=kartikchaturvedi-website --region=us-central1 \
     --image="$REVIEWED_NEW_IMAGE_DIGEST" \
     --service-account=valuation-api-runtime@kartikchaturvedi-website.iam.gserviceaccount.com \
     --cpu=1 --memory=1Gi --concurrency=1 --min=0 --max=1 --min-instances=0 --max-instances=1 \
     --timeout=50s --cpu-throttling --no-cpu-boost --execution-environment=gen2 \
     --ingress=all --no-allow-unauthenticated
   ```

5. Verify revision/digest/limits, private health/catalog/synthetic CLI matches and
   anonymous denial. Then apply the specifically authorized **service-only** public
   invoker grant (not to current staging, the project or runtime identity):

   ```bash
   gcloud run services add-iam-policy-binding valuation-api-public-preview \
     --project=kartikchaturvedi-website --region=us-central1 \
     --member=allUsers --role=roles/run.invoker
   ```

6. Freeze deployments to the new service while deploying the one preview, so pinTag
   selects the reviewed latest revision. Inspect the generated tag/rewrite revision:

   ```bash
   firebase hosting:channel:deploy ev-public-review --project=kartikchaturvedi-website \
     --config=firebase.preview.json --expires=1d
   ```

   The config names exactly one verified existing site; no target creation or live
   deployment. Public URL expiry is not backend expiry. [Channel lifecycle](https://firebase.google.com/docs/hosting/manage-hosting-resources).
7. Before sharing, check compiled-file membership/CSP, same-origin API/JSON/no-store
   at every status, unknown API versus SPA behavior, no private bytes, cross-site
   browser denial and direct headerless-call bounds, normal CLI equality, invalid/
   oversize rejection, and a short bounded browser journey. Inspect request/transfer/
   billing metrics and logs; no load test or peak-memory claim by implication. Recheck
   the original service remains authenticated and live Hosting/portfolio/DNS unchanged.

Rollback: for a broken first preview, withdraw that channel and remove the **new
service's** allUsers invoker binding first; verify direct and tagged URLs deny anonymous
calls. Deleting/expiring a channel alone does not revoke backend access. For a later
version, clone the recorded prior Hosting version **to this preview channel only**;
verify its retained tag. Redeploying an old config with pinTag alone would pin the
then-latest backend, not necessarily the desired prior revision. Never clone/deploy
to live. Retain rollback image/tag until the trial is accepted.
After explicit cleanup approval, delete only the preview channel/new service and
its now-unused tags/image/version; preserve original staging, shared runtime/builder,
repository/bucket and prior records. Check storage retention/soft-delete costs.
No automatic rollback, billing disablement, scheduled cleanup or monitoring service
is configured in this task.

Proposed withdrawal commands, only after approval and verification of the site ID:

```bash
gcloud run services remove-iam-policy-binding valuation-api-public-preview \
  --project=kartikchaturvedi-website --region=us-central1 \
  --member=allUsers --role=roles/run.invoker
firebase hosting:channel:delete ev-public-review --site="$VERIFIED_EXISTING_SITE_ID" \
  --project=kartikchaturvedi-website --config=firebase.preview.json
```

For an approved rollback to an already recorded prior version instead of withdrawal:

```bash
firebase hosting:clone "${VERIFIED_EXISTING_SITE_ID}:@${REVIEWED_PRIOR_VERSION_ID}" \
  "${VERIFIED_EXISTING_SITE_ID}:ev-public-review" --project=kartikchaturvedi-website
```

## Prior preparation verification and decisions remaining

[Narrow keyboard record](narrow-keyboard-review.md) completes the earlier outstanding
desktop-viewport check, with observed confirmation fixes and actual screenshots.
**95 focused tests passed**: 56 frontend + 39 API/catalog/lifecycle/preview/launcher/
publication/preservation. Build and public-artifact check passed; deploy guard rejected
unresolved site as intended. Existing valid cases/full JSON remain compatible.
Nine unset templates, historical/frozen/source approvals and financial formulas are
byte-unchanged; no actual-company case/default was saved. No full historical suite.
Earlier cloud arithmetic and Linux-image checks remain attributed to the
[browser/cloud](cloud-frontend-acceptance.md) and [deployment](cloud-staging-deployment.md)
records, not rerun. Existing Cloud Run anonymous
health returned **403**; there were no cloud builds/settings/IAM/public grants,
Firebase deployment, Docker/SDK installation, Netlify/DNS/portfolio changes or push.

Remaining decisions: **(1)** verify an existing Firebase site/project association and
approve only its preview channel; **(2)** approve the new public service and direct URL,
limits, one-day sharing window and monitored residual risks; **(3)** choose whether a
separately reviewed Cloud Run spend-cap budget is wanted, and who will monitor/withdraw
the trial; **(4)** authorize the reviewed new build/deployment and its actual remote
routing/security checks. Stronger global abuse protection remains optional only if
these bounded-preview risks are accepted; it is required for a stronger service promise.


## Deployment attempt and withdrawal — 2026-10-21

**BLOCKED, safely withdrawn; not a hosted-preview PASS.** Started clean at
02888f4454f47247946b7ddd57960073cbfdfe85, four ahead of origin/main.
The user separately authorized Firebase enrollment, then this bounded public trial,
ordinary scoped charges and a reviewed commit/push. Phase 1 remains paused.

### Preflight and exact artifacts

Firebase project kartikchaturvedi-website / 378340095652 is ACTIVE. The preceding
authorized enrollment created its default site and domains
kartikchaturvedi-website.web.app / kartikchaturvedi-website.firebaseapp.com.
Analytics details GET returned 404 (unlinked). Before deployment: live channel only,
no releases/preview channels/custom domains; the new backend name returned 404.
The config now names this verified single site; no extra site or target was added.

GitHub workflows, webhooks and deployments were empty, as were regional/global Cloud
Build triggers. The signed-in GitHub account settings showed **No installed GitHub Apps**.
The OAuth CLI could not list installations (403); no broader token was requested. Reused builder grants: repository Writer, source-bucket Viewer,
project Logs Writer. Runtime identity still has no project roles. No new project
grants, keys, API enablement, billing setting or automatic workflow in this attempt.

Official Firebase CLI **15.34.0** was installed temporarily outside the repository,
using existing login; system CLI 11.3.0 was not used for pinning. Current docs and
installed code confirm run.pinTag selects the newest revision at preview deployment.
Used --no-authorized-domains to skip optional Firebase Auth domain synchronization.
No Analytics, Auth application, local Docker or other infrastructure was added.
[Official pinning behavior](https://firebase.google.com/docs/hosting/cloud-run).

| Binding | Actual value |
| --- | --- |
| Clean API/frontend source | 02888f4454f47247946b7ddd57960073cbfdfe85 |
| API context | 89 allowlisted files: generated private bundle plus four recipe inputs; no full checkout/corpus, credentials or frontend |
| Context SHA256 | 5a16ecc3e31b8e675b3fe69cbdef4d53c9eb7e493542aa890328a382efe53125, canonical sorted path/hash JSON |
| Source archive | 834345 bytes; SHA256 50bf7506937408766e357878588f269da94abdf3b7dfa17c80e7637cbcc38d78; uploaded size/MD5 verified, object generation pinned |
| Remote build | 3f749624-8bfd-4819-85de-c09fe176da6d, us-central1, SUCCESS; existing builder, logging-only, 900s ceiling |
| Build interval, October 21 | 08:36:20.244530175–08:36:59.739907 UTC / 12:36:20.244530175–12:36:59.739907 Dubai; build duration, not request/cold-start latency |
| Image | us-central1-docker.pkg.dev/kartikchaturvedi-website/valuation-staging/valuation-api@sha256:28cf0f0b8161ef39d0ccd169aee56621dd1544c622750c8357f31cc27de9a471 |
| New service / revision | valuation-api-public-preview / valuation-api-public-preview-00001-hdj |
| Direct URLs, now anonymous 403 | <https://valuation-api-public-preview-378340095652.us-central1.run.app> / <https://valuation-api-public-preview-ailnp3irra-uc.a.run.app> |
| Created / ready, October 21 | 08:38:24.148166 / 08:38:38.638788 UTC; 12:38:24.148166 / 12:38:38.638788 Dubai |
| Static artifact | Four files / 291006 bytes; same JS index-Dm91Ibhh.js and CSS index-BUsYcr5G.css hashes as the [keyboard record](narrow-keyboard-review.md); not released |

Remote linux/amd64 Docker build, recipe dependency/manifest checks and image-inspection
step succeeded. Prior container lifecycle probes remain attributed to the
[original staging record](cloud-staging-deployment.md), not rerun. Initial REST create
body was rejected for including service.name; corrected before creation. Anonymous
health was initially 403. Firebase's user token was not accepted for private
application invocation (401); no authenticated application-success claim is made.

Verified new configuration: 1 vCPU/1GiB, service/revision min 0/max 1, concurrency 1,
gen2, request-based CPU, startup boost off, HTTP 50s, existing runtime identity;
one Uvicorn worker and unchanged request/parser/result/35s-child/CPU/cleanup/logging
limits. Only this service briefly received allUsers Run Invoker; anonymous health
then returned ready/200. No remote calculations or assumption/body logging.

### Exact deployment blocker and completed withdrawal

The command selected only ev-public-review, explicit project/site/config, --expires=1d,
API-before-SPA routing and pinTag:true. It created an empty channel/unreleased version,
then Run rejected its tag update. Cloud Audit Logs recorded the combined-name error:
service valuation-api-public-preview (28 characters) + CLI tag fh-2bf2e8b7a6e0faa6
(19) = **47, exceeding 46**. No pin or Hosting release was published. No CLI patch,
shortened tag, unpinned fallback, service rename, redeployment or second build.

Removed the new service's allUsers binding and deleted the empty preview channel.
IAM propagation was not immediate: an early health probe still returned 200 despite
the empty policy. Later **both direct aliases returned 403**; withdrawal verified
**2026-10-21 08:44:31.114 UTC / 12:44:31.114 Asia/Dubai**. Private staging's complete
service JSON/IAM policy matched preflight exactly: revision valuation-api-staging-00001-2rk,
same image/configuration, no public grants, anonymous health 403.
Live Hosting still has zero releases; no preview channels or custom domains remain.

Generated URL: <https://kartikchaturvedi-website--ev-public-review-55e9alzx.web.app>,
**withdrawn, never a working calculator preview**. Actual channel creation/expiry:
October 21 08:40:58.031730007 / October 22 08:40:58.031730007 UTC
(12:40:58.031730007 Dubai each respective day); deletion superseded expiry.
Public-grant request began October 21 08:40:18.819 UTC and completed 08:40:20.383
(12:40:18.819–12:40:20.383 Dubai). Conservative manual deadline:
**October 22, 2026, 08:40:18.819 UTC / 12:40:18.819 Dubai**, earlier than Hosting expiry.
Early withdrawal satisfied it. Recording a deadline did not enforce it; no automation
was scheduled. Revocation does not cancel in-flight requests. Channel expiry alone
would not disable the backend.

### Verification, retained costs and next decision

**95 focused local tests passed: 56 frontend + 39 API/catalog/lifecycle/preview/
launcher/publication/preservation**, plus locked install (zero reported vulnerabilities),
TypeScript/Vite build and the resolved-site publication guard. An explicit unresolved
fixture still rejects deployment. No formulas/schemas/financial resources changed.

**Not performed:** hosted browser journey, full hosted API/CLI comparisons, company-bound
synthetic remote calculations, malformed/oversized probes, CDN/SPA/API-error/cache/CSP,
responsive/keyboard or console acceptance. The blocker occurred before these gates.
Earlier checks are not newly executed evidence. Sparse health probes establish access
only; no measured application request timings or cold-start claim.

Retained resources/costs: authenticated new service/revision/image above; source
gs://kartikchaturvedi-website-valuation-build-uscentral1/public-preview/source-02888f4454f4-1792571775732.tar.gz
(generation 1792571778921103); unreleased Hosting version
sites/kartikchaturvedi-website/versions/2bf2e8b7a6e0faa6, status CREATED, empty config.
No shared resource was deleted. Build, invocation, registry/source/Hosting storage,
transfer/logging and soft-delete retention can charge. Existing $10 alerts are not a
hard cap. No bot resistance, fair-availability, peak-memory or global-quota guarantee.

Next decision: authorize a **shorter isolated backend name**, e.g. valuation-api-preview
(21 characters), compatible with the CLI's 19-character tag, and separately scope
cleanup of the unused attempted service/version. Preserve private staging. The reviewed
digest can be reused if still appropriate; documentation push must not rebuild.
Recheck collisions/settings/site/live state, authorize a fresh one-day window, and
complete all hosted acceptance gates. No unsupported CLI modification is recommended.

Exact withdrawal commands for a future authorized reopening of these same resources,
using authenticated Cloud Shell gcloud and a local Firebase CLI:

    gcloud run services remove-iam-policy-binding valuation-api-public-preview \
      --project=kartikchaturvedi-website --region=us-central1 \
      --member=allUsers --role=roles/run.invoker
    curl --silent --output /dev/null --write-out '%{http_code}\n' \
      https://valuation-api-public-preview-378340095652.us-central1.run.app/health
    firebase hosting:channel:delete ev-public-review --site=kartikchaturvedi-website \
      --project=kartikchaturvedi-website --config=firebase.preview.json

Names/routes were verified; the binding/channel are already removed. Allow IAM
propagation and confirm direct/tagged URLs deny anonymous access and channel absence.
Do not delete another channel/shared resource. Netlify, DNS, live Hosting content and
portfolio remain unchanged. No forecasts/defaults were saved; all nine unset templates,
historical/frozen/source approvals, formulas and Phase 1 pause are preserved.
Temporary scripts/context/tooling/logs are removed after this checkpoint; normal CLI
credentials remain outside the repository. No hosted-preview PASS is implied.

Final checkpoint checks: **451 changed-document local links/anchors** resolved;
whitespace, exact staged scope and credential patterns were checked. All nine company
templates are byte-identical to the starting commit (six with 37 unset numerical
inputs, three with 111); protected financial/history/source files are unchanged.
The narrow site/config test adjustment is the only test change. No application fix
or repeat of the full historical/valuation suites; prior four local reviewed commits
plus this checkpoint are intended for the normal push after the integration checks.
