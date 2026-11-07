# Scope 2 — Company Research Dashboard

**Status: scope approved for logging; implementation NOT STARTED.**
Owner direction: November 7, 2026. This is the second product scope, following
[Scope 1 — DCF pipeline](scope-1-dcf-pipeline.md). Historical Phase 1H/Phase 2A
names retain their original meanings. Registering this roadmap does not start
development, choose a data subscription, approve new numerical defaults or
resume paused universe reviews.

## Objective and initial universe

Connect business performance, observed market behaviour and disclosed valuation
assumptions in a company research dashboard. Initial pilot: **AAPL, META, GOOGL**.
Other tickers follow the [same gated onboarding path](ticker-onboarding-checklist.md)
when explicitly authorized. There is no blanket inheritance of pilot acceptance.

## Placement and experience

For a selected company, its overview becomes the landing view inside the
valuation platform. Keep the logo/home link, search, clear data dates and a
prominent Jump to DCF action. Overview charts and the DCF dip-finder widget sit
above the existing detailed DCF; return drivers and earnings-event analysis are
separate, readily accessible sections. A cross-company platform-home summary
may be specified later; changing the personal portfolio landing page is not
required by this scope.

## Delivery order and gates

| ID | Milestone | Depends on | Initial status |
| --- | --- | --- | --- |
| S2.0 | Shared market/fundamental data foundation | Scope 1 issuer identity/source records | NOT STARTED; provider/rights decisions pending |
| S2.1 | Company overview and price/fundamentals explorer | S2.0, metric-specific sufficiency | NOT STARTED |
| S2.2 | Earnings growth versus multiple changes | S2.0, approved EPS/split/attribution basis | NOT STARTED |
| S2.3 | Earnings-event study | S2.0, sourced event times, benchmark/window rules | NOT STARTED |
| S2.4 | DCF-based dip finder, dated snapshot release | Scope 1 per-share acceptance, S2.0, current-date valuation contract | NOT STARTED |
| S2.4H | Historical DCF-value curves | Separately accepted point-in-time valuation vintages | DEFERRED; not an initial-release obligation |

S2.1 → S2.2 → S2.3 → S2.4 is the agreed product progression. Data and method
prerequisites must pass before their consumer ships. A shared implementation
does not establish issuer-specific readiness.

## S2.0 — Shared data foundation

Create additive preparation/export tooling beside the unchanged Python pipeline.
Publish reviewed, versioned static packages for browser computation. Begin with
daily closing prices and reviewed annual financial history. Extra lookback is
needed for return, TTM or event-estimation windows; a chart range is not proof of
data sufficiency. No market-provider credentials belong in public assets.

The [market data contract](market-data-contract.md) owns security identity, prices,
corporate actions, metric definitions, information availability, restatement
vintages, earnings events, benchmark data and valuation records. Record source
rights for public display, storage, redistribution and exports before ingestion
or publication. Manual laptop refresh and visible last-update dates remain the
initial operating model; do not introduce a hosted refresh backend by default.

Acceptance:

- Provider, permitted uses and pricing are recorded before purchase/use.
- Every series has units, source, period, availability and adjustment metadata.
- Share classes/ticker changes map to the correct security, not just a CIK.
- Missing, stale, unsupported and date-ambiguous states are explicit.
- Reproducible exports, hashes and tests cover splits, dividends, revisions,
  publication timing and missing history without changing Scope 1 financial data.

## S2.1 — Overview and comparison chart

Experience: latest available closing price, financial/reporting/update dates,
1Y/3Y/5Y price history where supported, searchable metric menu, and at most four
additional metrics. Start with few active series. Tooltips show actual values,
units, financial periods, disclosure dates and sources.

Offer indexed-to-100 comparisons for compatible level series with a valid
positive starting value. Use linked panels/native units for ratios and cash
flows with unsuitable/nonpositive bases; never manufacture a meaningful index
from zero or a missing value. Keep price and dividend-inclusive return modes
distinct. Annual observations appear as points or disclosure-date steps without
fabricated monthly/quarterly observations.

Target menu, subject to individual definition/source checks:

| Group | Metrics |
| --- | --- |
| Business | Revenue; operating income; diluted EPS |
| Cash generation | CFO; CFO minus cash capex FCF; standardized FCFF; standardized FCFE |
| Profitability | Gross margin; operating margin; FCF margin; ROIC |
| Capital allocation | Capex/revenue; SBC/revenue; diluted shares; net debt |

The 15-item target is not a claim that 15 validated series already exist. ROIC,
net-debt perimeter, ratio definitions and quarterly/TTM conversion require
documented contracts before exposure. Existing FCFF/FCFE policy/ownership labels
remain visible. Historical and forecast methods cannot be silently joined or
used for automatic calibration. Distinguish latest-restated descriptive history
from filing-available history; research consumers use the appropriate vintage.

Acceptance: limit/keyboard/touch interactions pass; every observation traces to
evidence; unsupported series have a reason; no interpolated financial facts,
misleading axes or future-information leakage into an as-known view.

## S2.2 — Earnings and valuation-multiple return drivers

Experience: user selects a period and sees price change, EPS change and P/E
change, with dividends separately identified. Initial arithmetic uses
P = EPS × P/E and multiplicative factors. Example: 10% EPS growth and 20%
multiple expansion imply 32% price growth, not 30%.

