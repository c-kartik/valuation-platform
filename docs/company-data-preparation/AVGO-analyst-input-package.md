# AVGO — consolidated five-year historical-input review

## Review status and boundary

**Proposed only; no new assumption active.** Five exact frozen annuals /70 family slots: 15 source-supported observation slots and 55 pending company-treatment slots. No company completion or financial-sufficiency certification.

[Exact package](avgo-analyst-input-package.json) / [ONE batch approval sheet](../large-company-review-batch-results.md) / [company record](AVGO.md). All new material judgments are in that single sheet, not separate annual approvals. Review revision `9d80e3196ee38de156902103726ebeaad6c6d93d3be634015ca0f0dd36607c9f`; author/time/source commit are retained in JSON. Existing financial policies, pilot bytes, accepted peer views and CAT SBC exception remain unchanged.

## Exact frozen selections and retained source receipts

|FY|Accession / authoritative annual dates|Original retained primary and instance|
|---|---|---|
|2021|`0001730168-21-000153`; 2020-11-02–2021-10-31|[primary](https://www.sec.gov/Archives/edgar/data/1730168/000173016821000153/avgo-20211031.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/8`; [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016821000153/avgo-20211031_htm.xml) / [retained-income-instance-acquisition.json](../evidence/retained-income-instance-acquisition.json) `/artifacts/5`|
|2022|`0001730168-22-000118`; 2021-11-01–2022-10-30|[primary](https://www.sec.gov/Archives/edgar/data/1730168/000173016822000118/avgo-20221030.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/9`; [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016822000118/avgo-20221030_htm.xml) / [retained-income-instance-acquisition.json](../evidence/retained-income-instance-acquisition.json) `/artifacts/6`|
|2023|`0001730168-23-000096`; 2022-10-31–2023-10-29|[primary](https://www.sec.gov/Archives/edgar/data/1730168/000173016823000096/avgo-20231029.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/10`; [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016823000096/avgo-20231029_htm.xml) / [retained-income-instance-acquisition.json](../evidence/retained-income-instance-acquisition.json) `/artifacts/7`|
|2024|`0001730168-24-000139`; 2023-10-30–2024-11-03|[primary](https://www.sec.gov/Archives/edgar/data/1730168/000173016824000139/avgo-20241103.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/11`; [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016824000139/avgo-20241103_htm.xml) / [retained-income-instance-acquisition.json](../evidence/retained-income-instance-acquisition.json) `/artifacts/8`|
|2025|`0001730168-25-000121`; 2024-11-04–2025-11-02|[primary](https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102.htm) / [independent-validation-document-acquisition.json](../evidence/independent-validation-document-acquisition.json) `/artifacts/9`; [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102_htm.xml) / [retained-income-instance-acquisition.json](../evidence/retained-income-instance-acquisition.json) `/artifacts/9`|

CIK1730168, form10-K. Every source has exact original-body SHA256/digest type, byte length, actual receipt UTC/status and URL. Every fact retains taxonomy, context/occurrence, dates/dimensions, raw unit/sign/scale and source decimals; confirming and competing observations remain. The JSON links exact immutable preparation-ledger records with SHA256. Identity alone is not fact verification.

## Fourteen-family matrix

S = source-supported observation, **not complete financial coverage**. P = concrete inactive company-specific proxy/classification/omission decision. Null source requirements remain even if a proposal would make a specific operation unnecessary.

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
|reported_tax_context|S|S|S|S|S|
|cash_investment_components|P|P|P|P|P|
|debt_lease_components|P|P|P|P|P|
|other_equity_bridge_claims_assets|P|P|P|P|P|
|point_in_time_shares|P|P|P|P|P|

## Source schedule and proposed selections

Monetary values are **USD millions**; calculations inherit operand precision, never improve it. Cash payments below are negative contributions; original positive XBRL payment representations and−1 multipliers remain separately recorded. Calculated named populations/proxies are **proposed**, not accepted totals.

|Input / role|2021|2022|2023|2024|2025|
|---|---:|---:|---:|---:|---:|
|Revenue|27,450|33,203|35,819|51,574|63,887|
|EBIT (LLY registered derived)|8,519|14,225|16,207|13,463|25,484|
|Reported consolidated CFO|13,764|16,736|18,085|19,962|27,537|
|Proposed LIMITED D&A proxy|5,942|4,888|3,749|9,860|8,636|
|CFO mixed amortization/ROU|5,502|4,455|3,333|9,417|8,201|
|Depreciation expense/support|539|529|502|593|574|
|Named intangible amortization|unknown|unknown|unknown|unknown|8,062|
|Finance amortization SUPPORT|16|18|16|27|unknown|
|Cash PP&E, source perimeter|-443|-424|-452|-548|-623|
|Cash acquisitions, net|-8|-246|-53|-25,978|-0|
|Noncash finance ROU additions|15|1|0|49|unknown|
|Noncash operating ROU additions|92|16|28|1,165|220|
|SBC expense, proposed cost proxy once|1,704|1,533|2,171|5,670|7,568|
|SBC CFO addback|1,704|1,533|2,171|5,741|7,568|
|Tax provision / benefit, exact face|29|939|1,015|3,748|-397|
|Reported pretax|6,765|12,434|15,097|9,916|22,729|
|Cash tax IncomeTaxesPaidNet|-775|-908|-1,782|-3,155|-2,589|
|Deferred tax note/reconciliation observation|-997|-45|-501|1,965|-2,033|
|Proposed current financial captions|12,163|12,416|14,189|9,348|16,178|
|Proposed named financing, NOT complete debt|39,730|39,515|39,229|67,566|65,136|
|Operating lease liability, NOT added|543|463|419|1,350|1,325|
|Operating current liability, child|83|74|60|207|144|
|Operating noncurrent liability, child|460|389|359|1,143|1,181|
|Finance lease liability, embedded, NOT added|65|59|49|39|unknown|
|Separate benefit population OtherPostretirementBenefitPlansDefinedBenefitMember:DefinedBenefitPlanFundedStatusOfPlan|-9|unknown|unknown|unknown|unknown|
|Separate benefit population PensionPlansDefinedBenefitMember:DefinedBenefitPlanFundedStatusOfPlan|-5|17|4|-36|-39|
|Movement rows already in CFO (count)|3|3|3|3|3|
|Independent displayed CFO status|SUPPORTED|SUPPORTED|SUPPORTED|SUPPORTED|SUPPORTED|
|CFO residual (no separate operation proposed)|null — never0|null — never0|null — never0|null — never0|null — never0|

Expense observations and CFO reconciliation rows are not additive costs. Deferred-tax note/provision values need not equal mixed displayed cash adjustments; the independent CFO proof retains the actual displayed rows. Tax accounting ETR/operands and policy scope are linked through `preparation_ledger_evidence`, not suggested future rates. No investment, liquidity, financing or claims aggregate is called complete.

## Company-specific choices, overlap and comparability

The source operating statement separately expenses acquisition amortization in cost of revenue and operating expense. Proposed narrow D&A includes those captions plus depreciation, not the mixed intangible/ROU CFO row. FY2024 VMware integration, large acquisition consideration, restructuring and a 53-week year change the perimeter; do not label year-on-year growth organic. FY2025 cash acquisition zero is actually reported for that caption, not a conclusion of no acquisition/noncash activity. Retain source-business disposals and all note commitments separately.

Debt face captions include finance liabilities; FY2021 note parent39,665 excludes finance65 while the face current/noncurrent total39,730 includes it. Later source tags explicitly combine debt/capital leases. Never add leases twice. Gross principal, carrying discounts/hedges and fair value are not interchangeable.

The proposed financial balance is cash/equivalents only, not a finding that investments, restrictions or reserves are zero. Recognized benefit-plan net funded positions (pension −5/17/4/−36/−39m, plus FY2021 other-postretirement−9m) and gross recognized claims remain distinct, not an additional sum. Preferred carrying-zero observations retain their precise caption, not a blanket unidentified-claims zero. SBC2024 expense5,670 and CFO5,741 differ71; no plug. Original2021–23 share counts precede the2024 ten-for-one split; the2023 later cover count also follows VMware issuance. No automatic historical restatement.

## Dated common shares — actual counts, not millions

|Selected filing FY|Observation / count / precision|
|---|---|
|2021|2021-10-31: 413,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2021-11-26: 412,873,968 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|
|2022|2022-10-30: 418,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2022-11-25: 417,886,140 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|
|2023|2023-10-29: 414,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2023-11-24: 468,140,569 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|
|2024|2024-11-03: 4,686,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2024-11-29: 4,687,356,156 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|
|2025|2025-11-02: 4,741,000,000 shares (CommonStockSharesOutstanding, decimals `INF`); 2025-11-28: 4,741,273,799 shares (EntityCommonStockSharesOutstanding, decimals `INF`)|

## Unresolved inputs and stopping condition

Complete expense D&A, reinvestment, unidentified borrowing/claims, unknown restrictions/operating reserve and exhaustive lease-cash coverage stay null. Reported amounts are not invented when a selector is absent or conflicting. Source-binding exceptions distinguish unselected selectors from true missing disclosure; exact evidence remains in alternatives, supporting note rows and original ledgers. No zero/immateriality conclusion follows silence.

All15 selected source bodies/receipts and the existing LLY review reports are retained: **no essential acquisition target identified in this bounded pass; zero requests**. Remaining unquantified allocations are not a fabricated document backlog. Stop for ONE consolidated user review. A future source repair needs a precise demonstrated defect; a broader numerical/economic treatment needs explicit separate approval. No automatic research chain, support reclassification, Phase1 closure or Phase2 use.

## Validation

Focused batch tests replay exact identities, original receipts and every selected occurrence; original policy operands and LLY refresh checks, source arithmetic/signs, non-overlap boundaries, proxy/null distinctions, chronological dates, split/comparative limits, deterministic JSON and inactive decision revisions are checked. Final actual test counts and unchanged-peer preservation are recorded in the batch results.
