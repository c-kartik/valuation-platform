# Independent acceptance review

Verdict: **PASS WITH DISCLOSED QUALIFICATIONS** for the five Apple analyst outputs under the newly approved analyst-use contract.

Scope: FY2025 fiscal-end analytical origin (2025-09-27), later-filed information, five historical annuals FY2021–FY2025, and Bear/Base/Bull operating forecasts at five- and ten-year horizons using independent perpetual-growth terminal inputs. This verdict does not certify exact historical full FCFE, current-date share value, issuer-certified analyst assumptions, exit-multiple FCFE, or the paused wider universe.

## Independent verification

- Reviewed `review/apple_analyst.py`, policy projection builder, existing FCFE engine, HTTP intake/isolated worker/bundle binding, Apple frontend controls, result matching, and workspace integration.
- Source projection replay passes; all seven referenced source-document hashes agree with the retained source artifacts. The five historical CFO, cash PP&E, identified borrowing and Other-financing projections agree with their underlying financing records. The original source values and unknown financing components remain unchanged.
- Performed a separate exact-Fraction arithmetic replay across six scenario/horizon combinations. Starting from anchor revenue and submitted annual ratios, independently calculated revenue, EBIT, taxes, D&A, investment, working capital, FCFF, FCFE, annual discounting, terminal borrowing, terminal debt, both terminal values, equity bridges and per-share outputs. All comparisons pass. Matrix and 337 independent assertions are recorded in `independent-review.json`.
- Terminal debt remains constant during the explicit forecast and grows with terminal growth thereafter. The first terminal period uses opening-debt interest and required net borrowing; zero-growth and negative-growth terminal cases were additionally checked. Matched financed-asset additions and principal offset once. Debt is deducted from the FCFF bridge and not deducted again from FCFE.
- Focused Python review/API tests: **11 passed**. This includes a real sealed-bundle isolated HTTP worker, edited assumptions, ten-year requests, input rejections, and before/after preservation of Apple legacy evidence plus META and GOOGL histories.
- Focused frontend tests: **10 passed**. This includes automatic initial calculation, exact units, manual recalculation, stale labeling after edits, late-response rejection across scenario/horizon changes, cancellation, explicit retry, unsupported terminal methods, input preservation and non-Apple isolation.

## Financial judgments accepted under this contract

1. Historical FCFE excludes unidentified financing components by explicit assumption; it is labeled standardized/estimated, not exact. Allocating the observed net Other caption is a sensitivity, not a bound on unknown gross financing. The separately displayed economic variant subtracts reported SBC.
2. Reported combined D&A is retained. Its FY2024 note discrepancy stays disclosed. Since historical calibration is disabled, changing historical D&A alone does not change the independently specified forecast; this is not a claim that the unexplained source difference is economically zero in every possible model.
3. Tax-inclusive historical NWC and forward normalized tax/WC assumptions are distinct disclosed definitions. Historical and forecast populations are not silently equated.
4. The 2% operating-cash reserve, full existing-RSU vesting, zero additional claims, borrowing rollover, debt interest cost and other judgments are editable analyst assumptions. Zero claims does not establish zero exposure. Gross cash, dated shares and debt observations remain source facts.
5. Existing RSUs use a stated share-dilution proxy; no duplicate award-value deduction is made. Forecast compensation is treated as a future-grant expense proxy in margins. This is an approximation, not a precise security-by-security award valuation.
6. FCFF WACC target financing weights and FCFE flat explicit debt are deliberately different assumptions. Their values consequently need not agree; the difference is displayed. Neither method is represented as a reconciled equivalent of the other under identical financing.
7. Debt fair-value and carrying-value conventions are disclosed. Operating leases stay in service expenses rather than being deducted again. Debt and cash adjustments use the named historical date, not current balances.

## Findings

No unresolved blocking defect identified within this named analyst-output scope. Remaining exact-reconstruction questions are retained as qualifications in the earlier evidence-review records. They are not silently declared solved. Any later alteration to the source projection, financial conventions, financing policy or consumer scope requires a new validation of this verdict.

The ten-year matrix here extends the fifth-year annual assumptions for the independent engine exercise. It validates engine/horizon handling; it does not endorse that extrapolation as a uniquely preferred years-6–10 forecast policy. The frontend's selected submitted ten-year assumptions remain the actual consumer inputs.
