# Historical normalization v1 — qualified scope freeze

Phase 1H.6 complete, 2026-10-11. Frozen implementation reference:
`3fff1535012572f418b77f9999a26f651f9f475b` (documentation-only freeze).
This names a supported historical contract, not complete Top 50 support,
universal field coverage, a Git tag, or integrated FCFF certification.

## Baseline and issuer boundary

The [completed issuer validation](universe/phase-1h5-issuer-validation.md) and
[decision matrix](universe/phase-1h5-issuer-validation.json) govern issuer support:
**2 SUPPORTED (META/COST), 40 GENERALIZATION_REQUIRED, 8
SPECIALIZED_METHODOLOGY_REQUIRED**, across 50 issuers / 51 securities.
GOOG/GOOGL share one issuer. Historical core support is not full-field support.

Execution is separately **43 generic completions / seven specialized skips**.
GE is the eighth specialized classification for its industrial/insurance and
separation perimeter; its five-period generic execution and existing values
remain retained, not certified as a stable industrial-only series. Skips are
BRK-B, JPM, BAC, UNH, GS, WFC and MS. XOM has no selected history under its
current CIK; no predecessor traversal is approved. GEV/SNDK have two periods
each. Forty other histories have five periods: 200 + 2 + 2 = **204**.

The [measure reconciliation](phase-1h-generalization-exit-plan.md#current-production-reconciliation)+is frozen at **204 periods × 17 measures = 3,468 states**:
**1,905 resolved / 1,483 missing / 11 ambiguous / 27 methodology-blocked /
42 not-comparable**. Capex is **167 resolved / 37 missing / 0 ambiguous**:
147 direct results + 20 curated approvals. Original 57 Capex gaps = 20 approved
+ 37 unapproved; controls are not blanket reviewed denials.

## Measures and version contract

The seventeen standardized measures are Revenue, Operating Income, Pretax,
income-tax expense, Reported ETR, D&A, Capex, diluted weighted-average shares,
cash/equivalents, short-term investments, long-term marketable securities,
commercial paper, short-term borrowings, current long-term debt, noncurrent
long-term debt, Operating NWC and ΔNWC. Supported means implemented with typed
outcomes, not necessarily resolved for every issuer. Separate reconstruction
details are not additional corpus measures.

| Contract | Frozen identity / extent |
| --- | --- |
| Standardized output | `SCHEMA_VERSION = "5"`; exact Decimal strings, ISO dates, deterministic serialization |
| Pretax curated | `pretax_scope_equivalence`, version `1`; eight MA/CVX entries |
| Operating Income derivation | `operating_income_component_derivation`, version `1`; 25 LLY/JNJ/MRK/KLAC/IBM entries |
| D&A curated | `d_and_a_scope_equivalence`, version `1`; five Visa entries |
| Capex curated | `capex_scope_equivalence`, immutable versions `1` (10 AMZN/LLY), `2` (5 CVX), `3` (5 Visa); disjoint additive catalog |
| Legacy D&A / ETR / shares derivations | `msft_annual_d_and_a_v1`, `annual_reported_effective_tax_rate_v1`, `googl_annual_diluted_weighted_average_shares_v1`; existing scoped behavior |
| NWC valuation | `meta_operating_nwc_valuation` v2 active/v1 retained; `cost_operating_nwc_valuation` v1; GOOGL/MSFT/AAPL corresponding v1 policies blocked; five active/six addressable versions |
| Generic/reconstruction policies | Exact source snapshot at the implementation reference above; no invented independent policy version. Five seed NWC reconstruction policies remain distinct from valuation readiness. |

Source modules and registries at that Git object fix generic policy ordering,
issuer-specific debt/AP treatment and all evidence schemas. This freeze does
not migrate those contracts or create a floating “latest” curated approval.

## Annual selection and provenance guarantees

Retain original selected 10-K accession, filing/report dates, CIK, actual fiscal
dates and source identity; no later comparative substitution, inferred zero,
calendar-year conversion or reconstructed predecessor history. Authoritative
annual resolution uses nondimensional DEI contexts, normalized entity identity
and semantically equivalent periods, preserving non-calendar/52–53-week dates.
Revenue/Pretax/income-tax use resolved authoritative start/end before ambiguity;
other generic duration policies retain their documented selected-accession and
report-end rules. This is **not** a claim that all generic duration policies
universally enforce DEI start dates. Curated entries require exact reviewed
annual identity; instant measures require their exact selected report date.
Annual structural errors remain errors, not fabricated financial states.

Curated acceptance requires registered CIK/accession/period, taxonomy/concept,
unit, reviewed scope and operand identity under its actual contract. Unregistered,
future or amended filings receive no implicit curated approval. Invalid,
incomplete, dimensioned, nil, non-USD or conflicting evidence cannot acquire
approval through labels or numerical agreement. Existing direct precedence and
conflict handling remain unchanged. Equal semantic occurrences may confirm one
operand; eligible economic differences remain ambiguous, not arbitrarily chosen.

Preserve direct/derived/calculated distinctions, formulas and ordered operands,
policy ID/version, source references, reviewed evidence and confirming occurrences.
Filing-XBRL occurrence identity/raw value/precision/context/unit and ordinals
remain available where implemented; Company Facts metadata is not augmented
with invented contexts. ETR retains supporting Pretax policy provenance.
Schema 5 preserves compact provenance, not every raw SEC graph. Mandatory
original-body/typed-digest checks apply where the reviewed D&A/Capex contracts
require them; do not assert universal raw-body checks for every generic fact.
Parsed JSON equality is not response-byte equality. NWC changes retain both
levels and require matching issuer, policy/version, formula, ordered perimeter
and actual dates; opening changes are not comparable, not zero.

## Frozen exclusions and valuation boundary

All missing/ambiguous/blocked/not-comparable states remain explicit. The eleven
Revenue conflicts, seed NWC methodology blocks, ancillary debt/investment gaps,
share-scale gaps, separately gated extensions and selected-filing comparability
limits persist. A research methodology blocker is not automatically a production
blocked state. No stable common-perimeter restated five-year series is promised.
Capex research is closed; exhausted issuer work requires its specified new
completeness evidence to reopen. Broader D&A, debt, shares, investments and sector
NWC improvements are deferred under the [exit plan](phase-1h-generalization-exit-plan.md).

The [timing-readiness design](financial-timing-readiness-design.md) remains a
proposed, not implemented, consumer contract. Five Visa D&A entries have expense
basis evidence; generic/MSFT basis remains insufficiently evidenced. **No
integrated FCFF bundle is certified**, including META/COST. Unknown compatibility
is not demonstrated incompatibility and does not revoke historical values.
Book-inventory timing, incentive effects and EBIT/D&A/NWC alignment require
evidence; no inventory allocation, residual adjustment or lease correction is
approved. The timing gate belongs **after this freeze, before FCFF consumption
and before forecast use of historical ratios**, not as universal historical
coverage certification. Manual assumptions do not bypass consumer consistency.

## Authoritative artifacts and digests

SHA-256 below describes exact committed UTF-8 file bytes (not SEC responses).

| Artifact | SHA-256 |
| --- | --- |
| [Frozen universe CSV](universe/sp500-top-50-2026-10-02.csv) | `acfb12f6b3d5ac051093a3b88e9aac30972fa6a4c114843e65e87815366bcbcc` |
| [Validation JSON](universe/phase-1h5-issuer-validation.json), `phase-1h5-historical-validation-v1` | `1d7b538fa757eef51ef1fcc9edeb42a9fef3cebdd8882a9caf7abd822b6ab089` |
| [Validation narrative](universe/phase-1h5-issuer-validation.md) | `f0be36b92de0a5b714524dafb3048c5abe5a40192c96ad55d2ce22361ae60e0d` |
| Original runner JSON bytes embedded losslessly in validation JSON | `3d12d3e8a8f2212e70c478a8c8f12fd35eb9f94a550b07ba04d07548092d2f3b` |

Runner representation is `original_runner_json_utf8_bytes`, digest type
`sha256_original_runner_json_bytes`, length 128,331 bytes; run timestamp
`2026-10-11T12:10:44.715513+00:00`. It reports pre-implementation-commit HEAD
`fc1feaa409ed7aa720cb7e030a4becdf9d71189a` and a dirty worktree, bound to
the validated implementation by [Wave 38 results](capex-visa-scope-evidence-results.md).
This is not a fresh clean-HEAD run. Documentation-only descendants preserve
behavior. Matrix readiness describes its prior validation stage and remains
unchanged; this document records the subsequent freeze. Exact accession/context
and SEC-artifact digests remain in linked policy registries/research evidence,
not synthesized from the compact corpus.

## Decision, validation and single next milestone

**Phase 1H complete with qualified historical scope.** Identity/classification,
policy/schema versions, retained corpus bytes, measure/state totals and local
references reconcile; `git diff --check` passes. No production, policy, schema,
inventory or test changes; no SEC request, tests or corpus rerun.

**Next Phase 2 milestone: implement the bounded financial timing-readiness
valuation boundary from the existing design**, with independent evidence/gate
results, conservative unknown/error handling and provenance/serialization tests.
No FCFF calculator or automatic economic adjustment in that milestone. Preserve
historical statuses and current unknowns; do not fabricate READY bundles. Phase
2A manual assumptions already exist. Later forecast-anchor/consumer-convention,
tax (including loss treatment), Capex and other valuation checks remain separate
prerequisites; passing this timing gate alone cannot certify FCFF/DCF readiness.
