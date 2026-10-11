# LRCX Capex component completeness

Phase 1H.4 Wave 34; starting HEAD
`e4ee48865bcf7bc150c10db245c8b656b3b75234`, clean `main`, twelve commits
ahead of origin. Documentation-only; no push, policy change, tests or corpus.

## Decision and exact scope

**NO-GO for direct acceptance or a component equation.** All five frozen LRCX
periods remain `DERIVATION` / `COMPONENT_SCOPE_UNPROVED`; safe additional
coverage is **zero**. This is insufficient cash-component evidence, not a
demonstration that PP&E cash purchases are zero or inherently incompatible.
The [five-row supplement](capex-lrcx-component-inventory.json) extends research
without changing the [frozen 57-row inventory](capex-inventory.json).

The [current primitive](financial-methodology.md) is gross cash expenditure
to acquire PP&E. A combined PP&E/intangible payment is not equivalent merely
because it is an investing outflow, repeats annually, or uses a standard tag.
No generic fallback, issuer extension, residual, book-change equation or
mineral/lease analogy is approved. Existing 147 direct and fifteen curated
Capex results are unaffected; LRCX's five and the other 37 controls remain
unapproved. Those 37 periods did not receive fresh scope research here.

## Five-period evidence matrix

Amounts below are exact positive USD cash-outflow magnitudes. Each link is the
selected filing's consolidated cash-flow statement, not a later comparative.

