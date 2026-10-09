# Pretax scope-evidence policy design

## Scope and decision

Phase 1H.4 Wave 11 designs and independently reviews whether the eight exact
annual facts classified as `INCLUDED_PRETAX` in
[`pretax-equity-method-note-evidence.md`](pretax-equity-method-note-evidence.md)
can be normalized without parsing narrative text at execution time. The frozen
scope is MA three periods and CVX five periods. The 20
`SEPARATE_NET_OF_TAX` periods and five mixed-treatment LIN periods are mandatory
controls. The 12 ORCL, MCD, and PG issuer-extension periods remain outside
scope.

The decision is **PARTIAL GO**:

- **NO-GO for an automated structured-evidence rule.** No structured rule
  separates all eight positives from all 25 controls while also explaining the
  economic boundary. The candidate concept, exact annual context, USD unit,
  presentation-role pattern, renderer membership, labels, and statement
  membership are common to positive and negative periods. MA's tag transition
  and CVX's taxonomy/presentation mismatch are corroborating research facts,
  not non-circular production rules.
- **GO for a curated exact-accession policy design.** A human-reviewed,
  immutable registry may approve semantic equivalence for only the eight exact
  facts. Execution can be deterministic even though discovery was manual. This
  is consistent with the project's evidence-backed accession-scoped GOOGL debt
  and diluted-share precedents and with the rule that an issuer-specific policy
  requires filing evidence and accounting rationale. It is not a generic
  concept fallback or an issuer-history rule.

Wave 11 does not authorize or implement the registry. All 33 periods remain
typed missing in production, safe new production Pretax resolutions remain
zero, and production Pretax remains 159 resolved / 45 missing / 0 ambiguous.

## Automated structured-rule assessment

The evaluated evidence is the machine-readable evidence already retained or
proved by Waves 7–10: Company Facts identity and observations, the exact
selected accession, the authoritative DEI annual period, extracted filing-XBRL
facts and contexts, filer-submitted presentation roles and paths, SEC renderer
artifacts, labels, units, dimensions, and calculation relationships when
present.

| Proposed signal | 8 positives | 25 controls | Disposition |
|---|---|---|---|
| Candidate taxonomy and concept | Same standard candidate in all 33 | Same | Cannot separate |
| Exact selected accession and annual context | Present in all 8 | Present in all 25 | Eligibility only, not economics |
| USD, duration, report-date ending, numeric fact | Present in all 8 | Present in all 25 | Eligibility only |
| Submitted `Statement` role | One in all 8 | One in all 25 | Cannot separate |
| Submitted `Disclosure` role | One or more in all 8 | One or more in all 25 | Cannot separate |
| SEC MetaLinks and applicable R-file membership | Present in all 8 | Present in all 25 | Cannot separate |
| Statement membership or line label | Pretax line in all 8 | Pretax/tax-denominator line in controls too | Economically insufficient |
| Calculation relationships | No complete, stable relationship proves equity-method scope across all 8 | Absence or differing graphs do not prove exclusion | Incomplete and unsafe |
| MA tag transition | Later filing changes to the current concept | No analogous transition required for controls | Future issuer history; not exact-accession proof |
| CVX presentation/taxonomy mismatch | Candidate is the visible Pretax line while the note says affiliate income enters before-tax earnings | Demonstrates that tag semantics and filing economics can diverge | Requires the manually read note; cannot be the rule |

Numerical size, ETR plausibility, concept frequency, issuer name, statement
membership alone, presentation order alone, and narrative text are excluded by
design. A rule such as “accept when the note says included in pretax” merely
restates the desired classification and is circular unless a separately
validated semantic parser exists. None exists here.

Accordingly, the automated rule result is **NO-GO**. The failure is semantic,
not a lack of structured candidate coverage.

## Curated exact-accession policy assessment

### Policy identity and versioning

The proposed registry identity is `pretax_scope_equivalence`, version `1`.
Its stable serialized identity would be
`pretax_scope_equivalence_v1`. Version 1 contains exactly eight positive
entries and no wildcard, issuer-wide, or negative matching rule.

Each entry is immutable. Correcting evidence, changing economic scope, adding
an accession, or changing eligibility or precedence creates a new registry
version. Incidental code changes do not. Historical versions remain addressable
for reproducibility, and exactly one version may be active. Duplicate keys or
conflicting classifications are configuration errors.

The full key is:

```text
(CIK, accession, report_date, annual_start, annual_end,
 taxonomy, concept, unit, economic_scope_classification)
```

