# Phase 2 — qualified three-company scenario acceptance

## Status and attribution

**Scenario software acceptance complete; economic acceptance qualified; investment
readiness not established.** This records the supplied temporary META, GOOGL and
AAPL Bear/Base/Bull review at `50cfc8cad8c606625ee73efc800c5efee5317726`.
It supplements the [META](phase2-meta-milestone.md),
[GOOGL/AAPL](phase2-googl-aapl-milestones.md) and
[scenario engineering](phase2-scenario-workflow.md) records. It selects no standing
Base case, scenario defaults, financial approval, rating or price target.
[Phase 1 expansion remains paused](phase1-universe-pause-checkpoint.md).

Source: user-supplied `Pasted text.txt` under
`/Users/kc/.codex/attachments/996a7b5d-b625-4774-bacb-eac2e972383e/`, SHA256
`cb4ff5f96c432d0c75ff58f7ab933ef47d146a686084d3dd1fa27cbad77e080c`.
All trial economics, results and prior verification below are **attributed report
contents**, not newly authenticated evidence, rerun calculations or approvals.
The present checkpoint performs separate synthetic engineering checks only.
Temporary files were reported removed; no actual-company executable cases,
outputs, forecasts or defaults were saved. These Markdown tables are historical
narrative records, with rounded values that may not sum exactly.

All three Base cases reportedly reconstructed earlier EV to USD 0.001bn and
basic-share references to USD 0.01. This is **reconstruction from disclosed inputs,
not an authenticated replay** of removed original JSON/full-precision outputs.
Bear/Bull forecasts are agent-selected estimates. META Base FY2026 revenue
255bn, expenses 165.5bn, EBIT 89.5bn and expense D&A 28.3bn retain the user's
provisional selections; other forecast/market/terminal and bridge policies are
analyst judgments/proxies, distinct from reported historical facts.

## Retained anchors and fixed comparison policies

