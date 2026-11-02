# Historical FCFF — operating-profit method test

November 2, 2026. Alphabet, Apple and Meta, FY2021–FY2025.

**All 15 operating-method arithmetic tests calculate without an interest estimate.**
This resolves the interest-input dependency, including Apple FY2024/25.
It does not yet establish 15 fully reconciled operating FCFF observations:
mixed cash-movement rows, D&A scope and the investment perimeter still matter.
The figures below are explicitly a method test; verified_operating_fcff remains null.

## Tested definition

`EBIT × (1 − reported tax provision / reported pretax income) + disclosed D&A/identified noncash operating charges − cash PP&E + selected signed cash movements`

The standard EBIT/NOPAT approach is described by [CFA Institute](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation)
and [Wall Street Prep](https://www.wallstreetprep.com/knowledge/unlevered-free-cash-flow/).
Our statement-population choices below are explicit test conventions, not those sources' endorsement of these issuer inputs.

- Every numerical operand is verified against retained SEC primary inline and extracted XBRL, including exact annual dates, dimensions, units and source hashes.
- Use reported consolidated ETR, without clipping or normalizing. This is an allocation convention, not an observed unlevered cash-tax bill.
- Keep SBC expensed in operating profit. Exclude the separate CFO SBC add-back.
- Alphabet FY2021/22 includes both disclosed depreciation/impairment and intangible amortization/impairment captions. Later years use disclosed depreciation; missing intangible detail is not zero-filled.
- Meta includes separately disclosed facilities and data-center noncash charges/reversals once, in addition to D&A. They are not renamed D&A. No second finance-lease amortization add-back.
- Use the disclosed asset/liability cash movements, excluding explicitly named income-tax movements. Mixed Other and accrued rows remain mixed, not certified operating WC. Positive contribution adds cash; cash use is its negative.
- Deduct cash PP&E only. No finance-lease mix estimates, debt-based interest estimates, book-delta substitution or residual balancing item.

## Results — USD billions, method-test figures

| Company | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---:|---:|---:|---:|---:|
| GOOGL | 52.86 | 44.55 | 47.90 | 50.70 | 40.92 |
| AAPL | 89.74 | 101.68 | 91.46 | 99.18 | 86.26 |
| META | 29.03 | 9.80 | 28.50 | 40.90 | 6.63 |

These are reproducible filing-operand calculations under the stated perimeter, **not forecasts or fabricated missing amounts**.
They are also **not yet certified cash FCFF**; a source-supported number does not validate the classification of a mixed source row.

## Check against the previous CFO method

| Company | FY | Operating test | Prior CFO method | Difference: operating − prior |
|---|---|---:|---:|---:|
| GOOGL | FY2021 | 52.86 | 67.30 | -14.44 |
| GOOGL | FY2022 | 44.55 | 60.31 | -15.76 |
| GOOGL | FY2023 | 47.90 | 69.76 | -21.86 |
| GOOGL | FY2024 | 50.70 | 72.99 | -22.29 |
| GOOGL | FY2025 | 40.92 | 73.88 | -32.96 |
| AAPL | FY2021 | 89.74 | 95.25 | -5.50 |
| AAPL | FY2022 | 101.68 | 113.90 | -12.22 |
| AAPL | FY2023 | 91.46 | 102.94 | -11.48 |
| AAPL | FY2024 | 99.18 | Unavailable: interest undisclosed | — |
| AAPL | FY2025 | 86.26 | Unavailable: interest undisclosed | — |
| META | FY2021 | 29.03 | 39.14 | -10.11 |
| META | FY2022 | 9.80 | 19.19 | -9.40 |
| META | FY2023 | 28.50 | 44.21 | -15.72 |
| META | FY2024 | 40.90 | 54.70 | -13.80 |
| META | FY2025 | 6.63 | 46.93 | -40.30 |

The two methods do not currently have identical economic perimeters. Each of the 15 tests has an exact, zero-residual bridge:

`operating test + (pretax income − EBIT) × (1 − ETR) + excluded CFO adjustments/explicit tax movements = reported CFO − cash PP&E`.

Where disclosed, adding interest expense × (1 − ETR) to the right side independently reproduces all 13 prior results.
The bridge explicitly includes excluded SBC, deferred taxes, securities gains/losses, Other and tax movements; it never assigns a residual to WC.
This explains why switching formulas alone cannot establish equivalent FCFF.

## Input-alignment test

A second calculation includes only explicitly named trade cash movements, excluding mixed Other/accrued rows.
The difference shows the size of the classification exposure; neither variant is a confidence interval or a bound on economic FCFF.

| Company | FY | Broad disclosed-movement test | Named-trade-only test | Mixed movement contribution |
|---|---|---:|---:|---:|
| GOOGL | FY2021 | 52.86 | 47.41 | 5.46 |
| GOOGL | FY2022 | 44.55 | 45.68 | -1.13 |
| GOOGL | FY2023 | 47.90 | 46.10 | 1.79 |
| GOOGL | FY2024 | 50.70 | 53.26 | -2.56 |
| GOOGL | FY2025 | 40.92 | 32.52 | 8.40 |
| AAPL | FY2021 | 89.74 | 91.99 | -2.24 |
| AAPL | FY2022 | 101.68 | 102.55 | -0.87 |
| AAPL | FY2023 | 91.46 | 94.11 | -2.65 |
| AAPL | FY2024 | 99.18 | 95.36 | 3.82 |
| AAPL | FY2025 | 86.26 | 106.54 | -20.27 |
| META | FY2021 | 29.03 | 26.83 | 2.20 |
| META | FY2022 | 9.80 | 4.65 | 5.15 |
| META | FY2023 | 28.50 | 22.04 | 6.46 |
| META | FY2024 | 40.90 | 38.74 | 2.16 |
| META | FY2025 | 6.63 | 5.69 | 0.94 |

### Specific issues found

- **Apple:** the EBIT route needs no missing interest input. But FY2024's reported tax provision includes the Ireland State Aid charge, and FY2025 cash taxes/Other movements include subsequent timing effects. The FY2025 10-K Note 7 describes a 10.2B net FY2024 charge and 15.8B payable via escrow. Neither ETR nor broad Other movements are silently normalized. The cash-flow D&A caption is disclosed; complete expense/inventory timing is not newly certified.
- **Alphabet:** early noncash captions explicitly include impairment, while FY2023–25 separately display depreciation. Intangible/Other scope changes and operating/finance lease overlap remain limitations. Explicit cash income-tax movements are excluded; mixed accrual movements are not automatically tax-free.
- **Meta:** facilities/data-center noncash charges are separate from D&A. FY2025's tax provision is materially affected by deferred tax/valuation-allowance items; applying reported ETR retains those effects, rather than treating this as normalized cash tax. Mixed liabilities and financed investment remain separate review needs.

## Operand schedules — USD millions

Positive movement contribution adds cash; a negative value represents a use of cash. Source rounding is retained; displayed calculated digits add no filing precision.

### GOOGL

| FY | EBIT | Tax provision | Pretax | Selected noncash costs | Cash PP&E | Movement contribution | Test result |
|---|---:|---:|---:|---:|---:|---:|---:|
| FY2021 | 78,714.000 | 14,701.000 | 90,734.000 | 12,441.000 | 24,640.000 | -898.000 | 52,863.517 |
| FY2022 | 74,842.000 | 11,356.000 | 71,328.000 | 15,928.000 | 31,485.000 | -2,819.000 | 44,550.543 |
| FY2023 | 84,293.000 | 11,922.000 | 85,717.000 | 11,946.000 | 32,251.000 | -4,368.000 | 47,896.058 |
| FY2024 | 112,390.000 | 19,697.000 | 119,815.000 | 15,311.000 | 52,535.000 | -5,988.000 | 50,701.634 |
| FY2025 | 129,039.000 | 26,656.000 | 158,826.000 | 21,136.000 | 91,447.000 | 3,844.000 | 40,915.196 |

Primary SEC filings:

- [FY2021 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204422000019/goog-20211231.htm) — 2021-01-01 to 2021-12-31.
- [FY2022 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204423000016/goog-20221231.htm) — 2022-01-01 to 2022-12-31.
- [FY2023 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000022/goog-20231231.htm) — 2023-01-01 to 2023-12-31.
- [FY2024 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231.htm) — 2024-01-01 to 2024-12-31.
- [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm) — 2025-01-01 to 2025-12-31.

### AAPL

| FY | EBIT | Tax provision | Pretax | Selected noncash costs | Cash PP&E | Movement contribution | Test result |
|---|---:|---:|---:|---:|---:|---:|---:|
| FY2021 | 108,949.000 | 14,527.000 | 109,207.000 | 11,284.000 | 11,085.000 | -4,911.000 | 89,744.320 |
| FY2022 | 119,437.000 | 19,300.000 | 119,103.000 | 11,104.000 | 10,708.000 | 1,200.000 | 101,678.877 |
| FY2023 | 114,301.000 | 16,741.000 | 113,736.000 | 11,519.000 | 10,959.000 | -6,577.000 | 91,459.837 |
| FY2024 | 123,216.000 | 29,749.000 | 123,485.000 | 11,445.000 | 9,447.000 | 3,651.000 | 99,180.805 |
| FY2025 | 133,050.000 | 20,719.000 | 132,729.000 | 11,698.000 | 12,715.000 | -25,000.000 | 86,263.892 |

Primary SEC filings:

- [FY2021 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm) — 2020-09-27 to 2021-09-25.
- [FY2022 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/aapl-20220924.htm) — 2021-09-26 to 2022-09-24.
- [FY2023 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019323000106/aapl-20230930.htm) — 2022-09-25 to 2023-09-30.
- [FY2024 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm) — 2023-10-01 to 2024-09-28.
- [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm) — 2024-09-29 to 2025-09-27.

### META

| FY | EBIT | Tax provision | Pretax | Selected noncash costs | Cash PP&E | Movement contribution | Test result |
|---|---:|---:|---:|---:|---:|---:|---:|
| FY2021 | 46,753.000 | 7,914.000 | 47,284.000 | 7,967.000 | 18,567.000 | 700.000 | 29,027.874 |
| FY2022 | 28,944.000 | 5,619.000 | 28,819.000 | 12,245.000 | 31,431.000 | 5,683.000 | 9,797.628 |
| FY2023 | 46,751.000 | 8,330.000 | 47,428.000 | 13,386.000 | 27,266.000 | 3,836.000 | 28,495.905 |
| FY2024 | 69,380.000 | 8,303.000 | 70,663.000 | 15,881.000 | 37,256.000 | 1,048.000 | 40,900.754 |
| FY2025 | 83,276.000 | 25,474.000 | 85,932.000 | 18,616.000 | 69,691.000 | -885.000 | 6,629.354 |

Primary SEC filings:

- [FY2021 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680122000018/fb-20211231.htm) — 2021-01-01 to 2021-12-31.
- [FY2022 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680123000013/meta-20221231.htm) — 2022-01-01 to 2022-12-31.
- [FY2023 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680124000012/meta-20231231.htm) — 2023-01-01 to 2023-12-31.
- [FY2024 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680125000017/meta-20241231.htm) — 2024-01-01 to 2024-12-31.
- [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm) — 2025-01-01 to 2025-12-31.

## Conclusion and reproduction

The EBIT approach works as an arithmetic route for all 15 periods and removes the interest-disclosure dependency.
The remaining task is a defined operating tax/D&A/movement/investment reconciliation, rather than inventing interest.
Do not replace live historical FCFF, forecast calibration, EV or original approved history with these test figures.
The existing forecast's financed-investment perimeter is not certified by this cash-PP&E-only test.

- [Exact source operands, classified rows, fraction arithmetic and full bridges](company-data-preparation/historical-fcff-operating-test.json).
- [Flat calculation/comparison CSV](company-data-preparation/historical-fcff-operating-test.csv).
- Replay: `PYTHONPATH=src .venv/bin/python scripts/test_operating_fcff_from_filings.py --check`.
- Original filing receipts, frozen normalization, analyst packages and approval payloads are preserved. The earlier CFO calculation remains a separate definition; withdrawn estimates remain withdrawn.
