# D&A scope-equivalence evidence design

## Decision and boundary

Phase 1H.4 Wave 19 (2026-10-10): **PARTIAL GO**. Approve the design of
curated, exact-accession acceptance for the five Visa candidates below.
**NO-GO for a generic automated `DepreciationAndAmortization` fallback.**
Automation may enforce reviewed entry eligibility; it cannot infer economic
approval from a label, equal amounts, calculation arcs or cash-flow placement.

Wave 19 was design approval, not production registration; all 94 periods
were missing. Wave 20 implements only the five entries as verified below.
The [Wave 18 inventory](depreciation-amortization-inventory.json)
is unchanged, including its `production_policy_approval: false` fields.
Its research baseline is `1990594ce96dd85f9929b0c312b05509e4692494`;
this milestone starts at `c0b6aa467450816768022fd18ae60cacd43212c8`.
The validated starting commit was pushed before this research.

The positive economic classification for a future registry is
`OPERATING_D_AND_A_EQUIVALENT`. All 89 other periods are `NO_ENTRY`:
unapproved controls, **not 89 fresh reviewed economic denials**.
Wave 18's routing categories remain 31 CONCEPT_POLICY, 33 DERIVATION,
5 ISSUER_EXTENSION and 25 METHODOLOGY_BLOCKER. The controls contain respectively
26, 33, 5 and 25 periods. No root-cause category or standardized state changes.

## Economic equivalence review

