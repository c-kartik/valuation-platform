# GOOGL — company data preparation

CIK `1652044`; securities GOOGL, GOOG; **GENERALIZATION_REQUIRED**.

## Sources, history and retrieval

Frozen history: **5 periods**; selected ends: 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31.
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
| `commercial_paper` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `current_portion_of_long_term_debt` | 5/0/0/0/0 | derived 1, direct 4 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `depreciation_and_amortization` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../depreciation-amortization-concepts.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `diluted_weighted_average_shares` | 5/0/0/0/0 | derived 3, direct 2 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `income_tax_expense` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_debt_noncurrent` | 5/0/0/0/0 | derived 3, direct 2 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_marketable_securities` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `operating_income` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../operating-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `operating_nwc` | 0/0/0/5/0 | none | blocked issuer v1; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
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
checks passed; no fresh issuer financial review, SEC request or corpus run.
Remaining task: choose one explicit evidence/scenario
gap, not blanket company approval. Phase 2 forecast/valuation stays postponed.
