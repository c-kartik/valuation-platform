# NVDA retained Revenue/EBIT preparation — bounded application

Starting HEAD `20c32606a5c333e9a62339657970c1e29de4fc80`; Phase 1 only.
[Reproducible ten-slot ledger](nvda-retained-income-ledger.json),
[offline replay](../scripts/inspect_nvda_income.py),
[application](../src/valuation_platform/analyst/nvda_income_inputs.py),
[shared direct adapter](../src/valuation_platform/analyst/retained_income_preparation.py).
No new issuer-specific approval registry, concept fallback or financial treatment.

## Exact selected results

USD millions below; inputs preserve original USD, scale 1/sign +1/decimals −6.
EBIT is the existing approved reported `OperatingIncomeLoss` primitive, not
analytical EBIT, adjusted earnings or a new derivation.

| FY / exact accession | Authoritative annual dates | Revenue | EBIT | Revenue / EBIT occurrences |
| --- | --- | ---: | ---: | --- |
| 2022 / 0001045810-22-000036 | 2021-02-01–2022-01-30 | 26,914 | 10,041 | 4 / 2 |
| 2023 / 0001045810-23-000017 | 2022-01-31–2023-01-29 | 26,974 | 4,224 | 4 / 2 |
| 2024 / 0001045810-24-000029 | 2023-01-30–2024-01-28 | 60,922 | 32,972 | 4 / 2 |
| 2025 / 0001045810-25-000023 | 2024-01-29–2025-01-26 | 130,497 | 81,453 | 4 / 2 |
| 2026 / 0001045810-26-000021 | 2025-01-27–2026-01-25 | 215,938 | 130,387 | 3 / 1 |

Five exact frozen selections / ten field slots: **10 populated**, no missing
instance/receipt or unequal-value exceptions. Eleven candidate groups retain
28 occurrences. FY2022 Revenue has both approved `Revenues` (one occurrence)
and `RevenueFromContractWithCustomerExcludingAssessedTax` (three). Existing
direct-policy ordering selects the latter after exact agreement, with the
former retained as an alternative. Equality is not approval of a new concept;
both concepts were already approved. All later Revenue uses `Revenues`.
Every EBIT observation uses the existing approved operating-income concept.
No silent precedence, summation, rounding adjustment or missing-to-zero.

## Evidence depth and exceptions

The [identity manifest](phase1-selected-filing-identity-manifest.json) rows 0–4
fix CIK 1045810, accessions, 10-K form and annual dates. All five instances in
[retained response bodies](evidence/nvda-capex-response-bodies.json) have original
bytes, verified SHA-256/length, actual HTTP 200, UTC retrieval timestamps and
retrieval mode. Existing refresh history and unverifiable original fingerprints
are preserved; the current receipts do not masquerade as recovered originals.
Both authoritative manifests are byte-pinned in executable loading. Exact
instance URLs/digests/metadata and candidate namespace/context/unit/precision,
raw signs, ordinals and evidence references are retained in the ledger.

The shared API independently replays annual DEI, selected identity, exact annual
contexts, nondimensional scope and USD units. Independent tests read original
instance facts/contexts directly and assert the values above, not a corpus count
or adapter echo. Existing direct US-GAAP financial semantics supply the permitted
reported-input meaning; no issuer extension, expense derivation or label-based
equivalence is introduced.

**Explicit retained limitation:** FilingSummary identifies the consolidated
income statement as **R3.htm in all five filings**, but those report bodies and
original primary 10-Ks are not retained in this bounded evidence set. They are
not reconstructed, fetched or called reviewed. Integration is limited to the
verified approved direct annual observations, with quality limited and
completeness partial. No independently retained face-statement re-review,
organic/perimeter comparability or financial-input sufficiency claim. A missing
face report is not silently erased by successful instance inspection.

Future missing bodies, incomplete timestamp/status/mode, invalid identity/unit/
precision/context or competing eligible values remain explicit exceptions or
conservative data errors. No further research/retrieval is launched here.

## Bundle delivery and preservation

Existing immutable `AnnualBundle`/`HistoryBundle` models package all five periods
through the shared direct adapter, version 1, separate from the original pilots.
There are **10 reported values + 60 unassessed null family slots**, with one
reported Revenue alternative. All twelve other field families per period are
origin unavailable, review unreviewed, quality unassessed, unknown scope/
completeness and explicit “not searched in this pass” requirements. Nulls are
not claims of absent disclosure. Shares have no invented observation date;
bridge placeholders retain the target year-end without fabricating source facts.
No CFO, D&A, tax, investment, cash-movement or NWC approval follows.

Separate existing model serialization retains receipts, occurrence references,
raw values, roles, signs, precision, alternatives and all null requirements.
Full history round-trips deterministically. Generic structural deserialization
is not fresh source replay; use the offline application/ledger replay to validate
fact bindings. There is no new schema, source store, issuer acceptance registry
or valuation consumer. No forecasts, ratios, economic adjustments or FCFF.

Pilot serialized hashes/versions, their mappings, frozen schema 5 and financial
policies/registries/corpus results remain unchanged. NVDA stays
GENERALIZATION_REQUIRED; original blockers persist. Retained corpus baseline
1905/1483/11/27/42 across 3468 is not rerun or changed. Five selected periods with
two fields do not imply the three-period readiness target or 90%/80% field
coverage targets are satisfied. Financial sufficiency remains NOT_ASSESSED.

## Validation and bounded batch readiness

Focused checks cover all five exact identities/ten slots, independent source
values, receipt/body gaps, approved representation alternatives, conflicts,
duplicates, context/date/unit/precision errors, serialization and preservation.
**93 focused tests passed**: ten NVDA tests plus 83 relevant shared-inspector,
direct-income, pilot-adapter, mapping and historical-model regressions. All ten
slots replay exactly; five-period serialization is deterministic. Existing pilot
serialized history hashes and original source/policy bytes remain unchanged.
Compileall, 278 relevant local links, retained digests and `git diff --check`
pass. No full-suite/corpus or SEC requests.

**Shared approach ready for a bounded multi-issuer direct Revenue/EBIT batch, not
universal financial approval.** Use exact frozen identities and already retained
original bodies/receipts with the existing direct selectors. Require a fixed
issuer/period list and a candidate/exception ledger; stop with named missing
body/metadata/conflict/scope exceptions instead of a follow-on research chain.
No automatic support changes or extension to other field families. Stop after
NVDA; do not begin that batch in this milestone.
