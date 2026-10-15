# AAPL FY2025 — consolidated analyst-input decision package

**One draft for consolidated user review; new judgments are PROPOSED, not
accepted or integrated.** The [machine companion](aapl-analyst-input-package.json)
contains every retained occurrence, context, raw value, sign/scale, precision,
receipt and calculation operand. Original [accepted treatments](../aapl-treatment-acceptance-checklist.md)
remain accepted within their earlier restricted scope. No MSFT assumption or
approval is transferred. Financial sufficiency remains **NOT_ASSESSED**.

## 1. Exact source perimeter and reading key

CIK **320193**, selected non-amended 10-K **0000320193-25-000079**;
annual **2024-09-29–2025-09-27**, duration context `c-1`; closing instant
**2025-09-27**, `c-20`. Only FY2025 is packaged. Comparative columns are source
support, not additional registrations or an approved opening balance/movement.

Both original SEC bodies are in
[the retained manifest](../evidence/analyst-operating-nwc-response-bodies.json):

| Source | Exact artifact / original-body SHA-256 / receipt |
| --- | --- |
| Primary, `/artifacts/9` | [aapl-20250927.htm](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm); `b0dbcbbd800fd1c819007d63d884a1f8b9a5994486d0b2974a4b5b8a6e6eb80e`; 2026-10-11T17:12:47.260610+00:00, HTTP200 |
| Instance, `/artifacts/10` | [aapl-20250927_htm.xml](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_htm.xml); `e1076735f1c81bc96d5c1ff6e1a9d23515d6eacf52b405cb1f7da3e379ac533b`; 2026-10-11T17:12:47.622471+00:00, HTTP200 |

Representation is `sec_response_body_bytes`, digest type
`sha256_sec_response_body_bytes`, not compressed or reserialized bytes. No new
request. Inline IDs below identify the same primary numbers independently of
the instance; JSON records both. **S** source fact/calculation; **A** existing
acceptance; **P** proposed analyst classification; **U** unquantified/unavailable.
Unless specified, amounts are **USD millions**, source decimals **−6**. **R**
means decimals **−8**, rounded hundred-million points. Arithmetic does not
improve precision; labels are origins/review states, not confidence scores.

## 2. Income, D&A, CFO, SBC and taxes

| Population / recommendation | FY2025 | Evidence and status |
| --- | ---: | --- |
| Revenue; retain consolidated direct total | **416,161** | S; income statement p29, `RevenueFromContractWithCustomerExcludingAssessedTax`; ordinals285/599/1210/1302, `f-78` and confirmations. |
| EBIT; retain reported operating income | **133,050** | S; p29 / Note13, `OperatingIncomeLoss`, 309/1233, `f-102`/`f-1044`. No expense reconstruction. |
| CFO historical reference | **111,482** | A; p33 `NetCashProvidedByUsedInOperatingActivities`, 514/`f-307`; consolidated, not organic, unlevered or operating-only. |
| CFO D&A reconciliation add-back | **11,698** | S support; p33 `DepreciationDepletionAndAmortization`, 487/`f-280`. **Not approved expense-basis D&A in this draft.** |
| PP&E depreciation expense | **8,000R** | S support; Note5 p39, `Depreciation`, 866/`f-665`. Missing income-recognized amortization/lease/inventory bridge prevents complete expense-basis D&A. **Do not infer 3,698 amortization by subtraction.** |
| SBC recognized expense / CFO add-back | **12,863 / 12,863** | A expense cost proxy counted once; separate Note11 expense `AllocatedShareBasedCompensationExpense`, 1185/`f-996`, versus reconciliation `ShareBasedCompensation`, 490/`f-283`. Not two costs. |
| Pretax / tax provision / accounting ETR | **132,729 / 20,719 / 15.6100023356…%** | S; p29/Note7, pretax315/`f-108`, provision318/920/948; ETR uses existing positive-denominator provision/pretax rule, full precision in JSON. Not a future operating rate. |
| Net cash income taxes | **43,369** outflow | A; supplemental p33, `IncomeTaxesPaidNet`, 565/`f-358`. Provision difference **22,650** is a historical difference, not a tax allocation. |
| Deferred provision components | **−1,804 −139 +604 = −1,339** | S; Note7 federal/state/foreign, 896/905/914. Not a pure CFO deferred-tax row. CFO mixed Other **−89** remains separate. |

