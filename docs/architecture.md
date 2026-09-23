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

- `sec.client` handles GET requests, identifying headers, timeouts, HTTP errors,
  and JSON decoding.
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
- `normalization.historical` resolves selected annual observations into typed
  normalized, missing, or ambiguous results. It performs no network access and
  does not retain the complete Company Facts or selected-observation graph.

Annual normalization currently supports direct Revenue, Operating Income, and
Capex values. A candidate must be a numeric, exact-USD, current duration ending
on the selected 10-K report date. Actual observation start and end dates define
the economic period, including non-calendar and 52/53-week fiscal years. Capex
uses the same generic direct-resolution path and remains a positive expenditure
magnitude for later subtraction in FCFF.

Concept priority applies only after period validation. Equal lower-priority
facts for the same unit and period remain as confirming provenance. Conflicting
values and multiple valid USD periods return explicit ambiguity results.
Structurally valid non-USD observations are unsupported and do not participate
in period, priority, confirmation, or conflict resolution. Expected coverage
gaps return explicit missing results.

The normalization package does not infer interim period semantics, derive
quarters, aggregate financial concepts, or calculate valuation inputs. Those
remain separate later responsibilities.
