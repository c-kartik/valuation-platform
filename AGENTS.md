# AGENTS.md

## Parallel browser engine — November 5, 2026

The user authorizes a parallel JavaScript/TypeScript valuation engine and static
portfolio integration, with the existing Python pipeline left untouched and
available for switching back. Do not replace Python acquisition/normalization,
change its source or financial policies, or retire GCP under this migration.
The user explicitly approves keeping SEC/data refresh in Python permanently,
run manually on the laptop. Export reviewed data to the static JavaScript site;
no Node.js rewrite of that pipeline or hosted refresh service is required.
The ordinary frontend build retains Python/API execution; `build:browser` fixes
execution to the browser without an automatic backend fallback. See
`docs/browser-engine-migration.md` for parity evidence, static dataset refresh,
release prerequisites and remaining hosting access work. Wider issuer expansion
and new financial conventions remain outside this engineering migration.

## Project

Automated Equity Valuation Platform.

The application will accept a US stock ticker, retrieve and normalize historical financial data primarily from SEC EDGAR/XBRL, accept manual forecast assumptions, and calculate an FCFF DCF.

The Phase 1H validation universe includes every security in the frozen
S&P 500 Top 50 Index snapshot at
`docs/universe/sp500-top-50-2026-10-02.csv`. Record and classify every
constituent; do not omit financial or other specialized companies. The current
generic methodology initially supports ordinary operating companies. Classify
banks, insurers, REITs, and other structures that need dedicated treatment as
`SPECIALIZED_METHODOLOGY_REQUIRED` rather than forcing them through the
operating-company FCFF model.

## Cloud/mobile development

The user authorizes Codex Cloud setup and GitHub synchronization. Start with
`docs/codex-cloud.md` and `docs/cloud-work-handoff.md`. Use the portable setup,
verification and supervised loopback startup under `scripts/cloud/`. The original
42-company audit is a hash-verified snapshot restored into ignored `.cloud/`;
current company-resolution decisions supersede only their named historical scope.
Cloud setup does not approve new financial values, broader-universe work or a
public production deployment. Keep the environment owner-private. Never commit
personal credentials or infer missing inputs from the old audit.

## Current Phase

Phase 1 universe analyst-review expansion is **paused** at the user's direction.
The authoritative resumption/handoff is
`docs/phase1-universe-pause-checkpoint.md`: 24 completed scoped histories,
3 partial (CAT/JNJ/CVX), 15 assessment-only; 199 selected annuals and 11 target
deficits remain. Preserve unfinished work and do not automatically resume reviews.
The user intends Phase 2 in separate chats, starting with one company and a
traceable Base case; this checkpoint authorizes no engine or economic convention.
Future Phase 2 work requires its own explicit scope and valuation-use decisions.

Phase 1H expands the operational Python SEC/XBRL historical pipeline from the
five-company validation corpus (META, GOOGL, MSFT, AAPL, and COST) to a defined
S&P 500 Top 50 snapshot. Use corpus failures to improve normalization
architecture and policies without inventing missing values or forcing coverage.

Classify constituents as `SUPPORTED`, `GENERALIZATION_REQUIRED`, or
`SPECIALIZED_METHODOLOGY_REQUIRED`. During Phase 1H, prefer reusable,
high-frequency normalization fixes over issuer-specific hacks. Use an
issuer-specific policy only when filing evidence and accounting rationale
support it, and never force a result to improve coverage statistics.

Phase 1H.6 has frozen historical normalization v1 with qualified coverage.
The Phase 1 blocker-resolution extension has qualified evidence-accounted
preparation closure; see `docs/phase1-preparation-closure-checklist.md`.
This is not complete financial-input sufficiency, whole-history fact provenance
or five-year completeness. Financial blockers/history exceptions remain explicit;
no further research chain is required by this preparation standard.
Freeze completion is necessary but is not authority to start Phase 2.
The earlier Phase 2 postponement applied to the preparation milestones. Under
the current pause/handoff direction, do not begin FCFF, forecasting, DCF, WACC,
terminal value, sensitivities, equity/per-share valuation, valuation UI or
deployment without a separately scoped user request. Existing Phase 2A
assumption models do not authorize
consumption of incomplete historical inputs. Preserve frozen-v1 schemas,
policies, values and blockers; reported cash-flow input preparation must remain
separate from adjusted cash-flow calculations and valuation readiness.
The approved historical path uses reported movement rows and independently
reconciled CFO; complete reconstructed NWC/book ΔNWC is not a prerequisite.
Movements already included in CFO are supporting detail, not additional deductions.
Reconcile older timing/readiness designs with this path before consumer design;
historical acceptance does not itself approve a valuation formula or consumer.

## Engineering Principles

### Completion language and open roadblocks

Standing user instruction, November 3, 2026: do not call a company review,
development scope or the project complete while any roadblock in that scope
remains. An approved treatment, reconciled statement, passing test or published
component does not establish overall completion. Report the specific successful
check or implemented treatment and keep the parent status OPEN with its remaining
roadblocks. Do not hide unresolved inputs, classifications, methodology choices,
integration work or validation behind a completion label. Track cash-flow issues
and proposed closure criteria in `docs/company-resolutions/OPEN-ROADBLOCKS.md`.
Recommendations are not new numerical-method approvals; preserve prior decisions
and label proposed treatments until the user approves them.

