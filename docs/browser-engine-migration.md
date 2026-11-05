# Parallel browser valuation engine

November 5, 2026, Asia/Dubai. Status: local implementation and validation complete
within the recorded checks; external publication and actual phone-hosted review
remain OPEN. The user's controlling instruction is to preserve Python unchanged
while building a JavaScript alternative, retaining the option to switch later.

The user subsequently confirmed the intended ongoing architecture: keep data
retrieval/preparation in the unchanged Python pipeline and trigger it manually
on the laptop; export reviewed static data for the browser JavaScript engine.
A Node.js rewrite of SEC acquisition is not required. Neither website valuation
calculations nor this refresh workflow requires a GCP backend. Existing GCP
resources are not retired by this decision alone.

The user subsequently requested JavaScript as the default. Normal development
and builds now execute on-device from the verified dataset, without an API proxy
or fallback to Python. Python execution is an explicit opt-in; its source and
manual preparation workflow remain unchanged.

## Preserved boundaries

- No existing Python file was edited. `scripts/browser-migration/python-source-baseline.json`
  pins all 396 tracked Python files; `verify-assets.mjs` checks each byte digest.
- Python acquisition, normalization, financial policies, API and the supervised
  8135/5195 environment are retained. No GCP resource, IAM, billing, DNS, live
  portfolio deployment or webhook was changed. Retention is not a claim that
  cloud costs stopped or that current cloud state was audited.
- Pre-existing untracked follow-up folders remain excluded from this work.
- Original source facts and company-resolution policies remain unchanged. No
  source corpus expansion, new economic treatment or fresh SEC acquisition.

## Twelve-step disposition under the preservation instruction

| Step | Outcome |
| --- | --- |
| 1. Scope and baseline | Captured unchanged Python digests and independent API reference requests/results. |
| 2. Portfolio hosting audit | Live domain identified as Netlify; active GitHub webhook and two unpublished local commits observed; account/site configuration still requires login. |
| 3. Browser data | Fifteen hashed static data/metadata files; explicit GET route map, source-rich anchors and unchanged issuer policies. |
| 4. TypeScript engine | Operating forecasts, terminals, equity, FCFE, analyst conventions, scenarios, sensitivities and reverse DCF implemented independently of Python. |
| 5. Equivalence | 128 default/perturbed/rejected reference cases; full intermediate and final output comparisons, exact proof fractions. |
| 6. Worker execution | Disposable workers; abort/deadline termination, structured errors; six transport tests. |
| 7. UI transport | Same UI/shape checks; JavaScript default; explicit Python opt-in; no automatic cloud fallback. |
| 8. Portfolio assembly | Static portfolio plus `/valuation/`, legacy calculator, data and worker assets; route/hash/MIME checks; no API/functions. |
| 9. Hosted review | Prepared locally; external Netlify draft is pending existing-account access and verified site/protection settings. |
| 10. Release workflow | Documented build, integrity, test, assembly, review, release and rollback; live publication pending step 9. |
| 11. Python data migration | Not required under the confirmed architecture: retain Python acquisition/preparation and run it manually on the laptop; export reviewed static datasets to the JavaScript site. |
| 12. GCP retirement | Superseded by preservation/switchback requirement: retain existing cloud resources; no deletion or cost-elimination claim. |

## Choosing execution

In `frontend/`, using the repository-required Node runtime, ordinary development
now defaults to JavaScript:

```sh
npm run dev
```

The already-running main workspace at `http://127.0.0.1:5195/workspace/` picks up
the default. A separately launched ordinary server uses the configured port5173.
To run a second browser-only frontend on5196:

```sh
npm run dev:browser
```

Open `http://127.0.0.1:5196/workspace/`. Neither server needs Python to calculate.
There is no silent retry through Python. To explicitly use the retained local
Python API on8135 with a separate frontend on5197:

```sh
VALUATION_LOCAL_API=http://127.0.0.1:8135 npm run dev:python
```

```sh
npm run build:browser
```

Builds `frontend/dist-browser` with `/valuation/` asset paths and the browser
transport fixed on. Passing `?engine=python` cannot enable a backend in that
static artifact. Ordinary `npm run build` also uses JavaScript, with root-relative
asset paths in `dist/`. `npm run build:python` explicitly builds the API-backed
alternative into `dist-python/`. Choosing a deployed Python service requires a
separate explicit deployment/configuration; no cloud credentials enter the UI.

