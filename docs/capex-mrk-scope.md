# MRK 2021–2022 exact-selected-filing Capex scope research

Phase 1H.4 Wave 41; starting HEAD
`14192dccbff75e300dacff0140546d2f613fa476`. Documentation only. The
[two-row supplement](capex-mrk-scope-inventory.json) matches the
[frozen inventory](capex-inventory.json), which remains unchanged.

**NO-GO for acceptance or derivation; zero safe additional coverage.** Both
periods retain `CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`. Cash basis and
specific exclusions are evidenced, but exhaustive PP&E purchase scope is not.
This is insufficient evidence, not demonstrated incompatibility. Prior issuer
decisions, methodology, production policies and results remain unchanged.

## Exact primary facts

CIK **310158**, selected nonamended 10-Ks. Both facts are
`us-gaap:PaymentsToAcquireProductiveAssets`, caption **Capital expenditures** in
investing activities **of continuing operations**. Each has one eligible
nondimensional, non-nil, exact-USD (`usd`) occurrence, decimals `-6`; no conflicting
eligible primary signature. Displayed outflows become positive XBRL magnitudes.

| Selected accession | Authoritative annual dates | Candidate USD | Original ordinal | Context | Namespace |
| --- | --- | ---: | ---: | --- | --- |
| 0000310158-22-000003 | 2021-01-01–2021-12-31 | 4,448,000,000 | 366 | i090a240c01204951a8d43aeb0084e26c_D20210101-20211231 | http://fasb.org/us-gaap/2021-01-31 |
| 0001628280-23-005061 | 2022-01-01–2022-12-31 | 4,388,000,000 | 421 | iaf8fc8dc60ac4ca6b59f2a42ad4a7b23_D20220101-20221231 | http://fasb.org/us-gaap/2022 |

DEI annual-period evidence, normalized entity/context/unit, source namespace,
raw/Decimal values, dimensions, nil status and original ordinals are retained.
Selected cash-flow presentation/calculation relationships are included, with
original schema, presentation, calculation, label and FilingSummary bytes.
Calculation relationships establish the investing sign/subtotal, not asset-scope
equivalence. Book balances, dimensioned and support occurrences are not approved
additional operands.

## Reviewed statement and note locations

Each link identifies a verified retained original response body in the
[evidence fixture](evidence/mrk-capex-response-bodies.json). All **26 bodies** were
reused; **zero new SEC requests**, no fingerprint refresh. Primary filings were
consulted only for cash-purchase scope and continuing-operation presentation.

| Evidence | 2021 selected filing | 2022 selected filing |
| --- | --- | --- |
| Cash-flow statement | [R9](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R9.htm) | [R9](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R9.htm) |
| Accounting policies | [R12](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R12.htm) | [R12](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R12.htm) |
| Organon spin-off | [R13](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R13.htm) | [R13](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R13.htm) |
| Acquisitions / research collaborations / licenses | [R14](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R14.htm) | [R14](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R14.htm) |
| Goodwill / intangibles | [R19](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R19.htm) | [R19](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R19.htm) |
| Debt / leases | [R20](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R20.htm) | [R20](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R20.htm) |
| Primary 10-K | [2021](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/mrk-20211231.htm) | [2022](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/mrk-20221231.htm) |

## Scope conclusions

Apply the [existing cash PP&E primitive](financial-methodology.md), not an
all-productive-assets or all-capitalized-cost definition. Capitalized operational
software can be eligible only within a proven purchase perimeter; Visa's reviewed
scope does not approve MRK or all software/service costs.

- **PP&E/software versus cloud:** policies explicitly put internal-use software
  material/service/payroll development costs in PP&E, while capitalized
  cloud-service implementation costs go into Other Assets. Preliminary,
  post-implementation, maintenance and training costs are expensed. These
  classifications affirmatively distinguish categories, but do not establish
  which cash expenditures are in the candidate or exhaust its asset perimeter.
  No software/cloud cash allocation can be obtained from balances or absence.
- **Acquisitions:** Acceleron, Pandion and other acquisition cash are separate
  investing lines, not parts to subtract from the Capex line. Pandion was an
  asset acquisition with R&D expense; expense recognition does not make its cash
  PP&E Capex. Purchase-price allocations to IPR&D/products/goodwill are not cash
  operands or evidence of an ordinary purchase split.
- **Licensing/acquired R&D:** policies expense pre-approval asset-acquisition and
  licensing upfront/milestone payments in R&D; qualifying post-approval rights
  payments may be intangible assets amortized to cost of sales. Business-combination
  IPR&D is capitalized and impairment-tested. Recognition and cash payment can
  differ; R&D expenses, operating reconciliation add-backs and intangible book
  additions do not establish exact cash classification or authorize a PP&E
  adjustment. Subsequent 2023 transactions discussed in the 2022 filing are not
  2022 operands.
