# Apple — stage4 dated equity/share input review

**Outcome: partial source-bound review; verified equity value and value per share remain unavailable.** The approved plan selects the anchor-date ordinary common population as denominator support and distinguishes debt measurements, while preserving missing eligibility/claim/award decisions.

A fresh replay of retained primary inline and XBRL source observations verifies these non-overlapping populations at2025-09-27:

| Observation | Amount | Treatment |
|---|---:|---|
| Cash/current/noncurrent marketable securities |132.420B|Three parent captions summed once; not certified excess cash|
| CP+current/noncurrent term debt, carrying values |98.657B|Named debt carrying subtotal, not complete financing claims|
| Term-debt disclosed fair value |80.400B|Alternative to90.678B term carrying value; not added to it|
| Finance-lease liability |1.230B|Current+noncurrent; separate from operating-lease service policy|
| Anchor-date common shares outstanding |14,773,260,000 shares|Date-matched ordinary population selected; not EPS-weighted or later cover-date shares|
| Unvested RSUs |151,574,000 awards|Source observation, not automatic dilution|
| Unrecognized future service cost |21.800B|Not a fair-value deduction or a full award valuation|

The disclosed term principal91.281B differs from carrying90.678B by603M of aggregate net discount/cost arithmetic. The carrying-to-fair-value difference10.278B is a comparison, not an extra claim. Exact sources, periods, source precision, primary and instance locators and hashes are in[results.json](results.json). Fair value80.4B retains its rounded100M disclosure precision.

## Applied decisions

1. Selected the exact2025-09-27 `CommonStockSharesOutstanding` population, independently agreeing with reported issued shares. Later2025-10-17 cover shares and weighted-average EPS shares do not replace it. An award-adjusted denominator remains null.
2. Separated gross cash/securities from eligible excess cash. The filing does not prescribe the analyst's required operating liquidity; absence of a separate restriction is not proof every balance is freely distributable. No zero operating reserve or automatic cash eligibility is adopted.
3. Distinguished market-debt fair value from carrying/principal observations. The disclosed fair value is prepared as the anchor-date term-debt candidate. CP, finance leases and other potential claims need a coverage/measurement decision before one complete financing-claim operand can be published.
4. Kept operating leases in the service-cost policy rather than automatically subtracting the reported operating-lease liability again. Finance-lease principal still needs cash-containment evidence for historical FCFE; its year-end liability is not a cash repayment.
5. Prepared tax/legal/pension/contingent-claim review against forecast settlements. The23.242B unrecognized-tax-benefit source is not automatically deducted as a separate claim; doing so could duplicate taxes or omit timing/probability.
6. Preserved future SBC expense. Existing vested/nonvested award rights, future service, forfeiture, withholding and settlement need a non-overlap treatment. Neither the entire RSU count nor grant-date weighted-average fair value becomes current dilution/fair value by default.
7. Preserved route consistency: FCFF at WACC with a separate equity bridge; FCFE at matching cost of equity without a second debt subtraction. The unresolved financing/tax/investment populations prevent asserting that the two routes presently produce the same fair value.

## Numerical diagnostics and limits

The replay calculates only the per-share effect of a1B cash/claim change and the difference between using disclosed debt carrying/fair values, before all other adjustments. These are sensitivity measures, not share-price outputs, fair-value bounds or approved missing-claim assumptions. Complete eligible cash, financing claims, other claims, award adjustment, common equity and fair value/share remain **null**.

The platform now exposes these observations in a collapsed source-review panel. They do not populate the manual equity editor as eligible cash or declare coverage on the user's behalf. Actual manual entries remain supported by the unchanged bridge engine and explicitly qualified by their supplied declarations.

## Replay

```sh
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/equity/replay.py --check
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/equity/test_replay.py -v
```

Four tests cover source sums, dates/EPS substitution rejection, no duplicate carrying/fair values and missing claims/awards remaining null. The source replay does not alter old schedules or any issuer's financial amounts.
