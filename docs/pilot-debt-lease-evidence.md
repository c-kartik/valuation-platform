# Four-pilot retained year-end debt/lease components

Phase 1 only; starting HEAD `2b949f8bed817d2a72e06fdee3aa4e5687362f1c`.
[Contract](dcf-input-contract.md), [machine-checkable evidence](pilot-debt-lease-evidence.json),
[mappings](pilot-historical-input-mappings.json),
[isolated inspector](../src/valuation_platform/analyst/pilot_debt_leases.py).
This is reported component preparation, not a new issuer approval registry,
debt policy, lease convention, financing adjustment or valuation authorization.
No amounts are summed or substituted between carrying, principal and fair-value bases.

## Exact identities and provenance

| Period | CIK | Selected 10-K accession | Authoritative annual dates / balance instant |
| --- | ---: | --- | --- |
| MSFT FY2025 | 789019 | 0000950170-25-100235 | 2024-07-01–2025-06-30 / 2025-06-30 |
| MSFT FY2026 | 789019 | 0001193125-26-323660 | 2025-07-01–2026-06-30 / 2026-06-30 |
| AAPL FY2025 | 320193 | 0000320193-25-000079 | 2024-09-29–2025-09-27 / 2025-09-27 |
| Alphabet FY2024 | 1652044 | 0001652044-25-000014 | 2024-01-01–2024-12-31 / 2024-12-31 |

Reuse original instance/primary bodies and actual receipts from the unchanged
[MSFT](company-data-preparation/msft-reported-cash-flow-bundles.json),
[AAPL](company-data-preparation/aapl-reported-cash-flow-bundle.json) and
[Alphabet](company-data-preparation/googl-reported-cash-flow-bundle.json) packages.
Alphabet's [explicit refreshed receipt](evidence/googl-fy2024-instance-provenance-refresh.json)
and original metadata gap remain distinct. No fabricated retrieval metadata or
new SEC requests. The new evidence matrix records exact URLs, typed
`sha256_sec_response_body_bytes` digests, QName/namespace, primary inline IDs,
display/scale/decimals/context/unit/sign, reviewed note passages and dimensional
selectors. Mappings additionally retain every eligible extracted fact ordinal,
raw numeric representation, exact instant, CIK and normalized USD identity.

Evidence matrix SHA-256:
`aac330aeccc9c132fcaa3e30054edacb25419cb2a12f2647567111d062945aec`.
Mapping version 4 SHA-256:
`ff226429dd0ef9d9f2d11607827cb5993dd54efc2507fd093a584db359b3e53d`.
These are field mappings/review locators, not new financial acceptance policies.

## Independently reviewed reported observations

All amounts below USD millions, positive reported balances/obligations; output
uses raw USD, scale 1/sign +1. Main captions have decimals −6. Fair values have
decimals −8; Alphabet commercial paper retains issuer decimals `INF` with
inline display scale 9. Preserve that representation, not a calibrated accuracy
claim. MSFT FY2025 commercial paper has equal explicit zero representations at
−6 and −9 precision: both are retained, never an absence-to-zero inference.

| Component / basis | MSFT 2025 | MSFT 2026 | AAPL 2025 | Alphabet 2024 |
| --- | ---: | ---: | ---: | ---: |
| Commercial paper borrowing | 0 (reported) | null | 7,979 | 2,300 |
| Current term debt carrying | 2,999 | 9,227 | 12,350 | 999 |
| Noncurrent term debt carrying | 40,152 | 31,067 | 78,328 | 10,883 |
| Reported term-debt parent caption | 43,151 | 40,294 | 90,678 | 10,883 (noncurrent only) |
| Total face/principal of notes | 49,206 | 46,136 | 91,281 | 12,000 |
| Estimated notes fair value | 40,400 (rounded) | 36,500 (rounded) | 80,400 (rounded) | 9,000 (rounded) |
| Next-year principal maturity | 3,000 | 9,250 | 12,393 | 1,000 |
| Operating lease discounted total | 22,861 | 21,925 | 12,490 | 14,578 |
| Operating lease discounted current | 5,424 | 5,393 | 1,579 | 2,887 |
| Operating lease discounted noncurrent | 17,437 | 16,532 | 10,911 | 11,691 |
| Finance lease discounted total | 46,172 | 66,594 | 1,230 | 1,677 |
| Finance lease discounted current | 3,172 | 4,290 | 538 | 235 |
| Finance lease discounted noncurrent | 43,000 | 62,304 | 692 | 1,442 |
| Operating lease undiscounted future payments | 25,481 | 24,706 | 14,725 | 17,038 |
| Finance lease undiscounted future payments | 60,506 | 89,686 | 1,579 | 1,888 |
| Reported combined discounted lease parent | unbound | unbound | 13,720 | unbound |

Unbound combined parents are not synthesized. Separate explicit null requirements
preserve the lack of a complete aggregate; no missing combined tag implies zero.
Available individual components never claim a complete debt/lease perimeter.

### Scope and inclusion decisions

