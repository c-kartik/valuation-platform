# Apple A1–A8 implementation — parent review OPEN

This is the versioned execution record for the user's November 3 authorization to
implement the preferred treatments in `OPEN-ROADBLOCKS.md`. It adds research,
source-bound schedules and explicit policies; it does not rewrite the original
Apple ledger or historical facts. [Work log](work-log.json) records the work and
[evidence ledger](evidence-ledger.json) stores exact source observations and sums.
No missing amount is replaced with zero, a coupon estimate, a liability delta,
an unexplained residual or a blanket materiality waiver.

## Five-year availability

USD billions below are rounded for reading. Exact values and distinct consumer
statuses are in [availability-matrix.json](availability-matrix.json).

| FY | Reported-cash FCFF convention | Identified-funding FCFE, provisional | Verified FCFE | Valuation-aligned operating FCFF |
|---|---:|---:|---|---|
| 2021 | 95.246 | 105.618 | Unavailable: A2/A3 | Unavailable: A4/A5/A6 |
| 2022 | 113.899 | 111.320 | Unavailable: A2/A3 | Unavailable: A4/A5/A6 |
| 2023 | 102.938 | 89.683 | Unavailable: A2/A3 | Unavailable: A4/A5/A6 |
| 2024 | Unavailable: A1 | 102.809 | Unavailable: A2/A3 | Unavailable: A4/A5/A6 |
| 2025 | Unavailable: A1 | 90.284 | Unavailable: A2/A3 | Unavailable: A4/A5/A6 |

Reported-cash FCFF is CFO + expensed interest × (1 − reported provision / pretax)
− cash PP&E. It retains reported CFO adjustments including SBC, and therefore
does not share the forecast's SBC-expensed operating basis. Identified-funding
FCFE is CFO − cash PP&E + separately identified term-debt/CP cash. The reported
financing Other remains unclassified, not assumed non-debt. Displaying the
provisional number is different from certifying complete common-equity cash.

## Applied treatments and remaining evidence

| ID | Implementation performed | Result and exact remaining requirement |
|---|---|---|
| A1 | Replayed the five original primary/instance pairs; searched current SEC Company Facts exact annual standard monetary observations; retrieved the newly filed FY2026 annual primary/instance and searched FY2024/25 comparatives. | No separate FY2024/25 gross expensed interest found in these sources. Two CFO-based FCFF gaps remain. Next evidence: an exact issuer disclosure or a complete compatible expense bridge; coupons, net income/expense and cash interest are not substitutes. The EBIT route remains separately investigated across all years. |
| A2 | Replayed complete financing rows and preserved the original FY2021 equity-reclassification bridge. Reverified FY2024/25 CFO, PP&E and all debt/Other amounts against the newly filed FY2026 comparatives. | Other stays −129/−160/−581/−361/−111m. All five financing sums tie, but no full Other decomposition is supplied. The five FCFEs remain provisional. Next evidence: exact component disclosures/issuer clarification; no outgoing message was sent. |
| A3 | Inspected finance-lease stocks, future maturities, fixed operating-lease cash and combined operating/finance ROU additions in all five originals and the new annual filing. | No actual annual finance-lease principal or complete additions/interest/FX/modification cash roll-forward recovered. Principal and containment remain unknown. A stock change or a future maturity is not a repayment. |
| A4 | Replayed every CFO reconciliation row and the exact existing EBIT-to-CFO bridge. Bound named trade movements separately from mixed asset/liability movements. | Mixed rows sum −2.243/−0.867/−2.653/+3.821/−20.273bn across FY2021–25. These are actual broad cash-statement contributions, not pure operating WC. No tax, capital-creditor or noncurrent allocation is inferred from book deltas; a component cash reconciliation is still needed. |
| A5 | Rechecked reported cash-statement D&A and SBC. Bound newly disclosed FY2024/25 intangible amortization and PP&E depreciation from the FY2026 annual filing, preserving source/target dates and rounding. | FY2024 depreciation8.2bn + amortization3.6bn =11.8bn, versus repeated cash D&A11.445bn. The355m difference exceeds the combined displayed rounding interval. FY2025 8.0+3.7=11.7bn is compatible with11.698bn at stated precision, but compatibility does not prove complete income-expense alignment. No residual is added as amortization; no second lease add-back. |
| A6 | Preserved the cash PP&E perimeter. Reconciled new separately shown FY2025 noncurrent intangible assets to the old Other-assets presentation:83.727bn =72.634bn+11.093bn. | This exact balance presentation bridge is not a cash investment figure. Newly disclosed licensed/owned intangible stocks and combined ROU additions still do not give a complete cash/noncash operating-investment flow or creditor settlement schedule. No financing flow is deducted twice. |
| A7 | Applied the approved provision/pretax allocation convention explicitly to the unadjusted EBIT diagnostic; independently replayed all five effective-tax-rate reconciliation tables and current+deferred tax component sums. | Convention implemented with exact operands and labels. Allocated tax is not a separately reported operating cash-tax fact. Tax inside mixed cash movements remains part of A4; adopting a convention does not certify the operating series. |
| A8 | Reconciled reported taxes, cash payments and isolated State Aid effects. Retained the existing editable forecast path18%→20% and independent terminal20% as explicit assumptions, with no historical CFO adjustment. | The retained policy is not calibrated to the distorted reported ETR. No numeric forecast change is made; root integration must independently replay Base/Bear/Bull valuation parity. Geographic tax mix, R&D credits, valuation allowance and operating-tax allocation remain forecast uncertainties. |

