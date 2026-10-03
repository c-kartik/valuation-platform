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
  `ReceivablesNetCurrent` approved only for COST CIK `909832`. Costco's balance
  is retained as a required operating asset because it is substantially
  operating receivables, but it is a mixed caption that also contains
  tax-related amounts and is not a perfectly pure operating-working-capital
  balance.
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
- Accrued Revenue-Share Liability: filing-level issuer extension
  `AccruedRevenueShare`, approved only for GOOGL CIK `1652044` under the
  Google issuer namespace whose date exactly matches the selected 10-K report
  date. It represents a current
  operating obligation to distribution and network partners and is presented
  separately from accounts payable, deferred revenue, and employee liabilities.
  The selected-accession fact must be nondimensional, non-nil, instant, exact
  USD, and end on the selected report date.
- Accrued Customer Liabilities: filing-level issuer extension
  `AccruedCustomerLiabilitiesCurrent`, approved only for GOOGL CIK `1652044`
  under the Google issuer namespace dated to the selected 10-K report date. It
  is an additional required operating current liability, distinct from both
  `ContractWithCustomerLiabilityCurrent` and `AccruedRevenueShare`.

`AccountsNotesAndLoansReceivableNetCurrent` and broad other-current-asset or
liability concepts are not approved fallbacks. The policies do not infer
economically absent balances as zero and do not claim universal issuer coverage.

Across the 25-period corpus, live validation resolved Vendor Non-Trade
Receivables 5/25 overall, covering all 5/5 applicable Apple periods with 20
non-applicable periods typed missing. Employee-Related Liabilities resolved
20/25 overall, covering all 20/20 applicable META, GOOGL, MSFT, and COST periods
with five Apple periods typed missing. Member Rewards Liability resolved 5/25
overall, covering all 5/5 applicable Costco periods with 20 non-applicable
periods typed missing. No result was ambiguous. GOOGL accrued revenue share
additionally resolved 5/5 applicable periods from exact selected-filing XBRL
evidence: $8.996bn, $8.370bn, $8.876bn, $9.802bn, and $10.864bn for 2021–2025.
GOOGL accrued customer liabilities resolved all 5/5 applicable periods from
their original selected-filing XBRL artifacts at $3.505bn, $3.619bn, $4.140bn,
$4.304bn, and $5.029bn for 2021–2025. These balances are not yet combined into
an Operating NWC amount.

META trade accounts payable uses a CIK-specific adjustment to exclude investing
balances:

```text
PP&E in trade AP = combined PP&E payable - separately accrued PP&E
Adjusted trade AP = reported trade AP - PP&E in trade AP
```

Reported trade AP is `us-gaap:AccountsPayableTradeCurrent` from Company Facts.
Combined PP&E payable is
`us-gaap:CapitalExpendituresIncurredButNotYetPaid` from Company Facts, and
separately accrued PP&E is the filing-XBRL extension
`PropertyAndEquipmentAccruedLiabilitiesCurrent`. The combined concept is tagged
as a full-year duration because META presents it in supplemental non-cash
investing and financing disclosures, but the filing wording identifies PP&E
incurred and remaining in accounts payable and accrued current liabilities at
the reporting date. It is accepted only as special META derivation evidence for
the exact selected accession and actual fiscal-year duration. That duration is
evaluated only against observations of the configured target concept: exactly
one eligible current-FY duration ending on the selected report date resolves,
while multiple eligible target observations remain ambiguous. Unrelated
duration facts do not define its period, actual start and end dates are
preserved, and no calendar-year length is assumed. It is not a direct
balance-sheet primitive. Generic instant eligibility is unchanged.

The validated 2021–2025 adjusted trade AP values are $2.071bn, $4.592bn,
$2.957bn, $3.142bn, and $3.965bn. All three source facts and both subtraction
steps remain in provenance. The two PP&E operands are not separate O-NWC
liabilities, preventing double counting. META remains incomplete because other
accrued liabilities remain methodologically unresolved.
Apple accrued distribution and marketing remains unresolved because exact
selected-accession coverage is only 1/5; a later-filed comparative is not
reassigned to an earlier accession.

Company Facts remains the primary balance-sheet source. Filing-level XBRL is
used only by an explicit source policy and supplied to normalization on demand.
Broad accrued and other-current-liability residuals remain excluded.

Annual Operating NWC equals approved required operating current assets minus
approved required operating current liabilities. Annual change in Operating
NWC is derived as the closing annual level minus the opening annual level. A
positive change is an increase in operating NWC; the future FCFF calculation
will subtract it. No sign inversion is applied in the change calculation. The
methodology uses a hybrid distinction:
strict reconstruction completeness asks whether the relevant operating current-
account structure has been cleanly reconstructed, while valuation readiness
asks whether every mandatory component in an explicitly approved issuer
perimeter is usable for one period. A reported zero is resolved evidence;
missing, non-applicable, and unresolved are separate states and never become
zero.

