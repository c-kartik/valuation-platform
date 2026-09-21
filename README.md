# Automated Equity Valuation Platform

A full-stack equity valuation platform combining SEC financial data extraction, financial statement normalization, and automated valuation analysis.

## Planned Capabilities

- Accept a US stock ticker
- Retrieve historical financial data primarily from SEC EDGAR/XBRL
- Normalize filings into a standardized financial schema
- Accept manual forward assumptions
- Calculate an FCFF DCF
- Support reverse DCF
- Support Bear / Base / Bull scenarios
- Generate valuation sensitivity analysis

Initial scope is US-listed non-financial companies.

## Current Status

The project is in the initial development phase.

Current milestone:

**SEC/XBRL historical financial data pipeline**

Initial validation company: **META**

See [`docs/project-status.md`](docs/project-status.md) for current progress and next steps.

## Development

Python 3.12 is used for the initial data and valuation modules.

Detailed setup and usage instructions will be added as the project develops.