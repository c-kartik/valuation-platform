# Pretax Income concept-variant research

## Scope and decision

Phase 1H.4 Wave 7 investigates the 45 Pretax Income results that remain typed
missing after authoritative annual-period integration. The research uses the
selected 10-K accession, its resolved DEI annual period, Company Facts, and
selected-filing XBRL. It does not change production policy.

The decision is **PARTIAL GO FOR FURTHER RESEARCH/DESIGN ONLY**. One recurring
standard concept is a structurally eligible research candidate in 33 periods,
but it is not approved for normalization. Its taxonomy definition differs from
the current concept in equity-method scope, and being the issuer's reported
income-tax denominator does not prove equivalence to the current Pretax
primitive. Current filing-XBRL tooling cannot machine-check the required
presentation and scope evidence. Implementation and every fallback-precedence
change remain blocked. Issuer extensions and domestic/foreign components also
remain unapproved.

Independent review confirmed this classification and found no basis for a
production fallback from numerical equality, tax-denominator status, or
primary-statement placement alone.

## Current production policy

`PRETAX_INCOME_POLICY` has one candidate:

`us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`

The generic annual resolver requires the exact selected 10-K accession, a
`CURRENT` `DURATION` observation ending on the filing report date, numeric
non-Boolean value, and exact `USD`. When the supplied annual-period result is
resolved, Pretax candidates must match its actual `(start, end)` exactly. A
missing configured or structurally eligible observation remains typed missing.
Multiple eligible periods or observations remain ambiguous; equal approved
concepts may confirm, while differing approved concepts conflict. Pretax has no
filing-XBRL fallback. Filing XBRL supplies annual-period evidence only.

## Missing-period inventory

Every row below is a current production `MissingHistoricalMetric`. Values are
reported SEC values, not normalized results. `Standard variant` means the
recurring standard concept discussed below. `Issuer extension` means exact,
dimensionless selected-instance evidence outside Company Facts. All listed
facts match the Wave 6 annual period and use USD.

