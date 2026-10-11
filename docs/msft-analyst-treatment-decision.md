# MSFT analyst-input treatment decision memo

2026-10-12; starting HEAD `f3e67e6db5b306bc0283af1a04d138266fd0bb02`.
Original recommendations below were proposed for review. **Subsequent user
acceptance, 2026-10-12:** SBC recognized-expense cost proxy counted once,
consolidated reported CFO reference, separate narrow cash PP&E and reported cash
taxes are accepted for the limited historical-input scope. Lease cash-service is
accepted in principle; subsequent acceptance of the precise restricted reported
dataset permits historical preparation only. Future modeling applicability
remains unapproved. No tax rate, calculation or consumption approval is granted.
The [two-period acceptance checklist](msft-treatment-acceptance-checklist.md)
is authoritative for current statuses; the options below preserve the original
decision rationale, not new executable policy.
The user authorized designing an additional analyst path, not performing its
economic adjustments. Phase 2 remains postponed. Preserve the reported-only
baseline, frozen-v1 outputs/blockers, NWC scenarios, cash-flow bundles and sidecars.

## Recommended path and permitted use

Use the two selected consolidated cash-flow histories as an **analyst historical
cash-input profile**, with separately identified compensation-cost proxy, lease
service/financing classifications and an unpopulated operating-tax assumption.
This is more practical than requiring complete book-NWC reconstruction. It is
not an alternative approved FCFF formula, complete cash-interest number, organic
cash series or certification of operating-only cash. No adjusted subtotal,
interest sum, tax shield, forecast assumption value or valuation is calculated.

Permitted now: review source facts, compare reported scope, record proposed
classifications/proxy sources and identify unknown inputs. Subsequent numerical
analyst treatments require explicit acceptance and a separate authorized contract.
No recommendation here toggles a blocker, changes a primitive, overrides a pinned
bundle or authorizes a forecast consumer.

### Exact evidence boundary

