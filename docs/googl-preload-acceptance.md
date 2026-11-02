# GOOGL proposed preload — implementation and acceptance

## Reproduction audit — November 2, 2026

All 24 preload tests pass. Repeated generation from retained sources and policy
produces economic hash `1c652c65ae2cd9cbf5f726f163963434c17514c6f2b1a0afcf229d059a1768fe`
independently of the generation timestamp; existing-engine execution reproduces
EV 1,421,564,121,025.2409787628263166077237849572626227555 USD.
The engine-preservation test had retained the earlier five-year baseline. It now
pins the explicitly approved ten-year engine commit 634d98b, preserving the
original template and resource baselines. No engine or financial input changed.

Reproducibility is conditional on saved reviewed observations and explicit
forecast configuration. Acquisition does not automatically extract facts or
select forecasts. The generator and API/UI wiring remain Alphabet-specific;
META/AAPL profiles require separate implementation and company-specific policies.

Subsequent UI status: the [result-first workspace](investor-result-first-workspace.md)
now calculates complete starting profiles automatically through the local API and
uses one on-demand editor. Earlier no-auto/inline-layout statements below are
historical; financial rules, preload estimates and calculation-free preparation
remain unchanged.

October30,2026, local only. Started clean `main` at
`cb67dd8a7ad97e68bb05798e64be260f0bbb4bf8`, four commits ahead of local
`origin/main`. Scope: [versioned proposed-input policy](googl-preload-methodology.md),
reproducible preparation, [worked financial record](googl-preload-worked-model.md)
and integration into the existing direct-edit workspace. Phase1 remains
[paused](phase1-universe-pause-checkpoint.md). No push, deployment, cloud changes,
purchases/accounts, new other-company defaults or historical/approval changes.

## Implemented boundary

`preload.rules` owns generic, isolated precision50 HALF_EVEN estimation arithmetic;
`generate` owns Alphabet selections/configuration and input adaptation. `profile`
checks integrity/state/period bindings and generates categorized diffs. The explicit
CLI acquisition module is never imported by the API/financial worker. Raw primary
snapshots and reviewed extraction records are separate from immutable historical
packages. Publication unknowns remain null; Treasury availability is bounded by
actual retrieval, distinct from its October28 observation. No mirrored source changed.

The fixed API endpoint serves preparation only, after bundle/source verification;
no profile-load calculation, network or generic filesystem route. The catalog remains
under64KiB; the profile has a separate192KiB cap. Runtime has109 allowlisted files
plus manifest,24 resource pins including all15 prior pins unchanged. Engine financial
files, strict requests, Decimal/timing/lease/SBC/WC, reverse proof and validation
remain unchanged. Acquisition stores an unreviewed receipt; new disclosure shapes
still require bounded extraction/selection review, not fabricated automatic facts.

GOOGL loads available estimates into separate session baselines. META/AAPL stay
unset. Per-field disclosures expose generated annual values, exact operands,
source/reference periods, classifications, scope limits and reset. Equal-value
edits retain override identity. Refresh compares before explicit adoption; active
overrides and personal notes survive. Annual paths and pending replacement intent
are retained. Replacement controls appear after a constant is actually proposed.
Results/export provenance capture the submitted profile/overrides/revision; active
metadata updates cannot relabel older results. Full Model separates editable draft
rows from submitted assumptions/returned dollar rows and explanations. No JS DCF.

Scenario offsets are configured diagnostics with other ratios inherited, not
probabilities or a regenerated investment/WC plan. Both methods retain separate
inputs/axes; policy axes are centered without clamping. Missing exit selection
blocks only exit; a qualified equity bridge remains separately unresolved.

## Verification performed in this milestone

- Offline/hash, source identity/period/definition and explicit supersession,
  typed gaps versus zero, policy/configuration/provenance diffs, unavailable-state
  rejection, context isolation and engine-adaptation tests passed. Independent
  rational arithmetic checks every annual revenue/EBIT/tax/NOPAT/D&A/investment/WC/
  FCFF and discounted FCFF plus terminal FCFF/value/PVs/EV, with absolute error
  below1e-30 USD against precision50 engine output. This is arithmetic verification,
  not proof of accounting completeness or forecasting accuracy.
- Generated Base/Bear/Bull complete API JSON equals existing CLI JSON; profile GET
  and validation-only are calculation-free. Source pins and original catalog/file
  boundaries remain. No historical corpus retrieval or full repository suite.
- Full frontend regression:222 tests in21files passed. Later affected checks:34
  tests in4files passed after provenance/notes/export refinements. Existing valuation
  regression:199 tests passed. Focused API/catalog/case/terminal/history checks:
  29 passed in a34-test run whose separate preservation failure is explained below.
- The older broad preservation helper still pinned `assumptions.py` before the
  already-approved exit-method split. The file exactly matches starting HEAD.
  Updated that single pin to the reviewed starting commit, without changing source
  or financial expectations. The five preservation tests then passed;22 preload
  tests passed alongside them (27 total). A new exact-byte test covers every
  valuation source/example, all nine unset templates and all15 prior runtime pins.
- Both frontend builds passed. The existing prototype791.23KiB chunk advisory
  remains; no dependencies/build infrastructure changed. Exact final affected
  checks and staged/link/whitespace review are recorded below after completion.

## Actual local browser review

Chrome, actual loopback Python API, dedicated task tab; unrelated tabs/processes
preserved. Verified1440×900 CSS desktop and390×844 CSS viewport, no document-wide
horizontal overflow. Generated GOOGL, not a synthetic-company demonstration:

- Fresh profile populated37 Gordon inputs without calculation. Source/rule
  disclosures distinguish reported basis, estimates and configured assumptions.
