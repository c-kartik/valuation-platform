# Apple — stage3 historical tax, NWC and forecast-basis review

Date:2026-11-04. Parent company status: **OPEN**.

**Implemented:** the latest [user approval](../approval.json) explicitly adopts the uniform tax-inclusive historical NWC convention and retains the separate existing forward tax policy. Neither policy is awaiting another manual approval in this scope. **Not established:** exact operating cash-tax allocation or full economic alignment of the historical and forecast definitions. S1 is not cleared by an algebraic bridge.

## Original conflict and approved treatment

The selected historical FCFF allocates reported consolidated tax provision to EBIT using provision/pretax income, and deducts the change in noncash/non-debt current-balance NWC including current income-tax accruals. That is a source-derived standardized convention. It does not measure actual unlevered cash taxes. Separately, the forecast uses explicit analyst tax assumptions and an incremental-sales working-capital model. Treating historical tax settlements or broad balance changes as recurring forecast drivers would mix populations and could duplicate cash movements.

1. Replayed the selected FY2021–25 provision, pretax income, reported net cash taxes and six current/deferred jurisdiction components directly from retained primary filing and XBRL facts. All accounting provision components reconcile exactly. No historical tax expense or cash payment is restated.
2. Replayed the four disclosed current-tax balances at their exact dates. The2022 amount is from the2023 comparative disclosure;2020/21 current-tax splits remain missing. Missing is never zero. The adopted all-year NWC convention is retained rather than selectively excluding tax in later years.
3. Bound the2024/25 State Aid accounting-reconciliation facts and the2025 filing's charge/escrow/restricted-cash commentary. No unsupported allocation of all payable or cash-tax movements to State Aid is made.
4. Recorded explicit adoption of the existing forward18%→20% tax path, independent terminal20%, and Base5% incremental-sales cash coefficient. These are analyst assumptions, not sustainable rates disclosed by Apple. No new numerical assumption is introduced.
5. Generated fresh Base/Bear/Bull engine cases and reconciled each FY2025 standardized historical result to its first FY2026 forecast using signed differences in EBIT, allocated tax, D&A, investment and working-capital cash requirement. This explains the arithmetic; it does not certify economic equivalence or calibrate the forecast to history.
6. Kept the existing cross-basis FCFF CAGR prohibition. Preserved historical runtime amounts, forecast inputs and forecast outputs.

## Source and calculation results

USD billions; positive tax provision means expense, negative deferred component means benefit.

|FY|Current tax provision|Deferred provision|Total provision|Cash taxes paid, net|
|---|---:|---:|---:|---:|
|2021|19.301|−4.774|14.527|25.385|
|2022|18.405|0.895|19.300|19.573|
|2023|19.765|−3.024|16.741|18.679|
|2024|32.780|−3.031|29.749|26.102|
|2025|22.058|−1.339|20.719|43.369|

Provision, cash taxes, payables and escrow are different measurement populations. Their differences are not, by themselves, missing cash or an adjustment to FCFF. Exact operating cash-tax allocation remains **UNRESOLVED_NOT_INFERRED**.

The State Aid reconciliation item is a10.246B expense in FY2024 and a0.486B benefit in FY2025. The2025 note describes a rounded10.2B net2024 charge,15.8B payable via escrow release, a4.8B US foreign tax credit and a0.823B decrease in unrecognized tax benefits. The preceding year's restricted cash/securities are separately described as2.6B and13.2B. These note populations and rounded totals must not be substituted for an exact operating cash-tax schedule.

Disclosed current income-tax accruals:2022=6.552B,2023=8.819B,2024=26.601B,2025=13.016B. The corresponding all-tax-accrual NWC effects are+2.267B in2023,+17.782B in2024 and−13.585B in2025 relative to otherwise identical tax-excluded NWC. The2021/22 effects are unavailable because the opening/current-tax populations are not fully disclosed. No tax-excluded counterfactual is adopted.

## First-forecast component bridge

FY2025 historical standardized FCFF: **95.1238918925B**. Its reported-ETR EBIT tax allocation is an accounting convention, while FY2026 uses an18% forecast assumption.

|Signed change fromFY2025 toFY2026, B|Base|Bear|Bull|
|---|---:|---:|---:|
|EBIT|24.708757|12.488289|37.262155|
|Negative allocated-tax change|−7.627468|−5.427784|−9.887080|
|D&A|1.599333|1.370465|1.828201|
|Negative investment change|3.559013|3.716602|3.401424|
|Negative working-capital cash-requirement change|12.768907|12.826929|12.710886|
|Total FCFF change|35.008543|24.974502|45.315586|
|FY2026 forecast FCFF|130.132435|120.098393|140.439478|

Full-precision bridges and signed source operands are in [results.json](results.json). Engine serialization residuals are below1e−30USD, explicitly identified as numerical precision, never an economic balancing plug.

The Base WC/revenue ratio is derived from5% of incremental sales. Existing Bear/Bull policy inherits that ratio and applies it to each scenario's revenue; it does not recalculate5% of each scenario's incremental sales. Their effective first-year incremental-sales coefficients are about5.6060% and4.5272%. This documented scenario behavior is preserved. The differing D&A/investment dollars also reflect existing ratio inheritance.

This bridge spans a reported FY2025 population and a modeled FY2026 business with different scale, investment/expense populations, tax policy and WC definition. It is an **algebraic comparison, not a fully reconciled economic attribution**. No separate cash-tax line is subtracted from an already-taxed FCFF and no CFO-based working-capital deduction is added a second time.

## Replay, validation and remaining scope

From the repository root:

```
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/tax/replay.py --check
PYTHONPATH=src .venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/tax/test_replay.py -v
```

PASS: five annual schedules, four exact-date tax balances, two State Aid facts, three official-source commentary bindings, three independently generated scenario cases and five financial invariant tests. The workpaper records input SHA256 values and checks that all bound inputs remain unchanged during replay. Its assertions reject missing-as-zero, new cash-tax deductions and a material unexplained bridge residue.

Parent Apple review remains OPEN. In particular, the source evidence does not establish exact operating cash-tax allocation; the algebraic bridge does not resolve the D&A/investment population differences or strict history/forecast comparability. Other stages retain their own financing, award/claim and valuation-use limitations. No outgoing investor-relations message, policy-file mutation, source-package mutation or runtime financial change occurred in this stage.
