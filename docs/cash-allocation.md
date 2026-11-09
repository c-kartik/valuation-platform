# Alphabet cash allocation and Inside PP&E

User-approved implementation of the two cash-allocation mockups, November 9,
2026. Alphabet only. Apple/Meta reporting remains unchanged; this is not approval
of additional issuer mappings, revised valuation inputs or resumed universe work.

## Consumer and preservation boundary

`prepare_cash_allocation.py` is a new offline reporting consumer. It reads the
accepted GOOGL quarterly/annual cohort and the hash-verified extracted filing
instances already retained under `data/reporting-audit/`. It writes only
`frontend/public/cash-allocation/GOOGL.json`. No existing Python script/module,
DCF dataset, browser engine, source snapshot, forecast or workbook writer changes.
The new component loads this separate static package and appears after the cash
bridge and ahead of DCF. Loading failures/retries are isolated; company switches
abort/ignore stale responses. Only Alphabet exposes the section/navigation link.

## Cash allocation policy: alphabet-cash-allocation-v1

- Five annual cohorts: FY2021–FY2025; 20 quarters: FY2021 Q4–FY2026 Q3.
- Annual values and YTD operands use exactly the accessions/dates selected by the
  existing consolidated reporting policy. Q1 is reported; Q2/Q3 are successive
  YTD differences; Q4 is annual less nine months. The 17 full TTM windows begin
  at FY2022 Q3 and sum four standalone quarters. Earlier incomplete TTM is absent.
- Amounts are exact integer USD, displayed in billions using existing Decimal
  rounding. XBRL payment-positive facts are explicitly mapped to signed cash
  flows. Namespace, entity, whole-entity context, USD units, periods, ambiguity,
  retained-content hash and review cutoff are checked before publication.
- Cash PP&E + acquisitions net of acquired cash and intangible purchases form
  business investment. Buybacks + dividends form shareholder returns.
  Stock-award financing payments stay separate from repurchases and noncash SBC.
- Securities include marketable/non-marketable purchases, maturities and sales;
  debt includes proceeds net of issuance costs and debt/capital-lease repayments.
  Both are netted for the flow and retain gross components in the inspector.
- Subsidiary interests, equity issuance and other financing captions are separate
  when reported. In particular the 2026 filings include common/preferred issuance;
  these are not silently hidden in debt or a residual. Other investing is its
  reported caption, not a constructed plug.
- Component sums must equal reported investing and financing subtotals. CFO +
  investing + financing + FX must equal reported cash movement. Opening cash +
  movement must equal closing cash, for every cumulative/discrete/TTM period.
- An optional caption absent from a filing remains **null** with null evidence.
  It contributes no separately reported component to a subtotal that must reconcile
  exactly; it is never described as a reported zero. Required captions cannot be
  absent. An inconsistent or newly unsupported statement stops preparation.
- Sources and uses join through one pooled node: no claim that a particular
  borrowing funded a particular asset. Positive cash accumulation before FX is a
  destination; cash drawn before FX is a source. FX appears only in the cash
  reconciliation. The pool excludes the full opening balance. Cash uses the
  statement's cash/restricted-cash scope, not excess cash or parent-common cash.
- Each source fact retains reported/signed values, concept namespace, context IDs,
  dates, dimensions, filing date, source URL and content digest. Derived quarters
  retain signed operand references; TTM retains its four quarterly references.
  The UI exposes derivation/source details and missing captions. This remains a
  descriptive cohort series, not an as-known backtest or latest-restated history.

## Inside PP&E: a separate balance view

The latest reviewed annual filing (2025 10-K, accession
`0001652044-26-000018`) supplies its December 31, 2024/2025 comparative PP&E note.
These independent year-end controls never sum annual balances into TTM or imply
a split of cash capex. No earlier PP&E category history is inferred.

Technical infrastructure + office space + corporate/other assets = PP&E in
service. In-service assets − accumulated depreciation + assets not yet in service
= net PP&E. Gross PP&E = in-service assets + not-yet-in-service assets. The XBRL
scope includes finance-lease right-of-use assets. Both identities reconcile
exactly for both dates. Categories use exact axis/member bindings, with no extra
dimensions accepted. Net PP&E is $171.036bn (2024) / $246.597bn (2025).

The same note discloses that **approximately 60%** of technical infrastructure
is servers/network equipment at both dates; the balance is data-center land,
buildings and related assets. This reviewed approximate disclosure is text,
not an exact inferred dollar split. The preparation command deliberately stops
when the latest annual year changes until this note and mapping are reviewed.
A change in PP&E balances is not cash expenditure: depreciation, leases,
acquisitions and other noncash adjustments prevent that inference.

## Reproduction, refresh and acceptance

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/prepare_cash_allocation.py --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/prepare_cash_allocation.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/reporting -v
```

The first command is read-only reproduction; the second writes only the new
package. This consumer has no network option. Refresh the established quarterly
pipeline and retained filing audit separately under their own instructions,
then review changed source mappings/optional omissions and the PP&E note,
reproduce and test the new package, update this issuer record, and commit the
matching source/data/documentation before publication. Never silently expand
coverage or substitute Company Facts for dimensional PP&E.

New tickers require explicit concept/sign/axis mapping, complete components and
exact subtotal/balance reconciliation, issuer/calendar/provenance review,
missing-caption policy, standalone/YTD differences and a separate acceptance
record. Alphabet is a pilot, not automatic universe readiness.

Validation and publication evidence: [release receipt](cash-allocation-release.json).
Exports retain their existing DCF-only scope. No new provider, server, scheduled
refresh, current price or valuation-methodology approval is introduced.
