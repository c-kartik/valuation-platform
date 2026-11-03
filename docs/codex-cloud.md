# Codex Cloud — phone development setup

The approved workflow is phone → private Codex Cloud environment → GitHub
repository → tested changes for manual review. The laptop need not stay awake.
The cloud environment and provider-authenticated preview are separate resources;
repository preparation alone does not create either one.

## Tested repository entry points

Requirements: Python3.12 and Node22.12+ with npm. Runtime selectors are `.python-version`
and `.nvmrc`; the frontend lockfile and Python development lock remain authoritative.
From the checkout root:

```sh
bash scripts/cloud/setup.sh
bash scripts/cloud/verify.sh
.venv/bin/python scripts/cloud/workspace.py serve
```

Setup installs locked dependencies, verifies/restores the52-file original42-company
audit, builds the frontend and smoke-tests the isolated API/catalog plus a synthetic
valuation. It needs package-manager access but no financial-data API key, Google
credentials, OpenAI API key or live SEC retrieval. Python can be selected with
`VALUATION_PYTHON=/path/to/python3.12` before setup.

Verification runs valuation/preload tests, company-resolution/source checks, cloud
checks, original Apple and Meta/Alphabet ledger replays, registered preload replay,
frontend tests and production build. It makes no new financial approvals or live
filing requests. Existing historical gaps and basis labels remain unchanged.

Startup builds a fresh private read-only API bundle outside the repository, checks
health, starts the existing Vite same-origin proxy and supervises only its own two
processes. Ctrl+C stops both and removes that temporary bundle. It never kills
another server, publishes a tunnel or copies cloud credentials into the project.
Default local URL: `http://127.0.0.1:5173/workspace/`. Ports can be chosen explicitly:

```sh
.venv/bin/python scripts/cloud/workspace.py serve --api-port 8100 --frontend-port 5178
```

## Create the private environment

In ChatGPT web/desktop, open **Settings → Codex Cloud → Environments → Create
environment**, or choose **Work in → Cloud → Create environment**. Select only
`c-kartik/valuation-platform` and keep **Who can use: Only me**.

Give environment setup these instructions:

> Prepare this repository with Python3.12 and Node22.12 or later. Run
> `bash scripts/cloud/setup.sh`, then `bash scripts/cloud/verify.sh`. Configure the
> install script to rerun setup from the repository root. For the start skill,
> run `.venv/bin/python scripts/cloud/workspace.py serve` from that root, wait for
> Workspace ready, and verify `/workspace/` and its proxied `/api/v1/catalog`.
> Read AGENTS.md and docs/cloud-work-handoff.md. Keep the environment owner-private.
> Do not modify financial values, accepted sources, historical approvals, production
> deployments or domains. Report setup/test failures before publishing.

Review the setup report; save and publish the **environment** after its cloud
checks pass. This is distinct from deploying the public valuation platform. Existing
cloud tasks retain their state; new tasks use the published setup. Financial review
context belongs in Git so it survives task boundaries.

If a cloud test dependency is unavailable on Linux, record the actual installation
error and resolve its platform compatibility. Do not loosen financial/schema tests
or replace the pinned source data to make setup pass. A local macOS check is not a
Linux or published-environment certification.

## Use it from your phone

Open ChatGPT mobile → Codex → select the published Valuation Platform environment.
Reopen the same task to continue its context. Use a new branch for an implementation
and review the diff/test results before integrating. Work can continue while the
laptop is off. See the [official cloud guide](https://learn.chatgpt.com/docs/environments/cloud-environments).

For visual testing, ask the environment to start the workspace and supply its
**provider-authenticated private preview**. Verify it requires your account before
calling it private. Loopback startup itself supplies no remote URL; an anonymous
tunnel, public site or production redeployment is not part of this setup.
If the current environment offers no private preview, screenshots/artifacts can be
reviewed from mobile until a separate authenticated preview is configured.

## Sources and credentials

`docs/evidence/`, accepted packages, source manifests and current company resolutions
are version-controlled. The [original42-company audit](../research/historical-cashflows-42-2026-11-02/README.md)
is verified and restored under ignored `.cloud/research/`. The archive's original
scripts remain reference material and may contain old paths; current replay uses
portable repository paths.

No secret is needed for retained-data review. For explicitly requested future SEC
retrieval, supply your identifying `SEC_USER_AGENT` through the cloud environment's
personal configuration and allow the required SEC domains. Do not put personal
configuration, tokens, `.env` files or desktop auth state into Git or the research
archive. Existing broader-universe pause and manual treatment approvals remain.
