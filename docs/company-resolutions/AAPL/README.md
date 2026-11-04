# Apple — manually approved cash-flow treatments

## Current remaining-issue review — November4

The [four-stage implementation](remaining-issues-2026-11-04/report.html) executes the latest approved plan in order. Historical tax-inclusive NWC and existing forward-tax policy are now recorded under that approval; the date-matched common-share population is bound. Exact Other/lease financing, FY2024 D&A reconciliation and cash/claims/awards remain unresolved. FCFF and provisional FCFE are numerically unchanged. Current API/UI shows these decisions and preserves original review scope separately. **Apple remains OPEN; full financial review has not passed.**

## Current historical FCFF adoption — November 4

The [operating-method implementation](operating-fcff-2026-11-04/README.md) supersedes the earlier current-display statements below: FY2021–25 standardized FCFF is93.41/108.44/99.84/115.68/95.12B. All five use one source-bound EBIT/defined-current-NWC/cash-PP&E method. Current tax accruals/mixed Other remain inside NWC by disclosed convention;355M FY2024 D&A population mismatch is retained as a qualification. Both missing bars are populated and source/runtime review passes for that scope. This is not exact unlevered cash or full financial clearance. Legacy CFO gaps and all FCFE/open broader matters remain traceable; company status OPEN.

November 3, 2026. CIK 0000320193; selected FY2021–FY2025 annual filings. The user
approved the preferred treatments after the Apple-only review and requested a
traceable company folder. [Exact approval and bounded decisions](decisions.json).
The earlier [company preparation record](../../company-data-preparation/AAPL.md)
and original approvals remain authoritative for their original scopes.

**Applied outcome:** the five financing statements and the operating-method
calculations have been independently replayed from retained SEC sources. The
FY2021 equity-presentation conflict is resolved with no number change. Other
financing and operating-input alignment remain unresolved. No chart, forecast,
enterprise value or original historical fact has been overwritten.

## Issue → approved treatment → applied result

| Issue | Original problem | Approved treatment / rationale | Applied result |
| --- | --- | --- | --- |
| **AAPL-FCFE-001** | Other financing of −129/−160/−581/−361/−111m cannot be classified as debt or non-debt from its caption. Actual finance-lease principal cash is not separately disclosed. | Reconcile all financing rows; include identified term-debt/CP cash once; keep equity issuance, buybacks, common dividends and award withholding outside borrowing. Investigate Other/leases without a residual plug. | All five statements sum exactly to financing cash totals. Five identified-funding FCFE figures reproduce, but remain provisional. No additional lease principal or Other adjustment is invented. |
| **AAPL-FCFE-002** | The FY2023 comparative shows FY2021 Other of +976m rather than original −129m, because +1,105m common-stock proceeds were combined into the later caption. | Preserve the known stock proceeds as equity cash, not borrowing; reconcile original and later presentations. | −129m + 1,105m = 976m exactly; net borrowing and FCFE change **0**. The original −129m still needs classification. |
| **AAPL-FCFF-001** | Missing separate gross interest blocks the adopted CFO-based FCFF in FY2024–25. It does not prevent every EBIT-based calculation. | Reconcile a separate operating-income method over all five Apple years. Keep SBC expensed; do not fill missing interest from coupons, income, stocks or estimates. Preserve the old basis until the alternative inputs are justified. | Five source-bound calculations and exact EBIT-to-CFO bridges replay. Missing interest is no longer an input dependency of this alternative, but mixed cash movements, tax and investment/D&A scope still prevent verified operating FCFF. Diagnostic values are not adopted chart values. |
| **AAPL-TAX-001** | Accrued tax, cash tax and recurring operating tax are different. FY2024 includes the State Aid accounting charge and FY2025 has related timing effects. | Preserve reported historical tax and review recurring forecast taxes separately; do not remove an accounting charge from cash or infer an operating-tax allocation. | Reported provision/pretax remains an explicit diagnostic allocation; no normalized rate, cash-tax adjustment or forward-input change has been made. |

## Reproduced amounts

USD millions, rounded here for reading; exact fractions/operands are in the
[result ledger](results.json) and [comparison CSV](results.csv).

| FY | CFO less cash PP&E | Identified net borrowing | Provisional FCFE | Unallocated Other | Operating FCFF **diagnostic** | Current chart FCFF before → after |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2021 | 92,953 | 12,665 | 105,618 | −129 | 89,744.320 | 95,246.155 → unchanged |
| 2022 | 111,443 | −123 | 111,320 | −160 | 101,678.877 | 113,899.047 → unchanged |
| 2023 | 99,584 | −9,901 | 89,683 | −581 | 91,459.837 | 102,938.095 → unchanged |
| 2024 | 108,807 | −5,998 | 102,809 | −361 | 99,180.805 | Unavailable → unavailable |
| 2025 | 98,767 | −8,483 | 90,284 | −111 | 86,263.892 | Unavailable → unavailable |

