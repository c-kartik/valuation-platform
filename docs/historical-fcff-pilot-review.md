# Historical FCFF pilot — Alphabet, Apple and Meta

November 2, 2026. Scope: the existing FY2021–FY2025 accepted histories only.
The wider universe review stays paused. This review reuses extraction and
normalization; no historical package, fact, approval or forecast changes.

## Result

All fifteen selected annuals have source-bound reported CFO and cash PP&E;
their independently displayed CFO arithmetic rechecks exactly. The tables
show **CFO less cash PP&E**, a derived cash FCF measure, **not FCFF**.
No economic adjustment is inferred from a missing value. Historical chart
publication remains disabled pending the named reconciliation below.

The machine companion retains package/audit hashes, exact annual identities,
source pointers, occurrence precision/context and SEC source URLs:
[fifteen-period reconciliation](company-data-preparation/historical-fcff-pilot-review.json).

## Estimates prepared for review

The user authorized clearly labelled estimates for review. These **estimated
FCFF** figures are neither reported facts nor accepted historical chart values.
They retain cash taxes/timing in CFO and use annual reported ETR only as a
proxy for the tax effect of the estimated financing/nonoperating adjustment.
This is not a fully reconciled operating cash-tax calculation.

| Company | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| GOOGL | 51.41B | 38.39B | 44.54B | 45.69B | 42.41B |
| AAPL | 84.56B | 102.45B | 89.05B | 96.82B | 85.94B |
| META | 29.35B | 6.56B | 28.67B | 36.07B | 24.00B |

Amounts above are USD billions, rounded only for display. Full arithmetic,
operands and assumptions remain in the machine companion.

The review estimate is:

`CFO − cash PP&E − CFO SBC add-back − estimated financed investment − net nonoperating cash proxy × (1 − reported ETR)`

The net nonoperating cash proxy is `Pretax − EBIT + identified pure nonoperating
CFO reconciliation contributions`. The signed contributions prevent a second
removal of securities gains already reversed in CFO. Net nonoperating income
already includes interest expense: do not also add overlapping borrowing/lease
interest. Mixed Other, tax allocation and accrual/cash differences remain
unquantified uncertainty, not assumed reported zero.

Two explicit investment estimates need particular review:

- **Alphabet FY2021:** backcast finance additions using the median additions/
  cash PP&E ratio from FY2022–25. Later information is deliberately used;
  this is not a contemporaneous historical backtest.
- **Apple FY2021–25:** allocate combined lease additions using the closing net
  finance ROU asset share of total net ROU assets. Stock mix can differ from
  new-investment mix, so this is an allocation estimate, not a filing split.

Alphabet FY2022/23 instead use 577m/564m later-reported comparative additions
from the retained FY2024 instance (Note 4). Original FY2022/23 source packages
are unchanged. FY2024/25 Alphabet and all five META additions use existing
named source observations with an explicit non-overlap assumption.

## Proposed common calculation

Start with independently reconciled CFO, subtract cash PP&E, then separately:

1. Remove the CFO SBC add-back to retain compensation expense, consistently
   with the existing forecast. Review expense/add-back scope differences;
   do not also subtract the full SBC expense proxy a second time.
2. Reverse financing interest actually included in CFO. Resolve overlaps
   between borrowing and lease interest, and capitalized-interest treatment.
3. Remove excluded nonoperating cash still in CFO. Accrual gains already
   reversed in the cash-flow reconciliation are not another deduction.
4. Reconcile reported taxes to unlevered operating taxes. Do not automatically
   use reported ETR as a cash operating rate or apply a second tax shield.
5. Deduct non-overlapping new financed operating investment, consistent with
   the forecast's finance-asset convention. Review capital-creditor, cash
   PP&E and acquisition boundaries so purchases/settlements count once.

This is a **proposal**, not an activated historical formula. It does not
alter the existing manual forecast contract. A cash-flow route avoids needing
complete expense D&A or reconstructed book NWC; those are not new gates.
D&A and working-capital movements already in CFO are not added/deducted again.

