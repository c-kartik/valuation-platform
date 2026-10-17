# AAPL — consolidated frozen FY2021–FY2025 analyst-input package

## Current company batch — one consolidated review, new judgments inactive

[Machine companion](aapl-analyst-input-package.json) `/aapl_history_review` adds
one five-year review to the **unchanged** FY2025 source/proposal/accepted view.
The existing approval audit and every prior null remain exact. No new decision
is active, no MSFT financial assumption is transferred, and AAPL is **not yet
analyst-complete**. This review uses the existing14 families and your instructed
reported-movement/independently reconciled-CFO path; reconstructed complete NWC
and book ΔNWC are not prerequisites of that proposed path. It selects no Phase2
formula. All new judgments are in the single A1–A10 table below, not annual cycles.

### Exact frozen selection and evidence

CIK320193, original selected10-Ks; manifest rows5–9, checked against authoritative
annual DEI/entity/contexts. **FY2023 has53 weeks**, other years52; no annualization.
All ten bodies and original receipts already exist in
[retained evidence](../evidence/analyst-operating-nwc-response-bodies.json).

| FY | Selected accession | Authoritative annual dates | Primary / instance artifact pointers |
|---|---|---|---|
|2021|0000320193-21-000105|2020-09-27–2021-09-25|`/artifacts/1`, `/artifacts/2`|
|2022|0000320193-22-000108|2021-09-26–2022-09-24|`/artifacts/3`, `/artifacts/4`|
|2023|0000320193-23-000106|2022-09-25–2023-09-30|`/artifacts/5`, `/artifacts/6`|
|2024|0000320193-24-000123|2023-10-01–2024-09-28|`/artifacts/7`, `/artifacts/8`|
|2025|0000320193-25-000079|2024-09-29–2025-09-27|`/artifacts/9`, `/artifacts/10`|

Each `/aapl_history_review/periods/0..4/sources` retains URL, typed original-body
SHA256 (`sha256_sec_response_body_bytes`, `sec_response_body_bytes`), actual UTC
receipt/status and byte length. `/facts` binds namespace/concept, annual or actual
instant date, currency/unit, raw value/sign/scale, precision, all confirming
occurrences, inline ID and context; primary inline/instance values must agree.
`/passages` and `/note_observations` bind exact primary text/offset/body SHA for
scope and note transcriptions, **not fabricated XBRL occurrences**. Original
FY2025 receipt/metadata and acceptance remain separate and unchanged.

### Five-year14-family coverage (not a completeness certification)

S = source-supported input/operation; A = existing FY2025 approval within its
original scope; P = new analyst operation/proxy/perimeter requires approval.
All70 slots are accounted for: **27 S /8 A /35 P**. No missing body or broken
essential source binding was found; **this does not mean no missing disclosure**.
Unknown expense D&A, claim populations and allocations remain unknown. Every
year remains incomplete pending the choices below; supported arithmetic is not
financial acceptance. FY2025 borrowing is already selected narrowly but the
company-wide no-additional-borrowing-adjustment assumption is newly proposed.

| Existing family | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|:---:|:---:|:---:|:---:|:---:|
|Revenue|S|S|S|S|A|
|EBIT|S|S|S|S|A|
|D&A|P|P|P|P|P|
|Cash Capex|S|S|S|S|A|
|Reported CF working-capital movements|S|S|S|S|S|
|Deferred taxes|S|S|P|P|P|
|SBC|P|P|P|P|A|
|Separate CFO residual operation|P|P|P|P|P|
|Reported CFO|S|S|S|S|A|
|Reported tax context|S|S|S|S|A|
|Cash/investment components|P|P|P|P|A|
|Debt/lease components|P|P|P|P|P (named selection A)|
|Other claims/assets|P|P|P|P|P|
|Point-in-time shares|P|P|P|P|A|

### Source-supported schedule and precision

USD millions except shares. R = rounded note points (usually decimals−8); source
statement points generally decimals−6. Shares are counts, decimals−3. All operand
precision variants remain in JSON; arithmetic does not create additional accuracy.
The D&A proxy below is **proposed**, not a new active source selection.

