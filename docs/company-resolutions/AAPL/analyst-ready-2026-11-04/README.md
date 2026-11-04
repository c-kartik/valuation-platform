# Apple — five analyst-ready outputs

## Mandate and acceptance

The user approved a practical analyst standard, then instructed: “work on apple
to make all of those 5 outputs analyst ready.” This authorizes explicit,
reasonable modeling assumptions and implementation of this named Apple consumer.
It does not authorize invented source facts, current-price claims, a broader
universe rollout or public deployment.

The five outputs are historical FCFF, FCFF forecast/enterprise value, historical
FCFE, FCFE forecast/equity value, and fair value per share under both methods.
Current assessment: **ANALYST_READY_WITH_QUALIFICATIONS** for this contract, with
all five years FY2021–25 and five/ten-period perpetual-growth forecasts supported.
Earlier exact-reconstruction results remain unchanged and are superseded only
for the question of whether these analyst outputs may be used.

Requirements: source facts retain original dates/units/provenance; derived values
reproduce; chosen assumptions are exposed; uncertainties are tested and labeled;
no double counting; actual API/UI consumers work and stale values are identified.
Unknown disclosure is a qualification when a defensible convention exists, not
automatically a development blocker. Invalid inputs, broken arithmetic, hidden
assumptions and missing consumers remain genuine blockers.

## Issue → adopted treatment → effect

| Original issue | Adopted analyst treatment | Effect / qualification |
| --- | --- | --- |
| A1: missing FY2024/25 gross interest | Retain the already adopted uniform EBIT historical FCFF method across all five years. | Five values remain93.41/108.44/99.84/115.68/95.12B. No interest estimate or old-source change. |
| A2/A3: net Other and actual lease principal not decomposed | Historical FCFE uses reported CFO−cash PP&E+identified term-debt/CP net borrowing. Base excludes net Other by explicit convention and makes no extra guessed lease-principal deduction. An editable0–100% net-Other allocation tests the visible caption. |105.618/111.320/89.683/102.809/90.284B are standardized estimates, not verified full FCFE. Small net Other does not bound offsetting gross components. Existing source unknowns remain null. |
| SBC comparability | Keep CFO-based history visible; show an economic companion subtracting reported SBC once. Keep SBC expense within forward margins. | Economic companion97.712/102.282/78.850/91.121/77.421B. Neither historical variant is silently calibrated into forecasts. |
| A5:355M FY2024 D&A note difference | Retain the reported combined cash-statement D&A, without a reconciliation plug. | Remains a historical source qualification. Current forecast EV effect is zero when independent forward assumptions are held fixed; no claim that an economic forecast D&A error would be immaterial. |
| A7/A8: tax and NWC | Retain the approved historical tax-inclusive NWC/provision convention and independent forward18→20%/terminal20% tax assumptions. | Tax timing is not extrapolated as a recurring operating cash-tax observation. No new historical tax allocation. |
| S1: history/forecast population differences | Identify historical and forward methods separately; disable cross-basis CAGR/calibration. | Useful history does not require exact equality with a separately assumed forecast. |
| S2: absent default FCFE financing | Use opening carrying financing debt99.887B. Maintain constant net debt over explicit years, rolling cash maturities in net terms; interest=5.65%×opening debt. Financed assets are1/101 of total investment, matching the existing1% cash-PP&E overlay; corresponding aggregate repayment counts once. In the terminal year net debt grows at terminal growth. | All explicit financing rows and terminal inputs are generated, exported and checked through the existing FCFE engine. This is a net-financing convention, not Apple's disclosed gross maturity plan. |
| S3: cash eligibility | Gross cash/securities132.420B minus an analyst-selected2% of FY2025 revenue416.161B reserve. | Reserve8.32322B, eligible cash124.09678B. Editable, with0%/5% sensitivities. The ratio is neither a filing fact nor a CFA mandate. Ongoing operational liquidity costs are assumed included in forward margins/WC. |
| S3: debt bridge | Use term-debt fair value80.400B+CP7.979B+finance leases1.230B. |89.609B FCFF deduction; carrying-value99.887B comparison shown. Operating leases remain service expenses; no second operating-lease debt claim. FCFE never subtracts debt again after discounting. |
| S3: dated shares and awards | Use14,773,260,000 common shares dated2025-09-27 plus151,574,000 existing RSUs at100% vesting. Future SBC in margins is interpreted as a future-grant expense proxy. |14,924,834,000 valuation shares. No second existing-award settlement, grant-date-value deduction, exercise proceeds or21.8B future-cost cash deduction. Vesting fraction is editable. This approximates grant/service timing; it is not a grant-by-grant option valuation. |
| S3: other claims | Base assumes zero **additional non-operating** claim beyond ordinary forecast expense/tax coverage. Expose a user claim input and an illustrative23.242B stress. | Zero is a modeling choice, not a finding of no exposure. Gross UTB stress is not a proven liability or upper bound. Settled Ireland escrow is not deducted again. |
| Discount-rate provenance | Reproduce saved CAPM8.935%=5.05%+1.05×3.70%, debt cost5.65%, and Base target-weight WACC8.27275%. | Macro dates/source hashes are bound in policy.json; beta/spread/weights/shield remain analyst assumptions. Users can edit equity and debt costs; FCFF retains the selected operating WACC. |

