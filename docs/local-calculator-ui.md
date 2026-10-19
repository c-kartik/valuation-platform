# Local single-case calculator UI

## Scope and startup

The first React/TypeScript/Vite interface edits one `analyst-case-v1` through
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
alone does not proxy the API; use the documented dev command for this milestone.

## Entry and review contract

Four sections cover retained basis/metadata, five annual operating forecasts,
explicit terminal/discount inputs, and separate Validate / Calculate actions.
META/GOOGL/AAPL selections show source-bound FY2025 revenue, fiscal dates, filing
accession/form/SEC links, source precision and limitations. These are fixed retained
selections, not current/refreshed data; a separate filing-acceptance timestamp is
not exposed by this catalog. Only the separately labeled synthetic demonstration
loads the existing synthetic fixture ($100 revenue); it is not company data.

Each company starts with **37 unset numerical fields** and blank case name,
preparer, timestamp, rationale and scope. Retained limitations are visibly supplied
as editable text, not analyst approvals; update them to describe submitted inputs.
No declarations or current timestamps are silently filled to obtain validation.
All six original single-case templates and three scenario templates are unchanged.

Percentage fields use ordinary decimal percentage text: `10` → exact API string
`"0.10"`, `-2.5` → `"-0.025"`; blank → `null`. The decimal point moves as text,
without Number/parseFloat arithmetic. Percent signs, exponent notation, nonfinite
values and commas are rejected beside the field. Financial ranges/model semantics
remain Python checks. The UI constructs the existing strict EV-only schema; no
bridge, calculation-scope extension or structured cutoff field is invented.

The single-case reader does **not** enforce an information cutoff. Disclose it in
scope/limitations; the interface preserves the fiscal-end analytical/later-filed
notice and does not claim a contemporaneous backtest. Annual WC ratios apply to
full forecast revenue; positive uses cash, negative releases cash. Investment is
cash PP&E plus non-overlapping new finance-leased operating assets, excluding
principal. D&A must align with margin expense; SBC and operating-lease services
remain expensed. Joint economic consistency is a human review requirement.

Validate calls only `/api/v1/cases/validate`; Calculate explicitly calls `/run`.
Structural success is not economic approval. API field paths appear beside
matching fields and in a bounded error summary; subsequent validation may reveal
further errors beyond the API's 20-detail ceiling. Busy, deadlines, resource limits,
connection and internal errors preserve entries and require explicit retry.
Edits immediately mark existing results stale, cancel the local request and advance
revision tokens; obsolete responses are ignored even if abort is ineffective.
Populated entries require discard confirmation before changing basis. No automatic
saving, import/export or case management is added.

Returned annual components, discount factors/PVs, terminal FCFF/value and
explicit-period PV + terminal PV = EV are displayed directly. Money is **USD
millions**, ordinarily two decimals; nonzero amounts below USD 10,000 use eight
places to keep the small synthetic-dollar demonstration visible. An isolated
Decimal.js constructor performs display scaling/rounding only. Original inputs and
full-precision API strings remain in state and in the expandable review trace.
Negative values are preserved; EV is not equity or per-share value.

**Terminal contribution ratio is deferred:** the existing result object supplies
terminal PV and EV, but no ratio. The UI shows both, states the gap, and does not
introduce browser financial diagnostics. The existing CLI summary supplies the
ratio (undefined at zero EV; signed/over-100% values are not clamped). This follows
the milestone's instruction to defer diagnostics absent from the API rather than
change the existing result contract. An additive server presentation contract can
be separately scoped if needed.

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

## Verification record

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

Next bounded UI work can add an explicitly designed server presentation contract
for terminal contribution and improve review/field navigation, before separately
scoping JSON import/export or equity/share entry. Scenarios, sensitivity and reverse
screens remain outside this first UI. Public deployment still needs the separately
scoped [API launch checks](local-case-api.md#remaining-launch-boundary), Linux and
admission/load verification. Nothing is provisioned, deployed, connected to Netlify,
or changed in the separate personal website repository.
