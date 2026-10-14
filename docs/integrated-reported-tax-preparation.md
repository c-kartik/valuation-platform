# Integrated reported-tax preparation and review

Phase 1 only; no phase closure, coverage-shortfall acceptance or valuation use.
This supersedes the separate-delivery limitation in
[prior replay results](retained-reported-tax-context-results.md).

## Delivery and coverage

All 199 selected annuals / 42 non-specialized histories now contain separately
identified provision, continuing-operations Pretax and reported ETR inputs. Eleven
target-history deficits persist; XOM has no fabricated annual and GEV/SNDK have
two each. [Exact source/policy ledger](retained-reported-tax-context-ledger.json)
and [assembly summary](prepared-assembly-summary.json) replay offline.

| Component | Populated | Conflicting | Unavailable | Unit / origin |
|---|---:|---:|---:|---|
| Provision/benefit | 186 | 13 | 0 | USD / reported |
| Pretax | 162 | 0 | 37 | USD / reported, including eight existing curated approvals |
| Reported ETR | 154 | 13 | 32 | pure / existing-policy derived |

Conflicting and unavailable populations stay null with alternatives, reasons and
source requirements. All three are partial reported-tax **context**, not complete
operating-tax consumer inputs. Provision is not cash tax or deferred-tax CFO
reconciliation. Original four pilot cash-tax observations remain distinct. Other
cash-tax disclosures have not been searched or implicitly declared available.
No suggested rate, clamp, tax shield, proxy or analyst-adjusted ratio is created.

Field-family availability is 194 periods, not the sum of the three component
counts. Valued inputs 506 include four unchanged pilot cash-tax observations.
All 199 tax families still have unresolved scope/consumer requirements. Complete
field coverage remains zero; proposed 90%/80% targets are unchanged/unaccepted.

## MA: a demonstrated retained metadata join repair

The three formerly blocked MA entries already had filing metadata in the retained
D&A research inventory. The prior adapter consulted only income metadata and
Capex registrations. This is a join defect, not unavailable SEC disclosure.

| Exact accession | Annual period | Filed | Primary document | Sealed inventory row |
|---|---|---|---|---|
| 0001141391-22-000023 | 2021-01-01 → 2021-12-31 | 2022-02-11 | ma-20211231.htm | rows/40/filing |
| 0001141391-23-000020 | 2022-01-01 → 2022-12-31 | 2023-02-14 | ma-20221231.htm | rows/41/filing |
| 0001141391-24-000022 | 2023-01-01 → 2023-12-31 | 2024-02-13 | ma-20231231.htm | rows/42/filing |

[Verified identity manifest](phase1-selected-filing-identity-manifest.json) seals
[the inventory](depreciation-amortization-inventory.json) with SHA-256
`ad63ce09cdc3b1efeb04a3cde56f9afb4107e96789fc56b63b539835b34ad2a8`.
The adapter verifies exact row/CIK/accession/form/annual dates, original instance
URL/digest, filing metadata and registered primary-document identity. It replays
annual DEI and the unchanged scope policy. Ledger provenance retains the exact
metadata reference, seal and original reviewed evidence. All three original
requirements succeed, adding three Pretax and three ETR values. No request, new
receipt, recovered-original claim, changed approval or financial fallback.

## Representation and compatibility

The existing immutable models gain only a constrained `pure` tax role and an
`existing_reported_effective_tax_rate` formula descriptor for
`annual_reported_effective_tax_rate_v1`, version 1. It binds the original reported
USD provision/Pretax IDs and monetary source evidence. Materialization copies the
existing resolver result; it does not execute a new equation. A ratio cannot be
reported-direct, a proxy, a generic subtotal or a numerical override.