## Financial implementation

The TypeScript engine has no network or filesystem dependency. It receives
validated JSON declarations plus a verified data package. Decimal amounts stay
strings at boundaries. Isolated Decimal constructors prevent other UI libraries
from changing precision or rounding. Annual computations, terminals, financing,
claims and share denominators follow the retained approved Python conventions.

Reverse DCF keeps five-year/Gordon eligibility and uses BigInt exact rational
Bernstein derivative certification, 80-digit bounded bisection and fresh
50-digit forward verification. Uncertified, flat, unreachable and iteration-limit
results do not expose approximate successful solutions. Terminal comparisons do
not turn unsupported nonpositive-EBIT exit cases into values.

FCFE does not deduct debt twice. Alphabet's consolidated historical proxy,
separate minority claim, investment containment, share-class assumptions and
existing qualifications remain explicit. Apple and Meta retain their own source
histories and adopted treatments. Historical and forward bases remain distinct.

## Data and integrity

`frontend/public/browser-data/manifest.json` maps each existing supported GET
route to a static JSON asset and SHA256. Build configuration embeds the manifest
digest; the browser checks it and each loaded file before using data. Runtime
public assets exclude parity fixtures, research folders, private local paths and
credentials. Versioned data are downloadable by visitors; they are not secrets.

From the repository root, with the existing API running:

```sh
node scripts/browser-migration/export-baseline.mjs
node scripts/browser-migration/export-extra-parity.mjs
node scripts/browser-migration/verify-assets.mjs
```

These are explicit reference-refresh tools, not background data acquisition.
The immutable Python baseline prevents silently blessing later source changes.
Review data/fixture changes, rerun parity and rebuild before publishing a refresh.
Fresh filings cannot silently replace approved company policies. The browser
does not retrieve SEC filings or hold API keys. Live market reconciliation is
explicitly unavailable in browser mode; no stale/current price is invented.

## Validation

```sh
cd frontend
npm run test:browser -- --maxWorkers=1
npm test -- --maxWorkers=2
npm run build
npm run build:browser
npm run build:python
```

The recorded full frontend run passed 451 tests (309 pre-existing plus 128 parity,
six transport, four integrity and four validation checks). Baseline cases include every supported issuer with
Bear/Base/Bull at five/ten years; perturbed cases exercise reserve/debt/RSU/
investment/NCI/financing assumptions, signed operations, invalid inputs and
reverse statuses. Compare every result field, intermediate amount and proof
fraction. Decimal representation differences are bounded to 32 units in the
last place at precision 50, not cents, percentage materiality or changed cash;
exact rational certificate fractions must match exactly. Display agreement alone
is insufficient. This is implementation equivalence, not new financial approval.

The static preview origin serves no API and returns 404 for `/api/...`. Actual
browser checks confirm all three issuer defaults, changed assumptions and
sensitivity execution on that origin. Phone-size rendering is not an actual
iPhone Safari/virtual-keyboard or external hosted-access test.

## Portfolio publication and rollback

See `scripts/browser-migration/STATIC-PORTFOLIO.md`. The assembler reads the exact
ten allowlisted existing portfolio assets and adds the compiled browser app.
Modern workspace is `/valuation/`, legacy calculator `/valuation/calculator.html`.
Portfolio contents remain byte-preserved. Explicit aliases avoid masking missing
JS/JSON/CSS or unrelated routes as successful HTML. Release receipts stay outside
the public upload directory. Review headers currently mark the combined preview
noindex/no-store; production crawl/cache policy needs explicit review.

Before publication, sign in to the existing Netlify account, verify the actual
site ID/audience/plan and inspect GitHub integration behavior. Do not push the
portfolio to discover whether its active webhook publishes production. Publish
only the reviewed `public/` folder as a draft first. No new hosting provider,
anonymous tunnel or replacement site is created by these tools. Existing-site
publication and protection require real account access, not an invented URL.

After review, promote an accepted release deliberately. Preserve the previous
static deployment and its matching dataset manifest for rollback. Engine changes
and datasets are released as a compatible pair. Switching back to Python is
possible because its source/runtime were not migrated or removed; this does not
promise the old GCP deployment is current or publicly accessible.
