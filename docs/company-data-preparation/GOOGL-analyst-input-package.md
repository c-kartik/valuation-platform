# Alphabet FY2024 — consolidated analyst-input decision package

**One review package; new judgments are proposed, not accepted or integrated.**
[Machine companion](googl-analyst-input-package.json) records exact source facts,
all confirmations, alternatives, formula operands, signs, units, precision and
unknowns. GOOG/GOOGL are one issuer. Existing [accepted treatments](../googl-treatment-acceptance-checklist.md)
remain accepted only for their stated historical-preparation scope. No AAPL/MSFT
financial assumption is transferred. Financial sufficiency **NOT_ASSESSED**.

## 1. Exact filing, evidence and reading key

CIK **1652044**, selected non-amended 10-K **0001652044-25-000014**;
annual **2024-01-01–2024-12-31**, context `c-1`; closing instant **2024-12-31**,
`c-9`. Comparative columns are support, not additional registered inputs or an
approved opening schedule. All figures **USD millions** unless shares. Main
monetary facts have decimals **−6**; **R** means **−8** (rounded100m points).
Source `INF` is retained where supplied; it does not confer unlimited economic
accuracy on a displayed rounded/billion-dollar point. Arithmetic never improves
source precision. **A** existing scope-specific approval; **S** source fact or
supported calculation; **P** proposed classification; **U** unavailable amount.

| Retained source | Original response-body binding / actual metadata |
| --- | --- |
| [Primary statement/notes](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm) | [Original manifest](../evidence/analyst-operating-nwc-response-bodies.json), `/artifacts/30`; SHA256 `88bba3d95ca801192f0c9bf10e4b9baefc56d4567d24156b809a28fb8424746f`; 2,528,455bytes; 2026-10-11T17:12:59.460685+00:00, HTTP200. |
| [Selected extracted instance](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231_htm.xml) | [Explicit refreshed receipt](../evidence/googl-fy2024-instance-provenance-refresh.json), `/artifacts/0`; SHA256 `3847c7f5416ff6055de7bb2370934f9d6f3cafec50c310631ef9f96bd8d764a3`; 2,703,015bytes; **2026-10-11T21:10:46.050735+00:00**, HTTP200. |

Representation `sec_response_body_bytes`, digest type
`sha256_sec_response_body_bytes`. Refresh bytes are identical to retained original
instance; original timestamp/status are **still null**, not recovered. JSON
preserves that history and uses only the explicit fresh receipt. No new request.
Taxonomies are `http://fasb.org/us-gaap/2024`,
`http://www.google.com/20241231`, and DEI2024. JSON source IDs `FY2024-primary`
and `FY2024-instance` join every fact/inline ID to those exact bodies.

## 2. Income, D&A, CFO, SBC and taxes

| Named input / recommended treatment | FY2024 | Exact evidence / status |
| --- | ---: | --- |
| Revenue / EBIT | **350,018 /112,390** | S consolidated totals; income statement/Note15; `RevenueFromContractWithCustomerExcludingAssessedTax`541 and confirmations; `OperatingIncomeLoss`559/2015. No expense-derived fallback. |
| Reported CFO | **125,299** | A consolidated reference, not organic/unlevered cash; cash-flow statement p56,731/`f-347`. |
| PP&E depreciation CFO add-back | **15,311** | S reconciliation `Depreciation`,695/`f-311`; **not complete expense D&A**. |
| Finance ROU amortization | **413** | S Note4 cost observation1286/`f-917`; not an extra CFO add-back. **No sum with15,311, subtraction-based amortization or finance-inclusion assumption.** |
| SBC expense proxy / CFO add-back | **22,800R /22,785** | A rounded expense counted once; Note13 `AllocatedShareBasedCompensationExpense`1821/`f-1466`; separate `ShareBasedCompensation`698/`f-314`. No15m rounding adjustment, substitution or duplicate cost. |
| Pretax / provision / historical accounting ETR | **119,815 /19,697 /16.4395109127…%** | S income statement/Note14;565/1859,568/1881. Existing positive-denominator provision/pretax rule, not future operating tax. Note14's displayed16.4% retains rounded presentation, not a competing economic rate. |
| Cash income taxes net | **27,400R** payment | A Note14 `IncomeTaxesPaidNet`,1954/`f-1599`; cash/provision difference7,703 uses a rounded cash point and supplies no recurring allocation. |
| Deferred provision / CFO deferred reconciliation | **−5,256 /−5,257** | Separate Note14 provision1878 and CFO `DeferredIncomeTaxesAndTaxCredits`701. No1m plug or automatic equivalence. |
| Interest expense / capitalized interest | **268 /194** | S accrued expense populations,1556/1580; **borrowing cash interest unavailable**, no expense-to-cash proxy or lease overlap certification. |

