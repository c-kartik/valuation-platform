# AGENTS.md

## Project

Automated Equity Valuation Platform.

The application will accept a US stock ticker, retrieve and normalize historical financial data primarily from SEC EDGAR/XBRL, accept manual forecast assumptions, and calculate an FCFF DCF.

The Phase 1H validation universe includes every security in the frozen
S&P 500 Top 50 Index snapshot at
`docs/universe/sp500-top-50-2026-10-02.csv`. Record and classify every
constituent; do not omit financial or other specialized companies. The current
generic methodology initially supports ordinary operating companies. Classify
banks, insurers, REITs, and other structures that need dedicated treatment as
`SPECIALIZED_METHODOLOGY_REQUIRED` rather than forcing them through the
operating-company FCFF model.

## Current Phase

Phase 1H expands the operational Python SEC/XBRL historical pipeline from the
five-company validation corpus (META, GOOGL, MSFT, AAPL, and COST) to a defined
S&P 500 Top 50 snapshot. Use corpus failures to improve normalization
architecture and policies without inventing missing values or forcing coverage.

Classify constituents as `SUPPORTED`, `GENERALIZATION_REQUIRED`, or
`SPECIALIZED_METHODOLOGY_REQUIRED`. During Phase 1H, prefer reusable,
high-frequency normalization fixes over issuer-specific hacks. Use an
issuer-specific policy only when filing evidence and accounting rationale
support it, and never force a result to improve coverage statistics.

Phase 2A manual assumptions are available, but forecast, FCFF, DCF, equity
bridge, and per-share valuation work is paused throughout Phase 1H. Resume it
only after Phase 1H.6 freezes historical normalization v1. Do not implement
valuation UI or deployment infrastructure yet.

## Engineering Principles

- Prioritize correctness, modularity, explainability, and testability.
- Build incrementally; do not implement the entire application at once.
- Keep SEC retrieval, XBRL normalization, derived financial calculations, and valuation calculations separate.
- Prefer official SEC data for historical financials.
- Never invent missing financial values.
- Preserve source metadata so normalized values can be traced back to SEC filings.
- Avoid premature infrastructure such as databases, caching, containers, authentication, or cloud services unless clearly required.
- Add tests for financial calculations and important normalization logic.

## Financial Methodology

Historical standardized output should eventually support:

- Revenue
- EBIT / operating income
- Taxes
- D&A
- Capex
- Operating NWC and change in NWC
- Cash and investments
- Debt
- Diluted shares
- Other inputs required for FCFF valuation

Core FCFF relationship:

FCFF = NOPAT + D&A - Capex - Change in NWC

where:

NOPAT = EBIT × (1 - tax rate)

Forecast assumptions will initially be entered manually.

## Repository Documentation

Keep these files current when relevant decisions are made:

- `README.md` — project overview, setup, and usage
- `docs/architecture.md` — architecture and technical decisions
- `docs/financial-methodology.md` — financial definitions and methodology
- `docs/project-status.md` — completed work, current milestone, known issues, and next steps

Repository documentation is the source of truth for project state and decisions.

## Development Workflow

For each milestone:

1. Define what is being built and why.
2. Implement the smallest working version.
3. Add or update tests.
4. Run tests locally.
5. Validate financial outputs against actual SEC filings when applicable.
6. Update documentation when architecture, methodology, or project status changes.
7. Commit a coherent unit of work.

Do not silently change financial definitions or architecture decisions. Document material changes.
