# Phase 1H.5 issuer historical-coverage validation

Starting HEAD `095d31c725d0c1221775c8c7bae19ad0958b8fd6`. Documentation-only
validation using the latest verified Wave 38 corpus and completed research.
No SEC requests, policies, tests or full corpus rerun. The
[machine-checkable matrix](phase-1h5-issuer-validation.json) contains all fifty
issuer decisions, all fifty-one security mappings, exact recorded annual end
dates, all measure/status counts, rationales and provenance/comparability limits.

## Decision and classification criteria

**Phase 1H.5 complete; ready for Phase 1H.6 with explicit limitations.**
Classification: **2 SUPPORTED, 40 GENERALIZATION_REQUIRED, 8
SPECIALIZED_METHODOLOGY_REQUIRED = 50 issuers**. All 51 frozen security rows
map once to these issuers; GOOG/GOOGL remain separate securities of one CIK.

SUPPORTED requires expected five-period history and no material core historical
technical/policy gaps under the [documented criterion](sp500-top-50-failure-taxonomy.md#issuer-level-post-smoke-classification).
The core assessment includes Revenue, Operating Income, Pretax, taxes/Reported
ETR, D&A, Capex, weighted-average shares, cash, Operating NWC and comparable
NWC changes. The first NWC change is intentionally not comparable. This is
not a new policy, a 100%-of-all-seventeen-fields requirement or FCFF certification.
META and COST meet historical core support; their ancillary debt/investment
missing states remain explicit and are not retrospectively certified as zero.
All other ordinary issuers have material core gaps or inadequate history.

GE is reassessed from the historical GENERALIZATION_REQUIRED planning label to
SPECIALIZED_METHODOLOGY_REQUIRED for its consolidated industrial/run-off-insurance
perimeter. This constituent review makes explicit the [completed methodology
finding](../operating-income-cvx-ge-perimeter.md) and [Capex review](../capex-ge-perimeter.md),
not an automatic promotion from a research enum. Unsupported industrial-only
allocation and changing continuing perimeter prevent generic full-company support.
**Eight specialized classifications are not eight skips:** GE's five-period
generic execution and all its existing states are retained; seven other issuers
remain intentionally skipped. No execution routing or production enum changes.

## All-company decision matrix

S = SUPPORTED; G = GENERALIZATION_REQUIRED; X = SPECIALIZED_METHODOLOGY_REQUIRED.
R/M/A/B/NC are resolved/missing/ambiguous/methodology-blocked/not-comparable
standardized states. The compact limitation column lists material core gaps;
the JSON additionally records every ancillary gap and each issuer's rationale,
source references and comparability/provenance caveats. Zero skip counts mean
no generic history was evaluated, not zero economic values or absent SEC filings.

| Issuer (security tickers) | CIK | Class | History | R / M / A / B / NC | Material limitation |
| --- | ---: | --- | --- | --- | --- |
| NVDA | 1045810 | G | 5 annual periods | 50 / 34 / 0 / 0 / 1 | capex, change_in_operating_nwc, operating_nwc |
| AAPL | 320193 | G | 5 annual periods | 70 / 5 / 0 / 9 / 1 | change_in_operating_nwc, operating_nwc |
| MSFT | 789019 | G | 5 annual periods | 62 / 13 / 0 / 9 / 1 | change_in_operating_nwc, operating_nwc |
| AMZN | 1018724 | G | 5 annual periods | 45 / 39 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc, pretax_income, reported_effective_tax_rate |
| GOOGL, GOOG | 1652044 | G | 5 annual periods | 60 / 15 / 0 / 9 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| AVGO | 1730168 | G | 5 annual periods | 46 / 38 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| META | 1326801 | S | 5 annual periods | 63 / 21 / 0 / 0 / 1 | Historical core supported; ancillary gaps/timing caveats |
| MU | 723125 | G | 5 annual periods | 35 / 49 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc, pretax_income, reported_effective_tax_rate |
| TSLA | 1318605 | G | 5 annual periods | 40 / 44 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| AMD | 2488 | G | 5 annual periods | 47 / 37 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| BRK/B | 1067983 | X | not evaluated (skip) | 0 / 0 / 0 / 0 / 0 | Dedicated methodology; generic history not evaluated |
| LLY | 59478 | G | 5 annual periods | 50 / 34 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc |
| JPM | 19617 | X | not evaluated (skip) | 0 / 0 / 0 / 0 / 0 | Dedicated methodology; generic history not evaluated |
| XOM | 2115436 | G | 0 annual periods | 0 / 0 / 0 / 0 / 0 | Empty CIK-scoped history |
| JNJ | 200406 | G | 5 annual periods | 55 / 29 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc |
| V | 1403161 | G | 5 annual periods | 50 / 34 / 0 / 0 / 1 | change_in_operating_nwc, diluted_weighted_average_shares, operating_nwc |
| INTC | 50863 | G | 5 annual periods | 46 / 38 / 0 / 0 / 1 | cash_and_cash_equivalents, change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| WMT | 104169 | G | 5 annual periods | 45 / 34 / 5 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc, revenue |
| ABBV | 1551152 | G | 5 annual periods | 40 / 44 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| MA | 1141391 | G | 5 annual periods | 49 / 34 / 1 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc, revenue |
| CSCO | 858877 | G | 5 annual periods | 55 / 29 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc |
| LRCX | 707549 | G | 5 annual periods | 43 / 41 / 0 / 0 / 1 | capex, change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| PLTR | 1321655 | G | 5 annual periods | 46 / 38 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc |
| AMAT | 6951 | G | 5 annual periods | 49 / 35 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| CVX | 93410 | G | 5 annual periods | 37 / 42 / 5 / 0 / 1 | cash_and_cash_equivalents, change_in_operating_nwc, operating_income, operating_nwc, revenue |
| COST | 909832 | S | 5 annual periods | 70 / 14 / 0 / 0 / 1 | Historical core supported; ancillary gaps/timing caveats |
| CAT | 18230 | G | 5 annual periods | 40 / 44 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc, pretax_income, reported_effective_tax_rate |
| MRK | 310158 | G | 5 annual periods | 48 / 36 / 0 / 0 / 1 | capex, change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| BAC | 70858 | X | not evaluated (skip) | 0 / 0 / 0 / 0 / 0 | Dedicated methodology; generic history not evaluated |
| PG | 80424 | G | 5 annual periods | 46 / 38 / 0 / 0 / 1 | cash_and_cash_equivalents, change_in_operating_nwc, operating_nwc, pretax_income, reported_effective_tax_rate |
| UNH | 731766 | X | not evaluated (skip) | 0 / 0 / 0 / 0 / 0 | Dedicated methodology; generic history not evaluated |
| KO | 21344 | G | 5 annual periods | 51 / 33 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc |
| GE | 40545 | X | 5 annual periods | 27 / 57 / 0 / 0 / 1 | Industrial/insurance and separation perimeter |
| PM | 1413329 | G | 5 annual periods | 33 / 51 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc, pretax_income, reported_effective_tax_rate |
| HD | 354950 | G | 5 annual periods | 40 / 44 / 0 / 0 / 1 | capex, change_in_operating_nwc, operating_nwc |
| NFLX | 1065280 | G | 5 annual periods | 50 / 34 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc |
| KLAC | 319201 | G | 5 annual periods | 47 / 37 / 0 / 0 / 1 | change_in_operating_nwc, operating_nwc |
| TXN | 97476 | G | 5 annual periods | 50 / 34 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| GEV | 1996810 | G | 2 annual periods | 12 / 21 / 0 / 0 / 1 | Short history; capex, cash_and_cash_equivalents, change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| GS | 886982 | X | not evaluated (skip) | 0 / 0 / 0 / 0 / 0 | Dedicated methodology; generic history not evaluated |
| SNDK | 2023554 | G | 2 annual periods | 20 / 13 / 0 / 0 / 1 | Short history; change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| ORCL | 1341439 | G | 5 annual periods | 30 / 54 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc, pretax_income, reported_effective_tax_rate |
| WFC | 72971 | X | not evaluated (skip) | 0 / 0 / 0 / 0 / 0 | Dedicated methodology; generic history not evaluated |
| MS | 895421 | X | not evaluated (skip) | 0 / 0 / 0 / 0 / 0 | Dedicated methodology; generic history not evaluated |
| LIN | 1707925 | G | 5 annual periods | 39 / 45 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc, pretax_income, reported_effective_tax_rate |
| IBM | 51143 | G | 5 annual periods | 45 / 39 / 0 / 0 / 1 | change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| QCOM | 804328 | G | 5 annual periods | 50 / 34 / 0 / 0 / 1 | capex, change_in_operating_nwc, operating_nwc |
| VZ | 732712 | G | 5 annual periods | 40 / 44 / 0 / 0 / 1 | capex, change_in_operating_nwc, depreciation_and_amortization, operating_nwc |
| PEP | 77476 | G | 5 annual periods | 45 / 39 / 0 / 0 / 1 | capex, change_in_operating_nwc, operating_nwc |
| MCD | 63908 | G | 5 annual periods | 39 / 45 / 0 / 0 / 1 | change_in_operating_nwc, diluted_weighted_average_shares, operating_nwc, pretax_income, reported_effective_tax_rate |

## Reconciliation and provenance

The retained source corpus reports 43 generic completions, seven specialized
execution skips, zero pipeline failures, 204 annual periods × 17 measures =
3,468 states: **1,905 resolved / 1,483 missing / 11 ambiguous / 27 methodology-
blocked / 42 not-comparable**. Measure coverage matches the [exit-plan table](../phase-1h-generalization-exit-plan.md#current-production-reconciliation).
Capex remains **167/37/0**, with 147 direct + 20 curated resolutions;
original 57 gaps = 20 approved + 37 unapproved, partitioned 17 concept / 17
derivation / three methodology research gates. No research gate is silently
converted to a production methodology-blocked state.

The JSON retains the original runner JSON bytes losslessly as gzip/base64,
with explicit local-runner representation, SHA-256, byte length, run timestamp
and reported HEAD/dirty flag. It is **not an SEC-response artifact**. The source
run reports the pre-implementation-commit HEAD with a dirty worktree; the
[verified implementation results](../capex-visa-scope-evidence-results.md) bind
that run to the validated milestone. This is not claimed as a fresh clean-HEAD
run. Subsequent documentation-only commits preserve production behavior.
Compact corpus evidence does not contain every accession/context/occurrence or
raw SEC artifact; reviewed policy/research documents and their inventories remain
the authority for those identities and digests. No missing provenance fields
are synthesized. This pass verifies corpus identity/counts and evidence links,
not a new digest review of every filing or fresh SEC validation.

## Material limits the freeze must preserve

- XOM: execution completes with **zero selected periods**, not the target five;
  strict CIK ownership/succession remains unresolved. No predecessor traversal.
- GEV/SNDK: **two periods each**; no asserted five-year or predecessor history.
  GEV includes a spin-off/carve-out boundary; SNDK has post-separation history.
  Forty other histories have five selected periods: 200 + 2 + 2 = 204.
- GE: mixed industrial/insurance perimeter and HealthCare/Vernova separations;
  no stable five-year industrial-only basis or later-recast substitution.
  CVX affiliate/operating perimeter remains GENERALIZATION_REQUIRED, not
  automatically specialized, and no Operating Income equation is approved.
- WMT/MA/CVX: eleven genuine Revenue conflicts; no arbitrary winner.
  GOOGL/MSFT/AAPL: all 27 production methodology-blocked NWC states.
  Forty-two opening NWC changes remain separately NOT_COMPARABLE.
- Core and ancillary gaps in each row remain typed; missing is not zero and
  EXPECTED_TYPED_MISSING needs affirmative absence/non-applicability evidence.
  Visa/MCD share gaps, D&A timing/inventory/incentive questions and separately
  gated extensions remain unresolved. Capex research is closed; reopening needs
  the specific new completeness evidence, not another broad issuer sweep.
- Historical selected-accession values are not a common-perimeter restated
  series. Reviewed exact-accession approvals do not extend to future/amended
  filings; their policy versions, provenance and conservative conflicts persist.
- Generic/MSFT D&A basis is insufficiently evidenced; Visa expense basis alone
  does not prove joint FCFF timing compatibility. Unknown is not incompatible,
  and does not invalidate resolved historical values. Book inventory/NWC needs
  the [future timing contract](../financial-timing-readiness-design.md) before
  FCFF consumption. Weighted-average shares are not a valuation-share denominator.
- Banks, investment banks, managed-care and financial conglomerate skips remain
  dedicated-methodology exclusions. No entire Top 50 supported-universe claim.

## Freeze readiness and next milestone

**Ready for Phase 1H.6 — freeze historical normalization v1**, with the above
supported scope, explicit exclusions, deferred coverage and provenance limits.
No classification-critical evidence gap requires a new implementation or SEC
request. This does not complete the freeze or resume forecast/FCFF/DCF work.
The freeze must record the policy/output contract, approved evidence versions,
limited histories, typed unresolved states and absence of integrated FCFF
certification. Debt, investments, shares and sector NWC improvements remain a
bounded deferred backlog, not invented freeze prerequisites.

Validation: frozen CIK/security identity bijection; 50 classifications / 51
security mappings; source byte digest; per-issuer and all seventeen measure
counts; history and skip/classification distinctions; 57/20/37 Capex partition;
evidence references and local links; `git diff --check`. No code, policy, frozen
universe/inventory change, tests or corpus rerun.
