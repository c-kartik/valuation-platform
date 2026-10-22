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
| `/valuation` | 301 to `/valuation/`. |
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

Live-domain migration, DNS/certificates, the active portfolio Netlify push webhook,
production backend access/abuse/cost policy, longer-term hosting, canonical/sitemap
policy and production monitoring require separate decisions. The portfolio's
added `/valuation/` link requires this combined host; do not push its repository
or manually upload the changed portfolio alone to Netlify. Existing research
content is preserved, not independently fact-checked by this engineering review.

## Verification record

Deployment bindings, newly executed checks and local process details will be
recorded after verification. Earlier standalone tests remain attributed only to
their [original release](firebase-public-preview.md).
