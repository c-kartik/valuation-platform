# MSFT FY2025–2026 historical-input acceptance checklist

2026-10-12; documentation revision 1. Acceptance authority: the user's explicit
milestone instructions, not an inferred policy approval. This records analyst
choices alongside unchanged SEC-reported inputs; it is not a schema, sidecar,
calculator or valuation-consumption authorization. Phase 2 remains postponed.

## Decisions and permitted scope

| Treatment | Acceptance | Restriction |
| --- | --- | --- |
| SBC | Accepted economic-cost proxy: recognized annual expense, counted once | Expense is not cash replacement compensation. Outstanding awards remain separate; do not charge the same cost again through withholding, buybacks or dilution. A future cash-based calculation must address the existing CFO add-back once; an income-based calculation must not deduct expense twice. No adjustment performed here. |
| Historical reference | Accepted consolidated reported CFO | Not organic, adjusted or operating-company-only cash flow; no partial ΔNWC subtraction or repeated D&A/SBC addition. |
| Investment | Accepted separate evidenced cash PP&E input | Not complete reinvestment. Combined acquisition/intangible/other cash spending stays visible and unallocated; no assumed zero or residual allocation. |
| Taxes | Accepted reported cash-tax data | No operating-tax rate or basis approved. A future analyst entry requires justified scope, source and explicit acceptance; no second tax on already after-tax CFO. |
| Leases | Cash-service convention accepted **in principle**; restricted operand definition below | Future consumption remains conditional on explicit acceptance of the restricted coverage and consistent expense/investment/debt treatment. Not certified total lease cash or combined interest. Borrowing cash remains separate. |

The [decision memo](msft-analyst-treatment-decision.md) preserves the original
options, rationale and authoritative methodological references. Acceptance of
data/classifications is not evidence of completeness or integrated readiness.

## Exact two-period input checklist

CIK `0000789019`, selected non-amended 10-Ks only. Values below are **USD millions
as reported**, not newly calculated totals. Parent bundle IDs are
`msft-reported-cash-flow-fy2025` and `msft-reported-cash-flow-fy2026`, contract
`reviewed-msft-reported-cash-flow-inputs`, version 1. No extension to other years.

| Identity/input | FY2025 | FY2026 | Classification/restriction |
| --- | --- | --- | --- |
| Accession | `0000950170-25-100235` | `0001193125-26-323660` | Exact selected filing |
| Annual dates | 2024-07-01–2025-06-30 | 2025-07-01–2026-06-30 | Exact annual duration |
| Annual context | `C_7102029d-8d6c-44c5-b166-04cf41443b1e` | `C_29985a27-1d12-4b7e-9a06-156523f6e71e` | Nondimensional, non-nil USD occurrences |
| Consolidated CFO | 136,162 | 182,935 | Reported cash subtotal; accepted historical reference |
| SBC expense / separate CFO add-back | 11,974 / 11,974 | 12,405 / 12,405 | Separate noncash expense/reconciliation facts; expense selected as proxy, not two costs |
| Cash PP&E purchases | 64,551 | 115,948 | Investing cash outflow; narrow separate accepted input |
| Acquisition/intangible/other purchases | 5,978 | 1,743 | Reported combined investing outflow, visible but unallocated |
| Cash income taxes, net | 28,700 | 21,188 | Reported cash payment, not operating-tax assumption; decimals −8 / −6 |
| Borrowing interest cash | 1,600 | 1,500 | Note 10 debt-scoped payment, decimals −8; overlap and capitalization/gross-net basis unresolved |
| Operating-lease cash | 4,931 | 6,443 | Note 13 operating cash flows, already within CFO |
| Finance-lease interest cash | 1,372 | 2,547 | Note 13 operating cash flows, already within CFO |
| Finance-lease principal cash | 2,283 | 3,101 | Note 13 financing cash flows, outside CFO; separate future service-treatment candidate |

Unless explicitly noted, these facts have XBRL decimals −6. Reported precision
does not make an economic quantity exact. Source payment facts are positive
magnitudes; preserved bundle cash-outflow multipliers are −1, CFO and expense/
reconciliation classifications +1. No sum, adjustment or change of signs occurs.