| Observation / named calculation | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
|Revenue|365,817|394,328|383,285|391,035|416,161|
|EBIT|108,949|119,437|114,301|123,216|133,050|
|Reported CFO|104,038|122,151|110,543|118,254|111,482|
|Displayed CFO terms / movement rows|12 /7|12 /7|10 /6|10 /6|10 /6|
|CFO D&A add-back / proposed proxy|11,284|11,104|11,519|11,445|11,698|
|PP&E note expense, not complete D&A|9,500R|8,700R|8,500R|8,200R|8,000R|
|SBC expense / separate add-back|7,906 /7,906|9,038 /9,038|10,833 /10,833|11,688 /11,688|12,863 /12,863|
|Cash PP&E outflow|−11,085|−10,708|−10,959|−9,447|−12,715|
|Investing Other, mixed outflow|−608|−1,780|−1,337|−1,308|−1,480|
|Separately displayed net acquisition cash|−33|−306|unknown|unknown|unknown|
|Noncash combined ROU additions|3,300R|2,800R|2,100R|1,000R|2,800R|
|Pure deferred-tax CFO row|−4,774|895|unknown|unknown|unknown|
|Deferred provision, distinct role|−4,774|895|−3,024|−3,031|−1,339|
|Mixed Other CFO contribution|−147|111|−2,227|−2,266|−89|
|Tax provision / reported pretax|14,527 /109,207|19,300 /119,103|16,741 /113,736|29,749 /123,485|20,719 /132,729|
|Cash taxes outflow|−25,385|−19,573|−18,679|−26,102|−43,369|
|Reported net cash interest outflow|−2,687|−2,865|−3,803|unknown|unknown|
|Current cash + marketable securities|62,639|48,304|61,555|65,171|54,697|
|LT marketable securities, separate|127,877|120,805|100,544|91,479|77,723|
|CP / term net carrying / finance liability|6,000 /118,719 /848|9,982 /110,087 /941|5,985 /105,103 /1,024|9,967 /96,662 /896|7,979 /90,678 /1,230|
|Proposed named financing subtotal|125,567|121,010|112,112|107,525|99,887 (existing A)|
|Operating lease liability, separate|10,955|11,470|11,818|11,534|12,490|
|Fiscal-end common shares|16,426,786,000|15,943,425,000|15,550,061,000|15,116,786,000|14,773,260,000|
|Nonvested RSUs, separate|240,427,000|201,501,000|180,247,000|163,326,000|151,574,000|

Existing FY2025 approval also preserves partial current operating capital−9,159
(original−240 less identified distribution8,919), vendor receivables included;
employee/capital-creditor/mixed allocations unknown. Earlier source-bound narrow
levels−4,289/−6,149/−3,356/−3,680 are **support only**, exclude undisclosed accruals
and do not impute a distribution zero. Do not compare them with−9,159 as a
consistent-perimeter movement. No book or cash ΔNWC is selected or required by
the proposed cash-movement path. Noncurrent/mixed balances remain source observations.

### ONE consolidated proposed-decision / exception table

The nine new judgments **A2–A10 are pending user approval**, not runtime changes.
A1 is source-supported execution of your instructed path, **not another approval
request or a new assumption**. Their exact wording,
affected identities, source references, numerical effects, alternatives and risks
are in `/consolidated_proposals`; revision-bound to the full source review. Author
and actual review UTC are recorded for proxy proposals, not fictional SEC metadata.

