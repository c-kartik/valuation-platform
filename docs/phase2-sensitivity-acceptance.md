# Phase 2 — qualified three-company sensitivity acceptance

## Status and attribution

**Sensitivity software acceptance complete; economic acceptance qualified;
investment readiness not established.** This records the completed temporary
analyst review supplied in the preceding chat at
`a5719650723a4d5fcde4a0b3a3c42a0ad840e159`. It is an attributed historical
record, not independently authenticated evidence, new financial approvals or a
new execution log. **The prior company trials/checks below were not rerun during
this documentation/implementation checkpoint.**

The review reconstructed the latest provisional Bases from the
[META milestone](phase2-meta-milestone.md),
[GOOGL/AAPL milestones and ERP reconciliation](phase2-googl-aapl-milestones.md)
and [scenario record](phase2-scenario-acceptance.md). Exact disclosed dollar
amounts/derivation rules replaced rounded displayed ratios where available.
References reproduced documented precision, with no reported discrepancy.
Removed original JSON/metadata was not authenticated or replayed; new preparation
metadata identified Codex as reconstruction preparer. No current-market refresh,
new evidence, actual-company saved cases/grids/defaults or financial policy followed.

## Diagnostic grids and reconstructed references

All retained FY2025 revenue/source/approval bindings and original dates/cutoffs
were preserved. Timing remains fiscal-end analytical with later-filed information,
not a contemporaneous backtest or current-price comparison. All figures below are
**temporary assumption-led trial results**; displayed precision is not confidence.

| Issuer | Retained revenue / fiscal period | Analytical date / cutoff | Reference WACC / g | Explicit PV + terminal PV = EV, USD bn | Qualified USD/basic share |
| --- | --- | --- | --- | --- | --- |
| META | 200.966bn / 2025-01-01–2025-12-31 | 2025-12-31 / 2026-01-29 | 10% / 3% | 94.379 + 851.364 = 945.742 | 369.419042 |
| GOOGL | 402.836bn / 2025-01-01–2025-12-31 | 2025-12-31 / 2026-02-05 | 8.74% / 3%, ERP reconciled | 96.952 + 1290.982 = 1387.933 | 114.395258 |
| AAPL | 416.161bn / 2024-09-29–2025-09-27 | 2025-09-27 / 2025-10-31 | 8.59% / 2.5% | 475.743 + 1389.349 = 1865.092 | 124.918226 |

Each 5×5 grid used WACC offsets **−2/−1/0/+1/+2 percentage points** around its
reference. Absolute WACC rows: META 8/9/10/11/12%; GOOGL
6.74/7.74/8.74/9.74/10.74%; AAPL 6.59/7.59/8.59/9.59/10.59%.
META/GOOGL g columns: **1/2/3/3.5/4%**; AAPL: **1/1.5/2.5/3/3.5%**.
These were diagnostic choices probing combined discount-rate judgments and weaker
versus stronger perpetual nominal growth—not estimated confidence intervals,
probabilities, approved ranges or defaults. Different dated WACC builds remain
qualified despite the earlier ERP-variant reconciliation.

All review cells satisfied g<WACC. Separate invalid-pair/all-invalid probes tested
failure handling without distorting those economic grids. Annual operating paths,
terminal operating ratios, reserves, bridge/shares and conventions stayed fixed;
g recomputed terminal revenue/FCFF as well as the Gordon denominator.

| Diagnostic | META | GOOGL | AAPL |
| --- | --- | --- | --- |
| Reference terminal contribution | 90.02% | 93.01% | 74.49% |
| Terminal contribution across diagnostic grid | 84.96–94.08% | 88.63–96.53% | 63.76–85.79% |
| EV change, WACC +1pp at reference g | −15.19% | −17.70% | −14.05% |
| EV change, g +1pp at reference WACC | +16.02% | +20.72% | +15.50% |
| Narrowest WACC−g spread | 4.00pp | 2.74pp | 3.09pp |
| Fixed terminal net reinvestment / revenue | 6.15% | 6.00% | 2.40% |
| Fixed terminal reinvestment / NOPAT | 21.04% | 27.10% | 9.56% |
| Implied incremental returns, successive g columns | 4.75/9.51/14.26/16.63/19.01% | 3.69/7.38/11.07/12.92/14.76% | 10.46/15.69/26.16/31.39/36.62% |

