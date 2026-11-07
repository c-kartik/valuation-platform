# Scope 1 — DCF pipeline and valuation workspace

Recorded November 7, 2026. Product-scope checkpoint, not a renumbering of the
historical Phase 1H preparation or Phase 2A workstreams.

## Completed pilot scope

The named AAPL, META and GOOGL consumers are implemented and deployed with
**ANALYST_READY_WITH_QUALIFICATIONS** acceptance. Their core DCF workflow is the
prerequisite reference for [Scope 2](scope-2-research-dashboard.md).

- Retained Python SEC acquisition/preparation with source metadata and explicit
  missing values; manual laptop refresh remains the approved workflow.
- Five-year historical FCFF and standardized/qualified FCFE under each issuer's
  accepted conventions, editable forward assumptions, FCFF/FCFE valuations and
  per-share bridges with source/assumption distinctions.
- Bear/Base/Bull, sensitivity and supported reverse/terminal comparisons.
- Browser JavaScript default, disposable calculation workers, verified static
  datasets, and retained Python opt-in without modifying its pipeline.
- Live portfolio integration at https://kartikchaturvedi.com/valuation/,
  company search and Excel model-state saving, including incomplete editor drafts.

Acceptance records:

- [Apple](company-resolutions/AAPL/analyst-ready-2026-11-04/README.md)
- [Meta](company-resolutions/META/analyst-ready-2026-11-04/README.md)
- [Alphabet](company-resolutions/GOOGL/analyst-ready-2026-11-04/README.md)
- [Current qualification crosswalk](company-resolutions/OPEN-ROADBLOCKS.md)
- [Browser equivalence/release record](browser-engine-migration.md)
- [Excel saving contract](excel-model-snapshots.md)

Recorded validation: 467 frontend tests, 128 independent full-output Python
reference cases within the browser suite, five packaging checks, 396 unchanged
Python source hashes, and live three-company calculation/Excel downloads. See
[project status](project-status.md) for dates and exact release receipts.

## Completion boundaries

This closes the implemented three-company core workflow, not every research,
source or portfolio-development obligation. Existing qualifications remain.
It does not certify exact historical parent-common cash, all economic claims,
the whole universe, or current-market upside from fiscal-end valuations.

The current models use fiscal-end valuation origins and later-filed information.
Current-date price-versus-value signals need their own approved valuation-date
contract under Scope 2. Ten-year calculations support explicit user inputs;
automatic years 6–10 estimates are not approved. Excel import/recalculation and
actual user phone acceptance remain separate follow-ups. GCP was not retired.

## Gate for every additional ticker

Completion is per issuer and named consumer. Follow the reusable
[onboarding checklist](ticker-onboarding-checklist.md), first establishing
Scope 1 sufficiency and acceptance; then assess each Scope 2 feature separately.
Preparation traceability alone is not financial-input sufficiency. Specialized
issuers require an appropriate methodology rather than forced operating-company
DCF coverage. The broader [universe-review pause](phase1-universe-pause-checkpoint.md)
remains in force until the user explicitly resumes a named issuer/scope.
