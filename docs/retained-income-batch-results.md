# Retained Revenue/EBIT batch — eight issuers

Phase 1 only; starting HEAD `3289ba191e17bc6b78e3b061f3530557bd4b5ad6`.
[Reproducible ledger](retained-income-batch-ledger.json) /
[offline replay](../scripts/inspect_retained_income_batch.py) /
[one shared application](../src/valuation_platform/analyst/retained_income_batch.py).

| Issuer | Frozen periods | Populated slots | Conflicting slots | Unavailable slots |
| --- | ---: | ---: | ---: | ---: |
| AMZN | 5 | 0 | 0 | 10 |
| AVGO | 5 | 0 | 0 | 10 |
| CSCO | 5 | 10 | 0 | 0 |
| KO | 5 | 10 | 0 | 0 |
| HD | 5 | 10 | 0 | 0 |
| NFLX | 5 | 10 | 0 | 0 |
| PLTR | 5 | 10 | 0 | 0 |
| AMAT | 5 | 4 | 0 | 6 |
| **Total** | **40** | **54** | **0** | **26** |

Every row uses the exact accession and authoritative annual dates in the
[identity manifest](phase1-selected-filing-identity-manifest.json), including
non-calendar/53-week histories; no dates, filings or absent periods are invented.
The ledger accounts for all 80 field-period slots and retains 126 fact
occurrences. All available candidates agree; no reviewed conflict override was
needed. PLTR's 2021/2022 operating losses remain **−411,046,000 / −161,201,000 USD**.
NFLX/PLTR retain decimals −3; other available observations retain −6. Original
raw values, units, sign +1/scale 1, contexts, ordinals and receipt provenance
survive unchanged. Negative raw values are not converted to positive amounts.

## Evidence and finite exceptions

- **CSCO, KO, NFLX, PLTR:** all five original instances and actual HTTP/status/
  UTC/mode receipts are retained in the existing
  [fixed identity-acquisition evidence](evidence/selected-filing-identity-acquisition.json).
  Its gzip/base64 storage chunks are joined only for decoding; original response
  SHA-256/length still verify. Accession is explicitly bound from the frozen
  identity and exact artifact URL, not fabricated retrieval metadata.
- **HD:** all five full instances/receipts are in
  [retained HD bodies](evidence/hd-capex-response-bodies.json). Earlier refresh
  history is preserved, not reclassified as recovered original receipts.
- **AMAT:** only 2021-10-31 / 2022-10-30 instances are retained with complete
  receipts in the acquisition evidence. The 2023-10-29, 2024-10-27 and
  2025-10-26 selections have retained inventory fingerprints/extracts but no
  full bodies/receipts in the exhausted catalog: six unavailable slots.
- **AMZN:** the [existing statement/note fixture](../tests/fixtures/capex_amzn_response_bodies.json)
  retains cash-flow/note reports, not the five required full selected instances.
  Ten unavailable slots. Those reports are neither discarded nor substituted
  for exact annual Revenue/EBIT instance bindings.
- **AVGO:** exact identities/fingerprints/extracts exist, but full original
  instance bodies/receipts are not retained in the bounded source catalog:
  ten unavailable slots. Identity verification is not complete fact provenance.

**Unavailable here means retained evidence is insufficient, not that the issuer
failed to disclose Revenue/EBIT.** No missing-to-zero, inference from corpus
counts, substitution from comparatives or additional research/retrieval follows.
Sources are byte-pinned; every populated slot replays the shared annual-DEI/
CIK/context/unit/precision inspection and the unchanged approved direct concept
semantics. No extensions, component equations or new financial treatments.

Only direct instance observations are reviewed. No independent consolidated
face-statement/primary-filing review is claimed; quality is limited and
completeness partial. Policy ordering may choose an agreeing already-approved
representation, but cannot override unequal candidates. Future conflicts remain
null with all alternatives. Body/receipt gaps and malformed bindings fail
conservatively rather than producing implicit approval.

## Delivery, preservation and stopping point

The common adapter produces eight existing `HistoryBundle` objects with forty
annuals, **54 reported values and 506 nulls**: 26 Revenue/EBIT evidence gaps plus
480 explicitly unassessed other-family slots. Even all-null annuals preserve
their frozen selected identity and named gaps, not fabricated missing history.
The twelve other families per annual were not searched or financially approved.
Versions/schema, original NVDA/pilot serialized outputs and frozen policies/
registries/corpus results remain unchanged. Support classes and financial
blockers remain; financial sufficiency NOT_ASSESSED. This is not a complete
reported-CFO path, whole-issuer readiness or valuation preparation certification.

Focused parameterized tests independently verify every populated observation
against original retained XML, all 40 identities/80 slots, source gaps, duplicate
references, conflicts, precision/signs, replay and serialization/preservation.
**53 focused tests passed**: eight batch tests and 45 relevant shared/NVDA/model
regressions. Exact replay reconciles all 40 periods/80 slots. Independent XML
checks bind all 126 occurrences; eight histories round-trip deterministically,
and original pilot/NVDA serialized hashes remain unchanged. Compileall,
514 affected local links, source digests and `git diff --check` pass.
No full-suite/corpus or SEC requests; production remains 1905/1483/11/27/42
across 3468 states. The face-statement flag denotes no independent face proof
packaged/reviewed in this pass, not a claim that such a report is unavailable
elsewhere in the repository or filing.

**Main expansion constraint:** availability of complete retained selected-instance
bytes with exact identity and actual receipt metadata, followed by direct-scope/
conflict checks—not more issuer-specific code. Fingerprints, extracts and typed
pipeline success cannot fill that gap. Keep any subsequent batch finite and
exception-accounted; do not initiate acquisition or exhausted research here.
Stop after these eight issuers.
