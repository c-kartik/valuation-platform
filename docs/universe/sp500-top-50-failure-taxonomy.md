# S&P 500 Top 50 failure taxonomy

## Scope and evidence

This artifact records the Phase 1H.3 analysis of the production smoke test at
commit `3bca2f61ac4db335a334b88c502274aea2509cee`. The frozen input remains
`sp500-top-50-2026-10-02.csv`: 51 securities, 50 SEC issuers, 43 generic
pipeline attempts, and seven specialized-methodology skips. A fresh read-only
diagnostic on 2026-10-06 reproduced 41 standardized-output executions, two
Company Facts failures, 40 five-period histories, and XOM's empty history.

The analysis does not change a parser, selector, concept policy, financial
methodology, or issuer result. A missing value is not zero. A possible concept
match is evidence for research, not approval to normalize it.

## Operational taxonomy

| Category | Meaning | Observed evidence |
|---|---|---|
| `RETRIEVAL` | SEC transport or artifact retrieval failed | No corpus-wide instance in this run |
| `TICKER_CIK_IDENTITY` | The ticker identity does not lead to the registrant history needed by the pipeline | XOM |
| `FILING_SELECTION` | Correct-identity filings exist but the selector cannot identify the requested periods | No independent selector defect established; XOM's empty selection is downstream of identity |
| `COMPANY_FACTS_SCHEMA` | A legitimate SEC JSON representation violates a parser schema assumption | GEV and SNDK zero-padded string CIKs |
| `CONCEPT_POLICY` | Evidence uses an unapproved concept, an overly narrow CIK scope, or competing approved concepts | Cash, investments, debt, pretax income, Capex, and revenue conflicts |
| `ISSUER_EXTENSION` | Required evidence exists only in an issuer taxonomy or filing-level artifact | A research path for several missing statement facts; no repeatable extension family is approved yet |
| `DIMENSIONAL_CONTEXT` | Facts require explicit member/context handling | No new standalone blocker proved by the Company Facts artifact; filing-XBRL research remains necessary |
| `DERIVATION` | Direct evidence is absent and a complete, nonoverlapping derivation must be established | D&A components and downstream reported ETR |
| `PERIOD_ASSOCIATION` | One accession contains multiple durations ending on the report date | JNJ, ABBV, GE, and ORCL ambiguities |
| `METHODOLOGY_BLOCKER` | Extraction works, but accounting treatment or valuation perimeter is unresolved | GOOGL, MSFT, and AAPL O-NWC |
| `EXPECTED_TYPED_MISSING` | Filing evidence establishes economic absence or non-applicability under the approved methodology | Some debt or investment balances after filing confirmation; no corpus result is assigned this category merely because a fact is absent |
| `OTHER` | A root cause does not fit the operational categories | None currently identified |

`GENERALIZATION_REQUIRED` is an issuer-level planning conclusion, not a root
cause.

## Issuer-blocking diagnoses

### GEV and SNDK: Company Facts schema

Ticker resolution and filing selection are correct. GEV resolves to CIK
1996810 and selects 2024 and 2025; SNDK resolves to CIK 2023554 and selects
2025 and 2026. Their raw Company Facts identities are respectively
`"0001996810"` and `"0002023554"`. SEC returns both as ten-digit,
zero-padded strings.

The parser currently accepts a nonnegative integer or a canonical unpadded
decimal string, then requires equality with the requested CIK. It rejects a
leading-zero string before equality is tested. The two failures are therefore
one `COMPANY_FACTS_SCHEMA` issue, not issuer-specific problems.

The narrow Phase 1H.4 candidate is to accept either the existing canonical
decimal representation or an exact ten-digit ASCII-decimal representation
equal to `company.cik_padded`, normalize it to an integer, and retain the
existing equality check. Whitespace, signs, non-digits, arbitrary leading-zero
forms, and mismatched CIKs must remain invalid. Other issuers can expose the
same legal SEC representation, so the change belongs in the shared parser.

### XOM: ticker/CIK succession

The current official ticker dataset resolves XOM to CIK 2115436,
`ExxonMobil Holdings Corp`. That CIK's submissions response has 34 recent
rows, no exact 10-K, one 10-Q, and no supplemental history files. The 10-Q is
cross-listed as accession `0000034088-26-000093`, whose accession owner is
legacy CIK 34088. The filing contains both CIK identities and explicitly states
that ExxonMobil Holdings became the publicly traded parent and successor
registrant. These are observed SEC facts; the production resolver does not yet
interpret them.

