# T0 Target Repository Preflight — 2026-11-19

Date: 2026-11-19 (Asia/Ho_Chi_Minh)
Target repository: `kenznguyen/btcquant-application`
Target branch: `main`
Inspected target HEAD before this documentation update: `de669b8d804e71806e8db7d5f8b2fcd05d801e03`
Scope: read-only source/dependency/test-isolation inspection; documentation-only recording approved by owner.

## 1. Repository state and provenance

- The target is the public application repository selected by the owner.
- T0 selected snapshot: `fcaa2efefdd4b3e481e9db951d538824596d0038`.
- Source repository: `kenznguyen/btcusdt-telegram-signals2`.
- Source branch: `feature/t0-centralized-data-feeder-p1-20261101`.
- Source code baseline: `eb91528bab2b994f283dbe34cd7b0bcbfe406cb5`.
- Source documentation/evidence HEAD: `8623d1076d6b821091ff9da0d84033f48fd8ba7a`.
- Provenance manifest: `docs/T0_MIGRATION_PROVENANCE.md`.
- Existing branch `main` retained; no branch/PR divergence introduced.

## 2. Current migrated test inventory

The target includes these focused T0 tests:
- `market_data/test_feeder_recovery.py`
- `market_data/test_feeder_lease.py`
- `market_data/test_write_gateway.py`
- `market_data/test_storage.py`
- `market_data/test_sync.py` — added unchanged; source blob and target blob: `319e084d9c0a9c5b0319e9bb7d1f93a930564dc8`; transfer commit `3aa983c1d71e8fa054ffc61dcea2ec889d504b48`.
- `market_data/test_api.py` — added unchanged; source blob and target blob: `49df7e0bec12908adae67f18a4aa19063e461093`; transfer commit `7f5cf81eebdc53aae76adbba98c980219aefa15a`.

Static isolation review of the two added tests:
- Both use temporary directories/local SQLite paths and cleanup.
- Sync test uses a mocked exchange; subprocess checks help output and rejects a manual CLI request without `--shadow-only` before exchange access.
- API test calls the WSGI application directly, patches environment variables and uses temporary SQLite paths.
- Its PostgreSQL negative case verifies fail-closed behavior without a DSN; it does not connect to PostgreSQL.
- This is static code review only, not proof from execution.

## 3. Dependency and import findings

- The source `requirements.txt` blob is `f5c242bdac51eba200b19233e08e7d4b22f598c4`; it was not copied into the target.
- It declares: `requests>=2.32.0,<3`, `numpy>=1.26.0,<3`, `pandas>=2.2.0,<3`, `Flask>=3.0.0,<4`, `gunicorn>=22.0.0,<24`, `cryptography>=42.0.0,<47`, and `rfc8785>=0.1.4,<0.2`.
- It does not declare `ccxt` or `psycopg`. T0 imports them lazily for exchange collection and optional PostgreSQL paths respectively.
- Static imports in the inspected T0 modules resolve to files present in the target for the reviewed paths.
- `market_data/__init__.py` was not present at the inspected source baseline; no synthetic package initializer was added.
- For the SQLite/API test scope, the two new tests' reviewed paths do not require live exchange or PostgreSQL access. Exact dependency requirements for executing the complete test suite are still NOT VERIFIED.
- Minimum supported Python version, pinned versions, resolver outcome, and full transitive dependency closure remain NOT VERIFIED. Do not infer them from version ranges or install dependencies without a separate approval.

## 4. Backend boundary

- SQLite is the only backend in the currently scoped baseline.
- Four PostgreSQL/TimescaleDB SQL migration files remain absent from the target:
  - `001_initial_timescale.sql`: `777d884d217004569e97821a76b506572ee8f5b7`
  - `002_t0_feeder_leases.sql`: `009474f187a143381e5b29209a64709698795854`
  - `003_t0_database_fenced_candle_writer.sql`: `1e08f77a9e6411050f370f8f14096dcbff605aea`
  - `004_t0_fenced_lease_api.sql`: `cc79631a0c4e12010dc120413973cab7f84f6406`
- `market_data/test_timescaledb.py` remains excluded; it requires a separately provisioned disposable TimescaleDB test service.
- PostgreSQL/TimescaleDB migration execution is BLOCKED/incomplete in this snapshot. This does not itself block a SQLite-only test run.

## 5. Handoff correction

The pre-update target `docs/PROJECT_SESSION_HANDOFF.md` was stale at blob `30cbfe3019e601ce9abffbbc678ee2583fe89061`: its active repository/branch section still identified the source repository and source branch. Its large historical content is retained verbatim below the new target-repository override section; historical references are not silently rewritten.

## 6. Status

| Control | Status | Basis |
|---|---|---|
| Target repo / branch / inspected HEAD | PASS | GitHub readback at target `main` |
| T0 source provenance | PASS | Existing provenance manifest and exact SHAs |
| Six focused T0 test files present | PASS | Target paths read back |
| Two transferred test files unchanged | PASS | Source/target blob SHA equality |
| Static import-link inspection | PARTIAL PASS | Reviewed selected modules and tests |
| Static isolation review of two added tests | PASS | Source inspection only |
| Dependency closure / Python compatibility | NOT VERIFIED | No resolver, installation or execution |
| SQLite test behavior | NOT RUN | No test command executed |
| PostgreSQL migration completeness | BLOCKED | Four SQL migrations absent |
| TimescaleDB integration | NOT RUN / BLOCKED | No disposable service approved or provisioned |
| CI workflow / exact-HEAD result | NOT VERIFIED | No target workflow execution established |
| Runtime / canonical database / market data | NOT VERIFIED | Not accessed |
| Production readiness | NOT CERTIFIED | No test/runtime/data certification |

## 7. Scope and limits

This increment is documentation-only after owner approval. No application source, tests, dependency manifest, workflow, schema, runtime or deployment behavior was changed. No packages were installed; no tests or workflows were run; no database, canonical market data, exchange, VPS or service was accessed. No PostgreSQL asset was copied. Source repository remains unchanged.

Paper-only guardrails remain: no live trading, no real orders, and `AI_EXECUTION_ENABLED=false`. T0 remains an independent protected data foundation.

## 8. Next gate

Recommended next gate is a separately approved, isolated SQLite/API test execution plan. Before executing, resolve the Python runtime and dependency set from authoritative project configuration or reproducible evidence; verify test discovery and ensure no network/exchange/database access can occur. Do not install packages or dispatch CI without separate explicit approval. Keep PostgreSQL/TimescaleDB excluded unless the owner separately selects that backend and approves a disposable test service.
