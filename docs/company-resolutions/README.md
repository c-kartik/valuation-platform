# Company cash-flow resolutions

This is the durable record of manually reviewed FCFF/FCFE issues, treatments,
evidence and number changes. The user requested it on November 3, 2026 so future
filing updates can reproduce each decision. It complements the existing
[company-preparation register](../company-data-preparation/index.md); it does not
replace original filings, accepted histories or approval records.

**Overall status: OPEN for Apple, Meta and Alphabet.** Approved treatments have
been implemented within their recorded scopes; unresolved financial, methodology
and platform-integration roadblocks remain. The current
[open-roadblock register](OPEN-ROADBLOCKS.md) lists each known item, its effect,
preferred proposed treatment and closure evidence. No company or development
scope is complete while a roadblock remains. Passing checks must be named
individually rather than represented as overall completion.

| Company | Review scope | Current outcome | Record |
| --- | --- | --- | --- |
| Apple (AAPL) | FY2021–FY2025; Other financing, FY2021 stock-proceeds presentation, alternative FCFF route and tax separation | One presentation conflict resolved; five FCFE values reconciled but provisional; operating FCFF input alignment remains unresolved; no platform number changed | [Apple decisions and results](AAPL/README.md) |
| Meta (META) | FY2021–FY2025; five approved financing/investment/interest/tax treatments | Net investment changes chart FCFF+245m/+221m in2022/23; FCFE provisional; Other unresolved | [Meta decisions and results](META/README.md) |
| Alphabet (GOOGL) | FY2021–FY2025; NCI scope and lease containment | Consolidated FCFE labeled before NCI; parent-common cash missing; FCFF unchanged; leases counted once | [Alphabet decisions and results](GOOGL/README.md) |

## How each company is recorded

Use the [company template](TEMPLATE.md) and a separate ticker folder. Keep stable
issue identifiers. Record the original issue (a missing disclosure need not be a
software error), considered treatments, the approved treatment and why, exact
filing/period/caption/cell references, reproducible arithmetic, before/after values,
tests and remaining limitations. Distinguish reported facts, derived calculations
and analyst assumptions. Include the user approval and its scope.

Three different states must stay separate:

1. **Treatment approved:** the user agrees with the method or investigation.
2. **Evidence reconciled:** the required inputs and classifications are supported.
3. **Published:** the justified result is adopted by a named platform consumer.

An approved treatment does not turn an unknown amount into zero or make a method
test verified FCFF. A complete cash-statement sum does not classify each component.
Keep blocked or provisional results visible rather than fabricate closure.

## Updating a company

1. Retain the new SEC response with its URL, original-byte hash and receipt.
2. Record exact fiscal dates and source-versus-target dates for comparatives.
3. Review changed captions, tax/lease/ownership/investment scope and source mappings.
   Do not carry a policy into new periods merely because the ticker is unchanged.
4. Replay the existing record before changing anything. Preserve prior approvals,
   historical facts and results; create a new version when changing the basis.
5. Produce a proposed before/after schedule. Obtain manual review for decisions
   affecting numbers; identify the new approval and superseded decision explicitly.
6. Update the affected preparation record, methodology/status documentation and
   tests alongside any supported consumer change. Do not clear missing inputs by
   acceptance alone.

Current offline replay:

```sh
PYTHONPATH=src .venv/bin/python scripts/resolve_apple_cashflows.py --check
PYTHONPATH=src .venv/bin/python scripts/resolve_meta_alphabet_cashflows.py --check
```

The script reads retained repository evidence, not files in a chat's output
directory, and makes no network request. `--check` never writes. After reviewing
an intentional source/decision change, `--write` regenerates the separate JSON/CSV
resolution record. Meta also emits a separately pinned approved investment
overlay consumed by the historical display wrapper; neither replay edits forecast
assumptions or automatically publishes FCFE. Apple and Alphabet records do not
change chart amounts. See each company for its explicitly approved scope.
