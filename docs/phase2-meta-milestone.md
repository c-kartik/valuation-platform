# Phase 2 — META scope-qualified end-to-end testing milestone

**Completed first-company testing milestone; checkpoint documentation 2026-10-18.**
The implemented workflow supports historical anchor → editable manual forecast →
FCFF → DCF → enterprise value → explicit equity bridge → value/share. Assumptions
remain separate from financial formulas. Synthetic tests and separately authorized,
temporary META-anchored operating and equity/share trials exercised this path.

This completes the **first-company, scope-qualified end-to-end testing milestone**.
It does not certify complete historical or financial-input sufficiency, investment
readiness, complete claims coverage or fully diluted fair value. It selects no
permanent META Base case/default and changes no historical source or approval.
The [Phase 1 universe pause](phase1-universe-pause-checkpoint.md) remains in force.

## Implemented boundary

[Case intake](../src/valuation_platform/valuation/case_inputs.py) keeps
`analyst-case-v1` valid with unchanged EV-only JSON. `analyst-case-v2` explicitly
requests `EQUITY_PER_SHARE`, reusing the existing Stage C component, observation,
coverage and share models. Missing/unresolved requested inputs fail without
silently downgrading to EV. Validation alone performs no valuation calculation.
Explicit runs use the existing Stage A/B/C engines and preserve submitted inputs,
source/decision references, component signs, exclusions and null omissions.

The [CLI](../scripts/run_analyst_case.py) defaults to full-precision JSON;
`--format summary` renders the same results with labeled USD millions, actual
share units and USD/share, isolated Decimal display rounding and no DCF formulas.
Both formats retain exclusive output creation and protected-path rules.
References and declared coverage/class/award compatibility authenticate no
approval and cannot detect hidden economic overlap or prove completeness.

The runnable [synthetic EV](../examples/valuation/synthetic-base.json) and
[synthetic equity](../examples/valuation/synthetic-equity.json) examples are
separate from the incomplete [META EV](../examples/valuation/meta-fy2025-unset.json)
and [META equity](../examples/valuation/meta-fy2025-equity-unset.json) templates.
Both META templates retain all 37 numerical forecast/WACC/terminal inputs unset;
the equity template also retains unresolved component/share selections and
coverage. There is no runnable META case or saved META valuation output here.

## Prior temporary trial — historical validation record only

The following records the disclosed temporary trials in the task conversation;
it is not a newly executed case, permanent forecast policy, approval or test log.
Temporary inputs/results were kept outside the repository and removed. The
reported calculations and choices below remain **temporary, assumption-led trial
results**, even where their underlying historical observations are reported facts.
No current-price comparison, rating or approved price target was produced.

| Binding | Disclosed trial basis |
| --- | --- |
| Company / period | META, CIK 1326801; FY2025, 2025-01-01–2025-12-31 |
| Historical anchor | 10-K `0001628280-26-003942`; actual retained revenue **200,966,000,000 USD**, scale 1, precision `-6` |
| Analytical date / information cutoff | **2025-12-31 / 2026-01-29**; later-filed information, not a contemporaneous backtest |
| Retained authority | [Historical schedule](company-data-preparation/META-analyst-input-package.md), [effective package](company-data-preparation/meta-analyst-input-package.json), `/periods/4/facts/revenue` and `/current_history`; exact source/audit bindings remain in the [input review](phase2-meta-base-input-review.md) |
| Economic conventions | [Consumer contract](phase2-meta-base-consumer-contract.md): `meta-base-fcff-v1`, `fiscal-end-annual-gordon-v1`, `meta-base-equity-bridge-v1` |

### Operating assumptions used in the temporary trial

U = user-accepted provisional FY2026 amounts; E = agent-selected estimates;
D = ratios calculated from those amounts and the reported anchor. All table
rates are percentages; displayed repeating ratios are rounded, while the trial
used Decimal divisions at precision 50/HALF_EVEN without intermediate rounding.
No historical arithmetic averages were used as forecast defaults.

