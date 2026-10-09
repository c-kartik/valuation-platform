# Operating Income component-derivation evidence design

## Scope and decision

Phase 1H.4 Wave 14 reviews the 25 exact selected 10-K periods that Wave 13
identified for component research: five each for LLY, JNJ, MRK, KLAC, and IBM.
CVX and GE are outside this pass. Every equation below is bound to the frozen
CIK, accession, authoritative annual dates, consolidated face-statement role,
annual nondimensional exact-USD facts, and filer-submitted calculation
relationships.

The decision is **PARTIAL GO**:

- all 25 periods are `DERIVATION_APPROVED` under exact-accession evidence;
- the five recurring equations reproduce Revenue-to-Operating-Income and
  Operating-Income-to-Pretax bridges without an unexplained residual;
- 22 Pretax bridges reconcile exactly and IBM 2022, 2023, and 2025 differ by
  only $1 million because independently rounded face-statement lines are
  presented in whole millions;
- the approved economic treatment is stable within each issuer for all five
  periods, but changing concepts and issuer-specific presentation prevent a
  generic cross-issuer concept policy; and
- safe potential coverage is 25 exact periods. Future, amended, or unregistered
  filings remain missing. CVX and GE remain unresolved.

This is research and design only. Production remains Operating Income 169
resolved / 35 missing / 0 ambiguous, and no source, test, or policy changes are
made by this wave.

## Economic definition and operating perimeter

For this design, Operating Income is consolidated continuing-operations
revenue less the complete face-statement costs of producing that revenue and
the recurring or period-recognized operating costs reported above financing
and other non-operating activity. It includes cost of revenue, SG&A, R&D,
acquired IPR&D charged to earnings, restructuring, and operating asset
impairments. It excludes interest income, interest expense, debt-extinguishment
gains or losses, securities and investment gains or losses, non-service pension
components, divestiture gains, and other income or expense that the exact
filing identifies as non-operating.

The derivation is never `Pretax - residual`. Each result is built forward from
Revenue (or from reported Gross Profit after independently reconciling Revenue
less cost of revenue), then independently bridged to reported Pretax using
every excluded face-statement item. Reported issuer expense aggregates are
checkpoints only; because they mix operating and non-operating items, they are
not Operating Income operands.

All monetary values below are exact XBRL `Decimal` values expressed in USD
millions. A positive value on an expense line is displayed without parentheses
and subtracted unless noted. Parentheses on an income line mean the displayed
amount reduces expense. For credit-balance `NonoperatingIncomeExpense` and
`OtherNonoperatingIncomeExpense`, the XBRL numeric sign is positive for income
and negative for expense; the equations add that signed amount. IBM's
debit-balance `OtherIncomeAndExpense` / `OtherExpenseAndIncome` is subtracted,
so a negative value adds income. All operands are non-nil and nondimensional.

## Approved equations and concept inventories

### LLY

`OI = Revenue - Cost of sales - R&D - Marketing/selling/admin - acquired
IPR&D - impairment/restructuring/special charges`

`Pretax = OI + signed Other—net income (expense)`

