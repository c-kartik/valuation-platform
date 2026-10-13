# Fixed Capex original-artifact binding repair

Phase 1 evidence repair only, against `231dfa15d2844b36a8e5b087baa2655de30ca0d3`.
The [original backlog](retained-capex-ledger.json) contains exactly 85 requirements
for fifteen immutable approvals: AMZN five, LLY five, CVX five. No financial
approval, equation, registry fingerprint or frozen output changed.

## Search, acquisition and byte verification

[Acquisition/exception receipts](evidence/capex-binding-repair.json) retain the
exact target identities, required and actual digests, original response bytes,
URLs, actual UTC receipt metadata and prior fingerprint history. The bounded
search of 71 committed JSON files found **zero reusable verified bodies**; thirty
references declared matching raw fingerprints without recoverable original bodies.
Those are broken/missing body bindings, not evidence of matching bytes.

The fixed pass made **85 requests, 85 HTTP 200 responses, zero transport failures
and zero retries**. No additional index, statement research or broader crawl.
External SEC configuration was sourced only in the retrieval shell and was not
displayed or retained. New receipts are refreshes, not recovered original metadata.
Raw-response SHA-256 is verified against original bytes, never parsed/text equality.

| Issuer | Required | Exact raw matches | Byte mismatches |
|---|---:|---:|---:|
| AMZN | 30 | 30 | 0 |
| LLY | 40 | 25 | 15 |
| CVX | 15 | 15 | 0 |
| **Total** | **85** | **70** | **15** |

LLY's mismatches are R9/R11/R19.htm for 2021, and R9/R10/R18.htm for each of
2022–2025. Exact accession URLs and both digests are in the receipt ledger.
These fifteen responses are retained but **not accepted** as registered evidence.
Unavailable original bytes prevent deciding whether the differences are merely
representational or substantive. No fingerprint relabeling, text-equivalence
substitution, refresh approval or financial denial follows from this comparison.

## Unchanged-policy replay

[Current 199-period ledger](repaired-capex-ledger.json) is additive; the original
[150-populated result](retained-capex-results.md) and ledger remain historical
artifacts. Offline replay uses
`PYTHONPATH=src .venv/bin/python scripts/inspect_repaired_capex.py`.

| Outcome | Periods |
|---|---:|
| Direct | 145 |
| Curated | 15 (AMZN v1 five, CVX v2 five, Visa v3 five) |
| Approved-entry evidence gap | 5 (LLY, three reports each) |
| Unapproved scope | 34 |
| Conflict / other unavailable | 0 / 0 |
| **Total** | **199** |

**160 populated**: ten additional resolutions, not fifteen assumed repairs.
Existing annual-DEI, exact-entry, operand, scope, occurrence and provenance gates
are executed unchanged. Payments retain original magnitudes and negative outflow
signs. Full policy/version/audit and new receipt references survive serialization.
All prior 150 populated bindings, 34 unapproved rows, other prepared fields and
four original pilot annuals remain exact. This is not complete reinvestment,
whole-issuer support or financial-input sufficiency.

Forty register issuers plus two supported seeds, 199 selected periods and eleven
history deficits remain. XOM is empty; GEV/SNDK have two periods each. Frozen
schema 5, registries, policies and corpus stay unchanged: Capex 167/37/0;
aggregate 1,905/1,483/11/27/42 across 3,468 states. No corpus or full-suite rerun.

## Validation and stopping condition

Focused tests cover all 85 exact requirements, rate/receipt/body binding,
raw-versus-transformed representation, mismatch rejection, 199-period offline
replay, immutable registry preservation, signs, policy provenance, deterministic
serialization and independent revalidation. **61 focused tests pass**: six new
repair tests, eight existing preparation tests and 47 v1/v2/v3 policy regressions.
Compileall, all 436 affected local links and staged/unstaged diff checks pass.

Stop after this fixed pass. The remaining five LLY bindings require disposition
of the fifteen historical report fingerprints: recover the exact original bytes
and representation, or obtain explicit authorization for a separate provenance
review if unrecoverable. Repeating acquisition, numerical/text agreement or
automatic registry replacement cannot close them. All 34 financial-scope cases
and deferred D&A/timing/consumer requirements remain separate, unchanged limits.
