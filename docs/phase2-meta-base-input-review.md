# META Base case — first actual-input review

**2026-10-18 · PREPARATION / RECOMMENDATIONS ONLY.** All actual inputs and
selections below await one consolidated user review. No financial acceptance,
valuation execution or historical approval change is recorded. Financial-input
sufficiency remains **NOT_ASSESSED**. No forecast, indicative EV or per-share
value has been calculated.

META consolidated (Family of Apps and Reality Labs), CIK **1326801**; selected
10-K **0001628280-26-003942**, annual **2025-01-01–2025-12-31**. Forecast periods
are ordinal 1–5, labeled **FY2026–FY2030**. Analytical t=0 is **2025-12-31**,
with annual end-year discounting and later-filed information; this is neither a
contemporaneous backtest nor a current market-date case. An information cutoff
has not been established; no current market data or new evidence is assumed.

The [consumer contract](phase2-meta-base-consumer-contract.md) approves P2M-01–13
engine conventions and P2M-14 synthetic implementation, separately from actual
inputs. Versions: `meta-base-fcff-v1`, `fiscal-end-annual-gordon-v1`,
`meta-base-equity-bridge-v1`. Existing [assumptions](../src/valuation_platform/valuation/assumptions.py),
[anchor adapter](../src/valuation_platform/valuation/consumer.py),
[forecast](../src/valuation_platform/valuation/forecast.py),
[discounting](../src/valuation_platform/valuation/discounting.py) and
[bridge](../src/valuation_platform/valuation/bridge.py) interfaces are unchanged.
Numerical and declared-compatibility checks do not authenticate decisions,
prove economic completeness or detect hidden overlap inside aggregate rates.

**Retained authority and reference key.** The
[META historical schedule](company-data-preparation/META-analyst-input-package.md)
and [package](company-data-preparation/meta-analyst-input-package.json) remain
authoritative for their approved historical perimeter only. In that JSON:
`F` = `/periods/4/facts`; `N` = `/periods/4/passages` (retained primary excerpts,
offsets and source digests); `C` = `/periods/4/calculations`;
`E` = `/current_history/periods/4/inputs`.
`L` = [claims ledger](retained-claims-shares-ledger.json)
`/rows/34/fields/other_equity_bridge_claims_assets`, also retained at package
`/periods/4/preparation_ledger_evidence/retained-claims-shares-ledger/source_record/fields/other_equity_bridge_claims_assets`.

| Historical binding | Exact retained value / reference |
| --- | --- |
| Revenue anchor, not a manual assumption | `E/revenue` → `F/revenue`: **200,966,000,000 USD**, precision `-6`, FY2025, reported; base scale 1 |
| Historical audit | `/history_approval`, sequence **1**, **2026-10-17T18:17:50.735170+00:00**; SHA256 `ac2514aa5c57e8959f38f90e9cd8687748b490a01d75647e172b2922fed54927` |
| Audit source / revisions | Source commit `9bb110cb208ce3abcac0365c4ecf4820c498d60d`; source revision `19907563235d652f5913f92ede3d2c41035d096f665304d35759a312b7383178`; review revision `d253b875b14907963169fd7734e01fdf2500de01d0d447cc4b7fb4fb9bbb24ec`; proposal revision `8fedd075ac4d3ed087bb134b6a3bf409ec232d905410faa04e765f6f403b7b3d` |
| Primary source | `/periods/4/sources/0` → [receipt ledger](evidence/independent-validation-document-acquisition.json) `/artifacts/0`; body SHA256 `4ecf3d7d694870ae63f53dca8995e92dc0646cf7dad98eafaf743c2ac24fbbc4` |
| Instance source | `/periods/4/sources/1` → [receipt ledger](evidence/income-binding-repair.json) `/artifacts/13`; body SHA256 `6ad129780910ee26dfa4edcc98d33b0929f2365f5e3d64d1fc120014924aebfe` |

The effective view is `/current_history`, version 1; original proposals under
`/periods` and audit decision payloads remain historical. Historical
`valuation_consumption_approved=false`, incomplete expense D&A/reinvestment/debt
and potentially unbounded omissions are preserved. The [Phase 1 pause](phase1-universe-pause-checkpoint.md)
remains in force: 24 completed scoped histories, 3 partial, 15 assessment-only;
199 selected annuals, 11 deficits. No company review resumes.

