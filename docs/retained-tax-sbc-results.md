# Retained deferred-tax and SBC reconciliation observations

Phase 1 only. [199-period ledger](retained-tax-sbc-ledger.json) and replay:
`PYTHONPATH=src .venv/bin/python scripts/inspect_retained_tax_sbc.py`.
Uses unchanged [working-capital packages](retained-working-capital-results.md),
[shared inspection](architecture.md), [input contract](dcf-input-contract.md)
and [reviewed pilot mappings](pilot-historical-input-mappings.json).
No SEC requests, issuer-specific approval registry, new periods, residuals,
component totals, rates, assumptions, economic adjustments or valuation approval.

## Bounded roles, not a substring resolver

Only the following explicit standard-element/role mappings produce observations.
Definitions are concise taxonomy semantic summaries, with role/sign cases pinned
by the existing [MSFT](msft-alternative-historical-cash-flow-inputs.md),
[AAPL](aapl-alternative-historical-cash-flow-inputs.md) and
[Alphabet](googl-alternative-historical-cash-flow-inputs.md) evidence reviews.
No tag-name substring discovery or arbitrary issuer-extension acceptance.

| Field | Exact standard concept | Role / scope | Multiplier | Reconciliation eligibility |
|---|---|---|---:|---|
| deferred_taxes | `DeferredIncomeTaxesAndTaxCredits` | cfo_deferred_tax_adjustment_combined_credits: Deferred income taxes AND tax credits in the reported noncash reconciliation; not a certified pure deferred-tax component. | +1 | Eligible, partial scope only |
| deferred_taxes | `DeferredIncomeTaxExpenseBenefit` | deferred_tax_provision: Deferred income-tax expense/benefit; provision observation alone does not establish CFO placement. | +1 | Support only; cannot populate required CFO role |
| deferred_taxes | `DeferredIncomeTaxExpenseBenefitContinuingOperations` | continuing_deferred_tax_provision: Deferred expense/benefit for continuing operations, not consolidated CFO adjustment. | +1 | Support only; cannot populate required CFO role |
| deferred_taxes | `DeferredIncomeTaxExpenseBenefitDiscontinuedOperations` | discontinued_deferred_tax_provision: Deferred expense/benefit for discontinued operations, not consolidated CFO adjustment. | +1 | Support only; cannot populate required CFO role |
| stock_based_compensation | `ShareBasedCompensation` | sbc_cfo_addback: Reported noncash share-based compensation reconciliation observation; not grant/award value or withholding cash. | +1 | Eligible, partial scope only |
| stock_based_compensation | `AllocatedShareBasedCompensationExpense` | sbc_note_expense: Allocated recognized compensation expense, separate from CFO reconciliation and outstanding awards. | +1 | Support only; cannot populate required CFO role |
| deferred_taxes | `OtherNoncashIncomeExpense` | unallocated_other_noncash_support: Mixed other noncash income/expense; no assumption that it contains deferred tax or any allocatable amount. | -1 | Support only; cannot populate required CFO role |
| stock_based_compensation | `OtherNoncashIncomeExpense` | unallocated_other_noncash_support: Mixed other noncash income/expense; no assumption that it contains SBC or any allocatable amount. | -1 | Support only; cannot populate required CFO role |

Deferred expense/benefit is a **provision** observation by default, not proof of
cash-flow placement. Existing reviewed MSFT FY2025 evidence independently binds
its −7,056m provision to the CFO adjustment; that original input stays unchanged.
No similar role is inferred for other filings from numerical agreement.
`DeferredIncomeTaxesAndTaxCredits` retains the broader tax-credit scope, not a
certified pure deferred-tax amount. Continuing/discontinued provision tags cannot
substitute for a consolidated CFO adjustment. Deferred-tax asset/liability
balances, cash taxes and working-capital tax rows remain separate diagnostics,
not adjusted or substituted into the reconciliation field.
`IncreaseDecreaseInDeferredIncomeTaxes` is explicitly an unreviewed deferred-tax
account-movement role in this pass, **not** certified as working capital or a
complete deferred CFO adjustment. No expense/balance bridge is inferred.

`ShareBasedCompensation` is the reported noncash reconciliation observation;
`AllocatedShareBasedCompensationExpense` is a distinct expense observation.
Award/grant values, recognized tax benefits, withholding and buyback cash are
explicitly excluded by a closed diagnostic list. An expense-only observation
does not populate the required SBC reconciliation role. No second charge follows
from retaining both expense and add-back representations.

`OtherNoncashIncomeExpense` is a **mixed, unallocated support row**, never an
assumption that it contains deferred tax/SBC or a means to fill a missing input.
Its raw net-income sign is reversed (−1) to preserve the displayed reconciliation
sign: AAPL FY2025 raw +89m → −89m; Alphabet FY2024 raw −3,419m → +3,419m.
All other listed observations retain their signed raw numeric values (+1),
including negative deferred benefits. A provision/expense sign remains its own
role, not a cash-tax payment or automatic cash adjustment.