**Recommend retaining the reported income/tax/SBC schedules and restricted CFO
path**, without a new interest proxy, SBC adjustment or tax normalization.
The existing generic normalization/preparation D&A result is not rewritten or
declared erroneous: the narrower **expense/timing** question remains unproved.
Neither the CFO location nor the numerical difference certifies that question.

The ten independently displayed CFO contributions reproduce the reported subtotal:

`112,010 +11,698 +12,863 −89 −6,682 −347 +1,400 −9,197 +902 −11,076 =111,482`.

JSON retains raw asset-change signs and −1 display multipliers; liabilities have
their reported contribution signs. Vendor nontrade and mixed current/noncurrent
rows remain distinct. This is statement reproduction, not a residual-defined
proof or permission to add these items again to CFO. Reported cash movements do
not establish book ΔNWC, organic comparability or a capital/tax allocation.
The Ireland tax disclosures do not establish a full recurring cash-tax bridge.

## 3. Operating capital — concrete proposed perimeter

| Closing population | USDm | Treatment / exact evidence |
| --- | ---: | --- |
| Customer receivables | +39,777 | S operating; balance sheet `AccountsReceivableNetCurrent`, 370/`f-163`. |
| Vendor nontrade receivables | +33,180 | S supply-chain asset; 372/`f-165`, Note4 p39 says component sales to manufacturing vendors; gains reduce product costs. Recommend include, **not MSFT's investing-facilitation treatment**. |
| Inventory | +5,718 | S book FIFO inventory; 374/`f-167`; no cash/expense timing bridge. |
| Whole AP | −69,860 | S reported caption, 390/`f-183`. Operating-only portion not isolated; do not supply a capital-creditor correction. |
| Current deferred revenue | −9,055 | S current customer funding, 394/`f-187`; not total current/noncurrent advances. |
| **Original current-only partial NWC** | **−240** | Original [reviewed scenario](aapl-analyst-nwc-bundle.json), unchanged; excludes known distribution and unknown components explicitly. |
| Distribution and marketing accrual | **−8,919** | Note6 p40, Apple extension `AccruedDistributionAndMarketingCurrent`, 880/`f-679`, c-20. Recommend **include** this identified ordinary operating cost accrual. |
| **Proposed expanded partial current operating capital** | **−9,159** | P: original −240 less known8,919. Source-supported arithmetic, proposed inclusion; **not complete current NWC**. |

This resolves the known omission for the **new proposed** schedule, not the
original blocker. Unknown employee accrual **E** and investing-in-AP amount **K**
remain unavailable: an adjusted level would be `−9,159 − E + K` before other
omitted balances. Neither is assigned zero, an estimate, a materiality threshold
or a bound. No approved opening schedule: **no adjacent book movement or cash
ΔNWC** is populated.

Retained mixed populations and overlaps (all c-20, decimals−6): OCA **14,585**
(`f-169`); other noncurrent assets **83,727** = located DTA **20,777** + remaining
**62,950** (`f-177`/`f-670`/`f-672`); OCL **66,387** = taxes **13,016** +
distribution **8,919** + remaining **44,452** (`f-185`/`f-677`/`f-679`/`f-681`).
The remaining current parent includes operating/finance lease liabilities
**1,579 /538**; its remainder **42,335** is **not employee accrual**. Noncurrent
liabilities **41,549** include leases **10,911 /692**; **29,946** is still mixed,
not an operating liability allocation. ROU asset11,205 overlaps other NC assets.

**Recommend leave these residual captions unallocated support, not add a whole-
caption operating estimate.** Taxes and funding/lease populations must not be
double-counted as operating accruals. Unknown allocations may be material.
Alternative original −240 omits8,919; alternative excluding vendor receivables
from the expanded schedule gives **−42,339**, **−33,180** versus recommendation.
The supply-chain note makes the latter less appropriate. CFO already packages
reported movements without solving these closing-book allocations; that avoids
reconstruction for the reported-reference path only, not its economic limitations.

## 4. Investment, leases, financial balances and claims

