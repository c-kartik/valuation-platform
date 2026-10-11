# MSFT — company data preparation

CIK `789019`; securities MSFT; **GENERALIZATION_REQUIRED**.

## Sources, history and retrieval

Frozen history: **5 periods**; selected ends: 2022-06-30, 2023-06-30, 2024-06-30, 2025-06-30, 2026-06-30.
Pipeline stage: `complete`; completion `True` is not support.
Original selected-accession SEC Company Facts / policy-directed filing-XBRL;
initial register preparation added no retrieval or new filing review. The bounded
FY2025–2026 review below now binds exact NWC operands to retained evidence; other
metadata absent from the compact matrix remains unreviewed. Use linked research,
not inference, and do not extend this review to other measures.

## All seventeen measures

R/M/A/B/NC = resolved/missing/ambiguous/methodology-blocked/not-comparable.
Source kind counts classify existing resolved outputs only. Every row has the
same recorded history; missing disclosures/conflict reasons require source-level
review where not documented. No absent balance is certified as zero.

| Measure | R/M/A/B/NC | Retained source kinds | Policy/research; remaining preparation |
| --- | --- | --- | --- |
| `capex` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../capex-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `cash_and_cash_equivalents` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `change_in_operating_nwc` | 0/0/0/4/1 | none | blocked issuer v1; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `commercial_paper` | 2/3/0/0/0 | direct 2 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `current_portion_of_long_term_debt` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `depreciation_and_amortization` | 5/0/0/0/0 | derived 5 | MSFT component v1; [evidence](../depreciation-amortization-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `diluted_weighted_average_shares` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `income_tax_expense` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_debt_noncurrent` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_marketable_securities` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `operating_income` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../operating-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `operating_nwc` | 0/0/0/5/0 | none | blocked issuer v1; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `pretax_income` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `reported_effective_tax_rate` | 5/0/0/0/0 | derived 5 | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `revenue` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `short_term_borrowings` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `short_term_investments` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |

## Evidence and remaining blockers

Material core historical gaps remain: change_in_operating_nwc:methodology_blocked=4, operating_nwc:methodology_blocked=5. Pipeline completion does not satisfy support criteria.

Material core gaps: change_in_operating_nwc:methodology_blocked, operating_nwc:methodology_blocked.

- Compact runner evidence provides selected annual end dates and aggregate measure states, not individual context/occurrence digests; linked implementation and research evidence remains authoritative. No fresh filing retrieval or economic-absence certification.
- Historical resolution does not certify future FCFF timing or point-in-time valuation share denominator.
- Existing book Operating-NWC methodology remains blocked; integrated D&A/EBIT/inventory cash-timing compatibility unproved.
- Opening NWC change is NOT_COMPARABLE, not missing or zero; selected original-accession basis is not silently replaced by later comparatives.

[Complete issuer validation](../universe/phase-1h5-issuer-validation.json),
[failure taxonomy](../universe/sp500-top-50-failure-taxonomy.md),
[shared contracts and evidence-kind legend](index.md).

## Detailed NWC preparation

Frozen v1 blocks supplier AP scope. Driver equation: AR + inventory − AP − current unearned revenue − employee accruals. Only exact FY2025/2026 filings isolate PP&E remaining in AP, 6,900m/26,700m. Excluding those gives AP 20,824m/15,716m; adjacent movement effect +19,800m. Earlier selected allocations remain unknown; later comparatives cannot backfill. Other-current/strategic-component balances remain separately gated. Nuance/Activision, FX/noncash and timing effects prevent certifying cash ΔNWC.

[Three-issuer methodology/design](../analyst-operating-nwc-design.md),
[exact component/occurrence inventory](../analyst-operating-nwc-inventory.json),
[retained response bodies](../evidence/analyst-operating-nwc-response-bodies.json).

No analyst estimates, approved complete NWC or cash-adjusted ΔNWC are populated.
The isolated [implemented evaluator](../analyst-operating-nwc-design.md#implemented-isolated-foundation)
reproduces five reported-driver levels/four book movements and the two exact
selected FY2025/FY2026 PP&E-in-AP corrections. Tests reproduce unadjusted
-12,908m versus adjusted +6,892m movement: **19,800m effect**, with original
operands/precision retained. Results remain partial book perimeters, not complete
NWC/cash investment or FCFF readiness. Earlier required allocations stay unknown;
no later comparative backfill or default estimate. Frozen v1 stays blocked.
41 focused / 640 full-suite tests passed; this is retained-evidence arithmetic,
not a new approval of historical perimeters.

## Validation and next preparation

Reuse frozen issuer/measure counts and linked verified research. Source identity,
arithmetic and provenance must be validated before any future policy/scenario use;
unreviewed detail is not evidence of correctness. Register mapping/state/link
checks passed at initialization; no fresh issuer financial review, SEC request
or corpus run in that milestone. Its prior next task was to choose one explicit evidence/scenario
gap, not blanket company approval. Phase 2 forecast/valuation stays postponed.

## Reviewed FY2025–2026 partial input bundles

Review date 2026-10-11; starting commit `0af29bf40a3b2ac7d22cba906f140d0f77ff826e`.
**GO for explicitly selected partial scenarios only; NO-GO for complete Operating
NWC, cash-adjusted ΔNWC or FCFF certification.** The prior five-period driver
diagnostic and frozen `msft_operating_nwc_valuation` v1 blockers above remain
unchanged; these two bundles do not supersede them or approve earlier periods.

Original conflict: subtracting whole supplier AP also subtracts disclosed PP&E
supplier credit, an investing obligation. Considered treatments: keep whole AP
as a diagnostic comparator; remove the isolated investing balance; or expand to
all operating assets/liabilities. Choose only the second, within a deliberately
partial perimeter. Expansion lacks complete classifications and cash bridges;
whole AP is not an economically approved alternative. No residual allocation,
materiality waiver or assumed-zero omitted balance is used.

The [version-1 explicit bundles](msft-analyst-nwc-bundles.json) bind CIK 789019,
non-amended 10-K annual identities, original statement/instance URLs and four
typed byte digests to the unchanged inventory and response-body manifest hashes.
The JSON is analyst input preparation, not a production policy registry or a new
serialization schema. Its [reproducibility tests](../../tests/analyst/test_msft_bundles.py)
materialize existing immutable `Scenario`/`Evidence` models and invoke the pure
evaluator; there is no automatic runtime loading or selection. Explicit omission
classifications retain reviewer/date/rationale and selected statement evidence.

| Frozen filing / annual period | Whole-AP driver, USD m | PP&E in AP, USD m | Adjusted AP, USD m | Evaluated partial level, USD m |
| --- | ---: | ---: | ---: | ---: |
| 0000950170-25-100235 / 2024-07-01–2025-06-30 | -35,145 | 6,900 | 20,824 | -28,245 |
| 0001193125-26-323660 / 2025-07-01–2026-06-30 | -48,053 | 26,700 | 15,716 | -21,353 |

Exact source review: each filing's consolidated balance sheet identifies AR,
inventories, accounts payable, accrued compensation and short-term unearned
revenue; Note 1 provides receivable/inventory accounting context; **Note 6 —
Property and Equipment** explicitly says the PP&E purchases are *remaining in
accounts payable* as of closing. This is an instant investing balance, not annual
cash spending. Note 7 and the cash-flow statement supply acquisition/cash-flow
context, not an exhaustive component bridge. All six operands per bundle use
their exact selected instance namespaces (us-gaap 2024/2025 and the corresponding
Microsoft extension for PP&E in AP), current closing context, entity 0000789019,
empty dimensions and `U_USD`. All twelve eligible occurrences are retained with
root-child ordinals; none is summed twice or replaced with later comparatives.

Equation: **AR + book inventory − AP − current unearned revenue − accrued
compensation + PP&E remaining in AP**. Customer receivables, inventories and
customer/employee accruals support the narrowed operating classification;
remaining AP is a candidate operating balance after this known exclusion, not
proof that every remaining payable is operating. The positive PP&E correction
removes investing credit already included in negative AP; it does not add an
operating asset or measure Capex cash. The calculated subtotal is scenario
arithmetic over reported facts, not a new approved SEC-derived NWC primitive.

Adjusted adjacent book movement is **+6,892m**, versus **−12,908m** in the explicit
whole-AP comparator. Difference = 26,700 − 6,900 = **+19,800m**. Both use the same
annual boundaries and stable components within their respective scenarios;
mixing adjusted/unadjusted scenario identities is rejected. FY2025's bundle
opening is unavailable: no FY2024 adjusted amount is supplied or inferred.

### Omissions, uncertainty and downstream limits

- Mixed other-current assets: 25,723m/48,594m; mixed other-current liabilities:
  25,020m/26,738m. These are reported gross exposure, **not** estimated operating
  allocations or bounds on net ΔNWC. All are explicitly outside this partial
  perimeter, not zero or immaterial.
- Note 1 separately describes server-component facilitation receivables within
  other-current assets (8.2bn FY2025; 27.8bn current FY2026). They are not silently
  added to customer AR. Customer-financing disclosures combine short/long terms;
  current operating allocations and contract-cost timing are not completed here.
  Omission may exclude genuine operating investment; it is not a finding that
  every other-current asset is non-operating.
- Cash/investments/funding and separately modeled income taxes remain outside;
  leases await integrated treatment. Noncurrent operating balances are omitted
  by the current-book perimeter. No tax, lease, employee or inventory estimate
  or external/manual numerical input is supplied.
- Core inputs have submitted `decimals=-6`; the 6.9bn/26.7bn PP&E disclosures have
  `decimals=-8`. Raw points, namespace/context/unit/ordinal and original bodies
  survive serialization. Decimal sums are exact arithmetic **at reported
  precision**, not exact economic allocations. No fabricated rounding interval
  or tolerance is introduced.
- Acquisition/disposal allocations (including carried-forward effects), FX,
  noncash changes and transfers across the perimeter remain unbridged, not
  assumed zero. Prior Nuance/Activision evidence establishes exposure, not
  current component allocations. Cash-flow account movements cannot replace
  closing book balances or certify a residual cash reconciliation.
- Book inventory/contract costs, EBIT/taxes, MSFT D&A and Capex require the joint
  timing-readiness review before eventual consumption. Unknown compatibility
  is not demonstrated incompatibility. Evaluator outputs remain
  `partial_perimeter` / `partial_book_movement`, complete-NWC/FCFF flags false,
  `cash_investment_certified=False`. No blocker or support classification changes.
  `assumption_dependent=False` means no numerical estimate was used; explicit
  analyst scope judgments and incompleteness still remain.

Validation: 49 relevant tests pass (41 existing + eight bundle tests); both
identities, four original-body digests, twelve occurrences, note assertions,
level/AP arithmetic, adjacent movement/effect and source precision checked.
Tests reject changed identity/digest/ordinal/value/equation, amendments and
earlier/future extension; required unknown allocations remain unavailable;
explicit omissions and self-contained serialization retain provenance. Relevant
local links and `git diff --check` pass. No SEC requests, source changes, full
suite or corpus rerun; frozen v1 and baseline counts remain unchanged.

Smallest next milestone: review one explicit **AAPL FY2025 partial scenario
bundle** from retained evidence, including employee/distribution omissions and
unknown investing-in-AP allocation. No numerical estimate, other-period
extension, cash bridge or automatic readiness approval is authorized by this
MSFT review. Phase 2 remains postponed.