## Valuation results and route consistency

Base FCFF enterprise value is2.5842351109656T, common equity2.6187228909656T and
fair value **175.4607716887/share**. Base FCFE operating equity is
2.2787840661172T; after eligible cash common equity is2.4028808461172T and fair
value **160.9988322897/share**. These are FY2025-origin analytical estimates
using later information, not current-date prices or contemporaneous backtests.

The14.4619393990/share difference is material and explicitly displayed. FCFF's
selected WACC uses target financing weights; FCFE's fixed explicit debt and CAPM
equity discount rate describe a different financing case. Matching operating
assumptions does not make those financing cases equivalent. We do not adjust
cash flow or discount rates to force parity. Both estimates remain analyst-ready
with that qualification; no claim of equivalent-route validation is made.

Fair value per share is an estimate under assumptions. No current market price,
consensus, upside percentage, recommendation or trading suitability is asserted.
Lower growth/margins and higher discount rates are the principal operating/value
risks; the report shows Bear/Base/Bull and individual bridge/rate stresses.

## Sources and reproducibility

`policy.json` is a separately pinned source projection, never a replacement for
original filings. It preserves five exact annual identities, original CFO/cash
PP&E/SBC observations, equity observation locations/receipts and hashes of the
prior source workpapers. Dated macro observations and original source manifests
are bound. `source_documents` identifies the upstream files for future updates.

Primary valuation methodology: [CFA free cash flow valuation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation),
[CFA diligence/reasonable basis](https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-a),
[Damodaran restricted shares/future grants, PDF page2](https://pages.stern.nyu.edu/~adamodar/pdfiles/eqnotes/valopt.pdf).
These support the framework; the numerical reserve, financing and claim choices
are our analyst conventions, not requirements prescribed by those sources.

```sh
PYTHONPATH=src .venv/bin/python scripts/build_apple_analyst_policy.py --check
PYTHONPATH=src .venv/bin/python scripts/report_apple_analyst_readiness.py --check
PYTHONPATH=src .venv/bin/python -m unittest tests.review.test_apple_analyst tests.api.test_apple_analyst -v
```

Implementation: `review/apple_analyst.py`, bounded isolated
`POST /api/v1/apple/analyst/run`, and the live Apple DCF panel. The current
selected operating case drives both valuations; six assumptions are editable,
changes require recalculation, stale/in-flight responses are guarded, and
outputs/financing/qualifications are exportable. Five/ten-year cases and all
three scenarios are exercised. Original Cash flows records are explicitly
labeled as the earlier evidence review; META and GOOGL are unchanged.

For updates: retain new filings, update the reviewed source mapping, compare
period/date/definition changes, regenerate a **new version** of this projection,
review analyst conventions, rerun numerical/source/API/UI checks and update pins.
Do not silently refresh an old source observation or treat a prior estimate as
newly reported fact. Validation is recorded in `validation.json`; independent
acceptance is in `independent-review.md`.
