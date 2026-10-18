# Phase 2 META Base-case consumer contract — Stages A–C conventions approved

**2026-10-18 · convention version `meta-base-fcff-v1`.** The user's explicit
Stage A instruction approves **P2M-01–09** as clarified in proposal v1 and
authorized **P2M-14 for Stage A implementation and synthetic verification**.
The subsequent Stage B instruction approves **P2M-10–11** (fiscal-end analytical
valuation, annual years 1–5, constant manual WACC, explicit terminal ratios and
Gordon growth) and **P2M-14 Stage B implementation/synthetic verification**.
Discounting convention version is `fiscal-end-annual-gordon-v1`; Stage A economic
convention `meta-base-fcff-v1` is shared. The subsequent Stage C instruction
approves **P2M-12–13 mathematical/interface conventions** and **P2M-14 Stage C
implementation/synthetic verification** under `meta-base-equity-bridge-v1`.
Actual META numerical assumptions,
their reviewed scope/rationale and META execution remain unapproved; financial
sufficiency of actual inputs remains **NOT_ASSESSED**. **Actual META bridge,
share and award selections, unresolved requirements and all actual-case
execution remain pending.** No automatic
follow-on work is authorized. Historical acceptance records are not amended.

Proposal history: v1 was prepared at
`240f51d6893a8468f0566dfcdfcbabc4c1d97327` from clean `main`, matching live
`origin/main`, then clarified to distinguish convention approval, synthetic
verification and actual-case execution. Its original status was:

> Documentation only; all economic recommendations proposed, awaiting review.

Stage A started at that same HEAD with the expected uncommitted documentation
changes preserved. This approval supersedes v1's pending status only for the
conventions and implementation scope expressly listed above. Stage B started at
the same HEAD with the expected uncommitted Stage A code/tests/docs preserved;
its approval extended Stage A without approving actual inputs or the equity bridge.
Stage C starts at the same HEAD with uncommitted Stage A/B work preserved;
its later approval supersedes the proposal's pending mathematical/interface and
synthetic-implementation status only, selecting no actual META inputs.

The [pause checkpoint](phase1-universe-pause-checkpoint.md) controls Phase 1:
24 completed scoped histories, CAT/JNJ/CVX partial, 15 assessment-only; 199
selected annuals and 11 deficits. Preserve frozen-v1, evidence, unknowns, approvals
and the resumption backlog. Stages A–C change no historical preparation.

## 1. Company, anchor and authority

The approved convention covers consolidated META (Family of Apps and Reality Labs), one Base case,
five manually specified ordinal forecast periods, labeled FY2026–FY2030.
Labels are not discount dates. Retain FY2021–FY2025 as context without requiring
every historical field as an operand.

| Binding | Exact retained reference |
| --- | --- |
| Selected anchor | CIK **1326801**, form **10-K**, accession **0001628280-26-003942**, annual **2025-01-01–2025-12-31** |
| Historical authority | [META schedule](company-data-preparation/META-analyst-input-package.md); [effective JSON](company-data-preparation/meta-analyst-input-package.json) `/current_history/periods/4`, version 1 |
| Revenue seed | Effective `/inputs/revenue`: **200966000000 USD**, precision `-6`, reported; underlying `/periods/4/facts/revenue`. This is a historical seed, not a forecast assumption. |
| Historical approval | JSON `/history_approval`, sequence **1**, UTC **2026-10-17T18:17:50.735170+00:00**, audit SHA256 `ac2514aa5c57e8959f38f90e9cd8687748b490a01d75647e172b2922fed54927` |
| Approval binding | Source commit `9bb110cb208ce3abcac0365c4ecf4820c498d60d`; source revision `19907563235d652f5913f92ede3d2c41035d096f665304d35759a312b7383178`; review revision `d253b875b14907963169fd7734e01fdf2500de01d0d447cc4b7fb4fb9bbb24ec`; proposal revision `8fedd075ac4d3ed087bb134b6a3bf409ec232d905410faa04e765f6f403b7b3d` |
| Retained primary / instance | [Primary receipt ledger](evidence/independent-validation-document-acquisition.json) `/artifacts/0`; [instance receipt ledger](evidence/income-binding-repair.json) `/artifacts/13`; exact URLs/body digests and occurrences in package `/periods/4/sources` and `/facts` |

Historical decisions META-CF/SBC/CASH/CLAIMS/SHARES/DA/INV/FIN are active in
`/current_history/active_decisions`; original proposal flags remain historical.
The audit's source commit differs from the original package's source commit
`afd1a2598a790826be5dd1f4beebaf0ea412467a`; preserve both roles. The effective
view records 70/70 scoped historical requirements, but
`valuation_consumption_approved=false`, complete expense D&A remains unknown,
and complete debt/reinvestment remain false. Evidence-accounted preparation and
financial-input sufficiency for actual inputs under this consumer are separate:
the latter remains **NOT_ASSESSED**, pending actual input review and execution
authorization despite convention approval and synthetic verification.

## 2. Reuse and exact operand boundary

Reuse [ForecastYearAssumptions and ValuationAssumptions](../src/valuation_platform/valuation/assumptions.py)
and `valuation_assumptions_to_dict`; do not replace their framework. For each
ordinal period `t`, the approved equations are:

| Existing field / calculation | Proposed equation and consumed operands |
| --- | --- |
| `revenue_growth` | `R[t] = R[t-1] × (1 + growth[t])`; only FY2025 revenue seeds `R[0]` |
| `operating_margin` | `EBIT[t] = R[t] × margin[t]`; manual margin includes SBC and the agreed lease/D&A expense basis |
| `forecast_tax_rate` | `Tax[t] = max(EBIT[t], 0) × rate[t]`; `NOPAT[t] = EBIT[t] − Tax[t]` |
| `d_and_a_percent_revenue` | `DA[t] = R[t] × da_ratio[t]`; add back only depreciation/amortization already reducing this forecast EBIT |
| `capex_percent_revenue` | `Investment[t] = R[t] × capex_ratio[t]`; approved forecast scope in section 3, distinct from historical cash Capex |
| `change_in_operating_nwc_percent_revenue` | `WCcash[t] = R[t] × wc_ratio[t]`; positive cash requirement, negative release |
| Forecast FCFF | `NOPAT[t] + DA[t] − Investment[t] − WCcash[t]`; these four forecast operands only |
| `wacc`, `terminal_growth` | Stored/structurally validated in Stage A; Stage B now consumes them under approved P2M-10–11 |

Historical EBIT, D&A, cash PP&E, ETR, CFO and movement rows are **context only**
for this independent-manual path, not additional operands or automatically
populated rates. Stage B consumes approved forecast FCFF, WACC, terminal inputs
and timing; stage C consumes enterprise value and separately approved dated
bridge/share inputs. No five-year historical completeness gate is imposed on
an operation that consumes only the revenue anchor.

