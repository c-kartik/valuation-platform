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

Before forecast and DCF development continues, Phase 1H will generalize the
historical normalization boundary against a defined S&P 500 Top 50 constituent
snapshot. The intended sequence remains SEC/XBRL retrieval → normalization →
standardized historical output → manual assumptions → future forecast and DCF;
universe validation is now the gate between the existing assumptions model and
further valuation-engine work.

## Universe Validation Boundary

Phase 1H uses the immutable, dated snapshot at
`docs/universe/sp500-top-50-2026-10-02.csv`: 51 index securities representing
50 SEC issuers as of 2026-10-02. Source tickers remain distinct from canonical
project tickers, and the two Alphabet share classes remain separate security
rows tied to one SEC CIK. Future index changes require a new snapshot rather
than mutation of this validation record.

The development runner at `scripts/run_sp500_top50_smoke.py` passes each
supported-seed and operating-company candidate issuer through the existing
ticker, filing-selection, Company Facts, normalization, and standardized-output
APIs. Execution is grouped by SEC CIK, ordered by the frozen snapshot, and
continues after issuer-level failures. The runner records explicit pipeline
stages, selected annual dates, typed and per-measure statuses, and compact
direct/derived/calculated counts in an ephemeral JSON artifact. It retains all
security rows for reporting, marks specialized issuers as explicit skips, and
does not add a parallel parser or persistent cache.

Each constituent will be classified as `SUPPORTED`,
`GENERALIZATION_REQUIRED`, or `SPECIALIZED_METHODOLOGY_REQUIRED`. Failures will
be grouped into retrieval, filing-selection, concept-policy, issuer-extension,
dimensional, derivation, methodology, and specialized-business-model classes.
High-frequency generalizable problems take priority over issuer-specific
policies. An issuer-specific policy is appropriate only when filing evidence
and accounting treatment justify it.

Coverage does not override evidence discipline: missing is not zero,
ambiguity remains explicit, methodology blockers remain visible, provenance is
preserved, and later comparative filings do not silently replace original
selected-accession evidence.

Phase 1H.3 records root causes in
`docs/universe/sp500-top-50-failure-taxonomy.md`. Identity generalization must
continue to normalize only documented SEC representations and then enforce
exact CIK equality. Registrant-successor or filing-owner relationships must be
established from official SEC identifiers and filing metadata; fuzzy company
names and issuer hardcodes are not identity evidence. Financial gaps remain
typed until a reusable concept rule, complete derivation, or documented
issuer-specific accounting policy is supported by filing evidence.

## Valuation Assumptions Boundary

`valuation.assumptions` is independent from SEC retrieval and normalization.
It defines one immutable manual assumption set bound only to a company CIK,
the latest historical accession, and its fiscal-end date. Five explicit
forecast periods use canonical indices 1–5 and descriptive fiscal-year labels;
the module does not synthesize dates or assume a December year-end.

Each period stores finite `Decimal` fractions for revenue growth, operating
margin, forecast tax rate, D&A as a percentage of revenue, Capex as a
percentage of revenue, and change in Operating NWC as a percentage of revenue.
Rates must already be finite `Decimal` instances and are not coerced from
integers, floats, strings, or other numeric representations.
The set stores one constant manual WACC and one terminal-growth rate. Explicit
serialization emits Decimal strings and preserves period order.

This layer validates assumptions only. It does not inspect standardized
history, populate assumptions, calculate forecast financials, define
loss-period tax treatment, derive WACC, or calculate FCFF, terminal value, DCF,
an equity bridge, or per-share value. A future forecast boundary will validate
the historical anchor against `StandardizedHistoricalCompany`.

## Phase 1 SEC Boundary

The SEC package separates transport from dataset interpretation:

- `sec.client` handles GET transport, identifying headers, timeouts, HTTP errors,
  raw response retrieval, and JSON decoding.
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
  concepts or authoritative reporting periods. Its top-level identity parser
  accepts a nonnegative integer CIK, a canonical unpadded decimal string, or an
  exact ten-digit padded string equal to the requested company's
  `cik_padded`; every accepted form is normalized to an integer before the
  existing identity-equality check.
- `sec.filing_xbrl` discovers the SEC-generated extracted XBRL instance that
  corresponds to a selected filing's primary document, retrieves it explicitly
  on demand, and structurally preserves standard and issuer-extension facts,
  contexts, units, and dimensions.
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

