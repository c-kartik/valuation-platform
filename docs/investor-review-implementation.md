# Consolidated investor review — local implementation

## Contracts established before implementation

Scope is META, GOOGL and AAPL; Phase 1 expansion stays paused. The starting clean,
synchronized main is `fa91eb662911915a6d6aa74d4b02637f277d4b23`; performance source
`377b5b837ce05c794becccb85d2757f8a762994d` remains authoritative for request-local
validated anchors. This milestone is local only; no push/deploy/cloud changes.

The data boundary distinguishes fiscal/report end, SEC filing date/acceptance,
source retrieval/check time, retained fiscal-end analytical origin, and exchange-
timezone opening-price observation. No timestamp manufactures an information
cutoff. Current context is separate from pinned approved revenue anchors and
frozen historical packages. A newer filing with incomplete preparation is labeled
explicitly; its observations are not silently approved valuation inputs.

SEC submissions/companyfacts use the existing SEC transport and typed parsers,
with exact source/period/accession/units, bounded field selection and explicit
missing values. No quarterly annualization, unsupported TTM or reconstructed
claims completeness. Interim context does not authorize a new rolling/stub-period
DCF. The current engine still discounts at its approved fiscal-end origin;
current-market comparison remains unavailable until dates, share classes, price
adjustments and the economic bridge perimeter are compatible.

Credential presence check found SEC_USER_AGENT but no supported market API key.
Massive is the proposed narrow adapter: documented regular-session opening data,
unadjusted prices, source-bound sessions and corporate-action checks. Alpha Vantage
(personal noncommercial terms) and Twelve Data (separate external-display rights)
were considered. No account/subscription/paid calls or undocumented scraping.
A key alone does not grant display rights. Until an appropriate entitlement and
permitted local-display use are configured, market status is unavailable. No
synthetic observation is shown as current. Public redistribution is separately
unapproved; no persistent market cache or browser credentials.

Market-implied EV = dated opening-reference equity value − the same eligible
assets + financing + other claims. Reported balances are not eligibility/coverage
approval. No EPS denominator as current shares, no automatic GOOGL all-class
price equivalence, no tax/lease/award/settlement duplication. Comparisons use one
snapshot and the existing bounded certified constant-five-year-growth solver;
search bounds are explicit diagnostic policy, never silently widened. Failure
exposes no substituted root. Forward calculation survives missing market data.

