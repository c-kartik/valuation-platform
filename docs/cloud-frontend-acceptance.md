# Compiled frontend → authenticated Cloud Run review

## Result and artifact binding

**PASS within the tested integration scope**, reviewed by Codex on 2026-10-20
(Asia/Dubai). This is developer verification with synthetic assumptions, not human
investor acceptance, financial approval or public-launch acceptance. Phase 1 stays
[paused](phase1-universe-pause-checkpoint.md).

Starting clean `main`: `0211a30b085ba59f468f96b6fcb1374ce6d7c964`, one documentation
commit ahead of `origin/main` at `ebf6139df600580f6aa92cd759a8a67fc7aea823`.
Frontend/API source matches that pushed source; the intervening commit is documentation.
No frontend, API, engine, schema or financial-resource changes were needed here.

| Artifact | Verified binding |
| --- | --- |
| Existing backend | project `kartikchaturvedi-website`, region `us-central1`, service `valuation-api-staging` |
| Revision / traffic | `valuation-api-staging-00001-2rk`, 100% |
| Image digest | `sha256:5b5421c09fc2611b1b1315fa032a982f3cf53bc02c98d26cc5c70f400e608bd0` |
| Build | Node 22.14.0 / npm 10.9.2; locked `npm --prefix frontend ci`, TypeScript/Vite production build |
| Compiled files | 4 files / 290180 bytes; no HMR, source maps or private resources |
| JS SHA256 | `b5d08cb94b332ec6b32c3319d0548dde434dea0991b4147f7be88b4dbddac004` (`index-BxBjsvt2.js`) |
| CSS SHA256 | `24137cd0ef38cc09040410e9ec25ec2f65c0ebfeca5e5c1d3579eee4a0bc0a57` (`index-DX66fahC.css`) |

The [deployment record](cloud-staging-deployment.md) remains authoritative for the
original build and Linux-image checks; those checks were **not rerun** here.
Service configuration remained 1 vCPU/1GiB, min 0/max 1, concurrency 1, HTTP 50s,
with unchanged API limits and 35s calculation deadline. Service IAM had no bindings;
project IAM had no allUsers/allAuthenticatedUsers principals. Anonymous health
returned **403 before and after** testing. No IAM, build, revision or deployment change.

## Reproducible localhost arrangement

