# AAPL — company data preparation

CIK `320193`; securities AAPL; **GENERALIZATION_REQUIRED**.

## Sources, history and retrieval

Frozen history: **5 periods**; selected ends: 2021-09-25, 2022-09-24, 2023-09-30, 2024-09-28, 2025-09-27.
Pipeline stage: `complete`; completion `True` is not support.
Original selected-accession SEC Company Facts / policy-directed filing-XBRL;
initial register preparation added no retrieval or new filing review. The bounded
FY2025 NWC bundle review below now binds exact operands to retained evidence;
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
| `current_portion_of_long_term_debt` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `depreciation_and_amortization` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../depreciation-amortization-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `diluted_weighted_average_shares` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `income_tax_expense` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_debt_noncurrent` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_marketable_securities` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
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

Frozen v1 blocks employee liability evidence/materiality and distribution/marketing (only 2025 exact disclosure). Narrow driver equation: AR + vendor nontrade + inventory − whole AP − current deferred revenue. Employee/distribution omissions and unknown PP&E-in-AP contamination are explicit limitations, not zeros. Expanded scenarios need separately scoped accruals; 2025 distribution 8,919m is reported, not an estimate; do not import its 2024 comparative. Other-current captions mix tax, leases and other items. No cash ΔNWC acquisition/FX/noncash bridge or integrated timing proof.

[Three-issuer methodology/design](../analyst-operating-nwc-design.md),
[exact component/occurrence inventory](../analyst-operating-nwc-inventory.json),
[retained response bodies](../evidence/analyst-operating-nwc-response-bodies.json).

