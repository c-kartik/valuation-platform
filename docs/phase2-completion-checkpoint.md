# Phase 2 — final three-company workflow and regression checkpoint

## Latest status — COMPLETE within the defined scope

**2026-10-19: Phase 2 software acceptance is complete for the three retained
META, GOOGL and AAPL FY2025 anchors. Economic acceptance remains qualified.**
This closes a local analyst-controlled engine: editable five-year FCFF DCF through
EV and explicit equity/share; complete Bear/Base/Bull cases; explicit WACC ×
terminal-growth sensitivities; certified bounded constant-growth reverse DCF;
strict validation, traceable inputs/limitations and protected JSON/summary output.
Assumptions remain separate from financial formulas. No code, schema, formula,
financial convention or preservation guard changed in this checkpoint.

The [checklist](phase2-completion-checklist.md) records the closure boundary.
**Operating-driver sensitivities are DEFERRED and are not a closure blocker**;
future axes, coupling and held-fixed scope need separate decisions. The specific
[GOOGL ERP reconciliation](phase2-googl-aapl-milestones.md#googl-erp-reconciliation--2026-10-19)
is already recorded; further broad market-input harmonization is outside this
software checkpoint. No standing company Base case/default, financial approval,
complete input/claims sufficiency, investment readiness or fully diluted fair
value is certified. This is not arbitrary-ticker/latest-filing support, UI or
deployment. [Phase 1 universe expansion remains paused](phase1-universe-pause-checkpoint.md);
all historical unknowns and the resumption backlog remain intact.

## Attributed earlier acceptance versus this checkpoint

[Reverse-DCF acceptance](phase2-reverse-dcf-acceptance.md) records the supplied
prior report, including 1,668 arithmetic comparisons and 405 exact certificate
equalities. **Those prior checks are attributed, not claimed as rerun here.**
The [META](phase2-meta-milestone.md), [GOOGL/AAPL](phase2-googl-aapl-milestones.md),
[scenario](phase2-scenario-acceptance.md) and [sensitivity](phase2-sensitivity-acceptance.md)
records retain their original checks, dates and economic qualifications.

The new continuous sessions below used final code at
`790a7c8052e2bfc15c31479bf63871d58639bcc7`. Codex (AI analyst) prepared temporary
reconstructions at **2026-10-19T15:40:43.078590+00:00**; that is preparation
metadata, not an historical information date or human-supplied forecast claim.
Exact disclosed amounts/derivation rules from the linked records were used at
Decimal precision 50/HALF_EVEN, rather than rounded displayed ratios. All nine
provisional scenarios were recoverable numerically; removed original JSON,
metadata and outputs were **not authenticated or replayed**. New metadata and
explicit limited-scope omissions were supplied. No evidence was acquired.

## Continuous analyst sessions — newly executed

Exact retained selections/source/audit bindings remain in
[anchor integration](phase2-anchor-integration.md#fixed-selections-and-provenance).
META/GOOGL retain calendar FY2025; AAPL retains 2024-09-29–2025-09-27.
Timing is fiscal-end analytical using later-filed information, not a contemporaneous
backtest or current-price comparison. Every result below is a **temporary,
assumption-led trial result**, not a standing Base, financial approval or target.

| Session / input boundary | META | GOOGL | AAPL |
| --- | --- | --- | --- |
| Retained revenue, USD bn | 200.966 | 402.836 | 416.161 |
| Analytical date / cutoff | 2025-12-31 / 2026-01-29 | 2025-12-31 / 2026-02-05 | 2025-09-27 / 2025-10-31 |
| WACC / terminal g | 10% / 3% | 8.74% / 3% | 8.59% / 2.5% |
| Single-case validation, EV/equity JSON + summary, growth edit | PASS | PASS | PASS |
| Complete Bear/Base/Bull, fixed entire bridge, isolated Bear edit | PASS | PASS | PASS |
| Explicit Base-selected 2×2 sensitivity, single-case cell reproduction, separate invalid cell | PASS | PASS | PASS |
| Same Base-selected reverse: known growth, EV/share equivalence, forward match, unreachable failure | PASS | PASS | PASS |
| Independent arithmetic and preservation/error-path checks | PASS | PASS | PASS |
| Reconstructed Base EV / qualified basic-common USD/share | 945.742176bn / 369.419042 | 1387.933471bn / 114.395258 | 1865.091633bn / 124.918226 |

One continuous session per company used the actual readers and four CLIs,
embedded the same complete scenario set and explicitly selected `Base` for both
sensitivity and reverse requests. Single-case cutoff was disclosed in scope/
limitations; scenario/request date fields bound it explicitly. Source/approval
metadata, declared conventions, units, class/award policies and unbounded omissions
survived output. META's user-selected provisional FY2026 255bn revenue, 165.5bn
expenses, 89.5bn EBIT and 28.3bn expense D&A remain distinct from other
agent-selected estimates. All forecast/bridge economics are documented in the
linked historical records; none became executable repository defaults.

New acceptance checks:

- **162 subprocess CLI invocations**, including validation, JSON/summary execution,
  edits, independent single-case submissions and failure/output guards. Twelve
  additional instrumented CLI validations (four per company) rejected any attempt
  to call the valuation entry point or historical loaders. Validation produced no
  valuation result or file; `--output` without `--run` rejected.
- Raising only FY2028 growth by 1 percentage point left earlier annuals unchanged
  and propagated through later revenue/FCFF; the entire bridge stayed fixed.
  Raising only Bear FY2027 margin by 1 point left Base/Bull full results unchanged.
  All nine scenario results equaled separate single-case execution.
- Each explicit 2×2 diagnostic grid used WACC `[reference, reference+1pp]` and g
  `[reference, reference+0.5pp]`, including the reference cell. All **12 cells**
  matched separate single-case submissions (60 PV/EV/equity/share comparisons).
  Separate mixed grids retained g=WACC cells as invalid with null metrics. These
  temporary grids are engineering diagnostics, not approved economic ranges.
- Known constant growth 15% / 12% / 6% was recovered within 1e−12 fractional growth.
  Original full-precision Base EV and equivalent unrounded USD/share targets
  returned identical growth strings: approximately **15.043214% / 10.981804% /
  5.805551%**. Main diagnostic intervals were −10% to +40% for META/GOOGL and
  −10% to +25% for AAPL, as in the prior review. Nine successes matched fresh
  ordinary forward CLI execution. Signed Base-EV residuals were approximately
  **−0.929990 / −0.981121 / −0.495724 USD** and passed unchanged solver policy.
  Excluding known roots with intervals `[known+5pp, known+15pp]` returned
  `UNREACHABLE_TARGET`, exit 3 and null solution for each company.
- All four request/result paths per issuer were deterministic, immutable and
  isolated from a caller precision-7/ROUND_DOWN context with Inexact trapped.
  Twelve explicit new temporary saves succeeded; overwrite, input-path and
  protected repository-path attempts rejected. Cutoff comparability and stale
  accession probes rejected; unresolved requested equity scope rejected without
  downgrade or output. Starting inputs and all **596 tracked-file hashes** were
  unchanged after the sessions, before documentation edits.

## Independent arithmetic and regression — newly executed

An independently structured exact-`Fraction` oracle read the raw submitted strings;
it did not call engine functions. **1,737 numerical comparisons passed** across
all Base/scenario annual FCFF components, discount factors/PVs, terminal FCFF/value,
EV, signed bridge/share reconciliation, edited single cases, one non-reference
sensitivity cell per company and all nine successful reverse forward results and
target residuals. Oracle fractions were compared with engine Decimal strings using
precision 110 and tolerance **1e−32 + 1e−46 × |reference|**. Maximum observed absolute
difference was approximately **1.047e−37** in the compared units. Economic precision
is far lower; this tolerance tests arithmetic only. Prior exact-certificate
comparisons remain attributed; the current synthetic regression also verifies
exact coefficients, conservative certification and solver policy independently.

Actual commands, run against the same unchanged final code:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/valuation -t . -v
PYTHONPATH=src .venv/bin/python -m unittest tests.analyst.test_preparation_preservation -v
```

**174 valuation/CLI tests + 5 preparation-preservation tests = 179 passed.**
Discovery includes retained adapters/anchor cases, Stage A/B/C, strict intake,
legacy EV JSON bytes, summary rounding/units, scenarios, sensitivity and reverse.
Checks include stale source/review/proposal/audit/effective bindings, wrong dates/
units/scope, no silent downgrade, complete validation before execution, deterministic
serialization, Decimal/input isolation, exact endpoints, flat/unreachable/inconclusive
certificates, iteration/fresh-verification failures and output protections. Existing
source/hash pins and allowlists passed unchanged. No full slow Phase 1 suite,
new historical corpus research or prior source-body authentication was performed.
**No correctness defect or fix was required.**

## Preservation, qualifications and next boundary

Final checks confirmed six original company templates remain byte-unchanged and
**37-unset each**, and three scenario templates byte-unchanged and **111-unset each**;
equity templates retain unresolved components/coverage/shares/classes/awards.
Only the listed Markdown checkpoint/status references changed. Historical/frozen
artifacts, approvals, code, tests, schemas and examples stayed byte-unchanged.
Temporary runnable cases, grids, targets, bounds, results and verification scripts
were removed; none was saved in the repository. Changed local links/anchors,
whitespace and staged scope were checked for this local commit. Nothing was pushed.

Equal valuation does not approve the reconstructed forecasts: META's reverse
solution implies about **150.1bn FY2026 expenses versus 162–169bn outlook**;
GOOGL remains about **93% terminal-dependent**; AAPL retains the demanding
**26.16%** terminal physical-investment/WC implied-return diagnostic, not verified
historical ROIC. Funding, financial-asset eligibility, awards, venture economics,
unpaid obligations and unidentified claims/settlement overlap remain unresolved
and potentially unbounded. Basic-issued-share references are not fully diluted
fair values; diagnostic alternatives are not bounds on total value. Broader dated
market-input harmonization is outside this software closure. Verbose JSON and
technical certificate output remain nonblocking usability limitations.

Complete historical NWC reconstruction, resolution of every historical unknown
or review of all 42 eligible issuers is not required for this scoped milestone.
Required missing operands still block their requested output; explicit omissions
never become reported zeros or a financial-completeness certification.

**Recommended first bounded Phase 3 milestone:** a local case-entry/review UI over
the existing validated interfaces for these three retained anchors, starting with
synthetic/unset inputs, validation-first review, explicit run and traceable protected
output. Phase 3 requires a separately scoped prompt; no UI, deployment, latest-filing
retrieval, additional issuer or new financial policy starts in this checkpoint.