**Recommend retain these reported roles and accepted cost proxy; leave complete
expense-basis D&A null.** The CFO row and finance expense do not establish complete
income-recognized amortization, inventory timing or non-overlap. Mixed CFO Other
is not residual amortization. Original frozen D&A gaps and timing gates remain.

Thirteen independently displayed CFO contributions reproduce the reported total:

`100,118 +15,311 +22,785 −5,257 −2,671 +3,419 −5,891 −2,418 −1,397 +359 −1,161 +1,059 +1,043 =125,299`.

Raw source values/multipliers are retained, including investment gains and mixed
noncash signs. Working-capital cash rows are reported **net of acquisition effects**;
that does not make all CFO organic or remove FX/reclassification/timing questions.
No partial book movement is deducted from CFO or depreciation/SBC added again.

## 3. Partial operating capital — concrete recommendation

| Closing component | USDm / sign | Evidence and perimeter |
| --- | ---: | --- |
| Net AR | +52,340 | S450/`f-66`, c-9. |
| Whole AP | −7,987 | S470/`f-86`; supplier/operating-only completeness unproved. |
| Reviewed rounded PP&E-in-AP adjustment | **+3,200R** | Existing **manual-note reading**, not estimated allocation or exact instant XBRL fact. `CapitalExpendituresIncurredButNotYetPaid`1459/`f-1104`, **annual c-1**, raw3,200m/decimals−8. Note7 explicitly establishes closing scope. |
| Current deferred revenue | −5,036 | S478/`f-94`; not backlog/noncurrent customer advances. |
| Accrued compensation / revenue share | −15,069 /−9,802 | S472/476, separate employee and partner populations; not SBC expense. |
| Accrued customer liabilities | −4,304 | S Google extension1448/`f-1091`, subset of accrued parent. |
| **Recommended rounded partial current operating capital** | **13,342R** | P: source-supported arithmetic with existing manual reading. Inventory/other assets omitted explicitly; **not complete current NWC**. |
| Whole-AP alternative, no correction | **10,142** | Difference−3,200 from recommended point; contains known capital obligation. Less preferred, not a source-pure operating AP measure. |

The [unchanged original partial bundle](googl-analyst-nwc-bundle.json), SHA256
`a8a45520d79bdedbdeeae398c1ea16cbe3639e43fed4300998b109176e4aafdb`,
supplies the exact rounded manual note, assumptions, author/review date, source
ordinal and closing interpretation. No invented instant context, new estimate,
unrounded value or uncertainty interval. The remaining AP point **4,787R** is
not certified operating-only. Separate accrued PP&E **7,104** (Note7 1446) sits
inside accrued expenses/other current liabilities, **not AP**: do not add it to
the3,200 correction or subtract it again from this partial perimeter.

**Inventory remains U, not zero.** The filing discusses device inventory costs,
but retained evidence does not isolate a complete closing amount for this
perimeter. Other current assets15,714 contain mixed investment/collateral and
possible operating balances; no inventory-by-residual or whole-caption proxy.
Accrued parent51,228 overlaps customer4,304, capital creditors7,104, taxes2,905,
EC fines6,322, current operating lease2,887, and other financing. Do not subtract
the parent alongside the selected child. Current term debt999 and finance lease235
are also inside that mixed parent; neither is an operating employee accrual.
Noncurrent assets/liabilities remain outside this narrow schedule, not irrelevant.

Recommend keep this traceable **partial** schedule and explicit omissions, with
reported cash movements as separate evidence. No approved opening bundle, book
movement or cash ΔNWC. An alternative treating EC fines as ordinary operating
accrual would reduce this point by6,322 to7,020R; recommend instead a separately
identified regulatory claim because Note7 distinguishes fines, FX and interest,
not a recurring supplier/employee accrual. No later bridge adjustment authorized.
Unquantified inventory/supplier/other allocations could be material: stop with
these limits, not a zero or automatic research cycle.

## 4. Investment and independently reviewed lease approach

