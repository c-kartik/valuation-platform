# Four-pilot retained year-end cash/investment components

2026-10-13; starting HEAD `1a49f71fa8fb907a8dc9900bb463fc9656f37e48`.
Phase 1 only. [Reviewed evidence matrix](pilot-cash-investment-evidence.json)
version 1, SHA-256
`b9c1da7534ed8fb02530d6d2b8f8bbce22cbc0bede6079ca1b34b3fce3b7996d`.
[Pilot mappings](pilot-historical-input-mappings.json) advance to version 3,
SHA-256 `9ec38a0e22a235cc82aa76d1eaca8d64f328247881b46a09a650a73bd4a3d9ff`;
isolated preparation annual/history bundle versions advance to 3. Existing
model/serializer schemas, original receipts, reported bundles/sidecars and all
non-cash/investment field dispositions remain unchanged. No SEC requests.

## Available observations, not an aggregate

All amounts below are USD millions. Source raw dollars retain scale 1/sign +1;
primary display scale 6 (millions) or 9 (billions) remains explicit. Main captions
have decimals −6. Rounded strategic observations have decimals −8; rounding is
not silently upgraded. Every observation is **partial for this preparation
perimeter**, even where its own reported caption is source-verified.

| Exact selected filing and year-end instant | Cash/equivalents | Current investments | Long-term observation | Other retained reported observations |
| --- | ---: | ---: | --- | --- |
| MSFT `0000950170-25-100235`, 2025-06-30 | 30,242 | 64,323 | 15,405 mixed long-term investments | 94,565 reported cash/current parent; 2,900 rounded measurement-alternative equity; 6,000 rounded equity-method; 30,242 combined cash/restricted closing caption |
| MSFT `0001193125-26-323660`, 2026-06-30 | 20,935 | 55,908 | 36,348 mixed long-term investments | 76,843 reported cash/current parent; 12,400 rounded measurement-alternative equity; 12,000 rounded equity-method; 20,935 combined cash/restricted closing caption |
| AAPL `0000320193-25-000079`, 2025-09-27 | 35,934 | 18,763 | 77,723 non-current marketable securities | 35,934 combined cash/restricted closing caption; issuer-extension combined caption 132,420 retained **only as support under a null gated component** |
| Alphabet `0001652044-25-000014`, 2024-12-31 | 23,466 | 72,191 | 266 marketable equity under long-term lock-up restrictions | 37,982 non-marketable parent; 95,657 reported cash/current parent; 2,000 rounded equity-method; 23,466 combined cash/restricted caption; extension combined caption 83,250 **support-only under a null gate** |

Authoritative annual identities are unchanged: MSFT 2024-07-01–2025-06-30 /
2025-07-01–2026-06-30; AAPL 2024-09-29–2025-09-27; Alphabet
2024-01-01–2024-12-31. Only their year-end instants qualify. Comparative balances
and annual cash purchase/movement rows cannot populate these balance components.
No extra period or quarterly approval.

Exact namespace/concept, context/unit IDs, raw values, decimals and root-child
ordinals are in each mapping's `retained_cash.candidates`; the evidence matrix
records every reviewed primary inline ID and original displayed representation,
including nested inline note tags. Thus the independently reviewed statement/
note display can be reproduced, not just compared with adapter output.

## Scope, overlaps and unresolved requirements

