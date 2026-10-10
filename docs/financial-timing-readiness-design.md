# Financial timing evidence and consumer-readiness contract

## Decision and phase placement

Phase 1H.4 Wave 25; starting HEAD
`f8308df540e683df0d4f385e81614cdbf4f44cb7`. **GO for this documented contract;
NO-GO for certifying current integrated FCFF compatibility or migrating values.**
This is a proposed valuation-boundary contract, not an implemented model,
schema, policy registry, enum or calculator. Reuse the
[Wave 24 audit](depreciation-amortization-timing-audit.md) and its source references.

The [Phase 1H roadmap](project-status.md#phase-1h-roadmap) requires constituent
classification and unresolved typed states in 1H.5, then supported scope and
exclusions in the 1H.6 historical-normalization freeze. It does **not** require
every resolved historical measure to be FCFF-ready. Before that freeze, record
the timing evidence/unknowns and explicit exclusion of integrated FCFF
certification. This design supplies that boundary; it does not announce that
1H.5/1H.6 or the remaining historical work is complete. The executable joint
gate belongs at the **valuation boundary after 1H.6 and before historical
inputs are used to calculate FCFF**. It must also govern any forecast consumer
of historical ratios, not silently certify manual assumptions. No valuation
implementation is authorized during Phase 1H.

## Two independent decisions

Historical resolution answers whether a reported/approved-derived value can
be normalized. Timing readiness answers whether a specified input bundle is
compatible with a specified consumer convention. A resolved measure can have
unknown readiness; an unavailable NWC level can prevent use even when D&A
expense basis is established. Neither result overwrites the other. Existing
`HistoricalMetricResult`, standardized availability and
`OperatingNWCReadinessResult.is_ready` retain their present meanings.

Assess exact CIK, selected annual accession/start/end, continuing/consolidated
business perimeter and consumer convention. Delta-NWC includes its own opening
and closing selected-filing identities, with a compatible opening date at the
annual boundary; do not substitute later restatements or force adjacent fiscal
labels to mean matching periods. Retain the two source levels, not just a delta.
Year length alone cannot establish or destroy comparability. Scope/perimeter
changes need an explicit reviewed bridge, never a residual or inferred zero.

## Basis evidence and acceptance criteria

Keep **economic basis** separate from **presentation/source kind**:

| Proposed economic-basis conclusion | Minimum evidence |
| --- | --- |
| `INCOME_EXPENSE` | Selected annual operating statement and asset/expense notes prove qualifying recurring PP&E/finite-lived operating-intangible expense recognized in operating income, including software once and demonstrated expense reductions. |
| `GENERATED_ASSET_COST` | Exact-period evidence proves the asset-consumption amount generated, including capitalization/deferral treatment and incentive basis. Identifying this basis does not approve replacing the expense primitive. |
| `OTHER_EXPLICIT_BASIS` | A reproducible, precisely defined reported basis with exclusions and reviewed bridge. It is not usable through a generic fallback or automatically compatible. |
| `UNKNOWN` | Basis is not proved, even if value, QName, dates or cash-flow placement are known. No numerical agreement, policy name or source kind upgrades it. |

Record operating statement/cash-flow/note placement independently. A cash-flow
add-back whose underlying timing is unbridged is `UNKNOWN` economic basis,
not automatically generated cost or expense. Multiple placements may confirm
one fact. Visa's combined operating expense also appearing in cash flow does
not create two operands.

Joint acceptance requires **all** of the following, with each gate evidenced:

1. Usable exact-period EBIT and D&A, exact USD, matching economic scope, valid
   source identity and approved operand selection. Preserve each concept,
   original occurrence and sign; exclude overlapping support from arithmetic.
2. Exhaustive recurring operating D&A coverage, with positive evidence for
   asset/category separation, software, impairment/accretion, lease treatment,
   preproduction and incentive inclusion/exclusion where relevant. Do not
   impose manufacturing exposure on unrelated issuers or infer zero from silence.
3. An explicit link between the identified D&A basis and the expense already
   reducing this EBIT. Show direct expense, current capitalization/closing
   deferral and opening inventory releases when relevant. Net PP&E movement,
   total inventory movement and numerical residuals do not prove allocation.
4. Approved Operating-NWC perimeter, usable book levels and delta, matching
   policy/version/formula/ordered components, unit and actual dates. Prove the
   corresponding inventory and other noncash timing treatment is consistent
   with the chosen D&A/EBIT convention. Omitting inventory from a perimeter is
   not proof of no inventory economics or neutral omission.
5. Evidence that qualifying costs/incentive reductions are counted once across
   EBIT, D&A and NWC. Where Capex/tax/incentive treatment affects that conclusion,
   retain its approved convention and evidence too; unknown interactions block
   this gate. No double subtraction of an already-net incentive or inclusion of
   a grant receivable as depreciation. No isolated lease adjustment.

Income-expensed D&A plus unadjusted book inventory change is **not automatically
compatible**: noncash depreciation retained in inventory can remain in the
apparent investment deduction. Generated cost plus an expense-adjusted inventory
movement can instead add it twice. These are conditional mechanisms, not evidence
of a nonzero mismatch for every issuer. Acceptance may prove that a mechanism
does not affect a particular approved perimeter, but must not assume that away.
No period-wide cash bridge follows from a D&A basis label alone.

This gate covers timing compatibility, **not full FCFF/DCF readiness**. Tax,
Capex, forecast, lease/debt, WACC and other prerequisites still have their own
contracts. A ready timing bundle cannot authorize an unapproved primitive or
economic adjustment.

## Proposed readiness states and conservative evaluation

| Design state | Meaning / consumer action |
| --- | --- |
| `READY` | Every required timing/scope gate passes under the identified consumer convention; may proceed only to the remaining independent valuation checks. |
| `UNKNOWN_COMPATIBILITY` | Required basis/bridge evidence is absent or incomplete; no demonstrated contradiction. No automatic FCFF consumption. |
| `INCOMPATIBLE` | Valid, exact-scope evidence demonstrates a contrary basis, overlap or timing mismatch under this convention. Preserve the proof; do not invalidate or alter normalized historical values. |
| `AMBIGUOUS_EVIDENCE` | Competing usable inputs or contradictory reviewed bridges have no approved selection. Preserve all alternatives; do not choose by numerical closeness. |
| `INPUT_UNAVAILABLE` | A required historical value/level/perimeter is missing, unsupported, methodology-blocked or not usable for this bundle. No partial calculation or fabricated zero. |

Validate structure first: broken identity/context/unit links, malformed/nil
numeric evidence, inconsistent digests or impossible date order are evaluation
errors, **not economic incompatibility**. Preserve diagnostic inputs and reject
the evaluation; never emit `READY`. Evaluate every applicable gate and keep
ordered reasons rather than silently short-circuiting evidence collection.
For structurally valid bundles, select the summary deterministically:
proved `INCOMPATIBLE`, then `AMBIGUOUS_EVIDENCE`, then `INPUT_UNAVAILABLE`, then
`UNKNOWN_COMPATIBILITY`, otherwise `READY`. Incompatibility requires valid proof
even when another input is unavailable; missing evidence alone cannot produce
it. Keep additional unavailable/unknown reasons with the summary.
No waiver based on coverage, insignificant values or unproved materiality.

## Current-policy mapping — documentation, not new runtime output

| Family / exact entry | D&A economic basis from retained audit | Joint compatibility / gate disposition with current inputs |
| --- | --- | --- |
| Generic `D_AND_A_POLICY` / `DepreciationDepletionAndAmortization` | `UNKNOWN` at policy-family level; individual periods require review | Unproved; `UNKNOWN_COMPATIBILITY` if usable bundle otherwise exists, or `INPUT_UNAVAILABLE` for missing prerequisites. No blanket incompatible classification. |
| `msft_annual_d_and_a_v1`, CIK 789019 | `UNKNOWN`; the approved two-component addition is preserved | Unproved; current MSFT NWC trade-AP methodology blocker prevents a usable level (`INPUT_UNAVAILABLE`), independently of unknown D&A basis. |
| Visa `d_and_a_scope_equivalence` v1, `0001403161-21-000060`, 2020-10-01–2021-09-30 | `INCOME_EXPENSE` | Unproved; no configured Visa NWC valuation perimeter (`INPUT_UNAVAILABLE`). |
| Visa v1, `0001403161-22-000081`, 2021-10-01–2022-09-30 | `INCOME_EXPENSE` | Same unproved joint compatibility; no NWC perimeter. |
| Visa v1, `0001403161-23-000099`, 2022-10-01–2023-09-30 | `INCOME_EXPENSE` | Same unproved joint compatibility; no NWC perimeter. |
| Visa v1, `0001403161-24-000058`, 2023-10-01–2024-09-30 | `INCOME_EXPENSE` | Same unproved joint compatibility; no NWC perimeter. |
| Visa v1, `0001403161-25-000089`, 2024-10-01–2025-09-30 | `INCOME_EXPENSE` | Same unproved joint compatibility; no NWC perimeter. Rounded note corroboration does not replace the exact combined value. |

All five Visa rows have the same CIK 1403161 and policy/version; registry
identities and evidence remain in the [scope design](depreciation-amortization-scope-evidence-design.md)
and [source registry](../src/valuation_platform/normalization/d_and_a_scope_registry.json).
No existing integrated bundle is certified by this mapping. The
[audit](depreciation-amortization-timing-audit.md#inventory-and-nwc-consumers--complete-implemented-perimeter-coverage)
also reconciles META v1/v2 (no inventory entry), GOOGL v1 (inventory blocker),
MSFT/AAPL v1 (required inventory with other blockers), and COST v1 (required
book inventory). META/COST NWC readiness does not establish joint timing
readiness; TXN's three unapproved proposals remain outside approved mapping.

## Provenance, validation and adjustment boundary

Future evaluation must retain immutable, versioned consumer-convention identity;
exact input/filing/period/perimeter references; basis conclusion and its reviewed
scope; reviewer/date/rationale and artifact URL/location/digest; all confirming
and competing occurrences; raw value, exact Decimal, submitted precision, unit,
dimensions, nil status, context/entity and ordinal identity where available;
operand/exclusion decisions, every gate/reason and supported calculations.
Company Facts evidence remains distinct from richer filing-XBRL occurrences;
never synthesize absent context/ordinal metadata. Scope conclusions need traceable
source evidence, not merely a comment on a policy family.

Both NWC levels and their existing source contributions must remain referenceable.
Record opening-period evidence separately from current selected-filing operands;
do not demand the opening filing be the current accession or silently substitute
restated comparatives. Future serialization must preserve enum meanings,
versions, exact Decimal strings, deterministic gate/occurrence order and all
proof references; reconstruction must revalidate identity, digests, scope,
perimeter and arithmetic. These are design requirements, **not a schema change**.

**No new economic adjustment is approved.** Identity checks, source selection
under existing approved policies and existing book-level/delta arithmetic are
supported; they are not new timing corrections. Inventory D&A allocations,
incentive netting/gross-ups or alternate generated-cost inputs require a separate
exact-period, evidence-backed, versioned methodology approval and impact review.
If later approved, retain original normalized values and produce separately
identified consumer inputs with signed reconciliation, no overlap, exact
coefficients and explicit precision treatment. Residuals, absence-derived zeros
and generic tolerances are forbidden. This design alone cannot authorize them.

## Meaningful future tests — specified, not executed

| Scenario | Required outcome |
| --- | --- |
| Resolved generic/MSFT value but absent basis proof | Value stays resolved; `UNKNOWN_COMPATIBILITY` for an otherwise usable bundle. |
| Each of the five Visa identities | Expense basis retained; missing NWC perimeter yields `INPUT_UNAVAILABLE`, not `READY` or `INCOMPATIBLE`. |
| Synthetic fully evidenced same-scope expense/book-NWC bundle with every gate proved | `READY` for this timing contract only; no automatic tax/Capex/DCF readiness. |
| Positive exact-period proof of noncash inventory timing mismatch under the requested convention | `INCOMPATIBLE`; retain the mismatch and original historical values. No real issuer allocation is invented by this synthetic fixture. |
| Inventory movement known but D&A allocation unknown; policy omits inventory; cash-flow placement alone | No inferred allocation/zero/generated basis; unresolved applicable gates remain unknown. |
| MSFT/GOOGL/AAPL NWC methodology blocker; missing opening level | `INPUT_UNAVAILABLE`, even with established D&A expense basis. |
| Conflicting valid basis/bridge evidence or ambiguous required value | `AMBIGUOUS_EVIDENCE`; preserve candidates, unless valid incompatibility proof takes summary precedence. |
| Broken accession/CIK/annual dates, unit/context/digest/nil linkage | Structural evaluation error; never incompatible merely because malformed. |
| Different NWC policy/version/perimeter or reversed dates | Reject structural bundle; do not calculate an apparent movement. |
| Already-net incentive, duplicated support fact, or repeated equal occurrences | Do not adjust or add support twice; retain confirming occurrences once per economic operand. Unproved netting cannot pass. |
| Historical resolved/unknown serialized and reconstructed; input order permutations | Preserve historical status, exact evidence/Decimal/versions and deterministic canonical reasons; no readiness upgrade on round-trip. |
| Independent manual forecast ratios without an approved joint convention | Historical resolution does not certify forecast timing; future consumer requires separate convention/assumption consistency evidence. |

## Bounded next milestone and unchanged production

With this valuation contract designed and its freeze limitation documented,
resume the existing Phase 1H.4 historical work: **exact selected-filing Capex
concept inventory for the 57 missing periods recorded in the
[failure taxonomy](universe/sp500-top-50-failure-taxonomy.md)**. Freeze those
identities before research; no policy expansion or timing evaluator in that
milestone. D&A unknowns remain documented exclusions, not a reason to force
coverage or repeat the completed TXN/audit work. This is the single next
milestone; implementing this gate waits until after 1H.6.

Validate all three family mappings/five Visa identities, consistency of states
and acceptance rules, source/model references, phase placement, local links
and `git diff --check`. No source/schema/policy/test/research-inventory/corpus
changes, SEC requests, tests or corpus rerun. Counts are carried forward:
D&A **115/89/0**, aggregate **1,885/1,503/11/27/42 = 3,468**, all approvals,
43 generic completions and seven specialized skips preserved.
