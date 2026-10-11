# Phase 1H.4 generalization exit decision

Phase 1H.4 Wave 46; starting HEAD
`d8f6978c6bb79949b624ba3b34b106332d04b3be`. Documentation-only consolidation;
no production change, SEC request, test or corpus rerun.

**Proceed to Phase 1H.5 with documented exclusions. No further implementation
or issuer research is an essential prerequisite.** This is readiness to perform
validation, not a completed validation pass, supported-universe claim, historical
freeze or authorization to resume valuation.

## Criteria and essential work

The [Phase 1H roadmap](project-status.md#phase-1h-roadmap),
[universe boundary](architecture.md#universe-validation-boundary) and
[classification rule](universe/sp500-top-50-failure-taxonomy.md#issuer-level-post-smoke-classification)
require the frozen universe to remain fully represented, each constituent to
receive an evidence-backed support classification, and unresolved typed states
and exclusions to be documented. Phase 1H.6 subsequently records historical v1
supported scope and exclusions. They do not require every financial field to
resolve, specialized methodologies to be implemented, or universal integrated
FCFF readiness. The [timing contract](financial-timing-readiness-design.md)
belongs before future FCFF consumption, not as an extra historical-freeze gate.

The single next milestone is **Phase 1H.5 — S&P 500 Top 50 validation pass**:

1. Reconcile all 51 frozen security rows / 50 SEC issuers, including both Alphabet
   securities and all seven specialized exclusions, against retained evidence.
2. Reassess every issuer's expected history, material core-output gaps and
   provenance, assigning `SUPPORTED`, `GENERALIZATION_REQUIRED`, or
   `SPECIALIZED_METHODOLOGY_REQUIRED`. Map each security to its issuer decision.
   Do not promote issuers merely because the pipeline completed; the old
   post-smoke classifications are historical inputs, not refreshed certifications.
3. Publish current coverage, genuine ambiguities, missing/research states,
   methodology gates, opening-period non-comparability and selected-filing/history
   limitations. Cross-reference regression/evidence results for the approved
   policies. Reuse the validated corpus where adequate; any future validation
   execution is a separate milestone, not performed here. Resolve documentation
   inconsistencies, not economic gaps by invented values. If validation exposes
   a correctness/provenance defect, make only that defect a bounded prerequisite
   to freeze; no open-ended coverage target is introduced.

Only after that pass may Phase 1H.6 freeze historical normalization v1 with its
explicit supported scope. Forecast/FCFF/DCF remain paused until the freeze.

## Current production reconciliation

The [Wave 38 implementation results](capex-visa-scope-evidence-results.md)
establish the latest production baseline. Waves 39–46 are documentation only.
Counts below are carried forward and checked against the retained Wave 38 corpus
`/tmp/capex-wave38-corpus.json`, not newly measured or a new production approval.
Every row has 204 annual observations; columns are standardized states.

| Measure | Resolved | Missing | Ambiguous | Methodology-blocked | Not-comparable |
| --- | ---: | ---: | ---: | ---: | ---: |
| Revenue | 193 | 0 | 11 | 0 | 0 |
| Operating Income | 194 | 10 | 0 | 0 | 0 |
| Pretax Income | 167 | 37 | 0 | 0 | 0 |
| Income-tax expense | 204 | 0 | 0 | 0 | 0 |
| Reported ETR | 167 | 37 | 0 | 0 | 0 |
| D&A | 115 | 89 | 0 | 0 | 0 |
| Capex | 167 | 37 | 0 | 0 | 0 |
| Diluted weighted-average shares | 196 | 8 | 0 | 0 | 0 |
| Cash and cash equivalents | 185 | 19 | 0 | 0 | 0 |
| Short-term investments | 25 | 179 | 0 | 0 | 0 |
| Long-term marketable securities | 5 | 199 | 0 | 0 | 0 |
| Commercial paper | 12 | 192 | 0 | 0 | 0 |
| Short-term borrowings | 1 | 203 | 0 | 0 | 0 |
| Current portion of long-term debt | 116 | 88 | 0 | 0 | 0 |
| Noncurrent long-term debt | 140 | 64 | 0 | 0 | 0 |
| Operating NWC | 10 | 179 | 0 | 15 | 0 |
| Change in Operating NWC | 8 | 142 | 0 | 12 | 42 |
| **Total** | **1,905** | **1,483** | **11** | **27** | **42** |

204 × 17 = **3,468**; state columns sum to 3,468. **43 generic pipeline
completions, seven specialized skips**, zero execution failures. Forty-two
nonempty histories produce 204 periods: forty five-period histories plus GEV
and SNDK two each. XOM completes with zero history because the approved identity
boundary does not traverse the predecessor; this is not five-year coverage.
The 42 opening ΔNWC states are `NOT_COMPARABLE`, not missing or expected zero.
Research-level methodology blockers do not change production missing states:
the 27 production methodology-blocked outputs remain seed O-NWC/ΔNWC gates.

## Measure-family decision matrix

| Family / unresolved scope | Completed work and durable boundary | Required for validation/freeze | Deferred work / promising bounded option |
| --- | --- | --- | --- |
| Revenue: 11 genuine conflicts; taxes: 204 resolved | DEI annual association implemented; WMT/MA/CVX full-year economic conflicts remain | Retain competing evidence and ambiguity; no arbitrary precedence or value selection | Reopen only with new semantic distinction; no pending annual/Q4 fix |
| Pretax / ETR: 37 missing each | Eight MA/CVX acceptances; 25 variant controls plus 12 ORCL/MCD/PG extension periods unapproved; 20 separate-net-of-tax and five mixed cases preserve scope | Preserve exact registries and downstream provenance; classify denominator-driven ETR gaps | No generic variant fallback; extension/mixed scope work needs new evidence |
| Operating Income: ten CVX/GE gaps | 25 exact component derivations implemented; CVX affiliate perimeter and GE mixed-business/separation research NO-GO | Carry explicit operating perimeter limits; do not manufacture EBIT | Separate methodology only; no recurring research sequence or pretax residual |
| D&A: 89 missing | Five Visa scope approvals; 33 component proposals: 0 approved, 19 further research, 14 methodology-gated; TXN timing/incentive gaps remain; AMD extensions gated | Preserve historical values and approvals; disclose generic/MSFT insufficient basis proof and unproved joint FCFF compatibility | New exact component/timing evidence only; implement timing readiness at valuation boundary, not before 1H.5 |
| Capex: 37 missing | Current research pass closed: original 57 = 20 curated approvals + 37 unapproved; no additional complete cash equation | Preserve 147 direct + 20 curated results, typed failures and policy versions; no blanket control denial | No exhausted issuer reopening without specified new cash-scope evidence; no generic productive-assets fallback |
| Cash: 19 missing; investments: 179/199 missing | Cash policy generalized to 185 results; broad/restricted captions and investment class perimeters remain unsupported | Separate cash, restricted cash and investments; absence is not zero | Investment current/noncurrent scope research is optional future equity-bridge backlog |
| Debt: current/noncurrent 88/64 missing; CP/short borrowing 192/203 missing | Widespread standard variants combine lease principal, current maturities or totals; 57 current-debt periods have multiple families | Disclose carrying-value/lease/overlap limits; no inferred absence or total-debt residual | Promising reusable option: one bounded exact-filing inventory/design for `DebtCurrent`, preserving disjoint CP/borrowing/lease/current-maturity boundaries. Not a prerequisite; no acceptance yet |
| Shares: eight missing | Visa five selected Company Facts gaps; MCD three floating/scale-basis gaps; existing GOOGL derivations preserved | Distinguish weighted-average history from future point-in-time denominator; retain invalid/missing scale states | Optional bounded selected-filing scale/unit evidence review for the eight identities; no inferred multiplier |
| NWC / ΔNWC: 179/142 missing, 15/12 blocked | META/COST ten levels/eight changes; GOOGL/MSFT/AAPL blocked; other issuer perimeters not approved; book-inventory timing audit completed | Record policy absence, seed methodology limits and all 42 opening non-comparable periods; no residual universal formula | Sector-clustered component policy design is broader coverage backlog; integrated EBIT/D&A/book-inventory consistency requires future consumer evidence |
| History / specialized scope | Strict CIK/schema repairs complete; XOM succession NO-GO; GEV/SNDK two-period histories; seven specialized skips explicit | Preserve all constituents, limited histories and specialized classifications; no false supported status | Generic legally evidenced succession parser only with new directed continuity evidence; no hardcoded XOM link, predecessor reconstruction or specialized model implementation |

## Capex closure and explicit limitations

[GE final research](capex-ge-perimeter.md) closes the bounded remaining-issuer
pass. The 37 controls reconcile as follows, without changing the frozen inventory:

- 17 concept/scope gaps: HD 5, QCOM 5, PEP 5, MRK 2.
- 17 component gaps: NVDA 5, LRCX 5, VZ 5, GEV 2; extensions remain separately gated.
- Three business/asset methodology gates: GE 3.

Twenty implemented approvals are AMZN/LLY 10, CVX 5 and Visa 5. Direct results
are outside the original 57-gap inventory. No residual or absent component is
zero, no book balance becomes purchase cash, and no standalone industrial value
is forced from mixed consolidated scope. Reopening triggers are documented in
the issuer supplements; no new safe potential coverage is promised here.

`EXPECTED_TYPED_MISSING` still requires affirmative absence/non-applicability
evidence. Do not rename all 1,483 missing states as expected exclusions. Unknown
FCFF compatibility is not proven incompatibility, and does not revoke resolved
historical values. The old two-supported/41-generalization/seven-specialized
post-smoke planning distribution must be reassessed in Phase 1H.5, not silently
carried forward as the final support decision.

## Decision and validation

No remaining evidence-backed, already-approved implementation is waiting on
this consolidation. The optional high-frequency debt and share-scale options
are bounded deferred backlog, not mandatory exit criteria. The research blockers
are explicit and conservative; further broad research is not justified simply
to improve coverage. **Proceed to Phase 1H.5; no essential pre-validation work.**

Validation checks all 17 measure rows, aggregate/period/execution counts, frozen
Capex 57/20/37 and 17/17/3 partitions, current source-result references, roadmap
consistency and local links. `git diff --check` passes. Source, policies, schemas,
tests, frozen inventories and production remain unchanged; no tests/corpus rerun.
