# Project Status

## Current Milestone

Phase 1H expands historical normalization beyond the original five-company
corpus. Phase 1H.1 froze the S&P 500 Top 50 Index snapshot effective 2026-10-02
at `docs/universe/sp500-top-50-2026-10-02.csv`. Its 51 securities represent 50
unique SEC issuers because Alphabet has two included share classes. The
preliminary security classification contains six supported-seed rows (five
issuers), 38 operating-company candidates, and seven
specialized-methodology candidates.

Phase 1H.2 executed the current production pipeline for all 43 generic issuers.
Forty-one reached standardized output, while GEV and SNDK failed at Company
Facts parsing with the existing invalid-CIK validation error. The seven
specialized issuers remained represented as explicit skips. XOM reached
standardized output with zero selected annual periods; this and all typed
missing or ambiguous results remained evidence rather than automatic
methodology conclusions.

Phase 1H.3 completed the root-cause analysis in
`docs/universe/sp500-top-50-failure-taxonomy.md`. It reconciles all 3,400
standardized measure states for the 40 five-period histories, inventories all
24 ambiguities and 27 methodology blockers, diagnoses GEV/SNDK as one
zero-padded Company Facts CIK schema case, and diagnoses XOM as a ticker/CIK
registrant-succession case. The post-smoke issuer classification is two
`SUPPORTED`, 41 `GENERALIZATION_REQUIRED`, and seven
`SPECIALIZED_METHODOLOGY_REQUIRED`.

Phase 1H.4 Wave 1A implemented the first shared schema fix. Company Facts now
accepts an exact ten-digit padded CIK only when it equals the requested
company's `cik_padded`; arbitrary leading-zero strings and identity mismatches
remain invalid. Live reruns moved both GEV and SNDK through Company Facts and
all later stages to standardized output, with two annual periods each. The
full corpus rerun completed all 43 generic attempts with no stage failures and
left every five-issuer seed result unchanged. No issuer hardcode was added.

Phase 1H.4 Wave 1B completed the registrant-succession design in
`docs/sec-identity-linkage.md`. Official XOM filings establish the human-reviewed
edge from predecessor CIK 34088 to current successor CIK 2115436, effective
2026-07-01. The design nevertheless reached **NO-GO** for a generic automated
resolver: public structured SEC sources discover candidates but do not encode
the directed legal edge, while the decisive relationship remains in variable
narrative filing text. Cross-listing alone is explicitly rejected. No source
or test code changed, no issuer mapping was added, and XOM remains unresolved
in production.

Phase 1H.4 Wave 2 generalized the exact standard
`us-gaap:CashAndCashEquivalentsAtCarryingValue` Company Facts policy by removing
its five-seed-CIK restriction while preserving the existing selected-accession,
current-instant, report-date, USD, integer, and ambiguity rules. A live corpus
rerun increased cash coverage from 25 resolved / 179 missing / 0 ambiguous to
185 resolved / 19 missing / 0 ambiguous across the 204 selected periods. The
160 new resolutions span 34 issuers. The difference from the Phase 1H.3
estimate of 158 is SNDK's two exact eligible periods, which became available
after Wave 1A fixed its padded Company Facts CIK.

The 19 remaining cash gaps are INTC (four periods), CVX (three), PG (five), GE
(five), and GEV (two). Their selected filings expose broader restricted-cash
captions; PG also uses `CashEquivalentsAtCarryingValue`, and GE has a
disposal-group-inclusive caption. Wave 2 does not treat those concepts as the
same primitive, derive unrestricted cash, consume filing XBRL, or combine cash
with investments. Aggregate standardized states reconciled exactly to 1,823
resolved, 1,549 missing, 27 ambiguous, 27 methodology-blocked, and 42
not-comparable, with all 3,468 states and all other measure statuses unchanged.

Phase 1H.4 Wave 3 researched annual-period association and reached a blocked
result. A selected 10-K can contain both fiscal-year and Q4 durations, and a
unique current diluted-share duration ending on the report date does not prove
annuality. No source evaluated in that wave established the fiscal-year start,
so no automatic period filter was added. The 11 full-year/Q4
revenue collisions across JNJ, ABBV, GE, and ORCL remain typed ambiguity, as do
JNJ pretax and downstream reported ETR, plus SNDK pretax, income-tax expense,
and downstream reported ETR.

The other 11 revenue ambiguities are genuine full-year concept conflicts: five
WMT periods, one MA period, and five CVX periods. Filing presentation shows WMT
net sales versus total revenues, MA gross versus net revenue, and CVX sales and
other operating revenues versus revenues and other income. Those economic
definitions differ, so Wave 3 adds no global or issuer-specific precedence and
does not select by size or concept order. The corpus therefore remains at the
Wave 2 baseline: 1,823 resolved, 1,549 missing, 27 ambiguous, 27
methodology-blocked, and 42 not-comparable across 204 periods and 3,468 states.

Phase 1H.4 Wave 4 found authoritative annual-period evidence and records a
**GO** design in `docs/annual-period-evidence.md`. SEC staff guidance for EDGAR
validation describes the DEI required context for an exact 10-K as the
dimensionless duration matching the year of the submission reporting period;
the EDGAR Filer Manual and applicable filing requirements remain controlling.
A read-only diagnostic verified one consistent
DEI FY context across 42 selected filings for JNJ, ABBV, GE, ORCL, WMT, COST,
SNDK, META, and MSFT, including non-calendar and 52/53-week histories. All
eligible non-parenthetical duration-statement anchors independently matched the
same period. No production filter was added in this research milestone, so the
Wave 2 corpus totals and all 22 revenue ambiguities remain unchanged.

Phase 1H.4 Wave 5 implements the pure, network-free SEC-layer annual-period
resolver. Filing-XBRL contexts now preserve the raw entity-identifier scheme;
the resolver requires `http://www.sec.gov/CIK` plus a value matching the filing
registrant. It groups equivalent context IDs by normalized entity, dimensions,
period, and DEI values; identical duplicates confirm, conflicting same-context
DEI values are data errors, and different valid periods remain ambiguity. Its
immutable result types distinguish resolved, not-found, ambiguous, unsupported,
and data-error outcomes while retaining all confirming context IDs and DEI
provenance.

Thirteen focused annual-period tests and 18 filing-XBRL tests pass. Read-only
validation against the same 42 selected exact 10-Ks resolved all 42 and matched
every Wave 4 start/end date, including JNJ's annual/Q4 collision, COST's 53-week
year, SNDK's non-calendar year, and valid year-quarter SEC DEI namespaces. No
normalization integration was added, so all 22 revenue ambiguities and the Wave
2 standardized corpus totals remain unchanged.

Phase 1H.4 Wave 6 explicitly integrates typed annual-period results into annual
normalization for Revenue, Pretax Income, and Income Tax Expense only. A
resolved result filters CURRENT duration candidates to its exact `(start, end)`
before ambiguity evaluation. Not-found, ambiguous, and unsupported results
retain prior candidate behavior, while a data-error result stops normalization.
Each filing result retains the annual-period outcome beside existing metric
provenance; the standardized-output schema is unchanged.

