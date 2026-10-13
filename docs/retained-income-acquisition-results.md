# Fixed 13-instance acquisition and unchanged batch replay

Phase 1 only; baseline `3bf319eda79b9c5e3e855f134ebb82d496cb004a`.
[New receipts/original bodies](evidence/retained-income-instance-acquisition.json) /
[offline acquisition verifier](../scripts/acquire_retained_income_instances.py) /
[updated 80-slot ledger](retained-income-batch-ledger.json).

## Authorized scope and requests

The committed baseline ledger and verified identity manifest reconcile exactly
13 missing full instances / 26 unavailable slots: AMZN five, AVGO five, AMAT
three. Their exact URLs/accessions/authoritative annual dates were fixed before
requests. No new filing selection, extra periods, statement/note research or
broad discovery. External configuration was sourced in the same retrieval shell
and checked nonempty without displaying or retaining its contents/value.

**13 requests = 13 successful exact-instance responses.** Zero directory-index
requests, automatic retries or additional artifacts. Existing RecordingClient
enforced serial starts at most twice per second, timeout 15 seconds and a
stop-on-failure fixed pass. Actual HTTP 200, UTC start/retrieval timestamps,
URLs, original response bodies, byte lengths and typed
`sha256_sec_response_body_bytes` digests are retained. Gzip/base64 chunks are
storage only; decoded original bytes and receipt bindings replay offline.

All 13 independently reproduce exact CIK, selected accession/10-K form and
authoritative annual duration through existing DEI/entity/context parsing,
including AVGO's reviewed non-calendar/53-week identity. All new digests match
historical fingerprints. **That is not proof of byte equality with unavailable
old bodies or recovery of original retrieval metadata.** Every receipt preserves
the old claimed fingerprint/unverifiable status and explicitly identifies this
new acquisition. Old inventories, manifest and baseline Git ledger are unchanged
or retained at their pinned revision; nothing is silently relabeled/overwritten.

## Actual unchanged-rule outcome

| Issuer / acquired annual ends | Verified instances | Newly populated slots | Remaining conflict/unavailable |
| --- | ---: | ---: | ---: |
| AMZN / 2021–2025 December 31 | 5 | 10 | 0 / 0 |
| AVGO / 2021-10-31, 2022-10-30, 2023-10-29, 2024-11-03, 2025-11-02 | 5 | 10 | 0 / 0 |
| AMAT / 2023-10-29, 2024-10-27, 2025-10-26 | 3 | 6 | 0 / 0 |

Shared Revenue/EBIT inspection, concept rules, selection and packaging are
unchanged. Only the new byte-pinned receipt catalog is added. Every new value
has existing approved direct semantics, exact annual nondimensional USD context,
original precision/sign, occurrence and receipt provenance. No fallback,
derivation, issuer registry, conflict override or scope expansion.

Original batch: **54 populated / 0 conflicting / 26 unavailable**.
After acquisition: **80 populated / 0 conflicting / 0 unavailable**, all 40
original periods accounted for; each of eight issuers now has ten direct slots.
197 occurrences (previous 126 plus 71 newly bound) are retained. All 54 original
populated field ledgers/bindings remain exactly unchanged. No assumption that
acquisition must resolve slots was used; all candidates were re-inspected.

Forty annual bundles retain **480 explicitly unassessed nulls** for twelve other
contract families per annual. These fields were not searched or approved.
Direct-only quality/completeness remain limited/partial: independent retained
face-statement review, business/perimeter comparability, timing readiness and
whole-issuer financial sufficiency remain unproved. No support reclassification,
original metric-blocker removal, economic calculation or Phase 2 approval.

## Verification and stopping point

Focused tests replay all 13 receipt/body/identity/request bindings, exact scope,
digests/refresh history and rate-limit timestamps; reject malformed metadata,
wrong identities/digests and out-of-scope requests. The batch independently
checks all populated values against original XML, all 80 slots, original 54
bindings, candidate conflicts, serialization and pilot/NVDA preservation.
**56 focused tests passed**: eleven acquisition/batch checks plus 45 shared/
NVDA/model regressions; the three acquisition tests also pass after final
request/refresh-history guards. Offline receipt replay verifies 13/13; current
ledger replay reconciles all 80 slots. All original 54 bindings, pilot/NVDA
serialized hashes and financial-policy bytes remain unchanged. Compileall,
328 affected local links, source digests and `git diff --check` pass.
No full-suite or corpus rerun.
Frozen policies/schema 5 and production 1905/1483/11/27/42 across 3468 remain
unchanged. Stop after this fixed acquisition/replay; no further SEC requests or
research chain. Remaining limitations are financial/evidence-depth gates, not
unavailable Revenue/EBIT instance bindings in this batch.