For version 1, `taxonomy` is `us-gaap`, `concept` is
`IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments`,
`unit` is `USD`, and `economic_scope_classification` is
`INCLUDED_PRETAX`. Matching must be exact and case-sensitive after the
repository's existing canonical accession/date parsing. CIK or accession alone
is never sufficient.

### What an entry means

An active positive entry represents **approved semantic equivalence for that
one exact fact and annual period**, not merely a pointer to research evidence.
The supporting evidence record remains distinct and explains why the approval
exists. The 25 controls are regression fixtures and reviewed evidence, not
positive registry entries. `SEPARATE_NET_OF_TAX` and `UNRESOLVED` must never be
interpreted as alternate ways to produce the current Pretax primitive.

Deterministic registry execution must be described accurately: the program
matches an immutable human-approved conclusion; it does not discover economic
scope automatically. Future filings, amended filings, and unregistered periods
default to typed missing even for MA or CVX.

### Required evidence provenance

Every positive entry must retain an immutable evidence reference containing:

- an evidence ID and the registry ID/version;
- exact CIK, accession, form, report date, annual start/end, taxonomy, concept,
  unit, and candidate value signature;
- the official SEC primary-document URL and the exact statement/note location;
- the reviewed classification and the accounting rationale binding the
  equity-method activity to consolidated pretax earnings;
- a short supporting excerpt or content digest, the research artifact path,
  review date, and review status; and
- the structured-fact provenance used at execution: Company Facts URL and, if
  used to prove nondimensional context, filing-XBRL source URL/context ID.

The official filing remains the authority. A documentation link, issuer name,
or quote without the exact filing identity cannot authorize an entry.

### Candidate eligibility and annual-period validation

A registry entry may authorize candidate selection only after the current
approved Pretax concept is missing. The exact entry may still be consulted for
collision validation when both concepts are present. A candidate must satisfy
all of these conditions:

1. the selected filing is the exact registered 10-K accession, CIK, report
   date, and primary filing identity;
2. the supplied annual-period result is resolved and exactly matches the
   registered start/end dates;
3. taxonomy, concept, unit, and economic-scope classification match the entry;
4. the observation is numeric and non-Boolean, current, duration-shaped, ends
   on the report date, and belongs to the selected accession;
5. the fact is nondimensional, or its Company Facts observation is reconciled
   to a nondimensional selected-filing XBRL occurrence; and
6. all retained candidate occurrences have one consistent value and semantic
   context.

No numerical tolerance, materiality threshold, ETR test, issuer inference, or
later comparative fact may repair a failed guard.

### Precedence and ambiguity rules

- The current approved concept remains first. A resolved current-concept fact
  is used unless collision validation against an exact registered candidate
  finds a conflicting value.
- Current-concept ambiguity is never replaced by the curated candidate.
- If a registered candidate and the current concept are both eligible for the
  same period, equal values may be retained as confirmation because semantic
  equivalence was independently approved. Differing values are ambiguous; the
  registry does not silently override either fact.
- A missing registered candidate remains typed missing. The entry is not a
  license to manufacture a value from the evidence narrative.
- An exact duplicate source record is a data error. Multiple context-distinct,
  nondimensional occurrences may confirm only when their entity, annual
  period, unit, dimensions, and value are identical. Any conflicting value,
  period, unit, or dimensional scope is ambiguous.
- Malformed, nil, nonnumeric, Boolean, non-USD, dimensioned-only, interim, or
  wrong-accession facts are ineligible and remain typed missing or fail under
  the repository's existing structural data-error boundary as applicable.
- An unregistered accession always remains typed missing. Stable issuer history
  does not broaden an entry.
- A 10-K/A or other amendment is a different accession. It requires a new
  exact review and a new registry version; an original-filing entry is not
  transferred. A newly selected future 10-K is handled the same way.

### Provenance-model impact

Wave 11 found that the then-existing models could not retain the full approval
boundary without change:

- `NormalizedHistoricalValue` stores direct fact evidence but no policy ID,
  version, economic-scope classification, or reviewed-evidence reference.
- `DerivedHistoricalValue` stores a policy ID but no version.
- standardized direct output currently emits no policy reference.
- `DerivedMetricOperand`, used by Reported ETR, would lose the candidate's
  reviewed policy provenance.

Wave 12 therefore adds a provenance-bearing policy-approved historical result
that cannot be mistaken for a generic direct concept mapping. It retains policy
ID/version, the exact entry key, `INCLUDED_PRETAX`, reviewed evidence
references, and every confirming occurrence through standardized output and
into the Pretax operand of Reported ETR. Serialization now uses standardized
schema version 2. A plain second concept in `PRETAX_INCOME_POLICY` remains an
unacceptable implementation.

