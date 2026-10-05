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

**Phase 1F.8b — annual debt normalization**

Next milestone: **Phase 1F.9a — annual diluted-shares research/design**

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
Facts remains the default; filing XBRL is policy-driven and never fetched by
normalization. Missing balances remain distinct from zero. Broad other-current-
asset and liability accounts remain unresolved. Annual Operating NWC levels
and changes are implemented for ready META v2 and COST v1 periods; GOOGL, MSFT,
and AAPL retain explicit methodology blockers.
The same annual balance-sheet path now preserves gross reported cash and cash
equivalents and issuer-scoped short-term investments for all five validation
issuers, plus Apple-only non-current marketable securities. These captions may
contain restricted amounts. The platform does not yet calculate unrestricted
or excess cash, normalize strategic/non-marketable investments, or produce a
universal liquid-assets or enterprise-value-to-equity-value subtotal.
It also preserves four separate gross debt primitives: Commercial Paper,
COST-only Short-Term Borrowings, Current Portion of Long-Term Debt, and
Non-Current Long-Term Debt. Direct values use selected-filing Company Facts at
carrying value. Three validated GOOGL periods use explicit, accession-scoped
identities to remove finance-lease balances from combined debt-and-lease facts;
direct facts retain precedence and conflicts remain ambiguous. Missing debt is
never inferred as zero. Total debt, net debt, lease capitalization, and the
enterprise-value-to-equity-value bridge remain unimplemented.
Strict reconstruction policies continue to report whether each
annual period has complete evidence. Separate versioned valuation-perimeter
policies now determine whether the explicitly required components are ready for
future arithmetic. META valuation policy v2 excludes customer contract
liabilities from a stable measurable historical and forecast perimeter without
changing their normalized values or treating them as zero. META v2 and COST v1
have no perimeter blocker from that decision; period readiness still requires
every required normalized input. GOOGL, MSFT, and AAPL retain explicit
methodology blockers. Annual Operating NWC levels now calculate for ready
periods as required operating assets minus required operating liabilities.
Component balances retain their reported positive magnitudes, while ordered
calculation contributions apply the asset/liability sign and preserve the full
normalized or derived provenance. Non-ready periods produce their typed
readiness result rather than a partial amount.
Live validation calculated COST v1 and META v2 for all five selected periods.
For META's special combined unpaid-PP&E operand, eligibility and ambiguity are
evaluated only among observations of that configured target concept; unrelated
duration facts do not define its fiscal period. Actual start and end dates are
preserved without calendar-year assumptions.
Annual change in Operating NWC is derived from adjacent comparable calculated
levels as closing O-NWC minus opening O-NWC. Both levels must retain the same
company, exact valuation policy ID/version and formula, and the same actual
ordered component/side/normalized-metric perimeter; a perimeter change is rejected
rather than presented as cash flow. Results use actual fiscal dates, exact
`Decimal` arithmetic, and retain both complete level results and their SEC
provenance. Five current META or COST levels therefore produce four changes.
Positive change means operating NWC increased; the future FCFF layer will
subtract that amount. FCFF itself remains unimplemented.
Signed tax-evidence normalization preserves filing-displayed signs separately
from raw XBRL magnitudes and supports both rate and dollar reconciliations with
arithmetic validation. Callers supply explicit sign evidence; unresolved source
or methodology states remain visible. A pure operating-tax readiness layer now
requires an exact versioned policy, complete row treatment, exclusive pairs,
owned annual financial inputs, an evidenced statutory-rate anchor, and explicit
currency/scale compatibility. Historical operating-tax adjustments use strict
direct linkage: a complete tax effect must be explicitly linked to reported
Operating Income or have an exact filing-supported operating allocation. The
current 25-period corpus may therefore remain methodology-blocked. Historical
operating tax and NOPAT are optional analytical outputs; their absence does not
block forecast FCFF or DCF readiness. The forecast operating tax rate remains a
separate manually supplied assumption. Operating-tax expense and NOPAT remain
unimplemented.
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