CIK 34088 is `EXXON MOBIL CORP`; its submissions history contains the required
2021–2025 10-Ks and its Company Facts entity is `Exxon Mobil Corporation`. The
old CIK currently has no ticker in its submissions identity. The selector
therefore correctly returns zero annual filings for current CIK 2115436. This
is a `TICKER_CIK_IDENTITY` registrant-succession problem, not a reason to relax
filing selection or hardcode XOM to CIK 34088.

Phase 1H.4 must complete a registrant-succession identity-linkage design before
resolver code is changed. The design must:

- begin with the current CIK from the official SEC ticker dataset;
- use only official SEC evidence, including submissions metadata, filing
  accession ownership, filing cover-page or inline-XBRL registrant identities,
  and explicit predecessor/successor disclosures;
- treat cross-listing as evidence to investigate, never as sufficient authority
  to traverse to another CIK, because joint filings, multiple registrants, and
  parent/subsidiary arrangements can also produce cross-listed filings;
- require explicit authoritative succession, predecessor/successor status, or
  an equivalently strong SEC-documented legal-continuity relationship before a
  filing-owner CIK can supply historical continuity;
- reject multiple plausible registrants or any linkage that cannot be
  established deterministically as an explicit identity ambiguity or
  unresolved result;
- reject ticker equality as proof of continuity, protecting against unrelated
  ticker reuse; and
- remain reusable, without an `XOM -> 34088` mapping, fuzzy company-name
  matching, or another issuer hardcode.

Only after that design is independently reviewed should generic identity
handling be implemented. If official SEC evidence cannot support a reliable
general rule, XOM must remain unresolved.

## Standardized measure coverage

The denominator is 200 issuer-periods: 40 completed issuers with five annual
periods. XOM, GEV, SNDK, and specialized issuers do not contribute measures.

| Measure | Possible | Resolved | Missing | Ambiguous | Methodology blocked | Not comparable | Direct | Derived | Calculated | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Revenue | 200 | 178 | 0 | 22 | 0 | 0 | 178 | 0 | 0 | 89.0% |
| Operating income | 200 | 165 | 35 | 0 | 0 | 0 | 165 | 0 | 0 | 82.5% |
| Pretax income | 200 | 154 | 45 | 1 | 0 | 0 | 154 | 0 | 0 | 77.0% |
| Income-tax expense | 200 | 200 | 0 | 0 | 0 | 0 | 200 | 0 | 0 | 100.0% |
| Reported effective tax rate | 200 | 154 | 45 | 1 | 0 | 0 | 0 | 154 | 0 | 77.0% |
| D&A | 200 | 110 | 90 | 0 | 0 | 0 | 105 | 5 | 0 | 55.0% |
| Capex | 200 | 145 | 55 | 0 | 0 | 0 | 145 | 0 | 0 | 72.5% |
| Diluted weighted-average shares | 200 | 192 | 8 | 0 | 0 | 0 | 189 | 3 | 0 | 96.0% |
| Cash and cash equivalents | 200 | 25 | 175 | 0 | 0 | 0 | 25 | 0 | 0 | 12.5% |
| Short-term investments | 200 | 25 | 175 | 0 | 0 | 0 | 25 | 0 | 0 | 12.5% |
| Long-term marketable securities | 200 | 5 | 195 | 0 | 0 | 0 | 5 | 0 | 0 | 2.5% |
| Commercial paper | 200 | 12 | 188 | 0 | 0 | 0 | 12 | 0 | 0 | 6.0% |
| Short-term borrowings | 200 | 1 | 199 | 0 | 0 | 0 | 1 | 0 | 0 | 0.5% |
| Current portion of long-term debt | 200 | 114 | 86 | 0 | 0 | 0 | 113 | 1 | 0 | 57.0% |
| Long-term debt, noncurrent | 200 | 138 | 62 | 0 | 0 | 0 | 135 | 3 | 0 | 69.0% |
| Operating NWC | 200 | 10 | 175 | 0 | 15 | 0 | 0 | 0 | 10 | 5.0% |
| Change in Operating NWC | 200 | 8 | 140 | 0 | 12 | 40 | 0 | 0 | 8 | 4.0% |

The table reconciles to 3,400 standardized measures: 1,636 resolved, 1,673
missing, 24 ambiguous, 27 methodology-blocked, and 40 not-comparable.

