# Capex scope-evidence acceptance design

## Decision and economic boundary

Phase 1H.4 Wave 27 starts at `052525309a4e0b46dfe047cdb6e67eaa6bfaad63`.
Wave 28 now implements this ten-entry foundation with explicit LLY representation
correction and an authorized AMZN evidence refresh; see
[verified implementation/results](capex-scope-evidence-results.md). The Wave 27
matrix remains a frozen research snapshot, not the executable evidence registry.
**PARTIAL GO:** approve curated acceptance design for the ten exact AMZN/LLY
periods in the [acceptance matrix](capex-scope-evidence-matrix.json).
Five AMZN and five LLY entries are `CURATED_DESIGN_GO`, classified
`GROSS_CASH_PPE_EQUIVALENT`. No automated economic-equivalence rule, generic
productive-assets/other-PP&E fallback, derivation or production registration is
approved. Automation may enforce a reviewed entry, not manufacture approval.

The [Wave 26 inventory](capex-inventory.json) remains unchanged. Its 47 other
rows are `NO_ENTRY`, not 47 proved economic denials. They retain 27 scope gaps,
17 component-completeness gaps and three GE methodology gates. Wave 26 reviewed
identified patterns; this pass does not freshly review those controls or prove
that every possible measure is incompatible. Specific noncash, acquisition,
lease, intangible-only and netted substitutes are excluded by the primitive;
that is distinct from denying an entire issuer-period.

The [current primitive](financial-methodology.md) is reported gross cash
expenditure to acquire PP&E, preserved as a positive magnitude. These are
reported-value acceptances, not ADD/SUBTRACT component equations. The reported
purchase line, selected accounting policy and PP&E note establish scope;
numeric equality, a tag label, presentation membership or a balance-sheet
movement cannot establish it alone.

| Boundary | AMZN evidence and decision | LLY evidence and decision |
| --- | --- | --- |
| Cash and gross presentation | Selected consolidated cash flow reports purchases of property/equipment separately from property/equipment sales and incentives. Accept purchases only; do not net the latter combined line. | Selected consolidated cash flow reports purchases of property/equipment. Accept the reported purchase amount, not an asset-balance change or net investing subtotal. |
| PP&E versus other assets | Accounting/PP&E notes identify owned land/buildings, equipment, other PP&E assets and construction. Acquired intangibles/content are separate asset categories. Software capitalization is described as not significant, not zero; no inferred software deduction. | PP&E note identifies land, buildings, equipment and construction. Broader long-lived assets include leases and, explicitly in later notes, software; do not replace the PP&E cash caption with that broader geographic total or add software/intangibles. |
| Noncash and unpaid purchases | Supplemental lease additions and PP&E acquired but unpaid are not cash purchases. Their balances are not added or used as residual adjustments. | Noncash asset additions or accrued purchases do not increase the accepted cash amount. No unreported amount is inferred from absence. |
| Leases and financing | Finance-lease assets may appear in PP&E, but asset recognition is noncash and principal repayments are separately financing. Operating-lease cash and financing obligations are not accepted operands. | Operating ROU assets are distinguished from PP&E in broader asset disclosures. No ROU additions, lease payments or lease principal are added to purchases. This is not approval of an integrated lease model. |
| Business acquisitions | Separate acquisition/investment cash line and acquired intangible policy distinguish purchases from acquiring a business. Do not include acquired PP&E via acquisition accounting. | Separate acquisition cash line and IPR&D/acquisition treatment distinguish purchases from acquiring businesses or rights. Do not add acquisition cash, IPR&D or acquired asset balances. |
| Proceeds/incentives | Vendor incentives reduce asset costs; later policies also describe government incentives reducing assets/expenses. This does not make purchases a pre-incentive economic investment measure. Preserve the reported cash purchase amount; neither subtract the separate mixed proceeds/incentives line nor infer an incentive gross-up. | Product-rights/investment proceeds are not PP&E purchases and are not netted. No complete incentive allocation is evidenced or required to reconstruct a different pre-incentive measure; invent none. |
| Interest and consolidation | Preserve selected consolidated scope and reported PP&E acquisition cash costs without an interest/expense residual. No segment or later comparative substitute. | Capitalized interest described as nonmaterial in 2021–2024 is not zero; 2025 silence is not a zero. Accept reported consolidated purchase cash without an inferred interest adjustment. |