WP0 extends Phase 1 toward analyst-reviewable historical inputs under
`docs/dcf-input-contract.md`, separately from the completed facts/gaps closure.
It does not authorize Phase 2 or modify frozen-v1. Subsequent field-treatment or
mapping changes must maintain affected issuer records in the same milestone;
shared model-only work with no issuer value changes updates register guidance,
not all forty records. Required missing values stay unresolved despite acceptance.

- Prioritize correctness, modularity, explainability, and testability.
- Build incrementally; do not implement the entire application at once.
- Keep SEC retrieval, XBRL normalization, derived financial calculations, and valuation calculations separate.
- Prefer official SEC data for historical financials.
- Never invent missing financial values.
- Preserve source metadata so normalized values can be traced back to SEC filings.
- Avoid premature infrastructure such as databases, caching, containers, authentication, or cloud services unless clearly required.
- Add tests for financial calculations and important normalization logic.

## Financial Methodology

### Apple analyst-readiness contract

The user approved reasonable, disclosed analyst assumptions and explicitly
requested all five Apple outputs. The current named consumer and acceptance
record is `docs/company-resolutions/AAPL/analyst-ready-2026-11-04/README.md`.
It supersedes blanket exact-reconstruction blocking rules for this Apple scope:
five-year historical FCFF/standardized FCFE estimates, FCFF/FCFE valuations and
both share estimates are analyst-ready with qualifications after their tests.
Keep reported facts, derived estimates and assumptions distinct. Preserve old
source unknowns/strict review records; do not describe an estimate as exact
historical cash. No automatic extension to META/Alphabet or the wider universe.
The standing no-premature-completion rule still applies to actual implementation,
arithmetic, source contradiction and undisclosed-assumption blockers. Explicitly
accepted research qualifications are not themselves unfinished development.

### Meta and Alphabet analyst consumers

The subsequent explicit user request extends the same five-output analyst-ready
standard to META and GOOGL only. Current decisions, source projections and
acceptance are in each `docs/company-resolutions/<ticker>/analyst-ready-2026-11-04/`.
Use `review/company_analyst.py` and the selected-case live consumer. Qualified
FCFE estimates, carrying-value investment/NCI proxies, dated economic share-class
assumptions and financing differences must remain explicit. Alphabet's default
historical cash remains an unallocated consolidated proxy, not verified parent
cash; its forward minority claim is separate and deducted once. Reported facts,
legacy unknowns and Apple's accepted financial outputs remain preserved. This
extension does not authorize other issuers or public deployment.

Historical standardized output should eventually support:

- Revenue
- EBIT / operating income
- Taxes
- D&A
- Capex
- Operating NWC and change in NWC
- Cash and investments
- Debt
- Diluted shares
- Other inputs required for FCFF valuation

Core FCFF relationship:

FCFF = NOPAT + D&A - Capex - Change in NWC

where:

NOPAT = EBIT × (1 - tax rate)

Forecast assumptions will initially be entered manually.

## Repository Documentation

Keep these files current when relevant decisions are made:

- `README.md` — project overview, setup, and usage
- `docs/architecture.md` — architecture and technical decisions
- `docs/financial-methodology.md` — financial definitions and methodology
- `docs/project-status.md` — completed work, current milestone, known issues, and next steps

Repository documentation is the source of truth for project state and decisions.

### Standing company-preparation maintenance requirement

Track two independent preparation statuses: **evidence-accounted preparation**
(available evidence and gaps are traceable/explained within the stated binding
scope) and **financial-input sufficiency** (inputs satisfy a named, approved
consumer contract). Accounting PASS is not complete fact-level provenance,
five-year completion, support certification or valuation readiness. Keep financial
sufficiency NOT_ASSESSED/unknown when no such contract establishes it. Report
aggregate corpus, exact fact provenance and independently reviewed bundles
separately; pilot periods never approve whole histories. Preserve explicit
missing/broken/insufficient bindings and short/empty-history exceptions.

Any change to retrieval, filing/period selection, sorting/classification,
normalization, derivation, or valuation-input preparation must update affected
issuer records in `docs/company-data-preparation/` in the same milestone, and
the register index when its shared contracts or mapping are affected.

Records must explain the original conflict, exact sources/evidence, considered
treatments, chosen resolution and rationale, affected periods/policies,
validation, and unresolved limitations. Distinguish SEC-reported facts,
SEC-supported derivations, analyst classifications/estimates, manual inputs and
external data. Preserve prior decisions when superseded and link to detailed
evidence rather than duplicating it. Mark unreviewed details explicitly; records
must support eventual valuation use without implying unsupported readiness.

## Development Workflow

For each milestone:

1. Define what is being built and why.
2. Implement the smallest working version.
3. Add or update tests.
4. Run tests locally.
5. Validate financial outputs against actual SEC filings when applicable.
6. Update documentation when architecture, methodology, or project status changes.
7. Commit a coherent unit of work.

Do not silently change financial definitions or architecture decisions. Document material changes.
