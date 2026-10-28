# Phase 2 — editable Bear/Base/Bull workflow

Current local UI/API integration: [investor scenarios](integrated-investor-scenarios.md).
`investor-scenario-set-v1` embeds existing anonymous investor v1/v2 cases under the
same strict comparability rules and returns `investor-scenario-results-v1`.
Calculation-free validation and one bounded three-case request now have local API
routes; the legacy analyst contract described below remains compatible. No actual
economics, source approval or template changes follow from that software extension.

## Bounded comparison contract

`analyst-scenario-set-v1` contains `scenario_set_name` and a `scenarios` array
with exactly one `Bear`, `Base` and `Bull` entry. Each entry supplies `label`,
`analytical_date`, `information_cutoff` and `case`: a complete existing
`analyst-case-v1` (EV-only) or `analyst-case-v2` (equity/share) payload. Every case
supplies its own 37 numerical inputs, analyst identity/rationale, scope and
limitations. There are no external file references, inheritance, patches, runtime
copying, automatic calibration, probabilities or expected values. Labels imply
no ordering or approved economics. Examples repeat complete cases deliberately.

Within a set, exact anchor/company/annual period, input basis, convention
identifiers, output scope, five period indices/labels, analytical date and cutoff
must match. Analytical date must equal each case's fiscal end; cutoff must be an
explicit ISO date on or after it. Both dates are entry-level declarations because
the legacy case schema has no cutoff field. Cutoff consistency is enforceable;
actual evidence availability and contradictions in free-text rationale require
semantic review. The engine's own information-cutoff notice is preserved, not
rewritten as an authenticated historical-information claim.

Equity sets require **identical entire bridge/share payloads**, including component
populations, amounts, provenance, exclusions, coverage, review metadata, share
date/count, class/equivalence and award treatment. Even numerically equivalent
Decimal strings or different supporting metadata reject rather than override.
This intentionally holds all bridge choices fixed; bridge scenario variations
need a later scope decision. EV and equity sets cannot be mixed. Annual rates,
WACC, terminal growth and all explicit terminal ratios remain independently
editable in each case, with unchanged existing numerical validation.

## Interfaces and execution

[scenario_inputs.py](../src/valuation_platform/valuation/scenario_inputs.py)
provides immutable `ScenarioCase` / `ScenarioSet`, `read_scenario_set`,
`load_scenario_set`, `run_scenario_set` and `serialize_scenarios`. Strict parsing
reuses existing duplicate-key/number checks; embedded cases use `read_case`.
Validation performs no historical retrieval, activation or calculation. Missing
or invalid cases fail the set with scenario-qualified field paths; missing inputs
never inherit another scenario's values. Execution revalidates the complete set
before any `run_case` call. A later runtime failure returns no partial result/file.

`analyst-scenario-results-v1` retains submitted inputs and each complete existing
single-case result, including assumptions, provenance and limitations. Results
are always ordered Bear/Base/Bull regardless of input array order. Only existing
Stages A/B/C calculate; no financial formulas, single-case schemas or result bytes
change. Inputs and the caller's Decimal context are preserved.

The dedicated [CLI](../scripts/run_analyst_scenarios.py) validates by default;
`--run` is explicit, `--format json|summary` defaults to JSON, and `--output`
requires a run and a new file outside repository source/history paths (or under
`output/`). Existing files/inputs are never overwritten; exclusive creation also
protects against creation races. Nothing is written by validation or ordinary
stdout runs. [README usage](../README.md#editable-bearbasebull-scenarios) lists commands.

The summary compares annual revenue/FCFF, WACC/g, terminal assumptions/FCFF,
explicit/terminal PV and EV; equity sets also show the fixed bridge, dated shares,
class/award declarations, qualified USD/share and shared omissions. Money is USD
millions, share counts actual shares, values/share USD/share. Isolated Decimal
scaling/HALF_EVEN rounding is display-only; JSON retains full precision. Zero EV
has undefined terminal contribution; negative and over-100% ratios retain an
explanation without clamping. Scenario rationale/scope/limitations remain visible.

## Examples and acceptance boundary

Runnable [synthetic EV](../examples/valuation/synthetic-scenarios-ev.json) and
[synthetic equity](../examples/valuation/synthetic-scenarios-equity.json) sets use
only the synthetic revenue-100 fixture. Incomplete EV-only templates for
[META](../examples/valuation/meta-fy2025-scenarios-unset.json),
[GOOGL](../examples/valuation/googl-fy2025-scenarios-unset.json) and
[AAPL](../examples/valuation/aapl-fy2025-scenarios-unset.json) each leave **111
numerical inputs unset** (37 per case), analyst metadata/rationale unset and
cutoff unset. They cannot calculate. The six existing company templates are
unchanged, each still 37-unset; no trial assumptions or bridge selections transfer.

Engineering verification uses synthetic economics, including temporary integration
sets on all three actual retained revenue anchors in both output scopes. Synthetic
bridge quantities in those checks are not company balances/shares. Temporary
files/results are removed. **Subsequent status:**
[three-company scenario software acceptance is complete and economic acceptance
qualified](phase2-scenario-acceptance.md). The earlier engineering-only boundary is
preserved here; growth, margins, tax, D&A/investment/WC consistency, market/terminal
inputs and scope-qualified bridge eligibility/claims/awards retain the reported
limitations and require case-specific review.
Historical acceptance and declarations do not supply that approval; unknown and
unbounded omissions remain visible. [Phase 1 stays paused](phase1-universe-pause-checkpoint.md).
The earlier next-step boundary is superseded by [qualified sensitivity acceptance](phase2-sensitivity-acceptance.md),
[qualified reverse acceptance](phase2-reverse-dcf-acceptance.md) and the
[final three-company checkpoint](phase2-completion-checkpoint.md). Scoped Phase 2
software acceptance is complete; operating-driver sensitivities are **DEFERRED,
not a closure blocker**. Earlier economic qualifications remain unchanged.
