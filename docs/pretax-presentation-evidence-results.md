# Pretax presentation-evidence diagnostic results

## Decision

Phase 1H.4 Wave 9 implements and live-validates the development-only diagnostic
designed in `pretax-presentation-evidence-design.md`. It attempted the frozen 33
standard-concept periods and emitted 33 typed results with no retrieval, annual-
period, fact-reconciliation, submitted-presentation, or renderer data errors.

The evidence-pattern decision is **NEEDS_MORE_RESEARCH**. All 33 candidate facts
belong to exactly one submitted `Statement` role and also to one or more
submitted `Disclosure` roles. They therefore classify as
`MULTIPLE_ROLE_MEMBERSHIP`, not as statement-only facts. Statement membership is
now proved for this corpus, but it still does not establish equity-method scope
or semantic equivalence to the current Pretax primitive. Safe new Pretax
resolutions remain zero; production policy and corpus totals are unchanged.

## Reproduction

Run the read-only command with an identifying SEC user agent:

```console
SEC_USER_AGENT='Valuation Platform contact@example.com' \
  PYTHONPATH=src .venv/bin/python \
  scripts/run_pretax_presentation_diagnostic.py \
  --output /tmp/pretax-presentation-results.json
```

The deterministic JSON preserves every discovered filing-directory filename and
URL, exact fact/context/unit/dimensions/value provenance, every submitted role
and ordered root path, Filing Summary reports, MetaLinks and applicable R-file
cross-checks, typed failures, the issuer matrix, and the policy decision. The
command exits nonzero if any period has `PRESENTATION_DATA_ERROR`.

The live run on 2026-10-08 reported:

- 33 periods and 33 unique frozen accessions attempted;
- 33 `MULTIPLE_ROLE_MEMBERSHIP` results and zero other presentation outcomes;
- 33 `EQUITY_METHOD_SCOPE_UNRESOLVED` gates;
- one submitted `Statement` role in every period;
- between one and three submitted `Disclosure` roles in every period;
- MetaLinks candidate membership and an applicable candidate-containing R-file
  in every period; and
- zero presentation data errors and zero safe new Pretax resolutions.

Deterministic validation includes 11 focused diagnostic tests. The complete
repository suite passes 472 tests; `compileall` and `git diff --check` also
pass.

Candidate-fact occurrence counts below exceed one where equivalent context IDs
confirm the same annual fact. The diagnostic preserves every occurrence and
requires one consistent `(value, USD unit)` signature; it does not choose the
first context.

## Period inventory

| Issuer | Report date | Accession | Exact fact occurrences | Statement roles | Disclosure roles | MetaLinks | R-file | Outcome |
|---|---|---|---:|---:|---:|---|---|---|
| AMZN | 2021-12-31 | `0001018724-22-000005` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| AMZN | 2022-12-31 | `0001018724-23-000004` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| AMZN | 2023-12-31 | `0001018724-24-000008` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| AMZN | 2024-12-31 | `0001018724-25-000004` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| AMZN | 2025-12-31 | `0001018724-26-000004` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MU | 2021-09-02 | `0000723125-21-000065` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MU | 2022-09-01 | `0000723125-22-000048` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MU | 2023-08-31 | `0000723125-23-000054` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MU | 2024-08-29 | `0000723125-24-000027` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MU | 2025-08-28 | `0000723125-25-000028` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MA | 2021-12-31 | `0001141391-22-000023` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MA | 2022-12-31 | `0001141391-23-000020` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| MA | 2023-12-31 | `0001141391-24-000022` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CVX | 2021-12-31 | `0000093410-22-000019` | 2 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CVX | 2022-12-31 | `0000093410-23-000009` | 2 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CVX | 2023-12-31 | `0000093410-24-000013` | 2 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CVX | 2024-12-31 | `0000093410-25-000009` | 2 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CVX | 2025-12-31 | `0000093410-26-000078` | 2 | 1 | 3 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CAT | 2021-12-31 | `0000018230-22-000050` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CAT | 2022-12-31 | `0000018230-23-000011` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CAT | 2023-12-31 | `0000018230-24-000009` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CAT | 2024-12-31 | `0000018230-25-000008` | 3 | 1 | 3 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| CAT | 2025-12-31 | `0000018230-26-000008` | 3 | 1 | 3 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| PM | 2021-12-31 | `0001413329-22-000011` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| PM | 2022-12-31 | `0001413329-23-000025` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| PM | 2023-12-31 | `0001413329-24-000013` | 2 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| PM | 2024-12-31 | `0001413329-25-000013` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| PM | 2025-12-31 | `0001628280-26-005939` | 3 | 1 | 3 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| LIN | 2021-12-31 | `0001628280-22-004180` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| LIN | 2022-12-31 | `0001628280-23-005434` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| LIN | 2023-12-31 | `0001628280-24-007424` | 2 | 1 | 1 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| LIN | 2024-12-31 | `0001628280-25-007990` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |
| LIN | 2025-12-31 | `0001628280-26-011430` | 3 | 1 | 2 | yes | yes | `MULTIPLE_ROLE_MEMBERSHIP` |

