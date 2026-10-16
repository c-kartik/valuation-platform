# Analyst-complete historical inputs — retained-evidence completion assessment

Baseline `46a0b5729887e1b5fc2b54fafe840578f4c3abb7`; Phase 1 only.
[Machine assessment](analyst-complete-historical-assessment.json) and
[bounded replay/check helper](../scripts/assess_analyst_completion.py) join existing
records, fourteen-field coverage and exact displayed-population ledgers. This is
planning, not new source research, a financial approval or an executed backlog.

## Standard, scope and what is actually known

**Analyst-complete:** every required input has an evidenced reported/derived
selection, a defensible explicitly approved estimate/classification, or an approved
methodological exclusion that genuinely makes it unnecessary. Basis, scope,
uncertainty and provenance must survive. Acknowledging missing data or approving
a partial population is **not** such an exclusion. CFO alone is not completeness.
The [input contract](dcf-input-contract.md) is the field inventory; proposed
perimeter decisions below do not weaken it. A consumer-specific sufficiency gate
before valuation remains separate; no forecasts, WACC, terminal value or valuation.

**Zero of 42 issuers have demonstrated analyst completeness**, latest or full
available history. This means not established, not that every reported number is
wrong or every company impossible. All eight specialized issuers, including GE,
remain excluded. META/COST's frozen SUPPORTED classification is unchanged and is
not analyst-package completeness. No new specialized escalation is established.

Reconciliation: **42 histories; 199 selected annuals; 210 five-year target slots;
11 deficits; 2,786 selected field-family slots**. The prior40-company register has
189 periods; supported seeds META/COST add ten. Forty-one have a latest selected
period; XOM has none. Recent denominators remain121 selected/126 target, older
78/84. Proposed90%/80% targets are unchanged and do not meet this stricter binary
completion definition or waive required values.

Missing target history must not be called unavailable pre-existence history:

- XOM: zero current-CIK selected annuals, five deficits. This is not proof the
  business did not exist; current-registrant/predecessor continuity is unestablished.
- GEV/SNDK: two selected annuals each, three deficits each. Standalone/carve-out
  and predecessor comparability boundaries are documented, not five reconstructed
  years. The count of *proved nonexistent* business years remains unknown, not3.
- No missing slot receives an invented accession, fiscal date or zero.

Sources: [current delivery acceptance](phase1-delivery-acceptance-report.md),
[coverage](preparation-coverage-results.json), [assembly summary](prepared-assembly-summary.json),
[exact populations/CFO proofs](reported-population-delivery-ledger.json),
[frozen issuer mapping](universe/phase-1h5-issuer-validation.json),
[prior disposition](phase1-issuer-preparation-disposition.json) and
[consolidated pilot assessment](phase1-preparation-pilot-gap-assessment.md).
The companion pins source SHA256s, all42 issuer records and exact row pointers.
Current coverage flags may coexist with valid component values or null requirement
placeholders. They do not by themselves prove absent disclosure, numerical error,
or a repository defect. The old disposition/research routing is historical; later
approved ledgers and scoped decisions take precedence without rewriting history.

## Work groups and prioritization

| Readiness/effort planning band | Issuers | Reason, not a missing-field score |
| --- | ---: | --- |
| F — approved partial pilot / focused hard gaps | 3 | Existing company review and audits reduce setup; specific undisclosed allocations and scope remain. |
| S — retained standard-review candidate | 9 | No latest scalar absence/conflict flagged by this screen and all displayed CFO checks supported; bridge, expense/perimeter and company approval still required. |
| C — complex selection review | 27 | Latest scalar null/scope or component conflict, or some partial/failed CFO check; exact period/field proofs determine work. |
| H — history boundary | 3 | Empty or short history adds an independent comparability/selection prerequisite. |