Exact concepts, taxonomy namespaces, raw values, every retained occurrence and
zero-based occurrence ordinals remain in the [immutable input registry](company-data-preparation/msft-reported-cash-flow-bundles.json).
The [sidecars](company-data-preparation/msft-cash-interest-annotations.json)
retain rounding, cash/accrual distinctions, explicit unknowns and relationships.
They grant no summation/completeness permission. The [evidence matrix](msft-alternative-historical-cash-flow-inputs.md)
ties these to the selected statements, Note 10 debt, Note 12 taxes, Note 13
leases and Note 14 SBC, rather than replacing sources with this summary.

## Precise lease convention and conditional boundary

The proposed **restricted cash-service operand perimeter** includes only:
`OperatingLeasePayments`, `FinanceLeaseInterestPaymentOnLiability`, and
`FinanceLeasePrincipalPayments` reported in Note 13 as cash paid for amounts
included in measurement of lease liabilities. Both lease classes are in scope;
the first two are already in operating CFO, principal is financing cash. Do not
add the first two again to a CFO-based history. Principal is not reclassified or
deducted by this checklist. No combined amount is authorized.

Borrowing `InterestPaid` is outside this lease bucket. Its uncertain overlap
with finance-lease interest prevents certification of a mutually exclusive
all-interest total. Expense versus cash, interest capitalization and gross/net
basis are not resolved by matching values. Operating-lease expense, finance
interest expense, ROU amortization and total lease cost are not additional cash
operands. Noncash ROU asset/liability additions are not cash investment.

Coverage of variable/short-term payments and nonlease service components is not
established by the liability-measurement cash disclosures. Note 1 separates
lease/nonlease components generally but combines certain equipment/vehicle
components. Their cash allocations and overlap with reported payments/CFO are
unavailable; no separate amount or zero is inferred.

**Outstanding decision:** explicitly accept this limited reported-cash perimeter
with unallocated service-cost coverage, or require comprehensive lease-service
cash coverage, which retained disclosures cannot establish. The recommendation
is the limited perimeter, clearly labeled; the user's in-principle approval does
not silently approve comprehensive coverage or a financing-policy alternative.

Any future consumer must specify its starting basis and ensure lease expense,
cash interest/principal, asset investment and debt are treated consistently.
Service payments already in CFO must not be charged twice; noncash lease assets
must not be inserted as cash Capex. Full service-payment treatment must not also
charge the same lease obligation as financing debt in a later bridge. Reported
liabilities remain facts, not deleted data. An income-based or financing-based
alternative requires its own explicit reconciliation and approval. The
[timing-readiness contract](financial-timing-readiness-design.md) is not waived.

## Remaining inputs, restrictions and stopping point

Both years permit source inspection, separate reported input packaging and
comparison with the stated precision, plus recording accepted proxy/classification
choices. Neither permits adjusted subtotals, interest totals, FCFF or forecasts.
Future analyst entries must identify author, decision date, exact period, source
or justified assumption, uncertainty and affected treatment; no defaults.

| Requirement | FY2025–2026 disposition |
| --- | --- |
| Operating-tax assumption | Absent. Future basis and any rate require explicit justified acceptance; tax provision, cash tax and tax-interest accrual are distinct. |
| Lease applicability | Conditional restricted-perimeter decision above; unavailable coverage cannot be manufactured. |
| Organic/acquisition/intangible investment | Unallocated. Any future organic claim needs independent allocation evidence and growth-consistent treatment. |
| Acquisition, FX, reclassification and timing | Unresolved for comparable/adjusted economic use. Not required to reproduce consolidated reported CFO; not thereby eliminated or zero. |
| Complete book NWC / all-in cash interest | Existing blockers retained. Partial NWC scenarios and their capital-creditor movements are not complete cash-flow bridges. |
| Integrated future consumption | Unproved. Explicit basis/applicability and timing review required before any later valuation authorization. |

This **closes the MSFT Phase 1 pilot only as two-period reported historical-input
preparation with accepted choices and explicit conditional boundaries**. No
claim of complete NWC, cash interest, reinvestment, organic comparability or FCFF
readiness follows. No further data implementation is required for this scope.
Smallest subsequent Phase 1 milestone: **one user decision on the restricted
lease-service perimeter and its stated exclusions**; stop pending that review,
without another research/annotation cycle. Frozen-v1 and all bundles/sidecars
remain unchanged. Production baseline remains **1905/1483/11/27/42 = 3468**.
