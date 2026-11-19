# T0 Active Scope Index

- Date: 2026-11-19
- Application repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Source repository: `kenznguyen/btcusdt-telegram-signals2`
- Source branch: `feature/t0-centralized-data-feeder-p1-20261101`
- Latest source baseline inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`
- Purpose: define the selected T0 scope in the new application repository and separate it from optional, legacy, research and runtime workstreams. This index does not certify operational or production readiness.

## 1. Scope at a glance

| Workstream | Classification | Current disposition | Included in SQLite-only T0 acceptance? |
|---|---|---|---|
| Binance USD-M BTCUSDT M15/H1, SQLite store, fenced writer, feeder/scheduler/recovery and read-only Candle API | Canonical T0 data foundation | KEEP / SQLite-first | Yes, selected contracts |
| Empty-only SQLite initializer | Canonical schema utility | KEEP; tested only against disposable temp DBs | Yes |
| PostgreSQL/TimescaleDB adapters, migrations and tests | Optional backend | PARKED / NOT QUALIFIED | No |
| Kraken Spot modules | Separate research domain | NOT MIGRATED / OUT OF SCOPE | No |
| Binance connectivity probe | Manual support diagnostic | NOT MIGRATED / NETWORK APPROVAL REQUIRED | No |
| T0→T2 end-to-end consumer tests | Cross-layer integration | NOT MIGRATED / SEPARATE APPROVAL | No |
| Process/SIGKILL restart and systemd/VPS tests | Operational runtime assurance | NOT RUN / SEPARATE APPROVAL | No |
| Legacy dashboard health API tests | Retired/legacy application boundary | NOT MIGRATED | No |

## 2. Canonical T0 responsibility

The selected T0 data foundation is limited to:

1. Public Binance USD-M perpetual BTCUSDT candle acquisition for M15/H1.
2. Validation of market identity, timeframe, timestamps, closed-candle state and OHLCV.
3. SQLite canonical storage with a single-writer/lease-fencing boundary.
4. Gap-aware sync and recovery contracts that fail closed when coverage remains incomplete.
5. A bounded, authenticated, read-only Candle API.
6. Retention of canonical data and provenance; no automatic deletion or cleanup authority.

T0 remains an independent data asset. T1/T2 integration, dashboard routing, paper execution and live execution are not authorized by this scope index.

## 3. Selected code and contract coverage

Core production modules in the target include:

- `market_data/store.py`, `storage.py`, `initialize_sqlite.py`
- `market_data/feeder.py`, `feeder_service.py`, `sync.py`
- `market_data/write_gateway.py`
- `market_data/api.py`

The aggregate SQLite-only workflow runs an explicit 196-test allowlist covering initializer/store/fencing, API/Storage, write gateway, sync, lease/recovery, health, retry, scheduler, controlled ingestion and deterministic lifecycle.

Latest aggregate evidence:
- Workflow: [T0 SQLite-only aggregate](https://github.com/kenznguyen/btcquant-application/actions/workflows/t0-sqlite-aggregate.yml)
- Run: [44515824622](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824622)
- Exact tested SHA: `8f49439fafc95186a8c854fe482aad707525a658`
- Result: 196/196 PASS.

This is isolated contract-test evidence only. It does not establish current data availability, process startup, exchange connectivity, deployment or production readiness.

## 4. Optional backend — PostgreSQL/TimescaleDB

- PostgreSQL remains an optional backend in source code, not the selected canonical target.
- Migration SQL assets, psycopg dependency and PostgreSQL-specific qualification are outside this SQLite-first increment.
- Do not add PostgreSQL dependencies, run migrations or qualify PostgreSQL without a separate scope decision.
- Presence of `postgres.py` or `migrations.py` does not mean PostgreSQL is supported operationally in this target.

## 5. Separate domains and support work

- Kraken Spot is a separate research domain and is not part of canonical Binance USD-M BTCUSDT data.
- Binance connectivity probe is a manual diagnostic that requires explicit network authorization; it is not part of offline CI.
- T0→T2 end-to-end data flow and parity tests are cross-layer work, not T0-only acceptance.
- Process/SIGKILL restart, systemd service and VPS checks are operational runtime work and remain unverified.
- Legacy health API tests importing top-level `app` are not part of the target's selected read-only Candle API surface.

## 6. Data authority and retention

- T0 is an independent data asset; the canonical SQLite database and historical market-data payload are not stored in this application repository.
- Reading, using, consuming or acknowledging data does not authorize deletion.
- No default TTL, deletion-after-use, cleanup, archive, compaction, vacuum, backup expiry or replica removal is authorized.
- Any retention/deletion policy requires a separate design and approval.

## 7. Current status and limitations

| Area | Status |
|---|---|
| Selected SQLite-only T0 contracts | PASS 196/196 |
| Dependency lock | PASS for CPython 3.12 / Linux x86_64 |
| Source/target provenance | PARTIAL; documented per selected file |
| Canonical historical data/OOS bundle | BLOCKED / NOT PRESENT IN TARGET REPO |
| Current production feeder/API runtime | NOT VERIFIED |
| Systemd/VPS operation | NOT VERIFIED / NOT AUTHORIZED |
| Binance REST/WebSocket connectivity | NOT VERIFIED |
| PostgreSQL/TimescaleDB | PARKED / NOT QUALIFIED |
| T1/T2 integration | NOT AUTHORIZED |
| Production readiness | NOT CERTIFIED |

No live orders. `AI_EXECUTION_ENABLED=false` remains unchanged.

## 8. Evidence and navigation

- [T0 migration provenance](T0_MIGRATION_PROVENANCE.md)
- [Project session handoff](PROJECT_SESSION_HANDOFF.md)
- [SQLite foundation expansion evidence](evidence/T0_SQLITE_FOUNDATION_EXPANSION_2026-11-19.md)
- [SQLite aggregate regression evidence](evidence/T0_SQLITE_AGGREGATE_REGRESSION_2026-11-19.md)
- [Feeder lifecycle contracts evidence](evidence/T0_FEEDER_LIFECYCLE_CONTRACTS_2026-11-19.md)
- [Dependency compatibility evidence](evidence/T0_DEPENDENCY_COMPATIBILITY_GATE_2026-11-19.md)



## Source-to-target parity audit — 2026-11-19

- Read-only audit report: [T0 source-to-target parity audit](evidence/T0_SOURCE_TARGET_PARITY_AUDIT_2026-11-19.md).
- Audit report commit: `dacf11023869320a773930fb06aceaa289293bb3`.
- Selected SQLite test files were classified as byte-identical, intentionally adapted, target-specific, or separately gated. No additional source files were copied.
- Test parity: PASS for presence and identified blob parity/adaptation; semantic parity of byte-different `test_sync.py` remains PARTIAL pending a concrete contract-gap review.
- Documentation: target README and scope index are adapted for SQLite-first scope; historical source handoff and operational documentation were not copied wholesale.
- Audit was read-only; no tests were rerun, no workflow dispatched, and no source/runtime/data changed. The existing 191/191 evidence applies only to exact tested SHA `42c8172a4b4b0234fa50e64eb6172f970f45ab66`.
- Overall T0 parity remains **PARTIAL**; production readiness remains **NOT CERTIFIED**.


### Sync-test semantic review — 2026-11-19
- `market_data/test_sync.py` semantic review: **PASS**. Target retains the reviewed source cases and adds a page-2 transaction-atomicity regression; source and target `market_data/sync.py` are byte-identical.
- Keep target test as-is; no source test overwrite or additional test migration is justified.
- Detailed evidence: [T0 source-to-target parity audit](evidence/T0_SOURCE_TARGET_PARITY_AUDIT_2026-11-19.md).
- Review was static; no test or workflow was run. The 191/191 aggregate remains tied to exact tested SHA `42c8172a4b4b0234fa50e64eb6172f970f45ab66`.
- Source-only parity review can close for the inspected SQLite test set. This does not certify production readiness or authorize separately gated work.


## Availability and freshness contract update — 2026-11-19

- Current target HEAD: `8f49439fafc95186a8c854fe482aad707525a658`.
- Read-only Candle API contract version `1.1.0`; point-in-time replay uses `asOfMs` as the evaluation anchor, while live/current reads use `generatedAtMs`.
- `timestampValid` validates all returned candle timestamps and first-observed availability; `fresh` requires the latest expected closed candle; `evaluable` additionally requires complete coverage.
- Exact-SHA aggregate run [44515824622](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824622): **196/196 PASS**.
- Dedicated API/Storage run [44515824664](https://github.com/kenznguyen/btcquant-application/actions/runs/44515824664): **21/21 PASS**.
- Detailed evidence: [T0 Availability & Freshness Contract Audit](evidence/T0_AVAILABILITY_FRESHNESS_CONTRACT_AUDIT_2026-11-19.md).
- In-repository pipeline consumers remain on direct Storage reads with existing completeness/availability guards. External HTTP consumer compatibility is NOT VERIFIED. Production readiness remains NOT CERTIFIED.


## External HTTP consumer compatibility audit — 2026-11-19

- Read-only report: [T0 external HTTP consumer compatibility audit](evidence/T0_EXTERNAL_HTTP_CONSUMER_COMPATIBILITY_AUDIT_2026-11-19.md).
- Official target T0 API is contract 1.1.0. Active Core First source branch `feature/core-operational-proof-20261112` at `e6606e28a696374f31cd6db1ec0a1372d942d64d` still has T0 API 1.0.0, a strict 1.0.0 HTTP client and 1.0.0 Core Bundle normalization.
- Core Bundle provider, Common API gateway and FreqAI research context are confirmed T0 HTTP consumers. Android Five-Layer and Core dashboard consume the Common API indirectly.
- Strict version/freshness validation, `asOfMs` anchor mismatch and multi-page `evaluable` handling make active Core First compatibility **BLOCKED**.
- No endpoint connection, source/test/workflow change, CI dispatch, deployment or runtime activation was performed. Production readiness remains NOT CERTIFIED.


## T0 HTTP consumer migration scope — 2026-11-19

- TDD migration scope approved for preparation: [T0 HTTP Consumer Migration TDD Scope](evidence/T0_HTTP_CONSUMER_MIGRATION_TDD_SCOPE_2026-11-19.md).
- Official T0 contract 1.1.0 remains authoritative; active Core First HTTP client and Core Bundle normalization remain BLOCKED pending migration.
- Approval covers scope preparation only. No source implementation, tests, CI, endpoint probe, runtime connection, deployment or trading is authorized.
- Source implementation NOT STARTED; tests/workflows NOT RUN; endpoint/runtime NOT VERIFIED. Separate authorization is required before implementation and again before any endpoint/runtime connection.
