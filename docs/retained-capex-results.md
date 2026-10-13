# Retained cash-Capex preparation — existing approvals only

Historical result of the initial retained-only pass. The subsequent fixed
[artifact repair](capex-binding-repair-results.md) adds ten resolutions in a
[separate ledger](repaired-capex-ledger.json); this original ledger stays unchanged.

Phase 1 only. [199-period ledger](retained-capex-ledger.json); offline replay:
`PYTHONPATH=src .venv/bin/python scripts/inspect_retained_capex.py`.
Builds on unchanged [tax/SBC histories](retained-tax-sbc-results.md) under the
[historical-input contract](dcf-input-contract.md). No SEC requests, new financial
scope, equation, policy/registry entry, valuation calculation or issuer research.

## Actual period outcomes

| Outcome | Periods |
|---|---:|
| Existing direct policy replayed | 145 |
| Existing curated policy replayed | 5 (Visa v3) |
| Registered approval cannot replay retained evidence | 15 |
| Unapproved broader scope | 34 |
| Conflicting approved values | 0 |
| Other unavailable | 0 |
| **Selected periods** | **199** |

145 direct + five curated = **150 populated preparation periods**, not complete
reinvestment or financial sufficiency. All 42 non-specialized issuers are mapped;
XOM remains empty, GEV/SNDK have two annuals, eleven target-year deficits remain.
All eight specialized issuers, including GE, are excluded. Frozen Capex remains
167/37/0 (147 direct + twenty curated); two of its direct results and three
missing periods belong to excluded GE. This pass can replay 145 direct and five
of the twenty curated entries: **no frozen values are copied to fill gaps**.

## Direct policy replay and truthful filing provenance

Only existing `CAPEX_POLICY` / `PaymentsToAcquirePropertyPlantAndEquipment`
semantics are accepted directly. That existing policy has **no published version**;
provenance retains an explicit null version/unversioned status, not an invented
financial-policy v1. Shared inspection verifies original response-body/receipt,
selected accession/CIK/10-K and annual-DEI identity, exact nondimensional SEC
entity context, USD currency, raw representation and precision.

The unchanged historical numeric resolver consumes Company-Facts-shaped
selection records. This adapter projects exact **integer USD signatures** into
that selector internally, not into a fictional SEC Company Facts receipt.
Unknown filing-date/fiscal metadata remain null in the ephemeral projection;
no date, frame or receipt is invented. Equal numeric representations are one
selection signature, with all original occurrences and differing precision kept
in input sources/alternatives. Unequal eligible values remain ambiguous. The
selector's transient Company-Facts-labelled evidence is replaced with actual
filing-XBRL evidence; **all delivered sources are retained filing evidence**.
No float conversion; fractional USD that cannot pass the unchanged selector
exactly remains an explicit evidence error. This restriction did not affect
any actual populated period.

Only accepted payment magnitudes normalize to negative cash outflows
(`scale=1`, `sign=-1`), retaining raw positive values and original decimals.
Reported zeros may remain zeros; absence is never zero. A negative payment
magnitude cannot be turned into an asserted outflow by absolute-value arithmetic.
Source sign/dimensions/date/currency errors never acquire financial approval.

## Curated versions and mandatory evidence

Immutable published catalog and existing `verify_capex_artifacts`, annual resolver,
`apply_curated_capex_scope_policy` and provenance/output validators are reused.
Exact entries retain CIK, accession, form, filing metadata, annual dates,
namespace/concept/unit, scope, expected value, reviewed evidence, all confirming
occurrences and the complete existing policy audit. The reviewed expected amount
is checked against actual operands, not imported as an input value.

| Existing approvals | Successful replay | Evidence gaps | Version |
|---|---:|---:|---|
| AMZN five / LLY five | 0 | 10 | immutable v1 |
| CVX five | 0 | 5 | immutable v2 |
| Visa five | 5 | 0 | immutable v3 |

