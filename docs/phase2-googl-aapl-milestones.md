# Phase 2 — GOOGL and AAPL scope-qualified trial records

## Status and attribution

The separately authorized temporary GOOGL and AAPL trials completed the existing
historical anchor → manual forecast → FCFF → DCF → EV → explicit equity bridge →
value/share workflow. Together with the unchanged [META record](phase2-meta-milestone.md),
these complete scope-qualified actual-company trials for **META, GOOGL and AAPL**.
They do not certify investment readiness, complete financial-input sufficiency,
claims coverage or fully diluted fair value. No permanent Base case, defaults,
financial approval, rating, current-price comparison or approved target follows.
[Phase 1 expansion remains paused](phase1-universe-pause-checkpoint.md).

This document transcribes the two user-supplied trial reports as **attributed
records**, not independently authenticated evidence, new approvals or recreated
test logs. Figures and verification below are reported from those trials; no
valuation, source-body comparison or prior arithmetic check was rerun for this
documentation checkpoint. Rounded tables are interpretive records, not executable
cases or full-precision saved outputs; displayed components may not sum exactly.

| Record | Supplied attachment (`Pasted text.txt` under `/Users/kc/.codex/attachments/`) | SHA256 of supplied report bytes |
| --- | --- | --- |
| GOOGL trial | `541759d9-0356-48f5-91ef-b4c982ee423a/` | `ce83d24b52207f26527fb9055866149b4bc743f4dd172c6e56200194305876c0` |
| AAPL trial | `d458d4db-2c04-403c-8b34-f6730de5db65/` | `16b0324fb5496781b786494a32635ef02f6bfa77c67d549d740a6429ffc458d3` |

These digests bind this transcription to supplied text, not to authenticated SEC
evidence or actual execution. The reports say temporary files were removed, all
571 tracked-file hashes were unchanged and clean `main` remained at `1d2e918`,
three commits ahead of local `origin/main`. No actual case, output or default was
saved. This checkpoint records assumptions only in documentation.

## Retained anchors and timing

| Binding | GOOGL / Alphabet consolidated | AAPL consolidated |
| --- | --- | --- |
| CIK / selected 10-K | 1652044 / `0001652044-26-000018` | 320193 / `0000320193-25-000079` |
| FY2025 period | 2025-01-01–2025-12-31 | 2024-09-29–2025-09-27 |
| Retained revenue | **402,836,000,000 USD** | **416,161,000,000 USD** |
| Source precision / scale | `-6` / base USD, scale 1 | `-6` / base USD, scale 1 |
| Analytical t=0 | **2025-12-31** | **2025-09-27** |
| Information cutoff | **2026-02-05**, SEC filing date; report notes acceptance February 4 at 21:56:03 | **2025-10-31**, SEC filing date |
| Authoritative historical schedule / package | [Schedule](company-data-preparation/GOOGL-analyst-input-package.md) / [JSON](company-data-preparation/googl-analyst-input-package.json) | [Schedule](company-data-preparation/AAPL-analyst-input-package.md) / [JSON](company-data-preparation/aapl-analyst-input-package.json) |

