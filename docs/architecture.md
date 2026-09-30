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
- `normalization.balance_sheet` separately resolves annual instant Company Facts
  into primitive balance-sheet snapshots; it performs no retrieval or derived
  Operating NWC calculation.
- `normalization.derived` validates evidence-backed, CIK-scoped derivation
  policies and their operands. It performs no network access.

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

Annual balance-sheet normalization requires an exact selected 10-K accession,
a current instant observation with no start date, an end equal to the filing
report date, exact USD, and a numeric non-Boolean value. It preserves the actual
balance date and compact Company Facts provenance. Zero is valid; absence stays
typed missing. Conflicting eligible observations stay ambiguous.

The initial deterministic order is Operating Receivables, Inventory, Trade
Accounts Payable, then Customer Contract Liabilities. Evidence-backed
issuer-scoped alternatives support COST `ReceivablesNetCurrent`, META
`AccountsPayableTradeCurrent`, and COST `DeferredRevenueCurrent`. Concept
priority never suppresses a second eligible approved concept; equal values are
not confirmation unless a policy explicitly permits it. Filing-level XBRL
remains explicit and is not automatically connected.

Operating NWC and its change are not implemented. Research supports an eventual
component-derived result rather than a Current Assets minus Current Liabilities
shortcut. Broad other-current-asset and liability balances remain excluded
pending classification because they mix operating and non-operating items.
