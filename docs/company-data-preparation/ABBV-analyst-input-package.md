# ABBV — five-year historical-input review package

**PROPOSED ONLY. No new company selection or assumption is active.** Five exact frozen annuals/70 existing-family slots; source facts and prior generic policies are not amended.

[Machine package](abbv-analyst-input-package.json) / [ONE consolidated approval sheet](../pharma-network-tech-review-batch-results.md) / [company record](ABBV.md). Review revision `c0fc03eb9f0a17015dc0c04929068d854131d75b5c71c699181e74540f6cbd94`; source baseline `94b40c1753c5ed354933028793248ca31052b3db`, actual review UTC `2026-10-17T20:52:33+00:00`. Exact author/source/period/sign/precision and occurrence metadata are retained.

## Exact selections and source index

|FY|Selected accession / authoritative annual dates|Retained original primary and instance|
|---|---|---|
|2021|`0001551152-22-000007`; 2021-01-01–2021-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1551152/000155115222000007/abbv-20211231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/50` SHA256 `3674f4f10d4370476d8548ed462f7484d2ebe26e81c53a4126f791cb7aae2ecd`; [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115222000007/abbv-20211231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/52` SHA256 `7abc84402c0dff8e72567ec5435155cbbaee1ed7515c90c03ac68f8064a9aa45`|
|2022|`0001551152-23-000011`; 2022-01-01–2022-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1551152/000155115223000011/abbv-20221231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/51` SHA256 `0849115680416450586eb191e47050567a2791cde8b03b9345b32caf80421ac3`; [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115223000011/abbv-20221231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/53` SHA256 `f8b2afc6f176d84bf7c7ea82750ebacb6c3f253099e1c9ea6830339170aa3de3`|
|2023|`0001551152-24-000011`; 2023-01-01–2023-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1551152/000155115224000011/abbv-20231231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/52` SHA256 `289ac7462ce01482ebf19e4f325ead36a030d82f0961aced18cc2526f4e0adfb`; [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115224000011/abbv-20231231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/54` SHA256 `e7e2f2b04de02799b28d5cba6fb9c55a0a47b569befcd83ac0627c5c43b0db72`|
|2024|`0001551152-25-000020`; 2024-01-01–2024-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1551152/000155115225000020/abbv-20241231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/53` SHA256 `3dd113ef5c880bbdff930861c29d0e9886a1a61fe74e6291c309a99c170ea3af`; [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115225000020/abbv-20241231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/55` SHA256 `ad9e931f71084a541149c9cfe0d5c892dd9ab3cecc856f1e1875d214f2340022`|
|2025|`0001551152-26-000008`; 2025-01-01–2025-12-31|[primary](https://www.sec.gov/Archives/edgar/data/1551152/000155115226000008/abbv-20251231.htm) / [preparation-statement-acquisition.json](../evidence/preparation-statement-acquisition.json) `/artifacts/54` SHA256 `9706f89b6956498eae157c9a0ec380d835fb25629dfa3e37858807e5e2b06674`; [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115226000008/abbv-20251231_htm.xml) / [income-sweep-backlog-acquisition.json](../evidence/income-sweep-backlog-acquisition.json) `/artifacts/56` SHA256 `29a8df00d312ead28c1d8adf34e3dfcf931d2a230ef79e69d88c7a2bb20011e5`|

## Source schedule and proposed named calculations

USDm unless explicitly shares/pure. Raw cash-payment magnitudes are shown with payment sign−1; no FCFF, cash/debt aggregate certification or complete reinvestment calculation. Each code is a key in `/periods/*/facts` or `/calculations`, with exact independent primary/instance locators; null means not established by that selector, not absent disclosure or zero.

|Source / proposed operation|2021|2022|2023|2024|2025|
|---|---:|---:|---:|---:|---:|
|Face-approved generic Revenue (`revenue`)|56197|58054|54318|56334|61160|
|Reported EBIT (`ebit`)|17924|18117|12757|9137|15075|
|Reported CFO (`cfo`)|22777|24943|22839|18806|19030|
|Depreciation (`depreciation`)|803|778|752|764|762|
|Precise CFO intangible amortization (`cfo_intangible_amortization`)|7718|7689|7946|7622|7377|
|Cash PP&E payment (`cash_capex`)|787|695|777|974|1214|
|Cash business acquisitions (`acquisition`)|525|255|0|17493|204|
|Other investing purchases (`investment_cash`)|1377|539|1223|3024|5237|
|Acquired IPR&D expense (`iprd_expense`)|962|697|778|2757|5016|
|CFO collaboration/IPR&D scope (`upfront_collaboration_adjustment`)|1624|697|778|2757|5016|
|Separate intangible impairment (`intangible_impairment`)|0|770|4229|4476|847|
|SBC expense observation (`sbc_expense`)|692|671|747|911|955|
|CFO SBC add-back (`sbc_addback`)|692|671|747|911|955|
|Tax provision (`tax`)|1440|1632|1377|-570|2364|
|Direct pretax (`pretax`)|12989|13477|6250|3716|6597|
|Cash taxes NET payment (`cash_tax`)|unknown|unknown|unknown|unknown|3626|
|Cash taxes other/gross payment (`cash_tax_gross`)|3648|2988|4702|4064|unknown|
|Corporate face cash (`cash`)|9746|9201|12814|5524|5229|
|Current Investments (`current_investments`)|84|28|2|31|28|
|Borrowing/lease carrying parent (`debt_carrying_parent`)|76670|63270|59385|67144|64997|
|Other disclosed short borrowing (`short_borrowing`)|14|1|0|unknown|2499|
|Finance-lease liability (`finance_lease`)|34|34|42|40|41|
|Operating-lease liability (`op_lease`)|891|920|901|875|883|
|NCI (`nci`)|28|33|37|39|42|
|PROPOSED limited_da_proxy|8521|8467|8698|8386|8139|
|PROPOSED current_financial_captions|9830|9229|12816|5555|5257|
|PROPOSED named_financing|76684|63271|59385|67144|67496|

Reported ETR values/policy operands and exact curated scope proof are in `/periods/*/reported_tax_policy_replay`; they are not future rates. All source values retain original USD scale, sign multiplier, decimals and confirming/competing occurrences. Proposed calculations inherit operand precision; especially CSCO rounded PP&E does not become million-dollar precision.

## Fourteen-family coverage matrix

S=source observation within its reported scope, not completeness. P=proposed company selection/classification; E=essential evidence/operation exception. No pending choice is an acceptance.

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

## Company-specific decisions, overlaps and comparability

Precise CFO depreciation plus intangible amortization gives8,521/8,467/8,698/8,386/8,139 USDm. Rounded note amortization7,700/7,700/7,900/7,600/7,400 would instead give8,503/8,478/8,652/8,364/8,162; differences+18/−11/+46/+22/−23 are source precision/population differences, NOT adjustments. Separate intangible impairment unavailable/770/4,229/4,476/847 is not added; the later FY2021 comparative50 is not spliced. Finance-lease costs described insignificant are not zero and do not prove complete amortization coverage.

Cash PP&E787/695/777/974/1,214, business acquisition525/255/0/17,493/204 and other acquisition/investment1,377/539/1,223/3,024/5,237 stay separate; FY2025 investing caption adds net-of-acquired-cash. Acquired-IPR&D expense962/697/778/2,757/5,016 differs from FY2021 collaboration reconciliation1,624; no expense/cash identity or allocation. Contingent fair-value changes, financing payments698/1,132/752/0/0 and later separately displayed operating payments870/1,995/2,865 have different roles; earlier operating subamounts are not manufactured from note totals.

Debt carrying parent76,670/63,270/59,385/67,144/64,997 equals reported current/noncurrent parts, including finance liabilities34/34/42/40/41 and later financing liability328/378. Separately reported short borrowing14/1/0/unknown/2,499 gives proposed named financing76,684/63,271/59,385/67,144/67,496; FY2024 omission remains a proposal, NOT a reported zero. FY2025 CP499 and term loan2,000 already comprise2,499. Contractual principal75,962/63,128/59,245/66,841/64,503 is not a second debt amount or carrying-value replacement. Contingent fair-value parent14,887/16,384/19,890/21,666/25,374 and Level3/current/noncurrent views overlap; FY2021 current subamount stays unknown, never backsolved. Pension/OPEB3,153/1,638/1,538/1,234/1,410, NCI28/33/37/39/42, litigation and tax exposures remain separately visible. ImmunoGen/Cerevel and collaboration changes make as-filed EBIT/cash/expense history non-organic; no pro-forma recast.

Reported movement rows (not reconstructed book delta NWC) retain displayed cash contribution signs, tax/acquisition/FX/combined-row scope and independent CFO proof. They are already in CFO; no second deduction. Deferred-tax reconciliation is separate from provision, cash taxes and tax-related working-capital movements. No separately calculated residual or source zero is proposed.

### Dated shares and awards

|FY|Population / actual date / source precision|Shares|
|---|---|---:|
|2021|`shares:EntityCommonStockSharesOutstanding:2022-01-31:4f53cda1`; 2022-01-31; decimals `INF`|1768753829|
|2022|`shares:EntityCommonStockSharesOutstanding:2023-01-31:4f53cda1`; 2023-01-31; decimals `INF`|1769399971|
|2023|`shares:EntityCommonStockSharesOutstanding:2024-01-31:4f53cda1`; 2024-01-31; decimals `INF`|1766473359|
|2024|`shares:EntityCommonStockSharesOutstanding:2025-01-31:4f53cda1`; 2025-01-31; decimals `INF`|1765354859|
|2025|`shares:EntityCommonStockSharesOutstanding:2026-02-10:4f53cda1`; 2026-02-10; decimals `INF`|1768169012|

Select fiscal-end common populations where established; retain later cover dates, classes, awards and EPS denominators separately. No automatic class equivalence/aggregation, EPS replacement, dilution estimate or award valuation.

### Unavailable amounts / bounded stop

Complete expense D&A, complete reinvestment/lease coverage, unidentified borrowing/claims, unknown cash restrictions and operating reserves remain explicitly null. Omission assumptions knowingly omit potentially unquantified/unbounded exposure, never immateriality or reported zero. Existing component/caption alternatives and source-binding diagnostics are retained with exact requirements. No new essential acquisition target was established after this bounded pass; all15 selected primary/instance pairs are retained. Missing suballocations do not automatically create another research queue. Any later evidence reopening needs an exact new source or separately authorized treatment.

### Validation / permitted use

Source identity/context/unit/precision/occurrence, independent displayed CFO arithmetic, named calculation/non-overlap, inactive approval/serialization/revision and prior-package preservation checks are recorded in the consolidated batch sheet. This is decision preparation only: no new user approval, runtime overlay, support-class change, company-completion claim, Phase1 closure or Phase2 consumption.
