# Curated Operating Income derivation-policy design

## Scope and decision

Phase 1H.4 Wave 15 designs, but does not implement, the production boundary for
the 25 exact LLY, JNJ, MRK, KLAC, and IBM derivations approved by the
[Wave 14 evidence review](operating-income-derivation-design.md). The decision
is **PARTIAL GO**:

- **GO** for a later immutable, versioned, exact-accession policy containing
  only the 25 reviewed entries below;
- **NO-GO** for a generic component-expression engine, issuer-wide or
  concept-name fallback, future or amended filing inheritance, inferred zero,
  or automatic tolerance-based normalization; and
- **NO-GO** for CVX and GE. Their ten periods are negative regression controls,
  not policy entries.

The proposed stable identity is policy ID
`operating_income_component_derivation` and version `1`, serialized as
`operating_income_component_derivation_v1`. This wave changes no source code,
test, production policy, or corpus result. Operating Income therefore remains
169 resolved / 35 missing / 0 ambiguous.

## Immutable policy and evidence model

Implementation should add frozen value objects rather than extend the generic
`MetricDerivationPolicy` into a general expression language:

1. `OperatingIncomeDerivationPolicy`
   - `policy_id`, `version`, `metric`, `economic_scope`, `entries`, and
     `reviewed_evidence`;
   - rejects a duplicate entry identity, duplicate evidence ID, mutable
     container, unsupported version, or any metric other than Operating Income;
   - owns one immutable tuple of exactly 25 entries in version 1.
2. `OperatingIncomeDerivationEntry`
   - exact normalized CIK, accession, form `10-K`, report date, authoritative
     annual start/end, formula ID, perimeter ID, expected derived `Decimal`,
     ordered calculation terms, ordered validation terms, reviewed alternate
     occurrences, and reviewed-evidence IDs;
   - identity is `(policy_id, version, cik, accession, report_date,
     annual_start, annual_end)`; accession matching is exact after the existing
     hyphen-normalization convention, never prefix- or issuer-year-based;
   - rejects an amended form, duplicate term ordinal or operand ID, a
     coefficient other than exact `Decimal("1")` or `Decimal("-1")`, an operand
     reused in two calculation terms, a validation term presented as an output
     term, or a non-USD output.
3. `OperatingIncomeOperandDefinition`
   - ordinal, stable operand ID, economic role, source kind, exact taxonomy URI
     or approved taxonomy identity, namespace, concept, annual start/end,
     empty-dimension requirement, normalized unit `USD`, exact expected
     `Decimal`, coefficient, required/explicitly-absent state, and evidence IDs;
   - version 1 calculation operands are exact filing-XBRL facts. Company Facts
     may be retained as corroboration when present, but cannot substitute for
     a registered filing-XBRL operand or authorize an issuer extension;
   - an explicitly absent row is a reviewed completeness assertion, not a
     numeric operand and never an inferred zero.
4. `OperatingIncomeOperandEvidence`
   - the matched definition plus every confirming filing-XBRL occurrence in
     deterministic document order, each with an occurrence ordinal, namespace,
     concept, raw value, exact numeric value, context ID, normalized entity and
     period, dimensions, unit ID, normalized unit, decimals, nil status,
     accession, source URL, filing metadata, and retrieval time;
   - separately retains every registered nonselected alternate occurrence and
     the reviewed reason it is not the face-statement operand.
5. `OperatingIncomeDerivationPolicyProvenance`
   - policy ID/version, entry identity, formula/perimeter IDs, reviewed evidence,
     ordered operand definitions and evidence, exact signed contributions,
     calculated value, and validation results;
   - validation results preserve reported and recalculated Gross Profit where
     applicable, reported Pretax, calculated Pretax, exact signed variance,
     display scale, and whether the entry-specific validation gate passed.