- WACC9.123456789 and annual FY2027 growth21.1234567890123456789 were temporary
  interaction overrides; precision, Tab, stale labels and field-specific resets
  worked. They were removed before final generated-model screenshots.
- Refresh showed old/new generated values and active override; explicit adoption
  preserved it. The served candidate changed provenance/publication metadata, not
  economic values. Tests additionally exercise changed numerical candidates.
- Bear WACC11.25 stayed fixed while Base9.1 moved nonoverridden Bull to8.1;
  resetting restored generated diagnostic inheritance. These temporary test edits
  were removed. Actual scenario comparison and revenue/FCFF charts ran.
- Gordon grid center matched single-case EV. Exit started with a specific missing
  multiple error. A temporary **15× software-test override**, not a researched
  exit estimate, ran through the existing engine and13/15/17× grid; then removed.
- Full Model showed current draft versus submitted revision, independent terminal
  ratios and actual operand explanations. Clearing FY2028 expense D&A blocked
  calculation and focused that annual input; field reset restored it.
- Stopped only the identified task API, observed unavailable state and preserved
  entries, restarted its verified bundle and explicitly retried successfully.
- Exact export creation, full submitted result/profile/override/revision content
  and object-URL lifecycle are tested. The supported browser download event timed
  out after6seconds; **file arrival remains unverified**. No browser-policy bypass.

## Financial posture and handoff

The worked record's EV is a conditional, assumption-led starting-model result,
not an approved standing Base or per-share value. Terminal contribution exceeds
100% because explicit PV is slightly negative. Investment/expense D&A commissioning,
the terminal D&A transition, operating tax/WC and acquisition/perimeter remain
judgmental. No complete vintage, current-date timing or financial-input sufficiency
certification follows. Default exit, equity eligibility/claims/awards and share
basis remain open, potentially with unbounded omissions. Market comparison is not
available. Other companies remain unset; all nine original templates are byte-identical.

Local workspace: <http://127.0.0.1:5175/workspace/> → API8002. API PID34564,
working directory `/tmp/valuation-preload-20261030/runtime-final`, read-only109-file
bundle plus manifest, no credentials. Existing Vite listener PID99992, npm parent
99976, serves repository frontend at5175. Other listeners were not stopped.
Reverify PID and cwd before stopping; use TERM on only that task API process.
No deployment, push or automatic refresh. Source acquisition/candidate/export commands
are in the worked record and always require new outside destinations.

Representative actual generated-model screenshots:

- [Desktop](assets/googl-preload-desktop.png)
- [390×844 mobile](assets/googl-preload-mobile.png)
- [Full Model](assets/googl-preload-full-model.png)

Final check receipt and final browser observations are appended below. No prior
trial comparison count or browser download arrival is claimed as rerun/observed.

## Final verification receipt

- Final preparation campaign: **24 tests passed**, including explicit acquisition
  with mocked transport (no new retrieval), actual dated WACC independently checked,
  complete offline CLI generation/export and candidate diff with downstream results.
- Final local API, not only TestClient: all three generated Base/Bear/Bull **complete
  JSON outputs exactly matched CLI**, using temporary outside files removed by the
  test. Base EV1421.564121bn; diagnostic Bear1017.546718bn, Bull2006.393663bn.
  These are conditional estimates, not probability-weighted cases or value bounds.
- Final API/profile/catalog campaign: **26 tests passed** (overlapping preparation
  checks). Final frontend affected campaign after compact replacement behavior:
  **26 tests passed**, **12** source-note/preload checks and **18** method/scenario checks also passed
  after their affected refinements (overlapping coverage). Prior full222-test run is distinct, not
  represented as a rerun of the final tree. Both final frontend builds passed;
  the existing prototype chunk advisory remains.
- **925 changed-document local links/anchors checked**, no broken targets;
  whitespace review passed. Raw acquired HTML contains original publisher whitespace;
  scoped `.gitattributes` marks only those immutable bodies `-text -diff`, preserving
  bytes and avoiding text normalization. Extracted records, code and documentation
  retain ordinary whitespace checks. All six raw SHA256/byte counts and all24 runtime
  resource pins verified; none of the15 old pins changed.
- Nine templates remain byte-identical: **15 case bodies ×37 numerical UNSET values**.
  All pre-existing valuation source/examples, historical JSON/approvals, frozen
  evidence and universe files remain unchanged. No executable company case, saved
  engine output, credentials, temporary file or unrelated change enters the commit.
- Narrow-screen review additionally confirmed an equal-value WACC edit remains an
  override, then resets independently; Full Model selected FY2030 EBIT using returned
  operands, with horizontal scrolling contained inside both tables. Final generated
  Base has no user overrides, default Gordon, and current result. Viewport override
  reset; dedicated local review tab retained. Screenshots above contain actual
  generated GOOGL inputs; no15× diagnostic screenshot is presented as company research.

Concrete remaining dependencies: a supported mature exit selection; qualified
asset/claim/award/share preparation for per-share output; improved expense-D&A
commissioning/terminal transition and acquisition-perimeter treatment before an
investment forecast; bounded mapping review for a genuinely new disclosure shape;
and supported observation of browser download arrival. None authorizes Phase1
resumption, automatic anchor promotion or deployment.

The final source-review pass also preserves deliberate exploratory copies as
explicit input snapshots during later estimate adoption, rather than replacing
their forked rates with Base. **24 focused preload/reverse frontend tests passed**
after that lifecycle refinement; both builds passed again. This adds no reverse
solver or economics. All final test counts above overlap and are not summed as
independent campaigns.
