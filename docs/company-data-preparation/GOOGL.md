# GOOGL — company data preparation

CIK `1652044`; securities GOOGL, GOOG; **GENERALIZATION_REQUIRED**.

## Sources, history and retrieval

Frozen history: **5 periods**; selected ends: 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31.
Pipeline stage: `complete`; completion `True` is not support.
Original selected-accession SEC Company Facts / policy-directed filing-XBRL;
initial register preparation added no retrieval or new filing review. The bounded
FY2024 NWC bundle review below now binds exact operands to retained evidence;
other metadata absent from the compact matrix remains unreviewed. Do not extend
this review to other measures or periods; use linked evidence, not inference.

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
| `commercial_paper` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `current_portion_of_long_term_debt` | 5/0/0/0/0 | derived 1, direct 4 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `depreciation_and_amortization` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../depreciation-amortization-concepts.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `diluted_weighted_average_shares` | 5/0/0/0/0 | derived 3, direct 2 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `income_tax_expense` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_debt_noncurrent` | 5/0/0/0/0 | derived 3, direct 2 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_marketable_securities` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `operating_income` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../operating-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `operating_nwc` | 0/0/0/5/0 | none | blocked issuer v1; [methodology](../financial-methodology.md); [separate FY2024 partial review](#reviewed-fy2024-partial-input-bundle) below. No historical estimates/manual inputs; analyst note transcription is separately labeled. |
| `pretax_income` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `reported_effective_tax_rate` | 5/0/0/0/0 | derived 5 | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `revenue` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `short_term_borrowings` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `short_term_investments` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |

## Evidence and remaining blockers

Material core historical gaps remain: change_in_operating_nwc:methodology_blocked=4, depreciation_and_amortization:missing=5, operating_nwc:methodology_blocked=5. Pipeline completion does not satisfy support criteria.

Material core gaps: change_in_operating_nwc:methodology_blocked, depreciation_and_amortization:missing, operating_nwc:methodology_blocked.

- Compact runner evidence provides selected annual end dates and aggregate measure states, not individual context/occurrence digests; linked implementation and research evidence remains authoritative. No fresh filing retrieval or economic-absence certification.
- Historical resolution does not certify future FCFF timing or point-in-time valuation share denominator.
- Existing book Operating-NWC methodology remains blocked; integrated D&A/EBIT/inventory cash-timing compatibility unproved.
- Opening NWC change is NOT_COMPARABLE, not missing or zero; selected original-accession basis is not silently replaced by later comparatives.

[Complete issuer validation](../universe/phase-1h5-issuer-validation.json),
[failure taxonomy](../universe/sp500-top-50-failure-taxonomy.md),
[shared contracts and evidence-kind legend](index.md).

## Detailed NWC preparation

Frozen v1 blocks supplier AP and inventory perimeter. Narrow driver equation: AR − AP − current contract liabilities − employee − revenue share − accrued customer liabilities. Exclude inventory consistently in this labeled scenario; 2021/2022 reported 1,170m/2,670m, later missing disclosure is not zero. Expanded scenario needs explicit later allocations. 2024 rounded note supports 3,200m PP&E-in-AP; 2025 combined supplemental stock scope remains unproved. Customer accruals sit inside a broader caption and must not be counted twice. Recasts, acquisition/FX effects and missing D&A prevent FCFF certification.

[Three-issuer methodology/design](../analyst-operating-nwc-design.md),
[exact component/occurrence inventory](../analyst-operating-nwc-inventory.json),
[retained response bodies](../evidence/analyst-operating-nwc-response-bodies.json).

No analyst estimates, approved complete NWC or cash-adjusted ΔNWC are populated.
The isolated [implemented evaluator](../analyst-operating-nwc-design.md#implemented-isolated-foundation)
reproduces five narrow reported-driver levels/four book movements, with the
consistent inventory omission requiring explicit classification provenance.
Expanded unknown inventory prevents an amount; omitted disclosure is not zero.
Rounded source precision is retained, not converted to exact economic certainty.
The conditional 2025 stock-allocation proposal is not registered or implicitly
approved. Source byte/context/unit/occurrence checks and independent scenario
serialization preserve conflicts and omissions. Frozen v1 blockers and missing
D&A remain; no FCFF certification. 41 focused / 640 full-suite tests passed,
not a new company completeness review or approved estimate.

## Validation and next preparation

Reuse frozen issuer/measure counts and linked verified research. Source identity,
arithmetic and provenance must be validated before any future policy/scenario use;
unreviewed detail is not evidence of correctness. Register mapping/state/link
checks passed at initialization; that milestone added no fresh issuer financial
review, SEC request or corpus run. Its prior next task was to choose one explicit evidence/scenario
gap, not blanket company approval. Phase 2 forecast/valuation stays postponed.

## Reviewed FY2024 partial input bundle

Review date 2026-10-11; starting commit `73adc9557ba352dee09401c583f3d826b9832fb4`.
**GO only for explicitly labeled rounded partial-scenario use.** No complete
Operating NWC, cash ΔNWC or FCFF certification. This one Alphabet issuer record
covers GOOG/GOOGL; neither security creates another filing/level. Prior research
and frozen `googl_operating_nwc_valuation` v1 blockers remain unchanged.

Original conflicts: separately disclosed inventory disappears into a mixed
other-current caption in later periods; supplier AP includes investing credit;
customer accruals sit inside a broader accrued-liability caption. Considered
treatments: whole-AP diagnostic; subtract the explicitly isolated closing PP&E
credit from AP; or reconstruct all inventory/other operating allocations. Choose
only the **documented narrow perimeter with the supported rounded AP exclusion**.
Inventory is consistently omitted, not inferred zero. The remainder of AP is not
certified entirely operating; broader reconstruction lacks evidence. No parent
accrued caption is stacked with its isolated customer-liability component.

The [explicit version-1 bundle](googl-analyst-nwc-bundle.json) and
[source-binding/reproducibility tests](../../tests/analyst/test_googl_bundle.py)
follow existing [MSFT](MSFT.md#reviewed-fy20252026-partial-input-bundles) and
[AAPL](AAPL.md#reviewed-fy2025-partial-input-bundle) conventions: immutable model
inputs, typed original-body hashes, explicit classifications/limitations, separate
analyst serialization and no automatic production loader or policy approval.
Exact identity: CIK **1652044**, non-amended selected 10-K accession
**0001652044-25-000014**, FY **2024-01-01–2024-12-31**. Two retained original
statement/instance bodies are reused; unchanged inventory/manifest hashes bind
their retrieval provenance. No SEC requests or amended/later-comparative selection.

| Contribution / treatment | Reported USD m | Source occurrence / context / decimals |
| --- | ---: | --- |
| Net AR, add | 52,340 | 450 / c-9 instant / -6 |
| Whole AP, subtract once | 7,987 | 470 / c-9 instant / -6 |
| Current deferred revenue, subtract | 5,036 | 478 / c-9 instant / -6 |
| Compensation/benefits, subtract | 15,069 | 472 / c-9 instant / -6 |
| Accrued revenue share, subtract | 9,802 | 476 / c-9 instant / -6 |
| Isolated accrued customer liabilities, subtract | 4,304 | 1448 / c-9 instant / -6 |
| Rounded additional PP&E in AP, add back | 3,200 | 1459 / c-1 **duration** / -8 |
| Separate accrued PP&E, retain but omit | 7,104 | 1446 / c-9 instant / -6 |

All observations are non-nil/nondimensional USD (`usd`), entity `0001652044`.
Instant observations end 2024-12-31. Full namespaces, raw values, ordinals,
contexts, units and digests are retained in the bundle. Google extensions identify
revenue-share/customer/separate PP&E accruals; other listed concepts use us-gaap
2024. Evidence: consolidated balance sheet; accrued-expenses/other-current-
liabilities table and footnote (2); revenue, cash-flow, lease, derivative and
acquisition/reclassification context. Labels or numeric agreement alone do not
approve scope.

### Rounded note input and actual source representation

Footnote (2) expressly says **additional** PP&E purchases of **$3.2 billion as of
December 31, 2024 were included in accounts payable**; the table's separate
7,104m accrued PP&E is not that AP balance. The current inline fact is
`us-gaap:CapitalExpendituresIncurredButNotYetPaid`, ID `f-1104`, displayed `3.2`,
scale `9`, decimals `-8`. Extracted instance ordinal **1459** has raw
`3200000000`, unit `usd`, context **c-1: 2024-01-01–2024-12-31**, not an instant.
Its closing economic scope comes from the explicit note, not its duration tag.
The 2.8bn FY2023 comparative is not a reviewed opening operand.

The unchanged evaluator's native SEC-reported model verifies only instant facts.
Do **not** fabricate a closing `Occurrence` or label a duration fact as instant.
The adapter independently verifies both original bodies, actual XML fact/context/
unit/ordinal and inline value/scale/precision plus the complete closing-scope
sentence. It then supplies an explicit **`manual_input`**, `precision="rounded"`,
with reviewer/date/rationale and note-to-closing interpretation assumptions.
This is reviewed transcription of a reported rounded value, **not an estimated
allocation**. Actual duration-occurrence and inline/scope metadata are serialized
in evidence references, with both verified bodies; `occurrences=()` is deliberate.
No production parser/schema change or generic duration-to-stock inference.

Consequently `assumption_dependent=True` exposes the manual note interpretation;
it is not silently relabeled automatically SEC-resolved. Generic deserialization
rechecks model/provenance/digests and recomputes arithmetic; reviewed note binding
is enforced by the bundle adapter, not a new native duration verifier. No new
manual input is automatically accepted merely because it has a source reference.

Equation at reported precision: **52,340 − 7,987 − 5,036 − 15,069 − 9,802 −
4,304 + 3,200 = 13,342m**; unadjusted driver = 10,142m. AP after this known
rounded exclusion = **4,787m**, not certified pure operating AP. Available outcome
is `partial_perimeter`; complete-NWC/FCFF flags false. Exact Decimal arithmetic
on disclosed points does **not** establish an economic amount precise to 1m:
the adjustment is rounded to 0.1bn and that source precision remains attached.
No fabricated uncertainty interval or unrounded amount is introduced.

### Omissions and continuing limitations

- Inventory is unquantified and explicitly outside the narrow perimeter.
  Earlier 1,170m/2,670m balances and FY2024 other-current assets **15,714m** do not
  establish current inventory, zero absence, or an approved current allocation.
- Mixed other-current assets include investment/derivative collateral as well
  as possible operating balances. The gross caption is exposure, not an estimate
  of excluded operating investment or a net uncertainty bound.
- Accrued expenses/other-current liabilities **51,228m** include the separately
  selected customer balance, fines, PP&E, taxes, leases and mixed obligations.
  Do not subtract this parent caption again. Separate 7,104m PP&E evidence is
  retained outside the calculation, never added to or subtracted from AP's 3.2bn
  correction. Fines/settlements require consistency with recurring EBIT treatment.
- Remaining supplier AP scope stays unproved after the known exclusion; a
  required additional allocation or inventory amount gives `input_unavailable`,
  not a default estimate. Cash/investments/funding/taxes and leases/noncurrent
  balances remain outside this partial perimeter under existing methodology.
- Acquisition/disposal, FX, noncash movements and cross-perimeter recasts are
  unbridged. Cash-flow operating rows explicitly exclude acquisition effects;
  balance movements are not independently certified cash investment. One level
  supplies **no ΔNWC**: opening bundle absent, `opening_unavailable`, no amount,
  `cash_investment_certified=False`.
- Alphabet's D&A remains missing; integrated EBIT/tax/D&A/Capex/inventory/lease
  timing remains unproved. Unknown readiness is not proven incompatibility.
  Neither the conditional FY2025 6,213m stock proposal nor any other-period
  allocation is approved. Phase 2 remains postponed.

Validation: **66 relevant tests passed** (41 foundation + eight MSFT + eight AAPL
and nine Alphabet). One frozen identity, two original-body digests, six included
instant facts, one excluded instant fact and one actual duration-tagged note
verified. Inline/extracted precision and scope reconcile; scenario/evaluation
serialization retain manual classification, assumptions, duration metadata,
omissions and rounded diagnostics. Identity/amendment/comparative, source/hash,
context/unit/nil, precision/concept/scope and missing-input failures reject.
Links, compileall and diff checks pass; no production source changes, SEC
requests, full suite or corpus rerun. All seventeen frozen rows, NWC blockers,
missing D&A and baseline 1,905/1,483/11/27/42 = 3,468 remain unchanged.

The bounded bundle-review pass is complete. Remaining practical valuation-use
obstacles and **one decision milestone**, not another issuer-research cycle, are
in the [cross-issuer decision summary](../analyst-operating-nwc-design.md#remaining-obstacles-and-bounded-valuation-use-decision).

## FY2024 alternative reported cash-flow evidence review

2026-10-12; [exact evidence/input matrix](../googl-alternative-historical-cash-flow-inputs.md).
Original inventory/supplier-AP scope conflicts and missing D&A remain. Considered
book reconstruction versus preserving consolidated reported CFO; PARTIAL GO for
separate reported-input preparation design only. No MSFT/AAPL analyst treatment
or new Alphabet bundle is approved. Identity stays selected accession
0001652044-25-000014, 2024-01-01–2024-12-31, nondimensional c-1.

Verified CFO 125,299m reproduces thirteen statement terms; PP&E cash 52,535m is
narrow investment, not complete reinvestment. Rounded tax cash 27,400m (−8) is
distinct from provision 19,697m. CFO SBC add-back 22,785m (−6) and note expense
22,800m (−8) preserve different source precision, not equal exact values or two
costs. Independent SBC/lease/tax choices remain for review, no rate or proxy.

Note 4 separates operating lease cash 3,425m, finance interest cash 31m (both
operating) and finance principal 405m (financing, already inside face debt
repayments 12,701m). Noncash ROU additions and variable expense are separate;
total variable/nonlease cash and borrowing interest remain unproved. Note 7
interest expense 268m is net of capitalized expense 194m, not cash. Combined
acquisition/intangible payment 2,931m remains unallocated; Character note cash
and asset recognition are not a complete bridge or residual allocation.

CFO reported asset/liability changes exclude acquisition effects, but acquired
operations enter consolidation from acquisition date. Reported CFO reproduction
does not need missing inventory or complete closing AP/3.2bn-creditor
reconstruction; it does not certify organic trends, cash ΔNWC or timing. The
PP&E depreciation reconciliation 15,311m does not resolve the separate D&A
primitive: all five missing D&A states and original NWC blockers persist.
Comparative annual columns remain supporting evidence, not registered bundles.

Two retained original bodies/hashes/lengths verify source identity. Primary
receipt records timestamp/status; the reused extracted-instance record has
**unrecorded retrieval time/HTTP status**. Do not fabricate a receipt or imply
it meets the existing reported-bundle loader requirements. Exact-instance
receipt provenance must be recovered/verified before any implementation.
Preserve old body/digest/history if a separately authorized refresh is needed.

Validation: exact annual identity/QNames/occurrences, precision/unit/scope,
thirteen-term CFO and both comparative statement columns, references/links and
diff check. No SEC requests, tests/corpus, source/evidence/scenario changes;
baseline **1905/1483/11/27/42 = 3468** unchanged. Single next Phase 1 milestone:
bounded receipt-provenance recovery for this exact instance, not broad issuer
research or altered acceptance rules. Stop after this review.
