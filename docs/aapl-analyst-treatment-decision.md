# AAPL FY2025 analyst-input treatment decision memo

2026-10-12; starting HEAD `93a294d2cf5697c233e9997c0f517ec20e71ecb2`.
Original recommendations below were proposed for review. **Subsequent user
acceptance, 2026-10-12:** the [FY2025 acceptance checklist](aapl-treatment-acceptance-checklist.md)
records consolidated CFO/narrow PP&E, SBC expense cost proxy once, reported cash
taxes and restricted rounded fixed-lease dataset acceptance. Cash interest and
investment allocations stay unknown; no future tax basis/rate or valuation
consumption is approved. The original options/rationale remain below. This is a bounded
Phase 1 decision memo, not an economic calculation, policy implementation or
valuation-consumption approval. MSFT acceptance is not AAPL acceptance.

## Evidence and permitted-use boundary

Only CIK `0000320193`, selected non-amended 10-K `0000320193-25-000079`,
FY **2024-09-29–2025-09-27**. The [reported-input registry](company-data-preparation/aapl-reported-cash-flow-bundle.json)
is version 1, contract `reviewed-aapl-reported-cash-flow-inputs`, SHA-256
`d185b995c566d6bfb3b165627283b5ab52edc8ead1e62332d3d9458d0667b747`.
Its twenty-one inputs, twenty-six occurrences and eleven null unknowns remain
unchanged. The [evidence matrix](aapl-alternative-historical-cash-flow-inputs.md#exact-input-and-reconciliation-matrix)
supplies exact concepts, annual context `c-1`, USD units, raw/displayed signs,
ordinals and note locations. The [original-byte references](aapl-alternative-historical-cash-flow-inputs.md#frozen-identity-and-retained-evidence)
and [manifest](evidence/analyst-operating-nwc-response-bodies.json) retain primary
statement/instance bodies, typed SHA-256 digests and retrieval metadata.

Current permitted use: inspect and serialize reported inputs, reproduce the
reported CFO statement check, and review proposed classifications. No adjusted
subtotal, economic cost deduction, interest total, tax rate or future consumer
is created here. FY2024/FY2023 comparatives remain supporting evidence, not new
registrations. Existing partial NWC scenarios/frozen v1 remain authoritative for
their separate, limited scopes.

## Proposed decision table

Amounts below are **USD millions as reported**, not proposed new numbers.
Unless stated otherwise precision is `decimals=-6`. A classification describes
data scope; a proxy/economic policy requires separate explicit acceptance.

| Issue | Verified fact / unavailable information | One recommendation, limitation and user decision |
| --- | --- | --- |
| Consolidated CFO | 111,482, `NetCashProvidedByUsedInOperatingActivities`, ordinal 514; ten-term reported bridge checked. Organic/acquisition/FX and recurring cash allocations unproved. | **Propose consolidated reported CFO as historical reference**, not operating-only, organic or unlevered cash. Accept this limited historical scope, not extrapolation or adjustment authority. |
| Cash PP&E / other investment | 12,715 cash purchases, ordinal 526. Investing Other 1,480, ordinal 529, is mixed; isolated acquisition/intangible cash and complete reinvestment are unavailable. Noncash ROU additions are separate. | **Propose narrow cash PP&E as a separate input**, keep Other visible/unallocated. Accept incomplete investment coverage. Do not infer zero intangible/acquisition spending, allocate a residual, or claim all organic reinvestment. |
| SBC expense / add-back | 12,863 recognized expense (1185) and 12,863 CFO add-back (490); distinct source roles, same annual compensation observation. Outstanding awards and withholding are separate populations. Cash replacement compensation is not disclosed. | **Propose recognized expense as a labeled annual economic-cost proxy, counted once.** This is analyst policy, not issuer cash. A later authorized CFO-based path would neutralize its existing add-back once; an income-based path already expensing SBC would not deduct again. User accepts/rejects this proxy; no adjustment now. |
| Taxes | Net cash taxes 43,369 (565) versus accrued provision 20,719 (318/920/948). Note 7 Ireland/escrow and tax reconciliations do not give a complete recurring operating-cash allocation. | **Propose preserving reported cash tax only for historical cash scope; leave any future operating-tax assumption unpopulated.** User may accept this separation; no rate/basis approved. A future rate needs separately justified jurisdiction/reconciliation or explicit proxy rationale and acceptance. Do not tax after-tax CFO again. |
| Restricted lease cash | Fixed operating cash 2,100 (1023, `decimals=-8`). Fixed cost 2,100 (1017), variable cost 16,100 (1020) and noncash ROU additions 2,800 (1026) also −8. Note 1 combines lease/nonlease components for corporate/retail facilities. Finance interest/principal cash and total variable/nonlease cash coverage unavailable. | **Propose accepting only the rounded fixed operating-lease reported dataset**, preserving reported CFO classification without an extra deduction. User accepts its restricted coverage, not a comprehensive cash-service convention. Equal fixed expense/cash points do not establish completeness. No MSFT three-payment perimeter is imported. |
| Cash interest | No eligible annual cash-interest disclosure; Note 9 debt terms/rates/principal do not supply cash paid. Capitalization, financing/lease overlap and expense-to-cash bridge unavailable. | **Recommend retain explicit unknown, with no proxy.** User acknowledges the limitation rather than selecting an unsupported number. Reported CFO preparation can proceed; unlevering, interest adjustments or complete financing cash claims cannot. |
| NWC / timing | Employee/distribution allocations and investing contamination in AP remain unresolved; narrow book scenario is partial. Cash-flow mixed current/noncurrent changes do not establish book scope or acquisition/FX/reclassification allocation. | **Propose CFO history as a separate data path, leaving original NWC blockers intact.** User accepts that reproducing CFO avoids complete opening NWC/creditor reconstruction only for this narrow use. Do not subtract partial ΔNWC or add D&A/SBC again, certify cash comparability, or waive timing gates. |

## Methodological rationale and future requirements

Recognized SBC expense is a defensible **proposed proxy**, not observed cash:
the established [NYU course discussion of SBC](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/eqemailSpr25.html)
supports treating compensation as a cost despite noncash settlement. AAPL's own
Note 11, not MSFT's acceptance, supports the expense/add-back pairing. An
outstanding-award claim remains separate; no second charge for the same annual
cost through buybacks, withholding or dilution. Face financing employee-tax
payments 5,960 and rounded Note 11 remittance 6,100 have no approved scope bridge;
neither substitutes for corporate taxes or another compensation charge.

The established [NYU lease analysis](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/oplease.htm)
demonstrates that an economic recategorization must align expense, assets,
investment and debt. Its historical accounting illustrations are not current
ASC 842 rules or AAPL-specific evidence. Here **no cash-service or financing
modeling convention is recommended for approval**: only the fixed-payment
dataset is proposed. A future consumer would need a complete chosen perimeter
or expressly approved partial-use limitation, evidence for required finance/
variable cash, and consistent treatment of already embedded CFO costs, noncash
assets and lease debt. Do not charge the same obligation twice or infer annual
principal/interest from future maturities or balance changes.

The established [NYU tax discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/taxrate.htm)
distinguishes reported effective and marginal tax bases; old statutory numbers
are not imported. AAPL's Ireland effects make neither cash paid nor provision a
complete operating-tax assumption. Future consumption must identify tax basis,
period, source date, jurisdictions/weighting or proxy rationale, exceptional
items and uncertainty, with explicit analyst acceptance. No tax shield is implied.

Additional requirements depend on the future claim: acquisition/intangible cash
separation is needed for complete/organic investment; an acquisition-excluding
scope cannot retain acquisition-generated growth automatically. Missing cash
interest needs actual disclosure or a newly authorized defensible estimate with
independent inputs—not debt × rate or expense relabeled cash. No such estimate
is proposed. Acquisition/FX/reclassification and fiscal-length boundaries matter
for comparable trends. The [timing-readiness contract](financial-timing-readiness-design.md)
remains required before future consumption; a cash path must document any
inapplicable book-basis gates and demonstrate its alternative scope consistency,
not mark unknown compatibility as proved or waive it automatically.

## Bounded closure and stopping point

**After explicit acceptance, the FY2025 preparation pilot can close** as one
reported consolidated historical-input package with separately labeled narrow
PP&E, cash taxes, fixed lease cash and SBC expense/add-back roles, plus any
accepted SBC proxy recorded only as an analyst policy choice until separately
authorized numerical implementation. Closure requires recording the user's
choices, author/date, exact period, evidence links and these limitations. It
does **not** require recovering unavailable allocations or approving a tax rate.

Missing disclosure is a durable boundary, not a mandate for an indefinite
annotation/research cycle. Original facts/unknowns must remain; proxy acceptance
cannot manufacture issuer completeness. No complete NWC, interest, lease cash,
reinvestment, FCFF readiness or new supported-company status follows.

The then-next FY2025 acceptance/input checklist is completed; the pilot is closed
only for qualified historical-input preparation. Unknowns and all original
blockers persist. Next authorized work is the independent
[Alphabet FY2024 evidence review](googl-alternative-historical-cash-flow-inputs.md),
not AAPL source changes or numerical treatments. Phase 2 remains postponed.

Validation: registry identity/points/roles/precision and pinned source references,
recommendation-versus-disclosure distinctions, established methodological
references and local links checked; `git diff --check` passes. All other tracked
files, including source, frozen-v1 and every bundle/scenario, remain byte-identical.
No SEC requests, tests or corpus rerun. Baseline **1905/1483/11/27/42 = 3468**
is carried forward, not newly measured.