No local SDK/credentials initially existed. The user subsequently authorized a
temporary [official Google Cloud CLI installation](https://docs.cloud.google.com/sdk/docs/downloads-versioned-archives)
and interactive login. SDK 590.0.0 and its [official Cloud Run proxy](https://docs.cloud.google.com/sdk/gcloud/reference/run/services/proxy)
0.5.2 were used outside the repository. Authentication
used the existing authorized human account; no service-account key, role grant,
browser token field, explicit token file or token output. An SDK component installer
attempted an optional system Python installation; it was stopped at the sudo prompt,
without a password or system Python installation. Existing Python 3.12.3 ran gcloud.

With an authenticated local gcloud available, from the repository root:

```bash
gcloud run services proxy valuation-api-staging --project=kartikchaturvedi-website --region=us-central1 --port=8000
npm --prefix frontend ci
npm --prefix frontend run build
python3 scripts/preview_cloud_frontend.py
```

Open <http://127.0.0.1:4173/>. Confirm the official proxy listens on **127.0.0.1:8000**,
not a network interface. Google credentials stay in that proxy. The
[preview harness](../scripts/preview_cloud_frontend.py) serves only build-file paths
and forwards only catalog/validate/run routes to that fixed loopback endpoint.
It has no target URL/path argument, source-directory route or SPA file fallback.
Host/origin checks and a same-origin CSP restrict browser use; cookies/auth headers
are not forwarded. API responses are no-store, status/body/content type preserved.
Request body: 256KiB; socket read: 10s; upstream socket timeout: 48s; response: 2MiB.
These are engineering bounds, not a public admission/authentication design.

The committed harness logs no request bodies/tokens. A temporary, explicitly
instrumented subclass captured **synthetic** submitted JSON/full responses outside
the repository solely for comparisons, then was removed. No Google credentials
were in those captures. Browser Network showed only the local harness for application
requests: document, JS, CSS, favicon, catalog and calculation. Inspected request
headers had no authorization/cookie; response headers contained only the harness's
safe projection. Compiled asset inspection found relative `/api/v1` calls and no
credential/private-file/cloud-target markers.

## Browser tasks and comparisons

Chrome desktop and a 390×844 emulated viewport used actual compiled assets and the
existing authenticated cloud revision. Safari's initial catalog load also succeeded;
the walkthrough moved to Chrome to avoid concurrent Safari focus changes.

| Task | Newly observed result |
| --- | --- |
| Catalog / history versus demo | PASS: three retained FY2025 anchors, source/date limitations and separate explicitly synthetic $100 demonstration. Company selection starts unset; nothing persisted after intentional reload. |
| Missing/invalid input | PASS: unset META returned bounded field-linked 422 errors; `10%` rejected locally; AAPL annual tax 125% returned a 0%–100% diagnostic. Corrections preserved other inputs. |
| Compact / annual / terminal edits | PASS: explicit six-row apply, populated-row replacement confirmation, explicit terminal copy, independent annual refinements, Varies by year and stale-result notices. META year-five margin 21% left terminal margin 20%. |
| Review / traceability | PASS: USD millions, unrounded USD labels, annual components, EV reconciliation, terminal dependence, submitted rationale/limitations and fiscal-end/later-filed notice. EV expressly excludes equity/share. |
| Signed cash flows | PASS: negative AAPL annual/terminal probe retained negative FCFF and EV, with negative-EV ratio interpretation. No clamping. Zero/over-100% and rounding remain newly executed automated coverage. |
| Connection recovery | PASS: stopped only the local proxy; browser showed service/retry guidance with inputs preserved. Restarted proxy; identical-request retry succeeded and matched CLI. |
| Company switching / late responses | PASS for explicit discard and blank new-company state. A requested switch began during a repeat, but cloud response finished before discard confirmation; this did **not** force a late reply. Obsolete/out-of-order safety passed automated tests. |
| Narrow / keyboard | 390×844 view showed contained annual-table scrolling and readable compact controls. Desktop Tab reached Apply then margin; keyboard edit/stale/discard passed. DevTools focus interfered with the narrow keyboard probe, so narrow keyboard progression is **not certified**. Not exhaustive accessibility/device testing. |
| Console | Deliberate 422s and stopped-proxy 502 were expected. An Adblock `Extension context invalidated` error was observed; no application exception. Clean reload + successful demo repeat: zero console messages. |

Temporary engineering rates: annual growth **10%**, margin **20%**, operating tax
**25%**, expense D&A **5%**, investment **10%**, full-revenue WC cash requirement
**2%**, WACC **25%**, g **5%**. Each company explicitly copied terminal
20% / 25% / 5% / 10% / 2%. These deliberately convenient test inputs are **not
researched forecasts, historical calibration, economic scenarios or company defaults**.
Metadata identified Codex as preparer and used the browser's current-UTC action;
limitations disclosed engineering-only inputs and retained historical unknowns.
The unchanged demonstration kept its independent fixture terminal assumptions.

| Retained anchor | Initial EV, USD millions | Edited EV, USD millions |
| --- | ---: | ---: |
| META: 200966000000 USD; calendar FY2025, t0 2025-12-31 | 100224.02 | 104402.23: FY2028 growth 15%, FY2030 margin 21% |
| GOOGL: 402836000000 USD; calendar FY2025, t0 2025-12-31 | 200898.88 | 207607.19: FY2028 growth 15% |
| AAPL: 416161000000 USD; 2024-09-29–2025-09-27, t0 2025-09-27 | 207544.21 | 214474.42: FY2028 growth 15% |

Initial contribution: 44.44% each; edited META: 44.60%; edited GOOGL/AAPL: 44.96%.
Negative AAPL probe deliberately replaced annual growth with flat 10%, margin −10%,
D&A/investment/WC with zero and explicitly copied those terminal ratios; tax/WACC/g
unchanged. EV **−259430.27m**, contribution **44.44%** with the negative-EV warning.
Separate synthetic $100 demo: **0.00007758m / 64.29%**. All are engineering outputs.

**11 successful captured browser runs (eight distinct input cases, three repeats)
matched ordinary local CLI full parsed JSON**, including precision, inputs,
provenance and limitations. Four successful browser validation submissions passed
validation-only CLI; two invalid submissions also failed CLI. The local proxy outage
was a separate 502, not a failed financial-input check. Input bytes stayed unchanged.
An independently structured `Fraction` oracle passed **682 exact equalities**
for revenue/EBIT/tax/NOPAT/D&A/investment/WC/FCFF, discounts/PVs, terminal components,
terminal value and EV. Independent Decimal HALF_EVEN display calculations matched
USD-million scaling/contribution. It did not call engine functions. Actual screenshots
of reconciliation, narrow layout and the local Network route were emitted in chat;
no screenshot assets or executable company case were added.

## Timings, cloud checks and limits

- First observed authenticated health after idle: **7982.290ms**. A new-instance
  log occurred at 14:08:40 UTC; Monitoring's one nonempty startup observation in
  14:08–14:09 was **7286.156ms**. This associates the initial observation with startup,
  not a controlled cold/warm benchmark or proof all request time was startup.
- Harness-to-proxy/cloud successful run times: **2311.954–4565.685ms**; first demo
  3332.917ms, repeat 2664.936ms; repeated edited GOOGL 2553.588/2364.342ms; negative
  AAPL 4565.685ms, recovered identical retry 2808.228ms. Sparse sequential observations,
  not representative load or latency guarantees.
- Measured demo repeat: browser Network **2.73s** total, waiting **2.69s**;
  harness upstream **2664.936ms**; corresponding Cloud Run request log **2.360125440s**
  at 14:23:26.973369 UTC. These measure different boundaries, not click-to-paint time.
  Clean browser load reported DOMContentLoaded 514ms / load 596ms / network finish 879ms.
- Direct official-proxy probes reached Cloud Run: malformed JSON **422 / 270.634ms**;
  262145-byte body **413 / 952.162ms**. No pathological timeout/load requests.
- Bounded cloud-log query: 28 rows / 22 HTTP entries, zero ERROR-or-higher at that
  query; a later request query confirmed the demo repeat. Monitoring returned 16
  nonempty minute memory observations, mean utilization approximately **5.11%–6.04%**.
  Empty distribution intervals were excluded. This is **not peak RSS or a memory bound**.
  No forced deadline, abrupt death or kill/reap test was conducted in Cloud Run.
- Busy/deadline, child cleanup, cancellation and late-reply cases passed **host
  automated tests**; no claim those fault paths were forced in the cloud/browser.

## Newly executed checks and final boundary

```bash
npm --prefix frontend ci
npm --prefix frontend run build
npm --prefix frontend test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.api.test_frontend_preview -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.api.test_cases tests.api.test_catalog tests.analyst.test_preparation_preservation -v
git diff --check
```

**84 focused tests passed: six harness + 54 frontend + 19 API/catalog + five
preservation.** The six harness tests were repeated after final error/framing
hardening; other unchanged checks were not repeated. Locked install audit: zero
vulnerabilities. No full corpus suite or rerun of earlier 174 valuation tests.
No material application defect or local frontend/API fix. Harness tests cover exact
file exposure, origin/host, route/body/framing bounds, response fidelity, dropped
credentials, timeout/unavailable/malformed upstream and oversized response behavior.
441 local links/anchors, whitespace and staged scope were checked. All nine templates
remain byte-identical: six × 37 unset; three × 111; equity selections unresolved.
Engine/formulas, source approvals, historical/frozen artifacts and portfolio untouched.

The final committed harness was also started without capture instrumentation and
smoke-checked for static/catalog routing and private-path rejection. All temporary
inputs/results/captures, comparison helpers, SDK/configuration/credential directory
and proxy/harness processes were removed. No persistent local SDK/profile change,
saved actual case, cloud resource/IAM change, push, redeployment, keep-warm job,
Netlify/DNS or live-website change. The review commit remains local.

Next bounded step: decide **who may access a Firebase preview** and how an authorized
browser reaches the IAM-protected API, then scope preview routing/authentication and
its tests. This localhost proxy is not a hosted-authentication solution. Do not make
Cloud Run public or add a Firebase rewrite by implication. Anonymous exposure/abuse,
cost/load limits and production/domain migration remain separate decisions.
