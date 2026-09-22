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

**Phase 1C — relevant SEC filing selection and history orchestration**

Initial validation company: **META**

See [`docs/project-status.md`](docs/project-status.md) for current progress and next steps.

## Development

Python 3.12 is used for the initial data and valuation modules.

Install the current runtime dependency with:

```bash
python -m pip install -r requirements.txt
```

SEC requests require an identifying User-Agent supplied by the caller. The SEC
layer currently supports the official company ticker dataset and the recent
filing history in the main SEC submissions response. The main response also
discovers supplemental history-file metadata; each supplemental file is fetched
only when needed. A deterministic selector identifies the latest completed
annual periods and subsequent interim filings without performing network access.
Company Facts and financial normalization are later phases.

```python
from valuation_platform.sec import (
    SECClient,
    load_and_select_filings,
    resolve_ticker,
)

client = SECClient("Valuation Platform your-email@example.com")
identity = resolve_ticker("META", client)
selected = load_and_select_filings(client, identity, annual_limit=5)
```

Run the deterministic unit tests with:

```bash
PYTHONPATH=src python -m unittest discover -v
```
