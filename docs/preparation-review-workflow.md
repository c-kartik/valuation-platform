# Bounded Phase 1 preparation/review workflow

The [input contract](dcf-input-contract.md), [source assembly](prepared-assembly-results.md)
and [local analyst audit](analyst-override-review-controls.md) remain unchanged.
This milestone validates preparation mechanics, not financial sufficiency or
issuer coverage. No new extraction, treatment, assumption or acceptance is registered.

[Reproducible counts](preparation-workflow-summary.json): 42 histories / 199
annuals. Full: 2,786 primary items, 8,308 nested actionable / 1,575 nested
informational causes and 17,602 original annual diagnostics, including eight
invalid-evidence locations. Three history-exception cards remain separate
(eleven target-year deficits), yielding all original 17,605 cards. Every current
field slot has an actionable retained requirement; populated values do not
silently remove those requirements. Latest: 574 primary items across 41 nonempty
histories, 1,701 actionable / 325 informational causes and 3,527 annual diagnostics,
including one invalid-evidence location. Seven older invalid locations are
explicitly counted outside latest views, not resolved or discarded.

## Analyst-facing presentation

`analyst/preparation_review.py` adds one primary item per canonical issuer/exact
selected accession/field family with an actionable cause. Its ID is the existing
stable field target. Component targets keep the existing override IDs, original
input identity, binding category, dates/classes, precision, sources and alternatives.
Distinct causes reference verbatim original diagnostics nested once per item;
their original source/alternative/refresh payloads remain reachable. Causes are
not the count of required financial inputs, and component counts are not completeness.

Informational-only fields remain in `informational_fields`; history-exception
groups stay outside annual field items. XOM has no annual item. Neither section
clears requirements or approves complete balances. A single unambiguous field
target is not permission to override scope/date/class or invalid evidence.

`full` covers every selected annual; `latest` uses the newest registered annual,
not the newest period with a problem and not a newer SEC filing. Both use field
importance ordering, then newest annual. Latest explicitly reports full-history
and outside-view counts, including older invalid-evidence diagnostics. Switch
to full for the omitted detail; no warning is silently discarded. No score,
confidence threshold or automatic resolution is introduced.

`inspection_payload()` displays **original** and **effective** entries separately.
Effective means the original or an explicitly applied analyst patch, not an
economically adjusted or certified value. Source quality and queue requirements
remain unchanged when a patch applies. Patches retain displaced originals,
alternatives/evidence, completeness and unresolved requirements. Missing
acknowledgments do not fill inputs. Stale decisions apply no value until an
explicit revalidation event; nothing modifies the original source/ledger.

## Read-only local entry point

Existing `scripts/assemble_prepared_inputs.py` now supports:

```sh
PYTHONPATH=src .venv/bin/python scripts/assemble_prepared_inputs.py --ticker MSFT --view latest --section queue
PYTHONPATH=src .venv/bin/python scripts/assemble_prepared_inputs.py --ticker GOOG --view full --section quality
PYTHONPATH=src .venv/bin/python scripts/assemble_prepared_inputs.py --ticker WMT --section bundle
```

Default no-argument behavior still replays/checks the existing assembly summary.
Ticker inspection reuses the retained assembly builder, which can take several
minutes; no network request or new acquisition. `--prepared /path/to/payload.json`
can replay an existing separate assembled payload without rebuilding all issuers;
its typed provenance, retained ledger seals and overlays are validated normally.
No automatic cache or new persisted financial store. `--store /path/to/audit`
reads an existing local audit for original/effective comparison; it cannot create
decisions and rejects a missing directory. `--section all` includes bundle,
full-history quality, selected queue and separate audit overlay. Alphabet aliases
address one issuer, not equivalent share classes. Output is deterministic JSON
for a fixed source/audit/view; actual event times intentionally differ across
independent synthetic decision sessions.

## Bounded end-to-end cases

[Exact executed case identities/targets](preparation-workflow-cases.json):

| Issuer | Exact selected accession | Annual end | Exercised source |
| --- | --- | --- | --- |
| META | 0001628280-26-003942 | 2025-12-31 | Direct Revenue |
| MSFT | 0001193125-26-323660 | 2026-06-30 | Approved derived D&A |
| WMT | 0000104169-26-000055 | 2026-01-31 | Conflicting Revenue remains null |
| Alphabet | 0001652044-26-000018 | 2025-12-31 | One class-bound shares observation dated 2026-01-28; not an issuer total |

Periods/targets are chosen from materialized retained bindings, not invented years:

- META: latest eligible direct Revenue.
- MSFT: latest eligible approved derived D&A, with retained formula/operands.
- WMT: latest conflicting Revenue, preserving null and competing alternatives.
- Alphabet: latest eligible separately dated/classed share observation, not a total.

Tests exercise assembly → source/review payload → explicitly synthetic proposal/
acceptance → temporary audit persistence/restart → separate overlay → in-memory
source revision change → stale rejection → explicit synthetic revalidation →
closed overlay round trip. Source views are never re-registered and no receipt,
ledger or financial amount is edited. Source/ledger validation, retained formula
dependencies, partial components, conflict alternatives, date/class dimensions,
missing acknowledgments, deterministic grouping and pilot/frozen preservation
remain explicit assertions. Only temporary synthetic assumptions/decisions exist.

The initial new test lookup used input ID alone, which can repeat across annuals.
It was corrected to exact selected period **plus** input ID; the focused run was
restarted after interrupting its large assertion-diff formatting. Production
target IDs/matching already include accession and required no selection change.
No source amount, policy, receipt or ledger was changed to obtain a pass.

Verified result: **28 focused tests pass** (nine assembly, fourteen override and
five new workflow tests; the latter cover all four retained cases). Persistence/
restart, current/stale revisions, explicit synthetic revalidation, overlay round
trips, original/effective separation, null acknowledgment and complete diagnostic
membership pass. Existing assembly regressions pin original pilot bytes, retained
ledgers/evidence, financial policies/models and frozen outputs. Compileall,
affected local links, forty-plus-two mappings, count/reproducibility and diff
checks pass. No SEC requests, full-suite/corpus rerun or real decision store.

## Independent validation and closure boundary

This closes the authorized **mechanical end-to-end validation** pass, subject to
the recorded focused results; it does not automatically close analyst-reviewable
financial preparation. Evidence-accounted qualified closure and frozen support
classifications are unaffected.

Remaining finite gates: independent source/financial-input spot checks against
the delivered ledger references (including material conflicts/partial scope),
explicit field/recent-versus-older coverage denominators and user disposition of
material shortfalls against the proposed targets. Any actual analyst decision
requires identity/provenance, rationale and same-milestone issuer maintenance.
Financial sufficiency and timing/consumer readiness remain separate NOT_ASSESSED
gates; Phase 2 is still prohibited. No new issuer research or automatic acquisition
follows this workflow test. Stop for user review before any acceptance milestone.
