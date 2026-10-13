# Phase 1 historical-input preparation contract — WP0

Contract/schema `historical-input-preparation-v1`, version 1; 2026-10-12.
The name describes eventual input purpose, **not a DCF consumer or calculator**.
User-approved direction now extends beyond evidence-accounted facts/gaps to
analyst-reviewable preparation. [Decision record](wp0-historical-input-decision.md)
and [original blocker disposition](phase1-blocker-disposition-review.md) retain
the distinction between original metric resolution and alternative paths.
Phase 2 remains prohibited. This contract does not approve economic treatments.

## Delivered fields and identity

| Field family | Required representation and boundary |
| --- | --- |
| Revenue, EBIT, D&A, cash Capex | Separate annual inputs; preserve conflicting candidates and unresolved scope. A precedence choice is not economic equivalence. EBIT expenses must be operating-only. Cash Capex must disclose its purchase perimeter, not silently include acquisitions or noncash additions. |
| Reported cash-flow working-capital movements | Signed annual reconciliation rows, with original accounts/locations and acquisition/FX/reclassification limitations. These are not reconstructed book ΔNWC or certified operating cash investment. |
| Deferred taxes, SBC | Separate annual roles, expense versus reconciliation add-back and tax provision versus cash distinctions. No automatic add-back, removal or second economic charge. |
| Unclassified CFO reconciliation residual | Explicit versioned reconciliation remainder with retained operands and limitations. Not a newly approved FCFF adjustment, unexplained operating expense or hidden zero. |
| CFO, reported tax context | Consolidated cash subtotal and separately identified cash/provision/context inputs. No operating tax suggestion, default rate or tax-shield assumption. |
| Cash/investment components | Exact fiscal-year-end balances and component populations; restricted/unavailable components stay explicit. No knowingly overlapping aggregation. |
| Debt/lease components | Exact fiscal-year-end components with instrument/perimeter distinctions. Lease cash-service choices are not automatically debt treatment. No knowingly double-counted leases, principal or debt. |
| Other equity-bridge claims/assets | Separate fiscal-year-end entries, sign/unit/role and evidence or explicit missing requirement; no equity bridge calculation. |
| Point-in-time shares | Explicit separate observation date, evidence and shares unit. Not diluted weighted-average shares and not a dilution estimate. No quarterly/TTM history expansion. |

`Period` retains CIK, exact selected accession, 10-K form and authoritative annual
start/end. Cash/investment, debt/lease and other bridge entries require annual-end
`as_of`; point-in-time shares require their separately dated observation, not an
invented annual-end number. Unavailable shares may retain an explicitly unknown
observation date; a valued share input cannot. Comparatives are supporting evidence, never implicit
new registered annuals. Source and target period/date mismatches fail validation.

Target **five annual periods** with **three periods as a readiness target**, not
a sufficiency result. Histories are chronological, non-overlapping and capped at
five annual selections in WP0. Short/empty histories require explicit exception
reasons; no fabricated placeholders, predecessor continuity or zeros. Retained
cohort facts remain 189 selected identities and 11 target-history exceptions:
XOM five missing target slots; GEV/SNDK three each. WP0 does not create 189 bundles.

Exclude all eight frozen specialized issuers: BRK-B, JPM, BAC, UNH, GE, GS, WFC,
MS. The immutable CIK exclusion set is checked against the
[frozen classification matrix](universe/phase-1h5-issuer-validation.json).
GE's existing execution/values persist but are not approved for generic use.
The 40-issuer register remains intact; the foundation makes no support change.

## Origin, assessment and unresolved requirements

`Origin` is reported / derived / proxy / analyst override / unavailable.
It is independent of `Quality` (unassessed/supported/limited/conflicting),
`Scope` (unknown/consolidated reported/operating-only/mixed/restricted), scope
description, `Completeness` (complete/partial/unknown) and `Review`
(unreviewed/reviewed/accepted for stated preparation scope). These are not
calibrated confidence scores. A reported fact can have mixed scope and limited
quality. An accepted missing disclosure still has no value and remains unresolved.

