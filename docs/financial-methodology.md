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

### Initial Annual Direct Normalization

The initial normalization scope covers direct annual Revenue, Operating Income,
Depreciation and Amortization (D&A), and Capex values from selected exact 10-K
filings. It does not cover interim normalization or derived quarters.

Revenue uses this ordered candidate policy:

1. `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
2. `us-gaap:Revenues`

Operating Income currently uses:

1. `us-gaap:OperatingIncomeLoss`

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
annual periods each for META, GOOGL, MSFT, AAPL, and COST. Direct D&A was
validated for all five selected periods of META, AAPL, and COST, producing
15/25 direct coverage across the same corpus. MSFT requires separate derived
component arithmetic that is not implemented, and GOOGL remains financially
unresolved. These are initial evidence-based policies, not a claim of universal
issuer coverage.
`us-gaap:SalesRevenueNet` and issuer extensions are intentionally excluded
pending selected-filing evidence.

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
META, AAPL, and COST periods, but not GOOGL or MSFT. A Revenue-style fallback is
financially inappropriate because depreciation and amortization may be
components rather than substitutes. MSFT has evidence supporting a future
derived methodology, which is not implemented in the direct normalization
layer. GOOGL remains unresolved because some periods combine impairment with
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
