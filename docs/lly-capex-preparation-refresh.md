# LLY Capex: additive preparation evidence generations

## Decision and boundary

The user explicitly authorized the preparation-layer schema treatment following
the [completed review](lly-capex-refresh-review-results.md). Accept only its five
LLY entries and fifteen exact refreshed reports, under unchanged original
`capex_scope_equivalence` financial policy v1. No new equation, fallback,
financial perimeter, frozen registry mutation or original-digest verification.

The [review record](evidence/lly-capex-refresh-review-v1.json) remains immutable,
including its historical operational-blocked status. The new preparation path
resolves that schema limitation; it does not rewrite the old review, receipts or
legacy audit. Its seven financial-scope assertions are present for every entry.
Unknown original byte equivalence, incentive/noncash allocations and capitalized-
interest amounts stay explicit; no unsupported assertion or zero is supplied.

## Minimal typed contract

`analyst/refreshed_capex.py` adds immutable `RefreshedArtifact`, `RefreshAudit`
and `RefreshedHistory` models. A refresh audit retains:

- Exact CIK/accession/form/annual identity and original financial policy ID/v1,
  full immutable entry JSON and its digest.
- Exact review path/version/digest and entry snapshot, supported requirements,
  report role/caption/location and the unknowns from the independent review.
- Every historical report fingerprint and typed digest, explicitly
  `ORIGINAL_BODY_UNAVAILABLE_BYTE_EQUIVALENCE_UNESTABLISHED`.
- Every refreshed original-body artifact and actual receipt metadata, plus
  retained receipt path/locator/document digest. New receipts never masquerade
  as recovered old metadata.
- Exact refresh ID/version `lly-capex-preparation-refresh-v1`, selected input ID,
  `original_byte_equivalence=UNPROVED` and acceptance basis
  `INDEPENDENTLY_REVIEWED_REFRESH_NOT_ORIGINAL_DIGEST_VERIFICATION`.

The completed review digest pins the allowed five entries/fifteen pairs, not an
arbitrary hash substitution mechanism. Missing assertions, foreign identities,
changed bodies/receipts, unregistered generations or conflicting evidence fail
closed. The existing review validator is shared through an analyst module;
the historical CLI remains an unchanged-result wrapper. Seven non-report
requirements per entry and the original instance remain byte-bound. Review
replay independently checks statements, annual DEI, operands and scope.

The preparation path reparses the verified original instance and compares all
inspection facts/contexts to it, enforces exact original approved concept and
amount/precision, and keeps the existing direct path and conflicts separate.
There is **no replacement attestation passed to the legacy verifier or resolver**.
An eligible direct result cannot be silently relabeled as a refresh. The unchanged
legacy verifier and output validator still reject the refreshed digests.

Accepted values retain reported origin, sign -1, scale 1, all confirming source
occurrences, precision, raw support alternatives and restricted/partial scope.
The selected role explicitly names refreshed evidence. No complete reinvestment,
timing, integrated lease/tax or valuation sufficiency is certified.

## Serialization and compatibility

Preparation **`historical-input-preparation-v2`** wraps the unchanged immutable
historical bundle with typed refresh audits. Only LLY's new annual/history
container identities use preparation version 2; other input values are copied
unchanged. V2 uses a payload-local exact-byte table keyed by SHA-256 to avoid
repeating the same retained instance hundreds of times. URLs, accessions, receipt
metadata, contexts and occurrences remain individually represented. This is
transport deduplication, not an evidence cache or economic-equivalence rule.
Body hashes, missing references, unused bodies, closed fields and duplicate keys
are validated; decoding reconstructs identical original bytes.

The new API also reads/writes existing preparation v1 without migration and
returns exactly its prior serialized bytes. Existing schema 5 and reported
pilot/scenario/sidecar serialization are unchanged. V1 now rejects the reserved
refresh marker/role/input ID rather than silently losing the required typed audit.
V2 construction/deserialization independently replays each accepted Capex value
and requires one exact audit per selected input, with no orphaned or nested
acceptance. Legacy proof flags are never attached to the five refreshed values.

## Verified preparation results

[199-period ledger](refreshed-capex-ledger.json); offline replay:
`PYTHONPATH=src .venv/bin/python scripts/inspect_refreshed_capex.py`.

| Annual period | Exact selected accession | Accepted cash outflow USD | Precision |
|---|---|---:|---|
| 2021-01-01–2021-12-31 | `0000059478-22-000068` | -1,309,800,000 | -5 |
| 2022-01-01–2022-12-31 | `0000059478-23-000082` | -1,854,300,000 | -5 |
| 2023-01-01–2023-12-31 | `0000059478-24-000065` | -3,447,600,000 | -5 |
| 2024-01-01–2024-12-31 | `0000059478-25-000067` | -5,057,800,000 | -5 |
| 2025-01-01–2025-12-31 | `0000059478-26-000013` | -7,841,000,000 | -6 |

**Five accepted / zero blocked** in the preparation refresh path. All five
original legacy report attestations remain unsatisfied, preserved separately in
the ledger and audit; acceptance is not successful old-hash verification.

**145 direct + fifteen legacy curated + five independently reviewed refresh +
34 unapproved scope = 199 periods; 165 populated, zero conflicts/evidence gaps.**
Prior 160 populated results and 34 unapproved rows remain exact. All other
prepared fields, original four pilot outputs, 42 issuer mappings and eleven
history deficits remain unchanged. No history is fabricated for XOM or short
GEV/SNDK selections. Frozen corpus remains Capex 167/37/0 and aggregate
1,905/1,483/11/27/42 across 3,468 states; no corpus rerun.

Focused validation covers exact acceptance, original/refresh disclosure and
immutability, missing requirements, identity/digest/receipt tampering, financial
conflicts, orphaned audits, deterministic v2 replay, v1 byte compatibility and
legacy rejection. **58 unique focused tests pass**: eleven new integration/transport/
original-representation checks, 24 preparation model tests, six prior review
tests and seventeen legacy v1 policy tests. Compileall, all 363 affected local
links, independent ledger/serialization replay and diff checks pass.
Zero SEC requests, no full-suite rerun or Phase 2 work. Stop after integration.