Initial versioned perimeters require the individually evidenced operating
drivers selected for each issuer. Mixed residual captions can remain outside a
valuation perimeter without automatically blocking readiness, but they remain
visible reconstruction limitations. Their exclusion is not economically
neutral: any excluded balance and its year-over-year movement will also be
absent from eventual Operating NWC and change in Operating NWC. Historical and
forecast methodology must therefore use the same perimeter. A perimeter version
changes only when included components or mandatory treatment changes in a way
that changes calculation semantics.

COST is ready across all five selected periods under version `1`. META version
`1` requires current customer contract liabilities and therefore is not ready
for 2025. The selected 2025 filing reports $1.080bn of total deferred revenue
but does not quantify the exact current portion; qualitative disclosure that
most will be realized within one year does not support manufacturing that
balance or substituting the total amount. Historical current balances were
small relative to revenue, but that evidence is not proof of immateriality.

META version `2` instead uses a stable measurable perimeter comprising
operating receivables, adjusted trade accounts payable, and employee-related
liabilities. Customer contract liabilities remain genuine operating
liabilities, but are outside this valuation perimeter for every historical and
forecast period. Their reported historical values remain normalized and are
not changed or treated as zero. Their balances, and therefore their movements,
will be absent from future META Operating NWC, change in Operating NWC, and FCFF
under version `2`. This is a consistent perimeter choice, not proof that the
excluded balance is economically irrelevant. META v2 removes this perimeter
blocker while strict reconstruction remains incomplete; each period must still
resolve every remaining required normalized component.

GOOGL remains blocked by unresolved trade AP treatment and the inventory
perimeter decision. MSFT remains blocked by trade AP treatment. AAPL remains
blocked by employee-liability and distribution-and-marketing decisions. These
are explicit methodology blockers, not invented missing SEC observations.

Broad residual formulas remain prohibited. Cash, investments, debt, taxes,
accrued PP&E purchases, finance leases, and strategic component-purchase
receivables are excluded from initial Operating NWC policies where applicable.
Operating-lease current liabilities are also explicitly excluded while an
integrated treatment of lease amortization, liabilities, interest, ROU assets,
Capex, and FCFF remains deferred. The current policies intentionally leave all
five validation issuers reconstruction-incomplete. They do not all have the
same valuation-readiness status, and neither readiness nor completeness performs
numerical arithmetic.

The calculator uses exact `Decimal` arithmetic without rounding. Required
source balances preserve their reported magnitudes. Each asset has a positive
signed contribution and each liability has a negative signed contribution;
the stored source balance itself is not negated. Explicit zero is valid.
Missing, ambiguous, or methodology-blocked periods do not produce partial
amounts. Components outside the selected policy perimeter do not participate,
and their omission does not mean their economic balance is zero. Results retain
the selected filing, exact policy ID/version, ordered contributions, and each
underlying direct or derived normalized result. Live validation calculates META
v2 and COST v1 for all five selected periods. The META levels for 2021–2025 are
$8.816bn, $4.283bn, $6.553bn, $7.502bn, and $8.653bn; the COST levels are
-$8.063bn, -$6.166bn, -$7.312bn, -$7.783bn, and -$9.200bn. GOOGL, MSFT, and
AAPL remain blocked. Historical and forecast calculations must
continue to use the same issuer perimeter.

Annual changes require the same company CIK, exact valuation policy ID and
version, calculation formula, and actual ordered component/side/normalized-
metric perimeter on both retained level results. Policy identity alone is not
trusted when explicit policy objects are supplied. A perimeter change is not an economic
working-capital cash flow and is rejected. Calculations use actual opening and
closing fiscal dates, exact `Decimal` subtraction, and no annualization,
interpolation, calendar-year assumption, or rounding. The result retains both
complete O-NWC levels and their component-level provenance. Five currently
validated annual levels produce four adjacent changes because the earliest
level has no preceding opening level. ΔNWC is derived from normalized balances;
it is not a directly reported SEC cash-flow fact.

Live annual ΔNWC for META v2 is -$4.533bn, $2.270bn, $0.949bn, and
$1.151bn for 2022–2025. COST v1 is $1.897bn, -$1.146bn, -$0.471bn, and
-$1.417bn for its corresponding 2022–2025 fiscal periods. GOOGL, MSFT, and AAPL
remain blocked before level calculation and therefore have no annual ΔNWC
output.

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
