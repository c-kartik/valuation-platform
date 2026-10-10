# S&P 500 Top 50 failure taxonomy

## Scope and evidence

This artifact records the Phase 1H.3 analysis of the production smoke test at
commit `3bca2f61ac4db335a334b88c502274aea2509cee`. The frozen input remains
`sp500-top-50-2026-10-02.csv`: 51 securities, 50 SEC issuers, 43 generic
pipeline attempts, and seven specialized-methodology skips. A fresh read-only
diagnostic on 2026-10-06 reproduced 41 standardized-output executions, two
Company Facts failures, 40 five-period histories, and XOM's empty history.

The analysis does not change a parser, selector, concept policy, financial
methodology, or issuer result. A missing value is not zero. A possible concept
match is evidence for research, not approval to normalize it.

**Wave 1A follow-up:** commit `453751155fad5e82cdab0a507d311fe724b851a8`
is the Phase 1H.3 baseline described by the tables below. Wave 1A subsequently
implemented the exact padded-CIK schema fix without changing financial policy.
A live rerun completed GEV and SNDK through standardized output with two annual
periods each. The full corpus then completed all 43 generic attempts with zero
failures and produced 1,663 resolved, 1,709 missing, 27 ambiguous, 27
methodology-blocked, and 42 not-comparable states across 204 issuer-periods.
The original Phase 1H.3 matrix remains below as the evidence baseline for the
ranked backlog.

**Wave 2 follow-up:** the exact standard
`CashAndCashEquivalentsAtCarryingValue` policy now applies without a seed-CIK
restriction. The post-Wave-1A live baseline contained 25 resolved and 179
missing cash periods; Wave 2 produced 185 resolved, 19 missing, and no ambiguous
cash periods. The 160 new resolutions moved aggregate corpus totals to 1,823
resolved and 1,549 missing, while 27 ambiguous, 27 methodology-blocked, 42
not-comparable, and all 3,468 total states remained unchanged.

**Wave 3 follow-up:** research rejected a unique current diluted-share duration
as fiscal-year authority because a selected 10-K can also disclose Q4 or other
shorter durations. No source evaluated in that wave independently proved the
fiscal-year start, so no automatic period filter was retained. All 11
full-year/Q4 revenue collisions for JNJ, ABBV, GE, and ORCL remain typed
ambiguity. The other 11 revenue states remain genuine full-year
concept-definition conflicts for WMT, MA, and CVX. Aggregate corpus totals stay
at the Wave 2 baseline: 1,823 resolved, 1,549 missing, 27 ambiguous, 27
methodology-blocked, and 42 not-comparable across 204 periods and 3,468 states.

**Wave 4 follow-up:** the filing-XBRL DEI required context is authoritative
annual-period evidence for the tested exact 10-Ks. SEC staff guidance supporting
EDGAR validation describes that dimensionless duration as matching the year of
the submission reporting period; the EDGAR Filer Manual and applicable filing
requirements remain controlling.
The rule was verified across 42 selected filings for nine issuers, including
non-calendar and 52/53-week years, and is documented in
`../annual-period-evidence.md`. Wave 5 implements the pure SEC-layer resolver
and validates all 42 evidence-table filings, but does not integrate it with
normalization. All current ambiguities and aggregate corpus totals therefore
remain unchanged pending a separate integration and validation sub-wave.

**Wave 6 follow-up:** corpus orchestration now supplies typed annual-period
results explicitly to normalization. Exact resolved periods filter Revenue,
Pretax Income, and Income Tax Expense only. The 11 JNJ/ABBV/GE/ORCL annual/Q4
Revenue collisions resolved, as did JNJ Pretax/ETR and SNDK Pretax/Tax/ETR.
Revenue is 193 resolved and 11 ambiguous across 204 periods. Aggregate totals
are 1,839 resolved, 1,549 missing, 11 ambiguous, 27 methodology-blocked, and 42
not-comparable across 3,468 states. The 11 remaining Revenue ambiguities are
same-authoritative-period economic concept conflicts for WMT, MA, and CVX.

**Wave 7 follow-up:** `../pretax-income-concepts.md` inventories every one of
the 45 remaining typed-missing Pretax periods. A recurring standard
equity-method-scope variant appears in 33 periods across seven issuers, but is
not an unconditional semantic equivalent to the current concept. The research
reaches PARTIAL GO for further research/design only. The variant remains
`NEEDS_MORE_RESEARCH`: tax-denominator or primary-statement status does not
prove the current equity-method-inclusive scope, and current tooling cannot
machine-check presentation evidence. Twelve ORCL, MCD, and PG periods rely on
issuer extensions;
domestic/foreign components and namespace-agnostic extension matching remain
unapproved. The 33 periods are structural candidate coverage, safe new
resolutions remain zero, and production results and Wave 6 totals are unchanged.
Independent review confirmed the classification and the evidence boundary.
Wave 8 documents a PARTIAL GO for a read-only presentation-evidence diagnostic:
submitted `Statement` roles and exact instance facts may classify placement,
but cannot independently establish the required equity-method scope. SEC render
artifacts remain corroboration only, and production policy remains unchanged.

**Wave 9 follow-up:** the read-only diagnostic attempted all 33 frozen
standard-concept periods and emitted one typed result per period. Exact filing,
annual-period, fact, submitted-role, and renderer reconciliation completed with
zero data errors. Every candidate occurs in exactly one submitted `Statement`
role and in one to three `Disclosure` roles, producing 33
`MULTIPLE_ROLE_MEMBERSHIP` results. MetaLinks and applicable R-files corroborate
all 33. The separate semantic decision remains `NEEDS_MORE_RESEARCH`: the
issuer matrix has direct `SEPARATE_NET_OF_TAX` evidence for AMZN and
`INCLUDED_PRETAX` evidence for CVX, while MU, MA, CAT, PM, and LIN remain
`UNRESOLVED`. No result is approved for normalization, safe new Pretax
resolutions remain zero, and aggregate corpus totals remain unchanged.

**Wave 10 follow-up:** `../pretax-equity-method-note-evidence.md` inspects every
exact selected accession and annual period. Direct filing evidence classifies
eight periods as `INCLUDED_PRETAX` (MA three and CVX five), 20 as
`SEPARATE_NET_OF_TAX` (AMZN, MU, CAT, and PM five each), and five LIN periods as
`UNRESOLVED` because corporate-investee income is after tax while
partnership/LLC-investee income enters Pretax. No period is
`SEPARATE_PRETAX` or `NO_MATERIAL_ACTIVITY_FOUND`. No deterministic,
machine-checkable economic-equivalence rule was established; safe new
production resolutions remain zero, and the 12 issuer-extension periods and
all corpus totals remain unchanged.

