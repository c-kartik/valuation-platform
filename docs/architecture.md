# Architecture

## Overview

The Automated Equity Valuation Platform will be built incrementally, beginning with a Python financial data and valuation core before adding a web application.

The system should maintain clear boundaries between data retrieval, financial normalization, derived calculations, and valuation logic.

## Initial Architecture

```text
Ticker
  ↓
SEC Data Retrieval
  ↓
Raw SEC/XBRL Data
  ↓
Period Selection
  ↓
Financial Normalization
  ↓
Standardized Historical Financials
  ↓
Derived Financial Metrics
  ↓
Valuation Engine
  ↓
Valuation Outputs
```

## Phase 1 SEC Boundary

The SEC package separates transport from dataset interpretation:

- `sec.client` handles GET transport, identifying headers, timeouts, HTTP errors,
  raw response retrieval, and JSON decoding.
- `sec.tickers` interprets the official SEC `company_tickers.json` dataset and
  returns a typed company identity with source metadata.
- `sec.submissions` interprets recent filing metadata from the main SEC
  submissions response while preserving each parallel-array row. It also
  exposes supplemental history-file metadata and retrieves an individual
  supplemental file only when explicitly requested.
- `sec.filing_selection` keeps deterministic filing selection separate from
  history orchestration. The selector is network-free; the orchestrator fetches
  supplemental files in SEC order only until enough annual history is present.
- `sec.company_facts` retrieves and validates every taxonomy, concept, unit, and
  observation in the SEC Company Facts response without choosing financial
  concepts or authoritative reporting periods.
- `sec.filing_xbrl` discovers the SEC-generated extracted XBRL instance that
  corresponds to a selected filing's primary document, retrieves it explicitly
  on demand, and structurally preserves standard and issuer-extension facts,
  contexts, units, and dimensions.
- `sec.fact_selection` is a pure, network-free layer that associates Company
  Facts observations with selected filings by accession number. It preserves
  only the matched observations and compact source metadata.

```text
SEC retrieval and submissions parsing
  ↓
Incremental history orchestration
  ↓
Pure filing selection
  ↓
Company Facts retrieval
  ↓
Fact observation and structural period selection
  ↓
Annual financial normalization
  ↓
Later derived financial calculations
```

Selection currently uses exact 10-K and 10-Q forms and reporting dates. It does
not classify fiscal quarters, apply amendment precedence, infer Q4, inspect
financial facts, or perform financial normalization. Supplemental history files
are never downloaded after the requested annual coverage has been satisfied.

Company Facts observations preserve SEC ordering within each unit bucket,
source accession and filing metadata, optional period context, and their
JSON-decoded scalar values. Repeated and comparative observations remain intact
for later selection; retrieval does not decide which concept or observation is
authoritative.

Company Facts remains the primary standardized source. Filing-level extracted
XBRL is a targeted fallback source when filing evidence needed for later
methodology is absent from Company Facts. Retrieval is never automatic, and the
filing-level output is not yet connected to fact selection or normalization.
The parser consumes the SEC-generated XML instance rather than implementing an
Inline XBRL processor or resolving schemas and linkbases.

Fact selection classifies an observation as current, comparative, or after the
report date by comparing its end date with the selected filing's report date.
It classifies `start=None` as instant and a dated start as duration. Same-end,
different-start observations and observations in multiple units remain
distinct. Exact duplicates of accession, taxonomy, concept, unit, start, and
end fail explicitly.

The selector does not label durations as annual, YTD, discrete quarter, or Q4,
and it does not infer missing periods. Its compact output references selected
filings and matched immutable observations without retaining the complete
`SECCompanyFacts` observation graph.

## Financial Normalization Boundary

The top-level `normalization` package remains separate from SEC retrieval and
structural fact selection:

- `normalization.concepts` defines stable financial metric identities and
  ordered, metric-specific SEC concept candidates.
- `normalization.models` defines immutable direct, derived, missing, and
  ambiguous results with compact operand-level SEC provenance.
- `normalization.historical` resolves direct observations first and orchestrates
  an approved derivation only when the direct result is missing.
- `normalization.balance_sheet` separately resolves annual instant evidence
  from explicit Company Facts or filing-XBRL policies into primitive
  balance-sheet snapshots; parsed filing artifacts are supplied by the caller,
  so it performs no retrieval or derived Operating NWC calculation.
- `normalization.operating_nwc` preserves strict issuer-specific reconstruction
  diagnostics and separately evaluates versioned valuation perimeters for
  calculation readiness. It calculates annual O-NWC levels only after readiness
  succeeds, then derives adjacent annual changes only from levels with the same
  company, exact policy ID/version and formula, and actual ordered calculation
  perimeter. Level and change results retain their
  complete source results. The module remains pure and network-free.
- `normalization.derived` validates evidence-backed, CIK-scoped derivation
  policies and their operands. It performs no network access.