Use base USD internally, dimensionless fractional rates, and actual share units
at stage C; millions are display scale only. Preserve historical raw value,
sign, scale and precision: historical cash Capex is a negative contribution,
whereas forecast investment is a nonnegative expenditure subtracted once.
Never take an absolute value to disguise a conflicting source sign.
Use the approved local Decimal context of precision 50, `ROUND_HALF_EVEN`, no intermediate
quantization, explicit failure on nonfinite/overflow results, and exact string
serialization. Round only displayed USD millions/per-share amounts, separately
from stored results; computational digits do not improve source precision.

**Implemented structural checks:** finite Decimal rates (no int/float/string
coercion), growth ≥ −1, tax in [0,1], nonnegative D&A/Capex ratios, signed WC
ratio, unrestricted finite margin; ordered indices 1–5, unique nonempty labels,
positive integer CIK, exact date, nonempty accession/schema; WACC > 0 and
−1 < terminal growth < WACC. [Existing tests](../tests/valuation/test_assumptions.py)
cover these and immutability/serialization. They do not approve business inputs.

**Implemented consumer checks:** supported schema version `"1"`, exact anchor
CIK/accession/start/end/form and annual revenue unit/scale/precision, approved
effective-view/audit consistency, source/review/proposal revisions and stale
rejection; positive revenue seed; missing required inputs; explicit five-period
labels, declared convention-version compatibility, explicit operand exclusions
and Decimal results. No network lookup infers “latest filing” or silently rolls
the selected anchor. Reuse retained source models
and audit validation rather than trust a copied approval boolean.
Actual manual-input author/date/rationale and semantic-review references remain
required for a future authorized META run; Stage A does not introduce an actual
input intake/review framework or treat their absence as a synthetic-build blocker.

**Semantic input review:** assess the actual forecast scope/rationale and joint
EBIT/D&A/investment/WC/SBC/lease consistency. Six aggregate rates cannot reveal
embedded SBC, lease or capital-creditor double counting. Code can validate
declared conventions and exclude explicit extra operands; it cannot establish
economic completeness, prove the rationale or detect hidden duplication within
ratios. Synthetic tests verify equations and those explicit boundaries, not the
economic validity of a META forecast.

The older architecture anticipated a `StandardizedHistoricalCompany` anchor.
The implemented narrow adapter instead validates the exact accepted META view
and pinned annual identity directly. It takes no standardized-history object,
overwrites no frozen values and does not rebuild or activate historical views.

## 3. Approved Stage A conventions and retained limitations

**Revenue/EBIT:** independently entered growth and consolidated operating
margins; no automatic historical averaging, segment summation, restructuring
adjustment or useful-life normalization. Historical EBIT is a comparison point.
Manual margins must identify the forecast expense perimeter and assumptions.

**Tax:** manual unlevered operating tax rate on positive EBIT; zero modeled
operating tax at zero/negative EBIT, so a loss carries through NOPAT without
an immediate tax benefit. This is a simplifying forecast convention, not a
reported tax zero. No NOL creation/utilization, carryback, deferred-tax valuation
or automatic reported-ETR substitution. It omits potential tax benefits and
non-income/minimum taxes; a requested additional tax requires separate design.

**Working-capital cash:** apply the existing direct ratio to **forecast-year
revenue**, not incremental revenue. It represents a period cash requirement,
not an NWC level; no closing-minus-opening level calculation. Exclude financing,
cash/investments, tax payments already modeled in Tax, and noncash D&A/SBC.
Because cash PP&E includes settlement of capital creditors, do not deduct that
settlement again through WCcash. Signed releases require a plausible, approved
rationale; negative ratios cannot imply perpetual unlimited releases.

**SBC:** retain its expense inside operating margins and NOPAT; no separate
SBC add-back or second expense deduction. The historical expense proxy and CFO
add-back remain different roles even where equal. Future employee-service cost
is distinct from outstanding awards, future issuance and the stage-C dilution
policy; those must be reconciled before per-share output to avoid charging the
same economic cost twice.

**D&A, leases and investment — approved convention, not automatic proxy reuse:**

- Operating leases remain service costs inside margins; no operating ROU
  amortization add-back, separate lease-payment subtraction, capitalized operating
  ROU investment or operating-lease debt deduction under this convention.
- Finance leases remain asset financing: forecast EBIT includes the associated
  operating asset depreciation; DA includes that expense once. Finance interest
  and principal are financing flows outside FCFF. Existing finance liabilities
  belong in the later financing bridge once, subject to stage-C approval.
- Interpret the existing `capex_percent_revenue` as **total modeled
  operating-asset investment**: gross cash PP&E plus separately identified,
  non-overlapping new finance-leased operating assets at inception, excluding
  finance principal. **P2M-07 is now APPROVED as a forecast convention** (previously
  proposed): an explicit consumer interpretation, broader than historical `cash_capex`,
  not a relabeling of its source facts. Keep cash purchases and noncash financed
  additions separately explained in assumption support. Do not subtract finance
  principal as another purchase, or omit new financed assets merely because their
  inception is noncash. No debt issuance inflow enters FCFF.
- Exclude acquisitions, strategic securities/equity-method investments and
  disposal proceeds from this initial gross investment ratio; explicitly review
  whether the revenue/margin path assumes growth needing those expenditures.
  Internally expensed software/R&D remains in margins, not repeated as investment.
  No capital-creditor stock, ROU liability movement or residual is a cash purchase.

**Historical calibration limitation:** the retained history cannot prove complete
expense D&A or complete reinvestment. META-DA accepts CFO D&A only as a limited proxy;
separate finance amortization is support, not an incremental add-back. Note/CFO
precision and scope differences, useful-life changes and separate impairments
remain. META-INV accepts gross cash PP&E, separately from capital creditors,
noncash ROU, acquisitions and strategic investments. Historical acceptance
therefore does not automatically supply complete historical calibration or prove
D&A/EBIT alignment. Historical calibration requires exact-scope review of the
inputs actually used; incomplete proxies must remain labeled as such.

Independently specified manual forecasts do **not** universally require historical
reconstruction or new evidence. Their actual EBIT/D&A/lease/investment assumptions
require explicit semantic consistency review before executing the META Base case;
that review resolves no historical unknown. The broader Capex convention is now
approved and implemented; actual META rates and their reviewed consistency
record are needed for execution, not implementation or synthetic verification.
A later scope change requires a separately designed lease-consistent alternative;
cash PP&E alone plus finance-as-debt is not asserted to be complete FCFF. No gap
is filled with zero, inferred inclusion or a balancing allocation.