Exact source/effective revenue pointers, sequence-2 historical audits and pinned
audit digests remain in the [anchor integration](phase2-anchor-integration.md#fixed-selections-and-provenance).
Historical approval is not forecast or bridge approval. Both trials use later-filed
information at fiscal-end analytical t=0, not contemporaneous backtests or current
market-date valuations. AAPL retains ordinal fiscal forecast periods and its
earlier 53-week-year limitation; no unsupported week adjustment was made.

## GOOGL provisional trial

All future values and bridge policies below were **AI-analyst-selected estimates
under temporary-trial authority**, not user-supplied numerical forecasts or
reported actuals. All rates are percentages; money is USD billions unless stated.

| Temporary input | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 | Terminal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Revenue growth | 15% | 13% | 11% | 9% | 7% | 3% |
| Operating margin | 31% | 28% | 27% | 27.5% | 28% | 27% |
| Operating tax | 18% | 18% | 18% | 18% | 18% | 18% |
| Expense D&A / revenue | 8.203% | 11.844% | 14.628% | 16% | 16% | 16% |
| Investment / revenue | 39.503% | 37% | 32% | 27% | 23% | 21.5% |
| WC cash requirement / full revenue | 0.7% | 0.7% | 0.6% | 0.5% | 0.5% | 0.5% |

The report calculated the first three D&A ratios from **38/62/85bn**, and FY2026
investment from **183bn**, using 50-digit Decimal strings rather than these rounded
ratios. Management's reported FY2026 **175–185bn cash-CapEx** outlook informed an
estimated **180bn cash PP&E +3bn new non-overlapping financed assets**. Separately
estimated finance principal **0.8bn** was excluded from FCFF; cash CapEx already
excluded principal, so no META-style subtraction applied. This was not revenue
or margin guidance. Depreciation/commissioning, infrastructure costs and hiring
motivated initial margin compression followed by modest recovery as growth slowed.

FY2025 **21.136bn PP&E depreciation**, **91.447bn cash PP&E**, **1.606bn financed
additions** and **1.988bn principal** are historical observations, not complete
expense-D&A calibration or forward components. Forecast D&A included financed-asset
depreciation/amortization once; future software scope remained uncertain despite
historically immaterial capitalization. The 18% tax input was a normalized operating
cash-tax proxy, not reported ETR or a complete deferral/credit model.

Cash PP&E included opening capital-creditor settlements; WC excluded capital
creditors, financing, acquisitions, legacy settlements and income taxes. SBC,
operating-lease services and ongoing Other Bets/Waymo costs stayed in margins;
internal Waymo funding was not charged twice. Unclosed Wiz/Intersect consideration
and incremental acquired cash flows were both outside this scope.

**WACC 9.57%** was rounded from **9.56528%**: December 31, 2025 Treasury proxy
**4.18%**, judged beta **1.10**, **5% judged ERP**, **0.75% judged debt spread**,
**98/2 equity/debt** target weights and **20%** debt tax shield. Cost of equity was
9.68%; pretax debt cost 4.93%. The report cites Treasury historical rates; the
other building blocks are judgments, not observed company market estimates.

Terminal net reinvestment was **6% of revenue** (21.5−16+0.5), versus 22.14%
NOPAT/revenue: reported diagnostics of 27.10% reinvestment and 11.07% incremental
return supported 3% growth. This is conditional economic arithmetic, not verified ROIC.

| Reported annual result, USD bn | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Revenue | 463.261 | 523.485 | 581.069 | 633.365 | 677.701 |
| EBIT | 143.611 | 146.576 | 156.889 | 174.175 | 189.756 |
| FCFF | −30.482 | −15.162 | 24.220 | 69.987 | 104.772 |
| Discounted FCFF | −27.819 | −12.629 | 18.412 | 48.557 | 66.342 |

| Reported EV reconciliation | USD bn |
| --- | ---: |
| Explicit-period PV | 92.863 |
| Terminal FCFF / Year-5 terminal value | 112.662 / 1,714.799 |
| Discounted terminal value | 1,085.813 |
| **Enterprise value** | **1,178.675** |

Reported terminal contribution: **92.12%**. Early infrastructure spending suppressed
FCFF; later monetization and spending moderation dominated value.

| Named bridge choice | Signed USD bn | Measurement / policy limitation |
| --- | ---: | --- |
| Eligible current financial assets | +56.430 | Reported gross cash/current marketables 126.843 less estimated 70.413 reserve: one quarter of forward cash operating expenses; conditional accessibility, not a reported restriction |
| Notes | −45.600 | Reported fair-value measurement; carrying/face alternatives and overlapping totals excluded |
| Finance leases | −2.500 | Carrying proxy; children not added again |
| Consolidated NCI | −3.400 | Carrying proxy including redeemable NCI |
| Legacy income-tax payables | −10.054 | Nominal carrying proxy, not claim PV; corresponding settlements excluded from forecast tax/WC |
| **Equity reference** | **1,173.552** | Before unresolved populations |

Reported denominator **12.088bn issued shares** = A 5.822 + B 0.837 + C 5.429bn.
The trial assumed economic equivalence apart from voting, without a control premium;
neither Class-A-only shares nor diluted EPS shares were substituted. The reported
**97.08 USD/share** is a dated basic-common-equivalent reference, not fully diluted value.

Excluded **68.687bn strategic carrying holdings** require realizability, tax and
funding treatment; adding the full carrying amount was only a **+5.68 USD/share**
diagnostic. **15.594bn accrued fines and settlements** require net-obligation/escrow
reconciliation: gross deduction could repeat already funded settlements. Existing
rights within **282m outstanding RSUs** remain unresolved; no full addition or
invented service fraction was used. Venture commitments, guarantees, credit
backstops, additional financing and unidentified claims remain incomplete and
potentially unbounded. Gross exposure is not a claim PV.

## AAPL provisional trial

All future values and bridge policies were **agent-selected**, not annual guidance
or approved financial assumptions. Rates are percentages; money is USD billions.

| Temporary input | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 | Terminal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Revenue growth | 8% | 6.5% | 5.5% | 4.5% | 4% | 2.5% |
| Operating margin | 31% | 31.5% | 32% | 32.25% | 32.25% | 31% |
| Operating tax | 17.5% | 18% | 18.5% | 19% | 19% | 19% |
| Expense D&A / revenue | 3.004% | 3.134% | 3.2% | 3.2% | 3.1% | 3% |
| Investment / revenue | 4.005% | 4.3% | 4.5% | 4.7% | 4.8% | 5% |
| WC cash requirement / full revenue | 0.25% | 0.30% | 0.30% | 0.35% | 0.35% | 0.40% |

The first two D&A ratios were calculated from **13.5/15bn**, FY2026 investment
from **18bn**, divided by forecast revenue using Decimal arithmetic. Growth
moderation and Services mix were balanced against China weakness, tariffs and
AI/R&D costs. Final FY2026 margin 31%, at an estimated annual gross margin 47.8%,
allowed approximately 75.5bn operating expenses; neither is reported guidance.

The report's October 30 call context was December-quarter growth **10–12%**, gross
margin **47–48%**, expenses **18.1–18.5bn**, tax approximately **17%**. It used a
**third-party Motley Fool transcript reproduction** alongside official filings and
Apple's release because Apple's replay expired. Preserve that attribution and
quarterly scope; this checkpoint does not authenticate it as a primary-source
transcript or promote it to a full-year forecast.

FY2025 cash PP&E **12.715bn**, CFO D&A **11.698bn** and rounded PP&E depreciation
**8.0bn** did not establish complete expense D&A. FY2026 investment estimated
**17.5bn cash PP&E +0.5bn new financed assets**; **0.6bn estimated principal** was
financing, outside FCFF. Combined historical ROU additions were not split by
residual. Software within PP&E and financed depreciation were included once;
R&D, SBC and operating-lease services stayed expensed. Positive WC allowed for
ordinary supplier/inventory/vendor-receivable/accrual timing, excluding capital
creditors already in cash PP&E. Buybacks/dividends did not reduce FCFF or shares.
FY2024 Ireland charges and FY2025 settlement distorted tax history; **43.369bn**
FY2025 cash income taxes were not adopted as recurring forecast taxes.

**WACC 8.59%** was rounded from **8.586385%**: September 26 Treasury proxy **4.20%**
(preceding trading day), September 1 monthly implied ERP **3.94%**, judged beta
**1.15**, spread **0.75%**, target equity/debt **97/3**, marginal-US debt shield
**21%**. Cost of equity was 8.731%; pretax debt cost 4.95%. The report identifies
Damodaran's **trailing-12-month cash-yield** ERP variant, the same variant as META's
4.23%, not adjusted payout. It cites `ERPSept25.xlsx` and `ERPbymonth.xlsx`;
workbook metadata supported pre-anchor availability without authenticating the
first publication instant. The approximately four-week lag is explicit, not an
exact September 26 ERP observation.

Terminal net reinvestment **2.4% of revenue** (5−3+0.4), versus 25.11% NOPAT/revenue,
gave reported diagnostics of 9.56% reinvestment and 26.16% incremental return at
2.5% growth. This physical-capital/WC diagnostic is not verified historical ROIC.

| Reported annual result, USD bn | FY2026 | FY2027 | FY2028 | FY2029 | FY2030 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Revenue | 449.454 | 478.668 | 504.995 | 527.720 | 548.829 |
| EBIT | 139.331 | 150.781 | 161.598 | 170.190 | 176.997 |
| FCFF | 109.324 | 116.621 | 123.623 | 128.091 | 132.117 |

| Reported EV reconciliation | USD bn |
| --- | ---: |
| Explicit-period PV | 475.743 |
| Terminal FCFF / Year-5 terminal value | 127.755 / 2,097.783 |
| Discounted terminal value | 1,389.349 |
| **Enterprise value** | **1,865.092** |

Reported terminal contribution: **74.49%**.

| Named bridge choice | Signed USD bn | Measurement / policy limitation |
| --- | ---: | --- |
| Eligible financial assets | +82.983 | Reported cash/current/noncurrent marketables 132.420 less estimated 49.437 reserve: two months forward operating costs excluding D&A; conditional accessibility |
| Notes | −80.400 | Reported fair-value measurement; carrying alternative excluded |
| Commercial paper | −7.979 | Carrying proxy |
| Finance leases | −1.230 | Carrying proxy; no overlapping total added |
| Opening current income-tax payable | −13.016 | Nominal carrying proxy, not PV; settlements excluded from forecast tax/WC |
| **Equity reference** | **1,845.449** | Before unresolved populations |

Fixed denominator: **14.773260bn fiscal-end issued common shares**, producing
reported **124.92 USD/basic share**, not fully diluted fair value. Later cover,
weighted-basic and diluted EPS denominators were excluded. Existing rights within
**151.574m unvested RSUs** remain unresolved; no earned fraction, full RSU addition
or duplicate future-service SBC charge was manufactured.

Noncurrent marketables retain duration, credit and liquidation risk; they are not
cash. FY2024 Ireland escrow restrictions were not deducted again from FY2025
balances; other restrictions remained unquantified. Other tax/legal, pension,
preferred/NCI, derivatives and unidentified claims remained explicit omissions,
not zero requirements or transferred historical approvals. Gross tax assets and
unrecognized-tax-benefit disclosures were not mechanically selected. Standalone
reported diagnostics were **−5.26 USD/share** excluding long-term marketables,
**−0.70 USD/share** using Notes carrying value, and **−0.0677 USD/share** per extra
1bn net claim; none bounds total value.

## Reported diagnostics and verification — not rerun

Each stress changed only the named input group, holding other choices fixed.
These temporary diagnostics are not approved scenarios or reusable sensitivity
functionality, and do not bound either issuer's total value.

| Trial / separate diagnostic | EV, USD bn | Dated basic reference, USD/share | EV change |
| --- | ---: | ---: | ---: |
| GOOGL selected trial | 1,178.675 | 97.08 | — |
| GOOGL WACC +1 percentage point | 988.693 | 81.37 | −16.12% |
| GOOGL investment/revenue +2 points, annual and terminal | 1,000.744 | 82.36 | −15.10% |
| AAPL final trial | 1,865.092 | 124.92 | — |
| AAPL WACC +1 percentage point | 1,603.099 | 107.18 | −14.05% |
| AAPL investment/revenue +2 points, annual and terminal | 1,703.591 | 113.99 | −8.66% |

The GOOGL report states **219 independent rational-arithmetic comparisons** across
base/stresses and **26 inline observations** checked against hashed source bodies.
The AAPL report states **219 independent rational-arithmetic checks** across final
case/stresses and **33 inline observations** matched to retained bodies, with
isolated 50-digit Decimal arithmetic. Each reports maximum numerical difference
below **5×10⁻³⁸** and no engine defect. These are attributed prior checks, not newly
executed verification or independently authenticated logs. META's separately
reported 694 comparisons remain solely in its unchanged milestone record.

Both reports judged their cases defensible for illustrative analyst review,
requiring further financial review for investment use. Sustainable margins,
depreciation, investment, dated market judgments and incomplete awards/claims
drive limitations; displayed cents do not imply economic precision. Results are
neither conservative total-value bounds nor a harmonized company comparison.
See the [ERP reconciliation and remaining three-company checklist](phase2-completion-checklist.md).
