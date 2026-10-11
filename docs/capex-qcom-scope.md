# QCOM exact-selected-filing Capex scope research

Phase 1H.4 Wave 39; starting HEAD
`95f688f3b28bb6aeb8da1afd81c306e4b9cc7a35`. Documentation only. The
[five-period supplement](capex-qcom-scope-inventory.json) matches the frozen
[57-period inventory](capex-inventory.json); the latter is not rewritten.

**NO-GO for acceptance or derivation; zero safe additional coverage.** All five
retain `CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`. Cash basis and separate
acquisition presentation are established, but complete equivalence of the
productive-asset cash line to the existing PP&E cost primitive is not. This is
insufficient evidence, not demonstrated incompatibility or a methodology denial.

## Exact annual candidates

CIK **804328**, nonamended selected 10-Ks. All primary facts are
`us-gaap:PaymentsToAcquireProductiveAssets`, nondimensional, non-nil, exact USD
(`usd`), decimals `-6`; each has one eligible occurrence and no conflicting
eligible primary signature. The cash-flow caption is **Capital expenditures**,
displayed as an outflow; XBRL records a positive expenditure magnitude.

| Selected accession | Authoritative annual period | Candidate USD | Original ordinal | Context | Taxonomy namespace |
| --- | --- | ---: | ---: | --- | --- |
| 0001728949-21-000076 | 2020-09-28–2021-09-26 | 1,888,000,000 | 240 | i08b81277a0674d1882e49c47fe7aeca7_D20200928-20210926 | http://fasb.org/us-gaap/2021-01-31 |
| 0000804328-22-000021 | 2021-09-27–2022-09-25 | 2,262,000,000 | 276 | i8e873583180c476e887d11e6467cc566_D20210927-20220925 | http://fasb.org/us-gaap/2022 |
| 0000804328-23-000055 | 2022-09-26–2023-09-24 | 1,450,000,000 | 277 | c-1 | http://fasb.org/us-gaap/2023 |
| 0000804328-24-000075 | 2023-09-25–2024-09-29 | 1,041,000,000 | 282 | c-1 | http://fasb.org/us-gaap/2024 |
| 0000804328-25-000085 | 2024-09-30–2025-09-28 | 1,192,000,000 | 287 | c-1 | http://fasb.org/us-gaap/2025 |

DEI annual-period resolution, normalized entity/context identity, fact namespace,
unit measures, raw/Decimal values, original ordinal, dimensions and nil status
are preserved in the supplement. All five instances retain their frozen SHA-256.
Selected schema/presentation/calculation/label and FilingSummary bodies are
retained. The consolidated cash-flow role places the candidate in investing
activities with calculation weight `-1.0`; this proves its cash-flow relationship,
not that it exhausts the eligible PP&E purchase perimeter.

## Statement and note evidence

Every URL below was retrieved as the exact selected-accession artifact; original
response bodies, retrieval metadata, typed SHA-256 and byte lengths are retained
in [the evidence fixture](evidence/qcom-capex-response-bodies.json). Primary
filings were consulted only for the missing cash-asset-perimeter linkage.