## A. User-supplied forecast, WACC and terminal values

**All 37 numerical entries are UNSET.** Supply rates as explicitly labeled
percentages or fractional decimals; preserve the submitted values and rationale,
with finite Decimal fractions at eventual intake. No historical averaging,
default WACC/g, illustrative rates or automatic Year-5 terminal copy is proposed.
IDs A01–A06 identify five values each, in FY2026–FY2030 order.

| ID / input | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| A01 Revenue growth | UNSET | UNSET | UNSET | UNSET | UNSET | Compound each rate from prior-year revenue, starting with the FY2025 anchor. |
| A02 Operating margin | UNSET | UNSET | UNSET | UNSET | UNSET | Forecast consolidated EBIT/revenue including SBC, operating-lease service costs and the agreed depreciation expense. |
| A03 Operating tax rate | UNSET | UNSET | UNSET | UNSET | UNSET | Apply the unlevered operating rate to positive EBIT only, with no immediate loss benefit or NOL model. |
| A04 Expense-aligned D&A/revenue | UNSET | UNSET | UNSET | UNSET | UNSET | Add back only D&A already deducted in that year's forecast EBIT, including finance-asset depreciation once. |
| A05 Investment/revenue | UNSET | UNSET | UNSET | UNSET | UNSET | Subtract cash PP&E plus non-overlapping new finance-leased operating assets, excluding finance principal. |
| A06 WC cash requirement/full revenue | UNSET | UNSET | UNSET | UNSET | UNSET | Multiply a signed cash requirement by full forecast revenue, positive for a use and negative for a release. |

| ID / input | Value | Meaning |
| --- | --- | --- |
| A07 Constant WACC | UNSET | Discount nominal USD unlevered FCFF at one manual rate consistent with the financing/lease conventions. |
| A08 Terminal growth | UNSET | Grow Year-5 revenue into the terminal year and perpetuity at one sustainable nominal USD rate. |
| A09 Terminal operating margin | UNSET | Supply sustainable terminal EBIT/revenue including SBC, service leases and the aligned D&A expense. |
| A10 Terminal operating tax rate | UNSET | Supply terminal tax on positive operating EBIT under the same no-loss-benefit convention. |
| A11 Terminal D&A/revenue | UNSET | Supply the expense-aligned terminal add-back independently of Year 5. |
| A12 Terminal investment/revenue | UNSET | Supply replacement and growth investment, including non-overlapping new finance-leased assets. |
| A13 Terminal WC cash requirement/revenue | UNSET | Supply the sustainable terminal cash requirement against full terminal revenue. |

Structural bounds: growth ≥−1; annual/terminal tax in [0,1]; D&A/investment ≥0;
finite unrestricted margins and signed WC rates; WACC >0 and −1 <g<WACC.
These bounds alone do not make the forecast economically coherent.

**Joint review (C01):** reconcile margin depreciation with A04/A11 and investment
timing/replacement/growth with A05/A12; exclude operating ROU amortization,
finance principal and a second capital-creditor settlement deduction. Explain
the unlevered tax basis rather than copying reported ETR/cash tax; reconcile any
omitted tax benefits/obligations. Justify terminal growth together with terminal
investment/WC and WACC, including any perpetual releases. Retain SBC expense
once and distinguish future employee service from existing award rights (C06).
Six ratios cannot expose embedded duplication. No complete historical NWC
reconstruction is required for this independently specified cash-ratio path.

Optional historical context is already in the linked schedule: `F/ebit`
83,276 USDm, `F/da` 18,616 USDm, `F/cash_capex` 69,691 USDm gross cash purchases,
`F/sbc_expense` 20,427 USDm and `F/reported_etr` 0.296, all FY2025.
Monetary fact precision is `-6`; ETR precision is `3`. `E/depreciation_amortization`
is a **limited CFO D&A proxy**, not complete expense-aligned calibration;
historical cash Capex excludes the broader forecast financed-investment scope.
ETR is reported tax context, not the approved forecast rate. No ratios are
calculated here and no observation is promoted into A01–A13. Incomplete proxies
prevent automatic complete calibration, not independently reviewed manual inputs;
that review resolves no historical unknown.

## B. Proposed actual bridge/share selections needing approval

