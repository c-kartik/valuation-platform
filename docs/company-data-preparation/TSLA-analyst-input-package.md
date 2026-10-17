# TSLA — consolidated five-year historical-input review

## Review status and boundary

**Proposed only; no new assumption active.** Five exact frozen annuals /70 family slots: 15 source-supported observation slots and 55 pending company-treatment slots. No company completion or financial-sufficiency certification.

[Exact package](tsla-analyst-input-package.json) / [ONE batch approval sheet](../large-company-review-batch-results.md) / [company record](TSLA.md). All new material judgments are in that single sheet, not separate annual approvals. Review revision `6e7e14287a73d636cc959b90ff50873f348449cdcab04378bc94e7b316011059`; author/time/source commit are retained in JSON. Existing financial policies, pilot bytes, accepted peer views and CAT SBC exception remain unchanged.

## Exact frozen selections and retained source receipts

|FY|Accession / authoritative annual dates|Original retained primary and instance|
|---|---|---|
|2021|`0000950170-22-000796`; 2021-01-01–2021-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/17`; [instance](https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/12`|
|2022|`0000950170-23-001409`; 2022-01-01–2022-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1318605/000095017023001409/tsla-20221231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/18`; [instance](https://www.sec.gov/Archives/edgar/data/1318605/000095017023001409/tsla-20221231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/13`|
|2023|`0001628280-24-002390`; 2023-01-01–2023-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/19`; [instance](https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/14`|
|2024|`0001628280-25-003063`; 2024-01-01–2024-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/20`; [instance](https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/15`|
|2025|`0001628280-26-003952`; 2025-01-01–2025-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/21`; [instance](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/16`|

CIK1318605, form10-K. Every source has exact original-body SHA256/digest type, byte length, actual receipt UTC/status and URL. Every fact retains taxonomy, context/occurrence, dates/dimensions, raw unit/sign/scale and source decimals; confirming and competing observations remain. The JSON links exact immutable preparation-ledger records with SHA256. Identity alone is not fact verification.

## Fourteen-family matrix

S = source-supported observation, **not complete financial coverage**. P = concrete inactive company-specific proxy/classification/omission decision. Null source requirements remain even if a proposal would make a specific operation unnecessary.

|Family|2021|2022|2023|2024|2025|
|---|---|---|---|---|---|
|revenue|S|S|S|S|S|
|ebit|S|S|S|S|S|
|depreciation_amortization|P|P|P|P|P|
|cash_capex|P|P|P|P|P|
|reported_cash_flow_working_capital_movements|P|P|P|P|P|
|deferred_taxes|S|S|S|S|S|
|stock_based_compensation|P|P|P|P|P|
|unclassified_cfo_reconciliation_residual|P|P|P|P|P|
|reported_cfo|P|P|P|P|P|
|reported_tax_context|P|P|P|P|P|
|cash_investment_components|P|P|P|P|P|
|debt_lease_components|P|P|P|P|P|
|other_equity_bridge_claims_assets|P|P|P|P|P|
|point_in_time_shares|P|P|P|P|P|

## Source schedule and proposed selections

Monetary values are **USD millions**; calculations inherit operand precision, never improve it. Cash payments below are negative contributions; original positive XBRL payment representations and−1 multipliers remain separately recorded. Calculated named populations/proxies are **proposed**, not accepted totals.

|Input / role|2021|2022|2023|2024|2025|
|---|---:|---:|---:|---:|---:|
|Revenue|53,823|81,462|96,773|97,690|94,827|
|EBIT (LLY registered derived)|6,523|13,656|8,891|7,076|4,355|
|Reported consolidated CFO|11,497|14,724|13,256|14,923|14,747|
|Proposed LIMITED D&A proxy|2,911|3,747|4,667|5,368|6,148|
|CFO impairment-inclusive row|2,911|3,747|4,667|5,368|6,148|
|Depreciation expense/support|1,910|2,420|3,330|4,120|5,030|
|Named intangible amortization|51|unknown|unknown|unknown|unknown|
|Finance amortization SUPPORT|415|493|506|409|118|
|Cash PP&E, source perimeter|-6,482|-7,158|-8,898|-11,339|-8,527|
|Cash acquisitions, net|-0|-0|-64|-0|-0|
|Noncash finance ROU additions|486|58|10|144|0|
|Noncash operating ROU additions|818|1,059|2,170|1,808|1,643|
|SBC expense, proposed cost proxy once|2,121|1,560|1,812|1,999|2,825|
|SBC CFO addback|2,121|1,560|1,812|1,999|2,825|
|Tax provision / benefit, exact face|699|1,132|-5,001|1,837|1,423|
|Reported pretax|6,343|13,719|9,973|8,990|5,278|
|Cash tax IncomeTaxesPaidNet|unknown|unknown|unknown|unknown|-1,232|
|Cash tax IncomeTaxesPaid, caption scope retained|-561|-1,203|-1,119|-1,331|unknown|
|Deferred tax note/reconciliation observation|-149|-196|-6,349|477|123|
|Proposed current financial captions|17,707|22,185|29,094|36,563|44,059|
|Proposed named financing, NOT complete debt|6,834|3,099|5,230|8,213|8,376|
|Operating lease liability, NOT added|2,039|2,649|4,343|5,410|6,343|
|Operating current liability, child|368|485|672|807|954|
|Operating noncurrent liability, child|1,671|2,164|3,671|4,603|5,389|
|Finance lease liability, embedded, NOT added|1,492|1,054|573|335|223|
|Recognized NCI|826|785|733|704|670|
|Redeemable NCI, separate scope|568|409|242|63|58|
|Movement rows already in CFO (count)|7|7|5|5|5|
|Independent displayed CFO status|SUPPORTED|SUPPORTED|SUPPORTED|SUPPORTED|SUPPORTED|
|CFO residual (no separate operation proposed)|null — never0|null — never0|null — never0|null — never0|null — never0|

