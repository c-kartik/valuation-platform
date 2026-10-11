# MSFT alternative historical cash-flow inputs

## Decision and boundary

**PARTIAL GO: prepare reported historical inputs, not an adjusted cash-flow
subtotal.** Exact selected FY2025/FY2026 consolidated cash-flow statements and
notes provide a reproducible reported input path without complete reconstructed
Operating NWC. They do not approve an alternative FCFF equation, complete
operating-only cash perimeter, tax shield, lease adjustment or SBC adjustment.
This is the post-freeze **Phase 1 blocker-resolution extension**; Phase 2 remains
postponed. No production contract or historical value changes.

The [frozen v1](historical-normalization-v1-freeze.md),
[partial NWC bundles](company-data-preparation/msft-analyst-nwc-bundles.json) and
[timing-readiness gate](financial-timing-readiness-design.md) remain intact.
The reported CFO input is not Operating NWC, ΔNWC, EBIT or pure D&A.

## Frozen identities and retained evidence

CIK **789019**, entity identifier `0000789019`; no amendments or implicit
earlier/later approvals. All evidence already resides in the
[original-body manifest](evidence/analyst-operating-nwc-response-bodies.json).
Representation `sec_response_body_bytes`; digest type
`sha256_sec_response_body_bytes`; gzip/base64 is storage encoding, not the bytes
hashed. Manifest supplies retrieval timestamps, HTTP status, URLs and lengths.
No new SEC request was needed. The [NWC inventory](analyst-operating-nwc-inventory.json)
is authoritative for selected identities.

| FY | Selected accession / authoritative annual period | SEC primary / instance; SHA-256 of original bytes |
| --- | --- | --- |
| 2025 | `0000950170-25-100235`; 2024-07-01–2025-06-30 | [Primary](https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm) `9aee86c47d2e3fffc438c671493b709d0e0ba3960917cd5831d145b916eb2c7e`; [instance](https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630_htm.xml) `b90704839beab78c428874d38eaaf2582e048439d53a79f52af3d2cd4ee5e792` |
| 2026 | `0001193125-26-323660`; 2025-07-01–2026-06-30 | [Primary](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm) `cec8684979a7b9f8af4003dcab01ac6b85cbe760aaa8dfbc2d266fdcbf8ac67f`; [instance](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630_htm.xml) `56e56d82ee2d82cb75d37b85df51d4807ffc1e1a3cc4e02ec87513b7574aa886` |

Occurrence notation below is **zero-based root-child XML ordinal**, preserving
document order, not a context/fact count. `g` = `http://fasb.org/us-gaap/2024`
(FY2025) or `/2025` (FY2026); `m` =
`http://www.microsoft.com/20250630` or `/20260630`. All listed facts have empty
dimensions, non-nil numeric values, unit ID `U_USD` measuring exact ISO4217 USD.
Annual context: FY2025 `C_7102029d-8d6c-44c5-b166-04cf41443b1e`;
FY2026 `C_29985a27-1d12-4b7e-9a06-156523f6e71e`. Only capital-creditor balances
use closing instants: `C_f6acec30-41ed-4918-bef7-c8a710bf3a7a` (2025) and
`C_ca004a37-7abb-4b0e-8638-a7c6b14ebb45` (2026).

Values below are **USD millions**; raw numeric value = displayed point ×
1,000,000. `decimals=-6` unless marked `-8` (rounded to 100m). Neither precision
is economically exact. Positive payment tags describe outflow magnitudes,
not positive cash contributions; displayed signs are recorded separately.
Issuer-extension facts are reviewed data candidates only, not generic approvals.

## Input and scope matrix