## 4. Reconcile older readiness obligations for this consumer

The [older timing design](financial-timing-readiness-design.md) is preserved;
the [current historical-input contract](dcf-input-contract.md) and pause handoff
permit a different, explicitly reviewed consumer. P2M-08 approves this mapping:

| Older obligation | Disposition for this approved manual EBIT convention |
| --- | --- |
| Exact identity, dates, units, approved selection, immutable provenance | **Applicable:** validate consumed revenue and approval bindings; manual forecasts retain their own assumptions/convention identity. |
| Exact historical EBIT/D&A operands and exhaustive historical expense basis (gates 1–3) | **Inapplicable to arithmetic** while neither historical amount nor ratio is consumed. **Unresolved for historical-ratio reuse.** Forecast expense D&A must still match the forecast EBIT basis; historical proxy acceptance is no proof. |
| Book NWC levels, opening/closing identities, configured perimeter (gate 4) | **Inapplicable** to a directly assumed cash requirement. Required again for any proposed book-delta consumer; no historical state is upgraded or blocker removed. |
| Inventory/capitalization, incentives, tax and lease timing; count once (gates 3–5) | **Applicable** to forecast conventions and any historical calibration. Manual consistency must explain expense/add-back alignment and cash investment/WC boundaries. Unknown applicable interactions remain **unresolved**, not neutral. |
| CFO reconciliation and reported movement population | **Context/support only.** Preserve independent display checks and original FY2022–24 parser PARTIALs. CFO is not FCFF; movements already inside CFO are not deducted again. No CFO residual is an adjustment. |
| Structural errors versus unknown/incompatible economics | **Applicable:** reject broken identity/digest/unit links; retain missing/ambiguous/incompatible reasons separately. No coverage-based waiver or implicit readiness from manual entry. |
| Financial sufficiency beyond timing | **Unresolved** until actual META inputs pass enforceable checks and semantic review for execution. Convention approval and synthetic verification do not assess those inputs. Stage-specific requirements replace no historical acceptance records. |

Independent manual inputs require explicit economic rationale and joint
semantic consistency review before META execution, not manufactured historical
proof or universal reconstruction/new evidence. No historical unknown is resolved
by that review. If a rate is copied,
averaged or derived from history, label it **historically calibrated**, retain
exact numerator/denominator periods, signs, formula, scope/proxy status and
evidence; apply the relevant historical timing/expense/investment gates first.
Typing such a ratio manually does not bypass them. The old universal Phase 2
postponement/whole-history obligations do not restart the paused universe queue;
remaining [delivery obligations](phase1-delivery-acceptance-report.md) are carried
forward or explicitly scoped out, not claimed complete.

## 5. Stage B approval and remaining boundaries

**Stage B is approved and implemented for synthetic verification.** Analytical
t=0 is the anchor fiscal end; annual cash flows are discounted at integer years
1–5. No mid-year/stub timing or current market-date valuation is supported.
The output preserves Stage A identity, source/filing dates as supplied and all
provenance; no missing filing date or information cutoff is invented. It
explicitly discloses use of later-filed information: this is **not a
contemporaneous historical-information backtest**. The information cutoff remains
not established by the calculator. No historical source record is changed.

Use the existing constant manual WACC and terminal growth `g`, preserving
WACC > 0 and −1 < g < WACC. A separately supplied immutable `TerminalAssumptions`
requires operating margin, operating tax rate, D&A/revenue, investment/revenue,
and working-capital cash requirement/revenue. Margin is unrestricted finite,
tax is in [0,1], D&A/investment are nonnegative, and WC cash may be signed;
all rates must already be finite Decimal instances. Its declared economic
convention must match Stage A. It has no WACC, g or independent revenue-growth
field and copies no Year-5 ratios.

| Approved Stage B calculation | Consumed operands |
| --- | --- |
| `DF[t] = 1 / (1 + WACC)^t`, `PV[t] = FCFF[t] × DF[t]` | Validated five-period Stage A FCFF; WACC; integer t=1–5 |
| `Terminal revenue = Revenue[5] × (1 + g)` | Year-5 revenue and existing g |
| Terminal EBIT/tax/NOPAT/D&A/investment/WC cash/FCFF | Terminal revenue and the five explicit terminal ratios; shared Stage A equations, including no immediate loss-tax benefit |
| `TV[5] = Terminal FCFF / (WACC − g)` | Terminal FCFF, WACC, g |
| `PV TV = TV[5] / (1 + WACC)^5` | End-Year-5 terminal value and WACC |
| `EV = sum(PV[1..5]) + PV TV` | Discounted explicit and terminal flows |

Zero/negative FCFF, terminal value and EV remain visible, without clipping.
Inputs must support a sustainable growing perpetuity, including replacement and
growth investment and WC cash needs. Aggregate rates and matching convention
tags cannot prove that sustainability; actual assumptions require semantic
review, not automatic Year-5 perpetuation or historical proxy substitution.
Manual WACC must be justified consistently with nominal USD FCFF and leases;
no market WACC or price is acquired/derived. Actual META rates, terminal inputs,
their reviewed rationale/information scope and execution authorization remain
pending despite approved conventions and synthetic verification.

**Stage C:** bridge/share mathematical and interface conventions are now approved
and synthetically implemented; actual META execution still needs reviewed dated
amounts and populations. Decide
eligible financial assets/reserves/restrictions;
financing carrying-versus-economic values and complete claim scope; finance
leases already embedded in named financing; operating leases treated as service;
other claims/assets including strategic holdings, tax contingencies, preferred,
NCI and benefits where applicable. Historical no-additional-adjustment omissions
can be unbounded and need separate valuation-use decisions, not automatic reuse.
Gross current balances are not excess cash; named financing is not complete debt.
Choose share observation date, Class A/B economic equivalence, split basis,
existing-award treatment and future dilution policy. Fiscal-end classes,
independently reported aggregate, later cover shares and diluted EPS denominators
are distinct observations; none automatically supplies diluted valuation shares.

## 6. Implementation sequence — Stages A–C implemented; execution pending

Keep three gates distinct within the existing A–C sequence:

1. **Approve equations/conventions:** P2M-01–13 are approved for Stages A–C,
   with P2M-12–13 limited to mathematical/interface conventions. Convention
   approval alone does not authorize a run or select actual inputs.
2. **Implement and verify:** after a bounded implementation authorization, build
   the approved behavior and verify it with synthetic fixtures. Actual META
   numerical rates are not prerequisites for implementation or testing.
3. **Execute the META Base case:** supply actual manual assumptions and reviewed
   scope/rationale, pass programmatic checks and semantic input review, and obtain
   the relevant execution authorization. Verified code does not approve inputs.

