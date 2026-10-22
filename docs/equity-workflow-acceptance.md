# Local optional equity workflow acceptance

The subsequent [October 22 hosted preview review](firebase-public-preview.md#newly-performed-hosted-acceptance)
deploys this approved work and records fresh browser/CLI checks and a new bounded
withdrawal deadline. The local-only statements and counts below preserve the
October 21 checkpoint; they do not describe current Hosting access.

October 21, 2026; starting clean `main` at
`8652cbf0125d21ed280747ba3a528ce2c0c5b892`, four commits ahead of local
`origin/main`. **PASS for this local software workflow**, with the limitations
below. This extends the [initial optional-flow verification](local-calculator-ui.md#optional-equity-verification-local),
not the company's financial acceptance. Phase 1 remains
[paused](phase1-universe-pause-checkpoint.md).

## Browser exercise and temporary inputs

Actual Chrome used the local Vite frontend and compatible private-bundle Python
API. Each retained META, GOOGL and AAPL FY2025 anchor began with 37 unset rates
and no inherited bridge/result. These were synthetic engineering trials using
retained revenue, **not researched company forecasts or investment valuations**.

All five annual periods used growth 10%, margin 20%, operating tax 25%, expense
D&A/revenue 5%, investment/revenue 10% and full-revenue WC cash needs 2%.
WACC was 25%, terminal growth 5%; the five terminal operating ratios were
explicitly copied with the existing button. These choices test software only.
EV succeeded before opening equity. The manual bridge used assets USD100m,
financing USD40m, other claims USD10m and 20m issued test shares: equity is
EV + USD50m. Share dates were 2025-12-31 for META/GOOGL and 2025-09-27 for AAPL.

Coverage was explicitly selected-population-only for all roles. Named engineering
classes used an explicitly chosen one-for-one A/B or A/B/C equivalence for the
first two anchors and single common class for AAPL. These declarations do not
establish actual class rights. Existing awards were explicitly omitted
provisionally; the result prominently retained their unbounded limitation.

Observed browser checks passed:

- USD-million amount and million-share labels, dated population, collapsed
  declarations, signed reconciliation and provisional issued-share basis.
- Unassessed claims blocked equity while retaining EV; "None identified"
  instead produced an explicit null-valued, unbounded omission, not a factual zero.
- Zero shares and declared overlap rejected; correction retained valid entries.
  A collapsed overlap editor opened and focused its associated field.
- Closing/reopening equity retained amounts/date. Company-switch cancellation
  restored focus; confirmed switches discarded the old company bridge/results.
- WACC edits staled both results; a new EV left older equity stale. Bridge-only
  edits staled equity while leaving EV current. Explicit recalculation recovered.
- An intentional local API shutdown produced a proxy 502 and recovery guidance;
  entries survived. Restarting the same bundle and explicitly retrying succeeded.
- AAPL financing USD300,000m preserved negative equity and per-share signs.
  A separate 0.0000001-million-share diagnostic displayed the exact positive
  denominator and a long negative per-share value.
- Desktop and 390×844 emulation: keyboard disclosure/action navigation, visible
  error focus, field-associated guidance, dates, omissions and reconciliation
  remained readable, with no observed horizontal page overflow. Representative
  screenshots were captured in the review conversation, not saved in the repo.

## Demonstrated blockers and narrow fixes

| Finding | Fix and regression |
| --- | --- |
| Zero shares returned the engine's generic "sign domain" message. | Translate the existing rejection to positive shares in millions; amount-sign guidance identifies USD millions. No domain change. |
| A declared overlap hidden in collapsed component details focused only a generic error region. | Open/focus the relevant populated reference editor; add field error associations and a navigable component fallback. The calculator still cannot locate hidden economic overlap. |
| An automated precision probe showed 0.1 actual shares rounding to zero million shares. | Exact isolated-Decimal share-unit display, subsequently verified in browser; regression covers fractional/long values and caller-context isolation. |

No financial arithmetic, Python reader/engine/API, schema, source or validation
domain changed. The outage notice repeats "entries are preserved"; this remains
a minor cosmetic issue, not a recovery blocker.

## Numerical and validation checks performed

A temporary sanitized browser capture contained 16 submitted run requests:
11 successful, four expected invalid-case 422 responses and the intentional 502.
Each of the 11 successful submitted cases matched the real anonymous CLI's
**entire JSON output**. Equivalent legacy analyst cases also matched complete
Stage B/C financial components; preparation metadata intentionally differed.

An additional 22 HTTP trials covered, for each anchor, separate assets/financing/
claims increases, doubled shares, zero equity, negative equity and high-precision
assets, plus one explicit-zero-component case. Each matched anonymous CLI JSON
and equivalent legacy financial components. Thus **33 cases** had both kinds of
CLI comparison. **30 Stage C results** were independently reconciled with exact
rational arithmetic: signed components, role subtotals, equity and denominator.
Absolute tolerances were USD `1e-30` for components/equity and USD/share `1e-40`
for division; presentation rounding was excluded. Bridge variants preserved the
complete Stage B result. No binary float equality or second call to the bridge
formula was used as the independent check.

Twenty-five invalid HTTP validation requests rejected missing/zero/negative/
malformed/wrong-type shares, missing/invalid/mismatched dates, missing/negative/
percentage/wrong-type amounts, class mismatch, missing/unsupported awards,
missing coverage, unresolved requirements, overlaps, alternatives, duplicate
populations and excess precision. Explicit zero validated calculation-free and
ran successfully; blank required values did not become zero.

Fresh focused verification passed **82 frontend tests**, **101 Python tests**
and the TypeScript/Vite production build. Existing automated tests additionally
cover late replies after edits, operating/company switching, raw invalid entry,
busy/retry, real worker deadline/cancellation and preservation; these timing cases
are automated coverage, not claimed browser observations. Commands:

```sh
npm --prefix frontend test
npm --prefix frontend run build
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m unittest \
  tests.valuation.test_investor_equity tests.valuation.test_case_inputs \
  tests.valuation.test_equity_case_inputs tests.valuation.test_bridge \
  tests.valuation.test_case_summary tests.api.test_cases tests.api.test_catalog \
  tests.api.test_public_boundary tests.analyst.test_preparation_preservation
```

Changed local links/anchors, whitespace, credential markers and exact Git scope
were checked. All nine templates remain byte-identical: six contain 37 unset
numerical forecast inputs each; three scenario templates contain 111 each.
Financial formulas, historical/frozen artifacts and approvals are unchanged.
Temporary request captures, cases and numerical outputs were removed after review;
no runnable company case, defaults or valuation output was saved in the repository.

## Limits and review handoff

Manual aggregate declarations cannot authenticate evidence, prove complete
claims coverage or detect hidden economic overlap/forecast settlement duplication.
Award omissions may be unbounded; issued test shares are not fully diluted fair
value. Actual-company bridge/share choices remain unresolved. This is functional
workflow acceptance, not investment readiness, a new economic approval or a
complete accessibility audit. No actual mobile virtual-keyboard/screen-reader
test was performed.

Only loopback frontend/API review servers are left running; current PIDs and safe
stop instructions accompany the checkpoint report, rather than a durable PID
claim here. Browser trial state was cleared. No push, deployment or cloud action
was performed. The [public preview](firebase-public-preview.md) is unchanged;
manual backend withdrawal remains **October 22, 2026, 13:04:19 Dubai /
09:04:19 UTC**, with no extension or new automation.