## Exact evidence and conservative selection

The existing shared path independently binds actual original response bytes,
typed digests and receipt metadata, exact frozen accession/CIK/form/annual DEI,
nondimensional SEC-entity context, exact USD currency and original precision.
Every confirming occurrence retains namespace/concept, raw representation,
context/unit IDs and root ordinal. Unequal values within one concept/population
produce a null conflict with all alternatives. Numerically equal values with
differing decimals remain separate precision alternatives. Different note versus
reconciliation concepts are not conflicting or additive merely because values
differ. Invalid nil/unit/precision evidence and absent eligible observations
remain specific null requirements; never zero.

Combined/noncurrent/tax captions keep their declared scope. New inputs stay
PARTIAL/LIMITED; independent face placement, consolidated versus continuing
scope, acquisition/FX/reclassification and timing compatibility are not
retrospectively certified. The fixed diagnostics preserve excluded annual and
annual-end instant populations; comparative facts remain in the original body,
not additional registrations. Extensions using listed local names remain
unsupported for this shared pass; other unlisted concepts are not searched or
implicitly approved. No financial-policy or financial-sufficiency expansion.

## Period outcomes, independently for each field

| Required reconciliation role | Populated | Conflicting | Unavailable | Selected periods |
|---|---:|---:|---:|---:|
| Deferred-tax reconciliation | 39 | 0 | 160 | 199 |
| SBC reconciliation | 164 | 5 | 30 | 199 |

"Populated" means an evidenced observation within its stated scope, **not complete
component coverage**. Deferred-tax 39 comprises 38 broader tax-and-credit
observations plus the already reviewed MSFT FY2025 provision/CFO role. The 179
provision populations in the ledger are support observations, not 179 additional
CFO approvals. Mixed support rows cannot allocate the remaining 160 periods.
SBC has 169 eligible reconciliation populations (including five conflicts),
136 note-expense populations and 108 mixed support populations. Deferred-tax
also retains 108 mixed support populations. Observation counts are neither
additional periods nor completeness scores; support roles may themselves have
conflicting representations without becoming CFO substitutes.

INTC's five `ShareBasedCompensation` conflicts retain each exact and rounded
representation: 2021 2,036m / 2,000m; 2022 3,128m / 3,100m; 2023 3,229m / 3,200m;
2024 3,410m / 3,400m; 2025 2,434m / 2,400m. Precision is −6 versus −8. These may be
compatible rounded presentations, **not established economic contradictions**,
but neither rounding tolerance nor occurrence order establishes a selected CFO
population. They remain unresolved after this bounded pass, not silently adjusted.

All four original pilot annuals/serialized artifacts are reused verbatim:
MSFT FY2025/FY2026, AAPL FY2025, Alphabet FY2024. AAPL's deferred-tax gap remains;
MSFT FY2026's 14,189m reconciliation and 14,424m provision remain separate;
Alphabet's −5,257m tax/credit adjustment and −5,256m provision remain separate.
Alphabet SBC **22,785m / decimals −6** versus note expense **22,800m / decimals −8**
remain distinct, without a rounding adjustment or duplicate charge.

Per-issuer outcome counts and exact source/period/occurrence bindings are in the
ledger and linked from all forty preparation records plus the two seed notes.
XOM remains empty; GEV/SNDK have two periods. Eleven five-year target deficits
remain explicit; all eight specialized issuers, including GE, remain excluded.

## Preservation, validation and stopping point

Only the two new field families change in nonpilot partial histories. Original
income, CFO and movement inputs and their serialized/source bindings are
unchanged: income 357 direct / 25 derived / eleven conflicts / five CVX EBIT
gaps; CFO 195/0/4; movement observations in 199 periods, five KO totals and one
NFLX population conflict. Frozen schema 5, financial policies/registries,
corpus 1905/1483/11/27/42 across 3468 states, classifications and blockers
remain unchanged. Financial sufficiency and timing gates remain unassessed.
No full-suite/corpus rerun, new financial review or SEC request.

Verified validation: **nine new tests and 37 relevant shared/pilot regressions
pass** (46 unique focused tests). The new tests were rerun after correcting two
ledger signed-zero representations; no financial value or coverage rule changed.
Checks cover both signs, actual retained XML/role/precision binding, combined
captions and forbidden substitutions, duplicates/conflicts, missing/invalid
evidence, closed serialization with independent replay, original pilot rounding,
and all non-target fields/artifacts. All 199 receipt bindings replay; no mapped
evidence errors. Compileall, 1,892 affected local links, counts and diff checks
pass. No full-suite/corpus rerun or SEC request.

**Stop after these two fields. Next bounded step, only when authorized:** retained
cash-Capex preparation using existing direct semantics and exact approved curated
policies, preserving reported cash/noncash/acquisition distinctions and all
controls. No new scope fallback or adjustment equation. D&A keeps its separate
primitive/timing limitations until its own bounded integration.
