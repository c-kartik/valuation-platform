# MSFT — company data preparation

CIK `789019`; securities MSFT; **GENERALIZATION_REQUIRED**.

## Sources, history and retrieval

Frozen history: **5 periods**; selected ends: 2022-06-30, 2023-06-30, 2024-06-30, 2025-06-30, 2026-06-30.
Pipeline stage: `complete`; completion `True` is not support.
Original selected-accession SEC Company Facts / policy-directed filing-XBRL;
no retrieval or new filing review in preparation. Exact metadata not present in
compact matrix remains unreviewed; use underlying linked research, not inference.

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
checks passed; no fresh issuer financial review, SEC request or corpus run.
Remaining task: choose one explicit evidence/scenario
gap, not blanket company approval. Phase 2 forecast/valuation stays postponed.