Exact source/approval bindings remain in [anchor integration](phase2-anchor-integration.md#fixed-selections-and-provenance)
and the earlier company milestones; none changed here.

| Issuer | Reported FY2025 revenue, USD bn / fiscal period | Analytical date / information cutoff | Fixed WACC / terminal g |
| --- | --- | --- | --- |
| META | 200.966 / 2025-01-01–2025-12-31 | 2025-12-31 / 2026-01-29 | 10% / 3% |
| GOOGL | 402.836 / 2025-01-01–2025-12-31 | 2025-12-31 / 2026-02-05 | 8.74% / 3%, ERP-reconciled reference |
| AAPL | 416.161 / 2024-09-29–2025-09-27 | 2025-09-27 / 2025-10-31 | 8.59% / 2.5% |

Fiscal-end analytical timing uses later-filed information; this is neither a
contemporaneous backtest nor a current-price comparison. Common ERP-variant
reconciliation does not harmonize all market judgments; see
[P2-03](phase2-completion-checklist.md). Dates, conventions, bridge/share policies
and Base-derived operating reserves were held fixed across each company's cases.

## Temporary forecast assumptions

Vectors run FY2026→FY2030. Entries are **percentages**, except explicit **bn** dollar
estimates converted to full-revenue ratios with Decimal arithmetic. Terminal
tuples are margin / operating tax / expense D&A / investment / WC, all percentages.
Investment means cash PP&E plus non-overlapping new financed operating assets,
excluding finance principal; WC means cash requirement / full forecast revenue.

| META input | Bear | Base | Bull |
| --- | --- | --- | --- |
| Growth | 21.9112, 13, 10, 7, 5 | 26.8871, 18, 14, 10, 7 | 31.8631, 21, 17, 12, 8 |
| Margin | 31.0204, 30, 30.5, 31, 31 | 35.0980, 35, 36, 37, 38 | 38.1132, 37, 39, 40, 40 |
| Expense D&A | 30bn, 17, 19, 20, 20 | 28.3bn, 14, 16, 17, 17 | 29bn, 14, 16, 17, 17 |
| Investment | 137bn, 45, 38, 33, 28 | 127bn, 44, 36, 30, 25 | 132bn, 43, 35, 29, 24 |
| WC cash | 1, .9, .8, .6, .5 | .75, .6, .5, .4, .3 | .6, .5, .4, .3, .2 |
| Terminal tuple | 30 / 21 / 20 / 27 / .25 | 37 / 21 / 18 / 24 / .15 | 39 / 21 / 18 / 23 / .10 |

META operating taxes: 16/17/18/19/20% in every case. Exact FY2026
revenue/expenses/EBIT: Bear 245/169/76bn, Base 255/165.5/89.5bn,
Bull 265/164/101bn; rounded first-year growth/margin above are diagnostics.
Reported management outlook was expenses 162–169bn, spending 115–135bn including
principal and operating income above FY2025. Bear deliberately tests an
operating-income disappointment; Base/Bull monetize infrastructure more strongly.
FY2026 investment conversions were 135−1+3, 125−1+3, 130−1+3bn; principal/new
financed additions are forward estimates. License-expensing and venture/service
allowances remain inside margins. Commissioning/depreciation paths lack complete
asset-cohort calibration.

| GOOGL input | Bear | Base | Bull |
| --- | --- | --- | --- |
| Growth | 12, 10, 8, 6, 5 | 15, 13, 11, 9, 7 | 18, 16, 13, 11, 9 |
| Margin | 29, 25, 24, 24, 24 | 31, 28, 27, 27.5, 28 | 32, 31, 31.5, 32, 32.5 |
| Expense D&A | 40bn, 64bn, 90bn, 18, 18 | 38bn, 62bn, 85bn, 16, 16 | 38bn, 64bn, 90bn, 16, 16 |
| Investment | 188bn, 39, 35, 30, 26 | 183bn, 37, 32, 27, 23 | 188.5bn, 37, 31, 26, 22 |
| WC cash | .9, .9, .8, .7, .6 | .7, .7, .6, .5, .5 | .6, .6, .5, .4, .4 |
| Terminal tuple | 23.5 / 18 / 18 / 25 / .6 | 27 / 18 / 16 / 21.5 / .5 | 31 / 18 / 16 / 21.5 / .4 |

GOOGL operating tax: 18% throughout. The report cites strong advertising/Cloud
demand, 175–185bn CapEx and accelerating infrastructure depreciation, not annual
consolidated revenue/margin guidance. Bear assumes slow utilization despite
committed capacity; Bull higher utilization/profitability and larger dollar
spending. FY2026 investment: 185+3, 180+3, 185+3.5bn; estimated principal
.9/.8/.8bn stays excluded because those cash-PP&E definitions already exclude it.
Other Bets/Waymo costs are inside EBIT; internal funding is not deducted twice.
Unclosed acquisition consideration and incremental acquired cash flows are both
excluded from this operating scope.

| AAPL input | Bear | Base | Bull |
| --- | --- | --- | --- |
| Growth | 4, 3, 3, 2.5, 2.5 | 8, 6.5, 5.5, 4.5, 4 | 10, 8, 7, 6, 5 |
| Margin | 28.5, 28, 28.5, 29, 29 | 31, 31.5, 32, 32.25, 32.25 | 32, 33, 33.5, 34, 34 |
| Expense D&A | 13.5bn, 14.5bn, 3.4, 3.4, 3.3 | 13.5bn, 15bn, 3.2, 3.2, 3.1 | 14bn, 16bn, 3.3, 3.3, 3.2 |
| Investment | 17.5bn, 4.5, 4.7, 4.9, 5 | 18bn, 4.3, 4.5, 4.7, 4.8 | 20bn, 4.8, 5, 5.1, 5.2 |
| WC cash | .6, .6, .55, .5, .5 | .25, .3, .3, .35, .35 | .2, .25, .25, .3, .3 |
| Terminal tuple | 28.5 / 19 / 3.3 / 5 / .5 | 31 / 19 / 3 / 5 / .4 | 32.5 / 19 / 3.2 / 5.2 / .35 |

AAPL operating taxes: 17.5/18/18.5/19/19%. Reported Services/product facts motivate
narratives, not these annual forecasts. Bear retains development costs with weaker
products/tariffs/supplier timing; Bull stronger products/Services mix with more
investment/development expense. FY2026 gross-margin estimates 47/47.8/49% imply
functional OPEX 80.069/75.508/77.822bn. Investment: 17+.5, 17.5+.5, 19.4+.6bn;
estimated principal .6bn in each case stays excluded.

## Reported results and fixed limited bridges

Each triple is **Bear / Base / Bull**, USD billions except percentages/USD per share.
Every result remains a temporary assumption-led trial result, not a fair-value bound.

| Issuer | Explicit PV + terminal PV = EV | Qualified equity | Basic-equivalent USD/share | Terminal contribution |
| --- | --- | --- | --- | --- |
| META | 21.550+514.224=535.774 / 94.379+851.364=945.742 / 148.274+1065.950=1214.224 | 524.662 / 934.630 / 1203.112 | 207.38 / 369.42 / 475.54 | 95.98 / 90.02 / 87.79% |
| GOOGL | 6.165+821.689=827.854 / 96.952+1290.982=1387.933 / 192.290+1736.820=1929.110 | 822.730 / 1382.810 / 1923.986 | 68.06 / 114.40 / 159.16 | **99.26** / 93.01 / 90.03% |
| AAPL | 384.874+1123.075=1507.949 / 475.743+1389.349=1865.092 / 516.534+1573.522=2090.055 | 1488.307 / 1845.449 / 2070.413 | 100.74 / 124.92 / 140.15 | 74.48 / 74.49 / 75.29% |

Terminal FCFF triples: META 57.971/95.979/120.171bn;
GOOGL 71.708/112.662/151.570bn; AAPL 103.270/127.755/144.690bn.
Valuations ordered Bear<Base<Bull without engine enforcement or probabilities.

| Issuer | Fixed signed bridge, USD bn / denominator | Retained qualification |
| --- | --- | --- |
| META | +47.292 eligible liquidity −57.220 Notes fair value −1.184 lease carrying proxy / 2.530bn dated issued A/B common | A/B economic equivalence; 34.3bn Base-derived reserve fixed; legacy claims, unpaid acquisition, ventures and awards omitted, not zeros. |
| GOOGL | +56.4304085 eligible liquidity −45.600 Notes −2.500 lease proxy −3.400 NCI −10.054 opening tax / 12.088bn issued A/B/C | Economic equivalence apart from votes; 70.4125915bn fixed reserve; redeemable NCI counted once; strategic holdings, fines/escrow, awards and further venture/financing claims open. |
| AAPL | +82.9828038 eligible financial assets −80.400 Notes −7.979 commercial paper −1.230 lease proxy −13.016 opening tax / 14.773260bn fiscal-end issued common | 49.4371962bn fixed reserve; long-term securities realization risk; awards and other tax/legal, benefit, derivative and unidentified claims omitted. |

Eligibility/reserve, carrying/fair-value proxies and issued-share class equivalence
are trial policies, not approvals. GOOGL/AAPL opening tax settlements are excluded
from forecast tax/WC when deducted in the bridge. META's omitted legacy settlements
remain outside the limited recurring-core reference, with unbounded uncertainty.
SBC/operating leases stay expensed once; expense D&A, including financed assets, is
added back once. Capital-creditor cash PP&E is not also WC; CFO movements are not
deducted again. No buyback share reductions, automatic dilution or duplicate
future-service SBC charges were added. Basic-share results are not fully diluted.

**Funding flags:** reported cumulative Bear negative FCFF 56.684bn META and
77.052bn GOOGL exceeds their eligible-liquidity additions by about 9.392bn and
20.621bn. This flags potential financing needs, not a complete cash-runway estimate;
financing terms, costs and dilution were not modeled. GOOGL Bear's **99.26%**
terminal contribution makes its result especially dependent on terminal recovery.

Terminal physical-investment/WC diagnostics use net reinvestment = investment −
D&A + WC, and implied incremental return = g / (net reinvestment/NOPAT).

| Diagnostic, Bear / Base / Bull | META | GOOGL | AAPL |
| --- | --- | --- | --- |
| Net reinvestment / revenue | 7.25 / 6.15 / 5.10% | 7.60 / 6.00 / 5.90% | 2.20 / 2.40 / 2.35% |
| Reinvestment / NOPAT | 30.59 / 21.04 / 16.55% | 39.44 / 27.10 / 23.21% | 9.53 / 9.56 / 8.93% |
| Implied incremental return | 9.81 / 14.26 / 18.12% | 7.61 / 11.07 / 12.93% | 26.23 / 26.16 / 28.01% |

These are **not verified historical ROIC**. Expensed intangibles limit their meaning;
AAPL Bear's slightly higher diagnostic than Base follows lower net reinvestment,
with no forced ordering. Awards/claims remain incomplete and omissions potentially
unbounded. Scenario spreads and diagnostic alternatives do not bound total value.
Funding and terminal-driver review remain economic follow-ups.

## Prior verification and preservation-pin review — attributed, not rerun

The supplied report states three complete sets passed validation/JSON/summary,
all nine scenarios matched single-case execution, and **657 independent rational
comparisons** passed (`1e−32 + 1e−46 × |reference|`, max difference about 8.49e−38).
Three isolated Bear edits preserved Base/Bull, and input bytes, overwrite rejection
and protected paths passed. It reported no calculation/interface defect; verbose
JSON/comparison summaries still require complete input review. All **582 tracked
hashes** reportedly stayed unchanged, with temporary files removed, three 111-unset
scenario templates and six 37-unset single-case templates preserved.

The same prior review justified exactly one preservation pin correction: the old
`a10505f5` baseline predated `1d2e918`'s authorized assumption error-field metadata.
After removing only annotations and the exception metadata constructor, ASTs
reportedly matched; numerical conditions, limits and serialization were unchanged.
Six focused checks and isolated mutations of a WACC guard, retained META revenue
and frozen universe CSV reportedly rejected unauthorized changes. Protected
originals were never edited. **Those mutation probes and rational comparisons
were not rerun in this checkpoint**; no pin/hash/allowlist is weakened here.

The [completion checklist](phase2-completion-checklist.md) separates this qualified
acceptance from actual sensitivity review, broader market-input policy, reverse
DCF and final three-company analyst/regression acceptance. No complete historical
NWC reconstruction or all-company expansion is required for the scoped software
milestone; required missing operands and unbounded economic omissions stay explicit.