The diagnostic is **not** certified operating FCFF. It applies reported provision /
pretax to EBIT, adds disclosed cash-statement D&A, subtracts cash PP&E and includes
signed broad asset/liability cash movements. It excludes the CFO SBC add-back.
The earlier chart definition retains CFO SBC adjustments and adds after-tax
interest. The diagnostic bridge explains differences rather than forcing equality.

Known tax evidence remains in the [adjustment schedules](../../company-data-preparation/historical-fcff-adjustment-schedules.json):
FY2024 State Aid charge 10,246m; FY2025 benefit −486m. FY2025 current provision
22,058m plus deferred −1,339m equals total provision 20,719m, while cash taxes are
43,369m. None of those differences is an inferred operating cash movement or
an approved recurring forecast rate.

## Sources and classification controls

[Source map](source-map.json) records every financing row's filing identity,
actual caption, table/row/column, concept, namespace, context, raw amount, cash
sign and primary inline fact ID. [Results](results.json) add independently
reverified primary/instance observations, hashes, exact arithmetic, before/after
chart values and remaining reviews. The mapping originated in the sealed
42-company audit, but reproduction needs only evidence already in this repository.

Original primary/instance receipt pairs are retained in
[analyst-operating-nwc-response-bodies.json](../../evidence/analyst-operating-nwc-response-bodies.json).
The existing source verifier checks URLs, original-byte hashes/lengths, exact
annual dates, CIK, USD units and displayed-inline/extracted-instance agreement.
No SEC retrieval, original package rebuild or old approval mutation occurs.

| FY | Fiscal dates | Filing |
| --- | --- | --- |
| 2021 | 2020-09-27–2021-09-25 | [0000320193-21-000105](https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm) |
| 2022 | 2021-09-26–2022-09-24 | [0000320193-22-000108](https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm) |
| 2023 | 2022-09-25–2023-09-30 | [0000320193-23-000106](https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm) |
| 2024 | 2023-10-01–2024-09-28 | [0000320193-24-000123](https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm) |
| 2025 | 2024-09-29–2025-09-27 | [0000320193-25-000079](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm) |

Finance-lease year-end liabilities of 848/941/1,024/896/1,230m are stocks, not
principal cash. Future maturities include interest. Combined operating/finance
ROU additions are noncash and do not isolate finance investment. Fixed operating
lease cash is not finance principal. None supplies the missing annual repayment.
Arithmetic closure of the cash statement does not resolve these classifications.

## Reproduce and update

From the repository root:

```sh
PYTHONPATH=src .venv/bin/python scripts/resolve_apple_cashflows.py --check
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/review -p 'test_apple_resolution.py' -v
```

`--check` recomputes all source bindings, five financing sums, five CFO checks,
five operating-to-cash bridges, and the later FY2021 presentation bridge, then
compares the result byte-for-byte with the committed ledger and CSV. It fails on
changed source amounts, cash signs, periods, captions, omitted cells or decisions.
It never changes the chart or makes a network request. `--write` regenerates
only this separate record after an intentional reviewed mapping/decision update.

For a future filing: retain its original bytes/receipt; create a new reviewed
mapping/decision version; preserve this original five-year record; compare old
and new amounts/bases; review changed economic classifications manually. Do not
extend this approval to a new period or revise a reported fact to fit a formula.

## Remaining manual review

- Identify actual Other/debt/finance-lease cash, or separately approve a clearly
  labeled, justified partial-scope/materiality policy. Small net Other is not a
  bound on potentially offsetting gross financing components.
- Establish the operating FCFF tax, mixed-movement, complete expense-aligned
  noncash and investment basis. In FY2025, including versus excluding mixed
  movement rows changes the diagnostic by 20,273m; neither variant is a bound
  on verified operating cash flow.
- Select any recurring operating-tax forecast separately. Approval to preserve
  historical taxes is not approval of a numerical normalized rate.

Treatment approval has been recorded and the approved reconciliations performed.
These remaining disclosure/measurement gaps prevent honest numerical clearance;
they are not resolved by changing a status label.

## Validation performed

[Validation record](validation.json): 47 relevant tests passed (eight new Apple
resolution tests and 39 existing FCFF/source tests). Independent read-only review
found no source, sign, scope or documentation defect. Source replay and exact
statement/control checks pass. No frontend build is claimed or needed for this
review-only milestone; runtime/API/UI code and source data are unchanged.

## Approved treatment implementation and independent review — November3

The latest user approval covers the preferred treatments in the roadblock register.
New evidence and executed treatment logs are in [this implementation](implementation-2026-11-03/README.md).
The [shared implementation log](../implementation-2026-11-03/implementation-log.json),
[basis bridge](../implementation-2026-11-03/basis-bridge/decision-log.json),
[share-source schedules](../implementation-2026-11-03/share-bridge/README.md) and
[independent review](../implementation-2026-11-03/independent-review/findings.md)
retain the distinction between applied treatment, numerical verification and financial clearance.
The platform now exposes five-year FCFF/FCFE review records and a separate explicit manual FCFE forecast;
prior statements above about review-only integration describe the earlier milestone.
**Company status remains OPEN.** No missing/provisional/ownership item is cleared by software publication.