Use a consistent, positive EPS basis and split/share-class treatment at both
endpoints. Begin with clearly labelled annual reported EPS where validated;
TTM follows a separately validated quarterly series. Forward earnings are a
separate basis. Nonpositive or missing EPS makes P/E decomposition unavailable.
Any additive waterfall needs an approved interaction/log-attribution rule;
do not silently add percentage changes or imply causal attribution.

Required data: compatible endpoint prices; EPS periods/available-at times and
vintages; splits; dividend/return basis. A later revenue/margin/share-count
decomposition requires its own matched-income/share-denominator definitions.

Acceptance: components reconcile under the stated arithmetic, endpoint operands
are exportable/traceable, and unavailable or stale inputs never become plausible
zeros or a false P/E result.

## S2.3 — Earnings-event study

Experience: earnings markers; individual and aggregate event views; selectable
predefined trading-day windows; stock-versus-benchmark returns; usable event
counts and exclusions. Candidate windows are [-1,+1], [-5,+5], [-20,+20]; finalize
them before examining outcomes rather than choosing windows for attractive results.

Initial method: daily benchmark-adjusted AR = stock return − benchmark return;
CAR is the sum of daily AR, not compounded buy-and-hold relative performance.
Both return series use consistent dividend/corporate-action conventions and
trading calendars. A later alpha/beta market-model method needs a strictly
pre-event estimation window and separate validation.

Required data: daily security/benchmark history with sufficient lookback; actual
earnings-release timestamp/time zone/source; exchange sessions/holidays; fiscal
period identity. Use an official release/IR or earnings exhibit source: a later
10-K acceptance time is not automatically the earnings announcement time.
After-close releases map to the next session; unknown/inconsistent times require
explicit exclusion or a separately labelled coarse-date analysis.

Consensus/earnings-surprise analysis is optional and not included initially.
It needs pre-announcement estimate vintages and compatible reported earnings.

Acceptance: event/session alignment, no post-event estimation inputs, fixed
window definitions, reproducible AR/CAR, excluded-event reasons and sample sizes.
The three-company sample supports exploratory studies, not generalizable alpha
claims or a validated trading strategy. Overlapping events/confounding news
must be disclosed in interpretation and any later statistical tests.

## S2.4 — DCF-based dip finder

Experience: closing price; dated Bear/Base/Bull per-share values; selected-model
discount/upside; user-selected margin-of-safety threshold; model/data age and
readiness status; link to the assumptions. Use FCFF-derived equity value per
share as the primary basis; display FCFE separately. Never compare price with
enterprise value or silently average FCFF/FCFE values.

For price P, positive model value V, chosen historical high H and user margin m:

- Discount to model value: (V − P) / V.
- Upside to model value: (V − P) / P.
- Drawdown from high: P / H − 1, using a declared split-adjusted price/window.
- Threshold price: V × (1 − m).

For V=100 and P=80, discount is 20% and upside is 25%. This is a definition
example, not an approved company estimate or default threshold. Bear/Bull values
are scenarios, not probabilities, guaranteed boundaries or a price floor.

**Prerequisite:** existing accepted DCFs have fiscal-end origins and later-filed
inputs. A separate current-date valuation contract must address elapsed forecast
periods, information cutoff and dated cash/debt/claims/share inputs before current
price-based classifications are enabled. Preserve existing fiscal-end results;
do not merely relabel their valuation date or mechanically roll them forward.

Required data: correct-class price with timestamp/adjustments; dated accepted
scenario assumptions; equity/ownership/award bridge; source and model versions;
approved date-alignment/freshness rules; explicit user threshold.

Acceptance: correct denominators/units, compatible dates/classes/splits, explicit
method selection, no automatic investment recommendation, and no classification
for incomplete, stale, nonpositive-value or misaligned models.

S2.4H is a separate future milestone. Dashed historical value lines need actual
dated model snapshots or an explicitly labelled, hindsight-controlled historical
reconstruction. Save data/assumptions/policies/date versions at each point. Never
backfill current assumptions into history or alter historical valuations when a
user edits today's model. No initial-release historical valuation line is promised.

## Decisions still required before implementation

| Decision | Resolution required before |
| --- | --- |
| Market provider, display/storage/export rights and budget | S2.0 ingestion/publication |
| Price versus total-return convention, adjustment base, security mapping | All market consumers |
| Metric formulas/perimeters and initial supported subset | S2.1 metric exposure |
| Annual/TTM EPS basis and attribution interaction rule | S2.2 |
| Benchmark, event/window/timing and later estimation rules | S2.3 |
| Current-date valuation, freshness and threshold policy | S2.4 |
| Original versus reconstructed historical valuation records | Separate S2.4H approval |

## Out of initial scope and completion language

No broad-universe resumption, specialized-issuer forced DCF, live/intraday feed,
automated trading, composite moat/solvency scoring, hosted refresh service or
historical intrinsic-value reconstruction is authorized by this planning record.
Excel import and the agreed optional-ten-year wording are separate Scope 1
follow-ups, not silently completed or absorbed here. Existing GCP resources are
not retired. Do not change original Python or approved financial conventions.

Close a feature only when shared tests and named-issuer acceptance both pass;
close Scope 2 only after its initial-release milestones pass for all three pilots.
Retained accepted source qualifications are disclosed, not hidden or mislabeled
as exact facts. Historical reconstruction and other deferred work stay separately
tracked; broader research/preparation work remains OPEN/PAUSED as recorded.

See [per-ticker register](scope-2-ticker-register.md), [onboarding checklist](ticker-onboarding-checklist.md)
and [method proposals](financial-methodology.md#scope-2-methodology-proposals--november-7-2026).