Gross means **not net of separately presented disposal/incentive inflows**;
it does not authorize reconstruction of hypothetical cash before negotiated
rebates, basis reductions or tax incentives. No primitive expansion or incentive
allocation is approved. Future FCFF/tax/lease/timing compatibility remains a
separate valuation-boundary question, not established by this acceptance.

## Exact entries and reviewed evidence

The matrix freezes all 57 identities and ten positive operands. For each
positive entry it copies full filing metadata, authoritative dates, namespace,
concept, exact numeric strings, context/entity/dimensions, unit definition,
raw value/decimals/nil, original full-instance ordinal, instance digest,
presentation/calculation metadata, cash-flow captions and the three selected
statement/note URL/digest/location records. These copies are checked against the
unchanged inventory, whose SHA-256 is in the matrix. No later comparative,
amended filing or latest-five selection is substituted. Wave 26's 25 identities
bound from unique non-amended 10-K metadata for frozen baseline dates keep that
explicit identity provenance; this design does not claim an older lost manifest.

| Issuer / CIK | Accession | Annual start / end | Exact USD | Original ordinal | Statement / policy / PP&E locations |
| --- | --- | --- | ---: | ---: | --- |
| AMZN / 1018724 | `0001018724-22-000005` | 2021-01-01 / 2021-12-31 | 61053000000 | 95 | [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/R3.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/R10.htm); [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/R12.htm) |
| AMZN / 1018724 | `0001018724-23-000004` | 2022-01-01 / 2022-12-31 | 63645000000 | 101 | [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/R3.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/R10.htm); [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/R12.htm) |
| AMZN / 1018724 | `0001018724-24-000008` | 2023-01-01 / 2023-12-31 | 52729000000 | 105 | [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/R3.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/R10.htm); [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/R12.htm) |
| AMZN / 1018724 | `0001018724-25-000004` | 2024-01-01 / 2024-12-31 | 82999000000 | 123 | [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/R3.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/R10.htm); [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/R12.htm) |
| AMZN / 1018724 | `0001018724-26-000004` | 2025-01-01 / 2025-12-31 | 131819000000 | 135 | [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/R3.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/R10.htm); [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/R12.htm) |
| LLY / 59478 | `0000059478-22-000068` | 2021-01-01 / 2021-12-31 | 1309800000 | 400 | [R9.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/R9.htm); [R11.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/R11.htm); [R19.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/R19.htm) |
| LLY / 59478 | `0000059478-23-000082` | 2022-01-01 / 2022-12-31 | 1854300000 | 364 | [R9.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/R9.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/R10.htm); [R18.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/R18.htm) |
| LLY / 59478 | `0000059478-24-000065` | 2023-01-01 / 2023-12-31 | 3447600000 | 365 | [R9.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/R9.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/R10.htm); [R18.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/R18.htm) |
| LLY / 59478 | `0000059478-25-000067` | 2024-01-01 / 2024-12-31 | 5057800000 | 384 | [R9.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/R9.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/R10.htm); [R18.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/R18.htm) |
| LLY / 59478 | `0000059478-26-000013` | 2025-01-01 / 2025-12-31 | 7841000000 | 314 | [R9.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/R9.htm); [R10.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/R10.htm); [R18.htm](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/R18.htm) |

All ten current operands have one nondimensional, non-nil exact-USD occurrence,
one semantic signature, positive exact Decimal and the cash caption Purchases
of property and equipment. The JSON retains actual contexts, namespace versions
and decimals rather than a wildcard `us-gaap` name. The selected statements
display purchases as outflows; the XBRL facts carry positive magnitudes. Do not
apply a second sign reversal or absolute-value repair to a changed negative fact.

