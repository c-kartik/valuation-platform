# Retained other-bridge claims/assets and point-in-time shares

Phase 1 only; baseline `cbe33aba56133c1b8b03153f883aface272180da`.
[Machine-checkable ledger](retained-claims-shares-ledger.json) accounts for
199 selected periods × two fields = 398 slots across 42 non-specialized issuers.
Forty register issuers plus META/COST seeds; XOM remains empty, GEV/SNDK two
periods each. Eleven target-history exceptions persist. No SEC requests,
additional selected periods, policy expansion or issuer research chain.

## Observations and explicit requirements

| Family | Periods with observations | Observation-only outcome | Conflicting outcome | Invalid-evidence outcome | No eligible / unsupported-only | Populations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Other-bridge claims/assets | 199 | 143 | 48 | 8 | 0 / 0 | 8,404 |
| Point-in-time shares | 199 | 199 | 0 | 0 | 0 / 0 | 241 |

49 bridge periods contain conflicting components: 48 conflicting outcomes plus
TSLA 2021 (also invalid preferred evidence). The eight error outcomes are TSLA
2021 preferred stock and MRK 2021/2024 and PM 2021–2025 pension-asset populations
with nil/invalid numeric/precision evidence. Original diagnostics retain each
exact context/ordinal, dimension, raw/nil status and receipt. No body or receipt
is missing, and no acquisition is proposed. Other valid observations survive.

25 share periods have dimensioned classes: five each for Alphabet, META, Visa,
MA and PLTR. 188 periods have a non-year-end share observation; eleven have an
actual year-end observation. No selected filing has multiple eligible share
dates in this pass, but the API and tests preserve distinct dates independently.
241 class/date populations do not establish 199 complete issuer share totals.

Both fields report observation availability, conflicts, no eligible observations,
unsupported namespace/scope candidates and invalid/missing evidence separately.
Outcome totals partition 199 per field; a period with conflicting or invalid
components can still contain other eligible observations. Actual coverage is in
the ledger's `summary`; population counts are not complete field coverage.

Other-bridge mappings are closed, explicitly named elements: preferred carrying,
redemption and liquidation bases; equity versus redeemable NCI; pension funded
status, gross obligations, accumulated/projected bases, fair/gross plan assets
and recognized current/noncurrent captions; equity-method/other long-term
investments; NOL DTAs, broader carryforward/gross/net DTAs and valuation allowance
support. No asset/liability netting, pension calculation, DTA realization claim
or valuation adjustment. A bounded retained IBM instance check identified the
specific pension fair/gross/noncurrent asset elements added to the map; it did
not approve their financial consumption or start new issuer research.

Dimensions retain exact plan, jurisdiction and other population identities;
dimensioned observations are not automatically consolidated. Unequal values
within one concept/date/dimension population remain null components with all
alternatives; values from different accounting bases or populations are not
merged. Broader deferred-tax totals cannot substitute for pure NOL assets.
Equity-method and long-term investment observations explicitly overlap the
[earlier investment family](retained-bridge-component-results.md). They are not
new independent assets or permitted additions to an equity bridge.

Shares inspect only exact `dei:EntityCommonStockSharesOutstanding` with an
instant context, correct CIK and `xbrli:shares` unit. Actual observation dates
remain independent of fiscal year end. Every date/dimension population retains
all confirmations and precision alternatives. Class/member names are not ticker
mappings, equivalent securities, issuer totals or dilution estimates. No date
selection, class summation or use of one class as total. Basic/diluted weighted-
average facts are diagnostic exclusions, never share-denominator substitutes.
Comparative observations in a selected filing are supporting evidence, not
additional registered periods or quarterly/TTM expansion.

Absent mapped facts are not zero or proof of no claim, tax asset or share class.
Every annual overlay includes an explicit unresolved complete-perimeter/issuer-
share-total requirement, even where observations exist. Unsupported extensions
stay diagnostic; a closed mapping is not an exhaustive issuer-extension review.

## Evidence, serialization and preservation

The shared [inspection API](retained-component-inspection.md) now adds an explicit
dated-instant/share-unit path. Existing annual/year-end USD calls produce the
unchanged prior cash/investment/debt ledger. Sources retain exact accession,
authoritative annual identity, actual context/date/dimensions, unit, scale/sign,
raw numeric/precision, occurrence ordinal and original-body receipt/digest.
No receipt metadata, fact identity or absent amount is synthesized.

Separate immutable `AnnualClaimsShares` overlays use closed
`retained-claims-shares-inspection-v1` serialization and existing exact-byte body
transport. Deserialization revalidates the original instance and independently
replays date/class/concept selection. Changed body/value/role/date/class/precision
or unknown versions fail. Partial observation scope and review requirements
survive; no schema 5, preparation v1/v2 or pilot migration.

Parent annual histories, prior D&A and instant-component overlays, accepted
pilot values/alternatives/bytes, financial policies/registries and corpus remain
unchanged. Frozen baseline remains 1,905/1,483/11/27/42 across 3,468; support
classes 2/40/8 and financial sufficiency NOT_ASSESSED. Observational preparation
does not clear NWC/timing/financial blockers or certify valuation readiness.

## Validation and next bounded milestone

Focused tests check every exact identity/slot, actual retained XML sources,
instant dates versus duration and FY-end, dimensions/classes, shares/USD units,
raw sign/scale/precision, confirmations/conflicts, accounting-basis and overlap
boundaries, closed serialization/replay and original payload preservation.
**20 focused tests pass**: eight new claims/share cohort tests, eleven existing
shared-inspection regressions and the existing full parent/pilot/frozen bridge
preservation test. Its source-byte check now excludes only the intentionally
extended shared inspector; original USD ledger replay, pilot payload hashes and
all financial-policy/schema/evidence byte pins remain enforced. No financial
model or frozen artifact was changed. Compileall, 2,276 affected local links,
40-register-plus-two-seed mapping, 199 identities/398 slots and eleven history
exceptions reconcile; `git diff --check` passes. No full-suite or corpus rerun.

**Next: isolated bundle assembly and review controls**, only when authorized.
Combine existing prepared parents and separate overlays into opt-in review
packages with all contract families accounted for, deterministic source selection
logs, cross-family duplicate/overlap warnings and explicit unresolved values.
Preserve original accepted pilot packages as immutable references; do not silently
replace them. Review acknowledgment must not resolve a missing value, select a
conflict, approve a class total or establish financial sufficiency. Keep unassessed
tax context/residual/other requirements explicit. No new extraction/research,
financial equation, estimate, economic treatment or valuation calculation.
Acceptance: exact cohort/period reconciliation, unchanged sources/values,
serialization replay and review controls preventing implicit approval. Stop with
one finite exceptions list for user review, not another issuer-research sequence.
