# T0 deterministic feeder lifecycle contract parity — 2026-11-19

## Scope and safety

This increment preserves and executes deterministic feeder lifecycle contract tests in the new application repository. It does not start the production feeder process or a systemd service.

- Target repository: `kenznguyen/btcquant-application`, existing branch `main`.
- Source repository: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/t0-centralized-data-feeder-p1-20261101`.
- Source branch HEAD inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`.
- Target exact tested HEAD: `9938b01b2b14b651dc7b65f70bef5a446d28594a`.

No production source module was changed. The tests use fakes, synthetic exchange responses and disposable temporary SQLite databases. No canonical database/data, exchange, external network, systemd manager, VPS, PostgreSQL, T1/T2 or trading path was accessed.

## Source-to-target test reconciliation

- Source `market_data/test_feeder_lifecycle.py` blob: `5797d51e3165721863ceacb1fac76f44055f18a7`; 34 test methods.
- Target already contained `market_data/test_feeder_lifecycle.py` blob `f10de15b11ca00f6a4946c3877062cfb5dbd1442`; 28 different test methods. This existing file was preserved unchanged.
- To avoid overwriting the target's existing tests, the 34 source service/lifecycle contracts were copied into a separate target file: `market_data/test_feeder_service_lifecycle.py`.
- The new file retains all 34 source test methods, with a bounded fixture adaptation for the target's F1 write-gateway schema guard. Final target blob: `590c29a0fbf553d19582912a113a92bb74da083f`.
- Production `market_data/feeder.py` is byte-identical between source and target: `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c`.
- Production `market_data/feeder_service.py` is byte-identical between source and target: `6d238a01f35003b943e2b22c8e05f05090ccb518`.

The fixture helper provisions the exact F1 `feeder_leases` table in each disposable test DB before constructing `SQLiteWriteGateway`. This reflects the existing fail-closed contract: the gateway requires the canonical lease schema to exist before gateway construction. It does not relax the schema guard or modify production behavior.

## Dedicated workflow

- Workflow: `.github/workflows/t0-feeder-lifecycle-unit.yml`.
- Workflow commit: `6e921720d5e97727033516c386bce213e6930cf8`.
- Workflow blob: `4f4b3e9a08caeaa3ee5b0ef1006697a19477d89c`.
- Path-filtered push on `main` for feeder implementation/dependencies, the two lifecycle test modules and the workflow; also supports manual dispatch.
- Checkout is pinned to `github.sha`; preflight verifies `git rev-parse HEAD == GITHUB_SHA`.
- Explicit command: `python -m unittest -v market_data.test_feeder_lifecycle market_data.test_feeder_service_lifecycle`.
- Expected test count: 62 (28 existing target tests + 34 preserved source service/lifecycle tests).
- Python image: `python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df`.
- Test container: Docker `--network none`, read-only root/source, non-root UID, all capabilities dropped, no-new-privileges, bounded CPU/memory/PIDs and temporary writable `/tmp`.
- No credentials or canonical DB mount. PostgreSQL and production process startup are excluded. The `run_service` systemd notification contract tests pass a fake notification callback; no systemd manager is invoked.

## Iterations and failure analysis

- Initial run [44505987189](https://github.com/kenznguyen/btcquant-application/actions/runs/44505987189), checkout `6e921720d5e97727033516c386bce213e6930cf8`: 62 tests executed, 6 errors. The copied source fixtures initialized temporary candle DBs but did not provision the target's F1-required `feeder_leases` schema.
- Intermediate run [44506204245](https://github.com/kenznguyen/btcquant-application/actions/runs/44506204245), checkout `8e5ec92c7d16362de7003bd94265f40ea934d754`: 62 tests, 1 remaining error in the mock-store gateway composition fixture. The final missing fixture initialization was corrected.
- These failed runs are iteration history, not acceptance evidence. No production source change was made in response.

## Authoritative verification

- Final run [44506249466](https://github.com/kenznguyen/btcquant-application/actions/runs/44506249466).
- Job: `135498576940`.
- Exact checkout SHA: `9938b01b2b14b651dc7b65f70bef5a446d28594a`.
- Result: **SUCCESS**, `Ran 62 tests in 2.111s`, `OK`, 0 failures, 0 errors.
- Breakdown: existing target lifecycle/scheduler/retry tests 28/28; migrated source runtime/service lifecycle contract tests 34/34.
- Artifact: `t0-feeder-lifecycle-evidence`, ID `14519797216`, size 2,755 bytes, SHA-256 `80c29fbca88ade5ffc2cbb650f8fdbb64f03a689461a6ee223aacec073ed1cef`, expires 2026-12-03T10:30:39Z.
- Artifact ZIP was downloaded and independently SHA-256 checked. Payload inspection confirmed exact checkout SHA, 62 tests, exit code 0, container image digest, no network, no credentials, no canonical DB and no production service startup. The unittest log contains all 62 individual PASS cases.

## Status

- **PASS** — source lifecycle suite preserved in a separate target test module without overwriting the existing 28 target tests.
- **PASS** — target production `feeder.py` and `feeder_service.py` match the inspected source blobs.
- **PASS** — target F1 schema precondition represented correctly in disposable test fixtures.
- **PASS** — isolated exact-SHA lifecycle gate, 62/62.
- **PASS** — artifact download, digest and payload verification.
- **NOT VERIFIED / NOT AUTHORIZED** — production feeder process startup, systemd integration, VPS/runtime, canonical database/data, real Binance connectivity, PostgreSQL/TimescaleDB and production readiness.

No T0 production source, canonical DB/data, runtime, VPS, deployment, T1/T2 or trading behavior was changed or accessed. No live orders.
