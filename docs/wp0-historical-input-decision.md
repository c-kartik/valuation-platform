# WP0 decision — additive analyst-reviewable preparation

2026-10-12; starting HEAD `a33adb4f8955de890feb39322f01f2606fd3e48e`.
**GO for isolated contract/models only. Phase 2 remains prohibited.**

The user approved moving beyond evidence-accounted facts/gaps. Adopt the
[historical-input contract](dcf-input-contract.md) as a separate Phase 1 layer,
not a replacement of historical-normalization v1 or a financial sufficiency gate.
The earlier [restricted delivery proposal](phase1-blocker-disposition-review.md)
remains evidence/history context; its four-period index is not the active next step.
Qualified facts/gaps closure remains true under its original narrower standard.

Decisions:

- Five annual periods remain the target; three-period readiness and proposed
  90% recent/80% older coverage are targets, not measured success. User acceptance
  of material shortfalls is required and cannot turn missing values into resolved.
- Deliver all annual/bridge/share field families with independent origin, quality,
  scope, completeness and review status. Manual identity is not SEC provenance.
- Structural provenance checks do not certify fact occurrences, scope or supplied
  arithmetic. No issuer entries, new estimates or automatic pilot migration now.
- Keep reported cash movements distinct from book ΔNWC and CFO residuals distinct
  from economic adjustments. Operating-only and non-overlap boundaries constrain
  future formulas, not approve them. No tax rates or dilution assumptions.
- Eight specialized issuers, including GE, are excluded from generic bundles.
  Preserve their original outputs and all frozen support classes.
- Immutable additive models/serialization live in `analyst/historical_inputs.py`;
  reuse only safe immutable `Period`/`Artifact`/`Receipt`. No shared source change,
  resolver, persistence, policy expansion, valuation consumer or new framework.

No issuer value or treatment changes, so update shared register guidance only;
do not rewrite forty records to imply financial review. Subsequent mappings and
field treatments must maintain affected issuer records with evidence, rationale,
alternatives, validation and remaining requirements.

Validation: focused new model tests and existing pilot preservation checks,
compileall, local-reference checks, `git diff --check`; no full suite/corpus/SEC.
Next: one bounded four-pilot-period field-treatment/mapping design with explicit
missing requirements and acceptance tests. Stop after WP0, await authorization.