| Exact concept | FY2025 value / ordinals | FY2026 value / ordinals | Location; proposed treatment / completeness |
| --- | --- | --- | --- |
| g:NetCashProvidedByUsedInOperatingActivities | 136162 / 723 | 182935 / 730 | Consolidated cash flows: positive reported CFO, complete **reported subtotal** only; includes reported interest/tax/lease effects, not certified ordinary unlevered cash. |
| g:InterestPaid | 1600 (-8) / 1643 | 1500 (-8) / 1651 | Note 10 Debt explicitly **cash paid for interest on debt**. Retain narrow scope despite generic tag; not total all-in interest or interest expense. |
| g:InterestExpenseNonoperating | 2385 / 896 | 3051 / 907 | Note 3 Other income (expense): accrued non-operating interest expense; do not substitute for cash paid or assume all lease/capitalized interest included. |
| g:IncomeTaxesPaidNet | 28700 (-8) / 1774 | 21188 / 1808 | Note 12 Income taxes: cash paid net of refunds, all disclosed jurisdictions; not tax expense, operating-only tax or marginal tax rate. FY2026 jurisdiction sum 6246 + 2917 + 6495 + 5530 = 21188. |
| g:IncomeTaxExpenseBenefit | 21795 / 569,1680 | 32185 / 576,1688,1728 | Income statement / Note 12: duplicate confirming tax provision, count once; never infer cash tax from provision. |
| g:DeferredIncomeTaxExpenseBenefit | -7056 / 693,1677 | 14424 / 1685 | FY2025 cash-flow/Note 12 confirm the same value; FY2026 **note provision** differs from cash-flow adjustment below. Distinct semantic roles, not conflicting duplicates. |
| g:DeferredIncomeTaxesAndTaxCredits | Not reported here | 14189 / 700 | FY2026 cash-flow adjustment includes credits; do not replace with 14424 or infer an operating cash allocation from the 235 difference. |
| g:PaymentsToAcquirePropertyPlantAndEquipment | 64551 / 750 | 115948 / 757 | Cash-flow additions to PP&E: investing outflow (display negative). Reported cash purchases, not accrual additions or total investment including leases/acquisitions. Existing direct Capex result unchanged. |
| m:PurchasesOfPropertyAndEquipmentRemainingInAccountsPayable | 6900 (-8) / 1370 | 26700 (-8) / 1384 | Note 6 PP&E: closing capital creditors, not annual cash outflow. Their 19800 movement explains the existing partial-NWC adjustment effect, not a complete accrual-to-cash bridge. |
| m:AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets | 5978 / 753 | 1743 / 760 | Investing outflow magnitude; combined acquisition/intangible/other perimeter, **not separable acquisition cash**. Keep separate from cash PP&E; no residual allocation. |
| g:PaymentsForProceedsFromOtherInvestingActivities | -2317 / 765 | 19861 / 772 | Net other-investing tag: display +2317m / -19861m. Not cash PP&E, a complete productive-asset component or a separate noncash add-back; further separation is unavailable in this reviewed input contract. |
| g:ShareBasedCompensation | 11974 / 687 | 12405 / 694 | Cash-flow noncash adjustment, positive; Note 14 allocation concept below confirms expense, not a second add-back. Economic treatment requires analyst review. |
| g:AllocatedShareBasedCompensationExpense | 11974 / 2093 | 12405 / 2130 | Note 14 expense allocation: same economic expense under a different concept; retain linkage, never sum with cash-flow SBC. |
| g:EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense | 2027 / 2096 | 2089 / 2133 | Note 14 recognized tax benefit, not cash refund or total excess tax benefit. No second automatic tax adjustment. |
| g:PaymentsRelatedToTaxWithholdingForShareBasedCompensation | 5400 (-8) / 1972 | 5600 (-8) / 2009 | Note 14 financing cash withholding; not operating cash compensation, SBC expense or a second corporate income-tax payment. |
| g:Depreciation | 22000 (-8) / 1367 | 34300 (-8) / 1381 | Note 6 PP&E expense disclosure; does not exhaust amortization or prove timing compatibility of the existing MSFT D&A policy. |
| g:OperatingLeaseCost | 5524 / 1838 | 6968 / 1875 | Note 13 expense, distinct from cash operating payments. |
| g:OperatingLeasePayments | 4931 / 1851 | 6443 / 1888 | Note 13 operating cash outflows already inside CFO; not additional cash PP&E. |
| g:FinanceLeaseRightOfUseAssetAmortization | 3408 / 1841 | 5403 / 1878 | Note 13 noncash expense; no separate add-back atop reported CFO. |
| g:FinanceLeaseInterestExpense | 1417 / 1844 | 2547 / 1881 | Note 13 expense; do not conflate with cash debt interest. |
| m:FinanceLeaseCost | 4825 / 1847 | 7950 / 1884 | Note 13 issuer-extension total expense = amortization + interest; not an additional operand. |
| g:FinanceLeaseInterestPaymentOnLiability | 1372 / 1854 | 2547 / 1891 | Note 13 operating cash flow; keep separately identified from debt-interest disclosure. Equality to FY2026 expense does not establish general cash/accrual equivalence. |
| g:FinanceLeasePrincipalPayments | 2283 / 1857 | 3101 / 1894 | Note 13 financing outflow, not investing cash PP&E. |
| g:RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability | 7826 / 1860 | 4555 / 1897 | Note 13 noncash lease asset additions; excluded from cash purchases. |
| g:RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability | 20511 / 1863 | 24608 / 1900 | Note 13 noncash lease asset additions; not cash Capex or principal paid. |
| g:EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations | 63 / 771 | -196 / 778 | Separate cash reconciliation effect; does not quantify FX in operating working-capital balances or certify discontinued scope from its long concept name. |