Priority favors existing reviewed packages and reusable decision controls, then S
before C, H last. Within S/C ranks are alphabetical ties, **not** a claim that one
company is financially closer. F is an informed integration-leverage priority,
not an assurance it will complete sooner than S. Independent full financial review
of the other39 has not occurred. No information-only diagnostic is counted as a
new repair; the JSON preserves exact substantive flags and source limitations.

## All42 issuer work inventory

Latest/full review days below are **low/base/high financial-review person-days**,
not promised completion dates. S/C/F definitions and shared dependencies below
apply to every row. The companion accounts separately for each of14 families,
exact selected periods, current ledger null/conflict/support counts and original
frozen blockers. In the table, “DA/Capex/etc.” means an exact latest ledger
requirement, not that no useful observation exists. Every row also requires S0/S1
and financial-population/tax/share/claim disposition before completeness.

| Rank / issuer | Available / target; latest | Reviewed analyst periods | Band; latest / full review days | Specific retained prioritization flags (all other requirements in JSON) |
| --- | --- | --- | --- | --- |
| 1 / [MSFT](company-data-preparation/MSFT.md) | 5/5; 2026-06-30 | 2025-06-30,2026-06-30 (partial only) | F; 2/4/8 / 8/16/30 | named partial scopes/unknowns remain |
| 2 / [AAPL](company-data-preparation/AAPL.md) | 5/5; 2025-09-27 | 2025-09-27 (partial only) | F; 2/4/8 / 8/16/30 | named partial scopes/unknowns remain |
| 3 / [GOOGL](company-data-preparation/GOOGL.md) | 5/5; 2025-12-31 | 2024-12-31 (partial only) | F; 2/4/8 / 8/16/30 | DA required null; cash conflict; named partial scopes/unknowns remain |
| 4 / [CAT](company-data-preparation/CAT.md) | 5/5; 2025-12-31 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 5 / [COST](company-data-preparation/supported-seeds/COST.md) | 5/5; 2026-08-30 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 6 / [JNJ](company-data-preparation/JNJ.md) | 5/5; 2025-12-28 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 7 / [KO](company-data-preparation/KO.md) | 5/5; 2025-12-31 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 8 / [LLY](company-data-preparation/LLY.md) | 5/5; 2025-12-31 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 9 / [MU](company-data-preparation/MU.md) | 5/5; 2026-09-03 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 10 / [PG](company-data-preparation/PG.md) | 5/5; 2026-06-30 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 11 / [PM](company-data-preparation/PM.md) | 5/5; 2025-12-31 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 12 / [V](company-data-preparation/V.md) | 5/5; 2025-09-30 | none | S; 2/4/7 / 6/12/22 | No screened latest scalar hard flag; bridge/role/completeness decisions unreviewed |
| 13 / [ABBV](company-data-preparation/ABBV.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null; claims conflict |
| 14 / [AMAT](company-data-preparation/AMAT.md) | 5/5; 2025-10-26 | none | C; 4/8/15 / 12/25/45 | DA required null |
| 15 / [AMD](company-data-preparation/AMD.md) | 5/5; 2025-12-27 | none | C; 4/8/15 / 12/25/45 | DA required null; claims conflict; CFO 2 partial/0 failed across history |
| 16 / [AMZN](company-data-preparation/AMZN.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null; tax conflict |
| 17 / [AVGO](company-data-preparation/AVGO.md) | 5/5; 2025-11-02 | none | C; 4/8/15 / 12/25/45 | DA required null |
| 18 / [CSCO](company-data-preparation/CSCO.md) | 5/5; 2026-07-25 | none | C; 4/8/15 / 12/25/45 | debt conflict |
| 19 / [CVX](company-data-preparation/CVX.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | Revenue required null; Revenue conflict; EBIT required null |
| 20 / [HD](company-data-preparation/HD.md) | 5/5; 2026-02-01 | none | C; 4/8/15 / 12/25/45 | DA required null; Capex required null |
| 21 / [IBM](company-data-preparation/IBM.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null |
| 22 / [INTC](company-data-preparation/INTC.md) | 5/5; 2025-12-27 | none | C; 4/8/15 / 12/25/45 | DA required null; SBC conflict; debt conflict |
| 23 / [KLAC](company-data-preparation/KLAC.md) | 5/5; 2026-06-30 | none | C; 4/8/15 / 12/25/45 | claims conflict |
| 24 / [LIN](company-data-preparation/LIN.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null; CFO 5 partial/0 failed across history |
| 25 / [LRCX](company-data-preparation/LRCX.md) | 5/5; 2026-06-28 | none | C; 4/8/15 / 12/25/45 | DA required null; Capex required null |
| 26 / [MA](company-data-preparation/MA.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null |
| 27 / [MCD](company-data-preparation/MCD.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | debt conflict; CFO 0 partial/1 failed across history |
| 28 / [META](company-data-preparation/supported-seeds/META.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | claims conflict; CFO 3 partial/0 failed across history |
| 29 / [MRK](company-data-preparation/MRK.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null; CFO 5 partial/0 failed across history |
| 30 / [NFLX](company-data-preparation/NFLX.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | claims conflict |
| 31 / [NVDA](company-data-preparation/NVDA.md) | 5/5; 2026-01-25 | none | C; 4/8/15 / 12/25/45 | Capex required null; claims conflict |
| 32 / [ORCL](company-data-preparation/ORCL.md) | 5/5; 2026-05-31 | none | C; 4/8/15 / 12/25/45 | DA required null; claims conflict |
| 33 / [PEP](company-data-preparation/PEP.md) | 5/5; 2025-12-27 | none | C; 4/8/15 / 12/25/45 | Capex required null |
| 34 / [PLTR](company-data-preparation/PLTR.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | tax conflict; claims conflict; CFO 4 partial/0 failed across history |
| 35 / [QCOM](company-data-preparation/QCOM.md) | 5/5; 2025-09-28 | none | C; 4/8/15 / 12/25/45 | Capex required null; CFO 4 partial/0 failed across history |
| 36 / [TSLA](company-data-preparation/TSLA.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null; tax conflict; claims conflict |
| 37 / [TXN](company-data-preparation/TXN.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null; debt conflict |
| 38 / [VZ](company-data-preparation/VZ.md) | 5/5; 2025-12-31 | none | C; 4/8/15 / 12/25/45 | DA required null; Capex required null; claims conflict |
| 39 / [WMT](company-data-preparation/WMT.md) | 5/5; 2026-01-31 | none | C; 4/8/15 / 12/25/45 | Revenue required null; Revenue conflict; DA required null; SBC conflict; cash conflict; debt conflict; claims conflict |
| 40 / [GEV](company-data-preparation/GEV.md) | 2/5; 2025-12-31 | none | H; 4/8/15 / 6/12/22 | DA required null; Capex required null; 3 history deficits; not proved nonexistent years |
| 41 / [SNDK](company-data-preparation/SNDK.md) | 2/5; 2026-07-03 | none | H; 4/8/15 / 6/12/22 | DA required null; CFO 1 partial/0 failed across history; 3 history deficits; not proved nonexistent years |
| 42 / [XOM](company-data-preparation/XOM.md) | 0/5; none | none | H; not estimable / not estimable | 5 history deficits; not proved nonexistent years |

## Shared work — perform once, apply only to evidenced cases

| ID / work category | Bounded deliverable, dependency and acceptance | Beneficiaries / stop |
| --- | --- | --- |
| S0 company-specific financial selection | One required-perimeter checklist, then explicit company decisions: why each field is needed or genuinely excluded; defensible assumptions need author, basis, scope and uncertainty. No mathematical/economic execution. | All42; no exclusion merely because data are missing. Stop incomplete without defensible basis. |
| S1 reusable mapping/evidence repair + package/audit integration | Reuse existing adapters/audits after S0; fix only demonstrated exact joins/mappings, serialize selections and reject stale revisions/dependencies. | 41 selected histories; XOM depends on identity/history first. No new generic framework or blanket extraction. |
| S2 company income selection/conflicts | Resolve11 income conflicts (WMT5, CVX5, MA1) and five unregistered CVX EBIT gaps using actual scope; retain approved derivation operands. | Review all41, target these exact cases first. No precedence-only selection or invented equation. |
| S3 company D&A classification / analyst decision | Required expense scope versus CFO support, lease/inventory timing and combined captions; preserve seven negative reviews. An approved assumption remains an assumption. | All41 require review, not all require a repair. No residual amortization, unproved sum or automatic registry expansion. |
| S4 unavailable allocation / justified alternative | Approved cash Capex is a narrow purchase input; resolve required PP&E/software/acquisition/intangible/creditor/noncash perimeter. | All41; 34 unapproved generic Capex cases remain specific scope gaps, not receipt defects. Stop if broader required allocation cannot be supported. |
| S5 CFO/movement/SBC/deferred-tax/tax role decisions | Exact signed rows, parents/children, acquisition/FX/noncurrent limits, SBC once, historical provision/pretax/ETR versus cash. Remainder only if required, unclassified and source-bound. | All41; 174 supported/24 partial/1 failed displayed checks. MCD2024 remains9,446m versus9,447m, outside0.6m. No plug/tolerance change. |
| S6 financial selections + analyst assumption where justified | Cash/current/LT/restricted/strategic, term/CP/leases and carrying/principal/fair value, claims/NCI inclusion, actual dated/classed shares. | All41. Narrow liquidity46, shares162, finance92/operating186 selections; borrowing43 observations/33 periods **not** complete debt. Unknown is not zero. |
| S7 history/comparability boundary | After one-period success, verify remaining annuals independently, including opening/closing, acquisitions, FX, reclassifications and source/timing differences. | All42 need history disposition. Five-year target not silently reduced; no predecessor reconstruction or transfer of four pilot approvals. |

The JSON defines each task exactly once, benefiting issuers, dependencies,
acceptance test and stop condition. Per-field requirements reference those tasks,
not42 duplicate engineering projects. Repairable extraction/evidence defects are
**conditional on exact diagnostic confirmation**; this assessment found no new
demonstrated runtime defect. Unavailable reviewed disclosures and analyst choices
are not relabeled engineering bugs. Any specialized escalation needs specific new
evidence and separate authorization, not an automatic change to classification.

## Pilot gaps — approvals do not complete even the approved periods

| Issuer / approved exact periods | Selected / approved / assumption-dependent | Still preventing a complete required-input package |
| --- | --- | --- |
| MSFT FY2025–2026 | Named partial operating capital−25,755/−18,600m (includes noncurrent), book movement+7,155m; rounded D&A28,000/39,000 with **accepted but unproved finance-amortization inclusion assumption**; named financing89,323/106,888m, cash less identified restrictions94,565/73,043m. Residual-caption estimate is non-default. | FY2026 extra short borrowing **null**, zero proposal rejected. Required complete financing/claims/cash-availability populations unproved; facilitation/mixed operating allocations, investment/acquisition allocation and all-interest/lease coverage unavailable. CFO-to-EBIT/timing comparability unproved. Which allocations are genuinely unnecessary for the approved historical path requires S0 decision, not CFO availability alone. |
| AAPL FY2025 only | Partial current operating capital−9,159m includes identified distribution8,919m; finance99,887m only; current54,697m/LT securities77,723m separate; dated common shares selected. | Required expense D&A null (CFO11,698 versus depreciation8,000R not a bridge); employee/capital-creditor/mixed allocations unknown. Cash interest/full lease coverage/acquisition allocation absent; restrictions/claims not exhaustively accounted. No approved proxy for these gaps; no book/cash movement. |
| Alphabet FY2024 only; latest selected FY2025 **not approved** | Partial current operating capital13,342R includes manual-note3,200R; named financing15,859m; current financial95,657m. SBC22,800R once vs add-back22,785; dated classes/source aggregate retained. | Expense D&A null (CFO15,311/finance413 separate); inventory/supplier AP/other allocations unknown, cash borrowing interest and broader lease/investment coverage absent. Precision alternatives, restricted/strategic populations and claims need required-perimeter decisions. NCI4,200 includes1,100, not5,300. No opening/ΔNWC. Explicit refreshed receipt does not recover original metadata. |

Exact package/audit references and every original null reason are retained in JSON.
Some old nulls concern future operating taxes, award valuation, dilution or an
integrated valuation gate: these **economic calculations stay Phase2**, not new
historical requirements. Conversely historical financing/expense/investment scope
cannot be called complete simply by postponing all economic use. S0 must decide
necessity individually. Source uncertainty, approved classification and future
model choice remain distinct. All original frozen NWC/D&A/etc. blockers persist.
Excess-cash valuation, combined net debt and forecast diluted shares are not
new Phase1 requirements. Required reported populations still need justified
coverage: neither a broad valuation demand nor a narrow label can settle that
question automatically. Any CFO-path exclusion of book-NWC reconstruction needs
an independently evidenced coherent movement perimeter, not merely a subtotal.

### Requirements not presently meetable with an established alternative

No defensible approved alternative currently fills the pilot unavailable cash
interest/allocations or AAPL/Alphabet complete expense D&A; MSFT extra2026 short
borrowing remains unknown. Their necessity is not automatically waived. XOM's
selected history and GEV/SNDK's five-year standalone/comparable series cannot be
provided from current scope. MCD2024 cannot presently be certified reconciled.
These are completion blockers **where required**, not findings of immateriality.
No all42 completion date is defensible until evidence/alternatives are established.
Stopping incomplete is permissible; calling acknowledged gaps complete is not.

## Conditional effort, cadence and finite batches

These are uncalibrated planning budgets based on **tasks**, not calibrated
confidence scores, SEC request estimates or a forced6–12-week promise. A standard
latest review budgets roughly half a day income/D&A, half investment, one day
CFO/tax/SBC/movements, one day bridge/claims, half shares and half review/audit
signoff (base4). Complex base8 allows two scoped passes for conflicting/missing
expense/investment or reconciliation evidence; full-history base12/25 amortizes
company setup but still verifies each selected period. Pilot base4 assumes setup
already exists but does not assume missing disclosures solvable. These allocations
are proposed labor budgets, not empirical timing measurements. Confidence is LOW
on completion feasibility; pilot task boundaries are better known, not guaranteed.

| Hands-on work, person-days low / base / high | Latest selected attempt (41 issuers) | Full available-history attempt (199 annuals) |
| --- | ---: | ---: |
| Shared engineering, once | 8 / 15 / 25 | Same8 / 15 / 25, not charged again |
| Company package/decision integration engineering | 34 / 68 / 136 | 68 / 136 / 245 |
| Financial review and preparation of user decisions | 140 / 280 / 522 | 414 / 855 / 1,547 |
| External evidence availability and user response time | **Not estimable** | **Not estimable** |

Full-history column is an alternative total, **not** added on top of latest.
XOM numerical review is excluded from these labor sums because no period exists;
its future scope cannot be costed. GEV/SNDK cover available annuals only, not
fabricated target years. No external retrieval is authorized by these budgets.
Engineering includes future specifically authorized package integration/tests,
not a new platform build; discovery of a new technical contract changes the budget.

Illustrative cadence: one engineer at4 focused days/week and two qualified
financial reviewers at4 days/week each, with one consolidated user decision
session weekly. With shared work reused, engineering latest workload42/83/161
days is10.5/20.75/40.25 engineer-weeks; financial latest140/280/522 days is
17.5/35/65.25 review-team weeks. Full available-history financial effort is
51.75/106.875/193.375 review-team weeks; engineering is19/37.75/67.5 weeks.
These are capacity conversions, **not elapsed delivery forecasts**: tasks depend
on S0/approvals, staff availability, access to missing evidence and successful
alternatives. More reviewers may increase throughput but not resolve unavailable
disclosures. With a single reviewer the financial-work weeks double. All42
analyst completion and210-slot target completion remain **not estimable**.

**First recommended finite completion batch: MSFT FY2026 only.** Reuse its
accepted view; resolve the exact short-borrowing null and required claims/cash/
investment/expense perimeter through defensible evidence or an explicitly approved
alternative/exclusion. Do not reopen settled approvals or pick zero. Acceptance:
all required historical fields populated or genuinely unnecessary under an
approved reason; original facts, assumptions and exclusions separately auditable;
source/overlap/arithmetic tests and persisted/stale-source controls pass. Base
budget4 financial-review days +1 integration day, range2–8 +0.5–2, plus its share
of shared work and unbounded decision/evidence wait. Stop after one retained review
with either complete exact-period checklist or precise INCOMPLETE disposition.
This may fail; no fresh research chain is authorized.

Then, **only if separately authorized**:

1. B1: MSFT2025, AAPL2025, Alphabet2024 as one review batch; independently solve
   their hard gaps, not copy MSFT assumptions. Then B1-LATEST is one separate
   Alphabet2025 attempt before full-history extension. No company history
   completed by these approvals alone.
2. Nine S issuers in three groups of three; use shared controls and identical
   decision-sheet structure, independent financial treatments. C issuers in nine
   groups of three follow, prioritizing shared D&A/Capex and income/CFO causes.
   Exact targets are in JSON; Alphabet2025 remains separate from its2024 approval.
3. GEV/SNDK available histories and XOM selection boundary receive a finite
   history decision, not predecessor research. HISTORY-AVAILABLE attempts the
   two latest selected GEV/SNDK periods only after that boundary decision.
   Extend other available histories
   only after latest-period success, in the same groups. Stop on incompatible
   perimeter or required unavailable input with no defensible alternative.

User decisions needed: authorize/decline B0 and its strict acceptance standard;
approve any **specific** defensible historical assumptions/exclusions only after
their basis and uncertainty are presented; decide admissible history boundaries
without pretending the five-year target is met. Existing90%/80% shortfall
acceptance would qualify delivery, **not** make required gaps analyst-complete.
Future tax rates, dilution/award valuation and valuation calculations remain out
of scope. This assessment approves nothing and closes no phase.

## Reproducibility and validation

The helper joins committed machine results, never source-extracts or builds
cohort bundles. It validates42 unique CIK/ticker mappings,199 exact selected
accessions,210 target/11 deficits,2,786 field slots, four scoped approved periods,
all source pointers and deduplicated shared task IDs. Focused tests check replay,
history versus pre-existence, pilot non-extension, null short debt, failed CFO,
reference rejection and exact baseline source/accepted-view preservation.
No financial conclusion is strengthened by these technical checks. Issuer records
are unchanged: no new issuer financial fact, treatment or correction was found;
this planning assessment links their existing evidence and flags unreviewed work.
No SEC requests, full-suite/corpus rerun, source/policy changes or backlog execution.

Verified assessment result: **five focused tests pass (2.303s)**; exact offline
assessment replay, source-pointer resolution, unique identity/field/batch accounting,
baseline source/accepted-view digest preservation, compileall, **406 affected local
links** and `git diff --check` pass. The initial test invocation exposed a test-only
lookup using `value` instead of the existing `value_usd` null key; the test was
corrected to the unchanged source schema, without changing financial data or
asserted null behavior. No financial/source review or full-suite run is claimed.
