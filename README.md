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

**Phase 1F.5h.1 complete — Operating NWC valuation readiness**

Next milestone: **resolve mandatory O-NWC perimeter blockers before arithmetic**

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
Company Facts retrieval preserves every SEC taxonomy, concept, unit, and
observation. When Company Facts omits an issuer extension, an explicit on-demand
source layer can retrieve and structurally parse the SEC-generated extracted
XBRL instance for one selected filing. A pure fact selector associates Company
Facts observations with selected filing
accessions and classifies structural period relationships without choosing
authoritative financial concepts or inferring YTD/discrete semantics. The first
normalization slice resolves annual Revenue, Operating Income, Pretax Income,
Income Tax Expense, Reported Effective Tax Rate, D&A, and Capex with explicit
missing and ambiguity results while preserving SEC provenance.
D&A is direct for the validated META, AAPL, and COST periods and derived from an
evidence-backed, CIK-scoped Company Facts policy for MSFT. GOOGL remains
unresolved. Interim periods and the remaining standardized financial metrics
are not normalized yet. Reported ETR is a historical accounting diagnostic
derived from the normalized monetary facts; the forecast operating tax rate
remains a separate manual assumption.
The separate annual balance-sheet path currently normalizes operating
receivables, Apple vendor non-trade receivables, inventory, trade accounts
payable, customer contract liabilities, employee-related liabilities for four
validated issuers, and Costco member rewards from current instant Company Facts
observations. It also normalizes GOOGL accrued revenue share and accrued customer
liabilities from explicitly supplied selected-filing XBRL artifacts. Company
Facts remains the default;
filing XBRL is policy-driven and never fetched by normalization. Missing
balances remain distinct from zero. Broad other-current-
asset and liability accounts, Operating NWC, and change in Operating NWC remain
unresolved. Strict reconstruction policies continue to report whether each
annual period has complete evidence. Separate versioned valuation-perimeter
policies now determine whether the explicitly required components are ready for
future arithmetic. COST is ready for all five selected periods; META is ready
for 2021–2024 and remains blocked in 2025 by its missing required customer
contract liability. GOOGL, MSFT, and AAPL retain explicit methodology blockers.
Neither readiness layer calculates Operating NWC.
For META only, reported trade accounts payable is adjusted through a pure,
provenance-preserving derivation that removes PP&E payable evidence split across
Company Facts and explicitly supplied filing XBRL. The duration-shaped combined
PP&E disclosure remains special derivation evidence and does not weaken direct
instant balance-sheet normalization.

```python
from valuation_platform.sec import (
    SECClient,
    fetch_company_facts,
    load_and_select_filings,
    resolve_ticker,
    select_fact_observations,
)
from valuation_platform.normalization import (
    normalize_annual_balance_sheets,
    normalize_annual_financials,
)

client = SECClient("Valuation Platform your-email@example.com")
identity = resolve_ticker("META", client)
selected = load_and_select_filings(client, identity, annual_limit=5)
company_facts = fetch_company_facts(client, identity)
selected_facts = select_fact_observations(selected, company_facts)
annual_financials = normalize_annual_financials(selected_facts)
annual_balance_sheets = normalize_annual_balance_sheets(selected_facts)
```

Run the deterministic unit tests with:

```bash
PYTHONPATH=src python -m unittest discover -v
```
