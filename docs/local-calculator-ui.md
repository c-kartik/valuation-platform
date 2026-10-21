# Local single-case calculator UI

The subsequent [390×844 desktop keyboard review](narrow-keyboard-review.md) closes
the earlier narrow-keyboard qualification after focused confirmation fixes: native
modal, safe Keep focus, explicit Tab cycle, Escape cancellation and trigger restoration.
This is not mobile virtual-keyboard or complete accessibility certification.
The earlier [Firebase preparation](public-preview-preparation.md) is superseded by
the [hosted preview record](firebase-public-preview.md). This local redesign
is not deployed and changes no preview access or withdrawal deadline.

## Scope and startup

The React/TypeScript/Vite calculator constructs `investor-case-v1` through enterprise value, with an optional
explicit `investor-case-v2` equity/share step. The [packaged Python API](local-case-api.md) remains the
financial calculation/validation authority. The narrow
[metadata extension](local-case-api.md#anonymous-investor-metadata-local-update)
leaves formulas, conventions, financial approvals and historical resources unchanged.
Phase 1 expansion remains
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

The compact investor layout supersedes the earlier workbench presentation. The journey
is now company → compact assumptions → calculate → result → optional
annual refinement. It reuses the existing reader, API, revision/cancellation guards,
exact rate conversion and returned values; it is not a replacement for professional
Excel modeling or evidence/financial review.

The compact **DCF Calculator** header selects META/GOOGL/AAPL FY2025 data.
Company/ticker, year and reported revenue in a readable USD scale remain visible,
alongside fixed/not-live and unreviewed-forecast notices. **Data & methodology**
expands the fiscal period, filing identity, SEC links, precision, later-filed timing
and financial limitations. Internal project language and repository references
are absent from ordinary product copy; exact provenance remains in the trace. These are not
current/refreshed data; a separate filing-acceptance timestamp is not in the catalog.
The separate **Load synthetic demonstration** action explicitly loads the existing
$100 synthetic fixture; it is absent from the company selector and never supplies
company forecasts automatically.

The main view has **eight initially unset rates** with plain-language labels:
annual revenue growth, operating profit margin, operating tax, depreciation &
amortization/revenue, operating investment/revenue, working-capital cash needs/
revenue, discount rate (WACC) and long-term revenue growth. The grouped grid shares **Enter percentages: 10 = 10%** guidance and a count
of unset numerical operands (not a financial-validity count). Labeled **?** help
disclosures work with keyboard/touch, preserving EBIT, positive-profit tax,
financed-asset investment and signed full-revenue cash-needs meanings. No financial definitions or numerical domains change.

The authoritative request still contains **30 annual + 2 discount + 5 long-term
operating ratios**. While an annual row is uniform, typing in its main control
immediately updates that field in all five years. There is no Apply button or
second hidden value. Raw percentage text remains unchanged while typing, including
blank/partial/invalid strings; those states block submission instead of falling
back to an earlier valid rate. Discount rate and long-term growth edit their own
fields directly. A blank company supplies no numerical defaults.

**Edit individual years** exposes the same five-year strings individually.
Editing one year affects no other year or long-term ratio. Differing annual rates
show **Varies by year** and a blank uniform-replacement control, rather than a
misleading single rate. Entering a replacement leaves the existing path intact
and visibly blocks Calculate. **Use for all five years** requires confirmation
naming the field, proposed percentage and all affected fiscal labels. Cancel
clears the proposal, preserves every annual value and restores focus. **Keep
annual values** also discards the proposal explicitly. Confirm replaces only the
chosen field; subsequent uniform edits apply directly. A new individual-year edit
abandons a replacement proposal for that same field. Collapse/reopen changes no
values. Semantic equality of decimal formats does not falsely report variation.

Five long-term operating/reinvestment ratios remain explicit and independent.
**Copy final-year assumptions** copies margin, tax, expense D&A,
operating investment and cash needs once. Missing/invalid source text rejects the
copy atomically. Populated target values that would change require confirmation,
listing affected ratios and the source fiscal year; Cancel preserves them and
restores focus. Copy never changes WACC or long-term growth. Later annual edits
never change these ratios; a concise difference indication supports review.
Sustainable final-year economics remain a user assumption, not calculator approval.

Validation starts with **neutral required-input guidance**. An edited field gains
inline errors after leaving it; untouched optional fields receive no missing
counts. Presence/percentage syntax and local entry-state checks are frontend
checks; numerical domains and WACC/g remain the existing Python validator's job.
Blur can call the calculation-free validate route using actual current inputs,
including nulls, without fabricating other operands. Incomplete-case checks can
return expected HTTP 422 responses visible in browser DevTools; only touched
fields show those diagnostics in the form. Some server domains require complete
operand groups before they can be assessed. Failed background checks do not
become financial-error claims or approval; explicit submission reports service
failures normally.

**Calculate enterprise value** is the sole calculation action and reveals all local blocking errors, combining equivalent
uniform-year issues into one main control. The concise summary shows three links
and a disclosure for the rest, opens the first relevant editor and focuses its
field. Correcting an entry removes its resolved local error without clearing
unrelated errors; server errors refresh on checks. Existing bounded server
diagnostics can reveal further financial errors after correction. Known rate
messages use entered percentage units. Busy/unavailable/deadline failures stay
separate, preserve all entries and request an explicit retry. Error descriptions,
labels and one status announcement support keyboard review without a live alert
on every keystroke. Revision/abort guards also cover background validation.

**Analysis details** is collapsed and optional in the normal flow: select company
→ enter assumptions → calculate. A generated editable case name and UTC
preparation timestamp are created once when selecting a draft; they stay stable
through requests/retries. The timestamp records draft preparation, not the fiscal-end
analytical date, evidence review or verified information availability. Provenance
is explicitly anonymous investor, without verified identity or professional-analyst
status. There is no required preparer, rationale, time entry or scope/cutoff attestation.
Optional personal notes start empty (serialized null for absent); nonempty notes
retain the user's wording and are bounded to 2,048 characters. Notes/name edits
invalidate pending replies and mark results stale, just like numerical edits.
No optional-field missing count blocks calculation. A deliberately cleared case
name still receives a linked required-name error; the generated name needs no entry.

The template-only “all 37 unset” instruction is filtered from the runtime copy;
original catalog/templates remain unchanged. The UI separately counts currently
entered numerical inputs (not domain-valid inputs) and retains every enduring
financial limitation. Historical period, filing, precision and later-filed timing
remain readable source information. Forecasts are user-entered, not independently
reviewed, and inherit no historical approval. Exact requests/source bindings expand
inside Analysis details. Legacy documented analyst CLI/API cases remain supported
with their original requirements, rather than receiving fabricated boilerplate.

Percentage text remains exact: `10` → `"0.10"`, `-2.5` → `"-0.025"`; blank → null.
No financial input passes through Number/parseFloat arithmetic. Percent signs,
commas, exponents and nonfinite text reject locally; Python owns financial ranges
and model validation. The investor contract establishes no verified information
cutoff. Legacy analyst cases retain their free-text scope/limitation declarations.
Fiscal-end analytical timing uses later-filed
information; it is not a contemporaneous backtest or an authenticated cutoff.

WC uses full forecast revenue: positive consumes cash, negative releases cash.
Investment is cash PP&E plus non-overlapping new finance-leased operating assets,
excluding principal. Expense D&A must align with margin expenses; SBC and operating
leases remain expensed once. Interface entry/copy actions approve no company
forecast, sustainability, calibration, coverage or financial convention.

Calculate explicitly calls the unchanged run route, which validates before
calculation. The separate Check inputs control is removed from the investor UI;
calculation-free API/CLI validation and background blur checking remain unchanged. Input errors link to labeled fields/editors;
API errors remain bounded and may require another check after correction. Busy,
deadline and connection errors preserve entries. Every input edit immediately
marks prior output stale, cancels requests and advances revision tokens, so old
responses cannot attach after editing or switching companies. Expanding/collapsing
review panels changes no inputs. There is no automatic saving, analytics, import/
export or case management.

## Result presentation and precision

The desktop result panel sits beside inputs; narrow results follow the calculation
action. Its short initial placeholder becomes a readable USD enterprise value with
**Operating business value; excludes the cash/debt/share bridge**, and terminal
contribution. Detailed annual tables and provenance expand on demand. A newly authorized display-only
exception computes terminal PV / EV with an isolated Decimal.js precision-50 /
HALF_EVEN constructor, matching CLI summary semantics: undefined at zero EV, signed
and over-100% ratios retained, with explanatory notes before display rounding.
All raw financial strings are unchanged; the investor metadata/result version is
explicitly distinguished from the legacy analyst result. The original
milestone's deferred-ratio decision is superseded by this explicit UI exception;
no server presentation endpoint or financial formula change was needed.

Revenue/FCFF SVG trends use returned strings, normalize in isolated Decimal.js and
convert only bounded coordinates to ordinary JS numbers. Coordinates never feed
back into financial inputs or calculations. Nonfinite/excessive magnitudes reject
chart rendering; tables/trace retain data. The expandable compact table shows five years of
revenue, EBIT and FCFF in **USD millions**. Detailed FCFF components, discount factors,
PVs and explicit-period PV + terminal PV = EV expand separately. Submitted assumptions,
rationale, timing and limitations expand alongside a full-precision trace containing
an exact unrounded annual USD table. Compact cells also retain unrounded USD tooltips.

Headline revenue/EV scale to USD billions, millions or dollars using isolated
precision-220 HALF_EVEN Decimal arithmetic, with two display decimals. Raw
strings remain in full-precision traces. Detailed money is normally two decimals in USD millions; small nonzero amounts below USD
10,000 use eight places for the synthetic-dollar demonstration. Display rounding
does not change raw strings; displayed components may not sum, and display digits
improve neither source precision nor economic validity. Negative flows/values remain
visible. No share-price comparison, rating, recommendation or economic approval.

## Optional cash, debt and shares

**Add cash, debt & shares** appears below EV and starts closed. EV calculation
requires no bridge entries. Opening reveals eligible cash/investments, financing,
other claims, shares and their observation date, all initially unset. Inputs use
USD millions and millions of shares, converted exactly as decimal text to base
USD/shares. Blank stays missing; explicit zero is distinct. Negative equity and
per-share results are preserved; role-based nonnegative magnitudes determine
adjustment signs, with positive adjustments in eligible assets.

**Coverage, classes & awards** and **Component details & overlap references**
start closed. Required declarations remain discoverable in the main bridge text;
submission expands/focuses missing declarations. Assets exclude operating reserves
and operating value; financing includes finance leases once, without duplicate
forecast settlements. A mandatory explicit declaration records date, eligibility
and non-overlap. The user selects each role's population-only coverage or explicit
unbounded omissions; neither establishes complete economic coverage. Other claims
have separate amount, none-identified and not-assessed choices. None identified
is an unverified scoped omission with null amount, not an invented zero. Not
assessed blocks the requested equity result while EV remains available.

Shares require an explicit fiscal-end date, issued/basic-equivalent basis, named
class(es), single-class or one-for-one economic-equivalence declaration and award
treatment. No META/Alphabet class equivalence is assumed. Existing awards can be
explicitly declared absent within the user's population (unverified), omitted
provisionally, included as non-overlapping pre-anchor adjusted shares, or included
as an other-claims amount. Adjusted-share treatment requires the basic-equivalent
basis; claim treatment requires an explicit claim amount. SBC service costs stay
in margins once. The calculator supplies no automatic RSU addition, award value,
proceeds or dilution. These choices do not prove semantic consistency.

This compact form supplies three aggregate role components. Collapsed component
details name those populations and permit explicit overlap/alternative references;
selected overlapping operands reject in the existing engine. Richer named
multi-component/exclusion cases remain supported by the existing CLI/API.
The [anonymous v2 contract](local-case-api.md#optional-anonymous-equityshare-extension-local)
records unverified manual source references and coverage-choice attribution, never
fabricated financial review. Optional personal notes remain optional.

**Calculate value per share** explicitly submits the full operating case and bridge
to the existing A/B/C engine, checking returned Stage B against the current EV.
The UI does no bridge arithmetic. It shows server EV + assets − financing − claims
= equity, divided by dated valuation shares, with USD/share and issued or
basic-equivalent labels. Disclosed omissions are prominent beside a provisional
reference and retain potentially unbounded amounts. No result certifies fully
diluted fair value or complete claims coverage. Exact signed contributions and
submitted provenance expand separately; scaling/rounding is display-only.

Closing the bridge preserves values in the current page session; there is no
saving. Bridge edits stale only equity. Operating/metadata edits stale both and
require EV recalculation first. A fresh EV never makes an earlier equity result
current: per-share calculation stays explicit. Revision/abort guards ignore late
replies; failure preserves input and EV. Switching company confirms/discards the
whole populated draft, including its optional bridge.

## Optional equity verification (local)

The subsequent [three-anchor investor acceptance review](equity-workflow-acceptance.md)
records actual browser/CLI comparisons, independent arithmetic, responsive/error
recovery checks and three presentation fixes. The checks below describe the
earlier implementation checkpoint, not a newly rerun review.

**78 frontend tests** and **101 distinct focused Python checks** passed across the
focused run and targeted corrected-fixture rerun. Python scope covers intake,
legacy EV/equity/CLI-summary, bridge, API/catalog/public boundaries and preparation
preservation. Production TypeScript/Vite build passed. No historical suite or
actual-company valuation. The new frontend comparison writes equivalent anonymous
and legacy synthetic equity cases only in an automatically cleaned external
temporary directory, runs the real CLI and matches **complete Stage B and C
components**; submitted metadata intentionally differs. Independent fixture:
EV 77.577060352 +12 −20 −3 = equity 66.577060352, /4 shares =16.644265088 USD/share.
UI tests cover exact conversion, blank/zero/omissions, declarations, signed output,
focus, scope switching, service recovery and independent stale/revision handling.

Actual Chrome desktop and approximately 390×844 checks use the separate synthetic
$100 fixture and manual bridge amounts 0.000012/0.000020/0.000003 USD millions,
0.000004 million issued synthetic common shares, date 2025-12-31. Coverage is
explicitly population-only, single-class; existing awards are omitted provisionally.
EV succeeded without bridge inputs; unassessed claims blocked equity. Bridge
close/reopen, advanced disclosure, keyboard declaration/error navigation, bridge
edits, operating edits, EV refresh and explicit equity recalculation were checked.
Screenshots capture the compact bridge/reconciliation. This is desktop responsive
verification, not mobile virtual-keyboard or complete accessibility certification.
No company forecasts, balances, cases or outputs were saved. All nine unset
templates, engine formulas, historical approvals, Phase 1 pause and hosted preview
window remain unchanged. Only loopback frontend/API review servers remain running.

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

## Compact investor redesign verification (local)

**64 frontend tests and five preparation-preservation tests passed**, plus the
TypeScript/Vite production build. Frontend checks include the existing real
Python financial-component comparison, direct/annual entry, replacement and
terminal-copy independence, required financial inputs, optional metadata,
error navigation, stale/obsolete replies and service recovery. New checks cover
focusable help, source/qualification access, ordinary-screen terminology and
isolated readable-USD scaling/HALF_EVEN rounding. API behavior and Python code did
not change, so API tests and the historical suite were not rerun.

Actual Chrome desktop and 390×844 responsive walkthroughs started from unset
META, using deliberately synthetic engineering rates: growth 10%, margin 20%,
tax 25%, expense D&A 5%, investment 10%, WC 2%, WACC 25%, g 5%, with an explicit
final-year ratio copy. No optional details or company economics were required.
Desktop FY2027 growth 18% made the result stale; a proposed 12% uniform
replacement was canceled with Escape and focus restoration. Tax 150% produced
focused percentage guidance; correction to 25% recalculated successfully with
the annual refinement retained. Narrow keyboard selection, all eight entries,
source disclosure, final-year copy, FY2027 refinement and recalculation were exercised. The separate
$100 synthetic fixture was also run with annual/terminal margin −10%, retaining
negative EV/FCFF and the negative-EV contribution explanation. These are test
choices, not company forecasts, economic conclusions or saved cases.

Comparable before/after screenshots were captured at 1280×800 and 390×844,
plus narrow help and signed-result views. Labels/help and results stacked without
observed page-level horizontal overflow; wide tables retain their own scroll
regions. Expected incomplete/invalid validation 422s appeared in DevTools;
no application exception was observed. This was a resized desktop browser,
not mobile virtual-keyboard testing or complete accessibility certification.
Temporary browser assumptions were discarded. Only the requested loopback
frontend/API review servers remain running. Nine unset templates, formulas,
source/approval bindings and the anonymous metadata contract are unchanged.
No hosted services, public-preview window or Phase 1 pause changed.

## Earlier direct-entry and validation verification (local)

**60 frontend + 72 focused Python tests passed (132 total)**, plus TypeScript/Vite
production build. The Python invocation covered case inputs, equity/summary
compatibility, API/catalog/public boundaries and preparation preservation; no full
historical suite. Frontend coverage replaces obsolete Apply tests with direct raw
entry, varying-path proposal/confirm/cancel, partial/invalid-value blocking,
long-term replacement/independence, touched and submit navigation, correction,
notes/service recovery, stale replies and background-validation revision checks.
An actual Python pipeline comparison of old documented-analyst and equivalent
new direct-entry requests matched **complete Stage B financial components** and
the independently retained synthetic-fixture EV. Metadata intentionally differs;
no full-result JSON identity is claimed across metadata versions.

Actual compiled-build Chrome desktop and 390×844 walkthroughs began with unset
retained META and GOOGL selections. Explicit synthetic test inputs were growth
10%, margin 20%, operating tax 25%, D&A 5%, investment 10%, cash needs 2%, WACC
25% and long-term growth 5%, with a deliberate final-year copy action. No Apply or
Analysis-details entry was needed. These are engineering test choices, not
company forecasts or approved economic assumptions. Desktop missing-input
submission focused growth; partial `-` and a deliberate tax 150% were corrected
without losing other entries. A FY2027 growth edit to 18% produced a varying
path; a 13% replacement was canceled with focus restored, then 14% confirmed
across all five years. Margin 21% was explicitly copied after cancel/confirm;
a later annual margin 22% preserved the independent long-term 21% ratio.

Narrow keyboard entry used ordinary Tab between rates. Long-term margin was
changed to 21%, then copy cancellation, focus restoration, two-action Tab cycle
and confirmed restoration to final-year 20% were exercised before recalculation.
Expected partial-case validation 422s appeared in DevTools; no unrelated
application exception was observed. Representative neutral-form, confirmation,
focus and result screenshots were emitted during review. This is desktop
responsive/keyboard testing, not mobile virtual-keyboard or exhaustive
accessibility certification. Temporary browser assumptions were discarded and no
company case/output was saved. Only the requested localhost review frontend and
compatible private API are left running after the checkpoint; the compiled test
harness is stopped. Nine template bytes, formulas, source approvals, anonymous
metadata contract and the [public preview](firebase-public-preview.md) are unchanged.

## Earlier anonymous investor metadata verification (local)

This local update passed **59 frontend and 72 focused Python tests (131 total)**:
case-input/legacy equity/CLI-summary, API/catalog/public-boundary and preparation
preservation checks. Tests compare complete Stage B financial components across
investor and legacy metadata on synthetic and all three retained anchors, rather
than claiming identical metadata-bearing JSON. They cover null/present/edited/cleared
notes, wording/whitespace retention, generated details, invalidation/late replies,
financial/source/domain errors, calculation-free validation, budgets and legacy
compatibility. TypeScript/Vite production build passed; no full historical suite.

Actual Chrome desktop and 390×844 responsive walkthroughs used compiled static
assets and a fresh local packaged API. Starting from unset META (desktop), GOOGL
and AAPL (narrow), the tester explicitly entered synthetic growth 10%, margin 20%,
tax 25%, expense D&A 5%, investment 10%, WC 2%, WACC 25% and terminal growth 5%,
applied annual rows and explicitly copied year-five terminal ratios once. These
are engineering test choices, not company forecasts or economic recommendations.
Calculation succeeded without opening Analysis details. The empty META attempt
returned only required financial-field errors, without a result. Notes and a WACC
edit to 26% (desktop), then notes and terminal WC to 3% (final narrow build), marked
results stale and recalculated while retaining preparation time and wording.
Generated names were shortened during review; timestamps remain in details.
The final narrow result/source disclosure preserved fiscal-end timing, SEC links,
absence of rationale/cutoff and enduring qualifications, without the obsolete
“all 37 unset” instruction. The final narrow session showed zero console messages.

This is desktop keyboard/responsive testing, not actual mobile virtual-keyboard
or exhaustive accessibility certification. No actual-company economic case or
forecast defaults were saved. The browser trial tab, local servers and temporary
private bundle were removed. Existing [public preview](firebase-public-preview.md),
cloud resources and withdrawal window are unchanged; no push/deployment occurred.

## Earlier compiled-build investor walkthrough

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
scenario, sensitivity or reverse-DCF screens are added here. No verified cutoff is
established; anonymous preparation and legacy analyst declarations remain
unauthenticated, and economic completeness unproven. Public deployment still
requires the separately scoped
[API launch checks](local-case-api.md#remaining-launch-boundary), Linux/admission/
load verification and hosting decisions. Phase 2 qualified completion and Phase 1
pause are unchanged. No hosting, cloud, DNS or separate website files are changed.
