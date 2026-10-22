# Firebase calculator preview records

Subsequent October 22 [cost-control checkpoint](public-preview-preparation.md#configured-cloud-run-cap-and-local-client-controls--october-22)
configured a USD10 monthly project-wide Cloud Run cap (Configured; enforcement
not deliberately tested). It can pause this preview and private workloads, but
does not withdraw public access or extend the deadline below. Client lock/outage
changes are local only; this hosted image/frontend were not redeployed. Earlier
no-cap statements below describe their original release-time state.

The subsequent [combined portfolio preview](combined-site-preview.md) uses a
separate channel and the same existing pinned backend tag. It preserves the
calculator-only channel and this record's backend deadline; no Cloud Run change
or access extension was made.

## October 22 redesigned equity preview

**PASS for bounded hosted developer verification; anonymous preview active.**
[Open the fresh calculator preview](https://kartikchaturvedi-website--ev-public-review-fck0fjtl.web.app/).
The compact redesigned calculator, anonymous investor metadata and optional manual
equity/share workflow are now deployed. This supersedes the October 21 preview
below, preserving that record as history. No actual-company economic acceptance,
default forecasts, approved bridge/share selections or production readiness follows.
Phase 1 remains [paused](phase1-universe-pause-checkpoint.md).

**Manual backend withdrawal: October 23, 2026, 14:17:28.069 Asia/Dubai /
10:17:28.069 UTC.** Hosting expires at **14:17:35.195306922 Dubai /
10:17:35.195306922 UTC** that day. The earlier backend deadline is the intended
review end. No scheduler, reminder, automatic backend shutdown or hard spend cap
was configured. Hosting expiry does not revoke Cloud Run access.

### Old withdrawal and missed deadline

Starting clean `main` was `0f5200d300a6505b0e597403510d79bf7aed0bd1`, five commits
ahead of local `origin/main`, as expected. Initial clock check was October 22
**10:03:06 UTC / 14:03:06 Dubai**, after the old 09:04:19.869 UTC deadline.
An anonymous old-backend health request still returned 200. The deadline was
missed; this record does not backdate withdrawal or infer an exact cessation time.

Service policy inspection found only service-level `allUsers / roles/run.invoker`
and an enforced invoker check (`invokerIamDisabled=false`). Revocation began at
**10:04:58.651 UTC / 14:04:58.651 Dubai**. The expired-but-retained old preview
channel was deleted through the Hosting REST API; a subsequent read returned 404.
After propagation and transient network timeouts, anonymous **403** was confirmed
on the old default, project-number and tagged backend URLs by **10:07:05.987 UTC /
14:07:05.987 Dubai**, approximately 63 minutes after the old deadline. Requests
already in flight are not canceled by policy revocation.

Both private services' complete service JSON and IAM were snapshotted. Their known
default/project-number URLs denied anonymous requests. The later preview-only
deployment removed obsolete tag `fh-fc91aeb693b71112`; that retired URL now returns
404 rather than exposing the old image when the new grant is active.

### Traceable new release

| Binding | Verified value |
| --- | --- |
| Project / site / channel | `kartikchaturvedi-website` / `378340095652`; same default site; only `ev-public-review` |
| Clean pushed image/frontend source | `0f5200d300a6505b0e597403510d79bf7aed0bd1` |
| Remote build | `7a027296-ec96-4c29-94d6-a84e0a21ac22`, us-central1, SUCCESS |
| Build interval, October 22 | 10:13:32.385318862–10:14:05.022038 UTC / 14:13:32.385318862–14:14:05.022038 Dubai; not cold-start measurements |
| Immutable image | `us-central1-docker.pkg.dev/kartikchaturvedi-website/valuation-staging/valuation-api@sha256:b1a0f6d846a0af17afa0c98c36b9e3d808d64539b46c5d6361ff6c0d395331f8` |
| Backend revision | `valuation-api-preview-00002-kq7`; ready 10:15:28.281030 UTC / 14:15:28.281030 Dubai |
| Hosting version / pinned tag | `c2ae005fc1524503` / `fh-c2ae005fc1524503`, targeting exactly `valuation-api-preview-00002-kq7` |
| Hosting release | October 22 10:17:48.933 UTC / 14:17:48.933 Dubai |
| Anonymous service-only grant | Started October 22 10:17:28.069 UTC / 14:17:28.069 Dubai; completed 10:17:29.569 UTC / 14:17:29.569 Dubai |
| Deadline basis | At most 24 hours from grant-request start, not release completion; no implicit extension |
| Application artifact | Four files, 316021 bytes; `index-yPxQs3Sw.js`, `index-CJkQVHWF.css`, index and favicon; served bytes match local build |

The five local commits were reviewed and normally pushed to the existing `main`.
GitHub had zero workflows/hooks, no installed account GitHub Apps (browser check),
and no Pages deployment. Global/us-central1 Cloud Build trigger lists were empty.
The OAuth CLI could not inspect App installations, so its failure was not treated
as an empty inventory. No automatic deployment integration was added.

The new image was required because the old image predates `investor-case-v1/v2`.
One existing remote builder identity built the [allowlisted context](local-api-image.md#prepare-an-exclusive-allowlisted-build-context):
89 files, including the 84-entry private manifest, manifest itself and four build
inputs. Every source file matched the clean source commit. Context digest
`01d2286da4646d69a0712fad658719feddf7e8e2ce524e6a08e533ee92c410f9` is SHA256 of
canonical JSON sorted path/hash entries. Uploaded archive: 834996 bytes, SHA256
`c8fd186623f942f469c233d6e5ae7fc9f5a12ced62e2f40d29be9e02782cc78e`, pinned object
generation. Source object:
`gs://kartikchaturvedi-website-valuation-build-uscentral1/public-preview/source-0f5200d300a6-20261022T101259Z.tar.gz`.
No full corpus clone, credentials, frontend, tests or company case entered the
image context. Linux/amd64 build-time dependency and bundle verification succeeded.
The upstream base tag/wheels remain version-locked rather than a bit-reproducibility
claim. Documentation-only checkpoint changes cause no second build.

Only the preview service was updated. It retains 1 vCPU/1GiB, min 0/max 1 at both
levels, concurrency 1, gen2, 50s HTTP timeout, request-based CPU, startup boost off,
the existing runtime identity and one Uvicorn worker. Existing parser/result/child
deadline/cleanup/logging restrictions are unchanged; no request bodies or assumptions
are logged. Readiness/configuration, digest and anonymous 403 were verified while
private. The existing Firebase user ID token was rejected 401 for a private health
probe; private authenticated calculation was not claimed and no role was broadened
to obtain it. Functional execution was then verified through the authorized preview.

Firebase CLI 15.34.0 ran from a temporary directory with explicit project/site,
channel, one-day expiry, `--no-authorized-domains` and `pinTag`. A temporary config
only made the reviewed public/guard paths absolute; tracked config was unchanged.
API routing precedes SPA fallback. The 21-character service plus 19-character
generated tag is 40 ≤ 46; actual release and traffic verify the pin, not an unpinned
fallback. No new project IAM roles, service-account keys, APIs or infrastructure.

Credential-handling exception: the older installed CLI's account-list JSON
unexpectedly included token values in tool output. They were not copied into the
repository, assets or build. The existing CLI session was replaced with the same
account/scopes and its prior refresh token revoked; task authentication logs were
removed. Subsequent authenticated API calls kept tokens in memory. No credential
values are reproduced in this record.

### Newly performed hosted acceptance

Actual Chrome used the fresh Firebase origin. Each retained META/GOOGL/AAPL FY2025
selection began with 37 unset inputs and no inherited bridge/results. Synthetic
rates throughout: annual growth 10%, margin 20%, operating tax 25%, expense D&A 5%,
investment 10%, full-revenue WC cash requirement 2%; WACC 25%, terminal growth 5%.
All five terminal ratios were explicitly copied once as 20/25/5/10/2. These are
software test choices, not researched company forecasts or standing defaults.
The separate $100 demonstration was visibly labeled synthetic and also exercised.

Manual test bridge: assets USD100m, financing USD40m, claims USD10m and 20m issued
test shares; equity = EV + USD50m. Share dates were 2025-12-31 for META/GOOGL and
2025-09-27 for AAPL. Selected-population-only coverage, test class equivalence and
unresolved/omitted awards were explicitly chosen; no actual class rights or dilution
were authenticated. Qualifications stayed prominent.

| Newly observed path | Result |
| --- | --- |
| Direct entry / initial validation | Neutral unset state, focused missing-input guidance, direct rate entry, explicit terminal copy; EV without opening bridge or supplying analyst paperwork. |
| Annual refinement / replacement | META FY2028 growth edited to 12%; uniform 11% replacement canceled safely, then explicitly re-entered/confirmed. Other annual fields and terminal ratios preserved. |
| Operating / terminal independence | META annual margin changed to 21%, terminal stayed 20%; terminal margin later changed independently to 22%, annual margin stayed 21%. Both EV/equity staled on operating changes; fresh EV left prior equity stale. |
| Bridge-only edit | META assets 100m → 110m changed equity by exactly USD10m and left complete Stage B unchanged. Explicit per-share action required. |
| Anonymous metadata / notes | Generated case name/preparation timestamp; first runs had null notes. META later retained optional engineering-only notes. No authenticated analyst/rationale/cutoff was invented. |
| Required coverage / correction | Unassessed claims and missing date blocked equity with EV retained. AAPL zero shares returned linked positive-share guidance, focused shares and retained EV/entries. Correction recovered. |
| Signed / fractional output | AAPL financing USD300000m diagnostic produced equity −USD92.3657870379008bn and −4618.28935189504 USD per 20m issued test shares. A separate 0.0000001m-share diagnostic displayed 0.1 actual shares exactly, preserving the long negative output. These are artificial software stress inputs. |
| Responsive / keyboard | Desktop and 390×844 emulation: declarations expand, focus visible, date/amount/share units and unbounded award qualifications readable, long signed values contained. Representative screenshots captured in conversation. Not physical mobile/virtual-keyboard certification. |
| Switching / reload / console | Confirmed company switching discarded old bridge/results. Root reload cleared trial state. During entry, 22 console network errors were expected 422 validation responses; no application/CSP exception observed. Clean reload: zero messages. One non-error missing-autocomplete improvement notice remains. |

A sanitized temporary capture contained **15 successful runs, one canceled run
and one 422 zero-share rejection**. All 15 successful submitted cases matched the
real anonymous CLI's **entire JSON**; equivalent legacy analyst cases matched
complete Stage B/C components with intentionally different preparation metadata.
Nine Stage C results independently reconciled signed components, role subtotals,
EV → equity → denominator → per share using exact rational arithmetic. Absolute
tolerances: USD `1e-30` for equity/components, USD/share `1e-40` for division;
observed difference was zero. A temporary checker initially compared `0.20` with
`0.2` as text; its numeric assertion was corrected, with no engine/output change,
and the complete comparison passed. Canceled/rejected requests are not successes.

Fresh local release checks: **82 frontend tests, 113 focused Python checks**
(the prior 101-test scope plus image launcher, compiled-preview and publication
checks), production TypeScript/Vite build and artifact guard. No historical suite.
Remote timing/race/OOM/saturation tests were not performed; existing automated
lifecycle coverage keeps that attribution. Sparse request observations are not
cold-start, performance or load guarantees.

All four served app files match compiled bytes. API catalog/unknown routes return
JSON with no-store/nosniff, not SPA HTML. Malformed JSON rejects 422. Four private
source/case-path probes return only SPA index bytes. The version's six files are
the four app files plus Firebase's reserved `/__/firebase/init.js` and `init.json`;
no SDK was added and no private corpus/credentials were published. Static source
and credential-marker checks passed. All nine unset templates and financial/source/
approval artifacts are unchanged. Temporary captures, cases and outputs were
removed after recording the review.

Both private services' full configuration/revision/IAM remain identical to their
initial snapshots: staging `valuation-api-staging-00001-2rk`; failed attempt
`valuation-api-public-preview-00001-hdj`. All four known private-service URLs
returned anonymous 403. Live Hosting still has zero releases. No Netlify, DNS,
custom domains or separate portfolio changes; existing local review servers were
preserved. Footer/connection wording still refers to a local environment, a minor
known hosted-copy limitation. Manual declarations cannot prove economic completeness,
hidden non-overlap or complete claims/award coverage. This is qualified software
verification, not fully diluted fair value, a researched forecast or investment readiness.

### Withdrawal runbook for this release

**Owner must act by October 23, 2026, 14:17:28.069 Dubai / 10:17:28.069 UTC, or earlier.**
No recorded deadline enforces shutdown. Use an authenticated Cloud Shell for
gcloud; no local SDK or keys were installed. The following is the exact-resource
runbook, not a claim it was executed against the newly active release. This turn
verified the underlying policy revocation and channel deletion through REST.

```sh
gcloud run services remove-iam-policy-binding valuation-api-preview \
  --project=kartikchaturvedi-website --region=us-central1 \
  --member=allUsers --role=roles/run.invoker
```

The invoker IAM check is currently enforced. Inspect it at withdrawal; if disabled,
restore it on **this preview service only** using the documented
[`--invoker-iam-check`](https://docs.cloud.google.com/sdk/gcloud/reference/run/services/update)
flag before claiming denial. Do not alter either private service or project IAM.

```sh
gcloud run services update valuation-api-preview --invoker-iam-check \
  --project=kartikchaturvedi-website --region=us-central1
for url in \
  https://valuation-api-preview-ailnp3irra-uc.a.run.app \
  https://valuation-api-preview-378340095652.us-central1.run.app \
  https://fh-c2ae005fc1524503---valuation-api-preview-ailnp3irra-uc.a.run.app
do
  curl --silent --show-error --max-time 20 --output /dev/null \
    --write-out '%{http_code}\n' "$url/health"
done
```

Require anonymous 403 after propagation, not merely a successful IAM write. The
retired old tag should remain 404. If responses remain public, investigate effective
access and withdraw only this preview; do not reopen or extend the deadline.

Delete **only** `ev-public-review` if still present. This verified REST route avoids
the CLI deletion command's Firebase Auth-domain removal side effect. In authenticated
Cloud Shell, keep the token in memory and print only status:

```sh
python3 - <<'PY'
import subprocess
import urllib.request
import urllib.error
token = subprocess.check_output(['gcloud', 'auth', 'print-access-token'], text=True).strip()
url = ('https://firebasehosting.googleapis.com/v1beta1/projects/kartikchaturvedi-website/'
       'sites/kartikchaturvedi-website/channels/ev-public-review')
request = urllib.request.Request(url, method='DELETE', headers={'Authorization': 'Bearer ' + token})
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        print('Preview channel deletion HTTP', response.status)
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise SystemExit('Preview deletion failed: HTTP ' + str(error.code)) from None
    print('Preview channel already absent (404)')
PY
```

Then verify the channel is absent/unavailable, the three backend URLs deny access
and both private services remain private. Never delete the Hosting site or live
channel. Policy removal does not terminate already in-flight requests.

Retained resources/costs: the new image/source archive/Hosting version/revision and
tag; the older `28cf0f0…de9a471` image, source archive and old revision; unchanged
private staging and failed-attempt service/version; shared registry, source bucket,
identities and logs. No shared resource was deleted. Run/Hosting/network/log usage
and image/source/version storage can charge, including bucket soft-delete retention.
Max one instance and budget alerts are not hard spend caps. Cleanup is separate
reviewed work. No second build for this documentation checkpoint.

Final local checks: 495 changed-document local links/anchors, whitespace,
credential markers and exact seven-file documentation scope passed. Formulas,
intake schemas, examples, frozen/source/approval records and nine company templates
are byte-identical to the deployed source checkpoint (six ×37 and three ×111 unset
numerical inputs). Only release/status references changed after the image build.

## Earlier October 21 preview — historical record

The record below describes the earlier release and its original approval/checks.
Its old URL and active status are superseded by the verified October 22 withdrawal
and fresh release above; prior tests are not claimed as newly rerun.

**PASS within this bounded developer-test scope; preview is anonymous and active.**

[Open the calculator preview](https://kartikchaturvedi-website--ev-public-review-ztr805i5.web.app/).

**Manual backend withdrawal no later than October 22, 2026, 13:04:19.869 Asia/Dubai
/ 09:04:19.869 UTC.** Hosting expires at **13:04:55.672076339 Dubai /
09:04:55.672076339 UTC** that day. The effective window ends at the earlier backend
deadline. The project owner must monitor and withdraw manually; no scheduler,
reminder, automatic backend shutdown or hard spending cap was configured.
Hosting expiry alone does not disable Cloud Run. Do not extend this window implicitly.

This resumes the [failed-name checkpoint](public-preview-preparation.md#deployment-attempt-and-withdrawal--2026-10-21)
under explicit user authority for valuation-api-preview and a fresh one-day window.
Reviewed by Codex, October 21, 2026 (Asia/Dubai), starting clean main at
699561d7c3d5d25026785dcf5116dd7c76fcc244, synchronized with origin/main.
This is synthetic engineering verification, not actual-company forecasts, economic
acceptance, equity/share valuation, public-production certification or investment readiness.
Phase 1 remains [paused](phase1-universe-pause-checkpoint.md).

## Exact deployment and preservation bindings

| Binding | Verified value |
| --- | --- |
| Project / site | kartikchaturvedi-website / 378340095652; default Hosting site kartikchaturvedi-website |
| Backend | us-central1 / valuation-api-preview |
| Revision | valuation-api-preview-00001-mf4 |
| Reused immutable image | us-central1-docker.pkg.dev/kartikchaturvedi-website/valuation-staging/valuation-api@sha256:28cf0f0b8161ef39d0ccd169aee56621dd1544c622750c8357f31cc27de9a471 |
| Original image source / build | 02888f4454f47247946b7ddd57960073cbfdfe85 / 3f749624-8bfd-4819-85de-c09fe176da6d; **previous successful build, not rerun** |
| Suitability | Registry digest exists; API/frontend/image recipe and requirements are unchanged from that source. No rebuild or source upload this retry. |
| Direct backend | <https://valuation-api-preview-ailnp3irra-uc.a.run.app> |
| Hosting channel / version | ev-public-review / fc91aeb693b71112 |
| Release | 1792573507912000; October 21 09:05:07.912 UTC / 13:05:07.912 Dubai |
| Pinned traffic tag | fh-fc91aeb693b71112, targeting valuation-api-preview-00001-mf4 |
| Tagged backend | <https://fh-fc91aeb693b71112---valuation-api-preview-ailnp3irra-uc.a.run.app> |
| Anonymous access | Service-only allUsers / roles/run.invoker. Grant request started October 21 09:04:19.869 UTC / 13:04:19.869 Dubai; completed 09:04:21.439 UTC / 13:04:21.439 Dubai. Deadline uses the earlier request start. |
| Channel created | October 21 09:04:55.672076339 UTC / 13:04:55.672076339 Dubai |
| Frontend | Four application files, 291006 bytes; JS index-Dm91Ibhh.js and CSS index-BUsYcr5G.css, same hashes as the [keyboard record](narrow-keyboard-review.md) |

Before creating the service, inspected official Firebase CLI 15.34.0's fh- plus
version-ID tag format: 21-character service + 19-character tag = **40 ≤ 46**.
Cloud Run's validateOnly creation accepted this name with a representative
19-character tag before actual creation. The real deployment subsequently confirmed
the exact tag and revision. No CLI patch or unpinned fallback.

The service was initially authenticated, then received only its specifically
authorized service-level anonymous invoker binding. Retained 1 vCPU/1GiB, service
and revision min 0/max 1, concurrency 1, gen2, request-based CPU, startup boost off,
HTTP 50s, existing zero-project-role runtime identity, one Uvicorn worker and unchanged
request/parser/result/35s child/CPU/cleanup/logging limits. No assumption/body logging.
No new project roles, keys, APIs, Auth application, Analytics, database, build
submission, local Docker, domain or automatic-deployment integration.

Official CLI 15.34.0 was installed temporarily outside the repository, using existing
authentication. Deployment named explicit project/config/site, channel ev-public-review,
--expires=1d and --no-authorized-domains (no Firebase Auth domain synchronization).
API rewrite precedes SPA fallback, calculator at preview root; the release config
and Run traffic both point at the reviewed revision.
[Official pinning behavior](https://firebase.google.com/docs/hosting/cloud-run).

Both original private staging and the failed attempt were snapshotted before/after:
complete service JSON/IAM and project IAM unchanged, both anonymous health **403**.
Original staging remains valuation-api-staging-00001-2rk; failed attempt remains
valuation-api-public-preview-00001-hdj and private. Live Hosting still has zero
releases; no custom domain changes. No Netlify, DNS or separate portfolio changes.

## Actual hosted checks

Chrome used the deployed Firebase origin and compiled files, with a sanitized HAR
saved only outside the repository. Six successful browser requests were passed,
unchanged, to the ordinary local CLI; **all complete JSON objects matched**, including
numerical strings, submitted inputs, source bindings and limitations. This compares
two execution surfaces of the same engine, not an independent new arithmetic proof.

| Browser case — synthetic economics throughout | Full JSON / CLI | Observed HAR request time |
| --- | --- | ---: |
| Explicit synthetic $100 demonstration, fixture unchanged | PASS | 2429.513 ms |
| Demo growth 12% except period three 15%; terminal margin 31%, tax corrected to 20% | PASS | 2625.532 ms |
| META retained FY2025 revenue, flat synthetic annual rates | PASS | 2392.766 ms |
| META terminal margin independently changed 20% to 21% | PASS | 2382.436 ms |
| GOOGL retained FY2025 consolidated revenue, synthetic rates | PASS | 3143.374 ms |
| AAPL retained fiscal FY2025 revenue, synthetic rates | PASS | 2531.987 ms |

Company test rates: annual growth 10%, margin 20%, operating tax 25%, expense D&A 5%,
investment 10%, full-revenue WC cash requirement 2%, WACC 25%, terminal growth 5%.
All five terminal ratios were explicitly copied once as 20/25/5/10/2, except the
separate META terminal-margin edit. Demo retained its own fixture terminal
30/20/4/9/1 before the described edit. These convenient **test choices are not
researched forecasts, historical calibration, approved cases or permanent defaults**.
Anchors shown: META 200966m, GOOGL 402836m, AAPL 416161m USD. AAPL retained its
September 29, 2024–September 27, 2025 fiscal period rather than a calendar-year claim.
Company metadata identified Codex automated engineering review, current UTC
preparation times, synthetic scope and retained limitations; no actual-case approval.

| Workflow / boundary | Newly observed result |
| --- | --- |
| Catalog / selection | Three retained anchors, blank company assumptions on selection, separate explicitly synthetic $100 demo. |
| Entry and terminal independence | Quick entries, explicit apply and terminal copy, period-three refinement, independent terminal changes; other inputs preserved. |
| Confirmation keyboard | Safe Keep focus, two-button Tab cycle, Escape cancellation and restored Apply focus; explicit confirm. |
| Stale / recalculation | Edits showed STALE RESULT, original result retained as stale; explicit recalculation updated it. META year-five margin remained 20% when terminal margin became 21%. |
| Validation | One deliberate browser terminal-tax 125% returned linked 422/0%–100% guidance; corrected to 20% without lost entries. AAPL Check inputs returned calculation_performed=false before explicit Run. |
| Review | EV-only, USD millions, annual revenue/FCFF table and terminal dependence; no equity/share figure. |
| Narrow / keyboard | Actual Chrome 390×844 desktop emulation, contained result-table horizontal scrolling, readable controls, Tab focus visibly outlined and scrolled into view. Not physical-mobile/touch/virtual-keyboard or exhaustive accessibility testing. |
| Navigation / saving | Direct root navigation and root reload worked; reload returned blank company selection, no saved assumptions. Root is the only declared frontend route. |
| Console | Only the deliberate 422 network error during testing; clean reload showed zero console messages. No application/CSP exception observed. |

These sparse end-to-end timings are **not controlled cold starts, throughput or load
guarantees**. No adversarial load, remote deadline/OOM/abrupt-death or forced late-reply
test; prior host lifecycle tests retain their original attribution. Bounded cloud
query through October 21 09:18:37 UTC found zero ERROR-or-higher entries for this
service; not a general log/uptime guarantee.

Four affected local publication/config tests passed, including an explicit name-length
regression and unresolved-site rejection; production TypeScript/Vite build and artifact
guard passed. The prior 95 focused tests were **not repeated** because application
code/image are unchanged. No historical suite or company financial trial.

## Static/API publication review and limitations

All four served application files match local bytes. API catalog/unknown-route
responses remained JSON; unknown API 404, malformed JSON 422, one 256KiB+1 request
413, and declared cross-site request 403. All observed API responses have no-store
and nosniff. Root/fallback responses use no-store; hashed assets use immutable caching.
Source/document/environment/case path probes returned the same SPA index, not their
requested private bytes. No arbitrary source file route or credential in app assets.

Hosting's version lists **six files**, not four: the four application files plus
platform-generated /__/firebase/init.js and /__/firebase/init.json. Inspected field
names/project identity without printing or retaining their values. These are
standard reserved Firebase SDK configuration endpoints, unused by this frontend;
the Firebase project identifier/API key is public configuration, not a Cloud Run
credential. No Firebase SDK was added or loaded. The local four-file publication
guard does not bound Firebase's own reserved namespace.
[Reserved URLs](https://firebase.google.com/docs/hosting/reserved-urls),
[Firebase API-key scope](https://firebase.google.com/docs/projects/api-keys).

Minor existing copy limitation: title/footer still say Local and connection guidance
mentions the local API. Execution here is hosted; that wording was not redesigned
in this deployment scope. No material correctness/security defect was found in the
exercised paths. This is not production or economic validation. Anonymous direct/tagged
backend callers remain possible; CORS/Fetch Metadata are not authentication or bot
defense. Max one and $10 alerts are not total cost caps or distributed quotas.
Public full-result provenance and the existing API's equity-case support remain
the reviewed API contract even though this UI exposes only EV.

## Manual withdrawal and retained resources

**Deadline: October 22, 2026, 13:04:19.869 Dubai / 09:04:19.869 UTC.**
No automation enforces it. At or before that time (earlier if abuse/cost/correctness
requires), use authenticated Cloud Shell gcloud to remove only this service's grant:

    gcloud run services remove-iam-policy-binding valuation-api-preview \
      --project=kartikchaturvedi-website --region=us-central1 \
      --member=allUsers --role=roles/run.invoker

Then verify denial after IAM propagation on the default/tagged URLs, and delete only
this preview channel locally with the authenticated Firebase CLI:

    curl --silent --output /dev/null --write-out '%{http_code}\n' \
      https://valuation-api-preview-ailnp3irra-uc.a.run.app/health
    curl --silent --output /dev/null --write-out '%{http_code}\n' \
      https://fh-fc91aeb693b71112---valuation-api-preview-ailnp3irra-uc.a.run.app/health
    firebase hosting:channel:delete ev-public-review --site=kartikchaturvedi-website \
      --project=kartikchaturvedi-website --config=firebase.preview.json

Expect anonymous 403 after propagation, channel unavailable/absent and original
staging still 403. Earlier attempt demonstrated temporary 200 during IAM propagation;
do not equate policy-write success with effective denial. Revocation does not cancel
requests already in flight. If denial fails, inspect effective invoker grants and
withdraw only the new service under the authorized shutdown scope. Never change
original staging, the failed-attempt service, project-wide billing or shared identities.

Retained resources are separate:

- Active preview: valuation-api-preview / revision 00001-mf4, its revision tag and
  Hosting version fc91aeb693b71112. Service needs manual access withdrawal above.
- Failed attempt: private valuation-api-public-preview / revision 00001-hdj and
  unreleased CREATED Hosting version 2bf2e8b7a6e0faa6. Left private and untouched.
- Shared/reused artifact: one digest 28cf0f0…de9a471, original source archive
  gs://kartikchaturvedi-website-valuation-build-uscentral1/public-preview/source-02888f4454f4-1792571775732.tar.gz,
  existing registry/bucket, builder/runtime accounts and original private staging.
  No deletion or extra build/upload.

Ordinary Run invocation/startup/network, Hosting transfer/versions, registry/source
storage and logs can charge. Source soft-delete retention can preserve storage costs.
No hard-dollar claim; use existing budget/usage monitoring and withdraw early if needed.
Cleanup of retained versions/images/services is separate reviewed work, not blanket
deletion of shared resources.

Temporary HAR, cases, comparison outputs/scripts, SDK installation and task-generated
Hosting cache are removed after this checkpoint; normal interactive CLI credentials
remain outside the repository. No assumptions/results enter executable company cases,
templates or defaults. Financial formulas, source/frozen approvals and all nine unset
templates are preserved. Final documentation/configuration push causes no second
build or automatic deployment.

Final repository checks: 458 changed-document local links/anchors, whitespace, exact
staged scope and credential-pattern checks passed. Nine company templates remain
byte-identical (six with 37 unset numerical inputs and three with 111); no protected
financial/source/frozen/frontend/image files changed. Retry checks found no GitHub
workflow/webhook or regional/global Cloud Build trigger; the earlier signed-in account
inspection found no installed GitHub Apps. No additional integration was authorized
or added. A normal reviewed source/config/documentation push is the only Git action.