| ID / periods | Concrete recommendation and numerical consequence | Alternative / limitation / stopping condition |
|---|---|---|
|A1 /all5 — source-supported, no approval requested|Use your instructed reported movements + independently displayed/reconciled CFO104,038/122,151/110,543/118,254/111,482 historical path. No complete reconstructed NWC prerequisite; no further deduction of rows already in CFO.|An EBIT/book-NWC path would require unknown employee/investing-in-AP/mixed allocations. Current path remains consolidated, tax/acquisition/FX affected, not organic or cash ΔNWC. This row is operational evidence, not a new financial approval.|
|A2 /all5|Use **11,284/11,104/11,519/11,445/11,698** as explicitly labeled CFO-D&A historical noncash-cost proxies. Keep complete expense-basis D&A null and PP&E note separate. No additional ROU add-back or finance-inclusion assumption.|Alternative leave D&A required input unresolved. Differences to PP&E note1,784/2,404/3,019/3,245/3,698 are **not amortization**. Income/inventory/lease timing unbridged, effect unquantified. FY2021–22 note itself includes PP&E amortization; later prose says depreciation. Proxy approval would accept that uncertainty, not prove scope.|
|A3 /FY2021–24|Recognized SBC7,906/9,038/10,833/11,688 as cost proxy **once**, linked to separate matching add-backs. FY2025 existing12,863 unchanged.|Replacement-cost/award valuation basis unavailable; no duplicate cost or forecast dilution. Stop for this explicit classification.|
|A4 /all5|Operating leases service, finance leases asset financing; named CP + term net carrying + finance liability125,567/121,010/112,112/107,525/99,887, with **no additional undisclosed-borrowing adjustment**. Existing FY2025 convention/subtotal remains accepted; broader omission assumption is new.|Additional borrowing remains source-null and unbounded, not immaterial or a reported zero. All-lease alternative136,522/132,480/123,930/119,059/112,377 requires aligned treatment; not default. Term maturities already included; principal/fair value/lease maturities are not more debt. Stop if omission risk not approved.|
|A5 /FY2021–24|Select reported **gross current financial balances62,639/48,304/61,555/65,171**, not available/excess cash; LT securities separate. Preserve FY2025 accepted54,697. Known restrictions remain visible, not silently ignored.|FY2021–23 total restricted marketable17,900/12,700/13,800R lacks a selected current/LT split. FY2024 cash2,600R + marketable13,200R escrow; FY2025 explicitly dated comparative confirms the latter current. Alternative FY2024 current less identified15,800R =49,371R is non-default pending choice, not a plug. Other restrictions/reserves/strategic allocations unquantified. No gross amount approved for valuation consumption.|
|A6 /all5|Propose no additional preferred or NCI claim adjustment, based on exact common-equity partitions and consolidated wholly-owned presentation; source balances stay unknown.|Economically omits potentially undisclosed claims with unbounded size. Presentation is affirmative context, not explicit zero, exhaustive ownership proof or immateriality. Alternative keep claim requirement blocked; stop for explicit risk choice.|
|A7 /all5|Propose no separate pension funded-status adjustment; retain reported liabilities, do not invent retirement expense or a funded amount.|Weaker evidence: benefit/stock-plan notes do not establish pension completeness. Potential omitted claim/surplus unbounded. Alternative retain essential requirement blocked. Approval must knowingly accept that omission; absence/audit opinion is insufficient proof.|
|A8 /all5|Retain historical provision/positive pretax/ETR and cash taxes. Keep early deferred-tax CFO−4,774/+895; later mixed Other remains mixed, with no separate pure-deferred CFO operation under A1. Retain tax-credit DTA4,262/6,962/8,302/8,856/8,643, no separate pure-NOL economic asset.|Provision is not cash or a replacement CFO row; later pure component remains null. Alternative full operating-tax/deferred/NOL allocation unavailable. Ireland FY2024 charge and FY2025 cash settlement remain historical, not normalized. Future tax basis/rate is Phase2, not a historical completion prerequisite.|
|A9 /all5|No separately computed residual scalar for12/12/10/10/10 fully bound displays. Retain Other−147/+111/−2,227/−2,266/−89; no residual zero or balancing item.|Alternative classify every mixed subamount is unsupported. Display equality does not establish EBIT-based FCFF or operating-only cash. Stop for operation exclusion, not manufactured allocation.|
|A10 /FY2021–24|Select original dated fiscal-end common counts16,426,786,000/15,943,425,000/15,550,061,000/15,116,786,000. FY2025 remains accepted; later cover, EPS and awards separate.|Cover dates are2021-10-15/2022-10-14/2023-10-20/2024-10-18/2025-10-17. No aggregation/dilution. FY2021–22 unrecognized award cost13,600/16,700R covers RSUs **and options**; FY2023 onward18,600/19,400/21,800R covers RSUs. No economic award value.|

### Financial/source exceptions and comparability

- **All five independently displayed CFOs tie exactly**, not by defining a residual.
  FY2021–22 have12 terms/7 movement rows; later10/6. FY2023 re-presents FY2022
  deferred895 +Other111 as Other1,006, and deferred revenue478 +other liabilities
  5,632 as6,110. Selected FY2022 values are not overwritten. Earlier amounts also
  change comparative presentation. Movements include vendor nontrade receivables,
  mixed current/noncurrent balances and tax effects, not pure book ΔNWC.
- FY2021 debt note118,063 principal−380 costs+1,036 hedge =118,719 carrying;
  FY2022 111,824−374−1,363=110,087; FY2023 106,572−356−1,113=105,103;
  FY2024 97,341−321−358=96,662; FY2025 91,281−309−294=90,678.
  These are independently displayed signed note bridges. FY2021 rounded118,100
  and precise118,063 source candidates remain alternatives; the note bridge uses
  the identified precise table caption, not a silent tag/precision precedence.
  Fair values125,300/98,800/90,800/88,400/80,400R are separate observations.
- Acquisition payments33/306 are separately displayed only in FY2021–22.
  FY2021 also separately displays nonmarketable-security purchases/proceeds;
  later Other reclassifies populations. Do not treat all five Other captions as
  an identical acquisition/intangible perimeter. Missing allocations and current
  capital creditors stay unknown; noncash ROU additions are not cash purchases.
