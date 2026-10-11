# CVX cash-PP&E acquisition/perimeter review

Wave 32 [implements the five reviewed acceptances](capex-cvx-scope-evidence-results.md)
as disjoint curated v2, preserving v1/direct results and the methodology below.
Capex is now 162/42/0. No allocation or adjusted equation was approved; integrated
FCFF compatibility remains unknown. The next bounded pass concerns NVDA's five
combined-asset cash-component gaps, not repeated CVX perimeter research.

Wave 31 completes the [five-entry exact-accession scope design](capex-cvx-scope-evidence-design.md)
and [acceptance matrix](capex-cvx-scope-evidence-matrix.json), using the unchanged
Wave 30 methodology/supplement below. Five CVX designs form disjoint immutable
v2 alongside the ten unchanged v1 approvals, with 42 unapproved controls.
No production approval or equation; counts remain unchanged. Next implement
only that reviewed five-entry contract with incremental validation, not another
methodology or allocation research pass.

## Current decision: Wave 30 methodology review

Wave 30 starts at `16454c508cdce7e05be08fa11e043eed3ff6d293`, clean
`main`, eight commits ahead of origin; no push. **PARTIAL GO for five
exact-accession reported-value scope designs; no derivation, generic fallback
or production approval.** The historical Wave 29 decision below is superseded
for potential design coverage only. Its decision and original commit/path/digest
are preserved in the supplement, not silently rewritten.

### Methodological eligibility versus available amounts

The existing primitive is cash expenditure to acquire PP&E, not a hypothetical
materials-only purchase measure. Construction/development of recognized PP&E
is eligible; a construction input's origin as a service or rented piece of
equipment does not by itself make its capitalized cash cost ineligible.
This clarifies the existing asset-and-cash perimeter, **not** inclusion of all
exploration, leases, intangible rights or investments.

| Item | Methodological treatment | Retained evidence / amount availability |
| --- | --- | --- |
| Development wells and related plant/equipment | Cash acquisition/construction within recognized PP&E is eligible; unpaid/noncash additions are not. | Each R10 describes the successful-efforts PP&E cost basis; R12 independently reports annual cash PP&E with noncash movements excluded. |
| Proved mineral interests in crude-oil/natural-gas properties | Eligible within this selected depletable PP&E property perimeter when acquired for cash outside a business combination. PP&E is not restricted to non-depletable machinery; this is not generic intangible/right acceptance. | R10 expressly places these costs in the PP&E policy and describes subsequent depletion. A separate mineral cash amount is not established; no mineral-only equation. |
| Capitalized exploratory wells | Eligible cash costs while recognized within this evidenced PP&E perimeter, including qualifying pending-reserve assessments under the stated policy. | R10 distinguishes capitalized wells from other exploratory costs; R12 separately reports current dry-hole expenditure. No retrospective success-only adjustment or well-level split. |
| Expensed exploration, current dry holes, prior-year write-offs | Not additional cash PP&E operands. A prior-year write-off is not current investment cash. | R12's split and R10's policy support exclusion of the separate expense/dry-hole components. No total dry-hole expense or book-additions residual. |
| Operating-lease services capitalized into another PP&E asset | Eligible only as already included in the evidenced PP&E cash cost component; not acquisition of a ROU asset or a separate lease Capex policy. | R14 distinguishes incurred expense/capitalized costs and actual investing cash, without allocating that cash to the PP&E component. No separate ADD/SUBTRACT operand. |
| Lease cash in other destinations | Investing classification alone does not establish PP&E eligibility; operating cash is not added either. | Exact investing cash is available, but its PP&E destination/overlap is not separately quantified. Do not assume all of it belongs inside or outside PP&E. |
| Noncash operating/finance ROU additions and ARO recognition | Excluded from cash Capex even if the asset appears in PP&E. | R14 describes assets exchanged for new/modified liabilities; R10 describes ARO recognition, and R12 excludes noncash movements. |
| Finance-lease principal, acquired fair-value PP&E, business consideration, affiliate investments | Separate financing/acquisition/investment treatment; not substitutes or additions to this cash PP&E operand. | R7/R12/R14 and the acquisition notes establish separate lines and transaction nature. Never convert net acquisition cash into a positive PP&E payment. |

**Why five reported-value candidates, but zero equations:** R12 independently
reports the whole PP&E cash component, not a mixed productive-assets total whose
eligible part must be inferred. R10's cost policy, R27's separate book basis,
the explicit noncash exclusion and separate acquisition/other cash categories
support that perimeter. Under this clarification, capitalized cash inputs within
the reported PP&E component do not require removal merely because they originated
as services, rentals or mineral-property acquisition. A decomposition is not
needed to preserve this complete, independently reported component.