The full 204-period corpus rerun resolved 11 annual/Q4 Revenue ambiguities, JNJ
Pretax Income and downstream Reported ETR, and SNDK Pretax Income, Income Tax
Expense, and downstream Reported ETR. Revenue is now 193 resolved / 0 missing /
11 ambiguous. The remaining conflicts are five WMT periods, one MA period, and
five CVX periods whose competing concepts span the same authoritative annual
period. Aggregate states reconcile to 1,839 resolved, 1,549 missing, 11
ambiguous, 27 methodology-blocked, and 42 not-comparable across 3,468 states.
All other measure states and the five-company seed metric results are unchanged;
all 43 generic attempts completed and seven specialized issuers remained
skipped. Seventy-five historical-normalization tests, 17 corpus-runner tests,
304 normalization tests, and 461 tests overall pass.

Phase 1H.4 Wave 7 inventories all 45 remaining Pretax Income gaps in
`docs/pretax-income-concepts.md` and reaches **PARTIAL GO FOR FURTHER
RESEARCH/DESIGN ONLY** for one recurring standard concept. The concept
`IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments`
is an exact annual Company Facts observation in 33 periods across seven
issuers, but its taxonomy definition excludes equity-method income or loss.
It remains `NEEDS_MORE_RESEARCH` and is not approved for normalization: being
the reported tax denominator does not prove equivalence to the current Pretax
scope. Current filing-XBRL tooling does not preserve presentation roles or
statement placement needed to make that evidence machine-checkable. The other
12 gaps use issuer extensions across ORCL, MCD, and PG;
domestic/foreign components and extension local-name matching remain
unapproved. Structural candidate coverage is 33 periods, safe new resolutions
are zero, and no production policy or corpus result changed. Independent review
confirmed that numerical equality, tax-denominator status, and primary-statement
placement are not sufficient evidence of semantic equivalence.

Phase 1H.4 Wave 8 defines Pretax presentation-evidence research in
`docs/pretax-presentation-evidence-design.md` and reaches **PARTIAL GO FOR A
READ-ONLY RESEARCH DIAGNOSTIC**. Filer-submitted presentation roles can classify
ordered `Statement` membership, while the extracted instance binds the exact
fact and annual context. SEC render artifacts remain corroborating derivatives,
and equity-method note evidence remains a separate semantic gate. The design
does not change `PRETAX_INCOME_POLICY`, the current Pretax primitive, production
models, or corpus results.

Phase 1H.4 Wave 9 implements the development-only, read-only diagnostic and
records its live results in `docs/pretax-presentation-evidence-results.md`. All
33 frozen standard-concept candidate periods reconciled to the exact selected
10-K, authoritative annual context, exact USD fact, submitted schemas and
presentation linkbases, and SEC-renderer artifacts. Every candidate belongs to
one submitted `Statement` role and one to three submitted `Disclosure` roles;
all 33 therefore classify as `MULTIPLE_ROLE_MEMBERSHIP`. MetaLinks and an
applicable R-file corroborated all 33, with zero presentation data errors.

The evidence-pattern decision is **NEEDS_MORE_RESEARCH**. Statement membership
is established but equity-method scope remains a separate semantic gate. The
issuer matrix retains direct evidence of `SEPARATE_NET_OF_TAX` for AMZN and
`INCLUDED_PRETAX` for CVX while MU, MA, CAT, PM, and LIN remain `UNRESOLVED`;
these classifications do not approve any period. Safe new Pretax resolutions
remain zero, and production policies, standardized outputs, and corpus totals
are unchanged.

Phase 1H.4 Wave 10 completes exact-period equity-method note research in
`docs/pretax-equity-method-note-evidence.md` using the 33 frozen selected
accessions. Direct filing evidence classifies eight periods as `INCLUDED_PRETAX`
(MA three and CVX five), 20 as `SEPARATE_NET_OF_TAX` (AMZN, MU, CAT, and PM
five each), and five as `UNRESOLVED` (LIN). Linde directly reports mixed
treatment: corporate-investee income is after tax while partnership/LLC
investee income enters Pretax. No period is `SEPARATE_PRETAX` or
`NO_MATERIAL_ACTIVITY_FOUND`.

The same candidate concept therefore has issuer-dependent economics. Manual
exact-accession evidence establishes inclusion for eight periods, but no
deterministic, machine-checkable economic-equivalence rule was established.
Safe new production Pretax resolutions remain zero; `PRETAX_INCOME_POLICY`,
the 159 resolved / 45 missing / 0 ambiguous Pretax corpus result, and all
aggregate corpus totals remain unchanged. The 12 issuer-extension periods were
excluded as required.

Phase 1H.4 Wave 11 completes the separately reviewed scope-evidence design in
`docs/pretax-scope-evidence-design.md` and reaches **PARTIAL GO**. No automated
structured-evidence rule separates the eight MA/CVX positives from the 20
separate-net-of-tax and five LIN mixed-treatment controls: all 33 share the
same candidate and multiple-role presentation pattern, while MA's tag
transition and CVX's taxonomy/presentation mismatch require manually reviewed
filing evidence.

A curated, immutable `pretax_scope_equivalence_v1` registry is methodologically
acceptable for the eight exact CIK/accession/period/concept facts, provided a
later implementation retains policy version and reviewed evidence provenance,
keeps the current approved concept first, and defaults every future, amended,
or unregistered filing to missing. This is deterministic execution of manual
research, not automated discovery or a generic concept fallback. Wave 11 adds
no registry or source behavior: all 33 remain production missing, safe new
Pretax resolutions remain zero, and Pretax remains 159 resolved / 45 missing /
0 ambiguous.

Phase 1H.4 Wave 12 implements and validates that exact boundary. The immutable
`pretax_scope_equivalence_v1` registry contains only the eight reviewed MA/CVX
CIK-accession-period facts. The generic `PRETAX_INCOME_POLICY` remains
unchanged and retains precedence. The curated resolver groups eligible
nondimensional filing-XBRL occurrences by a complete semantic signature,
allowing MA's three repeated occurrences and CVX's two repeated nondimensional
occurrences to confirm one value while excluding CVX's dimensioned facts. It
retains every occurrence, original representation, and deterministic ordinal
through normalized Pretax, standardized-output schema version 2, serialization,
and Reported ETR supporting-policy provenance.

Focused validation passes 122 tests, the complete suite passes 491 tests, and
targeted live normalization resolves exactly eight Pretax and eight Reported
ETR periods. The full 204-period corpus produces Pretax and Reported ETR at
167 resolved / 37 missing / 0 ambiguous each. All 25 controls and all 12
ORCL/MCD/PG issuer-extension periods remain missing. Aggregate states reconcile
exactly to 1,855 resolved, 1,533 missing, 11 ambiguous, 27
methodology-blocked, and 42 not-comparable across 3,468 states; the only corpus
changes are the eight Pretax and eight corresponding Reported ETR resolutions.

