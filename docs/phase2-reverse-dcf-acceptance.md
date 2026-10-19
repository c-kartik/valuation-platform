# Phase 2 — qualified three-company reverse-DCF acceptance

## Status and attribution

**Reverse-DCF software acceptance complete; economic interpretation qualified.**
This records the supplied analyst report at
`790a7c8052e2bfc15c31479bf63871d58639bcc7`, separately from the new checks in the
[final completion checkpoint](phase2-completion-checkpoint.md). The prior report
is an attributed record, not independently authenticated evidence, new financial
approval or a claim that its checks were rerun here.

Source: user-supplied `Pasted text.txt` under
`/Users/kc/.codex/attachments/b9fe8395-3034-4ce8-990a-11ad1f393871/`, SHA256
`e2662aef3af2abdcf7884c1a5104afb3036de6402508fd80837311302ea5c00b`.
The report reconstructed disclosed inputs from the [META milestone](phase2-meta-milestone.md),
[GOOGL/AAPL milestones and ERP reconciliation](phase2-googl-aapl-milestones.md),
[scenarios](phase2-scenario-acceptance.md) and
[sensitivity acceptance](phase2-sensitivity-acceptance.md); it did not authenticate
or replay deleted original case files. Reported historical anchors, analytical
dates/cutoffs, conventions, bridges and omissions stayed fixed. No current-market
target, new evidence, standing Base case or company default was introduced.

## Reported reconstruction and bounded solves