Company Facts remains the primary standardized source. Filing-level extracted
XBRL is a targeted fallback source when filing evidence needed for later
methodology is absent from Company Facts. Retrieval is never automatic, and the
filing-level output is not yet connected to fact selection or normalization.
The parser consumes the SEC-generated XML instance rather than implementing an
Inline XBRL processor or resolving schemas and linkbases.

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
- `normalization.models` defines immutable direct, derived, missing, and
  ambiguous results with compact operand-level SEC provenance.
- `normalization.historical` resolves direct observations first and orchestrates
  an approved derivation only when the direct result is missing.
- `normalization.diluted_shares` contains the narrow, pure GOOGL filing-XBRL
  derivation for selected 2021–2023 diluted EPS denominators. Filing artifacts
  are explicitly supplied by the caller; the module performs no retrieval.
- `normalization.output` assembles already-normalized duration, instant,
  Operating NWC, and change results into an immutable period-centric company
  history. It is pure and network-free and validates consistency without
  repeating financial calculations.
- `normalization.balance_sheet` separately resolves annual instant evidence
  from explicit Company Facts or filing-XBRL policies into primitive
  balance-sheet snapshots; parsed filing artifacts are supplied by the caller,
  so it performs no retrieval or derived Operating NWC calculation.
- `normalization.operating_nwc` preserves strict issuer-specific reconstruction
  diagnostics and separately evaluates versioned valuation perimeters for
  calculation readiness. It calculates annual O-NWC levels only after readiness
  succeeds, then derives adjacent annual changes only from levels with the same
  company, exact policy ID/version and formula, and actual ordered calculation
  perimeter. Level and change results retain their
  complete source results. The module remains pure and network-free.
- `normalization.derived` validates evidence-backed, CIK-scoped derivation
  policies and their operands. It performs no network access.
- `normalization.balance_sheet_derivation` resolves the narrowly approved META
  trade-payables adjustment from already selected Company Facts and explicitly
  supplied filing-XBRL evidence. It performs no retrieval or O-NWC arithmetic.
- `normalization.tax_evidence` normalizes caller-supplied, explicitly signed tax
  reconciliation rows and validates rate or dollar bridge arithmetic. It keeps
  raw XBRL values separate from filing-displayed signs and retains unresolved
  evidence states. It has no retrieval, sign-scraping, operating-tax policy, or
  NOPAT behavior.
- `normalization.operating_tax` is a pure, network-free policy/readiness
  boundary. It binds one owned annual financial result to its signed bridge,
  explicit monetary scale, evidenced statutory-rate anchor, and exact immutable
  policy version. Guarded bridge-row decisions and exclusive pair definitions
  produce typed readiness or blockers without calculating operating tax or
  NOPAT. Historical operating tax and NOPAT are optional analytical outputs;
  valuation may proceed with a separately supplied forecast tax-rate assumption.

Annual normalization currently supports direct Revenue, Operating Income,
Pretax Income, Income Tax Expense, D&A, and Capex values, plus derived Reported
Effective Tax Rate. Results use the deterministic order Revenue, Operating
Income, Pretax Income, Income Tax Expense, Reported Effective Tax Rate, D&A,
then Capex, followed by Diluted Weighted-Average Shares. Monetary direct
candidates must be numeric, exact-USD, current durations ending on the selected
10-K report date. Actual observation start and end dates define the economic
period, including non-calendar and 52/53-week fiscal years. Diluted
Weighted-Average Shares instead requires the exact standard
`WeightedAverageNumberOfDilutedSharesOutstanding` concept, unit `shares`, an
integer non-Boolean Company Facts value, and the same selected-accession/current
annual-duration boundary. Its normalized value is an exact `Decimal`.
D&A and Capex use the same generic direct-resolution path. A direct D&A result
takes precedence. When direct D&A is missing, an approved policy may produce a
provenance-distinct derived value; direct ambiguity is never replaced by a
derivation. The initial derived policy applies only to Microsoft CIK `789019`
and adds same-period Company Facts observations for `Depreciation` and
`AmortizationOfIntangibleAssets`. Filing-level XBRL is not automatically
connected to normalization. Capex remains a positive expenditure magnitude for
later subtraction in FCFF.

