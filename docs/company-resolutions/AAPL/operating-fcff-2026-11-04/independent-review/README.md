# Independent Apple standardized-FCFF audit

**Verdict: PASS for five-year availability under the disclosed standardized definition. Apple's overall financial review remains OPEN.**

No calculation or runtime blocker was found for this particular historical consumer. The conclusion does not certify exact unlevered cash flow, an expense-population tie, complete FCFE, forecast calibration, or parent equity/per-share readiness.

## Source-to-runtime verification

The independent script uses exact `Fraction` arithmetic and does not call production calculation helpers to create its oracle. It then checks the production reader, chart history and catalog against that oracle.

- Verified **105 input points**: 25 annual operands and 80 beginning/ending balance observations, against both retained primary inline facts and extracted XBRL instances. Values, scale, sign, USD unit, CIK, exact period/instant and absence of segment dimensions agree.
- Recomputed all five values independently. The 80 balance observations collapse to eight consistent balance populations across **six dates**; every prior close equals the next opening balance.
- Verified ten original retained-body hashes and the source package pin. No source facts were changed.
- Rechecked four supplemental current-tax diagnostics. FY2022's 6.552B is correctly a comparative in the FY2023 filing; it is not an original FY2022 disclosure. No absent FY2020/FY2021 tax split becomes zero or enters a selective subtraction.
- The actual historical reader, adopted history window, chart catalog and live API expose the same five amounts. All five use the same basis; no two-year splice exists.
- The previous CFO-based FCFF records remain available separately, including both FY2024/FY2025 nulls. Apple FCFE is unchanged and provisional. Meta and Alphabet company records are unchanged.
- No interest operand, financing principal deduction, SBC add-back, fair-value NCI assumption or balancing plug is introduced. Both current finance-lease and operating-lease liabilities are excluded from current working capital in every year.
- Runtime policy forbids automatic forecast calibration and cross-basis FCFF CAGR. Historical scope is not relabeled as exact cash or as a fully cleared company review.
- The five focused Apple source/runtime tests passed independently. A separate live API receipt is retained in `live-api-results.json`.
- Started the actual sealed API in a **fresh interpreter** with imports restricted to the final private bundle. Its startup/health, five Apple history values and chart catalog passed; all material tax and D&A qualifications appeared in the notice. The catalog is 83,442 bytes, within the fixed 96 KiB ceiling. The bundled calculation dependency imported successfully. `sealed-runtime-results.json` records the six reviewed module hashes; this check did not borrow already imported repository modules.

## Recomputed values

USD billions, rounded here; exact fraction and decimal serialization are retained in `results.json`.

| Fiscal year | Opening standardized NWC | Closing standardized NWC | Change in NWC | Standardized FCFF |
|---|---:|---:|---:|---:|
| 2021 | -37.393 | -36.143 | 1.250 | 93.40531983 |
| 2022 | -36.143 | -44.108 | -7.965 | 108.44387710 |
| 2023 | -44.108 | -45.915 | -1.807 | 99.84383667 |
| 2024 | -45.915 | -66.065 | -20.150 | 115.67980529 |
| 2025 | -66.065 | -49.925 | 16.140 | 95.12389189 |

Formula checked:

`EBIT × (1 − reported tax provision / reported pretax income) + reported combined D&A − cash PP&E purchases − change in standardized current NWC`.

Current NWC is total current assets minus cash and current marketable securities, less total current liabilities after removing commercial paper, current term debt and both current lease liabilities.

## Financial interpretation and required qualifications

This is a defensible, reproducible **standardized balance-sheet model** when all of the following limits are explicit. It is not a claim that each remaining balance is an individually verified operating cash item.

1. **Current taxes remain included uniformly.** The model contains tax-accrual timing adjustments to provision-allocated NOPAT. FY2024's current-tax increase contributes +17.782B relative to a tax-excluded diagnostic; FY2025's reversal contributes -13.585B. These changes must not be described as entirely customer/supplier working-capital performance. Noncurrent tax/cash timing is not fully reconstructed.
2. **Other current aggregates remain broad.** They may contain nontrade, derivative or restricted balances. Keeping them is an explicit population convention, rather than an assertion that undisclosed components are zero. Choosing this population removes the need for a pure-operating-cash reconstruction in this consumer; it does not complete such a reconstruction.
3. **Combined reported D&A is the selected aggregate.** The reported amount is source-verifiable. The later FY2024 note sum exceeds it by 355M; no plug reconciles that difference. Using the reported combined figure is a qualified model choice, not proof that the note populations exactly align with EBIT expenses.
4. **Cash PP&E is the stated investment definition.** No noncash finance-lease asset addition or principal repayment is inserted into that line. This does not establish comprehensive economic reinvestment across all financed/acquired/licensed assets.
5. **Reported ETR is an allocation convention.** It is not an observed unlevered cash tax rate or recurring forecast tax rate. SBC stays inside operating expense and is not separately added back.

The prior separate-tax preference is therefore refined materially by the all-year tax-inclusive population. The adopted method and final user report must state that refinement and its numerical effects explicitly; the audit does not interpret a recommendation as evidence of prior approval of an exact tax policy.

No claim is made here that the new series is universally more economically accurate than the old cash-convention series. The useful scoped result is that five source-verifiable, consistently defined model calculations are available without estimating Apple's undisclosed interest expense.

## Preserved open matters

- The legacy CFO method still lacks Apple's FY2024/FY2025 gross expensed interest.
- Apple FCFE still lacks a fully resolved financing population and lease-principal containment.
- History/forecast basis alignment and any direct historical calibration remain unapproved by this availability audit.
- Complete parent equity, dated shares/classes, awards and per-share readiness are separate.

The old strict-review ledger is not retroactively rewritten. The new Apple historical consumer is assessed under its distinct standardized definition.

## Replay

From the repository root:

```sh
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/operating-fcff-2026-11-04/independent-review/audit.py
PYTHONPATH=src .venv/bin/python -m unittest tests.review.test_apple_operating_history -v
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/operating-fcff-2026-11-04/independent-review/sealed_runtime_check.py /path/to/an/existing/current/private/runtime
```

The independent audit writes only its own folder. No production, source, adoption or financial-amount file was modified by this reviewer. The live API check verifies the retained response/catalog, while visual browser review and full valuation parity remain separately reported implementation checks.