Assemblies use `assembled-historical-input-review-v2`, attaching the original tax
overlay and proof. Legacy v1 assembly decoding/serialization remains supported
against its exact source revision. Generic histories containing a pure ratio use
`historical-input-preparation-v3`; unchanged v1 histories keep their original bytes.
LLY refreshed-evidence v2 wrappers and frozen schema 5 are not migrated. Exact
tax replay on deserialization prevents changed amounts, evidence or proof from
populating accepted inputs.

Superseded pilot provision duplicates and generic tax placeholders remain in the
attached original history, not duplicate active warnings. Their active replacement
is the verified provision component, while cash-tax inputs are copied unchanged.
Non-tax inputs, policies, registries, evidence and all seven D&A negative reviews
are untouched. Intentional ratio/operand source reuse is dependency provenance,
not an independent overlapping monetary population; actual other overlaps remain.

## Review, audit and dependency behavior

Stable targets include issuer, exact annual/accession, tax family, channel and
component ID. One field primary nests distinct provision/Pretax/ETR causes and
alternatives. No field-level ambiguous target can silently supply an aggregate.
Relevant revisions include monetary sources, candidates, scope, precision, policy
proof and both ratio operands; transport timestamps alone do not stale decisions.
Superseded old tax targets/audits are retained, but cannot apply automatically to
new populations. Explicit revalidation is required for changed revisions.

Existing local immutable audit/overlay persistence is reused. Provision/Pretax
decisions remain analyst-origin patches with displaced originals. Any applied
operand override, even numerically equal, flags the **same-period** source ratio
as dependent. `inspection_payload()` retains the original ETR and displays the
effective ratio as null, `DEPENDENT_ETR_INVALIDATED`, without an effective formula.
No adjusted ratio is calculated. Other periods' source ratios remain unchanged.
Source ETR itself is read-only to numerical overrides; acknowledgment cannot fill
a missing result. Stale patches do not apply; explicit revalidation can restore
only the patch, not certify or recalculate ETR. No real analyst assumption is added.

## Validation and finite stopping point

Focused tests cover assembly/closed round trips, legacy versions, exact MA joins,
sealed-source rejection, stable component targets, grouped-cause reachability,
conflicts/nulls, local persistence/restart, period-qualified invalidation, stale
rejection/revalidation and original pilot/frozen/non-tax preservation. Existing
independent checks retain 119 CHECKED / zero FAILED / one NOT_VERIFIED (CVX EBIT).
No SEC requests, full-suite or corpus rerun.

Verified **76 distinct focused tests pass**: 74 model/assembly/tax/review/audit/
workflow regressions plus export-tamper and tax-proof revision checks. Constrained
ratio unit/scale/expression guards also pass. Compileall, affected local links and
`git diff --check` pass. All original non-tax ledger bytes and frozen artifacts are
pinned; original pilot serializer SHA-256s remain unchanged.

Current queue: 2,786 field-family primary items / 8,247 nested actionable causes /
18,012 annual diagnostics, plus three history cards (eleven target deficits).
Latest view: 574 primaries / 1,691 actionable / 3,612 annual diagnostics. All eight
invalid-evidence locations remain reachable. Grouped actionable counts fall by 68
because real tax gaps gain verified values, not because diagnostics are discarded;
new component/source-detail diagnostics remain reachable. Coverage does not imply
complete cash-tax, operating-tax or future-consumer approval.

Remaining decisions are finite, not a research queue:

1. Review/accept or reject reported-input coverage shortfalls under a named
   delivery contract; component availability is not complete input sufficiency.
2. Disposition the thirteen provision conflicts and 37 missing approved Pretax
   scopes as explicit limitations or separately authorized exact repairs. No
   silent precedence or generic fallback is permitted here.
3. Decide the independent validation sample/acceptance scope for any preparation
   closure; the current spot checks do not certify whole histories or FCFF use.
4. An analyst-adjusted ratio or operating/forecast-tax treatment would require a
   separately identified future derivation/method contract; none is approved now.

Stop after this integration. Phase 1 remains open; financial sufficiency remains
NOT_ASSESSED and Phase 2 is postponed.
