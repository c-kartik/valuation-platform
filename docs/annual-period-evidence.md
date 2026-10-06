# Annual-period evidence

## Decision

Phase 1H.4 Wave 4 reaches **GO — SAFE GENERIC RULE FOUND** for exact Form
10-K filings that provide a valid filing-level XBRL instance. The authoritative
annual period is the duration context that contains the filing's consistent DEI
annual-report facts. This is not an inference from the duration's length or
from the financial facts that happen to use it.

The SEC staff's February 2026 [EDGAR XBRL
Guide](https://www.sec.gov/files/edgar/filer-information/specifications/xbrl-guide-2026-02-17.pdf),
which supports EDGAR validation while the EDGAR Filer Manual and applicable
filing requirements remain controlling, defines the required context as a
dimensionless context whose period end
matches the reporting-period end and whose duration matches the quarter or year
of the submission reporting period. It separately specifies
`DocumentFiscalPeriodFocus=FY` for an annual report and defines
`DocumentPeriodEndDate` as the reporting or transition-period end. Those rules
provide the positive fiscal-year-period identity that Company Facts alone does
not preserve.

This milestone documents the rule. It does not change production selection or
normalization, so the 22 revenue ambiguities and the Wave 2 corpus totals remain
unchanged until a separately reviewed implementation sub-wave.

## Problem

A selected 10-K accession can contain dimensionless current facts for the full
fiscal year, Q4, and other shorter periods, all ending on the selected filing's
report date. Accession, form, Company Facts `fy`/`fp`, report-date end, frame,
duration length, and concept frequency cannot distinguish those economic
periods. Wave 3 correctly rejected a unique diluted-share duration as fiscal-
year authority.

Wave 4 asks a different question: whether filing-level SEC/XBRL structure
positively identifies the annual reporting context. The answer is yes for the
tested exact 10-Ks through the DEI required context.

## Evidence sources

| Source | What it establishes | Limitation | Decision |
|---|---|---|---|
| Company Facts | Accession-linked observations and their economic start/end dates | Does not carry DEI facts, context IDs, presentation roles, or an annual-context designation | Insufficient alone |
| SEC submissions and filing index | Exact form, accession, filing date, report date, and available filing artifacts | Does not expose fiscal-year start | Identity/retrieval support only |
| Extracted filing XBRL instance | Exact DEI facts, context IDs, entity-identifier value, duration dates, dimensions, and fact-to-context linkage; the current parser still needs scheme preservation or validation | Requires one explicit filing-artifact request | **Authoritative input after the identity prerequisite** |
| DEI required context | For an annual report, identifies the dimensionless duration matching the year of the submission reporting period | Must be complete, internally consistent, and unique | **Authoritative rule** |
| Presentation linkbase | Identifies issuer presentation groups and concept order | Relates concepts, not individual facts or contexts; one concept may appear in several roles | Corroboration only |
| Inline XBRL placement | Shows which individual tagged facts occur in primary statements and quarterly/note tables | HTML layout is issuer-authored and is not needed once the DEI context resolves | Audit corroboration |
| SEC-generated `MetaLinks.json` / rendered reports | Classifies reports and records statement anchors with their `contextRef` | SEC-generated derivative whose JSON schema is not the rule's required source | Strong cross-check, not authority |

The existing `sec.filing_xbrl` parser retains filing/company identity, source
URL, retrieval timestamp, context ID, entity-identifier value, start/end,
dimensions, and the DEI facts that reference each context. It does not retain
the entity-identifier `scheme`. Before annual-period resolution is implemented,
the parser must either preserve that scheme explicitly or validate it during
parsing and retain a trusted normalized identity. The resolver must require the
SEC scheme `http://www.sec.gov/CIK` and an identifier value equal to the actual
filing registrant CIK; the value alone is not complete XBRL entity identity.
No presentation-linkbase or Inline HTML parser is otherwise required.

## DEI findings

The official 2025 DEI schema gives all four observed concepts `periodType`
`duration`:

| Concept | Datatype | Meaning and evidentiary value |
|---|---|---|
| `DocumentFiscalYearFocus` | `xbrli:gYearItemType` | Labels the fiscal year in focus. It does not give the start date by itself. |
| `DocumentFiscalPeriodFocus` | `dei:fiscalPeriodItemType` | `FY` identifies an annual report, including its fourth quarter. The value alone does not distinguish full-year facts from Q4 facts elsewhere in the same accession. |
| `DocumentPeriodEndDate` | `xbrli:dateItemType` | Gives the reporting or transition-period end. It does not give the start date by itself. |
| `CurrentFiscalYearEndDate` | `xbrli:gMonthDayItemType` | Gives only `--MM-DD`; the SEC notes that it normally does not change from year to year. It cannot establish a full start date and is supporting metadata only. |

`EntityFiscalYearEnd` is not a concept in the current DEI schema and did not
appear in the tested filings. It must not be treated as an available standard
source.

The authority comes from the context jointly referenced by the first three
facts, not from any one scalar value. In all 42 tested filings, those facts
shared one dimensionless duration context, `DocumentFiscalPeriodFocus` was
`FY`, and `DocumentPeriodEndDate` equaled the selected report date.

## Live corpus

The read-only diagnostic used the production ticker resolver, filing selector,
and filing-XBRL parser on 2026-10-06. It covered 42 selected annual filings for
nine issuers: the requested JNJ, ABBV, GE, ORCL, WMT, COST, and SNDK cases, plus
META as a clean calendar-year control and MSFT as a June-year-end control.

Each row below is the unique dimensionless DEI FY context. The same period was
independently returned by every eligible non-parenthetical duration-statement
anchor in SEC `MetaLinks.json` for that filing.

| Issuer | Report date | Selected accession | DEI annual start | DEI annual end |
|---|---|---|---|---|
| JNJ | 2022-01-02 | `0000200406-22-000022` | 2021-01-04 | 2022-01-02 |
| JNJ | 2023-01-01 | `0000200406-23-000016` | 2022-01-03 | 2023-01-01 |
| JNJ | 2023-12-31 | `0000200406-24-000013` | 2023-01-02 | 2023-12-31 |
| JNJ | 2024-12-29 | `0000200406-25-000038` | 2024-01-01 | 2024-12-29 |
| JNJ | 2025-12-28 | `0000200406-26-000016` | 2024-12-30 | 2025-12-28 |
| ABBV | 2021-12-31 | `0001551152-22-000007` | 2021-01-01 | 2021-12-31 |
| ABBV | 2022-12-31 | `0001551152-23-000011` | 2022-01-01 | 2022-12-31 |
| ABBV | 2023-12-31 | `0001551152-24-000011` | 2023-01-01 | 2023-12-31 |
| ABBV | 2024-12-31 | `0001551152-25-000020` | 2024-01-01 | 2024-12-31 |
| ABBV | 2025-12-31 | `0001551152-26-000008` | 2025-01-01 | 2025-12-31 |
| GE | 2021-12-31 | `0000040545-22-000008` | 2021-01-01 | 2021-12-31 |
| GE | 2022-12-31 | `0000040545-23-000023` | 2022-01-01 | 2022-12-31 |
| GE | 2023-12-31 | `0000040545-24-000027` | 2023-01-01 | 2023-12-31 |
| GE | 2024-12-31 | `0000040545-25-000015` | 2024-01-01 | 2024-12-31 |
| GE | 2025-12-31 | `0000040545-26-000008` | 2025-01-01 | 2025-12-31 |
| ORCL | 2022-05-31 | `0001564590-22-023675` | 2021-06-01 | 2022-05-31 |
| ORCL | 2023-05-31 | `0000950170-23-028914` | 2022-06-01 | 2023-05-31 |
| ORCL | 2024-05-31 | `0000950170-24-075605` | 2023-06-01 | 2024-05-31 |
| ORCL | 2025-05-31 | `0000950170-25-087926` | 2024-06-01 | 2025-05-31 |
| ORCL | 2026-05-31 | `0001193125-26-277521` | 2025-06-01 | 2026-05-31 |
| WMT | 2022-01-31 | `0000104169-22-000012` | 2021-02-01 | 2022-01-31 |
| WMT | 2023-01-31 | `0000104169-23-000020` | 2022-02-01 | 2023-01-31 |
| WMT | 2024-01-31 | `0000104169-24-000056` | 2023-02-01 | 2024-01-31 |
| WMT | 2025-01-31 | `0000104169-25-000021` | 2024-02-01 | 2025-01-31 |
| WMT | 2026-01-31 | `0000104169-26-000055` | 2025-02-01 | 2026-01-31 |
| COST | 2021-08-29 | `0000909832-21-000014` | 2020-08-31 | 2021-08-29 |
| COST | 2022-08-28 | `0000909832-22-000021` | 2021-08-30 | 2022-08-28 |
| COST | 2023-09-03 | `0000909832-23-000042` | 2022-08-29 | 2023-09-03 |
| COST | 2024-09-01 | `0000909832-24-000049` | 2023-09-04 | 2024-09-01 |
| COST | 2025-08-31 | `0000909832-25-000101` | 2024-09-02 | 2025-08-31 |
| SNDK | 2025-06-27 | `0002023554-25-000034` | 2024-06-29 | 2025-06-27 |
| SNDK | 2026-07-03 | `0001628280-26-057406` | 2025-06-28 | 2026-07-03 |
| META | 2021-12-31 | `0001326801-22-000018` | 2021-01-01 | 2021-12-31 |
| META | 2022-12-31 | `0001326801-23-000013` | 2022-01-01 | 2022-12-31 |
| META | 2023-12-31 | `0001326801-24-000012` | 2023-01-01 | 2023-12-31 |
| META | 2024-12-31 | `0001326801-25-000017` | 2024-01-01 | 2024-12-31 |
| META | 2025-12-31 | `0001628280-26-003942` | 2025-01-01 | 2025-12-31 |
| MSFT | 2022-06-30 | `0001564590-22-026876` | 2021-07-01 | 2022-06-30 |
| MSFT | 2023-06-30 | `0000950170-23-035122` | 2022-07-01 | 2023-06-30 |
| MSFT | 2024-06-30 | `0000950170-24-087843` | 2023-07-01 | 2024-06-30 |
| MSFT | 2025-06-30 | `0000950170-25-100235` | 2024-07-01 | 2025-06-30 |
| MSFT | 2026-06-30 | `0001193125-26-323660` | 2025-07-01 | 2026-06-30 |

The COST 2023 context runs from 2022-08-29 through 2023-09-03 and therefore
captures the issuer's 53-week year without assuming a permitted day count. JNJ
and COST demonstrate moving week-based boundaries; WMT, ORCL, and MSFT
demonstrate non-calendar year ends.

## Context and presentation findings

The complete temporary diagnostic enumerated every report-date-ending duration
context, its dimensions, and its fact count. For consolidated annual-period
selection, the relevant dimensionless contexts showed the expected contrast:

| Filing | Annual DEI context | Other report-date-ending dimensionless context(s) | Filing placement |
|---|---|---|---|
| JNJ 2023 | `c-1`, 2023-01-02 to 2023-12-31, 331 facts | `c-269`, 2023-10-02 to 2023-12-31, 19 facts | Annual revenue is on the consolidated earnings statement; Q4 revenue is in selected quarterly information. |
| ABBV 2025 | `c-1`, 2025-01-01 to 2025-12-31, 299 facts | `c-514`, 2025-10-01 to 2025-12-31, 11 facts | Annual statement anchors use `c-1`; Q4 revenue is in quarterly information. |
| GE 2025 | `c-1`, 2025-01-01 to 2025-12-31, 407 facts | `c-424`, 2025-10-01 to 2025-12-31, 5 facts | Annual statement anchors use `c-1`; the shorter context does not anchor a primary statement. |
| ORCL 2026 | `C_24317829-d237-4c29-bae3-2e46dd1ae625`, 2025-06-01 to 2026-05-31, 336 facts | `C_785db112-bb7d-47e2-b27d-5564ac771e38`, 2026-03-01 to 2026-05-31, 4 facts | Annual statement anchors use the DEI context; the shorter context does not. |
| WMT 2026 | `c-1`, 2025-02-01 to 2026-01-31, 286 facts | `c-338`, 2025-11-01 to 2026-01-31, 3 facts | Annual statement anchors use `c-1`; the shorter context contains unrelated disclosure facts. |
| COST 2023 | `c-1`, 2022-08-29 to 2023-09-03, 219 facts | None dimensionless | All eligible duration-statement anchors use the 53-week DEI context. |
| SNDK 2026 | `c-1`, 2025-06-28 to 2026-07-03, 313 facts | `c-303`, 2026-04-04 to 2026-07-03, 2 facts | Annual statement anchors use `c-1`; the shorter context contains unrelated disclosure facts. |

Dimensioned contexts were numerous—between 20 and 260 report-date-ending
duration contexts per filing in this sample—so context frequency and candidate
voting are not meaningful. Dimensions must be preserved and the DEI annual
context must remain dimensionless.

The presentation linkbase cannot independently identify a context because its
relationships order concepts, not individual fact occurrences. Inline XBRL
does preserve the fact-to-context link and visibly separates statement facts
from quarterly tables, but generic HTML table interpretation would add
unnecessary layout fragility. SEC `MetaLinks.json` offered useful corroboration:
for every tested filing, all eligible non-parenthetical duration-statement
anchors ending on the report date resolved to the exact DEI period. The DEI
context remains the simpler authoritative source.

## Rejected standalone signals

None of these may identify the annual period without the DEI required-context
evidence: Form 10-K, Company Facts `fy` or `fp`, frame, report-date end, longest
or earliest duration, majority or most-common duration, a duration near 365
days, 52/53-week length, diluted shares, revenue, operating income, tax, or
cross-concept voting. They may be consistent with the resolved period but do
not prove it.

## Proposed rule

A future pure annual-period resolver should accept an already selected filing
and explicitly supplied `SECFilingXBRL`. It should resolve only when all of the
following hold:

1. Company, accession, and filing metadata match exactly; the selected form is
   exactly `10-K` and has a report date.
2. Non-nil DEI `DocumentFiscalPeriodFocus`, `DocumentFiscalYearFocus`, and
   `DocumentPeriodEndDate` facts occur together in an eligible context.
3. The context has entity scheme `http://www.sec.gov/CIK`, an identifier value
   equal to the actual filing registrant CIK, no dimensions, and a duration
   period. This validates the filing's current registrant only and does not
   infer registrant succession.
4. Fiscal-period focus is exactly `FY`, document-period end equals the selected
   report date, and the context end also equals that report date.
5. Exactly one normalized eligible annual-period evidence tuple survives the
   duplicate and context-equivalence rules below. Raw context ID is provenance,
   not economic identity.

Normalization uses two deterministic keys. The structural semantic-context key
consists of the SEC entity scheme, normalized registrant CIK, start, end, and
normalized dimensions. The normalized eligible evidence tuple extends that key
with the normalized values of the three relevant DEI facts. Dimension ordering
must be normalized deterministically rather than treated as economic meaning;
raw context ID belongs to neither key.

- Repeated occurrences of the same DEI concept with the same normalized value
  in the same normalized semantic context confirm one fact.
- Conflicting values for the same DEI concept in the same semantic context are
  internally inconsistent and produce `ANNUAL_PERIOD_DATA_ERROR`.
- Multiple raw context IDs with the same normalized semantic identity confirm
  one economic evidence tuple. Every contributing context ID remains in
  provenance.
- Internally consistent eligible tuples with different `(start, end)` periods
  produce `ANNUAL_PERIOD_AMBIGUOUS`; neither count nor input order selects one.
- Contexts with the same entity, dimensions, and period but contradictory DEI
  values produce `ANNUAL_PERIOD_DATA_ERROR`, not ambiguity.

The resolver must use the context's actual start/end unchanged. It must not
calculate a start from `CurrentFiscalYearEndDate`, a prior filing, a calendar,
or a permitted duration range. Once resolved, downstream annual Company Facts
candidates may be required to match that exact `(start, end)`.

## Failure and ambiguity model

The implementation design should use explicit immutable outcomes:

- `ANNUAL_PERIOD_RESOLVED`: exactly one normalized eligible annual-period
  evidence tuple survives; equivalent contexts may confirm it.
- `ANNUAL_PERIOD_NOT_FOUND`: a valid supported artifact lacks a complete
  eligible DEI tuple.
- `ANNUAL_PERIOD_AMBIGUOUS`: multiple internally consistent eligible evidence
  tuples imply different annual periods.
- `ANNUAL_PERIOD_UNSUPPORTED`: the filing form/artifact is outside the approved
  exact-10-K filing-XBRL boundary.
- `ANNUAL_PERIOD_DATA_ERROR`: malformed or internally inconsistent supplied
  evidence, including contradictory DEI values within one semantic context,
  conflicting DEI values for equivalent periods, or invalid/inconsistent SEC
  entity scheme and registrant identity.

SEC transport, discovery, and artifact retrieval errors remain existing SEC or
filing-XBRL errors; they are not evidence outcomes. Normalization must not turn
an unavailable annual-period artifact into a guessed period.

## Provenance

A resolved period should retain only compact evidence needed for audit:

- company CIK and selected accession;
- selected filing form, report date, filing date, and primary document;
- filing-XBRL source URL and retrieval timestamp;
- DEI namespace, concept names, normalized values, and every preserved raw
  value;
- all contributing raw context IDs;
- context entity-identifier scheme and value, normalized registrant CIK,
  start, end, and normalized dimensions;
- evidence kind `DEI_REQUIRED_CONTEXT` and resolution status.

Presentation-role/anchor evidence may be recorded as optional corroboration in
research tools, but should not become required production provenance.

## Option comparison

| Option | Correctness/generality | Complexity and cost | Decision |
|---|---|---|---|
| Company Facts only | Cannot identify the DEI required context | Lowest | Reject |
| Filing-XBRL DEI context | Standards-backed, exact dates, works across calendar, non-calendar, and 52/53-week filings | Small pure resolver; one explicit artifact retrieval when needed; existing parser suffices | **Adopt** |
| Presentation-linkbase parsing | Concept-role structure is useful, but does not itself bind individual facts to contexts | New DTS/linkbase processor; fragile as primary authority | Do not require |
| Inline statement-column parsing | Directly exposes fact placement, but HTML layout and headings vary | High parser complexity and fragility | Audit/research only |
| Separate annual-period metadata layer | Cleanly preserves typed outcomes and provenance without changing filing or fact models | Small new pure SEC-domain module | Recommended architecture |

## Next step

Implement a narrow, pure `sec/annual_period.py` layer over `SECFilingXBRL`,
with synthetic network-free tests for resolution, missing DEI facts,
conflicting contexts, dimensions, identity mismatch, wrong form, wrong report
date, non-calendar years, and 52/53-week periods. Retrieval should remain
explicit and on demand. After independent review, validate the resolver against
the 42 filing corpus before using it to filter annual normalization candidates.
