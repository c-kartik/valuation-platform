# Four-step implementation — November 4, 2026

Open [the detailed implementation report](report.html) first.

The user instructed the four proposed steps to run in succession. The ordered
[run log](run-log.json) records: Apple operating-income reconciliation; Apple/Meta
financing and evidence requests; Alphabet consolidated-versus-parent bridge;
platform consumer separation. The final stage adopts only the separately labeled
historical-availability contract. It does not adopt new historical measurements,
Other-financing assumptions, normalized tax/interest/lease treatments, subsidiary
ownership percentages or NCI fair values.

All three **financial reviews remain OPEN**. There are 18 available calculations
under stated conventions, 10 provisional financing calculations, and 2 missing
FCFF inputs. The original strict parent-common review still has 17 failed cells.
No missing value is filled, no amount changes and no diagnostic becomes FCFF.

## Reproduce in sequence

From the repository root, run these separately in order:

```sh
PYTHONPATH=src .venv/bin/python scripts/reconcile_pilot_execution.py --stage 1
PYTHONPATH=src .venv/bin/python scripts/reconcile_pilot_execution.py --stage 2
PYTHONPATH=src .venv/bin/python scripts/reconcile_pilot_execution.py --stage 3
PYTHONPATH=src .venv/bin/python scripts/reconcile_pilot_execution.py --stage 4
PYTHONPATH=src .venv/bin/python -m unittest tests.review.test_cashflow_readiness tests.api.test_cashflows_fcfe -v
.venv/bin/python docs/company-resolutions/execution-2026-11-04/independent-review/audit.py
PYTHONPATH=src .venv/bin/python docs/company-resolutions/execution-2026-11-04/independent-review/consumer_check.py
.venv/bin/python scripts/render_pilot_execution_report.py
```

Source-only replays retain their existing commands in each company record. The
baseline pins existing files; stages write only this version's workpapers. Replay
does not append duplicate implementation events. A GOOGL schedule pin was added
on independent review with its explicit supplemental provenance; its bytes match
the original stage-3 hash and initial Git HEAD.

The optional `scripts/check_pilot_execution_browser.mjs` uses a local running
workspace and externally configured Playwright/browser paths, writes screenshots
and served API snapshots here, and checks blank manual rates plus explicit
saved-rate opt-in. It makes no financing or discount assumption automatically.
The previously started saved-discount helper is included in validation: its
operands are existing dated preload assumptions, with no market refresh or policy
change. Unrelated earlier source follow-up work remains preserved in place.

## Audit trail

The original error/limitation, treatment, numerical effects and remaining inputs
are documented in the report and each versioned JSON workpaper. Source pins,
retained filing links, exact fractions, annual context identities and evidence
pointers support reproduction. Issuer questions are **drafts, not sent**. New
correspondence, alternative proxies or economic assumptions require their own
record and review. The original source bank, cash-flow projection, prior company
decisions and frozen preparation statuses are unchanged.

See [independent review](independent-review/README.md) and
[validation results](validation.json). Mechanical checks and financial clearance
remain separate verdicts. No claim of full company or project completion is made.
