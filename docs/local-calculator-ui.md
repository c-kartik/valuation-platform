# Local single-case calculator UI

The subsequent [390×844 desktop keyboard review](narrow-keyboard-review.md) closes
the earlier narrow-keyboard qualification after focused confirmation fixes: native
modal, safe Keep focus, explicit Tab cycle, Escape cancellation and trigger restoration.
This is not mobile virtual-keyboard or complete accessibility certification.
[Firebase/public-preview preparation](public-preview-preparation.md) remains local
and blocked on site identity/access/cost decisions; the deployed API is unchanged.

## Scope and startup

The React/TypeScript/Vite quick workbench edits one `analyst-case-v1` through
enterprise value only. The [packaged Python API](local-case-api.md) remains the
financial calculation/validation authority. No formulas, schemas, conventions,
financial approvals or historical resources changed. Phase 1 expansion remains
[paused](phase1-universe-pause-checkpoint.md); Phase 2's
[qualified software completion](phase2-completion-checkpoint.md) is preserved.

Run from the repository root in two terminals, using Python 3.12 and **Node
22.12+** (verified with Node 22.14.0 / npm 10.9.2). Check `node --version` in the
actual shell; this machine also has an older Node 18 installation. No global
Node/Python installation is changed by these commands.

Terminal 1: choose a **new private directory outside the repository** (replace the
example destination on subsequent builds), install the API lock and build/start:

```bash
.venv/bin/python -m pip install -r requirements-api.lock
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m valuation_platform.api.bundle /tmp/valuation-ui-api
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/valuation-ui-api/src VALUATION_APP_ROOT=/tmp/valuation-ui-api .venv/bin/python -m uvicorn valuation_platform.api.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --limit-concurrency 16 --backlog 32 --timeout-keep-alive 5 --timeout-graceful-shutdown 2 --no-access-log
```

Terminal 2, also from the repository root:

```bash
node --version
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open <http://127.0.0.1:5173/>. Both servers bind to loopback. Vite proxies `/api`
to `http://127.0.0.1:8000`, with a 50-second proxy timeout and fixed port; no CORS
middleware is added. Private bundles stay outside the frontend root. Vite's
filesystem allowlist is restricted to the frontend directory. Stop both servers
with Ctrl+C. `npm --prefix frontend run build` checks TypeScript and produces
ignored local `frontend/dist`; it is not deployment configuration. Vite preview
alone does not proxy the API; use the dev command above for development. The
[compiled-build review](local-workbench-acceptance.md) used a temporary local
static-plus-API harness; Vite preview is not a hosting/routing configuration.

## Quick-entry and review contract

The quick workbench supersedes the original four-section presentation. The journey
is now company → compact assumptions → explicit apply/calculate → result → optional
annual refinement. It reuses the existing reader, API, revision/cancellation guards,
exact rate conversion and returned values; it is not a replacement for professional
Excel modeling or evidence/financial review.

The header selects retained META/GOOGL/AAPL FY2025 data and shows reported revenue,
fiscal period and fixed data vintage separately from forecast assumptions. Filing
identity, SEC links, precision and limitations expand on demand. These are not
current/refreshed data; a separate filing-acceptance timestamp is not in the catalog.
The separate **Load synthetic demonstration** action explicitly loads the existing
$100 synthetic fixture; it is absent from the company selector and never supplies
company forecasts automatically.

The main view has **eight initially unset rates**: growth, margin, WACC, terminal
growth and four required FCFF cash-flow assumptions (operating tax, expense D&A,
investment and WC). Four headline inputs alone are insufficient. Six annual quick
entries are independent draft text; WACC/g edit their existing single-case fields.
Each annual row has Apply; **Apply all six to five years** requires all six values.
Applying creates a flat five-year path once, with no hidden continuing link.

The authoritative numerical inputs remain the existing **30 annual + 2 discount
+ 5 terminal fields**. Quick typing does not change them. Unapplied drafts are
marked and block both Calculate and Check inputs until applied or discarded.
Discard restores the displayed quick value to the current flat path, or blank if
annual values vary; it never changes annual inputs. Bulk application is atomic.
Changing populated annual values requires **Replace annual inputs** confirmation;
keeping annual edits leaves them intact. Any intervening input edit cancels the
pending replacement. Quick-only populated drafts also require company-switch
confirmation. No company selection or collapse/reopen action fills or resets rates.

**Advanced annual editing** exposes the same individually editable five-year rates.
A divergent row says **Varies by year — annual inputs used**. A flat path displays
its actual annual rate, even if the old quick entry differs. Calculate consumes the
annual path, never a silently linked quick draft. Collapsing preserves every value.

Five terminal operating/reinvestment ratios remain explicit and independent.
**Use year-five operating ratios for the terminal year** copies margin, tax, expense
D&A, investment and WC once. Missing/invalid year-five values reject the copy
atomically; it does not copy WACC or growth. The disclosed assumption is sustainable
year-five margins/reinvestment, requiring human consistency review. Later annual
edits never update terminal values. Every terminal ratio remains separately editable;
the main view lists missing terminal requirements even while the editors are closed.

