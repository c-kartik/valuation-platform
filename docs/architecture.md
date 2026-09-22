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

```text
SEC retrieval and submissions parsing
  ↓
Incremental history orchestration
  ↓
Pure filing selection
  ↓
Company Facts retrieval
  ↓
Later fact and period selection
  ↓
Later financial normalization
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
