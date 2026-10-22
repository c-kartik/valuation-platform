# Combined portfolio and calculator preview

This isolated review publishes the existing portfolio at `/` and the approved
calculator at `/valuation/`. It does not migrate the live domain or Netlify site.
Phase 1 remains [paused](phase1-universe-pause-checkpoint.md). Financial formulas,
contracts, historical approvals and all nine unset templates remain unchanged.

## Assembly and local review

Use Node 22.12+, the existing `frontend/package-lock.json` installation and Python
3.12. No portfolio dependencies or build tooling are added. Both checkouts must be
clean, including untracked files, and match explicitly supplied full commit SHAs.
Ignored dependencies/build caches are not publication inputs. The builder reads
the ten portfolio files from Git objects, builds Vite with `--base=/valuation/`
into temporary storage, checks local references/fragments and writes an exclusive
external artifact. The output contains `public/`, `manifest.json` and a generated
`firebase.json`; only `public/` is uploaded. The manifest hashes every public file.
This records source/build bindings, not bit-reproducible dependency execution.

```sh
python3 scripts/assemble_combined_preview.py \
  --valuation /Users/kc/Projects/valuation-platform \
  --portfolio /Users/kc/Projects/Website/V3/kartikchaturvedi.com \
  --valuation-commit FULL_REVIEWED_VALUATION_SHA \
  --portfolio-commit FULL_REVIEWED_PORTFOLIO_SHA \
  --output /tmp/NEW-combined-artifact
python3 scripts/preview_combined_site.py /tmp/NEW-combined-artifact --port 8088
```

