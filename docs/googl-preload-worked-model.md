# GOOGL reproducible starting model — worked record

Generated October 30, 2026 under [policy v1](googl-preload-methodology.md).
Proposed, assumption-led starting estimates; **screen-grade**, not an investment
recommendation or complete financial-input certification. No current-price comparison,
equity selection, fully diluted value or standing Base forecast. Phase 1 remains paused.

## Basis and retained sources

Economic-content hash: `1c652c65ae2cd9cbf5f726f163963434c17514c6f2b1a0afcf229d059a1768fe`. Same snapshots/configuration/rules
reproduce this hash; generation time is separate. Actual source retrieval dates/times,
body hashes, rights and extraction locators are in the separate
[source manifest](../data/preload/googl-v1/sources/manifest.json) and
[reviewed observations](../data/preload/googl-v1/observations.json). Public access
does not assert redistribution rights; snapshots support local research/attribution.

Actual retained FY2025 revenue **USD402.836bn**, source precision −6, CIK1652044,
10-K accession0001652044-26-000018; exact source/approval binding remains in
the [authoritative package](company-data-preparation/GOOGL-analyst-input-package.md).
GOOG/GOOGL share consolidated preparation but preserve listing A/C distinction.
Model origin December31,2025; information review October30,2026; latest selected
filing published October29. Treasury observed October28; ERP observed October1,
published October8. This uses later information at a retained fiscal-end origin;
it is neither a contemporaneous backtest nor current-market-date fair value.

