# Phase 2 — GOOGL and AAPL scope-qualified trial records

**Latest GOOGL reference:** the [2026-10-19 ERP reconciliation](#googl-erp-reconciliation--2026-10-19)
supersedes the original GOOGL ERP/WACC and resulting valuation reference below.
The original trial and AAPL record remain historical and unchanged; financial
limitations persist. ERP alignment does not establish full valuation comparability.

## Status and attribution

The separately authorized temporary GOOGL and AAPL trials completed the existing
historical anchor → manual forecast → FCFF → DCF → EV → explicit equity bridge →
value/share workflow. Together with the unchanged [META record](phase2-meta-milestone.md),
these complete scope-qualified actual-company trials for **META, GOOGL and AAPL**.
They do not certify investment readiness, complete financial-input sufficiency,
claims coverage or fully diluted fair value. No permanent Base case, defaults,
financial approval, rating, current-price comparison or approved target follows.
[Phase 1 expansion remains paused](phase1-universe-pause-checkpoint.md).

The original documentation checkpoint transcribed the two user-supplied trial reports as **attributed
records**, not independently authenticated evidence, new approvals or recreated
test logs. Figures and verification in the original trial sections are reported from those trials; no
valuation, source-body comparison or prior arithmetic check was rerun for this
original documentation checkpoint. New reconciliation checks are recorded separately
in the dated section below. Rounded tables are interpretive records, not executable
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

## GOOGL ERP reconciliation — 2026-10-19

### Authority, source and dates

The separately authorized reconciliation replaced only GOOGL's 5% judgment ERP
and resulting applied WACC. Analytical date **2025-12-31** and cutoff
**2026-02-05** remain fixed. OpenAI Codex (AI analyst) prepared the temporary
reconstruction at **2026-10-19T11:17:48+00:00**; this is execution metadata, not the
historical information date or a claim that estimates came directly from the user.

The original [Damodaran January workbook](https://pages.stern.nyu.edu/~adamodar/pc/implprem/ERPJan26.xlsx),
`Impl premium calculator`, selects trailing-12-month dividends plus buybacks
(B6=`C`), top-down growth (B8=`TD`), and no sustainable-payout adjustment (B16=`No`).
C45 is the ERP over the unadjusted US Treasury rate: cached value
**4.2312372103557351%**, reported as **4.23%**. The workbook's monthly sheet,
`Implied ERP (Monthly from 9-08)`, labels A210 **2026-01-01** (1904 date system),
J210 **ERP (T12m) =4.23%**. It is neither I210 sustainable-payout **4.18%**, K210
adjusted-risk-free **4.46%**, nor N210 net-cash-yield **3.96%**. Thus the earlier
descriptive phrase “trailing-12-month cash-yield” means column J, **not** the
distinct “Net Cash Yield” column. No misidentified META/AAPL number or variant
was found: September 1 AAPL's J206 is **3.94%** in this archived workbook.

Measurement is **start-2026 / December 31 closing market basis**, not publication
on January 1. The workbook metadata says modified **2026-01-06T20:42:16Z**; that
is not proof of upload or first publication. Damodaran's dated
[January 23, 2026 author post](https://aswathdamodaran.blogspot.com/2026/01/data-update-2-for-2026-equities-get.html?m=1)
documents the 4.23% result and links that workbook. This supports a publication
record within both META's January 29 and GOOGL's February 5 cutoffs, without
authenticating the first upload instant or contemporaneous December 31 availability.
Using the same observation is appropriate to the shared analytical date and
later-filed framing; no current observation or alternate ERP was substituted.

The [Treasury December table](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202512&type=daily_treasury_yield_curve)
confirms the unchanged **4.18% ten-year par yield on 2025-12-31**. It remains the
trial's Treasury proxy, not a default-risk-adjusted dollar risk-free rate.

Retrieved January workbook SHA256:
`d3cb1d01898431c31f5a0192934ff2b9859947efb2d6b9febd7da3a1a662ae4d`.
The current [rolling monthly workbook](https://pages.stern.nyu.edu/~adamodar/pc/implprem/ERPbymonth.xlsx)
corroborated the historical January J210 / September J206 values only; its
October-modified contents were not evidence of pre-cutoff publication or a source
of later market inputs. Retrieved SHA256:
`56605b608bad9fb49b24206954b3b38eedb364ebee0cc2663e5020e28449cc9f`.
These source checks did not change historical packages, source ledgers or approvals.

### Reconstruction and isolated WACC change

The disclosed economic inputs were reconstructed through the existing v2 reader
and CLI, with the same revenue/audit bindings and `manual-fcff-v1`,
`fiscal-end-annual-gordon-v1`, `manual-equity-bridge-v1` conventions. Annual growth,
margins, operating tax, WC and all terminal ratios remain exactly as in the
original table. First-three-year D&A ratios were recalculated from **38/62/85bn**
and compounded revenue, FY2026 investment from **183bn**, using isolated
precision-50/HALF_EVEN Decimal divisions. Rounded displayed ratios were not inputs.

The original reserve rule gives **70.4125915bn**:
`(FY2026 revenue × (1−31%) −38bn)/4`, retaining SBC. Gross current financial
balances **126.843bn** less that reserve give **56.4304085bn** eligible assets.
Notes **45.6bn**, finance leases **2.5bn**, consolidated NCI **3.4bn** including
redeemable NCI, and opening tax payables **10.054bn** are unchanged. Thus the
signed bridge is **−5.1235915bn**, with **12.088bn issued A/B/C common-equivalent
shares** fixed. Opening tax settlements remain outside forecast operating tax/WC;
capital creditors stay in cash PP&E, not WC or another bridge deduction.

The reconstruction reproduced original **1,178.675bn EV /97.08 USD/share** at
the supplied report's precision. The removed original JSON, metadata and
full-precision output were not recovered or independently authenticated; this is
a deterministic economic reconstruction from disclosed exact amounts/rules,
not a claim of byte-identical recovery or verification beyond the published digits.
No material numerical input needed for this reconstruction was left unspecified.

The selected ERP input is the published/series **4.23%**, matching META's disclosed
precision, rather than the calculator's extra cached digits. Unchanged judgments:
beta **1.10**, debt spread **0.75%**, equity/debt **98/2**, debt tax shield **20%**.

| WACC building block | Original | Reconciled |
| --- | ---: | ---: |
| Treasury proxy / ERP | 4.18% /5% | 4.18% /4.23% |
| Cost of equity = Treasury + beta × ERP | 9.68% | 8.833% |
| Pretax debt cost = Treasury + spread | 4.93% | 4.93% |
| Weighted after-tax WACC = 98% × Ke +2% × Kd ×(1−20%) | 9.56528% | 8.73522% |
| **Applied WACC**, rounded to 0.01 percentage point | **9.57%** | **8.74%** |

### Reconciled temporary results

Money is USD billions except USD/share. Original values here are the newly
reconstructed case, matching the earlier rounded record; percentage changes use
full-precision engine results. These remain assumption-led trial results, not a
standing Base case, defaults, fully diluted value or investment recommendation.

| Metric | Original reconstruction | ERP-reconciled | Absolute change | Relative change |
| --- | ---: | ---: | ---: | ---: |
| ERP | 5% | 4.23% | −0.77 pp | −15.40% |
| Applied WACC | 9.57% | 8.74% | −0.83 pp | −8.67% |
| Explicit-period PV | 92.862533 | 96.951930 | +4.089397 | +4.40% |
| Year-5 terminal value | 1,714.798910 | 1,962.757637 | +247.958727 | +14.46% |
| Discounted terminal value | 1,085.812634 | 1,290.981541 | +205.168907 | +18.90% |
| **Enterprise value** | **1,178.675167** | **1,387.933471** | **+209.258305** | **+17.75%** |
| Terminal contribution | 92.121448% | 93.014656% | +0.893208 pp | +0.97% |
| Equity reference | 1,173.551575 | 1,382.809880 | +209.258305 | +17.83% |
| **Basic-common-equivalent USD/share** | **97.084015** | **114.395258** | **+17.311243** | **+17.83%** |

| Fiscal year | Unchanged FCFF | Original discount factor | Reconciled discount factor | Original PV | Reconciled PV |
| --- | ---: | ---: | ---: | ---: | ---: |
| FY2026 | −30.481782 | 0.9126585744 | 0.9196247931 | −27.819460 | −28.031802 |
| FY2027 | −15.161745 | 0.8329456735 | 0.8457097601 | −12.628910 | −12.822436 |
| FY2028 | 24.220206 | 0.7601950109 | 0.7777356631 | 18.412080 | 18.836918 |
| FY2029 | 69.986828 | 0.6937984950 | 0.7152249983 | 48.556756 | 50.056329 |
| FY2030 | 104.772499 | 0.6332011454 | 0.6577386410 | 66.342066 | 68.912921 |

Terminal FCFF remains **112.662288bn**. The lower WACC both reduces the Gordon
denominator and discounts future flows less; negative early FCFF has a more
negative PV. The rise in EV is predominantly discounted terminal value, without
any operating improvement or changed bridge/denominator. No unexpected numerical
differences or engine/interface defects were found.

| Separate diagnostic around reconciled case | Applied WACC | EV | Equity reference | USD/basic-equivalent share | EV change vs reconciled |
| --- | ---: | ---: | ---: | ---: | ---: |
| Central reconciled | 8.74% | 1,387.933471 | 1,382.809880 | 114.395258 | — |
| WACC +1 percentage point | 9.74% | 1,142.299748 | 1,137.176156 | 94.074798 | −17.70% |
| Investment/revenue +2 percentage points, annual and terminal | 8.74% | 1,183.572351 | 1,178.448759 | 97.489143 | −14.72% |

Each diagnostic changed only its named group, holding bridge/reserve/shares fixed;
these are temporary standalone stresses, not scenarios, implemented sensitivity
features or bounds on total value.

### Verification performed in this reconciliation and retained limits

All four temporary cases passed calculation-free CLI validation, then explicit
JSON and summary runs using the unchanged reader/Stages A–C. **292 independent
exact-rational output comparisons** checked revenue compounding, eight annual
operating components, FCFF handoffs, five discount factors/PVs, terminal operating
components, terminal/explicit PV/EV and bridge/subtotals/shares/per-share across
the four cases. Two additional exact-rational equalities checked the WACC builds.
Arithmetic comparison policy: absolute tolerance **1e−33** plus **1e−47 × |reference|**;
maximum observed absolute difference approximately **8.69e−38** (base USD or
dimensionless factors as applicable). The independent implementation did not call
engine calculation functions. JSON/summary units, dates and reconciliation were
inspected; summary rounding remains display-only.

Central submitted cases differed only in WACC; annual operating results, terminal
components, Stage C inputs and signed contributions matched exactly. Case bytes
were unchanged by execution. All **573 tracked-file hashes** matched the starting
checkpoint after execution, before these documentation edits. No full suite or
prior source-body/219-check trial verification was rerun. This section records
new checks separately from those earlier attributed checks.

Temporary cases, JSON/summary outputs, downloaded workbooks and verification
scripts were removed after review; nothing executable or valuation output was
saved in the repository. All six templates retain their 37 numerical inputs unset.
No META/AAPL rerun was needed or performed, and their results remain unchanged.

ERP variant/dated-observation reconciliation is complete for this authorized
correction. Broader market judgments and direct three-company comparability are
not approved: beta, weights, spread/shield, cutoff/observation lag and operating
economics differ. Strategic-asset eligibility, NCI/lease/tax measurement proxies,
net fines/escrow settlement, existing awards, venture commitments/guarantees and
unidentified financing/claims retain the original uncertainty, including unbounded
omissions. No total-value bound, fully diluted fair value or investment-readiness
claim follows; [Phase 1 remains paused](phase1-universe-pause-checkpoint.md).
