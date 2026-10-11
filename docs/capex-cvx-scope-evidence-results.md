# CVX curated Capex v2 implementation and validation

Phase 1H.4 Wave 32 implements the [reviewed acceptance contract](capex-cvx-scope-evidence-design.md)
from starting HEAD `2c1422bff31e0d4c2f2676d670d6f22b986ec09a`.
Only the five exact CVX filings are added. No generic fallback, mineral/lease
adjustment equation, new primitive, or integrated FCFF-readiness approval.

## Published policy and provenance

[`capex_scope.py`](../src/valuation_platform/normalization/capex_scope.py)
publishes disjoint immutable `capex_scope_equivalence` versions: v1 retains
exactly ten AMZN/LLY entries and its default API; v2 contains exactly five CVX
entries in a [separate runtime registry](../src/valuation_platform/normalization/capex_scope_v2_registry.json).
The historical and corpus composition layers dispatch by exact selected-filing
and authoritative annual-period identity, not latest version or ticker default.
Unpublished versions, altered entries and overlapping catalog registrations fail.
The frozen [design matrix](capex-cvx-scope-evidence-matrix.json) remains research
history, not an executable approval flag. The v1 registry bytes and canonical
reviewed-entry hashes remain unchanged, including AMZN refresh and LLY
representation-correction provenance.

All 56 mandatory raw response-body digests were verified across the five
selected instances, submitted structures and reviewed statements/notes. The
selected instance is re-parsed and compared to supplied facts, contexts and
units. Raw bytes are never replaced by parsed equality. Discovery-only index,
calculation and label fingerprints do not become verified scope evidence; no
v1 mandatory artifact is removed. Existing retained bodies were reused without
refreshing fingerprints or inventing original retrieval metadata.

The resolver retains every confirming occurrence in document order, both the
original zero-based instance ordinal and one-based confirming ordinal, raw
value, exact Decimal, decimals, context/entity/period/dimensions and unit.
Scope-support/exclusion occurrences and reviewed statement/note assertions
remain audit evidence, not summed operands or numeric adjustment requirements.
Equivalent context/unit IDs or raw representations may confirm only one exact
eligible semantic value; eligible differing values stay ambiguous. Direct
ambiguity is never repaired; equal direct facts retain their chosen source,
and differing eligible direct/curated values remain ambiguous. Invalid links,
nil contradictions and source/accession inconsistencies are data errors;
future, amended, unregistered and incomplete approvals cannot resolve.
Dimensioned collisions cannot poison the nondimensional approved result.
Schema 5 retains the complete versioned review, typed digest manifest and
ordered occurrence audit, and validates provenance against its published
version. No downstream FCFF consumer is introduced or certified.

## Exact results

All dates are January 1–December 31 of the stated year, CIK `93410`, exact USD,
nondimensional `us-gaap:PaymentsToAcquireOilAndGasPropertyAndEquipment`.

| Year | Selected accession | Resolved USD | Original ordinal |
| --- | --- | ---: | ---: |
| 2021 | `0000093410-22-000019` | 7515000000 | 714 |
| 2022 | `0000093410-23-000009` | 10349000000 | 698 |
| 2023 | `0000093410-24-000013` | 14788000000 | 723 |
| 2024 | `0000093410-25-000009` | 15544000000 | 736 |
| 2025 | `0000093410-26-000078` | 16830000000 | 753 |

| Cohort / state | Verified result |
| --- | --- |
| Frozen Capex inventory | 57 exact identities = five CVX v2 + ten unchanged v1 + 42 unchanged missing controls |
| Existing direct Capex | All 147 normalized results unchanged, including values, chosen sources and provenance |
| Capex | 157/47/0 → **162 resolved / 42 missing / 0 ambiguous** |
| Aggregate | 1,895/1,493/11/27/42 → **1,900/1,488/11/27/42**, total **3,468** |
| Other measures | All issuer-level standardized measure states unchanged; 1,627 normalized metric results unchanged |
| Execution | 43/43 generic issuers completed; zero failures; seven specialized skips unchanged; 204 annual periods |

The 42 controls are unapproved, not freshly reviewed denials: 22 concept-policy,
17 derivation and three methodology-blocker research routes. Their production
states remain missing; no new blocker or incompatibility enum is inferred.

## Validation record

Focused tests: **31 passed**; complete suite: **583 passed**. These were already
complete before resumption and were not repeated because production/test code
was unchanged. The focused suite includes exact publication, v1 canonical hash
preservation, all 57 identities, duplicate/conflict and exclusion adversaries,
nil/structural errors, direct precedence and schema-5 provenance/serialization.
Five targeted selected-filing checks passed with 67 retained resources reused
and zero new SEC requests; all five original occurrence ordinals reconciled.

The first corpus attempt was blocked by SEC DNS inside the restricted sandbox,
not a normalization acceptance failure. On resumption, one bounded supported-
permission check resolved both SEC hosts and returned HTTP 200. One corpus gate
then passed using the existing validation runner: 404 retained resources reused
and 297 SEC requests. It compares complete normalized results with v2 evidence
disabled but v1 evidence retained, and reconciles all issuer-level standardized
states and execution metadata to the Wave 28 baseline. Exactly the five frozen
CVX missing-to-resolved differences occurred. No new cache system or weaker
acceptance rule was introduced. Logs and corpus artifact remain under `/tmp`
(`capex-wave32-corpus-resumed.log`, `capex-wave32-corpus.json`); they are not
runtime dependencies. `compileall` and `git diff --check` passed.

## Next bounded milestone

Documentation-only component-completeness and cash/asset-scope research for the
five frozen NVDA Capex periods in the [inventory](capex-inventory.json): determine
whether selected-filing evidence supplies an exhaustive PP&E-only cash split
from reported combined PP&E/intangible purchases. Keep the first two issuer
extensions separately gated. Do not approve a residual, missing-as-zero,
generic productive-assets fallback, or equation based only on matching totals.
All other gaps and valuation-boundary readiness stay outside that pass.
