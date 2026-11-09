# Full reporting review — November 9, 2026

Scope: historical trends, revenue mix and earnings-to-cash bridge for GOOGL,
AAPL and META. All 20 displayed quarters per company were reviewed. The original
Python/JS DCF pipelines, accepted inputs, dates, assumptions and valuation
calculations are unchanged. No reporting amount or financial definition needed
correction. This result does not close unrelated issuer/project roadblocks.

## Filing checks

The earlier historical-trends receipt independently checked only latest-quarter
operands and latest annual totals. This review expands verification to the whole
displayed window and all preparation annual totals. `scripts/audit_reporting.py`
reads retained filing XML directly using an independent XML selector; it does
not call either reporting-preparation calculation consumer. The selector checks
full concept namespaces, entity CIK, exact dates, USD units, dimensions and source
values. Missing, contradictory or dimensionally different observations fail.

| Company | Displayed quarters | Filings | Consolidated source observations | Revenue-mix source observations | Standalone-quarter comparisons | Preparation annual metric ties | Display-window annual mix ties |
|---|---:|---:|---:|---:|---:|---:|---:|
| Alphabet | 20 | 23 | 138 | 168 | 45 + 105 | 42 | 32 |
| Apple | 20 | 22 | 132 | 100 | 45 + 75 | 42 | 25 |
| Meta | 20 | 23 | 138 | 84 | 45 + 60 | 42 | 16 |
| Total | 60 | 68 | 408 | 352 | 375 | 126 | 73 |

All 760 underlying source observations match retained SEC filing XBRL exactly.
The 375 standalone comparisons were also re-extracted from the filing evidence.
Their disclosed YTD-versus-standalone differences remain preserved; a difference
is not silently rounded, plugged, or relabelled an exact standalone observation.
Repeated use of the same cumulative operand across adjacent quarters is counted
once in the underlying source-observation totals above. Annual checks are
arithmetic checks, not an additional independent economic-classification audit.

Checked for every displayed quarter:

- Six underlying metrics: revenue, operating income, net income, CFO, cash PP&E
  purchases and stock-based compensation, including every YTD subtraction operand.
- Actual fiscal dates, quarter durations, continuity and derivation boundaries.
- FCF = CFO − cash PP&E purchases.
- Other operating reconciliation = CFO − net income − SBC.
- Net income + SBC + Other = CFO, then CFO − cash capex = FCF.
- Operating and FCF margins use the same quarter's consolidated revenue.
- Revenue mix sums to consolidated revenue; nested detail equals its parent.
- Full displayed four-quarter category cohorts sum to their sourced annual value.

Receipts: `data/reporting-audit/{ticker}-audit.json`; URL/content-hash manifests
and retained evidence are in the same directory. The receipts bind to exact
published reporting-package hashes. These are checks of retained SEC filing
XBRL, not a manual line-by-line visual audit of every HTML/PDF table and not a
claim of current/latest-restated history.

## Functional checks

The production page passed 280 systematic quarter/view checks:

- 180 historical checks: all 20 quarters × all three metric groups × three
  companies. Displayed amounts, margins, linked revenue totals and cash-bridge
  summary values match the packages.
- 100 revenue checks: all 20 quarters in Alphabet/Meta primary and expanded modes,
  plus Apple's product/service view. Every table amount, revenue share, YoY value,
  reported total and each of the six cash-bridge bar labels matches expectations.
- Legend hiding/restoration, source/reconciliation disclosure, company switching,
  keyboard Home/End/arrows and shared selected-quarter updates work.
- All nine company/section combinations fit a 390px viewport with no horizontal
  page or chart overflow. Physical iPhone/Safari testing is not claimed.
- Existing interaction tests cover pointer preview/restoration, series visibility,
  failure/retry and stale issuer responses. These UI checks do not change DCF.

Machine-readable browser checks are retained in the release review output
folder. All 487 frontend tests and 17 reporting tests pass. The reporting validation
changes are deployed and the live bundle and all six reporting packages match
the reviewed artifact. The production build passes; the original 396 Python files, 15 browser
assets and 128 original engine fixtures match their preservation baseline.

## Improvements made during review

Current amounts were correct. Runtime reporting validation previously accepted
finite but inconsistent margins, incomplete derivation metadata or invalid
fiscal labels. The reporting-only validators now reject inconsistent margins,
nonconsecutive or malformed quarters, incorrect YTD boundaries/operand arithmetic
and revenue-mix fiscal metadata that could misalign YoY. Regression tests exercise
those failures. These checks reject bad refreshes; they do not alter values,
choose a new reporting policy, or supply missing data.

## Qualifications retained

- History is the explicit first-disclosure/cohort YTD-difference policy, not a
  latest-restated or historical as-known series. Alphabet has one and Meta eleven
  consolidated standalone presentation differences, each $1m; Apple has none.
  Meta's revenue detail has sixteen standalone differences (up to $2m), retained
  with their exact values in the audit receipt and selected-quarter UI disclosure.
- Meta FY2021 Q4 uses annual 2021 minus comparative nine-month 2021 segment
  disclosures in the 2022 Q3 filing; the comparative consolidated total matches
  the original operand. This exception is disclosed, not treated as as-known data.
- Alphabet's signed revenue hedging adjustment is separate from operating
  segments. Its old misleading standard tag is tied to the revenue table rather
  than a similarly named derivative-note amount. Expanded Services replaces its
  parent, preventing double counting.
- Apple displays products/services, not its geographic operating segments.
- Meta does not disclose a supported Facebook/Instagram/WhatsApp revenue split.
- Other is a derived aggregate, not separately sourced working-capital detail;
  FCF is CFO less cash PP&E, distinct from FCFF/FCFE.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/audit_reporting.py --ticker GOOGL
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/audit_reporting.py --ticker AAPL
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/audit_reporting.py --ticker META
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/reporting -v
```

Offline by default. `--refresh` permits retrieval of missing evidence using the
existing SEC client and configured identifying `SEC_USER_AGENT`; no reporting or
DCF input package is rewritten. A later accepted source refresh requires new
reconciliation/audit receipts bound to its updated package hashes.