| Population | USDm | Recommended handling / evidence |
| --- | ---: | --- |
| Cash PP&E | **−52,535** | A narrow purchases;734/`f-350`. No full reinvestment claim. |
| Combined acquisitions/intangible/other assets / investing Other | **−2,931 /−2,667** | Separate source captions749/752; preserve combined scope. Note8 Character cash2,700R, canceled instruments and asset recognition are not a complete bridge; do not subtract to invent the residual allocation. |
| Accrued PP&E / additional PP&E in AP | **7,104 /3,200R** | Distinct creditors, not another cash outflow or complete accrual-investment bridge. |
| Noncash operating / finance ROU additions | **2,510 /313** | Note4 1341/1344; separate noncash financing/service-asset observations, not cash PP&E/principal. |
| Operating cost / variable cost | **3,304 /1,425** | Note4 expense, not separate cash totals. Operating cash3,425 remains the accepted restricted payment observation already in CFO. |
| Finance ROU amortization / interest expense | **413 /31** | Note4 costs, not another economic charge or complete D&A. Net finance ROU asset2,585 =gross4,622−accumulated2,037; stock is not annual expense. |
| Finance interest cash / principal cash | **31 /405** | A separate restricted classes; interest already CFO, **principal already within debt repayments12,701**, not another payment. |
| Operating / finance recognized liabilities | **14,578 /1,677** | Note4 discounted totals; operating2,887+11,691; finance235+1,442. Future maturities17,038−imputed2,460 and1,888−211 reproduce totals, not annual cash. |

**Propose operating leases as service costs and finance leases as asset financing**
from Alphabet Note1/4: finance assets in PP&E, finance liabilities in mixed accrued/
other long-term liabilities, not the term-debt caption. This is a **new P choice**,
not approval implied by the restricted cash dataset. Preserve reported EBIT and
all source observations; no D&A inclusion assumption, income conversion or cash
adjustment. An all-lease financing alternative adds operating liabilities14,578
to the named financing subtotal below; economic treatment would need consistency
before any future consumption. A complete cash-service alternative cannot be
quantified because variable/nonlease cash and borrowing-interest overlap remain
unknown. No 12,701+405 repayment sum, all-interest or complete lease cash total.

## 5. Financial balances, borrowing and other claims

| Named population | USDm | Recommendation / boundary |
| --- | ---: | --- |
| Cash / current marketable / reported current parent | **23,466 /72,191 /95,657** | Balance sheet444/446/448; propose named current financial balances, **not unrestricted/excess cash**. Combined cash/restricted source23466 does not prove standalone restrictions zero or operating reserve. |
| Long marketable securities | **266** | Note3 1018/`f-639`: explicitly **long-term lock-up restricted**, in other NC assets. Keep outside current pool, separately. |
| Nonmarketable parent / equity-method | **37,982 /2,000R** | Balance sheet456 /Note3 1142; overlapping scopes, not extra cash. Equity fair-value population5,079 likewise overlaps financial captions. |
| Nonmarketable equity measurement alternatives | **35,500R /35,531** | Same QName at1019/1109 with different precision. Preserve competing candidates and actual inline displays; do not silently select, sum or create31m adjustment. |
| Term face / signed discount / net carrying | **12,000 −118 =11,882** | Note6 1402/1404/1418; current999+noncurrent10,883 corroborate partition. Fair9,000R is a different measurement; no2,882 gain/claim. |
| CP / named term+CP / proposed plus finance leases | **2,300 /14,182 /15,859** | CP is disclosed; source `INF`/2.3bn display retained. Finance1,677 is separately located, not already within Note6 net term. **Named subtotal only, not complete economic debt.** |
| All-lease alternative | **30,437** | Adds operating14,578 to15,859; proposed obligation scope, not debt certification or an EV-equity calculation. |
| NCI / redeemable NCI | **4,200R /1,100R** | Note5 explicitly **“of which”**: redeemable is a **subset**, not an extra1,100. Recommend retain total recorded NCI as separate ownership-claim observation, not financial borrowing or fair value. |
| Unconsolidated VIE funding commitments | **1,500R** | Note5 future commitments, not recorded funded debt; no sum with NCI or guaranteed cash investment estimate. |
| EC fines / gross loss DTA | **6,322 /3,472** | Note7 fines include FX/interest and are already accrued; separate regulatory claim, no double count. Note14 gross NOL DTA is before shared valuation allowance, not realizable equity value. |
| Uncertain tax benefits | **12,619 /12,600R** | Note14 exact roll-forward1973 versus rounded narrative1976; preserve candidates. Not automatically incremental debt/cash or a duplicated tax charge. |
| Preferred stock value | **0 expressly reported** | Balance sheet502; this is source zero only for the named preferred caption, not inference that other claims are zero. |

