# Four-pilot retained-evidence field mappings

2026-10-12; starting HEAD `98b3af9fe16a2fc74c7d0d233678f91193533c9a`.
Original milestone: mappings and executable checks only. The subsequent
[direct-income delivery](pilot-direct-income-evidence.md) now advances this matrix
to version 2 with Revenue/EBIT bindings and adapter integration. All other field
dispositions/source-package bindings remain unchanged; no new financial treatment.
[Machine-checkable matrix](pilot-historical-input-mappings.json) accounts for
four existing periods × fourteen [WP0 field families](dcf-input-contract.md).
Mapping statuses are not frozen metric availability states or confidence scores.
No unavailable row asserts that a disclosure is absent from the entire filing.

## Field-family disposition

M = mapped reported inputs for restricted preparation; L = related observations
only, insufficient for complete primitive/timing coverage; U = no adequate
binding/equation in these reviewed packages. M does not mean complete financial
coverage: every family retains unresolved requirements. CFO, Revenue and EBIT
are complete only within their explicitly **reported consolidated subtotal/total**
scope; none certifies timing or consumer sufficiency.

| Contract field | MSFT 2025 | MSFT 2026 | AAPL 2025 | Alphabet 2024 |
| --- | --- | --- | --- | --- |
| Revenue | M | M | M | M |
| EBIT | M | M | M | M |
| D&A | L | L | L | L |
| Cash Capex | M | M | M | M |
| Reported CF working-capital movements | M | M | M | M |
| Deferred taxes | M | M | U | M |
| SBC | M | M | M | M |
| Unclassified CFO reconciliation residual | U | U | U | U |
| CFO | M | M | M | M |
| Reported tax context | M | M | M | M |
| Cash/investment components | U | U | U | U |
| Debt/lease components | U | U | U | U |
| Other equity-bridge claims/assets | U | U | U | U |
| Separately dated point-in-time shares | U | U | U | U |
| **M / L / U** | **8 / 1 / 5** | **8 / 1 / 5** | **7 / 1 / 6** | **8 / 1 / 5** |

Exact selected identities: MSFT CIK 789019, FY2025 accession
`0000950170-25-100235`, 2024-07-01–2025-06-30; FY2026
`0001193125-26-323660`, 2025-07-01–2026-06-30. AAPL CIK 320193,
`0000320193-25-000079`, 2024-09-29–2025-09-27. Alphabet CIK 1652044,
`0001652044-25-000014`, 2024-01-01–2024-12-31. All are exact frozen 10-Ks;
comparative columns are not additional approvals or substituted source periods.

## Exact evidence references and reproducible depth

Version 2 adds eight `retained_direct` bindings to the
[reviewed face-statement matrix](pilot-direct-income-evidence.json), not new
inputs in the immutable cash-flow registries. They retain every eligible direct
candidate/occurrence and both instance and primary-statement receipts. Existing
69 cash-flow-package bindings/76 occurrences remain; eight bindings/25 confirming
direct occurrences are additional. The results below describing original mapping
validation remain a historical record; current selections/counts and validation
are in the [direct-income results](pilot-direct-income-evidence.md).

Matrix `registry_path` / SHA-256 / `registry_bundle_pointer` pin the existing
[MSFT registry](company-data-preparation/msft-reported-cash-flow-bundles.json),
[AAPL registry](company-data-preparation/aapl-reported-cash-flow-bundle.json) and
[Alphabet registry](company-data-preparation/googl-reported-cash-flow-bundle.json).
Each binding's `registry_pointer` identifies the exact source input: numeric
value, namespace/concept, source kind, location/scope, display multiplier,
decimals and every confirming ordinal. The matrix also fixes context, sign,
unit, scale, origin, semantic role and population. Registry `/artifacts` retains
original-body URL/representation/digest/length and actual retrieval metadata.
This avoids copying bodies or inventing source metadata in a second registry.

Existing opt-in loaders independently verify original bodies and exact eligible
occurrences against the pinned registrations; this is deeper than WP0 metadata
validation and not a counts-only corpus join. Alphabet explicitly uses its
[refreshed receipt](evidence/googl-fy2024-instance-provenance-refresh.json),
without recovering or overwriting the original missing time/status. Reviews:
[MSFT](msft-alternative-historical-cash-flow-inputs.md),
[AAPL](aapl-alternative-historical-cash-flow-inputs.md),
[Alphabet](googl-alternative-historical-cash-flow-inputs.md).