No analyst numerical estimate, manual allocation or external numerical input is
approved. Normalization classifications above are proposed **data labels** with
scope limitations, not adjusted calculations or policy approval.

## Reported CFO reconciliation and presentation comparability

The complete selected cash-flow reconciliation is below. These are signed
statement contributions, not reconstructed Operating NWC. All are annual,
nondimensional USD, `decimals=-6`; the multiplier converts raw XBRL into the
cash-flow display sign (asset increase tags are positive uses of cash).

| Concept | Raw-to-display multiplier | FY2025 contribution / ordinals | FY2026 contribution / ordinals |
| --- | --- | --- | --- |
| g:NetIncomeLoss | +1 | 101832 / 572,587,681,873 | 133749 / 579,594,688,884 |
| m:DepreciationAmortizationAndOther | +1 | 34153 / 684 | 38534 / 691 |
| g:ShareBasedCompensation | +1 | 11974 / 687 | 12405 / 694 |
| m:GainLossOnInvestmentsAndDerivativeInstruments | -1 | 609 / 690 | -11047 / 697 |
| g:DeferredIncomeTaxExpenseBenefit (2025); g:DeferredIncomeTaxesAndTaxCredits (2026) | +1 | -7056 / 693 | 14189 / 700 |
| g:IncreaseDecreaseInAccountsReceivable | -1 | -10581 / 696 | -12737 / 703 |
| g:IncreaseDecreaseInInventories | -1 | 309 / 699 | -461 / 706 |
| g:IncreaseDecreaseInOtherCurrentAssets | -1 | -3044 / 702 | -2627 / 709 |
| g:IncreaseDecreaseInOtherNoncurrentAssets | -1 | -2950 / 705 | -3964 / 712 |
| g:IncreaseDecreaseInAccountsPayable | +1 | 569 / 708 | 5268 / 715 |
| g:IncreaseDecreaseInContractWithCustomerLiability | +1 | 5438 / 711 | 9361 / 718 |
| g:IncreaseDecreaseInAccruedIncomeTaxesPayable | +1 | -38 / 714 | -1875 / 721 |
| g:IncreaseDecreaseInOtherCurrentLiabilities | +1 | 5922 / 717 | 6847 / 724 |
| g:IncreaseDecreaseInOtherNoncurrentLiabilities | +1 | -975 / 720 | -4707 / 727 |

Summing each column once reproduces **136162m / 182935m exactly at reported
precision**, with no residual or invented component. This is a statement check,
not an adjusted cash-flow/valuation calculation. D&A **and other** is a mixed
cash-flow adjustment, never pure D&A. Gain/loss adjustment need not be entirely
noncash in economic origin; the reported adjustment removes its net-income
effect from the operating reconciliation.

Dimensioned net-income occurrences 804 (FY2025) and 811 (FY2026) are excluded,
even though their values equal consolidated net income. Equal amounts do not
erase a scope dimension or create eligible confirming evidence.

FY2026 Note 1 expressly recasts prior cash-flow presentation with no change to
net operating/investing/financing cash. Its FY2025 comparative shows D&A-and-other
**29433m** (ordinal 692) and gain/loss **-5329m raw / +5329m displayed** (698),
versus selected FY2025 **34153m / +609m displayed**. Differences **-4720m / +4720m**
cancel. Comparative context `C_7575f467-7692-4974-a3da-f27e7e8e1c47` is
2024-07-01–2025-06-30 in the FY2026 accession; it is not selected FY2025 evidence.
Keep it as a linked recast observation, never overwrite the frozen value or
assume the two adjustment lines are trend-comparable. No allocation of the recast
to individual transactions is established by the cancelling arithmetic.

## Methodological references and judgments requiring review

