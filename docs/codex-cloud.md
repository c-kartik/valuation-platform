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
frontend tests and production build. The cloud runner uses two frontend workers
and a 15-second default test budget. Two multi-screen integration tests have
their own 60-second budget: the original scenario/sensitivity test exceeded
15 seconds in the cloud, and a single-worker diagnostic exceeded 30 seconds
(57.253 seconds reported). Repeated accessibility queries are now scoped to
their relevant controls; every interaction and assertion remains enabled.
The existing direct for/id label-binding lookup from `Workspace.test.tsx` is
also used for its large editor, avoiding jsdom's repeated whole-document
`label.control` traversal. A later cloud run also timed out on repeated Cancel
editing sessions, so that test has the same bounded 60-second allowance.
Financial tests and schema checks are unchanged.
It makes no new financial approvals or live
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

## Verification checkpoint — November3

[Validation record](codex-cloud-validation.json): fresh local checkout installation,
267 Python tests,278 frontend tests, all named financial replays and production
build pass. Real workspace/proxied-catalog HTTP checks pass and the supervised
processes stop cleanly. Original52-file research bytes/hashes match. The15-second
cloud UI-test budget is recorded; all original assertions remain active.

GitHub authorization now works. The `valuation-platform` environment selects only
`c-kartik/valuation-platform`; its configuration visibly states **Only me**.
Cloud installation, 267 Python tests, financial replays, all 52 research hashes,
production build and actual workspace/proxied-catalog startup checks passed.

The first cloud attempts timed out on long UI integration tests. The test changes
scope repeated queries, resolve editor inputs through the actual label for/id
binding (the existing `Workspace.test.tsx` pattern), and allow 60 seconds for the
two long integration workflows. No financial/application code, values, assertions
or test counts changed. The final cloud frontend run at `ca8e5ae` passed all
**278 tests in 24 files, none skipped**, in 146.10 seconds, followed by a passing
build. The 267 Python and financial checks were retained from `c7ed102`, whose
non-test application/data files are identical. This is a combined validation
record, not a claim that the earlier failing full-script invocation passed.

Timing samples during the successful run arrived every 5.006–6.289 seconds;
they showed no long environment suspension, but did not establish the cause of
prior stalls. Earlier failures remain in the validation record for traceability.
Publication completed on November 3, 2026. The setup chat confirmed publication,
and Settings → Codex Cloud lists `valuation-platform` as **Private**, with no
Unpublished badge. The published checkout is `ca8e5ae`; install/start instructions
and the retained research bank are saved. On your phone, open ChatGPT → Codex and
select `valuation-platform` for laptop-independent work. A separate authenticated
remote platform-preview URL has not been created.
