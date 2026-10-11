# XOM — company data preparation

CIK `2115436`; securities XOM; **GENERALIZATION_REQUIRED**.

## Sources, history and retrieval

Frozen history: **0 periods**; selected ends: none.
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
| `capex` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../capex-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `cash_and_cash_equivalents` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `change_in_operating_nwc` | 0/0/0/0/0 | none | no approved issuer perimeter; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `commercial_paper` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `current_portion_of_long_term_debt` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `depreciation_and_amortization` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../depreciation-amortization-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `diluted_weighted_average_shares` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `income_tax_expense` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_debt_noncurrent` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `long_term_marketable_securities` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `operating_income` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../operating-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `operating_nwc` | 0/0/0/0/0 | none | no approved issuer perimeter; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `pretax_income` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `reported_effective_tax_rate` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../pretax-income-concepts.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `revenue` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `short_term_borrowings` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |
| `short_term_investments` | 0/0/0/0/0 | none | v1 snapshot/shared contracts; [evidence](../financial-methodology.md); retain source/precision and comparability limits. Assumptions/manual/external: none supplied. |

## Evidence and remaining blockers

Generic execution completes but strict current-CIK association yields empty history; predecessor succession is not established by approved generic evidence. No material historical coverage.

Material core gaps: see validation rationale.

- Compact runner evidence provides selected annual end dates and aggregate measure states, not individual context/occurrence digests; linked implementation and research evidence remains authoritative. No fresh filing retrieval or economic-absence certification.
- Historical resolution does not certify future FCFF timing or point-in-time valuation share denominator.
- Five-year target unavailable; no hardcoded predecessor traversal.

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