Sources consulted October 29, 2026:
- [SEC API documentation](https://www.sec.gov/edgar/sec-api-documentation)
- [Massive custom bars, adjustment and plan delay](https://massive.com/docs/rest/stocks/aggregates/custom-bars)
- [Massive market holidays](https://massive.com/docs/rest/stocks/market-operations/market-holidays)
- [Massive terms and individual/business distinction](https://massive.com/legal/terms)
- [Alpha Vantage terms](https://www.alphavantage.co/terms_of_service/)
- [Twelve Data terms](https://twelvedata.com/terms)

The sections below record implementation and actual verification. These
contracts approve no financial inputs or current-date economic convention.

## Implemented boundary and current source basis

The main local navigation is Valuation / Scenarios / Sensitivity. Forward review
renders existing A/B/C outputs, a dated market-review status, chart and optional
exact JSON download. Equity remains optional. Sources/methodology contains the
submitted limitations and dated source context. No visible JSON, manual cutoff/
analytical date, reference-calculator link, solver certificate or standalone reverse
form remains in the main workflow; legacy CLI/reference interfaces remain intact.

| Context company | Latest checked report end | Filed | SEC accepted (UTC) | Companyfacts checked (UTC) | Selected observations |
| --- | --- | --- | --- | --- | --- |
| META | 2026-09-30, 10-Q | 2026-10-22 | 2026-10-22 00:00:08 | 2026-10-29 15:24:58.644839 | 8 |
| GOOGL | 2026-09-30, 10-Q | 2026-10-29 | 2026-10-29 00:29:06 | 2026-10-29 15:24:59.659089 | 9 |
| AAPL | 2026-06-27, 10-Q | 2026-07-31 | 2026-07-31 10:01:02 | 2026-10-29 15:25:01.131438 | 11 |

The snapshots ([META](../data/investor-context/2026-10-29/meta.json),
[GOOGL](../data/investor-context/2026-10-29/googl.json),
[AAPL](../data/investor-context/2026-10-29/aapl.json)) retain exact accession,
concept, amount, period/date, USD/shares, raw-response hashes and source URLs.
There were exactly six bounded live SEC requests: submissions + companyfacts for
each issuer, using the existing identified SEC client. No market price request.
This is an October 29 check of available SEC data, not an automatically fresh feed
or complete note/class/claims review. Raw retrievals were temporary; public
context-only snapshots are distinct from original approval/source records.

`review.prepare` reuses existing parsers/concept and balance-sheet candidate
policies; no TTM was derived. Alternative concepts are retained, never summed.
Quarter/YTD start/end remain explicit. Filing-cell precision and unprepared note,
lease, claim, eligibility, class and award fields remain unknown. All three are
**NEWER_FILING_AVAILABLE_PREPARATION_INCOMPLETE**, valuation-anchor approval false,
current-consumer sufficiency NOT_ASSESSED, information cutoff null. The retained
FY2025 approved revenue seeds remain the only actual-company calculation anchors.
Company preparation records receive append-only scope notes; historical approvals
and omission decisions are not transferred to current valuation use.

For a later explicit refresh, `SEC_USER_AGENT` must identify the SEC caller:
`PYTHONPATH=src .venv/bin/python scripts/prepare_investor_context.py /tmp/new-context`.
The destination must be new. This produces review observations, not approval or
activation; reviewed snapshot paths/resource pins require an explicit code update.
No scheduled retrieval, arbitrary ticker, automatic refresh or new anchor adapter.

## Market, timing and execution

The adapter is configured only server-side with `MASSIVE_API_KEY`,
`MARKET_LOCAL_DISPLAY_ENTITLED=yes` and `MASSIVE_DATA_DELAY` (actual plan delay).
Local display must be permitted under the account terms; setting these variables
is a declaration, not proof of a license. No credentials are sent to the browser,
committed or put in URLs. No account, paid subscription/call or cache was created.
Public/external redistribution rights remain separately unapproved.

At/after 09:30 America/New_York, a weekday review tries the documented unadjusted
regular-session open-close summary. If unavailable, or pre-open/weekend, returned
session bars in a bounded 14-day window identify the last actual prior session;
a separate summary supplies that day's regular opening price. At most three
bounded HTTP calls, never a guessed holiday or premarket/adjusted opening. The
returned ticker/date must match; source observation and check timestamps remain
separate. Split compatibility defaults false and cannot be inferred from a key.
The immutable source-bound snapshot is fetched once per explicit forward review,
never per solver iteration, scenario or grid cell. No provider market cap is used.

`/api/v1/review/run` accepts the existing strict case and internally packages a
server-supplied snapshot. Retrieval happens outside the network-disabled child;
forward execution and optional reverse share one validated anchor. The existing
shared job lock, late-response checks, cancellation, 35s child wall / 30s CPU,
256KiB intake and 2MiB output limits remain. Provider lookup has a separate 12s
outer deadline (8s individual fetch timeouts); a blocked thread may finish its
bounded read after cancellation. A failed quote returns usable forward output.
Validation-only routes remain calculation-free and make no quote requests.

New investor scenario/sensitivity/reverse v2 metadata explicitly supports null
unknown cutoffs; missing or invalid fields still fail. Older v1/analyst contracts
retain their required declared dates and exact financial results. No display or
retrieval timestamp substitutes for a cutoff or changes discount exponents.
No current-date stub/rolling convention is approved. Current market comparison
also needs compatible shares/classes, split treatment and dated financial
perimeter. Thus **genuine current-market/implied-growth output is unavailable in
this local handoff**, despite fixture-tested adapter/reconciliation/solver wiring.

Conditional opening-reference market cap is price × selected dated shares, not
EPS shares. Market EV subtracts the same selected eligible assets and adds the
same financing/other claims as the forward bridge. Signed operands, dates and
class scope are displayed. No completeness or eligibility proof is inferred.
Model EV differences use market EV as denominator; equity/per-share comparisons
are separately qualified. CAGR is an isolated Decimal endpoint calculation,
not the arithmetic average of growth rates or a cash-flow attribution.

Certified reverse solves one constant annual growth rate in fixed **−50% to +50%**
diagnostic bounds, holding all remaining annual/terminal/bridge assumptions fixed.
No widening or fallback root. Existing certificate, residual tolerance, fresh
verification and honest unreachable/inconclusive/iteration-limit outcomes remain.
Numeric-budget failures withhold the solve. Exact price/share arithmetic is
isolated Decimal; display rounding never becomes a target or engine operand.

## Editing and presentation

Bear/Bull are session working copies of the unset/user-entered Base. Untouched
fields follow Base; explicit overrides remain independent and visible. Resetting
loses edits only after confirmation. Annual edits do not copy independent terminal
ratios. Shared complete bridge inputs enable per-share scenarios; incomplete
bridges leave EV comparison available. Financial edits stale dependent results;
bridge edits withhold bridge-dependent market results while retaining operating EV.
Scenario runs do not retrieve quotes or manufacture market-linked growth; unchanged
forward review metadata is retained only for an identical current result snapshot.

Charts use paired revenue/FCFF bars on one labeled USD-billions scale, with metric
controls, case comparison, pattern/position legends, selected-year readout,
keyboard/focus/tap selection and a data table. Only the verified retained annual
revenue anchor is historical; no historical FCFF is invented. Negative values use
a zero baseline; zero and small nonzero values remain distinct. No new chart library.
Money formatting adds trillion headlines; ordinary percentages have two decimals,
percentage-point gaps are labelled, matrices use fixed units, exact exports retain
all submitted values and provenance. SVG coordinates alone use normalized numbers.

Sensitivity requires explicit generation or entry, then explicit calculation.
The 3×3 helper uses entered WACC ±1 percentage point (narrower near zero) and g
±0.5 point (narrower near −100%). Axes are visible/editable diagnostics, not default
forecasts, probabilities or confidence/fair-value bounds. Advanced entry preserves
11×11 limits and invalid-pair nulls. Keyboard/tap inspect and confirmed apply remain.
No additional cell actions or confidence score.

## Verification actually performed October 29

- **188 valuation tests**, including unchanged core byte pins, exact reverse
  certification/metrics/bisection AST checks and legacy CLI JSON compatibility.
  Only nullable v2 metadata and private request-local executor binding are normalized
  in wrapper preservation checks; core financial functions remain pinned.
- **46 affected API/preparation regression tests**, including real child limits,
  cancellation/busy/reap/recovery and three-anchor grid/reverse/CLI checks. Their
  newly executed grid/reverse tests reported 444 + 336 independent comparisons.
- **11 new review tests**: typed context/unknowns, source timing, matching ticker/
  session, weekends/holiday/pre-open, adjustment/split/class gates, exact signed
  reconciliation, certified target reproduction/fresh execution, single anchor
  preparation, non-average CAGR, hostile caller Decimal context, strict v1 versus
  nullable v2, calculation-free validation, provider failure and real shared-gate
  timeout/cleanup/retry. Fixtures are software-only, not live market verification.
- **Seven preservation/catalog checks**; existing pinned resources, original
  templates and historical preparation remain unchanged. No historical full suite.
- **195 frontend tests**:
  inheritance/overrides/terminals/reset, late responses/cancel/busy/retry,
  exact percentage/money conversion, paired negative/zero/missing chart data,
  trusted review response checks, stale bridge-market separation, fixed-unit
  grids and exact Blob/download-link lifecycle. Both default and prototype builds.
- Against the final running immutable local API: **12 complete API/CLI JSON
  matches**, six further sensitivity-corner CLI checks, **1,161 independent exact
  rational comparisons**, across all three retained revenue anchors and both EV/
  synthetic equity scopes. Exact fractions independently reconstruct compounding,
  tax-on-positive-EBIT, D&A/investment/WC signs, FCFF, discounting, terminal and
  bridge/share arithmetic; comparison tolerance is `1e-30 + |expected|×1e-46`.
  These additional temporary inputs were deleted automatically; no company
  forecast/bridge selections were approved or saved.

The actual Chrome journey used a deliberately arbitrary software case on GOOGL's
retained USD402.836bn revenue: annual growth 10%, margin 20%, tax 25%, D&A 5%,
investment 10%, WC 2%, WACC 25%, g 5%, explicit terminal ratios 20/25/5/10/2%.
This is **not a GOOGL forecast**. Browser EV USD200.90bn = displayed explicit PV
111.61bn + terminal PV89.29bn; contribution44.44%, CAGR10%. Diagnostic Bear8%
growth and Bull12%/22% margin produced displayed EV187.62/200.90/237.01bn.
Independent rational/CLI results match these displayed values. These are software
observations, not a repeat of the prior analyst valuation trials.

Desktop (verified 1440×1000 CSS) and actual **390×844 CSS** review exercised inline
inheritance, independent terminals/overrides, confirmed reset, comparison/chart
selection, arrow-key focus, tap/click and table access; explicit grid generation,
advanced axis editing, calculation, keyboard/inspect/apply confirmation; negative
FCFF (−73.96bn first year under a −10% Bear margin diagnostic), zero EV/FCFF and
undefined contribution; quote unavailability and actual local API outage/retry.
Trial values remained after outage; retry succeeded against the rebuilt local API.
The viewport override needed compensation for the existing Chrome zoom and was
checked through actual DOM dimensions; it is reset before handoff. A discovered
mobile overflow from absolutely positioned hidden table labels was fixed by
containing them in positioned cells; page width then stayed within the viewport.

Final review found and fixed a development Strict Mode export defect: a URL
created during render was revoked by effect cleanup before reuse. URLs now have
an effect-owned create/revoke lifecycle and replacement hides any obsolete link.
Exact precision/provenance/nulls, filename, Strict Mode setup-cleanup-setup and
replacement/unmount pass the focused regression. Browser delivery was retried
with the separate synthetic example after the fix; download observation still
timed out. Chrome downloads inspection was rejected by browser security policy;
no workaround was attempted. **Actual downloaded-file arrival remains unverified**.
The prototype build retains its existing >500KiB chunk warning. An initial concurrent
frontend run hit a test's 5s timeout; an isolated complete rerun passed. A new real-
worker timeout test initially expired before spawn under parallel build load; its
fixture-only deadline was raised from 1s to 3s and the check passed. Production
execution ceilings were not changed.

## Local handoff and preserved scope

The review is <http://127.0.0.1:5175/workspace/> → **local** 127.0.0.1:8002;
`VALUATION_LOCAL_API` accepts only explicit numeric loopback HTTP. No cloud fallback.
Frontend npm launcher PID99976 / Vite listener PID99992; API PID2044 runs the
94-entry verified, read-only bundle at
`/tmp/valuation-investor-review-20261029/runtime-final`. Minimal process metadata/
logs remain beside the running bundle. Raw SEC responses, trial scripts/cases/
outputs and obsolete task bundles are removed; browser test drafts are cleared.
These process identities are time-specific: check them before stopping.

Safe stop: verify `ps -p 2044,99976,99992 -o pid,ppid,pgid,command` and the listeners,
then `kill -TERM 2044` and `kill -TERM -- -99976` (owned frontend process group).
Unrelated API8000/workspace5173/prototype5174/built4173 and earlier authenticated
proxy/supervisor are preserved; any earlier scheduled proxy expiry is independent
of this local API and is not extended by this milestone. Normal authentication
stores remain untouched.

Local commit only, no push/deployment, provider/account creation, hosted change,
portfolio edit, IAM/billing/DNS/Netlify/Firebase action or new infrastructure.
Core formulas, frozen histories, source approvals, nine company templates and
Phase 1 pause remain unchanged. New snapshots are context-only; complete financial
sufficiency, licensed market access and current-date economics remain unresolved.