No cash/debt netting or equity-bridge calculation. Actual restrictions and reserves,
other nonmarketable allocations, claim fair values and exhaustive claim coverage
remain unresolved. Recommend retaining recorded captions and known parent/subset
relationships rather than guessed liquid/strategic/NCI aggregates.

## 6. Dated shares and awards — no automatic aggregation

| Population | Shares | Evidence / precision |
| --- | ---: | --- |
| Year-end Class A / B / C | **5,835,000,000 /861,000,000 /5,515,000,000** | 2024-12-31,523/526/527; decimals−3, exact stock-class dimensions retained. |
| Later cover Class A / B / C | **5,833,000,000 /860,000,000 /5,497,000,000** | **2025-01-28**,421/422/423; sourceINF with displayed million units. No forced year-end date or automatic class sum. |
| Independently reported year-end issuer common observation | **12,211,000,000** | Balance sheet522, decimals−3; source aggregate only, not newly derived class equivalence or diluted total. |
| Unvested RSUs | **299,000,000** | Note13 1840/`f-1485`, c-307, RSU dimension, sourceINF/million display. Note says eventual issuance ClassC; no fabricated stock-class axis or added share total. |
| Unrecognized RSU expense | **34,800R USDm** | Note13 1847/`f-1492`; future expense disclosure, not award value or extra current SBC cost. |
| Annual basic / diluted EPS denominators | **12,319,000,000 /12,447,000,000** | Note12 duration observations, decimals−6; not point-in-time or forecast shares. |

Recommend retain class/date populations individually and the source aggregate only
as an observation; no ClassA/B/C equivalence, voting-value assumption, RSU valuation,
class/award sum or dilution estimate. Future valuation choices are not prerequisites
for preparing these named historical observations.

## 7. One consolidated approval sheet — all new decisions remain P

| Decision / recommendation | Alternative and quantified effect | Remaining boundary |
| --- | --- | --- |
| Partial current operating capital **13,342R**, including reviewed manual correction | WholeAP10,142, difference−3,200; ordinary-fines alternative7,020R, difference−6,322 | No zero inventory, pure supplier AP, complete capital or book/cash movement. Preserve original note precision and scenario. |
| Operating service / finance asset financing | Named financing15,859 versus all-lease30,437, +14,578 | No D&A completeness/inclusion assumption or whole-service conversion; finance principal405 already within repayments. |
| Separate investment columns | Broader purchases include combined2,931 but no acquisition/organic allocation | Capital creditors and noncash additions are not extra cash; no reinvestment sum. |
| Current financial95,657; locked266/strategic holdings separate | Marketable/nonmarketable precision candidates retained; no31m adjustment | Not unrestricted/excess cash or exhaustive liquid assets; NCI4,200 includes1,100, not5,300. |
| Retain accepted SBC22,800R once, add-back22,785 separate; historical tax roles | No15m SBC or1m deferred-tax plug, future rate or interest proxy | Original acceptances unchanged; cash/provision/deferred scopes and precision remain. |
| Dated class shares, source aggregate and awards separately | Later cover dates are observations, not a dilution bridge | No automatic class/award aggregation, forecast dilution or valuation claims. |

## 8. Validation and stopping point

[Offline helper](../../scripts/prepare_googl_analyst_package.py) reuses existing
inspection, identity, receipt, inline/instance and arithmetic tools only. The
normalization skill informed role/precision/source separation and visible QA,
not valuation readiness; requested Markdown/JSON format is retained. Twelve
recorded arithmetic/source ties include CFO, income/tax, financial and lease
partitions, term basis and original rounded scenario. Arithmetic matching alone
is not evidence of completeness or economic equivalence.

Validation: **13 focused tests (5.319s)** and **57 relevant preservation tests**
pass: Alphabet reported10 in3.209s, partial-NWC9 in6.111s, accepted AAPL17 in5.403s,
accepted MSFT21 in7.479s. Tests bind literal retained facts, manual closing reading,
precision alternatives, source signs/roles, receipt history, class dates, overlaps,
nulls, malformed evidence rejection and deterministic round trips. All three
package replays, twelve recorded arithmetic/source ties, original JSON/runtime/
prior-helper byte preservation, compileall, **444 affected local links** and diff
checks pass. No full-suite/corpus rerun or SEC requests.
All original bundles/scenarios, metadata gaps/refresh,
policies/frozen outputs, pilot bytes and accepted AAPL/MSFT views remain unchanged.
**Stop for one consolidated user review.** No new acceptance, runtime integration,
SEC request, automatic research queue, financial-sufficiency certification, Phase 1
closure or Phase 2 calculation.
