# Four-pilot direct Revenue / EBIT evidence and delivery

2026-10-13; starting HEAD `e1f7d1c5310f2d6535e8f855382c066c9e422e53`.
Phase 1 only; no SEC requests, derivations, new fallback or period registration.
[Reviewed statement evidence](pilot-direct-income-evidence.json), version 1,
SHA-256 `efd4618955e56e17bd3a9b0b44374b501236151adcdefc04a4e661834844b274`,
binds eight observations to the original retained receipts in the unchanged
reported-input registries. The [mapping](pilot-historical-input-mappings.json)
is now version 2, SHA-256
`364bd0d2de9972e0119946b8ac83c465b6adbad07efcfeefa7fe54d406a0143c`.
Adapter annual/history bundle versions advance to 2; separate serializer/model
schemas remain unchanged. Original reported-input bundle identities/bytes do not
change. Earlier mapping/adapter delivery remains recorded in their results docs.

## Bounded inspection and selection

| Exact selected filing / authoritative annual dates | Revenue, USD millions | EBIT, USD millions | Revenue / EBIT confirming root-child ordinals |
| --- | ---: | ---: | --- |
| MSFT `0000950170-25-100235`, 2024-07-01–2025-06-30 | 281,724 | 128,528 | 536,2196,2216,2250 / 560,2205 |
| MSFT `0001193125-26-323660`, 2025-07-01–2026-06-30 | 331,839 | 155,237 | 543,2234,2254,2288 / 567,2243 |
| AAPL `0000320193-25-000079`, 2024-09-29–2025-09-27 | 416,161 | 133,050 | 285,599,1210,1302 / 309,1233 |
| Alphabet `0001652044-25-000014`, 2024-01-01–2024-12-31 | 350,018 | 112,390 | 541,856,892,1196,2000 / 559,2015 |

All eight inputs are available, origin **reported**, quality supported, reviewed,
complete only within their **consolidated reported annual statement-total scope**.
No whole-issuer, economic EBIT adjustment or consumer sufficiency certification.
Every value retains a consumer/timing limitation. XBRL dollars have scale 1,
positive sign and decimals −6; face statements display millions (inline scale 6,
decimals −6). No precision is manufactured by the display-to-dollar comparison.

Revenue uses the existing approved
`us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` meaning;
`us-gaap:Revenues`, the other existing approved direct candidate, has **no eligible
exact annual occurrence in any of these four instances**. EBIT uses only
`us-gaap:OperatingIncomeLoss`. Namespace URIs, raw values, context/unit IDs,
ordinals and every eligible candidate are explicitly retained in the mapping;
statement tag IDs/captions/attributes, URLs and typed original-body digests are
in the evidence matrix. Namespaces are the filing's FASB US-GAAP namespace,
not an issuer extension accepted by local-name similarity.

Selection is independently tied to the consolidated income statement: MSFT
“Total revenue” / “Operating income”; AAPL “Total net sales” / “Operating income”;
Alphabet “Revenues” / “Operating income”. First face-statement inline IDs:
MSFT 2025 `F_54f7ed46-65f2-456a-a77a-3c4b7593c6fb` /
`F_73173a29-1d08-4327-aaa1-9436332a6097`; MSFT 2026
`F_a62216e4-4826-4209-89af-643bc5c2df10` /
`F_606d36b1-9131-48c7-bcf9-e3c31061fd5c`; AAPL `f-78` / `f-102`;
Alphabet `f-157` / `f-175`. The primary receipt and exact inline locator survive
serialization in addition to every extracted-instance occurrence. The numerical
check confirms the tagged statement representation; it is not the sole proof of
scope, which also uses approved direct semantics, reviewed face location and
exact consolidated entity/annual context. Segment facts and comparatives remain
in original bodies but are excluded; no segment summation or expense bridge.

The isolated [inspection implementation](../src/valuation_platform/analyst/pilot_direct_income.py)
reuses the filing-XBRL structural context/unit/fact parsers and the existing
bundle annual-DEI/form checks, without constructing synthetic filing dates or
retrieval receipts. Four exact source identities only. Exact nondimensional
entity/annual dates, non-nil numeric facts and simple ISO-4217 USD are required.
Missing/broken structural links, nil collisions and invalid monetary evidence
fail conservatively. No amended/future filing, extension or new concept approval.

Duplicates with equivalent context/unit IDs and exact numeric representations
confirm; all occurrences remain in deterministic original ordinal order.
Different raw representations/precision stay intact (separate equal-value
candidate alternatives where precision differs). Every competing eligible
concept/value is inspected and retained. Differing values remain null/conflicting
with candidate provenance; policy order or statement matching cannot suppress
them. The committed exact-candidate mapping fails closed if its evidence changes.
There are **25 confirming occurrences and no differing eligible candidates** in
the actual eight reviewed sets.

## Delivery, limitations and preservation

Only Revenue/EBIT entries change in the previous four-period mappings; all other
field dispositions, requirements, original CFO checks and supplementary inputs
remain identical. Mapped/support-only/unavailable families now:
MSFT 2025 **8/1/5**, MSFT 2026 **8/1/5**, AAPL 2025 **7/1/6**, Alphabet 2024
**8/1/5** (31 mapped, four support-only, 21 unavailable family bindings).
The adapter has 68 top-level reported observations, 25 null required slots and
nine D&A support observations under four null required D&A slots. The original
69 cash-flow-package source bindings / 76 occurrences remain; eight direct
bindings / 25 occurrences are added separately. No component sum or residual.

Alphabet retains its separately refreshed instance receipt and the original
metadata gap, not invented original retrieval metadata. Native proof serializers
and all original registry/sidecar artifacts are unchanged. Frozen schema 5,
policies/values/output states, NWC blockers, D&A limitations and pilot acceptance
restrictions remain unchanged. Baseline 1905/1483/11/27/42 across 3468 is retained,
not rerun. No automatic valuation use, readiness, tax assumption or new period.

## Validation and stopping point

Focused tests compare hard-coded reviewed statement amounts against retained
primary inline tags independently of adapter values. They exercise all eight
selections, confirming duplicates, equivalent context/unit IDs, differing raw/
decimals representations, eligible conflicts, period/entity/accession, unit/nil/
precision and structural failures, excluded dimensions/extensions/comparatives,
candidate provenance, deterministic serialization and original-artifact/non-income
mapping preservation. Existing model/adapter/mapping and native serialization
preservation checks are reused. Compileall, local links and diff checks are
required; no full-suite/corpus run or fresh retrieval.

**Verified result: 75 focused tests passed**: 17 new direct-income tests, 15
adapter tests, 16 mapping tests, 24 immutable-model tests and three native
serialization preservation checks. All four mapping reports and independent
reported CFO reconciliations pass. Adapter replay is deterministic and rejects
tampered direct evidence; source identities/byte proofs are unchanged. Compileall
and `git diff --check` pass; **394 local documentation links resolve**. Validation
logs remain in `/tmp`, not retained as new financial evidence.

**Next smallest field-coverage milestone, only if authorized:** bounded retained
fiscal-year-end cash/investment component mapping and tests for these same four
periods. Preserve individual populations/restrictions; no totals or inference from
cash-flow rows. Stop with explicit missing scope/bindings rather than a research
chain. This milestone stops after direct Revenue/EBIT delivery.