- Cash interest2687/2865/3803 is expressly reported in FY2021–23 (`InterestPaidNet`),
  not derived from expense. FY2024/25 remains unavailable. Debt/lease overlap,
  capitalization/gross/net completeness is not certified by that tag; no proxy or
  combined interest total is proposed. Fixed operating lease cash1,400/1,800/1,900/
  1,900/2,100R is restricted reported data; variable expense12,900/14,900/13,900/
  13,800/16,100R is not cash. Finance cash/expense split remains unknown.
- FY2024 Ireland net charge10,200R and15,800R escrow obligation, FY2025 settlement
  and43,369 cash taxes impair recurring-tax comparability. They are not normalized
  or allocated into a new operating tax rate. Claims/UTB precision alternatives
  remain separately evidenced, not additive debt or exhaustive recognized claims.
- Source unknowns remain despite proposed no-adjustment choices. No missing amount
  is called immaterial or given an invented uncertainty bound. No original NWC,
  D&A or timing blocker is automatically cleared; accepted MSFT/Alphabet views and
  all frozen artifacts remain unchanged.

**Acquisition requirements: none identified.** All five exact primary/instance
pairs are retained and verified. Remaining gaps concern disclosure/population/
timing or proposed analyst judgments; no specific additional official artifact
has been established that would supply those allocations. Stop for the single
consolidated approval table; no automatic source/research queue or next issuer.

Validation:104 focused tests pass (52.020s), including10 new company-history
tests; all-three package replays, source/arithmetic/provenance, audit/stale,
serialization and original/pilot/frozen/peer preservation checks pass. Compileall,
574 affected local-path links and diff checks pass; no full-suite/corpus or SEC
requests. Exact logs/qualification are in the current project-status checkpoint. Current
company counts remain42 broad evidence assessments,1 complete company-wide MSFT,
2 partial company packages AAPL/Alphabet,39 broad-only. No Phase1 closure.

## Existing active FY2025 analyst view — preserved user-approved selections

The explicit five-part user instruction is implemented in JSON `accepted_view`
(`aapl-accepted-historical-view-v1`, version1). The immutable
[approval audit](aapl-analyst-treatment-acceptance.json) records authority,
rationale and actual recording UTC **2026-10-15T20:31:05.526779+00:00**
(2026-10-16 00:31:05.526779 Dubai), not a source retrieval or invented earlier
approval time. It binds the original proposal at
`36ef3d2fa63e712d1735e75d23ebeadc0f33bdcc` plus the already-reviewed annual
EPS weighted-average source observations now explicitly packaged separately.

| Active selection, USDm unless shares | Accepted scope / remaining limitation |
| --- | --- |
| **Partial current operating capital −9,159** | Original−240 less distribution8,919; includes manufacturing vendor receivables. Original−240, vendor-exclusion−42,339 and other alternatives are non-default history. Employee accruals, capital creditors and mixed allocations stay unknown; **no ΔNWC or completeness approval**. |
| **Operating leases service; finance leases asset financing. Named financing subtotal99,887** | CP+net term carrying+finance liability only; all-lease112,377 stays non-default. Not complete debt; cash/expense splits unavailable. **No finance-amortization inclusion assumption.** |
| **Current financial balances54,697; LT marketable77,723 separately** | Not unrestricted/excess cash. Unknown restrictions, operating reserves and other claims remain unknown; broader132,420 total is non-default support. |
| **CFO D&A11,698 and depreciation expense8,000R separate** | Complete expense-basis D&A stays explicitly **null/unresolved**. No subtraction to infer amortization, no extra ROU add-back. |
| **Cash PP&E−12,715; investing Other−1,480; noncash ROU+2,800R separate** | Original raw values and display signs/precision retained. No reinvestment sum, capital-creditor estimate or acquisition allocation. |
| **Revenue416,161; EBIT133,050; CFO111,482; SBC expense proxy12,863 once** | Original reported roles, sources and prior acceptance restrictions preserved; SBC add-back remains distinct, not another cost. |
| **Provision20,719; net cash taxes43,369 and other named historical tax observations** | Provision/cash/deferred/ETR stay distinct, no future tax basis/rate or economic adjustment. |
| **Fiscal-end common14,773,260,000, 2025-09-27, decimals−3** | Cover14,776,353,000 at2025-10-17, RSUs151,574,000 and annual weighted-average basic14,948,500,000/diluted15,004,697,000 remain separate. No class/award sum, dilution estimate or award valuation. |

The audit reuses the accepted MSFT view's canonical digest, relevant-content
revision filter, strict JSON and UTC manual-identity controls, **not its financial
assumptions**. A minimal company-specific selection overlay avoids mislabeling
book operating capital as generic cash-flow movements. Each active scalar retains
its original source status and an exact JSON pointer to unchanged proposal input,
plus the approval hash; origin/precision/completeness are not replaced by review
acceptance. Original proposal JSON sections remain exactly unchanged.