This is a compact selection view of the existing
[Stage C proposal](phase2-meta-base-consumer-contract.md#7-proposed-stage-c-decision-sheet),
which retains the full inventory and rationale. **Every B item is PROPOSED,
not selected.** Amounts are **USD millions at 2025-12-31** unless explicitly
stated; eventual operands must be base USD at scale 1. R = reported fact;
RN = retained reported note observation, not a new fact registration;
D = retained derivation; P = proposed valuation proxy; O = omission assumption.
F/L original precision survives; N amounts retain their displayed rounding
(e.g. Notes $57.22bn), without invented extra digits.

| ID / retained reference | Date, amount/unit and origin | Proposed treatment / non-overlap / pending decision |
| --- | --- | --- |
| B01 Cash/current marketables: `F/cash`, `F/marketable_current`; parent `C/0`, `E/cash_investment_components/selected` | 35,873 +45,719 USDm R; parent 81,592 USDm D | Use only as eligibility starting populations; choose eligible parent **or** children. Eligible addition remains **UNSET**: approve reserve/restriction policy and amount (C02), never gross=excess cash. |
| B02 Restricted populations: `F/cash_restricted_parent`, `N/9`, `N/11` | Cash/restricted parent 39,100 USDm R includes 35,873 cash plus restricted 837 current and 2,390 other assets RN; separate fair-value-table restricted observation 2,539 USDm RN | Recommend exclude separately restricted amounts from eligible assets and retain as support. Do not add the 39,100 parent or subtract restrictions again from a gross population that excludes them. The 2,539 scope is not a complete partition; approve policy, not a residual reconciliation (C02). |
| B03 Strategic holdings: `N/0`, `F/equity_method`, `L/observations/0` | Nonmarketable 27,524 USDm RN =20,076 measurement alternative RN +7,448 equity method R/RN | Consider **+20,076 P** only after approving carrying-value proxy and exclusion of its returns/value from operating EV. Defer 7,448 addition pending venture perimeter. Parent/children are alternatives; Scale AI 13,800 and Jio 5,820 USDm RN within 20,076 are support only. Resolve C03; neither carrying figure establishes realizable value/excess cash. |
| B04 Notes: `N/1`; alternatives `F/debt_long`, `F/debt_parent`, `F/debt_discount` | Estimated fair value 57,220 USDm RN; carrying 58,744 USDm R (duplicate QNames); face 59,000 USDm RN less discount/issuance costs 256 USDm R | Recommend **−57,220** as the named fiscal-end Notes measurement. Approve valuation use and rounded Level 2 measurement; carrying/face/discount remain support, not additional claims/assets. Does not establish complete financing (C04). |
| B05 Finance leases: `F/finance_lease`, `F/finance_current`, `F/finance_long`; financing parent `C/1`, `E/debt_lease_components/selected` | Liability 1,184 USDm R =308+876; historical named financing 59,928 USDm D =58,744+1,184 | Recommend **−1,184 P** carrying-liability proxy alongside B04, subject to approval of economic-value simplification. Never also deduct children or 59,928; that subtotal already embeds leases. Finance interest/principal are outside FCFF (C04). |
| B06 Operating leases/operating assets: `F/op_lease`, `F/op_current`, `F/op_long`, `N/19` | Operating liability 25,153 USDm R =2,213+22,940; gross finance ROU assets 8,187 USDm RN in PP&E | Recommend no separate service-lease liability deduction or operating/finance ROU asset addition under approved conventions. Confirm actual forecast service expense and finance depreciation/investment alignment (C01); exclusions do not assert zero obligations. |
| B07 Unpaid obligations: `F/capital_creditors`, `N/9`; `F/finance_principal_cash`, `F/finance_interest_cash` | **FY2025 duration**, `as_of=null`: unpaid PP&E 9,331 USDm R; acquisitions/intangibles in payables/other liabilities 2,659 USDm RN; finance principal 2,524 /interest 31 USDm R | Supporting observations, not verified instant claim PVs. No new fiscal-end debt stock or second purchase/payment deduction. Resolve future settlement coverage and dated claim scope through C05; do not infer an amount or default zero. |
| B08 Venture/other claims/assets: `N/18`, `N/19`, `N/1`, `N/4`; `E/other_equity_bridge_claims_assets/additional_adjustment`, `E/debt_lease_components/no_additional_adjustment`; `L/observations/4`–`L/observations/8` | Louisiana investment 1,830 USDm RN, leases ≈12,310, RVG threshold ≈28,000, max exposure 45,950; other VIE exposure/carrying investments 5,580; contractual commitments 131,050 USDm RN. Additional claims/borrowing **null O, unbounded**. Net accounting DTA 12,195 USDm R, overlapping gross/children/allowance | Venture investments support the 7,448 equity-method family, not additions to it; max exposure includes investment/funding/leases/RVG, not a claim PV. Recommend no gross commitment/max-exposure or accounting-DTA adjustment. Approve named exclusions separately; C03/C04/C07 still require treatment. Historical omission approval transfers no valuation authority and supplies no zero. |
| B09 Fiscal-end common basis: `F/shares:CommonStockSharesOutstanding:2025-12-31:e7683adf`; class suffixes `:1765640c` / `:1ca1ddc4` on the same key prefix | 2,530,000,000 shares R independently reported aggregate; A 2,187,000,000 /B 343,000,000, all 2025-12-31, precision `-6` | Recommend aggregate as **starting** denominator; approve A/B 1:1 economic equivalence, no voting/control premium, for A-share-equivalent output. Classes support, never add to aggregate. Final valuation shares remain **UNSET** until C06; not an approved diluted count. |
| B10 Later/average/award observations: `F/shares:EntityCommonStockSharesOutstanding:2026-01-23:1765640c` / `:1ca1ddc4`; `F/weighted_basic`, `F/weighted_diluted`; `F/shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2025-12-31:3de8d43f`; `N/2`, `N/3` | Cover A 2,187,177,748 /B 342,377,716 shares at 2026-01-23 (`INF`); FY2025 EPS basic 2,521,000,000 /diluted 2,574,000,000 shares (`-6`); unvested RSUs 115,552,000 at 2025-12-31 (`-3`), grant-date $500.68/share and unrecognized expense $54.81bn RN | Recommend support/exclusion from automatic denominator arithmetic: dates and period averages differ; awards are not issued shares. Retain future-service SBC in margins without a duplicate issuance/repurchase charge; this does not predict zero issuance. Existing award allocation/value, relevant proceeds and tax effects remain unresolved (C06); no treasury-stock, grant-date-value deduction or invented diluted count. |

Bridge signs remain EV +eligible assets −financing −other equity claims;
per-share divides by explicitly approved positive dated shares. Actual use
requires reviewed coverage for each role, component population identities,
source/decision references and explicit omissions with rationale; an empty list
is not evidence of absence. These are the existing Stage C input obligations,
not a new approval system. References remain declarations, not authentication.

## C. Unresolved requirements and optional refinements

“Blocks” identifies the affected output, not a research instruction. An omission
may bound a **named scope** without providing a numerical bound on omitted value;
the two must not be confused. **No unbounded omission below is recommended as a
shortcut to a complete per-share case.** Retained evidence is insufficient where
stated; leave the requirement open rather than start an acquisition chain.

| ID / why it matters | Decision/input to resolve | Bounded omission defensible? / remaining limitation | Blocks |
| --- | --- | --- | --- |
| C01 Actual operating/tax/terminal consistency | A01–A13 plus authored, dated rationale for growth, margin/SBC/lease expense, aligned D&A/investment/WC, tax and sustainable g/WACC; specify capital-creditor and venture cash coverage | No omission of required rates or scope review. Historical reconstruction/new evidence is not universally necessary for an independent manual forecast. Complete historical calibration is an optional separate refinement, not approved here. | Forecast/EV; hence downstream outputs |
| C02 Eligible cash/reserves/restrictions | B01/B02 policy and supported manual eligible amount, with operating reserve and restriction scope, avoiding duplicate exclusions | Excluding the named separately restricted populations is defensible under the proposed policy, not proof the rest is excess. No bounded total-eligibility estimate follows from retained material; do not manufacture eligible cash or a zero reserve. | Bridge/per-share only |
| C03 Strategic/venture operating perimeter | B03/B08: identify which returns, infrastructure/service costs (including leases commencing 2029), development funding and contingent effects are in forecast EV; then approve any nonoperating asset proxy and remaining exposure treatment | A named positive-asset addition may be expressly forgone with its limitation disclosed, but carrying value is not a bound on economic value. Omitting 7,448 alone does not dispose of funding/RVG or fix forecast costs. Retained maxima are not economic PVs or a full cash schedule. | EV if operating cash scope unresolved; bridge/per-share for assets/claims |
| C04 Financing coverage beyond named Notes/leases | B04/B05 measurement approvals plus explicit reviewed coverage/treatment for additional borrowing, `E/debt_lease_components/additional_borrowing` null | Carrying lease proxy is a named simplification; it does not bound residual borrowing. Historical omission is unbounded; no evidence-supported bounded residual omission is available here. Keep open or expressly justify a new scoped omission with unbounded limitation. | Bridge/per-share; no missing debt is silently deducted from FCFF |
| C05 Unpaid obligations/settlement overlap | B07: supply reviewed dated claim scope/value where relevant, or explain coverage through future cash PP&E/WC/other payments and ensure each settlement occurs once | Annual supplemental 9,331/2,659 observations cannot bound a fiscal-end claim PV. A named exclusion is defensible only with a supported scope/forecast-payment rationale; absent that, leave open. No second WC deduction for capital creditors already settled in cash PP&E. | EV if future operating payments unresolved; bridge/per-share if separate claims unresolved |
| C06 Classes, existing awards and proceeds | B09/B10: approve starting shares/class economics; separately reconcile pre-anchor award rights versus forecast-expensed future service, one claim/share treatment, relevant proceeds and award-tax effects | No automatic full-RSU addition, award deduction, zero proceeds or omission of all awards. Retained counts/grant-date/unrecognized expense do not resolve current value/service/vesting allocation. An express omission needs its own justification; no bounded award-value omission is established. | Per-share, and equity if an award claim belongs in bridge; EV only if SBC is double charged/omitted |
| C07 Other claims/tax assets and exclusions | B08 plus `L`, `N/4`: reviewed legal/tax/benefit/preferred/NCI and other-asset/claim coverage, relation to forecast payments and any separate cash-benefit valuation | No standalone accounting-DTA addition is defensible without cash-benefit support; a named excluded potential asset is an optional refinement, not zero benefits. Unidentified claims remain potentially unbounded; no net DTA, gross exposure or historical omission establishes a bounded net adjustment. | Bridge/per-share; EV where forecast tax/settlement scope is affected |
| C08 Actual-input scope and execution authority | Record who supplied/reviewed values, date/rationale, retained source/decision references and information scope; resolve required items for the requested output, then obtain a separately bounded execution instruction | No synthetic test result or this preparation sheet substitutes for actual-input acceptance or execution authority. A declared scope cannot authenticate evidence or certify hidden completeness. | All actual execution; authorization remains pending even after numerical inputs arrive |

## Consolidated response and smallest defensible path

Use the existing IDs in one response; **no item is pre-approved**. These are
document references for review, not a new persisted input/approval framework.

| Group | Stable references / requested response |
| --- | --- |
| **A — numerical values** | **A01–A06:** five values each in FY2026–FY2030 order; **A07–A08:** constant WACC/g; **A09–A13:** five explicit terminal ratios. All 37 remain **UNSET**; include units and rationale through C01/C08. |
| **B — proposed actual selections** | **B01–B10:** approve, amend or defer each named treatment, scope/proxy, exclusion and starting share/class basis; candidate amounts remain unselected. No B approval automatically resolves the linked C requirement. |
| **C — unresolved requirements** | **C01–C08:** provide a supported treatment/input or an expressly justified scoped omission and its limitation, or leave open and limit the requested output. Unbounded unknowns stay unbounded; execution authority is a later separate instruction. |

**Recommendation:** first review A01–A13 and C01/C08, with the operating parts of
C03/C05/C07 explicitly covered in the manual forecast. Then a separately
authorized **forecast/EV-only** case could proceed without forcing bridge/share
decisions. WACC/g must still be supplied because the existing Stage A assumption
container requires them, even though only Stage B consumes them. B04/B05 named
measurements, B06 convention-based exclusions and B09 starting shares/class
assumption can be decided now, conditionally and separately from completeness.
Defer equity/per-share until C02–C07 and actual population/share coverage are
resolved or expressly disposed of with justified limitations. Do not fill gaps
with zero, force complete historical NWC, or launch research to make this sheet
appear complete. **No actual run is authorized by this review package.**
