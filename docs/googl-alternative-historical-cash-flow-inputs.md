# Alphabet FY2024 alternative historical cash-flow input review

2026-10-12; documentation-only Phase 1, starting HEAD
`34f7b27eac41185a4a1e0fad6926dd7430fea6c9`. GOOG/GOOGL share one issuer.
No bundle implementation or transfer of MSFT/AAPL analyst treatments.

## Exact identity and original-body evidence

CIK `0001652044`, frozen selected non-amended 10-K **0001652044-25-000014**;
annual **2024-01-01–2024-12-31**, nondimensional context `c-1`. Numeric facts below
are non-nil `usd` (ISO USD). Namespaces: **g:** `http://fasb.org/us-gaap/2024`;
**a:** `http://www.google.com/20241231` (issuer namespace is verified from source
QName, not inferred from a concept's English name). Ordinals are zero-based
extracted-instance root-child positions.

The [retained manifest](evidence/analyst-operating-nwc-response-bodies.json)
contains both complete bodies, representation `sec_response_body_bytes`, digest
type `sha256_sec_response_body_bytes`. Hash decompressed original bytes, not gzip
or parsed/reserialized data:

| Artifact | Exact SEC URL | Original-body SHA-256 / retrieval limitation |
| --- | --- | --- |
| Primary statement/notes | https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm | `88bba3d95ca801192f0c9bf10e4b9baefc56d4567d24156b809a28fb8424746f`; 2,528,455 bytes; retrieved 2026-10-11T17:12:59.460685+00:00, HTTP 200 |
| Extracted instance | https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231_htm.xml | `3847c7f5416ff6055de7bb2370934f9d6f3cafec50c310631ef9f96bd8d764a3`; 2,703,015 bytes; reused retained original body; retrieval time and HTTP status **unrecorded** |

Instance byte identity is verified, but do not fabricate missing retrieval
metadata from the primary receipt or this review date. Existing `Receipt` models
require UTC time/status: this is a **packaging prerequisite**, not a failure of
the available numeric evidence. Retain the original fingerprint/history if a
later verified exact-artifact refresh is needed. No SEC request in this review.

Cash-flow statement printed page 56; Note 1 policies, Note 4 leases, Note 7
other income/interest, Note 8 acquisitions, Note 13 SBC and Note 14 taxes supply
scope. Comparative contexts `c-16` (2022-01-01–2022-12-31) and `c-17`
(2023-01-01–2023-12-31) are source evidence only, not registered bundles or
replacement selected accessions. Existing [FY2024 partial NWC bundle](company-data-preparation/googl-analyst-nwc-bundle.json)
and its rounded manual closing-note interpretation remain unchanged.

## Exact input matrix

Amounts are **USD millions**. `decimals=-6` unless noted. Signs below are
displayed statement signs; raw-value exceptions are explicit. All numeric rows
have exact annual `c-1` context. Confirmation occurrences count once.

| Concept / source | FY2024 displayed value | Ordinal | Role / limitation |
| --- | ---: | --- | --- |
| g:NetIncomeLoss | +100,118 | 571/580/682/**692** | Accrual income; 692 is CFO starting amount |
| g:Depreciation | +15,311 | 695 | CFO depreciation of PP&E add-back; **not complete D&A primitive** |
| g:ShareBasedCompensation | +22,785 | 698 | Reported CFO noncash reconciliation, not a second economic cost |
| g:DeferredIncomeTaxesAndTaxCredits | −5,257 | 701 | CFO deferred adjustment; separate provision fact −5,256 at 1878 is not interchangeable |
| g:DebtAndEquitySecuritiesGainLoss | −2,671 | 704 | Raw +2,671 gain; displayed cash reconciliation subtraction |
| g:OtherNoncashIncomeExpense | +3,419 | 707 | Raw −3,419; displayed addition, mixed scope |
| g:IncreaseDecreaseInAccountsReceivable | −5,891 | 710 | Raw +5,891, asset-change sign reversed |
| g:IncreaseDecreaseInIncomeTaxes | −2,418 | 713 | Raw −2,418; tax operating-change row, not separate tax payment |
| g:IncreaseDecreaseInOtherOperatingAssets | −1,397 | 716 | Raw +1,397; mixed operating assets |
| g:IncreaseDecreaseInAccountsPayable | +359 | 719 | Cash-flow change, not proof of closing operating-only AP |
| g:IncreaseDecreaseInAccruedLiabilities | −1,161 | 722 | Mixed operating reconciliation |
| a:IncreaseDecreaseInAccruedRevenueShare | +1,059 | 725 | Revenue-share operating reconciliation |
| g:IncreaseDecreaseInContractWithCustomerLiability | +1,043 | 728 | Deferred revenue operating reconciliation |
| g:NetCashProvidedByUsedInOperatingActivities | +125,299 | 731 | Consolidated reported CFO, not organic/unlevered cash |
| g:PaymentsToAcquirePropertyPlantAndEquipment | −52,535 | 734 | Raw +52,535 investing cash payment, narrow PP&E |
| a:AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets | −2,931 | 749 | Raw +2,931 combined acquisition/intangible cash; no full allocation |
| g:PaymentsForProceedsFromOtherInvestingActivities | −2,667 | 752 | Raw +2,667 net investing Other; no complete organic reinvestment claim |
| g:IncomeTaxesPaidNet | 27,400 payment magnitude | 1954; **−8** | Note 14 cash net of refunds, not operating-tax assumption |
| g:IncomeTaxExpenseBenefit | +19,697 expense | 568/1881 | Accrued provision, not cash; all exact confirmations retained in any later packaging |
| g:AllocatedShareBasedCompensationExpense | 22,800 expense | 1821; **−8** | Rounded note expense; do not silently substitute for 22,785 CFO observation |
| g:InterestExpenseNonoperating / InterestCostsCapitalized | 268 / 194 expense | 1556/1580 | Note 7 recognized interest net of capitalization / capitalized interest; neither is cash paid |
| Cash borrowing interest | **Unavailable** | No separate eligible annual cash-paid disclosure found | No expense-to-cash or debt-rate estimate approved |
| g:OperatingLeasePayments | 3,425 payment magnitude | 1332 | Note 4 operating cash, already CFO; liability-measurement population |
| g:FinanceLeaseInterestPaymentOnLiability | 31 payment magnitude | 1335 | Note 4 operating cash, already CFO; keep separate from accrued interest |
| g:FinanceLeasePrincipalPayments | 405 payment magnitude | 1338 | Note 4 financing cash, included in face repayments of debt 12,701 at 770; **not additional to that line** |
| g:OperatingLeaseCost / FinanceLeaseInterestExpense / VariableLeaseCost | 3,304 / 31 / 1,425 expense | 1283/1289/1295 | Costs, not extra payments or proof of total lease cash |
| g:RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability / RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability | 2,510 / 313 additions | 1341/1344 | Noncash ROU additions, not cash PP&E/principal |

Capital-creditor scope cross-check, **not annual cash spending**: Note 7 separately
reports a:AccruedPurchasesOfPropertyAndEquipmentCurrent **7,104m**, ordinal 1446, instant
`c-9`, 2024-12-31, −6, and footnote additional PP&E in AP **3,200m**,
g:CapitalExpendituresIncurredButNotYetPaid, ordinal 1459, actual duration `c-1`,
−8. Its closing meaning is established by the note, not the duration tag. Retain
the existing manual interpretation/precision; neither is a cash addition,
complete noncash bridge, or additional deduction from reported cash purchases.

**Reported CFO reconciliation only:**
100,118 + 15,311 + 22,785 − 5,257 − 2,671 + 3,419 − 5,891 − 2,418
− 1,397 + 359 − 1,161 + 1,059 + 1,043 = **125,299**.
This checks thirteen displayed source terms, not an adjusted subtotal. The
FY2022/FY2023 comparative columns reproduce CFO **91,495 / 101,746** with their
own raw/displayed signs. No comparative input approval follows.

## Findings, analyst choices and limitations

- **Reported history:** proposed data path is consolidated CFO plus separate
  evidenced PP&E and other inputs. CFO asset/liability changes explicitly say
  **net of effects of acquisitions**. This does not make the whole CFO organic:
  Note 1 includes acquired operations from acquisition date. FX, recasts and
  continuing-perimeter effects remain unresolved for economic trend use.
- **NWC avoided requirements:** reproducing reported CFO does not require
  reconstructing missing inventory, a complete operating-only AP balance or
  the rounded 3.2bn PP&E-in-AP correction. Do not subtract partial ΔNWC or add
  depreciation/SBC again. Those book-scope blockers remain for other uses; cash
  changes do not certify the partial book perimeter or cash comparability.
- **D&A preserved:** the cash statement's PP&E depreciation fact supplies a
  reconciliation term, not an approved complete depreciation/amortization
  amount. Mixed Other is not a residual amortization operand. Alphabet's frozen
  D&A remains missing in all five periods; see [D&A research](depreciation-amortization-concepts.md).
  No generic policy, component equation or timing gate is changed by this path.
- **SBC/tax choices:** the −8 note expense and −6 CFO add-back have different
  precision. Treat them as related but distinct reported representations, not
  equal exact points or two independent costs. A future proxy choice must bind
  its source/precision explicitly and avoid double counting; no cost proxy
  automatically inherited. Rounded cash taxes and precise provision/deferred
  reconciliation differ in basis; no operating-tax rate/assumption is selected.
- **Leases/interest:** Note 1 policy 818 combines fixed maintenance/utilities
  with lease components; variable costs are excluded from lease liabilities.
  Note 4 cash table 1329 establishes the three payment classes and explicitly
  embeds finance principal in repayments of debt. Variable/nonlease coverage,
  borrowing-interest overlap, cash capitalization and gross/net basis are not
  established. Note 7's quantified capitalized **expense** does not prove cash.
  Keep all populations separate; no certified total, service/financing convention
  or inferred operating-interest split is approved.
- **Acquisitions/noncash:** Note 8 text 1581 reports Character cash 2.7bn,
  canceled convertible instruments, goodwill 2.7bn and intangible assets 413m.
  The passage is rounded note evidence, not a full non-overlapping bridge to the
  2,931m cash-flow line. Do not subtract 2.7bn to infer other acquisition/intangible
  cash, or treat asset recognition/canceled instruments as cash. Securities
  investing payments are separate financial investments, not automatic operating
  reinvestment. Cash PP&E, accrued capital creditors and noncash ROU additions
  remain distinct.

## Decision, validation and bounded next milestone

**PARTIAL GO for one-period reported-input preparation design**, not complete
NWC, D&A, lease cash, interest, reinvestment or integrated readiness. Analyst
choices for SBC, leases, cash scope and future tax treatment remain unapproved.
Preserve source facts/unknowns and [timing-readiness requirements](financial-timing-readiness-design.md).

Validation: both original bodies/digests/lengths, selected CIK/accession/form and
annual contexts, exact numeric units/nil/dimensions/precision/ordinals, statement
signs and all three reported CFO column equations checked. Missing instance
receipt metadata is disclosed, not “validated” into existence. Local links and
diff check pass. No SEC requests, tests/corpus, production changes or artifact
edits; baseline **1905/1483/11/27/42 = 3468** carried forward.

Smallest next Phase 1 milestone: **bounded exact-instance receipt-provenance
recovery/verification before any Alphabet bundle implementation**. Establish
actual retained retrieval metadata, or transparently refresh only that selected
instance if essential under the existing receipt contract, preserving the old
body/digest/history. Do not weaken metadata requirements or manufacture a receipt.
No broader financial research/annotation cycle. Stop after this review.

## Exact-instance provenance repair — authorized refresh

Completed 2026-10-12 local date; **refresh, not recovery of original metadata**.
Inspected the original retained manifest, D&A inventory entry, cached-body
diagnostic `/tmp/da-wave18/0001652044-25-000014.json`, related note records,
`/tmp/analyst-nwc-research.log`, and the retained research scripts/cache. The
NWC script explicitly assigned `None` to receipt time/status when reusing a
cached body; the earlier D&A fetch/cache code retained bodies/hashes but no
body-bound receipt timestamp/status. No inspected record recovered those fields.
File modification dates, fetch-code expectations and present availability were
not used as original-receipt proof.

User-authorized **one exact URL GET**, no redirects or broad retrieval, returned
HTTP **200**. Actual receipt time **2026-10-11T21:10:46.050735+00:00** is UTC
(2026-10-12 in the project timezone), not a backdated original receipt.
The additive [refresh evidence](evidence/googl-fy2024-instance-provenance-refresh.json)
retains request-start/receipt times, response status/headers, exact accession/URL,
representation `sec_response_body_bytes`, digest type
`sha256_sec_response_body_bytes`, length and gzip/base64 original body.
Evidence-file SHA-256:
`1047e612f28d9da2e2974f687c61b858524b7ad168ebc0d8cc4c1118903e368b`.

The refreshed response is **byte-for-byte identical**, 2,703,015 bytes, to the
original retained instance; both have SHA-256
`3847c7f5416ff6055de7bb2370934f9d6f3cafec50c310631ef9f96bd8d764a3`.
There is no substantive or representational body change. The new retrieval
event supplies new metadata; equality does not retroactively recover old
metadata. The original manifest/body, null receipt fields and all fingerprints
remain unchanged and explicitly linked from the additive record.

Independent parsing of the refreshed bytes verified selected CIK, non-amended
10-K/FY identity, 2024-01-01–2024-12-31 context, exact taxonomy/concepts, normalized
USD, no dimensions/nil, occurrence positions, raw values and precision for
**30 relevant facts**: thirteen CFO operands, CFO/PP&E, investment, SBC/tax,
interest/capitalization and lease/noncash disclosures. All three annual reported
CFO statement bridges reproduce; no adjusted subtotal or new total. A new
receipt conforms to the existing immutable `Artifact`/`Receipt` validators using
actual refresh metadata; no model change or bundle registration was made.

This resolves **only the future packaging receipt prerequisite** via a separately
identified refresh. Source uncertainty, cash-interest/lease/investment scope,
SBC precision differences, D&A/NWC and timing limitations persist. No complete
financial coverage or analyst/valuation approval. Primary statement evidence and
all existing bundles/scenarios/frozen-v1 artifacts remain unchanged. Links and
`git diff --check` pass; no full suite or corpus rerun.

Single next Phase 1 milestone: **one isolated Alphabet FY2024 reported-input
bundle**, using the explicit new instance receipt and unchanged primary evidence,
with source roles/rounding and all unknowns preserved. Retain the separate
original-metadata gap/history and do not implicitly register comparative years
or import another issuer's analyst treatments. Stop after this evidence repair.