The existing `ReviewedPolicyEvidence` shape is reusable: each entry must retain
stable evidence ID, direct SEC URL, filing location, research artifact,
review date, approved classification, rationale, and content digest. The Wave
14 instance, face-statement, calculation-linkbase, and relevant note links are
the required evidence set; a documentation path alone is not sufficient.

## Exact source selection

The resolver remains pure and network-free. It receives the selected filing,
authoritative annual-period result, parsed filing-XBRL, and any Company Facts
already supplied by orchestration. It performs no discovery or retrieval.

Selection proceeds in this order:

1. Normalize and match exact CIK, accession, form, report date, annual start,
   and annual end to one active registry entry. No match means no derivation.
2. For every required operand, inspect only the registered namespace/taxonomy
   and concept in the selected filing. Require the selected registrant entity,
   exact annual dates, empty dimensions, non-nil numeric content, and a unit
   that normalizes to exact USD.
3. Match the registered exact `Decimal` value. This is deterministic execution
   of reviewed evidence, not a value-discovery heuristic. An expected value is
   never synthesized from Pretax or another residual.
4. Account for every same-concept, same-entity, same-period nondimensional USD
   occurrence. A differing value may be ignored only if its complete signature
   is explicitly registered as a reviewed nonselected representation, such as
   LLY's less-precise acquired-IPR&D note/cash-flow occurrences. An unexpected
   differing occurrence remains ambiguity.
5. Company Facts can confirm an exact registered standard fact when its CIK,
   accession, annual dates, taxonomy, concept, unit, and value agree. It neither
   overrides filing-XBRL nor fills a missing filing-XBRL operand in version 1.
6. After every calculation and validation operand is satisfied, calculate in
   declared ordinal order. No concept precedence, size test, residual, label
   match, calculation-tree search, or cross-accession fallback is permitted.

This boundary deliberately differs from the generic historical resolver. It
executes reviewed equations whose completeness depends on the exact face
statement and submitted calculation tree; it does not discover new equations.

## Equivalent occurrences and conflicts

After curated eligibility filtering, occurrences confirm one operand only when
they share this semantic signature:

`(namespace/taxonomy, concept, normalized CIK, accession, authoritative annual
start, authoritative annual end, empty dimensions, normalized exact-USD unit,
exact numeric Decimal, non-nil status)`.

Different context IDs may confirm when their normalized entity, period, and
empty-dimensional scope agree. Different unit IDs may confirm only when both
normalize to exact USD. Different raw strings or decimals attributes may
confirm only when they normalize to the same exact `Decimal`. All original
representations and deterministic occurrence ordinals remain in provenance.

Different numeric values never collapse. LLY's reviewed lower-precision
acquired-IPR&D occurrences are not equivalent duplicates: they must be listed
as exact nonselected evidence in their entry and preserved with the reason
`REVIEWED_NON_FACE_PRECISION`. Any additional unregistered value makes the
operand ambiguous. Dimensioned occurrences are excluded and cannot conflict
with a valid nondimensional operand, but they remain available in source-level
evidence. A nil/numeric collision, broken or missing context link, inconsistent
entity/accession/source metadata, or malformed unit is a structural data error.

## Arithmetic without a general expression engine

Each entry contains one ordered tuple of signed terms. The resolver computes
only `sum(coefficient * exact_operand_value)` under the repository Decimal
context. Parenthesized subtotals are represented by validation terms, not by
nested executable expressions. Formula IDs describe one of the five reviewed
perimeters but do not select concepts or generate terms:

| Formula ID | Ordered Operating Income terms |
|---|---|
| `LLY_OPERATING_PERIMETER_V1` | `+R -C -D -S -A -X` |
| `JNJ_OPERATING_PERIMETER_V1` | `+G -S -D -A -X`; validate `G = R - C` |
| `MRK_OPERATING_PERIMETER_V1` | `+R -C -S -D -X` |
| `KLAC_OPERATING_PERIMETER_V1` | `+R -C -D -S` and `-I` only when the exact entry registers the reported impairment row |
| `IBM_OPERATING_PERIMETER_V1` | `+G -S -D +A`; validate `G = R - C` |