**Wave 11 follow-up:** `../pretax-scope-evidence-design.md` independently tests
the eight positives against all 25 controls. No automated structured rule
survives: the same concept and multiple-role presentation pattern spans
included, separate-net-of-tax, and mixed economics. The design reaches PARTIAL
GO for a curated immutable `pretax_scope_equivalence_v1` policy covering only
the eight exact MA/CVX facts, with reviewed filing evidence, full-key matching,
current-concept precedence, and missing-by-default future/amended filings. No
registry is implemented; safe new production resolutions and corpus totals
remain unchanged.

**Wave 12 follow-up:** the immutable `pretax_scope_equivalence_v1` policy now
registers exactly the eight reviewed MA/CVX facts without changing the generic
Pretax policy. Equivalent repeated nondimensional filing-XBRL occurrences
confirm one value while retaining every original representation and ordinal;
CVX's dimensioned occurrences remain excluded. Exactly eight Pretax and eight
corresponding Reported ETR periods resolve. Pretax and Reported ETR each become
167 resolved / 37 missing / 0 ambiguous. All 25 controls and all 12 excluded
ORCL/MCD/PG extension periods remain missing. Aggregate states are 1,855
resolved, 1,533 missing, 11 ambiguous, 27 methodology-blocked, and 42
not-comparable across the unchanged 3,468 total states.

**Wave 13 follow-up:** the
[Operating Income concept inventory](../operating-income-concepts.md) reconciles all 35
missing Operating Income periods—five each for LLY, JNJ, CVX, MRK, GE, KLAC,
and IBM—to exact selected accessions, authoritative annual periods, submitted
income-statement roles, and SEC face statements. None reports a consolidated
Operating Income subtotal; none has an exact Company Facts observation or an
exact annual nondimensional filing-XBRL candidate. GE 2024 and 2025 have only
dimensioned segment and reconciliation `OperatingIncomeLoss` facts. Direct
policy expansion is NO-GO, safe coverage is zero, all 35 remain missing, and
production totals are unchanged. Twenty-five LLY/JNJ/MRK/KLAC/IBM periods move
to derivation-evidence design; CVX and GE require separate perimeter research.

**Wave 14 follow-up:** the
[Operating Income component-derivation evidence design](../operating-income-derivation-design.md)
reconciles all 25 LLY/JNJ/MRK/KLAC/IBM periods. Exact face-statement operands,
submitted calculation relationships, signs, and independent Pretax bridges
support `DERIVATION_APPROVED` for every reviewed period. Twenty-two bridges
are exact; three IBM bridges are within the explicitly bounded one-unit
($1 million) whole-statement rounding tolerance. Safe potential coverage is 25
exact accessions, but no generic concept rule or future filing is approved.
CVX and GE remain outside this design, and production counts remain unchanged.

**Wave 15 follow-up:** the
[curated Operating Income derivation-policy design](../operating-income-derivation-policy-design.md)
reaches **PARTIAL GO** for a later exact-accession implementation. The proposed
immutable `operating_income_component_derivation_v1` registry contains only the
25 approved equations, preserves ordered operand and occurrence evidence,
keeps the direct policy first, treats IBM's $1 million boundary as validation-
only, and defaults future, amended, unregistered, incomplete, or conflicting
evidence to no result. The ten CVX/GE periods remain negative controls. This
design wave changes no production counts.