### Reported ETR behavior

When an exact registered candidate resolves Pretax, Reported ETR continues to
equal normalized Income Tax Expense divided by that normalized Pretax value. It
retains the policy-approved Pretax operand provenance.
Plausibility of the resulting ratio is diagnostic only and cannot approve or
reject the entry. Missing or ambiguous Pretax continues to produce the existing
downstream missing or ambiguous Reported ETR behavior.

## Complete 8-positive / 25-control regression matrix

`AUTO NO-GO` means no approved structured separator exists. `ALLOW` describes
the production result of the implemented version-1 registry. `DENY` means the
candidate remains typed missing.

| Issuer | CIK | Report date | Annual period | Accession | Wave 10 scope | Automated result | Registry v1 expected |
|---|---:|---|---|---|---|---|---|
| AMZN | 1018724 | 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001018724-22-000005` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| AMZN | 1018724 | 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001018724-23-000004` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| AMZN | 1018724 | 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001018724-24-000008` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| AMZN | 1018724 | 2024-12-31 | 2024-01-01 → 2024-12-31 | `0001018724-25-000004` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| AMZN | 1018724 | 2025-12-31 | 2025-01-01 → 2025-12-31 | `0001018724-26-000004` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| MU | 723125 | 2021-09-02 | 2020-09-04 → 2021-09-02 | `0000723125-21-000065` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| MU | 723125 | 2022-09-01 | 2021-09-03 → 2022-09-01 | `0000723125-22-000048` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| MU | 723125 | 2023-08-31 | 2022-09-02 → 2023-08-31 | `0000723125-23-000054` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| MU | 723125 | 2024-08-29 | 2023-09-01 → 2024-08-29 | `0000723125-24-000027` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| MU | 723125 | 2025-08-28 | 2024-08-30 → 2025-08-28 | `0000723125-25-000028` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| MA | 1141391 | 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001141391-22-000023` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| MA | 1141391 | 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001141391-23-000020` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| MA | 1141391 | 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001141391-24-000022` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| CVX | 93410 | 2021-12-31 | 2021-01-01 → 2021-12-31 | `0000093410-22-000019` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| CVX | 93410 | 2022-12-31 | 2022-01-01 → 2022-12-31 | `0000093410-23-000009` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| CVX | 93410 | 2023-12-31 | 2023-01-01 → 2023-12-31 | `0000093410-24-000013` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| CVX | 93410 | 2024-12-31 | 2024-01-01 → 2024-12-31 | `0000093410-25-000009` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| CVX | 93410 | 2025-12-31 | 2025-01-01 → 2025-12-31 | `0000093410-26-000078` | `INCLUDED_PRETAX` | `AUTO NO-GO` | `ALLOW` |
| CAT | 18230 | 2021-12-31 | 2021-01-01 → 2021-12-31 | `0000018230-22-000050` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| CAT | 18230 | 2022-12-31 | 2022-01-01 → 2022-12-31 | `0000018230-23-000011` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| CAT | 18230 | 2023-12-31 | 2023-01-01 → 2023-12-31 | `0000018230-24-000009` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| CAT | 18230 | 2024-12-31 | 2024-01-01 → 2024-12-31 | `0000018230-25-000008` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| CAT | 18230 | 2025-12-31 | 2025-01-01 → 2025-12-31 | `0000018230-26-000008` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| PM | 1413329 | 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001413329-22-000011` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| PM | 1413329 | 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001413329-23-000025` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| PM | 1413329 | 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001413329-24-000013` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| PM | 1413329 | 2024-12-31 | 2024-01-01 → 2024-12-31 | `0001413329-25-000013` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| PM | 1413329 | 2025-12-31 | 2025-01-01 → 2025-12-31 | `0001628280-26-005939` | `SEPARATE_NET_OF_TAX` | `AUTO NO-GO` | `DENY` |
| LIN | 1707925 | 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001628280-22-004180` | `UNRESOLVED` | `AUTO NO-GO` | `DENY` |
| LIN | 1707925 | 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001628280-23-005434` | `UNRESOLVED` | `AUTO NO-GO` | `DENY` |
| LIN | 1707925 | 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001628280-24-007424` | `UNRESOLVED` | `AUTO NO-GO` | `DENY` |
| LIN | 1707925 | 2024-12-31 | 2024-01-01 → 2024-12-31 | `0001628280-25-007990` | `UNRESOLVED` | `AUTO NO-GO` | `DENY` |
| LIN | 1707925 | 2025-12-31 | 2025-01-01 → 2025-12-31 | `0001628280-26-011430` | `UNRESOLVED` | `AUTO NO-GO` | `DENY` |

