# Retained cash-flow working-capital movement inspection

Phase 1 only. [Machine-checkable ledger](retained-working-capital-ledger.json)
uses the existing [CFO histories](retained-cfo-results.md) and shared retained
inspection API. Replay: `PYTHONPATH=src .venv/bin/python scripts/inspect_retained_working_capital.py`.
No SEC requests, new issuer approval registry, financial policy or frozen-output
change. This is inspection/partial packaging, not an operating-NWC resolver.

## Bounded meanings and signs

Only the explicitly enumerated standard US-GAAP elements below produce inputs.
Definitions are concise account-movement semantic summaries, not new filing-note
scope approvals. Asset increases consume cash (multiplier −1); liability increases
contribute cash (+1). Both signs of the raw value are supported, without an
absolute-value conversion. The reported operating-capital **account movement**
total also uses −1, not the sign of a presumed cash subtotal.
The [reviewed pilot mappings](pilot-historical-input-mappings.json) pin exact
receivable/inventory/other-asset/payable/accrual/tax/contract-liability sign cases.
Combined asset-only or liability-only captions retain their separate population;
no such caption proves operating-only, current-only or non-overlapping coverage.

| Exact standard concept | Cash multiplier | Population / definition |
|---|---:|---|
| `IncreaseDecreaseInAccountsReceivable` | -1 | receivables: Increase/decrease in accounts receivable. |
| `IncreaseDecreaseInOtherReceivables` | -1 | other_receivables: Increase/decrease in other receivables. |
| `IncreaseDecreaseInReceivables` | -1 | combined_receivables: Increase/decrease in receivables. |
| `IncreaseDecreaseInAccountsAndOtherReceivables` | -1 | combined_receivables: Increase/decrease in accounts and other receivables. |
| `IncreaseDecreaseInInventories` | -1 | inventories: Increase/decrease in inventories. |
| `IncreaseDecreaseInPrepaidExpense` | -1 | prepaid: Increase/decrease in prepaid expense. |
| `IncreaseDecreaseInPrepaidDeferredExpenseAndOtherAssets` | -1 | combined_prepaid_deferred_other_assets: Increase/decrease in prepaid/deferred expense and other assets. |
| `IncreaseDecreaseInOtherCurrentAssets` | -1 | other_current_assets: Increase/decrease in other current assets. |
| `IncreaseDecreaseInOtherNoncurrentAssets` | -1 | other_noncurrent_assets: Increase/decrease in other noncurrent assets. |
| `IncreaseDecreaseInOtherOperatingAssets` | -1 | other_operating_assets_current_noncurrent_unspecified: Increase/decrease in other operating assets. |
| `IncreaseDecreaseInAccountsPayable` | +1 | payables: Increase/decrease in accounts payable. |
| `IncreaseDecreaseInAccountsPayableTrade` | +1 | trade_payables: Increase/decrease in trade accounts payable. |
| `IncreaseDecreaseInAccruedLiabilities` | +1 | accrued_liabilities: Increase/decrease in accrued liabilities. |
| `IncreaseDecreaseInAccountsPayableAndAccruedLiabilities` | +1 | combined_payables_accruals: Increase/decrease in accounts payable and accrued liabilities. |
| `IncreaseDecreaseInAccruedLiabilitiesAndOtherOperatingLiabilities` | +1 | combined_accruals_other_liabilities: Increase/decrease in accrued and other operating liabilities. |
| `IncreaseDecreaseInOtherOperatingLiabilities` | +1 | other_operating_liabilities_current_noncurrent_unspecified: Increase/decrease in other operating liabilities. |
| `IncreaseDecreaseInOtherCurrentLiabilities` | +1 | other_current_liabilities: Increase/decrease in other current liabilities. |
| `IncreaseDecreaseInOtherNoncurrentLiabilities` | +1 | other_noncurrent_liabilities: Increase/decrease in other noncurrent liabilities. |
| `IncreaseDecreaseInAccruedIncomeTaxesPayable` | +1 | income_tax_liabilities: Increase/decrease in accrued income taxes payable. |
| `IncreaseDecreaseInIncomeTaxes` | +1 | income_taxes_mixed: Reported income-tax reconciliation movement; reviewed Alphabet mapping uses cash contribution plus. |
| `IncreaseDecreaseInContractWithCustomerLiability` | +1 | contract_liabilities: Increase/decrease in contract-with-customer liabilities. |
| `IncreaseDecreaseInDeferredRevenue` | +1 | deferred_revenue: Increase/decrease in deferred revenue. |
| `IncreaseDecreaseInOperatingCapital` | -1 | reported_operating_capital_total: Increase/decrease in operating capital; an account-movement total, not a complete requested perimeter. |