Absent KLAC rows are entry metadata proving that the exact submitted face and
calculation tree omitted the row. They do not create a zero operand. Each term
must consume a distinct registered fact role; duplicate concept use, duplicate
occurrence consumption, or an unregistered extra operating row is a policy
configuration or evidence error, never an arithmetic shortcut.

Every entry also has an independently evaluated Pretax bridge using the exact
reported non-operating operands and reported Pretax fact reviewed in Wave 14:

- LLY and MRK: `Pretax = OI + signed N`;
- JNJ: `Pretax = OI + H - E + signed N`;
- KLAC: `Pretax = OI - E + signed L + signed N`, with `L` present only where
  the exact entry registers it; and
- IBM: `Pretax = OI - signed N - E`.

The bridge validates the registered equation. It never supplies, adjusts, or
replaces the Operating Income value.

## Direct-result precedence and coexistence

The unchanged generic `OPERATING_INCOME_POLICY` runs first.

- A direct ambiguity is final and is never replaced by a derivation.
- If direct Operating Income is missing and one exact registry entry resolves,
  return one policy-approved derived Operating Income result.
- If a direct value resolves and no complete registered derivation resolves,
  return the direct result unchanged.
- If both resolve to the same exact USD `Decimal` and exact annual period,
  return the direct result as primary and retain the curated derivation as
  confirming supporting-policy provenance.
- If both resolve but values differ, return ambiguity retaining the direct fact
  and complete derived evidence. Policy order must not erase an economic
  conflict.
- An incomplete curated derivation does not invalidate an otherwise valid
  direct result. A structural filing-data error still propagates as an error.

No version 1 entry currently coexists with a direct result; these rules are
required regression boundaries for later filings and policy versions.

## Failure behavior

| Condition | Required behavior |
|---|---|
| Unregistered CIK/accession/period, future filing, or amendment | no derivation; preserve the direct result, normally typed missing |
| Missing required operand or validation fact | no numeric derivation; typed missing with exact operand reason |
| Explicitly absent row is absent as reviewed | continue without a numeric term; do not emit zero provenance |
| Explicitly absent row unexpectedly appears | no derivation until reviewed; typed ambiguity or policy mismatch with occurrence retained |
| Dimensioned candidate plus valid nondimensional fact | exclude dimensioned fact; valid nondimensional fact may resolve |
| Only dimensioned, nil, non-USD, wrong-period, wrong-entity, wrong-concept, or wrong-accession evidence | no derivation; preserve the typed reason |
| Equivalent repeated eligible occurrences | one operand with every occurrence retained in deterministic order |
| Different unregistered eligible values | ambiguous operand and no derivation |
| Registered LLY non-face precision occurrence plus exact approved face occurrence | select the exact approved value; retain the registered alternate and reason |
| Nil/numeric collision, missing/broken context, malformed unit, or inconsistent source/accession metadata | structural data error |
| Operand reused, duplicate ordinal/identity, missing evidence ID, unsupported coefficient, or registry identity collision | policy construction error |
| Pretax or Gross Profit validation outside its exact entry gate | no derivation; retain calculated and reported values and signed variance |

## IBM exact arithmetic and rounding gate

IBM calculations use the exact registered whole-million `Decimal` operands.
The derived Operating Income is never rounded, normalized, plugged, or changed
to make Gross Profit or Pretax reconcile. Provenance preserves the reported
value, recalculated value, signed variance, and the filing display scale of
`1000000` USD.

The version 1 gate is validation-only and entry-specific:

- the selected filing must be one of the five registered IBM accessions;
- every relevant face line must be displayed and tagged in whole millions and
  tied to the submitted calculation relationship reviewed in Wave 14;
- Gross Profit and Pretax differences must each be exactly `0`, `1000000`, or
  `-1000000` USD as registered for that entry; and
