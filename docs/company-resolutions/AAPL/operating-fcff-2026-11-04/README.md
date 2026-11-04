# Apple — standardized operating FCFF adoption, November 4, 2026

**Scoped result: five historical FCFF calculations are available in the current platform under one disclosed standardized definition. Apple overall remains OPEN.**

The original FY2024/25 CFO method required undisclosed gross interest. The implemented solution replaces the entire five-year historical consumer with the approved operating-income route, rather than splicing two new observations into the old basis. No interest estimate is required. The [report](report.html) and [decision record](decision.json) distinguish the original error/dependency, treatments, source facts, implementation refinement and numerical effects.

| FY | Standardized FCFF, USD billions |
|---|---:|
| 2021 |93.41|
| 2022 |108.44|
| 2023 |99.84|
| 2024 |115.68|
| 2025 |95.12|

## Applied methodology and qualifications

`FCFF = EBIT × (1 − reported tax provision / pretax income) + reported combined D&A − cash PP&E − increase in defined current NWC`.

Current NWC = current assets − cash − current marketable securities − current liabilities + commercial paper + current term debt + current finance-lease liability + current operating-lease liability.

The original plan preferred separating current taxes. Exact FY2020/21 splits are unavailable. Implementation therefore refines that preference to **include current tax accruals uniformly** in the aggregate NWC population. This is a material disclosed modeling choice under the implementation mandate, not a claim of separate prior user approval or discovery of exact operating cash taxes. FY2024's current-tax increase contributes+17.782B; FY2025's reversal contributes−13.585B versus tax-excluded diagnostics. Mixed Other current balances also remain by convention, without being certified individually pure operating.

The cash-statement combined D&A is used consistently. The later FY2024 note sum exceeds it by355M; no plug or exact expense tie is asserted. Cash PP&E is the declared investment perimeter; noncash financed investment is not invented. SBC stays expensed and lease principal is not deducted again. The result is source-derived standardized FCFF, not a separately reported or assumption-free exact cash figure.

## Source and runtime trace

[Source ledger](source-ledger.json):25 annual and80 opening/closing balance observations, exact fiscal dates, USD units, source rounding, original primary/instance contexts and hashes. Six consecutive balance dates support five NWC changes. Missing early-year tax diagnostics stay null. [Adopted calculations](adopted-history.json) retain exact rational outputs and a pinned runtime copy. [Legacy comparison](legacy-comparison.json) explains all five differences from CFO−cash PP&E with zero bridge differences and no residual plug.

Runtime validation recalculates all operands, verifies the pin and continuity, then publishes the same five values to the chart catalog and historical FCFF/FCFE endpoint. The sealed runtime explicitly includes both calculation modules and the pinned overlay. Catalog remains bounded at96KiB (up from80KiB for the three-company source/legacy metadata). Current history labels explain the method. Historical-to-forecast FCFF CAGR and automatic forecast calibration stay disabled.

The original source bank, accepted history, old projection and earlier decisions are preserved. `legacy_cfo_fcff` retains all prior values and both nulls. FCFE, Meta/Alphabet cash flows, forward assumptions and enterprise values are unchanged. Current three-company counts are20 calculations available under their stated conventions,10 provisional FCFE,0 current selected-method FCFF gaps. The original strict audit's17 failed cells are an unchanged prior-basis snapshot, not the new count of missing chart FCFF.

## Replay

From repository root:

```sh
PYTHONPATH=src .venv/bin/python scripts/build_apple_operating_history.py --check
PYTHONPATH=src .venv/bin/python scripts/reconcile_apple_operating_history.py --check
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/operating-fcff-2026-11-04/independent-review/audit.py
PYTHONPATH=src .venv/bin/python -m unittest tests.review.test_apple_operating_history -v
PYTHONPATH=src .venv/bin/python scripts/render_apple_operating_report.py
```

The builder reads retained SEC bodies offline. Intentional future updates require a new reviewed version: preserve this folder and prior adoption, bind exact new source contexts/dates, review tax/Other/D&A/investment populations, regenerate and independently check, then explicitly update the source pin and runtime allowlist. Never carry a new year merely by ticker or replace missing operands with zero.

[Independent review](independent-review/README.md), [policy review](policy-review/README.md), [validation](validation.json) and [live browser results](browser-results.json) record separate checks. `browser-review.mjs` replays against the running private workspace using an installed Playwright module/browser; optional `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE` select local installations.

The scoped missing-bar calculation/runtime issue passes. Exact expanded unlevered cash reconstruction, complete FCFE financing classification, expense/investment alignment, forecast comparability and equity/per-share clearance remain separate open matters. This adoption does not call the company or project complete.
