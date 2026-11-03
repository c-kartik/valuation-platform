# Alphabet — manually approved cash-flow treatments

November 3, 2026. CIK0001652044; FY2021–FY2025. The user approved both preferred
treatments. [Approval](decisions.json), [source map](source-map.json),
[exact results](results.json), [CSV](results.csv), [validation](validation.json).

**Applied:** preserve consolidated FCFF; label FCFE **consolidated before NCI
attribution**; retain parent-common FCFE and NCI fair-value adjustment as missing.
Keep finance-lease cash within debt repayments once. No historical FCFF, forward
assumption or EV changes. This is not certification of parent-share fair value.

## Issue → approved treatment → applied result

| Issue | Original conflict | Approved treatment and alternatives rejected | Applied result / remaining limit |
| --- | --- | --- | --- |
| **GOOGL-NCI-001** | Consolidated cash flows include subsidiaries with outside ownership. Immaterial attributable net loss does not establish zero attributable cash. | Preserve consolidated FCFF; exclude NCI contributions from debt; label consolidated FCFE before attribution. Reject treating book NCI as fair value, using proceeds as an attribution adjustment, or assuming cash ownership is immaterial. | Five full financing schedules reconcile; FCFE is stored with scope. Parent-common FCFE and NCI fair value remain null. Contributions310/35/8/1,154/400m are outside borrowing. |
| **GOOGL-LEASE-001** | Lease financing cash is included in repayments of debt and can contain prepayments. Noncash financed-asset additions are a different population. | Count the debt/lease parent once; preserve cash/noncash/timing distinctions. Reject deducting the child payment again, adding noncash additions to cash-only capex, or subtracting a rounded prepayment figure to infer exact principal. | Verified lease financing cash586/705/405/1,988m for FY2022–25 is contained in repayments; no extra deduction. FY2021 remains covered by the combined debt/lease parent without an invented separate child amount. Operating investment timing is still a separate reconciliation. |

## Reproduced amounts

USD millions; FCFF rounded to three decimals here. Exact source operands,
classified full financing rows and derived amounts are in JSON/CSV.

| FY | CFO less cash PP&E | Identified net borrowing | Consolidated FCFE before NCI attribution | Consolidated historical FCFF | FCFF change |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2021 | 67,012 | −1,236 | 65,776 | 67,301.940 | 0 |
| 2022 | 60,010 | −1,196 | 58,814 | 60,310.163 | 0 |
| 2023 | 69,495 | −760 | 68,735 | 69,760.162 | 0 |
| 2024 | 72,764 | 888 | 73,652 | 72,987.942 | 0 |
| 2025 | 73,266 | 32,137 | 105,403 | 73,878.476 | 0 |

Consolidated FCFE = reported CFO − cash PP&E + identified net debt funding.
Parent-common FCFE is **not** this amount with NCI cash contributions simply
subtracted. The contribution is financing, not measurement of the minority
share of operating cash or its fair value.

## Source-backed ownership and lease distinctions

All five annual **Note5 VIE** paragraphs are retained as exact source-bound
excerpts. They say attributable net loss is not material; they do not provide the
cash-flow allocation needed here. NCI book balances4.3/3.8/3.4/4.2/3.4bn are not a
fair-value deduction. Redeemable NCI is already included; do not add it again.
An NCI fair-value bridge is needed before claiming parent-common equity value
from consolidated EV; no new equity-bridge valuation is implemented here.

FY2025 **Note4**, table123 row6, reports **1,988m financing cash flows used for
finance leases**. The footnote says this cash is included in **Repayments of debt**
and includes **$1.1bn prepayments for leases not yet commenced**. The amount is not
labeled as purely ordinary commenced-lease principal. Rounded1.1bn cannot justify
an exact888m residual principal. **1,606m finance-lease assets obtained** is noncash
investment and not another cash payment. The source map binds Note4's cash cells
and footnote; the result ledger preserves the debt-parent containment checks.

FY2022/23 cash586m/705m is sourced from FY2024 Note4 comparative columns; FY2024
cash405m is the current-year column. Source versus target filing identities remain
explicit. FY2021 has no selected separate lease cash binding in this review;
its parent concept explicitly includes debt and capital-lease obligations.

## Remaining limits and future updates

- Parent-common cash attribution and a justified NCI fair-value equity bridge
  remain unresolved. No book-value plug or arbitrary zero is adopted.
- CFO-based historical FCFF retains SBC and uses provision/pretax as its stated
  tax allocation. The forecast's EBIT/SBC/noncash/investment conventions differ;
  no FCFF CAGR joins history to forecast. Prior operating-method calculations
  remain diagnostic, not replacement chart values.
- Lease prepayments/noncash additions need a separate aligned operating-investment
  reconciliation before changing that convention. Approval to avoid double-counting
  cash is not approval to guess timing or asset splits.

```sh
PYTHONPATH=src .venv/bin/python scripts/resolve_meta_alphabet_cashflows.py --check
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/review -p 'test_meta_alphabet_resolution.py' -v
```

The offline replay verifies retained SEC primary/instance hashes, exact annual
periods, USD units, context and source cell IDs, captions and cash signs; five
financing totals; five VIE narratives; and four lease financing cash/parent
containments. It needs no network or old chat-output folder. `--write` regenerates
only separate review ledgers for Alphabet; no runtime FCFE model is silently added.

For new filings, retain source bytes and review changed ownership/lease facts,
map exact source and target periods, compare old/new calculations and record new
manual decisions without overwriting this approval or original accepted facts.
[Existing preparation record](../../company-data-preparation/GOOGL.md).

## Approved treatment implementation and independent review — November3

The latest approval covers the preferred treatments in the register. New [issuer workpapers](implementation-2026-11-03/README.md) and the [shared execution log](../implementation-2026-11-03/implementation-log.json) retain errors, treatments, sources and remaining limitations. Five-year review data and a separate manual FCFE forecast now reach the platform; earlier statements about review-only integration describe the earlier milestone. **Company status stays OPEN** pending full financial clearance.
