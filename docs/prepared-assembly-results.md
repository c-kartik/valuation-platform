# Isolated historical-input assembly and review

Phase 1 only; baseline `9b477defc6d2dba6e382ad8f27d26e8e6a575730`.
[Machine-checkable quality/review summary](prepared-assembly-summary.json).
Offline replay: `PYTHONPATH=src .venv/bin/python scripts/assemble_prepared_inputs.py`.
42 non-specialized issuer histories, 199 selected annuals and **2,786 period ×
field-family slots** (14 families). XOM is empty; GEV/SNDK have two annuals each.
Three explicit history records preserve eleven five-period-target deficits.
GOOG/GOOGL aliases access one Alphabet history, not duplicate annuals or class
equivalence. The eight specialized issuers, including GE, remain excluded.

## Assembly contract

`analyst/prepared_assembly.py` materializes existing field adapters and verifies
their retained-ledger identities; it introduces no selector, extraction treatment
or financial equation. Existing parents supply income/CFO/Capex, movement,
deferred-tax/SBC and reported-tax context. Existing separate D&A, instant-component
and claims/share overlays supply their already-prepared values and observations.
Actual `InputValue` objects, alternatives, formulas/operands, flags, precision,
scopes and provenance are copied unchanged into new `AnnualBundle`/`HistoryBundle`
containers. No residual is computed; tax/residual gaps remain explicit.

Prepared policy values, support observations, components, derivation operands
and null requirements have separate binding categories. Original valued pilot
components and reviewed limits remain alongside cohort observations; shared
fact reuse produces overlap warnings, not permission to count twice. Old generic
placeholders replaced by an overlay's explicit requirement remain in the attached
original parent. Original parents/pilots are immutable references, not rewritten
or retroactively certified. Original financial/NWC/timing blockers persist.

All partial components remain partial; cash, debt, pension, NOL and share totals
are not computed or approved. Share dates/classes remain independent. Invalid
fact diagnostics have no accepted value; their exact ledger locations remain
click-through evidence, not default zeros. Existing 25 EBIT and five MSFT D&A
derivations retain their equations/operands. Five LLY Capex values retain typed
original/refreshed provenance, unavailable historical bodies and unproved byte
equivalence, not substituted legacy hashes.

## Coverage — periods, not components or financial sufficiency

| Family | Periods with root values | Policy-prepared value periods |
| --- | ---: | ---: |
| Revenue | 188 | 188 |
| EBIT | 194 | 194 |
| CFO | 195 | 195 |
| Cash Capex | 165 | 165 |
| D&A | 199 including support | 115 |
| Cash-flow working-capital movements | 199 | 0 |
| Deferred taxes | 193 including provision/mixed support | 0 |
| SBC | 184 including expense/mixed support | 0 |
| Reported tax context | 4 | 0 |
| Unclassified CFO residual | 0 | 0 |
| Cash/investments | 199 | 0 |
| Debt/leases | 199 | 0 |
| Other bridge claims/assets | 199 | 0 |
| Dated shares | 199 | 0 |

Root-entry counts exclude nested alternatives, which remain in the review
payloads. The JSON summary separately reports valued roots, support/component
roots, operands, null requirements, origins, completeness and conflicting periods
for every field and issuer. Observation availability does not establish pure CFO
adjustments, complete balances, class totals or five-year/consumer readiness.
Financial sufficiency remains **NOT_ASSESSED**; no coverage percentage or target
acceptance is calculated. 90% recent/80% older remain proposed targets only.

## Deterministic review queue

**17,605 review cards**. Codes overlap and therefore do not sum to card count:
119 conflict, eight invalid-evidence, 1,860 missing-required-value,
11,787 overlap-warning, 17,271 partial/unreviewed-scope, 17,308 unresolved-
requirements and three history-exception cards. Invalid locations preserve the
eight existing claims/pension errors; no evidence acquisition is proposed.

Targets bind CIK/accession/field and fixed component input/channel identities;
field targets are separate. IDs do not depend on numerical values or review
codes. Order uses an explicit field-importance profile, then recent annual date,
field and target ID—not confidence, materiality or financial readiness. A caller
can supply a complete positive ranking without changing target IDs. Source/
alternative payloads expose exact original-body digests/URLs, contexts/ordinals,
raw units/signs/precision, locators, scopes and existing proof flags. LLY cards
also expose original fingerprints/statuses, actual refreshed receipts and review
references. Alias lookup does not map securities to a share class.

The queue is read-only: no automatic acceptance, acknowledgment state, estimate,
blocker removal or persistent override. A missing requirement stays missing.
Existing movement parent/child relationships and exact same-source reuse remain
warnings; no non-overlap or economic equivalence is inferred.

## Serialization, preservation and validation

Separate `assembled-historical-input-review-v1` serialization includes the new
bundle, original parent, all three typed overlay families, bindings, diagnostics
and source-ledger SHA seals using existing exact-byte payload-local transport.
Closed decoding checks integrity, exact ledger revision, container equality and
independent existing overlay replay. Original income/CFO/Capex values and retained
occurrences are checked against their existing ledger/body bindings. Changed
values/roles/dates/diagnostics or missing refresh provenance fail validation.
No migration of frozen schema 5, preparation v1/v2 or pilot serializers.

Preservation checks pin original pilot payload hashes, original financial code,
registries, corpus and retained evidence/ledgers. Baseline remains
1,905/1,483/11/27/42 across 3,468 states; support classes 2/40/8 remain unchanged.
No SEC request, research, full-suite/corpus rerun or valuation calculation.
**43 unique focused tests pass**: eight assembly tests, 24 existing immutable
input-model tests and eleven shared-inspection regressions. The round-trip
validator was corrected to read both existing ledger forms (pilot direct
`value_usd` and ordinary selected-candidate records); the affected test passes
on rerun with exact amounts and sources unchanged. No conflict selection or
evidence rule was weakened. Compileall, 2,367 affected local links, exact
40-register-plus-two-seed mapping, period/field counts and diff checks pass.

## Next bounded milestone: persistent analyst overrides

Only when authorized: a small opt-in override store bound to stable field/
component targets **and exact source-ledger/bundle revision**, with author,
actual UTC timestamp, rationale, explicit value/origin/precision/treatment,
superseded alternatives and audit history. Reject stale, conflicting or
cross-period overrides; acknowledgment alone cannot resolve a required value.
Preserve original packages and reported facts, never fabricate SEC provenance or
silently approve a complete total. Design explicit allowed Phase 1 operations
and user acceptance before implementation; no forecasts, rates, economic
adjustments, consumer certification or valuation calculations. Stop after one
finite persistence/validation milestone, not another research loop.
