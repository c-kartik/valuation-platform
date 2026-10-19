# Phase 2 — META, GOOGL and AAPL completion checklist

## Scope and completed foundation

This checklist defines remaining work for **META, GOOGL and AAPL only**. It records
status and decisions needed before separately scoped implementation; it approves
no new economics, ranges, calculation conventions or execution. The existing
[consumer conventions](phase2-meta-base-consumer-contract.md) and
[anchor integration](phase2-anchor-integration.md) remain authoritative.
[Phase 1 expansion is paused](phase1-universe-pause-checkpoint.md).

| ID | Milestone / current status | Decisions and acceptance needed |
| --- | --- | --- |
| P2-01 | **Complete:** editable single-case manual FCFF → EV → explicit equity/share workflow | Existing v1 EV / v2 equity scope, strict Decimal inputs, calculation-free validation, provenance, JSON/summary and file protection remain the foundation; no redesign implied. |
| P2-02 | **Complete, scope-qualified:** actual-company end-to-end trials for all three | [META record](phase2-meta-milestone.md) and [GOOGL/AAPL records](phase2-googl-aapl-milestones.md) preserve temporary estimates, omissions and attributed prior checks. Completion is workflow exercise, not a standing Base-case approval or complete financial sufficiency. |
| P2-03 | **ERP reconciliation complete, scope-qualified; broader market-input review outstanding** | [2026-10-19 GOOGL correction](phase2-googl-aapl-milestones.md#googl-erp-reconciliation--2026-10-19) verifies the specified ERP variant/date/publication basis and reruns only GOOGL. Company beta, weights, debt/shield judgments and wider comparability remain separate; no general market-input policy/default is approved. Further changed inputs require separate authority and reconciliation. |
| P2-04 | **Not implemented:** editable Bear/Base/Bull scenarios | Decide the smallest scenario representation, shared anchor/date/cutoff and conventions, explicitly editable annual/terminal inputs, bridge/share inheritance or overrides, and comparable outputs. User/analyst supplies each scenario's rationale and economics; names do not define approved forecasts. Verify independent editing, missing-input rejection and existing single-case compatibility. |
| P2-05 | **Not implemented:** reusable sensitivity tables | Decide supported axes, user-supplied grids/ranges, one-/two-variable scope, held-fixed assumptions, EV versus qualified per-share output, and invalid-cell handling. No automatic economic ranges or silent terminal/WACC repair. Verify selected cells against single-case execution and preserve provenance/input immutability. |
| P2-06 | **Not implemented:** bounded reverse DCF | Decide target metric/date/unit (EV or explicitly bridged per-share), one solved input and held-fixed path, admissible bounds, monotonicity/existence/non-uniqueness handling, convergence tolerance and reported residual. No target price, solved variable or growth/margin/investment coupling is approved here. Verify against hand-checkable synthetic cases; a numerical solution does not certify economic plausibility. |
| P2-07 | **Pending:** final three-company analyst acceptance and regression checkpoint | After the preceding decisions/features, agree a bounded review matrix across these three anchors, editable single/scenario inputs, sensitivity/reverse outputs, dates, units, traceability, error paths and file protection. Run affected synthetic regressions and separately authorized temporary issuer trials; attribute old checks separately. Preserve unresolved financial scopes and all unset templates. |

## Bounded market-input reconciliation

| Historical trial | ERP selection as disclosed | Comparability limitation |
| --- | --- | --- |
| META, analytical 2025-12-31; cutoff 2026-01-29 | **4.23%**, sourced start-2026 Damodaran implied ERP; identified in the AAPL report as the trailing-12-month cash-yield variant | Preserve the [META record](phase2-meta-milestone.md), including rounded 10% WACC; no ERP replacement or rerun here. |
| GOOGL, analytical 2025-12-31; cutoff 2026-02-05 | **5% analyst judgment**, not that sourced implied-ERP observation | Same analytical date as META does not make differing methods directly comparable. Its 9.57% WACC remains the reported trial input. |
| GOOGL, superseding 2026-10-19 reconciliation; same analytical date/cutoff | **4.23%**, January 1, 2026 T12m ERP over unadjusted Treasury; January 23 author publication record within cutoff | Applied WACC **8.74%**; only this market input and resulting discounting changed. Original 5%/9.57% results above remain historical; no META/AAPL rerun. |
| AAPL, analytical 2025-09-27; cutoff 2025-10-31 | **3.94%**, September 1 observation of the **same specified Damodaran variant as META**, not adjusted payout | Earlier date-appropriate observation with approximately four-week lag; workbook metadata did not independently authenticate first publication time. Its 8.59% WACC remains unchanged. |

The specified **ERP variant reconciliation is complete** for the authorized GOOGL
correction: the January workbook confirms the same T12m series as META/AAPL,
distinct from sustainable payout, net cash yield and adjusted-risk-free variants.
Measurement/start-month and documented publication dates remain separate.
The trials are **not fully harmonized for direct comparison**. Broader P2-03 review
still concerns dated observation/publication-lag and risk-free matching policies.
Keep beta, target capital structure, debt spread, tax shield, forecast operating
tax and WACC rounding separately justified; common ERP need not imply equal WACC.
No broad historical reconstruction or current-market substitution is required.

The separately authorized GOOGL reconstruction/rerun records changed inputs,
full-precision calculation, independent checks and result differences in the linked
reconciliation; original records remain historical. Any further methodology changes
must identify affected cases and separately scope their reruns. This checklist adds
no execution/evidence authority, issuer defaults or permanent financial selections.

## Completion boundary

Software acceptance means the scoped workflows calculate correctly, expose their
inputs/limits and support review across the three retained anchors. Investment
readiness separately requires a case-specific supported forecast and market basis,
asset eligibility, claim/settlement non-overlap and shares/awards treatment. Basic
issued-share trial references are not fully diluted fair values. Unknown or
unbounded claims stay visible; historical omission approvals do not resolve them.

Neither complete historical NWC reconstruction, every historical unknown nor all
42 eligible issuers is a prerequisite to this scoped engine milestone. A required
missing operand must still block its affected calculation; explicit qualified
omissions must not become silent zeros or economic-completeness claims. Financial
unknowns are not waived, and universe reviews do not resume. No new UI,
infrastructure or additional-issuer integration is part of this checklist.
