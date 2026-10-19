# Compiled EV workbench — developer investor walkthrough

Review date **2026-10-20 (Asia/Dubai)**; starting clean `main` at
`599dc31f1278d222f8ee4f638cff0c2a8a88b057`, 12 ahead of local `origin/main`.
This is a developer-conducted walkthrough by Codex, **not participant research,
investor acceptance or financial-input approval**. Phase 1 remains
[paused](phase1-universe-pause-checkpoint.md), and
[qualified Phase 2 closure](phase2-completion-checkpoint.md) is unchanged.

## Tasks, criteria and observations

All browser journeys used Safari and the **actual compiled Vite build**, served by
a temporary trusted loopback static/API routing harness on port 4173, with the
verified private bundle/Uvicorn on 8000. No Vite HMR/dev proxy was running.
The harness served static assets only and forwarded relative `/api` requests;
engineering POST bodies/responses were captured outside the repository for CLI
comparison, then removed. It is not a production proxy or Firebase routing proof.

| Investor task / acceptance criterion | Observed action and outcome |
| --- | --- |
| Understand output and supported data | PASS: company menu lists META/GOOGL/AAPL FY2025; retained revenue/date strip says fixed, not refreshed. EV placeholder/result explicitly excludes equity/share. Opened filing/source limitations to obtain accession, precision and fiscal-end/later-filed timing. |
| Understand separate demo | PASS: explicit button loads clearly labeled synthetic $100 anchor, distinct from company selection. Calculated and reviewed demo. |
| Complete unset company | PASS: each company started with eight blank compact fields, missing-terminal list and required-detail indicator. Typed eight rates, applied all six annual rows, copied terminal once, opened Case details and authored declarations; Check inputs then Calculate. |
| Understand percentages and cash flows | PASS after diagnostic fix below: visible percentage example, investment scope, full-revenue WC signs, expense/SBC/service-lease explanations; USD millions and unrounded USD trace. No financial input conversion through floats. |
| Review result | PASS: opened cash-flow/reconciliation and submitted-assumption/timing panels. Annual FCFF, PV reconciliation and terminal contribution available without source-code reading. |
| Refine annual path | PASS on each issuer: opened Advanced annual editing, changed FY2028 growth 10%→15%, saw Varies by year and STALE RESULT, explicitly recalculated. META also changed FY2030 margin 20%→21%; terminal margin stayed 20%. |
| Avoid unintended overwrite/link | PASS: applying changed populated rows required Replace annual inputs; explicit confirmation used for zero-flow probe. Company changes required discard confirmation; collapse/reopen preserved values. Apply/copy are one-time actions, never links. |
| Recover from entry/service error | PASS after fixes: `10%` rejected locally without changing annuals; missing terminal/detail and 125% operating tax rejected by API. Error links open/focus editors. Stopped API twice, saw connection failure, restarted and explicitly retried without losing inputs/results. |
| Interpret unusual outcomes | PASS: zero EV showed Undefined contribution; negative EV/FCFF retained signs; positive terminal PV offsetting negative explicit cash flows displayed 600.05%, with explanation. No clamping. |
| Desktop/narrow/keyboard | PASS within scope: desktop and Safari 390×844 responsive view; labeled fields, horizontal annual-table access through year five, Tab from year-five growth to next-row first margin, keyboard edit marked stale. Actual screenshots emitted in chat. Not assistive-technology or device certification. |
| Busy/deadline/late replies | Automated PASS: frontend covers busy/deadline/connection recovery and out-of-order replies; actual process tests cover busy+health, timeout/kill/reap/recovery and shutdown. Browser saw live Calculating state, edit-stale behavior and stopped-backend recovery; it did not replay every timed process fault. |

Required sections for entry were terminal ratios (opened by explicit copy) and
Case details. Annual editing was needed only for refinement; source, reconciliation
and trace panels were optional review. No typing-speed claim is made.
No unexpected input loss occurred. Explicit company discard and page reload erased
in-memory work as disclosed by **No automatic saving**; reload was intentional.

## Material findings and bounded fixes

1. Missing rate errors asked for a **fractional Decimal string**, contradicting
   percentage fields; tax errors said **0 to 1**, inviting a 100× entry mistake.
   The UI now translates only these recognized diagnostics to percentage wording
   (required percentage / tax 0%–100%). Native browser recovery and focused tests
   verified the change. Raw API errors, validation ranges and submitted JSON remain
   unchanged; unknown diagnostics pass through.
2. A stopped-backend error appeared under **Inputs need attention**, instructing
   correction of valid assumptions. Non-field failures now use **Request did not
   succeed**, service/retry guidance and explicit input preservation. Field errors
   retain their correction links. Tested identical-request retry and actual backend
   restart/recovery; the final shared status also directs review of the message.

No financial calculation defect was found. No engine/API/financial-resource changes
were needed. No persistence, equity/scenario UI, economic defaults or redesign added.

Nonblocking friction remains: manual rationale/cutoff needs analyst judgment; the
cutoff is free text and declarations unauthenticated. Detailed annual editing and
trace are long on a phone; there is no import/save. Old quick text can remain beside
a divergent annual path, but Varies by year states that annual values are used.
Template limitation text must be reviewed/updated by the preparer when it describes
unset inputs; it is never silently rewritten. Initial catalog failure requires a
reload after service recovery. Some unrecognized model diagnostics remain technical.
The UI cannot resolve economic consistency, evidence gaps or issuer input policy.

## Engineering sheet and actual comparison evidence