**Case details** moves name, preparer, preparation timestamp, rationale, scope/cutoff
and limitations out of the main entry area. Missing required declarations remain
listed beside Calculate with a direct opening action. Company name/scope/preparer/
rationale/time start blank. **Use current UTC time** is an explicit convenience
only; there is no silent author, generic rationale or approval. Retained limitations
are initially visible when expanded and must be reviewed for the submitted case.
Identity/version/conventions remain derived from trusted templates. The exact
request and mechanical bindings expand inside Case details; no schema is redesigned.

Percentage text remains exact: `10` → `"0.10"`, `-2.5` → `"-0.025"`; blank → null.
No financial input passes through Number/parseFloat arithmetic. Percent signs,
commas, exponents and nonfinite text reject locally; Python owns financial ranges
and model validation. The existing contract has no structured enforced cutoff:
disclose it in scope/limitations. Fiscal-end analytical timing uses later-filed
information; it is not a contemporaneous backtest or an authenticated cutoff.

WC uses full forecast revenue: positive consumes cash, negative releases cash.
Investment is cash PP&E plus non-overlapping new finance-leased operating assets,
excluding principal. Expense D&A must align with margin expenses; SBC and operating
leases remain expensed once. Interface copy/apply actions approve no company
forecast, sustainability, calibration, coverage or financial convention.

Calculate explicitly calls the unchanged run route; **Check inputs** calls the
calculation-free validation route. Input errors link to labeled fields/editors;
API errors remain bounded and may require another check after correction. Busy,
deadline and connection errors preserve entries. Every input edit immediately
marks prior output stale, cancels requests and advances revision tokens, so old
responses cannot attach after editing or switching companies. Expanding/collapsing
review panels changes no inputs. There is no automatic saving, analytics, import/
export or case management.

## Result presentation and precision

The result panel prominently shows **enterprise value**, explicitly distinct from
equity/value per share, and **terminal contribution**. A newly authorized display-only
exception computes terminal PV / EV with an isolated Decimal.js precision-50 /
HALF_EVEN constructor, matching CLI summary semantics: undefined at zero EV, signed
and over-100% ratios retained, with explanatory notes before display rounding.
The API result contract and all raw returned strings are unchanged. The original
milestone's deferred-ratio decision is superseded by this explicit UI exception;
no server presentation endpoint or financial formula change was needed.

Revenue/FCFF SVG trends use returned strings, normalize in isolated Decimal.js and
convert only bounded coordinates to ordinary JS numbers. Coordinates never feed
back into financial inputs or calculations. Nonfinite/excessive magnitudes reject
chart rendering; tables/trace retain data. The compact table shows five years of
revenue, EBIT and FCFF in **USD millions**. Detailed FCFF components, discount factors,
PVs and explicit-period PV + terminal PV = EV expand separately. Submitted assumptions,
rationale, timing and limitations expand alongside a full-precision trace containing
an exact unrounded annual USD table. Compact cells also retain unrounded USD tooltips.

Money is normally two decimals in USD millions; small nonzero amounts below USD
10,000 use eight places for the synthetic-dollar demonstration. Display rounding
does not change raw strings; displayed components may not sum, and display digits
improve neither source precision nor economic validity. Negative flows/values remain
visible. No share-price comparison, rating, recommendation or economic approval.

## Read-only catalog and runtime boundary

`GET /api/v1/catalog` returns `local-ev-catalog-v1`: three explicit public metadata
projections and unchanged EV-only templates, the existing synthetic fixture,
shared timing explanation and input definitions. It accepts no query operands or
filesystem paths and has a **64-KiB encoded ceiling**. Startup verifies the private
bundle and existing retained revenue bindings before building/caching the response;
requests return fixed bytes without calculation, approval activation or directory
serving. Source URLs are allowlisted HTTPS SEC links. Package/audit bodies, source
hash/revision internals and developer absolute paths are not projected. Existing
run responses retain their full provenance and unchanged JSON contract.

The bundle now has **84 manifest entries**: 71 Python files, 12 pinned resources
(the original eight plus three EV-unset templates and the synthetic EV fixture),
and allowlist metadata. Existing eight resource hashes are unchanged. No second
historical-data copy is tracked. API request budgets, 35-second child deadline,
CPU restrictions, single active worker, cleanup and serialization limits are
unchanged. Client timeout is 50 seconds; cancellation/late-reply guards are UI
behavior, not a replacement for server deadlines. No cloud/static-host routing,
production CORS or public admission controls are configured.

## Compiled-build investor walkthrough — current

