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

[fixtures.json](../frontend/src/prototype/fixtures.json) contains **48 forward
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

Newly executed: **122 frontend tests** (106 existing + 16 prototype), both default
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
