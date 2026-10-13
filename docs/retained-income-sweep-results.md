# Retained-only direct Revenue/EBIT universe sweep

Phase 1 only. [Reproducible ledger](retained-income-sweep-ledger.json),
[pinned retained catalog](retained-income-sweep-sources.json),
[input contract](dcf-input-contract.md) and
[frozen classifications](universe/phase-1h5-issuer-validation.json).
Replay: `PYTHONPATH=src .venv/bin/python scripts/inspect_retained_income_sweep.py`.
The same shared inspection/direct-policy path is used; no issuer approvals,
new semantics, derived EBIT, financial treatment, SEC requests or corpus run.

## Scope and outcomes

All 42 non-specialized issuers are accounted for: 199 selected periods / 398
Revenue/EBIT slots. The eight specialized issuers, including GE, are excluded.
The forty-company identity manifest binds 189 exact periods; the frozen
classification artifact records another ten selected years for META/COST but
does not supply exact accession/annual-start identities. Those twenty slots are
explicitly insufficient identity bindings, not inferred filings or values.

140 populated slots = 98 unchanged previously packaged slots (four pilots,
NVDA five periods, eight-issuer batch forty periods) + 42 newly populated slots.
192 slots lack retained bodies; 46 have bodies but incomplete original receipts;
20 lack exact identity binding. Zero fully bound cases produced conflicting
values, insufficient financial scope or absence of an eligible direct concept.
Those outcomes remain separate executable dispositions, not inferred outcomes
for uninspected evidence. Retained byte digests/lengths are checked even where
receipt metadata is incomplete; this does not recover missing retrieval metadata.

New packages contain the 140 previously unpackaged exact-manifest periods,
including explicitly null-only periods. Reused packages remain separate and
unchanged; this is not a replacement whole-history adapter. Original four pilot
outputs retain their other field families; twelve other families in newly
inspected packages remain unassessed/null, not searched or financially approved.
Each populated direct value remains partial, with original instance proof,
all confirming occurrences and alternatives. No independent face-statement
re-review or universal timing/financial sufficiency is claimed.

## Per-issuer slot matrix

P = populated; B = missing retained body; R = incomplete receipt;
I = insufficient exact identity. Conflicting/direct-concept-absent outcomes are
zero throughout this bounded pass. Alphabet represents GOOG/GOOGL once.

| Issuer | Periods | P | B | R | I |
|---|---:|---:|---:|---:|---:|
| AAPL | 5 | 10 | 0 | 0 | 0 |
| ABBV | 5 | 0 | 10 | 0 | 0 |
| AMAT | 5 | 10 | 0 | 0 | 0 |
| AMD | 5 | 0 | 10 | 0 | 0 |
| AMZN | 5 | 10 | 0 | 0 | 0 |
| AVGO | 5 | 10 | 0 | 0 | 0 |
| CAT | 5 | 0 | 10 | 0 | 0 |
| COST | 5 | 0 | 0 | 0 | 10 |
| CSCO | 5 | 10 | 0 | 0 | 0 |
| CVX | 5 | 0 | 10 | 0 | 0 |
| GEV | 2 | 0 | 0 | 4 | 0 |
| GOOGL | 5 | 2 | 0 | 8 | 0 |
| HD | 5 | 10 | 0 | 0 | 0 |
| IBM | 5 | 0 | 10 | 0 | 0 |
| INTC | 5 | 0 | 10 | 0 | 0 |
| JNJ | 5 | 0 | 10 | 0 | 0 |
| KLAC | 5 | 0 | 10 | 0 | 0 |
| KO | 5 | 10 | 0 | 0 | 0 |
| LIN | 5 | 0 | 10 | 0 | 0 |
| LLY | 5 | 0 | 10 | 0 | 0 |
| LRCX | 5 | 0 | 0 | 10 | 0 |
| MA | 5 | 0 | 10 | 0 | 0 |
| MCD | 5 | 0 | 10 | 0 | 0 |
| META | 5 | 0 | 0 | 0 | 10 |
| MRK | 5 | 0 | 6 | 4 | 0 |
| MSFT | 5 | 10 | 0 | 0 | 0 |
| MU | 5 | 2 | 8 | 0 | 0 |
| NFLX | 5 | 10 | 0 | 0 | 0 |
| NVDA | 5 | 10 | 0 | 0 | 0 |
| ORCL | 5 | 0 | 10 | 0 | 0 |
| PEP | 5 | 10 | 0 | 0 | 0 |
| PG | 5 | 6 | 4 | 0 | 0 |
| PLTR | 5 | 10 | 0 | 0 | 0 |
| PM | 5 | 0 | 10 | 0 | 0 |
| QCOM | 5 | 10 | 0 | 0 | 0 |
| SNDK | 2 | 0 | 4 | 0 | 0 |
| TSLA | 5 | 0 | 10 | 0 | 0 |
| TXN | 5 | 0 | 10 | 0 | 0 |
| V | 5 | 0 | 0 | 10 | 0 |
| VZ | 5 | 0 | 0 | 10 | 0 |
| WMT | 5 | 0 | 10 | 0 | 0 |
| XOM | 0 | 0 | 0 | 0 | 0 |
| **Total** | **199** | **140** | **192** | **46** | **20** |

## Exceptions, preservation and stopping point

Deduplicated exact-accession artifact backlog: **119** entries (96 missing
bodies, 23 incomplete receipts), each recording its required instance and
affected fields. Some manifest entries have no retained instance filename/hash:
the ledger explicitly leaves those null instead of inventing a URL or digest.
Ten separate META/COST identity exceptions require exact frozen selection
evidence before any acquisition can be specified. Corpus counts are not facts.
These are not 129 confirmed acquisition URLs or an acquisition authorization.

Eleven history target deficits remain: XOM five, GEV three, SNDK three. No
absent periods, calendar dates or predecessor history are fabricated. LLY/JNJ/
MRK/KLAC/IBM retain `operating_income_component_derivation` version `1` references
for later integration; their existing derived EBIT is not directly reported
evidence and is not substituted in this pass. Original revenue conflicts and
financial blockers remain unchanged regardless of this separate source path.

Frozen production stays 1,905/1,483/11/27/42 across 3,468 states, 43 completions
and seven execution skips; support classes and schema 5 unchanged. Pipeline
execution's seven skips are not the eight specialized classification exclusions.
Financial sufficiency remains NOT_ASSESSED. No full suite or corpus rerun.

Validation covers exact scope/slot uniqueness, offline ledger replay, source
file/body digests, independent XML occurrence values, absent evidence/receipts,
no-direct and conflicting candidates, serialization and original artifacts.
Relevant shared regressions cover annual/date/unit/dimension/precision matching,
equivalent occurrences and unchanged pilot/batch/NVDA serialization.
**27 focused tests passed**: eight sweep tests and nineteen shared/batch
regressions. Final sweep replay, compileall and affected local-link/diff checks
pass. No broader test or corpus execution was required.

**Stop after this sweep.** Next bounded step, only when authorized: disposition
the fixed artifact/identity backlog into an exact acquisition or retained-repair
plan, preserving receipt gaps and unresolved selection identities. No automatic
acquisition, exhausted research reopening, or new policy follows.
