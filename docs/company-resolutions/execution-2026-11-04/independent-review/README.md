# Independent review of the November 4 four-step execution

**Verdict: the reviewed arithmetic and consumer separation pass. Financial company reviews remain OPEN.** This is not clearance of all 30 parent-common cash-flow cells or valuation readiness.

The reviewer did not edit implementation, input ledgers, financial values, classifications or source receipts. The independent arithmetic script imports no production calculation code. It recomputes using Python `Fraction`, then compares against execution artifacts. A separate consumer check calls the actual reader and compares its classifications with that independent oracle.

## Checks performed

- Recomputed Apple's five operating-income/cash-flow reconciliation identities using retained operands and statement rows. All five bridge differences are exactly zero. Neither diagnostic becomes certified operating FCFF or a forecasting calibration input.
- Independently recalculated the 13 populated cash-convention FCFF observations. Decimal serialization differs from exact fractions only below 1e-30 dollars; the reported input precision remains unchanged.
- Recomputed all 15 financing-statement sums, net identified borrowing totals and FCFE calculations. All statement ties are exact. Apple and Meta remain provisional; no unknown Other component is replaced by zero or bounded by the net Other caption.
- Rechecked 191 fact/statement observations against retained extracted XBRL instances, annual context dates, no segment dimensions and source hashes. Rechecked 30 retained body hashes. Separately matched all 73 non-null FCFF formula operands to annual facts in those instances, allowing explicitly approved net cash PP&E to reconcile to reported gross PP&E and identified disposal receipts. Comparative interest observations may come from a later annual filing; issuer and target-period context remain exact.
- Classified the 30 metric observations independently: 13 available cash-convention FCFF, five available consolidated FCFE before minority attribution, ten provisional FCFE and two missing FCFF inputs.
- Confirmed the actual reader matches those classifications, preserves the entire original company record, adds readiness only, and does not disable manual forecasting because historical inputs are missing.
- Confirmed the pinned projection remains SHA256 `9b2a9d775745e9d4bd08efe60d49619c24f632b16a28fce5fcba014fe1f55d86`. All amounts and old clearance flags remain unchanged.
- Confirmed all 15 parent-common FCFE amounts remain null. Together with Apple's two missing FCFF observations, the original strict review still has **17 failed cells**.
- Within the narrower consolidated-history consumer, **12 observations remain unresolved**: two Apple FCFF measurements and ten Apple/Meta provisional FCFE classifications. Alphabet contributes a further **five parent-common attribution failures** under the original strict contract; those five are not missing consolidated measurements.
- Confirmed Alphabet outside-capital contributions are excluded from borrowing, redeemable NCI is recorded as already included in book NCI, no book NCI becomes fair value, and no 2026 financing round becomes a FY2025 input. Lease principal remains inside the approved parent debt-repayment population with zero additional deduction. The parent-value bridge is unpopulated; no invented equity or per-share result is produced.
- Read the readiness helper, history reader and history component; executed the three focused Python readiness tests and seven focused history/FCFE UI tests successfully.

## Apple numerical decomposition

USD billions, rounded here only for readability. Exact fractions are in `results.json`.

| Fiscal year | Provision minus cash taxes | Aggregate after removing that conversion, still unclassified | Tax-timing diagnostic, **not FCFF** |
|---|---:|---:|---:|
| 2021 | -10.858 | 3.694 | 95.681320 |
| 2022 | -0.273 | 0.412 | 102.957877 |
| 2023 | -1.938 | -2.942 | 91.170837 |
| 2024 | 3.647 | -2.092 | 93.267805 |
| 2025 | -22.650 | 2.288 | 108.824892 |

The observable provision/cash-tax difference can be algebraically separated from the aggregate reconciliation. That identity does **not** identify the actual tax-bearing caption, prove the remainder is operating working capital, align the D&A expense population, or establish an economic investment perimeter. These numbers must not be inserted as verified FCFF. The implementation retains those limits correctly.

## Issues found and corrected during this audit

1. **Issuer switching:** previously, retained Apple data could remain visible under a newly selected Alphabet heading while the replacement response was pending. The implementation owner cleared state and gated display on matching ticker. The new delayed switch without remount regression passes.
2. **Alphabet schedule pin:** stage 3 consumed its prior schedule without including it in the initial baseline pins. The implementation owner added an explicitly supplemental schedule pin, verified against the original stage-3 input hash and Git HEAD. The record does not pretend that the pin was present at the original start time.

No unresolved arithmetic, availability-classification, parent-common relabeling or double-counting defect was found in the reviewed implementation after those corrections.

## Remaining limitations

- Apple FY2024/FY2025 gross expensed interest remains unavailable under the adopted cash-convention formula. The alternative operating route still lacks certified working-capital, expense-aligned D&A and investment alignment. A reconciliation identity is not a substitute for those classifications.
- Apple/Meta Other financing and Apple's finance-lease principal containment remain unresolved. The prepared questions are draft requests, **not sent** and not answers. No ten provisional FCFE records become complete from this work.
- Alphabet's five consolidated FCFE observations are available under the stated convention; its exact annual parent-common cash attribution and dated NCI fair-value bridge are still unresolved. A value bridge would not itself prove annual cash allocation.
- Historical/forecast SBC, tax and investment alignment, explicit forward assumptions, claims, shares/classes and awards remain separate checks. The UI does not certify them.
- This audit verifies the retained historical source and calculation chain. It did not acquire new public disclosures, re-adopt economic conventions, establish legal class rights, certify market inputs, perform a fresh visual browser inspection, or independently validate every pre-existing DCF engine path.

## Replay

From the repository root:

```sh
.venv/bin/python docs/company-resolutions/execution-2026-11-04/independent-review/audit.py
PYTHONPATH=src .venv/bin/python docs/company-resolutions/execution-2026-11-04/independent-review/consumer_check.py
PYTHONPATH=src .venv/bin/python -m unittest tests.review.test_cashflow_readiness -v
```

The focused UI test command is `node node_modules/vitest/vitest.mjs run src/workspace/CashFlows.test.tsx` from `frontend/` using the configured Node runtime. Execution replays write only this independent-review folder.