The large upper cells relied on lower discounting/narrower spreads, without an
operating improvement. Fixed reinvestment ratios make higher g require higher
implied productivity; AAPL's upper-growth cells were particularly demanding.
At low g, META/GOOGL retained substantial reinvestment despite low implied returns.
These are physical-investment/WC diagnostics, **not verified historical ROIC**;
expensed intangible investment limits interpretation. Valid arithmetic does not
establish economic plausibility, probabilities or a fair-value range.

## Fixed bridge and unresolved financial scope

| Issuer | Signed bridge, USD bn / dated basic denominator | Fixed operating reserve |
| --- | --- | --- |
| META | +47.292 liquidity −57.220 Notes fair value −1.184 finance-lease carrying proxy / 2.530bn A/B issued common, assumed economic equivalence | 34.3bn |
| GOOGL | +56.4304085 liquidity −45.600 Notes −2.500 finance leases −3.400 NCI −10.054 opening tax / 12.088bn A/B/C, assumed economic equivalence apart from votes | 70.4125915bn |
| AAPL | +82.9828038 financial assets −80.400 Notes −7.979 CP −1.230 finance leases −13.016 opening tax / 14.773260bn fiscal-end common | 49.4371962bn |

GOOGL NCI includes redeemable NCI once. GOOGL/AAPL opening-tax settlements remained
outside recurring forecast tax/WC when deducted in the bridge. META's omitted
legacy legal/tax/unpaid acquisition settlements remained outside the limited
recurring-core reference, not reported zeros. Asset accessibility/realization,
strategic holdings, venture economics, awards and unidentified financing/claims
remain incomplete and potentially unbounded. Basic-share references are not fully
diluted fair values. No duplicate SBC, service-lease, financed depreciation or
capital-creditor charge was introduced.

META FY2026/FY2027 FCFF remained about **−25.433/−4.664bn**; GOOGL
**−30.482/−15.162bn**. Sensitivity does not finance those flows. Prior Bear funding
flags remain unresolved; financing terms/costs/dilution were not modeled. Diagnostic
endpoints and omitted positive assets do not bound total issuer value or make the
whole result conservative.

## Prior verification — attributed, not newly executed

The report states all three requests passed calculation-free validation and
explicit JSON/summary execution. GOOGL explicitly selected Base from a complete
reconstructed set; Bear/Bull were not newly valued. All **75 cells** matched
single-case execution (**375 component comparisons**).

It also reports **375 independent exact-rational comparisons**, covering reference
annuals/discount factors and five meaningful cells per company: reference, opposing
corners and isolated-axis changes. Tolerance was
`1e−32 + 1e−46 × |reference|`; maximum difference about **8.06e−38**.
Separate invalid pairs retained null results; all-invalid grids rejected. Nine
input/overwrite/protected-path checks passed. No correctness defect was found;
verbose JSON and USD-million summaries still required conversion/input review for
a compact USD-billion analyst view.

Temporary cases/results/reconstruction scripts were reported removed. All **589
tracked files** reportedly stayed byte-unchanged; six single templates stayed
37-unset and three scenario templates 111-unset. Git remained clean at `a571965`,
seven ahead of local `origin/main`, without commit/push or Phase 1 resumption.
The [checklist](phase2-completion-checklist.md) now separates this qualified
acceptance from reverse-DCF engineering, actual reverse analyst review and final
three-company acceptance. No actual-company sensitivity was rerun here.
