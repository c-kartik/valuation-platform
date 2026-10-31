# GOOGL proposed starting estimates — policy v1

Subsequent UI status: the [result-first workspace](investor-result-first-workspace.md)
now calculates complete starting profiles automatically through the local API and
uses one on-demand editor. Earlier no-auto/inline-layout statements below are
historical; financial rules, preload estimates and calculation-free preparation
remain unchanged.

Specification established before estimator implementation, October 30, 2026.
This is a separate forecast-preparation overlay, not a change to frozen history,
approvals or the [paused Phase 1](phase1-universe-pause-checkpoint.md).
It follows the existing [consumer convention](phase2-meta-base-consumer-contract.md)
and [exit-method boundary](exit-multiple-terminal-review.md). These are editable,
assumption-led starting estimates, not approved forecasts or investment-ready value.

## Selection, dates and reproducibility

`googl-preload-v1` maps GOOG and GOOGL to consolidated CIK 1652044; the requested
listing remains distinct. No class equivalence, price or denominator follows.
The engine anchor remains its exact approved FY2025 10-K identity and USD402.836bn
revenue. Model origin is December 31, 2025; information review is October 30,
2026. Publication, observation, retrieval and generation dates are separate.
Later information is hindsight at this fiscal-end origin, neither a contemporaneous
backtest nor a current-date valuation. No stub period is introduced.

Pin original source bodies and reviewed extraction records with SHA256, URL,
publication/accession, period, units, extraction version, retrieval time and reuse
posture. Original annual input packages and mirrored `sources/` stay read-only.
Only definition-compatible undimensioned consolidated periods are selected.
Duplicate same-period facts fail; a restatement must explicitly supersede an
observation, retaining both. No latest-filing anchor promotion occurs. Candidate
snapshots require explicit acquisition and reviewed extraction; acquisition alone
never supplies financial facts. Offline reproduction is the default.

Economic-content hashes cover sources, observations, rules, configuration and
forecasts; volatile profile-generation time is outside the hash. Never overwrite
snapshots, profiles, requests or results. Refresh compares source/restatement,
policy/configuration, forecasts, gaps and (only on explicit execution) value.
Reference research is a comparison record, not the policy implementation.

## Input rules

All engine rates are exact decimal strings in fractions, cash flows base USD.
UI percentages are a reversible display conversion. A five-point linear fade is
`start + (end-start)*i/4`, i=0..4. Historical statistics describe observations;
extending them is a forecast rule, never a reported fact. Minimum coverage is
stated below; no gap falls back to zero or a synthetic company.

| Input / engine field | Source, definition and required coverage | Transformation / configured judgment | Unavailable conditions / limitations |
| --- | --- | --- | --- |
| Revenue anchor | Exact retained FY2025 approved annual, precision −6, accession 0001652044-26-000018; one selected annual | No change; validate against existing consumer at execution | Identity/value mismatch blocks adaptation; later evidence cannot promote anchor |
| Annual growth / `revenue_growth` | Q3 release: consolidated YTD revenue and current/prior Q3 revenue; FY2025 Q4 from official annual/release; required all four | FY2026 revenue = reported 9m + prior Q4 × latest Q3 revenue ratio; derive growth from retained anchor. Fade growth to configured 7% in FY2030 | Not management revenue guidance; latest-quarter momentum may not persist; acquisitions/perimeter and seasonality not normalized. Missing/incompatible/nonpositive comparator blocks this rule |
| Annual margin / `operating_margin` | Latest reported Q3 EBIT/revenue; two matching period/definition facts | Fade reported Q3 margin to configured 29% FY2030; no normalization/add-back | Includes SBC, service leases, Other Bets and shared AI costs once; unallocated acquisition/service effects remain risk; no separate cost deduction |
| Annual tax / `forecast_tax_rate` | Historical provision/pretax are context only, not operating rates | Linear 18%→21% operating convention, deliberately independent of ETR; no immediate loss-tax benefit in engine | Configured forecast convention, not statutory/cash tax guidance; credits, discrete items, nonoperating gains and payment timing unmodeled; absent configuration unresolved |
| Annual D&A / `d_and_a_percent_revenue` | Historical PP&E noncash proxy remains incompatible with complete expense D&A; no calibration from CFO aggregate | Configured FY2026 expense D&A USD33bn; thereafter previous expense D&A + 12% of previous year's scoped investment; divide by each full revenue | Simplified commissioning allowance, NOT vintage/useful-life reconstruction. Includes expense finance-asset depreciation and intangible amortization once; impairment/capitalized costs excluded by declared estimate scope. Consistency is semantic, not proved by ratios |
| Annual investment / `capex_percent_revenue` | Named FY2026 cash PP&E starting amount/configuration considered alongside official spending outlook; no trailing average | Cash PP&E USD200bn, then configured cash growth +25%,−4%,−8%,−10%; new financed operating additions = 2.5% cash PP&E, separately estimated. Sum and divide by full annual revenue | Preserves infrastructure surge. Cash PP&E excludes principal already; do not subtract principal again. Acquisitions/disposals excluded. Cash settlements already in PP&E are not added as creditors/WC. Software within PP&E estimate, no second addition; finance additions not liability movements. Missing scope/configuration blocks |
| Annual WC / `change_in_operating_nwc_percent_revenue` | Mixed retained cash movements not definition-compatible calibration; no historical reconstruction prerequisite | Configured 20% × annual incremental revenue / full annual revenue; signed releases allowed | Excludes tax, capital creditors, acquisition settlement, financial collateral and financing; not balance-sheet NWC or second CFO deduction; absence is unresolved, not zero |
| Constant WACC | Dated Treasury 10y par proxy and Damodaran Treasury-based implied ERP; each required or explicitly configured as convention | `(rf+beta*ERP)*equity_weight + (rf+spread)*(1-tax_shield)*debt_weight`; beta1.10, spread75bp, target equity96%/debt4%, shield20% configured | Not observed issuer beta/market weights; no regression claimed. Monthly ERP/daily yield different dates. Treasury includes sovereign risk; no adjusted-RF ERP mixing. Shield applied once; weights must sum1 |
| Terminal nominal USD growth / `terminal_growth` | Long-run modeling convention, no current quote | Independent configured3%, not year-five growth or forced WACC spread | Macro/productivity risk; g≥WACC remains invalid; never clamp |
| Terminal margin / `terminal.operating_margin` | Mature operating convention | Independent29%, includes SBC/service leases | No automatic Year5 copying; setting equality is an explicit configuration |
| Terminal tax / `terminal.operating_tax_rate` | Mature operating convention | Independent21% | Not an automatic reported ETR or cash tax |
| Terminal D&A / `terminal.d_and_a_percent_revenue` | Mature expense convention | Independent16% | Asset renewal/commissioning and acquired-amortization scope uncertain |
| Terminal investment / `terminal.investment_percent_revenue` | Same forecast investment definition | Independent23% | Not solved to obtain value; assess jointly with D&A/WC/g. No observed ROIC asserted |
| Terminal WC / `terminal.working_capital_cash_requirement_percent_revenue` | Same incremental cash convention | 20%×g/(1+g), full terminal revenue denominator | Independent terminal rule, not copied Year5; signed possible |
| EV/EBIT exit / `exit_ev_ebit_multiple` | No supported mature exit measurement | Missing; user may explicitly override | Current/historical/implied multiple is not selected exit assumption; Gordon can run |
| Optional bridge assets/claims/shares | Existing Stage C definitions and qualified populations | Unresolved, no automatic values or omission approvals | No EV→equity/per-share by default; awards, eligibility, claims/settlements remain potentially unbounded |