CIK 789019; FY2025 accession `0000950170-25-100235`,
2024-07-01–2025-06-30; FY2026 `0001193125-26-323660`,
2025-07-01–2026-06-30. Only the two immutable version-1
[reported bundles](company-data-preparation/msft-reported-cash-flow-bundles.json)
and [cash-interest sidecars](company-data-preparation/msft-cash-interest-annotations.json).
The [evidence matrix](msft-alternative-historical-cash-flow-inputs.md#input-and-scope-matrix)
supplies exact QNames/occurrences, contexts/units/signs, submitted precision and
SEC URLs. The [original-byte identity table](msft-alternative-historical-cash-flow-inputs.md#frozen-identities-and-retained-evidence)
and [retained manifest](evidence/analyst-operating-nwc-response-bodies.json)
retain primary/instance bodies, typed hashes and retrieval receipts. No new SEC
request, later comparative substitution, amendment or period extension.

Selected facts used here, USD millions (not new analyst amounts):

| Input | FY2025 | FY2026 | Scope / precision |
| --- | ---: | ---: | --- |
| Reported CFO | 136162 | 182935 | Consolidated reported subtotal; decimals -6. |
| SBC expense / cash-flow add-back | 11974 | 12405 | Same economic observation under two concepts; -6; count once, not twice. |
| Cash PP&E purchases | 64551 | 115948 | Investing payment magnitude; -6; not all investment. |
| Debt-interest cash | 1600 | 1500 | Note 10 debt-scoped, -8; gross/net capitalization and coverage unknown. |
| Finance-lease interest cash / principal | 1372 / 2283 | 2547 / 3101 | Operating / financing cash disclosures respectively; -6; not summed here. |
| Cash taxes net of refunds / tax provision | 28700 / 21795 | 21188 / 32185 | Cash taxes -8 / -6 respectively; provisions -6; distinct bases. |
| Acquisition/intangible/other purchases | 5978 | 1743 | Combined investing outflow, -6; no acquisition-only allocation. |

Exact Decimal points do not remove reporting rounding. Other lease/tax/noncash
inputs and all ten interest unknowns per period remain in the linked evidence.

## Five decisions, recommendations and blocking conditions

### 1. SBC — compensation cost once

**Known / unavailable:** recognized expense and CFO add-back are 11974m/12405m;
Note 14 allocation confirms expense, not another cost. Withholding cash and
recognized tax benefits are separate facts. Expense is not an observed cash
replacement wage, current grant market value or complete outstanding-award claim.

**Options:** retain unadjusted reported CFO; treat recognized SBC expense as an
analyst proxy for annual economic compensation cost; or use a separate award/
dilution model, requiring additional claim and share information. Damodaran's
[course discussion, March 12](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/eqemailSpr25.html)
treats SBC as an expense despite its noncash form; his
[management-options discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/mgtoption.htm)
distinguishes outstanding option claims from simple share-count dilution.

**Recommend:** an explicitly labeled **recognized-expense economic-cost proxy**,
using the same annual SBC fact once. A future cash-based analyst path would
neutralize the CFO add-back once; an income-based path already charging SBC
would not deduct it again. No adjustment is performed now. Do not also charge
buybacks, withholding or future dilution for the *same* compensation cost.
Existing outstanding award claims are a separate population: this recommendation
does not waive them or authorize ignoring an eventual equity/share adjustment.

**Inputs / acceptance / limits:** exact `ShareBasedCompensation` and
`AllocatedShareBasedCompensationExpense` identities, role linkage, -6 precision,
reviewer/date and an explicit acceptance that expense is a proxy, not cash.
Record the chosen basis and exclusion of duplicate treatments. User must accept
the proxy before numerical use; actual grant/settlement differences remain
unquantified. Outstanding claims remain a later valuation-boundary requirement.

### 2. Leases and interest — proposed cash-service perimeter

**Known / unavailable:** Note 13 separates operating payments, finance interest,
finance principal and noncash additions; Item 7 evidences finance-lease effects
and debt-interest capitalization in recognized interest expense. Cash overlap,
capitalized amounts/gross-net basis and operating-lease interest split remain
unproved. [FASB's lease taxonomy guidance](https://xbrl.fasb.org/impguidance/LE_TIG/inline_f2017leasesig.htm)
distinguishes the cash categories; it is tagging guidance, not issuer completeness
proof. The selected notes, not generic tag names, govern the actual facts.

**Options:** retain reported GAAP cash classification; classify all leases as
financing, requiring consistent leased-asset, debt and tax treatment; or use an
explicit cash-service convention for the analyst path. Damodaran's
[lease analysis](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/oplease.htm)
shows that recategorization affects multiple income/investment/debt inputs;
isolated adjustments are not consistent. Its legacy off-balance-sheet examples
are not current ASC 842 rules or MSFT evidence.

**Recommend:** **cash-service treatment for both lease classes in this limited
analyst profile**, an analyst policy choice, not GAAP recategorization. Keep
operating-lease cash and finance-lease interest already inside CFO; identify
finance principal separately as an additional service-payment candidate for a
later authorized analyst calculation. Do not add interest twice, invent an
operating-lease interest split or treat noncash ROU additions as cash purchases.
Under that proposed convention, the same lease obligations must not also be
charged as financing debt in a later equity bridge; reported liabilities are
still retained. A financing convention remains a valid alternative but must
replace the whole treatment consistently, not mix with this proposal.

**Inputs / acceptance / limits:** user acceptance of cash-service scope and its
principal-payment timing, linked Note 13 inputs/receipts and the immutable
interest sidecar. Service treatment does not prove recurring lease cash or full
variable/non-lease coverage. Borrowing interest stays a separate rounded
debt-scoped disclosure, **not an approved all-in proxy or total**. Unknown cash
overlap/capitalization still blocks any attempted unlevering or interest tax
shield; it need not block a clearly financing-affected historical input profile.

### 3. Taxes — reported cash versus a separate analyst rate

**Known / unavailable:** cash paid net of refunds, provision, deferred adjustment,
SBC tax benefit and uncertain-tax-position interest are distinct. No complete
operating-only cash allocation, marginal operating burden or interest-tax bridge
is established. Provision divided by pretax is not automatically an operating
tax rate; recognized SBC benefit is not cash tax relief.

**Options:** retain actual consolidated cash taxes for historical cash inputs;
use reported ETR as a labeled provisional proxy; or select a normalized operating
tax-rate assumption using reviewed jurisdiction exposure and reconciliation.
Damodaran's [tax-rate discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/taxrate.htm)
distinguishes effective/marginal rates and multinational exposure. Its historical
statutory percentages are obsolete: none is imported into this memo.

**Recommend:** retain cash taxes already reflected in CFO for the historical
profile; reserve a **separate, explicitly selected normalized operating-tax-rate
assumption**, with jurisdiction/reconciliation rationale, for an independently
authorized operating-income basis. Prefer an evidenced operating/jurisdiction
basis over blindly importing reported ETR; a supplied ETR proxy would need an
explicit limitation. No rate is populated, inferred from cash taxes or defaulted.
This recommendation is not a forecast schedule or tax assumption engine.

**Inputs / acceptance / limits:** user supplies/accepts rate, basis, applicable
period, source date, jurisdictions/weighting or proxy rationale, exceptional-item
exclusions and uncertainty. A future contract must choose one tax basis, not tax
already-after-tax CFO again or combine reported cash taxes with an assumed
operating tax without a supported replacement bridge. Absent that bridge,
normalized after-tax economic use remains blocked, though reported cash inputs
remain usable for review. No tax shield is approved.

### 4. NWC, acquisitions, FX and timing — use cash history, not book residuals

**Known / unavailable:** CFO reconciles reported income and operating changes;
partial book NWC and the 19.8bn capital-creditor movement effect have narrower
meanings. Acquisition/FX/noncash allocations and complete operating book scope
remain unavailable. FY2026 recasts two FY2025 adjustment lines, not its CFO total.

**Options:** reconstruct complete NWC (needs missing allocations); select a
narrow book scenario (already available but partial); or use reported CFO as
the historical cash-input basis. **Recommend the reported-CFO basis** for this
additional path. Complete opening book NWC, PP&E-in-AP correction and inventory
D&A allocations become unnecessary *for reproducing that reported subtotal*.
Do not subtract partial ΔNWC or add D&A/SBC again. The SBC cost proxy above is
a separately proposed economic treatment, not another reported add-back.

**Inputs / acceptance / limits:** accept consolidated, acquisition-affected
reported history rather than organic or constant-currency history. Keep both
selected accessions, their CFO reconciliation and recast links; do not overwrite
FY2025 or trend-extrapolate reclassified adjustment components. Acquisition/FX/
continuing-scope effects still matter for trend interpretation, recurring/organic
claims and any later consumer. The cash FX reconciliation is not an operating
FX allocation. Damodaran's [acquisition guidance](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/acqcapex.htm)
requires consistency between acquisition investment and growth treatment.

The [timing-readiness contract](financial-timing-readiness-design.md) remains
mandatory at future consumption. Book-NWC/expense-D&A gates are not magically
passed by switching paths: a future approved consumer must state which gates
are inapplicable under its cash basis and prove the alternative cash-scope,
tax/lease/investment consistency. No new readiness state or waiver is approved.

### 5. Cash investment — narrow PP&E evidence, incomplete total reinvestment

**Known / unavailable:** reported cash PP&E is supported; capital creditors and
ROU additions are not current cash spending. Combined acquisition/intangible/
other purchases and net other investing are not fully separated. PP&E cash is
not proof that all operational software/intangible investment is captured.

**Options:** retain a narrowly named cash-PP&E input; claim the combined line is
all organic reinvestment (unsupported); or obtain separate cash/scope evidence.
**Recommend cash PP&E as the evidenced owned-asset input, with the combined and
other-investing amounts held separately as unallocated inputs.** This does not
change the existing Capex primitive or normalize undisclosed categories to zero.
No subtraction from CFO, lease-plus-Capex subtotal or residual allocation here.

**Inputs / acceptance / limits:** accept the narrow cash-purchase scope; keep
exact investment occurrences/signs and noncash/creditor exclusions. Lease cash
follows the proposed service convention, not PP&E addition arithmetic. An organic
investment claim requires explicit acquisition-versus-operational-intangible
cash separation and non-overlap evidence. Without it, broad reinvestment and
organic-growth use remains blocked. Choosing an acquisition-excluding scope
cannot retain acquisition-driven growth benefits by assumption.

## Acceptance, stopping point and smallest next Phase 1 milestone

The subsequent user approval supersedes the blanket proposed-pending-review
status, only as specified in the [acceptance checklist](msft-treatment-acceptance-checklist.md).
These are prose decisions, not registered policy IDs or executable enums.
Facts remain SEC-reported; scope selection is analyst classification; SBC
expense-as-economic-cost is an accepted labeled proxy, not cash evidence;
tax rate remains a missing analyst input. Unknown disclosures stay null.
No confidence/materiality threshold manufactures approval.

User choices: accept/reject the SBC proxy; lease cash-service versus whole
financing convention; consolidated cash-history scope versus a specifically
authorized organic alternative; narrow PP&E scope; and the tax-assumption basis
(a number is not required to approve the design, but is required before its use).
Record acceptance author/date, exact two periods, chosen treatment/version,
evidence references, proxy limitations, unpopulated required inputs and permitted
use. Any override retains the prior decision, never changes the pinned baseline.

The then-next acceptance checklist and restricted reported-dataset decision are
now completed: user acceptance 2026-10-12 permits separate historical preparation
only, not totals, adjustments or valuation consumption. All coverage/overlap
unknowns and future modeling restrictions persist. No further lease research,
new calculator,
annotation cycle, broad SEC search or automatic blocker removal. The pilot is
closed only for two-period historical input preparation, not completeness or
future consumer readiness. Only later explicit authorization can implement
calculations; Phase 2 remains postponed.

Validation: frozen identities/input points/precision and bundle/sidecar evidence
references checked against retained registries and original-body metadata;
recommendations checked for cash/accrual distinctions, non-overlap and readiness
limitations; primary methodological references reviewed, local links/diff check
pass. No SEC requests, tests or corpus rerun, source/schema/policy/evidence edits.
Frozen production **1905/1483/11/27/42 = 3468** is carried forward unchanged.