All values are **temporary assumption-led trial results**, not approved forecasts
or fair values. Money is USD billions unless labeled otherwise. Fiscal-end
analytical timing uses later-filed information, not a contemporaneous backtest.
Exact retained source/approval bindings remain in [anchor integration](phase2-anchor-integration.md#fixed-selections-and-provenance).

| Issuer | FY2025 revenue / annual period | Analytical date / cutoff | WACC / terminal g | Original Base EV / basic-equivalent USD/share | Base-EV solved constant growth |
| --- | --- | --- | --- | --- | --- |
| META | 200.966 / 2025-01-01–2025-12-31 | 2025-12-31 / 2026-01-29 | 10% / 3% | 945.742176 / 369.419042 | 15.043214% |
| GOOGL | 402.836 / 2025-01-01–2025-12-31 | 2025-12-31 / 2026-02-05 | 8.74% / 3% | 1387.933471 / 114.395258 | 10.981804% |
| AAPL | 416.161 / 2024-09-29–2025-09-27 | 2025-09-27 / 2025-10-31 | 8.59% / 2.5% | 1865.091633 / 124.918226 | 5.805551% |

The [bounded contract](phase2-reverse-dcf-workflow.md) replaces **all five annual
growth rates** with one constant, not their mean, CAGR or a shift. Fixed margins,
tax/D&A/investment/WC ratios rescale dollar amounts; WACC, terminal g/ratios and
bridge/shares remain fixed. Original provisional growth paths were META
`255/200.966−1, 18%, 14%, 10%, 7%`; GOOGL `15%, 13%, 11%, 9%, 7%`; AAPL
`8%, 6.5%, 5.5%, 4.5%, 4%`. User-selected META FY2026 amounts remain distinct from
other agent-selected estimates in the linked records.

The initial −100% to +40% interval was not certified for META/GOOGL: independent
review reportedly found negative derivatives near collapse and positive at the
upper endpoint. **Inconclusive certification does not prove multiple target roots.**
AAPL certified increasing. Subsequent diagnostic intervals −10% to +40% for
META/GOOGL and −10% to +25% for AAPL certified increasing. These were supplied
operating diagnostics, not plausible-endpoint claims, confidence bounds or defaults.

| Reported constant-growth solve | META | GOOGL | AAPL |
| --- | --- | --- | --- |
| Target 80% / 100% / 120% of original full-precision Base EV | 10.041103 / 15.043214 / 19.307718% | 6.185518 / 10.981804 / 15.071334% | 0.630774 / 5.805551 / 10.171354% |
| Known-growth recovery | 15%; exact | 12%; error <2.01e−13 fraction | 6%; error <1.01e−13 fraction |
| Equivalent unrounded basic-share target | Same growth string as EV target | Same growth string as EV target | Same growth string as EV target |

All nine EV solves reportedly passed the unchanged width ≤1e−12 fractional growth
and scale-aware residual policy; signed USD residuals ranged approximately −1.71
to +1.03. All 19 successes matched ordinary forward execution. Intervals excluding
known roots returned `UNREACHABLE_TARGET`, no solution. Mechanical −100% growth /
zero-EV endpoint probes passed fresh verification; they are not economic forecasts.
Synthetic flat, nonmonotonic and monotone-but-uncertifiable cases returned conservative
failures; forced iteration exhaustion also exposed no solution. An unsupported
certificate never became a nearest-bound success.

## Economic qualifications retained

- **META:** Base-EV solved FY2026 revenue about 231.2bn and fixed margin imply
  expenses **150.052bn**, below the documented **162–169bn** outlook. Equal EV
  does not make the fixed-ratio budget economically coherent without a cost thesis.
  Early cumulative negative FCFF falls 30.096→27.181bn but remains unfinanced;
  terminal contribution increases 90.02→90.30%.
- **GOOGL:** early negative FCFF falls 45.644→43.787bn; terminal contribution
  remains **93.01→93.09%**. Later monetization, margin recovery and moderated
  investment drive the result; proportional D&A is not an asset-cohort model.
- **AAPL:** terminal contribution rises 74.49→74.90%; terminal net reinvestment /
  NOPAT stays **9.56%**, implying approximately **26.16%** incremental return at
  2.5% growth. Solving annual growth does not repair this demanding productivity
  assumption. This physical-capital/WC diagnostic is not verified historical ROIC;
  expensed intangibles limit interpretation.

Named net bridges stayed −11.112 / −5.1235915 / −19.6421962bn, reserves
34.3 / 70.4125915 / 49.4371962bn and dated issued shares
2.530 / 12.088 / 14.773260bn (META / GOOGL / AAPL). A/B and A/B/C economic-unit
equivalence is assumed apart from votes; no automatic award addition, EPS-average
substitution or duplicate future-service SBC charge. Operating leases remain service
costs and financed depreciation is added once. GOOGL/AAPL bridged opening-tax
settlements remain outside forecast tax/WC. META omitted legacy settlements remain
outside its limited recurring-core reference, not zeros.

Funding, unidentified financing/other claims, awards, strategic/venture economics,
asset accessibility and settlement coverage remain unresolved, potentially unbounded.
These basic-common references are not fully diluted fair values; diagnostic
alternatives do not bound total company value. No rating, current-price comparison
or approved target follows. Software acceptance is distinct from investment readiness.

## Prior verification — attributed, not newly executed

The report states: **24 company JSON requests**, six summaries, three calculation-free
validation checks; **1,668 independent exact-Fraction arithmetic comparisons**
(`1e−32 + 1e−46 × |reference|`, max difference about 1.64e−37);
**405 exact certificate equalities** across 27 certificates and 27 direction checks.
The independent degree-four Bernstein reconstruction confirmed interval-wide
bounds, not uniqueness inferred from ordinary samples. It also reports 19 forward
agreements, a fresh-final-evaluation trace, four invalid-input probes and nine
output-protection probes. No correctness defect was reported; technical certificate
output, verbose JSON and USD-million display remain usability limitations.

Temporary cases, outputs and scripts were reported removed; all **596 tracked
files** reportedly stayed unchanged, with six 37-unset and three 111-unset templates.
No full suite was claimed rerun. The [new final checkpoint](phase2-completion-checkpoint.md)
records only its own executed checks separately. [Phase 1 remains paused](phase1-universe-pause-checkpoint.md).
