# Local investor experience prototype

## Scope and design grounding

This is a **product-design review**, not production integration or new financial
approval. Starting `ba23b49c35df6d5f6b6924ccbdd1f9db4e388433` was clean `main`,
five ahead of local `origin/main`. The separate approved calculator and its API
remain unchanged. Deployment/domain migration are paused; [Phase 1 remains
paused](phase1-universe-pause-checkpoint.md). No cloud calls or configuration,
portfolio edits, hosted release, push or actual-company valuation occurred.

The portfolio checkout was read-only: `a115327325754cb741b696fa115f38a30e63c866`,
clean `main`, two ahead. No `AGENTS.md` was present in that checkout or its checked
Website/Projects/user ancestors; the valuation repository instructions were read.
Its actual CSS/HTML uses Playfair Display/Georgia headings, Inter/system body,
IBM Plex Mono/monospace detail, navy `#0a1628`, gold `#c9a84c`, white surfaces,
light rules, 4px corners and compact text links. The prototype carries these
relationships into a denser application: small portfolio masthead, serif company
and result headings, mono financial entries, gold active indicators and a restrained
navy value panel. It uses local system fallbacks, with **no external font request**.
No portfolio hero, portrait, marketing statistics or production CSS was copied.

Public page content/documentation was reviewed, not authenticated product sessions:

