# AAPL FY2025 alternative historical cash-flow input review

2026-10-12; documentation-only Phase 1. Starting HEAD
`3c1804d89dca18b9c7a32fa9898a953c554ef2e2`. No bundle implementation,
economic adjustment or automatic approval. MSFT choices are not AAPL choices.

## Frozen identity and retained evidence

CIK `0000320193`, selected non-amended 10-K **0000320193-25-000079**;
authoritative annual period **2024-09-29–2025-09-27**, context `c-1`, no
dimensions. Numeric observations below use `usd` (ISO USD), non-nil. All concepts
use `http://fasb.org/us-gaap/2025` unless marked **a:**, which means
`http://www.apple.com/20250927`. Ordinals are zero-based XML root-child positions.

Original SEC response bytes retained in the [manifest](evidence/analyst-operating-nwc-response-bodies.json):

| Artifact | Exact URL | SHA-256 of original response body |
| --- | --- | --- |
| Selected statement and notes | https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm | `b0dbcbbd800fd1c819007d63d884a1f8b9a5994486d0b2974a4b5b8a6e6eb80e` |
| Selected extracted instance | https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_htm.xml | `e1076735f1c81bc96d5c1ff6e1a9d23515d6eacf52b405cb1f7da3e379ac533b` |

Representation `sec_response_body_bytes`, digest type
`sha256_sec_response_body_bytes`; both retrieved 2026-10-11, HTTP 200. Verify
decompressed retained bodies, not gzip or reserialized XML. No fresh retrieval.
Face cash-flow statement is printed page 33; Note 1 scope/policies, Note 7
taxes, Note 8 leases, Note 9 debt and Note 11 SBC provide cross-checks.

AAPL's frozen v1 history contains five selected periods. **This review covers
only the FY2025 selected filing and no second approved input bundle.** Its
FY2024 comparative is context `c-18`, 2023-10-01–2024-09-28; FY2023 is `c-19`,
2022-09-25–2023-09-30 (53 weeks). These are observations submitted in the 2025
accession, not replacements for earlier selected accessions, registered scenarios
or proof of comparability. Note 1 warns that certain prior note amounts were
reclassified. The [existing partial NWC bundle](company-data-preparation/aapl-analyst-nwc-bundle.json)
remains one reviewed level, not ΔNWC.

## Exact input and reconciliation matrix

Amounts are **USD millions**; numeric facts have `decimals=-6` unless specified.
Cash-flow signs below are displayed statement signs, not necessarily raw XBRL
signs. Reconciliation items are not extra cash inputs or cash-based NWC components.

| Exact concept / source role | FY2025 displayed amount | Occurrence(s) | Scope / restriction |
| --- | ---: | --- | --- |
| `NetIncomeLoss` | +112,010 | 321, 336, **484** | Accrual income; 484 is cash-flow opening amount; confirming other statements count once |
| `DepreciationDepletionAndAmortization` | +11,698 | 487 | Noncash reported reconciliation add-back, not a second addition to CFO or timing certification |
| `ShareBasedCompensation` | +12,863 | 490 | Noncash CFO reconciliation; separate recognized expense `AllocatedShareBasedCompensationExpense` 1185 confirms 12,863, Note 11 |
| `OtherNoncashIncomeExpense` | −89 | 493 | Raw +89; displayed subtraction. Mixed noncash reconciliation, no unsupported allocation |
| `IncreaseDecreaseInAccountsReceivable` | −6,682 | 496 | Raw +6,682; reported operating change |
| `IncreaseDecreaseInOtherReceivables` | −347 | 499 | Raw +347; vendor non-trade caption; not generic customer AR |
| `IncreaseDecreaseInInventories` | +1,400 | 502 | Raw −1,400; cash-flow sign opposite asset change |
| `IncreaseDecreaseInOtherOperatingAssets` | −9,197 | 505 | Raw +9,197; current and noncurrent assets, unallocated |
| `IncreaseDecreaseInAccountsPayable` | +902 | 508 | Reported cash-flow change, not proof of operating-only closing AP |
| `IncreaseDecreaseInOtherOperatingLiabilities` | −11,076 | 511 | Current/noncurrent mixed liabilities; tax/employee/distribution allocations unproved |
| `NetCashProvidedByUsedInOperatingActivities` | +111,482 | 514 | Complete **reported consolidated subtotal**, not organic/unlevered/adjusted operating-only cash |
| `PaymentsToAcquirePropertyPlantAndEquipment` | −12,715 | 526 | Raw +12,715 investing payment; separate narrow cash PP&E, not complete reinvestment |
| `PaymentsForProceedsFromOtherInvestingActivities` | −1,480 | 529 | Raw +1,480, investing “Other”; no approved acquisition/intangible breakdown or gross-purchase completeness |
| `IncomeTaxesPaidNet` | −43,369 | 565 | Supplemental cash payment; reported net tax, not rate or operating-only tax |
| `IncomeTaxExpenseBenefit` | +20,719 | 318 | Accrued tax provision, not cash; Note 7 tax table 892 and rate reconciliation 926 |
| Cash interest | **Unavailable** | No separate cash-interest fact/caption found | Note 9 debt 1082 gives terms, rates and principal; none supplies annual cash paid. No expense/rate × debt proxy approved |
| `OperatingLeasePayments` | 2,100 payment magnitude | 1023; **−8** | Note 8 fixed operating-lease cash only; no separately displayed lease row on face CFO |
| `OperatingLeaseCost` / `VariableLeaseCost` | 2,100 / 16,100 expense | 1017 / 1020; **−8** | Fixed operating cost and variable lease cost, not proof of equivalent cash payments |
| **a:**`RightofUseAssetsObtainedinExchangeforOperatingandFinanceLeaseLiabilities` | 2,800 addition | 1026; **−8** | Noncash combined ROU additions; not cash PP&E, interest or principal |
| `PaymentsRelatedToTaxWithholdingForShareBasedCompensation` | −5,960 | 535 | Financing payment; not corporate cash income tax or additional SBC expense |

