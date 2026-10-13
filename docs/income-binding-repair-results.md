# Fixed official income evidence-binding repair

Phase 1 only. Baseline `eb99ab310fe6d3860d4cd3036e8a922189350d38`;
[new original receipts](evidence/income-binding-repair.json),
[pinned receipt configuration](income-binding-repair-config.json) and
[additive 398-slot ledger](repaired-income-ledger.json).
Offline replay:
`PYTHONPATH=src .venv/bin/python scripts/repair_income_evidence_bindings.py`
and `PYTHONPATH=src .venv/bin/python scripts/inspect_repaired_income.py`.

## Fixed acquisition and verified bindings

Twenty targets: ten exact approved JNJ/KLAC accessions, nine documented META/
COST candidates, and one COST FY2026 frozen-end check. All twenty verified.
**25 requests, all HTTP 200; zero failures or retries**: four main submissions,
one necessary supplemental submissions record, ten selected-accession directory
indexes and ten seed instances. No JNJ/KLAC instance was downloaded: existing
verified original bodies are reused. No statements, notes, additional years,
ticker re-resolution or semantic research were requested.

The existing five-annual selector is replayed at the immutable corpus cutoff
recorded in the receipt document (2026-10-11). Every issuer reproduces all five
frozen selected ends; every known candidate accession agrees exactly. Original
dates, source URLs, actual UTC request/retrieval times, HTTP status, byte lengths,
explicit response-byte representation and SHA-256 are retained. New receipts
do not recover original missing metadata; prior candidates/gaps remain intact.
External SEC configuration was sourced only in the retrieval shell, not printed
or copied. Requests remain serial at at most two starts/second, no automatic retries.

META five and COST five annual instances replay the existing DEI resolver,
including exact entity/form/dimensionless annual context and week-based dates.
The previously unknown COST period is independently established as:

| Field | Official evidence |
|---|---|
| Accession | `0000909832-26-000093` |
| Form / filed / primary | 10-K / 2026-10-07 / `cost-20260830.htm` |
| Annual start/end | 2025-09-01 / 2026-08-30 |
| Selection | Existing selector at frozen cutoff; no plausible-accession choice |

It is the existing frozen annual end, not a new history period. The 189-period
forty-issuer manifest and all eleven target deficits stay unchanged; ten seed
identities are independently bound in this supplemental receipt ledger.

## Unchanged financial execution and actual coverage

The shared direct path supplies twenty newly verified META/COST Revenue/EBIT
slots. It retains all confirming occurrences, alternatives, precision and scope
limits. No fallback or new concept semantics is added.

JNJ/KLAC's ten official submission records supply the missing actual filing
dates and submission-bound primary documents. Exact metadata and authoritative
annual periods permit the unchanged immutable
`operating_income_component_derivation` version `1` to resolve all ten, using
retained operands and its existing arithmetic, precision/absence and validation
gates. These inputs are derived, not reported-direct. No equation or entry changes.

| Outcome | Previous | Repaired |
|---|---:|---:|
| Reported direct | 337 | 357 |
| Approved derived EBIT | 15 | 25 |
| Conflicting Revenue | 11 | 11 |
| No eligible direct / unintegrated EBIT | 15 | 5 |
| Seed missing body/receipt | 18 | 0 |
| Unknown seed identity | 2 | 0 |
| **Total** | **398** | **398** |

Exact remaining exceptions: five unregistered CVX EBIT periods (2021–2025),
plus eleven original Revenue conflicts: WMT five, CVX five, MA 2021. No economic
perimeter research is reopened or conflict replaced with a derived result.
All 337 previous direct and fifteen previous derived field/source bindings are
identical; previous ledgers remain immutable rather than overwritten.

## Provenance, serialization and limitations

The approved-input adapter has an explicit opt-in metadata-repair path; default
behavior/old bindings stay unchanged. New derived and seed inputs retain an
`official_selected_filing_metadata` provenance flag with the exact official
submission-array locator, actual receipt metadata/digest, filing identity and
frozen cutoff. Metadata is not inferred from file modification or retrieval time.
Original instance receipts remain the monetary fact sources. Approved equation,
all selected/nonselected operands, original versus policy-local ordinals, signed
contributions, precision and entry-specific bridge proof survive serialization.
The approved-history gate replays the existing resolver and exact metadata binding
after generic structural deserialization; no schema migration is introduced.

Other twelve families in newly packaged seed annuals remain unassessed/null.
COMPLETE on an approved EBIT equation is not integrated financial sufficiency,
timing or FCFF approval. Source receipt completeness does not certify organic
comparability, reinvestment, working capital, tax, lease or share readiness.
No support reclassification, frozen policy/value change or automatic blocker
removal. Frozen corpus remains 1905/1483/11/27/42 across 3468 states, with
43 executions/seven skips; eight specialized issuers including GE remain excluded.

Focused checks cover exact target/metadata/cutoff replay, original-body digests,
official array bindings, annual DEI, actual monetary occurrences, approved operand
arithmetic/precision/proof, tampering, serialization and all prior-result/pilot
preservation. Compileall, affected local links, offline reproducibility and diff
checks are required. No full suite or corpus run.
**48 focused tests passed**: seven repair, eight prior integration, twenty-two
active-policy and eleven shared/pilot-preservation tests. Both final offline
replays, compileall, 357 affected local links, count/rate/digest checks and
`git diff --check` pass. Original 337 direct/fifteen derived bindings, all eleven
conflicts, five CVX gaps, prior receipts and frozen artifacts pass preservation.

**Stop after this fixed repair/replay.** No additional acquisition, financial
rule, derivation, coverage research or valuation implementation is authorized.