| Source-supported input / proposed handling | USDm | Evidence / limitation |
| --- | ---: | --- |
| Cash PP&E / investing Other | **−12,715 / −1,480** | A narrow PP&E, S mixed Other; p33 526/`f-319`,529/`f-322`. Other is not proven acquisition/intangible-only or gross reinvestment. No combined reinvestment subtotal. |
| Noncash ROU additions | **2,800R** | S combined operating/finance; Note8 1026/`f-825`, Apple extension. No invented class allocation or cash Capex inclusion. Capital creditors/noncash PP&E bridge unavailable. |
| Fixed operating cost / fixed operating cash | **2,100R /2,100R** | Expense versus A restricted cash dataset; Note8 1017/1023. Equal points do not establish identical coverage; fixed cash already embedded in CFO. |
| Variable lease cost | **16,100R** | Note8 1020/`f-819`; expense based primarily on output purchases, **not cash paid**. Cannot create total lease cash by summing it with fixed cash. |
| Operating ROU / finance ROU assets | **11,205 /1,033** | Note8 1030/1032; other NC assets versus PP&E. No AAPL finance-amortization inclusion assumption or guessed expense add-back. |
| Operating lease liability | **1,579 +10,911 =12,490** | Note8 current/noncurrent; maturities14,725 less future imputed interest2,235 also tie. Those maturities are not annual cash. |
| Finance lease liability | **538 +692 =1,230** | Note8 current/noncurrent; future payments1,579 less imputed349 tie. Annual finance interest/principal cash and expense splits unavailable. |
| Cash / current / noncurrent marketable securities | **35,934 /18,763 /77,723** | Balance sheet/Note3; ord366/368/380 and725/726/727, `f-159`/`f-161`/`f-173` and confirmations. |
| Named current financial balances / all reported cash+securities | **54,697 /132,420** | S disjoint named partitions; latter agrees with Note3 Apple parent724/`f-521`. Recommend current pool for narrow liquidity, LT separate financial investments. Neither is unrestricted/excess cash. Strategic/restricted and reserve coverage remains unproved. |
| Term debt principal → net carrying | **91,281 −309 −294 =90,678** | Note9 p44: discount/issuance/premium and hedge deductions; 1123/1125/1127/1129. Concept `DebtInstrumentCarryingAmount` tags the **principal caption**, not the net total. |
| Current / noncurrent term debt / CP | **12,350 /78,328 /7,979** | Net carrying; balance sheet/Note9. CP is separately reported, not an inferred zero. Note9 rounded8,000 is not another borrowing to add. |
| Named CP+term / proposed plus finance leases | **98,657 /99,887** | Proposed financing inclusion of1,230, not complete debt. No cash/debt netting or enterprise-to-equity calculation. |
| Debt fair value | **80,400R** | Note9 Level2, 1143/`f-954`, c-74. Carrying/fair difference10,278 is a measurement comparison, not an economic gain or extra claim. |
| Tax-credit DTA / unrecognized tax benefits | **8,643 /23,242** | Note7: gross credit DTA is not pure NOL or equity value. Exact roll-forward1010/`f-809` versus rounded narrative23,200R987/`f-786` retained as distinct precision alternatives. Neither is automatically incremental borrowing/cash. |
| Future purchase commitments / uncommenced operating leases | **13,308 /523** | Note12 1201/`f-1012` (commitments with remaining term over one year); Note8 1079/`f-890`, explicitly dimensioned uncommenced operating leases. Not recognized funded debt, current cash or a proved disjoint aggregate; no sum. |

**Recommended AAPL-specific classification (P):** operating/variable lease costs
remain operating, finance ROU/liabilities remain asset financing, based on Note8
locations. Keep the accepted restricted cash dataset unchanged. Unlike MSFT,
**no assumption establishes a complete expense D&A or finance-amortization
overlap here**. An all-lease financing obligation alternative is **112,377**,
**+12,490** versus proposed99,887; choosing it would require consistent future
expense/debt/investment treatment, not a liability-only valuation adjustment.
An all-lease cash-service alternative cannot be quantified without finance cash
and variable cash evidence. No financing cash total is constructed.

Recommend preserve tax contingencies/commitments separately, not add gross tax
benefits to debt or tax-credit DTA to cash/equity. Pension, preferred/NCI and
strategic claims are **not separately established as an exhaustive population**,
not zero/immaterial. Stop on the stated bounds; no automatic research queue.
Note12 identifies supplier, licensed-IP/content and distribution-right purchase
commitments: recommend a separate future-commitment disclosure, not current
operating capital or a financial borrowing. Operating versus capital allocations
remain unquantified. Management's no-reasonably-possible-material-loss assessment
is an issuer judgment, not proof of zero legal accrual/exposure or a probability
estimate supplied by this package.

