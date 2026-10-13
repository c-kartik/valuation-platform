# Reusable retained-component inspection

Phase 1 implementation; starting HEAD
`0d8b3bdfd56a8e606290e0d6ef5a1d4c1e4b2105`.
[Shared API](../src/valuation_platform/analyst/retained_components.py) /
[focused tests](../tests/analyst/test_retained_components.py).
This is structural inspection, not a financial policy, issuer approval registry,
adapter, formula engine or consumer-readiness decision. No additional issuer,
field or period is registered. No SEC request or financial calculation.

## Public inspection contract

`prepare(period, receipts, bindings)` accepts the existing exact non-amended
annual `Period`, original immutable `Receipt` objects and explicit
`ArtifactBinding(url, sha256, role, digest_type)` specifications. One binding
identifies the extracted instance; additional support bindings identify exact
retained statement/note bodies. Typed digests are
`sha256_sec_response_body_bytes`, never parsed/reserialized representations.
Original metadata is reused, never manufactured. Receipt accession, body hash,
byte length and unique URLs must agree. A missing body produces an explicit
requirement; a digest/identity conflict or structural error fails.

Existing annual-DEI/form, context, unit and fact parsers replay only retained
bodies. `Evidence` returned by `prepare` carries exact period, bound original
receipts, parsed namespace/context mappings, facts with original root ordinals
and missing-body requirements. Namespace/context mappings are read-only.
It is an in-memory inspection result, not a provenance store or a new serialized
schema. Pass the prepared object to inspection; do not synthesize parsed facts.

`inspect(evidence, SelectionSpec(...))` requires explicit:

- Field identity, one or more exact namespace/concept/dimension selectors;
  `()` means nondimensional, not wildcard dimensions.
- Annual-duration or fiscal-year-end-instant mode and exact USD unit.
- Caller-supplied presentation role/scope and unresolved requirements.
  These annotations are not independently certified by matching a tag.

The API filters exact CIK, selected filing, authoritative dates and dimensions;
eligible facts must be non-nil, finite, exact USD with valid declared precision.
It retains raw source values, scale 1/sign +1 (not an output conversion), original
context/unit IDs, decimals, dimension representations and occurrence order.
Explicit dimensions are matched by expanded axis/member sets; source order
is preserved, and differently scoped populations cannot collapse.

Candidates group only namespace/concept, exact Decimal, precision and dimension
signature. Equivalent context IDs or USD unit IDs can confirm while every
occurrence is retained. Different precision or concept representations remain
separate candidates even when values match. Unequal observed values populate
`competing_values` and a specific requirement; absence produces no zero.
Neither numerical agreement nor an empty competing-values list proves scope
equivalence, completeness or non-overlap.

Each candidate retains immutable occurrence data and existing `SourceReference`
objects tied to the original instance receipt, exact period/QName/context/ordinal,
raw value/unit/precision/dimensions. Inspection returns bound support receipts
alongside the specification and unresolved requirements. Primary scope passages
and statement selection remain caller-owned evidence, not automatic financial
acceptance. There is **no `selected`, accepted/completed status, sum, ratio,
adjustment, output bundle or valuation authorization** in this API.

## Pilot routing and separation of responsibilities

| Layer | Shared responsibility | Preserved caller responsibility |
| --- | --- | --- |
| Revenue/EBIT | Exact annual candidate extraction/confirmations/provenance | Existing approved concepts, face-statement checks and conservative selection |
| Cash/investment | Exact nondimensional year-end candidates | Existing policy checks, strategic/restricted/mixed scopes, gates, overlaps and unresolved precision choices |
| Debt/lease | Exact year-end candidates including supplied location/fair-value dimensions | Principal/carrying/fair-value interpretation, parent inclusion, liability-versus-payment roles and unknown perimeter |

All three pilot inspectors call `prepare`/`inspect` and translate observations
back into their **unchanged existing inspection result shapes**. Reviewed issuer
interpretation remains in the existing byte-pinned evidence/mapping data. Shared
inspection does not know those registries, issuers or policies. Candidate inspection
does not itself run statement acceptance checks, and adapters retain their
unchanged output and serialization logic. Cash's prior structural-error boundary
remains conservative. No unrelated refactoring or new generic cascade.

## Exact regression and preservation

The same four pilot periods reproduce eight Revenue/EBIT totals/25 occurrences,
25 available cash observations/40 occurrences plus existing gates/conflicts,
and 60 debt/lease observations/80 occurrences plus one missing commercial-paper
slot. Existing nulls, precision alternatives, support-only D&A, roles/scope,
overlap, limitations and all financial blockers remain unchanged.
Mapping, annual/history versions stay **4**; model and native schemas do not change.
No field dispositions or preparation/support classifications change.

Pre-refactor serialized history SHA-256 pins, checked after routing and on round trip:

| History | Exact serialized hash |
| --- | --- |
| MSFT (FY2025/FY2026) | `e05f85125b6244c321fbdee6469fa89bb809533614bbcc9c5399d2b5c56eb8b5` |
| AAPL (FY2025) | `2772f34db57beb116f4fdb498f0016dc6502d7642b7bbc18f9e89e3645e66f83` |
| Alphabet (FY2024) | `f442e248f1ea2884967680db78c99076ee8beefdaae0bc050b6ee2f0c9b324d5` |

The [mapping](pilot-historical-input-mappings.json), all three reviewed matrices,
original native bundles/sidecars/scenarios, adapter code, model schemas, original
artifact bodies, frozen policies and parser source remain unchanged. The
baseline 1905/1483/11/27/42 across 3468 is retained, not rerun; financial
sufficiency remains NOT_ASSESSED. Mechanism-only updates to the three issuer
records explain shared structural inspection without claiming new coverage.

Validation covers all three field groups/four periods, missing bodies and tags,
wrong annual/instant dates, exact dimensions, unit/precision/nil/identity errors,
equivalent contexts/units, conflicting values and equal values across different
concepts, provenance and exact adapter bytes. **112 focused tests passed**:
11 new shared-interface tests and 101 relevant existing pilot/model/preservation
tests. All four mapping/CFO checks pass, retaining 25/40/80 income/cash/debt
occurrences. All three pre-refactor serialized history hashes match exactly,
including deterministic round trips. Compileall, 405 relevant local links and
`git diff --check` pass; no full-suite/corpus rerun.

## One concrete application beyond the pilots

**Next bounded implementation, only if authorized:** run the shared interface
for direct Revenue and EBIT over the five frozen NVDA selected periods, using
existing approved concept selectors and retained instances only. Deliver an
executable candidate/evidence/exception ledger with original receipts, exact
annual identities and every confirmation/conflict. Missing bodies or semantic
gaps remain explicit exceptions after that fixed pass; no SEC acquisition,
new financial acceptance, adapter registrations or research/design loop.
Acceptance: five exact selected identities reconciled, reproducible results and
focused bindings/conflict tests, with NVDA's preparation record updated and no
changes to frozen output. Stop after the present interface milestone.
