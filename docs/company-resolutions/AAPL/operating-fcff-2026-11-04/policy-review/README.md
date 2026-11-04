# Apple standardized operating FCFF policy review — 4 November 2026

Scope: independent policy review of the user's approved EBIT-based five-year
replacement. This workpaper does not modify sources, production, past decisions,
or adopt any amount by itself. `replay.py` independently reads retained annual
instances, checks nondimensional USD point-in-time observations, and calculates
policy comparisons with exact fractions. `results.json` contains source hashes,
URLs, contexts, instance ordinals and both beginning/ending snapshots.

## Decisive recommendation

Use one explicitly named **standardized balance-sheet operating FCFF** across
FY2021–25, rather than splice two years into the old CFO convention:

`EBIT × (1 − reported provision / reported pretax income) + reported cash-statement D&A − cash PP&E purchases − Δ standardized current working capital`.

For the broad current-working-capital version, include customer/vendor
receivables, inventory, all reported Other current assets, trade payables,
current deferred revenue and all reported Other current liabilities; remove
current finance and operating lease liabilities from the latter. Cash,
marketable securities, commercial paper and current term debt are excluded.
This is equivalent to noncash current assets less nondebt current liabilities
with the stated lease exclusion.

**Current tax policy must be explicit:** retain current income-tax balances
inside this aggregate for every year. The result therefore includes a current
tax-accrual timing adjustment to provision-allocated NOPAT. It does not claim
to measure exact operating cash tax or a completely tax-excluded WC population.
This is an implementation refinement to the prior plan's separate-tax preference;
it must be disclosed in the adopted policy, not silently introduced.

The alternative of excluding taxes only where disclosed creates inconsistent
five-year scope. Exact current taxes are first reported in the retained FY2023
filing, with a FY2022 comparative: 6.552B (2022), 8.819B (2023), 26.601B (2024),
13.016B (2025). No exact FY2020/21 current-tax split was found in selected annual
instances or the retained latest SEC Company Facts. Missing is not zero.

Damodaran's published general convention removes cash/investments and interest
bearing current debt, retains composite Other noncash assets and nondebt
liabilities, and expressly discusses the tradeoff between detailed and composite
WC modeling. It supports this **aggregate convention**, not certification that
every component of Apple's Other captions is individually operating.
[Working capital in valuation](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/noncashwc.htm).

CFA recognizes EBIT-based FCFF, requires interpretation of financial statements
and notes that required detail may not be transparent. Neither CFA nor this
workpaper declares the Apple aggregate a directly reported or assumption-free
cash-flow number.
[CFA Free Cash Flow Valuation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation).

## Independent numerical reproduction

USD billions, with both current lease liabilities excluded:

| Fiscal year | Opening standardized WC | Closing standardized WC | Change | Standardized FCFF |
|---|---:|---:|---:|---:|
| 2021 | −37.393 | −36.143 | 1.250 | 93.40531983 |
| 2022 | −36.143 | −44.108 | −7.965 | 108.44387710 |
| 2023 | −44.108 | −45.915 | −1.807 | 99.84383667 |
| 2024 | −45.915 | −66.065 | −20.150 | 115.67980529 |
| 2025 | −66.065 | −49.925 | 16.140 | 95.12389189 |

The FY2024 current-tax accrual increases this measure by 17.782B; the FY2025
reversal reduces it by 13.585B. These effects must be visible so the user does
not interpret the difference as purely customer/supplier cash conversion.
The tax-excluded **diagnostic** (not a complete five-year alternative) would be
97.57683667B/97.89780529B/108.70889189B for FY2023/24/25 respectively.

## D&A decision

Use the exact reported combined cash-statement D&A as the chosen standardized
aggregate for all five years: 11.284B, 11.104B, 11.519B, 11.445B, 11.698B.
Do not add later note figures to this amount and do not manufacture a plug.

The FY2026 note separately reports FY2024 PP&E depreciation of 8.2B and
intangible amortization of 3.6B. Their 11.8B rounded sum exceeds the FY2024
combined cash-statement amount by 355M; this exceeds ordinary combined rounding.
The later note includes both owned and licensed intangible amortization.
No retained explanation identifies the exact 355M economic/timing allocation.
Accordingly, preserving the combined reported aggregate is a documented
standardization choice; it does not establish an exact expense-population tie.
The FY2025 rounded note sum of 11.7B is compatible at rounding precision with
the 11.698B cash-statement amount; compatibility alone is not a proof of scope.

Source: [FY2026 Note 5–6](https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm),
hash `671be78e626940c4fd9627e14701489e46dcbca19ec7c5f106b7ab215edd3ec1`.

## Investment and lease decision

Use reported cash PP&E purchases as the consistently defined fixed-investment
input. Do not deduct lease principal in an EBIT-based model as an additional
operating investment cash flow. Do not insert noncash finance-lease additions
into the cash PP&E line without a corresponding model change. The resulting
series is a cash-PP&E standardized model, not comprehensive economic investment
including every internally developed/acquired/licensed asset or financed asset.

Both current lease liabilities are excluded from WC because they are fixed
asset/service lease balances rather than customer/supplier working capital.
This avoids counting their change as an unrelated current operating cash source.
Finance-lease current balances are exact: 24M (2020), 79M (2021), 129M (2022),
165M (2023), 144M (2024), 538M (2025). Source facts for operating-lease balances
are retained in `results.json` too.

## What the publication status may and may not say

The adopted standardized series may be **available under a disclosed model
convention**, with verifiable filing operands and exact arithmetic. Gross
interest nondisclosure and FCFE Other-financing questions do not block that
particular consumer. Preserve the old CFO-based calculations and their gaps.

It must not be described as directly reported, exact historical cash FCFF,
an audited Apple measure, a completely classified pure operating-WC schedule,
or automatic clearance of forecasts/FCFE/per-share readiness. Derivative and
restricted-cash balances may be embedded in Other current assets/liabilities;
the selected annuals do not provide every current/noncurrent split needed to
remove them individually. The aggregate convention is therefore an analyst
classification, not a missing fact filled with zero.

The narrower core-trade-only variant is reproduced solely as a sensitivity.
It excludes both Other buckets completely and produces 91.51B, 102.34B,
95.24B, 95.85B, 107.82B. It is not recommended as an unqualified full FCFF
replacement because it intentionally omits operating accruals/prepayments.

Reproduce: `.venv/bin/python docs/company-resolutions/AAPL/operating-fcff-2026-11-04/policy-review/replay.py`.
