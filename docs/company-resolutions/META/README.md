# Meta — manually approved cash-flow treatments

November 3, 2026. CIK 0001326801; FY2021–FY2025. The user approved all five
preferred treatments and requested implementation with company-level documentation.
[Approval](decisions.json), [exact source map](source-map.json), [results](results.json),
[comparison CSV](results.csv), [validation](validation.json).

**Applied:** historical cash investment now nets separately identified PP&E
receipts. The public catalog/chart FCFF increases **245m in FY2022** and **221m in
FY2023**, with a new explicit basis. Original source facts, packages and prior
ledgers are preserved. Five source-bound FCFE calculations are stored for review,
but unclassified financing keeps them provisional. No forward inputs or EV change.

## Issue → approved treatment → applied result

| Issue | Original conflict | Approved treatment and alternative rejected | Applied result / remaining limit |
| --- | --- | --- | --- |
| **META-FCFE-001** | Other financing is −13/+344/−111/−277/+2,220m. Its caption alone does not establish debt content. | Reconcile full financing; include disclosed debt and lease principal once; investigate explanatory notes and calls. Reject treating all Other as debt, all non-debt, or zero. | All five statements reconcile exactly. Lease principal 677/850/1,058/1,969/2,524m is counted once. Reviewed primary disclosures provide context, but no dollar-linked residual allocation; FCFE remains provisional. |
| **META-INV-001** | As-filed gross and later net PP&E presentations differ; mixing them can omit or double-count receipts. | Subtract identified disposal receipts from gross purchases; use a later net amount without subtracting those receipts again. Reject unallocated investing-caption guesses. | Net cash investment 18,567/31,186/27,045/37,256/69,691m. FCFF and provisional FCFE increase 245m/221m in FY2022/23. Three cross-vintage investment comparisons reconcile exactly. Other mixed investing amounts are not asserted to contain zero receipts. |
| **META-FCFE-002** | Later FY2021 Other+1m subsumes original overdraft+14m and Other−13m. | Preserve known overdraft borrowing once; keep original residual separate. Reject dropping the overdraft or treating later Other as new borrowing. | **14 − 13 = 1m** exactly; net borrowing and FCFE change 0 from this presentation treatment. |
| **META-INT-001** | Original FY2021/22 selection lacked separate gross interest expense. | Bind 23m/185m to FY2021/22 from FY2023 Note14, retaining source and target dates. Reject coupon, interest-income and cash-interest estimates. | Original adopted exact operands remain in place; no numeric change. A later filing is the source, not the economic period. |
| **META-TAX-001** | FY2025 provision contains a 15,930m charge, including a 14,030m noncash valuation allowance. | Preserve reported historical CFO and tax; separate any recurring forecast tax decision. Reject adding an accounting charge to CFO or assuming it equals cash tax. | Provision25,474m remains unchanged. No automatic cash add-back, normalized rate or forecast revision. The prior EBIT-route diagnostic remains outside the adopted series. |

## Reproduced amounts

USD millions; FCFF rounded to three decimals here. Exact operands and results are
stored in JSON/CSV; source rounding still limits economic precision.

| FY | Net cash PP&E | Identified net borrowing | Provisional FCFE | Historical FCFF before → after | Residual Other |
| --- | ---: | ---: | ---: | --- | ---: |
| 2021 | 18,567 | −663 | 38,453 | 39,135.150 → unchanged | −13 |
| 2022 | 31,186 | 9,071 | 28,360 | 19,192.930 → **19,437.930** | 344 |
| 2023 | 27,045 | 7,397 | 51,465 | 44,214.667 → **44,435.667** | −111 |
| 2024 | 37,256 | 8,463 | 62,535 | 54,702.987 → unchanged | −277 |
| 2025 | 69,691 | 27,382 | 73,491 | 46,928.643 → unchanged | 2,220 |

FCFF = reported CFO + reported interest expense × (1 − provision / pretax income)
− cash PP&E net of identified receipts. Provisional FCFE = reported CFO − that
investment + identified net borrowing. Actual financing-classification gaps are
not eliminated by a complete statement sum. These are derived measures, not
separately reported GAAP FCFF/FCFE facts.

