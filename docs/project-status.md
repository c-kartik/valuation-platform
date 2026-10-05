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

The current validated standardized-output corpus is five companies—META,
GOOGL, MSFT, AAPL, and COST—and 25 annual periods, consisting of five selected
10-K periods per company. Validation means the production historical pipeline
was run and checked against expected filing evidence, not that every metric
resolved. GOOGL D&A remains typed missing, GOOGL/MSFT/AAPL Operating NWC remains
methodology-blocked, and missing debt primitives remain missing rather than
being inferred as zero.

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

## Next Step

Phase 1H.4 will execute the ranked generalization waves recorded in
`docs/universe/sp500-top-50-failure-taxonomy.md`: resolve shared schema and
identity blockers first, then high-frequency low-risk standard facts, core
FCFF flows, equity-bridge balances, and narrower filing-evidence or O-NWC
policies. The Phase 2A assumptions model is implemented, but forecast, FCFF,
DCF, equity-bridge, per-share, reverse-DCF, scenario, and sensitivity work is
intentionally paused through Phase 1H.

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
4. **Phase 1H.4 — Generalization waves:** address high-frequency reusable gaps
   first, including concept variants, extension patterns, dimensions,
   non-calendar periods, acquisition accounting, debt/lease presentation, D&A
   decomposition, and working-capital perimeters.
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
│       │   └── operating_nwc.py
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
│   │   └── test_operating_nwc.py
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