The existing [D&A primitive](financial-methodology.md#da-research-status)
is recurring operating depreciation of property/equipment and amortization
of finite-lived operating intangibles, including qualifying capitalized
technology/software. It is not every noncash cash-flow adjustment.

The selected Visa accounting-policy notes describe consolidated Visa and
controlled entities, elimination of intercompany activity, and a payments
technology business that does not issue cards or extend credit. Property,
equipment and technology depreciation/amortization starts when assets are
ready for use, follows useful lives, and includes purchased, developed and
acquired software. Finite-lived intangible amortization is separately identified
in the intangible note; goodwill and indefinite-lived assets are not amortized.
These asset classes, the consolidated operating-expense presentation, and the
separate treatment below establish the perimeter. The evidence is not a claim
that every acquisition or every future Visa filing has the same perimeter.

| Scope item | Reviewed treatment / acceptance limit |
|---|---|
| Property/equipment, leasehold improvements and technology/software | Include their recurring expense in the already-reported consolidated combined D&A; do not add the property note again. Leasehold-improvement depreciation is not ROU lease expense. |
| Finite-lived acquired intangibles | Include recurring amortization already in the combined amount. Do not add the separately tagged note amount again. |
| Goodwill, indefinite-lived assets and impairment | Exclude impairment and goodwill/indefinite-lived balances. Accounting policies distinguish useful-life expense from impairment recognition. 2021/2022 explicitly disclose no intangible/goodwill impairment in their three-year histories; later policies disclose annual review conclusions and no period-end indicators. These statements do not establish a zero for every possible impairment category. No impairment-inclusive tag is accepted. |
| Accretion, financing and investment items | No accretion-inclusive substitute, debt discount/issuance amortization or investment impairment enters this approval. Selected policies place investment income/loss and credit impairment outside this asset-expense perimeter. No absence-based zero or residual subtraction. |
| Client incentive / contract costs | Capitalized incentive payments amortized against net revenue are separately described and separately represented in cash flow. They are not finite-lived operating-asset D&A for this primitive. Some incentives exchanged for distinct goods/services are operating expenses; that does not make incentive amortization D&A. |
| Pension/tax amortization | Exclude actuarial/prior-service and tax incidental facts; these are not consumption of the approved asset classes. |
| Leases | Operating ROU assets are reported in Other assets and lease costs are separately discussed in G&A (2025: primarily G&A). Lease costs, ROU movement and lease impairment are not added to D&A. 2021/2022 explicitly state no finance leases at the annual end; 2023–2025 do not repeat that statement. Do not infer annual finance-lease amortization is zero from either silence or an end-date balance. Acceptance rests on the specifically described property/technology and finite-lived asset expense perimeter, not presumed absence of leases. No lease adjustment or integrated lease model is approved. |
| Business scope | Preserve the exact selected consolidated annual scope, including acquired consolidated technology/intangibles where recognized. No segment, affiliate, comparative from a later filing, carve-out or discontinued perimeter is substituted. |

### Exact candidate facts and corroboration

All five candidates are `us-gaap:DepreciationAndAmortization`, exact USD,
non-nil, nondimensional duration facts. CIK is 1403161, form 10-K, report date
equals annual end. Each has two identical eligible occurrences; their raw and
numeric values agree, unit ID is `usd`, decimals is `-6`, and entity scheme
is `http://www.sec.gov/CIK` with identifier `0001403161`.
No occurrence is thrown away.

| Accession | Annual start / end | Exact namespace | Exact USD value | Context ID | Original instance ordinals |
|---|---|---|---:|---|---|
| `0001403161-21-000060` | 2020-10-01 / 2021-09-30 | `http://fasb.org/us-gaap/2021-01-31` | 804000000 | `ia9ffd445549f441e9121047e42233bae_D20201001-20210930` | 202, 505 |
| `0001403161-22-000081` | 2021-10-01 / 2022-09-30 | `http://fasb.org/us-gaap/2022` | 861000000 | `i501005a952cc4b068e83ae86d38ef829_D20211001-20220930` | 235, 514 |
| `0001403161-23-000099` | 2022-10-01 / 2023-09-30 | `http://fasb.org/us-gaap/2023` | 943000000 | `c-1` | 225, 499 |
| `0001403161-24-000058` | 2023-10-01 / 2024-09-30 | `http://fasb.org/us-gaap/2024` | 1034000000 | `c-1` | 185, 474 |
| `0001403161-25-000089` | 2024-10-01 / 2025-09-30 | `http://fasb.org/us-gaap/2025` | 1220000000 | `c-1` | 216, 504 |

Original ordinals above are the inventory's zero-based full-instance ordinals,
not the existing policy provenance's consecutive one-based confirming ordinals.
Preserve both meanings explicitly; do not pass 202 or 505 to a field whose
validator requires 1 and 2. Primary documents, filing dates, normalized context
identities, units and full statement/calculation definitions are frozen in the
unchanged companion JSON; they form part of each entry, not optional lookups
against a later filing.

| Annual end | Property/equipment/technology expense (USD m) | Finite-lived intangible expense (USD m) | Combined D&A (USD m) | Review reconciliation |
|---|---:|---:|---:|---|
| 2021-09-30 | 721 | 83 | 804 | Exact displayed-component sum |
| 2022-09-30 | 771 | 90 | 861 | Exact displayed-component sum |
| 2023-09-30 | 867 | 76 | 943 | Exact displayed-component sum |
| 2024-09-30 | 955 | 79 | 1,034 | Exact displayed-component sum |
| 2025-09-30 | 1,100 | 78 | 1,220 | Property note displays $1.1 billion, XBRL decimals -8; rounded sum 1,178 differs by 42 |

For 2025, the note's property amount has a 50m half-unit precision interval;
the intangible and combined facts each have 0.5m. Their independent reported
intervals overlap (maximum summed comparison bound 51m). The 42m difference
is compatible with the explicitly submitted precision. **This does not prove
equivalence by approximate equality:** asset policies, distinct finite-lived
expense notes and operating presentation establish scope first. It corroborates
that scope without manufacturing a missing 42m component or inferring an exact
1,142m property expense. Accept the reported exact numeric candidate 1,220m,
not a derived 1,178m. This accession-specific reviewed precision explanation
is retained with evidence; no runtime generic tolerance or equation is approved.

The property note's `DepreciationAndAmortization` facts carry
`us-gaap:PropertyPlantAndEquipmentByTypeAxis` with Visa's
`PropertyEquipmentAndTechnologyMember`. They are supporting scope evidence,
not nondimensional alternatives. Intangible note
`us-gaap:AmortizationOfIntangibleAssets` is also support, not a replacement
for the combined primitive. Future schedules and accumulated amortization
are neither operands nor candidate expense facts.

### Reviewed statement and note locations

The inventory retains the exact submitted operating statement role
`http://wwww.visa.com/role/CONSOLIDATEDSTATEMENTSOFOPERATIONS` (literal four
w's), its definition, and the cash-flow role. The combined caption is
Depreciation and amortization. The submitted operating calculation is
`CostsAndExpenses -> DepreciationAndAmortization` with weight +1; cash flow
also has a +1 add-back relationship. Operating locations are R4.htm in 2021
and R5.htm in 2022–2025, recorded in submitted presentation metadata.
Role membership is concept-level evidence; it does not independently assign
a rendered statement location to each repeated instance occurrence.

The following previously retrieved statement/notes were re-read from retained
bytes and verified against their committed SHA-256. No additional SEC material
or unchanged-link HTTP revalidation was needed. Exact instance source/hash
and all linkbase artifact URLs remain in the companion inventory.

| Accession | Reviewed location and direct SEC URL | Frozen SHA-256 |
|---|---|---|
| `0001403161-21-000060` | [CONSOLIDATED STATEMENTS OF CASH FLOWS](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/R8.htm) | `c28f72373b0a27cb6e83c20ae1dd75f70fa50382ed8730272136cb981dba154b` |
| `0001403161-21-000060` | [Property, Equipment and Technology, Net](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/R15.htm) | `7da518239e679b1c7cbe0da441ce0cadcdf5015c6846a8a84d1d69bb1cfbaab5` |
| `0001403161-21-000060` | [Intangible Assets and Goodwill](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/R16.htm) | `c3dc87158e3d49fa7ceaf58c0d3ed8d17f305eda8f1368a44705225a441ac004` |
| `0001403161-21-000060` | [Summary of Significant Accounting Policies](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/R9.htm) | `ac805ab3d1f20a592ae0f5d21a6838cbaf06f9ce474b8a5bccbe70851ea4ed9e` |
| `0001403161-21-000060` | [Leases](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/R17.htm) | `04a006ce65ab5ae458164b2c4cd1f55a6028a7f495e1cdad3cf828101685e46d` |
| `0001403161-22-000081` | [CONSOLIDATED STATEMENTS OF CASH FLOWS](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/R9.htm) | `3b0d60601c8d2ebeb639817cf883bcea748274fffb8269a589f8859c518b5349` |
| `0001403161-22-000081` | [Property, Equipment and Technology, Net](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/R16.htm) | `87d14fb66b531775ac1e2330133ebdc157de4259e349100ef5c3c78aa7548b7e` |
| `0001403161-22-000081` | [Intangible Assets and Goodwill](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/R17.htm) | `8acacdcc6651ba8a1b7d13de5875317912f639b97b1c304a500cb25c86b0b034` |
| `0001403161-22-000081` | [Summary of Significant Accounting Policies](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/R10.htm) | `7e62e3e8ed85734bedcadb37e0c0a4010b9afb036b44dbc9fd8d5f01ce7b271c` |
| `0001403161-22-000081` | [Leases](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/R18.htm) | `40a1779d86e52aa04bcd7d2312e2849cefe217cded862cc2436021c1c1a848b4` |
| `0001403161-23-000099` | [CONSOLIDATED STATEMENTS OF CASH FLOWS](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/R9.htm) | `96de42105506f8e95dae81e826789bd9e37533f82112cbbb3daff5b411b068fc` |
| `0001403161-23-000099` | [Property, Equipment and Technology, Net](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/R16.htm) | `4bb2f4423967bb338b30a8e1fb99fbd8c6d4c6a8f8fa0414665186273f7d3ae5` |
| `0001403161-23-000099` | [Intangible Assets and Goodwill](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/R17.htm) | `5bc05f247a27bd102f119ebc71c8b38c8004314c79a720be030975b3cf94ac86` |
| `0001403161-23-000099` | [Summary of Significant Accounting Policies](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/R10.htm) | `e83387f6e00793e2475d16e7c72414eea2b944599150f38d59b471397d49f47f` |
| `0001403161-23-000099` | [Leases](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/R18.htm) | `2582305cd15c2c5e9555da56e9b8bb687cfc324a10bf6c2a30d7710872e62add` |
| `0001403161-24-000058` | [CONSOLIDATED STATEMENTS OF CASH FLOWS](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/R9.htm) | `9640619c9453b264de415c3b04086a779892cceab78740b67ffc389fef990327` |
| `0001403161-24-000058` | [Property, Equipment and Technology, Net](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/R16.htm) | `925f01ce13f6d2d949b5f00a4f22e796d5402930e03ea8d62a846490e3db201c` |
| `0001403161-24-000058` | [Intangible Assets and Goodwill](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/R17.htm) | `ffcd03c9df1b18a19b13e90f8d34b86d0c538925e54452dd6891377d0dd889b1` |
| `0001403161-24-000058` | [Summary of Significant Accounting Policies](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/R10.htm) | `e3feafdea01bd9da17d7dc4119225ec798e618dfc19e53825013399b2f6e7da3` |
| `0001403161-24-000058` | [Leases](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/R18.htm) | `f2f7c263a9603945348001ac4995b95d534f96d4b463b91f7f8ce7d9ce7dd9c8` |
| `0001403161-25-000089` | [CONSOLIDATED STATEMENTS OF CASH FLOWS](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/R9.htm) | `196107563e584ab86c233eafb6ba42d8c080a2037b5da53bdb9fa5bf66441f8f` |
| `0001403161-25-000089` | [Property, Equipment and Technology, Net](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/R17.htm) | `457e61964601e92e632ce9707ba8efed6d730ef537c097dfe692fb3f3a766db9` |
| `0001403161-25-000089` | [Intangible Assets and Goodwill](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/R18.htm) | `b025d70dc25c5fe011456d1d7ac8888cabcb48396e055e6e14b3761e94266e5e` |
| `0001403161-25-000089` | [Summary of Significant Accounting Policies](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/R11.htm) | `3fc9ae7ff8367692532170bc1f070127be73562c1b9428ec209e73e186aede85` |
| `0001403161-25-000089` | [Leases](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/R19.htm) | `36841640d85b26bd4c07a592f45587e4fecd569b23dea830e415463b8224581a` |

## Frozen Wave 19 curated foundation (implemented in Wave 20)

### Immutable registry and reviewed evidence

Use an immutable tuple registry of frozen validated entry/evidence models;
proposed policy ID `d_and_a_scope_equivalence`, version `1`, serialized identity
`d_and_a_scope_equivalence_v1`. Changes to scope, entry set or evidence require
a new version; never mutate a previously published version. Only the five
exact rows above can carry `OPERATING_D_AND_A_EQUIVALENT`. Reject duplicate
registry keys, incomplete evidence, unsupported classification and malformed
identity at model construction; registration must never follow automatically
from inventory flags or issuer name.

Entry identity freezes metric D&A; normalized CIK; accession; form; filed date;
primary document; report date; authoritative annual start/end; exact namespace,
taxonomy and local concept; empty dimensions; exact USD unit; approved scope
classification; expected exact Decimal value; selected instance URL/hash; and
reviewed evidence identities. The full namespace is checked, not just
`us-gaap` or a local-name match. No wildcard year, accession prefix or issuer-wide
approval, no 10-K/A and no later comparative substitution.

Every entry requires approved reviewed evidence records with immutable ID,
review date, rationale, selected SEC URL, precise statement/note/paragraph
location, research artifact, content digest and exact entry association.
Freeze the five note records per accession above, selected presentation and
calculation evidence, property and finite-lived supporting fact identities,
and the 2025 precision explanation. A malformed digest, swapped-accession
note, missing mandatory item or contradictory scope is not complete approval.
Hashes identify reviewed bytes; they do not themselves prove accounting scope.
The JSON is a research snapshot, not the runtime registry or a network cache.

### Eligibility, selection and conflict boundary

Place acceptance narrowly in a curated D&A resolver composed at historical
normalization. Do not change the parser, generic historical selection or
generic D&A concept policy; do not generalize Microsoft's component derivation.

1. Resolve the existing approved direct concept first. Existing direct ambiguity
   is never repaired by curated acceptance. With no registered entry, preserve
   the existing direct/derived/missing behavior.
2. For a registered entry, verify selected filing, authoritative annual identity,
   source metadata, reviewed evidence and exact QName/entity/unit/scope before
   evaluating any candidate. Broken links cannot be made eligible by equality.
3. Exclude structurally valid wrong-entity, wrong-period, other-concept,
   dimensioned and non-USD facts from the approved candidate set. Retain exclusion
   reasons; such facts neither confirm nor conflict with a valid candidate.
   Dimensional support above is not reclassified as a nondimensional operand.
4. Group eligible facts by exact namespace/taxonomy/concept, normalized CIK,
   accession, annual start/end, empty dimensions, exact normalized USD unit,
   exact Decimal numeric value and non-nil status. Preserve every occurrence
   in document order, including raw value, decimals and context/unit IDs.
   Different IDs or lexical precision may confirm only if the full semantic
   signature agrees. No float conversion, nearest value or precision tolerance.
5. Exactly one signature with the reviewed expected value may resolve.
   A single changed value receives no policy approval (missing fallback with
   explicit mismatch); two different eligible numeric signatures remain
   ambiguous, even if one equals the registered expected value.
   No eligible fact remains missing. Nil/numeric collision in the same relevant
   identity, missing/broken context or unit links, malformed numeric evidence,
   or inconsistent source/accession metadata is a structural data error,
   not an excluded harmless duplicate or an implicit zero.
6. When an approved current direct fact and an eligible curated result coexist,
   equal exact values confirm: keep the current direct concept as selected,
   retaining the curated confirmation and its policy provenance. Differing
   eligible values remain ambiguous. Never replace a direct ambiguity, average,
   prioritize a reviewed expected number over conflict or hide a conflict.
7. Retain existing direct-first MSFT behavior, its exact component policy and
   all unregistered periods. Future, amended, mismatched-namespace and unregistered
   filings receive no curated approval; a legitimately existing direct result
   is not suppressed merely because it has no curated entry.

### Provenance, normalized output and serialization

A curated acceptance is a policy-approved reported value, **not a component
derivation**. No artificial ADD operand or sum is emitted. Reuse the generic
`HistoricalPolicyProvenance`/`ReviewedPolicyEvidence` conventions where
compatible, not Pretax-specific economic classifications.

Retain policy ID/version, D&A scope classification, full registry identity,
selected QName/namespace, exact Decimal value, instance digest, every reviewed
note/statement record and all confirming filing-XBRL occurrences. Keep a
deterministic selected first eligible occurrence plus the ordered confirming
sequence; original context ID/entity/period/dimensions, original and normalized
unit, raw numeric representation, decimals, nil and source/accession survive.
Use consecutive one-based confirming occurrence ordinals as existing provenance
requires, and an explicit original-instance ordinal in D&A-specific audit
metadata. Do not discard same-context repetition or substitute a set.

Supporting dimensional property and finite-lived intangible facts, presentation
arcs and precision review must remain separately typed reviewed support, not
put into the existing nondimensional candidate-only `filing_xbrl_evidence`
tuple (its validator prohibits dimensions and other concepts).
Keep the support records and exclusion decisions through normalized D&A,
standardized output and serialization; an equal direct selection retains the
supporting policy rather than attributing generic direct approval to the policy.

The implementation must explicitly version any serialization extension that
adds this audit/support structure (next schema version 4, preserving existing
schema-3 meanings). Exact Decimal representation must survive serialization,
not just a lossy numeric summary. Round-trip tests must assert metadata,
multiplicity and order, as well as value. No schema changes occur in Wave 19.
Reported ETR depends on Tax/Pretax, not D&A: it must remain unchanged; no invented
ETR supporting-policy relationship. Future FCFF consumers may use only the
approved primitive and must retain its origin.

## Complete 94-period acceptance reconciliation

This matrix copies exact frozen inventory identities. `CURATED_DESIGN_GO`
means reviewed design acceptance, not a production resolution.
`NO_ENTRY` means no acceptance in v1; controls retain Wave 18 research routing
without a new claim of fresh economic denial. Reviewed denials concern specific
candidate substitutions (dimensioned property-only amount, incentive/pension
amortization, impairment/accretion-inclusive or lease adjustments), not all
89 issuer-periods.

| Ticker / CIK | Selected accession | Annual start / end | Wave 18 routing | Wave 19 disposition |
|---|---|---|---|---|
| GOOGL / 1652044 | `0001652044-22-000019` | 2021-01-01 / 2021-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GOOGL / 1652044 | `0001652044-23-000016` | 2022-01-01 / 2022-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GOOGL / 1652044 | `0001652044-24-000022` | 2023-01-01 / 2023-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GOOGL / 1652044 | `0001652044-25-000014` | 2024-01-01 / 2024-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GOOGL / 1652044 | `0001652044-26-000018` | 2025-01-01 / 2025-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| AVGO / 1730168 | `0001730168-21-000153` | 2020-11-02 / 2021-10-31 | `DERIVATION` | `NO_ENTRY` |
| AVGO / 1730168 | `0001730168-22-000118` | 2021-11-01 / 2022-10-30 | `DERIVATION` | `NO_ENTRY` |
| AVGO / 1730168 | `0001730168-23-000096` | 2022-10-31 / 2023-10-29 | `DERIVATION` | `NO_ENTRY` |
| AVGO / 1730168 | `0001730168-24-000139` | 2023-10-30 / 2024-11-03 | `DERIVATION` | `NO_ENTRY` |
| AVGO / 1730168 | `0001730168-25-000121` | 2024-11-04 / 2025-11-02 | `DERIVATION` | `NO_ENTRY` |
| TSLA / 1318605 | `0000950170-22-000796` | 2021-01-01 / 2021-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| TSLA / 1318605 | `0000950170-23-001409` | 2022-01-01 / 2022-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| TSLA / 1318605 | `0001628280-24-002390` | 2023-01-01 / 2023-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| TSLA / 1318605 | `0001628280-25-003063` | 2024-01-01 / 2024-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| TSLA / 1318605 | `0001628280-26-003952` | 2025-01-01 / 2025-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| AMD / 2488 | `0000002488-22-000016` | 2020-12-27 / 2021-12-25 | `ISSUER_EXTENSION` | `NO_ENTRY` |
| AMD / 2488 | `0000002488-23-000047` | 2021-12-26 / 2022-12-31 | `ISSUER_EXTENSION` | `NO_ENTRY` |
| AMD / 2488 | `0000002488-24-000012` | 2023-01-01 / 2023-12-30 | `ISSUER_EXTENSION` | `NO_ENTRY` |
| AMD / 2488 | `0000002488-25-000012` | 2023-12-31 / 2024-12-28 | `ISSUER_EXTENSION` | `NO_ENTRY` |
| AMD / 2488 | `0000002488-26-000018` | 2024-12-29 / 2025-12-27 | `ISSUER_EXTENSION` | `NO_ENTRY` |
| V / 1403161 | `0001403161-21-000060` | 2020-10-01 / 2021-09-30 | `CONCEPT_POLICY` | `CURATED_DESIGN_GO` |
| V / 1403161 | `0001403161-22-000081` | 2021-10-01 / 2022-09-30 | `CONCEPT_POLICY` | `CURATED_DESIGN_GO` |
| V / 1403161 | `0001403161-23-000099` | 2022-10-01 / 2023-09-30 | `CONCEPT_POLICY` | `CURATED_DESIGN_GO` |
| V / 1403161 | `0001403161-24-000058` | 2023-10-01 / 2024-09-30 | `CONCEPT_POLICY` | `CURATED_DESIGN_GO` |
| V / 1403161 | `0001403161-25-000089` | 2024-10-01 / 2025-09-30 | `CONCEPT_POLICY` | `CURATED_DESIGN_GO` |
| INTC / 50863 | `0000050863-22-000007` | 2020-12-27 / 2021-12-25 | `DERIVATION` | `NO_ENTRY` |
| INTC / 50863 | `0000050863-23-000006` | 2021-12-26 / 2022-12-31 | `DERIVATION` | `NO_ENTRY` |
| INTC / 50863 | `0000050863-24-000010` | 2023-01-01 / 2023-12-30 | `DERIVATION` | `NO_ENTRY` |
| INTC / 50863 | `0000050863-25-000009` | 2023-12-31 / 2024-12-28 | `DERIVATION` | `NO_ENTRY` |
| INTC / 50863 | `0000050863-26-000011` | 2024-12-29 / 2025-12-27 | `DERIVATION` | `NO_ENTRY` |
| WMT / 104169 | `0000104169-22-000012` | 2021-02-01 / 2022-01-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| WMT / 104169 | `0000104169-23-000020` | 2022-02-01 / 2023-01-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| WMT / 104169 | `0000104169-24-000056` | 2023-02-01 / 2024-01-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| WMT / 104169 | `0000104169-25-000021` | 2024-02-01 / 2025-01-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| WMT / 104169 | `0000104169-26-000055` | 2025-02-01 / 2026-01-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| ABBV / 1551152 | `0001551152-22-000007` | 2021-01-01 / 2021-12-31 | `DERIVATION` | `NO_ENTRY` |
| ABBV / 1551152 | `0001551152-23-000011` | 2022-01-01 / 2022-12-31 | `DERIVATION` | `NO_ENTRY` |
| ABBV / 1551152 | `0001551152-24-000011` | 2023-01-01 / 2023-12-31 | `DERIVATION` | `NO_ENTRY` |
| ABBV / 1551152 | `0001551152-25-000020` | 2024-01-01 / 2024-12-31 | `DERIVATION` | `NO_ENTRY` |
| ABBV / 1551152 | `0001551152-26-000008` | 2025-01-01 / 2025-12-31 | `DERIVATION` | `NO_ENTRY` |
| MA / 1141391 | `0001141391-22-000023` | 2021-01-01 / 2021-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| MA / 1141391 | `0001141391-23-000020` | 2022-01-01 / 2022-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| MA / 1141391 | `0001141391-24-000022` | 2023-01-01 / 2023-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| MA / 1141391 | `0001141391-25-000011` | 2024-01-01 / 2024-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| MA / 1141391 | `0001141391-26-000013` | 2025-01-01 / 2025-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LRCX / 707549 | `0000707549-22-000107` | 2021-06-28 / 2022-06-26 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LRCX / 707549 | `0000707549-23-000102` | 2022-06-27 / 2023-06-25 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LRCX / 707549 | `0000707549-24-000106` | 2023-06-26 / 2024-06-30 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LRCX / 707549 | `0000707549-25-000075` | 2024-07-01 / 2025-06-29 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LRCX / 707549 | `0000707549-26-000037` | 2025-06-30 / 2026-06-28 | `CONCEPT_POLICY` | `NO_ENTRY` |
| AMAT / 6951 | `0000006951-23-000041` | 2022-10-31 / 2023-10-29 | `CONCEPT_POLICY` | `NO_ENTRY` |
| AMAT / 6951 | `0000006951-24-000044` | 2023-10-30 / 2024-10-27 | `CONCEPT_POLICY` | `NO_ENTRY` |
| AMAT / 6951 | `0001628280-25-056742` | 2024-10-28 / 2025-10-26 | `CONCEPT_POLICY` | `NO_ENTRY` |
| MRK / 310158 | `0000310158-22-000003` | 2021-01-01 / 2021-12-31 | `DERIVATION` | `NO_ENTRY` |
| MRK / 310158 | `0001628280-23-005061` | 2022-01-01 / 2022-12-31 | `DERIVATION` | `NO_ENTRY` |
| MRK / 310158 | `0001628280-24-006850` | 2023-01-01 / 2023-12-31 | `DERIVATION` | `NO_ENTRY` |
| MRK / 310158 | `0001628280-25-007732` | 2024-01-01 / 2024-12-31 | `DERIVATION` | `NO_ENTRY` |
| MRK / 310158 | `0000310158-26-000063` | 2025-01-01 / 2025-12-31 | `DERIVATION` | `NO_ENTRY` |
| GE / 40545 | `0000040545-22-000008` | 2021-01-01 / 2021-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GE / 40545 | `0000040545-23-000023` | 2022-01-01 / 2022-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GE / 40545 | `0000040545-24-000027` | 2023-01-01 / 2023-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GE / 40545 | `0000040545-25-000015` | 2024-01-01 / 2024-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| GE / 40545 | `0000040545-26-000008` | 2025-01-01 / 2025-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| PM / 1413329 | `0001413329-22-000011` | 2021-01-01 / 2021-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| PM / 1413329 | `0001413329-23-000025` | 2022-01-01 / 2022-12-31 | `DERIVATION` | `NO_ENTRY` |
| TXN / 97476 | `0000097476-22-000009` | 2021-01-01 / 2021-12-31 | `DERIVATION` | `NO_ENTRY` |
| TXN / 97476 | `0000097476-23-000007` | 2022-01-01 / 2022-12-31 | `DERIVATION` | `NO_ENTRY` |
| TXN / 97476 | `0000097476-24-000007` | 2023-01-01 / 2023-12-31 | `DERIVATION` | `NO_ENTRY` |
| TXN / 97476 | `0000097476-25-000007` | 2024-01-01 / 2024-12-31 | `DERIVATION` | `NO_ENTRY` |
| TXN / 97476 | `0000097476-26-000059` | 2025-01-01 / 2025-12-31 | `DERIVATION` | `NO_ENTRY` |
| GEV / 1996810 | `0001996810-25-000011` | 2024-01-01 / 2024-12-31 | `DERIVATION` | `NO_ENTRY` |
| GEV / 1996810 | `0001996810-26-000015` | 2025-01-01 / 2025-12-31 | `DERIVATION` | `NO_ENTRY` |
| SNDK / 2023554 | `0002023554-25-000034` | 2024-06-29 / 2025-06-27 | `CONCEPT_POLICY` | `NO_ENTRY` |
| SNDK / 2023554 | `0001628280-26-057406` | 2025-06-28 / 2026-07-03 | `CONCEPT_POLICY` | `NO_ENTRY` |
| ORCL / 1341439 | `0001564590-22-023675` | 2021-06-01 / 2022-05-31 | `DERIVATION` | `NO_ENTRY` |
| ORCL / 1341439 | `0000950170-23-028914` | 2022-06-01 / 2023-05-31 | `DERIVATION` | `NO_ENTRY` |
| ORCL / 1341439 | `0000950170-24-075605` | 2023-06-01 / 2024-05-31 | `DERIVATION` | `NO_ENTRY` |
| ORCL / 1341439 | `0000950170-25-087926` | 2024-06-01 / 2025-05-31 | `DERIVATION` | `NO_ENTRY` |
| ORCL / 1341439 | `0001193125-26-277521` | 2025-06-01 / 2026-05-31 | `DERIVATION` | `NO_ENTRY` |
| LIN / 1707925 | `0001628280-22-004180` | 2021-01-01 / 2021-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LIN / 1707925 | `0001628280-23-005434` | 2022-01-01 / 2022-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LIN / 1707925 | `0001628280-24-007424` | 2023-01-01 / 2023-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LIN / 1707925 | `0001628280-25-007990` | 2024-01-01 / 2024-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| LIN / 1707925 | `0001628280-26-011430` | 2025-01-01 / 2025-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| IBM / 51143 | `0001558370-22-001584` | 2021-01-01 / 2021-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| IBM / 51143 | `0001558370-23-002376` | 2022-01-01 / 2022-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| IBM / 51143 | `0000051143-24-000012` | 2023-01-01 / 2023-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| IBM / 51143 | `0000051143-25-000015` | 2024-01-01 / 2024-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| IBM / 51143 | `0000051143-26-000010` | 2025-01-01 / 2025-12-31 | `METHODOLOGY_BLOCKER` | `NO_ENTRY` |
| VZ / 732712 | `0000732712-22-000008` | 2021-01-01 / 2021-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| VZ / 732712 | `0000732712-23-000012` | 2022-01-01 / 2022-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| VZ / 732712 | `0000732712-24-000010` | 2023-01-01 / 2023-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| VZ / 732712 | `0000732712-25-000006` | 2024-01-01 / 2024-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |
| VZ / 732712 | `0000732712-26-000007` | 2025-01-01 / 2025-12-31 | `CONCEPT_POLICY` | `NO_ENTRY` |

Totals: **94 unique identities = 5 CURATED_DESIGN_GO + 89 NO_ENTRY**.
Five Visa annual facts have ten confirming nondimensional occurrences and five
distinct eligible signatures (one per accession). Potential new coverage is
five, never 31 or 94. Production remains D&A **110 resolved / 94 missing /
0 ambiguous** and Operating Income **194 / 10 / 0**. Aggregate remains
**1,880 resolved / 1,508 missing / 11 ambiguous / 27 methodology-blocked /
42 not-comparable = 3,468**. Project counts are carried forward, not remeasured.

## Implementation gate, validation and next milestone

Smallest next milestone: implement only the five-entry curated D&A foundation
and provenance/output support after this design, with 5 positive / 89 no-entry
regression. Other 89 periods require separate evidence/scope/component research;
nothing in this design approves their facts, equations or issuer extensions.

Required tests before production: immutable models/versioning and duplicate
keys; all five exact identities/namespaces/values; missing or swapped review
records/digests; direct precedence/equal confirmation/conflict; same-context
duplicates and equivalent different contexts/USD unit IDs; same exact Decimal
with different raw/decimals; differing eligible numbers; wrong CIK/accession/
annual dates/QName/unit/dimensions; nil collision, broken links and malformed
source metadata; amendments/future/unregistered filings; property dimension
exclusion; separate support provenance and original versus confirming ordinals;
normalized-to-standardized-to-serialized round trips; five approved candidates
and all 89 no-entry controls. The 2025 reported candidate is 1,220m, not the
rounded component sum; no tolerance leaks into eligibility or conflict handling.
Regress existing MSFT D&A and unaffected Pretax/ETR/Operating Income.

Then targeted live validation must produce exactly five new D&A resolutions,
before full tests/corpus. Expected implementation-only D&A would be 115 / 89 /
0, aggregate 1,885 / 1,503 / 11 / 27 / 42 across 3,468 states, with no other
metric or issuer execution changes. Stop on any mismatch. Those are future
acceptance targets, not Wave 19 results.

Wave 19 validation checks all 94 identities against the frozen JSON, selected
metadata/authoritative annual evidence, categories and candidate signatures;
five-by-two occurrences and reviewed raw-byte digests; supporting arithmetic/
explicit precision; local documentation links and selected-directory SEC link
identity; and `git diff --check`. No new SEC URLs, tests, production normalization
or corpus rerun. Forecast/FCFF/DCF remains paused through Phase 1H.6.

## Wave 20 implementation and verified results

Implemented from clean main at `378d7ebe3ef26c272f37c4d6e5240f2460f5dbfc`,
after pushing that validated design. The five-entry immutable policy ID is
`d_and_a_scope_equivalence`, version `1`. Its source registry is separate from
the unchanged Wave 18 research JSON; controls are no-entry, not fresh denials.
The parser, generic D&A policy and Microsoft derivation are unchanged.

The corpus pipeline retrieves only registered entries' required artifacts:
the instance, schema/presentation/calculation files and five reviewed statement/
notes. SHA-256 checks cover all nine sources per entry and re-parsing binds the
supplied structural instance to its verified bytes. Missing or changed artifacts
raise a structural policy error in this explicit verification boundary; absence
of a supplied bundle never implies acceptance in normalization. Exact full
filing/annual/QName/entity/USD identity gates candidate selection. A changed
single eligible numeric value yields explicit curated-evidence-mismatch missing;
differing eligible values stay ambiguous.

Two nondimensional occurrences resolve each reported amount; original instance
ordinals remain 202/505, 235/514, 225/499, 185/474 and 216/504 respectively.
Each policy retains confirming ordinals 1/2, original representations, all
reviewed locations/digests, two separately typed asset-support facts, submitted
relationship definitions and ordered eligibility/exclusion audit. Schema 4
preserves this complete support and exact Decimal serialization; no fake ADD
derivation or component residual is emitted. Equal current direct values retain
their chosen concept and the supporting curated policy. Downstream normalized-
metric operands can retain the same policy support; Reported ETR has no D&A
dependency and is unchanged.

Validation on 2026-10-10:

- Focused policy/normalization/output/prior-curated/corpus-interface tests:
  **200 passed**, including 39 new D&A tests and the complete 94-row regression.
- Inventory regression: **five approved Visa resolutions / 89 unchanged missing
  controls**. Routing totals stay 31/33/5/25 in the historical research snapshot.
- Targeted production normalization: all five exact selected accessions resolve
  **804m / 861m / 943m / 1,034m / 1,220m**. Every other normalized metric is equal
  to a same-input run without the curated bundles. Fifty-five retained SEC
  resources were reused; one Company Facts request was made.
- Complete suite run once: **552 passed**.
- One production corpus run: **43/43 generic issuers complete**, zero failures,
  seven specialized skips, 204 periods and 3,468 states.
- D&A: repository-artifact baseline **110 resolved / 94 missing / 0 ambiguous**
  becomes **115 / 89 / 0**; exactly five missing-to-resolved changes.
- Aggregate: **1,885 resolved / 1,503 missing / 11 ambiguous /
  27 methodology-blocked / 42 not-comparable**. All other measure states, 89
  controls, issuer completion, frozen selections and specialized skips agree
  with the baseline. Operating Income remains **194 / 10 / 0**; Pretax and
  Reported ETR remain **167 / 37 / 0** each.
- `compileall`, local documentation links and `git diff --check` pass.

Lengthy validation logs/artifacts are outside the repository:
`/tmp/da-wave20-focused.log`, `/tmp/da-wave20-full-tests.log`,
`/tmp/da-wave20-targeted.log`, `/tmp/da-wave20-corpus-validation.log` and
`/tmp/da-wave20-corpus.json`. The corpus reuses 288 retained resources and makes
257 fresh requests; this validation-only reuse adds no production cache.

Next milestone: D&A component-completeness/scope evidence design for the 33
DERIVATION periods, with AMD's five extension periods a separate gated pattern.
The 26 other combined-concept and 25 methodology-blocker controls are not
approved by this implementation; lease/business/impairment research remains
separate. Forecast/FCFF/DCF remains paused through Phase 1H.6.