Phase 1H.4 Wave 13 completes the exact selected-filing
[Operating Income concept inventory](operating-income-concepts.md). All 35
missing periods—five
each for LLY, JNJ, CVX, MRK, GE, KLAC, and IBM—reconcile to their frozen
selected accessions, authoritative annual periods, submitted income-statement
roles, and SEC-rendered face statements. None reports a consolidated Operating
Income subtotal, none has an exact Company Facts observation, and none has an
exact annual nondimensional filing-XBRL Operating Income fact. GE 2024 and 2025
contain only economically distinct dimensioned segment and reconciliation
`OperatingIncomeLoss` facts.

Wave 13 reaches **NO-GO FOR DIRECT CONCEPT-POLICY EXPANSION**. Safe potential
direct coverage is zero. Twenty-five LLY/JNJ/MRK/KLAC/IBM periods have
component patterns that require separate derivation-evidence design; CVX has no
reported consolidated Operating Income, while GE requires separate
business/perimeter and segment-reconciliation research. No source, test, or
policy changes were made, all 35 periods remain missing, and production counts
remain unchanged.

Phase 1H.4 Wave 14 completes the
[Operating Income component-derivation evidence design](operating-income-derivation-design.md)
for those 25 exact LLY/JNJ/MRK/KLAC/IBM periods and reaches **PARTIAL GO**. All
25 are `DERIVATION_APPROVED`: each candidate starts from Revenue or an
independently reconciled Gross Profit, includes a complete and non-overlapping
operating-cost perimeter, and bridges through every separately reported
non-operating item to Pretax. Twenty-two Pretax bridges reconcile exactly; IBM
2022, 2023, and 2025 differ by only one displayed $1 million unit because its
face statements round every independently reported line to whole millions.

The reviewed perimeter includes acquired IPR&D, restructuring, operating-asset
impairments, pension service cost, and IBM IP/custom-development income. It
excludes interest, non-service pension components, and reviewed other
non-operating activity. No generic cross-issuer concept rule is approved:
changing concepts, issuer extensions, explicit row absence, LLY's differing-
precision IPR&D occurrences, and IBM's rounding boundary require a curated
exact-accession policy design. Safe potential coverage is 25 periods; CVX and
GE remain outside the pass. Production code, tests, policies, and counts remain
unchanged.

Phase 1H.4 Wave 15 completes the
[curated Operating Income derivation-policy design](operating-income-derivation-policy-design.md)
and reaches **PARTIAL GO** for a later narrow implementation. The proposed
immutable `operating_income_component_derivation_v1` registry contains only
the 25 reviewed exact CIK/accession/period equations. It freezes ordered signed
filing-XBRL operands, explicit row absence, exact-value and occurrence rules,
reviewed lower-precision LLY evidence, independent Gross Profit and Pretax
validation, direct-result precedence, complete provenance and serialization,
and an Operating Tax compatibility boundary.

IBM's three one-million Pretax differences remain validation-only signed
variances at the filing's whole-million display scale; no derived value is
rounded, normalized, or plugged. Equivalent occurrences may confirm only when
their complete semantic signature and exact `Decimal` agree. Unexpected values
remain ambiguous, structural evidence faults remain errors, and future,
amended, or unregistered filings produce no derivation. The ten CVX/GE periods
are frozen negative controls. No production code, test, policy, or corpus count
changes in this design wave.

The current validated standardized-output corpus contains 204 selected annual
periods across the 43 generic issuer attempts. All 43 attempts complete through
standardized output, while the seven specialized issuers remain explicit
skips. Validation means the production historical pipeline was run and checked
against expected filing evidence, not that every metric resolved; missing,
ambiguous, methodology-blocked, and not-comparable states remain explicit and
are never inferred as zero.

Phase 1H.4 Wave 16 implements and validates
`operating_income_component_derivation_v1` for exactly the 25 reviewed
LLY/JNJ/MRK/KLAC/IBM equations. The generic direct policy remains first;
filing-XBRL operands, exact identities, ordered signed arithmetic, every
confirming occurrence and reviewed nonselected evidence remain mandatory.
IBM's exact signed rounding variances are validation gates only. Standardized
output schema 3 and Operating Tax supporting-input serialization retain the
complete immutable provenance; no tax policy becomes ready automatically.

