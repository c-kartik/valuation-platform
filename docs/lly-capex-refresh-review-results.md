# LLY Capex: fixed retained report refresh disposition

Phase 1 only, baseline `6e9634c3b3c5c11228c3e1e3c207a848367e66d8`.
The user authorized independent review of only the fifteen already-retrieved
reports. **Zero SEC requests.** No financial approval, registry fingerprint,
frozen schema or output changed.

## Decision

All fifteen refreshed reports support the existing five financial-scope
decisions. **Five content reviews supported; zero entries activated; five
operational bindings remain blocked.** This is not a financial rejection.

The immutable v1 verifier requires `entry.artifact_digests` exactly. Its resolver
requires that same attestation; its output validator requires the original
`reviewed_evidence`, `reviewed_entry_json` and `verified_artifact_digests` exactly.
See [implementation](../src/valuation_platform/normalization/capex_scope.py) and
[audit model](../src/valuation_platform/normalization/models.py). It has no
separate evidence-generation/refresh reference. Fresh digests cannot be truthfully
serialized as verified historical digests. A new financial policy is unnecessary
on these findings, but **a different provenance/schema treatment is necessary**.
Per the explicit stop condition, none was implemented or silently substituted.

The additive, versioned [review record](evidence/lly-capex-refresh-review-v1.json)
binds every old fingerprint to its exact entry, report type/role/URL, actual new
receipt/digest/time/status, cited observations and requirement dispositions.
It is review evidence, **not** a `VerifiedCapexArtifacts` attestation or an
activated approval. Its version does not replace financial policy v1.
The existing [receipt/mismatch ledger](evidence/capex-binding-repair.json) and
all old fingerprints/statuses remain unchanged.

## Historical-body check

One bounded retained-source check searched the 73 committed JSON sources and
their explicit retained paths; the versioned record pins the complete source
snapshot and digests. **Zero historical-body matches**; thirty matching-fingerprint
references lack original bodies (including repeated ledger references), with no
additional explicit body paths. Retained sources are exhausted for this pass.

Historical byte equivalence **cannot be established**. These reports' actual raw
SHA-256 values differ from the registered fingerprints. Matching amounts or
captions do not establish renderer-only changes, text equivalence or historical
body identity. No cause of the byte differences is inferred. New receipts retain
their original acquisition metadata; this review neither creates requests nor
claims to recover old metadata.

## Independent five-period findings

| Selected accession | Annual period | Displayed PP&E purchase outflow, USD millions | Refreshed reports | Content / operational disposition |
|---|---|---:|---|---|
| `0000059478-22-000068` | 2021-01-01–2021-12-31 | (1,309.8) | R9 / R11 / R19.htm | Supported / blocked |
| `0000059478-23-000082` | 2022-01-01–2022-12-31 | (1,854.3) | R9 / R10 / R18.htm | Supported / blocked |
| `0000059478-24-000065` | 2023-01-01–2023-12-31 | (3,447.6) | R9 / R10 / R18.htm | Supported / blocked |
| `0000059478-25-000067` | 2024-01-01–2024-12-31 | (5,057.8) | R9 / R10 / R18.htm | Supported / blocked |
| `0000059478-26-000013` | 2025-01-01–2025-12-31 | (7,841) | R9 / R10 / R18.htm | Supported / blocked |

The review separately reads the current annual cash-flow column, its exact
`PaymentsToAcquireOtherPropertyPlantAndEquipment` caption/concept link, investing
section, parentheses outflow sign and USD-million scale. It then verifies the
unchanged selected instance's authoritative annual DEI, exact namespace/context,
CIK, nondimensional USD unit, positive magnitude, occurrence and decimals against
the original entry. 2021–2024 precision is `-5`; 2025 is `-6`, not an extra digit
inferred from earlier comparative columns. Seven unchanged non-report requirements
per entry remain byte-bound; only three reports per entry are under refresh review.

| Requirement | Independent support / limitation |
|---|---|
| Consolidated cash purchase scope | Current consolidated investing cash-flow caption plus accounting-policy consolidation and intercompany-elimination passages; not a balance movement, residual or net investing subtotal. |
| Physical PP&E perimeter | Cost-basis PP&E note and land/buildings/equipment/construction categories, not numerical agreement alone. |
| Acquisitions and IPR&D excluded | Separate acquisition/IPR&D cash rows plus acquired-IPR&D accounting policy. No acquired balances, rights or licensing cash added. |
| Leases/software/noncash excluded from substitution | Broader long-lived assets expressly include operating-lease assets and other noncurrent assets (2021–2022), or unamortized software (2023–2025). Those broader populations, noncash additions, creditors and principal are not operands or additions. No inference that undisclosed amounts are zero. |
| Reported gross cash, not hypothetical pre-incentive investment | Preserve the independently identified purchase outflow. Separate investment/product-rights proceeds, incentives, noncash/accrued costs and financing populations are not netted, grossed up or allocated. Complete incentive/noncash allocations remain unverified and are not required by the existing reported-value approval. |
| Capitalized interest | 2021–2024 PP&E notes say not material, not zero. 2025 amount is undisclosed in these reports. No interest adjustment; completeness of capitalized interest remains unverified. |

**No financial-scope contradiction found.** The operational assertion that the
fresh bodies satisfy the original registered report fingerprints is false;
historical byte equivalence and the cause of differences remain unverified.
The 2023 accounting-policy note reclassifies prior IPR&D development-milestone
cash between operating/investing categories. This is retained as a comparability
limitation; selected current-year PP&E remains separate. No later comparative
substitution, IPR&D equation or CFO correction is authorized.

## Replay, preservation and stopping point

The unchanged policy rejects fresh digest attestations for all five entries.
No successful normalized value or provenance is manufactured. The unchanged
[199-period coverage ledger](repaired-capex-ledger.json) therefore remains:
**145 direct + fifteen curated + five evidence gaps + 34 unapproved scope**;
**160 populated**, zero conflicts. All 160 inputs, other fields, pilot outputs,
frozen registries/policies/schema 5 and corpus artifacts stay exact. Financial
sufficiency and deferred timing/coverage limitations are unchanged.

Offline review replay:
`PYTHONPATH=src .venv/bin/python scripts/validate_lly_capex_refresh.py`.
Focused checks cover old/new receipt identity, all five independent report/operand
reviews, wrong amount/date/caption/scope, unsupported refreshes, v1 rejection,
review-record serialization and prior input/policy preservation. No full-suite
or corpus rerun.

Validation passed: **29 unique focused tests** (six review, six existing binding/
offline replay and seventeen v1 policy tests), including the updated output-
provenance rejection check rerun. Compileall, all 310 affected local links and
staged/unstaged diff checks pass. All fifteen receipt/old-new pairs, five annual
operand bindings and unchanged 199-period ledger reproduce offline.

**Stop.** Remaining prerequisite is an explicitly authorized additive evidence-
generation/provenance contract that can distinguish the unchanged financial entry
from approved replacement report bytes, enforce the exact reviewed fifteen pairs,
and serialize/revalidate both generations without falsifying historical hashes.
It needs no further SEC acquisition or new financial research on these findings.
This milestone does not implement or preapprove that schema treatment.