| Key | Face caption | Exact taxonomy/concept | Display / XBRL treatment | Calculation relationship |
|---|---|---|---|---|
| R | Revenue | `us-gaap:Revenues` | income / positive; add | Pretax aggregate child, `+1` |
| C | Cost of sales | `us-gaap:CostOfGoodsAndServicesSold` | expense / positive; subtract | issuer total child, `+1` |
| D | Research and development | `us-gaap:ResearchAndDevelopmentExpense` (2021–2022); `us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost` (2023–2025) | expense / positive; subtract | issuer total child, `+1` |
| S | Marketing, selling, and administrative | `us-gaap:SellingGeneralAndAdministrativeExpense` | expense / positive; subtract | issuer total child, `+1` |
| A | Acquired IPR&D | `lilly:AcquiredInProcessResearchAndDevelopment` (2021); `lilly:AcquiredInProcessResearchAndDevelopmentAndDevelopmentMilestones` (2022); `us-gaap:ResearchAndDevelopmentAssetAcquiredOtherThanThroughBusinessCombinationWrittenOff` (2023–2025) | expense / positive; subtract | issuer total child, `+1` |
| X | Asset impairment, restructuring, and other special charges | `us-gaap:RestructuringSettlementAndImpairmentProvisions` | expense / positive; subtract | issuer total child, `+1` |
| N | Other—net, (income) expense | `us-gaap:NonoperatingIncomeExpense` | income positive, expense negative; add | issuer total child, `-1` |
| T | Income before income taxes | `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | income / signed | `R - CostOfSalesOperatingExpensesAndOtherNet` |

The filing-only `lilly:CostOfSalesOperatingExpensesAndOtherNet` exactly sums
`C + D + S + A + X - N`; it remains a validation aggregate, not Operating
Income. The 2023–2025 acquired-IPR&D concept has a second rounded occurrence in
the same annual context. The approved operand is the more precise face value
(`decimals=-5` in 2023–2024 and `-6` in 2025), which alone reproduces the
submitted calculation. The less precise cash-flow/note representation is
retained as conflicting occurrence evidence and must not silently replace the
face operand.

### JNJ

`Gross Profit = Sales - Cost of products sold`

`OI = Gross Profit - SG&A - R&D - IPR&D impairments - restructuring`

`Pretax = OI + interest income - interest expense + signed other non-operating
income (expense)`

| Key | Face caption | Exact taxonomy/concept | Display / XBRL treatment | Calculation relationship |
|---|---|---|---|---|
| R | Sales to customers | `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` | income / positive; add | Gross Profit child, `+1` |
| C | Cost of products sold | `us-gaap:CostOfGoodsAndServicesSold` | expense / positive; subtract | Gross Profit child, `-1` |
| G | Gross profit | `us-gaap:GrossProfit` | income / positive | `R - C` |
| S | Selling, marketing and administrative | `us-gaap:SellingGeneralAndAdministrativeExpense` | expense / positive; subtract | Pretax child, `-1` |
| D | Research and development | `us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost` | expense / positive; subtract | Pretax child, `-1` |
| A | In-process R&D / impairments | `us-gaap:ResearchAndDevelopmentInProcess` (2021–2022); `jnj:ResearchAndDevelopmentInProcess1` (2023–2025) | expense / positive; subtract | Pretax child, `-1` |
| X | Restructuring | `us-gaap:RestructuringCharges` | expense / positive; subtract | Pretax child, `-1` |
| H | Interest income | `us-gaap:InvestmentIncomeInterest` | displayed in parentheses / positive income; add | Pretax child, `+1` |
| E | Interest expense | `us-gaap:InterestExpense` (2021–2023); `us-gaap:InterestExpenseNonoperating` (2024–2025) | expense / positive; subtract | Pretax child, `-1` |
| N | Other (income) expense, net | `us-gaap:OtherNonoperatingIncomeExpense` | income positive, expense negative; add | Pretax child, `+1` |
| T | Earnings before provision for taxes | `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | income / signed | complete children above |

### MRK

`OI = Sales - Cost of sales - SG&A - R&D - restructuring`

`Pretax = OI + signed Other (income) expense, net`

