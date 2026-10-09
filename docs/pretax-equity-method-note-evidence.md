# Pretax equity-method note evidence

## Scope and decision

Phase 1H.4 Wave 10 inspects the exact 33 selected 10-K accessions and annual
periods frozen in `pretax-presentation-evidence-results.md`. The 12 ORCL, MCD,
and PG issuer-extension periods are excluded. This is filing research only: it
does not change `PRETAX_INCOME_POLICY`, the Pretax primitive, fallback
precedence, standardized output, or corpus counts.

The exact-period classification is:

- 8 `INCLUDED_PRETAX`: MA 3 and CVX 5;
- 20 `SEPARATE_NET_OF_TAX`: AMZN 5, MU 5, CAT 5, and PM 5;
- 5 `UNRESOLVED`: LIN 5, because the filing directly establishes both
  after-tax corporate-investee income and pretax partnership/LLC-investee
  income; and
- zero `SEPARATE_PRETAX` and zero `NO_MATERIAL_ACTIVITY_FOUND`.

The research establishes exact-accession economic scope for the 8
`INCLUDED_PRETAX` periods, but it does **not** establish a deterministic,
machine-checkable economic-equivalence rule. Safe new production Pretax
resolutions therefore remain **zero**. The 8 periods are evidence candidates
for a later reviewed design, not normalized results.

## Methodology and evidence rules

Only the selected filing's official SEC primary document was used. Each row
binds the candidate amount to its authoritative annual period and records the
filing location that directly describes the equity-method treatment. Primary-
statement order is used only when the line itself identifies equity-method or
unconsolidated-affiliate activity; otherwise a note must identify the line in
which the activity is recognized.

`INCLUDED_PRETAX`, `SEPARATE_PRETAX`, and `SEPARATE_NET_OF_TAX` require a
direct line-location or accounting-policy statement in that accession.
`NO_MATERIAL_ACTIVITY_FOUND` requires affirmative filing evidence and is not
inferred from silence. Numerical equality, the candidate tag name, statement
membership, ETR plausibility, presentation order alone, and a small balance do
not determine scope. Comparative evidence is accepted only where the exact
accession presents the exact annual period. Quotations below are deliberately
short; the location and SEC link are the authority.

“Quantified” means that the filing supplies a separable amount for the activity
or identified component. “Not isolated” means the filing proves location but
does not provide a complete equity-method amount. Percentages below are simple
comparisons with the frozen candidate amount and are not a project materiality
threshold.

## Complete 33-period inventory

### Amazon — stable separate net-of-tax presentation

Each accession's Consolidated Statements of Operations places
`Equity-method investment activity, net of tax` after the income-tax provision.
Note 1, Summary of Significant Accounting Policies, under Non-Marketable
Investments, states that the investee earnings/losses and related basis,
gain/loss, and impairment items are recognized in that line. This is direct
`SEPARATE_NET_OF_TAX` evidence, not candidate equivalence.

