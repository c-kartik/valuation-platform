# Analyst Operating NWC design — AAPL, MSFT and GOOGL

Starting HEAD `99fc3707e4faf86c88bed7022b1f81bd1d00c128`. Documentation/research
only; **Phase 2 remains postponed**. This is an additive analyst layer, not a
revision of [historical normalization v1](historical-normalization-v1-freeze.md).
GO for a separately labeled scenario/evidence contract; NO-GO for automatic
removal of current blockers, complete cash ΔNWC certification or FCFF use.

## Methodological boundary

[Damodaran's valuation working-capital definition](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/noncashwc.htm)
excludes cash/marketable investments and interest-bearing funding, and supports
operating-driver analysis rather than blindly extrapolating a volatile annual
movement. That general guidance does not identify issuer-specific payable
contents. His [acquisition discussion](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/acqcapex.htm)
also warns against combining acquisition-driven growth with an assumed absence
of acquisition investment. Neither reference approves our issuer allocations.

Use recurring, noncash operating current assets less operating current
liabilities. Exclude financing principal, investing obligations and separately
modeled income-tax balances. Sales taxes collected for governments are distinct
from income taxes: exclude from the proposed core, disclose that omission, and
allow a separately reviewed operating pass-through scenario. Do not apply the
analytical tax rate to those collections. Include customer financing and cash
employee/distribution accruals where isolated; share-based compensation expense
or unrecognized award cost is not a current cash-payroll liability.

The project already allows a **defined measurable perimeter** to differ from
complete reconstruction. A narrowed perimeter is an explicit analytical choice,
not proof that omitted operating balances are immaterial or zero. Income-tax,
investment collateral, settlement, PP&E and lease balances cannot become
operating solely because they occupy an other-current caption. No blanket
`CurrentAssets - CurrentLiabilities` or inferred residual decomposition.

## Three-issuer decision matrix

| Issuer / frozen v1 blockers | Proposed consistent treatment | Evidence versus assumptions / decision |
| --- | --- | --- |
| AAPL, CIK 320193, 2021–2025: employee liability evidence/materiality unresolved; distribution/marketing only 1/5 exact selected accessions | Core = AR + vendor nontrade receivables + inventory − operating AP − current deferred revenue. Omit unidentified employee/distribution balances consistently from a narrow scenario; expanded scenario subtracts separately supplied cash operating accruals. | Vendor balances are operating supply-chain balances, not investment receivables. AP remains subject to investing contamination uncertainty. 2025 distribution 8,919m is reported; do not inject its 2024 comparative into that selected accession. Missing employee allocations remain unknown. Narrow subtotal is measurable, not complete NWC or approved FCFF. |
| MSFT, CIK 789019, FY2022–2026: supplier-payable methodology unresolved | Core = AR + inventory − (reported AP − PP&E in AP) − current unearned revenue − employee accruals. Strategic component-purchase receivables and broad other-current captions remain separately assessed, not customer AR. | PP&E-in-AP 6,900m FY2025 and 26,700m FY2026 are explicitly disclosed current balances. Earlier exact selected filings do not supply equivalent isolated operands; later 2023/2024 comparative 3,800m/4,300m cannot silently fill them. Partial evidence-backed adjustment; no five-period complete equation. |
| GOOGL, CIK 1652044, 2021–2025: supplier AP and stable inventory treatment unresolved | Narrow core = AR − operating AP − current deferred revenue − employee accruals − revenue share − accrued customer liabilities. Inventory is excluded consistently across all five periods in this scenario, not switched off when its tag disappears. Expanded alternative adds separately evidenced/estimated inventory. | Inventory 1,170m/2,670m is reported in 2021/2022; 2023–2025 merged other-current-asset captions do not prove zero. 2024 note identifies 3,200m PP&E in AP at submitted rounded precision. 2025 combined supplemental PP&E 15,090m and separate accrual 8,877m suggest a 6,213m AP allocation, but stock-versus-period scope must be established before approving subtraction. No all-five automatic equation. |

Each issuer has five frozen periods. No preferred numerical estimate of the
unidentified allocations is approved. Selecting the narrow alternative requires
an explicit analyst perimeter decision; it cannot be the silent production default.

## Exact annual mapping and arithmetic

[Machine-checkable inventory](analyst-operating-nwc-inventory.json) records all
15 accession/DEI annual identities, exact reported component values, namespace,
context/entity, empty dimensions, unit IDs, raw value/decimals/nil and deterministic
occurrence ordinals. Repeated equal occurrences are retained, not summed.
The companion [response-body manifest](evidence/analyst-operating-nwc-response-bodies.json)
retains 34 bodies: 30 primary/instance artifacts and four submissions/history
responses, with URL, accession where applicable, retrieval metadata, explicitly
typed SHA-256 and gzip/base64 lossless bytes. Five retained originals reused;
29 specific-gap retrievals. Reused bodies have unknown original retrieval time
where unavailable; none is invented. Historical unverified fingerprints are
not upgraded or overwritten by this new manifest.

The table is **reported-driver arithmetic**, not approved normalized NWC or
cash ΔNWC. It uses whole reported AP, excludes unidentified residual captions,
and omits AAPL employee/distribution and GOOGL inventory consistently. MSFT
inventory/employee and GOOGL revenue-share/customer liabilities are included.
Units are USD millions; original USD values and source precision are retained.

| Issuer | Selected accession | Authoritative annual start–end | Unadjusted driver subtotal | Adjacent subtotal change |
| --- | --- | --- | ---: | ---: |
| AAPL | 0000320193-21-000105 | 2020-09-27–2021-09-25 | -4,289 | opening unavailable |
| AAPL | 0000320193-22-000108 | 2021-09-26–2022-09-24 | -6,149 | -1,860 |
| AAPL | 0000320193-23-000106 | 2022-09-25–2023-09-30 | -3,356 | 2,793 |
| AAPL | 0000320193-24-000123 | 2023-10-01–2024-09-28 | -3,680 | -324 |
| AAPL | 0000320193-25-000079 | 2024-09-29–2025-09-27 | -240 | 3,440 |
| MSFT | 0001564590-22-026876 | 2021-07-01–2022-06-30 | -27,196 | opening unavailable |
| MSFT | 0000950170-23-035122 | 2022-07-01–2023-06-30 | -28,817 | -1,621 |
| MSFT | 0000950170-24-087843 | 2023-07-01–2024-06-30 | -33,972 | -5,155 |
| MSFT | 0000950170-25-100235 | 2024-07-01–2025-06-30 | -35,145 | -1,173 |
| MSFT | 0001193125-26-323660 | 2025-07-01–2026-06-30 | -48,053 | -12,908 |
| GOOGL | 0001652044-22-000019 | 2021-01-01–2021-12-31 | 3,589 | opening unavailable |
| GOOGL | 0001652044-23-000016 | 2022-01-01–2022-12-31 | 5,205 | 1,616 |
| GOOGL | 0001652044-24-000022 | 2023-01-01–2023-12-31 | 8,178 | 2,973 |
| GOOGL | 0001652044-25-000014 | 2024-01-01–2024-12-31 | 10,142 | 1,964 |
| GOOGL | 0001652044-26-000018 | 2025-01-01–2025-12-31 | 10,669 | 527 |

All annual starts are confirmed by FY DEI context, not inferred from duration
length; AAPL's 53-week 2023 is retained. End dates match the frozen validation
matrix; unique non-amended 10-K metadata binds accessions, not a new latest-five
selection. Each row's primary SEC URL and source excerpts are in the inventory.
For example: [AAPL 2025 notes 3/6/7/leases](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm),
[MSFT 2026 property/business-combination notes](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm),
[GOOGL 2024 accrued-expenses note](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm).
Excerpts are locator candidates, not standalone semantic approvals; review the
retained complete statement/note in context. Numeric facts exclude text blocks.

## Component review and quantifiable uncertainty

**AAPL:** Balance sheet, receivables, revenue, statement-details, lease and tax
notes support trade AR, vendor receivables from component sales to manufacturing
vendors, inventory and current deferred revenue as core drivers. Other assets
include restricted/other balances, not proven entirely operating. Other current
liabilities contain income taxes, collected taxes and lease obligations; 2025
separately identifies distribution/marketing, but not employee cash accruals.
The 2021 accounting disclosure associates noncash PP&E with AP/other liabilities
in an earlier year; neither it nor absence of later disclosure proves current
AP is pure operating. Keep an unknown investing-in-AP allocation, not zero.

Other-current assets are 14,111/21,223/14,695/14,287/14,585m; other-current
liabilities 47,493/60,845/58,829/78,304/66,387m. These are gross caption exposure,
not estimated operating amounts or proof of immateriality. Including reported
2025 distribution alone lowers that narrow level from -240m to -9,159m. A
five-period distribution/employee series is still unavailable. Do not backfill
the 7,679m 2024 comparative shown in the 2025 filing. Income-tax/lease amounts
can support explicit exclusion only under an independently reconciled caption
mapping; a remainder is mixed, not employee accrual by subtraction.

**MSFT:** Balance sheet and inventory notes identify current AR, inventories,
unearned revenue and accrued compensation. Inventories are raw material/WIP/
finished goods, not cash-equivalent assets; preserve book amounts and noncash
timing uncertainty. Exclude income taxes and borrowing/leases from core.
Property note explicitly isolates PP&E remaining in AP for the last two exact
selected filings. Adjusted AP = 27,724 − 6,900 = **20,824m** (2025), and
42,416 − 26,700 = **15,716m** (2026). The resulting narrow levels are -28,245m
and -21,353m; adjacent change is **+6,892m**, versus -12,908m using whole AP.
The **19,800m difference** demonstrates consequence without an arbitrary
materiality threshold. Reported precision is not unrounded economic certainty.
Earlier allocation remains unquantified; model `k_PP&E` as unknown or a reviewed
analyst estimate, never current-year AP minus a cash-flow residual.

Other-current assets 16,924/21,807/26,021/25,723/48,594m and liabilities
13,067/14,745/19,185/25,020/26,738m remain gross exposure, not operating estimates.
Keep strategic component receivables, prepaid/deferred acquisition or investment
items and contract costs separate pending exact current classification. Current
contract-cost capitalization/amortization must not be counted both as D&A and
working-capital investment. Broad balance labels cannot settle that interaction.

**GOOGL:** Compensation, TAC/revenue-share, current contract and accrued customer
liabilities are distinct; customer accruals sit inside broad accrued liabilities,
so do not subtract both the whole caption and its components. Accrued PP&E is
separate from AP: subtracting that balance directly from AP would be wrong.
The 2024 footnote expressly identifies **additional** 3,200m PP&E in AP, giving
reported-precision operating AP 7,987 − 3,200 = **4,787m** and narrow level
13,342m. Do not silently reassign its 2023 2,800m comparative. In 2025 the
supplemental duration-shaped combined 15,090m is not automatically an instant
closing balance; 15,090 − 8,877 = 6,213m is a **conditional proposal**, not an
approved operand or standalone completeness proof. Earlier AP allocation is
unquantified. No generic META adjustment formula transfers by numeric similarity.

Inventory is 1,170m/2,670m in the first two selected statements. Later merged
other-current assets of 12,650/15,714/16,309m cannot establish missing inventory
as zero. A conditional nonnegative inventory-only book bound is [0, that gross
caption], not a probability interval or approved point estimate. Including known
inventory changes the first two narrow levels to 4,759m/7,875m; continuing that
expanded perimeter requires new allocations for all later years. Other assets
also contain investment/derivative collateral. Accrued captions include fines,
income taxes, leases, PP&E and unsettled investment trades; fines and settlement
cash require consistency with the chosen recurring EBIT normalization, not
automatic recurring operating classification. Residual liabilities remain mixed.

## Assumption and override contract

Propose immutable `analyst_operating_nwc` design version `1` with separate
issuer/perimeter/scenario identities, not new versions replacing frozen policies.
Each contribution has `REPORTED`, `EVIDENCE_DERIVED`, `ANALYST_ESTIMATE`, or
`OUTSIDE_PERIMETER` provenance; unresolved required inputs yield no complete
amount. A reported-driver subtotal remains explicitly partial/narrow even when
its arithmetic is exact. Record excluded amounts where known without calling
them zero. No default 0%, peer ratio, fixed dollar or materiality waiver.

An analyst override must retain author/date/rationale, targeted CIK/accession/
annual/instant identity, original observation, scenario/perimeter version,
superseded estimate, amount or range, unit/precision, supporting evidence IDs,
and assumptions about scope/acquisition/FX/timing. Explicit zero is allowed only
as a labeled analyst assumption or reported fact, never absence conversion.
Finite Decimal arithmetic and signed contributions; intervals require endpoints
and dependencies. Estimated allocation of a mixed caption must stay within its
evidenced gross balance unless a separately evidenced bridge explains otherwise.
Do not stack distributions, employee accruals and a residual that includes them.
No automated base-case choice is approved here.

For a narrowed baseline `C`, expose the analytical correction as
`NWC_scenario = C + PP&E_in_AP + other_operating_assets − other_operating_liabilities`
plus inventory only in GOOGL's explicitly expanded scenario. This equation is
a transparent design, **not proof of completeness**. Unknown correction is not
zero. Bounds on a period amount do not tightly bound its movement without
opening/closing covariance or scenario consistency; retain paired assumptions.

## ΔNWC, comparability and downstream readiness

Book movement = closing minus opening under identical scenario/perimeter.
First frozen period has no selected opening level; do not invent one. A cash
operating-investment bridge would additionally separate acquisition/disposal,
FX translation, noncash changes and classification transfers **component by
component**, preserving original book movement. No such exhaustive bridge is
approved for these fifteen periods. Cash-flow operating rows are cross-checks,
not replacements for book levels or residual allocation generators.

MSFT's Nuance/Activision business-combination notes establish acquisition
exposure in FY2022/FY2024, not full current operating-account allocations.
GOOGL cash-flow changes explicitly exclude effects of acquisitions; prior
balance presentations are recast (including the 2022 inventory caption merger
and 2024 accrued fines/other classifications in later filings). AAPL cash-flow
rows mix current/noncurrent assets/liabilities; FX and noncash effects also
prevent equating those rows to our perimeter changes. These are precise reasons
for unproved cash comparability, not proof every period is incompatible. A
reclassification within a fully included perimeter may cancel; a transfer across
its boundary requires a bridge. Later comparative observations remain separate
corroboration and cannot silently change the frozen selected observations.

Income-tax balances excluded here must be handled once by future tax cash/EBIT
conventions; customer/employee accruals must align with operating revenues/costs.
Lease balances remain outside pending integrated lease treatment. Book inventory
and PP&E supplier credit require EBIT/D&A/Capex consistency under the
[timing-readiness design](financial-timing-readiness-design.md). Generic/MSFT
D&A basis and GOOGL missing D&A are not cured by analyst NWC estimates. Scenario
availability does not imply READY; unknown, input-unavailable, ambiguous and
demonstrated-incompatible conclusions remain distinct. No automatic FCFF use.

## Required implementation/validation boundary

Keep the three frozen v1 policies and all 27 blocked production states. An
analyst evaluator/serialization namespace must be separate from schema 5 and
the active normalization registries. Any future substitution requires explicit
perimeter approval/version and consumer impact review, not toggling blockers.
Meaningful tests before production behavior changes:

- Fifteen frozen identities/actual annual dates; wrong CIK/accession, amendment,
  missing context, dimension, nil, non-USD or mismatched raw-body digest rejects.
- Duplicate representations confirm one operand only after full semantic
  equality; preserve ordinal/precision; competing values remain ambiguous.
- Independently reproduce all fifteen driver sums and twelve adjacent changes;
  first three openings unavailable; reconstruct after serialization exactly.
- Verify MSFT 2025/2026 adjusted AP/19,800m delta effect and GOOGL 2024 rounded
  note scope. Reject later comparative backfill and unproved 2025 combined stock
  subtraction; an isolated accrual is never assumed to reside within AP.
- Required unknown allocation blocks complete scenario amount; explicit narrow
  omission/zero estimate retains assumption labels and cannot upgrade historical
  readiness. Reject overlap and incompatible opening/closing perimeter versions.
- Acquisition/FX/reclassification adjustments require signed, independently
  sourced reconciliation; unmatched cash-flow residual remains diagnostic.
- Override/interval dependency/history round-trips; synthetic assumption changes
  expose signed sensitivity and never mutate reported facts or frozen outputs.
- Timing unknown/input unavailable remains non-ready even with an analyst amount;
  no generic/MSFT D&A certification, tax duplication or automatic lease adjustment.

Targeted documentation checks passed: 3 × 5 identities, exact DEI FY context,
numeric occurrence/entity/unit links, all 34 byte digests, driver arithmetic,
supported partial adjustments, local references and `git diff --check`.
Production remains 1,905/1,483/11/27/42 = 3,468; classifications and historical
v1 approvals unchanged. No full tests/corpus rerun or policy implementation.

**Smallest next implementation milestone:** isolated analyst-NWC scenario and
assumption-provenance models plus a pure reported-driver/override evaluator,
with unknown-required-input and interval handling, serialization and focused
synthetic/retained-evidence tests. No default estimates, v1 blocker removal,
cash-adjusted ΔNWC or valuation engine. Phase 2 timing-gate/forecast start stays
postponed until explicitly resumed; no broader issuer research is implied.

## Implemented isolated foundation

This subsequent milestone implements the bounded foundation in
[`analyst/nwc.py`](../src/valuation_platform/analyst/nwc.py), not the earlier
research conclusions as production policies. Frozen v1 evidence, schema 5,
registries and blockers remain unchanged. The
[preparation register](company-data-preparation/index.md) contains 40 issuer
records / 680 measure rows, with one Alphabet file covering GOOG/GOOGL. It carries
forward evidence/counts and marks unreviewed details, not fresh financial review.

Every scenario supplies its own identity/version/perimeter, actual CIK/accession/
annual period, ordered signed components, scope keys, treatments, rationale,
limitations and unresolved effects. Every omission needs explicit classification
provenance; required unknown inputs produce `input_unavailable`, not zero or a
silently available subtotal. Valid competing values produce `ambiguous_evidence`.
Available amounts are **always `partial_perimeter`**, never complete Operating
NWC; `is_complete_operating_nwc` and `fcff_ready` remain false. Caller classifications
and scope assertions are recorded, not automatically approved economically.

Reported evidence verifies original-body representation/hash and binds every
eligible confirming/competing instant occurrence and actual FY context to retained
instance bytes. Different equivalent context/unit IDs and raw precision can
confirm; omitted eligible occurrences, broken links, nil collisions, non-USD
selected units or value/source mismatches reject. Dimensioned source facts do
not conflict with consolidated facts. SEC-supported derivations require explicit
same-period operands/coefficient arithmetic; they cannot use estimates as SEC
facts. No retrieval or new parser/normalization policy is added to historical v1.

Classification, numerical estimates, manual and external input kinds remain
separate. No estimates/input values are populated by the register or foundation.
Explicit overrides retain original/superseded provenance and their changed amount;
unselected competing overrides remain ambiguous. Mixed-caption ceilings reject
out-of-range allocations. Decimal interval arithmetic keeps declared dependencies
and conservative enclosures, never estimates covariance or calls a range tight.
Rounded reported points retain raw/Decimal/decimals and submitted-precision
diagnostics; the evaluator invents no economic uncertainty interval or tolerance.

`change` requires identical issuer/scenario/version/perimeter and ordered component
treatment/scope with exactly adjacent actual fiscal boundaries. First openings
are unavailable; required missing values prevent changes. The available outcome
is `partial_book_movement`, retains both levels and all unresolved effects, and
always has `cash_investment_certified=False`. No acquisition/FX/reclassification/
timing correction or forecast consumption is implemented. Schema `1` is a
separate analyst namespace: scenarios and evaluations preserve exact decimals,
dates, provenance, occurrences and verified body bytes. Round-trip reconstruction
rechecks model/source linkage and recomputes evaluation summaries; it cannot
upgrade completeness/readiness. It is not standardized historical schema 5.

Validation: **41 focused / 640 full-suite tests passed**; all 15 retained sums and
12 adjacent movements reproduce, MSFT FY2025/FY2026 partial adjustments preserve
the **19,800m effect**, without earlier-year or FCFF approval. Mapping checks cover
all 40 register files/17 measures, with source references and frozen-validation
digest. Compileall and staged `git diff --check` pass. No SEC requests or corpus
rerun; existing source/registry/output files and baseline 1,905/1,483/11/27/42
remain untouched. Logs are in `/tmp/analyst-nwc-focused.log` and
`/tmp/analyst-nwc-full-suite.log`.

**Next bounded milestone:** review and publish explicit MSFT FY2025–2026 partial
scenario input bundles, with classified omissions and retained evidence. No
default/earlier-year estimates, cash bridge or automatic policy readiness. Phase
2 remains postponed; the future joint timing contract still gates consumption.

## Reviewed MSFT partial bundles

The preceding foundation's next milestone is now completed by the
[detailed MSFT review](company-data-preparation/MSFT.md#reviewed-fy20252026-partial-input-bundles)
and [explicit version-1 input bundles](company-data-preparation/msft-analyst-nwc-bundles.json).
These are opt-in input artifacts, **not** historical policies, defaults, a new
schema or automatic loader. The test adapter constructs existing immutable
models; the production evaluator is unchanged. Four original statement/instance
byte digests and twelve exact selected occurrences bind two frozen 10-K periods.
Analyst omission classifications have author/date/rationale and evidence;
no estimates, manual or external numerical inputs are introduced.

GO only for partial AR/inventory/AP/current-contract/compensation scenarios with
the Note 6 PP&E-in-AP exclusion. Whole AP remains a separately identified
diagnostic comparator. Adjusted levels −28,245m/−21,353m produce +6,892m book
movement, versus −12,908m without exclusion; **+19,800m effect at reported
precision**. Omitted gross other-current captions are not zero or immaterial.
PP&E source decimals −8 and core −6 are retained, not upgraded to economic
certainty. Required unknown allocations remain unavailable if an expanded
perimeter is selected. No FY2024 opening or earlier-period adjustment is supplied.

Both outputs remain partial/non-ready; acquisition, FX, reclassification,
inventory/contract-cost and integrated EBIT/D&A/Capex/tax/lease timing bridges
are unproved, not declared incompatible. Historical blockers and frozen values
remain intact. **49 relevant tests passed**; no production source changes,
SEC requests, full-suite or corpus rerun. Register maintenance is now a
[standing same-milestone requirement](company-data-preparation/index.md#standing-maintenance-requirement).

Next bounded milestone: one explicit AAPL FY2025 partial-bundle review using
retained evidence, with unknown AP allocation and employee/distribution
limitations exposed. No estimates, earlier-period extension or Phase 2 restart.

## Reviewed AAPL FY2025 partial bundle

The preceding MSFT milestone's bounded next step is completed by the
[AAPL record](company-data-preparation/AAPL.md#reviewed-fy2025-partial-input-bundle)
and [explicit version-1 input](company-data-preparation/aapl-analyst-nwc-bundle.json).
GO only for the documented narrow **reported-driver partial scenario**, not
complete NWC or certified operating AP. The exact FY2025 selected accession and
actual annual period bind two retained statement/instance bodies and six numeric
occurrences: five included balances plus known-but-omitted distribution evidence.
The unchanged evaluator yields **−240m**, retaining submitted `decimals=-6`.

Whole AP is transparent diagnostic input; unknown investing contamination is
not approved as zero. Employee accruals remain unquantified; distribution and
marketing **8,919m** is reported but outside the narrow perimeter, not unknown.
Explicit classifications and original reported evidence survive serialization;
requiring an unknown allocation makes the expanded result unavailable. No
default estimates, expanded distribution equation or later-comparative backfill.

One reviewed level supplies **no ΔNWC**: no opening bundle; opening unavailable,
amount absent. Acquisition/FX/noncash/reclassification and integrated financial
timing remain unproved. Complete-NWC/FCFF/cash-certification flags remain false;
historical values, policies and blockers unchanged. The test-only adapter invokes
existing models/serialization; no production loader or source change.
**57 relevant tests passed**; evidence, links, compileall and diff checks pass.
No SEC requests, full suite or corpus rerun; Phase 2 remains postponed.

Next bounded milestone: one retained-evidence GOOGL FY2024 partial-bundle review,
with consistent inventory omission and rounded PP&E-in-AP scope explicit; no
conditional FY2025 allocation approval, period extension or cash/FCFF readiness.