These distinguish convention approval, synthetic verification and actual-case
execution; they add no approval model or replacement assumption framework.

| Stage | Modules / interfaces | Convention prerequisites, focused verification and META execution |
| --- | --- | --- |
| **A — implemented anchor boundary and five-year forecast through FCFF** | [consumer.py](../src/valuation_platform/valuation/consumer.py): `prepare_meta_revenue_anchor(package, decisions)`, `load_meta_revenue_anchor(repository_root)` validate retained metadata using existing relevant-content/hash/manual-identity helpers, without approval activation. [forecast.py](../src/valuation_platform/valuation/forecast.py): `RevenueAnchor`, `forecast_five_years`, `forecast_to_dict`, `serialize_forecast`; existing assumption classes remain unchanged. | P2M-01–09 conventions approved; Stage A implementation authorized. Synthetic checks cover independent multi-year arithmetic, 8.8/−29.7/13.2 examples, loss/zero taxes, full-revenue signed WC, zero/−100% growth, missing inputs, stale approvals/revisions, wrong identities/schema/units, deterministic immutable output, original precision, isolated Decimal context and HALF_EVEN ties. Explicit extra operands/unsupported convention versions are rejected; hidden ratio duplication is not detected. Optional historical context is not a revenue gate. Actual META rate sets, reviewed scope/rationale/semantic consistency and execution authorization remain pending. |
| **B — implemented discounting and terminal value through EV** | [discounting.py](../src/valuation_platform/valuation/discounting.py): `TerminalAssumptions`, `discount_to_enterprise_value`, `enterprise_value_to_dict`, `serialize_enterprise_value`. Consumes validated Stage A results, existing WACC/g and five explicit terminal rates; shared operating equations in `forecast.py`. | P2M-10–11 and Stage B implementation/synthetic verification approved. Checks nested Stage A models, five immutable ordered/finite annuals, labels and recomputed components against assumptions; dataclass type alone is insufficient. Synthetic tests cover independent integrated arithmetic, distinct terminal ratios, zero/negative g and flows/EV, invalid/missing inputs, malformed handoffs, unsupported timing/economic conventions, immutable traceable output and Decimal isolation/rounding. Actual META WACC/g, terminal inputs, rationale/information scope and execution remain pending. |
| **C — implemented equity/share arithmetic and traceable output** | [bridge.py](../src/valuation_platform/valuation/bridge.py): `BridgeComponent`, `BridgeObservation`, `PopulationCoverage`, `ValuationShares`, `BridgeInputs`, `bridge_to_per_share`, `bridge_to_dict`, `serialize_bridge`; fixed roles and existing `ManualIdentity` metadata. | P2M-12–13 mathematical/interface conventions and P2M-14 synthetic implementation approved. Revalidate/recompute publicly constructible Stage B results; require explicit coverage/omissions, dated base-unit operands and compatible declared class/award conventions. Reject duplicate numeric populations and declared overlap; do not certify hidden economic completeness or authenticate references. Actual META population/share/award selections and unresolved requirements remain pending. |

Stages A–C arithmetic is network-free; local anchor reads and historical
preparation stay separate.
Existing [company acceptance tests](../tests/analyst/test_company_batch_activation.py)
and [retained review tests](../tests/analyst/test_trillion_review_batch.py) provide
revision, stale-input, precision and preservation patterns. Do not activate
historical approvals again. Any future preparation change must maintain affected
issuer records/register under [AGENTS.md](../AGENTS.md). Stages A–C change neither
preparation field treatments nor accepted issuer values, so no issuer records
are amended. No evidence acquisition or corpus/full-suite run is performed.

Hand-check fixture specification (**synthetic units, not META assumptions**):
prior revenue 100, growth 10%, margin 20%, tax 25%, DA/revenue 5%,
investment/revenue 10%, WCcash/revenue 2% gives revenue 110, EBIT 22,
tax 5.5, NOPAT 16.5, DA 5.5, investment 11, WCcash 2.2 and FCFF **8.8**.
Changing only margin to −20% gives EBIT/NOPAT −22, tax 0 and FCFF **−29.7**;
changing only WCcash ratio to −2% in the profitable fixture gives FCFF **13.2**.
These independent expected results are implemented as synthetic tests, not
actual META assumptions or a numerical META Base case.

### Stage A implementation and verification

The immutable result retains the anchor (period, base USD, scale/sign, original
precision, exact source/effective/audit references and source occurrence metadata),
supplied immutable assumptions, convention `meta-base-fcff-v1`, and all eight
annual components. JSON-ready/deterministic serialization uses Decimal strings;
no display rounding or global Decimal-context mutation occurs. WACC/g are retained
and structurally validated by the existing model but unused in Stage A arithmetic.
Output explicitly records `semantic_input_review=NOT_ASSESSED_BY_CALCULATOR`.

The adapter pins the existing META audit SHA256 and revalidates source/review/
proposal revisions, five retained identities and the effective revenue selection.
It validates retained bindings, not fresh SEC XML or whole-history sufficiency.
A later historical approval requires a bounded consumer update. No approval is
created/reactivated, and no financial source object is changed.

**41 focused tests PASS** (14 new Stage A, 18 unchanged assumption, 9 company
approval/preservation tests):

```sh
PYTHONPATH=src python3 -m unittest tests.valuation.test_forecast tests.valuation.test_assumptions tests.analyst.test_company_batch_activation -v
```

At the Stage A checkpoint, the preservation assertion permitted only the two
new Stage A modules as additions; all pre-existing historical sources/evidence/
frozen artifacts remain under its unchanged-byte requirement. Local links,
targeted compilation and `git diff --check` are checked separately. Actual META
execution remained unapproved; Stage C was unapproved and unimplemented at that checkpoint.
These 41 checks are the retained Stage A checkpoint, separate from the expanded
Stage B and Stage C verification counts below.

### Stage B implementation and verification

The smallest extension is one module, `valuation.discounting`, reusing existing
assumption validation patterns and the shared Stage A operating equations.
WACC/g remain only in `ValuationAssumptions`. Before discounting, Stage B
revalidates anchor/period/assumptions and requires a five-year tuple of exact
annual result objects with finite Decimal components. Recomputing Stage A checks
schema, identity, convention, order, labels and every component; it does not
revalidate SEC bodies or certify economic consistency/sustainability.

Immutable `EnterpriseValueResult` retains the full Stage A result, terminal
assumptions, all annual FCFF/factors/PVs, every terminal component, terminal/PV
terminal value, explicit-period PV and EV. Serialization uses schema
`stage-b-enterprise-value-v1`, both convention versions and the complete Stage A
schema/source/assumption output. It records analytical timing, later-filed
information disclosure and `semantic_input_review=NOT_ASSESSED_BY_CALCULATOR`.
Fresh precision-50/HALF_EVEN contexts isolate precision, traps and flags; no
intermediate display quantization or noninteger exponent is introduced.