| Key | Face caption | Exact taxonomy/concept | Display / XBRL treatment | Calculation relationship |
|---|---|---|---|---|
| R | Sales | `us-gaap:Revenues` | income / positive; add | Pretax child through issuer total |
| C | Cost of sales | `us-gaap:CostOfGoodsAndServicesSold` | expense / positive; subtract | issuer total child, `+1` |
| S | Selling, general and administrative | `us-gaap:SellingGeneralAndAdministrativeExpense` | expense / positive; subtract | issuer total child, `+1` |
| D | Research and development | `us-gaap:ResearchAndDevelopmentExpense` | expense / positive; subtract | issuer total child, `+1` |
| X | Restructuring costs | `us-gaap:RestructuringCharges` | expense / positive; subtract | issuer total child, `+1` |
| N | Other (income) expense, net | `us-gaap:OtherNonoperatingIncomeExpense` | income positive, expense negative; add | issuer total child, `-1` |
| T | Income before taxes | `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | income / signed | `R - CostsExpensesAndOther` |

`merck:CostsExpensesAndOther` exactly sums `C + S + D + X - N`; it is a
Pretax-reconciling aggregate and is not itself Operating Income.

### KLAC

`OI = Revenue - Cost of revenue - R&D - SG&A - operating impairment`

`Pretax = OI - interest expense + signed debt-extinguishment gain (loss) +
signed other non-operating income (expense)`

| Key | Face caption | Exact taxonomy/concept | Display / XBRL treatment | Calculation relationship |
|---|---|---|---|---|
| R | Revenues / Total revenues | `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` | income / positive; add | Pretax child, `+1` |
| C | Costs of revenues | `us-gaap:CostOfRevenue` | expense / positive; subtract | Pretax child, `-1` |
| D | Research and development | `us-gaap:ResearchAndDevelopmentExpense` | expense / positive; subtract | Pretax child, `-1` |
| S | Selling, general and administrative | `us-gaap:SellingGeneralAndAdministrativeExpense` | expense / positive; subtract | Pretax child, `-1` |
| I | Goodwill / goodwill and purchased-intangible impairment | `us-gaap:GoodwillImpairmentLoss` (2022); absent zero line (2023); `us-gaap:AssetImpairmentCharges` (2024–2026) | operating expense / positive; subtract; zero where reported | Pretax child, `-1` when present |
| E | Interest expense | `us-gaap:InterestExpense` (2022–2023); `us-gaap:InterestExpenseNonoperating` (2024–2026) | expense / positive; subtract | Pretax child, `-1` |
| L | Loss on extinguishment of debt | `us-gaap:GainsLossesOnExtinguishmentOfDebt` | loss negative, gain positive; add; no line in 2026 | Pretax child, `+1` when present |
| N | Other expense (income), net | `us-gaap:OtherNonoperatingIncomeExpense` | income positive, expense negative; add | Pretax child, `+1` |
| T | Income before income taxes | `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | income / signed | complete children above |

An absent 2023 impairment row and absent 2026 debt-extinguishment row are not
inferred zeros. They are absent from both face presentation and the submitted
calculation tree; the remaining disclosed children form the complete equation.

### IBM

`Gross Profit = Revenue - Cost`

`OI = Gross Profit - SG&A - R&D + IP/custom-development income`

`Pretax = OI - signed Other (income) and expense - interest expense`

