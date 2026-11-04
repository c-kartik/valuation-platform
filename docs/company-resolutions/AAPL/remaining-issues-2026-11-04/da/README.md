# Apple remaining issues — stage 2: D&A population

Date: 2026-11-04. Target scope: FY2021–25. Stage 1 financing precedes this stage; tax/working-capital and valuation-bridge work follow separately.

**Implemented treatment:** retain the reported combined cash-statement D&A for all five standardized historical FCFF calculations. No added depreciation, amortization, lease principal or $355M balancing plug. **Exact expense-population reconciliation remains OPEN.** A policy treatment is implemented; no evidence-based reconciliation has been invented.

## Sequential work performed

1. Rebound all five original cash-statement D&A amounts and cash PP&E amounts to primary inline facts and extracted XBRL instances. Confirmed these are exactly the operands in the adopted standardized history.
2. Read the retained FY2026 primary annual report and instance with their original URL/body hashes. Bound depreciation, intangible amortization and combined D&A to the exact FY2024, FY2025 and FY2026 fiscal contexts. FY2024 is 2023-10-01–2024-09-28; all three competing observations cover those same dates. This is not a fiscal-year selection error. Original FY2024/25 cash-statement D&A equals the later comparative amounts.
3. Calculated conservative rounding envelopes using XBRL `decimals`: depreciation and intangible amortization are each rounded to $100M, while combined cash-statement D&A is rounded to $1M. Ordinary rounding cannot explain FY2024.
4. Mapped the disclosed asset populations and cash/investment implications below. The notes provide population clues but no numerical bridge assigning the FY2024 discrepancy to a particular category.
5. Tested the nominal difference as a diagnostic only. Holding all other inputs constant, an unsupported additional $355M would change FY2024 FCFF from $115.679805288B to $116.034805288B. This is not adopted, not a forecast, and not evidence that $355M is an appropriate add-back. No DCF or perpetuity adjustment was made.
6. Added replay and source/year/precision/no-double-count tests. Nothing in the runtime, accepted source bank, forecasts or prior stage was edited.

## Comparison and rounding

| Fiscal year | PP&E depreciation | Intangible amortization | Combined cash-statement D&A | Nominal difference | Conservative difference envelope |
|---|---:|---:|---:|---:|---:|
| 2024 | $8.2B | $3.6B | $11.445B | $355M | $254.5M–$455.5M |
| 2025 | $8.0B | $3.7B | $11.698B | $2M | −$98.5M–$102.5M |
| 2026 — supplemental only | $8.7B | $4.9B | $13.423B | $177M | $76.5M–$277.5M |

The envelopes are conservative closed bounds around displayed precision, not confidence intervals or estimates. FY2025 can be explained by rounding; FY2024 and supplemental FY2026 cannot. The latter is not added to the platform's five-year target scope.

## Asset, expense and cash population map

| Population | Supported filing evidence | Implemented treatment / unresolved point |
|---|---|---|
| PP&E | Note 1 states cost basis and straight-line depreciation. Note 5 discloses PP&E depreciation. Cash statements disclose cash PP&E purchases separately. | Retain cash PP&E once and combined reported D&A once. Note depreciation is not separately added on top of combined D&A. Notes do not provide a complete cost-of-sales/operating-expense allocation or bridge to the cash-statement D&A population. |
| Finance-lease assets | Note 10 places finance-lease ROU assets in PP&E, net. This proves balance-sheet location, not a quantified D&A overlap. | Do not add a separate lease-depreciation amount, infer actual principal from stock changes, or count noncash asset additions as cash capex. Separate financing/principal disclosure dependency remains in stage 1. |
| Owned amortizable intangibles | Note 6 separates owned from licensed asset balances and gives one aggregate intangible-amortization expense. | Aggregate expense split and associated acquisition/cash investment are not separately reconciled here. No incremental intangible amortization add-back or guessed investment deduction. |
| Licensed amortizable intangibles | Note 6 reports licensed balances including a current portion. Note 12 identifies licensed IP/content and distribution rights among purchase obligations. | These observations establish asset/obligation categories, not the timing or cash-statement classification of actual payments or their portion of amortization. They do not prove the $355M explanation. Current-asset amortization and associated payment movements must be traced before any extra add-back; otherwise D&A and NWC could overlap. |
| Non-amortizable owned intangibles | Note 6 separately labels non-amortizable owned assets. | Do not treat their balances as amortization expense or forecast them mechanically as recurring capex. |
| Operating leases | Note 10 separately reports operating-lease expense/cash and noncash ROU additions. | No separate operating-lease ROU amortization added to D&A, no noncash ROU addition treated as cash PP&E. This preserves existing convention without certifying a full expense-to-investment reconstruction. |

Reported consolidated EBIT is the starting profit measure. The supplied disclosures do not locate every D&A category within EBIT versus capitalized inventory/other asset costs. Capitalization, cash-reconciliation reclassification and differing intangible-payment populations are **hypotheses requiring evidence**, not accepted numerical explanations. Neither all intangible amortization nor finance-lease asset depreciation is assumed automatically incremental to the reported combined line.

## Sources and reproducibility

- Original five annual primary/instance receipts: linked for each operand in [results.json](results.json).
- Later comparative: [Apple FY2026 10-K, notes 1, 5, 6, 10 and 12](https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm). Received 2026-11-03; body hash and exact fact IDs/contexts/precision are in results. This later information is expressly marked and does not imply availability at FY2025 year-end.
- Retained later source bodies and immutable receipts remain in `implementation-2026-11-03/`; no source edits or network reconstruction.
- Run from repository root: `.venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/da/replay.py`.
- Tests: `.venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/da/test_replay.py -v`.

## Closure condition and next action

To close **exact expense alignment**, obtain a source-supported numerical reconciliation of the cash-statement and note expense populations, including the corresponding cash/investment/current-asset treatment, and independently review it. If not publicly disclosed, a precise issuer question should request that bridge; no issuer message was sent. Accepting the user-approved reported-combined convention permits the existing standardized historical calculation but does not answer the undisclosed population difference. Apple remains OPEN while this or other required roadblocks persist.