Standard mixed/net movements outside this fixed map remain unreviewed. A separate
**discovery-only** diagnostic records annual change-tag names (including tags
that may not be working capital at all); name matching cannot produce an input,
assign a role, normalize a sign, approve an extension or imply eligible scope.
Dimensioned populations remain separate/excluded. This distinction prevents
arbitrary `IncreaseDecrease` name matching from becoming financial acceptance.

## Exact evidence and conservative handling

Shared preparation replays exact selected CIK/accession/10-K and authoritative
annual DEI identity, actual retained receipt/body digest, nondimensional context,
SEC entity scheme, standard taxonomy namespace, exact USD and finite numeric
precision. Inputs retain every confirming original occurrence/root ordinal,
context/unit ID, raw representation, sign multiplier, decimals and full typed
original-body receipt through existing separate immutable-model serialization.
Equal numeric values with different decimals retain distinct alternatives.
Unequal values **within a concept/population** produce a null conflicting input
with all candidates; differing components are not conflicts with each other.
Invalid nil/unit/precision evidence produces a specific null requirement rather
than a replacement value. Missing tags mean not observed in this bounded map,
not zero or no financial disclosure.

Parent/combined captions and children are never summed. The ledger's
`possible_children` relationships indicate potential inclusion/overlap, not
calculation-linkbase proof or permission to add. Other named populations may also
overlap. Tax and noncurrent rows are visible, not automatically operating-current
capital. Standard total observations may include items outside requested roles.
No sum, equation, residual, ratio, completeness score or readiness calculation.

The nonpilot statement scope is explicitly **not independently established**:
consolidated versus continuing, acquisition/disposal exclusions, FX and
reclassifications require statement-specific evidence. Nondimensional entity
matching alone does not settle them. Pilot statement descriptions and their
stated exclusions remain in unchanged original source locators/mappings, not
universal assumptions. In particular MRK 2021–2023 and LIN 2021 retain their
existing narrower CFO scope exception. Movement inspection does not repair it.

## Period coverage versus rows

| Period-level outcome | Count |
|---|---:|
| Selected periods / non-specialized issuers | 199 / 42 |
| Periods with eligible mapped observations | 199 |
| Periods retaining a reported operating-capital total | 5 (KO) |
| Partial/unknown complete-family coverage | 199 |
| No eligible mapped observations | 0 |
| Periods with a conflicting population | 1 |
| Periods with invalid mapped evidence | 0 |

These counts overlap; reported-total periods are a subset, **not** extra years.
Row accounting: **983 observed populations + one conflicting population**;
**421 unsupported/dimensioned discovery occurrences**, not approved rows or
missing disclosures. The four reviewed pilot periods keep 31 original observations
verbatim; 30 also match this standard-only map. Alphabet's already reviewed
revenue-share extension remains in its original bundle, not approved by this
shared map; its diagnostic means unsupported **for new generic acceptance**.
New packages have 953 observed populations and
one null conflicting population. Every new annual also has a specific complete-
perimeter unresolved entry. Reported totals do not discharge that requirement.

NFLX FY2021 `IncreaseDecreaseInContractWithCustomerLiability` has eligible
USD 91,350,000 and 91,000,000 representations. Both values/precisions/occurrences
remain in alternatives; no silent rounding tolerance or order-based selection.
Other evidenced rows in that annual stay available, but this population is null.
One bounded pass ends here, with no new research queue.

Per-issuer counts and every exact period/receipt/occurrence are in the ledger.
XOM remains empty; GEV/SNDK have two annuals. Eleven five-year target deficits
remain explicit, never filled with dates or zero rows. All eight specialized
issuers, including GE, remain excluded from generic preparation.

## Preservation and next step

Original pilot annuals/serialized artifacts, schemas, policies/registries and
all non-movement inputs are unchanged. CFO remains **195 populated / zero
conflicting / four unavailable**. Income remains **357 direct / 25 derived /
11 Revenue conflicts / five CVX EBIT gaps**; all sixteen unresolved income
reviews remain active, not silently accepted. Frozen corpus remains
1905/1483/11/27/42 across 3468 states. No complete NWC, full CFO reconciliation,
financial sufficiency, timing certification or valuation approval follows.

Verified validation: **eight new movement tests and 35 existing shared/CFO/pilot
mapping regressions pass** (43 unique focused tests). The movement tests were
rerun after correcting an AAPL fixture year and separating the already reviewed
Alphabet extension from generic standard inspection. Original-XML/sign/precision
replay, duplicates/conflicts, parent/child scope, invalid evidence, deterministic
serialization, ledger reproducibility and original-artifact/pilot/CFO/income
preservation pass. The ledger retains 990 confirming/candidate occurrences.
Compileall, 1,798 affected local links, count reconciliation and diff checks pass.
No full suite/corpus rerun or SEC request.

**Next bounded step, only with authorization:** retained annual deferred-tax
CFO reconciliation observations using explicit standard concepts, separate from
tax provision/cash-tax and tax working-capital movements. Do not sum them, infer
zero, broaden scope or compute economic adjustments.