Normal replay reads the persisted audit only. Missing/malformed/conflicting audit,
or changed values, scope, precision, alternatives, unknowns, evidence digests or
weighted-average sources fails closed; **explicit revalidation is required**, not
automatic approval. The one-time recording command refuses an existing receipt.
Digest checks detect changes, not adversarially signed user identity. Serialization
is additive and separately versioned within the existing report; no pilot migration.

Original accepted inputs, registries/scenarios, source bytes, all frozen policies/
outputs and the accepted MSFT view remain unchanged. Financial sufficiency remains
**NOT_ASSESSED**; no original blocker removal, complete input certification,
valuation approval, Phase 1 closure or automatic Alphabet work. Validation:
**17 AAPL package/integration tests (5.509s)** and **44 preservation tests**
(AAPL cash15 in2.591s, partial-NWC8 in2.138s, accepted MSFT21 in7.776s) pass.
Tests cover active source/value ties, precision/roles/nulls/non-defaults,
deterministic round trips, audit persistence/restart/staleness, duplicate/tampered
or missing audit rejection and full prior-proposal equality. Original JSON/
runtime/MSFT bytes, both package replays, compileall, **445 local links** and diff
checks pass. No full-suite/corpus rerun or SEC requests. **Stop after AAPL integration.**

## Original proposal record — preserved history, selections superseded above

**One draft for consolidated user review; new judgments are PROPOSED, not
accepted or integrated.** The [machine companion](aapl-analyst-input-package.json)
contains every retained occurrence, context, raw value, sign/scale, precision,
receipt and calculation operand. Original [accepted treatments](../aapl-treatment-acceptance-checklist.md)
remain accepted within their earlier restricted scope. No MSFT assumption or
approval is transferred. Financial sufficiency remains **NOT_ASSESSED**.

## 1. Exact source perimeter and reading key

CIK **320193**, selected non-amended 10-K **0000320193-25-000079**;
annual **2024-09-29–2025-09-27**, duration context `c-1`; closing instant
**2025-09-27**, `c-20`. Only FY2025 is packaged. Comparative columns are source
support, not additional registrations or an approved opening balance/movement.

Both original SEC bodies are in
[the retained manifest](../evidence/analyst-operating-nwc-response-bodies.json):

| Source | Exact artifact / original-body SHA-256 / receipt |
| --- | --- |
| Primary, `/artifacts/9` | [aapl-20250927.htm](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm); `b0dbcbbd800fd1c819007d63d884a1f8b9a5994486d0b2974a4b5b8a6e6eb80e`; 2026-10-11T17:12:47.260610+00:00, HTTP200 |
| Instance, `/artifacts/10` | [aapl-20250927_htm.xml](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_htm.xml); `e1076735f1c81bc96d5c1ff6e1a9d23515d6eacf52b405cb1f7da3e379ac533b`; 2026-10-11T17:12:47.622471+00:00, HTTP200 |

Representation is `sec_response_body_bytes`, digest type
`sha256_sec_response_body_bytes`, not compressed or reserialized bytes. No new
request. Inline IDs below identify the same primary numbers independently of
the instance; JSON records both. **S** source fact/calculation; **A** existing
acceptance; **P** proposed analyst classification; **U** unquantified/unavailable.
Unless specified, amounts are **USD millions**, source decimals **−6**. **R**
means decimals **−8**, rounded hundred-million points. Arithmetic does not
improve precision; labels are origins/review states, not confidence scores.

## 2. Income, D&A, CFO, SBC and taxes

| Population / recommendation | FY2025 | Evidence and status |
| --- | ---: | --- |
| Revenue; retain consolidated direct total | **416,161** | S; income statement p29, `RevenueFromContractWithCustomerExcludingAssessedTax`; ordinals285/599/1210/1302, `f-78` and confirmations. |
| EBIT; retain reported operating income | **133,050** | S; p29 / Note13, `OperatingIncomeLoss`, 309/1233, `f-102`/`f-1044`. No expense reconstruction. |
| CFO historical reference | **111,482** | A; p33 `NetCashProvidedByUsedInOperatingActivities`, 514/`f-307`; consolidated, not organic, unlevered or operating-only. |
| CFO D&A reconciliation add-back | **11,698** | S support; p33 `DepreciationDepletionAndAmortization`, 487/`f-280`. **Not approved expense-basis D&A in this draft.** |
| PP&E depreciation expense | **8,000R** | S support; Note5 p39, `Depreciation`, 866/`f-665`. Missing income-recognized amortization/lease/inventory bridge prevents complete expense-basis D&A. **Do not infer 3,698 amortization by subtraction.** |
| SBC recognized expense / CFO add-back | **12,863 / 12,863** | A expense cost proxy counted once; separate Note11 expense `AllocatedShareBasedCompensationExpense`, 1185/`f-996`, versus reconciliation `ShareBasedCompensation`, 490/`f-283`. Not two costs. |
| Pretax / tax provision / accounting ETR | **132,729 / 20,719 / 15.6100023356…%** | S; p29/Note7, pretax315/`f-108`, provision318/920/948; ETR uses existing positive-denominator provision/pretax rule, full precision in JSON. Not a future operating rate. |
| Net cash income taxes | **43,369** outflow | A; supplemental p33, `IncomeTaxesPaidNet`, 565/`f-358`. Provision difference **22,650** is a historical difference, not a tax allocation. |
| Deferred provision components | **−1,804 −139 +604 = −1,339** | S; Note7 federal/state/foreign, 896/905/914. Not a pure CFO deferred-tax row. CFO mixed Other **−89** remains separate. |

