# Scope 2 — market and research data contract

Planning contract, November 7, 2026. Implementation NOT STARTED. This defines
requirements for [Scope 2](scope-2-research-dashboard.md), not selected providers,
validated new metric values or an authorization to purchase subscriptions.

## Common observation envelope

Every package/observation needs a stable record ID, schema/data/policy version,
security identity, source reference/URL, source retrieval/update time, units,
classification (reported, derived or analyst estimate), and readiness/limitations.
Derived observations retain operand IDs, formula/version and missing-input reasons.
Packages have reproducible manifests/hashes and a visible last-update date.

Separate the financial period, original public availability, retrieval, analyst
review and valuation timestamps. A retrieval/review date is not proof of historical
availability. Date-only evidence must not silently become an exact midnight event.
Store the original timestamp/time zone, normalized instant when justified,
precision and evidence; preserve unknown time rather than guessing.

## Datasets and required fields

| Dataset | Required fields/controls |
| --- | --- |
| Security master | Vendor/security ID, issuer CIK, dated ticker aliases, share class, exchange, currency, trading time zone/calendar, effective dates |
| Daily prices | Session date, observed close, split-adjusted price basis/factor, source, currency/class, availability/retrieval time, freshness status; distinguish observed close from adjusted history |
| Corporate actions/returns | Effective/ex-dividend dates, splits, cash dividend currency/amount, adjustment base and provider methodology; separately identified dividend-inclusive return series |
| Financial observations | Metric ID, value/unit, financial period start/end, annual/quarterly/TTM frequency and duration/instant type, source accession/concept/document, public-availability evidence, vintage/restatement chain |
| Derived metrics | Formula/perimeter version, source operand IDs, classifications, valid period/availability, sign/denominator checks and missing/unsupported reason |
| Earnings events | Event/security ID, fiscal period, earnings release timestamp/time zone/precision, official source, before/during/after-session classification, mapped trading day, confidence/exclusion reason |
| Benchmarks | Explicit instrument/index ID, source/rights, session/currency, dividend and price adjustment conventions, return series and calendar alignment |
| Valuation snapshots | Issuer/class/currency, model ID/version/hash, valuation origin, information cutoff, public/analyst creation times, complete scenario assumptions and equity bridge, dated source inputs, FCFF/FCFE method outputs and freshness/readiness |

One issuer CIK can have multiple traded share classes. Market prices and model
denominators must identify compatible securities; GOOGL and GOOG are not an
interchangeable ticker label. Ticker changes retain identity history.

## Availability and revision rules

- Preserve reported and restated versions; do not replace original history.
- Descriptive latest-restated views must be explicitly labelled. As-known views
  select only observations available by the relevant cutoff, including the
  chosen vintage, not merely an old financial period carrying a later value.
- An earnings release can precede its SEC filing. Use evidence for the relevant
  fact/event; conservative filing-available views cannot claim earliest availability.
- Do not interpolate annual statements into invented monthly data. Quarterly/TTM
  preparation must reconcile periods, source rows and year-to-date/standalone
  observations before use. Missing quarters are not zeros.
- A daily price calendar does not change the financial data's reporting frequency.
- Record enough preceding history for return, TTM and estimation windows; show
  partial coverage explicitly rather than extrapolating missing observations.

## Adjustments and market comparisons

Keep observed close, split-adjusted price and dividend-inclusive performance
distinct. Document whether a provider's adjusted-close series already includes
dividends; never add them again. Use compatible adjustments for EPS, price,
historical per-share values and peak-price comparisons. Dates/class/currency and
denominator alignment are required before price/value comparisons.

Initial release uses end-of-day snapshots with explicit market session/source
dates, including the last available session on non-trading days. Provider/refresh
freshness thresholds are unresolved decisions, not silently invented defaults.

## Source rights and secrets

Record the provider, agreement/plan version and permission for public display,
historical storage, derived outputs, redistribution and user downloads. Public
static JSON is downloadable; a hidden UI is not access control. Free or delayed
API access is not evidence of permission to republish. Do not buy a plan or infer
rights from marketing text. Capture any provider attribution requirements.

Provider credentials remain in approved local preparation environments, never
frontend source, public packages or exported snapshots. Additive tools prepare
reviewed data beside the unchanged Python pipeline; static/browser operation
and manual laptop refresh remain the default architecture.

## Readiness and acceptance

Record shared package QA and per-issuer/per-feature readiness independently.
Planning states include NOT_ASSESSED, INCOMPLETE, QUALIFIED_READY and
SPECIALIZED_METHODOLOGY_REQUIRED; they do not alter existing frozen classifiers.
Missing fields, unsupported methods, stale data and date ambiguity need reason
codes plus reader-facing explanations. No plausible zero, invented cutoff or
success badge may replace an unresolved required input.

Acceptance checks cover source tie-outs, revision/availability selection,
splits/dividends, security aliases/classes, currency/period/unit checks, calendar
alignment, freshness/missing states, deterministic exports and artifact integrity.
No feature is ready solely because its shared data loader or chart renders.