The separate lease disclosure is **not** assigned wholly to PP&E. Its unknown
allocation remains a real limitation for a lease-adjusted, mineral-only or
materials-only derivation: no such equation is approved. If a later consumer
requires that split, these 36 reports exhaust the available evidence; an explicit
exact-period destination/overlap allocation would be needed. Numerical agreement,
residuals, incurred lease costs or assumed zeros cannot provide it.
Software/intangible or incentive silence is not zero. Acceptance does not add
separate intangible purchases, reconstruct pre-incentive cash, or approve the
broad productive-assets aggregate. No subcost allocation is invented.

### Per-period decisions and lease evidence

Amounts are USD millions; frozen accessions/contexts/ordinals remain those in
the original five-period table and JSON.

| Year | PP&E cash | Investing operating-lease cash | Noncash ROU additions: operating / finance | Finance-lease principal | Wave 30 decision |
| --- | ---: | ---: | ---: | ---: | --- |
| 2021 | 7,515 | 398 | 1,063 / 60 | 193 | `EXACT_ACCESSION_ACCEPTANCE_CANDIDATE` |
| 2022 | 10,349 | 467 | 1,807 / 3 | 44 | `EXACT_ACCESSION_ACCEPTANCE_CANDIDATE` |
| 2023 | 14,788 | 713 | 2,556 / 233 | 42 | `EXACT_ACCESSION_ACCEPTANCE_CANDIDATE` |
| 2024 | 15,544 | 979 | 2,205 / 40 | 67 | `EXACT_ACCESSION_ACCEPTANCE_CANDIDATE` |
| 2025 | 16,830 | 881 | 2,845 / 971 | 136 | `EXACT_ACCESSION_ACCEPTANCE_CANDIDATE` |

R14's current-year ROU footnotes establish noncash additions, not cash operands
or a subtraction from R12. Investing-lease/principal facts retain exact annual
contexts, units and ordinals. Total lease costs incurred mix expense and
capitalization and are not interchangeable with cash/noncash additions.
The five PP&E cash values are unchanged; exact statement checks corroborate
them but do not prove their economic scope.

### Impact, remaining gates and bounded next milestone

No primitive change is proposed and no production policy is altered. This does
not retrospectively recertify every generic observation or unresolved issuer.

| Current policy family | Impact |
| --- | --- |
| Generic standard cash PP&E | Concept, precedence, value and provenance unchanged; no productive-assets/oil-gas fallback; cash construction is not book additions. |
| META gross-versus-net facts | Gross cash remains unnetted against proceeds; no restatement. |
| Ten AMZN/LLY curated entries | Existing reported acquisition/construction cash preserved; no mineral generalization, lease adjustment, interest adjustment or incentive gross-up. |
| CVX | Five potential exact-accession designs only; runtime approval stays false and all five remain missing. |
| Future FCFF consumers | Lease, depletion/write-off, EBIT, affiliate and timing compatibility is not certified. |

The supplement is now `wave30-cvx-capex-methodology-v2`: five
`EXACT_PERIOD_SCOPE_EQUIVALENT` candidates, five historical Wave 29 decisions
retained, zero approved equations. The frozen Wave 26 inventory, Wave 27
acceptance matrix and 36-body fixture/digests are unchanged. Five candidates
plus 42 other current gaps reconcile to 47 production missing periods; the
other gaps are not fresh denials. Production remains Capex 157/47/0 and
aggregate 1,895/1,493/11/27/42 = 3,468, carried forward without a rerun.

Wave 30 validation: five unique frozen identities and all immutable fact,
context, occurrence and value fields match Wave 29; five selected-instance
digests and all 36 retained response-body digests verify. Five exact statement
checks, five candidate decisions, zero equations and zero production approvals
reconcile. All 71 local links across the six reviewed documentation files
resolve; `git diff --check` passes. No source, policy, schema, evidence-body or
test files changed; no tests or corpus rerun.

**One bounded next milestone:** documentation-only design of the five-entry
CVX exact-accession reported-cash-PP&E scope-evidence contract. Freeze operand
and reviewed evidence identities, exclusions, direct precedence,
duplicate/conflict and conservative failure rules, immutable versioning and
full provenance/serialization. No implementation, future/amended approval,
lease/mineral derivation or broad research. No new SEC retrieval was needed.
The allocation blocker for adjusted equations is recorded, not a request to
repeat exhausted research.

## Wave 29 decision and scope (historical)

Phase 1H.4 Wave 29 starts at
`7fa04cf60df284b7a6338c3896b63535fe9ed90a`, clean `main`, seven commits
ahead of origin. No push. This is research, not a new acceptance policy.