Start/reuse the compatible [local Python API](local-calculator-ui.md#scope-and-startup)
on loopback port 8000 first. Open <http://127.0.0.1:8088/>. The harness verifies the
manifest, confines static serving to the artifact and reuses the existing bounded
loopback proxy without forwarding cookies/authorization. Stop the harness with
Ctrl+C. It models the routes below, not Firebase/CDN infrastructure, reserved SDK
paths, generated 404 appearance or all HTTP normalization behavior. The default
calculator build/dev workflow and [standalone Hosting config](../firebase.preview.json)
remain unchanged.

## Route and publication boundary

| Request | Combined behavior |
| --- | --- |
| `/`, five original `.html` pages | Original portfolio HTML with one calculator navigation entry per page; existing styles, contact/content and relative links preserved. |
| `/featured`, `/project-pipeline`, `/work`, `/contact` | Explicit aliases to the corresponding HTML file; original `.html` URLs remain available. |
| `/style.css`, `/profile.jpg`, `/resume.pdf`, `/robots.txt`, `/sitemap.xml` | Byte-preserved assets except the small navigation wrapping addition to CSS. Production canonical/crawler URLs retained; no calculator sitemap entry. |
| `/valuation` | Anchored-regex 301 to `/valuation/`; a glob also matches the slash URL on Hosting and loops. |
| `/valuation/`, `/valuation/**` | Compiled calculator; exact assets before calculator-only fallback. Unknown subpaths (including nonexistent asset names) inherit that fallback. |
| `/api`, `/api/**` | First rewrite to existing public Cloud Run service; JSON API errors do not become HTML. |
| Unknown portfolio paths | Real 404; no global SPA fallback. |

The separate [combined configuration](../firebase.combined-preview.json) has
no-store defaults/API, immutable hashed calculator assets, nosniff and preview-only
noindex/nofollow headers. Portfolio Google Fonts and existing inline CSS require
their explicit style/font CSP allowances. No scripts/forms were present in the
portfolio. Ten portfolio files plus four calculator files are allowed; Git,
README, dependencies, JSON cases, private evidence, credentials and maps are denied.
Firebase may add its reserved SDK configuration endpoints; the app uses no SDK.

## Deployment guard and withdrawal

**Unchanged backend withdrawal deadline: October 23, 2026, 14:17:28 Dubai /
10:17:28 UTC.** No extension, scheduler or automatic backend withdrawal is provided.
Hosting expiry does not revoke Cloud Run anonymous access. The existing
[backend withdrawal runbook](firebase-public-preview.md#withdrawal-runbook-for-this-release)
remains authoritative.

Only deploy channel `combined-site-review` in project/site
`kartikchaturvedi-website`, using a supported current Firebase CLI, explicit
`--project`, generated `--config`, `--no-authorized-domains` and an expiry safely
before the deadline. Never run a live `firebase deploy`, change the standalone
channel, push either repository, or enable debug/auth output.

The approved service is `valuation-api-preview` in us-central1, revision
`valuation-api-preview-00002-kq7`, already tagged `fh-c2ae005fc1524503`. CLI 15.34.0's
reviewed `pinTag` implementation reuses an existing tag on the latest ready
revision without updating Cloud Run. **Before deployment verify that exact ready
revision/tag and fewer than ten tags; otherwise stop.** The CLI ignores a manually
supplied `run.tag`, so do not rely on that field as a pin. Verify the resulting
Hosting version's tag and unchanged complete service/IAM afterwards. No image
rebuild, service/revision/tag change or anonymous-access grant is authorized here.

To remove only the combined preview without Firebase Auth domain edits, use an
authenticated DELETE of the supported Hosting REST resource:

```text
https://firebasehosting.googleapis.com/v1beta1/projects/kartikchaturvedi-website/sites/kartikchaturvedi-website/channels/combined-site-review
```

Keep credentials in the normal external CLI store and access tokens in memory;
never log them. Do not delete shared versions, the standalone channel or backend.

## Future migration decisions

The subsequent [production backend/cost proposal](public-preview-preparation.md#production-backend-and-cost-policy--proposed-october-22)
records read-only billing verification and the staged launch plan. It changes
neither this preview nor its deadlines; production and billing actions remain pending.

Live-domain migration, DNS/certificates, the active portfolio Netlify push webhook,
production backend access/abuse/cost policy, longer-term hosting, canonical/sitemap
policy and production monitoring require separate decisions. The portfolio's
added `/valuation/` link requires this combined host; do not push its repository
or manually upload the changed portfolio alone to Netlify. Existing research
content is preserved, not independently fact-checked by this engineering review.

## Verification record

**PASS for bounded developer review, October 22, 2026.**
[Open the combined preview](https://kartikchaturvedi-website--combined-site-review-kwvkxedj.web.app/)
or [local combined review](http://127.0.0.1:8088/). Neither repository was pushed.

| Binding | Verified value |
| --- | --- |
| Initial valuation checkpoint | Clean `main`, `0a9282c843c9888a3adf159a7e051db118fe3fd6`, synchronized with local `origin/main`. |
| Initial portfolio checkpoint | Clean `main`, `85d928ee71cef30f202488008ef3e20d18c85107`, one ahead of local `origin/main`. Active Netlify push integration preserved. |
| Assembled valuation source | `faadd0d01d8cbc57dbe0c8fac4237a423970689a` (integration plus redirect correction). Subsequent documentation/screenshots do not change the artifact. |
| Assembled portfolio source | `a115327325754cb741b696fa115f38a30e63c866` (navigation link and narrow-screen wrapping only, plus README). |
| Build | Node 22.14.0, TypeScript + Vite 8.3.4, explicit `/valuation/` base; 14 files, 1,384,015 bytes. All ten portfolio files equal committed Git bytes. |
| Calculator assets | `index-yPxQs3Sw.js`, `index-CJkQVHWF.css`; unchanged JS/CSS from the standalone release, with subpath references in the index. |
| Final Hosting version | `5f2dbbeabcb9b288`; site/project `kartikchaturvedi-website`, channel `combined-site-review`. |
| Final release | `1792667448367000`, October 22 **11:10:48.367 UTC / 15:10:48.367 Dubai**. |
| Actual combined expiry | October 23 **09:10:39.991846463 UTC / 13:10:39.991846463 Dubai**. CLI `--expires 22h`; no extension of backend access. |
| Backend routing | Existing tag `fh-c2ae005fc1524503` → `valuation-api-preview-00002-kq7`, us-central1. Complete service/IAM snapshots unchanged. Existing immutable image retained; no rebuild. |

The first combined release (`b577f1c06457e3fd`, 11:06:51.460 UTC) revealed a
Hosting-specific redirect loop: glob `/valuation` also matched `/valuation/`.
Only the combined channel was deleted via REST, with absence verified 404. An
anchored regex replaced the glob; the harness now consumes that regex. The clean
corrected source was rebuilt and redeployed to the same channel name, with a new
URL. Both slash forms then passed on Hosting. Earlier Hosting versions/storage
are retained; no shared resource was deleted. The retired first URL is not the
review URL above. The local harness alone had not exposed Firebase's glob matching.

Newly executed checks (earlier standalone checks were **not** rerun or reattributed):

- **18 focused Python tests passed**: eight new assembly/publication/routing tests
  and ten existing compiled-preview/publication regression tests. The eight new
  tests passed again after the redirect correction. Two TypeScript/Vite builds
  passed, one for each source checkpoint; no financial/full historical suite.
- Every local HTML link, asset and fragment resolves within the publication
  allowlist. All **14 local and final hosted files** match manifest SHA256 hashes.
  Root, four extensionless aliases, `.html` pages, slash redirect, calculator
  fallback/refresh, unknown portfolio/private-path 404 and API routing passed
  HTTP checks. API catalog and unknown-route responses are JSON with no-store.
- Actual Chrome visited all five pages locally and on Hosting, at desktop and
  approximately **390×844**. The portrait, preserved Google Fonts/styles, nav,
  existing mailto/LinkedIn targets and résumé were checked; no messages/contact
  forms were submitted. The one-page PDF rendered locally and on the corrected
  hosted release and its bytes matched. New navigation entered `/valuation/`;
  direct visits/refresh worked. Mobile input/terminal/action layout was inspected.
  This is desktop emulation, not physical mobile or full accessibility acceptance.
- Hosted **synthetic EV and equity/share** requests matched the local CLI's
  **complete JSON**, two successful runs total. Synthetic anchor USD100; annual
  growth/margin/tax/D&A/investment/WC percentages **10/20/25/5/10/2**, WACC **25%**,
  terminal growth **5%**, explicit terminal ratios **30/20/4/9/1**. These are the
  existing demonstration's test choices, not company forecasts or new defaults.
  Bridge: USD12 assets, USD20 financing, USD3 other claims, four issued synthetic
  common shares at 2025-12-31, single-class declaration, selected-population-only
  coverage and explicitly unresolved/omitted awards. Independent exact rational
  checks reconciled EV **77.577060352** → equity **66.577060352** →
  **16.644265088 USD/share**, tolerance `1e-40` for division, observed difference zero.
  Full Stage B was identical across scopes. No actual-company valuation was run.
- Tax **150%** produced specific correction guidance; restoring **25%** recovered.
  Operating edits staled the EV/equity workflow. Reload cleared trial state.
  Clean calculator console: zero messages; no application/CSP exception observed.
  The portfolio has no favicon, producing an incidental `/favicon.ico` 404;
  this pre-existing missing asset was left unchanged. Chrome also retains the
  calculator's non-error autocomplete improvement notice.
- Read-only before/after comparisons: complete public/private Cloud Run service
  JSON/IAM, standalone channel (including its expiry/version), Firebase live
  channel and zero live releases unchanged. Live-domain and existing Netlify
  hostname homepage response bytes remained identical. This is a bounded
  behavior check, not a claim to audit all provider configuration. No DNS or
  Netlify integration/configuration operation was performed.
- The final Hosting inventory has the 14 reviewed files plus Firebase's two
  reserved `/__/firebase/init.js` and `init.json` endpoints. No SDK was added or
  consumed. Publication checks found no unintended private/credential files.
  All nine company templates retain original bytes: six × 37 unset inputs and
  three scenario templates × 111, with bridge/share decisions still unresolved.
  Financial/source/history files and the standalone config remain byte-unchanged.

Representative screenshots: [portfolio desktop](images/combined-preview/portfolio-desktop.png),
[portfolio 390×844](images/combined-preview/portfolio-mobile.png),
[calculator desktop](images/combined-preview/calculator-desktop.png) and
[calculator 390×844](images/combined-preview/calculator-mobile.png). The calculator
screenshots show neutral initial state; temporary cases, CLI outputs and sanitized
request captures were removed after comparison. No actual-company case was saved.

The combined local server uses PID **2855**, port **8088**; the compatible existing
API uses PID **85874**, port **8000**. The unrelated existing Vite server was
preserved. Verify process identities before stopping with `kill 2855 85874`.
The external review artifact/log/process note remains under the directory named
in `/tmp/combined-site-review-current`; retain it while reviewing, then stop the
combined server before removing that task-owned directory. CLI installation,
cloud snapshots and trial files were temporary, not repository/public artifacts.

**Backend withdrawal remains October 23, 14:17:28 Dubai / 10:17:28 UTC.** The
combined preview expires earlier, but direct backend and standalone access still
need the existing manual withdrawal. No automated shutdown has been added.