GOOGL CIK `1652044` selected 2021–2023 filings provide only class-dimensional
diluted denominators. When the nondimensional direct result is missing, the
approved derivation adds the Class A denominator, which assumes Class B
conversion, to the economically separate Class C denominator. Class B is not
added again. The rule requires the exact selected accession, annual period,
standard concept, shares unit, approved class axis/members, and report-date
Google namespace for Class C. Direct results and direct ambiguity retain
precedence. Original-filing share basis is preserved; no later comparative fact
or automatic stock-split restatement replaces GOOGL 2021's pre-split result.

Concept priority applies only after period validation. Equal lower-priority
facts for the same unit and period remain as confirming provenance. Conflicting
values and multiple valid USD periods return explicit ambiguity results.
Structurally valid non-USD observations are unsupported and do not participate
in period, priority, confirmation, or conflict resolution. Expected coverage
gaps return explicit missing results.

Derived values preserve the operation and every ordered operand, including its
source kind, source URL, taxonomy, concept, value, unit, period, and selected
accession. The derived layer supports approved addition and division policies;
it does not provide a general expression engine, issuer-extension arithmetic,
impairment or lease adjustments, or interim derivation. MSFT D&A retains its
existing fact operands. Reported ETR uses a
minimal normalized-metric operand model so it can preserve both authoritative
direct inputs without repeating Company Facts concept selection.

### Standardized Historical Output

The company-level historical boundary uses ordered annual records as its
canonical representation. Each record retains one selected 10-K, its actual
fiscal duration, its closing balance date, and ordered standardized measures.
Resolved duration facts must agree on start/end dates and end on the filing
report date. Instant facts remain explicitly instant and use that same closing
date. Metric series are accessors over annual records rather than a second data
store.

Resolved values use exact `Decimal` objects and retain direct, derived, or
calculated identity. Missing, ambiguous, not-comparable, and methodology-blocked
states remain explicit. Compact provenance contains source kind, URL,
accession, concept or namespace, and filing-XBRL context where applicable,
without retaining raw Company Facts or filing-XBRL graphs. Serialization emits
Decimal strings, ISO dates, stable enum values, and ordered arrays.

Operating NWC levels and changes enter only as existing calculation or
readiness results; the assembler performs no O-NWC arithmetic. Cash,
investment, and debt primitives remain separate. This boundary introduces no
historical NOPAT, financial subtotal, forecast, FCFF, equity bridge, or
valuation calculation.

Reported ETR divides normalized Income Tax Expense by normalized Pretax Income
using a 34-digit local `Decimal` context and a dimensionless `pure` unit. Its
operands must be direct, USD, accession- and period-compatible results. Operand
source URLs remain independent. A negative denominator produces a valid ratio
with an explicit diagnostic; a zero denominator produces a typed missing
result. No near-zero threshold or presentation rounding is applied.

The normalization package does not infer interim period semantics, derive
quarters, aggregate financial concepts, determine forecast operating tax
assumptions, or calculate valuation inputs. Those remain separate later
responsibilities.

Tax evidence accepts explicit sign authority from the original filing table or
a reliable calculation relationship. Percentage-point rows retain their
displayed rate and pretax denominator alongside the unrounded Decimal tax
amount derived from them. Dollar rows retain their reported currency amount.
Bridge validation reports exact, disclosed-rounding, unreconciled, or incomplete
evidence status. Rounding tolerance conservatively counts the starting value,
each displayed row, and reported total at the declared precision; it never
creates a balancing row. Normalized rows validate their own source identity and
rate/dollar arithmetic. Calculation-relationship sign authority requires an
auditable rationale. Diagnostic income-base, pairing, and treatment
classifications do not drive an adjusted-tax result.

Operating-tax readiness requires complete treatment of the exact bridge-row
inventory. Row references combine bridge position with source and identity
guards so repeated labels cannot be confused. Paired rows have complete,
exclusive membership, and policy order does not determine their meaning. The
boundary validates company, filing, accession, report date, economic period,
currency, scale, and statutory-rate ownership. Zero or negative Operating
Income, negative Pretax Income, and unresolved benefit realizability are
conservatively blocked. No production issuer policy is registered yet; the
current 25-period corpus remains methodology-blocked.
Changing row treatment, pairing, allocation, supported periods, readiness,
loss behavior, or future calculation semantics requires a new policy version.
No active production-policy registry is introduced while no real issuer period
has an approved complete policy.