- Existing direct policies justify cash/equivalents and issuer-scoped current
  investments: MSFT `ShortTermInvestments`; AAPL/Alphabet
  `MarketableSecuritiesCurrent`. Cash is the **reported caption**, not certified
  unrestricted, operating or excess cash. See [unchanged methodology](financial-methodology.md#cash-and-investments).
- AAPL `MarketableSecuritiesNoncurrent` is the existing approved direct long-term
  marketable caption. MSFT `LongTermInvestments` is retained as a **mixed reported
  observation**, not a marketable-only fallback. Rounded measurement-alternative
  and equity-method observations are separately identified and may overlap it;
  no residual partition, subtraction or non-overlap certification.
- Alphabet's Note 3 expressly describes the 266m marketable equity amount as
  subject to long-term lock-up restrictions and located in other non-current
  assets. It is not unrestricted liquid cash and does not expand the frozen
  AAPL-only long-term marketable policy. Its non-marketable parent is distinct
  from current marketable securities; note accounting describes measurement-
  alternative and equity-method securities, not interchangeable cash equivalents.
- Reported parent captions and children remain separate, flagged for overlap.
  They are **never summed**. Combined cash/restricted captions may overlap cash,
  but even equal amounts do not prove standalone restricted cash is zero.
  MSFT cash/current parents overlap both their children. AAPL's extension caption
  overlaps the cash/current/non-current marketable populations; Alphabet's
  differently scoped extension caption is not equivalent to its 95,657m parent.
  Both extensions stay separately gated, with their reported facts preserved as
  support alternatives under null components, not generic concept approvals.
- Alphabet `EquitySecuritiesWithoutReadilyDeterminableFairValueAmount` has **two
  eligible representations**: 35,500m at decimals −8 (`f-640`, ordinal 1019) and
  35,531m at decimals −6 (`f-730`, ordinal 1109). Both remain reported alternatives
  beneath a null/conflicting component. The figures may reflect different
  reporting precision; this is not proof of economic disagreement or permission
  to force exact equality, a rounding adjustment or a preferred numeric value.

Every period has explicit null requirements for unrestricted/operating allocation,
standalone restricted cash, and a complete cash/investment aggregate. MSFT also
lacks a complete marketable-only partition of its mixed long-term caption. AAPL
has no independently reviewed/bound strategic component in this bounded pass;
that is **not absence or zero**. Alphabet lacks a complete non-overlapping
non-marketable partition. These are stopping conditions, not a new issuer-research
queue. Future economic treatment/availability must be separately designed.

| Period | Available reported component observations | Gated/conflicting component slots | Additional explicit null requirements | Family completeness |
| --- | ---: | ---: | ---: | --- |
| MSFT FY2025 | 7 | 0 | 4 | Partial, no aggregate |
| MSFT FY2026 | 7 | 0 | 4 | Partial, no aggregate |
| AAPL FY2025 | 4 | 1 | 4 | Partial, no aggregate |
| Alphabet FY2024 | 7 | 2 | 4 | Partial, no aggregate |

Totals: 25 available observations; three gated/conflicting slots retaining four
reported alternatives; 16 additional null requirements. Forty extracted
occurrences are retained. Component availability is not full financial-input
sufficiency. The field family is mapped/partial, never a complete cash aggregate.

## Implementation and preservation

[Isolated inspector/packager](../src/valuation_platform/analyst/pilot_cash_investments.py)
reuses existing annual-DEI/form/context/unit/occurrence checks against byte-pinned
native receipts. Exact year-end, normalized CIK, selected accession, nondimensional
USD, namespace, concept, raw/precision and statement/note representation are
verified. Broken links, nil/numeric collisions, non-USD and malformed evidence
fail conservatively. Missing exact-instant evidence remains unavailable; matching
labels or values are not scope proof. Equal-value duplicates confirm without loss;
different precision representations remain intact; differing values stay unresolved.
No new retrieval metadata, generic policy, fallback, derivation or economic choice.

`SourceReference` preserves original-body receipts, actual retrieval metadata,
typed digests, every fact ordinal/context and primary locators/scope excerpts.
No fabricated primary XBRL ordinal. Existing separate serialization carries original
bodies once in native proofs and the additional component/overlap/unknown metadata;
replay rebuilds and verifies all mappings. Alphabet's refreshed instance receipt
and original retrieval gap remain distinct. No source registry/body is rewritten.

Mapping family counts become 9/1/4, 9/1/4, 8/1/5, 9/1/4, but the new family is
explicitly partial. There are 93 top-level reported observations / 40 null slots,
nine unchanged D&A support observations and four cash support alternatives. All
other mappings and original CFO reconciliations are unchanged. Frozen schema 5,
policies, outputs, history exceptions, NWC/D&A blockers and pilot restrictions
persist. Corpus baseline remains 1905/1483/11/27/42 across 3468, retained not rerun.
No integrated readiness, asset/debt bridge, total, adjustment or valuation approval.

## Validation and next bounded step

Focused tests independently assert retained statement/note values; exact instant,
currency/scale/precision, nested notes, duplicates, conflicts, scope/overlap,
gated extensions, nulls, serialization and original artifact/non-cash mapping
preservation. **89 focused tests passed**: 14 new component tests, 17 direct-income,
15 adapter, 16 mapping, 24 historical-input model and three original-artifact
preservation checks. The mapping validator passed for all four periods, including
their unchanged independent CFO reconciliations. Compileall, 408 local links and
`git diff --check` passed. No full-suite/corpus run or SEC requests.

**Next smallest field milestone, only if authorized:** retained year-end debt/
lease component mapping for these same four periods. Preserve borrowing versus
lease liabilities, parent/subcomponent overlaps, restrictions and nulls; no net
debt or enterprise/equity bridge calculation. Stop after this cash/investment work.
