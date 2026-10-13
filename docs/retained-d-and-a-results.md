# Retained D&A preparation — separate annual overlays

Phase 1 only, baseline `78b15277293d35442eb178b962a44713a8271881`.
[199-period ledger](retained-d-and-a-ledger.json), 42 non-specialized issuers;
offline replay: `PYTHONPATH=src .venv/bin/python scripts/inspect_retained_d_and_a.py`.
No SEC requests, new scope approval, fallback, equation, registry or economic
adjustment. Frozen-v1 output is not imported as a substitute for evidence.

## Actual coverage, separately reported

| Required D&A outcome | Selected periods |
|---|---:|
| Existing generic direct policy | 105 |
| Existing MSFT derivation | 5 |
| Existing Visa curated policy v1 | 5 |
| Unapproved scope / component completeness | 84 |
| Conflicting / missing evidence bindings | 0 / 0 |
| **Total** | **199** |

**115 approved values**, not 199 resolved values. **199 periods have support-only
observations (1,320 populations)**; all remain partial/unknown complete-family
coverage, never additional D&A charges. Observation counts are not complete
operating expense, CFO reconciliation or consumer sufficiency. No eligible
observations are absent in this retained pass; absence elsewhere is not zero.

All 45 original artifact requirements for the five Visa entries match retained
original bodies. **Zero deduplicated acquisition/evidence blockers**. Existing
proof checks bind nine artifacts per entry, selected filing/annual DEI, primary
and dimensioned supporting facts, units, precision, reviewed scope and all
confirming occurrences. No Capex approval or refresh is transferred to D&A.
Missing or changed registered bodies would leave the corresponding value blocked.

The 84 periods needing financial scope/completeness approval are explicit, not
missing-artifact requests: GOOGL, AVGO, TSLA, AMD, INTC, WMT, ABBV, MA, LRCX,
MRK, TXN, ORCL, LIN, IBM and VZ five each; AMAT three; PM two; GEV/SNDK two each.
Components alone do not approve a sum. Exhausted issuer research and the separate
AMD extension/TXN inventory-timing gates are not reopened.

## Existing-policy replay and evidence basis

- Generic `D_AND_A_POLICY` accepts only
  `us-gaap:DepreciationDepletionAndAmortization`; it has no published version,
  represented explicitly as null/unversioned. The shared inspector verifies
  exact accession/CIK/authoritative annual/nondimensional USD/precision bindings.
  Equal numeric signatures may select one value; every occurrence and differing
  original precision remain sources/alternatives. Unequal values stay conflicting.
- Existing `msft_annual_d_and_a_v1` alone permits
  `Depreciation + AmortizationOfIntangibleAssets` for CIK 789019. The unchanged
  arithmetic resolver executes with exact verified same-annual operands, and
  retains equation, source facts/contexts/precision and policy identity/version.
  Separate observations for other issuers cannot invoke that equation.
- Selectors receive exact integer signatures internally, not fabricated Company
  Facts receipts. Output evidence is rebound to actual filing-XBRL sources;
  fractional USD that cannot be represented by the unchanged numeric selector
  without float conversion is an explicit error, not rounded. No frozen values
  or counts-only corpus evidence populate an input.
- Visa `d_and_a_scope_equivalence` v1 is executed only after original artifact
  byte verification and exact reviewed-entry matching. Full serialized policy
  audit, scope evidence, original/support occurrence identities and artifact
  references survive the preparation payload. No refreshed D&A approval exists
  or is implicitly registered by this pass.

These are **existing historical policy approvals**, not retrospective timing
certification. Generic/MSFT timing evidence and integrated FCFF compatibility
remain insufficient/unproved under the [timing contract](financial-timing-readiness-design.md).
Visa's expense-basis review does not certify its joint consumer compatibility.

## Required values versus observations and parent preservation

`analyst/retained_d_and_a.py` produces immutable, exact-period `AnnualDAndA`
overlays containing one required slot, separate raw support populations and
explicit approved-derivation operands when applicable. Parent histories are
returned **unchanged**, including all four accepted pilot annuals and the LLY
Capex preparation-v2 wrapper. Newly approved pilot D&A is delivered separately;
the earlier support-only D&A, omissions and serialized pilot bytes persist.
There is no automatic merge or blocker removal.

Bounded exact concept-role mappings distinguish depreciation/amortization
components from mixed impairment/accretion/other-noncash, finance/operating-lease
amortization, debt-financing costs and restricted asset populations. Extensions
remain support-only and separately flagged. Annual/dimensioned observations retain
scope and raw signs; instant balances or nonannual contexts stay diagnostic-only.
Roles identify populations, **not independently reverified statement placement**.
The raw observation role, policy-approved required role and note/CFO support
must not be collapsed or charged twice. No residual, lease adjustment or new sum.

Separate schema `retained-d-and-a-preparation-v1` retains the existing immutable
input/evidence types and exact-byte payload transport. Closed deserialization
independently reparses the original instance and reruns policy selection/audits.
Tampered policy/value/source/precision or unsupported versions fail validation.
All prior income/CFO/movement/deferred-tax/SBC/Capex values and serialized formats
remain unchanged; no unnecessary migration of preparation v1/v2 or frozen schema 5.

Forty register records plus META/COST seeds remain distinct; eleven history
deficits persist (XOM empty, GEV/SNDK two annuals). All eight specialized issuers,
including GE, remain excluded from this 199-period pass. Frozen corpus remains
D&A 115/89/0; aggregate 1,905/1,483/11/27/42 across 3,468. The five additional
frozen missing periods are excluded GE, not hidden generic preparation history.
No full-suite or corpus rerun.

## Validation and stop

Focused tests cover actual XML values/source positions, direct and approved
MSFT/Visa policies, exact identity, duplicate/conflicting values, dimensions,
units/precision, scope exclusions, missing registered artifacts, overlay replay
and serialization, parent/pilot/Capex-v2 preservation and unchanged financial
policy/registry/schema artifacts. **61 unique focused tests pass**: eight new
overlay/replay/preservation tests, 39 curated-policy tests and fourteen existing
direct/MSFT normalization tests. Compileall, 2,093 affected local links, exact
40-register-plus-two-seed mappings, counts and diff checks pass. Stop after this
retained pass.

Next bounded field step, only when authorized: retained fiscal-year-end cash/
investment component inspection across this same selected cohort, preserving
scope/overlap/missing-component limits without aggregates. Do not start a new
D&A issuer-research chain or reopen the 84 scope/completeness gates without
specific new evidence/authorization.