The preferred treatments have been executed to the extent supported by evidence.
Apple remains OPEN because A1–A6 contain measurement/classification gaps. Policy
approval cannot create the missing historical observations.

## Tax reconciliation and the forecast choice

FY2024 reported provision29.749bn less the exact State Aid charge10.246bn gives
19.503bn, or **15.793821%** of reported pretax income123.485bn. FY2025 provision
20.719bn minus the State Aid benefit−0.486bn gives21.205bn, or **15.976162%** of
pretax132.729bn. These are accounting ratios excluding only the named State Aid
line. They are not fully normalized recurring operating cash-tax rates.

FY2025 also reports a2.091bn change-in-valuation-allowance reconciliation line.
It is preserved. Calling it nonrecurring merely to lower the rate is unsupported.
Current/deferred provisions and cash taxes retain separate source populations;
their difference is not plugged into operating WC.

The18% starting and20% endpoint/terminal assumptions are therefore retained as
the existing explicit forecasting policy rather than replaced with either raw
reported ETR or the isolated State Aid-adjusted ratio. Retaining the same inputs
and methods changes the forecast and valuation by zero. This work does not claim
that20% is a filing fact, management guidance or the unique economically correct
tax rate. The independent root consumer comparison is a separate validation.

## New official evidence and provenance

The SEC submissions response identifies a new Apple FY2026 annual filing dated
**November3,2026**, accession **0000320193-26-000026**, report dateSeptember26,2026.
Its [primary filing](https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm)
and extracted instance are retained here with [receipts](new-source-manifest.json),
original-byte hashes and original receipt times. They are used only for explicitly
identified FY2024/25 comparative evidence. The historical target remains FY2021–25.
No FY2026 history, revenue anchor or operating preload is silently substituted.

The new filing's exact additional detail matters: it discloses amortization and
intangibles previously absent from the reviewed notes, while repeating the old
cash D&A, CFO, cash PP&E, debt and Other financing figures. Neither a new caption
nor a newly visible book asset creates a cash flow. The source/target identifiers
remain separate in every comparative observation.

The original five SEC sources remain the previously retained byte/hash verified
primary/instance pairs in the repository source bank. Current SEC Company Facts
and submissions responses are new snapshots, not replacements for those pairs.
The API search is bounded to its standard us-gaap USD exact annual observations;
primary/instance searches separately cover the issuer's custom tags and prose.
Absence here is not a claim that no possible future issuer evidence could exist.

## Reproduce

From the repository root:

```sh
PYTHONPATH=src .venv/bin/python scripts/implement_apple_roadblocks.py --check
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests/review -p 'test_apple_roadblock_implementation.py' -v
```

The replay uses only retained source bytes and performs no network requests.
It independently verifies the new SEC body hashes and submissions identity,
replays original and later primary/instance bindings, checks contribution signs,
cash/financing sums, five tax tables, and current+deferred tax totals. `--write`
regenerates only this version's evidence ledger and availability matrix. It does
not mutate the source bank, old ledgers, accepted packages, UI or forecast policy.

Future evidence needs a new version and source map. Retain this version to show
which observations were actually available for the approved November3 review.

## Root integration contract

Consume the versioned [availability matrix](availability-matrix.json), with the
evidence ledger as provenance. Preserve **metric, method, ownership, investment
perimeter, tax convention, status and blocking issue IDs** independently. For
Apple, the filing's consolidation basis is Apple and wholly owned subsidiaries;
this does not resolve financing completeness.

1. Existing reported-cash FCFF values for2021–23 can remain available with their
   exact convention and history/forecast basis warning. FY2024/25 stay null.
2. Identified-funding FCFE can be displayed only with its provisional status;
   verified FCFE remains null in all five years. Do not promote a numeric review
   result merely because it is finite or its full statement reconciles.
3. Valuation-aligned historical FCFF remains null; the EBIT diagnostic is not a
   fallback for missing reported-cash FCFF or a forecast-calibration source.
4. The forecast tax policy remains explicitly estimated18%→20%, terminal20%;
   adoption should retain existing inputs and verify all scenario outputs agree.
5. Maintain parent status OPEN and carry all A1–A6 evidence gaps to current
   reports/API/UI. Future FCFE discounting/financing development is outside this
   Apple historical data contract and cannot be inferred from these numbers.
