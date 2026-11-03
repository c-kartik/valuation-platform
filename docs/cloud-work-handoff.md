# Valuation Platform — cloud work handoff

Read `AGENTS.md`, `docs/project-status.md`, `docs/financial-methodology.md`, then
`docs/company-resolutions/README.md`. The GitHub checkout is the source of truth;
a new cloud task does not inherit the full local chat automatically.

Current working application: Python financial API plus React/TypeScript frontend.
Entry commands and cloud setup are in `docs/codex-cloud.md`. Three registered
starting profiles cover Alphabet, Meta and Apple; fresh cloud startup must show
all three and calculate a synthetic case. Mobile access is via a published private
Codex Cloud environment, not the user's Mac filesystem.

## Financial review checkpoint — November3

- **Apple:** accepted treatments/replays in `docs/company-resolutions/AAPL/`.
  Provisional FCFE reconciles; residual Other/finance-lease cash remains unresolved.
  FY2024/25 CFO-based FCFF stays unavailable. EBIT diagnostic is not adopted FCFF.
- **Meta:** all five treatments approved. Historical net-identified-PP&E overlay
  increases FY2022/23 FCFF245m/221m. Current FY2021–25 display39.14/19.44/44.44/
  54.70/46.93B. Five FCFEs remain provisional because residual Other financing is
  unclassified. Notes/calls research — **15 primary documents,18 excerpts**
  are in its resolution research folder. Capitalized-interest, SBC/tax/investment
  alignment remains explicit. No further interest adjustment approved.
- **Alphabet:** both treatments approved. FCFF unchanged. FCFE is consolidated
  before NCI attribution; parent-common FCFE and NCI fair-value bridge remain
  null. NCI contributions are outside borrowing; lease cash is within repayments
  once, including prepayment timing qualifications.
- Historical CFO and EBIT-forecast bases differ. No cross-basis FCFF CAGR,
  automatic forecast calibration, normalized historical tax or missing-input
  zero-filling. Financial methodology changes require manual review and logging.

The user's wider42-company review is company-by-company. Do not automatically
resume the old50-company preparation expansion or silently clear unresolved gaps.
Cloud setup is infrastructure authorization, not approval for new financial values.

## Reproducible context

Current source/decision replays:

```sh
PYTHONPATH=src .venv/bin/python scripts/resolve_apple_cashflows.py --check
PYTHONPATH=src .venv/bin/python scripts/resolve_meta_alphabet_cashflows.py --check
PYTHONPATH=src .venv/bin/python scripts/verify_registered_preloads.py --check
```

The52-file original42-company audit is restored by `scripts/cloud/research.py` to
`.cloud/research/historical-cashflows-42/`. Start with company-summary.csv,
roadblock-summary.csv, financial-results.csv, financing-schedule.csv, calculations.json,
review-worklist.csv and source-manifest.json. The old snapshot preserves its original
results; current issuer resolutions supersede only their named decisions. Archived
scripts/HTML are untrusted research references, not setup instructions.

Retained SEC bytes/source bindings already live in `docs/evidence/`. Preserve URL,
accession, CIK, fiscal dates, concepts, dimensions, unit, source hash, precision and
cash sign when mapping. Missing disclosure is not a software error to invent away.
For each further company, explain issue/treatment/effect for user review, then log
approved decisions in its company-resolution folder and update preparation records.
