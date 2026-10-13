# Retained year-end cash/investment and debt/lease inspection

Phase 1 only; baseline `1220bd2ee2edaa3867de7eb7ba8066f5554a3b96`.
[Reproducible 199-period ledger](retained-bridge-component-ledger.json) covers
42 non-specialized issuers. Offline replay:
`PYTHONPATH=src .venv/bin/python scripts/inspect_retained_bridge_components.py`.
No SEC requests, financial approvals, registry changes or aggregation.

## Coverage — two independent period denominators

| Family | Periods with eligible observations | Observation-only outcome | Conflicting outcome | No eligible observations | Evidence gaps | Component populations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Cash/investments | 199 | 188 | 11 | 0 | 0 | 855 |
| Debt/leases | 199 | 168 | 31 | 0 | 0 | 2,056 |

Conflict periods are included in the 199 with observations, not additional
periods. Outcomes partition 199 per family. Population counts are distinct
concept observations, not complete balances or independent assets/liabilities.
All family completeness remains **partial/unknown**. Every overlay includes a
null complete-perimeter requirement; observations do not erase it. No evidence
acquisition backlog exists in this pass. XOM has no selected periods; GEV and
SNDK have two each. All eleven five-period-target exceptions persist.

## Explicit exceptions and conservative selection

Cash conflicts: Alphabet's measurement-alternative equity in all five periods;
Walmart cash/equivalents in all five; McDonald's combined cash/restricted cash
at 2022-12-31. These eleven remain unresolved, with original precision and all
values/occurrences. Rounded and more precise unequal values are not reconciled
by a tolerance or numerical adjustment.

Debt conflicts: AAPL 2021 instrument carrying caption; MSFT 2024 commercial
paper; INTC five current-debt captions; WMT five short-term borrowing captions;
CSCO five long-term-debt captions; HD 2022 commercial paper; NFLX 2021/2023/2024
short-term borrowing; TXN five long-term-debt captions; MCD five long-term-debt
captions. The ledger records exact accessions, dates, concepts and every
competing representation for these 31 periods. No note-driven selection,
precedence, new economic interpretation or follow-on research is authorized.

Every family retains unobserved bounded concepts as explicit requirements, not
zero. Dimensioned facts and known combined issuer-extension captions remain
diagnostic-only. Unsupported extension names do not enter standard selectors;
the closed mapping is not a full extension inventory. Comparatives and other
dates remain retained in original bodies, not new period registrations.

## Meaning and evidence depth

`analyst/retained_bridge_components.py` reuses
[shared inspection](retained-component-inspection.md) and verified annual
filing/receipt bindings. Selectors require exact accession, CIK, authoritative
annual-end **instant**, standard namespace, nondimensional USD, numeric/non-nil
status and valid original precision. Scale/sign are explicitly 1; raw XBRL
numeric representations and every confirming context/unit ID remain sources.
Equal amounts with distinct precision are alternatives; unequal amounts leave a
null conflicting component. Invalid units/nil/precision create explicit errors.

The bounded mapping distinguishes cash equivalents, current/long-term
investment captions, marketable securities, restricted cash, equity-method and
nonmarketable equity populations. It does not infer liquidity, unrestricted
status or instrument composition. Debt mappings distinguish current/noncurrent
borrowing, commercial paper, instrument carrying/face candidates, fair value,
principal maturity schedules, discounted lease liabilities and undiscounted
future payments. Historical lease cash payments and ROU assets are explicitly
excluded from liability selection.

Element definitions identify **candidate populations**, not independently
reviewed issuer scope. For example, `LongTermDebt` does not universally establish
face principal or carrying value, and `DebtInstrumentCarryingAmount` cannot
override an issuer note's reviewed presentation. Pilot note interpretations are
not transferred to other issuers. Known possible parent/child and alternative
basis overlap is recorded in rules, observations and flags; it is neither a
complete inclusion graph nor permission to sum. No amount is charged twice,
offset, aggregated or labeled total debt/excess cash.

## Delivery and preservation

Immutable `AnnualComponents` overlays provide separate cash/investment and
debt/lease tuples with original-body receipts and explicit null requirements.
Separate schema `retained-bridge-component-inspection-v1` uses the existing
exact-byte payload transport. Closed deserialization validates hashes and
independently replays the actual retained instance; changed value, role,
precision, identity or source fails. This is inspection, not a new approval
registry or valuation-consumption contract.

All parent histories are returned **unchanged**. Original four pilot values,
alternatives, dimension-specific reviewed components, lease cash observations
and serialized output remain authoritative for their existing scope. The
cohort overlays do not replace them. Separate D&A overlays, all prior income,
CFO, movement, deferred-tax, SBC and Capex results (including LLY v2), frozen
schema 5, policies, registries and corpus are unchanged. Support classes remain
2/40/8; financial sufficiency remains NOT_ASSESSED. Frozen counts remain
1,905/1,483/11/27/42 across 3,468 states.

## Validation and stopping point

Focused checks cover 199 unique selected identities, 42 issuer mappings,
eleven history exceptions, ledger replay, actual XML facts for both families,
independently reviewed pilot statement amounts, dates/units/precision, equivalent
occurrences, conflicts, dimension/extension exclusions, parent/measurement/lease
distinctions, closed serialization and parent/frozen preservation. **46 unique
focused tests pass**: nine new cohort tests, eleven shared inspection regressions,
fourteen pilot cash and twelve pilot debt tests. An overlap tuple/list ledger
report-shape mismatch was fixed and the exact replay test rerun successfully.
Two existing preservation tests pinned the preparation model before the
approved LLY v2 anti-downgrade guard (`78b1527`); only that model's source pins
now use this milestone's reviewed starting HEAD. Both reruns pass. Original
serialized pilot hashes and every other artifact pin remain unchanged; no
production model was edited. Compileall, 2,182 affected local links, 40-register
plus two-seed mapping/count checks and `git diff --check` pass. No full suite or
corpus rerun.

Next bounded field step, only when authorized: retained fiscal-year-end other
equity-bridge claims/assets inspection, with a closed concept mapping and
explicit unknowns, not an equity valuation bridge or a new issuer research loop.