Unknowns and limitations have exact registry pointers. Remaining existing inputs
are explicitly listed as supplementary, not discarded or reclassified into
required families: lease payments/costs, borrowing interest where reported,
capital creditors, ROU additions, acquisition/intangible/other investing rows,
withholding and cash FX. They do not supply bridge balances, point shares,
complete interest, complete investment or a new economic adjustment.

## Treatment decisions and finite limitations

- Cash PP&E maps its reported cash-purchase fact, USD scale 1 and statement sign
  −1. Preserve the source magnitude as well; no silently chosen positive Capex
  economic convention or claim of complete reinvestment. Missing allocations
  remain requirements, not amounts inferred from accrual/noncash disclosures.
- Cash-flow working-capital rows preserve every reviewed signed reconciliation
  item individually, including mixed current/noncurrent and tax movements.
  No total or reconstructed book ΔNWC, acquisition/FX bridge or operating-only
  certification. Asset-tag sign reversal does not change the original raw sign.
- MSFT D&A-and-other is a mixed add-back, not pure D&A. Note depreciation and
  finance-lease amortization remain distinct support; their non-overlap and
  completeness are unproved. AAPL's combined D&A cash-flow add-back remains a
  reported observation with timing uncertainty. Alphabet depreciation excludes
  unproved amortization coverage. None of these limitations invalidates a
  previously resolved frozen historical value; no replacement D&A equation.
- MSFT FY2025 deferred adjustment/provision confirmations bind once. FY2026
  14,189m CFO adjustment and 14,424m note provision retain different roles.
  Alphabet −5,257m CFO adjustment is not −5,256m provision. AAPL has no reviewed
  deferred input in its package; mixed OtherNoncash is not a residual allocation.
- SBC expense and CFO add-back share the recognized-expense population but
  remain non-additive roles. Alphabet note expense **22,800m / decimals −8**
  remains separate from **22,785m / −6** add-back. No rounding adjustment,
  duplicate charge, estimate or executable cost proxy is introduced.
- Taxes preserve reported net cash payments versus accrued provision. No
  operating-tax basis/rate, capitalized-interest allocation or economic tax removal.
- Revenue/EBIT and all four bridge/share families have no reviewed mapping from
  these cash-flow packages. Counts-only historical results cannot fill them;
  leases' cash payments/ROU additions cannot become fiscal-year-end debt.

**No CFO residual equation/value is approved.** The original mixed reconciliation
rows remain source observations. The existing complete reported CFO check sums
the independently reported terms once against independently reported CFO:
14 terms for each MSFT year, 10 AAPL, 13 Alphabet. There is no residual operand.
Introducing `CFO − known rows` as a balancing term would be an unclassified
remainder, not independent validation or an FCFF adjustment; it cannot turn
unknown field classification into zero. No other equation or component total is
proposed. D&A, deferred-tax and SBC components are never summed here.

## Validation and preservation

Offline check: `python3 scripts/validate_pilot_input_mappings.py`.
[Focused tests](../tests/analyst/test_pilot_input_mappings.py) exercise all exact
source/period/context/ordinal bindings, sign/scale and precision, null reasons,
distinct roles, duplicate imports/populations, unsupported complete/sum claims,
residual-defined checks and the existing independent CFO equation. The script
returns diagnostics only, not WP0 `InputValue`/bundle instances or adapted values.

Results: 56 field rows = **23 M + 4 L + 29 U**. **69 bound input references**
(19/20/13/17), **76 confirming occurrences** (21/22/15/18); **61 supplementary
inputs** (18/18/8/17) account for the remaining reviewed package inputs.
The 130 existing source inputs and all original unknowns/limits are preserved.
All four independent CFO checks pass. **43 focused tests pass**: 16 new mapping
tests, 24 WP0 model tests and three existing pilot preservation checks.
Compileall, 22 relevant local links and diff
checks pass. No SEC requests, full suite, corpus rerun, adapter or registration.
Frozen schema 5, all policies/outputs, pilot bytes/sidecars, support classes and
baseline 1905/1483/11/27/42 remain unchanged; no original blocker is cleared.

**Smallest next implementation:** an isolated explicit four-period adapter for
only the tested reported mappings, retaining raw and displayed roles, all
limitations and separate serialization; unavailable requirements and D&A support
must not become complete values. No source resolver, residual value, aggregation,
estimates, new period registration or valuation consumption. Before authorizing
that step, preserve the cash Capex magnitude/sign distinction and the separate
support-only versus required-primitive slot semantics. Stop after this mapping pass.