| Key | Face caption | Exact taxonomy/concept | Display / XBRL treatment | Calculation relationship |
|---|---|---|---|---|
| R | Revenue | `us-gaap:Revenues` | income / positive; add | Gross Profit child, `+1` |
| C | Cost | `us-gaap:CostOfRevenue` | expense / positive; subtract | Gross Profit child, `-1` |
| G | Gross profit | `us-gaap:GrossProfit` | income / positive | `R - C` |
| S | Selling, general and administrative | `us-gaap:SellingGeneralAndAdministrativeExpense` | expense / positive; subtract | issuer total child, `+1` |
| D | Research, development and engineering | `us-gaap:ResearchAndDevelopmentExpense` | expense / positive; subtract | issuer total child, `+1` |
| A | Intellectual property and custom development income | `ibm:IntellectualPropertyAndCustomDevelopmentIncome` | displayed in parentheses / positive income; add | issuer total child, `-1` |
| N | Other (income) and expense | `ibm:OtherIncomeAndExpense` (2021–2023); `ibm:OtherExpenseAndIncome` (2024–2025) | debit-positive expense, negative income; subtract | issuer total child, `+1` |
| E | Interest expense | `us-gaap:InterestExpense` | expense / positive; subtract | issuer total child, `+1` |
| T | Income from continuing operations before income taxes | `us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | income / signed | `G - ExpenseAndOtherIncome` / `G - ExpenseAndIncomeOther` |

IBM's segment disclosure includes IP/custom-development income in
Infrastructure segment expense and other income, and defines the surrounding
aggregate as including recurring expense and income associated with normal
operations. It is therefore operating income in this exact issuer perimeter.
The separate Other line contains foreign-currency and derivative gains/losses,
interest income, securities/investment gains/losses, retirement-related
non-service amounts, divestiture gains, and miscellaneous other items; it is
excluded. IBM's retirement note separately places the non-service pension
components in Other. Service cost remains embedded in cost/SG&A/R&D and is
therefore operating. The filing evidence is available in the SEC-rendered
[2025 segment table](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/R39.htm),
[Other income note](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/R16.htm),
and [retirement note](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/R31.htm).

## Complete 25-period evidence matrix

The value columns list operands in the key order defined above. `OI`, `Bridge`,
and `T` are independently recalculated candidate Operating Income, calculated
Pretax, and reported Pretax. Each linked instance is the fact source; the face
statement proves caption/order and the calculation linkbase proves the stated
relationships and weights.

| Issuer / annual period | Selected accession; namespaces | Context; unit; decimals; dimensions | Exact operands (USD millions) | OI; Bridge; T; variance | Classification | SEC evidence |
|---|---|---|---|---|---|---|
| LLY 2021-01-01 / 2021-12-31 | `0000059478-22-000068`; `us-gaap@2021-01-31`, `lilly@20211231` | `i22de8effd1e0473ea9e6b2ebf9fa4dfd_D20210101-20211231`; `usd→USD`; `-5`; ∅ | R 28,318.4; C 7,312.8; D 7,025.9; S 6,431.6; A 874.9; X 316.1; N -201.6 | 6,357.1; 6,155.5; 6,155.5; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/lly-20211231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/lly-20211231_cal.xml) |
| LLY 2022-01-01 / 2022-12-31 | `0000059478-23-000082`; `us-gaap@2022`, `lilly@20221231` | `i095cf5e171c244d4957ecbd3f0e77a2d_D20220101-20221231`; `usd→USD`; `-5`; ∅ | R 28,541.4; C 6,629.8; D 7,190.8; S 6,440.4; A 908.5; X 244.6; N -320.9 | 7,127.3; 6,806.4; 6,806.4; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/lly-20221231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/lly-20221231_cal.xml) |
| LLY 2023-01-01 / 2023-12-31 | `0000059478-24-000065`; `us-gaap@2023` | `c-1`; `usd→USD`; `-5`; ∅ | R 34,124.1; C 7,082.2; D 9,313.4; S 7,403.1; A 3,799.8; X 67.7; N +96.7 | 6,457.9; 6,554.6; 6,554.6; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/lly-20231231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/lly-20231231_cal.xml) |
| LLY 2024-01-01 / 2024-12-31 | `0000059478-25-000067`; `us-gaap@2024` | `c-1`; `usd→USD`; `-5`; ∅ | R 45,042.7; C 8,418.3; D 10,990.6; S 8,593.8; A 3,280.4; X 860.6; N -218.6 | 12,899.0; 12,680.4; 12,680.4; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/lly-20241231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/lly-20241231_cal.xml) |
| LLY 2025-01-01 / 2025-12-31 | `0000059478-26-000013`; `us-gaap@2025` | `c-1`; `usd→USD`; `-6`; ∅ | R 65,179; C 11,052; D 13,337; S 11,094; A 2,910; X 484; N -571 | 26,302; 25,731; 25,731; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/lly-20251231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/lly-20251231_cal.xml) |
| JNJ 2021-01-04 / 2022-01-02 | `0000200406-22-000022`; `us-gaap@2021-01-31` | `i20918a3d76934ae3867fbaabde676443_D20210104-20220102`; `usd→USD`; `-6`; ∅ | R 93,775; C 29,855; G 63,920; S 24,659; D 14,714; A 900; X 252; H 53; E 183; N -489 | 23,395; 22,776; 22,776; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/200406/000020040622000022/jnj-20220102_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/200406/000020040622000022/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/200406/000020040622000022/jnj-20220102_cal.xml) |
| JNJ 2022-01-03 / 2023-01-01 | `0000200406-23-000016`; `us-gaap@2022` | `i0535b75a91b0440fba341aa27ca7ca13_D20220103-20230101`; `usd→USD`; `-6`; ∅ | R 94,943; C 31,089; G 63,854; S 24,765; D 14,603; A 783; X 321; H 490; E 276; N -1,871 | 23,382; 21,725; 21,725; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/200406/000020040623000016/jnj-20230101_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/200406/000020040623000016/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/200406/000020040623000016/jnj-20230101_cal.xml) |
| JNJ 2023-01-02 / 2023-12-31 | `0000200406-24-000013`; `us-gaap@2023`, `jnj@20231231` | `c-1`; `usd→USD`; `-6`; ∅ | R 85,159; C 26,553; G 58,606; S 21,512; D 15,085; A 313; X 489; H 1,261; E 772; N -6,634 | 21,207; 15,062; 15,062; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/200406/000020040624000013/jnj-20231231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/200406/000020040624000013/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/200406/000020040624000013/jnj-20231231_cal.xml) |
| JNJ 2024-01-01 / 2024-12-29 | `0000200406-25-000038`; `us-gaap@2024`, `jnj@20241229` | `c-1`; `usd→USD`; `-6`; ∅ | R 88,821; C 27,471; G 61,350; S 22,869; D 17,232; A 211; X 234; H 1,332; E 755; N -4,694 | 20,804; 16,687; 16,687; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/200406/000020040625000038/jnj-20241229_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/200406/000020040625000038/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/200406/000020040625000038/jnj-20241229_cal.xml) |
| JNJ 2024-12-30 / 2025-12-28 | `0000200406-26-000016`; `us-gaap@2025`, `jnj@20251228` | `c-1`; `usd→USD`; `-6`; ∅ | R 94,193; C 30,256; G 63,937; S 23,676; D 14,665; A 81; X 228; H 1,056; E 971; N +7,209 | 25,287; 32,581; 32,581; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/200406/000020040626000016/jnj-20251228_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/200406/000020040626000016/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/200406/000020040626000016/jnj-20251228_cal.xml) |
| MRK 2021-01-01 / 2021-12-31 | `0000310158-22-000003`; `us-gaap@2021-01-31` | `i090a240c01204951a8d43aeb0084e26c_D20210101-20211231`; `usd→USD`; `-6`; ∅ | R 48,704; C 13,626; S 9,634; D 12,245; X 661; N +1,341 | 12,538; 13,879; 13,879; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/mrk-20211231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/mrk-20211231_cal.xml) |
| MRK 2022-01-01 / 2022-12-31 | `0001628280-23-005061`; `us-gaap@2022` | `iaf8fc8dc60ac4ca6b59f2a42ad4a7b23_D20220101-20221231`; `usd→USD`; `-6`; ∅ | R 59,283; C 17,411; S 10,042; D 13,548; X 337; N -1,501 | 17,945; 16,444; 16,444; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/mrk-20221231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/mrk-20221231_cal.xml) |
| MRK 2023-01-01 / 2023-12-31 | `0001628280-24-006850`; `us-gaap@2023` | `c-1`; `usd→USD`; `-6`; ∅ | R 60,115; C 16,126; S 10,504; D 30,531; X 599; N -466 | 2,355; 1,889; 1,889; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000162828024006850/mrk-20231231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/310158/000162828024006850/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/310158/000162828024006850/mrk-20231231_cal.xml) |
| MRK 2024-01-01 / 2024-12-31 | `0001628280-25-007732`; `us-gaap@2024` | `c-1`; `usd→USD`; `-6`; ∅ | R 64,168; C 15,193; S 10,816; D 17,938; X 309; N +24 | 19,912; 19,936; 19,936; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000162828025007732/mrk-20241231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/310158/000162828025007732/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/310158/000162828025007732/mrk-20241231_cal.xml) |
| MRK 2025-01-01 / 2025-12-31 | `0000310158-26-000063`; `us-gaap@2025` | `c-1`; `usd→USD`; `-6`; ∅ | R 65,011; C 16,382; S 10,733; D 15,789; X 889; N -151 | 21,218; 21,067; 21,067; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000031015826000063/mrk-20251231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/310158/000031015826000063/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/310158/000031015826000063/mrk-20251231_cal.xml) |
| KLAC 2021-07-01 / 2022-06-30 | `0000319201-22-000023`; `us-gaap@2022` | `if1b7f5a910c24f34a1eb3d55c6507918_D20210701-20220630`; `usd→USD`; `-3`; ∅ | R 9,211.883; C 3,592.441; D 1,105.254; S 860.007; I 0; E 160.339; L 0; N -4.605 | 3,654.181; 3,489.237; 3,489.237; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/319201/000031920122000023/klac-20220630_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/319201/000031920122000023/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/319201/000031920122000023/klac-20220630_cal.xml) |
| KLAC 2022-07-01 / 2023-06-30 | `0000319201-23-000031`; `us-gaap@2023` | `c-1`; `usd→USD`; `-3`; ∅ | R 10,496.056; C 4,218.307; D 1,296.727; S 986.326; I absent; E 296.940; L -13.286; N +104.720 | 3,994.696; 3,789.190; 3,789.190; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/319201/000031920123000031/klac-20230630_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/319201/000031920123000031/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/319201/000031920123000031/klac-20230630_cal.xml) |
| KLAC 2023-07-01 / 2024-06-30 | `0000319201-24-000021`; `us-gaap@2024` | `c-1`; `usd→USD`; `-3`; ∅ | R 9,812.247; C 3,928.073; D 1,278.981; S 969.509; I 289.474; E 311.253; L 0; N +155.075 | 3,346.210; 3,190.032; 3,190.032; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/319201/000031920124000021/klac-20240630_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/319201/000031920124000021/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/319201/000031920124000021/klac-20240630_cal.xml) |
| KLAC 2024-07-01 / 2025-06-30 | `0000319201-25-000024`; `us-gaap@2025` | `c-1`; `usd→USD`; `-3`; ∅ | R 12,156.162; C 4,751.867; D 1,360.334; S 1,029.734; I 239.100; E 302.166; L 0; N +171.487 | 4,775.127; 4,644.448; 4,644.448; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/319201/000031920125000024/klac-20250630_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/319201/000031920125000024/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/319201/000031920125000024/klac-20250630_cal.xml) |
| KLAC 2025-07-01 / 2026-06-30 | `0000319201-26-000027`; `us-gaap@2026` | `c-1`; `usd→USD`; `-3`; ∅ | R 13,579.476; C 5,255.060; D 1,532.118; S 1,131.518; I 0; E 284.440; L absent; N +229.585 | 5,660.780; 5,605.925; 5,605.925; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/319201/000031920126000027/klac-20260630_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/319201/000031920126000027/R5.htm) · [calc](https://www.sec.gov/Archives/edgar/data/319201/000031920126000027/klac-20260630_cal.xml) |
| IBM 2021-01-01 / 2021-12-31 | `0001558370-22-001584`; `us-gaap@2021-01-31`, `ibm@20211231` | `Duration_1_1_2021_To_12_31_2021_WlJ6c3zD106iejIq2PdgaQ`; `Unit_Standard_USD_qrxSbNGXmUigHWDQl1jnYQ→USD`; `-6`; ∅ | R 57,350; C 25,865; G 31,486; S 18,745; D 6,488; A 612; N 873; E 1,155 | 6,865; 4,837; 4,837; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000155837022001584/ibm-20211231x10k_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/51143/000155837022001584/R2.htm) · [calc](https://www.sec.gov/Archives/edgar/data/51143/000155837022001584/ibm-20211231_cal.xml) |
| IBM 2022-01-01 / 2022-12-31 | `0001558370-23-002376`; `us-gaap@2022`, `ibm@20221231` | `Duration_1_1_2022_To_12_31_2022_M62iYm1530e69wSMRRzSSg`; `Unit_Standard_USD_V0S28s59cUiaBq97g8Wwbw→USD`; `-6`; ∅ | R 60,530; C 27,842; G 32,687; S 18,609; D 6,567; A 663; N 5,803; E 1,216 | 8,174; 1,155; 1,156; -1 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000155837023002376/ibm-20221231x10k_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/51143/000155837023002376/R2.htm) · [calc](https://www.sec.gov/Archives/edgar/data/51143/000155837023002376/ibm-20221231_cal.xml) |
| IBM 2023-01-01 / 2023-12-31 | `0000051143-24-000012`; `us-gaap@2023`, `ibm@20231231` | `c-1`; `usd→USD`; `-6`; ∅ | R 61,860; C 27,560; G 34,300; S 19,003; D 6,775; A 860; N -914; E 1,607 | 9,382; 8,689; 8,690; -1 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000005114324000012/ibm-20231231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/51143/000005114324000012/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/51143/000005114324000012/ibm-20231231_cal.xml) |
| IBM 2024-01-01 / 2024-12-31 | `0000051143-25-000015`; `us-gaap@2024`, `ibm@20241231` | `c-1`; `usd→USD`; `-6`; ∅ | R 62,753; C 27,201; G 35,551; S 19,688; D 7,479; A 996; N 1,871; E 1,712 | 9,380; 5,797; 5,797; 0 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000005114325000015/ibm-20241231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/51143/000005114325000015/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/51143/000005114325000015/ibm-20241231_cal.xml) |
| IBM 2025-01-01 / 2025-12-31 | `0000051143-26-000010`; `us-gaap@2025`, `ibm@20251231` | `c-1`; `usd→USD`; `-6`; ∅ | R 67,535; C 28,239; G 39,297; S 20,123; D 8,316; A 964; N -442; E 1,935 | 11,822; 10,329; 10,328; +1 | `DERIVATION_APPROVED` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/ibm-20251231_htm.xml) · [face](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/R3.htm) · [calc](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/ibm-20251231_cal.xml) |

## Completeness, overlap, and sign proof

For every row, the filer-submitted calculation tree contains the complete
primary-statement path from Revenue/Gross Profit to Pretax. The candidate
equation partitions those children exactly once into operating operands and
the excluded Pretax bridge. The primary statement contains no additional line
between Revenue and Pretax outside that partition. All selected facts use the
same authoritative annual entity/period context, empty dimensions, and an
exact USD unit. The linked statement captions and calculation weights agree
with the displayed and XBRL signs described above.

LLY and MRK provide an additional issuer aggregate whose calculation children
exactly equal the complete face-statement lines. IBM provides the analogous
`ExpenseAndOtherIncome` / `ExpenseAndIncomeOther` aggregate. JNJ and KLAC attach
every component directly to Pretax. These independent relationships prove
coverage and non-overlap; the derivations do not infer a missing component from
the numerical difference to Pretax.

IBM presents all values in whole millions. Its independently reported Gross
Profit differs from Revenue less Cost by -$1 million in 2021 and 2025 and +$1
million in 2022 and 2024; the submitted calculation nevertheless links those
rounded lines. The Gross-Profit-based Pretax bridge differs by -$1 million in
2022 and 2023 and +$1 million in 2025. The explicit tolerance is therefore at
most $1 million, exactly one displayed unit, only for an IBM whole-million
statement, and only when the submitted calculation relationship exists. It is
not a general plug or percentage tolerance.

## Disputed-component decisions

| Component | Decision | Rationale and boundary |
|---|---|---|
| Acquired IPR&D | Operating | It is a period R&D charge on the consolidated operations statement and an explicit operating-side child before separately identified non-operating items. Include LLY and JNJ exact face facts; do not generalize issuer-extension names by label. |
| Restructuring | Operating | Exit/disposal costs of continuing operations remain in operating expense. Include LLY, JNJ, and MRK exact facts. A discontinued-operation or financing restructuring fact would require separate review. |
| Impairment | Operating | LLY special charges and KLAC goodwill/intangible impairments are period costs tied to operating assets on the consolidated operations statement. Include exact reviewed facts, including reported zero facts; never infer zero from absence. |
| Other income/expense | Non-operating in these equations | The exact LLY/JNJ/MRK/KLAC concepts are taxonomy-defined non-operating facts. IBM's note identifies currency/derivatives, interest income, investments, non-service retirement items, divestitures, and miscellaneous items. Add/subtract them only in the Pretax bridge. |
| Interest income and expense | Non-operating | Exclude from Operating Income and include in the Pretax bridge. This includes JNJ investment interest, KLAC/IBM interest expense, and interest income embedded in IBM Other. |
| Pension service cost | Operating | Employee service cost remains embedded in cost/SG&A/R&D and is not removed. |
| Non-service pension components | Non-operating | IBM explicitly places these components in Other; exclude them from Operating Income and retain them in the Pretax bridge. |
| IBM IP/custom-development income | Operating, IBM-scoped | IBM assigns it to Infrastructure segment expense/other and describes the aggregate as including income associated with normal operations. Add the exact issuer-extension fact. No local-name fallback is approved. |
| Issuer expense aggregates | Checkpoint only | LLY `CostOfSalesOperatingExpensesAndOtherNet`, MRK `CostsExpensesAndOther`, and IBM `ExpenseAndOtherIncome` / `ExpenseAndIncomeOther` include non-operating items and reconcile to Pretax. They are not Operating Income and are not operands. |

## Issuer stability and policy scope

| Issuer | Approved periods | Equation stability | Safest implementation scope |
|---|---:|---|---|
| LLY | 5 | Economic equation stable; acquired-IPR&D and R&D concepts change | exact five-accession registry with reviewed occurrence selection |
| JNJ | 5 | Economic equation stable; IPR&D and interest concepts change | exact five-accession registry |
| MRK | 5 | Same standard component equation in all periods | exact five-accession registry; evidence does not approve future filings |
| KLAC | 5 | Same perimeter; impairment/debt-loss rows can be reported zero or absent | exact five-accession registry with explicit operand-presence rules |
| IBM | 5 | Same perimeter; issuer aggregate and Other concept names change | exact five-accession registry plus $1 million whole-statement rounding gate |
| **Total** | **25** | **five issuer-stable patterns** | **curated exact-accession policy only** |

There is a generic economic pattern—Revenue less a complete set of operating
costs—but no generic concept-set implementation is approved. The evidence
supports issuer-scoped equations across the five reviewed periods only in the
sense that each issuer repeats one economic perimeter. Because completeness is
proved by the exact selected statement and calculation tree, registration must
still be exact-accession scoped. Future filings must be researched rather than
inherited.

## Implementation boundary and next milestone

Wave 15 completes the separately reviewed
[curated Operating Income derivation-policy design](operating-income-derivation-policy-design.md).
It freezes `operating_income_component_derivation_v1` as an immutable registry
for only these 25 exact CIK/accession/period equations, with ordered signed
operands, exact filing-XBRL selection, reviewed alternate occurrences,
validation-only IBM rounding gates, direct-result precedence, complete
provenance, serialization, Operating Tax boundaries, and conservative failure
behavior. It explicitly excludes CVX, GE, future filings, amendments, and
unregistered evidence.

The next milestone is narrow implementation and validation of that approved
design. The design target is 25 additional Operating Income resolutions,
leaving the ten CVX/GE periods missing; production counts do not change until
implementation tests and exact live corpus reconciliation succeed.
