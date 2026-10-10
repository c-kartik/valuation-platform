# D&A Component-Completeness and Derivation Design

## Decision and scope

Phase 1H.4 Wave 21, researched against committed HEAD
`e128235b9b243e28ab0f545ed3a4e6c3319a1879` after its validated push.
**NO-GO for component-derivation implementation:** zero newly approved equations,
19 periods require further research and 14 are methodology-blocked in this
research design. This does not reclassify any production measure state.
Safe additional coverage is **0/33**, not the number of available components.

The [machine-checkable matrix](depreciation-amortization-component-derivation-matrix.json)
contains exactly the 33 `DERIVATION` rows of the unchanged
[Wave 18 inventory](depreciation-amortization-inventory.json): AVGO, INTC,
ABBV, MRK, TXN and ORCL five each, GEV two and PM one. Each row freezes CIK,
selected 10-K metadata, exact annual dates, authoritative DEI, instance digest,
component QNames, captions, context/entity/dimensions, unit definition,
raw/Decimal value, decimals, nil status and original occurrence ordinals.
Presentation roles and calculation relationships are linked to the exact
concept entry in the digest-bound source inventory; no label-only approval.
All other annual occurrences have explicit audit references, not silent loss.

AMD's five extension periods are outside this pass and remain separately
gated. The five Visa approvals and generic/MSFT policies are unchanged.
The other 61 inventory rows (including Visa and AMD) are not freshly reviewed
denials. All 33 reviewed rows remain unapproved for production.

## Economic acceptance boundary

