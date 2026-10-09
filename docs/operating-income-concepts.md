# Operating Income concept inventory

## Scope and decision

Phase 1H.4 Wave 13 inventories all 35 Operating Income periods that remain
typed missing after Wave 12: five exact selected 10-Ks each for LLY, JNJ, CVX,
MRK, GE, KLAC, and IBM. The research binds every row to the selected accession,
the filing-XBRL DEI authoritative annual period, the filer-submitted primary
income-statement role, the SEC-rendered face statement, and exact Company Facts
and filing-XBRL observations.

The decision is **NO-GO for a direct concept-policy expansion**:

- none of the 35 face statements reports a consolidated Operating Income,
  Income from Operations, or Operating Profit subtotal;
- none has an exact selected-accession Company Facts observation for
  `us-gaap:OperatingIncomeLoss` or another face-statement Operating Income fact;
- none has an exact annual nondimensional filing-XBRL Operating Income fact;
- GE 2024 and 2025 contain only dimensioned segment and reconciliation
  `us-gaap:OperatingIncomeLoss` facts, which are not a consolidated subtotal;
- expense totals, Pretax Income, gross profit, segment profit, and individual
  expense components are not semantic substitutes for Operating Income; and
- a component derivation might be researchable for 25 LLY/JNJ/MRK/KLAC/IBM
  periods, but completeness, operating scope, sign conventions, and
  non-overlap have not been independently established.

No pattern is `APPROVED_EQUIVALENT`. Safe potential direct coverage is zero,
all 35 production periods remain missing, and `OPERATING_INCOME_POLICY` remains
unchanged.

## Evidence method and field interpretation

For each exact selected filing, the research retrieved the filing directory,
SEC-extracted filing-XBRL instance, filer-submitted schema and presentation
linkbase, Filing Summary, and applicable rendered primary statement. The
existing annual-period resolver supplied the authoritative dates and context.
The submitted role definition—not the renderer alone—establishes that the
reviewed table is a `Statement` role. Renderer evidence supplies the displayed
caption and filing location.

In the inventory below, `None / —` is an affirmative finding that the reviewed
consolidated face statement has no Operating Income subtotal or value. It is
not a zero. Consequently, taxonomy, namespace, concept, unit, numeric value,
raw value, decimals, nil status, and candidate dimensions are all absent. The
listed context ID is the authoritative annual context used to test candidate
facts, not provenance for a nonexistent Operating Income fact. `CF: none`
means Company Facts contains no exact selected-accession annual Operating
Income observation. `FX: required` means filing-XBRL and submitted presentation
evidence were required to establish face-statement absence or exclude
dimensioned facts. Unless explicitly noted for GE, there are no candidate
duplicates, conflicts, dimensioned occurrences, nil facts, or broken context
links because there is no candidate occurrence.

## Complete 35-period inventory