Each positive entry requires its selected cash-flow statement, accounting-policy
note and PP&E note, plus instance and submitted schema/presentation/calculation/
label artifacts frozen in the matrix. Review assertions bind the cash caption,
asset perimeter and exclusions to precise report/section locations, not merely
to hashes. Role/arc membership is concept-level support, not proof that every
duplicate occurrence is rendered in that statement. Matrix records preserve
report role, definition, URL and hash; the unchanged inventory retains all
supporting fact occurrences, contexts and units. Supporting facts are not extra
Capex operands. Retained Wave 26 note text was re-read; no new SEC requests or
unchanged-link HTTP revalidation are needed. A digest verifies reviewed bytes,
not accounting truth by itself.

## Proposed immutable contract

Proposed ID `capex_scope_equivalence`, version `1`, serialized identity
`capex_scope_equivalence_v1`. Use frozen validated entry/review models and an
immutable tuple registry of exactly ten entries. Duplicate entry keys,
unsupported classifications, invalid dates/CIKs/accessions, empty rationale,
missing mandatory evidence, invalid digests or cross-accession evidence fail
construction. Publish a new version for any entry, scope or evidence change;
never edit v1 in place. This JSON is a design artifact, not an executable registry
or a schema change; no automatic registration from research flags.

Entry identity includes metric Capex, normalized CIK, exact accession, 10-K form,
filing date, primary document, report date, annual start/end, exact taxonomy
namespace/local concept, empty dimensions, normalized exact USD, positive exact
expected Decimal, scope classification and selected instance URL/hash. Reviewed
records require immutable IDs, review milestone/date, rationale, evidence kind,
exact selected SEC location, digest and entry association. No wildcard year,
issuer-wide scope, accession prefix, 10-K/A or future filing approval.

Retrieval stays outside normalization. A separate registered-entry artifact
manifest, analogous to curated D&A, retrieves required bytes only for registered
filings. The narrow curated Capex resolver verifies digests and re-parses the
instance to bind supplied occurrence/context/unit evidence to those bytes.
It also verifies all mandatory review records. Missing evidence leaves the
fallback unavailable; malformed/tampered linkage is a structural data error.
Do not alter `filing_xbrl`, generic historical selection or generic Capex policy.

## Selection, duplicate and failure rules

1. Run the existing approved direct policy first. Preserve direct ambiguity;
   do not repair it with a curated candidate. Unregistered entries retain current
   behavior, including any legitimate direct resolution.
2. For a registered identity, validate selected source/form/annual authority and
   mandatory reviewed byte evidence before acceptance. Full namespace matters.
   A nil collision for the relevant identity, broken context/unit link, malformed
   numeric value or inconsistent source/accession metadata is a structural error,
   never a harmless duplicate or zero.
3. Exclude structurally valid wrong-entity, wrong-period, other-concept,
   dimensioned or non-USD observations with ordered reasons. They cannot confirm
   or conflict with a valid nondimensional operand. Do not collapse across these
   differences; support facts remain separately typed.
4. Group eligible occurrences by exact namespace/concept, normalized CIK,
   accession, authoritative start/end, empty dimensions, normalized exact USD,
   exact Decimal and non-nil status. Different context/unit IDs and lexical
   values/decimals may confirm only if all semantic fields agree. Preserve every
   representation in document order. Never sum duplicates or round values to
   create equivalence.
5. Exactly one signature matching the reviewed expected value may resolve.
   No eligible facts or a single changed value leaves curated acceptance missing,
   with a diagnostic. Multiple eligible numeric values remain ambiguous even if
   one matches the expected number. No precision tolerance, averaging or picking
   a preferred matching occurrence. Negative values receive no sign repair.
6. If a valid existing direct result coexists with complete eligible curated
   evidence, equal values confirm: retain the direct concept as selected and
   attach supporting policy/review provenance. Different values remain ambiguous.
   Invalid/missing curated evidence cannot override a valid direct value; report
   structural errors rather than hide them. Existing direct ambiguity is never
   replaced. Evidence need not be fetched for unregistered filings.