- the calculated Operating Income remains the unadjusted signed sum.

There is no percentage tolerance, no general $1 million tolerance, and no
permission to choose an operand or value because it falls within tolerance.
Any other variance fails the entry.

## Provenance, standardized output, and serialization

The derived result must retain `policy_id`, `policy_version`, exact registry
entry identity, formula/perimeter IDs, reviewed evidence, ordered operands,
signed contributions, all confirming and registered-nonselected occurrences,
exact arithmetic, and validation outcomes. The current single-concept
`HistoricalPolicyProvenance` should not be overloaded; implementation should
add a derivation-specific provenance value and allow a normalized direct result
to carry it as supporting confirmation when both paths agree.

Standardized output should expose an immutable policy reference containing the
same fields. Serialization must:

- increment the standardized-output schema version because the policy shape is
  additive but materially new;
- serialize every `Decimal` as an exact string, never a binary float;
- retain operand order, coefficients, occurrence ordinals, context and unit
  IDs, raw values, decimals, nil status, source URLs, exclusions, and evidence
  digests;
- retain IBM reported/calculated bridge values, signed variance, scale, and
  validation-only gate result; and
- round-trip direct-primary/derived-confirming and derived-primary results
  without losing policy identity or evidence.

## Downstream Operating Tax boundary

The current Operating Tax readiness path accepts only direct normalized
Operating Income with the approved `us-gaap:OperatingIncomeLoss` source. A
later implementation may accept a derived Operating Income only when it carries
complete `operating_income_component_derivation_v1` provenance and the active
Operating Tax policy independently matches the same CIK, accession, annual
period, currency, and policy version. It must reject a generic
`DerivedHistoricalValue`, a missing/unknown policy version, a partial operand
set, or stripped serialization.

The Operating Tax readiness result and its serialization must retain the full
Operating Income supporting-policy reference. The curated derivation does not
approve an Operating Tax bridge, tax allocation, or NOPAT result by itself;
all existing tax-regime and bridge gates remain mandatory.

## Frozen positive registry manifest