The existing [primitive](financial-methodology.md#da-research-status) is recurring
operating PP&E depreciation plus finite-lived operating-intangible amortization,
including qualifying software only once. An expense or cash-flow caption can
combine asset classes, impairment or leases despite an apparently pure QName.
Neither a matching total nor a cash-flow calculation arc proves completeness.

Approval would require all of: exact current selected-accession annual operands;
proved consolidated/continuing operating scope; exhaustive qualifying asset
classes; independently proved disjointness; expense-versus-capitalized/inventory
alignment; correct displayed/XBRL signs; explicit handling of impairment,
accretion and leases; and a reproducible bridge to the stated scope. None of
these rows currently meets the complete conjunction. Accordingly every
`approved_equation` and `approved_value_usd` is null. No illustrative sum below
is an approved D&A formula. No missing category is assigned zero.

Research dispositions (not policy or standardized-output enums):

- `EXACT_ACCESSION_DERIVATION_DESIGN_APPROVED`: all prerequisites proved; 0.
- `FURTHER_RESEARCH_REQUIRED`: filing-specific coverage/containment or precision
  selection remains unproved without a demonstrated need to redefine the primitive; 19.
- `METHODOLOGY_BLOCKED`: documented mixed lease/impairment exposure requires a
  reviewed compatible perimeter/treatment before arithmetic can be accepted; 14.

The last category does not say the issuer needs specialized valuation or that
all finance leases invalidate already accepted direct D&A. It gates these new
component proposals only. Integrated lease methodology remains deferred;
an embedded lease is not permission for an isolated add-back or subtraction.

## Issuer conclusions and evidence-backed treatment

### AVGO — four blocked; 2025 further research

The two acquired-intangible operating captions cover cost of products sold and
operating expenses, not separate additional asset classes. Their annual
reported amounts are 3,427/1,976; 2,847/1,512; 1,853/1,394; 6,023/3,244;
and 6,031/2,031 USD m. The cash-flow intangible/right-of-use caption instead
reports 5,502; 4,455; 3,333; 9,417; 8,201. Do not add that aggregate to its
operating subcategory, or infer a missing component from the difference.
2025's finite-intangible fact 8,062 agrees with the two acquired rows only as
corroboration; it does not establish the scope of the broader 8,201 caption.

Selected lease notes for 2021–2024 explicitly place finance ROU assets in PP&E
and report lease expense 16/18/16/27m. Those are gates, not subtractive
operands. The 2025 lease note describes operating leases; silence about a
current finance expense is not zero and must not inherit prior-year treatment.
Operating software/non-acquired coverage and acquisition/disposal alignment
still need affirmative proof. Financing-cost amortization 96/129/132/427/344m
and 2021 debt-cost write-off are excluded, not operating amortization.
Annual authoritative dates are retained, including AVGO 2021's explicit
legacy-DEI research evidence; this design does not repair the resolver gap.

### INTC — five further research

The identified-intangible note independently places acquisition-related,
licensed-technology and patent amortization in operating income and reports
1,839/1,907/1,755/1,428/949m. Repeated note/cash-flow occurrences confirm this
category, not another component. Depreciation add-backs are
9,953/11,128/7,847/9,951/10,757m. Accounting policies describe manufacturing
inventory capitalization, capitalized interest and capital-related grants or
incentives that reduce asset basis and depreciation. In 2022 a dimensional
grant contra-depreciation observation is 230m, with the note identifying cost
of sales relief. Do not subtract it from the add-back without proving whether
that amount is already net. Separate grants, software/lease containment,
accelerated/restructuring depreciation and operating-versus-capitalized
expense require an exact statement/asset bridge. The 2023 useful-life change
and 2025 Altera divestiture also prevent blindly assuming a stable perimeter.

### ABBV — five methodology-blocked

Accounting notes explicitly include internal-use computer software in
equipment depreciation (803/778/752/764/762m). Adding a software operand
again would overlap. Definite-lived developed product rights and licenses
are amortized in cost of products sold; precise cash-flow figures are
7,718/7,689/7,946/7,622/7,377m. The corresponding asset-note observations
7,700/7,700/7,900/7,600/7,400m have lower precision and remain distinct values.
IPR&D is indefinite-lived until regulatory approval/reclassification; acquired
IPR&D expense and subsequent impairment are not recurring amortization.
The note separately describes Vuity, CoolSculpting/Liletta and
Resonic/Durysta impairment; no impairment may be absorbed merely because it
also hits cost of products sold.

Every selected lease note explicitly places finance leases in PP&E and calls
finance costs insignificant without quantifying exact expense. Insignificant
does not mean zero. A pure non-lease depreciation split or a compatible
reviewed integrated perimeter is absent. Rounded-note corroboration cannot
resolve that scope gate or authorize a minimum-materiality exception.

### MRK — five further research

Exact cash-flow depreciation is 1,578/1,824/1,828/2,104/3,045m; generic
`AdjustmentForAmortization` is 1,636/2,085/2,044/2,395/2,793m. The finite-
intangible note shows rounded 1,600/2,100/2,000/2,400/2,800m primarily in
cost of sales. Their precision agreement is not an identity proof for the
generic adjustment. Accounting notes put internal-use software in PP&E but
cloud-service implementation costs in Other Assets. The adjustment's
containment of these categories, qualifying-versus-service-cost perimeter,
manufacturing/inventory and lease scope need a complete bridge. Preserve
2021 Organon scope rather than assume cash-flow and continuing EBIT align.
IPR&D impairment/research expense, pension amortization and tax reconciliation
amounts or ratios are excluded, not substitute amortization operands.

### PM — one methodology-blocked

The 1,189m extension explicitly includes impairment. The asset note reports
159m finite-intangible amortization, partitioned 58m in cost of sales and
101m in marketing/administration/research. Those location facts must not be
added to the 159m total. Its submitted major-class dimension is not discarded
or assumed to enumerate all classes merely because the note prose is broader.
The same note separately identifies 112m Wellness/Healthcare impairment.
That does not establish exhaustive impairment within the broad add-back.
The selected lease note reports 83m finance ROU amortization and places
finance assets in machinery/equipment. No residual reconstruction of
depreciation or isolated lease subtraction is approved. Acquisition-close
timing (Swedish Match) must be aligned to the consolidated annual scope.

### TXN — five further research; smallest targeted next pass

Cash-flow depreciation is 755/925/1,175/1,508/1,918m and capitalized software
amortization 57/54/63/72/81m. The first three filings also report acquired-
intangible amortization 142/0/0m. Income-statement
`AmortizationOfAcquisitionCosts` and cash-flow `AmortizationOfIntangibleAssets`
represent the same category: adding both would double count. The accounting
note establishes straight-line PP&E, leasehold improvements, acquired
intangibles and software licenses, but does not by itself prove a complete
expense/asset partition or depreciation's treatment of separately reported
software and factory inventory. 2024/2025 lack the acquired-intangible
operand; absence is not a zero observation. Capital incentives reduce asset
basis and depreciation, so grant-netting must be traced, not grossed up from
cash incentives. Lease notes identify operating leases outside the PP&E
caption; that helps scope but does not prove all other categories absent.

### GEV — two methodology-blocked

Asset notes establish finite customer/technology/software/trademark categories;
software is already in intangible amortization (277/238m). PP&E depreciation
and amortization is 895/615m. Crucially the 2024 note explicitly includes
108m Hydro restructuring impairment in the 895m amount; pure QName matching
would therefore overstate recurring D&A. The 2025 filing repeats that 108m
as **2024 comparative evidence**, not a 2025 operand. Reported broad totals
1,172/853m reproduce the reported components exactly, but this is not proof
that those components are impairment-free. Prior 2022 impairment disclosures
also must not migrate into the selected annual period.

The PP&E note includes operating ROU assets and separately disclosed equipment
leased to customers; the lease note also reports finance liabilities.
Containment of lease expense, exhaustive impairment exclusions and matching
the combined/pre-spin and consolidated/post-spin business scope remain gates.
Even a separately described 108m impairment does not approve a recurring D&A
equation before the remaining perimeter is proved.

### ORCL — 2022–2024 further research; 2025–2026 blocked

Exact PP&E depreciation is 1,972/2,526/3,129/3,867/7,623m. Finite acquired-
intangible expense is 1,150/3,582/3,010/2,307/1,671m; four identical
nondimensional representations per filing confirm, never quadruple, expense.
Retirement movements (716/2,400/1,298/2,155/2,392m) and amortized sales
commissions are not current finite-asset expense operands. Immaterial
capitalized software language does not prove zero or complete software
containment, so the earlier three filings remain unapproved.

2025's lease note explicitly says no finance leases in 2024; that does not
prove zero software or settle all earlier scope questions. Finance leases
begin in 2025, with 48m ROU amortization; 2026 reports 351m. Policy notes place
those assets in PP&E. Neither adding these to depreciation nor subtracting
them without a complete containment/integrated treatment is approved.
2026's note depreciation 7,600m is rounded support for 7,623m, not an equal
fact and not permission to choose by retrieval order.

## Complete frozen-period matrix

Numbers below are reported candidate magnitudes in USD millions, **not D&A
equations or normalized results**. D = depreciation; A = intangible expense
or the explicitly named generic adjustment; S = software; C/O = acquired-
intangible operating cost/expense captions; B = broad mixed aggregate; L =
finance-lease support. Multiple values separated by a slash retain precise
and rounded observations, not alternatives approved for selection. A dash
means absent from the relevant nondimensional inventory, never zero.
`R` = FURTHER_RESEARCH_REQUIRED; `M` = METHODOLOGY_BLOCKED. Exact occurrence
and dimension inventories, roles, calculation links, note URLs/digests and
row-specific checks are in the linked JSON matrix and source inventory.

| Issuer / CIK | Frozen accession | Annual start / end | Reported components (USD m) | Outcome |
|---|---|---|---|---|
| AVGO / 1730168 | `0001730168-21-000153` | 2020-11-02 / 2021-10-31 | C 3427; O 1976; B-ROU 5502; D 539; L 16 | M |
| AVGO / 1730168 | `0001730168-22-000118` | 2021-11-01 / 2022-10-30 | C 2847; O 1512; B-ROU 4455; D 529; L 18 | M |
| AVGO / 1730168 | `0001730168-23-000096` | 2022-10-31 / 2023-10-29 | C 1853; O 1394; B-ROU 3333; D 502; L 16 | M |
| AVGO / 1730168 | `0001730168-24-000139` | 2023-10-30 / 2024-11-03 | C 6023; O 3244; B-ROU 9417; D 593; L 27 | M |
| AVGO / 1730168 | `0001730168-25-000121` | 2024-11-04 / 2025-11-02 | C 6031; O 2031; B-ROU 8201; D 574; A 8062 | R |
| INTC / 50863 | `0000050863-22-000007` | 2020-12-27 / 2021-12-25 | D 9953; A 1839 | R |
| INTC / 50863 | `0000050863-23-000006` | 2021-12-26 / 2022-12-31 | D 11128; A 1907 | R |
| INTC / 50863 | `0000050863-24-000010` | 2023-01-01 / 2023-12-30 | D 7847; A 1755 | R |
| INTC / 50863 | `0000050863-25-000009` | 2023-12-31 / 2024-12-28 | D 9951; A 1428 | R |
| INTC / 50863 | `0000050863-26-000011` | 2024-12-29 / 2025-12-27 | D 10757; A 949 | R |
| ABBV / 1551152 | `0001551152-22-000007` | 2021-01-01 / 2021-12-31 | D 803; A 7718/7700 | M |
| ABBV / 1551152 | `0001551152-23-000011` | 2022-01-01 / 2022-12-31 | D 778; A 7689/7700 | M |
| ABBV / 1551152 | `0001551152-24-000011` | 2023-01-01 / 2023-12-31 | D 752; A 7946/7900 | M |
| ABBV / 1551152 | `0001551152-25-000020` | 2024-01-01 / 2024-12-31 | D 764; A 7622/7600 | M |
| ABBV / 1551152 | `0001551152-26-000008` | 2025-01-01 / 2025-12-31 | D 762; A 7377/7400 | M |
| MRK / 310158 | `0000310158-22-000003` | 2021-01-01 / 2021-12-31 | A-adjustment 1636; D 1578/1600; A 1600 | R |
| MRK / 310158 | `0001628280-23-005061` | 2022-01-01 / 2022-12-31 | A-adjustment 2085; D 1824/1800; A 2100 | R |
| MRK / 310158 | `0001628280-24-006850` | 2023-01-01 / 2023-12-31 | A-adjustment 2044; D 1828/1800; A 2000 | R |
| MRK / 310158 | `0001628280-25-007732` | 2024-01-01 / 2024-12-31 | A-adjustment 2395; D 2104/2100; A 2400 | R |
| MRK / 310158 | `0000310158-26-000063` | 2025-01-01 / 2025-12-31 | A-adjustment 2793; D 3045/3000; A 2800 | R |
| PM / 1413329 | `0001413329-23-000025` | 2022-01-01 / 2022-12-31 | B-impairment 1189; L 83 | M |
| TXN / 97476 | `0000097476-22-000009` | 2021-01-01 / 2021-12-31 | D 755; A 142; S 57 | R |
| TXN / 97476 | `0000097476-23-000007` | 2022-01-01 / 2022-12-31 | D 925; A 0; S 54 | R |
| TXN / 97476 | `0000097476-24-000007` | 2023-01-01 / 2023-12-31 | D 1175; A 0; S 63 | R |
| TXN / 97476 | `0000097476-25-000007` | 2024-01-01 / 2024-12-31 | D 1508; S 72 | R |
| TXN / 97476 | `0000097476-26-000059` | 2025-01-01 / 2025-12-31 | D 1918; S 81 | R |
| GEV / 1996810 | `0001996810-25-000011` | 2024-01-01 / 2024-12-31 | D 895; A 277; B-impairment 1172 | M |
| GEV / 1996810 | `0001996810-26-000015` | 2025-01-01 / 2025-12-31 | D 615; A 238; B-impairment 853 | M |
| ORCL / 1341439 | `0001564590-22-023675` | 2021-06-01 / 2022-05-31 | A 1150; D 1972 | R |
| ORCL / 1341439 | `0000950170-23-028914` | 2022-06-01 / 2023-05-31 | A 3582; D 2526 | R |
| ORCL / 1341439 | `0000950170-24-075605` | 2023-06-01 / 2024-05-31 | A 3010; D 3129 | R |
| ORCL / 1341439 | `0000950170-25-087926` | 2024-06-01 / 2025-05-31 | A 2307; D 3867; L 48 | M |
| ORCL / 1341439 | `0001193125-26-277521` | 2025-06-01 / 2026-05-31 | A 1671; D 7623/7600; L 351 | M |

Totals: **33 = 0 approved + 19 further research + 14 methodology-blocked**.
The original 94-row routing stays **31 concept-policy + 33 derivation +
5 issuer-extension + 25 methodology-blocker**. These 14 design gates are not
14 new production methodology-blocked states or edits to those routing counts.

## Occurrences, signs, precision and reconciliation

Candidate expense/add-back observations are positive magnitudes (including
TXN's explicit zeros); a future equation must assign independently reviewed
coefficients, not inherit a cash-flow arc's sign automatically. Original raw
representations, decimals and nil status remain in the matrix. Negative
pension/OCI amounts, tax ratios, accumulated-amortization movement and future
schedules are excluded rather than changed to positive D&A. Dimensions
retain full axis/member identity: an asset class, grant, segment or income-
statement location is not a consolidated interchangeable occurrence.

Repeated exact-Decimal facts retain deterministic full-instance ordinals.
Concept-level presentation membership is not proof of the rendered location
of an individual occurrence. No approval by first occurrence, largest amount,
highest precision, Company Facts availability or matching labels. Future
source-selective design would need explicit reviewed locations and retain
nonselected representations. Different eligible values remain ambiguous;
nil collisions, broken context/unit links and inconsistent identity are data
errors. No parser, production resolver or serialization change occurs here.

ABBV's five precise/rounded amortization pairs and MRK's five depreciation
pairs plus five amortization comparisons are compatible with submitted
precision, not exact duplicates or proof of category completeness. For a
-6 observation and a -8 observation the maximum independent comparison
bound is 0.5m + 50m = 50.5m. MRK's generic adjustment versus the finite-
intangible note remains a cross-concept scope question even inside this bound.
ORCL 2026 depreciation differs by 23m and similarly corroborates precision
only. No generic tolerance, replacement amount or rounding of operands is
designed. The matrix recalculates retained same-concept precision checks.

GEV broad reported totals reproduce the two reported categories exactly;
the explicitly embedded 2024 impairment demonstrates why exact arithmetic
does not establish equivalence. PM's 58m and 101m location disclosures total
159m, but cannot prove the broad 1,189m's complete composition. Accretion is
not a qualifying component; absence of an inspected accretion caption is not
zero or proof that an unspecified adjustment excludes it. No residual is
used to reconstruct depreciation, software, amortization, impairment or leases.

## Evidence reuse and new selected-filing gaps

All committed statement/asset/accounting evidence is reused, bound to its
frozen raw-byte SHA-256. Only 23 selected-filing lease notes were newly
retrieved to resolve specific ROU/PP&E and containment questions: AVGO five,
ABBV five, PM one, TXN five, GEV two, ORCL five. Every new URL returned HTTP
200 and stays under the frozen selected accession directory. Their report
roles, definitions, exact SEC URLs, SHA-256 and reviewed note text are retained
in each matrix row. No unchanged link is re-requested and no full concept
inventory is repeated. INTC has no separate lease report in the retained
report inventory; its incomplete lease/expense bridge remains explicit.

## Implementation boundary and next milestone

**NO-GO now:** no generic sum, issuer policy, exact-accession registry entry,
component-selection schema or runtime tolerance is approved. Direct-concept
precedence, the existing MSFT derivation and five Visa entries must remain.
A future curated derivation must independently retain each selected operand,
every confirming occurrence, reviewed selection/exclusion and scope proof,
exact coefficients and arithmetic through normalized/output/serialization
provenance; supporting notes never silently become operands.

Smallest next milestone: **TXN 2021–2023 targeted completeness/expense-scope
closure**, not implementation. Use its explicitly reported three categories
and zero observations to prove software/PP&E disjointness, exhaustive finite-
asset coverage and manufacturing/inventory plus grant-netting alignment to
the existing primitive. Resolve those specific evidence gaps before seeking
an exact-accession equation. If that cannot be proved, retain unresolved
outcomes or bring an explicit methodology decision for review. No forced
five-year extension; TXN 2024–2025 absent intangible operands stay separately
gated. ORCL 2022–2024 is a subsequent software-containment research candidate,
not approved coverage. Lease/impairment cases and AMD remain separate.

## Validation and unchanged production

Validate the exact 33 unique CIK/accession/start/end identities against the
digest-bound Wave 18 inventory and its frozen selected-filing/annual evidence;
six five-period issuers plus GEV two and PM one; every copied occurrence and
ordinal; reused raw-byte digests and new selected-directory evidence URLs;
classification totals and null equations; precision checks and broad-subtotal
arithmetic; relevant local documentation links; and `git diff --check`.
There are no approved equations to recalculate or implied operational results.

Production counts are carried forward, **not remeasured**: D&A **115 resolved /
89 missing / 0 ambiguous**, Operating Income **194 / 10 / 0**, aggregate
**1,885 resolved / 1,503 missing / 11 ambiguous / 27 methodology-blocked /
42 not-comparable = 3,468**. All 43 generic issuers, seven specialized skips,
204 annual periods and other measure states remain unchanged. No code,
tests, policies, schemas, source inventory or corpus artifacts change. No
tests or corpus rerun. Forecast/FCFF/DCF remains paused through Phase 1H.6.