Every entry retains ID, exact period, optional observation date, finite Decimal
or null, unit, positive scale, explicit sign multiplier, precision, economic/
presentation role, assessment statuses, flags and unresolved requirements.
Reported `value = raw_value × scale × sign`; all confirming source representations
must agree exactly and retain their original decimals. Rounded observations
stay rounded; no invented tolerances or rounding adjustments. Nulls require
origin unavailable, a specific null reason and unresolved requirements. An
acknowledgment cannot mark a null complete or erase a required missing value.

Manual/proxy/override entries require author, actual UTC timestamp and rationale.
They never acquire fabricated SEC provenance. Contextual SEC evidence may accompany
an analyst choice but does not change its origin. Overrides retain displaced
alternatives; alternatives keep the same target field/period/date/unit and
distinct candidate IDs. Selection rationale is mandatory and never proves
economic equivalence. No default estimate, missing-to-zero conversion, rate or
numerical analyst assumption is supplied by this foundation.

## Evidence depth and derivation boundaries

`SourceReference` retains exact period, original-body `Artifact`/`Receipt`, URL,
typed SHA-256, retrieval UTC/status/mode, locator, QName, context and occurrence
ordinal when present, source dates, dimensions, unit, raw value and decimals.
Note evidence has a locator and no fabricated XBRL occurrence. Reuse the existing
immutable evidence/receipt models without changing their contracts.

**Validation depth is structural:** body integrity, exact accession/period/date/
unit linkage and declared numeric representation, not fresh XML occurrence
verification, authoritative annual-DEI replay or scope review. Those independent
checks must precede real issuer registration; unreviewed metadata is not a
verified fact. WP0 creates no issuer registry, resolver, receipt acquisition,
evidence store or automatic import of existing pilot bundles.

Derived entries require explicit formula ID/version/expression, kind, exact
retained operand IDs and scope-evidence references. Formula dependencies must be
present, valued and acyclic. Model validators do **not execute expressions or
certify supplied arithmetic**; reviewed equation tests are required in the later
field-treatment milestone. Supported descriptor kinds are deliberately limited:

- Component totals require declared non-overlap, retained scope evidence and
  unique operand coverage keys; unknown coverage cannot be called complete.
  Partial coverage forces partial output, even when arithmetic is successful.
- Revenue-minus-expenses can describe EBIT only, requires a revenue operand
  followed by explicitly operating-only expense-role operands and scope evidence.
  A label or user assertion alone does not establish economic equivalence.
- CFO remainders belong only to the unclassified reconciliation-residual field.
  They cannot populate EBIT or authorize an economic adjustment.

Coverage keys prevent known duplicate populations in declared component totals;
they are not proof that differently named populations do not overlap. Semantic
review remains necessary. No general formula execution, financial adjustment,
CF-movement/book-change substitution or cash/debt aggregation engine is provided.

## Packaging, serialization and coverage reporting

The authorized [revision-bound override/review controls](analyst-override-review-controls.md)
now provide a separate local immutable audit and analyst-origin overlay. Explicit
proposals require author/actual UTC time/rationale, normalized value/unit/sign,
precision, exact scope and numerical-assumption labeling where applicable.
Acceptance binds exact relevant-content revisions; stale decisions require new
explicit revalidation. Acknowledgment supplies no number. Original evidence,
alternatives, completeness and unresolved requirements persist; no partial-to-total
promotion or automatic blocker removal. Grouping retains every original diagnostic.
This additive contract supersedes the earlier assembly-only next-step statement;
no prior serializer, policy or financial value is migrated.

The isolated [assembly/review layer](prepared-assembly-results.md) now packages
existing parents and overlays in separate immutable review histories. It copies
values/provenance without promoting support or partial components to totals.
Original parents/pilots remain attached unchanged; source-ledger seals, typed
refresh audits, formulas/operands and invalid-evidence diagnostics survive separate
serialization. Field coverage distinguishes policy-prepared values from support
and component observations. Review priority is configured field importance, not
confidence. Stable targets and click-through payloads confer no acceptance or
blocker-removal authority. No residual, aggregation or financial sufficiency is
calculated. Persistent overrides require a subsequent explicitly authorized
contract with provenance, revision checks and preserved originals.