- **Leases/noncash:** operating lease payments and noncash ROU additions are
  separately disclosed. ROU additions are not cash investing purchases. No
  inferred zero finance leases, noncash PP&E, unpaid-purchase timing or invented
  lease allocation is used. No complete cash exclusion equation is evidenced.
- **Proceeds/netting/overlap:** other investing cash is aggregated; securities
  purchases/sales and acquisitions are separate. Absence of a standalone disposal,
  incentive or intangible-purchase tag does not prove zero or gross PP&E scope.
  No residual calculation, book movement, proceeds netting or incentive gross-up.
- **Organon:** the spin-off completed June 2, 2021. The statement separates
  continuing cash from discontinued-operation cash. Neither total discontinued
  investing cash nor the $9 billion distribution to Merck is an ordinary PP&E
  purchase operand. Do not silently convert a continuing subtotal into a
  whole-company series by adding discontinued investing cash. Explicitly reported
  2022 zeros address those lines only, not every scope question.
- **Extensions:** any issuer-extension observations remain separately gated,
  support/exclusion evidence only. Neither extensions nor broad numbered US-GAAP
  acquisition concepts are Capex fallbacks or approved derivation components.

## Per-period support and decisions

USD millions; exact namespaces, context/unit/dimensions and original signs for
all listed facts are in the supplement. Support is not an approved equation.

| Period | Acquisition cash outside candidate | Operating lease cash / noncash ROU additions | Discontinued investing cash | Conclusion |
| --- | --- | --- | --- | --- |
| 2021 | Acceleron 11,174 (ordinal 378), Pandion 1,554 (381), other 179 (396) | 340 (1585) / 117 (1588) | −134 (435); not discontinued Capex | `SCOPE_RESEARCH_REQUIRED`: 4,448 candidate is continuing cash; no complete PP&E/internal-use-software versus cloud/rights perimeter or justified discontinued-operation bridge |
| 2022 | Other 121 (445); acquisition-specific zero facts retained, not inferred absence | 335 (1569) / 57 (1572) | Explicit 0 (484) | `SCOPE_RESEARCH_REQUIRED`: 4,388 candidate is cash; explicit zero discontinued/acquisition lines do not establish exhaustive PP&E/cloud/licensing scope |

For 2021 the concepts at ordinals 378/381 are US-GAAP
`PaymentsToAcquireBusinessTwoNetOfCashAcquired` and
`PaymentsToAcquireBusinessThreeNetOfCashAcquired`, not issuer extensions;
their cash-flow captions and selected acquisition note corroborate the identity.
The ordinary `PaymentsToAcquireBusinessesNetOfCashAcquired` facts at 396/445 are
separate US-GAAP observations. No equality between R&D expense and acquisition
cash is used to establish classification or completeness.

Only displayed cash millions × 1,000,000 equals the selected annual positive
XBRL magnitude exactly. No rounding tolerance, derivation equation, generic
fallback or extension approval. Two unresolved periods, zero safe new coverage.

## Provenance, validation and bounded next milestone

The 26 stored bodies verify as `sec_response_body_bytes` with
`sha256_sec_response_body_bytes`, lengths and exact URL/accession. Retained
original paths and reuse metadata are recorded; original retrieval times are not
invented. Existing instance and statement/note fingerprints match the retained
original bytes. The supplement records that independent verification without
rewriting historical frozen records. Matching extracted text is only a secondary
check, never a substitute for bytes. Discovery-index fingerprints are left
ancillary/unverified, not promoted to acceptance evidence.

Two unique frozen accession/annual identities, DEI dates, entity/unit/occurrences,
classification totals and transcription arithmetic reconcile. All 26 retained
typed digests/lengths and cited evidence/local links validate; `git diff --check`
passes. No tests, corpus, code, policy, schema or methodology changes. Production
carried forward, not remeasured: Capex **167/37/0**, aggregate
**1,905/1,483/11/27/42 = 3,468**. Prior issuer decisions are unchanged.

**Durable blocker:** reopen MRK only with exact-period evidence establishing the
complete eligible cash purchase perimeter, including cloud/rights classification
and any necessary non-overlapping cash operands; separately justify any change
from the explicitly presented continuing scope. Broad repeat research or matching
book/residual totals cannot supply those missing assertions.

**Next bounded milestone:** documentation-only component/perimeter research for
the five frozen VZ other-productive-asset cash periods, distinguishing network
PP&E from licenses/intangibles and other excluded purchases. Do not implement
coverage or reopen prior issuers without new completeness evidence.
