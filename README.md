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

The initial methodology targets US-listed non-financial operating companies.
Specialized financial and other structures will require separate methodology
where the operating-company FCFF framework is not appropriate.

## Current Status

The project is in the initial development phase.

Current milestone:

**Phase 1H — S&P 500 Top 50 universe expansion**

Next step: **Phase 1H.4 — execute the ranked generalization waves**

See [`docs/project-status.md`](docs/project-status.md) for current progress and next steps.

The current historical standardized-output corpus contains five companies and
25 annual periods: META, GOOGL, MSFT, AAPL, and COST, with five selected 10-K
periods each. Validation means the production historical pipeline has been run
and checked against filing evidence; it does not mean every metric resolves.
Typed missing, derived, ambiguous, and methodology-blocked results remain valid
outcomes.

The next target is the frozen S&P 500 Top 50 snapshot, followed over time by
broader S&P 500 coverage. Forecast and DCF calculation work is temporarily
paused while the historical layer is stress-tested across that wider universe.
The existing Phase 2A manual assumptions model remains available.

Phase 1H.1 froze the official **S&P 500 Top 50 Index** universe effective
2026-10-02 in
[`docs/universe/sp500-top-50-2026-10-02.csv`](docs/universe/sp500-top-50-2026-10-02.csv).
It contains 51 securities representing 50 SEC issuers because Alphabet has two
included share classes. Five issuers are validated seeds, 38 are preliminary
operating-company candidates, and seven are specialized-methodology candidates.
See the accompanying [snapshot note](docs/universe/sp500-top-50-2026-10-02.md)
for sources, classification rationale, and Phase 1H.2 execution waves.

The Phase 1H.2 production smoke test attempted all 43 generic issuers. Forty-one
reached standardized output, GEV and SNDK stopped at Company Facts parsing, and
the seven specialized issuers were retained as explicit skips. All five seed
issuers preserved their expected five-period typed behavior. XOM reached
standardized output with no selected annual periods, which remains diagnostic
evidence rather than an inferred value or automatic policy change.

Phase 1H.3 classified the smoke evidence without changing production policy.
Across the 50 issuers, two are currently `SUPPORTED`, 41 are
`GENERALIZATION_REQUIRED`, and seven are
`SPECIALIZED_METHODOLOGY_REQUIRED`. The [failure-taxonomy and root-cause
artifact](docs/universe/sp500-top-50-failure-taxonomy.md) records the complete
17-measure coverage matrix, all 24 ambiguities, schema and identity blockers,
and the ranked Phase 1H.4 backlog.

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
It also resolves annual Diluted Weighted-Average Shares as the reported GAAP
EPS denominator. Twenty-two validated periods use the direct standard Company
Facts concept; GOOGL 2021–2023 use a CIK- and accession-scoped filing-XBRL
derivation that adds Class A and Class C denominators without double-counting
Class B. Values retain the share basis of the original selected filing,
including GOOGL 2021's pre-split basis. This historical metric is not a current
or forecast fully diluted valuation-share policy.
The standardized historical-output layer now assembles these annual duration
results with fiscal-year-end cash, investment, debt, and calculated Operating
NWC results in a period-centric company record. It preserves typed missing and
ambiguity states, actual fiscal dates, compact SEC provenance, policy versions,
and exact `Decimal` values serialized as strings. It does not calculate cash or
debt subtotals, historical NOPAT, forecasts, FCFF, or valuation results.
The separate valuation package now defines immutable manual assumptions for
five ordered explicit forecast periods. Rates use finite `Decimal` fractions;
each year supplies revenue growth, operating margin, forecast tax rate, and
D&A, Capex, and change in Operating NWC as percentages of revenue. One manual
WACC and one terminal-growth rate are stored with the company CIK and latest
historical filing anchor. This layer validates and serializes assumptions only:
it does not populate them from history or calculate forecasts, FCFF, terminal
value, DCF, an equity bridge, or value per share.
D&A is direct for the validated META, AAPL, and COST periods and derived from an
evidence-backed, CIK-scoped Company Facts policy for MSFT. GOOGL remains
unresolved. Phase 1H.4 Wave 20 additionally accepts five exact Visa filings
through the [reviewed curated D&A policy](docs/depreciation-amortization-scope-evidence-design.md#wave-20-implementation-and-verified-results):
115 corpus periods resolve and 89 remain missing. This is not a generic fallback
or component sum; schema 4 preserves full reviewed scope and occurrence/support
provenance. Interim periods and the remaining standardized financial metrics
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
