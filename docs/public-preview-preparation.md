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

1. Obtain approval for one-day anonymous exposure of the **new service only**, direct
   URL access, bounded settings above, monitored cost/availability risk and shutdown
   authority. Identify an already existing Hosting site in this project read-only
   using an authenticated current Firebase CLI. If Firebase is not enabled or no
   suitable site exists, **stop** for separate scope; do not initialize/create one.
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

## Local verification and decisions remaining

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