- [Alphabet Q3 2026 earnings release](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm) — publication 2026-10-28, observation 2026-09-30; retrieved 2026-10-30T13:40:06.263687+00:00.
- [Alphabet official Q3 2026 earnings call transcript](https://abc.xyz/investor/events/event-details/2026/2026-Q3-Earnings-Call-2026-Ujou16CTw9/default.aspx) — publication 2026-10-28, observation 2026-09-30; retrieved 2026-10-30T13:40:06.863876+00:00.
- [Alphabet Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000084/goog-20260930.htm) — publication 2026-10-29, observation 2026-09-30; retrieved 2026-10-30T13:40:07.230635+00:00.
- [Alphabet Q4 and FY2025 earnings release](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000012/googexhibit991q42025.htm) — publication 2026-02-04, observation 2025-12-31; retrieved 2026-10-30T13:40:07.681611+00:00.
- [US Treasury October 2026 daily par yield curve](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202610&type=daily_treasury_yield_curve) — publication not separately retained, observation 2026-10-28; retrieved 2026-10-30T13:40:25.931113+00:00.
- [Aswath Damodaran October 8 2026 market update](https://aswathdamodaran.blogspot.com/2026/10/stock-prices-earnings-and-cashflows-ai.html) — publication 2026-10-08, observation 2026-10-01; retrieved 2026-10-30T13:40:26.745937+00:00.

Reported revenue YTD2026 USD357.269bn; Q3 revenue2026/2025 USD127.577/102.346bn;
Q4FY2025 USD113.828bn. Their momentum extension produces FY2026 revenue below.
Q3EBIT USD40.576bn / revenue supplies the initial margin; no normalization.
YTD PP&E depreciation21.955bn is **incomplete expense D&A**; cash PP&E131.953bn
and combined acquisition/intangible cash34.103bn remain separate. Nine-month2025
revenue289.007bn plus Q4 differs from the retained annual by1m; no plug.
Management call cash CapEx195–205bn and significant2027 increase inform configured
investment, not an automatic investment-scope conversion. Assets not yet in service
145.270bn, finance/intangible depreciation overlap, TPU inventory and acquired
perimeter prevent a claimed complete vintage or organic cash calibration.

## Complete five-year input paths

All values below are **forecast estimates**, not reported future actuals. Growth/
margin combine reported observations with configured fade endpoints. Other operating
rates are generated from explicit policy configuration; source facts are not defaults.
Rates are fractions in engine JSON and percentages below. Exact operands/rules/
periods/limitations are field-level profile data.

| Engine input / all percentages | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Growth (`revenue_growth`) | 23.91112441% | 19.68334331% | 15.45556221% | 11.22778110% | 7.00000000% |
| Operating margin (`operating_margin`) | 31.80510594% | 31.10382945% | 30.40255297% | 29.70127648% | 29.00000000% |
| Operating tax (`forecast_tax_rate`) | 18.00000000% | 18.75000000% | 19.50000000% | 20.25000000% | 21.00000000% |
| Expense D&A/revenue (`d_and_a_percent_revenue`) | 6.61112497% | 9.64162415% | 12.80912335% | 15.36394926% | 17.66724610% |
| Investment/revenue (`capex_percent_revenue`) | 41.06910969% | 42.89351023% | 35.66547080% | 29.50003390% | 24.81311263% |
| WC cash/full revenue (`change_in_operating_nwc_percent_revenue`) | 3.85939915% | 3.28923688% | 2.67731791% | 2.01888071% | 1.30841121% |

Constant WACC **8.94080000%**: `(5.05% + 1.10×3.70%)×96% +
`(5.05% + 0.75%)×(1−20%)×4%`. Treasury/ERP are dated sourced observations;
beta1.10, spread75bp, target96/4 weights and shield20% are configured judgments.
The Treasury-based ERP variant is not mixed with the adjusted-risk-free variant.
WACC is not rounded to the prior8.94% input. No beta regression or market weights claimed.

| Terminal field | Estimate (%) | Basis |
| --- | ---: | --- |
| `terminal_growth` | 3.00000000% | Independent mature configuration; WC =20%×g/(1+g) |
| `operating_margin` | 29.00000000% | Independent mature configuration; WC =20%×g/(1+g) |
| `operating_tax_rate` | 21.00000000% | Independent mature configuration; WC =20%×g/(1+g) |
| `d_and_a_percent_revenue` | 16.00000000% | Independent mature configuration; WC =20%×g/(1+g) |
| `investment_percent_revenue` | 23.00000000% | Independent mature configuration; WC =20%×g/(1+g) |
| `working_capital_cash_requirement_percent_revenue` | 0.58252427% | Independent mature configuration; WC =20%×g/(1+g) |

FY2026 expense D&A33bn and annual commissioning allowance12% of prior scoped
investment are simplified **analyst estimates** including expense finance depreciation
and acquired amortization once. This is not completed historical D&A or a useful-life
model. Cash PP&E200bn then +25/−4/−8/−10%, plus separately estimated financed additions
2.5% of cash PP&E, preserves the AI cycle. Principal already excluded from cash PP&E
is not deducted twice. Software is included within the cash estimate; no extra settlement
or capital-creditor stock adjustment. Acquisition cash is excluded, not silently zero.
Operating tax18→21% is a normalized convention, not reported ETR; SBC and service leases
remain in margin once. Base WC20% of incremental sales is converted to full revenue.

Terminal net reinvestment/revenue =23%−16%+0.58252427%=7.58252427%.
Its implied incremental return diagnostic is about9.064264%, **not measured ROIC**.
Annual expense D&A reaches17.67% of revenue then independently becomes16% terminal;
the transition/retirements are not modeled. That discontinuity and acquired cash/perimeter
need analyst revision before an investment forecast; the calculator cannot prove scope.

Exit multiple: **MISSING_EVIDENCE**; no current/implied multiple becomes a selection.
Bridge eligibility/claims/shares/awards: **UNSUPPORTED_PREPARATION**, with potentially
unbounded omissions. Neither gap blocks Gordon EV. No per-share output is produced.

## Existing-engine result

| USD billions | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| revenue | 499.158617 | 597.409721 | 689.742753 | 767.185559 | 820.888548 |
| ebit | 158.757927 | 185.817301 | 209.699406 | 227.863904 | 238.057679 |
| tax | 28.576427 | 34.840744 | 40.891384 | 46.142441 | 49.992113 |
| nopat | 130.181500 | 150.976557 | 168.808022 | 181.721463 | 188.065566 |
| d_and_a | 33.000000 | 57.600000 | 88.350000 | 117.870000 | 145.028400 |
| investment | 205.000000 | 256.250000 | 246.000000 | 226.320000 | 203.688000 |
| working_capital_cash_requirement | 19.264523 | 19.650221 | 18.466606 | 15.488561 | 10.740598 |
| fcff | -61.083023 | -67.323664 | -7.308585 | 57.782902 | 118.665369 |

Explicit-period PV **-0.091237bn** + terminal PV
**1,421.655358bn** = **1,421.564121bn EV**.
Terminal FCFF 129.596138bn; undiscounted terminal value
2,181.459362bn; terminal contribution **100.00641806%**.
Negative first-three-year FCFF and signed contribution are preserved. Almost all value
comes from the terminal economics; this is an input/economic limitation, not an engine defect.

## Comparison with October29 research

The comparison artifact is attributed prior research, not approved calibration. Its
Base case was rerun through the unchanged engine here solely to compare this policy.
It supplied hand-selected FY2027–30 growth18/14/10/7%, margins30.5/29/29/30%, D&A
dollars55/80/105/125bn and investment258/250/226/197bn, with an FY2026 Q4 growth
judgment of20%. The new rule instead extends observed Q3 momentum into Q4, then
linearly fades growth/margin; it replaces the ad hoc annual dollar path with named
cash-investment and lagged-commissioning rules.

| USD billions | October29 research Base rerun | Reproducible policy v1 |
| --- | ---: | ---: |
| EV | 1,368.221232 | 1,421.564121 |
| Explicit PV | -48.898398 | -0.091237 |
| Terminal PV | 1,417.119631 | 1,421.655358 |
| FY2026 FCFF | -61.023467 | -61.083023 |
| FY2027 FCFF | -75.920017 | -67.323664 |
| FY2028 FCFF | -30.262822 | -7.308585 |
| FY2029 FCFF | 36.313330 | 57.782902 |
| FY2030 FCFF | 105.432987 | 118.665369 |

Prior beta/spread/weights/shield, initial expense D&A33bn, cash PP&E200bn, WC20%
and some long-run conventions remain explicitly configured judgments; they are not
automated SEC forecasts. The prior terminal investment22.29047573% was constructed
from an assumed10% mature incremental return; v1 instead independently configures23%
and reports the implied return. New data are not the main driver: differences chiefly
reflect transformation rules, investment/depreciation paths, terminal reinvestment
and removal of intermediate WACC rounding. Anchor/timing convention is unchanged.
No tuning to the prior EV or Alpha Spread FCFE/P-S outputs.

Bear/Bull shift annual growth and margin by−2/+2pp, WACC by+1/−1pp; other **ratios**
inherit Base. WC is not rederived from stressed incremental revenue. These are named
diagnostic stresses, not approved scenario economics, probabilities or full downside bounds.

## Reproduction and explicit refresh

From repository root; every destination must be new and outside the repository:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src
.venv/bin/python scripts/prepare_preload.py generate /tmp/googl-profile-v1.json
.venv/bin/python scripts/prepare_preload.py export /tmp/googl-profile-v1.json /tmp/googl-run-v1 --run
.venv/bin/python scripts/run_analyst_case.py /tmp/googl-run-v1/request.json --run --format summary
```

Offline reruns do not acquire sources. To propose a policy/configuration update, copy
`data/preload/googl-v1/policy.json` to a new outside file and edit its version/rationale
and named parameters, then:

```sh
.venv/bin/python scripts/prepare_preload.py generate /tmp/googl-candidate-v2.json --policy /tmp/googl-policy-v2.json
.venv/bin/python scripts/prepare_preload.py export /tmp/googl-candidate-v2.json /tmp/googl-run-v2 --run
.venv/bin/python scripts/prepare_preload.py diff /tmp/googl-profile-v1.json /tmp/googl-candidate-v2.json /tmp/googl-diff-v2.json --previous-result /tmp/googl-run-v1/result.json --candidate-result /tmp/googl-run-v2/result.json
```

Explicit bounded primary-source acquisition (identifying SEC user agent; TLS verified):

```sh
export SEC_USER_AGENT="Your project name contact@example.com"
.venv/bin/python scripts/prepare_preload.py acquire https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm /tmp/googl-source-candidate --published-at 2026-10-28 --observation-date 2026-09-30
```

Acquisition stores a new raw body/receipt, **UNREVIEWED**, and never changes a profile.
For a source update, prepare a new outside dataset with `sources/manifest.json`,
reviewed `observations.json` and versioned `policy.json`, preserving prior raw bodies,
explicit supersession, definition/issuer/dimension and period selections. Use
`generate NEW_PROFILE --dataset NEW_DATASET`; diff before adoption. New disclosure
shapes or forward-period definitions require bounded mapping review; v1 is not an
unattended SEC forecast extractor. This avoids guessing expense D&A or new anchors.

To expose a reviewed candidate locally, copy only reviewed new overlay resources into
the allowlist with exact pins, rebuild a new immutable local bundle and restart the
identified local API. The workspace’s Check pinned estimate update is network-free
beyond the local API; it compares, then explicitly adopts nonoverridden estimates.
It never acquires filings or overwrites active overrides. No background refresh.

See [acceptance record](googl-preload-acceptance.md) for current checks, screenshots,
local processes and concrete remaining dependencies.