| Temporary input | FY2026 | FY2027 E | FY2028 E | FY2029 E | FY2030 E | Terminal E |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Revenue growth | 26.887135% D | 18% | 14% | 10% | 7% | 3% |
| Operating margin | 35.098039% D | 35% | 36% | 37% | 38% | 37% |
| Operating tax | 16% E | 17% | 18% | 19% | 20% | 21% |
| Expense D&A / revenue | 11.098039% D | 14% | 16% | 17% | 17% | 18% |
| Investment / revenue | 49.803922% E/D | 44% | 36% | 30% | 25% | 24% |
| WC cash requirement / full revenue | 0.75% E | 0.60% | 0.50% | 0.40% | 0.30% | 0.15% |

U amounts were FY2026 revenue **255bn**, expenses **165.5bn**, EBIT **89.5bn**
and expense-aligned D&A **28.3bn**. The exact derived inputs were
`255/200.966−1`, `89.5/255` and `28.3/255`. E investment was **127bn**:
management-definition spending budget **125bn** (selected midpoint of guidance)
less estimated finance principal **1bn**, plus distinct new financed operating
assets **3bn**. These forward components are estimates, not reported amounts.

Constant WACC was **10% E**, rounded from a 10.0052% build: dated Treasury proxy
4.18%, start-2026 ERP 4.23%, assumed beta 1.45, debt cost 5.25%, target equity/debt
weights 95/5 and 21% debt tax shield. The dated-source basis was disclosed in the
prior trial; this checkpoint acquires no evidence or new market inputs.

Growth moderation, commissioning/depreciation and later operating leverage were
judgments, not guidance. SBC remained expensed once. Operating leases stayed
service costs; finance depreciation was added back once, with principal/interest
outside FCFF. WC used full revenue, excluding financing/tax/noncash items and
capital-creditor payments already included in cash PP&E. Historical CFO D&A
remained a limited proxy, not complete expense calibration.

The trial's explicit software simplification expensed a **2.5bn E** FY2026
purchased-license cash budget, growing with revenue, within analytical margins;
it was not also invested or newly amortized. Existing intangible amortization
remained in D&A. This was not a detailed GAAP forecast or software tax-timing model.
Net venture/service operating-cost allowances **0.25/0.35/0.50/2.0/3.0bn E** were
embedded in margins, with the Louisiana lease ramp from 2029. Unscheduled funding,
guarantees and equity-method investment value were outside the named reference.

### Named reference bridge and temporary results

All money below is USD billions, except the explicitly labeled per-share result.
R = retained reported amount; P = measurement/policy proxy; O = omission from
this limited calculation, not reported zero. Package references use
`F=/periods/4/facts`, `N=/periods/4/passages`.

| Temporary reference choice | Amount / treatment | Origin and scope |
| --- | ---: | --- |
| Cash/current marketables | 35.873 +45.719 =81.592 | R components, calculated total; `F/cash`, `F/marketable_current` |
| Three-month operating reserve | −34.300 | P: `(165.5−28.3)/4`, retaining SBC; not measured minimum cash or a second reserve for FCFF deficits |
| Eligible liquidity | **+47.292** | P: total less reserve; separately restricted populations outside selected cash are not deducted again (`N/9–11`) |
| Senior Notes | **−57.220** | R fiscal-end fair-value estimate (`N/1`), selected measurement; carrying/face and financing totals are alternatives, not additions |
| Finance leases | **−1.184** | P: reported carrying liability (`F/finance_lease`) as economic-value proxy, counted once |
| Holdings / DTA additions | O | Potential assets forgone; carrying amounts are not economic PVs or proof of zero benefits |
| Other claims / venture / existing awards | O | No numerical deduction in this reference; scope exclusions and potentially unbounded omissions, not completeness or absence |
| Issued common shares | **2.530bn shares** | R fiscal-end aggregate `F/shares:CommonStockSharesOutstanding:2025-12-31:e7683adf`; assumed A/B 1:1 economic equivalence with no control premium |