**Recommend retaining the reported income/tax/SBC schedules and restricted CFO
path**, without a new interest proxy, SBC adjustment or tax normalization.
The existing generic normalization/preparation D&A result is not rewritten or
declared erroneous: the narrower **expense/timing** question remains unproved.
Neither the CFO location nor the numerical difference certifies that question.

The ten independently displayed CFO contributions reproduce the reported subtotal:

`112,010 +11,698 +12,863 −89 −6,682 −347 +1,400 −9,197 +902 −11,076 =111,482`.

JSON retains raw asset-change signs and −1 display multipliers; liabilities have
their reported contribution signs. Vendor nontrade and mixed current/noncurrent
rows remain distinct. This is statement reproduction, not a residual-defined
proof or permission to add these items again to CFO. Reported cash movements do
not establish book ΔNWC, organic comparability or a capital/tax allocation.
The Ireland tax disclosures do not establish a full recurring cash-tax bridge.

## 3. Operating capital — concrete proposed perimeter

| Closing population | USDm | Treatment / exact evidence |
| --- | ---: | --- |
| Customer receivables | +39,777 | S operating; balance sheet `AccountsReceivableNetCurrent`, 370/`f-163`. |
| Vendor nontrade receivables | +33,180 | S supply-chain asset; 372/`f-165`, Note4 p39 says component sales to manufacturing vendors; gains reduce product costs. Recommend include, **not MSFT's investing-facilitation treatment**. |
| Inventory | +5,718 | S book FIFO inventory; 374/`f-167`; no cash/expense timing bridge. |
| Whole AP | −69,860 | S reported caption, 390/`f-183`. Operating-only portion not isolated; do not supply a capital-creditor correction. |
| Current deferred revenue | −9,055 | S current customer funding, 394/`f-187`; not total current/noncurrent advances. |
| **Original current-only partial NWC** | **−240** | Original [reviewed scenario](aapl-analyst-nwc-bundle.json), unchanged; excludes known distribution and unknown components explicitly. |
| Distribution and marketing accrual | **−8,919** | Note6 p40, Apple extension `AccruedDistributionAndMarketingCurrent`, 880/`f-679`, c-20. Recommend **include** this identified ordinary operating cost accrual. |
| **Proposed expanded partial current operating capital** | **−9,159** | P: original −240 less known8,919. Source-supported arithmetic, proposed inclusion; **not complete current NWC**. |

This resolves the known omission for the **new proposed** schedule, not the
original blocker. Unknown employee accrual **E** and investing-in-AP amount **K**
remain unavailable: an adjusted level would be `−9,159 − E + K` before other
omitted balances. Neither is assigned zero, an estimate, a materiality threshold
or a bound. No approved opening schedule: **no adjacent book movement or cash
ΔNWC** is populated.

Retained mixed populations and overlaps (all c-20, decimals−6): OCA **14,585**
(`f-169`); other noncurrent assets **83,727** = located DTA **20,777** + remaining
**62,950** (`f-177`/`f-670`/`f-672`); OCL **66,387** = taxes **13,016** +
distribution **8,919** + remaining **44,452** (`f-185`/`f-677`/`f-679`/`f-681`).
The remaining current parent includes operating/finance lease liabilities
**1,579 /538**; its remainder **42,335** is **not employee accrual**. Noncurrent
liabilities **41,549** include leases **10,911 /692**; **29,946** is still mixed,
not an operating liability allocation. ROU asset11,205 overlaps other NC assets.

**Recommend leave these residual captions unallocated support, not add a whole-
caption operating estimate.** Taxes and funding/lease populations must not be
double-counted as operating accruals. Unknown allocations may be material.
Alternative original −240 omits8,919; alternative excluding vendor receivables
from the expanded schedule gives **−42,339**, **−33,180** versus recommendation.
The supply-chain note makes the latter less appropriate. CFO already packages
reported movements without solving these closing-book allocations; that avoids
reconstruction for the reported-reference path only, not its economic limitations.

