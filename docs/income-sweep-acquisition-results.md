# Fixed 119-accession acquisition and unchanged direct replay

Subsequent [existing-evidence integration](approved-income-integration-results.md)
adds fifteen separately derived EBIT inputs and documents nine prior seed identity
candidates. This acquisition/direct ledger and its 337 direct/eleven conflicting
bindings remain unchanged; acquisition receipts and frozen outputs are preserved.

Phase 1 only. Baseline `5d4f3808584a2712a054978420ca80bcbdb19c3f`:
119 deduplicated exact-accession exceptions, 96 missing instance bodies and
23 incomplete receipts, verified against the unchanged
[identity manifest](phase1-selected-filing-identity-manifest.json) before requests.
The ten META/COST identity gaps were excluded; no filing selection occurred.

[New original-body receipts](evidence/income-sweep-backlog-acquisition.json),
[updated sweep ledger](retained-income-sweep-ledger.json),
[pinned source-file digests](retained-income-sweep-sources.json).
Offline replay: `PYTHONPATH=src .venv/bin/python scripts/acquire_income_sweep_backlog.py`
and `PYTHONPATH=src .venv/bin/python scripts/inspect_retained_income_sweep.py`.

## Actual acquisition

148 requests: 119 exact instances and 29 filing-directory indexes to establish
previously unrecorded instance filenames. All 148 responses HTTP 200; all 119
targets verify exact CIK/accession/form and authoritative annual dates through
the existing retained instance/DEI checks. Zero request/identity failures,
zero retries, zero unattempted targets. Serial requests use the established
two-starts/second limit. No notes/statements, new years, submissions, broad
discovery or semantic research were acquired. External SEC configuration was
sourced in the acquisition shell; its contents and value were not displayed
or copied into the repository.

Resumable generated checkpoint is outside the repository. Completed successes
and failures are not reattempted; independent subsequent targets continue.
Every retained response preserves original bytes, URL, actual UTC start/end
timestamps and HTTP status, explicit byte representation, SHA-256 and length.
Directory receipts bind discovered filenames to the exact selected directory;
ambiguous directories cannot authorize a plausible instance selection.

All **23 retained original bodies are byte-identical** to their refreshed bodies.
For the other 96, prior original bytes were unavailable: 67 match historical
claimed fingerprints and 29 have no historical fingerprint. Thus 90 total
fingerprints agree, but this is not a 90-body byte-equality claim. No observed
byte or fingerprint differences. Prior bodies, receipt gaps and historical
claims remain untouched and linked in each verification row. New receipts are
explicit refreshes, never recovered original retrieval metadata.

## Actual 398-slot reconciliation

| Outcome | Before | After |
|---|---:|---:|
| Populated direct | 140 | 337 |
| Missing retained body | 192 | 0 |
| Incomplete receipt | 46 | 0 |
| Conflicting eligible values | 0 | 11 |
| No eligible direct concept | 0 | 30 |
| Insufficient exact identity | 20 | 20 |
| Insufficient scope | 0 | 0 |
| **Total** | **398** | **398** |

All original 140 populated field/source/occurrence bindings remain identical.
The 238 formerly evidence-blocked slots become 197 new direct populated slots,
11 conflicts and 30 direct-concept absences. Acquisition does not establish
semantic equivalence, completeness or financial sufficiency. Candidate
occurrences, competing values and limitations stay explicit; no precedence was
changed. WMT five Revenue periods, MA 2021 Revenue and CVX five Revenue periods
remain conflicting. All five EBIT periods for LLY/JNJ/MRK/KLAC/IBM retain their
existing `operating_income_component_derivation` version `1` references without
direct integration; CVX's five EBIT periods also have no eligible direct concept.
No derivations or fallbacks are introduced.

The exact-accession acquisition backlog is **zero**. Ten META/COST selected-year
identity gaps (twenty slots) remain outside this authorization. Eleven history
target deficits remain XOM five, GEV three and SNDK three. No absent periods are
invented. All 42 non-specialized issuers / 199 selected periods remain accounted;
all eight specialized issuers including GE excluded, without support changes.

## Preservation and validation

Original pilot/NVDA/batch serialized outputs, frozen schema 5, policies and
registries remain unchanged. New packages keep twelve other field families
unassessed/null. Revenue conflicts in the frozen baseline are not cleared by
this separate preparation path. Production remains 1,905/1,483/11/27/42 across
3,468 states, 43 completions/seven execution skips; no corpus rerun.
Financial-input sufficiency remains NOT_ASSESSED.

Focused acquisition/refresh/receipt, resume/failure, exact identity, direct
sweep, candidate conflict/absence, independent original XML, serialization and
preservation tests; compileall, affected local links, reproducible offline
replay and `git diff --check` are the validation gates. No full-suite execution.
**34 focused tests passed** (seven acquisition, eight sweep, eight batch and
eleven shared inspection regressions). Both final offline replays pass,
1,051 affected local links resolve, request starts meet the rate limit, and
compileall/diff checks pass. All 140 prior populated bindings, original pilot
serialization and frozen artifacts pass preservation checks.

**Stop after this fixed acquisition/replay.** Remaining semantic conflicts,
direct-concept absences and excluded selection-identity gaps are explicit, not
an automatic research or acquisition queue. Future integration of existing
derived EBIT would require a separate bounded authorization and preservation
checks; this milestone grants none.