7. Future, amended, incomplete and unregistered entries have no curated approval.
   Mismatched facts do not migrate a reviewed entry to a new period/source.

## Provenance and serialization

Emit a policy-approved reported Capex value, not a fabricated derivation. Retain
policy ID/version/classification, complete entry and review identities, rationale,
selected source/QName/exact numeric value, verified artifact digests, review
locations and ordered exclusions through normalized Capex, standardized output
and serialization. Candidate-only evidence must not absorb dimensional support
or other concepts. Preserve support and relationship metadata separately.

Select the first eligible occurrence deterministically, retain every confirming
occurrence, and distinguish consecutive one-based confirming ordinals from
zero-based original instance ordinals. Each keeps raw/numeric strings, decimals,
nil, context/entity/period/dimensions, original and normalized units, source and
accession. Round trips preserve order, multiplicity, exact Decimal and full
policy/support provenance. Reuse existing historical reviewed-policy conventions
where compatible; explicitly version any necessary serialization extension
without silently changing schema-4 meanings. This milestone changes no schema.
Future normalized-input consumers must retain the supporting policy. ETR,
Operating Tax and NWC have no Capex dependency and gain no invented reference;
future FCFF must subtract the positive magnitude exactly once and cannot infer
integrated readiness from this provenance.

## Reconciliation, tests and next milestone

57 matrix rows: **10 CURATED_DESIGN_GO / 47 NO_ENTRY**. Candidate approval is
5 AMZN / 5 LLY; controls retain 27 CONCEPT_POLICY, 17 DERIVATION and three
METHODOLOGY_BLOCKER routes. No fresh control denial or approved equation.
Production remains Capex **147/57/0**, aggregate **1,885/1,503/11/27/42 = 3,468**;
43 generic executions, seven specialized skips and 204 periods unchanged.

The smallest next milestone is implementation of only this ten-entry curated
reported-value policy. Required tests: immutable model/version/duplicate keys;
exact ten positives and all 47 baseline controls; current-direct precedence,
equal confirmation and conflict; same/different-context duplicates; equivalent
USD IDs and exact lexical Decimal representations; changed/multiple/negative
values; nil collision, broken links, malformed numbers, source/digest swaps;
wrong entity/period/namespace/concept/dimensions/unit; missing required notes;
future/amended/unregistered filings; deterministic support/exclusion/occurrence
serialization and unaffected downstream measures. No generic resolver changes.
After focused checks, targeted ten-accession validation precedes a full suite
and one corpus reconciliation. Conditional implementation target: Capex 157/47/0,
aggregate 1,895/1,493/11/27/42, exactly ten missing-to-resolved changes and no
other state or issuer-execution changes. This is not a measured result.

Design validation checks 57 exact inventory identities, all ten operand/evidence
copies, counts, retained-byte provenance, local links and `git diff --check`.
No tests or corpus rerun; no production code, policies or inventory modifications.

## Wave 28 implementation attempt: representation correction and blocked validation

This section records the historical blockers, subsequently resolved by the
authorized evidence refresh in [Wave 28 results](capex-scope-evidence-results.md).

The ten-entry implementation is uncommitted and not validated for production.
Focused checks pass (158 tests, including ten positives / 47 unchanged controls),
but targeted validation is blocked. No full suite or corpus reconciliation has
run; the production baseline above is not replaced by the conditional target.

The five LLY directory-index hashes in the historical Wave 26/27 inventory/matrix
describe retained UTF-8 `json.dumps(parsed_object)` bytes with default separators,
no indentation and no trailing newline. They do **not** describe original SEC
response bodies. The saved objects' key order makes sorted and unsorted default
serialization identical; the evidence establishes the bytes, not which optional
sort flag was used. Original SEC response bodies were retrieved independently
and their parsed JSON matches the retained objects, but their byte hashes differ.