Independent integrated synthetic hand fixture: reuse the Stage A growth/expense
fixture above, but WACC 25%, g 5% and explicit terminal margin/tax/D&A/investment/
WC ratios 30%/20%/4%/9%/1%. Discount factors are 0.8/0.64/0.512/0.4096/0.32768;
annual PVs 7.04/6.1952/5.451776/4.79756288/4.2218553344 sum to 27.7063942144.
Terminal revenue 169.10355 gives EBIT 50.731065, tax 10.146213, NOPAT 40.584852,
D&A 6.764142, investment 15.2193195, WC cash 1.6910355 and FCFF 30.438639.
TV is 152.193195, its PV is 49.8706661376, and EV is **77.5770603520 synthetic
units**. These are test inputs/expected results, not META assumptions/value.

**Stage B checkpoint: 56 focused tests PASS** (15 Stage B +14 Stage A +18 existing
assumption +9 company approval/preservation). Stage B verification command:

```sh
PYTHONPATH=src python3 -m unittest tests.valuation.test_discounting tests.valuation.test_forecast tests.valuation.test_assumptions tests.analyst.test_company_batch_activation -v
```

At the Stage B checkpoint, the preservation check permitted only the three new valuation modules as additions;
historical source/evidence/frozen-artifact preservation remains strict. No
issuer preparation treatment changes or issuer-record updates are introduced.
No full suite/corpus, new evidence, historical approval activation or actual META
valuation is run.

## 7. PROPOSED Stage C decision sheet

**Current status (2026-10-18): P2M-12–13 mathematical/interface conventions and
P2M-14 Stage C implementation/synthetic verification are approved and implemented.**
The original decision sheet was documentation only and all its Stage C choices
were proposed/unapproved. Preserve that history: the retained META selections
below are **still PROPOSED**, not approved by the subsequent implementation request.
HEAD is still `240f51d6893a8468f0566dfcdfcbabc4c1d97327`;
the expected uncommitted Stage A/B work is preserved. No actual META valuation,
historical selection/approval change, evidence acquisition or company review is
authorized. The historical audit in section 1 approves preparation, not these
valuation-use proposals; actual financial-input sufficiency remains NOT_ASSESSED.

### Approved mathematical bridge conventions

```text
Equity value = enterprise value + eligible nonoperating assets
                              − financing claims − other equity claims
Value per share = equity value / approved valuation shares
```

Use nonnegative base-USD component magnitudes with explicit roles/signs:
`ELIGIBLE_ASSET` +1; `FINANCING_CLAIM` −1; `OTHER_EQUITY_CLAIM` −1;
`SUPPORT/EXCLUDED` non-additive. Eligibility adjustments to a gross asset must be
explained in its separately supplied eligible amount, not mislabeled as debt.
Every population is counted once across all families and the forecast: use a
parent **or** its children/alternative measurement, never both. Keep excluded
observations and unknowns visible; an exclusion/omission is not a reported zero.
Mathematical implementation with synthetic components is now approved; it selects
no actual META populations. Actual execution separately
requires approved populations, amounts, dates, rationale and unresolved-item
dispositions. Preserve raw negative equity/per-share arithmetic without claiming
it measures limited-liability option value or investment suitability.

### Retained META candidates — proposed use, not new selections

References below resolve to the linked [effective package](company-data-preparation/meta-analyst-input-package.json):
`F` = `/periods/4/facts`; `N` = `/periods/4/passages` (exact retained primary-note
excerpts, with offsets and source SHA256); `C` = `/periods/4/calculations`;
`E` = `/current_history/periods/4/inputs`. `L` denotes the
[claims ledger](retained-claims-shares-ledger.json) `/rows/34/fields/other_equity_bridge_claims_assets`;
the identical record is embedded in the package at
`/periods/4/preparation_ledger_evidence/retained-claims-shares-ledger/source_record`.
The approval binding is package `/history_approval`, audit SHA256
`ac2514aa5c57e8959f38f90e9cd8687748b490a01d75647e172b2922fed54927`;
`E` is current, original proposal flags under `C` are historical.

**Amounts below are USD millions at 2025-12-31 unless a period/date is stated.**
Underlying `F`/`L` amounts are base USD with scale 1 and original precision;
display conversion is ×1,000,000 back to USD, not additional precision.
R = reported fact; R-note = retained reported note observation, not a newly
verified/registered XBRL fact; D = derivation; P = proposed valuation proxy;
O = analyst omission assumption. Neither R nor historical acceptance implies
valuation eligibility. All proposed inclusion/proxy/omission choices need
P2M-12 approval; unresolved scope/value requirements block actual consumption.

