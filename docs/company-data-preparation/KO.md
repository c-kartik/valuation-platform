# KO — company data preparation

CIK `21344`; securities KO; **GENERALIZATION_REQUIRED**.

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
| `change_in_operating_nwc` | 0/4/0/0/1 | none | no approved issuer perimeter; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `commercial_paper` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `current_portion_of_long_term_debt` | 3/2/0/0/0 | direct 3 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `depreciation_and_amortization` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../depreciation-amortization-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `diluted_weighted_average_shares` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `income_tax_expense` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_debt_noncurrent` | 3/2/0/0/0 | direct 3 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `long_term_marketable_securities` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `operating_income` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../operating-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `operating_nwc` | 0/5/0/0/0 | none | no approved issuer perimeter; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `pretax_income` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `reported_effective_tax_rate` | 5/0/0/0/0 | derived 5 | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `revenue` | 5/0/0/0/0 | direct 5 | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `short_term_borrowings` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |
| `short_term_investments` | 0/5/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); unresolved source details unreviewed. Assumptions/manual/external: none supplied. |

## Evidence and remaining blockers

Material core historical gaps remain: change_in_operating_nwc:missing=4, operating_nwc:missing=5. Pipeline completion does not satisfy support criteria.

Material core gaps: change_in_operating_nwc:missing, operating_nwc:missing.

- Compact runner evidence provides selected annual end dates and aggregate measure states, not individual context/occurrence digests; linked implementation and research evidence remains authoritative. No fresh filing retrieval or economic-absence certification.
- Historical resolution does not certify future FCFF timing or point-in-time valuation share denominator.
- Opening NWC change is NOT_COMPARABLE, not missing or zero; selected original-accession basis is not silently replaced by later comparatives.

[Complete issuer validation](../universe/phase-1h5-issuer-validation.json),
[failure taxonomy](../universe/sp500-top-50-failure-taxonomy.md),
[shared contracts and evidence-kind legend](index.md).

## Validation and next preparation

Reuse frozen issuer/measure counts and linked verified research. Source identity,
arithmetic and provenance must be validated before any future policy/scenario use;
unreviewed detail is not evidence of correctness. Register mapping/state/link
checks passed; no fresh issuer financial review, SEC request or corpus run.
Remaining task: choose one explicit evidence/scenario
gap, not blanket company approval. Phase 2 forecast/valuation stays postponed.
