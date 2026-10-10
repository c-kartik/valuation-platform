# D&A timing-basis compatibility audit

## Decision and scope

Phase 1H.4 Wave 24; starting HEAD
`52b0353a040578e3d8ff7f1a492c612cdca70dca`, clean `main`, ahead of origin by
two. No commits are pushed. This audits implemented contracts and retained
approval evidence, not all issuers' statements. **PARTIAL GO for contract
design; NO-GO for basis-driven policy migration or FCFF certification.**
No existing value is revoked, adjusted or newly approved.

`ESTABLISHED_COMPATIBILITY` below is always qualified by the named contract;
`ESTABLISHED_INCOMPATIBILITY` requires a demonstrated contrary behavior, not
mere lack of proof; `INSUFFICIENT_EVIDENCE` is neither compatibility nor a
finding of economically incorrect values. These are audit terms, not new
runtime states. The [Wave 23 target](financial-methodology.md#da-timing-basis--wave-23-methodology-decision)
for new derivation acceptance is income-recognized recurring operating expense,
net of demonstrated expense reductions. It did not retrospectively prove the
basis of every existing accepted source.

## Implemented D&A families — complete registry reconciliation

| Implemented family / scope | Actual selected basis and evidence | Compatibility conclusion |
| --- | --- | --- |
| `D_AND_A_POLICY`; generic `us-gaap:DepreciationDepletionAndAmortization`, exact annual USD Company Facts | Runtime selects a reported observation, not a reviewed income-versus-generated-cost basis. It does not require statement location, inventory-allocation evidence or incentive netting. Initial META/AAPL/COST validation proves reported-value coverage, not every current issuer-period's timing bridge. | `INSUFFICIENT_EVIDENCE` for family-wide income-expense basis and EBIT/NWC compatibility. Do not label every observation a cash-flow add-back or manufacturing measure from its QName. |
| `msft_annual_d_and_a_v1`; CIK 789019 only; `Depreciation` + `AmortizationOfIntangibleAssets` | Exact same-period Company Facts component addition, with each operand retained. Approval establishes the reported two-component aggregation, but neither policy nor retained initial approval documentation establishes an exhaustive current-income/inventory-release or incentive bridge. No statement-location basis check runs. | `INSUFFICIENT_EVIDENCE` for income-versus-generated/cash-flow timing and combined FCFF compatibility; no demonstrated MSFT incompatibility. Numerical addition and earlier validation are not timing certification. |
| `d_and_a_scope_equivalence`, version `1`; five exact Visa entries, CIK 1403161 | Reviewed consolidated operating D&A expense, also present as a cash-flow adjustment. Operating statement, property/technology and finite-lived intangible expense notes establish the expense perimeter. Runtime preserves the exact combined fact, never sums its two occurrences or adds notes again. | `ESTABLISHED_COMPATIBILITY` with the income-expense target for these five entries only. `INSUFFICIENT_EVIDENCE` for integrated EBIT/NWC/Capex/incentive cash compatibility; Visa has no implemented issuer NWC valuation policy. No manufacturing allocation is presumed. |

Registry coverage is exactly one generic direct family, one D&A component
derivation in `ANNUAL_DERIVATION_POLICIES`, and one five-entry curated policy.
Direct ambiguity is final; curated review can confirm a compatible direct
result; a non-missing result precedes MSFT derivation. Precedence is not a
timing-basis test. Generic eligibility is not restricted to the three initial
validation issuers; this audit does not classify every resolved corpus period.

Code references: [concept registry](../src/valuation_platform/normalization/concepts.py),
[derivation registry and sum](../src/valuation_platform/normalization/derived.py),
[resolution/precedence](../src/valuation_platform/normalization/historical.py),
[curated resolver](../src/valuation_platform/normalization/d_and_a_scope.py) and
[five-entry registry](../src/valuation_platform/normalization/d_and_a_scope_registry.json).
Initial approval evidence is retained in commits `a8ad22b` and `8cf63c1` and
[methodology](financial-methodology.md#da-research-status); neither approval
claims an inventory-timing proof. Visa's exact five accessions, dates, namespaces,
ordinals, source URLs and byte digests are in the
[reviewed scope evidence](depreciation-amortization-scope-evidence-design.md#exact-candidate-facts-and-corroboration)
and source registry. Its operating location is R4 in 2021 and R5 in 2022–2025;
`CostsAndExpenses -> DepreciationAndAmortization` is +1. Cash-flow membership
alone and the rounded 2025 note comparison are not the approval rationale.

## Inventory and NWC consumers — complete implemented perimeter coverage

| Valuation policy/version | Inventory treatment actually configured | Consequence for this audit |
| --- | --- | --- |
| `meta_operating_nwc_valuation` v2, active | No inventory entry; mandatory receivables/AP/employee liabilities only | No inventory-D&A interaction is implemented through this perimeter. This does not prove absence of inventory economics or full FCFF compatibility. |
| `meta_operating_nwc_valuation` v1, archived addressable | No inventory entry; includes customer contract liabilities unlike v2 | Same inventory limitation; v1/v2 levels cannot be combined as a working-capital movement. |
| `googl_operating_nwc_valuation` v1 | Inventory is an explicit methodology blocker | No numerical ready NWC is authorized while blocked; do not replace missing D&A or inventory treatment with zero. |
| `msft_operating_nwc_valuation` v1 | Inventory required; trade AP remains a methodology blocker | Required inventory is the normalized book balance, not an expense-only or cash inventory balance. No numerical ready NWC while blocked; no MSFT expense/inventory bridge established. |
| `aapl_operating_nwc_valuation` v1 | Inventory required; employee/distribution liabilities have methodology blockers | Same book-balance basis; no D&A allocation correction, no currently certified joint timing bridge. |
| `cost_operating_nwc_valuation` v1 | Inventory required; ready when all required facts resolve | Book inventory enters calculated levels. Readiness establishes configured component availability, not D&A timing alignment. Do not infer factory capitalization applies to COST from the TXN case. |

Exactly five active valuation policies, six addressable policy versions and
five strict reconstruction policies exist. Strict reconstruction classifies
evidence and produces no amount: inventory is an asset for GOOGL/MSFT/AAPL/COST
and is not a META entry. It is not a second inventory calculation.
There is no TXN or Visa NWC valuation perimeter. References:
[balance-sheet `InventoryNet` policy](../src/valuation_platform/normalization/balance_sheet.py)
and [NWC registries, readiness, levels and changes](../src/valuation_platform/normalization/operating_nwc.py).

| Consumer | Established behavior | Timing compatibility boundary |
| --- | --- | --- |
| Normalized output/serialization | Preserves direct/derived/curated sources, operands and reviewed Visa audit; schema 4 does not require a common income-expense/generated-cost classification or an allocation bridge. | `INSUFFICIENT_EVIDENCE` for automatic economic basis certification. Source kind (`company_facts` / `filing_xbrl`) is not economic timing basis. |
| `calculate_operating_nwc_level` | Sums required reported balances, assets positive and liabilities negative; no inventory D&A/incentive decomposition. | `ESTABLISHED_COMPATIBILITY` with its book-perimeter arithmetic contract only; joint EBIT/D&A cash compatibility unproved. |
| `calculate_operating_nwc_change` | Exact closing-minus-opening book levels, matching CIK/policy/version/formula/perimeter/USD; preserves both source levels. | Consistent book-change contract, not proof of cash-only change; no D&A or EBIT input is inspected. |
| EBIT / Operating Income output | Separate direct or approved-derived operating subtotal; not linked to a D&A inventory or incentive bridge. | Its reported scope and resolution do not establish compatibility with a separately resolved D&A source. |
| Manual forecast assumptions / future FCFF | Independent operating-margin, D&A/revenue and change-NWC/revenue rates; validation does not reconcile their timing bases. No forecast/FCFF calculator is implemented. | No presently calculated FCFF is proved wrong or right. Treating normalized resolution or NWC readiness as FCFF certification is `ESTABLISHED_INCOMPATIBILITY` with what those contracts actually establish, not an issuer-value finding. |

References: [output](../src/valuation_platform/normalization/output.py),
[assumptions](../src/valuation_platform/valuation/assumptions.py) and
[architecture](architecture.md#financial-normalization-boundary).

## Economic mechanisms, evidence limits and affected scope

Manufacturing depreciation may enter inventory before later cost of revenue;
direct expense, current capitalization and opening inventory releases need not
equal current generated depreciation. If noncash D&A remains in book inventory
changes, an expense-only add-back with unadjusted book NWC can leave an apparent
noncash investment deduction; a generated-cost add-back paired with an
expense-adjusted inventory movement can instead add it twice. These are
conditional algebraic incompatibilities, **not proved nonzero mismatches for
an implemented issuer-period**. Cash-flow add-back placement also does not
identify which basis was used. The approved families lack a universal allocation
bridge; this does not mean every issuer has manufacturing inventory exposure.

The [TXN evidence/methodology review](depreciation-amortization-component-derivation-design.md#wave-23--txn-methodology-review)
is a concrete unresolved example, not an approved policy: all three 2021–2023
periods remain further research. Factory allocation and normal-capacity costing
are supported, but expense/inventory/preproduction amounts are not bridged.
The 2022 395m and 2023 1,360m incentive receivables reduce asset basis; 2023's
45m reduces recognized depreciation expense. Neither basis amounts nor that
reduction may be added/subtracted as operands without demonstrated containment.
These facts are not generalized to MSFT, Visa or every direct-policy issuer.

Visa's excluded client-incentive amortization is a different economic category
from TXN asset-related incentives. Existing Visa expense scope is supported;
no absence-based zero asset grant or universal incentive-neutrality claim is
made. Generic/MSFT code neither grosses up nor separately nets incentives: it
preserves selected values, with netting only to the extent actually contained
in those sources, which is not universally established. Adding intangible
support twice, ignoring deferred depreciation, changing NWC to an unproved
cash basis, or subtracting an already-net incentive would be unsafe.

Thus **no approved family's numeric economic incompatibility is established**
by this bounded audit. Visa expense basis is established; generic/MSFT timing
and all joint future FCFF bridges remain insufficiently evidenced. Current
generic issuer coverage and all approvals are preserved. No new SEC retrieval
is essential to identify these contract gaps; committed evidence is reused.

## Proposed next contract — not current behavior

Smallest next milestone: **documentation-only historical financial-input
timing-basis and consumer-readiness contract design**. Specify period-level
reviewed basis (income expense, generated cost, cash-flow adjustment with
unresolved underlying basis, or unknown), evidence/bridge requirements, and
how joint EBIT/D&A/NWC compatibility differs from normalization resolution.
Do not infer basis from taxonomy, source kind or resolved status. Unknown
must remain unknown; no retrospective certification or migration is authorized.
Assess versioning/provenance/serialization and future forecast-rate consistency
before implementation; preserve book NWC rather than silently adjusting it.
Any generated-cost alternative requires an explicit primitive and integrated
Capex/incentive/tax impact decision. Targeted issuer evidence comes later only
where essential to a specific acceptance; AMD and other unapproved research
remain separate. Phase 2A forecasting/valuation stays paused.

Validation: reconcile all three implemented D&A families, Visa's five identities,
all five active/six addressable NWC policies and five reconstruction policies;
verify code/provenance references, relevant local links and `git diff --check`.
No source/policy/schema/test/inventory/matrix/corpus changes, full tests or corpus
rerun. Production is carried forward, not remeasured: D&A **115/89/0** and
aggregate **1,885/1,503/11/27/42 = 3,468**; existing approvals/skips unchanged.