- `normalization.balance_sheet_derivation` resolves the narrowly approved META
  trade-payables adjustment from already selected Company Facts and explicitly
  supplied filing-XBRL evidence. It performs no retrieval or O-NWC arithmetic.
- `normalization.tax_evidence` normalizes caller-supplied, explicitly signed tax
  reconciliation rows and validates rate or dollar bridge arithmetic. It keeps
  raw XBRL values separate from filing-displayed signs and retains unresolved
  evidence states. It has no retrieval, sign-scraping, operating-tax policy, or
  NOPAT behavior.

Annual normalization currently supports direct Revenue, Operating Income,
Pretax Income, Income Tax Expense, D&A, and Capex values, plus derived Reported
Effective Tax Rate. Results use the deterministic order Revenue, Operating
Income, Pretax Income, Income Tax Expense, Reported Effective Tax Rate, D&A,
then Capex. A direct candidate must be a numeric, exact-USD, current
duration ending on the selected 10-K report date. Actual observation start and
end dates define the economic period, including non-calendar and 52/53-week
fiscal years.
D&A and Capex use the same generic direct-resolution path. A direct D&A result
takes precedence. When direct D&A is missing, an approved policy may produce a
provenance-distinct derived value; direct ambiguity is never replaced by a
derivation. The initial derived policy applies only to Microsoft CIK `789019`
and adds same-period Company Facts observations for `Depreciation` and
`AmortizationOfIntangibleAssets`. Filing-level XBRL is not automatically
connected to normalization. Capex remains a positive expenditure magnitude for
later subtraction in FCFF.

Concept priority applies only after period validation. Equal lower-priority
facts for the same unit and period remain as confirming provenance. Conflicting
values and multiple valid USD periods return explicit ambiguity results.
Structurally valid non-USD observations are unsupported and do not participate
in period, priority, confirmation, or conflict resolution. Expected coverage
gaps return explicit missing results.

Derived values preserve the operation and every ordered operand, including its
source kind, source URL, taxonomy, concept, value, unit, period, and selected
accession. The derived layer supports approved addition and division policies;
it does not provide a general expression engine, issuer-extension arithmetic,
impairment or lease adjustments, or interim derivation. MSFT D&A retains its
existing fact operands. Reported ETR uses a
minimal normalized-metric operand model so it can preserve both authoritative
direct inputs without repeating Company Facts concept selection.

Reported ETR divides normalized Income Tax Expense by normalized Pretax Income
using a 34-digit local `Decimal` context and a dimensionless `pure` unit. Its
operands must be direct, USD, accession- and period-compatible results. Operand
source URLs remain independent. A negative denominator produces a valid ratio
with an explicit diagnostic; a zero denominator produces a typed missing
result. No near-zero threshold or presentation rounding is applied.

The normalization package does not infer interim period semantics, derive
quarters, aggregate financial concepts, determine forecast operating tax
assumptions, or calculate valuation inputs. Those remain separate later
responsibilities.

Tax evidence accepts explicit sign authority from the original filing table or
a reliable calculation relationship. Percentage-point rows retain their
displayed rate and pretax denominator alongside the unrounded Decimal tax
amount derived from them. Dollar rows retain their reported currency amount.
Bridge validation reports exact, disclosed-rounding, unreconciled, or incomplete
evidence status. Rounding tolerance conservatively counts the starting value,
each displayed row, and reported total at the declared precision; it never
creates a balancing row. Normalized rows validate their own source identity and
rate/dollar arithmetic. Calculation-relationship sign authority requires an
auditable rationale. Diagnostic income-base, pairing, and treatment
classifications do not drive an adjusted-tax result.

Annual balance-sheet normalization requires an exact selected 10-K accession,
a current instant observation with no start date, an end equal to the filing
report date, exact USD, and a numeric non-Boolean value. It preserves the actual
balance date and source-specific compact provenance. Company Facts is the
default source. A policy may instead explicitly require filing XBRL; the caller
retrieves selected-filing artifacts and supplies them to the network-free
normalizer. There is no automatic fallback or bulk retrieval. Zero is valid;
absence stays typed missing. Conflicting eligible observations stay ambiguous.

The deterministic order is Operating Receivables, Vendor Non-Trade
Receivables, Inventory, Trade Accounts Payable, Customer Contract Liabilities,
Employee-Related Liabilities, Accrued Revenue-Share Liability, Accrued Customer
Liabilities, then Member Rewards Liability. Evidence-backed
issuer-scoped policies support COST `ReceivablesNetCurrent`, META
`AccountsPayableTradeCurrent`, COST `DeferredRevenueCurrent`, Apple
`NontradeReceivablesCurrent`, employee liabilities for META, GOOGL, MSFT, and
COST, and COST `AccruedLiabilitiesCurrent` specifically as member rewards.
GOOGL CIK `1652044` accrued revenue share and accrued customer liabilities use
filing XBRL only: exact local names `AccruedRevenueShare` and
`AccruedCustomerLiabilitiesCurrent` under the Google issuer namespace whose
date exactly matches the selected 10-K report date. It requires a nondimensional, non-nil
instant fact from the exact selected accession. Matching uses namespace URI and
local name, never an XML prefix. Filing provenance retains the source URL, namespace, context,
dimensions, decimals, nil state, raw value, and parsed value. Multiple eligible
facts remain ambiguous even when only their context IDs differ.