The uncommitted runtime registry retains the exact old serialized text and hash,
labeled `sha256_retained_reserialized_json_utf8_bytes`, in an explicit correction
audit. Its mandatory URL hash now requires `sha256_sec_response_body_bytes`.
The original response-body fixture preserves bytes as base64, not regenerated
JSON. Both representations are independently hashed and byte-count checked;
only afterward is parsed equality checked. Hash equality is never inferred
from parsed equality. Review facts, values, identities and scope are unchanged.
The historical research inventory and design matrix remain unchanged snapshots;
the correction is a transparent delta in the unpublished runtime registry, not
a silent mutation of a published policy version.

| LLY accession | Retained JSON SHA-256 | Original response-body SHA-256 | Retained / response bytes |
| --- | --- | --- | ---: |
| `0000059478-22-000068` | `858016f796991d93679d370235204efb82fb6a66f55fe27f19cb1a7eb60c73f0` | `0149695203760e7d01fc89e2eee08e18e66af90f39ee8eeccdf990ed938212da` | 15161 / 14143 |
| `0000059478-23-000082` | `ee985125475590789495babe9baf9b58f1f37061e1ffb9b8d9a415f6ad13a646` | `a9e4f89284614558e1be5c40f173c863f6ff494792067151b15175a335c59d29` | 13391 / 12478 |
| `0000059478-24-000065` | `ef461a99e8775dad8d041a98d92f7ccc1e3d2b7e245f9d6d518dd064b7a96048` | `786a0bca7cba5e97c617a2c36fb47647e9588c13e4dbdc7167071417b04ff75f` | 13635 / 12708 |
| `0000059478-25-000067` | `ed645d64c1c072bb04690a492b25a8a79ed8091b576387298bb32d44a2500a62` | `1f183c0d52cd33ffb654b860c62f67e622f221f784b9e90a9c911140729ac1bf` | 13738 / 12804 |
| `0000059478-26-000013` | `97963e357c13675d1b1f1353ff46975b0e57950ca8bcc05330422c97e688c555` | `d0e2ec46b324e0f0a0c53f2a05424eda95e0c250290c2a842603ac19aff8fcbc` | 12312 / 11476 |

Targeted validation then found a **separate 15-artifact AMZN blocker**: R3.htm
(cash flow), R10.htm (accounting policy) and R12.htm (PP&E) for all five selected
accessions currently return bytes different from their reviewed fingerprints.
All 15 extracted report texts equal the retained Wave 26 review texts exactly.
For the first accounting-policy report, requests with Accept `*/*`,
`application/octet-stream` and `text/html` returned the same current body/hash;
that check did not recover the reviewed byte representation. Retained AMZN
records contain parsed text and hashes, not the original HTML bytes, and no
matching raw cache files were found. Other registered artifact hashes matched.
Text equality cannot certify the missing original HTML bytes or bypass the
reviewed-byte contract. No AMZN hash, acceptance rule or expected value was
changed. The precise remaining gap is recovery of those reviewed HTML bodies,
or a separately authorized, explicit review/versioned evidence refresh of the
current 15 rendered bodies preserving the old audit records. Until addressed,
do not run the full suite/corpus, claim ten live resolutions or commit Wave 28.

## Wave 28 completed implementation

The authorized 15-artifact AMZN refresh independently reconfirms scope and
retains unavailable-old-body status and fingerprints separately from approved
new response bodies. Strict byte checks remain in force. Ten positive / 47
control regression, ten-accession validation, 160 focused tests, 569 full-suite
tests and one corpus reconciliation pass. Capex is 157/47/0; aggregate is
1,895/1,493/11/27/42 = 3,468, with all other states/execution unchanged.
Schema 5 preserves the separate Capex audit and full correction/refresh histories.
Next research the five CVX cash PP&E components' acquisition/asset containment;
do not approve aggregate spending or infer component absence. See
[results and next boundary](capex-scope-evidence-results.md#next-bounded-milestone).