## Equity-method evidence matrix

This matrix originally recorded the evidence available at the end of Wave 9.
Wave 10 completed the exact-period note review linked below; the classifications
now reflect that evidence. Silence is never converted to
`NO_MATERIAL_ACTIVITY_FOUND`.

| Issuer | Candidate periods | Classification | Direct evidence | Decision |
|---|---:|---|---|---|
| AMZN | 5 | `SEPARATE_NET_OF_TAX` | All five filings bind investee activity to the separate net-of-tax statement line | Economically non-equivalent |
| MU | 5 | `SEPARATE_NET_OF_TAX` | All five statements separately present equity in investee net income/loss after tax | Economically non-equivalent |
| MA | 3 | `INCLUDED_PRETAX` | Each investment policy binds equity-method results to pretax statement lines | Issuer-specific evidence for later design |
| CVX | 5 | `INCLUDED_PRETAX` | Each filing directly places affiliate earnings before consolidated tax | Issuer-specific evidence for later design |
| CAT | 5 | `SEPARATE_NET_OF_TAX` | Each Statement 1 presents equity in unconsolidated affiliates after tax | Economically non-equivalent |
| PM | 5 | `SEPARATE_NET_OF_TAX` | Each statement places the combined equity-investment line after the tax provision; exact notes bind equity-method effects to it | Economically non-equivalent |
| LIN | 5 | `UNRESOLVED` | Corporate-investee income is after tax; partnership/LLC income enters Pretax | Stable mixed treatment; no single classification |

## Wave 12 production follow-up

Wave 10 completed the exact-period note research and Wave 11 approved only a
curated exact-accession policy design. Wave 12 now implements that design for
the eight `INCLUDED_PRETAX` MA/CVX facts. It does not convert the presentation
diagnostic into automated discovery or change the generic Pretax concept
policy.

The production duplicate diagnostic confirmed that each MA eligible fact has
three semantically identical same-context occurrences. Each CVX eligible fact
has two semantically identical nondimensional occurrences plus distinct
dimensioned facts that remain excluded. The curated resolver applies the same
one-consistent-signature principle already used here: context IDs, exact-USD
unit IDs, raw strings, and decimals may differ only when all normalized semantic
fields and the exact `Decimal` value agree. Every original occurrence and its
deterministic ordinal remains in provenance and serialization.

Targeted live validation resolves all eight Pretax and all eight corresponding
Reported ETR periods. The full 33-period regression resolves exactly the eight
`ALLOW` facts and leaves all 25 controls missing; the 12 ORCL/MCD/PG extension
periods remain unchanged. Full-corpus Pretax and Reported ETR each reconcile to
167 resolved / 37 missing / 0 ambiguous. The complete suite passes 491 tests.

The next milestone is selected-filing face-statement research for the 35
missing Operating Income periods. It is research only; no new policy is yet
approved.
