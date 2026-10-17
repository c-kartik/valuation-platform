# PLTR — five-year historical-input review

**PROPOSED ONLY. No new selection/assumption is active; no company completion.**

[Machine source package](pltr-analyst-input-package.json) / [ONE consolidated approval sheet](../semiconductor-software-review-batch-results.md) / [issuer record](PLTR.md). Source baseline `67545e76752a42c4800aa32b10445441a09366f1`; actual review UTC `2026-10-17T21:23:08+00:00`; source/review revision `a70ada61223488cfad135636a86a3298151ff7341d8df2c07fade92ce2ec70e5`. Existing policies replay only within their original scope.

## Exact frozen selections and evidence

|FY|Annual dates|Exact accession / form|Primary receipt|Instance receipt|
|---|---|---|---|---|
|2021|2021-01-01 through 2021-12-31|0001193125-22-050913 / 10-K|[/artifacts/69](../evidence/preparation-statement-acquisition.json#/artifacts/69)|[/artifacts/16](../evidence/selected-filing-identity-acquisition.json#/artifacts/16)|
|2022|2022-01-01 through 2022-12-31|0001321655-23-000011 / 10-K|[/artifacts/70](../evidence/preparation-statement-acquisition.json#/artifacts/70)|[/artifacts/18](../evidence/selected-filing-identity-acquisition.json#/artifacts/18)|
|2023|2023-01-01 through 2023-12-31|0001321655-24-000022 / 10-K|[/artifacts/71](../evidence/preparation-statement-acquisition.json#/artifacts/71)|[/artifacts/20](../evidence/selected-filing-identity-acquisition.json#/artifacts/20)|
|2024|2024-01-01 through 2024-12-31|0001321655-25-000022 / 10-K|[/artifacts/72](../evidence/preparation-statement-acquisition.json#/artifacts/72)|[/artifacts/22](../evidence/selected-filing-identity-acquisition.json#/artifacts/22)|
|2025|2025-01-01 through 2025-12-31|0001321655-26-000011 / 10-K|[/artifacts/73](../evidence/preparation-statement-acquisition.json#/artifacts/73)|[/artifacts/24](../evidence/selected-filing-identity-acquisition.json#/artifacts/24)|

Receipts retain original response bytes, exact URLs, HTTP200, actual retrieval times and typed SHA256. Facts retain QName/context, exact dates/dimensions, raw amounts, USD/shares/pure units, display scales/signs, decimals and all confirming occurrences. Each source field is at `/periods/N/facts/KEY`; source tables/prose/alternatives and unchanged ledgers bind review judgments, not inferred provenance.

## Source-supported schedule and INACTIVE proposed selections

USDm except shares/ratios. Payment magnitudes are shown as negative cash contributions below; underlying source signs are unchanged. Unknown never means zero.

|Input / role|2021|2022|2023|2024|2025|
|---|---|---|---|---|---|
|Revenue|1541.889|1905.871|2225.012|2865.507|4475.446|
|EBIT|-411.046|-161.201|119.966|310.403|1414.015|
|Reported CFO|333.851|223.737|712.183|1153.865|2134.473|
|Limited CFO D&A proxy — PROPOSED|14.897|22.522|33.354|31.587|26.145|
|Cash PP&E outflow|-12.627|-40.027|-15.114|-12.634|-33.882|
|SBC expense observation|778.215|564.798|475.903|691.638|684.033|
|SBC CFO add-back|778.215|564.798|475.903|691.638|684.033|
|Tax provision — face selection proposed|31.885|10.067|19.716|21.255|22.724|
|Pretax source context|-488.494|-361.027|237.091|489.173|1657.368|
|Cash taxes net payment|-4.131|-2.904|-13.515|-16.179|-21.686|
|Cash taxes gross payment|unknown|unknown|unknown|unknown|unknown|
|Cash tax refunds separately|unknown|unknown|unknown|unknown|unknown|
|Gross named current financial captions — PROPOSED|2524.827|2633.675|3674.179|5229.987|7177.043|
|Named financing — PROPOSED, incomplete|0|0|0|0|0|
|Operating lease parent|260.073|249.404|229.392|239.219|229.338|
|Operating lease current|39.927|45.099|54.176|43.993|45.864|
|Operating lease noncurrent|220.146|204.305|175.216|195.226|183.474|
|Finance liability — separate, may be embedded|unknown|unknown|unknown|unknown|unknown|
|Noncash operating ROU additions|34.606|28.169|28.112|58.32|37.784|
|Noncash finance ROU additions|unknown|unknown|unknown|unknown|unknown|
|Capital creditors — not cash paid|unknown|unknown|unknown|unknown|unknown|
|Acquisition cash magnitude, not Capex|unknown|unknown|0|unknown|unknown|
|Pension/benefit liabilities — separate|unknown|unknown|unknown|unknown|unknown|
|Strategic holdings — not free cash|unknown|unknown|32.6|64.9|170.0|
|Recorded NCI — separate from acquisition-date consideration|unknown|77.111|85.404|91.132|100.743|
|Restricted current cash — outside face cash|36.628|16.244|0.37|7.704|2.518|
|Restricted noncurrent cash — outside face cash|39.612|12.551|18.69|13.708|25.111|

## Existing14-family matrix

S = exact source-supported observation, **not completeness**. P = proposed company treatment, inactive pending consolidated approval. All70 slots remain `financial_complete=false`; accepted peers do not approve these companies.

|Family|2021|2022|2023|2024|2025|
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
|2021|PARTIAL|SUPPORTED / difference 0|9|-0.06527204018882524657416467756001097|
|2022|PARTIAL|SUPPORTED / difference 0|9|unresolved|
|2023|PARTIAL|SUPPORTED / difference 0|9|unresolved|
|2024|PARTIAL|SUPPORTED / difference 0|9|unresolved|
|2025|SUPPORTED|Original displayed proof supported|5|unresolved|

All displayed checks use independently bound operands, not a residual-defined balance. Original PLTR parser PARTIAL statuses remain unchanged; the separate checks do not redefine movement scope. Reported movements already in CFO are supporting detail, not a second deduction or book ΔNWC. Deferred-tax provision/note observations, displayed deferred rows, tax working-capital rows and cash taxes are distinct; a note amount is not inserted into a reconciliation. ETR nulls/conflicts remain from the unchanged approved policy; no analyst-adjusted ratio or future rate.

## Dated shares and awards — no automatic aggregation

|FY|Source population / actual date|Count|Source decimals|
|---|---|---|---|
|2021|shares:EntityCommonStockSharesOutstanding:2022-02-17:1765640c / 2022-02-17|1929183497|INF|
|2021|shares:EntityCommonStockSharesOutstanding:2022-02-17:1ca1ddc4 / 2022-02-17|99929842|INF|
|2021|shares:EntityCommonStockSharesOutstanding:2022-02-17:76589e5a / 2022-02-17|1005000|INF|
|2021|shares:CommonStockSharesOutstanding:2021-12-31:1765640c / 2021-12-31|1926589000|INF|
|2021|shares:CommonStockSharesOutstanding:2021-12-31:1ca1ddc4 / 2021-12-31|99880000|INF|
|2021|shares:CommonStockSharesOutstanding:2021-12-31:76589e5a / 2021-12-31|1005000|INF|
|2021|shares:CommonStockSharesOutstanding:2021-12-31:4f53cda1 / 2021-12-31|2027474000|INF|
|2021|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2021-12-31:3de8d43f / 2021-12-31|153749000|INF|
|2022|shares:EntityCommonStockSharesOutstanding:2023-02-14:1765640c / 2023-02-14|1997726022|INF|
|2022|shares:EntityCommonStockSharesOutstanding:2023-02-14:1ca1ddc4 / 2023-02-14|102656175|INF|
|2022|shares:EntityCommonStockSharesOutstanding:2023-02-14:76589e5a / 2023-02-14|1005000|INF|
|2022|shares:CommonStockSharesOutstanding:2022-12-31:1765640c / 2022-12-31|1995414000|INF|
|2022|shares:CommonStockSharesOutstanding:2022-12-31:1ca1ddc4 / 2022-12-31|102656000|INF|
|2022|shares:CommonStockSharesOutstanding:2022-12-31:76589e5a / 2022-12-31|1005000|INF|
|2022|shares:CommonStockSharesOutstanding:2022-12-31:e7683adf / 2022-12-31|2099075000|INF|
|2022|shares:CommonStockSharesOutstanding:2022-12-31:4f53cda1 / 2022-12-31|2099075000|INF|
|2022|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2022-12-31:3de8d43f / 2022-12-31|126426000|INF|
|2023|shares:EntityCommonStockSharesOutstanding:2024-02-13:1765640c / 2024-02-13|2110901985|INF|
|2023|shares:EntityCommonStockSharesOutstanding:2024-02-13:1ca1ddc4 / 2024-02-13|100826007|INF|
|2023|shares:EntityCommonStockSharesOutstanding:2024-02-13:76589e5a / 2024-02-13|1005000|INF|
|2023|shares:CommonStockSharesOutstanding:2023-12-31:1765640c / 2023-12-31|2096982000|INF|
|2023|shares:CommonStockSharesOutstanding:2023-12-31:1ca1ddc4 / 2023-12-31|102141000|INF|
|2023|shares:CommonStockSharesOutstanding:2023-12-31:76589e5a / 2023-12-31|1005000|INF|
|2023|shares:CommonStockSharesOutstanding:2023-12-31:e7683adf / 2023-12-31|2200128000|INF|
|2023|shares:CommonStockSharesOutstanding:2023-12-31:4f53cda1 / 2023-12-31|2200128000|INF|
|2023|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2023-12-31:3de8d43f / 2023-12-31|82262000|INF|
|2023|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2023-12-31:09e53081 / 2023-12-31|1976000|INF|
|2024|shares:EntityCommonStockSharesOutstanding:2025-02-07:1765640c / 2025-02-07|2248950826|INF|
|2024|shares:EntityCommonStockSharesOutstanding:2025-02-07:1ca1ddc4 / 2025-02-07|95400680|INF|
|2024|shares:EntityCommonStockSharesOutstanding:2025-02-07:76589e5a / 2025-02-07|1005000|INF|
|2024|shares:CommonStockSharesOutstanding:2024-12-31:1765640c / 2024-12-31|2242389000|INF|
|2024|shares:CommonStockSharesOutstanding:2024-12-31:1ca1ddc4 / 2024-12-31|95401000|INF|
|2024|shares:CommonStockSharesOutstanding:2024-12-31:76589e5a / 2024-12-31|1005000|-3|
|2024|shares:CommonStockSharesOutstanding:2024-12-31:e7683adf / 2024-12-31|2338795000|INF|
|2024|shares:CommonStockSharesOutstanding:2024-12-31:4f53cda1 / 2024-12-31|2338795000|-3|
|2024|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2024-12-31:3de8d43f / 2024-12-31|65236000|INF|
|2024|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2024-12-31:09e53081 / 2024-12-31|577000|INF|
|2025|shares:EntityCommonStockSharesOutstanding:2026-02-10:1765640c / 2026-02-10|2291470751|INF|
|2025|shares:EntityCommonStockSharesOutstanding:2026-02-10:1ca1ddc4 / 2026-02-10|99199960|INF|
|2025|shares:EntityCommonStockSharesOutstanding:2026-02-10:76589e5a / 2026-02-10|1005000|INF|
|2025|shares:CommonStockSharesOutstanding:2025-12-31:1765640c / 2025-12-31|2290987000|INF|
|2025|shares:CommonStockSharesOutstanding:2025-12-31:1ca1ddc4 / 2025-12-31|99200000|INF|
|2025|shares:CommonStockSharesOutstanding:2025-12-31:76589e5a / 2025-12-31|1005000|INF|
|2025|shares:CommonStockSharesOutstanding:2025-12-31:e7683adf / 2025-12-31|2391192000|-3|
|2025|shares:CommonStockSharesOutstanding:2025-12-31:4f53cda1 / 2025-12-31|2391192000|INF|
|2025|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2025-12-31:3de8d43f / 2025-12-31|41644000|INF|
|2025|shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2025-12-31:09e53081 / 2025-12-31|118000|INF|

Weighted-average basic/diluted EPS counts remain separate facts. Dimensioned confirmations of an unclassed total are not extra classes. A source-reported PLTR aggregate is an observation, not a reconstructed class sum; A/B/F voting/conversion rights do not establish diluted economic counts. LRCX original-as-filed counts straddle October2024 ten-for-one split; no automatic recast.

## Company-specific decisions / limitations

**PLTR-CF — PROPOSED:** Use reported movement detail and independently reconciled CFO; no separately calculated residual and no second movement deduction.

Numerical effect: 333.851/223.737/712.183/1153.865/2134.473 USDm. Consolidated reported CFO is not FCFF, organic cash or cash delta NWC. PLTR four original PARTIAL results remain, alongside independently exact displayed-row checks. Mixed tax/noncurrent/lease/customer populations retained; no residual plug.

**PLTR-DA — PROPOSED:** Select a labeled limited historical CFO D&A proxy, not complete expense-basis D&A.

Numerical effect: 14.897/22.522/33.354/31.587/26.145 USDm. Keep noncash operating-lease expense, impairment and investment losses separate. Alternative pure expense D&A requires complete scope not established by CFO; do not infer amortization by subtraction.

**PLTR-INV — PROPOSED:** Select direct cash PP&E; keep marketable/private investments, strategic commercial customer agreements and gold purchases/disposal separate. Customer/investee cash may be commercially related, not an invented loan population or ordinary Capex. Alternative broader investment requires a separately defined scope; no double deduction with CFO.

Numerical effect: 12.627/40.027/15.114/12.634/33.882 USDm payment magnitudes; cash sign -1. Acquisitions, software/intangibles, noncash ROU and capital-creditor timing stay separate. No complete reinvestment subtotal or policy/registry expansion.

**PLTR-SBC — PROPOSED:** Select expense as a labeled cost proxy once, keeping CFO add-back, APIC recognition, capitalization and awards distinct.

Numerical effect: 778.215/564.798/475.903/691.638/684.033 USDm expense; add-back 778.215/564.798/475.903/691.638/684.033 USDm. LRCX note expense uses ShareBasedCompensation rather than an inferred Allocated expense; AMAT FY2025 expense660 versus add-back668. PLTR APIC recognition is not expense. No duplicate cost, rounding adjustment or dilution assumption.

**PLTR-TAX — PROPOSED:** Retain historical provision, cash taxes, deferred rows and existing policy Pretax/ETR separately; select PLTR face provision explicitly.

Numerical effect: 31.885/10.067/19.716/21.255/22.724 USDm provision; cash net 4.131/2.904/13.515/16.179/21.686 USDm; gross unknown/unknown/unknown/unknown/unknown USDm. PLTR rounded prose alternatives10.1/19.7/21.3/22.7 retain original generic conflicts versus face10.067/19.716/21.255/22.724. No automatic ratio from selected provision or negative pretax; no forecast rate. AMAT cash refunds/tax incentives differ from provision/deferred movements.

**PLTR-CASH — PROPOSED:** Select named gross current financial captions; no unrestricted/excess-cash assertion.

Numerical effect: 2524.827/2633.675/3674.179/5229.987/7177.043 USDm. FY2021/22 current marketable securities are public equities, later balances include Treasury securities: preserve composition change and private/strategic/gold scope. Restricted CDs and customer relationships remain outside gross face selection; do not subtract already excluded restrictions again. Unknown restrictions/reserves stay unknown. Alternative cash only 2290.674/2598.54/831.047/2098.524/1423.796 USDm changes known perimeter, not an operating-reserve estimate.

**PLTR-FIN — PROPOSED:** Operating leases as service costs, finance leases as asset financing; select named carrying subtotal with no additional unidentified-borrowing adjustment only if approved.

Numerical effect: 0/0/0/0/0 USDm. Source explicitly says no debt outstanding after2021 repayment and in later liquidity notes. Select the disclosed named debt population only; retain undrawn facilities, operating leases and customer deposits separately. Do not infer debt from mis-tagged FY2021 financing cash rows or net flows. Unquantified additional/finance obligations remain unknown. Omitted exposure remains unquantified/unbounded. Alternative leave additional operation unresolved; not reported zero or complete debt.

**PLTR-CLAIMS — PROPOSED:** Retain disclosed named claims/assets, with no additional unidentified/preferred/NCI/pension adjustment beyond bound populations only if approved.

Numerical effect: Named observations remain visible; no valuation deduction or new source zero.. Preserve NCI, legal/tax/customer claims, investment commitments and strategic holdings. Preferred authorization and incorrectly tagged share counts do not prove outstanding preferred value; face preferred dollar row and equity note control the proposed scope. No separate pension claim is a proposed omission, not source absence. Potential undisclosed claim size is unbounded; no financial-statement or valuation immateriality inference. Alternative keep omission unapproved.

**PLTR-SHARES — PROPOSED:** Use actual fiscal-end common populations/classes and retain separately dated covers, EPS denominators and awards.

Numerical effect: Exact source counts, dates, dimensions and precision in shares:*; no automatic sum.. LRCX October2024 ten-for-one split and FY2024 53weeks remain original-as-filed boundaries. PLTR A/B/F retain1/10/founder voting, F-to-B conversion and separate reported aggregate; no class equivalence or award/dilution sum. AMAT fiscal52/53weeks/cover dates preserved. Alternative cover dates are not year-end replacements.

No essential new acquisition target identified in this bounded retained review; all ten selected source artifacts are bound. Missing selectors, unknown suballocations, complete expense D&A/reinvestment/lease/claim coverage and proposed omissions remain distinct. Approval may establish a limited historical operation, never a source zero or proof of immateriality. No financial-sufficiency/Phase1 closure or Phase2 consumption claim.

Validation is consolidated in the [batch results](../semiconductor-software-review-batch-results.md); source package JSON is deterministic and proposals remain inactive.