| Period | Cash-flow statement | Accounting / composition notes | Lease / acquisition notes | Primary filing |
| --- | --- | --- | --- | --- |
| 2021 | [R5](https://www.sec.gov/Archives/edgar/data/804328/000172894921000076/R5.htm) | [R7 policies](https://www.sec.gov/Archives/edgar/data/804328/000172894921000076/R7.htm), [R8 composition](https://www.sec.gov/Archives/edgar/data/804328/000172894921000076/R8.htm) | [R13 commitments](https://www.sec.gov/Archives/edgar/data/804328/000172894921000076/R13.htm), [R15 acquisitions](https://www.sec.gov/Archives/edgar/data/804328/000172894921000076/R15.htm) | [10-K](https://www.sec.gov/Archives/edgar/data/804328/000172894921000076/qcom-20210926.htm) |
| 2022 | [R6](https://www.sec.gov/Archives/edgar/data/804328/000080432822000021/R6.htm) | [R8 policies](https://www.sec.gov/Archives/edgar/data/804328/000080432822000021/R8.htm), [R9 composition](https://www.sec.gov/Archives/edgar/data/804328/000080432822000021/R9.htm) | [R14 commitments](https://www.sec.gov/Archives/edgar/data/804328/000080432822000021/R14.htm), [R16 acquisitions](https://www.sec.gov/Archives/edgar/data/804328/000080432822000021/R16.htm) | [10-K](https://www.sec.gov/Archives/edgar/data/804328/000080432822000021/qcom-20220925.htm) |
| 2023 | [R6](https://www.sec.gov/Archives/edgar/data/804328/000080432823000055/R6.htm) | [R8 policies](https://www.sec.gov/Archives/edgar/data/804328/000080432823000055/R8.htm), [R9 composition](https://www.sec.gov/Archives/edgar/data/804328/000080432823000055/R9.htm) | [R14 commitments](https://www.sec.gov/Archives/edgar/data/804328/000080432823000055/R14.htm), [R16 acquisitions/divestitures](https://www.sec.gov/Archives/edgar/data/804328/000080432823000055/R16.htm) | [10-K](https://www.sec.gov/Archives/edgar/data/804328/000080432823000055/qcom-20230924.htm) |
| 2024 | [R6](https://www.sec.gov/Archives/edgar/data/804328/000080432824000075/R6.htm) | [R8 policies](https://www.sec.gov/Archives/edgar/data/804328/000080432824000075/R8.htm), [R9 composition](https://www.sec.gov/Archives/edgar/data/804328/000080432824000075/R9.htm) | [R14 commitments](https://www.sec.gov/Archives/edgar/data/804328/000080432824000075/R14.htm); separate cash acquisition line remains evidence, no standalone acquisition note in this filing's general-note list | [10-K](https://www.sec.gov/Archives/edgar/data/804328/000080432824000075/qcom-20240929.htm) |
| 2025 | [R6](https://www.sec.gov/Archives/edgar/data/804328/000080432825000085/R6.htm) | [R8 policies](https://www.sec.gov/Archives/edgar/data/804328/000080432825000085/R8.htm), [R9 composition](https://www.sec.gov/Archives/edgar/data/804328/000080432825000085/R9.htm) | [R14 commitments](https://www.sec.gov/Archives/edgar/data/804328/000080432825000085/R14.htm), [R16 acquisitions](https://www.sec.gov/Archives/edgar/data/804328/000080432825000085/R16.htm) | [10-K](https://www.sec.gov/Archives/edgar/data/804328/000080432825000085/qcom-20250928.htm) |

## Scope conclusions and exclusions

The [existing primitive](financial-methodology.md) accepts cash PP&E costs,
including evidenced capitalized operational software within a proven purchase
perimeter. Visa's reviewed software acceptance does not transfer approval to
QCOM. Product software development or intellectual-property investments are not
automatically operational PP&E purchases.

- **PP&E and software:** each composition note lists land, buildings, computer
  equipment and software, machinery, furniture, leasehold improvements and
  construction in progress. Policies record PP&E at cost and expense maintenance,
  repairs and minor renewals. These establish asset recognition, not current cash
  allocations. No complete payment-to-asset-class bridge or definition limiting
  the entire cash candidate to these eligible classes is disclosed in the
  reviewed material. Neither software balances nor their movements are operands.
- **Other intangibles and acquisitions:** goodwill/intangible policies and
  acquisition notes distinguish purchase-price allocations and acquired
  technologies from ordinary purchases. The cash-flow acquisition/investment
  line is separate. Its extension `qcom:AcquisitionsAndOtherInvestmentsNetofCashAcquired`
  remains separately gated, support/exclusion evidence only, never a Capex
  fallback. Acquisition fair values are not subtracted from the candidate or
  used to infer independent intangible cash payments.
- **Leases:** policies put operating ROU assets/liabilities in other asset/
  liability categories, with lease expense and commitments separately disclosed.
  These are neither PP&E purchase cash nor a complete annual cash/noncash lease
  bridge. No assumed zero finance leases or invented lease adjustment is used.
- **Noncash and timing:** book additions, acquisition-origin PP&E, unpaid purchase
  timing, supplier commitments, advance payments and operating noncash adjustments
  cannot be converted into Capex by subtraction. The line itself is cash, but
  exhaustive classification of eligible cash expenditures remains unproved.
  Absence of a separately tagged noncash or intangible purchase is not zero.
- **Proceeds and netting:** PP&E disposal proceeds are separately displayed in
  2023–2025, so these are not netted against purchase cash. Earlier filings' other
  investing items do not establish zero PP&E proceeds. No assumed incentive
  allocation, gross-up or netting adjustment is made.
- **Business scope:** MD&A explicitly describes cash capital outflows and
  manufacturing/production/testing needs; this supports cash purpose, not an
  exhaustive definition. Veoneer/Non-Arriver discontinued-operation cash flows
  and acquisitions are separately presented in later filings. No predecessor,
  disposal or discontinued-investing total is silently added to the candidate.

## Five-period conclusions

Amounts below are USD millions; excluded/supporting items are not equation
operands. Exact XBRL occurrences, contexts, namespaces and original signs are in
the supplement, including dimensioned acquisition and book-balance facts.

| Period | Candidate | Separate acquisition/investment cash (extension ordinal) | Separate PP&E proceeds | Decision / remaining blocker |
| --- | ---: | --- | --- | --- |
| 2021 | 1,888 | 1,377 (249) | Not separately displayed; not zero | `SCOPE_RESEARCH_REQUIRED`: cash and NUVIA separation evidenced; full purchase perimeter not exhausted |
| 2022 | 2,262 | 4,912 (285) | Not separately displayed; not zero | `SCOPE_RESEARCH_REQUIRED`: Veoneer and supplier advance payments are not candidate operands; no complete eligible cash bridge |
| 2023 | 1,450 | 235 (286) | 127 (ordinal 289) | `SCOPE_RESEARCH_REQUIRED`: separately reported disposal/discontinued cash cannot prove intangible or PP&E cash completeness |
| 2024 | 1,041 | 254 (291) | 10 (ordinal 294) | `SCOPE_RESEARCH_REQUIRED`: PP&E/software classes and production purpose evidenced, exhaustive reported purchase scope unproved |
| 2025 | 1,192 | 743 (296) | 14 (ordinal 299) | `SCOPE_RESEARCH_REQUIRED`: testing purpose and acquisition separation evidenced; no complete cash class mapping |

The only arithmetic validated is displayed millions × 1,000,000 equals the
selected annual positive XBRL value, exactly, with no rounding tolerance. This
checks transcription/sign/period identity; it is not scope proof. No derived
equation, residual, book-balance cash flow, generic fallback or extension approval.

## Provenance, validation and durable blocker

The committed inventory and historical extracted statements/notes were reused.
Original QCOM bodies were unavailable in the retained directories inspected;
59 specific selected-filing artifacts were retrieved and retained, rather than
certifying historical fingerprints. New records use `sec_response_body_bytes`
and `sha256_sec_response_body_bytes`, with byte length, HTTP status, retrieval
time, exact URL/accession and gzip/base64 lossless storage.

All five current instance digests match the frozen inventory. Ten current
cash-flow/accounting-note byte digests differ from historical claims, while
their independently extracted whitespace-normalized report text matches the
retained research text. Historical response bodies were not recovered, so no
byte-equivalence, purely representational-change or original-digest-verification
claim is made. Fresh bodies were independently reviewed for the scope findings
above. Old fingerprints remain unchanged, explicitly unverified historical
representations linked to current bodies; parsed equality does not approve scope
or replace byte verification. Discovery `index.json` is not refreshed or an
acceptance artifact in this research.

Five unique frozen identities and DEI annual periods reconcile; all units,
entities and primary occurrences match; classification totals are five
`CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED`. All 59 stored bodies decode to their
stated typed digests/lengths, and all introduced evidence URLs identify retained
selected-filing bodies. Relevant local links and `git diff --check` pass.
No production code, policy, schema, test or corpus rerun. Production carried
forward: Capex **167/37/0**, aggregate **1,905/1,483/11/27/42 = 3,468**.

**Durable blocker:** reopen QCOM only if exact-period evidence explicitly
establishes the complete eligible cash purchase scope, or provides all required
non-overlapping cash exclusion components. Broad repeat research, software
balance changes, residuals or numerical agreement cannot close this gap.
There is no proposed primitive expansion or policy impact.

**Next bounded milestone:** documentation-only cash PP&E scope research for
the five frozen HD Capex periods. Preserve QCOM's unapproved outcomes and all
existing approvals; no production changes are authorized by this research.
