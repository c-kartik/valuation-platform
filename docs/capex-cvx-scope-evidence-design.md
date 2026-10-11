# CVX exact-accession Capex scope acceptance

## Decision and frozen boundary

Phase 1H.4 Wave 31 starts at `b333a144163a9ccdaefe6bfcd118fcb8bde700e2`,
clean `main`, nine commits ahead of origin. No push.
**PARTIAL GO:** five CVX `CURATED_DESIGN_GO` entries, classification
`GROSS_CASH_PPE_EQUIVALENT`, for later implementation only. No generic fallback,
mineral/lease equation, primitive expansion or production approval.

The [five-entry acceptance matrix](capex-cvx-scope-evidence-matrix.json)
freezes the [Wave 30 supplement](capex-cvx-perimeter-inventory.json),
[Wave 26 inventory](capex-inventory.json), [36 retained report bodies](evidence/cvx-capex-perimeter-response-bodies.json)
and published ten-entry runtime registry by file SHA-256. It includes separate
ten-entry v1 and 42-control regression manifests; all 57 identities reconcile.
These controls are unapproved, not freshly reviewed economic denials.

The [reviewed methodology](capex-cvx-acquisition-perimeter.md#current-decision-wave-30-methodology-review)
admits evidenced cash development/mineral-property and capitalized service/lease
inputs **within the independently reported PP&E cash component**. R12 reports
that complete component separately from investment additions, current dry holes
and other assets/liabilities, excluding noncash movements. R10 defines its
PP&E cost perimeter; R7 and acquisition notes distinguish business consideration;
R14 distinguishes incurred lease costs, actual investing cash, noncash ROU
additions and financing principal. Preserve the component intact and positive.
Do not net proceeds, add affiliate/lease cash, subtract all investing lease cash,
count acquired fair values or reconstruct a materials-only/mineral-only measure.
Unknown separate allocation prevents adjusted equations, not this unadjusted
reported-value acceptance. Scope is not established by a label or matching total.
Future FCFF/lease/depletion/EBIT/timing compatibility remains unproved.

## Exact entries, operands and mandatory evidence

All entries are CIK `93410`, metric Capex, exact non-amended 10-Ks, annual
January 1–December 31. Each operand is
`us-gaap:PaymentsToAcquireOilAndGasPropertyAndEquipment`, empty dimensions,
non-nil, exact USD and a positive exact Decimal. Full taxonomy namespace,
filing date, primary document and report date are in the matrix, not wildcards.

| Year | Exact accession | Expected USD | Namespace suffix | Original instance ordinal / annual context |
| --- | --- | ---: | --- | --- |
| 2021 | `0000093410-22-000019` | 7515000000 | `2021-01-31` | 714 / `idd436c1bb1314e08bd5fd6d1285101ad_D20210101-20211231` |
| 2022 | `0000093410-23-000009` | 10349000000 | `2022` | 698 / `i3cd5a5d08ac0405882d3e0768d20dc50_D20220101-20221231` |
| 2023 | `0000093410-24-000013` | 14788000000 | `2023` | 723 / `c-1` |
| 2024 | `0000093410-25-000009` | 15544000000 | `2024` | 736 / `c-1` |
| 2025 | `0000093410-26-000078` | 16830000000 | `2025` | 753 / `c-1` |

Namespace prefix is `http://fasb.org/us-gaap/`. Each currently has one eligible
occurrence and semantic signature. Preserve original `usd` unit definition,
raw/numeric strings, decimals `-6`, SEC CIK entity, context and source/accession.
Stored original ordinal/context IDs identify the reviewed occurrence, not a
rule that blindly selects that ordinal or rejects equivalent context IDs.

An entry key binds metric, normalized CIK, accession, form, filing date, primary
document, report date, authoritative annual start/end, full namespace/taxonomy/
concept, nondimensional scope, exact USD and approved classification. Expected
Decimal and selected instance URL/body digest are also immutable acceptance
constraints. Confirm the authority against selected annual DEI and registrant,
not a calendar-year guess or later comparative. No issuer-wide, future,
accession-prefix or amended registration.

Mandatory raw-byte manifest: selected instance, submitted schema, presentation
linkbase where present (embedded schema roles where applicable), FilingSummary,
and all selected R7/R10/R12/R14/R24/R27/R38 report bodies; R39 is also required
for 2023. Counts are 11/11/12/11/11 unique URLs respectively. Each has explicitly
typed `sha256_sec_response_body_bytes`, byte length and exact accession URL.
Each review has a unique ID, milestone/date, approved-for-design status,
location, rationale and association with the entry. Implementation must publish
the separately reviewed immutable runtime records; flags in research JSON are
not automatically executable approval.

The 36 report bodies remain losslessly retained as gzip/base64; verify their
decompressed bytes. Original retrieval time/status remain unknown/null, not
invented. Instance/structure original bodies were independently verified from
retained `.bin` artifacts. No new SEC request or replacement fingerprint.

Directory `index.json` is discovery metadata, not necessary to verify these
fixed v2 URLs; no parsed/reserialized JSON hash is promoted to a response-body
hash. Standalone calculation/label XML originals are not retained. Their old
discovery fingerprints are explicitly ancillary/unverified in this design,
never a mandatory v2 gate or scope proof. Calculation arcs are not required:
the component is independently reported, not derived. Submitted verified
presentation/schema and primary statement/note evidence establish location and
scope. This does not remove any v1 manifest requirement. If later functionality
requires those ancillary bodies, obtain original bytes and review them explicitly;
do not certify them from extracted metadata or bypass a mandatory digest.

## Immutable versioning and integration

Keep ID `capex_scope_equivalence`. Publish **version `2` containing only the
five CVX entries**, serialized identity `capex_scope_equivalence_v2`, alongside
the existing immutable version `1` containing exactly ten AMZN/LLY entries.
Version 2 is an additive disjoint approval set, not a latest-version replacement
or a fifteen-entry rewrite of v1. The matrix freezes the v1 registry file hash
and each canonical reviewed-entry hash, identities and expected values.
Existing v1 normalized/serialized approval provenance, AMZN refresh history
and LLY representation correction must remain unchanged.

Use an explicit immutable published-policy catalog and exact filing dispatch;
reject overlapping entry registrations across active versions, duplicate keys,
unknown versions, unsupported classifications and incomplete models. Never use
the largest version, ticker default or arbitrary caller-supplied policy. Changes
to an entry, scope or evidence require another reviewed version and explicit
supersession, not in-place modification. The v1 default/API and old validation
path remain valid; shared v2 validation must not weaken or reinterpret v1.

The bounded implementation will extend only curated Capex models/registry
selection, artifact manifest lookup at historical/corpus composition and
published-version provenance validation. Existing code currently hardcodes v1,
two CIKs, three reviews and ten entries; merely adding CVX to that list is not
the approved design. Give v2 its canonical five-entry/evidence specification.
Do not alter `filing_xbrl`, generic historical selection, generic
`CAPEX_POLICY`, the ten-entry JSON registry or any other measure's rules.
SEC retrieval stays outside normalization. Re-parse verified instance bytes and
compare facts, contexts and units with the supplied parsed instance before
acceptance. Verify every required statement/note/structure digest first.

## Occurrences, conflicts, precedence and conservative failures

1. Run the existing direct Capex policy first. Preserve its chosen concept and
   all direct ambiguities. Unregistered filings retain existing direct behavior;
   they do not trigger v2 evidence retrieval or approval.
2. Match the exact registered filing and authoritative period. Missing delivered
   evidence makes v2 unavailable, never a resolution. An incomplete published
   entry fails model construction. Tampered hashes, cross-accession artifacts,
   inconsistent source/registrant/annual metadata, missing/broken context or unit
   links, malformed numerics and contradictory nil/numeric structure are data
   errors, not missing-as-zero. Keep v1's existing error behavior unchanged.
3. Structurally valid wrong-entity/period/namespace/concept, dimensioned and
   non-USD facts are excluded with ordered reasons; they neither confirm nor
   conflict with the eligible nondimensional USD component. Nil-only target
   evidence cannot resolve. A relevant nil/numeric collision in the same target
   semantic scope is a structural error; nil in an excluded dimensional scope
   cannot poison a valid nondimensional fact.
4. Group eligible occurrences by namespace/concept, normalized CIK, accession,
   authoritative start/end, empty dimensions, exact-USD normalized unit, exact
   finite Decimal and non-nil status. Different context IDs or USD unit IDs may
   confirm; different lexical strings/decimals may confirm only at the same
   exact Decimal. Retain every representation in document order. No tolerance,
   rounding, summation, absolute-value repair or first/maximum-value preference.
5. Exactly one signature equal to the frozen positive expected value may approve.
   No eligible occurrence or one changed/negative value leaves fallback missing
   with a mismatch diagnostic. Multiple eligible values remain ambiguous even
   when one matches the reviewed value. Source-body mutation ordinarily fails
   the integrity gate before this selection logic; it never authorizes new scope.
6. With complete approved v2 evidence, an equal current direct value may confirm:
   retain the direct concept, attach supporting v2 provenance. A differing valid
   direct and eligible curated value remains ambiguous. Unavailable/unapproved
   evidence cannot replace a valid direct result or claim confirmation; structural
   errors are surfaced. Direct ambiguity is never repaired by v2.
7. The aggregate productive-assets duplicates, dry-hole/investment/lease/acquisition
   facts and dimensional support are not Capex operands. Preserve them as typed
   support/exclusions, not confirming sources or implicit ADD/SUBTRACT terms.
   No assertion assigns all separately disclosed investing lease cash to PP&E.
8. Future, 10-K/A, unregistered and partial-period filings receive no implicit
   approval. A supplied approved accession cannot override the selected filing.

## Provenance and serialization

Emit a policy-approved **reported** positive Capex value, not a derivation.
Preserve v2 policy/entry identity, scope classification, review IDs/locations/
rationales, exact expected Decimal, selected instance and mandatory typed
digests, canonical entry snapshot, authority and ordered support/exclusions.
Select the first eligible occurrence deterministically but retain all confirming
occurrences, one-based confirming ordinals and zero-based original instance
ordinals. Keep raw values, decimals/nil, contexts/entity/period/dimensions,
original unit IDs/definitions, normalized USD, source and accession.

Carry this audit through normalization, standardized output and serialization,
including supporting policy provenance on equal direct confirmation. Schema 5's
existing Capex audit can represent this contract; no new field meaning or schema
change is designed. Extend published-policy lookup/round-trip validation to v2
while preserving v1 acceptance and byte-equivalent v1 entry/audit records.
Serializers must not silently drop v2, coerce Decimal via float, collapse
multiplicity or relabel v1 as v2. Unknown policy versions fail validation.
Future consumers retain supporting policy provenance; no current ETR, taxes or
NWC measure has a Capex dependency, and no FCFF/readiness calculator is authorized.

## Regression plan, validation and next milestone

| Cohort | Count | Future implementation assertion |
| --- | ---: | --- |
| New CVX entries | 5 | Exactly five missing-to-resolved reported values under v2; frozen operands and all review evidence survive output/round trip. |
| Existing AMZN/LLY | 10 | Same v1 values, approval records, reviews, correction/refresh history and serialized provenance; no relabeling. |
| Other frozen inventory controls | 42 | All baseline missing states unchanged; no v2 entry/retrieval or fresh economic denial. |
| Existing direct Capex results | 147 | Values/states/chosen concepts and provenance unchanged; preserve META gross treatment. |

The machine manifest reconciles 5 + 10 + 42 = 57 unique inventory identities.
Current production remains 147 direct + 10 curated = **157/47/0**;
aggregate **1,895/1,493/11/27/42 = 3,468**. These are carried-forward results,
not remeasured. Conditional implementation target only: **162/42/0**, aggregate
**1,900/1,488/11/27/42 = 3,468**, exactly five new Capex states, no other measure
changes, 43 generic completions and seven specialized skips unchanged.

Focused plan: immutable/catalog/version/cross-version overlap tests; all five
positives, ten v1 preservation cases and 42 controls; equal/direct conflict and
direct ambiguity; same/different-context duplicates; equivalent exact USD IDs
and lexical Decimal/decimals; conflicting/changed/negative values; wrong entity,
dates, accession, namespace, concept, dimension or unit; nil-only/collision,
malformed numbers and broken links; omitted/swapped/digest-mismatched artifacts;
future/amended/unregistered sources; deterministic original/confirming order,
support/exclusions and schema-5 exact-Decimal round trips under both versions.
Selection adversaries use coherent independently reviewed synthetic byte fixtures
and test policies, not mutated published hashes or bypassed integrity checks.

After focused and 57-period checks, targeted validation of five CVX accessions
and ten v1 preservation cases must pass before one complete suite and one corpus
reconciliation. Stop on unexpected states, provenance changes or execution
differences. This design runs **none** of those tests or corpus steps.

Design validation checks frozen identities/operands, five approval decisions,
ten published v1 entry fingerprints, 42 controls, raw report/instance/structure
digests, version/catalog consistency, local links and `git diff --check`.
Validation passed: five exact operand/authority copies, ten unchanged canonical
v1 entry fingerprints, 42 controls (22 concept-policy / 17 derivation / three
methodology routes), 57 unique identities, 56 mandatory original-body digests
including the 36 retained reports, and 87 relevant local links. All bound source
files, runtime registries and evidence fixtures remain unchanged. No tests,
corpus execution or SEC requests; `git diff --check` passed.
**Next bounded milestone:** implement and incrementally validate only the five
CVX v2 reported-value entries with the immutable disjoint catalog; preserve v1
and generic policies. No broad research, adjusted equation or other issuer entry.
