# Visa curated Capex v3 implementation results

Phase 1H.4 Wave 38; implementation baseline
`fc1feaa409ed7aa720cb7e030a4becdf9d71189a`. This completes the
[exact-accession design](capex-visa-scope-evidence-design.md) and its frozen
[acceptance matrix](capex-visa-scope-evidence-matrix.json), without expanding
the Capex primitive or approving a generic fallback or adjustment equation.

## Published policy and evidence

The published catalog adds immutable `capex_scope_equivalence_v3` alongside
unchanged v1 (ten AMZN/LLY entries) and v2 (five CVX entries). Visa CIK 1403161
has exactly five entries for `us-gaap:PaymentsToAcquireProductiveAssets`.
CIK, accession, nonamended 10-K, report date, authoritative annual start/end,
namespace/concept, nondimensional scope, exact USD and expected Decimal value
must match. Future/unregistered/amended filings receive no approval.

Each entry requires thirteen original-response artifacts and seven reviewed
scope records: 65 artifacts and 35 entry-associated reviews across the registry.
Typed representations, SHA-256 and byte lengths are verified against the
[retained original bodies](evidence/visa-capex-response-bodies.json), not parsed
equality. No response refresh, fingerprint replacement or historical-fingerprint
promotion occurred. Support/exclusion facts and namespaces remain part of the
canonical reviewed evidence; scope completeness is not inferred from arithmetic.

Missing/incomplete verification cannot produce a curated result; corrupt bytes,
inconsistent metadata, broken context/unit links and contradictory nil/numeric
evidence are structural errors. Dimensioned, wrong-period/entity/concept and
non-USD occurrences are ineligible. Equivalent eligible occurrences confirm
one signature, preserving deterministic occurrence ordinals, original context/
unit IDs, raw values and decimals. Different eligible values remain ambiguous.
An equal approved direct result remains selected and may retain confirmation;
conflicting evidence is not hidden by precedence.

Schema 5 retains policy ID/version, canonical entry, all reviews and typed artifact
digests, ordered confirming occurrences, and support/exclusion provenance through
normalization, standardized output and serialization. Unknown versions, altered
or incomplete audits and reordered occurrence evidence fail validation. There
is no schema, generic policy, parser, economic definition or FCFF consumer change.

## Targeted retained-accession validation

All five exact annual periods resolve using retained originals and existing
selected-filing artifacts: 75 resource reuses, zero new SEC requests. This gate
uses filing-only observations, not an invented Company Facts observation; the
subsequent full corpus exercises normal production retrieval and dispatch.

| Accession | Authoritative annual period | Capex USD | Original occurrence ordinal |
| --- | --- | ---: | ---: |
| 0001403161-21-000060 | 2020-10-01–2021-09-30 | 705,000,000 | 547 |
| 0001403161-22-000081 | 2021-10-01–2022-09-30 | 970,000,000 | 556 |
| 0001403161-23-000099 | 2022-10-01–2023-09-30 | 1,059,000,000 | 541 |
| 0001403161-24-000058 | 2023-10-01–2024-09-30 | 1,257,000,000 | 516 |
| 0001403161-25-000089 | 2024-10-01–2025-09-30 | 1,482,000,000 | 546 |

## Validation and reconciliation

- Focused v1/v2/v3 policy, evidence, integration and serialization tests: **47 passed**.
- Complete suite, run once after focused/targeted gates: **599 passed** (583 + 16).
- Original 57 inventory identities: **five Visa resolved / fifteen prior approvals unchanged / 37 controls unchanged**. Controls remain unapproved, not freshly reviewed denials.
- All **147 direct results** and all fifteen old curated results are unchanged, including normalized provenance. Old registry bytes and canonical entry fingerprints are preserved.
- One corpus run: **43/43 generic issuers completed**, zero failures, seven specialized skips; **204 annual periods**, **3,468 states**.
- Capex: **162/42/0 → 167/37/0**. Aggregate: **1,900/1,488/11/27/42 → 1,905/1,483/11/27/42** (resolved/missing/ambiguous/methodology-blocked/not-comparable).
- Exactly five Visa Capex missing→resolved changes; all other measure statuses, 1,627 other normalized metric objects, issuer completion and selected-period identities are unchanged.
- The existing corpus runner reused 469 resources and made 297 SEC requests. Same-input normalization with only v3 evidence removed and the retained Wave 32 corpus independently establish preservation; no acceptance rules were weakened.

Detailed validation outputs remain outside the repository:
`/tmp/capex-wave38-focused.log`, `/tmp/capex-wave38-targeted.log`,
`/tmp/capex-wave38-full-tests.log`, `/tmp/capex-wave38-corpus-validation.log`,
and `/tmp/capex-wave38-corpus.json`. `compileall`, relevant local documentation
links, frozen inventory/matrix/evidence preservation and `git diff --check` passed.

## Next bounded milestone

Documentation-only exact selected-filing cash PP&E scope research for the five
frozen QCOM Capex periods. The 37 remaining controls comprise 17 concept-policy,
17 derivation and three methodology-blocker periods; no additional coverage is
approved here. Preserve current production and existing timing-readiness boundaries.
