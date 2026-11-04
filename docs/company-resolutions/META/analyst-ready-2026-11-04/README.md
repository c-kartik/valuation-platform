# Meta — analyst source and treatment contract

## Current acceptance and platform output

All five named outputs are **ANALYST_READY_WITH_QUALIFICATIONS** following source, arithmetic, isolated API, frontend and independent acceptance checks. Open the [implementation report](report.html), [validation record](validation.json) and [independent review](independent-review.md). The selected-case live DCF panel exposes editable assumptions and both share estimates; five/ten-period forecasts and all three operating scenarios are checked. Exact historical cash/ownership reconstruction is not claimed.

The user authorized Meta's five outputs at Apple's analyst-readiness level:
reasonable disclosed assumptions, reproducible calculations, and qualifications
instead of blanket exact-reconstruction gates. This is a **new named analytical
consumer**, not a rewrite of original filings or the earlier strict review.
The [policy](policy.json) projects retained facts and makes the choices below
explicit. Runtime/UI adoption and their independent checks are recorded by the
shared implementation; this source-preparation record alone does not certify them.

## Anchor inputs and selections

All balance/share observations represent **2025-12-31**, from Meta's original
FY2025 10-K, accession `0001628280-26-003942`. Exact source URLs, body digests,
inline IDs, instance contexts, precision, unit and class/award dimensions remain
in `facts`. Original reported precision remains authoritative.

| Input | Selected amount | Basis |
|---|---:|---|
| Cash and named marketable securities | $81.592bn | $35.873bn cash + $45.719bn marketable securities. Restricted cash is excluded. |
| Term debt carrying amount | $58.744bn | Net carrying amount; $59.000bn principal is alternative support, not additive. |
| Term debt disclosed fair value | $57.220bn | Selected notes fair value, with the original hierarchy/basis dimensions. |
| Finance-lease liability | $1.184bn | $0.308bn current + $0.876bn noncurrent; add once to the selected debt basis. |
| Financing debt, carrying / bridge proxy | $59.928bn / $58.404bn | Carrying debt funds FCFE; notes fair value + lease carrying is the FCFF bridge proxy. |
| Nonmarketable investments | $27.524bn | Note 5 total, including equity-method $7.448bn. **Do not add $7.448bn again.** |
| Dated common shares | 2,530 million | Class A 2,187m + Class B 343m; agrees to reported common total. Later cover-date and EPS weighted shares are not selected. |
| Unvested RSUs | 115.552 million | Anchor award count; not weighted-average diluted EPS shares. |

Note 5 verifies measurement-alternative holdings $20.076bn plus equity-method
holdings $7.448bn equal the $27.524bn total. The default additional-assets
adjustment uses **the total once at carrying value as an analyst proxy**, not a
claimed market value. Note 5 describes unconsolidated VIEs, and the operating
forecast begins with consolidated EBIT rather than investee earnings. The
carrying proxy, exclude-all and half-carrying sensitivities make the investment
judgment visible. It does not value these holdings as available cash.

## Issue → treatment → effect

