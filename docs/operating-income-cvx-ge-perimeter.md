# CVX and GE Operating Income business-perimeter research

## Scope and decision

Phase 1H.4 Wave 17 reviews only the ten remaining Operating Income gaps:
five frozen CVX filings and five frozen GE filings. The committed
[Wave 13 inventory](operating-income-concepts.md#complete-35-period-inventory)
supplies the selected accessions, authoritative annual dates, consolidated
face-statement locations and absence of a direct equivalent. Its concept,
Company Facts, presentation-role and occurrence inventory is not repeated.
The [reviewed Operating Income definition](operating-income-derivation-design.md#economic-definition-and-operating-perimeter)
remains controlling.

**Decision: NO-GO for adding any of these ten periods to the existing Operating
Income primitive.** Five CVX periods are `BUSINESS_PERIMETER_UNRESOLVED`; five
GE periods are `SPECIALIZED_METHODOLOGY_REQUIRED` for a consolidated
industrial/insurance measure. There are zero `DERIVATION_CANDIDATE` periods
and zero approved additional resolutions. This is not a finding that either
company has zero operating earnings, nor that financial arithmetic is
impossible. It means a complete, compatible, non-overlapping equation has not
been established for the existing generic operating-company primitive.

These are research classifications, not changes to normalized availability or
the universe execution plan. In particular, GE remains one of the 43 generic
issuer executions in the validated corpus; this wave does not add an eighth
specialized skip or reclassify a constituent automatically. A future
methodology/constituent review must distinguish the industrial business from
the consolidated mixed-business perimeter.

The frozen production baseline remains Operating Income **194 resolved / 10
missing / 0 ambiguous**, and aggregate **1,880 resolved / 1,508 missing / 11
ambiguous / 27 methodology-blocked / 42 not-comparable**, across **3,468
states**. No code, test, policy, parser, filing selection or corpus result is
changed. No tests or corpus runs are performed in this research wave.

## Additional evidence method

Only the ten selected filings' note indexes and the additional notes identified
in the evidence register below were retrieved on 2026-10-10. The note indexes
were used to locate the relevant consolidation, revenue, affiliate,
investment, pension, segment, discontinued-operation and separation
disclosures. No new Company Facts or filing-XBRL concept inventory was run.
The existing `R3.htm` face statements are reused from Wave 13, not fetched
again or revalidated. No filing outside the frozen ten-accession set supplies
an operand or classification.

Selected-period values below come from the current-year column of that exact
selected filing. Later filings' comparative columns are used only to
demonstrate restatements or perimeter changes; they never replace the selected
observation. Note amounts are USD millions unless specified otherwise. They
are evidence of scope, **not derived Operating Income values**. Notes commonly
contain multiple periods, plan/geographic dimensions or segment eliminations;
none is promoted to a nondimensional operand by this research.

## Complete ten-period matrix

`C` and `G` refer to the incomplete research expressions below, not executable
or approved equations. `C1`–`C5` and `G1`–`G5` identify exact note sets in the
evidence register. All annual periods are January 1 through December 31 of the
listed year, as frozen by Wave 13; no calendar-period inference is performed.

| Issuer / CIK | Exact authoritative annual period | Frozen selected accession | Face and additional note evidence | Proposed perimeter / equation status | Adjacent-period comparability and remaining conflict | Classification |
|---|---|---|---|---|---|---|
| CVX / 93410 | 2021-01-01 / 2021-12-31 | `0000093410-22-000019` | Wave 13 `R3.htm`; C1. Equity earnings 5,657; interest/debt expense 712. Controlled/proportionate operations differ from equity-method affiliates. | C: own consolidated operating activities, excluding affiliate earnings and financing; operating portion of Other not proved complete. No numeric OI approved. | Core accounting perimeter resembles 2022, but affiliate tax/measurement mix and Other remain unresolved; do not use after-tax segment earnings. | `BUSINESS_PERIMETER_UNRESOLVED` |
| CVX / 93410 | 2022-01-01 / 2022-12-31 | `0000093410-23-000009` | Wave 13 `R3.htm`; C2. Equity earnings 8,585; interest/debt expense 516. REG acquired June 13, 2022. | Same incomplete C boundary; purchased-crude netting and embedded costs must be preserved. No numeric OI approved. | REG is included only from acquisition; 2021/2022 are not a constant-asset series. Mixed-tax affiliate earnings and exact Other split unresolved. | `BUSINESS_PERIMETER_UNRESOLVED` |
| CVX / 93410 | 2023-01-01 / 2023-12-31 | `0000093410-24-000013` | Wave 13 `R3.htm`; C3. Equity earnings 5,131; interest/debt expense 469. PDC acquired August 7, 2023. | Same incomplete C boundary; impairment/abandonment costs cannot be removed merely as unusual items. No numeric OI approved. | Partial-year PDC versus later full-year ownership changes economics, not the annual dates. Other and affiliate perimeter unresolved. | `BUSINESS_PERIMETER_UNRESOLVED` |
| CVX / 93410 | 2024-01-01 / 2024-12-31 | `0000093410-25-000009` | Wave 13 `R3.htm`; C4. Equity earnings 4,596; interest/debt expense 594. Restructuring 980 already included in operating expense 706 and SG&A 274. | Same incomplete C boundary. Do not subtract restructuring again; segment operating/SG&A bundle includes other benefit components. No numeric OI approved. | Full-year PDC; new segment detail does not prove operating/non-operating separation. Hess is not yet consolidated in this selected period. | `BUSINESS_PERIMETER_UNRESOLVED` |
| CVX / 93410 | 2025-01-01 / 2025-12-31 | `0000093410-26-000078` | Wave 13 `R3.htm`; C5. Equity earnings 3,000; interest/debt expense 1,217. Hess acquired July 18, 2025; segment Other includes interest income. | Same incomplete C boundary; neither all Other nor affiliate net earnings can be inserted wholesale. No numeric OI approved. | Partial-year Hess and acquired assets/noncontrolling interests create a substantial asset-perimeter change from 2024; no pro-forma/backcast substitution. | `BUSINESS_PERIMETER_UNRESOLVED` |
| GE / 40545 | 2021-01-01 / 2021-12-31 | `0000040545-22-000008` | Wave 13 `R3.htm`; G1. Aviation, Healthcare, Renewable Energy and Power; GECAS discontinued. Continuing insurance revenue 3,106; insurance profit 566. | G: industrial-only expression would require a new carve-out; consolidated totals mix insurance and EFS with industrial operations. No compatible equation approved. | 2021/2022 broad industrial basis is similar, but cannot be joined directly to later HealthCare/Vernova-excluded periods. Corporate includes EFS financing/tax effects. | `SPECIALIZED_METHODOLOGY_REQUIRED` |
| GE / 40545 | 2022-01-01 / 2022-12-31 | `0000040545-23-000023` | Wave 13 `R3.htm`; G2. HealthCare remains in the selected 2022 continuing perimeter; January 3, 2023 separation is a subsequent event. Insurance revenue 2,954; profit 60. | Same G carve-out gap. Segment profit excludes selected costs and is not consolidated OI. No compatible equation approved. | Later 2023 filing retrospectively removes HealthCare and applies revised insurance accounting; selected 2022 values cannot be spliced into that basis. | `SPECIALIZED_METHODOLOGY_REQUIRED` |
| GE / 40545 | 2023-01-01 / 2023-12-31 | `0000040545-24-000027` | Wave 13 `R3.htm`; G3. HealthCare discontinued; Aerospace, Renewable Energy and Power remain. Insurance revenue 3,389; profit 332; LDTI adopted with January 1, 2021 transition date. | Same G carve-out gap, now on a different continuing perimeter. Other includes retained-investment gains, interest, royalties and equity income. No compatible equation approved. | Not comparable as a common-perimeter OI row to selected 2022 or selected 2024; Vernova is still in this selected continuing series. | `SPECIALIZED_METHODOLOGY_REQUIRED` |
| GE / 40545 | 2024-01-01 / 2024-12-31 | `0000040545-25-000015` | Wave 13 `R3.htm`; G4. Vernova spun April 2, 2024 and retrospectively discontinued; CES/DPT reporting introduced. Continuing insurance revenue 3,581; profit 1,022. | G remains an unapproved industrial carve-out. Segment profit 8,116 plus Corporate & Other -89 is not OI; goodwill impairment and mixed Other must be addressed. | New continuing basis differs from selected 2023. The 2024/2025 industrial reporting block is more aligned, but still includes insurance and mixed corporate items. | `SPECIALIZED_METHODOLOGY_REQUIRED` |
| GE / 40545 | 2025-01-01 / 2025-12-31 | `0000040545-26-000008` | Wave 13 `R3.htm`; G5. CES/DPT plus Corporate & Other; continuing insurance revenue 3,533; profit 992. Canadian insurance novations affect results. | G remains unapproved. Segment profit 10,157 plus Corporate & Other -96 includes mixed scopes; separation cost 202 is a GAAP continuing expense, not an automatic add-back. | No new five-period common perimeter. 2024/2025 are more aligned but not an insurance-free FCFF series; 2025 earnings-to-net-income terminology change alone is not an economic break. | `SPECIALIZED_METHODOLOGY_REQUIRED` |

Reconciliation: **CVX 5 + GE 5 = 10 distinct CIK/accession/annual identities**.
Classification totals: **5 BUSINESS_PERIMETER_UNRESOLVED + 5
SPECIALIZED_METHODOLOGY_REQUIRED**; all other primary categories have zero
rows. The GE common-five-period series is separately **NOT_COMPARABLE**; this
series-level conclusion does not replace the primary methodology classification
of its individual rows or change the 42 production not-comparable states.

## CVX: consolidation, affiliates and operating costs

### Entity and affiliate perimeter

Each selected accounting-policy note consolidates controlled subsidiaries and
qualifying VIEs, proportionately recognizes undivided interests in certain oil
and gas ventures/assets, and uses equity accounting for significant-influence
investments without control. These are not interchangeable perimeters.
Affiliate revenue/costs cannot be grossed into Chevron's consolidated operating
lines merely by multiplying ownership percentages.

The selected investments notes expressly distinguish affiliates for which
Chevron pays some income taxes directly: those taxes are excluded from the
affiliate earnings line and recognized in Chevron's income-tax expense.
Other affiliate earnings have different tax incidence. Consequently the
aggregate affiliate earnings line is not a uniform before-interest-and-tax
operating contribution. Calling every affiliate economically operational does
not establish compatible EBIT, NOPAT, reinvestment or capital scope.

An own-consolidated-operations perimeter would keep Chevron's actual sales to,
and purchases from, nonconsolidated affiliates already recognized in its own
sales/purchased-crude lines. It would not eliminate those transactions as if
the affiliate were controlled. Conversely, inserting equity earnings into that
perimeter without affiliate financing, taxes, D&A, reinvestment and capital
alignment produces a hybrid. Neither a pro-rata affiliate consolidation nor
an affiliate-inclusive FCFF policy is approved here.

### Potential expression C — incomplete, not an approved subtotal

For each of the five exact periods, the research expression is:

`C = S - P - O - G - X - D - T + U_operating`

where `S` is face Sales and other operating revenues; `P` purchased crude oil
and products; `O` face operating expenses; `G` face SG&A; `X` exploration;
`D` depreciation/depletion/amortization; `T` taxes other than on income; and
`U_operating` is an independently proved, non-overlapping operating portion of
Other income, **not** an estimated residual or assumed zero. No value for
`U_operating` is established in any row. Thus C is not calculated or labeled
consolidated Operating Income.

An eventual independent bridge would have to account for the exact excluded
affiliate earnings, non-operating Other, financing and non-service benefit
components, with correct signs and no duplicate consumption. Pretax would be
a check only, never the source of C or the source of `U_operating`. Simply
adding interest to Pretax would instead be analytical EBIT containing the
affiliate/Other mix; it is not approved as the current primitive.

| Component | Required treatment / unresolved boundary |
|---|---|
| Sales / purchased crude | Preserve the filed amounts and revenue scope. Revenue notes record contemplated buy/sell arrangements net in purchased crude. Do not gross up both sides or import intersegment transfers before eliminations. |
| Operating costs / SG&A | Retain ordinary and period-recognized operating costs, including employee service cost and operating restructuring. Do not replace face lines with the segment operating/SG&A bundle, which also includes other benefit components. |
| Exploration | Expensed successful-efforts exploration/dry-hole and related costs are operating. Capitalized wells/assets are not additional current expenses. No cash-versus-accrual conversion is assumed. |
| D&A / impairment | Retain operating depreciation/depletion and recognized operating-asset charges once. Supplemental impairment or abandonment disclosures do not authorize a second deduction or an adjusted-income add-back. |
| Non-income taxes | Operating deduction where separately reported; never confuse with income taxes used for NOPAT/Reported ETR. |
| R&D / restructuring detail | Supplemental detail is not an extra operand when embedded in face costs. The 2024 restructuring note proves 980 is already in operating expenses/SG&A. |
| Affiliate earnings | Not admitted wholesale to the own-consolidated-operating expression; mixed tax/financing/capital treatment prevents equivalence. This does not remove reported affiliate earnings from Pretax. |
| Other income | Contains identified non-operating items, including asset-sale gains and investment interest; selective after-tax supplemental amounts do not give a complete exact pretax partition. Foreign-currency effects can arise in both consolidated operations and affiliates; classification cannot be made from the label alone. |
| Interest | Exclude financing/investment interest from generic OI. Expensed interest/debt costs differ from total financing costs because some interest is capitalized; do not deduct capitalized interest again. Segment All Other interest expense is not automatically the complete face interest/debt amount. |
| Pension/OPEB | Retain employee service cost in operating costs; exclude non-service interest/return/amortization/settlement components under the existing perimeter. Plan-note components span plan/geographic scopes and cannot be separately subtracted again without a face-line allocation reconciliation. |
| All Other | Corporate costs must not disappear when using segment totals. Insurance, real estate and technology activities also occur here; their existence is not proof that the entire issuer is an insurer, or permission to treat unquantified scope as immaterial. |

The five selected segment notes evaluate segment earnings **after tax**, exclude
globally managed debt/investment interest and leave some corporate costs in All
Other. Their totals are therefore neither consolidated Operating Income nor a
permitted operating-expense completeness proof. The richer 2024/2025 segment
tables still bundle benefit components and other deductions. They do not close
the outstanding partition.

**CVX conclusion:** a repeated face-line structure exists, but no complete
compatible operating-only subtotal is established. Keep five periods unresolved.
The scope question is not solved by rejecting all affiliates solely because of
their names, or by accepting them solely because their businesses are upstream
or downstream. A future energy/affiliate policy would need matched income,
tax, invested-capital and reinvestment treatment, plus an exact Other/benefit
allocation. That is outside this wave's approval.

## GE: mixed business and changing continuing operations

### Continuing versus discontinued perimeter

The same selected registrant CIK, 40545, spans all five filings. The scope
changes are business separations and retrospective presentation, not evidence
for an automated predecessor/successor CIK linkage. GE HealthCare and GE
Vernova do not supply substitute operands for the selected GE filings.

- **2021–2022 selected filings:** the broad industrial perimeter includes
  Healthcare and energy businesses. GECAS and other disposed businesses are
  discontinued. Remaining Capital activities, including insurance and EFS,
  are reported within Corporate. EFS has financing/tax effects integral to its
  measurement; an industrial segment-profit sum does not remove them cleanly.
- **2023 selected filing:** the January 3, 2023 HealthCare separation causes
  retrospective discontinued-operation presentation; Aerospace, Renewable
  Energy and Power remain. Retained HealthCare investment effects remain in
  continuing Other rather than recreating Healthcare operating revenue.
- **2024–2025 selected filings:** after the April 2, 2024 Vernova separation,
  historical Vernova results are discontinued. Commercial Engines & Services
  (CES) and Defense & Propulsion Technologies (DPT) become the reportable
  industrial segments. Corporate & Other and run-off insurance remain; this
  is not a consolidated insurance-free Aerospace perimeter.

GE's insurance notes in **every** selected filing report continuing revenue,
profit and material insurance assets/liabilities. Insurance revenue includes
premiums and investment income; annuity contracts can create deposit
liabilities rather than revenue. Future-benefit reserves, investment assets,
reinsurance and statutory capital requirements are not ordinary operating-NWC
or generic industrial financing components. Removing all interest/investment
income from this consolidated business would remove part of insurance's
operating economics. Retaining it wholesale would violate the existing generic
industrial perimeter. Run-off status does not eliminate these obligations.

### Potential expression G — new carve-out needed, not approved

There is **no approved selected-period equation** for consolidated GE Operating
Income. A prospective industrial-only research expression is:

`G = industrial equipment/service revenue + separately proved industrial
operating Other - complete related GAAP industrial costs - allocated continuing
corporate operating costs`

Every term must use a consistent industrial/continuing scope and include the
related corporate and noncontrolling-interest basis. The expression cannot be
executed until insurance/EFS allocations, mixed Other, segment adjustments,
intersegment eliminations and the continuing/discontinued boundary are proved.
It would be a **new industrial carve-out**, not the existing consolidated
primitive, unless a separately reviewed methodology established compatibility.
No Pretax-minus-residual method or manufactured consolidated subtotal is used.

| Component | Required treatment / unresolved boundary |
|---|---|
| Segment operating income/profit | CODM measurements may exclude impairments, higher-cost restructuring, separation, acquisitions and litigation. They exclude noncontrolling interests and may include Other income. Dimensioned facts retain these boundaries; summing them does not create a consolidated nondimensional fact. |
| Corporate / reconciliation | Contains insurance, legacy financial interests, investment effects and operating corporate costs. Cannot be added wholesale to segments or dropped wholesale. Early filings explicitly include EFS financing/tax effects in Corporate. |
| Other income | Licensing/royalty income may be operational, but interest/investment income, retained-share gains, disposals, equity earnings and unpartitioned Other coexist. The selected 2025 note separately reports licensing/royalties 175, equity income 216 and total Other 1,487; this does not prove a complete industrial allocation. |
| Interest | Exclude financing interest for a proven industrial perimeter; insurance investment income requires its own business treatment. Customer-advance interest is separately identified in Other but is not silently approved as generic operating revenue. |
| Pension | Selected pension notes label service cost operating and place remaining non-service components in the non-operating benefit line. Preserve signs, including benefit income; do not subtract total pension cost on top of face costs. Plan splits at separations also affect comparability. |
| Restructuring / impairment | Retain GAAP costs of continuing operating activities, once. Selected restructuring notes show charges already in cost of equipment/services or SG&A; segment exclusions must be restored, not turned into non-GAAP add-backs. |
| Separation costs | Continuing employee, systems, professional-fee and transition costs are not excluded merely because nonrecurring. Costs specifically identifiable to disposed HealthCare/Vernova businesses belong to discontinued operations as filed. Do not charge continuing operations twice or pull discontinued costs back into an industrial series. |
| Insurance / financial services | Neither aggregate insurance profit nor net earnings is industrial EBIT. A consolidated mixed-business or sum-of-parts approach requires dedicated capital/tax/reinvestment methodology and explicit allocation evidence. |

The 2024 and 2025 segment notes explicitly say other segment expenses/income
include equity-method income, interest and licensing/royalty income. Adding
the two segment profits and Corporate & Other therefore retains an economic
mix even before reviewing goodwill impairment, taxes, financing and NCI. The
Wave 13 dimensioned facts remain non-equivalent; no duplicate or context
collapse changes this conclusion.

**GE conclusion:** a stable five-period generic operating-company perimeter
does not exist in the frozen selected series. All five consolidated mixed-
business rows need specialized perimeter treatment. This is not a conclusion
that the industrial engine business itself is an insurer or cannot ultimately
be analyzed using FCFF; it is a refusal to substitute that business for the
selected consolidated company without a separately approved carve-out.

## Adjacent-period comparability decision

| Boundary | Decision and selected-filing evidence |
|---|---|
| CVX 2021 → 2022 | Core consolidation/affiliate policy repeats, but June 2022 REG changes the asset perimeter. As-reported periods may be retained with acquisition disclosure; not a constant-asset growth series. |
| CVX 2022 → 2023 | August 2023 PDC creates partial-year ownership; complete five-period OI remains unapproved independently of this acquisition effect. |
| CVX 2023 → 2024 | Same broad reporting basis, but partial versus full-year PDC and 2024 embedded restructuring require explicit interpretation. Do not normalize unusual costs away. |
| CVX 2024 → 2025 | July 2025 Hess materially changes assets, ownership and operating footprint. No implied full-year Hess backcast or later-filing operand substitution. |
| GE 2021 → 2022 | Broad industrial perimeter is substantially aligned, with insurance/EFS still present. That limited alignment does not establish a generic OI equation. |
| GE 2022 → 2023 | **NOT_COMPARABLE as selected common-perimeter OI.** Selected 2022 segment note reports revenue 76,555; selected 2023 recasts its 2022 comparative to 58,100 after HealthCare discontinuation. LDTI adoption also revises prior insurance measurement: selected 2022 insurance profit 60 becomes comparative 205 in selected 2023. |
| GE 2023 → 2024 | **NOT_COMPARABLE as selected common-perimeter OI.** Selected 2023 revenue 67,954 becomes comparative 35,348 in selected 2024 after Vernova discontinuation. Selected 2023 Other 7,129 becomes comparative 6,718; separation costs 978 become comparative 692. These are scope changes, not interchangeable observations. |
| GE 2024 → 2025 | CES/DPT reporting and retrospective Vernova exclusion are more aligned. Insurance remains, and 2025 novations/reserve releases change its results. No common five-year industrial series or OI approval follows from this two-year alignment. |

Comparative disclosures establish the breaks; they do not authorize replacing
the frozen selected accessions. A common-perimeter recast history would be a
separate research product with explicit provenance, accounting transitions,
corporate allocations and cross-filing comparability rules. None is produced
here. The five GE primary methodology classifications and this series-level
comparability decision are deliberately distinct.

## Exact additional note evidence register

Face evidence for every row remains the selected `R3.htm` linked in Wave 13.
All links below are newly introduced note evidence in the **same selected
accession**. Titles/locations were matched using its Filing Summary. Every
linked note returned HTTP 200 and its selected-period header was checked;
unchanged Wave 13 links were not revalidated.

| Set / period | Direct SEC selected-filing note evidence |
|---|---|
| C1 / CVX 2021 | [Accounting/consolidation](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R10.htm); [segments](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R23.htm); [affiliates](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R24.htm); [benefits](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R32.htm); [revenue](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R35.htm); [other financial information](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R36.htm) |
| C2 / CVX 2022 | [Accounting/consolidation](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R10.htm); [segments](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R23.htm); [affiliates](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R24.htm); [benefits](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R32.htm); [revenue](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R35.htm); [other financial information](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R36.htm); [REG acquisition](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R38.htm) |
| C3 / CVX 2023 | [Accounting/consolidation](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R10.htm); [segments](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R23.htm); [affiliates](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R24.htm); [benefits](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R32.htm); [revenue](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R35.htm); [other financial information](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R36.htm); [PDC acquisition](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R38.htm) |
| C4 / CVX 2024 | [Accounting/consolidation](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R10.htm); [segments](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R23.htm); [affiliates](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R24.htm); [benefits](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R32.htm); [revenue](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R35.htm); [other financial information](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R36.htm); [embedded restructuring](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R17.htm) |
| C5 / CVX 2025 | [Accounting/consolidation](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R10.htm); [segments](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R23.htm); [affiliates](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R24.htm); [benefits](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R32.htm); [revenue](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R35.htm); [other financial information](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R36.htm); [restructuring](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R17.htm); [Hess acquisition](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R38.htm) |
| G1 / GE 2021 | [Basis/financial services](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/R9.htm); [discontinued operations](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/R10.htm); [insurance](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/R19.htm); [pensions](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/R20.htm); [Other](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/R26.htm); [segments/corporate](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/R31.htm) |
| G2 / GE 2022 | [Basis](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R9.htm); [discontinued operations](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R10.htm); [insurance](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R20.htm); [pensions](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R21.htm); [Other](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R27.htm); [restructuring/separation](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R28.htm); [segments](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R33.htm); [HealthCare subsequent event](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R36.htm) |
| G3 / GE 2023 | [Basis](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R9.htm); [discontinued operations](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R10.htm); [insurance/LDTI](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R20.htm); [pensions](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R21.htm); [Other](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R27.htm); [restructuring/separation](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R28.htm); [segments](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R33.htm) |
| G4 / GE 2024 | [Basis](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R10.htm); [discontinued operations](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R11.htm); [insurance](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R21.htm); [pensions](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R22.htm); [Other](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R28.htm); [restructuring/separation](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R29.htm); [segments/reconciliation](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R34.htm) |
| G5 / GE 2025 | [Basis](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R10.htm); [discontinued operations](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R11.htm); [insurance/novations](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R21.htm); [pensions](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R22.htm); [Other](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R28.htm); [restructuring/separation](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R29.htm); [segments/reconciliation](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R34.htm) |

## Risks, validation and next milestone

The remaining risks are economic scope and completeness, not a request to
relax the parser or concept policy: CVX mixed-tax affiliates, mixed Other and
benefit/corporate allocations; GE insurance/industrial economics, mixed Other,
CODM exclusions, NCI, LDTI transition and portfolio separations. Approximate
arithmetic, repeating captions, a nearby Pretax total or a later comparative
does not resolve any of them.

The matrix matches exactly ten Wave 13 accessions and annual periods, five per
issuer. All 70 newly linked notes are in those selected filing directories and
were retrieved successfully; no unchanged evidence links were revalidated.
Local documentation targets/anchors and `git diff --check` pass. The only
repository changes are this research document and its status/concept/taxonomy
cross-references. Downloaded evidence and discovery scripts remain outside the
repository in `/tmp/valuation-platform-wave17-evidence` and `/tmp`; they are
ephemeral research material, not application caching infrastructure.

**Safe additional coverage: 0/10.** Keep all ten production gaps typed missing;
do not emit the analytical expressions as Operating Income or force a
five-year series. No financial definition or architecture is changed, so no
methodology or architecture rewrite is required.

The recommended next Phase 1H.4 milestone is the higher-frequency **exact
selected-filing D&A concept/component evidence inventory for the 94 missing
D&A periods** in the existing failure-taxonomy backlog. Do not implement D&A
policies without reviewed completeness and overlap evidence. CVX energy/
affiliate treatment and GE industrial/insurance carve-out or common-perimeter
recast design remain separate, explicitly unapproved research paths; revisiting
them requires a dedicated methodology scope, not another generic Operating
Income fallback. Valuation and forecast work remain paused through Phase 1H.6.