## 5. Dated common shares and disclosed awards

| Observation | Amount / precision | Evidence and recommended handling |
| --- | --- | --- |
| Fiscal-end common | **14,773,260,000 shares**, decimals−3, 2025-09-27 | Balance sheet417/`f-210`, c-20. Proposed historical snapshot, not exact-unit precision or diluted shares. |
| Cover common | **14,776,353,000 shares**, decimals−3, **2025-10-17** | Cover262/`f-51`, c-11; keep separate. +3,093,000 is a later-date difference, not forecast dilution or a reconciliation defect. |
| Nonvested RSUs | **151,574,000 shares**, decimals−3, 2025-09-27 | Note11 1174/`f-985`, c-146, explicit RSU award class. Not incremental dilution or an added share total. |
| Unrecognized RSU compensation | **21,800R USDm** | Note11 1191/`f-1002`, same class/date. Future expense disclosure, not award market value or another current SBC charge. |

Annual weighted-average diluted shares **15,004,697,000** (EPS330/333 and616/622)
are a different **duration** population, not closing shares. No award valuation,
forecast dilution or EPS/per-share calculation. Such future choices are not
prerequisites for preparing these named historical observations.

## 6. One consolidated approval sheet

All new rows below remain **P**. Existing AAPL accepted CFO/cash PP&E/SBC proxy/
cash-tax/restricted fixed-lease data remain **A**, not reopened for approval.

| Decision / recommendation | Alternative and numerical consequence | What this solves / boundary |
| --- | --- | --- |
| Include known distribution accrual: partial capital **−9,159** | Original **−240** omits8,919; excluding vendor gives **−42,339** | Corrects a named omission only. Employee/capital-creditor and mixed residuals remain unknown; no cash ΔNWC. |
| Operating service / finance asset financing, using AAPL Note8 | Named financing **99,887** vs all-lease **112,377**, +12,490; all-cash-service amount unavailable | Coherent historical locations without fabricated expense/cash bridge. D&A11,698 is CFO support; complete expense D&A unavailable. |
| Separate investment columns | Other1,480 remains visible; noncash2,800R not cash | Keeps approved PP&E12,715 narrow. No organic/acquisition allocation or full reinvestment. |
| Current financial pool **54,697**; LT **77,723** separately | Broader reported pool132,420, +77,723; not a cash availability estimate | Named financial populations and borrowing measurements traceable, not unrestricted/excess cash or complete claims. |
| Retain accepted SBC once and historical tax roles | Cash43,369 vs provision20,719, difference22,650; no rate/proxy selected | No duplicate cost or tax charge; operating-tax/interest allocation unavailable, not a historical rate assumption. |
| Fiscal-end common snapshot; dated cover and RSUs separate | Cover +3,093,000 later-date shares; no RSU sum | Preserves dates/classes/precision; not diluted or valuation shares. |

## 7. Validation, preservation and stopping point

[Offline reporting helper](../../scripts/prepare_aapl_analyst_package.py) reuses
existing primary/instance identity, context, units, precision, confirming-occurrence
and arithmetic infrastructure. It does not call MSFT's financial selection logic.
Twelve recorded arithmetic/independent-parent checks include both lease
partitions/maturity bridges, term-debt bridge, financial parent, income/tax and
the complete displayed CFO. Source matching alone does not establish scope.
The normalization skill informed the source/decision separation and QA limits;
the explicitly requested Markdown/JSON format is retained.

Validation: **12 new focused tests (4.788s)** plus **44 relevant preservation
tests** pass (AAPL reported15 in2.563s, AAPL partial-NWC8 in2.248s, accepted
MSFT21 in7.947s). Tests pin literal statement values/ordinals, all confirmations,
source roles/precision, null requirements, proposed alternatives, conflicts,
date/dimension/unit/nil mismatches, exact replay and JSON round trips. All prior
tracked JSON/runtime files and the MSFT helper are byte-equal to starting HEAD;
AAPL and accepted MSFT package replay, compileall, **429 affected local links**
and `git diff --check` pass. No full-suite/corpus rerun or SEC requests.
Original receipts, registries, partial scenarios, frozen policies/
outputs, pilot bytes and the accepted MSFT package/view remain unchanged.
**Stop for one consolidated user review.** No acceptance, runtime integration,
support reclassification, Phase 1 closure, Phase 2 calculation or research chain.
