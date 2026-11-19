# F3 SQLite Multi-Page Atomicity Regression — 2026-11-19

## Scope approved
- Prioritize F3 before F2.
- Add a regression test for a successful first ingestion page followed by a failing second page.
- Verify first-page rows remain committed and the failed page leaves no partial inserts or overwrites.
- SQLite test database only. No Binance access, canonical database access, PostgreSQL/TimescaleDB, Scheduler, RetryPolicy, Runtime, VPS, or trading path.

## Implementation
- Test-only change: `market_data/test_sync.py`.
- Test: `test_second_page_write_conflict_rolls_back_page_without_removing_first_page`.
- Source/test commit: `15d404cb970de14415b21bbadd843027cea7441d`.
- Test file blob: `7621c85a4c7eb2ad233de94da89e6fbb411ea534`.
- The test uses the existing temporary SQLite database, LeaseStore and SQLiteWriteGateway.
- Page 1 contains 1,000 valid candles and is committed by the first write_batch call.
- Page 2 contains one new valid candle followed by a conflicting candle already present in the test database. The gateway inserts the first page-2 row inside its transaction, detects the conflict on the next row, and must roll the entire page-2 transaction back.
- Assertions require all 1,000 page-1 rows to remain, the new page-2 row to be absent, and the pre-existing conflicting row to retain its original values and observation timestamp.
- No production ingestion, store, gateway, schema, or runtime logic was changed.

## Isolated workflow
- Updated `.github/workflows/t0-sqlite-api-isolated.yml` to checkout the exact test commit above and expect 63 tests (previous baseline 62 plus this regression).
- Workflow commit: `f046cd445c21d84f7a9d3dacc3107a833fd820be`.
- Workflow blob: `c7bea616b38bc6fda8fcc319264686a1bd27eaf7`.
- The existing workflow still uses the six approved SQLite/API test modules, a Docker test container with `--network none`, no credentials, and no canonical database mount.

## Verification status
- Test source commit and changed-file scope readback: PASS.
- Regression test presence and workflow source pin/count readback: PASS.
- Test execution: **NOT RUN / NOT VERIFIED** in this session.
- The GitHub connector exposes read-only workflow inspection but no workflow-dispatch operation. A local checkout attempt was also blocked because this execution environment could not resolve `github.com`. No substitute run or success claim was made.
- Binance/exchange access: NOT ACCESSED.
- Canonical database: NOT ACCESSED.
- PostgreSQL/TimescaleDB, Scheduler, RetryPolicy, Runtime, VPS, T1/T2 and trading: NOT ACCESSED.

## Required next step
Manually dispatch **T0 SQLite API isolated tests** from the Actions tab on `main`. Verify the run checks out exactly `15d404cb970de14415b21bbadd843027cea7441d`, discovers and passes 63 tests with zero failures/skips, and publishes the evidence artifact. Then append the exact run ID, workflow SHA, job result, artifact ID/digest and payload verification to this report and `docs/PROJECT_SESSION_HANDOFF.md`.

## Status
- F3 regression implementation: **PASS (committed; static readback only)**.
- F3 execution: **NOT VERIFIED**.
- F2 Scheduler/RetryPolicy/Runtime design: **NOT STARTED**, intentionally deferred until F3 execution evidence is complete.
- Production/runtime/canonical database: **NOT CERTIFIED**.


## Automatic trigger approval — 2026-11-19
- User approved enabling automatic execution on every push to `main`.
- Workflow commit adding trigger: `bd0b885f97627955ac02b72d89ad86db6e722b70`.
- Workflow blob: `cc772e6595cbe8b7ecda583039ddefbda98b3176`.
- Trigger configuration now includes both `push: branches: [main]` and `workflow_dispatch`.
- The test checkout remains deliberately pinned to F3 source SHA `15d404cb970de14415b21bbadd843027cea7441d` and the suite expects 63 tests. Thus every main push re-runs the same reproducible F3-approved source snapshot; it does not automatically test arbitrary later main source changes.
- No application runtime or deployment is triggered. The job remains a read-only, isolated SQLite test container with network disabled and no canonical DB mount.
- First automatic push-triggered run has not yet been observed at the time of this report update. Execution remains NOT VERIFIED until the run and artifact are inspected.
