# Phase 1 retained selected-filing identity manifest

2026-10-12; starting HEAD `48b5d8be3a454926dd912045444d5444b4f75f45`.
[Manifest](phase1-selected-filing-identity-manifest.json) reconciles 40 issuers,
189 selected annual periods and 11 five-period-target history exceptions.
[Offline builder](../scripts/build_selected_filing_manifest.py) reuses existing
binding path/digest conventions. Run
`.venv/bin/python scripts/build_selected_filing_manifest.py` for reproducible
JSON (formatting may differ from the compact retained rows).

## Results and verification depth

| Selected-period identity status | Count | Meaning |
| --- | ---: | --- |
| VERIFIED_RETAINED_IDENTITY | 162 | One consistent exact accession/form/annual identity supported by retained reviewed filing/DEI evidence |
| MISSING_BINDING | 26 | No matching exact identity in this bounded source set; not proof a filing does not exist |
| INCOMPLETE_BINDING | 1 | Candidate exists but authoritative annual evidence unresolved; not promoted |
| CONFLICTING | 0 | No competing eligible identity signatures found |
| HISTORY_EXCEPTION | 11 separately | Unfilled target slots, not selected or invented fiscal years |

Structured Capex/D&A inventories supply selected filing metadata, resolved annual
DEI, matching nondimensional entity/duration contexts and instance fingerprints.
Reviewed Operating Income/Pretax tables explicitly supply selected 10-K and
authoritative annual basis. Source row/line and repository-file SHA-256 are
retained. Unapproved financial concepts do not invalidate filing identity, nor
does verified identity approve concepts or economic scope.

Fifteen NWC inventory instances are checked against retained bodies: decompress,
verify declared hash/length, parse exact CIK/nondimensional annual context and DEI
DocumentType 10-K, FiscalPeriod FY and PeriodEnd. Form comes from evidence, not a
default for the form-less inventory. Four reviewed reported-input registries
provide confirming exact identities under their existing binding contracts.
Comparative columns are not selected or registered automatically.

Inventory fingerprints whose bodies/representations are not rechecked here are
labeled inventory-recorded, not verified raw-response digests. Checked NWC
artifacts preserve original representation/digest type and receipt metadata,
including Alphabet's original null fields; its refreshed registry receipt remains
separate. Repository-file hashes are not SEC-response hashes. URLs are retained,
not requested. Absent digests/metadata are not supplied by inference.

Every selected row keeps all candidates/confirmations and incomplete rejected
claims. Differing eligible accession/start signatures are conflicts, not arbitrary
winners. Unbound result identity is null, even when candidate fields are present.
No annual-start/calendar-year, succession or absent-period inference.
**Filing-identity verification is not complete measure-level fact provenance**:
all 189 rows retain `measure_fact_provenance=NOT_ESTABLISHED` under this contract.
Financial sufficiency is NOT_ASSESSED; support/policy/financial states unchanged.

## Remaining evidence and history boundaries

Missing: CSCO/PLTR/KO/NFLX five each; PG three (2024–2026 ends), AMAT two
(2021–2022 ends), MU one (2026 end). Exact known annual ends are in JSON; these
year labels do not infer fiscal dates. Accession/form/start/digest binding is
absent in the bounded sources, not evidence that issuer disclosures are absent.
AVGO 2021-10-31 retains proposed identity/context but inventory status
`annual_period_not_found`; this does not establish an authoritative annual period.
No fresh interpretation or annual-policy change is made.

History exceptions: XOM five, GEV three, SNDK three. Numbered slots have null
dates/accessions, not reconstructed predecessor years. Histories remain
37 five-period/two two-period/one empty = 189; target 200. Universe remains
204 × 17 = 3468 states, **1905/1483/11/27/42**, 43 completions/seven skips,
unchanged support classes. Revenue conflicts and NWC/D&A/timing limits persist.

## Validation and stopping point

Nine manifest tests and eleven existing binding tests pass. Unique identities,
40 mappings/189 rows/11 null exceptions, JSON reproducibility, invalid form/entity/
date/accession, conflicting versus confirming evidence, original receipt gaps
and lack of financial certification are covered. Local links, compileall and
diff check pass; no SEC requests, full suite or corpus rerun.
All affected issuer records link their count/limits. The prior binding ledger is
an immutable historical pass: its record hashes describe the preceding revision,
not these updated records. Live validation checks current records independently.

**Next bounded Phase 1 milestone: one retained-source availability audit for the
27 unresolved identity bindings**, locating existing authoritative selection/
metadata and AVGO annual-resolution diagnostics only. Stop at a source-location/
missing-evidence ledger; no SEC retrieval, issuer research, guessing, policy
change or pilot extension. Absent retained sources require new explicit authority,
not repeated searches. Complete fact/policy joins remain a separate bounded task.
