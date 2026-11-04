# Company cash-flow resolutions

## Current Apple analyst-ready outputs — November4,2026

[Apple five-output acceptance](AAPL/analyst-ready-2026-11-04/report.html) implements the user's revised reasonable-assumption standard. All five Apple outputs are analyst-ready with qualifications, including generated FCFE financing and both share values. Sources/legacy unknowns remain immutable; exact historical FCFE is not claimed. META/Alphabet are unchanged and remain separately open. Earlier blanket Apple OPEN claims below are preserved dated evidence assessments and are superseded for this named analyst contract.

## Apple ordered remaining-issue run — November4

[New Apple report](AAPL/remaining-issues-2026-11-04/report.html) distinguishes four executed treatments from unresolved financial evidence. Tax/NWC policy adoption and a coherent dated share-source population are recorded; financing/expense/claim/award completeness remains OPEN. Source, test, fresh-runtime and UI checks do not turn provisional FCFE into verified cash. Existing three-company amounts and forward policies are unchanged.

## Current Apple historical consumer — November 4

The [five-year operating-method adoption](AAPL/operating-fcff-2026-11-04/report.html) resolves the current Apple FY2024/25 FCFF display gaps under an explicitly qualified standardized methodology, consistently replacing all five years. Current three-company selected-method counts:15FCFF+5consolidated FCFE available under stated conventions;10provisional FCFE;0selected-method FCFF gaps. The old18/10/2 counts and17strict failed cells below describe earlier scopes/bases and remain preserved. Tax/Other conventions,355M D&A qualification and legacy CFO nulls are explicit. Overall company reviews remain OPEN.

## Four-step execution — November 4

The [implementation report](execution-2026-11-04/report.html) records five exact
Apple operating/cash reconciliations, ten provisional Apple/Meta financing
workpapers, Alphabet ownership/value separation and an additive API/UI readiness
contract. The user approved running these four steps in succession. No financial
amount changes: 18 stated-convention calculations are available, 10 remain
provisional and 2 lack required FCFF inputs. All three financial reviews remain
OPEN; the original 17 strict failed cells remain unchanged.

## Latest research — November 4

The [online notes/commentary follow-up](commentary-research-2026-11-04/README.md)
adds fifteen Apple target-history quarterlies, nine later comparative quarterlies,
Alphabet's proxy and twenty-two public SEC correspondence documents. It records
the evidence limits and preferred next treatments. No cash-flow amount, numerical
method or completion status is changed; issuer and combined reviews remain OPEN.

## Latest approved execution — November3

All18preferred treatments are approved. See the [execution log](implementation-2026-11-03/implementation-log.json), [current platform projection](implementation-2026-11-03/platform-cashflows.json), and [independent review](implementation-2026-11-03/independent-review/findings.md). The platform exposes qualified five-year FCFF/FCFE history plus a separate manual financing/FCFE forecast. New research does not overwrite prior ledgers or fabricate missing data. Full financial clearance remainsOPEN; earlier per-milestone integration statements retain their original date/scope.

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
| Apple (AAPL) | FY2021–FY2025; Other financing, FY2021 stock-proceeds presentation, alternative FCFF route and tax separation | Five standardized operating FCFF values available after November4 adoption; old CFO gaps preserved; five FCFE values remain provisional; broader financial review OPEN | [Apple decisions and results](AAPL/README.md) |
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