Every field carries rule, operands, selected periods/source IDs, estimate versus
reported/derived basis, availability state and limitation. Required configuration
may be null, producing a typed gap. `AVAILABLE_ESTIMATE` does not mean approved.
`CONFIGURED_CONVENTION`, `MISSING_EVIDENCE`, `INCOMPATIBLE_DEFINITION`,
`UNSUPPORTED_PREPARATION`, `STALE`, `USER_OVERRIDE` remain distinct. Freshness is
measured against an explicit reviewed-date/max-age policy, not the wall clock
silently changing deterministic outputs. A stale profile requires review/adoption.

## Diagnostics and alternatives

Report annual CAGR separately from each annual rate. Show cash versus financed
investment and expense D&A operands. Terminal net reinvestment = investment−D&A+WC;
compare g×NOPAT/net reinvestment as an **implied incremental return diagnostic**,
not a measured historical ROIC or proof of completeness. Flag negative net
reinvestment with positive growth, material terminal dependence and the unmatched
acquisition cash/perimeter. Never change inputs to clear a diagnostic. A simplified
D&A rule cannot establish full commissioning or useful-life consistency.

Bear/Bull are `diagnostic-offset-v1`: all five annual growth and margin rates
respectively shift by −2/+2 percentage points and WACC +1/−1 point. All other
inputs inherit Base, including independent terminal ratios. This stresses the
case, not statistically calibrated economics, probabilities or guaranteed ordering.
Offsets are named configuration, not hidden constants; no clamp. Inherited WC,
D&A and investment ratios are held fixed in these diagnostics: the Base dollar
schedules and 20% incremental-WC relation are not regenerated for stressed growth. Existing engine
validation remains authoritative. Generated axes use diagnostic ±1pp WACC and
±0.5pp g, or ±2× exit multiple once explicitly entered; centered on active case,
editable, never silently truncated/clamped. Invalid cells keep reasons.

## Lifecycle and handoff

GOOGL loads a separate proposed profile without calculation; other issuers stay
unset. Edits—including equal-value edits—are explicit overrides; per-field reset
restores only that generated field. Annual paths remain annual. Base changes flow
to nonoverridden scenario fields with their declared diagnostic transform.
Refresh first displays old/new generated values and active override; explicit
adoption replaces only nonoverridden inputs and invalidates results. Requests,
charts, Full Model, explanations and downloads bind the submitted revision;
derived values are read-only. No JS DCF is introduced.

See [worked model and usage](googl-preload-worked-model.md) and
[implementation/acceptance](googl-preload-acceptance.md) for actual sources,
commands, results, checks and remaining dependencies.

## Ten-year consumer boundary

The [extended horizon](ten-year-horizon.md) can consume these same five proposed
annual years plus explicit manual years 6–10. This policy supplies no estimates
for the additional years, and its diagnostic scenario offsets do not extend
automatically beyond year five. Profile adoption preserves manually supplied
additional years. Independent terminal ratios remain proposed and require
review for their use after a longer horizon. No source/history approval changes.
