# Apple and Meta cash allocation / Inside PP&E

User-approved extension, November 9, 2026. This acceptance covers Apple and Meta
only, alongside the already accepted Alphabet consumer. Existing Python SEC/DCF
pipelines, financial conventions, model dates, accepted input packages and
reporting datasets remain unchanged. This does not resume the issuer universe.

## Coverage and reproduction

| Consumer | Apple | Meta |
| --- | --- | --- |
| Annual cash allocation | FY2021–FY2026 (6) | FY2021–FY2025 (5) |
| Quarterly cash allocation | FY2021 Q1–FY2026 Q4 (24) | FY2021 Q1–FY2026 Q3 (23) |
| Complete TTM windows | FY2021 Q4–FY2026 Q4 (21) | FY2021 Q4–FY2026 Q3 (20) |
| PP&E balance dates | 2025-09-27 / 2026-09-26 | 2024-12-31 / 2025-12-31 |

Apple's actual fiscal dates, including the 53-week FY2023, are preserved.
FY2021 Q1 spans September 27–December 26, 2020; it is not calendar Q1 2021.
Year-then-quarter controls work identically across all three companies. Missing
future quarters and incomplete TTM windows are disabled. PP&E dates are separate
balance selections and never summed into quarterly/TTM spending.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/prepare_issuer_cash_allocation.py --ticker AAPL --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/prepare_issuer_cash_allocation.py --ticker META --check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/reporting -v
```

Omit `--check` to write the named new package only. To retain specifically missing
filings/primary statements, add `--fetch-missing`, `PYTHONPATH=src`, and an
identifying `SEC_USER_AGENT`. Retained sources, URL/content hashes and manifests
are isolated under `data/cash-allocation/`; original source stores are read-only.
Normal preparation/checking remains offline and deterministic. Alphabet's own
preparation command and published package reproduce unchanged.

## Selection, source roles and financial identities

Policies `aapl-cash-allocation-v1` and `meta-cash-allocation-v1` use the existing
accepted annual CFO cohorts and their exact filing accessions. Earlier FY2021
quarters use original first-disclosure YTD facts anchored to the frozen Company
Facts snapshots. Every overlapping quarter must match the existing reporting
package's CFO, cash capex, dates and selected accessions exactly. Q1 is reported;
Q2/Q3 use successive YTD differences; Q4 is annual minus nine months. Four
standalone quarters form TTM. All completed annual cohorts tie component by
component to the annual filing: 168 Apple and 140 Meta flow-caption ties.

The consumer reads both retained extracted XBRL and the corresponding primary
HTML cash-flow statement. It identifies the smallest table containing all three
operating/investing/financing subtotals, retains its inline concept set and hash,
and admits only separate statement components. Exact namespace, context,
entity, integer USD, date, sign, source digest and filing cutoff checks remain.
Ambiguous/missing required facts stop preparation. Optional omitted captions
remain null, with null evidence; they are not reported zeros.

For every cumulative, standalone and TTM period:

- investing components equal reported investing cash flow;
- financing components equal reported financing cash flow;
- CFO + investing + financing + reported FX equal reported cash movement;
- opening cash + cash movement equal closing cash.

There is no balancing plug. Caption aliases are explicit and selected by their
actual statement presence, never chosen to obtain a preferred total. First-
disclosure/YTD presentation differences remain a descriptive cohort convention,
not a latest-restated series or as-known backtest.

### Apple mappings

Marketable purchases, sales and maturities remain separate gross components;
other-investment purchases/proceeds are included when separately reported.
Acquisitions are net of acquired cash, without asserting that the caption also
contains intangible purchases. Common-share proceeds, long-term debt proceeds,
repayments and signed net commercial-paper changes are separate source facts.
Note-only short-term-debt subcomponents are not counted again alongside the net
commercial-paper line. Equity-award payments are reported tax withholding on net
share settlements, separate from buybacks, dividends and noncash SBC.

Apple does not separately present FX in the selected cash-flow statements. That
caption remains null and the balance view says **Not separately reported**;
the cash movement identity reconciles without an invented FX observation.

### Meta mappings and note-only exclusion

Old separate marketable sales/maturities and newer combined captions are mapped
explicitly. Non-marketable equity-investment payments use Meta's custom namespace
(`fb`/`meta` are lexical aliases for the dated facebook.com taxonomy).
Acquisition/intangible caption aliases are explicit. Asset-sale proceeds,
held-for-sale asset purchases and venture distributions are retained separately;
the 2026 venture caption uses `EquityMethodInvestmentDividendsOrDistributions`.

Finance-lease principal is financing cash, counted once with net debt cash flows;
it is not another deduction from cash PP&E. Cash-pooling overdraft changes,
long-term borrowing, taxes on net share settlement, buybacks, dividends and
reported other financing are included exactly as presented.

The FY2021 Q2 filing `0001326801-21-000049` tags a $20m equity-investment payment
in a note. Its cash-flow table does **not** separately present that caption:
the payment is within the $62m Other investing aggregate. Counting both produces
a $20m discrepancy. The consumer retains the note fact as explicitly excluded
supporting evidence, leaves the separate component null, and shows that
exclusion/source in the UI. Investing cash flow reconciles to −$13.069bn.
This is a statement-role rule applied before reconciliation, not a residual
adjustment or a blanket rule to discard non-marketable investment payments.

## Issuer-specific PP&E

The latest accepted annual filing supplies both comparative balance dates.
Source dimensions and category definitions are issuer-specific, with no imported
Alphabet 60% infrastructure assumption.

- **Apple:** land/buildings; machinery, equipment/internal-use software; leasehold
  improvements. These sum to gross PP&E; gross less accumulated depreciation
  equals net PP&E. Net balances are $49.834bn / $52.084bn. No separately reported
  construction-in-progress category or server/manufacturing split is invented.
- **Meta:** land; servers/network assets; buildings; leasehold improvements;
  equipment/other; finance-lease right-of-use assets; construction in progress.
  Categories sum to gross PP&E including the reported finance-lease asset scope;
  gross less accumulated depreciation equals net PP&E. Net balances are
  $121.346bn / $176.400bn. The server category includes components stored by
  suppliers, matching the 2025 note/member definition. Construction in progress
  is a reported balance, not inferred annual capex.

Each PP&E fact retains concept, dimension, context IDs, balance date, source URL
and digest. Historical balance changes include depreciation and noncash activity;
they do not break down the cash-allocation PP&E purchases line.

## Acceptance and refresh boundaries

Independent raw-instance replay checks **897 source observations** across 47
filings: 865 cash-flow observations and 32 PP&E observations. Primary-table role
checks guard against note-only double counting. Arithmetic tests cover all 99
new annual/quarterly/TTM views and all 308 annual component ties. Runtime tests
cover wrong issuers, fiscal dates, source contradictions, category transplants,
null FX, lease double counting, failures/retry, stale supported-company responses
and independent PP&E dates.

Refresh the established reporting/retained-source pipeline under its existing
instructions, then review any new statement captions, taxonomy aliases, fiscal
coverage and PP&E note/category changes. Retain sources explicitly, reproduce,
validate, update the affected issuer record and publish matching code/data.
This script does not schedule or auto-publish refreshes. Other issuers need their
own reviewed mapping and acceptance. Existing DCF Excel export scope is unchanged.

[Release and verification receipt](cash-allocation-issuers-release.json).