- **MSFT:** Note 10 labels `DebtInstrumentCarryingAmount` observations as total
  face value, versus adjusted `LongTermDebt` total debt and current/noncurrent
  carrying balances. Note 13 locates operating current/finance current/finance
  noncurrent liabilities using exact `BalanceSheetLocationAxis` members
  `OtherCurrentLiabilitiesMember`/`OtherNoncurrentLiabilitiesMember`.
  Those reviewed location dimensions are preserved; arbitrary segment or
  instrument dimensions cannot confirm them. Dedicated operating noncurrent
  and total lease tags remain separate. Finance liabilities are included in
  other current/long-term liabilities, not silently in the notes-debt caption.
- **AAPL:** Note 9 distinguishes 91,281 principal, 90,678 adjusted term debt,
  current/noncurrent carrying balances and 80,400 fair value. The fair-value
  observation retains exact `FairValueByFairValueHierarchyLevelAxis` /
  `FairValueInputsLevel2Member`, not an inferred nondimensional total. Note 8
  separately reports operating/finance current/noncurrent and discounted totals.
  The `aapl:OperatingandFinanceLeaseLiability` parent is a reported book
  observation with explicit component overlap, not generic extension approval.
- **Alphabet:** Note 6 explicitly calls `LongTermDebt` 12,000 **face value**.
  Balance-sheet `LongTermDebtAndCapitalLeaseObligations` is the 10,883 noncurrent
  notes caption linked to Note 6, duplicating `LongTermDebtNoncurrent`.
  Do not infer finance-lease inclusion from the local name or apply historical
  2021–2023 derivations to this accession. Note 4 places finance liabilities in
  other current/long-term liabilities and operating liabilities separately.
- Lease payment schedules include imputed interest before discounting; they
  are future obligations, not liabilities to add to discounted totals and not
  the previously packaged historical lease cash payments. Principal maturities
  are not current carrying debt. Fair values are not carrying balances.
  Parent/subcomponent and alternative-basis overlap flags prohibit aggregation.

## Availability versus completeness and conservative behavior

| Period | Available component slots | Missing component slots | Additional null requirements | Retained fact occurrences |
| --- | ---: | ---: | ---: | ---: |
| MSFT FY2025 | 15 | 0 | 3 | 21 |
| MSFT FY2026 | 14 | 1 | 3 | 19 |
| AAPL FY2025 | 16 | 0 | 3 | 20 |
| Alphabet FY2024 | 15 | 0 | 3 | 20 |

61 mapped slots = 60 available / one unavailable, with 80 fact occurrences.
The FY2026 MSFT commercial-paper field remains null after one bounded inspection;
FY2025 zero and FY2026 narrative/tag absence do not approve FY2026 zero.
Every period has three further null requirements: other short-term borrowing
population, complete non-overlapping debt/lease aggregate, and unrecognized
lease commitments/coverage. Notes describe not-yet-commenced leases, but these
cannot become recognized liabilities or prove a complete financing perimeter.
No complete-debt or financial-sufficiency claim; acknowledgment cannot clear nulls.

Existing annual-DEI and filing-XBRL parsers verify exact selected filing/annual
identity, CIK, instant, QName, reviewed dimensions, non-nil exact USD numeric
evidence and precision. All matching occurrences remain ordered by original
ordinal. Equal values confirm, with differing precision kept as alternatives;
differing eligible values become a null/conflicting component with all
alternatives. Invalid contexts/units/nil/precision and changed receipt/statement
bindings fail conservatively. Other instants/scopes cannot populate the field.
Primary note references never acquire fabricated extracted-fact ordinals.

Mapping and isolated annual/history bundle versions advance to 4, with schemas
unchanged. Separate serialization replays every exact component binding,
dimension/role/precision/overlap/unknown. Current top-level observations/nulls are
153/49; family M/L/U counts 10/1/3, 10/1/3, 9/1/4, 10/1/3.
Nine D&A support observations, four cash alternatives and one additional
commercial-paper precision alternative remain explicitly separate.
All non-debt mappings and original bundles/sidecars/evidence, frozen schema 5,
policies/outputs, support classifications and blockers remain unchanged.
Baseline 1905/1483/11/27/42 across 3468 remains retained, not rerun.

## Validation and stopping point

[Focused tests](../tests/analyst/test_pilot_debt_leases.py) independently pin
statement values and precision; verify exact instants, CIK/QName/dimensions,
receipts, duplicate/conflicting candidates, overlap and liability/payment roles,
nulls, deterministic serialization and unchanged non-debt/frozen/original artifacts.
Relevant existing mapping/adapter/income/cash/model preservation tests and four
independent CFO checks are reused. **101 focused tests passed**: 12 new debt/lease,
14 cash, 17 direct-income, 15 adapter, 16 mapping, 24 historical-input model and
three native artifact-preservation checks. All four mapping/CFO checks passed;
compileall, 426 local links, evidence/mapping digests and `git diff --check` passed.
Deterministic round trips preserve all four periods' meanings, dimensional
occurrence references and original packages. No SEC, full-suite/corpus,
adjustment or valuation calculation.

**Next bounded step, only if authorized:** factor a reusable retained-instance
direct-component inspection interface from the tested pilot income/cash/debt
patterns. Acceptance: reproduce all four pilot mappings and serialized meanings
exactly, preserve scope selectors/unknowns and financial policies, and add focused
cross-field tests. No additional issuer/period registration or new economic
treatment; this is a shared prerequisite for later universe-wide preparation,
not forty fresh research cycles. Stop after this component milestone.
