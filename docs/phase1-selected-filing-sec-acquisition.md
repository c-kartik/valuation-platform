# Phase 1 fixed selected-filing SEC identity acquisition

Subsequent [preparation closure](phase1-preparation-closure-checklist.md) accepts
the explicit fact-provenance/history limits under the user-approved accounting
standard. The final-prerequisite/next-decision wording below is acquisition-stage
history: no valuation consumer contract or whole-history fact join is required
to close that preparation scope. Future sufficiency remains a separate gate.

Starting HEAD `149fe9a1f64105a49cfc537b57b695ff11313630`.
Explicit user authorization covers only the 26 missing identities in the prior
[availability ledger](phase1-selected-filing-availability.json). Configuration
check sourced the external environment file in the same shell as retrieval;
only nonempty status was checked. No value/file content was displayed or copied,
and no repository/global configuration changed.

## Result and selection proof

**26 verified, zero unresolved**, seven issuers: MU one, CSCO five, PLTR five,
AMAT two, PG three, KO five, NFLX five. Current
[manifest](phase1-selected-filing-identity-manifest.json) is **189 verified,
zero missing/incomplete/conflicting**, 40 issuers, eleven history exceptions.
The prior 163 identities and all exception slots remain byte-equivalent as JSON
records; no annual period or frozen filing was replaced.

60 successful serial requests: seven main SEC submissions, one supplemental
submissions history, 26 exact-accession directory indexes, 26 extracted instances.
At most two request starts/second, 15-second timeout, no automatic/repeated retries.
No Company Facts, financial notes, broad search or extra issuer requests.
[Original-body receipts](evidence/selected-filing-identity-acquisition.json)
retain URL, actual UTC request/retrieval times, HTTP 200, headers, byte length,
SHA-256 of `sec_response_body_bytes`, and lossless gzip/base64 bodies. Base64
storage chunks concatenate before decoding; they are not separate representations.
These are newly acquired response bodies after HTTP transfer decoding, not raw
wire-compression bytes, reserialized JSON, or recovered original-run receipts.
Older evidence and its metadata limitations remain unchanged.

The pinned original corpus records run cutoff
`2026-10-11T12:10:44.715513+00:00`. Main/history submissions are parsed with the
existing code; filings after that date are excluded, and the unchanged selector
requires unique exact 10-K per report date (10-K/A never substitutes). The complete
five selected ends must equal the issuer's frozen selected-end list before any
in-scope accession is accepted. Only then is the corresponding extracted instance
discovered from the actual directory response. This is selector replay from new
official metadata, not an invented missing original accession log. It does not
recover original submission response bytes or certify against hypothetical
retroactive SEC metadata corrections; contradictory evidence would reopen identity.
All accepted filings predate the cutoff date, so no same-day timestamp inference
was required.

The unchanged annual resolver establishes exact CIK, nondimensional duration,
FY/fiscal-year/end DEI facts and unique annual signature. Additional same-annual-
context DEI DocumentType must be 10-K. Conflicting starts, entities, forms or
end dates are not collapsed; authoritative annual starts come from contexts,
never calendar subtraction. Every row retains annual context IDs/DEI occurrences,
selected filing metadata and request bindings. Directory/instance URLs, response
digests and receipt metadata remain separate from repository-file SHA-256.

## Replay, preservation and closure

[Acquisition/replay tool](../scripts/acquire_selected_filing_identities.py) defaults
to offline validation; network access requires explicit `--acquire`. Do not rerun
acquisition: the authorized pass is complete. Replay checks all body digests,
request/receipt identity, official URLs, fixed scope/baseline/cutoff, exact selector
history, directory discovery and parsed annual evidence. The manifest builder
accepts only independently replayed verified claims. Malformed evidence fails,
not a bypass or financial-policy relaxation.

The exception ledger preserves original retained-source search hits/absence and
adds the explicit `VERIFIED_NEW_SEC_EVIDENCE` disposition for 26 rows. AVGO remains
the one retained-evidence repair. Seven company records/index/status are updated
without erasing prior conclusions. Frozen-v1 source policies/schemas/values,
all 17 measure states, support classifications, financial blockers, pilots,
189 selected periods and eleven unfilled target slots remain unchanged.
Universe baseline stays **1905/1483/11/27/42 = 3468**, 43 completions/seven skips.

Focused acquisition, manifest, availability and preparation-binding tests,
offline reproducibility/count/source-digest checks, local links, compileall and
diff check validate the milestone. No full suite or corpus rerun.
Identity verification is **not complete measure-level fact provenance**;
all 189 manifest rows retain NOT_ESTABLISHED. Financial-input sufficiency remains
NOT_ASSESSED. New instances contain facts but this pass does not approve their
economic scope, policy routes or consumer use.

**Closure:** fixed identity acquisition is finished; no further identity retrieval
is needed. Final preparation prerequisites remain explicit disposition of eleven
history-target exceptions, measure-level fact/policy provenance where required,
and a named approved financial-input consumer contract before sufficiency can be
assessed. These are distinct from identity closure and Phase 2 remains postponed.
The smallest next decision is to specify one bounded fact/policy-binding acceptance
scope, without fresh issuer research, policy changes or automatic certification.