**NO-GO for acceptance or derivation now; zero safe additional coverage.**
All five periods retain `CONCEPT_POLICY` / `SCOPE_RESEARCH_REQUIRED` in the
frozen inventory. The narrower review decision
`UNRESOLVED_METHODOLOGY_BLOCKER` means that the cash construction/development,
mineral-interest and capitalized-lease perimeter needs an explicit decision
against the existing primitive. It is not a new production enum, a demonstrated
economic incompatibility, or a change from historical `missing` to
`methodology_blocked`.

The reported PP&E cash component is substantially better evidence than the
aggregate capital-expenditure tag. Business-combination cash, investments,
noncash additions and disposal proceeds can be distinguished. Nevertheless,
that separation alone does not prove full equivalence to the project's
[gross cash PP&E acquisition primitive](financial-methodology.md). Neither
capitalization nor an arithmetic bridge establishes the remaining cost perimeter.

The [five-period machine-checkable supplement](capex-cvx-perimeter-inventory.json)
binds the unchanged [57-period Wave 26 inventory](capex-inventory.json) by
SHA-256. It preserves exact filing/DEI identities, all selected annual
occurrences for the relevant concepts, raw/Decimal values, signs, units,
contexts, dimensions, ordinals and candidate presentation/calculation metadata.
The Wave 27 acceptance matrix and runtime AMZN/LLY registry are unchanged.
The other 42 current Capex gaps are outside this review, not newly reviewed denials.

## Five frozen periods

All periods are CIK `93410`, January 1–December 31 of the listed year,
selected non-amended 10-Ks. Monetary table amounts are **USD millions**;
the supplement preserves exact USD strings, not rounded replacements.

| Year | Selected accession / cash-flow components note | PP&E cash candidate | Full-instance ordinal / annual context | Decision |
| --- | --- | ---: | --- | --- |
| 2021 | [0000093410-22-000019 / R12](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R12.htm) | 7,515 | 714 / `idd436c1bb1314e08bd5fd6d1285101ad_D20210101-20211231` | Unresolved methodology perimeter |
| 2022 | [0000093410-23-000009 / R12](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R12.htm) | 10,349 | 698 / `i3cd5a5d08ac0405882d3e0768d20dc50_D20220101-20221231` | Unresolved methodology perimeter |
| 2023 | [0000093410-24-000013 / R12](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R12.htm) | 14,788 | 723 / `c-1` | Unresolved methodology perimeter |
| 2024 | [0000093410-25-000009 / R12](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R12.htm) | 15,544 | 736 / `c-1` | Unresolved methodology perimeter |
| 2025 | [0000093410-26-000078 / R12](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R12.htm) | 16,830 | 753 / `c-1` | Unresolved methodology perimeter |

Each candidate is `us-gaap:PaymentsToAcquireOilAndGasPropertyAndEquipment`,
with selected taxonomy namespaces respectively
`http://fasb.org/us-gaap/2021-01-31`, `/2022`, `/2023`, `/2024`, `/2025`.
Each has one exact annual nondimensional non-nil occurrence, unit ID `usd`
normalizing to exact USD, decimals `-6`, positive raw/numeric value and one
semantic signature. Context entity is SEC CIK `0000093410`. The selected note
caption describes consolidated additions to PP&E, not merely upstream spending;
the tag's oil/gas local name does not itself prove economic scope. Full-instance
ordinals are zero-based. No candidate conflict or duplicate is hidden.

R12 is Information Relating to the Consolidated Statement of Cash
Flows; its detailed presentation role is retained per selected namespace.
R7 is the consolidated cash-flow statement, R10 accounting policies,
R14 leases, R24 investments/advances, R27 PP&E and
R38 acquisitions. R39 in 2023 also contains the acquisition/Hess
agreement disclosure. Exact report URLs and original bodies for all these
locations are in the supplement and [retained-body evidence](evidence/cvx-capex-perimeter-response-bodies.json).

## Cash-flow component reconciliation, not a Capex equation

| Year | PP&E | Investments | Current-year dry holes | Other assets/liabilities, net | Cash-flow capital expenditures | Excluded noncash PP&E movements |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2021 | 7,515 | 460 | 83 | -2 | 8,056 | 316 |
| 2022 | 10,349 | 1,147 | 309 | 169 | 11,974 | 334 |
| 2023 | 14,788 | 690 | 326 | 25 | 15,829 | 1,559 |
| 2024 | 15,544 | 573 | 331 | 0 | 16,448 | 395 |
| 2025 | 16,830 | 225 | 292 | 0 | 17,347 | 1,235 |