All listed amounts have the exact annual context above. Raw integer USD values
are the displayed million-dollar magnitudes × 1,000,000, with the noted raw sign
differences. `decimals=-8` means hundred-million-dollar reporting precision;
rounded points are not exact economic quantities. No invented rounding interval.

**Reported CFO reproduction only:**
112,010 + 11,698 + 12,863 − 89 − 6,682 − 347 + 1,400 − 9,197 + 902 − 11,076
= **111,482**. This is an independent statement check, not an adjusted subtotal
or permission to construct FCFF. FY2024/FY2023 comparative CFO **118,254 / 110,543**
(515/516), PP&E **9,447 / 10,959** (527/528), cash taxes **26,102 / 18,679**
(566/567) and SBC **11,688 / 10,833** (491/492) are source reference only.
Their complete reported CFO reconciliation also reproduces, with displayed
asset-change/noncash signs—not an approved comparative scenario.

## Scope findings, proposed choices and remaining requirements

**Available reported-data path:** preserve consolidated CFO and each supported
cash/reconciliation input separately, with occurrence, sign, precision and
source binding. This is proposed historical preparation, not automatic acceptance
of MSFT's SBC cost proxy, lease convention or economic treatment for AAPL.

- **NWC:** reproducing reported CFO does not require extracting employee cash
  accruals, deciding the omitted 8,919m distribution balance or removing PP&E
  creditors from closing AP. CFO already incorporates reported operating changes.
  Do not subtract partial ΔNWC or add D&A/SBC again. This avoids reconstruction
  requirements for this narrow use only; mixed current/noncurrent changes do
  not prove complete book NWC or cash comparability. Preserve all frozen blockers.
- **SBC:** expense/add-back facts agree; future cost proxy versus another
  treatment is an AAPL analyst choice still requiring review. Note 11 shows
  outstanding awards separately. Its rounded employee-tax remittance 6,100m
  (1181, dimensioned context `c-145`, −8) differs from face financing 5,960m;
  do not collapse or sum them. No complete scope bridge is established.
- **Leases:** Note 1 policy text 581 combines lease/nonlease components for
  corporate/retail facilities. Note 8 text blocks 1014/1015 confirm fixed cash,
  variable cost and noncash additions. Variable cost 16,100m is material disclosed
  exposure, **not cash**. Finance ROU assets/liabilities are reported in stocks
  and maturities, but no isolated eligible annual finance principal/interest cash
  or all-variable cash bridge is found. Do not import MSFT's three-input convention,
  assume absent payments zero, infer cash from balances or allocate imputed
  future maturity interest to this year. Future service/financing choice must
  be explicit and avoid repeated CFO costs, noncash Capex and debt charges.
- **Interest:** annual cash interest, capitalization basis and lease overlap
  remain unavailable; consolidated CFO can still be preserved as reported.
  Any later unlevering/interest adjustment remains blocked without disclosure
  or an explicitly authorized, sourced analyst proxy—not invented here.
- **Taxes:** cash 43,369m is not provision 20,719m. Note 7 (886/892/926) describes
  the Ireland State Aid decision, prior-year charge/escrow release and current
  tax effects. No full FY2025 cash-tax decomposition or recurring operating-tax
  allocation is established; do not equate a note charge/credit with cash or use
  a residual allocation. Any normalized-tax basis/value needs separate review;
  none selected. Reported jurisdiction/provision evidence is retained, not a
  forecast tax-rate recommendation.
- **Investment/acquisitions:** PP&E cash is evidenced separately; investing
  Other remains mixed. Securities purchases/proceeds are separate financial
  investment facts, not cash operating reinvestment. No isolated acquisition/
  intangible cash or complete cash/noncash PP&E-accrual bridge is approved.
  Acquisitions, FX, note reclassifications and continuing-perimeter effects remain
  unresolved for organic trend/adjusted comparisons, not assumed absent. No
  discontinued-operation adjustment is inferred from lack of a separate caption.

## Decision, validation and stopping point

**PARTIAL GO for data-only packaging design** of one FY2025 reported history;
NO-GO for complete interest, lease cash, reinvestment, cash-adjusted NWC or
valuation readiness. No AAPL economic-treatment choice or estimate approved.
Future entries must be separately labeled facts, classifications or assumptions,
with source, precision, exact period, author and limitations; no default zeros.
The [timing-readiness gate](financial-timing-readiness-design.md) is preserved.

Validation: retained original-body hashes/lengths, CIK/non-amended selected
identity, annual/ comparative contexts, units/dimensions, exact facts/occurrences
and displayed signs verified. All three reported CFO columns reconcile exactly
at submitted rounded points. Evidence/local references and diff check pass.
No SEC requests, source/policy/schema/bundle/scenario changes, tests or corpus
rerun. Baseline **1905/1483/11/27/42 = 3468** unchanged.

Smallest next Phase 1 milestone: implement **one isolated FY2025 reported-input
bundle** containing supported facts and explicit interest/lease/investment
unknowns, without economic treatments or comparative registration. No new
annotation framework or broad research. Stop after this review.