## 4. Investment, leases, financial balances and claims

| Source-supported input / proposed handling | USDm | Evidence / limitation |
| --- | ---: | --- |
| Cash PP&E / investing Other | **−12,715 / −1,480** | A narrow PP&E, S mixed Other; p33 526/`f-319`,529/`f-322`. Other is not proven acquisition/intangible-only or gross reinvestment. No combined reinvestment subtotal. |
| Noncash ROU additions | **2,800R** | S combined operating/finance; Note8 1026/`f-825`, Apple extension. No invented class allocation or cash Capex inclusion. Capital creditors/noncash PP&E bridge unavailable. |
| Fixed operating cost / fixed operating cash | **2,100R /2,100R** | Expense versus A restricted cash dataset; Note8 1017/1023. Equal points do not establish identical coverage; fixed cash already embedded in CFO. |
| Variable lease cost | **16,100R** | Note8 1020/`f-819`; expense based primarily on output purchases, **not cash paid**. Cannot create total lease cash by summing it with fixed cash. |
| Operating ROU / finance ROU assets | **11,205 /1,033** | Note8 1030/1032; other NC assets versus PP&E. No AAPL finance-amortization inclusion assumption or guessed expense add-back. |
| Operating lease liability | **1,579 +10,911 =12,490** | Note8 current/noncurrent; maturities14,725 less future imputed interest2,235 also tie. Those maturities are not annual cash. |
| Finance lease liability | **538 +692 =1,230** | Note8 current/noncurrent; future payments1,579 less imputed349 tie. Annual finance interest/principal cash and expense splits unavailable. |
| Cash / current / noncurrent marketable securities | **35,934 /18,763 /77,723** | Balance sheet/Note3; ord366/368/380 and725/726/727, `f-159`/`f-161`/`f-173` and confirmations. |
| Named current financial balances / all reported cash+securities | **54,697 /132,420** | S disjoint named partitions; latter agrees with Note3 Apple parent724/`f-521`. Recommend current pool for narrow liquidity, LT separate financial investments. Neither is unrestricted/excess cash. Strategic/restricted and reserve coverage remains unproved. |
| Term debt principal → net carrying | **91,281 −309 −294 =90,678** | Note9 p44: discount/issuance/premium and hedge deductions; 1123/1125/1127/1129. Concept `DebtInstrumentCarryingAmount` tags the **principal caption**, not the net total. |
| Current / noncurrent term debt / CP | **12,350 /78,328 /7,979** | Net carrying; balance sheet/Note9. CP is separately reported, not an inferred zero. Note9 rounded8,000 is not another borrowing to add. |
| Named CP+term / proposed plus finance leases | **98,657 /99,887** | Proposed financing inclusion of1,230, not complete debt. No cash/debt netting or enterprise-to-equity calculation. |
| Debt fair value | **80,400R** | Note9 Level2, 1143/`f-954`, c-74. Carrying/fair difference10,278 is a measurement comparison, not an economic gain or extra claim. |
| Tax-credit DTA / unrecognized tax benefits | **8,643 /23,242** | Note7: gross credit DTA is not pure NOL or equity value. Exact roll-forward1010/`f-809` versus rounded narrative23,200R987/`f-786` retained as distinct precision alternatives. Neither is automatically incremental borrowing/cash. |
| Future purchase commitments / uncommenced operating leases | **13,308 /523** | Note12 1201/`f-1012` (commitments with remaining term over one year); Note8 1079/`f-890`, explicitly dimensioned uncommenced operating leases. Not recognized funded debt, current cash or a proved disjoint aggregate; no sum. |

**Recommended AAPL-specific classification (P):** operating/variable lease costs
remain operating, finance ROU/liabilities remain asset financing, based on Note8
locations. Keep the accepted restricted cash dataset unchanged. Unlike MSFT,
**no assumption establishes a complete expense D&A or finance-amortization
overlap here**. An all-lease financing obligation alternative is **112,377**,
**+12,490** versus proposed99,887; choosing it would require consistent future
expense/debt/investment treatment, not a liability-only valuation adjustment.
An all-lease cash-service alternative cannot be quantified without finance cash
and variable cash evidence. No financing cash total is constructed.

