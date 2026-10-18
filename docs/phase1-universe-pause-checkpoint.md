# Phase 1 universe expansion — pause checkpoint and resumption handoff

## Authority and scope

**Universe analyst-review expansion is paused at the user's direction.** This is
its authoritative resumption/handoff document, anchored to
`2e12bf2679c3e96510c1de7cba51500bbae2b179` (the last implementation commit).
The user intends to begin Phase 2 in separately scoped chats and revisit unfinished
universe preparation later. This checkpoint changes documentation only: no new
financial selection, approval, valuation convention, engine or company review.

Three distinct milestones must not be conflated:

1. [Phase 1H.6 normalization-v1 freeze](historical-normalization-v1-freeze.md):
   completed with qualified coverage; schema 5, policies, outputs, classifications
   and original blockers remain frozen.
2. [Evidence-accounted preparation closure](phase1-preparation-closure-checklist.md):
   qualified facts/gaps traceability, not financial sufficiency or full fact-level
   verification. Later [technical delivery validation](phase1-delivery-acceptance-report.md)
   and independent samples retain their exact scope and limitations.
3. [Analyst-complete historical expansion](analyst-complete-historical-assessment.md):
   now paused with **24 completed scoped histories, 3 partial, 15 assessment-only**.
   This is neither full-universe completion nor closure of every Phase 1 obligation.

## Reconciled inventory and selected histories

The frozen snapshot contains 51 securities / 50 SEC issuers (GOOG/GOOGL share one
issuer). [Authoritative classifications](universe/phase-1h5-issuer-validation.json)
retain **42 non-specialized eligible issuers** and **8 specialized exclusions**:
**BRK-B, JPM, BAC, UNH, GE, GS, WFC, MS**. GE's retained generic outputs do not
approve generic use. No classification is changed.

**199 selected annuals / 210 five-period target slots; 11 deficits.** Completed
companies account for 120 selected annuals, partial packages 15, assessment-only
issuers 64. The original forty-generalization-required identity cohort has 189
annuals; adding the ten META/COST seed selections gives the full eligible 199.
The [repaired income ledger](repaired-income-ledger.json) supplies the exact
accessions/annual identities for all 199; the [assessment JSON](analyst-complete-historical-assessment.json)
retains the history inventory and proposed shared backlog, not today's approval
statuses. Current accepted package views/audits below determine those statuses;
older proposed/pending parent snapshots remain historical.

Tables give exact selected annual-end dates, not inferred calendar-year labels.
Each package links the current schedule and its machine-readable audit/effective
view; source identities, precision, units and evidence remain there.

### Completed scoped histories — 24 companies