**Wave 16 follow-up:** the curated Operating Income derivation policy is now
implemented for exactly the 25 approved accessions. All 25 resolve and all ten
CVX/GE controls remain missing. Operating Income is 194 resolved / 10 missing /
0 ambiguous (169 direct, 25 derived); aggregate states are 1,880 resolved /
1,508 missing / 11 ambiguous / 27 methodology-blocked / 42 not-comparable.
The denominator remains 204 periods / 3,468 states, with 43/43 generic issuers
complete and seven specialized skips. All direct OI results, 25 seed annual
financial results, non-OI metric states and execution stages remain unchanged.
The 163 focused and 513 complete tests, exact 25-positive/10-control live run,
full corpus, compile checks and `git diff --check` pass. Full ordered policy,
occurrence and validation provenance survives schema 3 serialization and
Operating Tax supporting inputs; no tax policy is automatically ready. See
[verified results](../operating-income-derivation-policy-design.md#wave-16-implementation-and-verified-results).

**Wave 17 follow-up:** the
[CVX/GE business-perimeter research](../operating-income-cvx-ge-perimeter.md)
matches all ten frozen selected filings and reaches NO-GO for additional
Operating Income coverage. CVX's five periods remain
`BUSINESS_PERIMETER_UNRESOLVED`; GE's five require specialized consolidated
industrial/insurance treatment, and its common five-period continuing series
is not comparable after portfolio separations and accounting changes. These
are research findings, not new production states or universe execution
classifications. All ten remain missing; Operating Income stays 194 / 10 / 0
and aggregate states stay 1,880 / 1,508 / 11 / 27 / 42 across 3,468 states.
The next reusable research target is the 94 missing D&A periods. Dedicated
CVX affiliate and GE industrial carve-out/recast designs remain unapproved.

**Wave 18 follow-up:** the
[D&A inventory](../depreciation-amortization-concepts.md) and
[machine-checkable evidence](../depreciation-amortization-inventory.json)
reconcile exactly 94 frozen missing annual periods across 21 issuers. Primary
research routing is 31 `CONCEPT_POLICY`, 33 `DERIVATION`, five
`ISSUER_EXTENSION` and 25 `METHODOLOGY_BLOCKER`. Five Visa periods support
bounded scope-equivalence design; the other 89 remain unapproved. PARTIAL GO
is not a generic fallback, new component policy or production result. All
1,374 inspected annual numeric occurrences retain their dimensional, unit,
representation and selected-source distinctions. D&A remains 110 / 94 / 0;
Operating Income remains 194 / 10 / 0 and aggregate remains 1,880 / 1,508 / 11 /
27 / 42 across 3,468 states. No test suite or corpus rerun was performed.

**Wave 20 implementation:** the five-entry curated D&A policy resolves exactly
five Visa periods; all 89 controls retain their baseline missing states and
research routing. Current D&A is **115 resolved / 89 missing / 0 ambiguous**.
Aggregate is **1,885 resolved / 1,503 missing / 11 ambiguous /
27 methodology-blocked / 42 not-comparable** across **3,468** states. All other
measure states, 43 generic completions, seven specialized skips and 204 annual
periods are unchanged. Focused tests pass 200 checks; the full suite passes
552 tests; targeted five-accession and one corpus reconciliation match exactly.
Reviewed artifacts, confirming multiplicity and separate support/exclusion
audit survive schema 4. See the
[verified results](../depreciation-amortization-scope-evidence-design.md#wave-20-implementation-and-verified-results).
Next design component-completeness/scope evidence for the 33 DERIVATION periods;
AMD's five extension periods and lease/business controls remain separate.

## Operational taxonomy

| Category | Meaning | Observed evidence |
|---|---|---|
| `RETRIEVAL` | SEC transport or artifact retrieval failed | No corpus-wide instance in this run |
| `TICKER_CIK_IDENTITY` | The ticker identity does not lead to the registrant history needed by the pipeline | XOM |
| `FILING_SELECTION` | Correct-identity filings exist but the selector cannot identify the requested periods | No independent selector defect established; XOM's empty selection is downstream of identity |
| `COMPANY_FACTS_SCHEMA` | A legitimate SEC JSON representation violates a parser schema assumption | GEV and SNDK zero-padded string CIKs |
| `CONCEPT_POLICY` | Evidence uses an unapproved concept, an overly narrow CIK scope, or competing approved concepts | Cash, investments, debt, pretax income, Capex, and revenue conflicts |
| `ISSUER_EXTENSION` | Required evidence exists only in an issuer taxonomy or filing-level artifact | A research path for several missing statement facts; no repeatable extension family is approved yet |
| `DIMENSIONAL_CONTEXT` | Facts require explicit member/context handling | No new standalone blocker proved by the Company Facts artifact; filing-XBRL research remains necessary |
| `DERIVATION` | Direct evidence is absent and a complete, nonoverlapping derivation must be established | D&A components and downstream reported ETR |
| `PERIOD_ASSOCIATION` | One accession contains multiple durations ending on the report date | **Implemented for the known annual/Q4 class:** Wave 6 integrates the filing-XBRL DEI period for Revenue, Pretax Income, and Income Tax Expense; nonresolved evidence retains ambiguity-safe behavior |
| `METHODOLOGY_BLOCKER` | Extraction works, but accounting treatment or valuation perimeter is unresolved | GOOGL, MSFT, and AAPL O-NWC |
| `EXPECTED_TYPED_MISSING` | Filing evidence establishes economic absence or non-applicability under the approved methodology | Some debt or investment balances after filing confirmation; no corpus result is assigned this category merely because a fact is absent |
| `OTHER` | A root cause does not fit the operational categories | None currently identified |

`GENERALIZATION_REQUIRED` is an issuer-level planning conclusion, not a root
cause.

## Issuer-blocking diagnoses

### GEV and SNDK: Company Facts schema

Ticker resolution and filing selection are correct. GEV resolves to CIK
1996810 and selects 2024 and 2025; SNDK resolves to CIK 2023554 and selects
2025 and 2026. Their raw Company Facts identities are respectively
`"0001996810"` and `"0002023554"`. SEC returns both as ten-digit,
zero-padded strings.

At the Phase 1H.3 baseline, the parser accepted a nonnegative integer or a
canonical unpadded decimal string, then required equality with the requested
CIK. It rejected a leading-zero string before equality was tested. The two
failures were therefore one `COMPANY_FACTS_SCHEMA` issue, not issuer-specific
problems.

Wave 1A implemented the narrow shared fix: the parser additionally accepts an
exact ten-digit ASCII-decimal representation only when it equals
`company.cik_padded`, normalizes it to the requested integer CIK, and retains
the identity-equality check. Whitespace, signs, non-digits, arbitrary
leading-zero forms, and mismatched CIKs remain invalid. Live GEV and SNDK runs
both completed Company Facts, filing association, normalization, and
standardized output without an issuer-specific branch.

### XOM: ticker/CIK succession

The current official ticker dataset resolves XOM to CIK 2115436,
`ExxonMobil Holdings Corp`. That CIK's submissions response has 34 recent
rows, no exact 10-K, one 10-Q, and no supplemental history files. The 10-Q is
cross-listed as accession `0000034088-26-000093`, whose accession owner is
legacy CIK 34088. The filing contains both CIK identities and explicitly states
that ExxonMobil Holdings became the publicly traded parent and successor
registrant. These are observed SEC facts; the production resolver does not yet
interpret them.

CIK 34088 is `EXXON MOBIL CORP`; its submissions history contains the required
2021–2025 10-Ks and its Company Facts entity is `Exxon Mobil Corporation`. The
old CIK currently has no ticker in its submissions identity. The selector
therefore correctly returns zero annual filings for current CIK 2115436. This
is a `TICKER_CIK_IDENTITY` registrant-succession problem, not a reason to relax
filing selection or hardcode XOM to CIK 34088.

Phase 1H.4 Wave 1B completed the detailed design in
`docs/sec-identity-linkage.md`. The official 2026-07-01 Form 8-K12B explicitly
identifies Exxon Mobil Corporation as predecessor, ExxonMobil Holdings as
successor under Rule 12g-3(a), and 2026-07-01 as the effective date. The joint
2026 10-Q corroborates both registrants, the one-for-one reorganization, and
continuity of the consolidated business and reporting basis. Together they
support the human-reviewed edge `34088 -> 2115436`.

The implementation decision is nevertheless **NO-GO**. The structured
submissions, archive, cover-page, and DEI evidence discover and bind candidate
registrants but do not encode the directed legal edge. That direction remains
in variable narrative filing text, for which no generic ambiguity-safe parser
has been established. Cross-listing alone remains insufficient because it also
occurs for joint filers, parent/subsidiary registrants, and co-obligors. The
design therefore rejects ticker/name matching, multiple or conflicting
candidates, unclear direction, inconsistent chronology, and incomplete
evidence; it supports bounded, cycle-detected chains conceptually but does not
authorize production traversal. XOM remains unresolved without an
`XOM -> 34088` hardcode.

## Standardized measure coverage

The denominator is 200 issuer-periods: 40 completed issuers with five annual
periods. XOM, GEV, SNDK, and specialized issuers do not contribute measures.

| Measure | Possible | Resolved | Missing | Ambiguous | Methodology blocked | Not comparable | Direct | Derived | Calculated | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Revenue | 200 | 178 | 0 | 22 | 0 | 0 | 178 | 0 | 0 | 89.0% |
| Operating income | 200 | 165 | 35 | 0 | 0 | 0 | 165 | 0 | 0 | 82.5% |
| Pretax income | 200 | 154 | 45 | 1 | 0 | 0 | 154 | 0 | 0 | 77.0% |
| Income-tax expense | 200 | 200 | 0 | 0 | 0 | 0 | 200 | 0 | 0 | 100.0% |
| Reported effective tax rate | 200 | 154 | 45 | 1 | 0 | 0 | 0 | 154 | 0 | 77.0% |
| D&A | 200 | 110 | 90 | 0 | 0 | 0 | 105 | 5 | 0 | 55.0% |
| Capex | 200 | 145 | 55 | 0 | 0 | 0 | 145 | 0 | 0 | 72.5% |
| Diluted weighted-average shares | 200 | 192 | 8 | 0 | 0 | 0 | 189 | 3 | 0 | 96.0% |
| Cash and cash equivalents | 200 | 25 | 175 | 0 | 0 | 0 | 25 | 0 | 0 | 12.5% |
| Short-term investments | 200 | 25 | 175 | 0 | 0 | 0 | 25 | 0 | 0 | 12.5% |
| Long-term marketable securities | 200 | 5 | 195 | 0 | 0 | 0 | 5 | 0 | 0 | 2.5% |
| Commercial paper | 200 | 12 | 188 | 0 | 0 | 0 | 12 | 0 | 0 | 6.0% |
| Short-term borrowings | 200 | 1 | 199 | 0 | 0 | 0 | 1 | 0 | 0 | 0.5% |
| Current portion of long-term debt | 200 | 114 | 86 | 0 | 0 | 0 | 113 | 1 | 0 | 57.0% |
| Long-term debt, noncurrent | 200 | 138 | 62 | 0 | 0 | 0 | 135 | 3 | 0 | 69.0% |
| Operating NWC | 200 | 10 | 175 | 0 | 15 | 0 | 0 | 0 | 10 | 5.0% |
| Change in Operating NWC | 200 | 8 | 140 | 0 | 12 | 40 | 0 | 0 | 8 | 4.0% |

The table reconciles to 3,400 standardized measures: 1,636 resolved, 1,673
missing, 24 ambiguous, 27 methodology-blocked, and 40 not-comparable.

## Issuer status frequencies

Counts below cover the 17 standardized measures for each selected annual
period. Stage failures and XOM's empty history have no measure denominator.

| Issuer | Periods | Resolved | Missing | Ambiguous | Methodology blocked | Not comparable | Pipeline result |
|---|---:|---:|---:|---:|---:|---:|---|
| NVDA | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| AAPL | 5 | 70 | 5 | 0 | 9 | 1 | complete |
| MSFT | 5 | 62 | 13 | 0 | 9 | 1 | complete |
| AMZN | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| GOOGL | 5 | 60 | 15 | 0 | 9 | 1 | complete |
| AVGO | 5 | 41 | 43 | 0 | 0 | 1 | complete |
| META | 5 | 63 | 21 | 0 | 0 | 1 | complete |
| MU | 5 | 30 | 54 | 0 | 0 | 1 | complete |
| TSLA | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| AMD | 5 | 42 | 42 | 0 | 0 | 1 | complete |
| LLY | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| XOM | 0 | 0 | 0 | 0 | 0 | 0 | empty history |
| JNJ | 5 | 42 | 39 | 3 | 0 | 1 | complete |
| V | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| INTC | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| WMT | 5 | 40 | 39 | 5 | 0 | 1 | complete |
| ABBV | 5 | 30 | 49 | 5 | 0 | 1 | complete |
| MA | 5 | 38 | 45 | 1 | 0 | 1 | complete |
| CSCO | 5 | 50 | 34 | 0 | 0 | 1 | complete |
| LRCX | 5 | 38 | 46 | 0 | 0 | 1 | complete |
| PLTR | 5 | 41 | 43 | 0 | 0 | 1 | complete |
| AMAT | 5 | 44 | 40 | 0 | 0 | 1 | complete |
| CVX | 5 | 20 | 59 | 5 | 0 | 1 | complete |
| COST | 5 | 70 | 14 | 0 | 0 | 1 | complete |
| CAT | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| MRK | 5 | 38 | 46 | 0 | 0 | 1 | complete |
| PG | 5 | 46 | 38 | 0 | 0 | 1 | complete |
| KO | 5 | 46 | 38 | 0 | 0 | 1 | complete |
| GE | 5 | 23 | 57 | 4 | 0 | 1 | complete |
| PM | 5 | 28 | 56 | 0 | 0 | 1 | complete |
| HD | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| NFLX | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| KLAC | 5 | 37 | 47 | 0 | 0 | 1 | complete |
| TXN | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| GEV | 0 | 0 | 0 | 0 | 0 | 0 | Company Facts failure |
| SNDK | 0 | 0 | 0 | 0 | 0 | 0 | Company Facts failure |
| ORCL | 5 | 24 | 59 | 1 | 0 | 1 | complete |
| LIN | 5 | 34 | 50 | 0 | 0 | 1 | complete |
| IBM | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| QCOM | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| VZ | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| PEP | 5 | 40 | 44 | 0 | 0 | 1 | complete |
| MCD | 5 | 34 | 50 | 0 | 0 | 1 | complete |

## High-frequency evidence patterns

### Cash and investments

At the Phase 1H.3 baseline, the cash policy was intentionally scoped to the five
seed CIKs. The exact standard `CashAndCashEquivalentsAtCarryingValue` fact was
structurally eligible in 183 periods across 38 issuers, leaving 158 eligible
policy-scope misses after the 25 seed resolutions. Wave 2 removed only that CIK
restriction. The current 204-period corpus resolves 185 periods across 39
issuers: 25 seed periods plus 160 newly resolved periods across 34 issuers.
SNDK contributes the two resolutions beyond the original 158 estimate because
Wave 1A made its two-period Company Facts history available; GEV's two new
periods remain missing.

The remaining 19 missing periods are INTC (four), CVX (three), PG (five), GE
(five), and GEV (two). All expose the broader standard
`CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`; PG also exposes
`CashEquivalentsAtCarryingValue`, while GE exposes a further
disposal-group-inclusive variant. Those captions are not silently treated as
the approved gross cash-and-cash-equivalents primitive. Company Facts does not
provide dimensions, no filing-XBRL or segment aggregation is performed, and
multiple eligible selected-accession observations would remain ambiguous.

The current short-term-investment candidates appear in 121 periods across 25
issuers, including two periods with overlapping candidates, while only 25
periods resolve. Long-term candidate families appear in 60 periods across 14
issuers, while five resolve. These are not safe missing-to-zero cases: concept
semantics, overlap, restricted cash, equity investments, and current/noncurrent
classification must be reviewed before widening policy.

### D&A

At the original Phase 1H.3 baseline, D&A resolved in 110/200 periods: 105
direct and five through the approved MSFT derivation. Ninety periods across
19 issuers remained missing. Wave 1A added two GEV and two SNDK missing
periods, giving the pre-Wave-20 D&A corpus **110 resolved / 94 missing /
0 ambiguous across 204 periods**. The following Company Facts pattern counts
are historical screening, not the Wave 18 filing-XBRL inventory.

- `DepreciationAndAmortization` appears in 46 periods across ten issuers,
  including repeated gaps for V, LRCX, LIN, and VZ. Its relationship to the
  approved D&A definition must be verified before a general fallback.
- `DepreciationAmortizationAndAccretionNet` appears in all five WMT, MA, and GE
  periods. Accretion makes it a distinct methodology case, not an equivalent
  fallback.
- `Depreciation` appears in 141 periods and
  `AmortizationOfIntangibleAssets` in 139, but completeness and nonoverlap are
  issuer- and period-dependent. The MSFT derivation cannot be generalized by
  concept presence alone.
- GOOGL still lacks sufficient complete direct/component evidence under the
  approved methodology.
- No repeatable issuer-extension D&A family was present in Company Facts for
  the missing issuers. Filing-level XBRL may provide evidence, but that remains
  explicit research. Impairment and lease amortization are not silently added.

Wave 18 now inspects all 94 selected instances first and records complete
context/namespace/unit/occurrence and submitted presentation/calculation
evidence. Thirty-one periods expose nondimensional
`DepreciationAndAmortization`; none exposes the current direct concept
nondimensionally for the exact annual period. Filing evidence exposes AMD's
changing extension pattern and broader GOOGL/TSLA/PM impairment captions,
notwithstanding the earlier lack of a repeatable Company Facts extension
family. Broad cash-flow add-backs, software/contract distinctions, embedded
leases, rounded note values and GE's mixed-business perimeter require separate
review. Only five Visa periods currently support safe potential scope-design
coverage; 89 are unapproved. No period becomes zero or resolves in production.

Wave 19's [scope-evidence design](../depreciation-amortization-scope-evidence-design.md)
reaches PARTIAL GO for five exact Visa curated entries; no generic automated
combined-concept approval. All 94 remain production missing. The 89 no-entry
controls retain Wave 18 routing (26 CONCEPT_POLICY, 33 DERIVATION, five
ISSUER_EXTENSION, 25 METHODOLOGY_BLOCKER), not fresh reviewed denials. Semantic
duplicates confirm only after exact eligibility; conflicts remain ambiguous.
Supporting asset notes and 2025 precision cannot become residual operands or
lease adjustments. Wave 20 implements only that five-entry foundation:
115 resolved / 89 missing / 0 ambiguous; all controls stay missing.

Wave 21's [component-completeness design](../depreciation-amortization-component-derivation-design.md)
and [machine-checkable matrix](../depreciation-amortization-component-derivation-matrix.json)
review exactly the 33 `DERIVATION` identities: AVGO/INTC/ABBV/MRK/TXN/ORCL
five each, GEV two and PM one. **NO-GO for implementation: 0 approved /
19 further research / 14 methodology-blocked**. The narrow design dispositions
are defined in that document; they neither replace the frozen routing counts
nor add production methodology-blocked states. Software/asset containment,
manufacturing/grant scope, rounded representations and known lease/impairment
mixes remain unresolved. Only specific lease-note gaps were fetched; no full
inventory or corpus was repeated. AMD's five extensions remain separately
gated, the other 61 inventory periods are not new reviewed denials, and all
five Visa approvals remain. Safe additional coverage is zero. Next is targeted
TXN 2021–2023 completeness/expense-scope closure, not a generic sum or policy.

### Pretax Income

Pretax Income now has 37 typed-missing periods and no remaining known
period-shape ambiguity. Thirty-three periods across AMZN, MU, MA, CVX, CAT, PM,
and LIN expose the exact annual standard concept
`IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments`.
Its formal scope excludes equity-method income or loss, unlike the current
approved concept, so frequency and matching statement labels do not make it an
unconditional fallback. It remains `NEEDS_MORE_RESEARCH`; current instance-only
filing-XBRL evidence cannot establish statement role, placement, or equity-
method scope generically.

Wave 10 exact-period note research resolves the manual evidence question but
not the production boundary. Eight periods (MA and CVX) have direct
issuer-specific evidence that equity-method activity enters the candidate
Pretax amount; 20 (AMZN, MU, CAT, and PM) present it separately net of tax; and five
LIN periods have mixed included and after-tax treatment and remain unresolved.
The result rejects a global alias and supplies no machine-checkable generic
rule. Wave 11 also rejects automated structured discovery but finds a curated,
versioned exact-accession policy methodologically acceptable for the eight
positives. Wave 12 implements only those eight approvals. The 20
separate-net-of-tax controls and five LIN mixed-treatment controls remain
missing, while each resolved result retains the reviewed policy and all
confirming filing-XBRL occurrence provenance.

The remaining 12 periods are ORCL five, MCD five, and PG two. Their exact annual
Pretax evidence is present only as selected-filing issuer extensions. The same
local name across two issuer namespaces is not a reusable family, and Oracle
uses a different extension family. Domestic and foreign Pretax components
appear in 39 candidate periods but are jurisdiction pieces, not direct
substitutes. No missing value is treated as zero and no arithmetic derivation
is approved. Production Pretax is 167 resolved / 37 missing / 0 ambiguous.

### Operating NWC

META and COST produce ten O-NWC levels and eight comparable changes. GOOGL,
MSFT, and AAPL produce 15 methodology-blocked levels and 12 blocked changes.
The issuers without a valuation-perimeter policy produce 179 missing levels and
142 missing changes. Each of the 42 nonempty histories has one correctly
not-comparable opening change period.

Raw standard facts demonstrate why a universal residual formula is unsafe:
`AccountsReceivableNetCurrent` is eligible in 166 periods,
`InventoryNet` in 171, `AccountsPayableCurrent` in 182, and
`ContractWithCustomerLiabilityCurrent` in 94. Absence can reflect sector
economics or a concept variant. Retail, pharmaceutical, asset-light payment,
technology, industrial, and energy issuers require evidence-backed component
classification; broad residual current-asset/liability captions remain
excluded.

### Debt

Current debt resolves in 116 periods and noncurrent debt in 140. Evidence for
common unapproved variants is widespread:

- `DebtCurrent` appears in 73 periods across 16 issuers.
- `LongTermDebtAndCapitalLeaseObligationsCurrent` appears in 41 periods across
  nine issuers.
- `LongTermDebtAndCapitalLeaseObligations` appears in 60 periods across 13
  issuers.
- `CommercialPaper` appears in 57 periods across 13 issuers while the current
  scoped policy resolves 12.
- `OtherShortTermBorrowings` appears in 16 periods across four issuers while
  the current scoped policy resolves one.

Some variants combine leases, current maturities, or total debt, and 57
current-debt periods expose more than one candidate family. They require
carrying-value and overlap analysis. Missing commercial paper, borrowings, or
debt may also be genuine zero/absence; no zero is inferred and no total-debt
fallback is proposed.

### Shares and core flow measures

Diluted weighted-average shares resolve in 196/204 periods. V has no matching
Company Facts fact in its five selected filings. MCD resolves two periods, but
three later facts are floating values such as `751.8` in a `shares` unit and
fail the integer/share-basis boundary. Both need filing-level scale and
presentation research. GOOGL's three A+C derivations and two direct periods
remain unchanged; historical weighted-average shares remain distinct from the
future DCF denominator.

Income-tax expense resolves 204/204. Revenue resolves 193/204 with no missing
periods and 11 same-period concept ambiguities. Operating income was missing in
35 periods across LLY, JNJ, CVX, MRK, GE, KLAC, and IBM before Wave 16. Wave 13 proves that
none of those exact face statements reports a consolidated Operating Income
subtotal. Pretax income is missing in 37 periods and ambiguous in none;
reported ETR mirrors that upstream
availability. Several missing pretax issuers
report the standard minority-interest/equity-method variant, making it a
candidate for explicit semantic research. Capex is missing in 57 periods; the
common `PaymentsToAcquireProductiveAssets` and industry-specific PP&E concepts
are broader or different from the approved gross PP&E cash-purchase definition
and are not automatic fallbacks. No new sign defect was observed.

Wave 14 proves complete component derivations for the 25 LLY/JNJ/MRK/KLAC/IBM
periods without using Pretax as a residual. All 25 are approved research
patterns, with acquired IPR&D, restructuring, operating-asset impairments,
pension service cost, and IBM IP/custom-development income inside the reviewed
operating perimeter; interest, non-service pension components, and reviewed
other non-operating activity remain outside. They are potential—not current—
coverage at the Wave 14 baseline. Wave 15 freezes the versioned exact-accession
policy/model boundary, including occurrence conflicts, arithmetic, provenance,
serialization, IBM validation, and Operating Tax gates; it adds no result.
Wave 16 implements that boundary and resolves those exact 25 periods, leaving
only five CVX and five GE Operating Income gaps for separate perimeter research.
Wave 17 completes that research with zero safe additional coverage: five CVX
business-perimeter gaps and five GE mixed industrial/insurance methodology
gaps remain missing. No generic subtotal, segment-profit substitution or
common-five-year recast is approved.

## Wave 2 ambiguity inventory and Wave 6 disposition

The table records the 24 original Phase 1H.3 ambiguous outputs from selected
10-K accessions. Wave 1A subsequently exposed three SNDK period-association
ambiguities. Wave 6 resolves the 13 JNJ/ABBV/GE/ORCL rows and all three SNDK
rows. The 11 WMT/MA/CVX Revenue rows below remain; no amendment or
cross-accession collision is involved.

| Issuer | Report date | Selected accession | Measure | Candidates | Candidate concepts | Result reason |
|---|---|---|---|---:|---|---|
| JNJ | 2023-12-31 | `0000200406-24-000013` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax` ×2 | `multiple_annual_periods` |
| JNJ | 2023-12-31 | `0000200406-24-000013` | Pretax income | 2 | `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` ×2 | `multiple_annual_periods` |
| JNJ | 2023-12-31 | `0000200406-24-000013` | Reported ETR | 2 | The two ambiguous pretax operands | `incompatible_derivation_operands` |
| WMT | 2022-01-31 | `0000104169-22-000012` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `conflicting_concept_values` |
| WMT | 2023-01-31 | `0000104169-23-000020` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| WMT | 2024-01-31 | `0000104169-24-000056` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| WMT | 2025-01-31 | `0000104169-25-000021` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| WMT | 2026-01-31 | `0000104169-26-000055` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| ABBV | 2021-12-31 | `0001551152-22-000007` | Revenue | 3 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` ×2 | `multiple_annual_periods` |
| ABBV | 2022-12-31 | `0001551152-23-000011` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ABBV | 2023-12-31 | `0001551152-24-000011` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ABBV | 2024-12-31 | `0001551152-25-000020` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ABBV | 2025-12-31 | `0001551152-26-000008` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| MA | 2021-12-31 | `0001141391-22-000023` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `conflicting_concept_values` |
| CVX | 2021-12-31 | `0000093410-22-000019` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `conflicting_concept_values` |
| CVX | 2022-12-31 | `0000093410-23-000009` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| CVX | 2023-12-31 | `0000093410-24-000013` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| CVX | 2024-12-31 | `0000093410-25-000009` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| CVX | 2025-12-31 | `0000093410-26-000078` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| GE | 2021-12-31 | `0000040545-22-000008` | Revenue | 3 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` ×2 | `multiple_annual_periods` |
| GE | 2022-12-31 | `0000040545-23-000023` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| GE | 2023-12-31 | `0000040545-24-000027` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| GE | 2024-12-31 | `0000040545-25-000015` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ORCL | 2022-05-31 | `0001564590-22-023675` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `multiple_annual_periods` |

The 11 WMT/MA/CVX cases remain `CONCEPT_POLICY` conflicts. The JNJ, ABBV, GE,
and ORCL `PERIOD_ASSOCIATION` cases and the downstream JNJ ETR result are now
resolved using the authoritative DEI period. All candidates retain the selected
accession and official Company Facts provenance.

## Methodology-blocked and expected missing

All 27 methodology-blocked outputs are intentional O-NWC states: five levels
and four changes each for GOOGL, MSFT, and AAPL. They are not parser or
extraction failures. The first change for every one of the 42 nonempty histories
is `NOT_COMPARABLE`, accounting for all 42 such states. `NOT_COMPARABLE` is its
own standardized-output status and is not a missing result or a form of
`EXPECTED_TYPED_MISSING`.

`EXPECTED_TYPED_MISSING` requires affirmative filing evidence of economic
absence or non-applicability. Potential candidates, only after affirmative
filing confirmation, include no commercial paper, short-term borrowing,
current debt, or long-term marketable securities in a particular period. In
contrast, CIK-scoped policies that ignore an otherwise eligible fact,
unapproved standard variants, absent issuer-level O-NWC policy, and
period/concept conflicts are generalization gaps. The 1,673 missing results are
not relabeled wholesale: unresolved cases remain missing until filing evidence
establishes the correct category.

## Issuer-level post-smoke classification

`SUPPORTED` requires expected history and no material technical or policy gap
in core standardized output. The classification is a Phase 1H planning result;
it does not alter the frozen snapshot or production policy.

| Issuer | Classification | Primary evidence |
|---|---|---|
| NVDA | `GENERALIZATION_REQUIRED` | Cash/O-NWC scope and Capex gap |
| AAPL | `GENERALIZATION_REQUIRED` | O-NWC methodology blocker |
| MSFT | `GENERALIZATION_REQUIRED` | O-NWC methodology blocker |
| AMZN | `GENERALIZATION_REQUIRED` | Pretax, Capex, cash, and O-NWC gaps |
| GOOGL | `GENERALIZATION_REQUIRED` | D&A and O-NWC methodology blockers |
| AVGO | `GENERALIZATION_REQUIRED` | D&A, debt, cash, and O-NWC gaps |
| META | `SUPPORTED` | Five-period core output and valuation-ready O-NWC |
| MU | `GENERALIZATION_REQUIRED` | Pretax, debt, cash, and O-NWC gaps |
| TSLA | `GENERALIZATION_REQUIRED` | D&A, debt, cash, and O-NWC gaps |
| AMD | `GENERALIZATION_REQUIRED` | D&A, debt, cash, and O-NWC gaps |
| BRK-B | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial/conglomerate methodology |
| LLY | `GENERALIZATION_REQUIRED` | Operating income, Capex, debt, cash, and O-NWC gaps |
| JPM | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| XOM | `GENERALIZATION_REQUIRED` | Ticker/CIK registrant succession blocks history |
| JNJ | `GENERALIZATION_REQUIRED` | Period ambiguity, operating income, cash, and O-NWC gaps |
| V | `GENERALIZATION_REQUIRED` | Shares, D&A, Capex, cash, and O-NWC gaps |
| INTC | `GENERALIZATION_REQUIRED` | D&A, cash, and O-NWC gaps |
| WMT | `GENERALIZATION_REQUIRED` | Revenue ambiguity, D&A, cash, and O-NWC gaps |
| ABBV | `GENERALIZATION_REQUIRED` | Revenue-period ambiguity, D&A, debt, cash, and O-NWC gaps |
| MA | `GENERALIZATION_REQUIRED` | Revenue conflict, pretax, D&A, cash, and O-NWC gaps |
| CSCO | `GENERALIZATION_REQUIRED` | Cash/investment and O-NWC scope |
| LRCX | `GENERALIZATION_REQUIRED` | D&A, Capex, cash, debt, and O-NWC gaps |
| PLTR | `GENERALIZATION_REQUIRED` | Cash, debt, and O-NWC scope |
| AMAT | `GENERALIZATION_REQUIRED` | Partial D&A/debt plus cash and O-NWC gaps |
| CVX | `GENERALIZATION_REQUIRED` | Revenue conflict and multiple core concept gaps |
| COST | `SUPPORTED` | Five-period core output and valuation-ready O-NWC |
| CAT | `GENERALIZATION_REQUIRED` | Pretax, current debt, cash, and O-NWC gaps |
| MRK | `GENERALIZATION_REQUIRED` | Operating income, D&A, Capex, cash, and O-NWC gaps |
| BAC | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| PG | `GENERALIZATION_REQUIRED` | Partial pretax plus cash and O-NWC gaps |
| UNH | `SPECIALIZED_METHODOLOGY_REQUIRED` | Insurance/specialized methodology |
| KO | `GENERALIZATION_REQUIRED` | Debt, cash, and O-NWC gaps |
| GE | `GENERALIZATION_REQUIRED` | Revenue-period ambiguity and operating-income/D&A/debt gaps |
| PM | `GENERALIZATION_REQUIRED` | Pretax, D&A, debt, cash, and O-NWC gaps |
| HD | `GENERALIZATION_REQUIRED` | Capex, debt, cash, and O-NWC gaps |
| NFLX | `GENERALIZATION_REQUIRED` | Current debt, cash, and O-NWC gaps |
| KLAC | `GENERALIZATION_REQUIRED` | Operating income, debt, cash, and O-NWC gaps |
| TXN | `GENERALIZATION_REQUIRED` | D&A, cash, and O-NWC gaps |
| GEV | `GENERALIZATION_REQUIRED` | Company Facts zero-padded CIK schema blocker |
| GS | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| SNDK | `GENERALIZATION_REQUIRED` | Company Facts zero-padded CIK schema blocker |
| ORCL | `GENERALIZATION_REQUIRED` | Revenue period, pretax, D&A, debt, cash, and O-NWC gaps |
| WFC | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| MS | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| LIN | `GENERALIZATION_REQUIRED` | Pretax, D&A, cash, and O-NWC gaps |
| IBM | `GENERALIZATION_REQUIRED` | Operating income, D&A, current debt, cash, and O-NWC gaps |
| QCOM | `GENERALIZATION_REQUIRED` | Capex, cash, and O-NWC gaps |
| VZ | `GENERALIZATION_REQUIRED` | D&A, Capex, debt, cash, and O-NWC gaps |
| PEP | `GENERALIZATION_REQUIRED` | Capex, current debt, cash, and O-NWC gaps |
| MCD | `GENERALIZATION_REQUIRED` | Share scale, pretax, current debt, cash, and O-NWC gaps |

Reconciliation: two `SUPPORTED`, 41 `GENERALIZATION_REQUIRED`, and seven
`SPECIALIZED_METHODOLOGY_REQUIRED`, totaling 50 issuers. All 43 generic
issuers have one post-smoke classification.

## Ranked generalization backlog

| Priority | Root cause | Evidence / affected scope | Blocking scope | Candidate fix | Generalizability | Accounting risk |
|---:|---|---|---|---|---|---|
| 1 | `COMPANY_FACTS_SCHEMA` | GEV and SNDK; four selected periods | Entire issuer | **Implemented in Wave 1A:** strict ten-digit padded-string CIK support with equality protection | High | Low |
| 2 | `TICKER_CIK_IDENTITY` | XOM; intended five-year history | Entire issuer | **Wave 1B NO-GO:** structured SEC evidence does not encode the directed legal edge; retain unresolved until a generic exact-CIK succession parser is independently supported | Medium | Medium-high |
| 3 | `CONCEPT_POLICY` | **Implemented in Wave 2:** 160 additional periods resolved; 19 broader-caption periods remain missing | One high-value balance | Keep broader restricted-cash and cash-equivalents-only captions unresolved pending separate evidence | Very high | Low |
| 4 | `CONCEPT_POLICY` / `PERIOD_ASSOCIATION` | **Implemented in Wave 6:** all known annual/Q4 collisions resolved; 11 genuine full-year conflicts remain for WMT, MA, and CVX | Core flow metric | Preserve distinct concept economics and never select by size or order | High | Medium |
| 5 | `CONCEPT_POLICY` | **Implemented in Wave 12:** 8/33 standard-variant periods resolve under the reviewed exact-accession policy; 20 separate-net-of-tax and five mixed-treatment controls plus 12 issuer-extension periods remain missing | Core flow and diagnostic | Preserve the frozen v1 registry, full occurrence provenance, current-concept precedence, and missing-by-default future/amended filings | Medium | Medium-high |
| 6 | `DERIVATION` / `CONCEPT_POLICY` | **Implemented in Wave 16:** 25 exact LLY/JNJ/MRK/KLAC/IBM derivations resolve; **Wave 17 NO-GO:** ten CVX/GE periods remain missing | Core FCFF input | Preserve v1; CVX affiliate scope and GE industrial/insurance carve-out or recast require separate methodology research | Medium | Very high |
| 7 | `DERIVATION` / `CONCEPT_POLICY` | **Wave 20 implemented:** five exact Visa D&A acceptances; **Wave 21 NO-GO:** 33 proposals = 19 research + 14 methodology-gated; all 89 controls unchanged | Core FCFF input | Target TXN 2021–2023 completeness/expense-scope closure; AMD and lease/impairment/accretion boundaries remain separately gated | No additional approval | High |
| 8 | `CONCEPT_POLICY` | Capex: 57 missing across the 204-period corpus | Core FCFF input | Validate productive-asset and industry PP&E concepts against definition | Medium-high | High |
| 9 | `CONCEPT_POLICY` | Short investments: 179 missing; long investments: 199 missing | Equity bridge | Evidence-backed current/noncurrent investment policies | High | Medium-high |
| 10 | `CONCEPT_POLICY` / `DERIVATION` | Current debt 88 missing; noncurrent 64; widespread combined variants | Equity bridge | Carrying-value, lease, and overlap-aware variants | High | High |
| 11 | `CONCEPT_POLICY` | Commercial paper 192 missing; short borrowings 203 missing | Equity bridge | Generalize exact concepts only where economically present | High | Medium |
| 12 | `METHODOLOGY_BLOCKER` | 35 issuers without O-NWC policy; three blocked seed policies | O-NWC and change | Sector-clustered component research and versioned perimeters | Medium | Very high |
| 13 | `CONCEPT_POLICY` / filing evidence | V five share gaps; MCD three scale/type gaps | Per-share history | Filing-XBRL denominator and scale validation | Low-medium | Medium |

## Recommended Phase 1H.4 waves

1. **Infrastructure/schema blockers:** Wave 1A completed and tested strict
   padded Company Facts CIK normalization. Wave 1B completed the
   registrant-succession identity-linkage design and reached NO-GO for a generic
   automated resolver; keep XOM unresolved and do not add a hardcoded link.
2. **High-frequency, low-risk standard facts:** exact cash generalization is
   implemented; retain the 19 broader-caption cases as typed missing. Wave 3
   rejected heuristic fiscal-year signals. Wave 4 found a GO design using the
   filing-XBRL DEI required context; Wave 5 implemented the pure resolver, and
   Wave 6 integrated it for the three approved metrics. Preserve the 11
   same-period Revenue concept conflicts. Wave 7 leaves the 33-period Pretax
   variant `NEEDS_MORE_RESEARCH`. Wave 8 authorizes only a read-only 33-period
   presentation-evidence diagnostic; Wave 9 establishes statement membership.
   Wave 10 finds eight included-Pretax, 20 separate-net-of-tax, and five mixed-
   treatment periods but no machine-checkable equivalence rule. Wave 11 rejects
   an automated rule and approves only a curated, versioned exact-accession
   design with reviewed evidence and conservative defaults. Wave 12 implements
   and validates that narrow foundation for exactly the eight positives; all 25
   controls and 12 extension periods remain unresolved. Wave 13 inventories all
   35 Operating Income gaps, finds zero direct equivalents, and sends only the
   25 LLY/JNJ/MRK/KLAC/IBM component patterns to derivation-evidence design;
   CVX and GE retain separate perimeter risk. Wave 14 approves all 25 exact
   component equations after complete Revenue-to-Operating-Income and
   Operating-Income-to-Pretax reconciliation. Wave 15 freezes the curated
   exact-accession policy/model, selection, arithmetic, failure, provenance,
   serialization, Operating Tax, and regression design. Wave 16 implements and
   validates all 25 exact entries, preserves 169 direct results, and retains
   ten missing CVX/GE controls. Wave 17 completes their separate perimeter
   research with NO-GO; no coverage or production classification changes.
3. **Core FCFF flows:** Wave 18 completes the exact 94-period D&A inventory.
   Wave 19 freezes scoped acceptance for five exact Visa entries and 89
   unapproved controls. Wave 20 implements that foundation; Wave 21 reviews
   all 33 derivation periods with no approved equation. Next close TXN
   2021–2023 completeness/expense-scope evidence. Keep issuer-extension and
   lease-perimeter research separately gated.
   Then investigate Capex
   variants. CVX/GE mixed-business designs remain separate. Approve only
   repeatable definitions with
   selected-accession evidence.
4. **Equity-bridge balances:** generalize investments, commercial paper,
   borrowings, and debt with explicit overlap, lease, and absence rules.
5. **Narrow evidence-backed policies:** address V/MCD shares and any filing-XBRL
   issuer extensions; build O-NWC perimeters by repeatable sector/component
   clusters rather than residual formulas.
6. **Corpus rerun and reclassification:** reproduce all counts, preserve typed
   absence and ambiguity, and reassess issuer classifications before Phase
   1H.5.