| Issue | Adopted analyst treatment | Effect and retained qualification |
|---|---|---|
| Unidentified Other financing | Default allocation to net borrowing 0%; retain identified notes proceeds, overdraft funding and finance-lease principal. Make residual allocation editable. | Five FCFE estimates become usable under an explicit approximation. Other remains −13/+344/−111/−277/+2,220m. Allocation stress is **not a bound** on offsetting unidentified gross flows. |
| Gross versus net cash PP&E | Preserve the approved net-of-identified-receipts history and its source vintage. | FY2022 receipts245m and FY2023 receipts221m are netted once. FY2021 original investment is already net; later gross/net controls reproduce it. |
| Capitalized versus expensed interest | Preserve the approved expensed-interest historical FCFF convention; do not add capitalized interest a second time. | Reported FY2024/25 capitalized interest384m/535m stays a scope qualification. Historical cash PP&E and forecast cash plus financed investment are labeled differently. |
| Exceptional FY2025 tax provision | Preserve reported historical CFO and tax allocation. Use separately disclosed analyst recurring forecast tax. | No automatic cash add-back of the15.930bn accounting charge or14.030bn valuation allowance; reported CFO already reflects its cash/noncash accounting. |
| Eligible excess cash | Reserve2% of anchor revenue, then add the remainder of named unrestricted cash/marketable assets; reject a reserve above observed liquidity. | Reserve is an editable operating-cash proxy, not a reported requirement. Restricted cash is not available excess cash. |
| Strategic/unconsolidated investments | Add total27.524bn carrying proxy outside EBIT value; test0%/50%. | Equity-method7.448bn is nested, preventing double counting. No assumption that carrying equals realizable fair value. |
| Debt and leases | Use notes fair value plus finance-lease carrying proxy for FCFF bridge; carrying debt plus lease amount for FCFE interest/rollover. | Do not add principal, carrying and fair value together. Operating leases remain service costs and are not a second financing claim. No second debt subtraction after FCFE discounting. |
| Share classes | Equal per-unit cash-flow claim across A/B, without a control premium. | Source Note3 states identical liquidation/dividend rights with different voting rights. No voting-equivalence claim. |
| Existing awards | Add assumed vesting fraction of115.552mRSUs to dated shares; default100%. Keep future SBC expensed. | Conservative dilution proxy, not an option-pricing or current award-fair-value calculation. Do not also deduct54.810bn unrecognized future service cost or grant-date value. Potential future-service overlap bias remains visible in vesting sensitivity. |
| Other legal/tax/contingent claims | Default additional separate claim0; keep identified operating accrual effects within modeled cash flows and expose an editable deduction. | This is an analytical baseline, **not a factual assertion that all exposures are zero**. Note5 Louisiana venture maximum exposure45.95bn combines equity, future funding, leases and RVGs; it is not a current expected-loss claim. RVG payments were reported not probable. Alternative expected incremental losses belong in a claim stress rather than deducting the maximum mechanically. |
| Minority attribution | Default separate NCI claim and minority cash share0 for this Meta analytical perimeter; fixed in this named Meta perimeter; a new separate minority population requires its own policy version. | Zero is an assumption, not a fabricated reported fact. Meta's stakes in unconsolidated investees are its assets, not automatically outside-owner claims against Meta. |

The future financing policy uses the existing registered3% financed-assets-to-
cash-PP&E ratio. Net rollover, interest and terminal financing are explicit model
assumptions; no company maturity or leverage promise is inferred. The registered
WACC uses target5% debt; a flat explicit FCFE debt model can produce a different
answer. The two valuations must not be forced equal through a plug.

## Five-year cash-flow operands

USD millions, with FCFF rounded only in this table. FCFE here is the default
identified-financing CFO-based estimate **before reversing SBC**; the economic
SBC variant subtracts the exact CFO add-back once and remains separately labeled.

| FY | CFO | Net cash PP&E | Identified net borrowing | Other financing | SBC add-back | FCFF | Default FCFE |
|---|---:|---:|---:|---:|---:|---:|---:|
|2021|57,683|18,567|−663|−13|9,164|39,135.150|38,453|
|2022|50,475|31,186|9,071|344|11,992|19,437.930|28,360|
|2023|71,113|27,045|7,397|−111|14,027|44,435.667|51,465|
|2024|91,328|37,256|8,463|−277|16,690|54,702.987|62,535|
|2025|115,800|69,691|27,382|2,220|20,427|46,928.643|73,491|

Historical FCFF = CFO + expensed interest ×(1−reported provision/pretax income)
− net identified cash PP&E. Historical FCFE = CFO − net identified cash PP&E +
identified borrowing + selected fraction of residual Other financing. Historical
taxes, SBC cash-flow add-backs and investment perimeter differ from the forecast;
no automatic cross-basis cash-flow CAGR or forecast calibration is approved.

## Discount basis

The existing registered Meta discount profile is reused, rather than importing
Apple's beta or debt weight. Retained source bodies and hashes are checked:
Treasury10-year5.05% at2026-10-28; Damodaran implied ERP3.70% for October2026;
configured analyst beta1.20, credit spread0.90%, equity/debt targets95%/5%,
tax shield20%. Therefore cost of equity is **9.49%**, pretax debt cost **5.95%**
and saved Base WACC **9.2535%**. These are dated macro observations plus analyst
assumptions, not company-reported costs. The valuation origin is FY2025 with
later-filed information, not a historical point-in-time investable backtest.

## Reproduce

```sh
PYTHONPATH=src .venv/bin/python scripts/build_meta_analyst_policy.py --check
```

The builder replays all five complete financing statements, rebinds all52
balance/share source points, independently re-extracts five CFO/SBC/PP&E annual
facts, checks gross-to-net investment, class and lease sums, and verifies the
rights and investment-scope prose against retained original filings. It retains
source-document hashes and never edits the source bank or earlier decisions.
Changes require a new reviewed policy version and runtime digest; this file
does not relax arithmetic, source contradiction or integration failures.

The conceptual basis follows [CFA free cash flow valuation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation)
and [Damodaran's separation of existing awards from future compensation](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/mgtoption.htm).
Those references inform the methodology; they do not mandate these issuer-specific
reserve, dilution, financing, investment or claims assumptions.