## Issuer status frequencies

Counts below cover the 17 standardized measures for each selected annual
period. Stage failures and XOM's empty history have no measure denominator.

| Issuer | Periods | Resolved | Missing | Ambiguous | Methodology blocked | Not comparable | Pipeline result |
|---|---:|---:|---:|---:|---:|---:|---|
| NVDA | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| AAPL | 5 | 70 | 5 | 0 | 9 | 1 | complete |
| MSFT | 5 | 62 | 13 | 0 | 9 | 1 | complete |
| AMZN | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| GOOGL | 5 | 60 | 15 | 0 | 9 | 1 | complete |
| AVGO | 5 | 41 | 43 | 0 | 0 | 1 | complete |
| META | 5 | 63 | 21 | 0 | 0 | 1 | complete |
| MU | 5 | 30 | 54 | 0 | 0 | 1 | complete |
| TSLA | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| AMD | 5 | 42 | 42 | 0 | 0 | 1 | complete |
| LLY | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| XOM | 0 | 0 | 0 | 0 | 0 | 0 | empty history |
| JNJ | 5 | 42 | 39 | 3 | 0 | 1 | complete |
| V | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| INTC | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| WMT | 5 | 40 | 39 | 5 | 0 | 1 | complete |
| ABBV | 5 | 30 | 49 | 5 | 0 | 1 | complete |
| MA | 5 | 38 | 45 | 1 | 0 | 1 | complete |
| CSCO | 5 | 50 | 34 | 0 | 0 | 1 | complete |
| LRCX | 5 | 38 | 46 | 0 | 0 | 1 | complete |
| PLTR | 5 | 41 | 43 | 0 | 0 | 1 | complete |
| AMAT | 5 | 44 | 40 | 0 | 0 | 1 | complete |
| CVX | 5 | 20 | 59 | 5 | 0 | 1 | complete |
| COST | 5 | 70 | 14 | 0 | 0 | 1 | complete |
| CAT | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| MRK | 5 | 38 | 46 | 0 | 0 | 1 | complete |
| PG | 5 | 46 | 38 | 0 | 0 | 1 | complete |
| KO | 5 | 46 | 38 | 0 | 0 | 1 | complete |
| GE | 5 | 23 | 57 | 4 | 0 | 1 | complete |
| PM | 5 | 28 | 56 | 0 | 0 | 1 | complete |
| HD | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| NFLX | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| KLAC | 5 | 37 | 47 | 0 | 0 | 1 | complete |
| TXN | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| GEV | 0 | 0 | 0 | 0 | 0 | 0 | Company Facts failure |
| SNDK | 0 | 0 | 0 | 0 | 0 | 0 | Company Facts failure |
| ORCL | 5 | 24 | 59 | 1 | 0 | 1 | complete |
| LIN | 5 | 34 | 50 | 0 | 0 | 1 | complete |
| IBM | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| QCOM | 5 | 45 | 39 | 0 | 0 | 1 | complete |
| VZ | 5 | 35 | 49 | 0 | 0 | 1 | complete |
| PEP | 5 | 40 | 44 | 0 | 0 | 1 | complete |
| MCD | 5 | 34 | 50 | 0 | 0 | 1 | complete |

## High-frequency evidence patterns

### Cash and investments

The cash policy is intentionally scoped to the five seed CIKs. The exact
standard `CashAndCashEquivalentsAtCarryingValue` fact is structurally eligible
in 183 periods across 38 issuers. After the 25 seed resolutions, 158 currently
missing issuer-periods already contain that same evidence. This is the clearest
high-frequency, low-interpretation `CONCEPT_POLICY` generalization candidate.
The remaining 17 missing periods need separate presentation research.

The current short-term-investment candidates appear in 121 periods across 25
issuers, including two periods with overlapping candidates, while only 25
periods resolve. Long-term candidate families appear in 60 periods across 14
issuers, while five resolve. These are not safe missing-to-zero cases: concept
semantics, overlap, restricted cash, equity investments, and current/noncurrent
classification must be reviewed before widening policy.

### D&A

D&A resolves in 110/200 periods: 105 direct and five through the approved MSFT
derivation. Ninety periods across 19 issuers remain missing.

- `DepreciationAndAmortization` appears in 46 periods across ten issuers,
  including repeated gaps for V, LRCX, LIN, and VZ. Its relationship to the
  approved D&A definition must be verified before a general fallback.
