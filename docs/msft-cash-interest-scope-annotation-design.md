# MSFT cash-interest scope annotation design

## Decision and preservation boundary

**GO for an isolated, nonnumeric annotation sidecar for only FY2025–2026.**
This is a Phase 1 historical-data preparation design, not implemented behavior.
The [completed cash-interest review](msft-alternative-historical-cash-flow-inputs.md#cash-interest-completeness-review)
is the evidence authority. It supports separately reported inputs, not complete
all-in cash interest. No further broad issuer research is scheduled.

Preserve the [immutable registry](company-data-preparation/msft-reported-cash-flow-bundles.json),
bundle identities/version, values, roles, signs, precision, original evidence,
unknowns and `reported-cash-flow-input-bundle-v1` serialization byte contract.
Do not replace the existing `location_and_scope` text with a refined annotation.
Sidecars supplement its conservative warning with reviewed evidence; they are
not overrides. Preserve frozen historical schema 5, NWC blockers/partial bundles
and false completeness/valuation-consumption flags. No total, adjusted formula,
tax shield, estimate, inferred zero or forecast/valuation consumer is defined.

## Exact registrations and evidence binding

Proposed contract ID `reviewed-msft-cash-interest-scope-annotations`, contract
version string `1`; separate schema `cash-interest-scope-annotations-v1`.
Only these two explicit registrations; no ticker fallback or period inference:

| Annotation set ID | Parent bundle ID / version | CIK / form / selected accession | Authoritative annual period |
| --- | --- | --- | --- |
| msft-cash-interest-scope-fy2025 | msft-reported-cash-flow-fy2025 / 1 | 789019 / 10-K / 0000950170-25-100235 | 2024-07-01–2025-06-30 |
| msft-cash-interest-scope-fy2026 | msft-reported-cash-flow-fy2026 / 1 | 789019 / 10-K / 0001193125-26-323660 | 2025-07-01–2026-06-30 |

Pin parent registry SHA-256
`c3c35e020066f0887d9d8fe493f975afe9e6f0ea4b1785d2f341691ebb49d993`;
inventory `ef68344fe6d523cb55f5478eb03045fa984f067e07b2b37e6687011cd5a4d1b6`;
original-body manifest `8b7dd48e6408fb84af1493acfba3136d4a7671fc8bb1147c339015da80990542`.
These are hashes of the referenced local file bytes, **not** SEC-body digests.
The [evidence identity table](msft-alternative-historical-cash-flow-inputs.md#frozen-identities-and-retained-evidence)
supplies four original-body digests/URLs and all namespace/context conventions.
Reuse those bodies and retrieval receipts, not a parsed/reserialized substitute.

Each input reference must bind parent ID/version/period, exact input ID and
QName, kind, raw Decimal point as a string, display multiplier, submitted
decimals, and the **entire ordered occurrence tuple**. Include instance artifact
URL/accession/representation/digest type/digest, each context/entity/start/end,
dimensions, unit ID/normalized unit, raw value, decimals, nil status and ordinal.
Verify exact equality against the parent registry and original instance;
an ordinal, concept name or equal numeric point alone is not identity.
Retain every confirmation in source order; do not add their values.

Each assertion also has a reviewed evidence reference: exact primary artifact
identity/receipt plus note/section and a short verbatim locator, and where
available the instance text-block QName/context/root-child ordinal. The review
author/date, classification rationale and research-document section are required.
Locator text must be present in a specified deterministic visible-text extraction
(HTML parser text nodes, whitespace collapsed); record extraction algorithm
version and occurrence selector if repeated. The digest always covers original
response bytes, not extracted text. Validation must verify locators against the
pinned body and exact reviewed assertion, not merely find the phrase somewhere.
No new SEC retrieval is needed for these registrations.

## Reviewed input mapping and precision

The following **eleven existing input IDs per set** receive annotations; all are
nondimensional, non-nil exact-USD annual facts. Points are USD millions; ordinals
are zero-based instance root-child positions. `-8` preserves reported rounding
to 100m; `-6` preserves rounding to 1m. Exact Decimal storage is not economically
exact measurement. No intervals, rounding allocations or added tolerances.

| Parent input ID | FY2025 point / decimals / ordinal | FY2026 point / decimals / ordinal | Annotation scope and recognition basis |
| --- | --- | --- | --- |
| InterestPaid | 1600 / -8 / 1643 | 1500 / -8 / 1651 | Note 10 debt-interest cash payment; neither all-in nor a certified gross/net-capitalization amount. |
| FinanceLeaseInterestPaymentOnLiability | 1372 / -6 / 1854 | 2547 / -6 / 1891 | Note 13 finance-lease liability-measurement cash, reported operating cash flow; separate from debt cash and principal. |
| InterestExpenseNonoperating | 2385 / -6 / 896 | 3051 / -6 / 907 | Note 3 recognized accrued aggregate; Item 7 establishes finance-lease effects and reduction from debt-interest capitalization, not their amounts. |
| FinanceLeaseInterestExpense | 1417 / -6 / 1844 | 2547 / -6 / 1881 | Note 13 finance-lease interest cost; not cash, not a proved full profit/loss allocation or second addition to aggregate expense. |
| OperatingLeasePayments | 4931 / -6 / 1851 | 6443 / -6 / 1888 | Note 13 whole operating-lease liability-measurement cash; no reported interest split or all-variable/non-lease completeness. |
| OperatingLeaseCost | 5524 / -6 / 1838 | 6968 / -6 / 1875 | Note 13 accrued single lease cost, not separate interest cash. Note 1 equipment lease/non-lease exceptions retained. |
| FinanceLeasePrincipalPayments | 2283 / -6 / 1857 | 3101 / -6 / 1894 | Note 13 financing cash principal; not interest. |
| FinanceLeaseRightOfUseAssetAmortization | 3408 / -6 / 1841 | 5403 / -6 / 1878 | Note 13 noncash amortization; not interest cash. |
| FinanceLeaseCost | 4825 / -6 / 1847 | 7950 / -6 / 1884 | Issuer-extension total lease cost; includes amortization and interest; not another operand. |
| RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability | 7826 / -6 / 1860 | 4555 / -6 / 1897 | Noncash asset/liability addition, not paid interest. |
| RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability | 20511 / -6 / 1863 | 24608 / -6 / 1900 | Noncash asset/liability addition, not paid interest. |

Cash payment multipliers remain `-1`; expense/cost/noncash rows remain `+1`.
`FinanceLeaseCost` uses each exact Microsoft namespace; the other ten use the
selected US-GAAP namespace. No extension gains normalization approval here.

Assertion evidence: Notes 1/10/13 use verified text-block ordinals
831/1503/1831 (FY2025), 838/1516/1868 (FY2026), with exact selected annual
contexts. Note 3's numeric occurrence and Item 7 *Other Income (Expense), Net*
paragraph beginning “Interest expense decreased primarily” / “Interest expense
increased primarily” establish aggregate-expense effects. Full locator passages
and conclusions remain in the review; the new implementation must freeze them
in its own reviewed annotation registry, not rely on a mutable prose link alone.

Tax-position interest is **research-only evidence**, not a nonexistent parent
input reference. Note 12 text blocks 1654/1662: annual
`UnrecognizedTaxBenefitsIncomeTaxPenaltiesAndInterestExpense` 1300m/1400m,
`decimals=-8`, ordinals 1786/1820; closing-instant
`UnrecognizedTaxBenefitsIncomeTaxPenaltiesAndInterestAccrued` 8200m/9400m,
`-8`, ordinals 1783/1817. Use the original closing contexts, not annualized stock.
Note captions narrow the generic combined tag to tax-position interest net of
tax benefits. Bind these as evidence occurrences, never new bundle amounts,
debt/lease cash or an inferred tax-interest payment.

## Models, assertions and explicit unknowns

Reuse immutable `Period`, `Artifact`, `Receipt` and `Occurrence` from the
[reported-input models](../src/valuation_platform/analyst/cash_flow_inputs.py)
where applicable, without modifying shared models. New immutable sidecar models
should contain: set identity/version, exact parent binding, review metadata,
ordered input annotations, ordered evidence references, relations, granular
unknowns and fixed limitations. A binding is a reference plus verification
snapshot, never a replacement `ReportedInput` or numerical scenario.

Use separate concepts of **assertion state** (`evidence_supported`,
`unresolved_scope`, `unavailable_disclosure`) and **attachment validation state**
(`validated`, `not_provided`, `invalid`, `conflicting`). Unknown compatibility
is not demonstrated incompatibility. An invalid attachment is not a financial
zero or proof the parent input is invalid.

An assertion has a stable key, typed subject (existing reported input, existing
bundle unknown, or explicitly research-only evidence), controlled claim,
assertion state, rationale and evidence references. All subjects must resolve;
no free-form input aliases. Evidence-backed scope labels are analyst
classifications of SEC facts, not new reported facts or numerical estimates.
Unknown records have stable issue IDs, affected subject references, reason,
evidence/search boundary and reopening requirement; their numeric value is
always null, never a missing-key default. Bind the following **ten issues per
set** to parent unknown `all_in_cash_interest` and the affected inputs:

| Issue ID | State / preserved unknown |
| --- | --- |
| debt_lease_cash_overlap | unresolved_scope: distinct disclosed populations, no certified numerical mutual-exclusion reconciliation. |
| capitalized_interest_expense_amount | unavailable_disclosure: capitalization is evidenced; amount not quantified. |
| capitalized_interest_cash_amount | unavailable_disclosure: no quantified paid/capitalized allocation or cash-flow placement bridge. |
| debt_cash_capitalization_basis | unresolved_scope: Note 10 gross/net or inclusion/exclusion basis not stated. |
| finance_lease_cash_capitalization_basis | unresolved_scope: lease cash gross/net capitalization basis not stated. |
| operating_lease_interest_cash_split | unavailable_disclosure: no annual cash split, not inferable from rates, maturity discounts or balances. |
| tax_position_interest_cash | unavailable_disclosure: expense/accrual net of tax benefits is not cash. |
| interest_expense_accrual_noncash_cash_bridge | unavailable_disclosure: no complete expense, capitalization, payable, amortization and cash bridge. |
| borrowing_hedge_cash_coverage | unresolved_scope: commercial-paper/coupon/hedge cash allocations and all-borrowing coverage not established. |
| finance_lease_cost_profit_loss_allocation | unresolved_scope: cost-to-recognized-aggregate allocation is unquantified, despite evidenced lease-related effects. |

Required relations: debt cash versus lease cash `overlap_unquantified`; aggregate
expense versus lease cost `lease_effect_evidenced_full_allocation_unknown`;
lease interest cash versus cost `different_recognition_bases`; total lease cost
versus its interest/amortization disclosures `reported_component_relationship`.
Relations retain endpoints and evidence, **no coefficient, summation operator,
allocation or cash residual**. Equal FY2026 cash/cost points cannot change these
states. Reported cost arithmetic stays in the parent review, not a new sidecar
calculator. `all_in_cash_interest` remains null/unresolved in the parent.

Every validated set must carry fixed `certified_interest_total=false`,
`summation_authorized=false`, `valuation_consumption_approved=false`, and
`is_complete_operating_nwc=false`. These are prohibitions, not readiness scores.
No true state or numeric total exists in contract version 1.

## Versioning, serialization and conservative behavior

Contract/schema version and per-set registration version are separate from
parent bundle version; both new versions start at string `1`. The future
annotation registry is independently byte-pinned. Review changes require a new
immutable version with explicit predecessor identity/reason; retain earlier
versions, never edit pinned parent/sidecar bytes. No automatic latest-version
selection, migration, future/amended approval or cross-period reuse. A different
parent version needs separate review, not a relaxed digest check.

Separate serialization envelope carries schema/contract/version, annotation
registry SHA-256, parent ID/version/registry digest/exact period, review metadata,
ordered assertions/relations/unknowns, evidence locators/receipts and fixed flags.
Use deterministic registry order, sorted object keys, Decimal strings and ISO
dates; retain raw values/signs/decimals and every occurrence representation.
Reference the separately verified parent artifact bodies once by exact identity;
do not embed/rewrite its bundle serialization. Research-only occurrences point
to those same verified bodies. Detached JSON without the parent and required
body evidence is unverified, never usable as a validated sidecar.

Deserialization requires the verified parent plus original bodies, rechecks the
exact reviewed registry, binding snapshots, receipts, source locators and all
assertions/unknowns/relations/flags, and then rebuilds the sidecar. Reject extra
or missing fields, duplicate JSON keys, bool/int confusion, unsupported versions,
duplicate set/assertion/issue identities and unauthorized numeric fields.
No last-write-wins, fuzzy text matching, hash relabeling or silent field repair.

Missing attachment yields `not_provided`: the existing bundle remains usable
only within its existing reported-input boundary; do not create approved default
annotations. Missing mandatory evidence/unknowns or mismatched accession,
period, entity, namespace, unit, decimals, source occurrence or digest yields
`invalid`, with no validated annotation set. Conflicting reviewed assertions or
two supplied versions without explicit selection yield `conflicting`, retaining
both identities and reasons in diagnostics; do not merge, select by arrival
order or downgrade to valid. No validated subset of a failed set. These failures
must not alter parent resolution, remove NWC blockers or authorize combination.

## Validation plan and present design checks

Implementation tests must cover: exact two registrations; all 22 input mappings
and 20 unknown records; note/Item 7 evidence and four research-only tax
occurrences; original-byte/metadata mismatch; wrong input/parent/version/QName,
annual versus instant period, dimensions/nil/non-USD and lost confirmations;
changed rounding/sign/role; cost/cash equality without collapse; missing,
duplicate and conflicting assertions/versions; tax stock never cash; no synthetic
capitalized amount/overlap zero/interval; separate serialization round-trip and
unverified detached payload; missing annotations preserve parent behavior;
attempted true certification/sum flags rejected. Parent registry/model/schema
and both original serialized bundle outputs must remain unchanged.

This documentation milestone checks two frozen identities, input points/roles,
signs/precision/ordinals, namespace/context/unit bindings, pinned file digests
and original-body evidence references, ten issue IDs, version consistency and
local links. No executable model/registry/schema was added. No SEC requests,
tests or corpus rerun; frozen **1905/1483/11/27/42 = 3468** remains unchanged.

## Finite blocker disposition and next milestone

| Blocker family | What retained evidence resolves | What remains / closure route |
| --- | --- | --- |
| Reported data identity and packaging | CFO, cash PP&E, debt/lease cash, taxes, SBC and reconciliation roles/precision; both reported CFO bridges and original provenance. | Implement this sidecar once; no repeated data-discovery cycle. |
| Interest scope | Debt versus lease captions, cash versus cost, noncash/principal distinctions, positive capitalization/lease-expense effects, tax-scoped expense. | Complete cash overlap/capitalization/gross-net/operating-split/cash bridge needs explicit new disclosure. An analyst can choose a limited scope, not certify missing issuer facts. |
| Mixed NWC / accrual PP&E | Two reviewed partial levels, capital-creditor exclusion and 19.8bn movement effect. | Missing operating allocations and acquisition/FX/timing bridges are not in retained evidence; retain blockers. Reported CFO bypasses reconstruction, not certification. |
| Cash-tax, SBC and lease economics | Separate reported facts and classifications, not an approved adjusted treatment. | Analyst decisions on desired perimeter/SBC cost-versus-dilution/lease treatment require explicit authority and rationale; missing allocations remain unknown. No decisions or amounts approved here. |
| Acquisition/intangible/other investing and organic cash | Reported combined spending and consolidated scope; selected versus recast reconciliation distinguished. | Complete separation, continuing-only and component acquisition/FX/reclassification allocations require additional disclosure; assumptions would be labeled alternatives, never reported facts. |
| Joint timing readiness | Existing D&A/EBIT/NWC limitations and reported cash scope are documented. | Integrated compatibility is unproved; retained numerical agreement cannot certify it. Future use requires the separate timing contract and explicit analyst decisions. |

**Single next Phase 1 milestone:** implement this isolated two-set annotation
contract and focused binding/serialization/preservation tests, with no new totals,
research or numeric inputs. That closes the current packaging sequence. After
implementation, report the remaining finite blocker ledger for user disposition
(accept explicitly limited data, authorize specific analyst judgments, or hold
for unavailable disclosure); do not automatically launch another annotation or
issuer-research milestone. Phase 2 stays postponed.
