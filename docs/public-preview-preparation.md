# Anonymous EV preview — local preparation and abuse review

> **Current: the shorter-name retry is deployed and verified within its bounded scope.**
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
