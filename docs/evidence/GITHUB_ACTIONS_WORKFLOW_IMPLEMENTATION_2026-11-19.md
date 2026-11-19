# GitHub Actions Workflow Implementation — 2026-11-19

## Owner approval and implementation

The owner explicitly approved the previously recorded workflow proposal. The minimal manual-only workflow has now been added to the existing `main` branch.

- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Workflow path: `.github/workflows/t0-sqlite-api-isolated.yml`
- Workflow commit: `d4e8b039b9eeb436667d69e642664f7462825dc3`
- Workflow blob: `53411a017a977108f4ef4710647701f38147f8fe`
- Repository HEAD after workflow commit: `d4e8b039b9eeb436667d69e642664f7462825dc3`
- Exact test source checkout SHA: `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f` (kept fixed; not replaced by workflow commit).

## Pinned execution inputs

- Runner: `ubuntu-24.04`, GitHub-hosted.
- Python image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- `actions/checkout` v7.0.1 commit: `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- `actions/upload-artifact` v7.0.2 commit: `cf430e030ddbb5b0abf93d22962f4752f3646cd9`.
- Action commit refs were resolved and fetched from the respective public GitHub repositories.
- Docker Official Image tag/digest and Python 3.12.16 identity were checked against Docker Hub's Python image listing. The workflow pins the immutable multi-platform index digest and selects `linux/amd64`.

## Safety and scope controls in the workflow

- Only `workflow_dispatch` trigger; no push, pull-request, schedule or deployment trigger.
- Repository permission is `contents: read`; no GitHub secrets are referenced.
- Checkout is pinned to the exact approved test source SHA and verified before tests.
- Exactly six approved modules are invoked: feeder recovery, feeder lease, write gateway, storage, sync and API.
- Python test process runs in Docker with `--network none`, read-only root filesystem, read-only source mount, non-root UID, dropped capabilities, no-new-privileges and bounded resources.
- A container preflight verifies Python 3.12.16 and that only loopback is present in `/proc/net/dev`.
- No packages are installed. No PostgreSQL/TimescaleDB tests, exchange access, service startup, canonical DB, VPS, runtime or trading path is included.
- Test log, image identity, Python version, runner metadata, source SHA, run ID and test count/exit code are written to a 14-day artifact.

## Verification performed after commit

- Workflow file fetched back from GitHub; blob SHA matches the committed file.
- Static content checks confirmed the exact source SHA, both immutable action pins, six test module paths, manual-only trigger, Docker network isolation flags and artifact upload step.
- Main branch HEAD confirmed as `d4e8b039b9eeb436667d69e642664f7462825dc3`.
- GitHub Actions dispatch/run API is not exposed by the connected GitHub actions available in this session. No workflow run was dispatched and no run ID, test count or test result exists yet.
- The prior local clone failure remains historical; it was not bypassed by substituting another source SHA.

## Status

| Item | Status |
|---|---|
| Owner approval of proposal | PASS |
| Workflow file committed to existing main | PASS |
| Immutable source SHA and action refs | PASS |
| Python image digest/version selected | PASS |
| Workflow static readback | PASS |
| GitHub-hosted runner/Docker preflight | NOT RUN |
| Network isolation runtime probe | NOT RUN |
| Six-module test suite | NOT RUN |
| Workflow run URL/ID and artifact | NOT AVAILABLE |
| Runtime/canonical DB/exchange/VPS/live trading | NOT ACCESSED |
| Production readiness | NOT CERTIFIED |

## Next step

Open the repository's **Actions** tab, select **T0 SQLite API isolated tests**, and click **Run workflow** on `main`. The workflow itself verifies the fixed source SHA and fails closed if the runner/Docker/image/network preflight fails. After a run starts, record the run ID/URL and inspect the job and evidence artifact before assigning PASS/BLOCKED to the tests.