For each selected filing, PP&E + investments + current-year dry holes + other
equals the reported cash-flow capital-expenditure aggregate **exactly** at the
reported million-dollar precision: zero difference and no rounding tolerance.
This checks the explicitly disclosed component table; it does **not** derive
PP&E from a residual or approve the aggregate as Capex. The PP&E component is
independently reported. The aggregate has two equal nondimensional annual
occurrences (face and detail), retained separately. The PP&E candidate has one.
No statement bridge is confused with a submitted calculation arc: the candidate
has no calculation relationships in the retained 2021–2024 inventory;
2025 has a +1 parent/child arc into `PaymentsToAcquireProductiveAssets`.

Investment additions use `PaymentsToAcquireInterestInSubsidiariesAndAffiliates`.
The first four cash dry-hole components use `ResultsOfOperationsDryHoleCosts`;
2025 uses the CVX extension `PaymentsForCurrentYearDryHoleExpenditures`.
Do not substitute total `DryHoleExpense`, which also includes prior-year
write-offs. Other assets/liabilities use the selected CVX extension
`PaymentsToAcquireOtherProductiveAssetsLiabilities`; preserve the negative
2021 value and explicit 2024/2025 zeros. None is a Capex acceptance operand.

R12 explicitly excludes noncash balance-sheet changes and its PP&E footnote
excludes the noncash movements listed above. R27's book additions are a different
measure: they include business-combination fair values and prior-year dry-hole
write-offs. Do not reconstruct cash spending from a book roll-forward. The
2024 R12 comparative footnote states 316 for 2022, whereas selected 2022 R12
states 334. Preserve that comparative discrepancy; do not substitute it for
the selected-period disclosure or silently merge later comparatives.

## Acquisition containment and period-specific conclusions

| Year | Selected evidence | Conclusion / remaining blocker |
| --- | --- | --- |
| 2021 | R38 describes the October 2020 Noble stock transaction; R27 identifies 16,703 of acquired property in 2020, not 2021. R7's current-year cash-acquired line explicitly reports zero; annual extension `CashAcquiredFromAcquisition`, ordinal 312, is zero. R12 separately expands the aggregate to exploration, finance-lease/other-obligation asset additions and equity-affiliate spending. | Do not carry 2020 acquired assets into 2021 cash Capex or infer zero from an absent concept. The 7,515 component excludes noncash movements and investment/dry-hole components, but capitalized development/mineral and lease-input scope remains unproved. |
| 2022 | R38 identifies REG as an ASC 805 all-cash business acquisition, purchase price 3,155, acquired PP&E fair value 1,778, and tangible/intangible valuation. R7 separately reports business acquisition net of cash received of (2,862), tagged positive `PaymentsToAcquireBusinessesNetOfCashAcquired`, ordinal 304. | Business-combination cash is not the PP&E component and acquired fair-value PP&E is not an operand. Do not allocate the purchase price or infer acquired cash from differences. The 10,349 PP&E component still needs the cost-perimeter decision. |
| 2023 | R38/R39 identify PDC consideration of 6,520 in Chevron shares; R27 includes 10,487 acquired PP&E in book additions. R7 separately reports +55 net acquisition cash received, tagged -55 under the payments concept, ordinal 329. | Exclude acquired fair values and preserve the negative payments fact, not its absolute value. No subtraction from the 14,788 component is justified; the common cost-perimeter blocker remains. |
| 2024 | R38 describes the prior-year PDC acquisition and the still-pending Hess agreement; R27's 10,487 acquired-property comparative belongs to 2023. R7's selected annual business-acquisition payments fact explicitly reports zero, ordinal 333. | Neither prior-year PDC nor a pending Hess transaction authorizes a 2024 acquisition adjustment. The 15,544 component remains unapproved for the same cost-perimeter reason. |
| 2025 | R38 describes the July 18 Hess acquisition, stock consideration plus first-quarter Hess share purchases. R7 separately reports +1,056 net acquisition cash received (payments fact -1,056, ordinal 346) and (2,225) cash purchases of Hess stock (CVX `PaymentsToAcquireCommonStockDuringAcquisition`, ordinal 349). R27 identifies 73,538 acquired PP&E in book additions; R38 presents that fair value rounded to 73.5 billion. R12 expressly excludes acquisition-related noncash balance-sheet changes. | Keep both business-acquisition lines outside the 16,830 component. Do not count stock consideration, assumed debt, leases or fair-value assets as cash PP&E. The larger post-acquisition business perimeter is actual selected consolidated history, not a pro-forma comparable series. The same cost-perimeter blocker remains. |