- `DepreciationAmortizationAndAccretionNet` appears in all five WMT, MA, and GE
  periods. Accretion makes it a distinct methodology case, not an equivalent
  fallback.
- `Depreciation` appears in 141 periods and
  `AmortizationOfIntangibleAssets` in 139, but completeness and nonoverlap are
  issuer- and period-dependent. The MSFT derivation cannot be generalized by
  concept presence alone.
- GOOGL still lacks sufficient complete direct/component evidence under the
  approved methodology.
- No repeatable issuer-extension D&A family was present in Company Facts for
  the missing issuers. Filing-level XBRL may provide evidence, but that remains
  explicit research. Impairment and lease amortization are not silently added.

### Operating NWC

META and COST produce ten O-NWC levels and eight comparable changes. GOOGL,
MSFT, and AAPL produce 15 methodology-blocked levels and 12 blocked changes.
The 35 newly completed issuers have no valuation-perimeter policy, producing
175 missing levels and 140 missing changes. Each of the 40 first periods is
correctly not comparable.

Raw standard facts demonstrate why a universal residual formula is unsafe:
`AccountsReceivableNetCurrent` is eligible in 166 periods,
`InventoryNet` in 171, `AccountsPayableCurrent` in 182, and
`ContractWithCustomerLiabilityCurrent` in 94. Absence can reflect sector
economics or a concept variant. Retail, pharmaceutical, asset-light payment,
technology, industrial, and energy issuers require evidence-backed component
classification; broad residual current-asset/liability captions remain
excluded.

### Debt

Current debt resolves in 114 periods and noncurrent debt in 138. Evidence for
common unapproved variants is widespread:

- `DebtCurrent` appears in 73 periods across 16 issuers.
- `LongTermDebtAndCapitalLeaseObligationsCurrent` appears in 41 periods across
  nine issuers.
- `LongTermDebtAndCapitalLeaseObligations` appears in 60 periods across 13
  issuers.
- `CommercialPaper` appears in 57 periods across 13 issuers while the current
  scoped policy resolves 12.
- `OtherShortTermBorrowings` appears in 16 periods across four issuers while
  the current scoped policy resolves one.

Some variants combine leases, current maturities, or total debt, and 57
current-debt periods expose more than one candidate family. They require
carrying-value and overlap analysis. Missing commercial paper, borrowings, or
debt may also be genuine zero/absence; no zero is inferred and no total-debt
fallback is proposed.

### Shares and core flow measures

Diluted weighted-average shares resolve in 192/200 periods. V has no matching
Company Facts fact in its five selected filings. MCD resolves two periods, but
three later facts are floating values such as `751.8` in a `shares` unit and
fail the integer/share-basis boundary. Both need filing-level scale and
presentation research. GOOGL's three A+C derivations and two direct periods
remain unchanged; historical weighted-average shares remain distinct from the
future DCF denominator.

Income-tax expense resolves 200/200. Revenue has no missing periods, but 22
ambiguities. Operating income is missing in 35 periods across LLY, JNJ, CVX,
MRK, GE, KLAC, and IBM. Pretax income is missing in 45 periods and ambiguous in
one; reported ETR mirrors that upstream state. Several missing pretax issuers
report the standard minority-interest/equity-method variant, making it a
candidate for explicit semantic research. Capex is missing in 55 periods; the
common `PaymentsToAcquireProductiveAssets` and industry-specific PP&E concepts
are broader or different from the approved gross PP&E cash-purchase definition
and are not automatic fallbacks. No new sign defect was observed.

## Ambiguity inventory

All 24 ambiguous outputs come from selected 10-K accessions. No amendment or
cross-accession collision is involved.