The subsequently authorized [LLY preparation refresh contract](lly-capex-preparation-refresh.md)
adds a separate `historical-input-preparation-v2` typed wrapper for five exact
Capex entries. It retains original financial approval/fingerprints and unavailable
original status alongside independently reviewed refreshed receipts/digests.
Original byte equivalence remains unproved; no legacy attestation is synthesized.
V2 uses an exact-byte payload-local body table and independent replay. The
existing v1 models/serialization remain supported with byte-identical output;
reserved refresh markers/roles/IDs require v2 and cannot be downgraded silently.
No frozen schema 5, policy, registry, original proof requirement or pilot migration.

Immutable `InputValue` → `AnnualBundle` → `HistoryBundle`. All fourteen field
families must appear per annual, as individually identified components or explicit
unavailable entries; component counts are not additional years. Bundle identity
and positive version are explicit. Flags, limitations, alternatives, missing
requirements and evidence survive separate closed deterministic serialization.
Deserialization revalidates invariants; malformed fields, unknown versions,
duplicate JSON keys, tampered body representations/digests and cross-period
bindings fail. No migration of schema 5 or existing pilot serialization.

`coverage()` reports entry counts by field, origin and completeness, plus available
entries; it does not calculate readiness, confidence or a closure percentage.
Later reports must also show period-level field coverage and distinguish component
counts from complete field coverage, unknowns from zeros, and unavailable target
years from selected years. **90% recent / 80% older are proposed targets only**;
the recent/older partition and required field denominators need explicit later
design. No current coverage claim or automatic closure follows. Material
shortfalls require explicit user acceptance with retained limitations; acceptance
does not resolve required values or establish financial sufficiency.

Bundle producibility is not financial-input sufficiency. The
[timing-readiness contract](financial-timing-readiness-design.md) and future
consumer-specific acceptance remain separate gates before valuation consumption.
Tax suggestions, dilution estimates, lease/SBC economics, allocations and all
forecast/valuation calculations require later explicit design. Phase 2 is paused.

## Preservation, validation and smallest next step

Frozen schema 5, generic and curated policies/registries, corpus outputs and all
four independently reviewed pilot periods remain unchanged. Those four periods
do not approve whole issuer histories. Baseline remains 1905/1483/11/27/42 across
3468 states, 43 executions/seven skips; support classes 2/40/8. No SEC request,
full-suite/corpus run, financial value change or support reclassification in WP0.

Focused tests cover invariants/nulls, origin versus quality, partial totals,
source identity/digests, sign/scale/precision, manual entries, alternatives,
formula operand/scope guards, history exclusions, coverage and closed serialization.
Pinned hashes preserve seven pilot registry/sidecar artifacts and schema 5;
focused existing serialization preservation checks remain valid. Compileall,
relevant local links and diff checks complete the milestone.

Verified WP0 result: **27 focused tests pass** (24 new model tests plus three
existing AAPL/Alphabet/MSFT-sidecar serialized-parent preservation checks).
No existing executable source, financial policy, registry or corpus artifact
changed; retained pilot artifact digests are pinned in focused tests. No full
suite or corpus rerun was required by this isolated, unregistered foundation.

**Next bounded step:** design (not implement without authorization) one retained-
evidence field-treatment and mapping plan for the four existing pilot periods.
Enumerate each WP0 field's available operands, missing required inputs, permitted
origin/role, exact evidence depth and equation tests; separate bridge/share gaps
from annual cash-flow facts. Stop with explicit unresolved requirements rather
than launch new research or assume economic treatments. No new period approval.
Subsequent field-treatment changes must update affected issuer records in the same
milestone, preserving original decisions and explaining rationale/evidence/tests.

The subsequent authorized [four-pilot mapping milestone](pilot-historical-input-mappings.md)
now completes that bounded step with [exact references](pilot-historical-input-mappings.json)
and executable treatment checks, not adapters or additional period registrations.
Its next isolated adapter scope must keep support-only D&A, unavailable families
and all role/precision/coverage limitations explicit; no residual is approved.
