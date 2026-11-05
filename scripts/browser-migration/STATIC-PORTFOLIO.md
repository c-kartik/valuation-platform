# Static portfolio review artifact

These additive Node tools read the existing portfolio checkout and a separately
built browser-only application. They do not modify the portfolio or Python,
publish, log in, change DNS, or change GCP resources.

Build the browser-only frontend first using its documented browser build command.
The default build input is `frontend/dist-browser`; it must use `/valuation/` as
its asset base and fix the transport to browser execution. Then run from this
repository:

```sh
node scripts/browser-migration/assemble-portfolio.mjs
node scripts/browser-migration/validate-portfolio.mjs
node scripts/browser-migration/serve-static.mjs /Users/kc/Documents/Codex/2026-11-05/valuation-platform-local/outputs/browser-portfolio/public 5200
```

While that loopback server is running, use a second shell:

```sh
node scripts/browser-migration/validate-portfolio.mjs /Users/kc/Documents/Codex/2026-11-05/valuation-platform-local/outputs/browser-portfolio http://127.0.0.1:5200
```

Open `http://127.0.0.1:5200/valuation/` for the modern workspace. The existing
calculator remains at `/valuation/calculator.html`. The server binds only to
loopback and has no API, proxy, functions or data refresh. Its read-only
`/__static_health` metadata reports static mode. The default port is 5200.

Assembly options are `--portfolio`, `--build`, and `--output`, each an absolute
directory. Output must be outside either source checkout and must not already
exist: each release is an exclusive directory. Only its `public/` folder may be
uploaded. `release-manifest.json` stays outside public and records source commit,
working-tree state, file source paths, lengths and SHA256 hashes. A dirty source
is recorded honestly rather than misrepresented as a committed release. Build
contents are copied, not rebuilt, by the assembler.

The exact ten portfolio inputs are `index.html`, `featured.html`,
`project-pipeline.html`, `work.html`, `contact.html`, `style.css`, `profile.jpg`,
`resume.pdf`, `robots.txt`, `sitemap.xml`. They are preserved byte for byte.
The browser build accepts reviewed web asset extensions and refuses symlinks,
hidden entries, source maps and functions/dependency directories. No test fixture
or source repository is copied. The verifier checks exact manifest membership,
hashes, local HTML/CSS references, backend hostnames and recognizable secret
patterns; it is not a general proof that arbitrary content is safe to disclose.

Netlify `_redirects` and `_headers` are generated. No global SPA fallback exists.
`/valuation` redirects to `/valuation/`; legacy `/valuation/workspace` and
`/valuation/workspace/` map to the same entry. The current application uses no
other path-based client routes, so broad wildcard rewrites are unnecessary and
would mask missing JavaScript/JSON/CSS as HTML. Missing files and unrelated
portfolio paths stay genuine 404s. New client paths require explicit review and
matching static-server/Netlify rules. Headers use same-origin connections and
workers plus the portfolio's existing Google Fonts, noindex/nofollow and
no-store for this review artifact; hashed application assets are immutable.
Review crawler/cache policy separately before a production release.

## Publication prerequisite and existing-site draft

Read-only investigation on November 5, 2026 found the live portfolio on Netlify,
an active GitHub webhook including push events, two local unpublished portfolio
commits, no installed Netlify CLI or verified local site binding, and an
unauthenticated Netlify browser session. The actual Netlify site ID, account plan,
preview protection and automatic production deployment behavior remain unknown.
Do not push the portfolio to discover those behaviors. Existing Firebase configs
include backend rewrites and must not be used for this static artifact.

After the account and existing site have been verified, a deliberate draft can
use the following shape with the current supported CLI:

```sh
netlify deploy --site VERIFIED_EXISTING_SITE_ID --dir REVIEWED_OUTPUT/public --no-build --json
```

Netlify documents draft deploys as the default:
https://cli.netlify.com/commands/deploy/

Do not add production flags, create a new site, bypass authentication, or assume
a preview URL is private. The tools here perform none of those actions. Retain
the existing Python/GCP deployment as a switchback; retirement is deferred under
the user's preservation requirement.
