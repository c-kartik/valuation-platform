# Financial Methodology

## Purpose

This document defines the financial concepts and calculation methodology used by the valuation platform.

Financial definitions should remain consistent across SEC normalization, historical analysis, forecasting, and valuation.

## Historical Financials

Historical financial data should primarily come from official SEC EDGAR/XBRL filings.

The standardized historical schema should eventually include:

- Revenue
- EBIT / operating income
- Taxes
- Depreciation & amortization
- Capital expenditures
- Operating net working capital
- Change in operating net working capital
- Cash and investments
- Debt
- Diluted shares outstanding

Exact XBRL concept mappings will be documented as the SEC normalization pipeline is developed and validated.

### Initial Annual Normalization

The initial normalization scope covers direct annual Revenue, Operating Income,
Pretax Income, Income Tax Expense, Depreciation and Amortization (D&A), and
Capex values from selected exact 10-K filings. It does not cover interim
normalization or derived quarters.

Revenue uses this ordered candidate policy:

1. `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
2. `us-gaap:Revenues`

Operating Income currently uses:

1. `us-gaap:OperatingIncomeLoss`

Pretax Income is the reported continuing-operations income before income taxes
and uses exactly:

1. `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`

Income Tax Expense is the reported GAAP provision or benefit and uses exactly:

1. `us-gaap:IncomeTaxExpenseBenefit`

Both are historical accounting facts. The SEC-reported sign is preserved, so a
tax benefit may be negative. Neither metric is the FCFF operating tax rate.
Cash taxes and current/deferred tax components remain outside this normalization
milestone. The eventual forecast operating tax rate remains a manually entered
analytical assumption informed by, but not mechanically equal to, historical
reported tax evidence.

Reported Effective Tax Rate is a derived historical accounting diagnostic:

```text
Reported ETR = Income Tax Expense / Pretax Income
```

It uses the already-normalized direct monetary results rather than selecting
Company Facts concepts again. The ratio is calculated with a 34-digit local
`Decimal` context, retained without presentation rounding, and expressed in
unit `pure`. A negative pretax-income denominator retains the mathematical ratio
with a `negative_denominator` diagnostic. A zero denominator returns typed
missing, while any nonzero denominator is calculated without an arbitrary
near-zero threshold. Negative tax benefits and rates above 100% retain their
reported signs and magnitudes.

`us-gaap:EffectiveIncomeTaxRateContinuingOperations` is validation evidence
only. Its presentation-rounded percentage is not substituted for the calculated
ratio or retained as confirming provenance. Reported ETR is not automatically
used as the FCFF/NOPAT tax rate or as a forecast assumption.

For FCFF, D&A means recurring depreciation of operating PP&E plus amortization
of finite-lived intangible assets. Direct annual D&A uses exactly:

1. `us-gaap:DepreciationDepletionAndAmortization`

Depreciation and amortization component concepts are not equivalent fallbacks;
they may become operands in a later derived layer only after completeness and
non-overlap are established. Impairments, stock compensation, restructuring,
unspecified other noncash charges, and unsupported finance-lease adjustments
are excluded from this direct policy.

Finance-lease amortization is not mechanically added to direct D&A. Broader
finance-lease treatment is deferred until an integrated methodology addresses
lease amortization, lease liabilities and debt, lease interest, and Capex
consistently, avoiding an isolated lease adjustment that could distort FCFF.

Capex is the cash expenditure to acquire property, plant and equipment and uses:

1. `us-gaap:PaymentsToAcquirePropertyPlantAndEquipment`

Capex is preserved as a positive expenditure magnitude. The later FCFF
calculation will subtract it. PP&E additions, capital expenditures incurred but
not yet paid, productive-asset purchases, acquisitions, intangible purchases,
lease additions, and issuer extensions are not approved alternatives.

META's 2022 and 2023 primary cash-flow presentation reports net PP&E purchases,
while `PaymentsToAcquirePropertyPlantAndEquipment` reports gross purchases. The
initial FCFF methodology intentionally uses the SEC fact's gross cash PP&E
purchases and does not adjust it to reproduce the net presentation.

The Revenue, Operating Income, and Capex policies were validated against five
annual periods each for META, GOOGL, MSFT, AAPL, and COST. Direct D&A covers all
five selected periods of META, AAPL, and COST. For Microsoft CIK `789019` only,
an evidence-backed derived policy adds same-period Company Facts observations
for `us-gaap:Depreciation` and
`us-gaap:AmortizationOfIntangibleAssets`. Direct D&A takes precedence, and a
direct ambiguity is not replaced by derivation. Together, direct and approved-
derived D&A provide 20/25 evidence-backed periods across the corpus. GOOGL
remains financially unresolved. These are initial evidence-based policies, not
a claim of universal issuer coverage.
`us-gaap:SalesRevenueNet` and issuer extensions are intentionally excluded
pending selected-filing evidence.

The Pretax Income and Income Tax Expense policies were also validated for five
selected annual periods each across META, GOOGL, MSFT, AAPL, and COST. All 50
values resolved directly and reproduced the selected filings' consolidated
income-statement amounts. This evidence supports the initial policies but is
not a claim of universal issuer coverage.

The derived Reported ETR also resolved for all 25 periods and agreed with the
SEC structured rate after normal filing-presentation rounding. All live periods
had positive, nonzero pretax income and positive tax expense; negative, zero,
near-zero, and above-100% cases are covered with synthetic tests rather than
claimed as live observations.

An annual candidate must be a numeric, exact-USD, current duration whose end
date equals the selected 10-K report date. The SEC observation's actual start
and end dates define the economic period; normalization does not assume calendar
years or 365/366-day durations.

The highest-priority concept with a valid annual observation is selected. A
lower-priority concept is used only when higher-priority concepts lack a valid
observation for that period. Equal values from another configured concept with
the same unit, start, and end are retained as confirming provenance. Conflicting
same-period USD values or multiple valid USD starts remain explicitly ambiguous
rather than being selected silently. Non-USD observations are unsupported in
this slice and do not participate when a valid USD candidate exists; if no
valid USD candidate exists, the metric is missing.

## Annual Balance-Sheet Primitives

Balance-sheet primitives are point-in-time snapshots and use a separate instant
normalization path. A candidate must belong to the selected 10-K accession, be
current and instant with no start date, end on the selected report date, use
exact USD, and contain a numeric non-Boolean value. Actual balance dates are
preserved. Zero is a reported balance; an absent fact remains missing.

The initial policies are:

- Operating Receivables: `AccountsReceivableNetCurrent`, with
  `ReceivablesNetCurrent` approved only for COST CIK `909832`.
- Vendor Non-Trade Receivables:
  `NontradeReceivablesCurrent`, approved only for Apple CIK `320193`.
- Inventory: `InventoryNet` only.
- Trade Accounts Payable: `AccountsPayableCurrent`, with
  `AccountsPayableTradeCurrent` approved only for META CIK `1326801`.
- Customer Contract Liabilities: `ContractWithCustomerLiabilityCurrent`, with
  `DeferredRevenueCurrent` approved only for COST CIK `909832`.
- Employee-Related Liabilities: `EmployeeRelatedLiabilitiesCurrent`, approved
  for META CIK `1326801`, GOOGL CIK `1652044`, MSFT CIK `789019`, and COST CIK
  `909832`. Apple remains missing rather than using a broad accrual caption.
- Member Rewards Liability: `AccruedLiabilitiesCurrent`, approved only for COST
  CIK `909832`, where selected filing evidence identifies the caption as member
  rewards. The generic concept is not treated as member rewards for other
  issuers.

`AccountsNotesAndLoansReceivableNetCurrent` and broad other-current-asset or
liability concepts are not approved fallbacks. The policies do not infer
economically absent balances as zero and do not claim universal issuer coverage.

Across the 25-period corpus, live validation resolved Vendor Non-Trade
Receivables 5/25 overall, covering all 5/5 applicable Apple periods with 20
non-applicable periods typed missing. Employee-Related Liabilities resolved
20/25 overall, covering all 20/20 applicable META, GOOGL, MSFT, and COST periods
with five Apple periods typed missing. Member Rewards Liability resolved 5/25
overall, covering all 5/5 applicable Costco periods with 20 non-applicable
periods typed missing. No result was ambiguous. GOOGL accrued revenue share and
Apple accrued distribution and marketing remain future filing-XBRL research
candidates.

Operating NWC will eventually be derived from classified operating components.
Neither Operating NWC nor its year-over-year change is implemented. Cash,
investments, debt, taxes, leases, and mixed residual balances remain outside
this milestone, and the Current Assets minus Current Liabilities shortcut is
not used.

## Source vs. Derived Values

Values obtained directly from SEC filings should remain distinguishable from values calculated by the platform.

Each normalized value should preserve sufficient metadata to identify its source, including where applicable:

- XBRL concept
- Filing/accession
- Fiscal period
- Form type
- Filing date
- Unit

Derived values should record the calculation used to produce them.

Missing values must not be silently invented.

### D&A Research Status

Direct `DepreciationDepletionAndAmortization` normalization covers the selected
META, AAPL, and COST periods. A Revenue-style fallback remains financially
inappropriate because depreciation and amortization may be components rather
than substitutes. MSFT's approved derived values preserve both reported
components and their addition in provenance; the policy is restricted to CIK
`789019` rather than generalized to every issuer exposing those concepts.
GOOGL remains unresolved because some periods combine impairment with
depreciation or amortization and later periods do not establish complete
amortization coverage. Filing-level XBRL remains an explicit research source
and is not automatically connected to normalization.

## FCFF

The core valuation methodology is unlevered free cash flow to the firm (FCFF).

```text
NOPAT = EBIT × (1 - Tax Rate)

FCFF = NOPAT
       + D&A
       - Capital Expenditures
       - Change in Operating NWC