All five Visa entries verify their thirteen mandatory raw-artifact digests and
seven reviewed evidence records; original artifact byte lengths and instance
parsing are rechecked. The exact approved operational-software perimeter is
retained only for those registered entries, never generalized to other issuers.
Policy audit ordinals and original XML-root occurrence ordinals are both retained
in their original conventions, not silently interchanged.

The fifteen gaps are **85 required original-artifact bindings**, listed individually
with exact URL, registered typed digest, missing reason and any retained
alternative representation in the ledger. AMZN: six each (30), LLY: eight each
(40), CVX: three each (15). Registered fingerprints are not bypassed, relabeled or
replaced. Canonical review metadata/digests alone do not prove an absent body.
Available original bodies are read only from documented committed collections;
no undocumented temporary-cache search or recreated XML/JSON response.
Missing original retrieval time/status in support-artifact records stays explicit:
raw-byte verification is not recovery of original metadata. Monetary instance
sources keep their actual verified receipt metadata. No synthetic attestation is
used for this preparation replay; existing selection-only adversarial fixtures
remain tests, not production evidence.

## Unapproved/support populations and scope limits

The 34 unapproved periods are NVDA five, LRCX five, MRK 2021–2022, HD five,
GEV two, QCOM five, VZ five and PEP five. They remain financial-scope requirements,
**separate from the fifteen already approved entries' evidence defects**.
Broader productive/other-PP&E/software/intangible captions remain support-only.
NVDA's issuer-extension combined caption is retained explicitly, not accepted
through local-name similarity. No component subtraction or inferred zero.

The closed support mapping retains cash-purchase alternatives separately from
noncash lease additions, capital creditors, financing lease/principal payments,
acquisition consideration and asset-sale proceeds. Annual USD support values
retain **raw signs (+1), not asserted cash-Capex contribution signs**; they cannot
substitute or be summed. Selected exact curated operands are not relabeled as
unapproved replacements. Instant debt/creditor/noncash balances remain diagnostic
records with exact dates/units/contexts, not fabricated annual input values.
Diagnostics and full scope/policy payloads survive separate serialization flags;
annual support alternatives retain original-body SourceReferences. No generic
software acceptance, net/gross adjustment or complete reinvestment claim.

## Preservation, validation and next bounded step

Only nonpilot Capex inputs change. All four original pilot annuals/serialized
outputs stay verbatim, and their payment values are independently replayed.
Income, CFO, working-capital, tax/SBC and all other prepared fields remain exact;
frozen schema 5, policies/registries, corpus 1905/1483/11/27/42 across 3468 states,
classifications, blockers and history exceptions are unchanged. Financial
sufficiency and timing readiness remain unassessed; no automatic blocker removal.

Focused tests cover real direct/curated replay, all applicable versions and
mandatory missing-body gates, exact scope/period/entity/unit/precision, duplicates,
conflicts, payment signs, noncash/combined support exclusions, actual XML values,
policy/source serialization and prior-field/pilot/frozen preservation.
**66 unique focused tests pass:** eight new preparation/representation checks
and 58 existing v1/v2/v3/shared regressions. The final representation guard
rejects missing/parsed-body labels without relabeling; actual retained catalog
types/digests verify unchanged. Offline ledger replay, 199 identities/42 issuer
mappings, eleven history exceptions and 85 deduplicated registered requirements
reconcile. Compileall, 1,976 affected local links and diff checks pass.
No full suite/corpus rerun or SEC requests.

**Stop after Capex. Next bounded step, only with authorization:** fixed raw-evidence
repair for the fifteen already approved AMZN/LLY/CVX entries, using the ledger's
85 exact URL/digest requirements. Acceptance requires the registered original
representations and unchanged resolver gates; unavailable or differing bodies
remain gaps unless separately authorized/reviewed. No new financial research,
registry edits or scope expansion. D&A remains a separate retained-policy/timing
integration milestone; these evidence defects must not be disguised as denial.
