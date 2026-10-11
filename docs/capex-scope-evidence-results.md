# Wave 28 curated Capex implementation and verified results

Starting HEAD `2b017b57fa70c03939b8e87633fadea41ed58f16`; no push.
Implements only the [ten-entry design](capex-scope-evidence-design.md) as
`capex_scope_equivalence`, version `1`, scope `GROSS_CASH_PPE_EQUIVALENT`.
The generic Capex concept policy and all 47 unapproved controls are unchanged.
The historical [inventory](capex-inventory.json) and
[acceptance matrix](capex-scope-evidence-matrix.json) remain frozen research
snapshots; runtime registration is a separate immutable reviewed registry.

## Explicit evidence correction and refresh

Five LLY index digests describe retained default-separator UTF-8 JSON
serialization, not original response bodies. The
[correction audit](capex-scope-evidence-design.md#wave-28-implementation-attempt-representation-correction-and-blocked-validation)
retains both representations and independently verified fingerprints. Mandatory
source hashes are `sha256_sec_response_body_bytes`; retained JSON hashes are
`sha256_retained_reserialized_json_utf8_bytes`. Parsed equality is checked only
after hashing each against its own representation. No byte equality is claimed.

For 15 AMZN rendered artifacts, retained raw/JSON caches had no recoverable
original body matching the old digest. User-authorized fresh retrieval covered
R3.htm cash flow, R10.htm accounting policies and R12.htm PP&E for the five
exact selected accessions. Each refresh retains URL, accession, retrieval time,
HTTP status, representation, response hash/length and losslessly gzip/base64
encoded original body in the [response-body fixture](../tests/fixtures/capex_amzn_response_bodies.json).
The active registry links each old claimed fingerprint, marked
`unverifiable_original_body_unavailable`, to its approved fresh evidence.
Hashes are over decompressed original response-body bytes, not compressed or
base64 storage. The old evidence is not silently relabeled or treated as verified.

Fresh review independently reconfirms consolidated annual cash PP&E purchases,
owned PP&E asset classes, separate intangible/content policies, software
capitalization treatment, lease financing/noncash additions, unpaid purchases,
acquisition cash, and proceeds/incentive treatment. AMZN's five face purchase
amounts are respectively 61,053 / 63,645 / 52,729 / 82,999 / 131,819 USD million,
displayed as cash outflows and tagged as positive expenditures. The submitted
instance hashes, QName, current annual contexts, CIK, USD and operand values
remain unchanged and were re-parsed/verified in targeted normalization.
The selected accounting policy keeps software capitalization described as not
significant (not zero), vendor incentives reducing costs, and later government
incentives reducing assets/expenses. The PP&E note distinguishes asset classes
and noncash/unpaid amounts. Do not net the mixed proceeds/incentives line,
invent a pre-incentive gross-up or add finance-lease principal/noncash assets.

All 15 extracted report texts match retained review texts exactly, with no
substantive scope or operand discrepancy detected on fresh review. Because old
HTML bytes are missing, exact byte-level representational differences cannot
be proved; text equality alone was not the approval criterion. Fresh approval
comes from reviewing the current bodies/passages against the unchanged scope
criteria. No scope relaxation, economic adjustment or additional period approval.
This completes the unpublished v1 evidence foundation, not an in-place mutation
of a previously published runtime policy.

| Accession / location | Old unverified claimed SHA-256 | Approved refreshed response SHA-256 |
| --- | --- | --- |
| `0001018724-22-000005` / [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/R3.htm) | `690b031d178866865af507279ef5c7d921771647c38d37a3eed03166555506dd` | `7a7073d3654b4bdb47c76276abdd261778fbba9af244b431f50cee514d3f3baa` |
| `0001018724-22-000005` / [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/R10.htm) | `9f2992366011fec755e6966d329b26061c071ee5eedca5c00a33999e7ed6959d` | `3693d4f645f9d766c6df1cf6d312197ce38d7bfe8a3247a61cf1b9df9d300627` |
| `0001018724-22-000005` / [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/R12.htm) | `0ba87811887d954a243413a9944fd3f02948671255e362a6ccd128f3baa74086` | `6cc2e36b42ae7126f7f51080d6492341e5b8c0c30687e10713b89c8c6cde9187` |
| `0001018724-23-000004` / [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/R3.htm) | `d615fd070d097912f450af71ca988bd13e1845d41f8def6eb028032139abd526` | `a0915e28a88a0adf42e276b6736082062c7cca3410636f5894c359c24549def8` |
| `0001018724-23-000004` / [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/R10.htm) | `06d2c899d7fea3b76e67e765f4cb65ce490c453839384a2203c731b9f71e7b93` | `6d9dc5593b0a745eeb0dce5f410874d4a010689990bba02d309c8cd5357e0e04` |
| `0001018724-23-000004` / [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/R12.htm) | `8b9712927cbb414573abf45897f48c299160f9a0f6e01bc9919b6fcfc5872076` | `50769c8befdbac81c6d8f22edecce1036a37e440f45a607a03a6e9e08ae68919` |
| `0001018724-24-000008` / [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/R3.htm) | `0795c9cb473a7520b1f58f2e6eab9a3f33cf67a2652825f98794fb03f964e62c` | `3c5e5e66c5220c46c6e8d7b8f676cf441dde63e461c0b8e6712a0f050eaee22c` |
| `0001018724-24-000008` / [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/R10.htm) | `1df070f08b117b23a96161d72bd5480f85d25dbba959fc79078c116b08a78ac1` | `f625223586ae301547b9d0ab509837f1915514e2c271a96299fa8781afab80b1` |
| `0001018724-24-000008` / [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872424000008/R12.htm) | `0558c196997d941b48c4a7e4f5b209fe2d1afd04ab2f5c4eaf9dfe7ad4e32d1a` | `416cc1cbe204d2a3b325e7a9ec016ed09eef17b95c42685056819e99774fa24b` |
| `0001018724-25-000004` / [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/R3.htm) | `dcd28a4c0e57c344862f3cd4fe240c4ddb5d20209df040c278f30211e4095706` | `dc6b84ba2847bc846c14bb6cb7c239a1f444288a2716344c70afbb0531e7ac04` |
| `0001018724-25-000004` / [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/R10.htm) | `c4ca9fffbc1de2c9ebca1f4e0b87da4085569a5626e188d672ad1af705076f5a` | `81d1355554bbdd2ca5753d7d489a017b75f9a4fd0dd307d7b607c152408f99c8` |
| `0001018724-25-000004` / [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/R12.htm) | `88da40c406e1631592e431839d23f4691bb913268d8755c5a41ee0c9cca2af75` | `180944b46c73aa890adf1b960d3c77cf3852982dc9a4a83cf9cc5c6259733bd8` |
| `0001018724-26-000004` / [R3.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/R3.htm) | `3d14ddb9c153614e3446437f31dd5312f2e77ae18023c707af52c9b67d906628` | `98afcca778787e6f8e2c088cf7c951549be730eb4081e2e1fcaed75490697133` |
| `0001018724-26-000004` / [R10.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/R10.htm) | `270082b0cf8bdef12e8a6ced1ecb3c4520dfc349de9e70af653d8cbcc29d4db5` | `d0430593f8496a5ebc7a97197c5cd5059778670cc19c70e2f4bd3e1b3b71e293` |
| `0001018724-26-000004` / [R12.htm](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/R12.htm) | `e2a917de95d5912962f252eadbb139d88761123f8a848566003a846529c93be1` | `4e66adb1da6f33b63d7d6967985485648d0458c2cbcf7afe8e8afb005f794c5e` |

## Implementation and provenance

`normalization.capex_scope` and its immutable registry compose narrowly with
historical normalization. Corpus retrieval gets mandatory artifacts only for
exact registered entries. All raw-body hashes, mandatory review records and
the source instance re-parse must verify before approval; no SEC retrieval in
the resolver, generic parser change or automatic concept fallback.

One eligible semantic signature may resolve only at the reviewed exact value.
Equivalent context/unit IDs or lexical Decimal representations may confirm;
all occurrences survive in deterministic order, not a set or sum. Different
eligible values remain ambiguous. Exact filing/period/QName/entity/USD and
nondimensional scope are required; nil/numeric collisions, broken links and
inconsistent metadata are data errors. Missing, future/amended and unregistered
evidence receives no implicit approval. Direct ambiguity is never repaired;
equal direct selection retains precedence and supporting policy provenance.

Schema **5** extends standardized policy references with a separate Capex
review/support/exclusion audit without changing schema-4 field meanings.
Normalized output and JSON serialization retain policy/version, entry, reviewed
locations, artifact digests, both representation correction/refresh histories,
exact numeric strings and confirming multiplicity. Consecutive confirming
ordinals and original zero-based instance ordinals remain distinct. Supporting
relationship/asset-scope evidence is review support, not extra operands.
ETR, Operating Tax and NWC gain no invented dependency. Historical resolution
is not certification of future integrated FCFF/tax/lease/timing readiness.

## Verified gates and production reconciliation

| Gate | Result |
| --- | --- |
| Focused policy/integration/output/provenance/adversarial tests | 160 passed, including representation and refresh rejection tests |
| Frozen inventory regression | Ten AMZN/LLY positives resolve; all 47 controls retain baseline missing states |
| Targeted selected-accession run | Ten Capex resolutions; other normalized metrics unchanged; 71 resources reused / 51 requests |
| Complete suite | 569 passed; initial run exposed one stale smoke-runner mock missing the new empty Capex bundle argument, corrected and revalidated with a clean run |
| Single corpus reconciliation | 43/43 generic completions, seven specialized skips, 204 annual periods, no execution failures |
| Capex | 147/57/0 → **157 resolved / 47 missing / zero ambiguous**, exactly ten changes |
| Aggregate | **1,895 resolved / 1,493 missing / 11 ambiguous / 27 methodology-blocked / 42 not-comparable = 3,468** |
| Other outputs | Issuer-level measure-state counts match retained baseline except the ten Capex changes; 1,622 other normalized historical metric results unchanged; all 47 controls also checked live |
| Final checks | `compileall`, local documentation links and `git diff --check` pass |

The corpus used 348 retained resources and 297 new requests; no second corpus
run. Validation-only retention is outside repository runtime infrastructure.
Logs and reconciliation artifacts are in `/tmp/capex-wave28-*`. No push.

## Next bounded milestone

Research the five frozen CVX cash PP&E component candidates' acquisition/asset
containment. Their supplemental cash-flow components are promising but remain
unapproved; prove gross cash PP&E scope independently before designing any
acceptance. Do not map aggregate productive-assets spending, include affiliate
investment/dry-hole amounts, infer zero or derive a residual. The other 42 Capex
gaps and specialized GE perimeter work stay outside that bounded research pass.
Valuation/FCFF implementation remains paused through the Phase 1H.6 freeze.
