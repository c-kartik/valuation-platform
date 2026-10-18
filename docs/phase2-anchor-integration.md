# Phase 2 — GOOGL/AAPL revenue-anchor integration

This engineering milestone extends the editable v1 EV / v2 equity-share workflow
to exact retained GOOGL and AAPL revenue anchors. Only synthetic fixtures exercise
financial calculations. It supplies no actual-company forecasts, WACC, bridge,
class equivalence or award treatment and transfers no META financial approval.
The [completed META milestone](phase2-meta-milestone.md) remains a historical
record. [Phase 1 expansion remains paused](phase1-universe-pause-checkpoint.md).

## Fixed selections and provenance

| Kind | CIK / accession / form | Selected annual | Revenue, base USD / precision |
| --- | --- | --- | --- |
| `meta-fy2025` (unchanged) | 1326801 / 0001628280-26-003942 / 10-K | 2025-01-01–2025-12-31 | 200966000000 / −6 |
| `googl-fy2025` | 1652044 / 0001652044-26-000018 / 10-K | 2025-01-01–2025-12-31 | 402836000000 / −6 |
| `aapl-fy2025` | 320193 / 0000320193-25-000079 / 10-K | 2024-09-29–2025-09-27 | 416161000000 / −6 |

These are retained reported facts, not forecast defaults. Revenue is positive,
finite USD at scale 1; −6 is source precision, not a multiplier. Original fact
occurrences, source metadata and inline display scales remain in provenance.
No filing refresh, source acquisition, normalization or historical selection changes.

For each new kind, replace `{issuer}` below with `googl` or `aapl` in its
[GOOGL package](company-data-preparation/googl-analyst-input-package.json) or
[AAPL package](company-data-preparation/aapl-analyst-input-package.json):

| Role | Exact retained reference / binding |
| --- | --- |
| Reported revenue | `/{issuer}_history_review/periods/4/facts/revenue` |
| Effective consumed revenue | `/{issuer}_current_history/periods/4/inputs/revenue` |
| Current historical audit | `/{issuer}_history_approval`, sequence 2 |
| Prior scoped audit | `/accepted_view/approval_audit`, sequence 1; FY2024 for GOOGL, FY2025 for AAPL |
| Effective revenue acceptance | `/{issuer}_current_history/periods/4/checklist` revenue entry; source/prior scope, not a new forecast approval |

The new consumer pins the exact audit SHA256:

- GOOGL: `728eaf073b0ef2fb5234f835e018e2290f7c3eac652cc91cb05e14cdef41d847`.
- AAPL: `f0a91b70b853ec380091a779b227d742c5d1d0aa0add21fdd09e91d39cf96f62`.

Existing hash and manual-identity validators check the audit's content digest,
prior-audit chain, parent/source relevant-content revision and review revision
(periods, consolidated proposals, parent revision). Effective period identities,
audit reference, reported-value projection and consumed revenue checklist must
match exactly. A stale source, review/proposal, audit or effective selection fails;
nonempty strings alone authenticate no approval. The GOOGL revenue checklist has
no prior scoped approval reference; AAPL's refers to `/accepted_view`. These
distinct roles are preserved, not replaced with a blanket sequence-1 approval.
META retains its original separate package/decision binding and serialization.

Only revenue is a required historical operand. Missing optional effective D&A,
NWC, financing or shares do not block this boundary. Source changes still
invalidate their retained approval revision; optional context is not permission
to edit an approved source. Current unknowns and incomplete expense-D&A/debt/
reinvestment coverage remain unchanged; historical omissions may be unbounded.
See authoritative [GOOGL](company-data-preparation/GOOGL.md) and
[AAPL](company-data-preparation/AAPL.md) preparation records for financial scope.

## Intake, conventions and limitations

`ANCHORS` in [consumer.py](../src/valuation_platform/valuation/consumer.py) is an
explicit fixed dispatch, not a generic ticker resolver or latest-filing policy.
`read_case` validates supplied identity/declarations without loading history or
calculating. Only explicit `run_case` resolves retained revenue and delegates to
existing Stages A/B/C. Unknown anchor kinds reject; there is no synthetic fallback.
V2 missing/unresolved bridge data fail instead of downgrading to EV-only success.

New issuers explicitly declare `manual-fcff-v1` and `manual-equity-bridge-v1`.
These technical aliases reuse the existing arithmetic: SBC and operating-lease
service costs inside margins; expense-aligned D&A once; investment is cash PP&E
plus non-overlapping new finance-leased operating assets, excluding principal;
signed WC cash requirement uses full forecast revenue. Neither alias establishes
economic consistency or company financial acceptance. Legacy META convention
identifiers, examples, formulas and JSON remain backward compatible. No input
schema fields or general approval framework are added.

AAPL's analytical t=0 is September 27, 2025; five periods are ordinal 1–5 with
FY2026–FY2030 labels. No December year-end, stub/week adjustment or automatic
annualization of its earlier 53-week year is assumed. GOOGL's kind refers to
Alphabet consolidated revenue, not approved equivalence of Classes A/B/C. Both
cases require a separately stated information cutoff and disclose later-filed
information; these are not current-date valuations or contemporaneous backtests.

Four incomplete templates retain **all 37 numerical inputs and analyst metadata
unset**, with unresolved Stage C components, coverage, shares/classes/awards:

- [GOOGL EV](../examples/valuation/googl-fy2025-unset.json) /
  [equity-share](../examples/valuation/googl-fy2025-equity-unset.json).
- [AAPL EV](../examples/valuation/aapl-fy2025-unset.json) /
  [equity-share](../examples/valuation/aapl-fy2025-equity-unset.json).

The [README commands](../README.md#editable-analyst-inputs--forecast-through-value-per-share)
intentionally reject these templates without calculations or result writes.
Errors identify paths, e.g. `forecast_years[2].revenue_growth` for numeric JSON
rates, `anchor.accession`, `terminal.operating_tax_rate`,
`terminal_growth (relative to wacc)` and `bridge.unresolved_requirements`. Duplicate keys,
nonfinite numbers, unknown fields/versions, dates and units remain strict;
there is no coercion or default calibration. Only error-field metadata changes
existing assumption models; their validation rules remain identical.

## Verification and next boundary

Focused coverage includes actual retained anchors without company calculations,
stale revisions/effective selections, missing consumed revenue versus optional
context, AAPL fiscal timing, unset templates, actionable paths, explicit dispatch,
shared-convention synthetic A→B→C arithmetic, deterministic serialization and
caller Decimal-context isolation. Starting-checkpoint example hashes and complete
synthetic EV/equity JSON byte hashes are regression assertions. Existing CLI
summary and file-protection tests remain applicable.

Historical/normalization/evidence/frozen preservation checks remain active. The
existing source allowlist gains only the assumption model's field-error metadata;
an AST comparison verifies every original validation rule remains unchanged.
No issuer preparation record is rewritten because no preparation changed.
Current test totals and manual acceptance checks are recorded in
[project status](project-status.md).

Next is a separately scoped financial input review for one issuer, including
expense D&A/investment consistency, operating taxes/WC, WACC/terminal economics
and any actual bridge/share policy. Engineering support is not an investment
valuation or financial-sufficiency certification. Scenarios, sensitivities and
reverse DCF remain later capabilities; universe expansion does not resume.
