# Independent Static Review — T0 SQLite/API Test Suite — 2026-11-19

## Scope and method

- Repository: `kenznguyen/btcquant-application`, branch `main`.
- Reviewed immutable application source: `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f`.
- Reviewed all six executed test modules and their principal implementation modules: feeder/recovery, lease, write gateway, store, storage factory, sync and WSGI API.
- Cross-checked review scope against GitHub Actions run [44443686889](https://github.com/kenznguyen/btcquant-application/actions/runs/44443686889), which executed the same six modules at the exact source SHA.
- Review method: static source/test inspection. No code was changed and no additional tests, coverage instrumentation, runtime service, exchange or database were run/accessed.
- This is an independent review of the test suite and selected implementation paths, not a full repository, runtime or production audit.

## Five-axis assessment

| Axis | Assessment | Basis |
|---|---|---|
| Test intent and behavioral assertions | PASS / PARTIAL | Tests generally assert observable contracts, fail-closed behavior, transaction outcomes and response payloads. |
| Correctness coverage | PARTIAL | Good focused coverage for six paths, but important scheduler/runtime and failure-boundary behaviors are not covered. |
| Readability and maintainability | PASS | Tests are organized by domain, use unittest, temporary directories and descriptive test names. |
| Architecture alignment | PASS / PARTIAL | SQLite default, explicit PostgreSQL selection, lease fencing and read-only API boundaries are represented; scheduler/runtime integration is absent. |
| Security/isolation | PASS for reviewed test design | Temporary SQLite paths, mocked exchange, direct WSGI invocation, no credentials in test fixtures beyond a dummy token. Runtime isolation evidence is separately provided by the workflow. |
| Performance | NOT ASSESSED | No benchmark or load test was part of this suite or review. |

## Confirmed verification evidence

Run [44443686889](https://github.com/kenznguyen/btcquant-application/actions/runs/44443686889):
- Checked-out source SHA: `32aaa78a6a8da2ef04c98c7f5ef4c7a4be2afb6f`.
- Six modules; 61 discovered/executed; 61 passed; 0 failed; 0 skipped; process exit code 0.
- Runtime summary: `Ran 61 tests in 0.796s / OK`.
- Artifact `t0-sqlite-api-test-evidence`, ID `14491519041`; downloaded payload SHA-256 matched GitHub digest.
- These results prove execution of the selected tests only. They do not prove untested behavior or runtime/production correctness.

## Strengths observed

1. Recovery planner/coordinator tests cover valid complete coverage, chronological gap windows, invalid alignment/range, sync callback invocation, post-recovery recheck, residual gaps and upstream failure propagation.
2. Lease tests cover singleton acquisition, competing store instances, expiry takeover, generation fencing, stale owner heartbeat/release/write rejection, TTL/heartbeat defaults and fail-closed storage failure.
3. Write-gateway tests cover current/stale/expired leases, rollback on conflicting candles, committed data surviving writer process exit, same-database enforcement, schema/path preconditions and WAL keeper lifecycle.
4. Storage tests cover SQLite default, explicit PostgreSQL configuration, no silent fallback, missing-database read behavior and SQLite factory/ingestion contract.
5. Sync tests cover market identity, exchange/local close-time checks, bounded pagination, idempotent duplicate observations, gap preservation, malformed pages, invalid clocks/ranges, upstream errors and explicit shadow-only CLI acknowledgement.
6. API tests cover auth/configuration failures, read-only methods, bounded/invalid query parameters, gaps/as-of semantics, corrupt data rejection, contract identity/version, freshness and provenance fields.

## Findings

### Finding F1 — Missing lease table is not rejected by gateway schema preflight

- Severity: **Required follow-up / medium** (fail-fast contract gap; no evidence of unauthorized write).
- Location: `market_data/write_gateway.py`, `SQLiteWriteGateway._validate_existing_schema()`.
- The function declares `expected_lease` and reads `PRAGMA table_info(feeder_leases)`, but validates the lease schema only inside `if lease_rows:`. If the `candles` table is valid while `feeder_leases` is absent, constructor validation succeeds. The first write then fails later when its lease SELECT references the missing table.
- Impact: an incomplete canonical schema is accepted at construction, contrary to the method's fail-fast intent; the failure is deferred from initialization to write time and surfaces as a lower-level SQLite error.
- Suggested bounded remedy: require the `feeder_leases` table to exist and match the expected columns/primary key during preflight; add a regression test using a temporary database containing a valid candles table but no lease table.
- No source change or test addition was made in this review.

### Finding F2 — Feeder scheduler/runtime lifecycle is outside the 61-test coverage

- Severity: **Coverage gap / medium**.
- The `test_feeder_recovery.py` module tests `RecoveryPlanner` and `RecoveryCoordinator`; `test_feeder_lease.py` tests `LeaseStore` primitives. The reviewed suite does not exercise `FeederScheduler`, `RetryPolicy`, or `FeederRuntime` lifecycle/state transitions.
- Important unverified paths include per-timeframe scheduling/watermarks, retry classification and Retry-After behavior, heartbeat thread failure/lease loss, startup recovery gating, shutdown/drain timeouts, WAL keeper lifecycle through runtime, and health-state transitions.
- Suggested next test-only increment: design a small, deterministic test plan around scheduler/retry/runtime lifecycle with injected clocks, callbacks and fake lease/store dependencies. Keep it separate from the already-passing six-module baseline and do not connect a live runtime.

### Finding F3 — Multi-page partial-commit contract lacks a direct regression assertion

- Severity: **Coverage gap / low-to-medium**.
- `sync.py` documents that each fetched page commits atomically and earlier pages survive a later page fetch failure. Existing sync tests verify 1000+1 pagination and an upstream failure on a single-page request, but do not directly assert that page 1 remains committed when page 2 raises.
- Suggested regression: return one valid full page, raise on the next fetch, then assert the first page remains readable and no rows from the failed page were committed.

### Finding F4 — API tests exercise WSGI callable directly, not a bound HTTP server

- Severity: **Coverage gap / low**.
- Direct invocation gives good deterministic coverage of request parsing, auth and response contracts, but does not test actual socket binding, HTTP server/header behavior, reverse-proxy routing, timeouts or deployment configuration.
- This is intentionally outside the current isolated unit suite and must not be inferred as a failure of the API contract tests.

## Coverage limitations

- No coverage percentage was measured; 61 passing tests is a test count, not a line/branch coverage metric.
- PostgreSQL/TimescaleDB migrations and live database integration are excluded.
- No real Binance calls, exchange ingestion, canonical database, deployed T0 service, VPS, T1/T2 integration or trading path was tested.
- No performance/load or long-duration concurrency test was performed.

## Verdict

- Six-module suite execution: **PASS — 61/61** (run evidence above).
- Test quality for the narrowly scoped SQLite/API baseline: **CONDITIONAL PASS**.
- Overall coverage of T0 feeder lifecycle and operational behavior: **PARTIAL / NOT VERIFIED**.
- F1 should be addressed before treating the write-gateway schema preflight as fully fail-fast.
- F2 and F3 are recommended follow-up regression-test work; F4 remains an explicitly out-of-scope integration layer.
- Runtime, canonical data and production: **NOT VERIFIED / NOT CERTIFIED**.

## Next gate

1. Owner review of F1 and approval for a minimal source-plus-regression-test fix, if accepted.
2. Separately scope scheduler/retry/runtime tests and the multi-page partial-commit test.
3. Preserve the current 61/61 run as a baseline; do not change its immutable source SHA or widen its workflow scope retroactively.
