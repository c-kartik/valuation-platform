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
  submissions response while preserving each parallel-array row.

SEC retrieval and parsing do not perform filing selection, financial-period
classification, Company Facts access, XBRL normalization, derived financial
calculations, or valuation logic. Supplemental historical submission files are
outside the Phase 1B scope.
