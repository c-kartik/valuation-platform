# Financial Methodology

## Purpose

This document defines the financial concepts and calculation methodology used by the valuation platform.

Financial definitions should remain consistent across SEC normalization, historical analysis, forecasting, and valuation.

## Operating-Company Methodology Scope

The initial valuation framework is designed for ordinary operating companies:

```text
Revenue
→ EBIT
→ NOPAT
+ D&A
− Capex
− Change in Operating NWC
= FCFF
```

This structure is appropriate for many technology, consumer, industrial,
communications, healthcare, and other non-financial operating businesses. It
is not automatically appropriate for every industry.

For banks, deposits and wholesale funding are operating inputs, interest is a
core operating result, conventional operating NWC is not comparable, and
regulatory capital is central. Insurers require specialized treatment of
reserves, claims, float, investment portfolios, underwriting economics, and
regulatory capital. REITs and other specialized structures may also require
dedicated normalization and valuation methods. Those methods are not defined
in the current milestone, and such companies must not be forced into the
generic FCFF framework.

Historical support remains evidence-driven. A supported pipeline run need not
resolve every metric: missing remains missing, ambiguity remains ambiguity,
and methodology blockers remain explicit with filing provenance intact.

## Manual Forecast Assumptions

The initial forecast design uses five explicit ordinal periods rather than
invented calendar dates. Each period is identified by an index from 1 through
5 and a descriptive fiscal-year label, allowing calendar, June, September, and
52/53-week issuers to use the same assumption model.

All rates are manually supplied finite `Decimal` fractions. Each year contains
revenue growth, operating margin, forecast tax rate, D&A as a percentage of
revenue, Capex as a positive expenditure percentage of revenue, and change in
Operating NWC as a percentage of revenue. Positive forecast ΔNWC will later be
a use of cash; negative ΔNWC will be a source of cash. Direct ΔNWC assumptions
avoid making unresolved historical O-NWC a forecast-readiness blocker.
Rate inputs must already be finite `Decimal` instances; integers, floats,
strings, and other numeric representations are rejected rather than coerced.

The assumption set contains one constant manual WACC and one terminal-growth
rate with terminal growth strictly below WACC. It does not calculate Gordon
Growth terminal value. Historical reported ETR, tax expense, and operating-tax
readiness do not populate the manual forecast tax rate. Loss-period tax
treatment must be defined explicitly before a future forecast calculator can
calculate NOPAT for negative EBIT.

Historical diluted weighted-average shares are not a valuation-share policy.
Valuation share count, cash/debt adjustments, and the enterprise-to-equity
bridge remain separate future methodology decisions.

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
- Diluted weighted-average shares

Exact XBRL concept mappings will be documented as the SEC normalization pipeline is developed and validated.

### Initial Annual Normalization

The initial normalization scope covers direct annual Revenue, Operating Income,
Pretax Income, Income Tax Expense, Depreciation and Amortization (D&A), and
Capex values from selected exact 10-K filings. It does not cover interim
normalization or derived quarters.

Revenue uses this ordered candidate policy:

1. `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
2. `us-gaap:Revenues`

Direct Operating Income uses:

1. `us-gaap:OperatingIncomeLoss`

Wave 13 reviewed all 35 then-remaining gaps across LLY, JNJ, CVX, MRK, GE, KLAC,
and IBM in [the Operating Income concept inventory](operating-income-concepts.md).
None of the exact selected
consolidated face statements reports an Operating Income, Income from
Operations, or Operating Profit subtotal. None has an exact annual
nondimensional filing-XBRL Operating Income fact or an exact selected-accession
Company Facts observation. GE's 2024 and 2025 `OperatingIncomeLoss` facts are
dimensioned segment and reconciliation facts, not a consolidated subtotal.
Expense totals, gross profit, Pretax Income, segment profit, and component lines
remain non-equivalent. The generic policy is unchanged, safe direct coverage is
zero, and all 35 periods remained missing at that research baseline.

Component derivation is a separate methodology question. No derivation is
approved until consolidated completeness, operating versus non-operating scope,
signs, and non-overlap are established for every operand. Wave 14's
[Operating Income derivation design](operating-income-derivation-design.md)
establishes that evidence for the 25 exact LLY/JNJ/MRK/KLAC/IBM accessions and
reaches PARTIAL GO for a future curated exact-accession policy. It defines
Operating Income as consolidated continuing-operations revenue less the
complete operating cost perimeter, including acquired IPR&D, restructuring,
and operating-asset impairments, while excluding interest and reviewed other
non-operating activity. IBM service cost remains embedded in operating
expenses; its separately disclosed non-service pension components remain in
Other and are excluded. IBM IP/custom-development income is operating only in
the reviewed IBM perimeter.

Each approved equation builds forward from Revenue or a separately reconciled
Gross Profit and then bridges candidate Operating Income to Pretax through all
excluded face-statement items. Pretax-minus-residual derivations remain
prohibited. Issuer expense aggregates that mix operating and non-operating
items are validation checkpoints, not Operating Income. The evidence approves
no generic concept fallback, future filing, CVX equation, or GE equation, and
Wave 16 implements only the separately reviewed exact-accession policy and
model design.

Wave 15's
[curated derivation-policy design](operating-income-derivation-policy-design.md)
approves the production boundary implemented in Wave 16. The immutable
`operating_income_component_derivation_v1` registry contains only the 25 exact
reviewed CIK/accession/period equations. It preserves ordered signed operands,
every confirming and reviewed-nonselected occurrence, calculation and Pretax-
bridge evidence, and exact arithmetic. The generic `OperatingIncomeLoss`
policy remains first. A direct ambiguity is never replaced; equal complete
direct and derived values may confirm, while differing values remain
ambiguous. Future, amended, unregistered, incomplete, dimensioned-only, nil,
non-USD, or conflicting evidence cannot create a result.

IBM's three one-million Pretax variances are validation-only consequences of
independently reported whole-million face lines. The exact derived Operating
Income is never rounded, plugged, or changed, and the reported/calculated
values, signed variance, and scale remain provenance. The tolerance does not
generalize beyond the five registered IBM filings. The Operating Tax path
accepts a derived Operating Income only with complete active-version policy
provenance and all existing tax-policy gates; the derivation alone never
approves tax allocation or NOPAT.

Wave 16 verifies all 25 registered forward component equations and independent
Pretax bridges. Operating Income is 194 resolved (169 direct and 25 derived) /
10 missing / 0 ambiguous. CVX and GE remain missing; no integrated-energy,
segment-profit or business-perimeter assumption is added. KLAC's 2023 absence
is a reviewed face-row completeness assertion, not an inferred zero: its
non-face USD-zero impairment occurrence is retained as nonselected evidence
and is not consumed by arithmetic. LLY's lower-precision occurrences likewise
cannot replace the exact approved face facts. Tax-policy readiness gates are
unchanged; derived Operating Income alone is insufficient for Operating Tax or
NOPAT. The [verified results](operating-income-derivation-policy-design.md#wave-16-implementation-and-verified-results)
record the exact positive/control and corpus reconciliation.

Pretax Income is the reported continuing-operations income before income taxes
and uses exactly:

1. `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`

Wave 12 does not change that generic concept policy. The separately versioned
`pretax_scope_equivalence_v1` policy approves the differently scoped standard
candidate only for three MA and five CVX accessions where reviewed filing
evidence establishes that equity-method activity is inside consolidated
Pretax. Current-concept precedence remains intact, and exact CIK, accession,
authoritative annual dates, taxonomy, concept, exact-USD unit, and approved
classification must match. Future, amended, malformed, or unregistered filings
remain missing.

Equivalent repeated nondimensional filing-XBRL occurrences confirm one result
only when their complete semantic signature and exact `Decimal` value agree.
Every original context, unit ID, raw value, decimals value, nil status, and
source reference remains in deterministic provenance. Dimensioned facts are
excluded; different eligible values remain ambiguous; structural
inconsistencies are data errors. The same candidate remains non-equivalent in
20 reviewed periods and mixed in five LIN periods, so concept presence, issuer
history, statement membership, ETR plausibility, or numerical size cannot
establish equivalence. Live validation resolves only the eight registered
periods, leaving all 25 controls and 12 issuer-extension periods missing.
Pretax is now 167 resolved / 37 missing / 0 ambiguous across the 204-period
corpus.

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

When the Pretax operand is policy-approved, Reported ETR retains that operand's
policy ID, version, reviewed-evidence references, and complete ordered
filing-XBRL occurrence provenance. Wave 12 therefore adds exactly the eight
corresponding Reported ETR resolutions, producing 167 resolved / 37 missing /
0 ambiguous Reported ETR periods without changing its calculation.

### Cash and Investments

Historical normalization preserves gross reported liquidity and investment
captions rather than deciding what is excess or available to equity holders.
Cash and cash equivalents use
`us-gaap:CashAndCashEquivalentsAtCarryingValue` for the validated META, GOOGL,
MSFT, AAPL, and COST CIKs. The metric means the reported balance-sheet caption;
it is not labeled unrestricted cash. Combined cash/restricted-cash facts and
cash fair-value disclosures are not fallbacks.

Short-term investments use issuer-scoped concepts. META, GOOGL, and AAPL use
`us-gaap:MarketableSecuritiesCurrent`; META alone may fall back to
`us-gaap:AvailableForSaleSecuritiesDebtSecuritiesCurrent` for its 2021 selected
filing. MSFT and COST use `us-gaap:ShortTermInvestments`.
`CashCashEquivalentsAndShortTermInvestments` is not a primitive and is not
arithmetically decomposed. Apple CIK `320193` alone normalizes
`us-gaap:MarketableSecuritiesNoncurrent` as long-term marketable securities.

All three metrics use the existing exact selected-accession, current instant,
report-date, USD, integer non-Boolean rules. Missing is distinct from zero, and
conflicting eligible concepts remain ambiguous. Restricted cash and restricted
investments are not subtracted or normalized in this milestone. Non-marketable,
equity-method, venture, and other strategic investments remain outside scope.
No unrestricted-cash, excess-cash, universal liquid-assets subtotal, or
enterprise-value-to-equity-value bridge is calculated. Those require later
valuation policies and explicit treatment of restriction overlap, operating
cash needs, liquidity discounts, and possible tax leakage.

### Debt

Annual debt normalization preserves four gross reported primitives at carrying
value: `CommercialPaper`, COST CIK `909832` only
`OtherShortTermBorrowings`, `LongTermDebtCurrent`, and
`LongTermDebtNoncurrent`. The usual exact selected-accession, current instant,
report-date, USD, integer non-Boolean rules apply. Explicit zero is evidence;
absence and narrative immateriality remain missing.

GOOGL CIK `1652044` uses two narrow Company Facts derivations for its selected
2021–2023 filings. Current long-term debt equals
`LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities` minus
`LongTermDebtAndCapitalLeaseObligations`, minus
`FinanceLeaseLiabilityCurrent`, minus
`DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet`. Non-current
long-term debt equals `LongTermDebtAndCapitalLeaseObligations` minus the
non-current finance-lease liability, where that lease amount is
`FinanceLeaseLiability` minus `FinanceLeaseLiabilityCurrent`. These identities
reproduce the selected filings' debt-note carrying values without classifying
finance leases as conventional funded debt. They are accession scoped,
direct-first, and retain every operand; conflicting direct and derived evidence
is ambiguous. In the current identity, the selected filings present the
unamortized discount/issuance-cost fact as a positive contra amount, so it is
subtracted once from the face-value debt remainder. The non-current combined
balance already reflects that contra amount; its separate identity therefore
removes only the non-current finance-lease balance and does not subtract the
discount a second time.

`LongTermDebt`, fair values, maturity-schedule principal, revolver availability,
and combined debt-and-lease concepts are not direct substitutes. Notes, secured
debt, convertible debt, and foreign-currency notes are not added separately to
current/non-current carrying debt. Commercial paper is kept separate, and COST
commercial paper is not substituted for its evidenced bank borrowing. No total
debt or net debt is calculated. Finance and operating lease treatment remains
deferred until Capex, lease amortization, lease interest, and lease liabilities
can be handled consistently in FCFF and valuation.

### Diluted Weighted-Average Shares

`DILUTED_WEIGHTED_AVERAGE_SHARES` is the GAAP diluted EPS denominator reported
for a selected fiscal year. Direct normalization uses only
`us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding`, exact unit `shares`,
an integer non-Boolean Company Facts value, and the exact selected 10-K's current
annual duration ending on its report date. Output is an exact `Decimal`; actual
calendar, non-calendar, 52-week, and 53-week dates are preserved.

Direct Company Facts resolves 22 of the 25 validated periods. GOOGL CIK
`1652044` selected 2021–2023 filings use an approved filing-XBRL derivation:
Class A diluted denominator plus Class C diluted denominator. The Class A
calculation already assumes conversion of Class B, so Class B is not added
again. Both operands must have the exact selected accession and annual period,
standard diluted-share concept, shares unit, and approved class dimension; the
Class C issuer-member namespace must match the selected report date. All
operand dimensions and filing provenance are retained.

Each value preserves the share basis reported in the original selected filing.
GOOGL 2021 therefore remains 677,674,000 shares on its pre-20-for-1-split basis;
later restated comparative facts do not replace it. No split-restated series is
created. The 25-period validation produced 22 direct and three derived results,
with no missing, ambiguity, or value mismatch.

This metric is not basic weighted-average shares, period-end shares,
treasury-stock-method incremental shares, or a current or forecast fully diluted
valuation share count. RSUs, options, contingently issuable shares, convertibles,
and antidilutive securities are not separately added. A future value-per-share
denominator requires a distinct policy for current shares, future dilution, and
buybacks.

### Standardized Historical Company Output

The standardized annual output aligns actual fiscal-year duration measures with
the selected filing's closing instant balances without treating those balances
as durations. It preserves the selected accession, actual dates, exact units,
direct/derived/calculated identity, compact SEC source references, and versioned
Operating NWC policy metadata. Missing, ambiguous, not-comparable, and
methodology-blocked states remain distinct. Exact `Decimal` values serialize as
strings; millions, billions, percentages, and localized formatting are
presentation concerns.

Operating NWC and its change enter only from the existing approved calculation
results. The first displayed period has no invented change without an opening
level. Cash, investment, and debt primitives remain separate: the output does
not create total cash, excess cash, total debt, net debt, or an equity bridge.
Reported tax diagnostics remain available, but historical operating tax and
NOPAT are not manufactured. Diluted Weighted-Average Shares remains the
historical GAAP EPS denominator rather than a forecast valuation-share count.

### Signed Tax Reconciliation Evidence

The signed tax-evidence layer records what a selected filing's reconciliation
reports. Each displayed sign requires explicit evidence from the filing table
or a reliable calculation relationship; raw XBRL magnitude is retained
separately and never determines that sign. Rate bridges preserve percentage
points, pretax income, and the Decimal tax amount derived from the displayed
rate. Dollar bridges preserve the filing's signed currency amounts. Both retain
row order and validate against the reported ETR or provision using disclosed
precision, without adding a synthetic balancing row. Because the evidence model
does not identify which displayed terms were rounded, its tolerance conservatively
counts the starting value, each row, and the reported total at the declared
precision. Normalized rows enforce source identity and rate/dollar arithmetic;
signs supported by a calculation relationship require an auditable rationale.

Missing evidence, ambiguous signs, competing sources, conflicts, and unresolved
methodology remain explicit. This layer does not approve operating-tax
treatment, calculate operating tax or NOPAT, or populate a forecast tax
assumption. Reported ETR remains an accounting diagnostic.

### Operating-Tax Readiness

The operating-tax readiness foundation evaluates whether signed tax evidence
could support a future policy-adjusted tax on reported Operating Income. It
requires an exact versioned issuer policy, an evidenced statutory starting
rate, compatible normalized Operating Income and Pretax Income, explicit
currency/scale conversion, complete row treatment, and complete exclusive
membership for paired effects. Diagnostic treatment fields in tax evidence do
not become approved policy automatically.

No materiality waiver, foreign-credit allocation, combined-SBC estimate, or
analytical EBIT adjustment is implemented. Zero or negative Operating Income,
negative Pretax Income, and unresolved benefit realizability remain blocked;
the system does not monetize losses or manufacture tax benefits. Explicit zero
adjustments remain valid evidence. The current 25 validation periods remain
blocked by unresolved methodology. Operating-tax expense and NOPAT are not yet
calculated, and the forecast operating tax rate remains a manual assumption.

### Historical Operating-Tax Attribution

Historical operating-tax methodology uses strict direct linkage. A complete
jurisdictional or reconciliation adjustment may enter tax on reported Operating
Income only when its tax effect is explicitly linked to income inside reported
Operating Income or the filing supplies an exact reproducible operating
allocation. Paired gross-tax and credit effects also require complete pair
membership, evidence of a common regime and income base, and explicit Operating
Income linkage. Any adjustment that does not meet these conditions remains
`METHODOLOGY_UNRESOLVED`.

A recurring caption, a state or foreign label, net presentation, or the absence
of disclosed contamination does not establish operating attribution. The
methodology also prohibits proportional allocation using Operating Income and
Pretax Income, revenue or geographic allocation without a matching disclosed
tax base, and applying a reconciliation percentage directly to Operating
Income.

Percentage-point reconciliation rows are first dollarized using their reported
Pretax Income denominator. Because that denominator can include interest,
investment, financing, and other non-operating income or expense, the resulting
tax amount cannot generally be transferred to Operating Income. Missing
historical operating tax is not estimated to complete a valuation.

Historical operating tax and historical NOPAT are optional analytical outputs.
Reported Income Tax Expense, Reported ETR, signed reconciliation evidence, and
typed operating-tax readiness remain available even when strict linkage cannot
produce an operating-tax amount. The current validation corpus may legitimately
remain methodology-blocked. Forecast FCFF instead uses a separately entered
forecast operating tax-rate assumption; historical operating-tax or NOPAT
availability is not a prerequisite for forecast assumptions or DCF readiness.

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
exact USD, and contain an integer non-Boolean value. Actual balance dates are
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
```

For forecast FCFF, the tax rate is a manual analytical assumption rather than
an automatic substitution of Reported ETR or an estimate manufactured from
methodology-blocked historical reconciliation rows. Historical operating tax
and NOPAT may supplement analysis when strict direct linkage resolves, but are
not required to run the forecast or DCF.
