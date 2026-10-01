# Project Status

## Current Milestone

Phase 1F.5d is complete for explicit filing-XBRL-backed annual balance-sheet
normalization and GOOGL accrued revenue share. Operating NWC and change in
Operating NWC remain future work.

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
- Kept filing-level XBRL explicit/on demand and left broad current residuals,
  Operating NWC, and change in Operating NWC unimplemented
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
- Kept Apple accrued distribution and marketing unresolved at 1/5 exact
  selected-accession coverage and excluded broad residual liability captions

## Next Step

Resolve the remaining material Operating NWC component-classification gaps
without broad residual formulas. Apple distribution and marketing remains
unresolved, and broad residual accounts, tax and lease balances, the opening
snapshot needed for a five-period change series, and change in Operating NWC
remain outside the implemented scope. GOOGL D&A, NOPAT, interim normalization,
and valuation also remain outside the current scope.

## Current Repository Structure

```text
valuation-platform/
├── AGENTS.md
├── README.md
├── docs/
│   ├── architecture.md
│   ├── financial-methodology.md
│   └── project-status.md
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
│       │   ├── historical.py
│       │   └── models.py
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
│   │   └── test_historical.py
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