The standard CFO route includes after-tax financing adjustments
([CFA Institute](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation));
the additional SBC/perimeter treatment here follows this platform's existing
forecast convention rather than claiming every published FCF measure is equivalent.

## Source-supported schedules

Amounts are USD millions at retained filing precision. Cash PP&E is shown as
an outflow magnitude. Original-as-selected periods and restatement boundaries
remain; this is not a recast common-calendar series.

### GOOGL

| FY | Reported CFO | Cash PP&E | CFO less cash PP&E | CFO SBC add-back |
|---|---:|---:|---:|---:|
| FY2021 | 91,652 | 24,640 | 67,012 | 15,376 |
| FY2022 | 91,495 | 31,485 | 60,010 | 19,362 |
| FY2023 | 101,746 | 32,251 | 69,495 | 22,460 |
| FY2024 | 125,299 | 52,535 | 72,764 | 22,785 |
| FY2025 | 164,713 | 91,447 | 73,266 | 24,953 |

Supporting disclosures below are **candidates, not additive adjustments**.

| FY | Cash-interest candidate | Finance-interest candidate | Finance-additions candidate (including later comparative) | Combined lease-additions support |
|---|---:|---:|---:|---:|
| FY2021 | Not separately selected | Not separately selected | Not separately selected | Not separately selected |
| FY2022 | Not separately selected | Not separately selected | 577 | Not separately selected |
| FY2023 | Not separately selected | Not separately selected | 564 | Not separately selected |
| FY2024 | Not separately selected | 31 | 313 | Not separately selected |
| FY2025 | Not separately selected | 65 | 1,606 | Not separately selected |

Borrowing cash interest is not separately selected in any of the five retained annual packages. FY2024/25 interest expense is accrual support, not a cash payment. Original finance-additions selections exist only in FY2024/25; the review adds separately identified later FY2024 comparatives for FY2022/23, retaining source/fact dates and receipt hash. Combined early debt/lease repayments do not supply interest or additions. The rounded SBC expense and CFO add-back differ; do not call the difference rounding or charge both.

Selected primary filings:

- [FY2021 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204422000019/goog-20211231.htm) — 2021-01-01 to 2021-12-31.
- [FY2022 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204423000016/goog-20221231.htm) — 2022-01-01 to 2022-12-31.
- [FY2023 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000022/goog-20231231.htm) — 2023-01-01 to 2023-12-31.
- [FY2024 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm) — 2024-01-01 to 2024-12-31.
- [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm) — 2025-01-01 to 2025-12-31.

### AAPL

| FY | Reported CFO | Cash PP&E | CFO less cash PP&E | CFO SBC add-back |
|---|---:|---:|---:|---:|
| FY2021 | 104,038 | 11,085 | 92,953 | 7,906 |
| FY2022 | 122,151 | 10,708 | 111,443 | 9,038 |
| FY2023 | 110,543 | 10,959 | 99,584 | 10,833 |
| FY2024 | 118,254 | 9,447 | 108,807 | 11,688 |
| FY2025 | 111,482 | 12,715 | 98,767 | 12,863 |

Supporting disclosures below are **candidates, not additive adjustments**.

| FY | Cash-interest candidate | Finance-interest candidate | Finance-additions candidate (including later comparative) | Combined lease-additions support |
|---|---:|---:|---:|---:|
| FY2021 | 2,687 | Not separately selected | Not separately selected | 3,300 |
| FY2022 | 2,865 | Not separately selected | Not separately selected | 2,800 |
| FY2023 | 3,803 | Not separately selected | Not separately selected | 2,100 |
| FY2024 | Not separately selected | Not separately selected | Not separately selected | 1,000 |
| FY2025 | Not separately selected | Not separately selected | Not separately selected | 2,800 |