Temporary rates were **synthetic engineering choices**, not company estimates:
annual growth 10%, margin 20%, operating tax 25%, expense D&A 5%, investment 10%,
WC cash requirement 2%, WACC 25%, terminal growth 5%. Explicit terminal copy set
20% / 25% / 5% / 10% / 2%; no year-five inference was made automatically.
Each case was labeled SYNTHETIC engineering walkthrough, prepared by Codex (AI
developer) with the browser's explicit UTC-time action. Rationale/scope disclosed
engineering-only rates, retained history/later-filed timing and no economic cutoff.
No fabricated approval or researched forecast was supplied. The separate unchanged
demo retains its independent fixture terminal assumptions.

| Continuous retained-anchor session | Revenue anchor, USD | Initial EV, USD millions | Edited EV, USD millions |
| --- | ---: | ---: | ---: |
| META, calendar 2025, t0 2025-12-31 | 200966000000 | 100224.02 | 104402.23 (growth FY2028 15%, margin FY2030 21%) |
| GOOGL, calendar 2025, t0 2025-12-31 | 402836000000 | 200898.88 | 207607.19 (growth FY2028 15%) |
| AAPL, 2024-09-29–2025-09-27, t0 2025-09-27 | 416161000000 | 207544.21 | 214474.42 (growth FY2028 15%) |

Initial copied-terminal contribution was 44.44% for each. These values are
**engineering outputs, not actual-company valuation conclusions**. Subsequent
AAPL zero/negative/offsetting probes explicitly applied zero margin/D&A/investment/
WC, then −10% margin (no immediate loss tax benefit), then terminal margin 20%
with negative annual margins. Growth remained 10%, tax 25%, WACC 25%, g 5%.
All-zero flows gave EV 0; negative-flow EV was −259430.27m; offsetting-flow EV
28822.88m with 600.05% contribution. These are interface stress inputs, not scenarios.

**14 successful browser submissions** (including demo, three issuer paths/edits,
retries and final-build recheck) matched ordinary CLI **full parsed result JSON
exactly**, including submitted assumptions, full precision and source bindings.
The exact captured browser bodies were used, not separately reconstructed requests.
Four successful validation submissions also passed ordinary validation-only CLI;
three invalid submissions failed it; two stopped-backend attempts had no result.
Input-file bytes remained unchanged. An independent `Fraction` oracle using those
submitted strings and explicit retained/synthetic seeds passed **882 exact numeric
equalities** across annual components, discount factors/PVs, terminal components,
terminal value and EV. No engine functions were used by that arithmetic oracle.
All equality claims are for this engineering sheet, not economic precision.

## New regression and artifact checks

Commands actually run in this checkpoint:

```bash
npm --prefix frontend test
npm --prefix frontend run build
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.api.test_cases tests.api.test_catalog tests.api.test_image_launcher -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/valuation -t . -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest tests.analyst.test_preparation_preservation -v
.venv/bin/python -m pip check
npm --prefix frontend audit
git diff --check
```

**54 frontend + 21 API/catalog/launcher + 174 valuation/CLI + five preservation =
254 passed.** Frontend tests/build were rerun after the final shared-status wording
change; unchanged Python checks were not repeated. Two new frontend tests cover
percentage-error recovery and identical-input service retry; two host launcher tests
cover PORT/one-worker settings and invalid PORT rejection. Dependency checks passed;
npm reported zero vulnerabilities. No full slow historical suite or financial
research ran. Earlier milestone measurements remain earlier records, not new tests.

Final compiled static artifact: **four files / 290180 bytes** (index, favicon, CSS,
JS); Vite reports approximately 91.46 kB gzip JS. Inspected relative `/api/v1` paths,
no localhost backend URL, source maps, private bundle markers or credential markers.
Private files are outside the static root. The prepared API context verified exact
membership: **89 files / 7694552 bytes**, not image size. All nine templates remained
byte-unchanged: six × 37 unset and three × 111 unset; bridge/share selections remain
unresolved. Engine formulas, examples, schemas, source approvals, historical/frozen
artifacts and Phase 1 pause are unchanged. Changed local links/anchors, whitespace,
protected diff and exact staged scope were checked. Temporary cases/results,
captures, harness, bundles and servers were removed; none enters this commit.

## Readiness

| Boundary | Verdict and remaining gate |
| --- | --- |
| Restricted staging experiment | **Prepared locally; not yet ready for a cloud run.** First obtain an available local runtime and pass the Linux/image test matrix in the [image candidate guide](local-api-image.md), then approve region/configuration/budget/access and conduct a separately authorized authenticated Cloud Run test. |
| Anonymous staging | **Not ready.** Above gates plus explicit exposure decision, Firebase `/api` routing, direct backend access/abuse controls and cost/load tests. One child per process is not a deployment-wide quota. |
| Public production | **Not ready.** Above plus measured cloud cold starts, memory/Linux enforcement, transfer billing, load/recovery and operational/security acceptance. No investment-readiness claim follows software checks. |

Docker, Podman and Colima were absent from PATH. No local runtime/VM was installed
or started, and no remote/cloud builder used. **No Linux image was built or run**:
architecture, image size, startup/RSS, read-only enforcement, Linux child cleanup
and container shutdown remain unverified. Host launcher/process tests cannot close
those gates. The image recipe uses supported Python, locked API dependencies,
allowlisted verified private resources, nonroot execution and configurable PORT;
there is no actual hosting/Firebase project configuration or deployment command.

Smallest next step: on an already available local Linux-container runtime, build
and run the candidate and execute that bounded matrix before any authenticated
cloud experiment. No cloud login/provisioning/deployment, DNS/Netlify change, push
or access to the separate personal website repository occurred.