| Population / exact reference | Amount, origin and scope / overlap | Proposed treatment, limitation and approval needed |
| --- | --- | --- |
| Cash `F/cash`; current marketables `F/marketable_current`; parent `C/0`, `E/cash_investment_components/selected` | 35,873 +45,719; R; gross parent **81,592 D**, same date, decimals −6. Parent already contains both children. | Use as eligibility starting populations, **not automatically excess cash**. Actual eligible positive amount requires an explicit operating-reserve and restriction policy. No zero reserve/default unrestricted assumption. Choose eligible parent or eligible children, not both; P2M-12 cash decision unresolved. |
| Cash/restricted-cash parent `F/cash_restricted_parent`; restriction breakdown `N/9` (also `N/10`) | 39,100 R includes cash 35,873 and restricted current 837 / other-assets 2,390 R-note. | Exclude the parent as an additional asset; recommend excluding the two restricted populations from eligible cash. They sit outside the 35,873 cash caption: do not subtract them again from it. Restriction scope/any recoverability and unknown restrictions still need review. |
| Fair-value-table restricted equivalents `N/11` | 2,539 R-note; a fair-value-measurement population, not the complete 837/2,390 cash-reconciliation partition. | Support only. No addition to cash, second restriction deduction or residual-based reconciliation. Population relationship remains unresolved. |
| Nonmarketable parent / measurement alternative / equity method `N/0`; equity method also `F/equity_method`, `L/observations/0` | **27,524 R-note =20,076 measurement-alternative +7,448 equity-method**. `L` warns of cash/investment-family overlap. | Never add 27,524 and 7,448. Recommend considering **+20,076 as an explicitly approved carrying-value proxy** for the measurement-alternative population only, conditional on excluding its returns/value from operating EV and reviewing strategic dependencies. Not fair value, excess cash or a selected actual input. Defer the 7,448 addition until its operating/venture perimeter is resolved. |
| Scale AI / Jio `N/0`; dimensioned candidates `L/observations/1` and `/2` | 13,800 /5,820 R-note (rounded), within measurement-alternative holdings. Generic diagnostics use `EquityMethodInvestments` with investee dimensions; the note identifies measurement-alternative scope. | Supporting constituents of 20,076, not additions to it or interchangeable consolidated equity-method facts. Preserve the generic scope/conflict flags; no new historical correction. Strategic/economic classification and carrying-proxy approval remain necessary. |
| Louisiana venture / other VIE investments `N/18`, `N/19`; dimensioned candidate `L/observations/3` | Louisiana 1,830 carrying R-note; other VIE maximum exposure 5,580 equals their carrying investments R-note. Both relate to the 7,448 equity-method population; rounded scope need not exhaust it. | Support, not separate additions to 7,448. Venture service/lease/funding economics can intersect forecast operations. Do not construct a residual investment or assume a passive asset outside EV; valuation treatment remains unresolved. |
| Senior Notes estimated fair value `N/1` | **57,220 R-note**, reported as $57.22bn, Level 2 estimate at fiscal end; source precision remains that rounded note basis. Same Notes as carrying/face figures below. | **Recommend −57,220** as the named Notes measurement for this fiscal-end analytical bridge, subject to explicit valuation-use approval. Retained reported fair value, not a fetched current price or complete financing total. No additional face/carrying deduction. |
| Notes carrying parents `F/debt_long`, `F/debt_parent`; face/discount `N/1`, `F/debt_discount` | 58,744 R appears under both debt QNames; face 59,000 R-note less 256 R discount/issuance costs. Historical named financing `C/1`, `E/debt_lease_components/selected` is **59,928 D =58,744+1,184**. | Alternatives/support only if the recommended 57,220 fair value is selected. Do not add the duplicate QNames, face, discount or historical subtotal. Issuance costs are not another asset/claim. Unknown additional borrowing/current populations are not certified absent by these Notes observations. |
| Finance-lease parent `F/finance_lease`; children `F/finance_current`, `F/finance_long` | **1,184 R =308 current +876 noncurrent**; already in historical financing 59,928. | **Recommend −1,184 as a carrying-value liability proxy**, once alongside the Notes fair value; not alongside 59,928. Approve carrying-to-economic-value simplification and completeness limitation. Children remain support. |
| Operating leases `F/op_lease`, `F/op_current`, `F/op_long`; finance ROU assets `N/19` | Operating liability 25,153 R =2,213+22,940; gross finance ROU asset 8,187 R-note within operating PP&E. | No separate operating-lease claim or ROU asset addition under the approved service-cost/finance-asset conventions. No operating-lease children addition; finance assets are already represented in operating EV, with their liability considered separately above. Approval of actual forecast consistency still needed. |
| Notes/lease payments and capital-creditor observation `F/finance_principal_cash`, `F/finance_interest_cash`, `F/capital_creditors`; `N/9` | **FY2025 annual observations, not instant claims:** principal 2,524 R; interest 31 R; unpaid Capex 9,331 R has `as_of=null`, duration 2025-01-01–2025-12-31. | Support only; no second finance claim, purchase or annual payment deduction. Do not promote 9,331 to a fiscal-end debt stock. Actual future settlement coverage across investment/WC/claims requires semantic review, not an inferred balance. |
| Noncash acquisition/intangible amounts in payables/other liabilities `N/9` | 2,659 R-note in FY2025 supplemental noncash activity; no separately retained approved instant claim/allocation here. | Do not deduct as a verified dated debt balance. Determine existing unpaid-claim scope and forecast-payment coverage or retain an explicit unresolved requirement; no zero/automatic operating classification. |
| Venture commitments/guarantees `N/18`; contractual commitments `N/1` | Louisiana initial leases ≈12,310, RVG threshold ≈28,000, maximum exposure 45,950 R-note; maximum includes investment, commitments, fundings and RVG. Contractual commitments 131,050 R-note, as of fiscal end. | No gross maximum/undiscounted commitment deduction. Do not count the included 1,830 investment again, derive fundings by residual, or equate “no RVG liability recorded” with zero economic exposure. Service/funding/guarantee effects and non-overlap with forecasts need explicit disposition; retained values are not claim PVs. |
| DTA populations `L/observations/4`–`/8` | Named carryforward DTA 4,432 R; SBC DTA 706 R; gross DTA 28,090 R; allowance alternatives 15,895 /15,900 R at different precision (conflict retained); net DTA 12,195 R. | Recommend **no standalone accounting-DTA addition** without a separately approved cash-benefit valuation. Children/allowance/net are overlapping, not additive. Neither QName nor net carrying amount establishes a pure usable NOL economic asset; future tax/SBC effects may overlap. Excluding potential tax value is an explicit valuation choice, not zero tax benefits. |
| Book equity `F/equity`; unidentified claims/borrowing `E/other_equity_bridge_claims_assets/additional_adjustment`, `E/debt_lease_components/no_additional_adjustment`; package `/periods/4/original_supporting_unknowns` | Book equity 217,243 R, not a separate asset. Additional preferred/NCI/pension/borrowing amounts **null O**, potentially unbounded; `L/unobserved_concepts` is not proof of absence. `N/4` retains legal/tax contingencies without a complete valued claim schedule. | No book-equity addition. Do not transfer historical omission approval into Stage C. Require a separate actual-use omission/coverage decision or supported amounts for relevant claims/assets, including legal/tax/benefit populations; unresolved required items fail closed. No missing amount becomes a zero requirement. |

These are named retained candidates, not an exhaustive bridge or approval of
new accounting classifications. In particular, no actual eligible-cash number,
venture/contingent-claim value or complete additional-claims amount is supplied.
The suggested Notes/finance-lease measurements do not by themselves permit a
complete actual META equity/per-share calculation.

### Shares, awards and SBC — proposed P2M-13

Share references use the same `F` alias. All are R; counts below are **actual
shares**, not millions; note dollar measures are explicitly labeled separately.
Fiscal-end counts/EPS have original decimals −6;
cover counts are `INF`, and the unvested-RSU fact has decimals −3.