| Issuer | Report date | Selected accession | Annual period `(start, end)` | Evidence | Value (USD) | Statement/presentation | Provenance |
|---|---|---|---|---|---:|---|---|
| AMZN | 2021-12-31 | `0001018724-22-000005` | 2021-01-01 → 2021-12-31 | standard equity-method-scope variant | 38,151,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| AMZN | 2022-12-31 | `0001018724-23-000004` | 2022-01-01 → 2022-12-31 | standard equity-method-scope variant | -5,936,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| AMZN | 2023-12-31 | `0001018724-24-000008` | 2023-01-01 → 2023-12-31 | standard equity-method-scope variant | 37,557,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| AMZN | 2024-12-31 | `0001018724-25-000004` | 2024-01-01 → 2024-12-31 | standard equity-method-scope variant | 68,614,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| AMZN | 2025-12-31 | `0001018724-26-000004` | 2025-01-01 → 2025-12-31 | standard equity-method-scope variant | 97,311,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MU | 2021-09-02 | `0000723125-21-000065` | 2020-09-04 → 2021-09-02 | standard equity-method-scope variant | 6,218,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MU | 2022-09-01 | `0000723125-22-000048` | 2021-09-03 → 2022-09-01 | standard equity-method-scope variant | 9,571,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MU | 2023-08-31 | `0000723125-23-000054` | 2022-09-02 → 2023-08-31 | standard equity-method-scope variant | -5,658,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MU | 2024-08-29 | `0000723125-24-000027` | 2023-09-01 → 2024-08-29 | standard equity-method-scope variant | 1,240,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MU | 2025-08-28 | `0000723125-25-000028` | 2024-08-30 → 2025-08-28 | standard equity-method-scope variant | 9,654,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MA | 2021-12-31 | `0001141391-22-000023` | 2021-01-01 → 2021-12-31 | standard equity-method-scope variant | 10,307,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MA | 2022-12-31 | `0001141391-23-000020` | 2022-01-01 → 2022-12-31 | standard equity-method-scope variant | 11,732,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MA | 2023-12-31 | `0001141391-24-000022` | 2023-01-01 → 2023-12-31 | standard equity-method-scope variant | 13,639,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CVX | 2021-12-31 | `0000093410-22-000019` | 2021-01-01 → 2021-12-31 | standard equity-method-scope variant | 21,639,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CVX | 2022-12-31 | `0000093410-23-000009` | 2022-01-01 → 2022-12-31 | standard equity-method-scope variant | 49,674,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CVX | 2023-12-31 | `0000093410-24-000013` | 2023-01-01 → 2023-12-31 | standard equity-method-scope variant | 29,584,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CVX | 2024-12-31 | `0000093410-25-000009` | 2024-01-01 → 2024-12-31 | standard equity-method-scope variant | 27,506,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CVX | 2025-12-31 | `0000093410-26-000078` | 2025-01-01 → 2025-12-31 | standard equity-method-scope variant | 19,743,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CAT | 2021-12-31 | `0000018230-22-000050` | 2021-01-01 → 2021-12-31 | standard equity-method-scope variant | 8,204,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CAT | 2022-12-31 | `0000018230-23-000011` | 2022-01-01 → 2022-12-31 | standard equity-method-scope variant | 8,752,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CAT | 2023-12-31 | `0000018230-24-000009` | 2023-01-01 → 2023-12-31 | standard equity-method-scope variant | 13,050,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CAT | 2024-12-31 | `0000018230-25-000008` | 2024-01-01 → 2024-12-31 | standard equity-method-scope variant | 13,373,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| CAT | 2025-12-31 | `0000018230-26-000008` | 2025-01-01 → 2025-12-31 | standard equity-method-scope variant | 11,541,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| PG | 2022-06-30 | `0000080424-22-000064` | 2021-07-01 → 2022-06-30 | issuer extension `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | 17,995,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| PG | 2023-06-30 | `0000080424-23-000073` | 2022-07-01 → 2023-06-30 | issuer extension `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | 18,353,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| PM | 2021-12-31 | `0001413329-22-000011` | 2021-01-01 → 2021-12-31 | standard equity-method-scope variant | 12,232,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| PM | 2022-12-31 | `0001413329-23-000025` | 2022-01-01 → 2022-12-31 | standard equity-method-scope variant | 11,634,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| PM | 2023-12-31 | `0001413329-24-000013` | 2023-01-01 → 2023-12-31 | standard equity-method-scope variant | 10,450,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| PM | 2024-12-31 | `0001413329-25-000013` | 2024-01-01 → 2024-12-31 | standard equity-method-scope variant | 12,199,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| PM | 2025-12-31 | `0001628280-26-005939` | 2025-01-01 → 2025-12-31 | standard equity-method-scope variant | 13,880,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| ORCL | 2022-05-31 | `0001564590-22-023675` | 2021-06-01 → 2022-05-31 | issuer extensions (two equal Pretax facts) | 7,649,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| ORCL | 2023-05-31 | `0000950170-23-028914` | 2022-06-01 → 2023-05-31 | issuer extensions (two equal Pretax facts) | 9,126,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| ORCL | 2024-05-31 | `0000950170-24-075605` | 2023-06-01 → 2024-05-31 | issuer extensions (two equal Pretax facts) | 11,741,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| ORCL | 2025-05-31 | `0000950170-25-087926` | 2024-06-01 → 2025-05-31 | issuer extensions (two equal Pretax facts) | 14,160,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| ORCL | 2026-05-31 | `0001193125-26-277521` | 2025-06-01 → 2026-05-31 | issuer extensions (two equal Pretax facts) | 19,554,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| LIN | 2021-12-31 | `0001628280-22-004180` | 2021-01-01 → 2021-12-31 | standard equity-method-scope variant | 5,099,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| LIN | 2022-12-31 | `0001628280-23-005434` | 2022-01-01 → 2022-12-31 | standard equity-method-scope variant | 5,543,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| LIN | 2023-12-31 | `0001628280-24-007424` | 2023-01-01 → 2023-12-31 | standard equity-method-scope variant | 7,988,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| LIN | 2024-12-31 | `0001628280-25-007990` | 2024-01-01 → 2024-12-31 | standard equity-method-scope variant | 8,569,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| LIN | 2025-12-31 | `0001628280-26-011430` | 2025-01-01 → 2025-12-31 | standard equity-method-scope variant | 8,897,000,000 | Company Facts label: Income (Loss) from Continuing Operations before Equity Method Investments, Income Taxes, Noncontrolling Interest | Company Facts, selected accession |
| MCD | 2021-12-31 | `0000063908-22-000011` | 2021-01-01 → 2021-12-31 | issuer extension `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | 9,127,900,000 | Income/Earnings before income taxes | selected-filing XBRL |
| MCD | 2022-12-31 | `0000063908-23-000012` | 2022-01-01 → 2022-12-31 | issuer extension `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | 7,825,400,000 | Income/Earnings before income taxes | selected-filing XBRL |
| MCD | 2023-12-31 | `0000063908-24-000072` | 2023-01-01 → 2023-12-31 | issuer extension `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | 10,522,200,000 | Income/Earnings before income taxes | selected-filing XBRL |
| MCD | 2024-12-31 | `0000063908-25-000012` | 2024-01-01 → 2024-12-31 | issuer extension `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | 10,345,000,000 | Income/Earnings before income taxes | selected-filing XBRL |
| MCD | 2025-12-31 | `0000063908-26-000035` | 2025-01-01 → 2025-12-31 | issuer extension `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` | 10,897,000,000 | Income/Earnings before income taxes | selected-filing XBRL |