No analyst estimates, approved complete NWC or cash-adjusted ΔNWC are populated.
The isolated [implemented evaluator](../analyst-operating-nwc-design.md#implemented-isolated-foundation)
reproduces all five reported-driver partial levels and four book movements.
Omissions need classification provenance; unknown required employee/distribution
or AP allocations prevent expanded scenario amounts. No default zeros,
later-comparative backfill or cash/FCFF certification. Scenario evidence and
submitted precision survive separate analyst serialization; frozen v1 remains
blocked. The 41 focused / 640 full-suite tests include these retained operands,
not a new company completeness review or approved analyst estimate.

## Validation and next preparation

Reuse frozen issuer/measure counts and linked verified research. Source identity,
arithmetic and provenance must be validated before any future policy/scenario use;
unreviewed detail is not evidence of correctness. Register mapping/state/link
checks passed at initialization; that milestone added no fresh issuer financial
review, SEC request or corpus run. Its prior next task was to choose one explicit evidence/scenario
gap, not blanket company approval. Phase 2 forecast/valuation stays postponed.

## Reviewed FY2025 partial input bundle

Review date 2026-10-11; starting commit `d07c980317be85e333baa6390cd342ead32e86a1`.
**GO only for explicitly labeled narrow reported-driver partial-scenario use.**
NO-GO for complete Operating NWC, operating-only AP, ΔNWC or FCFF certification.
The prior five-period diagnostics above remain historical research, not five
reviewed bundles. Frozen `aapl_operating_nwc_valuation` v1 blockers and support
classification are unchanged; this review does not supersede them.

Original conflicts: employee cash accruals are not isolated; distribution and
marketing was separately disclosed in only one frozen selected filing; whole
supplier AP may contain investing obligations. Considered treatments were a
documented narrow reported-driver perimeter, adding known distribution, and
expanding to fully classified operating balances/AP. Choose **only the documented
narrow perimeter**, with explicit omissions and contamination warnings. No
expanded equation is approved here. Reported distribution is retained, not
misrepresented as unavailable; employee and investing-in-AP allocations remain
unknown. No residual, numerical agreement or materiality waiver proves completeness.

The [explicit version-1 bundle](aapl-analyst-nwc-bundle.json) and
[reproducibility tests](../../tests/analyst/test_aapl_bundle.py) follow the
[reviewed MSFT convention](MSFT.md#reviewed-fy20252026-partial-input-bundles):
reference the unchanged inventory/manifest hashes, verify original response-body
representations and typed byte digests, construct existing immutable models and
evaluate/serialize through the unchanged pure evaluator. The adapter is test-only,
not an automatic loader, policy registry or default scenario.

Exact identity: CIK **320193**, selected non-amended 10-K accession
**0000320193-25-000079**, authoritative FY **2024-09-29–2025-09-27**; current
instant **2025-09-27**. Two retained original bodies (statement and extracted
instance) bind the assertions and observations. All six reviewed numeric
occurrences are nondimensional, non-nil USD (`usd`), context `c-20`, entity
`0000320193`, with submitted `decimals=-6`. Five included concepts use
us-gaap namespace `http://fasb.org/us-gaap/2025`; the omitted distribution fact
uses `http://www.apple.com/20250927`. Full namespace, raw value, context/unit,
source ordinal and SHA-256 identities are in the bundle, not inferred from labels.

| Component / treatment | Reported USD m | Root-child occurrence ordinal |
| --- | ---: | ---: |
| Net customer AR, add | 39,777 | 370 |
| Vendor non-trade receivables, add | 33,180 | 372 |
| Book inventory, add | 5,718 | 374 |
| Whole reported AP, subtract; operating purity unproved | 69,860 | 390 |
| Current deferred revenue, subtract | 9,055 | 394 |
| Distribution/marketing, retain but omit | 8,919 | 880 |

Reviewed statement/note evidence: consolidated balance sheet identifies all five
driver balances; Note 1 supports FIFO inventory; vendor non-trade disclosure
explains component sales to manufacturing vendors, with gains reducing product
cost of sales rather than product revenue; Note 2 explains deferred revenue;
Note 6 separately discloses distribution/marketing within other-current
liabilities. Leases, taxes and cash-flow disclosures supply scope cross-checks,
not a complete operating allocation or cash reconciliation. Exact scope passages
are tested against the verified retained statement, not re-fetched SEC material.

Evaluator result: **39,777 + 33,180 + 5,718 − 69,860 − 9,055 = −240m**,
`partial_perimeter`. This is book reported-driver arithmetic, not an approved
SEC-derived Operating NWC value. Whole AP is used transparently; no zero PP&E
allocation or claim of operating-only AP is embedded in acceptance. The unknown
positive investing-in-AP correction is explicitly outside this diagnostic;
requiring it in an operating-only scenario yields `input_unavailable`.

### Omissions, precision and unresolved effects

- Employee cash accruals: unquantified, explicitly omitted. Share-based award
  expense and a mixed-liability residual cannot substitute for a current balance.
- Distribution/marketing: **known 8,919m**, explicitly outside the chosen narrow
  perimeter. Both its reported evidence and omission classification survive
  serialization. Its omission is an analyst scope judgment, not a finding of
  zero, immateriality or non-operating character. The 7,679m FY2024 comparative
  is not a FY2024 approved operand/bundle. No automatic expanded −9,159m scenario.
- Other-current assets **14,585m** and liabilities **66,387m** are gross exposure,
  not operating estimates or net uncertainty bounds. Note 6 identifies income
  taxes **13,016m**, distribution **8,919m** and remaining mixed liabilities
  **44,452m**; that remainder is not inferred employee compensation. Never stack
  whole other-current liabilities with separately included subcaptions.
- Cash/investments, funding and separately modeled income taxes remain outside;
  leases await integrated treatment; noncurrent operating balances are excluded
  by the current-book perimeter. Other genuine operating balances may be omitted.
- Arithmetic is exact Decimal summation of **rounded reported points** at
  submitted million-dollar precision. No fabricated interval or rounding
  tolerance is supplied; original raw values and precision remain traceable.
- Acquisition/disposal, FX, noncash and reclassification effects remain unbridged,
  not assumed zero. Cash-flow rows mix current/noncurrent captions; near agreement
  with book movements cannot certify this perimeter's cash investment. Inventory,
  EBIT/tax, D&A, Capex and lease timing compatibility is unproved, not demonstrated
  incompatible. The future joint timing gate remains required.
- **One reviewed level does not establish ΔNWC.** No reviewed opening bundle is
  supplied: `change(None, result)` gives `opening_unavailable`, amount absent,
  `cash_investment_certified=False`. Earlier research's driver changes do not
  supply an approved opening or permit implicit period extension.

`is_complete_operating_nwc=False`, `fcff_ready=False`; numerical
`assumption_dependent=False` means no estimates were used, not absence of analyst
scope judgments. No manual/external inputs, default estimates or automatic
blocker removal. Frozen NWC remains 5 methodology-blocked states; ΔNWC remains
4 blocked / one not-comparable. All seventeen historical measure rows stay intact.

Validation: **57 relevant tests passed** (41 foundation + eight MSFT + eight AAPL).
One frozen identity, two typed original-body digests, six exact occurrences,
scope passages, included sum/omitted fact, unknown-required-input failure,
scenario/evaluation serialization and absent opening checked. Changed identities,
amendments, precision/source/occurrence mismatches, dimension/nil/non-USD inputs,
missing operands/omission evidence and comparative substitution reject. Local
links, compileall and `git diff --check` pass. No production source changes,
SEC requests, full suite or corpus rerun; frozen evidence and baseline counts
1,905/1,483/11/27/42 = 3,468 remain unchanged.

Smallest next milestone: review one explicit **GOOGL FY2024 partial bundle** using
retained evidence, with inventory omitted consistently and the rounded PP&E-in-AP
note assessed under the existing design. Do not approve the conditional FY2025
stock allocation, earlier-period extension, cash ΔNWC or Phase 2 restart.

## FY2025 alternative reported cash-flow input review

2026-10-12; [exact evidence/input matrix](../aapl-alternative-historical-cash-flow-inputs.md).
Original conflict remains incomplete employee/distribution and supplier-AP
allocation for book NWC. Considered complete reconstruction versus preservation
of consolidated reported CFO. Choose **PARTIAL GO for data-only packaging design**:
reported CFO needs no reconstructed opening NWC, employee/distribution split or
PP&E-creditor allocation to reproduce its subtotal. This is not removal of those
blockers or approval of MSFT's economic treatments for AAPL.

Selected FY2025 accession 0000320193-25-000079, 2024-09-29–2025-09-27,
nondimensional annual context c-1; two retained original bodies/digests verified.
The reported CFO reconciliation reproduces 111,482m; separate cash PP&E 12,715m,
net cash taxes 43,369m and SBC expense/add-back 12,863m are supported. Mixed
investing Other 1,480m remains unallocated. Note 8 fixed operating-lease cash
2,100m is rounded at −8; variable lease expense 16,100m is not cash. Noncash
ROU additions 2,800m are not investment payments. Cash borrowing interest and
separate finance-lease interest/principal cash are not established. No zero,
expense-to-cash proxy, residual acquisition allocation or total is supplied.

FY2024/FY2023 annual comparative observations in this selected filing reproduce
their reported CFO columns, but are not new registered bundles or substitutes
for original selected filings. AAPL has five frozen history periods; the existing
reviewed partial scenario remains FY2025 only. Prior 53-week and note-reclassification
boundaries persist. No comparative ΔNWC or cash comparability is approved.

Proposed future choices: separately register only supported reported inputs and
explicit unknowns; review AAPL-specific SBC, lease and tax treatments separately
before any economic use. Corporate cash taxes, tax provision and employee-tax
financing are distinct; Ireland/escrow-related notes do not establish a complete
recurring cash-tax bridge. Acquisition/intangible reinvestment, FX/reclassification
and integrated timing remain unproved. No complete NWC/FCFF certification.

Validation: selected identity/contexts, typed original-body hashes and lengths,
numeric occurrence/unit/precision/sign evidence, three displayed CFO column sums,
local links and diff check pass. No SEC requests, tests/corpus, source/policy/
schema/scenario changes. Frozen baseline **1905/1483/11/27/42 = 3468** retained.
Smallest next Phase 1 milestone: one isolated FY2025 reported-input bundle with
explicit interest/lease/investment unknowns; no automatic treatment transfer,
economic calculation or comparative registration. Stop after this review.