[FASB Statement 95](https://storage.fasb.org/aop_fas95.pdf), paragraphs 17(c),
23(d), 25, 28 and 32, provides the historical basis for investing purchases,
operating interest, FX separation and indirect/noncash reconciliation. It is a
superseded pronouncement, **not a substitute for current ASC 230/842**. Its
capitalized-interest footnote is important: not every interest payment is
necessarily operating, and this review does not establish MSFT's capitalized
interest cash allocation. The issuer's Note 13 explicitly identifies operating
lease cash, finance-lease operating interest and financing principal.

[FASB ASU 2016-09](https://storage.fasb.org/ASU%202016-09.pdf), summary and
Topic 230 amendments, distinguishes operating cash tax effects of share awards
from financing cash paid for employee withholding. This prevents treating both
as a second corporate cash-tax adjustment. Recognized tax benefit is not proof
of current-period cash benefit.

[Damodaran's management-option discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/mgtoption.htm)
and [NYU's SBC discussion](https://www.stern.nyu.edu/experience-stern/faculty-research/why-investors-should-be-wary-stock-based-compensation)
explain why noncash compensation can still transfer economic value to employees.
This conventional analyst consideration is **not an issuer fact** or approval
to deduct SBC, buybacks or withholding from CFO here. No valuation is performed.

User review is required **before any later adjusted-use contract** for:
SBC economic-cost versus dilution treatment (avoid counting both), lease/debt
perimeter and capitalized interest, cash tax versus operating tax and any tax
shield, acquisition/intangible/other investing separation, and recurring versus
non-operating cash classifications. This review proposes preservation of the
reported inputs, not a numerical choice on any of those questions.

## What this avoids; remaining blockers

Reported CFO avoids reconstructing every mixed current balance, deciding its
operating allocation, obtaining an opening complete NWC level, or inferring
cash changes from book balances. The cash-flow statement already reconciles
recognized income to its reported operating cash scope, including disclosed
noncurrent changes. **Do not subtract the partial book ΔNWC again, or add D&A/SBC
again, to reported CFO.** The existing +19800m capital-creditor correction belongs
to a book scenario, not to a cash-flow correction.

It does not eliminate mixed/non-operating cash scope, interest/tax treatment,
cash/noncash lease distinctions, SBC economics, acquisition/FX timing or the
need to understand reported cash-flow reclassifications. The combined acquisition
line is not an acquisition-only input; cash PP&E plus creditor movement plus
lease additions is not proved to be a complete accrual-additions equation.
Discontinued-operation allocations and component-specific acquisition/FX effects
are **not established**, not zero. Reported consolidated scope is established
by Note 1 (subsidiaries included, intercompany eliminated); an independent
continuing-only or organic cash perimeter is not certified.

Expense tax 21795m/32185m, cash tax 28700m/21188m and deferred adjustments remain
distinct. No current tax rate, cash interest completeness, invented allocation
or rounding tolerance is inferred. D&A timing compatibility with EBIT/book NWC
remains unknown; this alternative bypasses reconstruction for reported CFO,
not the valuation-boundary gate for any future adjusted consumption.

## Validation and smallest next milestone

Targeted checks verify both frozen identities; four original-body SHA-256/lengths;
all matrix ordinals, QNames, annual/instant contexts, entity, units, dimensions,
nil status, values/precision and confirming occurrences; statement signs and
both complete CFO bridges; lease expense component sums; tax jurisdiction sum;
capital-creditor movement and comparative recast cancellation. Source presentation
and Notes 1/3/6/10/12/13/14 support the stated scope labels. No source/policy/test
or corpus change; baseline **1905/1483/11/27/42 = 3468** remains frozen.

Meaningful future tests: wrong accession/period/context/entity/digest; amended or
unregistered filing; dimensioned/nil/non-USD/broken facts; equal occurrences
retained once economically versus conflicting values; raw/display sign mapping;
rounded debt-interest/tax/creditor precision; note-scoped interest versus generic
tag; separate expense/cash/deferred tax; duplicate expense/adjustment roles;
recast comparatives cannot overwrite selected history; omitted allocation stays
unknown; serialization retains every occurrence, artifact representation and
analyst label. Arithmetic success must not enable complete-NWC/readiness flags.

**Single next Phase 1 milestone:** implement an isolated, explicit two-period
MSFT **reported cash-flow input bundle and provenance contract**, preserving CFO,
cash PP&E, debt-interest, lease, cash-tax, expense-tax and SBC as separate scoped
inputs with this reconciliation evidence and unknowns. No default estimates,
adjusted subtotal, extension to other periods, blocker removal, forecast or
valuation consumer. Phase 2 remains postponed.