The [new developer walkthrough](local-workbench-acceptance.md) records continuous
META/GOOGL/AAPL entry/edit/recalculation on the actual compiled build, captured
browser-request/full-result CLI comparisons, zero/negative probes and 254 passing
checks. Two observed recovery blockers were fixed: recognized missing/tax diagnostics
now use percentage units; service failures no longer ask for assumption correction.
This is developer verification, not human investor research or economic approval.
The [API image candidate](local-api-image.md) separates static/private artifacts.
Its originally unexecuted Linux/cloud gates are superseded within scope by the
[authenticated deployment](cloud-staging-deployment.md) and subsequent
[compiled frontend/cloud review](cloud-frontend-acceptance.md); no public launch.

## Quick workbench verification

**Earlier milestone record, superseded by the compiled-build review above.**
That verification used the actual packaged API and Safari desktop/narrow-screen
sessions. Company selection began unset; compact synthetic rates were explicitly
applied, year-five terminal ratios copied, required metadata supplied and Calculate
run. A META FY2028 growth edit marked output stale/Varies by year, survived table
collapse/reopen, required confirmation before replacement and recalculated with
terminal inputs unchanged. Other retained companies were separately entered from
blank selections; no synthetic company defaults were saved.

All temporary annual rates came from the existing synthetic EV fixture; the copy
action deliberately made terminal ratios equal to year five instead of the fixture's
independent terminal ratios. This tests an explicit convenience assumption, not
company economics or approval. The separate proxy/API executions matched ordinary
CLI **full JSON exactly** for all three flat cases and the META edit. Browser EV /
contribution displays matched CLI: META 100,224.02m / 44.44%; edited FY2028 growth
15% (other annual growth 10%) 103,570.65m / 44.96%; GOOGL 200,898.88m / 44.44%;
AAPL 207,544.21m / 44.44%. All are synthetic engineering outcomes on retained
revenue, not actual-company valuation conclusions or saved cases/defaults.

The focused frontend tests include actual CLI comparison of terminal-contribution
formatting at zero/negative EV, signed/over-100% ratios and HALF_EVEN ties. Chart
coordinates are bounded for signed/zero/extreme values. Existing API/engine contracts
and all nine template bytes remain unchanged. **52 frontend + 19 API/catalog + 174 valuation/CLI + five preparation-preservation
tests passed (250 total)**, plus TypeScript/Vite build, Python dependency check and
full npm audit. Frontend CLI-comparison tests require the project Python `.venv`;
Node type declarations were added as a dev dependency only. Safari desktop and
390×844 checks exercised keyboard entry and scrollable result tables; a responsive
grid overflow found during review was corrected and rechecked. No unexpected
browser-console errors were observed in the workflow or fresh-load check. Temporary cases/results and
the test bundle are removed; actual review screenshots are emitted without adding
screenshots to the repository. Developer verification is not investor acceptance
or exhaustive accessibility/device certification.

## Earlier four-section verification record

The following is the **prior interface milestone's record**, preserved for context;
its original counts/results are not a claim that those trial sessions were replayed.
The commands remain the affected test invocations:


Commands for affected checks:

```bash
npm --prefix frontend run build
npm --prefix frontend test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.api.test_cases tests.api.test_catalog -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/valuation -t . -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.analyst.test_preparation_preservation -v
```

The local browser review used Safari against the actual packaged API/Vite proxy.
The explicit synthetic demo and temporary synthetic forecasts on each retained
company were validated and run. The test rates came solely from the synthetic
fixture, not prior company trials or analyst economics. Separate proxy HTTP runs
matched ordinary CLI **full JSON exactly in all four cases**, including provenance.
META/GOOGL/AAPL browser EV displays matched CLI values rounded to USD millions:
155,903.52 / 312,508.33 / 322,845.47. These are engineering checks with synthetic
forecasts, **not actual-company valuation conclusions**. Temporary case files were
outside the repository and removed. No runnable company assumptions were saved.

Browser checks also exercised missing inputs, invalid percentage notation, stale
results, labels, keyboard field movement, switching confirmation, responsive layout
and developer-console errors. Automated tests cover conversion, request compatibility,
no terminal copying/defaults, field/API errors, client deadline and obsolete replies.
**35 frontend tests + 19 API/catalog tests + 174 valuation/CLI tests + five
preparation-preservation tests = 233 passed**; TypeScript/Vite build, Python
dependency checks and npm full dependency audit passed. The browser console
initially showed a missing favicon and the deliberately invalid-input 422; the
favicon was added and a fresh load had no console errors. Safari desktop and
390×844 responsive mode were exercised, including Tab between annual inputs and
horizontal access to year five. Screenshots were emitted during review; no
screenshots or temporary case/results were saved in the repository. This is not
exhaustive browser/device or assistive-technology certification.
No full historical suite or new financial research was run.

## Next boundary

JSON import/export or equity/share entry require separately bounded work. No equity,
scenario, sensitivity or reverse-DCF screens are added here. The current cutoff
remains free text, analyst declarations unauthenticated, and economic completeness
unproven. Public deployment still requires the separately scoped
[API launch checks](local-case-api.md#remaining-launch-boundary), Linux/admission/
load verification and hosting decisions. Phase 2 qualified completion and Phase 1
pause are unchanged. No hosting, cloud, DNS or separate website files are changed.