| Exact fact key under `F` | Amount / date or period | Proposed use and overlap |
| --- | --- | --- |
| `shares:CommonStockSharesOutstanding:2025-12-31:e7683adf` | **2,530,000,000**, 2025-12-31, independently reported CommonStock-member aggregate | **Recommend as the dated common-outstanding starting denominator**, not automatically diluted valuation shares. Matches analytical t=0. It is not our derived class sum. |
| `shares:CommonStockSharesOutstanding:2025-12-31:1765640c` / `:1ca1ddc4` | Class A **2,187,000,000** / Class B **343,000,000**, 2025-12-31 | Support to the same common population; never add classes to the aggregate. Propose one common economic unit per A/B share and no voting/control premium; this is an **analyst class-equivalence assumption**, not proved by XBRL dimensions or equal arithmetic. Needs explicit approval for an A-share-equivalent output. |
| `shares:EntityCommonStockSharesOutstanding:2026-01-23:1765640c` / `:1ca1ddc4` | A **2,187,177,748** / B **342,377,716**, 2026-01-23 | Later cover-date observations, not year-end replacements or additions. No backdated roll-forward, inferred issuance/buyback bridge or new automatic aggregate. |
| `weighted_basic` / `weighted_diluted` | **2,521,000,000** / **2,574,000,000**, annual 2025-01-01–2025-12-31 | EPS period averages, not dated outstanding or an approved dilution estimate. Exclude as the default denominator; do not add the diluted increment to fiscal-end counts. |
| `shares:ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber:2025-12-31:3de8d43f` | **115,552,000** unvested RSUs, 2025-12-31; `N/2`–`/3` additionally report $500.68 weighted-average grant-date fair value and $54.81bn unrecognized compensation | Outstanding awards are not issued common shares, a cash liability or automatically fully dilutive shares. Grant-date value is not current award value/exercise price; unrecognized expense is not an equity claim PV. Do not multiply these into an automatic deduction. |

**Recommend the existing cost convention for future service:** forecast margins
already expense SBC once, so do not also add a mechanical future-issuance
denominator, repurchase charge or second SBC deduction for the same service.
This is a cash-equivalent economic-cost convention, not a prediction of actual
shares outstanding or an assertion that dilution is zero.

**Existing awards remain unresolved for an actual per-share case.** Determine
which rights reflect pre-anchor services versus compensation already charged
in forecast margins; then approve either a non-overlapping existing-award claim
deduction or an explicitly reconciled share adjustment, never both for the same
rights. Retained counts, expense and grant-date measures do not supply the
required value/service/vesting allocation. Do not silently ignore all existing
awards or add all 115,552,000 while also charging their full future service cost.
No automatic exercise-proceeds asset, treasury-stock calculation, tax-withholding
proceeds or future grant/vesting/repurchase schedule is justified here; actual
exercise terms/proceeds and the award-tax interaction would require a separately
reviewed input where relevant. A zero-proceeds/default option assumption is not
invented. The dated 2,530,000,000 selection can be approved as a starting basis
while final award-adjusted valuation shares/claims remain unapproved.

### Stage C implementation and synthetic verification

The later Stage C instruction authorizes the mathematical/interface conventions
and synthetic implementation proposed here. One network-free
[valuation/bridge.py](../src/valuation_platform/valuation/bridge.py) retains the
existing `EnterpriseValueResult` and provenance/`ManualIdentity` patterns without
a generic registry or evidence/approval framework. Narrow immutable inputs:
`BridgeComponent` (ID, role, finite nonnegative USD amount, date, population and
declared overlap/alternative IDs, origin/precision/source and decision references),
`ValuationShares` (positive Decimal shares, observation date, class/equivalence
convention, award-policy references), and `BridgeInputs` (component/observation/
coverage tuples, share selection, declared output class, explicit synthetic/manual
input basis, convention version and unresolved requirements).

`BridgeObservation` preserves SUPPORT/EXCLUDED/OMISSION metadata outside numeric
operands. An omission's amount remains null and needs no fabricated source or
precision; it requires decision references and rationale. `PopulationCoverage`
requires one explicit declaration per fixed role, exactly naming its numeric
populations and/or referenced omission observations, with existing `ManualIdentity`
author/UTC date/rationale metadata and decision references. Empty numeric tuples
therefore require explicit omissions, never an inferred zero or proof of absence.
Every omission binds to its role's coverage. Numeric population IDs are unique;
support may retain the same population without adding it. Overlap/alternative
references resolve to supplied component/observation IDs (no dangling/self links);
coexisting linked numeric operands or declared forecast overlap are rejected.
Source/decision references and coverage reviews are supplied declarations, not
authenticated approvals. `MANUAL_INPUT` is an input-basis label, not authority to
execute an actual META case; no actual-input approval workflow is implemented.

`bridge_to_per_share(stage_b, inputs)` returns every signed component,
eligible-assets/financing/other-claims subtotals, equity value, denominator and
per-share result, with the complete Stage B serialization/Stage A provenance and
all supplied convention/schema/source/assumption/review references. It uses local precision
50/HALF_EVEN, no intermediate quantization, immutable objects and deterministic
Decimal-string serialization via `bridge_to_dict`/`serialize_bridge`, schema
`stage-c-equity-bridge-v1` and convention `meta-base-equity-bridge-v1`.
Numeric components are ordered by ID for deterministic contributions/arithmetic;
observations and coverage are also serialized in stable order. Output retains
`semantic_input_review=NOT_ASSESSED_BY_CALCULATOR`, all exclusions/omissions and
explicit limits. No candidate loader or actual META selection is supplied.

Before consuming publicly constructible `EnterpriseValueResult`, Stage C requires exact
nested models and immutable ordered annuals, finite Decimal components, supported
conventions, anchor/timing alignment, and recompute via the existing Stage B
entry point. Compare annual FCFF/factors/PVs, every terminal component, TV/PV,
explicit-period PV and EV; a dataclass type or serialized EV alone is insufficient.
This reuses Stage B's narrow Stage A validation, not a general validation engine.

Programmatic checks reject explicit unresolved requirements, missing required amounts/review references,
wrong CIK/date/unit/scale, nonpositive shares, incompatible **declared** classes,
repeated IDs, parent/child or alternative-measurement coexistence and declared
forecast/claim overlap. They cannot prove economic completeness, undisclosed
restrictions, class rights or hidden overlap within amounts or aggregate rates.
Numeric bridge components/shares must match company and analytical fiscal-end
t=0, with USD/shares at scale 1; later cover counts fail the operand date gate.
Non-additive observations retain their own dates/units, with matching company.
Shares must match the declared output class and explicitly declare either a
single common class or common-unit equivalence, plus award policy
`sbc_expensed_no_duplicate_service_charge_v1`. These declarations do not prove
rights or award allocation; no automatic dilution/proceeds/award valuation runs.
Narrative semantic review must establish
eligibility and what an omission means before an actual run.