Cash-interest candidates exist for FY2021–23; FY2024/25 are not separately selected. The note combines operating and finance lease additions in all five years: neither the whole combined value nor a liability-stock change is a finance-only addition. InterestPaidNet is a named reported population, not an automatically approved borrowing/lease split.

Selected primary filings:

- [FY2021 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm) — 2020-09-27 to 2021-09-25.
- [FY2022 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm) — 2021-09-26 to 2022-09-24.
- [FY2023 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm) — 2022-09-25 to 2023-09-30.
- [FY2024 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm) — 2023-10-01 to 2024-09-28.
- [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm) — 2024-09-29 to 2025-09-27.

### META

| FY | Reported CFO | Cash PP&E | CFO less cash PP&E | CFO SBC add-back |
|---|---:|---:|---:|---:|
| FY2021 | 57,683 | 18,567 | 39,116 | 9,164 |
| FY2022 | 50,475 | 31,431 | 19,044 | 11,992 |
| FY2023 | 71,113 | 27,266 | 43,847 | 14,027 |
| FY2024 | 91,328 | 37,256 | 54,072 | 16,690 |
| FY2025 | 115,800 | 69,691 | 46,109 | 20,427 |

Supporting disclosures below are **candidates, not additive adjustments**.

| FY | Cash-interest candidate | Finance-interest candidate | Finance-additions candidate (including later comparative) | Combined lease-additions support |
|---|---:|---:|---:|---:|
| FY2021 | Not separately selected | 15 | 160 | Not separately selected |
| FY2022 | Not separately selected | 16 | 223 | Not separately selected |
| FY2023 | 448 | 20 | 588 | Not separately selected |
| FY2024 | 486 | 23 | 181 | Not separately selected |
| FY2025 | 696 | 31 | 613 | Not separately selected |

Finance interest and noncash finance additions are selected for all five years; borrowing/cash-interest candidates exist for FY2023–25. Interest populations may overlap and must not be summed automatically. FY2022–24 original shared-parser PARTIAL statuses remain; their separate accepted caption-specific display proofs recheck exactly. Original FY2021 cash PP&E18,567 remains selected, not later18,690.

Selected primary filings:

- [FY2021 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680122000018/fb-20211231.htm) — 2021-01-01 to 2021-12-31.
- [FY2022 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680123000013/meta-20221231.htm) — 2022-01-01 to 2022-12-31.
- [FY2023 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680124000012/meta-20231231.htm) — 2023-01-01 to 2023-12-31.
- [FY2024 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680125000017/meta-20241231.htm) — 2024-01-01 to 2024-12-31.
- [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm) — 2025-01-01 to 2025-12-31.

## Remaining decision and delivery boundary

For each issuer/year, the machine review retains six unresolved signed
adjustment roles: financing cash, nonoperating cash, operating taxes, SBC
alignment, financed investment and investment perimeter. An observed support
amount does not by itself resolve its economic allocation or overlap.

The user explicitly chose **Allow clearly labeled estimates for review**.
The concrete estimates above implement that review scope. Their specific tax,
mixed-row, lease-allocation/backcast and investment-omission assumptions still
need review before chart use. Original unresolved requirements and null actual
FCFF remain; estimates do not silently resolve the source gaps or activate
a new historical financial convention.

Once resolved, connect the versioned calculation and its provenance to the
existing historical chart window. Keep cash FCF separately named and never
feed this intermediate into forecasts, DCF, cash-conversion calibration or EV.

## Reproduce and verify

Run `PYTHONPATH=src .venv/bin/python scripts/prepare_historical_fcff_review.py --check`.
Tests cover all fifteen independent CFO sums/cash FCF values, source identities,
unaltered packages, effective-value tampering, stale approvals, signs/units,
rounded-note precision, missing support and Decimal-context independence.
The 27-test review/history suite includes 12 new pilot financial/provenance
tests, independent Fraction checks, later-comparative receipt tampering and
separation of estimates from publishable FCFF. No runtime/UI change is included.
