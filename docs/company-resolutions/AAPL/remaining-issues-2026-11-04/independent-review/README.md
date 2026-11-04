# Independent Apple remaining-issues audit — November 4, 2026

**Verdict: Ready with caveats for source review and the qualified platform decision panel. Not ready for complete Apple FCFE or fair-value-per-share certification. Apple remains OPEN.**

This review independently checked the four workstreams after their implementation. The auditor did not change source packages, accepted history, producer calculations, runtime modules or financial values. The parent workflow owns the reader-facing report; this folder contains its audit evidence.

## Checks that pass

- Independently decoded and SHA-256/byte-length verified 12 retained filing bodies. Checked 146 distinct primary-inline and instance fact bindings directly, including concept, fact value, context, date, issuer and unit. The independent script does not import the four producer scripts.
- Recomputed five financing statement sums, separately identified borrowing and CFO-minus-cash-PP&E-plus-identified-borrowing FCFE. All reproduce. The unknown Other components, actual finance-lease principal and containing captions remain null; the issuer question draft remains unsent.
- Recomputed D&A note-minus-cash-statement differences and conservative rounding envelopes. The FY2024 nominal $355M difference lies outside the rounding envelope. No extra D&A, financed asset or lease-principal adjustment is applied.
- Recomputed five current-plus-deferred tax-provision schedules, available tax-payable movements and the three signed historical-to-first-forecast component bridges. Missing early current-tax balances remain missing. The bridges are algebraic comparisons, not demonstrated economic attribution.
- Bound dated cash/securities ($132.420B), named debt carrying values ($98.657B), term-debt fair value ($80.4B), finance-lease liability ($1.230B) and common shares (14.773260B) to their separate filing populations. No automatic cash eligibility, debt-value addition, share-award addition or zero missing claim is introduced.
- Recomputed Apple Base/Bear/Bull enterprise values agree with the prior saved parity baseline, and the preload policy bytes remain unchanged.
- Loaded the final sealed allowlist in a fresh interpreter outside the repository, then compared it to the live API. The pinned decision record matches; all existing current FCFF, provisional FCFE and legacy CFO FCFF records are preserved.
- Independently exercised the live Cash flows tab in Chrome at desktop and mobile sizes. The panel keeps the company open, shows the dated support and unresolved evidence, preserves five provisional FCFE rows and FY2024/FY2025 FCFF of $115.68B/$95.12B. Existing displayed Base EV remains $2.58tn. No JavaScript page errors occurred. Screenshots were inspected for legibility and qualifications.
- Replayed the four stage workpapers in financing → D&A → tax → equity order without changing their outputs. Ran the original Apple resolution suite, new progress tests and operating-history tests separately from the producer's validation run; receipt is retained here.

## Remaining findings, by decision impact

| Finding type | Issue | Permitted conclusion and next evidence |
|---|---|---|
| Unsupported assumption | Exact debt content of Other financing and finance-lease principal/containment | Identified-funding FCFE is reproducible but provisional. Obtain components and actual principal/containing captions, or a complete sourced liability roll-forward. A small net residual is not a gross exposure bound. |
| Not comparable without bridge | FY2024 D&A population difference | The reported combined cash-statement aggregate is an adopted standardized input. An exact expense and corresponding investment/cash bridge is still required before claiming full expense alignment. |
| Not comparable without bridge | Historical tax-inclusive balance-sheet convention versus recurring forecast tax/investment/working capital | Policy acceptance is documented, and existing forward rates are retained analyst assumptions. Algebraic bridges do not demonstrate economic consistency; cross-basis CAGR and automatic history calibration remain disabled. |
| Missing decision output | Complete reviewed equity bridge and award treatment | Cash observations and dated shares are support, not a complete equity numerator or denominator. Determine eligible nonoperating cash, full claims and forecast overlap, and non-overlapping existing-award treatment before verified value per share. |

The tax-inclusive historical convention and reported provision allocation are resolved **as policies**, not as proof of observed operating cash tax. Selecting point-in-time common shares resolves a date/population choice, not full diluted equity valuation. The historical current-FCFF gap stays resolved under its stated standardized method; absent legacy gross interest is not reintroduced as a current FCFF input.

No new material implementation defect was found in the final inspected scope. The evidence findings above are not hidden by passing tests. All four implementation stages have reproducible workpapers, but the user's desired overall financial success is not established and no full-company completion label is warranted.

## Replay and evidence

From the repository root:

```sh
.venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/independent-review/audit.py
PYTHONPATH=src .venv/bin/python -m unittest tests.review.test_apple_resolution tests.review.test_apple_resolution_progress tests.review.test_apple_operating_history -v
```

For a newly built sealed runtime, pass `--bundle ABSOLUTE_RUNTIME_PATH`; for the supervised API also pass `--api http://127.0.0.1:8133`. The recorded final runtime was `/var/folders/xr/lsv4vk2979nbt46kx6sjxryh0000gn/T/valuation-cloud-dev-rx54xr3n/runtime`, an ephemeral local path, not a portable dependency. `browser.mjs` uses the installed local Chrome and recorded local ports; it is a local verification helper rather than part of the production bundle.

Supporting files: `results.json`, `audit-receipt.log`, `stage-replay-receipts.log`, `focused-test-receipt.log`, `browser-results.json`, and the desktop/mobile screenshots. No external message was sent. No market price, PM recommendation, new forecast or exact historical financing amount was inferred by this audit.