| Issuer | Authoritative annual period | Selected accession | Annual context | Face-statement caption / value | XBRL identity, unit, and scope | Submitted role definition | Evidence result | Classification | Direct SEC evidence |
|---|---|---|---|---|---|---|---|---|---|
| LLY | 2021-01-01 / 2021-12-31 | `0000059478-22-000068` | `i22de8effd1e0473ea9e6b2ebf9fa4dfd_D20210101-20211231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `1001003 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/59478/000005947822000068/) |
| LLY | 2022-01-01 / 2022-12-31 | `0000059478-23-000082` | `i095cf5e171c244d4957ecbd3f0e77a2d_D20220101-20221231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/59478/000005947823000082/) |
| LLY | 2023-01-01 / 2023-12-31 | `0000059478-24-000065` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/59478/000005947824000065/) |
| LLY | 2024-01-01 / 2024-12-31 | `0000059478-25-000067` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/59478/000005947825000067/) |
| LLY | 2025-01-01 / 2025-12-31 | `0000059478-26-000013` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/59478/000005947826000013/) |
| JNJ | 2021-01-04 / 2022-01-02 | `0000200406-22-000022` | `i20918a3d76934ae3867fbaabde676443_D20210104-20220102` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `1003005 - Statement - Consolidated Statements of Earnings` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/200406/000020040622000022/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/200406/000020040622000022/) |
| JNJ | 2022-01-03 / 2023-01-01 | `0000200406-23-000016` | `i0535b75a91b0440fba341aa27ca7ca13_D20220103-20230101` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000005 - Statement - Consolidated Statements of Earnings` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/200406/000020040623000016/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/200406/000020040623000016/) |
| JNJ | 2023-01-02 / 2023-12-31 | `0000200406-24-000013` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000005 - Statement - Consolidated Statements of Earnings` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/200406/000020040624000013/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/200406/000020040624000013/) |
| JNJ | 2024-01-01 / 2024-12-29 | `0000200406-25-000038` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952153 - Statement - Consolidated Statements of Earnings` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/200406/000020040625000038/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/200406/000020040625000038/) |
| JNJ | 2024-12-30 / 2025-12-28 | `0000200406-26-000016` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952153 - Statement - Consolidated Statements of Earnings` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/200406/000020040626000016/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/200406/000020040626000016/) |
| CVX | 2021-01-01 / 2021-12-31 | `0000093410-22-000019` | `idd436c1bb1314e08bd5fd6d1285101ad_D20210101-20211231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `100010003 - Statement - Consolidated Statement of Income` | No consolidated candidate; `OperatingCostsAndExpenses` is the operating-expense line, not income | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/93410/000009341022000019/) |
| CVX | 2022-01-01 / 2022-12-31 | `0000093410-23-000009` | `i3cd5a5d08ac0405882d3e0768d20dc50_D20220101-20221231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - Consolidated Statement of Income` | No consolidated candidate; `OperatingCostsAndExpenses` is the operating-expense line, not income | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/93410/000009341023000009/) |
| CVX | 2023-01-01 / 2023-12-31 | `0000093410-24-000013` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - Consolidated Statement of Income` | No consolidated candidate; `OperatingCostsAndExpenses` is the operating-expense line, not income | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/93410/000009341024000013/) |
| CVX | 2024-01-01 / 2024-12-31 | `0000093410-25-000009` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - Consolidated Statement of Income` | No consolidated candidate; `OperatingCostsAndExpenses` is the operating-expense line, not income | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/93410/000009341025000009/) |
| CVX | 2025-01-01 / 2025-12-31 | `0000093410-26-000078` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - Consolidated Statement of Income` | No consolidated candidate; `OperatingCostsAndExpenses` is the operating-expense line, not income | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/93410/000009341026000078/) |
| MRK | 2021-01-01 / 2021-12-31 | `0000310158-22-000003` | `i090a240c01204951a8d43aeb0084e26c_D20210101-20211231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `100010003 - Statement - Consolidated Statement of Income` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/) |
| MRK | 2022-01-01 / 2022-12-31 | `0001628280-23-005061` | `iaf8fc8dc60ac4ca6b59f2a42ad4a7b23_D20220101-20221231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - Consolidated Statement of Income` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/) |
| MRK | 2023-01-01 / 2023-12-31 | `0001628280-24-006850` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - Consolidated Statement of (Loss) Income` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/310158/000162828024006850/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/310158/000162828024006850/) |
| MRK | 2024-01-01 / 2024-12-31 | `0001628280-25-007732` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - Consolidated Statement of Income` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/310158/000162828025007732/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/310158/000162828025007732/) |
| MRK | 2025-01-01 / 2025-12-31 | `0000310158-26-000063` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - Consolidated Statement of Income` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/310158/000031015826000063/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/310158/000031015826000063/) |
| GE | 2021-01-01 / 2021-12-31 | `0000040545-22-000008` | `i4d33ed7f883a49acab246ac403c05f7e_D20210101-20211231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `100010003 - Statement - STATEMENT OF EARNINGS (LOSS)` | No consolidated or segment `OperatingIncomeLoss` occurrence | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/) |
| GE | 2022-01-01 / 2022-12-31 | `0000040545-23-000023` | `if0cc44b875a84cd3909cdd03262feb78_D20220101-20221231` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - STATEMENT OF EARNINGS (LOSS)` | No consolidated or segment `OperatingIncomeLoss` occurrence | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/) |
| GE | 2023-01-01 / 2023-12-31 | `0000040545-24-000027` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - STATEMENT OF EARNINGS (LOSS)` | No consolidated or segment `OperatingIncomeLoss` occurrence | `NO_REPORTED_OPERATING_INCOME_FOUND` | [statement](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/) |
| GE | 2024-01-01 / 2024-12-31 | `0000040545-25-000015` | `c-1` | None / — | face concept: —; CF: none; FX: `us-gaap:OperatingIncomeLoss`, USD, dimensioned only | `9952151 - Statement - STATEMENT OF EARNINGS (LOSS)` | Four exact annual segment/reconciliation facts; distinct contexts, dimensions, and values; no conflict or duplicate collapse | `NOT_EQUIVALENT` | [statement](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/) |
| GE | 2025-01-01 / 2025-12-31 | `0000040545-26-000008` | `c-1` | None / — | face concept: —; CF: none; FX: `us-gaap:OperatingIncomeLoss`, USD, dimensioned only | `9952151 - Statement - STATEMENT OF OPERATIONS` | Four exact annual segment/reconciliation facts; distinct contexts, dimensions, and values; no conflict or duplicate collapse | `NOT_EQUIVALENT` | [statement](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/) |
| KLAC | 2021-07-01 / 2022-06-30 | `0000319201-22-000023` | `if1b7f5a910c24f34a1eb3d55c6507918_D20210701-20220630` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `100030005 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/319201/000031920122000023/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/319201/000031920122000023/) |
| KLAC | 2022-07-01 / 2023-06-30 | `0000319201-23-000031` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000005 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/319201/000031920123000031/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/319201/000031920123000031/) |
| KLAC | 2023-07-01 / 2024-06-30 | `0000319201-24-000021` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952153 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/319201/000031920124000021/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/319201/000031920124000021/) |
| KLAC | 2024-07-01 / 2025-06-30 | `0000319201-25-000024` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952153 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/319201/000031920125000024/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/319201/000031920125000024/) |
| KLAC | 2025-07-01 / 2026-06-30 | `0000319201-26-000027` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952153 - Statement - Consolidated Statements of Operations` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/319201/000031920126000027/R5.htm) · [filing](https://www.sec.gov/Archives/edgar/data/319201/000031920126000027/) |
| IBM | 2021-01-01 / 2021-12-31 | `0001558370-22-001584` | `Duration_1_1_2021_To_12_31_2021_WlJ6c3zD106iejIq2PdgaQ` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `00100 - Statement - CONSOLIDATED INCOME STATEMENT` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/51143/000155837022001584/R2.htm) · [filing](https://www.sec.gov/Archives/edgar/data/51143/000155837022001584/) |
| IBM | 2022-01-01 / 2022-12-31 | `0001558370-23-002376` | `Duration_1_1_2022_To_12_31_2022_M62iYm1530e69wSMRRzSSg` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `00100 - Statement - CONSOLIDATED INCOME STATEMENT` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/51143/000155837023002376/R2.htm) · [filing](https://www.sec.gov/Archives/edgar/data/51143/000155837023002376/) |
| IBM | 2023-01-01 / 2023-12-31 | `0000051143-24-000012` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `0000003 - Statement - CONSOLIDATED INCOME STATEMENT` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/51143/000005114324000012/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/51143/000005114324000012/) |
| IBM | 2024-01-01 / 2024-12-31 | `0000051143-25-000015` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - CONSOLIDATED INCOME STATEMENT` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/51143/000005114325000015/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/51143/000005114325000015/) |
| IBM | 2025-01-01 / 2025-12-31 | `0000051143-26-000010` | `c-1` | None / — | concept, namespace, unit, value, dimensions: —; CF: none; FX: required | `9952151 - Statement - CONSOLIDATED INCOME STATEMENT` | No candidate occurrence; no duplicate, conflict, dimension, or nil issue | `DERIVATION_RESEARCH_REQUIRED` | [statement](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/R3.htm) · [filing](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/) |

## GE dimensioned Operating Income evidence

GE is the only issuer with exact annual `us-gaap:OperatingIncomeLoss` facts in
these filings, and only in 2024 and 2025. They are USD, non-nil, `decimals=-6`,
and economically distinct rather than duplicates:

| Period | Context | Dimensions | Raw / numeric value (USD) | Decision |
|---|---|---|---:|---|
| 2024 | `c-144` | `ConsolidationItemsAxis=OperatingSegmentsMember`; `StatementBusinessSegmentsAxis=CommercialEnginesAndServicesReportableSegmentMember` | 7,055,000,000 | Segment fact; `NOT_EQUIVALENT` |
| 2024 | `c-147` | `ConsolidationItemsAxis=OperatingSegmentsMember`; `StatementBusinessSegmentsAxis=DefenseAndPropulsionTechnologiesReportableSegmentMember` | 1,061,000,000 | Segment fact; `NOT_EQUIVALENT` |
| 2024 | `c-600` | `ConsolidationItemsAxis=OperatingSegmentsMember` | 8,116,000,000 | Operating-segments aggregate, not consolidated Operating Income; `NOT_EQUIVALENT` |
| 2024 | `c-150` | `ConsolidationItemsAxis=CorporateAndReconcilingItemsMember` | -89,000,000 | Reconciliation member; `NOT_EQUIVALENT` |
| 2025 | `c-132` | `ConsolidationItemsAxis=OperatingSegmentsMember`; `StatementBusinessSegmentsAxis=CommercialEnginesAndServicesReportableSegmentMember` | 8,861,000,000 | Segment fact; `NOT_EQUIVALENT` |
| 2025 | `c-135` | `ConsolidationItemsAxis=OperatingSegmentsMember`; `StatementBusinessSegmentsAxis=DefenseAndPropulsionTechnologiesReportableSegmentMember` | 1,296,000,000 | Segment fact; `NOT_EQUIVALENT` |
| 2025 | `c-636` | `ConsolidationItemsAxis=OperatingSegmentsMember` | 10,157,000,000 | Operating-segments aggregate, not consolidated Operating Income; `NOT_EQUIVALENT` |
| 2025 | `c-138` | `ConsolidationItemsAxis=CorporateAndReconcilingItemsMember` | -96,000,000 | Reconciliation member; `NOT_EQUIVALENT` |

Company Facts contains none of these exact selected-accession observations.
The facts occur in segment evidence, not the submitted consolidated face-
statement role. Adding the two named segment values reproduces the operating-
segments aggregate, while the corporate/reconciling member remains a separate
economic scope. Neither aggregation is silently promoted to consolidated
Operating Income.

## Recurring candidate and component patterns

| Issuer | Periods | Recurring face-statement evidence | Structured pattern | Classification and rationale |
|---|---:|---|---|---|
| LLY | 5 | Revenue, detailed costs, `Other—net, (income) expense`, aggregate `Costs, expenses, and other`, then Pretax | Filing-only issuer extension `CostOfSalesOperatingExpensesAndOtherNet`; USD annual value; no exact Company Facts observation | Aggregate includes other-net and reconciles to Pretax, not Operating Income: `NOT_EQUIVALENT`. Excluding or reclassifying components requires `DERIVATION_RESEARCH_REQUIRED`. |
| JNJ | 5 | Gross profit; SG&A; R&D; IPR&D impairments; interest; other income/expense; restructuring; then Pretax | Recurring standard component facts, but no reported operating subtotal or total-operating-expense fact | No direct candidate. A component equation requires an explicit operating/non-operating perimeter and complete sign/overlap proof: `DERIVATION_RESEARCH_REQUIRED`. |
| CVX | 5 | Total revenues and other income; purchased crude; operating expense; SG&A; exploration; D&A; non-income taxes; interest; benefit costs; then Pretax | `us-gaap:OperatingCostsAndExpenses` is only the captioned operating-expense line; `us-gaap:CostsAndExpenses` includes non-operating deductions | Both are `NOT_EQUIVALENT`. Integrated energy and equity-affiliate presentation provides no reported consolidated Operating Income: `NO_REPORTED_OPERATING_INCOME_FOUND`. |
| MRK | 5 | Sales; cost of sales; SG&A; R&D; restructuring; other income/expense; aggregate costs/other; then Pretax | Filing-only issuer extension `CostsExpensesAndOther`; no exact Company Facts observation | Aggregate explicitly includes non-operating income/expense and produces Pretax, not Operating Income: `NOT_EQUIVALENT`. Component isolation requires `DERIVATION_RESEARCH_REQUIRED`. |
| GE | 5 | Revenue; expenses including interest, insurance, and non-operating benefit cost; other income; then Pretax | No face subtotal. 2024–2025 add dimensioned segment/reconciliation `OperatingIncomeLoss`; 2021–2023 have none | Segment facts are `NOT_EQUIVALENT`; 2021–2023 are `NO_REPORTED_OPERATING_INCOME_FOUND`. A consolidated derivation would require a separately reviewed business/perimeter and reconciliation policy. |
| KLAC | 5 | Revenue and cost/expense lines followed by interest, other income/expense, then Pretax | Recurring standard components in Company Facts and filing-XBRL; no aggregate operating subtotal | Direct candidate absent. Component arithmetic may be testable, but impairment classification, completeness, signs, and non-overlap require `DERIVATION_RESEARCH_REQUIRED`. |
| IBM | 5 | Gross profit; SG&A; R&D; IP/custom-development income; other income/expense; interest; aggregate expense/other; then Pretax | Filing-only `ExpenseAndOtherIncome` / `ExpenseAndIncomeOther` extensions; no exact Company Facts observation | Aggregate includes interest and other income/expense and produces Pretax, not Operating Income: `NOT_EQUIVALENT`. IP and pension/other classifications require `DERIVATION_RESEARCH_REQUIRED`. |

No local-name, label, numerical difference, or statement position converts an
expense aggregate into Operating Income. No component equation is approved by
this inventory.

## Issuer-level conclusions and reconciliation

| Issuer | Periods | Primary period classification | Safe direct coverage | Unresolved |
|---|---:|---|---:|---:|
| LLY | 5 | `DERIVATION_RESEARCH_REQUIRED` | 0 | 5 |
| JNJ | 5 | `DERIVATION_RESEARCH_REQUIRED` | 0 | 5 |
| CVX | 5 | `NO_REPORTED_OPERATING_INCOME_FOUND` | 0 | 5 |
| MRK | 5 | `DERIVATION_RESEARCH_REQUIRED` | 0 | 5 |
| GE | 5 | Three `NO_REPORTED_OPERATING_INCOME_FOUND`; two `NOT_EQUIVALENT` dimensioned-only patterns | 0 | 5 |
| KLAC | 5 | `DERIVATION_RESEARCH_REQUIRED` | 0 | 5 |
| IBM | 5 | `DERIVATION_RESEARCH_REQUIRED` | 0 | 5 |
| **Total** | **35** | **25 derivation-research / 5 no-reported / 3 no-reported GE / 2 not-equivalent GE** | **0** | **35** |

The inventory reconciles exactly seven issuers × five periods. All rows use the
five frozen selected accessions and the authoritative annual start/end dates.
All 35 submitted income-statement roles and renderer links were retrieved and
matched; the filing directory indexes independently contain each linked
statement and filing location. Production remains Operating Income 169 resolved
/ 35 missing / 0 ambiguous and aggregate states remain 1,855 resolved / 1,533
missing / 11 ambiguous / 27 methodology-blocked / 42 not-comparable across
3,468 states.

## Recommended next milestone

The next smallest milestone is **Operating Income derivation-evidence design**,
not implementation. Freeze exact candidate equations for the 25
LLY/JNJ/MRK/KLAC/IBM periods and test each component against the consolidated
face statement, calculation linkbase, taxonomy definition, sign, completeness,
and overlap. The design must decide an explicit GAAP operating perimeter for
acquired IPR&D, restructuring, impairments, IP income, pension components, and
other income/expense before approving any equation. CVX and GE require separate
issuer/business-model perimeter research and must not be forced into the same
derivation. Until that work reaches a reviewed GO decision, all 35 periods
remain typed missing.
