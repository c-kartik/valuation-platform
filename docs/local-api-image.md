# API image recipe — local candidate and subsequent remote verification

The [subsequent remote checkpoint](cloud-staging-deployment.md) built this unchanged
recipe with Cloud Build, deployed authenticated staging and ran a same-image probe
on preinstalled Cloud Shell Docker. No local Docker was installed. The **earlier
local candidate record below** preserves what was unverified at that time; the new
checkpoint lists exactly which gates were exercised and which remain open.

This earlier milestone was local build preparation, not deployment configuration. The frontend artifact
is only `frontend/dist`; private API resources belong only in the separate image.
The [walkthrough record](local-workbench-acceptance.md) states the actual checks.
No Firebase project, IAM, cloud command, deployment or automatic integration is added.

## Prepare an exclusive, allowlisted build context

From the repository root, with the documented Python 3.12 environment:

```bash
IMAGE_CONTEXT=$(mktemp -d /tmp/valuation-api-image.XXXXXX)
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m valuation_platform.api.bundle "$IMAGE_CONTEXT/runtime"
cp deploy/api/Dockerfile deploy/api/.dockerignore deploy/api/start.py requirements-api.lock "$IMAGE_CONTEXT/"
```

Use **this newly prepared directory**, never the repository root, as context.
The existing builder verifies pinned resources, copies only its allowlist and
creates/verifies the manifest. The context contains 85 runtime files (84 manifest
entries plus manifest) and four build inputs: **89 files**. It excludes `.git`,
local environments, node_modules, tests, unrelated historical corpus, credentials
and frontend assets. `.dockerignore` denies everything except these build inputs
and the generated runtime directory. Do not add files to that directory afterward.
Private historical packages retain existing paths/bytes; no second copy is tracked.

## Candidate local Linux build and run

These commands are for an **already available local Docker runtime**. They were
**not executed** on the review machine: Docker, Podman and Colima were absent from
PATH. No runtime/VM was installed or started; no remote/cloud builder was used.

```bash
docker build --platform linux/amd64 -t valuation-api:local "$IMAGE_CONTEXT"
docker run --rm --name valuation-api-local --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m --memory=512m --cpus=1 --pids-limit=64 \
  --cap-drop=ALL --security-opt=no-new-privileges \
  -p 127.0.0.1:8080:8080 -e PORT=8080 valuation-api:local
```

The resource settings above are **local test proposals**, not measured sufficiency
or an approved cloud configuration. The official Python `3.12.15-slim-bookworm`
candidate and version-locked API dependencies are used in a two-stage recipe.
Dependency installation permits wheels only and checks their consistency; missing
Linux wheels fail the build. A build-time bundle check precedes read-only permissions.
The final image runs UID/GID 10001, with no frontend, tests or build tools copied in.
The launcher execs one Uvicorn process, binds `0.0.0.0` to validated `PORT` (8080 by
default), retains concurrency/backlog/keepalive/shutdown settings and disables
access logs. Existing 35-second calculation / 30-second CPU limits, one child slot,
manifest/source checks and worker network/write denials are unchanged.
No runtime financial retrieval or resource generation is required.

The recipe is repeatable, **not a demonstrated bit-reproducible image**: registry
resolution, OS digest and wheel artifacts have not been inspected/pinned by hash.
Resolve/review the base digest and Linux dependency artifacts in the next local
image test. Host launcher tests do not prove Linux imports, permissions or signals.
Image size/architecture, readiness time, RSS, read-only execution and abrupt-death
behavior remain unmeasured. In particular, no per-process RSS cap exists; an external
container memory limit requires verification rather than an assumption of recovery.

## Gates before cloud experimentation

With an available runtime, verify both synthetic EV/equity API scopes against CLI,
source/manifest tamper rejection, read-only resources/root filesystem, health during
busy rejection, deadline terminate/kill/reap/recovery, bounded large/invalid input,
peak memory and clean shutdown without orphan work. Record resolved image digest,
actual linux/amd64 architecture, image bytes, startup and request timings. These
would be **local container measurements**, not Cloud Run cold starts.

The target static → `/api` → Cloud Run split follows the
[Cloud Run container contract](https://docs.cloud.google.com/run/docs/container-contract)
(PORT, 0.0.0.0, Linux amd64); the base candidate comes from the
[official Python image](https://hub.docker.com/_/python).
Compatibility is still a test gate. No Firebase rewrite or cloud service is configured.
Before an authenticated first cloud test, approve region, CPU/memory, concurrency,
instance limits, request timeout/cleanup margin, access policy, logging and budget/
billing controls. A future Firebase rewrite and direct backend exposure need explicit
review; static hosting does not authenticate the API or impose a global quota.
Real cloud cold starts, Linux enforcement, transfer billing and abuse controls remain
unverified. See the [readiness verdicts](local-workbench-acceptance.md#readiness).