| Issuer | Report date | Selected accession | Measure | Candidates | Candidate concepts | Result reason |
|---|---|---|---|---:|---|---|
| JNJ | 2023-12-31 | `0000200406-24-000013` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax` ×2 | `multiple_annual_periods` |
| JNJ | 2023-12-31 | `0000200406-24-000013` | Pretax income | 2 | `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` ×2 | `multiple_annual_periods` |
| JNJ | 2023-12-31 | `0000200406-24-000013` | Reported ETR | 2 | The two ambiguous pretax operands | `incompatible_derivation_operands` |
| WMT | 2022-01-31 | `0000104169-22-000012` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `conflicting_concept_values` |
| WMT | 2023-01-31 | `0000104169-23-000020` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| WMT | 2024-01-31 | `0000104169-24-000056` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| WMT | 2025-01-31 | `0000104169-25-000021` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| WMT | 2026-01-31 | `0000104169-26-000055` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| ABBV | 2021-12-31 | `0001551152-22-000007` | Revenue | 3 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` ×2 | `multiple_annual_periods` |
| ABBV | 2022-12-31 | `0001551152-23-000011` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ABBV | 2023-12-31 | `0001551152-24-000011` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ABBV | 2024-12-31 | `0001551152-25-000020` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ABBV | 2025-12-31 | `0001551152-26-000008` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| MA | 2021-12-31 | `0001141391-22-000023` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `conflicting_concept_values` |
| CVX | 2021-12-31 | `0000093410-22-000019` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `conflicting_concept_values` |
| CVX | 2022-12-31 | `0000093410-23-000009` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| CVX | 2023-12-31 | `0000093410-24-000013` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| CVX | 2024-12-31 | `0000093410-25-000009` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| CVX | 2025-12-31 | `0000093410-26-000078` | Revenue | 2 | Same two concepts | `conflicting_concept_values` |
| GE | 2021-12-31 | `0000040545-22-000008` | Revenue | 3 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` ×2 | `multiple_annual_periods` |
| GE | 2022-12-31 | `0000040545-23-000023` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| GE | 2023-12-31 | `0000040545-24-000027` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| GE | 2024-12-31 | `0000040545-25-000015` | Revenue | 3 | Same three concept observations | `multiple_annual_periods` |
| ORCL | 2022-05-31 | `0001564590-22-023675` | Revenue | 2 | `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` | `multiple_annual_periods` |

The 11 WMT/MA/CVX cases are `CONCEPT_POLICY` conflicts. The JNJ, ABBV, GE,
and ORCL cases are `PERIOD_ASSOCIATION` conflicts caused by same-end,
different-start durations; the JNJ ETR ambiguity is a downstream `DERIVATION`
result. All candidates use the selected accession and its official Company
Facts URL; the table preserves the accession and concept provenance needed to
reproduce each case. Company Facts does not retain dimensional context, so the
evidence does not justify attributing these cases to dimensions.

## Methodology-blocked and expected missing

All 27 methodology-blocked outputs are intentional O-NWC states: five levels
and four changes each for GOOGL, MSFT, and AAPL. They are not parser or
extraction failures. The first change for every one of the 40 histories is
`NOT_COMPARABLE`, accounting for all 40 such states. `NOT_COMPARABLE` is its
own standardized-output status and is not a missing result or a form of
`EXPECTED_TYPED_MISSING`.

`EXPECTED_TYPED_MISSING` requires affirmative filing evidence of economic
absence or non-applicability. Potential candidates, only after affirmative
filing confirmation, include no commercial paper, short-term borrowing,
current debt, or long-term marketable securities in a particular period. In
contrast, CIK-scoped policies that ignore an otherwise eligible fact,
unapproved standard variants, absent issuer-level O-NWC policy, and
period/concept conflicts are generalization gaps. The 1,673 missing results are
not relabeled wholesale: unresolved cases remain missing until filing evidence
establishes the correct category.

## Issuer-level post-smoke classification

`SUPPORTED` requires expected history and no material technical or policy gap
in core standardized output. The classification is a Phase 1H planning result;
it does not alter the frozen snapshot or production policy.

| Issuer | Classification | Primary evidence |
|---|---|---|
| NVDA | `GENERALIZATION_REQUIRED` | Cash/O-NWC scope and Capex gap |
| AAPL | `GENERALIZATION_REQUIRED` | O-NWC methodology blocker |
| MSFT | `GENERALIZATION_REQUIRED` | O-NWC methodology blocker |
| AMZN | `GENERALIZATION_REQUIRED` | Pretax, Capex, cash, and O-NWC gaps |
| GOOGL | `GENERALIZATION_REQUIRED` | D&A and O-NWC methodology blockers |
| AVGO | `GENERALIZATION_REQUIRED` | D&A, debt, cash, and O-NWC gaps |
| META | `SUPPORTED` | Five-period core output and valuation-ready O-NWC |
| MU | `GENERALIZATION_REQUIRED` | Pretax, debt, cash, and O-NWC gaps |
| TSLA | `GENERALIZATION_REQUIRED` | D&A, debt, cash, and O-NWC gaps |
| AMD | `GENERALIZATION_REQUIRED` | D&A, debt, cash, and O-NWC gaps |
| BRK-B | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial/conglomerate methodology |
| LLY | `GENERALIZATION_REQUIRED` | Operating income, Capex, debt, cash, and O-NWC gaps |
| JPM | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| XOM | `GENERALIZATION_REQUIRED` | Ticker/CIK registrant succession blocks history |
| JNJ | `GENERALIZATION_REQUIRED` | Period ambiguity, operating income, cash, and O-NWC gaps |
| V | `GENERALIZATION_REQUIRED` | Shares, D&A, Capex, cash, and O-NWC gaps |
| INTC | `GENERALIZATION_REQUIRED` | D&A, cash, and O-NWC gaps |
| WMT | `GENERALIZATION_REQUIRED` | Revenue ambiguity, D&A, cash, and O-NWC gaps |
| ABBV | `GENERALIZATION_REQUIRED` | Revenue-period ambiguity, D&A, debt, cash, and O-NWC gaps |
| MA | `GENERALIZATION_REQUIRED` | Revenue conflict, pretax, D&A, cash, and O-NWC gaps |
| CSCO | `GENERALIZATION_REQUIRED` | Cash/investment and O-NWC scope |
| LRCX | `GENERALIZATION_REQUIRED` | D&A, Capex, cash, debt, and O-NWC gaps |
| PLTR | `GENERALIZATION_REQUIRED` | Cash, debt, and O-NWC scope |
| AMAT | `GENERALIZATION_REQUIRED` | Partial D&A/debt plus cash and O-NWC gaps |
| CVX | `GENERALIZATION_REQUIRED` | Revenue conflict and multiple core concept gaps |
| COST | `SUPPORTED` | Five-period core output and valuation-ready O-NWC |
| CAT | `GENERALIZATION_REQUIRED` | Pretax, current debt, cash, and O-NWC gaps |
| MRK | `GENERALIZATION_REQUIRED` | Operating income, D&A, Capex, cash, and O-NWC gaps |
| BAC | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| PG | `GENERALIZATION_REQUIRED` | Partial pretax plus cash and O-NWC gaps |
| UNH | `SPECIALIZED_METHODOLOGY_REQUIRED` | Insurance/specialized methodology |
| KO | `GENERALIZATION_REQUIRED` | Debt, cash, and O-NWC gaps |
| GE | `GENERALIZATION_REQUIRED` | Revenue-period ambiguity and operating-income/D&A/debt gaps |
| PM | `GENERALIZATION_REQUIRED` | Pretax, D&A, debt, cash, and O-NWC gaps |
| HD | `GENERALIZATION_REQUIRED` | Capex, debt, cash, and O-NWC gaps |
| NFLX | `GENERALIZATION_REQUIRED` | Current debt, cash, and O-NWC gaps |
| KLAC | `GENERALIZATION_REQUIRED` | Operating income, debt, cash, and O-NWC gaps |
| TXN | `GENERALIZATION_REQUIRED` | D&A, cash, and O-NWC gaps |
| GEV | `GENERALIZATION_REQUIRED` | Company Facts zero-padded CIK schema blocker |
| GS | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| SNDK | `GENERALIZATION_REQUIRED` | Company Facts zero-padded CIK schema blocker |
| ORCL | `GENERALIZATION_REQUIRED` | Revenue period, pretax, D&A, debt, cash, and O-NWC gaps |
| WFC | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| MS | `SPECIALIZED_METHODOLOGY_REQUIRED` | Financial-institution methodology |
| LIN | `GENERALIZATION_REQUIRED` | Pretax, D&A, cash, and O-NWC gaps |
| IBM | `GENERALIZATION_REQUIRED` | Operating income, D&A, current debt, cash, and O-NWC gaps |
| QCOM | `GENERALIZATION_REQUIRED` | Capex, cash, and O-NWC gaps |
| VZ | `GENERALIZATION_REQUIRED` | D&A, Capex, debt, cash, and O-NWC gaps |
| PEP | `GENERALIZATION_REQUIRED` | Capex, current debt, cash, and O-NWC gaps |
| MCD | `GENERALIZATION_REQUIRED` | Share scale, pretax, current debt, cash, and O-NWC gaps |

Reconciliation: two `SUPPORTED`, 41 `GENERALIZATION_REQUIRED`, and seven
`SPECIALIZED_METHODOLOGY_REQUIRED`, totaling 50 issuers. All 43 generic
issuers have one post-smoke classification.

## Ranked generalization backlog

| Priority | Root cause | Evidence / affected scope | Blocking scope | Candidate fix | Generalizability | Accounting risk |
|---:|---|---|---|---|---|---|
| 1 | `COMPANY_FACTS_SCHEMA` | GEV and SNDK; four selected periods | Entire issuer | Strict ten-digit padded-string CIK support with equality protection | High | Low |
| 2 | `TICKER_CIK_IDENTITY` | XOM; intended five-year history | Entire issuer | Design and validate deterministic SEC registrant-succession linkage; implement only if generalizable and ambiguity-safe | Medium-high | Medium |
| 3 | `CONCEPT_POLICY` | Cash: 175 missing; 158 have exact eligible standard facts | One high-value balance | Generalize exact cash policy beyond seed CIKs | Very high | Low |
| 4 | `CONCEPT_POLICY` / `PERIOD_ASSOCIATION` | Revenue: 22 ambiguities across seven issuers | Core flow metric | Separate full-year selection from genuine concept-definition conflicts | High | Medium-high |
| 5 | `CONCEPT_POLICY` | Pretax: 45 missing + one ambiguous; ETR mirrors it | Core flow and diagnostic | Research approved standard pretax variants and period rules | High | Medium |
| 6 | `CONCEPT_POLICY` / `ISSUER_EXTENSION` | Operating income: 35 missing across seven issuers | Core FCFF input | Filing-level face-statement concept inventory | Medium | High |
| 7 | `DERIVATION` / `CONCEPT_POLICY` | D&A: 90 missing across 19 issuers | Core FCFF input | Group combined concepts and complete component derivations | High | High |
| 8 | `CONCEPT_POLICY` | Capex: 55 missing across 12 issuers | Core FCFF input | Validate productive-asset and industry PP&E concepts against definition | Medium-high | High |
| 9 | `CONCEPT_POLICY` | Short investments: 175 missing, 121 periods with candidate families; long investments: 195 missing, 60 candidate periods | Equity bridge | Evidence-backed current/noncurrent investment policies | High | Medium-high |
| 10 | `CONCEPT_POLICY` / `DERIVATION` | Current debt 86 missing; noncurrent 62; widespread combined variants | Equity bridge | Carrying-value, lease, and overlap-aware variants | High | High |
| 11 | `CONCEPT_POLICY` | Commercial paper 188 missing with 57 raw facts; short borrowings 199 with 16 raw facts | Equity bridge | Generalize exact concepts only where economically present | High | Medium |
| 12 | `METHODOLOGY_BLOCKER` | 35 issuers without O-NWC policy; three blocked seed policies | O-NWC and change | Sector-clustered component research and versioned perimeters | Medium | Very high |
| 13 | `CONCEPT_POLICY` / filing evidence | V five share gaps; MCD three scale/type gaps | Per-share history | Filing-XBRL denominator and scale validation | Low-medium | Medium |

## Recommended Phase 1H.4 waves

1. **Infrastructure/schema blockers:** first implement and test strict padded
   Company Facts CIK normalization. Next complete and independently review the
   registrant-succession identity-linkage design above. Implement generic
   identity handling only if the resulting rule is deterministic,
   generalizable, and ambiguity-safe; otherwise keep XOM unresolved. Re-run
   GEV, SNDK, and XOM before touching financial policy.
2. **High-frequency, low-risk standard facts:** generalize exact cash evidence;
   then separate revenue full-year period association from true concept
   conflicts and research pretax variants.
3. **Core FCFF flows:** investigate operating-income face-statement evidence,
   D&A groups, and Capex variants. Approve only repeatable definitions with
   selected-accession evidence.
4. **Equity-bridge balances:** generalize investments, commercial paper,
   borrowings, and debt with explicit overlap, lease, and absence rules.
5. **Narrow evidence-backed policies:** address V/MCD shares and any filing-XBRL
   issuer extensions; build O-NWC perimeters by repeatable sector/component
   clusters rather than residual formulas.
6. **Corpus rerun and reclassification:** reproduce all counts, preserve typed
   absence and ambiguity, and reassess issuer classifications before Phase
   1H.5.