The inventory reconciles to 45 periods: AMZN 5, MU 5, MA 3, CVX 5, CAT 5,
PG 2, PM 5, ORCL 5, LIN 5, and MCD 5. No absence is interpreted as economic
zero.

## Standard-concept inventory

| Concept | Issuers | Issuer-periods | Exact annual matches | Equal coexistence with current concept | Differing coexistence | Classification | Rationale |
|---|---:|---:|---:|---:|---:|---|---|
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | 4 representative clean issuers | 20 inspected clean periods | 20 | n/a | n/a | `APPROVED_EQUIVALENT` | Existing approved primitive; the broader corpus has 159 resolved Pretax periods after Wave 6. |
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments` | 7 | 33 | 33 | 0 in the 65 inspected missing/clean periods | 0 in the 65 inspected missing/clean periods | `NEEDS_MORE_RESEARCH` | The fact is structurally eligible, but its exclusion of equity-method income/loss prevents approval under the current Pretax definition. Tax-denominator or statement-line status alone is insufficient. |
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic` | 9 | 39 | 39 | not applicable | not applicable | `NOT_EQUIVALENT` | A jurisdiction component, not consolidated Pretax. |
| `IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign` | 9 | 39 | 39 | not applicable | not applicable | `NOT_EQUIVALENT` | A jurisdiction component, not consolidated Pretax. |

No other recurring standard consolidated Pretax concept appeared in the 45
missing periods. Domestic plus foreign sometimes reconstructs a disclosed
total, but that would be a separately reviewed derivation with completeness,
scope, and nonoverlap requirements. Neither component is a direct fallback.

## Taxonomy and economic semantics

The existing concept includes income or loss from equity-method investments in
continuing-operations Pretax. The recurring candidate explicitly measures
continuing-operations income before equity-method investments, income taxes,
and noncontrolling interest. That distinction can be economically material.
Similar statement labels therefore do not establish unconditional taxonomy
equivalence.

Both concepts are before income tax and before allocation to noncontrolling
interests. Noncontrolling-interest attribution occurs below consolidated net
income and does not justify changing the Pretax amount. The legacy
`ExtraordinaryItems` wording in the existing concept name does not authorize
adding a separately disclosed extraordinary or discontinued-operation amount.
The project primitive remains **continuing-operations pretax income**. A
separate discontinued-operation fact must not be folded into it.