Historical operating-tax attribution uses strict direct linkage. A complete
jurisdictional or reconciliation tax effect may enter tax on reported Operating
Income only when the filing explicitly links it to income inside that measure
or supplies an exact reproducible operating allocation. A paired gross-tax and
credit effect additionally requires complete membership, a common evidenced
regime and income base, and explicit Operating Income linkage. Otherwise the
row remains methodology-unresolved. Recurring captions, state or foreign
labels, net presentation, absence of disclosed contamination, proportional
Operating Income/Pretax Income allocation, geographic or revenue allocation,
and applying a reconciliation percentage directly to Operating Income do not
satisfy this boundary.

Rate-reconciliation percentages are dollarized using their original reported
Pretax Income denominator. Because that denominator includes non-operating
items, the resulting amount cannot generally be transferred to Operating
Income. Missing historical operating tax is preserved rather than estimated.
The forecast and valuation layers will accept a manual forecast operating tax
rate independently, so unresolved historical operating tax or NOPAT does not
block forecast FCFF or DCF readiness.

Annual balance-sheet normalization requires an exact selected 10-K accession,
a current instant observation with no start date, an end equal to the filing
report date, exact USD, and an integer non-Boolean value. It preserves the actual
balance date and source-specific compact provenance. Company Facts is the
default source. A policy may instead explicitly require filing XBRL; the caller
retrieves selected-filing artifacts and supplies them to the network-free
normalizer. There is no automatic fallback or bulk retrieval. Zero is valid;
absence stays typed missing. Conflicting eligible observations stay ambiguous.

The instant resolver also preserves three gross reported liquidity and
investment primitives. `CashAndCashEquivalentsAtCarryingValue` supplies cash
for the five validated CIKs. Short-term investments use CIK-scoped policies:
`MarketableSecuritiesCurrent` for META, GOOGL, and AAPL, a META-only
`AvailableForSaleSecuritiesDebtSecuritiesCurrent` fallback, and
`ShortTermInvestments` for MSFT and COST. Apple alone uses
`MarketableSecuritiesNoncurrent` for long-term marketable securities. These
policies use Company Facts only. They do not retrieve filing XBRL, subtract
restricted balances, include strategic/non-marketable investments, or derive a
liquid-assets subtotal.

The same resolver preserves four separate annual debt primitives from Company
Facts: `CommercialPaper`, COST-only `OtherShortTermBorrowings`,
`LongTermDebtCurrent`, and `LongTermDebtNoncurrent`. Values retain reported
carrying-value classifications; the normalizer does not create current debt,
total debt, or net debt subtotals. GOOGL CIK `1652044` has two explicit
derivation policies restricted to its selected 2021–2023 10-K accessions. The
current portion is combined debt and finance leases including current
maturities, minus non-current combined debt and leases, current finance-lease
liability, and unamortized discount/issuance costs. Non-current debt is the
non-current combined balance minus total finance-lease liability net of its
current portion. Every concept operand and arithmetic step is retained. A
matching direct value wins; a direct/derived conflict is ambiguous. Outside the
validated accessions, the derivations do not run.

The deterministic balance-sheet order is Operating Receivables, Vendor Non-Trade
Receivables, Inventory, Trade Accounts Payable, Accrued PP&E Purchases,
Customer Contract Liabilities, Employee-Related Liabilities, Accrued
Revenue-Share Liability, Accrued Customer Liabilities, Member Rewards
Liability, Cash and Cash Equivalents, Short-Term Investments, Long-Term
Marketable Securities, Commercial Paper, Short-Term Borrowings, Current Portion
of Long-Term Debt, then Non-Current Long-Term Debt. Evidence-backed
issuer-scoped policies support COST `ReceivablesNetCurrent`, META
`AccountsPayableTradeCurrent`, COST `DeferredRevenueCurrent`, Apple
`NontradeReceivablesCurrent`, employee liabilities for META, GOOGL, MSFT, and
COST, and COST `AccruedLiabilitiesCurrent` specifically as member rewards.
GOOGL CIK `1652044` accrued revenue share and accrued customer liabilities use
filing XBRL only: exact local names `AccruedRevenueShare` and
`AccruedCustomerLiabilitiesCurrent` under the Google issuer namespace whose
date exactly matches the selected 10-K report date. It requires a nondimensional, non-nil
instant fact from the exact selected accession. Matching uses namespace URI and
local name, never an XML prefix. Filing provenance retains the source URL, namespace, context,
dimensions, decimals, nil state, raw value, and parsed value. Multiple eligible
facts remain ambiguous even when only their context IDs differ.

