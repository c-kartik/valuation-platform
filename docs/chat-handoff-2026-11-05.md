# Valuation Platform — fresh local chat handoff

Prepared November 5, 2026 (Asia/Dubai). Replaces the need to load the long prior conversation. Repository state takes precedence over this checkpoint.

## Immediate objective and environment

The user requests a fresh Codex conversation with compact context, the same local implementation/browser/preview capabilities, and access through both this Mac and its already-paired iPhone. Use a **local Codex chat on this Mac**, in the existing Valuation Platform project. No new cloud environment, fork with full history, worktree, financial changes, deployment or broad implementation is required by this handoff.

- Authoritative Git checkout: `/Users/kc/Projects/valuation-platform`.
- GitHub: `c-kartik/valuation-platform`, branch `main`; financial milestone commit `6a35fd9` (pushed). Apple preceding milestone `47748c6`.
- ChatGPT project mirror: `/Users/kc/.codex/.chatgpt-projects/g-p-6ab15a151e34819197344ac9d5c05df2`. Its `sources/` files are read-only references. Run actual repo operations in the authoritative checkout.
- Previous chat: `01a14e99-dc80-7b30-a334-1a9da62fd6be`, title “Plan phase 2 DCF engine”. Read targeted old turns only if a specific missing decision requires it. Do not import the full transcript.
- Prior cloud chat “Set up valuation-platform” is a different execution host. Repository/context access does not automatically provide access to this Mac's browser or localhost server.
- iPhone pairing is confirmed by the user. Phone → Codex/Remote → connected Mac should expose local chats. Same-host tools/configuration are expected; inspect actual available tools and permissions rather than promise exact inventory parity.

## First-turn checks only

1. Read this file and the repo AGENTS.md. Read the newest sections of docs/project-status.md and docs/cloud-work-handoff.md; do not load every historical report or source bundle.
2. Confirm the actual checkout, branch and working tree; preserve pre-existing files.
3. Verify shell/filesystem access, inspect relevant browser/app tools, check local API health and preview page, and open the preview in this new chat with `open_in_codex`. Opening a tab is separate from confirming the app works.
4. Report what is verified, then wait for the user's next development task. No financial edits or extra implementation are requested yet.

## Preview and runtime

Local Mac preview: `http://127.0.0.1:5195/workspace/`; API health: `http://127.0.0.1:8135/health`. Same-origin API through frontend: `/api/v1/catalog`, `/api/v1/analyst/META`, `/api/v1/analyst/GOOGL`.

The preceding chat restarted the supervised server during handoff preparation. Check whether it is still running before starting another. If needed, run from the checkout:

```sh
PATH=/Users/kc/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH PYTHONPATH=src .venv/bin/python scripts/cloud/workspace.py serve --api-port 8135 --frontend-port 5195
```

Startup seals a fresh read-only API bundle and supervises API/Vite; it does not publish anything. Preserve unrelated processes. Runtime docs: `docs/codex-cloud.md`. Python `.venv/bin/python`; frontend `npm` under the Node path above. No API key is needed for retained-data app use.

Loopback is local to the executing device. This Mac's link is not a phone Safari preview URL. Remote access to the chat and remote access to the website are separate. Do not create an anonymous public tunnel or promise direct iPhone browser access. Report actual mobile preview support if available; otherwise clearly distinguish it from Mac preview capability.

## Current financial milestone

Apple, Meta and Alphabet have five named outputs accepted as **analyst-ready with disclosed qualifications**, not exact cash/ownership reconstruction:

1. FY2021–FY2025 historical FCFF.
2. FCFF forecast and enterprise valuation.
3. Five-year standardized historical FCFE estimates.
4. FCFE forecast and equity valuation.
5. Fair value per share under both routes.

Base five-year FCFF/FCFE share outputs: Apple175.46/161.00; Meta374.70/370.36; Alphabet125.91/124.04 USD. FY2025 valuation origins use later information, not current-date target prices or contemporaneous backtests. Five/ten-year Bear/Base/Bull are supported in the accepted scope. Do not force FCFF/FCFE parity: financing assumptions differ.

Current per-company authority: `docs/company-resolutions/{AAPL,META,GOOGL}/analyst-ready-2026-11-04/` (README, policy, report, results, validation, independent review). Earlier blanket OPEN statements are retained legacy scopes; distinguish them from the newer named acceptance.

Critical policies:
- Keep reported facts, derived calculations, estimates and analyst assumptions distinct and traceable. Reasonable disclosed analyst conventions were explicitly approved; do not revert to exact-reconstruction gates or falsely label estimates as facts.
- Alphabet historical FCFE remains an unallocated consolidated proxy, **not verified parent-common cash**. Forward NCI claim defaults3.4B book proxy including841M redeemable NCI; deduct once in both bridges. Historical minority cash allocation is a separate diagnostic.
- Meta private-investment total27.524B already includes7.448B equity-method holdings. Alphabet private investments68.687B. Carrying-value proxies, not current market values; editable stresses.
- Leases, debt, existing awards, operating cash reserves and additional claims are explicitly treated once. FCFE has no second debt deduction.
- Meta residual Other financing defaults0% debt allocation as an assumption; not proof unidentified funding is zero. Preserve qualifications and source bank.
- Don't call scoped work complete if an implementation, arithmetic, integration or undisclosed-assumption blocker remains. Accepted research qualifications are not automatically unfinished development.

Latest validation:80API tests,309frontend tests,22focused financial regressions, production build, source/report replays, twelve issuer/scenario/horizon combinations, desktop/mobile checks and640 independent arithmetic assertions. Counts overlap; do not sum as unique tests. Apple outputs preserved. Results are saved with logs; rerun appropriate checks only after actual changes or a specific concern.

Runtime entry points: `review/company_analyst.py`, `review/apple_analyst.py`, `valuation/fcfe.py`, `frontend/src/workspace/CompanyAnalyst.tsx`, `AppleAnalyst.tsx`, `Workspace.tsx`. Both peer analyst panels expose histories, editable assumptions, sensitivities, both share values and exports on the DCF tab. Shared FCFE rounding repair bounds representation error only; no cash adjustment/materiality waiver.

## Standing workflow and scope

- Read repo AGENTS.md. Wider42/50-company expansion is paused. Do not automatically research or resolve other issuers.
- Log issue → approved treatment → effect → validation in each relevant company-resolution record; update preparation docs when financial preparation changes.
- User wants concise, direct communication, practical action and manual review of decisions affecting financial numbers. No repeated approval for authorized reversible work.
- GitHub is authoritative; preserve unknowns and original files. No credentials in Git, no public production deployment without explicit scope.
- Current pre-existing untracked folders must be preserved and excluded from unrelated commits: `docs/company-resolutions/AAPL/follow-up-2026-11-04/`, `docs/company-resolutions/META/follow-up-2026-11-04/`, `docs/company-resolutions/follow-up-2026-11-04/`.
- Established UI preferences: navy/gold scheme, solid equal-width slightly rounded bars, compact inputs with2decimal percentages, large company name and share/EV emphasis, stable graph while hover percentage axis appears, compact dynamic year/value legend. Inspect current code/screens before changing UI; historical preferences are not a new change request.
- New financial or UI work should wait for the user's next request after the local capability checks.
