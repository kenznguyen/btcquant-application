# T0 Feeder, Sync, Recovery Gate and Dependency Manifest — 2026-11-19

Date: 2026-11-19 (Asia/Ho_Chi_Minh)
Repository: `kenznguyen/btcquant-application`
Branch: `main`
Scope: isolated SQLite feeder lease/sync/recovery regression and SQLite-first T0 runtime dependency declaration.

## 1. Exact workflow execution

- Workflow: `.github/workflows/t0-sqlite-feeder-sync-recovery.yml`
- Workflow commit / exact checked-out source SHA: `78e67b7bec139452d2cf6e6a6976dfcc96f69a1a`
- Workflow blob: `71d7c0564918f1da2f31dd5853442fc6352d7444`
- Run: [44500564066](https://github.com/kenznguyen/btcquant-application/actions/runs/44500564066)
- Event: `push`; conclusion: `success`; run attempt: 1.
- Job: `SQLite-only feeder, sync and recovery tests`; job ID `135478919064`; conclusion: `success`.
- Exact checkout identity verified in job log: `git rev-parse HEAD == GITHUB_SHA == 78e67b7bec139452d2cf6e6a6976dfcc96f69a1a`.
- Test command: `python -m unittest -v market_data.test_sync market_data.test_feeder_lease market_data.test_feeder_recovery`.
- Actual result from runner log and downloaded artifact: `Ran 31 tests in 0.458s`; `OK`; exit code 0.
- Breakdown: sync ingestion 11/11; lease/fencing 10/10; recovery planner/coordinator 10/10.
- Test interpreter image: Python 3.12.16 slim Bookworm, immutable image digest `sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Isolation recorded in runner metadata/log: Docker `--network none`, read-only source mount, non-root UID, no credentials, no canonical database mount. PostgreSQL and feeder service runtime excluded.

## 2. Artifact verification

- Artifact: `t0-sqlite-feeder-sync-recovery-evidence`
- Artifact ID: `14516972397`
- Size: 1,994 bytes
- GitHub digest: `sha256:b5e8f4ac1e5b2084d288daf8e167d47df2b6ca55255457b34ea080d4ae8a43a5`
- Downloaded ZIP independently SHA-256 hashed to the same digest.
- ZIP payload inspected: `container_image.txt`, `runner_metadata.txt`, and `unittest.log`.
- Runner metadata confirms run ID, exact workflow/source SHA, selected test modules, expected/actual test count 31, exit code 0, standard-library-only test dependencies, network disabled, no credentials, no canonical DB mount, feeder service runtime excluded, PostgreSQL excluded.
- Artifact expiry: 2026-12-03T09:53:45Z.

## 3. Scoped dependency manifest

- Added `requirements-market-data.txt`; commit `78299c2357f5ef4d9bb27766a1c99646fed04efa`; blob `107b1bad04982506a8023cd784d5d0dafae3e41a`.
- Direct runtime packages declared: `ccxt==4.5.92` for Binance USD-M exchange ingestion; `gunicorn==23.0.0` for serving the WSGI API.
- The versions match the previously recorded T0 environment baseline; this is a compatibility starting point, not proof that a fresh install or current runtime works.
- The 31-test isolated suite itself uses Python standard library only; neither package is needed to execute that gate.
- Flask is not included: the API is a direct WSGI application. The broad source `requirements.txt` was not copied because it includes unrelated application dependencies and does not declare CCXT.
- `psycopg` is deliberately omitted: PostgreSQL/TimescaleDB, its migration payload, TLS and runtime validation remain outside the approved SQLite scope.

## 4. Verification limits

- Workflow execution and exact checkout: PASS.
- 31 selected SQLite tests: PASS 31/31.
- Artifact presence, digest and payload: PASS.
- Manifest path/content/blob readback: PASS.
- Dependency resolver, package installation, transitive lock, fresh-environment compatibility and runtime startup: NOT VERIFIED.
- Python minimum supported version for the full runtime: NOT ESTABLISHED by this gate.
- PostgreSQL/TimescaleDB, feeder service runtime, canonical database/recovery, VPS/deployment, T1/T2 and paper/live trading: NOT TESTED / OUT OF SCOPE / NOT CERTIFIED.

## 5. Change and scope record

Only the scoped dependency manifest and this evidence documentation are added in this increment. No T0 source code or tests, source repository, canonical database/data, PostgreSQL assets, runtime, VPS, T1/T2 or trading behavior was changed or accessed. No packages were installed and no live exchange/network access occurred in the test container.

## 6. Next step

Update the session handoff and T0 migration provenance with this exact run, job, artifact digest, manifest commit/blob and verification limits. Do not treat the manifest as a lockfile or authorize runtime/deployment from these results.