Expense observations and CFO reconciliation rows are not additive costs. Deferred-tax note/provision values need not equal mixed displayed cash adjustments; the independent CFO proof retains the actual displayed rows. Tax accounting ETR/operands and policy scope are linked through `preparation_ledger_evidence`, not suggested future rates. No investment, liquidity, financing or claims aggregate is called complete.

## Company-specific choices, overlap and comparability

Recommend one consolidated manufacturing/energy/leasing historical perimeter, not an invented industrial carve-out. Nonrecourse asset-backed/solar/cash-equity funding remains with related financing assets, operating-lease vehicles and recognized NCI. Lessor sales-type net receivable observations (including2025 net240, current130/noncurrent110m) are not cash or lessee debt; current/noncurrent are children of240, not another240 addition. Known restricted-current/noncurrent cash is retained separately from the gross current balance.

The impairment-inclusive CFO row is an expressly broader proposed proxy, not verified pure D&A or reversal of frozen negative/scope findings. Expense depreciation, finance amortization, leased-vehicle/solar depreciation and impairments are separate support. No manufactured split or subtraction-based amortization. The cash PP&E caption's stated net-of-sales perimeter is retained; later2025 comparatives11,342/8,899 do not replace the originally selected2024/2023 values11,339/8,898. Accrued purchases mix populations, not a cash or pure capital-creditor estimate.

Named financing uses current/noncurrent face carrying captions already including finance leases. The LongTermDebt tag6,584 in2025 is noncurrent, not complete debt; note principal8,177, its carrying adjustments and capacity are not interchangeable. Finance223 is not added again. Source note populations retain recourse/nonrecourse distinctions, security/collateral and funding exposures; no netting against held assets.

Exact2023 face tax benefit−5,001 is distinct from rounded−5,000, with no rounding plug; original generic conflicts remain unchanged. Earlier cash-tax caption explicitly says net of refunds despite the IncomeTaxesPaid concept name. Three-for-one2022 split, actual cover dates and2025 award issuance break naive share comparability. Awards/contingent rights are not diluted closing shares or an automatic economic charge.

## Dated common shares — actual counts, not millions

|Selected filing FY|Observation / count / precision|
|---|---|
|2021|2022-01-31: 1,033,507,611 shares (EntityCommonStockSharesOutstanding, decimals `0`)|
|2022|2022-12-31: 3,164,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2023-01-25: 3,164,102,701 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|
|2023|2023-12-31: 3,185,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2024-01-22: 3,184,790,415 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|
|2024|2024-12-31: 3,216,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2025-01-22: 3,216,517,037 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|
|2025|2025-12-31: 3,751,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2026-01-23: 3,752,431,984 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|

## Unresolved inputs and stopping condition

Complete expense D&A, reinvestment, unidentified borrowing/claims, unknown restrictions/operating reserve and exhaustive lease-cash coverage stay null. Reported amounts are not invented when a selector is absent or conflicting. Source-binding exceptions distinguish unselected selectors from true missing disclosure; exact evidence remains in alternatives, supporting note rows and original ledgers. No zero/immateriality conclusion follows silence.

All15 selected source bodies/receipts and the existing LLY review reports are retained: **no essential acquisition target identified in this bounded pass; zero requests**. Remaining unquantified allocations are not a fabricated document backlog. Stop for ONE consolidated user review. A future source repair needs a precise demonstrated defect; a broader numerical/economic treatment needs explicit separate approval. No automatic research chain, support reclassification, Phase1 closure or Phase2 use.

## Validation

Focused batch tests replay exact identities, original receipts and every selected occurrence; original policy operands and LLY refresh checks, source arithmetic/signs, non-overlap boundaries, proxy/null distinctions, chronological dates, split/comparative limits, deterministic JSON and inactive decision revisions are checked. Final actual test counts and unchanged-peer preservation are recorded in the batch results.