FY2021 original investment18,567m is already net. Later gross18,690m minus123m
receipt reproduces18,567m. FY2022 gross31,431m minus245m reproduces later net31,186m;
FY2023 gross27,266m minus221m reproduces later net27,045m. This approval is for
**identified PP&E receipts**, not an assertion that every investing line has been
economically decomposed.

## What the commentary establishes

The [primary-source research](research/other-financing-findings.json) retains five
annual filings and ten official earnings/follow-up transcripts, each with URL,
retrieval date and original-byte SHA256. [18 exact excerpts](research/disclosure-excerpts.json)
are bound to hashed searchable text. This is a bounded search, not a claim that
no public explanation exists anywhere.

FY2021 Notes1/11 describe a bank extending overdraft credit within the notional
cash pool. This supports the separately reported14m borrowing. Later comparative
presentation merges it into Other; that is an exact classification bridge.

FY2025 management discusses third-party capital and flexible infrastructure
structures, but the reviewed commentary does not bind an amount to residual
Other financing2,220m. The **2,554m Venture distribution is investing cash flow**.
Susan Li's Q3 call also says future20% venture construction contributions belong
to other investing cash flows. Neither is evidence to insert that amount into
borrowing. No IR message was sent; a specific issuer disclosure or clarification
linking a residual cash component would allow a new reviewed mapping.

## Preserved limitations

- Reported CFO retains SBC and other noncash adjustments. The forecast keeps SBC
  expensed and can include financed asset additions. No FCFF CAGR joins these
  accounting bases; historical numbers do not auto-populate forecasts.
- The existing historical interest input is the disclosed **expense** line. FY2025
  Note10 says notes interest is net of capitalized interest; Note6 reports
  capitalized interest535m/384m in FY2025/24. This is an additional investment/
  interest-scope alignment flag, not authorization to silently add it again to
  FCFF. Any expanded gross-interest convention must reconcile investment and
  tax treatment before adoption.
- Reported tax provision/current/deferred/cash amounts differ. No pure operating
  cash-tax allocation or recurring rate is inferred. Existing operating-method
  tests remain diagnostic; this milestone does not certify their alignment.
- Other financing net size does not bound potentially offsetting gross components.
  No materiality waiver, debt residual plug or missing-input estimate is adopted.

## Reproduce and future updates

```sh
PYTHONPATH=src .venv/bin/python scripts/resolve_meta_alphabet_cashflows.py --check
.venv/bin/python docs/company-resolutions/META/research/verify_sources.py
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/review -p 'test_meta_alphabet_resolution.py' -v
```

Replay checks original primary/instance bytes, exact fiscal dates, contexts,
USD units, captions, source cells and displayed cash signs; all five full
financing sums; three investment comparisons; and the overdraft presentation.
No network or old chat-output files are needed. `--write` regenerates reviewed
records and [adoption overlay](adopted-history.json); a reviewed overlay digest
and the private bundle pin must also match before runtime consumption.

The runtime wrapper recomputes the five results over the sealed original ledger
and verifies period, original investment, receipts and arithmetic. It changes only
Meta historical display. Updated filings require new retained evidence, manual
mapping and before/after review; preserve this version and original approvals.

[Earlier preparation record](../../company-data-preparation/META-analyst-input-package.md)
and [supplemental record](../../company-data-preparation/supported-seeds/META.md)
retain their original preparation and financial-sufficiency scopes.

## Approved treatment implementation and independent review — November3

The latest user approval covers the preferred treatments in the roadblock register.
New evidence and executed treatment logs are in [this implementation](implementation-2026-11-03/README.md).
The [shared implementation log](../implementation-2026-11-03/implementation-log.json),
[basis bridge](../implementation-2026-11-03/basis-bridge/decision-log.json),
[share-source schedules](../implementation-2026-11-03/share-bridge/README.md) and
[independent review](../implementation-2026-11-03/independent-review/findings.md)
retain the distinction between applied treatment, numerical verification and financial clearance.
The platform now exposes five-year FCFF/FCFE review records and a separate explicit manual FCFE forecast;
prior statements above about review-only integration describe the earlier milestone.
**Company status remains OPEN.** No missing/provisional/ownership item is cleared by software publication.
