# Alphabet FY2024 analyst-input treatment decision memo

2026-10-12; starting HEAD `b4bf92963864fe5b0818f721857ecf020c9b91a8`.
**All recommendations are proposed pending user review.** MSFT/AAPL decisions
are architecture/methodology references, not Alphabet approvals. Strictly Phase 1:
no numerical economic treatment, total, forecast or valuation consumption.

## Exact evidence boundary

GOOG/GOOGL share CIK 1652044. Only selected non-amended 10-K
`0001652044-25-000014`, annual **2024-01-01–2024-12-31**, is registered.
The version-1 [reported registry](company-data-preparation/googl-reported-cash-flow-bundle.json),
contract `reviewed-googl-reported-cash-flow-inputs`, has SHA-256
`97ca73213b6bb46dfdaec67f930d3abd0cfbd6d1a17e50047998c0b2764f509f`.
Its 34 inputs, 38 confirmations and 12 null unknowns remain unchanged.
[Exact input matrix](googl-alternative-historical-cash-flow-inputs.md#exact-input-matrix)
supplies concepts, namespaces, annual context c-1, USD, raw/displayed signs,
ordinals and statement/notes. [Refresh history](googl-alternative-historical-cash-flow-inputs.md#exact-instance-provenance-repair--authorized-refresh)
binds the new instance receipt; original body and missing original metadata
remain separate. Comparatives are supporting evidence, not approved bundles.

Current permitted use is inspection, separate serialization and the reported
CFO reconciliation. Acceptance below would record analyst choices in prose;
it would not change the immutable package or authorize numerical implementation.

## Proposed decisions

All amounts are reported **USD millions**, not new estimates. Decimals −6
unless expressly −8; arithmetic precision is not economic precision.

| Issue | Verified facts and unavailable information | Recommended treatment / permitted use | Limitation and user decision |
| --- | --- | --- | --- |
| Consolidated CFO | CFO 125,299 (ordinal 731), thirteen-term statement bridge; operating balance changes exclude acquisition effects, but acquired operations enter consolidation from acquisition date. Organic/FX/reclassification allocations unavailable. | Use consolidated reported CFO as the historical reference only. | Accept financing-affected, acquisition-affected reported scope, not organic, recurring, operating-only or unlevered cash. No extrapolation approval. |
| Cash PP&E / other investment | Cash PP&E 52,535 (734); combined acquisition/intangible/other-assets cash 2,931 (749); net investing Other 2,667 (752). Noncash ROU additions and capital creditors are separately reported, not cash purchases. Complete investment allocations unavailable. | Retain narrow cash PP&E separately; keep combined and Other amounts visible and unallocated. | Accept incomplete reinvestment coverage, not zero omitted investment. Character note cash/asset recognition is not a full bridge; no residual allocation or acquisition-only estimate. |
| SBC | CFO add-back 22,785 (698, −6); recognized note expense 22,800 (1821, −8). Different roles/precision, not interchangeable exact points. Cash replacement compensation/outstanding-award economic claims are not supplied by these facts. | Propose the **rounded recognized expense as an explicitly labeled annual economic-cost proxy, counted once**. Preserve the exact reported add-back for reconciliation. | User accepts/rejects this source-specific proxy. Do not substitute the expense into the reported bridge, compute a rounding adjustment, or treat both representations as independent costs. Future numerical use requires a separate authorized contract; outstanding awards remain separate. |
| Taxes | Net cash taxes 27,400 (1954, −8); accrued provision 19,697 (568/1881); deferred provision −5,256 differs from CFO deferred adjustment −5,257. Operating-only cash burden unavailable. | Retain reported cash taxes as historical disclosure; leave future operating-tax basis/rate unpopulated. | Accept separation, not a rate or tax shield. A later assumption needs independently justified jurisdiction/reconciliation or explicit proxy rationale and user acceptance. Do not tax already-after-tax CFO again. |
| Restricted lease classes | OperatingLeasePayments 3,425 (1332) and FinanceLeaseInterestPaymentOnLiability 31 (1335) are operating cash already in CFO. FinanceLeasePrincipalPayments 405 (1338) is financing cash already included in debt repayments 12,701 (770). | Retain the three separately labeled reported payment classes and their locations; propose acceptance of this restricted dataset only, not a cash-service modeling convention. | Liability-measurement population only; variable/nonlease cash coverage and borrowing-interest overlap unknown. No sum, extra CFO deduction or duplicate principal charge. User accepts restricted preparation scope; future service-versus-financing convention remains a separate decision. |
| Borrowing interest | Accrued interest expense 268 (1556) and capitalized interest expense 194 (1580), not cash paid. Eligible borrowing cash-interest disclosure unavailable; capitalization/gross-net cash basis unproved. | Retain explicit unknown with **no proxy**. | User acknowledges missing disclosure. Expense, rates, lease interest and future maturities cannot manufacture cash paid. Unknown blocks unlevering/interest completeness claims, not inspection of reported CFO. |
| D&A / NWC / timing | PP&E depreciation add-back 15,311 (695) is not complete D&A. Inventory completeness, supplier-AP scope and acquisition/FX/reclassification bridges remain unresolved; one partial book level supplies no ΔNWC. | Use CFO preparation as a separate path without reconstructing complete opening/closing book NWC; retain all original blockers. | Acceptance avoids book reconstruction only for reproducing the reported subtotal. Do not subtract partial ΔNWC, add D&A/SBC again, infer amortization from mixed Other, or certify timing compatibility. Future consumer must demonstrate its own consistent basis. |

## Rationale and future-consumer boundaries

SBC recommendation uses Alphabet Note 13, not another issuer's accepted proxy.
The established [NYU compensation discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/eqemailSpr25.html)
supports treating noncash compensation as a cost; it does not establish an issuer
cash amount. Choosing rounded recognized expense trades finer numerical precision
for an explicit expense basis. The more precise add-back remains a reconciliation
fact, not automatically the recognized-expense proxy. A future CFO-based consumer
would need a single documented compensation-cost treatment acknowledging the
existing add-back; an income-based consumer already expensing SBC must not charge
again. No numerical neutralization, difference or adjustment is performed here.
Buybacks/withholding/dilution cannot independently charge the same annual cost;
outstanding award claims remain a separate population for later assessment.

Note 1 combines fixed maintenance/utilities with lease components; variable costs
are excluded from liabilities. Note 4, not generic tags, establishes payment
scope and principal inclusion in debt repayments. Expense, finance ROU
amortization and noncash additions are not additional cash. The established
[NYU lease analysis](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/oplease.htm)
requires consistent expense, investment, assets and debt treatment for economic
recategorization; its legacy accounting illustrations are not current ASC 842
or Alphabet evidence. Here restricted data acceptance does **not** approve a
service/financing convention. Future use must define all required payment
populations, embedded CFO/financing overlap and whether lease obligations are
treated as debt, without duplicate cash or asset-investment charges.

The established [NYU tax discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/taxrate.htm)
distinguishes effective/marginal bases; no historical statutory number is imported.
Reported cash/provision/deferral are not a normalized operating-tax assumption.
[Acquisition guidance](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/acqcapex.htm)
requires consistency between acquisition investment and growth. Complete or
organic reinvestment would need evidenced cash allocation and non-overlap;
excluding acquisition investment cannot automatically retain acquired growth.
No new methodological question or new external/SEC request is needed here:
these are established references reused from prior decision memos.

The [timing-readiness contract](financial-timing-readiness-design.md) remains
mandatory before future consumption. A cash-based path must explain which book
gates are inapplicable and prove alternative scope consistency; it cannot waive
unknown compatibility or resolve frozen D&A/NWC by numerical agreement.

## Qualified closure criteria and stopping point

The FY2024 pilot may close **only after explicit user acceptance is recorded**
with author/date, this exact period, source/version, chosen proxy and restrictions:
consolidated reported reference, separate narrow PP&E/investment unknowns,
rounded SBC proxy once, reported taxes with no future rate, and restricted lease
dataset only. Retain all null unknowns, original receipt gap and source precision.
An alternative or rejection must be recorded without replacing prior decisions
or pinned reported facts. Proxy acceptance is a prose analyst choice, not a
source fact, automatic estimate or permission to execute adjustments.

Closure means **qualified one-period historical-input preparation**, not complete
financial coverage, organic/cash comparability, complete interest/leases/D&A/NWC,
complete reinvestment, supported-company upgrade or valuation readiness. It does
not require inventing unavailable allocations or selecting a future tax rate.
Unavailable disclosure is a durable boundary, not an indefinite annotation cycle.

Single next bounded Phase 1 milestone: user review followed by **one FY2024
treatment-acceptance/input checklist**, recording choices/limitations and qualified
closure only if accepted. No further research or implementation starts here.
Phase 2 remains postponed.

Validation: registry hash/exact identity and points/roles/precision checked against
the unchanged registry; evidence and established reference mapping, proposed
versus approved statuses and local links checked; `git diff --check` passes.
No source, schema, policy, bundle, scenario, sidecar or evidence changes; no SEC
requests, tests or corpus rerun. Frozen baseline **1905/1483/11/27/42 = 3468**
is carried forward unchanged, not newly measured.
