# T0 SQLite API/Storage Isolated Regression Gate — 2026-11-19

Repository: `kenznguyen/btcquant-application`
Branch: `main`
Implementation commit / exact CI checkout SHA: `dc7190e392de1b0bb940ba4acf9a1df0f44eb130`
Workflow: `.github/workflows/t0-sqlite-api-storage.yml`
Workflow blob: `48f06ecc27bba90fcd4d6d05ff7ed3158a0b7014`

## Approved scope

User approved a dedicated SQLite-only API/Storage gate. This workflow:
- Runs on `push` to `main` only when the selected API/Storage implementation, dependency, test or workflow paths change; also supports explicit `workflow_dispatch`.
- Checks out exactly `${{ github.sha }}` and asserts checked-out `HEAD == GITHUB_SHA`.
- Uses the immutable Python 3.12.16 slim image already used by the F1 isolated gate.
- Runs in Docker with `--network none`, read-only source mount, non-root UID, read-only root filesystem, dropped capabilities, no-new-privileges, resource limits and disposable tmpfs.
- Does not mount canonical DB, pass credentials, install dependencies, contact an exchange or access a runtime.
- Explicitly invokes only 16 approved SQLite test methods: 12 API tests and 4 Storage tests.
- Excludes API's explicit PostgreSQL-no-DSN test, all 3 PostgreSQL-specific Storage tests, all feeder lifecycle tests and all other modules.
- Requires exactly 16 tests and uploads runner metadata, image identity and unittest log.

## Exact workflow evidence

Run: [44496561587](https://github.com/kenznguyen/btcquant-application/actions/runs/44496561587)
Job: `135465125699`
Event: `push`
Run result: SUCCESS
Exact checked-out SHA: `dc7190e392de1b0bb940ba4acf9a1df0f44eb130`
Test output: `Ran 16 tests in 0.025s`; `OK`.
All 16 selected tests passed.
Docker image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
Docker network: none.
Canonical database mount: none.
Credentials: none.
Feeder lifecycle tests: excluded.

Artifact:
- Name: `t0-sqlite-api-storage-evidence`
- ID: `14514253952`
- Size: 1,470 bytes
- SHA-256: `bd75b0a6053b4ea4a1558f85947cf28ba2b10667eb51fa64d710d9eed4a49870`
- Expires: `2026-12-03T09:27:39Z`

## Status

- Workflow implementation and exact-SHA check: PASS.
- SQLite API regression: PASS, 12/12 selected methods.
- SQLite Storage regression: PASS, 4/4 selected methods.
- Combined isolated gate: PASS, 16/16.
- PostgreSQL/TimescaleDB behavior: NOT TESTED / OUT OF SCOPE.
- Feeder lifecycle, runtime, canonical data/recovery: NOT TESTED / OUT OF SCOPE.
- Full T0 parity and production readiness: NOT CERTIFIED.

## Strict non-changes

No source repository change. No application production/test source change. No PostgreSQL execution or migration. No canonical database/data, VPS, runtime, T1/T2, paper/live trading, exchange or trading execution access. No dependency installation. No manual legacy workflow dispatch. No branch creation, merge, rebase, cherry-pick, reset or force-push.

## Next step

Continue with read-only review of any remaining T0 API/Storage integration dependencies and contract boundaries. Do not broaden this SQLite gate to PostgreSQL or feeder lifecycle without separate approval.
