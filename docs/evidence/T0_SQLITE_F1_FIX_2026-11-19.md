# F1 SQLite Schema Preflight Fix — 2026-11-19

## Scope and approval
- Owner approved fixing independent review finding F1 together with a regression test.
- Repository: `kenznguyen/btcquant-application`; branch: `main`.
- Scope is SQLite only: `SQLiteWriteGateway._validate_existing_schema()` and its focused regression test.
- Explicit exclusions: PostgreSQL/TimescaleDB, runtime/Feeder operation, canonical database/data, exchange, VPS, T1/T2, trading, dependencies and schema migrations.

## Change
- Source/test commit: `57b54116188167904e2a2a6020ab349588b42186`.
- Changed `market_data/write_gateway.py`: reject a missing `feeder_leases` table during read-only schema preflight, before Gateway construction succeeds.
- Changed `market_data/test_write_gateway.py`: add `test_gateway_rejects_valid_candles_schema_when_lease_table_is_missing`; fixture uses the existing temporary SQLite database, drops only its test-owned lease table, asserts constructor rejection, and verifies the table remains absent while `candles` remains present.
- No canonical database is referenced or modified.

## Isolated workflow alignment
- Workflow: `.github/workflows/t0-sqlite-api-isolated.yml`.
- Workflow update commit: `5d8ea2e2f9945db90f1799509e156571b77eb87b`.
- Workflow now checks out the exact source/test commit above and expects 62 tests (the prior six-module inventory of 61 plus this regression).
- Existing runner isolation remains: GitHub-hosted `ubuntu-24.04`, Docker `--network none`, read-only source mount, no secrets, no canonical DB mount.
- No workflow run was dispatched in this session; available GitHub connection is read-only for workflow execution/dispatch.

## Evidence and status
- Source/test implementation: **COMMITTED**.
- Regression test: **ADDED; NOT RUN**.
- Six-module suite at new SHA: **NOT RUN / NOT VERIFIED**.
- Workflow configuration: **UPDATED / STATIC READBACK PENDING**.
- Prior baseline remains valid only for its original immutable source SHA `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f`: run `44443686889`, 61/61 PASS. It is not evidence for this new fix.
- Runtime, canonical SQLite data, PostgreSQL/TimescaleDB, exchange, VPS and trading: **NOT ACCESSED**.
- Production: **NOT CERTIFIED**.

## Next step
Manually dispatch **T0 SQLite API isolated tests** from GitHub Actions on `main`. Inspect the run logs and artifact; verify checked-out source SHA is `57b54116188167904e2a2a6020ab349588b42186`, test count is 62, failures/skips are zero, and the network-isolation probe passes. Update this report and handoff with run URL/ID, job result, artifact ID and payload digest. Do not widen the scope.