Recommend preserve tax contingencies/commitments separately, not add gross tax
benefits to debt or tax-credit DTA to cash/equity. Pension, preferred/NCI and
strategic claims are **not separately established as an exhaustive population**,
not zero/immaterial. Stop on the stated bounds; no automatic research queue.
Note12 identifies supplier, licensed-IP/content and distribution-right purchase
commitments: recommend a separate future-commitment disclosure, not current
operating capital or a financial borrowing. Operating versus capital allocations
remain unquantified. Management's no-reasonably-possible-material-loss assessment
is an issuer judgment, not proof of zero legal accrual/exposure or a probability
estimate supplied by this package.

## 5. Dated common shares and disclosed awards

| Observation | Amount / precision | Evidence and recommended handling |
| --- | --- | --- |
| Fiscal-end common | **14,773,260,000 shares**, decimals−3, 2025-09-27 | Balance sheet417/`f-210`, c-20. Proposed historical snapshot, not exact-unit precision or diluted shares. |
| Cover common | **14,776,353,000 shares**, decimals−3, **2025-10-17** | Cover262/`f-51`, c-11; keep separate. +3,093,000 is a later-date difference, not forecast dilution or a reconciliation defect. |
| Nonvested RSUs | **151,574,000 shares**, decimals−3, 2025-09-27 | Note11 1174/`f-985`, c-146, explicit RSU award class. Not incremental dilution or an added share total. |
| Unrecognized RSU compensation | **21,800R USDm** | Note11 1191/`f-1002`, same class/date. Future expense disclosure, not award market value or another current SBC charge. |

Annual weighted-average diluted shares **15,004,697,000** (EPS330/333 and616/622)
are a different **duration** population, not closing shares. No award valuation,
forecast dilution or EPS/per-share calculation. Such future choices are not
prerequisites for preparing these named historical observations.

## 6. One consolidated approval sheet

All new rows below remain **P**. Existing AAPL accepted CFO/cash PP&E/SBC proxy/
cash-tax/restricted fixed-lease data remain **A**, not reopened for approval.

| Decision / recommendation | Alternative and numerical consequence | What this solves / boundary |
| --- | --- | --- |
| Include known distribution accrual: partial capital **−9,159** | Original **−240** omits8,919; excluding vendor gives **−42,339** | Corrects a named omission only. Employee/capital-creditor and mixed residuals remain unknown; no cash ΔNWC. |
| Operating service / finance asset financing, using AAPL Note8 | Named financing **99,887** vs all-lease **112,377**, +12,490; all-cash-service amount unavailable | Coherent historical locations without fabricated expense/cash bridge. D&A11,698 is CFO support; complete expense D&A unavailable. |
| Separate investment columns | Other1,480 remains visible; noncash2,800R not cash | Keeps approved PP&E12,715 narrow. No organic/acquisition allocation or full reinvestment. |
| Current financial pool **54,697**; LT **77,723** separately | Broader reported pool132,420, +77,723; not a cash availability estimate | Named financial populations and borrowing measurements traceable, not unrestricted/excess cash or complete claims. |
| Retain accepted SBC once and historical tax roles | Cash43,369 vs provision20,719, difference22,650; no rate/proxy selected | No duplicate cost or tax charge; operating-tax/interest allocation unavailable, not a historical rate assumption. |
| Fiscal-end common snapshot; dated cover and RSUs separate | Cover +3,093,000 later-date shares; no RSU sum | Preserves dates/classes/precision; not diluted or valuation shares. |

## 7. Validation, preservation and stopping point

[Offline reporting helper](../../scripts/prepare_aapl_analyst_package.py) reuses
existing primary/instance identity, context, units, precision, confirming-occurrence
and arithmetic infrastructure. It does not call MSFT's financial selection logic.
Twelve recorded arithmetic/independent-parent checks include both lease
partitions/maturity bridges, term-debt bridge, financial parent, income/tax and
the complete displayed CFO. Source matching alone does not establish scope.
The normalization skill informed the source/decision separation and QA limits;
the explicitly requested Markdown/JSON format is retained.

Validation: **12 new focused tests (4.788s)** plus **44 relevant preservation
tests** pass (AAPL reported15 in2.563s, AAPL partial-NWC8 in2.248s, accepted
MSFT21 in7.947s). Tests pin literal statement values/ordinals, all confirmations,
source roles/precision, null requirements, proposed alternatives, conflicts,
date/dimension/unit/nil mismatches, exact replay and JSON round trips. All prior
tracked JSON/runtime files and the MSFT helper are byte-equal to starting HEAD;
AAPL and accepted MSFT package replay, compileall, **429 affected local links**
and `git diff --check` pass. No full-suite/corpus rerun or SEC requests.
Original receipts, registries, partial scenarios, frozen policies/
outputs, pilot bytes and the accepted MSFT package/view remain unchanged.
**Stop for one consolidated user review.** No acceptance, runtime integration,
support reclassification, Phase 1 closure, Phase 2 calculation or research chain.