`Report` equals the selected 10-K report date and the authoritative annual end.
Expected values are exact USD millions solely for readability; implementation
stores exact USD `Decimal` values. The complete operand qnames, captions,
contexts, raw values, decimals, calculation relationships, and direct SEC URLs
are frozen in the [Wave 14 evidence matrix](operating-income-derivation-design.md#complete-25-period-evidence-matrix)
and must be copied into the immutable entries without substitution.

| # | CIK | Accession | Annual start / report | Formula | Expected OI (USDm) | Pretax bridge variance (USDm) | Expected |
|---:|---:|---|---|---|---:|---:|---|
| 1 | 59478 | `0000059478-22-000068` | 2021-01-01 / 2021-12-31 | LLY | 6,357.1 | 0 | resolve |
| 2 | 59478 | `0000059478-23-000082` | 2022-01-01 / 2022-12-31 | LLY | 7,127.3 | 0 | resolve |
| 3 | 59478 | `0000059478-24-000065` | 2023-01-01 / 2023-12-31 | LLY | 6,457.9 | 0 | resolve |
| 4 | 59478 | `0000059478-25-000067` | 2024-01-01 / 2024-12-31 | LLY | 12,899.0 | 0 | resolve |
| 5 | 59478 | `0000059478-26-000013` | 2025-01-01 / 2025-12-31 | LLY | 26,302 | 0 | resolve |
| 6 | 200406 | `0000200406-22-000022` | 2021-01-04 / 2022-01-02 | JNJ | 23,395 | 0 | resolve |
| 7 | 200406 | `0000200406-23-000016` | 2022-01-03 / 2023-01-01 | JNJ | 23,382 | 0 | resolve |
| 8 | 200406 | `0000200406-24-000013` | 2023-01-02 / 2023-12-31 | JNJ | 21,207 | 0 | resolve |
| 9 | 200406 | `0000200406-25-000038` | 2024-01-01 / 2024-12-29 | JNJ | 20,804 | 0 | resolve |
| 10 | 200406 | `0000200406-26-000016` | 2024-12-30 / 2025-12-28 | JNJ | 25,287 | 0 | resolve |
| 11 | 310158 | `0000310158-22-000003` | 2021-01-01 / 2021-12-31 | MRK | 12,538 | 0 | resolve |
| 12 | 310158 | `0001628280-23-005061` | 2022-01-01 / 2022-12-31 | MRK | 17,945 | 0 | resolve |
| 13 | 310158 | `0001628280-24-006850` | 2023-01-01 / 2023-12-31 | MRK | 2,355 | 0 | resolve |
| 14 | 310158 | `0001628280-25-007732` | 2024-01-01 / 2024-12-31 | MRK | 19,912 | 0 | resolve |
| 15 | 310158 | `0000310158-26-000063` | 2025-01-01 / 2025-12-31 | MRK | 21,218 | 0 | resolve |
| 16 | 319201 | `0000319201-22-000023` | 2021-07-01 / 2022-06-30 | KLAC | 3,654.181 | 0 | resolve |
| 17 | 319201 | `0000319201-23-000031` | 2022-07-01 / 2023-06-30 | KLAC | 3,994.696 | 0 | resolve |
| 18 | 319201 | `0000319201-24-000021` | 2023-07-01 / 2024-06-30 | KLAC | 3,346.210 | 0 | resolve |
| 19 | 319201 | `0000319201-25-000024` | 2024-07-01 / 2025-06-30 | KLAC | 4,775.127 | 0 | resolve |
| 20 | 319201 | `0000319201-26-000027` | 2025-07-01 / 2026-06-30 | KLAC | 5,660.780 | 0 | resolve |
| 21 | 51143 | `0001558370-22-001584` | 2021-01-01 / 2021-12-31 | IBM | 6,865 | 0 | resolve |
| 22 | 51143 | `0001558370-23-002376` | 2022-01-01 / 2022-12-31 | IBM | 8,174 | -1 | resolve under exact IBM gate |
| 23 | 51143 | `0000051143-24-000012` | 2023-01-01 / 2023-12-31 | IBM | 9,382 | -1 | resolve under exact IBM gate |
| 24 | 51143 | `0000051143-25-000015` | 2024-01-01 / 2024-12-31 | IBM | 9,380 | 0 | resolve |
| 25 | 51143 | `0000051143-26-000010` | 2025-01-01 / 2025-12-31 | IBM | 11,822 | +1 | resolve under exact IBM gate |

The registered ordered qnames follow the Wave 14 keys exactly. LLY 2021 uses
`lilly:AcquiredInProcessResearchAndDevelopment`; LLY 2022 uses
`lilly:AcquiredInProcessResearchAndDevelopmentAndDevelopmentMilestones`; LLY
2023–2025 use
`us-gaap:ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff`.
JNJ 2021–2022 use `us-gaap:ResearchAndDevelopmentInProcess`; JNJ 2023–2025 use
`jnj:ResearchAndDevelopmentInProcess1`. JNJ interest changes from
`us-gaap:InterestExpense` to `us-gaap:InterestExpenseNonoperating` in 2024.
KLAC interest changes on the same boundary; its impairment and
debt-extinguishment terms are present only in the exact rows frozen by Wave 14.
IBM 2021–2023 use `ibm:OtherIncomeAndExpense`; IBM 2024–2025 use
`ibm:OtherExpenseAndIncome`. Namespace taxonomy identities are entry fields,
not inferred from local names.

## Ten negative controls

The registry contains no entry for these exact selected filings. All must stay
missing unless the unchanged direct policy independently resolves:

| CIK | Issuer | Accession | Annual start / report | Reason |
|---:|---|---|---|---|
| 93410 | CVX | `0000093410-22-000019` | 2021-01-01 / 2021-12-31 | integrated-energy perimeter unapproved |
| 93410 | CVX | `0000093410-23-000009` | 2022-01-01 / 2022-12-31 | integrated-energy perimeter unapproved |
| 93410 | CVX | `0000093410-24-000013` | 2023-01-01 / 2023-12-31 | integrated-energy perimeter unapproved |
| 93410 | CVX | `0000093410-25-000009` | 2024-01-01 / 2024-12-31 | integrated-energy perimeter unapproved |
| 93410 | CVX | `0000093410-26-000078` | 2025-01-01 / 2025-12-31 | integrated-energy perimeter unapproved |
| 40545 | GE | `0000040545-22-000008` | 2021-01-01 / 2021-12-31 | business/perimeter research required |
| 40545 | GE | `0000040545-23-000023` | 2022-01-01 / 2022-12-31 | business/perimeter research required |
| 40545 | GE | `0000040545-24-000027` | 2023-01-01 / 2023-12-31 | business/perimeter research required |
| 40545 | GE | `0000040545-25-000015` | 2024-01-01 / 2024-12-31 | dimensioned segment/reconciliation facts only |
| 40545 | GE | `0000040545-26-000008` | 2025-01-01 / 2025-12-31 | dimensioned segment/reconciliation facts only |

## Required implementation regression matrix

Before production behavior changes, focused tests must prove:

- all 25 manifest entries resolve to the exact Wave 14 value and retain exact
  policy ID/version, entry identity, evidence, ordered terms, signed
  contributions, occurrences, and validation results;
- all ten CVX/GE controls remain missing, as do a future filing, a `10-K/A`, a
  different accession for the same dates, and every unregistered issuer-period;
- all 169 currently direct Operating Income periods are unchanged, direct
  ambiguity is never replaced, equal direct/derived evidence confirms the
  direct result, and differing direct/derived values remain ambiguous;
- every Wave 14 concept, taxonomy, CIK, accession, report date, annual period,
  empty-dimensional scope, unit, exact value, coefficient, operand order,
  explicit absence, and completeness assertion matches the frozen registry;
- equivalent duplicate contexts, different exact-USD unit IDs, and different
  raw/decimals representations of the same `Decimal` confirm while retaining
  every occurrence; unexpected values conflict;
- entity, period, concept, namespace, accession, normalized unit, dimension,
  nil, missing-context, broken-link, and source-metadata differences follow the
  failure table and never collapse;
- LLY registered lower-precision occurrences are retained but cannot replace
  the face operand; an unregistered third value is ambiguous;
- an operand cannot be reused or double-counted and incomplete term sets never
  calculate; Pretax cannot act as a plug;
- IBM exact sums remain unchanged, the three signed one-million variances pass
  only their exact validation gates, and any other scale or variance fails;
- serialization round-trips every provenance field deterministically; and
- Operating Tax accepts only a complete active-version curated result, retains
  its supporting-policy provenance, and otherwise preserves existing direct
  behavior and blockers.

The five-company seed corpus and every non-Operating-Income metric must remain
unchanged. A full live corpus rerun is permitted only after focused and complete
tests pass.

## Expected future reconciliation and next milestone

If a later implementation passes the regression matrix and live evidence, the
design target is Operating Income 194 resolved / 10 missing / 0 ambiguous. The
25 new resolutions would move the aggregate corpus to 1,880 resolved / 1,508
missing / 11 ambiguous / 27 methodology-blocked / 42 not-comparable, with the
total fixed at 3,468 states. These are design targets, not current production
counts.

The exact next milestone is implementation and validation of
`operating_income_component_derivation_v1`: add the immutable models and
25-entry registry, narrow resolver integration after the unchanged direct
policy, provenance/output/serialization and Operating Tax support, focused
regressions, targeted 25-positive/10-control live validation, complete tests,
and only then a full corpus reconciliation. CVX/GE research remains separate
and must not be folded into that implementation.
