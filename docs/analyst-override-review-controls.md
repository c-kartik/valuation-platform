# Revision-bound analyst decisions and grouped review

Phase 1 only. The [historical-input contract](dcf-input-contract.md) and
[assembled sources](prepared-assembly-results.md) remain authoritative.
`analyst/analyst_overrides.py` adds opt-in local persistence and a separate
analyst overlay, not a financial resolver or a replacement source history.
No real issuer override, assumption, acceptance or local decision store is
registered in this milestone; examples/tests use synthetic decisions only.

## Target and revision contract

Targets reuse assembly's exact CIK/accession/field/component IDs. Field-level
targets are writable only when there is exactly one source population; multi-
component families require an explicit component target. Observation date,
share-class dimensions, role, unit and financial scope come from that population,
not a new manual date/class or an implied issuer total.

SHA-256 relevant-content revisions include all populations/candidates within
the annual field, raw representations, precision, signs/scale, source URLs,
typed body digests/representations, occurrences/contexts/dimensions, scope and
completeness, formulas, binding categories and detailed diagnostics/refresh
review references. Transport timestamps/status/mode and whole-ledger seals
are excluded; changing retrieval time alone is not a financial revision.
Changed facts, evidence, alternatives, interpretation or diagnostics stale
the decision. Unrelated fields/issuers do not stale it. No hash establishes
economic equivalence or changes financial approval requirements.

## Persistence and explicit decisions

`AuditStore(directory)` uses a caller-chosen local directory; there is no default
estimate or automatic store in the repository. `record()` requires a current
`Target`, explicit author/rationale and action. Runtime records actual UTC time.
`PROPOSE` supplies a finite normalized value, matching unit/sign, stated precision,
exact compatible scope and `NUMERICAL_ASSUMPTION` or
`CLASSIFICATION_CORRECTION`. Cash Capex cannot become a positive inflow.
It supplies no default numerical assumption. Unknown share dates/classes cannot
be manufactured. Scope expansion requires a separate treatment milestone.

Explicit `ACCEPT` references the exact proposal/current revision; proposal alone
does not apply. `REVALIDATE` is a new explicit author/time/rationale event after
changed-source review; old events are retained. `REVOKE` withdraws applicability,
not history. `ACKNOWLEDGE` contains no number and leaves required values unresolved.
No decision clears source invalid-evidence/conflict/overlap/completeness diagnostics.

Each immutable `event-N.json` is exclusively created and SHA-256 chained. A local
event retains its displaced source snapshot (value, alternatives, evidence
references, period, scope, coverage keys and exact review payloads, including
typed refresh review details where applicable); revalidation adds the new snapshot
without replacing the old one. Retained original bodies remain at their exact
digest references, not duplicated or re-fetched by this store. A local
writer lock and atomic `HEAD.json` anchor serialize append operations. Restart
validates closed keys, sequence, chain, head, exact proposal references and UTC
manual identity. Missing/tampered/unanchored events fail closed. An interrupted
append may leave an unanchored event: stop for explicit local-store recovery,
never silently truncate history. This is local integrity checking, not an
adversarial signing service; a malicious writer replacing both history and head
is outside its trust boundary. Back up the complete directory, not only the head.

## Overlay and serialization

`overlay(prepared, store)` returns immutable analyst-origin patches plus applied,
stale, acknowledgment and dependent-derivation review IDs. Original histories,
facts, ledgers and accepted pilot bytes are not rewritten. Stale or unregistered
targets cannot apply. Concurrent field/component decisions for the same source
population fail rather than silently select precedence.

Each patch retains the displaced original as an alternative, including all its
evidence/candidates; manual identity is the decision's identity, not SEC provenance.
Normalized value uses scale 1; source raw scale/precision/sign remain in the
alternative. Analyst precision and assumption classification remain explicit.
Original completeness, scope, limitations, coverage keys and unresolved
requirements persist, even when a number is supplied. A partial component cannot
become a complete aggregate. Dependent formulas are flagged for review, not
recalculated or certified against a changed operand. Patches are separate, not
automatic substitutions into a financially sufficient history.

Separate closed `analyst-input-overlay-v1` serialization includes patches and
audit decisions. Deserialize rebuilds against the current exact `PreparedHistory`
and anchored store and rejects any discrepancy. The assembled parent (including
typed LLY refreshed-evidence history) remains separately required; this is not
a downgrade of refresh provenance into a legacy source attestation. No prior
serializer/schema migration. No total, residual, assumption engine, economic
adjustment, financial sufficiency approval or valuation calculation.

## Grouped queue

The subsequent [primary field-family workflow](preparation-review-workflow.md)
now nests these unchanged cause groups under one annual/field primary item.
Stable component IDs, original details and revision/audit semantics are unchanged;
full/latest filters and separate history exceptions are presentation only.

`grouped_queue()` groups by issuer/accession/field/actionable cause and review
class. Stable group IDs do not depend on count, priority or value. Every original
card is retained in expandable `details`, including source/alternative/refresh
payloads. A card may appear in several cause groups: original diagnostic count,
group count and expanded detail memberships are different denominators.

Missing values/requirements, conflicts, invalid evidence and overlap remain
actionable. Partial/unreviewed **valued support/component/operand** scope is an
informational observation unless conflicting; separate completeness/null/overlap
groups remain actionable. History exceptions are informational retained
limitations, not fabricated periods. No issue is accepted or discarded by grouping.
Priority remains configured field importance, not confidence or materiality.

## Validation and stopping point

[Reproducible retained summary](grouped-preparation-review-summary.json): 42
histories / 199 annuals; 17,605 original diagnostic cards → 9,886 cause/review-class
groups (8,308 actionable, 1,578 informational). Group detail memberships exceed
card counts because cards can have multiple causes. Forty register records plus
META/COST seed notes describe the changed mechanism, not new financial review.

Focused tests exercise synthetic append/restart, explicit acceptance/revalidation/
revocation, null acknowledgment, stale values/candidates/evidence/scope/date/class,
transport-time independence, invalid values/units/signs/scope/provenance, partial
coverage, dependency flags, separate serialization, tampering/missing events,
group membership and source/pilot/frozen preservation. Actual retained assembly
is used for queue replay only; no real override values are supplied.

Next bounded milestone: validate the end-to-end local review workflow and its
delivery coverage/reporting using synthetic decisions and current retained
bundles, including stale/restart recovery and unresolved-field denominators.
Do not start new extraction/research or financial acceptance automatically.

Verified result: **58 unique focused tests pass** (14 synthetic override tests,
nine assembly/grouping tests, 24 immutable input-model tests and eleven shared
inspection regressions). The combined 54-test run used the initial ten override
cases; all fourteen final override cases were then rerun after additive guards.
Original pilot hashes, retained ledgers/evidence, financial policies/models and
frozen artifacts pass preservation checks. Compileall, 2,459 affected local
links, forty-plus-two mappings, exact queue memberships/counts and
`git diff --check` pass. No full suite/corpus or SEC requests.
