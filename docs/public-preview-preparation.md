# Anonymous EV preview — local preparation and abuse review

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
