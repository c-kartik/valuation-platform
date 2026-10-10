# Depreciation and amortization concept/component inventory

## Decision and frozen scope

Wave 19 follow-up: the
[scope-evidence design](depreciation-amortization-scope-evidence-design.md)
reviews and approves design acceptance for the five exact Visa candidates.
It rejects generic automated concept equivalence and keeps all 89 other rows
unapproved, not freshly reviewed economic denials. The immutable Wave 18 JSON
and the production-missing flags below remain unchanged. Asset perimeter,
lease/incentive separation, 2025 precision, direct precedence and confirming
occurrence/support provenance are now explicitly designed, not implemented.

Wave 20 [implements and verifies](depreciation-amortization-scope-evidence-design.md#wave-20-implementation-and-verified-results)
only those five curated entries. Current D&A is **115 resolved / 89 missing /
0 ambiguous**. The 94-row JSON remains the immutable Wave 18 missing-period
research snapshot, not a current availability report or automatic registry.
All 89 controls remain unapproved and unchanged.

Wave 21 [reviews component completeness](depreciation-amortization-component-derivation-design.md)
for all 33 derivation rows: **0 approved / 19 further research / 14
methodology-blocked** research outcomes. No new equation or production
approval; AMD extensions stay separate. Next is targeted TXN 2021–2023
completeness/expense-scope closure, not implementation.

Phase 1H.4 Wave 18 researches **94 then-missing annual D&A periods across
21 issuers**, not all historical facts or all 204 corpus periods. The frozen
identities come from the saved Phase 1H.3 exact-filing diagnostic plus the four
GEV/SNDK periods enabled by Wave 1A, reconciled to the validated Wave 16 corpus.
The research starts at `1990594ce96dd85f9929b0c312b05509e4692494`.

**PARTIAL GO for a separately reviewed scope-evidence/policy design, not
implementation or a generic fallback.** Five exact Visa periods have supported
potential coverage; 89 remain unresolved for economic completeness, source
selection, lease/impairment/accretion treatment or business scope. All 94 remain
production missing. The 31 occurrences-of-a-combined-concept periods are a
structural research population, not 31 safe resolutions. No derived equation
or new concept policy is approved for production in this milestone.

The [machine-checkable companion inventory](depreciation-amortization-inventory.json)
contains exactly one row per frozen CIK/accession/annual period. It retains all
1,374 matching annual numeric occurrences (including 803 dimensioned facts),
the exact namespace/concept, raw and exact numeric representation, decimals,
nil state, original ordinal, context/entity/dimensions, unit measures,
submitted presentation roles and calculation weights/hrefs, source URLs and
instance hashes. There are no nil occurrences and three non-USD occurrences;
neither dimensioned nor non-USD evidence is eligible for automatic inclusion.
Repeated occurrences and differing values are preserved, not silently collapsed.

## Evidence and machine-checking conventions

Selected filing-XBRL was inspected first. Only the selected cash-flow statement
and the asset/accounting/lease notes needed to establish or question scope were
retrieved subsequently: 320 rendered statements/notes across all 94 filings.
No full test suite, normalization, corpus runner or fresh filing selection was
run. Temporary retrieval artifacts/scripts are outside the repository under
`/tmp/da-wave18`; the committed JSON is research evidence, not application cache
infrastructure or a new production schema.

Each instance was structurally parsed without financial selection. Annuality
uses the exact nondimensional SEC-CIK DEI FY context, DocumentType, fiscal-year
focus and DocumentPeriodEndDate, not calendar length or a D&A duration guessed
from values. The existing resolver confirms 93 periods. AVGO 2021 uses submitted
DEI namespace `http://xbrl.sec.gov/dei/2020-01-31`, outside the existing resolver's
accepted namespace grammar: its four explicit DEI facts and entity/context
independently prove 2020-11-02 through 2021-10-31 in research. Its resolver
`annual_period_not_found` remains recorded; no parser behavior is changed.
All selected annual ends agree with frozen report dates. ORCL's later submitted
linkbases are embedded in its schema and were inspected there; absence of a
separate `_pre.xml` is not absence of presentation evidence.

The lexical inventory includes exact-period concept names containing
`depreci`, `amorti`, `deplet` or `accreti`, including incidental financing,
pension, tax, contract-cost and accumulated-amortization movements. These are
explicit negative-scope evidence, not extra D&A operands. Text blocks were
reviewed in selected notes rather than counted as numeric facts. This is not a
claim that unrelated unnamed Other noncash facts have been reconstructed.

In JSON, `concept_key` is the exact namespace plus local name; namespace is
never discarded when deciding equivalence. `contexts` and `units` are row-local
maps; each ordered occurrence points to them and inherits only the row's source
URL/accession and exact annual dates. `concept_inventory` retains labels,
submitted role definitions, rendered location references and calculation arcs.
An arc documents what the filer sums; it does not prove economic equivalence,
scope, sign, non-overlap or a zero for an absent component. Namespace-qualified
schema hrefs remain available to audit presentation/calculation membership.

## Classifications and coverage

No new root-cause classification is needed. Each period has one primary
**research-routing** category from the existing
[failure taxonomy](universe/sp500-top-50-failure-taxonomy.md#operational-taxonomy):

| Classification | Periods | Meaning in this inventory |
|---|---:|---|
| `CONCEPT_POLICY` | 31 | Exact combined standard concept exists but is not admitted by current policy; economic scope still needs review except the five bounded Visa design candidates. |
| `DERIVATION` | 33 | Separate or independently disaggregatable evidence needs complete/non-overlapping component design; presence or equality is not derivation approval. |
| `ISSUER_EXTENSION` | 5 | AMD's recurring cash-flow/acquisition-extension pattern needs exact-source and changing-composition design. |
| `METHODOLOGY_BLOCKER` | 25 | Mixed impairment/accretion, incomplete amortization, lease/business or continuing-operation scope prevents a defensible current primitive. |
| **Total** | **94** | Categories are mutually exclusive routing totals, not production status changes. |

GE's five rows additionally require specialized industrial/insurance methodology
research as established in [Wave 17](operating-income-cvx-ge-perimeter.md).
That is an economic qualifier, not another five rows or a new specialized skip.
There are no inferred `EXPECTED_TYPED_MISSING` zeros.

## Issuer-level recurring patterns

| Issuer | Missing periods | Primary routing | Findings / boundary |
|---|---:|---|---|
| GOOGL | 5 | METHODOLOGY_BLOCKER (5) | Impairment-combined extensions in 2021/2022; depreciation only thereafter; complete amortization is not established. No zero or impairment residual. |
| AVGO | 5 | DERIVATION (5) | Depreciation plus finite-lived intangible amortization requires exact scope proof. Cash-flow amortization combines intangibles and ROU assets; financing-cost amortization is separate and excluded. |
| TSLA | 5 | METHODOLOGY_BLOCKER (5) | Cash-flow add-back includes impairment. Depreciation, finance-lease amortization and partial intangible evidence do not establish a complete operating-only sum. |
| AMD | 5 | ISSUER_EXTENSION (5) | Cash-flow OtherDepreciationAndAmortization and acquisition-related extensions change composition in 2024/2025 when AdjustmentForAmortization becomes separate. Inventory step-up, lease and financing amounts must not be added as D&A. |
| V | 5 | CONCEPT_POLICY (5) | Combined operating expense and cash-flow D&A; property/equipment/technology and finite-lived intangible notes independently identify the asset perimeter. Incentive amortization is separate, not D&A. |
| INTC | 5 | DERIVATION (5) | Separate depreciation and intangible amortization recur. Verify manufacturing/capitalized inventory, asset costs, grants and lease coverage before a complete additive policy. |
| WMT | 5 | METHODOLOGY_BLOCKER (5) | Accretion-inclusive standard tag and different-precision occurrences. A shorter displayed caption does not remove accretion or authorize selection of the largest or first value. |
| ABBV | 5 | DERIVATION (5) | Separate depreciation and intangible amortization recur; exact cash-flow amortization and rounded note amounts differ. A complete source/occurrence policy and impairment exclusion are required. |
| MA | 5 | CONCEPT_POLICY (5) | Operating statement uses DepreciationAndAmortization, cash flow uses accretion-inclusive tag. PPE/ROU aggregate includes operating-lease amortization and finance leases are embedded in the operating D&A line; do not equate tags solely by equal values. |
| LRCX | 5 | CONCEPT_POLICY (5) | Combined cash-flow D&A recurs; detailed depreciation, software/intangible amortization and finance-lease coverage are not interchangeable. Later intangible effect described as not material is not zero. |
| AMAT | 3 | CONCEPT_POLICY (3) | Combined cash-flow D&A in only the three missing periods. Depreciation and 2023 intangible amortization corroborate components; absent later annual intangible facts do not establish zero. Do not replace the two already resolved periods. |
| MRK | 5 | DERIVATION (5) | Depreciation plus AdjustmentForAmortization is a candidate, not approval; rounded depreciation/intangible note facts differ from precise cash-flow facts. Complete operating/non-overlap and source precision must be proved. |
| GE | 5 | METHODOLOGY_BLOCKER (5) | Accretion-inclusive cash-flow amount and industrial/insurance plus changing continuing/discontinued perimeter. Specialized mixed-business treatment and comparability review are required; do not splice later recasts. |
| PM | 2 | CONCEPT_POLICY (1), DERIVATION (1) | 2021 combined D&A has separately reported depreciation and amortization. 2022 issuer extension includes intangible impairment; independently reported impairment permits further derivation research, not a blanket fallback. |
| TXN | 5 | DERIVATION (5) | Separate depreciation, acquired-intangible amortization and capitalized software amortization. Adding only the first two is incomplete; absence in later years is not zero. Government incentives affect the reported depreciation basis. |
| GEV | 2 | DERIVATION (2) | Separate depreciation and intangible amortization coexist with impairment-inclusive cash-flow tag. Exact sums agree but that does not prove excluded impairment is zero or consolidated continuing scope complete. |
| SNDK | 2 | CONCEPT_POLICY (2) | Combined cash-flow D&A equals reported depreciation. No separate amortization observation does not prove zero; carve-out/spin-off asset basis and complete intangible perimeter require review. |
| ORCL | 5 | DERIVATION (5) | Separate depreciation and intangible amortization recur; do not add accumulated-amortization retirements, financing costs or future amortization. Later filings use embedded schema linkbases. |
| LIN | 5 | CONCEPT_POLICY (5) | Combined operating/cash-flow D&A has submitted positive-weight depreciation plus finite-lived amortization calculation and exact reconciliation. Lease notes expressly embed finance-lease costs; preserving versus adjusting that perimeter remains a policy-design question. |
| IBM | 5 | METHODOLOGY_BLOCKER (5) | Depreciation includes operating-ROU amortization in later cash-flow footnotes; amortization covers software and acquired intangibles, not the separate contract-cost expense. 2021 Kyndryl separation and currency-adjusted versus raw note amounts require scope review. |
| VZ | 5 | CONCEPT_POLICY (5) | Combined operating/cash-flow D&A and separate component notes recur; finance-ROU amortization is explicitly embedded. Contract-cost amortization and debt discounts are separate and must not be added mechanically. |

## Complete 94-period matrix

Every row links directly to the exact selected instance. Counts are
nondimensional/dimensioned **occurrences**, not unique economic amounts. The
concept/value inventory, context IDs, normalized units, labels, statement/note
locations and calculation relationships for that row are in the companion JSON;
they are not replaced by an issuer-level generalization. All rows remain missing.
Annual dates below are authoritative, including non-calendar and 52/53-week years.

| Issuer / CIK | Exact annual start / end | Frozen accession | Occurrences ND / D | Primary classification | Selected filing-XBRL |
|---|---|---|---:|---|---|
| GOOGL / 1652044 | 2021-01-01 / 2021-12-31 | `0001652044-22-000019` | 2 / 4 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1652044/000165204422000019/goog-20211231_htm.xml) |
| GOOGL / 1652044 | 2022-01-01 / 2022-12-31 | `0001652044-23-000016` | 2 / 3 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1652044/000165204423000016/goog-20221231_htm.xml) |
| GOOGL / 1652044 | 2023-01-01 / 2023-12-31 | `0001652044-24-000022` | 1 / 4 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1652044/000165204424000022/goog-20231231_htm.xml) |
| GOOGL / 1652044 | 2024-01-01 / 2024-12-31 | `0001652044-25-000014` | 2 / 2 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000014/goog-20241231_htm.xml) |
| GOOGL / 1652044 | 2025-01-01 / 2025-12-31 | `0001652044-26-000018` | 2 / 2 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231_htm.xml) |
| AVGO / 1730168 | 2020-11-02 / 2021-10-31 | `0001730168-21-000153` | 8 / 2 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016821000153/avgo-20211031_htm.xml) |
| AVGO / 1730168 | 2021-11-01 / 2022-10-30 | `0001730168-22-000118` | 7 / 2 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016822000118/avgo-20221030_htm.xml) |
| AVGO / 1730168 | 2022-10-31 / 2023-10-29 | `0001730168-23-000096` | 7 / 2 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016823000096/avgo-20231029_htm.xml) |
| AVGO / 1730168 | 2023-10-30 / 2024-11-03 | `0001730168-24-000139` | 7 / 2 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016824000139/avgo-20241103_htm.xml) |
| AVGO / 1730168 | 2024-11-04 / 2025-11-02 | `0001730168-25-000121` | 7 / 2 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1730168/000173016825000121/avgo-20251102_htm.xml) |
| TSLA / 1318605 | 2021-01-01 / 2021-12-31 | `0000950170-22-000796` | 6 / 1 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231_htm.xml) |
| TSLA / 1318605 | 2022-01-01 / 2022-12-31 | `0000950170-23-001409` | 3 / 1 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1318605/000095017023001409/tsla-20221231_htm.xml) |
| TSLA / 1318605 | 2023-01-01 / 2023-12-31 | `0001628280-24-002390` | 3 / 1 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1318605/000162828024002390/tsla-20231231_htm.xml) |
| TSLA / 1318605 | 2024-01-01 / 2024-12-31 | `0001628280-25-003063` | 3 / 2 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231_htm.xml) |
| TSLA / 1318605 | 2025-01-01 / 2025-12-31 | `0001628280-26-003952` | 3 / 2 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231_htm.xml) |
| AMD / 2488 | 2020-12-27 / 2021-12-25 | `0000002488-22-000016` | 4 / 2 | `ISSUER_EXTENSION` | [instance](https://www.sec.gov/Archives/edgar/data/2488/000000248822000016/amd-20211225_htm.xml) |
| AMD / 2488 | 2021-12-26 / 2022-12-31 | `0000002488-23-000047` | 7 / 3 | `ISSUER_EXTENSION` | [instance](https://www.sec.gov/Archives/edgar/data/2488/000000248823000047/amd-20221231_htm.xml) |
| AMD / 2488 | 2023-01-01 / 2023-12-30 | `0000002488-24-000012` | 7 / 2 | `ISSUER_EXTENSION` | [instance](https://www.sec.gov/Archives/edgar/data/2488/000000248824000012/amd-20231230_htm.xml) |
| AMD / 2488 | 2023-12-31 / 2024-12-28 | `0000002488-25-000012` | 9 / 1 | `ISSUER_EXTENSION` | [instance](https://www.sec.gov/Archives/edgar/data/2488/000000248825000012/amd-20241228_htm.xml) |
| AMD / 2488 | 2024-12-29 / 2025-12-27 | `0000002488-26-000018` | 7 / 1 | `ISSUER_EXTENSION` | [instance](https://www.sec.gov/Archives/edgar/data/2488/000000248826000018/amd-20251227_htm.xml) |
| V / 1403161 | 2020-10-01 / 2021-09-30 | `0001403161-21-000060` | 6 / 5 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1403161/000140316121000060/v-20210930_htm.xml) |
| V / 1403161 | 2021-10-01 / 2022-09-30 | `0001403161-22-000081` | 6 / 5 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1403161/000140316122000081/v-20220930_htm.xml) |
| V / 1403161 | 2022-10-01 / 2023-09-30 | `0001403161-23-000099` | 6 / 1 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1403161/000140316123000099/v-20230930_htm.xml) |
| V / 1403161 | 2023-10-01 / 2024-09-30 | `0001403161-24-000058` | 6 / 1 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1403161/000140316124000058/v-20240930_htm.xml) |
| V / 1403161 | 2024-10-01 / 2025-09-30 | `0001403161-25-000089` | 6 / 1 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/v-20250930_htm.xml) |
| INTC / 50863 | 2020-12-27 / 2021-12-25 | `0000050863-22-000007` | 4 / 3 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/50863/000005086322000007/intc-20211225_htm.xml) |
| INTC / 50863 | 2021-12-26 / 2022-12-31 | `0000050863-23-000006` | 4 / 4 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/50863/000005086323000006/intc-20221231_htm.xml) |
| INTC / 50863 | 2023-01-01 / 2023-12-30 | `0000050863-24-000010` | 4 / 3 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/50863/000005086324000010/intc-20231230_htm.xml) |
| INTC / 50863 | 2023-12-31 / 2024-12-28 | `0000050863-25-000009` | 4 / 5 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/50863/000005086325000009/intc-20241228_htm.xml) |
| INTC / 50863 | 2024-12-29 / 2025-12-27 | `0000050863-26-000011` | 4 / 4 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/50863/000005086326000011/intc-20251227_htm.xml) |
| WMT / 104169 | 2021-02-01 / 2022-01-31 | `0000104169-22-000012` | 4 / 4 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/104169/000010416922000012/wmt-20220131_htm.xml) |
| WMT / 104169 | 2022-02-01 / 2023-01-31 | `0000104169-23-000020` | 4 / 4 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/104169/000010416923000020/wmt-20230131_htm.xml) |
| WMT / 104169 | 2023-02-01 / 2024-01-31 | `0000104169-24-000056` | 4 / 4 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/104169/000010416924000056/wmt-20240131_htm.xml) |
| WMT / 104169 | 2024-02-01 / 2025-01-31 | `0000104169-25-000021` | 4 / 4 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/104169/000010416925000021/wmt-20250131_htm.xml) |
| WMT / 104169 | 2025-02-01 / 2026-01-31 | `0000104169-26-000055` | 4 / 4 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/104169/000010416926000055/wmt-20260131_htm.xml) |
| ABBV / 1551152 | 2021-01-01 / 2021-12-31 | `0001551152-22-000007` | 4 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115222000007/abbv-20211231_htm.xml) |
| ABBV / 1551152 | 2022-01-01 / 2022-12-31 | `0001551152-23-000011` | 4 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115223000011/abbv-20221231_htm.xml) |
| ABBV / 1551152 | 2023-01-01 / 2023-12-31 | `0001551152-24-000011` | 4 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115224000011/abbv-20231231_htm.xml) |
| ABBV / 1551152 | 2024-01-01 / 2024-12-31 | `0001551152-25-000020` | 4 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115225000020/abbv-20241231_htm.xml) |
| ABBV / 1551152 | 2025-01-01 / 2025-12-31 | `0001551152-26-000008` | 4 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1551152/000155115226000008/abbv-20251231_htm.xml) |
| MA / 1141391 | 2021-01-01 / 2021-12-31 | `0001141391-22-000023` | 6 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1141391/000114139122000023/ma-20211231_htm.xml) |
| MA / 1141391 | 2022-01-01 / 2022-12-31 | `0001141391-23-000020` | 6 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1141391/000114139123000020/ma-20221231_htm.xml) |
| MA / 1141391 | 2023-01-01 / 2023-12-31 | `0001141391-24-000022` | 6 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1141391/000114139124000022/ma-20231231_htm.xml) |
| MA / 1141391 | 2024-01-01 / 2024-12-31 | `0001141391-25-000011` | 6 / 1 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1141391/000114139125000011/ma-20241231_htm.xml) |
| MA / 1141391 | 2025-01-01 / 2025-12-31 | `0001141391-26-000013` | 6 / 1 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1141391/000114139126000013/ma-20251231_htm.xml) |
| LRCX / 707549 | 2021-06-28 / 2022-06-26 | `0000707549-22-000107` | 8 / 0 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/707549/000070754922000107/lrcx-20220626_htm.xml) |
| LRCX / 707549 | 2022-06-27 / 2023-06-25 | `0000707549-23-000102` | 8 / 0 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/707549/000070754923000102/lrcx-20230625_htm.xml) |
| LRCX / 707549 | 2023-06-26 / 2024-06-30 | `0000707549-24-000106` | 8 / 0 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/707549/000070754924000106/lrcx-20240630_htm.xml) |
| LRCX / 707549 | 2024-07-01 / 2025-06-29 | `0000707549-25-000075` | 6 / 0 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/707549/000070754925000075/lrcx-20250629_htm.xml) |
| LRCX / 707549 | 2025-06-30 / 2026-06-28 | `0000707549-26-000037` | 6 / 0 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/707549/000070754926000037/lrcx-20260628_htm.xml) |
| AMAT / 6951 | 2022-10-31 / 2023-10-29 | `0000006951-23-000041` | 6 / 4 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/6951/000000695123000041/amat-20231029_htm.xml) |
| AMAT / 6951 | 2023-10-30 / 2024-10-27 | `0000006951-24-000044` | 3 / 5 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/6951/000000695124000044/amat-20241027_htm.xml) |
| AMAT / 6951 | 2024-10-28 / 2025-10-26 | `0001628280-25-056742` | 3 / 3 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/6951/000162828025056742/amat-20251026_htm.xml) |
| MRK / 310158 | 2021-01-01 / 2021-12-31 | `0000310158-22-000003` | 6 / 20 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000031015822000003/mrk-20211231_htm.xml) |
| MRK / 310158 | 2022-01-01 / 2022-12-31 | `0001628280-23-005061` | 4 / 20 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000162828023005061/mrk-20221231_htm.xml) |
| MRK / 310158 | 2023-01-01 / 2023-12-31 | `0001628280-24-006850` | 6 / 19 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000162828024006850/mrk-20231231_htm.xml) |
| MRK / 310158 | 2024-01-01 / 2024-12-31 | `0001628280-25-007732` | 6 / 19 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000162828025007732/mrk-20241231_htm.xml) |
| MRK / 310158 | 2025-01-01 / 2025-12-31 | `0000310158-26-000063` | 4 / 17 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/310158/000031015826000063/mrk-20251231_htm.xml) |
| GE / 40545 | 2021-01-01 / 2021-12-31 | `0000040545-22-000008` | 5 / 19 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/40545/000004054522000008/ge-20211231_htm.xml) |
| GE / 40545 | 2022-01-01 / 2022-12-31 | `0000040545-23-000023` | 7 / 19 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/40545/000004054523000023/ge-20221231_htm.xml) |
| GE / 40545 | 2023-01-01 / 2023-12-31 | `0000040545-24-000027` | 5 / 17 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/40545/000004054524000027/ge-20231231_htm.xml) |
| GE / 40545 | 2024-01-01 / 2024-12-31 | `0000040545-25-000015` | 6 / 15 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/40545/000004054525000015/ge-20241231_htm.xml) |
| GE / 40545 | 2025-01-01 / 2025-12-31 | `0000040545-26-000008` | 5 / 15 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/40545/000004054526000008/ge-20251231_htm.xml) |
| PM / 1413329 | 2021-01-01 / 2021-12-31 | `0001413329-22-000011` | 5 / 22 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1413329/000141332922000011/pm-20211231_htm.xml) |
| PM / 1413329 | 2022-01-01 / 2022-12-31 | `0001413329-23-000025` | 4 / 25 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1413329/000141332923000025/pm-20221231_htm.xml) |
| TXN / 97476 | 2021-01-01 / 2021-12-31 | `0000097476-22-000009` | 10 / 11 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/97476/000009747622000009/txn-20211231_htm.xml) |
| TXN / 97476 | 2022-01-01 / 2022-12-31 | `0000097476-23-000007` | 10 / 11 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/97476/000009747623000007/txn-20221231_htm.xml) |
| TXN / 97476 | 2023-01-01 / 2023-12-31 | `0000097476-24-000007` | 10 / 11 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/97476/000009747624000007/txn-20231231_htm.xml) |
| TXN / 97476 | 2024-01-01 / 2024-12-31 | `0000097476-25-000007` | 8 / 11 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/97476/000009747625000007/txn-20241231_htm.xml) |
| TXN / 97476 | 2025-01-01 / 2025-12-31 | `0000097476-26-000059` | 6 / 11 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/97476/000009747626000059/txn-20251231_htm.xml) |
| GEV / 1996810 | 2024-01-01 / 2024-12-31 | `0001996810-25-000011` | 5 / 20 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1996810/000199681025000011/gev-20241231_htm.xml) |
| GEV / 1996810 | 2025-01-01 / 2025-12-31 | `0001996810-26-000015` | 5 / 20 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1996810/000199681026000015/gev-20251231_htm.xml) |
| SNDK / 2023554 | 2024-06-29 / 2025-06-27 | `0002023554-25-000034` | 3 / 3 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/2023554/000202355425000034/sndk-20250627_htm.xml) |
| SNDK / 2023554 | 2025-06-28 / 2026-07-03 | `0001628280-26-057406` | 3 / 1 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/2023554/000162828026057406/sndk-20260703_htm.xml) |
| ORCL / 1341439 | 2021-06-01 / 2022-05-31 | `0001564590-22-023675` | 6 / 6 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1341439/000156459022023675/orcl-10k_20220531_htm.xml) |
| ORCL / 1341439 | 2022-06-01 / 2023-05-31 | `0000950170-23-028914` | 6 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1341439/000095017023028914/orcl-20230531_htm.xml) |
| ORCL / 1341439 | 2023-06-01 / 2024-05-31 | `0000950170-24-075605` | 6 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1341439/000095017024075605/orcl-20240531_htm.xml) |
| ORCL / 1341439 | 2024-06-01 / 2025-05-31 | `0000950170-25-087926` | 7 / 8 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1341439/000095017025087926/orcl-20250531_htm.xml) |
| ORCL / 1341439 | 2025-06-01 / 2026-05-31 | `0001193125-26-277521` | 8 / 6 | `DERIVATION` | [instance](https://www.sec.gov/Archives/edgar/data/1341439/000119312526277521/orcl-20260531_htm.xml) |
| LIN / 1707925 | 2021-01-01 / 2021-12-31 | `0001628280-22-004180` | 16 / 26 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1707925/000162828022004180/lin-20211231_htm.xml) |
| LIN / 1707925 | 2022-01-01 / 2022-12-31 | `0001628280-23-005434` | 14 / 24 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1707925/000162828023005434/lin-20221231_htm.xml) |
| LIN / 1707925 | 2023-01-01 / 2023-12-31 | `0001628280-24-007424` | 14 / 24 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1707925/000162828024007424/lin-20231231_htm.xml) |
| LIN / 1707925 | 2024-01-01 / 2024-12-31 | `0001628280-25-007990` | 14 / 25 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1707925/000162828025007990/lin-20241231_htm.xml) |
| LIN / 1707925 | 2025-01-01 / 2025-12-31 | `0001628280-26-011430` | 14 / 25 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/1707925/000162828026011430/lin-20251231_htm.xml) |
| IBM / 51143 | 2021-01-01 / 2021-12-31 | `0001558370-22-001584` | 8 / 21 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000155837022001584/ibm-20211231x10k_htm.xml) |
| IBM / 51143 | 2022-01-01 / 2022-12-31 | `0001558370-23-002376` | 8 / 21 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000155837023002376/ibm-20221231x10k_htm.xml) |
| IBM / 51143 | 2023-01-01 / 2023-12-31 | `0000051143-24-000012` | 9 / 21 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000005114324000012/ibm-20231231_htm.xml) |
| IBM / 51143 | 2024-01-01 / 2024-12-31 | `0000051143-25-000015` | 9 / 22 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000005114325000015/ibm-20241231_htm.xml) |
| IBM / 51143 | 2025-01-01 / 2025-12-31 | `0000051143-26-000010` | 9 / 21 | `METHODOLOGY_BLOCKER` | [instance](https://www.sec.gov/Archives/edgar/data/51143/000005114326000010/ibm-20251231_htm.xml) |
| VZ / 732712 | 2021-01-01 / 2021-12-31 | `0000732712-22-000008` | 7 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/732712/000073271222000008/vz-20211231_htm.xml) |
| VZ / 732712 | 2022-01-01 / 2022-12-31 | `0000732712-23-000012` | 7 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/732712/000073271223000012/vz-20221231_htm.xml) |
| VZ / 732712 | 2023-01-01 / 2023-12-31 | `0000732712-24-000010` | 7 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/732712/000073271224000010/vz-20231231_htm.xml) |
| VZ / 732712 | 2024-01-01 / 2024-12-31 | `0000732712-25-000006` | 7 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/732712/000073271225000006/vz-20241231_htm.xml) |
| VZ / 732712 | 2025-01-01 / 2025-12-31 | `0000732712-26-000007` | 7 / 8 | `CONCEPT_POLICY` | [instance](https://www.sec.gov/Archives/edgar/data/732712/000073271226000007/vz-20251231_htm.xml) |

## Cash-flow add-backs versus the required primitive

The [existing definition](financial-methodology.md#initial-annual-normalization)
is recurring operating PP&E depreciation plus finite-lived intangible
amortization. An indirect cash-flow adjustment is not automatically that amount:
it may cover impairment, accretion, contract/incentive amortization, debt-cost
amortization, lease expense, discontinued activities or amounts excluded from
the operating-income perimeter. Stock compensation and pension/tax adjustments
are not substitutes. Accumulated-amortization retirements, FX movements and
future amortization schedules are not current expense.

- GOOGL 2021/2022 and TSLA/PM 2022 explicitly combine impairment. Neither total
  is a direct equivalent. PM's selected 2022 intangible note separately reports
  amortization 159 million and impairment 112 million, a useful derivation
  research path; do not assume the entire 1,189 million cash-flow amount minus
  112 million is complete D&A until all included scope is independently proved.
- WMT/GE use `DepreciationAmortizationAndAccretionNet`. WMT's exact face and
  rounded narrative values differ; a caption omitting accretion does not remove
  the taxonomy distinction. MA instead has a separate operating-statement
  `DepreciationAndAmortization` fact; equality to the cash-flow broader tag is
  corroboration only, not a generic concept equivalence rule.
- AVGO cash-flow amortization includes intangible and ROU assets, while acquired
  intangible expense is separately split between cost of sales and operating
  expense. Adding those splits to the total double counts. Its financing-cost
  amortization is excluded. AMD changes its split in 2024; acquisition inventory
  step-up is not finite-lived intangible amortization.
- TXN separately reports capitalized-software amortization (including 81 million
  in selected 2025). A two-component MSFT-style rule can omit a genuine third
  component. Reported zero for acquisition amortization in 2022/2023 is retained
  as evidence; absent later observations do not become zero.
- IBM's later cash-flow depreciation includes operating-ROU amortization (the
  selected 2025 statement footnote identifies 0.9 billion). Its separate
  capitalized-contract-cost amortization is not the same as software/acquired
  intangible amortization. Its 2021 total also requires Kyndryl continuing versus
  discontinued scope review. Never substitute currency-adjusted note expense
  for the selected cash-flow operand merely because the names resemble each other.
- Finance-lease amortization is embedded in several reported expenses, including
  MA, LRCX, LIN and VZ; operating-ROU amortization also occurs in some broader
  note aggregates. This wave neither subtracts nor adds lease amounts and does
  not newly declare all embedded finance-lease expense incompatible. Its
  compatibility requires explicit scope/policy design under the existing
  integrated-lease deferral; no isolated adjustment is approved.

## Five bounded Visa design candidates

Visa's exact `us-gaap:DepreciationAndAmortization` amount belongs to both the
consolidated operating statement and cash-flow statement. Submitted calculation
relationships place it in operating costs; selected accounting notes distinguish
property/equipment/technology expense from finite-lived intangible amortization
and separate client-incentive amortization. This is asset/perimeter evidence,
not an approval from local-name resemblance or value matching alone.

| Selected annual end | Reported combined D&A, USD | Property/equipment/technology D&A, USD | Finite-lived amortization, USD | Independent corroboration |
|---|---:|---:|---:|---|
| 2021-09-30 | 804000000 | 721000000 | 83000000 | Exact independent sum |
| 2022-09-30 | 861000000 | 771000000 | 90000000 | Exact independent sum |
| 2023-09-30 | 943000000 | 867000000 | 76000000 | Exact independent sum |
| 2024-09-30 | 1034000000 | 955000000 | 79000000 | Exact independent sum |
| 2025-09-30 | 1220000000 | 1100000000 | 78000000 | 42 million difference; property note rounds to 0.1 billion (decimals -8); within 51 million sum-of-half-units display bound. Not a plug or source-value adjustment. |

The 2021/2022 lease notes explicitly state no finance leases at their annual
ends; later selected notes describe operating leases separately in Other assets.
No absent finance-lease amount is inferred as zero. The independently disclosed
asset-expense split supplies the D&A scope; no operating-lease add-back is used.
For 2025 the exact direct candidate remains 1,220 million, not the sum of its
rounded corroborating notes. The display bound is a research check only, not a
future production rounding gate or general tolerance policy.

**Safe potential design coverage is 5/94 (Visa only); current additional
production coverage is 0.** The remaining 26 combined-concept periods and all
63 other periods remain unresolved. LIN's exact positive-weight decomposition
is particularly promising, but its lease note expressly includes finance-lease
costs in D&A/interest; it is not included in the safe five without the separate
compatibility decision. VZ/MA/LRCX/AMAT/PM/SNDK must not be admitted by extending
Visa's conclusion across issuers or concept names.

## Occurrences, dimensions and conflicts

Every confirming representation remains ordered by its extracted-instance
ordinal. Exact duplicates may eventually confirm only on complete
namespace/concept, normalized CIK, accession, exact period, dimensions, exact
USD and exact Decimal agreement. This research does not collapse the parser's
occurrences. Different dimensions are different scopes, not components that
can automatically be added to a consolidated fact. Different units and nil
states cannot confirm.

ABBV's precise cash-flow amortization and lower-precision note figures differ;
MRK has analogous precise/rounded depreciation and amortization distinctions.
WMT also has materially different raw representations at different decimals.
These are distinct values retained in the evidence, not equal Decimal duplicates.
A future policy must explicitly select reviewed statement occurrences and retain
nonselected note representations; it cannot globally apply a tolerance, round
them into agreement or select by source order. Unexpected differing eligible
facts remain ambiguous. Broken contexts, nil/numeric collisions and inconsistent
source/accession identity remain structural data errors, not coverage.

## Validation and next milestone

The inventory reconciles 94 unique CIK/accession/start/end rows, 21 issuers,
and classification counts 31 + 33 + 5 + 25 = 94. It retains all 1,374 inspected
annual occurrences with exact context/unit links; each filing identity matches
its frozen metadata and authoritative annual DEI evidence. All selected-instance,
submitted artifact and new statement/note URLs were retrieved or read from the
existing SEC evidence cache and checked against their selected directories.
Local documentation links and `git diff --check` pass. No production code,
policy, schema, test or corpus output changes; no tests or corpus reruns.

Production remains D&A **110 resolved / 94 missing / 0 ambiguous**, Operating
Income **194 resolved / 10 missing / 0 ambiguous**, and aggregate **1,880 /
1,508 / 11 / 27 / 42**, totaling **3,468** states. Research categories are not
new standardized states or universe classifications.

Wave 21's [component-completeness design](depreciation-amortization-component-derivation-design.md)
and [33-period matrix](depreciation-amortization-component-derivation-matrix.json)
review all 33 derivation identities without changing this frozen inventory.
**NO-GO for derivation implementation: 0 approved / 19 further research /
14 methodology-blocked** research outcomes; safe new coverage is zero. Known
mixed leases/impairment, software containment, precision distinctions and
manufacturing/grant scope remain gates. The other 61 inventory rows are not
freshly reviewed denials; AMD's five extension periods stay separately gated.
Current production remains Wave 20 D&A **115 / 89 / 0** and aggregate
**1,885 / 1,503 / 11 / 27 / 42 = 3,468**; the Wave 18 counts above are historical.

Next: targeted TXN 2021–2023 completeness/expense-scope closure, not
implementation; preserve the five exact Visa entries and all 89 no-entry controls.
No generic combined-concept fallback, residual, lease adjustment or automatic
scope approval is justified. Component
completeness research for the 33 derivation and five AMD extension periods is a
separate gated workstream, not an automatic generalization of MSFT's two operands.
Forecast/FCFF/DCF remains paused through Phase 1H.6.
