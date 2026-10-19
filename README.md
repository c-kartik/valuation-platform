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

**Phase 1 universe analyst-review expansion is paused.** The authoritative
[pause/resumption and Phase 2 handoff checkpoint](docs/phase1-universe-pause-checkpoint.md)
records 24 completed scoped company histories, 3 partial (CAT/JNJ/CVX) and
15 assessment-only among 42 eligible issuers; 8 specialized exclusions remain.
There are 199 selected annuals / 210 target slots, with 11 explicit deficits.
This is not full-universe completion or valuation-consumer certification.
That pause checkpoint proposed separately scoped Phase 2 work, initially one
company and a traceable Base case; it approved no engine or economic convention.
Subsequent Phase 2 milestones are recorded below. Universe reviews do not resume
automatically.

The [META Base-case consumer contract](docs/phase2-meta-base-consumer-contract.md)
records approved Stages A–C mathematical/interface conventions, a read-only
revenue-anchor boundary, five-year FCFF forecast, terminal/annual discounting
through EV and explicit equity/per-share arithmetic, verified with synthetic
fixtures and separately authorized temporary META, GOOGL and AAPL trials. Standing META
assumptions and bridge/share/award selections remain pending. The read-only
[anchor integration](docs/phase2-anchor-integration.md) also supports exact retained
GOOGL/AAPL revenue selections without approving their forecast or bridge inputs.
The [GOOGL/AAPL trial records](docs/phase2-googl-aapl-milestones.md) document the
completed, scope-qualified temporary trials; the
[three-company completion checklist](docs/phase2-completion-checklist.md) defines
remaining work. The [GOOGL ERP correction](docs/phase2-googl-aapl-milestones.md#googl-erp-reconciliation--2026-10-19)
aligns its specified ERP variant with META/AAPL; broader market judgments and
full valuation comparability remain open.
Timing is fiscal-end analytical using later-filed information,
not a contemporaneous backtest or current market-date valuation.

**Phase 1H complete with qualified scope: historical normalization v1 frozen.**
See the [frozen contract and artifact digests](docs/historical-normalization-v1-freeze.md)
and [all-issuer validation](docs/universe/phase-1h5-issuer-validation.md).

Completed freeze milestone (historical):

**Phase 1H.6 — historical-normalization-v1 scope freeze (complete)**

The separate analyst preparation layers and [company register](docs/company-data-preparation/index.md)
preserve frozen v1. Their current accepted company schedules supersede the earlier
pilot-only review queue, not its source history. The historical path uses reported
movements and reconciled CFO, without requiring complete reconstructed NWC or
deducting CFO movements twice. Older [timing/readiness designs](docs/financial-timing-readiness-design.md)
must be reconciled with that path and explicit manual forecasts when specifying
a future consumer; existing Phase 2A assumption models do not by themselves
certify valuation use. See the checkpoint for the exact unfinished backlog.

See [`docs/project-status.md`](docs/project-status.md) for current progress and next steps.

The frozen corpus has 43 generic completions and seven specialized execution
skips, 204 periods × 17 measures = 3,468 states: 1,905 resolved / 1,483 missing /
11 ambiguous / 27 methodology-blocked / 42 not-comparable. All 50 issuers / 51
securities are classified: 2 SUPPORTED (META/COST), 40 GENERALIZATION_REQUIRED,
8 SPECIALIZED_METHODOLOGY_REQUIRED. GE's specialized classification does not
remove its retained generic execution. XOM has no selected history; GEV/SNDK
have two periods each. Missing is not zero, and execution is not support.

Broader coverage is deferred, not claimed. Exact-accession curated approvals
do not extend implicitly to future/amended filings. Historical support does
not establish joint EBIT/D&A/book-NWC timing compatibility or full FCFF readiness.

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
At that historical smoke stage, two were `SUPPORTED`, 41 were
`GENERALIZATION_REQUIRED`, and seven are
`SPECIALIZED_METHODOLOGY_REQUIRED`. The [failure-taxonomy and root-cause
artifact](docs/universe/sp500-top-50-failure-taxonomy.md) records the complete
17-measure coverage matrix, all 24 ambiguities, schema and identity blockers,
and the ranked Phase 1H.4 backlog.

## Editable analyst inputs — forecast through value per share

The [META milestone record](docs/phase2-meta-milestone.md) completes the first-company,
scope-qualified end-to-end testing milestone: historical anchor → manual forecast →
FCFF/DCF → EV → explicit equity bridge → value/share. Synthetic tests and temporary
META-anchored trials exercised the workflow; no permanent META Base case, complete
claims coverage, financial-input sufficiency or fully diluted fair value is certified.
Phase 1 remains paused. [GOOGL/AAPL temporary trials](docs/phase2-googl-aapl-milestones.md)
have also completed with explicit limitations, without standing financial approval.
The [remaining Phase 2 scope](docs/phase2-completion-checklist.md) is META, GOOGL and
AAPL: market-input reconciliation, editable Bear/Base/Bull scenarios, reusable
sensitivities, bounded reverse DCF and final analyst acceptance/regression.
Those features and their economic conventions are not approved or implemented here.

Edit a copy of [synthetic-base.json](examples/valuation/synthetic-base.json) or
[meta-fy2025-unset.json](examples/valuation/meta-fy2025-unset.json); keep the
provided examples as references. Each year's six rates, WACC/g and all five
terminal ratios are independent fields. Rates must be fractional Decimal
**strings**: `"0.12"` means 12%, `"1"` means 100%; no percent signs, JSON numeric
rates, historical defaults or automatic Year-5 terminal copies. `null` means
unset, never zero. Supply analyst author, UTC timestamp and rationale, plus the
case's declared scope/limitations. Ordinary edits create no company policy or
approval record.

From the repository root, validate without calculating, then explicitly run the
synthetic example (revenue anchor 100, all assumptions synthetic):

```sh
python3 scripts/run_analyst_case.py examples/valuation/synthetic-base.json
python3 scripts/run_analyst_case.py examples/valuation/synthetic-base.json --run
python3 scripts/run_analyst_case.py examples/valuation/synthetic-base.json --run --output /tmp/synthetic-base-ev.json
python3 scripts/run_analyst_case.py examples/valuation/synthetic-base.json --run --format summary
python3 scripts/run_analyst_case.py examples/valuation/synthetic-base.json --run --format summary --output /tmp/synthetic-review.txt
python3 scripts/run_analyst_case.py examples/valuation/meta-fy2025-unset.json
python3 scripts/run_analyst_case.py examples/valuation/googl-fy2025-unset.json
python3 scripts/run_analyst_case.py examples/valuation/aapl-fy2025-unset.json
```

The three company-template commands intentionally exit 2 and list all 37 missing
numerical entries plus unset analyst metadata. They perform no forecast/valuation.
The synthetic example reproduces the independently checked A/B fixture EV
77.5770603520 in synthetic USD units, not a META value or recommended assumption.

The [runner](scripts/run_analyst_case.py) validates by default; `--run` requests
A/B computation for v1 or A/B/C for explicitly scoped v2 cases. `--format json` is the unchanged default with full-precision
values and provenance; `--format summary` renders a compact analyst report from
the same result. Without `--run`, either format validates only, with no valuation
or report calculation. Results print to stdout unless `--output` names a **new** file
outside the repository or under `output/`; its parent must exist. Existing
files, inputs and repository source/history paths cannot be overwritten.
`--output` saves the selected format, independent of filename extension, and
requires `--run`. Errors go to stderr with exit 2. JSON output retains the case identity, exact submitted
rate strings, author/date/rationale/scope/limitations and complete Stage A/B (and requested Stage C)
provenance. Validation checks JSON/models and the declared pinned identity only;
the selected retained audit/revenue boundary is resolved at run time, without network
retrieval or automatic refresh. Supported kinds are `synthetic-fixture-v1`,
`meta-fy2025`, `googl-fy2025` and `aapl-fy2025`. AAPL's selected fiscal end is
**2025-09-27**, not December 31; the five periods remain ordinal fiscal labels.
Errors identify paths such as `forecast_years[2].revenue_growth` for a JSON
numeric rate and `anchor.accession` for a mismatched selection.

New company templates declare shared engine behavior with `manual-fcff-v1` and,
for Stage C, `manual-equity-bridge-v1`. These use the existing arithmetic and
lease/SBC conventions, but grant no company financial acceptance. Legacy
`meta-base-fcff-v1` / `meta-base-equity-bridge-v1` identifiers and existing examples
remain valid and unchanged. See [exact selections, audit roles and limitations](docs/phase2-anchor-integration.md).

The additive `analyst-case-v2` extension requires
`"calculation_scope": "EQUITY_PER_SHARE"` and an explicit `bridge` object.
`analyst-case-v1` and its EV-only JSON remain unchanged. Copy
[synthetic-equity.json](examples/valuation/synthetic-equity.json) for a complete
synthetic example, or [meta-fy2025-equity-unset.json](examples/valuation/meta-fy2025-equity-unset.json)
for the deliberately incomplete META extension. It preserves all 37 unset
forecast inputs and adds no pending actual bridge/share numbers.

```sh
python3 scripts/run_analyst_case.py examples/valuation/synthetic-equity.json
python3 scripts/run_analyst_case.py examples/valuation/synthetic-equity.json --run --format summary
python3 scripts/run_analyst_case.py examples/valuation/synthetic-equity.json --run --output /tmp/synthetic-equity.json
python3 scripts/run_analyst_case.py examples/valuation/meta-fy2025-equity-unset.json
python3 scripts/run_analyst_case.py examples/valuation/googl-fy2025-equity-unset.json
python3 scripts/run_analyst_case.py examples/valuation/aapl-fy2025-equity-unset.json
```

The three company extensions fail with unset forecast, bridge/share and
unresolved-requirement errors; no company calculation runs. The synthetic example has EV 77.577060352 + eligible
assets (10+2) − financing 20 − other claims 3 = equity 66.577060352;
4 actual shares yield **16.644265088 USD/share**. These are synthetic USD units,
not millions. The summary labels money in USD millions and the denominator in
actual shares; per-share output is USD/share, displayed to eight decimals.

The `bridge` mirrors the existing [Stage C models](src/valuation_platform/valuation/bridge.py):
`components` (`BridgeComponent`), non-operand `observations` (`BridgeObservation`),
three-role `coverage` (`PopulationCoverage`), `shares` (`ValuationShares`),
`input_basis`, `valuation_class_id`, `unresolved_requirements` and
`convention_version: "manual-equity-bridge-v1"` (legacy META spelling remains valid).
Supply every model field
explicitly, including empty reference arrays and booleans. Monetary amounts and
share counts use Decimal strings in base USD/actual shares at scale 1; CIK and
scale are JSON integers. Dates are `YYYY-MM-DD`. Component roles are
`ELIGIBLE_ASSET`, `FINANCING_CLAIM`, `OTHER_EQUITY_CLAIM`; magnitudes are nonnegative
and the engine supplies signs. Keep reported/derived/proxy/manual origins,
source precision, source/decision references and rationale explicit. Overlap and
alternative references name component/observation IDs; two selected operands
cannot overlap or be alternative measurements, nor overlap the forecast.
Selected components/shares match the anchor company and date; supporting
observations may retain different dates/units without becoming operands.

Coverage must name exactly each role's selected populations; an empty role needs
a referenced `OMISSION` observation with `value: null` and explicit rationale.
An omission is an assumption, never reported zero or a numeric deduction.
Coverage reviews carry author/UTC timestamp/rationale and decision references.
Shares require company/date/class, declared equivalence and the existing SBC/award
convention plus references/rationale. Examples show the exact editable structure.
Nonempty references authenticate no approval, economic completeness or hidden
overlap. Unresolved requirements must be resolved explicitly before running;
requested per-share cases never silently fall back to EV-only output.

Equity JSON uses `analyst-case-equity-per-share-v1`, retains submitted inputs and
full Stage A/B/C provenance, and records signed components, subtotals, shares and
raw negative results. The summary includes class/award declarations, material
exclusions, unknown omissions and supplied limitations. Actual META eligibility,
claims, share equivalence and existing awards remain pending for a standing case;
the milestone records separately authorized temporary trials. No standing actual
selections are inferred from historical approvals or example metadata.

The summary shows the analyst/input basis and anchor, annual percentage inputs,
USD-million cash flows with discount factors/PVs, explicit terminal inputs and an
enterprise-value reconciliation. Investment means cash PP&E plus non-overlapping
new finance-leased operating assets, excluding finance principal. Working-capital
cash requirement uses full forecast revenue; positive uses cash and negative
releases it. EV is enterprise value, not equity or per-share value.
Discounted terminal value / EV is undefined for zero EV; signed or >100% ratios
remain visible with an explanation. Display-only HALF_EVEN rounding uses 8
decimals for USD millions, 2 for percentages and 6 for factors; rounded components
may not sum exactly and display digits do not improve source precision. Supplied
scope/rationale/limitations and later-filed-information timing remain visible;
the JSON result and inputs are never rounded or mutated by the renderer.

The engine has synthetic verification and temporary scope-qualified META/GOOGL/AAPL trial
coverage. Editable inputs and `--run` do not certify economic consistency, evidence
completeness or financial acceptance. A permanent META case and further execution
require separately scoped decisions; the [input review](docs/phase2-meta-base-input-review.md)
remains review material. No approval workflow is required for editing or validating
a case, and none of the incomplete company templates contains trial assumptions.

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
or component sum; schema 4 introduced full reviewed scope and occurrence/support
provenance. Interim periods and the remaining standardized financial metrics
are not normalized yet. Reported ETR is a historical accounting diagnostic
derived from the normalized monetary facts; the forecast operating tax rate
remains a separate manual assumption.
Wave 28 adds only ten exact AMZN/LLY [curated Capex acceptances](docs/capex-scope-evidence-results.md),
bringing Capex to 157 resolved / 47 missing / zero ambiguous. Schema 5 preserves
the complete Capex review/occurrence audit and explicit evidence-representation
correction/refresh histories. The generic policy and 47 controls are unchanged;
aggregate is 1,895/1,493/11/27/42 across 3,468 states. This does not certify
future integrated FCFF readiness or resume valuation work.
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
never inferred as zero. Automatic total/net debt and lease capitalization remain
unimplemented in historical normalization. The separate Stage C bridge consumes
explicit manual components; it does not infer a complete financing population.
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
Positive change means operating NWC increased. A book-delta FCFF consumer remains
unimplemented; approved Stage A instead consumes a direct manual cash-requirement
ratio and does not subtract these historical changes.
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