Concept priority never suppresses a second eligible approved concept; equal
values are not confirmation unless a policy explicitly permits it. Filing-level
XBRL remains explicit and targeted.

META CIK `1326801` uses an explicit two-stage trade-payables derivation:
combined PP&E payable minus separately accrued PP&E identifies PP&E included in
trade AP; that amount is then subtracted from reported trade AP. Reported trade
AP comes from Company Facts `AccountsPayableTradeCurrent`; separately accrued
PP&E comes from filing-XBRL `PropertyAndEquipmentAccruedLiabilitiesCurrent`
under the report-date-specific Facebook namespace. The combined Company Facts
concept `CapitalExpendituresIncurredButNotYetPaid` is duration-shaped because it
is presented as supplemental non-cash cash-flow information. It is accepted
only as CIK-, concept-, selected-accession-, and current-FY-scoped derivation
evidence. Eligibility and ambiguity are evaluated only among observations of
that configured target concept: an eligible duration must end on the selected
report date, and its actual start and end dates are preserved. Unrelated
duration facts do not define the operand's fiscal period, and no calendar-year
length is assumed. The operand is never a direct instant balance-sheet value.
Missing or ambiguous target evidence keeps adjusted trade AP unresolved.

Annual Operating NWC level and adjacent annual change calculations are
implemented. A strict completeness layer
classifies required operating assets and liabilities, explicit exclusions,
issuer-specific non-applicability, and methodology-unresolved components. It
groups underlying resolved, missing, and ambiguous normalized results without
producing an amount. Explicit SEC zero remains resolved; missing evidence is
not zero, and methodology uncertainty is distinct from missing SEC evidence.

A separate valuation-readiness layer uses immutable, versioned, issuer-specific
component perimeters. Each ordered perimeter entry identifies its asset or
liability side and is either required evidence, an explicit methodology
blocker, or outside the valuation perimeter. Issuer-inapplicable components are
omitted from that issuer's valuation perimeter. Readiness inspects
only configured required metrics, preserves direct or derived evidence, and
does not infer a perimeter from whichever facts happen to resolve. Policy
versions record distinct economic perimeters; changing included components or
their required treatment requires a new version, while incidental code changes
do not. One active registry preserves exactly one default policy per CIK, while
a separate version-addressable registry retains historical definitions and
rejects duplicate policy ID/version identities. META v2 is active; META v1
remains available through explicit policy/version lookup. Reconstruction can
remain incomplete while valuation readiness succeeds.

Research supports an eventual component-derived result rather than a Current
Assets minus Current Liabilities shortcut. Broad residual formulas remain
prohibited because other-current captions mix operating and non-operating
items. Operating-lease current liabilities are explicitly excluded from the
initial policies while integrated lease treatment remains deferred. Apple
accrued distribution and marketing remains unresolved because only one of five
selected accessions contains the fact. GOOGL accrued revenue share and accrued
customer liabilities are the filing-XBRL-backed balance-sheet primitives
currently normalized. Strict reconstruction policies keep all five issuers
incomplete. META valuation policy v2 moves customer contract liabilities
outside its stable measurable valuation perimeter; their balances and movements
are omitted rather than treated as zero. META v2 and COST v1 are ready for all
periods with complete required evidence, while GOOGL, MSFT, and AAPL retain
explicit methodology blockers. Numerical O-NWC is produced only for ready
policy-periods. Current live validation calculates META v2 and COST v1 for all
five selected periods. Missing, ambiguous, or methodology-blocked periods
return readiness details without a partial amount. Required asset balances
contribute positively and required liability balances negatively using exact
`Decimal` arithmetic; the source results retain their reported magnitudes and
provenance. Readiness also requires every resolved mandatory result and its
evidence to match the selected filing accession, report date, and exact USD
unit.

Annual change in Operating NWC is calculated as closing O-NWC minus opening
O-NWC from two already calculated levels. The inputs must have the same company
CIK, policy ID, policy version, calculation formula, actual ordered
component/side/normalized-metric perimeter, and exact USD unit, with the closing date
strictly after the opening date. Inputs are never sorted. Actual fiscal dates
are preserved without assumptions about calendar years or year length. Each
change retains both full level results, including their component-level SEC
provenance. A policy/perimeter change raises a domain error instead of becoming
an apparent working-capital movement.