**Temporary trial results only:** operating EV approximately **945.742bn**,
comprising explicit-period PV **94.379bn** plus terminal PV **851.364bn**;
terminal contribution approximately **90.02%**. Named scoped equity was
**934.630bn =945.742bn +47.292bn −57.220bn −1.184bn**, using unrounded engine
values internally, yielding approximately **369.42 USD per dated basic common
share**. This is before omitted legacy/venture claims and award adjustments;
it is not fully diluted fair value, an approved target or a permanent Base case.

The prior review separately tested cash reserve, holdings-carrying and Notes
measurement alternatives; legal/tax payment-versus-bridge representations; and
unit claim/earned-share diagnostics. Its cash-policy interval **369.42–378.46
USD/basic share** varied only one-to-three-month reserves, with other choices
fixed. Those endpoints are policy definitions, **not bounds on total META value**.
The earlier 20% holdings haircut, guarantee probabilities, acquisition-payment
allowance and 25%/90% award fractions were withdrawn as established valuation
inputs. No probability distribution or defensible total-value range was inferred.

For settlement diagnostics, original aggregate rates did not prove inclusion of
opening legal/tax payments. Tests explicitly interpreted them as recurring/core
cash flows before the named payments, and charged each payment either in the
forecast or through equivalent bridge PV, never both. Full payment in FY2026
for legal accruals or FY2028 for uncertain tax positions was hypothetical, not
source-supported timing. The tax variant was a one-period cash-tax-load diagnostic,
not an approved normalized operating rate; Treasury yields alone do not value
risky claims. Actual settlement coverage and payment populations remain open.

## Verification attribution and remaining work

The **prior temporary scope-qualified trial reported 694 independent
exact-rational comparisons**, covering A/B/C arithmetic and settlement equivalence
within 0.000001 in base-unit comparisons. This checkpoint does **not** rerun or
invent that trial log; this documentation preserves its disclosed conversation
record. Removed temporary cases/results are not archived as evidence or approvals.

The checkpoint runs the affected synthetic regression and preservation checks
using the README's `PYTHONPATH=src python -m unittest` invocation, restricted to:

```sh
PYTHONPATH=src .venv/bin/python -m unittest \
  tests.valuation.test_equity_case_inputs tests.valuation.test_case_inputs \
  tests.valuation.test_case_summary tests.valuation.test_bridge \
  tests.valuation.test_discounting tests.valuation.test_forecast \
  tests.valuation.test_assumptions tests.analyst.test_company_batch_activation -v
```

**Checkpoint result: 118 tests PASS** (12 equity-intake, 16 EV-intake, 13 summary,
21 bridge, 15 discounting, 14 forecast, 18 assumptions and 9 company
approval/preservation). Executed numerical cases were synthetic; no META trial
or full corpus suite was rerun. Additional checkpoint checks confirmed EV-only
JSON compatibility with starting HEAD, unchanged engine/historical bytes, both
37-unset META templates, local links/anchors, whitespace and intended staged scope.

Remaining financial limitations include incomplete historical D&A/reinvestment
calibration, unsettled reserve/eligibility policies, legacy legal/tax settlement
overlap, unidentified financing/other claims, unpaid acquisition obligations,
venture asset/funding/guarantee economics and pre-anchor award/service allocation.
Potentially unbounded omitted liabilities prevent describing the overall result
as conservative. Future service already expensed through SBC must not be charged
again through automatic full-RSU dilution, repurchases or an award claim.
The [input review](phase2-meta-base-input-review.md) and original proposals remain
historical review material, not newly approved standing selections.

The **next milestone is separately scoped GOOGL validation**: inspect its approved
historical package and generalize only the necessary consumer boundary. No GOOGL
review, evidence acquisition, adapter or implementation is started here.
Reusable scenarios, sensitivities and reverse DCF remain later capabilities;
temporary diagnostics did not implement them. Completing every eligible company
is not a prerequisite for the engine's defined incremental Phase 2 milestones.