| Report date | Annual period | Accession and SEC evidence | Classification | Quantitative evidence |
|---|---|---|---|---|
| 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001018724-22-000005` — [10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/amzn-20211231.htm), Consolidated Statements of Operations and Note 1, Non-Marketable Investments: “recognized in ‘Equity-method investment activity, net of tax’” | `SEPARATE_NET_OF_TAX` | $4m income versus $38.151bn candidate; quantified and below 0.1% |
| 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001018724-23-000004` — [10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/amzn-20221231.htm), same statement line and Note 1 location | `SEPARATE_NET_OF_TAX` | $3m loss versus $(5.936)bn candidate; quantified and below 0.1% in magnitude |
| 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001018724-24-000008` — [10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/amzn-20231231.htm), same statement line and Note 1 location | `SEPARATE_NET_OF_TAX` | $12m loss versus $37.557bn candidate; quantified and below 0.1% |
| 2024-12-31 | 2024-01-01 → 2024-12-31 | `0001018724-25-000004` — [10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm), same statement line and Note 1 location | `SEPARATE_NET_OF_TAX` | $101m loss versus $68.614bn candidate; quantified, about 0.15% |
| 2025-12-31 | 2025-01-01 → 2025-12-31 | `0001018724-26-000004` — [10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm), Consolidated Statements of Operations; Note 1; MD&A caption `Equity-Method Investment Activity, Net of Tax` | `SEPARATE_NET_OF_TAX` | $554m loss versus $97.311bn candidate; quantified, about 0.57% |

### Micron — stable separate net-of-tax presentation

Each Consolidated Statement of Operations places `Equity in net income (loss)
of equity method investees` after the income-tax provision. The exact line is
separately quantified in every accession. The segment note's statement that
equity-method gains/losses, other non-operating items, and taxes are not
allocated to segments does not conflict with this consolidated presentation.

| Report date | Annual period | Accession and SEC evidence | Classification | Quantitative evidence |
|---|---|---|---|---|
| 2021-09-02 | 2020-09-04 → 2021-09-02 | `0000723125-21-000065` — [10-K](https://www.sec.gov/Archives/edgar/data/723125/000072312521000065/mu-20210902.htm), Consolidated Statements of Operations, line `Equity in net income (loss) of equity method investees` | `SEPARATE_NET_OF_TAX` | $37m income versus $6.218bn candidate; about 0.60% |
| 2022-09-01 | 2021-09-03 → 2022-09-01 | `0000723125-22-000048` — [10-K](https://www.sec.gov/Archives/edgar/data/723125/000072312522000048/mu-20220901.htm), same statement and line | `SEPARATE_NET_OF_TAX` | $4m income versus $9.571bn; below 0.1% |
| 2023-08-31 | 2022-09-02 → 2023-08-31 | `0000723125-23-000054` — [10-K](https://www.sec.gov/Archives/edgar/data/723125/000072312523000054/mu-20230831.htm), same statement and line | `SEPARATE_NET_OF_TAX` | $2m income versus $(5.658)bn; below 0.1% in magnitude |
| 2024-08-29 | 2023-09-01 → 2024-08-29 | `0000723125-24-000027` — [10-K](https://www.sec.gov/Archives/edgar/data/723125/000072312524000027/mu-20240829.htm), same statement and line | `SEPARATE_NET_OF_TAX` | $11m loss versus $1.240bn; about 0.89% |
| 2025-08-28 | 2024-08-30 → 2025-08-28 | `0000723125-25-000028` — [10-K](https://www.sec.gov/Archives/edgar/data/723125/000072312525000028/mu-20250828.htm), same statement and line | `SEPARATE_NET_OF_TAX` | $9m income versus $9.654bn; below 0.1% |

### Mastercard — stable inclusion in Pretax

In Note 1, Summary of Significant Accounting Policies, under Investments,
each accession says Mastercard's share of net earnings/losses and basis
amortization for equity-method investees “is included in other income
(expense), net” on the Consolidated Statement of Operations. That statement
line precedes and contributes to `Income before income taxes`. The filing also
places flow-through equity-method results in `gains (losses) on equity
investments, net`, another component of pretax earnings. This is direct
`INCLUDED_PRETAX` evidence; it is not merely continuity across the later tag
transition.

| Report date | Annual period | Accession and SEC evidence | Classification | Quantitative evidence |
|---|---|---|---|---|
| 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001141391-22-000023` — [10-K](https://www.sec.gov/Archives/edgar/data/1141391/000114139122000023/ma-20211231.htm), Note 1, Investments — Equity method; Consolidated Statement of Operations | `INCLUDED_PRETAX` | Complete equity-method result not isolated; materiality unresolved |
| 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001141391-23-000020` — [10-K](https://www.sec.gov/Archives/edgar/data/1141391/000114139123000020/ma-20221231.htm), same note subsection and statement | `INCLUDED_PRETAX` | Complete equity-method result not isolated; materiality unresolved |
| 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001141391-24-000022` — [10-K](https://www.sec.gov/Archives/edgar/data/1141391/000114139124000022/ma-20231231.htm), same note subsection and statement | `INCLUDED_PRETAX` | Complete equity-method result not isolated; materiality unresolved |

### Chevron — stable inclusion in Pretax

Note 15, Investments and Advances, reports equity-affiliate earnings and taxes.
The 2022–2025 accessions state that Chevron's affiliate net income “is recorded
in the company's before-tax consolidated earnings.” The 2021 accession states
that equity in earnings is shown in the note and that, for affiliates whose
tax Chevron pays directly, those taxes are reported as `Income tax expense` on
the Consolidated Statement of Income. Together with the same filing's
affiliate-earnings table, that directly places the affiliate earnings before
the consolidated tax line. This is not inferred from the candidate tag.

| Report date | Annual period | Accession and SEC evidence | Classification | Quantitative evidence |
|---|---|---|---|---|
| 2021-12-31 | 2021-01-01 → 2021-12-31 | `0000093410-22-000019` — [10-K](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/cvx-20211231.htm), Note 15 `Investments and Advances`, equity-in-earnings table and tax-location paragraph | `INCLUDED_PRETAX` | $5.657bn affiliate income versus $21.639bn candidate; quantitatively material |
| 2022-12-31 | 2022-01-01 → 2022-12-31 | `0000093410-23-000009` — [10-K](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/cvx-20221231.htm), Note 15 table footnote and Consolidated Statement of Income | `INCLUDED_PRETAX` | $8.585bn versus $49.674bn; quantitatively material |
| 2023-12-31 | 2023-01-01 → 2023-12-31 | `0000093410-24-000013` — [10-K](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/cvx-20231231.htm), same note/table footnote and statement | `INCLUDED_PRETAX` | $5.131bn versus $29.584bn; quantitatively material |
| 2024-12-31 | 2024-01-01 → 2024-12-31 | `0000093410-25-000009` — [10-K](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/cvx-20241231.htm), same note/table footnote and statement | `INCLUDED_PRETAX` | $4.596bn versus $27.506bn; quantitatively material |
| 2025-12-31 | 2025-01-01 → 2025-12-31 | `0000093410-26-000078` — [10-K](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/cvx-20251231.htm), same note/table footnote and statement | `INCLUDED_PRETAX` | $3.000bn versus $19.743bn; quantitatively material |

### Caterpillar — stable separate net-of-tax presentation

Statement 1, Consolidated Results of Operations, places `Equity in profit
(loss) of unconsolidated affiliated companies` after the provision for income
taxes and after profit of consolidated companies. Note 1, Basis of
Consolidation, states that qualifying noncontrolled investments are accounted
for by the equity method. The identified equity line is therefore direct
`SEPARATE_NET_OF_TAX` evidence in each accession.

| Report date | Annual period | Accession and SEC evidence | Classification | Quantitative evidence |
|---|---|---|---|---|
| 2021-12-31 | 2021-01-01 → 2021-12-31 | `0000018230-22-000050` — [10-K](https://www.sec.gov/Archives/edgar/data/18230/000001823022000050/cat-20211231.htm), Statement 1 and Note 1, Basis of Consolidation | `SEPARATE_NET_OF_TAX` | $31m versus $8.204bn candidate; about 0.38% |
| 2022-12-31 | 2022-01-01 → 2022-12-31 | `0000018230-23-000011` — [10-K](https://www.sec.gov/Archives/edgar/data/18230/000001823023000011/cat-20221231.htm), same statement and note | `SEPARATE_NET_OF_TAX` | $19m versus $8.752bn; about 0.22% |
| 2023-12-31 | 2023-01-01 → 2023-12-31 | `0000018230-24-000009` — [10-K](https://www.sec.gov/Archives/edgar/data/18230/000001823024000009/cat-20231231.htm), same statement and note | `SEPARATE_NET_OF_TAX` | $63m versus $13.050bn; about 0.48% |
| 2024-12-31 | 2024-01-01 → 2024-12-31 | `0000018230-25-000008` — [10-K](https://www.sec.gov/Archives/edgar/data/18230/000001823025000008/cat-20241231.htm), same statement and note | `SEPARATE_NET_OF_TAX` | $44m versus $13.373bn; about 0.33% |
| 2025-12-31 | 2025-01-01 → 2025-12-31 | `0000018230-26-000008` — [10-K](https://www.sec.gov/Archives/edgar/data/18230/000001823026000008/cat-20251231.htm), same statement and note | `SEPARATE_NET_OF_TAX` | $109m versus $11.541bn; about 0.94% |

### Philip Morris International — stable separate net-of-tax presentation

The Consolidated Statements of Earnings place `Equity investments and
securities (income)/loss, net` after `Earnings before income taxes` and the
income-tax provision, immediately before net earnings. The
Related Parties — Equity Investments and Other note (Note 4 in 2021, Note 6 in
2022–2024, and Note 5 in 2025) identifies
the equity-method investments and says identifiable basis-difference
amortization is included in that statement line. Exact filings also bind
specific equity-method events to the same line, including the 2021 investee
ownership-dilution income and the 2025 equity-method impairment. The 2025
filing expressly calls the latter a $146 million after-tax charge. The combined
line also contains non-equity-method securities activity, so its total cannot
be treated as pure equity-method activity. This is direct
`SEPARATE_NET_OF_TAX` evidence, not candidate equivalence.

| Report date | Annual period | Accession and SEC evidence | Classification | Quantitative evidence |
|---|---|---|---|---|
| 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001413329-22-000011` — [10-K](https://www.sec.gov/Archives/edgar/data/1413329/000141332922000011/pm-20211231.htm), Consolidated Statements of Earnings; Note 4; MD&A `Equity investee ownership dilution` | `SEPARATE_NET_OF_TAX` | Combined line reports $149m income; at least $55m investee-dilution income identified, but complete equity-method activity is not isolated |
| 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001413329-23-000025` — [10-K](https://www.sec.gov/Archives/edgar/data/1413329/000141332923000025/pm-20221231.htm), statement and Note 6, `Equity Method Investments` | `SEPARATE_NET_OF_TAX` | Combined line reports $137m income; equity-method portion and materiality are unresolved |
| 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001413329-24-000013` — [10-K](https://www.sec.gov/Archives/edgar/data/1413329/000141332924000013/pm-20231231.htm), statement and Note 6, `Equity Method Investments` | `SEPARATE_NET_OF_TAX` | Combined line reports $157m income; equity-method portion and materiality are unresolved |
| 2024-12-31 | 2024-01-01 → 2024-12-31 | `0001413329-25-000013` — [10-K](https://www.sec.gov/Archives/edgar/data/1413329/000141332925000013/pm-20241231.htm), statement and Note 6, `Equity Method Investments` | `SEPARATE_NET_OF_TAX` | Combined line reports $637m income; the separate $2.316bn RBH ASC 321 impairment is not equity-method activity |
| 2025-12-31 | 2025-01-01 → 2025-12-31 | `0001628280-26-005939` — [10-K](https://www.sec.gov/Archives/edgar/data/1413329/000162828026005939/pm-20251231.htm), statement and Note 5, `Equity Method Investments`; MD&A `Impairment of Wellness business related equity investment` | `SEPARATE_NET_OF_TAX` | $146m after-tax equity-method impairment identified within $705m combined income; complete activity is not isolated |

### Linde — stable mixed treatment; unresolved as one classification

Each Consolidated Statement of Income labels the candidate amount `Income
Before Income Taxes and Equity Investments` and separately presents `Income
from equity investments` after the income-tax line. Note 1, Summary of
Significant Accounting Policies, under Equity Investments, directly states
that corporate-investee income is reported after tax, while pretax income from
partnership and LLC investees is included in `Other income (expenses) — net`
with related taxes in `Income taxes`. The candidate therefore excludes one
equity-method population but includes another. Selecting either
`SEPARATE_NET_OF_TAX` or `INCLUDED_PRETAX` for all equity-method activity would
discard direct conflicting evidence, so every period remains `UNRESOLVED`.

| Report date | Annual period | Accession and SEC evidence | Classification | Quantitative evidence |
|---|---|---|---|---|
| 2021-12-31 | 2021-01-01 → 2021-12-31 | `0001628280-22-004180` — [10-K](https://www.sec.gov/Archives/edgar/data/1707925/000162828022004180/lin-20211231.htm), Consolidated Statement of Income and Note 1, `Equity Investments` | `UNRESOLVED` | $119m separate after-tax line is quantified; included partnership/LLC component is not isolated |
| 2022-12-31 | 2022-01-01 → 2022-12-31 | `0001628280-23-005434` — [10-K](https://www.sec.gov/Archives/edgar/data/1707925/000162828023005434/lin-20221231.htm), same statement and note | `UNRESOLVED` | $172m separate line; included component not isolated |
| 2023-12-31 | 2023-01-01 → 2023-12-31 | `0001628280-24-007424` — [10-K](https://www.sec.gov/Archives/edgar/data/1707925/000162828024007424/lin-20231231.htm), same statement and note | `UNRESOLVED` | $167m separate line; included component not isolated |
| 2024-12-31 | 2024-01-01 → 2024-12-31 | `0001628280-25-007990` — [10-K](https://www.sec.gov/Archives/edgar/data/1707925/000162828025007990/lin-20241231.htm), same statement and note | `UNRESOLVED` | $170m separate line; included component not isolated |
| 2025-12-31 | 2025-01-01 → 2025-12-31 | `0001628280-26-011430` — [10-K](https://www.sec.gov/Archives/edgar/data/1707925/000162828026011430/lin-20251231.htm), same statement and note | `UNRESOLVED` | $150m separate line; included component not isolated |

## Issuer-level stability matrix

| Issuer | Periods | Exact-period result | Stability | Pattern decision |
|---|---:|---|---|---|
| AMZN | 5 | 5 `SEPARATE_NET_OF_TAX` | Stable statement line and policy wording | Economically non-equivalent to the current primitive; reject candidate as an unconditional fallback |
| MU | 5 | 5 `SEPARATE_NET_OF_TAX` | Stable statement line | Economically non-equivalent; reject candidate as an unconditional fallback |
| MA | 3 | 3 `INCLUDED_PRETAX` | Stable note-to-statement binding; tag transition is not the evidence | Issuer-specific evidence potentially suitable for later production design |
| CVX | 5 | 5 `INCLUDED_PRETAX` | Stable; explicit before-tax wording in 2022–2025 and equivalent direct tax-location evidence in 2021 | Issuer-specific evidence potentially suitable for later production design |
| CAT | 5 | 5 `SEPARATE_NET_OF_TAX` | Stable statement line and consolidation policy | Economically non-equivalent; reject candidate as an unconditional fallback |
| PM | 5 | 5 `SEPARATE_NET_OF_TAX` | Stable combined after-tax line and note binding | Economically non-equivalent; combined-line contamination must be preserved |
| LIN | 5 | 5 `UNRESOLVED` | Stable mixed legal-form treatment | Contradicted as a single all-equity-method classification and economically non-equivalent without a complete split |

## Conflicts and economic-equivalence conclusions

- The same standard candidate participates in three different economics:
  separate after-tax activity, inclusion in Pretax, and Linde's mixed treatment.
  The concept is therefore not a generic semantic alias for the current
  equity-method-inclusive Pretax primitive.
- `INCLUDED_PRETAX` is established manually for MA and CVX, but by
  issuer-specific prose and statement-line bindings. No structured field in the
  existing diagnostic encodes those relationships.
- MA's later tag transition corroborates continuous visible presentation but
  does not prove scope. The investment accounting policy does.
- PM's after-tax line combines equity-method and non-equity-method securities
  effects; its total cannot be treated as pure equity-method activity.
- LIN directly contradicts a binary issuer-wide rule: corporate equity income
  is after tax, while partnership/LLC equity income enters Pretax.
- No period qualifies as `NO_MATERIAL_ACTIVITY_FOUND`; every issuer discloses
  equity-method activity or policy, and silence was never converted to absence.

Accordingly, **no deterministic, machine-checkable economic-equivalence rule
was established**. The exact economic-equivalence candidate count is 8, but
the exact safe new production-resolution count is **0**. Production Pretax
remains 159 resolved / 45 missing / 0 ambiguous.

## Wave 11 disposition

The separately reviewed design is recorded in
[`pretax-scope-evidence-design.md`](pretax-scope-evidence-design.md). It rejects
an automated structured-evidence rule because no non-circular structured signal
separates the eight positives from all 25 controls. It finds a curated,
immutable exact-accession policy methodologically acceptable only as
deterministic execution of these manual filing conclusions, with versioned
reviewed-evidence provenance and missing-by-default future/amended filings.
Wave 11 does not implement that policy; all 33 remain production missing.

## Recommended next milestone

The smallest next milestone is implementation and focused validation of the
reviewed curated-policy foundation for the eight exact MA/CVX accessions. It
must not add a generic concept fallback or extrapolate beyond the reviewed
entries, and all 25 controls must remain missing.
