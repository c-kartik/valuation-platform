# Isolated four-pilot historical-input adapter

**Subsequent additive delivery:** [direct Revenue/EBIT](pilot-direct-income-evidence.md)
now uses mapping version 2 and annual/history bundle version 2, with unchanged
model/serializer schemas. All eight reported totals are available; no other
field disposition or original source package changes. The version-1 adapter
results below remain the earlier delivery record, not current income availability.
Current scalar/null counts are 68/25, with nine D&A support observations; current
family dispositions are 8/1/5, 8/1/5, 7/1/6, 8/1/5. No readiness or new treatment.

2026-10-13; starting HEAD `31aa2ff615467146d4f1463450b0d3accd07d848`.
Phase 1 only. [Implementation](../src/valuation_platform/analyst/pilot_historical_inputs.py)
consumes the unchanged [committed mappings](pilot-historical-input-mappings.md)
and [matrix](pilot-historical-input-mappings.json), SHA-256
`d4afc39f1700c6189a43bc72d0be31058d167dbf010c493bcfc25cca433eac33`.
No financial treatment, mapping, model or frozen schema change.

## Delivered objects and restricted scope

`load_annual(original_bundle_id)` accepts only the four already registered
reported-input IDs. `load_history(issuer)` accepts only MSFT, AAPL, GOOGL; it
returns existing immutable `AnnualBundle`/`HistoryBundle` models, not new
registrations, generic ticker cascades or valuation inputs. No comparative
columns, future/amended filing approval or additional fiscal years.

| Period | Mapped / support-only / unavailable families | Top-level reported observations | Null required slots | D&A evidence-only observations |
| --- | --- | ---: | ---: | ---: |
| MSFT FY2025 | 6 / 1 / 7 | 16 | 8 | 3 |
| MSFT FY2026 | 6 / 1 / 7 | 17 | 8 | 3 |
| AAPL FY2025 | 5 / 1 / 8 | 12 | 9 | 1 |
| Alphabet FY2024 | 6 / 1 / 7 | 15 | 8 | 2 |

Counts are preparation structure, not financial sufficiency or primitive coverage.
Every annual includes all fourteen field families; component observations are
not summed. Short adapter histories have explicit scope exceptions: two MSFT
packages, one AAPL, one Alphabet, not claims that their selected histories are
short. Five-period target and three-period readiness target are unchanged.

### Faithful support-only representation using unchanged models

Each required D&A slot has `value=None`, origin unavailable, the mapping's limited
quality/restricted scope/partial completeness/reviewed status and exact unresolved
requirements. Its `alternatives` retain the separate reported source observations,
original roles/precision/requirements and source evidence. These are explicitly
flagged `support_only` and `non_substitutable_for_required_da_primitive`, **not
economically equivalent candidates or an approved alternative D&A amount**.
No selected primitive, numeric total or implied zero. This uses the existing
nullable input/alternative/flag fields, without changing the WP0 model contract.

All other unavailable families retain null reasons and requirements; no invented
share observation date. Missing bridge values have the contract's known fiscal
year-end target date, not a source fact. Placeholder sign/scale/precision on nulls
are flagged as non-observations. Available inputs preserve statement signs,
scale 1, original raw representations and separately named roles; cash PP&E is
a signed reported outflow, not an automatically chosen positive economic Capex.
SBC expense and CFO add-back stay separate with the same population key. Alphabet
22,800m rounded expense and 22,785m reconciliation keep −8/−6 precision; no charge
or rounding adjustment. CF movements never become book ΔNWC. Residuals remain null.

## Provenance and serialization

Source references retain exact period, namespace/concept, context, occurrence
ordinal, normalized unit, raw value, decimals, dimensions and verified original
instance receipt. The locator also retains original unit ID/nil status, original
reported-input kind, statement/note scope, registry identity/hash and mapping hash.
All confirming occurrences survive. CFO has an additional primary-statement
reference with no invented XBRL ordinal, preserving the original primary receipt.
Selection rationale/flags preserve mapping status, population and source role.
Annual limitations retain original bundle limitations, exact null-unknown records
and supplementary-input registry references; supplementary inputs are not promoted
into bridge/primitive values.

`serialize(history)` / `deserialize(payload)` use separate envelope
`pilot-historical-input-adapter-v1`, referencing unchanged model schema
`historical-input-preparation-v1`. Existing reported bundle serializers carry
original response bodies once per artifact as their existing gzip/base64 proofs.
The complete typed adapter metadata references those bodies by URL/digest rather
than repeatedly embedding the same large instance bytes in each source reference.
No new persistence store or body transformation/digest convention. No existing
serializer/schema is altered; generic WP0 serialization remains unchanged.

Deserialization verifies the native pinned proofs, rebuilds immutable models
from the same committed mappings, and compares the entire typed metadata snapshot
exactly, including JSON scalar types. Changed evidence, origin, role, sign,
precision, flags, nulls or requirements fail. Unknown periods/issuers, duplicate
JSON keys, extra source proofs or changed mapping bytes fail conservatively.
Alphabet's native proof preserves both original metadata gaps and the separately
identified refreshed receipt; refresh is not retroactive metadata recovery.

Only the original source loaders' existing reported CFO statement validation is
reused. The adapter performs no component/residual/ratio calculation, assumption,
override, economic adjustment or readiness decision. It never consumes these
observations for FCFF/forecasts/DCF or removes NWC/D&A/timing blockers.

## Validation, preservation and next bounded step

Focused tests exercise all four mappings, source/role/sign/precision fidelity,
unresolved requirements, D&A nulls/support evidence, exact deterministic round
trips, malformed/tampered evidence and original bundle proof preservation.
Existing model/mapping/pilot preservation checks are reused. Compileall, relevant
local links and `git diff --check` pass; no SEC requests/full suite/corpus.

Verified result: **58 focused tests passed**, including 15 new adapter tests,
16 committed mapping tests, 24 WP0 model tests and three original pilot-preservation
checks. All three histories/four annuals round-trip deterministically; unchanged
mapping validator retains its four independent reported statement checks.

Frozen schema 5, policies/outputs, original mappings, evidence, all pilot bundles,
scenarios and sidecars are unchanged. Baseline 1905/1483/11/27/42 = 3468 remains
retained, not rerun. Support classes, history exceptions and all original blockers
remain; financial sufficiency NOT_ASSESSED. Three issuer records explain this
delivery and its limits without transferring approvals to other companies.

**Next bounded step toward generic coverage:** one retained-source mapping design
for direct annual Revenue and EBIT in these same four exact selected filings.
Identify already retained evidence and required occurrence/scope checks, retain
unavailable/conflicting rows and stop at that fixed set. No component bridge,
new issuer/period, SEC retrieval or generic cascade until separately authorized.
This is a finite shared-field prerequisite, not forty issuer research cycles.
Stop after the present adapter milestone.
