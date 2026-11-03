# Approved pilot FCFF/FCFE implementation and independent review

**Overall status: OPEN. Full requested financial availability review: FAIL.**

The user approved all 18 preferred treatments and required an independent review
of Apple, Meta and Alphabet over FY2021–FY2025. Approval and executed actions are
retained in [approval](approval.json) and [implementation log](implementation-log.json).
A disclosure gap is distinguished from a software error, and cannot be fixed by
inventing an amount or changing its status label.

| Company | FCFF under adopted reported-cash convention | FCFE review calculations | Parent-common FCFE clearance |
| --- | --- | --- | --- |
| Apple | 3 available; FY2024/25 gross interest missing | All 5 present, provisional financing scope | None cleared |
| Meta | All 5 available | All 5 present, provisional Other financing scope | None cleared |
| Alphabet | All 5 available | All 5 available as consolidated before minority allocation | Annual parent attribution missing |

Thus13 of 30 strict FCFF/parent-common FCFE cells pass the named historical
contract; 17 remain blocked. This does not mean Alphabet's consolidated FCFE
calculations are absent. They are visible with their actual ownership label.
Amounts derive from rounded filing figures and a stated tax convention; they are
not a separately reported audited FCFF line item.

## Implemented work and traceability

- [Apple](../AAPL/implementation-2026-11-03/README.md): later annual comparatives,
  financing, expense/D&A, investment presentation and tax schedules.
- [Meta](../META/implementation-2026-11-03/README.md): complete quarterly financing
  review, interest scope, capitalized-interest cash limits and recurring-tax policy.
- [Alphabet](../GOOGL/implementation-2026-11-03/README.md): ownership, VIE, Waymo
  funding and lease cash/noncash timing schedules.
- [S1 partial basis bridges](basis-bridge/decision-log.json):15 exact CFO less
  reported SBC add-back diagnostics. Remaining noncash/tax/investment/ownership
  differences prevent full valuation alignment. Historical published values stay
  unchanged. [Executed tax-policy parity](basis-bridge/valuation-parity.json)
  covers12 actual valuations and six zero-difference before/after pairs.
- [S3 share and claims source schedules](share-bridge/README.md):171 source
  observations. Gross cash, debt carrying amounts, share counts and award counts
  remain separate from reviewed eligible assets and valuation deductions.
- S2: explicit manual forward financing and FCFE calculation, separate cost-of-
  equity discounting, stable-capital-structure terminal, bounded API and UI.
  Independent leverage/debt-growth/lease/tax tests pass the software contract.
  Issuer economic inputs and ownership are not thereby certified.
- S4: a [versioned projection](platform-cashflows.json), read-only
  `/api/v1/cashflows/{ticker}`, Cash flows UI, JSON export and current report.
  Full historical ownership/input clearance remains open.

## Independent review

[Findings](independent-review/findings.md) and the
[integrated verdict](independent-review/integrated-verdict.json) distinguish
source arithmetic, exact statement financing population, extended evidence,
software correctness, current bundle pins, API and browser publication from
financial availability. The independent source checker does not import the
production verifier or cash-flow calculator. Separate forward-model reconciliation
uses independent expected values and actual isolated API execution.

The immutable November2 42-company snapshot is retained; this is the current
three-company result. Do not label any company or the development scope complete
while the [roadblock register](../OPEN-ROADBLOCKS.md) retains unresolved evidence,
methodology, valuation or development work. No broader universe is approved here.

## Reproduction

```sh
PYTHONPATH=src .venv/bin/python scripts/prepare_pilot_cashflows.py
PYTHONPATH=src .venv/bin/python -m unittest tests.api.test_cashflows_fcfe tests.valuation.test_fcfe -v
PYTHONPATH=src .venv/bin/python docs/company-resolutions/implementation-2026-11-03/independent-review/audit_source_cashflows_independent.py
```

Use issuer/shared workpaper scripts and tests for their exact replay. The
projection resource SHA is pinned in `src/valuation_platform/api/bundle-files.json`;
bundle build/verification must pass before publication. An intentional new
source, mapping or ownership approval requires a new version and independent
review, not silent replacement of these records.