The matrix reconciles to 33 exact accessions: MA 3 + CVX 5 = 8 positive;
AMZN 5 + MU 5 + CAT 5 + PM 5 = 20 separate-net-of-tax controls; and LIN 5 =
5 mixed-treatment controls. A version-1 registry must allow exactly eight and
deny exactly 25. ORCL, MCD, and PG do not appear.

## Independent adversarial review

The review attempted to falsify both proposed boundaries after the design was
drafted.

| Objection | Test and result | Disposition |
|---|---|---|
| Statement membership separates positives | All 20 separate-net-of-tax and all five LIN controls have the same submitted `Statement` plus `Disclosure` membership pattern | Automated rule rejected |
| The candidate label or taxonomy definition is enough | The same concept covers included, separate-after-tax, and mixed economics | Automated rule rejected |
| Small equity-method amounts make controls equivalent | AMZN, MU, CAT, and PM remain economically separate regardless of size; PM's combined line is also contaminated by securities activity | Materiality rule rejected |
| ETR plausibility validates the candidate | Both positive and negative issuers use the candidate as a tax denominator | ETR rule rejected |
| MA's 2024 tag transition proves the earlier three periods | The transition is outside the three selected accessions and does not encode the investment-policy binding | Transition retained only as corroboration |
| CVX's candidate tag should exclude affiliate income | Exact notes place affiliate earnings in before-tax consolidated earnings, exposing a taxonomy/presentation mismatch | Structured tag semantics cannot decide the filing economics |
| Issuer name plus stable history is deterministic | It would approve unreviewed future/amended periods and fail on treatment changes such as LIN's mixed legal-form rule | Issuer-wide rule rejected |
| The allowlist is circular | If entries merely store `INCLUDED_PRETAX`, they are circular; the proposed registry instead requires external exact-filing evidence and a reviewed rationale | Objection satisfied only by retaining the separate evidence record |
| A curated entry is an unjustified hardcode | The eight entries are exact-accession, exact-period, evidence-backed semantic approvals with conservative defaults, comparable in scope discipline to existing GOOGL accession policies | Acceptable as a curated exception, never as generic discovery |
| Negative controls need denylist entries | A denylist could imply that unlisted facts are acceptable | Rejected; registry contains positives only and absence always denies |

Every one of the 25 controls remains denied under the full-key lookup. Removing
CIK, accession, annual dates, taxonomy/concept, unit, or classification from the
key weakens that result and is prohibited. The evidence supports only manual
accession-specific decisions; it does not support automated economic-scope
discovery.

## Wave 12 implementation outcome

Wave 12 implements the reviewed curated-policy foundation, not a generic
concept fallback:

1. immutable policy and reviewed-evidence models register exactly the eight
   approved MA/CVX facts as `pretax_scope_equivalence_v1`;
2. current-concept-first and deny-by-default behavior remains in force without
   changing `PRETAX_INCOME_POLICY`;
3. the resolver groups eligible nondimensional filing-XBRL occurrences by the
   complete semantic signature. MA's three same-context occurrences and CVX's
   two nondimensional occurrences therefore confirm one result; CVX's distinct
   dimensioned facts remain excluded;
4. every confirming occurrence is retained in deterministic order with a
   one-based ordinal and its original context ID, unit ID, raw value, decimals,
   nil status, dates, dimensions, and source metadata; policy identity and
   reviewed evidence flow through standardized-output schema version 2 and the
   Pretax operand of Reported ETR; and
5. different eligible values remain ambiguous, while broken context links,
   missing contexts, inconsistent entity/accession/source identity, bad unit
   links, and nil/numeric collisions remain structural data errors.

Focused validation passes 122 tests and the complete suite passes 491. The
targeted live run resolves exactly eight Pretax and eight Reported ETR periods.
The 33-period regression resolves all eight `ALLOW` rows and leaves all 25
controls missing; all 12 excluded ORCL/MCD/PG extension periods also remain
missing. Full-corpus Pretax and Reported ETR each reconcile to 167 resolved /
37 missing / 0 ambiguous, and aggregate states reconcile to 1,855 resolved /
1,533 missing / 11 ambiguous / 27 methodology-blocked / 42 not-comparable
across 3,468 states.

Any future accession still requires its own filing review and a new policy
version. The exact next milestone is research of the 35 missing Operating
Income periods using selected-filing face-statement evidence; production policy
design or implementation is not yet authorized.