Business-acquisition separation is supported by disclosed transaction nature
**and** distinct statement lines, not equality of cash, net-assets or asset
values. Subsequent ordinary cash investment in acquired subsidiaries is not
automatically a business-combination payment; invent no allocation. Nothing
here certifies CVX EBIT/affiliate or joint FCFF readiness.

## Other perimeter boundaries and unresolved methodology

- **Affiliates/consolidation:** R10 consolidates controlled subsidiaries and
  proportionate interests, with noncontrolled affiliates on the equity method;
  R24 documents that separate investment perimeter. R12 separately reports
  investment additions. Its 2021 bridge adds the company's share of affiliate
  expenditure only after capital/exploratory expenditure excluding affiliates.
  Neither that affiliate-inclusive total nor investment/loan payments is a
  replacement for consolidated cash PP&E.
- **Proceeds/gross spending:** the R7 asset-sale/return-of-investment inflows are
  1,791 / 2,635 / 669 / 7,704 / 1,826. R12 separately splits disposal proceeds
  and affiliate returns. Do not net this mixed inflow against PP&E or treat
  its productive-assets tag as pure PP&E disposal proceeds.
- **Leases:** R14 explicitly combines income-recognized and capitalized lease
  costs, and reports investing cash flows from operating leases of
  398 / 467 / 713 / 979 / 881. Financing principal is separately
  193 / 44 / 42 / 67 / 136. Noncash ROU recognition is not cash Capex. The
  investing lease amounts are not allocated between the reported PP&E component
  and other uses. Subtracting the whole amount would invent destination and
  overlap assumptions; ignoring the disclosure would not prove a purchase-only
  perimeter. Capitalized lease inputs may be legitimate construction costs:
  this review does not declare them incompatible or approve removing them.
  Existing AMZN/LLY acceptance of reported purchases, including evidenced
  construction scope, is not revoked. The question is the scope of this CVX
  component, not a new universal requirement to strip every construction input
  or to obtain a zero-lease certification for every policy.
- **Development/mineral costs:** R10's successful-efforts policy capitalizes
  development wells, related plant/equipment, proved mineral interests and
  qualifying exploratory wells. ARO asset recognition is noncash. The present
  primitive does not expressly settle the treatment of mineral interests and
  capitalized cash construction/service inputs for this exact component.
  Do not exclude all exploration, add expensed exploration, or recast mineral
  rights as PP&E solely from book classification or the oil/gas tag.
- **Intangibles/incentives:** REG's acquisition note explicitly discusses
  tangible/intangible valuation; these acquired amounts are outside ordinary
  cash purchases. The reviewed reports do not provide an exhaustive standalone
  software/intangible purchase split or incentive/netting allocation for the
  candidate. This is insufficient evidence, not evidence of zero. No hypothetical
  pre-incentive gross-up or intangible/lease residual equation is approved.

## Provenance, validation and bounded next milestone

All 36 report bodies were reused from retained `.bin` artifacts; **no new SEC
request** was needed. Gzip/base64 storage is lossless, and each explicitly typed
`sha256_sec_response_body_bytes` digest is over decompressed bytes, never
extracted text or parsed/reserialized JSON. All 15 existing R7/R10/R12 digests
matched their retained original bodies. The additional 21 report-body digests
are explicitly newly recorded review metadata, not replacements for old hashes.
Original retrieval timestamps/HTTP statuses were unavailable and remain null;
no fresh retrieval or invented metadata is claimed. Five selected-instance
digests also matched retained bytes before parsing. URLs, accession directory,
report location and retained-source path are recorded.

Validation reconciles five unique frozen identities, five candidate signatures,
five exact statement checks, five unresolved decisions, zero approvals and zero
equations. The frozen 57-row inventory and acceptance matrix remain unchanged;
its routing totals remain 37/17/3. Documentation links and `git diff --check`
pass. No source, policy, schema or tests changed; no tests/corpus were run.
Production counts are carried forward, not remeasured: Capex **157/47/0**;
aggregate **1,895/1,493/11/27/42**, total **3,468**; 43 completions/seven skips.

**Wave 29 next milestone (completed by Wave 30 above):** a documentation-only CVX Capex methodology
decision on reported cash construction/development/mineral costs and capitalized
lease inputs, using these five exact note sets. Decide whether the existing
primitive admits the reported component without an unsupported adjustment.
If it does, proceed later to exact-accession evidence design; if it requires
a pure-purchase split, identify the essential allocation evidence or retain
the gaps. Any primitive expansion must be explicit with an existing-policy
impact assessment, not implemented to obtain coverage. Do not repeat acquisition
inventory, research other issuers, or implement acceptance in that milestone.