| Reference | Interaction lesson and limits |
| --- | --- |
| [Stock Analysis](https://stockanalysis.com/tools/dcf-calculator/) | Compact assumption/result pairing, explicit terminal share of value and an identified matrix reference cell. No buy-zone or buy/sell language is borrowed. |
| [EvidInvest](https://evidinvest.com/tools/dcf-calculator) | Reuse the forward case for reverse interpretation; keep terminal dependence visible. Its public model and operating-growth sensitivity differ from our scope. |
| [Talval](https://talval.com/tools/dcf-calculator) | Place the implied-growth explanation, reconciliation and sensitivity near the main result. Its FCF-growth/fade model does not establish our revenue/operating FCFF conventions. |
| [Alpha Spread bull-case page](https://www.alphaspread.com/security/nasdaq/amzn/dcf-valuation/bull-case) | Case-specific analysis/navigation informed the persistent case context. The accessible page reported an unavailable editor; no hands-on scenario editing or gated features were tested. |

These references supply product interaction ideas, not forecasts, prices, formulas
or evidence for an actual issuer. Their example security values were not imported.

## Entry and isolation

```bash
npm --prefix frontend run dev:prototype
# http://127.0.0.1:5174/prototype/

npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend run build:prototype
```

Use the repository's Node 22.12+ tooling (review used Node 22.14.0). No new dependency,
framework, package installation, API route or infrastructure. The prototype entry
is [prototype/index.html](../frontend/prototype/index.html), with isolated React,
CSS, state and fixtures in [src/prototype](../frontend/src/prototype/Prototype.tsx).
The separate [Vite configuration](../frontend/vite.prototype.config.ts) has no API
proxy. Existing `main.tsx`, `App.tsx`, CSS, API client, default Vite configuration,
examples and schemas are byte-unchanged. Only two package scripts are added.

The separate build emits ignored `frontend/dist/prototype-preview/`, with relative
assets and `prototype/index.html`. Its relative URLs support mounting the build
under `/valuation/` with the entry at `/valuation/prototype/`; this is not a new
Hosting rewrite or an approved publication artifact. The existing calculator
remains at <http://127.0.0.1:5173/> with its prior local API. The prototype at 5174
needs **no API**. Default production build still emits the unchanged calculator;
run that before the separate prototype build because it clears `dist/`.

## Functional workspace, illustrative economics

The persistent header names **Northstar Instruments, a fictional company**, its
synthetic FY2025 USD1,000m revenue anchor, December 31, 2025 analytical date and
fictional January 29, 2026 information cutoff. A persistent prototype banner,
illustrative result labels, source/methodology disclosure and session-only footer
qualify the entire experience. There are no actual META/GOOGL/AAPL identities,
quotes, accounts, local/session storage, cookies or saved cases. Reload resets work.
External portfolio navigation is an ordinary explicit link, not an automatic call.

| Workflow | Functional interaction | Calculation boundary |
| --- | --- | --- |
| Valuation | Constant five-year and expandable annual entries, confirmed replacement of varied rates, independent terminal editing/confirmed FY2030 copy, notes, synthetic history, explicit shared bridge and manual dated comparison price. | Preview looks up a complete prepared input state. Unsupported edits stay not calculated/stale; old figures are identified as earlier illustrations. Bridge edits invalidate per-share eligibility without changing operating EV. Price differences are display-only, require positive finite price and matching analytical date. |
| Reverse DCF | Selected forward case, dated price/advanced EV target, explicit interval, held-fixed review, prepared success/unreachable/uncertified states and implied-versus-forward path. | Replaces **all five revenue-growth rates** with one constant rate. No FCF-growth or arbitrary-variable solving. Unsupported combinations have no preview. Uncertified does not prove absence of a mathematical root; no guessed solution is shown. |
| Scenarios | Create Bear/Bull from exact Base copies; one selected-case editor, annual/terminal detail, notes, removal confirmation, marked driver differences and revenue/FCFF comparisons. Explicit optional fixture loading and unexpected ordering example. | No optimistic/pessimistic economics generated on creation. No probabilities, weighted target or forced ordering. Shared bridge/shares are identical across cases. Only current prepared results appear in comparison paths. |
| Sensitivity | Select a completed scenario; edit WACC/g ranges and steps, preview supported grids, inspect without mutation, then confirm applying only WACC/g. Invalid cells have reasons and cannot be applied. | Finite prepared WACC × terminal-growth grids only, not operating-driver sensitivity. Other inputs fixed. Applying stales the selected case and grid; explicit re-preview is required. An experiment is not a probability range or investment bound. |

Essential investment scope, working-capital full-revenue denominator/sign, SBC/lease
cost treatment and terminal sustainability questions stay visible next to entries.
The optional share reference uses issued synthetic common shares, one class,
selected component populations and explicit unresolved awards/unidentified claims.
It is not fully diluted fair value or complete financial coverage. Loss taxes,
lease treatment and all other actual engine conventions are unchanged.

At narrow widths, the summary precedes inputs, annual inputs become year groups,
scenario cards stack and comparison drivers become labeled case tiles. The 3×3
sensitivity grid retains readable touch targets; detailed annual cash flows remain
in a labeled, scrollable disclosure. Keyboard tabs use arrows/Home/End, controls
have visible focus/labels, dialogs default to keeping inputs and return focus,
errors associate with fields, and changes/invalid cells use words as well as color.

## Fixture provenance and limits

[generate_fixtures.py](../frontend/prototype/generate_fixtures.py) is an **offline,
synthetic-only** preparation script; the website neither imports nor executes it.
It invokes the existing A/B/C and bounded reverse engines on the existing synthetic
revenue-100 identity, then uniformly scales monetary amounts **and shares** by
10,000,000. Displayed USD millions and millions of shares are thus engine values
×10; USD/share remains unchanged. This provides a fictional USD1bn revenue company
without adding a new engine anchor or touching company packages. No actual-company
forecasts or executable actual-company cases are created.

[fixtures.json](../frontend/src/prototype/fixtures.json) initially contained **48 forward
illustrations and 12 reverse records**, not arbitrary calculators. Four profiles:
steady (10% growth/24% margin), lower (6%/20%), higher (14%/27%) and deliberately
reinvestment-heavy (10%/15% with 35% investment/revenue). All have independently
specified terminal inputs. The last is a diagnostic for mixed-sign cash flows and
uncertified interval-wide uniqueness, not a sustainable forecast recommendation.
The prepared bridge is USD150m eligible assets, USD200m financing, USD25m other
claims and 100m issued common shares; unresolved awards/claims remain explicit.
None are company defaults or financial approvals.

Supported standard grid: WACC 9/10/11%, terminal growth 2.5/3/3.5%. Invalid-pair
illustration: each axis 2/3/4%, retaining only valid g<WACC cells. Prepared reverse
targets: USD25/share, USD1,000/share (outside the normal interval), USD2,500m EV;
normal growth interval −10% to 30%, heavy diagnostic interval −100% to 100%.
They are explicit design fixtures, not approved economic ranges.

The browser only matches inputs and renders fixed result components. Decimal
arithmetic is limited to input checks, canonical comparisons, unit/display rounding
and reference/entered-price difference. SVG coordinates use ordinary display
numbers. There is no browser FCFF, discounting, Gordon formula or root search.
Restoring a supported input combination still requires explicit preview. There is
no hidden queue, API fetch, automatic company calibration or persistence.

## Verification and next decisions

At the initial `5466345` milestone: **122 frontend tests** (106 existing + 16 prototype), both default
and isolated TypeScript/Vite builds, independent fixture component/reconciliation
assertions, source/template/portfolio preservation, local links, whitespace and
staged-scope checks. No financial full suite, cloud tests or actual-company run.
The offline generator was used to create the synthetic fixture records; this is
not evidence of new financial-input acceptance.

Actual Chrome review covered desktop **1440×1000** and **390×844**: forward →
qualified shares; successful reverse, outside-bounds and uncertified states;
explicit Bear/Bull copy/edit/compare; unexpected ordering; scenario sensitivity
inspection/confirmation/apply; return to forward with stale status and retained
notes/inputs. Annual varying-to-constant replacement and keyboard tab/dialog
behavior were also inspected. Representative captures of four tabs and narrow
views are outside the repository. Narrow page width did not exceed the viewport.
This is resized desktop testing, not mobile virtual-keyboard or full accessibility
certification. Existing review servers were preserved; one loopback prototype
server is left running for the user's review.

Design approval is needed before replacing the existing calculator. Future work
must separately scope the public scenario/sensitivity/reverse API adapters using
existing strict contracts, bounded execution/errors, source and date declarations,
shared bridge/coverage rules and actual engine traceability. No endpoint, new
financial formula or changed convention is proposed here. Product/economic choices
still include actual-company entry/freshness, price-date policy, scenario ownership
and comparability, user-specified axis limits, reverse interval/error presentation
and mobile annual-table usability. The prototype settings approve none of them.

**Public-preview withdrawal remains October 23, 2026, 14:17:28 Asia/Dubai /
10:17:28 UTC.** This task neither performs nor extends it. No push, deployment,
billing/IAM, DNS, Netlify, live Hosting or portfolio changes are authorized here.


## Connected journey checkpoint

Starting HEAD `5466345103f16cdf36135012f24a69e4535916d3` was clean `main`,
six ahead of local `origin/main`. This local-only extension preserves the same
synthetic identity, analytical date/cutoff, palette, isolated entry and financial
contracts. No engine, API, calculator, portfolio, historical, template or cloud
change is included. The withdrawal deadline above is unchanged.

Valuation now opens a compact **selected-case overview**: current EV/qualified
issued-share reference and eligible price comparison; conditional reverse growth
and target; Bear/Base/Bull values and first-year driver differences; and that
case's grid status, WACC/g reference and terminal contribution. Unperformed,
unsupported and stale analyses are identified in words. Detailed editors, paths
and annual tables remain in their workflow views. Contextual links carry the
selected case, and Return to overview restores a relevant action's focus.

### Shared workspace and dependencies

[workspace.ts](../frontend/src/prototype/workspace.ts) owns one session-only
workspace: cases keyed by stable names, financial revisions, shared bridge/shares,
one comparison price/date, and per-case reverse form/result, grid settings/result
and inspected cell. Exploratory cases have separate incrementing identities and
record source identity/revision and target or rate-pair relationship. Notes do
not increment financial revisions. A new case starts without its own analyses;
selecting another case restores its work instead of relabeling the previous one.

| Change | Affected illustrations | Preserved |
| --- | --- | --- |
| Annual, terminal or WACC/g inputs | Selected forward result, reverse and grid; comparison excludes stale paths | Sibling cases/analyses, notes, shared populations |
| Shared bridge/shares | All qualified equity/share references and price-target reverse results | Operating EV, EV-target reverse and EV grid |
| Shared comparison price/date | Display comparison and reverse using shared price | Business value, grid, independent reverse overrides |
| Reverse override/bounds | That case's reverse result | Shared comparison price, forward case, sibling analyses |
| Grid settings | That case's grid requires explicit preview again | Operating inputs, forward/reverse results |
| Notes/navigation | No financial invalidation | All current illustrations |

These correct the earlier global reverse/grid state and overly broad bridge
invalidation. A bridge edit can leave the EV grid current while removing its
per-share presentation. Analysis keys bind source identity/revision and relevant
inputs; they do not authenticate economic assumptions or financial approvals.

### Guided illustrative journey

1. From the overview, **Start guided illustrative journey** explicitly loads the
   synthetic USD25/share comparison/date and prepared shared bridge. It preserves
   entered cases/notes and performs no analyses. Starting from the original Base
   gives the supported complete example; unsupported edits still need an explicit
   prepared-illustration replacement or remain not calculated.
2. Preview valuation, return to overview and **Explain this price**. Missing
   forward/share/price prerequisites route to their control. This action uses the
   shared price/date; **Review price expectations** instead restores that case's
   existing target, including an explicitly independent override.
3. Explicitly preview reverse. A prepared success shows the forward/implied
   revenue paths and offers **Create scenario from implied growth**. Confirmation
   shows the exact solved constant rate/target and preserves the source. The new
   exploratory case replaces only the five annual revenue-growth rates, with all
   remaining annual ratios, terminal ratios, WACC and g unchanged. Preview it
   explicitly. It is not an independently researched forecast.
4. Compare scenarios: Bear/Base/Bull remain the strict three-case set. Exploratory
   cases are separate, and a current implied-growth case supplies a labeled
   reference overlay, never a fourth probabilistic outcome. Bear/Bull still start
   as exact independent Base copies; no overwrite or economics is automatic.
5. **Test sensitivity** on a completed case carries that exact identity. Explicitly
   preview the grid, inspect a cell without mutation, then either confirm applying
   its WACC/g or confirm a new exploratory case changing only that pair. The source
   is preserved on a fork. Preview changed/new cases explicitly; return to overview
   to see the case-associated state. Case selection restores earlier grids/cells.

No tabs launch calculations or multiple analyses. Overrides, copying and application
are explicit. The strict engine scenario contract is unchanged; exploratory cases
are a prototype workspace concept, not a new engine scenario label.

### Additional prepared fixtures and verification

The offline script now prepares **120 forward illustrations and 12 reverse
records**. The original four profiles, 48 forward records and 12 reverse records
are unchanged. Six successful prepared reverse conditions each gain a family of
12 forward WACC/g pairs using the exact solved growth rate through the existing
engine. This supports forward previews and grids after exploratory creation.
Reverse solving for those new cases is not prepared and honestly remains not
calculated. Other arbitrary edits/targets remain unsupported. No browser financial
formula, API call, account, persistence or actual-company case was added.

Current checks: **133 frontend tests** (106 existing + 27 prototype), including
linked navigation/focus, exact fork differences, per-case preservation and
selective invalidation, plus both TypeScript/Vite builds. Original fixture records
and all protected sources/templates are compared against starting HEAD. The
isolated build warns that its synthetic-fixture bundle exceeds 500 kB; this is a
local design artifact, not production performance acceptance. The original
calculator bundle remains unchanged.

The earlier desktop/390×844 browser record above belongs to the initial milestone,
not this extension. **Current connected-journey browser verification is pending:**
browser inventory returned no available browser, the previous Chrome connection
was unavailable, and native Chrome's computer-use pipe failed to start. Component
tests exercise the entire linked journey but are not screenshots or browser/mobile
acceptance. No current screenshots are claimed. The existing prototype/calculator/API
servers are preserved and the prototype responds locally on port 5174.

Future design/API work still requires separate scope: approval of the connected
experience, actual-company data/input freshness, price-date rules, ownership and
lifecycle of exploratory versus strict scenarios, supported input/range limits,
reverse failure presentation and complete narrow-screen/browser acceptance. Future
adapters must use the existing [scenario](phase2-scenario-workflow.md),
[sensitivity](phase2-sensitivity-workflow.md) and
[reverse](phase2-reverse-dcf-workflow.md) contracts with their source/date/coverage
and explicit execution boundaries. This checkpoint authorizes no integration or
deployment and does not resolve economic consistency or investment readiness.