Concept priority never suppresses a second eligible approved concept; equal
values are not confirmation unless a policy explicitly permits it. Filing-level
XBRL remains explicit and targeted.

META CIK `1326801` uses an explicit two-stage trade-payables derivation:
combined PP&E payable minus separately accrued PP&E identifies PP&E included in
trade AP; that amount is then subtracted from reported trade AP. Reported trade
AP comes from Company Facts `AccountsPayableTradeCurrent`; separately accrued
PP&E comes from filing-XBRL `PropertyAndEquipmentAccruedLiabilitiesCurrent`
under the report-date-specific Facebook namespace. The combined Company Facts
concept `CapitalExpendituresIncurredButNotYetPaid` is duration-shaped because it
is presented as supplemental non-cash cash-flow information. It is accepted
only as CIK-, concept-, selected-accession-, and current-FY-scoped derivation
evidence. Eligibility and ambiguity are evaluated only among observations of
that configured target concept: an eligible duration must end on the selected
report date, and its actual start and end dates are preserved. Unrelated
duration facts do not define the operand's fiscal period, and no calendar-year
length is assumed. The operand is never a direct instant balance-sheet value.
Missing or ambiguous target evidence keeps adjusted trade AP unresolved.

Annual Operating NWC level and adjacent annual change calculations are
implemented. A strict completeness layer
classifies required operating assets and liabilities, explicit exclusions,
issuer-specific non-applicability, and methodology-unresolved components. It
groups underlying resolved, missing, and ambiguous normalized results without
producing an amount. Explicit SEC zero remains resolved; missing evidence is
not zero, and methodology uncertainty is distinct from missing SEC evidence.

A separate valuation-readiness layer uses immutable, versioned, issuer-specific
component perimeters. Each ordered perimeter entry identifies its asset or
liability side and is either required evidence, an explicit methodology
blocker, or outside the valuation perimeter. Issuer-inapplicable components are
omitted from that issuer's valuation perimeter. Readiness inspects
only configured required metrics, preserves direct or derived evidence, and
does not infer a perimeter from whichever facts happen to resolve. Policy
versions record distinct economic perimeters; changing included components or
their required treatment requires a new version, while incidental code changes
do not. One active registry preserves exactly one default policy per CIK, while
a separate version-addressable registry retains historical definitions and
rejects duplicate policy ID/version identities. META v2 is active; META v1
remains available through explicit policy/version lookup. Reconstruction can
remain incomplete while valuation readiness succeeds.

Research supports an eventual component-derived result rather than a Current
Assets minus Current Liabilities shortcut. Broad residual formulas remain
prohibited because other-current captions mix operating and non-operating
items. Operating-lease current liabilities are explicitly excluded from the
initial policies while integrated lease treatment remains deferred. Apple
accrued distribution and marketing remains unresolved because only one of five
selected accessions contains the fact. GOOGL accrued revenue share and accrued
customer liabilities are the filing-XBRL-backed balance-sheet primitives
currently normalized. Strict reconstruction policies keep all five issuers
incomplete. META valuation policy v2 moves customer contract liabilities
outside its stable measurable valuation perimeter; their balances and movements
are omitted rather than treated as zero. META v2 and COST v1 are ready for all
periods with complete required evidence, while GOOGL, MSFT, and AAPL retain
explicit methodology blockers. Numerical O-NWC is produced only for ready
policy-periods. Current live validation calculates META v2 and COST v1 for all
five selected periods. Missing, ambiguous, or methodology-blocked periods
return readiness details without a partial amount. Required asset balances
contribute positively and required liability balances negatively using exact
`Decimal` arithmetic; the source results retain their reported magnitudes and
provenance. Readiness also requires every resolved mandatory result and its
evidence to match the selected filing accession, report date, and exact USD
unit.

Annual change in Operating NWC is calculated as closing O-NWC minus opening
O-NWC from two already calculated levels. The inputs must have the same company
CIK, policy ID, policy version, calculation formula, actual ordered
component/side/normalized-metric perimeter, and exact USD unit, with the closing date
strictly after the opening date. Inputs are never sorted. Actual fiscal dates
are preserved without assumptions about calendar years or year length. Each
change retains both full level results, including their component-level SEC
provenance. A policy/perimeter change raises a domain error instead of becoming
an apparent working-capital movement.