| Issuer / authoritative record | Selected / target | Selected annual ends |
| --- | ---: | --- |
| [AAPL](company-data-preparation/AAPL-analyst-input-package.md) / [JSON](company-data-preparation/aapl-analyst-input-package.json) | 5/5 | 2021-09-25, 2022-09-24, 2023-09-30, 2024-09-28, 2025-09-27 |
| [ABBV](company-data-preparation/ABBV-analyst-input-package.md) / [JSON](company-data-preparation/abbv-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [AMAT](company-data-preparation/AMAT-analyst-input-package.md) / [JSON](company-data-preparation/amat-analyst-input-package.json) | 5/5 | 2021-10-31, 2022-10-30, 2023-10-29, 2024-10-27, 2025-10-26 |
| [AMD](company-data-preparation/AMD-analyst-input-package.md) / [JSON](company-data-preparation/amd-analyst-input-package.json) | 5/5 | 2021-12-25, 2022-12-31, 2023-12-30, 2024-12-28, 2025-12-27 |
| [AMZN](company-data-preparation/AMZN-analyst-input-package.md) / [JSON](company-data-preparation/amzn-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [AVGO](company-data-preparation/AVGO-analyst-input-package.md) / [JSON](company-data-preparation/avgo-analyst-input-package.json) | 5/5 | 2021-10-31, 2022-10-30, 2023-10-29, 2024-11-03, 2025-11-02 |
| [COST](company-data-preparation/COST-analyst-input-package.md) / [JSON](company-data-preparation/cost-analyst-input-package.json) | 5/5 | 2022-08-28, 2023-09-03, 2024-09-01, 2025-08-31, 2026-08-30 |
| [CSCO](company-data-preparation/CSCO-analyst-input-package.md) / [JSON](company-data-preparation/csco-analyst-input-package.json) | 5/5 | 2022-07-30, 2023-07-29, 2024-07-27, 2025-07-26, 2026-07-25 |
| [GOOGL](company-data-preparation/GOOGL-analyst-input-package.md) / [JSON](company-data-preparation/googl-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [INTC](company-data-preparation/INTC-analyst-input-package.md) / [JSON](company-data-preparation/intc-analyst-input-package.json) | 5/5 | 2021-12-25, 2022-12-31, 2023-12-30, 2024-12-28, 2025-12-27 |
| [KO](company-data-preparation/KO-analyst-input-package.md) / [JSON](company-data-preparation/ko-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [LLY](company-data-preparation/LLY-analyst-input-package.md) / [JSON](company-data-preparation/lly-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [LRCX](company-data-preparation/LRCX-analyst-input-package.md) / [JSON](company-data-preparation/lrcx-analyst-input-package.json) | 5/5 | 2022-06-26, 2023-06-25, 2024-06-30, 2025-06-29, 2026-06-28 |
| [MA](company-data-preparation/MA-analyst-input-package.md) / [JSON](company-data-preparation/ma-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [META](company-data-preparation/META-analyst-input-package.md) / [JSON](company-data-preparation/meta-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [MRK](company-data-preparation/MRK-analyst-input-package.md) / [JSON](company-data-preparation/mrk-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [MSFT](company-data-preparation/MSFT-analyst-input-package.md) / [JSON](company-data-preparation/msft-analyst-input-package.json) | 5/5 | 2022-06-30, 2023-06-30, 2024-06-30, 2025-06-30, 2026-06-30 |
| [MU](company-data-preparation/MU-analyst-input-package.md) / [JSON](company-data-preparation/mu-analyst-input-package.json) | 5/5 | 2022-09-01, 2023-08-31, 2024-08-29, 2025-08-28, 2026-09-03 |
| [NVDA](company-data-preparation/NVDA-analyst-input-package.md) / [JSON](company-data-preparation/nvda-analyst-input-package.json) | 5/5 | 2022-01-30, 2023-01-29, 2024-01-28, 2025-01-26, 2026-01-25 |
| [PG](company-data-preparation/PG-analyst-input-package.md) / [JSON](company-data-preparation/pg-analyst-input-package.json) | 5/5 | 2022-06-30, 2023-06-30, 2024-06-30, 2025-06-30, 2026-06-30 |
| [PLTR](company-data-preparation/PLTR-analyst-input-package.md) / [JSON](company-data-preparation/pltr-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [TSLA](company-data-preparation/TSLA-analyst-input-package.md) / [JSON](company-data-preparation/tsla-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [V](company-data-preparation/V-analyst-input-package.md) / [JSON](company-data-preparation/v-analyst-input-package.json) | 5/5 | 2021-09-30, 2022-09-30, 2023-09-30, 2024-09-30, 2025-09-30 |
| [WMT](company-data-preparation/WMT-analyst-input-package.md) / [JSON](company-data-preparation/wmt-analyst-input-package.json) | 5/5 | 2022-01-31, 2023-01-31, 2024-01-31, 2025-01-31, 2026-01-31 |

### Partial approved packages — 3 companies

| Issuer / authoritative record | Selected / target | Selected annual ends |
| --- | ---: | --- |
| [CAT](company-data-preparation/CAT-analyst-input-package.md) / [JSON](company-data-preparation/cat-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [CVX](company-data-preparation/CVX-analyst-input-package.md) / [JSON](company-data-preparation/cvx-analyst-input-package.json) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [JNJ](company-data-preparation/JNJ-analyst-input-package.md) / [JSON](company-data-preparation/jnj-analyst-input-package.json) | 5/5 | 2022-01-02, 2023-01-01, 2023-12-31, 2024-12-29, 2025-12-28 |

### Assessment-only issuers — 15 companies

| Issuer / authoritative record | Selected / target | Selected annual ends |
| --- | ---: | --- |
| [GEV](company-data-preparation/GEV.md) | 2/5 | 2024-12-31, 2025-12-31 |
| [HD](company-data-preparation/HD.md) | 5/5 | 2022-01-30, 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01 |
| [IBM](company-data-preparation/IBM.md) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [KLAC](company-data-preparation/KLAC.md) | 5/5 | 2022-06-30, 2023-06-30, 2024-06-30, 2025-06-30, 2026-06-30 |
| [LIN](company-data-preparation/LIN.md) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [MCD](company-data-preparation/MCD.md) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [NFLX](company-data-preparation/NFLX.md) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [ORCL](company-data-preparation/ORCL.md) | 5/5 | 2022-05-31, 2023-05-31, 2024-05-31, 2025-05-31, 2026-05-31 |
| [PEP](company-data-preparation/PEP.md) | 5/5 | 2021-12-25, 2022-12-31, 2023-12-30, 2024-12-28, 2025-12-27 |
| [PM](company-data-preparation/PM.md) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [QCOM](company-data-preparation/QCOM.md) | 5/5 | 2021-09-26, 2022-09-25, 2023-09-24, 2024-09-29, 2025-09-28 |
| [SNDK](company-data-preparation/SNDK.md) | 2/5 | 2025-06-27, 2026-07-03 |
| [TXN](company-data-preparation/TXN.md) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [VZ](company-data-preparation/VZ.md) | 5/5 | 2021-12-31, 2022-12-31, 2023-12-31, 2024-12-31, 2025-12-31 |
| [XOM](company-data-preparation/XOM.md) | 0/5 | None — frozen empty history |

Completed means all five selected years satisfy the existing 14-family historical
checklist **under each company's approved perimeter, proxies and assumptions**.
It does not mean every possible component is disclosed, all expense D&A verified,
or an exhaustive debt/reinvestment/equity bridge is established. Partial CAT is
one company, not two additional issuers for its industrial/Financial Products
perimeters. Assessment-only means retained preparation evidence exists at its
stated depth, not a company-wide analyst approval or permission to infer values.

## Accepted methodology and controls to carry forward

The [historical-input contract](dcf-input-contract.md) remains authoritative for
fields and operation-specific requirements. Detailed company choices stay in the
linked schedules/audits; the [latest accepted batch](energy-pharma-staples-review-batch-results.md)
records MRK/PG completion and CVX's retained essential exception.

- **Origins remain separate:** SEC-reported facts, source-supported derivations,
  limited analyst proxies, approved assumptions, manual-note observations and
  unavailable inputs retain source/period identity, precision, role and scope.
  Origin is not a calibrated confidence score. Acceptance never turns a null into
  a reported zero or an unknown into an immaterial item.
- **Active historical path:** reported cash-flow movement rows and independently
  reconciled CFO. Complete reconstructed historical NWC/book ΔNWC is **not a
  prerequisite** for this path; existing book schedules remain supporting history.
  Movement rows already included in CFO are not deducted again. Cash movements
  are not book changes or operating-only cash ΔNWC. CFO is not FCFF; mixed rows,
  partial/failed parser results and independent displayed checks remain distinct.
- **D&A/investment:** accepted company/year-specific expense selections or limited
  reconciliation proxies retain impairment, depletion, lease and acquisition
  scope/comparability labels. Proxy acceptance does not prove complete expense
  D&A; no residual amortization, automatic ROU add-back or universal overlap rule.
  Cash PP&E, broader combined investment proxies, acquisitions/IPR&D, incentives,
  capital creditors and noncash additions remain separately identified. Prior
  pure-PP&E negative findings are not reversed by accepting a broader proxy.
- **Financing/claims:** named carrying populations, current maturities, CP and
  embedded lease amounts retain non-overlap safeguards. Approved unidentified
  borrowing/claim omissions are analyst assumptions, not exhaustive totals,
  reported zeros or immateriality findings; omitted amounts can be unbounded.
  Known claims, funding/plan assets, NCI and preferred populations stay visible.
- **Financial balances:** gross current or explicitly restriction-adjusted balances
  retain restrictions, reserves, strategic/equity-method holdings and alternatives;
  never automatically unrestricted/excess cash. No automatic bridge netting.
- **Tax/SBC/shares:** historical provision, pretax, reported ETR, deferred-tax
  reconciliation and cash taxes remain different roles. SBC expense/proxy is
  counted once, separate from CFO add-backs, capitalized awards and cash payments;
  precision differences are not adjustments. Share dates/classes, independent
  aggregates, EPS denominators, awards and split boundaries are not interchangeable.
  Forecast tax, award value and dilution are not selected by historical acceptance.
- **Comparability:** accession-specific acquisitions, disposals/separations,
  fiscal calendars and original-as-filed versus recast presentations remain
  explicit. No silent historical splice or transferred issuer-specific assumption.
- **Approval controls:** reuse existing revision-bound audits, supersession history,
  source/proposal hashes, actual author/UTC and stale-input rejection. Original
  facts/proposals/nulls and refreshed-evidence history stay intact. Any later
  preparation change maintains affected issuer records and the register in the
  same milestone, per [AGENTS.md](../AGENTS.md).

Completion under an approved historical perimeter does **not** automatically
certify a valuation consumer. Evidence-accounted preparation and financial-input
sufficiency for a named consumer remain separately assessed statuses.

## Exact unfinished work — retained, not launched

| Population | Open work and resumption boundary |
| --- | --- |
| CAT FY2021–FY2025 | Both approved industrial and Financial Products perimeters remain **13/14 each year**: SBC expense allocation is essential. Consolidated expense is support, supplemental Other is not a pure allocation. Require direct scoped evidence or an explicitly justified approved treatment; no revenue allocation, all-to-industrial default or consolidated substitution. Eliminations remain separate supporting columns, not standalone figures. See [CAT current schedule](company-data-preparation/CAT-analyst-input-package.md). |
| JNJ FY2021–FY2025 | **5/14 each year; 45 family-period requirements open.** Original FY2021/22 Consumer Health-inclusive income versus later continuing income cannot be assumed coterminous with consolidated cash/D&A/tax/investment. Affected families: Revenue, EBIT, D&A, cash investment, cash-flow working-capital movements, deferred taxes, SBC, CFO and reported tax context. Need evidence-bound scope allocations/cross-year bridge or separately justified approved analyst-use treatment; no silent recast splice. Exact identities/requirements: [JNJ current view](company-data-preparation/jnj-analyst-input-package.json) `/current_history/open_analyst_use_requirements`. |
| CVX FY2021–FY2025 | **13/14 each year; five required EBIT values remain null.** Mixed-tax affiliates, operating/nonoperating Other and incomplete benefit allocations leave the operating-business perimeter unproved. Prior negative findings prohibit substitute pretax-plus-interest, after-tax segment totals, expressionC or a zero/waiver without a new justified decision. Accepted Sales/DD&A/Capex do not solve EBIT. See [CVX package](company-data-preparation/CVX-analyst-input-package.md). |
| 15 assessment-only companies | HD, IBM, KLAC, LIN, MCD, NFLX, ORCL, PEP, PM, QCOM, TXN, VZ, GEV, SNDK and XOM have no completed company-wide analyst review. Their exact histories and record links are above. Source observations/field ledgers are not approvals. |
| XOM | Empty current-CIK frozen selection: **0/5, five deficits**. This is not proof that the issuer lacks historical operations. No predecessor identity, annual date or period is inferred. |
| GEV / SNDK | **2/5 each, three deficits each**. Standalone/carve-out histories and predecessor comparability remain bounded exceptions; the unfilled slots are not proved nonexistent business years. No invented dates/periods or automatic predecessor expansion. |

The target remains five annual periods: **XOM 5 + GEV 3 + SNDK 3 = 11 deficits**,
not eleven newly populated, waived or accepted slots. Specialized methodologies
remain excluded from this ordinary-company path, not abandoned or certified.

When the user resumes universe work, the existing next standard-review candidates
are **PM, HD, NFLX** (five retained exact selections each), then the remaining
[documented company/shared-task backlog](analyst-complete-historical-assessment.md)
and [machine backlog](analyst-complete-historical-assessment.json). This is a
resumption pointer, not an automatic queue or new timetable. Preserve exhausted
searches and negative scope/evidence findings in the company records; reopen only
with a defined new evidence basis or explicit methodological decision. No further
acquisition, review, repair or financial acceptance is authorized by this pause.

## Phase 2 handoff — future separately scoped work

Start with **one company and one traceable Base-case valuation**, choosing the
company and valuation-use perimeter explicitly in the future chat. Do not assume
all 24 completed histories are interchangeable or that full-universe completion
is a prerequisite to that separately scoped implementation.

Reuse the existing immutable [manual-assumption models](architecture.md#valuation-assumptions-boundary)
and their explicit input/serialization validation. They are not a forecasting or
valuation engine. Forecasting, FCFF construction, discounting, terminal value,
and the equity/share bridge remain future implementation; tax, lease, SBC,
working-capital, claims and share-consumption conventions require explicit design.
No Base-case numerical assumptions, detailed economic convention or engine are
approved here. Historical-input acceptance and valuation-use decisions must stay
separately identifiable, traceable to source and analyst approvals.

The older [timing/readiness design](financial-timing-readiness-design.md),
[financial methodology](financial-methodology.md) and
[delivery-acceptance obligations](phase1-delivery-acceptance-report.md) must be
reconciled with the newer approved reported-movement/manual-forecast approach
when specifying that consumer. Do **not** silently reinstate complete historical
NWC reconstruction as a universal prerequisite. Equally, do not assume CFO/movement
availability resolves EBIT/tax/investment timing, financial bridges, overlap or
forecast-consistency questions. Retained historical obligations must be explicitly
resolved, made inapplicable with rationale, or carried forward—not silently waived.
The older universal Phase 2 postponement records describe earlier milestones;
the current direction permits separately requested Phase 2 planning/implementation,
not implementation in this documentation checkpoint.

## Checkpoint validation and resumption procedure

Documentation-only reconciliation at the anchor commit:

- 42 unique eligible issuer/CIK mappings plus 8 specialized exclusions match the
  frozen classification artifact; GOOG/GOOGL are not double-counted.
- 199 unique selected issuer/accession/annual identities match the retained income
  ledger and 42-row history inventory; all 27 package current-view identities agree.
- 24 completed / 3 partial / 15 assessment-only reconcile to 42; their selected
  annual counts are 120 / 15 / 64. All 24 complete views pass their recorded 70/70
  scoped checklist; CAT/JNJ/CVX retain their existing essential requirements.
- 210 target slots minus 199 selected equals 11; exact XOM/GEV/SNDK exceptions
  retain null missing-period identities, without inventing unavailable history.
- **96 added local links/anchors PASS**; relevant schema/policy references and
  `git diff --check` PASS. Exactly eight Markdown files changed (this checkpoint
  plus seven current-guidance documents).
  Source/code/tests/registries, package JSON/audits, financial selections, retained
  evidence, pilot bytes and frozen outputs are unchanged. No financial tests,
  full suite, corpus rerun, compilation or network requests are needed or run.
  Prior executable validation remains in the linked batch results; it is not
  presented as a newly executed test run for this checkpoint.

On resumption: read this document, AGENTS.md and the relevant current package/audit;
verify actual Git state; preserve unrelated work; select one explicitly authorized
scope. Universe review remains paused until requested. This document creates no
new chat, implementation job, research task or automatic financial acceptance.