| FY / selected accession | Authoritative annual dates | Combined cash | Context / occurrence ordinal | Decision |
| --- | --- | ---: | --- | --- |
| [2022 / 0000707549-22-000107](https://www.sec.gov/Archives/edgar/data/707549/000070754922000107/R7.htm) | 2021-06-28–2022-06-26 | 546,034,000 | `ie4a58d9db8804280b7fb575e3fbfb49f_D20210628-20220626` / 246 | Component scope unproved |
| [2023 / 0000707549-23-000102](https://www.sec.gov/Archives/edgar/data/707549/000070754923000102/R7.htm) | 2022-06-27–2023-06-25 | 501,568,000 | `c-1` / 254 | Component scope unproved |
| [2024 / 0000707549-24-000106](https://www.sec.gov/Archives/edgar/data/707549/000070754924000106/R7.htm) | 2023-06-26–2024-06-30 | 396,670,000 | `c-1` / 253 | Component scope unproved |
| [2025 / 0000707549-25-000075](https://www.sec.gov/Archives/edgar/data/707549/000070754925000075/R7.htm) | 2024-07-01–2025-06-29 | 759,186,000 | `c-1` / 259 | Component scope unproved |
| [2026 / 0000707549-26-000037](https://www.sec.gov/Archives/edgar/data/707549/000070754926000037/R7.htm) | 2025-06-30–2026-06-28 | 966,405,000 | `c-1` / 260 | Component scope unproved |

All five facts are `us-gaap:PaymentsToAcquireProductiveAssets`, namespace
`http://fasb.org/us-gaap/{2022…2026}` for the respective filing. Each has one
eligible consolidated annual occurrence, CIK 707549, empty dimensions, exact
USD, decimals `-3`, non-nil status and a positive XBRL magnitude. The face
caption is “Capital expenditures and intangible assets,” displayed negatively
in USD thousands. The calculation link contributes weight `-1.0` to net
investing cash, not a PP&E/intangible decomposition. Selected-instance DEI
reconciles all annual identities, including the 53-week FY2024 period. The
supplement preserves every researched numeric occurrence, raw representation,
unit/context link, dimensions, original zero-based instance ordinal and
presentation/calculation metadata. No exact annual nondimensional direct
PP&E or intangible cash-payment fact was found in these selected instances.

## Component and cash-basis findings

For every accession, `R11.htm` establishes consolidation and asset accounting;
`R20.htm` reports PP&E classes, book balances and depreciation; `R21.htm`
reports intangibles; `R24.htm` distinguishes lease cash and noncash additions;
`R26.htm` covers purchase commitments and, where disclosed, government
assistance. Their exact URLs, original bytes, hashes and reviewed text are
bound per accession in the supplement and [body fixture](evidence/lrcx-capex-response-bodies.json).

| Period | Intangible / acquisition evidence | Cash split and remaining blocker |
| --- | --- | --- |
| 2022 | Customer relationships, existing technology, patents/other; net intangibles $101.850m; amortization $78.0m. Future-amortization schedule excludes $17.8m not yet in service. | No exhaustive intangible cash operand. Neither amortization nor excluded capitalized costs establish current-year payments. |
| 2023 | Net intangibles $168.454m, including IPR&D $30.081m. [Business-combination note](https://www.sec.gov/Archives/edgar/data/707549/000070754923000102/R30.htm) identifies November 2022 transactions valued at $153.8m and acquired intangible fair value $81.210m. | Separate acquisition cash net of acquired cash is $119.955m. PPA fair values are not an intangible cash component of the $501.568m combined line; no subtraction or overlap inferred. |
| 2024 | Net intangibles $138.545m; amortization $56.3m; impairment described as insignificant, not zero. [Acquisition note](https://www.sec.gov/Archives/edgar/data/707549/000070754924000106/R29.htm) finalizes the prior-year PPA, not a new annual cash operand. | Reported acquisition cash is zero, but this does not prove zero separate intangible purchases. IPR&D/technology balance movements are not a cash bridge. |
| 2025 | Intangibles $182.2m; amortization/impairment effects described as not material; less detailed class disclosure. | Actual reported acquisition cash zero does not establish intangible cash zero. Balance growth is not an eligible payment operand. |
| 2026 | Intangibles $269.3m, primarily capitalized software; amortization/impairment effects not material. | Software in the PP&E accounting policy does not establish that separate intangible software belongs in PP&E or quantify its paid portion. No current acquisition cash line is not proof of zero. |

### Noncash, lease and gross/net exclusions

All amounts in the following table are USD thousands, from exact selected
annual facts. They are supporting exclusions, **not approved equation operands**.

| FY | Unpaid Capex (year-end noncash schedule) | Inventory transferred to PP&E (noncash) | Operating ROU additions (noncash) | Finance ROU additions (noncash) | Finance principal cash (financing) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2022 | 80,296 | 75,068 | 121,580 | 13,868 | 11,513 |
| 2023 | 31,899 | 76,856 | 91,592 | 20,161 | 14,985 |
| 2024 | 60,826 | 71,267 | 146,169 | 226,519 | 255,695 |
| 2025 | 80,799 | 90,873 | 81,011 | 2,884 | 4,059 |
| 2026 | 119,605 | 125,691 | 207,172 | 3,308 | 4,971 |

Unpaid purchases are not cash paid, inventory transfers do not constitute a
new investing payment, and lease obligations exchanged for ROU assets are
noncash. Operating lease payments and financing principal are separately
classified cash flows; neither repairs the intangible split. Do not add them
to the combined line or subtract them on an assumption of inclusion.

The [2024 lease note](https://www.sec.gov/Archives/edgar/data/707549/000070754924000106/R24.htm)
identifies exercise of California facility purchase options during the quarter
ended September 24, 2023, release of approximately $250m restricted collateral,
and $250.5m PP&E additions (land $40.5m; buildings/improvements $210.0m).
The annual financing principal is $255.695m. These are different reported
quantities; no equality, cash-allocation equation or addition to investing
Capex is asserted. Finance-lease purchase treatment would require a separate
methodology decision and explicit payment/non-overlap evidence, not an
implicit extension of the CVX acceptance. PP&E tables exclude finance ROU
assets, so their book movements cannot independently reproduce all spending.

The cash-flow statements separately present securities proceeds and other
investing cash. The latter is not disaggregated into eligible PP&E disposal
proceeds in this review. No disposal netting, zero-proceeds assumption or
gross-up is approved. Commitments describe future obligations, not actual
annual intangible payments. FY2025/2026 notes describe insignificant cash
grants and immaterial refundable-tax-credit reductions of PP&E basis with
tax-liability offsets; “immaterial” is not zero and a basis reduction is not
an independently quantified investing-cash netting operand.

## Completeness and reconciliation

**No equation is approved.** A theoretical split of combined cash less an
exhaustive excluded-intangible cash amount needs independently evidenced
payment timing, asset perimeter, signs and non-overlap. None of the five
selected statements/notes supplies that operand or an independently complete
PP&E cash total. Asset balances, amortization, acquired fair values and
noncash additions do not fill the gap. Matching residuals would not prove it.

The statement display reconciles exactly to each tagged combined cash value
(thousands × 1,000); no rounding tolerance is needed. Separately, PP&E gross
less accumulated depreciation reconciles to the R20 net amount exactly in all
five periods, explicitly excluding finance ROU. That book identity is stored
as a check, **not** a cash-flow equation or completeness proof. The acquired
intangible classes in FY2023/FY2024 sum to the disclosed $81.210m PPA fair
value; this likewise cannot be substituted for cash paid.

## Provenance, validation and next milestone

Sixty-two original response bodies are retained losslessly as gzip/base64 with
explicit `sha256_sec_response_body_bytes` digests and byte lengths: fifty
reused bodies and twelve targeted SEC gap retrievals (ten lease/commitment
notes and two acquisition notes). Forty-five existing required artifact/note
fingerprints match their retained original bytes. Reused retrieval timestamps
and HTTP status remain unknown rather than fabricated; new responses retain
their timestamps/status. Parsed report text is derived review material, not
the representation hashed. Five historical index/discovery fingerprints are
preserved separately as not independently verified in this milestone and are
not used as acceptance proof; the frozen inventory is unchanged.

Validation reconciles five unique frozen accession/start/end identities, CIK,
annual DEI, units, dimensions, original occurrence ordinals, statement signs,
classification totals, relationship bodies, typed digests, book arithmetic and
relevant local links. Production baselines are carried forward, not remeasured:
Capex **162 resolved / 42 missing / 0 ambiguous**; aggregate **1,900 / 1,488 /
11 / 27 / 42**, total **3,468**. No code, tests, policies or schema changes;
no tests or corpus rerun.

Next bounded milestone: documentation-only cash-technology/software and PP&E
perimeter research for the five frozen Visa Capex controls. Visa D&A expense
approvals do not approve Capex cash scope. Do not repeat LRCX research unless
new exact-period cash-component evidence becomes available.