Focused synthetic verification hand-checks a signed bridge/per-share example
and integrates the retained **synthetic** A→B fixture through C. It covers
negative equity/raw per-share results, missing/null requirements, USD-million
versus USD/share scale errors, wrong dates/CIK/classes, duplicate parents/children,
Notes alternative bases, embedded finance leases, incompatible declared award/
SBC treatments, malformed publicly constructed B totals/years/terminal values,
immutable/deterministic provenance, overflow and caller-context isolation.
Independent flat-flow fixture: annual and terminal FCFF 8, WACC 25%, g 0 give
EV 32; assets 10+2, financing 20 and other claims 3 give equity **21** and
**5.25** per 4 shares. Integrated A→B fixture EV 77.5770603520 with that bridge
gives equity **66.5770603520**, per share **16.6442650880**. These are synthetic
units and assumptions, not actual META inputs/value.

**77 focused tests PASS** (21 Stage C +15 Stage B +14 Stage A +18 existing
assumption +9 company approval/preservation):

```sh
PYTHONPATH=src python3 -m unittest tests.valuation.test_bridge tests.valuation.test_discounting tests.valuation.test_forecast tests.valuation.test_assumptions tests.analyst.test_company_batch_activation -v
```

The preservation check permits only four new valuation modules as additions
(`consumer.py`, `forecast.py`, `discounting.py`, `bridge.py`); pre-existing
historical sources/evidence/frozen artifacts remain subject to unchanged-byte
checks. No issuer-record or historical preparation change is introduced. Local
links, targeted compilation and whitespace are checked separately. No actual META
selection/valuation, full suite, evidence acquisition, company review, commit or
push is performed.

## Consolidated decisions — approved implementation; proposed actual META choices

Repeated P2M-12/13 rows separate decisions within those existing IDs; they create
no new approval framework. **Actual META selection rows remain PROPOSED/pending**,
including supported numerical candidates. Implementation approval alone selects no actual
inputs and clears no unresolved requirement.

| Decision ID | Category | Treatment / current status | Limitation / approval still needed | Stage |
| --- | --- | --- | --- | --- |
| P2M-01 | Approved convention | META consolidated FY2025 anchor/accepted revisions; Base, five periods | Actual consumer-input review/execution pending; revenue alone seeds forecast | A |
| P2M-02 | Approved convention | Six annual rates; growth→revenue→manual-margin EBIT | No automatic historical calibration; actual rates/provenance pending | A |
| P2M-03 | Approved convention | Manual tax on positive EBIT; no immediate loss benefit/NOL model | Actual rate/rationale pending; no ETR substitution | A |
| P2M-04 | Approved convention | Signed WC cash ratio ×full forecast revenue | Actual cash perimeter/release sustainability and embedded overlap review pending | A |
| P2M-05 | Approved convention | SBC in margins; no separate FCFF add-back | Actual consistency and Stage C award/dilution treatment pending | A/C |
| P2M-06 | Approved convention | Expense DA once; operating leases service; finance leases financing | Actual joint consistency pending; historical unknowns unchanged | A |
| P2M-07 | Approved forecast convention | Cash PP&E +non-overlapping new finance-leased operating assets, excluding principal | Broader forecast meaning preserves historical cash-Capex definition; actual split/support pending | A |
| P2M-08 | Approved convention | Consumer-specific readiness; historical CFO/NWC context | Actual semantic review pending; historical calibration needs its own exact-scope review | A |
| P2M-09 | Approved numeric policy | Base USD, scale once, precision 50/HALF_EVEN; display-only rounding, reused through C | Does not prove completeness or improve source precision | A/B/C |
| P2M-10 | Approved convention | Fiscal-end analytical t=0, annual 1–5, constant manual WACC | Later-filed disclosure required; actual WACC/information review/execution pending | B |
| P2M-11 | Approved convention | Gordon growth; five explicit sustainable terminal ratios, existing g | No Year-5 defaults; actual ratios/sustainability review pending | B |
| P2M-12 | **Implementation conventions — APPROVED / IMPLEMENTED** | Signed eligible assets less financing/other claims; magnitudes/roles, dates, declared non-overlap, explicit coverage/omissions and Stage B recomputation | Synthetic verification approves no actual selections, evidence or economic completeness; no hidden-overlap detector | C |
| P2M-12 | **Actual META cash — PROPOSED** | Start from 35,873 cash +45,719 current marketables (parent 81,592); exclude separately restricted populations | Approve eligibility/reserve/restriction policy and supplied eligible amount; gross parent is not excess cash | C |
| P2M-12 | **Actual META strategic assets — PROPOSED** | Consider +20,076 measurement-alternative carrying proxy conditionally; defer 7,448 equity-method addition; 27,524 parent support only | Approve proxy/operating-EV perimeter and tax/value limitations; do not add constituents or venture exposure twice | C |
| P2M-12 | **Actual META financing — PROPOSED** | −57,220 reported Notes fair value and −1,184 finance-liability carrying proxy, each once; exclude 59,928 subtotal and alternative debt bases | Approve named measurements/proxy and residual financing coverage; not complete debt | C |
| P2M-12 | **Actual META exclusions — PROPOSED** | No book-equity, separate operating ROU/service-liability, gross accounting-DTA or gross commitment/maximum-exposure adjustment | Approve scoped exclusions; they are not claims of zero economic value/exposure. Forecast/claim coverage must remain consistent | C |
| P2M-12 | **Unresolved requirements** | Eligible cash/reserve, venture/service/funding/guarantee scope, dated unpaid-claim amounts, tax/legal/benefit/other claims and additional borrowing | Supply supported reviewed treatment or separately justify explicit omission; historical omissions can be unbounded. No default zeros or automatic historical approval transfer | C actual run |
| P2M-13 | **Implementation conventions — APPROVED / IMPLEMENTED** | Equity /positive dated valuation shares; declared class/award compatibility, unit/date checks, immutable deterministic output | Mathematical success is not approval of actual share rights, award adjustments or dilution | C |
| P2M-13 | **Actual META starting shares — PROPOSED** | 2,530,000,000 reported common outstanding at 2025-12-31; assume A/B 1:1 common economics, no control premium | Approve dated basis and explicit class-equivalence assumption; cover/EPS/award counts are not substitutes or additions | C |
| P2M-13 | **Actual META future-service treatment — PROPOSED** | Cash-equivalent SBC cost remains in margins; no duplicate future-issuance/repurchase charge for the same service | Approve allocation/convention consistent with actual margins; does not predict zero actual issuance | C |
| P2M-13 | **Unresolved existing awards/proceeds** | 115,552,000 unvested RSUs are not automatic shares or a valued claim; separate pre-anchor rights from already forecast-expensed service | Approve one non-overlapping claim/share adjustment or justified omission after review; value/vesting/service allocation, relevant exercise proceeds and award-tax effects unresolved | C actual run |
| P2M-14 | Implementation scope | **AUTHORIZED / IMPLEMENTED: A/B/C mathematical interfaces and synthetic verification only**, with prior authority preserved | Actual META assumptions/population/share/award selections, unresolved requirements and execution remain pending | A/B/C |
