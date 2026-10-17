# LRCX — five-year historical-input review

**PROPOSED ONLY. No new selection/assumption is active; no company completion.**

[Machine source package](lrcx-analyst-input-package.json) / [ONE consolidated approval sheet](../semiconductor-software-review-batch-results.md) / [issuer record](LRCX.md). Source baseline `67545e76752a42c4800aa32b10445441a09366f1`; actual review UTC `2026-10-17T21:23:08+00:00`; source/review revision `098aff581e84e803344fa5fe3efb3ad065b9d0117eb1deb0e6d741f7846e2615`. Existing policies replay only within their original scope.

## Exact frozen selections and evidence

|FY|Annual dates|Exact accession / form|Primary receipt|Instance receipt|
|---|---|---|---|---|
|2022|2021-06-28 through 2022-06-26|0000707549-22-000107 / 10-K|[/artifacts/64](../evidence/preparation-statement-acquisition.json#/artifacts/64)|[/artifacts/62](../evidence/income-sweep-backlog-acquisition.json#/artifacts/62)|
|2023|2022-06-27 through 2023-06-25|0000707549-23-000102 / 10-K|[/artifacts/65](../evidence/preparation-statement-acquisition.json#/artifacts/65)|[/artifacts/63](../evidence/income-sweep-backlog-acquisition.json#/artifacts/63)|
|2024|2023-06-26 through 2024-06-30|0000707549-24-000106 / 10-K|[/artifacts/66](../evidence/preparation-statement-acquisition.json#/artifacts/66)|[/artifacts/64](../evidence/income-sweep-backlog-acquisition.json#/artifacts/64)|
|2025|2024-07-01 through 2025-06-29|0000707549-25-000075 / 10-K|[/artifacts/67](../evidence/preparation-statement-acquisition.json#/artifacts/67)|[/artifacts/65](../evidence/income-sweep-backlog-acquisition.json#/artifacts/65)|
|2026|2025-06-30 through 2026-06-28|0000707549-26-000037 / 10-K|[/artifacts/68](../evidence/preparation-statement-acquisition.json#/artifacts/68)|[/artifacts/66](../evidence/income-sweep-backlog-acquisition.json#/artifacts/66)|

Receipts retain original response bytes, exact URLs, HTTP200, actual retrieval times and typed SHA256. Facts retain QName/context, exact dates/dimensions, raw amounts, USD/shares/pure units, display scales/signs, decimals and all confirming occurrences. Each source field is at `/periods/N/facts/KEY`; source tables/prose/alternatives and unchanged ledgers bind review judgments, not inferred provenance.

## Source-supported schedule and INACTIVE proposed selections

USDm except shares/ratios. Payment magnitudes are shown as negative cash contributions below; underlying source signs are unchanged. Unknown never means zero.

|Input / role|2022|2023|2024|2025|2026|
|---|---|---|---|---|---|
|Revenue|17227.039|17428.516|14905.386|18435.591|23232.69|
|EBIT|5381.822|5174.86|4263.913|5900.968|8199.795|
|Reported CFO|3099.674|5178.938|4652.269|6173.264|5857.657|
|Limited CFO D&A proxy — PROPOSED|333.739|342.432|359.699|386.277|441.533|
|Cash investment outflow — combined PP&E/intangibles|-546.034|-501.568|-396.67|-759.186|-966.405|
|SBC expense observation|259.064|286.6|293.058|343.371|386.381|
|SBC CFO add-back|259.064|286.6|293.058|343.371|386.381|
|Tax provision|587.828|598.279|532.45|599.912|997.077|
|Pretax source context|5193.114|5109.21|4360.222|5958.129|8262.473|
|Cash taxes net payment|-807.669|-809.748|-991.821|-972.513|-1333.996|
|Cash taxes gross payment|unknown|unknown|unknown|unknown|unknown|
|Cash tax refunds separately|unknown|unknown|unknown|unknown|unknown|
|Gross named current financial captions — PROPOSED|3657.732|5374.697|5847.856|6390.659|5579.171|
|Named financing — PROPOSED, incomplete|5005.83|5011.541|4983.334|4484.505|3734.563|
|Borrowing-note carrying parent — alternative, not additional|4962.459|4965.365|4967.361|4469.364|3722.061|
|Operating lease parent|218.723|237.568|287.716|272.05|387.002|
|Operating lease current|54.11|64.682|64.443|78.707|90.415|
|Operating lease noncurrent|164.613|172.886|223.273|193.343|296.587|
|Finance liability — separate, may be embedded|43.371|46.176|15.973|unknown|unknown|
|Noncash operating ROU additions|121.58|91.592|146.169|81.011|207.172|
|Noncash finance ROU additions|13.868|20.161|226.519|2.884|3.308|
|Capital creditors — not cash paid|80.296|31.899|60.826|80.799|119.605|
|Noncash inventory transfers to PP&E — not a cash-split equation|75.068|76.856|71.267|90.873|125.691|
|Acquisition cash magnitude, not Capex|unknown|119.955|0|0|unknown|
|Pension/benefit liabilities — separate|unknown|unknown|unknown|unknown|unknown|
|Strategic holdings — not free cash|unknown|unknown|unknown|unknown|unknown|
|Deferred-plan obligation — overlapping accrued/other liabilities|280.0|318.0|385.5|423.9|498.5|
|Correlated plan assets — Other assets, no automatic netting|291.3|318.1|393.5|438.8|511.8|

## Existing14-family matrix

S = exact source-supported observation, **not completeness**. P = proposed company treatment, inactive pending consolidated approval. All70 slots remain `financial_complete=false`; accepted peers do not approve these companies.

|Family|2022|2023|2024|2025|2026|
|---|---|---|---|---|---|
|revenue|S|S|S|S|S|
|ebit|S|S|S|S|S|
|depreciation_amortization|P|P|P|P|P|
|cash_capex|P|P|P|P|P|
|reported_cash_flow_working_capital_movements|P|P|P|P|P|
|deferred_taxes|P|P|P|P|P|
|stock_based_compensation|P|P|P|P|P|
|unclassified_cfo_reconciliation_residual|P|P|P|P|P|
|reported_cfo|P|P|P|P|P|
|reported_tax_context|P|P|P|P|P|
|cash_investment_components|P|P|P|P|P|
|debt_lease_components|P|P|P|P|P|
|other_equity_bridge_claims_assets|P|P|P|P|P|
|point_in_time_shares|P|P|P|P|P|

## CFO, movements and tax role checks

|FY|Original parser|Independent displayed check|Movement rows (not completeness)|Historical policy ETR|
|---|---|---|---|---|
|2022|SUPPORTED|Original displayed proof supported|6|0.1131937407882823292537001883648231|
|2023|SUPPORTED|Original displayed proof supported|6|0.1170981423742613828752390291258335|
|2024|SUPPORTED|Original displayed proof supported|6|0.1221153418335121468585773843625393|
|2025|SUPPORTED|Original displayed proof supported|6|0.1006879844326969087107714519104907|
|2026|SUPPORTED|Original displayed proof supported|6|0.1206753716472053826983761399280821|

All displayed checks use independently bound operands, not a residual-defined balance. Original PLTR parser PARTIAL statuses remain unchanged; the separate checks do not redefine movement scope. Reported movements already in CFO are supporting detail, not a second deduction or book ΔNWC. Deferred-tax provision/note observations, displayed deferred rows, tax working-capital rows and cash taxes are distinct; a note amount is not inserted into a reconciliation. ETR nulls/conflicts remain from the unchanged approved policy; no analyst-adjusted ratio or future rate.

## Dated shares and awards — no automatic aggregation

|FY|Source population / actual date|Count|Source decimals|
|---|---|---|---|
|2022|shares:EntityCommonStockSharesOutstanding:2022-08-22:4f53cda1 / 2022-08-22|136987792|INF|
|2022|shares:CommonStockSharesOutstanding:2022-06-26:4f53cda1 / 2022-06-26|136975000|-3|
|2022|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2022-06-26:d9ce98c1 / 2022-06-26|904000|-2|
|2022|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2022-06-26:a21e122e / 2022-06-26|196600|-2|
|2023|shares:EntityCommonStockSharesOutstanding:2023-08-10:4f53cda1 / 2023-08-10|132511701|INF|
|2023|shares:CommonStockSharesOutstanding:2023-06-25:4f53cda1 / 2023-06-25|133297000|-3|
|2023|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2023-06-25:d9ce98c1 / 2023-06-25|896000|-2|
|2023|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2023-06-25:a21e122e / 2023-06-25|182000|-2|
|2024|shares:EntityCommonStockSharesOutstanding:2024-08-22:4f53cda1 / 2024-08-22|129876000|-3|
|2024|shares:CommonStockSharesOutstanding:2024-06-30:4f53cda1 / 2024-06-30|130377000|-3|
|2024|shares:CommonStockSharesOutstanding:2024-06-30:e7683adf / 2024-06-30|130377000|-3|
|2024|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2024-06-30:3de8d43f / 2024-06-30|923000|-3|
|2024|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2024-06-30:d9ce98c1 / 2024-06-30|749000|-3|
|2024|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2024-06-30:a21e122e / 2024-06-30|174000|-3|
|2025|shares:EntityCommonStockSharesOutstanding:2025-08-07:4f53cda1 / 2025-08-07|1265621000|-3|
|2025|shares:CommonStockSharesOutstanding:2025-06-29:4f53cda1 / 2025-06-29|1268740000|-3|
|2025|shares:CommonStockSharesOutstanding:2025-06-29:e7683adf / 2025-06-29|1268740000|-3|
|2025|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2025-06-29:3de8d43f / 2025-06-29|8964000|-3|
|2025|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2025-06-29:d9ce98c1 / 2025-06-29|7212000|-3|
|2025|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2025-06-29:c3e02465 / 2025-06-29|1752000|-3|
|2026|shares:EntityCommonStockSharesOutstanding:2026-08-04:4f53cda1 / 2026-08-04|1251321000|-3|
|2026|shares:CommonStockSharesOutstanding:2026-06-28:4f53cda1 / 2026-06-28|1251278000|-3|
|2026|shares:CommonStockSharesOutstanding:2026-06-28:e7683adf / 2026-06-28|1251278000|-3|
|2026|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2026-06-28:3de8d43f / 2026-06-28|5930000|-3|
|2026|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2026-06-28:d9ce98c1 / 2026-06-28|4714000|-3|
|2026|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2026-06-28:c3e02465 / 2026-06-28|1216000|-3|

Weighted-average basic/diluted EPS counts remain separate facts. Dimensioned confirmations of an unclassed total are not extra classes. A source-reported PLTR aggregate is an observation, not a reconstructed class sum; A/B/F voting/conversion rights do not establish diluted economic counts. LRCX original-as-filed counts straddle October2024 ten-for-one split; no automatic recast.

## Company-specific decisions / limitations

**LRCX-CF — PROPOSED:** Use reported movement detail and independently reconciled CFO; no separately calculated residual and no second movement deduction.

Numerical effect: 3099.674/5178.938/4652.269/6173.264/5857.657 USDm. Consolidated reported CFO is not FCFF, organic cash or cash delta NWC. PLTR four original PARTIAL results remain, alongside independently exact displayed-row checks. Mixed tax/noncurrent/lease/customer populations retained; no residual plug.

**LRCX-DA — PROPOSED:** Select a labeled limited historical CFO D&A proxy, not complete expense-basis D&A.

Numerical effect: 333.739/342.432/359.699/386.277/441.533 USDm. Finance amortization is explicitly included with depreciation under the source policy: do not add7.439/7.899/5.175m again. Separate depreciation/intangible notes are rounded/incomplete later. Alternative strict pure operating expense D&A remains unresolved; no source zero for later not-material amortization.

**LRCX-INV — PROPOSED:** Approve an explicitly BROADER combined PP&E/intangible cash-investment proxy; strict pure-PP&E split stays null and prior negative component-completeness findings unchanged. Unpaid capital80.296/31.899/60.826/80.799/119.605 and inventory transfers75.068/76.856/71.267/90.873/125.691 are separate noncash/timing observations, not a split equation. Alternative reject broader perimeter and keep required narrow investment unresolved.

Numerical effect: 546.034/501.568/396.67/759.186/966.405 USDm payment magnitudes; cash sign -1. Acquisitions, software/intangibles, noncash ROU and capital-creditor timing stay separate. No complete reinvestment subtotal or policy/registry expansion.

**LRCX-SBC — PROPOSED:** Select expense as a labeled cost proxy once, keeping CFO add-back, APIC recognition, capitalization and awards distinct.

Numerical effect: 259.064/286.6/293.058/343.371/386.381 USDm expense; add-back 259.064/286.6/293.058/343.371/386.381 USDm. LRCX note expense uses ShareBasedCompensation rather than an inferred Allocated expense; AMAT FY2025 expense660 versus add-back668. PLTR APIC recognition is not expense. No duplicate cost, rounding adjustment or dilution assumption.

**LRCX-TAX — PROPOSED:** Retain historical provision, cash taxes, deferred rows and existing policy Pretax/ETR separately; select PLTR face provision explicitly.

Numerical effect: 587.828/598.279/532.45/599.912/997.077 USDm provision; cash net 807.669/809.748/991.821/972.513/1333.996 USDm; gross unknown/unknown/unknown/unknown/unknown USDm. PLTR rounded prose alternatives10.1/19.7/21.3/22.7 retain original generic conflicts versus face10.067/19.716/21.255/22.724. No automatic ratio from selected provision or negative pretax; no forecast rate. AMAT cash refunds/tax incentives differ from provision/deferred movements.

**LRCX-CASH — PROPOSED:** Select named gross current financial captions; no unrestricted/excess-cash assertion.

Numerical effect: 3657.732/5374.697/5847.856/6390.659/5579.171 USDm. Cash plus disclosed current Investments FY2022/23; cash-only thereafter, NOT a claim absent investments are zero. Restricted cash251.534/250.316/2.947/16.997/18.772 and correlated plan holdings remain separate. Unknown restrictions/reserves stay unknown. Alternative cash only 3522.001/5337.056/5847.856/6390.659/5579.171 USDm changes known perimeter, not an operating-reserve estimate.

**LRCX-FIN — PROPOSED:** Operating leases as service costs, finance leases as asset financing; select named carrying subtotal with no additional unidentified-borrowing adjustment only if approved.

Numerical effect: 5005.83/5011.541/4983.334/4484.505/3734.563 USDm. Current/noncurrent debt-plus-finance captions include finance leases once; borrowing-only carrying parent is an alternative, not additional. Explicit no CP at year end covers CP only. Finance liability separately43.371/46.176/15.973 then unquantified, not zero. Carrying, principal, fair value and maturity schedules are different measurements. Omitted exposure remains unquantified/unbounded. Alternative leave additional operation unresolved; not reported zero or complete debt.

**LRCX-CLAIMS — PROPOSED:** Retain disclosed named claims/assets, with no additional unidentified/preferred/NCI/pension adjustment beyond bound populations only if approved.

Numerical effect: Named observations remain visible; no valuation deduction or new source zero.. Preserve unfunded deferred-plan obligation280/318/385.5/423.9/498.5 and correlated Other-assets investments291.3/318.1/393.5/438.8/511.8 separately, never automatically netted. Accrued-compensation tag is broader, not that plan. Known pension/OPEB, tax and warranty obligations overlap captions. Potential undisclosed claim size is unbounded; no financial-statement or valuation immateriality inference. Alternative keep omission unapproved.

**LRCX-SHARES — PROPOSED:** Use actual fiscal-end common populations/classes and retain separately dated covers, EPS denominators and awards.

Numerical effect: Exact source counts, dates, dimensions and precision in shares:*; no automatic sum.. LRCX October2024 ten-for-one split and FY2024 53weeks remain original-as-filed boundaries. PLTR A/B/F retain1/10/founder voting, F-to-B conversion and separate reported aggregate; no class equivalence or award/dilution sum. AMAT fiscal52/53weeks/cover dates preserved. Alternative cover dates are not year-end replacements.

No essential new acquisition target identified in this bounded retained review; all ten selected source artifacts are bound. Missing selectors, unknown suballocations, complete expense D&A/reinvestment/lease/claim coverage and proposed omissions remain distinct. Approval may establish a limited historical operation, never a source zero or proof of immateriality. No financial-sufficiency/Phase1 closure or Phase2 consumption claim.

Validation is consolidated in the [batch results](../semiconductor-software-review-batch-results.md); source package JSON is deterministic and proposals remain inactive.