The current primitive follows the continuing-operations Pretax scope of the
approved concept, including equity-method income or loss. The recurring
candidate may instead be the issuer's reported income-tax denominator while
excluding separately presented equity-method activity. Those are not
automatically the same economic measure. If the project later chooses the
reported tax denominator as its historical primitive, that would require a
separately reviewed financial-methodology decision; Wave 7 makes no such
change.

Equity-method presentation is the gating issue. An issuer may report
equity-method activity below its tax provision as a net-of-tax line, or may
include affiliate earnings in the consolidated pretax line while separately
disclosing the affiliate's tax. Chevron's filing is a concrete warning that
the recurring tag's taxonomy description and the face-statement presentation
can appear misaligned. The selected filing, not tag frequency or label
similarity, must resolve that question.

## Filing-presentation evidence

- [Amazon 2025 10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm)
  reports `Income before income taxes` of $97.311 billion and a $19.087 billion
  provision, followed by $0.554 billion of equity-method activity, net of tax,
  below the tax line. The recurring standard fact equals the reported tax
  denominator, but the separate equity-method amount proves that tax-denominator
  status does not establish equivalence to the current equity-method-inclusive
  Pretax primitive.
- [Mastercard 2024 10-K](https://www.sec.gov/Archives/edgar/data/1141391/000114139125000011/ma-20241231.htm)
  presents one `Income before income taxes` line across the tag transition:
  $13.639 billion for 2023 under the recurring candidate and $15.254 billion
  for 2024 under the current approved concept. This supports issuer-specific
  continuity and further taxonomy/presentation research. It does not establish
  generic semantic equivalence across issuers or erase the formal equity-method
  distinction.
- [Chevron 2025 10-K](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/cvx-20251231.htm)
  reports `Income (Loss) Before Income Tax Expense` of $19.743 billion and tax
  expense of $7.258 billion. The filing also explains that affiliate net income
  is recorded in before-tax consolidated earnings and discloses affiliate tax.
  The candidate is the primary Pretax line even though its formal concept scope
  excludes equity-method income/loss. Affiliate activity is economically
  material, so primary-statement placement by itself cannot prove equivalence
  to the current primitive.
- [Oracle 2026 10-K](https://www.sec.gov/Archives/edgar/data/1341439/000119312526277521/orcl-20260531.htm)
  reports $19.554 billion before tax, but only issuer-extension facts represent
  the exact line in the selected instance.
- [McDonald's 2025 10-K](https://www.sec.gov/Archives/edgar/data/63908/000006390826000035/mcd-20251231.htm)
  reports $10.897 billion before the income-tax provision through an issuer
  extension.
- [P&G 2023 10-K](https://www.sec.gov/Archives/edgar/data/80424/000008042423000073/pg-20230630.htm)
  reports `Earnings before income taxes` of $18.353 billion through an issuer
  extension. P&G switches to the current standard concept in later selected
  filings.

The inspected technology, payments, energy, consumer, and industrial evidence
supports further presentation research, not a production fallback or universal
semantic alias.

## Equity-method evidence by candidate issuer

Only evidence established during Wave 7 is classified below. Lack of a finding
is `UNRESOLVED`, not evidence of absence.

| Issuer | Candidate periods | Equity-method activity status | Primary-statement Pretax presentation | Evidence summary | Research conclusion |
|---|---:|---|---|---|---|
| AMZN | 5 | Separately presented | Established for the inspected 2025 filing | Candidate is the tax denominator; equity-method activity follows tax as a net-of-tax line | Not equivalent merely because it is the tax denominator |
| MU | 5 | `UNRESOLVED` | Not independently established in Wave 7 | Exact annual Company Facts candidate only | Requires filing presentation and scope research |
| MA | 3 | `UNRESOLVED` | Established across the inspected 2024 filing's comparative columns | The same Pretax line transitions from the candidate to the current concept | Issuer-specific continuity only; generic equivalence unproved |
| CVX | 5 | Included and economically material | Established for the inspected 2025 filing | Affiliate net income enters before-tax consolidated earnings despite the candidate's formal exclusion | Statement placement alone is insufficient; note-level scope evidence is required |
| CAT | 5 | `UNRESOLVED` | Not independently established in Wave 7 | Exact annual Company Facts candidate only | Requires filing presentation and scope research |
| PM | 5 | `UNRESOLVED` | Not independently established in Wave 7 | Exact annual Company Facts candidate only | Requires filing presentation and scope research |
| LIN | 5 | `UNRESOLVED` | Not independently established in Wave 7 | Exact annual Company Facts candidate only | Requires filing presentation and scope research |

## Reported-ETR diagnostic

Tax expense divided by the candidate agrees with the filing's reported-tax
presentation in the representative cases: Amazon 2025 is about 19.61%,
Mastercard 2023 about 17.92%, Chevron 2025 about 36.76%, Oracle 2026 about
12.62%, McDonald's 2025 about 21.42%, and P&G 2023 about 19.70%. This is only a
diagnostic. A plausible ratio cannot override unclear taxonomy scope or choose
between competing concepts.

## Issuer-extension evidence

Twelve periods have no consolidated standard Company Facts candidate:

- Oracle has two selected-instance extension concepts with equal annual values:
  `IncomeLossFromContinuingOperationsIncludingNoncontrollingInterestBeforeIncomeTaxesExtraordinaryItems`
  and
  `IncomeLossFromContinuingOperationsAfterNoncontrollingInterestBeforeIncomeTaxes`.
- McDonald's has the extension local name
  `IncomeLossFromContinuingOperationsBeforeIncomeTaxes` in five periods.
- P&G has that same local name in two periods, then uses the current approved
  standard concept in later periods.

These are `NEEDS_MORE_RESEARCH`. Matching a local name across different issuer
namespaces is not a generic extension-family rule, and Oracle uses a different
family. No issuer hardcode or namespace-agnostic matching is approved.

## Presentation-evidence boundary

Current filing-XBRL tooling preserves instance facts, contexts, units,
dimensions, accession/source identity, and annual-period evidence. It does not
preserve or expose enough presentation structure to prove consolidated income-
statement role, primary-statement placement, statement-column identity,
neighboring-line order, presentation-linkbase role relationships, or inline-
document statement structure. The proposed presentation condition is therefore
not currently machine-checkable.

Research must determine whether presentation linkbases and inline filing
structure can identify the primary consolidated income statement and its fact
membership generically, and whether note-level evidence is necessary to resolve
equity-method scope. No pure evidence object or normalization policy should be
implemented until that boundary is established.

## Future precedence and ambiguity constraints

No fallback precedence change is authorized. If later research independently
establishes equivalent economic scope, the current concept would remain first
because it directly matches the current primitive. Any later precedence must
not depend on frequency, magnitude, SEC response order, or first match. Equal
values may support confirmation only after independent evidence establishes
equivalent economic scope; numerical equality alone is insufficient and may be
coincidental. Differing values remain ambiguity or non-equivalence evidence.

Any future condition must be evaluated for the exact selected 10-K accession
and authoritative annual period. Company Facts presence, primary-statement
placement alone, domestic-plus-foreign arithmetic, numerical equality, and ETR
plausibility are insufficient.

## Coverage and next step

Structural candidate coverage is 33/45 missing periods. These are potential
coverage only, not safe future resolutions. Safe new resolutions today remain
0/45. The other 12 periods remain unresolved filing-XBRL issuer-extension
cases.

The recommended next milestone is **Pretax presentation-evidence
research/design**. It should investigate presentation-linkbase roles,
statement-role identification, generic primary consolidated income-statement
identification, fact placement and membership, note-level equity-method scope,
and the additional presentation metadata filing-XBRL extraction may need. It
must assess all 33 candidate periods before proposing production policy. No
fallback implementation is authorized, and issuer extensions remain outside
that research scope.