Validation: 163 focused tests and 513 complete-suite tests pass. Targeted live
validation resolves all 25 positives and keeps all ten CVX/GE controls missing.
The full 43-issuer run completes with seven specialized skips, 204 periods and
3,468 measure states. Operating Income is **194 resolved / 10 missing / 0
ambiguous** (169 direct, 25 derived). Aggregate states are **1,880 resolved /
1,508 missing / 11 ambiguous / 27 methodology-blocked / 42 not-comparable**.
Same-input comparisons preserve all 169 direct Operating Income results, all
25 seed annual financial results and 1,428 other financial results. All
non-Operating-Income metric states, execution stages and selected periods match
the prior validated corpus. Pretax and Reported ETR each remain 167 resolved /
37 missing / 0 ambiguous. Compile checks and `git diff --check` pass.
See the [Wave 16 evidence/results record](operating-income-derivation-policy-design.md#wave-16-implementation-and-verified-results).

Phase 1H.4 Wave 17 completes the
[CVX/GE business-perimeter research](operating-income-cvx-ge-perimeter.md)
for exactly ten frozen selected filings (five per issuer). All five CVX periods
are `BUSINESS_PERIMETER_UNRESOLVED`: mixed-tax equity-affiliate earnings and
incomplete Other/benefit allocations do not establish a complete consolidated
operating equation. All five GE periods are research-classified
`SPECIALIZED_METHODOLOGY_REQUIRED` for the mixed industrial/insurance
consolidated perimeter; the selected five-period series is also not comparable
on a common continuing-business basis after HealthCare/Vernova separations and
insurance-accounting changes. Segment profit is not a substitute.

The decision is NO-GO, with zero safe additional coverage. These research
classifications do not change production states or reclassify universe
execution: all ten remain missing, 43 generic issuers execute and seven are
skipped. Operating Income remains 194 resolved / 10 missing / 0 ambiguous;
aggregate states remain 1,880 / 1,508 / 11 / 27 / 42 across 3,468 states.
Only additional selected-filing notes were retrieved; no production code,
tests, policies, full test suite or corpus were changed or run.

Phase 1H.4 Wave 18 completes the
[D&A concept/component inventory](depreciation-amortization-concepts.md)
and its [machine-checkable evidence](depreciation-amortization-inventory.json)
for all 94 missing periods across 21 issuers. Every frozen CIK/accession/annual
period matches selected filing-XBRL and explicit annual DEI evidence. The
inventory retains 1,374 exact-period numeric occurrences, including dimensions,
units, raw representations, deterministic ordinals, presentation/calculation
relationships and selected statement/note sources. AVGO 2021's older DEI
namespace is reviewed separately without changing the production resolver.

Primary research categories reconcile to 31 `CONCEPT_POLICY`, 33 `DERIVATION`,
five `ISSUER_EXTENSION` and 25 `METHODOLOGY_BLOCKER` periods. PARTIAL GO is for
scope-evidence/policy design only: five Visa periods have supported potential
coverage; 89 remain unapproved. Cash-flow impairment/accretion, embedded lease
expense, incomplete amortization, financing/contract costs, source precision
and mixed-business scope prevent a generic fallback or automatic MSFT-style
sum. No production result changes: D&A stays 110 resolved / 94 missing / 0
ambiguous, Operating Income 194 / 10 / 0 and aggregate 1,880 / 1,508 / 11 / 27 /
42 across 3,468 states. No tests or corpus runs were performed.

Phase 1H.4 Wave 19 completes the
[D&A scope-evidence acceptance design](depreciation-amortization-scope-evidence-design.md).
PARTIAL GO approves a five-entry exact-accession Visa design, not a generic
combined-concept rule or production registration. Asset/finite-lived notes,
separate incentive/lease treatment and operating presentation establish scope;
2025's rounded property disclosure is corroboration, never a residual operand.
All 89 controls remain unapproved, not freshly reviewed denials. Immutable
versioning, direct precedence, exact semantic confirmation, structural-error
boundaries and complete occurrence/support serialization are specified.
Production counts remain unchanged; no tests or corpus reruns.

## Completed

- Completed Milestone 0 — development environment and repository setup
- Created GitHub repository
- Cloned repository locally
- Connected local repository to GitHub remote
- Configured Git identity
- Set up Python 3.12 virtual environment
- Configured VS Code to use the project virtual environment
- Created initial repository structure
- Created initial project documentation
- Added a reusable SEC JSON HTTP client with identifying User-Agent support
- Added exact ticker → SEC company identity resolution using the official SEC
  `company_tickers.json` dataset
- Added deterministic unit tests for SEC transport and ticker resolution
- Added typed recent-filing metadata retrieval from the official SEC
  Submissions API
- Added explicit validation for SEC parallel-array structure, required fields,
  and filing dates
- Added deterministic unit tests for submissions retrieval and parsing
- Added typed metadata for supplemental SEC submissions history files
- Added explicit, on-demand retrieval and shared parsing for individual
  supplemental history files
- Added deterministic unit tests for supplemental metadata and retrieval
- Added a pure, deterministic selector for exact 10-K annual periods and exact
  10-Q filings after the latest selected annual period
- Added incremental history orchestration that stops retrieving supplemental
  files as soon as the requested annual coverage is available
- Added explicit ambiguity handling for duplicate reporting periods
- Added deterministic unit tests for selection and orchestration
- Added complete Company Facts retrieval through the existing SEC client
- Added immutable models for concepts and unit-tagged fact observations
- Added explicit Company Facts validation while preserving optional context,
  observation ordering, and repeated comparative facts
- Added deterministic unit tests for Company Facts parsing and errors
- Added a development-only cross-company Company Facts validation harness that
  uses the production SEC APIs sequentially, reports per-stage failures without
  stopping the run, and defaults to a repeatable 20-company corpus
- Validated Company Facts across all 20 corpus companies: 11,181 concepts and
  528,990 observations parsed with no failures
- Added narrowly validated canonical decimal-string CIK support after XOM
  exposed that live SEC representation, with mismatch regression coverage
- Added pure Company Facts observation selection anchored to selected filing
  accessions, preserving annual/interim grouping and deterministic ordering
- Added structural current, comparative, and after-report-date relationships,
  plus instant/duration classification without YTD or discrete-quarter inference
- Added explicit exact-observation ambiguity handling while preserving
  same-end/different-start periods, multiple units, and legitimate absence
- Added compact selection output that retains only matched observations and
  Company Facts source metadata rather than the full parsed observation graph
- Added deterministic tests for calendar, non-calendar, 52/53-week, and interim
  period shapes, ambiguity, absence, provenance, ordering, and ownership
- Added a pure top-level normalization package with stable metric identities
  and ordered, metric-specific SEC concept policies
- Added immutable annual normalized, missing, and ambiguous result models with
  compact SEC provenance and no retained Company Facts graph
- Added annual Revenue normalization using an evidence-based
  `RevenueFromContractWithCustomerExcludingAssessedTax` → `Revenues` policy
- Added annual Operating Income normalization using `OperatingIncomeLoss`
- Preserved actual calendar, non-calendar, 52-week, and 53-week economic period
  dates without inferring fiscal boundaries
- Validated five annual periods each for META, GOOGL, MSFT, AAPL, and COST: all
  50 Revenue/Operating Income values resolved, with no ambiguity or face-
  statement mismatch
- Confirmed GOOGL Revenue fallback behavior and retained equal COST Revenue
  observations as confirming provenance
- Added direct annual Capex normalization using only
  `PaymentsToAcquirePropertyPlantAndEquipment`, preserving positive expenditure
  magnitudes and actual fiscal boundaries
- Validated 25 annual Capex periods across META, GOOGL, MSFT, AAPL, and COST
  alongside the existing 50 Revenue and Operating Income values
- Confirmed that direct DDA covers META, AAPL, and COST but not GOOGL or MSFT;
  a fallback is inappropriate, aggregation requires complete non-overlapping
  evidence, and some relevant issuer-extension facts are absent from Company
  Facts
- Added explicit on-demand discovery and retrieval of the SEC-generated
  extracted XBRL instance corresponding to a selected filing's primary document
- Added immutable filing-level context, dimension, unit, and fact models that
  preserve standard and issuer-extension concepts without financial selection
- Added structural parsing for duration, instant, comparative, explicit- and
  typed-dimensional contexts, simple and divided units, numeric, nil, and
  nonnumeric facts
- Kept filing-level XBRL separate from Company Facts selection and historical
  normalization; Revenue, Operating Income, and Capex behavior is unchanged
- Live-validated exact nondimensional issuer-extension facts from the selected
  GOOGL 2021 and MSFT 2022 extracted instances, including dates, USD units, and
  decimals
- Established an FCFF D&A definition that excludes impairment, stock
  compensation, restructuring, unspecified other noncash items, and unsupported
  lease adjustments from direct D&A
- Added direct annual D&A normalization using only
  `DepreciationDepletionAndAmortization` through the generic annual resolver
- Validated direct D&A for all five selected META, AAPL, and COST periods:
  15/25 direct coverage across the five-company corpus, with GOOGL and MSFT
  returning typed missing results as intended
- Added provenance-distinct derived historical values with ordered operands,
  source identity, and an explicit addition operation
- Added a Company Facts derivation policy scoped to Microsoft CIK `789019` for
  `Depreciation` plus `AmortizationOfIntangibleAssets`
- Preserved direct-first precedence and direct ambiguity while keeping derived
  coverage gaps typed rather than exceptional
- Validated all five selected MSFT periods as derived D&A, producing 20/25
  evidence-backed D&A periods across META, GOOGL, MSFT, AAPL, and COST; GOOGL
  remains unresolved
- Added direct annual Pretax Income normalization using only
  `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`
- Added direct annual Income Tax Expense normalization using only
  `IncomeTaxExpenseBenefit`, preserving reported expense and benefit signs
- Ordered normalized metrics as Revenue, Operating Income, Pretax Income,
  Income Tax Expense, D&A, and Capex
- Validated both tax-related metrics across five selected annual periods for
  META, GOOGL, MSFT, AAPL, and COST: 25/25 resolved for each, with no missing or
  ambiguous results and exact selected-filing face-statement agreement
- Added derived annual Reported Effective Tax Rate from the direct normalized
  Income Tax Expense and Pretax Income results
- Added 34-digit `Decimal` division, ordered normalized-metric provenance,
  explicit negative-denominator diagnostics, and typed zero-denominator results
- Preserved negative and above-100% rates without clamping and applied no
  arbitrary near-zero threshold
- Validated Reported ETR for all 25 selected periods with agreement to SEC's
  structured disclosed rate after normal presentation rounding
- Added a separate annual instant balance-sheet normalization path with typed
  resolved, missing, and ambiguous results and compact Company Facts provenance
- Added primitive policies for Operating Receivables, Inventory, Trade Accounts
  Payable, and Customer Contract Liabilities, including only the evidence-backed
  CIK-scoped COST and META alternatives
- Validated 25 selected annual periods across META, GOOGL, MSFT, AAPL, and COST:
  Operating Receivables 25/25, Inventory 17/25, Trade Accounts Payable 25/25,
  and Customer Contract Liabilities 24/25, with nine explicit missing results
  and no ambiguity
- Preserved META inventory as missing in all five periods, GOOGL inventory as
  missing for 2023-2025, and META 2025 customer liabilities as missing rather
  than substituting unsupported concepts or zero
- Added Apple CIK-scoped Vendor Non-Trade Receivables from
  `NontradeReceivablesCurrent` and validated 5/25 overall: all 5/5 applicable
  Apple periods resolved and 20 non-applicable periods remained typed missing
- Added `EmployeeRelatedLiabilitiesCurrent` only for META, GOOGL, MSFT, and
  COST, validating 20/25 overall: all 20/20 applicable periods resolved and all
  five Apple periods remained typed missing
- Added Costco CIK-scoped Member Rewards Liability from
  `AccruedLiabilitiesCurrent` and validated 5/25 overall: all 5/5 applicable
  Costco periods resolved and 20 non-applicable periods remained typed missing,
  without generalizing that broad concept to other issuers
- No new primitive result was ambiguous
- At the primitive-normalization milestone, kept filing-level XBRL explicit/on
  demand and deferred broad current residuals, Operating NWC, and its change
- Added an explicit Company Facts versus filing-XBRL source distinction to
  annual balance-sheet policies while keeping normalization network-free
- Added GOOGL CIK `1652044` Accrued Revenue-Share Liability from exact
  `AccruedRevenueShare` filing-XBRL facts under the Google issuer namespace whose
  date exactly matches the selected 10-K report date
- Preserved filing-level namespace, source URL, context, dimensions, decimals,
  nil state, raw value, parsed value, accession, and filing metadata in compact
  normalized provenance; multiple eligible facts remain ambiguous
- Live-validated all five selected GOOGL accessions at $8.996bn, $8.370bn,
  $8.876bn, $9.802bn, and $10.864bn for 2021–2025, with no missing or ambiguous
  results
- Added GOOGL CIK `1652044` Accrued Customer Liabilities from exact
  `AccruedCustomerLiabilitiesCurrent` selected-filing XBRL facts, distinct from
  customer contract liabilities and accrued revenue share
- Live-validated all five original selected GOOGL accessions at $3.505bn,
  $3.619bn, $4.140bn, $4.304bn, and $5.029bn for 2021–2025, with no missing or
  ambiguous results
- Made accrued customer liabilities a required GOOGL operating-liability
  component while preserving unresolved trade-payables and residual-liability
  blockers, so GOOGL remains incomplete
- Added a pure META CIK `1326801` derivation that subtracts PP&E included in
  trade accounts payable using reported trade AP, combined unpaid PP&E, and
  separately accrued PP&E evidence
- Preserved duration-shaped `CapitalExpendituresIncurredButNotYetPaid` Company
  Facts observations as special selected-accession/full-fiscal-year derivation
  operands rather than direct instant balance-sheet values; eligibility is
  evaluated only among target-concept observations, with multiple eligible
  target periods unresolved and unrelated duration facts ignored
- Used explicit filing XBRL for report-date-specific Facebook namespace
  `PropertyAndEquipmentAccruedLiabilitiesCurrent`; normalization performs no
  retrieval
- Live-validated adjusted META trade AP for 2021–2025 at $2.071bn, $4.592bn,
  $2.957bn, $3.142bn, and $3.965bn, with all five periods resolved and complete
  three-fact/two-step provenance
- Made derived adjusted trade AP the required META operating-liability evidence
  without counting either PP&E operand separately; other accrued liabilities
  remain unresolved, so META remains incomplete
- Kept Apple accrued distribution and marketing unresolved at 1/5 exact
  selected-accession coverage and excluded broad residual liability captions
- Added immutable Operating NWC component classifications distinct from
  normalized financial metric identities
- Added CIK-specific META, GOOGL, MSFT, AAPL, and COST policies for required
  operating assets and liabilities, exclusions, non-applicable components, and
  methodology-unresolved balances
- Added pure annual completeness evaluation that preserves resolved, missing,
  and ambiguous normalized evidence without calculating an Operating NWC value
- Preserved explicit SEC zero as resolved while keeping missing evidence,
  issuer non-applicability, and methodology uncertainty as distinct states
- Explicitly deferred and excluded operating-lease current liabilities under
  the initial methodology; no lease arithmetic or capitalization was added
- Confirmed all five issuer policies remain incomplete because material
  component-classification or evidence blockers remain
- Preserved strict reconstruction completeness as an audit diagnostic without
  weakening its missing, ambiguous, unresolved, excluded, or not-applicable
  classifications
- Added immutable versioned issuer-specific valuation perimeters and a separate
  pure readiness evaluator that preserves direct, derived, missing, and
  ambiguous evidence without calculating Operating NWC
- Made COST ready for all five selected annual periods and META ready for
  2021–2024; META 2025 remains not ready because required customer contract
  liabilities are typed missing
- Kept GOOGL not ready for its trade-AP and inventory methodology decisions,
  MSFT not ready for trade AP, and AAPL not ready for employee and distribution-
  and-marketing liability decisions
- Kept broad mixed residual captions visible as reconstruction limitations but
  outside the initial valuation perimeters; omitted balances and movements are
  not treated as zero and will remain absent from future arithmetic
- Defined perimeter version changes around economic component or mandatory-
  treatment changes rather than incidental code changes
- Confirmed the selected META 2025 filing reports $1.080bn of total deferred
  revenue but does not quantify an exact current-only amount; neither the total
  balance nor qualitative timing disclosure is used as a substitute
- Added META valuation policy v2 with operating receivables, adjusted trade AP,
  and employee-related liabilities as required components
- Kept customer contract liabilities normalized and visible but outside the
  META v2 valuation perimeter for every period; excluded balances and movements
  are omitted rather than treated as zero or economically irrelevant
- Made META v2 the sole active default while retaining META v1 through explicit
  policy ID/version lookup and rejecting duplicate historical identities
- Confirmed META v2 removes customer contract liabilities as a readiness blocker
  while strict reconstruction remains incomplete; every remaining required
  normalized component must still resolve for a period to calculate
- Preserved COST v1 readiness and the existing GOOGL, MSFT, and AAPL blockers
- Added pure annual Operating NWC level calculation as required operating assets
  minus required operating liabilities for valuation-ready periods only
- Added ordered `Decimal` component contributions that preserve positive source
  balances, apply asset/liability signs separately, and retain complete direct
  or derived normalized provenance
- Kept missing, ambiguous, and methodology-blocked periods nonnumeric; no
  partial result or zero substitution is produced
- Corrected META's special combined unpaid-PP&E eligibility to consider only
  observations of the configured target concept; unrelated duration facts no
  longer create false period ambiguity, while competing target facts remain
  deterministically ambiguous
- Live-validated META v2 and COST v1 levels for all five selected periods, with
  exact agreement between every result and its signed component contributions;
  META 2021–2025 is $8.816bn, $4.283bn, $6.553bn, $7.502bn, and $8.653bn
- Kept GOOGL, MSFT, and AAPL blocked
- Preserved exact policy ID/version selection and kept out-of-perimeter evidence
  outside arithmetic without treating it as economically zero
- Added immutable annual ΔNWC results calculated as closing O-NWC minus opening
  O-NWC using exact `Decimal` arithmetic without rounding
- Required the same company CIK, exact policy ID/version, calculation formula,
  and actual ordered component/side/normalized-metric perimeter so explicit
  policy-definition changes cannot become economic working-capital movements
- Preserved actual opening and closing fiscal dates and both complete calculated
  O-NWC levels with their component-level SEC provenance
- Added ordered adjacent-series calculation: five compatible annual levels
  produce four changes, while reversed dates or an intervening policy change
  fail explicitly rather than being sorted or skipped
- Live-validated META v2 annual ΔNWC at -$4.533bn, $2.270bn, $0.949bn, and
  $1.151bn and COST v1 at $1.897bn, -$1.146bn, -$0.471bn, and -$1.417bn for
  their four respective 2022–2025 fiscal periods
- Added immutable caller-driven tax reconciliation evidence and bridge models
  that preserve explicit filing-displayed signs separately from raw XBRL values
- Supported both percentage-point rate bridges and reported dollar bridges,
  exact Decimal rate dollarization, disclosed-precision validation, row order,
  and typed evidence problems without synthetic residual rows
- Kept diagnostic income-base, pairing, and proposed-treatment classifications
  separate from operating-tax policy; operating tax, NOPAT, and forecast tax
  assumptions remain unimplemented
- Added immutable operating-tax readiness policies, guarded bridge-row
  decisions, explicit evidence requirements, and exclusive paired-row
  membership without a generalized rule engine
- Added company, selected-filing, accession, report-date, economic-period,
  monetary-scale, statutory-anchor, and exact policy-version integrity checks
- Added typed ready, missing, ambiguous, unsupported, policy-mismatch,
  unreconciled, methodology-blocked, and loss-policy-blocked outcomes
- Proved readiness with a fully evidenced synthetic case. Completed methodology
  review leaves all 25 real validation periods blocked by unresolved
  foreign/state allocation, combined or embedded SBC, Other-row, and
  operating-income linkage decisions. Representative blocker regressions are
  automated; the repository does not persist and replay all 25 full bridges.
- Conservatively blocked zero/negative Operating Income, negative Pretax Income,
  and unresolved benefit realizability; explicit zero adjustments remain valid
- Completed the 25-period first-ready screening and jurisdictional-attribution
  methodology review without introducing a materiality waiver or forcing a real
  issuer period ready
- Adopted strict direct linkage for historical operating tax: complete state,
  foreign, jurisdictional, and other reconciliation effects require explicit
  reported-Operating-Income linkage or an exact reproducible operating
  allocation; paired gross-tax and credit effects also require complete common-
  base evidence
- Rejected caption recurrence, state/foreign labels, net presentation, absence
  of disclosed contamination, proportional Operating Income/Pretax Income
  allocation, unsupported geographic or revenue allocation, and direct
  application of reconciliation percentages to Operating Income
- Made historical operating tax and historical NOPAT optional analytical
  outputs while preserving reported tax expense, Reported ETR, signed bridge
  evidence, and typed readiness; a manual forecast tax-rate assumption keeps
  unresolved historical tax outside the DCF critical path
- Added annual Cash and Cash Equivalents from exact selected-filing
  `CashAndCashEquivalentsAtCarryingValue` observations for the five validation
  issuers
- Added CIK-scoped annual Short-Term Investments policies for META, GOOGL,
  MSFT, AAPL, and COST, including the narrow META 2021 available-for-sale debt
  fallback
- Added Apple-only annual Long-Term Marketable Securities without treating
  other issuers' strategic, non-marketable, or mixed investment captions as
  equivalents
- Preserved gross reported balances without subtracting restrictions or
  deriving unrestricted, excess, or total liquid cash
- Validated 25/25 cash values, 25/25 short-term investment values, and 5/5
  applicable Apple long-term marketable-security values with no missing or
  ambiguous results
- Added annual Commercial Paper using `CommercialPaper` for GOOGL, MSFT, and
  AAPL, with 12 direct, 13 missing, and no ambiguous values across 25 periods
- Added COST-only annual Short-Term Borrowings using
  `OtherShortTermBorrowings`, resolving the evidenced 2022 balance while the
  other 24 periods remain typed missing rather than inferred zero
- Added direct annual Current Portion of Long-Term Debt using
  `LongTermDebtCurrent` and Non-Current Long-Term Debt using
  `LongTermDebtNoncurrent`
- Added accession-scoped GOOGL 2021–2023 carrying-debt derivations that remove
  finance-lease liabilities from combined debt-and-lease facts and retain all
  Company Facts operands and arithmetic steps
- Validated Current Portion of Long-Term Debt as 19 direct, 1 derived, and 5
  missing; validated Non-Current Long-Term Debt as 21 direct, 3 derived, and 1
  missing, with no ambiguity or value mismatch across the 25-period corpus
- Kept commercial paper and short-term borrowings separate and prohibited
  total debt, net debt, lease debt, maturity-principal, and fair-value
  substitutions
- Added annual Diluted Weighted-Average Shares from only
  `WeightedAverageNumberOfDilutedSharesOutstanding`, requiring the selected
  10-K's current duration, unit `shares`, integer non-Boolean input, and exact
  `Decimal` output
- Added a GOOGL CIK- and accession-scoped filing-XBRL derivation for selected
  2021–2023 filings that adds the Class A denominator, which includes Class B
  conversion, to the separate Class C denominator while retaining full
  dimensional provenance
- Validated 22 direct and three derived diluted-share periods with no missing,
  ambiguity, or value mismatch; preserved GOOGL 2021 at 677,674,000 on the
  original pre-split filing basis
- Kept basic shares, period-end shares, split-restated series, current fully
  diluted shares, forecast dilution, and future valuation-share policy outside
  this milestone
- Added an immutable period-centric standardized company history with selected
  filing references, actual fiscal durations, closing balance dates, and
  deterministic top-level measure ordering
- Added pure assembly and explicit serialization that preserve direct, derived,
  calculated, missing, ambiguous, not-comparable, and methodology-blocked
  outcomes; exact Decimal values serialize as strings
- Aligned duration and instant results by company, accession, filing identity,
  and report date, rejecting conflicting fiscal starts, duplicate periods,
  unit mismatches, binary floats, and later-filing evidence
- Exposed existing Operating NWC levels and changes without repeating their
  arithmetic, retaining policy ID/version and component-level SEC references
- Live-assembled five annual records for META, GOOGL, MSFT, AAPL, and COST;
  standardized values matched their immediate normalized inputs while
  preserving GOOGL blockers and derived shares, MSFT June periods, Apple
  long-term securities, and COST's 53-week year
- Kept cash, investment, and debt primitives separate and left historical
  NOPAT, forecast assumptions, FCFF, equity bridges, valuation shares, and DCF
  outside the standardized historical boundary
- Added a separate `valuation` package with immutable five-year manual
  assumption models bound to company CIK, latest historical accession, and
  fiscal-end date without retaining normalization or SEC objects
- Required ordered forecast indices 1–5 and descriptive labels without
  synthesizing future dates or assuming calendar fiscal years
- Added strict finite-Decimal fraction validation for per-year revenue growth,
  operating margin, forecast tax rate, D&A/revenue, Capex/revenue, and
  ΔNWC/revenue, plus one manual WACC and terminal-growth rate
- Chose direct ΔNWC as a percentage of revenue so unresolved historical O-NWC
  does not block manual forward assumptions; no forecast O-NWC level is added
- Added deterministic explicit serialization with Decimal strings and preserved
  the boundary around manual forecast tax, unresolved loss-period tax policy,
  valuation shares, and the enterprise-to-equity bridge
- Kept all forecast calculations, NOPAT, FCFF, discounting, terminal value, DCF,
  scenarios, sensitivity analysis, and reverse DCF unimplemented
- Froze the dated and sourced 2026-10-02 S&P 500 Top 50 universe as 51
  securities representing 50 SEC issuers, preserving both Alphabet share
  classes and the explicit Invesco `BRK/B` to SEC/project `BRK-B` ticker mapping
- Reconciled all five validated issuers to the snapshot and live-prechecked all
  51 canonical project tickers through the existing SEC resolver with no
  unresolved tickers
- Classified 38 securities as operating-company candidates and seven issuers
  as specialized-methodology candidates without assigning
  `GENERALIZATION_REQUIRED` before pipeline evidence exists
- Added a deterministic development corpus runner that validates and consumes
  the frozen snapshot, groups its 51 securities into 50 CIK-based issuer
  records, uses GOOGL as Alphabet's single execution ticker, and retains GOOG
  as a separate reporting row
- Added explicit ticker-resolution, submissions, filing-selection, Company
  Facts, filing-association, normalization, standardized-output, complete, and
  specialized-skip stages with issuer-boundary exception capture
- Added an ephemeral JSON result containing snapshot and commit identity,
  selected annual dates, per-stage status, typed availability counts, and
  per-measure direct/derived/calculated summaries
- Live-attempted all 43 generic issuers: 41 reached standardized output, GEV
  and SNDK failed at Company Facts parsing, and all seven specialized issuers
  were preserved as explicit skips
- Recorded 1,636 resolved, 1,673 missing, 24 ambiguous, 27
  methodology-blocked, 40 not-comparable, and no unsupported, not-applicable,
  or out-of-perimeter standardized measures across completed issuers
- Preserved all five seed regressions and their 25 annual periods, including
  GOOGL missing D&A, three derived GOOGL diluted-share periods,
  GOOGL/MSFT/AAPL blocked O-NWC, and each seed's first non-comparable ΔNWC
- Recorded XOM as completing the pipeline with zero selected annual periods;
  no later comparative filing, zero, alias, or policy change was introduced
- Classified all Phase 1H.2 results into an operational root-cause taxonomy,
  reconciled the 17-measure coverage matrix, and preserved the complete
  ambiguity and methodology-blocker inventories
- Established that GEV and SNDK share a strict Company Facts representation
  issue, while XOM requires official-evidence registrant-succession handling
  rather than a filing-selector relaxation or ticker hardcode
- Assigned all 50 issuers a post-smoke planning status: two `SUPPORTED`, 41
  `GENERALIZATION_REQUIRED`, and seven
  `SPECIALIZED_METHODOLOGY_REQUIRED`
- Generalized Company Facts CIK parsing to accept the exact SEC ten-digit
  padded representation only when it matches `company.cik_padded`, with no
  GEV/SNDK-specific branch and with canonical/mismatch protections preserved
- Live-reran GEV and SNDK through complete standardized output with two annual
  periods each, then completed all 43 generic corpus attempts with no failures;
  the five seed histories and typed states remained unchanged
- Completed the registrant-succession identity-linkage design with exact
  terminology, official SEC evidence hierarchy, deterministic acceptance and
  rejection gates, bounded chain semantics, provenance, Company Facts and
  filing-selection interactions, and adversarial cases
- Recorded a NO-GO decision for automated linkage because public structured SEC
  sources do not encode the directed predecessor/successor CIK edge; retained
  XOM as unresolved rather than adding a ticker, name, or issuer hardcode
- Generalized the exact standard cash Company Facts policy beyond the seed CIKs,
  resolving 160 additional issuer-periods without accepting broader
  restricted-cash or combined cash-and-investment captions

## Next Step

Implement Wave 19's five-entry curated D&A scope-equivalence foundation with
exact identity/evidence validation, direct-first selection and full confirming
occurrence/support provenance. Regress five accepted candidates and all 89
no-entry controls; validate targeted results before full tests/corpus. No
generic combined-concept fallback or lease adjustment. Component completeness
research for the 33 derivation and five AMD extension periods remains separate;
do not generalize MSFT's two operands or approve a generic cash-flow fallback.
Wave 17 leaves the ten CVX/GE Operating Income gaps unresolved; dedicated CVX
energy/affiliate and GE industrial/insurance carve-out or common-perimeter
recast research are separate, unapproved methodology paths. Preserve the
completed 25-entry Operating Income policy and all typed missing controls. The
Phase 2A assumptions model is implemented, but
forecast, FCFF, DCF, equity-bridge, per-share, reverse-DCF, scenario, and
sensitivity work is intentionally paused through Phase 1H.

## Phase 1H Roadmap

1. **Phase 1H.1 — Universe definition (complete):** froze the dated and sourced
   2026-10-02 S&P 500 Top 50 list, existing coverage, and preliminary
   specialized-methodology flags.
2. **Phase 1H.2 — Automated corpus smoke test (complete):** ran the existing
   historical pipeline across all 43 generic issuers and preserved structured
   typed results, stage failures, and seven specialized skips.
3. **Phase 1H.3 — Failure taxonomy (complete):** classified retrieval,
   identity, filing-selection, schema, concept-policy, issuer-extension,
   dimensional, derivation, period-association, methodology, and specialized
   business-model issues and ranked the reusable backlog.
4. **Phase 1H.4 — Generalization waves (in progress):** Wave 1A fixed exact
   padded Company Facts CIK handling. Wave 1B completed the
   registrant-succession design and reached NO-GO for automated linkage, leaving
   XOM unresolved. Wave 2 generalized the exact standard cash policy, resolving
   160 additional periods while leaving 19 broader-caption cases missing. Wave
   3 rejected annual-looking heuristic evidence. Wave 4 found a standards-backed
   authority in the filing-XBRL DEI required context and documented a GO design.
   Wave 5 implemented and validated the pure resolver. Wave 6 integrates it for
   Revenue, Pretax Income, and Income Tax Expense, resolving all known annual/Q4
   collisions while retaining 11 same-period economic Revenue conflicts. Wave
   7 reaches PARTIAL GO for further research/design only: a 33-period standard
   Pretax variant remains unapproved because its equity-method scope differs.
   Wave 8 defines a read-only presentation-evidence diagnostic without changing
   production policy. Wave 9 implements it and validates all 33 periods as
   multiple-role members with statement membership established but equity-
   method scope still unapproved. Wave 10 completes exact-period note research:
   eight periods are included in Pretax, 20 are separate net of tax, and five have
   mixed treatment and remain unresolved. No machine-checkable equivalence rule
   or production resolution is established. Wave 11 rejects an automated rule
   but approves the design boundary for a curated, versioned exact-accession
   registry with mandatory provenance and conservative defaults. Wave 12
   implements that boundary for only the eight reviewed MA/CVX facts, preserves
   all confirming occurrences through Reported ETR and serialization, and
   leaves all 25 controls and 12 issuer-extension periods unresolved. Wave 13
   finds no consolidated face-statement Operating Income subtotal in any of 35
   missing periods and rejects direct policy expansion; two GE periods contain
   only dimensioned segment/reconciliation facts. Wave 14 approves exact
   component-derivation evidence for all 25 LLY/JNJ/MRK/KLAC/IBM periods. Wave
   15 freezes the immutable exact-accession policy/model, arithmetic, evidence,
   provenance, serialization, Operating Tax, and regression design while
   keeping CVX and GE as negative controls. Wave 16 implements and validates
   all 25 exact derivations, retaining all 169 direct results and reducing
   Operating Income gaps to the ten CVX/GE controls. Wave 17 completes their
   business/perimeter research with NO-GO and zero additional coverage: CVX
   remains unresolved, GE requires specialized mixed-business treatment and
   has no common five-period continuing perimeter. Wave 18 inventories all
   94 D&A gaps across 21 issuers and reaches PARTIAL GO for scoped evidence
   design with five Visa candidates, not production expansion. Wave 19 freezes
   their curated scope-equivalence acceptance design; next implement only those
   five entries with 89 unapproved controls, then continue with other
   extension patterns, dimensions,
   non-calendar periods, acquisition
   accounting, debt/lease presentation, D&A decomposition, and working-capital
   perimeters.
5. **Phase 1H.5 — S&P 500 Top 50 validation pass:** assign every constituent
   `SUPPORTED`, `GENERALIZATION_REQUIRED`, or
   `SPECIALIZED_METHODOLOGY_REQUIRED` and document unresolved typed states.
6. **Phase 1H.6 — Freeze historical normalization v1:** record supported scope
   and exclusions, then resume Phase 2 forecast and DCF development.

The near-term target is S&P 500 Top 50 validation, the medium-term goal is broader
S&P 500 coverage, and specialized financial methodologies remain separate
long-term work. The repository does not currently claim S&P 500 Top 50 or
broader S&P 500 support.

## Current Repository Structure

```text
valuation-platform/
├── AGENTS.md
├── README.md
├── docs/
│   ├── architecture.md
│   ├── financial-methodology.md
│   ├── project-status.md
│   ├── sec-identity-linkage.md
│   └── universe/
│       ├── sp500-top-50-2026-10-02.csv
│       └── sp500-top-50-2026-10-02.md
├── scripts/
│   └── validate_company_facts.py
├── src/
│   └── valuation_platform/
│       ├── __init__.py
│       ├── normalization/
│       │   ├── __init__.py
│       │   ├── balance_sheet.py
│       │   ├── concepts.py
│       │   ├── derived.py
│       │   ├── diluted_shares.py
│       │   ├── historical.py
│       │   ├── models.py
│       │   ├── output.py
│       │   ├── operating_nwc.py
│       │   └── pretax_scope.py
│       ├── valuation/
│       │   ├── __init__.py
│       │   └── assumptions.py
│       └── sec/
│           ├── __init__.py
│           ├── client.py
│           ├── company_facts.py
│           ├── fact_selection.py
│           ├── filing_selection.py
│           ├── filing_xbrl.py
│           ├── submissions.py
│           └── tickers.py
├── tests/
│   ├── __init__.py
│   ├── test_validate_company_facts.py
│   ├── normalization/
│   │   ├── __init__.py
│   │   ├── test_balance_sheet.py
│   │   ├── test_diluted_shares.py
│   │   ├── test_historical.py
│   │   ├── test_output.py
│   │   ├── test_operating_nwc.py
│   │   └── test_pretax_scope.py
│   ├── valuation/
│   │   ├── __init__.py
│   │   └── test_assumptions.py
│   └── sec/
│       ├── __init__.py
│       ├── test_client.py
│       ├── test_company_facts.py
│       ├── test_fact_selection.py
│       ├── test_filing_selection.py
│       ├── test_filing_xbrl.py
│       ├── test_submissions.py
│       └── test_tickers.py
├── .gitignore
└── requirements.txt
```
