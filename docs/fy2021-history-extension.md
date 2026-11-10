# Full FY2021 historical chart coverage — November 10, 2026

Historical trends and Revenue mix now begin at FY2021 Q1 for GOOGL, AAPL and
META. Alphabet/Meta have 23 quarters through FY2026 Q3; Apple has 24 through
FY2026 Q4. Apple uses fiscal dates, so its FY2021 Q1 began September 27, 2020.
No periods are padded with invented values.

## Data boundaries

The original `research-data/` and `revenue-mix/` packages, original Python
modules/preparation scripts, all allocation packages and DCF inputs/engines are
unchanged. The display now reads the previously accepted complete FY2021
`cash-bridge/` history after verifying it against the original 20-quarter
baseline. Revenue mix uses a separate `revenue-mix-expanded/` package. Every
previously displayed consolidated observation and revenue row remains identical.

`overviewHistory.ts` validates both overlapping source-checked history windows,
FY2021-Q1 coverage, snapshot identity and unchanged baseline observations.
`RevenueMix.tsx` uses actual row counts for chart geometry, labels, pointer/touch
selection and Home/End/arrow navigation. Latest-quarter selection and the page's
quarter count also follow the dataset. Cash analysis remains compatible with
both baseline and expanded history; its selected cash period stays independent.

## Revenue preparation and evidence

Run offline, from the repository root:

```sh
PYTHONPATH=src python3 scripts/prepare_expanded_revenue_mix.py
```

The new additive consumer reuses existing SEC transport, filing parser and exact
reviewed dimensional revenue mappings. It reads the original retained filing
stores and writes only new expanded packages, manifests, audit receipts and any
new evidence under `data/revenue-mix-expanded/`. `--refresh` permits missing
artifact retrieval using an identifying `SEC_USER_AGENT`; subsequent runs use
the retained bytes. Apple's FY2021 annual index/extracted instance were the
missing artifacts retrieved during this extension.

All quarterly component totals and parent/detail totals reconcile exactly to
consolidated revenue. Complete fiscal-year category sums match annual reported
categories. No balancing residual is manufactured.

### Meta FY2021 presentation

FoA/Reality Labs reporting began in Q4 2021. FY2021 Q1–Q3 therefore use the
comparative three/six/nine-month segment disclosures in the matching 2022
filings. Their consolidated values match the original accepted 2021 amounts
exactly. Q2/Q3 use differences of those comparative YTD amounts. The existing
Q4 annual-minus-comparative-nine-month calculation is unchanged, and the whole
2021 category series ties to the annual figures. This is a disclosed recast
segment presentation, not an as-known historical series. Package notes, methods
and original comparative filing links preserve that qualification.

## Validation

Independent raw-XML selection (the existing audit helper, without changing its
original fixed-window consumer) checked every newly exposed quarter's six
underlying consolidated metrics and every revenue component/detail operand:

| Issuer | Added quarters | Financial metric checks | Dimensional revenue checks |
| --- | --- | ---: | ---: |
| GOOGL | FY2021 Q1–Q3 | 30 | 40 |
| AAPL | FY2021 Q1–Q4 | 42 | 35 |
| META | FY2021 Q1–Q3 | 30 | 20 |

Checks are operand validations, not unique-fact counts or a line-by-line visual
filing audit. Receipts preserve contexts, source amounts and annual category
checks in `data/revenue-mix-expanded/<ticker>-audit.json`.

Frontend coverage checks all three issuers' full history, baseline preservation,
revenue reconciliation, cash-chart compatibility and synchronized Home/End
navigation in both historical charts. Existing metric tabs, drill-downs, source
links and DCF/export actions remain mounted.

This is a correction within Layout Option 2. Saved Option 1 and the initial
layout tags remain intact; `layout/option-2` follows the corrected deployed view.
