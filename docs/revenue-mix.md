# Revenue mix — financial-statement reporting extension

Implemented November 9, 2026. Scope: GOOGL first, then AAPL/META; 20 fiscal
quarters matching each accepted consolidated reporting package. This adds a
separate descriptive reporting consumer and does not resume market-price work,
modify original Python normalization, update DCF assumptions/anchors, or certify
the wider issuer universe.

## Data flow and reproduction

Existing SEC transport, submissions/history discovery and extracted filing-XBRL
parser → new `reporting/revenue_mix.py` selection/reconciliation consumer →
`frontend/public/revenue-mix/<ticker>.json` → independent browser request.
Original consolidated reporting packages and all existing DCF assets are unchanged.
Retained filing bytes and URL/content hashes live in `data/revenue-mix/`.
The browser has no SEC request, credentials, new backend or subscription.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/prepare_revenue_mix.py --ticker GOOGL
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/prepare_revenue_mix.py --ticker AAPL
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/prepare_revenue_mix.py --ticker META
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/reporting -v
```

Offline reproduction is default. `--refresh` permits retrieval of missing retained
sources using `SEC_USER_AGENT` and the existing SEC client; it does not silently
replace frozen sources. For a later reporting snapshot, first commit the accepted
sources/packages/receipts together, prepare and review updated consolidated
reporting via its existing command, then reproduce revenue mix, review taxonomy
or scope changes and affected issuer records, test and publish the matching
snapshot. Review new recast exceptions explicitly; there is no general fallback
to later filings. A new issuer needs its own mapping and reconciliation gates.

## Policy: filing-dimensional-revenue-mix-v1

- Exact USD integer facts selected by concept, taxonomy namespace, complete axis
  and member set, dates, and filing accession. Additional dimensions, ambiguous
  values, missing facts and contradictions stop publication. Missing is not zero.
- Use the same fiscal YTD operand dates/accessions as consolidated history, except
  the specifically disclosed Meta first-segment-history exception below.
- Q1 reported; Q2/Q3 successive YTD differences; Q4 annual less nine months.
  Validate cumulative operands and each displayed quarter against total revenue.
- Nested detail must equal its parent and replaces the parent in the expanded
  chart. It is never added alongside the parent as extra revenue.
- Every prepared observation carries source URL/accession, filing date, periods,
  concepts, namespaces, dimensions, context IDs, values and derivation operands.
- Closed full four-quarter cohorts in the displayed window tie back to the
  selected annual category values. These are arithmetic checks, not independent
  evidence of economic classification.
- Retain same-filing standalone-quarter comparisons. The chart uses the disclosed
  YTD-difference basis even when standalone figures differ. Differences are shown
  in the selected quarter's source disclosure, not redistributed to categories.
- Shares divide signed components by consolidated revenue; displayed rounded
  shares may not total exactly 100%. YoY compares the same prior fiscal quarter
  within the retained window; absent/nonpositive bases and hedging growth are
  unavailable. No synthetic observations are supplied for earlier YoY bases.
- This is descriptive cohort history, not a historical as-known backtest or a
  guarantee of constant segment composition across acquisitions/reclassifications.

## Issuer decisions

### Alphabet

Google Services + Google Cloud + Other Bets + signed revenue hedging adjustment
= total revenue. Services expands to Search & other, YouTube advertising, Google
Network and subscriptions/platforms/devices. Earlier Google other revenues is
mapped to the last category, with original members preserved; the label does not
claim unchanged economic composition. Earlier `*SegmentMember` names are explicit
aliases for the later segment member names.

Older revenue tables use the misleading US-GAAP
`GainLossOnOilAndGasHedgingActivity` tag for their displayed revenue hedging row;
later tables use `RevenueNotFromContractWithCustomer`. The retained FY2022 Q2
`DisaggregationOfRevenueTableTextBlock` confirms six-month hedging of $653m,
not the $654m derivative-note `SalesMember` amount. Never select the latter by
similar name. Source table:
https://www.sec.gov/Archives/edgar/data/1652044/000165204422000071/goog-20220630_htm.xml
All 20 quarterly top-level totals and Services detail reconcile exactly, with no
residual plug. Negative hedge adjustments are kept signed and drawn below zero.

### Apple

Five product/service categories: iPhone, Mac, iPad, Wearables/Home/Accessories,
and Services. These reconcile to total revenue; they are **not Apple's official
geographic operating segments**. Fiscal calendar/date identities are preserved,
including the September 26, 2026 latest year-end.

### Meta

Family of Apps + Reality Labs = total revenue. FoA expands to advertising + other
FoA revenue. No Facebook/Instagram/WhatsApp allocation is inferred.

FoA/RL reporting began in Q4 2021. Q4 2021 uses the original annual 2021 values
less the comparative nine-month 2021 segment figures in the 2022 Q3 filing
`0001326801-22-000108`. That comparative consolidated nine-month total must equal
the original 2021 Q3 consolidated operand before it is accepted. The exception
is explicit in code, sources and UI; never silently treat it as first-disclosed
2021 segment evidence. Its later availability makes this unsuitable for as-known
backtests.

The latest FY2026 Q3 YTD-derived FoA advertising is $63,062m and other revenue
$1,096m, versus standalone $63,061m/$1,097m. Both presentations sum to the same
$64,158m parent. Retain and disclose the difference; do not silently switch bases.

## UI and validation boundaries

Revenue mix sits after historical trends and before the cash-flow bridge and
DCF. Stacked quarter bars preview with pointer movement; click/tap or keyboard
arrows/Home/End select a quarter shared with the existing reporting charts.
Amounts, shares and YoY update with the active quarter. Segment expansion
replaces its parent, with exact reconciliation/source details available below.
Failure/retry and stale-issuer-response handling are isolated from history/DCF.

Tests cover all retained quarterly and annual ties, deterministic offline
reproduction, missing/conflicting/wrong-namespace/extra-dimension facts,
consolidated contradictions, signed hedging, Meta recast/presentation differences,
Apple calendar/categories, UI expansion, issuer binding, load failures and input
interaction. Browser checks cover desktop and a 390px viewport; this is not a
physical iPhone/Safari certification.

No export changes are included: existing DCF Excel downloads keep their scope.
Other issuers and new disclosure structures require separate reviewed mappings;
three pilot packages are not universal segment extraction readiness.
