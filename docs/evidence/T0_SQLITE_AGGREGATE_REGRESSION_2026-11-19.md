# T0 SQLite-only aggregate regression — 2026-11-19

## Scope

This gate combines the already-approved isolated SQLite-only T0 regression modules at one exact application SHA. It does not expand into PostgreSQL, canonical data, production runtime or deployment.

- Repository: `kenznguyen/btcquant-application`, branch `main`.
- Workflow: `.github/workflows/t0-sqlite-aggregate.yml`.
- Workflow commit and exact tested source SHA: `ccf8348e86b637d42343982d306f65c14cf4aaa5`.
- Workflow blob: `89beb460326015abf5daaaaab606e142b50c486d`.
- Exact checkout is `github.sha`; the uploaded metadata independently records `checked_out_source_sha == workflow_commit`.

## Explicit allowlist

| Suite | Tests |
|---|---:|
| SQLite write gateway and shadow gateway | 14 |
| Sync ingestion contracts | 11 |
| Lease/fencing contracts | 10 |
| Recovery planner/coordinator | 10 |
| Existing target lifecycle/scheduler/retry | 28 |
| Preserved source feeder/service lifecycle contracts | 34 |
| SQLite API methods | 12 |
| SQLite Storage factory methods | 4 |
| **Total** | **123** |

The API PostgreSQL-no-DSN test and all three PostgreSQL-specific Storage tests are explicitly excluded. No module discovery or broad test sweep is used; the workflow lists the exact approved test modules/methods.

## Isolation

- Immutable image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Actual image ID: `sha256:313cf8f190a1abab00472c1f0c950c10486c22114bcd8aef2a8198fb587a6d18`.
- Docker `--network none`, read-only root filesystem and source mount, non-root UID, all capabilities dropped, no-new-privileges, bounded PIDs/memory/CPU, temporary writable `/tmp`.
- No credentials and no canonical database mount. Test modules use temporary SQLite databases and fake/synthetic exchange collaborators.
- PostgreSQL/TimescaleDB, production feeder process, systemd manager, real Binance connectivity, VPS, deployment, T1/T2 and trading are excluded.

## Authoritative run

- GitHub Actions run [44506768218](https://github.com/kenznguyen/btcquant-application/actions/runs/44506768218).
- Job: `135500303865`.
- Exact checkout SHA: `ccf8348e86b637d42343982d306f65c14cf4aaa5`.
- Result: **SUCCESS**; `Ran 123 tests in 3.259s`; `OK`; 0 failures and 0 errors.
- Artifact: `t0-sqlite-aggregate-evidence`, ID `14518344977`, size 4,363 bytes, SHA-256 `2dc7bdc991aa01592bc37bd0b29511599af5612034c0fc0435784634c853aebc`, expires 2026-12-03T10:33:40Z.
- Artifact ZIP downloaded and independently SHA-256 verified. Payload inspection confirmed exact checked-out SHA, 123 tests, exit code 0, immutable image ID and the stated scope/isolation metadata.

## Status

- **PASS** — aggregate exact-SHA checkout.
- **PASS** — 123/123 SQLite-only T0 regression tests.
- **PASS** — PostgreSQL-specific tests excluded by explicit allowlist.
- **PASS** — Docker network/source/filesystem/user isolation.
- **PASS** — artifact digest and payload verification.
- **NOT VERIFIED / NOT CERTIFIED** — PostgreSQL/TimescaleDB, canonical historical data/OOS bundle, production feeder/API startup, systemd operation, live exchange connectivity, current VPS/runtime, deployment and production readiness.

No T0 production source, canonical DB/data, runtime, VPS, deployment, T1/T2 or trading path was changed or accessed. No live orders.
